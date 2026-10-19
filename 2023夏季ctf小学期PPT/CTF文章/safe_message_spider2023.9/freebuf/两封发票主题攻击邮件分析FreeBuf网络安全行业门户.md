**一大早收到两封“发票主题”攻击邮件。**

## 0x1基本情况

3月6日上午，邮箱连续收到两封以税务发票“Tax
Invoice”为主题的邮件，全部是英文信息，接收时间分别是早上8：27和9：15，附件是windows系统.cab压缩格式文件，内含PE文件，初一看，是一个很直接、很low的攻击方式。

![](https://image.3001.net/images/20200310/1583809874_5e6705527904b.png!small)

![](https://image.3001.net/images/20200310/1583809893_5e670565eabb6.png!small)

其中第二封邮件的附件没有接收完全（仅仅336B），第一封邮件包含完整的PE文件（cab文件大小为1.02M），利用WINRAR打开，两个.cab文件如下图所示，其中内含的两个exe分别创建于2020年3月5日的22：18和23：13，文件创建时间很接近。

![](https://image.3001.net/images/20200310/1583809910_5e67057605b25.png!small)

![](https://image.3001.net/images/20200310/1583809910_5e67057630081.png!small)

## 0x2邮件头分析

本地邮件接收客户端是outlook，两封邮件寄送地址分别是ecomm@leviton.com和info@orcspain.es，两封邮件在outlook主页面看不到具体的收件人信息。

查看两封邮件的头部，分别如下，已去掉收件方相关信息：

邮件| 邮件头  
---|---  
邮件1|  
  
X-Barracuda-Envelope-From: info@orcspain.es  
  
  
X-Barracuda-Effective-Source-IP: server.marinebiz.tv[95.168.186.145]  
  
  
X-Barracuda-Apparent-Source-IP: 95.168.186.145  
  
  
Received: from [::1] (port=52094 helo=server.marinebiz.tv) by  
  
  
server.marinebiz.tv with  
esmtpa (Exim 4.92) (envelope-from  
  
  
<info@orcspain.es>) id 1jA0pC-0001rb-Ti; Fri, 06 Mar 2020  
05:56:47 +0530  
  
  
MIME-Version: 1.0  
  
  
Content-Type: multipart/mixed;  
boundary="=_b3c3f613c183dc3457d3a967d71d9688"  
  
  
Date: Fri, 6 Mar 2020 05:56:46 +0530  
  
  
From: "Lalitha .S " <info@orcspain.es>  
  
  
To: undisclosed-recipients:;  
  
  
Subject: Invoice No. 013696.  
  
  
Message-ID:  
<f40ee8eb3b3cb546f4e55cca5de1546b@orcspain.es>  
  
  
X-ASG-Orig-Subj: Invoice No. 013696.  
  
  
X-Sender: info@orcspain.es  
  
  
User-Agent: Roundcube Webmail/1.3.8  
  
  
X-AntiAbuse: This header was added to track abuse, please  
include it with any abuse report  
  
  
X-AntiAbuse: Primary Hostname - server.marinebiz.tv  
  
  
X-AntiAbuse: Original Domain - xxx.com.cn  
  
  
X-AntiAbuse: Originator/Caller UID/GID - [47 12] / [47 12]  
  
  
X-AntiAbuse: Sender Address Domain - orcspain.es  
  
  
X-Get-Message-Sender-Via: server.marinebiz.tv:  
authenticated_id: awards@shiptek20.com  
  
  
X-Authenticated-Sender:  
server.marinebiz.tv: awards@shiptek20.com  
邮件2|  
  
X-Barracuda-Envelope-From: ecomm@leviton.com  
  
  
X-Barracuda-Effective-Source-IP: server.marinebiz.tv[95.168.186.145]  
  
  
X-Barracuda-Apparent-Source-IP: 95.168.186.145  
  
  
Received: from [::1] (port=56596 helo=server.marinebiz.tv) by  
  
  
server.marinebiz.tv with  
esmtpa (Exim 4.92) (envelope-from  
  
  
<ecomm@leviton.com>) id 1jA1ZW-000FZ3-9n; Fri, 06 Mar 2020  
06:44:38 +0530  
  
  
MIME-Version: 1.0  
  
  
Content-Type: multipart/mixed;  
boundary="=_10de085ef3812b51106adcb305befeaa"  
  
  
Date: Fri, 6 Mar 2020 06:44:38 +0530  
  
  
From: Arun Khanduja <ecomm@leviton.com>  
  
  
To: undisclosed-recipients:;  
  
  
Subject: Tax Invoice for the Unit  
  
  
Reply-To: <ecomm@leviton.com>  
  
  
X-ASG-Orig-Subj: Tax Invoice for the Unit  
  
  
Mail-Reply-To: ecomm@leviton.com  
  
  
Message-ID:  
<46081d3d495fd3fea6779388c2042795@leviton.com>  
  
  
X-Sender: ecomm@leviton.com  
  
  
User-Agent: Roundcube Webmail/1.3.8  
  
  
X-AntiAbuse: This header was added to track abuse, please  
include it with any abuse report  
  
  
X-AntiAbuse: Primary Hostname - server.marinebiz.tv  
  
  
X-AntiAbuse: Original Domain - xxx.com.cn  
  
  
X-AntiAbuse: Originator/Caller UID/GID - [47 12] / [47 12]  
  
  
X-AntiAbuse: Sender Address Domain - leviton.com  
  
  
X-Get-Message-Sender-Via: server.marinebiz.tv:  
authenticated_id: awards@shiptek20.com  
  
  
X-Authenticated-Sender:  
server.marinebiz.tv: awards@shiptek20.com  
  
虽然，从邮件头我们可以看到，这两封邮件分别是以ecomm@leviton.com和info@orcspain.es账户发出，其中info@orcspain.es的名称为Lalitha
.S，ecomm@leviton.com 的名称是Arun Khanduja，两个账户名称差异很大，好像攻击者不是同一个人。

但是，经过分析后还是认为两封邮件属于同一攻击来源，主要根据如下：

> 1.两封邮件都是从server.marinebiz.tv发出，authenticated_id都是awards@shiptek20.com。
>
> 2.显示的收件人地址是“Undisclosed-Recipient”（导致在outlook无法看到收件人信息），Undisclosed-> Recipient设置可以让收件人收到邮件后无法查看收件人信息，用于群发邮件的时候，不让收件人看到其他接收邮件人的地址。
>
> 3.都利用Roundcube Webmail/1.3.8软件用于群发邮件，并且发送时间间隔很短。

server.marinebiz.tv的域名解析地址是：95.168.186.145，位于英国伦敦，直接telnet 95.168.186.145
25端口获取banner信息，确实是部署Exim4.92用作邮件发送服务器。

![](https://image.3001.net/images/20200310/1583810231_5e6706b793635.png!small)

另外，telnet 95.168.186.145 110的端口信息如下：

![](https://image.3001.net/images/20200310/1583810245_5e6706c56bd0d.png!small)

邮件接收服务器则是采用Dovecot， Dovecot是一个开源的 IMAP 和 POP3 邮件服务器，支持 Linux/Unix 系统。

访问95.168.186.145的80端口，访问页面如下：

![](https://image.3001.net/images/20200310/1583810258_5e6706d2957f3.png!small)

从该页面可以，该IP是属于cPanel公司的服务器，通过搜索发现cPanel是一个托管平台。

因此，可以初步判断awards@shiptek20.com是server.marinebiz.tv服务器的注册账户，攻击者利用该台服务器发起邮件攻击。网络搜索awards@shiptek20.com相关信息，发现该邮件地址是2020年ShipTek国际海事大奖的对外联系邮箱，该颁奖会议将于2020年4月7日在迪拜的Dusit
Thani酒店举办。如下图所示：

![](https://image.3001.net/images/20200310/1583810272_5e6706e0483ee.png!small)

![](https://image.3001.net/images/20200310/1583810299_5e6706fb8738b.png!small)

从网站上看，该机构应该属于一个合法企业，说明攻击者可能入侵了该机构的托管服务器用于发动网络攻击。

## 0x3邮件附件分析

从cab附件中解压完整的PE文件的文件属性如下图：

![](https://image.3001.net/images/20200310/1583810336_5e670720d9229.png!small)

该PE文件是一个win32程序，运行后在任务管理器中查看如下：

![](https://image.3001.net/images/20200310/1583810344_5e670728ef1e1.png!small)

在任务管理器，选择该PE文件，并且选择“打开文件位置”后，来到“%ppdata”目录下，如下图：

![](https://image.3001.net/images/20200310/1583810370_5e670742cfbd3.png!small)

直接到CMD下查看，发现该目录下生成一个名为E07D76.exe的隐藏文件，大小和“Invoice No. 013696.exe”一样，如下图所示：

![](https://image.3001.net/images/20200310/1583810371_5e67074326ea6.png!small)

原先运行的“Invoice No. 013696.exe”的会自动删除，在注册表下生成键值如下：

![](https://image.3001.net/images/20200310/1583810371_5e6707433bf6a.png!small)

利用Process Monitor查看PE的运行过程，发现该PE文件在运行后，不断连续调用新进程实例运行，如下图所示：

![](https://image.3001.net/images/20200310/1583810371_5e670743b2b7c.png!small)

利用wiereshark抓包，发现该PE连接的域名是assemba.co.uk，解析的ip地址是192.185.76.26，访问的是HTTP80端口，如下图所示：

![](https://image.3001.net/images/20200310/1583810371_5e670743dad83.png!small)

IP所在地址为：美国休斯顿。

![](https://image.3001.net/images/20200310/1583810372_5e67074407f49.png!small)

HTTP连接成功后，向目标主机的/jpg/five/fre.php页面发送POST数据包，发送的数据包括了windows系统当前登陆账户名、主机名称等，目前该页面无法访问，如下两图所示：

![](https://image.3001.net/images/20200310/1583810372_5e6707445b47f.png!small)

![](https://image.3001.net/images/20200310/1583810372_5e670744b1147.png!small)

用浏览器直接访问<http://192.185.76.26/jpg/five/fre.php>，服务器报404错误，可能该台服务器是攻击者入侵的服务器（被管理员发现）或攻击者尚未启动C2控制器进行实际操作，此外，根据返回的页面，我们发现该台服务器也是托管于cPanel。

![](https://image.3001.net/images/20200310/1583810373_5e67074518547.png!small)

利用OLLYICE调试该PE文件，运行后发现跳出如下界面：

![](https://image.3001.net/images/20200310/1583810373_5e6707457b529.png!small)

跟踪调试，发现该PE调用IsDebuggerPresent判定是否属于调试状态：

![](https://image.3001.net/images/20200310/1583810373_5e6707458e77e.png!small)

如果处于调试状态，则弹出对话框：

![](https://image.3001.net/images/20200310/1583810541_5e6707edc130b.png!small)

经过分析得知，该PE是AutoIT3编译而成。AutoIt是一个使用类似BASIC脚本语言的免费软件,它设计用于Windows
GUI(图形用户界面)中进行自动化操作。它利用模拟键盘按键，鼠标移动和窗口/控件的组合来实现自动化任务。

利用exe2aut进行反编译，发现无法成功，经过分析该exe基于最新版本的autoit3版本，目前的exe2aut不支持该版本。有兴趣的小伙伴可以跟踪动态调试。

## 0x4小结

这是一个非常粗暴的邮件攻击方法，攻击者直接通过发送exe恶意程序用于传播，而不是类似利用文档漏洞的攻击方式。EXE文件利用AutoIt3最新版制作，修改重新编译比较方便，并且目前网络上还很难找到直接反编译的工具，有利于攻击者代码保护。目前该PE文件已经被virustotal收录。

### IOCS:

> Invoice No. 013696.exe ：e8c64db377c590669b3fad71ac58fba8
>
> <http://assemba.co.uk/jpg/five/fre.php>
>
> 192.185.76.26

 ***本文原创作者：cgf99，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

