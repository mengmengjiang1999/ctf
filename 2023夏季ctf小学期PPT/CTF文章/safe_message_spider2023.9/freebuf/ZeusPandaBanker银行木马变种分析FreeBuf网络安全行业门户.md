## 一、概述(前言)  

**从2007年开始，ZeusPanda Banker 银行木马已经演变出了很多不同的变种版本并展开攻击，近日360企业安全华南基地反病毒团队检测到Zeus
Panda Banker通过仿冒邮件又发起新一轮网络攻击。新变种病毒Zeus Panda
Banker使用了更高强度的代码加密技术，更灵活更强大的恶意插件分发，盗取用户的银行账户、窃取受害者信息，攫取钱财。**

后门病毒Zeus Panda Banker通过伪装成
“您的信用卡在苹果商城消费了了2812.56美元”的邮件进行传播，用户点击恶意链接后，将会下载的Word文档。

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263725037781.png!small)

盗取其银行账户同时还会收集用户计算机内的数据信息，包括系统版本，CPU情况，内存，用户名，系统中的服务项，浏览器中保存的密码、证书等信息等。不仅如此，木马可随时通过远程操控进行模块下发安装VNC模块，键盘记录，截屏等功能

## 二、技术细节详细分析

用户点击恶意链接后，将会下载的Word文档（如下图），病毒作者将文档伪造成内容被加密保护，用户必须开启宏才可以显示内容，为了防止分析，病毒作者将宏代码高度混淆加密

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/1526370247614.png!small)

Zeus Panda Banker使用ZwWriteVirtualMemory将解密后的PE文件写入到svchost

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263702577372.png!small)

a) 攻击流程图& Shellcode

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263702679367.png!small)  

Zeus Panda Banker通过
shellcode解密出一个新的Win32PE文件并加载到自身内存空间执行，然后进行修复导入表、重定位、最后修正OEP开始执行功能代码

解密出的EXE的OEP：

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/152637027736.png!small)

b) 反调试检测

通过遍历进程列表、读取注册表、文件路径和一些系统监控工具的设备名称，判断是否被反病毒人员进行分析，如果检测到有以下环境，则不做任何事情并结束进程

 **检测广告弹窗杀手:**

    
    
    C:\popupkiller.exe、C:\stimulator.exe、C:\TOOLS\execute.exe

 **检测沙箱环境：**

> SbieDll.dll
>
> andboxie_SingleInstanceMutex_Control （互斥体名称）
>
> Frz_State （冰点还原-互斥体名称）

 **检测Wireshark** **：**

> \\\\.\NPF_NdisWanIp驱动设备名
>
> Wireshark 进程名

 **检测Wine** **环境：**

> Kernel32.wine_get_unix_file_name导出函数
>
> HKEY_CURRENT_USER\Software\WINE 注册表项

 **检测进程列表：**

    
    
    Immunity、processhacker、procexp、procmon、idaq、reghot、aut2exe、perl、python

 **检测监控软件驱动设备名：**

    
    
     \\.\REGVXG Regmon
    
    \\.\FILEVXG  Filemon
    
    \\.\REGSYS   RegMON
    
    \\.\FILEM    FileMON
    
    \\.\TRW    TRW2000

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263705684901.png!small)

使用CRC32计算DLL模块导出表函数名称，得到hash后对比。计算硬盘序列号的CRC32值，创建互斥体等

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263711566121.png!small)

使用RC4解密硬编码的字符串，并且每个加密字符串的密钥都是唯一的，以此来增加静态分析难度

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263711728308.png!small)  

SHA256 用来加密用户电脑名称或系统安装时间，作为互斥体名称

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263707335009.png!small)

导入RSA密钥，加密HTTP数据，上传到C&C服务器

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263712831355.png!small)

释放自身到C:\Users\user\AppData\Roaming\\[任意目录]\ MDeskTopGC.exe，添加注册表启动项

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263713165497.png!small)

c) 注入Svchost.exe  

木马以远程线程的方式将自身注入到svchost进程中，以svchost做为傀儡进程，执行木马的功能

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263713477705.png!small)  

创建多个子线程，功能包括：初始化GDI函数截屏、修改浏览器配置，释放DLL、写入注册表启动项、监控注册表、启动项文件、防止删除自保护、上传用户数据、上传截屏以及键盘记录日志

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263713728501.png!small)

d) 功能模块分析

 **1\. 截屏**

获取GDI函数，截取屏幕图片

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263713931369.png!small)  

  

发送截屏文件和键盘记录文件到C&C服务器，随后删除保存的截图文件

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263714127635.png!small)  

**2\. 浏览器注入**

修改火狐浏览器配置

通过读取火狐浏览器的配置文件C:\Users\user\AppData\Roaming\Mozilla\Firefox\profiles.ini里面的KEY
“IsRelative“来判断用户的配置文件prefs.JS的路径是否是相对目录，然后读取profiles.ini配置文件中的path来获取保存prefs.js的路径。

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263715038768.png!small)  

