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
    def rule_name(self) -> str:
        return "Overfitting Cego"

    @property
    def default_severity(self) -> Severity:
        return Severity.WARNING

    @property
    def hint(self) -> str:
        return "Use sempre validação cruzada (cross_val_score) em vez de apenas métricas simples em hold-out."

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
                self.add_violation(
                    message="Métrica de performance calculada sem evidência de validação cruzada (Cross-Validation). Resultados em hold-out simples podem ser excessivamente otimistas.",
                    line=node.lineno,
                    column=node.col_offset,
                    snippet=f"Uso de: {ast.unparse(node.func) if hasattr(ast, 'unparse') else '...'}",
                    hint="Use sempre cross_val_score ou GridSearchCV em vez de apenas métricas simples."
                )
        return self.violations

class PHackingRule(ScientificRule):
    """
    SCI-004: Tenta detectar indícios de P-Hacking (múltiplos testes sem correção).
    """

    @property
    def rule_id(self) -> str:
        return "SCI-004"

    @property
    def rule_name(self) -> str:
        return "P-Value Hacking"

    @property
    def default_severity(self) -> Severity:
        return Severity.WARNING

    @property
    def hint(self) -> str:
        return "Ao realizar múltiplos testes, use correções como Bonferroni ou FDR para evitar falsos positivos."

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
                self.add_violation(
                    message=f"Detectados {self._stat_tests_count} testes estatísticos sem funções de correção. Risco ALTO de P-Hacking.",
                    line=node.lineno,
                    column=node.col_offset,
                    snippet="Múltiplos testes sem correção detectados.",
                    hint="Use correções de comparativos múltiplos como Bonferroni ou FDR."
                )
            elif self._stat_tests_count >= 3:
                node = self._test_nodes[0]
                self.add_violation(
                    message=f"Detectados {self._stat_tests_count} testes estatísticos sem funções de correção. Risco MODERADO de P-Hacking.",
                    line=node.lineno,
                    column=node.col_offset,
                    snippet="Padrão de múltiplos testes sem correção.",
                    hint="Considere usar multipletests para ajustar os p-values."
                )
        return self.violations
