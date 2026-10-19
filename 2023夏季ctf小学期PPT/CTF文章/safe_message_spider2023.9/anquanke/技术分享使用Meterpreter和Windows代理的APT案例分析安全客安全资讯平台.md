# 【技术分享】使用Meterpreter和Windows代理的APT案例分析

阅读量 **147009**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-05-17 14:13:26

 **x**

##### 译文声明

本文是翻译文章，文章来源：medium.com/@br4nsh

原文地址：<https://medium.com/@br4nsh/a-meterpreter-and-windows-proxy-case-4af2b866f4a1>

译文仅供参考，具体内容表达以及含义原文为准。

****

翻译：[ **興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

**稿费：200RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**  
**

**一、前言**

几个月之前，我自己开发了一个APT工具，工具的使用场景为企业中的Windows攻击模拟环境，这个环境只能通过代理方式访问互联网。在测试工具时，我发现使用HTTPS协议的Meterpreter载荷工作不正常。说实话，一开始我并不确定这个问题是否与我的APT工具的工作机制有关（将Meterpreter载荷注入内存），还是与其他原因有关。在这个环境中，我的APT工具必须与代理打交道，因此我不得不找到确切原因，再去解决这个问题。

在全面分析整个情况之后，我发现我正在使用的Meterpreter载荷可能无法正常工作。当时我使用的Meterpreter载荷为“windows/meterpreter/reverse_https”，Metasploit的版本为4.12.40-dev。

在讨论技术细节之前，先介绍一下我的测试环境：

1、受害者机器系统及IP地址：Windows 8.1 x64 Enterprise/10.x.x.189；

2、互联网访问方式：通过认证代理访问（设置DHCP选项，并且在IE中勾选“自动检测设置（Automatically detect
settings）”选项）；

3、代理服务器的外部IP地址：190.x.x.x；

4、攻击者主机IP地址：190.y.y.y；

5、Meterpreter载荷：windows/meterpreter/reverse_https。

需要注意的是，“reverse_https”载荷是一个传输器载荷（staged
payload）。也就是说，这是一种“先遣队”类型的载荷，在受害者主机上运行，可以下载真正的Meterpreter
DLL载荷（如metsrv.x86.dll或者metsrv.x64.dll），通过反射注入方式（reflective
injection），将DLL注入到受害者主机内存中。

受害者主机的外部IP如下图所示：

受害者主机的代理配置情况如下图所示（已勾选“自动检测设置”选项）：

“autoprox.exe”工具在受害者主机上的运行结果如下图所示。可以看到，受害者主机通过DHCP（252选项）获取代理配置信息。

从上图可知，对于“www.google.com”来说，主机在访问这个地址必须使用“10.x.x.20:8080”这个代理。如果不使用工具，我们也可以手动下载wpad.dat文件（这个文件位置可通过DHCP的252选项获得），检查其中包含的规则，了解代理的具体使用场景。

请注意：根据我的研究结果，autoprox.exe（pierrelc@microsoft.com写的一款工具）首先会使用Windows
API搜索DHCP提供的代理信息，如果搜索失败，会尝试通过DNS获取代理信息。

  

**二、具体分析**

在分析这个问题的过程中，我会修改Meterpreter载荷中的几行代码，并在受害者主机上测试运行，因此，我们需要创建一个使用HTTPs协议的meterpreter反弹载荷（windows/meterpreter/reverse_https）的后门程序，或者使用某个Web传输模块。对你而言，选择使用那种方式都可以。

请注意：我们可以使用Shellter以及其他可信的程序（如putty.exe）创建一个简单的后门程序，除此之外，我建议使用Metasploit的Web传输载荷。我们将要修改的是传输体（stage）载荷，而不是传输器（stager）载荷，因此我们只需要创建一个后门程序，就能满足所有实验场景。

接下来，我们在受害者主机上运行后门程序，在攻击者主机上运行Metasploit监听端，看一下执行结果。

如下图所示， MSF handler在攻击者主机的443端口上监听，之后接收到来自于受害者主机的一个连接请求（源端口为18903）：

从上图可知，受害者主机已经连接到攻击者主机上的handler，此时我们应该已经获得了一个Meterpreter
shell。然而，不管我输入什么命令，我都收不到受害者主机的有效回应，然后会话就会被关闭。

当传输器载荷（很小的一段代码）在受害者主机上运行时，它会回连到攻击者主机上的监听端，下载真正的攻击代码（即Meterpreter载荷）并将其注入到内存中，之后再将控制权交给攻击代码。加载成功后Meterpreter载荷会再次连接到攻击者主机上监听端，以便攻击者与受害主机系统进行交互。

到目前为止，我们知道传输器载荷已经成功在受害者主机上运行，能够穿透代理回连到监听端。然而，当传输体载荷注入到受害者主机内存后（如果注入过程有效的话），哪里出了点问题导致传输体载荷不能正常工作。

请注意：为了打消你的顾虑，我检查了整个攻击过程是否受到AV软件的影响，然而这些攻击载荷都不会被AV软件查杀。此外，为了避免网管对HTTPS的监听行为，我手动创建了一个PEM证书，配置监听端使用这个证书。使用浏览器观察手动访问Metasploit监听端时的指纹信息，将这个指纹与刚刚创建的证书的指纹信息进行对比，确保证书在传输过程中没有被替换。排除掉这些可能存在的问题之后，我决定继续在其他地方查找问题的真正原因。

接下来我决定嗅探来自于受害者主机的网络流量，从黑盒测试角度获取更多的信息。

在受害者主机上使用Wireshark抓的包如下图所示：

我们可以从上图中观察到受害者主机（10.x.x.189）与代理服务器（10.x.x.20:8080）之间所建立的TCP连接，受害者主机发送了一个CONNECT方法（第一个报文），请求与攻击者主机（190.x.x.x:443）建立一个安全的（SSL/TLS）通信渠道。此外，我们从第一和第二个数据包中可知，受害者主机的请求中使用了NTLM身份验证（NTLMSSP_AUTH），代理服务器的响应是“连接建立”（HTTP/1.1
200）。之后就是SSL/TLS握手过程。

值得一提的是，上图反应的是第一阶段的发送和接收数据包，也就是传输器载荷执行时的通信数据包。连接建立完毕后，通信两端（即客户端和服务端）之间就会进行典型的SSL/TLS握手过程，建立加密通信信道，之后传输体载荷就会经过加密信道，从攻击者主机发往受害者主机。

现在，我们可以确定Meterpreter在第一阶段的部署过程（即传输器载荷）工作正常，接下来我们需要了解第二阶段的工作过程，也就是传输体载荷和监听端之间的通信过程。为此，我们只需要继续分析Wireshark的抓包结果即可。

传输器载荷和监听端的最后一部分通信数据包如下图所示，在这之后，受害者主机会尝试不经过代理，直接与攻击者主机建立连接：

在上图的前5个数据包中，我们可以看到受害者主机（10.x.x.189）与代理服务器（10.x.x.20）的TCP连接中断标识（FIN、ACK；ACK；FIN、ACK；ACK）。之后我们可以看到，第6个数据包为受害者主机直接发往攻击者主机的数据包，其中包含一个TCP
SYN标志（用来初始化一个TCP握手过程），也就是说受害者主机没有使用代理服务器作为建连的跳板。最后，我们可以看到，第7个数据包为受害者主机所收到的网关响应报文，表明建连目的地（即攻击者主机）无法通过该网络直接访问（我在前文提到过，这个环境中必须使用代理服务器才能访问互联网）。

通过上述抓包结果，我们知道Meterpreter会话建立失败。我们认为Meterpreter传输体载荷之所以不能访问监听端，原因在于传输体载荷使用了直接建连方式，没有像传输器载荷那样使用系统代理服务器。

现在我们要做的就是下载Meterpreter源代码，尝试从源代码角度分析这种行为的根本原因。为此，我们需要遵循Rapid7在github上发布的如何在Windows上编译的指南（读者可以在本文的参考资料中找到相关链接）。

根据指南给出的建议，我们使用Visual Studio 2013打开项目解决方案文件（metasploit-payloadscmeterpreterworkspacemeterpreter.sln），开始分析源代码。

浏览源代码之后，我们发现在源代码的“server_transport_winhttp.c”文件中，有关于代理处理逻辑的具体实现（请阅读参考资料快速定位源代码文件）。

Meterpreter中对代理设置情况的判断如以下部分代码所示：

我之前从github了解到，Meterpreter的reverse_https（第一次）会尝试使用WinHTTP Windows
API访问互联网，正如我们在这部分代码中看到的情况一样。

从代码中我们可以看到很多dprint调用语句，使用这些语句是为了方便调试，以便在运行时给我们提供有价值的信息。

为了使这些调试信息对我们可见，我们需要编辑源代码中的common.h头文件，修改其中的DEBUGTRACE预处理器（pre-processor）常量，这样就可以使服务器（受害者主机中加载的Meterpreter DLL文件）在Visual
Stuido的Output窗口打印调试信息，我们也可以使用SysInternals的DebugView工具或者Windbg工具查看调试信息。

在原始的common.h头文件中，DEBUGTRACE常量在代码中处于被注释状态，如下图所示：

现在我们可以编译工程文件，将生成的“metsrv.x86.dll”二进制文件（位于“metasploit-payloadscmeterpreteroutputx86”文件夹中）拷贝到攻击者主机中（即运行metasploit监听端的主机）的正确文件目录中（对我来说，这个目录位于“/usr/share/metasploit-framework/vendor/bundle/ruby/2.3.0/gems/metasploit-payloads-1.1.26/data/meterpreter/”路径）。

在调试主机上，我们运行DebugView工具，然后执行后门程序，使Meterpreter传输器载荷再次运行。

受害者主机上的调试信息输出如下：

从Meterpreter生成的调试（日志）信息中，我们可以看到第70-74行对应的是 “server_transport_winhttp.c”
源代码文件中第48-52行的dprintf语句。具体说来，第71行（““[PROXY] AutoDetect:
yes””）表明程序检测出来受害者主机上的代理被设置为“自动检测（AutoDetect）”。然而，获取的代理URL地址却为空（NULL）。最后，我们可以观察到传输体载荷试图发送GET请求（第75行）。

感谢Meterpreter生成的调试信息，现在我们已经接近事实的真相。看起来程序中负责处理Windows代理的代码片段没有被正确实现。为了解决这个问题，我们需要对代码进行分析、修改以及测试。

我需要重复多次编译Meterpreter的C工程文件，将生成的metsrv
DLL拷贝到攻击者主机中，使用受害者主机进行测试，这个过程非常耗时。因此我决定使用Python语言，复制C文件中与代理有关的处理代码，这样一来整个处理过程会更加轻松（感谢Python
ctypes库的强大功能）。

提取“server_transport_winhttp.c”源代码中与Meterpreter的代理处理逻辑有关的代码，将其转换为Python语言，如下所示：

    
    
    import ctypes
    import ctypes.wintypes
    import sys
    class WINHTTP_CURRENT_USER_IE_PROXY_CONFIG(ctypes.Structure):
    _fields_ = [("fAutoDetect", ctypes.wintypes.BOOL),
    ("lpszAutoConfigUrl", ctypes.wintypes.LPWSTR),
    ("lpszProxy", ctypes.wintypes.LPWSTR),
    ("lpszProxyBypass", ctypes.wintypes.LPWSTR)]
    class WINHTTP_AUTOPROXY_OPTIONS(ctypes.Structure):
    _fields_ = [("dwFlags", ctypes.wintypes.DWORD),
    ("dwAutoDetectFlags", ctypes.wintypes.DWORD),
    ("lpszAutoConfigUrl", ctypes.wintypes.LPCWSTR),
    ("lpvReserved", ctypes.c_void_p),
    ("dwReserved", ctypes.wintypes.DWORD),
    ("fAutoLogonIfChallenged", ctypes.wintypes.BOOL)]
    class WINHTTP_PROXY_INFO(ctypes.Structure):
    _fields_ = [("dwAccessType", ctypes.wintypes.DWORD),
    ("lpszProxy", ctypes.wintypes.LPCWSTR),
    ("lpszProxyBypass", ctypes.wintypes.LPCWSTR)]
    # dwFlags values
    WINHTTP_AUTOPROXY_AUTO_DETECT = 0x00000001
    WINHTTP_AUTOPROXY_CONFIG_URL = 0x00000002
    # dwAutoDetectFlags values
    WINHTTP_AUTO_DETECT_TYPE_DHCP = 0x00000001
    WINHTTP_AUTO_DETECT_TYPE_DNS_A = 0x00000002
    # Parameters for WinHttpOpen
    WINHTTP_USER_AGENT = "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko"
    WINHTTP_ACCESS_TYPE_DEFAULT_PROXY = 0
    WINHTTP_NO_PROXY_NAME = 0
    WINHTTP_NO_PROXY_BYPASS = 0
    WINHTTP_FLAG_ASYNC = 0x10000000
    test_url = "http://www.google.com"
    # Gets the current user IE proxy configuration
    ieConfig = WINHTTP_CURRENT_USER_IE_PROXY_CONFIG()
    result = ctypes.windll.winhttp.WinHttpGetIEProxyConfigForCurrentUser(ctypes.byref(ieConfig))
    if not result:
    print "[-] Error on WinHttpGetIEProxyConfigForCurrentUser: %s" % ctypes.GetLastError()
    sys.exit()
    print "[+] Got IE configuration"
    print "tAutoDetect: %s" % ieConfig.fAutoDetect
    print "tAuto URL: %s" % ieConfig.lpszAutoConfigUrl
    print "tProxy: %s" % ieConfig.lpszProxy
    print "tProxy Bypass: %s" % ieConfig.lpszProxyBypass
    # We have three alternatives:
    #  1. The configuration is set to "auto detect" the proxy, that is, via DHCP or DNS (in that order)
    #  2. There is a URL for downloading the script with the configuration (proxy autoconfiguration, PAC)
    #  3. A manually configured proxy is being used
    if ieConfig.lpszAutoConfigUrl:
    autoProxyOpts = WINHTTP_AUTOPROXY_OPTIONS()
    proxyInfo = WINHTTP_PROXY_INFO()
    print "[+] IE config set to autodetect with URL %s" % ieConfig.lpszAutoConfigUrl
    autoProxyOpts.dwFlags = WINHTTP_AUTOPROXY_AUTO_DETECT | WINHTTP_AUTOPROXY_CONFIG_URL
    autoProxyOpts.dwAutoDetectFlags = WINHTTP_AUTO_DETECT_TYPE_DHCP | WINHTTP_AUTO_DETECT_TYPE_DNS_A
    autoProxyOpts.fAutoLogonIfChallenged = True
    autoProxyOpts.lpszAutoConfigUrl = ieConfig.lpszAutoConfigUrl
    hInternet = ctypes.windll.winhttp.WinHttpOpen(WINHTTP_USER_AGENT, WINHTTP_ACCESS_TYPE_DEFAULT_PROXY, WINHTTP_NO_PROXY_NAME, WINHTTP_NO_PROXY_BYPASS, WINHTTP_FLAG_ASYNC)        
    if not hInternet:
    print "[-] Error on WinHttpOpen: %s" % ctypes.GetLastError()
    sys.exit()
    result = ctypes.windll.winhttp.WinHttpGetProxyForUrl(hInternet, unicode(test_url), ctypes.byref(autoProxyOpts), ctypes.byref(proxyInfo))
    if not result:
    print "[-] Error on WinHttpGetProxyForUrl: %s" % ctypes.GetLastError()
    sys.exit()
    print "[+] Proxy Host: %s" % proxyInfo.lpszProxy
    elif ieConfig.lpszProxy:
    print "[+] IE config set to proxy %s with bypass %s" % (ieConfig.lpszProxy, ieConfig.lpszProxyBypass)

这一段脚本程序在受害者主机上的执行结果如下图所示：

从脚本的输出信息中，我们可知Python程序的执行结果与C版本的一致。程序检测到代理的自动配置选项，但没有获取到代理地址。

如果我们再次检查代码，我们会发现，程序在某个“if”代码块内判断是否可能使用DHCP以及DNS获取代理信息，如果自动配置URL（ieConfig.lpszAutoConfigUrl）的条件为真就会执行这个代码块。然而，如果仅仅启用了AutoDetect选项，这部分代码并不会被执行，而这正是受害者主机上发生的情况。

在这个特定场景中（受害者主机所处的环境），代理的配置信息需要通过DHCP的252选项获取。

受害者主机上嗅探的DHCP传输数据包如下图所示：

从这个传输数据包中我们可以看出，DHCP服务器的应答中包含252选项（“Private/Proxy
autodiscovery”，私有选项，用于代理的自动发现），包含代理的URL地址。这正是我们在运行autoprox.exe工具时获得的信息。

在继续分析之前，我们需要了解Windows为代理配置提供的三种选项：

1、自动检测代理设置：使用DHCP（252选项）获取代理URL地址，或者使用DNS、LLMNR、NBNS（如果启用的话）获取WPAD主机名；

2、使用自动配置脚本：从某个URL下载配置脚本，通过这个脚本决定何时使用代理服务器；

3、手动设置代理服务器：为不同的协议手动配置代理服务器。

关于这个问题的根本原因，现在我们又掌握了更多的信息，我会稍微修改程序代码，将代理自动检测的可能性考虑在内。让我们先修改Python代码，如果代码工作正常，我们就可以修改Meterpreter的C语言代码，然后再编译生成Meterpreter载荷。

修改后的Python代码如下所示：

    
    
    import ctypes
    import ctypes.wintypes
    import sys
    class WINHTTP_CURRENT_USER_IE_PROXY_CONFIG(ctypes.Structure):
        _fields_ = [("fAutoDetect", ctypes.wintypes.BOOL),
                    ("lpszAutoConfigUrl", ctypes.wintypes.LPWSTR),
                    ("lpszProxy", ctypes.wintypes.LPWSTR),
                    ("lpszProxyBypass", ctypes.wintypes.LPWSTR)]
    class WINHTTP_AUTOPROXY_OPTIONS(ctypes.Structure):
        _fields_ = [("dwFlags", ctypes.wintypes.DWORD),
                    ("dwAutoDetectFlags", ctypes.wintypes.DWORD),
                    ("lpszAutoConfigUrl", ctypes.wintypes.LPCWSTR),
                    ("lpvReserved", ctypes.c_void_p),
                    ("dwReserved", ctypes.wintypes.DWORD),
                    ("fAutoLogonIfChallenged", ctypes.wintypes.BOOL)]
    class WINHTTP_PROXY_INFO(ctypes.Structure):
        _fields_ = [("dwAccessType", ctypes.wintypes.DWORD),
                    ("lpszProxy", ctypes.wintypes.LPCWSTR),
                    ("lpszProxyBypass", ctypes.wintypes.LPCWSTR)]
    # dwFlags values
    WINHTTP_AUTOPROXY_AUTO_DETECT = 0x00000001
    WINHTTP_AUTOPROXY_CONFIG_URL = 0x00000002
    # dwAutoDetectFlags values
    WINHTTP_AUTO_DETECT_TYPE_DHCP = 0x00000001
    WINHTTP_AUTO_DETECT_TYPE_DNS_A = 0x00000002
    # Parameters for WinHttpOpen
    WINHTTP_USER_AGENT = "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko"
    WINHTTP_ACCESS_TYPE_DEFAULT_PROXY = 0
    WINHTTP_NO_PROXY_NAME = 0
    WINHTTP_NO_PROXY_BYPASS = 0
    WINHTTP_FLAG_ASYNC = 0x10000000
    test_url = "http://www.google.com"
    # Gets the current user IE proxy configuration
    ieConfig = WINHTTP_CURRENT_USER_IE_PROXY_CONFIG()
    result = ctypes.windll.winhttp.WinHttpGetIEProxyConfigForCurrentUser(ctypes.byref(ieConfig))
    if not result:
        print "[-] Error on WinHttpGetIEProxyConfigForCurrentUser: %s" % ctypes.GetLastError()
        sys.exit()
    print "[+] Got IE configuration"
    print "tAutoDetect: %s" % ieConfig.fAutoDetect
    print "tAuto URL: %s" % ieConfig.lpszAutoConfigUrl
    print "tProxy: %s" % ieConfig.lpszProxy
    print "tProxy Bypass: %s" % ieConfig.lpszProxyBypass
    # We have three alternatives:
    #  1. The configuration is to "auto detect" the proxy, that is, via DHCP or DNS
    #  2. There is a URL for the script with the configuratoin (proxy autoconfiguration, PAC)
    #  3. A manually configured proxy is being used
    if ieConfig.lpszAutoConfigUrl or ieConfig.fAutoDetect:
        autoProxyOpts = WINHTTP_AUTOPROXY_OPTIONS()
        proxyInfo = WINHTTP_PROXY_INFO()
        if ieConfig.lpszAutoConfigUrl:
            print "[+] IE config set to autodetect with URL %s" % ieConfig.lpszAutoConfigUrl
            autoProxyOpts.dwFlags = WINHTTP_AUTOPROXY_CONFIG_URL
            autoProxyOpts.dwAutoDetectFlags = 0
            autoProxyOpts.lpszAutoConfigUrl = ieConfig.lpszAutoConfigUrl
        if ieConfig.fAutoDetect:
            print "[+] IE config set to autodetect via DHCP or DNS"
            autoProxyOpts.dwFlags = WINHTTP_AUTOPROXY_AUTO_DETECT
            autoProxyOpts.dwAutoDetectFlags = WINHTTP_AUTO_DETECT_TYPE_DHCP | WINHTTP_AUTO_DETECT_TYPE_DNS_A
            autoProxyOpts.lpszAutoConfigUrl = 0
        autoProxyOpts.fAutoLogonIfChallenged = True
        hInternet = ctypes.windll.winhttp.WinHttpOpen(WINHTTP_USER_AGENT,  WINHTTP_ACCESS_TYPE_DEFAULT_PROXY, WINHTTP_NO_PROXY_NAME, WINHTTP_NO_PROXY_BYPASS, WINHTTP_FLAG_ASYNC)        
        if not hInternet:
            print "[-] Error on WinHttpOpen: %s" % ctypes.GetLastError()
            sys.exit()
        result = ctypes.windll.winhttp.WinHttpGetProxyForUrl(hInternet, unicode(test_url), ctypes.byref(autoProxyOpts), ctypes.byref(proxyInfo))
        if not result:
            print "[-] Error on WinHttpGetProxyForUrl: %s" % ctypes.GetLastError()
            sys.exit()
        print "[+] Proxy Host: %s" % proxyInfo.lpszProxy
    elif ieConfig.lpszProxy:
        print "[+] IE config set to proxy %s with bypass %s" % (ieConfig.lpszProxy, ieConfig.lpszProxyBypass)

修改后的代码考虑到了通过DHCP/DNS获取代理的可能性。现在我们可以运行这段代码，观察代码的执行结果。

修改后的Python代码在受害者主机上的执行结果如下图所示：

从上图可知，程序成功通过DHCP获取了代理信息，代理信息与本文开头给出的信息一致（即10.x.x.20）。

Python版的代码工作正常，我们可以更新Meterpreter的C版代码（server_transport_winhttp.c），测试我们的后门程序能否正常运行。

修改后的Meterpreter源代码如下所示：

    
    
    ...
    dprintf("[PROXY] Got IE configuration");
    dprintf("[PROXY] AutoDetect: %s", ieConfig.fAutoDetect ? "yes" : "no");
    dprintf("[PROXY] Auto URL: %S", ieConfig.lpszAutoConfigUrl);
    dprintf("[PROXY] Proxy: %S", ieConfig.lpszProxy);
    dprintf("[PROXY] Proxy Bypass: %S", ieConfig.lpszProxyBypass);
    if (ieConfig.lpszAutoConfigUrl || ieConfig.fAutoDetect)
    {
    WINHTTP_AUTOPROXY_OPTIONS autoProxyOpts = { 0 };
    WINHTTP_PROXY_INFO proxyInfo = { 0 }; 
    if (ieConfig.fAutoDetect)
    {
    dprintf("[PROXY] IE config set to autodetect via DHCP or DNS");
    autoProxyOpts.dwFlags = WINHTTP_AUTOPROXY_AUTO_DETECT;
    autoProxyOpts.dwAutoDetectFlags = WINHTTP_AUTO_DETECT_TYPE_DHCP | WINHTTP_AUTO_DETECT_TYPE_DNS_A;
    autoProxyOpts.lpszAutoConfigUrl = 0;
    }
    else if (ieConfig.lpszAutoConfigUrl)
    {
    dprintf("[PROXY] IE config set to autodetect with URL %S", ieConfig.lpszAutoConfigUrl);
    autoProxyOpts.dwFlags = WINHTTP_AUTOPROXY_CONFIG_URL;
    autoProxyOpts.dwAutoDetectFlags = 0;
    autoProxyOpts.lpszAutoConfigUrl = ieConfig.lpszAutoConfigUrl;
    }
    autoProxyOpts.fAutoLogonIfChallenged = TRUE;
       if (WinHttpGetProxyForUrl(ctx->internet, ctx->url, &autoProxyOpts, &proxyInfo))
    ...

代码修改完毕后，我们重新编译工程文件，将生成的metsrv Meterpreter DLL文件拷贝到监听端主机上，再次运行监听端，等待客户端连接。

监听端在攻击者主机上的运行情况如下图所示：

从上图可知，当受害者主机使用“自动探测”代理选项时（本例中使用的是DHCP的252选项），我们能够成功建立Meterpreter会话。

  

**三、分析问题的根本原因**

文章阅读至此，现在是时候讨论以下这些问题了：

1、为什么最开始时，传输器载荷能够到达攻击者主机？

2、传输器载荷与传输体载荷在通信上有什么区别？

为了找到这些问题的答案，我们首先需要理解Meterpreter（在本文撰写时）的工作机制。

Windows
API提供了两种方式（或接口）与HTTP(s)进行交互：WinInet以及WinHTTP。对于Meterpreter而言，我们需要关注它在处理HTTPs通信时的两个功能：

1、Meterpreter可以验证HTTPs服务器（即运行在攻击者主机上的Metasploit监听端）所提供的证书签名，避免代理设备（如L7网络防火墙）检查其通信内容。

2、Meterpreter可以透明地使用当前用户的代理设置，通过互联网访问监听端。

这两个功能无法同时在同一个Windows API中找到，具体如下：

**WinInet：**

1、可以透明感知代理。也就是说，如果当前用户系统的代理设置适用于Internet
Explorer浏览器，那么这个设置对使用WinInet的程序来说同样适用。

2、不支持SSL/TLS证书的自定义验证。

**WinHTTP：**

1、允许自定义验证服务器所提供的SSL证书。

2、不能透明地使用当前用户的系统代理设置。

现在，对于Meterpreter而言，我们可以使用两种不同的传输器载荷：

1、Meterpreter的reverse_https载荷。该载荷使用的是WinInet这个Windows
API，这意味着它不能验证服务器证书，但可以透明地使用系统代理。也就是说，如果用户可以通过IE浏览器访问互联网，那么这个传输器载荷也可以。

2、Meterpreter的reverse_winhttps载荷。该载荷使用的是WinHTTP这个Windows
API，这意味着它可以验证服务器证书，但必须手动设置代理信息才能访问互联网。

对Meterpreter传输体载荷来说，默认情况下它使用的是WinHTTP Windows API，如果出现问题则会切换为使用WinInet
API（读者可以阅读官方文档，查看旧版本中如何判断代理是否存在问题）。这种切换是自动发生的，除非用户决定使用“paranoid”（偏执）模式，这种模式优先级较高。

请注意：对于Meterpreter而言，使用“paranoid”模式意味着SSL/TLS证书签名必须被验证，如果证书签名被替换（比如，Palo
Alto网络防火墙会替换证书以检查通信内容），那么传输体载荷就不会被下载，当然会话也无法成功建立。如果用户确实需要使用“paranoid”模式，那么传输器载荷就必须使用WinHTTP这个Windows
API。

现在对于这个问题，我们已经掌握了必要的背景知识。之前我使用的是“reverse_https”
Meterpreter载荷（出于测试目的，没有使用“paranoid”模式），这意味着传输器载荷使用的是WinInet
API来访问监听端，也就是说它透明地使用了当前用户的代理设置，可以正常工作。然而，Meterpreter传输体载荷默认使用的是WinHTTP
API，根据我们前面的分析结论，这个载荷在处理代理时有个bug，因此无法回连到攻击者主机上的监听端。我想这足以回答我们前面提出来的两个问题。

  

**四、代理识别方法**

我们并没有回答另外一个问题，那就是：在使用WinHTTP Windows API时，获取当前用户代理设置的最佳方法是什么？

为了回答这个问题，我们需要探索系统在处理代理时的优先级。当系统中配置了多个代理的情况下，如果某个代理无法正常工作，Windows如何处理这种情况（即Windows是否会尝试另一个代理选项）。

根据我的研究结论，代理设置的优先级与Internet选项中设置的代理顺序一致。也就是说，系统首先会检查“自动检测设置”选项是否已设置，然后再检查“使用自动配置脚本”选项是否已设置，最后再检查“为LAN使用代理服务器”选项是否设置。

此外，我们可以在微软MSDN的“开发者代码示例”中，找到使用WinHTTP API的示例代码，其中关于代理的优先级，有这样一段说明：

    
    
    // WinHTTP API会按照以下顺序检测代理： 
     // 1) 自动检测
    // 2) 自动配置的URL
    // 3) 静态配置的代理

这个说明跟我们前面提到的代理优先级一样。

  

**五、容错机制**

前面我们提到的问题是，假设当前主机配置了多个代理选项，如果某个优先选项失效了，结果会如何？Windows是否会按照优先级继续尝试下一选项，直到找到一个可用的代理？

为了回答这个问题，我们可以做个简单的实验，或者花无数个小时，逆向分析与代理有关的Windows组件（主要是wininet.dll）。我们可以先尝试做个实验，至少这个过程花费的时间没那么多。

**5.1 实验环境**

为了进一步分析Windows的代理设置及功能，我创建了如下的实验环境：

使用1台域控的Windows域环境：

1、域：lab.bransh.com

2、域控IP：192.168.0.1

3、DHCP地址范围：192.168.0.100–150

3个微软Forefront TMG（Thread Management Gateway）服务器：

1、tmg1.lab.bransh.com：192.168.0.10

2、tmg2.lab.bransh.com：192.168.0.11

3、tmg3.lab.bransh.com：192.168.0.12

每个TMG服务器都有两个网络接口：“内部（internal）”接口（地址范围为192.168.0.x）连接到域中，客户端可以通过这个接口访问互联网。“外部（external）”接口连接到另一个网络，代理使用这个接口直接访问互联网。

1台Windows主机（Windows 8.1 x64）：

1、通过DHCP获取IP地址

2、代理设置情况：

（1）通过DHCP获取的代理（252选项）：tmg1.lab.bransh.com

（2）通过脚本配置的代理：http://tmg2.lab.bransh.com/wpad.dat

（3）手动设置的代理：tmg3.lab.bransh.com:8080

3、Windows主机无法直接访问互联网

4、Firefox浏览器设置为使用系统代理

Windows主机的代理设置情况如下图所示：

通过DHCP（252选项）获取的代理信息如下图所示：

请注意：“自动检测设置”选项可以通过DHCP或DNS获取代理信息。我们在使用Windows API时，可以指定使用哪种（或者同时使用两种）方式获取代理信息。

我们可以编写一段简单的代码，使用Windows提供的API，测试几种代理场景。我先写了一段Python代码，因为这样我可以更加简单地修改和运行代码，而不需要像C/C++代码那样每次修改后都需要重新编译。读者可以根据自己的喜好选择喜欢的语言完成这一任务。

Python代码如下：

    
    
    import ctypes
    import ctypes.wintypes
    import sys
    class WINHTTP_CURRENT_USER_IE_PROXY_CONFIG(ctypes.Structure):
        _fields_ = [("fAutoDetect", ctypes.wintypes.BOOL),
                    ("lpszAutoConfigUrl", ctypes.wintypes.LPWSTR),
                    ("lpszProxy", ctypes.wintypes.LPWSTR),
                    ("lpszProxyBypass", ctypes.wintypes.LPWSTR)]
    class WINHTTP_AUTOPROXY_OPTIONS(ctypes.Structure):
        _fields_ = [("dwFlags", ctypes.wintypes.DWORD),
                    ("dwAutoDetectFlags", ctypes.wintypes.DWORD),
                    ("lpszAutoConfigUrl", ctypes.wintypes.LPCWSTR),
                    ("lpvReserved", ctypes.c_void_p),
                    ("dwReserved", ctypes.wintypes.DWORD),
                    ("fAutoLogonIfChallenged", ctypes.wintypes.BOOL)]
    class WINHTTP_PROXY_INFO(ctypes.Structure):
        _fields_ = [("dwAccessType", ctypes.wintypes.DWORD),
                    ("lpszProxy", ctypes.wintypes.LPCWSTR),
                    ("lpszProxyBypass", ctypes.wintypes.LPCWSTR)]
    WINHTTP_USER_AGENT = ctypes.c_wchar_p('Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko')
    WINHTTP_ACCESS_TYPE_DEFAULT_PROXY = 0
    WINHTTP_ACCESS_TYPE_NO_PROXY = 1
    WINHTTP_ACCESS_TYPE_NAMED_PROXY = 3
    WINHTTP_NO_PROXY_NAME = 0
    WINHTTP_NO_PROXY_BYPASS = 0
    def ShowLastError(message, alignment = 0):
        error_id = ctypes.GetLastError()
        print ' ' * alignment + '[-] Error on %s: %s' % (message, error_id)
        if error_id == 12167:
            title = 'ERROR_WINHTTP_UNABLE_TO_DOWNLOAD_SCRIPT'
            message = 'The PAC file cannot be downloaded. For example, the server referenced by the PAC URL may not have been reachable, or the server returned a 404 NOT FOUND response.'
        elif error_id == 12007:
            title = 'ERROR_WINHTTP_NAME_NOT_RESOLVED'
            message = 'The server name cannot be resolved.'
        elif error_id == 12029:
            title = 'ERROR_WINHTTP_CANNOT_CONNECT'
            message = 'Returned if connection to the server failed.'
        elif error_id == 12002:
            title = 'ERROR_WINHTTP_TIMEOUT'
            message = 'The request has timed out.'
        elif error_id == 12180:
            title = 'ERROR_WINHTTP_AUTODETECTION_FAILED'
            message = 'Returned by WinHttpDetectAutoProxyConfigUrl if WinHTTP was unable to discover the URL of the Proxy Auto-Configuration (PAC) file.'
        else:
            title = 'UNKNOWN'
            message = 'unknown'
        msg_max_len = 70
        msg_list = [message[i:i+msg_max_len] for i in range(0, len(message), msg_max_len)]
        print ' ' * alignment + '    => %s' % title
        for msg in msg_list:
            print ' ' * alignment + '       %s' % msg
    def GetCurrentProxies():
        pProxyConfig = WINHTTP_CURRENT_USER_IE_PROXY_CONFIG()
        result = ctypes.windll.winhttp.WinHttpGetIEProxyConfigForCurrentUser(ctypes.byref(pProxyConfig))
        if result == False:
            ShowLastError('WinHttpGetIEProxyConfigForCurrentUser')
            return False, None
        return True, pProxyConfig
    def GetProxyInfoList(pProxyConfig, target_url):
        print 'n[*] Checking proxy configuration alternatives...'
        proxy_list = []
        hSession = ctypes.windll.winhttp.WinHttpOpen(WINHTTP_USER_AGENT,  WINHTTP_ACCESS_TYPE_NO_PROXY, WINHTTP_NO_PROXY_NAME, WINHTTP_NO_PROXY_BYPASS, 0)
        if hSession is None:
            ShowLastError('WinHttpOpen')
            sys.exit()
        WINHTTP_AUTOPROXY_AUTO_DETECT = 0x00000001
        WINHTTP_AUTO_DETECT_TYPE_DHCP = 0x00000001
        WINHTTP_AUTO_DETECT_TYPE_DNS_A = 0x00000002
        WINHTTP_AUTOPROXY_CONFIG_URL = 0x00000002
        if pProxyConfig.fAutoDetect:
            print 'n  (1) Automatically detect settings (enabled)'
            print '      [*] Trying to get the proxy using the conventional method...'
            pAutoProxyOptions = WINHTTP_AUTOPROXY_OPTIONS()
            pProxyInfo = WINHTTP_PROXY_INFO()
            pAutoProxyOptions.dwFlags = WINHTTP_AUTOPROXY_AUTO_DETECT
            pAutoProxyOptions.dwAutoDetectFlags = WINHTTP_AUTO_DETECT_TYPE_DHCP | WINHTTP_AUTO_DETECT_TYPE_DNS_A
            pAutoProxyOptions.lpszAutoConfigUrl = 0
            lpcwszUrl = ctypes.wintypes.LPCWSTR(target_url)
            result = ctypes.windll.winhttp.WinHttpGetProxyForUrl(hSession, lpcwszUrl, ctypes.byref(pAutoProxyOptions), ctypes.byref(pProxyInfo))
            if result == False:
                ShowLastError('WinHttpGetProxyForUrl', 6)
                print 'n      [*] Trying to get the proxy using the AutoConfigURL...'
                dwAutoDetectFlags = WINHTTP_AUTO_DETECT_TYPE_DHCP | WINHTTP_AUTO_DETECT_TYPE_DNS_A
                ppwszAutoConfigUrl = ctypes.wintypes.LPWSTR()
                result = ctypes.windll.winhttp.WinHttpDetectAutoProxyConfigUrl(dwAutoDetectFlags, ctypes.byref(ppwszAutoConfigUrl))
                if result == False:
                    ShowLastError('WinHttpDetectAutoProxyConfigUrl', 10)
                else:
                    print '      [+] Trying to get the proxy from the obtained URL (%s)' % ppwszAutoConfigUrl.value
                    pAutoProxyOptions.dwFlags = WINHTTP_AUTOPROXY_CONFIG_URL
                    pAutoProxyOptions.dwAutoDetectFlags = 0
                    pAutoProxyOptions.fAutoLogonIfChallenged = True
                    pAutoProxyOptions.lpszAutoConfigUrl = ppwszAutoConfigUrl
                    result = ctypes.windll.winhttp.WinHttpGetProxyForUrl(hSession, lpcwszUrl, ctypes.byref(pAutoProxyOptions), ctypes.byref(pProxyInfo))
                    if result:
                        print '      [+] Proxy: %s' % (pProxyInfo.lpszProxy)
                        proxy_list.append(pProxyInfo)
                    else:
                        ShowLastError('WinHttpGetProxyForUrl', 10)
            else:
                print '      [+] Proxy: %s' % (pProxyInfo.lpszProxy)
                proxy_list.append(pProxyInfo)
        if pProxyConfig.lpszAutoConfigUrl:
            print 'n  (2) Use automatic configuration script (%s)' % pProxyConfig.lpszAutoConfigUrl
            pAutoProxyOptions = WINHTTP_AUTOPROXY_OPTIONS()
            pProxyInfo = WINHTTP_PROXY_INFO()
            pAutoProxyOptions.dwFlags = WINHTTP_AUTOPROXY_CONFIG_URL
            pAutoProxyOptions.dwAutoDetectFlags = 0
            pAutoProxyOptions.fAutoLogonIfChallenged = True
            pAutoProxyOptions.lpszAutoConfigUrl = pProxyConfig.lpszAutoConfigUrl
            lpcwszUrl = ctypes.wintypes.LPCWSTR(target_url)
            result = ctypes.windll.winhttp.WinHttpGetProxyForUrl(hSession, lpcwszUrl, ctypes.byref(pAutoProxyOptions), ctypes.byref(pProxyInfo))
            if result == False:
                ShowLastError('WinHttpGetProxyForUrl', 6)
            else:
                print '      [+] Proxy: %s' % (pProxyInfo.lpszProxy)
                proxy_list.append(pProxyInfo)
        if pProxyConfig.lpszProxy:
            print 'n  (3) Use a proxy server for your LAN'
            pProxyInfo = WINHTTP_PROXY_INFO()
            WINHTTP_ACCESS_TYPE_NAMED_PROXY = 3
            pProxyInfo.dwAccessType = WINHTTP_ACCESS_TYPE_NAMED_PROXY
            pProxyInfo.lpszProxy = pProxyConfig.lpszProxy
            pProxyInfo.lpszProxyBypass = pProxyConfig.lpszProxyBypass
            print '      [+] Proxy: %s' % pProxyConfig.lpszProxy
            print '      [+] Proxy Bypass: %s' % pProxyConfig.lpszProxyBypass
            proxy_list.append(pProxyInfo)
        ctypes.windll.winhttp.WinHttpCloseHandle(hSession)
        return proxy_list
    def CheckProxyStatus(proxyInfo, target_server, target_port):
        hSession = ctypes.windll.winhttp.WinHttpOpen(WINHTTP_USER_AGENT,  WINHTTP_ACCESS_TYPE_DEFAULT_PROXY, WINHTTP_NO_PROXY_NAME, WINHTTP_NO_PROXY_BYPASS, 0)
        if hSession is None:
            ShowLastError('WinHttpOpen')
            return
        server_name = ctypes.c_wchar_p(target_server)
        INTERNET_DEFAULT_HTTP_PORT = target_port
        hInternet = ctypes.windll.winhttp.WinHttpConnect(hSession, server_name, INTERNET_DEFAULT_HTTP_PORT, 0)
        if hInternet is None:
            ShowLastError('WinHttpConnect', 8)
            return False
        WINHTTP_FLAG_BYPASS_PROXY_CACHE = 0x00000100
        WINHTTP_FLAG_SECURE = 0x00800000
        dwFlags = WINHTTP_FLAG_BYPASS_PROXY_CACHE
        pwszVerb = ctypes.c_wchar_p('GET')
        pwszObjectName = ctypes.c_wchar_p('')
        hRequest = ctypes.windll.winhttp.WinHttpOpenRequest(hInternet, pwszVerb, pwszObjectName, 0, 0, 0, dwFlags)
        if hRequest is None:
            ShowLastError('WinHttpOpenRequest', 8)
            return False
        WINHTTP_OPTION_PROXY = 38
        result = ctypes.windll.winhttp.WinHttpSetOption(hRequest, WINHTTP_OPTION_PROXY, ctypes.byref(proxyInfo), ctypes.sizeof(proxyInfo))
        if result == False:
            ShowLastError('WinHttpSetOption', 8)
            return False
        WINHTTP_NO_ADDITIONAL_HEADERS = 0
        WINHTTP_NO_REQUEST_DATA = 0
        result = ctypes.windll.winhttp.WinHttpSendRequest(hRequest, WINHTTP_NO_ADDITIONAL_HEADERS, 0, WINHTTP_NO_REQUEST_DATA, 0, 0, 0)
        if result == False:
            ShowLastError('WinHttpSendRequest', 8)
            return False
        else:
            WINHTTP_QUERY_STATUS_CODE = 19
            WINHTTP_QUERY_STATUS_TEXT = 20
            WINHTTP_QUERY_RAW_HEADERS_CRLF = 22
            WINHTTP_HEADER_NAME_BY_INDEX = 0
            WINHTTP_NO_HEADER_INDEX = 0
            dwInfoLevel = WINHTTP_QUERY_RAW_HEADERS_CRLF
            lpdwBufferLength = ctypes.wintypes.DWORD()
            lpdwIndex = ctypes.wintypes.DWORD()
            result = ctypes.windll.winhttp.WinHttpReceiveResponse(hRequest, 0)
            if result:
                result = ctypes.windll.winhttp.WinHttpQueryHeaders(hRequest, WINHTTP_QUERY_RAW_HEADERS_CRLF,
                                                                   WINHTTP_HEADER_NAME_BY_INDEX, 0,
                                                                   ctypes.byref(lpdwBufferLength),
                                                                   WINHTTP_NO_HEADER_INDEX)
                ERROR_INSUFFICIENT_BUFFER = 122
                if ctypes.GetLastError() == ERROR_INSUFFICIENT_BUFFER:
                    lpBuffer = ctypes.create_string_buffer(lpdwBufferLength.value)
                    result = ctypes.windll.winhttp.WinHttpQueryHeaders(hRequest, WINHTTP_QUERY_RAW_HEADERS_CRLF,
                                                                       WINHTTP_HEADER_NAME_BY_INDEX, ctypes.byref(lpBuffer),
                                                                       ctypes.byref(lpdwBufferLength),
                                                                       WINHTTP_NO_HEADER_INDEX)
                    if result:
                        line = lpBuffer.raw.replace('x00', '').split('n')[0]
                        space_1 = line.find(' ')
                        space_2 = line.find(' ', space_1+1)
                        code = line[space_1:space_2].strip()
                        text = line[space_2:].strip()
                        print "t[*] HTTP Query Status Code / Text: nt    %s / %s" % (code, text)
                        if code != "200":
                            return False
                        else:
                            return True
        ctypes.windll.winhttp.WinHttpCloseHandle(hRequest)
        ctypes.windll.winhttp.WinHttpCloseHandle(hInternet)
        ctypes.windll.winhttp.WinHttpCloseHandle(hSession)
        return True
    def main():
        result, pProxyConfig = GetCurrentProxies()
        if result == False:
            sys.exit()
        print 'n[*] We got the proxy configuration.'
        if pProxyConfig is None:
            print '[*] No proxy setting found for the current user.'
            sys.exit()
        target_server = 'www.google.com'
        target_url = 'http://' + target_server
        target_port = 80
        proxy_list = GetProxyInfoList(pProxyConfig, target_url)
        print 'n[*] Number of proxies: %s' % str(len(proxy_list))
        print 'n[*] Testing if proxy servers actually work...'
        for proxy in proxy_list:
            print 'n    [*] Proxy "%s" ... ' % proxy.lpszProxy
            result = CheckProxyStatus(proxy, target_server, target_port)
            if result:
                print '        [+] Works! :)'
            else:
                print '        [-] Does not work :('
    if __name__ == '__main__':
        main()

以上代码有两个重要函数：

1、GetProxyInfoList(pProxyConfig,
target_url)：这个函数会评估当前用户的代理设置，根据传入的URL地址，返回一个代理套接字（IP:PORT）列表。需要注意的是这个代理列表中包含具体的代理地址，我们有可能使用这些代理地址访问目标URL，但是这并不意味着代理服务器一定处于正常工作状态。比如，这个列表中可能包含从WPAD.DAT文件中读取的代理信息，这个WPAD.DAT文件为“使用自动配置脚本”选项中设置的脚本文件，但在访问目标URL时这个代理可能不起作用。

2、CheckProxyStatus(proxy, target_server,
target_port)：这个函数会使用给定的代理，访问目标服务器和端口（直接访问根目录），以测试代理是否实际可用。我们可以使用这个函数判断某个代理是否可用。

**5.2 测试场景 #1**

在这个测试场景中，代理服务器tmg1以及tmg2的内部网络接口（192.168.0.x）在客户机启动前已被禁用。这意味着客户机只能通过代理服务器TMG3访问互联网。

脚本程序的输出结果如下所示。此外，我们还可以从输出结果中看到IE和Firefox浏览器如何处理这种场景：

从测试程序的输出结果中我们可知以下信息：

1、“自动检测设置”选项已启用，获取的代理为“192.168.0.10:8080”（Windows会在后台下载WPAD.PAC文件，同时在代理服务器内部接口被禁用前缓存已获取的代理信息）。然而，这个代理并不能正常工作，因为TMG1的内部接口已被禁用，客户机不可能通过网络访问到这个接口（会出现访问超时情况）。

2、“使用自动配置脚本”选项已启用，获取的代理为“192.168.0.11:8080”（Windows会在后台下载WPAD.PAC文件，同时在代理服务器内部接口被禁用前缓存已获取的代理信息）。然而这个代理依然不能正常工作，因为TMG2的内部接口已被禁用，客户机不可能通过网络访问到这个接口（会出现访问超时情况）。

3、手动配置的代理服务器为“tmg3.lab.bransh.com:8080”。这个代理可以正常使用，客户机可以通过它发送请求。

同时我们还知道，在当前的代理环境下，不管是IE还是Firefox浏览器都不能访问互联网。然而，使用tmg3作为代理服务器的自定义应用程序可以成功访问互联网。

**5.3 测试场景 #2**

这个场景与测试场景#1非常类似，代理服务器tmg1和tmg2的内部网络接口（192.168.0.x）在客户机启动前已被禁用。这意味着客户机只能通过代理服务器TMG3访问互联网。

脚本程序的输出结果如下图所示。此外，我们还可以从输出结果中看到IE和Firefox浏览器如何处理这种场景：

从测试程序的输出结果中我们可知以下信息：

1、“自动检测设置”选项已启用（tmg1.lab.bransh.com/wpad.dat），但没有获取到任何一个代理信息。之所以出现这种情况，原因在于当客户机收到DHCP配置信息（252选项）时，代理服务器（tmg1）并不可达，因此客户机无法下载wpad.dat代理配置文件。

2、“使用自动配置脚本”选项已启用，配置文件所使用的URL地址为“tmg2.lab.bransh.com/wpad.dat”。然而客户机无法下载配置脚本，因为代理服务器此时并不可达。

3、手动配置的代理服务器为“tmg3.lab.bransh.com:8080”。这个代理可以正常使用，客户机可以通过它发送请求。

同时我们还知道，在当前的代理环境下，IE浏览器能够正确识别代理信息，访问互联网，然而Firefox浏览器却不能做到这一点。

**5.4 测试场景 #3**

在这个场景中，代理服务器TMG2的内部网络接口（192.168.0.11）在客户机启动前已被禁用。这意味着客户机可以通过代理服务器TMG1和TMG3代理服务器访问互联网。

脚本程序的输出结果如下图所示。此外，我们还可以从输出结果中看到IE和Firefox浏览器如何处理这种场景：

从测试程序的输出结果中我们可知以下信息：

1、“自动检测设置”选项已启用，客户机可以使用已获取的代理信息（192.168.0.10:8080）访问互联网。

2、“使用自动配置脚本”选项已启用，配置文件所使用的URL地址为“tmg2.lab.bransh.com/wpad.dat”。然而由于这个代理服务器的网络接口已被禁用，客户机无法下载配置脚本。

3、手动配置的代理服务器为“tmg3.lab.bransh.com:8080”。这个代理可以正常使用，客户机可以通过它发送请求。

同时我们还知道，在当前的代理环境下，IE浏览器能够正确识别代理信息，访问互联网，然而Firefox浏览器却不能做到这一点。

**5.5 测试场景 #4**

在这个场景中，只有TMG2代理服务器的内部网络接口（192.168.0.11）处于启用状态：

从测试程序的输出结果中我们可知以下信息：

1、“自动检测设置”选项已启用，客户机无法通过这个代理（192.168.0.10:8080）访问互联网。

2、“使用自动配置脚本”选项已启用，配置文件所使用的URL地址为“tmg2.lab.bransh.com/wpad.dat”。此外，获取到的代理地址为“192.168.0.11:8080”，客户机可以通过这个代理访问互联网。

3、手动配置的代理服务器为“tmg3.lab.bransh.com:8080”。这个代理可以正常使用，客户机可以通过它发送请求。

同时我们还知道，在当前的代理环境下，IE浏览器不能识别代理信息，无法访问互联网。然而Firefox成功获取了代理配置信息，能够正常访问互联网。

**5.6 测试场景 #5**

在这个场景中，所有三个代理服务器的内部网络接口全部处于启用状态。然而，TMG1和TMG2服务器的外部接口处于禁用状态：

从测试程序的输出结果中我们可知以下信息：

1、“自动检测设置”选项已启用，对应的代理服务器（192.168.0.10:8080）也可达。然而代理服务器返回了一个错误应答（502错误），表明客户机无法通过此代理服务器访问互联网。

2、“使用自动配置脚本”选项已启用，对应的代理服务器（192.168.0.11:8080）也可达。然而代理服务器返回了一个错误应答（502错误），表明客户机无法通过此代理服务器访问互联网。

3、手动配置的代理服务器为“tmg3.lab.bransh.com:8080”。这个代理可以正常使用，客户机可以通过它访问互联网。

在当前的代理环境下，IE和Firefox浏览器都不能访问互联网，然而使用TMG3作为代理服务器的自定义应用程序可以成功访问互联网。

  

**六、总结**

在某些场景下（比如本文第一部分描述的场景），我们会发现我们最喜爱的工具无法像预期那样正常工作。在这些情况下，我们主要有两种选择：尝试找到另一种解决方案，或者亲自上手修改工具，使其能正常工作。在本文所描述的企业网络场景中，我们修改了Meterpreter载荷源码，重新编译载荷Dll后，Meterpreter载荷能够在上文描述的代理环境中正常工作。我不确定我的这些修改是否会反馈到Meterpreter官方代码中，但如果你面临的是类似的场景，现在你应该知道该如何处理。

另一方面，我们知道Windows会按一定优先级顺序使用代理（如前文提到的优先级顺序）。然而，我们似乎发现，如果Windows已经获取了某个代理信息（如场景
#1给出的结果），即使这个代理无法正常工作，Windows也不会继续尝试使用另一个可用的代理选项。此外，我们发现在启用“使用系统代理设置”选项的条件下，IE和Firefox浏览器在查找代理时的表现也不尽相同。最后我们也发现，如果某个代理可达，但这个代理出于某些原因（比如互联网连接失败），无法提供互联网访问服务，此时这两个浏览器都不会尝试使用其他可能生效的代理服务器访问互联网。

考虑到这些测试结果，我们可以看到，我们的确可以使用某些API函数来评估所有的代理配置情况，甚至可以测试这些代理，以确认它们能否访问互联网资源。因此，我们只需要修改几行代码，就可以增加我们APT工具的鲁棒性，使其可以在这种网络环境下正常工作。然而，我必须承认，客户工作站存在多个代理的情况的确比较罕见，我不大相信管理员能够妥善处理这种混乱场面。另一方面，在连IE浏览器都不能正常工作的场景中，如果我们的APT工具还能正常工作的话，我不敢完全确定这是一个好主意。如果人们认为某个主机肯定不能访问互联网，但突然某一天，它开始通过可用的代理服务器访问互联网，这种情况对于蓝队来说可能比较奇怪。

最后总结一下，我认为如果我们的APT工具能够像IE浏览器那样健壮，那么它已经足以应付大多数情况。如果IE浏览器能够访问互联网，那么我们的APT工具也可以。

  

**七、参考资料**

[1] 自动代理：

<https://blogs.msdn.microsoft.com/askie/2014/02/07/optimizing-performance-with-automatic-proxyconfiguration-scripts-pac/>

[2] Windows Web代理配置：

<https://blogs.msdn.microsoft.com/ieinternals/2013/10/11/understanding-web-proxy-configuration/>

[3] 编译Meterpreter：

<https://github.com/rapid7/metasploit-payloads/tree/master/c/meterpreter>

[4] Meterpreter WinHTTP源代码：

<https://github.com/rapid7/metasploit-payloads/blob/master/c/meterpreter/source/server/win/server_transport_winhttp.c>

[5] Meterpreter common.h源代码：

<https://github.com/rapid7/metasploit-payloads/blob/master/c/meterpreter/source/common/common.h>

[6] Sysinternals DebugView：

<https://technet.microsoft.com/en-us/sysinternals/debugview.aspx>

[7] 对比WinHTTP与WinInet：

<https://github.com/rapid7/metasploit-framework/wiki/The-ins-and-outs-of-HTTP-and-HTTPS-communications-in-Meterpreter-and-Metasploit-Stagers>

[8] Metasploit bug反馈：

<https://github.com/rapid7/metasploit-payloads/issues/151>

[9] WinHTTP示例代码：

<http://code.msdn.microsoft.com/windowsdesktop/WinHTTP-proxy-sample-eea13d0c>

本文翻译自medium.com/@br4nsh [原文链接](https://medium.com/@br4nsh/a-meterpreter-and-windows-proxy-case-4af2b866f4a1)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86110](/post/id/86110)

安全客 - 有思想的安全新媒体

本文转载自: [medium.com/@br4nsh](https://medium.com/@br4nsh/a-meterpreter-and-windows-proxy-case-4af2b866f4a1)

如若转载,请注明出处： <https://medium.com/@br4nsh/a-meterpreter-and-windows-proxy-case-4af2b866f4a1>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

