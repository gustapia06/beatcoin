from flask import render_template, send_from_directory, request, jsonify
from app import app
import random
import time
import redis
import os

# options in navbar
navbar = ['Home','Open Book','Trades']
navlinks = ['/home','/book','/trades']

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(APP_ROOT,'db-stream-ip.txt'),'r') as fp:
    lines = fp.readlines()
redisIP = lines[0]

buy_btc = redis.StrictRedis(host=redisIP, port=6379, db=0, decode_responses=True)
sell_btc = redis.StrictRedis(host=redisIP, port=6379, db=1, decode_responses=True)
buy_eth = redis.StrictRedis(host=redisIP, port=6379, db=2, decode_responses=True)
sell_eth = redis.StrictRedis(host=redisIP, port=6379, db=3, decode_responses=True)

def getPrices(db,side,markets,numElements):
    db.delete('tmp')
    if len(markets) == 1:
        key = markets[0]
    elif len(markets) < 4:
        db.zunionstore('tmp', markets)
        key = 'tmp'
    else:
        key = 'all'

    if side=='buy':
        top = db.zrevrange(key,0,numElements-1)
    elif side=='sell':
        top = db.zrange(key,0,numElements-1)

    dataPrices = {}
    for market in markets:
        dataPrices[market] = []
        msgs = db.zrange(market,0,-1)
        for msg in msgs:
            dataPrices[market].append(db.hmget(msg,'price','amount'))

    return top, dataPrices

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
  return render_template("home.html", active='Home', navbar=navbar, navlinks=navlinks)

@app.route('/book', methods=['GET'])#,'POST'])
def book():
    if request.method == "GET":
#        checked = ['coinbase','bitfinex','cexio','okcoin','btc']
        return render_template("book.html", active='Open Book', navbar=navbar, navlinks=navlinks)#,checked=checked)
#    elif request.method == "POST":
#        if request.form['submit'] == 'submit':
#            print(request.form)
#            currency = request.form["currency"]
#            markets = request.form.getlist('markets')
#            print('******* post *************')
#            print(currency)
#            print(markets)
#            print('*****************************')
#            checked = [currency] + markets
#            return render_template("book.html", active='Open Book', navbar=navbar, navlinks=navlinks,checked=checked)

@app.route('/_get_book')
def getBookData():
    markets = request.args.get('markets').split(',')#, 0, type=int)
    currency = request.args.get('currency')#, 0, type=int)
    numElements = int(request.args.get('num'))
    
    if currency == 'btc':
        top_buy, dataBuys = getPrices(buy_btc,'buy',markets,numElements)
        low_sell, dataSells = getPrices(sell_btc,'sell',markets,numElements)
    elif currency == 'eth':
        top_buy, dataBuys = getPrices(buy_eth,'buy',markets,numElements)
        low_sell, dataSells = getPrices(sell_eth,'sell',markets,numElements)

    top_buy_fmt = [i.replace('-',' $') for i in top_buy]
    low_sell_fmt = [i.replace('-',' $') for i in low_sell]

#    for market in markets:
#        i = random.randint(2,15)
#        fake = []
#        for j in range(i):
#            fake.append([random.random(),random.random()])
#        dataPlot[market] = sorted(fake, key=lambda x: x[0])
    print(top_buy)

    return jsonify(bids=top_buy_fmt, asks=low_sell_fmt, Buys=dataBuys, Sells=dataSells, product=currency.upper())
#data = {bids=[list of top bids for markets], asks=[list of lowest ask for markets], data={'market': [[price,amount],[p2,a2],...], ...} }

@app.route('/trades')
def trades():
    return render_template("trades.html", active='Trades', navbar=navbar, navlinks=navlinks)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
