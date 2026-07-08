#!/usr/bin/env python3
"""Smallest check that fails if pre_tool's gate logic breaks. Run: python hooks/test_pre_tool.py"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import audit_level, load_config, review_model  # noqa: E402
from pre_tool import duplicate_defs, is_dep_install  # noqa: E402


def test_audit_level():
    import os
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        assert load_config(root) is None  # no marker -> not launched
        (root / ".claude").mkdir()
        (root / ".claude" / "fable.json").write_text('{"level": "strict"}', encoding="utf-8")
        assert audit_level(load_config(root)) == "strict"  # from config
        (root / ".claude" / "fable.json").write_text("{}", encoding="utf-8")
        assert audit_level(load_config(root)) == "standard"  # default
        (root / ".claude" / "fable.json").write_text("not json", encoding="utf-8")
        assert audit_level(load_config(root)) == "standard"  # unparseable -> {} -> default
        os.environ["FABLE_AUDIT_LEVEL"] = "light"
        try:
            assert audit_level({"level": "strict"}) == "light"  # env wins over config
            assert audit_level({}) == "light"
        finally:
            del os.environ["FABLE_AUDIT_LEVEL"]


def test_review_model():
    import os
    assert review_model({}) == "haiku"  # smallest by default
    assert review_model({"review_model": "sonnet"}) == "sonnet"  # config override
    os.environ["FABLE_REVIEW_MODEL"] = "opus"
    try:
        assert review_model({"review_model": "sonnet"}) == "opus"  # env wins
    finally:
        del os.environ["FABLE_REVIEW_MODEL"]


def test_dep_install_detection():
    assert is_dep_install("pip install requests")
    assert is_dep_install("poetry add numpy")
    assert is_dep_install("npm install lodash")
    assert not is_dep_install("pip install -r requirements.txt")
    assert not is_dep_install("pip install -e .")
    assert not is_dep_install("poetry install")
    assert not is_dep_install("npm install")
    assert not is_dep_install("git status")


def test_duplicate_def_detection():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "SYMBOLS.md").write_text(
            "# Symbol Index\n\n"
            "- `parse_config(path)` — app/config.py:10 — Parse it.\n"
            "- `main()` — app/cli.py:5 — Entry.\n",
            encoding="utf-8")
        target = root / "app" / "new.py"
        # duplicate of parse_config in another file -> flagged
        assert duplicate_defs("def parse_config(p):\n    return p\n", target, root)
        # same name in its own file -> exempt (that's an edit, not a duplicate)
        assert not duplicate_defs("def parse_config(p):\n    return p\n", root / "app" / "config.py", root)
        # exempt name and fresh name -> clean
        assert not duplicate_defs("def main():\n    pass\ndef load_config():\n    pass\n", target, root)
        # indented (method) defs are not top-level -> ignored
        assert not duplicate_defs("class C:\n    def parse_config(self):\n        pass\n", target, root)


if __name__ == "__main__":
    test_dep_install_detection()
    test_duplicate_def_detection()
    test_audit_level()
    test_review_model()
    print("test_pre_tool: all checks passed")
