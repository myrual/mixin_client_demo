# -*- coding: utf-8 -*-
import web
import json
import requests
import jwt
import datetime
import calendar
import hashlib
import base64
import Crypto
import time
import uuid
import random

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP


private_key = """-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQDG+84eobu6hfDYYr+hsTOFi9w0ska988FB009yDgWBmSQA3TNI
jl6QKZVuJ0TwPijUfzkc1af6dfvJ60J4REPHLdhUghg0oVgWOjrYlYadb7XIqzw4
a9R+NH66dHyXhVnoHxEM+2c7eUvam3vvj1UFQFx3iNPCxYganLtGarkffwIDAQAB
AoGAJmepU74xhoGdh5YfmGykHg1tdfpGrxjh3vuS5NeR9n6BNW18HW/lDnwILFeF
9bx5kvHvKwKNxkiJTWKL1LyQPAT9h78IkNlrW7ayLAwaasKg23UU8V+htf0WczAd
YWQ7woWU4ADbigximpmCtQCpuH7V6vvel72ny8QxYDGXOWECQQDt7e8fPBWjyHOp
uRivZi3prhDgf+pUIEYb4Sm5NEOa/wi+v76ZbZgg792rBGktq1Lt06d4vY2UpGr+
771cns9RAkEA1hilnNE8J6IcPSAfgFD9vYhVX0J6kNTKfLUeINlt7hiYeRTxP9d0
60Jdt/6btKW6AHpoCjngWFgXPTFO6OptzwJBAIj2dLZIQjS8CUjkUj911Gw2VWTG
fb/brEAUR45jdZ9dvE0B19g+bFpZegMeUOWHP//D3R32D/BHDYifvSP6D2ECQG2O
LzEP4LhnPAwLZBNFXpKeMRGN8yopuXQXOlOU76vm6h8LmGgS2MGKNGry3rqSE5wr
BxI0i5ipezrVAIwvagECQCHgwaDAobG5UpflHlzamTSu4OURVF1gomqSnpZp2AM9
r9fVfWzUIFLuXFM/1eM+MbZrDs9J1WHyaRHK+F/3WKs=
-----END RSA PRIVATE KEY-----"""


mixin_pin_token = """csEaHIh5RuVcXqcJ9aNp/AoubC/0L9ZtGWn037XREiR5JlbAvDW52obceJ9wWxVB12V9QxmabGmGR59wLoyfhfQeSVer56jOIUrOgL4ZXaMq32Rsddp2wpydEsCJbIjDftKwHJJvfz0XFAsNeBCTC+OfouaLW86Q50g3p7razbM="""

urls = (
    '/', 'index',
    '/auth','auth',
    '/CNB', 'balanceOfCNB',
    '/depositCNB','depositCNB'
)

mixin_client_id = "3c5fd587-5ac3-4fb6-b294-423ba3473f7d"
mixin_client_secret = "9cb0c7245bda18ca34b6e23bf2f194826b474907f8d898a92013e2c0dee8f977"
mixin_pay_pin = '515532'
mixin_pay_sessionid = '25083eb4-adab-49f3-9600-81d244b7cbc4'


class LUCKY:
    def init(self):
        self.counter = 0
    def increase(self):
        self.counter = self.counter + 1
    def isLucky(self):
        self.increase()
        if self.counter < 10:
            return True
        if self.counter > 20:
            self.reset()
            return False
        return False
    def reset(self):
        self.counter = 0

luckyinstanc = LUCKY()
luckyinstanc.init()

BLOCK_SIZE = 16  # Bytes
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * \
                chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
