# A-Journey-into-Synology-NAS-系列四-HTTP处理流程分析

阅读量 **275907**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-21 10:30:29

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0114a0d4fa50481a90.jpg)

## 前言

前面两篇文章从局域网的角度出发，对群晖`NAS`设备上开放的部分服务进行了分析。而在大部分情况下，群晖`NAS`设备是用于远程访问的场景中，即唯一的入口是通过`5000/http(5001/https)`进行访问(暂不考虑使用`QuickConnect`或其他代理的情形)。因此，本篇文章将主要对`HTTP`请求流程和处理机制进行分析，并分享在部分套件中发现的几个安全问题。

## HTTP请求处理流程

在正常登录过程中抓取的部分请求如下，可以看到请求`url`包含`query.cgi`、`login.cgi`和`entry.cgi`等。根据群晖的开发者手册可知，与设备进行交互的大概流程如下：

  1. 通过`query.cgi`获取`API`相关的信息；
  2. 通过`login.cgi`和`encryption.cgi`进行认证，获取`session id`；
  3. 通过`entry.cgi`发送请求、解析响应；
  4. 完成交互后登出。

![](https://p2.ssl.qhimg.com/t0136bddb2d9dfe55ec.png)

某个具体的请求示例如下，可以看到有点类似于`JSON-RPC`。对于大部分请求，其`url`均为`"/webapi/entry.cgi"`。在`POST`
`data`部分，`api`参数表示要请求的`API`名称，`method`表示要请求的`API`中的方法，`version`表示要请求的`API`版本。

![](https://p0.ssl.qhimg.com/t01812f762497399243.png)

针对`API`请求，群晖在后端采用`json`元数据文件`SYNO.***.***.lib`来定义与`API`相关的信息，示例如下。

    
    
    {
        "SYNO.Core.PersonalNotification.Event": {            // API名称
            "allowUser": [ "admin.local"],                    // 哪个组可以访问该API
            "appPriv": "",            
            "authLevel": 1,                                    // 是否需要认证 (0表示无需认证)
            "disableSocket": false,
            "lib": "lib/SYNO.Core.PersonalNotification.so",    // 处理具体请求的文件
            "maxVersion": 1,
            "methods": {                                    // API中支持的方法以及对应的版本
                "1": [{
                        "fire": {
                            "allowUser": [ "admin.local","normal.local" ],    // 覆盖上面的定义
                            "grantByUser": false,
                            "grantable": true }
                    }]
            },
            "minVersion": 1,
            "priority": 0,
            "socket": ""
        }
    }
    

根据上述信息，可以知道如何构造一个具体的请求来触发后端的某个处理程序。

整体的`HTTP`请求处理流程大概如下。首先，请求通过`5000`端口发送给设备，基于请求的`url`，`nginx`服务会将该请求分发给不同的`cgi`，如`query.cgi`、`login.cgi`和`entry.cgi`，其中，`entry.cgi`是大部分`POST`请求的端点。这些`cgi`会与另外两个服务`synocgid`和`synoscgi`进行通信，其中`synocgid`负责处理与`session`相关的事务，而`synoscgi`则负责分发具体的请求到最终的处理程序。

![](https://p1.ssl.qhimg.com/t01bc9f4363454eb8fb.png)

## 安全问题

在理解了`HTTP`请求流程和处理机制后，便可以对群晖`NAS`设备的功能模块进行分析。在群晖`NAS`设备上，主要包含两大攻击面：`DSM`操作系统本身和群晖提供的大量套件。下面结合具体的实例进行分析。

###  Diagnosis Tool

前面提到过，`Diagnosis Tool`是群晖提供的一个工具套件，支持抓包、调试等功能。该工具的界面和具体的抓包请求示例如下。

![](https://p3.ssl.qhimg.com/t010b4431407e84e436.png)

该请求由`packet_capture.cgi`程序进行处理，部分示例代码如下。在`handle_action_start()`中，获取请求中的参数后将其以`json`字符串的形式传给`tcpdump_wrapper`程序。

    
    
    __int64 __fastcall handle_action_start(__int64 a1, __int64 a2, const char *a3, const char *a4)
    {
      // ...
      Json::Value::Value((Json::Value *)&v39, (const std::string *)&v28);
      v17 = Json::Value::operator[](&v35, "output_dir");
      Json::Value::operator=(v17, &v39);
      Json::Value::~Value((Json::Value *)&v39);
      Json::Value::Value((Json::Value *)&v40, v4);
      v18 = Json::Value::operator[](&v35, "expression");
      Json::Value::operator=(v18, &v40);
      Json::Value::~Value((Json::Value *)&v40);
      Json::Value::Value((Json::Value *)&v41, v6);
      v19 = Json::Value::operator[](&v35, "interface");
      Json::Value::operator=(v19, &v41);
      Json::Value::~Value((Json::Value *)&v41);
      Json::FastWriter::write((Json::FastWriter *)&v33, (const Json::Value *)&v37);
      std::string::assign((std::string *)&v29, (const std::string *)&v33);
      // ...
      if (SLIBCExec("/var/packages/DiagnosisTool/target/bin/tcpdump_wrapper", "--params", v29, 0LL, 0LL) == -1 )
        // ...
    

在`tcpdump_wrapper`中，调用`sub_401F10()`解析得到`output_dir`、`expression`和`interface`参数，并传入`RunTcpDump()`，其最终调用`execve()`执行命令`tcpdump
-i <interface> -w <file> -C 10 -s 0 filter_expression`。

    
    
    __int64 __fastcall main(signed int a1, char **a2, char **a3)
    {
      if ( a1 > 1 )
      {
        // ...
        if ( v3 != 2 && !strcmp(v4[1], "--params") )
        {
          std::string::string(&v11, v4[2], &v6);
          // resolve parameters from json string
          sub_401F10(&v11, &output_dir, &expression,&interface);
          // ...
        }
      }
      if (sub_4019D0(&output_dir) )
      {
        if (sub_401900() && !RunTcpdump(&output_dir, &expression, &interface) )
        {
         // ...
    

调用`execve()`来执行命令，相对比较安全，避免了命令注入的问题，但其中的`filter_expression`参数是可控的。通过查看`tcpdump`命令的帮助文档，发现`-z`选项与`-C`或`-G`选项组合也可达到命令执行的目的。

![](https://p2.ssl.qhimg.com/t0104be8cb564e941c3.png)

针对`tcpdump -i <interface> -w <file> -C 10 -s 0
filter_expression`，其中已包含`-C`选项，因此通过伪造`filter_expression`参数为`-z<path to your
shell script>`，即通过注入命令选项，可实现命令执行的效果。

###  DS File

`DS
File`是群晖提供的一个移动应用程序，便于从移动设备上访问和管理`DiskStation`上的文件，使用该应用访问`DiskStation`的流程与通过`web`的流程类似。当尝试登录到`DiskStation`时，认证过程采用基于`PKI`的加密机制。而在某些情形下如目标`IP`输入错误，或者网络临时不可用，正常的请求会失败，`DS
File`会发送额外的请求。

![](https://p1.ssl.qhimg.com/t015a02824428a412fc.png)

通过查看对应的第`3`个请求发现，在请求头中包含经过`Base64`编码后的`Authorization`信息，相当于明文。

![](https://p0.ssl.qhimg.com/t0164203185d1ff282c.png)

因此，在一个不安全的网络环境中，当尝试通过`DS
File`应用访问`DiskStation`时，通过简单地丢弃或重定向对应的请求，”中间人’’可窃取用户的明文账号信息。

###  Synology Calendar

该套件是一个基于`Web`的应用程序，用于管理日常的事件和任务，其支持在事件中添加附件和分享日程等功能。其中，添加附件的功能支持从本地上传和从
`NAS`中上传两种方式。普通用户创建事件并添加附件的示例如下，同时给出了与附件链接相关的部分前端代码。

![](https://p1.ssl.qhimg.com/t015f7e3bb5f09358b3.png)

可以看到，上传文件的名称被拼接到`href`链接中。如果伪造一个文件名，能否控制对应的`href`链接呢？经过测试发现，由于未对文件名进行校验，通过伪造一个合适的文件名，可以更改对应的`href`链接，同时让显示的文件名称看起来正常。

![](https://p4.ssl.qhimg.com/t01c2f2dceccdc76124.png)

此外，借助日程分享功能，还可以将该事件分享到管理员组中。当管理员组中的某个人查看该事件并点击对应的附件之后，该请求就会被执行。因此，利用该漏洞，一个普通权限的用户可以以”管理员”的权限执行”任意”请求，比如将其添加到管理员组中。

###  Media Server

`Media
Server`套件提供与多媒体相关的服务，允许在`NAS`上通过`DLNA/UPnP`播放多媒体内容。在安装该套件后，会启动一些自定义的服务，如下。

![](https://p1.ssl.qhimg.com/t01b03ee0a8e037a760.png)

通过简单的分析，发现`dms`中存在一些可供访问的`url`，且无需认证。

![](https://p2.ssl.qhimg.com/t0116271c7f97c3b3a5.png)

第`1`个比较有意思的`api`是`videotranscoding.cgi`，对应的请求`url`格式为`http://%s:%d/transcoder/videotranscoding.cgi/%s/id=%d%s`，处理该请求的部分代码如下。可以看到，如果`url`中包含字符串`id=`和字符`?`，就将`id=`和`?`之间的内容拷贝到`dest`缓冲区中。由于没有考虑两者出现的先后顺序，如果请求`url`为`http://%s:%d/transcoder/videotranscoding.cgi/VideoStation?id=1`，在调用`strncpy()`时就会出现整数下溢问题。

    
    
    __int64 sub_406E80(__int64 a1)
    {
      // ...
      v4 = getenv("REQUEST_URI");
      snprintf(s, 0x800uLL, "%s", v4);
      v99 = strstr(s, "id=");
      if ( v99 )
      {
        v5 = strchr(s, '?');
        if ( v5 )
          strncpy(dest, v99 + 3, v5 - (v99 + 3)); // integer underflow
      }
      // ...
      std::string::assign(v3, dest, strlen(dest));
      // ...
      sub_403F50(a1, v1, v3, (std::string *)(a1 + 136));
    

假设请求`url`的格式和程序预期的一致，函数`sub_403F50()`将会在后续被调用，其第`3`个参数对应前面拷贝的请求`url`中`id=`和`?`之间的内容。在`sub_403F50()`中，对参数`a2`进行简单校验后，参数`a3`会被当做`id`后面的参数进行格式化。由于未对参数`a3`进行适当校验，且参数`a3`外部可控，因此会存在`SQL`注入的问题。

    
    
    __int64 sub_403F50(__int64 a1, std::string *a2, _QWORD *a3, std::string *a4)
    {
      // ...
      if ( !(unsigned int)std::string::compare(a2, "MediaServer") )
      {
        std::string::assign((std::string *)v32, "mediaserver", 0xBuLL);
        std::string::assign((std::string *)&v34, "MediaServer", 0xBuLL);
        std::string::assign((std::string *)v33, "video", 5uLL);
      }
      else
      {
        if ( (unsigned int)std::string::compare(a2, "VideoStation") )
          goto LABEL_4;
        std::string::assign((std::string *)v32, "video_metadata", 0xEuLL);
        std::string::assign((std::string *)&v34, "VideoStation", 0xCuLL);
        std::string::assign((std::string *)v33, "video_file", 0xAuLL);
      }
      snprintf(s, 0x100uLL, "SELECT * from %s where id = %s", v33[0], (const char *)*a3); // SQL injection
    

另外`1`个类似的`api`为`jpegtnscaler.cgi`，对应的请求`url`格式为`http://%s:%d/transcoder/jpegtnscaler.cgi/%s/%d.%s`，处理该请求的部分代码如下。可以看到，在调用`strncpy()`前未对其长度参数进行校验，通过构造请求如`http://%s:%d/transcoder/jpegtnscaler.cgi/<a*0x450>/1`，可造成缓冲区溢出。

    
    
    __int64 main(__int64 a1, char **a2, char **a3)
    {
      // ...
      v3 = getenv("REQUEST_URI");
      // ...
      v4 = strrchr(v3, '/');
      v5 = v4;
      // ...
      v6 = strtol(v4 + 1, 0LL, 10);
      bzero(s, 0x400uLL);
      strncpy(s, v3, v5 - v3);  // buffer overflow
    

###  Audio Station

`Audio
Station`套件提供收听广播节目、管理音乐库、建立个人播放清单等功能，并支持随时随地与朋友分享。安装该套件后，在其安装路径下会存在一些自定义的`cgi`程序，如`media_server.cgi`、`web_player.cgi`、`audiotransfer.cgi`等。在使用该套件的同时进行抓包，部分请求示例如下。

![](https://p4.ssl.qhimg.com/t01c25b783bbe797547.png)

在前面提到的`HTTP`请求处理流程中，`execl_cgi()`负责处理自定义的`cgi`请求。更重要的是，在某些情形下，认证的处理由自定义的`cgi`程序负责。

![](https://p1.ssl.qhimg.com/t01c140b53cc37f2743.png)

通过分析，最有意思的`api`为`audiotransfer.cgi`，对应的请求`url`格式为`http://%s:%d/webman/3rdparty/AudioStation/webUI/audiotransfer.cgi/%s.%s`，处理该请求的部分代码如下。可以看到，在`main()`函数开始处调用`sub_402730()`。在函数`sub_402730()`中，先获取请求`url`路径最后面的内容，然后将其传给`MediaIDDecryption()`。在`MediaIDDecryption()`中，先计算参数`a1`的长度，在拷贝前`6`个字节后，调用`snprintf()`。由于调用`snprintf()`时，其`size`参数和后面的字符串内容可控，存在缓冲区溢出问题。更重要的是，这个过程中没有对认证进行处理，即无需认证，因此通过构造并发送特定的请求，远程未认证的用户可触发该缓冲区溢出漏洞。

    
    
    __int64 main(__int64 a1, char **a2, char **a3)
    {
      sub_402730((__int64)v5);
    
    
    _BOOL8 sub_402730(__int64 a1)
    {
      // ...
      v8 = getenv("REQUEST_URI");
      snprintf(s, 0x400uLL, "%s", v8);
      // ...
      v11 = strrchr(s, '/');
      v12 = v11;
      if ( v11 )
      {
        // ...
        v15 = MediaIDDecryption((__int64)(v12 + 1));
    
    
    __int64 MediaIDDecryption(const char *a1)
    {
      // ...
      v1 = strlen(a1);
      if ( v1 > 5 )
      {
        v3 = (v1 - 6) >> 1;
        snprintf(s, 7uLL, "%s", a1);
        v14 = 0; v4 = s; v5 = (char *)&v14;
        do
        {
          v6 = *v4; --v5; ++v4; v5[6] = v6;
        }
        while ( v5 != &v13 );   // copy first 6 bytes
        __isoc99_sscanf(s, "%x", &v8);
        __isoc99_sscanf(&v14, "%x", &v9);
        snprintf(v17, v3 + 1, "%s", a1 + 6);
        snprintf(v18, v3 + 1, "%s", &a1[v3 + 6]); // buffer overflow
    

关于漏洞利用，知道创宇的`[@fenix](https://github.com/fenix "@fenix")`师傅基于`DSM
5.2-5592`和`Audio Station
5.4-2860`进行了[分析和测试](https://paper.seebug.org/1604/)，其中相关的条件包括`x86架构`、`NX保护`、`ASLR为半随机`，感兴趣的可以去看看。这里补充几点：

  * 针对`x86`架构，基于`DSM 6.x`，`ASLR`为全随机，通过寻找合适的`gadgets`，可实现稳定利用，无需堆喷或爆破；
  * 在`DSM 6.x`上，获取到`shell`后，还需要进行提权操作；
  * 针对`x64`架构，由于存在地址高位截断的问题，暂时未找到合适的思路进行利用。  

> 如果师傅们有合适的思路，欢迎交流 🙂

## One More Thing

上面只是列举了几个典型的套件，以及在其中发现的部分问题。实际上，群晖的`DSM`系统中有非常多的功能，以及大量的套件可供分析。群晖官方会不定期发布其产品的[安全公告](https://www.synology.com/en-global/security/advisory)，结合群晖的[镜像仓库](https://archive.synology.com/download/)，可以很方便地去做补丁分析和漏洞挖掘。

## 小结

针对群晖`NAS`的远程使用场景，本文重点对`web`接口上请求的流程和处理机制进行了分析。同时，结合几个典型的套件，基于上述流程，分享了在其中发现的部分安全问题。

本文是该系列的最后一篇，希望对群晖`NAS`设备感兴趣的同学有所收获。

## 相关链接

  * [Synology-SA-20:07 Synology Calendar](https://www.synology.cn/zh-cn/security/advisory/Synology_SA_20_07)
  * [Synology-SA-21:21 Audio Station](https://www.synology.cn/zh-cn/security/advisory/Synology_SA_21_21)
  * [聊聊 Synology NAS Audio Station 套件未授权 RCE 调试及 EXP 构造](https://paper.seebug.org/1604/)
  * [群晖产品安全公告](https://www.synology.com/zh-cn/security/advisory)
  * [群晖镜像仓库](https://archive.synology.com/download/)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **cq** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/266297](/post/id/266297)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __8赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t037e042cf93164b03c.jpg) cq

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

