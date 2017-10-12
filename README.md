# B[ea]tcoin

A real-time trading tool for crypto-traders

# Description
In the last 5 years, cryptocurrencies have become a new form of financial assets designed to work as a medium of exchange. Because of the popularity of these new currencies, as well as the features and advantages they provide, many different cryptocurrency exchanges or markets have established with traders being widespread all around the world.
The objective of B[ea]coin is to be a centralized hub of real-time data from different cryptocurrency exchanges, such that traders are provided with information for best pricing and trades in order to **beat** the markets.

## Markets and data sources
B[ea]tcoin currently works with four of the biggest cryptocurrency exchanges in the world:

| Market                      |                                                                                                     |
|:-----------------------:|:-----------------------------------------------------------------------:|
| Coinbase (or GDAX) | <img src="img/coinbase.png" alt="coinbase" width="75px"/> |
| Bitfinex                     | <img src="img/bitfinex.png" alt="bitfinex" width="50px"/>       |
| CEX-IO                     | <img src="img/cexio.png" alt="cexio" width="85px"/>             |
| OkCoin                     | <img src="img/okcoin.png" alt="okcoin" width="85px"/>         |

Each of these markets provide a real-time API for users to have access to up-to-date order book and latest trading information through a websocket connection. B[ea]tcoin connects to all the APIs and collects the data from each market.
Similarly, B[ea]tcoin only provides information for only Bitcoin and Ethereum to US Dollars trades (BTC-USD and ETH-USD).

## Data Pipeline
The data pipeline implemented on the back-end of B[ea]tcoin is shown in the following diagram. Different APIs from the markets are ingested by several Kafka producers and categorized into different queues according to its nature ("buy order" or "sell order" depending on "BTC-USD" or "ETH-USD").
Next, Spark Streaming consumes all queues from Kafka and processes each message in a distributed manner to speed up execution time, and updates a cache-based Redis database that keeps the open book for each market as well as an aggregated open book.
The front-end is served by Flask where queries from users (i.e., traders) about specific markets or a combination of them may be selected.
![pipeline](img/pipeline.png?raw=true "pipeline")

## Set up instructions
This code runs on Amazon AWS EC2 servers.

### Installation
The code is executed in 4 different EC2 clusters:
1. **_ingestion-cluster_** that connects to all markets' APIs and sends mesages to the Kafka producers.
Needs: Zookeeper, Kafka, python3
2. **_processing-cluster_** that collects all messages with Spark Streaming and processes them to maintain an up-to-date order book from each market.
Needs: Hadoop, Spark, Spark Streaming, python3
3. **_db-stream-cluster_** keeps the open books Redis database which is constantly changing depending on the amount of activity at each market.
Needs: Redis, python3
4. **_web-server_** works as the server for the front-end website.
Needs: python3 (with Flask, Tornado)

### Deployment
To start B[ea]tcoin, there are several steps that need to be executed, however they have been easily packed into three shell scripts for the user to deploy it.
1. On the root `~` directory of *processing-cluster*, execute the following shell script: `$ ./src/startJob.sh`. This will start submit a *Spark* job into the scheduler to start consuming data from the Kafka broker.
**Note:** IP directions for the different clusters should be added into files `db-stream-ip.txt`, `ingestion-ip.txt` and `processing-ip.txt` located in `~/src/` directory.
2. On the root `~` directory of *ingestion-cluster*, execute the following shell script: `$ ./src/startMarkets.sh`. This will start the API for every market and for every product (BTC and ETH) and send every message to the specific Kafka topic.
3. On the root `~` directory of *web-server*, execute the following line to start the website: `$ sudo -E python3 tornadoapp.py`. The website will be available at [www.beatcoin.services](http://www.beatcoin.services/).
**Note:** IP direction for the Redis database should be added into file `db-stream-ip.txt` located in `~/src/app/` directory.

## Testing
The complete back-end was tested to analyze how many messages it could process, and on average, 5,000 messages (total and balanced for every topic) are successfully processed every second with no scheduling delays. This benchmark was run with a cluster consisting of 1 master and 3 worker nodes on m4.large EC2 instances.

## Demo
The presentation is available [here](https://drive.google.com/open?id=0B4JSY7CzxKlwWUdWOVFyX0MwY00).
The video for demo is available [here](http://youtu.be/xmxOe01nYi8).

---
> Gustavo Tapia. Insight Data Engineering - NYC Fall 2017
