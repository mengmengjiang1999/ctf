## 一、事件报告

最近，国外某安全研究人员再次发现GandCrab勒索病毒V2.1最新变种，千里目安全实验室EDR安全团队第一时间拿到相关的样本，发现这次GandCrab勒索病毒最新的变种采用RSA1024加密算法，将系统中的大部分文档文件加密为.GRAB后缀的文件，然后对用户进行勒索。

GandCrab勒索病毒首次发现是2018年2月份，也是首例向受害者勒索达世币的勒索病毒，此次发现的最新样本，可以让受害者使用比特币和达世币进行赎金支付。用户点击之后会加密受害者主机大部分文件，然后在相应的目录生成勒索信息文件。

截止到发稿，VT上对此样本的查杀情况如下

![图片.png](https://image.3001.net/images/20180426/15247077339324.png!small)
![图片.png](https://image.3001.net/images/20180426/15247077383827.png!small)  

## 二、攻击方式

### 传播方式

这个勒索病毒主要通过邮件、漏洞、垃圾网站挂马等方式进行传播，其不具备横向感染的能力，不会能局域网的其他设备发起相应的攻击。

样本母体分析grounded.exe

1\. GandCrab母体使用了多层封装与代码混淆，代码会经过几层解密操作，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247077503378.png!small)  

2\. 经过几层解密完成之后，启动系统目录下的SVCHOST.EXE程序，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247077558230.png!small)  

执行之后进程列表如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247077619465.png!small)  

3\. 将解密完的Payload通过反射式DLL注入的方式，注入到SVCHOST.EXE进程中，如下图所示:

![图片.png](https://image.3001.net/images/20180426/15247077654184.png!small)  

然后通过VirtualProtect、WriteProcessMemory修改Payload内存属性和数据，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247077703122.png!small)  

4\. Payload加载完成之后，执行Payload程序，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247077756998.png!small)  

5\. 最后进行自删除操作，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247077793624.png!small)  

Payload恶意加密程序分析

1.创建一个主线程来，执行恶意行为，如下图所示：

![图片.png](https://image.3001.net/images/20180426/1524707784915.png!small)  

2.加密线程初始化操作，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247077888569.png!small)  

3.获取系统信息，创建互斥变量，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247077926052.png!small)  

相关的系统信息，如下：

pc_user（用户名）、pc_name（主机名）、pc_group（用户组）、av（安全软件信息）、pc_lang（操作系统语言）、pc_keyb、os_major（操作系统版本）、os_bit（操作系统位数）、ransom_id（勒索ID）、hdd（磁盘空间）、ip（IP地址），安全软件相关的信息如下图所示：

![图片.png](https://image.3001.net/images/20180426/1524707796323.png!small)  

如果发现有进程中有上述安全相关的进程，则上报到远程服务器，相关的安全进程列表如下：

AVP.EXE、ekrn.exe、avgnt.exe、ashDisp.exe、NortonAntiBot.exe、Mcshield.exe

avengine.exe、cmdagent.exe、smc.exe、persfw.exe、pccpfw.exe、fsguiexe.exe

cfp.exe、msmpeng.exe

4.遍历相关的进程，然后结束进程，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078039015.png!small)  

相关的进程列表如下：

msftesql.exe、sqlagent.exe、sqlbrowser.exe、sqlservr.exe、sqlwriter.exe、oracle.exe

ocssd.exe、dbsnmp.exe、synctime.exe、mydesktopqos.exe、agntsvc.exeisqlplussvc.exe

xfssvccon.exe、mydesktopservice.exe、ocautoupds.exe、agntsvc.exeagntsvc.exe、agntsvc.exeencsvc.exe、firefoxconfig.exe、tbirdconfig.exe、ocomm.exe、mysqld.exe

mysqld-nt.exe、mysqld-opt.exe、dbeng50.exe、sqbcoreservice.exe、excel.exe、infopath.exe、msaccess.exe、mspub.exe、onenote.exe、outlook.exe、powerpnt.exe、steam.exe、sqlservr.exe、thebat.exe、thebat64.exe、thunderbird.exe、visio.exe

winword.exe、wordpad.exe

6.创建ID，创建勒索字符串相关信息，以及拼接相应的URL地址，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078111819.png!small)  

URL地址：[www.torproject.org/download/download-easy.html.en](http://www.torproject.org/download/download-easy.html.en)

7.生成RSA密钥，连接CSP容器，获得指定的CSP的密钥容器句柄，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078158275.png!small)  

Microsoft Enhanced Cryptographic Provider1.0的密钥长度为1024位，生成密钥，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078214171.png!small)  

然后导出相应的公钥和私钥，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078268529.png!small)  

8.将导出的公钥和私钥，加上用户主机相关的信息，进行字符串拼接，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078318448.png!small)  

9.将拼接的字符串，通过POST的方式发送到远程恶意服务器上，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078356174.png!small)  

