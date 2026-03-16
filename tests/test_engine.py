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
        v = Violation("TEST", "Msg", Severity.CRITICAL, 1, 0)
        score = self.engine._calculate_score([v])
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
        
        code = self.engine._parse_ipynb("tmp_test.ipynb")
        self.assertIn("print('hello')", code)
        os.remove("tmp_test.ipynb")

if __name__ == "__main__":
    unittest.main()
