**前段时间网上流传 Android 平台 Cerberus 木马家族出现了新的变种，在网上找了一番没有找到新变种的木马样本反而找到了 2019 年 6
月披露的一批样本，这里挑选了其中一个样本深入的分析下看看 Cerberus 木马的工作机制。**

> Cerberus
> 木马的详细介绍可以阅读之前发的文章：<https://mp.weixin.qq.com/s/UewBO4RgTlh9vBKzqYXEcQ>

##  恶意样本特征

> 样本名称：Flash Player
>
> 应用包名：com.uxlgtsvfdc.zipvwntdy
>
> SHA-256：728a6ea44aab94a2d0ebbccbf0c1b4a93fbd9efa8813c19a88d368d6a46b4f4f

##  流程概览

恶意样本的执行流程大概如下：

![](https://image.3001.net/images/20200317/1584413859_5e703ca33ad18.png!small)

##  内存解密新 dex

Android 应用程序必须在 AndroidManifest.xml 文件中声明其使用的服务、广播接收器和活动组件才能使用它们。在反编译 Cerberus
恶意样本中很明显能看到其使用的服务、广播接收器和活动等组件并不在主 dex 文件中，所以这里基本可以判断其核心 dex 文件是在内存中动态解密的。

![](https://image.3001.net/images/20200317/1584414191_5e703deff0145.png!small)

通过在内存搜索匹配 dex 文件特征并转储内存中解密后的 dex 获取木马的核心代码。

![](https://image.3001.net/images/20200317/1584414223_5e703e0f47c39.png!small)

##  地区白名单

恶意样本在解密释放新的 dex 文件后判断当前感染者所在国是否在白名单中，如果在白名单中则不执行恶意行为。

白名单国家名单有：乌克兰、俄罗斯、白俄罗斯、塔吉克斯坦、乌兹别克斯坦、土库曼斯坦、阿塞拜疆、亚美尼亚、哈萨克斯坦、吉尔吉斯斯坦、摩尔多瓦等。

![](https://image.3001.net/images/20200317/1584414338_5e703e8231634.png!small)![](https://image.3001.net/images/20200317/1584414365_5e703e9d0eef6.png!small)![](https://image.3001.net/images/20200317/1584414374_5e703ea6a59fb.png!small)

##  隐藏图标

如果感染者不在白名单国家则恶意软件将进一步执行，其通过禁用入口组件来实现隐藏图标使其在手机桌面上不可见来规避感染者卸载恶意应用。

![](https://image.3001.net/images/20200317/1584414416_5e703ed00e360.png!small)

##  定时触发保活广播

恶意软件通过在清单文件中注册高频的系统广播事件以及定时让系统时钟发送自身广播事件实现了一个简单的保活机制使其能持续的活动在系统中。

![](https://image.3001.net/images/20200317/1584414583_5e703f7733f16.png!small)![](https://image.3001.net/images/20200317/1584414645_5e703fb566637.png!small)![](https://image.3001.net/images/20200317/1584414687_5e703fdf14ec1.png!small)![](https://image.3001.net/images/20200317/1584414702_5e703feebe35c.png!small)

###  计步机制触发与 C2 服务器通信

在保活广播接收器组件中，实现了一个简单的计步器来触发木马与 C2 服务器的通信。

![](https://image.3001.net/images/20200317/1584414793_5e704049b0676.png!small)![](https://image.3001.net/images/20200317/1584414837_5e70407552e39.png!small)

###  更新攻击命令

计步数量达到阀值后，启动 HBOxMrf 木马服务拉取 C2 服务器的攻击命令，C&C
服务器地址为：<http://94.156.77.32/gate.php> **目前服务已经无法正常访问** 。

客户端与 C2 服务器交互流程如下：

1、首先拉取 C2 服务器下发的攻击命令。

![](https://image.3001.net/images/20200317/1584417715_5e704bb3881b7.png!small)

2、如果响应命令为 ||no|| 则注册到 C2 服务器成为肉鸡设备

![](https://image.3001.net/images/20200317/1584418370_5e704e42dfbe0.png!small)

3、如果命令包含 ||youNeedMoreResources|| 则下载 payload 并保存到 data/data/包名/apk/system.apk
文件中。

![](https://image.3001.net/images/20200317/1584418394_5e704e5a79465.png!small)

![](https://image.3001.net/images/20200317/1584418414_5e704e6e72a47.png!small)

4、更新攻击命令到 payload 等待完成攻击。

![](https://image.3001.net/images/20200317/1584418461_5e704e9d0802e.png!small)

![](https://image.3001.net/images/20200317/1584418479_5e704eaf774a3.png!small)

###  忽略电池优化

Cerberus 木马除了定时触发保活广播，还通过将自己加入电池优化白名单中来增强持续在系统中执行恶意活动的可能。

![](https://image.3001.net/images/20200317/1584418518_5e704ed635163.png!small)![](https://image.3001.net/images/20200317/1584418531_5e704ee35fe4f.png!small)

###  窃听短信消息

保活广播接收器同时也在接收短信消息类型的系统广播，当收到此类型广播时则读取出短信内容和发信人并保存到配置文件中，为后续执行恶意活动窃取短信消息做准备。

![](https://image.3001.net/images/20200317/1584418559_5e704eff5c9bc.png!small)![](https://image.3001.net/images/20200317/1584418576_5e704f10b5f94.png!small)

###  激活设备管理员

Cerberus 木马除了通过隐藏图标的方式防止感染者卸载自身外，还通过激活设备管理员权限来防止感染者卸载自身，同时也为了防止其他安全软件查杀卸载
Cerberus 木马。

![](https://image.3001.net/images/20200317/1584418609_5e704f31dacbc.png!small)

##  启动后台服务

###  诱导启用无障碍服务

Cerberus 木马的所有敏感操作都严重依赖于无障碍服务的启用，其通过循环拉起 “启用无障碍服务界面” 来诱导感染者对其进行无障碍服务授权。

![](https://image.3001.net/images/20200317/1584418646_5e704f56d7df6.png!small)![](https://image.3001.net/images/20200317/1584418662_5e704f66e8c18.png!small)![](https://image.3001.net/images/20200317/1584418680_5e704f7822335.png!small)

###  请求窃听短信所需的权限

请求窃取短信消息和联系人所需的权限。

![](https://image.3001.net/images/20200317/1584418711_5e704f97a352d.png!small)

###  启动设备锁

根据 lockDevice 标记执行设备锁操作。

![](https://image.3001.net/images/20200317/1584418735_5e704faf97f63.png!small)

![](https://image.3001.net/images/20200317/1584418758_5e704fc64ee97.png!small)![](https://image.3001.net/images/20200317/1584418772_5e704fd406c59.png!small)

###  更新辅助服务状态到 payload

![](https://image.3001.net/images/20200317/1584418804_5e704ff416111.png!small)

##  无障碍服务

无障碍服务启用后通过监控界面元素，模拟点击界面授权按钮来完成权限的自我授权和设备管理员的激活操作。同时监控界面活动是否正在进行安全扫描、是否正在卸载恶意软件来避免木马被查杀和卸载。包括监控界面是否打开目标活动，将其通知给
payload 完成界面劫持攻击操作。

在无障碍服务中模拟点击激活按钮，完成激活设备管理员防止被用户卸载，也为后续锁定设备提供权限支撑。

![](https://image.3001.net/images/20200317/1584418856_5e705028c9464.png!small)![](https://image.3001.net/images/20200317/1584418871_5e70503789e82.png!small)

监控界面是否在 Google Play 保护机制扫描界面，如果是则发送回退事件防止被查杀。

![](https://image.3001.net/images/20200317/1584418901_5e7050552d72c.png!small)

监控当前前台活动发送到 payload 执行相关攻击操作。

![](https://image.3001.net/images/20200317/1584418922_5e70506aa4de7.png!small)

##  木马传播机制

Cerberus 木马的作者曾在 Twitter 上表明，其传播采用钓鱼网站以 Flash Player 的形式进行传播来诱导用户下载安装恶意木马。
**建议用户在网站下载应用时应特别注意网站的真实性和安全性避免被钓鱼或劫持攻击** 。

![](https://image.3001.net/images/20200317/1584418949_5e705085bf8d6.png!small)![](https://image.3001.net/images/20200317/1584418975_5e70509faa72e.png!small)![](https://image.3001.net/images/20200317/1584418990_5e7050ae07c15.png!small)

##  总结

Cerberus 恶意木马通过字符串混淆、执行流混淆、动态加载代码、动态解密字符串和实现了一个简单的计步器机制来对抗安全人员的分析工作。同时利用了
Android
无障碍服务的屏幕监控功能，通过监控手机屏幕内容的改变事件，模拟点击危险权限授权按钮进行自我授权、监控用户的安全扫描和卸载行为进行自我保护以及监控前台应用活动界面完成对目标的劫持攻击。

对于本次分析遗憾的是由于 C2 服务器的关闭导致无法获取到核心的 payload 代码和相关恶意指令，从而无法进行更加全面的分析木马的攻击机制。但
payload 想要完成攻击终究还是依赖于无障碍服务的启用，我相信 Cerberus 木马家族的新变种也会依赖于该功能，所以建议在日常使用 Android
设备时应谨慎启用设置中的无障碍服务开关。

Cerberus 仍是目前较为活跃的 Android 平台新型木马，其作者通过租赁的方式进行盈利，同时在黑市和 Twitter
上宣传木马内容从而吸引恶意活动参与者购买此木马。

此类木马危害极大，普通用户在下载相关软件时请首先确认网站的真实性，确保软件来源的可靠性防止被钓鱼攻击下载到此类恶意软件。

##  参考文章

> <https://www.threatfabric.com/blogs/cerberus-a-new-banking-trojan-from-the-> underworld.html>

***本文作者： 北京链安安全实验室，转载请注明来自FreeBuf.COM**  

