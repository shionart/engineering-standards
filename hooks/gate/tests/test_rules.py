"""Tests for the wider write paths: MCP tools, PowerShell, cp/mv/patch/download, more extensions and basenames."""

import json
import re
import unittest
from pathlib import Path

from gate_rules import CODE_EXTENSIONS, command_writes_code, is_code_path, needs_gate

EXT = CODE_EXTENSIONS
MCP_VERBS = [
    "write_file", "edit_file", "create_file", "move_file", "copy_file", "append_file", "apply_patch",
    "update_file", "save_file", "put_object", "upload_file", "insert_text", "replace_text", "rename_file",
    "writeFile", "WriteFile", "Create_File",
]


class ExtensionTests(unittest.TestCase):
    def test_the_added_extensions_are_code(self):
        for name in ["a.ipynb", "a.pl", "a.pm", "a.groovy", "a.gradle", "a.tf", "a.lua", "a.dart", "a.scala",
                     "a.ex", "a.exs", "a.r", "a.R", "a.zig", "a.nim"]:
            self.assertTrue(is_code_path(name, EXT), name)

    def test_data_and_document_extensions_stay_ungated_on_purpose(self):
        for name in ["a.yaml", "a.yml", "a.json", "a.md", "a.txt", "a.py.bak", "a.pyc", "a.python", "a.py~"]:
            self.assertFalse(is_code_path(name, EXT), name)

    def test_extensionless_build_files_are_code(self):
        for name in ["Dockerfile", "src/Dockerfile", "Dockerfile.dev", "C:\\p\\Dockerfile.prod", "api.Dockerfile",
                     "Makefile", "build/Makefile", "Jenkinsfile", "Containerfile", "dockerfile"]:
            self.assertTrue(is_code_path(name, EXT), name)

    def test_names_that_only_contain_a_build_file_name_are_not_code(self):
        for name in ["MyDockerfile", "Makefile.md.txt", "notmakefile", "Dockerfiles/readme.md", "Makefile.bak"]:
            self.assertFalse(is_code_path(name, EXT), name)

    def test_extra_extensions_passed_in_are_honoured(self):
        self.assertFalse(is_code_path("a.yaml", EXT))
        self.assertTrue(is_code_path("a.yaml", EXT + ("yaml",)))


class BuildFileNameTests(unittest.TestCase):
    def test_backup_copies_of_a_build_file_are_not_code(self):
        for name in ["Dockerfile.bak", "Dockerfile.orig", "Dockerfile.old", "Dockerfile.tmp", "Dockerfile.swp",
                     "Dockerfile.save", "Dockerfile.dev.bak", "Dockerfile~", "Dockerfile.dev~", "Makefile.bak",
                     "Jenkinsfile.old"]:
            self.assertFalse(is_code_path(name, EXT), name)

    def test_build_files_with_a_real_suffix_are_code(self):
        for name in ["Dockerfile.dev", "Dockerfile.prod", "api.Dockerfile", "Containerfile", "Makefile", "Jenkinsfile"]:
            self.assertTrue(is_code_path(name, EXT), name)


