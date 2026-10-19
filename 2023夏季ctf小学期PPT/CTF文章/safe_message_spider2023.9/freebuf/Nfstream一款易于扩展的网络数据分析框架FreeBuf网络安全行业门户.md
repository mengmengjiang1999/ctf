![](https://image.3001.net/images/20200206/1580979180_5e3bd3ec39291.png!small)

**Nfstream本质上来说是一款Python包，它可以提供快速、灵活且有效的数据结构，支持针对在线或离线状态的网络数据进行分析，这种方式既简单又直观。在Nfstream的帮助下，广大研究人员可以直接在自己的Python代码中集成数据分析功能，并对真实场景下的实际网络数据进行分析。除此之外，Nfstream目前仍处于开发阶段，该项目将会为研究人员提供各种实验数据复现功能，并成为一款通用的网络数据处理与分析框架。**

##  功能介绍

> 1、性能：Nfstream的运行速度非常快（集成pypy3后，速度将会快10倍），而且对CPU和内存的需求并不大；
>
>
> 2、七层可见度：Nfstream深度数据包检测引擎基于[nDPI](https://github.com/ntop/nDPI)实现，它允许Nfstream执行[可靠的](http://people.ac.upc.edu/pbarlet/papers/ground-> truth.pam2014.pdf)加密应用识别与元数据提取（例如TLS, QUIC, TOR, HTTP, SSH, DNS）；
>
>
> 3、灵活性：引入[NFPlugin](https://nfstream.readthedocs.io/en/latest/plugins.html)插件概念，便于实现功能扩展；
>
>
> 4、机器学习：支持以[NFPlugin](https://nfstream.readthedocs.io/en/latest/plugins.html)的形式添加训练模型；

##  工具依赖

广大研究人员可以运行下列命令来完成NFPlugin依赖组件的配置：

    
    
    apt-get install libpcap-dev

##  工具下载

###  使用pip安装

如果你习惯使用pip的话，你可以直接使用pip3命令安装本项目的最新版本：

    
    
    pip3 install nfstream

###  源码构建

广大研究人员也可以使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/aouinizied/nfstream.git

##  工具使用

当你在处理一个非常大的pcap文件时，如果你只想将其聚合为网络流，那么你只需要实现下列几行代码，剩下的就可以交给Nfstream来完成了：

    
    
    from nfstream import NFStreamer
    
           my_awesome_streamer = NFStreamer(source="facebook.pcap") # or network interface (source="eth0")
    
           for flow in my_awesome_streamer:
    
               print(flow)  # print it, append to pandas Dataframe or whatever you want :)!
    
        NFEntry(
    
                id=0,
    
                first_seen=1472393122365,
    
                last_seen=1472393123665,
    
                version=4,
    
                src_port=52066,
    
                dst_port=443,
    
                protocol=6,
    
                vlan_id=0,
    
                src_ip='192.168.43.18',
    
                dst_ip='66.220.156.68',
    
                total_packets=19,
    
                total_bytes=5745,
    
                duration=1300,
    
                src2dst_packets=9,
    
                src2dst_bytes=1345,
    
                dst2src_packets=10,
    
                dst2src_bytes=4400,
    
                expiration_id=0,
    
                master_protocol=91,
    
                app_protocol=119,
    
                application_name='TLS.Facebook',
    
                category_name='SocialNetwork',
    
                client_info='facebook.com',
    
                server_info='*.facebook.com',
    
                j3a_client='bfcc1a3891601edb4f137ab7ab25b840',
    
                j3a_server='2d1e***17ece335c24904f516ad5da12'
    
        )

###  将pcap转换为Pandas DataFrame：

    
    
    import pandas as pd	
    
        streamer_awesome = NFStreamer(source='devil.pcap')
    
        data = []
    
        for flow in streamer_awesome:
    
           data.append(flow.to_namedtuple())
    
        my_df = pd.DataFrame(data=data)
    
        my_df.head(5) # Enjoy!

###  如果你没找到特定的数据流功能，你可以通过几行代码来向Nfstream增加插件：

    
    
    from nfstream import NFPlugin
    
        class my_awesome_plugin(NFPlugin):
    
            def on_update(self, obs, entry):
    
                if obs.length >= 666:
    
                    entry.my_awesome_plugin += 1
    
        streamer_awesome = NFStreamer(source='devil.pcap', plugins=[my_awesome_plugin()])
    
        for flow in streamer_awesome:
    
           print(flow.my_awesome_plugin) # see your dynamically created metric in generated flows

更多详细的使用方法，请参考Nfstream的官方文档：【[点我获取](https://readthedocs.org/projects/nfstream/downloads/pdf/latest/)】

##  项目地址

> NFPlugin：【[GitHub传送门](https://github.com/aouinizied/nfstream)】

 ***
参考来源：[aouinizied](https://github.com/aouinizied/nfstream)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

