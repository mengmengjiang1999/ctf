**7月份，我们发现了一个伪装成新订单通知的钓鱼邮件，里面带有一个恶意附件，会导致Remcos RAT（被Trend
Micro检测为BKDR_SOCMER.SM）这一恶意软件的执行。该攻击方式使用AutoIt对其进行封装和传播，并且使用了多种混淆和反调试技术来规避检测。**

Remcos
RAT的出现最早可以追溯到2016年，当时在黑客论坛里作为一种有偿服务进行广告和销售，曾经很多网站和论坛还提供该工具的破解版本。直至今日，Remcos仍然是网络罪犯们的常用工具并不断推动着其发展。在2017年，我们发现了一个通过恶意PowerPoint幻灯片传播Remcos的样本，该样本还内置了编号为CVE-2017-0199漏洞的利用方法。最近，Remcos又开始使用钓鱼邮件进行大肆传播了。

钓鱼邮件背后的恶意攻击者使用rud-division@alkuhaimi[.]com（合法域名）这个邮箱和“RE: NEW ORDER
573923”的主题。邮件中包含的恶意附件使用ACE压缩的文件格式，“Purchase
order201900512.ace”，可以通过Boom.exe进行加载和封装。

##  封装器/加载器分析

可执行文件转换成AutoIt脚本之后，我们发现恶意代码被多重混淆保护了，有可能是为了规避检测，同时增大研究人员对其进行逆向的难度。最顶层的混淆方法如下所示：

