
import duckdb, pandas as pd, json

with open("config/test_data/sales_kpis.json") as f:
    sales = json.load(f)

rows = []
for region, val in sales["sales"].items():
    rows.append({
        "region": region,
        "sales": val,
        "growth": sales["growth"][region]
    })

df = pd.DataFrame(rows)
con = duckdb.connect(database=":memory:")
con.register("df_sales", df)
con.execute("CREATE TABLE sales_kpi AS SELECT * FROM df_sales")

def query_kpi(region):
    try:
        return con.execute(f"SELECT * FROM sales_kpi WHERE region = '{region}'").df()
    except:
        return pd.DataFrame()

def assert_kpi_with_output(region, llm_output):
    df_out = query_kpi(region)
    if df_out.empty:
        ground = "No ground truth for region"
    else:
        ground = f"Sales={df_out.iloc[0]['sales']}, Growth={df_out.iloc[0]['growth']}"
    return {"ground": ground, "row": df_out}
