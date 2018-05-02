# -*- coding: utf-8 -*-
import websocket
import requests
import json
import ssl
from mixin_api import MIXIN_API
import uuid
import zlib
import gzip
from cStringIO import StringIO
import base64
import mixin_config
import mixin_asset_list
import random
import datetime

try:
    import thread
except ImportError:
    import _thread as thread
import time
btccash_asset_id = "fd11b6e3-0b87-41f1-a41f-f0e9b49e5bf0"

admin_conversation_id = ""

mixin_api_robot = MIXIN_API()
mixin_api_robot.appid = mixin_config.mixin_client_id
mixin_api_robot.secret = mixin_config.mixin_client_secret
mixin_api_robot.sessionid = mixin_config.mixin_pay_sessionid
mixin_api_robot.private_key = mixin_config.private_key
mixin_api_robot.asset_pin = mixin_config.mixin_pay_pin
mixin_api_robot.pin_token = mixin_config.mixin_pin_token


freeBonusTimeTable = {}

def transferTo(robot, config, to_user_id, to_asset_id,to_asset_amount,memo):
    encrypted_pin = robot.genEncrypedPin()
    body = {'asset_id': to_asset_id, 'counter_user_id':to_user_id, 'amount':str(to_asset_amount), 'pin':encrypted_pin, 'trace_id':str(uuid.uuid1())}
    body_in_json = json.dumps(body)

    encoded = robot.genPOSTJwtToken('/transfers', body_in_json, config.mixin_client_id)
    r = requests.post('https://api.mixin.one/transfers', json = body, headers = {"Authorization":"Bearer " + encoded})
    result_obj = r.json()
    if 'error' in result_obj:
        error_body = result_obj['error']
        error_code = error_body['code']
        if error_code == 20119:
            print("to :" + to_user_id + " with asset:" + to_asset_id + " amount:" + to_asset_amount)
            print(result_obj)
        return False
    else:
        return True

def writeMessage(websocketInstance, action, params):
    Message = {"id":str(uuid.uuid1()), "action":action, "params":params}
    Message_instring = json.dumps(Message)
    fgz = StringIO()
    gzip_obj = gzip.GzipFile(mode='wb', fileobj=fgz)
    gzip_obj.write(Message_instring)
    gzip_obj.close()
    websocketInstance.send(fgz.getvalue(), opcode=websocket.ABNF.OPCODE_BINARY)


def sendUserAppButton(websocketInstance, in_conversation_id, to_user_id, realLink, text4Link, colorOfLink = "#d53120"):
    btn = '[{"label":"' + text4Link + '","action":"' + realLink + '","color":"' + colorOfLink + '"}]'
    params = {"conversation_id": in_conversation_id,"recipient_id":to_user_id,"message_id":str(uuid.uuid4()),"category":"APP_BUTTON_GROUP","data":base64.b64encode(btn)}
    return writeMessage(websocketInstance, "CREATE_MESSAGE",params)

def sendUserGameEntrance(webSocketInstance, in_config, in_conversation_id, to_user_id, inAssetName, inAssetID, inPayAmount, linkColor = "#0CAAF5"):
    payLink = "https://mixin.one/pay?recipient=" + in_config.mixin_client_id + "&asset=" + inAssetID + "&amount=" + str(inPayAmount) + '&trace=' + str(uuid.uuid1()) + '&memo=PRS2CNB'
    btn = '[{"label":"' + inAssetName + '","action":"' + payLink + '","color":"' + linkColor + '"}]'
    gameEntranceParams = {"conversation_id": in_conversation_id,"recipient_id":to_user_id,"message_id":str(uuid.uuid4()),"category":"APP_BUTTON_GROUP","data":base64.b64encode(btn)}
    writeMessage(webSocketInstance, "CREATE_MESSAGE",gameEntranceParams)
sendUserPayAppButton = sendUserGameEntrance

 
def showReceipt(websocketInstance, inConversationID, reply_user_id, reply_snapShotID):
    payLink = "https://mixin.one/snapshots/" + reply_snapShotID
    shortSnapShort = reply_snapShotID[0:13] + "..."
    btn = '[{"label":"Your receipt:' + shortSnapShort + '","action":"' + payLink + '","color":"#0CAAF5"}]'

    params = {"conversation_id": inConversationID,"recipient_id":reply_user_id,"message_id":str(uuid.uuid4()),"category":"APP_BUTTON_GROUP","data":base64.b64encode(btn)}
    writeMessage(websocketInstance, "CREATE_MESSAGE",params)