10.使用HTTP协议进行发送数据包，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078406476.png!small)  

远程服务器连接请求的地址：ipv4bot.whatismyipaddress.com

11.相关的HTTP请求，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078441454.png!small)  

HTTP请求的主机名：ahnlab.com

12.对导出的公钥和私钥进行编码处理，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078507348.png!small)  

RSA公钥如下：

06 02 00 00 00 A4 00 00 52 53 41 31 00 08 00 00 01 00 01 00 57 C0 F3 73 ED D7
6D C6 8C 8F 75 20 2A A1 D7 68 55 C7 62 0A 07 9D 16 D1 61 23 2F 04 EA 3E A8 78
16 DC 0E 76 F4 28 B5 3F 0C 99 C9 BB D9 FF 28 97 BF 3B 77 CF C9 C6 C9 26 B8 6C
BF 6D 90 52 6D 33 EB F0 71 AF B4 D4 EC 1B C1 4B 60 87 65 5B 23 92 80 D1 B8 72
C5 11 44 03 6B 07 D4 47 A8 80 13 E2 F1 70 53 89 B5 9E 3A E4 85 7F 35 F5 04 7B
D2 04 6C B6 D0 FC E5 D7 9F 8A 7B 9B F6 60 0F 6B 0C 41 11 E6 59 F7 E7 4D 94 AB
C8 7D 7A 48 31 77 CA 7F E2 3D 26 97 1F 47 76 DC D6 31 36 56 BE 4F C3 0F 48 66
39 07 27 CC D7 B1 9E BF 56 4D 48 DF 2F BB 34 33 F2 ED 26 26 ED 1B E8 38 D4 4A
27 30 BD CB 00 77 5A C4 0C 97 E9 A8 8A 38 81 49 08 9E 0D F9 FE 6E AD 94 F5 1E
5F 7C AA 7F 2B 83 17 94 F3 57 31 A4 F5 4A A7 90 6B 29 F3 AF 26 BB 42 F4 7B 06
EA 52 7B B5 00 9C A0 0E 27 A6 D7 26 AD 81 28 96

通过编码之后，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078552232.png!small)  

对RSA私钥编码之后如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078591392.png!small)  

最后将获得的主机相关信息与RSA生成的公钥和私钥的编码拼接在一起，发送到远程恶意服务器上，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078655809.png!small)  

发送数据到远程后台服务器，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078707012.png!small)  

服务器地址：

ransomware.bit

zonealarm.bit

远程服务器IP，如下所示：

185.183.98.202

13.获得主机磁盘信息，创建线程进行文件加密操作，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078764845.png!small)  

14\. 以下文件目录下的文件不会被加密，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078802417.png!small)  

相关的文件目录列表如下：

> \ProgramData\
>
> \IETldCache\
>
> \Boot\
>
> \Program Files\
>
> \Tor Browser\
>
> \All Users\
>
> \Local Settings\
>
> \Windows\

15\. 在相应的目录下生成勒索信息文本文件CRAB-DECRYPT.txt，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078859902.png!small)  

16\. 加密进程不会加密以下文件，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078907242.png!small)  

相关的文件名列表如下：

> desktop.ini、autorun.inf、ntuser.dat、iconcache.db、bootsect.bak、boot.ini、
>
> ntuser.dat.log、thumbs.db、CRAB-DECRYPT.txt

17\. 最后进行文件加密操作，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247078951795.png!small)  

18\. 调用wmic.exe删除卷影服务，使得文档无法恢复，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247079002891.png!small)  

19.最后执行关机操作，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247079049146.png!small)  

20.加密完成之后的，文件名以“.GRAB”作为后缀，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247079094882.png!small)  

21.勒索信息的文件文件，打开之后如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247079132649.png!small)  

打开所提示的链接，可以看到GandCrab向受害用户勒索价值499美元的达世币和比特币，如下图所示：

![图片.png](https://image.3001.net/images/20180426/15247079196358.png!small)
![图片.png](https://image.3001.net/images/20180426/15247079234787.png!small)  

## 三、预防措施

同时千里目安全实验室提醒用户，日常防范措施：

> 1.不要点击来源不明的邮件以及附件，不从不明网站下载相关的软件
>
> 2.及时给电脑打补丁，修复漏洞
>
> 3.对重要的数据文件定期进行非本地备份
>
> 4.安装专业的终端/服务器安全防护软件
>
> 5.定期用专业的反病毒软件进行安全查杀
>
> 6.尽量关闭不必要的文件共享权限以及关闭不必要的端口，如：445,135,139,3389等

## 四、相关IOC

> MD5
>
> EF5353B4B40EDB06AC7250AEFB6B7000
>
> DNS/URL
>
> ipv4bot.whatismyipaddress.com
>
> ahnlab.com
>
> ransomware.bit
>
> zonealarm.bit
>
> IP
>
> 185.183.98.202

 *** 本文作者千里目安全实验室，转载注明来自FreeBuf**  

