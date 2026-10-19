## **概括** ****

Lazarus
APT组织是一个长期活跃的组织，因为2014年攻击索尼影业而开始受到广泛关注，该组织早期主要针对韩国，美国等国家的政府机构进行攻击活动，以窃取情报等信息为目的。自2014年后，该组织开始针对全球金融机构，加密交易机构等为目标，进行敛财活动。

近期，奇安信威胁情报中心红雨滴团队在日常的APT样本追踪中，捕获一例利用心理测验为诱饵的Lazarus攻击样本，该样本通过宏释放powershell脚本执行,从而控制受害者计算机。奇安信威胁情报中心通过溯源关联，捕获另一例针对Macos的攻击样本，并在发现此次攻击活动的第一时间通过社交媒体进行预警。

![图片.png](https://image.3001.net/images/20191104/1572833444_5dbf88a4bd780.png!small)  

## **样本分析** ****

###  **诱饵文档** ****

MD5|  6850189bbf5191a76761ab20f7c630ef  
---|---  
作者| Windows User  
修改时间| 2019:10:22 02:53:14  
  
本次攻击活动攻击者使用心里测验相关内容为诱饵，诱导用户启用宏：

![图片.png](https://image.3001.net/images/20191104/1572833456_5dbf88b095a59.png!small)

启用宏需点击笑脸，从而执行恶意宏代码：

![图片.png](https://image.3001.net/images/20191104/1572833496_5dbf88d842e3b.png!small)

之后将powershell代码写入到%temp%目录下并通过powershell.exe执行：

![图片.png](https://image.3001.net/images/20191104/1572833529_5dbf88f99d51d.png!small)

### **P** **owershell** ****

释放的powershell脚本是一个后门，硬编码了三个c2：

![图片.png](https://image.3001.net/images/20191104/1572833595_5dbf893b9c45e.png!small)

  

执行后与内置的c2服务器进行通信，若通信失败，则休眠一段事件尝试连接其他c2：

![图片.png](https://image.3001.net/images/20191104/1572833604_5dbf89449d23a.png!small)![图片.png](https://image.3001.net/images/20191104/1572833617_5dbf89519cc7c.png!small)

从c2获取命令执行，根据不同的命令执行不同功能：

![图片.png](https://image.3001.net/images/20191104/1572833635_5dbf89637cc6c.png!small)

支持的命功能如下表所示：

命令| 功能  
---|---  
2| 设置休眠时间  
3| 结束本进程  
11| 获取本机基本信息上传  
12| 检查恶意程序当前状态  
14| 显示当前恶意程序配置  
15| 更新恶意程序c2等配置  
18| 通过cmd执行命令  
20| 上传指定文件  
21| 下载文件保存到指定文件  
24| 执行命令  
  
获取本机计算机名，ip地址，系统版本号等信息上传：

![图片.png](https://image.3001.net/images/20191104/1572833692_5dbf899c8fd98.png!small)

通过cmd执行c2命令：

![图片.png](https://image.3001.net/images/20191104/1572833704_5dbf89a868cd6.png!small)

更新c2服务器配置：

![图片.png](https://image.3001.net/images/20191104/1572833716_5dbf89b4a9b7e.png!small)  

上传指定文件：

![图片.png](https://image.3001.net/images/20191104/1572833730_5dbf89c279eca.png!small)

下载文件保存到指定位置：

![图片.png](https://image.3001.net/images/20191104/1572833773_5dbf89ed9b9ff.png!small)

###  **Mac** **os Backdoor** ****

经关联分析，奇安信威胁情报中心关联使用相同c2针对MacOS 平台的攻击样本，样本基本信息如下：

文件名| Album.app.zip  
---|---  
MD5| a8096ddf8758a79fdf68753190c6216a  
  
  

该文件包含一个正常的.Flash Player文件，而恶意程序隐藏在Flash Player中：

![图片.png](https://image.3001.net/images/20191104/1572833808_5dbf8a10ea088.png!small)

运行后首先从偏移1340，截取大小0x6c74的数据保存到.FlashUpdateCheck：

![图片.png](https://image.3001.net/images/20191104/1572833821_5dbf8a1dc4b77.png!small)

之后写入配置文件com.adobe.macromedia.flash.plist，并通过launchctl
load加载配置文件，从而使配置文件生效实现.FlashUpdateCheck的自启动：

![图片.png](https://image.3001.net/images/20191104/1572833831_5dbf8a27771f9.png!small)

使用chmod命令提升.FlashUpdateCheck权限：

![图片.png](https://image.3001.net/images/20191104/1572833842_5dbf8a32b7021.png!small)

文件名| .FlashUpdateCheck  
---|---  
MD5| bac54e7199bd85afa5493e36d3f193d2  
  
该文件具有后门功能，功能与powershell后门基本一致。同样硬编码了三个c2：

![图片.png](https://image.3001.net/images/20191104/1572833854_5dbf8a3e4911f.png!small)

运行后与c2通信获取c2指令：

![图片.png](https://image.3001.net/images/20191104/1572833869_5dbf8a4d39c4b.png!small)  

之后根据c2指令执行不同功能：

![图片.png](https://image.3001.net/images/20191104/1572833889_5dbf8a613970f.png!small)

功能列表如下：

命令| 功能  
---|---  
2| 设置休眠时间  
3| 结束本进程  
11| 获取本机基本信息上传  
12| 检查恶意程序当前状态  
14| 显示当前恶意程序配置  
15| 更新恶意程序c2等配置  
18| 通过bash执行命令  
19| 执行其他命令  
20| 上传指定文件  
21| 下载文件  
24| 通过system执行  
25| 通过system执行  
  
##  **溯源关联** ****

通过对本次攻击活动的后门以及ttps分析，奇安信威胁情报中心判断本次攻击活动的幕后黑手是Lazarus。

### 相似的后门

Powershell基本一致：

![图片.png](https://image.3001.net/images/20191104/1572833938_5dbf8a92bcce6.png!small)  

Macos 样本主要流程基本一致：

![图片.png](https://image.3001.net/images/20191104/1572833949_5dbf8a9d13db8.png!small)

且c2在奇安信威胁情报大数据平台（ti.qianxin.com）已打上Lazarus标签：

![图片.png](https://image.3001.net/images/20191104/1572833957_5dbf8aa5d982f.png!small)  

综上，本次捕获的攻击样本应该是出自臭名昭著的Lazarus APT团伙。

##  **总结** ****

Lazarus
团伙是一个长期活跃的APT组织，武器库十分强大，拥有对多平台进行攻击的能力，近年来，该团伙多次被安全厂商披露，但从未停止进攻的脚本，反而越发活跃，攻击目标也越发广泛。同时，该团伙也多次针对国内进行攻击活动，企业用户在日常的工作中，切勿随意打开来历不明的邮件附件。

目前，基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC等，都已经支持对此类攻击的精确检测。

## **I** **OC** ****

6850189bbf5191a76761ab20f7c630ef

a8096ddf8758a79fdf68753190c6216a

hxxps://crabbedly.club/board.php

hxxps://craypot.live/board.php

htxxps://indagator.club/board.php

##  **参考链接：** ****

[ _https://securelist.com/cryptocurrency-businesses-still-being-targeted-by-lazarus/90019/_](https://securelist.com/cryptocurrency-businesses-still-being-targeted-by-lazarus/90019/)

  
****

## ****

  

