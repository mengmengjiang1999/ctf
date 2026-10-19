**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

##  **一、背景**

2021年3月初，暗影实验室就发现了几个针对西班牙投放的移动端木马，这些木马从代码结构，到主控地址，到安装名称，再到针对的对象都是极其相似，这是一个有具有针对性的木马传播事件，APP通过仿冒西班牙邮政快递及国际知名快递诱导用户安装使用，从而获取用户设备上的各种敏感信息。

本次发现的APP大致分为两类：一类是仿冒西班牙邮政快递(Correos)，一类是仿冒国际知名快递(DHL、FedEx)。

此类木马针对安卓5.0系统到安卓9.0系统，危害范围比较大。需要注意的是，此类木马在启动后，会诱骗用户开启无障碍辅助服务(AccessibilityService)。此服务设计初衷在于帮助残障用户使用android设备和应用，在后台运行，可以监听用户界面的一些状态转换。木马通过此服务监听用户手机界面变化，禁止用户查看应用程序列表，阻止用户卸载此应用。一般用户极难卸载此类木马。

仿冒西班牙邮政快递及国际知名快递的木马通过相同或者相似的安装图标及安装名称诱导用户下载安装，然后通过开启无障碍辅助服务之后，后台获取用户设备上的短信及联系人等信息上传到服务器。

##  **二、木马分析**

###  **2.1 信息汇总**

本次发现的APP主要伪装成西班牙邮政快递应用、国际知名快递应用。

 **MD5**

  

|

 **安装名**

  

|

 **图标**

  

|

 **最低兼容版本**

  
  
  
---|---|---|---  
  
74F88D5480AEFE165721C36100DCF89A

  

|

DHL

  

|

