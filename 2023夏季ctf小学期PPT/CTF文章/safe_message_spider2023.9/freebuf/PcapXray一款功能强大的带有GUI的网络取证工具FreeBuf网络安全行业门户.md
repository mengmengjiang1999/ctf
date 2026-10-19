## 前言

**网络取证工具通常是安全研究专家用来测试目标网络系统安全性的特殊工具，今天我们给大家介绍的正是这样的一种工具。该工具名叫PcapXray，它带有非常强大的GUI界面，并且能够帮助我们离线分析捕获到的数据包。**

![网络取证工具](https://image.3001.net/images/20181105/1541411629_5be0132d68164.png!small)

该工具不仅能够扫描出目标网络内的所有主机、网络通信流量、以高亮的形式标注重要流量和Tor流量，而且还能够识别和扫描出潜在的恶意流量。

 **该工具包含了以下组件：**

> 1\. 网络图表
>
> 2\. 设备/流量细节和分析
>
> 3\. 恶意流量识别
>
> 4\. Tor流量
>
> 5\. GUI-用户可使用GUI及相关参数选项来上传pcap文件

## 网络取证工具使用

该数据包捕捉工具可以直接从GitHub上获取，研究人员可以利用该工具所提供的信息进行目标初始调查。

项目地址：【[GitHub传送门](https://github.com/Srinivas11789/PcapXray)】

### 安装和使用命令

    
    
    git clone <https://github.com/Srinivas11789/PcapXray.git>
    
    cd PcapXray
    
    python Source/main.py

![网络取证工具使用](https://image.3001.net/images/20181105/1541411658_5be0134a613d3.png!small)

运行命令之后，会启动图形化的用户接口，并询问用户上传pcap文件。

![网络取证工具使用](https://image.3001.net/images/20181105/1541411669_5be01355800f0.png!small)

![网络取证工具使用](https://image.3001.net/images/20181105/1541411670_5be013561c9d3.png!small)

比如说，我们这里上传了一个跟Netflix钓鱼活动相关的pcap文件，在这款工具的帮助下，我们可以提取出Web流量、Tor流量、恶意流量和其他类型的流量。

分析的过程需要花掉一点时间，分析完成之后，我们将能够得到目标通信流量、设备和数据包的详细分析报告。

![网络取证工具使用](https://image.3001.net/images/20181105/1541411682_5be0136250170.png!small)

![网络取证工具使用](https://image.3001.net/images/20181105/1541411682_5be01362ccb7f.png!small)

![网络取证工具使用](https://image.3001.net/images/20181105/1541411683_5be0136344ba8.png!small)

分析提取出的目标URL地址为一个Netflix钓鱼页面。

![Netflix钓鱼页面](https://image.3001.net/images/20181105/1541411698_5be01372c517c.png!small)

![Netflix钓鱼页面](https://image.3001.net/images/20181105/1541411699_5be0137332904.png!small)

目标IP地址为98[.]209[.]70[.]101，不过在我们分析的时候这个IP地址已经无法成功解析了。

除此之外，该工具还包含了下列Python库：

    
    
    Scapy：爬取pcap文件中的数据包信息；
    
    Ipwhois：用于获取whois信息中的IP地址；
    
    Netaddr：Python网络编程库；
    
    Pillow：Python图形处理模块；
    
    Stem：一款与Tor网络进行交互的Python控制器；
    
    pyGraphviz：一个用于可视化查看数据包的Python接口；
    
    Networkx：Python复杂网络分析库；
    
    Matplotlib：一款Python 2D绘图库；

 *** 参考来源：[gbhackers](https://gbhackers.com/pcapxray-network-forensics-tool/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

