**导读：“土耳其轰炸美盟友”、“伊朗游轮被炸”等一系列的重大事件的发生无疑显示出中东地区紧张的局势。此时此刻的中东犹如一个**桶，一不小心就会出现战争风险。不过，中东局势虽然很乱，但也主要是两大利益集团控制着局面：一个是以美国、以色列、沙特等为攻的集团，一个是以俄罗斯、伊朗和叙利亚等为守的集团。伊朗作为其中势力强大的国家之一，纵然会成为敌对国家的攻击目标。**

近期，暗影移动安全实验室在日常监测中，发现了一款中文名叫“费雷顿·莫希里”的间谍木马软件，研究人员分析发现，该软件是专门针对伊朗开发的，其主要目的是窃取情报。样本启动后并没有任何效果，但它却默默地在后台远程的监控用户行为，比如录视频、对通话过程录音、拍摄照片等，还会收集用户通讯录联系人、短信息、精确位置、浏览器记录、账户等信息，并将收集的信息上传到指定的服务器。

![201910141137216141018145_html_17b781c5.p](http://image.3001.net/2019/10/8bed7bb2e70cf0c435bb7780214abfdc.png)

图1 “费雷顿·莫希里”的安装图标

## 一、基本信息

> 样本MD5：43BD113A0952172BCBA57055F5A707BB
>
> 安装名称：فریدونمشیری
>
> 中文名：费雷顿·莫希里
>
> 样本包名：air.com.arsnetworks.poems.moshiri

## 二、运行原理

该样本通过电量变化广播唤醒恶意服务AMService，然后在AMService服务中监听大量系统广播（如：网络变化广播、短信广播、电话拨号广播、电话关机广播、），监听数据库的变化（如：短信数据库、浏览器书签数据库），激活各种恶意行为，其运行过程主要分两步，第一步是通过各种系统广播，监听用户手机动态，保证恶意程序在后台持续运行。并对用户通话记录进行录音、收集用户通讯录、接收的短信、浏览器记录、联系人、账号、安装应用等信息；然后上传到指定服务器，第二步是从远程服务器获取大量的控制指令，然后根据控制指令执行收集用户信息，通过录制视频以及拍摄照片监控用户行为，上传持续收集的情报、并删除指定文件等操作。

![图片1.png](https://image.3001.net/images/20191018/1571383247_5da967cf35559.png!small)图2
样本运行流程图

## 三、代码分析

### 3.1启动恶意服务，监听大量系统广播

启动恶意服务AMService，监听用户手机短信数据库变化、浏览器书签数据库变化、基站信息变化、注册网络变化广播、接收短信广播、电话拨号拦截广播。

![图片1.png](https://image.3001.net/images/20191018/1571383354_5da9683adc4bc.png!small)图3
监听系统广播

### 3.2窃取用户隐私数据

注册接收短信广播，监听短信数据库变化，不管是接收短信、发送短信、编辑短信，短信数据库都会发生变化，当短信数据库发生变化或用户接收到短信时，该程序收集用户的短信号码和短信内容，并且将内容保存至log文件。

![图片2.png](https://image.3001.net/images/20191018/1571383374_5da9684ecfaea.png!small)图4
监听短信变化，收集短信号码和内容

![图片3.png](https://image.3001.net/images/20191018/1571383388_5da9685cf3279.png!small)图5
收集用户接收的短信号码和内容

注册电话拨号广播，当电话为来电状态时，匹配来电号码的尾号，如果号码匹配上，且用户已接听（从此看出攻击者是有目的性针对特定号码进行攻击。），将开始对通话过程进行录音。

![图片4.png](https://image.3001.net/images/20191018/1571383496_5da968c814fac.png!small)图6
对用户通话过程录音

监听浏览器书签数据库变化，获取用户网页浏览记录。

![图片5.png](https://image.3001.net/images/20191018/1571383510_5da968d67599e.png!small)图7
获取用户网页浏览记录

监听基站信息变化，保存基站经纬度信息。

![图片6.png](https://image.3001.net/images/20191018/1571383540_5da968f498e12.png!small)图8
获取基站经纬度信息

获取用户所有短信信息、联系人信息、通话记录信息、账号信息、Google浏览器书签信息。

![图片1.png](https://image.3001.net/images/20191018/1571383616_5da9694075fbf.png!small)图9
获取短信、通讯录、通话记录、账号、浏览器书签等信息

将获取的所有信息通过AES算法加密并保存至后缀名为log的文件。

![图片2.png](https://image.3001.net/images/20191018/1571383662_5da9696e760b3.png!small)图10
保存用户信息到指定文件（后缀为.log）

获取所有后缀名为.log的文件，并上传至服务器。

[http://www.](http://www./)*****.com/mmh/upload-log.php。

![图片3.png](https://image.3001.net/images/20191018/1571383684_5da96984512c3.png!small)图11
上传保存获取信息的文件

![图片4.png](https://image.3001.net/images/20191018/1571383701_5da9699595cc1.png!small)图12
截获的数据包

### 3.3远程控制行为

该样本从指定服务器获取控制端下发的指令，通过一级指令和二级指令，双重控制。

服务器URL:[http://www.](http://www./)****/mmh/get-function.php?uuid=14768afcde85653d

![图片5.png](https://image.3001.net/images/20191018/1571383721_5da969a9018eb.png!small)图13
加载远程服务器

控制指令思维导图：

![图片6.png](https://image.3001.net/images/20191018/1571383732_5da969b4c1757.png!small)图14
控制指令思维导图

远控指令详细解析:

一级指令”Get”，修改配置文件。

![图片1.png](https://image.3001.net/images/20191018/1571383836_5da96a1ce6070.png!small)图15
修改配置文件

一级指令”Get”，二级指令”AllLog”，导出.log文件。

![图片2.png](https://image.3001.net/images/20191018/1571383854_5da96a2e14fb8.png!small)图16
导出.log文件。

一级指令”Get”，二级指令”AllContact”，获取所有联系人信息。

![图片3.png](https://image.3001.net/images/20191018/1571383924_5da96a746a3fb.png!small)图17
获取所有联系人信息。

一级指令”Get”，二级指令”AllFile”，获取所有文件。

![图片4.png](https://image.3001.net/images/20191018/1571383940_5da96a84006cf.png!small)图18
获取所有文件。

一级指令”Get”，二级指令”AllSms”，获取所有短信信息。

![图片5.png](https://image.3001.net/images/20191018/1571383956_5da96a94a4b34.png!small)图19
获取所有短信信息

一级指令”Get”，二级指令”AllCall”，获取所有通讯录信息。

![图片6.png](https://image.3001.net/images/20191018/1571383972_5da96aa44657e.png!small)图20
获取所有通讯录信息

一级指令”Get”，二级指令”AllApp”，获取手机已安装应用信息。

![图片1.png](https://image.3001.net/images/20191018/1571384069_5da96b059a071.png!small)图21
获取手机已安装应用信息

一级指令”Get”，二级指令”AllBrowser”，获取用户浏览器记录。

![图片2.png](https://image.3001.net/images/20191018/1571384125_5da96b3d57388.png!small)图22获取用户浏览器记录

一级指令”Get”，二级指令”AllAccount”，获取用户所有账号。

![图片3.png](https://image.3001.net/images/20191018/1571384142_5da96b4e9f709.png!small)图23
获取用户所有账号

一级指令”Get”，二级指令”AllSetting”，获取设置信息。

![图片4.png](https://image.3001.net/images/20191018/1571384155_5da96b5b1d799.png!small)图24
获取设置信息

一级指令”Get”，二级指令”Location”，获取精确位置信息。

![图片5.png](https://image.3001.net/images/20191018/1571384229_5da96ba560c01.png!small)图25
获取精确位置信息

一级指令”Get”，二级指令”HardwareInfo”，获取设备硬件信息。

![图片6.png](https://image.3001.net/images/20191018/1571384189_5da96b7dc4c78.png!small)图26
获取设备硬件信息

一级指令”Get”，二级指令”File”，更新从控制端获取的指定文件内容，并发送到服务器。

![图片1.png](https://image.3001.net/images/20191018/1571384322_5da96c0238f81.png!small)图27
更新从控制端获取的指定文件内容

一级指令”Take”，二级指令”Audio”，录音并保存至/sdcard//Android/data/com.android.browser/files目录。

![图片2.png](https://image.3001.net/images/20191018/1571384341_5da96c159edea.png!small)图28
录音

一级指令”Take”，二级指令”Audio”，录制视频并保存至/sdcard//Android/data/com.android.browser/files目录。

![图片3.png](https://image.3001.net/images/20191018/1571384349_5da96c1d3de03.png!small)图29
录制视频

一级指令”Take”，二级指令”Photo”，拍摄照片并保存至/sdcard//Android/data/com.android.browser/files目录。

![图片4.png](https://image.3001.net/images/20191018/1571384379_5da96c3ba38ec.png!small)图30拍摄照片

一级指令”Delete”，二级指令”SMS”，删除短信。

![图片5.png](https://image.3001.net/images/20191018/1571384390_5da96c4677f0f.png!small)图31
删除短信

一级指令”Delete”，二级指令”Call”，删除通讯录。

![图片6.png](https://image.3001.net/images/20191018/1571384417_5da96c61a4c4f.png!small)图32
删除通讯录

一级指令”Delete”，二级指令”File”，删除控制端指定的文件。

![图片1.png](https://image.3001.net/images/20191018/1571384448_5da96c80297e0.png!small)图33
删除控制端指定的文件

一级指令”Reset”，二级指令”AllCommand”，将保存所有获取信息的文件上传到服务器后，删除所有文件。

![图片2.png](https://image.3001.net/images/20191018/1571384464_5da96c9052ea1.png!small)图34
删除所有保存获取信息的文件

## 四、同源分析

通过对费雷顿·莫希里应用样本的分析，我们发现了一批与该样本拥有同样文件框架的家族样本。他们的攻击目标都是伊朗，且通过仿冒与伊朗当地文化相关的应用名来骗取用户安装使用，从而在后台远程监控用户行为，窃取用户隐私数据。以下为部分同源样本信息。

表4-1同源样本信息

MD5| 安装名称| 包名  
---|---|---  
4567824a45a818bc389d7eeae3c7b678| جهاددراسلام| jehaddareslam.sunnibook.net  
CC88F21406EAEED70A890F53E57C98B6| صور شهر رمضان| com.ramadan.kareem.app  
FBD0AFE5BD3D0D61FEB21680B304D7AE| ندائےحق اردو| com.nidayehaq  
86da3a7378e17b51ba83ba3333e86a32| حکم بما انزل الله| ir.hukmi.moanzalalloh  
155316526FF476698494E90EFC1127BC| Iranian Woman Ninja| com.coolwallpapers  
AC32FFAA379AED78DCC11EA74FBDFCFE| کوروش بزرگ| ir.korosh.kabir  
D199C202BEB4380E2F675E93C36CF0F4| سهراب سپهری|
air.com.arsnetworks.poems.sohrab  
f05d8588cf2e8be9fa6ccac39a0f7311| کوروش بزرگ!| ir.cheshmac.CyrustheGreat  
3c0011dd7f6c9474cda5ffd52415d4a8| توبيكات سعادة و فرح| gemy.saadaa  
05eaa04bc27db3af51215d68a1d32d05| Exotic Flowers|
com.majorityapps.exoticflowers  
  
### C&C服务器地址：

> [http://www.](http://www./)****.com/mmh/upload-log.php
>
> [http://www.](http://www./)****.com/mmh/answer.php
>
> [http://www.](http://www./)****.com/mmh/get-> function.php?uuid=de39361c255e9af2

## 五、安全建议

信息化时代的到来，使国家之间的战争从武器战争上升为网络战争。所以个人信息的安全不仅关乎到自身的安全，更关乎到国家的安全。建议大家慎重向外提供隐私信息，慎重从其它不安全渠道下载应用软件。

