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

def sendUserContactCard(websocketInstance, in_conversation_id, to_user_id, to_share_userid):
    btnJson = json.dumps({"user_id":to_share_userid})
    params = {"conversation_id": in_conversation_id,"recipient_id":to_user_id,"message_id":str(uuid.uuid4()),"category":"PLAIN_CONTACT","data":base64.b64encode(base64.b64encode(btnJson))}
    return writeMessage(websocketInstance, "CREATE_MESSAGE",params)

def sendUserText(websocketInstance, in_conversation_id, to_user_id, textContent):
    params = {"conversation_id": in_conversation_id,"recipient_id":to_user_id ,"message_id":str(uuid.uuid4()),"category":"PLAIN_TEXT","data":base64.b64encode(textContent)}
    return writeMessage(websocketInstance, "CREATE_MESSAGE",params)


def sendUserSticker(websocketInstance, in_conversation_id, to_user_id, album_id, sticker_name):
    realStickerObj = {}
    realStickerObj['album_id'] = album_id
    realStickerObj['name'] = sticker_name

    btnJson = json.dumps(realStickerObj)
    params = {"conversation_id": in_conversation_id,"recipient_id":to_user_id,"message_id":str(uuid.uuid4()),"category":"PLAIN_STICKER","data":base64.b64encode(base64.b64encode(btnJson))}
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
def listAssets(robot, config):
    encoded = robot.genGETJwtToken('/assets', "", config.mixin_client_id)
    r = requests.get('https://api.mixin.one/assets', headers = {"Authorization":"Bearer " + encoded, "Mixin-Device-Id":config.admin_uuid})
    print(r.status_code)
    if r.status_code != 200:
        error_body = result_obj['error']
        print(error_body)

    r.raise_for_status()

    result_obj = r.json()
    print(result_obj)
    assets_info = result_obj["data"]
    asset_list = []
    for singleAsset in assets_info:
        if singleAsset["balance"] != "0":
            asset_list.append((singleAsset["symbol"], singleAsset["balance"]))
    return asset_list


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
                    btn = u"浑身掉钱的大佬就是很任性".encode('utf-8')
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
                for eachNonZeroAsset in listAssets(mixin_api_robot, mixin_config):
                    sendUserText(ws, data['conversation_id'], data['user_id'], str(eachNonZeroAsset))


            sendUserText(ws, data['conversation_id'], data['user_id'], "-----文本消息 example-----")
            introductionContent = u"CNB是数字货币社区行为艺术作品产生的token。由老社发行，zhuzi撰写白皮书，西乔设计logo，霍大佬广为宣传。本机器人代码 https://github.com/myrual/mixin_client_demo \n机器人可以理解区块链系列贴纸：向大鳄/大喵/大牛低头；不玩了，不玩了，没钱了".encode('utf-8')
            sendUserText(ws, data['conversation_id'], data['user_id'], introductionContent)


            sendUserText(ws, data['conversation_id'], data['user_id'], "-----Sticker example-----")
            sticker_blockchain_album_id = "eb002790-ef9b-467d-93c6-6a1d63fa2bee"
            sendUserSticker(ws, data['conversation_id'], data['user_id'], sticker_blockchain_album_id, 'productive')

            sendUserText(ws, data['conversation_id'], data['user_id'], "-----名片 example 老社和zhuzi-----")
            laoshe_user_id_in_contact_card_in_uuid_format = "99cf45c4-a64b-4aa1-8f9b-40c3e21d6468"
            zhuzi_user_id_in_contact_card_in_uuid_format = "b4450d4c-9218-4d30-995f-83e14b29e9ad"

            sendUserContactCard(ws, data['conversation_id'], data['user_id'],laoshe_user_id_in_contact_card_in_uuid_format)
            sendUserContactCard(ws, data['conversation_id'], data['user_id'],zhuzi_user_id_in_contact_card_in_uuid_format)

            sendUserText(ws, data['conversation_id'], data['user_id'], "-----链接按钮 example-----")
            sendUserAppButton(ws, ConversationId, data['user_id'], "http://dapai.one:8080", u"了解我的user id".encode('utf-8'))

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
    while True:

        encoded = mixin_api_robot.genGETJwtToken('/', "", str(uuid.uuid4()))
        websocket.enableTrace(True)
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
            
