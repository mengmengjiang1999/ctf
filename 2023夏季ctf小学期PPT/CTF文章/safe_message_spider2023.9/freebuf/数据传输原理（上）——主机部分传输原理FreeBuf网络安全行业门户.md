## 0、前言

本主题主要讲述计算机网络世界中数据传送的原理，一共分为（上）（下）篇文章；  
（上）主要描述主机部分传输原理；  
（下）主要描述网络设备部分传输原理。  
![image.png](https://image.3001.net/images/20211218/1639806422_61bd75d6aa736207a8be7.png!small)

主机部分传输原理内容主要涉及以下知识点：

  1. 应用层协议，如dns/http等

  2. 表示层/会话层的socket

  3. 传输层协议，如tcp/udp

  4. 网络层的IP协议及其路由选择等

  5. 链路层的ARP、网卡驱动程序等

  6. 物理层的硬件设备网卡、网线等

![image.png](https://image.3001.net/images/20211218/1639806449_61bd75f1c2017a5e5ab84.png!small)

下面我们就从应用层开始进行描述。

## 1、应用层

应用层协议(application layer
protocol)定义了运行在不同端系统上的应用程序进程如何相互传递报文。下面以DNS、HTTP、HTTPS、WebSocket为例进行说明：

### 1.1 DNS

域名系统（Domain Name
System，缩写：DNS）是互联网的一项服务。它作为将域名和IP地址相互映射的一个分布式数据库，能够使人更方便地访问互联网。DNS使用TCP和UDP端口53。当前，对于每一级域名长度的限制是63个字符，域名总长度则不能超过253个字符。DNS协议是用来将域名转换为IP地址（也可以将IP地址转换为相应的域名地址）。  
其工作流程如下（以查询www.test.com为例）：

  1. 本地PC会先搜索浏览器缓存是否有该域名的记录，没有则查询下本地hosts文件是否有记录

  2. 本地缓存和hosts查询不到记录，则向自己配置的首选DNS服务器发起请求，要求首选DNS服务器返回域名对应的IP地址

  3. 首选DNS服务器接收到该请求后，首先会向.根域DNS服务器询问管理com域名服务器的IP

  4. 拿到管理com域名的DNS服务器IP后首选DNS服务器则再向管理com域名服务器询问管理test.com的域名的服务器IP

  5. 拿到管理test.com的域名的服务器IP后，则再次发起询问，询问www.test.com的服务器IP

  6. 至此，首选DNS拿到了www.test.com对应的IP地址，则返回给本地PC

  7. PC拿到www.test.com的IP地址后，就可以发起访问请求了。

![image.png](https://image.3001.net/images/20211218/1639806507_61bd762b482af0b55f779.png!small)

### 1.2 HTTP

HTTP默认为无状态连接，即通过TCP三次握手建立连接后，客户端使用请求报文向服务器请求内容，而服务端使用响应报文回应客户端的请求后，则使用TCP四次挥手断开释放了连接。  
下一次客户端再请求，服务器将会当成一个全新的请求来处理。  
其工作过程如下：  
![image.png](https://image.3001.net/images/20211218/1639806537_61bd7649ad508b69097ab.png!small)

数据包交互如下：  
![image.png](https://image.3001.net/images/20211218/1639806583_61bd7677cb859cf7a8963.png!small)

### 1.3 HTTPS

因为HTTP之间传输数据是明文的，这样子如果数据流被劫持到，那么将造成严重的数据泄露，所以出现了HTTPS协议，HTTPS协议是在HTTP的基础上增加了加密协议SSL。  
其工作过程如下：

  1. TCP三次握手后建立了连接

  2. 连接建立后马上使用SSL机制在连接隧道上，用非对称加密技术协商出一个对称加密密钥

  3. 然后利用这个对称加密密钥，客户端和服务器再进行请求和响应，这样子真正有价值的业务数据HTTP数据在整个交互过程中就都是加密的了。

![image.png](https://image.3001.net/images/20211218/1639806653_61bd76bde1552800387bf.png!small)

### 1.4 WebSocket

http机制只能由客户端主动发起请求，然后服务端再进行响应，无法服务端主动推送数据给客户端，为了解决这个问题，websocket就出现了。  
websocket的工作过程：

  1. TCP三次握手建立连接

  2. 客户端使用http协议发送一个升级到websocket协议的请求给服务端

  3. 服务端接收到后，确认可以升级到websocket

  4. 此后，客户端和服务器的交互均使用websocket协议，也就是服务端可以主动发送数据给客户端了

![image.png](https://image.3001.net/images/20211218/1639806688_61bd76e037256b395be72.png!small)

客户端发送的HTTP升级报文格式如下：  
![image.png](https://image.3001.net/images/20211218/1639806718_61bd76fea66b59b494bed.png!small)

服务端响应的HTTP报文如下：  
![image.png](https://image.3001.net/images/20211218/1639806742_61bd77162c50a471e1b9e.png!small)

> 当然了，websocket如果需要加密通信，同样是在TCP三次握手建立连接后，使用SSL协议进行加密。

## 2、Socket

Socket是应用层和传输层之间的接口。  
![image.png](https://image.3001.net/images/20211218/1639806775_61bd7737e95164e87972d.png!small)

### 2.1 Socket的工作过程

![image.png](https://image.3001.net/images/20211218/1639806802_61bd775267ea5b416a082.png!small)

### 2.2 Socket C示例代码

服务端:

    
    
    #include <stdio.h>
    #include <string.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <arpa/inet.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    
    int main(){
        //创建套接字
        int serv_sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    
        //将套接字和IP、端口绑定
        struct sockaddr_in serv_addr;
        memset(&serv_addr, 0, sizeof(serv_addr));  //每个字节都用0填充
        serv_addr.sin_family = AF_INET;  //使用IPv4地址
        serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");  //具体的IP地址
        serv_addr.sin_port = htons(1234);  //端口
        bind(serv_sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr));
    
        //进入监听状态，等待用户发起请求
        listen(serv_sock, 20);
    
        //接收客户端请求
        struct sockaddr_in clnt_addr;
        socklen_t clnt_addr_size = sizeof(clnt_addr);
        int clnt_sock = accept(serv_sock, (struct sockaddr*)&clnt_addr, &clnt_addr_size);
    
        //向客户端发送数据
        char str[] = "http://c.biancheng.net/socket/";
        write(clnt_sock, str, sizeof(str));
    
        //关闭套接字
        close(clnt_sock);
        close(serv_sock);
    
        return 0;
    }
    

客户端

    
    
    #include <stdio.h>
    #include <string.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <arpa/inet.h>
    #include <sys/socket.h>
    
    int main(){
        //创建套接字
        int sock = socket(AF_INET, SOCK_STREAM, 0);
    
        //向服务器（特定的IP和端口）发起请求
        struct sockaddr_in serv_addr;
        memset(&serv_addr, 0, sizeof(serv_addr));  //每个字节都用0填充
        serv_addr.sin_family = AF_INET;  //使用IPv4地址
        serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");  //具体的IP地址
        serv_addr.sin_port = htons(1234);  //端口
        connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr));
    
        //读取服务器传回的数据
        char buffer[40];
        read(sock, buffer, sizeof(buffer)-1);
    
        printf("Message form server: %s\n", buffer);
    
        //关闭套接字
        close(sock);
    
        return 0;
    }
    

## 3、传输层

传输层的主要作用就是提供应用进程间端到端的通信,也可以说是端口服务之间的通信。

![image.png](https://image.3001.net/images/20211218/1639806912_61bd77c04b61bf17f69a0.png!small)

### 3.1 TCP和UDP

TCP和UDP最主要的区别就是TCP是面向连接的，而UDP则是无连接的，TCP因为面向连接的特性，所以可以保障数据的传输是可靠的，对数据传输中出现的各种问题，也可以采取对应的机制进行控制，而UDP因为其无连接的特性，数据包发送出去后就不管了，至于数据包是否正确到达则没有对应的控制机制，也因为UDP无需对发送出去的数据包进行控制和管理，比起TCP少了许多开销。  
![image.png](https://image.3001.net/images/20211218/1639806943_61bd77df65c0039db450e.png!small)

### 3.2 端口

TCP、UDP端口有什么用呢？  
我们知道，一台拥有IP地址的主机可以提供许多服务，比如Web服务、FTP服务、SMTP服务等，这些服务完全可以通过1个IP地址来实现。  
那么，主机是怎样区分不同的网络服务呢？显然不能只靠IP地址，因为IP 地址与网络服务的关系是一对多的关系。  
实际上是通过“IP地址+端口号”（套接字）来区分不同的服务的。  
![image.png](https://image.3001.net/images/20211218/1639806970_61bd77fab1aef3c9ae035.png!small)

### 3.3 TCP交互过程

![image.png](https://image.3001.net/images/20211218/1639807029_61bd7835006a89227b4f1.png!small)

### 3.4 TCP确认机制

TCP为传输的每个字节分配了一个序号Sequence Number ，并期望从接收端的TCP得到一个肯定的确认（ACK）。  
因为数据按块（TCP报文段）的形式传输，所有TCP报文段中的每一个数据字节的序列号被发送到目的主机。当报文无序到达时，接收端TCP使用序列号来重排TCP报文段，并删除重复发送的报文段。  
TCP的确认是对接收到的数据的最高序号的确认，并向发送端返回一个下次期望收到的第一个数据字节的序号。  
![image.png](https://image.3001.net/images/20211218/1639807057_61bd78517ce803f97fffb.png!small)

### 3.5 TCP重传机制

TCP重传主要分为两种，超时重传和快速重传。  
超时重传：若发送方在规定时间内没有收到接收方的确认信息，就要将未被确认的数据包重新发送。接收方如果收到一个有差错的报文，则丢弃此报文，并不向发送方发送确认信息。因此，TCP报文的重传机制是由设置的超时定时器（根据算法动态变化）来决定的，在定时的时间内没有收到确认信息，则进行重传。  
快速重传：TCP引入了一种叫Fast Retransmit
的算法，不以时间驱动，而以数据驱动重传。也就是说，如果包没有连续到达，就ack最后那个可能被丢了的包，如果发送方连续收到3次相同的ack，就重传。Fast
Retransmit的好处是不用等timeout了再重传。  
快速重传示意图：  
![image.png](https://image.3001.net/images/20211218/1639807083_61bd786bef1f2f88f69dc.png!small)

### 3.6 TCP流控机制

TCP要解决一个很大的事，那就是要在一个网络根据不同的情况来动态调整自己的发包的速度，小则让自己的连接更稳定，大则让整个网络更稳定。TCP必需要知道网络实际的数据处理带宽或是数据处理速度，这样才不会引起网络拥塞，导致丢包。所以，TCP引入了一些技术和设计来做网络流控。  
滑动窗口：  
TCP头里有一个字段叫Window，又叫Advertised-Window，这个字段是接收端告诉发送端自己还有多少缓冲区可以接收数据。于是发送端就可以根据这个接收端的处理能力来发送数据，而不会导致接收端处理不过来。  
TCP头里有一个字段叫Window，又叫Advertised-Window，这个字段是接收端告诉发送端自己还有多少缓冲区可以接收数据。于是发送端就可以根据这个接收端的处理能力来发送数据，而不会导致接收端处理不过来。

![image.png](https://image.3001.net/images/20211218/1639807112_61bd78883e63dfd4b9fab.png!small)

工作过程：  
![image.png](https://image.3001.net/images/20211218/1639807132_61bd789c37de0acf5d600.png!small)

### 3.7 TCP拥塞控制

TCP不是一个自私的协议，当拥塞发生的时候，要做自我牺牲。就像交通阻塞一样，每个车都应该把路让出来，而不要再去抢路了。关于拥塞控制的论文请参看《Congestion
Avoidance and Control》(PDF) 。拥塞控制主要是四个算法：1）慢启动，2）拥塞避免，3）拥塞发生，4）快速恢复。  
![image.png](https://image.3001.net/images/20211218/1639807160_61bd78b86f173a8061f0b.png!small)  
(3）快重传要求接收方在收到一个失序的报文段后就立即发出重复确认（为的是使发送方及早知道有报文段没有到达对方，可提高网络吞吐量约20%）而不要等到自己发送数据时捎带确认。快重传算法规定，发送方只要一连收到三个重复确认就应当立即重传对方尚未收到的报文段，而不必继续等待设置的重传计时器时间到期。如下图：  
![image.png](https://image.3001.net/images/20211218/1639807187_61bd78d3346695b0c08e1.png!small)

（4）快重传配合使用的还有快恢复算法，有以下两个要点：  
当发送方连续收到三个重复确认时，就执行“乘法减小”算法，把ssthresh门限减半（为了预防网络发生拥塞）。但是接下去并不执行慢开始算法，考虑到如果网络出现拥塞的话就不会收到好几个重复的确认，所以发送方现在认为网络可能没有出现拥塞。所以此时不执行慢开始算法，而是将cwnd设置为ssthresh减半后的值，然后执行拥塞避免算法，使cwnd缓慢增大。如下图：TCP
Reno版本是目前使用最广泛的版本。  
![image.png](https://image.3001.net/images/20211218/1639807211_61bd78eb1d9386c296da3.png!small)

### 3.8 TCP标志位

主机接受到不同的tcp包进入不同的tcp状态，并响应不同的tcp包。  
不同的标志位（或组合）代表不同的tcp数据包类型，也表示着不同的作用，如syn包、syn/ack包、ack包、ack/psh包、rst包、fin包等。  
![image.png](https://image.3001.net/images/20211218/1639807242_61bd790a70ed08f14870b.png!small)

### 3.9 TCP状态机

网络上的传输是没有连接的，包括TCP也是一样的。而TCP所谓的“连接”，其实只不过是在通讯的双方维护一个“连接状态”，让它看上去好像有连接一样。  
TCP整个状态的变化如下：  
![image.png](https://image.3001.net/images/20211218/1639807267_61bd792392001e49ac041.png!small)

## 4、网络层

网络层的主要功能为提供主机到主机的通信，即把数据包从一台机器搬运到另一台机器的过程。  
![image.png](https://image.3001.net/images/20211218/1639807289_61bd7939ef3e1ef7e6d00.png!small)

### 4.1 IP地址

![image.png](https://image.3001.net/images/20211218/1639807315_61bd79530a057204a2536.png!small)

### 4.2 IP地址分类

![image.png](https://image.3001.net/images/20211218/1639807339_61bd796be64e3a33fac85.png!small)

### 4.3 子网划分

主机地址和掩码地址进行二进制与运算，得到网络号。  
通信双方是否在同一网段就看网络号是否一样。  
![image.png](https://image.3001.net/images/20211218/1639807361_61bd7981bb50ab0e68fb3.png!small)

### 4.4 路由

![image.png](https://image.3001.net/images/20211218/1639807386_61bd799a9f5cc00b45431.png!small)

### 4.5 路由表

路由表即是数据包在网络传输过程中选路的依据。  
![image.png](https://image.3001.net/images/20211218/1639807411_61bd79b3a5b145296b0cc.png!small)

### 4.6 路由匹配

即确定路由是否按照一定规则进行转发的机制。  
![image.png](https://image.3001.net/images/20211218/1639807436_61bd79cc21a76fae9230d.png!small)

### 4.7 数据包发送/接收过程

![image.png](https://image.3001.net/images/20211218/1639807457_61bd79e1217d91a12e8df.png!small)

### 4.8 防火墙

![image.png](https://image.3001.net/images/20211218/1639807476_61bd79f4d46cdb1d09081.png!small)

![image.png](https://image.3001.net/images/20211218/1639807486_61bd79fea264a15c351e1.png!small)

![image.png](https://image.3001.net/images/20211218/1639807497_61bd7a09a910925c44ae7.png!small)

![image.png](https://image.3001.net/images/20211218/1639807511_61bd7a177d203d929844a.png!small)

## 5、物理层和数据链路层

数据链路层的主要功能是提供结点到结点的通信，就是一台机器到它下一台机器的物理链路间的通信。  
而物理层则规定则各种物理特性及规程。

![image.png](https://image.3001.net/images/20211218/1639807535_61bd7a2f92660e57b6f75.png!small)

![image.png](https://image.3001.net/images/20211218/1639807547_61bd7a3bc48f6104daef1.png!small)

### 5.1 ARP

在一个稳定的网络中，IP地址和MAC地址是成对出现的。如果一台计算机要和网络中另一外计算机通信，那么要配置这两台计算机的IP地址，MAC地址是网卡出厂时设定的，这样配置的IP地址就和MAC地址形成了一种对应关系。在数据通信时，IP地址负责表示计算机的网络层地址，网络层设备（如路由器）根据IP地址来进行操作；MAC地址负责表示计算机的数据链路层地址，数据链路层设备（如交换机）根据MAC地址来进行操作。IP和MAC地址这种映射关系由ARP（Address
Resolution Protocol，地址解析协议）协议完成。  
![image.png](https://image.3001.net/images/20211218/1639807569_61bd7a51de49349d5e3dc.png!small)

为什么要同时具备IP和MAC地址？

信息传递时候，需要知道的其实是两个地址：终点地址（Final destination address）、下一跳的地址（Next hop address）  
IP地址本质上是终点地址，它在跳过路由器（hop）的时候不会改变，而MAC地址则是下一跳的地址，每跳过一次路由器都会改变。这就是为什么还要用MAC地址的原因之一，它起到了记录下一跳的信息的作用。分层实现如果在IP包头（header）中增加了“下一跳IP地址”这个字段，在逻辑上来说，如果IP地址够用，交换机也支持根据IP地址转发（现在的二层交换机不支持这样做），其实MAC地址并不是必要的。但用MAC地址和IP地址两个地址，用于分别表示物理地址和逻辑地址是有好处的。这样分层可以使网络层与链路层的协议更灵活地使用，网络层不一定非要用IP协议，链路层也不一定非用以太网协议。  
另外，如果只有MAC，没有IP，则需要向全世界发送arp广播包以获取目的mac，网络带宽瞬间会饱和。

### 5.2 传输介质

数据在物理世界中传输的本质是电磁，所以传输介质不必是像网线一样的可见连接器物，还可以是像WI-FI、移动基站等能发送电磁信号等物体。

![image.png](https://image.3001.net/images/20211218/1639807602_61bd7a7225a8b70e8f99a.png!small)

## 6、总结与扩展

![image.png](https://image.3001.net/images/20211218/1639807782_61bd7b263b51ef21b5227.png!small)

