#!/usr/bin/env python
#coding: utf-8

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
import hashlib
import mixin_asset_list
import random
import datetime
import md5

try:
    import thread
except ImportError:
    import _thread as thread
import time

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from database_type import *

engine = create_engine('sqlite:///sqlalchemy_home_of_cnb.db')
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

mixin_api_robot = MIXIN_API()
mixin_api_robot.appid = mixin_config.mixin_client_id
mixin_api_robot.secret = mixin_config.mixin_client_secret
mixin_api_robot.sessionid = mixin_config.mixin_pay_sessionid
mixin_api_robot.private_key = mixin_config.private_key
mixin_api_robot.asset_pin = mixin_config.mixin_pay_pin
mixin_api_robot.pin_token = mixin_config.mixin_pin_token

freeBonusTimeTable = {}

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
    params = {"conversation_id": in_conversation_id,"recipient_id":to_user_id,"message_id":str(uuid.uuid4()),"category":"PLAIN_CONTACT","data":base64.b64encode(btnJson)}
    return writeMessage(websocketInstance, "CREATE_MESSAGE",params)

def sendUserText(websocketInstance, in_conversation_id, to_user_id, textContent):
    params = {"conversation_id": in_conversation_id,"recipient_id":to_user_id ,"message_id":str(uuid.uuid4()),"category":"PLAIN_TEXT","data":base64.b64encode(textContent)}
    return writeMessage(websocketInstance, "CREATE_MESSAGE",params)

def sendGroupText(websocketInstance, in_conversation_id, textContent):
    params = {"conversation_id": in_conversation_id,"message_id":str(uuid.uuid4()),"category":"PLAIN_TEXT","data":base64.b64encode(textContent)}
    return writeMessage(websocketInstance, "CREATE_MESSAGE",params)

def sendGroupPay(webSocketInstance, in_conversation_id, inAssetName, inAssetID, inPayAmount, linkColor = "#0CAAF5"):
    payLink = "https://mixin.one/pay?recipient=" + mixin_config.mixin_client_id + "&asset=" + inAssetID + "&amount=" + str(inPayAmount) + '&trace=' + str(uuid.uuid1()) + '&memo=PRS2CNB'
    btn = '[{"label":"' + inAssetName + '","action":"' + payLink + '","color":"' + linkColor + '"}]'
    gameEntranceParams = {"conversation_id": in_conversation_id,"message_id":str(uuid.uuid4()),"category":"APP_BUTTON_GROUP","data":base64.b64encode(btn)}
    writeMessage(webSocketInstance, "CREATE_MESSAGE",gameEntranceParams)
    return

def sendUserSticker(websocketInstance, in_conversation_id, to_user_id, album_id, sticker_name):
    realStickerObj = {}
    realStickerObj['album_id'] = album_id
    realStickerObj['name'] = sticker_name
    btnJson = json.dumps(realStickerObj)
    params = {"conversation_id": in_conversation_id,"recipient_id":to_user_id,"message_id":str(uuid.uuid4()),"category":"PLAIN_STICKER","data":base64.b64encode(btnJson)}
    return writeMessage(websocketInstance, "CREATE_MESSAGE",params)

def sendUserPayAppButton(webSocketInstance, in_conversation_id, to_user_id, inAssetName, inAssetID, inPayAmount, linkColor = "#0CAAF5"):
    payLink = "https://mixin.one/pay?recipient=" + mixin_config.mixin_client_id + "&asset=" + inAssetID + "&amount=" + str(inPayAmount) + '&trace=' + str(uuid.uuid1()) + '&memo=PRS2CNB'
    btn = '[{"label":"' + inAssetName + '","action":"' + payLink + '","color":"' + linkColor + '"}]'
    gameEntranceParams = {"conversation_id": in_conversation_id,"recipient_id":to_user_id,"message_id":str(uuid.uuid4()),"category":"APP_BUTTON_GROUP","data":base64.b64encode(btn)}
    writeMessage(webSocketInstance, "CREATE_MESSAGE",gameEntranceParams)

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

def buildConversationId(robot_id, user_id):
    n = md5.new()
    n.update(user_id)
    n.update(robot_id)
    result = n.digest()
    result_6 = chr((ord(result[6]) & 0x0f) | 0x30)
    result_8 = chr((ord(result[8]) & 0x3f) | 0x80)
    result_new = result[:6] + result_6 + result[7] + result_8 + result[9:]
    conver_id = uuid.UUID(bytes=result_new)
    return str(conver_id)

