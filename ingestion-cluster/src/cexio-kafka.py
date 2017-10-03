import sys
from datetime import datetime, timedelta
from kafka import KafkaProducer
import json
import time
import hmac
import hashlib
from threading import Thread
from websocket import create_connection, WebSocketConnectionClosedException


class WebsocketClient(object):
    def __init__(self, products=None, producer=None, addr='0.0.0.0', topic=""):
        self.url = "wss://ws.cex.io/ws/"
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

    def start(self):
        def _go():
            self._connect()
            self._listen()
        
        self.on_open()
        self.thread = Thread(target=_go())
        self.thread.start()
    
    def _connect(self):
        with open('cexio-keys.pem','r') as fp:
            lines = fp.readlines()
        cexiokeys = lines[1].split(',')
        
        self.ws = create_connection(self.url)
        sub_params = auth_request(cexiokeys[1].rstrip(), cexiokeys[2].rstrip())
        self.ws.send(json.dumps(sub_params))
        time.sleep(2)
        
        if self.topic == 'book':
            sub_params = {'e': "order-book-subscribe",'data': {'pair': [self.products,"USD"], 'subscribe': 'true', 'depth': 0},'oid': 'auth'}
        elif self.topic == 'trades':
            sub_params = {'e': "subscribe", "rooms": ["tickers"]}

        self.ws.send(json.dumps(sub_params))

    def _listen(self):
        while not self.stop:
            try:
                msg = json.loads(self.ws.recv())
                if msg['e'] == 'ping':
                    self.ws.send(json.dumps({"e":"pong"}))
                    pass
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
            if msg["e"] ==  "order-book-subscibe":
                return
            
            if self.topic == "book" and msg["e"] == "md_update":
                bids = msg["data"]["bids"]
                asks = msg["data"]["asks"]

                topic = 'buy-' + self.products.lower()
                for i in bids:
                    fmt_msg = {'price': "{:.2f}".format(round(float(i[0]), 2)),
                        'amount': str(i[1]) if i[1]!=0 else '0',
#                        'product_id': self.products + "USD",
                        'market': "cexio",
                        'time': str(time.time())}
#                    print(i)
#                    print(fmt_msg)
#                    print(topic)
                    self.producer.send(topic, key=topic, value=fmt_msg) #***************

                topic = 'sell-' + self.products.lower()
                for i in asks:
                    fmt_msg = {'price': "{:.2f}".format(round(float(i[0]), 2)),
                        'amount': str(i[1]) if i[1]!=0 else '0',
#                        'product_id': self.products + "USD",
                        'market': "cexio",
                        'time': str(time.time())}
                    
#                    print(fmt_msg)
#                    print(topic)
                    self.producer.send(topic, key=topic, value=fmt_msg) #***************

            elif self.topic == "trades" and msg["e"] == "tick":
                if msg["data"]["symbol2"] != "USD" or msg["data"]["symbol1"] not in ["BTC","ETH"]:
                    return

                fmt_msg = {'price': msg["data"]["price"],
                        'amount': '',
#                        'product_id': msg["data"]["symbol1"] + msg["data"]["symbol2"],
                        'market': "cexio",
                        'time': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+0000")}

                topic = self.topic + '-' + msg["data"]["symbol1"].lower()
#                print(fmt_msg)
#                print(topic)
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

def create_signature(key, secret):  # (string key, string secret)
#    timestamp = int(datetime.now().timestamp())  # UNIX timestamp in seconds
    timestamp = int((datetime.now() - timedelta(seconds=15)).timestamp())  # UNIX timestamp in seconds
    string = "{}{}".format(timestamp, key)
    return timestamp, hmac.new(secret.encode(), string.encode(), hashlib.sha256).hexdigest()

def auth_request(key, secret):
    timestamp, signature = create_signature(key, secret)
    return {'e': 'auth', 'auth': {'key': key, 'signature': signature, 'timestamp': timestamp,},
        'oid': 'auth'}

if __name__ == "__main__":
    ip_addr = str(sys.argv[1])
    topic = str(sys.argv[2])
    prod = str(sys.argv[3]).upper() #only BTC or ETH

    wsClient = WebsocketClient(addr=ip_addr, topic = topic, products = prod)
    wsClient.start()
#    wsClient.close()
