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

from ..core.config import load_config
from ..core.models import Severity

def render_banner():
    banner = """
    \033[94m   _____Np_    _  _   _             _ _ _   
     / ____|  (_) / \\ | |           | (_) |  
    | (___   ___ / _ \\| |  _   _  __| |_| |_ 
     \\___ \\ / __/ /_\\ \\ | | | | |/ _` | | __|
     ____) | (__/ ___ \\ | |_| | | (_| | | |_ 
    |_____/ \\___/_/   \\_\\_| \\__,_|\\__,_|_|\\__|
                                             \033[0m
    \033[93m>>> A integridade científica como código.\033[0m
    """
    print(banner)

def get_engine():
    config = load_config()
    engine = AuditEngine(config=config)
    
    # Registrando as leis científicas por categoria
    engine.register_rule(TargetLeakageRule())
    engine.register_rule(TestSetContaminationRule())
    engine.register_rule(TimeLeakageRule())
    engine.register_rule(LabelLeakageRule())
    engine.register_rule(ReproducibilityRule())
    engine.register_rule(ShuffleBeforeTimeSplitRule())
    engine.register_rule(OverfittingCegoRule())
    engine.register_rule(PHackingRule())
    engine.register_rule(ClassImbalanceRule())
    engine.register_rule(SilentNaNDropRule())
    engine.register_rule(FeatureImportanceRule())
    engine.register_rule(CausalClaimsRule())
    
    return engine

def run_audit(paths: list[str], export_report: bool = False, output_format: str = "text", exit_strategy: str = "any-error", suggest: bool = False):
    engine = get_engine()
    reports = []
    
    for p in paths:
        if os.path.isfile(p):
            if not engine.config.should_ignore(p):
                reports.append(engine.audit_file(p))
        else:
            for root, _, files in os.walk(p):
                # Check if current directory should be ignored
                if engine.config.should_ignore(root):
                    continue
                for file in files:
                    if file.endswith((".py", ".ipynb")):
                        fpath = os.path.join(root, file)
                        if not engine.config.should_ignore(fpath):
                            reports.append(engine.audit_file(fpath))

    total_errors = sum(sum(1 for v in r.violations if v.severity == Severity.ERROR) for r in reports)
    total_warnings = sum(sum(1 for v in r.violations if v.severity == Severity.WARNING) for r in reports)
    total_infos = sum(sum(1 for v in r.violations if v.severity == Severity.INFO) for r in reports)
    
    scores = [r.score for r in reports]
    avg_score = "A+"
    if scores:
        score_map = {"A+": 5, "A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
        inv_map = {v: k for k, v in score_map.items()}
        avg_val = round(sum(score_map.get(s, 0) for s in scores) / len(scores))
        avg_score = inv_map.get(avg_val, "F")

    if output_format == "json":
        output = {
            "summary": {
                "score": avg_score,
                "errors": total_errors,
                "warnings": total_warnings,
                "infos": total_infos,
                "files_audited": len(reports)
            },
            "violations": []
        }
        for r in reports:
            for v in r.violations:
                output["violations"].append({
                    "id": v.rule_id,
                    "severity": v.severity.value,
                    "file": r.file_path,
                    "cell": v.cell,
                    "line": v.line,
                    "message": v.message,
                    "hint": v.hint,
                    "rule_name": v.rule_name
                })
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        render_banner()
        for report in reports:
            name = os.path.relpath(report.file_path)
            print(f"\n\033[1;97m📄 Arquivo: {name}\033[0m")
            
            score_colors = {"A+": "\033[92m", "A": "\033[92m", "B": "\033[93m", "C": "\033[93m", "D": "\033[91m", "F": "\033[1;91m"}
            c = score_colors.get(report.score, "\033[0m")
            print(f"Integridade: {c}{report.score}\033[0m | {len(report.violations)} alertas detectados")
            print("\033[90m" + "─" * 50 + "\033[0m")
            
            for v in report.violations:
                sev_color = {Severity.ERROR: "\033[1;91m", Severity.WARNING: "\033[93m", Severity.INFO: "\033[96m"}
                s_col = sev_color.get(v.severity, "\033[0m")
                cell_info = f" [Cell {v.cell}]" if v.cell else ""
                
                print(f"  {s_col}● {v.rule_id} [{v.severity.value}]{cell_info}\033[0m \033[1;97m{v.rule_name}\033[0m")
                print(f"    \033[97m{v.message}\033[0m")
                
                if suggest and v.hint:
                    print(f"    \033[1;92m➔ Sugestão: {v.hint}\033[0m")
                elif v.hint and output_format == "text":
                    print(f"    \033[90m💡 Dica: {v.hint}\033[0m")
                
                print(f"    \033[90mLinha {v.line}: {v.snippet}\033[0m\n")

        print("\033[90m" + "═" * 50 + "\033[0m")
        print(f"\033[1;97mRESUMO DA AUDITORIA\033[0m")
        print(f"Arquivos: {len(reports)} | ERR: {total_errors} | WRN: {total_warnings} | INF: {total_infos}")
        final_c = score_colors.get(avg_score, "\033[0m")
        print(f"Score Médio: {final_c}{avg_score}\033[0m")
        print("\033[90m" + "═" * 50 + "\033[0m")

    if export_report:
        md_content = engine.generate_markdown_report(reports, avg_score)
        with open("SCIAUDIT_REPORT.md", "w", encoding="utf-8") as f:
            f.write(md_content)
        if output_format == "text":
            print(f"\n\033[92m[✓] Laudo de Integridade gerado: SCIAUDIT_REPORT.md\033[0m")

    # Exit code logic
    if exit_strategy == "any-error":
        if total_errors > 0: sys.exit(1)
    elif exit_strategy == "errors-only":
        if total_errors > 0: sys.exit(1)
    # always-zero just continues

def main():
    parser = argparse.ArgumentParser(description="SciAudit: Integridade científica como código.")
    parser.add_argument("paths", nargs="*", default=["."], help="Arquivos ou diretórios (default: .)")
    parser.add_argument("--report", action="store_true", help="Gera SCIAUDIT_REPORT.md")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Formato da saída")
    parser.add_argument("--exit-code-strategy", choices=["any-error", "errors-only", "always-zero"], 
                        default="any-error", help="Estratégia de exit code")
    parser.add_argument("--suggest-fix", action="store_true", help="Mostra sugestões de correção detalhadas")
    
    args = parser.parse_args()
    
    try:
        run_audit(args.paths, export_report=args.report, output_format=args.format, 
                  exit_strategy=args.exit_code_strategy, suggest=args.suggest_fix)
    except SystemExit:
        raise
    except Exception as e:
        print(f"\033[91m[Fatal Error] {e}\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()
