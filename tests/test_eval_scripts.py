from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import eval_routing, eval_tasks, validate_skills


class RoutingEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = eval_routing.read_jsonl(
            eval_tasks.ROOT / "quality" / "routing" / "cases.jsonl"
        )
        self.skills = {path.parent.name for path in eval_tasks.ROOT.glob("*/SKILL.md")}
        eval_routing.validate_cases(self.cases, self.skills)

    def perfect_predictions(self) -> list[dict[str, object]]:
        predictions: list[dict[str, object]] = []
        for case in self.cases:
            selected = [] if case["expected_primary"] is None else [case["expected_primary"]]
            selected.extend(case["expected_secondary"])
            predictions.append({"id": case["id"], "selected": selected})
        return predictions

    def test_perfect_ordered_predictions_pass(self) -> None:
        result = eval_routing.score(self.cases, self.perfect_predictions(), self.skills)
        self.assertEqual(result["primary_accuracy"], 1.0)
        self.assertEqual(result["ordered_exact_rate"], 1.0)
        self.assertEqual(result["macro_f1"], 1.0)
        self.assertEqual(result["forbidden_violations"], [])

    def test_forbidden_selection_is_reported(self) -> None:
        predictions = self.perfect_predictions()
        predictions[0]["selected"].append(self.cases[0]["forbidden"][0])
        result = eval_routing.score(self.cases, predictions, self.skills)
        self.assertEqual(len(result["forbidden_violations"]), 1)


class RepositoryValidationTests(unittest.TestCase):
    def test_evaluation_result_markdown_is_treated_as_immutable_artifact(self) -> None:
        root = Path("/repository")
        result = root / "quality" / "results" / "2026-07-20" / "response.md"
        regular_doc = root / "impl-review" / "SKILL.md"
        self.assertTrue(validate_skills.is_evaluation_result_artifact(root, result))
        self.assertFalse(validate_skills.is_evaluation_result_artifact(root, regular_doc))


class TaskEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(prefix="skill-eval-test-")
        self.packet_root = Path(self.tempdir.name)
        self.cases = eval_tasks.load_cases(eval_tasks.DEFAULT_CASES)
        eval_tasks.prepare(self.cases, self.packet_root)
        self.manifest_path = self.packet_root / "manifest.json"
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def score_rows(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for case in self.manifest["cases"]:
            rubric = json.loads(
                (self.packet_root / case["rubric_path"]).read_text(encoding="utf-8")
            )
            criterion_ids = [criterion["id"] for criterion in rubric["criteria"]]
            for condition in eval_tasks.CONDITIONS:
                for repetition in range(1, case["repetitions"] + 1):
                    treatment = condition == "with-skill"
                    rows.append(
                        {
                            "case_id": case["id"],
                            "condition": condition,
                            "repetition": repetition,
                            "criteria": {
                                criterion_id: treatment for criterion_id in criterion_ids
                            },
                            "tokens": 120 if treatment else 100,
                            "latency_ms": 1200 if treatment else 1000,
                            "cost_usd": 0.012 if treatment else 0.01,
                            "tool_errors": 0,
                            "notes": "synthetic unit-test score",
                        }
                    )
        return rows

    def run_score(
        self, rows: list[dict[str, object]], allow_incomplete: bool = False
    ) -> dict[str, object]:
        with mock.patch.object(eval_tasks, "read_jsonl", return_value=rows):
            return eval_tasks.score_runs(
                self.manifest_path, Path("unused-by-mocked-reader"), allow_incomplete
            )

    def test_packets_separate_executor_content_from_rubric(self) -> None:
        tasks = list((self.packet_root / "run-packets").rglob("task.md"))
        rubrics = list((self.packet_root / "grader-packets").glob("*.json"))
        self.assertEqual(len(tasks), len(self.cases))
        self.assertEqual(len(rubrics), len(self.cases))
        executor_text = "\n".join(path.read_text(encoding="utf-8") for path in tasks)
        for rubric_path in rubrics:
            rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
            for criterion in rubric["criteria"]:
                self.assertNotIn(criterion["description"], executor_text)

    def test_valid_unified_diff_is_accepted(self) -> None:
        patch_path = self.packet_root / "valid.diff"
        patch_path.write_text(
            """diff --git a/example.txt b/example.txt
--- a/example.txt
+++ b/example.txt
@@ -1,2 +1,2 @@
 keep
-old
+new
""",
            encoding="utf-8",
        )
        eval_tasks.validate_unified_diff(patch_path, "valid-patch")

    def test_unified_diff_hunk_count_mismatch_is_rejected(self) -> None:
        patch_path = self.packet_root / "invalid.diff"
        patch_path.write_text(
            """diff --git a/example.txt b/example.txt
--- a/example.txt
+++ b/example.txt
@@ -1,2 +1,3 @@
 keep
-old
+new
""",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "hunk count mismatch"):
            eval_tasks.validate_unified_diff(patch_path, "invalid-patch")

    def test_complete_strict_improvement_is_adoption_ready(self) -> None:
        result = self.run_score(self.score_rows())
        self.assertTrue(result["all_cases_complete"])
        self.assertTrue(result["all_evaluated_cases_improved"])
        self.assertTrue(result["adoption_ready"])

    def test_partial_results_are_never_adoption_ready(self) -> None:
        first_case = self.manifest["cases"][0]["id"]
        rows = [row for row in self.score_rows() if row["case_id"] == first_case]
        result = self.run_score(rows, allow_incomplete=True)
        self.assertFalse(result["all_cases_complete"])
        self.assertTrue(result["all_evaluated_cases_improved"])
        self.assertFalse(result["adoption_ready"])

    def test_unknown_provider_cost_is_preserved_as_null(self) -> None:
        rows = self.score_rows()
        for row in rows:
            row["cost_usd"] = None
        result = self.run_score(rows)
        first_case = self.manifest["cases"][0]["id"]
        case_result = result["case_results"][first_case]
        self.assertIsNone(case_result["baseline"]["mean_cost_usd"])
        self.assertIsNone(case_result["with-skill"]["mean_cost_usd"])
        self.assertIsNone(case_result["cost_overhead_ratio"])

    def test_invalid_provider_cost_is_rejected(self) -> None:
        rows = self.score_rows()
        rows[0]["cost_usd"] = "unknown"
        with self.assertRaisesRegex(ValueError, "cost_usd must be null"):
            self.run_score(rows)

    def test_critical_regression_rejects_higher_average(self) -> None:
        target = "skill-improvement-commit-message"
        rubric = json.loads(
            (self.packet_root / "grader-packets" / f"{target}.json").read_text(encoding="utf-8")
        )
        critical = {criterion["id"] for criterion in rubric["criteria"] if criterion["critical"]}
        rows = self.score_rows()
        for row in rows:
            if row["case_id"] != target:
                continue
            for criterion_id in row["criteria"]:
                row["criteria"][criterion_id] = (
                    criterion_id in critical
                    if row["condition"] == "baseline"
                    else criterion_id not in critical
                )
        result = self.run_score(rows)
        target_result = result["case_results"][target]
        self.assertGreater(target_result["pass_rate_delta"], 0)
        self.assertEqual(target_result["decision"], "reject")
        self.assertFalse(result["adoption_ready"])

    def test_tool_error_regression_rejects_improvement(self) -> None:
        target = self.manifest["cases"][0]["id"]
        rows = self.score_rows()
        for row in rows:
            if row["case_id"] == target and row["condition"] == "with-skill":
                row["tool_errors"] = 1
        result = self.run_score(rows)
        self.assertEqual(result["case_results"][target]["decision"], "reject")
        self.assertFalse(result["adoption_ready"])

    def test_packet_tampering_is_detected(self) -> None:
        first_task = self.packet_root / self.manifest["cases"][0]["task_path"]
        first_task.write_text(
            first_task.read_text(encoding="utf-8") + "\ntampered\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "changed after preparation"):
            eval_tasks.validate_manifest_integrity(self.manifest_path, self.manifest)


if __name__ == "__main__":
    unittest.main()