class McpToolTests(unittest.TestCase):
    def test_a_writing_mcp_tool_with_a_code_path_is_gated(self):
        for tool, tool_input in [
            ("mcp__filesystem__write_file", {"path": "x.py", "content": "1"}),
            ("mcp__filesystem__edit_file", {"path": "src/a.ts", "edits": []}),
            ("mcp__filesystem__move_file", {"source": "a.txt", "destination": "b.rs"}),
            ("mcp__filesystem__copy_file", {"source": "a.txt", "destination": "b.go"}),
            ("mcp__filesystem__append_file", {"file_path": "run.sh", "content": "x"}),
            ("mcp__fs__Create_File", {"filePath": "a.java"}),
            ("mcp__git__apply_patch", {"filename": "a.c"}),
            ("mcp__x__create_thing", {"target": "a.tf"}),
            ("mcp__x__write_notebook", {"notebook_path": "n.ipynb"}),
            ("mcp__fs__write_many", {"paths": ["a.md", "b.py"]}),
            ("mcp__fs__edit_many", {"edits": [{"path": "a.md"}, {"path": "b.lua"}]}),
            ("mcp__fs__write_files", {"files": [{"path": "Dockerfile", "content": "x"}]}),
        ]:
            self.assertTrue(needs_gate(tool, tool_input, EXT), tool)

    def test_unrelated_or_non_code_mcp_calls_are_not_gated(self):
        for tool, tool_input in [
            ("mcp__filesystem__read_file", {"path": "x.py"}),
            ("mcp__filesystem__list_directory", {"path": "src.py"}),
            ("mcp__zoho__create_a_task", {"name": "fix x.py", "description": "x.py"}),
            ("mcp__filesystem__write_file", {"path": "notes.md", "content": "x.py"}),
            ("mcp__filesystem__write_file", {"path": "config.yaml"}),
            ("mcp__filesystem__write_file", {}),
            ("mcp__filesystem__write_file", {"path": 5, "paths": "x.py", "edits": ["x.py", 3]}),
            ("filesystem_write_file", {"path": "x.py"}),
        ]:
            self.assertFalse(needs_gate(tool, tool_input, EXT), tool)

    def test_every_write_like_verb_is_recognised_in_the_tool_part(self):
        for tool in MCP_VERBS + ["Update-File", "UPLOAD_FILE"]:
            name = f"mcp__server__{tool}"
            self.assertTrue(needs_gate(name, {"path": "a.py"}, EXT), name)

    def test_a_verb_hidden_inside_a_longer_word_is_not_a_verb(self):
        for tool in ["get_output", "send_input", "compute_stats", "getOutput", "list-outputs", "reputation_score",
                     "rewrite_check_status", "updated_at", "saved_searches"]:
            name = f"mcp__server__{tool}"
            self.assertFalse(needs_gate(name, {"path": "a.py"}, EXT), name)

    def test_verbs_are_found_as_whole_words_in_snake_kebab_and_camel_case(self):
        for tool in ["writeFile", "update_file", "put_object", "file-write", "fileWriteAll", "HTTPPut", "bulkUpload"]:
            name = f"mcp__server__{tool}"
            self.assertTrue(needs_gate(name, {"path": "a.py"}, EXT), name)

    def test_drive_style_tools_with_a_path_are_gated(self):
        self.assertTrue(needs_gate("mcp__claude_ai_Google_Drive__update_file", {"path": "a.py"}, EXT))

    def test_the_server_name_alone_never_makes_a_read_tool_a_write_tool(self):
        for name in ["mcp__editor__read_file", "mcp__create_things__list_files", "mcp__copy-tool__get_file",
                     "mcp__plugin_update_x__search_files", "mcp__claude_ai_Google_Drive__read_file_content"]:
            self.assertFalse(needs_gate(name, {"path": "a.py"}, EXT), name)


class MatcherTests(unittest.TestCase):
    """The hooks.json matcher must let through every call the rules can gate, and no MCP read."""

    @classmethod
    def setUpClass(cls):
        hooks = json.loads((Path(__file__).resolve().parents[2] / "hooks.json").read_text(encoding="utf-8"))
        cls.matcher = hooks["hooks"]["PreToolUse"][0]["matcher"]

    def matches(self, name):
        return re.search(self.matcher, name) is not None

    def test_file_and_shell_tools_reach_the_hook(self):
        for name in ["Edit", "Write", "NotebookEdit", "MultiEdit", "Bash", "PowerShell"]:
            self.assertTrue(self.matches(name), name)

    def test_other_built_in_tools_do_not(self):
        for name in ["Read", "Grep", "Glob", "TodoWrite", "Skill", "WebFetch", "Task"]:
            self.assertFalse(self.matches(name), name)

    def test_mcp_reads_never_start_the_hook(self):
        for name in ["mcp__filesystem__read_file", "mcp__editor__read_file", "mcp__filesystem__list_directory",
                     "mcp__zoho-sandbox__ZohoProjects_get_projects_list",
                     "mcp__plugin_context-mode_context-mode__ctx_search"]:
            self.assertFalse(self.matches(name), name)

    def test_every_mcp_call_the_rules_can_gate_reaches_the_hook(self):
        for tool in MCP_VERBS:
            name = f"mcp__some_server__{tool}"
            self.assertTrue(needs_gate(name, {"path": "a.py"}, EXT), name)
            self.assertTrue(self.matches(name), name)
        self.assertTrue(self.matches("mcp__claude_ai_Google_Drive__update_file"))


