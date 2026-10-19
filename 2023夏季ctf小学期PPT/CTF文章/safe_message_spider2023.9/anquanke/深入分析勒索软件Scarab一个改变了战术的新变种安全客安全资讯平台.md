# 深入分析勒索软件Scarab：一个改变了战术的新变种

阅读量 **199838**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-02-02 16:30:43

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Malwarebytes Labs ，文章来源：blog.malwarebytes.com

原文地址：<https://blog.malwarebytes.com/threat-analysis/2018/01/scarab-ransomware-new-variant-changes-tactics/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t016c2b5e2895bf4109.jpg)

## 前言

Scarab（圣甲虫）恶意软件于2017年6月首次发现。此后，有多个版本的变种陆续产生并被发现。最流行的一个版本是通过Necurs僵尸网络进行分发，使用Visual
C语言编写而成。但是，在针对多个变种进行脱壳之后，我们发现有一个2017年12月首次发现的变种Scarabey，其分发方式与其他变种不同，并且它的有效载荷代码也并不相同。  
如同其他大多数勒索软件一样，Scarabey会将系统中的文件进行加密，并勒索比特币赎金。然而，Scarabey并没有像原来的Scarab那样通过内部的malspam进行分发，而是针对特定的俄罗斯用户群体，并通过RDP或手动的方式分发到服务器和系统上。  
另外，Scarabey与此前我们发现的任何样本都不相同，其恶意代码是由Delphi编写的，没有Scarab所具有的C++包装，并且勒索赎金的提示内容和使用语言也与其他样本完全不同。

    
    
    Scarab原始样本MD5：e8806738a575a6639e7c9aac882374ae
    Scarabey变种样本MD5：9a02862ac95345359dfc3dcc93e3c10e

## 勒索赎金的提示

针对感染者而言，Scarabey和其他Scarab勒索软件的主要区别在于勒索赎金提示信息的语言，以及加密信息中所使用的恐吓手段。  
在Scarab样本中，勒索赎金的提示信息是英文，但如果仔细阅读，会发现它似乎是从俄文逐字翻译成英文的，其中一些地方并没有遵循正确的英语语法或习惯表达。而Scarabey的提示信息直接就是俄语。非常有趣的是，如果我们将Scarabey的俄语提示内容复制粘贴到谷歌翻译中，所得到的机翻英语内容，包含与Scarab勒索提示信息相同的语法错误，如下图所示。  
原始的Scarab提示信息：  
  
使用谷歌翻译，俄译英后的Scarabey提示信息：  
  
我们认为，Scarab勒索软件的作者可能使用俄语，他使用自己的母语写了勒索提示信息，并通过在线翻译将其转换成英语，并放入了Scarab勒索软件之中。如果真是这样，该作者很可能为了能够感染更多的用户，使用自己的母语制作了Scarabey勒索软件，并将其瞄准俄罗斯用户这一特定人群。

## 不同的威胁提示内容

在最初的Scarab版本中，它警告用户说：用户支付赎金所耗费的时间越久，价格就会越高。  
而在Scarabey中，它警告用户：在不支付赎金的情况下，文件会不断被删除，直至所有文件都被彻底删除，且无法恢复。  
但经过深入分析，攻击者自称被感染用户他们保留了未加密的副本，或者暗示被感染用户他们能够控制被感染用户的计算机，这些都是骗人的。具体原因如下：

  1. 攻击者并不会保留未加密文件的副本，也没有任何途径将这些文件发送到被感染用户的计算机上。同样，也无法将任何文件从受感染计算机发送给勒索软件作者。
  2. 在Scarab及其变种，不存在后门或远程访问相关的代码，因此攻击者无法在被感染的计算机上远程删除文件。
  3. 根据我们的理解，在用户支付赎金后，攻击者会向被感染用户发送拥有唯一密钥的解密软件。用户运行该软件，可以解密电脑中的文件。这也就是说，攻击者无法控制解密的过程，因为解密过程是在被感染者主机本地、在离线状态下完成的。
  4. 根据对恶意软件代码的分析，不存在删除用户文件的相关功能。

具体来说，在勒索提示信息中，作者声称文件是在服务器端被加密，这是不真实的：

>
> “如果您不支付赎金，每隔24小时我们就删除24个文件（我们具有文件的副本）。如果在72小时之内没有运行解密程序，计算机上的所有文件都将被彻底删除，无法再恢复。”  
>  然后，恶意软件的作者给出了解密步骤，在被感染用户付款后，会收到一个解密程序，带有唯一密钥的解密软件可以在本地执行解密操作：  
>  “运行解密软件后，文件会在1小时之内被解密。”  
>  “每个解密软件中都包含唯一的密钥，无法使用其他用户的解密器为您的数据解密。”

