import os
import subprocess
import json
import csv
import sys

def eval_corpus():
    corpus_dir = "corpus"
    if not os.path.exists(corpus_dir):
        print("Error: 'corpus' directory not found.")
        sys.exit(1)

    results = []
    
    rule_metrics = {} # rule_id -> {"good": count, "bad": count}

    for category in ["good", "bad"]:
        path = os.path.join(corpus_dir, category)
        if not os.path.exists(path): continue
        
        for file in os.listdir(path):
            if file.endswith((".py", ".ipynb")):
                fpath = os.path.join(path, file)
                print(f"Evaluating {fpath}...")
                
                # Run sciaudit in JSON mode
                try:
                    res = subprocess.run(
                        ["python", "-m", "sciaudit", fpath, "--format", "json"],
                        capture_output=True,
                        text=True,
                        check=False,
                        env={**os.environ, "PYTHONPATH": "."}
                    )
                    
                    if res.stdout:
                        try:
                            # Clean potential encoding noise from start of stdout
                            clean_stdout = res.stdout[res.stdout.find("{"):]
                            data = json.loads(clean_stdout)
                            violations = data.get("violations", [])
                            
                            rule_ids_in_file = set()
                            for v in violations:
                                rid = v["id"]
                                rule_ids_in_file.add(rid)
                                if rid not in rule_metrics:
                                    rule_metrics[rid] = {"good": 0, "bad": 0}
                                rule_metrics[rid][category] += 1

                            results.append({
                                "file": fpath,
                                "is_good": (category == "good"),
                                "violation_count": len(violations),
                                "rules_triggered": ", ".join(rule_ids_in_file),
                                "score": data.get("summary", {}).get("score", "N/A"),
                                "errors": data.get("summary", {}).get("errors", 0),
                                "warnings": data.get("summary", {}).get("warnings", 0),
                                "infos": data.get("summary", {}).get("infos", 0)
                            })
                        except json.JSONDecodeError as je:
                            print(f"Error parsing JSON for {fpath}: {je}")
                    else:
                        print(f"No output for {fpath}: {res.stderr}")
                except Exception as e:
                    print(f"Failed to run SciAudit on {fpath}: {e}")

    # Save summary
    if results:
        with open("corpus_eval_summary.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        
        # Save rule metrics
        with open("rule_metrics.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["rule_id", "triggered_in_good", "triggered_in_bad"])
            writer.writeheader()
            for rid, counts in sorted(rule_metrics.items()):
                writer.writerow({
                    "rule_id": rid,
                    "triggered_in_good": counts["good"],
                    "triggered_in_bad": counts["bad"]
                })
        
        print(f"\nEvaluation complete. Summaries saved to 'corpus_eval_summary.csv' and 'rule_metrics.csv'.")

if __name__ == "__main__":
    eval_corpus()
