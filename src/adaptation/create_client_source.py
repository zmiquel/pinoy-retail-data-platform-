import pandas as pd
import numpy as np
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
# Generate store master
# -----------------------------

stores = pd.DataFrame(
    [
        {
            "store_id": "STR001",
            "store_name": "Seven Evelyn - Calamba",
            "city": "Calamba",
            "province": "Laguna",
            "region": "CALABARZON",
            "country_code": "PH",
        },
        {
            "store_id": "STR002",
            "store_name": "Tipid Tindahan - Batangas",
            "city": "Batangas City",
            "province": "Batangas",
            "region": "CALABARZON",
            "country_code": "PH",
        },
        {
            "store_id": "STR003",
            "store_name": "Ate Tess Mini Mart",
            "city": "Lipa",
            "province": "Batangas",
            "region": "CALABARZON",
            "country_code": "PH",
        },
        {
            "store_id": "STR004",
            "store_name": "Kuya Jun's Store",
            "city": "Calamba",
            "province": "Laguna",
            "region": "CALABARZON",
            "country_code": "PH",
        },
        {
            "store_id": "STR005",
            "store_name": "Suking Tindahan",
            "city": "Santa Rosa",
            "province": "Laguna",
            "region": "CALABARZON",
            "country_code": "PH",
        },
    ]
)

stores.to_csv(
    OUTPUT_DIR.parent / "stores.csv",
    index=False
)

# -----------------------------
# Assign store per invoice
# -----------------------------

invoice_store = pd.DataFrame({
    "invoice_no": sales["invoice_no"].unique()
})

invoice_store["store_id"] = np.random.choice(
    stores["store_id"],
    size=len(invoice_store)
)

sales = sales.merge(
    invoice_store,
    on="invoice_no",
    how="left"
)



# -----------------------------
# Output
# -----------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

monthly_sales = sales.groupby(sales["invoice_date"].dt.to_period("M"), sort=True)

for month, sales_month in monthly_sales:
    sales_month.to_csv(OUTPUT_DIR / f"sales_{month}.csv", index=False)
