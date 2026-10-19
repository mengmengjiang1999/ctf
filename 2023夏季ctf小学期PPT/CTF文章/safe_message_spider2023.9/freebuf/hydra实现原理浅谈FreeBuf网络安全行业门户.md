## 前言

弱口令和端口爆破是网络攻击中最简单也是最常见的漏洞利用方式，特别是在内网，许多攻防演练主要的攻击成果都是由弱口令打下来的，不得不让人高呼一句弱口令天下第一。

爆破端口和测试弱口令的工具有很多，这么多年用下来感觉还是hydra最好用，但是对于Hydra的实现原理一直只有个模糊的概念，最近正好学习了下hydra源码，抛砖引玉：

ps.本文仅讨论C语言实现的Hydra,主要实现代码：[https://github.com/vanhauser-thc/thc-hydra/blob/master/hydra.c](https://github.com/vanhauser-thc/thc-hydra/blob/master/hydra.c)

## 正文

hydra支持协议如下：

> "smb" "smbnt") "afp" "cisco" "cisco-enable" "cvs" "firebird" "ftp" "ftps"
> "http-get" "http-get-form" "http-head" "http-post-form" "http-proxy" "http-> proxy-urlenum" "icq" "imap" "irc" "ldap2" "ldap3" "ldap3-crammd5"
> "ldap3-digestmd5" "mssql" "mysql" "ncp" "nntp" "oracle" "oracle-listener"
> "oracle-sid" "pcanywhere" "pcnfs" "pop3" "postgres" "rdp" "rexec" "rlogin"
> "rsh" "sapr3" "sip" "smtp" "smtp-enum" "snmp" "socks5" "ssh" "svn"
> "teamspeak" "telnet" "vmauthd" "vnc" "xmpp"

![](https://image.3001.net/images/20210802/1627873794_61076202b1146e91cf3e6.png!small)

在21行开始的源码中写的比较详细了

![](https://image.3001.net/images/20210802/1627873897_61076269073a9b0016b39.png!small)

96行开始定义各个协议爆破时所需的参数，主要是用Ifdef的条件编译，同时注释中也贴心的写明了，需要新加服务/协议请在此处定义

![](https://image.3001.net/images/20210802/1627873948_6107629c403efee65d72f.png!small)

481行开始主要是对使用help命令的输出

![](https://image.3001.net/images/20210802/1627874028_610762ec08422dca868cb.png!small)

1231行开始主要是和服务之间进行具体通信的过程

对某个服务进行密码破解时，是使用fork进程，并且创建了两个互相通信的套接字，

Socketpair函数是创建一对相互连接的套接字，用于本机内的进程通信。

在子进行中开启密码破解服务，父进程中进行数据的接收处理。

![](https://image.3001.net/images/20210802/1627874124_6107634c31d2d605393b4.png!small)

1507行开始hydra_send_next_pair函数

在子进程中获取用户名和密码也是通过套接字进行数据的获取。

由于不只是一个进程，会存在多个父子程同时处理，父子进程在用户名密码这块的处理使用的是一个数组

即从套接字中获取一对用户名和密码存储在pair数组中。

![](https://image.3001.net/images/20210802/1627874483_610764b31b1a6cd87438e.png!small)

一个个从数组中提取用户名和密码的过程![](https://image.3001.net/images/20210802/1627874644_610765545ea9ac583bc87.png!small)

到1903处共计6处返回hydra_send_next_pair，在不同情况下获取下一组存储在pair中的用户名和密码

![](https://image.3001.net/images/20210802/1627874672_610765707df42a1ccb02c.png!small)

然后是主函数的逻辑，破解密码首先判断获取字符为什么服务

![](https://image.3001.net/images/20210802/1627874700_6107658c0b9862e3c6672.png!small)

是否使用ssl的检测

![](https://image.3001.net/images/20210802/1627874751_610765bf09f6c1ec64082.png!small)

对不同服务类型置为i=1或2

![](https://image.3001.net/images/20210802/1627874781_610765ddb56b010a0cb8e.png!small)

3001处判断加密所用算法，置数为J进行记录

![](https://image.3001.net/images/20210802/1627874809_610765f9d6e05c8e2a9b0.png!small)

之后根据i,j的情况进行不同的处理和输出

![](https://image.3001.net/images/20210802/1627874841_61076619c82170ceaac2f.png!small)

对服务的ip和port进行tcp连接，对不同的服务进行不同的处理，如

![](https://image.3001.net/images/20210802/1627874871_6107663716215d29b16e6.png!small)

![](https://image.3001.net/images/20210802/1627874895_6107664fd71b30ae2f5af.png!small)

postgres和mysql这类有现成api的服务。直接使用api进行连接。成功时代表用户名密码正确，失败代表不正确。

![](https://image.3001.net/images/20210802/1627874926_6107666ec8d617fcc1d4c.png!small)

对于telnet、ftp这类的服务。使用的是数据交换的方式，将用户名密码封装为特定格式数据通过之前的套接字进行发送，然后接收返回信息。根据返回信息进行结果的判断。

![](https://image.3001.net/images/20210802/1627882261_6107831582377b1ba78c5.png!small)

判断服务是否需要导入用户名密码或者只需要用户名

![](https://image.3001.net/images/20210802/1627882360_610783782ec712d444386.png!small)

3894行处hydra对Ipv6/v4的支持和实现

![](https://image.3001.net/images/20210802/1627882394_6107839af38dcae12055b.png!small)

4045行处父进程对数据进行接受处理，依据不同case返回结果

![](https://image.3001.net/images/20210802/1627882616_61078478bd85da9846313.png!small)

最后就是输出环节，目前支持模式：

text - 普通文本。

jsonv1 - 1.x版本使用的JSON数据格式（见下）。

json - 最后一个版本使用的JSON数据格式，当前最后一个版本就是1.x。

2400处为判断用户需要什么输出格式

![](https://image.3001.net/images/20210802/1627882652_6107849c30bc3aa45ceb0.png!small)![](https://image.3001.net/images/20210802/1627882669_610784adccbcb583fd9e0.png!small)

![](https://image.3001.net/images/20210802/1627882696_610784c804c6bf917e39a.png!small)

具体输出JSONV1的代码

![](https://image.3001.net/images/20210802/1627882732_610784ec09d4d14e3474b.png!small)

4254行处对任务进行时间，剩余时间等的输出

![](https://image.3001.net/images/20210802/1627882753_61078501926d4cbd661bc.png!small)

另外值得一提的是hydra的会话存储

当hydra终止后，可能是因为Control-C，进程被杀死，或者崩溃，它会留下一个 “hydra.restore”
文件，这个文件包含了所有的恢复会话所需的必要信息。这个会话文件每隔5分钟写一次。

注意：hydra.restore文件不能复制到不同的平台下（例如：在不同的字符编码的平台间复制，或者不同的操作系统）。

## 后记

很久不接触C语言，读的有些吃力。在自己思考实现弱口令端口爆破的时候，虽然思路设计比较简单，但具体实现的细节，包括多线程调用，不同服务实现，以及如何提高效率，都是有很多难点。之所以hydra可以说是爆破第一工具，也是因为它代码实现这个功能的卓越性吧。同时在此处也再次体现了C实现底层通信的效率，是平常使用python不能比的。路漫漫其修远兮，吾将上下而求索。

