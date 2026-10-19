![1657607524_62cd15641a1192a582fcb.png!small?1657607525503](https://image.3001.net/images/20220712/1657607524_62cd15641a1192a582fcb.png!small?1657607525503)

## 一、工具介绍

Social-Engineer Toolkit
是一个专为社会工程设计的开源渗透测试框架，可以帮助或辅助你完成二维码攻击、可插拔介质攻击、鱼叉攻击和水坑攻击等。SET
本身提供了大量攻击选项，可让您快速进行信任型攻击，也是一款高度自定义工具。 SET 是 TrustedSec, LLC
的产品，该公司是一家位于俄亥俄州克利夫兰的信息安全咨询公司。Social-Engineer Toolkit 则是由TrustedSec的创始人Dave
Kennedy所创建和编写。

## 二、工具安装

命令行键入：git clone https://github.com/trustedsec/social-engineer-toolkit.git

## 三、工具使用

### 初始界面

命令行键入：setoolkit![1656924427_62c2a90b733b280a1630e.png!small](https://image.3001.net/images/20220704/1656924427_62c2a90b733b280a1630e.png!small)

1) Social-Engineering Attacks  
2) Penetration Testing (Fast-Track)  
3) Third Party Modules  
4) Update the Social-Engineer Toolkit  
5) Update SET configuration  
6) Help, Credits, and About

1) 社会工程攻击  
2) 渗透测试（快速通道）  
3) 第三方模块  
4) 更新社会工程师工具包  
5) 更新 SET 配置  
6) 帮助、鸣谢和关于

###
所有模块![1656925226_62c2ac2aa55ea84ba19a4.png!small?1656925227472](https://image.3001.net/images/20220704/1656925226_62c2ac2aa55ea84ba19a4.png!small?1656925227472)

1) Spear-Phishing Attack Vectors  
2) Website Attack Vectors  
3) Infectious Media Generator  
4) Create a Payload and Listener  
5) Mass Mailer Attack  
6) Arduino-Based Attack Vector  
7) Wireless Access Point Attack Vector  
8) QRCode Generator Attack Vector  
9) Powershell Attack Vectors  
10) Third Party Modules

1) 鱼叉式网络钓鱼攻击  
2) 网站攻击  
3) 传染性媒体生成器  
4) 创建有效负载和侦听器  
5) 群发邮件攻击  
6) 基于 Arduino 的攻击  
7) 无线接入点攻击  
8) 二维码攻击生成器  
9) Powershell 攻击  
10) 第三方模块

该款工具的使用方法非常简单 ，我们可以直接通过数字 **（1、2、3、4……）**
在交互式的命令行界面进行使用，接下来我会为大家讲解每个模块，部分模块为了让大家便于理解而并没有选择直译，但不会影响到大家使用或导致差异。现在世界各地的企业都开始流行
**BYOC（Bring Your Own Compute）、BYOD（Bring Your Own Device）和BYOL（Bring Your Own
Laptop）** 办公。使得企业员工更容易受到社会工程学攻击，从而影响到企业安全。

