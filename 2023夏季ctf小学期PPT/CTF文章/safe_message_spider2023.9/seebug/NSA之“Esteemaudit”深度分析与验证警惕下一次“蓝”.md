作者: **启明星辰ADLab**

### 一、背景

2017年5月12日晚间时候，一款名为“WanaCry”的勒索蠕虫病毒开始肆虐全球，波及上百个国家和成千上万个组织机构，影响深远，关于该蠕虫的详情请见启明星辰ADLab的分析报告《“WanaCry”事件分析与启示：警惕下一个“永恒之蓝”》。该款蠕虫基于“Shadow
Brokers”（影子经纪人）近期泄露的NSA旗下的黑客团队 “Equation
Group”（方程式组织）的漏洞利用工具之一“EternalBlue”（永恒之蓝），被“幸运”的选为蠕虫载体的原因可能是其打击范围涵盖了windows
xp到windows
2012（目前来看，是此次泄露的工具中覆盖最广的）。在上面提及的报告后半部分，我们提到勒索是目的，漏洞是先决条件，下一个能承载该目的的并非只有永恒之蓝。而这次我们的主角便是“Esteemaudit”。相较EternalBlue，Esteemaudit影响范围只包括windows
2003和windows
xp，但是一方面这两个系统目前的用户量仍不在少数，另一方面因为微软早已对2003和xp停止支持（除了5月13日针对此次永恒之蓝的紧急补丁），也就是说该工具利用的漏洞还是个0
day。

本文首先针对该0
day的细节做深入的分析，另外对于安全研究人员来说该批泄露工具中部分利用在使用上以及测试环境搭建上的问题造成了很多触发漏洞不成功的情况，针对Esteemaudit尤其如此，因此我们加入了该部分的详细说明并给出对比测试结论，排除研究该漏洞带来的干扰。

后续，我们会放出该漏洞的检测工具。

### 二、Esteemaudit涉及0day漏洞的分析

##### （1）漏洞描述

