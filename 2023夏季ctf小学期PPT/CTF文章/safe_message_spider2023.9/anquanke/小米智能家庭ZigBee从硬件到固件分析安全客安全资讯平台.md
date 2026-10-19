# 小米智能家庭ZigBee从硬件到固件分析

阅读量 **786726**

|评论 **15**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-09-16 15:45:13

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

#  小米智能家庭ZigBee通信分析

![](https://p3.ssl.qhimg.com/dm/1024_633_/t014d20e1d7fe6ce222.png)

## 一、简单介绍

    
    
      小米智能家庭是一套基于ZigBee Home Auto 1.2的一套智能化管理套件。自发布以来，因其出色的性价比，在市场中占了很大的比重。
      套件的结构为以小米网关为核心。小米网关同时支持WIFI和ZigBee低功耗通讯。在同一个局域网下，手机通过 WIFI 与网关进行通讯，网关负责将手机的 WIFI 数据指令转换成对它其他智能设备的 Zigbee 数据命令。
    

**大体结构如下图**

![](https://p0.ssl.qhimg.com/dm/1024_518_/t015a519a1683b19c7a.png)

####  本次嗅探破解，主要以ZigBee层交互破解为中心。

## 二、初探

  * 首先，需要嗅探Zigbee通讯层设备入网过程中，网关是否将密钥以明文的形式发送给终端节点。

需要如下图所示的一个ZigBee抓包器。（CC2531芯片 USB Dongle）

![](https://p0.ssl.qhimg.com/t01ca65cd0c34d6e57f.png)

  * 软件使用Ubiqua，这款软件为有偿使用的软件。而且价格不菲。遗憾的是，现在网上都没有它的破解版本。好在官方提供了新账号21天的使用权。
  * 打开软件插上USB Dongle之后，在设备列表中右键选择通讯信道。（这里的通讯信道出场固化不一定 11-25号信道 我是一个个信道的试出来的）。

以下为抓到的开关的入网过程：

![](https://p0.ssl.qhimg.com/dm/1024_576_/t01a1eb77eaddaceacf.png)

以下为开关按下多次后发送的ZigBee数据：

![](https://p0.ssl.qhimg.com/dm/1024_576_/t01525853fcb452fcae.png)

由上图可以看出。通讯过程全部加密。必须获取到ZigBee的通讯加密密钥才能将其通讯数据破解。

  * 未加密的数据部分中只展示了我现在所使用的网关创建的Zigbee网络信息为：  
PANID：0x3190  
网关的：IEEE 长地址为 ：00:15:8d:00:02:d3:94:cb

一般情况下信任中心（Zigbee协调器）保存密钥。在设备入网过程中，再使用次主密钥生成会话密钥并下发给其他节点。

  * ZigBee通讯安全密钥知识参考链接：<http://blog.csdn.net/stonerme/article/details/53409732>

## 三、尝试串口调试中获取通讯密钥

  * 在此，将小米智能网关拆解。

![](https://p2.ssl.qhimg.com/t01af31c362dd44c142.png)

  * 最初拆解后可以看到一共为两层，但是下面的一层为小米网关的灯光的电路板设计和电源集成的一块电路板。所以我们关注的重点就是上面的一层集成MCU和Zigbee射频模块的电路板（如下图连同电磁屏蔽罩一起拆掉）。

![](https://p5.ssl.qhimg.com/dm/1024_640_/t01cc523e4502c42a00.png)

  * 拆解后可以看到这块电路板上暴露了主控MCU，存储数据的Flash闪存，以及ZigBee射频芯片。

  * 下图为使用华为Mate20 Pro 的超细微距拍摄的主控放大图 ( HuaWei 加油 ！) ：  

可以看到芯片为 88MW302-NXU2 。

  * ###  网上查询资料后发现这是一款支持WIFI的低功耗无线主控芯片。也就是说 MCU和 WIFI 集成在了一起。

  * 继续查看ZigBee主控芯片。发现这款芯片 型号为 NXP 公司的 JN5169 Zigbee芯片 （如下图）。  

  * 下载主控芯片 88MW302-NXU2的 DataSheet PDF文件，查找Package （引脚图）：

![](https://p2.ssl.qhimg.com/t016016300df2b8d0a2.png)

上图中只表示了GPIO口的序号，详细的GPIO功能在文档中有明确的说明。

  * 详细查看小米底板后发现主控下方有10个测试点。  

  * 使用万用表进行测试后发现这10个测试点对应于芯片的功能引脚图如下：  

###  继续查看芯片手册中的GPIO引功能表发现如下图所示的对应关系。至此就找到了UART串口调试所需要的引脚测试点。

![](https://p4.ssl.qhimg.com/t01b12c2a3fa634c8d0.png)

![](https://p0.ssl.qhimg.com/t01f4b7b32b9866c15a.png)

  * 在测试点处焊接排针，使用杜邦线与USB转TTL板连接（如下图）。准备进行串口调试。

![](https://p4.ssl.qhimg.com/t01ea6be275fac73c7a.png)

  * 连接后将网关上电，同时将USB转TTL插到主机上。(注意此时不能连接GND和VCC 否则网关无法征程启动)

![](https://p5.ssl.qhimg.com/t010f5d45c3b9209921.png)

  * 连接后打开SecureCRT串口调试 。  
并且操作一次开关入网流程。在UART串口调试信息展示出了如下的调试信息

![](https://p1.ssl.qhimg.com/dm/1024_555_/t015fd110cccdf96270.png)

  * 直接看上去会发现这一大堆的数据看的让人头昏眼花。但是仔细的将所有的有关Zigbee的通讯的数据观察后发现，调试信息中会展示电路板上的ZigbeeJN5169芯片会给主控发送Zigbee的数据。(如下图)

![](https://p4.ssl.qhimg.com/t0134314eb78b1b68e6.png)

分析数据之前回顾之前未揭秘前拿到的Zigbee网络信息

    
    
    PANID：0x3190
    网关的：IEEE 长地址为 ：00:15:8d:00:02:d3:94:cb
    

将数据取出后，仔细分析其中两次的Zigbee回馈的数据：

    
    
    01 50 15 d6 63 4c e1 32 0f 08 6d 4e 7b 84 b9 2a a7 01 01 0b 31 90 00 01 00 06 28 40 00 15 8d 00 02 d3 94 cb 00 15 8d 00 02 d3 94 cb 20 4a e1 41 d7 da
    
    01 50 15 d6 63 4c e1 32 0f 08 6d 4e 7b 84 b9 2a a7 01 01 0b 31 90 00 01 00 06 28 2a 00 15 8d 00 02 d3 94 cb 00 15 8d 00 02 d3 94 cb 20 4a f7 d8 56 92
    

![](https://p0.ssl.qhimg.com/dm/1024_224_/t01a9db3ec7445eaaa6.png)

  * 首先先两次返回的数据中黄色和绿色部分都为网关Zigbee IEEE长地址。而 蓝色部分为网关创建的Zigbee 网络的 PANID 。  
由此猜测 如果本条调试信息中 存在密钥的话 蓝色部分之前应该为密钥。（因为Zigbee网络中密钥为 128位 16字节的 AES
密钥，这也是为什么在众多的UART调试信息中为什么比较关注这条长一点的数据的原因）

蓝色部分之前 有 20 个字节长度的 所以 因为其他部分识别不出来，所以只能去尝试在这20字节中进行最多五次的尝试解密。

  * 当取出这20字节中第二个的16个字节进行第二次尝试，将其导入到Ubiqua的密钥列表中。

![](https://p5.ssl.qhimg.com/t015828826d02f88920.png)

## 导入后发现成功解密 。

  * 至此就将所有小米智能家居的Zigbee通讯报文数据全部解密。  
解密后下图中发现了在入网过程中网关发送给开关结点的会话密钥。  
（然后就可以尝试自己使用 已经拿到的Zigbee密钥进行 Zigbee的其他途径的攻击了）  

  * 下图为开关按下后 发出的 Zigbee 数据包 。

![](https://p4.ssl.qhimg.com/dm/1024_556_/t01fe2569f4275eaa33.png)

## 四、最值得分析的部分

![](https://p5.ssl.qhimg.com/t016f2c2bb8d3bc110b.png)

  * 值得进一步分析的是如下图所示的存放小米固件的Flash芯片！  
可以看出小米为了安全已经将芯片印记涂抹，难以辨识。  
将Flash芯片取下后进行连接编程器：  
编程器自动识别出Flash芯片厂商和类型。

![](https://p0.ssl.qhimg.com/t01f8ff985574cbc416.png)

  * 将固件提取出来后，放到Ubuntu下 使用 binwalk 提取文件系统：

![](https://p5.ssl.qhimg.com/dm/1024_533_/t01a98d04f5120ae979.png)

![](https://p3.ssl.qhimg.com/dm/1024_125_/t01d72558e5b3f629be.png)

#####  如上图所示，提取出的文件系统解密失败。（决定之后再进行尝试解密）

## 五、总结

由此看出
，小米还是一家良心的注重安全的厂商！安全防护还是做的很到位。在找UART调试口的时候，废了很大的功夫才确定了最后的测试点，原因是电磁防护罩做的额很好，每条边都是焊接上去的。很难取下来。而且还擦出了zigbee芯片和flash芯片的芯片印字。固件读出后又面临这解密的问题。

###  参考链接：

<http://blog.csdn.net/stonerme/article/details/53409732>

<https://blog.csdn.net/weixin_42030357/article/details/92030179>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **破壳** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/186619](/post/id/186619)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [物联网](/tag/物联网)
  * [Zigbee](/tag/Zigbee)

 **+1** __24赞

 __收藏

![](https://p0.ssl.qhimg.com/t010e14b27cbc40355c.png) 破壳

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

