import ast
import json
import os
import datetime
from typing import List, Dict
from .models import Violation, AuditReport, Severity
from ..rules.base import ScientificRule

class AuditEngine:
    """O motor central que coordena a análise AST e as regras."""
    
    def __init__(self):
        self.rules: List[ScientificRule] = []

    def register_rule(self, rule: ScientificRule):
        self.rules.append(rule)

    def _parse_ipynb(self, file_path: str) -> str:
        """Extrai o código das células de um Jupyter Notebook."""
        with open(file_path, "r", encoding="utf-8") as f:
            nb_data = json.load(f)
        
        full_code = []
        line_offset = 0
        for cell in nb_data.get("cells", []):
            if cell.get("cell_type") == "code":
                source = cell.get("source", [])
                if isinstance(source, list):
                    source = "".join(source)
                full_code.append(source)
                # Adicionamos uma quebra de linha entre células para manter a separação
                full_code.append("\n")
        
        return "".join(full_code)

    def audit_file(self, file_path: str) -> AuditReport:
        content = ""
        is_notebook = file_path.endswith(".ipynb")
        
        try:
            if is_notebook:
                content = self._parse_ipynb(file_path)
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            
            tree = ast.parse(content)
        except Exception as e:
            report = AuditReport(file_path=file_path)
            error_msg = str(e) if not isinstance(e, SyntaxError) else e.msg
            report.violations.append(Violation(
                rule_id="SYS-001",
                message=f"Falha ao processar arquivo: {error_msg}",
                severity=Severity.CRITICAL,
                line=getattr(e, 'lineno', 0),
                column=getattr(e, 'offset', 0)
            ))
            report.score = "F"
            return report

        report = AuditReport(file_path=file_path)
        
        for rule in self.rules:
            rule.reset()
            rule.visit_content(content)
            rule.visit(tree)
            report.violations.extend(rule.collect())

        report.score = self._calculate_score(report.violations)
        return report

    def generate_markdown_report(self, reports: List[AuditReport], avg_score: str) -> str:
        """Gera um laudo de integridade técnica em Markdown."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Cores conceituais para badges (urls de exemplo)
        color_map = {"A+": "brightgreen", "A": "green", "B": "yellow", "C": "orange", "D": "red", "F": "black"}
        badge_color = color_map.get(avg_score, "grey")
        badge_url = f"https://img.shields.io/badge/SciAudit_Score-{avg_score}-{badge_color}?style=for-the-badge&logo=python"

        md = f"""# 🛡️ Relatório de Integridade Científica: SciAudit
Gerado em: `{now}`

![SciAudit Badge]({badge_url})

## 📊 Sumário Executivo
- **Score Global do Projeto:** `{avg_score}`
- **Arquivos Auditados:** {len(reports)}
- **Total de Alertas:** {sum(len(r.violations) for r in reports)}

---

## 🔍 Detalhes por Arquivo
"""
        for r in reports:
            md += f"\n### 📄 `{os.path.basename(r.file_path)}`\n"
            md += f"- **Score:** `{r.score}`\n"
            md += f"- **Alertas:** {len(r.violations)}\n\n"
            
            if not r.violations:
                md += "> ✅ Nenhuma violação metodológica detectada.\n"
            else:
                md += "| Regra | Severidade | Mensagem | Linha |\n"
                md += "| :--- | :--- | :--- | :--- |\n"
                for v in r.violations:
                    md += f"| {v.rule_id} | {v.severity.value} | {v.message} | {v.line} |\n"
            
            md += "\n---\n"

        md += """
## 💡 Sugestões de Remediação
- **Para SCI-001 (Leakage):** Certifique-se de realizar o `train_test_split` antes de qualquer chamada a `StandardScaler`, `MinMaxScaler` ou `fit_transform`.
- **Para SCI-002 (Reprodutibilidade):** Sempre passe um `random_state` (ex: 42) em funções estocásticas do scikit-learn ou pandas.
- **Para SCI-003 (Multicolinearidade):** Antes de interpretar `feature_importances_`, use `df.corr()` ou um `heatmap` para demonstrar que você verificou se as variáveis não estão correlacionadas demais.

---
*Este relatório foi gerado automaticamente pelo [SciAudit](https://github.com/seu-usuario/SciAudit) - A integridade científica como código.*
"""
        return md

    def _calculate_score(self, violations: List[Violation]) -> str:
        if any(v.severity == Severity.CRITICAL for v in violations):
            return "F"
            
        # Penalidade por severidade
        score_value = 100
        for v in violations:
            if v.severity == Severity.CRITICAL: score_value -= 50
            elif v.severity == Severity.HIGH: score_value -= 20
            elif v.severity == Severity.MEDIUM: score_value -= 10
            elif v.severity == Severity.LOW: score_value -= 5
        
        if score_value < 0: score_value = 0

        if score_value >= 95: return "A+"
        if score_value >= 85: return "A"
        if score_value >= 70: return "B"
        if score_value >= 50: return "C"
        if score_value >= 30: return "D"
        return "F"
