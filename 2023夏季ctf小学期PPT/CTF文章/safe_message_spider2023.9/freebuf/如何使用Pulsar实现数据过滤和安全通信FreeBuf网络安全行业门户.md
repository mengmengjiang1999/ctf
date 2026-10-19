## 关于Pulsar

Pulsar是一款针对数据通信安全的强大工具，该工具可以帮助广大研究人员实现数据过滤和安全（隐蔽）通信，并通过使用各种不同的协议来创建安全的数据传输和聊天隧道。比如说，在Pulsar的帮助下，我们可以通过TCP连接来接收数据，并通过DNS数据包将其转发到真实的数据目的地址。

## 工具安装&配置

注意：我们需要确保本地设备上安装并配置好了Go v1.8环境，因为Pulsar基于Go语言开发，因此Go环境是构建Pulsar所必备的。

接下来，使用下列命令将该项目代码克隆至本地，并构建Pulsar项目代码：

    
    
    $ cd pulsar
    
    $ export GOPATH=$(shell pwd)
    
    $ go get golang.org/x/net/icmp
    
    $ go build -o bin/pulsar src/main.go

或者直接使用make命令：

    
    
    $ make

## 数据连接器

数据连接器就是一个简单的通信信道，帮助我们与外部世界进行连接。在数据连接器的帮助下，我们可以使用Pulsar并从不同的数据源读取或写入数据。

### 命令行终端

默认的数据出入连接器，支持通过STDIN读取数据，通过STDOUT写入数据。

### TCP

通过TCP连接读取或写入数据：

    
    
    tcp:127.0.0.1:9000

### UDP

通过UDP数据包读取或写入数据：

    
    
    udp:127.0.0.1:9000

### ICMP

通过ICMP数据包读取或写入数据：

    
    
    icmp:127.0.0.1 (the connection port is obviously useless)

### DNS

通过DNS数据包读取或写入数据：

    
    
    dns:fakedomain.net@127.0.0.1:1994

### 自定义配置

我们还可以使用--in参数来选择数据输入连接器，使用--out选项来选择数据输出连接器：

    
    
    --in tcp:127.0.0.1:9000
    
    --out dns:fkdns.lol:2.3.4.5:8989

## 数据处理器

数据处理器将允许我们在数据的传输过程中修改数据，我们也可以任意选择组合使用数据处理器。

### Stub

默认的数据处理器，什么都不会操作，允许数据直接通过。

### Base32

Base32编码/解码器：

    
    
    --handlers base32

### Base64

Base64编码/解码器：

    
    
    --handlers base64

### Cipher

CTR密码工具，支持CTR模式下的AES/DES/TDES加密，默认为AES：

    
    
    --handlers cipher:<key|[aes|des|tdes#key]>

### 解码

我们可以使用--decode选项来使用所有数据处理器的解码模式：

    
    
    --handlers base64,base32,base64,cipher:key --decode

## 工具使用样例

在下列演示样例中，我们将使用Pulsar来创建一个基于DNS协议的安全双向通信信道，并通过TCP连接来读取数据，然后通过隧道发送加密数据：

    
    
    [nc 127.0.0.1 9000] <--TCP--> [pulsar] <--DNS--> [pulsar] <--TCP--> [nc -l 127.0.0.1 -p 9900]

192.168.1.198：

    
    
    $ ./pulsar --in tcp:127.0.0.1:9000 --out dns:test.org@192.168.1.199:8989 --duplex --plain in --handlers 'cipher:supersekretkey!!'
    
    $ nc 127.0.0.1 9000

192.168.1.199：

    
    
    $ nc -l 127.0.0.1 -p 9900
    
    $ ./pulsar --in dns:test.org@192.168.1.199:8989 --out tcp:127.0.0.1:9900 --duplex --plain out --handlers 'cipher:supersekretkey!!' --decode

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/jacopodl/Pulsar/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Pulsar：** 【[ _GitHub传送门_](https://github.com/jacopodl/Pulsar)】

