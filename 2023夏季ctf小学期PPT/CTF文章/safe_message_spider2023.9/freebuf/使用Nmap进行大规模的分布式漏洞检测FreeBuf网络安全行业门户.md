*** 本文作者：你会忘了我，本文属FreeBuf原创奖励计划，未经许可禁止转载**

## 0x01 介绍：

微软在2017年3月14日发布了严重的安全公告，公告显示，微软在4013389号补丁中修补了Microsoft
Windows的多个漏洞，其中最为严重的就是如果攻击者向 Windows SMBv1
服务器发送特殊设计的消息，那么漏洞可能允许远程执行代码。这个漏洞覆盖之广，导致microsoft专门为Microsoft Windows
XP系统专门颁布了修补补丁。也因为漏洞的影响力之广，微软将其安全更新的等级设置为“严重”。

而在一个月之后的4月14日，曾经以入侵了方程式组织（Equation
Group是一个被卡巴斯基实验室在一次对震网病毒分析的时候发现的尖端网络犯罪组织，卡巴斯基实验室的安全研究员将其称为世界上最尖端的网络攻击组织之一，方程式组织同震网（Stuxnet）和火焰（Flame）病毒的制造者紧密合作且在幕后操作并提供技术支持）而闻名的黑客组织影子经纪人在steemit.com上公开了一大批NSA（美国国家安全局）“方程式组织”
(Equation
Group)曾经使用过的一批极具破坏力的黑客工具，其中就包括了可以远程攻破全球约70%Windows机器的漏洞利用工具，也就是ms17-010的exp。一夜之间，全世界70%的windows服务器处在危险之中，国内使用windows服务器的高校、国企甚至政府机构都不能幸免。随后爆发的勒索病毒，对高校、国企、政府等行业都带来了巨大的损失。

## 0x02 nmap参数配置

nmap是一个采用GPL许可的开源扫描器，在最初的时候nmap只是一个网络扫描和嗅探工具包。2009年7月17日nmap发布了里程碑式的5.0版本。新的5.0版本因为支持了nse插件，使得nmap能够进行更复杂的软件版本检测，脆弱性测试和一些漏洞的利用。黑客和网络管理员可以通过nmap很方便的发现网络中存活的主机和主机开放的端口，利用指纹信息来判断端口绑定的服务的版本号。甚至利用nmap的nse脚本进行漏洞扫描操作。

但是nmap也有自己的缺陷，在笔者扫描大网段的时候常常牵涉到几千台主机，这个时候如果使用单个节点进行扫描，耗费的时间会相对较多。而nmap在扫描大量资源的时候会有卡死的情况发生。所以这篇文章主要探讨尝试结合nse插件和dnmap工具来用nmap进行一个分布式的漏洞检测。

在Kali Linux中，nmap的扫描脚本存储在/usr/share/nmap/scripts这个目录中

使用 lc -l | wc
-l命令可以看见在更新到目前最新的版本7.6.0之后，共有581个扫描脚本可以使用，当配合上nmap扫描探测能力比较快速的特点。结合上分布式的漏洞检测方式在对大规模的集群进行扫描时可以获得相对更快的扫描速度和准确率。

在大型的网络环境中，对数以万计的服务器进行扫描筛查一直是网络管理员所头疼的弊病nmap中的smb-vuln-ms17-010.nse脚本可以用来批量的检测网段中的windows主机是否存在Miscrosoft Windows ms17-010漏洞。

nmap参数的构造：

假设我们要扫描的网段为192.168.124.0/24，其中192.168.124.20-52是linux服务器，192.168.124.220-250是已知还未分配的IP。其余的都是windows主机和服务器。

因为我们已经知道了windows主机的IP范围，所以我们可以使用-Pn来取消nmap来使用ping来探测目标主机是否存活直接进行检测，也可以防止因为禁ping造成nmap以为主机未存活而跳过扫描。

> sS是半开放的TCP扫描，因为不进行完整的TCP连接所以扫描的速度会快一些
>
> T参数是指定nmap的扫描速度，一共有1-5档可以选择，速度越快也越容易被入侵检测设备发现

因为在扫描大范围地址段的时候有可能会在扫描某个IP的时候卡住，可以用--host-timeout来设定一个延时，在这里我选择一个IP延时10秒

我们还可以加上-n参数来取消nmap进行DNS反向解析来增加扫描的速度

加上这些参数，我们的nmap扫描语句就是下面这样：

    
    
    nmap -sS -Pn -n -p 445 -T4 192.168.124.0/24 --exclude 192.168.124.20-52 
    192.168.124.220-250 --script=smb-vuln-ms17-010.nse --host-timeout=10s  
    

## 0x03 dnmap参数配置

dnmap是一个用python写的进行分布式扫描的nmap扫描框架，我们可以用dnmap来通过多个终端发起一个大规模的扫描，dnmap采用C/S结构。

