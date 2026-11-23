"""Tests for the engineering-standards gate. Run: python -m unittest discover -s tests -t . (from hooks/gate/)."""

import os
import tempfile
import unittest
from pathlib import Path

from gate_rules import CODE_EXTENSIONS, command_writes_code, is_code_path, is_standards_skill, needs_gate
from flagstore import FlagStore
from hook import handle
from config import Config


DAY = 86400.0


def age_session(folder, session, when):
    """Make a session folder and every flag file in it look last used at `when`."""
    path = Path(folder) / session
    for item in [*path.iterdir(), path]:
        os.utime(item, (when, when))


class CodePathTests(unittest.TestCase):
    def test_code_and_script_files_are_code(self):
        for path in ["a/b.rs", "x.PY", "C:\\p\\main.ts", "run.sh", "t.ps1", "m.sql", "s.css", "p.html", "b.mjs"]:
            self.assertTrue(is_code_path(path, CODE_EXTENSIONS), path)

    def test_documents_and_data_are_not_code(self):
        for path in ["README.md", "notes.txt", "settings.json", "plan.yaml", "memory/x.md", "image.png", ""]:
            self.assertFalse(is_code_path(path, CODE_EXTENSIONS), path)


class ToolGateTests(unittest.TestCase):
    def test_edit_write_and_notebook_of_code_are_gated(self):
        for tool in ["Edit", "Write", "NotebookEdit"]:
            self.assertTrue(needs_gate(tool, {"file_path": "src/lib.rs"}, CODE_EXTENSIONS), tool)

    def test_edit_of_a_document_and_read_tools_are_not_gated(self):
        self.assertFalse(needs_gate("Write", {"file_path": "docs/plan.md"}, CODE_EXTENSIONS))
        self.assertFalse(needs_gate("Read", {"file_path": "src/lib.rs"}, CODE_EXTENSIONS))
        self.assertFalse(needs_gate("Grep", {"pattern": "x"}, CODE_EXTENSIONS))

    def test_bash_is_gated_only_when_it_writes_a_code_file(self):
        self.assertTrue(needs_gate("Bash", {"command": "cat > a.py <<EOF\nprint(1)\nEOF"}, CODE_EXTENSIONS))
        self.assertFalse(needs_gate("Bash", {"command": "cargo test -p x 2>&1 | tail -5"}, CODE_EXTENSIONS))


