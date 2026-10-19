## 概述：

疫情还未结束，欺诈者就已经蠢蠢欲动，年中时分，KBuster团伙再次发力，非法获取大量用户数据。

近期 **恒安嘉新暗影安全实验室** 通过 **APP** **全景态势与案件情报溯源挖掘系统**
，发现KBuster组织针对韩国地区进行的仿冒金融机构的最新钓鱼活动，此次攻击活动从2019年12月开始持续到2020年8月，攻击者可能来自荷兰。该组织会利用xampp框架搭建钓鱼网站向外传播仿冒APP。经分析发现该类软件具有信息窃取、远程控制和系统破坏的恶意行为。此次攻击活动利用的样本，包名具有明显的相似性；窃取用户信息时，利用FileZilla生成FTP服务器,用于接收用户信息，服务器上绑定有大量的连续ip地址，形成ip地址池，推测用于链接防封，从而稳定地获取用户信息，使用了如此多的网络基础资源，也从侧面印证了该组织财力可观。

![](https://image.3001.net/images/20210108/1610094448_5ff817700c6cb72e3977d.png!small)

##  **1\. 程序运行流程图**

恶意程序运行主要分为两大功能，第一种功能会仿冒金融结构，诱导用户填写个人信息，利用提示信息诱骗用户拨打电话联系咨询员，并自动监听手机通话状态，利用黑名单来自动挂断指定号码；第二种功能会获取个人敏感信息，包括用户通讯录、短信、通话记录等个人信息上传到指定服务器，还会获取用户保存在SD卡上的各种文件（如doc、xlsx、pdf等），并且有意识的收集韩国本土办公软件的文件（如hwp类型）；该软件还留有远控模块，方便日后升级与持续获取信息。

![](https://image.3001.net/images/20210108/1610094473_5ff81789d6ce46c2c21cf.png!small)图1-1
程序运行流程图

此次活动，利用的样本包名相似度极高，具有一定的命名规律，都会包含要仿冒的金融机构的缩写和一串数字组成：

![](https://image.3001.net/images/20210108/1610094504_5ff817a8a1cbae7ca3ff4.png!small)图2-1
包名对比

##  **2\. 样本基本信息**

本次以“현대캐피탈”软件为例进行分析。

程序名称

  

|

현대캐피탈

  
  
  
---|---  
  
程序包名

  

|

com.hd7202008056.activity1

  
  
  
程序MD5

  

|

1D937D1E0E95B3258B309EF35CC61F3E

  
  
  
签名信息

  

|

EMAILADDRESS=android@android.com, CN=Android, OU=Android, O=Android,
L=Mountain View, ST=California, C=US

  
  
  
签名MD5

  

|

8DDB342F2DA5408402D7568AF21E29F9

  
  
  
图标

  

|

![927_1610090805_776.png](https://image.3001.net/images/20210108/1610095325_5ff81add77f0216b02d23.png!small)

  
  
  
##  **3\. 技术原理分析**

###  **3.1 仿冒金融机构**

仿冒金融机构的应用图标。

![](https://image.3001.net/images/20210108/1610094540_5ff817cc319d0334d6b21.png!small)图2-2
仿冒金融机构的应用图标（部分展示））

程序启动后加载本身携带的仿冒界面：

![](https://image.3001.net/images/20210108/1610094569_5ff817e9603c4244928c6.png!small)

![](https://image.3001.net/images/20210108/1610094590_5ff817fee7991fbf83997.png!small)图2-3
加载的仿冒页面

###  **3.2 程序恶意行为**

（1）忽略电池优化，保障应用在后台正常运行。

![](https://image.3001.net/images/20210108/1610094614_5ff81816a072adf7effca.png!small)图2-4
忽略电池优化

（2）设置主要服务开机自启，用于进程保活：

![](https://image.3001.net/images/20210108/1610094637_5ff8182d61b1ffc35b212.png!small)图2-5
服务自启

（3）获取手机号码等固件信息经过BASE64加密后进行上传：

![](https://image.3001.net/images/20210108/1610094667_5ff8184b4fee1b70635fb.png!small)![](https://image.3001.net/images/20210108/1610094687_5ff8185f0feba9b438601.png!small)![](https://image.3001.net/images/20210108/1610094718_5ff8187e2c220cc3cf39d.png!small)图2-6
上传基本信息

（4）获取已安装应用列表进行上传：

![](https://image.3001.net/images/20210108/1610094752_5ff818a0ce78231123884.png!small)![](https://image.3001.net/images/20210108/1610094768_5ff818b0c5723abe13bd9.png!small)图2-6
上传应用列表

（5）监听通话状态，通过黑名单挂断指定电话：

![](https://image.3001.net/images/20210108/1610094830_5ff818ee92c883a759682.png!small)![](https://image.3001.net/images/20210108/1610094846_5ff818fe3afbd796a880a.png!small)图2-7
挂断指定电话

（6）对外呼电话进行录音并保存本地，等待上传：

![](https://image.3001.net/images/20210108/1610094867_5ff819137dd2e7607e5b1.png!small)图2-8
通话录音

（7）程序留有远控模块，方便后期更新和持续获取信息：

![](https://image.3001.net/images/20210108/1610094902_5ff81936e8fb5e907305d.png!small)图2-9
解析指令

指令列表：

 **服务器**

  

|

 **远控指令**

  

|

 **对应操作**

  
  
  
---|---|---  
  
http://110.173.***.10:3500/socket.io

  

|

update

  

|

安装升级包

  
  
  
x0000mc sec

  

|

设置时间，定时录音并上传，然后删除录音文件

  
  
  
order_x0000lm

  

|

上传地理位置信息

  
  
  
order_x0000cn

  

|

上传通讯录

  
  
  
order_liveSM

  

|

上传短信

  
  
  
liveCallHistory

  

|

上传通话记录

  
  
  
addContact

  

|

插入通讯录联系人

  
  
  
deleteContact

  

|

删除指定通讯录联系人

  
  
  
order_getAppList

  

|

上传应用列表

  
  
  
permission

  

|

请求通讯录、监听短信、读取通话日志、获取精准位置、录音等权限

  
  
  
serverRestart

  

|

重启SmartService

  
  
  
file extra=del

  

|

删除指定文件

  
  
  
file extra=all

  

|

上传指定类型的所有文件到ftp服务器

  
  
  
file extra=up

  

|

获取文件

  
  
  
file extra=ls

  

|

获取指定文件列表

  
  
  
file extra=dl

  

|

上传指定文件

  
  
  
 **3.3 上传用户个人信息**

（1）程序通过FTP服务器，将获取的用户短信、通讯录、通话记录、录音文件加密后进行上传。

![](https://image.3001.net/images/20210108/1610094928_5ff819504a55c6a82c2e8.png!small)图2-10
获取短信

![](https://image.3001.net/images/20210108/1610094952_5ff819681d9de56f181f2.png!small)图2-11
获取通讯录

![](https://image.3001.net/images/20210108/1610094971_5ff8197b158e4b48c8832.png!small)图2-12
获取通话记录

![](https://image.3001.net/images/20210108/1610094993_5ff81991d4e7ade0d8a41.png!small)图2-13
进行上传

（2）该程序包含有三个专门用于接收个人隐私信息的FTP服务器地址，服务器上包含有大量用户数据，根据上传日期判断，最早在2020年5月开始进行收集用户数据。

![](https://image.3001.net/images/20210108/1610095037_5ff819bd786c79e4d167e.png!small)图2-14
上传的用户数据

![](https://image.3001.net/images/20210108/1610095055_5ff819cf0bb61a3064fb2.png!small)图2-15
数据解密

 **3.4 上传SD卡信息**

（1）程序会在SD卡中搜索hwp、doc、docx、dwg、xls、xlsx、ppt、pptx、pdf、eml、msg、email、rar、zip、egg、7z、alz、iso格式的文件进行上传。

![](https://image.3001.net/images/20210108/1610095098_5ff819faeb985f8e7dc44.png!small)图2-16
获取的文件类型

（2）该程序有一个专门用于接收用户文件的FTP服务器:

![](https://image.3001.net/images/20210108/1610095114_5ff81a0af1b334ef5d847.png!small)图2-17
上传的用户文件（包含doc、xlsx、pdf、hwp等文件）

![](https://image.3001.net/images/20210108/1610095133_5ff81a1d4764f1e348017.png!small)图2-18
FTP通信

## 4 **. 服务器溯源**

![](https://image.3001.net/images/20210108/1610095148_5ff81a2cd5455633e2a79.png!small)

（1）该软件使用的服务器，ip归属地为香港，端口采用3500，首次访问会要求使用websocket协议进行连接。

url：http://110.173.***.10:3500/socket.io

ip地址：110.173.***.10

![](https://image.3001.net/images/20210108/1610095178_5ff81a4a217cd6498b99c.png!small)图3-1
ip归属地

##  **5\. 样本信息**

 **MD** **5**

|

 **包名**  
  
---|---  
  
D391AF6A1DA2A0BBCCFD74FB3773572FC1F564BB

|

com.hd7202008056.activity1  
  
77F4488E0BB62AAC51A59DF7c4C2A74C6F56FE26

|

com.aju1202008103.activity1  
  
C1456AE93EE7D80A4873F39A71360E51A59A2F12

|

com.dws1202008116.activity1  
  
8D517CFE95184B943DC16D3C6A0E4F72B3217EB7

|

com.hn15202008116.activity1  
  
95A8188E38619D1CE60A7E778C7A3A53CA19D71C

|

com.hd7202008116.activity1  
  
09AFAEF467F2C01F65BF3FA2FFBB5FC7B80B6359

|

com.jb4202008116.activity1  
  
F08844E8CDB9B738CBE5722DC60054978871D256

|

com.jtc1202008116.activity1  
  
F3F720E673DAF2301361D5A81B564D24DC5C5443

|

com.kb38202008116.activity1  
  
995EEEBA1D4A9DB38E5D7313481BAA9DD1FC9EFE

|

com.kbc9202008116.activity1  
  
C9DBC9A26363C1D279138AD61A09B13D2E8E655F

|

com.kbs15202006053.activity  
  
2028D6BEF399025588D326D9DB400A542FFCBB1F

|

com.nh1202008116.activity1  
  
B12C3BB2E5B0B281F1E9B229FAA8A7F95CBF908E

|

com.ok10202008116.activity1  
  
389A28F63F8F5EC58C5EAFCD218AF5F6C3D5801D

|

com.sbi3202008116.activity1  
  
2ED81CBF395F20BEA5139C33A67602CB2B5C36F1

|

com.shs12202008116.activity1  
  
 **URL**  
  
---  
  
http://110.173.***.10:3500/socket.io  
  
http://148.66.***.202:3500/socket.io  
  
http://112.121.***.146:3500/socket.io  
  
http://112.121.***.178:3500/socket.io  
  
http://112.121.***.194:3500/socket.io  
  
http://216.118.***.250:3500/socket.io  
  
##  **6\. 安全建议**

  * 让你的设备保持最新，最好将它们设置为自动补丁和更新，这样即使你不是最熟悉安全的用户，你也能得到保护。

  * 坚持去正规应用商店下载软件，避免从论坛等下载软件，可以有效的减少该类病毒的侵害。关注”暗影实验室”公众号，获取最新实时移动安全状态，避免给您造成损失和危害。

  * 安装好杀毒软件，能有效的识别已知的病毒。