class ShellWriteTests(unittest.TestCase):
    def test_copy_move_install_to_a_code_file_are_caught(self):
        for command in [
            "cp template.txt app.py",
            "cp -r a b/main.go",
            "mv draft.txt src/lib.rs",
            "git mv old.txt new.ts",
            "install -m 755 tool run.sh",
            "sudo cp a.txt /usr/local/bin/x.sh",
            "cd x && cp a.txt b.py",
            'cp a.txt "dir/b.py"',
            "cp a.txt Dockerfile",
            "cp a.txt Containerfile",
        ]:
            self.assertTrue(command_writes_code(command, EXT), command)

    def test_copying_a_code_file_to_a_non_code_name_is_not_caught(self):
        for command in [
            "cp app.py app.py.bak",
            "cp app.py notes.txt",
            "cp Dockerfile Dockerfile.bak",
            "cp a.txt b.txt",
            "npm install left-pad.py",
            "pip install x.py",
            "ls cp.py",
            "cp a.txt b.py.bak",
        ]:
            self.assertFalse(command_writes_code(command, EXT), command)

    def test_patch_and_git_apply_are_caught_unless_dry_run(self):
        for command in [
            "git apply fix.diff",
            "git -C repo apply fix.diff",
            "patch -p1 < fix.diff",
            "patch app.py fix.diff",
            "cat fix.diff | git apply -",
        ]:
            self.assertTrue(command_writes_code(command, EXT), command)
        for command in [
            "git apply --check fix.diff",
            "git apply --stat fix.diff",
            "patch --dry-run -p1 < fix.diff",
            "npm version patch",
            "curl -X PATCH https://x/y",
            "git format-patch -1",
        ]:
            self.assertFalse(command_writes_code(command, EXT), command)

    def test_downloads_into_a_code_file_are_caught(self):
        for command in [
            "curl -o setup.py https://x/y",
            "curl -sSL --output tools/run.sh https://x/y",
            "curl https://x/y -o a.ts",
            "wget -O install.sh https://x/y",
            "wget --output-document=x.py https://x/y",
            "wget -q -O - https://x/y > run.sh",
            "curl -O https://x/y/setup.py",
            "curl -sSLO https://x/y/setup.py?raw=1",
            "curl -sSLo a.py https://x/y",
            "curl --output a.py https://x/y",
            "curl --output=a.py https://x/y",
            "curl --remote-name https://x/y/a.py",
            "wget https://x/y/setup.py",
            "wget -q https://x/y/setup.py#frag",
            "wget -qO a.py https://x/y",
            "wget -Oa.py https://x/y",
            "wget --output-document a.py https://x/y",
        ]:
            self.assertTrue(command_writes_code(command, EXT), command)
        for command in [
            "curl -o data.json https://x/a.py",
            "curl -O https://x/y/archive.tar.gz",
            "wget https://x/y/archive.tar.gz",
            "wget -qO- https://x/a.py",
            "wget -O out.tar.gz https://x/a.py",
            "curl https://x/y | sh",
        ]:
            self.assertFalse(command_writes_code(command, EXT), command)

    def test_a_redirect_to_a_backup_name_is_not_caught(self):
        self.assertFalse(command_writes_code("echo x > a.py.bak", EXT))
        self.assertTrue(command_writes_code("echo x > Dockerfile", EXT))
        self.assertTrue(command_writes_code("echo x >> Makefile", EXT))
        self.assertFalse(command_writes_code("echo x > Dockerfile.bak", EXT))

    def test_extra_extensions_apply_to_commands(self):
        self.assertFalse(command_writes_code("cp a.txt b.yaml", EXT))
        self.assertTrue(command_writes_code("cp a.txt b.yaml", EXT + ("yaml",)))


