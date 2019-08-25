本教程展示了一个机器人如何接入mixin网络，实现读取用户信息，给用户转账，给用户消息，转账。
本教程基于ubuntu 16.04 lts 64bit , python 2.7，[代码在此](https://github.com/myrual/mixin_client_demo)
有经验的程序员应该能够直接去github上搞定。

### 1. 需要一个linux vps
#### 1.1 在linode买一个vps，建议东京节点，快一点点
#### 1.2 做好安全防护措施
不用密码，而是使用密钥登陆
打开终端
```
ssh-copy-id root@45.79.215.97
```
然后尝试登陆vps，应该不会提示密码
```
ssh root@45.79.215.97
```
建立新用户
```
adduser appdev
```
把这个用户改成管理员权限，并且上传公钥
```
adduser appdev sudo
exit
ssh-copy-id appdev@45.79.215.97
ssh appdev@45.79.215.97
```
禁用密码登陆，首先把远程机器上的配置文件取下来。
```
scp root@45.79.215.97:/etc/ssh/sshd_config .
```
在本地用文本编辑器如记事本，打开sshd_config文件，如果找不到文件
```
open .
```
打开文件后，找到
```
PasswordAuthentication yes
```
把yes 改成no
改好的文件如下
```
# Package generated configuration file
# See the sshd_config(5) manpage for details

# What ports, IPs and protocols we listen for
Port 22
# Use these options to restrict which interfaces/protocols sshd will bind to
#ListenAddress ::
#ListenAddress 0.0.0.0
Protocol 2
# HostKeys for protocol version 2
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_dsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key
#Privilege Separation is turned on for security
UsePrivilegeSeparation yes

# Lifetime and size of ephemeral version 1 server key
KeyRegenerationInterval 3600
ServerKeyBits 1024

# Logging
SyslogFacility AUTH
LogLevel INFO

# Authentication:
LoginGraceTime 120
PermitRootLogin yes
StrictModes yes

RSAAuthentication yes
PubkeyAuthentication yes
#AuthorizedKeysFile	%h/.ssh/authorized_keys

# Don't read the user's ~/.rhosts and ~/.shosts files
IgnoreRhosts yes
# For this to work you will also need host keys in /etc/ssh_known_hosts
RhostsRSAAuthentication no
# similar for protocol version 2
HostbasedAuthentication no
# Uncomment if you don't trust ~/.ssh/known_hosts for RhostsRSAAuthentication
#IgnoreUserKnownHosts yes

# To enable empty passwords, change to yes (NOT RECOMMENDED)
PermitEmptyPasswords no

# Change to yes to enable challenge-response passwords (beware issues with
# some PAM modules and threads)
ChallengeResponseAuthentication no

# Change to no to disable tunnelled clear text passwords
PasswordAuthentication no

# Kerberos options
#KerberosAuthentication no
#KerberosGetAFSToken no
#KerberosOrLocalPasswd yes
#KerberosTicketCleanup yes

# GSSAPI options
#GSSAPIAuthentication no
#GSSAPICleanupCredentials yes

X11Forwarding yes
X11DisplayOffset 10
PrintMotd no
PrintLastLog yes
TCPKeepAlive yes
#UseLogin no

#MaxStartups 10:30:60
#Banner /etc/issue.net

# Allow client to pass locale environment variables
AcceptEnv LANG LC_*

Subsystem sftp /usr/lib/openssh/sftp-server

# Set this to 'yes' to enable PAM authentication, account processing,
# and session processing. If this is enabled, PAM authentication will
# be allowed through the ChallengeResponseAuthentication and
# PasswordAuthentication.  Depending on your PAM configuration,
# PAM authentication via ChallengeResponseAuthentication may bypass
# the setting of "PermitRootLogin without-password".
# If you just want the PAM account and session checks to run without
# PAM authentication, then enable this but set PasswordAuthentication
# and ChallengeResponseAuthentication to 'no'.
UsePAM yes

```
然后在终端里面
```
scp sshd_config  root@45.79.215.97:/etc/ssh
ssh root@45.79.215.97
sudo /etc/init.d/ssh restart
```
现在账户不能用密码登陆了，更安全了一丢丢，而且开始使用appdev作为管理员


#### 1.3 安装必要的系统更新和工具包
```
ssh appdev@45.79.215.97
sudo apt update
sudo apt upgrade
sudo apt install git
sudo apt install python-pip
```
 
### 2 代码下载和部署
#### 2.1 下载各种依赖库和代码
```
export LC_ALL=C
pip install web.py
pip install PyJWT
pip install websocket-client
pip install requests
pip install pycrypto
pip install cryptography
pip install pycrypto ecdsa

git clone https://github.com/myrual/mixin_client_demo.git
cd mixin_client_demo/
git checkout master

```

#### 2.2 申请账号，获取参数
##### 2.2.1 申请账号
访问 https://developers.mixin.one/dashboard ， 使用Mixin App的摄像头扫描二维码登陆。

填写注册App需要的信息，包括callback URL，目前图标暂时不是必选的。

注册成功 App 之后，你就拥有了一个mixinapp里面的一个机器人账户，目前是7000开头的那一段数字。

##### 2.2.2 获取参数
点击相应 App 的 “Click to generate a new session”，会出现三组数据：请牢记在心， 因为私钥部分不会再显示一次。

第一行的 6 位数字是 api接入 的提现/转账PIN 码，此处也是机器人的提现/转账密码

第二行的 UUID 是 session ID，

第三行是PIN_TOKEN， 

最后一部分 RSA PRIVATE KEY 是跟 API 进行交互时用来签名 JWT 的私钥。

#### 2.3 修改配置
```
scp appdev@45.79.215.9:/home/appdev/mixin_client_demo/mixin_config.py .
```
文件下载到本地，内容如下，按着dashboard的参数修改，然后上传

```
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

```
```
scp mixin_config.py appdev@45.79.215.9:/home/appdev/mixin_client_demo
```

```
python home_cnb.py
http://0.0.0.0:8080/
```
同时按下Ctrl和C键可以取消程序运行。

#### 2.4填写配置信息

点击dashboard里面的，appid，可以看到除了名字和icon以外还有 和The OAuth redirect uri.

The home uri 是指机器人的服务主页，此处我们填写 
```
45.79.215.9:8080
```
The OAuth redirect uri 是指用户在mixin app里面授权我们可以获取用户信息之后浏览器会访问的地址，此处填写 
```
45.79.215.9:8080/auth
```

现在重新回到linux 服务器上
```
nohup python home_cnb.py&
nuhup python home_of_cnb_robot.py&
```

现在机器人弄好了。可以尝试和机器人说话了。
mixin_config中的admin_uuid 是指开发者你，获取uuid的方法是在机器人聊天界面里面点+号，看见第二栏点击就能看到You are xxxxxxx，xxx是访问者的🆔
```
admin_uuid = "28ee416a-0eaa-4133-bc79-9676909b7e4e"
```