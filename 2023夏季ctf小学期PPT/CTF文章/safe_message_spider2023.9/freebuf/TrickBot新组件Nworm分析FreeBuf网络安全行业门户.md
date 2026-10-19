**TrickBot于2016年被首次发现，其主要目的是窃取目标主机数据，安装恶意软件后门。TrickBot拥有不同的功能模块，可从受感染的Windows客户端传感染DC。在2020年4月，TrickBot将其传播模块“mworm”更新为“nworm”。nworm不会在DC上留下任何痕迹，服务器重新启动或关闭后会消失。**

新nworm模块主要包括：

> 加密可执行文件和网络通信流量（旧mworm模块没有任何类型的加密/编码）
>
> TrickBot感染从RAM运行，不可持久存在
>
> 通过RAM运行以逃避受感染DC的检测

本文回顾了TrickBot模块，并详细地介绍了新nworm模块的特性。

## TrickBot模块

TrickBot可以模块化安装运行，感染期间可加载各种二进制文件执行不同功能。
在大多数情况下，TrickBot感染的基础是保存在磁盘的恶意Windows可执行文件（EXE）。 此EXE通常称为“
TrickBot加载程序”，可加载TrickBot模块。 TrickBot模块是从系统内存运行的动态链接库（DLL）或EXE。

