**本文是作为一个新手接触这款产品时使用的一些记录和理解，由于入手时在网上找到的资料有限，翻译成为中文的文档也更是少之又少，没有找到较好的指导文档（也可能姿势不对）。因此出现了本篇文章，对使用及测试过程中遇到的问题和心得进行记录，并包括对于不同模块的简单介绍，对于某些模块测试记录了简单示例，以供跟我一样的新人基础入门，如果想要完整地进行一些攻击的话，需要熟练使用不同模块，了解原理和机制，并不断进行尝试以达到目的，由于个人水平极其有限，文章中可能出现一些理解偏差，描述偏差甚至是错误的情况，不接受任何批评（哈哈哈哈，欢迎指正QAQ）**

## 一 简介

The WiFi Pineapple
是由国外无线安全审计公司Hak5开发并售卖的一款无线安全测试神器（俗称大菠萝），从2008年起目前已经发布到第六代产品。当前的主打产品是The WiFi
Pineapple NANO 和WiFI Pineapple TETRA（支持5GHz频段）

手上这款是WiFi Pineapple NANO

###  **产品规格：**

> ·CPU：400 MHz MIPS Atheros AR9331 SoC
>
> ·内存：64 MB DDR2 RAM
>
> ·磁盘：16 MB ROM + Micro SD（6G）
>
> ·无线：Atheros AR9331（wlan0）+ Atheros AR9271（wlan1），均为IEEE 802.11 b / g / n
>
> ·端口：（2）RP-SMA天线，USB网卡（ASIX AX88772A）
>
> ·USB 2.0主机，Micro SD读卡器
>
> ·电源：USB 5V 1.5A. 包括 Y型USB电源线
>
> ·可配置状态指示灯LED
>
> ·可配置的重置按钮

## 二 使用背景

对于这种黑客 “外设” 来讲，和其他外设没什么两样，都是烧钱的东西，那这个东西在什么情况下入手比较合适呢？

###  **1安全研究**

对于正在进行安全研究并计划将研究方向定为wifi安全的小伙伴们，可以使用这款 “外设”
作为入门和进阶的部分，能够带领我们了解一些常见的wifi安全问题、原理和攻击手段，进一步的可以分析这些利用工具的原理，实现方法，组合攻击手段

###  **2安全演示**

如果你是安服的小伙伴，给客户演示的时候不要总是带着自建靶场，给领导搞一个SQL注入，永恒之蓝，过时了！就算你配合Cobalt
Strike来个主机上线，也顶多是视觉上的刺激。你带个wifipineapple，现场来个中间人，搞个绵羊墙，抓个密码，岂不美哉？

###  **3有钱**

您老要是有闲钱，那就买个玩玩！

## 三 管理

安装与配置过程不在此赘述，网上均有相关指导文章，在本文第十章”参考链接”处也能找到， 可以使用 USB 网卡或 wifi 进行网络接入

Web管理端地址：<http://172.16.42.1:1471>

