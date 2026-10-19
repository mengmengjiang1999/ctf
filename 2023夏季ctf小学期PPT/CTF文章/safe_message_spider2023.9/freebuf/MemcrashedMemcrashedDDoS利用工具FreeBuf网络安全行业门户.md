**Memcrashed是一款由Python编写的Memcached
DDoS攻击工具，允许你将伪造的UDP数据包发送至从[Shodan](https://www.darknet.org.uk/2014/06/shodan-internet-computer-search-engine/)获取的Memcached服务器列表。**

 **![Memcrashed-Memcached-DDoS-Exploit-Tool.png](https://image.3001.net/images/20180315/1521069261640.png!small)  
**

这与最近破纪录的[Memcached DDoS攻击](https://www.darknet.org.uk/2018/03/memcached-ddos-attacks-will-be-big-in-2018/)有关。据统计，在Shodan中有超过100,000个的易受攻击的Memcached服务器。

 **Memcached是什么？**

摘自百科：Memcached是一个高性能的分布式内存对象缓存系统，用于动态Web应用以减轻数据库负载。它通过在内存中缓存数据和对象来减少读取数据库的次数，从而提高动态、数据库驱动网站的速度。

 **安装**

你需要安装Python 3.x：

    
    
    apt-get install python3

你还需要安装Scapy和Shodan Python模块：

    
    
    pip install scapy
    
    
    pip install shodan

该工具还需要你拥有升级的Shodan API密钥。

你可以在这里下载Memcrashed：

[Memcrashed-DDoS-Exploit-master.zip](https://github.com/649/Memcrashed-DDoS-Exploit/archive/master.zip)

 ***参考来源：[darknet](https://www.darknet.org.uk/2018/03/memcrashed-memcached-ddos-exploit-tool/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

