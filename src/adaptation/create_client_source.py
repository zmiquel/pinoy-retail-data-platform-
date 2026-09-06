import pandas as pd
from pathlib import Path


# -----------------------------
# config
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2] 
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "online_retail.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "data" / "adapted" / "sales"



# -----------------------------
# Read UCI dataset
# -----------------------------

df = pd.read_excel(INPUT_FILE)

print(df.head())
print(df.info())

# -----------------------------
# Adapt UCI fields
# -----------------------------

sales = df.copy()

sales = sales.rename(
    columns={
        "InvoiceNo": "invoice_no",
        "StockCode": "stock_code",
        "Description": "description",
        "Quantity": "quantity",
        "InvoiceDate": "invoice_date",
        "UnitPrice": "unit_price",
        "CustomerID": "customer_id",
        "Country": "country",
    }
)

sales["country"] = "PH"
# -----------------------------
# Generate synthetic fields
# -----------------------------

invoice_hashes = pd.util.hash_pandas_object(
    sales["invoice_no"].astype("string"), index=False
)
sales["store_id"] = "PH-STORE-" + (invoice_hashes % 10 + 1).astype(str).str.zfill(3)


sales["currency"] = "PHP"
sales["sales_channel"] = "online"
sales["payment_method"] = (invoice_hashes % 3).map(
    {0: "cash", 1: "card", 2: "e_wallet"}
)


# -----------------------------
# Handle derived fields
# -----------------------------

sales["line_total"] = sales["quantity"] * sales["unit_price"]


# -----------------------------
# Output
# -----------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

monthly_sales = sales.groupby(sales["invoice_date"].dt.to_period("M"), sort=True)

for month, sales_month in monthly_sales:
    sales_month.to_csv(OUTPUT_DIR / f"sales_{month}.csv", index=False)