![1.png](https://image.3001.net/images/20190221/1550741580_5c6e704c033c1.png!small)

第一次登陆会以root身份登陆，并在安装时配置密码， 这个密码将同样作为ssh连接时的root密码

![2.png](https://image.3001.net/images/20190221/1550741569_5c6e704136d62.png!small)

## 四 特性

> a.用作 Wi-Fi 中间人攻击测试平台
>
> b.一整套的针对 AP 的渗透测试套件
>
> c.基于 WEB 应用的管理界面
>
> d.基于嵌入式 linux 系统
>
> e.不定时的各种软件更新，可以自定义模块、payload

## 五 管理页面简介

###  **1 Dashboard仪表盘**

仪表盘上显示了一些状态、统计信息、通知和公告的概览视图，包括：

> CPU 使用率、设备运行时间、客户端连接数量
>
> Landing Page 浏览状态，公告
>
> Bulletins从wifipineapple.com获取的最新项目信息

###  **2 Recon侦察**

Recon模块采用被动式扫描方式，扫描过程会自动将网卡设置为监听模式，监听周围不同信道上（客户端）发出的各种数据包。能够扫描出SSID、MAC地址、加密方式、是否启用了WPS功能、信道及信号强度等信息，甚至还能扫描出当前未连接任何AP的客户端

从下拉列表为扫描的持续时间，增加扫描时间可以在每个信道上看到更多潜在的流量，选中“Continuous”框将启用正在进行的扫描。每隔一段时间进行持续扫描，并更新扫描结果列表，直到扫描停止

扫描结果将显示在表格视图中

![3.png](https://image.3001.net/images/20190221/1550741560_5c6e70389225b.png!small)

未关联的客户端仅显示 MAC 地址。这些客户端具有活动无线电，但不与接入点关联

![4.png](https://image.3001.net/images/20190221/1550741546_5c6e702abe7de.png!small)

单击SSID和MAC地址旁的下拉菜单，会出现如下两张图的菜单，用于 PineAP 模块的 Filter(过滤) 和 Tracking(追踪) 功能，以及进行
Deauth(取消认证洪水) 攻击中发送取消身份验证帧的倍数参数

![5.png](https://image.3001.net/images/20190221/1550741533_5c6e701daff8d.png!small)![6.png](https://image.3001.net/images/20190221/1550741533_5c6e701dd7b3b.png!small)

需要注意的是，使用 Recon 模块进行扫描将会断开已有的连接

### 3 Clients客户端

如果在 PineAP 中勾选了 Allow Associations(允许关联)，WiFi Pineapple将允许客户端进行连接

已连接的客户端将在“ Clients ”视图中列出它们各自的MAC地址，IP地址，它们已连接的 SSID （如果在PineAP中启用了Log
Probes(日志探测) 功能）和主机名

Kick按钮可以从Wi-Fi Pineapple网络中删除客户端

MAC地址和SSID旁边的下拉菜单按钮用于 PineAP 模块的 Filter 和 Tracking 功能

Refresh按钮可以刷新Clients表格视图

### 4 Filters过滤器

![7.png](https://image.3001.net/images/20190221/1550741517_5c6e700d9a05e.png!small)

可以通过客户端MAC地址或SSID来执行过滤。支持“Deny”和“Allow”模式，可以使用Swith按钮进行切换

 **Client Filtering 客户端过滤**

在Deny Mode下，客户端过滤器中列出的具有MAC地址的客户端将无法连接到WiFi Pineapple

在 Allow Mode下，只有客户端过滤器中列出的具有MAC地址的客户端才能连接

进行WI-FI安全测试时，最好使用“Allow Mode”以确保仅针对参与范围内的客户端

 **SSID Filtering SSID过滤**

在Deny Mode下，如果客户端尝试连接到过滤器中列出的SSID，则客户端将无法与WiFi Pineapple关联

在 Allow Mode下，如果过滤器中列出了他们尝试连接的SSID，则客户端只能与WiFi Pineapple关联

SSID可以从与Recon中各自列表相关联的菜单按钮添加到过滤器中，也可以手动添加或删除过滤器中的条目

### 5 PineAP Pine接入点

PineAP是通过伪造的Probe
Response响应包来响应周围的客户端（可能是笔记本、手机、pad等等），让客户端以为周围存在着曾经成功连接过的无线AP，而用来欺骗客户端进行连接我们的Pineapple
Nano设备

![8.png](https://image.3001.net/images/20190221/1550741507_5c6e7003c99b0.png!small)

 **Allow Associations 允许关联**

此项被勾选时，客户端可以通过任何请求的 SSID连接到Pineapple

禁用时，客户端将不允许被连接。相当于以前的 karma

 **Log Probes 日志探测**

开启后，将记录客户端的探针请求。可以从 Logging 模块里看查看分析

 **Log Associations 日志关联**

开启后，客户端的连接信息将会被记录。可以从 Logging 模块里查看分析

禁用后，连接成功的信息将不被记录，并且不会出现在 Clients 模块的 SSID 一栏里

 **PineAP Daemon PineAP 守护进程**

这个进程必须开启

可以使用 Beacon 响应，捕获 SSIDs 到池里，以及对SSID进行广播

这个设置会作用于 wlan1 ，并且 wlan1 不能用于 Client 模式去桥接外网

 **Beacon Response Beacon 响应**

开启之后，目标 beacons 将会发送给客户端设备，用来响应客户端的 SSID 探针请求

这些 beacons 将不会被广播，而是指定发送给发送了探针请求的客户端设备。这可以防止beacon 被其他设备看见。如果 Allow
Associations 启用并且有客户端连接，目标 beacon 响应将持续发送给客户端设备一段时间

Beacon 响应将会使用源 mac 地址设置，并且也会与广播 SSID池特性共享

Beacon 响应间隔将决定发射的频率

 **Capture SSIDs to Pool 捕获SSID到池中**

开启之后，将会把捕捉到的探针请求里的 SSID 保存到 SSID 池中

 **Broadcast SSID Pool 广播SSID池**

开始之后，SSID 池将会按照设定的时间间隔以及源地址、目标地址来广播beacon

SSID 池也可以手动来管理，相当于以前的 Dogma

 **Source MAC 源Mac地址**

默认情况下，是Pineapple wlan0 的 Mac 地址，可以在 Networking 里进行设置

Target MAC 目标Mac地址

默认情况下是广播的 Mac 地址 FF:FF:FF:FF:FF:FF

用于广播帧数据将会被附近的客户端识别，如果设置为某一个固定的 mac 地址，将会对该地址本身进行 PineAP唯一的攻击目标

类似 beacon 响应，只有池中的 SSID 广播会被目标客户端看到

如果使用了 Filters，将更精确的定位到目标设备

 **Broadcast SSID Pool Interval 指定广播 SSID 的时间间隔**

间隔越小，对 CPU 的占用就越高

 **Beacon Response Interval 指定 beacon 响应的时间间隔**

间隔越小，对 CPU 的占用就越高

 **Save as Default on Boot 保存为启动默认配置**

将会把设置保存，并且系统启动时会继续执行

 **SSID Pool SSID池**

当 Capture SSID Pool 功能开启时，将会自动记录捕获到的SSID，也可以手动添加或删除

### 6 Tracking跟踪

![9.png](https://image.3001.net/images/20190221/1550741497_5c6e6ff9286fc.png!small)

跟踪功能将按MAC地址连续扫描指定的客户端，并执行可自定义的跟踪脚本

此功能需要启用 PineAP 的 Log Probes 和 Log Associations 中的至少一个选项

可以手动添加客户端，也可以在 Clients 或 Recon 视图中关联的MAC地址使用 PineAP Tracking Add MAC 按钮添加 Mac
地址到此模块中

当客户端被识别时，将会执行自定义脚本

### 7 Logging日志记录

![10.png](https://image.3001.net/images/20190221/1550741481_5c6e6fe99c229.png!small)

Logging模块共记录了 PineAP Log、System Log、Dmesg、Reporting Log四种日志

 **PineAP Log**

如果启用了Log Probes 和 Log
Associations其中的一个或全部，则按时间顺序显示PineAP事件。每个事件都包含时间戳，事件类型（探测请求或关联），客户端设备的MAC地址以及设备探测或关联的SSID

可以对结果进行过滤，在按下”Apply Filter”之前，过滤器不会生效，默认情况下，PineAP日志位于/tmp中，重启不会保存

 **PineAP Log**

系统日志，没什么好说的

 **Dmesg**

设备故障的诊断，硬件连接断开等信息

 **Reporting Log**

生成报告日志

### 8 Reporting报告

![11.png](https://image.3001.net/images/20190221/1550741466_5c6e6fdadef4a.png!small)

此功能能够以指定的间隔生成报告。报告可以通过电子邮件发送，也可以本地保存在SD卡上

报告内容可选，包括PineAP日志（可以在生成报告后删除），PineAP Site Survey（可指定扫描时间）PineAP 探测和跟踪客户端报告。

### 9 Networking网络

在 Networking 模块中，可以更改路由，接入点，MAC地址，主机名，并使用WiFi客户端模式连接到接入点

 **Route 路由**

显示内核IP路由表，可以针对所选接口进行修改，默认网关为172.16.42.42

使用WiFi Pineapple Connector Android应用程序时，IP路由将自动更新以使用usb0作为默认网关

下拉菜单可以重启DNS服务

![12.png](https://image.3001.net/images/20190221/1550741373_5c6e6f7d0463c.png!small)

 **Access Points 接入点**

可以配置WiFi Pineapple主要开放接入点和管理接入点。开放和管理接入点共享相同的信道

可以隐藏开放接入点，并且可以禁用管理接入点

![13.png](https://image.3001.net/images/20190221/1550741442_5c6e6fc2e5d1a.png!small)

 **WiFi Client Mode WI-FI客户端模式**

能够将WiFi Pineapple连接到另一个无线接入点，以进行Internet或本地网络访问

![14.png](https://image.3001.net/images/20190221/1550741414_5c6e6fa6d9c2a.png!small)

 **MAC Addresses Mac地址**

可以手动更改MAC地址，也可以设置随机MAC，更改MAC可能会断开连接的客户端与WiFi Pineapple的连接

 **Advanced 高级**

能够更新主机名

下拉菜单中能够将WI-FI配置恢复默认

显示ifconfig的输出

![16.png](https://image.3001.net/images/20190221/1550741318_5c6e6f4692417.png!small)

### 10 configuration配置  

**General 常规**

一些设备的常规设置，如设置时区、更改密码、关机、重启、恢复出厂设置

![17.png](https://image.3001.net/images/20190221/1550741294_5c6e6f2e9a7df.png!small)  

**Landing Page 着陆页面(钓鱼)**

启动后，客户端全部链接将会被强制导向到此页面，页面访问的统计信息将会显示在 Dashboard 上

页面可以是 PHP 或 HTML 的

只有WiFi Pineapple具有Internet连接时，才会显示此页面

例如下图是之前写的模仿某宝的钓鱼页面

![18.png](https://image.3001.net/images/20190221/1550741275_5c6e6f1be6f0a.png!small)

### 11 Advanced高级  

高级视图提供有关系统资源，USB设备，文件系统表，CSS以及升级WiFi Pineapple固件的功能的信息

 **Resources 资源**

显示文件系统磁盘使用情况和内存，下拉菜单按钮可以清除页面缓存

![19.png](https://image.3001.net/images/20190221/1550741253_5c6e6f05b5307.png!small)

 **USB**

显示外接USB，设置文件系统表（fstab）。下拉菜单按钮可以格式化SD卡

![20.png](https://image.3001.net/images/20190221/1550741238_5c6e6ef6c7df9.png!small)  

**CSS 层叠样式表**

可以修改WiFi Pineapple Web界面样式表

Firmware Upgrade 固件升级

固件升级将替换所有数据（不包括SD卡或USB等外部存储器）

升级前应备份重要的非系统数据

## 六 常用模块

 **Dwall绵羊墙**

DWall 是一款可以实时抓取 http 数据的插件，并且可以实时展示在web页面上

Enable开启模块，Start Listening 开始监听

所有连到 Pineapple 客户端的http连接都会被抓到

页面显示了客户端、URL、Cookies、数据内容，以及图片

![21.png](https://image.3001.net/images/20190221/1550741222_5c6e6ee687b04.png!small)

 **Deauth 取消验证洪水攻击**

De-authenticationFlood
Attack，全称为取消身份验证洪水攻击或验证阻断洪水攻击，通常被简称为Deauth攻击，是无线网络拒绝服务攻击的一种形式。它旨在通过欺骗从AP到客户端单播地址的取消身份验证帧来将客户端转为未关联／未认证的状态

![22.png](https://image.3001.net/images/20190221/1550741204_5c6e6ed4dd140.png!small)

normal模式下，选中网卡，点击 Start
后就开始攻击攻击过程中同网段内的网络认证（由于NANO不支持5G，所以攻击仅支持2.4G）均会失败，无法认证并连接

要针对某个WI-FI攻击，可以在Editor中选中网卡，扫描WI-FI，并Add to
Blacklist（添加到黑名单），在Mode中也选择blacklist，输入Channels，信道可以去SiteSurvey中查看

![23.png](https://image.3001.net/images/20190221/1550741186_5c6e6ec21a781.png!small)

测试过程中发现，blacklist模式不生效，Pineapple
没有发出数据包；normal模式可以使用，但已经认证成功并通信的连接无法阻断，只能攻击正在进行认证的连接

 **DNS/DNSMasq Spoof DNS欺骗**

这个插件会启动 DNSMasq 服务，对客户端访问的域名进行重定向

在Hosts处填写要重定向的域名，写法与其他 Hosts 文件一致

此处可以填写内网配置好的钓鱼服务器，也可以指到Pineapple，并在上面搭建服务

![24.png](https://image.3001.net/images/20190221/1550741170_5c6e6eb288742.png!small)

点击 Start 之后，重定向就开始了，ping 域名可以发现被重定向到了内部网络IP

![25.png](https://image.3001.net/images/20190221/1550741156_5c6e6ea42e418.png!small)

针对钓鱼页面，可以修改Landing Page，也可以编写自己的页面，网页储存位置位于 /www 中

![26.png](https://image.3001.net/images/20190221/1550741138_5c6e6e9272d7f.png!small)

支持 php 和 html

![27.png](https://image.3001.net/images/20190221/1550741124_5c6e6e84201d8.png!small)

 **urlsnarf URL捕获**

选定网口后点击 Start ，模块将会捕获全部的HTTP流量，GET及POST的数据均会显示

显示格式为web访问日志类型

![28.png](https://image.3001.net/images/20190221/1550741101_5c6e6e6ddcd60.png!small)

 **Evil Portal 恶意门户认证**

模块主要由以下几个部分组成：

Controls（控制）：启用模块和设置自动启动；

Word Bench（创建工作目录）：包含门户页面的php文件等；

White List（白名单）：不需要通过门户认证页面跳转的IP地址列表；

Authorized Clients（认证客户端）：当前通过门户页面认证跳转过的IP地址列表；

Live Preview（预览）：预览恶意门户页面。

Evil Portal模块和自带的Landing Page功能很像，区别在于Landing
Page仅能够提供一个强制跳转显示页面的效果，不具有认证、白名单以及更自由化的门户页面自定义功能。Evil
Portal能够实现像现在的商业WiFi接入访问一样，提供一个由我们自定义的认证页面，引导客户端用户完成认证及跳转功能

新建名为 test1 的项目，系统会自动生成三个页面

![29.png](https://image.3001.net/images/20190221/1550741079_5c6e6e574c7d7.png!small)

可以随意修改三个页面达到想要的效果，也可以SSH登录到Nano的系统中，找到Evil Portal的配置文件夹直接将我们编辑好的页面复制进去

如果要启动该项目，需要点击 Activate 按钮进行激活，就可以在 Live Preview 功能下看到页面状况

![30.png](https://image.3001.net/images/20190221/1550741060_5c6e6e4499e1a.png!small)

启用模块后，凡是连接Pineapple wifi的客户端，均需要进行认证后再连接网络

下面进行一个简单的示例，我们修改源代码

index.php

![31.png](https://image.3001.net/images/20190221/1550741044_5c6e6e34c6ff8.png!small)

MyPortal.php

![32.png](https://image.3001.net/images/20190221/1550741029_5c6e6e2564be4.png!small)

此处注意目录的写权限，否则可能保存不成功

ssh到Pineapple或使用Cabinet模块管理文件，在模块所在路径下创建portal.log

认证一下，看看新建的log文件中是否记录

![33.png](https://image.3001.net/images/20190221/1550741012_5c6e6e143bc0a.png!small)

连接后的客户端也会被记录

![34.png](https://image.3001.net/images/20190221/1550740995_5c6e6e0308423.png!small)

 **ettercap 中间人攻击**

这个模块相当于调用 ettercap 这款工具进行中间人欺骗，将参数转换为web页面，并将输出返回到页面上

![35.png](https://image.3001.net/images/20190221/1550740974_5c6e6dee27bc6.png!small)

 **SSLsplit SSL分离**

SSLsplit可以作为中间人监听 SSL 信息及 HTTP 信息。SSL
实现代理的同时要与服务器建立连接，同时伪造证书与客户端建立连接，即双连接，依据获取的 Client 信息再与服务器通信，从而实现明文数据监听

Configuration无需改变，使用默认即可

在客户端使用HTTPS进行通讯时，将会由SSLsplit作为中间代理

![36.png](https://image.3001.net/images/20190221/1550740958_5c6e6ddea6470.png!small)

SLLsplit的实现需要配合其他欺骗手段，如果有Clients连接到Pineapple，那么就直接可以进行攻击，如果要攻击的目标在同一网段内，则需要将目标流量定向到此模块的监听端口，通常配合
ettercap等欺骗软件

如果网站具有HSTS（HTTP Strict Transport Security）,网站将不能正常显示，也就无法攻击

 **tcpdump 网络数据采集**

tcpdump可以将网络中传送的数据包完全截获下来提供分析。它支持针对网络层、协议、主机、网络或端口的过滤，并提供and、or、not等逻辑语句来去掉无用的信息，是一款非常高级的网络数据分析工具

与Pineapple上很多其他的模块一样，提供的可供点选的web管理界面

Options提供了基本的选项模块

![37.png](https://image.3001.net/images/20190221/1550740942_5c6e6dce5fb09.png!small)

在下方选中或勾选的参数将会被格式化到 Command 处

Interface 为需要监听的端口

Verbose 对应 -v 选项，代表输出报文信息的详细程度

Resolve 对应 -n 选项，不将主机名转换为IP地址，以及不进行端口名称的转换

Timestamp 对应 -t 选项，指定是否输出时间戳或时间戳格式

Don’t print domain name qualification of host names:对应 -N
选项，不输出主机名中的域名部分。例如，’wiki.ver007.org’只输出’wiki’

Show the packet’s contents in both hex and ASCII:对应 -X
选项，在解析和打印时，除了打印每个包的报头之外，还要用十六进制和ASCII打印每个包的数据（通常用于分析一种协议）

Print absolute sequence numbers：对应 -S 选项，将tcp的序列号以绝对值形式输出

Get the ethernet header as well：对应 -e 选项，在输出行打印出数据链路层的头部信息

Show less protocol information：对应 -q 选项，快速输出。只输出较少的协议信息

Monitor mode：对应 -I 选项，使标准输出变为缓冲行形式，可以把数据导出到文件

Filter提供了一些过滤规则，我们可以利用Filter编写过滤表达式，用来匹配得到我们想要的结果，在点选参数之后，手动输入参数值，并继续点击下一个参数，同样的，如果你熟悉tcpdump的话，可以进行手工填写，跟wireshark什么的过滤语法道理都类似

![38.png](https://image.3001.net/images/20190221/1550740925_5c6e6dbd71745.png!small)

Output为系统回显，History则可以查看和管理抓住的完整tcp数据包

![39.png](https://image.3001.net/images/20190221/1550740910_5c6e6dae992f2.png!small)

例如，我想查看172.16.42.225和m.tool.chinaz.com之间端口为80的通讯

![40.png](https://image.3001.net/images/20190221/1550740892_5c6e6d9ce1c82.png!small)

Output中输出一些信息

![41.png](https://image.3001.net/images/20190221/1550740874_5c6e6d8a78e9b.png!small)

history中能看到捕获的数据包

![42.png](https://image.3001.net/images/20190221/1550740859_5c6e6d7b845ab.png!small)

在此处可以将捕获的包下载，得到一个pcap文件，可以在wireshark、networkminer、科来等其他工具中

具体的使用方法就根据需求不同定制，需要熟悉过滤表达式的编写

需要注意的是，tcpdump只能抓取流经本机的数据包，因此确保有 Client 连接上网

由于页面仅提供部分命令，如果想要达到与命令行完全一样的效果，可以SSH连接到Pineapple直接运行tcpdump.sh，路径在/pineapple/modules/tcpdump/scripts

**Meterpreter 漏洞攻击**

大名鼎鼎的 Meterpreter，配置主机端口后能够接收会话，无需更多介绍

![43.png](https://image.3001.net/images/20190221/1550740839_5c6e6d6702373.png!small)

 **nmap 网络地图**

著名的网络扫描工具，用法一模一样

Options（选项）与图形化的Nmap页面相似，输入目标，在 Profile 中选择一些预置的规则

各种参数设置在下面可以手动点选

![44.png](https://image.3001.net/images/20190221/1550740821_5c6e6d5555d19.png!small)

也可以在 Command 处手动输入参数

![45.png](https://image.3001.net/images/20190221/1550740803_5c6e6d43c86f3.png!small)

结果会回显在 Output 中，也可以在Log Manager模块中查看记录结果

![46.png](https://image.3001.net/images/20190221/1550740787_5c6e6d336f23d.png!small)

测试发现无论针对内网和外网扫描，过程都比较慢，而且经常有进程退出的情况，效果不是很好

 **APITokens API令牌**

/api 允许对Pineapple模块进行远程调用，存储路径为/pineapple/api

已生成的API令牌存储在Pineapple本地数据库中，路径为/etc/pineapple/pineapple.db

本模块的作用就是提供对API调用的访问控制

只有在本模块中生成APIToken，并作为JSON参数进行传递时，Pineapple才会返回结果

 **autossh 反向SSH连接**

autossh是一个程序，原理是启动一个 ssh 副本并进行监视，如果进程中断或停止流量传输，则根据需要重新启动

想法来自rstunnel，但是由C语言编写的，使用端口转发循环或远程回显服务进行连接监视

当遇到连接被拒绝等快速故障时，能够降低连接尝试的速率

多数情况下，程序用于反向SSH，以及解决连接不稳定等问题，利用这个模块，我们可以利用具有公网IP的VPS随时随地连接到 Pineapple 下进行操作

例如VPS 用户是 root IP是 1.1.1.1 SSH端口是 22，在反向连接Pineapple时，需要登录的端口是 8888

那么应该如下填写

![47.png](https://image.3001.net/images/20190221/1550740769_5c6e6d218787b.png!small)

填写后点击Save保存到下方的命令行中

![48.png](https://image.3001.net/images/20190221/1550740751_5c6e6d0f2a19b.png!small)

在Additional Configuration（附加配置）中生成公钥

![49.png](https://image.3001.net/images/20190221/1550740727_5c6e6cf7afa60.png!small)

SSH到 Pineapple中，执行

    
    
    cat ~/.ssh/id_rsa.autossh.pub | ssh -p 22 root@1.1.1.1 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'

输入VPS密码，将Pineapple公钥导入VPS的authorized_keys中

点击Start

此时 SSH 反向连接已经建立，可以随时随地在VPS中ssh连接到 Pineapple

在vps中输入

    
    
    ssh localhost -p 8888

再输入Pineapple NANO 的密码，即可成功登录

![50.png](https://image.3001.net/images/20190221/1550740708_5c6e6ce42e6a8.png!small)

 **base64encdec BASE64编/解码**

一个普通的 base64 编码/解码 模块

![51.png](https://image.3001.net/images/20190221/1550740689_5c6e6cd14c7b3.png!small)

 **Cabinet 文件管理**

可以理解为一个文件管理的webshell（-_-||）

![52.png](https://image.3001.net/images/20190221/1550740671_5c6e6cbfbded2.png!small)

 **Commander 指挥者**

此模块能够允许我们通过IRC来控制Pineapple

![53.png](https://image.3001.net/images/20190221/1550740655_5c6e6caf5ac40.png!small)

下面这个图是官方论坛截的，从来没用过IRC，这辈子可能都不会用了，此模块略过了

![54.png](https://image.3001.net/images/20190221/1550740640_5c6e6ca0e466a.png!small)

 **ConnectedClients 已连接客户端**

这个模块直观的显示通过不同网卡连接的不同客户端

包括主机名称、IP地址、MAC地址

可以对客户端进行 Disassociate（取消关联）、Deauthenticate（解除认证）、Blachlist（黑名单）操作

![55.png](https://image.3001.net/images/20190221/1550740617_5c6e6c896d6dd.png!small)

**CursedScreech 命令执行**

这是一个远控模块

![56.png](https://image.3001.net/images/20190221/1550740594_5c6e6c72167e9.png!small)

Sein：信息收集功能，当监听的网络内出现漏洞系统时，将会更新模块的 target 列表

Kuro：攻击功能，自动尝试连接Sein功能发现的目标机器，并连接

![57.png](https://image.3001.net/images/20190221/1550740568_5c6e6c58e1b17.png!small)

Listening Interface（监听端口）：用于组播socket的接口，如果目标直接连接到Pineapple，使用br-lan就可以

Multicast Group（组播组）：发送和接收目标心跳的地址，对于Sein和目标机器，组需要相同

Multicast Port（组播端口）：Sein将从目标接收消息的端口。这个端口需要在payload的startMulticaster()方法中

Heartbeat Interval（心跳间隔）：payload发送广播的间隔，Sein在3个心跳间隔还为收到广播包的话，就会判断目标为掉线状态

Kuro Keys/Target Keys（密钥）：用于TLS通信时的密钥，可以使用Papers模块创建Keys

可以从下方两个下载按钮下载 C# 和 Python 的payload模板

![58.png](https://image.3001.net/images/20190221/1550740547_5c6e6c43cbf1b.png!small)

Activity Log（活动日志）：记录 Kuro 功能执行过程中产生的全部记录，使用模块的大部分时间都是盯着这里看

右边的Targets就是一个上线机器列表，以及一个命令执行功能

如果有目标机器的话，可以通过Select选择机器，并执行命令

EZ Cmds事先预置了一些cmd命令，可以添加及删除

![59.png](https://image.3001.net/images/20190221/1550740520_5c6e6c287a6bb.png!small)

设置好了之后，按照下载的模板，编写payload，在目标机器上运行

运行后点击Sein进行监听，测试时发现python版本的payload在监听后需要多等一下才能上线，此处要耐心等待一下，上线后可以开启Kuro，再耐心多等一会

当日志显示Kuro is ready后，就可以执行命令了

![60.png](https://image.3001.net/images/20190221/1550740499_5c6e6c133900f.png!small)

 **dump1090 接收/解码无线信号**

本模块能够对 1090MHz 的无线电进行收取和解码，通过调用google-API等方式，可以在web地图上描绘出飞机的轨迹，当然也可以手动更改频率如：

我国民航使用的无线电频率：1090MHz

民用对讲机使用的无线电频率：408-409MHz

警用频率：350-390MHz

等等

![61.png](https://image.3001.net/images/20190221/1550740473_5c6e6bf945038.png!small)

软件有很多参数，但是界面上只显示了Gain

Checkbox 参数可以切换度量衡使用公制单位、切换到自动获取、增大功率、将结果输出为csv格式

使用此模块需要RTL-SDR（电视棒）接收无线电信号，插入模块，将显示地图

![62.png](https://image.3001.net/images/20190221/1550740443_5c6e6bdb32f4b.png!small)

 **get 获取**

get模块用于获取客户端连接信息，包括浏览器和相关插件

![63.png](https://image.3001.net/images/20190221/1550740423_5c6e6bc7bad04.png!small)

能够获取连接到 Pineapple 的 Clients信息，点击View Information能够查看获取的详细信息

![64.png](https://image.3001.net/images/20190221/1550740394_5c6e6baad4a42.png!small)

识别库比较老，插件识别的也比较少，能够获取屏幕尺寸还是挺惊喜的，不过在实战用处一般

 **HackRF 无线电攻击**

这个模块需要配合HackRF 硬件进行使用，在接入HackRF后，会出现一个简单的设置界面

![65.png](https://image.3001.net/images/20190221/1550740355_5c6e6b83eaf81.png!small)

模块选项相当于 hackrf_transfer 的相关参数

> Sample Rate（采样率）：每秒发送或接受的样本量。受到系统计算能力限制，设置过高可能会导致系统不稳定，此处建议设置默认10M或更低，相当于 -s
>
> Center Frequency（中心频率）：就是HackRF开始调谐的频率，相当于 -f
>
> Transceiever Mode（收发方式）：HackRF是半双工工作模式，因此必须指定是要 TX（发送）还是RX（接收），相当于 -t 或 -r
>
> File Name（文件名）：目标文件路径，可以将收到的信号记录，也可以从文件发送
>
> RF Amp & Antenna Power（射频放大器和天线功率）：Enable RF AMP可以指定是否开启射频放大器，Antenna
> Power可以指定功率是否被传送到天线端口
>
> RX IF Gain & RX BB Gain（RX二中频增益和RX BB增益）：根据不同层级的db及步长选择增益模式
>
> Repeat Transmission & TX IF Gain（重复和TX二中频增益）：是否重复播放，以及设置发送增益

先进行录制，并保存到文件中

![65-1.png](https://image.3001.net/images/20190221/1550740330_5c6e6b6a949c0.png!small)

然后进行重放，即可攻击成功，如果重放失败，可以调整放大器的增益

![65-2.png](https://image.3001.net/images/20190221/1550740296_5c6e6b480c0d6.png!small)

在实际测试过程中，将会如上图报错，调试了一会依旧无法实现功能

这个模块仅仅是简单的收取/重放，如果想要解码、编码再重放，单靠这个是实现不了的，而且在不清楚无线电工作频率的情况下还是没有办法使用，因此还是将其定义为演示模块

 **Key Manager 密钥管理**

如题，本模块是用于SSH密钥管理的模块

生成SSH Key Pair之后，自定义Remote Host（远程主机）主机名、端口、账户、密码

下面两个按钮就是将自己的公钥复制到对方的主机上，或将对方的公钥加入自己的主机上

![66.png](https://image.3001.net/images/20190221/1550740271_5c6e6b2f31ef1.png!small)

在Known Hosts（已知主机）中可查看和管理目前已保存的一些公钥

 **LED Controller LED灯控制**

如题，就是一个控制LED灯的模块

![67.png](https://image.3001.net/images/20190221/1550740249_5c6e6b194f44c.png!small)

Trigger（触发器）有三个选项

Netdev：在网络传输时会闪烁，Mode（模式） TX 代表发送 RX 代表接收，Interface 输入要监听的网口

Timer（计时器）：将会根据设置的On和OFF时间进行交替亮灭，差不多是个呼吸灯，单位是 ms（毫秒）

![68.png](https://image.3001.net/images/20190221/1550740202_5c6e6aea3388c.png!small)

设置为None时将会常亮，测试效果没有图，但模块还是好用的

 **Log Manager 日志管理**

该模块能够查看和管理各个模块产生的日志

能够显示名称、模块、大小、日期，并能够查看、下载和删除

![69.png](https://image.3001.net/images/20190221/1550740179_5c6e6ad3ef75d.png!small)

 **Modem Manager 调制解调器管理**

这个模块允许Pineapple通过3G和4G USB调制解调器连接到互联网

![70.png](https://image.3001.net/images/20190221/1550740161_5c6e6ac12ac33.png!small)

这个模块暂时不知道怎么用，略过

**Module Maker 模块制作**

能够生成及管理模块

![71.png](https://image.3001.net/images/20190221/1550740141_5c6e6aad96dcd.png!small)

并给出了模块需要的模式

![72.png](https://image.3001.net/images/20190221/1550740123_5c6e6a9b3d23c.png!small)

是一个为开发者编写新模块的web界面

 **ngrep 网络抓取**

ngrep就相当于网络版的grep，支持大量的操作系统和网络协议。能识别TCP、UDP和ICMP包，理解bpf的过滤机制。与 tcpdump 类似

![73.png](https://image.3001.net/images/20190221/1550740103_5c6e6a87438bc.png!small)

 **Occupineapple 占领**

Occupineapple 是一个干扰模块，能够在周围生成各种随机或者自定义的SSID

![74.png](https://image.3001.net/images/20190221/1550740084_5c6e6a744eacf.png!small)

Speed：每秒发送的数据包

Channel：在哪个信道上生成虚假AP

Show station as Ad-Hoc：将站点显示为点对点

Set WEP bit (Generates encrypted networks)：设置WEP位（生成加密网络）

Show station using WPA TKIP encryption：显示使用WPA-TKIP加密的站点

Show station using WPA AES encryption：显示使用WPA-AES加密的站点

Use valid accesspoint MAC from OUI database：使用来自OUI数据库的有效Access

Editor 参数处可以选择、编辑或创建List，List中存放SSID名称及Mac地址

![75.png](https://image.3001.net/images/20190221/1550740061_5c6e6a5d86d69.png!small)

在配置好参数后，点击Start就会在周围生成List中名称的SSID

![76.png](https://image.3001.net/images/20190221/1550740046_5c6e6a4e8e115.png!small)

可以看到生成了事先预设的SSID

![77.png](https://image.3001.net/images/20190221/1550740030_5c6e6a3e24a81.png!small)

这个模块的作用目前只能想到有两个，第一个就是SSID广告，可以利用这个发布一些广告信息，第二个是导致无线网卡产生拒绝服务攻击

 **Online Hash Crack 在线哈希破解**

模块调用了[www.onlinehashcrack.com](http://www.onlinehashcrack.com)网站接口，可以将Hash值或后缀为.cap/.pacp/.hccapd的WPA握手包

传入模块中进行破解

先设置 Email，点击Save保存，结果将会输出到回显并发送到邮箱中

![78.png](https://image.3001.net/images/20190221/1550739996_5c6e6a1ca3b52.png!small)![79.png](https://image.3001.net/images/20190221/1550739996_5c6e6a1cc8fc3.png!small)

 **p0f 被动网络指纹识别**

p0f是万能的被动操作系统指纹工具，利用SYN数据包实现操作系统被动检测技术，能够正确地识别目标系统类型。和其他扫描软件不同，它不向目标系统发送任何的数据，只是被动地接受来自目标系统的数据进行分析。因此，一个很大的优点是：几乎无法被检测到，而且p0f是专门系统识别工具，其指纹数据库非常详尽，更新也比较快，适合于安装在网关中

依旧是一款在 KALI 中经常使用的信息收集软件，页面只给了设置网口的选项，没有提供其他参数选项

![80.png](https://image.3001.net/images/20190221/1550739970_5c6e6a02c0ad4.png!small)

测试过程中服务一直无法启动，暂略

 **Papers 证件**

Papers模块的作用就是生成 公/私 密钥对，X.509数字证书，能生成可部署自签名证书

有了这个模块我们可以在HTTPS上管理Pineapple，也可以让我们的钓鱼页面在HTTPS上部署，更具有一定的迷惑性

我们可以在此模块生成证书，让我们的管理端口1471,80，等其他端口均通过443转发，也可以下载后部署于其他服务器上

首先我们使用Build Certificates来生成证书

![81.png](https://image.3001.net/images/20190221/1550739940_5c6e69e4aece6.png!small)

Modify Certificate info（定义证书信息）：中包含了一些描述信息，可以自定义填写

Encrypt Private
Key（加密私钥）：选项勾选后，在访问时浏览器将会等待输入密码，在部署于其他网站应用时，应该进行勾选，但不建议在Pineapple上勾选

Export keys to PKCS#12 container：将密钥导出到PKCS#12用户密钥储存库中

填写完成之后点击Build Keys生成密钥对，我们就能在Certificate Store中查看和管理了

![82.png](https://image.3001.net/images/20190221/1550739920_5c6e69d0563ef.png!small)

生成证书存放位置/pineapple/modules/Papers/includes/ssl/

![83.png](https://image.3001.net/images/20190221/1550739897_5c6e69b9a89cf.png!small)

将生成的两个文件copy至/etc/nginx/ssl/

接下来我们配置nginx，修改 nginx 配置文件 /etc/nginx/nginx.conf

添加监听端口 443 ssl

![84.png](https://image.3001.net/images/20190221/1550739877_5c6e69a5b1318.png!small)

设置完重启 nginx，点击Actions选项中的小锁头按钮，Pineapple会自动将1471端口转发到443上， 此时就可以通过HTTPS进行访问了

由于证书是自签名，所以依旧会被浏览器标记为Not Secure（不安全），所以多少有点鸡肋，但是也具有一定的作用

 **Portal Auth 门户认证**

暂略

 **RandomRoll 随机翻滚**

这个模块是一个略微搞怪的模块，开启模块后，将会把全部 http 连接进行重定向到内置的黑页中

就是下面勾选的这些 rolls，每个对应一个黑页，随机选择出现

![85.png](https://image.3001.net/images/20190221/1550739856_5c6e69905e245.png!small)

模块开启后，客户机将会随机出现选中的黑页

![86.png](https://image.3001.net/images/20190221/1550739835_5c6e697b4411f.png!small)![87.png](https://image.3001.net/images/20190221/1550739835_5c6e697b8402a.png!small)

不同的黑页具有不同的动态图，有的还有背景音乐，挺有意思的  

**Responder 响应者**

依旧是一款非常有名的LLMNR欺骗工具，还可以伪造HTTP/s、SMB、SQL
Server、FTP、IMAP、POP3等多项服务，从而采用钓鱼的方式获取服务认证信息，如用户名和密码等

使用方式和其他嵌入式软件一样，选择网卡，勾选参数即可

![88.png](https://image.3001.net/images/20190221/1550739812_5c6e6964d4fea.png!small)

 **SignalStrength 信号强度**

选中一个网卡并扫描，将能够得到附近wifi信号的强度列表，原理是从iwlist命令收集信号强度和质量信息

![89.png](https://image.3001.net/images/20190221/1550739787_5c6e694b2b1c7.png!small)

能够将结果以列表形式展示

![90.png](https://image.3001.net/images/20190221/1550739767_5c6e6937cf7d1.png!small)

并绘制成饼状图，以供查看

![91.png](https://image.3001.net/images/20190221/1550739743_5c6e691f7e1b7.png!small)

在扫描过程中发现，使用 wlan0 能够更快的进行扫描，而使用 wlan1 能够获得更大的扫描范围

 **Site Survey 现场勘测**

如题，这就是一个对周边进行扫描勘测的模块

![1541921919969.png](https://image.3001.net/images/20190221/1550739380_5c6e67b48ee7e.png!small)

Interface 和 Monitor 需要两个网卡，一个作为通讯，一个作为监听

![92.png](https://image.3001.net/images/20190221/1550739160_5c6e66d8f0b3a.png!small)

点击Scan后可以进行扫描，结果将以列表的形式返回

对于SSID和MAC，可以通过下拉菜单放入PineAP中进行下一步操作

对于不同的网络，可以点击Capture进行抓包，也可以点击Deauth进行取消认证攻击

模块使用airodump-ng 使用ssid参数捕获，记录发现的接入点的坐标，并写入一个文本文件中

![93.png](https://image.3001.net/images/20190221/1550739134_5c6e66be4e041.png!small)

实际测试时，在此处使用Deauth会导致系统卡死，尤其是在使用wlan1作为监听网卡的时候，对此官方的回答是：你为什么要在进行初步勘测的时候就进行大范围的洪范类攻击？好吧，我竟无言以对

而且在测试WPA握手时，一直报告No，尝试了很多次都报告No，感觉功能是不好用的，如果想要在Pineapple上实现此功能，建议使用Aircrack

 **Status 状态**

Status模块是一个展示模块，展示出了系统各方面运行情况

![94.png](https://image.3001.net/images/20190221/1550739109_5c6e66a5b026e.png!small)![95.png](https://image.3001.net/images/20190221/1550739109_5c6e66a5d7e8c.png!small)

在网口处可以以图形实时显示一段时间内上下行流量状况  

![96.png](https://image.3001.net/images/20190221/1550739081_5c6e6689a0bc4.png!small)

**wps wps攻击**

此模块集成了 reaver 和 bully ，利用路由的wps漏洞来破解 WI-FI 密码

## 七 攻击场景

如果我们手里有Pineapple及一些相关设备，我们能进行哪些攻击呢？本章将列举一些攻击场景，并列出攻击场景使用的模块

### 1 简单搞怪

如果想要简单的搞怪一下周围的人，不进行恶意的破坏和复杂的攻击行为，可以使用Occupineapple或者RandomRoll模块

使用Occupineapple在四周生成一些有趣的SSID，比如“XXX是个小智障”，“XXX是个小笨蛋”等等，十分有趣

也可以使用RandomRoll，在有客户端连入Pineapple网络时，可以将HTTP网页重定向到默认搞怪的网页上，给人一个惊喜

### 2 技术演示

如果想要给身边的人演示一些简单的WI-FI攻击，无需特别多的技术准备，可以使用Dwall、DNS/DNSMasq Spoof、urlsnarf

Dwall即是著名的“绵羊墙”，可以显示抓到的URL、cookie、图片用，用来做演示十分方便

DNS/DNSMasq Spoof 可以重定向用户DNS，配合Landing Page或其他web应用可以进行钓鱼、嗅探等

urlsnarf显示网络内http数据包，抓取到的url，显示也很直观

配合HackRF硬件可以简单重放无线电攻击，进行一些演示

### 3 窃取密码

如果想要窃取在同一网络下其他客户端产生的密码，也许是某些网站账户密码，也许是其他WI-FI密码，有几种方式可以达到目的

想要获得附近的WI-FI密码，可以使用Site Survery抓取WPA握手包，再使用Online Hash Crack进行尝试破解

使用wps模块直接进行WI-FI密码破解

想要获得客户端在其他某些网站上的密码，可以使用Landing Page、Evil Portal、Portal
Auth制作钓鱼页面，结合ettercap做欺骗，或者让客户端连接到Pineapple网络中，在钓鱼页面输入密码，进行记录

也可以使用ettercap进行网络欺骗，将自己欺骗成为网关，获取流量，就可以截获明文传输的密码，配合SSLsplit即可抓取https传输的密码

使用Responder进行欺骗，窃取某些协议中的密码/hash值

### 4 漏洞利用

Pineapple还提供了一些漏洞利用模块，可以针对网络内漏洞进行攻击

可以通过ettercap欺骗，替换目标下载文件，可以改变js利用浏览器漏洞，可以改变文档利用office漏洞，可以改变exe利用各种漏洞

可以使用CursedScreech的payload进行监听和执行命令

也可以使用Meterpreter接收会话

这个总结起来就是，我是你的网关，你的全部网络流量我都做主，我想怎么玩就怎么玩

### 5 数据采集展示

如果使用Pineapple在网络内采集数据，用于展示或进一步分析的话，可以使用一些抓取类模块

tcpdump可以对网络数据进行抓取和过滤，配合其他软件可以进行展示

ngrep功能同上，对网络内数据进行抓取及展示

nmap用于网络内设备发现及扫描

p0f被动网络指纹识别，被动收集网络内系统指纹

get模块抓取客户端浏览器信息

dump1090配合电视棒，可以获取无线电信息，展示如飞机航线等信息

### 6 恶意破坏

如果就是想要搞事情，Pineapple也可以实现一些功能

可以使用ettercap进行网络欺骗，将自己欺骗成网关，可以导致断网

Deauth模块可以导致网络内认证失败，无法进行认证连接

## 八 操作Tips

在使用过程中，发现root用户没有访问写权限，比如无法更改配置文件，在页面修改的文件保存不生效等等，此时应重新挂载磁盘，并赋予写权限

有时候想要对整个Pineapple进行备份，所有模块同时备份，然后一键恢复，但是Pineapple本身不提供这种功能，所以解决办法就是/etc/config
下的文件整体复制，能够解决大部分的问题

如果想快速确定Pineapple是否连接网络，只需点击首页加载信息的按钮，如果能够获得官网信息，则已经联网

![97.png](https://image.3001.net/images/20190221/1550739045_5c6e66658fd0e.png!small)

WI-FI Pineapple可以在移动端使用，如果在公共场合嗅探，可以使用安卓手机进行管理，不会引人注目

在更改完模块配置后，千万不要忘了点击Save，否则测试一万遍模块都不好使的（都是眼泪）

测试过程中不一定完全依赖Pineapple本身，还可以配合一些常见的工具、平台进行进一步渗透，如Kali等

## 九 总体感受

玩了大概一周左右，最直观的感觉就是这玩意很坑（嗯，一个字足以概括）

其实本质来讲就是一台Linux系统机器+好几块网卡+一些很牛的软件

只不过有些人把这些东西放在了一起，做了个PHP web界面，并将硬件缩小化，然后就拿出来卖了

所以学习使用这款工具，就变成了学习使用很多软件怎么使用

使用过程中也不是很愉快，经常出现断网、wifi无法连接、机器卡死、页面刷新不出来等等

而且有一些模块用起来确实是不太好用的，大多数模块都是网上很有名的软件（kali中也有收录），只是做了个web页面而已，而且点选复杂，还不能覆盖全部参数

但是毋庸置疑，WI-FI Pineapple确实能够实现一些网络攻击方式，并且有一些有趣的模块以供选择，模块更新速度很快，也可以自定义模块

因此，对于手中这款 WI-FI Pineapple
NANO，作为学习、研究、演示用，还是可以的，但如果作为实际环境攻击、大型网络嗅探等较为复杂的环境，鉴于计算能力或其他各方面的限制，可能表现的不是那么优秀

而且在实现一些接近实际环境的渗透测试时，需要一定的shell编程/php编程/python编程/网络流量分析等等技能，不同模块涉及知识面不同，需要多方面学习

建议手头宽裕、有一定编程基础、并想要对WI-FI渗透进行入门学习研究的同学入手

在测试时，如果思路广一点，可以实现很多组合攻击，如ettercap配合BeEF，XSS平台，配合metasploit，配合CobaltStrike，Evil
Portal配合实时双因子认证钓鱼，网络嗅探类配合被动扫描等等，下面给一张图自己体会：

![98.png](https://image.3001.net/images/20190221/1550739026_5c6e665297173.png!small)

具体实现就需要大家自己开脑洞并研究了

## 十 参考链接

官方wiki：<https://wiki.wifipineapple.com/#!index.md>

官方论坛：<https://forums.hak5.org/>

Modules库：<https://github.com/hak5/wifipineapple-modules>

中文用户手册：<http://www.wifipi.org:8080/WiFiPineapple-%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C-V1.3.pdf>

搭建视频：<https://www.youtube.com/watch?v=Nv1eiIwOPKo>

模块编写视频：<https://www.youtube.com/watch?v=Lvf2At3G1C0>

SSLsplit模块：<https://www.roe.ch/SSLsplit>

ettercap模块：<https://github.com/Ettercap/ettercap>

autossh模块：<https://blog.csdn.net/fanwenjieok/article/details/53033317>

dump1090 模块：<http://www.satsignal.eu/raspberry-pi/dump1090.html>

tcpdump 模块：<http://www.tcpdump.org/>

ngrep 模块：<https://www.trustauth.cn/wiki/10824.html>

CursedScreech 模块：<https://github.com/sud0nick/CursedScreech>

Reaponder 模块：<https://github.com/SpiderLabs/Responder>

组合案例演示视频：<https://www.youtube.com/watch?v=Bvo43JvmeW0>

 ***本文作者：安百科技，转载请注明来自FreeBuf.COM**

