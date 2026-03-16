import unittest
from sciaudit.cli.main import get_engine
from sciaudit.core.models import Severity

class TestRegistry(unittest.TestCase):
    def test_rule_metadata(self):
        engine = get_engine()
        self.assertGreater(len(engine.rules), 0)
        
        for rule in engine.rules:
            rule_id = rule.rule_id
            self.assertTrue(hasattr(rule, "rule_name"), f"Rule {rule_id} missing rule_name")
            self.assertTrue(rule.rule_name, f"Rule {rule_id} has empty rule_name")
            
            self.assertIsInstance(rule.default_severity, Severity, f"Rule {rule_id} has invalid severity")
            
            # Rule must have a hint (even if derived from class, but we use the property)
            self.assertTrue(hasattr(rule, "hint"), f"Rule {rule_id} missing hint")
            
            # Create a dummy violation to see if add_violation works and uses metadata
            rule.reset()
            rule.add_violation("msg", 1, 0, "snippet", hint="specific hint")
            v = rule.collect()[0]
            self.assertEqual(v.rule_id, rule_id)
            self.assertEqual(v.rule_name, rule.rule_name)
            self.assertEqual(v.hint, "specific hint")

if __name__ == "__main__":
    unittest.main()
