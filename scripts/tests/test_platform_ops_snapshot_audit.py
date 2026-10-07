"""Offline contract tests; temporary Git repositories, no cloud or network."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "platform_ops_snapshot_audit.py"
spec = importlib.util.spec_from_file_location("snapshot_audit", SCRIPT)
audit_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_tool)


class AuditContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.names = ["platform-ops-toolkit", "gitops", "iac_modules", "playbooks"]
        self.entry = ".github/workflows/daily.yml"
        workflow = """name: Daily
on:
  workflow_dispatch:
    inputs:
      unused: {type: string}
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Probe
        uses: ./.github/actions/probe
      - name: Run
        run: ./.github/scripts/probe.sh
        env:
          TEST_SECRET_LITERAL: SECRET_SENTINEL_MUST_NOT_BE_EXPORTED
  owner:
    uses: ai-workspace-infra/playbooks/.github/workflows/run.yml@main
"""
        self.config = {
            "audit_date": "2026-10-07", "repositories": {}, "entry_workflow": self.entry,
            "workflow_scope": {self.entry: "入口"}, "execution_mappings": [],
            "job_annotations": {"check": {"steps": {"Probe": {}, "Run": {}}}, "owner": {"steps": {}}},
        }
        self.repos = {}
        for name in self.names:
            repo = self.root / name
            repo.mkdir()
            self.command(repo, "init", "-q")
            (repo / "README.md").write_text("fixture\n")
            if name == "platform-ops-toolkit":
                for path, content in {
                    self.entry: workflow,
                    ".github/scripts/probe.sh": "#!/bin/sh\nterraform plan\n",
                    ".github/actions/probe/action.yml": "name: probe\nruns:\n  using: composite\n  steps:\n    - uses: actions/checkout@v7\n",
                }.items():
                    target = repo / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(content)
            self.command(repo, "add", ".")
            self.command(repo, "-c", "user.email=fixture@example.invalid", "-c", "user.name=Fixture",
                         "-c", "commit.gpgsign=false", "commit", "-qm", "fixture")
            sha = self.command(repo, "rev-parse", "HEAD")
            self.config["repositories"][name] = {"sha": sha, "remote": "ai-workspace-infra/" + name}
            self.repos[name] = audit_tool.Repository(repo, name, sha, "ai-workspace-infra/" + name)
        self.config_path = self.root / "config.json"
        self.save_config()

    @staticmethod
    def command(repo, *args):
        return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()

    def save_config(self):
        self.config_path.write_text(json.dumps(self.config))

    def run_main(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return audit_tool.main(["--config", str(self.config_path), "--infra-root", str(self.root),
                                    "--output-dir", str(self.root / "report"), *args])

    def test_github_on_is_not_boolean(self):
        parsed = audit_tool.load_yaml("on:\n  workflow_dispatch: {}\nflag: false\n")
        self.assertIn("on", parsed)
        self.assertIs(parsed["flag"], False)

    def test_uncommitted_worktree_is_ignored(self):
        path = self.root / "platform-ops-toolkit" / self.entry
        path.write_text("not even valid workflow YAML")
        report = audit_tool.audit(self.config, self.repos)
        self.assertEqual(report["daily"]["name"], "Daily")

    def test_owner_and_composite_calls_are_audited(self):
        report = audit_tool.audit(self.config, self.repos)
        codes = {f["code"] for f in report["findings"]}
        self.assertIn("FLOATING_OWNER_REF", codes)
        self.assertIn("UNREFERENCED_INPUT", codes)
        self.assertTrue(any(u["job"] == "__composite_action__" for u in report["uses"]))
        self.assertTrue(any(f["code"] == "EXECUTION_CANDIDATE" and f["severity"] == "review"
                            for f in report["findings"]))

    def test_missing_existing_mapping_is_an_error(self):
        self.config["execution_mappings"] = [{"id": "I-test", "implementations": [
            {"repository": "iac_modules", "path": "modules/does-not-exist"}]}]
        report = audit_tool.audit(self.config, self.repos)
        self.assertTrue(any(f["code"] == "MAPPING_PATH_MISSING" and f["severity"] == "error"
                            for f in report["findings"]))

    def test_renamed_step_is_not_silently_reused(self):
        self.config["job_annotations"]["check"]["steps"]["Removed step"] = {}
        report = audit_tool.audit(self.config, self.repos)
        self.assertIn("STALE_STEP_MAPPING", {f["code"] for f in report["findings"]})

    def test_generated_region_preserves_human_plan(self):
        text = "manual before\n" + audit_tool.BEGIN + "\nold\n" + audit_tool.END + "\nmanual after"
        updated = audit_tool.replace_region(text, "generated table")
        self.assertTrue(updated.startswith("manual before\n"))
        self.assertTrue(updated.endswith("\nmanual after"))
        with self.assertRaises(ValueError):
            audit_tool.replace_region("no markers", "generated")

    def test_check_is_deterministic_and_does_not_repair_drift(self):
        self.assertEqual(self.run_main(), 0)
        self.assertEqual(self.run_main("--check"), 0)
        target = self.root / "report/tables.md"
        target.write_text("manual drift")
        self.assertEqual(self.run_main("--check"), 1)
        self.assertEqual(target.read_text(), "manual drift")

    def test_no_raw_env_secret_in_persisted_report(self):
        self.assertEqual(self.run_main(), 0)
        for path in (self.root / "report").iterdir():
            self.assertNotIn("SECRET_SENTINEL_MUST_NOT_BE_EXPORTED", path.read_text())

    def test_warning_threshold_and_argument_errors(self):
        self.assertEqual(self.run_main("--fail-on", "warning"), 1)
        self.assertEqual(self.run_main("--check", "--update-lock"), 2)
        self.assertEqual(self.run_main("--ref", "not-a-repository=main"), 2)

    def test_missing_entry_fails_without_publishing_success_report(self):
        self.config["entry_workflow"] = ".github/workflows/missing.yml"
        self.save_config()
        self.assertEqual(self.run_main(), 2)
        self.assertFalse((self.root / "report/audit.json").exists())


if __name__ == "__main__":
    unittest.main()
