作者：启明星辰ADLab

#### 一、威胁概述

近期，思科Talos团队因情况紧急提前公开了一项未完成的研究，该研究提及了一个可能对全球网络产生重大危害的高级威胁攻击(大约有50万台设备受到感染)，由于其核心模块文件为VPNFilter，故该恶意代码也被命名为”VPNFilter”。该攻击是一起以入侵物联网为载体从事可能由国家发起的全球性的高级恶意软件攻击，恶意软件通过三个阶段来部署其攻击武器，目前已经有至少50万台设备受到感染。攻击者利用该恶意软件来控制并监视处于工控网络、办公环境中的网络设备(包含路由器、网关、防火墙以及其他的物联网设备)，其支持工控网络情报收集、重要敏感的流量(登录凭证)截取、流量篡改、定向JS注入、设备破坏性攻击等功能。

恶意软件在5月8日出现大规模的以乌克兰为主要目标的攻击活动，并且在5月17日乌克兰的受感染设备出现大幅度增加，这些受感染设备均受控于C&C
46.151.209.33,
看起来此次攻击目标似乎瞄准乌克兰。乌克兰电力系统曾经受到过两次黑客攻击，并且导致了停电事故，两次攻击均以持久而隐秘的渗透手段入侵到目标。而这次的攻击活动以物联网入口，利用大量存在漏洞的物联网设备作为载体进行撒网式攻击，并且以惊人的速度感染了至少50万台设备，其中包含有华为、中兴、华硕、Dlink、Ubiquiti、UPVEL、Linksys、MikroTik、NETGEAR
和 TP-Link等设备。同样，此次恶意代码与2015年攻击乌克兰电网的BlackEnergy使用相同的变形RC4算法对关键信息进行加密；并且与之类似的是同样也有对主机设备进行重要数据擦除与重启的连环动作以达到让设备无法启动的目的(同时也提高了取证的难度)。

启明星辰ADLab发现该预警后对该恶意软件进行了深入的分析，以剖析其实现机制。我们发现该恶意软件中除了采用图片文件的EXIF数据传输用于下载恶意代码核心组件的C&C外，还采用HTTP头中的location和direct字段传输该C&C，甚至采用了一种我们称之为”SYN隧道技术”的高级隐藏技术来实现恶意软件C&C的被动更新，即使如之前所报道那样，FBI阻断了该恶意软件的C&C，该技术也可以让该恶意软件快速复活。其中第三阶段恶意组件专门针对TCP协议进行嗅探处理，不仅对工控modbus
SCADA协议进行情报收集，同时还会嗅探基于http协议的登录凭证信息和Authorization信息。该嗅探模块需要黑客远程指定modbus服务器进行精确的监控，以发现所有连接的从机设备。此外，在最近公开的攻击插件模块中还可以看出，该次攻击可用于广泛的情报收集以及对特定目标进行渗透攻击，其中包含对80端口的流量重定向、强制转换HTTPS为HTTP以方便流量监控、窃取HTTP请求包中的登录凭证信息、向指定网站的响应数据中注入恶意javascript脚本等等。

#### 二、恶意软件工作原理

该恶意软件通过利用路由器、网关、防火墙等物联网设备漏洞进行广泛的感染和传播。在感染设备中，其首先启动一个Loader模块执行，该模块主要实现了VPNFilter组件的下载与执行。Loader模块并不是直接通过指定的下载地址来下载VPNFilter组件，而是通过多种技术手段来获取VPNFilter的下载地址(存储点)。其首先会向服务器photobucket.com发送请求并尝试解析响应数据中的Locaion、direct、图片EXIF信息来获取；如果失败则向服务器taknowall.com发送请求并解析图片的EXIF来获取；如果仍然无法获取到C&C，则会采用”SYN隧道技术”来获取C&C实现下一个阶段组件的下载地址。此外，VPN存储点获取成功后，Loader通过内置SSL证书文件来验证下载VPNFilter组件。

