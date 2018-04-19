# -*- coding: utf-8 -*-
import web
import json
import requests

urls = (
    '/', 'index',
    '/auth','auth'
)

mixin_client_id = "3c5fd587-5ac3-4fb6-b294-423ba3473f7d"
mixin_client_secret = "9cb0c7245bda18ca34b6e23bf2f194826b474907f8d898a92013e2c0dee8f977"
class index:
    def GET(self):
        print(web.ctx.env)
        return "Hello, mixin world"
class auth:
    def GET(self):
        mixindata = web.input()
	print(mixindata)
        r = requests.post('https://api.mixin.one/oauth/token', json = {"client_id": mixin_client_id, "code": mixindata.code,"client_secret": mixin_client_secret})
        result = r.json()
	print(result)
        access_token = result["data"]["access_token"]
        personinfo = requests.get('https://api.mixin.one/me', headers = {"Authorization":"Bearer " + access_token})
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
        print("check my cnb assets")
        cnb_asset = cnb_asset_response.json()

        return "Your cnb balance in mixin world is " + str(cnb_asset["data"]["balance"])

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
