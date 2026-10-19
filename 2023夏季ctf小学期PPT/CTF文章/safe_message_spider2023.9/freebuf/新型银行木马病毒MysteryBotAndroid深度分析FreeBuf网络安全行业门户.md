**近日，国外某安全公司发现一种新型银行木马病毒MySteryBot Android，该病毒为银行木马LokiBot Android的变种，
其恶意行为除了利用银行木马窃取金融信息外，还包括恶意监视键盘、植入勒索软件进行勒索操作。经分析发现该木马病毒已适配Android7.0和Android
8.0，一旦被恶意传播，Android7.0和Android 8.0的所有设备均有被感染的可能。鉴于此，通付盾移动安全实验室对MySteryBot
Android病毒进行了深入分析，以下为详细分析内容。**

## 一、样本信息

程序名称 ：MysteryBot

MD5: 9eeeaa4f33ed24b33cd40a21637734bc9b4caeb2

病毒名称：install.apps

应用图标：![微信图片_20180709092249.jpg](https://image.3001.net/images/20180709/153109939613.jpg!small)

恶意行为描述：该程序中包含恶意代码，通过伪装成android
flash，诱导用户下载，从而提高装机量。安装后恶意获取设备管理员权限，用户无法正常卸载，在后台持续运行；私自将用户联系人、短信等隐私信息上传到远程服务端；监听用户键盘，执行勒索操作，具有私自发送短信、拨打电话等恶意扣费行为。

典型样本信息如下：

**SHA256** |  **程序名** **** |  **包名** ****  
---|---|---  
62a09c4994f11ffd61b7be99dd0ff1c64097c4ca5806c5eca73c57cb3a1bc36a | Adobe Flash
Player | install.apps  
334f1efd0b347d54a418d1724d51f8451b7d0bebbd05f648383d05c00726a7ae | Adobe Flash
Player | install.apps  
0963bc9fbb6747e9475c94bb0387b7f4e444ff557dcd0fc81822dce7fab4c3e9 | Adobe Flash
Player | dddddddd.ssssss.hhhhhh.ggggggggg  
  
该木马病毒首先在AndroidManifest.xml文件中病毒申请了一系列与恶意行为密切相关的权限：

![2018-07-06_1.png](https://image.3001.net/images/20180709/15310994709806.png!small)

此外还注册了各种receiver用来监听系统消息：

![2018-07-06_2.png](https://image.3001.net/images/20180709/15310994941528.png!small)

深入分析完成开发的Boot、SmsBroadcast、Scrynlock，其中Boot主要用来在屏幕未唤醒的情况下继续运行，如果CommandService没有启动，则启动CommandService之后屏幕变亮；SmsBroadcast中，当有android.provider.Telephony.SMS_RECEIVED意图时候，最终按照{
"action": "log", "params": {"imei": "%s","type":"sms","text": "%s:
%s"}}的格式将Android设备ID、短信来源、短信内容格式化，
并base64编码，最后组成[http://89.42.211.24/site/gate.php?i=base64字符串](http://89.42.211.24/site/gate.php?i=base64%E5%AD%97%E7%AC%A6%E4%B8%B2)
这样的格式，连接远程服务器，同时唤醒屏幕;Scrynlock实现了一个Admin的设备管理，同时会用webview加载这个
[http://89.42.211.24/site/inj/test/?p=imei](http://89.42.211.24/site/inj/test/?p=imei,)，并向/storage/sdcard0/sslocks.txt文件中写入+1，其次该病毒还对Home健监听和通过对手势进行判断执行触屏按键监听，该组件目前处于正在开发阶段，暂未工作。

其中SmsBroadcast的关键代码如下：

![2018-07-06_3.png](https://image.3001.net/images/20180709/15310995084070.png!small)三、恶意行为分析

该木马的核心类是CommandService.class、install.apps.c.class、install.apps.Cripts$mainActivity、install.apps.g.class,通过对这四个核心类分析后，获得该木马的核心恶意行为。该木马的整体恶意流程如下图所示：

![微信截图_20180709092621.png](https://image.3001.net/images/20180709/15310996148758.png!small)

Step1 : 成为Admin的设备管理者和完成自我隐藏

![2018-07-06_5.png](https://image.3001.net/images/20180709/15310996523899.png!small)

Step2：后台运行的CommandService,上传数据和设置Boot.class用来监督CommandService是否成功运行，没有则再次启动。

![2018-07-06_6.png](https://image.3001.net/images/20180709/15310996729249.png!small)

设置定时器为5s，然后重复执行这些恶意代码

![2018-07-06_7.png](https://image.3001.net/images/20180709/15310997273747.png!small)

判断/mnt/sdcard/是否存在sslocks.txt

![2018-07-06_8.png](https://image.3001.net/images/20180709/15310997804855.png!small)

判断/mnt/sdcard/是否存在dblocks.txt

![2018-07-06_9.png](https://image.3001.net/images/20180709/15310997955816.png!small)

Step3：install.apps.Cripts$mainActivity，主要是勒索部分，暂时还没有明确的勒索付费方式。

将联系人和文件压缩在zip包中，并没有将其加密。

![2018-07-06_10.png](https://image.3001.net/images/20180709/15310998634257.png!small)

其次是上传隐私信息到服务器

![2018-07-06_11.png](https://image.3001.net/images/20180709/15310998842829.png!small)

勒索的HTML页面信息

![2018-07-06_12.png](https://image.3001.net/images/20180709/15310999078301.png!small)

按键手势和Home键监听广播

![2018-07-06_13.png](https://image.3001.net/images/20180709/15310999392272.png!small)

Step4：install.app.g主要用来上传用户隐私信息与远控端通信

![2018-07-06_14.png](https://image.3001.net/images/20180709/1531099985289.png!small)

与远控端通信，远控端发出action指令后，该木马进行执行，主要是上传用户联系人、发短信、打电话、上传键盘日志等隐私信息。

![2018-07-06_15.png](https://image.3001.net/images/20180709/15311000222734.png!small)四、
影响范围

通信的IP地址可以看出来，该木马面向的银行主要是中东和欧洲银行。目前国内相关机构，暂未发现该木马的行踪，我们会持续追踪其动态。木马运行如下：

![78DD186DFB6AC49B91B4B16C2F5C1C3F.gif](https://image.3001.net/images/20180709/15311000527673.gif!small)

## 分析总结

该木马建立起了一套完整的远程控制体系，涵盖了各种远程控制恶意行为，包括对各种设备硬件信息采集、短信监控，以及键盘监听等等，极大程度上侵犯了用户的个人隐私信息安全，具有非常强的危害性。

通付盾移动安全实验室已实现对该类病毒的检测查杀，同时相关移动应用检测类产品也已具备对该类恶意应用的检出能力。

 **通付盾移动安全实验室目前已实现对该类病毒的检测查杀，同时相关移动应用检测类产品也已具备对该类恶意应用的检出能力。**  

 ***文章作者 **通付盾移动安全实验室，转载请注明来自Freebuf.COM****

