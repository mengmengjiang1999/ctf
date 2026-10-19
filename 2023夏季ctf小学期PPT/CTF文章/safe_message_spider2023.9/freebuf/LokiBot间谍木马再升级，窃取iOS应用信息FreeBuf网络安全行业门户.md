**近日亚信安全截获了LokiBot间谍木马最新变种，LokiBot是一款著名的间谍木马，其通过垃圾邮件传播，窃取用户敏感数据，包括浏览器、电子邮箱、ftp、sftp密码及凭证。本次截获的LokiBot变种与之前版本不同的是，其还会窃取Windows上支持的IOS应用信息。亚信安全将其命名为：TSPY_LOKI.SMA。**

##  **攻击流程**

![](https://image.3001.net/images/20200424/1587698647_5ea25bd77a14c.png!small)

##  **病毒详细分析**

脱壳后，我们发现该病毒是VC++编写：

![](https://image.3001.net/images/20200424/1587698676_5ea25bf4dcb29.png!small)

其代码中存在大量花指令，payload在以下地址中：

![](https://image.3001.net/images/20200424/1587698686_5ea25bfead580.png!small)

病毒首先检查WSA是否启动，为socket做准备：

![](https://image.3001.net/images/20200424/1587698695_5ea25c0726926.png!small)

进入第一个payload，其主要功能是遍历计算机中的所有应用，根据相应的应用程序，到默认指定目录窃取用户的信息。

该病毒不仅识别包含了Windows常用的浏览器，还会窃取IOS应用信息：

![](https://image.3001.net/images/20200424/1587698703_5ea25c0fa15d3.png!small)

识别FTP软件：

![](https://image.3001.net/images/20200424/1587698711_5ea25c170c9ca.png!small)

识别邮箱应用：

![](https://image.3001.net/images/20200424/1587698717_5ea25c1d76e65.png!small)

窃取以上应用的相应文件和里面的信息：

**![](https://image.3001.net/images/20200424/1587698728_5ea25c28bb7ff.png!small)**

（1）窃取浏览器密码，以本机所安装的火狐浏览器为例：

先判断机器中的浏览器版本，定位浏览器的位置，窃取密码：

![](https://image.3001.net/images/20200424/1587698739_5ea25c33d7da2.png!small)![](https://image.3001.net/images/20200424/1587698747_5ea25c3b49894.png!small)

窃取信息步骤：

读取profiles.ini文件：

![](https://image.3001.net/images/20200424/1587698758_5ea25c46500ca.png!small)

读取登录信息：

![](https://image.3001.net/images/20200424/1587698766_5ea25c4eaed86.png!small)

读取密码的主要步骤是从内部key槽，对slot进行鉴权，随后破译密码：

![](https://image.3001.net/images/20200424/1587698779_5ea25c5b9601e.png!small)

（2）窃取IOS应用密码，首先会读取plutil.exe文件，该软件用于Windows支持IOS应用，从keychain.plist中窃取用户账号密码，最后转换格式保存在数组或者字典中，等待发送：

![](https://image.3001.net/images/20200424/1587698791_5ea25c67deb93.png!small)

（3）针对email所窃取的信息如下图：

![](https://image.3001.net/images/20200424/1587698807_5ea25c77bcafd.png!small)

窃取数据后，病毒会删除自身，并把自己备份到临时文件目录下，重命名为B3AB29.exe：

![](https://image.3001.net/images/20200424/1587698818_5ea25c8212474.png!small)

建立socket ，外联远程服务器<http://noniwire8.beget.tech/Brokenskull/fre.php>：

![](https://image.3001.net/images/20200424/1587698825_5ea25c896eb3f.png!small)

该域名为动态域名：

![](https://image.3001.net/images/20200424/1587698837_5ea25c955e8c4.png!small)

病毒停止系统lsass.exe进程中保护敏感信息的protected_storage服务：

![](https://image.3001.net/images/20200424/1587698849_5ea25ca13b983.png!small)

![](https://image.3001.net/images/20200424/1587698859_5ea25cabd6537.png!small)

读取内存中所有信息，发送数据：

![](https://image.3001.net/images/20200424/1587698868_5ea25cb42529d.png!small)

![](https://image.3001.net/images/20200424/1587698878_5ea25cbe5a2fb.png!small)

##  **解决方案**

> 不要点击来源不明的邮件以及附件；
>
> 不要点击来源不明的邮件中包含的链接；
>
> 请到正规网站下载程序；
>
> 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> 打开系统自动更新，并检测更新进行安装；

##  **IOC**

> SHA-1：C922961134235AAE9DCB06B304951562**602FF2
>
> URL：<http://noniwire8.beget.tech/Brokenskull/fre.php>

 ***本文作者： 亚信安全，转载请注明来自FreeBuf.COM**  

