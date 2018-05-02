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







class MIXIN_API:
    def __init__(self):
        self.appid = ""
        self.secret = ""
        self.sessionid = ""
        self.asset_pin = ""
        self.pin_token = ""
        self.private_key = ""
        self.keyForAES = ""

    def generateSig(self, method, uri, body):
        hashresult = hashlib.sha256(method + uri+body).hexdigest()
	#print("generate sha256 for sig" + " with: " + method + uri + body)
        #print(hashresult)
	return hashresult

    def genGETPOSTSig(self, methodstring, uristring, bodystring):
        jwtSig = self.generateSig(methodstring, uristring, bodystring)
        #print(methodstring + " sig:" + jwtSig)
        #print("method:" + methodstring)
        #print("uri   :" + uristring)
        #print("body  :" + bodystring)
        return jwtSig


    def genGETSig(self, uristring, bodystring):
        return self.genGETPOSTSig("GET", uristring, bodystring)

    def genPOSTSig(self, uristring, bodystring):
        return self.genGETPOSTSig("POST", uristring, bodystring)
    def genGETJwtToken(self, uristring, bodystring, jti):
        jwtSig = self.genGETSig(uristring, bodystring)
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
	encoded = jwt.encode({'uid':self.appid, 'sid':self.sessionid,'iat':iat,'exp': exp, 'jti':jti,'sig':jwtSig}, self.private_key, algorithm='RS512')
        #print("get jwt token with")
        #print("appid:" + self.appid)
        #print("sid  :" + self.sessionid)
        #print("iat  :" + str(iat))
        #print("exp  :" + str(exp))
        #print("jti  :" + jti)
        #print("sig  :" + jwtSig)
        #print("priv :" + self.private_key)
        #print("RS512")
        #print("====>" + encoded)
        return encoded

    def genGETListenSignedToken(self, uristring, bodystring, jti):
        jwtSig = self.genGETSig(uristring, bodystring)
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
	encoded = jwt.encode({'uid':self.appid, 'sid':self.sessionid,'iat':iat,'exp': exp, 'jti':jti,'sig':jwtSig}, self.private_key, algorithm='RS512')
        privKeyObj = RSA.importKey(self.private_key)
        signer = PKCS1_v1_5.new(privKeyObj)
        signature = signer.sign(encoded)
        return signature


    def genPOSTJwtToken(self, uristring, bodystring, jti):
        jwtSig = self.genPOSTSig(uristring, bodystring)
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
	encoded = jwt.encode({'uid':self.appid, 'sid':self.sessionid,'iat':iat,'exp': exp, 'jti':jti,'sig':jwtSig}, self.private_key, algorithm='RS512')
        return encoded

    def genEncrypedPin(self):
        if self.keyForAES == "":
            privKeyObj = RSA.importKey(self.private_key)
            decoded_result = base64.b64decode(self.pin_token)
            decoded_result_inhexString = ":".join("{:02x}".format(ord(c)) for c in decoded_result)
#        print("pin_token is:" + self.pin_token)
#        print("lenth of decoded pin_token is:" + str(len(decoded_result)))
            cipher = PKCS1_OAEP.new(key = privKeyObj, hashAlgo = Crypto.Hash.SHA256, label = self.sessionid)

            decrypted_msg = cipher.decrypt(decoded_result)
	    decrypted_msg_inhexString = ":".join("{:02x}".format(ord(c)) for c in decrypted_msg)
#        print("lenth of AES key:" + str(len(decrypted_msg)))
#        print("content of AES key:")
#        print(decrypted_msg_inhexString)
        
            self.keyForAES = decrypted_msg

        ts = int(time.time())
#        print("ts"+ str(ts))
        tszero = ts%0x100                                  
        tsone = (ts%0x10000) >> 8
        tstwo = (ts%0x1000000) >> 16
        tsthree = (ts%0x100000000) >> 24
        tsstring = chr(tszero) + chr(tsone) + chr(tstwo) + chr(tsthree) + '\0\0\0\0'
        counter = '\1\0\0\0\0\0\0\0'
        toEncryptContent = self.asset_pin + tsstring + tsstring
#        print("before padding:" + str(len(toEncryptContent)))
        lenOfToEncryptContent = len(toEncryptContent)
        toPadCount = 16 - lenOfToEncryptContent % 16
        if toPadCount > 0:
            paddedContent = toEncryptContent + chr(toPadCount) * toPadCount
        else:
            paddedContent = toEncryptContent
#        print("after padding:" + str(len(paddedContent)))

        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.keyForAES, AES.MODE_CBC, iv)
        encrypted_result = cipher.encrypt(paddedContent)
        msg = iv + encrypted_result
        encrypted_pin = base64.b64encode(msg)
#        print("to encrypted content in hex is :" + ":".join("{:02x}".format(ord(c)) for c in paddedContent))
#        print("iv in hex is " + ":".join("{:02x}".format(ord(c)) for c in iv))
#        print("iv + encrypted result in hex is :" + ":".join("{:02x}".format(ord(c)) for c in (iv + encrypted_result)))
#        print("iv + encrypted_result in base64 :" + encrypted_pin)

        return encrypted_pin



