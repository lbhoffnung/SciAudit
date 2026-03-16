import ast
from ..base import ScientificRule
from ...core.models import Violation, Severity

class TestSetContaminationRule(ScientificRule):
    """
    SCI-006: Detecta o uso do conjunto de teste em funções de treinamento (fit) 
    ou busca de hiperparâmetros (search).
    """

    @property
    def rule_id(self) -> str:
        return "SCI-006"

    @property
    def description(self) -> str:
        return "Contaminação do Conjunto de Teste: Uso de X_test/y_test em fase de treinamento."

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name in ["fit", "fit_transform", "search", "grid_search", "random_search"]:
            # Verifica se os argumentos passados contêm nomes 'test'
            for arg in node.args:
                if isinstance(arg, ast.Name) and "test" in arg.id.lower():
                    self.violations.append(Violation(
                        rule_id=self.rule_id,
                        message=f"O conjunto de teste '{arg.id}' foi passado para uma função de treinamento '{func_name}'. Isso invalida a avaliação do modelo.",
                        severity=Severity.CRITICAL,
                        line=node.lineno,
                        column=node.col_offset,
                        snippet=ast.unparse(node) if hasattr(ast, "unparse") else "..."
                    ))
            
            # Verifica keywords (ex: X=X_test)
            for kw in node.keywords:
                if isinstance(kw.value, ast.Name) and "test" in kw.value.id.lower():
                    self.violations.append(Violation(
                        rule_id=self.rule_id,
                        message=f"O conjunto de teste '{kw.value.id}' foi passado via keyword '{kw.arg}' para '{func_name}'.",
                        severity=Severity.CRITICAL,
                        line=node.lineno,
                        column=node.col_offset,
                        snippet=ast.unparse(node) if hasattr(ast, "unparse") else "..."
                    ))

        self.generic_visit(node)