Windows
2000以后的版本都支持SmartCard认证机制，SmartCard中包含一个芯片存储用户登录信息，包括私钥和公钥，登录本地计算机时，需要将SmartCard插入本地计算机，并向WINLOGON输入PIN码；登录远程计算机时，在本地计算机插入Smartcard，输入PIN码，远程计算机Winlogon将会对PIN码进行验证，如下图所示。
![](https://images.seebug.org/content/images/2017/05/----_20170519104344.png-w331s)
基于SmartCard认证的RDP协议

其中，gpkcsp.dll模块中的MyCPAcquireContext函数存在漏洞，该模块由winlogon.exe调用。MyCPAcquireContext函数的功能是创建Prov
Context，通过接收SmartCard数据，对Prov Context结构体赋值。如果构造超长的SmartCard数据，在对Prov
Context进行赋值时可能覆盖其他字段，产生溢出。

##### （2）Smart Card协议

根据智能卡协议标准smartcard_standard_ISO7816，发送命令请求的数据包格式定义如下：
![](https://images.seebug.org/content/images/2017/05/----_20170519104702.png-w331s)
![](https://images.seebug.org/content/images/2017/05/----_20170519104719.png-w331s)
command APDU structure

其中，部分字段的意义如下：

  * INS：指令码，取值范围如下表： ![](https://images.seebug.org/content/images/2017/05/1-2.png-w331s)

  * Lc：表示数据段的长度。

  * Le：表示期望接收命令应答的最大长度。

##### （3）利用工具分析

首先，Esteemaudit利用代码会初始化一些从xml文件和脚本输入中获得的配置信息。
![](https://images.seebug.org/content/images/2017/05/2-1.png-w331s)
![](https://images.seebug.org/content/images/2017/05/3-2.png-w331s)

在初始化信息之后，exploit开始构造漏洞利用数据包。
![](https://images.seebug.org/content/images/2017/05/3-3.png-w331s)

首先构造第一段数据(buffer1)，内容随机，长度为0xb2，并将GlobalBufAddr+4（0x080190dc）的地址赋值给buffer偏移0x8d的位置，将0x9000写入buffer偏移0x91的位置。其中这个GlobalBufAddr来自xml配置文件，是目标机上存在漏洞的模块gpkcsp.dll中一个全局变量的地址，该地址用来存储客户端中读取的data。由于被攻击目标（xp和2003）中不存在ASLR，所以xml可以根据不同的目标机版本硬编码这个地址。

这里漏洞利用代码并不是完美无缺，如果想要成功触发漏洞，这段数据中的第五个字节不能为0x30，否则RDP程序将会进入另一个分支，而作者是通过随机方式来填充第五个字节，也就是说该利用程序可能会有1/256的可能会失败。
![](https://images.seebug.org/content/images/2017/05/4-2.png-w331s)

第二段数据(buffer2)主要是从一个Exp参数结构体中取出从xml文件中获取的rop链地址。
![](https://images.seebug.org/content/images/2017/05/5-2.png-w331s)

第三段数据的内容是shellcode，其内容被固定的放在Esteemaudit的数据段中。
![](https://images.seebug.org/content/images/2017/05/6-2.png-w331s)
![](https://images.seebug.org/content/images/2017/05/7-2.png-w331s)

之后，Esteemaudit程序会模拟SmartCard和被攻击端进行通讯，通讯的过程中将构造的exploit数据通过数据包发送到被攻击端，和漏洞相关的部分通信代码逻辑如下：
![](https://images.seebug.org/content/images/2017/05/8-2.png-w331s)

##### （4）漏洞原理分析

被攻击端漏洞发生在gpkcsp.dll的MyCPAcquireContext函数中，要想明确漏洞触发的原因先要理解和漏洞有关的两个buffer，第一个buffer是存在于gpkcsp.dll中的全局变量数组，我们把其命名为_pbRecvBuffer（地址0x080190d8）；第二个buffer是程序分配的用于存放CSP
context的结构体,我们称之为_TAG_Prov_Context（大小为0xB8），其数据结构如下所示。在这该数据结构中比较重要的位置有两个（红色标注的位置），一个是位于偏移0x18处的char数组keyset_name，通过逆向判断其长度不能超过128字节；另一个位于偏移0xa0处的HCRYPTKEY，这个位置稍后会被覆盖并导致程序流程被劫持。

    
    
    typedef struct _TAG_Prov_Context
    {
        HProvider _0000;//+0000
        SCARDHANDLE hCard;//+0004
        DWORD dwCspFlags;//+0008
        int _000C;//+000C;//index?
        int _0010;
        int _0014;
        char keyset_name[128];//+0x18//"Gemplus GemSAFE Card CSP Default Container"
        char _0098[4];//
        HCRYPTKEY _009C;//+9C
        HCRYPTKEY _00A0;//+A0//g_buffer+4;//destrokey(_0xA0);
        int _00A4;
        int _00A8;
        int _00AC;
        int _00B0;
        int _00B4;
    }TAG_Prov_Context;//sizeof=0xB8

MyCPAcquireContext在一开始的时候会对HCRYPTKEY置0。
![](https://images.seebug.org/content/images/2017/05/9-1.png-w331s)

接着，程序读取Esteemaudit发送来的buffer1然后将buffer1的数据拷贝到全局变量_pbRecvBuffer中。
![](https://images.seebug.org/content/images/2017/05/10-1.png-w331s)

上图中红色的数据是这个全局变量的_pbRecvBuffer
地址+4，蓝色的数据是0x9000，其他数据则是随机生成（之前我们提到过）。随后我们会看到如下的代码，代码首先从_pbRecvBuffer+4的位置（之前提到的第5个字节）读取数据和0x30h比较，如果相等的话就跳转到800e2a4处执行指令（会跳过存在漏洞的代码分支）。如果不相等则向_TAG_Prov_Context+0x18位置也就是keyset_name拷贝数据，被拷贝的数据是从_pbRecvBuffer的第六个字节开始，长度是_pbRecvBuffer的长度0xb2-7（十进制171）。
![](https://images.seebug.org/content/images/2017/05/11-1.png-w331s)

由于拷贝的时候并没有检查长度的大小是否大于keyset_name数组大小（171>128），从而导致了溢出的产生。
![](https://images.seebug.org/content/images/2017/05/12-1.png-w331s)

此时，位于_pbRecvBuffer
+0x8d位置的0x080190dc（被复制的第0x88字节）正好能够覆盖_TAG_Prov_Context指针偏移0xA0的位置处的HCRYPTKEY指针（0x8d-5+0x18=0xa）。

接着Esteemaudit发送buffer2，也就是rop的数据，这段数据同样被保存在_pbRecvBuffer中，图中的红框是我们构造的rop链的第一个代码片段地址（pop
ret0c）。 ![](https://images.seebug.org/content/images/2017/05/13-1.png-w331s)

之后，MyCPAcquireContext会调用ReleaseProvider。
![](https://images.seebug.org/content/images/2017/05/14-1.png-w331s)

在ReleaseProvider中会取出TAG_Prov_Context中偏移a0位置的hkey并调用ADVAPI32!CryptDestroyKey，此时hkey已经被覆盖成了0x080190dc。
![](https://images.seebug.org/content/images/2017/05/15-1.png-w331s)

在CryptDestroyKey函数会取出hkey（也就是该函数的参数），并执行命令call dword ptr [esi+8]。
![](https://images.seebug.org/content/images/2017/05/16-1.png-w331s)

这个esi+ 8正好是rop链的第一个代码片段的地址。

### 三、Esteemaudit的利用验证

Esteemaudit利用工具针对windows 2003和windows
xp，利用成功需要被攻击机开启域和远程桌面（默认3389端口）。域(Domain)是Windows网络中独立运行的单位，基于域可进行用户身份统一认证和安全边界集中管理等。

#### （1）环境搭建(以windows 2003为例)

##### 1.域的安装和设置

###### 1.1 DC的安装

要建立和管理域需要域控制器（DC），DC上存储着域中的信息资源如名称、位置和特性描述等。通过在一台服务器上安装活动目录（AD）来实现DC，首先要给DC设置一个静态IP，然后在windows
2003的“运行”中输入dcpromo，打开Active Directory安装向导。创建一个新域，填写DNS域名和NetBIOS域名，如下所示。
![](https://images.seebug.org/content/images/2017/05/17-1.png-w331s)
![](https://images.seebug.org/content/images/2017/05/18-1.png-w331s)
![](https://images.seebug.org/content/images/2017/05/19-1.png-w331s)
![](https://images.seebug.org/content/images/2017/05/20.png-w331s)

之后，一路“下一步”直到“DNS注册诊断”，如下图设置
![](https://images.seebug.org/content/images/2017/05/21.png-w331s)
![](https://images.seebug.org/content/images/2017/05/22.png-w331s)

到此DC成功建立，重启系统

###### 1.2 创建域用户

打开 “开始->管理工具->Active Directory用户和计算机”在创建的域下新建一个用户“adlab-test”如下图。
![](https://images.seebug.org/content/images/2017/05/23.png-w331s)
![](https://images.seebug.org/content/images/2017/05/24.png-w331s)
![](https://images.seebug.org/content/images/2017/05/25.png-w331s)

###### 2.域主机成员的设置

在要加入该域的主机中先开启远程桌面，然后打开“我的电脑->属性¬->计算机名->更改”后在域中填入刚才创建的域名，确定后输入DC的管理员账号密码，在加入域前先设置自己的IP和DNS，把DNS指向DC。
![](https://images.seebug.org/content/images/2017/05/26.png-w331s)
![](https://images.seebug.org/content/images/2017/05/27.png-w331s)

加入域成功后有如下提示：
![](https://images.seebug.org/content/images/2017/05/28.png-w331s)

上述对应测试环境网络拓扑如下：
![](https://images.seebug.org/content/images/2017/05/29.png-w331s)

##### （2）Esteemaudit利用

###### 1.攻击端(以win 10为例)

受限于fuzzbunch，攻击端需安装python2.6和pywin32-py2.6，
在`“…\shadowbroker\windows\”`下执行“fb.py”进行利用框架(Fuzzbanch)初始化设置，如下：
![](https://images.seebug.org/content/images/2017/05/30.png-w331s)

  1. 被攻击机器ip
  2. 本机ip
  3. 日志存储路径

初始设置后使用命令“use
Esteemaudit”对插件进行设置，由于初始设置了目标和监听ip所以基本使用默认设置就可以了。需要注意的是当设置到“Listen IP
[127.0.0.1]：”时这里需要填写的是被攻击机器的IP地址。
![](https://images.seebug.org/content/images/2017/05/31.png-w331s)

在“Press Any Key To Continue
:”提示后，会对被攻击机器做一次扫描，得到系统版本、平台等信息（如下图所示）。需要注意的是当测试不同的系统版本、平台时需要重新运行“fb.py”扫描被攻击机器，或者使用reset命令手动更新被攻击机器信息。
![](https://images.seebug.org/content/images/2017/05/32.png-w331s)

然后，进行再次的确认或设置，如果想修改被攻击机器的相关信息（payload的行为方式、目标机指令构架、目标机系统版本等），可以依据工具提示输入选项号进行修改，如下所示:
![](https://images.seebug.org/content/images/2017/05/33.png-w331s)
![](https://images.seebug.org/content/images/2017/05/34.png-w331s)

最后，需要（手动）设置回连端口和（手动设置或使用默认）NSA工具库文件的绝对路径。例如：“D:\shadowbroker\windows\storage\rudo_x86.dll”，如下图所示其中rudo_x86.dll、capa_x86.dll、lipa_x86.dll分别用作远程注入、回连、监听。
![](https://images.seebug.org/content/images/2017/05/35.png-w331s)

再次确认攻击与被攻击双方的IP和端口（其中Destination IP [0.0.0.0] 项使用默认值不需要手动设置）。
![](https://images.seebug.org/content/images/2017/05/36.png-w331s)

最终需确认配置信息 ![](https://images.seebug.org/content/images/2017/05/37.png-w331s)

若攻击成功，会显示如下信息。
![](https://images.seebug.org/content/images/2017/05/38.png-w331s)

攻击成功后被攻击机器会创建新进程回连之前设置的攻击机器端口（5678），如下所示（实际测试环境请关闭防火墙）：
![](https://images.seebug.org/content/images/2017/05/39.png-w331s)

上述通过Esteemaudit的利用流程如下：
![](https://images.seebug.org/content/images/2017/05/40.png-w331s)

###### 2.对比测试

我们以被攻击机器回连成功为标志，进行对比测试受影响系统和利用成功需要的关键触发条件，结果如下
![](https://images.seebug.org/content/images/2017/05/41.png-w331s)

测试结论：以上环境中并未对智能卡进行特别设置，除了域环境与远程桌面其余都是系统默认设置。所以，根据上述实验结果，网上所说的“需要开启智能卡登录”容易引起歧义（此结论也呼应了漏洞分析部分关于SmartCard的全部数据都由Esteemaudit模拟实现）。因此，只要是在域中开启了远程桌面的目标就可以被攻击，与是否是域控制器（DC）无关，与是否登录了域账号无关，与加入域后域控制器（DC）是否存在无关。

###### 3.防御建议

  * 关闭远程桌面
  * 退出域环境
  * 升级操作系统版本
  * 开启防火墙，过滤不信任的链接

### 四、总结

安全源自未雨绸缪，提高安全意识，及时止损。启明星辰ADLab会持续关注并研究由此次“永恒之蓝”以及影子经纪人陆续泄露的工具引发的“余震”，最后附上影子经纪人活动时间轴，也许下一次“蓝”不远了。
![](https://images.seebug.org/content/images/2017/05/42.png-w331s)
![](https://images.seebug.org/content/images/2017/05/43.png-w331s)

* * *

**启明星辰积极防御实验室（ADLab）**

ADLab成立于1999年，是中国安全行业最早成立的攻防技术研究实验室之一，微软MAPP计划核心成员。截止目前，ADLab通过CVE发布Windows、Linux、Unix等操作系统安全或软件漏洞近300个，持续保持亚洲领先并确立了其在国际网络安全领域的核心地位。实验室研究方向涵盖操作系统与应用系统安全研究、移动智能终端安全研究、物联网智能设备安全研究、Web安全研究、工控系统安全研究、云安全研究。研究成果应用于产品核心技术研究、国家重点科技项目攻关、专业安全服务等。
![](https://images.seebug.org/content/images/2017/05/adlab.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/306/>

