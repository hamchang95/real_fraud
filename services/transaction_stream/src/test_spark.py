# Import necessary libraries
import os
import numpy as np
import pandas as pd
import datetime
import time
import random
import matplotlib.pyplot as plt
import sys
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, FloatType, IntegerType
from pyspark.sql.functions import floor, lit, array, date_diff, date_sub, date_add, current_date, col, size, rand, uniform, to_date, from_unixtime

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()

n_customers = int(sys.argv[1]) if len(sys.argv) > 1 else 1000000

##### Customer profiles table generation #####
def array_choice(array):
    index = (rand()*size(array)).cast("int")
    return array[index]

def generate_customer_profiles_table(n_customers):
    # define epoch time range 
    dob_epoch_end = 1199145600 # Corresponds to 2008-01-01, minimum age of 18 years in 2026
    dob_epoch_start = -1388534400 # Corresponds to 1926-01-01, maximum age of 100 years in 2026
    open_epoch_start = 1735689600 # Corresponds to 2025-01-01
    open_epoch_end = 1772323200 # Corresponds to 2026-03-01
    
    # define delta
    delta_transaction = uniform(0, 365*2, seed=234).cast('int') 

    # define categorical features and their possible values
    gender = array(*[lit(g) for g in ['M', 'F']])
    card_type = array(*[lit(ct) for ct in ['debit', 'credit']])
    card_tier = array(*[lit(ct) for ct in ['standard', 'gold', 'platinum']])
    first_names = array(*[lit(fn) for fn in ['Mohammed', 'Mahmoud', 'Mohammad', 'Mohamed', 'Mohamad', 'Hasheem', 'Ahmed', 'Ibrahim', 'Saheed', 'James', 'Hannah', 'Anna', 'Charles', 'Charlie', 'Hector', 'Robert', 'Bob', 'Bobby', 'Marie', 'Mary', 'Marry', 'Lizzy', 'Liz', 'Elizabeth', 'Dunah', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'David', 'Joseph', 'Joe', 'Haewon', 'Hae Won', 'Sangah', 'Sang Ah', 'Yuna', 'Yu Na', 'Yuri', 'Yu Ri', 'Minji', 'Min Ji', 'Seohyun', 'Seo Hyun']])
    last_names = array(*[lit(ln) for ln in ['Ali', 'Jang', 'Chang', 'Park', 'Lee', 'Kim', 'McDonald', 'Mcdonald', 'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Anderson', 'Hamid', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson']])

    df = spark.range(n_customers) \
    .withColumn("x_customer_id", (uniform(50.0, 58.0, seed=1234)).cast('float')) \
    .withColumn("y_customer_id", (uniform(-5.0, 2.0, seed=123)).cast('float')) \
    .withColumn("first_name", array_choice(first_names)) \
    .withColumn("last_name", array_choice(last_names)) \
    .withColumn("mean_amount", (uniform(5, 1000, seed=124)).cast('float')) \
    .withColumn("std_amount", (col("mean_amount") / 2).cast('float')) \
    .withColumn("mean_nb_tx_per_day", (uniform(0, 4, seed=234)).cast('float')) \
    .withColumn("epoch_date_of_birth", uniform(dob_epoch_start, dob_epoch_end, seed=345).cast('long')) \
    .withColumn("date_of_birth", to_date(from_unixtime(col("epoch_date_of_birth")))) \
    .withColumn("age", floor(date_diff(current_date(), col("date_of_birth"))/365)) \
    .withColumn("epoch_account_open_date", uniform(open_epoch_start, open_epoch_end, seed=345).cast('long')) \
    .withColumn("account_open_date", to_date(from_unixtime(col("epoch_account_open_date")))) \
    .withColumn("card_expiry_date", date_add(col("account_open_date"), 365*6)) \
    .withColumn("last_transaction_date", date_add(current_date(), delta_transaction)) \
    .withColumn("gender", array_choice(gender)) \
    .withColumn("card_type", array_choice(card_type)) \
    .withColumn("card_tier", array_choice(card_tier)) 


    df = df \
    .withColumnRenamed("id", "CUSTOMER_ID") \
    .drop(*['epoch_date_of_birth', 'epoch_account_open_date'])

    df.printSchema()
    df.show(5)
    return df

if __name__ == "__main__":
    customer_profiles_table = generate_customer_profiles_table(n_customers)

spark.stop()