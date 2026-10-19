**Stealth Falcon黑客组织，自2012年以来一直活跃，其主要目标是中东的政治活动家和记者。citizen
lab机构在2016年发表了一份针对某一网络攻击的分析报告。2019年1月，路透社发表了一份关于“Raven计划”的调查报告，该计划目标与Stealth
Falcon相同。根据这两份关于同一目标和攻击的报告可以看出Stealth Falcon和Raven计划实际上是同一个群体。**

![1.PNG](https://image.3001.net/images/20190911/1568165834_5d784fca7dc2f.png!small)

citizen lab报告中记录的攻击中关键组件是一个基于powershell的后门，该后门通过一个包含在恶意电子邮件中的附件文档进行传播。  

近期发现了一个以前未报告的二进制后门，我们命名为win32/stealthfacon。在本文中，我们将分析介绍新二进制后门和powershell脚本之间的相似之处。这些相似之处证明了win32/stealthfelcon属于Stealth
Falcon黑客组织。  

Win32/StealthFalcon后门是在2015年创建的，允许攻击者远程控制受损的计算机。在阿联酋、沙特、泰国和荷兰发现了该后门。  

## C&C通信  

在与C&C服务器的通信中，Win32/StealthFalcon使用标准的Windows组件Background Intelligent Transfer
Service（BITS）。BITS的设计目的是在不消耗大量网络带宽的情况下传输大量数据，从而不影响其他应用程序的带宽需求。它通常用于更新程序、信使和其他设计为在后台运行的应用程序。

与传统的通过api函数的通信相比，BITS机制是通过com接口，因此安全产品很难检测到。传输因网络中断、用户注销或系统重新启动等原因中断后会自动恢复。此外，由于BITS根据可用带宽调整文件传输速率，因此不会让用户产生怀疑。  

win32/stealthfalcon可以在两个c&c服务器之间切换通信，这两个服务器的地址与其他配置值一起存储在注册表项中，并且可以通过后门命令进行更新。如果后门无法联系到C&C服务器，后门会在多次失败后将自己从受损系统中移除。  

## 后门功能

win32/stealthfalcon是一个dll文件，在执行之后，它将自己设置为用户登录时运行。它只支持基本的命令。  

![1.PNG](https://image.3001.net/images/20190911/1568166138_5d7850fa7da37.png!small)

后门程序的关键功能，下载和执行文件，是通过定期检查执行恶意软件的目录中名为“win*.dll”或“std*.dll”的库并加载这些库来实现的。

此外，win32/stealthfalcon通过在临时文件夹中存储一个带有硬编码前缀的加密副本来收集文件并进行过滤。后门会定期检查这些文件，并自动过滤它们。在文件成功地被过滤后，恶意软件删除所有日志文件和收集的文件，在删除文件之前，它用随机数据重写它们，以防止被分析和恢复删除的数据。  

配置值存储在hkey_current_user\software\microsoft\windows\currentversion\shell
extensions注册表项中。所有值的前缀都是恶意软件的文件名（不带扩展名）。  

![1.PNG](https://image.3001.net/images/20190911/1568166284_5d78518cd608e.png!small)

在任何恶意有效载荷启动之前会有300多个引用，但根本不使用它们，它总是返回并继续执行有效载荷，并且没有条件检查。  
![1.PNG](https://image.3001.net/images/20190911/1568166454_5d785236a0ae7.png!small)![1.PNG](https://image.3001.net/images/20190911/1568166470_5d7852463f3f9.png!small)

## 与Stealth Falcon的联系

Citizen Lab分析中描述的win32/StealthFalcon和基于powershell的后门共享同一个C&C服务器：在Citizen
Lab分析的后门中，地址windowsearchcache[.]com被用作“第二阶段C2服务器域”，在一个版本的win32/Stealt中也是如此。  

这两个后门在代码上都显示出显著的相似性——尽管它们是用不同的语言编写的，但底层逻辑是相同的。两者都使用硬编码标识符（很可能是活动ID/目标ID）。在这两种情况下，来自目标主机的所有网络通信都以标识符为前缀，并使用硬编码密钥用rc4加密。  

对于c&c服务器通信都使用https，并为连接设置特定的标志以忽略服务器证书。  

## 结论

我们发现并分析了一个后门，它采用了一种罕见的C&C通信技术，使用Windows BITS以及一些先进的技术来阻碍检测和分析，代码和基础框架与Stealth
Falcon先前已知的恶意软件相似。以上可知，win32/StealthFalcon后门归属于该黑客组织。

## IoCs  

### SHA-1  

> 31B54AEBDAF5FBC73A66A**1CCB35943CC9B7F72
>
> 50973A3FC57D70C7911F7A952356188B9939E56B
>
> 244EB62B9AC30934098CA4204447440D6F**E259
>
> 5C8F83C**FF57E7C67925DF4D9DAABE5D0CC07E2

### R** keys  

> 258A4A9D139823F55D7B9DA1825D101107FBF88634A870DE9800580DAD556BA3
>
> 2519DB0FFEC604D6C9A655CF56B98EDCE10405DE36810BC3DCF125CDE30BA5A2
>
> 3EDB6EA77CD0987668B360365D5F39FDCF6B366D0DEAC9ECE5ADC6FFD20227F6
>
> 8DFFDE77A39F3AF46D0CE0B84A189DB25A2A0FEFD71A0CD0054D8E0D60AB08DE

### Malware file names  

> ImageIndexer.dll
>
> WindowsBackup.dll
>
> WindowsSearchCache.dll
>
> JavaUserUpdater.dll

### Log file name patterns  

> %TEMP%\dsc*
>
> %TEMP%\sld*
>
> %TEMP%\plx*

### Registry keys/values  

HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Shell Extensions

> X-MRUList
>
> X-MRUData
>
> X-FontDisposition
>
> X-IconDisposition
>
> X-IconPosition
>
> X-PopupPosition
>
> X is the malware’s filename (without extension)

### MITRE ATT&CK  

![1.PNG](https://image.3001.net/images/20190911/1568166898_5d7853f2a8d33.png!small)![1.PNG](https://image.3001.net/images/20190911/1568166916_5d785404c213a.png!small)

***参考来源：[welivesecurity](https://www.welivesecurity.com/2019/09/09/backdoor-stealth-falcon-group/)，由Kriston编译，转载请注明来自FreeBuf.COM **  

