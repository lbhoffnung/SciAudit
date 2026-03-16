import ast
from ..base import ScientificRule
from ...core.models import Violation, Severity

class ReproducibilityRule(ScientificRule):
    """
    Detecta problemas de reprodutibilidade: falta de sementes determinísticas 
    em funções que possuem componente aleatório.
    """

    @property
    def rule_id(self) -> str:
        return "SCI-002"

    @property
    def rule_name(self) -> str:
        return "Falta de Semente"

    @property
    def default_severity(self) -> Severity:
        return Severity.WARNING

    @property
    def hint(self) -> str:
        return "Passe sempre um random_state ou seed em funções estocásticas (ex: train_test_split(..., random_state=42))."

    def __init__(self):
        super().__init__()
        # Funções que deveriam ter random_state ou seed
        self._stochastic_functions = {
            "train_test_split", "RandomForestClassifier", "RandomForestRegressor",
            "KMeans", "GradientBoostingClassifier", "SGDClassifier", "sample"
        }

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name in self._stochastic_functions:
            # Verifica se 'random_state' ou 'seed' está nos keywords
            has_seed = any(kw.arg in ["random_state", "seed", "random_seed"] for kw in node.keywords)
            
            if not has_seed:
                self.add_violation(
                    message=f"A função '{func_name}' foi chamada sem um 'random_state' ou 'seed' definido. Isso impede que seus resultados sejam reproduzidos exatamente.",
                    line=node.lineno,
                    column=node.col_offset,
                    snippet=ast.unparse(node) if hasattr(ast, "unparse") else "...",
                    hint="Passe sempre um random_state ou seed em funções estocásticas."
                )

        self.generic_visit(node)
