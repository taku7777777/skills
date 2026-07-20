#!/usr/bin/env python3
"""Prepare leakage-resistant task packets and score baseline/with-skill runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import sys
import tempfile
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "quality" / "tasks" / "cases.jsonl"
CONDITIONS = ("baseline", "with-skill")
SAFE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
HUNK_HEADER_RE = re.compile(
    r"^@@ -\d+(?:,(\d+))? \+\d+(?:,(\d+))? @@(?: .*)?$"
)


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


def resolve_repo_file(raw_path: object, case_id: str, field: str) -> Path:
    if not isinstance(raw_path, str) or not raw_path:
        raise ValueError(f"{case_id}: {field} must be a non-empty repository-relative path")
    path = (ROOT / raw_path).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"{case_id}: {field} escapes repository: {raw_path!r}") from exc
    if not path.is_file():
        raise ValueError(f"{case_id}: missing {field}: {path}")
    return path


def validate_unified_diff(path: Path, case_id: str) -> None:
    """Reject textual patch fixtures whose hunk headers do not match their bodies."""
    lines = path.read_text(encoding="utf-8").splitlines()
    hunk_count = 0
    index = 0
    while index < len(lines):
        header = lines[index]
        if not header.startswith("@@"):
            index += 1
            continue

        match = HUNK_HEADER_RE.fullmatch(header)
        if match is None:
            raise ValueError(
                f"{case_id}: malformed unified-diff hunk header at "
                f"{path}:{index + 1}: {header!r}"
            )

        hunk_count += 1
        header_line = index + 1
        expected_old = int(match.group(1) or 1)
        expected_new = int(match.group(2) or 1)
        actual_old = 0
        actual_new = 0
        index += 1

        while index < len(lines):
            line = lines[index]
            if line.startswith("@@") or line.startswith("diff --git "):
                break
            if line == r"\ No newline at end of file":
                index += 1
                continue
            if line.startswith(" "):
                actual_old += 1
                actual_new += 1
            elif line.startswith("-"):
                actual_old += 1
            elif line.startswith("+"):
                actual_new += 1
            else:
                break
            index += 1

        if (actual_old, actual_new) != (expected_old, expected_new):
            raise ValueError(
                f"{case_id}: unified-diff hunk count mismatch at {path}:{header_line}: "
                f"header declares old={expected_old}, new={expected_new}; "
                f"body has old={actual_old}, new={actual_new}"
            )

    if hunk_count == 0:
        raise ValueError(f"{case_id}: patch fixture has no unified-diff hunks: {path}")


def load_cases(path: Path) -> list[dict[str, object]]:
    cases = read_jsonl(path)
    seen: set[str] = set()
    known_skills = {skill_path.parent.name for skill_path in ROOT.glob("*/SKILL.md")}
    skill_coverage: set[str] = set()
    required = {"id", "skill", "prompt", "fixture", "rubric", "repetitions"}
    for case in cases:
        missing = required - case.keys()
        if missing:
            raise ValueError(f"task case is missing {sorted(missing)}: {case}")
        extra = set(case) - required
        if extra:
            raise ValueError(f"task case has unexpected fields {sorted(extra)}: {case}")
        if not isinstance(case["id"], str) or not SAFE_ID_RE.fullmatch(case["id"]):
            raise ValueError(f"invalid task case id: {case['id']!r}")
        case_id = case["id"]
        if case_id in seen:
            raise ValueError(f"duplicate task case id: {case_id}")
        seen.add(case_id)
        skill = case["skill"]
        if not isinstance(skill, str) or skill not in known_skills:
            raise ValueError(f"{case_id}: unknown skill {skill!r}")
        skill_coverage.add(skill)
        if not isinstance(case["prompt"], str) or not case["prompt"].strip():
            raise ValueError(f"{case_id}: prompt must be a non-empty string")
        if (
            not isinstance(case["repetitions"], int)
            or isinstance(case["repetitions"], bool)
            or case["repetitions"] < 3
        ):
            raise ValueError(f"{case_id}: repetitions must be an integer >= 3")
        fixture_path = resolve_repo_file(case["fixture"], case_id, "fixture")
        rubric_path = resolve_repo_file(case["rubric"], case_id, "rubric")
        try:
            fixture_path.relative_to((ROOT / "quality" / "fixtures" / skill).resolve())
        except ValueError as exc:
            raise ValueError(
                f"{case_id}: fixture must be under quality/fixtures/{skill}/"
            ) from exc
        if fixture_path.suffix.lower() in {".diff", ".patch"}:
            validate_unified_diff(fixture_path, case_id)
        try:
            rubric_path.relative_to((ROOT / "quality" / "graders").resolve())
        except ValueError as exc:
            raise ValueError(f"{case_id}: rubric must be under quality/graders/") from exc
        rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
        if not isinstance(rubric, dict) or set(rubric) != {"case_id", "criteria"}:
            raise ValueError(f"{case_id}: rubric fields must be exactly case_id and criteria")
        if rubric.get("case_id") != case_id:
            raise ValueError(f"{case_id}: rubric case_id does not match")
        criteria = rubric.get("criteria")
        if not isinstance(criteria, list) or not criteria:
            raise ValueError(f"{case_id}: rubric criteria must be non-empty")
        ids = [criterion.get("id") for criterion in criteria if isinstance(criterion, dict)]
        if len(ids) != len(criteria) or len(ids) != len(set(ids)) or any(not item for item in ids):
            raise ValueError(f"{case_id}: rubric criterion ids must be present and unique")
        critical_count = 0
        for criterion in criteria:
            if set(criterion) != {"id", "description", "critical"}:
                raise ValueError(f"{case_id}: criterion fields must be id, description, and critical")
            if not isinstance(criterion["id"], str) or not SAFE_ID_RE.fullmatch(criterion["id"]):
                raise ValueError(f"{case_id}: invalid rubric criterion id {criterion['id']!r}")
            if (
                not isinstance(criterion["description"], str)
                or not criterion["description"].strip()
                or not isinstance(criterion["critical"], bool)
            ):
                raise ValueError(f"{case_id}: each criterion needs description:string and critical:boolean")
            critical_count += int(criterion["critical"])
        if not critical_count:
            raise ValueError(f"{case_id}: rubric needs at least one critical criterion")
    missing_skills = known_skills - skill_coverage
    if missing_skills:
        raise ValueError(f"missing held-out task coverage: {sorted(missing_skills)}")
    return cases


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_empty_output(output: Path) -> None:
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)


def prepare(cases: list[dict[str, object]], output: Path) -> None:
    ensure_empty_output(output)
    run_root = output / "run-packets"
    grader_root = output / "grader-packets"
    run_root.mkdir()
    grader_root.mkdir()
    manifest_cases: list[dict[str, object]] = []

    for case in cases:
        case_id = str(case["id"])
        fixture_path = resolve_repo_file(case["fixture"], case_id, "fixture")
        rubric_path = resolve_repo_file(case["rubric"], case_id, "rubric")
        task_dir = run_root / case_id
        task_dir.mkdir()
        task_text = "\n".join(
            [
                f"# Evaluation task: {case_id}",
                "",
                "## User request",
                "",
                str(case["prompt"]).strip(),
                "",
                "## Attached artifact",
                "",
                fixture_path.read_text(encoding="utf-8").rstrip(),
                "",
            ]
        )
        task_path = task_dir / "task.md"
        task_path.write_text(task_text, encoding="utf-8")
        shutil.copy2(rubric_path, grader_root / f"{case_id}.json")
        manifest_cases.append(
            {
                "id": case_id,
                "skill": case["skill"],
                "repetitions": case["repetitions"],
                "task_path": f"run-packets/{case_id}/task.md",
                "rubric_path": f"grader-packets/{case_id}.json",
                "task_sha256": sha256(task_path),
                "rubric_sha256": sha256(grader_root / f"{case_id}.json"),
            }
        )

    manifest = {
        "protocol_version": 1,
        "conditions": list(CONDITIONS),
        "isolation": (
            "Give the executor only one task.md file. Do not expose grader-packets, this manifest, "
            "the source skill repository, or prior outputs."
        ),
        "cases": manifest_cases,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def score_template(manifest_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be an object")
    validate_manifest_integrity(manifest_path, manifest)
    packet_root = manifest_path.parent
    for case in manifest["cases"]:
        rubric = json.loads((packet_root / case["rubric_path"]).read_text(encoding="utf-8"))
        criteria = {criterion["id"]: None for criterion in rubric["criteria"]}
        for condition in manifest["conditions"]:
            for repetition in range(1, int(case["repetitions"]) + 1):
                print(
                    json.dumps(
                        {
                            "case_id": case["id"],
                            "condition": condition,
                            "repetition": repetition,
                            "criteria": criteria,
                            "tokens": None,
                            "latency_ms": None,
                            "cost_usd": None,
                            "tool_errors": None,
                            "notes": "",
                        },
                        ensure_ascii=False,
                    )
                )


def resolve_packet_file(packet_root: Path, raw_path: object, expected_dir: str, case_id: str) -> Path:
    if not isinstance(raw_path, str) or not raw_path:
        raise ValueError(f"{case_id}: packet path must be a non-empty string")
    path = (packet_root / raw_path).resolve()
    expected_root = (packet_root / expected_dir).resolve()
    try:
        path.relative_to(expected_root)
    except ValueError as exc:
        raise ValueError(f"{case_id}: packet path escapes {expected_dir}/: {raw_path!r}") from exc
    if not path.is_file():
        raise ValueError(f"{case_id}: packet file is missing: {raw_path!r}")
    return path


def validate_manifest_integrity(manifest_path: Path, manifest: dict[str, object]) -> None:
    packet_root = manifest_path.parent
    required = {"protocol_version", "conditions", "isolation", "cases"}
    if set(manifest) != required:
        raise ValueError(f"manifest fields must be exactly {sorted(required)}")
    if manifest.get("protocol_version") != 1 or manifest.get("conditions") != list(CONDITIONS):
        raise ValueError("unsupported or malformed manifest")
    if not isinstance(manifest.get("isolation"), str) or not manifest["isolation"].strip():
        raise ValueError("manifest isolation instructions must be non-empty")
    if not isinstance(manifest.get("cases"), list) or not manifest["cases"]:
        raise ValueError("manifest cases must be a non-empty array")
    seen: set[str] = set()
    case_fields = {
        "id",
        "skill",
        "repetitions",
        "task_path",
        "rubric_path",
        "task_sha256",
        "rubric_sha256",
    }
    for case in manifest["cases"]:
        if not isinstance(case, dict) or set(case) != case_fields:
            raise ValueError(f"manifest case fields must be exactly {sorted(case_fields)}")
        case_id = case["id"]
        if not isinstance(case_id, str) or not SAFE_ID_RE.fullmatch(case_id):
            raise ValueError(f"invalid manifest case id: {case_id!r}")
        if case_id in seen:
            raise ValueError(f"duplicate manifest case id: {case_id}")
        seen.add(case_id)
        if (
            not isinstance(case["repetitions"], int)
            or isinstance(case["repetitions"], bool)
            or case["repetitions"] < 3
        ):
            raise ValueError(f"{case_id}: manifest repetitions must be an integer >= 3")
        task_path = resolve_packet_file(packet_root, case["task_path"], "run-packets", case_id)
        rubric_path = resolve_packet_file(
            packet_root, case["rubric_path"], "grader-packets", case_id
        )
        if sha256(task_path) != case["task_sha256"]:
            raise ValueError(f"task packet changed after preparation: {case_id}")
        if sha256(rubric_path) != case["rubric_sha256"]:
            raise ValueError(f"rubric changed after preparation: {case_id}")


def score_runs(manifest_path: Path, score_path: Path, allow_incomplete: bool) -> dict[str, object]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be an object")
    validate_manifest_integrity(manifest_path, manifest)
    scores = read_jsonl(score_path)
    packet_root = manifest_path.parent

    rubric_by_case: dict[str, dict[str, object]] = {}
    repetitions_by_case: dict[str, int] = {}
    for case in manifest["cases"]:
        rubric_by_case[case["id"]] = json.loads(
            (packet_root / case["rubric_path"]).read_text(encoding="utf-8")
        )
        repetitions_by_case[case["id"]] = int(case["repetitions"])

    indexed: dict[tuple[str, str, int], dict[str, object]] = {}
    required_fields = {
        "case_id",
        "condition",
        "repetition",
        "criteria",
        "tokens",
        "latency_ms",
        "cost_usd",
        "tool_errors",
        "notes",
    }
    for result in scores:
        if set(result) != required_fields:
            raise ValueError(f"score fields must be exactly {sorted(required_fields)}: {result}")
        if not isinstance(result["case_id"], str) or not SAFE_ID_RE.fullmatch(result["case_id"]):
            raise ValueError(f"invalid score case_id: {result['case_id']!r}")
        case_id = result["case_id"]
        condition = str(result["condition"])
        repetition = result["repetition"]
        if case_id not in rubric_by_case:
            raise ValueError(f"unknown case_id in scores: {case_id}")
        if condition not in CONDITIONS:
            raise ValueError(f"{case_id}: unknown condition {condition}")
        if not isinstance(repetition, int) or not 1 <= repetition <= repetitions_by_case[case_id]:
            raise ValueError(f"{case_id}: invalid repetition {repetition}")
        key = (case_id, condition, repetition)
        if key in indexed:
            raise ValueError(f"duplicate score row: {key}")
        expected_ids = {criterion["id"] for criterion in rubric_by_case[case_id]["criteria"]}
        criteria = result["criteria"]
        if not isinstance(criteria, dict) or set(criteria) != expected_ids:
            raise ValueError(f"{case_id}: criteria ids must equal {sorted(expected_ids)}")
        if any(not isinstance(value, bool) for value in criteria.values()):
            raise ValueError(f"{case_id}: every criterion score must be true or false")
        tokens = result["tokens"]
        if not isinstance(tokens, int) or isinstance(tokens, bool) or tokens < 0:
            raise ValueError(f"{case_id}: tokens must be a non-negative integer")
        latency_ms = result["latency_ms"]
        if (
            not isinstance(latency_ms, (int, float))
            or isinstance(latency_ms, bool)
            or not math.isfinite(latency_ms)
            or latency_ms < 0
        ):
            raise ValueError(f"{case_id}: latency_ms must be a non-negative number")
        cost_usd = result["cost_usd"]
        if cost_usd is not None and (
            not isinstance(cost_usd, (int, float))
            or isinstance(cost_usd, bool)
            or not math.isfinite(cost_usd)
            or cost_usd < 0
        ):
            raise ValueError(f"{case_id}: cost_usd must be null or a non-negative number")
        tool_errors = result["tool_errors"]
        if not isinstance(tool_errors, int) or isinstance(tool_errors, bool) or tool_errors < 0:
            raise ValueError(f"{case_id}: tool_errors must be a non-negative integer")
        if not isinstance(result["notes"], str):
            raise ValueError(f"{case_id}: notes must be a string")
        indexed[key] = result

    expected_keys = {
        (case_id, condition, repetition)
        for case_id, repetitions in repetitions_by_case.items()
        for condition in CONDITIONS
        for repetition in range(1, repetitions + 1)
    }
    missing = expected_keys - indexed.keys()
    if missing and not allow_incomplete:
        raise ValueError(f"missing {len(missing)} score rows; first missing rows: {sorted(missing)[:5]}")

    summaries: dict[str, object] = {}
    adopted = 0
    evaluated = 0
    for case_id, rubric in rubric_by_case.items():
        case_summary: dict[str, object] = {}
        complete = True
        for condition in CONDITIONS:
            rows = [
                indexed[(case_id, condition, repetition)]
                for repetition in range(1, repetitions_by_case[case_id] + 1)
                if (case_id, condition, repetition) in indexed
            ]
            if len(rows) != repetitions_by_case[case_id]:
                complete = False
            total_criteria = len(rubric["criteria"])
            pass_rates = [sum(row["criteria"].values()) / total_criteria for row in rows]
            critical_ids = {criterion["id"] for criterion in rubric["criteria"] if criterion["critical"]}
            critical_failures = sum(
                1 for row in rows for criterion_id in critical_ids if not row["criteria"][criterion_id]
            )
            token_values = [row["tokens"] for row in rows]
            latency_values = [row["latency_ms"] for row in rows]
            cost_values = [row["cost_usd"] for row in rows if row["cost_usd"] is not None]
            case_summary[condition] = {
                "runs": len(rows),
                "mean_pass_rate": sum(pass_rates) / len(pass_rates) if pass_rates else None,
                "critical_failures": critical_failures,
                "mean_tokens": sum(token_values) / len(token_values) if token_values else None,
                "mean_latency_ms": sum(latency_values) / len(latency_values) if latency_values else None,
                "mean_cost_usd": sum(cost_values) / len(cost_values) if cost_values else None,
                "tool_errors": sum(row["tool_errors"] for row in rows),
            }
        if complete:
            evaluated += 1
            baseline = case_summary["baseline"]
            treatment = case_summary["with-skill"]
            improved = (
                treatment["mean_pass_rate"] > baseline["mean_pass_rate"]
                and treatment["critical_failures"] <= baseline["critical_failures"]
                and treatment["tool_errors"] <= baseline["tool_errors"]
            )
            if improved:
                adopted += 1
            case_summary["decision"] = "adopt" if improved else "reject"
            case_summary["pass_rate_delta"] = treatment["mean_pass_rate"] - baseline["mean_pass_rate"]
            if baseline["mean_tokens"] and treatment["mean_tokens"] is not None:
                case_summary["token_overhead_ratio"] = treatment["mean_tokens"] / baseline["mean_tokens"]
            else:
                case_summary["token_overhead_ratio"] = None
            if baseline["mean_cost_usd"] and treatment["mean_cost_usd"] is not None:
                case_summary["cost_overhead_ratio"] = (
                    treatment["mean_cost_usd"] / baseline["mean_cost_usd"]
                )
            else:
                case_summary["cost_overhead_ratio"] = None
        else:
            case_summary["decision"] = "incomplete"
            case_summary["pass_rate_delta"] = None
            case_summary["token_overhead_ratio"] = None
            case_summary["cost_overhead_ratio"] = None
        summaries[case_id] = case_summary

    all_cases_complete = evaluated == len(rubric_by_case)
    all_evaluated_cases_improved = evaluated > 0 and evaluated == adopted
    return {
        "cases": len(rubric_by_case),
        "evaluated_cases": evaluated,
        "adopted_cases": adopted,
        "all_cases_complete": all_cases_complete,
        "all_evaluated_cases_improved": all_evaluated_cases_improved,
        "adoption_ready": all_cases_complete and all_evaluated_cases_improved,
        "warning": "Three repetitions detect gross regressions but are not a statistical significance claim.",
        "case_results": summaries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate task, fixture, and rubric definitions.")
    validate_parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)

    prepare_parser = subparsers.add_parser("prepare", help="Create isolated executor and grader packets.")
    prepare_parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    prepare_parser.add_argument("--output", type=Path)

    template_parser = subparsers.add_parser("score-template", help="Emit score JSONL rows to stdout.")
    template_parser.add_argument("--manifest", type=Path, required=True)

    score_parser = subparsers.add_parser("score", help="Validate and aggregate completed score rows.")
    score_parser.add_argument("--manifest", type=Path, required=True)
    score_parser.add_argument("--scores", type=Path, required=True)
    score_parser.add_argument("--allow-incomplete", action="store_true")
    score_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()
    try:
        if args.command == "validate":
            cases = load_cases(args.cases)
            print(f"task_cases={len(cases)} valid=true")
            return 0
        if args.command == "prepare":
            cases = load_cases(args.cases)
            output = args.output or Path(tempfile.mkdtemp(prefix="skill-evals-"))
            prepare(cases, output)
            print(output.resolve())
            return 0
        if args.command == "score-template":
            score_template(args.manifest)
            return 0
        if args.command == "score":
            result = score_runs(args.manifest, args.scores, args.allow_incomplete)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(
                    f"cases={result['cases']} evaluated={result['evaluated_cases']} "
                    f"adopted={result['adopted_cases']} "
                    f"complete={str(result['all_cases_complete']).lower()} "
                    f"adoption_ready={str(result['adoption_ready']).lower()}"
                )
                for case_id, case_result in result["case_results"].items():
                    print(
                        f"{case_id}: decision={case_result['decision']} "
                        f"delta={case_result['pass_rate_delta']} "
                        f"token_overhead={case_result['token_overhead_ratio']} "
                        f"cost_overhead={case_result['cost_overhead_ratio']}"
                    )
            return 0 if result["adoption_ready"] else 1
    except (OSError, ValueError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
