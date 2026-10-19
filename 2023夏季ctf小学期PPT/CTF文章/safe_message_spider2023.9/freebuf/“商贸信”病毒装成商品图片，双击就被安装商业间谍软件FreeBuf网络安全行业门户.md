## 一、背景  

**腾讯御见威胁情报中心近期检测到商贸信木马家族最新变种攻击。攻击者将伪装成图片的lnk文件放置于压缩包中，然后将其作为邮件附件发送给目标邮箱，当被攻击者收到邮件，并尝试点击附件中的“图片”进行查看时，lnk文件指向的mshta脚本或powershell恶意代码会立即执行。**

恶意代码首先会下载并打开一个用于掩饰攻击行动的图片，而后台却在下载商业间谍软件NanoCoreRAT运行，该商业间谍软件可完全控制受害者电脑，窃取任意文件资料，执行键盘记录窃取关键密码信息，下载运行任意程序，控制中毒电脑的音频、摄像头设备，也可接受远程指令对目标计算机进行拒绝服务攻击（DoS）。

以往的商贸信钓鱼邮件攻击，多以word文件作邮件附件来欺骗打开，通过文档触发Office高危漏洞(CVE-2017-11882、CVE2017-8759)攻击为主，此次发现的攻击直接发送包含恶意代码执行的lnk文件。一旦用户双击假冒的图片文件，还以为真的只看到商品信息，而实际上RAT（远程控制）木马已被下载运行。此类攻击构造简单，可灵活更换攻击脚本代码，恶意代码的执行并不需要利用电脑安全漏洞，具有高度隐蔽性和欺骗性，会对相关行业人员造成极大威胁。

腾讯电脑管家及腾讯御点终端安全管理系统均可成功防御商贸信病毒的本次攻击。

