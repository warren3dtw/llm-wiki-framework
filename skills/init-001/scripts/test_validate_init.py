import shutil
import tempfile
import unittest
from pathlib import Path

from validate_init import validate

EXAMPLES = Path(__file__).resolve().parent.parent / "tests" / "examples"


class Examples(unittest.TestCase):
    def test_each_example_passes(self):
        for mode in ["general", "rhino-cadcraft", "rhino-animation"]:
            with self.subTest(mode=mode):
                self.assertEqual(validate(EXAMPLES / mode, mode), [])

    def test_wrong_mode_fails(self):
        problems = validate(EXAMPLES / "general", "rhino-animation")
        self.assertTrue(any("缺少 docs/ANIMATION.md" in p for p in problems))


class Broken(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "general"
        shutil.copytree(EXAMPLES / "general", self.root)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_missing_file_and_cross_mode_link(self):
        (self.root / "docs/FEEDBACK.md").unlink()
        (self.root / "docs/DRAWING.md").write_text("# 出圖\n" + "說明" * 60, encoding="utf-8")
        with (self.root / "CLAUDE.md").open("a", encoding="utf-8") as f:
            f.write("\n另讀 [DRAWING](docs/DRAWING.md)。\n")
        problems = validate(self.root, "general")
        self.assertTrue(any("缺少 docs/FEEDBACK.md" in p for p in problems))
        self.assertTrue(any("不應該有 docs/DRAWING.md" in p for p in problems))
        self.assertTrue(any("連到其他模式的文件" in p for p in problems))

    def test_nonempty_gitkeep_and_bad_settings(self):
        (self.root / "docs/plans/.gitkeep").write_text("x", encoding="utf-8")
        (self.root / ".claude/settings.json").write_text('{"permissions": {"allow": ["a", "a"], "deny": ["a"]}}',
                                                         encoding="utf-8")
        problems = validate(self.root, "general")
        self.assertTrue(any("不是零位元檔" in p for p in problems))
        self.assertTrue(any("有重複項目" in p for p in problems))
        self.assertTrue(any("同時允許又拒絕" in p for p in problems))

    def test_heading_only_file(self):
        (self.root / "docs/FEATURES.md").write_text("# 功能與成果清單\n\n## 清單\n", encoding="utf-8")
        self.assertTrue(any("FEATURES.md 只有標題" in p for p in validate(self.root, "general")))

    def test_codex_requires_agents_md(self):
        self.assertTrue(any("缺少 AGENTS.md" in p for p in validate(self.root, "general", codex=True)))


if __name__ == "__main__":
    unittest.main()
