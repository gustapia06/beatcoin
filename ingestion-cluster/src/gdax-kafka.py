import sys
from datetime import datetime
from kafka import KafkaProducer
import json
import time
from threading import Thread
from websocket import create_connection, WebSocketConnectionClosedException


class WebsocketClient(object):
    def __init__(self, products=None, channels="full", producer=None, addr='0.0.0.0', topic=""):
        self.url = "wss://ws-feed.gdax.com"
        self.products = products
        self.channels = channels
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

    def start(self):
        def _go():
            self._connect()
            self._listen()
        
        self.on_open()
        self.thread = Thread(target=_go())
        self.thread.start()
    
    def _connect(self):
        sub_params = {'type': 'subscribe', 'channels': self.channels, 'product_ids': self.products}
        self.ws = create_connection(self.url)
        self.ws.send(json.dumps(sub_params))

    def _listen(self):
        while not self.stop:
            try:
                if int(time.time() % 30) == 0:
                    # Set a 30 second ping to keep connection alive
                    self.ws.ping("keepalive")
                msg = json.loads(self.ws.recv())
            except Exception as e:
                self.on_error(e)
            else:
                self.on_message(msg)

    def close(self):
        if not self.stop:
            if self.channels == "heartbeat":
                self.ws.send(json.dumps({"type": "heartbeat", "on": False}))
            self.on_close()
            self.stop = True
            self.thread.join()
            try:
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
            if msg["type"] not in ['l2update','match']:
                return
            
            if self.topic == "book" and msg["type"] == 'l2update':
                fmt_msg = {'price': "{:.2f}".format(round(float(msg["changes"][0][1]), 2)),
                        'amount': msg["changes"][0][2],
                        'time': str(time.time())}
                topic = msg["changes"][0][0].lower() + '-' + msg["product_id"][0:3].lower()
            elif self.topic == "trades" and msg["type"] == 'match':
                fmt_msg = {'price': msg["price"],
                        'amount': msg["size"],
                        'time': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+0000")}
                topic = self.topic + '-' + msg["product_id"][0:3].lower()

            fmt_msg['market'] = "coinbase"
            
#            print(topic)
#            print(fmt_msg)
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
    products = str(sys.argv[3]).upper()
    if topic == 'book':
        chann = 'level2'
    elif topic == 'trades':
        chann = 'matches'

    wsClient = WebsocketClient(addr=ip_addr, channels = [chann], topic = topic, products = [products+"-USD"])
    wsClient.start()
#    wsClient.close()
