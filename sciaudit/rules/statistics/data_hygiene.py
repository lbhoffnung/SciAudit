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
    def rule_name(self) -> str:
        return "Silent NaN Drop"

    @property
    def default_severity(self) -> Severity:
        return Severity.WARNING

    @property
    def hint(self) -> str:
        return "Adicione um print(df.shape) ou log após 'dropna()' para documentar quantos dados foram perdidos."

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self):
        super().reset()
        self._pending_dropna = [] # Lista de nós dropna sem reporte

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        if func_name == "dropna":
            self._pending_dropna.append(node)

        if func_name in ["print", "info", "log", "len", "shape", "head", "display"]:
            # Se houve um reporte, assumimos que todos os dropnas anteriores foram "registrados"
            self._pending_dropna = []

        self.generic_visit(node)

    def collect(self) -> list[Violation]:
        for node in self._pending_dropna:
            self.add_violation(
                message="Chamada de 'dropna()' detectada sem print/log subsequente. Remover dados silenciosamente pode introduzir vieses de seleção não documentados.",
                line=node.lineno,
                column=node.col_offset,
                snippet=ast.unparse(node) if hasattr(ast, "unparse") else "...",
                hint="Adicione um print(df.shape) ou log após chamadas de dropna()."
            )
        return self.violations

class ClassImbalanceRule(ScientificRule):
    """
    SCI-009: Detecta uso de accuracy em datasets possivelmente desbalanceados.
    """

    @property
    def rule_id(self) -> str:
        return "SCI-009"

    @property
    def rule_name(self) -> str:
        return "Imbalance Ignored"

    @property
    def default_severity(self) -> Severity:
        return Severity.WARNING

    @property
    def hint(self) -> str:
        return "Cheque o balanceamento de classes (df.value_counts()) ou use métricas como F1/AUC/MCC."

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
            self.add_violation(
                message="Uso de 'accuracy_score' detectado sem evidência de checagem de balanceamento de classes (ex: value_counts). Acurácia é uma métrica enganosa em datasets desbalanceados.",
                line=self._acc_node.lineno,
                column=self._acc_node.col_offset,
                snippet=ast.unparse(self._acc_node) if hasattr(ast, "unparse") else "...",
                hint="Cheque o balanceamento de classes (value_counts) antes de usar acurácia bruta."
            )
        return self.violations
