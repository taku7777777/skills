#!/usr/bin/env python3
"""Validate routing cases or score ordered skill selections from a JSONL file."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


SAFE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def read_jsonl(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno}: invalid JSON: {exc}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"{path}:{lineno}: each line must be an object")
        records.append(record)
    return records


def validate_cases(cases: list[dict[str, object]], known_skills: set[str]) -> None:
    seen: set[str] = set()
    primary_coverage: set[str] = set()
    null_cases = 0
    multi_skill_cases = 0
    required = {"id", "prompt", "expected_primary", "expected_secondary", "forbidden"}
    for case in cases:
        missing = required - case.keys()
        if missing:
            raise ValueError(f"routing case is missing fields {sorted(missing)}: {case}")
        extra = set(case) - required
        if extra:
            raise ValueError(f"routing case has unexpected fields {sorted(extra)}: {case}")
        if not isinstance(case["id"], str) or not SAFE_ID_RE.fullmatch(case["id"]):
            raise ValueError(f"invalid routing case id: {case['id']!r}")
        case_id = case["id"]
        if case_id in seen:
            raise ValueError(f"duplicate routing case id: {case_id}")
        seen.add(case_id)
        if not isinstance(case["prompt"], str) or not case["prompt"].strip():
            raise ValueError(f"{case_id}: prompt must be non-empty")
        primary = case["expected_primary"]
        if primary is not None and not isinstance(primary, str):
            raise ValueError(f"{case_id}: expected_primary must be a skill name or null")
        for field in ("expected_secondary", "forbidden"):
            if not isinstance(case[field], list) or any(
                not isinstance(item, str) for item in case[field]
            ):
                raise ValueError(f"{case_id}: {field} must be an array of skill names")
        secondary = case["expected_secondary"]
        forbidden = case["forbidden"]
        if primary is None:
            null_cases += 1
            if secondary:
                raise ValueError(f"{case_id}: null primary cannot have secondary skills")
            expected: list[str] = []
        else:
            primary_coverage.add(primary)
            expected = [primary, *secondary]
        if secondary:
            multi_skill_cases += 1
        labels = set(expected) | set(forbidden)
        unknown = labels - known_skills
        if unknown:
            raise ValueError(f"{case_id}: unknown skills: {sorted(unknown)}")
        if len(expected) != len(set(expected)):
            raise ValueError(f"{case_id}: expected skills contain duplicates")
        if len(forbidden) != len(set(forbidden)):
            raise ValueError(f"{case_id}: forbidden skills contain duplicates")
        overlap = set(expected) & set(forbidden)
        if overlap:
            raise ValueError(f"{case_id}: expected and forbidden overlap: {sorted(overlap)}")
    missing_primary = known_skills - primary_coverage
    if missing_primary:
        raise ValueError(f"missing primary routing coverage: {sorted(missing_primary)}")
    if not null_cases:
        raise ValueError("routing suite needs at least one no-skill case")
    if not multi_skill_cases:
        raise ValueError("routing suite needs at least one ordered multi-skill case")


def f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


def score(
    cases: list[dict[str, object]],
    predictions: list[dict[str, object]],
    known_skills: set[str],
) -> dict[str, object]:
    prediction_map: dict[str, list[str]] = {}
    for prediction in predictions:
        if set(prediction) != {"id", "selected"}:
            raise ValueError(f"prediction fields must be exactly id and selected: {prediction}")
        if not isinstance(prediction["id"], str) or not SAFE_ID_RE.fullmatch(prediction["id"]):
            raise ValueError(f"invalid prediction id: {prediction['id']!r}")
        case_id = prediction["id"]
        selected = prediction["selected"]
        if not isinstance(selected, list) or any(not isinstance(item, str) for item in selected):
            raise ValueError(f"{case_id}: selected must be an array of skill names")
        if len(selected) != len(set(selected)):
            raise ValueError(f"{case_id}: selected contains duplicate skills")
        unknown = set(selected) - known_skills
        if unknown:
            raise ValueError(f"{case_id}: unknown selected skills: {sorted(unknown)}")
        if case_id in prediction_map:
            raise ValueError(f"duplicate prediction id: {case_id}")
        prediction_map[case_id] = selected

    case_ids = {str(case["id"]) for case in cases}
    missing = case_ids - prediction_map.keys()
    extra = prediction_map.keys() - case_ids
    if missing or extra:
        raise ValueError(f"prediction id mismatch; missing={sorted(missing)} extra={sorted(extra)}")

    primary_correct = 0
    ordered_exact = 0
    forbidden_violations: list[dict[str, str]] = []
    per_label = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    details: list[dict[str, object]] = []

    for case in cases:
        case_id = str(case["id"])
        expected = []
        if case["expected_primary"] is not None:
            expected.append(str(case["expected_primary"]))
        expected.extend(str(item) for item in case["expected_secondary"])
        predicted = prediction_map[case_id]
        actual_primary = predicted[0] if predicted else None
        if actual_primary == case["expected_primary"]:
            primary_correct += 1
        if predicted == expected:
            ordered_exact += 1

        expected_set = set(expected)
        predicted_set = set(predicted)
        for label in known_skills:
            if label in expected_set and label in predicted_set:
                per_label[label]["tp"] += 1
            elif label not in expected_set and label in predicted_set:
                per_label[label]["fp"] += 1
            elif label in expected_set and label not in predicted_set:
                per_label[label]["fn"] += 1
        for label in set(str(item) for item in case["forbidden"]) & predicted_set:
            forbidden_violations.append({"id": case_id, "skill": label})

        details.append(
            {
                "id": case_id,
                "expected": expected,
                "predicted": predicted,
                "primary_ok": actual_primary == case["expected_primary"],
                "ordered_exact": predicted == expected,
            }
        )

    label_metrics: dict[str, dict[str, float | int]] = {}
    label_f1s: list[float] = []
    for label in sorted(known_skills):
        counts = per_label[label]
        precision = counts["tp"] / (counts["tp"] + counts["fp"]) if counts["tp"] + counts["fp"] else 0.0
        recall = counts["tp"] / (counts["tp"] + counts["fn"]) if counts["tp"] + counts["fn"] else 0.0
        value = f1(precision, recall)
        label_f1s.append(value)
        label_metrics[label] = {**counts, "precision": precision, "recall": recall, "f1": value}

    total = len(cases)
    return {
        "cases": total,
        "primary_accuracy": primary_correct / total if total else 0.0,
        "ordered_exact_rate": ordered_exact / total if total else 0.0,
        "macro_f1": sum(label_f1s) / len(label_f1s) if label_f1s else 0.0,
        "forbidden_violations": forbidden_violations,
        "labels": label_metrics,
        "details": details,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=root / "quality" / "routing" / "cases.jsonl")
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--min-primary-accuracy", type=float, default=0.90)
    parser.add_argument("--min-macro-f1", type=float, default=0.85)
    parser.add_argument("--json", action="store_true", help="Print the full result as JSON.")
    args = parser.parse_args()

    try:
        cases = read_jsonl(args.cases)
        known_skills = {path.parent.name for path in root.glob("*/SKILL.md")}
        validate_cases(cases, known_skills)
        for name, value in (
            ("--min-primary-accuracy", args.min_primary_accuracy),
            ("--min-macro-f1", args.min_macro_f1),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if args.validate_only:
            print(f"routing_cases={len(cases)} valid=true")
            return 0
        if args.predictions is None:
            parser.error("--predictions is required unless --validate-only is used")
        predictions = read_jsonl(args.predictions)
        result = score(cases, predictions, known_skills)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            " ".join(
                [
                    f"cases={result['cases']}",
                    f"primary_accuracy={result['primary_accuracy']:.3f}",
                    f"ordered_exact_rate={result['ordered_exact_rate']:.3f}",
                    f"macro_f1={result['macro_f1']:.3f}",
                    f"forbidden_violations={len(result['forbidden_violations'])}",
                ]
            )
        )

    passed = (
        result["primary_accuracy"] >= args.min_primary_accuracy
        and result["macro_f1"] >= args.min_macro_f1
        and not result["forbidden_violations"]
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
