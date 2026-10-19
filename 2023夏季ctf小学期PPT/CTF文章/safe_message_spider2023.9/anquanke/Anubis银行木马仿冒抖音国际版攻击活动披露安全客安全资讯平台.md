# Anubis银行木马仿冒抖音国际版攻击活动披露

阅读量 **888040**

发布时间 : 2019-11-05 11:30:56

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t014f5968a3cea0b43d.jpg)

## 概述

Anubis(阿努比斯)是一种主要活动在欧美等地的Android银行木马，其攻击手法主要通过伪装成金融应用、聊天应用、手机游戏、购物应用、软件更新、邮件应用、浏览器应用等一些主流的APP及用户较多的APP进行植入。Anubis自爆发以来，已经席卷全球100多个国家，为300多家金融机构带来了相当大的麻烦。

近期奇安信病毒响应中心，捕获到一款仿冒为抖音国际版“TikTok”的恶意软件，经过分析发现该恶意软件为Anubis木马变种。抖音在国内拥有广大的用户群，甚至可以说异常火爆，对于国内用户来说并不陌生，仅应用宝平台，抖音下载量就达到了5.5亿次，抖音国际版“TikTok”在国外也同样火爆，在国际市场也拥有广大的用户。

应用宝抖音下载量：

![](https://p1.ssl.qhimg.com/t0114b4a66a9b0a6214.png)

Google Play抖音相关软件及下载情况：

![](https://p0.ssl.qhimg.com/t0164affed47e85c54d.png)

此次Anubis通过仿冒国际版抖音“TikTok”传播，就是看到了“TikTok”的用户量。虽然被仿冒的为国际版抖音“TikTok”
，但因为各种原因此应用还会被国内用户尝试安装使用，奇安信病毒响应中心移动安全团队通过数据分析确实发现了基于这个渠道导致Anubis木马感染的部分国内用户。

## 样本分析

Anubis银行木马虽然仿冒的种类繁多，但其核心代码结构并未有较大的改变。Anubis代码核心以远控为主体，钓鱼、勒索等其它功能为辅，目的则为获取用户关键信息，窃取用户财产。

此次发现的仿冒“TikTok”的Anubis木马，其在功能上做了一些改变，并根据实际的需求，增加及优化了一些功能。

![](https://p3.ssl.qhimg.com/t01ca16c7d3aa6af600.png)

仿冒“TikTok”的运行界面：

![](https://p5.ssl.qhimg.com/t01834fc278d06acff9.png)

通过拼接URL下发远控指令：

![](https://p4.ssl.qhimg.com/t013f7a5ca6ad4cfda0.png)

远控指令片段：

![](https://p1.ssl.qhimg.com/t01c88eae1126470755.png)

主要远控指令与指令对应功能：

主要远控指令 | 指令对应的功能  
---|---  
state1letsgotxt | 设置  
ALLSETTINGSGO | 配置相关信息  
Send_GO_SMS | 发送短信  
nymBePsG0 | 获取手机通讯录  
GetSWSGO | 获取手机短信  
|telbookgotext= | 获取手机通讯录  
getapps | 获取已安装APP  
getpermissions | 获取响应的权限  
startaccessibility | 申请可访问性  
startpermission | 启动权限  
=ALERT| | 设置警报  
=PUSH| | 打开钓鱼页面  
startAutoPush | 根据不同国家，弹出不同钓鱼信息  
RequestPermissionInj | 请求注入权限  
RequestPermissionGPS | 获取地理位置  
|ussd= | 向指定号码打电话  
|sockshost= | 连接服务器  
stopsocks5 | Stop socks  
|recordsound= | 录音  
|replaceurl= | 替换URL  
|startapplication= | 启动应用程序  
killBot | 杀死进程  
getkeylogger | 获取键盘记录  
|startrat= | 获取新操作指令  
| opendir: | 列出所有文件  
| downloadfile: | 下载文件  
| deletefilefolder: | 删除文件  
| startscreenVNC | 开启远控  
| stopscreenVNC | 关闭远控  
| startsound | 开始录音  
| startforegroundsound | 开启前景声音  
| stopsound | 关闭录音  
startforward= | 开启呼叫转移  
stopforward | 关闭呼叫转移  
|openbrowser= | 打开浏览器  
|openactivity= | 打开URL  
|cryptokey= | 加密文件  
|decryptokey= | 解密文件  
getIP | 获取用户IP地址  
  
## 影响分析

通过木马下发指令及回传数据的域名：tratata.space，注册于2019年6月26日。基于奇安信威胁情报中心的数据，发现目前受害者大多均来自俄罗斯，国内也有用户中招。

![](https://p3.ssl.qhimg.com/t013d20625a9be84909.png)

## 同源分析

自Anubis爆发以来，我们一直对其进行着监控。我们发现近年来Anubis主要代码结构并没有经过大的改动，但每次新的变种都会在功能上有相应的改动，增加或者优化一些功能。其投递方式及仿冒的类型，一直是优先Google
Play投放，仿冒当下流行的应用及金融应用。

Anubis代码结构演变：

![](https://p4.ssl.qhimg.com/t01aec688581bec2ebe.png)

经过了加固处理的代码结构：

![](https://p2.ssl.qhimg.com/t01855a26931988b407.png)

此次仿冒抖音代码结构：

![](https://p0.ssl.qhimg.com/t011bb5cff30d72beaf.png)

盘古团队的Janus移动安全威胁信息平台中发现如下仿冒的主要图标：

![](https://p4.ssl.qhimg.com/t0147459b40bf6c42b0.png)

## 总结

Anubis银行木马主要市场原本在中国以外，但是随着国内网民对互联网技术的进一步熟悉尝试安装一些国外来源的应用，此次通过仿冒国际版抖音“TikTok”导致了部分国内用户受到了影响。

在此我们提醒广大用户，去正规的平台下载手机应用，将风险降到最低，从而可以防止用户个人信息、财产被盗的风险。奇安信病毒响应中心移动安全团队会保持对Anubis最新变种的跟踪，PC及移动终端安全产品支持对于此类威胁的及时查杀。

## IOC

940F562DED0DD9C48235FB9EA738F405

<http://tratata.space/private/checkPanel.php>

http://tratata.space/private/settings.php

http://tratata.space/private/add_log.php

http://tratata.space/private/set_location.php

http://tratata.space/private/getSettingsAll.php

http://tratata.space/private/setAllSettings.php

http://tratata.space/private/getDataCJ.php

http://tratata.space/private/setDataCJ.php

http://tratata.space/private/add_inj.php

http://tratata.space/private/locker.php

http://tratata.space/private/datakeylogger.php

http://tratata.space/private/sound.php

http://tratata.space/private/playprot.php

<http://tratata.space/private/spam.php>

## 参考

https://ti.qianxin.com/blog/articles/anubis-android-bank-trojan-technical-analysis-and-recent-activities-summary/

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信威胁情报中心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/190274](/post/id/190274)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t01dce0f9e833e11f13.png) 奇安信威胁情报中心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

