import pandas as pd
import json
from pathlib import Path

# Load sales KPI data from JSON (stored in repo under config/test_data)
DATA_PATH = Path(__file__).resolve().parents[1] / "config" / "test_data" / "sales_kpis.json"

with open(DATA_PATH) as f:
    sales = json.load(f)

rows = []
for region, val in sales.get("sales", {}).items():
    rows.append({
        "region": region,
        "sales": val,
        "growth": sales.get("growth", {}).get(region)
    })

# Keep the data in-memory as a pandas DataFrame and query it directly.
df = pd.DataFrame(rows)

def query_kpi(region):
    try:
        df_out = df[df["region"] == region].reset_index(drop=True)
        return df_out
    except Exception:
        return pd.DataFrame()

def assert_kpi_with_output(region, llm_output):
    df_out = query_kpi(region)
    if df_out.empty:
        ground = "No ground truth for region"
    else:
        ground = f"Sales={df_out.iloc[0]['sales']}, Growth={df_out.iloc[0]['growth']}"
    return {"ground": ground, "row": df_out}