class CommandWriteTests(unittest.TestCase):
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
            self.assertTrue(command_writes_code(command, CODE_EXTENSIONS), command)

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
            self.assertFalse(command_writes_code(command, CODE_EXTENSIONS), command)


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
            store.mark("../evil", "../../agent")
            files = [p for p in Path(folder).rglob("*") if p.is_file()]
            self.assertEqual(len(files), 2)
            for path in files:
                self.assertTrue(path.resolve().is_relative_to(Path(folder).resolve()), path)

    def test_each_agent_has_its_own_flag_inside_a_session(self):
        with tempfile.TemporaryDirectory() as folder:
            store = FlagStore(Path(folder))
            store.mark("s1", "a1")
            self.assertTrue(store.has("s1", "a1"))
            self.assertFalse(store.has("s1"))  # the main agent is not unlocked
            self.assertFalse(store.has("s1", "a2"))
            self.assertFalse(store.has("s2", "a1"))
            store.mark("s1")
            self.assertTrue(store.has("s1"))
            store.clear("s1", "a1")
            self.assertFalse(store.has("s1", "a1"))
            self.assertTrue(store.has("s1"))  # clearing one agent leaves the others

    def test_an_agent_called_main_is_not_the_main_agent(self):
        with tempfile.TemporaryDirectory() as folder:
            store = FlagStore(Path(folder))
            store.mark("s1", "main")
            self.assertFalse(store.has("s1"))

    def test_clear_session_removes_main_and_every_agent_of_that_session_only(self):
        with tempfile.TemporaryDirectory() as folder:
            store = FlagStore(Path(folder))
            store.mark("s1")
            store.mark("s1", "a1")
            store.mark("s1", "a2")
            store.mark("s2")
            store.mark("s2", "a1")
            store.clear_session("s1")
            self.assertFalse(any([store.has("s1"), store.has("s1", "a1"), store.has("s1", "a2")]))
            self.assertTrue(store.has("s2") and store.has("s2", "a1"))
            store.clear_session("s1")  # clearing twice is harmless

    def test_prune_removes_session_folders_older_than_the_limit_only(self):
        with tempfile.TemporaryDirectory() as folder:
            store = FlagStore(Path(folder))
            store.mark("old")
            store.mark("old", "a1")
            store.mark("fresh")
            now = 1_000_000_000.0
            age_session(folder, "old", now - 8 * DAY)
            age_session(folder, "fresh", now - 6 * DAY)
            store.prune(now)
            self.assertFalse(store.has("old") or store.has("old", "a1"))
            self.assertTrue(store.has("fresh"))
            store.prune(now)  # pruning twice is harmless

    def test_prune_keeps_a_session_whose_newest_file_is_recent(self):
        with tempfile.TemporaryDirectory() as folder:
            store = FlagStore(Path(folder))
            store.mark("busy")
            store.mark("busy", "a1")
            now = 1_000_000_000.0
            old = now - 8 * DAY
            os.utime(Path(folder) / "busy", (old, old))
            os.utime(Path(folder) / "busy" / "main.flag", (old, old))
            os.utime(Path(folder) / "busy" / "agent-a1.flag", (now - DAY, now - DAY))
            store.prune(now)
            self.assertTrue(store.has("busy"))

    def test_refresh_keeps_an_active_session_from_being_pruned(self):
        with tempfile.TemporaryDirectory() as folder:
            store = FlagStore(Path(folder))
            store.mark("s1")
            age_session(folder, "s1", 0)
            now = 1_000_000_000.0
            store.refresh("s1", None, now - 2 * DAY)
            store.prune(now)
            self.assertTrue(store.has("s1"))
            store.prune(now + 6 * DAY)
            self.assertFalse(store.has("s1"))

    def test_refresh_of_a_missing_flag_is_harmless(self):
        with tempfile.TemporaryDirectory() as folder:
            FlagStore(Path(folder)).refresh("nobody", "a1", 1_000_000_000.0)

    def test_prune_of_a_missing_folder_is_harmless(self):
        with tempfile.TemporaryDirectory() as folder:
            FlagStore(Path(folder) / "never-created").prune(1_000_000_000.0)

    def test_prune_leaves_plain_files_in_the_folder_alone(self):
        with tempfile.TemporaryDirectory() as folder:
            note = Path(folder) / "note.txt"
            note.write_text("x", encoding="utf-8")
            os.utime(note, (0, 0))
            FlagStore(Path(folder)).prune(1_000_000_000.0)
            self.assertTrue(note.exists())


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

    def skill_payload(self, session="s1", agent_id=None, skill="engineering-standards"):
        payload = {"session_id": session, "tool_name": "Skill", "tool_input": {"skill": skill}}
        if agent_id:
            payload["agent_id"] = agent_id
            payload["agent_type"] = "general-purpose"
        return payload

    def agent_edit(self, agent_id, session="s1"):
        return {**self.edit_payload(session=session), "agent_id": agent_id, "agent_type": "general-purpose"}

    def gate_code(self, payload):
        return handle("gate", payload, self.store, self.config).exit_code

    def test_a_subagent_is_blocked_even_when_the_main_agent_loaded_the_skill(self):
        handle("mark", self.skill_payload(), self.store, self.config)
        self.assertEqual(self.gate_code(self.edit_payload()), 0)
        self.assertEqual(self.gate_code(self.agent_edit("a1")), 2)

    def test_a_subagent_that_loaded_the_skill_itself_passes(self):
        handle("mark", self.skill_payload(agent_id="a1"), self.store, self.config)
        self.assertEqual(self.gate_code(self.agent_edit("a1")), 0)

    def test_a_subagent_mark_does_not_unlock_the_main_agent_or_another_subagent(self):
        handle("mark", self.skill_payload(agent_id="a1"), self.store, self.config)
        self.assertEqual(self.gate_code(self.edit_payload()), 2)
        self.assertEqual(self.gate_code(self.agent_edit("a2")), 2)
        self.assertEqual(self.gate_code(self.agent_edit("a1", session="s2")), 2)

    def test_the_block_message_tells_subagents_to_load_the_skill_themselves(self):
        message = handle("gate", self.agent_edit("a1"), self.store, self.config).message
        self.assertIn("subagent", message.lower())

    def test_a_missing_or_empty_agent_id_is_the_main_agent(self):
        handle("mark", {**self.skill_payload(), "agent_id": ""}, self.store, self.config)
        self.assertEqual(self.gate_code(self.edit_payload()), 0)
        self.assertEqual(self.gate_code({**self.edit_payload(), "agent_id": ""}), 0)

    def test_a_session_start_clears_the_main_agent_and_every_subagent_of_that_session_only(self):
        for session in ("s1", "s2"):
            handle("mark", self.skill_payload(session=session), self.store, self.config)
            handle("mark", self.skill_payload(session=session, agent_id="a1"), self.store, self.config)
        handle("reset", {"session_id": "s1", "source": "compact"}, self.store, self.config)
        self.assertEqual(self.gate_code(self.edit_payload()), 2)
        self.assertEqual(self.gate_code(self.agent_edit("a1")), 2)
        self.assertEqual(self.gate_code(self.edit_payload(session="s2")), 0)
        self.assertEqual(self.gate_code(self.agent_edit("a1", session="s2")), 0)

    def test_a_finished_subagent_forgets_its_flag_and_leaves_the_others(self):
        handle("mark", self.skill_payload(), self.store, self.config)
        handle("mark", self.skill_payload(agent_id="a1"), self.store, self.config)
        handle("mark", self.skill_payload(agent_id="a2"), self.store, self.config)
        stop = {"session_id": "s1", "hook_event_name": "SubagentStop", "agent_id": "a1", "agent_type": "general-purpose"}
        self.assertEqual(handle("agent_stop", stop, self.store, self.config).exit_code, 0)
        self.assertEqual(self.gate_code(self.agent_edit("a1")), 2)
        self.assertEqual(self.gate_code(self.agent_edit("a2")), 0)
        self.assertEqual(self.gate_code(self.edit_payload()), 0)

    def test_agent_stop_without_an_agent_id_changes_nothing(self):
        handle("mark", self.skill_payload(), self.store, self.config)
        handle("agent_stop", {"session_id": "s1"}, self.store, self.config)
        self.assertEqual(self.gate_code(self.edit_payload()), 0)

    def test_another_skill_does_not_unlock_the_gate(self):
        other = {"session_id": "s1", "tool_name": "Skill", "tool_input": {"skill": "impeccable"}}
        handle("mark", other, self.store, self.config)
        self.assertEqual(handle("gate", self.edit_payload(), self.store, self.config).exit_code, 2)

    def test_the_block_message_says_how_to_turn_the_gate_off(self):
        message = handle("gate", self.edit_payload(), self.store, self.config).message
        self.assertTrue(message.endswith("To turn the gate off, set ENG_STANDARDS_GATE=0 (see the plugin README)."))

    def test_with_the_gate_off_nothing_is_blocked(self):
        off = Config(state_dir=self.config.state_dir, reply_check=False, gate=False)
        self.assertEqual(handle("gate", self.edit_payload(), self.store, off).exit_code, 0)

    def test_with_the_gate_off_marking_and_resetting_still_work(self):
        off = Config(state_dir=self.config.state_dir, reply_check=False, gate=False)
        handle("mark", self.skill_payload(), self.store, off)
        self.assertTrue(self.store.has("s1"))
        handle("reset", {"session_id": "s1"}, self.store, off)
        self.assertFalse(self.store.has("s1"))

    def test_an_extra_extension_from_the_config_is_gated(self):
        yaml_edit = self.edit_payload(path="deploy.yaml")
        self.assertEqual(self.gate_code(yaml_edit), 0)
        extra = Config(state_dir=self.config.state_dir, reply_check=False, code_extensions=CODE_EXTENSIONS + ("yaml",))
        self.assertEqual(handle("gate", yaml_edit, self.store, extra).exit_code, 2)

    def test_every_allowed_gate_check_refreshes_the_flag_so_an_active_session_is_not_pruned(self):
        handle("mark", self.skill_payload(), self.store, self.config)
        handle("mark", self.skill_payload(agent_id="a1"), self.store, self.config)
        old = 1_000_000_000.0
        for name in ("main.flag", "agent-a1.flag"):
            os.utime(Path(self.folder.name) / "s1" / name, (old, old))
        later = old + 3 * DAY
        handle("gate", self.agent_edit("a1"), self.store, self.config, now=lambda: later)
        self.assertEqual((Path(self.folder.name) / "s1" / "agent-a1.flag").stat().st_mtime, later)
        self.assertEqual((Path(self.folder.name) / "s1" / "main.flag").stat().st_mtime, old)  # only the caller's flag

    def test_a_blocked_gate_check_creates_nothing(self):
        handle("gate", self.edit_payload(), self.store, self.config, now=lambda: 5.0)
        self.assertFalse((Path(self.folder.name) / "s1").exists())

    def test_mcp_and_powershell_calls_are_blocked_without_the_skill(self):
        mcp = {"session_id": "s1", "tool_name": "mcp__filesystem__write_file", "tool_input": {"path": "x.py"}}
        ps = {"session_id": "s1", "tool_name": "PowerShell", "tool_input": {"command": "Set-Content x.ps1 'a'"}}
        dockerfile = self.edit_payload(path="Dockerfile")
        for payload in (mcp, ps, dockerfile):
            self.assertEqual(self.gate_code(payload), 2, payload["tool_name"])
        handle("mark", self.skill_payload(), self.store, self.config)
        for payload in (mcp, ps, dockerfile):
            self.assertEqual(self.gate_code(payload), 0, payload["tool_name"])

    def test_a_session_start_prunes_old_session_folders(self):
        handle("mark", self.skill_payload(session="old"), self.store, self.config)
        age_session(self.folder.name, "old", 0)
        handle("reset", {"session_id": "s1"}, self.store, self.config, now=lambda: 8 * DAY)
        self.assertFalse(self.store.has("old"))

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
