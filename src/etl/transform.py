from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType, IntegerType, TimestampType


def clean_strings(df: DataFrame) -> DataFrame:
    """Trim leading and trailing whitespace from string columns."""

    for field in df.schema.fields:
        if field.dataType.simpleString() == "string":
            df = df.withColumn(
                field.name,
                F.trim(F.col(field.name))
            )

    return df


def transform_sales(sales_df: DataFrame) -> DataFrame:
    """Clean and standardize the sales DataFrame."""

    sales_df = clean_strings(sales_df)

    sales_df = (
        sales_df
        .withColumn("quantity", F.col("quantity").cast(IntegerType()))
        .withColumn("invoice_date", F.col("invoice_date").cast(TimestampType()))
        .withColumn("unit_price", F.col("unit_price").cast(DecimalType(12, 2)))
        .withColumn("customer_id", F.col("customer_id").cast(IntegerType()))
        .withColumn("gross_sales", F.col("line_total").cast(DecimalType(14, 2)))
        .withColumn(
            "status",
            F.when(
                F.upper(F.col("invoice_no")).startswith("C"),
                F.lit("CANCELLED")
            ).otherwise(F.lit("COMPLETED"))
        )
        .withColumn(
            "net_sales",
            F.when(
                F.col("status") == "COMPLETED",
                F.col("gross_sales")
            ).otherwise(F.lit(0).cast(DecimalType(14, 2)))
        )
    )
    
    sales_df = sales_df.select(
        "invoice_no",
        "stock_code",
        "customer_id",
        "store_id",
        "description",
        "quantity",
        "invoice_date",
        "unit_price",
        "gross_sales",
        "net_sales",
        "country",
        "currency",
        "sales_channel",
        "payment_method",
        "status",
    )

    return sales_df


def transform_customers(customers_df: DataFrame) -> DataFrame:
    """Clean and standardize the customer DataFrame."""

    customers_df = clean_strings(customers_df)

    customers_df = customers_df.select(
        "customer_id",
        "customer_name",
        "email",
        "city",
        "province",
        "region",
        "country_code",
    )

    return customers_df


def transform_products(products_df: DataFrame) -> DataFrame:
    """Clean and standardize the product DataFrame."""

    products_df = clean_strings(products_df)

    products_df = products_df.select(
        "stock_code",
        "product_name",
        "category",
        "subcategory",
        "brand",
        "currency",
    )

    return products_df


def transform_stores(stores_df: DataFrame) -> DataFrame:
    """Clean and standardize the store DataFrame."""

    stores_df = clean_strings(stores_df)

    stores_df = stores_df.select(
        "store_id",
        "store_name",
        "city",
        "province",
        "region",
        "country_code",
    )

    return stores_df

def create_denormalized_sales(
    sales_df: DataFrame,
    customers_df: DataFrame,
    products_df: DataFrame,
    stores_df: DataFrame,
) -> DataFrame:
    """Enrich sales data with customer, product, and store attributes."""

    customers = customers_df.select(
        "customer_id",
        "customer_name",
        F.col("city").alias("customer_city"),
        F.col("province").alias("customer_province"),
        F.col("region").alias("customer_region"),
        "country_code",
    )

    products = products_df.select(
        "stock_code",
        "product_name",
        "category",
        "subcategory",
        "brand",
    )

    stores = stores_df.select(
        "store_id",
        "store_name",
        F.col("city").alias("store_city"),
        F.col("province").alias("store_province"),
        F.col("region").alias("store_region"),
        F.col("country_code").alias("store_country_code"),
    )

    denormalized_sales_df = (
        sales_df
        .join(customers, on="customer_id", how="left")
        .join(products, on="stock_code", how="left")
        .join(stores, on="store_id", how="left")
    )

    return denormalized_sales_df

if __name__ == "__main__":
    from extract import create_spark_session, extract_source_data

    spark = create_spark_session()

    data = extract_source_data(spark)

    sales_df = transform_sales(data["sales"])
    customers_df = transform_customers(data["customers"])
    products_df = transform_products(data["products"])
    stores_df = transform_stores(data["stores"])

    denormalized_sales_df = create_denormalized_sales(
        sales_df,
        customers_df,
        products_df,
        stores_df,
    )

    print("Sales rows:", sales_df.count())
    print("Denormalized sales rows:", denormalized_sales_df.count())

    denormalized_sales_df.printSchema()
    denormalized_sales_df.show(10, truncate=False)
    
    print("Customers:", customers_df.count())
    print("Unique customer IDs:", customers_df.select("customer_id").distinct().count())

    print("Products:", products_df.count())
    print("Unique stock codes:", products_df.select("stock_code").distinct().count())

    print("Stores:", stores_df.count())
    print("Unique store IDs:", stores_df.select("store_id").distinct().count())
    spark.stop()