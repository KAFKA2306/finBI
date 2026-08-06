from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]


class StaticBoundaryTests(unittest.TestCase):
    def test_one_canonical_entry_point_and_no_duplicate_functions(self) -> None:
        tree = ast.parse((CODE_DIR / "your_streamlit_app.py").read_text(encoding="utf-8"))
        names = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
        self.assertEqual(len(names), len(set(names)))
        main_guards = [
            node
            for node in tree.body
            if isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and ast.unparse(node.test) == "__name__ == '__main__'"
        ]
        self.assertEqual(len(main_guards), 1)

    def test_no_personal_windows_path_or_pickle_load(self) -> None:
        python_text = "\n".join(
            path.read_text(encoding="utf-8") for path in CODE_DIR.glob("*.py")
        )
        self.assertIsNone(
            re.search(r"[A-Za-z]:\\\\(?:Users|ML|Documents)\\\\", python_text)
        )
        self.assertNotIn("pickle.load", python_text)
        self.assertNotIn("pd.read_pickle", python_text)


if __name__ == "__main__":
    unittest.main()
