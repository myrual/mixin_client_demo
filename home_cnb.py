#!/usr/bin/env python
#coding: utf-8

import web
import json
import requests
import uuid
import mixin_config
import mixin_asset_list

urls = (
    '/', 'index',
    '/auth','auth',
    '/depositCNB','depositCNB',
)

class index:
    def GET(self):
        web.seeother('https://mixin.one/oauth/authorize?client_id='+mixin_config.mixin_client_id+'&scope=PROFILE:READ+PHONE:READ+ASSETS:READ')

class depositCNB:
    def GET(self):
        raise web.seeother('https://mixin.one/pay?recipient='+mixin_config.mixin_client_id+'&asset='+mixin_asset_list.CNB_ASSET_ID+'&amount=5000&trace=' + str(uuid.uuid1()) + '&memo=depositCNB')

class auth:
    def GET(self):
        mixindata = web.input(code = "no")
        if mixindata.code == "no":
            return "invalid code"

        r = requests.post('https://api.mixin.one/oauth/token', json = {"client_id": mixin_config.mixin_client_id, "code": mixindata.code, "client_secret": mixin_config.mixin_client_secret})
        result = r.json()
        print(result)
        if "data" not in result or "access_token" not in result["data"]:
            return "I don't know you, can not give your bonus"
        
        access_token = result["data"]["access_token"]
        personinfo = requests.get('https://api.mixin.one/me', headers = {"Authorization":"Bearer " + access_token})
        userid = personinfo.json()["data"]["user_id"]
        print(personinfo.json())
        return "You are " + userid

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
