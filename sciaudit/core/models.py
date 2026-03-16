import ast
from dataclasses import dataclass, field
from typing import List, Optional, Any
from enum import Enum

class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class Violation:
    rule_id: str
    rule_name: str
    message: str
    severity: Severity
    line: int
    column: int
    cell: Optional[int] = None
    snippet: Optional[str] = None
    hint: Optional[str] = None

@dataclass
class AuditReport:
    file_path: str
    violations: List[Violation] = field(default_factory=list)
    score: str = "A+"

    @property
    def total_violations(self) -> int:
        return len(self.violations)
