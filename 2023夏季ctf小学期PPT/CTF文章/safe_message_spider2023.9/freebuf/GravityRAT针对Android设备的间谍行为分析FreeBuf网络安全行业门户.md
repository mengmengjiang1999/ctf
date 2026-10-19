## **​概述：**

GravityRAT是一款隐秘的间谍软件，从2016年开始就反复被用于针对印度的持续性攻击。在此期间，GravityRAT添加了很多新功能，尤其是文件渗透，远程命令执行，以及反VM技术，使其更难以检测，它可以非常快速地从受感染计算机中窃取大量数据，甚至可以扫描连接到受害设备的外部硬盘驱动器或USB，然后提取这些文件。之前GravityRAT比较注于计算机的恶意攻击，但是研究者发现该木马正增加针对macOS和Android平台的攻击。

近期，恒安嘉新暗影实验室App全景态势与情报溯源挖掘平台监测到一款名为爱欲故事（英文：Lust
Stories）的恶意程序，研究人员分析发现该应用利用用户Android
设备的多个广播事件（开关飞行模，电量，充电状态，开关屏幕等）触发启动恶意服务，然后窃取用户短信箱信息、用户联系人信息、通话记录信息等，并上传至C2服务器，给用户个人隐私造成严重的威胁，同时，研究人员发现该样本GravityRAT家族类的特征，但样本代码并不复杂，推断是GravityRAT针对Android平台的早期版本，本文针对GravityRAT的间谍行为进行披露，防患于未然。

##  **1\. 样本信息**

 **MD5** ：c7b8e65e5d04d5ffbc43ed7639a42a5f

 **包名：** com.example.first

 **应用名：** LustStories

 **安装图标：**

