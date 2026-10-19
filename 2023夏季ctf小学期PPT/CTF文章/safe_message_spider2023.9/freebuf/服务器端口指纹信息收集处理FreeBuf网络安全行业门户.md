**0x01 概述**  

日常服务器端口扫描监控，是一个比较日常的工作。我们通过脚本对大批量的内部服务器进行端口监控检查。我们要监控服务器的端口一种方式是安装agent，当服务器新开端口时会主动把消息发给中心服务，这种场景需要针对不同的系统环境，部署agent，服务器系统平台复杂，实现起来困难。
而采用扫描的形式，无论服务器是freebsd、solaris、还是centos都可以收集端口信息。针对日常的扫描工作，产生了一个构思，我们能不能增量动态的分析，没天服务器端口的变化动态，分析发现一些问题。

##  **0x02 指纹处理流程**

![1.png](https://image.3001.net/images/20180416/15238709822267.png!small)  

服务器端口的指纹收集处理的流程比较简单：1.指纹采集。 2.指纹存储。 3.指纹比较。 4.指纹预警。

##  **0x03 服务部署结构**

  
![2.png](https://image.3001.net/images/20180416/15238709953028.png!small)  

系统部署，一个控制终端，调度扫描任务，将扫描的端口信息存放到数据库，数据库的控制系统操作更细致。如果采用文件形式存储算法更简单一些。

##  **0x04 正常指纹数据结构**

![3.png](https://image.3001.net/images/20180416/15238710045587.png!small)  

最基本的服务器端口指纹数据结构，就是这种线性的字符串，比如：192.168.0.3的机器开放了443,80,22,53,3306这些端口，构成这组指纹数据形式就是，
192.168.0.3:443,80,22,53,3306，我们把这组数据理解为一台服务器的假定正常的指纹组合。我们把初次扫描的结果作为基础指纹数据。

##  **0x05 异常指纹数据结构**

![4.png](https://image.3001.net/images/20180416/15238710131842.png!small)  

在基本指纹数据库构建后，我们日常增量扫描时，如果发现新增端口，我们要再次确认预警。在增量扫描时192.168.0.7新开了8118端口。192.158.0.9新开端口8116端口。

##  **0x06 异常指纹数据序列化**

![5.png](https://image.3001.net/images/20180416/15238710242970.png!small)  

我们把一个IP的端口开放信息，采用二维表的形式存储，也可以采用字符串序列化的方式存储，为了说明简单，我们采用字符串的形式，进行说明。

##  **0x07 指纹比较匹配**

![6.png](https://image.3001.net/images/20180416/15238710336384.png!small)  

我们通过指纹字符串差分diff的方式算出新增端口，针对简单的字符串比较增量端口开放数据。

##  **0x08 伪代码逻辑**

![7.png](https://image.3001.net/images/20180416/15238710475400.png!small)  

处理方法的逻辑比较简单，操作nmap的语言也有很多，干脆就用伪代码表达一下处理逻辑，省去流程图了。主要说明处理逻辑，具体用什么语言实现都行。不过其中使用syslog发送预警的代码比较通用。

> import socket
>
> class Facility:
>
> "Syslog facilities"
>
> KERN, USER, MAIL, DAEMON, AUTH, SYSLOG, \
>
> LPR, NEWS, UUCP, CRON, AUTHPRIV, FTP = range(12)
>
> LOCAL0, LOCAL1, LOCAL2, LOCAL3, \
>
> LOCAL4, LOCAL5, LOCAL6, LOCAL7 = range(16, 24)
>
> class Level:
>
> "Syslog levels"
>
> EMERG, ALERT, CRIT, ERR, \
>
> WARNING, NOTICE, INFO, DEBUG = range(8)
>
> class Syslog:
>
> """A syslog client that logs to a remote server.
>
> """
>
> def __init__(self,
>
> host="localhost",
>
> port=8000,
>
> facility=Facility.DAEMON):
>
> self.host = host
>
> self.port = port
>
> self.facility = facility
>
> self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
>
> def send(self, message, level):
>
> "Send a syslog message to remote host using UDP."
>
> data = "<%d>%s" % (level + self.facility*8, message)
>
> self.socket.sendto(data, (self.host, self.port))
>
> def warn(self, message):
>
> "Send a syslog warning message."
>
> self.send(message, Level.WARNING)
>
> def notice(self, message):
>
> "Send a syslog notice message."
>
> self.send(message, Level.NOTICE)
>
> def error(self, message):
>
> "Send a syslog error message."
>
> self.send(message, Level.ERR)
>
> import syslog_client
>
> log = syslog_client.Syslog("192.168.0.168")
>
> log.send("finger print", syslog_client.Level.WARNING)

##  **0x09 异常指纹的可视化**

![8.png](https://image.3001.net/images/20180416/15238710618682.png!small)  

如果系统只是输出字符串形式的数据，可视化效果不够理想，所以构想出用细胞基因的方式，画出top10的IP异常开放端口的可视化图，通过线条的连接，通过图的方式发现问题。比如，如果某个子网里的服务器，同时都开了一个陌生的端口，我们通过图的形式就可以发现。

