**虽然处于暑期，但sednit组织一直在为zebrocy恶意软件开发新的组件。sednit组织（又称apt28、Fancy Bear、Sofacy
、STRONTIUM）从2004年开始运营，近年来频频登上各大新闻头条。**

2019年8月20日，该组织针对东欧和中亚国家的大使馆和外交部等目标发起了新的攻击活动。攻击活动以一封包含恶意附件的钓鱼电子邮件开始，该邮件启动了一长串下载程序，最后以后门程序结束。

sednit组织针对他们的下载程序添加一种新的开发语言：nim语言。  

## 攻击流程

图1描述了攻击活动复杂的攻击链，从最初在收件箱中收到的恶意电子邮件到部署后门。

![1.PNG](https://image.3001.net/images/20190924/1569334834_5d8a26326e5fb.png!small)

Zebrocy在攻击过程中会有明显的行为特征，在执行最终有效负载之前，受害者至少需要将六个恶意组件安装在计算机上，这将会很容易地被安全产品检测到。

附加到电子邮件的文档为空，但引用了托管在Dropbox的远程模板WordData.dotm。在Word中打开此文档将下载WordData.dotm，如图2所示。

![1.PNG](https://image.3001.net/images/20190924/1569335162_5d8a277ab2921.png!small)

worddata.dotm文件包含恶意宏，它还包含一个嵌入的ZIP存档。

如图1所示，worddata.dotm中的宏打开另一个文档（lmss.doc，它是从worddata.dotm文件中解压出来的）。lmss.doc中的宏执行lmss.exe（Zebrocy的新NIM下载程序，也从嵌入worddata.dotm的存档文件中提取），而不是直接执行下载程序的worddata.dotm。  

根据其文件属性，lmss.doc创建于2019年1月，并于8月20日进行了修改。  

##
![1.PNG](https://image.3001.net/images/20190925/1569420249_5d8b73d90711b.png!small)下载器

sednit组织使用了多个用不同语言编写的下载程序。此次攻击活动中的插件使用的相对较新的语言nim编写的下载程序。这是一个简单的下载执行二进制文件，添加了两个小部分。第一部分用作反沙箱，它检查执行文件的第一个字母（此处为字母L或十六进制为0x6C）有没有更改。  

![1.PNG](https://image.3001.net/images/20190925/1569422167_5d8b7b57321dd.png!small)第二部分用作混淆，如图5所示下载程序使用此方法重建下载URL字符串，以避免静态分析工具定位URL字符串。  

![1.PNG](https://image.3001.net/images/20190925/1569422956_5d8b7e6c2a8e6.png!small)

NIM下载器将其动态链接库（DLL）有效载荷（OSPVC.DLL）下载到C:\StudioDavaJavaOracle，并通过ReVSR32／S将其作为服务执行。ospsvc.dll是一个用golang编写的下载程序，它不同于过去发现的其他sednit下载程序。

函数main_init（）包含已初始化的库，这些库的名称不再赘述（有关更多信息，请参阅[本文](https://www.vkremez.com/2018/12/lets-learn-dissecting-apt28sofacy.html)）。  

![1.PNG](https://image.3001.net/images/20190925/1569424855_5d8b85d7bb5da.png!small)

dll是作为服务运行的，需要分析main_dllregisterserver（）函数。字符串和密钥是XOR加密，可以使用简单的异或循环对它们进行解密。  

![1.PNG](https://image.3001.net/images/20190925/1569424331_5d8b83cb712ee.png!small)

恶意软件的主要功能：下载下一阶段的恶意软件，截图桌面和执行从C&C服务器接收到的命令。

在下载程序执行的前几分钟，每35秒截图一次，然后以base64编码的形式发送到C&C服务器。主机名和%userprofile%值也会发送到C&C服务器。C&C服务器的回复也很简单：Base64编码字符串的串联，用“”分隔。  

## 新后门

### 功能分析

新的Zebrocy后门不是用Delphi编写，是用Golang编写的。

通过再次查看main_init（）函数的库初始化代码（图8），我们可以看到新的函数，主要用于AES算法、十六进制编码和屏幕截图功能。  

![1.PNG](https://image.3001.net/images/20190925/1569424938_5d8b862a5fd09.png!small)

可以看到image_png_init代替image_jpeg_init拍摄屏幕快照。jpg格式的图像通常比png格式的图像小。

后门是以一个十六进制编码的字符串作为参数开始的。除了字符串的最后六个字节外，其他所有字符都是用存储在字符串最后六个字节中的密钥进行异或加密的。解密逻辑如下：

    
    
    key = arg[-6:].decode('hex')
    
    enc = arg[:-6].decode('hex')
    
    ''.join(chr(ord(i) ^ ord(j)) for i, j in zip(itertools.cycle(key), enc))

新后门有各种功能，之前在Zebrocy的Delphi后门中也可以看到：  

> 1、文件操作，如创建、修改和删除  
>
>
> 2、屏幕截图功能  
>
>
> 3、驱动器枚举  
>
>
> 4、命令执行（通过cmd.exe）  
>
>
> 5、计划一个名为windows\software\osdebug的任务  
>

与Delphi后门一样命令集非常有限，但是可以通过cmd.exe执行任意命令。  

### 网络

网络协议与Delphi版本的后门有一些相似之处。与C&C服务器的第一次交互会检索AES 32位密钥以加密将来的通信。

头部信息解密脚本如下：

    
    
    len_filename = len(filename)
    len_key = 14
    xor_key = filename[-len_key:].decode('hex')
    filename = filename[:len_filename-len_key].decode('hex')
    val_filename = ''.join(chr(ord(i)^ord(j)) for i,j in zip(itertools.cycle(xor_key),filename))
    random_int = val_filename[-4:]  
    

## IOCs

MITRE ATT&CK techniques

![](https://image.3001.net/images/20190925/1569426406_5d8b8be6c8a87.png!small)

![](https://image.3001.net/images/20190925/1569426416_5d8b8bf057366.png!small)

 ***参考来源：[welivesecurity](https://www.welivesecurity.com/2019/09/24/no-summer-vacations-zebrocy/)，由Kriston编译，转载请注明来自FreeBuf.COM**

