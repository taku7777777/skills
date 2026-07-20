#!/usr/bin/env python3
"""Validate every skill package and the repository-level evaluation assets."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
TOC_RE = re.compile(r"^## (?:目次|Table of Contents|Contents)\s*$", re.MULTILINE)
SAFE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def parse_frontmatter(path: Path, validation: Validation) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        validation.error(f"{path}: YAML frontmatter is missing or malformed")
        return {}

    values: dict[str, str] = {}
    for lineno, raw_line in enumerate(match.group("body").splitlines(), start=2):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if ":" not in raw_line:
            validation.error(f"{path}:{lineno}: unsupported frontmatter syntax")
            continue
        key, value = raw_line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in values:
            validation.error(f"{path}:{lineno}: duplicate frontmatter key {key!r}")
        values[key] = value
    return values


def validate_markdown_links(root: Path, path: Path, validation: Validation) -> None:
    text = path.read_text(encoding="utf-8")
    for raw_target in MARKDOWN_LINK_RE.findall(text):
        target = raw_target.strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        target = target.split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            validation.error(f"{path}: local link escapes repository: {raw_target}")
            continue
        if not resolved.exists():
            validation.error(f"{path}: broken local link: {raw_target}")


def is_evaluation_result_artifact(root: Path, path: Path) -> bool:
    """Return whether a Markdown file is immutable/generated evaluation evidence."""
    try:
        relative_parts = path.resolve().relative_to(root.resolve()).parts
    except ValueError:
        return False
    return relative_parts[:2] == ("quality", "results")


def validate_eval_markdown(path: Path, validation: Validation, strict: bool) -> None:
    text = path.read_text(encoding="utf-8")
    positive = len(re.findall(r"^\| F\d+\s*\|", text, re.MULTILINE))
    negative = len(re.findall(r"^\| N\d+\s*\|", text, re.MULTILINE))
    scenarios = len(re.findall(r"^### S\d+:", text, re.MULTILINE))
    if positive < 5:
        validation.error(f"{path}: needs at least 5 positive trigger cases; found {positive}")
    if negative < 3:
        validation.error(f"{path}: needs at least 3 negative trigger cases; found {negative}")
    if scenarios < 3:
        validation.error(f"{path}: needs at least 3 task scenarios; found {scenarios}")
    if "(未実施)" in text:
        message = f"{path}: one or more model evaluations remain unexecuted"
        if strict:
            validation.error(message)
        else:
            validation.warn(message)


def load_json(path: Path, validation: Validation) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        validation.error(f"{path}: invalid JSON: {exc}")
        return None


def load_jsonl(path: Path, validation: Validation) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        validation.error(f"{path}: cannot read: {exc}")
        return records
    for lineno, line in enumerate(lines, start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            validation.error(f"{path}:{lineno}: invalid JSON: {exc}")
            continue
        if not isinstance(record, dict):
            validation.error(f"{path}:{lineno}: each line must be a JSON object")
            continue
        record["_line"] = lineno
        records.append(record)
    return records


def resolve_repo_file(
    root: Path, raw_path: object, label: str, validation: Validation
) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path:
        validation.error(f"{label}: path must be a non-empty string")
        return None
    candidate = (root / raw_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        validation.error(f"{label}: path escapes repository: {raw_path!r}")
        return None
    if not candidate.is_file():
        validation.error(f"{label}: missing file {raw_path!r}")
        return None
    return candidate


def validate_sources(
    root: Path, skills: set[str], validation: Validation, strict: bool
) -> None:
    path = root / "quality" / "sources.json"
    data = load_json(path, validation)
    if not isinstance(data, list):
        validation.error(f"{path}: top-level value must be an array")
        return
    required = {
        "id",
        "title",
        "url",
        "status",
        "published_at",
        "accessed_at",
        "review_due",
        "applies_to",
        "claims",
    }
    seen: set[str] = set()
    for index, source in enumerate(data):
        if not isinstance(source, dict):
            validation.error(f"{path}: item {index} must be an object")
            continue
        missing = required - source.keys()
        if missing:
            validation.error(f"{path}: item {index} missing {sorted(missing)}")
            continue
        if not isinstance(source["id"], str) or not SAFE_ID_RE.fullmatch(source["id"]):
            source_id = str(source["id"])
            validation.error(f"{path}: invalid source id {source_id!r}")
        else:
            source_id = source["id"]
        if source_id in seen:
            validation.error(f"{path}: duplicate source id {source_id}")
        seen.add(source_id)
        parsed = urlparse(str(source["url"]))
        if parsed.scheme != "https" or not parsed.netloc:
            validation.error(f"{path}: source {source_id} must use an absolute HTTPS URL")
        if source["status"] not in {"official", "peer-reviewed", "preprint", "industry-research"}:
            validation.error(f"{path}: source {source_id} has unsupported status {source['status']!r}")
        applies_to = source["applies_to"]
        if (
            not isinstance(applies_to, list)
            or not applies_to
            or any(not isinstance(skill, str) for skill in applies_to)
        ):
            validation.error(f"{path}: source {source_id} needs applies_to skill names")
        else:
            unknown_skills = set(applies_to) - skills
            if unknown_skills:
                validation.error(
                    f"{path}: source {source_id} applies to unknown skills {sorted(unknown_skills)}"
                )
            if len(applies_to) != len(set(applies_to)):
                validation.error(f"{path}: source {source_id} has duplicate applies_to entries")
        if (
            not isinstance(source["claims"], list)
            or not source["claims"]
            or any(not isinstance(claim, str) or not claim.strip() for claim in source["claims"])
        ):
            validation.error(f"{path}: source {source_id} needs at least one claim")
        for field in ("accessed_at", "review_due"):
            try:
                parsed_date = date.fromisoformat(str(source[field]))
            except ValueError:
                validation.error(f"{path}: source {source_id} has invalid {field}: {source[field]!r}")
                continue
            if field == "review_due" and parsed_date < date.today():
                message = f"{path}: source {source_id} review is overdue ({parsed_date.isoformat()})"
                validation.error(message) if strict else validation.warn(message)


def validate_routing_cases(root: Path, skills: set[str], validation: Validation) -> None:
    path = root / "quality" / "routing" / "cases.jsonl"
    records = load_jsonl(path, validation)
    seen: set[str] = set()
    primary_coverage: set[str] = set()
    null_cases = 0
    multi_skill_cases = 0
    for record in records:
        lineno = record.get("_line")
        required = {"id", "prompt", "expected_primary", "expected_secondary", "forbidden"}
        missing = required - record.keys()
        if missing:
            validation.error(f"{path}:{lineno}: missing {sorted(missing)}")
            continue
        extra = set(record) - required - {"_line"}
        if extra:
            validation.error(f"{path}:{lineno}: unexpected fields {sorted(extra)}")
        if not isinstance(record["id"], str) or not SAFE_ID_RE.fullmatch(record["id"]):
            case_id = str(record["id"])
            validation.error(f"{path}:{lineno}: invalid id {case_id!r}")
        else:
            case_id = record["id"]
        if case_id in seen:
            validation.error(f"{path}:{lineno}: duplicate id {case_id}")
        seen.add(case_id)
        if not isinstance(record["prompt"], str) or not record["prompt"].strip():
            validation.error(f"{path}:{lineno}: prompt must be a non-empty string")
        primary = record["expected_primary"]
        if primary is not None and not isinstance(primary, str):
            validation.error(f"{path}:{lineno}: expected_primary must be a skill name or null")
            continue
        secondary = record["expected_secondary"]
        forbidden = record["forbidden"]
        if not isinstance(secondary, list) or any(not isinstance(item, str) for item in secondary):
            validation.error(f"{path}:{lineno}: expected_secondary must be an array of skill names")
            continue
        if not isinstance(forbidden, list) or any(not isinstance(item, str) for item in forbidden):
            validation.error(f"{path}:{lineno}: forbidden must be an array of skill names")
            continue
        if primary is None:
            null_cases += 1
            if secondary:
                validation.error(f"{path}:{lineno}: null primary cannot have secondary skills")
        else:
            primary_coverage.add(primary)
        if secondary:
            multi_skill_cases += 1
        labels = [primary, *secondary, *forbidden]
        for label in labels:
            if label is not None and label not in skills:
                validation.error(f"{path}:{lineno}: unknown skill {label!r}")
        selected = ([] if primary is None else [primary]) + secondary
        if len(selected) != len(set(selected)):
            validation.error(f"{path}:{lineno}: expected skills contain duplicates")
        if len(forbidden) != len(set(forbidden)):
            validation.error(f"{path}:{lineno}: forbidden skills contain duplicates")
        if set(selected) & set(forbidden):
            validation.error(f"{path}:{lineno}: a skill cannot be expected and forbidden")
    missing_primary = skills - primary_coverage
    if missing_primary:
        validation.error(f"{path}: missing primary routing coverage for {sorted(missing_primary)}")
    if not null_cases:
        validation.error(f"{path}: needs at least one no-skill routing case")
    if not multi_skill_cases:
        validation.error(f"{path}: needs at least one ordered multi-skill routing case")


def validate_task_cases(root: Path, skills: set[str], validation: Validation) -> None:
    path = root / "quality" / "tasks" / "cases.jsonl"
    records = load_jsonl(path, validation)
    seen: set[str] = set()
    skill_coverage: set[str] = set()
    for record in records:
        lineno = record.get("_line")
        required = {"id", "skill", "prompt", "fixture", "rubric", "repetitions"}
        missing = required - record.keys()
        if missing:
            validation.error(f"{path}:{lineno}: missing {sorted(missing)}")
            continue
        extra = set(record) - required - {"_line"}
        if extra:
            validation.error(f"{path}:{lineno}: unexpected fields {sorted(extra)}")
        if not isinstance(record["id"], str) or not SAFE_ID_RE.fullmatch(record["id"]):
            case_id = str(record["id"])
            validation.error(f"{path}:{lineno}: invalid id {case_id!r}")
        else:
            case_id = record["id"]
        if case_id in seen:
            validation.error(f"{path}:{lineno}: duplicate id {case_id}")
        seen.add(case_id)
        skill = record["skill"]
        if not isinstance(skill, str) or skill not in skills:
            validation.error(f"{path}:{lineno}: unknown skill {record['skill']!r}")
            continue
        skill_coverage.add(skill)
        if not isinstance(record["prompt"], str) or not record["prompt"].strip():
            validation.error(f"{path}:{lineno}: prompt must be a non-empty string")
        if (
            not isinstance(record["repetitions"], int)
            or isinstance(record["repetitions"], bool)
            or record["repetitions"] < 3
        ):
            validation.error(f"{path}:{lineno}: repetitions must be an integer >= 3")
        fixture_path = resolve_repo_file(root, record["fixture"], f"{path}:{lineno}: fixture", validation)
        rubric_path = resolve_repo_file(root, record["rubric"], f"{path}:{lineno}: rubric", validation)
        if fixture_path is not None:
            expected_fixture_root = (root / "quality" / "fixtures" / skill).resolve()
            try:
                fixture_path.relative_to(expected_fixture_root)
            except ValueError:
                validation.error(f"{path}:{lineno}: fixture must be under quality/fixtures/{skill}/")
        if rubric_path is not None:
            expected_rubric_root = (root / "quality" / "graders").resolve()
            try:
                rubric_path.relative_to(expected_rubric_root)
            except ValueError:
                validation.error(f"{path}:{lineno}: rubric must be under quality/graders/")
        rubric = load_json(rubric_path, validation) if rubric_path is not None else None
        if not isinstance(rubric, dict) or rubric.get("case_id") != case_id:
            validation.error(f"{rubric_path}: case_id must equal {case_id!r}")
            continue
        if set(rubric) != {"case_id", "criteria"}:
            validation.error(f"{rubric_path}: fields must be exactly case_id and criteria")
        criteria = rubric.get("criteria")
        if not isinstance(criteria, list) or not criteria:
            validation.error(f"{rubric_path}: criteria must be a non-empty array")
            continue
        criterion_ids: set[str] = set()
        critical_count = 0
        for criterion in criteria:
            if not isinstance(criterion, dict) or set(criterion) != {"id", "description", "critical"}:
                validation.error(f"{rubric_path}: every criterion needs id, description, and critical")
                continue
            if not isinstance(criterion["id"], str) or not SAFE_ID_RE.fullmatch(criterion["id"]):
                criterion_id = str(criterion["id"])
                validation.error(f"{rubric_path}: invalid criterion id {criterion_id!r}")
            else:
                criterion_id = criterion["id"]
            if criterion_id in criterion_ids:
                validation.error(f"{rubric_path}: duplicate criterion id {criterion_id}")
            criterion_ids.add(criterion_id)
            if not isinstance(criterion["description"], str) or not criterion["description"].strip():
                validation.error(f"{rubric_path}: criterion {criterion_id} needs a description")
            if not isinstance(criterion["critical"], bool):
                validation.error(f"{rubric_path}: criterion {criterion_id} critical must be boolean")
            elif criterion["critical"]:
                critical_count += 1
        if not critical_count:
            validation.error(f"{rubric_path}: needs at least one critical criterion")
    missing_skills = skills - skill_coverage
    if missing_skills:
        validation.error(f"{path}: missing held-out task coverage for {sorted(missing_skills)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat unexecuted model evaluations as errors (use for release readiness, not ordinary CI).",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    validation = Validation()

    skill_dirs = sorted(path.parent for path in root.glob("*/SKILL.md"))
    skills = {path.name for path in skill_dirs}
    if not skill_dirs:
        validation.error(f"{root}: no skill directories found")

    for skill_dir in skill_dirs:
        skill_path = skill_dir / "SKILL.md"
        frontmatter = parse_frontmatter(skill_path, validation)
        if set(frontmatter) != {"name", "description"}:
            validation.error(
                f"{skill_path}: frontmatter keys must be exactly name and description; "
                f"found {sorted(frontmatter)}"
            )
        if frontmatter.get("name") != skill_dir.name:
            validation.error(f"{skill_path}: name must match directory {skill_dir.name!r}")
        if not frontmatter.get("description"):
            validation.error(f"{skill_path}: description must not be empty")
        line_count = len(skill_path.read_text(encoding="utf-8").splitlines())
        if line_count > 500:
            validation.error(f"{skill_path}: {line_count} lines exceeds the 500-line limit")
        eval_path = skill_dir / "evals.md"
        if not eval_path.is_file():
            validation.error(f"{skill_dir}: evals.md is missing")
        else:
            validate_eval_markdown(eval_path, validation, args.strict)
        worked_example = skill_dir / "references" / "worked-example.md"
        if not worked_example.is_file():
            validation.error(f"{skill_dir}: references/worked-example.md is missing")
        openai_yaml = skill_dir / "agents" / "openai.yaml"
        if not openai_yaml.is_file():
            validation.error(f"{skill_dir}: agents/openai.yaml is missing")
        else:
            metadata = openai_yaml.read_text(encoding="utf-8")
            for key in ("display_name", "short_description", "default_prompt"):
                if not re.search(rf'^\s+{key}: "[^"]+"\s*$', metadata, re.MULTILINE):
                    validation.error(f"{openai_yaml}: missing quoted interface.{key}")
            if f"${skill_dir.name}" not in metadata:
                validation.error(
                    f"{openai_yaml}: interface.default_prompt must mention ${skill_dir.name}"
                )

    for markdown in sorted(root.rglob("*.md")):
        if ".git" in markdown.parts or is_evaluation_result_artifact(root, markdown):
            continue
        validate_markdown_links(root, markdown, validation)
        if "references" in markdown.parts:
            line_count = len(markdown.read_text(encoding="utf-8").splitlines())
            if line_count > 100 and not TOC_RE.search(markdown.read_text(encoding="utf-8")):
                validation.error(f"{markdown}: references over 100 lines need a table of contents")

    validate_sources(root, skills, validation, args.strict)
    validate_routing_cases(root, skills, validation)
    validate_task_cases(root, skills, validation)

    for warning in validation.warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    for error in validation.errors:
        print(f"ERROR: {error}", file=sys.stderr)

    print(
        f"skills={len(skill_dirs)} errors={len(validation.errors)} "
        f"warnings={len(validation.warnings)} strict={args.strict}"
    )
    return 1 if validation.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
