**作者**
：[百度安全实验室](https://mp.weixin.qq.com/s?__biz=MzA3NTQ3ODI0NA==&mid=2247483791&idx=1&sn=78858dc62d56bef962df9cc106b50a8b&chksm=9f6ea404a8192d12605c8537ed11c374b4466ab845dc6e1fcba2bd7fb41f9215c33758eccc3e)

### 一、概述

近期，百度安全实验室反高级威胁团队截获多封利用Microsoft Office Word漏洞进行攻击的恶意邮件。

通过对邮件附件样本进一步分析发现，其利用的漏洞为澳洲国防部计算机应急响应中心提交的CVE-2016-7193。该漏洞为RTF文件解析漏洞，成功利用该漏洞可以远程执行任意代码。我们拦截的样本双击打开后会在本地释放后门程序，从而完全控制目标主机。

微软已经于2016年10月11日发布了该漏洞的相关补丁（参见微软安全公告
MS16-121）。公告显示，该漏洞影响的Office版本非常广泛，几乎全版本Word都会受到该漏洞影响，包括最新的Word
2016。可以预见的将来，本漏洞将和CVE-2012-0158、CVE-2015-1641等经典Word内存破坏型漏洞一起，作为黑客进行APT渗透的标准工具包核心成员。虽然微软已经针对该漏洞发布了补丁，但由于多数用户安全意识薄弱，不倾向于打Office补丁，导致此类漏洞会长期威胁这批用户。通过进一步样本筛选以及情报确认，黑色产业地下市场已经有很成熟的利用该漏洞生成Exploit的工具在售(见附录参考链接)。

从2017年3月份开始，该漏洞利用样本首次在VirusTotal上出现。如下图所示，多家安全厂商虽然可以识别该样本，但命名均不准确，显然并未深入了解该漏洞的本质，可能误导用户对于漏洞针对性地防范。通过百度安全实验室数据监测显示，利用该漏洞进行的远程攻击事件数量正在不断增长，广大网民和安全从业者要提高警惕，做好相应的防范措施。

![](https://images.seebug.org/content/images/2017/04/7A385D36-563C-45C9-B779-B372CB083C71.png-w331s)

**受影响的 Word 版本:**

    
    
    Microsoft Word 2007 Service Pack 3
    Microsoft Word 2010 Service Pack 2
    Microsoft Word 2013 Service Pack 1
    Microsoft Word 2013 RT Service Pack 1
    Microsoft Word 2016
    Microsoft Word for Mac 2011
    Microsoft Word 2016 for Mac
    Microsoft Office 兼容包 Pack Service Pack 3
    Microsoft Word Viewer
    Microsoft SharePoint Server 2010 Service  Pack 2 上的 Word Automation Services
    Microsoft SharePoint Server 2013 Service  Pack 1 上的 Word Automation Services
    Microsoft Office Web Apps 2010 Service  Pack 2
    Microsoft Office Web Apps Server 2013  Service Pack 1

### 二、漏洞成因分析

  1. 分析环境  
文件信息：wwlibversion:12.0.4518.1014

  2. 分析过程  
经测试发现，该样本在一些特定的操作步骤下打开会利用失败，我们在这种情形下得到了如下的崩溃现场：

![](https://images.seebug.org/content/images/2017/04/392636F2-448B-46D2-98C0-E0FBC398D636.png-w331s)

![](https://images.seebug.org/content/images/2017/04/ED459CCB-EF96-4243-B829-38DB04756E0A.png-w331s)

可见崩溃点位于 wwlib.dll 中，而负责 RTF 解析的逻辑正是位于该模块。通过进一步回溯，edi 的值来源于
[obj_xx+0x761c]，相关的调用点如下:

![](https://images.seebug.org/content/images/2017/04/BE2F77CC-5130-4411-BEB3-710937CF1A8A.png-w331s)

关于这里用到的ROP链及shellcode本文最后将单独说明。这里继续查找地址edi+0x761c中0x09c00c0c的来源。我们定位到了如下关键代码：

![](https://images.seebug.org/content/images/2017/04/E4D78B83-2BBE-4377-8D85-FA02DBD97391.png-w331s)

很显然，关键代码位于一个大的switch结构中。应该是解析某种“bytecode”对应的handler部分。从这段代码来看，eax+0x75f8开始是一个字节数组(不是数组指针)，而位于eax+0x7618处是当前数组元素个数。每解析对应的“bytecode”时，该数组附加一个字节。数组最大长度被限制为0x40字节。按代码逻辑来看，数组起始于eax+0x75f8,终止于eax+0x7638。而表示数组当前元素个数的变量位于该数组范围内，即eax+0x7618。

**这似乎很不科学！**

在wwlib的反汇编中搜索所有对75f8的引用代码，也就是对该数组的引用。结果有些意外，只有一处有效的。关键代码如图：

![](https://images.seebug.org/content/images/2017/04/372D6648-BA6F-482A-85F5-C9A1A90FC114.png-w331s)

可以看出这个代码是复制该数组数据的逻辑，从拷贝大小参数来看该数组实际分配的大小为0x20字节。而在为该数组附加字节的逻辑中限制写成了0x40字节，发生数组越界写入，进而导致数组之后的类成员变量被改写。

重新加载样本，仔细观察该数组的数据赋值过程：

    
    
    0:000> bp 315EB380 "db @edi+75f8;"
    *** ERROR: Symbol  file could not be found.  Defaulted to  export symbols for C:\Program Files\Microsoft Office\Office12\wwlib.dll -    0:000> g
    //第1次附加字节
    (1e0.610):  Unknown exception - code e0000002 (first chance)
    03bb75f8  09 00 00 00  00 00 00 00-00 00 00 00 00 00 00 00   ................
    03bb7608  00 00 00 00 00 00 00 00-00 00 00 00 00 00  00 00  ................
    03bb7618  01 00 00 00 60 59 57 01-00 00 00 00 00 00 00 00   ....`YW.........
    03bb7628  00 00 00 00 00 00 00 00-00 00 00 00 00 00  00 00  ................
    03bb7638  00 00 00 00 00 00 00 00-00 00 00 00 00 00  00 00  ................
    03bb7648  00 00 00 00 60 59 57 01-00 00 00 00 00 00  00 00  ....`YW.........
    03bb7658  01 00 00 00 00 00 00 00-00 00 00 00 00 00  00 00  ................
    03bb7668  ff ff ff ff ff ff ff ff-00 00 00 00 00 00  00 00  ................
    eax=03bb0000  ebx=00000009  ecx=00000000  edx=02000000  esi=03bb0948  edi=03bb0000
    eip=315eb380   esp=00127b9c  ebp=00128124  iopl=0  nv up ei pl nz na po cy
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000  efl=00000203
    wwlib!wdGetApplicationObject+0x2977a:
    315eb380  e968c8a500  jmp  wwlib!DllCanUnloadNow+0x5598ab  (32047bed)
    0:000> g
    //第2次附加字节
    03bb75f8  09 c0 00 00  00 00 00 00-00 00 00 00 00 00 00 00   ................
    03bb7608  00 00 00 00 00 00 00 00-00 00 00 00 00 00  00 00  ................
    03bb7618  02 00 00 00 60 59 57 01-00 00 00 00 00 00 00 00   ....`YW.........
    03bb7628  00 00 00 00 00 00 00 00-00 00 00 00 00 00  00 00  ................
    03bb7638  00 00 00 00 00 00 00 00-00 00 00 00 00 00  00 00  ................
    03bb7648  00 00 00 00 60 59 57 01-00 00 00 00 00 00  00 00  ....`YW.........
    03bb7658  01 00 00 00 00 00 00 00-00 00 00 00 00 00  00 00  ................
    03bb7668  ff ff ff ff ff ff ff ff-00 00 00 00 00 00  00 00  ................
    eax=03bb0000  ebx=000000c0 ecx=00000001 edx=02000000 esi=03bb0948 edi=03bb0000
    eip=315eb380  esp=00127b9c ebp=00128124 iopl=0   nv up ei pl nz na po cy
    cs=001b  ss=0023   ds=0023  es=0023  fs=003b   gs=0000    efl=00000203
    wwlib!wdGetApplicationObject+0x2977a:
    315eb380  e968c8a500  jmp  wwlib!DllCanUnloadNow+0x5598ab  (32047bed)
    0:000> g
    ……略
    0:000> g
    //第0x20次附加字节
    03bb75f8  09 c0 0c 0c 0c c0  09 0c-0c c0 09 0c 0d c0 09 0c   ................
    03bb7608  0c 09 c0 0b 18 20  17 15-0c 0c c0 09 c0 09 0c 20   ..... .........
    03bb7618  20 00 00 00  60 59 57 01-00 00 00 00 00 00 00 00    ...`YW.........
    03bb7628  00 00 00 00 00 00 00 00-00 00 00 00 00 00  00 00  ................
    03bb7638  00 00 00 00 00 00 00 00-00 00 00 00 00 00  00 00  ................
    03bb7648  00 00 00 00 60 59 57 01-00 00 00 00 00 00  00 00  ....`YW.........
    03bb7658  01 00 00 00 00 00 00 00-00 00 00 00 00 00  00 00  ................
    03bb7668  ff ff ff ff ff ff ff ff-00 00 00 00 00 00  00 00  ................
    eax=03bb0000  ebx=00000020 ecx=0000001f  edx=02000000  esi=03bb0948 edi=03bb0000
    eip=315eb380  esp=00127b9c  ebp=00128124  iopl=0  nv up ei pl nz ac po cy
    cs=001b  ss=0023   ds=0023  es=0023  fs=003b  gs=0000  efl=00000213
    wwlib!wdGetApplicationObject+0x2977a:
    315eb380  e968c8a500  jmp  wwlib!DllCanUnloadNow+0x5598ab  (32047bed)
    
    0:000> g
    //第0x21次附加字节,注意，该次要正确覆盖偏移为7618处的变量（计数器变量，表示当前字节数组的字符个数），不然之后会无法覆盖到目标指针，恶意代码作者提供的数据为0x23，计数器加1后恰好为0x24，这个可以保证后续正确覆盖对象指针！
    
    03bb75f8  09 c0 0c 0c 0c c0  09 0c-0c c0 09 0c 0d c0 09 0c   ................
    03bb7608  0c 09 c0 0b 18 20  17 15-0c 0c c0 09 c0 09 0c 20   ..... .........
    03bb7618  24 00 00 00 60 59 57 01-00  00 00 00 00 00 00 00  $...`YW.........
    03bb7628  00 00 00 00 00 00 00 00-00 00 00 00 00 00  00 00  ................
    03bb7638  00 00 00 00 00 00 00 00-00 00 00 00 00 00  00 00  ................
    03bb7648  00 00 00 00 60 59 57 01-00 00 00 00 00 00  00 00  ....`YW.........
    03bb7658  01 00 00 00 00 00 00 00-00 00 00 00 00 00  00 00  ................
    03bb7668  ff ff ff ff ff ff ff ff-00 00 00 00 00 00  00 00  ................
    eax=03bb0000  ebx=00000023ecx=00000020 edx=02000000  esi=03bb0948 edi=03bb0000
    eip=315eb380  esp=00127b9c ebp=00128124 iopl=0  nv up ei pl nz na pe cy
    cs=001b  ss=0023   ds=0023  es=0023  fs=003b   gs=0000   efl=00000207
    wwlib!wdGetApplicationObject+0x2977a:
    315eb380  e968c8a500  jmp  wwlib!DllCanUnloadNow+0x5598ab  (32047bed)
    0:000> dps  1575960

之后将覆盖我们关心的偏移为0x761c处的值0x01575960，而该值为mso模块创建的一个对象指针，覆盖完成后该值被替换成了0x09c00c0c。

最终“0x40”字节的数组内容如下：

![](https://images.seebug.org/content/images/2017/04/C3D5F6E5-52A4-417A-AF66-35E6C1668BF9.png-w331s)

这些附加的字节又从哪里来呢？由于有针对RTF格式混淆技术的运用，现有工具无法满足提取ole对象的目的，我们人工仔细分析了该RTF文档发现，该RTF文档包括如下几个部分：

1）文件头（被混淆过，会影响一些工具或者杀毒引擎的解析）  
2）一个ocx控件（用于加载OTKLOADR、msvcr71等）  
3）一个内嵌的word文档（用于进行堆喷射）。0x09c00c0c就指向堆喷射的数据区域  
4）关键控制字区域。（用于数组越界写，劫持控制流）  
5）overlay数据。（编码payload和伪word文档）

通过分析第4部分的关键控制字区域，我们看到了如下的敏感数据：

![](https://images.seebug.org/content/images/2017/04/9AF176DD-0DD8-49F8-A62C-E866E9D8A6AB.png-w331s)

很明显，数据源于控制字\dfrxst。查阅RTF格式文档，相关说明如下：

![](https://images.seebug.org/content/images/2017/04/0297615F-B277-4F9E-A086-9EDBFE191633.png-w331s)

该控制字用于构造RevsionMark相关的字符串，参数为字节。即构造unicode字符串也是以单字节的形式进行的。然而文档中对控制字 \dfrxst
对应的内部字节数组是多长并未明确指出。详细查看该部分其它的控制字，我们发现了一个类似的控制字有这样的描述：

![](https://images.seebug.org/content/images/2017/04/249E7B90-A8FE-4667-9BD2-725B79D70474.png-w331s)

根据此处的描述我们推断对于\dfrxst，内部分配的字节数组长度为0x20字节。然而在解析该控制字的代码中，控制数组字节数的常量被认为是0x20(32)个Unicode字符，写成了
0x20* sizeof(wchar_t)，结果为0x40，大于内存分配的长度0x20，结果导致数组越界写入。
之后进一步的分析我们发现，被0x09c00c0c替换掉的偏移0x761c处的对象与\shp控制字相关。因而该控制字在样本中是必要的。还有两个控制字\shpbxignore和\shpbyignore用于操作\shp对应的对象过程中执行流的调整（位于wwlib.31fd6d99处的函数调用中），以避免相关的逻辑执行导致对象数据构造复杂化。当然，这里样本中这么做取决于作者开发漏洞利用的方法。我们调试发现，控制了\shp对象数据后，还有其它劫持控制流的路径，本文不再详述。

**3\. 原理及利用流程总结**

Word（wwlib.dll）在解析RTF文档的控制字
“\dfrxst”时发生内存越界写，导致紧邻的对象指针被覆盖。通过堆喷射技术，精心构造被覆盖的对象，可以达到劫持控制流，从而执行任意代码的目的。CVE-2016-7193漏洞原理的伪码表示如下：

    
    
    #define MAX_CHARS 0x20
    class CParserObj {
    public:
        BYTE m_ByteArray[MAX_CHARS]; //offs 75f8h DWORD m_NrOfChars;//offs 7618h
        CXXObj *m_pShpObj; //offs 761ch
        ......
        RESULT ParseControlWord(BYTE ByteCode,PVOID Params); 
    }
    RESULT CParserObj:: ParseControlWord(BYTE ByteCode,PVOID Params) 
    {
        ......;
        switch(ByteCode)
        {
        case BYTE_CODE_ dfrxst:
            if(m_NrOfChars < MAX_CHARS * sizeof(WCHAR) //0x40 {
                m_ByteArray[m_NrOfChars++] = (BYTE)Params; 
                }
            break; 
        case ......:
            break; 
        default:
            break; 
        }
    return RESULT_ERROR_CODE; 
    }

### 三、ROP 链、shellcode 和 payload 简要分析

首先，样本在劫持控制流后，首先运行ROP链（基于msvcr71构造）将shellcode所在内存区修改为可执行属性，对应的代码和ROP链的信息如下：

![](https://images.seebug.org/content/images/2017/04/55017116-6F7C-45DC-A2E9-A58B0DB9F37C.png-w331s)

![](https://images.seebug.org/content/images/2017/04/9A43A6DC-B17C-4A4A-BAFF-70623D6893F3.png-w331s)

内存属性修改成功后，接着跳入shellcode

![](https://images.seebug.org/content/images/2017/04/1FEE7C55-EAD8-44DF-86CA-223452D19A67.png-w331s)

然后执行解码器解码shellcode。该解码器很简单仅仅是xor解码。

最后执行解码后的shellcode，其功能包括：

1）暴力遍历句柄，寻找当前进程中对应RTF文档的句柄。  
2）创建RTF文档的内存映射。  
3）通过 egg hunt 技术定位位于RTF文档Overlay部分的大型shellcode，并跳入执行，加载执行payload。

![](https://images.seebug.org/content/images/2017/04/D35B7135-9060-458C-B8FB-A2DC6024FB14.png-w331s)

本文分析的Payload中包含一个正常doc文件用于覆盖当前文档迷惑用户和一个要释放的商业远控木马用于控制目标主机。当然，这里的payload可以很方便地替换成其它的恶意程序，满足黑客个性化的需求。

### 四、结语

如今越来越多的APT攻击使用Office套件中的Nday甚至0day漏洞进行攻击，虽然微软提供了该漏洞相应的修复补丁，但大部分用户对于此类应用补丁的不重视造成了漏洞威胁依然存在。百度安全实验室建议用户提高安全意识，及时更新如Office、Flash、浏览器等常被漏洞利用的应用程序，对于安全性未知的程序应谨慎执行。

### 参考链接：

1、微软 MS16-121 安全公告 https://technet.microsoft.com/library/security/ms16-121

2、exploit生成器的相关信息 http://www.tuicool.com/articles/BNnqArU
https://www.youtube.com/watch?v=D3hwTBD0xE4

3、RTF官方文档 https://www.microsoft.com/en-us/download/details.aspx?id=10725

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/288/>

