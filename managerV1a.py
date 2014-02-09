import btcchina.btcChina as btcChina
import MtGox.MtGox as MtGox
import time,sched
from threading import Timer

#btc china
access_key=""
secret_key=""
#mtgox
mtgox_key = ''
mtgox_secret = ''
#bitStamp
bitStamp_key = ''
bitStamp_secret = ''
actionValue = 2

#bc = btcChina.client(access_key,secret_key)
#print bc.cancel(3977386)
#bc.cancelAll()
#bc.buy(6000,0.001)
#print bc.orders
#mtgox = MtGox.api(mtgox_key,mtgox_secret)
#print mtgox.request('money/ticker')
#bs_client_public = bitstamp.client.public()
#ticker = bs_client_public.ticker()
#bs_client_trading = bitstamp.client.trading('803858', bitStamp_key, bitStamp_secret)
#print account_balance

#a flag used to mark current currency, 0 money 1 bitcoin

def buy(bc,price):
	#calculeate moneyNum
	coinNum = bc.moneyNum()/price
	coinNum = float('%0.3f'%coinNum)
	if coinNum < 0.0005:
		print 'not enough money'
		return
	#cancel all padding process,get all coin avilable and sell all
	bc.cancelAll()
	order = bc.buy(price,coinNum-0.0005)
	if order != 'OK':
		Timer(60,bc.cancel,(order['id'],)).start()
	
def currentState(bc):
	#display current state, including total money total processing orders total coins etc
	info = bc.getInfo()
	money = float(info['balance']['cny']['amount'])
	coin = float(info['balance']['btc']['amount'])
	if info['frozen']['cny']['amount'] == None:
		frozenMoney = 0
	else:
		frozenMoney = float(info['frozen']['cny']['amount'])
	if info['frozen']['btc']['amount'] == None:
		frozenCoin = 0
	else:
		frozenCoin = float(info['frozen']['btc']['amount'])
	currentBid = float(bc.historyBid)
	totalMoney = (frozenCoin + coin)*currentBid + frozenMoney + money
	print ''
	print 'currentState'
	print 'total money: ' +str(totalMoney)
	print 'money: ' + str(money) + ' coin: ' + str(coin)
	#cal risk and benifits
	myPercent = str((totalMoney - bc.initMoney)/totalMoney*100)+'%'
	marketPercent = str((currentBid - bc.initBid)/currentBid*100) + '%'
	print 'initMoney: '+ str(bc.initMoney) + ' initBid: '+str(bc.initBid)
	print 'my risk: '+myPercent + ' market risk: ' + marketPercent
	print 'frozenMoney: ' + str(frozenMoney) +' frozenCoin: ' + str(frozenCoin)
	print 'currentOrder'
	print ''
	getCurrentOrder(bc)
	
def getCurrentOrder(bc):
	orders = bc.getOrder()['order']
	totalOrder = len(orders)
	for order in orders:
		if order['type'] == 'bid':
			amount = order['amount']
			price = order['price']
			print 'buy Coin ' + amount + ' in '+price
			print 'status: ' + order['status']
		if order['type'] == 'ask':
			amount = order['amount']
			price = order['price']
			print 'sell Coin ' + amount + ' in '+price
			print 'status: ' + order['status']
			print ''
	
def sell(bc,price):
	coinNum = bc.coinNum()
	if coinNum < 0.0005:
		print 'not enough coin'
		return
	coinNum = float('%0.4f'%coinNum)
	#cancel all padding process, get all money avilable and buy all
	bc.cancelAll()
	order = bc.sell(price,coinNum-0.0005)
	if order != 'OK':
		Timer(60,bc.cancel,(order['id'],)).start()


def makeDecision(bc):
	print 'begin decision'
	currentBid = bc.bid()
	#avgBid
	#bc.updateAvg(currentBid)
	#avgBid = bc.getAvgBid()
	#if avgBid == 'no':
		#print 'not enough data'
		#print 'data Num: ' + str(len(bc.historyBidList))
		#return
	print 'historyBid: ' +str(bc.historyBid) +' currentBid: '+str(currentBid)
	if currentBid -bc.historyBid > actionValue:
		print 'price incresed'
		print 'buy now'
		buy(bc,bc.ask())
	if bc.historyBid - currentBid >actionValue:
		print 'price decreased'
		print 'sell now'
		sell(bc,bc.bid())
	if currentBid - bc.historyBid <= actionValue and currentBid - bc.historyBid >= -actionValue:
		print 'no change'
		currentState(bc)
		return
	bc.historyBid = currentBid
	currentState(bc)
	print 'begin sleep'
	

if __name__ == "__main__":
	print 'initializating...'
	bc = btcChina.client(access_key,secret_key)
	count = 20
	while True:
		if count == 0:
			count = 20
			try:
				makeDecision(bc)
			except:
				bc = btcChina.client(access_key,secret_key)
		count -= 1
		print count
		time.sleep(1)
