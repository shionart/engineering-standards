"""Tests for hooks/run.sh, the launcher. Needs bash; skipped where there is none."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

RUN_SH = Path(__file__).resolve().parents[2] / "run.sh"
BASH = shutil.which("bash")


@unittest.skipUnless(BASH, "bash not found")
class RunShTests(unittest.TestCase):
    def run_without_python(self, mode: str) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as empty_path:
            return subprocess.run(
                [BASH, str(RUN_SH), mode],
                input="{}",
                capture_output=True,
                text=True,
                env={"PATH": empty_path},
                timeout=30,
            )

    def test_session_start_tells_the_user_when_python_is_missing(self):
        result = self.run_without_python("reset")
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "SessionStart")
        self.assertEqual(
            output["additionalContext"], "engineering-standards gate is inactive: Python 3.10+ not found."
        )

    def test_the_other_modes_stay_silent_when_python_is_missing(self):
        for mode in ("gate", "mark", "agent_stop", "reply"):
            result = self.run_without_python(mode)
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""), mode)


if __name__ == "__main__":
    unittest.main()
