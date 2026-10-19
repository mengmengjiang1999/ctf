**Polymorph是一个用Python3编写的框架，其允许实时修改网络数据包，为用户提供对数据包内容的最大化控制。该框架旨在实现任何现有协议（包括没有公共规范的私有协议）的网络数据包的实时修改。除此之外，其主要目的之一是为用户提供对数据包内容的最大化控制，并能够对信息执行复杂处理。**

**![Polymorph.png](https://image.3001.net/images/20180910/1536566695_5b9625a76c38f.png!small)**

## 安装

项目地址：<https://github.com/shramos/polymorph>

### 在Windows上安装

Polymorph可以在Windows操作系统上被安装，若要正常运行，需要以下必备组件：

> Python3（添加到Path），URL：<https://www.python.org/downloads/>
>
> Wireshark添加到Path），URL：<https://www.wireshark.org/download.html>
>
> Visual C++ Build Tools，URL：<https://www.visualstudio.com/en/thank-you-> downloading-visual-studio/?sku=BuildToolsrel=15>
>
> Winpcap（如果没和wireshark一起安装）。URL：<https://www.winpcap.org/install/default.htm>

一旦依赖安装好，你只需要打开控制台执行以下命令：

    
    
    pip install --process -dependency -links polymorph

注意，必须要以管理员身份打开控制台使用polymorph。

### 在Linux上下载和安装

Polymorph也用于在Linux操作系统（如Kali Linux）上安装和运行。 在安装框架之前，必须安装以下依赖：

    
    
    apt-get install build-essential python-dev libnetfilter-queue-dev tshark tcpdump python3-pip wireshark

在安装好依赖之后，可以使用Python pip通过以下方式安装框架本身：

    
    
    pip3 install polymorph

## Docker环境

从项目根目录：

    
    
    docker-compose up -d

任何机器访问：

    
    
    docker exec -ti [polymorph | alice | bob] bash

## 如何使用Polymorph

Polymorph框架由两个主要界面组成：

> Polymorph：它由一个命令控制台界面组成。也是主界面，建议将其用于复杂的任务，例如修改复杂协议，修改字段中的类型或在无需规范的情况下修改协议。
>
> Phcli：它是Polymorph框架的命令行界面。建议用于修改简单协议或执行先前生成的模板等任务。

### 使用Polymorph主界面

参照：<https://github.com/shramos/polymorph/blob/master/doc/whitepaper/whitepaper_english.pdf>

## 使用Phcli

### 解析几乎任何网络协议

现在让我们看看Polymorph如何解析不同网络协议的字段，如果我们想要实时修改这些字段，那么引用它们将会很有用。你可以尝试任何想到的协议。

HTTP协议，仅显示HTTP层和属于它的字段。

    
    
    # phcli --protocol http --show-fields

显示完整的HTTP数据包及其所属的字段。

    
    
    # phcli --protocol http --show-packet

你还可以对网络数据包进行过滤，例如，你可以仅显示包含特定字符串或数字的数据包。

    
    
    # phcli -p dns --show-fields --in-pkt "phrack"
    
    
    # phcli -p icmp --show-packet --in-pkt "84" --type "int"

过滤也可以这样用：

    
    
    # phcli -p http --show-packet --in-pkt "phrack;GET;issues"
    
    
    # phcli -p icmp --show-packet --in-pkt "012345;84" --type "str;int"

你可以按协议包含的字段名称进行筛选，但要注意的是，此名称是Polymorph在分析网络数据包时提供的名称。

    
    
    # phcli -p icmp --show-packet --field "chksum"
    
    
    # phcli -p mqtt --show-packet --field "topic;msg"

### 实时修改网络数据包

知道了Polymorph中显示的要修改的网络数据包，我们将要实时修改它。让我们先从一些例子开始。上一节中介绍的所有过滤器也可以在此处应用。

该例子将通过在request_uri字段中插入值/issues/61/1.html来修改包含字符串/issues/40/1.html及GET的数据包。
因此，当用户访问<http://phrack.org/issues/40/1.html>时，浏览器将访问<http://phrack.org/issues/61/1.html>

    
    
    # phcli -p http --field "request_uri" --value "/issues/61/1.html" --in-pkt "/issues/40/1.html;GET"

如果我们处于机器和网关之间，则上一个命令会起作用。

    
    
    # phcli --spoof arp --target 192.168.1.20 --gateway 192.168.1.1 -p http -f "request_uri" -v "/issues/61/1.html" --in-pkt "/issues/40/1.html;GET"

或者也许用户想在localhost上尝试它，因为他只需要修改Polymorph默认建立的iptables规则。

    
    
    # phcli -p http -f "request_uri" -v "/issues/61/1.html" --in-pkt "/issues/40/1.html;GET" -ipt "iptables -A OUTPUT -j NFQUEUE --queue-num 1"

用户可能想要修改未被Polymorph解释为字段的网络分组的一组字节的情况。为此，你可以使用“切分”直接访问数据包字节。（如果在localhost中尝试，请记住添加iptables规则）

    
    
    # phcli -p icmp --bytes "50:55" --value "hello" --in-pkt "012345"
    
    
    # phcli -p icmp -b "\-6:\-1" --value "hello" --in-pkt "012345"
    
    
    # phcli -p tcp -b "\-54:\-20" -v '"><script>alert("hacked")</script>' --in-pkt "</html>"

### 实时添加复杂处理

在某些情况下，PHCLI选项可能不足以执行某个操作。为此，框架实现了条件函数的概念，条件函数是用Python编写的函数，它将在实时拦截的网络数据包。

条件函数具有以下格式：

    
    
    def precondition(packet):
    
        # Processing on the packet intercepted in real time
    
        return packet

举个简单的例子，我们将屏蔽我们拦截的数据包的原始字节。（如果在localhost中尝试，请记住添加iptables规则）

    
    
    def execution(packet):
    
        print(packet.get_payload())
    
        return None
    
    # phcli -p icmp --executions execution.py -v "None"

 ***参考来源：[kitsploit](https://www.kitploit.com/2018/08/polymorph-real-time-network-packet.html)，Covfefe编译，转载请注明来自FreeBuf.COM**