![](https://image.3001.net/images/20180404/15228296194104.png!small)

用户在服务器端设定好nmap执行的命令，dnmap会自动的分配给客户端进行扫描，并将扫描结果提交给服务器。

dnmap有两个可执行文件，分别是dnmap_client何dnmap_server。在进行一个分布式namp扫描之前，我们可以用dnmap_server来生成一个dnmap的服务端，然后在其他机器用dnmap_client进行连接。然后就能进行分布式的nmap扫描了。

这里我们可以使用Kali Linux，自带有dnmap。也可以使用阿里云等云虚拟机等进行搭建

当然dnmap也可以在[sourceforge](http://dnmap.sourceforge.net/)上下载

为了保证dnmap服务端和客户端的连接安全，dnmap默认采用了TLS加密传输。TLS加密是SSL加密的升级版。SSL可以对通信双方身份进行认证和维护数据完整性，SSL是在socket上二次协商建立的安全通道。SSL刚开始是作为http的扩展，即https，后来因为应用广泛，目前SSL已经成为了一种单独的协议

dnmap中TLS连接的过程图：

![clipboard2.png](https://image.3001.net/images/20180404/15228296466116.png!small)

1 客户端向服务器发送一个Client Hello包，在Client Hello包中会包含Cipher
suite、客户端支持的加密算法、客户端随机生成的32字节的随机数，以及一个Session ID

> cipher suite是客户端支持的算法以下面的格式发送给服务器：非对称加密算法_对称加密算_Hash
>
> 客户端生成的32字节的随机数用来参与秘钥的创建
>
> session ID，默认为0，如果客户端和服务器有通信过session ID就会变化

2 服务器收到客户端发的Client Hello之后会向客户端返回服务器的Server
Hello，其中会包含服务器生成的32位的对称秘钥、服务器从客户端支持的加密协议栈中选择的加密协议的版本、cipher suite、压缩算法(可选)

> 服务器生成的32位的对称秘钥用来进行公私钥的创建
>
> 服务器接到客户端发送的session id之后会向客户端发送一个服务器指定的新的session id

3 服务器发完Server
Hello之后会继续向客户端发送服务器的公钥证书，因为证书是由证书机构颁发，通过证书机构的私钥签名。客户端收到服务器发送的证书之后通过浏览器中自带的大量证书机构的公钥来进行解密。如果解密成功说明证书是合法的

4
客户端会再次产生一个随机数，用上一步证书中服务器的公钥生成密文发给服务器。如果服务器能用私钥解密就说明建立成功，基于这三个随机数，客户端和服务端都各自独立算出master
key。后续的会话秘钥都是由这个master key来加密。后续就变成对称加密来节省服务器的CPU资源

5 客户端继续向服务器发送一个ChangeCipherSpec-Client包来表示客户端后续的通信将全部加密

6 服务端收到客户端的ChangeCipherSpec-Client包后会向客户端发送一个Finished-Server包，其中包含着刚才客户端和服务端发送的所有信息，如果客户端解密成功，则整个握手协商成功，否则整个握手协商就失败并断开连接

因为dnmap自带的用于TLS连接的pem文件证书太过久远，必须要重新生成一个pem证书客户端和服务器才能正常连接。

生成命令：

    
    
    openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout key.pem -out server.pem
    cat key.pem >> server.pem
    rm -rf key.pem  
    

![clipboard3.png](https://image.3001.net/images/20180404/15228297295989.png!small)

dnmap的参数：

dnmap_server(dnmap的服务端)：

> -f, 跟一个待会要执行的nmap命令的文件
>
> -p, 指定一个dnmap_clien连接的端口
>
> -L, 输出log文件的名字，默认是 /var/log/dnmap_server.conf.
>
> -l, Log输出的等级，默认是信息级别.
>
> -v, Verbose(输出的信息的等级模式)1-5，默认是1，等级是0时代表不输出.
>
> -t, 设置一个客户端离线重连等待的时长 -s, 对扫描输出的内容进行排序. 选择的关键字: Alias, #Commands, UpTime,
> RunCmdXMin, AvrCmdXMin, Status
>
> -P, 跟一个用于TLS连接的pem文件，默认是使用随服务器提供的server.pem

dnmap_client的参数：

选项:

> -s, 输入dnmap的服务器地址.
>
> -p, dnmap服务的端口号，默认是46001
>
> -a, [可选项]你的名字的别名，我们可以给予你一些帮助
>
> -d, Debuging.
>
> -m, 给nmap扫描最快的速度定一个阈值. 添加一个 --max-rate 参数.

## 0x04 例子

我们在作为服务端的主机中首先把待会叫执行的nmap命令保存成一个文件

在例子中我保存在execnmap.txt中

![clipboard4.png](https://image.3001.net/images/20180404/15228298393612.png!small)

然后我们在服务端执行dnmap_server -f execnmap.txt -p 4321 -t 60 -P server.pem

![clipboard5.png](https://image.3001.net/images/20180404/15228298568649.png!small)

在客户端执行 dnmap_client -s 10.0.2.15 -p 4321 -a slave1 就可以连接上服务器进行分布式扫描了

![clipboard6.png](https://image.3001.net/images/20180404/15228298772569.png!small)

下面是服务器检测到客户端的连接之后的信息：

![clipboard7.png](https://image.3001.net/images/20180404/15228298996364.png!small)

## 题外话

因为dnmap是使用python编写的，所以可以很方便得使用django等框架移植成B/S架构，方便使用和管理。有空的时候想基于dnmap和django或者flask写一个开源项目，有兴趣的小伙伴一起组队吗(求私信，大佬们求带)。先定个小目标，先挣他个1000个star

 *** 本文作者：你会忘了我，本文属FreeBuf原创奖励计划，未经许可禁止转载**

