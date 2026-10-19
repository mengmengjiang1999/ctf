## **一、背景**

2021年刚过完春节，暗影实验室就发现了几个针对印度投放的移动端木马，这些木马从代码结构，到主控地址，到安装名称，再到针对的对象都是极其相似，这是一个有预谋的木马传播事件，APP通过仿冒系统应用或者知名软件诱导用户安装使用，从而获取用户设备上的各种敏感信息。

本次发现的APP大致分为两类：一类是仿冒系统应用，一类是仿冒国外流行的聊天软件。

仿冒系统应用的木马在编译时会特意将自己转为兼容旧版系统的软件，系统的最低兼容版本会降低到Android4，这样APP在安装时就会自动授权所有权限，防止出现系统应用向用户索要权限的不合理现象。

仿冒国外知名软件的木马则是会通过相同或者相似的安装名诱导用户下载安装，然后伪造登录、联系人、聊天等页面，用户进行操作时触发相应的权限请求，使得木马可以获取设备上的信息。

##  **二、木马分析**

###  **2.1 信息汇总**

本次发现的APP主要伪装成系统Settings应用、WhatsApp以及BoltChat应用。

 **MD5**

  

|

 **安装名**

  

|

 **图标**

  

|

 **最低兼容版本**

  
  
  
---|---|---|---  
  
D2A9B362FDF56C10BB89C8164A779601

  

|

Settings

  

|