class MIXIN_API:
    def init(self):
        self.appid = ""
        self.secret = ""
        self.sessionid = ""
        self.asset_pin = ""
        self.pin_token = ""
        self.private_key = ""

    def generateSig(self, method, uri, body):
        hashresult = hashlib.sha256(method + uri+body).hexdigest()
	print("generate sha256 for sig" + " with: " + method + uri + body)
        print(hashresult)
	return hashresult

    def genGetSig(self, uristring, bodystring):
        jwtSig = self.generateSig("GET", uristring, bodystring)
        print("get sig:" + jwtSig)
        print("method:" + "get")
        print("uri   :" + uristring)
        print("body  :" + bodystring)
        return jwtSig

    def genPOSTSig(self, uristring, bodystring):
        jwtSig = self.generateSig("POST", uristring, bodystring)
        print("post sig:" + jwtSig)
        print("method:" + "post")
        print("uri   :" + uristring)
        print("body  :" + bodystring)

        return jwtSig

    def genGetJwtToken(self, uristring, bodystring):
        jwtSig = self.genGetSig(uristring, bodystring)
	encoded = jwt.encode({'uid':self.appid, 'sid':self.sessionid,'iat':datetime.datetime.utcnow(),'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=200), 'jti':mixin_client_id,'sig':jwtSig}, self.private_key, algorithm='RS512')
        return encoded

    def genPOSTJwtToken(self, uristring, bodystring, jti):
        jwtSig = self.genPOSTSig(uristring, bodystring)
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
	encoded = jwt.encode({'uid':self.appid, 'sid':self.sessionid,'iat':iat,'exp': exp, 'jti':jti,'sig':jwtSig}, self.private_key, algorithm='RS512')
        print("post jwt token with")
        print("appid:" + self.appid)
        print("sid  :" + self.sessionid)
        print("iat  :" + str(iat))
        print("exp  :" + str(exp))
        print("jti  :" + jti)
        print("sig  :" + jwtSig)
        print("priv :" + self.private_key)
        print("RS512")
        print("====>" + encoded)
        return encoded

    def genEncrypedPin(self):
        privKeyObj = RSA.importKey(self.private_key)
        decoded_result = base64.b64decode(self.pin_token)
        decoded_result_inhexString = ":".join("{:02x}".format(ord(c)) for c in decoded_result)
        print("pin_token is:" + self.pin_token)
        print("lenth of decoded pin_token is:" + str(len(decoded_result)))
        cipher = PKCS1_OAEP.new(key = privKeyObj, hashAlgo = Crypto.Hash.SHA256, label = self.sessionid)

        decrypted_msg = cipher.decrypt(decoded_result)
	decrypted_msg_inhexString = ":".join("{:02x}".format(ord(c)) for c in decrypted_msg)
        print("lenth of AES key:" + str(len(decrypted_msg)))
        print("content of AES key:")
        print(decrypted_msg_inhexString)
        
        keyForAES = decrypted_msg

        ts = int(time.time())
        print("ts"+ str(ts))
        tszero = ts%0x100                                  
        tsone = (ts%0x10000) >> 8
        tstwo = (ts%0x1000000) >> 16
        tsthree = (ts%0x100000000) >> 24
        tsstring = chr(tszero) + chr(tsone) + chr(tstwo) + chr(tsthree) + '\0\0\0\0'
        counter = '\1\0\0\0\0\0\0\0'
        toEncryptContent = self.asset_pin + tsstring + tsstring
        print("before padding:" + str(len(toEncryptContent)))
        lenOfToEncryptContent = len(toEncryptContent)
        toPadCount = 16 - lenOfToEncryptContent % 16
        if toPadCount > 0:
            paddedContent = toEncryptContent + chr(toPadCount) * toPadCount
        else:
            paddedContent = toEncryptContent
        print("after padding:" + str(len(paddedContent)))

        iv = Random.new().read(AES.block_size)
        cipher = AES.new(keyForAES, AES.MODE_CBC, iv)
        encrypted_result = cipher.encrypt(paddedContent)
        msg = iv + encrypted_result
        encrypted_pin = base64.b64encode(msg)
        print("to encrypted content in hex is :" + ":".join("{:02x}".format(ord(c)) for c in paddedContent))
        print("iv in hex is " + ":".join("{:02x}".format(ord(c)) for c in iv))
        print("iv + encrypted result in hex is :" + ":".join("{:02x}".format(ord(c)) for c in (iv + encrypted_result)))
        print("iv + encrypted_result in base64 :" + encrypted_pin)

        return encrypted_pin


class index:
    def GET(self):
        print(web.ctx.env)
        return "Hello, mixin world"

class balanceOfCNB:
    def GET(self):
        raise web.seeother('https://mixin.one/oauth/authorize?client_id=3c5fd587-5ac3-4fb6-b294-423ba3473f7d&scope=PROFILE:READ')
    def GETlistAsset(self):
        raise web.seeother('https://mixin.one/oauth/authorize?client_id=3c5fd587-5ac3-4fb6-b294-423ba3473f7d&scope=PROFILE:READ+ASSETS:READ')

class depositCNB:
    def GET(self):
        raise web.seeother('https://mixin.one/pay?recipient=3c5fd587-5ac3-4fb6-b294-423ba3473f7d&asset=965e5c6e-434c-3fa9-b780-c50f43cd955c&amount=5000&trace=' + str(uuid.uuid1()) + '&memo=TEXT')


class auth:
    def listAsset(self):
        mixindata = web.input()
	print(mixindata)
        r = requests.post('https://api.mixin.one/oauth/token', json = {"client_id": mixin_client_id, "code": mixindata.code,"client_secret": mixin_client_secret})
        result = r.json()
	print(result)
        access_token = result["data"]["access_token"]
        personinfo = requests.get('https://api.mixin.one/me', headers = {"Authorization":"Bearer " + access_token})
	userid = personinfo.json()["data"]["user_id"]
	print(personinfo.json())
        xin_asset_id = "c94ac88f-4671-3976-b60a-09064f1811e8"
        xin_asset_response = requests.get('https://api.mixin.one/assets/' + xin_asset_id, headers = {"Authorization":"Bearer " + access_token})
        print("check my mixin assets")
        xin_asset = xin_asset_response.json()
        cnb_asset_id = '965e5c6e-434c-3fa9-b780-c50f43cd955c'
        cnb_asset_response = requests.get('https://api.mixin.one/assets/' + cnb_asset_id, headers = {"Authorization":"Bearer " + access_token})
        if luckyinstanc.isLucky() == False:
            return "Shame on your luck"

	mixin_api_robot = MIXIN_API()
	mixin_api_robot.appid = mixin_client_id
        mixin_api_robot.secret = mixin_client_secret
        mixin_api_robot.sessionid = mixin_pay_sessionid
        mixin_api_robot.private_key = private_key
        mixin_api_robot.asset_pin = mixin_pay_pin
        mixin_api_robot.pin_token = mixin_pin_token
        encrypted_pin = mixin_api_robot.genEncrypedPin()

        bonus = str(random.randint(0,2345))
        body = {'asset_id': cnb_asset_id, 'counter_user_id':userid, 'amount':bonus, 'pin':encrypted_pin, 'trace_id':str(uuid.uuid1())}
        body_in_json = json.dumps(body)

        encoded = mixin_api_robot.genPOSTJwtToken('/transfers', body_in_json, mixin_client_id)
        r = requests.post('https://api.mixin.one/transfers', json = body, headers = {"Authorization":"Bearer " + encoded})
        print("post url with:https://api.mixin.one/transfers" + " with body:" + body_in_json + " with header:" + json.dumps({"Authorization":"Bearer " + encoded}))
	print(r.json())
        allassets = myasset.json()["data"]
        cnb_asset = cnb_asset_response.json()

        return "You got " + bonus + " CNB"

    def GET(self):
        mixindata = web.input()
	print(mixindata)
        r = requests.post('https://api.mixin.one/oauth/token', json = {"client_id": mixin_client_id, "code": mixindata.code,"client_secret": mixin_client_secret})
        result = r.json()
	print(result)
        access_token = result["data"]["access_token"]
        personinfo = requests.get('https://api.mixin.one/me', headers = {"Authorization":"Bearer " + access_token})
	userid = personinfo.json()["data"]["user_id"]
	print(personinfo.json())
        xin_asset_id = "c94ac88f-4671-3976-b60a-09064f1811e8"
        print("check my mixin assets")
        cnb_asset_id = '965e5c6e-434c-3fa9-b780-c50f43cd955c'
        if luckyinstanc.isLucky() == False:
            return "Shame on your luck"

	mixin_api_robot = MIXIN_API()
	mixin_api_robot.appid = mixin_client_id
        mixin_api_robot.secret = mixin_client_secret
        mixin_api_robot.sessionid = mixin_pay_sessionid
        mixin_api_robot.private_key = private_key
        mixin_api_robot.asset_pin = mixin_pay_pin
        mixin_api_robot.pin_token = mixin_pin_token
        encrypted_pin = mixin_api_robot.genEncrypedPin()

        bonus = str(random.randint(0,2345))
        body = {'asset_id': cnb_asset_id, 'counter_user_id':userid, 'amount':bonus, 'pin':encrypted_pin, 'trace_id':str(uuid.uuid1())}
        body_in_json = json.dumps(body)

        encoded = mixin_api_robot.genPOSTJwtToken('/transfers', body_in_json, mixin_client_id)
        r = requests.post('https://api.mixin.one/transfers', json = body, headers = {"Authorization":"Bearer " + encoded})
        print("post url with:https://api.mixin.one/transfers" + " with body:" + body_in_json + " with header:" + json.dumps({"Authorization":"Bearer " + encoded}))
	print(r.json())

        return "You got " + bonus + " CNB"

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
