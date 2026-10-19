#
![图片.png](https://image.3001.net/images/20200313/1584064356_5e6ae764266f1.png!small)  

## 背景介绍

近期奇安信病毒响应中心在日常监测中，发现大量Cerberus银行木马，其通过仿冒一些流量较大的APP，甚至通过仿冒“新型冠状病毒”进行传播。

Cerberus银行木马最早出现在2019年6月，当时研究人员将该木马作为Anubis的变体进行分析命名。然而其作者在Twitter上发文并建议安全厂商将其命名为：Trojan-Android:Banker-Cerberus，至此Cerberus（地狱犬）正式出现在大众的视野中。

![图片.png](https://image.3001.net/images/20200313/1584064370_5e6ae77233bfb.png!small)

Cerberus作者声称其过去两年一直处于私人运营，目前正在寻找合作伙伴中，且正式在地下论坛开始进行租赁。Cerberus具有专门的销售渠道，而且目前客户广泛，其木马经过不断更新后，目前已可以适配大多数国家。Cerberus作者也声称其代码不是继承自Anubis或其它银行木马，而是重新编写的。

![图片.png](https://image.3001.net/images/20200313/1584064379_5e6ae77b409b5.png!small)

在进入2020年以后，Cerberus变得更为活跃，在经过功能更新后该木马可以盗用Google
Authenticator应用创建的2-FactorAuthentication（2FA）代码，从而绕过身份验证服务，并且能够启动TeamViewer实行远控。

而且借着“新型冠状病毒”在全球的爆发之际，其也利用“新型冠状病毒”作为诱饵进行传播，成为第一个借“新型冠状病毒”传播的移动木马。

仿冒“新型冠状病毒”样本信息：

![图片.png](https://image.3001.net/images/20200313/1584064384_5e6ae780d0bfb.png!small)

**应用名** |  **Coronavirus**  
---|---  
**包名** |  hdjro.nzaqrgffealnhmorwihd.mfukiybfx  
**MD5** |  B8328A55E1C340C1B4C7CA622AD79649  
**图标** |
![图片.png](https://image.3001.net/images/20200313/1584064390_5e6ae78687a8f.png!small)  
  
## Cerberus木马分析

Cerberus木马与其它银行木马一样功能众多，而且由于其一直在地下论坛中进行租赁，可以根据“客户”的不同需求进行功能的增加等，加上其作者的高调做派，俨然已经接过了Anubis的邪恶传承，成为了目前威胁最大的银行木马。

 **Cerberus** **木马接棒Anubis：**

图片来自ThreatFabric

Cerberus木马运行以后会诱骗用户激活设备管理器、隐藏自身图标、防止卸载等方式进行自我保护。Cerberus木马会获取并上传用户手机中短信、通讯录、手机已安装的应用信息、gmail信息等。此外Cerberus木马还可以截取用户手机屏幕，电话呼叫转移，获取用户银行账号、密码等恶意操作，并可以通过Team
Viewe进行远控。

相比于2019年6月发现的Cerberus初代木马，目前Cerberus木马已增加了更多的恶意功能，根据其在论坛的实时更新，我们发现其已可以仿冒TeamViewe，目前并没有看到作者发布新的版本，应该还在测试阶段。

 **仿冒Team Viewe界面：**

![图片.png](https://image.3001.net/images/20200313/1584064415_5e6ae79f7cfdb.png!small)

 **Cerberus** **木马早期远控功能列表：**

**远控指令** |  **指令含义**  
---|---  
**push** |  **显示推送通知。单击通知将导致启动指定的应用程序**  
**startApp** |  **启动指定的应用程序**  
**getInstallApps** |  **获取受感染设备上已安装应用程序的列表**  
**getContacts** |  **获取受感染设备上的通讯录**  
**deleteApplication** |  **删除指定应用程序**  
**forwardCall** |  **来电呼叫转移**  
**sendSms** |  **发送短信**  
**startInject** |  **针对指定程序进行攻击**  
**startUssd** |  **调用指定的USSD代码**  
**openUrl** |  **在WebView中打开指定的URL**  
**getSMS** |  **获取受感染设备上的短信**  
**killMe** |  **删除机器人**  
**updateModule** |  **更新模块**  
  
**Cerberus** **木马最新远控功能列表：**

**远控指令** |  **指令含义**  
---|---  
**grabbing_lockpattern** |  **对用户解锁密码时进行截屏**  
**request_permission** |  **请求敏感权限**  
**run_admin_device** |  **运行设备管理器**  
**URL** |  **在WebView中打开指定的URL**  
**ussd** |  **调用指定的USSD代码**  
**get_data_logs** |  **获取受感染设备上已安装应用程序信息、通讯录、短信**  
**grabbing_google_authenticator2** |  **截取google二次验证输入的信息**  
**notification** |  **设置消息通知图标、标题、内容、样式并发送。**  
**grabbing_pass_gmail** |  **获取受感染设备上的gmail信息**  
**remove_app** |  **防止卸载应用**  
**remove_bot** |  **删除机器人**  
**send_sms** |  **发送短信**  
**run_app** |  **运行更新的应用**  
**call_forward** |  **来电呼叫转移**  
**patch_update** |  **更新补丁**  
**run_injects_emails** |  **获取注入的电子邮件页面的账号密码信息**  
**run_injects_banks** |  **获取注入的银行页面的账号密码信息**  
  
Cerberus木马经过了这段时间的发展，对木马的保护也在不断的完善，我们在分析最新的样本时发现，Cerberus木马使用了大量的代码混淆、字符串加密、动态加载等方式。如果随着Cerberus的“客户”的增加，相信安全分析人员与Cerberus的对抗在将来是一个更为持久的过程。

大量无用的代码：

![图片.png](https://image.3001.net/images/20200313/1584064425_5e6ae7a9f297a.png!small)

经过字符串加密的代码：

![图片.png](https://image.3001.net/images/20200313/1584064431_5e6ae7af58d2d.png!small)

加载恶意代码：

![图片.png](https://image.3001.net/images/20200313/1584064436_5e6ae7b41c63f.png!small)

连接Team Viewe：

_![图片.png](https://image.3001.net/images/20200313/1584064440_5e6ae7b8ed58c.png!small)_

## Cerberus木马数据总结

通过Janus平台监测到的Cerberus木马：

![图片.png](https://image.3001.net/images/20200313/1584064446_5e6ae7be025ec.png!small)

![图片.png](https://image.3001.net/images/20200313/1584064449_5e6ae7c167982.png!small)

近期Cerberus木马针对性较强的仿冒应用信息。

Cerberus仿冒whatsapp:

**应用名** |  **whatsapp**  
---|---  
**包名** |  xpmwjinzd.qzcwcqqkimadlxdk.hsomeub  
**MD5** |  d2f9c7e9319cd3425f53319bf1e4f7e2  
**图标** |
![图片.png](https://image.3001.net/images/20200313/1584064454_5e6ae7c69e980.png!small)  
  
![图片.png](https://image.3001.net/images/20200313/1584064461_5e6ae7cd4725a.png!small)

Cerberus伪装为西班牙税务局AEAT：

**应用名** |  **AEAT**  
---|---  
**包名** |  jtizpsfwsbfcedbb.xjlej.ssblmgielhtp  
**MD5** |  F438F12BAE6132C3997D4CF6153D36CA  
**图标** |
![图片.png](https://image.3001.net/images/20200313/1584064471_5e6ae7d75e507.png!small)  
  
![图片.png](https://image.3001.net/images/20200313/1584064476_5e6ae7dc81fd3.png!small)

近期Cerberus仿冒较多的应用图标：

![图片.png](https://image.3001.net/images/20200313/1584064483_5e6ae7e31b5eb.png!small)

## 总结

目前暂时没有发现Cerberus仿冒国内应用，但随着Cerberus木马的不断更新，“潜在客户”的不断增加，Cerberus将目标瞄准到国内也是可能发生的。奇安信病毒响应中心会随时关注Cerberus木马的实时动态，同时奇安信病毒响应中心提醒用户不要安装未知来源的APP，同时提高个人的安全意识。

目前奇安信威胁情报中心文件深度分析平台：（[https://sandbox.ti.qianxin.com/sandbox/page](https://sandbox.ti.qianxin.com/sandbox/page)）已支持Android样本分析：

![图片.png](https://image.3001.net/images/20200313/1584064491_5e6ae7eb3cacf.png!small)

同时基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC等，都已经支持对此类攻击的精确检测。

## IOC

文件MD5：

B8328A55E1C340C1B4C7CA622AD79649

d2f9c7e9319cd3425f53319bf1e4f7e2

F438F12BAE6132C3997D4CF6153D36CA

8ff2ac17c07768c5079e646dd9f1e550

12a57ba309cc0e9421d36abbf78d51e6

79157c3e0a3aeab23d190d4b2ebe045b

C2：

bilbaobbva.com

vergaespanola.site

postarmailsrv.xyz

<http://kryll.ug>

<http://aeat-tgss.com/aeat.apk>

