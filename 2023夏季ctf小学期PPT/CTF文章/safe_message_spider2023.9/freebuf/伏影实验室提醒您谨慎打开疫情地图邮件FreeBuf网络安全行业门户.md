# 一、前言

随着新冠肺炎病毒（nCoV-19）在世界范围内的传播扩散，多个国际黑客组织开始注意到疫情话题在社会工程学方面的易用性，用疫情信息做掩护发起攻击。

在绿盟科技伏影实验室早前发布的信息中显示，已有Emotet、FormBook等知名木马在攻击中使用了疫情信息作为诱饵。（详情可见：http://blog.nsfocus.net/watch-out-for-hackers-attacked-by-new-crown-virus-pneumonia/）

近期，伏影实验室发现，NetWire远控木马控制者开始使用nCoV-19疫情相关的诱饵文档来投放木马。相关IOC可通过绿盟威胁情报中心（https://nti.nsfocus.com/）获取。

NetWire，又称NetWireRC或Recam，是一款远控木马，最早出现在2012年。曾被尼日利亚的黑客用于攻击企业目标。多年以来，NetWire一直在更新版本，并演化出多条不同的攻击链。2019年起，NetWire进入新一轮的爆发期，借助由鱼叉邮件和网盘组建的扩散网络广为传播。

# 二、事件简述

近期，伏影实验室捕获的部分NetWire文档样本中含有nCoV-19疫情的社工信息。

当受害者打开恶意邮件中的附件文档时，将会看到如下所示的内容：