由于Mozilla
Firefox支持多用户，每个用户的配置文件可以由Profiles.INI中的[Profile0]键名后面的数字递增，该木马在遍历的时候会修改所有用户的配置文件

Profiles.INI文件内容：

 **![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263715249607.png!small)  
**

 ****

得到prefs.js文件的内容后，通过正则查找并禁用spdy协议配置项：

    
    
     user_pref("network.http.spdy.enabled",false)；
    
    user_pref("network.http.spdy.enabled.http2",false);

如果没有找到则追加到配置文件末尾

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263715481716.png!small)  

修改后的火狐浏览器prefs.js配置文件差异：

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263715646492.png!small)  

修改IE浏览器配置

修改注册表

    
    
    Software\Microsoft\Windows\CurrentVersion\InternetSettings

键值

    
    
    WarnonBadCertRecving，EnableHTTP2，EnableSPDY3_0

达到禁止弹出窗口阻止提醒

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263716099569.png!small)  

修改Chrome浏览器快捷方式

遍历锁定在任务栏中的以及桌面上的快捷方式link文件，找到Chrome.EXE的快捷方式，

修改快捷方式目标exe启动参数，—disable-http2禁用HTTPS

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263716305076.png!small)

    
    
    C:\Users\user\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\*
    
    C:\Users\Public\Desktop\*.lnk

遍历进程，找到浏览器进程

遍历进程列表，尝试使用OpenProcess打开进程，如果打开成功，则复制目标进程权限，然后判断目标进程是不是浏览器进程（firefox、iexplore、chrome、MecrosoftEdge、opera、MecrosoftEdgeCP）

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263716561057.png!small)

成功打开一个进程句柄后，判断释放是目标浏览器

释放DLL文件& 反射加载

找到目标浏览器后，解密出libinject.dll，然后在内存中展开，
通过传入CRC32加密过的函数名来遍历DLL导出表得到两个导出函数地址，保存到两个全局变量中，

然后检测用户机器上是否有 HKEY_CURRENT_USER\\\SOFTWARE\\\Microsoft\\\IBaxx 键项,
如果存在，随后初始化调用libinject.dll导出函数，并注入到Chrome进程中

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263716851081.png!small)

DLL导出表

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263717018784.png!small)

传入浏览器进程ID进行DLL模块的注入

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263717203471.png!small)

libinject.dll
通过ZwWow64QueryInformationProcess64，ZwWow64ReadVirtualMemory64用于搜索PEB中的NTDLL，然后使用NtCreateSection
NtMapViewOfSection NtUnmapViewOfSection查找注入DLL模块（x32 / x64）工作所需的API地址

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263765696910.png!small)

libinject.dll 会向浏览器注入云端下发的webInject模块（x86/x64），该模块是负责获取受害者的银行账户信息![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263791714497.png!small)

####  **3\. 自我保护**

监控注册表

添加注册表启动项达到自启动的目的:

    
    
    Software\Microsoft\Windows\Currentversion\Run
    
    C:\Users\user\AppData\Roaming\SweetScape\010Editor\Repository\QMDeskTopGC.exe

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263717965501.png!small)  

并调用RegNotifyChangeKeyValue函数来监控注册表，防止启动项被删除

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263717435269.png!small)

监控文件

除了监控注册表启动项防止被删除，还使用 **FindFirstChangeNotificationW** 函数监控木马副本的寄生目录：
**C:\Users\user\AppData\Roaming**
，在开始监控之前，先读取木马Buffer到内存中做备份，一旦目录下的文件被重命名或重写，就判断木马和寄存目录的文件夹是否存在，不存在则重新创建目录，如果木马副本文件被删除，则从内存读取之前保存的木马Buffer重新写入该文件

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263718193487.png!small)![Zeus
Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263718603122.png!small)

####  **4\. 收集信息**

解密C&C主机地址

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263718965961.png!small)

解密出的URL： <https://bithetbuter.ru/1afhecysoduunselisoig.dat>，随后拆分URL，获取域名部分

 **![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263719284816.png!small)**

通过WMI接口来取系统信息、电脑名称、木马副本进程名称、木马版本信息、系统语言、时区、通过WQL命令查询防火墙、杀软信息等

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263719615354.png!small)

**使用WQL命令通过WMI接口查询杀软信息：**

    
    
     Select * from FirewallProduct
    
    Select * from AntiSpywareProduct
    
    Select * from AntiVirusProduct

导入公钥到CSP

导入公钥到CSP对象后，把之前收集的用户电脑环境信息拼接成JSON对象

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/1526371978316.png!small)  

拼接后的JSON信息：

