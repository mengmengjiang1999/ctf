作者：黑蛋![](https://image.3001.net/images/20221102/1667378115_63622bc357f6c43f0e3ce.png!small)

​陌生链接可以随便点吗？《你安全吗》电视剧中，秦淮发给周游一个链接，称周游只要点击授权，秦淮就可以获取周游位置，玄乎其技。这个链接，就是我们此篇的关键：钓鱼网站。所谓的钓鱼网站到底是个什么东西，他是黑客手段中比较简单常见的一种技术，简单来说就是仿造正规网站，然后通过用户授权，输入关键信息，这些信息会反馈到黑客的服务器后台中，达到获取用户信息的目的。接下来我们详细的去介绍一下黑客手段之钓鱼网站。

![](https://image.3001.net/images/20221102/1667378117_63622bc5002e767595ae8.gif!small)

首先钓鱼网站类型多种多样，有以下几种常见的：

（1）短信诈骗：利用短信向用户发送链接，当用户点击链接的时候，通常会在手机上下载木马软件之类的东西。

（2）搜索引擎诈骗：当你跳转某个网站时，他会提醒你下载某个恶意软件，来解决问题。

（3）仿造网站诈骗：当你进入一个网站，你看着和平时网站相似的画面，很放心的输入你的账户密码，关键信息等，实则这些信息都会反馈到黑客手中。

以上只是简单的举例，实则花样百出。如果手机上下载了恶意软件，这些软件可以自己设置自启动，自己后台运行，获取键盘输入信息，各种网站浏览记录，手机保存照片视频等，把这些信息发送到黑客手中，获取用户在某个网站账户信息，就可以登录这个网站，获取更多的信息，亦或者进行其他恶意行为，也可以售卖用户信息，然后不法分子可以通过这些信息，对用户实施诈骗。

 **下面介绍一种钓鱼网站的制作方法：**

 **靶机:win10（作为一台服务器，里面部署了某个网站，比如wsdc（无效网站，这里只做例子）**

 **攻击机:kali**

注意：kali和win10可以互通，kali中可以访问wsdc这个网站。

（1）：

![](https://image.3001.net/images/20221102/1667378118_63622bc659cfd362daf52.png!small)

kali中自带的一个社会工程学工具集

（2）：

![](https://image.3001.net/images/20221102/1667378119_63622bc7451fbc1def9e1.png!small)

  * Social-Engineering Attacks：社会工程学攻击
  * Penetration Testing（Fast-Track）：渗透测试

  * Third Party Modules：第三方组件

  * Update the Social-Engineer Toolkit：更新软件

  * Update SET configuration：升级配置

（3）：

![](https://image.3001.net/images/20221102/1667378119_63622bc7e8be27b5b580c.png!small)

l spear-phishing attack：鱼叉式钓鱼攻击

l Website Attack：网站攻击

l Infectious Media Generator：介质感染攻击

l Mass Mailer Attack：邮件群发

l Arduino-Based
Attack（类似于单片机）：Arduino是一款便捷灵活、方便上手的开源电子原型平台。通过它可以模拟硬件，比如：串口设备。可以实现在OS禁用U盘自动播放功能情况下，依然能运行U盘中的病毒。

l Wireless Access Point Attack：无线接入点攻击

l QRCode Generator Attack：二维码攻击

l Powershell Attack：powershell攻击

（4）：

![](https://image.3001.net/images/20221102/1667378120_63622bc89b42ccf6b2ab9.png!small)

 **Credential Harvester Attack Method 凭证收割机攻击方法（钓鱼网站攻击）**

（5）：

![](https://image.3001.net/images/20221102/1667378121_63622bc92adf2e6735c26.png!small)

l Web模板

l 网站克隆器

l 自定义导入

（6）：

![](https://image.3001.net/images/20221102/1667378121_63622bc9dd5bcb646a6c2.png!small)

（7）：

![](https://image.3001.net/images/20221102/1667378122_63622bcacb6389e3998c4.png!small)

![](https://image.3001.net/images/20221102/1667378123_63622bcbbe4a8e0891789.png!small)

出现这代表你已经克隆成功了

然后我们在另一台主机上F问刚刚克隆的网制（也是本地IP）

制作完钓鱼网站，就可以开始钓鱼，如果有人点击这个网站，并输入信息，就可以在我们后台反馈：

![](https://image.3001.net/images/20221102/1667378124_63622bccd0f3484705afd.png!small)

这个网站和真实网站的登录界面是一模一样的，但你们克隆的并不是真正的服务器，我们克隆的网站只是克隆了一个登录界面

当我们登录之后，他便会自动跳回原来正确的网站，然后用户再输入了正确的用户名和密码就可以登录网站了，就像什么都没发生过。

SET就是利用大部分人们，输错账号密码，页面会重新刷新，便不会在意的心理去进行欺骗

 **陌生链接请不要轻易点击，谨防上当受骗！**