![](https://image.3001.net/images/20190826/1566783506_5d63381207021.png!small)

图1混淆后的关键函数

![](https://image.3001.net/images/20190826/1566783555_5d633843ada06.png!small)

图2 去混淆使用的函数

Boom.exe的主要目的是为了实现持续性，以及进行反分析检测和在已感染系统种释放/执行Remcos
RAT。上面的代码片段首先计算出数组内的值，然后使用ChrW()函数将Unicode数字转化为ASCII码字符.

![](https://image.3001.net/images/20190826/1566783602_5d633872a094b.png!small)

图3 字符串解码样例

在一些情况种，该恶意软件在解密后会使用AutoIt的BinaryToString()函数对下一层混淆进行去混淆。下面的代码片段展示了这一行为：

![](https://image.3001.net/images/20190826/1566783650_5d6338a20a9ed.png!small)

图4 使用AutoIt函数将二进制解码为字符串

去混淆之后的AutoIt代码种可以看到大量的垃圾代码，意在分散分析人员的精力。

![](https://image.3001.net/images/20190826/1566783698_5d6338d29a210.png!small)

图5 垃圾代码示例

该恶意软件之后会对自身进行复制，复制到%AppData%\Roaming\appidapi\UevTemplateBaselineGenerator.exe下，然后从其资源段种加载主要载荷（Remcos
RAT）。该恶意软件接下来会准备执行主要载荷的环境，通过执行以下Shellcode来实现（frenchy_shellcode version 1）

![](https://image.3001.net/images/20190826/1566783774_5d63391e8091e.png!small)

图6 Frenchy_ShellCode_001

![](https://image.3001.net/images/20190826/1566783868_5d63397cda2ad.png!small)

图7 执行与解码Frenchy Shellcode

![](https://image.3001.net/images/20190826/1566783899_5d63399b4bfd9.png!small)

图8 Frenchy Shellcode变体

从资源中解码并加载Remcos

DecData()函数从其资源段中加载数据，然后对所有数据进行逆序，并用“/”替换“%$=”。

![](https://image.3001.net/images/20190826/1566783963_5d6339db402ab.png!small)

图9 使用AutoIt解码主要载荷：代码+编码过的资源

![](https://image.3001.net/images/20190826/1566783994_5d6339fa5649c.png!small)

图10 AutoIt解码主要载荷：只有代码

然后使用以下代码对PE文件进行base64解密，该PE文件即为主要载荷：

    
    
    $a_call = DllCall(“Crypt32.dll”, “int”, “CryptStringToBinary”, “str”, $sData, “int”, 0, “int”, 1, “ptr”, 0, “ptr”, DllStructGetPtr($struct, 1), “ptr”, 0, “ptr”, 0)

![](https://image.3001.net/images/20190826/1566784039_5d633a27b8d50.png!small)

图11 从AutoIt中解码Remcos

##  加载器功能

###  反虚拟机

该AutoIt加载器能够通过检查正在运行的进程列表中是否包含vmtoolsd.exe和vbox.exe来检测虚拟机环境。但是，值得注意的是这一功能在该样本中并未被调用。

![](https://image.3001.net/images/20190826/1566784101_5d633a658799d.png!small)图12
AutoIt加载器的反虚拟机代码

###  UAC绕过

根据Windows版本，该恶意软件会选择使用内置的Event Viewer组件 （eventvwr）或fodhelper来绕过用户账户控制（UAC）。  
![](https://image.3001.net/images/20190826/1566784199_5d633ac74a500.png!small)

图13 UAC绕过

###  反调试

如果加载器检测到了系统API的IsdebuggerPresent返回值为1，会显示“This is a third-party compiled
AutoIt script.”的消息，并退出程序。

![](https://image.3001.net/images/20190826/1566784261_5d633b0572ae9.png!small)

图14 AutoIt加载器检查调试器是否存在的代码

##  Remcos RAT主要载荷

Remcos
RAT本来是作为一个让用户远程控制系统的正规合法的远程访问工具进行销售的，但最近却成为了网络罪犯的犯罪利器。一旦该RAT被执行，入侵者就有能力在用户的系统中执行远程命令。比如，在之前的宣传中，就说明该工具具有多功能性的特点，包括下载并执行命令，键盘记录，屏幕记录以及使用摄像头和麦克风进行录音录像等功能。

为了分析这一载荷，我们研究了Remcos Professional 1.7版本的样本。

![](https://image.3001.net/images/20190826/1566784341_5d633b557ffc3.png!small)图15
Remcos版本

在执行时，该恶意软件会根据配置生产一份自身的拷贝并放在%AppData%\remcos\remcos.exe中，使用install.bat脚本在%APPDATA%目录下执行remcos.ex$，最后进行自身删除。之后会在注册表中创建以下Run键值从而保证在系统中持久驻留。

![](https://image.3001.net/images/20190826/1566784406_5d633b960561a.png!small)

图16 Remcos释放的Install.bat

![](https://image.3001.net/images/20190826/1566784449_5d633bc180d13.png!small)

图17 Remcos RAT更改注册表项实现驻留

![](https://image.3001.net/images/20190826/1566784484_5d633be49e3b2.png!small)

图18 Remcos RAT代码中对注册表的更改

该恶意软件会从其资源段中提取名为“SETTING”的配置。

![](https://image.3001.net/images/20190826/1566784518_5d633c068d9f7.png!small)

图19 Remcos从其资源中加载加密配置

配置文件的内容使用RC4加密算法进行加密，如下：

![](https://image.3001.net/images/20190826/1566784582_5d633c46e19d0.png!small)

图20 Remcos加密配置

以下是用来解密上述配置的RC4解密算法：

![](https://image.3001.net/images/20190826/1566784625_5d633c71612a1.png!small)

图21解密配置的RC4算法

![](https://image.3001.net/images/20190826/1566784672_5d633ca04bf0d.png!small)

图22 解密配置

之后，该恶意软件会创建以下mutex来标记已在系统中存在：

![](https://image.3001.net/images/20190826/1566784706_5d633cc2d6fc5.png!small)

图23 Remcos RAT mutex

然后，开始收集系统信息，例如用户名，计算机名，Windows版本等，并将这些信息发送到C&C服务器。该恶意软件使用RC4算法对收集的信息进行加密，加密使用的密码“pass”也是从配置文件中取得的。

![](https://image.3001.net/images/20190826/1566784746_5d633ceae6b14.png!small)

图24 Remcos收集系统信息

以下列表展示了该恶意软件支持的一些命令：

![](https://image.3001.net/images/20190826/1566784821_5d633d353ca7a.png!small)

表1 Remcos RAT命令

在分析了这个Remcos变种之后——其配置文件，通信机制和功能分析——我们发现该样本和之前版本的变种（被检测为Backdoor.Win32.Remcosrat.A）有很多相似之处。但是这个特殊的样本使用AutoIt对Remcos进行封装，并使用了不同的混淆和反调试技术来规避检测。

##  **预防措施和解决方案**

为了防御类似Remcos
RAT等基于邮件的攻击方法，我们建议用户避免打开来历不明的邮件——尤其是那些带附件的——来自未知发件人的。用户也需要在点击URL之前三思，以防感染恶意软件。而对于企业来说，如果怀疑系统中存在异常行为，那么需要马上向网络管理员汇报。我们也建议以下额外的防护措施：

> 1、了解如何鉴别钓鱼邮件，掌握恶意邮件的特征（如错别字，生僻字等）
>
> 2、经常更新应用和系统
>
> 3、使用白名单，屏蔽用不到的端口，禁用用不到的组件
>
> 4、监控系统中流量以发现异常行为

##  IoCs

![](https://image.3001.net/images/20190826/1566784957_5d633dbde367e.png!small)

***本文作者： Kriston，转载请注明来自FreeBuf.COM**  

