**研究人员近期发现Android恶意软件“TrickMo”，该程序可通过TrickBot木马感染用户。攻击者利用该恶意app可绕过2FA认证并授权交易，TrickMo正在频繁升级更新，虽然它可以针对任何银行或地区，但目前只在德国出现。**

##  首次发现

2019年9月网络犯罪团伙利用银行木马TrickBot进行攻击，攻击者在网上银行web界面注入恶意代码，获取用户手机号码和设备类型。

![](https://image.3001.net/images/20200331/1585637840_5e82e9d075a5a.png!small)

当银行木请求此类信息时，通常意味着攻击者将试图感染受害者的移动设备。

##  桌面木马及其移动组件

木马对移动设备的攻击活动已有十年的历史。当用户台式机上感染了TrickBot时，用户访问的网页会被注入恶意代码并收集移动设备系统类型和电话号码。木马通过伪造银行网站欺骗受害者安装假冒程序，获取“安全代码”登录其在线银行。

TrickMo目前针对德国用户，其目的是窃取交易身份验证号码（TAN），主要功能包括：

> 窃取个人设备信息
>
> 拦截短信
>
> 记录目标应用程序的密码（TAN）
>
> 手机锁定
>
> 获取设备图片
>
> 自毁和清除

##  软件发展

随着银行安全措施增强，银行恶意软件也在不断发展。十年前银行木马可以使用凭据访问受害者在线银行帐户并进行汇款。之后金融机构引入了第二因素认证（2FA）方法，向客户端移动设备发送一次性密码消息，客户在浏览器中输入后才能授权交易。2011年左右，Zeus
Trojan开始使用web注入诱使用户下载“ZitMo”移动组件，拦截银行SMS消息并窃取密码绕过2FA。同一时期，其他银行恶意软件家族也纷纷效仿。

在过去的几年中，欧洲的一些银行，尤其是德国的银行，停止使用基于SMS的身份验证，使用2FA方案pushTAN程序。这些应用程序不再依赖于可以被第三方拦截的SMS消息，而是使用用户推送通知，其中包含交易明细和TAN。
pushTAN方法可降低SIM交换攻击和SMS窃取风险。为了应对这一变化，TrickMo添加了屏幕视频录制和屏幕数据抓取功能来窃取TAN。

##  技术分析

Android辅助功能服务最初目的是面向残障用户，任何应用程序都可以请求其权限，例如屏幕阅读，更改对象的大小和颜色，增强听觉能力，用其他形式的控件代替触摸等等。TrickMo安装在设备上后会授权攻击者执行操作，其中包括：

> 防止用户卸载应用程序
>
> 更改设备设置成为默认的SMS应用程序
>
> 监视当前正在运行的应用程序
>
> 获取屏幕文字

Android操作系统包含许多对话框屏幕，必须点击屏幕按钮拒绝或批准权限操作，TrickMo可识别和控制屏幕，在用户做出反应之前做出自己的选择。恶意软件会检测特定对话框并根据预定义选项选择，如下图所示：

![](https://image.3001.net/images/20200331/1585639547_5e82f07b1f1b4.png!small)TrickMo注册侦听“
android.intent.action.SCREEN_ON”和“
android.provider.Telephony.SMS_DELIVER”广播接收器，TrickMo可在设备互动后或收到新SMS消息后启动。

![](https://image.3001.net/images/20200331/1585639637_5e82f0d557743.png!small)

TrickMo使用共享机制存储数据，可以从C＆C服务器或SMS消息获取命令执行任务。

为了增强其安全性增加分析难度，TrickMo使用混淆器来加密函数，类和变量名称。
2020年1月发布的TrickMo可检测自身是否处于模拟环境以防止被分析。下图可以看到加密和解密文件，该文件使用Java“PBEWithMD5AndDES”算法加密。

##
![](https://image.3001.net/images/20200331/1585639912_5e82f1e8dcc1f.png!small)网络通信

TrickMo代码包含C＆C服务器URL，通过未加密的HTTP定期连接服务器，通过JSON数据格式发送受害者手机数据：

> ID
>
> IMSI
>
> IMEI
>
> Phone number
>
> Operator
>
> AID
>
> Model
>
> Brand
>
> Version
>
> Build
>
> Battery
>
> Wi-Fi state
>
> Wake time
>
> Screen size
>
> Installed applications
>
> SMS messages

某些银行仍在使用SMS授权交易，TrickMo可以自动窃取设备上存储的所有SMS消息，向C＆C服务器发送设备数据以及所有保存的SMS消息，也可以删除SMS消息。下图可以看到发送到攻击者C＆C服务器的数据包，其中包含收集的信息以及SMS数据。

![](https://image.3001.net/images/20200331/1585640300_5e82f36c49e06.png!small)

TrickMo可自动将SMS发送到C＆C服务器，同时也发送操作日志数据。下图是TrickMo成为默认SMS应用程序后发送给攻击者的日志。
如果该恶意软件成为默认的SMS应用程序，它将以俄语发送成功结果。

![](https://image.3001.net/images/20200331/1585640518_5e82f446df72a.png!small)TrickMo可通过两种方式进行控制：

> 1、利用C&C服务器发送HTTP数据
>
> 2、利用加密SMS消息

控制命令包括：

**sms控制**

> 1、更新C&C服务器地址，SMS消息以“http://”开头
>
> 2、发送加密消息，SMS以“sms://”开头
>
> 3、更新唤醒服务——“2”
>
> 4、停止活动——“4”

**C &C控制**

> 1、更新C＆C服务器地址——“1”
>
> 2、更新唤醒服务——“2”
>
> 3、锁定屏幕——“5”
>
> 4、显示图片——“11”
>
> 5、发送短信——“8”
>
> 6、窃取图像——“12”和“13”
>
> 7、成为默认的短信应用——“6”
>
> 8、启用录制——“15”
>
> 9、停止活动——“4”

TrickMo可在目标应用程序运行时记录屏幕，程序记录通过两种方法实现：

1、应用程序运行时，使用Android MediaRecorder录制屏幕视频

2、记录屏幕上所有对象的数据

所有数据发送到攻击者C＆C服务器，下图可以看到恶意软件如何从C＆C服务器接收JSON数据，其中包含开始录制命令，目标应用程序和录制的视频比率。

![](https://image.3001.net/images/20200331/1585641148_5e82f6bcd9805.png!small)![](https://image.3001.net/images/20200331/1585641158_5e82f6c6403aa.png!small)![](https://image.3001.net/images/20200331/1585641172_5e82f6d41c27f.png!small)

TrickMo恶意软拥有自己的kill开关。下图可以看到来自C＆C服务器的命令，如果返回的JSON数据为“4”，它将打开kill开关并启动自删除。

##
![](https://image.3001.net/images/20200331/1585641454_5e82f7ee7081c.png!small)![](https://image.3001.net/images/20200331/1585641464_5e82f7f872397.png!small)IoCs

###  url

> hxxp://mcsoft365.com/c
>
> hxxp://pingconnect.net/c

###  Hashes

> MD5: 5c749c9fce8c41bf6bcc9bd8a691621b
>
> SHA256: 284bd2d16092b4d13b6bc85d87950eb4c5e8cbba9af2a04d76d88da2f26c485c
>
> MD5: b264af5d2f3390e465052a***2b0726d
>
> SHA256: 8ab1712ce9ca2d7952ab763d8a4872aa6a278c3f60dc13e0aebe59f50e

***参考来源：[securityintelligence](https://securityintelligence.com/posts/trickbot-pushing-a-2fa-bypass-app-to-bank-customers-in-germany/)，由Kriston编译，转载请注明来自FreeBuf.COM**

  

