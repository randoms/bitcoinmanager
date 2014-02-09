import btcchina.btcChina as btcChina
import MtGox.MtGox as MtGox
import time,sched

#btc china
access_key="8d0a40db-c86d-41dc-8919-23b4942ad5fd"
secret_key="c60f15f0-9b62-469b-bd57-b652c985565c"
#mtgox
mtgox_key = '1f555377-079a-4341-b029-15deedd0652b'
mtgox_secret = 'l3ktuVtOySNkqxTu49HSAcVqqg7PjC2ZyK0Jx+QHFjtY/Jzv6LYndhqJecmc7IvC0PFtMN8pOd4VUGX5c/WLFw=='
#bitStamp
bitStamp_key = 'Ux0rlo7CKks7fmiv32YkuKPJ1qhEZDPd'
bitStamp_secret = '9wU0koZFIEqSmHDpUWQWY9WlOrnwAAeJ'



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
			print 'buy coin ' + amount + ' in '+price
			print 'status: ' + order['status']
		if order['type'] == 'ask':
			amount = order['amount']
			price = order['price']
			print 'buy coin ' + amount + ' in '+price
			print 'status: ' + order['status']

if __name__ == "__main__":
	print 'initializating...'
	bc = btcChina.client(access_key,secret_key)
	#bc.cancelAll()
	#print bc.getOrder()
	currentState(bc)
