**作者：** 「Tencent Blade Team」 **Leonwxqian & Xbalien & Nicky**  
**公众号：腾讯安全应急响应中心<http://https://mp.weixin.qq.com/s/4kO3pU_tCDZmgj2CkROzMg>**

### **0x01 前言**

智能音箱是近几年最热门的智能设备，在销量的暴涨背后，各种智能音箱“偷听”的新闻也让人们非常担心智能音箱会泄露自己的隐私，而在2018年初Tencent
Blade
Team把关注点放在了智能音箱自身的安全漏洞上，当时国外的苹果，谷歌，亚马逊，以及国内的阿里巴巴，百度，小米均已加入了这个战场发布了各自的智能音箱产品，团队选取当时全球用户最多，破解难度最高的Amazon
Echo，Google
Home，小米AI音箱作为研究目标，耗时近一年时间完成了对这三款智能音箱的远程无接触式破解（静默窃听/RCE/ROOT）并协助厂商完成了漏洞修复。

### **0x02 概述**

Google Home是Google在2017年发布的系列智能音箱产品，在全球拥有超过5000万用户，销量仅次于Amazon Echo系列智能音箱。

![](https://images.seebug.org/content/images/2020/01/f54385af-d84e-405d-bb65-3416d636cc51.png-w331s)

在本文中，我们将分享Tencent Blade Team在2018年下半年利用多个漏洞远程攻破Google Home音箱实现远程代码执行的研究成果。

Google Home音箱采用精简版Chrome OS作为操作系统，这一系统之前普遍使用在Google
Chromecast产品中，研究资料较少，同时系统特性相比市面上其它基于Linux和Android系统的智能音箱存在着不少差异，所以破解难度更高，Google
Home与Amazon Echo都是这两年Mobile Pwn2own的奖金最高的IoT比赛项目。

![](https://images.seebug.org/content/images/2020/01/fb97e72d-45bb-46b8-9616-e49907faccd8.png-w331s)

### **0x03 固件提取与分析**

Google Home的系统固件并未公开下载，但Google遵循开源协议公开了Google Home音箱系统部分源代码资料，如下图，可以看到包含Google
Home/Chromecast系列设备固件的信息，包括Bootloader、Kernel以及系统部分二进制程序等，甚至还包括带符号的.o文件，这些文件能够帮助我们快速了解Google
Home/Chromecast系列的设备的概况。

![](https://images.seebug.org/content/images/2020/01/26e3cdb5-eeca-4ea6-8dc8-e8da07ee3037.png-w331s)

此外Google
Home在其OTA流程中虽然通过HTTPS请求检测是否存在新版本，但使用了HTTP的方式下载固件，所以当云端有新版本固件推送，设备下载更新包时可以通过局域网嗅探抓包的方式拿到固件（最佳时机是新设备第一次联网时）。

![](https://images.seebug.org/content/images/2020/01/97a274d6-d095-4450-9d9d-17578cb8a237.png-w331s)

除了抓包获取固件外，我们后期分析代码发现也可以主动模拟设备更新请求，获取不同设备最新的更新包。通过如下图中的CURL命令就能够获取，需要在请求中填入合适的设备版本以及对应产品的代号。

![](https://images.seebug.org/content/images/2020/01/7ad2b028-015b-4039-adcb-9dab0683bf22.png-w331s)

以上三种方法使我们可以比较方便的获得Google
Home的部分系统文件，但如果我们需要获得完整固件或者尝试通过修改系统文件的方式搭建漏洞调试环境，最快速及暴力的方法的还是从硬件下手，由于整个Google
Home系列产品硬件几乎类似，我们以Google Home mini为例进行拆解，发现其使用了Marvell的Amada系列主控，以及东芝的NAND
Flash芯片。

![](https://images.seebug.org/content/images/2020/01/dcef4639-6ce7-4e54-a491-255b66c4c976.png-w331s)

在简单尝试未发现主板存在烧录/调试接口后，我们使用热风枪将Flash芯片焊下，选择直接使用编程器读取Flash芯片中的固件。通过对比芯片的datasheet我们发现此芯片使用BGA67的封装方式，BGA的芯片封装方式在小型智能设备上很常见，不过由于我们没有找到适合BGA67的转接座将芯片测试座（如下图）导出的接口直接连接到编程器，所以我们需要使用飞线连接或设计一个新的转接座。

![](https://images.seebug.org/content/images/2020/01/8c89a9d9-5338-456d-9502-0452685a3f56.png-w331s)

由于从测试座直接人工焊接飞线难度过高（焊点间距不到1mm），我们选择了使用PCB设计软件自己设计一个转接座并转由淘宝PCB制板厂商生产了一块样板。

![](https://images.seebug.org/content/images/2020/01/9978344c-b96a-48b4-8a49-314882996c65.png-w331s)

此时我们可以将Flash转接座与RT809H编程器连接，并直接提取整个Flash芯片原始数据。

![](https://images.seebug.org/content/images/2020/01/6430c34b-44c2-4969-aa10-e1661fdbd047.png-w331s)

不同自带主控的EMMC芯片，我们从NAND
Flash芯片中提取的是原始Flash数据，还需要对其中的OOB数据及ECC校验位进行处理，最终才能解析出正确的文件系统与数据。

![](https://images.seebug.org/content/images/2020/01/9350c5e6-6f21-4332-b5dd-ea1e0f71e295.png-w331s)

以下就是Google Home的完整系统目录：

![](https://images.seebug.org/content/images/2020/01/88271846-6170-4483-965c-ff8b0309c030.png-w331s)

在对获取的固件包以及公开资源进行分析后，我们发现在整个Google
Home的启动流程中，Bootloader、boot.img以及system.img，都是需要通过安全校验才能加载的：

Bootloader和boot.img使用的签名方式相同，采用SHA256+RSA签名实现;在Bootloader正常流程中没有提供解锁的逻辑，只有签名验证通过才会加载boot.img;

![](https://images.seebug.org/content/images/2020/01/864f04ee-ca9d-4c3f-aaf3-09e04452f5ae.png-w331s)

除此之外，Google Home还对system.img进行验证。主要通过内核启用了Dm-verity验证机制，极大增加了通过硬件方法修改system.img完成实现root的难度。

![](https://images.seebug.org/content/images/2020/01/4d95d5bd-7bfd-483c-a9d8-a044664f2ef1.png-w331s)

在少数的系统程序中，最核心的cast_shell可以认为就是一个Chrome浏览器，这个进程同时也受沙箱机制的保护。

![](https://images.seebug.org/content/images/2020/01/841ddaee-e7bd-429d-8cd1-7da8eb1b11f9.png-w331s)

在Chrome OS上，沙箱机制主要涵盖setuid，user namespace 和seccomp-bpf。除此之外，在利用缓解措施方面，系统也启用了ASLR机制，cast_shell程序也包含了NX和Stack Canary。

### **0x04 Google Home攻击面**

![](https://images.seebug.org/content/images/2020/01/e3ccacdc-a805-47e7-8568-4659350d0aa5.png-w331s)

网络通信上，Google Home开放了多个端口，其中包含端口8008。这是HTTP服务器，方便用户在局域网内向Google
Home进行基本命令操作。若路由器开启了UPnP Forwarding，则有可能将局域网扩展到互联网，之前在youtube的网站上热传的Cast
Hack就是此原理进行批量远程攻击。8009端口主要是Google CAST 协议通信端口，采用TLS和protocol
buffer封装，我们发现CAST协议能够远程将任意页面推送到Google Home的cast_shell中访问，这得我们可以将攻击Google
Home转换为攻击Chrome浏览器；

无线协议上，Google Home使用的是Marvell的芯片，关于Marvell Wi-Fi , BLE固件攻击的思路都可以进行尝试。在去年的Zero
Nights会议上，就有关于Marvell Wi-Fi固件的攻击方法。

另外，效仿由HubCap（通过Bootloader
Usb协议处理的漏洞完成Chromecast的root），挖掘Bootloader里的漏洞也是可以尝试的思路。

### **0x05 Google Cast协议暗藏的风险**

在上节我们提到了CAST协议，在架构上Google
CAST协议包括Sender和Receiver。Sender可以是移动设备或者Chrome，而Receiver则是加载了CAST
APP的接收设备，例如Google Home就是一个Receiver。

![](https://images.seebug.org/content/images/2020/01/e40b46a0-4ff3-41a2-9d6f-d22990fa5020.png-w331s)

先来介绍CAST APP的加载流程，正如下图所示：

![](https://images.seebug.org/content/images/2020/01/b4dc4d8d-6c34-49b7-97ef-4047409ccb77.png-w331s)

当用户通过Sender（移动设备或者Chrome）访问了Sender
Application时，便会通过CAST协议寻找局域网内的Receiver并与之通信，接着Receiver会去CAST
APP市场拉取指定的APP链接并通过cast_shell加载访问。

在这个过程中，我们发现CAST协议存在着以下安全风险，这些风险将是后续攻击Google Home的关键所在：

  1. CAST APP可以是任何网页。若给定的CAST APP是恶意的网页，Google Home仍会访问它； 

  2. CAST应用商店中的应用可能是恶意的。当攻击者注册为CAST开发者后就可上传CAST应用，并且看起来并未经过严格审核，很快就可以发布并上线； 

  3. 局域网内，Sender可以直接发送CAST协议，甚至不需要用户交互。

综合以上几点安全风险，可以巧妙的把攻击Google Home转换为对浏览器的攻击。具体的攻击过程大致为以下思路：

  1. 攻击者欺骗用户通过Chrome浏览器或移动设备访问Sender Application。通过SENDER URL触发CAST协议让Google Home访问CAST RECEIVER URL（CAST APP链接地址）; 

  2. 若攻击者和Google Home位于同一个局域网，攻击者还可以直接与端口8009进行CAST协议交互（例如发送LAUNCH APP请求），直接触发Google Home访问CAST RECEIVER URL。 

  3. 更糟糕的是，若用户家中的路由器打开UPnP Forwarding，攻击者也可以在互联网上完成远程静默攻击。 

下图为CAST APP的发布界面与局域网触发CAST协议交互的代码：

![](https://images.seebug.org/content/images/2020/01/ae646f54-b4c8-4676-9119-df05263f1daa.png-w331s)

### **0x06 Magellan漏洞详情**

在确定了利用CAST协议作为我们的远程攻击入口后，我们开始对Google
Home中的核心程序cast_shell（Chrome浏览器）进行了漏洞审计，经过一段时间的研究我们在Chrome浏览器核心组件sqlite3中发现了多个高风险0day漏洞，我们把这组漏洞命名为Magellan。

Magellan漏洞对所有平台(Android、Chrome
OS、Windows、Linux、Mac)上的Chrome、Webview都会产生影响。包括使用Webview的产品，如Android
App内嵌webview网页浏览功能的APP，或使用sqlite3的客户端与服务器软件，如Apache+PHP等。

在下面的部分我们将介绍Magellan漏洞的相关细节。

**6.1 CVE-2018-20346**

fts3扩展中的`merge`操作可能允许攻击者泄漏堆数据或导致堆缓冲区溢出。

  * 表结构而言，fts3和fts4非常相似，在Chrome中关闭了fts4。

  * fts3和fts4都有一些表来存储节点信息。

  * sqlite不禁止用户修改(CREATE，INSERT，DELETE)这些表(%_SEGMENTS，%_SEGDIR，%_STAT)的数据。

  * fts4与fts3共享很多代码分支，可以通过添加一些特殊的内置表(如%_stat)来激活。

  * sqlite3使用assert()进行条件检查，但当Google构建Chrome时，assert变为void()，因为它不是debug版本。

因此，Google Chrome的发布版本中缺少许多关键条件检查，sqlite3中也会发生同样的事情。

  * 当我们伪造一些关键的内置表和记录，并调用`merge`函数时，该函数会从攻击者控制的内存区读取数据，并执行memcpy操作，从而导致一些堆相关问题。

通过下面的代码，我们可以触发漏洞：

![](https://images.seebug.org/content/images/2020/01/d7cf0673-4aa9-4ae3-9b61-f372f4fe9e17.png-w331s)

首先，我们尝试通过nodeReaderInit→nodeReaderNext读取错误的值nDoclist(由攻击者控制)。

然后，将恶意的nDoclist值传递给fts3AppendToNode，我们可能会在这两个地方导致堆缓冲区溢出：

![](https://images.seebug.org/content/images/2020/01/f4182778-b704-4ce8-a9f6-e8d25d31b3ba.png-w331s)

在我们的攻击中，我们选择使用第二个点，因为它更稳定和易于使用。

nDoclist和aDoclist是可控制的，pNode->a和pNode->n也可以由我们调整，因此我们可以做堆风水。

**6.2 CVE-2018-20505**

fts3扩展中的fts3ScanInteriorNode(`match`)可能允许攻击者泄漏堆数据或导致堆缓冲区溢出。

简单介绍要利用的步骤：

  1. 将%_segdir中的节点设置为不是根节点。

  2. 修改节点的BLOB数据。

  3. 调用`match`触发攻击。

有漏洞的函数如下：

![](https://images.seebug.org/content/images/2020/01/83305b8c-611f-44b6-9ba7-757c1cf94d6b.png-w331s)

1.函数fts3GetVariant32，该函数最多返回0x7fffffff的整数(输入数据为Little-endian，输入ff ff ff ff
07将产生输出0x7fffffff)。

代码将从BLOB(zNode)中提取nPrefix和nSuffix，BLOB可由攻击者控制。

![](https://images.seebug.org/content/images/2020/01/67949643-d003-44f1-8d5d-cfc74e4e7794.png-w331s)

2.第一次检查，将检查zCsr+nSuffix-1是否超过zEnd。

但在32位机器(如Google
Home)中，堆通常位于大于0x7fffffff的地址中，当加上另一个较大的数字(如0x7fffffff)时，必然存在整数溢出，结果可能非常小，此检查将通过。

![](https://images.seebug.org/content/images/2020/01/a29b9b47-b1d7-48be-9454-3d9e62d9d2a0.png-w331s)

zCsr是表示BLOB中当前位置的指针，zEnd是指向BLOB的最后一个字符的指针。

如zCsr=0xe00000000，zEnd=0xe0002000，nSuffix=0x20000001，zCsr+nSuffix的结果为0x1，小于zEnd，可以通过此检查。

总而言之，可能有2个条件：

a).nSuffix小于未处理的实际数据量。

b).nSuffix是一个巨大的数字，导致zCsr+nSuffix的整数溢出，我们认为b在Google Home中是可利用的。

选择的值将对下一次验证产生影响，我们将在此处将该值命名为“X”。

3、第二次检查

![](https://images.seebug.org/content/images/2020/01/9535c8e9-1842-45c1-a9ac-67278c00099c.png-w331s)

变量nAlloc是分配的缓冲区数量，通常每次值增加两倍。

请注意，nAlloc可以大于实际数据，并且不能保证重新分配的内存区内的数据是从原始BLOB获得的，因此我们可以在这里泄漏一些堆信息。

d）如果nSuffix满足上述条件(a)，但nPrefix大于buf持有的实际数据，则下一步可能存在信息泄漏问题。

(因为sqlite3_realloc调用libc的realloc，这不会将内存初始化为零)。

e）如果(nPrefix+nSuffix)*2大于0x1`0000
0000(仅保留低32位)，则在realloc之后，buf将被设置为非常小的缓冲区，这可能使缓冲区溢出。

攻击者可以将nPrefix设置为较大的值，而将nSuffix设置为较小的值，这将导致越界写。

f)如果我们选择利用a)或b)，将nSuffix(我们称其为“Y”)设置为Y=0x80000000-X(你可能不想将Y设置为80000000-X，你可以这么做，但如果这样做，则很可能会在memcpy期间崩溃)。

例如,

  * 我们有zCsr=0xa0000000，nPrefix=7ffff001来触发zCsr+nPrefix-1，结果是0x1 1FFF000，较高的0x1被截断，因此它实际上是0x1ffff000。

  * 我们将nSuffix设置为0xfff，因此nPrefix+nSuffix整数溢出，结果是0x0，0x0小于nalloc，因此我们不会进入realloc部分。(if( nPrefix+nSuffix>nAlloc ) {realloc…})

  * 因此，最后，将会有一个写大小为0xfff的对0x1ffff000的越界写入。

4、触发缓冲区相关漏洞的代码h)

memcpy(&zBuffer[nPrefix]，zCsr，nSuffix)；

这将复制数据，并且nPrefix、zCsr、nSuffix是可控制的。nPrefix，nSuffix的最大值为0x7fffffff。

5、信息泄漏i )

![](https://images.seebug.org/content/images/2020/01/2b0b08a5-32b1-4185-803a-bc950da78385.png-w331s)

我们可以使用SELECT来获取匹配的数据，以获取泄漏的数据。

(我们现在没有足够的时间来编写PoC，但我们认为这是可利用的。)

**6.3 CVE-2018-20506**

fts3扩展中的fts3SegReaderNext可能允许攻击者泄漏堆数据或导致堆缓冲区溢出。

有漏洞的函数

此代码位于fts3SegReaderNext中，此漏洞原理与6.2相同。

![](https://images.seebug.org/content/images/2020/01/d4f2c4fa-f30c-4dfe-a05a-a2f8b095a6af.png-w331s)

### **0x07 远程攻破Google Home**

本节将会介绍如何结合Google CAST协议安全风险与Magellan漏洞，对Google
Home发起攻击并最终实现远程代码执行。第一部分主要是编写与调试CVE-2018-20346的漏洞利用代码，这包含了寻找劫持控制流的函数指针，寻求触发函数指针的调用路径，堆内存布局及RCE。第二部分是通过CAST协议在局域网及互联网远程环境下推送payload到Google
Home中实现恶意代码执行。

**7.1可利用函数指针**

首先，需要找到在堆上使用的函数指针用于劫持控制流。在创建fts3表时，默认情况下会创建tokenizer其默认值为simple_tokenizer。具体结构如下图所示：

![](https://images.seebug.org/content/images/2020/01/69a9dfcf-1991-4910-a383-e0120d75d001.png-w331s)

simple_tokenizer是堆上分配的结构，其成员base指向sqlite3_tokenizer结构，sqlite3_tokenizer结构的成员pModule指向tokenizer_module，而tokenizer_module包含了许多回调函数，例如xCreate
/ xOpen。分析调用流程后，我们了解到在对fts3表进行插入操作时将触发xOpen回调函数，若将xOpen的地址修改为任意地址，则可以劫持PC。

**7.2 劫持PC**

在漏洞触发后的路径上，若要完成前述的PC劫持需要满足两个条件。第一，在堆溢出后能够操作fts3表；另外，还需要在内存释放前完成劫持，否则就会导致crash从而中断利用过程。通过分析memcpy到free代码路径，存在函数fts3TruncateSegment，该函数会执行一次SQL
update操作，正如下图蓝色标记的代码。既然能够执行SQL语句，那么就可以利用SQL Trigger在执行该update操作前执行fts3表的操作

![](https://images.seebug.org/content/images/2020/01/743c07f9-5229-4291-9085-1ccd6d09432e.png-w331s)

最终，我们通过Trigger在SQL update操作和free内存之前执行了fts3 表的插入操作，进而触发xOpen回调完成劫持PC。

**7.3 堆内存布局**

完成了前述两步后，接下来将会介绍进行内存布局的思路。具体思路如下图：

![](https://images.seebug.org/content/images/2020/01/57fe1290-9031-4676-8764-c2f19e3b6c69.png-w331s)

  1. 通过创建多个fts3表，即可在堆上创建多个simple_tokenizer结构；

  2. 选择适当的时机删除之前创建的fts3表，对应simple_tokenizer结构也会随之释放；

  3. 由于simple_tokenizer结构体在堆上会连续存储且分配与simple_tokenizer相同大小的内存将会重用已经释放的simple_tokenizer结构。因此，通过调整payload大小，可以将fts3表的simple_tokenizer结构覆盖掉；

  4. 最后，利用SQL Trigger执行fts3表的操作，触发被覆盖的回调函数来劫持PC。

**7.4绕过ASLR**

当具备劫持PC和控制寄存器的能力后，我们还需要信息泄露漏洞绕过ASLR。同样还是利用漏洞CVE-2018-20346，通过调节nDoclist和pNode->a，就能够泄露以下两类地址：

  1. 泄露cast_shell加载基址，根据该地址和偏移计算出需要的ROP gadgets；

  2. 泄露最后堆的基址，根据这个地址和偏移，较大概率能计算出堆喷地址。

**7.5 cast_shell渲染进程RCE**

cast_shell是一个很大的二进制程序，包含了很多可用的ROP
gadget。结合堆喷和ROP技术，便可以在cast_shell的renderer中远程执行代码，下图为ROP和堆喷内存状况：

![](https://images.seebug.org/content/images/2020/01/8f93fe50-e786-4447-bdd7-4091b63531fc.png-w331s)

一个堆喷单元里面包含伪造的sqlite3_tokenizer_module和ROP
gadgets。伪造的sqlite3_tokenizer_module结构体里的xCreate/xOpen地址将会被赋值为stack
pivot地址。堆喷的过程就是把多个这样的单元插入到数据库的表中。经过多次尝试，可以把其放置在和最后堆基址相对固定的偏移上；而溢出后覆盖的simple_tokenizer结构里包含了stack
pivot所需的寄存器数据。一切顺利的话，将能在cast_shell的renderer里实现远程代码执行，效果如下图所示:

![](https://images.seebug.org/content/images/2020/01/1ddd9fd0-1343-4948-ae73-a86def9ec2a9.png-w331s)

左图表示可以完成了PC劫持和控制的寄存器。右图则是ShellCode的运行结果（正常情况下，navigator.appName是只读数据，为”Netscape”，Shellcode代码执行后将其改成了”AAAAcape”。

**7.6 局域网内与远程攻击链**

![](https://images.seebug.org/content/images/2020/01/6f28251a-420b-40f1-ba82-af37b034bfa5.png-w331s)

**局域网攻击链**

局域网内，攻击者可以直接发送CAST协议完成攻击。

  1. 通过"Launch APPID=1"的指令，Google Home会根据APPID拉取应用市场上的Leak.html并加载，可利用该恶意网页用于泄露内存数据； 

  2. 接着，发送"Launch APPID=2"的指令，Google Home就会加载Exp.html，从而远程代码执行，整个过程不需要用户交互。 

**互联网远程攻击链**

  1. 攻击者诱导用户通过Chrome浏览器访问Sender Application的url，这时Chrome浏览器会提示用户选择设备，用户确认后将会开始攻击流程； 

  2. 参考Cast Hack的攻击思路，通过扫描网络上存在UPnP Forwarding的路由器，尝试发起远程攻击；

### **0x08 后记**

在向Google报告漏洞后，Google在2018年12月的Chrome安全补丁中修复了我们提交的所有漏洞。

![](https://images.seebug.org/content/images/2020/01/7ea879bb-32f8-4738-a2fe-21204f4b00cf.png-w331s)

本文是Tencent Blade Team物联网安全系列的第一篇，主要内容整理自团队在BlackHat USA
2019及DEFCON27的演讲，由于篇幅限制部分内容无法详细叙述，大家可以参考附录中的whitepaper，同时也欢迎大家同我们进行技术交流，联系方式参见Blade
Team官网： （<https://blade.tencent.com>）

参考：

  1. <https://drive.google.com/drive/folders/0B3j4zj2IQp7MZkplRzRvcERtaU0>
  2. <https://2018.zeronights.ru/wp-content/uploads/materials/19-Researching-Marvell-Avastar-Wi-Fi.pdf>
  3. <https://github.com/axoltl/HubCap>
  4. <https://developers.google.com/cast/docs/developers>
  5. <https://blade.tencent.com/magellan/>
  6. <https://chromereleases.googleblog.com/2018/12/stable-channel-update-for-desktop.html>
  7. <https://media.defcon.org/DEF%20CON%2027/DEF%20CON%2027%20presentations/DEFCON-27-Wenxiang-Qian-Yuxiang-Li-Huiyu-Wu-Breaking-Google-Home-Exploit-It-with-SQLite-Magellan.pdf>
  8. <http://i.blackhat.com/USA-19/Thursday/us-19-Qian-Exploring-The-New-World-Remote-Exploitation-Of-SQLite-And-Curl.pdf>
  9. <https://i.blackhat.com/USA-19/Thursday/us-19-Qian-Exploring-The-New-World-Remote-Exploitation-Of-SQLite-And-Curl-wp.pdf>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1111/>

