import unittest
import ast
from sciaudit.rules.data_leakage import TargetLeakageRule
from sciaudit.rules.reproducibility import ReproducibilityRule
from sciaudit.rules.methodology import FeatureImportanceRule

class TestRules(unittest.TestCase):
    def test_leakage_rule(self):
        code = """
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
from sklearn.model_selection import train_test_split
X_train, X_test = train_test_split(X_scaled)
        """
        tree = ast.parse(code)
        rule = TargetLeakageRule()
        rule.visit(tree)
        violations = rule.collect()
        self.assertTrue(any(v.rule_id == "SCI-001" for v in violations))

    def test_reproducibility_rule(self):
        code = "from sklearn.model_selection import train_test_split; train_test_split(X, y)"
        tree = ast.parse(code)
        rule = ReproducibilityRule()
        rule.visit(tree)
        violations = rule.collect()
        self.assertTrue(any(v.rule_id == "SCI-002" for v in violations))

    def test_feature_importance_no_corr(self):
        code = "model.fit(X, y); print(model.feature_importances_)"
        tree = ast.parse(code)
        rule = FeatureImportanceRule()
        rule.visit(tree)
        violations = rule.collect()
        self.assertTrue(any(v.rule_id == "SCI-003" for v in violations))

if __name__ == "__main__":
    unittest.main()
