import ast
from ..base import ScientificRule
from ...core.models import Violation, Severity

class OverfittingCegoRule(ScientificRule):
    """
    SCI-005: Detecta o uso de métricas de performance sem validação cruzada.
    """

    @property
    def rule_id(self) -> str:
        return "SCI-005"

    @property
    def description(self) -> str:
        return "Overfitting Cego: Uso de métricas simples sem Cross-Validation detectável."

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self):
        super().reset()
        self._metrics_found = []
        self._cv_found = False

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        metrics = {"accuracy_score", "r2_score", "mean_squared_error", "f1_score", "score"}
        cv_tools = {"cross_val_score", "cross_validate", "GridSearchCV", "RandomizedSearchCV", "KFold", "StratifiedKFold"}

        if func_name in metrics:
            self._metrics_found.append(node)
        
        if func_name in cv_tools:
            self._cv_found = True

        self.generic_visit(node)

    def collect(self) -> list[Violation]:
        if self._metrics_found and not self._cv_found:
            for node in self._metrics_found:
                self.violations.append(Violation(
                    rule_id=self.rule_id,
                    message="Métrica de performance calculada sem evidência de validação cruzada (Cross-Validation). Resultados em hold-out simples podem ser excessivamente otimistas.",
                    severity=Severity.HIGH,
                    line=node.lineno,
                    column=node.col_offset,
                    snippet=f"Uso de: {ast.unparse(node.func) if hasattr(ast, 'unparse') else '...'}"
                ))
        return self.violations

class PHackingRule(ScientificRule):
    """
    SCI-004: Tenta detectar indícios de P-Hacking (múltiplos testes sem correção).
    """

    @property
    def rule_id(self) -> str:
        return "SCI-004"

    @property
    def description(self) -> str:
        return "P-Value Hacking: Múltiplos testes estatísticos sem correção aparente."

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self):
        super().reset()
        self._stat_tests_count = 0
        self._has_correction = False
        self._test_nodes = []

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        stat_tests = {"ttest_ind", "ttest_rel", "pearsonr", "spearmanr", "anova", "pvalue", "chi2_contingency"}
        corrections = {"bonferroni", "fdr", "multipletests", "sidak", "holm"}

        if func_name in stat_tests:
            self._stat_tests_count += 1
            self._test_nodes.append(node)
        
        if any(c in func_name.lower() for c in corrections):
            self._has_correction = True

        self.generic_visit(node)

    def collect(self) -> list[Violation]:
        if not self._has_correction:
            if self._stat_tests_count >= 5:
                node = self._test_nodes[0]
                self.violations.append(Violation(
                    rule_id=self.rule_id,
                    message=f"Detectados {self._stat_tests_count} testes estatísticos sem funções de correção. Risco CRÍTICO de P-Hacking.",
                    severity=Severity.CRITICAL,
                    line=node.lineno,
                    column=node.col_offset,
                    snippet="Múltiplos testes sem correção detectados."
                ))
            elif self._stat_tests_count >= 3:
                node = self._test_nodes[0]
                self.violations.append(Violation(
                    rule_id=self.rule_id,
                    message=f"Detectados {self._stat_tests_count} testes estatísticos sem funções de correção. Recomendado usar Bonferroni/FDR.",
                    severity=Severity.MEDIUM,
                    line=node.lineno,
                    column=node.col_offset,
                    snippet="Padrão de múltiplos testes sem correção."
                ))
        return self.violations
