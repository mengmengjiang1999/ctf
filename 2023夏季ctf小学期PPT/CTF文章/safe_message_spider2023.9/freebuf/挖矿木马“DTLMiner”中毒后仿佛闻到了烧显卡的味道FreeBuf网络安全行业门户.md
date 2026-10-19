**近日，瑞星安全专家率先监测到挖矿木马病毒“DTLMiner”最新变种，新版本病毒更换了IP和域名，并且增加了一个挖矿模块，新版挖矿模块会下载显卡驱动，利用显卡进行挖矿，大幅提升挖矿速度的同时会导致系统卡顿，显卡发热。目前，瑞星云安全系统显示，已有数千用户感染该挖矿病毒。**

下载后文件名  |  MD5  |  功能  
---|---|---  
%appdata%\Microsoft\cred.ps1  |  E05827E44D487D1782A32386123193EF  |
Powershell攻击模块  
%temp%\mn.exe  |  66EA09330BEE7239FCB11A911F8E8EA3  |  挖矿模块  
%temp%\4-8个字符的随机名称  |  CDF6384E4CD8C20E7B22C2E8E221F8C8  |  python编写的攻击模块  
%temp%\ddd.exe  |  8A2042827A7FCD901510E9A21C9565A8  |  新增挖矿模块  
  
表：病毒下载的各模块

新版挖矿木马病毒“DTLMiner”不仅会导致中毒机器CPU占用率过高，机器卡顿，同时还会导致显卡占用率过高，显卡发热等现象，严重影响用户正常工作。目前瑞星ESM已能成功查杀该病毒的最新版本。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824302_5c9d7a2e94d0c.png!small)

图：瑞星ESM查杀截图

**“DTLMiner”挖矿木马的黑历史：**

2018年12月，“驱动人生”的升级模块被不法分子利用传播挖矿木马病毒“DTLMiner”，短期内感染数万台计算机。

2019年2月、3月又分别进行了更新，增加了数字签名与弱口令攻击，攻击面进一步增大，同时又躲避查杀。

此次瑞星截获的“DTLMiner”已经是第5次变种。

 **针对该木马病毒对企业网络安全带来的潜在威胁，瑞星安全专家建议：**

> 1.安装永恒之蓝漏洞补丁，防止病毒通过漏洞植入；
>
> 2.系统和数据库不要使用弱口令账号密码；
>
> 3.多台机器不要使用相同密码，病毒会抓取本机密码，攻击局域网中的其它机器；
>
> 4.安装杀毒软件，保持防护开启。

##  **技术分析**

新版挖矿木马病毒“DTLMiner”通过漏洞和弱口令攻击植入，创建快捷方式开机自启动。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824366_5c9d7a6e47253.png!small)

图：病毒创建的快捷方式

快捷方式运行之后，执行flashplayer.tmp。此文件是一个脚本，使用JS 调用PowerShell脚本下载。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824386_5c9d7a82f081b.png!small)

图：flashplayer.tmp 内容

下载的文件就是下载模块，此模块会下载攻击模块和挖矿模块。下载模块使用多层混淆。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824454_5c9d7ac6618be.png!small)

图：多层混淆的下载模块

最终解密出下载脚本，脚本运行后首先获取本机网卡mac地址，获取本机安装的杀毒软件信息。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824483_5c9d7ae3cec91.png!small)

图：获取本机网卡和杀软信息

之后随机延时一段时间。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824511_5c9d7affc63cd.png!small)

图：延时一段时间

判断配置文件是否存在，如果不存在则下载对应样本。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824534_5c9d7b16469bb.png!small)

图：根据配置文件下载对应样本

### 1）如果配置文件k1.log不存在，则创建计划任务持久驻留。

根据用户权限不同，创建的计划任务不同，如果当前用户是管理员权限则访问：<http://v.y6h.net/g?h> \+
当前日期，如果当前用户非管理员权限则访问：<http://v.y6h.net/g?l> \+ 当前日期。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824564_5c9d7b348c857.png!small)

图：下载更新脚本

计划任务的功能是访问此网址，使用PowerShell执行获取到的内容。目前此网址处于无法访问状态，攻击者随时可以开启，下发任意脚本。

### 2）如果配置文件kkkk2.log不存在，则下载new.dat保存为cred.ps1，内容是混淆的PowerShell脚本。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824592_5c9d7b506d650.png!small)

图：下载cred.ps1

判断文件大小是否正确，如果正确则创建计划任务定时执行cred.ps1。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824619_5c9d7b6b2967a.png!small)

图：执行cred.ps1

cred.ps1 脚本被多层混淆。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824672_5c9d7ba045362.png!small)

图：多层混淆的cred.ps1脚本

解密后可以看到，此版本是V5。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824694_5c9d7bb686e97.png!small)

图：病毒版本

此模块主要还是为了攻击。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824729_5c9d7bd96f6bc.png!small)

图：cred.ps1脚本主要功能

调用永恒之蓝漏洞攻击。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824754_5c9d7bf202d8b.png!small)

图：永恒之蓝漏洞攻击

eb7函数针对win7和win2008。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824776_5c9d7c0840657.png!small)

图：eb7函数

eb8函数针对win8和win2012。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824806_5c9d7c263bca1.png!small)

图：eb8函数

SMB弱口令攻击。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824835_5c9d7c431870b.png!small)

图：SMB弱口令

完整的密码列表如下，如果使用以下密码，建议尽快修改。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190403/1554255507_5ca40e93d056c.jpg!small)

图：cred.ps1攻击模块内置的弱口令列表

