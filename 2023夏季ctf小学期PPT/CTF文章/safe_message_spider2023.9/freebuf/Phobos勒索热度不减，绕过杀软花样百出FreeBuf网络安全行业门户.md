## 背景概述

老牌勒索病毒Phobos自从2019年出现以来，一直保持着很高的活跃度，并常年占据勒索病毒榜单前三，其不断推出新变种，并频繁通过
**RDP暴破、钓鱼邮件等方式** 对企业单位及个人用户进行攻击，使受害者遭受数据财产的严重损失，影响十分恶劣。

![](https://image.3001.net/images/20211202/1638446128_61a8b430baa1ed629a080.png!small)

/Phobos勒索信页面/

近日，深信服安服应急响应中心联合终端安全团队捕获了一起Phobos勒索病毒的新变种，其通过 **伪装成正常的程序安装包** ，将
**勒索病毒主体加密保存到配置文件中** 的方式，绕过杀软检测。

可以看到，不同于以往简单粗暴的直接加密，勒索病毒越来越多的开始借鉴APT攻击中的一些高级技术，以提高攻击成功的概率，用户在使用电脑时更加需要增强安全意识，注意防范。

## 样本分析

病毒母体伪装成了一个程序安装包：

![](https://image.3001.net/images/20211202/1638446155_61a8b44b079e409912b98.png!small)

运行后会将程序安装释放到%appdata%\Plagius Device Service目录下并运行plagsync.exe：

![](https://image.3001.net/images/20211202/1638446172_61a8b45cb75e0c6affc99.png!small)

plagsync.exe运行后会加载动态链接库libGLES3.dll，如下：

![](https://image.3001.net/images/20211202/1638446186_61a8b46aa10749d1ab9d4.png!small)

调用导出函数sws_printVec2，如下：

![](https://image.3001.net/images/20211202/1638446202_61a8b47ad70c68320422e.png!small)

读取changelog.xml文件：

![](https://image.3001.net/images/20211202/1638446219_61a8b48bf1fe177eb1b0e.png!small)

changelog.xml为一个xml格式的文件，如下：

![](https://image.3001.net/images/20211202/1638446242_61a8b4a2aa17f9028b848.png!small)

其中被插入了多段二进制数据：

![](https://image.3001.net/images/20211202/1638446257_61a8b4b10a39a4e681e11.png!small)

逐段提取出xml中的二进制数据：

![](https://image.3001.net/images/20211202/1638446270_61a8b4bebdc577967d429.png!small)

将二进制数据解密到内存中，结果为一个PE文件，即Phobos勒索病毒本体：

![](https://image.3001.net/images/20211202/1638446283_61a8b4cb9dd6dab414775.png!small)

装载运行解密出的PE文件，执行勒索行为：

![](https://image.3001.net/images/20211202/1638446297_61a8b4d9948d61340e030.png!small)

将进程对应文件即plagsync.exe拷贝到Local目录：

![](https://image.3001.net/images/20211202/1638446309_61a8b4e586b17d6b8fdf0.png!small)

通过注册表将plagsync.exe设置为自启动：

![](https://image.3001.net/images/20211202/1638446651_61a8b63be6e84b0d1e36c.png!small)

将”Plagius Device Service”目录下的文件khjdr5ytekre.txt也拷贝到Local目录，但事实上”Plagius Device
Service”目录下并不存在文件khjdr5ytekre.txt，因此猜测为其他变种的勒索payload，病毒的开发者这里可能使用了错误的变种文件，同时也可以看到Phobos已经开始用各种不同的方式绕过杀软：

![](https://image.3001.net/images/20211202/1638446630_61a8b626c91948af4d750.png!small)

将plagsync.exe以及khjdr5ytekre.txt拷贝到系统启动项目录，如下：

![](https://image.3001.net/images/20211202/1638446350_61a8b50e64f994d971b53.png!small)

结束如下进程：

![](https://image.3001.net/images/20211202/1638446584_61a8b5f828c364556c975.png!small)

删除磁盘卷影：

![](https://image.3001.net/images/20211202/1638446567_61a8b5e789cbfab9c3d5a.png!small)

关闭防火墙：

![](https://image.3001.net/images/20211202/1638446551_61a8b5d7946f19ad4b92c.png!small)

获取磁盘信息：

![](https://image.3001.net/images/20211202/1638446541_61a8b5cd0e5f44a91c852.png!small)

遍历文件：

![](https://image.3001.net/images/20211202/1638446531_61a8b5c3e7c3d562c6dc3.png!small)

遍历共享文件：

![](https://image.3001.net/images/20211202/1638446515_61a8b5b3e1486c20c000c.png!small)

对文件进行加密，加密后的文件加上”Devos”后缀：

![](https://image.3001.net/images/20211202/1638446497_61a8b5a1a9db0e3e440b6.png!small)

生成并打开勒索信息文件：

![](https://image.3001.net/images/20211202/1638446456_61a8b578938a769e9279c.png!small)

## 日常加固

  1. 日常生活工作中的重要的数据文件资料设置相应的访问权限，关闭不必要的文件共享功能并且定期进行非本地备份；
  2. 使用高强度的主机密码，并避免多台设备使用相同密码，不要对外网直接映射3389等端口，防止暴力破解；
  3. 避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；
  4. 定期检测系统漏洞并且及时进行补丁修复。

> 前期变种分析文章：《[
> **准备交赎金？当心Phobos勒索病毒二次加密！**](http://mp.weixin.qq.com/s?__biz=MzI4NjE2NjgxMQ==&mid=2650238046&idx=1&sn=115c00415236cec5ede6791d11ee9e21&chksm=f3e2d62ac4955f3c3230c4568df1bdc6d76ed7081985009df73f86b369ce7176d1a4b27668c8&scene=21#wechat_redirect)》

