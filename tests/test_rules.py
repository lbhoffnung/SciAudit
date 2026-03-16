import unittest
import ast
from sciaudit.rules.leakage.target_leakage import TargetLeakageRule
from sciaudit.rules.leakage.contamination import TestSetContaminationRule
from sciaudit.rules.leakage.temporal_label import TimeLeakageRule, LabelLeakageRule
from sciaudit.rules.reproducibility.random_seed import ReproducibilityRule
from sciaudit.rules.reproducibility.shuffle_logic import ShuffleBeforeTimeSplitRule
from sciaudit.rules.statistics.rigor import OverfittingCegoRule, PHackingRule
from sciaudit.rules.statistics.data_hygiene import ClassImbalanceRule, SilentNaNDropRule
from sciaudit.rules.causal.feature_importance import FeatureImportanceRule
from sciaudit.rules.causal.claims import CausalClaimsRule

class TestRules(unittest.TestCase):
    def test_SCI_001_target_leakage(self):
        code = "scaler.fit_transform(X); train_test_split(X, y)"
        tree = ast.parse(code)
        rule = TargetLeakageRule()
        rule.visit(tree)
        self.assertTrue(any(v.rule_id == "SCI-001" for v in rule.collect()))

    def test_SCI_006_contamination(self):
        code = "model.fit(X_test, y_test)"
        tree = ast.parse(code)
        rule = TestSetContaminationRule()
        rule.visit(tree)
        self.assertTrue(any(v.rule_id == "SCI-006" for v in rule.collect()))

    def test_SCI_007_time_leakage(self):
        code = "train_test_split(X); df.sort_values('date')"
        tree = ast.parse(code)
        rule = TimeLeakageRule()
        rule.visit(tree)
        self.assertTrue(any(v.rule_id == "SCI-007" for v in rule.collect()))

    def test_SCI_008_label_leakage(self):
        code = "df['new'] = df['target'] * 2"
        tree = ast.parse(code)
        rule = LabelLeakageRule()
        rule.visit(tree)
        self.assertTrue(any(v.rule_id == "SCI-008" for v in rule.collect()))

    def test_SCI_002_random_seed(self):
        code = "train_test_split(X, y)"
        tree = ast.parse(code)
        rule = ReproducibilityRule()
        rule.visit(tree)
        self.assertTrue(any(v.rule_id == "SCI-002" for v in rule.collect()))

    def test_SCI_004_p_hacking(self):
        code = "ttest_ind(a,b); ttest_ind(c,d); ttest_ind(e,f); ttest_ind(g,h)"
        tree = ast.parse(code)
        rule = PHackingRule()
        rule.visit(tree)
        self.assertTrue(any(v.rule_id == "SCI-004" for v in rule.collect()))

    def test_SCI_005_overfitting_cego(self):
        code = "accuracy_score(y_true, y_pred)"
        tree = ast.parse(code)
        rule = OverfittingCegoRule()
        rule.visit(tree)
        self.assertTrue(any(v.rule_id == "SCI-005" for v in rule.collect()))

    def test_SCI_009_imbalance(self):
        code = "accuracy_score(y, pred)"
        tree = ast.parse(code)
        rule = ClassImbalanceRule()
        rule.visit(tree)
        self.assertTrue(any(v.rule_id == "SCI-009" for v in rule.collect()))

    def test_SCI_014_silent_nan(self):
        code = "df.dropna(inplace=True)"
        tree = ast.parse(code)
        rule = SilentNaNDropRule()
        rule.visit(tree)
        self.assertTrue(any(v.rule_id == "SCI-014" for v in rule.collect()))

    def test_SCI_017_time_shuffle(self):
        code = "train_test_split(X_date, y, shuffle=True)"
        tree = ast.parse(code)
        rule = ShuffleBeforeTimeSplitRule()
        rule.visit(tree)
        self.assertTrue(any(v.rule_id == "SCI-017" for v in rule.collect()))

    def test_SCI_013_causal_hubris(self):
        content = "# Este fator causa impacto no resultado"
        rule = CausalClaimsRule()
        rule.visit_content(content)
        self.assertTrue(any(v.rule_id == "SCI-013" for v in rule.collect()))

    # --- Casos Negativos (Garantia de que código bom não gera alerta) ---
    
    def test_no_false_positive_SCI_001(self):
        code = "X_train, X_test = train_test_split(X); scaler.fit(X_train)"
        tree = ast.parse(code)
        rule = TargetLeakageRule()
        rule.visit(tree)
        self.assertEqual(len(rule.collect()), 0)

    def test_no_false_positive_SCI_008(self):
        # O uso de 'y' como variável isolada não deve disparar Label Leakage
        code = "X, y = train_test_split(df); model.fit(X, y)"
        tree = ast.parse(code)
        rule = LabelLeakageRule()
        rule.visit(tree)
        self.assertEqual(len(rule.collect()), 0)

    def test_no_false_positive_SCI_014(self):
        code = "df.dropna(); print(df.shape)"
        tree = ast.parse(code)
        rule = SilentNaNDropRule()
        rule.visit(tree)
        self.assertEqual(len(rule.collect()), 0)

    def test_no_false_positive_SCI_002(self):
        code = "train_test_split(X, y, random_state=42)"
        tree = ast.parse(code)
        rule = ReproducibilityRule()
        rule.visit(tree)
        self.assertEqual(len(rule.collect()), 0)

if __name__ == "__main__":
    unittest.main()