通过我们的分析，我们认为：恶意软件作者通过诈称“会删除文件”，促使用户快速支付赎金。

## 技术分析

通过比较Scaraby和Scarabey，我们发现Scarabey这一变种明显是使用俄语编写的，并且明显针对俄罗斯用户，但是原作者可能是同一人。从代码上来分析，这两个恶意软件的变种几乎是每个字节都相同。另外，Scarab和Scarabey所生成的子进程，所投放的文件、使用的加密方法和使用的互斥量都是相同的。正是由于上述原因，我们才认为Scarabey是一个变种，而不是一个新的家族。  
下图展现了两个恶意软件变种的输出。唯一不通的是代码和内存数据所引用的地址（用黄色和红色标出）。  

## 代码分析

Scarabey变种是用Delphi语言编写的。运行后，首先会检查自身是否为第一次运行。具体来说，先会检查是否已经传入了参数。如果没有，则检查是否已经设置了以下注册表项：

    
    
    SoftwareILRTISoidle
    

  
如果没有设置注册表项（意味着是第一次运行），勒索软件接下来会检查SEVNZ是否已经被创建，并使用下面的命令利用命令提示符将自身复制到临时目录下，并命名为sevnz.exe：

    
    
    cmd.exe /c copy /y C:UsersvirusLabDesktop9a02862ac95345359dfc3dcc93e3c10e.exe “C:UsersvirusLabAppDataRoamingsevnz.exe”
    

随后，它会在退出的时候，产生一个带有参数“runas”的进程。  
  
至此，将会由子进程进行接管。  
代码流现在将进入与以前相同的功能，删除SEVNZ并重新复制它。由于参数的传入，它会跳过最开始的步骤，并运行复制后的sevnz.exe：

    
    
    C:Users[username]AppDataRoamingsevnz.exe
    

随后，使用命令行打开cmd.exe进程。

    
    
    “mshta.exe “javascript:o=new ActiveXObject(‘Scripting.FileSystemObject’);setInterval(function(){try{o.DeleteFile(‘9a02862ac95345359dfc3dcc93e3c10f.exe’);close()}catch(e){}},10);””
    

之后开始等待将自身删除，原因在于进程不能在运行时被删除。  
  
现在，我们进入到SEVNZ.exe进程：  
该进程通过尝试删除”…AppDataRoamingsevnz.exe”，来检查它是否以sevnz.exe运行。  
如果失败，它就会知道当前运行的是sevnz.exe，而不是原来的可执行文件。该检查通过后，会使用mtsha.exe来执行JavaScript，将延迟一段时间，并将其自身添加到注册表来自动运行：

    
    
    mshta.exe “javascript:o=new ActiveXObject(‘WScript.Shell’);
    x=newActiveXObject(‘Scripting.FileSystemObject’);
    setInterval(function(){try{i=x.GetFile(‘sevnz.exe’).Path;
    o.RegWrite(‘HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce\ILRTISo’,i);}
    catch(e){}},10);
    

