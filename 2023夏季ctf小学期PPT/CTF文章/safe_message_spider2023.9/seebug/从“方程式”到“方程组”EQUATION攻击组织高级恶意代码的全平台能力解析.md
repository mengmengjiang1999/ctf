来源：[安天实验室](http://www.antiy.com/response/EQUATIONS/EQUATIONS.html)

## 1 背景

安天从2015年2月起，陆续公布了两篇针对方程式攻击组织的分析报告，分析了其针对Windows平台的恶意代码组件构成、对硬盘的持久化能力和对加密算法的使用。本报告则将首次公布安天对方程式攻击组织针对Solaris平台和Linux平台的部分样本分析，我们也可以自豪的说，这是业内首次正式证实这些“恶灵”真实存在的公开分析。事实上，安天的相关工作完成于数年前。安天的分析工程师们从2012年起，已经关注到超级攻击组织，力图将其载荷能力覆盖一切可以达成入侵和持久化的场景，在这些场景中，各种服务器操作系统，如Linux、Solaris、FreeBSD等是其高度关心的目标。这些载荷不是寻常的脚本木马，而是
**组件化、具备Rootkit能力、具有超强加密抗分析能力、严格进行加密通讯的二进制组件**
。在安天工程师一直将类似超级攻击组织发起的攻击称为A2PT，并把恶意代码载荷的全平台覆盖能力作为A2PT组织的重要标志。

安天将长期跟踪分析高级威胁和高级恶意代码的经验转化为产品能力，为用户探海威胁检测系统协助用户在网络中捕获载荷投放与横向移动，利用智甲终端防御系统为传统Windows主机和国产操作系统提供全面的保护，协助用户使用追影安全分析平台进行多种平台的恶意代码分析。这些产品的部署也使安天能够在用户支持下获取更多的威胁检索。同时安天也积极关注开源情报和公开信息，关注相关组织的的有关信息与动向。

在去年年初卡巴斯基和安天先后对方程式组织使用的恶意代码进行分析曝光后，方程式组织又在一系列“爆料”事件中浮出水面。在2016年8月所外泄的方程式组织针对多种防火墙和网络设备的攻击代码中[1]，公众第一次把方程式组织和名为“ANT”的攻击装备体系联系起来，并以此看到其针对Cisco、Juniper、Fortinet等防火墙产品达成注入和持久化的能力。而在2016
年 10 月 31 日，The Hacker News 发布文章“Shadow Brokers reveals list of Servers Hacked
by the NSA”
[2]，文章披露了“影子经纪人”公开的更多文件，其中包括部分方程式组织入侵的外国服务器列表。相关文件声称，大部分被感染的服务器运行的是 Solaris,
Oracle-owned Unix等版本的操作系统，有些运行的是 FreeBSD 或 Linux
系统。而随着这些信息和安天的捕获分析工作相互印证，一个关于这个超级攻击组织的 **几乎无死角的、全平台化攻击能力** 已经日趋清晰。

我们的分析工作不断验证着这些信息，在过去数年，这种分析如此漫长、复杂和艰难，超出了我们之前对“震网”、“火焰”的分析和复现中所面临的挑战。这种高度复杂、隐蔽的全能高级恶意代码，无论是对受害者，还是分析者来说，都是一个巨大的挑战。特别是当其打击范围几乎覆盖所有体系结构与操作系统的时候，相对更擅长Windows、Linux和Android等主流操作系统平台下恶意代码分析的传统安全分析团队感受到了巨大的压力和挑战。如果用这个组织的名称“方程式”做一个关于分析难度的比喻的话，
**我们需要破解的已经并不只是一个“方程式”，而是更为复杂的多元多次的“方程组”** 。

## 2 方程式组织的多平台作业能力

方程式组织采用了工业水准的制式化攻击武器库，安天在此前报告中已经对其6件恶意代码组件“装备”进行了分析，他们分别是：
**EquationLaser、EquationDrug、DoubleFantasy、TripleFantasy、Fanny和GrayFish** ，其中
**EquationDrug、DoubleFantasy** 安天均已发现其他平台的样本。方程式武器库信息见下表：

![](https://images.seebug.org/content/images/2016/11/E122AAEA-76E6-4C10-8A72-FF8B9A16B5C8.png-w331s)

读者可以通过阅读下列报告，自己完成方程式攻击组织针对多平台操作系统的拼图：

![](https://images.seebug.org/content/images/2016/11/FFA8EEEE-7407-49AE-8469-E9BBCC0559E3.png-w331s)

注：安天在Solaris样本中分析出的User Agent具有Solaris标识，而卡巴斯基在“EQUATION GROUP: QUESTIONS AND
ANSWERS” [8]中披露出曾捕获到Mac OS X的User Agent的信息，由此来看，尽管安天和卡巴斯基等厂商目前都尚未捕获Mac OS
X的样本，但方程式组织针对MAC OS X的攻击载荷是真实存在的。

## 3 X86 Linux部分载荷分析

安天已经捕获分析了Linux下的DoubleFantasy组件。该组件是方程式组织在Linux平台上用于前期侦查、探测预期目标的攻击样本。由于是Linux平台下的样本，在具体功能实现的技术细节上与我们之前的曝光的Windows样本有所区别。

### 3.1 侦查、探测的前导模块——DoubleFantasy

#### 3.1.1文件标签

![](https://images.seebug.org/content/images/2016/11/AECEFFE7-E03B-43F7-A414-5F72E5566167.png-w331s)

#### 3.1.2运行流程

Trojan/Linux.DoubleFantasy
样本执行时分为有参数和无参数两种情况，当有参数‘-c’时候，仅仅是用于获取系统信息，可以视为场景侦查功能，其流程如下：

![](http://www.antiy.com/response/EQUATIONS/img/image005.png)

图 1 Trojan/Linux.DoubleFantasy–c参数流程

如果样本以无参数运行会具有网络通信行为，流程如下：

![](http://www.antiy.com/response/EQUATIONS/img/image006.png)

图 2 Trojan/Linux.DoubleFantasy无参数运行流程

#### 3.1.3 基本功能

遍历系统文件、清除/var/log/lastlog记录、获取系统账户密码信息。 连接Google判断网络连通状态。
连接远程服务器，并根据远程控制指令进行不同的操作。 样本中同样存在多处信息加密算法和网络通讯加密算法。
样本会利用一个链接文件启动自身，proc/%d/exe文件指向样本自身文件。 样本运行后会开启三个连续的PID线程。
随后样本收集被感染机器的信息包括系统目录、文件扩展名等信息。如下图：
![](http://www.antiy.com/response/EQUATIONS/img/image007.png)

图 3收集常规系统信息

恶意代码开始fork( )进程，并判断fork( )的子进程的PID号，判断是否执行成功，如果执行成功则主进程退出，无法调试，影响调试过程如下图所示：

![](http://www.antiy.com/response/EQUATIONS/img/image008.png)

图 4 子进程判断

分别解密各种字符串，获取用户信息，包括系统版本等。 获取用户登陆信息 getpwnam。 查看文件 /bin/fast /sbin/login
/usr/sbin/nologin 。 获取用户登陆密码getpwuid。 读取用户日志var/log /lastlog。

#### 3.1.4 函数、数据动态加载

此样本所调用的函数和数据都是动态加载调用，在分析中需要动态调试，经过分析我们把函数调用地址通过动态分析解密出来如下图：

![](http://www.antiy.com/response/EQUATIONS/img/image009.png)

图 5 函数调用地址

#### 3.1.5 字符串解密分析

样本内部采用了一种自定义的加密算法，用于加密内部要用到的字符串信息，该算法共被调用了115次，加密算法如下：

![](http://www.antiy.com/response/EQUATIONS/img/image010.png)

图 6 Linux样本字符串加密算法

3.1.6 网络通信加密
DoubleFantasy的Linux样本在网络通信时，硬编码在样本中的16位密钥与DoubleFantasy在Windows平台样本中加密注册表相关数据的16位密钥相同：

    
    
    66 39 71 3c 0f 85 99 81 20 19 35 43 fe 9a 84 11 

经计算后生成的子密钥为：

    
    
    E9 BE CD E0 A8 9F 4D DB C3 42 AC 2B 24 77 AB CB 5A C1 52 F8 5B 3E F0 78 CB 01 0A 69 29 8F 85 8C 03 9C 7C EF 5E 36 0E 8B C0 40 76 28 9C 9C F2 24 81 9D 02 72 4F 6A BB B5 5B 42 73 14 88 F2 73 75 8B F9 37 98 3B 9F 64 2B A3 C4 FF C7 8A 40 67 C1 25 9F 65 54 45 36 48 FF E2 86 05 1A F4 94 AC 2B 08 D5 E5 83 BE 2C AD EE D0 A6 98 CB 8D 35 ED EE C4 F0 8C F2 CD BA 87 03 54 27 3D 13 A7 9B 6A 05 C7 02 30 21 05 67 58 3B E6 A1 44 0A 37 16 3C 86 E9 BC 8B 20 1A 98 7E 28 E6 7F F7 CA F7 9E 38 31 7F F0 2F 93 11 2B 28 F0 FF 11 B7 FC 1C 63 86 CB

Linux样本的自定义算法与Windows下的样本相同，而使用的加密密钥只有一个（因为Linux系统没有注册表，所以就没有注册表加密这功能），该密钥与Windows平台下注册表加密数据的Key相同（Windows平台有两组key，一组注册表key一组网络通讯key），从下图中可以看出两个平台的二级密钥变化算法是相同的（具体算法可以参照Windows加密算法分析部分）。

![](http://www.antiy.com/response/EQUATIONS/img/image011.png)

图 7 二级密钥变化算法

### 3.1.7 网络控制指令

Linux样本的指令分支部分与安天此前所发布的报告中分析的Windows部分基本相同，Linux样本共有9个分支指令，功能也大致相同，指令代码分别为：0x4A、0x4B、0x60、0x70、0x75、0x76、0x78、0x79、0x80。

![](http://www.antiy.com/response/EQUATIONS/img/image012.png)

图 8 Linux样本的指令分支代码

Linux系统下的样本在指令上与Windows样本功能一致，仅在获取系统信息上有细微差别，Linux样本获取信息格式如图：

![](http://www.antiy.com/response/EQUATIONS/img/image013.png)

图 9 Linux样本获取信息格式

获取信息格式说明：

![](https://images.seebug.org/content/images/2016/11/2440E49D-A34E-4D49-9C87-1186AA539BA4.png-w331s)

## 4 SPARC架构Solaris场景能力

方程式组织可能制造了第一个SPARC架构[9]下的具有Rootkit属性的恶意代码，并为DoubleFantasy的Solaris[10]版本来提供掩护。

### 4.1 Solaris系统及SPARC架构

Solaris是Sun
Microsystems研发的计算机操作系统，采用SPARC架构或X86架构，主要用于工作站、服务器上的操作系统。Solaris平台下的恶意代码比较罕见，从安天统计来看，即使加上之前的SUN
OS时期，二进制编译形态的恶意代码变种数也不超过60种，而且几乎都是基于X86平台的。 SPARC全称为“可扩充处理器架构”（Scalable
Processor ARChitecture），是RISC微处理器架构之一，其指令集和X86有显著区别，并且有自己独有的窗口、延迟槽、过程调用特点。
SPARC架构的计算机一般用于工业、航天相关领域，其在类似IDC和一般IT场景的使用极为罕见。

### 4.2 Rootkit隐藏模块

该模块是SPACR架构的Solaris平台下的一个Rootkit程序，同其他Rootkit程序一样，它主要负责隐藏主功能样本文件、以及相关衍生的文件和其自身，包括进程、文件、和服务信息。它首先在目标机器上运行，侦查目标机器的系统环境、配置信息、网络状态，并隐藏指定的文件和进程。

#### 4.2.1文件标签

![](https://images.seebug.org/content/images/2016/11/A70129E5-221A-4A44-A84C-51AB7BDDDA08.png-w331s)

#### 4.2.2 样本主函数

样本共有249个函数，如图所示为样本主函数流程，部分函数也相对复杂，且样本内部同样存在多种加密数据。

![](https://images.seebug.org/content/images/2016/11/640.png-w331s)

图 10 样本主函数

#### 4.2.3衍生文件名及路径

样本运行后根据内部配置的两组字符串组合生成文件名，作为自身的新文件名，并将自身复制到/sbin/目录下。
![](https://images.seebug.org/content/images/2016/11/79CC830D-E8F5-4651-BB4F-2B3B74917686.png-w331s)

#### 4.2.4 启动脚本

样本使用服务的方式实现开机启动，在etc/rc.d/目录下创建脚本（S85s%），此脚本会作为开机要执行的服务以start参数运行。

![](http://www.antiy.com/response/EQUATIONS/img/image015.png)

图 11 服务脚本

S85s%文件的内容是加密的，样本运行时调用自身函数解密，并修改其中文件名的变量，再将其写入到/etc/rc.d/目录（下图%E处会修改为样本自身路径）。

![](http://www.antiy.com/response/EQUATIONS/img/image016.png)

图 12 解密后脚本内容

#### 4.2.5 隐藏目录、文件

样本会根据目标机器的HOSTID生成MD5，然后再将MD5进行一个类base64的算法计算，最后取前6位，将.tmp与这6位字符拼接成文件夹名称，然后创建该文件夹。

![](http://www.antiy.com/response/EQUATIONS/img/image017.png)

图 13 样本创建的文件夹名 样本还会根据运行参数，将其他文件复制到此文件夹下执行，并负责隐藏此文件夹下的所有文件。

#### 4.2.6 版本判断

样本通过uname函数确定系统不是sun4m、sun4d版本，通过读取/dev/ksyms文件判断系统架构：i386、ia64、sparc、sparcv9，确定是SPARC架构，确定release版本必须是5.1。

![](http://www.antiy.com/response/EQUATIONS/img/image018.png)

图 14 版本判定

#### 4.2.7 加密配置数据

样本内部存在多处加密算法，其中一个调用多次，我们分析并解密出其数据。

![](http://www.antiy.com/response/EQUATIONS/img/image019.png)

图 15 加密算法 解密的加密数据：

![](https://images.seebug.org/content/images/2016/11/640-3.png-w331s)

![](https://images.seebug.org/content/images/2016/11/640-4.png-w331s)

#### 4.2.8 解密执行其他代码/样本

样本在文件尾部添加加密数据，执行后通过末尾数据确定加密数据大小，通过定义的格式进行解析和读取，解密数据后猜测会加载执行。

![](http://www.antiy.com/response/EQUATIONS/img/image020.png)

### 4.3 DoubleFantasy的Sparc架构模块

该样本与Windows、Linux平台样本的功能基本相同，主要区别在于CPU架构、汇编指令、配置信息存储位置、获取系统信息等。

#### 4.3.1 文件标签

![](https://images.seebug.org/content/images/2016/11/28ECD6BE-10E5-48E3-A5D4-4D2499C72CF1.png-w331s)

#### 4.3.2 基本功能

初始化字符串、动态数组，解密内部配置信息。 连接Google或Yahoo网址判断网络连通状态。
连接远程URL地址。样本会收集主机的信息回传至远程地址，并等待远程主机发送指令。 具有读取系统账户密码文件的功能，可以窃取用户及密码信息。
样本内部实现了以守护进程模式运行，可以达到自我保护防止被结束的功能。 该样本采用多种加密算法加密字符串信息。
获取系统大量信息并回传到服务器（如计算机名称、IP地址、进程信息、账户信息等，详细内容可见本章节后面详细分析）。
网络指令部分，具有7条网络指令，功能上与Windows版本相同，可对计算机进行相对应的指令操作，对应指令详细功能见本章后面详细分析。

#### 4.3.3 配置信息加密

由于Solaris系统没有Windows的注册表，因此该样本的配置数据会直接解密后使用，其中一个解密算法如下，该解密函数共调用63次。

![](http://www.antiy.com/response/EQUATIONS/img/image021.png)

图 16 字符串解密 解密出字符串信息见下表：

![](https://images.seebug.org/content/images/2016/11/640-1.png-w331s)

![](https://images.seebug.org/content/images/2016/11/640-2.png-w331s)
样本使用的另一个加密字符串的算法，用于加密样本运行时需要使用的配置信息，解密算法如下：

![](http://www.antiy.com/response/EQUATIONS/img/image022.png)

图 17 另一解密算法 解密内容见下表：
![](https://images.seebug.org/content/images/2016/11/27D92EA3-FD35-4AEE-9B01-4274A7D1EB26.png-w331s)

#### 4.3.4 网络通信加密

Solaris样本的自定义算法与Windows下的样本相同，而使用的加密密钥只有一个（因为Solaris系统没有注册表，所以就没有注册表加密的功能），该密钥与Windows平台下注册表加密数据的Key相同，两个平台的自定义加密算法是相同的（具体算法可以参考3.1.6加密算法分析部分）。

通过安天CERT分析，得到原始16位密钥为： 66 39 71 3c 0f 85 99 81 20 19 35 43 fe 9a 84 11
长度为16字节，与Windows的原始16位密钥长度相同。 由于Solaris和Windows样本生成网络通信子密钥的算法相同，那么可生成子密钥：

    
    
    E9 BE CD E0 A8 9F 4D DB C3 42 AC 2B 24 77 AB CB 5A C1 52 F8 5B 3E F0 78 CB 01 0A 69 29 8F 85 8C 03 9C 7C EF 5E 36 0E 8B C0 40 76 28 9C F2 24 81 9D 02 72 4F 6A BB B5 5B 42 73 14 88 F2 73 75 8B F9 37 98 3B 9F 64 2B A3 C4 FF C7 8A 40 67 C1 25 9F 65 54 45 36 48 FF E2 86 05 1A F4 94 AC 2B 08 D5 E5 83 BE 2C AD EE D0 A6 98 CB 8D 35 ED EE C4 F0 8C F2 CD BA 87 03 54 27 3D 13 A7 9B 6A 05 C7 02 30 21 05 67 58 3B E6 A1 44 0A 37 16 3C 86 E9 BC 8B 20 1A 98 7E 28 E6 7F F7 CA F7 9E 38 31 7F F0 2F 93 11 2B 28 F0 FF 11 B7 FC 1C 63 86 CB

此子密钥才是用于加解密发送、接收数据的。

#### 4.3.5 网络控制指令

在对Solaris样本的分析中我们发现它的功能要比Windows样本的指令少一些，Solaris平台下只有7个指令，功能上与Windows大致相同。下面为两个平台下IDA中的对比图，多图中可以看出Solaris平台下的样本指令比Windows平台上少很多结构图也很简单。

![](http://www.antiy.com/response/EQUATIONS/img/image023.png)

图 18 Windows平台与Solaris平台下网络指令结构对比

Solaris样本的指令功能并未在上图中实现，起初我们以为Solaris样本的指令功能还未完成，不过在进行进一步的分析后我们发现，Solaris样本采用一种特殊的动态计算方式来跳转到不同的指令分支代码，下图中红色部分即为动态计算后跳转的指令分支。

![](http://www.antiy.com/response/EQUATIONS/img/image024.png)

图 19 Solaris指令分支函数

Solaris样本各个指令功能简要描述如下，大体功能与Windows指令相同：

![](https://images.seebug.org/content/images/2016/11/3C7572B8-E063-4CDD-A079-F012B7AB964E.png-w331s)

其中下载执行部分样本与Windows一样，使用相同的指令标记，也是通过三步（创建、写入、执行）来完成下载执行的功能，只是在代码结构上有所不同，Solaris把三条指令整合到一个函数中。
执行文件时，先给文件提权，然后使用execle函数带有参数执行文件：

参数1：文件B路径

参数2：文件名B或"sendmail"（猜测与mail有关）

参数3：0

参数4：PATH=%PATH%（环境变量）

例如：execle("/usr/bin/sample","sample", NULL, %envp%);

![](http://www.antiy.com/response/EQUATIONS/img/image025.png)

图 20执行文件参数

Solaris样本指令功能、数据包格式与Windows样本相同，指令的详细功能、数据包格式说明可见 Windows平台样本的指令分析。
Solaris样本下收集的系统信息与Windows略有不同，具体如下：

![](https://images.seebug.org/content/images/2016/11/111.png-w331s)

## 5 总结

### 5.1 以真实威胁驱动我国信息防御能力的的改进

安天希望用自己的工作告诉中国用户，那些关于超级攻击组织全平台覆盖功能能力的种种爆料，并非传说，而且是一种真实的威胁，是一种既定的事实。

在我国安全防御的实践中，有一种先入为主的观点，即认为由于各种规定和约束，暴露在互联网上的节点，乃至能够访问互联网的内网中，并不存放高价值的信息。“一切有价值的信息都存在与隔离网内”——这是一个美好的愿景想象，但并非在这个信息大量产生、高速流动时代的真实情况。同时在大数据时代，高价值信息的定义和范围也在不断变化着。更多的信息资产已经不可避免分布在公共网络体系中。而对这些资产的窥视和攻击也持续在增加着。而超级攻击组织则是类似攻击的始作俑者和长期实践者。

针对DNS服务器的入侵，可以辅助对其他网络目标实现恶意代码注入和信息劫持；针对邮件服务器的植入可以将用户所有的邮件通联一网打尽，针对运营商骨干节点的持久化，可以用来获取全方位的信息，包括收获类似CamberDada[11]计划中说的那种“轻而易举的胜利”

注：Camberdada计划是斯诺登曝光的一份监听行动计划，相关机构通过在运营商的持久化节点，监听用户发放给杀毒厂商的邮件，以发现自己的攻击是否暴露，并实现对其他方投放的样本捕获和再利用。

而“物理隔离”的安全神话也已经到了应该破灭的时候，习近平总书记在4.19讲话中已经提醒国内用户和网络安全工作者：“‘物理隔离’防线可被跨网入侵，电力调配指令可被恶意篡改，金融交易信息可被窃取，这些都是重大风险隐患。”

而中国庞大又脆弱的信息化肌体则又面对着武装到牙齿的对手。攻击载荷的代码工程规模、作业链条的精密设计、全方位无死角的平台覆盖都已显示了方程式攻击组织这样的超级攻击组织空前的攻击能力。而根据相关曝光的信息，其所发动的面对大量的关键目标为期数年的攻击，也表明了这一组织极为坚定的攻击决心。安天在此前的研究中曾将类似的攻击能力组织称为A2PT，并从恶意代码载荷视角给出了A2PT的若干评价标准。这些标准与方程式组织的行为与能力高度吻合。

![](https://images.seebug.org/content/images/2016/11/5C9ACC9E-3A86-44AE-ADC3-0D27D7661C7E.png-w331s)

就像我们此前所概括的那样，相关超级攻击组织拥有“成建制的网络攻击团队、庞大的支撑工程体系与制式化的攻击装备库、强大的漏洞采集和分析挖掘能力和关联资源储备以及系统化的作业规程和手册，具有装备体系覆盖全场景、漏洞利用工具和恶意代码载荷覆盖全平台、持久化能力覆盖全环节的特点。面对这种体系化、即具备工业级水准由具有高度定向性的攻击，永动机注定停摆；银弹注定哑火。想要达成防御效果，实现追踪溯源，唯有以清晰的战略、充分的成本投入，以体系化的防守对决体系化[12]的攻击，通过长期艰苦、扎实的工作和能力建设，才能逐渐取得主动。

### 5.2 我们的努力和对能力型厂商深入协作的期待

从2010年开始，安天先后对“震网”、“毒曲”、“火焰”、“APT-TOCS(海莲花)”、“白象”、“乌克兰停电”、“方程式”等高级攻击行动或攻击组织进行了深入的分析，累计发布了数百页的分析报告。毫无疑问，高级威胁检测产品的能力，是依托扎实有效的分析过程来不断改进的。安天发布了面向高级威胁检测和态势感知的产品体系：安天的探海威胁检测系统改善了用户流量侧的威胁检测的深度和能力，安天的智甲终端防御系统为用户提供了包括“白名单+安全基线”在内的多种防御策略，安天的追影威胁分析平台则为用户提供了通过动静态手段深度分析威胁载荷的能力，安天也在多个行业和部门的态势感知和通报预警平台的建设中扮演了关键角色，提供整体的设计支持、开发集成以及供应关键的检测分析能力。

安天将下一代威胁检测引擎、高定制化深度分析、面向资产和威胁的交互可视分析和知识与情报支撑，作为自身达成有效的、可落地的用户价值的产品基因。

但安天也客观的的看到，面对超级攻击组织的强大能力、坚定意志和难以想象的攻击成本，任何厂商的单打独斗，都难以有效的达成使命，因此安天一直与同业一起，倡导能力型安全厂商间的积极协作和能力互认。在此前针对来自南亚次大陆的网络攻击分析应对中，虽然安天将事件命名为“白象”，360企业安全命名为“摩诃草”，但双方在报告形成中进行了有效的信息互通，以及对对方分析成果的引用互认，这是一个良好的开端，我们相信类似的能力型安全厂商的协作，将会越来越多。

### 5.3 期待一个更安全的网络世界

当前，超级攻击组织的全环节覆盖能力，已经引发了全球用户‘一切均不可信’的安全焦虑。”去年部分国内媒体对方程式攻击的报道中，将攻击者针对高价值目标节点硬盘固件实现攻击持久化的植入，解读为当前主流的硬盘都带有后门，这固然是一种误解，但也不能不说当一个超级攻击组织的能力强大到了只能猜测和想象的程度时，就不可能不引发恐慌，从而导致对超级大国产生“滥用供应链和信息流优势”的严重质疑。

而近期的方程式攻击代码泄露事件以及此前“ANT”装备体系的曝光，则又使我们看到了相关的Exploit储备和攻击思路流入到网络犯罪组织、甚至恐怖主义组织的可能性。鉴于网络攻击技术存在极低的复制成本的特点，当前已经存在严峻的网络军备扩散风险。因此，超级大国能否合理控制自身网络军备发展的速度和规模，并对因自身未有效履行责任而使网络领域发生可能的军备扩散，进行有效地的干预和控制，是我们能达成一个更安全的网络世界的关键因素。

我们期待一个更安全的网络世界，我们为之努力！

### 附录一：参考资料

Equation Group Cyber Weapons Auction - Invitation
https://github.com/theshadowbrokers/EQGRP-AUCTION

Shadow Brokers reveals list of Servers Hacked by the NSA
http://thehackernews.com/2016/10/nsa-shadow-brokers-hacking.html

安天：修改硬盘固件的木马 探索方程式（EQUATION）组织的攻击组件
http://www.antiy.com/response/EQUATION_ANTIY_REPORT.html

安天：方程式（EQUATION）部分组件中的加密技巧分析
http://www.antiy.com/response/Equation_part_of_the_component_analysis_of_cryptographic_techniques.html

Kaspersky：Equation: The Death Star of Malware Galaxy
http://securelist.com/blog/research/68750/equation-the-death-star-of-malware-galaxy/

Kaspersky：A Fanny Equation: "I am your father, Stuxnet"
http://securelist.com/blog/research/68787/a-fanny-equation-i-am-your-father-stuxnet/

Kaspersky：Equation Group: from Houston with love
http://securelist.com/blog/research/68877/equation-group-from-houston-with-love/

Kaspersky：Equation_group_questions_and_answers
https://securelist.com/files/2015/02/Equation_group_questions_and_answers.pdf

SPARC架构 https://en.wikipedia.org/wiki/SPARC

Solaris系统 https://en.wikipedia.org/wiki/Solaris_(operating_system)

An Easy Win：Using SIGINT to Learn about New Viruses 黄晟：关于网络纵深防御的思考
http://www.antiy.com/wtc/2015/02_Joe.pdf

### 附录二：关于安天

安天从反病毒引擎研发团队起步，目前已发展成为以安天实验室为总部，以企业安全公司、移动安全公司为两翼的集团化安全企业。安天始终坚持以安全保障用户价值为企业信仰，崇尚自主研发创新，在安全检测引擎、移动安全、网络协议分析还原、动态分析、终端防护、虚拟化安全等方面形成了全能力链布局。安天的监控预警能力覆盖全国、产品与服务辐射多个国家。安天将大数据分析、安全可视化等方面的技术与产品体系有效结合，以海量样本自动化分析平台延展工程师团队作业能力、缩短产品响应周期。结合多年积累的海量安全威胁知识库，综合应用大数据分析、安全可视化等方面经验，推出了应对高级持续性威胁（APT）和面向大规模网络与关键基础设施的态势感知与监控预警解决方案。
全球超过三十家以上的著名安全厂商、IT厂商选择安天作为检测能力合作伙伴，安天的反病毒引擎得以为全球近十万台网络设备和网络安全设备、近两亿部手机提供安全防护。安天移动检测引擎是全球首个获得AV-TEST年度奖项的中国产品。安天技术实力得到行业管理机构、客户和伙伴的认可，安天已连续四届蝉联国家级安全应急支撑单位资质，亦是中国国家信息安全漏洞库六家首批一级支撑单位之一。安天是中国应急响应体系中重要的企业节点，在红色代码、口令蠕虫、震网、破壳、沙虫、方程式等重大安全事件中，安天提供了先发预警、深度分析或系统的解决方案。

安天实验室更多信息请访问：

http://www.antiy.com （中文） http://www.antiy.net （英文）

安天企业安全公司更多信息请访问：

http://www.antiy.cn

安天移动安全公司（AVL TEAM）更多信息请访问：

http://www.avlsec.com

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/100/>

