from abc import ABC, abstractmethod
import ast
from typing import List
from ..core.models import Violation

class ScientificRule(ABC, ast.NodeVisitor):
    """Classe base para todas as regras de integridade científica."""
    
    def __init__(self):
        self.violations: List[Violation] = []
        self.current_file: str = ""

    @property
    @abstractmethod
    def rule_id(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    def collect(self) -> List[Violation]:
        return self.violations

    def reset(self):
        self.violations = []

    def visit_content(self, content: str):
        """Opcional: Analisa o conteúdo bruto (ex: comentários)."""
        pass