![0.png](https://image.3001.net/images/20190403/1554260060_5ca4205c7c9f1.png!small)

## 二、载荷投递

黑客向目标人员发送邮件。

![1.png](https://image.3001.net/images/20190403/1554260067_5ca420633e4e9.png!small)

邮件中说明附件内容为产品信息，并提出关于价格方面的意见。

![2.png](https://image.3001.net/images/20190403/1554260073_5ca42069d9d89.png!small)

附件压缩包中的文件后缀为.jpg.lnk，但并不是图片文件，而是一个快捷方式（lnk文件）。

![3.jpg](https://image.3001.net/images/20190403/1554260084_5ca420748ed75.jpg!small)

对多个类似邮件附件进行分析，发现其中的快捷方式中暗藏的恶意代码分为两种：

一种为下载执行远程mshta脚本，另一种为指向下载执行远程Powershell脚本，而下载的地址都是77.73.68.175。

![4.png](https://image.3001.net/images/20190403/1554260095_5ca4207f7a203.png!small)

下载Hta脚本hxxp://77.73.68.175/BwVuHr/cabinm/nap.hta进行分析，发现其中代码经过了混淆，同时又包含解密函数：

![5.png](https://image.3001.net/images/20190403/1554260104_5ca420882fc8c.png!small)

脚本执行时先通过解密函数对加密的内容进行解密：

![6.png](https://image.3001.net/images/20190403/1554260114_5ca4209294782.png!small)

解密后的代码为Powershell脚本，脚本首先下载图片hxxp://excursiionline.ro/cgib/159.jpg并打开，图片提示workbook读取Excel失败，让中招者误以为是附件中的数据格式不支持。

![7.png](https://image.3001.net/images/20190403/1554260126_5ca4209ee95b7.png!small)

然后下载木马hxxp://77.73.68.175/BwVuHr/cabinm/nap.exe，获取三位随机字符作为木马文件名，并保存木马至C:\Users\Public\xxx.exe目录，通过命令Start-Process启动木马执行。

![8.png](https://image.3001.net/images/20190403/1554260137_5ca420a91e239.png!small)

## 三、RAT（远程控制）木马

Lnk文件打开后导致木马下载并被保存至C:\Users\Public\目录下，木马外壳使用VB语言编写，核心代码实际上为商业间谍软件NanoCoreRAT：

![9.png](https://image.3001.net/images/20190403/1554260147_5ca420b3a0a60.png!small)

运行后拷贝自身到Temp目录下，创建用于启动木马的VBS脚本From1Galo.vbs：  

![10.png](https://image.3001.net/images/20190403/1554260159_5ca420bf32288.png!small)

将VBS脚本添加注册表启动项：

    
    
    HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunOnce\Form1MOTO

![11.jpg](https://image.3001.net/images/20190403/1554260171_5ca420cb07c26.jpg!small)

创建计划任务启动木马：  

计划任务名：SCSI Subsystem

![12.jpg](https://image.3001.net/images/20190403/1554260181_5ca420d5d9a48.jpg!small)

还会拷贝自身到软件目录下，作为另一个副本执行，以增加木马驻留几率：

    
    
    C:\Program Files (x86)\SCSI Subsystem\scsiss.exe

(伪装成SCSI接口设备程序)，并通过注册表添加启动项：

    
    
    HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Run\SCSI Subsystem

![13.jpg](https://image.3001.net/images/20190403/1554260191_5ca420df7369d.jpg!small)

添加计划任务启动：

计划任务名：SCSI Subsystem Task

![14.jpg](https://image.3001.net/images/20190403/1554260203_5ca420ebb71b2.jpg!small)

分析发现该木马为商业窃密软件NanoCoreRAT，主要功能为窃取感染用户的敏感信息、密码等，同时还支持多种插件功能。

创建%appdata%Roaming[MachineGuid]文件夹，将当前的时间写入run.dat并保存在这个目录中后，将配置信息放入一个字典中用来检索对应的配置，根据这些信息来执行对应的操作，包括设置自启动、bypassUAC、设置访问权限、加载插件等等，并将获取到的键盘输入信息加密后保存至Logs目录下。

![15.png](https://image.3001.net/images/20190403/1554260215_5ca420f735d62.png!small)

木马接收远程指令执行以下功能：

1.密钥记录

2.“压力测试”或DDoS

3.下载、执行或安装其他软件

4.远程CLI和UI

5.注册表编辑

6.SOCKS代理

7.防火墙修改

8.网络摄像头和音频控制

![16.png](https://image.3001.net/images/20190403/1554260228_5ca42104a7f5b.png!small)

木马连接到C&C服务器，上传用户信息和接收下一步的指令，此样本中包含的C&C地址为：194.5.98.79:9320  

![17.png](https://image.3001.net/images/20190403/1554260238_5ca4210e07fe7.png!small)

## 四、安全建议

1.不要打开不明来源的邮件附件；可修改资源管理器查看文件的选项：“选择查看文件扩展名”，如果发现任何文件有两个扩展名，都需要高度警惕。

2.及时打系统补丁和重要软件的补丁；

3.使用杀毒软件防御可能的病毒木马攻击；

4.使用腾讯御界高级威胁检测系统。御界高级威胁检测系统，是基于腾讯反病毒实验室的安全能力、依托腾讯在云和端的海量数据，研发出的独特威胁情报和恶意检测模型系统。

![18.png](https://image.3001.net/images/20190403/1554260248_5ca4211870dd0.png!small)

## IOCs

### IP

77.73.68.175

194.5.98.79

94.100.18.101

### URL

hxxp://77.73.68.175/LUvUtvw/PO4506748678.jpg.zip

hxxp://77.73.68.175/LUvUtvw/out-1331592449.ps1

hxxp://77.73.68.175/BwVuHr/cabinm/nap.hta

hxxp://77.73.68.175/LUvUtvw/out-512330769.ps1

hxxp://77.73.68.175/LUvUtvw/out-2117802234.ps1

hxxp://77.73.68.175/BwVuHr/cabinm/nap.exe

hxxp://excursiionline.ro/cgib/159.jpg

### Md5

95d241d7748e60423779db4e31595aa3

f059cbce29ab770bddf628f1a921477a

3d4c124df87c3be8d49e49b07a16be84

13654be48ee95fcb4c7d9ee8addf7876

00143acfa694db7393293dda936f6b1c

8cd1e7208641d4c1050a8ced8bec48bf

9f8f5fa0a7966755f4e0797e42e03d41

9203483e93815aa5aafa741edae2b21b

b57b9c113ca398d017b587fbdbeb8734

37886213afee09067d07e0cc973c001f

39aef29d0b341498cdf7f87963369120

fdd99e434664fa04aec707d9f36c9670

204e7679f29b04b3605ddce5c78493bf

22f9bf146e16ef3da4702aadb5afa645

c18bc555dbac0385d2ca58f813f8d3db

3b59af680e370a84a066bb15dfa41000

07e7a14e2e05af9de1562decc12ac5c5

ed06f19eff1bd501bc295b114806124b

9396d2a5f881ead48bdfaafb405b9186

76def4416fdc6f92053b199405470269

4f5fe0af211aa19d4b3f0682e39898cc

 ***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**

