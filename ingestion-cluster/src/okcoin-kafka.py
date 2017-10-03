import sys
from datetime import datetime
from kafka import KafkaProducer
import json
import time
import hmac
import hashlib
from threading import Thread
from websocket import create_connection, WebSocketConnectionClosedException


class WebsocketClient(object):
    def __init__(self, products=None, producer=None, addr='0.0.0.0', topic=""):
        self.url = "wss://real.okcoin.com:10440/websocket/okcoinapi"
        self.products = products
        self.stop = False
        self.message_count = 0
        self.ws = None
        self.thread = None
        self.producer = KafkaProducer(bootstrap_servers=addr,
                                      key_serializer=lambda v: v.encode('ascii'),
                                      value_serializer=lambda v: json.dumps(v).encode('ascii'))
        self.topic = topic
        self.probCount = 0
        self.snapshot = 0
        self.channel = ''

    def start(self):
        def _go():
            self._connect()
            self._listen()
        
        self.on_open()
        self.thread = Thread(target=_go())
        self.thread.start()
    
    def _connect(self):
        if self.topic == 'book':
            self.channel = "ok_sub_spotusd_" + self.products + "_depth"
        elif self.topic == 'trades':
            self.channel = "ok_sub_spotusd_" + self.products + "_trades"
        sub_params = "{'event':'addChannel','channel':'" + self.channel + "'}"
        self.ws = create_connection(self.url)
        self.ws.send(sub_params)

    def _listen(self):
        while not self.stop:
            try:
                msg = json.loads(self.ws.recv()[1:-1])
            except Exception as e:
                self.on_error(e)
            else:
                self.on_message(msg)

    def close(self):
        if not self.stop:
            self.on_close()
            self.stop = True
            try:
                self.thread.join()
                if self.ws:
                    self.ws.close()
            except WebSocketConnectionClosedException as e:
                self.on_error(e)

    def on_open(self):
        pass

    def on_close(self):
        pass

    def on_message(self, msg):
#        print(msg)
        try:
            # try if 'type'=='snapshot'
            if msg["channel"] == self.channel and self.snapshot==0:
                self.snapshot = 1
                return

            if self.topic == "book" and msg["channel"] == self.channel:
                bids = msg["data"]["bids"]
                asks = msg["data"]["asks"]
                
                topic = 'buy-' + self.products
                for i in bids:
                    fmt_msg = {'price': "{:.2f}".format(round(float(i[0]), 2)),
                        'amount': str(i[1]),
#                        'product_id': self.products.upper() + "USD",
                        'market': "okcoin",
                        'time': str(time.time())}
#                    print(msg)
#                    print(topic)
                    self.producer.send(topic, key=topic, value=fmt_msg) #***************

                topic = 'sell-' + self.products
                for i in asks:
                    fmt_msg = {'price': "{:.2f}".format(round(float(i[0]), 2)),
                        'amount': str(i[1]),
#                        'product_id': self.products.upper() + "USD",
                        'market': "okcoin",
                        'time': str(time.time())}
#                    print(fmt_msg)
#                    print(topic)
                    self.producer.send(topic, key=topic, value=fmt_msg) #***************

            elif self.topic == "trades" and msg["channel"] == self.channel:
                trades = msg['data']
                for i in trades:
                    fmt_msg = {'price': i[1],
                        'amount': i[2],
#                        'product_id': self.products.upper() + "USD",
                        'market': "okcoin",
                        'time': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+0000")}

                topic = self.topic + '-' + self.product
#                print(fmt_msg)
                self.producer.send(topic, key=topic, value=fmt_msg) #***************

            self.probCount = 0
        except Exception as e:
            self.on_error(e)

    def on_error(self, e):
        print(e)
        self.probCount += 1
        if self.probCount > 10:
            self.close()
            exit(-1)

if __name__ == "__main__":
    ip_addr = str(sys.argv[1])
    topic = str(sys.argv[2])
    prod = str(sys.argv[3]).lower() #only BTC or ETH

    wsClient = WebsocketClient(addr=ip_addr, topic = topic, products = prod)
    wsClient.start()
#    wsClient.close()
