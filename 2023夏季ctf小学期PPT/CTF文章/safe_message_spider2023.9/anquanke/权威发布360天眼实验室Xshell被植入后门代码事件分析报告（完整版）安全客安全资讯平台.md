# 【权威发布】360天眼实验室：Xshell被植入后门代码事件分析报告（完整版）

阅读量 **307723**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-08-18 18:29:34

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

****

**  
**

**文档信息**

  

**事件概要**

  

**事件简述**

近日，非常流行的远程终端Xshell被发现被植入了后门代码，用户如果使用了特洛伊化的Xshell工具版本会导致本机相关的敏感信息被泄露到攻击者所控制的机器甚至被远程控制执行更多恶意操作。

Xshell特别是Build
1322在国内的使用面很大，敏感信息的泄露及可能的远程控制导致巨大的安全风险，我们强烈建议用户检查自己所使用的Xshell版本，如发现，建议采取必要的补救措施。

  

**事件时间线**

**2017年8月7日**

流行远程管理工具Xshell系列软件的厂商NetSarang发布了一个更新通告，声称在卡巴斯基的配合下发现并解决了一个在7月18日的发布版本的安全问题，提醒用户升级软件，其中没有提及任何技术细节和问题的实质，而且声称没有发现漏洞被利用。

**2017年8月14日**

360威胁情报中心分析了Xshell Build
1322版本（此版本在国内被大量分发使用），发现并确认其中的nssock2.dll组件存在后门代码，恶意代码会收集主机信息往DGA的域名发送并存在其他更多的恶意功能代码。360威胁情报中心发布了初始的分析报告，并对后续更复杂的恶意代码做进一步的挖掘分析，之后其他安全厂商也陆续确认了类似的发现。

**2017年8月15日**

卡巴斯基发布了相关的事件说明及技术分析，与360威胁情报中心的分析完全一致，事件可以比较明确地认为是基于源码层次的恶意代码植入。非正常的网络行为导致相关的恶意代码被卡巴斯基发现并报告软件厂商，在8月7日NetSarang发布报告时事实上已经出现了恶意代码在用户处启动执行的情况。同日NetSarang更新了8月7日的公告，加入了卡巴斯基的事件分析链接，标记删除了没有发现问题被利用的说法。

  

**影响面和危害分析**

目前已经确认使用了特洛伊化的Xshell的用户机器一旦启动程序，主机相关基本信息（主机名、域名、用户名）会被发送出去。同时，如果外部的C&C服务器处于活动状态，受影响系统则可能收到激活数据包启动下一阶段的恶意代码，这些恶意代码为插件式架构，可能执行攻击者指定任意恶意功能，包括但不仅限于远程持久化控制、窃取更多敏感信息。

根据360网络研究院的C&C域名相关的访问数量评估，国内受影响的用户或机器数量在十万级别，同时，数据显示一些知名的互联网公司有大量用户受到攻击，泄露主机相关的信息。

  

**解决方案**

检查目前所使用的Xshell版本是否为受影响版本，如果组织保存有网络访问日志或进行实时的DNS访问监控，检查所在网络是否存在对于附录节相关IOC域名的解析记录，如发现，则有内网机器在使用存在后门的Xshell版本。

目前厂商NetSarang已经在Xshell Build
1326及以后的版本中处理了这个问题，请升级到最新版本，修改相关系统的用户名口令。厂商修复过的版本如下：

Xmanager Enterprise Build 1236

Xmanager Build 1049

Xshell Build 1326

Xftp Build 1222

Xlpd Build 1224

软件下载地址：<https://www.netsarang.com/download/software.html>

  

**技术分析**

**基本执行流程**

Xshell相关的用于网络通信的组件nssock2.dll被发现存在后门类型的代码，DLL本身有厂商合法的数字签名，但已经被多家安全厂商标记为恶意：

360威胁情报中心发现其存在加载执行Shellcode的功能：

我们将这段代码命名为loader_code1,
其主要执行加载器的功能，会再解出一段新的代码（module_Activation），然后动态加载需要的Windows API和重定位，跳转过去。

