![](https://image.3001.net/images/20200203/1580731809_5e380da129e74.jpg!small)

**MassDNS是一款功能强大的高性能DNS
stub解析工具，它可以帮助研究人员解析数百万甚至上亿个域名。在没有特殊配置的情况下，MassDNS可以利用公共可用的解析器每秒钟解析超过350000个域名。**

##  项目编译

首先，使用下列命令将MassDNS源码克隆至本地目录中：

    
    
    git clone https://github.com/blechschmidt/massdns.git

使用cd命令切换到本地项目目录中：

    
    
    cd massdns

接下来，运行"make"命令构建源码。

如果你使用的不是Linux操作系统，那么则需要运行下列命令：

    
    
    make nolinux

在Windows平台下，你还需要安装Cygwin包、gcc-core、git和make。

##  工具使用

    
    
    Usage: ./bin/massdns [options] [domainlist]
    
          -b  --bindto           Bind to IP address and port. (Default: 0.0.0.0:0)
    
              --busy-poll        Use busy-wait polling instead of epoll.
    
          -c  --resolve-count    Number of resolves for a name before giving up. (Default: 50)
    
              --drop-group       Group to drop privileges to when running as root. (Default: nogroup)
    
              --drop-user        User to drop privileges to when running as root. (Default: nobody)
    
              --flush            Flush the output file whenever a response was received.
    
          -h  --help             Show this help.
    
          -i  --interval         Interval in milliseconds to wait between multiple resolves of the same
    
                                 domain. (Default: 500)
    
          -l  --error-log        Error log file path. (Default: /dev/stderr)
    
              --norecurse        Use non-recursive queries. Useful for DNS cache snooping.
    
          -o  --output           Flags for output formatting.
    
              --predictable      Use resolvers incrementally. Useful for resolver tests.
    
              --processes        Number of processes to be used for resolving. (Default: 1)
    
          -q  --quiet            Quiet mode.
    
              --rcvbuf           Size of the receive buffer in bytes.
    
              --retry            Unacceptable DNS response codes. (Default: REFUSED)
    
          -r  --resolvers        Text file containing DNS resolvers.
    
              --root             Do not drop privileges when running as root. Not recommended.
    
          -s  --hashmap-size     Number of concurrent lookups. (Default: 10000)
    
              --sndbuf           Size of the send buffer in bytes.
    
              --sticky           Do not switch the resolver when retrying.
    
              --socket-count     Socket count per process. (Default: 1)
    
          -t  --type             Record type to be resolved. (Default: A)
    
              --verify-ip        Verify IP addresses of incoming replies.
    
          -w  --outfile          Write to the specified output file instead of standard output.
    
        Output flags:
    
          S - simple text output
    
          F - full text output
    
          B - binary output
    
          J - ndjson output

如果你需要查看更详细的操作选项以及帮助手册（尤其是输出格式），你可以使用“--help”命令。

##  工具使用样例

解析目标域名（位于lists的resolvers.txt中）的AAAA记录，并将结果存储至result.txt中：

    
    
    $ ./bin/massdns -r lists/resolvers.txt -t AAAA domains.txt > results.txt

或者运行下列命令：

    
    
    $ ./bin/massdns -r lists/resolvers.txt -t AAAA -w results.txt domains.txt

样本输出

默认配置下，MassDNS将会输出响应数据包，格式为文本格式，输出样例如下：

    
    
    ;; Server: 77.41.229.2:53
    
        ;; Size: 93
    
        ;; Unix time: 1513458347
    
        ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 51298
    
        ;; flags: qr rd ra ; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 0
    
        ;; QUESTION SECTION:
    
        example.com. IN A
    
        ;; ANSWER SECTION:
    
        example.com. 45929 IN A 93.184.216.34
    
        ;; AUTHORITY SECTION:
    
        example.com. 24852 IN NS b.iana-servers.net.
    
        example.com. 24852 IN NS a.iana-servers.net.
    
        输出结果包含了解析的IP地址，可以帮助我们轻松对输出结果进行过滤。

##  数据解析

代码库中包含了一个名为resolvers.txt的文件，其中包含了一套有[subbrute项目](https://github.com/TheRook/subbrute)提供的已过滤的解析器子集。请注意，MassDNS的使用可能会提升系统/网络负载，因为需要加载大量解析器，具体将取决于你的ISP。

MassDNS的DNS解析实现目前还不完整，只支持最常见的一些记录类型。欢迎您通过代码贡献来帮助改变这种状况。

###  PTR记录

MassDNS包含了一个Python脚本，允许我们解析所有的IPv4 PTR记录：

    
    
    $ ./scripts/ptr.py | ./bin/massdns -r lists/resolvers.txt -t PTR -w ptr.txt

请注意，in-addr.arpa中的标签会被反转。为了解析域名为1.2.3.4的地址，MassDNS将需要以“4.3.2.1.in-addr.arpa”的方式来作为输入查询名称。此时，Python脚本并不会按升序解析记录，这样可以避免在IP v4子网的域名服务器上突然出现的负载激增。

###  网络侦察&爆破子域名

注意：请不要随意使用该工具，适当调整-s参数以避免给权威域名服务器造成负载压力。

跟[subbrute](https://github.com/TheRook/subbrute)类似，MassDNS允许我们使用subbrute.py脚本来对子域名进行爆破枚举：

    
    
    $ ./scripts/subbrute.py lists/names.txt example.com | ./bin/massdns -r lists/resolvers.txt -t A -o S -w results.txt

作为一种额外的网络侦察手段，ct.py脚本可以从[crt.sh](https://crt.sh/)中抓取数据，并从证书透明日志中提取子域名：

    
    
    $ ./scripts/ct.py example.com | ./bin/massdns -r lists/resolvers.txt -t A -o S -w results.txt

###  工具运行截图

![](https://image.3001.net/images/20200203/1580731874_5e380de2d27a6.png!small)

###  安全性

MassDNS的运行不需要Root权限，
我们建议用户以非特权用户的身份运行MassDNS。除此之外，我们不建议大家使用“--root”参数来运行。另外，除了Master以外的其他分支不适用于生产环境。

##  项目地址

> MassDNS：【[GitHub传送门](https://github.com/blechschmidt/massdns)】

 ***
参考来源：[blechschmidt](https://github.com/blechschmidt/massdns)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

