![](https://image.3001.net/images/20200310/1583850081_5e67a26152b8b.png!small)

##  HoneyBot

**HoneyBot是一款功能强大的网络流量捕捉、上传和分析框架，本质上HoneyBot可以实现基于云的PCAP分析，由PacketTotal.com驱动。**

HoneyBot其实是由一系列脚本与代码库组成的，并且可以给广大研究人员提供网络数据包的捕捉与分析功能。当前版本的代码库提供了下列三个脚本：

> 1、capture-and-analyze.py - 对目标接口进行一段时间的数据捕捉，并上传捕捉到的数据以供后续分析。
>
> 2、upload-and-analyze.py - 将捕捉到的数据包上传至PacketTotal.com进行后续分析
>
> 3、trigger-and-analyze.py - 监听未知连接，并在建立连接时开始数据捕捉，完成捕捉后会自动上传并分析。

###  注意事项

使用该工具集所捕捉到的任何流量或数据包都将被上传并完全公开可获取。

##  限制条件

> 1、目前HoneyBot仅支持.pcap和.pcapng文件；
>
> 2、最大支持的数据包大小为6MB；

如需了解更多关于HoneyBot的信息，请参考[PacketTotal.com](https://packettotal.com/about.html)。

##  工具使用场景

> 1、设置蜜罐环境，并直接将捕捉到的网络流量上传至PacketTotal.com以供分析；
>
> 2、分析个人的恶意PCAP库；
>
> 3、一次性判断数百个数据包是否具有恶意性；
>
> 4、自动分析/共享蜜罐环境捕捉到的数据包；
>
> 5、自动化恶意软件分析/分类；

![](https://image.3001.net/images/20200310/1583850126_5e67a28ea1ebf.png!small)

##  依赖组件

1、必须安装[WireShark](https://www.wireshark.org/download.html)，如果你是在基于Linux的操作系统上使用HoneyBot的话，你可以直接安装t-shark：

    
    
    apt-get install tshark

2、需要使用[Python 3.5](https://www.python.org/downloads/)或更高版本；

3、在使用这些脚本之前，必须申请一个[API密钥](https://packettotal.com/api.html)；

##  工具安装

> pip install -r requirements.txt
>
> python setup.py install

##  工具使用

###  capture-and-analyze.py

    
    
    usage: capture-and-analyze.py [-h] [--seconds SECONDS] [--interface INTERFACE]
    
                                      [--analyze] [--list-interfaces] [--list-pcaps]
    
                                      [--export-pcaps]
    
        Capture, upload and analyze network traffic; powered by PacketTotal.com.
    
        optional arguments:
    
          -h, --help            show this help message and exit
    
          --seconds SECONDS     The number of seconds to capture traffic for.
    
          --interface INTERFACE
    
                                The name of the interface (--list-interfaces to show
    
                                available)
    
          --analyze             If included, capture will be uploaded for analysis to
    
                                PacketTotal.com.
    
          --list-interfaces     Lists the available interfaces.
    
          --list-pcaps          Lists pcaps submitted to PacketTotal.com for analysis.
    
          --export-pcaps        Writes pcaps submitted to PacketTotal.com for analysis
    
                                to a csv file.

###  upload-and-analyze.py

    
    
    usage: upload-and-analyze.py [-h] [--path PATH [PATH ...]] [--analyze]
    
                                     [--list-pcaps] [--export-pcaps]
    
        Upload and analyze .pcap/.pcapng files in bulk; powered by PacketTotal.com.
    
        optional arguments:
    
          -h, --help            show this help message and exit
    
          --path PATH [PATH ...]
    
                                One or more paths to pcap or directory of pcaps.
    
          --analyze             If included, capture will be uploaded for analysis to
    
                                PacketTotal.com.
    
          --list-pcaps          Lists pcaps submitted to PacketTotal.com for analysis.
    
          --export-pcaps        Writes pcaps submitted to PacketTotal.com for analysis
    
                                to a csv file.

###  trigger-and-analyze.py

    
    
    usage: trigger-and-analyze.py [-h] [--interface INTERFACE] [--learn LEARN]
    
                                      [--listen] [--capture-seconds CAPTURE_SECONDS]
    
                                      [--list-interfaces] [--list-pcaps]
    
                                      [--export-pcaps]
    
        Listen for unknown connections, and begin capturing when one is made. Captures
    
        are automatically uploaded and analyzed; powered by PacketTotal.com
    
        optional arguments:
    
          -h, --help            show this help message and exit
    
          --interface INTERFACE
    
                                The name of the interface (--list-interfaces to show
    
                                available)
    
          --learn LEARN         The number of seconds from which to build the known
    
                                connections whitelist. Connections in this whitelist
    
                                will be ignored.
    
          --listen              If included, we will begin listening for unknown
    
                                connections, and immediately starting a packet capture
    
                                and uploading to PacketTotal.com for analysis.
    
          --capture-seconds CAPTURE_SECONDS
    
                                The number of seconds worth of network traffic to
    
                                capture and analyze after a trigger has fired.
    
          --list-interfaces     Lists the available interfaces.
    
          --list-pcaps          Lists pcaps submitted to PacketTotal.com for analysis.
    
          --export-pcaps        Writes pcaps submitted to PacketTotal.com for analysis
    
                                to a csv file.

##  项目地址

> HoneyBot：【[GitHub传送门](https://github.com/PacketTotal/HoneyBot)】

 ***
参考来源：[PacketTotal](https://github.com/PacketTotal/HoneyBot)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

