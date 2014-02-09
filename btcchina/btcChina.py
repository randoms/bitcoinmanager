
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import re
import hmac
import hashlib
import base64
import httplib
import json
 
 
historyNum = 10

class api():
    def __init__(self,access=None,secret=None):
        self.access_key=access
        self.secret_key=secret
        self.conn=httplib.HTTPSConnection("api.btcchina.com")
 
    def _get_tonce(self):
        return int(time.time()*1000000)
 
    def _get_params_hash(self,pdict):
        pstring=""
        # The order of params is critical for calculating a correct hash
        fields=['tonce','accesskey','requestmethod','id','method','params']
        for f in fields:
            if pdict[f]:
                if f == 'params':
                    # Convert list to string, then strip brackets and spaces
                    # probably a cleaner way to do this
                    param_string=re.sub("[\[\] ]","",str(pdict[f]))
                    param_string=re.sub("'",'',param_string)
                    pstring+=f+'='+param_string+'&'
                else:
                    pstring+=f+'='+str(pdict[f])+'&'
            else:
                pstring+=f+'=&'
        pstring=pstring.strip('&')
 
        # now with correctly ordered param string, calculate hash
        phash = hmac.new(self.secret_key, pstring, hashlib.sha1).hexdigest()
        return phash
 
    def _private_request(self,post_data):
        #fill in common post_data parameters
        tonce=self._get_tonce()
        post_data['tonce']=tonce
        post_data['accesskey']=self.access_key
        post_data['requestmethod']='post'
 
        # If ID is not passed as a key of post_data, just use tonce
        if not 'id' in post_data:
            post_data['id']=tonce
 
        pd_hash=self._get_params_hash(post_data)
 
        # must use b64 encode        
        auth_string='Basic '+base64.b64encode(self.access_key+':'+pd_hash)
        headers={'Authorization':auth_string,'Json-Rpc-Tonce':tonce}
 
        #post_data dictionary passed as JSON        
        self.conn.request("POST",'/api_trade_v1.php',json.dumps(post_data),headers)
        response = self.conn.getresponse()
 
        # check response code, ID, and existence of 'result' or 'error'
        # before passing a dict of results
        if response.status == 200:
            # this might fail if non-json data is returned
            resp_dict = json.loads(response.read())
 
            # The id's may need to be used by the calling application,
            # but for now, check and discard from the return dict
            if str(resp_dict['id']) == str(post_data['id']):
                if 'result' in resp_dict:
                    return resp_dict['result']
                elif 'error' in resp_dict:
                    return resp_dict['error']
        else:
            # not great error handling....
            print "status:",response.status
            print "reason:".response.reason
 
        return None
 
    def get_account_info(self,post_data={}):
        post_data['method']='getAccountInfo'
        post_data['params']=[]
        return self._private_request(post_data)
 
    def get_market_depth(self,post_data={}):
        post_data['method']='getMarketDepth2'
        post_data['params']=[]
        return self._private_request(post_data)
 
    def buy(self,price,amount,post_data={}):
        post_data['method']='buyOrder'
        post_data['params']=[price,amount]
        return self._private_request(post_data)
 
    def sell(self,price,amount,post_data={}):
        post_data['method']='sellOrder'
        post_data['params']=[price,amount]
        return self._private_request(post_data)
 
    def cancel(self,order_id,post_data={}):
        post_data['method']='cancelOrder'
        post_data['params']=[order_id]
        return self._private_request(post_data)
 
    def request_withdrawal(self,currency,amount,post_data={}):
        post_data['method']='requestWithdrawal'
        post_data['params']=[currency,amount]
        return self._private_request(post_data)
 
    def get_deposits(self,currency='BTC',pending=True,post_data={}):
        post_data['method']='getDeposits'
        if pending:
            post_data['params']=[currency]
        else:
            post_data['params']=[currency,'false']
        return self._private_request(post_data)
 
    def get_orders(self,id=None,open_only=True,post_data={}):
        # this combines getOrder and getOrders
        if id is None:
            post_data['method']='getOrders'
            if open_only:
                post_data['params']=[]
            else:
                post_data['params']=['false']
        else:
            post_data['method']='getOrder'
            post_data['params']=[id]
        return self._private_request(post_data)
 
    def get_withdrawals(self,id='BTC',pending=True,post_data={}):
        # this combines getWithdrawal and getWithdrawls
        try:
            id = int(id)
            post_data['method']='getWithdrawal'
            post_data['params']=[id]
        except:
            post_data['method']='getWithdrawals'
            if pending:
                post_data['params']=[id]
            else:
                post_data['params']=[id,'false']
        return self._private_request(post_data)