攻击成功后，调用CopyRun函数，将
FlashPlayer.lnk和flashplayer.tmp植入被攻击机器，被攻击机器又会开始新的一轮循环，下载病毒攻击其它机器。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824862_5c9d7c5ed501e.png!small)

图：植入病毒

### 3）如果配置文件333.log不存在，则下载mn.dat，命名为mn.exe，此模块就是之前的挖矿模块。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824893_5c9d7c7d178dc.png!small)

图：下载mn.exe

###
4）如果配置文件kk4.log不存在，则下载ii.da，并使用4-8位随机字母命名，例如hjqgbs.exe，此模块就是之前的攻击模块，使用Python开发，使用pyinstaller打包。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824917_5c9d7c9579d6f.png!small)

图：下载ii.dat并随机命名

判断下载的文件大小是否正确，如果正确则创建计划任务运行此exe，根据不同的权限使用不同的方法运行，如果是管理员权限，直接创建计划任务运行此exe。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824940_5c9d7cac307de.png!small)

图：运行下载的exe

如果非管理员权限，则释放run.vbs脚本，将run.vbs脚本设置为计划任务，通过脚本运行此exe。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553824976_5c9d7cd02c6d8.png!small)

图：调用vbs脚本运行下载的exe

释放的run.vbs脚本。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825017_5c9d7cf96279c.png!small)

图：vbs脚本内容

此exe仍然使用窃取的数字签名。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825042_5c9d7d12802a0.png!small)

图：窃取的数字签名

解包后可以看到Python脚本。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825071_5c9d7d2f0cef0.png!small)

图：Python脚本

脚本使用了base64编码。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825103_5c9d7d4f6930e.png!small)

图：base64编码的脚本

解码后得到病毒的Python代码，代码中的关键字符串也进行了混淆。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825139_5c9d7d73d4fbc.png!small)

图：混淆的代码

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825165_5c9d7d8d99c34.png!small)

图：混淆的代码

去混淆后，可以看到最终的病毒代码，病毒最开始会通过内存映射，检测当前版本。首先打开内存映射读取内容，如果没有获取到映射的内存，则创建内存映射将自身的路径+“**”+当前版本号+“$$”写入到新创建的内存映射中。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825192_5c9d7da8916a6.png!small)

图：内存映射

如果获取到内存映射，则解析映射中的版本号和内存映射中的文件路径，计算MD5。如果当前程序的MD5和内存映射中路径对应的文件MD5相同，则不执行操作。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825226_5c9d7dca7dc8f.png!small)

图：计算MD5

否则判断当前版本是否大于内存映射中的版本，如果大于结束之前版本的进程，当前程序复制过去。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825278_5c9d7dfec52f4.png!small)

图：判断版本

之后就是攻击传播的部分，病毒内置的攻击IP段、弱口令账号密码列表。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825309_5c9d7e1d19694.png!small)

图：弱口令列表

弱口令密码又进行了扩充，完整的密码如下，如果当前计算机或者数据库软件使用了此列表中的密码，建议尽快修改密码。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190403/1554255461_5ca40e65bf86b.jpg!small)

图：Python攻击模块内置的密码列表

病毒仍然会抓取密码，因此局域网中多台机器使用相同密码，一台机器中毒，也会导致其它机器被攻击。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825339_5c9d7e3b4273c.png!small)

图：抓取密码

永恒之蓝漏洞攻击。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825362_5c9d7e5264faa.png!small)

图：永恒之蓝漏洞

开启共享，将病毒发送过去。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825384_5c9d7e681fe6f.png!small)

图：发送病毒

SMB弱口令攻击。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825422_5c9d7e8ed6746.png!small)

图：SMB弱口令攻击

MS SQL数据库弱口令攻击。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825452_5c9d7eac25c71.png!small)

图：MS SQL弱口令攻击

### 5）如果配置文件kk5.log不存在，则下载ddd.dat，命名为ddd.exe，此模块为新版挖矿模块，会下载显卡挖矿相关的驱动。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825491_5c9d7ed3d5565.png!small)

图：下载挖矿模块ddd.exe

挖矿模块运行后界面。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825527_5c9d7ef7de050.png!small)

图：挖矿模块界面

挖矿模块除了使用CPU挖矿之外，还会下载显卡挖矿相关的驱动，使用显卡进行挖矿。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825549_5c9d7f0ddc95d.png!small)

图：下载的显卡驱动

### 6）最后访问控制服务器，将本机状态信息信息上传到控制服务器，便于统计感染状态。

统计的信息包括本地网卡mac地址、安装的杀毒软件、系统版本、感染标志、当前用户组、当前用户名等。

![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825586_5c9d7f322de95.png!small)![挖矿木马“DTLMiner”](https://image.3001.net/images/20190329/1553825586_5c9d7f3264a2d.png!small)

图：统计信息

##  **IOC**

### md5：

> 17891737D9970812FE875D0B955B0E15
>
> 7441A59ABB6B4C96D0EAC70D884E8008
>
> 8A2042827A7FCD901510E9A21C9565A8
>
> CDF6384E4CD8C20E7B22C2E8E221F8C8
>
> E05827E44D487D1782A32386123193EF
>
> 3E96A29E82513C5859D5E508A75FA974
>
> 66EA09330BEE7239FCB11A911F8E8EA3

### Domain：

> mm.abbny.com
>
> mm.beahh.com
>
> lplp.beahh.com
>
> lplp.abbny.com
>
> lpp.beahh.com
>
> lpp.abbny.com

### ip：

> 128.199.64.236
>
> 27.102.107.137
>
> 27.102.118.147

 ***本文作者：瑞星，转载请注明来自FreeBuf.COM**

