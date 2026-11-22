"""Tests for the engineering-standards gate. Run: python -m unittest discover -s tests -t . (from hooks/gate/)."""

import tempfile
import unittest
from pathlib import Path

from gate_rules import bash_writes_code, is_code_path, is_standards_skill, needs_gate
from flagstore import FlagStore
from hook import handle
from config import Config


class CodePathTests(unittest.TestCase):
    def test_code_and_script_files_are_code(self):
        for path in ["a/b.rs", "x.PY", "C:\\p\\main.ts", "run.sh", "t.ps1", "m.sql", "s.css", "p.html", "b.mjs"]:
            self.assertTrue(is_code_path(path), path)

    def test_documents_and_data_are_not_code(self):
        for path in ["README.md", "notes.txt", "settings.json", "plan.yaml", "memory/x.md", "image.png", ""]:
            self.assertFalse(is_code_path(path), path)


class ToolGateTests(unittest.TestCase):
    def test_edit_write_and_notebook_of_code_are_gated(self):
        for tool in ["Edit", "Write", "NotebookEdit"]:
            self.assertTrue(needs_gate(tool, {"file_path": "src/lib.rs"}), tool)

    def test_edit_of_a_document_and_read_tools_are_not_gated(self):
        self.assertFalse(needs_gate("Write", {"file_path": "docs/plan.md"}))
        self.assertFalse(needs_gate("Read", {"file_path": "src/lib.rs"}))
        self.assertFalse(needs_gate("Grep", {"pattern": "x"}))

    def test_bash_is_gated_only_when_it_writes_a_code_file(self):
        self.assertTrue(needs_gate("Bash", {"command": "cat > a.py <<EOF\nprint(1)\nEOF"}))
        self.assertFalse(needs_gate("Bash", {"command": "cargo test -p x 2>&1 | tail -5"}))


class BashWriteTests(unittest.TestCase):
    def test_writes_to_code_files_are_caught(self):
        for command in [
            "cat > crates/a/src/lib.rs <<'EOF'\nfn main(){}\nEOF",
            "echo x >> tools/run.sh",
            "printf hi | tee web/src/main.ts",
            "sed -i 's/a/b/' web/app.css",
            'python - <<PY\nfrom edit import edit\nedit("crates/x/src/lib.rs", [("a","b")])\nPY',
            "python -c \"open('a.py','w').write('x')\"",
            "python -c \"from pathlib import Path; Path('b.rs').write_text('x')\"",
        ]:
            self.assertTrue(bash_writes_code(command), command)

    def test_reads_builds_and_non_code_writes_are_not_caught(self):
        for command in [
            "cargo test --workspace 2>&1 | tail -5",
            "python tools/export_docs.py",
            "git diff crates/a/src/lib.rs",
            "ls > out.txt",
            "echo hi >> notes.md",
            "cat src/main.rs | head",
            "node --test src/model.test.ts > /dev/null 2>&1",
            "grep -n foo web/src/main.ts",
        ]:
            self.assertFalse(bash_writes_code(command), command)


class SkillNameTests(unittest.TestCase):
    def test_the_standards_skill_is_recognised_with_or_without_a_plugin_prefix(self):
        self.assertTrue(is_standards_skill("engineering-standards"))
        self.assertTrue(is_standards_skill("x:engineering-standards"))
        self.assertTrue(is_standards_skill("engineering-standards:engineering-standards"))
        self.assertFalse(is_standards_skill("engineering-standards:other"))
        self.assertFalse(is_standards_skill("impeccable"))
        self.assertFalse(is_standards_skill(None))


class FlagStoreTests(unittest.TestCase):
    def test_mark_has_and_clear_are_per_session(self):
        with tempfile.TemporaryDirectory() as folder:
            store = FlagStore(Path(folder))
            self.assertFalse(store.has("s1"))
            store.mark("s1")
            self.assertTrue(store.has("s1"))
            self.assertFalse(store.has("s2"))
            store.clear("s1")
            self.assertFalse(store.has("s1"))
            store.clear("s1")  # clearing twice is harmless

    def test_a_session_id_cannot_escape_the_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            store = FlagStore(Path(folder))
            store.mark("../evil")
            self.assertEqual([p.parent for p in Path(folder).rglob("*") if p.is_file()], [Path(folder)])


class HandleTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.store = FlagStore(Path(self.folder.name))
        self.config = Config(state_dir=Path(self.folder.name), reply_check=False)

    def tearDown(self):
        self.folder.cleanup()

    def edit_payload(self, session="s1", path="src/lib.rs"):
        return {"session_id": session, "tool_name": "Edit", "tool_input": {"file_path": path}}

    def test_code_edit_is_blocked_until_the_skill_was_used_in_this_session(self):
        blocked = handle("gate", self.edit_payload(), self.store, self.config)
        self.assertEqual(blocked.exit_code, 2)
        self.assertIn("engineering-standards", blocked.message)
        skill = {"session_id": "s1", "tool_name": "Skill", "tool_input": {"skill": "engineering-standards"}}
        self.assertEqual(handle("mark", skill, self.store, self.config).exit_code, 0)
        self.assertEqual(handle("gate", self.edit_payload(), self.store, self.config).exit_code, 0)
        self.assertEqual(handle("gate", self.edit_payload(session="s2"), self.store, self.config).exit_code, 2)

    def test_another_skill_does_not_unlock_the_gate(self):
        other = {"session_id": "s1", "tool_name": "Skill", "tool_input": {"skill": "impeccable"}}
        handle("mark", other, self.store, self.config)
        self.assertEqual(handle("gate", self.edit_payload(), self.store, self.config).exit_code, 2)

    def test_the_block_message_is_neutral(self):
        message = handle("gate", self.edit_payload(), self.store, self.config).message
        self.assertIn("project's engineering standards", message)
        self.assertNotIn("owner", message.lower())

    def test_documents_pass_without_the_skill(self):
        self.assertEqual(handle("gate", self.edit_payload(path="notes.md"), self.store, self.config).exit_code, 0)

    def test_a_session_start_locks_the_gate_again(self):
        skill = {"session_id": "s1", "tool_name": "Skill", "tool_input": {"skill": "engineering-standards"}}
        handle("mark", skill, self.store, self.config)
        handle("reset", {"session_id": "s1", "source": "compact"}, self.store, self.config)
        self.assertEqual(handle("gate", self.edit_payload(), self.store, self.config).exit_code, 2)

    def test_a_payload_without_a_session_id_is_allowed_rather_than_bricking_the_tools(self):
        self.assertEqual(handle("gate", {"tool_name": "Edit", "tool_input": {"file_path": "a.rs"}}, self.store, self.config).exit_code, 0)


if __name__ == "__main__":
    unittest.main()
