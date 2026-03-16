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
    def rule_name(self) -> str:
        return "Time Leakage"

    @property
    def default_severity(self) -> Severity:
        return Severity.ERROR

    @property
    def hint(self) -> str:
        return "Evite reordenar dados após splits temporais (manter ordem cronológica)."

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self):
        super().reset()
        self._split_found = False
        self.violations = [] # Explicitly clearing violations

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if "split" in func_name.lower():
            self._split_found = True

        if self._split_found and func_name == "sort_values":
            self.add_violation(
                message="Chamada de 'sort_values' detectada após um split. Em séries temporais, isso pode misturar passado e futuro indevidamente no conjunto de treino.",
                line=node.lineno,
                column=node.col_offset,
                snippet=ast.unparse(node) if hasattr(ast, "unparse") else "...",
                hint="Evite reordenar dados após splits temporais (manter ordem cronológica)."
            )

        self.generic_visit(node)

class LabelLeakageRule(ScientificRule):
    """
    SCI-008: Detecta features derivadas diretamente do alvo (target).
    """

    @property
    def rule_id(self) -> str:
        return "SCI-008"

    @property
    def rule_name(self) -> str:
        return "Label Leakage"

    @property
    def default_severity(self) -> Severity:
        return Severity.ERROR

    @property
    def hint(self) -> str:
        return "Não use a variável alvo para derivar novas features."

    def visit_Assign(self, node: ast.Assign):
        # Procura por padrões tipo df['feature'] = df['target'] * x
        
        # 'y' removido para evitar falsos positivos críticos em todo projeto
        # Nomes comuns de target, mas ignoramos 'y' para evitar falsos positivos
        target_names = {
            "target", "label", "y_true", "y_train", "y_test", 
            "survived", "churn", "default", "price", "preço", 
            "valor", "classe", "category"
        }
        
        class TargetFinder(ast.NodeVisitor):
            def __init__(self):
                self.found = False
                self.target_node = None
            def visit_Subscript(self, s_node):
                # Detecta d['target'] ou df['target']
                if isinstance(s_node.slice, (ast.Constant, ast.Str)):
                    val = s_node.slice.value if isinstance(s_node.slice, ast.Constant) else s_node.slice.s
                    if str(val).lower() in target_names:
                        self.found = True
                        self.target_node = s_node
                self.generic_visit(s_node)
            
            def visit_Name(self, n_node):
                # Detecta variáveis com nomes muito específicos de target
                # Mas ignoramos se for apenas 'y' sozinho em nomes genéricos
                if n_node.id.lower() in target_names and len(n_node.id) > 1:
                    self.found = True
                    self.target_node = n_node
                self.generic_visit(n_node)

        finder = TargetFinder()
        finder.visit(node.value)
        
        if finder.found:
            self.add_violation(
                message=f"Possível Label Leakage: A variável '{ast.unparse(finder.target_node)}' (alvo) está sendo usada para criar uma nova variável no lado direito da atribuição.",
                line=node.lineno,
                column=node.col_offset,
                snippet=ast.unparse(node) if hasattr(ast, "unparse") else "...",
                hint="Não use a variável alvo para derivar novas features."
            )

        self.generic_visit(node)
