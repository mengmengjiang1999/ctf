**近期，英特尔在远程键盘APP中发现三个严重的安全漏洞之后，并没有决定修复这些漏洞，而是正式下架该应用，并且提醒用户停止使用。**

![Intel-Remote-Keyboard.jpg](https://image.3001.net/images/20180408/15231727578016.jpg!small)  

这款远程键盘APP是英特尔在2015年推出的Android应用程序，允许用户通过无线控制英特尔NUC和英特尔Compute Stick单板计算机设备。

CVE| 评分| 描述  
---|---|---  
CVE-2018-3641| 9.0（严重）| 在所有版本的英特尔远程键盘中提升权限，允许网络攻击者以本地用户的身份注入按键指令。  
CVE-2018-3645| 8.8（高）| 在所有版本的英特尔远程键盘中提升权限，允许本地攻击者将按键指令注入另一个远程键盘会话。  
CVE-2018-3638| 7.2（高）| 英特尔远程键盘的所有版本中的提升权限，允许授权的本地攻击者以特权用户的身份执行任意代码。  
  
三个漏洞分别由三个不同的研究人员发现，该漏洞会被黑客利用，获得访问权限，并将击键指令注入到远程键盘会话中，并在用户的Android设备上执行恶意代码。

其中两个漏洞的评分为“高”，另一个被列为“严重”。英特尔公司在一份安全公告中称：“英特尔已经远程键盘APP发布了产品停产通知，并建议所有用户尽早将其卸载。”

![Intel-Remote-Keyboard.png](https://image.3001.net/images/20180408/15231720486195.png!small)  

在应用下架前，Google Play Store中显示英特尔远程键盘APP安装量已经超过500000，平均评分为3.8分，并且最近一次更新是在去年六月份。

***参考来源：[bleepingcomputer](https://www.bleepingcomputer.com/news/security/intel-tells-users-to-uninstall-remote-keyboard-app-over-unpatched-security-bugs/)，由Andy编译，转载请注明来自FreeBuf.COM**

