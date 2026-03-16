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
                        check=False # We don't want it to crash if exit code is 1
                    )
                    
                    if res.stdout:
                        try:
                            data = json.loads(res.stdout)
                            violations = data.get("violations", [])
                            results.append({
                                "file": fpath,
                                "category": category,
                                "violation_count": len(violations),
                                "rules_triggered": ", ".join(set(v["id"] for v in violations)),
                                "score": data.get("summary", {}).get("score", "N/A")
                            })
                        except json.JSONDecodeError:
                            print(f"Error parsing JSON for {fpath}")
                    else:
                        print(f"No output for {fpath}: {res.stderr}")
                except Exception as e:
                    print(f"Failed to run SciAudit on {fpath}: {e}")

    # Save summary
    if results:
        # CSV
        with open("corpus_eval_summary.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\nEvaluation complete. Summary saved to 'corpus_eval_summary.csv'.")
    else:
        print("No results found.")

if __name__ == "__main__":
    eval_corpus()
