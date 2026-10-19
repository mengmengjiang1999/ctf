## **背景**

**2019年1月9日，360威胁情报中心捕获到多个专门为阿拉伯语使用者设计的诱饵文档。钓鱼文档为携带恶意宏的OfficeExcel文档，恶意宏代码最终会释放执行一个C#编写的后门程序，该后门程序利用了复杂的DNS隧道技术与C2进行通信并执行指令，且通过GoogleDrive
API实现文件的上传下载。**

360威胁情报中心经过溯源和关联后确认，这是DarkHydrus APT组织针对中东地区的又一次定向攻击行动。DarkHydrus APT组织是Palo
Alto在2018年7月首次公开披露的针对中东地区政府机构进行定向攻击的APT团伙[1]。而在此之前，360威胁情报中心曾发现并公开过该组织使用SettingContent-ms文件任意代码执行漏洞（CVE-2018-8414）进行在野攻击的样本，并进行了详细分析[2]。

## 时间线

与DarkHydrusAPT组织相关的时间线如下：

![image.png](https://image.3001.net/images/20190118/1547801613_5c41940d0994f.png!small)

根据社交网络的反馈，对此团伙卡巴斯基内部的跟踪代号为:LazyMeerka。[4]

## **样本分析**

###  **Dropper（Macros）**

MD5 | 5c3f96ade0ea67eef9d25161c64e6f3e  
---|---  
文件名 | الفهارس.xlsm（indexes. xlsm）  
MD5 | 8dc9f5450402ae799f5f8afd5c0a8352  
---|---  
文件名 | الاطلاع.xlsm（viewing. xlsm）  
  
以下分析均以MD5：5c3f96ade0ea67eef9d25161c64e6f3e的样本为例，诱饵文档是一个OfficeExcel文档，名为الفهارس.xlsm（指标.xlsm）。其内嵌VBA宏，当受害者打开文档并启用宏后，将自动执行恶意宏代码。

该恶意宏代码的功能为释放WINDOWSTEMP.ps1和12-B-366.txt文件到%TEMP%目录，最后使用regsvr32.exe启动12-B-366.txt文件：

![dd53d25afe8351da81c3bfd64ff1ffde.png](https://image.3001.net/images/20190125/15484065644531.png!small)

实际上12-B-366.txt是一个HTA（HTML应用程序）文件，该文件用于启动释放出来的PowerShell脚本：%TEMP%\\\
WINDOWSTEMP.ps1

![3e9b26b2293c12cb70c87a3a09b2545e.png](https://image.3001.net/images/20190125/15484065903177.png!small)

WINDOWSTEMP.ps1脚本内容如下，该PowerShell脚本使用Base64和gzip解码和解压缩脚本里的content，然后写入到文件：%TEMP%\\\OfficeUpdateService.exe，最后运行%TEMP%\\\OfficeUpdateService.exe：

![4c1af717b36953c61081d270be296b21.png](https://image.3001.net/images/20190125/15484066176226.png!small)

###  **Backdoor（OfficeUpdateService.exe）**

MD5 | b108412f1cdc0602d82d3e6b318dc634  
---|---  
文件名 | OfficeUpdateService.exe  
PDB路径 | C:\Users\william\Documents\Visual Studio
2015\Projects\DNSProject\DNSProject\obj\Release\DNSProject.pdb  
编译信息 | Jan 08 14:26:53 2019 Microsoft Visual C# v7.0 / Basic .NET (managed)  
  
释放执行的后门程序使用C#编写：

![image.png](https://image.3001.net/images/20190118/1547801679_5c41944f743e7.png!small)

样本PDB路径信息和其使用的通信技术有很强的关联性，指示其使用了DNS相关的技术：

后门程序运行后会先检查参数是否包含“st:off”和“pd:off”，如果包含“st:off”则不会写启动项，如果包含“pd:off”则不会释放PDF文件。随后检测是否运行在虚拟机、沙箱中，或者是否被调试等，通过这些检查后最终执行恶意代码：

![7649d9af7e7e91fed1a403e865ad3a84.png](https://image.3001.net/images/20190125/15484066359397.png!small)

写入启动项的持久化操作：

![1a3d0ef4d8280aac53f98b41f6460ab5.png](https://image.3001.net/images/20190125/15484066565632.png!small)

释放诱饵PDF文件：

![image.png](https://image.3001.net/images/20190118/1547801715_5c4194735ae3c.png!small)

执行虚拟机、沙箱检测以及反调试等操作：

![ca6bfcff8842ff62f2ff5d87a8e9e432.png](https://image.3001.net/images/20190125/15484066788428.png!small)

紧接着获取主机信息：

![image.png](https://image.3001.net/images/20190118/1547801733_5c4194851f05a.png!small)

![17a14e2687cc947367440b71108f10a1.png](https://image.3001.net/images/20190125/1548406713479.png!small)

然后通过DNS隧道发送搜集到的主机信息，其中DNS隧道通信部分封装到queryTypesTest函数中：

![a1f267ea496adc9dde88cbd715b22d54.png](https://image.3001.net/images/20190125/15484067449590.png!small)

最后进入命令分发循环, 该命令分发流程首先判断是否是x_mode模式，如果不是，则通过DNS隧道技术与C2通信获取需要执行的指令，否则通过HTTP传输数据：

![a2464d30f473af356be99e64b8a2281e.png](https://image.3001.net/images/20190125/15484067672477.png!small)

与C2通过DNS隧道建立通信，并解析返回的数据，然后提取指令，最后通过taskHandler函数分发指令：

![image.png](https://image.3001.net/images/20190118/1547801801_5c4194c968135.png!small)

以下是部分指令截图：

![76ccd47cb3b57e5dea5abb11bbe7f904.png](https://image.3001.net/images/20190125/15484067908751.png!small)

值得注意的是，^\\\$x_mode指令将设置文件上传下载的服务器，服务器地址通过DNS隧道获取：

![image.png](https://image.3001.net/images/20190118/1547801820_5c4194dce7243.png!small)

其中一个样本指定了服务器为GoogleDrive服务器：

![fe26e127473d927a5c5504d97191a30b.png](https://image.3001.net/images/20190125/15484068105857.png!small)

所有命令列表如下：

**命令** | **功能**  
---|---  
**^kill** | 结束线程？进程  
**^\\\$fileDownload** | 文件下载  
**^\\\$importModule** | 获取进程模块  
**^\\\$x_mode** | 采用x_mode模式，此模式设置RAT服务器，然后采用HTTP发送RAT数据  
**^\\\$ClearModules** | 卸载模块  
**^\\\$fileUpload** | 文件上载  
**^testmode** | 测试某个模块  
**^showconfig** | 获取配置信息  
**^changeConfig** | 更改配置  
**^slp** | 睡眠一段时间  
**^exit** | 退出进程  
  
### **DNS隧道通信分析**

DNS隧道通信技术是指通过DNS查询过程来建立通信隧道。该通信方式有极强的隐蔽性，容易穿透各种流量网关的检测。

实现DNS隧道通信技术主要有两种方法：

> 1.指定DNS服务器实现DNS隧道通信；
>
> 2.通过域名提供商提供的接口修改NS记录，将解析域名的DNS服务器指定为攻击者的DNS服务器，接管域名的DNS解析请求。

本文所描述的后门程序OfficeUpdateService.exe使用的则是第二种方式实现DNS隧道通信，其主要原理为修改木马程序需要解析的域名的NS记录，由于DNS解析过程会首先尝试向NS记录指定的DNS服务器请求解析域名，所以NS记录指定的DNS服务器能收到DNS查询请求以及附带的数据。如果域名对应的NS记录中的DNS服务器是由攻击者控制的，那么攻击者就可以通过该DNS服务器与木马程序通过DNS查询建立起特殊的通信渠道。

木马程序请求的域名列表如下：

![image.png](https://image.3001.net/images/20190118/1547801860_5c419504b5c7c.png!small)

##  **设置NS记录**

NS（Name Server）记录是域名服务器记录，用来指定该域名由哪个DNS服务器来进行解析。

攻击者首先将相关域名的NS记录修改为了攻击者控制的DNS服务器，攻击者指定用于解析相关域名的NS服务器为：tvs1.trafficmanager.live，tvs2.trafficmanager.live，我们通过nslookup可以查询得到：

![image.png](https://image.3001.net/images/20190118/1547801866_5c41950a9811c.png!small)

样本再通过本机的nslookup程序向相关域名提交请求，而由于这些域名的NS记录被指定为了攻击者的DNS服务器（tvs1.trafficmanager.live），故nslookup提交的查询信息会被发送给攻击者的DNS服务器，然后读取DNS服务器返回的信息进行数据交互。所以样本其实是在和攻击者控制的DNS服务器进行最终的通信。

样本使用nslookup解析域名并附带以下参数：timeout（请求超时时间）、q（DNS请求类型）：

![image.png](https://image.3001.net/images/20190118/1547801872_5c419510c20f8.png!small)

##  **发送上线请求并获取执行指令**

木马会根据不同的查询类型，使用不同的正则表达式去匹配DNS服务器返回的结果数据。

比如执行nslookup并使用查询类型为A进行查询，最终使用以下正则表达式匹配返回的数据结果：

![image.png](https://image.3001.net/images/20190118/1547801879_5c4195176620c.png!small)

而样本首先会通过向攻击者控制的DNS服务器发送DNS查询请求来发送当前木马的上线ID给攻击者。首先获取当前的进程ID，并与请求查询的域名组成一个二级域名，依次使用nslookup指定DNS的查询类型发送DNS查询信息：

![image.png](https://image.3001.net/images/20190118/1547801886_5c41951ec6958.png!small)

接着根据当前DNS请求的类型分别用不同的正则表达式规则匹配其返回的数据结果，并取取其中的数据：

![image.png](https://image.3001.net/images/20190118/1547801891_5c41952378940.png!small)

 **我们手动模拟使用TXT** **查询请求并上传木马ID** **的过程如下：**

首先我们构造一个二级域名：ajpinc.akamaiedge.live，二级域名ajpinc中的a代表第一次请求，末尾的c代表结尾，a和c之间是编码过后的当前进程ID。然后我们使用nslookup发送该请求，执行的效果如下：

![image.png](https://image.3001.net/images/20190118/1547801896_5c419528a9c8d.png!small)

而木马程序会使用以下正则表达式来匹配返回的数据结果：

    
    
    (\\w+).(akdns.live|akamaiedge.live|edgekey.live|akamaized.live)

该正则表达式会匹配上述结果中的ajpinc和ihn字符串，然后将ihn通过指定的解码函数解码得到“107”，解码函数如下：

![image.png](https://image.3001.net/images/20190118/1547801901_5c41952d75562.png!small)

最后获取当前的配置信息，再通过DNS协议传输给攻击者控制的DNS服务器，并持续发送DNS请求，最终分别使用不同的正则表达式来匹配返回的结果，获取下一步需要执行的指令。

##  **数据匹配规则**

样本主要使用的DNS查询类型如下：

A  
---  
AAAA  
AC  
CNAME  
TXT  
SRV  
SOA  
MX  
  
木马会根据不同的查询类型，使用不同的正则表达式去匹配攻击者的DNS服务器返回的结果数据。

比如执行nslookup并使用查询类型AC得到返回的数据，并使用以下正则表达式匹配返回的数据结果：

![image.png](https://image.3001.net/images/20190118/1547801911_5c4195371cb5b.png!small)

使用查询类型为AAAA得到的数据使用以下正则表达式匹配返回的数据结果：

![image.png](https://image.3001.net/images/20190118/1547801916_5c41953cced2e.png!small)

使用其他DNS查询类型得到的数据使用以下正则表达式匹配返回的数据结果：

![image.png](https://image.3001.net/images/20190118/1547801924_5c419544cc818.png!small)

样本所使用的DNS查询类型及返回数据对应匹配的正则表达式如下：

**DNS** **查询类型** | **匹配结果的正则表达式**  
---|---  
A | Address:\\\s+(\\\d+.\\\d+.\\\d+.\\\d+)  
AC | ([^r-v\\\s]+)[r-v]([\\\w\\\d+\\\/=]+)-\\\w+.(<C2DOMIAN>)  
AAAA | Address:\\\s+(([a-fA-F0-9]{0,4}:{1,4}[\\\w|:]+){1,8})  
CNAME、TXT、SRV、SOA、MX |
([^r-v\\\s]+)[r-v]([\\\w\\\d+\\\/=]+)-\\\w+.(<C2DOMIAN>)和(\\\w+).(<C2DOMIAN>)  
  
如果当返回的DNS请求结果中被：

    
    
    "216.58.192.174|2a00:1450:4001:81a::200e|2200::|download.microsoft.com|ntservicepack.microsoft.com|windowsupdate.microsoft.com|update.microsoft.com"

正则表达式命中，则代表请求被取消，则不会执行后续的操作：

![image.png](https://image.3001.net/images/20190118/1547801931_5c41954b6e4e5.png!small)

##  **溯源与关联**

360威胁情报中心通过对样本详细分析后发现，此次攻击的幕后团伙疑似为DarkHydrus APT组织，部分关联依据如下。

###  **样本使用DNS隧道进行通信**

与之前Palo Alto披露[2]的木马类似的，都使用了相同的DNS隧道通信技术：

![image.png](https://image.3001.net/images/20190118/1547801936_5c419550abc4d.png!small)

###  **高度一致的沙箱检测代码和后门功能代码**

几乎完全一致的虚拟机、沙箱检测代码：

![image.png](https://image.3001.net/images/20190118/1547801942_5c41955607936.png!small)

恶意代码相似度极高，木马功能也高度相似：

![image.png](https://image.3001.net/images/20190118/1547801948_5c41955c5db89.png!small)

###  **拓展**

有趣的是，我们关联到某个Twitter用户@darkhydrus2的昵称为SteveWilliams，该用户名与DarkHydrus吻合，且昵称williams与此次C#编写的木马程序的PDB路径又有些关联：

![image.png](https://image.3001.net/images/20190118/1547801955_5c41956312025.png!small)

##  **总结**

从近年来的高级攻击事件分析中可以看出，由于利用Office 0day等漏洞进行攻击的成本较高，多数攻击者更趋向于利用Office
VBA宏执行恶意代码。企业用户应尽可能小心打开来源不明的文档，如有需要可通过打开Office文档中的：文件-选项-信任中心-信任中心设置-宏设置，来禁用一切宏代码执行。

![image.png](https://image.3001.net/images/20190118/1547801960_5c4195688bb65.png!small)

目前，基于360威胁情报中心的威胁情报数据的全线产品，包括360威胁情报平台（TIP）、天眼高级威胁检测系统、360
NGSOC等，都已经支持对此类攻击的精确检测。

##  **IOC**

**MD5**  
---  
5c3f96ade0ea67eef9d25161c64e6f3e  
8dc9f5450402ae799f5f8afd5c0a8352  
b108412f1cdc0602d82d3e6b318dc634  
039bd47f0fdb6bb7d68a2428c71f317d  
**PDB** **路径**  
C:\Users\william\Documents\Visual Studio
2015\Projects\DNSProject\DNSProject\obj\Release\DNSProject.pdb  
**CC** **地址**  
0ffice365.life  
0ffice365.services  
0nedrive.agency  
akamai.agency  
akamaiedge.live  
akamaiedge.services  
akamaized.live  
akdns.live  
azureedge.today  
cloudfronts.services  
corewindows.agency  
edgekey.live  
microsoftonline.agency  
nsatc.agency  
onedrive.agency  
phicdn.world  
sharepoint.agency  
skydrive.agency  
skydrive.services  
t-msedge.world  
trafficmanager.live  
  
## **参考链接**

[1].<https://ti.360.net/blog/articles/analysis-of-settingcontent-ms-file/>

[2].<https://unit42.paloaltonetworks.com/unit42-new-threat-actor-group-darkhydrus-targets-middle-east-government/>

[3].<https://ti.360.net/>

[4].<https://twitter.com/craiu/status/1083305994652917760>

 ***本文作者：360天眼实验室，转载请注明来自FreeBuf.COM**

