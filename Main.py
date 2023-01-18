from pyspark.sql import SparkSession
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
import time


def spark_wordcount():
    spark = SparkSession \
        .builder \
        .appName("APP") \
        .config("spark.cassandra.connection.host", "cassandra-server") \
        .config("spark.cassandra.connection.port", "9042") \
        .config("spark.cassandra.auth.username", "cassandra") \
        .config("spark.cassandra.auth.password", "cassandra") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "my_word_count") \
        .option("topic.creation.enable", "true") \
        .option("startingOffsets", "earliest") \
        .load()

    df_cast = df.selectExpr("CAST(value AS STRING) as word")
    wordcount = df_cast \
        .groupBy('word').count()

    def writeToCassandra(writeDF, _):
        writeDF.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode('append') \
            .options(table="word_count", keyspace="ks_wordcount") \
            .save()

    wordcount.writeStream \
        .trigger(processingTime='2 seconds') \
        .outputMode("update") \
        .foreachBatch(writeToCassandra) \
        .start() \
        .awaitTermination()


def connect_cassandra():
    while True:
        try:
            auth_cass = PlainTextAuthProvider(username='cassandra', password='cassandra')
            cluster = Cluster(['cassandra-server'],
                              port=9042,
                              auth_provider=auth_cass)
            session = cluster.connect()
            session.execute(
                "CREATE KEYSPACE IF NOT EXISTS ks_wordcount WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor' : 1}")
            session.execute(
                "CREATE TABLE IF NOT EXISTS ks_wordcount.word_count (word text, count int, PRIMARY KEY (word))")
            successful = True
            print("successful")
            break

        except Exception:
            time.sleep(5)
            print('Connecting to Cassandra...')
    return successful


def main():
    if connect_cassandra():
        spark_wordcount()
    else:
        main()


if __name__ == "__main__":
    main()
