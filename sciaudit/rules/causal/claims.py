import ast
import re
from ..base import ScientificRule
from ...core.models import Violation, Severity

class CausalClaimsRule(ScientificRule):
    """
    SCI-013: Detecta afirmações de causalidade em comentários sem evidência 
    de métodos de inferência causal ou variáveis de controle.
    """

    @property
    def rule_id(self) -> str:
        return "SCI-013"

    @property
    def rule_name(self) -> str:
        return "Causal Claims"

    @property
    def default_severity(self) -> Severity:
        return Severity.INFO

    @property
    def hint(self) -> str:
        return "Evite usar 'causa' ou 'efeito' em comentários sem métodos de inferência causal."

    def __init__(self):
        super().__init__()
        self._causal_keywords = [r"causa", r"impacto", r"efeito", r"decorrente de"]
        self._control_keywords = ["control", "vif", "instrumental", "propensity", "causal", "dag"]
        self.reset()

    def reset(self):
        super().reset()
        self._has_rigor = False
        self._suspicious_comments = []

    def visit_Module(self, node: ast.Module):
        # A análise de comentários em Python via AST requer acessar o atributo 'type_ignores'
        # ou, de forma mais robusta, ler o arquivo novamente.
        # Simplificação: Usaremos o visit_Call para detectar rigor e uma busca por comentários se possível.
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, (ast.Name, ast.Attribute)):
            func_name = ast.unparse(node.func).lower()
        
        if any(k in func_name for k in self._control_keywords):
            self._has_rigor = True
        
        self.generic_visit(node)

    def visit_content(self, content: str):
        # Como o AST não expõe comentários facilmente, faremos uma análise textual simples
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if "#" in line:
                comment = line.split("#")[1].lower()
                if any(re.search(k, comment) for k in self._causal_keywords):
                    # Se não detectamos rigor até agora
                    self._suspicious_comments.append((i+1, line.strip()))

    def collect(self) -> list[Violation]:
        if not self._has_rigor:
            for line_no, content in self._suspicious_comments:
                self.add_violation(
                    message="Afirmação de causalidade ('causa', 'impacto') detectada em comentário. Sem o uso de variáveis de controle ou inferência causal, correlação não implica causalidade.",
                    line=line_no,
                    column=0,
                    snippet=content,
                    hint="Evite usar 'causa' ou 'efeito' em comentários sem métodos de inferência causal."
                )
        return self.violations