{"BotInfo"：{"systime":1526027380,"process":"QMDeskTopGC.exe","user":"WIN0LRR8CGQ4H6\\\user","id":"D1E9050600E8205AA2E7E5C50DEBA231","botnet":"notset","version":"2.6.8"},"File":{"name":"1afhecysoduunselisoig.dat"}

加密数据

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/1526372008323.png!small)

发送加密后的数据到C&C服务器

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263720268591.png!small)  

生成接收数据的URL地址，然后发送加密的数据到：<https://bithetbuter.ru/mMrzRDbYm/vKR3fF/K/s/QgPPiqi3d7n/m/Uw>

 **5. 远程指令**

木马通过指令，达到模块下发

指令 |  功能  
---|---  
botnet |  僵尸网络  
check_config |  检查配置文件  
send_report |  发送报告  
check_update |  检查更新  
url_config |  设置URL  
url_webinjects |  注入URL  
url_update |  更新木马地址  
url_plugin_vnc32 |  VNC模块32位下载地址  
url_plugin_vnc64 |  VNC模块64位下载地址  
url_plugin_vnc_backserver |  VNC反弹服务地址  
url_plugin_grabber |  密码拦截模块下载地址  
url_plugin_backsocks |  反弹SOCK模块下载地址  
url_plugin_backsocks_backserver |  反弹SOCK服务下载地址  
reserved |  未知  
dgaconfigs |  未知  
grabber_pause |  暂停记录  
grab_softlist |  获取软件列表  
grab_pass |  获取浏览器中保存的密码  
grab_form |  获取网页表单信息  
grab_cert |  获取浏览器证书信息  
grab_cookie |  获取Cookie  
grab_del_cookie |  删除Cookie  
grab_del_cache |  删除缓存  
notify_process |  通知程序  
url_plugin_keylogger |  键盘记录模块下载地址  
keylog_process |  键盘记录进程  
screen_process |  获取运行的进程列表  
url_plugin_webinject32 |  web注入模块32位下载地址  
url_plugin_webinject64 |  web注入模块64位下载地址  
remove_csp |  卸载CSP  
inject_vnc |  注入VNC  
webfilters |  过滤网络请求  
webinjects |  注入网页  
  
**6\. 卸载功能**  

清除添加的注册表启动项，以及释放的文件，木马副本等

![Zeus Panda
Banker银行木马变种分析](https://image.3001.net/images/20180515/15263720475363.png!small)

写入清理痕迹的bat脚本到用户临时目录下：C:\Users\user\AppData\Local\Temp\upd71e4a9ab.bat

脚本内容如下：

    
    
    @echooff..:d..del /F /Q 
    
    "C:\Users\user\AppData\Roaming\SweetScape\010Editor\Repository\QMDeskTopGC.exe"
    
    "C:\Users\user\AppData\Roaming\SweetScape\010Editor\Repository\secmod.ozc"
    
    "C:\Users\user\AppData\Roaming\SweetScape\010Editor\Repository\QQProtect.aga"
    
    "C:\Users\user\AppData\Roaming\SweetScape\010Editor\Repository\010Editor70.dau"
    
    ..ifexist "C:\Users\user\AppData\Roaming\SweetScape\010Editor\Repository\QMDeskTopGC.exe"
    
    gotod..if exist"C:\Users\user\AppData\Roaming\SweetScape\010Editor\Repository\secmod.ozc"
    
    gotod..if exist 
    
    "C:\Users\user\AppData\Roaming\SweetScape\010Editor\Repository\QQProtect.aga" 
    
    gotod..if exist
    
    "C:\Users\user\AppData\Roaming\SweetScape\010Editor\Repository\010Editor70.dau" 
    
    gotod..del /F "C:\Users\user\AppData\Local\Temp\upd71e4a9ab.bat"
    
    "C:\Users\user\AppData\Roaming\SweetScape\010Editor\Repository\QQProtect.aga"
    
    goto d ifexist "C:\Users\user\AppData\Roaming\SweetScape\010Editor\Repository\010Editor70.dau"
    
    goto d

## 三、IOCs & URLs

域名  
---  
bithetbuter.ru  
api.ipify.org  
supratparfa.com/4/forum.php  
losupsofof.ru/4/forum.php  
depeparand.ru/4/forum.php  
  
**MD5**

文件名  |  MD5  
---|---  
Panda-Banker.exe  |  353E713E1F980B696147B6E05E4D476C  
Hancitor.doc  |  EE055BC7F83D2B32E8D09B88B02E79D3  
  
## 四、总结

越来越多的攻击者结合社会工程学手段，利用邮件精准传播进行恶意攻击行为，相比传统的恶意程序更具有成功性很多安全意识薄弱的用户很容易中招。在此提醒广大用户，陌生人发来的陌生文档，邮件不要轻易打开！

 ***本文作者：neverstop，转载请注明来自 FreeBuf.COM**

