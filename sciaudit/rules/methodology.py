import ast
from .base import ScientificRule
from ..core.models import Violation, Severity

class FeatureImportanceRule(ScientificRule):
    """
    Detecta o 'Multicollinearity Trap': Tentar interpretar importância de features
    sem evidência de análise de correlação prévia.
    """

    @property
    def rule_id(self) -> str:
        return "SCI-003"

    @property
    def description(self) -> str:
        return "Atribuição de Importância sem Verificação de Correlação: Resultados podem ser enganosos devido a multicolinearidade."

    def __init__(self):
        super().__init__()
        self._has_correlation_check = False
        self._suspicious_attributes = {"feature_importances_", "coef_", "get_feature_importance"}
        self._found_interpretations = []

    def visit_Attribute(self, node: ast.Attribute):
        # Verifica se está acessando atributos de interpretação
        if node.attr in self._suspicious_attributes:
            self._found_interpretations.append(node)
        
        # Verifica se houve chamada a .corr() (comum em pandas)
        if node.attr == "corr":
            self._has_correlation_check = True

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Verifica chamadas a funções de visualização de correlação conhecidas
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            
        if any(term in func_name.lower() for term in ["heatmap", "corr", "vif", "correlation"]):
            self._has_correlation_check = True
            
        self.generic_visit(node)

    def collect(self) -> list[Violation]:
        violations = []
        if not self._has_correlation_check:
            for node in self._found_interpretations:
                violations.append(Violation(
                    rule_id=self.rule_id,
                    message=f"Atributo '{node.attr}' acessado sem evidência de checagem de correlação. Em presença de multicolinearidade, os valores de importância de features podem estar totalmente distorcidos.",
                    severity=Severity.MEDIUM,
                    line=node.lineno,
                    column=node.col_offset,
                    snippet=f"Acesso a: {ast.unparse(node) if hasattr(ast, 'unparse') else '...'}"
                ))
        return violations
