import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Accents, an arrow and U+2014: the characters cp1252 decoding corrupted.
SAMPLE = "Complexité, défis → ok — fin"


class Utf8DecodingTest(unittest.TestCase):
    def run_fixture(self, stdout):
        # Exercise the current journaled CLI, including its explicit UTF-8 decode.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases, config, output = (root / n for n in ('cases.jsonl', 'runner.json', 'output.jsonl'))
            cases.write_text(json.dumps({'id': 'utf8', 'category': 'encoding',
                'prompt': 'Return the fixture.', 'risk': 'low', 'criteria': ['Exact text']}) + '\n', encoding='utf-8')
            script = f"import sys; sys.stdout.buffer.write({stdout!r}.encode('utf-8'))"
            config.write_text(json.dumps({'fixture': {'command': [sys.executable, '-c', script],
                'response_format': 'claude-json'}}), encoding='utf-8')
            completed = subprocess.run([sys.executable, str(ROOT / 'scripts/run_evals.py'),
                'run', '--cases', str(cases), '--runner-config', str(config), '--runner', 'fixture',
                '--condition', 'baseline', '--trials', '1', '--retries', '0', '--budget-usd', '1',
                '--output', str(output)], capture_output=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            return json.loads(output.read_text(encoding='utf-8'))

    def test_runner_output_is_decoded_as_utf8(self):
        row = self.run_fixture(json.dumps({'result': SAMPLE, 'total_cost_usd': 0.01}, ensure_ascii=False))
        self.assertEqual(row['response'], SAMPLE)

    def test_claude_event_array_keeps_unicode(self):
        events = [
            {"type": "system", "subtype": "init"},
            {"type": "result", "result": SAMPLE, "usage": {}, "total_cost_usd": 0.01},
        ]
        row = self.run_fixture(json.dumps(events, ensure_ascii=False))
        self.assertEqual(row['response'], SAMPLE)
        self.assertEqual(row['cost_usd'], 0.01)


if __name__ == "__main__":
    unittest.main()
