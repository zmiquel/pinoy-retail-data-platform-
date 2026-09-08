from pathlib import Path

from pyspark.sql import DataFrame, SparkSession


def create_spark_session() -> SparkSession:
    """Create a local Spark session for ETL development."""
    return (
        SparkSession.builder
        .appName("RetailSalesETL")
        .master("local[*]")
        .getOrCreate()
    )


def extract_source_data(spark: SparkSession) -> dict[str, DataFrame]:
    """Read adapted client source files into Spark DataFrames."""

    project_root = Path(__file__).resolve().parents[2]
    adapted_dir = project_root / "data" / "adapted"

    sales_df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(adapted_dir / "sales" / "*.csv"))
    )

    customers_df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(adapted_dir / "customers.csv"))
    )

    products_df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(adapted_dir / "products.csv"))
    )

    stores_df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(adapted_dir / "stores.csv"))
    )

    return {
        "sales": sales_df,
        "customers": customers_df,
        "products": products_df,
        "stores": stores_df,
    }
    
if __name__ == "__main__":
    spark = create_spark_session()

    data = extract_source_data(spark)

    for name, df in data.items():
        print(f"\n{name.upper()}")
        df.printSchema()
        print(f"Rows: {df.count()}")
        df.show(5, truncate=False)

    spark.stop()