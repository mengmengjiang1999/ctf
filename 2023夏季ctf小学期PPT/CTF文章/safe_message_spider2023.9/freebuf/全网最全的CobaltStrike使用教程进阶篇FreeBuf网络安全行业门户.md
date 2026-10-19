**前言**

在这篇文章中，斗哥将详细介绍一下Cobalt Strike的各个模块是干什么的以及部分模块的具体使用方式。

 **Cobalt Strike模块详解**

 **2.1 Cobalt Strike 模块**

Cobalt Strike 模块的功能选项，如下图。

![](https://image.3001.net/images/20210927/1632732188_6151841c293dcbdb5ca66.jpg!small)

●New Connection：打开一个新的”Connect”窗口。在当前窗口中新建一个连接，即可同时连接不同的团队服务器( 便于团队之间的协作)。

●Preferences：偏好设置，首选项，用于设置Cobalt Strike主界面、控制台、TeamServer 连接记录、报告的样式。

●Visualization：将主机以不同的权限展示出来（主要以输出结果的形式展示）。

●VPN Interfaces：设置VPN接口。

●Listeners：创建监听器。

●Script Manager：查看和加载CNA脚本。

●Close：关闭当前与TeamServer的连接。

 **2.2 View模块**

View 模块的功能选项，如下图。

![](https://image.3001.net/images/20210927/1632732237_6151844d69982471e528c.jpg!small)

●Applications：显示被控机器的应用信息。

●Credentials：通过HashDump或mimikatz获取的密码或者散列值都储存在这里。

●Downloads：从被控机器中下载的文件。

●Event Log：主机上线记录，以及与团队协作相关的聊天记录和操作记录。

●Keystrokes：键盘记录。

●Proxy Pivots：代理模块。

●Screenshots：屏幕截图模块。

●Script Console：控制台，在这里可以加载各种脚本。（链接）

●Targets：显示目标。

●Web Log：Web 访问日志。

 **2.3 Attacks模块**

 **下面介绍Attacks模块下的Packages 和 Web Drive-by 模块。**

1.Packages模块

依次单击 “Attacks” → “Packages” 选项，可以看到一系列功能模块，如下图。

![](https://image.3001.net/images/20210927/1632732561_6151859159b6765ef8dc7.jpg!small)

●HTML
Application：基于HTML应用的Payload模块，通过HTML调用其他语言的应用组件进行攻击测试，提供了可执行文件、PowerShell、
VBA三种方法。

●MS Office Macro：生成基于Office病毒的Payload 模块。

●Payload Generator：Payload 生成器，可以生成基于C、C#、COM Scriptlet、 Java、 Perl、
PowerShell、Python、 Ruby、 VBA等的Payload。

●USB/CD AutoPlay：用于生成利用自动播放功能运行的后门文件。

●Windows Dropper:捆绑器，能够对文档进行捆绑并执行Payload。

●Windows
Executable:可以生成32位或64位的EXE和基于服务的EXE、DLL等后门程序。在32位的Windows操作系统中无法执行64位的Payload,
而且对于后渗透测试的相关模块，使用32位和64位的Payload会产生不同的影响，因此在使用时应谨慎选择。

●Windows Executable (S):用于生成一个Windows
可执行文件，其中包含Beacon的完整Payload,不需要阶段性的请求。与Windows
Executable模块相比，该模块额外提供了代理设置，以便在较为苛刻的环境中进行渗透测试。该模块还支持PowerShell脚本，可用于将●Stageless
Payload注入内存。

2.Web Drive-by 模块

依次单击 “Attacks” → “Web Drive-by” 选项，可以看到一系列基于网络驱动的功能模块，如下图。

![](https://image.3001.net/images/20210927/1632732594_615185b223264758e3cf3.jpg!small)

Manage：管理器，用于对TeamServer上已经开启的Web服务进行管理，包括 Listener 及 Web Delivery模块。

●Clone Site：用于克隆指定网站的样式。

●Host File：用于将指定文件加载到Web目录中，支持修改Mime Type。

●Script Web Delivery：基于Web的攻击测试脚本，自动生成可执行的Payload。

Signed Applet Attack：使用Java自签名的程序进行钓鱼攻击测试。如果用户有Applet 运行权限，就会执行其中的恶意代码。

●Smart Applet
Attack：自动检测Java的版本并进行跨平台和跨浏览器的攻击测试。该模块使用嵌入式漏洞来禁用Java的安全沙盒。可利用此漏洞的Java版本为1.6.0_45以下及1.7.0
_21以下。

●System Profiler：客户端检测工具，可以用来获取一些系统信息，例如系统版本、浏览器版本、Flash版本等。

 **2.4 Reporting模块**

Reporting模块可以配合Cobalt Strike的操作记录、结果等，直接生成相关报告，如下图。

![](https://image.3001.net/images/20210927/1632732632_615185d8afd168ba0b016.jpg!small)

●activity report 活动报告生成。

●Hosts report 主机报告。

●Indicators opromisef com 目标报告。

●Sessions report 会话报告。

●Social engineering report 社会工程学报告。

●Reset Data 重置数据。

●Export data 数据出口。

 **常用模块具体使用**

测试环境如下：

 **系统**

|

 **服务**

|

 **i** **p**  
  
---|---|---  
  
kali

|

teamserver

|

192.168.123.210  
  
win2008

|

边界服务器(victim)

|

192.168.123.193 1.1.1.10  
  
win2012

|

DC域控(victim)

|

1.1.1.2  
  
 **注意：因为IP地址是动态获取的，所以可能IP地址会发生改变。**

 **3.1 用户驱动攻击**

用户驱动攻击攻击简单来说就是控制端通过远程控制让受控端来执行某一些操作。  
常见的用户驱动攻击的模块如下：屏幕截图、键盘记录、进程处理、端口扫描、用户发现、文件管理、远程vnc、浏览器代理(仅针对ie浏览器)等，如下图所示。

![](https://image.3001.net/images/20210927/1632732677_61518605688accfb762a8.jpg!small)

因为Beacon的每次回连时间默认为60秒，为了方便测试，我们通过可以通过sleep命令将回连时间改为1秒。

可以通过图形化设置，如下图。

![](https://image.3001.net/images/20210927/1632732714_6151862a872d6a55651dc.jpg!small)

![](https://image.3001.net/images/20210927/1632732727_61518637c561fd6a20960.jpg!small)

也可以直接通过命令行设置，因为图形化页面也只是代替我们输入命令而已，本质上都是一样的。

![](https://image.3001.net/images/20210927/1632732754_615186529c038da3f9ce4.jpg!small)

####  **3.1.1 浏览器代理**

该模块用于对目标靶机上的ie浏览器进行代理攻击。

具体使用步骤如下：

1、选择 Browser Privot 代理。

![](https://image.3001.net/images/20210927/1632732946_6151871299b8276cbec2e.jpg!small)

2、选择对应的进程。

![](https://image.3001.net/images/20210927/1632733034_6151876aa467b03351321.jpg!small)

这里我们要将Proxy Serve Port 的值记录下来。

在命令行可以看到浏览器代理已经成功开启。

![](https://image.3001.net/images/20210927/1632733060_6151878468a5d86ac3dfd.jpg!small)

3、为浏览器设置代理。![](https://image.3001.net/images/20210927/1632733104_615187b0c32cf7390eb51.jpg!small)

注意：代理服务器的IP地址为teamserver的IP地址，代理端口为刚刚记录下的Proxy Serve Port 的值。

4、对浏览器进行代理攻击。

如果目标用户曾经通过IE浏览器登录某网站后台，并保存登录信息。这时候我们只需要通过访问目标后台地址即可实现免密登录。

目标靶机登录后台页面如下：

![](https://image.3001.net/images/20210927/1632733146_615187da4ae73fc3c7850.jpg!small)

我们这时候可以在开启代理的浏览器中直接访问网站后台的url，即可成功登录，运行结果如下。

![](https://image.3001.net/images/20210927/1632733194_6151880ae59f875bf2f05.jpg!small)

5、通过browserpivot stop 关闭浏览器代理。

![](https://image.3001.net/images/20210927/1632733858_61518aa2b1379bd6eba24.jpg!small)

####  **3.1.2 远程VNC**

该模块可以对目标用户进行远程控制，具体使用步骤如下。

选择VNC模块进行利用。

![](https://image.3001.net/images/20210927/1632734065_61518b714605697481487.jpg!small)

运行结果如下：

![](https://image.3001.net/images/20210927/1632734113_61518ba13e514db19d7f3.jpg!small)

####  **3.1.3 文件管理**

该模块对目标文件系统进行管理使用，例如上传文件、创建文件等，具体使用步骤如下。

选择File Browser模块进行利用。

![](https://image.3001.net/images/20210927/1632734198_61518bf676402b03d9cca.jpg!small)

运行结果如下：

![](https://image.3001.net/images/20210927/1632734229_61518c15961b68eb5df9a.jpg!small)

####  **3.1.4 Net View**

该模块用于显示域列表、计算机列表或指定计算机的共享资源列表，具体使用步骤如下。

选择对应的Net View模块利用即可。

![](https://image.3001.net/images/20210927/1632734353_61518c914761147682ba2.jpg!small)

运行结果如下：

![](https://image.3001.net/images/20210927/1632734401_61518cc162c489dc24c97.jpg!small)

注意：如果目标服务器上并没有开启Computer Browser服务，会返回6118错误码，如下图。

![](https://image.3001.net/images/20210927/1632734486_61518d169226ce46cec89.jpg!small)

解决方式：

1 **.** 关闭防火墙。

2.在命令行输入services.msc打开服务

3.开启Server、WorkStation以及Computer Browser服务，将Computer Browser服务属性设置为”手动启动即可”。

![](https://image.3001.net/images/20210927/1632734514_61518d321b66f842d7a52.jpg!small)

####  **3.1.5 端口扫描**

该模块用于探针目标主机所在网段内主机端口开放情况，使用步骤如下。

1、选择对应的 Port Scan 模块进行利用。

![](https://image.3001.net/images/20210927/1632734545_61518d51a422af60b36d5.jpg!small)

2、选择需要探针的网段、端口范围、最大连接数以及使用的协议类型。

![](https://image.3001.net/images/20210927/1632734578_61518d7230458f75c522c.jpg!small)

3、查看命令行，发现扫描已经开始运行。

![](https://image.3001.net/images/20210927/1632734612_61518d940cf4dc0af1a15.jpg!small)

4、在View视图内的Targets可以查看扫描结果。

![](https://image.3001.net/images/20210927/1632735943_615192c767092e2d87427.jpg!small)、

![](https://image.3001.net/images/20210927/1632735963_615192db236ccfbb0a384.jpg!small)

####  **3.1.6 进程列表**

该模块用于查看目标的进程，使用该模块可以对目标主机进行进程注入、屏幕截图，键盘记录、删除进程等操作，使用步骤如下。

1、右键选择Explore下的Process List模块。

![](https://image.3001.net/images/20210927/1632736003_61519303c9eedf731da93.jpg!small)

2、控制台输出区可以查看进程列表。

![](https://image.3001.net/images/20210927/1632736032_61519320bbb76fab9faaf.jpg!small)

3、选择explore.exe进程，点击Screenshot进行屏幕截取。

![](https://image.3001.net/images/20210927/1632736083_61519353d2f7603b636e3.jpg!small)

运行结果可以在view视图的Screenshots中查看。

![](https://image.3001.net/images/20210927/1632736098_61519362e1bd635693056.jpg!small)

4、点击Log Keystrokes进行键盘记录，运行结果可以在view视图的Keystrokes中查看。

![](https://image.3001.net/images/20210927/1632736126_6151937e256b14390d408.jpg!small)

####  **3.1.7 屏幕截取**

该模块用于对目标屏幕进行截取，该模块运行的结果与上述在进程列表中通过Screenshot进行截图的结果基本一致，具体使用步骤如下。

右键选择Explore下的Screenshot模块进行利用即可。

![](https://image.3001.net/images/20210927/1632736189_615193bd4fe7b1b91a429.jpg!small)

 **会话管理**

测试环境拓扑如下：

 **系统**

|

 **服务**

|

 **ip**  
  
---|---|---  
  
kali-cs

|

teamserver

|

192.168.123.193  
  
kali-msf

|

metasploit

|

192.168.123.183  
  
win2008

|

边界服务器(victim)

|

192.168.123.210  
  
win7-sp

|

内网主机

|

192.168.123.45  
  
 **注意：因为IP地址是动态获取的，所以可能IP地址会发生改变。**

####  **4.1 cobalt strike派生会话**

#####  **4.1.1 cobalt strike自身增加会话**

1、首先创建一个新的监听器，用于自身派生会话。

![](https://image.3001.net/images/20210927/1632736228_615193e4d5dc0b91b925d.jpg!small)

2、然后在要派生的会话上右键点击Spawn即可。

![](https://image.3001.net/images/20210927/1632736253_615193fdf2a2a2e93f961.jpg!small)

3、选择要派生到刚刚新建的监听器上，点击choose即可。

![](https://image.3001.net/images/20210927/1632736278_615194162240f8d71e28d.jpg!small)

4、可以看到会话成功派生。

![](https://image.3001.net/images/20210927/1632736303_6151942f96cecdd747379.jpg!small)

#####  **4.1.2 在其他teamserver上做备份会话**

1、在另一台linxu服务器上开启teamserver。

![](https://image.3001.net/images/20210928/1632814478_6152c58e62c3bfa1dfe90.jpg!small)

2、通过客户端连接上新开启的teamserver。

![](https://image.3001.net/images/20210928/1632814506_6152c5aa038b3b472eadc.jpg!small)

3、新建一个监听器，用于将会话派生到新开启的teamserver上。

![](https://image.3001.net/images/20210928/1632814531_6152c5c300193db5810b8.jpg!small)

4、选择将要派生到teamserver的会话，通过spawn模块派生即可。

![](https://image.3001.net/images/20210928/1632814557_6152c5ddbcde05e1447ad.jpg!small)

5、在新开启的teamserver上查看会话是否成功派生。

![](https://image.3001.net/images/20210928/1632814583_6152c5f7079aec5dd4c37.jpg!small)

这里可以看到会话成功派生。

####  **4.2 cobalt strike派生metasploit会话**

1、在 kali-msf 服务器上开启metasploit框架，并开启监听。

![](https://image.3001.net/images/20210928/1632814625_6152c621bb95069502faa.jpg!small)

2、在cobalt strike上创建一个监听器。

![](https://image.3001.net/images/20210928/1632814648_6152c6384268567899bb1.jpg!small)

3、通过Spawn将会话派生到新创建的监听器中。

![](https://image.3001.net/images/20210928/1632814671_6152c64f4bee730a2be28.jpg!small)

4、在msf服务器上查看会话是否已经成功派生。

![](https://image.3001.net/images/20210928/1632814694_6152c666d497a66d4e40f.jpg!small)

####  **4.3 metasploit 生成木马与cobalt strike会话**

1、通过 msfvenom 生成木马文件。

![](https://image.3001.net/images/20210928/1632815813_6152cac577537fcd5b0dd.jpg!small)

其中LHOST和LPORT要设置为teamserver的IP与端口。

2、在cobalt strike上创建一个监听器。

![](https://image.3001.net/images/20210928/1632815884_6152cb0c548354539f889.jpg!small)

3、将木马文件上传到目标靶机，并执行。

![](https://image.3001.net/images/20210928/1632815909_6152cb25db3b827d9d515.jpg!small)

这时候就可以看到，目标成功在cobalt strike上线。

####  **4.4 metasploit使用溢出exp与cobalt strike会话**

这里我们将使用ms14-064漏洞进行测试。

这里简单介绍一下ms14-064漏洞：

Microsoft Windows
OLE远程代码执行漏洞，OLE（对象链接与嵌入）是一种允许应用程序共享数据和功能的技术，远程攻击者利用此漏洞通过构造的网站执行任意代码，影响Win95+IE3
–Win10+IE11全版本。

具体利用流程如下：

1、在msf服务器上搜索ms14-064模块。

![](https://image.3001.net/images/20210928/1632815951_6152cb4f8b97e3a82151d.jpg!small)

2、使用对应模块，并设置参数。

这里我们使用exploit/windows/browser/ms14_064_ole_code_execution模块，参数设置如下。

![](https://image.3001.net/images/20210928/1632815974_6152cb66e888e7b21bddf.jpg!small)

这里要简单说明几个参数的作用：

1.set disablepayloadhandler
True：这告诉metasploit框架，它不需要在metasploit框架内创建处理程序来服务有效负载连接。

2.set PrependMigrate
true：告诉metasploit框架修改其stager，以便在利用之后立即迁移到另一个进程，此选项对于客户端攻击非常重要。它允许您的会话在被利用的应用程序崩溃或关闭时存活。

通过explot执行完，会生成一行漏洞利用代码：

![](https://image.3001.net/images/20210928/1632815998_6152cb7ea6901c2e6b409.jpg!small)

3、在 cobalt strike 上设置监听器。

![](https://image.3001.net/images/20210928/1632816115_6152cbf34e8952056b68c.jpg!small)

监听器设置的payload，hosts和port均要与msf上所设置的一致。

4、在目标靶机上的IE浏览器中执行上面的利用代码。

![](https://image.3001.net/images/20210928/1632816138_6152cc0ad330f6b04799e.jpg!small)

可以看到代码成功执行。

5、在cobalt strike上查看目标主机是否成功上线。

![](https://image.3001.net/images/20210928/1632816171_6152cc2bdb4832823c195.jpg!small)

####  **4.5 metasploit session 派生会话给cobalt strike**

这里我们依旧通过ms14-064漏洞进行演示。

1、通过ms14-064漏洞获取目标主机的meterpreter会话。

步骤与上述的基本一致，只需要修改Lhost、Lport以及disablepayloadhandler 的值即可，参数设置如下。

![](https://image.3001.net/images/20210928/1632816196_6152cc4411538916de5ac.jpg!small)

通过exploit执行获得利用代码，并在目标靶机上执行即可。

![](https://image.3001.net/images/20210928/1632816218_6152cc5a426cfff5b9b75.jpg!small)

这时候可以看到成功获取到meterpreter会话了。

2、将会话派生到 cobalt strike上。

使用 exploit/windows/local/payload_inject 模块，设置对应的参数。

![图片](https://image.3001.net/images/20210928/1632816429_6152cd2d660123a4e6f19.jpg!small)

在cobalt strike 上创建监听器。

![图片](https://image.3001.net/images/20210928/1632816720_6152ce50a966d99a55efa.jpg!small)

执行msf的模块，在cobalt strike上查看会话是否派生成功。

![图片](https://image.3001.net/images/20210928/1632816749_6152ce6dc26f96fb0e879.jpg!small)

可以看到会话成功派生。

 **后语**

在本篇文章中，斗哥简单介绍了CS中每个模块的作用，具体演示了如何使用用户驱动模块和派生会话模块。在下一篇文章中，斗哥还会为大家演示其他一些模块的具体使用，敬请期待。

![](https://image.3001.net/images/20210928/1632816777_6152ce895e537aa8f78cc.jpg!small)

