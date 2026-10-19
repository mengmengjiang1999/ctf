**作者：360威胁情报中心  
公众号：[360威胁情报中心](https://mp.weixin.qq.com/s/OOjDvnTm7oH0FCbaHKGgLA
"360威胁情报中心")**

## 背景

2019年1月9日，360威胁情报中心捕获到多个专门为阿拉伯语使用者设计的诱饵文档。钓鱼文档为携带恶意宏的Office
Excel文档，恶意宏代码最终会释放执行一个C#编写的后门程序，该后门程序利用了复杂的DNS隧道技术与C2进行通信并执行指令，且通过GoogleDrive
API实现文件的上传下载。

360威胁情报中心经过溯源和关联后确认，这是DarkHydrus APT组织针对中东地区的又一次定向攻击行动。DarkHydrus APT组织是Palo
Alto在2018年7月首次公开披露的针对中东地区政府机构进行定向攻击的APT团伙[1]。而在此之前，360威胁情报中心曾发现并公开过该组织使用SettingContent-ms文件任意代码执行漏洞（CVE-2018-8414）进行在野攻击的样本，并进行了详细分析[2]。

## 时间线

与DarkHydrus APT组织相关的时间线如下：

![img](https://images.seebug.org/content/images/2019/01/16/1547627608000-edc527e434d2aa3cbae441f8079ad9c2.jpg-w331s)

根据社交网络的反馈，对此团伙卡巴斯基内部的跟踪代号为:LazyMeerka。[4]

## 样本分析

### Dropper（Macros）

![
](https://images.seebug.org/content/images/2019/01/5a42e4f1-c508-4880-92e7-b6ca8a4aa83e.png-w331s)

以下分析均以MD5：5c3f96ade0ea67eef9d25161c64e6f3e的样本为例，诱饵文档是一个Office
Excel文档，名为???????.xlsm（指标.xlsm）。其内嵌VBA宏，当受害者打开文档并启用宏后，将自动执行恶意宏代码。

该恶意宏代码的功能为释放WINDOWSTEMP.ps1和12-B-366.txt文件到%TEMP%目录，最后使用regsvr32.exe启动12-B-366.txt文件：

![img](https://images.seebug.org/content/images/2019/01/16/1547627608000-dd53d25afe8351da81c3bfd64ff1ffde.png-w331s)

实际上12-B-366.txt是一个HTA（HTML应用程序）文件，该文件用于启动释放出来的PowerShell脚本：%TEMP%\
WINDOWSTEMP.ps1

![img](https://images.seebug.org/content/images/2019/01/16/1547627608000-3e9b26b2293c12cb70c87a3a09b2545e.png-w331s)

WINDOWSTEMP.ps1脚本内容如下，该PowerShell脚本使用Base64和gzip解码和解压缩脚本里的content，然后写入到文件：%TEMP%\OfficeUpdateService.exe，最后运行%TEMP%\OfficeUpdateService.exe：

![img](https://images.seebug.org/content/images/2019/01/16/1547627608000-4c1af717b36953c61081d270be296b21.png-w331s)

### Backdoor（OfficeUpdateService.exe）

![
](https://images.seebug.org/content/images/2019/01/1378e6c7-fef6-4e95-b6f7-bfd4751d01e7.png-w331s)

释放执行的后门程序使用C#编写：

![img](https://images.seebug.org/content/images/2019/01/16/1547627609000-9551a34797f0ad5899094f9e0d312382.png-w331s)

样本PDB路径信息和其使用的通信技术有很强的关联性，指示其使用了DNS相关的技术：

C:\Users\william\Documents\Visual Studio
2015\Projects\DNSProject\DNSProject\obj\Release\DNSProject.pdb

后门程序运行后会先检查参数是否包含“st:off”和“pd:off”，如果包含“st:off”则不会写启动项，如果包含“pd:off”则不会释放PDF文件。随后检测是否运行在虚拟机、沙箱中，或者是否被调试等，通过这些检查后最终执行恶意代码：

![img](https://images.seebug.org/content/images/2019/01/16/1547627609000-7649d9af7e7e91fed1a403e865ad3a84.png-w331s)

写入启动项的持久化操作：

![img](https://images.seebug.org/content/images/2019/01/16/1547627609000-1a3d0ef4d8280aac53f98b41f6460ab5.png-w331s)

释放诱饵PDF文件：

![img](https://images.seebug.org/content/images/2019/01/16/1547627609000-9bf3a9bc3acd635e748d853a61cf0621.png-w331s)

执行虚拟机、沙箱检测以及反调试等操作：

![img](https://images.seebug.org/content/images/2019/01/16/1547627609000-ca6bfcff8842ff62f2ff5d87a8e9e432.png-w331s)

紧接着获取主机信息：

![img](https://images.seebug.org/content/images/2019/01/16/1547627609000-e97b3da585aa9409fe5895af71eddf8b.png-w331s)

![img](https://images.seebug.org/content/images/2019/01/16/1547627609000-17a14e2687cc947367440b71108f10a1.png-w331s)

然后通过DNS隧道发送搜集到的主机信息，其中DNS隧道通信部分封装到queryTypesTest函数中：

![img](https://images.seebug.org/content/images/2019/01/16/1547627609000-a1f267ea496adc9dde88cbd715b22d54.png-w331s)

最后进入命令分发循环, 该命令分发流程首先判断是否是x_mode模式，如果不是，则通过DNS隧道技术与C2通信获取需要执行的指令，否则通过HTTP传输数据：

![img](https://images.seebug.org/content/images/2019/01/16/1547627609000-a2464d30f473af356be99e64b8a2281e.png-w331s)

与C2通过DNS隧道建立通信，并解析返回的数据，然后提取指令，最后通过taskHandler函数分发指令：

![img](https://images.seebug.org/content/images/2019/01/16/1547627609000-39be8110906c9b6464f7b5bd7b5bbdbb.png-w331s)

以下是部分指令截图：

![img](https://images.seebug.org/content/images/2019/01/16/1547627610000-76ccd47cb3b57e5dea5abb11bbe7f904.png-w331s)

值得注意的是，^\$x_mode指令将设置文件上传下载的服务器，服务器地址通过DNS隧道获取：

![img](https://images.seebug.org/content/images/2019/01/16/1547627610000-5ff9bfc4006e52bb4b00e2154d6ce71f.png-w331s)

其中一个样本指定了服务器为Google Drive服务器：

https://www.googleapis.com/upload/drive/v3/files/" + file_id +
"?supportsTeamDrive=true&uploadType=resumable&fields=kind,id,name,mimeType,parents

![img](https://images.seebug.org/content/images/2019/01/16/1547627610000-fe26e127473d927a5c5504d97191a30b.png-w331s)

所有命令列表如下：

![
](https://images.seebug.org/content/images/2019/01/e7d7de6f-d645-4d2f-b001-0d495eff28ef.png-w331s)

### DNS隧道通信分析

DNS隧道通信技术是指通过DNS查询过程来建立通信隧道。该通信方式有极强的隐蔽性，容易穿透各种流量网关的检测。

实现DNS隧道通信技术主要有两种方法：

  1. 指定DNS服务器实现DNS隧道通信
  2. 通过域名提供商提供的接口修改NS记录，将解析域名的DNS服务器指定为攻击者的DNS服务器，接管域名的DNS解析请求

本文所描述的后门程序OfficeUpdateService.exe使用的则是第二种方式实现DNS隧道通信，其主要原理为修改木马程序需要解析的域名的NS记录，由于DNS解析过程会首先尝试向NS记录指定的DNS服务器请求解析域名，所以NS记录指定的DNS服务器能收到DNS查询请求以及附带的数据。如果域名对应的NS记录中的DNS服务器是由攻击者控制的，那么攻击者就可以通过该DNS服务器与木马程序通过DNS查询建立起特殊的通信渠道。

木马程序请求的域名列表如下：

![img](https://images.seebug.org/content/images/2019/01/16/1547627610000-e5428eb693b95d9c2c8d3bbf0fa5213e.png-w331s)

#### 设置NS记录

NS（Name Server）记录是域名服务器记录，用来指定该域名由哪个DNS服务器来进行解析。

攻击者首先将相关域名的NS记录修改为了攻击者控制的DNS服务器，攻击者指定用于解析相关域名的NS服务器为：tvs1.trafficmanager.live
, tvs2.trafficmanager.live，我们通过nslookup可以查询得到：

![img](https://images.seebug.org/content/images/2019/01/16/1547627610000-4f4257c49ba5798bbf7beccd7df102eb.png-w331s)

样本再通过本机的nslookup程序向相关域名提交请求，而由于这些域名的NS记录被指定为了攻击者的DNS服务器（tvs1.trafficmanager.live），故nslookup提交的查询信息会被发送给攻击者的DNS服务器，然后读取DNS服务器返回的信息进行数据交互。所以样本其实是在和攻击者控制的DNS服务器进行最终的通信。

样本使用nslookup解析域名并附带以下参数：timeout（请求超时时间）、q（DNS请求类型）：

![img](https://images.seebug.org/content/images/2019/01/16/1547627610000-9bb8d3edf302b8a537de5cad3fe1a604.png-w331s)

#### 发送上线请求并获取执行指令

木马会根据不同的查询类型，使用不同的正则表达式去匹配DNS服务器返回的结果数据：

比如执行nslookup并使用查询类型为A进行查询，最终使用以下正则表达式匹配返回的数据结果：

![img](https://images.seebug.org/content/images/2019/01/16/1547627610000-1f0b4d55822eb6f419beee9d22cb84ef.png-w331s)

而样本首先会通过向攻击者控制的DNS服务器发送DNS查询请求来发送当前木马的上线ID给攻击者：首先获取当前的进程ID，并与请求查询的域名组成一个二级域名，依次使用nslookup指定DNS的查询类型发送DNS查询信息：

![img](https://images.seebug.org/content/images/2019/01/16/1547627611000-8bdae68c0eccc67696e7511beb9af156.png-w331s)

接着根据当前DNS请求的类型分别用不同的正则表达式规则匹配其返回的数据结果，并取取其中的数据：

![img](https://images.seebug.org/content/images/2019/01/16/1547627611000-1ab36fc1cf8b211e0f78954585b42dc9.png-w331s)

**我们手动模拟使用TXT查询请求并上传木马ID的过程如下：**

首先我们构造一个二级域名：ajpinc.akamaiedge.live，二级域名ajpinc中的a代表第一次请求，末尾的c代表结尾，a和c之间是编码过后的当前进程ID。然后我们使用nslookup发送该请求，执行的效果如下：

![img](https://images.seebug.org/content/images/2019/01/16/1547627611000-8c2d17a45dda4fb21e0651e69cb90dc8.png-w331s)

而木马程序会使用以下正则表达式来匹配返回的数据结果：(\w+).(akdns.live|akamaiedge.live|edgekey.live|akamaized.live)

该正则表达式会匹配上述结果中的ajpinc和ihn字符串，然后将ihn通过指定的解码函数解码得到“107”，解码函数如下：

![img](https://images.seebug.org/content/images/2019/01/16/1547627611000-bb9aec785bca8618f6c3d704c0191731.png-w331s)

最后获取当前的配置信息，再通过DNS协议传输给攻击者控制的DNS服务器，并持续发送DNS请求，最终分别使用不同的正则表达式来匹配返回的结果，获取下一步需要执行的指令。

#### 数据匹配规则

样本主要使用的DNS查询类型如下：

![
](https://images.seebug.org/content/images/2019/01/bc54f12b-0419-4797-8278-54f6d2819637.png-w331s)

木马会根据不同的查询类型，使用不同的正则表达式去匹配攻击者的DNS服务器返回的结果数据：

比如执行nslookup并使用查询类型AC得到返回的数据，并使用以下正则表达式匹配返回的数据结果：

![img](https://images.seebug.org/content/images/2019/01/16/1547627611000-0ee23e7725e3ecacc44b4204d9d5d455.png-w331s)

使用查询类型为AAAA得到的数据使用以下正则表达式匹配返回的数据结果：

![img](https://images.seebug.org/content/images/2019/01/16/1547627611000-c55eec4dcdd7e936a82c5ce2bb4aa8bd.png-w331s)

使用其他DNS查询类型得到的数据使用以下正则表达式匹配返回的数据结果：

![img](https://images.seebug.org/content/images/2019/01/16/1547627611000-03e663f255b8a7732367bf6769feee29.png-w331s)

样本所使用的DNS查询类型及返回数据对应匹配的正则表达式如下：

![
](https://images.seebug.org/content/images/2019/01/8b87387f-2b5a-4c69-8f9f-2de2c612c975.png-w331s)

如果当返回的DNS请求结果中被"216.58.192.174|2a00:1450:4001:81a::200e|2200::|download.microsoft.com|ntservicepack.microsoft.com|windowsupdate.microsoft.com|update.microsoft.com"正则表达式命中，则代表请求被取消，则不会执行后续的操作：

![img](https://images.seebug.org/content/images/2019/01/16/1547627611000-3ea73894d69603f376ed853417b6cccb.png-w331s)

## 溯源与关联

360威胁情报中心通过对样本详细分析后发现，此次攻击的幕后团伙疑似为DarkHydrus APT组织，部分关联依据如下。

### 样本使用DNS隧道进行通信

与之前Palo Alto披露[2]的木马类似的，都使用了相同的DNS隧道通信技术：

![img](https://images.seebug.org/content/images/2019/01/16/1547627611000-30de0c60db0e298e345a0737c2b78667.png-w331s)

### 高度一致的沙箱检测代码和后门功能代码

几乎完全一致的虚拟机、沙箱检测代码：

![img](https://images.seebug.org/content/images/2019/01/16/1547627612000-65c818b7aba82c2cf2370643124a61f3.png-w331s)

恶意代码相似度极高，木马功能也高度相似：

![img](https://images.seebug.org/content/images/2019/01/16/1547627612000-845cfba5935f00626c4f6a52577c7e92.png-w331s)

### 拓展

有趣的是，我们关联到某个Twitter用户@darkhydrus2的昵称为Steve
Williams，该用户名与DarkHydrus吻合，且昵称williams与此次C#编写的木马程序的PDB路径又有些关联：

![img](https://images.seebug.org/content/images/2019/01/16/1547627612000-2ec9676d85908c4915445ff4d3181459.png-w331s)

## 总结

从近年来的高级攻击事件分析中可以看出，由于利用Office 0day等漏洞进行攻击的成本较高，多数攻击者更趋向于利用Office
VBA宏执行恶意代码。企业用户应尽可能小心打开来源不明的文档，如有需要可通过打开Office文档中的：文件-选项-信任中心-信任中心设置-宏设置，来禁用一切宏代码执行：

![img](https://images.seebug.org/content/images/2019/01/16/1547627612000-c1ca847b048f775f2bb93fe55e1e4372.png-w331s)

目前，基于360威胁情报中心的威胁情报数据的全线产品，包括360威胁情报平台（TIP）、天眼高级威胁检测系统、360
NGSOC等，都已经支持对此类攻击的精确检测。

## IOC

![
](https://images.seebug.org/content/images/2019/01/33c189f6-71cb-441e-b172-64eaeebabe61.png-w331s)
![
](https://images.seebug.org/content/images/2019/01/b7963905-a398-40a1-9727-113bc4e772d5.png-w331s)

## 参考链接

[1]. <https://ti.360.net/blog/articles/analysis-of-settingcontent-ms-file/>

[2]. <https://unit42.paloaltonetworks.com/unit42-new-threat-actor-group-darkhydrus-targets-middle-east-government/>

[3]. <https://ti.360.net/>

[4]. <https://twitter.com/craiu/status/1083305994652917760>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/793/>