def recordFreeBonus(in_user_id):
    hashOfUserID = hashlib.sha256(in_user_id).hexdigest()
    thisFreshMan = session.query(Freshman).filter_by(userid = hashOfUserID).first()
    if thisFreshMan != None:
        thisFreshMan.bonusCounter = thisFreshMan.bonusCounter + 1
        session.commit()
    else:
        newFreshMan = Freshman()
        newFreshMan.userid = hashOfUserID
        newFreshMan.bonusCounter = 1
        session.add(newFreshMan)
        session.commit()

def notFreshMen(in_user_id):
    hashOfUserID = hashlib.sha256(in_user_id).hexdigest()
    thisFreshMan = session.query(Freshman).filter_by(userid = hashOfUserID).first()
    if thisFreshMan != None and thisFreshMan.bonusCounter > 20:
        return True
    return False

def on_message(ws, message):
    inbuffer = StringIO(message)
    f = gzip.GzipFile(mode="rb", fileobj=inbuffer)
    rdata_injson = f.read()
    rdata_obj = json.loads(rdata_injson)
    action = rdata_obj["action"]
    print("recv:", rdata_obj)

    if action not in ["ACKNOWLEDGE_MESSAGE_RECEIPT" ,"CREATE_MESSAGE", "LIST_PENDING_MESSAGES"]:
        print("unknow action")
        return
        
    if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
        return

    if action == "CREATE_MESSAGE":
        if 'error' in rdata_obj:
            msgid = rdata_obj["data"]["message_id"]
            replayMessage(ws, msgid)
            return

        data = rdata_obj["data"]
        msgid = data["message_id"]
        typeindata = data["type"]
        categoryindata = data["category"]
        userId = data["user_id"]
        conversationId = data["conversation_id"]
        dataindata = data["data"]
        # why?
        replayMessage(ws, msgid)

        if categoryindata not in ["SYSTEM_ACCOUNT_SNAPSHOT", "PLAIN_TEXT", "SYSTEM_CONVERSATION", "PLAIN_STICKER", "PLAIN_IMAGE", "PLAIN_CONTACT"]:
            print("unknow category")
            return

        if categoryindata == "PLAIN_IMAGE" or categoryindata == "SYSTEM_CONVERSATION":
            realData = base64.b64decode(dataindata)
            sysConversationObj = json.loads(realData)
            if sysConversationObj["action"] == "ADD":
                sendGroupText(ws, conversationId, "hello")

        if categoryindata == "SYSTEM_ACCOUNT_SNAPSHOT" and typeindata == "message":
            realData = base64.b64decode(dataindata)
            realAssetObj = json.loads(realData)
            counterUserId = realAssetObj["counter_user_id"]
            asset_amount = realAssetObj["amount"]
            #showReceipt(ws, conversationId, counterUserId, realAssetObj["snapshot_id"])
            if realAssetObj["asset_id"] == mixin_asset_list.CNB_ASSET_ID:
                if asset_amount == "1":
                    mixin_api_robot.transferTo(counterUserId, realAssetObj["asset_id"], "2", "pay 1 get 2")
                    return
            else:
                mixin_api_robot.transferTo(counterUserId, realAssetObj["asset_id"], asset_amount, "rollback")
                #sendUserText(ws, counterUserId, counterUserId, str(realAssetObj))
                return

        if categoryindata == "PLAIN_STICKER":
            typeindata = data["type"]
            categoryindata = data["category"]
            realStickerData = base64.b64decode(dataindata)
            realStickerObj = json.loads(realStickerData)
            sendUserText(ws, conversationId, userId, str(realStickerObj))

            if realStickerObj['album_id'] == "eb002790-ef9b-467d-93c6-6a1d63fa2bee":
                if realStickerObj['name'] == 'no_money':
                    sendUserAppButton(ws, conversationId, userId, "https://babelbank.io", u"数字资产抵押贷款了解一下？".encode('utf-8'))
                if realStickerObj['name'] in ['capital_predator', 'capital_cattle', 'capital_cat']:
                    now = datetime.datetime.now()
                    if notFreshMen(userId):
                        sendUserText(ws, conversationId, userId, u"新手期已过，没有奖励了".encode("utf-8"))
                        return

                    recordFreeBonus(userId)
                    if userId in freeBonusTimeTable:
                        oldtime = freeBonusTimeTable[userId]
                        if (now - oldtime).total_seconds() <  10 * 60:
                            sendUserText(ws, conversationId, userId, u"点钞机过热，冷却中".encode('utf-8'))
                            return

                    freeBonusTimeTable[userId] = now
                    sendUserText(ws, conversationId, userId, u"浑身掉钱的大佬就是很任性，10分钟以后继续尝试".encode('utf-8'))
                    bonus = str(random.randint(0,12345))
                    mixin_api_robot.transferTo(userId, mixin_asset_list.CNB_ASSET_ID, bonus,"you are rich")

        if categoryindata == "PLAIN_TEXT" and typeindata == "message":
            realData = base64.b64decode(dataindata)
            if '?' == realData or u'？'.encode('utf-8') == realData or 'help' == realData or 'Help' == realData or u'帮助'.encode('utf-8') == realData:
                introductionContent = u"CNB是数字货币社区行为艺术作品产生的token。由老社发行，zhuzi撰写白皮书，西乔设计logo，霍大佬广为宣传。本机器人代码 https://github.com/myrual/mixin_client_demo \n机器人可以理解区块链系列贴纸：向大鳄/大喵/大牛低头；买币是第一生产力；不玩了，不玩了，没钱了\n 输入 contact\sticker\link\paycnb\payeos\payprs 可获取各种例子".encode('utf-8')
                sendUserText(ws, conversationId, userId, introductionContent)
                return

            if 'sticker' == realData:
                # 买币是第一生产力
                sticker_blockchain_album_id = "eb002790-ef9b-467d-93c6-6a1d63fa2bee"
                sendUserSticker(ws, conversationId, userId, sticker_blockchain_album_id, 'productive')
                return

            if 'contact' == realData:
                #1054813
                my_uuid = "a9c754ff-1e26-4f81-bd20-955de8982cd6"
                sendUserContactCard(ws, conversationId, userId, my_uuid)
                return

            if 'link' == realData:
                sendUserAppButton(ws, conversationId, userId, "http://hxzqlh.com", u"了解下我?".encode('utf-8'))
                return

            if 'paycnb' == realData:
                sendUserPayAppButton(ws, conversationId, userId, u"付1CNB，得2CNB".encode('utf-8'),mixin_asset_list.CNB_ASSET_ID,  1, "#ff0033")
                return

            if 'payeos' == realData:
                sendUserPayAppButton(ws, conversationId, userId, u"付0.001EOS并闪电退款".encode('utf-8'),mixin_asset_list.EOS_ASSET_ID,  0.001, "#ff0033")
                return

            if 'payprs' == realData:
                sendUserPayAppButton(ws, conversationId, userId, u"付0.01PRS并闪电退款".encode('utf-8'),mixin_asset_list.PRS_ASSET_ID,  0.01, "#ff0033")
                return

            if 'friendsofju' == realData.lower() or 'friendsofxiaodong' == realData.lower() or 'friendsoflaoshe' == realData.lower() or 'friendsofzhuzi' == realData.lower():
                if notFreshMen(userId):
                    sendUserText(ws, conversationId, userId, u"新手期已过，没有奖励了".encode("utf-8"))
                    return

                recordFreeBonus(userId)
                now = datetime.datetime.now()
                if userId in freeBonusTimeTable:
                    oldtime = freeBonusTimeTable[userId]
                    if (now - oldtime).total_seconds() < 60 * 10:
                        sendUserText(ws, conversationId, userId, u"点钞机过热，冷却中".encode('utf-8'))
                        return

                freeBonusTimeTable[userId] = now
                sendUserText(ws, conversationId, userId, u"与大佬做朋友就是好，10分钟以后再来一发".encode('utf-8'))
                bonus = str(random.randint(0,100))
                mixin_api_robot.transferTo(userId, mixin_asset_list.CNB_ASSET_ID, bonus, "you are rich")

            if 'ye' == realData and userId == mixin_config.admin_uuid:
                for eachNonZeroAsset in mixin_api_robot.listAssets():
                    sendUserText(ws, conversationId, userId, str(eachNonZeroAsset))
                return

        elif categoryindata == "PLAIN_TEXT":
            print("PLAIN_TEXT but unkonw:")

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_data(ws, readableString, dataType, continueFlag):
    return

def on_open(ws):
    def run(*args):
        print("ws open")
        Message = {"id":str(uuid.uuid1()), "action":"LIST_PENDING_MESSAGES"}
        Message_instring = json.dumps(Message)
        fgz = StringIO()
        gzip_obj = gzip.GzipFile(mode='wb', fileobj=fgz)
        gzip_obj.write(Message_instring)
        gzip_obj.close()
        ws.send(fgz.getvalue(), opcode=websocket.ABNF.OPCODE_BINARY)
        while True:
            time.sleep(1)
    thread.start_new_thread(run, ())

if __name__ == "__main__":
    while True:
        encoded = mixin_api_robot.genGETJwtToken('/', "", str(uuid.uuid4()))
        #websocket.enableTrace(True)
        ws = websocket.WebSocketApp("wss://blaze.mixin.one/",
                on_message = on_message,
                on_error = on_error,
                on_close = on_close,
                header = ["Authorization:Bearer " + encoded],
                subprotocols = ["Mixin-Blaze-1"],
                on_data = on_data)
        ws.on_open = on_open
        ws.run_forever()
