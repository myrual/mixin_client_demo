# The open source code for Home of CNB bot in mixin app and mixin blockchain

There are many other language examples and SDK：

- NodeJS: https://github.com/virushuo/mixin-node
- Go: https://github.com/MixinMessenger/bot-api-go-client
- Java https://github.com/qige-one/mixin_java_sdk 

[Official development resource](http://developers.mixin.one)

community development resource：

- mixin_dev_resource: https://github.com/myrual/mixin_dev_resource
- MiXin_Player：https://github.com/albertschr/MiXin_Player


## install pip if it is missing in your OS
```
$ curl “https://bootstrap.pypa.io/get-pip.py" -o “get-pip.py”
$ python get-pip.py
```
### install python27 and pip on centos6.8
https://gist.github.com/dalegaspi/dec44117fa5e7597a559
```
yum install gcc
yum install gcc-c++
yum install python-devel
```
## pre request
```
pip2.7 install web.py
pip2.7 install PyJWT
pip2.7 install websocket-client
pip2.7 install requests
pip2.7 install pycrypto
pip2.7 install cryptography
pip2.7 install pycrypto ecdsa
```


## run robot 
```
python home_cnb_robot.py
```

## run robot as long as possible
```
nohup python home_cnb_robot.py &
```

## kill program
```
ls -ef
kill prociess id
```


[中文搭建教程](https://www.jianshu.com/p/727cca139a57)
