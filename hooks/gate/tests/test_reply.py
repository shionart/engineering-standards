"""Tests for the closing-block check: every reply must end with Updated, Created, Removed, Not done and the skills line."""

import json
import tempfile
import unittest
from pathlib import Path

from config import Config
from flagstore import FlagStore
from hook import handle
from reply_rules import missing_sections
from transcript import last_reply_text

GOOD = """Done.

**Updated:** none.
**Created:** a.py
**Removed:** none.
**Not done:** the rest.

Relevant skill(s) not used: `humanizer`."""


class MissingSectionsTests(unittest.TestCase):
    def test_a_complete_block_in_either_style_is_accepted(self):
        self.assertEqual(missing_sections(GOOD), [])
        plain = "Updated: x\nCreated: y\nRemoved: none\nNot done: z\nRelevant skill(s) not used: none"
        self.assertEqual(missing_sections(plain), [])
        listed = "- **Updated**: x\n- **Created**: y\n- **Removed**: none\n- **Not done**: z\nRelevant skills not used: none"
        self.assertEqual(missing_sections(listed), [])

    def test_each_missing_part_is_named(self):
        self.assertEqual(
            missing_sections("hello"),
            ["Updated", "Created", "Removed", "Not done", "Relevant skill(s) not used"],
        )
        without_skills = GOOD.rsplit("\n\n", 1)[0]
        self.assertEqual(missing_sections(without_skills), ["Relevant skill(s) not used"])
        without_removed = GOOD.replace("**Removed:** none.\n", "")
        self.assertEqual(missing_sections(without_removed), ["Removed"])

    def test_a_label_inside_a_sentence_does_not_count(self):
        text = "We updated: things and created: others.\nRelevant skill(s) not used: none"
        self.assertIn("Updated", missing_sections(text))


class TranscriptTests(unittest.TestCase):
    def write(self, folder, entries):
        path = Path(folder) / "t.jsonl"
        path.write_text("\n".join(json.dumps(e) for e in entries), encoding="utf-8")
        return str(path)

    def assistant(self, *blocks):
        return {"type": "assistant", "message": {"role": "assistant", "content": list(blocks)}}

    def test_the_text_of_the_last_assistant_message_is_returned(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(
                folder,
                [
                    {"type": "user", "message": {"role": "user", "content": "hi"}},
                    self.assistant({"type": "text", "text": "first"}),
                    self.assistant({"type": "text", "text": "part one"}, {"type": "text", "text": "part two"}),
                ],
            )
            self.assertEqual(last_reply_text(path), "part one\npart two")

    def test_a_last_message_with_only_a_tool_call_has_no_reply_text(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, [self.assistant({"type": "tool_use", "name": "Bash", "input": {}})])
            self.assertIsNone(last_reply_text(path))

    def test_a_missing_or_broken_transcript_gives_nothing(self):
        self.assertIsNone(last_reply_text("C:/no/such/file.jsonl"))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.jsonl"
            path.write_text("not json\n", encoding="utf-8")
            self.assertIsNone(last_reply_text(str(path)))


class ReplyGateTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.store = FlagStore(Path(self.folder.name))

    def tearDown(self):
        self.folder.cleanup()

    def run_reply(self, text, enabled=True, **extra):
        payload = {"session_id": "s1", "transcript_path": "t", **extra}
        config = Config(state_dir=Path(self.folder.name), reply_check=enabled)
        return handle("reply", payload, self.store, config, read_reply=lambda _path: text)

    def test_a_reply_without_the_block_is_sent_back_with_the_missing_parts(self):
        result = self.run_reply("All done.")
        self.assertEqual(result.exit_code, 2)
        self.assertIn("Updated", result.message)
        self.assertIn("Relevant skill(s) not used", result.message)

    def test_the_reply_check_is_skipped_unless_enabled(self):
        self.assertEqual(self.run_reply("All done.", enabled=False).exit_code, 0)

    def test_the_reply_message_is_neutral(self):
        self.assertNotIn("owner", self.run_reply("All done.").message.lower())

    def test_the_reply_message_says_how_to_turn_the_check_off(self):
        message = self.run_reply("All done.").message
        self.assertTrue(message.endswith("To turn this check off, set ENG_STANDARDS_REPLY_CHECK=0."))

    def test_a_complete_reply_finishes(self):
        self.assertEqual(self.run_reply(GOOD).exit_code, 0)

    def test_the_hook_never_loops_when_it_already_sent_the_reply_back_once(self):
        self.assertEqual(self.run_reply("All done.", stop_hook_active=True).exit_code, 0)

    def test_a_turn_with_no_reply_text_is_left_alone(self):
        self.assertEqual(self.run_reply(None).exit_code, 0)


if __name__ == "__main__":
    unittest.main()