经过对进程执行的整体分析观察，对大致的执行流程还原如下图所示：

**基本插件模块**

**Module_Activation**

module_Activation会开启一个线程，然后创建注册表项：HKEY_CURRENT_USERSOFTWARE-[0-9]+(后面的数字串通过磁盘信息xor
0xD592FC92生成)，然后通过RegQueryValueExA查询该注册表项下”Data”键值来执行不同的功能流程。

当注册表项”Data”的值不存在时，进入上传信息流程，该流程主要为收集和上传主机信息到每月一个的DGA域名，并保存服务器返回的配置信息，步骤如下：

获取当前系统时间，根据年份和月份按照下面的算法生成一个长度为10-16的字符串，然后将其与”.com”拼接成域名。

年份-月份 和 生成的域名对应关系如下：

接着，将前面收集的网络、计算机、用户信息按照特定算法编码成字符串，然后作为上面的域名前缀，构造成查询*. nylalobghyhirgh.com 的DNS
TXT的数据包，分别向8.8.8.8 | 8.8.4.4 | 4.2.2.1 | 4.2.2.2 | [cur_dns_server]
发送，然后等待服务器返回。

服务器返回之后（UDP）校验数据包，解析之后把数据拷贝到之前传入的参数中，下一步将这些数据写入前面设置的注册表项，也就是HKEY_CURRENT_USERSOFTWARE-[0-9]+的Data键中。这些数据应该是作为配置信息存放的，包括功能号，上次活跃时间，解密下一步Shellcode的Key等等。

当RegQueryValueExA查询到的Data键值存在数据时，则进入后门执行流程，该流程利用从之前写入注册表项的配置信息中的Key解密loader_code2后跳转执行。

解密loader_code2的算法如下：先取出module_Activation偏移0x3128处的original_key，接着取key的最后一个byte对偏移0x312C处长度为0xD410的加密数据逐字节进行异或解码，每次异或后original_key再与从配置信息中读取的key1、key2进行乘、加运算，如此循环。

解密之后跳转到loader_code2中,
loader_code2其实和loader_code1是一样的功能，也就是一个loader，其再次从内存中解密出下一步代码：module_ROOT,
然后进行IAT的加载和重定位，破坏PE头，跳转到ROOT模块的入口代码处。

**Module_ROOT**

ROOT模块即真正的后门核心模块，为其他插件提供了基本框架和互相调用的API，其会在内存中解密出5个插件模块Plugin、Online、Config、Install和DNS，分别加载到内存中进行初始化，如果插件在初始化期间返回没有错误，则被添加到插件列表中。

每个插件由DLL变形而成，加载后根据fwReason执行不同功能
(其中有一些自定义的值100,101,102,103,104).不同的插件模块fwReason对应的功能可能有细微的差异，整体上如下：

接着ROOT模块搜索ID为103（“Install”）的插件，并调用其函数表的第二个函数。进行安装操作。

同时ROOT模块也通过把自身函数表地址提供给其他模块的方式为其他模块提供API，这些API主要涉及跨模块调用API、加解密等功能。

另外其中解密的函数以及加载插件的函数也是由动态解出来的一段shellcode，可见作者背后的煞费苦心：

**Module_Plugin**

Plugin模块为后门提供插件管理功能，包括插件的加载、卸载、添加、删除操作，管理功能完成后会通过调用Online的0x24项函数完成回调，向服务器返回操作结果。模块的辅助功能为其他插件提供注册表操作。

Plugin的函数列表如下：

其中比较重要的是fuc_switch和CreateLoadRegThread。

fuc_switch

此函数根据第二个参数结构体的0x4偏移指令码完成不同操作，指令码构造如下：

（ID<<0x10）| Code

0x650000功能

此功能获取当前加载的插件列表字符串，此功能遍历全局ModuleInfo结构体获取模块名称列表，完成后通过Online模块的0x24执行调用者参数的回调函数，该回调为网络通知函数。

0x650001功能

