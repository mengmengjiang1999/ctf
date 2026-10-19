**新冠疫情的发展动态，仍然是全球关注的焦点，目前国外确诊病例已经超过300万，美国确诊病例将接近100万。新冠病毒是我们人类共同面对的“敌人”，在每个国家的共同努力抗疫下，我们终会战胜病毒。**

随着疫情的发展，各行各业都受到严重影响，尽管在如此困难的情况下，不法黑客组织仍然没有放弃网络攻击活动，从疫情一开始我们便追踪到多次利用疫情话题进行攻击的安全事件，在3月初，疑似Kimsuky
APT组织就利用新冠疫情对韩国进行网络攻击，通过投放大量的疫情相关的诱饵文档进行攻击。Kimsuky
APT组织一直针对韩国的智囊团、政府组织、新闻组织和大学教授等发动攻击活动，其使用的C2也常常与这些组织有一定的关联。

近期，亚信安全网络安全实验室关注到疑似Kimsuky
APT组织利用假冒的ESET安全软件更新程序进行信息收集的恶意活动，该文件伪装成ESET更新程序，运行后，会有ESET软件更新成功的窗口提示，诱导用户相信其为正常程序。亚信安全将此文件检测为Backdoor.Win32.KIMSUK.A。

![](https://image.3001.net/images/20200429/1588152333_5ea9480d5b4ff.png!small)![](https://image.3001.net/images/20200429/1588152340_5ea9481483a2e.png!small)

##  病毒详细分析

该病毒首先会创建互斥体GoogleUpdate_01，以防止多次运行。

![](https://image.3001.net/images/20200429/1588152351_5ea9481f54c21.png!small)

该病毒为了免杀，使用的函数、文件、文件路径和注册表名称等全部进行加密处理。

![](https://image.3001.net/images/20200429/1588152359_5ea94827e38a4.png!small)

具体的字符串解密函数中利用了运算指令，程序多次被调用该函数进行解密。

![](https://image.3001.net/images/20200429/1588152368_5ea948308d892.png!small)

![](https://image.3001.net/images/20200429/1588152374_5ea948367ffe7.png!small)

获取要使用的函数地址，主要是网络请求相关模块的函数。

![](https://image.3001.net/images/20200429/1588152383_5ea9483fd3092.png!small)![](https://image.3001.net/images/20200429/1588152387_5ea94843aca9c.png!small)

病毒通过将文件复制到临时目录并且添加启动项进行持久化。然后弹窗提示ESET更新成功，诱导用户。

![](https://image.3001.net/images/20200429/1588152395_5ea9484b751aa.png!small)![](https://image.3001.net/images/20200429/1588152419_5ea94863bc34f.png!small)

根据本机网络信息和系统版本信息生成后续网络请求URL所需要的字段值。

![](https://image.3001.net/images/20200429/1588152433_5ea948715d5e8.png!small)

根据系统版本等信息生成Note字段所需要的值。

![](https://image.3001.net/images/20200429/1588152440_5ea948786c674.png!small)

通过注册表等信息生成域名。

![](https://image.3001.net/images/20200429/1588152447_5ea9487fc9bb0.png!small)

![](https://image.3001.net/images/20200429/1588152455_5ea94887a8272.png!small)

然后通过创建新的线程进行网络请求，通过前面获取的domain+m+NOTE结构组成请求的URL，然后构造HTTP请求结构。

![](https://image.3001.net/images/20200429/1588152465_5ea948918f13a.png!small)![](https://image.3001.net/images/20200429/1588152470_5ea94896e1524.png!small)

![](https://image.3001.net/images/20200429/1588152478_5ea9489ebb14b.png!small)

然后使用GET方法，从远端的服务器请求数据。

![](https://image.3001.net/images/20200429/1588152491_5ea948ab0f4b8.png!small)

请求的数据如下，经过base64解密后，其是收集系统新的命令。

![](https://image.3001.net/images/20200429/1588152497_5ea948b1c04a8.png!small)![](https://image.3001.net/images/20200429/1588152503_5ea948b7ee13b.png!small)

我们注意到请求回来的数据有tiger|等之类的标识。程序会识别这些标识，然后进行不同的行为。如果是tiger标识，将会通过WinExec函数执行cmd指令，通过以上请求回来的数据，我们发现这些指令是收集设备系统，文件以及驱动器等信息。然后将这些信息写入到临时目录中的tmp.LOG文件中，回传给服务器。

![](https://image.3001.net/images/20200429/1588152512_5ea948c049e83.png!small)![](https://image.3001.net/images/20200429/1588152516_5ea948c4d9254.png!small)

通过HttpSendRequestA函数进行信息回传。

![](https://image.3001.net/images/20200429/1588152523_5ea948cb7be01.png!small)

C2服务器返回的数据指令都是通过动物名称命名，该样本也对此进行了解析，除了tiger标识外，还有lion，wolf，monkey，fox和
cat等标识，每个标识对应的处理方式也不一样。

例如monkey标识会通过创建进程的方式执行下载的文件。

![](https://image.3001.net/images/20200429/1588152529_5ea948d14d602.png!small)

如果是fox标识和cat标识等相关的，除了执行文件外将还会对注册表信息进行操作。

![](https://image.3001.net/images/20200429/1588152535_5ea948d7b906f.png!small)![](https://image.3001.net/images/20200429/1588152539_5ea948db97334.png!small)

##  **关联分析**

通过对Kimsuky
APT组织的关联分析，其使用的域名大多数都和政府等组织有关联，本次使用的域名仍然使用包含org相关字段的域名，开源情报平台已经可以对其识别。以前使用过的域名：

![](https://image.3001.net/images/20200429/1588152549_5ea948e58aba9.png!small)

本次使用的域名信息：

![](https://image.3001.net/images/20200429/1588152557_5ea948ed38b2e.png!small)

该组织以往的样本中，通过VBS脚本或者PowerShell命令进行信息收集。本次虽然方式改变，但是信息收集指令没有多大变化，在Windows平台使用dir，systeminfo命令等。

![](https://image.3001.net/images/20200429/1588152570_5ea948fa1f22b.png!small)

![](https://image.3001.net/images/20200429/1588152575_5ea948ffb415f.png!small)

仿冒成软件更新程序这种攻击方式是较为常见的，例如之前有通过伪装成微软的更新补丁的恶意程序，当用户运行后，其会提示补丁安装成功，让用户误以为其是正常的程序。所以我们在使用软件时，要在软件开发商的官方网站下载程序，一般软件的更新程序都会在自身原本的旧版本中进行更新后覆盖，无需额外下载软件操作。尤其是企业用户，当收到相关软件更新的邮件时，更加要谨慎和判断其内容的真实性。

![](https://image.3001.net/images/20200429/1588152589_5ea9490d8bcd5.png!small)

##  **解决方案**

> 不要点击来源不明的邮件以及附件；
>
> 请到正规网站下载程序；
>
> 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> 打开系统自动更新，并检测更新进行安装；

##  **IOC**

**文件Sha-1** |  **文件名称** |  **亚信安全检测名**  
---|---|---  
ae986dd436082fb9a7fec397c8b6e717  |  eset_update.exe  |
Backdoor.Win32.KIMSUK.A  
  
***本文作者：亚信安全，转载请注明来自FreeBuf.COM**

