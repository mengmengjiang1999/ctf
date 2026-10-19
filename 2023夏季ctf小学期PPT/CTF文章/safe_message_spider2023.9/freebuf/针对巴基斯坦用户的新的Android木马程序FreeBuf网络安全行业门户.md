## **概述**

临近年底，黑客利用钓鱼网站分发恶意软件的热情并未熄火。近日安全研究人员发现了一批新的android木马程序，这批木马程序通过在安全应用的启动程序中加入自身的恶意代码或修改安全应用的启动组件，然后将应用程序重打包，以达到窃取用户隐私数据的目的。修改后的应用看起来与安全的应用程序完全相同，甚至可执行其正常功能。

这批木马程序主要针对巴基斯坦用户，程序启动后首先连接服务器下载恶意dex文件，通过加载恶意的dex文件执行窃取用户通讯录、短信息、通话记录、文件等信息的行为。并不影响原程序的执行流程，用户难以发现恶意软件的异常行为。

##  **一、发现过程**

在域名为pmdu.info的钓鱼网站上托管着修改后的由巴基斯坦政府发行的PakistanCitizen Portal
应用程序，PakistanCitizen Portal 应用程序是由一个名为PMDU的政府机构于2019年创建的，其真正托管在域名为gov.pk的网站上。

![](https://image.3001.net/images/20210119/1611047792_6006a37091386ddd89b95.png!small)图1-1
托管恶意程序的钓鱼网站

![](https://image.3001.net/images/20210119/1611047892_6006a3d410e2265e2dc4c.png!small)图1-2
伪造google play页面

用户无论点击以下那个按钮都会直接下载该恶意程序：

![](https://image.3001.net/images/20210119/1611047914_6006a3ead4035779a0b62.png!small)图1-3
下载连接

其中研究人员在巴基斯坦一家私人公司巴基斯坦贸易有限公司（TCP）的官方网站页面上发现了托管该恶意软件的网址，该链接直接指向钓鱼网站。怀疑该网站招到了黑客的破坏。

![](https://image.3001.net/images/20210119/1611047934_6006a3fe43e6df93962b9.png!small)图1-4
TCP网站程序钓鱼网站链接

##  **二、样本信息**

除了重打包PakistanCitizen Portal 应用程序外，我们还发现了该木马的同源样本，这些应用程序都是针对巴基斯坦用户。

 **应用名称**

  

|

 **包名**

  

|

 **MD5**

  
  
  
---|---|---  
  
Pakistan Citizen Portal

  

|

com.govpk.citizensportal

  

|

176DF6CE5CD78189A3F554961EF226FA

  
  
  
Pakistan Salat Time

  

|

com.tos.salattime.pakistan

  

|

1514376339E4A0B4727C6897640C7C3E

  
  
  
Mobile Packages Pakistan

  

|

com.blogspot.istcpublishers.mobilepackagespakistan

  

|

A7A95c490C23F2F991F0E975D7A2BA88

  
  
  
TPL Insurance

  

|

com.tpl.insuranceapp

  

|

44A84E62C5BB2487E3175C720803BA54

  
  
  
Registered SIMs Checker

  

|

com.siminformation.checker)

  

|

D194CB0948E85D1D6A61959403EB38CA

  
  
  
Pakistan Chat

  

|

com.PakistanChatMessenger

  

|

1C1745F997D30D1F2E8D1AFF7322C774

  
  
  
###  **2.1 文件结构**

安全的应用程序与被重打包的应用程序文件目录大致相同：

![](https://image.3001.net/images/20210119/1611048239_6006a52f2ef2c37802b8b.png!small)图2-1
文件结构对比

黑客修改了安全应用的启动组件：

![](https://image.3001.net/images/20210119/1611048257_6006a541e661c627ad7ac.png!small)图2-2
启动程序对比

并在启动程序中加入了自身代码，从而控制程序执行流程：

![](https://image.3001.net/images/20210119/1611048275_6006a5530bf0296f9af6d.png!small)图2-3
启动程序中加入自身代码

###  **2.2 程序图标**

![](https://image.3001.net/images/20210119/1611048304_6006a570d60d757c24fdb.png!small)
图2-1 应用图标

###  **2.3 程序运行界面**

![](https://image.3001.net/images/20210119/1611048325_6006a58529af91b4b08a7.png!small)![](https://image.3001.net/images/20210119/1611048344_6006a598b5f96cb04f584.png!small)
图2-2 程序运行界面

### 2.4 程序运行流程

这些应用程序都是通过在安全应用的启动代码中加入自身代码或修改安全应用的启动组件来改变程序执行流程，从而达到窃取用户隐私数据的目的，恶意功能执行完毕便回归到合法程序的政常执行流程。

![](https://image.3001.net/images/20210119/1611048367_6006a5af16d9d863a68e7.png!small)图2-3
程序运行流程图

##  **三、行为分析**

###  **3.1 动态加载恶意代码**

程序启动首先会发送设备的唯一IMEI标识符和时间戳以及用户名和密码组合（"abc"、"def"）提交到服务器。提交此信息后，应用程序立即从服务器下载[DEX](https://source.android.com/devices/tech/dalvik/dex-format)有效负载class.dex，然而加载DEX文件执行其恶意代码。在大多数情况下，有效负载名为class.dex，但是Trojanized
TPLInsurance应用程序会检索名为class_tpl.dex的有效负载。

![](https://image.3001.net/images/20210119/1611048404_6006a5d4a5f4fdfccf26d.png!small)图3-1下载class.dex文件

从服务器下载DEX文件并保存在本地文件目录，接着从本地加载DEX文件。

![](https://image.3001.net/images/20210119/1611048436_6006a5f43921c182fdb0d.png!small)图3-2
加载DEX文件

###  **3.2 窃取用户隐私数据**

调用DEX文件中的loadData方法，窃取用户设备、位置、联系人、短信、通话记录、文件信息：

![](https://image.3001.net/images/20210119/1611048474_6006a61ae6095772de5ea.png!small)图3-3
执行恶意程序

为了隐藏自身，恶意程序对服务器地址进行了AES加密，且对上传的用户隐私数据进行亦或加密：

![](https://image.3001.net/images/20210119/1611048520_6006a648340640b758f3c.png!small)图3-4
服务器地址加密密钥

恶意软件上传用户设备所以文件列表：

![](https://image.3001.net/images/20210119/1611048540_6006a65c71bb74bb0cd86.png!small)图3-5
上传用户文件信息

网络请求数据包：

![](https://image.3001.net/images/20210119/1611048565_6006a6756c0e712a5f647.png!small)图3-6
服务器请求

Pakistan CitizenPortal
应用程序以及其他一些应用程序将窃取的用户信息上传到域名p***hat.online、172.16.***.72的服务器，而伪造的TPLInsurance应用程序将其窃取的数据上传到域名为tpli***rance.xyz的服务器。

服务器列表：

​服务器地址

|

功能  
  
---|---  
  
[http://pa***hat.online/Chat_view/api/json/log_data.php](http://pakchat.online/Chat_view/api/json/log_data.php)

|

上传设备IMEI、用户名、密码  
  
[http://pa**at.online/Chat_view/api/dex/class.dex](http://pakchat.online/Chat_view/api/dex/class.dex)

|

下载class.dex  
  
[http://pa**at.online/Chat_view/api/device_info.php](http://pakchat.online/Chat_view/api/device_info.php)

|

上传设备信息  
  
[http://pa***hat.online/Chat_view/api/json/contact.php](http://pakchat.online/Chat_view/api/json/contact.php)

|

上传联系人信息  
  
[http://pa***hat.online/Chat_view/api/json/message.php](http://pakchat.online/Chat_view/api/json/message.php)

|

上传短信息  
  
[http://pa***hat.online/Chat_view/api/json/call_log.php](http://pakchat.online/Chat_view/api/json/call_log.php)

|

上传通话记录  
  
[http://pa***hat.online/Chat_view/api/file_manager.php](http://pakchat.online/Chat_view/api/file_manager.php)

|

上传文件目录  
  
[http://pa***hat.online/Chat_view/api/files_up.php](http://pakchat.online/Chat_view/api/files_up.php)

|

上传文件信息  
  
[http://tpli***rance.xyz/insurance/products/json/log_data.php](http://tplinsurance.xyz/insurance/products/json/log_data.php)

|

上传设备IMEI、用户名、密码  
  
[http://tplin***ance.xyz/insurance/products/dex/class_tpl.dex](http://tplinsurance.xyz/insurance/products/dex/class_tpl.dex)

|

下载class.dex  
  
[http://tplins***nce.xyz/insurance/products/device_info.php](http://tplinsurance.xyz/insurance/products/device_info.php)

|

上传设备信息  
  
[http://tpli***rance.xyz/insurance/products/location.php](http://tplinsurance.xyz/insurance/products/device_info.php)

|

上传位置信息  
  
[http://tpli***rance.xyz/insurance/products/contact.php](http://tplinsurance.xyz/insurance/products/device_info.php)

|

上传联系人信息  
  
[http://tplin***rance.xyz/insurance/products/message.php](http://tplinsurance.xyz/insurance/products/device_info.php)

|

上传短信息  
  
[http://tpli***rance.xyz/insurance/products/call_log.php](http://tplinsurance.xyz/insurance/products/device_info.php)

|

上传通话记录  
  
[http://tpli***rance.xyz/insurance/products/file_manager.php](http://tplinsurance.xyz/insurance/products/device_info.php)

|

上传文件目录  
  
[http://tplin***ance.xyz/insurance/products/files_up.php](http://tplinsurance.xyz/insurance/products/device_info.php)

|

上传文件信息  
  
[http://172.16.***.72/fury/api/device_info.php
](http://172.16.150.72/fury/api/device_info.php)

|

上传设备信息  
  
[http://172.16.***.72/fury/api/json/contact.php](http://172.16.150.72/fury/api/json/contact.php)

|

上传联系人信息  
  
[http://172.16.***.72/fury/api/json/message.php](http://172.16.150.72/fury/api/json/message.php)

|

上传短信息  
  
[http://172.16.***.72/fury/api/dex/class.dex](http://172.16.150.72/fury/api/dex/class.dex)

|

下载class.dex  
  
[http://172.16.***.72/fury/api/json/call_log.php](http://172.16.150.72/fury/api/json/call_log.php)

|

上传通话记录  
  
https://kv33.z***to.org:8887/mobisync

|

上传获取的所以用户隐私数据  
  
###  **3.3 延迟执行数据上传行为**

其中PakistanSalat Time程序的窃取用户隐私数据的恶意代码直接写在合法程序中，并直接通过广播触发窃取用户隐私数据的服务。

![](https://image.3001.net/images/20210119/1611048589_6006a68de64417a950ff9.png!small)图3-8通过广播促发相应恶意服务

该应用程序除了具有与PakistanCitizen Portal 应用程序一样的窃取用户隐私数据的行为外，还会对用户录音及上传屏幕截屏信息，具有监控性质。

![](https://image.3001.net/images/20210119/1611048620_6006a6ac3dd863a26cb3b.png!small)图3-9
执行恶意程序

上传用户隐私数据，服务器地址：https://kv33.z***to.org:8887/mobisync

![](https://image.3001.net/images/20210119/1611048661_6006a6d5ef2f88f722b65.png!small)图3-10
保存收集的用户隐私数据

![](https://image.3001.net/images/20210119/1611048691_6006a6f383e532ddfd969.png!small)图3-11
上传至服务器

该应用程序并不会马上上传用户隐私数据，而是设置了一个值，当这个值大于50便上传，如果小于50便休眠50s，所以分析人员一开始并不会发现他上传用户隐私数据行为。

![](https://image.3001.net/images/20210119/1611048714_6006a70a73cfdb697ba53.png!small)图3-12
设置验证执行

##  **五、安全建议**

> 用户安装所需软件，建议去正规的应用市场下载、去官方下载。
>
> 在手机当中安装必要的安全软件，并保持安全软件更新。

#  **IOC**

> Pa***hat.online
>
> Tpli***rance.xyz
>
> kv33.z**to.org
>
> 172.16.***.72