此功能首先通过参数ID获取模块信息，如果该ID未被加载，则调用Root的加密函数加密模块数据，随后更新对应注册表值，完成模块更新，模块数据加密后保存，在Root模块初始化过程中会调用Plugin的注册表监听线程，该线程检测到注册表项变动后加载此模块：

0x650002功能

此功能通过文件名称加载PE结构的插件，Root模块的0x30项调用LoadLibrary函数加载DLL，并将插件结构插入全局插件双链表：

0x650003功能

该功能通过模块基址查找指定模块，内存卸载模块后删除对应注册表键值，彻底卸载模块：

0x650004功能

此功能检测参数指定模块ID是否被加载，如果该ID已被加载，通过Online的网络回调发送一个长度为1，数据为0x00的负载网络包，如果ID未被加载则发送一个长度为0的负载网络包。

CreateLoadRegThread

该函数创建线程，异步遍历注册表项“SOFTWAREMicrosoft<MachineID>”，其中MachineID根据硬盘序列号生成。随后创建Event对象，使用RegNotifyChangeKeyValue函数监测插件注册表键值是否被更改，被更改后则遍历键值回调中解密并加载模块并插入全局插件ModuleInfo。

Plugin模块的维护数据结构为双链表，并为每个插件定义引用计数，当引用计数为0时才从内存卸载插件。结构大致如下：

Module_Online

该模块主要功能是与服务器连接，获取服务器返回的控制指令，然后根据控制指令中的插件ID和附加数据来调用不同的插件完成相应的功能。同时Online也提供API接口给其他插件模块用于回传数据。

Online模块的函数表如下，可以看到其提供了一系列收发数据的API

网络连接开始时首先调用Config表中的第二个函数读取配置信息，通过InternetCrackUrlA将配置信息中的字符串(默认为dns://[www.notepad.com](http://www.notepad.com)
)取得C&C地址，并根据字符串前面的协议类型采取不同的连接方式，每个协议对应一个ID，同时也是协议插件的ID，目前取得的样本中使用的DNS协议对应ID为203。（虽然有HTTP和HTTPS，但是ONLINE只会使用HTTP），协议与ID的对应关系如下：

在建立起与C&C服务器的连接之后，可以根据接收到的服务器指令调用指定的插件执行指定的操作，并返回执行结果。首先先接收0x14字节的头部数据，这些数据将用于解压和解密下一步接收的指令数据。

接受的指令结构大致如下：

    
    
    struct Command
    {
    DWORD HeaderSize; 
    WORD OpCode;
    WORD PluginID;
    DWORD DWORD0;
    DWORD DataSize;
    DWORD DWORD1;
    DWORD DataBuff
    ...
    };

Online模块会根据PluginID找到对应的模块，调用其函数列表的第一个函数func_switch()，根据OpCode执行switch中不同的操作，并返回信息给服务器。

另外当Online使用内置的URL方式时，会根据指定的参数使用HTTP-GETHTTPS-GET FTP来下载文件：

在请求服务器的时候，也会将受害者的基本信息上传到服务器中，这些信息包括：当前日期和时间、内存状态、CPU信息、可用磁盘空间、系统区域设置、当前进程的PID、操作系统版本、host信息和用户名。

Online模块还通过调用Plugin模块提供的API维护一个注册表项：

HKLMSOFTWARE[0-9A-Za-z]{7} 或者 HKCUSOFTWARE[0-9A-Za-z]{7}，内容是记录系统时间和尝试连接次数。

**Module_Config**

Config模块在初始化的过程中，先分别解出数据段保存的一些默认配置信息，然后把这些参数拼接起来，使用Root模块虚表中的DoEncipher函数进行加密，最后保存到一个用硬盘卷标号计算出来的路径里。同时Config模块提供了读取配置文件的接口。

Config模块的虚表共有3个函数

ModInit

该函数共有三个子功能

660000

该功能主要调用Config模块的GetDecodedConfigData函数，获取配置文件作为Payload，最终调用Online模块虚表的0x24功能（上传给CC服务器）

660001