def replayMessage(websocketInstance, msgid):
    parameter4IncomingMsg = {"message_id":msgid, "status":"READ"}
    Message = {"id":str(uuid.uuid1()), "action":"ACKNOWLEDGE_MESSAGE_RECEIPT", "params":parameter4IncomingMsg}
    Message_instring = json.dumps(Message)
    fgz = StringIO()
    gzip_obj = gzip.GzipFile(mode='wb', fileobj=fgz)
    gzip_obj.write(Message_instring)
    gzip_obj.close()
    websocketInstance.send(fgz.getvalue(), opcode=websocket.ABNF.OPCODE_BINARY)



    return

def on_message(ws, message):
    global admin_conversation_id

    inbuffer = StringIO(message)
    f = gzip.GzipFile(mode="rb", fileobj=inbuffer)
    rdata_injson = f.read()
    rdata_obj = json.loads(rdata_injson)
    action = rdata_obj["action"]
    if action not in ["ACKNOWLEDGE_MESSAGE_RECEIPT" ,"CREATE_MESSAGE"]:
        print("unknow action")
        print(rdata_obj)
        return
    if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
        return
    if action == "CREATE_MESSAGE" and 'error' not in rdata_obj:
        msgid = rdata_obj["data"]["message_id"]
        data = rdata_obj["data"]
        typeindata = data["type"]
        categoryindata = data["category"]
        dataindata = data["data"]
        conversationid = data["conversation_id"]
        if data['user_id'] == mixin_config.admin_uuid:
            admin_conversation_id = data["conversation_id"]

        if categoryindata not in ["SYSTEM_ACCOUNT_SNAPSHOT", "PLAIN_TEXT", "SYSTEM_CONVERSATION", "PLAIN_STICKER","PLAIN_IMAGE" ]:
            print("unknow category")
            print(data)
            replayMessage(ws, msgid)
            return
        if categoryindata == "PLAIN_IMAGE" or categoryindata == "SYSTEM_CONVERSATION":
            replayMessage(ws, msgid)

        if categoryindata == "SYSTEM_ACCOUNT_SNAPSHOT" and typeindata == "message":

            replayMessage(ws, msgid)
            realData = base64.b64decode(dataindata)
            realAssetObj = json.loads(realData)
            userid = realAssetObj["counter_user_id"]
            asset_amount = realAssetObj["amount"]
            if realAssetObj["asset_id"] == mixin_asset_list.CNB_ASSET_ID:
                showReceipt(ws, conversationid, userid, realAssetObj["snapshot_id"])
        if categoryindata == "PLAIN_STICKER":
            ConversationId = data['conversation_id']
            realStickerData = base64.b64decode(dataindata)
            realStickerObj = json.loads(base64.b64decode(realStickerData))

            stickerData = base64.b64decode(dataindata)
            replayMessage(ws, msgid)
            if realStickerObj['album_id'] == "eb002790-ef9b-467d-93c6-6a1d63fa2bee":
                if realStickerObj['name'] == 'no_money':
                    sendUserAppButton(ws, ConversationId, data['user_id'], "https://babelbank.io", u"数字资产抵押贷款了解一下？".encode('utf-8'))
                if realStickerObj['name'] in ['capital_predator', 'capital_cattle', 'capital_cat']:
                    now = datetime.datetime.now()
                    if data['user_id'] in freeBonusTimeTable:
                        oldtime = freeBonusTimeTable[data['user_id']]
                        if (now - oldtime).total_seconds() < 60 * 5:
                            btn = u"发动机过热，冷却中".encode('utf-8')
	                    params = {"conversation_id": data['conversation_id'],"recipient_id":data['user_id'],"message_id":str(uuid.uuid4()),"category":"PLAIN_TEXT","data":base64.b64encode(btn)}
                            writeMessage(ws, "CREATE_MESSAGE",params)
                            return
                    freeBonusTimeTable[data['user_id']] = now
                    btn = u"High起来".encode('utf-8')
	            params = {"conversation_id": data['conversation_id'],"recipient_id":data['user_id'],"message_id":str(uuid.uuid4()),"category":"PLAIN_TEXT","data":base64.b64encode(btn)}
                    writeMessage(ws, "CREATE_MESSAGE",params)
                    bonus = str(random.randint(0,123456))
                    transferTo(mixin_api_robot, mixin_config, data['user_id'] , mixin_asset_list.CNB_ASSET_ID,bonus,"you are rich")

        if categoryindata == "PLAIN_TEXT" and typeindata == "message":
            replayMessage(ws, msgid)
            ConversationId = data['conversation_id']
            realData = base64.b64decode(dataindata)
            if '?' == realData or u'？'.encode('utf-8') == realData or 'help' == realData or 'Help' == realData or u'帮助'.encode('utf-8') == realData:
                btn = u"发送区块链系列贴纸有奇效：向大鳄/大喵/大牛低头；买币是第一生产力；不玩了，不玩了，没钱了".encode('utf-8')
	        params = {"conversation_id": data['conversation_id'],"recipient_id":data['user_id'],"message_id":str(uuid.uuid4()),"category":"PLAIN_TEXT","data":base64.b64encode(btn)}
                writeMessage(ws, "CREATE_MESSAGE",params)
                return
            if data['user_id'] == mixin_config.admin_uuid:
                btn = u"老板您来了".encode('utf-8')
	        params = {"conversation_id": data['conversation_id'],"recipient_id":data['user_id'],"message_id":str(uuid.uuid4()),"category":"PLAIN_TEXT","data":base64.b64encode(btn)}
                writeMessage(ws, "CREATE_MESSAGE",params)
                return
            btn = u"CNB由老社发行，zhuzi撰写白皮书巨量CNB请西乔设计logo，目前已成为最具收藏价值的空气币。本机器人代码 https://github.com/myrual/mixin_client_dem我可以理解区块链系列贴纸：向大鳄/大喵/大牛低头；买币是第一生产力；不玩了，不玩了，没钱了".encode('utf-8')
	    params = {"conversation_id": data['conversation_id'],"recipient_id":data['user_id'],"message_id":str(uuid.uuid4()),"category":"PLAIN_TEXT","data":base64.b64encode(btn)}
            writeMessage(ws, "CREATE_MESSAGE",params)
            return
           
        elif categoryindata == "PLAIN_TEXT":
            print("PLAIN_TEXT but unkonw:")
            print(rdata_obj)