![1.png](https://image.3001.net/images/20200319/1584615637_5e7350d5d271a.png!small)

文档中图片显示了nCoV-19病毒的全球传播情况，并且有地域上的错误。

而该文档实际包含cve-2017-11882公式编辑器漏洞，会下载并执行恶意程序，最终使NetWire木马在受害者主机上运行。

该NetWire的大致攻击流程如下：

![2.png](https://image.3001.net/images/20200319/1584615637_5e7350d5d1969.png!small)

漏洞rtf文档运行后，通过短链接获取到二阶段载荷的地址并下载运行，二阶段载荷将解密后的字符串和shellcode注入到windows程序ieinstal.exe中运行，shellcode访问GoogleDrive并将NetWire下载到内存中执行。该NetWire变种最终连接cnc服务器79.137.*.103。

#

# 三、事件分析

## rtf文档

该诱饵文档包含高度混淆的rtf编码，会触发cve-2017-11882漏洞：

![3.png](https://image.3001.net/images/20200319/1584615638_5e7350d690c50.png!small)

漏洞触发后，程序跳转至shellcode运行。shellcode使用常见的GlobalLock思路寻找Ole流对象位置，随后跳转至对象中的第二段shellcode运行。第二段shellcode亦经过高度混淆。

该漏洞文档的恶意shellcode最终下载短链接bit.ly/2T*xW（当前被解析至hxxp://www.asim*.com/new/Notepad.txt）中的内容并执行，同时在word中显示文档中附带的jpeg格式疫情地图。

##

## Notepad.txt

恶意rtf下载运行的二阶段载荷Notepad.txt是vb程序，主要功能为启动和注入windows程序ieinstal.exe，注入内容为shellcode和解密后的字符串配置项等。

被注入的isinstal.exe运行后，会创建指定目录USER\\\Bagtaler4\\\，将恶意程序本体转移至目录下并命名为Samipat8.exe，之后创建注册表启动项实现持久化：

![4.png](https://image.3001.net/images/20200319/1584615638_5e7350d6232d7.png!small)

随后程序访问硬编码地址hxxps://drive.google.com/uc?export=download&id=1kFK*Jz90下载解密并执行最终阶段载荷NetWire远控木马。

解密过程中使用了以下函数：

![5.png](https://image.3001.net/images/20200319/1584615676_5e7350fc66291.png!small)  
解密逻辑为长键值异或，使用的异或键由shellcode提供。本例中用到的解密键长度为0x24A，由长为0x100的键循环生成，值为：  

076C3D0F54873230F1AE34A2E026CB21DCF06F35280A6456C631AAC7B4EEFD46B0B7E516FC8DDA379AF9DDA94471746B843A183BD1110D5C6E7C53CE19F4A64D58BD4A60A5D83F8142FF85F3ED771C722D41C042795BB5A71782FBD4C1FB4E9701**F2674DDEE888EB062EFA95C2C5BCD547698C22625EADBFCDA41F6A45F79EA90E9BB1F6E590D24F50D6003EC829C33A921193CAAC06B424D30825124C9FE80E1543B89E2F38D9F8577F4BE6CFD2C9E298BADD2FB3AFFECCDAB12CBB5248EFB61BECBE0336E1DFA0A127518F197A148BE31EE4D7B9130575245976639DF0F55F669409AB3C892A49A8D09C3720231A33E9C7EA8004BC0B1D2B027D0CA35540076C3D0F54873230F1AE34A2E026CB21DCF06F35280A6456C631AAC7B4EEFD46B0B7E516FC8DDA379AF9DDA94471746B843A183BD1110D5C6E7C53CE19F4A64D58BD4A60A5D83F8142FF85F3ED771C722D41C042795BB5A71782FBD4C1FB4E9701**F2674DDEE888EB062EFA95C2C5BCD547698C22625EADBFCDA41F6A45F79EA90E9BB1F6E590D24F50D6003EC829C33A921193CAAC06B424D30825124C9FE80E1543B89E2F38D9F8577F4BE6CFD2C9E298BADD2FB3AFFECCDAB12CBB5248EFB61BECBE0336E1DFA0A127518F197A148BE31EE4D7B9130575245976639DF0F55F669409AB3C892A49A8D09C3720231A33E9C7EA8004BC0B1D2B027D0CA35540076C3D0F54873230F1AE34A2E026CB21DCF06F35280A6456C631AAC7B4EEFD46B0B7E516FC8DDA379AF9DDA94471746B843A183BD1110D5C6E7C53CE19F4A64D58BD4A60A5D83F8142FF

## NetWire

被注入的ieinstal程序最终在内存中加载了NetWire木马。

木马程序连接C&C地址为79.137.*.103:39561,通信遵循以下格式:

![微信截图_20200319154828.png](https://image.3001.net/images/20200319/1584615677_5e7350fd68a80.png!small)

data部分使用aes加密，加密的key与IV在木马初始化时随机生成，并在首次通信时上传给C&C：

![6.png](https://image.3001.net/images/20200319/1584615676_5e7350fc63e24.png!small)图中蓝色部分为协议头部，红色部分为32字节key，黄色部分为16字节IV，绿色部分为加密例文，对应的明文硬编码在木马文件中。

C&C收到木马提供的加密键后，使用此键加密data段内容，与木马持续通信：

![7.png](https://image.3001.net/images/20200319/1584615676_5e7350fc6cbf5.png!small)

本例中使用的NetWire木马是功能较全的变种，共支持57种不同的指令，可进行包括文件操作、进程操作、窗口操作、注册表操作、反弹shell、流量转发、模拟输入、用户凭证窃取等行为。具体功能见指令表：

![11.png](https://image.3001.net/images/20200319/1584615676_5e7350fcae862.png!small)![22.png](https://image.3001.net/images/20200319/1584615676_5e7350fcb67fb.png!small)![33.png](https://image.3001.net/images/20200319/1584615676_5e7350fcc56da.png!small)  

# 四、事件影响

关联数据显示，此次事件中的域名www.asim*.com在2019年10月就开始下发NetWire木马，而事件中的网盘链接自2月26日被发现以来已经运行了超过两周。此外，我们通过数据发现，自今年以来NetWire已经下发了25个不同的网盘链接，其中早在1月9日的链接至今仍可访问。以上信息均证实了NetWire攻击具有长效性。

本次nCoV-19疫情诱饵的传播表明NetWire及其背后的团体进入了新的活跃期，长效的攻击链使得邮件用户将有相当长的时间笼罩在NetWire的攻击之下。

#  

## 关于伏影实验室

伏影实验室专注于安全威胁研究与监测技术，包括但不限于威胁识别技术，威胁跟踪技术，威胁捕获技术，威胁主体识别技术。研究目标包括：僵尸网络威胁，DDOS对抗，WEB对抗，流行服务系统脆弱利用威胁、身份认证威胁，数字资产威胁，黑色产业威胁
及 新兴威胁。通过掌控现网威胁来识别风险，缓解威胁伤害，为威胁对抗提供决策支撑。

## 关于绿盟威胁情报中心

绿盟威胁情报中心（NSFOCUS Threat Intelligence center,
NTI）是绿盟科技为落实智慧安全2.0战略，促进网络空间安全生态建设和威胁情报应用，增强客户攻防对抗能力而组建的专业性安全研究组织。其依托公司专业的安全团队和强大的安全研究能力，对全球网络安全威胁和态势进行持续观察和分析，以威胁情报的生产、运营、应用等能力及关键技术作为核心研究内容，推出了绿盟威胁情报平台以及一系列集成威胁情报的新一代安全产品，为用户提供可操作的情报数据、专业的情报服务和高效的威胁防护能力，帮助用户更好地了解和应对各类网络威胁。

NTI网址：https://nti.nsfocus.com/

  

