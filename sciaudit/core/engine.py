import ast
import json
import os
import datetime
from typing import List, Dict, Optional
from .models import Violation, AuditReport, Severity
from ..rules.base import ScientificRule

from .config import Config

class AuditEngine:
    """O motor central que coordena a análise AST e as regras."""
    
    def __init__(self, config: Optional[Config] = None):
        self.rules: List[ScientificRule] = []
        self.config = config or Config()

    def register_rule(self, rule: ScientificRule):
        # Aplicar overrides do config
        rule_id = rule.rule_id
        if self.config.is_rule_off(rule_id):
            rule.enabled = False
        
        severity_val = self.config.get_rule_severity(rule_id)
        if severity_val:
            try:
                rule.severity_override = Severity(severity_val)
            except ValueError:
                pass
                
        self.rules.append(rule)

    def _parse_ipynb(self, file_path: str):
        """Extrai o código das células de um Jupyter Notebook e mapeia linhas para células."""
        with open(file_path, "r", encoding="utf-8") as f:
            nb_data = json.load(f)
        
        full_code = []
        line_to_cell = {}
        current_line = 1
        
        for idx, cell in enumerate(nb_data.get("cells", [])):
            if cell.get("cell_type") == "code":
                source = cell.get("source", [])
                source_str = "".join(source) if isinstance(source, list) else source
                
                cell_lines = source_str.splitlines(keepends=True)
                for i in range(len(cell_lines)):
                    line_to_cell[current_line + i] = idx + 1
                
                full_code.append(source_str)
                # Adicionamos uma quebra de linha entre células
                if not source_str.endswith("\n"):
                    full_code.append("\n")
                    current_line += len(cell_lines) + 1
                else:
                    current_line += len(cell_lines)
        
        return "".join(full_code), line_to_cell

    def audit_file(self, file_path: str) -> AuditReport:
        content = ""
        line_to_cell = {}
        is_notebook = file_path.endswith(".ipynb")
        
        try:
            if is_notebook:
                content, line_to_cell = self._parse_ipynb(file_path)
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            
            tree = ast.parse(content)
        except Exception as e:
            report = AuditReport(file_path=file_path)
            error_msg = str(e) if not isinstance(e, SyntaxError) else e.msg
            report.violations.append(Violation(
                rule_id="SYS-001",
                rule_name="System Error",
                message=f"Falha ao processar arquivo: {error_msg}",
                severity=Severity.ERROR,
                line=getattr(e, 'lineno', 0),
                column=getattr(e, 'offset', 0)
            ))
            report.score = "F"
            return report

        report = AuditReport(file_path=file_path)
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            rule.reset()
            rule.visit(tree)
            rule.visit_content(content)
            
            violations = rule.collect()
            if is_notebook:
                for v in violations:
                    v.cell = line_to_cell.get(v.line)
            
            report.violations.extend(violations)

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
- **Para SCI-001 (Leakage):** Realize o split *antes* de qualquer transformação (`StandardScaler`, `fit_transform`).
- **Para SCI-002 (Reprodutibilidade):** Passe sempre um `random_state` ou `seed` em funções estocásticas.
- **Para SCI-003 (Multicolinearidade):** Verifique a correlação (`df.corr()`) antes de interpretar importâncias.
- **Para SCI-004 (P-Hacking):** Use correções de comparativos múltiplos como Bonferroni ou FDR (`multipletests`).
- **Para SCI-005 (Overfitting):** Use sempre `cross_val_score` ou `GridSearchCV` em vez de apenas métricas simples.
- **Para SCI-006 (Contaminação):** Nunca passe `X_test` ou `y_test` para o método `fit()`.
- **Para SCI-007 (Time Leakage):** Evite reordenar dados após splits temporais (manter ordem cronológica).
- **Para SCI-008 (Label Leakage):** Não use a variável alvo para derivar novas features.
- **Para SCI-009 (Imbalance):** Cheque o balanceamento de classes (`value_counts`) antes de usar acurácia bruta.
- **Para SCI-013 (Causal Claims):** Evite usar "causa" ou "efeito" em comentários sem métodos de inferência causal.
- **Para SCI-014 (Silent Drop):** Adicione um `print(df.shape)` ou log após chamadas de `dropna()`.
- **Para SCI-017 (Time Shuffle):** Use `shuffle=False` em splits de séries temporais para preservar a causalidade temporal.

---
*Este relatório foi gerado automaticamente pelo [SciAudit](https://github.com/lbhoffnung/SciAudit) - A integridade científica como código.*
"""
        return md

    def _calculate_score(self, violations: List[Violation]) -> str:
        # Penalidade por severidade
        score_value = 100
        errors = sum(1 for v in violations if v.severity == Severity.ERROR)
        warnings = sum(1 for v in violations if v.severity == Severity.WARNING)
        infos = sum(1 for v in violations if v.severity == Severity.INFO)

        score_value -= (errors * 30)
        score_value -= (warnings * 10)
        score_value -= (infos * 2)
        
        if score_value < 0: score_value = 0

        # Regra de teto: se houver ERROR, o score máximo é B
        if errors > 0 and score_value > 70:
            return "B"

        if score_value >= 95: return "A+"
        if score_value >= 85: return "A"
        if score_value >= 70: return "B"
        if score_value >= 50: return "C"
        if score_value >= 30: return "D"
        return "F"