功能主要就是传递了自己的功能ID，没有Payload

660002

功能主要就是传递了下自己的功能ID，没有Payload

GetDecodedConfigData

该函数首先通过磁盘卷标号计算得到当前机器的配置文件路径。然后读取配置文件，并调用Root模块的DoDecipher解密后，返回结果给调用者。

GetEncodedVolumeSN

该函数首先获取系统盘的磁盘卷标号，根据压入的szKey计算出一个结果，然后调用Root模块的Base64Encode1Byte来加密得到加密串。

默认配置信息主要为以下信息

接着写入配置文件，分别通过磁盘卷标号，以及不同的key，得出四组不同的加密串

然后和依次系统路径”%ALLUSERSPROFILE%\”拼接得到最终配置文件的路径（例如C:ProgramDataYICIOPMIEYKOSIYMXIEUWSOY），最后将加密后的配置文件直接写入到该路径下。

**Module_Install**

Install模块主要用于检测进程环境、控制进程退出和进入后门流程。Install模块被ROOT模块调用其函数表的第二个函数开始执行，首先调整进程权限，然后调用Config模块函数表的第二个函数读取配置信息。

接着通过判断ROOT模块从上层获取的参数进行不同的流程：

当参数为234时，创建互斥体 “Global[16-48个随机字符]”，并直接调用Online模块函数表偏移为0x04的函数，即开始循环连接C&C服务器。

当参数为56时，尝试加载ID为106（这个模块不在默认内置的模块列表中，需要进一步下载）。

如果都不是以上情况，则尝试以系统权限启动winlogon.exe或者启动scvhost.exe，然后注入自身代码，然后启动Online模块。

同时Install模块还会提供检测当前运行环境的接口：是否在调试、是否被进程监控、流量监控等，下面是一些特征字符串和相关代码：

**Module_DNS**

该模块的主要功能是使用DNS协议处理CC通信过程。模块的函数表如下，对

应的函数功能分别为：

模块的工作流程为：

在模块入口函数100编号对应的初始化过程中，模块会开启线程，等待其他插件数据到来，当收到数据时，调用dispatch将数据通过DNS发送到CC服务器。

其他插件调用该插件的第二个函数(也就是ThreadRecv函数)时，模块开启线程从CC接收数据，并将解码后的数据写到共享内存。

其他插件调用该插件的第三个函数(也就是RecvDataProc函数)可以取得该模块与CC服务器通信后的数据内容

其他插件调用该插件的第四个函数(也就是SendDataProc 函数)可以使用该模块向CC服务器发送数据内容。

在初始化函数中，创建一个线程，在线程内部通过互斥量等待，当互斥量被触发后，调用该模块的dispatch函数。

从CC接收数据的代码过程

在通信过程中，开启线程接收数据

线程函数将接收到数据存储在结构体的0x60偏移处

接收到的数据首先判断接收到的数据长度是否符合要求，然后使用解码函数(DecodeCCData1)进行解码并判断解码后的内容格式是否符合。此后，使用同样的解码算法(DecodeCCData1)再对数据进行一次解码。

将上面解码后的内容使用另一个解码算法(DecodeCCData2)进行解码，解出来的内容的第一个DWORD为解密KEY，使用解密KEY将接收到的数据进行解密后，判断解密后的内容的第一个WORD为数据包类型id，数据包类型ID包括:0，1，3三种。每种不同的数据包使用不同的结构类型和不同的解密算法。

在对不同的数据类型的处理过程中，都会将解码后的内容写入到结构体偏移+0x5C的地址中，该地址就是数据传输时使用的共享内存地址。

数据包的解密算法代码片段为：

向CC发送数据的代码片段

**代码分析对抗**

样本使用到的技术很多，例如动态加载、花指令、反调试、多层解密、代码注入等，使用的这些技巧大大增加了安全人员分析工作所需要花费的时间，也能有效躲避杀软检测，并使一些分析工具产生异常而无法正常执行恶意代码流程。下面举例说明一下使用到的技巧：

