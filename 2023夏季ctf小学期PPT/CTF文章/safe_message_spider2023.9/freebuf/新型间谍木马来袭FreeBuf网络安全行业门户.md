**背景：近些年，地下黑产组织针对全世界各国大型银行进行持续性的APT攻击，尤其是针对韩国、西班牙、葡萄牙等大型银行，采用仿冒、间谍软件、钓鱼劫持、勒索等技术手段，窃取用户个人信息，非法入侵用户的互联网账户系统。**

近期，恒安嘉新暗影安全实验室在日常监测中，发现一批针对韩国银行用户的新型间谍软件。这批木马样本仿冒成“智能快递”、“罗森快递”、“CJ韩国快递”、“现代快递”、“交货查询”、“韩进快递”、“SJEMS”等12种知名快递公司名称，采用加固代码隐藏，免杀，任意更换远程控制地址、任意替换新型木马等手段，配置非常灵活，根据C&C端下发的指令进行远程控制，窃取用户手机号码、通信录、通话录音、短信等个人隐私信息，最终盗取用户互联网账户的资金，其中，“智能快递”间谍木马的安装图标如图1所示。

![](https://image.3001.net/images/20200429/1588134733_5ea9034d734fd.png!small)

图1 “스마트택배”（智能快递）图标

##  **一、基本信息**

> **样本名称** ：스마트택배（智能快递）
>
> **样本MD5** ：d891a72721a8f2b31c5e0759afb0d4a9
>
> **样本包名** :com.mix.kr
>
> **签名信息** ：CN=AndroidDebug,O=Android,C=US

##  **二、运行原理**

该程序是一款通过仿冒成“스마트택배”（智能快递）名称的间谍木马软件，开机时自启动，隐藏安装图标，激活设备管理器，屏蔽拦截短信、屏蔽挂断指定电话、上传通话录音文件、删除通话记录，上传用户手机号和固件信息到指定服务器，根据C&C服务端下发的指令执行远程控制行为：

> 设置配置文件信息
>
> 上传通信录列表
>
> 上传应用列表
>
> 上传短信列表
>
> 发送任意短信
>
> 更新间谍软件程序
>
> 更新服务器地址

**木马运行流程示意图：**

![](https://image.3001.net/images/20200429/1588134788_5ea9038437f4d.png!small)

图2 木马运行流程示意图

##  **三、代码分析**

新型间谍木马采用伪加固将其核心代码隐藏，避开杀软检测，同时，通过C&C服务端任意更新间谍木马变种版本，任意更新服务器地址，主要分为基础功能和远控功能两大部分，所谓基础功能就是样本自身所具有的恶意行为，远控功能就是与C&C服务端交互的恶意行为。

![](https://image.3001.net/images/20200429/1588134804_5ea903940be01.png!small)

图3 代码框架

通过C&C服务端任意更新间谍木马变种版本，任意更新服务器地址后续说明。

（1） **基础功能**

开机时自启动，隐藏安装图标，激活设备管理器，屏蔽拦截短信、屏蔽挂断指定电话、上传通话录音文件、删除通话记录。

隐藏安装图标:

![](https://image.3001.net/images/20200429/1588134816_5ea903a06d7b1.png!small)

图4 隐藏安装图标

激活设备管理器:

![](https://image.3001.net/images/20200429/1588134842_5ea903bac661d.png!small)

图5 激活设备管理器

屏蔽拦截短信：

![](https://image.3001.net/images/20200429/1588134858_5ea903cabb8fb.png!small)

图6 屏蔽拦截短信

屏蔽挂断指定电话：

![](https://image.3001.net/images/20200429/1588134882_5ea903e231545.png!small)

图7 屏蔽挂断指定电话

删除通话记录：

![](https://image.3001.net/images/20200429/1588134907_5ea903fb8a32a.png!small)![](https://image.3001.net/images/20200429/1588134906_5ea903fa8689e.png!small)

图8 删除指定通话记录

后台开启服务将通话录音发送到指定邮箱：

![](https://image.3001.net/images/20200429/1588134949_5ea904255f166.png!small)![](https://image.3001.net/images/20200429/1588134965_5ea90435ee7ad.png!small)

图9 将通话录音发送到指定邮箱

**(2) **远控功能****

上传手机号、固件信息，并请求远控指令，根据C&C服务端下发的指令执行远程控制行为。

上传手机号、固件信息，并请求远控指令:

![](https://image.3001.net/images/20200429/1588134983_5ea90447b3a96.png!small)

图10 获取手机号

![](https://image.3001.net/images/20200429/1588135052_5ea9048c3ff00.png!small)

图11 请求远控指令

根据C&C服务端下发的指令执行远程控制行为：

C&C服务端  |  指令  |  指令详解  
---|---|---  
[http://113.](http://0.0.0.113/)***.137.171 /kbs.php  |  sendsms  |  发送任意短信  
issms  |  设置短信相关配置文件  |  
iscall  |  设置电话相关配置文件  |  
contact  |  上传通讯录联系人  |  
apps  |  上传应用程序列表  |  
changeapp  |  更新木马  |  
move  |  更新服务器地址  |  
  
接收到指令“sendsms”，发送任意短信：

![](https://image.3001.net/images/20200429/1588135067_5ea9049b75ad2.png!small)

图12 发送短信并反馈

接收到指令“issms/iscall”，设置短信/电话相关的配置参数：

![](https://image.3001.net/images/20200429/1588135098_5ea904ba69332.png!small)

图13 设置短信/电话相关的配置参数

接收到指令“contact”，上传通讯录联系人：

![](https://image.3001.net/images/20200429/1588135112_5ea904c84bfeb.png!small)

图14 上传通讯录联系人

接收到指令“apps”，上传应用程序列表：

![](https://image.3001.net/images/20200429/1588135136_5ea904e08fe82.png!small)![](https://image.3001.net/images/20200429/1588135147_5ea904eb4059e.png!small)

图15 上传应用程序列表

接收到指令“changeapp”，卸载并更新木马版本（指定的仿冒银行木马）：

![](https://image.3001.net/images/20200429/1588135173_5ea905053285d.png!small)

图16 卸载并更新木马版本

涉及韩国的NH智能银行、新韩银行、韩亚银行、友利银行、KB国民银行等5家银行，针对性非常强。

![](https://image.3001.net/images/20200429/1588135186_5ea90512deb7e.png!small)

图17 目标银行列表

接收到指令“move”，更新C&C服务器地址：

![](https://image.3001.net/images/20200429/1588135204_5ea9052403074.png!small)

图18 更新C&C服务器地址

##  **四、溯源分析**

从上文技术分析我们得到了C&C服务器地址，远控邮箱账户。

**（1）溯源** **IP** **地址**

从这批木马C&C服务器所在位置的角度，我们发现8个不同IP地址(IP地址去重)，其中，中国香港占4个，日本占3个，美国占1个。

样本MD5  |  服务器地址  |  IP地理位置  
---|---|---  
DD0ACE0363BA60A96753ED21D4DDEB07  |
[http://103.](http://0.0.0.103/)***.237.30/kbs.php  |  中国香港  
C72F2B6DC3D8F3BBF506E7CB7F35B79F  |
[http://113.](http://0.0.0.113/)***.136.143/kbs.php  |  中国香港  
F36AA75CFE9EEC1D8E755C34AC50A**5  |
[http://113.](http://0.0.0.113/)***.137.171/kbs.php  |  中国香港  
3C326883FEB95ABB049A010EFD738A83  |
[http://113.](http://0.0.0.113/)***.137.236/kbs.php  |  中国香港  
3DA715A5191065D596AEE0AEDF27C7EB  |
[http://60.](http://0.0.0.60/)***.97.36/kbs.php  |  日本东京都  
5A678A32CA866F13FF99A0ECB1FB**57  |
[http://122.](http://0.0.0.122/)***.100.128/kbs.php  |  日本兵库县  
97966D65B2976B06CCE09E6**299A713  |
[http://126.](http://0.0.0.126/)***.162.113/kbs.php  |  日本东京都  
DDCB9D034A01B014173BA80DC1ACB5BD  |
[http://45.](http://0.0.0.45/)***.80.109/kbs.php  |  美国加利福尼亚州洛杉矶  
  
其中，103.251.237.30地址反查，我们发现其曾经绑定过的58个域名（二级域名去重），经常用于僵尸网络和垃圾邮件。

IP地址曾经绑定过的部分域名列表如下：

序号  |  域名  |  
---|---|---  
1  |  [111xxx.cn](https://x.threatbook.cn/nodev4/domain/111xxx.cn) |
[www.111xxx.cn](https://x.threatbook.cn/nodev4/domain/www.111xxx.cn)  
2  |  [ahzxxx.cn](https://x.threatbook.cn/nodev4/domain/ahzxxx.cn) |
[www.ahzxxx.cn](https://x.threatbook.cn/nodev4/domain/www.ahzxxx.cn)  
3  |  [aitan***zers.cn](https://x.threatbook.cn/nodev4/domain/aitanalyzers.cn)
|
[mail.aita***zers.cn](https://x.threatbook.cn/nodev4/domain/mail.aitanalyzers.cn)  
4  |
[www.ait***yzers.cn](https://x.threatbook.cn/nodev4/domain/www.aitanalyzers.cn)
|  [ch***ol.cn](https://x.threatbook.cn/nodev4/domain/chemcol.cn)  
5  |  [www.ch***col.cn](https://x.threatbook.cn/nodev4/domain/www.chemcol.cn)
|
[aitana***ers.com.cn](https://x.threatbook.cn/nodev4/domain/aitanalyzers.com.cn)  
6  |
[www.aitan***ers.com.cn](https://x.threatbook.cn/nodev4/domain/www.aitanalyzers.com.cn)
|
[www.anv***larm.com.cn](https://x.threatbook.cn/nodev4/domain/www.anvoxalarm.com.cn)  
7  |  [bj***f.com.cn](https://x.threatbook.cn/nodev4/domain/bjcgf.com.cn) |
[www.b***f.com.cn](https://x.threatbook.cn/nodev4/domain/www.bjcgf.com.cn)  
8  |  [delta-tec***ik.com.cn](https://x.threatbook.cn/nodev4/domain/delta-technik.com.cn) |  [www.delta-te***ik.com.cn](https://x.threatbook.cn/nodev4/domain/www.delta-technik.com.cn)  
9  |  [j***x.com.cn](https://x.threatbook.cn/nodev4/domain/jdx.com.cn) |
[www.j***x.com.cn](https://x.threatbook.cn/nodev4/domain/www.jdx.com.cn)  
10  |
[www.t***ts.com.cn](https://x.threatbook.cn/nodev4/domain/www.tdts.com.cn) |
[won***odels.com.cn](https://x.threatbook.cn/nodev4/domain/wondermodels.com.cn)  
  
**（2）溯源邮箱**

从接收/发送邮件账户的角度，发送邮件和接收邮件的邮箱账户是同一个：qq18***65379@163.com，密码是rk***014。

邮箱中还包含大量PC端木马程序，DNS配置SP，DNS批量域名生成器，跳转劫持代码等，说明该邮箱常用来接收其他木马文件：

![](https://image.3001.net/images/20200429/1588135272_5ea9056807927.png!small)![](https://image.3001.net/images/20200429/1588135282_5ea9057281cf3.png!small)

图19 邮箱内有大量恶意软件

**（3）样本扩展**

在恒安嘉新
App全景态势与案件情报溯源挖掘平台上，通过应用名称、包名等特征关联搜索相关样本，发现平台上存在大量新型间谍木马类恶意应用，其中，该类恶意程序代码结构、包名及其类似，极有可能是同一批人开发。

![](https://image.3001.net/images/20200429/1588135296_5ea90580abb53.png!small)![](https://image.3001.net/images/20200429/1588135315_5ea90593b1824.png!small)

##  **五、总结**

新型间谍木马具有代码结构相似，变种快的特点，窃取用户手机号码、通信录、通话录音、短信等个人隐私信息，最终盗取用户互联网账户的资金，危害极大，同时可能是某地下灰黑产组织针对韩国银行持续性攻击，不轻易相信陌生人，不轻易点击陌生人发送的链接，不轻易下载不安全应用。

> （1）安全从自身做起，建议用户在下载软件时，到针对的应用商店进行下载正版软件，避免从论坛等下载软件，可以有效的减少该类病毒的侵害；
>
>
> （2）很多用户受骗正是因为钓鱼短信的发件人显示为10086、95588等正常号码而放松安全警惕导致中招，运营商需要加强对***的监控打击力度，减少遭受***干扰的几率；
>
> （3）各大银行、各支付平台需要加强对各自支付转账渠道的监管，完善对用户资金转移等敏感操作的风控机制，防止被不法分子利用窃取用户网银财产;
>
> （4）警惕各种借贷软件的套路，不要轻易使用借贷类App。

 ***本文作者：暗影安全实验室，转载请注明来自FreeBuf.COM**