![](https://image.3001.net/images/20210312/1615516201_604ad229087b13e3074ca.png!small)

  

|

Android4.0.3

  
  
  
F6B028CCC8A872AD5EB3D9A36020ADAC

  

|

Settings

  

|

![](https://image.3001.net/images/20210312/1615516201_604ad229087b13e3074ca.png!small)

  

|

Android4.1

  
  
  
Cc4D7B39DEC5335E209F80A3C212A6BA

  

|

Whats app

  

|

![](https://image.3001.net/images/20210312/1615516230_604ad2467b49571838b1a.png!small)

  

|

Android4.4

  
  
  
976743EDF6BCC12BB0349B3EA11AAB2F

  

|

Chat Bolt

  

|

![](https://image.3001.net/images/20210312/1615516255_604ad25f672437cf5dc63.png!small)

  

|

Android4.4

  
  
  
579B9C358475B9E45D91A06DF58493D6

  

|

Chat Bolt

  

|

![](https://image.3001.net/images/20210312/1615516255_604ad25f672437cf5dc63.png!small)

  

|

Android4.4

  
  
  
BF5CC683A34F697AFFEC1AEF221CCB30

  

|

Whs app

  

|

![](https://image.3001.net/images/20210312/1615516230_604ad2467b49571838b1a.png!small)

  

|

Android4.4

  
  
  
BB8E05EC8B15EFA2F9D5B66DE1A7EB1D

  

|

WhatsApp lite

  

|

![](https://image.3001.net/images/20210312/1615516230_604ad2467b49571838b1a.png!small)

  

|

Android5.0

  
  
  
02A121AEA1BFB7B0684462B112C82552

  

|

AF News

  

|

![472_1615453897_86.png](https://image.3001.net/images/20210311/1615456671_6049e99fee08ea357d8d3.png!small)

  

|

Android4.4

  
  
  
###  **2.2 运行分析**

运行本次发现的木马发现其界面简单，仿冒聊天类得APP界面上登录的手机号前缀国家代码均是91，为印度境内所属。

![](https://image.3001.net/images/20210311/1615456064_6049e740c58d011a2933b.png!small)图1-1仿冒应用的登录界面

除了仿冒Settings的应用没有登录等操作外，其余仿冒APP均有一个url处理登录、APP联系人等逻辑，主服务器地址经过整理发现两个：

> http://www.iwil***you.com
>
> https://cha***sion.000w***ostapp.com/application

经过抓包佐证了分析结果：IP地址均位于境外。

![](https://image.3001.net/images/20210311/1615455975_6049e6e7b855c9135c46c.png!small)图1-2
数据传输

###  **2.3 指令解析**

 **2.3.1 指令获取**

木马指令的获取有一些变化，大致分为两种，一类是硬编码在APP中，包括明文编写和base编码，另一种经过了改进，通过一个固定网址下载配置文件获得主控地址。

1）硬编码地址

一部分APP以字符串的形式明文编写在代码中，如下图：

![](https://image.3001.net/images/20210311/1615456003_6049e703d3500b0642466.png!small)

图1-3 服务器地址硬编码

还有一种以base64编码的形式存储：

![](https://image.3001.net/images/20210311/1615456089_6049e7595af7a7370ec95.png!small)图1-4
服务器地址base64编码

经过整理，主控地址主要有以下几个：IP地址均位于荷兰境内。

> 178.132.***.230:5987
>
> 109.236.***.16:5987
>
> O***1.d***s.net:5987
>
> My***xyz.d***s.net:5987

2）配置文件读取

通过APP中base64编码的url获得配置文件：http://trya***horse.com/config.txt，

读取第一行作为真实主控地址，这样可以任意变更主控地址而APP无需改动。

![](https://image.3001.net/images/20210311/1615456131_6049e7836302a45a3af0e.png!small)图1-5
从配置文件获取主控地址

 **2.3.2 oder指令**

下图是不同功能的order指令，一共八种。

![](https://image.3001.net/images/20210311/1615456155_6049e79b85f09d968b95c.png!small)图1-6
远控命令脑图

3）x0000fm

extra 如果是ls则获得path字段，获取该字段下的目录文件列表：

![](https://image.3001.net/images/20210311/1615456178_6049e7b2cef41c48ba409.png!small)图1-7
获取目录文件列表

extra 如果是dl则获得path字段，上传该path指定的文件至服务器：

![](https://image.3001.net/images/20210311/1615456199_6049e7c74942df6f82d57.png!small)图1-8
上传指定路径文件至服务器

4）x000adm

收到该指令后APP上传设备的通讯录、短信、log日志、几个特定目录（包括Records、Download、DCIM/Camera、Documents、WhatsApp/Media/WhatsAppImages、WhatsApp/Media/WhatsAppDocuments）下的文件。

![](https://image.3001.net/images/20210311/1615456239_6049e7ef09414bcdf3421.png!small)![](https://image.3001.net/images/20210311/1615456252_6049e7fc2c6047f64d194.png!small)![](https://image.3001.net/images/20210311/1615456268_6049e80c0bc8fe30da20c.png!small)![](https://image.3001.net/images/20210311/1615456280_6049e818928546cf6da91.png!small)图1-9
上传设备的通讯录、短信、log日志、目录文件

5）sms

![](https://image.3001.net/images/20210311/1615456297_6049e82910069edf1b135.png!small)图1-10
sms命令

extra如果是ls则获取短信列表：

![](https://image.3001.net/images/20210311/1615456317_6049e83d990f4aba6e184.png!small)图1-11
获取短信列表

extra如果是sendSMS则发送指定内容的短信到指定手机号：

![](https://image.3001.net/images/20210311/1615456339_6049e8530bc21b18ac3bf.png!small)图1-12
发送短信

extra如果是deleteSMS则删除指定内容的短信：

![](https://image.3001.net/images/20210311/1615456361_6049e869663edddce0f64.png!small)图1-13
删除短信

6）x0000cl

收到该指令则获取设备的通话记录上传到服务器：

![](https://image.3001.net/images/20210311/1615456398_6049e88eeb301f220bf0d.png!small)图1-14
获取通话记录

7）x0000cn

收到该指令则获取通讯录列表将手机号姓名上传到服务器：

![](https://image.3001.net/images/20210311/1615456418_6049e8a2275e0d0d15c10.png!small)图1-15
获取通讯录

8）x0000mc

该指令获取extra字段然后细分为三个子指令：au、mu、muS：

![](https://image.3001.net/images/20210311/1615456449_6049e8c1c9203c0463ab5.png!small)图1-16
extra字段子指令

extra如果是au则获取sec字段，录制sec秒的音频，保存为sound.mp3，然后上传服务器：

![](https://image.3001.net/images/20210311/1615456472_6049e8d8bf9b5a7a6e243.png!small)图1-17
录制音频，保存为sound.mp3

extra如果是mu，则执行立即停止录音的操作，然后将录音文件上传服务器，并删除该文件：

![](https://image.3001.net/images/20210311/1615456503_6049e8f7d9ba99996f820.png!small)图1-18
上传录音文件，并删除保存在本地的录音文件

extra如果是muS，则开启录音，并把该次录音取名sound.mp3：

![](https://image.3001.net/images/20210311/1615456521_6049e909016a5b24a606a.png!small)图1-19
开启录音按钮

9）x0000lm

APP收到该指令则获取用户设备的地理位置上传到服务器：

![](https://image.3001.net/images/20210311/1615456545_6049e921ccc4e6303b0c7.png!small)图1-20
获取地理位置信息

10）x000upd

APP收到该指令则获取path字段，到指定的网址获取APP，下载到本地以system.apk命名，并启动APP安装程序：

![](https://image.3001.net/images/20210311/1615456565_6049e9356d80143429df2.png!small)图1-21
下载安装其它应用程序

 **2.3.3 上传服务器地址**

目前发现上述指令文件上传的服务器地址有两个，分别通过不同的方式保存，一个是通过base64编码存储，解码后的地址为：http://178.132.***.230:80/server/upload.php

![](https://image.3001.net/images/20210311/1615456581_6049e9451ad690550e25a.png!small)图1-22
base64编码保存的服务器地址

一个是直接明文写在代码中，地址为：http://212.8.***.221:80/server/upload.php：

![](https://image.3001.net/images/20210311/1615456596_6049e9548194fc9bc4a08.png!small)图1-23
明文保存的服务器地址

##  **三、服务器整理**

将以上获得的服务器地址进行整理：IP地址归属地均位于境外。

> 212.8.***.221:80
>
> 178.132.***.230:80
>
> 178.132.***.230:5987
>
> 109.236.***.16:5987
>
> obs1.d***s.net:5987
>
> mya***xyz.d***s.net:5987
>
> trya***rhorse.com
>
> www.iwil***eyou.com
>
> cha***rsion.00***hostapp.com

以下两个地址目前指向同一页面：

> http://www.iwil***reyou.com/
>
> https://cha***sion.000w***tapp.com/application/

![](https://image.3001.net/images/20210311/1615456648_6049e9880f8658ae03b2c.png!small)图1-24
服务器后台页面

##  **四、总结**

本次捕获的木马可以看出来在不断的改进，从单纯的明文编码到base64编码隐藏主要地址，再到通过中间服务器获取主控地址，应用虽然针对的是印度，但是安全无国界，恶意应用需要我们时刻警惕，恒安暗影实验室也会不断监测，为网络安全、移动安全出一份力。

