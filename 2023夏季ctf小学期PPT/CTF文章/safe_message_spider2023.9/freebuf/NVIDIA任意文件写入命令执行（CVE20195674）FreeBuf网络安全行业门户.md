***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 漏洞介绍

 **在这篇文章中，我们将对NVIDIA GeForce
Experience（GFE）中的任意文件写入漏洞（CVE-2019-5674）进行深入分析。大家都知道，很多使用了N卡的设备在安装NVIDIA
GeForce产品时默认都会安装NVIDIA GeForce
Experience（GFE），由于存在这个漏洞，攻击者将能够强制让应用程序以特权用户身份在目标系统中写入任意文件。简单来说，你可以通过重写关键系统文件来让主机无法正常服务，而且你甚至还可以控制、利用和窃取目标系统中的数据。**

由于GFE在写入日志文件时使用的是SYSTEM用户权限，这种不安全的权限设置将导致任意系统文件均可被重写。除此之外，日志文件中的数据也是用户可控制的，攻击者将可以向日志文件中注入控制命令，然后将其存储为batch文件来执行并实现提权。

![1.gif](https://image.3001.net/images/20190410/1554906564_5cadfdc4c8ffb.gif!small)

### NVIDIA GeForce Experience

根据NVIDIA官网的介绍，GeForce Experience
GFE不仅可以更新升级显卡驱动，并优化你的游戏设置，而且还可以截图，或跟朋友分享视频流文件。更重要的是，它可以给N卡用户提供更多的附加功能。

## 漏洞发现

当时在分析NVIDIA服务和应用程序时，我先打开的是进程监控软件（Procmon），分析后我发现，有两个跟NVIDIA有关的进程可能会有搞头：nvcontainer.exe和NVDisplay.Container.exe。接下来，我在Procmon中添加了一个过滤器来查看*container.exe会向那些文件写入数据。

![2.png](https://image.3001.net/images/20190410/1554906582_5cadfdd6e16c5.png!small)

在过滤器的帮助下，我们只需要关注“写入文件”的操作即可，大家可以从下图中看到，这些进程会以“NT
AUTHORITY\SYSTEM”来向“C:\ProgramData”目录中写入多个日志文件（其中还包括普通用户可以修改的文件）。

![3.png](https://image.3001.net/images/20190410/1554906588_5cadfddc429d2.png!small)

检查这些文件的权限之后，我们可以看到“Everyone”组中的用户拥有对这些文件的完整控制权。

所以，SYSTEM组和Everyone组中的成员均可随意控制这些文件，包括创建跟其他系统文件的硬链接或符号链接。如果攻击者不能以普通用户身份来修改某个系统文件，那么在创建了跟该文件相关联的链接之后，SYSTEM进程将搜索这个链接（本身就是日志文件，默认时可写入的），并允许向该文件写入数据。受影响的文件将包括关键系统文件，而这些文件一旦被非法修改，将导致应用程序或操作系统崩溃。

## 利用任意文件写入漏洞

在利用该漏洞前，我们需要使用symboliclink-testing-tools来创建符号链接和硬链接，因为该工具可以帮我们以普通用户权限创建系统文件的链接。在测试过程中，我还使用了Createsymlink工具并创建了一个临时符号链接：“C:\ProgramData\NVIDIACorporation\nvstapisvr\nvstapisvr.log”=>“C:\windows\test.file”，这个test.file文件只有管理员权限可写。为了确保符号链接创建成功，我们需要让“C:\ProgramData\NVIDIACorporation\nvstapisvr\”目录为空，如果该目录不为空，则会看到如下图所示的错误信息：

![4.png](https://image.3001.net/images/20190410/1554906601_5cadfde99091e.png!small)

接下来，当NVIDIA特权进程向日志文件“C:\ProgramData\NVIDIACorporation\nvstapisvr\nvstapisvr.log”中写入数据时，该进程实际上是在向“C:\windows\test.file”写入数据。

![5.png](https://image.3001.net/images/20190410/1554906609_5cadfdf1d3f78.png!small)

这就表明，该漏洞可以允许我们重写任意系统文件。但这样还远远不够，因为我们还无法让某些文件崩溃或让系统拒绝服务。这是因为特定日志文件中的数据目前仍是不可控制的，它只会写入所有本该记录的日志数据。

因此，我们需要控制写入到日志文件中的数据。经过分析之后，我发现“C:\ProgramData\NVIDIACorporation\nvstreamsvc\nvstreamsvcCurrent.log”中包含一些有趣的字符串，而且当GeForce
Experience的“GameStream”开关打开或关闭时，“C:\ProgramData\NVIDIA
Corporation\NvStreamSrv\settings.txt”中包含的某些变量会写入到nvstreamsvcCurren日志文件中。

![6.png](https://image.3001.net/images/20190410/1554906619_5cadfdfb55c68.png!small)

点击这个开关，可以让“C:\ProgramData\NVIDIACorporation\nvstreamsvc\nvstreamsvcCurrent.log”记录settings.txt文件中包含的URL地址：

![7.png](https://image.3001.net/images/20190410/1554906628_5cadfe049ccf1.png!small)

接下来，我尝试向这些变量值后面添加一些命令来修改日志文件：

![8.png](https://image.3001.net/images/20190410/1554906635_5cadfe0b14f6c.png!small)

果然成功了：

![9.png](https://image.3001.net/images/20190410/1554906642_5cadfe12c98d1.png!small)

虽然这里有一堆其他的日志数据，但我们注入的命令最终还是会在.bat文件中执行的。再加上现在我可以向任意目录中写入文件，那么我就可以向存在漏洞的文件中注入有效命令，然后把文件写入到系统启动目录中，然后执行注入的命令，最终实现提权。

但这里还是有一个问题，也就是创建符号链接的目录必须为空，但现在的目录包含NVIDIA服务需要使用的文件，而且我还删不掉。但是，这个问题进入安全模式就解决了。

总结一下：

1、将需要执行的命令添加到“C:\ProgramData\NVIDIACorporation\NvStreamSrv\settings.txt”；

2、 清空“C:\ProgramData\NVIDIACorporation\nvstreamsvc\”目录；

3、
创建符号链接：“C:\ProgramData\NVIDIACorporation\nvstreamsvc\nvstreamsvcCurrent.log”=>“C:\ProgramData\Microsoft\Windows\Start
Menu\Programs\StartUp\cmd.bat”

创建符号链接：

![10.png](https://image.3001.net/images/20190410/1554906661_5cadfe2562756.png!small)

切换“GameStream”服务的开关，然后系统启动目录中就会有我们的cmd.bat文件了：

![11.png](https://image.3001.net/images/20190410/1554906670_5cadfe2e38fc9.png!small)

## 完整提权

NVIDIA本身带有很多batch文件，这些文件可以在“C:\Windows”目录中找到：

![12.png](https://image.3001.net/images/20190410/1554906686_5cadfe3e9186b.png!small)

当“NVIDIA Display Container”或“NVIDIA
TelemetryContainer”服务崩溃了两次以上时，这些文件就会以SYSTEM权限运行，这也是NVIDIA服务的恢复机制：

![13.png](https://image.3001.net/images/20190410/1554906693_5cadfe45d621a.png!small)

这些文件同样是我们可以利用的，我们只需要让NVIDIA服务崩溃三次，就可以强制让BAT文件执行，并实现提权。

### 所受影响版本

    
    
    GeForce Experience <= 3.18

 *** 参考来源：[rhinosecuritylabs](https://rhinosecuritylabs.com/application-security/nvidia-arbitrary-file-writes-to-command-execution-cve-2019-5674/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

