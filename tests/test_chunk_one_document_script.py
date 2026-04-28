import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts.chunk_one_document import main


class ChunkOneDocumentScriptTest(unittest.TestCase):
    def test_prints_raw_normalized_and_chunks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "note.md").write_text("# 标题\n\nabcdefghi", encoding="utf-8")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "note.md", "--chunk-size", "4", "--overlap", "1"])

        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("--- RAW MARKDOWN ---", output)
        self.assertIn("--- NORMALIZED TEXT", output)
        self.assertIn("--- CHUNKS (n=", output)
        self.assertIn("--- CHUNK #0 note.md#0", output)
        self.assertIn("abcdef", output)


if __name__ == "__main__":
    unittest.main()
