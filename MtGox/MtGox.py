import base64, hashlib, hmac, urllib2, time, urllib, json
base = 'https://data.mtgox.com/api/2/'


def post_request(key, secret, path, data):
    hmac_obj = hmac.new(secret, path + chr(0) + data, hashlib.sha512)
    hmac_sign = base64.b64encode(hmac_obj.digest())

    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'gox2 based client',
        'Rest-Key': key,
        'Rest-Sign': hmac_sign,
    }

    request = urllib2.Request(base + path, data, header)
    response = urllib2.urlopen(request, data)
    return json.load(response)


def gen_tonce():
    return str(int(time.time() * 1e6))


class api:

    def __init__(self, key, secret):
        self.key = key
        self.secret = base64.b64decode(secret)

    def request(self, path, params={}):
        params = dict(params)
        params['tonce'] = gen_tonce()
        data = urllib.urlencode(params)

        result = post_request(self.key, self.secret, path, data)
        if result['result'] == 'success':
            return result['data']
        else:
            raise Exception(result['result'])