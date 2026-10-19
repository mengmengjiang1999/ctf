![image.png](https://image.3001.net/images/20180508/15257732882243.png!small)

## 一、前言

Ghost
Tunnel是一种可适用于隔离环境下的后门传输方式，可在用户无感知情况下对目标进行控制及信息回传（不创建或依赖于任何有线、无线网络，甚至不需要外插任何硬件模块）。

在4月的HITB阿姆斯特丹站上，我们（PegasusTeam）分享了一个关于隔离网攻击的议题——"Ghost Tunnel :Covert Data
Exfiltration Channel to Circumvent Air Gapping"。

Ghost
Tunnel是一种可适用于隔离环境下的后门传输方式。一旦payload在目标设备释放后，可在用户无感知情况下对目标进行控制及信息回传。相比于现有的其他类似研究（如WHID，一种通过
Wi-Fi 进行控制的 HID 设备），Ghost Tunnel不创建或依赖于任何有线、无线网络，甚至不需要外插任何硬件模块。

到底有多棒，先把demo放出来镇文。

  

## 二、背景

为了便于读者理解Ghost
Tunnel的使用场景，在本节中将会介绍“远控木马上线方式”、“网络隔离”、“HID攻击”等相关知识，部分内容引用自其他文章，在小节末将给出原文以便于大家扩展阅读。

### 2.1 远控木马上线方式

说起远控木马，大家可能会想到一大堆耳熟能详的名称，如灰鸽子、冰河、Byshell、PCshare、Gh0st等等，在此我们以上线方式的角度对远控木马进行一个简单分类。

 **主动连接型**

被控端开启特定端口，主控端通过该主机IP及端口连接到被控端，如3389远程桌面、VNC远程桌面等。

 **反弹连接型**

由于主动连接的方式不适用于攻击目标处在内网的环境，许多木马采用反弹型进行上线。与主动连接的方式相反，由主控端监听特定端口，被控端执行木马后反连回主控端。由于该种方式的适用性更广，大部分的木马都采用该方式上线，如利用FTP上线、DNS域名解析上线等。

![image.png](https://image.3001.net/images/20180508/15257733099358.png!small)

 **通过第三方域名型**

出于隐蔽性或者反追踪的目的，有些新型的木马采用第三方网站来进行上线。比如通过知名博客类网站的文章内容及评论区，利用QQ空间、微博、推特的推送内容，甚至笔者还见过利用QQ个性签名来作为上线地址。八仙过海各显神通，利用知名网站的好处是可以绕过某些防火墙的白名单限制。

![image.png](https://image.3001.net/images/20180508/15257733462498.png!small)>《木马的前世今生：上线方式的发展及新型上线方式的实现》
<http://www.freebuf.com/articles/terminal/77412.html>

其实，Ghost Tunnel也可以理解为一种木马的上线方式，只是它更针对于攻击目标处在隔离网络中的场景。

### 2.2 什么是Air Grapping

> Wikipedia: “An air gap, air wall or air gapping is a network security
> measure employed on one or more computers to ensure that a secure computer
> network is physically isolated from unsecured networks, such as the public
> Internet or an unsecured local area network.”

简单来说，Air Grapping是一种用于保护特定网络，采用物理隔离的安全措施，通常被用来防止利用网络连接途径造成的入侵及信息泄漏事件。

![image.png](https://image.3001.net/images/20180508/15257733807310.png!small)

隔离网闸是常见的一种形态，其原理为：切断网络之间的通用协议连接；将数据包进行分解或重组为静态数据；对静态数据进行安全审查，包括网络协议检查和代码扫描等；确认后的安全数据流入内部单元；内部用户通过严格的身份认证机制获取所需数据。其经常被使用在涉密网与非涉密网间。

攻击者无论是想利用操作系统、应用软件、通信协议的漏洞，都需要通过网络触碰目标机器，而网络隔离环境中就将这条路给封住了。不过凡事没有绝对，一些大新闻告诉我们利用恶意USB就是一种具有可操作性的攻击方式，以下就是几个针对隔离网攻击的案例。

 **震网病毒 Stuxnet Worm**

![image.png](https://image.3001.net/images/20180508/1525773394140.png!small)

著名的震网病毒便利用了USB的方式将病毒传入隔离网络，随后将病毒传播到网络中的其他设备。在适当的时候给工控机器下发错误指令，导致机器异常直至报废。最终震网病毒导致伊朗的核计划被迫延迟至少两年。

 **水蝮蛇一号 COTTONMOUTH-I**

![image.png](https://image.3001.net/images/20180508/15257734087253.png!small)

在斯诺登披露的NSA秘密武器中包含了该工具，其内部包含了一套 ARMv7
芯片和无线收发装置。当它插入目标主机后，植入恶意程序并创建一个无线网桥，配套的设备可通过RF信号与其进行交互，传输命令及数据。同样，它被NSA用于攻击伊朗的秘密机构，从物理隔离的设备中窃取数据长达数年。

### 2.3 HID攻击

HID是Human Interface
Device的缩写，由其名称可以了解HID设备是直接与人交互的设备，例如键盘、鼠标与游戏杆等。不过HID设备并不一定要有人机接口，只要符合HID类别规范的设备都是HID设备。一般来讲针对HID的攻击主要集中在键盘鼠标上，因为只要控制了用户键盘，基本上就等于控制了用户的电脑。攻击者会把攻击隐藏在一个正常的鼠标键盘中，当用户将含有攻击向量的鼠标或键盘，插入电脑时，恶意代码会被加载并执行。

 **Teensy**

攻击者在定制攻击设备时，会向USB设备中置入一个攻击芯片，此攻击芯片是一个非常小而且功能完整的单片机开发系统，它的名字叫TEENSY。通过TEENSY你可以模拟出一个键盘和鼠标，当你插入这个定制的USB设备时，电脑会识别为一个键盘，利用设备中的微处理器与存储空间和编程进去的攻击代码，就可以向主机发送控制命令，从而完全控制主机，无论自动播放是否开启，都可以成功。

![image.png](https://image.3001.net/images/20180508/15257734268365.png!small)

 **USB Rubber Ducker**

简称USB橡皮鸭，是最早的按键注入工具，通过嵌入式开发板实现，后来发展成为一个完全成熟的商业化按键注入攻击平台。它的原理同样是将USB设备模拟成为键盘，让电脑识别成为键盘，然后进行脚本模拟按键进行攻击。

![image.png](https://image.3001.net/images/20180508/15257734362928.png!small)

 **BadUSB**

Teensy和橡皮鸭的缺陷在于要定制硬件设备，通用性比较差。但是BadUSB就不一样了，它是在“USB RUBBER
DUCKY”和“Teensy”攻击方式的基础上用通用的USB设备（比如U盘）。BadUSB就是通过对U盘的固件进行逆向重新编程，相当于改写了U盘的操作系统而进行攻击的。

 **BashBunny**

![image.png](https://image.3001.net/images/20180508/15257734483862.png!small)

可以发动多种payload是这款设备的一大特色。将开关切换到相应payload选择（上图中的Switch Position 1/2），将Bash
Bunny插入目标设备，观察LED灯的变化就能了解攻击状态。在硬件方面，设备中包含1颗四核CPU和桌面级SSD，Hak5介绍说此设备从插入到攻击发动只需要7秒。此外，这款Bash
Bunny设备实际上拥有Linux设备的各种功能，通过特定串口可访问shell。绝大部分渗透测试工具的功能都能在其中找到。

 **DuckHunter**

在Kali Linux NetHunter中提供了该工具。它可以将USB Rubber Ducky的脚本转化为NetHunter 自有的HID
Attacks格式，由此我们将刷有Nethunter的Android设备通过数据线与电脑相连便能模拟键盘进行输入。

![image.png](https://image.3001.net/images/20180508/15257734647253.png!small)

 **WHID**

WHID就是WiFi +HID的组合，WHID注入器顾名思义就是对HID攻击进行无线化攻击时的一种注入工具，通过在USB设备上提供WiFi功能以供远程控制。

![image.png](https://image.3001.net/images/20180508/15257735166601.png!small)

> 《HID攻击之TEENSY实战》

<http://blog.topsec.com.cn/ad_lab/hid%E6%94%BB%E5%87%BB%E4%B9%8Bteensy%E5%AE%9E%E6%88%98/>

> 《新的U盘自动运行——BadUSB原理与实现》

<https://security.tencent.com/index.php/blog/msg/74>

> 《据说是“最先进的USB攻击平台”》

<http://www.freebuf.com/news/128788.html>

> 《DuckHunterHID for mac》

<http://www.ggsec.cn/DuckHunterHID.html>

> 《WHID注入器：在无线环境下实现HID攻击的最新利器》

<http://www.4hou.com/technology/4565.html>

## 三、Ghost Tunnel

对于隔离网络的攻击一般有两个步骤：

> 1\. 在目标系统植入恶意软件
>
> 2\. 建立数据通道，(infiltrate & exfiltrate)，以便执行命令和窃取数据。

根据之前的案例可以看到，任何可以承载数据的媒介都是可以用来建立数据通信的通道。Ghost Tunnel便是一个利用WiFi信号的隐蔽传输通道。

![image.png](https://image.3001.net/images/20180508/15257735335657.png!small)

首先，以HID攻击为例：我们使用BashBunny或者DuckHunter等HID工具将恶意程序植入受害者设备，比如一台Windows笔记本。随后恶意程序将使用受害者设备的
**内置无线通信模块** 与另一台由攻击者控制的设备建立端到端的WiFi传输通道。此时，攻击者就可以远程执行命令并窃取数据。

值得注意的是，Ghost
Tunnel指的是通过利用受害者设备自身的无线模块来建立传输通道的一种方式，其并不仅局限于使用HID攻击来植入恶意程序，实际上以其他方式植入也是可行的。

### 3.1 优势

Ghost Tunnel的实现方式具有这几个优势：

> HID设备只用于植入攻击代码，当植入完成就可以移除了。（HID攻击外的其他植入形式也是可以的）
>
> 没有正常的网络连接，可以绕过防火墙。
>
> 不会对现有的网络通信及连接状态造成影响。
>
> 跨平台支持。该攻击可用于任何拥有WiFi模块的设备，我们在Win7、Win10、Mac OSX上进行了测试。
>
> 可在几十米内工作，配合信号桥接设备理论上可做到无限远。

### 3.2 原理

在正常的Wi-Fi通信中，一个站点必须经历Beacon，Probe，Authentication，Association等过程后才能建立与接入点的连接，其整个流程如下图。

![image.png](https://image.3001.net/images/20180508/15257735532450.png!small)

而Ghost Tunnel并没有使用正常的Wi-Fi连接，而只用到了Beacon、Probe Request、Probe Response，如下图。

![image.png](https://image.3001.net/images/20180508/15257735661557.png!small)  

为什么用这三个帧呢？在802.11的状态机中，取决于认证和关联的状态，一共有三个阶段。

![image.png](https://image.3001.net/images/20180508/15257735897209.png!small)  

在State
1时，客户端处于Unauthenticated、Unassociated状态。而该阶段可以使用的802.11帧有以下具体几种，其中就包含了Probe
Request，Probe Response，Beacon帧。

![image.png](https://image.3001.net/images/20180508/15257736126632.png!small)

原本它们被使用在无线网络扫描阶段。当802.11客户端在扫描可用无线网络时，有两种扫描方式：

  * 主动扫描，客户端主动发送Probe Request，接收由接入点返回的Probe Response。

  * 被动扫描，客户端在每个频道监听AP周期性发送的Beacon。

![image.png](https://image.3001.net/images/20180508/15257736666076.png!small)  

总而言之，Ghost Tunnel通过Probe Request，Probe
Response，Beacon三种类型帧来进行通信，并不建立完整的WiFi连接。

首先攻击者创建一个具有特殊SSID的AP，攻击者和受害设备都使用它作为通信的标识符（而不是常规WiFi通信中的MAC）。此时，攻击者通过解析受害者设备发出的Probe
Request帧得到数据；受害者设备上的恶意程序将解析攻击者发出的Beacon及Probe Response帧来执行命令并返回数据。这便是Ghost
Tunnel WiFi隐蔽传输通道的秘密。

![image.png](https://image.3001.net/images/20180508/1525773715836.png!small)

### 3.3 其他

你可能会有关于实现原理等更深入的问题，比如：

  * 如何在802.11帧中携带我们的载荷？

  * 如何在用户空间利用设备的无线网卡来发送和接受802.11数据包？

  * 各个操作系统平台的WiFi应用接口是什么，具体如何实现？

  * 攻击者端的C&C Server是如何实现的？

欢迎查看我们已对外公布的PPT，你可以在其中找到这些问题的答案。如果觉得该研究还不错的话，欢迎点下Star。

<https://github.com/360PegasusTeam/PegasusTeam/tree/master/talks>

## 四、影响

P4wnP1项目受GhostTunnel启发，在新版本加入了此种方式。

<https://github.com/mame82/P4wnP1>

![image.png](https://image.3001.net/images/20180508/15257737311819.png!small)

![image.png](https://image.3001.net/images/20180508/1525773740428.png!small)  

在MSF近期更新的一个脚本中（<https://github.com/rapid7/metasploit-framework/pull/9862>
）利用类似的思路实现了近场探测的功能，作者表明该脚本的主要场景就是探测目标设备是否是否已经物理接近了被攻击端。

![image.png](https://image.3001.net/images/20180508/15257737639796.png!small)

 ***本文作者qingxp9，转载注明来自FreeBuf**  

