import sys
import json
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import redis
from cassandra.cluster import Cluster


def sendPartition(iter,topics,redisIP,cassandraIP):
    
    activeTopics = []
    redisDB = []

    for record in iter:
        iTopic = topics.index(record[0])
        msg = record[1]
        
        if iTopic < 4:
            key = record[1]['market'] + '-' + record[1]['price']
        
        try:
            if iTopic not in activeTopics:
                activeTopics.append(iTopic)

                if iTopic < 4:
                    redisDB.append(redis.StrictRedis(host=redisIP, port=6379, db=iTopic))
                elif ((iTopic == 4) and (5 not in activeTopics)) or ((iTopic == 5) and (4 not in activeTopics)):
                        cassandraCluster = Cluster([cassandraIP])
                        cassandraDB = cassandraCluster.connect('crypto')
        
            if iTopic < 4:
                iDB = activeTopics.index(iTopic)

                if redisDB[iDB].exists(key):
                    existsTime = redisDB[iDB].hget(key,'time')

                    if float(msg['time']) > float(existsTime):
                        if msg['amount'] == '0':
                            redisDB[iDB].delete(key)
                            redisDB[iDB].zrem('all',key)
                            redisDB[iDB].zrem(msg['market'],key)
                        else:
                            redisDB[iDB].hmset(key,msg)
                            redisDB[iDB].zadd('all',msg['price'],key)
                            redisDB[iDB].zadd(msg['market'],msg['price'],key)
                else:
                    
                    if msg['amount'] != '0':
                        redisDB[iDB].hmset(key,msg)
                        redisDB[iDB].zadd('all',msg['price'],key)
                        redisDB[iDB].zadd(msg['market'],msg['price'],key)

            else:
                if iTopic == 4:
                    query = "INSERT INTO crypto.trades_btc JSON '"
                elif iTopic == 5:
                    query = "INSERT INTO crypto.trades_eth JSON '"

                cassandraDB.execute(query + json.dumps(msg) + "'")
        except Exception as e:
            print(e)
            continue

if __name__ == "__main__":
    kafkaIP = str(sys.argv[1]) + ':9092'
    redisIP = str(sys.argv[2])
    cassandraIP = str(sys.argv[3])
    topics = ["buy-btc","sell-btc","buy-eth","sell-eth","trades-btc","trades-eth"]

    sc = SparkContext(appName='b[ea]tcoin')
    sc.setLogLevel("ERROR")
    ssc = StreamingContext(sc, 1)

    kafkaStream = KafkaUtils.createDirectStream(ssc,
                                                topics,
                                                {"bootstrap.servers": kafkaIP},
                                                keyDecoder=lambda x: x.decode('ascii'),
                                                valueDecoder=lambda x: json.loads(x.decode('ascii')))

    kafkaStream.foreachRDD(lambda rdd: rdd.foreachPartition(lambda x: sendPartition(x,topics,redisIP,cassandraIP)))

    ssc.start()
    ssc.awaitTermination()
