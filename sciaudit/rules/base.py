from abc import ABC, abstractmethod
import ast
from typing import List, Optional
from ..core.models import Violation, Severity

class ScientificRule(ABC, ast.NodeVisitor):
    """Classe base para todas as regras de integridade científica."""
    
    def __init__(self):
        self.violations: List[Violation] = []
        self.current_file: str = ""
        self.enabled: bool = True
        self.severity_override: Optional[Severity] = None

    @property
    @abstractmethod
    def rule_id(self) -> str:
        pass

    @property
    @abstractmethod
    def rule_name(self) -> str:
        pass

    @property
    @abstractmethod
    def default_severity(self) -> Severity:
        pass

    @property
    @abstractmethod
    def hint(self) -> str:
        pass

    @property
    def effective_severity(self) -> Severity:
        return self.severity_override if self.severity_override else self.default_severity

    def add_violation(self, message: str, line: int, column: int, snippet: Optional[str] = None, hint: Optional[str] = None, cell: Optional[int] = None):
        if not self.enabled:
            return
            
        self.violations.append(Violation(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            message=message,
            severity=self.effective_severity,
            line=line,
            column=column,
            cell=cell,
            snippet=snippet,
            hint=hint or self.hint
        ))

    def collect(self) -> List[Violation]:
        return self.violations

    def reset(self):
        self.violations = []

    def visit_content(self, content: str):
        """Opcional: Analisa o conteúdo bruto (ex: comentários)."""
        pass
