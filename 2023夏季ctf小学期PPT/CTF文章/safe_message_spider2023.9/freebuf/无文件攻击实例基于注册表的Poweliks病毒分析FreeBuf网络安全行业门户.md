## 前言：

**病毒与杀软的博弈持续进行着，双方的攻防技术也是日新月异，随着杀软杀毒能力的不断提升，病毒对抗也在持续加强，无文件攻击作为一种比较新型的攻击手段，正逐步扩大其影响力。**

千里目安全实验室EDR安全团队发现，
从2016年至今，所有重大的APT事件中，有77%的组织采用了无文件的攻击方式进行入侵，再纵观这三年，无文件的攻击方式也越来越流行：

![图片.png](https://image.3001.net/images/20180420/15241904057451.png!small)  
（图片来自Gartner的演讲Get Ready for 'Fileless' Malware Attacks）

近日，我们捕获了一个poweliks病毒样本，此病毒家族就是一个典型的基于注册表的无文件攻击实例。为了对此类攻击有更直观且全面的了解，我们研究分析poweliks病毒，来梳理无文件式攻击的整体流程。Poweliks是著名的无文件式攻击病毒，其后出现了多个版本的变种，其采用了注册表、powershell、进程注入这三种无文件攻击方式来对主机进行隐蔽性攻击，由于行为很隐蔽，所以其很难被杀软所查杀。

##  **病毒原理：**

![图片.png](https://image.3001.net/images/20180420/15241904112318.png!small)  

Poweliks.exe为此病毒的母体，
poweliks.exe首先修改注册表，然后调用rundll32.exe执行powershell脚本（包含恶意代码），powershell脚本首先创建一个合法进程dllhost.exe（此文件在C:\Windows\System32目录下），然后将恶意代码注入到此进程中并执行（躲避杀软查杀）
，达到与C&C服务器通信的目的。最后，当系统每次重启时，都会自动运行注册表里的恶意代码，实现持久化攻击。

双击Poweliks.exe（病毒母体），运行情况如下：

![图片.png](https://image.3001.net/images/20180420/15241904165279.png!small)  

## **技术分析：** ****

Poweliks病毒一般是通过邮件的方式进行传播的，在邮件里面包含一个恶意的word文档，一旦打开这个word文档，它将会执行恶意代码并运行Poweliks病毒。

病毒主流程如下：

![图片.png](https://image.3001.net/images/20180420/15241904203462.png!small)  

以下是C&C服务器的地址及HTTP请求的格式

![图片.png](https://image.3001.net/images/20180420/15241904259929.png!small)

![图片.png](https://image.3001.net/images/20180420/15241904301341.png!small)

![图片.png](https://image.3001.net/images/20180420/15241904344977.png!small)

Poweliks.exe接着向注册表默认启动项键值（HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\\(Default)）中写入两条恶意代码：

写入第一个恶意代码（调用rundll32.exe读取run键值里的jscript代码并执行）

![图片.png](https://image.3001.net/images/20180420/15241904404422.png!small)  

这段代码由于是使用Unicode编码的，所以使用regedit.exe打开会报错误，使用常规的方式删除不了此注册表键：  

![图片.png](https://image.3001.net/images/20180420/15241904677654.png!small)  

写入第二个恶意代码（被调用执行的Jscript代码）

![图片.png](https://image.3001.net/images/20180420/15241904731997.png!small)

![图片.png](https://image.3001.net/images/20180420/15241904789943.png!small)  

然后在Run项下创建创建一个Unicode字符的项：

![图片.png](https://image.3001.net/images/20180420/15241904822398.png!small)  

这里的目的也是为了使用户在打开regedit.exe打开的时候出现报错，防止用户删除恶意的注册表项：

![图片.png](https://image.3001.net/images/20180420/15241904906226.png!small)

我们现在回过头来看看jscript的关键代码

![图片.png](https://image.3001.net/images/20180420/15241904954211.png!small)

![图片.png](https://image.3001.net/images/20180420/15241904999797.png!small)  

这段代码的主要功能是调用powershell执行一段base64加密后的代码，将powershell代码解密，发现其中继续调用了一段加密代码，解密后发现是一段恶意的二进制shellcode。

![图片.png](https://image.3001.net/images/20180420/1524190505718.png!small)  

然后，poweliks.exe调用进程poweliks.exe:0进行自删除：

![图片.png](https://image.3001.net/images/20180420/15241905093789.png!small)

![图片.png](https://image.3001.net/images/20180420/15241905141854.png!small)

![图片.png](https://image.3001.net/images/20180420/15241905195233.png!small)  

poweliks.exe:0进程在删除母体文件poweliks.exe后退出。

最后，遗留在系统中dllhost.exe进程被注入恶意代码后做了两个操作，连接C&C服务器和监控注册表，确保自己的恶意代码不会被删除：

![图片.png](https://image.3001.net/images/20180420/15241905309577.png!small)

![图片.png](https://image.3001.net/images/20180420/15241905335048.png!small)

## **处理方法：**

> 1\. 结束进程dllhost.exe
>
> 2\.
> 使用PCHunter删除注册表相应的恶意键值，即删除默认键对应的值。（HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\默认）

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

