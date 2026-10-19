![图片1.png](https://image.3001.net/images/20200418/1587213038_5e9af2eeb484a.png!small)

**Eavesarp是一款基于ARP请求分析的内部通信主机和过期网络地址配置的识别工具，它本质上一个网络侦察工具，它可以通过分析ARP请求来识别可能跟其他设备通信的主机，这种功能在LLMNR/NBN无法用于域名解析的情况下非常实用。**

## 工具下载

广大研究人员可以使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/arch4ngel/eavesarp.git

## 工具要求

当前版本的Eavesarp仅支持在Kali或其他基于Debian的Linux发行版操作系统上运行。

该工具要求Python 3.7环境和Scapy项目，安装好Python之后，可以运行下列命令来安装Scapy：

    
    
    python3.7 -m pip install -r requirements.txt

## 工具使用

### 捕捉ARP请求

注意事项：

> 1、Eavesarp要求使用root权限来从网络接口嗅探ARP数据包；
>
> 2、捕捉到的数据将自动输出并写入到本地磁盘中，导出文件名为eavesarp.db；

### 被动执行

Eavesarp工具最基础的使用/执行方法如下:

    
    
    sudo ./eavesarp.py capture -i eth1

该命令将会对Eavesarp进行初始化，并执行APR请求的捕捉、分析，然后将最终的处理结果输出给用户，最后将所有内容存储进数据库表中。我们可以使用--help命令来查看该工具的其他帮助选项以及非常规参数。需要注意的是，在此模式下运行时，如果尚未观察到来自目标的ARP请求时，stale列表示[UNCONFIRMED]。通过`-ar`参数启用APR解析后，可以判断给定的目标地址是否已过期。

    
    
     ___ ___ __  _____ ___ ___ ________
    
    / -_) _ `/ |/ / -_|_-</ _ `/ __/ _ \
    
    \__/\_,_/|___/\__/___/\_,_/_/ / .__/
    
    -----------------------------/ /---    
    [LISTEN CAREFULLY]          /_/
    
     
    
    Capture interface: eth1
    
    ARP resolution:    disabled
    
    DNS resolution:    disabled
    
    Requests analyzed: 65
    
     
    
    SNAC    Sender         Target            ARP#  Stale
    
    ------  -------------  --------------  ------  -------------    
            192.168.86.5   192.168.86.101      29  [UNCONFIRMED]
    
                           192.168.86.3         1
    
            192.168.86.3   192.168.86.37       25  [UNCONFIRMED]
    
                           192.168.86.38        7  [UNCONFIRMED]
    
                           192.168.86.5         1
    
                           192.168.86.99        1
    
            192.168.86.99  192.168.86.3         1

### 主动执行（ARP解析、DNS解析）

我们可以使用`-ar`和`-dr`这两个参数选项来启用ARP和DNS解析。请注意，这两个命令参数将会让工具以非被动模式执行，但优势就在于此时工具将返回DNS记录、MAC地址和以确定的SNAC状态。

    
    
    sudo ./eavesarp.py capture -i eth1 -ar -dr --blacklist 192.168.86.5

我们可以从下面的输出中清楚地看到有哪些发送方受到一个或多个SNAC以及地址的影响。最后一列数据表明是否存在潜在的中间人攻击威胁。Eavesarp可以检查给定发送方的PTR解析的FWD地址是否不同，如果不同，工具将会显示一个标识符来标记目标转移到了新的FWD地址。

    
    
     ___ ___ __  _____ ___ ___ ________
    
    / -_) _ `/ |/ / -_|_-</ _ `/ __/ _ \
    
    \__/\_,_/|___/\__/___/\_,_/_/ / .__/
    
    -----------------------------/ /---    
    [LISTEN CAREFULLY]          /_/
    
     
    
    Capture interface: eth1
    
    ARP resolution:    enabled
    
    DNS resolution:    enabled
    
    Requests analyzed: 55
    
     
    
    SNAC    Sender         Target            ARP#  Stale    Sender PTR      Target PTR        MITM
    
    ------  -------------  --------------  ------  -------  --------------  ----------------  ---------------------------------------------    
    True    192.168.86.2   192.168.86.101      21  True     iron.aa.local.  syslog.aa.local.  T-IP:192.168.86.101 != PTR-FWD:192.168.86.102
    
    True    192.168.86.3   192.168.86.38       17  True     crux.aa.local.
    
                           192.168.86.37       15  True
    
                           192.168.86.99        1                           w10.aa.local.
    
            192.168.86.99  192.168.86.3         1           w10.aa.local.   crux.aa.local.

### 分析PCAP文件和SQLite数据库（由Eavesarp生成）

Eavesarp可以对SQLite数据库和PCAP文件进行分析，工具将会把提取出的值输出至一个新的数据库文件中以供后续分析。你可以使用--help选项来查看更多帮助信息，下面给出的是基础使用方式：

    
    
    sudo ./eavesarp.py analyze -sfs eavesarp.db  -cp disable --blacklist 192.168.86.5 --csv-output-file eavesarp_analysis.db 
    
    SNAC    Sender         Target            ARP#  Stale    Sender PTR      Target PTR        MITM
    
    ------  -------------  --------------  ------  -------  --------------  ----------------  ---------------------------------------------    
    True    192.168.86.2   192.168.86.101      21  True     iron.aa.local.  syslog.aa.local.  T-IP:192.168.86.101 != PTR-FWD:192.168.86.102
    
    True    192.168.86.3   192.168.86.38       17  True     crux.aa.local.
    
                           192.168.86.37       15  True
    
                           192.168.86.99        1                           w10.aa.local.
    
            192.168.86.99  192.168.86.3         1           w10.aa.local.   crux.aa.local.
    
    - Writing csv output to eavesarp_analysis.db

输出的CSV格式文件如下所示：

    
    
    arp_count,sender,sender_mac,target,target_mac,stale,sender_ptr,target_ptr,target_forward,mitm_op,snac
    
    21,192.168.86.2,74:d4:35:1a:b5:fb,192.168.86.101,[STALE TARGET],True,iron.aa.local.,syslog.aa.local.,192.168.86.102,T-IP:192.168.86.101 != PTR-FWD:192.168.86.102,True
    
    17,192.168.86.3,b8:27:eb:a9:5c:8f,192.168.86.38,[STALE TARGET],True,crux.aa.local.,,,False,True
    
    15,192.168.86.3,b8:27:eb:a9:5c:8f,192.168.86.37,[STALE TARGET],True,crux.aa.local.,,,False,True
    
    1,192.168.86.99,08:00:27:22:49:c5,192.168.86.3,b8:27:eb:a9:5c:8f,False,w10.aa.local.,crux.aa.local.,192.168.86.3,False,False
    
    1,192.168.86.3,b8:27:eb:a9:5c:8f,192.168.86.99,08:00:27:22:49:c5,False,crux.aa.local.,w10.aa.local.,192.168.86.99,False,True

### 项目地址

Eavesarp：【[ _GitHub传送门_](https://github.com/arch4ngel/eavesarp)】

 ***参考来源：[
_arch4ngel_](https://github.com/arch4ngel/eavesarp)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

