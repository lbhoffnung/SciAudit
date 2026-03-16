import argparse
import sys
import os

from ..core.engine import AuditEngine
from ..rules.leakage.target_leakage import TargetLeakageRule
from ..rules.leakage.contamination import TestSetContaminationRule
from ..rules.leakage.temporal_label import TimeLeakageRule, LabelLeakageRule
from ..rules.reproducibility.random_seed import ReproducibilityRule
from ..rules.reproducibility.shuffle_logic import ShuffleBeforeTimeSplitRule
from ..rules.statistics.rigor import OverfittingCegoRule, PHackingRule
from ..rules.statistics.data_hygiene import ClassImbalanceRule, SilentNaNDropRule
from ..rules.causal.feature_importance import FeatureImportanceRule
from ..rules.causal.claims import CausalClaimsRule

def render_banner():
    banner = """
    \033[94m   _____Np_    _  _   _             _ _ _   
     / ____|  (_) / \ | |           | (_) |  
    | (___   ___ / _ \| |  _   _  __| |_| |_ 
     \___ \ / __/ /_\ \ | | | | |/ _` | | __|
     ____) | (__/ ___ \ | |_| | | (_| | | |_ 
    |_____/ \___/_/   \_\_| \__,_|\__,_|_|\__|
                                             \033[0m
    \033[93m>>> A integridade científica como código.\033[0m
    """
    print(banner)

def run_audit(target_path: str, export_report: bool = False):
    engine = AuditEngine()
    
    # Registrando as leis científicas por categoria
    # 1. Leakage
    engine.register_rule(TargetLeakageRule())
    engine.register_rule(TestSetContaminationRule())
    engine.register_rule(TimeLeakageRule())
    engine.register_rule(LabelLeakageRule())
    
    # 2. Reproducibility
    engine.register_rule(ReproducibilityRule())
    engine.register_rule(ShuffleBeforeTimeSplitRule())
    
    # 3. Statistics & Rigor
    engine.register_rule(OverfittingCegoRule())
    engine.register_rule(PHackingRule())
    engine.register_rule(ClassImbalanceRule())
    engine.register_rule(SilentNaNDropRule())
    
    # 4. Causal & Methodology
    engine.register_rule(FeatureImportanceRule())
    engine.register_rule(CausalClaimsRule())

    reports = []
    if os.path.isfile(target_path):
        reports.append(engine.audit_file(target_path))
    else:
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith((".py", ".ipynb")):
                    reports.append(engine.audit_file(os.path.join(root, file)))

    total_violations = 0
    scores = []

    for report in reports:
        total_violations += report.total_violations
        scores.append(report.score)
        
        name = os.path.basename(report.file_path)
        print(f"\n\033[1;97m📄 Arquivo: {name}\033[0m")
        
        score_colors = {"A+": "\033[92m", "A": "\033[92m", "B": "\033[93m", "C": "\033[93m", "D": "\033[91m", "F": "\033[1;91m"}
        c = score_colors.get(report.score, "\033[0m")
        print(f"Integridade: {c}{report.score}\033[0m | {report.total_violations} alertas detectados")
        
        print("\033[90m" + "─" * 50 + "\033[0m")
        
        for v in report.violations:
            sev_color = {"CRITICAL": "\033[1;91m", "HIGH": "\033[91m", "MEDIUM": "\033[93m", "LOW": "\033[96m"}
            s_col = sev_color.get(v.severity.value, "\033[0m")
            
            print(f"  {s_col}● {v.rule_id} [{v.severity.value}]\033[0m")
            print(f"    \033[97m{v.message}\033[0m")
            print(f"    \033[90mLinha {v.line}: {v.snippet}\033[0m\n")

    if reports:
        print("\033[90m" + "═" * 50 + "\033[0m")
        print(f"\033[1;97mRESUMO DA AUDITORIA\033[0m")
        print(f"Arquivos analisados: {len(reports)}")
        print(f"Total de violações: {total_violations}")
        
        avg_score = "F"
        if scores:
            # Simplificação da média de scores
            score_map = {"A+": 5, "A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
            inv_map = {v: k for k, v in score_map.items()}
            avg_val = round(sum(score_map.get(s, 0) for s in scores) / len(scores))
            avg_score = inv_map.get(avg_val, "F")
            
        final_c = score_colors.get(avg_score, "\033[0m")
        print(f"Score Médio do Projeto: {final_c}{avg_score}\033[0m")
        print("\033[90m" + "═" * 50 + "\033[0m")

        if export_report:
            md_content = engine.generate_markdown_report(reports, avg_score)
            with open("SCIAUDIT_REPORT.md", "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"\n\033[92m[✓] Laudo de Integridade gerado: SCIAUDIT_REPORT.md\033[0m")
    else:
        print("\033[91m[!] Nenhum arquivo (.py, .ipynb) encontrado para auditoria.\033[0m")

def main():
    parser = argparse.ArgumentParser(
        description="SciAudit: Auditor de integridade científica em código Python.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "path", 
        nargs="?", 
        default=".", 
        help="Caminho para o arquivo ou diretório a ser auditado (default: .)"
    )
    
    parser.add_argument(
        "--strict", 
        action="store_true", 
        help="Ativa o modo rigoroso (falha se o score for menor que A)"
    )

    parser.add_argument(
        "--report", 
        action="store_true", 
        help="Gera um laudo de integridade em Markdown (SCIAUDIT_REPORT.md)"
    )

    if len(sys.argv) == 1:
        render_banner()
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    
    render_banner()
    run_audit(args.path, export_report=args.report)

if __name__ == "__main__":
    main()
