**原文链接:[ShellReset RAT Spread Through Macro-Based Documents Using AppLocker
Bypass](https://www.zscaler.com/blogs/research/shellreset-rat-spread-through-macro-based-documents-using-applocker-bypass)**  
**译者：知道创宇404实验室翻译组**

之前我们说到：网络犯罪分子通常会将[攻击点与热点相联系](https://www.zscaler.com/blogs/research/30000-percent-increase-covid-19-themed-attacks)。近期，我们就发现有犯罪分子使用伦敦技术事件做诱饵来进行网络攻击。

2020年2月-5月，我们观察到在基于.space和.xyz域的新注册站点上托管了四个基于恶意宏的Microsoft
Word文档。由于几个文档的最终有效负载的部署策略、技术和过程（TTP）十分类似，我们认为这是同一个攻击者的行为。

据了解，.NET有效负载的最终版以往从未被检测到过，它的代码段很小，而且与QuasarRAT相重叠，但此代码段在运行时并未使用。根据最终有效负载中的唯一字符串我们为把该RAT命名为ShellReset。由于被检测到的数量有限，我们认为这可能是是一种小范围的攻击活动，而攻击者在这个攻击过程中使用的主题也和今年在伦敦发生的热点事件有关，其中还包括[5G
Expo](https://5gexpo.net/global/)
和[Futurebuild](https://www.futurebuild.co.uk/)。

其中的感染链涉及一些有趣的技术，如在运行时使用受信任的Windows实用程序在终端上编译有效负载以绕过安全机制，还会从攻击者的服务器下载混淆后的源代码。本文我将对分发策略和攻击的技术进行详细分析。

## 分发策略

2020年2月，与此攻击活动相关的示例文档进行了发布，其托管网址为：hxxps：//documentsharing.space/files/5G%20Expo.doc？clientEmail
=

**MD5 hash: 93f913f3b9e0ef3f5cedd196eae3f2ae**  
**File name: 5G Expo.doc**

本文档的内容与5G博览会活动有关，该活动计划于2020年3月17日至18日在伦敦举行，如图所示。

![](https://images.seebug.org/content/images/2020/06/83261209-4ee5-4208-97d3-3941881a1162.png-w331s)
启用宏后，本文档显示5G Expo 2020主题

同日，我们在URL上的同一域中找到了了另一个托管文档网址：hxxps：//documentsharing.space/files/FutureBuild.doc？clientEmail
=

**MD5 hash: b34b74effbd8647c4f5dc61358e1555f**  
**File name: FutureBuild.doc**

该文档的内容与本应于2020年3月3-5日在伦敦举行的Futurebuild 2020会议有关。该文件在形式上伪装成了本次会议的入场券，如图所示。

![](https://images.seebug.org/content/images/2020/06/0edd4eb5-b77e-493f-b9c2-bd347659054c.png-w331s)
启用宏后，文档显示Futurebuild 2020主题

在这两种情况下，用于承载文件的域都是documentharing[.]space。根据域的Whois记录，它已于2019年10月21日注册。

2020年5月发现同一攻击者的的两个文档示例。

2020年5月19日，我们在URL上找到了一个托管的基于宏的恶意Word文档，其网址为：hxxps://misrmarket[.]xyz/files/Get%20Stared.doc?clientEmail=

**MD5 hash: 7bebf686b6e1d3fa537e8a0c2e5a4bdc**  
**File name: Get%20Stared.doc**

本文档的内容是有关个人数据革命的内容，其中包括合法站点列表，如图所示

![](https://images.seebug.org/content/images/2020/06/0dfa0cda-382e-4e8c-ae58-c4a45f37e546.png-w331s)
文档显示有关个人数据革命的消息

经过进一步的研究，我们发现该文本是从网站datacoup.com上复制的，如图所示

![](https://images.seebug.org/content/images/2020/06/57b0b6f2-b071-467d-be42-5bcde63e01f9.png-w331s)
文档中显示的消息是从datacoup.com复制

用于承载此文档的网站是一个欺诈网站anonfiles.com，该网站允许用户匿名上传文件。但该欺诈网站站点和原始站点在用户界面上存在着细微差别。下图显示了欺诈网站站点的用户界面。

![](https://images.seebug.org/content/images/2020/06/b55e1180-ab59-41df-8dbd-9aff0b3e8e7c.png-w331s)
anonfiles.com欺诈网站的Web用户界面

下图显示了原始网站站点的用户界面。

![](https://images.seebug.org/content/images/2020/06/4afd75de-c241-4510-9ab7-40f0c4fe34ce.png-w331s)
原始网站站点anonfiles.com

红色标记区域不在欺诈网站区域范围内，根据Whois数据，欺诈网站misrmarket [.xyz]已于2020年2月26日注销。

我们在托管文档的所有URL中观察到其常见模式是：“？clientEmail=”，其中URL的参数还包含目标用户的电子邮件地址。

## **宏的技术分析**

打开宏的文档时，它会显示一条消息，其要求用户启用宏以查看内容，如下图所示：

![](https://images.seebug.org/content/images/2020/06/17be805b-ccbe-4eba-8340-5d02ab1420bb.png-w331s)
文档显示的消息，要求用户启用宏

启用宏后，将调用宏的Auto_Open()子例程，这将隐藏上图并显示与文档主题（5G Expo，Future Build 2020等）相对应的图像。

部分的宏代码也在启用宏后取消隐藏图像，如下图所示：

![](https://images.seebug.org/content/images/2020/06/373fd3c7-a753-47a7-9c27-055edd8599c0.png-w331s)
用于取消隐藏图像的宏代码

为了更好进行分析，我们将使用MD5的 hash: 7bebf686b6e1d3fa537e8a0c2e5a4bdc文件。宏的内容如图所示：

![](https://images.seebug.org/content/images/2020/06/8a23522f-e899-45ce-9fe7-715d0f5ed6e2.png-w331s)
文档中的宏代码

该宏代码的主要功能是：

  1. 它将工作目录和放置文件的名称设置为ServiceHostV1000。

  2. 它包含嵌入在宏中的完整C＃代码，这些代码在运行时写在了工作目录文件ServiceHostV1000.cs中。在源代码中混淆了C＃代码，但仅混淆了变量、类和名称。

  3. 它将编译器目录设置为文件csc.exe在计算机上的位置。Csc.exe是C＃代码的命令行编译器，一般情况下默认与Microsoft.NET框架一起安装。宏会在计算机上搜索版本3.5和4.0.x，会根据计算机上安装的.NET Framework版本设置相应的编译器目录，如图所示。

![](https://images.seebug.org/content/images/2020/06/50eeb861-ac65-4874-bfc0-d66db00c4464.png-w331s)
用于在计算机上编译C＃代码的宏代码

  1. 它使用csc.exe和命令行参数“-target：winexe -out：”编译代码。编译后的二进制文件将出现在“启动”目录中。

  2. 它将删除包含源代码的工作目录。

  3. 它执行编译的二进制文件。

## AppLocker绕过

在这种情况下，MSbuild.exe使用.csproj文件编译计算机上的代码，以此作为绕过Windows安全机制（例如AppLocker和Device
Guard）的方法。几年前，[凯西·史密斯](https://twitter.com/subtee)首次公开了这项技术。

## .NET二进制文件分析

**MD5 hash: 4e0f9f47849949b14525c844005bb567  
File name: ServiceHostV1000.exe**

.NET二进制文件的主要子例程如图所示：

![](https://images.seebug.org/content/images/2020/06/a98c1a1e-3890-4f77-b1f2-47f20c215f55.png-w331s)
.NET二进制文件的主要子例程

下面是此.NET二进制文件执行的主要操作：

它将HTTP GET请求发送到URL：misrmarket[.]xyz/files/app-provider/getApp，并将Content-type请求设置为：“application/json”。

下图显示了来自服务器的响应的内容，其中包含一个JSON文件。

![](https://images.seebug.org/content/images/2020/06/72f0a961-f346-4900-9fa4-56aa13e92ff6.png-w331s)
包含JSON数据的服务器响应

此JSON文件包含三个键：

版本：设置为null

csproj：包含编译C＃项目时msbuild.exe使用的项目文件

cs：包含在运行时需要编译的C＃代码。

  1. C＃代码使用 DataContractJsonSerializer类来解析服务器响应。.cs和.csproj文件被放置在%USERPROFILE%\ServiceTaskV1001位置，文件被命名为w.cs和w.csproj。

  2. 为了编译C＃代码，它使用msbuild.exe。在计算机上检查以找到msbuild.exe的.NET Framework3.5和4.0.x版本，如下图所示：

![](https://images.seebug.org/content/images/2020/06/1d86873a-851f-4bf1-b997-c6965cbe8ecc.png-w331s)
.NET Framework版本的代码部分

## 基于.NET的RAT分析

有效负载的MD5 Hash值：8f62d7499d5599b9db7eeddf9c01a061

**系统信息收集**

有效负载执行的第一个活动是收集有关系统的信息，如图所示：

![](https://images.seebug.org/content/images/2020/06/ca2a61f4-3291-440a-8a56-2fcd5ea5994b.png-w331s)
用于收集系统信息的代码部分

从计算机收集有关以下属性的信息：

  * bot ID：机器的唯一标识符

  * CPU名称：处理器详细信息

  * RAM –计算机上安装的RAM总量

  * 用户名

  * 主机名

  * 系统驱动器名称

  * 系统目录路径

  * 正常运行时间

  * 操作系统类型：此字段设置为Windows。

计算唯一bot ID：有效负载首先计算机器的唯一标识符，它使用机器的各种属性来计算这个ID，如下所示:

a = WMI查询输出一个“SerialNumber”字段：SELECT * FROM Win32_DiskDrive

b = WMI查询输出字段：SELECT * FROM Win32_Processor

c = WMI查询输出中的“Manufacturer”和“SerialNumber”字段：SELECT * FROM Win32_BaseBoard

d = WMI查询输出“Manufacturer”字段：SELECT * FROM Win32_BIOS

通过链接上述所有值（a，b，c和d），然后计算MD5的Hash值并使用所得MD5的Hash值前12个字符来计算最终ID。

可以表示为：MD5(a+b+c+d)[0:12]

加上整数15以以生成最终ID。

一旦从机器上收集了以上信息，它就会以HTTP POST请求的形式发送到服务器，如图所示:

![](https://images.seebug.org/content/images/2020/06/511009d6-cc39-48c3-9c95-5353162954c9.png-w331s)
代码部分，用于在命令与控制（C＆C）服务器上注册bot

该请求将发送到URL：hxxp://theashyggdrasil[.]xyz/api/clients/identifyClient， 并且Content-Type字段设置为“application/json”。感染后的第一个网络请求用于使用具有唯一标识符的bot向攻击者的服务器注册。

网络请求如图所示:

![](https://images.seebug.org/content/images/2020/06/25d5796d-5a65-4452-bdef-a07024a53db9.png-w331s)
在HTTP POST请求中发送到C＆C服务器的系统信息

## C＆C

僵尸程序在服务器上注册后，它将GET请求发送到以下路径：`/api/orders/getOrders/<bot_id>`以获取需要在机器上执行的命令。服务器响应将采用bot解析的JSON格式。

处理C＆C通信的子例程如图所示:

![](https://images.seebug.org/content/images/2020/06/0cc91d1b-4eee-43ed-a9aa-6c66401b9776.png-w331s)
处理C＆C通信的子例程

该程序支持四种操作，如下所述：

cmdExec：此操作允许攻击者在计算机上执行代码。通过解析JSON响应，检索两个成员的CmdReq结构，shellId命令。

cmdExec操作的子例程如图所示：

![](https://images.seebug.org/content/images/2020/06/e9f38b0c-84b4-4563-aea8-30eb2ae4bcb5.png-w331s)
处理cmdExec命令的子例程

如果命令等于`***reset*shell***`，则会在计算机上生成cmd.exe的新实例，如图所示:

![](https://images.seebug.org/content/images/2020/06/1f51b590-fccc-44e0-96d8-71c9db4f53f8.png-w331s)
用于产生新外壳的子例程

对于任何其他命令，将使用同一外壳程序执行。

**getDir** ：此命令可以检索计算机上特定路径中存在的所有文件的完整列表。

![](https://images.seebug.org/content/images/2020/06/c38bf647-70d3-42ac-aa99-ecc06dcf39d0.png-w331s) 处理getDir命令的子例程

此信息将通过HTTP GET请求泄漏到服务器，该请求的路径为：`/api/files/onGetDirRun`

**uploadFile** ：此命令用于将文件从计算机上的给定路径上载到攻击者的服务器，如图所示:

![](https://images.seebug.org/content/images/2020/06/1b8a3c80-c040-4580-9883-4fede02b3397.png-w331s)
处理uploadFile C＆C命令的子例程

AwsInfoRes是具有两个成员的类：

  * uploadUrl

  * fileKey

通过将HTTP GET请求发送到以下路径来从服务器检索此信息：/api/assets/getAwsUploadUrl

从JSON响应中，提取uploadURL和fileKey值,通过将HTTP
PUT请求发送到AwsInfoRes对象的uploadURL成员定义的URL中，对文件进行提取。

**getScreenshot** ：此命令使攻击者可以远程获取计算机的屏幕截图，如图所示：

![](https://images.seebug.org/content/images/2020/06/3ca7819a-f9bd-4bc7-aae4-a0b241558a80.png-w331s)
处理getScreenshot命令的子例程

## QuasarRAT代码重叠

.NET二进制文件中有一小段代码，其代码与QuasarRAT重叠。重叠仅与QuasarRAT的StringHelper类一起使用。

下图显示了.NET二进制的部分代码
![](https://images.seebug.org/content/images/2020/06/a69a2325-10a9-4f5d-bdf6-988e158b7369.png-w331s)
与QuasarRAT重叠的代码部分

这些功能与QuasarRAT中的[StringHelper](https://github.com/quasar/QuasarRAT/blob/3aed553e1aa8cb506dec96125d2fe2c9f6fd8dc2/Quasar.Common/Helpers/StringHelper.cs#L7
"StringHelper")功能类似。但是，在这种情况下，.NET二进制文件中不会调用其中的大多数功能。

## 云沙箱检测

下图显示了[Zscaler Cloud
Sandbox](https://www.zscaler.com/products/sandboxing)成功检测到此基于文档的威胁。
![](https://images.seebug.org/content/images/2020/06/e31359c9-1d2f-4c54-b509-5619c0d5dc41.png-w331s)
Zscaler Cloud沙箱检测

除了检测沙箱外，Zscaler的多层云安全平台还可以检测各个级别的指标，如下所示：
[Win32.RAT.ShellReset](https://threatlibrary.zscaler.com/threats/c4175119-c135-424a-bce0-2d6dea559e9e)

## 结论

黑客们利用与当前事件（例如会议和展览）相关的主题来传播基于宏的恶意文档。用户应在打开此类文件之前要验证其来源。

作为额外的预防措施，用户不可随便因为未知来源的Microsoft Office文件启用宏，因为这些宏可以在计算机上随意执行恶意代码。

Zscaler ThreatLabZ团队将继续监视此攻击以及其他攻击，以帮助确保客户安全。

## MITRE ATT&CK TTP Mapping

![](https://images.seebug.org/content/images/2020/06/8387c5cd-3ede-4fe7-aae9-430421dcbf28.png-w331s)

## IoCs

**Hash**

93f913f3b9e0ef3f5cedd196eae3f2ae  
b34b74effbd8647c4f5dc61358e1555f  
7bebf686b6e1d3fa537e8a0c2e5a4bdc  
1d94b086996c99785f78bf484295027a

**托管文档的URL**

hxxps：//documentsharing.space/files/5G%20Expo.doc？clientEmail =  
hxxps：//documentsharing.space/files/FutureBuild.doc？clientEmail =  
hxxps：//misrmarket.xyz/files/Get%20Stared.doc  
hxxps：//consumerspost.xyz/files/Swissin-Voucher.doc

**用于下载下一阶段的URL**

hxxps：//misrmarket.xyz/files/app-provider/getApp  
hxxps：//misrmarket.xyz/files/app-provider/getLatestVersion  
hxxps：//centeralfiles.xyz/files/app-provider/getApp  
hxxps：//centeralfiles.xyz/files/app-provider/ getLatestVersion

**感染后域**

theashyggdrasil.xyz

**感染后域中使用的API端点**

/ api / cmd / onCmdRun  
/ api / clients / identifyClient  
/ api / assets / onCreated  
/ api / assets / getAwsUploadUrl  
/ api / files / onGetDirRun  
/ api / orders / getOrders /

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1228/>