class SegmentTests(unittest.TestCase):
    def test_each_command_of_a_compound_line_is_judged_on_its_own(self):
        for command in [
            "git apply fix.patch && ruff format --check .",
            "git diff --stat; git apply x.patch",
            "git diff --stat\ngit apply x.patch",
            "ruff check . || cp a.txt b.py",
            "ls | xargs cp x.txt a.py",
            "(cd src && cp a.txt b.py)",
            "if true; then cp a.txt b.py; fi",
        ]:
            self.assertTrue(command_writes_code(command, EXT), command)

    def test_a_dry_run_flag_only_counts_inside_the_patch_command_itself(self):
        self.assertFalse(command_writes_code("git apply --check fix.patch && git status --short", EXT))
        self.assertTrue(command_writes_code("git apply --check fix.patch && git apply fix.patch", EXT))
        self.assertTrue(command_writes_code("git diff --summary; patch -p1 < fix.diff", EXT))

    def test_leading_space_and_wrappers_do_not_hide_a_command(self):
        for command in [
            " cp a.py b.py",
            "\tcp a.py b.py",
            " git apply p.patch",
            "env X=1 cp a.py b.py",
            "env -i X=1 Y=2 cp a.py b.py",
            "X=1 cp a.py b.py",
            "time cp a.py b.py",
            "nohup cp a.py b.py",
            "command cp a.py b.py",
            "builtin cp a.py b.py",
            "sudo -u root cp a.txt b.py",
            "sudo env X=1 git apply p.patch",
            "xargs -I {} cp {} a.py",
            'bash -c "cp a.txt b.py"',
            "powershell -Command \"Set-Content x.ps1 'a'\"",
        ]:
            self.assertTrue(command_writes_code(command, EXT), command)

    def test_trailing_redirections_do_not_hide_the_destination(self):
        for command in [
            "cp a.py b.py 2>/dev/null",
            "cp a.py src/",
            "cp a.py src/ 2>&1",
            "mv x.py y.py >log",
            "cp a.py b.py 2> err.txt",
            "cp a.py .",
        ]:
            self.assertTrue(command_writes_code(command, EXT), command)

    def test_a_directory_destination_counts_only_when_a_source_is_code(self):
        self.assertTrue(command_writes_code("cp a.py backup", EXT))
        self.assertTrue(command_writes_code("mv a.py b.txt c.rs dir/", EXT))
        self.assertTrue(command_writes_code("cp -t out a.py", EXT))
        self.assertFalse(command_writes_code("cp a.txt backup", EXT))
        self.assertFalse(command_writes_code("cp notes.md dir/", EXT))
        self.assertFalse(command_writes_code("cp a.py a.py.bak 2>/dev/null", EXT))
        self.assertFalse(command_writes_code("cp -r src", EXT))

    def test_text_that_only_mentions_a_command_is_not_a_command(self):
        for command in [
            'echo "cp a.py src/"',
            'echo "a; cp a.py b.py"',
            "grep -n 'git apply' README.md",
            "git commit -m 'run cp a.py b.py'",
            "git log --stat",
        ]:
            self.assertFalse(command_writes_code(command, EXT), command)

    def test_an_unbalanced_quote_does_not_hide_the_next_line(self):
        self.assertTrue(command_writes_code("echo don't\ncp a.txt b.py", EXT))


class PowerShellWriteTests(unittest.TestCase):
    def test_powershell_writes_to_code_files_are_caught(self):
        for command in [
            "Set-Content x.ps1 -Value 'Write-Host hi'",
            "Set-Content -Path src\\app.py -Value 'x'",
            "'x' | Add-Content run.sh",
            "'x' | Out-File -FilePath a.ts -Encoding utf8",
            "New-Item -ItemType File -Path build.gradle",
            "New-Item x.rb -ItemType File",
            "Copy-Item a.txt b.cs",
            "Copy-Item -Path a.txt -Destination src\\b.cs -Force",
            "Move-Item a.txt b.go",
            "move-item a.txt b.go -Force",
            "Copy-Item a.ps1 backup\\",
            "Copy-Item -Path a.ps1 -Destination out",
            "'x' > a.py",
            "'x' >> a.py",
            "set-content a.ps1 'x'",
        ]:
            self.assertTrue(command_writes_code(command, EXT), command)

    def test_powershell_reads_and_non_code_writes_are_not_caught(self):
        for command in [
            "Get-Content x.ps1",
            "Set-Content notes.txt -Value hi",
            "Copy-Item a.ps1 a.ps1.bak",
            "New-Item -ItemType Directory -Path out",
            "Out-File log.txt",
            "Get-ChildItem *.py | Measure-Object",
        ]:
            self.assertFalse(command_writes_code(command, EXT), command)

    def test_the_powershell_tool_is_gated_like_bash(self):
        self.assertTrue(needs_gate("PowerShell", {"command": "Set-Content x.ps1 'a'"}, EXT))
        self.assertTrue(needs_gate("PowerShell", {"command": "cp a.txt b.py"}, EXT))
        self.assertFalse(needs_gate("PowerShell", {"command": "Get-Content x.ps1"}, EXT))
        self.assertFalse(needs_gate("PowerShell", {}, EXT))


if __name__ == "__main__":
    unittest.main()
