ESET 的研究人员发现了一个全新的攻击组织 Worok，该组织自动 2020 年就一直处于活跃状态。Worok 使用的工具集包括一个 C++
编写的加载程序 CLRLoad、一个 PowerShell 编写的后门 PowHeartBeat 和一个 C# 编写的加载程序
PNGLoad，攻击者使用隐写术来提取隐藏在 PNG 文件中的 Payload。

## Worok

在 2021 年初 ProxyShell（CVE-2021-34523）漏洞披露期间，研究人员发现了各种 APT 组织的利用活动。其中发现与 TA428
组织类似的特征：

> 活动时间
>
> 目标行业
>
> ShadowPad 的使用

但其余工具集大不相同，所以分析人员分为 Worok 与 TA428 归属相同的证据不足，将其确定为一个新的攻击组织。根据 ESET 的遥测数据，Worok
自从 2020 年底一直保持活跃至今。

2020 年底，Worok 就瞄准多个国家的政府和公司进行攻击，具体来说：

> 东亚某电信公司
>
> 中亚某银行
>
> 东南亚某海运公司
>
> 中东某政府单位
>
> 南非某私营公司

从 2021 年 5 月到 2022 年 1 月，攻击者进入静默期。Worok 在 2022 年 2 月又重出江湖，攻击了：

> 中亚某能源公司
>
> 东南亚某公共部门

下图显示了攻击影响的可视化：