![](https://image.3001.net/images/20201112/1605150618_5faca79aa3584619ee061.png!small)

##  **2\. 恶意行为综述**

该应用以流行影视题材为应用名称，诱导用户安装使用。在用户的使用过程中恶意服务获取用户通话记录信息、用户短信箱信息、用户联系人信息等，并将获取的用户联系人信息、短信箱信息、通话记录信息等保存到指定的文件当中，恶意程序以设备的状态触发恶意服务的条件，通过相应状态的广播触发恶意服务，将包含用户信息的文件上传到指定服务器。

##  **3\. 运行流程图**

该应用以流行影视题材为应用名称，诱导用户安装使用。用户安装后恶意服务获取用户通话记录信息、用户短信箱信息、用户联系人信息等，恶意程序以设备的状态为触发恶意服务的条件，通过相应状态的广播触发恶意服务，获取包含用户短信箱信息、用户联系人信息、用户通话记录信息等用户隐私文件。

![](https://image.3001.net/images/20201112/1605150642_5faca7b22fa0ed8dc53cc.png!small)图3-1
程序运行流程图

#  **4\. 技术原理分析**

###  **4.1 诱导用户安装**

该应用以流行影视题材为应用名称，诱导用户安装使用，用户安装后可正常使用，用户打开界面获取所需信息。

![](https://image.3001.net/images/20201112/1605150688_5faca7e098b868997d18f.png!small)图4-1
诱导用户安装

用户登录应用：

![](https://image.3001.net/images/20201112/1605150711_5faca7f747f5c210ffb79.png!small)图4-2
用户登录

用户进入应用获取内容:

![](https://image.3001.net/images/20201112/1605150743_5faca817a77710d2e3950.png!small)图4-3
向用户展示内容

###  **4.2 程序加载运行**

恶意程序启动恶意服务，恶意服务初始化远控地址，并将获取的信息上传到指定服务器。获取的用户信息前面添加了用户的IMEI字段，用来区分用户信息的来源。

1）恶意程序初始化远控地址：

![](https://image.3001.net/images/20201112/1605150780_5faca83c69c8442e613a3.png!small)图4-4
初始化远控地址

2）恶意服务远控地址:http://n2.norto***dates.online:64443 /FOXTROT/upload.php。

![](https://image.3001.net/images/20201112/1605151767_5facac1702296fcf71c9c.png!small)图4-5
远控地址

3）恶意服务在获取的用户信息前面添加用户IMEI字段，并将带有IMEI的用户信息上传到指定服务地址。

![](https://image.3001.net/images/20201112/1605151152_5faca9b0ebe2dc6789059.png!small)图4-6
上传带有IMEI的用户信息

###  **4.3 恶意行为分析**

恶意程序根据设备的状态发送对应的广播，发送对应的广播启动恶意服务，恶意服务获取用户通话记录信息、用户短信箱信息、用户联系人信息等，将获取的信息上传到指定服务器。

 **4.3.1 恶意程序启动恶意服务**

恶意程序根据设备状态发送广播，发送对应动作广播，启动恶意服务。

1）恶意程序根据设备状态发送广播启动恶意服务。

相关联的动作

  

|

广播类型

  

|

恶意行为

  
  
  
---|---|---  
  
设备关闭屏幕

  

  

|

android.intent.action.SCREEN_OFF

  

|

启动恶意服务

  
  
  
设备打开屏幕

  

  

|

android.intent.action.SCREEN_ON

  

|

启动恶意服务

  
  
  
设备开关飞行模式

  

  

|

android.intent.action.AIRPLANE_MODE

  

|

启动恶意服务

  
  
  
设备电量过低

  

  

|

android.intent.action.BATTERY_LOW

  

|

启动恶意服务

  
  
  
设备电量充足

  

  

|

android.intent.action.BATTERY_OKAY

  

|

启动恶意服务

  
  
  
设备修改日期

  

  

|

android.intent.action.DATE_CHANGED

  

|

启动恶意服务

  
  
  
设备充电

  

  

|

android.intent.action.ACTION_POWER_CONNECTED

  

|

启动恶意服务

  
  
  
设备断开充电

  

  

|

android.intent.action.ACTION_POWER_DISCONNECTED

  

|

启动恶意服务

  
  
  
2）设备关闭屏幕时，设备发送android.intent.action.SCREEN_OFF广播，启动恶意服务，获取用户通话记录、通讯录、短信等内容。

![](https://image.3001.net/images/20201112/1605151181_5faca9cd6472d4a7dd5cb.png!small)图4-8
屏幕关闭发送广播启动恶意服务

3）设备打开屏幕时，设备发送android.intent.action.SCREEN_ON广播，启动恶意服务，获取用户通话记录、通讯录、短信等内容。

![](https://image.3001.net/images/20201112/1605151203_5faca9e3f010636c8cc1d.png!small)图4-9
屏幕打开发送广播启动恶意服务

4）设备开关飞行模式时，设备发送android.intent.action.AIRPLANE_MODE广播，启动恶意服务，获取用户通话记录、通讯录、短信等内容。

![](https://image.3001.net/images/20201112/1605151222_5faca9f6e69c27402886d.png!small)图4-10
飞行模式开关发送广播启动恶意服务

5）设备电量过低时，设备发送android.intent.action.BATTERY_LOW广播，启动恶意服务，获取用户通话记录、通讯录、短信等内容。

![](https://image.3001.net/images/20201112/1605151239_5facaa07ab4309510fe14.png!small)图4-11
电量过低发送广播启动恶意服务

6）设备电量充足时，设备发送android.intent.action.BATTERY_OKAY广播，启动恶意服务，获取用户通话记录、通讯录、短信等内容。

![](https://image.3001.net/images/20201112/1605151256_5facaa1854471a0df4a47.png!small)图4-12
电量充足时发送广播启动恶意服务

7）设备修改日期时，设备发送android.intent.action.DATE_CHANGED广播，启动恶意服务，获取用户通话记录、通讯录、短信等内容。

![](https://image.3001.net/images/20201112/1605151272_5facaa287766bec012262.png!small)图4-13
日期改变发送广播启动恶意服务

8）设备充电时，设备发送android.intent.action.ACTION_POWER_CONNECTED广播，启动恶意服务，获取用户通话记录、通讯录、短信等内容。

![](https://image.3001.net/images/20201112/1605151293_5facaa3d63fa1df77c4a2.png!small)图4-14
设备充电发送广播启动恶意服务

9）设备断开充电，设备发送android.intent.action.ACTION_POWER_DISCONNECTED广播，启动恶意服务，获取用户通话记录、通讯录、短信等内容。

![](https://image.3001.net/images/20201112/1605151310_5facaa4ecbc1c1d030a0b.png!small)图4-15
断开电源发送广播启动恶意服务

 **4.3.2 恶意服务获取用户信息**

恶意服务启动后获取用联系人信息、用户通话记录信息、用户sd目录信息、用户短信信息。

1）恶意服务获取用户联系人信息：

![](https://image.3001.net/images/20201112/1605151327_5facaa5f30e76aa7fc60b.png!small)图4-16
获取用户联系人信息

将获取的联系人信息保存到cs.log当中：

![](https://image.3001.net/images/20201112/1605151360_5facaa803338a35f8bd52.png!small)图4-17
联系人信息保存到cs.log当中

2）恶意服务获取用户通话记录信息：

![](https://image.3001.net/images/20201112/1605151384_5facaa988c212776c95e1.png!small)图4-18
获取用户通话记录

恶意服务将获取到的通话记录保存到cl.log当中：

![](https://image.3001.net/images/20201112/1605151412_5facaab4e99cb0226400b.png!small)图4-19
通话记录保存到cl.log当中

3）恶意服务获取用户sd当中的目录：

![](https://image.3001.net/images/20201112/1605151472_5facaaf0ce8e739b080ac.png!small)图4-20
获取用户sd目录

恶意服务将获取的sd目录信息保存到fsc.log当中：

![](https://image.3001.net/images/20201112/1605151503_5facab0f02b3ea5479436.png!small)图4-21
保存sd卡目录信息

4）恶意服务获取用户短信信息：

![](https://image.3001.net/images/20201112/1605151528_5facab28c52236f04a46f.png!small)图4-22
获取用户短信信息

将获取的短信信息保存到ms.log当中：

![](https://image.3001.net/images/20201112/1605151567_5facab4fb1a67dd94d259.png!small)图4-23
保存用户短信信息

 **4.3.3 上传用户隐私信息**

恶意服务将获取的用户通讯、通话记录、短信上传到指定服务器。服务器地址是：http://n2.nor***pdates.online:64443/FOXTROT/upload.php。

![](https://image.3001.net/images/20201112/1605151592_5facab683e5022c833213.png!small)图4-24
上传用户隐私信息

#  **5\. 扩展分析**

###  **5.1 关联域名**

经远控域名关联分析，此域名还对应其他子域名：

序号

  

|

全域名

  

|

对应域名

  
  
  
---|---|---  
  
1

  

|

n1.nort***dates.online

  

|

norto***dates.online

  
  
  
2

  

|

n2.nort***pdates.online

  

|

norto***dates.online

  
  
  
3

  

|

n3.nort***pdates.online

  

|

norto***dates.online

  
  
  
4

  

|

n4.nort***pdates.online

  

|

norto***dates.online

  
  
  
5

  

|

www.n***nupdates.online

  

|

norto***dates.online

  
  
  
###  **5.2 域名注册更新时间**

根据域名分析发现此域名域名在18年注册，并在2020年6月更新，此组织比较活跃。

![](https://image.3001.net/images/20201112/1605151620_5facab84c02b624dc99f5.png!small)

###  **5.3 域名访问量**

根据最近的域名访问情况来看攻击行为一直持续存在。

日期

  

|

访问量

  
  
  
---|---  
  
2020年10月11日

  

|

2

  
  
  
2020年10月15日

  

|

2

  
  
  
2020年10月20日

  

|

6

  
  
  
2020年10月24日

  

|

2

  
  
  
2020年10月28日

  

|

2

  
  
  
2020年11月5日

  

|

2

  
  
  
##  **6\. 安全建议**

  * 用户安装所需软件，建议去正规的应用市场下载、去官方下载。

  * 在手机当中安装必要的安全软件，并保持安全软件更新。

  * 关注“暗影安全实验室”微信公众号，我们将持续关注安全事件。

#  **7\. 更多信息**

恒安嘉新App全景态势与情报溯源挖掘平台能够检测出此次攻击事件的样本。

![](https://image.3001.net/images/20201112/1605151634_5facab9294f3c1cf14a83.png!small)

目前，恒安嘉新App全景态势与情报溯源挖掘平台针对300多家公开渠道以及非公开渠道进行持续的监测，支持App恶意程序、安全漏洞、违法违规收集使用用户个人信息，威胁内容等方面多维度检测，支持App全维度的情报数据提取，建立App丰富的情报库，并提供专业的检测报告，可以为移动应用开发商、运营商、公安等不同行业提供App安全漏洞检测，恶意程序检测，家族样本聚类，样本关联分析、黑产线索扩展、溯源，大屏展示等专业的服务，同时平台支持私有化部署、SaaS云服务部署。

![](https://image.3001.net/images/20201112/1605151659_5facababca0c3706d9f39.png!small)

  

  

