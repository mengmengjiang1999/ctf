![](https://image.3001.net/images/20191114/1573713951_5dccf81f27af5.jpg!small)

> 环境：Windows 7 32位
>
> 工具：Ollydbg、Wireshark
>
> 文件信息：
>
> 7229569b8e3d544c2901bcfa622c0c28

安全运维人员日前在进行系统安全检查时，在沙箱中捕获到一个高危恶意样本。经过简单的攻击路径回溯，得知该样本为一个邮件的附件，该邮件在投放给客户时被沙箱捕获，邮件附件被提取并还原。随后安全分析人员对该样本进行了简要分析。

![](https://image.3001.net/images/20191114/1573714052_5dccf88499b8e.jpg!small)

## Emotet背景

Emotet是一种银行木马恶意软件程序，它通过将计算机代码注入受感染计算机的网络堆栈来获取财务信息。但由于该木马具有模块化架构及自我传播功能，使它可以根据不同情形传播恶意软件。该木马编写者似乎也因此转变了商业模式，从针对欧洲的银行客户转变为了使用其基础设施为全球其他威胁行为者提供恶意软件包装和交付服务。

## 行为流程

![](https://image.3001.net/images/20191114/1573714181_5dccf9056b81b.jpg!small)

## 具体功能

### 1、钓鱼邮件

如下图所示，攻击者首先将含有恶意宏代码的Microsoft文档作为邮件附件发送给受害者，并尝试诱使受害者启动宏。

![](https://image.3001.net/images/20191114/1573714237_5dccf93decca7.png!small)

宏代码进行反混淆后，核心代码功能为调用powershell.exe执行一段由Base64编码算法加密的代码。

![](https://image.3001.net/images/20191114/1573714359_5dccf9b7376f4.png!small)

加密的代码进行解密与反混淆后，得到的结果如下图所示。该段代码的功能为从指定网址下载文件并保存为620.exe，若下载文件的长度大于35841则执行该文件。

![](https://image.3001.net/images/20191114/1573714376_5dccf9c800bbc.png!small)

五个恶意网址链接如下：

> [http://timurjayaindosteel.com/wp-> content/suqzjgt3871/](https://www.freebuf.com/wp-> admin/post.php?post=220305&action=edit)[http://gioitrerusseykeo.com/wp-> content/81q8053/](https://www.freebuf.com/wp-> admin/post.php?post=220305&action=edit)
>
> [https://insideiost.com/is32htu/zbmm4323/](https://www.freebuf.com/wp-> admin/post.php?post=220305&action=edit)
>
> [http://supremesaadiq.com/wordpress/uf7kz53/](https://www.freebuf.com/wp-> admin/post.php?post=220305&action=edit)
>
> [http://kelseygouldie.com/cgi-bin/91ap40244/](https://www.freebuf.com/wp-> admin/post.php?post=220305&action=edit)

### 2、Emotet银行木马

下载的样本将在内存中分配空间，释放并解密出一段shellcode，该shellcode为Emotet银行木马的核心代码。

![](https://image.3001.net/images/20191114/1573714464_5dccfa20f2c70.png!small)

该样本将生成一个参数，该参数用以判断该进程是否以含参的形式启动。

![](https://image.3001.net/images/20191114/1573714487_5dccfa37243e6.png!small)

![](https://image.3001.net/images/20191114/1573714487_5dccfa376243c.png!small)

若该进程以不含参的形式启动，则创建相应含参子进程，创建完成后退出父进程。

![](https://image.3001.net/images/20191114/1573715817_5dccff6975237.png!small)

若该进程以含参的形式启动，首先将获取大量随机字符串。该字符串将随机进行拼接作为复制体的文件名，例如在本次运行中使用的字符串wce、query，拼接后得到文件名wcequery。

![](https://image.3001.net/images/20191114/1573715834_5dccff7ac355a.png!small)

样本将获取用户名并生成该次连接中的通信标识，ROOTXPC_20C82D8C。

![](https://image.3001.net/images/20191114/1573715858_5dccff92ca215.png!small)

样本将获取文件名machinefolders.exe并尝试删除该文件。

![](https://image.3001.net/images/20191114/1573715887_5dccffafe2cc3.png!small)

样本将复制自身至C:\Windows\system32\文件夹下，文件名为先前拼接得到的字符串wcequery。

![](https://image.3001.net/images/20191114/1573717385_5dcd0589515eb.png!small)

样本将自身的复制体作为服务创建，达到持久化感染系统的目的。

![](https://image.3001.net/images/20191114/1573717405_5dcd059dd0cc4.png!small)

样本将修改服务描述以增加恶意服务的隐蔽性，随后启动该服务并结束子进程。

![](https://image.3001.net/images/20191114/1573717450_5dcd05ca8540a.png!small)

样本将生成与服务端通信的加密密钥。

![](https://image.3001.net/images/20191114/1573717471_5dcd05dfac818.png!small)

样本将枚举正在运行的进程，进程信息随后将与先前获取的主机用户名等信息被加密，将被加密的信息设为参数三。

![](https://image.3001.net/images/20191114/1573717483_5dcd05ebacaba.png!small)

![](https://image.3001.net/images/20191114/1573717498_5dcd05fa73422.png!small)

样本将获取将要进行通信的服务端IP，该IP有多个候选，候选值在内存地址00220390处开始，本次连接使用的是该地址的前四个字节，即为181.59.253.20。

![](https://image.3001.net/images/20191114/1573717511_5dcd060721241.png!small)

样本将获取大量字符串，该字符串将被随机选取用以拼接URL。

![](https://image.3001.net/images/20191114/1573717523_5dcd0613992dd.png!small)

样本将拼接HTTP头部的Referer字段。

![](https://image.3001.net/images/20191114/1573717535_5dcd061f33601.png!small)

样本将通过内置的Base64算法对先前被加密的参数三进行编码，将得到的结果设为参数二。

![](https://image.3001.net/images/20191114/1573717563_5dcd063b7df32.png!small)

下图即为参数二的具体信息。

![](https://image.3001.net/images/20191114/1573717578_5dcd064a18762.png!small)

样本将调用GetTickCount()函数得到返回值，该返回值随后通过内置算法从”ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789”中生成随机字符串，该字符串设为参数一。

![](https://image.3001.net/images/20191114/1573717600_5dcd066042ef6.png!small)

样本将参数二中的”+”替换为”%2B”，”/”替换为”%2F”，”=”替换为”%3D”，随后将参数一与参数二通过”=”拼接，该拼接字符串将作为第一次发送给服务端的通信信息。

![](https://image.3001.net/images/20191114/1573717614_5dcd066e2f78b.png!small)

样本将向服务端发送通信信息。

![](https://image.3001.net/images/20191114/1573717627_5dcd067b2c2dc.png!small)

若当前使用的ip已失效，样本将重新在IP列表中获取新IP并选取随机字符串拼接新的URL直至连接成功，连接成功后将发送最新拼接的通信信息。

![](https://image.3001.net/images/20191114/1573717638_5dcd0686203a8.png!small)

若主机与控制端成功建立连接，样本将尝试获取从服务端返回的信息。

![](https://image.3001.net/images/20191114/1573717650_5dcd06927f19a.png!small)

样本将解密返回的信息。

![](https://image.3001.net/images/20191114/1573717664_5dcd06a087e8f.png!small)

样本将自身的复制体添加进注册表自启动项并设置键值，达到持续感染系统的目的。

![](https://image.3001.net/images/20191114/1573717756_5dcd06fc2f375.png!small)

![](https://image.3001.net/images/20191114/1573717756_5dcd06fc57562.png!small)

![](https://image.3001.net/images/20191114/1573717756_5dcd06fc51722.png!small)

样本将获取的数据写入文件。

![](https://image.3001.net/images/20191114/1573717773_5dcd070d64f7b.png!small)

样本从服务端获取的数据将通过三种不同方式被执行，调用CreateThread()函数执行获取的shellcode；调用CreateProcessAsUserW()函数执行被下载的文件；调用CreateProcessW()函数执行被下载的文件。

![](https://image.3001.net/images/20191114/1573717786_5dcd071a1cfa2.png!small)

### 3、后续恶意组件

由于服务端获取后续恶意组件的URL已失效，通过对恶意IP与恶意URL的关联分析可得知，后续恶意组件有如下类型：

> 私密信息窃取模块：搜集并窃取如用户名密码等个人私密信息；
>
> 内网横向移动模块：进行内网感染与横向移动，将木马植入内网其余主机；
>
> 银行木马模块：下载其余类型（例如TrickBot）的银行木马，联合感染主机；
>
> 勒索软件模块：加密主机文件，向受害者勒索赎金。

## IOCs

### MD5

> 7229569b8e3d544c2901bcfa622c0c28
>
> e83c5ba6be05ec51ae6ceb2470fcfdf3

### C&C

> <http://timurjayaindosteel.com/wp-content/suqzjgt3871/>
>
> <http://gioitrerusseykeo.com/wp-content/81q8053/>
>
> <https://insideiost.com/is32htu/zbmm4323/>
>
> <http://supremesaadiq.com/wordpress/uf7kz53/>
>
> <http://kelseygouldie.com/cgi-bin/91ap40244/>
>
> 181.59.253.20
>
> 14.160.93.230
>
> 74.208.68.48
>
> 104.131.58.132
>
> 68.183.190.199
>
> 62.75.143.100
>
> 159.203.204.126
>
> 151.80.142.33
>
> 123.168.4.66
>
> 46.28.111.142
>
> 46.101.212.195
>
> 183.82.97.25
>
> 190.10.194.42
>
> 217.199.160.224
>
> 186.1.41.111
>
> 185.86.148.222
>
> 185.187.198.10
>
> 114.79.134.129
>
> 200.57.102.71
>
> 80.85.87.122
>
> 87.106.77.40
>
> 190.230.60.129
>
> 125.99.61.162
>
> 142.93.82.57
>
> 77.55.211.77
>
> 82.196.15.205
>
> 139.5.237.27
>
> 178.249.187.151

### 防护措施

> 1、不轻易执行来历不明的文档格式文件中的宏代码；
>
> 2、不轻易下载可疑邮件中的附件；
>
> 3、及时更新病毒库，查杀主机中的恶意病毒；

 ***本文作者：东巽科技2046Lab，转载请注明来自FreeBuf.COM**

