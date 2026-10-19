## 一、背景

腾讯安全威胁情报中心研究人员在日常巡检中发现，有攻击者利用Apache
Solr远程代码执行漏洞（CVE-2019-0193）对某客户进行攻击，由于客户部署的腾讯云防火墙已对该类型攻击进行识别并设置为“阻断”，该攻击未对客户资产造成损失。

![](https://image.3001.net/images/20200928/1601256788_5f713d54d7a168487c17f.png!small)

进一步分析后发现，此次攻击属于BuleHero挖矿蠕虫病毒，且该变种版本新增了SMBGhost（CVE-2020-0796）漏洞利用代码。

该团伙擅长利用各类Web服务器组件漏洞进行攻击，包括：Tomcat任意文件上传漏洞、Apache
Struts2远程代码执行漏洞、Weblogic反序列化漏洞、Drupal远程代码执行漏洞、Apache Solr
远程命令执行漏洞、PHPStudy后门利用均在其武器列表中。此外还会利用永恒之蓝漏洞、$IPC和MSSQL弱口令爆破等等攻击手法，攻击成功后，会在目标机器植入门罗币挖矿木马和远控木马。

## 二、详细分析

腾讯云防火墙捕获到利用Apache
Solr远程代码执行漏洞（CVE-2019-0193）攻击流量，该攻击Payload利用certutil.exe命令下载http[:]//UeR.ReiyKiQ.ir/download.exe执行。

![](https://image.3001.net/images/20200928/1601256825_5f713d793f6873a4af315.png!small)

2019年08月01日Apache官方发布Apache Solr远程代码执行漏洞（CVE-2019-0193）安全通告，Apache Solr
DataImport功能在开启Debug模式时，可以接收来自请求的"dataConfig"参数，在dataConfig参数中可以包含script恶意脚本导致远程代码执行。官方通告如下：https://issues.apache.org/jira/browse/SOLR-13669

腾讯云防火墙对该漏洞利用及时进行阻断，客户服务器资产未遭受损失。

![](https://image.3001.net/images/20200928/1601256842_5f713d8ae52e9b10f4d31.png!small)

  

腾讯安全研究人员对Payload进行分析后，确认该攻击事件属于BuleHero挖矿蠕虫病毒，此次变种新增了SMBGhost（CVE-2020-0796）漏洞利用代码。

download.exe下载木马http[:]//UeR.ReiyKiQ.ir/SesnorDateService.exe。

![](https://image.3001.net/images/20200928/1601256852_5f713d94dec07fc6df636.png!small)

SesnorDateService.exe在Windows目录下创建文件

C:\Windows\<random>\EventisCache\divsfrsHost.exe，并释放SMBGhost漏洞攻击程序divsfrsHost.exe。

![](https://image.3001.net/images/20200928/1601256863_5f713d9f705b70c6205ba.png!small)

漏洞攻击代码采用开源程序

<https://github.com/chompie1337/SMBGhost_RCE_PoC/blob/master/exploit.py>

生成，并利用Pyinstaller打包生成exe可执行程序。

![](https://image.3001.net/images/20200928/1601256873_5f713da9786f88f276369.png!small)

此外SesnorDateService.exe还利用其他多个Web应用漏洞进行攻击：

Apache Struts2漏洞【CVE-2017-5638】  
WebLogic 漏洞【CVE-2018-2628】  
WebLogic 漏洞【CVE-2017-10271】  
Thinkphp5漏洞【CNVD-2018-24942】  
Tomcat漏洞【CVE-2017-12615】  
Drupal漏洞【CVE-2018-7600】

![](https://image.3001.net/images/20200928/1601256883_5f713db375c172efaf71f.png!small)

通过内置的账号密码字典对MSSQL进行远程爆破攻击。

![](https://image.3001.net/images/20200928/1601256893_5f713dbd2427abf4f0490.png!small)

通过内置的账号密码字典对IPC$进行远程爆破攻击。

![](https://image.3001.net/images/20200928/1601256905_5f713dc9d3059e86add64.png!small)

利用永恒之蓝漏洞攻击。

![](https://image.3001.net/images/20200928/1601256915_5f713dd38bcda6adc6eff.png!small)

检测phpStudy后门。

![](https://image.3001.net/images/20200928/1601256934_5f713de65e0a96a33f763.png!small)

释放XMRig挖矿木马挖矿门罗币。

![](https://image.3001.net/images/20200928/1601256944_5f713df0e4adbabe0958a.png!small)

释放远控木马Hentai.exe拷贝自身至系统system32目录下命名为随机名，并将文件设置为隐藏属性，然后安装为服务“Uvwxya”进行自启动。

![](https://image.3001.net/images/20200928/1601256957_5f713dfd6182c20756a88.png!small)

木马启动后解密出PE文件并加载到内存执行。

![](https://image.3001.net/images/20200928/1601256969_5f713e0946f95fd44dd2b.png!small)

尝试连接C2地址ai.0x1725.site。

![](https://image.3001.net/images/20200928/1601256985_5f713e198dcc4cf49b964.png!small)

释放的远控木马可根据服务端指令完成上传下载文件、执行任意程序、进程管理、窗口管理、服务管理、网络代理、远程shell、清除日志等功能。

![](https://image.3001.net/images/20200928/1601256998_5f713e262c529d4027f4f.png!small)

## IOCs

 **Domain**

uer.reiykiq.ir

gie.ezrutou.ir

Ecc.0ieyFeD.ir

Sub.0ieyFed.ir

Js.0ieyFed.ir

fky.6d6973616b61.cyou

fky.6d6973616b61.icu

fky.6d6973616b61.xyz

fky.simimasai.fun

fky.simimasai.online

fky.simimasai.site

fky.simimasai.space

fky.simimasai.xyz

oio.seeeeeeeeyou.su

ai.0x1725.site

 **MD5**

download.exe

303d038621c2737f4438dbac5382d320

divsfrshost.exe

daf42817f693d73985cd12c3052375e2

hentai.exe

386be8418171626f63adb52d763ca1c0

 **URL**

http[:]//uer.reiykiq.ir/AdPopBlocker.exe

http[:]//UeR.ReiyKiQ.ir/download.exe

http[:]//UeR.ReiyKiQ.ir/SesnorDateService.exe

## 参考链接：

https://cloud.tencent.com/developer/article/1486905

https://issues.apache.org/jira/browse/SOLR-13669

https://www.freebuf.com/column/180544.html

https://www.freebuf.com/column/181604.html

https://www.freebuf.com/column/197762.html

https://www.freebuf.com/column/204343.html

[https://www.freebuf.com/articles/219973.html](articles/219973.html)

