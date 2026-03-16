import ast
from .base import ScientificRule
from ..core.models import Violation, Severity

class TargetLeakageRule(ScientificRule):
    """
    Detecta Target Leakage: Normalização/Escalonamento ocorrendo antes do Split 
    de treino e teste.
    """

    @property
    def rule_id(self) -> str:
        return "SCI-001"

    @property
    def description(self) -> str:
        return "Possível Target Leakage: Transformações globais detectadas antes do split."

    def __init__(self):
        super().__init__()
        self._found_split = False
        self._transform_calls_before_split = []

    def visit_Call(self, node: ast.Call):
        # Detecção simplificada de funções comuns de split e transform
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        # Detectando o Split
        if "split" in func_name.lower():
            self._found_split = True

        # Detectando transforms (fit, transform, fit_transform, scale)
        transforms = {"fit", "transform", "fit_transform", "scale", "StandardScaler", "MinMaxScaler"}
        if func_name in transforms and not self._found_split:
            self._transform_calls_before_split.append(node)

        self.generic_visit(node)

    def collect(self) -> list[Violation]:
        violations = []
        for node in self._transform_calls_before_split:
            violations.append(Violation(
                rule_id=self.rule_id,
                message="Transformação de dados detectada possivelmente antes do train/test split. Isso pode causar vazamento de informações do conjunto de teste para o treino.",
                severity=Severity.HIGH,
                line=node.lineno,
                column=node.col_offset,
                snippet=f"Chamada de função: {ast.unparse(node) if hasattr(ast, 'unparse') else '...'}"
            ))
        return violations