![1591580155_5edd95fb8bd7c.png!small](https://image.3001.net/images/20200608/1591580155_5edd95fb8bd7c.png!small)

在受感染的Windows 10主机上，TrickBo仅出现在系统内存中。在受感染的Windows 7主机上，在磁盘中会存储的相关模块。
在TrickBot感染期间，加密的二进制文件将作为TrickBot模块解密并从系统内存中运行。 下图显示了2020年1月Windows 7
TrickBot模块工件示例。

![1591580726_5edd9836a2f0a.png!small](https://image.3001.net/images/20200608/1591580726_5edd9836a2f0a.png!small)

文件名称以64结尾，说明该主机运行的是Windows 7 64位版本。如果感染发生在32位Windows 7主机上，这些文件名称将以32而不是64结尾。

TrickBot在Active Directory（AD）环境中扩展到DC的三个模块：

> mwormDll64（“ mworm”模块）
>
> mshareDll64（“ mshare”模块）
>
> tabDll64（“标签”模块）

### 传播模块

具有传播功能的TrickBot模块为mworm，mshare和tab，mshare和tab模块：

> 受感染的Windows客户端使用HTTP URL检索新的TrickBot EXE
>
> 受感染的Windows客户端通过SMB将新的TrickBot EXE发送到易受攻击的DC

对于mworm模块：

> 受感染的Windows客户端对易受攻击的DC进行SMB攻击。
>
> 易受攻击的DC使用HTTP URL检索新的TrickBot EXE并感染自身。

除非在带有DC的AD环境中发生TrickBot感染，否则通常不会显示mworm模块。

下图显示了这三个TrickBot模块的传播流程图：

![1591583323_5edda25b825c6.png!small](https://image.3001.net/images/20200608/1591583323_5edda25b825c6.png!small)

自2020年2月以来，这些模块生成的URL遵循以下模式：

> mshare模块以/images/cursor.png结尾
>
> mworm模块以/images/redcar.png结尾
>
> tab模块以/images/imgpaper.png结尾

这些URL使用IP地址而不是域。 下图显示了2020年3月TrickBot感染流量：

![1591583440_5edda2d04d249.png!small](https://image.3001.net/images/20200608/1591583440_5edda2d04d249.png!small)

## 新模块分析

2020年4月TrickBot停止使用mworm模块，取而代之的是名为“nworm”的模块出现在受感染的Windows
7客户端上。下图显示了这种新的nworm模块：

![1591583524_5edda324c2463.png!small](https://image.3001.net/images/20200608/1591583524_5edda324c2463.png!small)

nworm的HTTP流量与mworm流量明显不同：

> mworm：TrickBot EXE的URL以/images/redcar.png结尾
>
> nworm：TrickBot EXE的URL以/ico/VidT6cErs结尾
>
> mworm：HTTP流量中TrickBot EXE未加密
>
> nworm：TrickBot EXE会在HTTP流量中加密编码

使用Wireshark检查TCP流，可以发现mworm模块和nworm模块HTTP流差异。

![1591583684_5edda3c45bf20.png!small](https://image.3001.net/images/20200608/1591583684_5edda3c45bf20.png!small)

![1591583691_5edda3cb04b4b.png!small](https://image.3001.net/images/20200608/1591583691_5edda3cb04b4b.png!small)

下图显示了当前的传播流程，突出显示了nworm模块变化：

![1591583733_5edda3f54c281.png!small](https://image.3001.net/images/20200608/1591583733_5edda3f54c281.png!small)

### 不持久性

nworm感染易受攻击的DC时，恶意软件将从内存中启动。受感染的DC上未发现任何攻击痕迹，但DC上的TrickBot重新后会消失。mshare和tab感染易受攻击的DC时，DC重启后仍然持续存在。对于TrickBot而言，重启后消失并不是急需解决的问题，因为DC是一台服务器，服务器很少像Windows客户端那样关闭或重新启动。

### Gtag标识

每个TrickBot都有一个gtag标识符，可从TrickBot二进制文件配置数据中找到。在TrickBot感染期间，也可以在HTTP流量中找到Gtag。

Gtag是一个短字母字符串，后跟一个数字表示序列。示例如下：

> mor系列gtag：由Emotet感染引起的TrickBot，例如：TrickBot gtag mor84是由Emotet在2020年1月27日感染的。
>
> ono系列gtag：TrickBot通过恶意Microsoft Office文档（如Word文档或Excel电子表格）传播的。
>
> red系列gtag：TrickBot以DLL文件而不是EXE的形式传播，例如：2020年3月17日记录的TrickBot gtag red5。
>
> TrickBot模块使用的TrickBot二进制文件的Gtag是唯一的。
>
> tot系列gtag：mshare模块使用的TrickBot二进制文件
>
> jim系列gtag：nworm（和旧的mworm）模块使用的TrickBot二进制文件
>
> lib系列gtag：tab模块使用的TrickBot二进制文件

下图显示了2020年4月20日Wireshark中的gtag。其中Windows客户端为10.4.20.101，DC为10.4.20.4。

![1591585981_5eddacbda2317.png!small](https://image.3001.net/images/20200608/1591585981_5eddacbda2317.png!small)

![1591585989_5eddacc54d67e.png!small](https://image.3001.net/images/20200608/1591585989_5eddacc54d67e.png!small)

## IOCs

### HTTP URLs

> 2020-04-20 – nworm – hxxp://107.172.221[.]106/ico/VidT6cErs
>
> 2020-04-20 – mshare – hxxp://107.172.221[.]106/images/cursor.png
>
> 2020-04-20 – tab – hxxp://107.172.221[.]106/images/imgpaper.png
>
> 2020-05-08 – nworm – hxxp://23.95.227[.]159/ico/VidT6cErs
>
> 2020-05-08 – mshare – hxxp://23.95.227[.]159/images/cursor.png
>
> 2020-05-08 – tab – hxxp://23.95.227[.]159/images/imgpaper.png

### nwormDll64 （Windows 7 client April 24th 2020）

> 900aa025bf770102428350e584e8110342a70159ef2f92a9bfd651c5d8e5f76b

### nwormDll64（Windows 7 client May 8th 2020）

> 85d88129eab948d44bb9999774869449ab671b4d1df3c593731102592ce93a70

## 参考来源

> [unit42](https://unit42.paloaltonetworks.com/goodbye-mworm-hello-nworm-> trickbot-updates-propagation-module/)

