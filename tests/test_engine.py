import unittest
import os
import ast
from sciaudit.core.engine import AuditEngine
from sciaudit.core.models import Severity

class TestAuditEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AuditEngine()

    def test_calculate_score_perfect(self):
        score = self.engine._calculate_score([])
        self.assertEqual(score, "A+")

    def test_calculate_score_f_on_critical(self):
        from sciaudit.core.models import Violation
        # 4 errors should drop score to 0 (100 - 4*30 = -20 -> 0)
        violations = [Violation("TEST", "RuleName", "Msg", Severity.ERROR, i, 0) for i in range(4)]
        score = self.engine._calculate_score(violations)
        self.assertEqual(score, "F")

    def test_parse_ipynb(self):
        # Cria um notebook temporário simples
        nb_content = {
            "cells": [
                {"cell_type": "code", "source": ["print('hello')"]}
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 5
        }
        import json
        with open("tmp_test.ipynb", "w") as f:
            json.dump(nb_content, f)
        
        code, mapping = self.engine._parse_ipynb("tmp_test.ipynb")
        self.assertIn("print('hello')", code)
        os.remove("tmp_test.ipynb")

if __name__ == "__main__":
    unittest.main()