代码中加入了大量的JMP类型花指令，还有一些无效的计算，比如下图中红框中ECX。

在每次获取API地址之后，都会检测API代码第一字节是否等于0xcc，如果等于则结束后续行为，否则继续。

Shellcode通过自身的配置信息，通过一个for循环，循环4次。每次根据EDI定位配置信息，通过下面的结构体来获取要拷贝的数据的大小，将所有需要的数据拷贝到申请的内存中。然后解密数据。

循环拷贝数据

  

**关联分析及溯源**

8月的域名为 nylalobghyhirgh.com，360威胁情报中心显示此域名为隐私保护状态：

此域名目前在7月23日被注册，8月3日达到解析量的顶峰，360网络研究院的数据显示解析量巨大，达到800万。

所有的请求类型为NS记录，也就是说域名极有可能被用来析出数据而不是用于C&C控制，这与前面的分析结论一致。

而notped.com作为已知的相关恶意域名，我们发现其注册人为Yacboski
Curtis，据此关联点找到了一些其他的关联域名，具体见附件的IOC节，由于这些域名并没有找到对应的连接样本，目前只是怀疑，不能确定就是其他的相关恶意域名。

  

**参考链接**

<https://www.netsarang.com/news/security_exploit_in_july_18_2017_build.html>

<https://securelist.com/shadowpad-in-corporate-networks/81432/>

<https://cdn.securelist.com/files/2017/08/ShadowPad_technical_description_PDF.pdf>

**附件**

**IOC列表**

**DNS 隧道编解码算法**

Xshell后门代码通过DNS子域名的方式向C&C服务器输出收集到的主机信息，以下是分析得到的编码算法及实现的对应解码程序。

编码算法是先经过下图的算法1加密成二进制的形式如图：

算法1加密后的数据：

然后把结果转换成可见的字符转换方法是通过每个字节的高位减‘j’低位减‘a’，把1个字节拆分成2个字节的可见字符，这样就浪费了一个字节：

解密算法是加密算法的逆运算，解密算法流程入下图：

根据网上的一些公开的流量数据，

解密出的一些上传的数据：

实现的解码代码如下：

    
    
    int sub_1C3E(int a1, unsigned char* a2, int a3, int a4)
    {
    char v4; // cl@1
    int v5; // esi@1
    unsigned char* v6; // edi@2
    byte v7[1024]= {0}; // eax@11
    char v8; // dl@11
    int v10; // [sp+4h] [bp-10h]@1
    int v11; // [sp+8h] [bp-Ch]@1
    int v12; // [sp+Ch] [bp-8h]@1
    int v13; // [sp+10h] [bp-4h]@1
    v4 = 0;
    v5 = 0;
    v10 = a1;
    v11 = a1;
    v12 = a1;
    v13 = a1;
    int i = 0;
    if ( a3 > 0 )
    {
    v6 = a2 - a4;
    do
    {
    if ( v5 & 3 )
    {
    switch ( v5 & 3 )
    {
    case 1:
    v11 = 0xBFD7681A - 0x7DB1F70F * v11;
    v4 = (*((byte *)&v11  + 2) ^ (*((byte *)&v11 + 1)
    + (*((byte *)&v11) ^ v4)))
    - *((byte *)&v11 + 3);
    //v7 = (byte *)(v5 + a4);
    v8 = v4 ^ *(byte *)(v6 + v5++ + a4);
    v7[i] = v8;
    i++;
    break;
    case 2:
    v12 = 0xE03A30FA - 0x3035D0D6 * v12;
    v4 = (*((byte *)&v12  + 2) ^ (*((byte *)&v12 + 1)
    + (*((byte *)&v12) ^ v4)))
    - *((byte *)&v12 + 3);
    //v7 = (byte *)(v5 + a4);
    v8 = v4 ^ *(byte *)(v6 + v5++ + a4);
    v7[i] = v8;
    i++;
    break;
    case 3:
    v13 = 0xB1BF5581 - 0x11C208F * v13;
    v4 = (*((byte *)&v13  + 2) ^ (*((byte *)&v13 + 1)
    + (*((byte *)&v13) ^ v4)))
    - *((byte *)&v13 + 3);
    //v7 = (byte *)(v5 + a4);
    v8 = v4 ^ *(byte *)(v6 + v5++ + a4);
    v7[i] = v8;
    i++;
    break;
    }
    }
    else
    {
    v10 = 0x9F248E8A - 0x2F8FCE7E * v10;
    v4 = (*((byte *)&v10 + 2) ^ (*((byte *)&v10 + 1)
    + (*((byte *)&v10 ) ^ v4)))
    - *((byte *)&v10 + 3);
    //v7 = (byte *)(v5 + a4);
    v8 = v4 ^ *(byte *)(v6 + v5++ + a4);
    v7[i] = v8;
    i++;
    }
    }
    while ( v5 < a3 );
    printf("Last Step Decode：%s", (char*)v7);
    }
    return 0;
    }
    int _tmain(int argc, _TCHAR* argv[])
    {
    unsigned char szText[117] = "ajajlyoogrmkdmnndtgphpojmwlvajdkbtephtetcqopnkkthlplovbvardopqfleonrgqntmresctokkxcnfvexhjpnpwepgnjubrbrbsenhxbkmy";
    unsigned char szXXX[58] = {0};
    for (int i=0; i<57; i++)
    {
    unsigned char One = szText[2*i] - 'a';
    unsigned char Two = szText[2*i+1] -'j';
    printf("%d, %drn", One, Two);
    unsigned char Total = One+Two*16;
    szXXX[i] = Total;
    }
    printf("First Step Decode：%s", (char*)szXXX); 
    sub_1C3E(0, szXXX, 56, 0); //算法1
    return 0;
    }