![image.png-297.4kB](https://image.3001.net/images/20220910/1662824878_631cb1ae28a89a0324bd8.png!small)攻击地图

根据分析，研究人员认为 Worok 的主要目标是窃密。

## 技术分析

攻击者会利用 ProxyShell 漏洞，成功后上传 Webshell 进行持久化与后续攻击阶段。

获取权限后，攻击者部署了多个公开的侦察工具，如 Mimikatz、EarthWorm、ReGeorg 和 NBTscan。紧接着会部署后续两阶段的攻击
Payload，但未发现最终的攻击 Payload 是什么。在 2021 年，第一阶段加载程序是 CLRLoad，而在 2022 年已经被功能齐全的
PowerShell 后门 PowHeartBeat 所取代。

执行链如下所示：

![image.png-313.5kB](https://image.3001.net/images/20220910/1662824879_631cb1afd11cabe354cac.png!small)两条执行链

## CLRLoad

CLRLoad 是一个 C++ 编写的 Loader，用于加载下一阶段的 PNGLoad 样本。该样本为一个 DLL 文件，有 32 位与 64
位两个版本。样本也是通过合法目录中的文件进行加载的，用于欺骗作为合法软件。

CLRLoad 样本查找文件的完整路径，路径被单字节异或编码，且每个样本中都使用不同的密钥。部分路径如下所示：

> C:\Program Files\VMware\VMware Tools\VMware VGAuth\xsec_1_5.dll
>
> C:\Program Files\UltraViewer\msvbvm80.dll
>
> C:\Program Files\Internet Explorer\Jsprofile.dll
>
> C:\Program Files\WinRar\RarExtMgt.dll
>
> C:\Program Files (x86)\Foxit Software\Foxit Reader\lucenelib.dll

样本使用的一个互斥量名为 `Wo0r0KGWhYGO`，故将其命名为 Worok。

## PowHeartBeat

PowHeartBeat 是一个 PowerShell 编写的全功能后门，利用压缩、编码和加密等手段进行了混淆处理。根据 ESET
的遥测数据，PowHeartBeat 在最近取代了 CLRLoad 作为用于启动 PNGLoad 的工具。

代码的第一层由多块 base64 编码的 PowerShell 代码组成，重组 Payloda 后会通过 IEX
执行。解码后，会执行另一层混淆代码，如下所示：

![image.png-450.1kB](https://image.3001.net/images/20220910/1662824881_631cb1b16ece525c67cbd.png!small)PowerShell
代码

第二层首先使用 base64 解码其代码的下一层，然后使用 CBC 模式的三重 DES 算法进行解密。解密后再使用 gzip 算法解压获得
PowerShell 的第三层代码，这才是真正的后门代码。

后门使用 HTTP 或者 ICMP 协议与 C&C 服务器进行通信，原理如下所示：

![image.png-95.9kB](https://image.3001.net/images/20220910/1662824882_631cb1b2a609dba7c8e2e.png!small)工作原理

### 配置

配置中有许多可选字段，如下所示：

字段名称| 描述  
---|---  
nouse| 未使用  
ClientId| 客户端标识  
Version| 版本号  
ExecTimes| 执行命令尝试次数  
UserAgent| 用于C&C通信的 User-Agent  
Referer| 用于C&C通信的 Referer  
AcceptEncoding| 未使用  
CookieClientId/CookieTaskId/CookieTerminalId| 用于C&C通信的 Cookie  
UrlHttps| 用于C&C通信的协议  
UrlDomain/IPAddress/Domains| 用于C&C通信的地址  
UrlSendHeartBeat| 用于C&C通信的 URL 路径  
UrlSendResult| 用于C&C通信的 URL 路径  
GetUrl| 完整的 URL  
PutUrl| 完整的 URL  
currentPath| 未使用  
ProxyEnableFlag| 是否启用代理  
Proxymsg| 代理地址  
Interval| 请求间隔  
BasicConfigPath| 基础配置路径  
UpTime| 开始运行时间  
DownTime| 停止运行时间  
DomainIndex| 用于 C&C 通信的当前域名  
SecretKey| 用于加解密的密钥  
IfLog| 未使用  
IfLogFilePath| 是否启用日志记录  
logpath| 日志文件路径  
ProxyFile| 代理配置文件路径  
IfConfig| 是否启用配置文件  
  
PowHeartBeat 样本中提取的配置如下所示：

    
    
    $Script:nouse = 100;if(Test-Path $MyInvocation.MyCommand.Path){Remove-item $MyInvocation.MyCommand.Path -Force;}$Script:ClientId = "83";$Script:Version = "2.1.3.0003";$Script:ExecTimes = 10;$Script:UserAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3487.100 Safari/537.36";$Script:Referer = "www.adobe.com";$Script:AcceptEncoding = "text/html,app1ication/xhtml+xml,app1ication/xml;q=0.9,*/*;q=0.8";$Script:CookieClientId = "s_ecid";$Script:CookieTaskId = "aam_uuid";$Script:CookieTerminalId = "AAMC_adobe_0";﻿$Script:UrlHttps = "http://";$Script:UrlDomain=  " 118.193.78[.]22:443";$Script:UrlSendHeartBeat = "/latest/AdobeMessagingClient.js";$Script:UrlSendResult = "/content/dam/offers-homepage/homepage.jpg";$Script:GetUrl = $Script:UrlHttps + $Script:UrlDomain + $Script:UrlSendHeartBeat;$Script:PutUrl = $Script:UrlHttps + $Script:UrlDomain + $Script:UrlSendResult;$Script:currentPath = Split-Path -Parent $MyInvocation.MyCommand.Definition;$Script:ProxyEnableFlag = $false;$Script:Proxymsg;$Script:Interval = 10 ;$Script:BasicConfigPath = "C:\ProgramData\unins.dat";$Script:UpTime = 0;$Script:DownTime = 24;$Script:Domains;$Script:DomainIndex;$Script:SecretKey = "###ConfigKey###";#$Script:IfLog = $true;$Script:IfLogFilePath = "C:\ProgramData\tpncp.dat";$Script:logpath = "C:\ProgramData\unins000.dat";$Script:ProxyFile = "C:\ProgramData\hwrenalm.dat";$Script:IfConfig = $false;﻿

### C&C 通信

PowHeartBeat 在 2.4 版本前使用 HTTP 进行 C&C 通信，后续切换到 ICMP，这两者都没有经过加密。

#### HTTP

GET 请求的格式如下所示：

    
    
    GET <UrlSendHeartBeat> HTTP/1.1User-Agent: <UserAgent>Referer: <Referer>Host: <Domain>Cookie: <CookieClientId>=<ClientId>Connection: close﻿

响应中通过 command_id 提供要执行的命令，加密算法如下所示：

    
    
    o[int] $pos = $taskId % 256;for ($i = 0; $i -lt $tmpBytes.Value.Length; $i++){$pos = $pos + $clientId;if ($pos -ge 256){$pos = $pos % 256;}$tmpBytes.Value[$i] = [byte]($tmpBytes.Value[$i] -bxor $hexEnc[$pos]);}

#### ICMP

从 PowHeartBeat 的 2.4 版本开始，HTTP 被 ICMP 取代，这可能是一种逃避检测的方式。

更新的代码中有一些细微的修改：

> 请求命令之前，PowHeartBeat 会在每个循环中发送一个包含字符串`abcdefghijklmnopqrstuvwxyz`的心跳包，告知 C&C
> 服务器准备好接收命令
>
> 获取后门执行命令的请求中包含字符串`abcdefghijklmnop`

心跳包如下所示：

![image.png-49.4kB](https://image.3001.net/images/20220910/1662824883_631cb1b3b3060aee68f08.png!small)心跳包布局

Client ID 和 Client Flag 的区别在于每个样本的 Client ID 都不同，而 Client Flag
在每个样本中都一样。Heartbeat Flag 表示后门正在发送心跳包。响应如下所示：

![image.png-66.8kB](https://image.3001.net/images/20220910/1662824884_631cb1b47f8c4d379287c.png!small)响应布局

此处的 Flag 表明是否有命令下发，获取命令的请求如下所示：

![image.png-50kB](https://image.3001.net/images/20220910/1662824885_631cb1b5322333ae752e1.png!small)获取命令的请求布局

ICMP 通信使得后门可以接收无限的数据，请求的响应如下所示：

![image.png-53.6kB](https://image.3001.net/images/20220910/1662824886_631cb1b60949f8580792f.png!small)获取命令的响应布局

与 HTTP 响应一样，data 中的第三个字节为命令标识符。

连续七次 ICMP 响应为空或者格式不一致的内容，C&C 通信就被认为完成了。

### 后门命令

PowHeartBeat 具备多种功能，支持命令如下所示：

命令| 标识符| 描述  
---|---|---  
Cmd| 0x02| 执行 PowerShell 命令  
Exe| 0x04| 执行程序  
FileUpload| 0x06| 将文件压缩上传到失陷主机  
FileDownLoad| 0x08| 在失陷主机下载文件  
FileView| 0x0A| 获取特定目录的文件信息  
FileDelete| 0x0C| 删除文件  
FileRename| 0x0E| 重命名/移动文件  
ChangeDir| 0x10| 更改工作目录  
Info| 0x12| 获取失陷主机的信息  
Config| 0x14| 更新配置文件并重新加载  
N/A| 0x63| 程序退出  
  
如果执行出现了错误，后门会向 C&C 服务器发起的 POST 请求中使用特定的命令标识符 0x00。

## PNGLoad

二阶段载荷为 PNGLoad，通过后门 PowHeartBeat 从 C&C 服务器下载和执行额外的载荷。PNGLoad 是一个 Loader，它使用
PNG 文件中的字节来创建要执行的 Payload。

该文件是 64 位的 .NET 可执行文件，并且使用 [.NET
Reactor](https://www.eziriz.com/dotnet_reactor.htm)进行了混淆，伪装成 WinRAR 的 DLL 文件。

![image.png-653.2kB](https://image.3001.net/images/20220910/1662824886_631cb1b6d14158a8076d6.png!small)伪造的文件信息

去混淆后发现文件只有一个类，有一个 MainPath 属性包含后门搜索的目录路径，以查找扩展名为 `.png`的文件，如下所示。

![image.png-469.3kB](https://image.3001.net/images/20220910/1662824888_631cb1b83fb358014c4f5.png!small).png
文件列表

通过此 MainPath 搜索找到的每个 .png 文件中的隐写嵌入内容。使用存储在 PNGLoad 的 SecretKeyBytes
属性中的密钥，对缓冲区的其余部分进行多字节异或解密，然后对解密的缓冲区进行 gzip 解压缩。得到的应该是 PowerShell 脚本，会被立即执行。

![image.png-182.7kB](https://image.3001.net/images/20220910/1662824889_631cb1b94853e105c5088.png!small)图片隐写

PNGLoad 执行的操作记录在一个文件中，该文件的路径存储在变量 LogFilePath 中。仅当存在其路径由内部变量 IfLogFilePath
指定的文件时，才会记录操作。

受限于数据视野，研究人员未能获得与 PNGLoad 一起使用的示例 .png 文件。攻击者将恶意 Payload 隐藏在看起来无害的 PNG
图片中，将恶意内容隐藏在明处。

## 总结

Worok 是一个能够自己开发攻击工具入侵目标的攻击组织，攻击者专注于亚洲和非洲的政府部门发起攻击。从攻击的时间与工具集上看，可能与 TA428
存在关联，但并没有可靠的证据证明这一点。

## IOC

> ce1f6a25c0f5fbe1ee4616fe4bcdee30  
> 8c09b80f28f444574719b5ff53ac4394  
> d3cdd49a55f062af46b8375ca3be9462  
> 2cd5c4608e165e5e4f11dc00398913ed  
> 017e8d89d7bab7f6f5cac0067faf69e7  
> aaa66fb6194f1c90be7519977d56945a  
> 6d0deb9181031a75990867c1597aa01a  
> 333cce11f50adff79ea193019d8f8905  
> 8a043a6bf7dee520d05680a35db6c399  
> 1cd36decbc8daf047501e5721558e2b7  
> 37aa47031adac4de609650d7ae307145  
> e60da077ee9e2217feafa524b9ce522a  
> 64f73627d91efe1a46e916c3095e7aa6  
> 2aa84d8672fd472e6c206d80a56743ff  
> 047cb0a376094509219c9f56359f92b9  
> 072a94adb5db5b4717573d1a4874fa65  
> e4b34594383fa2ee452e55176f21571e  
> da1e5e96b8ad75580f7544639d9e46f2  
> d0893703f0f1ec10e59efff775044b6b  
> 0c2ed7015a90cd1652cb172f6d03e214  
> 2403cccd6a27437a9aa8f31af8b537c0  
> 78E6BF7726C03F240A3A69FAE222BFBA  
> 12F62B96F9F42BB484CE3DE5786D5999  
> 118.193.78.22  
> 118.193.78.57  
> 5.183.101.9  
> 45.77.36.243  
> airplane.travel-commercials.agency  
> central.suhypercloud.org

## 参考来源

> [ESET](https://www.welivesecurity.com/2022/09/06/worok-big-picture/)

