#!/bin/bash
SPARK_IP=$(head -1 processing-ip.txt)
KAFKA_IP=$(head -1 ingestion-ip.txt)
REDIS_IP=$(head -1 db-stream-ip.txt)
CASSANDRA_IP=$(head -1 db-batch-ip.txt)

until spark-submit --master spark://$SPARK_IP:7077 --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.2.0 spark-job.py $KAFKA_IP $REDIS_IP $CASSANDRA_IP; do
    echo "Server SPARK crashed with exit code $?.  Respawning.." >&2
    sleep 0.5
done