**ShellCode的处理**

本次后门多次解出ShellCode的过程都是用的同一套模版代码。经过分析发现PE的一些基本信息还是保留了的，ShellCode解码用到的结构整理如下：

    
    
    struct ShellContext
    {
    u32 dwShellKey;//用于解密重定位表以及输入表的数据
    u32 HeadCheck;//和dwShellKey异或用来校验Key是否合法
    u32 SizeOfImage;//Image大小
    u32 ModBase;//默认基地址
    u32 RelocTable;//重定位表偏移
    u32 RelocSize;//重定位表大小
    u32 ImportTable;//输入表偏移
    u32 ImportSize;//输入表大小
    u32 OEP;//OEP地址
    u16 Magic;//010b为pe32
    u8MajorVer;//链接器版本
    u8  MinorVer;//
    u32 NumberOfSections;//节表数
    u32 timeStamp;//时间戳
    SectionDescsecArray[1]; //节表描述数组
    };

下面介绍下ShellCode的加载过程，在调用Loader之前先将ShellCode起始地址以及大小入栈。

然后进入Loader部分处理流程：

1）从PEB里找到Kernel模块，从中找到LoadLibrary，GetProcAddress，VirtualAlloc以及Sleep，以备后续过程使用。

2）接着利用ShellCode中的SizeOfImage去分配内存。

3）往分配的内存头部填充垃圾数据，一直填充到代码段开始。

4）根据结构里保存的节表信息，依次填充到分配的内存。

5）如果结构里重定位信息不为空，则使用dwShellKey去解密重定位数据并利用重定位数据去修正内存的数据。处理完之后把重定位数据清零。

解密重定位数据的算法还原如下

6）如果输入表信息不为空，接着使用重定位处理用的dwShellKey去解密输入表对应的字符串信息，如果是ordinal方式的则不做处理。使用解密了的DLL名以及API名获取到API地址后，并不直接填充，而是先把地址做求补操作后，生成一个小的stub再填进去。

最后再把输入表用到的数据清零。

解密输入表的流程还原如下：

7）跳到入口处执行，并设置fdwReason为1。

根据保留的结构可以大致还原出本来模块文件。

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信威胁情报中心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86655](/post/id/86655)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t01dce0f9e833e11f13.png) 奇安信威胁情报中心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

