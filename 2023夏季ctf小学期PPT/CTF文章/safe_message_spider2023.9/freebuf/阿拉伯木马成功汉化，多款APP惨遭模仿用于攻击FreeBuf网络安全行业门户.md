##  **概述**

**近日，奇安信病毒响应中心在日常样本监控过程中发现了一批伪装成点读通.apk、作业帮.apk、手机找回.apk、PUBG.apk等国内用户常用软件的MobiHok家族样本。**

样本在执行过程中为了迷惑用户会安装内置的正规APK，真正的恶意程序则隐匿执行，用户在此过程中一般感觉不到异常，从而窃取用户短信、联系人、通话记录、地理位置、键盘记录、文件目录、应用信息、手机固件信息、录音、录像、截屏、拨打电话、发送短信等。

基于奇安信的多维度大数据关联分析，我们已经发现国内有用户中招，为了防止危害进一步扩散，我们对该远控木马进行了详细分析，并给出解决方案。

##  **MobiHokRAT** **简介**

MobiHok最早在2019年七月份在地下论坛中被发现，售卖者名为“Mobeebom”，除了在多个阿·拉伯语地下论坛活跃之外，售卖者还通过FaceBook、youtube进行宣传，在FaceBook进行宣传时同样使用了阿拉伯文。

![](https://image.3001.net/images/20200103/1578032414_5e0edd1e41a34.png!small)

YouTube中拍摄了各个版本的运行视频和一些安全机制绕过方法：

![](https://image.3001.net/images/20200103/1578032423_5e0edd2742ce1.png!small)

目前V4版本已经免费，在其官网上可以下载，其余版本收费情况如下，价格不菲：

![](https://image.3001.net/images/20200103/1578032432_5e0edd30c4329.png!small)

相关证据表明在V4版本免费之后，国内使用该家族的团伙逐渐变多，且V4版本就可以绕过华为、三星、Google
Play安全机制和FaceBook身份验证。奇安信监控的数据如下：

![](https://image.3001.net/images/20200103/1578032440_5e0edd38e5f20.png!small)

V4版本主控端界面如下：

![](https://image.3001.net/images/20200103/1578032448_5e0edd401847f.png!small)

Mergin App项中可以嵌入任意正规APP。

##  **样本分析**

相关样本如下：

![](https://image.3001.net/images/20200103/1578032467_5e0edd53ec733.png!small)

申请的权限：

![](https://image.3001.net/images/20200103/1578032502_5e0edd76d2029.png!small)

该远控APK木马功能复杂，在执行过程中会运行内置正规Apk软件来迷惑用户，可以从资源中dump出正规的apk文件：

![](https://image.3001.net/images/20200103/1578032511_5e0edd7f95773.png!small)

安装后为作业帮app：

![](https://image.3001.net/images/20200103/1578032521_5e0edd896d16b.png!small)

而木马则在手机中隐秘执行，监听电池变化的广播，每当电池电量有变化时，计算百分比，并获取充电类型：

![](https://image.3001.net/images/20200103/1578032529_5e0edd91931a9.png!small)

获取手机网络链接类型：

![](https://image.3001.net/images/20200103/1578032536_5e0edd98c0e5f.png!small)

测试是否能访问[www.google.com：](http://www.google.com/)

![](https://image.3001.net/images/20200103/1578032545_5e0edda197a0d.png!small)

查看屏幕保护的状态：

![](https://image.3001.net/images/20200103/1578032553_5e0edda9b20c6.png!small)

会静默安装内置的正规APP，并启动：

![](https://image.3001.net/images/20200103/1578032560_5e0eddb0c66bc.png!small)

kforniwwsw0类作为服务在MainActivity中被调用，连接远程C2服务器：

![](https://image.3001.net/images/20200103/1578032566_5e0eddb6f2b06.png!small)

远控功能列表整理如下

指令参数  |  指令功能  
---|---  
calls_delete  |  删除通话记录  
OpenApp  |  打开指定app  
KeyStart  |  配置相关  
ViewFile  |  文件查看  
WriteFiles  |  文件写入  
fcbkopen()  |  创建子目录  
ConnectedDownloadManager  |  指定URL下载者  
AccountManager()  |  账户管理  
MicrophoneStop()  |  麦克风停止  
ViewFileVideoPlay  |  浏览视频文件  
PlayStop  |  停止播放  
Apps()  |  枚举安装的app  
DelLog  |  删除日志  
GetLog  |  获取日志  
gglopen()  |  获取指定app信息  
SaveEdit  |  保存编辑  
REHost  |  修改Host  
StartServiceGLocation()  |  启动位置服务  
CompressFiles  |  压缩文件  
DownManager  |  下载者  
CallsManager()  |  通话记录管理  
DDownManager  |  Socket管理  
WinCall  |  联网环境下电话呼入呼出  
StartServiceCamera  |  开启摄像头服务  
contacts_delete  |  联系人删除  
Microphone20()  |  麦克风相关  
deleteFiles  |  删除文件  
Terminal  |  远程终端  
SetWallpaper  |  设置手机背景墙  
FileManager2  |  文件管理  
FileDelete  |  文件删除  
Microphone()  |  麦克风相关  
ContactsManager()  |  联系人管理  
properties  |  获取properties文件  
FileMove  |  文件移动  
FileRename  |  文件重命名  
FSettings  |  获取设备相关信息  
_VibratorOff  |  设置相关  
contacts_write  |  添加联系人  
FUN  |  恶搞相关  
FControl  |  控制音量、蓝牙、GPS、WIFI等功能  
AmDPM  |  修改锁屏密码  
FileManager  |  文件管理  
toast  |  弹框  
unzip  |  解压缩  
PlayStart  |  开始播放  
FindCamera()  |  寻找摄像头设备  
SMSManager  |  短信管理  
key_logger  |  键盘记录  
ListenMicrophone  |  麦克风监听  
FileStart  |  弹出文件  
FileWrite  |  文件写入  
ViewFileVideoBreak()  |  视频相关  
StopServiceGLocation()  |  停止定位服务  
KeyStop  |  设置相关  
CallPhone  |  拨打电话  
_Vibrator  |  设置相关  
chatOpen  |  打开聊天框  
chat_set  |  聊天设置  
edithost  |  修改Host  
EditFile  |  修改文件  
SetParameters  |  设置摄像头参数  
StopServiceCamera()  |  停止摄像头服务  
InfDownManager  |  下载者  
  
相关的远控操作：

![](https://image.3001.net/images/20200103/1578032583_5e0eddc7d6b68.png!small)

相关功能代码：

FSettings获取本机设备相关信息，如手机号、SDK_INT、Language、Siminfo、IMSI、IMEI、MAC、SSID、RSSI等相关信息：

![](https://image.3001.net/images/20200103/1578032596_5e0eddd45a2cb.png!small)

获取当前音频模式：

![](https://image.3001.net/images/20200103/1578032608_5e0edde00137d.png!small)

获取手机摄像头相关信息：

![](https://image.3001.net/images/20200103/1578032618_5e0eddea29e48.png!small)

获取通话记录相关信息。姓名、电话号、类型、持续时间：

![](https://image.3001.net/images/20200103/1578032626_5e0eddf249916.png!small)

录音功能：

![](https://image.3001.net/images/20200103/1578032634_5e0eddfa888e2.png!small)

文件管理：

![](https://image.3001.net/images/20200103/1578032644_5e0ede04a2e91.png!small)

音频管理：

![](https://image.3001.net/images/20200103/1578032651_5e0ede0bdad04.png!small)

键盘记录：

![](https://image.3001.net/images/20200103/1578032659_5e0ede1335c54.png!small)

下载者：

![](https://image.3001.net/images/20200103/1578032666_5e0ede1a8a7ee.png!small)

获取联系人信息：

![](https://image.3001.net/images/20200103/1578032674_5e0ede229042e.png!small)

拨号功能：

![](https://image.3001.net/images/20200103/1578032683_5e0ede2b12714.png!small)

添加新联系人：

![](https://image.3001.net/images/20200103/1578032691_5e0ede33d1565.png!small)

##  **总结**

近年来，诸如SpyNote、AhMyth、AndroRAT等安卓远控相继免费甚至公开源代码，黑产向移动端转型的成本大大降低，相比于PC端的远控，安卓远控在地下论坛中售价较为便宜，1500-2500不等，有些中间商甚至使用开源的远控框架不做任何免杀就在地下论坛进行贩卖。

奇安信病毒响应中心提醒用户不要安装未知来源的APP，同时提高个人的安全意识，从而可以防止用户隐私信息被盗取的风险，目前奇安信威胁情报中心文件深度分析平台，奇安信病毒响应中心会移动安全团队会持续对新型远控框架的跟踪，目前奇安信威胁情报中心文件深度分析平台

（<https://sandbox.ti.qianxin.com/sandbox/page>）已支持Android样本分析：

![](https://image.3001.net/images/20200103/1578032720_5e0ede5012c61.png!small)

同时基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC等，都已经支持对该家族的精确检测。

 ***本文作者： 奇安信威胁情报中心，转载请注明来自FreeBuf.COM**  
  
  
  

