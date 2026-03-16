import ast
from ..base import ScientificRule
from ...core.models import Violation, Severity

class TimeLeakageRule(ScientificRule):
    """
    SCI-007: Detecta manipulações temporais suspeitas após o split, 
    como re-ordenamento que pode vazar futuro pro passado.
    """

    @property
    def rule_id(self) -> str:
        return "SCI-007"

    @property
    def description(self) -> str:
        return "Time Leakage: Reordenação de dados temporais detectada após o split."

    def __init__(self):
        super().__init__()
        self._split_found = False

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if "split" in func_name.lower():
            self._split_found = True

        if self._split_found and func_name == "sort_values":
            self.violations.append(Violation(
                rule_id=self.rule_id,
                message="Chamada de 'sort_values' detectada após um split. Em séries temporais, isso pode misturar passado e futuro indevidamente no conjunto de treino.",
                severity=Severity.HIGH,
                line=node.lineno,
                column=node.col_offset,
                snippet=ast.unparse(node) if hasattr(ast, "unparse") else "..."
            ))

        self.generic_visit(node)

class LabelLeakageRule(ScientificRule):
    """
    SCI-008: Detecta features derivadas diretamente do alvo (target).
    """

    @property
    def rule_id(self) -> str:
        return "SCI-008"

    @property
    def description(self) -> str:
        return "Label Leakage: Criação de feature baseada diretamente na variável alvo."

    def visit_Assign(self, node: ast.Assign):
        # Procura por padrões tipo df['feature'] = df['target'] * x
        # Primeiro, verifica se há acesso a 'target' no lado direito
        
        target_names = {"target", "label", "y", "preço", "valor", "classe"} # Names comuns
        
        class TargetFinder(ast.NodeVisitor):
            def __init__(self):
                self.found = False
                self.target_node = None
            def visit_Subscript(self, s_node):
                if isinstance(s_node.slice, (ast.Constant, ast.Str)):
                    val = s_node.slice.value if isinstance(s_node.slice, ast.Constant) else s_node.slice.s
                    if str(val).lower() in target_names:
                        self.found = True
                        self.target_node = s_node
                self.generic_visit(s_node)
            def visit_Name(self, n_node):
                if n_node.id.lower() in target_names:
                    self.found = True
                    self.target_node = n_node

        finder = TargetFinder()
        finder.visit(node.value)
        
        if finder.found:
            self.violations.append(Violation(
                rule_id=self.rule_id,
                message=f"Possível Label Leakage: A variável '{ast.unparse(finder.target_node)}' (alvo) está sendo usada para criar uma nova variável no lado direito da atribuição.",
                severity=Severity.CRITICAL,
                line=node.lineno,
                column=node.col_offset,
                snippet=ast.unparse(node) if hasattr(ast, "unparse") else "..."
            ))

        self.generic_visit(node)