![](https://images.seebug.org/content/images/2018/06/780a4c81-f9f8-4b55-801a-89fcf94414bf.png-w331s)

VPNFilter组件最后会被下载到”/var/run/”目录下，是该类恶意攻击的核心组件，通过该组件，恶意软件得以驻留在被感染系统中。VPNFilter组件为攻击者提供了一个用于维护僵尸网络的框架，攻击者可以基于不同的攻击目的加载不同的插件和执行不同远控控制命令。目前所发现的插件模块有：一个用于支持连接到Tor网络的Tor
客户端（Tor Client,文件tor）；一个为嗅探登录凭证和Modbus工控协议信息的TCP流量嗅探模块（TCP Traffic
Sniffer，文件ps）;一个专门为HTTP 80端口进行流量监控、截取、篡改、注入的HTTP 流量监控模块（HTTP Traffic
Controllor，文件ssler）；以及可用于破坏设备使其无法重启、无法取证的设备破坏模块（Destroy
Module，文件dstr），此外其还存在其他的模块如：mikrotik.o、torrc、ip_tables.ko、iptable_filter.ko、iptable_nat.ko。

#### 三、恶意软件剖析

根据该恶意软件执行攻击的步骤，可以将其划分为三个阶段，其中Loader文件为第一个阶段的恶意模块，VPNFilter文件为第二阶段的恶意模块，Tor客户端和流量嗅探器为第三阶段的恶意模块。以下分别对这三个阶段的恶意代码进行深入的剖析。

##### 第一阶段：感染设备并下载恶意代码主体执行

第一个阶段的样本可以看作是一个Loader（文件名为msvf），攻击者利用设备漏洞将其落地到设备内存中运行。该Loader主要目的是从C&C服务器上下载第二阶段的恶意组件执行。该Loader不同于以往的物联网恶意代码那样将C&C内置于代码内，而是通过在合法图片网站上下载一张隐藏有C&C地址的图片进行解析，从而得到真实的C&C。而恶意代码为了防止流量追踪，采用socks5代理、Tor、以及ssl的方式进行该图片的下载。如果图片下载失败，也会采用极其隐蔽的原始流量数据嗅探的方式来获取C&C。

同时该模块还试图修改NVRAM并将自身加入定时任务文件”crontab”中，以达到常驻的目的。一般物联网恶意代码如mirai等没有涉及常驻机制，使得其在设备重启后会消失。

1.两次创建子进程并且启用恶意代码对当前用户组的读写执行权限

第一阶段样本执行后，会fork两次，第一次用于清理进程资源启用读写执行权限。

![](https://images.seebug.org/content/images/2018/06/6841d0f8-ff26-4075-95a2-1fdce12035be.png-w331s)

第二次fork会在子进程中确认进程文件是否存在，如果不存在会进行文件的回写，防止进行文件丢失。

![](https://images.seebug.org/content/images/2018/06/e0ed8dee-2200-401e-955d-454c23808ebb.png-w331s)

此外在第二次fork的子进程中，恶意代码为了防止自身文件在设备重启后消失，还会将自身文件加入到crontab文件末尾，以实现开启启动、常驻设备的目的。

![](https://images.seebug.org/content/images/2018/06/629d6fcb-da00-449c-8a7a-2330aa4827c2.png-w331s)

2.解密证书文件名、图片链接数据等内容

接下来恶意代码会通过变形的RC4算法来解密后续要用到的字符串和数据，变形RC4秘钥为`“%^:d”`，最新版本已经更新为`“g&*kdj$dg0_@@7’x”`。

![](https://images.seebug.org/content/images/2018/06/76074604-3d05-4f80-86e8-af288c98b209.png-w331s)
![](https://images.seebug.org/content/images/2018/06/bd18467f-1950-4927-b73e-b0c0df3c5ad9.png-w331s)

变形RC4的stable数据如下：

![](https://images.seebug.org/content/images/2018/06/70f052f4-9e61-4cd4-bc01-3a4adc64b4d0.png-w331s)

最后解密得到如下信息，其中包含证书文件名、版本号、build信息、图片url等。

![](https://images.seebug.org/content/images/2018/06/853d01c9-ea96-47ca-8fe5-005c5e8f2e60.png-w331s)
![](https://images.seebug.org/content/images/2018/06/8f594f60-27d7-40fc-b0c6-2f8ba22afefe.png-w331s)
![](https://images.seebug.org/content/images/2018/06/714a83b7-7a11-4a97-a58d-df21ecace13a.png-w331s)
![](https://images.seebug.org/content/images/2018/06/10ef7c4e-e2a3-4969-81ab-ef8906b1310e.png-w331s)
![](https://images.seebug.org/content/images/2018/06/941b0586-9584-461c-813d-87769e918d8d.png-w331s)
![](https://images.seebug.org/content/images/2018/06/1d9c4f8d-b947-4c29-87b4-4874082ce7df.png-w331s)
![](https://images.seebug.org/content/images/2018/06/4e0aad36-90b2-46af-bc89-c07494a1ce09.png-w331s)

解密url：

![](https://images.seebug.org/content/images/2018/06/8c63be92-80a7-4618-9dbd-d5d2ff6423b4.png-w331s)
![](https://images.seebug.org/content/images/2018/06/c039b2ca-5bc6-43f8-9b2f-b0d43c6c27f0.png-w331s)
![](https://images.seebug.org/content/images/2018/06/806ad2b4-320d-4a00-88f2-062507bb9c89.png-w331s)
![](https://images.seebug.org/content/images/2018/06/c68e563e-09c2-452b-9363-094758648f35.png-w331s)
![](https://images.seebug.org/content/images/2018/06/c8d0bf13-10de-4855-9af4-78b544c5fb03.png-w331s)

3.创建ssl证书文件以及恶意代码版本文件

解密完成后，恶意代码会将代码中内嵌的公钥、私钥数据存储在证书文件中。该恶意代码中存放有三个证书数据，其中两个公钥和一个私钥，公钥存储在文件`“/var/run/client_ca.crt”`和`“/var/run/client.crt”`中，私钥存储在文件`“/var/run/client.key”`中。

![](https://images.seebug.org/content/images/2018/06/aa8e9b01-e7df-4819-ae5b-370fc4733e72.png-w331s)

此外，版本信息0.3.9qa会被写入到文件/var/run/msvf.pid中。

![](https://images.seebug.org/content/images/2018/06/c20cfdaf-7aec-4b43-9400-8acbd5005575.png-w331s)

4.下载第二阶段组件

第二阶段的恶意代码下载地址采用三种方式获取。首先尝试从photobucket网站请求C&C，具体按照如下链接顺序去下载并提取第二阶段恶意代码的服务器地址。

<http://photobucket.com/user/nikkireed11/library>  
<http://photobucket.com/user/kmila302/library>  
<http://photobucket.com/user/lisabraun87/library>  
<http://photobucket.com/user/katyperry45/library>

虽然当前这些链接已经失效，但是通过逆向可以看出，如果请求响应码为302，恶意代码则会从响应数据中的”Location”/”location”参数中提取出第二阶段恶意代码的下载地址。

![](https://images.seebug.org/content/images/2018/06/3d21a996-e7ae-4f31-907f-f5729a0ced08.png-w331s)

如果恶意代码请求的响应码为200，则会从请求的响应数据包的HTTP头部中提取”direct”参数的值，作为第二阶段恶意代码下载地址。

![](https://images.seebug.org/content/images/2018/06/d3216b09-eae4-4252-8379-c426ebb9784b.png-w331s)

如果不存在该值，则会从图片文件中的EXIF域提取经纬度数据并将其转换为第二阶段恶意代码下载的IP地址。下载的图片文件EXIF部分数据类似下图。

![](https://images.seebug.org/content/images/2018/06/a56a6ae0-fb22-4a7b-9b63-862c56194c39.png-w331s)

处理代码如下：

![](https://images.seebug.org/content/images/2018/06/0f3669a2-c033-4c1d-902a-9c57a1cb9bd6.png-w331s)
![](https://images.seebug.org/content/images/2018/06/a6eb99a4-b9a5-4cb3-9264-644ba22362a3.png-w331s)
![](https://images.seebug.org/content/images/2018/06/9f13eb44-0fee-4f52-afe7-72f56a470785.png-w331s)

如果以上情况均失败，恶意代码还会尝试请求如下链接，该链接也是一张图片，和上面方法一样从EXIF中提取经纬度并处理得到下载地址。

<http://taknowall.com/manage/content/update.php>

如果上面的所有方式都尝试后依然无法成功获取C&C地址，恶意代码会通过链接<http://api.ipify.org?format=json>获取到当前设备的外网IP地址，然后嗅探当前设备的原始网络流量数据，并试图从这些流量数据中过滤出符合特定格式的网络数据包，如果满足格式要求，便会从该数据中提取出第二阶段恶意代码的下载地址。其中过滤包时需满足如下条件：

  1. 原始数据流长度必须大于0x3D
  2. 数据包必须为TCP包
  3. 数据包的SYN必须被设置
  4. 目的IP必须为当前设备的公网IP
  5. Tcp Option的MSS(Maximum Segment Size) 必须为0c 15 22 2B（实际上为非法MSS）

如果满足以上条件，则从MSS之后的4个字节提取出C&C的IP地址。我们将这种以SYN
TCP数据流作为数据传输的技术成为”SYN隧道技术”。利用该种技术来传输C&C地址不仅能够很好隐秘黑客的踪迹(无需在恶意代码逆向或者网络存储点上暴露黑客C&C地址)，而且能够灵活的变换C&C，非常难以被发觉。因此，可以说样本中任何内置C&C或者存储C&C的存储点被处置后，该恶意代码仍然可以受控于黑客。这给执法部门处置该恶意代码带来了巨大挑战。原始流的部分判定代码如下：

![](https://images.seebug.org/content/images/2018/06/16aa33d5-6bfb-422a-8b96-70582e1b3890.png-w331s)

如果以上任何一种方式能够成功获取到下载地址并且下载组件成功，恶意代码便会直接执行所下载恶意代码，然后退出。下载的第二阶段的恶意代码被保存为文件”/var/vpnfilter”。

![](https://images.seebug.org/content/images/2018/06/1b7ee0b2-1978-4dd9-a1b7-a2625ced21a5.png-w331s)

##### 第二阶段：控制命令接收、分发、执行

该样本以实现后门控制为目的，其主要用于连接控制端服务器，接收控制命令执行相应的功能控制。样本首先为了确保运行实体的唯一性，会绑定1386端口。如果该端口被占用便会终止运行。此外在新版本中不再通过这种容易自我暴露的方式来做唯一性判定，并且添加了自我删除的功能。

![](https://images.seebug.org/content/images/2018/06/9a824dce-83fc-4e55-8449-b32aff6baec2.png-w331s)

如果绑定成功，便会进入核心工作代码中执行。首先为了防止因CPU资源不足、平台兼容性等问题导致无法工作或者退出，其还注册了大量异常信号用于自我复活。

![](https://images.seebug.org/content/images/2018/06/d4ad3bf7-0bc4-415c-9aaa-0e0577c4cb68.png-w331s)

然后采用同样的变形RC4算法和秘钥来解密关键字符串以供后续使用。接下来会完成后续安装配置流程。

首先检测ssl证书文件是否存在，如果不存在，其会处于等候状态，直到证书文件安装完成。否则开始配置工作目录、设置代理地址、设置Tor网络地址、获取外网IP地址、MAC地址、网络名称等信息。下图为部分安装信息。

![](https://images.seebug.org/content/images/2018/06/4ae72a10-fd60-4b0f-8e10-21fc21f8f445.png-w331s)

接下来创建工作目录/var/run/xxm/及/var/run/xxw并开启主循环，向控制端请求控制命令并且执行相应的控制功能。

控制命令的请求有两种方式，一种是通过socks5代理方式，一种是通过Tor网络请求。通过socks5代理请求的C&C地址如下(在新版本中91.121.109.209被移除)：

91.121.109.209  
217.12.202.40  
94.242.222.68

通过Tor网络请求的地址如下（在新版本中”zuh3vcyskd4gipkm.onion/bin32/update.php”被移除）：

6b57dcnonk2edf5a.onion/bin32/update.php  
zuh3vcyskd4gipkm.onion/bin32/update.php  
tljmmy4vmkqbdof4.onion/bin32/update.php

这两种方式的请求都是通过ssl协议进行的。请求完成后，恶意代码解析相应数据并且提取出控制命令和控制参数信息。其实现的远程控制命令和控制参数信息如下：

![](https://images.seebug.org/content/images/2018/06/d4ca0c46-6a0e-46fa-8aba-d245bf0c9474.png-w331s)

![](https://images.seebug.org/content/images/2018/06/c2541c33-ade1-442d-b544-87c75d143448.png-w331s)

从该后门实现的远程控制功能我们可以推测该黑客的动机：

(1)和其他后门一样，黑客希望能够通过远程shell命令对设备进行完全的控制。  
(2)黑客可以在一定时机对这些设备进行破坏性操作，使其无法再次使用。  
(3)为了隐藏其可疑的控制流量，采用socks5和Tor逃避IDS监测。  
(4)可以灵活的配置其在Tor网络中的C&C服务器以及代理服务器  
(5)能提供扩展模块的下载与执行的操作。  
(6)可灵活配置连接C&C的频率，提高其活动的隐蔽性。

此外，该阶段的最新恶意代码有较大的变化，不仅对代码做了优化、去除了日志信息，还改变了部分控制命令的功能，比如kill命令用于结束进程及清理其下载的插件，新增加了update命令和restart命令。不言而喻，update命令用于更新样本，restart命令用于重启样本执行。同时移除了seturl、proxy命令。

##### 第三阶段：扩展组件

第三阶段目前已经发现大量的组件，其中包含一个为MIPS平台的流量嗅探器、一个用于破坏设备的dstr模块、一个用于进行广泛HTTP流量嗅探和监控的ssler模块，还有一些辅助性模块如：Tor
client、mikrotik.o、torrc、ip_tables.ko、iptable_filter.ko、iptable_nat.ko等。辅助性模块如Tor客户端用于支持第二阶段的Tor网络通信。Tor工程提示：

![](https://images.seebug.org/content/images/2018/06/4c9c2b54-a1d9-45ae-a471-53e601bbd694.png-w331s)

由于其为标准的Tor客户端，不具备恶意功能，因此我们仅仅分析核心的三个模块。

1、MIPS平台的TCP流量嗅探模块

该模块为MIPS平台，其主要通过从原始数据包中过滤出TCP/IP数据包，并且通过对TCP的payload数据进行过滤，检索其中的敏感信息存储起来。

该流量嗅探模块通过第二阶段恶意代码远程下载并启动执行，其启动运行参数如下：

{模块名} DstDir Unkownagr ModbusServer

其中第一个参数为嗅探数据的存放路径，第二个参数未使用，第三个参数为modbus server的IP地址。

该模块启动后并没有做过多额外的工作，初始化环境后直接调用流量截取函数进行流量嗅探。

![](https://images.seebug.org/content/images/2018/06/658f3779-6e28-452d-91ea-6a6c2dd8475c.png-w331s)

同样二进制程序中不带任何符号文件，函数由我们分析完后进行了重命名。该函数主要创建一个原始socket并且接收当前设备所通过的原始数据流。

![](https://images.seebug.org/content/images/2018/06/92177f85-832c-4d6f-b28f-090d79dca8c0.png-w331s)

接下来恶意代码会根据TCP/IP头部格式识别出TCP数据包以进行进一步的处理。

首先该模块只关心数据包长度大于0x96个字节的原始流数据，也就是说除去TCP/IP协议头部的长度的0x36个字节，该模块仅仅监视大于0x60个字节的TCP
payload数据。

![](https://images.seebug.org/content/images/2018/06/4033aef8-c96d-4c5c-9fb0-b311636531aa.png-w331s)

对于TCP payload数据大于0x60个字节的数据包，该模块会解析IP、TCP协议，并且通过目的端口502判定当前流量数据是否是工控的modbus
TCP协议包，如果是，且当前数据包的目的IP为运行参数中指定的IP地址，该模块便会将该数据包中的源IP、目的IP、源端口、目的端口记录下来。

![](https://images.seebug.org/content/images/2018/06/72ce10b7-5eb2-4ee3-a4ee-6307a51fdcb6.png-w331s)

其中记录的信息格式如下：

_modbus_

源IP:源端口->目的IP:目的端口(如：192.168.1.5:2243->192.168.1.3:503)

该信息记录在文件`%workdir%/rep_[time].bin`。

![](https://images.seebug.org/content/images/2018/06/a2232a63-50d0-4c9a-b8b2-333e8eee3aae.png-w331s)
![](https://images.seebug.org/content/images/2018/06/e1227709-bcef-4967-825d-c06f79755602.png-w331s)

如果当前协议不是modbus协议，该模块会根据已有的规则进行过滤，找出其关心的两类数据：一种为携带有验证信息HTTP数据包，一种是携带有登录信息的HTTP请求数据。其中提取验证数据的关键字为"Authorization:
Basic”，一旦找到该信息，该模块会将当前嗅探到的数据包直接记录到文件`%workdir%/rep_[%time%].bin`中。

提取登录信息的关键字如下：

用户名关键字："User="、"user="、"Name="、"name="、"Usr="、"usr="、"Login="、"login="

登录密码关键字："Pass="、"pass="、"Password="、"password="、"Passwd="、"passwd="

此外要说明的是，数据包中只要满足如下条件，该模块便会丢弃：

(1)数据包的目的IP为模块运行参数所指定的IP。  
(2)数据包的源端口小于1024。  
(3)数据包的源端口为8080/8088。  
(4)TCP payload数据长度小于0x14。  
(5)TCP Payload数据包中包含有`"<?xml"、">"、"Basic Og=="、"/tmUnblock.cgi"、"Password
required"、"<div”、"<form"、"<input"、"{"、"}"、"200 OK"、".get"、"<span "、"<SPAN
"、"<DIV "`等。

2、ssler HTTP嗅探与监控模块

该模块主要针对HTTP层实施更加丰富和强大的处理，其提供有HTTP流量重定向、HTTP流量监控与截取、流量劫持与篡改、定向注入JS以进行精准攻击等功能。其由第二阶段的恶意模块启动运行，运行参数说明如下：

![](https://images.seebug.org/content/images/2018/06/19784bf9-4add-4ee5-ada3-b25d7c84a016.png-w331s)

首先该模块会使用insmod命令安装三个iptable相关的内核模块 (ip_tables.ko、iptable_filter.ko、
iptable_nat.ko)，通过这三个模块，恶意代码可以将自己的规则配置到iptable中去 。

![](https://images.seebug.org/content/images/2018/06/6b60f850-458a-4ca6-922e-f912133179d0.png-w331s)

接下来执行如下命令将所有80端口的流量重定向到其所监听的8888端口上：

    
    
    iptables -I INPUT -p tcp --dport 8888 -j ACCEPT
    iptables -t nat -I PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8888

![](https://images.seebug.org/content/images/2018/06/a1a2125b-44b9-4277-91e3-ad46e9934eed.png-w331s)

为了保证该规则不会被删除，该模块会每隔5分钟更新一次该规则。

该模块会关注所有80端口上的数据，包括流向服务器端和流向客户端的数据。在处理流向服务器端的数据时，为了最大化的监控到敏感数据，其会对HTTP请求的数据进行一定篡改。在处理流向客户端的响应数据时，同样会对数据进行篡改并且根据启动参数的指定来对特定目标实施精准的JS注入，入侵到具体客户端主机上，也可以是内网的办公主机上。

（1）对请求数据的处理

首先，该模块为了能够最大限度的监控到流量，其会将所有请求数据的`"https://"`篡改为`"http://"`。为了确保HTTP传输的数据都为可处理数据，会修改”Accept-Encoding”的值，以及修改Connection的方式，具体处理方式如下：

i.将请求数据中的所有https篡改为http，以方便监控并窃取敏感信息，如登录凭证等。

![](https://images.seebug.org/content/images/2018/06/c1499777-461e-4ac6-94bf-b7b4b1a45aa4.png-w331s)
![](https://images.seebug.org/content/images/2018/06/5948fef3-fb61-4ab0-bad9-46b12384e09b.png-w331s)

ii.如果HTTP请求中包含有”Connection: keep-alive”，将会被替换为”Connection: close”。

![](https://images.seebug.org/content/images/2018/06/24316f08-7c92-418a-b3cf-3c9dee8c29fb.png-w331s)
![](https://images.seebug.org/content/images/2018/06/a7faa4b6-ebab-41dd-adaf-095fe89e82c3.png-w331s)

iii.如果HTTP请求中,HTTP头中包含有gzip值的”Accept-Encoding”头部域(排除url为jpg、jpeg、png、gif、css、js、ttf、woff文件)，其将会转化为”Accept-Encoding:
plaintext/none”，这样请求得到的数据便不会被服务器端压缩。

![](https://images.seebug.org/content/images/2018/06/a8f506f3-fd0d-4c17-aac4-7c279a66bc0b.png-w331s)

随后，该组件可对截取的流量进行过滤并将相关数据保存到设备中。首先如果`“dump:domain”`参数被指定，http请求的url、port、http
header都会保存在指定的文件中。如果在dump参数中没有指定具体值(domain字符串为空)或者dump参数没有指定时，其会dump包含有特定信息http请求信息。其通过URL来判定当前请求是否是其关心的请求，如果URL中包含有关键字：

“sername=”、“ser=”、“ame=”、“ogin=”、“ail=”、“hone=”、“session%5Busername”、“session%5Bpassword”、“session[password”

便会dump请求的头部信息到指定的文件中。

![](https://images.seebug.org/content/images/2018/06/36fd45fd-309c-4f5e-8b0b-8f7c6539ffd3.png-w331s)

另外，对accounts.google.com发送的POST请求，只要其中包含有字符串“signin”,都会被dump下来。

![](https://images.seebug.org/content/images/2018/06/96cf16e4-499b-4ec6-a840-1685a5176eca.png-w331s)

（2）对响应信息的处理

所有HTTP请求得到的响应数据都会被处理，其处理方式如下：

i.响应信息中Location的值如果是`“https://”`，则被替换为`http://`。

ii.如果响应头部中包含有Alt-Scv、Vary、Content-MD5、content-security-policy、X-FB-Debug、public-key-pins-report-only、Access-Control-Allow-Origin，便会被阻断，也就是说，请求方无法得到响应。

iii.Dump所有请求包的数据到本地，其中包含`https://`和`http://`。

iv.如果参数`“site:domain”`指定了域名关键字或者域名的一部分，其会将一段javascript脚本注入到所有包含有的`“Content-Type: text/html”` 或者`“Content-Type:
text/javascript”`响应数据的msgbody中。其注入方法：首先响应的msgbody数据中必须包含字符串`“<meta name= …
>”`并且长度必须大于参数`“hook:”`所指定的字符串长度。如果满足条件，字符串`“<meta name= … >”`将会被替换成为`“<script
type="text/javascript" src="[hook
value]">”`，当前受害者IP及其访问的网站域名将会加入到内部的一个白名单中，以防止重复注入，白名单每4天会被清空一次。

![](https://images.seebug.org/content/images/2018/06/868badd8-32be-4980-a8e5-7af26153c2a3.png-w331s)

在响应数据中，恶意模块会提取每个链接中的域名，并且将其加入到截取列表中，这个截取列表中所有的https和http请求都会按照“（1）对请求数据的处理”的方式进行处理。默认情况下包含有
www.google.com、 twitter.com、 www.facebook.com、www.youtube.com。

![](https://images.seebug.org/content/images/2018/06/8c07670f-c879-4990-bb4f-baa3d57c8ad6.png-w331s)

3、 设备破坏模块（Destroy module）

由于老版本的第二阶段模块单纯的只是简单擦除设备mtdblock0的前5000个字节以破坏设备，有很大几率会失败，因此新版本的第二阶段模块将kill指令的破坏性功能取消，并采用插件模块的方式来实现。该插件模块不仅改进了破坏设备功能，而且还提供了痕迹清理的功能。其目的不仅让设备无法恢复，而且即便恢复了也无法取证获取恶意代码相关痕迹。

模块启动后首先删除自身文件，然后强制关闭所有包含"vpnfilter"、"security"、"tor"关键字的进程。

![](https://images.seebug.org/content/images/2018/06/4fbecfcb-8ce6-4267-99da-3babaf3e0f9c.png-w331s)

接下来清理掉所有痕迹文件，其中包含有证书文件、Tor客户端相关文件、版本信息文件等。

![](https://images.seebug.org/content/images/2018/06/31934567-09a3-4f30-8edf-3b6841af0ee1.png-w331s)

该模块还会遍历mtd分区，并强制擦除整个FLASH。

![](https://images.seebug.org/content/images/2018/06/a1721b0e-4eda-47e7-83d7-2450a6447438.png-w331s)

最后，其采用`“"rm -rf /*"”`强制递归删除文件系统上的所有文件，并重启设备。

![](https://images.seebug.org/content/images/2018/06/1bc09d93-5ce3-487a-abee-6364ae5839ef.png-w331s)

#### 四、总结

通过分析我们可以看出，该恶意代码攻击手法隐秘高明，其不仅采用代理+Tor+SSL的方式以逃避网络流量的监测，而且还有多重策略用于确保核心组件(第二阶段恶意代码)的成功下发。首先采用了HTTP的方式将C&C存放于”direct”或者”location”字段中，如果这种方式被阻断则采用图片隐写技术将C&C存储于EXIF中，如果存储C&C的图片链接失效，其还在代码中留了一个”SYN”后门，通过”SYN隧道技术”来传输C&C。这种可以说是黑客采取的一种较为高明且非常保险的策略，为其行动在被发现甚至是被阻断后设置了多重保险，也便于在黑客发现被阻断后进行快速切换，极大地提高了其控制的持久性和灵活性。

我们还可以看到，迅猛发展的物联网设备也开始变成高级威胁组织的一类攻击向量，其试图通过这些设备来收集情报，包括登录凭证以及工控设施相关的重要信息，通过灵活的模块化架构，可根据相关情报对特定主机实施精准攻击或者对大量设备实施极具破坏性的攻击，其危害性非常之大。

建议厂商将检测规则（Talos已经公开了100多条snort规则）加入到流量检测设备中，如果支持原始流量检测，也可利用“SYN隧道技术”中的特征进行更加深度和精确的检测。一旦发现受感染设备，建议采用应急策略对设备进行处置（比如对设备进行断网并且复位恢复到出厂模式、更新最新固件），同时进一步检查内网主机是否有被攻击并请专业人士进行处理。

IOC: 第一阶段涉及的相关URL：

    
    
    photobucket[.]com/user/nikkireed11/library
    photobucket[.]com/user/kmila302/library
    photobucket[.]com/user/lisabraun87/library
    photobucket[.]com/user/eva_green1/library
    photobucket[.]com/user/monicabelci4/library
    photobucket[.]com/user/katyperry45/library
    photobucket[.]com/user/saragray1/library
    photobucket[.]com/user/millerfred/library
    photobucket[.]com/user/jeniferaniston1/library
    photobucket[.]com/user/amandaseyfried1/library
    photobucket[.]com/user/suwe8/library
    photobucket[.]com/user/bob7301/library
    toknowall[.]com

第二阶段涉及的相关IP及链接：

    
    
    91.121.109[.]209
    217.12.202[.]40
    94.242.222[.]68
    82.118.242[.]124
    46.151.209[.]33
    217.79.179[.]14
    91.214.203[.]144
    95.211.198[.]231
    195.154.180[.]60
    5.149.250[.]54
    91.200.13[.]76
    94.185.80[.]82
    62.210.180[.]229
    62.210.180[.]229
    91.200.13[.]76
    23.111.177[.]114
    6b57dcnonk2edf5a[.]onion/bin32/update.php
    tljmmy4vmkqbdof4[.]onion/bin32/update.php
    zuh3vcyskd4gipkm[.]onion/bin32/update.php
    4seiwn2ur4f65zo4.onion/bin256/update.php
    zm3lznxn27wtzkwa.onion/bin16/update.php

最新受感染的设备如下：

![](https://images.seebug.org/content/images/2018/06/c0bd0ed4-0cf0-4c58-964b-0ddc6c60cc71.png-w331s)

![](https://images.seebug.org/content/images/2018/06/7509b147-ecdf-4596-bf4e-48ec28b69fb2.png-w331s)
![](https://images.seebug.org/content/images/2018/06/ffd43397-2e79-40b5-94d3-c46d91026e91.png-w331s)

参考链接：  
<https://blog[.]talosintelligence.com/2018/05/VPNFilter.html>  
<https://blog.talosintelligence.com/2018/06/vpnfilter-update.html>

* * *

**启明星辰积极防御实验室（ADLab）**

ADLab成立于1999年，是中国安全行业最早成立的攻防技术研究实验室之一，微软MAPP计划核心成员。截止目前，ADLab通过CVE发布Windows、Linux、Unix等操作系统安全或软件漏洞近400个，持续保持国际网络安全领域一流水准。实验室研究方向涵盖操作系统与应用系统安全研究、移动智能终端安全研究、物联网智能设备安全研究、Web安全研究、工控系统安全研究、云安全研究。研究成果应用于产品核心技术研究、国家重点科技项目攻关、专业安全服务等。
![](https://images.seebug.org/content/images/2017/05/adlab.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/618/>