SocketStatus = 0
def on_error(ws, error):
    SocketStatus = SocketStatus + 1
    print("error")
    print(error)

def on_close(ws):
    print("### closed ###")

def on_data(ws, readableString, dataType, continueFlag):
    return

def on_open(ws):


    def run(*args):
        print("run")
        Message = {"id":str(uuid.uuid1()), "action":"LIST_PENDING_MESSAGES"}
        Message_instring = json.dumps(Message)
        fgz = StringIO()
        gzip_obj = gzip.GzipFile(mode='wb', fileobj=fgz)
        gzip_obj.write(Message_instring)
        gzip_obj.close()

        ws.send(fgz.getvalue(), opcode=websocket.ABNF.OPCODE_BINARY)
        while True:
            a = 1
            time.sleep(10)
    thread.start_new_thread(run, ())


if __name__ == "__main__":

    if SocketStatus == 0:
        while True:
            encoded = mixin_api_robot.genGETJwtToken('/', "", str(uuid.uuid4()))
            websocket.enableTrace(False)
            ws = websocket.WebSocketApp("wss://blaze.mixin.one/",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                              header = ["Authorization:Bearer " + encoded],
                              subprotocols = ["Mixin-Blaze-1"],
                              on_data = on_data)
            ws.on_open = on_open
            ws.run_forever()
    print("run")
            btn = u"CNB是无投资价值的空气币，请勿购买。CNB由老社发行，zhuzi撰写白皮书并出巨量CNB请西乔设计logo。本机器人代码 https://github.com/myrual/mixin_client_dem我可以理解区块链系列贴纸：向大鳄/大喵/大牛低头；买币是第一生产力；不玩了，不玩了，没钱了".encode('utf-8')