![](https://image.3001.net/images/20210330/1617087252_6062cb140ec8ef9059395.png!small)

  

|

Android5.0

  
  
  
CBCEE88707CD523D7F1131F26E9DD4AF

  

|

Correos

  

|

  

![](https://image.3001.net/images/20210330/1617087265_6062cb218716ef57f55db.png!small)

|

Android5.0

  
  
  
CBCEE88707CD523D7F1131F26E9DD4AF

  

|

Correos

  

|

  

![](https://image.3001.net/images/20210330/1617087277_6062cb2d350e68d51d41f.png!small)

|

Android5.0

  
  
  
1A2A4044CF18EED59E66c413DB766145

  

|

FedEx

  

|

  

![](https://image.3001.net/images/20210330/1617087297_6062cb4199341675ce8c8.png!small)

|

Android5.0

  
  
  
B991622168F7787CB1A89FC2BDD38A30

  

|

FedEx

  

|

  

![](https://image.3001.net/images/20210330/1617087311_6062cb4f49c3ae13cb41f.png!small)

|

Android5.0

  
  
  
###  **2.2 运行分析**

运行本次发现的木马发现界面极其简单，仿冒西班牙邮政快递、全球著名快递的APP应用图标、应用名称均与快递公司官网图标相似，用户难以区分真伪。

![](https://image.3001.net/images/20210330/1617087339_6062cb6b5145cfc3535a8.png!small)图1-1
仿冒图标

木马启动后诱导用户开启无障碍辅助服务，隐藏图标，并监听用户界面，防止卸载。

![](https://image.3001.net/images/20210330/1617087360_6062cb807db80a9134b27.png!small)图1-2
请求开启无障碍辅助服务并隐藏图标

除此以外，仿冒APP均由随机字母组成的域名前缀加上.ru或者.com域名后缀组成多个域名并启动多个线程进行上传用户隐私信息。

![](https://image.3001.net/images/20210330/1617087507_6062cc137d376838a21ca.png!small)![](https://image.3001.net/images/20210330/1617087529_6062cc2955286796825e6.png!small)图1-3
随机字母组成域名

通过抓包，发现了多个域名：

![](https://image.3001.net/images/20210330/1617087568_6062cc505c714793ca589.png!small)图1-4
抓包数据

域名如下：

> http://egus****rrmqvj.ru/poll.php
>
> http://pde****holjjkn.com/poll.php
>
> http://lnnr****cbmdhn.com/poll.php
>
> http://icim****dffbr.com/poll.php
>
> http://bm****ttkswfh.com/poll.php
>
> http://we****pgfumtk.com/poll.php
>
> http://bfw****cedupj.com/poll.php
>
> http://nfiu****tasnuk.com/poll.php
>
> http://afh****cjbpln.com/poll.php
>
> http://uh****ablfmwm.com/poll.php
>
> http://ao****wqhuokpd.ru/poll.php
>
> http://ap****drpokfbc.com/poll.php
>
> http://gb****vsgkvkdh.ru/poll.php

经过分析，发现只有4个域名还能进行访问：

![](https://image.3001.net/images/20210330/1617087591_6062cc677ea3871bd308f.png!small)图1-5
有效域名

IP地址均位于境外。

http://egusn****rmqvj.ru/poll.php

  

|

德国

  
  
  
---|---  
  
http://wenk****gfumtk.com/poll.php

  

|

美国

  
  
  
http://nfiue****snuk.com/poll.php

  

|

法国

  
  
  
http://gbm****sgkvkdh.ru/poll.php

  

|

美国

  
  
  
###  **2.3 指令解析**

 **2.3.1 指令获取**

木马通过向指定域名上传用户设备的一些基本信息来下发指令。

![](https://image.3001.net/images/20210330/1617087620_6062cc842032efd94c0b4.png!small)图1-6
服务器下发指令

在获得服务器发送的指令后，程序根据指令进行不同的操作。

![](https://image.3001.net/images/20210330/1617087643_6062cc9b98e621d8f3f92.png!small)![](https://image.3001.net/images/20210330/1617087659_6062ccabc3260e31623cc.png!small)图1-7
解析指令

 **2.3.2 oder指令**

木马指令进行了一定程度的加密混淆，使分析木马比较困难。

![](https://image.3001.net/images/20210330/1617087683_6062ccc333861779301f4.png!small)图1-8
指令经过加密混淆

经过测试进行解密后得到指令内容。

![](https://image.3001.net/images/20210330/1617087702_6062ccd6b1d469f8b81b0.png!small)图1-9
解密后指令

下图是不同功能的order指令，一共十二种。

![](https://image.3001.net/images/20210330/1617087721_6062cce9e1eadf0dd0ec6.png!small)

 **1）BLOCK**

收到该指令后，程序会停止50秒：

![](https://image.3001.net/images/20210330/1617087746_6062cd0241e67ac36f553.png!small)

![](https://image.3001.net/images/20210330/1617087762_6062cd12caff1503051f9.png!small)

![](https://image.3001.net/images/20210330/1617087786_6062cd2a16820248303d3.png!small)图1-10
程序休眠指令

 **2）CARD_BLOCK**

收到该指令后，启动一个新的线程开启SOCK客户端：

![](https://image.3001.net/images/20210330/1617087814_6062cd466ba89b423803b.png!small)

![](https://image.3001.net/images/20210330/1617087841_6062cd619c735e70b5aac.png!small)图1-11开启SOCK客户端

 **3）OPEN_URL**

收到此指令后，程序会打开指定内容的界面：

![](https://image.3001.net/images/20210330/1617088022_6062ce1652c411c78e70d.png!small)图1-12
打开指定界面

 **4）RUN_USSD**

收到该指令后，程序启动无障碍辅助服务：

![](https://image.3001.net/images/20210330/1617088044_6062ce2c5cf00019471b5.png!small)

![](https://image.3001.net/images/20210330/1617088059_6062ce3b24ff8018b30de.png!small)图1-13
启动无障碍辅助服务

 **5）DISABLE_PLAY_PROTECT**

收到该指令，程序关闭设备的GooglePlay Protect功能：

![](https://image.3001.net/images/20210330/1617088083_6062ce53e3b8ca4512335.png!small)图1-14
关闭设备的GooglePlay Protect功能

 **6）RELOAD_INJECTS**

收到该指令后，获取用户设备已安装应用程序列表并上传到服务器：

![](https://image.3001.net/images/20210330/1617088104_6062ce682bf2238901763.png!small)图1-15
获取设备已安装应用列表

 **7）SEND_SMS**

收到该指令后，发送短信到指定号码：

![](https://image.3001.net/images/20210330/1617088123_6062ce7b5db4fad894a47.png!small)![](https://image.3001.net/images/20210330/1617088136_6062ce88324e0a79aa020.png!small)图1-16
发送短信至指定号码

 **8）GET_CONTACTS**

收到该指令后，获取用户的通讯录并上传到服务器：

![](https://image.3001.net/images/20210330/1617088155_6062ce9bc182b42f39292.png!small)图1-17
获取用户设备通讯录

 **9）UNINSTALL_APP**

收到该指令后，卸载用户设备上指定的app：

![](https://image.3001.net/images/20210330/1617088187_6062cebbabed819de8e45.png!small)

![](https://image.3001.net/images/20210330/1617088199_6062cec771c568ff79ca8.png!small)图1-18
卸载设备指定应用

 **10）CARD_BLOCK**

收到该指令后，弹出窗口获取用户信用卡信息：

![](https://image.3001.net/images/20210330/1617088224_6062cee00e2783379de58.png!small)

![](https://image.3001.net/images/20210330/1617088236_6062ceec9f2010b04f5d2.png!small)图1-19
窃取用户信用卡信息

 **11）SMS_INT_TOGGLE**

收到该指令后，替换用户默认短信程序：

![](https://image.3001.net/images/20210330/1617088265_6062cf09b3eb4c151382c.png!small)

![](https://image.3001.net/images/20210330/1617088278_6062cf16b7f63a67d45cc.png!small)图1-20
弹框提示用户

 **2.3.3 上传服务器地址**

目前发现上述指令文件上传的服务器地址有许多个，程序启动后就会不停的进行上传用户设备信息。短短几分钟就达到一百多条上传数据包，域名分别通过随机字母数组随机组成，然后拼接域名不同的后缀进行发送，程序获取指令后进行不同的操作。服务器链接成功的地址为四个，分别如下：

> ​http://egus****rrmqvj.ru/poll.php
>
> http://wen****pgfumtk.com/poll.php
>
> http://nfi****tftasnuk.com/poll.php
>
> http://gbm****sgkvkdh.ru/poll.php

服务器链接失败的地址如下：

> http://pde****holjjkn.com/poll.php
>
> http://lnn****stcbmdhn.com/poll.php
>
> http://ici****cudffbr.com/poll.php
>
> http://bmp****ttkswfh.com/poll.php
>
> http://bfw****icedupj.com/poll.php
>
> http://afh****cjbpln.com/poll.php
>
> http://uhl****ablfmwm.com/poll.php
>
> http://aog****qhuokpd.ru/poll.php
>
> http://apd****rpokfbc.com/poll.php

##  **三、服务器威胁情报信息**

序号

  

|

木马（C&C）域名

  

|

IP地址

  

|

归属地

  

|

用途

  

|

近期发现时间

  
  
  
---|---|---|---|---|---  
  
1

  

|

egus****rmqvj.ru

  

|

47.91.***.36

  

|

德国

  

|

木马回传信息地址

  

|

2021-03-17

  
  
  
2

  

|

wenk****gfumtk.com

  

|

173.231.***.124

  

173.231.***.8

  

35.205.***.67

  

|

美国

  

|

木马回传信息地址

  

|

2021-03-25

  
  
  
3

  

|

nfiu****tasnuk.com

  

|

51.254.***.105

  

|

法国

  

|

木马回传信息地址

  

|

2021-03-25

  
  
  
4

  

|

gbms****gkvkdh.ru

  

|

206.191.***.37

  

206.191.***.42

  

|

美国

  

|

木马回传信息地址

  

|

2021-03-25

  
  
  
##  **四、总结**

本次捕获的木马可以看出来此类木马进行了加固并对代码大量的加密混淆，企图加大病毒分析人员的分析难度。病毒采用开启无障碍辅助服务后台运行防止用户卸载，国内也只是通过此服务来开发抢红包功能，可见病毒制作者的狡猾程度。通过仿冒西班牙邮政快递及全球知名快递，虽然仿冒西班牙邮政快递应用针对的是西班牙境内，但是仿冒全球知名快递应用，也极有可能传播到我国。

君子以思患而豫防之，今天木马出现在西班牙，明天就有可能出现在我国。我们应时刻关注国际国内手机安全局势，恒安暗影实验室也会不断监测，为网络安全、移动安全出一份力。

