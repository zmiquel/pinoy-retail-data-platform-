import pandas as pd
import numpy as np
from pathlib import Path
import random

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
# Generate synthetic customer names
# -----------------------------
# Get unique customers from the adapted sales data
customer_ids = (
    sales["customer_id"]
    .dropna()
    .unique()
)

customers = pd.DataFrame({
    "customer_id": customer_ids
})
# -----------------------------
# Generate synthetic customer names
# -----------------------------

first_names = [
    "Juan", "Maria", "Jose", "Ana", "Carlo",
    "Miguel", "Sofia", "Mark", "Angela", "Paolo",
    "Kevin", "Nicole", "Daniel", "Christine", "Rafael",
    "Gabriel", "Andrea", "Joshua", "Patricia", "Christian",
    "Jerome", "Camille", "Francis", "Jasmine", "Nathan",
    "Bianca", "Adrian", "Clarisse", "Enrique", "Monica",
    "Anthony", "Beatrice", "Dominic", "Elaine", "Felix",
    "Hannah", "Ivan", "Julia", "Kyle", "Leah",
]

middle_names = [
    "Andres", "Antonio", "Benito", "Cesar", "Emilio",
    "Fernando", "Isabel", "Lorenzo", "Manuel", "Ramon",
    "Rico", "Roberto", "Samuel", "Teresa", "Victoria",
]

last_names = [
    "Santos", "Dela Cruz", "Reyes", "Garcia", "Mendoza",
    "Bautista", "Navarro", "Castillo", "Ramos", "Aquino",
    "Cruz", "Torres", "Villanueva", "Flores", "Gonzales",
    "Rivera", "Fernandez", "Manalo", "Mercado", "Salazar",
    "Magsaysay", "Valdez", "Santiago", "Aguilar", "Pascual",
    "Diaz", "Soriano", "Domingo", "Del Rosario", "Francisco",
]

# Create unique name combinations
name_pool = [
    f"{first} {middle} {last}"
    for first in first_names
    for middle in middle_names
    for last in last_names
]

# Randomize, but keep results reproducible
random.seed(42)
random.shuffle(name_pool)

# Make sure we have enough names
if len(customers) > len(name_pool):
    raise ValueError(
        f"Not enough unique customer names. "
        f"Need {len(customers)}, "
        f"but only {len(name_pool)} available."
    )

# Assign unique names
customers["customer_name"] = name_pool[:len(customers)]
customers["n_for_email"] = customers["customer_name"].str.split().str[0] + "." + customers["customer_name"].str.split().str[-1]
# Synthetic email based on customer ID
customers["email"] = (
    "c-" + customers["n_for_email"]
    + customers["customer_id"].astype(int).astype(str)
    + "@example.com"
)
customers = customers.drop(columns=["n_for_email"])
# Valid Philippine location combinations
locations = [
    {
        "city": "Calamba",
        "province": "Laguna",
        "region": "CALABARZON",
        "country_code": "PH",
    },
    {
        "city": "Santa Rosa",
        "province": "Laguna",
        "region": "CALABARZON",
        "country_code": "PH",
    },
    {
        "city": "Biñan",
        "province": "Laguna",
        "region": "CALABARZON",
        "country_code": "PH",
    },
    {
        "city": "Cabuyao",
        "province": "Laguna",
        "region": "CALABARZON",
        "country_code": "PH",
    },
    {
        "city": "Lipa",
        "province": "Batangas",
        "region": "CALABARZON",
        "country_code": "PH",
    },
    {
        "city": "Batangas City",
        "province": "Batangas",
        "region": "CALABARZON",
        "country_code": "PH",
    },
    {
        "city": "Tanauan",
        "province": "Batangas",
        "region": "CALABARZON",
        "country_code": "PH",
    },
    {
        "city": "Imus",
        "province": "Cavite",
        "region": "CALABARZON",
        "country_code": "PH",
    },
    {
        "city": "Dasmariñas",
        "province": "Cavite",
        "region": "CALABARZON",
        "country_code": "PH",
    },
    {
        "city": "Bacoor",
        "province": "Cavite",
        "region": "CALABARZON",
        "country_code": "PH",
    },
]

