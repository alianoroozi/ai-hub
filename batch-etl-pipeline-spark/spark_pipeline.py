from pyspark.sql import SparkSession
from pyspark.sql.functions import sum


# Create the Spark session
spark = (
    SparkSession.builder.appName("MyApp")
    .config(
        "spark.jars",
        "/home/ali/data/mysql-connector-j-9.4.0.jar,/home/ali/data/postgresql-42.7.7.jar",
    )
    .getOrCreate()
)

# Connectivity details for the source database, MySQL
url = "jdbc:mysql://mysql:3306/masterclass"
properties = {
    "user": "mysqluser",
    "password": "mysqlpwd",
    "driver": "com.mysql.jdbc.Driver",
}

df1 = spark.read.jdbc(url, "order_items", properties=properties)
df2 = spark.read.jdbc(url, "products", properties=properties)

joined_df = df1.join(df2, df1.product_id == df2.product_id, "inner").select(
    df2.product_id, df2.product_name, df1.total_price, df1.quantity
)
final_df = (
    joined_df.groupBy("product_id", "product_name")
    .agg(sum("quantity").alias("total_qty"))
    .sort("total_qty", ascending=False)
)

# Connectivity details for the target database, Postgres
url = "jdbc:postgresql://postgres:5432/masterclass"
properties = {
    "user": "postgresuser",
    "password": "postgrespwd",
    "driver": "org.postgresql.Driver",
}
table_name = "top_selling_products"

final_df.write.jdbc(url, table_name, properties=properties)