接下来，会删除卷影副本（Shadow Volume Copy），这是绝大多数勒索软件都会执行的一个操作，以确保用户无法恢复被加密的文件。

    
    
    —–Executes these scripts with mtsha.exe:—–
    ActiveXObject(“WScript.Shell”);
    o.Run(“cmd.exe /c wbadmin DELETE SYSTEMSTATEBACKUP -keepVersions:0”,0);
    o.Run(“cmd.exe /c wmic SHADOWCOPY DELETE”,0);
    o.Run(“cmd.exe /c vssadmin Delete Shadows /All /Quiet”,0);
    o.Run(“cmd.exe /c bcdedit “
    
    new ActiveXObject(“WScript.Shell”);
    o.Run(“cmd.exe /c wbadmin DELETE SYSTEMSTATEBACKUP-keepVersions:0”,0);
    o.Run(“cmd.exe /cwmicSHADOWCOPYDELETE”0);
    o.Run(“cmd.exevssadminDeleteShadows /All/Quiet”,0);
    o.Run(“cmd.exe /c bcdedit /set {default} recoveryenabled No”,0);
    o.Run(“cmd.exe /c bcdedit /set {default} bootstatuspolicy ignoreallfailures”,0);
    

随后，打开一个始终循环的线程，并确保没有“关键进程”正在运行。如果发现“关键进程”存在，将会关闭这些进程。原因在于，这些进程可能会锁定一些勒索软件本来想要加密的文件。这些“关键进程”是在一个字符串中定义的：

    
    
    agntsvc.exe
    isqlplussvc.exe
    ncsvc.exe
    msftesql.exe
    sqlagent.exe
    sqlbrowser.exe
    sqlservr.exe
    sqlserver.exe
    sqlwriter.exe
    oracle.exe
    ocssd.exe
    dbsnmp.exe
    synctime.exe;
    mydesktopqos.exe
    agntsvc.exe
    isqlplussvc.exe
    xfssvccon.exe
    mydesktopservice.exe
    ocautoupds.exe
    agntsvc.exe
    agntsvc.exe
    agntsvc.exe
    encsvc.exe
    firefoxconfig.exe
    tbirdconfig.exe
    ocomm.exe
    mysqld.exe
    mysqld-nt.exe
    mysqld-opt.exe
    dbeng50.exe
    sqbcoreservice.exe

在加密函数的主循环中，会在整个代码中进行对互斥量的持续检查，如果它存在，将会作为清除自身并从系统中移除的标志：  
互斥量：STOPSCARABSTOPSCARABSTOPSCARABSTOPSCARABSTOPSCARAB。  
加密循环可以被代码中的许多部分调用，但最初运行并主要执行加密操作的部分如下：  
  
随后，递归遍历所有文件夹进行检查，确保扩展名不是.exe或.dll。如果检查无误，将会加密文件，并使用.scarab扩展名对其进行重命名。  
使用POS()检查当前文件扩展名是否为.exe或.dll：  
  
加密代码不直接使用任何加密API。相反，AES代码嵌入在恶意软件之中，如上图所示。  
一些可以调用主加密函数的地方：  

## 加密算法

目前，我们已经确定加密算法是AES。在读取实际的文件数据之前，勒索软件首先会将一个4字节的块（0xDEFACE01）添加到缓冲区中。这可能是盐（Salt），也可能是恶意软件作者用于迷惑研究人员所执行的一个操作。它会使用生成的字节来执行一些数据处理操作，可能是创建随机的初始化向量。  
在AES加密前的IV 生成器函数：

  
异或后的数据被传递到IV的MAIN_AES_LOOP_FUNCTION，其中var_8是加密密钥：

  
恶意软件会继续通过AES_ALGO标记的函数，在数据上执行AES 256加密算法。我们是根据其中的一些特征判断使用的是AES 256加密。  
加密使用了16个字符的块，这是非常标准的AES加密，每次会加密文件中的16个字符，即128位。  
AES加密算法不同版本之间的区别在于密钥的大小和加密轮（Encryption
Round）次数。在该勒索软件中，使用了AES246标准中的14轮，而没有使用AES128标准中的10个。密钥大小为256位（32个字节或字符）。  
密码分组链接模式（Cipher Block
Chaining，CBC）也被使用。在这里，CBC主要是使用之前的密文来加密下一个明文块。换而言之，先前的加密块会被用作下一个数据块的初始化向量。  
AES CBC的流程，先使用IV，接下来使用先前的密文作为IV：

  
在这种情况下，作为初始化步骤，IV中的字节会与待加密原文进行异或操作，以保证有更强的随机性。如下图所示，AES的输出将会被复制到循环开始处所使用的变量中，以在执行AES加密操作之前初始化下一个明文块。在这里，尽管并没有通过加密API调用，但还是清楚地说明了AES的用法。  
下图展现了以前的密文被用作IV，其中var_28包含加密的数据：

![](https://blog.malwarebytes.com/wp-content/uploads/2018/01/screenshot11.png)

下面展示了一些算法相关的截图。数据被加载到矩阵中，随后会对硬编码的数据以及加密密钥所在字节执行一系列数据操作。在下图突出显示的是一轮中的一组操作（共进行4组）。其中4组共同构成一轮。为了执行对矩阵的数学运算，需要对矩阵中的每个项目执行操作。如前文所述，共有14轮。

  
编码的加密密钥保存在注册表的“temp”键中：

  
如果在注册表中找到该密钥，那么就会继续执行函数，将注册表中的密钥解码为原始加密密钥。否则，会跳转到新的生成函数。

  
这是勒索软件对文件进行加密的关键所在。其格式类似于支付赎金提示中的密钥，但这一个更长，是保存在注册表中加密版本的用户ID标识。一个转储后键值的示例如下：

    
    
    [HKEY_CURRENT_USERSoftwareILRTISo]
    "temp"="VkIAAAAAAADpt9Q2lAzhCExfqjLoD3vSpluc678N56Zn8b7LVRxMi1ZsYk2HXD1e4s3tiefTmZJAc0vxPposvLzP0yaCh5+KRQm60U0EkzeB2NXetarabUFYgJxb8QRsygKaOqBriC4Bs4ajM24h=e2CsVNP9R3q==UXNmfRFGIsv7NR9BIxE35bdoFpTU8rMGQ14MeQcAii1iY7GpNoY3b4DOgfuKGo3qNC1MYKYdfpn0dbiow3f7ZQGClpwTZ0shFhkWk7aTA7TM1prtgJte7TWe=ERHg8GaFrZtVs9ylNTYPt5CmzHBdAIaXeKZvZnSSafbi83o9gLgAS1OxAb7LBtJpZAJDyBkuyJFR4dFbXztponIBKT1OjtTvTMy07+0B4jI3=K1QGuKSROjAdCF06TsjKWlvUw0iUHRGasz946H3Mnxu3GdCHrAp9Cd94bMo1x1PVdIi3bXSwobjgOlJgJPJC4Y6J4QIE=e45PDNzdK6aCY0uiQ0jOD=8lDWTp=+r+dbGJrJ12qn8CRnBwaFIpyNjDhzdMdTwyvExCmuOesOLms8S7TRoV1GcTyWJAQpSJYcR66H6CngM5GHopdpoTH4mWVOOYp5HFHTDAvMafomF2S6xEmUgXIcKpB7oNohO+Wx0cUmf95=+9uozHMBWE4kFhj+OOKw0I7w7HnwYfafhxsw0CmoOvorZztXk8whlh1d4U26z=aJ6JwH8wVBSszsRLQ+H4y3bRaeupq5Vo+smDfigjVVzCam4HoAdOKzN9MWiigl9Oi+4vTkSFFazc6HzyVaHg8luKGBJMhi2FNHTFO56RA"
    

在支付赎金提示信息中提供的密钥如下：

    
    
    +4IAAAAAAADIGnmIHZL=FYRQCAN=AgKnzw+0uzFbXSR5AdFlfTrhWN9sifnho8LiX5=V8SbNVWyWWrdbTLipFEeeEv=9zLmnid8e
    
    
    
    UqlqKr2RUN=V7LdjoyNwjWMNbylRiGNAKWK6g9exeHhVfUrZ+9oRTq6Kp5eNe7kDdV7UMPVZ12=5pm9a+5lOMw==TNi2R2tUjFcK
    tTD3c9IZgJwOMgcOw3fRrmgaloh5cIV3V74DRy2segx13RDL4J6B+gJnfT2mxIZuBE1G5HcmuLHCoqQif2BamhfbMASCUEpOp7+Z
    G0jI=1PTmOhD3Yq4XjJWI4mc61AruRlaYqwPTUUbrsI0zTYX1mmM3Tvyso8bqDy4h5meyPYuXlgtRj06mtdrGZszb6ObsIT4Fz0O
    Ag=4HgI4VSHA=HAU5yCjZzIIkLhlWGvdAk
    

上述密钥用于对加密文件的过程进行改变。这意味着，两个具有相同内容的文件，在被加密后，所得到的加密文件会不相同。存在一个初始密钥，而所有的子密钥都从该密钥派生。如果只有一个加密密钥用于所有的文件，那么我们就可以在加密过程中的任何一个时刻捕获内存，得到密钥，并使用该密钥来对硬盘上所有文件进行解密。但由于Scarab执行了这一关键的循环，我们就无法借助捕获内存的方式来解密文件了。  
在磁盘加密过程完成之后，勒索软件会调用一个函数，遍历所有网络文件夹和驱动器，例如：VMWare共享文件夹、终端服务、网络驱动器。一旦找到，它也会对这些文件夹中的文件进行加密。  
在上述全部操作都完成之后，它会通过记事本，显示支付赎金的相关提示。

## 传闻

我们看到网上的一些文章指出，Scarabey具有后门的相应功能，允许远程访问被感染主机，并允许在主机上收集敏感数据。根据我们的分析，我们认为上述结论是不正确的。除了加密用户计算机上的文件之外，我们没有发现该勒索软件变种具有任何其他的功能。  
此外，还有人指出Scarab是基于GitHub上的开源勒索软件项目HiddenTear产生的。经过分析，这一点也是不正确的，然而这一错误的观点目前已经被广泛流传。  
Windows的Malwarebytes可以检测到该威胁及其变种，并将其命名为：Ransom.Scarab。

本文翻译自blog.malwarebytes.com [原文链接](https://blog.malwarebytes.com/threat-analysis/2018/01/scarab-ransomware-new-variant-changes-tactics/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **P!chu** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/97261](/post/id/97261)

安全客 - 有思想的安全新媒体

本文转载自: [blog.malwarebytes.com](https://blog.malwarebytes.com/threat-analysis/2018/01/scarab-ransomware-new-variant-changes-tactics/)

如若转载,请注明出处： <https://blog.malwarebytes.com/threat-analysis/2018/01/scarab-ransomware-new-variant-changes-tactics/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [勒索软件](/tag/勒索软件)
  * [Scarab](/tag/Scarab)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t01bd1dba67fe13cdc6.png) P!chu

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

