作者：[腾讯科恩实验室](https://mp.weixin.qq.com/s/LFh5cxWKt0ev7E2OA_5_0g "腾讯科恩实验室")

#### 背景介绍

OTA（Over-The-Air）是汽车行业智能网联变革的核心能力之一。本次Black Hat USA
2018上，腾讯科恩实验室带来了2017年对特斯拉具备的先进OTA功能相关的安全研究成果。本成果对于促进汽车行业安全稳定落地智能网联化具有重大积极作用，同时本次议题也是全球首次涉及对汽车先进驾驶辅助系统（ADAS，特斯拉相关系统名为：Autopolit）的信息安全研究成果披露。更多详细信息请关注腾讯科恩实验室官方微信号：KeenSecurityLab，并回复“车联网安全”即可获得此次研究技术细节白皮书。

![](https://images.seebug.org/content/images/2018/08/67c52b63-59dc-45a5-acdf-30cc17ed4839.png-w331s)

#### 议题概要

腾讯安全科恩实验室在2016年和2017年，在避免物理接触汽车的远程攻击场景下，连续两年针对特斯拉Model S和Model
X进行了攻击测试。在去年举办的Black Hat
USA大会上，科恩实验室的研究人员介绍了2016年特斯拉公司对其研究成果的致谢中所包含的具体细节，并向与会者展示了一系列Tesla汽车的安全漏洞，获得了与会者的好评。此外，借助灯光舞蹈秀的形式展示了利用2017年发现的另一批漏洞攻击的威力，但相关漏洞的细节并未公布。今年，该议题将会进一步介绍2017年彩蛋视频背后涉及到的技术细节。除了介绍特斯拉的由云端主导的空中升级（OTA）机制，并展示一些攻击链中开发的新技术外，该议题还将着重介绍测试过程中发现的多个严重的安全漏洞。

![](https://images.seebug.org/content/images/2018/08/9ccc72b6-3a8c-4f55-b0c6-edd62908503c.png-w331s)

#### 作者简介

刘令，腾讯科恩实验室研究员，专注于逆向工程、漏洞挖掘、漏洞研究等技术，多次参与特斯拉等汽车的安全研究。曾在QEMU和XEN中发现多个虚拟化漏洞，同时也是一名CTF爱好者。

![](https://images.seebug.org/content/images/2018/08/017d4cef-abe3-4013-b9dc-eb9e7fe7a6af.png-w331s)

张文凯，腾讯科恩实验室研究员，多次参与特斯拉、宝马等汽车安全研究项目，主要负责汽车CAN网络和汽车固件分析工作，有丰富的嵌入式系统软件开发经验，熟悉ECU设计过程和汽车CAN网络结构。

![](https://images.seebug.org/content/images/2018/08/49fb644c-f921-47ab-bdb3-b5999ed75d76.png-w331s)

杜岳峰，腾讯科恩实验室研究员，多次参与特斯拉汽车安全研究，对逆向工程和恶意软件分析领域有着浓厚的兴趣。

![](https://images.seebug.org/content/images/2018/08/eb08e748-b168-44b6-845b-f570736ff851.png-w331s)

#### 议题解析

在今年的Black Hat
USA大会上，我们向大家介绍2017年的攻击链中相关漏洞的细节，并分享使用这些漏洞是如何完成灯光秀的。此外，自动驾驶系统的安全性已经成为一个新的热点话题，我们则会向大家展示在特斯拉车上，对辅助驾驶模块（即Autopillot，也称APE）的安全研究成果。最后，和以往一样，我们将会介绍特斯拉对相关漏洞的修复结果，并再一次强调只有安全研究者、安全社区和设备厂商互相合作，才能有效的提高整体安全水平。

![](https://images.seebug.org/content/images/2018/08/24fe3ff3-5e1e-41fb-8798-c3976643f959.png-w331s)

攻击过程中涉及到的部分硬件单元和连接方式如下图所示。在去年，我们利用了两个Webkit中存在的漏洞，实现了浏览器中的任意代码执行。今年的情况和去年类似，整个攻击过程依然是从一个Webkit漏洞开始的。

![](https://images.seebug.org/content/images/2018/08/387b723d-c2bf-42f2-a679-3b065caf7ffc.png-w331s)

CID上具有一个Webkit内核的浏览器，在漏洞报告时，该浏览器仍保持为534.34版。该版本的Webkit内核中，存在一个UAF漏洞，下图即是该漏洞的PoC代码：

![](https://images.seebug.org/content/images/2018/08/e66e55c5-795c-4a8b-8927-a2414508f88a.png-w331s)

这个漏洞存在于对SVGTransformList元素的操作过程中。该元素内部存在多个SVGTransform实例，这些实例的SVGMatrix结构会存储在一个Vector里。当SVGTransformList的Initialize或clear方法被调用后，Vecotr被释放，但访问Vector中Matrix的指针仍然存留。利用该UAF漏洞，经过精心的内存布局之后，即可借助ArrayStorage、Uint32Array等结构的特性实现对内存的任意读和任意写，并从而实现了浏览器中的代码执行。

![](https://images.seebug.org/content/images/2018/08/d667aa16-cb5b-4c1d-9b24-69cac2c58d8d.png-w331s)

获取了浏览器的权限之后，下一步操作就是突破内核和其他安全防护措施对浏览器的限制，从而得到root
shell。2016年，我们是通过利用Linux内核中的一个漏洞实现该目的的，但在2017年，由于特斯拉修复了相当多的内核漏洞，我们不得不寻找新的漏洞。

在2017年的车机固件中，浏览器进程只能访问/dev/nvmap和/dev/nvhost-ctrl两个文件，这两个文件都是用来与英伟达Tegra芯片进行通信的驱动接口。在和这两个接口相关的代码中，我们发现了一处漏洞，该漏洞可使我们从用户空间对内核空间的任意内存地址减1。

![](https://images.seebug.org/content/images/2018/08/b7cd17bf-7af1-4121-8ba7-7908cf23cdc3.png-w331s)

这一漏洞存在于NVMap驱动中，当处理命令NVMAP_IOC_PIN_MULT时，由于对用户提供的指针数组验证不当，当其中包含一个非法结构时，非法结构体的引用数会被减1，而这个引用数的指针是用户态可控的。这意味着，用户态可以对内核态的任意内存地址减1。利用这一漏洞，结合Kernel中的其他gadget，我们可以对内核空间中的任意地址进行读写操作。之后对相关的syscall和AppArmor配置进行篡改，即可拥有root
shell。

![](https://images.seebug.org/content/images/2018/08/ce9bf96f-b86d-46be-8653-6df2e280512f.png-w331s)

得到root
shell证明CID已被完全攻破，下一个目标则是网关。2016年我们报告了网关上的一些设计缺陷，特斯拉在收到报告后对相关漏洞进行了修复，通过加入签名机制，对网关上的升级软件传输操作进行了限制，未签名的升级软件将不能被传输到网关上，因此理论上使用非物理攻击方法是无法传输篡改后的升级软件的。

但在对新软件进行安全审计的过程中，我们发现，升级过程中存在行为不一致的问题。如下图所示，尽管网关的文件传输协议限制了直接传输升级软件的操作，名为”boot.img”的升级软件无法直接传输到网关上，但文件系统的重命名行为和文件传输协议的重命名行为不一致。文件系统会忽略目标文件名首部的空格，导致目标文件名“\x20boot.img”会被文件系统理解为”boot.img”，从而绕过了升级软件对文件名的检查。

![](https://images.seebug.org/content/images/2018/08/30500cc6-fdac-481c-a65d-8bf356e4a7bf.png-w331s)

用这种方法刷入我们修改后的升级软件后，重启网关，使其执行升级软件，即可在网关上执行我们修改后的升级代码，植入后门，或绕过原有升级软件对固件签名的检查。

此外，我们还对整个OTA升级过程进行了研究。特斯拉的OTA升级过程大致可由下图所示的几个关键步骤描述。

![](https://images.seebug.org/content/images/2018/08/f7743e67-0050-44ec-8f7a-9a758d644e29.png-w331s)

云端通过特斯拉自有的握手协议下发固件下载地址后，特斯拉CID上的cid-updater会从云端下载固件，进行解密，并校验其完整性。之后通过类似于A/B
Update的方式，车内其他强运算力的联网组件（如IC、APE等）根据cid-updater提供的固件文件进行升级。

![](https://images.seebug.org/content/images/2018/08/7b7a5633-2eed-4627-9479-72855c7a26ff.png-w331s)

此外，cid-updater还会负责根据固件包中的目录信息，与车辆配置做比照，据此产生release.tgz文件，并和上文提到过的升级软件boot.img一同提供给网关，网关执行上述升级软件，更新在网关上连接的二十余个ECU。

为了展示我们对车电系统整体的理解，我们对特斯拉在2016年年末推出的彩蛋功能进行了自定义修改和展示。下图是彩蛋过程中几个重点参与活动的ECU：

![](https://images.seebug.org/content/images/2018/08/deb70b8b-f1ee-4df2-9818-1f5492c43e65.png-w331s)

首先，CID会发送启动信号，触发这一过程，信号会被发送至BCCEN，该控制器对相关硬件进行初始化操作后，会确认目前车辆是否准备好启动彩蛋，并等待钥匙的按键信号。按键后，CID开始播放音乐，同时BCCEN以及其他ECU会按照各ECU中存储的动作表，控制各组件按照预定计划动作。

因此为了实现自定义彩蛋功能，我们在CID中动态修改了多个检查点，并对ECU固件中的动作表进行了修改，将修改后的固件刷入了ECU中。

![](https://images.seebug.org/content/images/2018/08/1eeb1367-4a3e-49f7-ad0b-d5f63aeba292.png-w331s)

最后，作为对前沿技术的一个尝试，我们研究了ape-updater中的安全漏洞。该程序作为特斯拉OTA框架中的一部分，负责整个APE系统的更新。

![](https://images.seebug.org/content/images/2018/08/6488e7ce-3cd2-43f9-9637-f547a82077ec.png-w331s)

该程序提供了两个业务端口，其中25974端口提供了一个交互式shell和多种命令，可供CID进行控制；28496端口可通过一个HTTP服务器提供其他组件需要的文件。

![](https://images.seebug.org/content/images/2018/08/0069c67c-fae3-40d5-b288-7b8a096370fd.png-w331s)

在25974端口提供的handshake命令中，会从服务器请求一个JSON字符串，并稍后提供给install命令解析。在某个特定版本的特斯拉APE固件中，我们发现了名为m3-factory-deploy的命令，该命令可覆盖handshake返回的JSON，从而让攻击者提供的JSON被解析。

![](https://images.seebug.org/content/images/2018/08/1ee0ccd3-73bc-442d-a096-00adcfa3c4ac.png-w331s)

利用JSON中存在的self_serve键值，可以要求APE将/var/etc/saccess/tesla1这一文件暴露在HTTP服务器下，从而可得到其内容。利用其为凭据，可通过25974端口得到ape-updater中自带的命令执行权限，可以重新开启SSH，并以root权限在APE上执行任意程序。

![](https://images.seebug.org/content/images/2018/08/0c70c18e-7294-4e29-b781-91ad9550debf.png-w331s)

在上述所有漏洞报告给特斯拉后，特斯拉做出了及时的反应，其中包括：

  * 修复Webkit漏洞
  * 与英伟达共同修复NVMap中的内核漏洞
  * 修复Gateway中的漏洞

我们还注意到特斯拉在其系统安全性上不断地进行改善与提高，比如：

  * 更严格的iptables限制
  * 对OTA框架中的几个关键程序进行进一步加固
  * 降低saccess文件夹中token的权限
  * 禁止系统降级
  * ……

我们认为在这一过程中，特斯拉专业的安全响应团队和他们的OTA机制起到了关键的作用，防止了车主受到进一步的威胁。

![](https://images.seebug.org/content/images/2018/08/72250d73-5f5d-40a8-83ef-3d6649df9414.png-w331s)
![](https://images.seebug.org/content/images/2018/08/d8f48c05-ad30-405a-a0be-86fe3415c63f.png-w331s)

由于篇幅所限，对相关漏洞我们只介绍了类型和核心原理，对我们的研究感兴趣的朋友可以查看我们发布的白皮书[《穿云拨雾：对特斯拉汽车网关、车身控制模块以及辅助驾驶（Autopilot）ECU的渗透测试》](https://share.weiyun.com/5v6B2md
"《穿云拨雾：对特斯拉汽车网关、车身控制模块以及辅助驾驶（Autopilot）ECU的渗透测试》")获取更多信息。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/664/>

