import ast
from ..base import ScientificRule
from ...core.models import Violation, Severity

class SilentNaNDropRule(ScientificRule):
    """
    SCI-014: Detecta dropna() sem logs/prints que indiquem ciência do impacto.
    """

    @property
    def rule_id(self) -> str:
        return "SCI-014"

    @property
    def description(self) -> str:
        return "Silent NaN Drop: Remoção de dados faltantes sem registro do impacto."

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self):
        super().reset()
        self._pending_dropna = [] # Lista de nós dropna sem reporte

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        if func_name == "dropna":
            self._pending_dropna.append(node)

        if func_name in ["print", "info", "log", "len", "shape", "head", "display"]:
            # Se houve um reporte, assumimos que todos os dropnas anteriores foram "registrados"
            self._pending_dropna = []

        self.generic_visit(node)

    def collect(self) -> list[Violation]:
        for node in self._pending_dropna:
            self.violations.append(Violation(
                rule_id=self.rule_id,
                message="Chamada de 'dropna()' detectada sem print/log subsequente. Remover dados silenciosamente pode introduzir vieses de seleção não documentados.",
                severity=Severity.LOW,
                line=node.lineno,
                column=node.col_offset,
                snippet=ast.unparse(node) if hasattr(ast, "unparse") else "..."
            ))
        return self.violations

class ClassImbalanceRule(ScientificRule):
    """
    SCI-009: Detecta uso de accuracy em datasets possivelmente desbalanceados.
    """

    @property
    def rule_id(self) -> str:
        return "SCI-009"

    @property
    def description(self) -> str:
        return "Class Imbalance Ignored: Uso de acurácia sem checagem de balanceamento."

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self):
        super().reset()
        self._accuracy_found = False
        self._imbalance_check_found = False
        self._acc_node = None

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name == "accuracy_score":
            self._accuracy_found = True
            self._acc_node = node
        
        if func_name in ["value_counts", "Counter", "hist"]:
            self._imbalance_check_found = True

        self.generic_visit(node)

    def collect(self) -> list[Violation]:
        if self._accuracy_found and not self._imbalance_check_found:
            self.violations.append(Violation(
                rule_id=self.rule_id,
                message="Uso de 'accuracy_score' detectado sem evidência de checagem de balanceamento de classes (ex: value_counts). Acurácia é uma métrica enganosa em datasets desbalanceados.",
                severity=Severity.MEDIUM,
                line=self._acc_node.lineno,
                column=self._acc_node.col_offset,
                snippet=ast.unparse(self._acc_node) if hasattr(ast, "unparse") else "..."
            ))
        return self.violations
