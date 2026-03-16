import ast
from ..base import ScientificRule
from ...core.models import Violation, Severity

class ShuffleBeforeTimeSplitRule(ScientificRule):
    """
    SCI-017: Detecta o uso de shuffle em datasets que parecem ser temporais.
    """

    @property
    def rule_id(self) -> str:
        return "SCI-017"

    @property
    def description(self) -> str:
        return "Shuffle Before Time Split: Embaralhamento de dados temporais detectado."

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        # 1. Verifica se é um split com shuffle=True (ou default True)
        if "train_test_split" in func_name:
            shuffle_val = True # Default é True no sklearn
            for kw in node.keywords:
                if kw.arg == "shuffle" and isinstance(kw.value, ast.Constant):
                    shuffle_val = kw.value.value
            
            if shuffle_val:
                # Agora verifica se há indícios de série temporal no arquivo
                # (Simplificação: procura por 'date', 'time', 'ano', 'mes' no código)
                code_snippet = ast.unparse(node).lower()
                if any(x in code_snippet for x in ["date", "time", "ano", "data", "hora"]):
                    self.violations.append(Violation(
                        rule_id=self.rule_id,
                        message="Embaralhamento (shuffle=True) detectado em um split que parece envolver dados temporais. Isso destrói a estrutura de tempo e invalida a validação.",
                        severity=Severity.HIGH,
                        line=node.lineno,
                        column=node.col_offset,
                        snippet=ast.unparse(node) if hasattr(ast, "unparse") else "..."
                    ))

        # 2. Verifica df.sample(frac=1) sem shuffle=False
        if func_name == "sample":
            has_frac_1 = any(kw.arg == "frac" and getattr(kw.value, "value", None) == 1 for kw in node.keywords)
            if has_frac_1:
                 self.violations.append(Violation(
                    rule_id=self.rule_id,
                    message="Uso de '.sample(frac=1)' detectado. Se os dados forem temporais, isso causará vazamento de dados futuros no treino.",
                    severity=Severity.MEDIUM,
                    line=node.lineno,
                    column=node.col_offset,
                    snippet=ast.unparse(node) if hasattr(ast, "unparse") else "..."
                ))

        self.generic_visit(node)
