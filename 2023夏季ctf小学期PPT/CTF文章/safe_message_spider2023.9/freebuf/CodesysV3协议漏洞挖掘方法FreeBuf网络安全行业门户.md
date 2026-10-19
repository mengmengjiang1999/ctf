## 背景概述

Codesys是全球最著名的软PLC内核软件研发厂家德国的3S（SMART，SOFTWARE，SOLUTIONS）公司发布的一款与制造商无关IEC
61131-1编程软件及工控设备内核（runtime SDK）。Codesys
支持完整版本的IEC61131标准的编程环境，支持标准的六种编程语言，是一个标准的与硬件无关的Runtime，被很多硬件厂家支持，
Codesys提供了许多组合产品的扩充，诸如各种不同领域的总线配置程序和运动控制系统。

由于Codesys提供的解决方案覆盖全面、功能强大、开发周期短、灵活性高、支持硬件架构及操作系统丰富等原因在全球工控厂商中广泛使用，据官方统计使用Codesys解决方案的知名企业超过500家，Codesys市场占有率为35%，其中我们熟知ABB、施耐德电气、费斯托Festo、伊顿电气、博世力士乐、WAGO、倍福BECKHOFF、研华科技、凌华科技、巴赫曼Bachmann、KEBA、深圳合信、汇川技术、深圳英威腾、华中数控、步科、固高科技等等都使用了Codesys
Runtime。

更详细的合作厂商及案例见Codesys厂商网站：http://www.codesys.cn/list-Partner-1.html

