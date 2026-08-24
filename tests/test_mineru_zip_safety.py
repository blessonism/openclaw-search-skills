"""Regression tests for safe MinerU archive extraction."""

import importlib.util
import io
import pathlib
import stat
import sys
import tempfile
import unittest
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "mineru-extract" / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load_module(name: str, relative_path: str):
    """Load a repository script as a module for focused testing."""
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MINERU_EXTRACT = load_module(
    "mineru_extract", "mineru-extract/scripts/mineru_extract.py"
)
MINERU_PARSE = load_module(
    "mineru_parse_documents", "mineru-extract/scripts/mineru_parse_documents.py"
)


def build_zip(name: str, content: str = "content") -> bytes:
    """Build an in-memory ZIP containing one regular file."""
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr(name, content)
    return payload.getvalue()


def build_symlink_zip(name: str, target: str) -> bytes:
    """Build an in-memory ZIP containing one symbolic-link entry."""
    payload = io.BytesIO()
    member = zipfile.ZipInfo(name)
    member.create_system = 3
    member.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr(member, target)
    return payload.getvalue()


class MinerUZipSafetyTests(unittest.TestCase):
    """Protect both MinerU archive extraction paths."""

    def test_low_level_extractor_rejects_parent_traversal(self):
        """Reject parent traversal through the low-level extractor."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, "Unsafe archive path"):
                MINERU_EXTRACT.extract_markdown_from_zip(
                    build_zip("../outside.md"), pathlib.Path(temp_dir)
                )

    def test_wrapper_rejects_parent_traversal(self):
        """Reject parent traversal through the multi-document wrapper."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, "Unsafe archive path"):
                MINERU_PARSE.extract_main_markdown(
                    build_zip("../outside.md"), pathlib.Path(temp_dir)
                )

    def test_valid_markdown_archives_still_extract(self):
        """Preserve extraction of valid nested Markdown files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            markdown_path, extracted = MINERU_EXTRACT.extract_markdown_from_zip(
                build_zip("document/main.md", "# Safe"), pathlib.Path(temp_dir)
            )

            self.assertEqual(markdown_path.name, "main.md")
            self.assertEqual(len(extracted), 1)

    def test_rejects_symbolic_links(self):
        """Reject symbolic-link members before extraction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, "Archive links are not supported"):
                MINERU_EXTRACT.extract_markdown_from_zip(
                    build_symlink_zip("document/link.md", "../outside.md"),
                    pathlib.Path(temp_dir),
                )


if __name__ == "__main__":
    unittest.main()