class client:
	historyBid = 0
	money = 0
	coin = 0
	def __init__(self,access=None,secret=None):
		self.conn=httplib.HTTPSConnection("api.btcchina.com")
		self.api = api(access,secret)
		#cancel all orders
		self.orders = self.api.get_orders()['order']
		self.cancelAll()
		self.money = float(self.moneyNum())
		self.coin = float(self.coinNum())
		self.moneyFlag = 0
		client.historyBid = self.bid()
		self.initBid = client.historyBid
		self.initMoney = self.money + self.coin*self.initBid
		self.historyBidList = []
		
	def bid(self):
		'''
			get the lowest sell money
		'''
		marketData = self.api.get_market_depth()
		return float(marketData['market_depth']['ask'][0]['price'])
	def ask(self):
		'''
			get the highest buy money
		'''
		marketData = self.api.get_market_depth()
		return float(marketData['market_depth']['bid'][0]['price'])
	
	def moneyNum(self):
		info = self.api.get_account_info()
		if info['balance']['cny']['amount'] != None:
			return float(info['balance']['cny']['amount'])
		else:
			return 0
	def coinNum(self):
		info = self.api.get_account_info()
		if info['balance']['cny']['amount'] != None:
			return float(info['balance']['btc']['amount'])
		else:
			return 0
	def sell(self,price,amount):
		#check coin
		print str(price) +'  '+ str(amount)
		res = self.api.sell(str(price),str(amount))
		if res == True:
			#get order id
			orders = self.api.get_orders()['order']
			if len(orders) == 0:
				print 'sell success'
				return 'OK'
			new_order = sorted(orders,key=lambda time:int(-time['date']))[0]
			self.orders = orders
			return new_order
		else:
			print 'price: '+ str(price)
			print 'amount: '+ str(amount)
			print res
			raise ValueError('sell coin failed')
	def buy(self,price,amount):
		#check money 
		print str(price) +'  '+ str(amount)
		res = self.api.buy(str(price),str(amount))
		if res == True:
			#get order id
			orders = self.api.get_orders()['order']
			if len(orders) == 0:
				print 'buy success'
				return 'OK'
			new_order = sorted(orders,key=lambda time:int(-time['date']))[0]
			self.orders = orders
			return new_order
		else:
			print 'price: '+ str(price)
			print 'amount: '+ str(amount)
			print res
			raise ValueError('buy coin failed!')
	def cancel(self,id):
		#check order exsist
		print id
		order = self.getOrder(id)
		if order['order']['status'] == 'open':
			self.api.cancel(id)
			print 'order canceled!'
			return
		print 'order already canceled'
	
	def cancelAll(self):
		for order in self.orders:
			res = self.cancel(order['id'])
	def getOrder(self,id=None):
		return self.api.get_orders(id)
	def getInfo(self):
		return self.api.get_account_info()
	def getAvgBid(self):
		if len(self.historyBidList) < historyNum:
			return 'no'
		total = 0
		for bid in self.historyBidList:
			total += bid
		return total/historyNum
	def updateAvg(self,currentBid):
		if len(self.historyBidList) < historyNum:
			self.historyBidList.append(currentBid)
		else:
			self.historyBidList.pop(0)
			self.historyBidList.append(currentBid)
			total = 0
			for bid in self.historyBidList:
				total += bid
			return total/historyNum