### 模块一：Spear-Phishing Attack Vectors
基于邮件媒介的钓鱼攻击![1656925572_62c2ad848e3175ce7dca0.png!small?1656925573180](https://image.3001.net/images/20220704/1656925572_62c2ad848e3175ce7dca0.png!small?1656925573180)

The Social-Engineer
Toolkit支持多种鱼叉式攻击，无论你身处红队实施攻击，还是身处蓝队完成溯源分析和溯源反制，它都可以是你的大杀器。在这个模块中，The Social-Engineer Toolkit可以帮助或辅助你完成
**Phishing和Whaling。**![1656935219_62c2d333ca60283f26de4.png!small?1656935220475](https://image.3001.net/images/20220704/1656935219_62c2d333ca60283f26de4.png!small?1656935220475)

支持高度自定义可扩展可联动的工具是一个真正好工具的重要体现，SET的几乎每个模块都既提供了默认的temples，也支持自定义。这个模块中你可以使用Gmail或者其他邮箱，在最后还可以自动调用C2框架进行监听。![1657626934_62cd6136cacb8393e49c8.png!small](https://image.3001.net/images/20220712/1657626934_62cd6136cacb8393e49c8.png!small)

作为演示，我们这里直接使用模板，SET给
大家提供了一些模板可以直接使用，我们这里选择DLL劫持攻击。![1657627295_62cd629f4b1bade868545.png!small?1657627296495](https://image.3001.net/images/20220712/1657627295_62cd629f4b1bade868545.png!small?1657627296495)

选择攻击载荷。![1657627422_62cd631ee190e0ae29cf9.png!small?1657627424063](https://image.3001.net/images/20220712/1657627422_62cd631ee190e0ae29cf9.png!small?1657627424063)

端口我们这里设置默认。![1657627513_62cd63796b2c53f4e6f56.png!small?1657627514783](https://image.3001.net/images/20220712/1657627513_62cd63796b2c53f4e6f56.png!small?1657627514783)

选择回连载荷。![1657627631_62cd63efaa2cd6013a300.png!small?1657627633176](https://image.3001.net/images/20220712/1657627631_62cd63efaa2cd6013a300.png!small?1657627633176)

选择文件扩展类型。![1657627700_62cd64347bbbd9418c8a2.png!small?1657627702125](https://image.3001.net/images/20220712/1657627700_62cd64347bbbd9418c8a2.png!small?1657627702125)

安装RAR。![1657627716_62cd64441072d9c04f8c9.png!small?1657627717498](https://image.3001.net/images/20220712/1657627716_62cd64441072d9c04f8c9.png!small?1657627717498)

或者安装ZIP。![1657896021_62d17c55e44552e7dcc7e.png!small?1657896023763](https://image.3001.net/images/20220715/1657896021_62d17c55e44552e7dcc7e.png!small?1657896023763)

设置文件名并选择一种压缩方式。![1657627178_62cd622a9f842da8141a7.png!small?1657627179885](https://image.3001.net/images/20220712/1657627178_62cd622a9f842da8141a7.png!small?1657627179885)

确认是否要重命名该文件。![1657896298_62d17d6a073d073de7058.png!small?1657896299751](https://image.3001.net/images/20220715/1657896298_62d17d6a073d073de7058.png!small?1657896299751)

选择向单个/多个邮箱发起攻击。![1657628700_62cd681cd30986badd677.png!small?1657628702973](https://image.3001.net/images/20220712/1657628700_62cd681cd30986badd677.png!small?1657628702973)

选择使用的预定义邮件模板/制作一次性邮件模板。![1657874858_62d129aa130dfe66a6fcc.png!small?1657874859940](https://image.3001.net/images/20220715/1657874858_62d129aa130dfe66a6fcc.png!small?1657874859940)

我选择了使用预定义邮件模板，所以大家可以看到这里提供了一些，我们随便选择一个，这将关系到邮件的内容。![1657874945_62d12a016bf4e13a98530.png!small?1657874947218](https://image.3001.net/images/20220715/1657874945_62d12a016bf4e13a98530.png!small?1657874947218)

设置一个收件邮箱（被攻击者）。![1657896648_62d17ec8c581ab4d0f3f5.png!small](https://image.3001.net/images/20220715/1657896648_62d17ec8c581ab4d0f3f5.png!small)

设置一个发件邮箱（攻击者）。![1657875107_62d12aa39bf7cd8aca0ee.png!small?1657875109362](https://image.3001.net/images/20220715/1657875107_62d12aa39bf7cd8aca0ee.png!small?1657875109362)

邮件已经成功发送，并自动调用C2框架开始监听。

### 模块二：Website Attack Vectors
基于网站媒介的钓鱼攻击![1656936444_62c2d7fc3773d8ad776b3.png!small?1656936444874](https://image.3001.net/images/20220704/1656936444_62c2d7fc3773d8ad776b3.png!small?1656936444874)

在这个模块中，The Social-Engineer
Toolkit具有克隆整个网站然后在本地托管的强大功能，它拥有网站的精确克隆的绝对优势，当然同样支持自定义模板，但需要你具备一定的 **HTML**
基础。![1657875147_62d12acbd8d0c5a3caeef.png!small?1657875150450](https://image.3001.net/images/20220715/1657875147_62d12acbd8d0c5a3caeef.png!small?1657875150450)

这里提供了一些攻击类型，比如java应用攻击、浏览器漏洞攻击、凭据收割攻击、重写页面攻击、Web-jacking、Multi-Attack和HTA
attack。我们这里选择票据收割为大家演示。![1657876096_62d12e80a567702229fa5.png!small?1657876098401](https://image.3001.net/images/20220715/1657876096_62d12e80a567702229fa5.png!small?1657876098401)

这里可以选择模板或者站点克隆或自定义，我们直接使用模板。![1657876172_62d12ecc6b874aff3aa6f.png!small?1657876174970](https://image.3001.net/images/20220715/1657876172_62d12ecc6b874aff3aa6f.png!small?1657876174970)

设置收集提交数据的服务器地址。![1657876234_62d12f0a680ab0f176ccd.png!small?1657876236741](https://image.3001.net/images/20220715/1657876234_62d12f0a680ab0f176ccd.png!small?1657876236741)

选择模板后将自动完成创建。![1657876253_62d12f1d5d7256165a3ba.png!small?1657876255021](https://image.3001.net/images/20220715/1657876253_62d12f1d5d7256165a3ba.png!small?1657876255021)

当用户访问我们的服务器，会看到这个钓鱼页面。

![1657876312_62d12f586da4097a6ece4.png!small?1657876314097](https://image.3001.net/images/20220715/1657876312_62d12f586da4097a6ece4.png!small?1657876314097)

用户误认为时登录页面，并将自己的用户名和密码输入表单并进行登陆提交操作。![1657876397_62d12fade0e3affc15744.png!small?1657876399784](https://image.3001.net/images/20220715/1657876397_62d12fade0e3affc15744.png!small?1657876399784)

我们便得到了包含用户名和密码的凭据。这里我直接使用的模板，但在实战时，大家可以配合穿透工具，通过克隆或制作一些控制台登录界面，比如OA、EMS和CMS等服务的登录界面。此时，如果我们也已经劫持目标移动端或移动端APP，甚至可以通过劫持手机验证码等方式永久盗取账号等信息，但可能会触发风控和被对手发觉。

### 模块三：Infectious Media Generator
传播性恶意媒体文件生成器![1657876725_62d130f53b696d126d750.png!small?1657876726945](https://image.3001.net/images/20220715/1657876725_62d130f53b696d126d750.png!small?1657876726945)

在这个模块中，The Social-Engineer
Toolkit可以创建一个可以加载到可移动存储介质的恶意文件，并在插入目标计算机时用于传递有效载荷。当社会工程师想要将拇指驱动器放入目标的场所中并希望有人将它们拾取并插入计算机时，这是一个特别有用的功能。该工具还允许用户导入自己的恶意可执行文件或使用随附的可执行文件。该工具将恶意文件作为自动运行文件加载，这意味着它将在插入后立即由计算机运行，无需用户操作。![1657877032_62d13228458c42dbf7b65.png!small?1657877033938](https://image.3001.net/images/20220715/1657877032_62d13228458c42dbf7b65.png!small?1657877033938)

你可以选择生成特定的文件格式载荷或者标准格式载荷。![1657877087_62d1325f9c4f56319d646.png!small?1657877089380](https://image.3001.net/images/20220715/1657877087_62d1325f9c4f56319d646.png!small?1657877089380)

选择自己要使用的载荷。![1657877160_62d132a81484e677c4c4b.png!small?1657877161638](https://image.3001.net/images/20220715/1657877160_62d132a81484e677c4c4b.png!small?1657877161638)

设置选项参数。![1657877183_62d132bf7c9735d0f93e1.png!small?1657877185304](https://image.3001.net/images/20220715/1657877183_62d132bf7c9735d0f93e1.png!small?1657877185304)

此时载荷已经生成成功，只需要写入到CD/DVD/USB固件中。![1657877263_62d1330f54cdbac5888bc.png!small?1657877265013](https://image.3001.net/images/20220715/1657877263_62d1330f54cdbac5888bc.png!small?1657877265013)

SET会自动调用msf的监听模块帮我们监听。

### 模块四：Create a Payload and Listener
创建载荷并监听![1657877309_62d1333d696677ceba441.png!small?1657877311258](https://image.3001.net/images/20220715/1657877309_62d1333d696677ceba441.png!small?1657877311258)

在这个模块中，The Social-Engineer
Toolkit单独创建使用恶意载荷，并自动调用msf监听模块监听。![1657877432_62d133b8a8586f0e10368.png!small?1657877434401](https://image.3001.net/images/20220715/1657877432_62d133b8a8586f0e10368.png!small?1657877434401)

选择载荷。  
![1657890945_62d168814b5b11b87b81a.png!small?1657890946925](https://image.3001.net/images/20220715/1657890945_62d168814b5b11b87b81a.png!small?1657890946925)

设置选项参数。![1657890998_62d168b6bea8d8bd6241e.png!small?1657891000601](https://image.3001.net/images/20220715/1657890998_62d168b6bea8d8bd6241e.png!small?1657891000601)

SET会自动调用msf的监听模块帮我们监听。

### 模块五：Mass Mailer Attack
群发邮件攻击![1657877617_62d13471f2f2302552be3.png!small?1657877619671](https://image.3001.net/images/20220715/1657877617_62d13471f2f2302552be3.png!small?1657877619671)

在这个模块中，The Social-Engineer
Toolkit单独制作发送钓鱼邮件，并自动调用msf监听模块监听。![1657877675_62d134abc6e69e00d56bf.png!small?1657877677594](https://image.3001.net/images/20220715/1657877675_62d134abc6e69e00d56bf.png!small?1657877677594)

在之前的的过程中该模块也是充当了其它模块的一部分，已经给大家演示过了，有一点点鸡肋。![1657628339_62cd66b30d3ce6f8ccd30.png!small?1657628340342](https://image.3001.net/images/20220712/1657628339_62cd66b30d3ce6f8ccd30.png!small?1657628340342)

选择向单个/多个邮箱发起攻击。![1657628700_62cd681cd30986badd677.png!small?1657628702973](https://image.3001.net/images/20220712/1657628700_62cd681cd30986badd677.png!small?1657628702973)

选择使用的预定义邮件模板/制作一次性邮件模。![1657874858_62d129aa130dfe66a6fcc.png!small?1657874859940](https://image.3001.net/images/20220715/1657874858_62d129aa130dfe66a6fcc.png!small?1657874859940)

我在演示的时候选择了使用预定义邮件模板，所以大家可以看到这里提供了一些，我们随便选择一个，这将关系到邮件的内容。![1657874945_62d12a016bf4e13a98530.png!small?1657874947218](https://image.3001.net/images/20220715/1657874945_62d12a016bf4e13a98530.png!small?1657874947218)

设置一个收件邮箱（被攻击者）。![1657896648_62d17ec8c581ab4d0f3f5.png!small?1657896650437](https://image.3001.net/images/20220715/1657896648_62d17ec8c581ab4d0f3f5.png!small?1657896650437)

设置一个发件邮箱（攻击者）。![1657896782_62d17f4ea21d9ce1ba504.png!small?1657896784274](https://image.3001.net/images/20220715/1657896782_62d17f4ea21d9ce1ba504.png!small?1657896784274)

设置为高权重标注邮件。![1657875107_62d12aa39bf7cd8aca0ee.png!small?1657875109362](https://image.3001.net/images/20220715/1657875107_62d12aa39bf7cd8aca0ee.png!small?1657875109362)

SET会自动调用msf的监听模块帮我们监听。

### 模块六：Arduino-Based Attack Vector
基于Arduino的攻击![1657877800_62d135281f9ff01027563.png!small?1657877802038](https://image.3001.net/images/20220715/1657877800_62d135281f9ff01027563.png!small?1657877802038)

在这个模块中，我们会生成用于近源攻击的Arduino代码文件，基于 Arduino 的攻击向量利用基于 Arduino
的设备对设备进行编程。您可以利用板载的 Teensy存储，并且可以允许在物理上远程执行代码系统。由于设备已注册为 USB
键盘的它将绕过任何自动运行禁用或端点保护系统。![1657878239_62d136df39f7ab9e0469c.png!small?1657878242306](https://image.3001.net/images/20220715/1657878239_62d136df39f7ab9e0469c.png!small?1657878242306)

你需要购买Teensy USB 设备，并将生成的文件并通过 Arduino（用于对 Teensy 进行编程的 IDE）写入Teensy USB
设备。![1657878188_62d136acc9c1cc2d9f0c0.png!small?1657878190550](https://image.3001.net/images/20220715/1657878188_62d136acc9c1cc2d9f0c0.png!small?1657878190550)

选择一个载荷。![1657878204_62d136bc542a4d15006f8.png!small?1657878205926](https://image.3001.net/images/20220715/1657878204_62d136bc542a4d15006f8.png!small?1657878205926)

设置选项和自动监听。![1657878400_62d137808d5753a02376f.png!small?1657878402356](https://image.3001.net/images/20220715/1657878400_62d137808d5753a02376f.png!small?1657878402356)

选择创建的载荷。![1657627422_62cd631ee190e0ae29cf9.png!small?1657627424063](https://image.3001.net/images/20220712/1657627422_62cd631ee190e0ae29cf9.png!small?1657627424063)

设置监听端口。![1657878528_62d1380011b8290c2cd9d.png!small?1657878529740](https://image.3001.net/images/20220715/1657878528_62d1380011b8290c2cd9d.png!small?1657878529740)

选择注入的代码。![1657878547_62d13813c901c79bfb37b.png!small?1657878549443](https://image.3001.net/images/20220715/1657878547_62d13813c901c79bfb37b.png!small?1657878549443)

代码文件生成完成，需要将生成的文件并通过 Arduino（用于对 Teensy 进行编程的 IDE）写入Teensy USB
设备。笔者也尝试了通过树莓派进行编码。

### 模块七：Wireless Access Point Attack Vector
无线接入点攻击![1657878623_62d1385fadc2f6b8a14d0.png!small?1657878625396](https://image.3001.net/images/20220715/1657878623_62d1385fadc2f6b8a14d0.png!small?1657878625396)

在这个模块中，SET提供的另一个有效功能，它允许攻击者创建无线网络的克隆，当目标加入该克隆副本时，它会将他或她的浏览器定向到恶意站点。该功能利用了包括
**AirBase-ng、arpspoof和dnsspoof**
在内的工具组合，打出“组合拳”。关于此功能的工作原理没有太多要解释的，因为我们所要做的就是告诉SET启动无线接入点并指定要在攻击中使用的设备网卡。这很简单，但非常有效。它可以在组织中用于收集登录凭据。由于组织用户严重依赖组织提供的
Internet。其实，无线渗透测试出来evil twin还有很多别的攻击方式，常见的有Caffe
Latte、Hirte、KRACK等，一些攻击甚至可以破解WPS的WPS PIN。

### 模块八：QRCode Generator Attack Vector
二维码攻击生成器![1657878737_62d138d1ebf71acc05a30.png!small?1657878739625](https://image.3001.net/images/20220715/1657878737_62d138d1ebf71acc05a30.png!small?1657878739625)

在这个模块中，我们可以将搭配其它模块使用，将之前生成的钓鱼网站等资源转换成二维码。![1657878835_62d13933f05d80523a242.png!small?1657878837645](https://image.3001.net/images/20220715/1657878835_62d13933f05d80523a242.png!small?1657878837645)

设置二维码指向网站地址，这里写我们的钓鱼网站地址。![1657878879_62d1395fe6f95ad9b0704.png!small?1657878881903](https://image.3001.net/images/20220715/1657878879_62d1395fe6f95ad9b0704.png!small?1657878881903)

二维码生成完成，由于二维码无法直观的辨别安全性，制作者通常会将二维码贴至公共场合，或是掩盖合法二维码进行攻击。笔者最近在研究一项自己发表的议题，通过动态二维码（活码）替换静态二维码（死码）进行灵活的社会工程学攻击。

### 模块九：Powershell Attack Vectors Powershell
攻击![1657879138_62d13a622139662c4905d.png!small?1657879139751](https://image.3001.net/images/20220715/1657879138_62d13a622139662c4905d.png!small?1657879139751)

在这个模块当中我们将主要进行针对powershell的攻击，通常当我们进行到TTPs（请注意这里不是PTH和PTT）中的一个环节，将RAT传到目标主机时但无法加载，便可以考虑powershell。![1657879182_62d13a8e8c099c3131014.png!small?1657879184509](https://image.3001.net/images/20220715/1657879182_62d13a8e8c099c3131014.png!small?1657879184509)

选择一个模块。![1657879663_62d13c6faf228519a2f69.png!small?1657879665354](https://image.3001.net/images/20220715/1657879663_62d13c6faf228519a2f69.png!small?1657879665354)

设置选项参数。![1657879675_62d13c7b77b2c2aaec40c.png!small?1657879677253](https://image.3001.net/images/20220715/1657879675_62d13c7b77b2c2aaec40c.png!small?1657879677253)

当目标通过powershell运行代码时便会建立会话。

### 模块十：Third Party Modules
第三方模块![1657880857_62d141190c8585c9b3d7c.png!small?1657880858691](https://image.3001.net/images/20220715/1657880857_62d141190c8585c9b3d7c.png!small?1657880858691)![1657942345_62d2314927b0afd77a6f0.png!small?1657942346356](https://image.3001.net/images/20220716/1657942345_62d2314927b0afd77a6f0.png!small?1657942346356)

## 四、总结

Social-Engineer Toolkit曾是排名TOP 1 的社会工程学利用工具，对于Offensive Security和Defensive
Security都有它分享的价值，在笔者之前这款工具除TrustedSec官方的使用help外，国内和国外还没有一篇完整的使用教程。这是
**该工具在互联网的第一篇完全使用教程**
。笔者也对该工具进行了DIY，大家如果感兴趣可以自己进行尝试，添加一些属于自己的modules用于pentesting。麻省理工最新研究表明，AI/ML并不能很好的防止该类攻击。目前，对抗这种攻击最好的方法就是健全企业的网络安全规范和员工的网络安全意识。

## 五、作者

Hacker-零

###

