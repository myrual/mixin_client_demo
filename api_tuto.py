# -*- coding: utf-8 -*-
import web
import json
import requests
import jwt
import datetime
import calendar
import hashlib
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Cipher import AES
from Crypto import Random


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
    '/CNB', 'balanceOfCNB'
)

mixin_client_id = "3c5fd587-5ac3-4fb6-b294-423ba3473f7d"
mixin_client_secret = "9cb0c7245bda18ca34b6e23bf2f194826b474907f8d898a92013e2c0dee8f977"
mixin_pay_pin = '515532'
mixin_pay_sessionid = '25083eb4-adab-49f3-9600-81d244b7cbc4'


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
        decoded_result = base64.b64decode(self.pin_token)
        print("pin_token is:" + self.pin_token)
        print("decoded content of encrypted pin_token is:")
        print(decoded_result)
        return self.pin_token


class index:
    def GET(self):
        print(web.ctx.env)
        return "Hello, mixin world"

class balanceOfCNB:
    def GET(self):
        raise web.seeother('https://mixin.one/oauth/authorize?client_id=3c5fd587-5ac3-4fb6-b294-423ba3473f7d&scope=PROFILE:READ+ASSETS:READ')

class auth:
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
        myasset = requests.get('https://api.mixin.one/assets', headers = {"Authorization":"Bearer " + access_token})
        allassets = myasset.json()["data"]
        for each in allassets:
            print("----asset----:")
            try:
                print(each["name"])
                print(each["symbol"])
            except UnicodeEncodeError:
                print "it was not a ascii-encoded unicode string"
                continue
            else:
                print("asset_id:" + each["asset_id"])
                print("public_key:" + each["public_key"])
                print("chain_id:" + each["chain_id"])

        xin_asset_id = "c94ac88f-4671-3976-b60a-09064f1811e8"
        xin_asset_response = requests.get('https://api.mixin.one/assets/' + xin_asset_id, headers = {"Authorization":"Bearer " + access_token})
        print("check my mixin assets")
        xin_asset = xin_asset_response.json()
        cnb_asset_id = '965e5c6e-434c-3fa9-b780-c50f43cd955c'
        cnb_asset_response = requests.get('https://api.mixin.one/assets/' + cnb_asset_id, headers = {"Authorization":"Bearer " + access_token})

	mixin_api_robot = MIXIN_API()
	mixin_api_robot.appid = mixin_client_id
        mixin_api_robot.secret = mixin_client_secret
        mixin_api_robot.sessionid = mixin_pay_sessionid
        mixin_api_robot.private_key = private_key
        mixin_api_robot.asset_pin = mixin_pay_pin
        mixin_api_robot.pin_token = mixin_pin_token
        encrypted_pin = mixin_api_robot.genEncrypedPin()

        body = {'asset_id': cnb_asset_id, 'counter_user_id':userid, 'amount':'123', 'pin':'12345', 'trace_id':'965e5c6e-434c-3fa9-b780-c50f43cd955c'}
        body_in_json = json.dumps(body)
        
        sig = mixin_api_robot.genGetSig("users", body_in_json)
        print("sig")
        print(sig)

        encoded = mixin_api_robot.genPOSTJwtToken('/transfers', body_in_json, mixin_client_id)
        r = requests.post('https://api.mixin.one/transfers', json = body, headers = {"Authorization":"Bearer " + encoded})
	print(r.json())
        allassets = myasset.json()["data"]
        print("check my cnb assets")
        cnb_asset = cnb_asset_response.json()

        return userid + "Your cnb balance in mixin world is " + str(cnb_asset["data"]["balance"])

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
