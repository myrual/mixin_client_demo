mixin_client_id = "3c5fd587-5ac3-4fb6-b294-423ba3473f7d"
mixin_client_secret = "9cb0c7245bda18ca34b6e23bf2f194826b474907f8d898a92013e2c0dee8f977"
mixin_pay_pin = '515532'
mixin_pay_sessionid = '25083eb4-adab-49f3-9600-81d244b7cbc4'

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
admin_uuid = "28ee416a-0eaa-4133-bc79-9676909b7b4e"
class user_mixin_config:
    def __init__(self):
        self.mixin_client_id = ""
        self.mixin_pay_sessionid= ""
        self.mixin_pin_token= ""
        self.mixin_pay_pin = ""
        self.private_key = ""
        self.deviceID = ""
        self.keyForAES = ""
        self.asset_pin = ""
 
