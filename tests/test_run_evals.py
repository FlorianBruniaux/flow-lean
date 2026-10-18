import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("run_evals", ROOT / "scripts" / "run_evals.py")
run_evals = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run_evals)

# Accents, an arrow and U+2014: the characters cp1252 decoding corrupted.
SAMPLE = "Complexité, défis → ok — fin"


class Utf8DecodingTest(unittest.TestCase):
    def test_runner_output_is_decoded_as_utf8(self):
        script = f"import sys; sys.stdout.buffer.write({SAMPLE!r}.encode('utf-8'))"
        completed = run_evals._run_command([sys.executable, "-c", script], ROOT)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, SAMPLE)
        self.assertIn("—", completed.stdout)

    def test_claude_event_array_keeps_unicode(self):
        events = [
            {"type": "system", "subtype": "init"},
            {"type": "result", "result": SAMPLE, "usage": {}, "total_cost_usd": 0.01},
        ]
        script = (
            "import sys; sys.stdout.buffer.write("
            f"{json.dumps(events, ensure_ascii=False)!r}.encode('utf-8'))"
        )
        completed = run_evals._run_command([sys.executable, "-c", script], ROOT)
        text, _, cost = run_evals._parse_response(completed.stdout, "claude-json")
        self.assertEqual(text, SAMPLE)
        self.assertEqual(cost, 0.01)


if __name__ == "__main__":
    unittest.main()
