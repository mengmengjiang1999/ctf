## 概述

 **[TA505](https://www.proofpoint.com/us/threat-insight/post/threat-actor-profile-ta505-dridex-globeimposter)是Proofpoint研究团队一直在跟踪的一个活动非常频繁的网络犯罪组织，根据目前收集到的数据，该组织操作过始于2014年的上百次Dridex恶意活动，以及2016年和2017年的大规模Locky攻击活动，而且其中的很多攻击活动涉及到了全世界数以亿计的恶意消息。近期，该组织又开始传播各种远程访问木马（RAT），以及各类信息提取、加载和网络侦侦查工具了，其中就包括我们之前没介绍过的tRat。**

tRat是一款采用Delphi开发的模块化RAT，这款RAT在今年9月份和10月份的恶意活动中首次出现。那么在这篇文章中，我们将对这款RAT进行简单的分析。

## 恶意活动

在2018年9月27日，Proofpoint检测到了一次恶意邮件活动，该活动中的恶意Microsoft
Word文档使用了宏功能来下载tRat。这份恶意文档中标记了Norton杀毒引擎的字样，并且通过文档名称和嵌入的图片告诉用户这份文件是受卡巴斯基安全产品保护的。邮件的主题栏包含了“安全共享文件”的字样，这里同样也使用了社工技术来安装tRat：

![2.png](https://image.3001.net/images/20181202/1543724866_5c035f42d804c.png!small)

![3.png](https://image.3001.net/images/20181202/1543724874_5c035f4a1906f.png!small)

在2018年10月11日，我们还观察到了另一个传播tRAT的恶意活动。这次活动背后的攻击者就是TA505，而且这一活动比之前的更加复杂，他们使用了Microsoft和Microsoft
Publisher文件，并且丰富了主题栏和发送方的内容。通过分析来看，此次活动似乎针对的是商业银行机构的用户。

在这一活动中，带有恶意Microsoft
Publisher文档的消息会标记上“计费单”和“收货单”等字样。比如说，有的恶意邮件主题为“呼叫通知-[随机数字]-[随机数字]”，携带的附件名为“Report.doc”：

![4.png](https://image.3001.net/images/20181202/1543724882_5c035f523f979.png!small)

其中，邮件附件会包含恶意宏，启用之后，便会下载tRat：

![5.png](https://image.3001.net/images/20181202/1543724890_5c035f5a9879b.png!small)

## 恶意文件分析

在对恶意软件样本进行了分析之后，我们发现tRat会通过将代码拷贝到下列位置来实现持续性感染：

    
    
    C:\Users\<user>\AppData\Roaming\Adobe\FlashPlayer\Services\Frame Host\fhost.exe

接下来，tRat会在启动目录中创建一个LNK文件，然后目标设备会在系统启动时执行恶意代码：

    
    
    C:\Users\<user>\AppData\Roaming\Microsoft\Windows\StartMenu\Programs\Startup\bfhost.lnk

tRat中大多数的重要字符串都会加密存储，并使用了十六进制转码。这里给大家提供了一个Python脚本来对这些字符串进行解密。【[脚本下载](https://github.com/EmergingThreats/threatresearch/blob/master/tRat/decrypt_str.py)】

tRat使用TCP（端口80）来与远程C2服务器进行通信，数据进行了加密并以十六进制形式发送。为了生成解密密钥，tRat会连接三个字符串，并生成一个大写的十六进制编码字符串，我们解码出的样本字符串如下：

    
    
    "Fx@%gJ_2oK"
    
    "AC8FFF33D07229BF84E7A429CADC33BFEAE7AC4A87AE33ACEAAC8192A68C55A6"
    
    "&LmcF#7R2m"

目前我们还不知道不同恶意软件样本的这些字符串会不会变化。

为了生成密钥，tRat会在解密过程中使用一个1536字节的密码表，虽然我们现在还没弄清楚这个密码表中所有元素的明确含义，但是我们发现代码会进行异或计算，而且算法中的部分值是从加密数据中获取的。【[密码表获取](https://github.com/EmergingThreats/threatresearch/blob/master/tRat/table)】

tRat的初始网络请求为“ATUH_INF”，解密样本如下：

    
    
    MfB5aV1dybxQNLfg:D29A79D6CD2F47389A66BB5F2891D64C8A87F05AE3E1C6C5CBA4A79AA5ECA29F8E8C8FFCA6A2892B8B6E

这个字符串包含了两个子字符串，由“:”分隔。第一个子字符串是一个硬编码的标识符（加密字符串），第二个子字符串包含了加密的系统数据，样本如下：

    
    
    FASHYEOHAL/nXAiDQWdGwORzt:3A176D130C266A4D

这些数据中会包含受感染主机的名称、系统用户名和tRat bot ID。

目前，我们还没观察到tRat的远程C2服务器发送任何新的功能模块，所以我们现在还无法确定新版本恶意软件会增加哪些功能。

## 入侵威胁指标IoC

    
    
    IoC：cd0f52f5d56aa933e4c2129416233b52a391b5c6f372c079ed2c6eaca1b96b85

IoC类型：SHA256

IoC描述：tRat样本哈希，9月27日活动

    
    
    IoC：cdb8a02189a8739dbe5283f8bc4679bf28933adbe56bff6d050bad348932352b

IoC类型：SHA256

IoC描述：tRat样本哈希，10月1日活动

    
    
    IoC：51.15.70[.]74

IoC类型：IP

IoC描述：C&C

## 参考资料

1.<https://github.com/EmergingThreats/threatresearch/blob/master/tRat/decrypt_str.py>

2.<https://github.com/EmergingThreats/threatresearch/blob/master/tRat/table>

3.<https://github.com/EmergingThreats/threatresearch/blob/master/tRat/decrypt_comms.py>

 ***参考来源：[proofpoint](https://www.proofpoint.com/us/threat-insight/post/trat-new-modular-rat-appears-multiple-email-campaigns)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

