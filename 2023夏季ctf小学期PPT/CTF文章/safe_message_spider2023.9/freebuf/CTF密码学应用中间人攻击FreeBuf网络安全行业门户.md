中间人攻击（Man-in-the-MiddleAttack，简称“MITM攻击”）是一种“间接”的入侵攻击，这种攻击模式是通过各种技术手段将受入侵者控制的一台计算机虚拟放置在网络连接中的两台通信计算机之间，这台计算机就称为“中间人”。

本次试验地址：https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182015011915514700001&pk_campaign=freebuf-wemedia。

看下实验描述实验主机在8002和8003端口上分别运行了两个服务，这两个服务互相进行通信，且通信内容会进行加密处理，请对这两个服务进行分析，并还原出被加密的flag字符串。提示：你需要充当中间人完成两个端口之间信息的相互转发工作。

来看实验操作，使用nc分别连接实验主机的8002和8003端口（如果服务未运行，请双击C:\Crypto\6\Bob.pyw以及C:\Crypto\6\Alice.pyw脚本），其中8002端口会返回信息“Let's
encrypt with
RSA!”，而8003端口则没有返回任何信息，根据题目所给的提示“你需要充当中间人完成两个端口之间信息的相互转发工作”，我们将8002返回的信息转发给8003端口，8003返回”OK”，然后把“OK”转发给8002端口，这样不断进行测试，如图所示：

![图片1.png](https://image.3001.net/images/20210413/1618302497_607556218d50262ac6cd7.png!small)

这感觉像RSA加密，我们先获取一下完整的消息内容编写一个Python脚本来完成流量转发的操作（位于实验主机的C:\Crypto\6\TraceLog.py）：

#!/usr/bin/env python

# -- coding:utf-8 --
import socket

if **name** == " **main** ":

s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s1.connect(("127.0.0.1", 8002))

s2.connect(("127.0.0.1", 8003))

while True:

data = s1.recv(65535)

if not data:

break

print "[8002] %s" % data

s2.sendall(data)

data = s2.recv(65535)

print "[8003] %s" % data

s1.sendall(data)

s1.close()

s2.close()

通过如下命令重定向将数据写入文件：TraceLog.py > log.txt

这个数据量很大，我们一个一个分析整个通信流程如下（[8002]表示8002端口发出的内容，[8003]表示8003端口发出的内容）：

[8002] Let's encrypt with RSA!

[8003] OK

[8002] My public key is {e1,n1}

[8003] My public key is {e2,n2}

8002

8003

双方在完成密钥交换之后，分别发送了一条经过RSA加密的消息。现在使用nc单独对8002端口进行测试，我们使用的测试公钥为{7,2449}，交互过程如下：

![图片2.png](https://image.3001.net/images/20210413/1618302498_607556224c3c15ef52c20.png!small)

提示2048位的RSA是安全，这里推测所给密钥长度不够，因此连接被关闭了。

这里是值得RSA算法里面的N值，使用PyCrypto库可以方便的生成2048位的RSA密钥，示例代码如下（位于实验主机的C:\Crypto\6\genKey.py）：

from Crypto.PublicKey import RSA

if **name** == " **main** ":

key = RSA.generate(2048)

print "e = %d" % key.e

print "e = %d" % key.d

print "n = %d" % key.p * key.q

运行结果如下图所示：

![图片3.png](https://image.3001.net/images/20210413/1618302499_6075562300604adf29e60.png!small)

先看一下中间人攻击模型在通信双方使用RSA对通信内容进行加密时，如果在交换密钥之前通信链路被劫持，那么就可以对其发起中间人攻击。假设Alice和Bob为正常的通信双方，Mallory为中间人，那么中间人攻击模型如下图所示：

![图片4.png](https://image.3001.net/images/20210413/1618302499_60755623b98f725f0a4e2.png!small)

中间人攻击的流程如下：

\1. Alice将自己的公钥发送给Bob；

\2. Alice的流量被Mallory截获，Mallory冒充Alice，并将自己的公钥发送给Bob；

\3. Bob收到Mallory的公钥，并将自己的公钥发给Mallory；

\4. Mallory冒充Bob，回复自己的公钥给Alice；

经过上面的步骤之后，Mallory分别与Alice和Bob建立了连接并完成RSA公钥的交换，因为Alice和Bob都使用了Mallory的公钥对消息进行了加密，因此，Mallory可以使用自己的私钥对消息进行解密还原出明文，达到监听通信内容的目的，甚至，Mallory可以对消息进行篡改，然后发送给对应的接收方。

也就是说他们直接发送了flag但是通过了RSA加密，我们要做的就是通过中间人把内容截取并且解密。

经过实验步骤一以及实验步骤二的分析，我们已经知道了通信双方的协议细节，以及知道通过中间人攻击可以窃听通信内容，中间人只要使用2048位的RSA密钥，即可完成通信内容的解密，攻击脚本的代码如下（位于实验主机的C:\Crypto\6\RSAMITM.py）：

#!/usr/bin/env python

# -- coding:utf-8 --
import socket

from Crypto.PublicKey import RSA

def splitkey(data):

e, n = data[18:len(data)-1].split(",")

return int(e), int(n)

def genkey():

key = RSA.generate(2048)

e = key.e

d = key.d

n = key.p * key.q

return e, d, n

def wrapkey(e, n):

return "My public key is {%d,%d}" % (e, n)

def RsaEncrypt(msg, e, n):

res = []

for ch in msg:

res.append(str(pow(ord(ch), e, n)))

return "[%s]" % (",".join(res))

def RsaDecrypt(msg, d, n):

msg = msg[1:len(msg)-1].split(",")

res = []

for ch in msg:

res.append(chr(pow(int(ch), d, n)))

return "".join(res)

def mitm():

s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s1.connect(("127.0.0.1", 8002))

s2.connect(("127.0.0.1", 8003))

# hello message

data1 = s1.recv(4096)

s2.sendall(data1)

data2 = s2.recv(4096)

s1.sendall(data2)

# key1

data1 = s1.recv(4096)

e1, n1 = splitkey(data1)

# MITM key

e, d, n = genkey()

publickey = wrapkey(e, n)

s2.sendall(publickey)

# key2

data2 = s2.recv(4096)

e2, n2 = splitkey(data2)

s1.sendall(publickey)

# decrypt flag1

data1 = s1.recv(40960)

flag1 = RsaDecrypt(data1, d, n)

data2 = RsaEncrypt(flag1, e2, n2)

s2.sendall(data2)

# decrypt flag2

data2 = s2.recv(40960)

flag2 = RsaDecrypt(data2, d, n)

data2 = RsaEncrypt(flag2, e1, n1)

# flag

print "[ FLAG ] %s%s" % (flag1, flag2)

if **name** == " **main** ":

mitm()

在命令行下运行脚本，等待一段时间后即可得到flag。

注意RSA加密和中间人攻击的流程，是解题关键。

