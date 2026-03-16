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
    def rule_name(self) -> str:
        return "Contaminação de Teste"

    @property
    def default_severity(self) -> Severity:
        return Severity.ERROR

    @property
    def hint(self) -> str:
        return "Nunca use dados de teste (X_test, y_test) durante a fase de treinamento (fit)."

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
                    self.add_violation(
                        message=f"O conjunto de teste '{arg.id}' foi passado para uma função de treinamento '{func_name}'. Isso invalida a avaliação do modelo.",
                        line=node.lineno,
                        column=node.col_offset,
                        snippet=ast.unparse(node) if hasattr(ast, "unparse") else "...",
                        hint="Nunca passe X_test ou y_test para o método fit()."
                    )
            
            # Verifica keywords (ex: X=X_test)
            for kw in node.keywords:
                if isinstance(kw.value, ast.Name) and "test" in kw.value.id.lower():
                    self.add_violation(
                        message=f"O conjunto de teste '{kw.value.id}' foi passado via keyword '{kw.arg}' para '{func_name}'.",
                        line=node.lineno,
                        column=node.col_offset,
                        snippet=ast.unparse(node) if hasattr(ast, "unparse") else "...",
                        hint="Verifique se está usando X_train/y_train no treinamento."
                    )

        self.generic_visit(node)
