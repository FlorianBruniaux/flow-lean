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


class RunnerIsolationTest(unittest.TestCase):
    def test_empty_cwd_is_fresh_and_removed(self):
        with run_evals._runner_cwd({"cwd": "empty"}) as cwd:
            self.assertNotEqual(cwd, ROOT)
            self.assertEqual(list(cwd.iterdir()), [])
        self.assertFalse(cwd.exists())

    def test_repo_cwd_is_default(self):
        with run_evals._runner_cwd({}) as cwd:
            self.assertEqual(cwd, ROOT)

    def test_unknown_cwd_is_rejected(self):
        with self.assertRaises(ValueError):
            with run_evals._runner_cwd({"cwd": "home"}):
                pass

    def test_example_text_runner_is_isolated(self):
        config = json.loads((ROOT / "evals" / "runners.example.json").read_text(encoding="utf-8"))
        command = config["claude"]["command"]
        self.assertEqual(config["claude"]["cwd"], "empty")
        self.assertIn("--strict-mcp-config", command)
        self.assertIn("--system-prompt", command)
        tools = command.index("--tools")
        self.assertEqual(command[tools + 1], "")
        # --tools is variadic: another flag must follow, or it swallows the appended prompt.
        self.assertTrue(command[tools + 2].startswith("--"))

    def test_example_codex_runner_is_isolated(self):
        config = json.loads((ROOT / "evals" / "runners.example.json").read_text(encoding="utf-8"))
        codex = config["codex"]
        command = codex["command"]
        self.assertEqual(codex["cwd"], "empty")
        self.assertEqual(codex["response_format"], "codex-jsonl")
        for flag in ("--ignore-user-config", "--ephemeral"):
            self.assertIn(flag, command)
        self.assertEqual(command[command.index("--sandbox") + 1], "read-only")
        disabled = {command[i + 1] for i, part in enumerate(command) if part == "--disable"}
        self.assertTrue({"plugins", "apps", "hooks"} <= disabled)
        self.assertIn('web_search="disabled"', command)

    def test_runner_stdin_is_closed(self):
        completed = run_evals._run_command([sys.executable, "-c", "import sys; print(repr(sys.stdin.read()))"], ROOT)
        self.assertEqual(completed.stdout.strip(), "''")


if __name__ == "__main__":
    unittest.main()