# Assign complete location records to customers
customer_locations = [
    locations[i % len(locations)]
    for i in range(len(customers))
]

customers["city"] = [
    location["city"]
    for location in customer_locations
]

customers["province"] = [
    location["province"]
    for location in customer_locations
]

customers["region"] = [
    location["region"]
    for location in customer_locations
]

customers["country_code"] = [
    location["country_code"]
    for location in customer_locations
]

# Save customer master
customers.to_csv(
    OUTPUT_DIR.parent / "customers.csv",
    index=False
)


# -----------------------------
# Generate product master
# -----------------------------

# Get unique products from adapted sales data
products = (
    sales[
        ["stock_code", "description"]
    ]
    .dropna(subset=["stock_code"])
    .drop_duplicates(subset=["stock_code"])
    .copy()
)

# Clean product name
products["product_name"] = (
    products["description"]
    .fillna("Unknown Product")
    .str.strip()
)

# -----------------------------
# Product categorization
# -----------------------------

def categorize_product(product_name):
    name = product_name.upper()

    if any(keyword in name for keyword in [
        "CANDLE",
        "LIGHT",
        "LAMP",
        "HOLDER",
        "DECOR",
        "HEART",
        "ORNAMENT",
        "FRAME",
    ]):
        return "Home & Living", "Home Decor"

    if any(keyword in name for keyword in [
        "MUG",
        "CUP",
        "PLATE",
        "BOWL",
        "GLASS",
        "SPOON",
        "FORK",
        "KITCHEN",
    ]):
        return "Home & Living", "Kitchen & Dining"

    if any(keyword in name for keyword in [
        "BAG",
        "PURSE",
        "WALLET",
        "SHOPPER",
        "TOTE",
    ]):
        return "Fashion & Accessories", "Bags & Accessories"

    if any(keyword in name for keyword in [
        "NECKLACE",
        "BRACELET",
        "EARRING",
        "RING",
        "JEWEL",
    ]):
        return "Fashion & Accessories", "Jewelry"

    if any(keyword in name for keyword in [
        "TOY",
        "GAME",
        "DOLL",
        "CHILDREN",
        "CHILD",
    ]):
        return "Toys & Hobbies", "Toys"

    if any(keyword in name for keyword in [
        "BOOK",
        "CARD",
        "PAPER",
        "NOTEBOOK",
        "PENCIL",
        "PEN",
    ]):
        return "Stationery & Gifts", "Stationery"

    if any(keyword in name for keyword in [
        "CHRISTMAS",
        "XMAS",
        "EASTER",
        "HALLOWEEN",
    ]):
        return "Seasonal", "Holiday Items"

    if any(keyword in name for keyword in [
        "SOAP",
        "PERFUME",
        "COSMETIC",
        "BEAUTY",
        "CREAM",
    ]):
        return "Personal Care", "Beauty & Personal Care"

    return "General Merchandise", "Other"


# Apply category rules
products[["category", "subcategory"]] = (
    products["product_name"]
    .apply(categorize_product)
    .apply(pd.Series)
)

# -----------------------------
# Synthetic brands
# -----------------------------

brands = [
    "Casa Lokal",
    "Bayan Finds",
    "Lokal Living",
    "Isla Home",
    "Pinoy Essentials",
    "Tahanan Co.",
    "Munting Tindahan",
    "Sari Goods",
]

products["brand"] = [
    brands[i % len(brands)]
    for i in range(len(products))
]

# Currency used by adapted Philippine source
products["currency"] = "PHP"

# Keep final product schema
products = products[
    [
        "stock_code",
        "product_name",
        "category",
        "subcategory",
        "brand",
        "currency",
    ]
]

# -----------------------------
# Validation
# -----------------------------

assert products["stock_code"].is_unique
assert products["product_name"].notna().all()

# Save product master
products.to_csv(
    OUTPUT_DIR.parent / "products.csv",
    index=False
)

print(f"Generated {len(products)} products")

# -----------------------------
# Output
# -----------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

monthly_sales = sales.groupby(sales["invoice_date"].dt.to_period("M"), sort=True)

for month, sales_month in monthly_sales:
    sales_month.to_csv(OUTPUT_DIR / f"sales_{month}.csv", index=False)
