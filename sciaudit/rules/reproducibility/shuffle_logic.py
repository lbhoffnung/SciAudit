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
    def rule_name(self) -> str:
        return "Time Shuffle"

    @property
    def default_severity(self) -> Severity:
        return Severity.ERROR

    @property
    def hint(self) -> str:
        return "Use shuffle=False em splits de séries temporais para preservar a ordem cronológica."

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
                    self.add_violation(
                        message="Embaralhamento (shuffle=True) detectado em um split que parece envolver dados temporais. Isso destrói a estrutura de tempo e invalida a validação.",
                        line=node.lineno,
                        column=node.col_offset,
                        snippet=ast.unparse(node) if hasattr(ast, "unparse") else "...",
                        hint="Use shuffle=False em splits de séries temporais para preservar a causalidade temporal."
                    )

        # 2. Verifica df.sample(frac=1) sem shuffle=False
        if func_name == "sample":
            has_frac_1 = any(kw.arg == "frac" and getattr(kw.value, "value", None) == 1 for kw in node.keywords)
            if has_frac_1:
                 self.add_violation(
                    message="Uso de '.sample(frac=1)' detectado. Se os dados forem temporais, isso causará vazamento de dados futuros no treino.",
                    line=node.lineno,
                    column=node.col_offset,
                    snippet=ast.unparse(node) if hasattr(ast, "unparse") else "...",
                    hint="Evite reordenar dados se a ordem cronológica for importante."
                )

        self.generic_visit(node)
