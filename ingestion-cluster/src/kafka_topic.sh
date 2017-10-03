#!/bin/bash
TOPIC=$1
PARTN=$2
REPF=$3

/usr/local/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --topic $TOPIC --partitions $PARTN --replication-factor $REPF
