"""
Benchmarking-Loop Script (Ephemeral)

Purpose: Run CostEstimateGenerator on standalone past bid PDFs, compare outputs to actuals, and generate error metrics for estimator improvement. Not for permanent repo inclusion.
"""
import sys
from pathlib import Path
import pandas as pd

# Ensure src is on path for imports
sys.path.append(str(Path(__file__).resolve().parents[1] / 'CostEstimateGenerator' / 'src'))
from costest.eval import evaluate_contract, summarize_errors

PDF_FOLDER = Path('../CostEstimateGenerator/past-bids-for-training-AI')
WORK_DIR = Path('../CostEstimateGenerator/example_outputs/benchmarking_loop')
GLOB = '*.pdf'

WORK_DIR.mkdir(parents=True, exist_ok=True)
pdfs = sorted(PDF_FOLDER.glob(GLOB))
if not pdfs:
    print(f"No PDFs found in {PDF_FOLDER.resolve()} matching {GLOB}")
    sys.exit(1)

all_rows = []
for pdf in pdfs:
    print(f"Evaluating {pdf.name}...")
    try:
        merged, out_dir = evaluate_contract(pdf, WORK_DIR)
    except Exception as ex:
        print(f"Failed {pdf.name}: {ex}")
        continue
    merged['CONTRACT'] = pdf.stem
    all_rows.append(merged)
    merged.to_csv(out_dir / 'comparison.csv', index=False)

if not all_rows:
    print("No evaluations completed")
    sys.exit(2)

results = pd.concat(all_rows, ignore_index=True)
summary = summarize_errors(results.to_dict("records"))
results.to_csv(WORK_DIR / 'all_comparisons.csv', index=False)
pd.DataFrame([summary]).to_csv(WORK_DIR / 'summary_metrics.csv', index=False)
print("Summary:", summary)

# Optional: Call API AI for recommendations (pseudo-code)
# from api_ai import recommend_improvements
# recommendations = recommend_improvements(results)
# print("AI Recommendations:", recommendations)

print("\nNOTE: This script is for local benchmarking only. Remove before committing to the main repo.")
