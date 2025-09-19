# Batch ETL Pipeline with Apache Spark

This project demonstrates a batch ETL pipeline using Apache Spark that:

- Extracts two tables from a MySQL database into Spark DataFrames.
- Joins and aggregates the DataFrames to calculate the top-selling products.
- Writes the aggregated result into a Postgres table.

---

## Environment Setup

Run the following to start all services:

```bash
docker compose up --detach
```

Services started:
- mysql – source database
- postgres – destination database
- spark-master – Spark master node
- spark-worker – Spark worker node for executing jobs
- jupyterlab – Jupyter notebook environment for writing and deploying Spark jobs

⸻

# Create the Source Database (MySQL)

Access the MySQL container and log in:
```bash
docker compose exec mysql mysql -u mysqluser -p
```

The source database contains the following tables:
- orders
- products
- order_items

⸻

# Data Processing with PySpark

The Spark job written in Python using PySpark (spark_pipeline.py) and should be run inside JupyterLab.

Steps:
1. Read source tables from MySQL into Spark DataFrames.
2. Join and aggregate to calculate the top-selling products.
3. Write results to the Postgres destination database.

⸻

# Verify Results

After running the pipeline, check the results in Postgres:
```bash
docker compose exec postgres psql -U postgresuser -d masterclass
```

Run the query:
```bash
SELECT * FROM top_selling_products;
```

This should display the aggregated list of top-selling products.
