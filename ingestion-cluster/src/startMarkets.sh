#!/bin/bash
for TOPIC in book trades;
do
    for CURRENCY in btc eth;
    do
        for MARKET in gdax bitfinex cexio okcoin;
        do
            LOGFILE="$MARKET-$TOPIC-$CURRENCY.log"
            ./startAPI.sh $MARKET $TOPIC $CURRENCY >> $LOGFILE 2>&1 &
        done
    done
done