![1691411677_64d0e4ddf17f0b58b5be4.png!small?1691411678821](https://image.3001.net/images/20230807/1691411677_64d0e4ddf17f0b58b5be4.png!small?1691411678821)

正因为诸多知名工控厂商大规模使用该内核，因此Codesys产品的安全性影响巨大。一旦源头出现问题则很有可能影响诸多厂商的多款产品使工业生产过程面临严重威胁。出于此目的，笔者从2021年开始研究Codesys
V2相关产品并发现了数十个漏洞，提交给厂商后经过修改发布了最新修复版本，详情请见链接[1]所示。Codesys
V2产品设计理念只关注了功能业务在信息安全方面涉及较少。目前主推的Codesys
V3产品宣称加入了信息安全的设计考量，那么是不是就无懈可击呢？本文就带领大家看看笔者是如何从Codesys厂商的安全通告出发一步步发现多个漏洞的。

## 信息收集

先打开Codesys厂商的安全通告网站，浏览相关安全通告。

![1691411897_64d0e5b9bdd7952f7e993.png!small?1691411898528](https://image.3001.net/images/20230807/1691411897_64d0e5b9bdd7952f7e993.png!small?1691411898528)

2023-2的这份通告[2]吸引了笔者的注意力，其中包含了大量的漏洞而且都是通信协议相关，最重要的是暴露了很多敏感信息让我们可以从中分析出很有价值的信息。下图为CVE编号总数为16个，且影响的是V3.5.19.0以前的所有版本的多个通信组件。

![1691411930_64d0e5dad9d248c853110.png!small?1691411931669](https://image.3001.net/images/20230807/1691411930_64d0e5dad9d248c853110.png!small?1691411931669)

从通告中选取存在CVE编号最多的一个组件开始详细分析，这些漏洞的类型为栈溢出，影响组件名称为CmpTraceMgr。可以得出结论：在Codesys
V3.5.19.0之前版本中CmpTraceMgr组件存在多个地方的栈溢出漏洞。

![1691411958_64d0e5f6366339ea6e110.png!small?1691411958555](https://image.3001.net/images/20230807/1691411958_64d0e5f6366339ea6e110.png!small?1691411958555)

接下来我们的思路如下：

  1. 搭建Codesys V3.5.19.0之前任一版本和该版本环境，从Codesys V3自带模拟器control win V3出发分析在CmpTraceMgr组件中修改了哪些存在栈溢出风险的代码
  2. 在存在漏洞的Codesys模拟器环境下构造报文进行漏洞复现和分析；
  3. 学习2023-2安全通告中微软研究人员的相关思路，在修复后的版本模拟器中挖掘漏洞；

## 环境搭建

在Codesys厂商官网下载受影响的版本Codesys V3.5.18.20

![1691412044_64d0e64c4673cde06bce0.png!small?1691412044925](https://image.3001.net/images/20230807/1691412044_64d0e64c4673cde06bce0.png!small?1691412044925)

将其安装在Windows 10虚拟机中，安装后启动模拟器，并且在x64dbg工具中将其进程附加，如下所示

![1691412086_64d0e6767d51330791e00.png!small?1691412086818](https://image.3001.net/images/20230807/1691412086_64d0e6767d51330791e00.png!small?1691412086818)

由于模拟器使用了威步wibu的安全解决方案因此需要利用插件从内存中对其dump后进行整体分析

![1691412117_64d0e695eb1228923afad.png!small?1691412118271](https://image.3001.net/images/20230807/1691412117_64d0e695eb1228923afad.png!small?1691412118271)

同样，我们还需要下载修改漏洞后的版本Codesys V3.5.19.0软件并在另外一个虚拟机上安装，安装后同样进行dump内存操作。

将2个dump后的内存文件分别保存，以备后续步骤使用。准备两个不同版本的模拟器后，还需要搭建一个IDE开发环境，给两个模拟器中分别下装简单的测试工程，如下所示。

![1691412168_64d0e6c82b61b173b116b.png!small?1691412169148](https://image.3001.net/images/20230807/1691412168_64d0e6c82b61b173b116b.png!small?1691412169148)

## 漏洞点定位

将前述的两个dump文件导入至IDA进行分析，首先对Codesys
V3.5.18.20的CODESYSControlService_dump.exe进行分析。

  1. 通过字符串定位CmpTraceMgr组件位置，直接利用CmpTraceMgr字符串定位发现存在诸多困难，比如字符搜索“CmpTraceMgr”出现的引用较少，函数之间也没有引用关系，或者利用引用字符串搜索出现的调用有太多，如下所示

![1691412270_64d0e72e34b0394d4b7ad.png!small?1691412271346](https://image.3001.net/images/20230807/1691412270_64d0e72e34b0394d4b7ad.png!small?1691412271346)

基于此需要变换策略，有两个思路：A.搭建环境，在IDE编程软件中添加trace功能，执行多项操作，抓取报文从报文信息出发进行关键词搜索；B.利用Codesys
V3带有符号的固件代码进行比对快速定位关键点；

2\. 基于1步骤提出的B思路，从某个使用了Codesys V3
Runtime的固件（带有符号表）中比对搜索CmpTraceMgr，再在关键位置找到特征字符串后，利用该字符串在5.18.20模拟器dump分析文件中进行搜索。如下图是在带有符号表的固件中搜索结果

![1691412393_64d0e7a98f39f97bafdf1.png!small?1691412394082](https://image.3001.net/images/20230807/1691412393_64d0e7a98f39f97bafdf1.png!small?1691412394082)

再在该函数中寻找特殊字符“Creating events failed”

![1691412428_64d0e7cc101d1b680f5b5.png!small?1691412428345](https://image.3001.net/images/20230807/1691412428_64d0e7cc101d1b680f5b5.png!small?1691412428345)

接下来利用特殊字符在目标文件中进行搜索，并且可以对照带有符号表的固件对目标文件进行函数重命名；

3\. 利用Creating events failed作为特征字符搜索定位

![1691412481_64d0e8018893f1499693b.png!small?1691412481870](https://image.3001.net/images/20230807/1691412481_64d0e8018893f1499693b.png!small?1691412481870)

在该函数中寻找CmpTraceMgr处理部分，最终定位到函数为TraceMgr的处理部分，如下所示

![1691412512_64d0e820c0cd0119a5683.png!small?1691412512971](https://image.3001.net/images/20230807/1691412512_64d0e820c0cd0119a5683.png!small?1691412512971)

4\.
熟悉TraceMgr整个函数处理流程，再次打开5.19.0的CODESYSControlService_dump.exe分析文件，分析过程如前所述，找到TraceMgr处理函数后，逐个过程比对每个流程中的函数实现的差异点。按照如上思路，在TraceMgrSrvPacketCreate函数中找到了差异点，下图是V3.5.18.20的TraceMgrSrvPacketCreate处理部分，当输入参数为19、20、21等值时，进入mencpy分支

![1691412652_64d0e8ac2a15d6150f497.png!small?1691412652480](https://image.3001.net/images/20230807/1691412652_64d0e8ac2a15d6150f497.png!small?1691412652480)

但是对比V3.5.19.0的TraceMgrSrvPacketCreate处理部分时发现其对该部分做了特殊处理（对输入的内容做限制长度），并且使用的BTagReaderGetContent函数都是特殊封装后的，因此可以断定是由于使用了memcpy函数并且未对输入参数进行检查验证出现的栈溢出漏洞。

![1691412700_64d0e8dc574e31d7612a5.png!small?1691412700530](https://image.3001.net/images/20230807/1691412700_64d0e8dc574e31d7612a5.png!small?1691412700530)

## 漏洞复现及分析

基于前述的分析，我们要复现漏洞首先需要了解Codesys V3通信协议相关的基础知识，该部分可以参考看雪论坛中的文章《Codesys V3
协议及授权机制分析》。要触发该漏洞，需要经过如下通信流程：

  * 打开通道，此时模拟器会给客户端返回channel_id,该值在后续的通信中会用到；
  * 创建会话连接，模拟器会给客户端返回session_id，同样该值在后续的请求报文中需要携带；
  * 获取challenge值，用来进行授权验证相关算法使用；
  * 发送授权后的登录请求，输入正确的用户名和密码才可进行敏感操作；
  * 发送应用程序的登录请求，此时模拟器会返回op_key，后续的敏感操作还需要携带该值；
  * 至此才可以发送服务码为TraceMgrServic群组中子功能码为TraceMgrSrvPacketCreate的PoC攻击报文；

![1691413025_64d0ea210fb0a83ff1658.png!small?1691413025622](https://image.3001.net/images/20230807/1691413025_64d0ea210fb0a83ff1658.png!small?1691413025622)

发送攻击报文后，在调试模式下分析漏洞根因。发送报文payload部分填充0x18ac个A，可以看到在memcpy之前目的地址片区布局正常。

![1691413112_64d0ea78751f50c3511b3.png!small?1691413113131](https://image.3001.net/images/20230807/1691413112_64d0ea78751f50c3511b3.png!small?1691413113131)

当执行完memcpy之后内存布局如下所示，栈上空间全被AAAA填充。基于此漏洞后续还可以做漏洞利用，在栈上构造指向“目标”函数的指针已达到远程代码执行的效果，本文中不再深入讲解。

![1691413156_64d0eaa4eaa6fc8157e2b.png!small?1691413157359](https://image.3001.net/images/20230807/1691413156_64d0eaa4eaa6fc8157e2b.png!small?1691413157359)

## 漏洞复现及分析

在第五章讲述的基础上结合2023-02的安全通告，我们继续可以深入各个服务群组的各个子功能码进行协议模糊测试，服务群组信息如下所示

![1691413223_64d0eae7dd9fd05e31802.png!small?1691413224471](https://image.3001.net/images/20230807/1691413223_64d0eae7dd9fd05e31802.png!small?1691413224471)

比如我们可以深入AppServiceHandler中的各个子功能码函数进行测试，构造进入各个分支函数的报文进行模糊测试。由于Codesys
V3协议对象层次清晰，报文结构有研究机构已经披露[3],因此可以采用基于生产的模糊测试进行漏洞挖掘工作，推荐采用boofuzz框架，可以参考claroty开源的OPC
UA模糊测试程序[4]来适配Codesys V3协议的模糊测试。

![1691413286_64d0eb26222acd42b7e19.png!small?1691413287390](https://image.3001.net/images/20230807/1691413286_64d0eb26222acd42b7e19.png!small?1691413287390)

笔者采用多种模糊测试技术已经在修改后的版本V3.5.19.0模拟器上发现了多个漏洞并且将这些漏洞上报给国家相关单位。

在2023年8月10日的Blackhat USA会议上，微软的研究人员将分享他们发现Codesys
V3协议16个漏洞的相关议题，感兴趣的朋友可以围观。笔者在该议题开讲之前先在国内对Codesys V3协议漏洞的分析和发现方法做一分享，让大家提前预热。

![1691413352_64d0eb68b6562fc7b2c0e.png!small?1691413353638](https://image.3001.net/images/20230807/1691413352_64d0eb68b6562fc7b2c0e.png!small?1691413353638)

## 防护措施

由于Codesys V3现在广泛应用在各大工控厂商的产品中，因此这些漏洞的影响范围较广，工控系统用户应做好积极防护措施。

  1. 将受影响的产品放置于安全防护设备之后，做好网络安全的纵深防御策略；
  2. 当需要进行远程访问时，尽量采用安全的VPN网络，并且做好访问审计；
  3. 关注受影响厂商的安全补丁，经过测试后升级受影响的产品以使其免受威胁。
  4. 尽量减少受影响设备的私有通信端口暴露，可根据业务场景选择关闭1740/1741/1742/1743/11740/11741等端口；
  5. 尽量给受影响的控制器设置用户名和密码保护，设置保护策略后攻击难度提升必须要获取用户名和密码后才能执行攻击；
  6. 建议使用Codesys V3 runtime的工控厂商及时自查，并且积极修复，发布修复版本的固件；

## 总结

本文以在国际上广泛使用的Codesys V3为研究对象，从Codesys厂商安全通告出发进行信息搜集和分析
，进行了漏洞复现和分析，并且在修改过后的版本中发现了新的漏洞，以此来阐述对于工控安全研究的思路和方法，也让更多对于保护工业系统安全的有识之士能够看到并且共同守护工控系统的安全。

## 相关链接

[1]：<https://github.com/ic3sw0rd/Codesys_V2_Vulnerability>

[2]:
[https://customers.codesys.com/index.php?eID=dumpFile&t=f&f=17554&token=5444f53b4c90fe37043671a100dffa75305d1825&download](https://customers.codesys.com/index.php?eID=dumpFile&t=f&f=17554&token=5444f53b4c90fe37043671a100dffa75305d1825&download)=

[3]: [https://ics-cert.kaspersky.com/publications/reports/2019/09/18/security-research-Codesys-runtime-a-plc-control-framework-part-2/](https://ics-cert.kaspersky.com/publications/reports/2019/09/18/security-research-codesys-runtime-a-plc-control-framework-part-2/)

[4]:
[https://github.com/claroty/opcua_network_fuzzer﻿](https://github.com/claroty/opcua_network_fuzzer)

