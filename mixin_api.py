#!/usr/bin/env python
#coding: utf-8

from Crypto.PublicKey import RSA
import base64
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
import Crypto
import time
from Crypto import Random
from Crypto.Cipher import AES
import hashlib
import datetime
import jwt
import uuid
import requests
import json
import ssl

class MIXIN_API:
    def __init__(self):
        self.appid = ""
        self.secret = ""
        self.sessionid = ""
        self.asset_pin = ""
        self.pin_token = ""
        self.private_key = ""

    def __genSig(self, method, uri, body):
        hashresult = hashlib.sha256(method + uri + body).hexdigest()
        return hashresult

    def genGETSig(self, uristring, bodystring):
        return self.__genSig("GET", uristring, bodystring)

    def genPOSTSig(self, uristring, bodystring):
        return self.__genSig("POST", uristring, bodystring)

    def __genJwtToken(self, method, uristring, bodystring, jti):
        jwtSig = self.__genSig(method, uristring, bodystring)
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
        encoded = jwt.encode({'uid':self.appid, 'sid':self.sessionid,'iat':iat,'exp': exp, 'jti':jti,'sig':jwtSig}, self.private_key, algorithm='RS512')
        return encoded

    def genGETJwtToken(self, uristring, bodystring, jti):
        return self.__genJwtToken("GET", uristring, bodystring, jti)
     
    def genPOSTJwtToken(self, uristring, bodystring, jti):
        return self.__genJwtToken("POST", uristring, bodystring, jti)

    def genGETListenSignedToken(self, uristring, bodystring, jti):
        jwtSig = self.genGETSig(uristring, bodystring)
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
        encoded = jwt.encode({'uid':self.appid, 'sid':self.sessionid,'iat':iat,'exp': exp, 'jti':jti,'sig':jwtSig}, self.private_key, algorithm='RS512')
        privKeyObj = RSA.importKey(self.private_key)
        signer = PKCS1_v1_5.new(privKeyObj)
        signature = signer.sign(encoded)
        return signature

    def genEncrypedPin(self):
        privKeyObj = RSA.importKey(self.private_key)
        cipher = PKCS1_OAEP.new(key = privKeyObj, hashAlgo = Crypto.Hash.SHA256, label = self.sessionid)
        pinTokenObj = base64.b64decode(self.pin_token)
        keyForAES = cipher.decrypt(pinTokenObj)

        ts = int(time.time())
        tszero = ts%0x100                                  
        tsone = (ts%0x10000) >> 8
        tstwo = (ts%0x1000000) >> 16
        tsthree = (ts%0x100000000) >> 24
        tsstring = chr(tszero) + chr(tsone) + chr(tstwo) + chr(tsthree) + '\0\0\0\0'
        counter = '\1\0\0\0\0\0\0\0'
        toEncryptContent = self.asset_pin + tsstring + tsstring
        lenOfToEncryptContent = len(toEncryptContent)
        toPadCount = 16 - lenOfToEncryptContent % 16
        if toPadCount > 0:
            paddedContent = toEncryptContent + chr(toPadCount) * toPadCount
        else:
            paddedContent = toEncryptContent

        iv = Random.new().read(AES.block_size)
        cipher = AES.new(keyForAES, AES.MODE_CBC, iv)
        encrypted_result = cipher.encrypt(paddedContent)
        msg = iv + encrypted_result
        encrypted_pin = base64.b64encode(msg)
        return encrypted_pin

    def transferTo(self, to_user_id, to_asset_id, to_asset_amount, memo, trace_uuid=""):
        encrypted_pin = self.genEncrypedPin()
        body = {'asset_id': to_asset_id, 'counter_user_id':to_user_id, 'amount':str(to_asset_amount), 'pin':encrypted_pin, 'trace_id':trace_uuid, 'memo':memo}
        if trace_uuid == "":
            body['trace_id'] = str(uuid.uuid1())

        body_in_json = json.dumps(body)
        token = self.genPOSTJwtToken('/transfers', body_in_json, str(uuid.uuid4()))
        r = requests.post('https://api.mixin.one/transfers', json = body, headers = {"Authorization":"Bearer " + token})
        result_obj = r.json()
        print("transfer to:", to_user_id, result_obj)
        return result_obj

    def listAssets(self):
        token = self.genGETJwtToken('/assets', "", str(uuid.uuid4()))
        r = requests.get('https://api.mixin.one/assets', headers = {"Authorization":"Bearer " + token})
        if r.status_code != 200:
            print(r.status_code, r.text)
            r.raise_for_status()

        result_obj = r.json()
        assets_info = result_obj["data"]
        asset_list = []
        for singleAsset in assets_info:
            if singleAsset["balance"] != "0":
                asset_list.append((singleAsset["symbol"], singleAsset["balance"]))
        return asset_list