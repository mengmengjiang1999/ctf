**最近国外安全研究人员，又发布了一个Gamaredon组织的攻击样本，利用恶意程序对乌克兰进行攻击，伪装成行政诉讼，如下所示：**

![](https://image.3001.net/images/20190924/1569297365_5d8993d5998e7.png!small)

Gamaredon是一个俄罗斯的APT攻击组织，首次出现于2013年,主要是针对乌克兰进行网络间谍活动。2017年，Palo
Alto披露过该组织针对乌克兰攻击活动的细节，并首次将该组织命名为Gamaredon group。

该组织主要利用受感染域名、动态DNS、俄罗斯和乌克兰国家代码顶级域名（ccTLD）以及俄罗斯托管服务提供商来分发其定制的恶意软件。

之前Gamaredon团队会使用大量使用现成的工具，经过发展，也开始定制开发相关的恶意软件，其自定义开发的恶意软件包括以下功能：

> 1、用于下载和执行其选择的附加有效负载的机制
>
> 2、能够扫描特定文件类型的系统驱动器
>
> 3、捕获屏幕截图的能力
>
> 4、能够在用户的安全上下文中远程执行系统上的命令
>
> 5、SFX文件攻击

## 样本分析

恶意程序运行之后释放一个伪装成行政诉讼的WORD文档Document.docx，以及其它恶意脚本程序并运行，如下所示：

![](https://image.3001.net/images/20190924/1569297377_5d8993e18414e.png!small)

在%appdata%目录下释放的文件，如下所示：

![](https://image.3001.net/images/20190924/1569297384_5d8993e805236.png!small)

5369.cmd是一个混淆的脚本，通过cmd.exe程序执行：

![](https://image.3001.net/images/20190924/1569297387_5d8993eb33d00.png!small)

分析脚本，拷贝11816.txt到同目录下的Document.docx，伪装成行政诉讼的WORD文档：

![](https://image.3001.net/images/20190924/1569297391_5d8993ef4b9ac.png!small)

同时拷贝18415.txt到%APPDATA%\Microsoft\Installer目录下shellscript.cmd，如下所示：

![](https://image.3001.net/images/20190924/1569297406_5d8993fe77d65.png!small)

脚本去混淆，删除无用的脚本代码，结果如图：

![](https://image.3001.net/images/20190924/1569297410_5d8994022b461.png!small)

生成jqGVSbE.vbs脚本，然后再拷贝9383.txt到%APPDATA%\Microsoft\Installer目录下的shellscript.exe程序，拷贝8954.txt到%APPDATA%\Microsoft\Windows\Start
Menu\Programs\Startup目录下shellscript.lnk，最后启动相应的脚本，删除文件，生成的两个主脚本程序在%APPDATA%\Microsoft\Installer目录下。

![](https://image.3001.net/images/20190924/1569297414_5d899406c8886.png!small)

### jqGVSbE.vbs

此脚本的内容是修改注册表，允许对文档的VB模块进行访问和修改，并启动VBA宏，如下所示：

![](https://image.3001.net/images/20190924/1569297418_5d89940a2e3d5.png!small)

### 8954.txt

此脚本是一个lnk快捷方式，用于生成自启动目录下的shellscript.lnk，指向的目标为生成的shellscript.vbs脚本，如下所示：

![](https://image.3001.net/images/20190924/1569297422_5d89940e37e7c.png!small)

包含的内容，如下所示：

![](https://image.3001.net/images/20190924/1569297425_5d8994115a4de.png!small)

### 18415.txt

此脚本被复制到%APPDATA%\Microsoft\Installer目录下shellscript.cmd,也是一个混淆的脚本，如下所示：

![](https://image.3001.net/images/20190924/1569297434_5d89941ae2c3f.png!small)

### shellscript.cmd

下面分析一下主脚本程序shellscript.cmd，去混淆之后，如下所示：

![](https://image.3001.net/images/20190924/1569297440_5d89942068d44.png!small)

（1）拼接远程服务器URL地址[http://list-sert.ddns.net](http://list-sert.ddns.net/)，如下所示：

![](https://image.3001.net/images/20190924/1569297451_5d89942b2b2df.png!small)

（2）在%APPDATA%\Microsoft\SystemCertificates\My\Certificates\PowerShell目录下生成ps1脚本和vbs脚本，如下所示：

![](https://image.3001.net/images/20190924/1569297454_5d89942ec6f63.png!small)

生成后的脚本：

![](https://image.3001.net/images/20190924/1569297457_5d8994319d91b.png!small)

（3）将生成的vbs脚本，并设置为计划任务启动项，如下所示：

![](https://image.3001.net/images/20190924/1569297462_5d899436463a8.png!small)

自启动计划任务如下所示：

![](https://image.3001.net/images/20190924/1569297465_5d899439eab6e.png!small)

（4）设置浏览器代码，并通过之前shellscript.exe程序发送数据包到远程服务器URL

[http://document-listing.ddns.net](http://document-listing.ddns.net/)，并下载相应的程序到%TEMP%目录，如下所示：

![](https://image.3001.net/images/20190924/1569297469_5d89943d8375f.png!small)

（5）生成的VBS脚本，主要用于启动生成PS脚本：

![](https://image.3001.net/images/20190924/1569297473_5d899441d0323.png!small)

生成的PS脚本，主要用于远程连接服务器，下载相应的恶意程序，如下所示：

![](https://image.3001.net/images/20190924/1569297479_5d899447cd78c.png!small)

（6）于远程服务器未连接成功，导致下载恶意程序失败，创建的文件大小为0KB，正常情况下载下来的文件应该为一个远控程序：

![](https://image.3001.net/images/20190924/1569297485_5d89944d4d6be.png!small)

## IOCs

### URL：

> [http://list-sert.ddns.net](http://list-sert.ddns.net/)
>
> [http://document-listing.ddns.net](http://document-listing.ddns.net/)

### MD5：

> Email LibreOffice 12B5371D60129F305743284EDFB59B50
>
> shellscript.cmd 986FB45573C836B9F791B0BE30353CAB
>
> shellscript.vbs BB1ABBF4960D7A0A45BE76BFC83F82CA
>
> PowerShellCertificates_1A9E9938.ps1 A34EF150FDBE13ABF8A628A1C25643BA
>
> PowerShellCertificates_1A9E9938.vbs CE84A815C9DCE52CC5177C2D76A2B418

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

