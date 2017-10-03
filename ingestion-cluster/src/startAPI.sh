#!/bin/bash
MARKET=$1
TOPIC=$2
CURRENCY=$3
until python3 $MARKET-kafka.py localhost $TOPIC $CURRENCY;
do
    echo "Server $MARKET $TOPIC $CURRENCY crashed with exit code $?.  Respawning.." >&2
    sleep 0.5
done
