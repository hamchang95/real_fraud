from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()

n_customers = 1000000
df = spark.range(n_customers)
print(df.rdd.getNumPartitions())

spark.stop()