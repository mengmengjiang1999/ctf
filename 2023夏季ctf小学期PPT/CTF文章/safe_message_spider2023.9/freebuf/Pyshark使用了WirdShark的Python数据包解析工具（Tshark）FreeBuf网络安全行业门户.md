![](https://image.3001.net/images/20190906/1567702893_5d713f6d4b4de.jpg!small)

##  Pyshark

**Pyshark是一款针对tshark的Python封装器，在Pyshark的帮助下，广大研究人员可以使用wireshark的解析器来进行Python数据包解析。**

> 扩展文档：【[Pyshark](http://kiminewt.github.io/pyshark)】

虽然目前社区也有多款针对Python包的解析模块，但Pyshark与它们不同的是，它本身并不会解析任何数据包，它只会使用tshark的功能（Wireshark命令行实用工具）来导出XML并完成包解析。

##  工具安装

###  针对全平台

广大用户可以直接使用pip来从pypi安装Pyshark：

    
    
    pip install pyshark

或者，大家也可以直接从该项目的GitHub库直接将项目代码克隆至本地：

    
    
    git clone <https://github.com/KimiNewt/pyshark.git>
    
        cd pyshark/src
    
        python setup.py install

###  Mac OS X

在macOS上，你可能还需要安装libxml，如果你在运行clang命令时遇到了错误，或系统弹出了关于libxml的错误，你就需要运行下列命令了：

    
    
    xcode-select--install
    
        pip install libxml

##  工具使用

###  从捕捉到cap文件中读取解析内容：

    
    
    >>>import pyshark
    
        >>>cap = pyshark.FileCapture('/tmp/mycapture.cap')
    
        >>>cap
    
        <FileCapture/tmp/mycapture.cap (589 packets)>
    
        >>>print cap[0]
    
        Packet(Length: 698)
    
        LayerETH:
    
        Destination: BLANKED
    
        Source: BLANKED
    
        Type: IP (0x0800)
    
        LayerIP:
    
        Version: 4
    
        Header Length: 20 bytes
    
        Differentiated Services Field: 0x00(DSCP 0x00: Default; ECN: 0x00: Not-ECT (Not ECN-Capable Transport))
    
        Total Length: 684
    
        Identification: 0x254f (9551)
    
        Flags: 0x00
    
        Fragment offset: 0
    
        Time to live: 1
    
        Protocol: UDP (17)
    
        Header checksum: 0xe148 [correct]
    
        Source: BLANKED
    
        Destination: BLANKED
    
        ...

###  其他选项：

    
    
    paramkeep_packets: 在读取完内容后是否保存包；
    
        paraminput_file: 判断路径或文件对象是否包含包文件（PCAP、PCAP-NG…）或TSharkXML；
    
        paramdisplay_filter: 是否需要在读取包内容前配置过滤器；
    
        paramonly_summaries: 生成包概括数据，速度快，但信息少；
    
        paramdisable_protocol: 禁用协议探测功能 (tshark > version 2)；
    
        paramdecryption_key: 用于加密和解密捕捉流量的密钥；
    
        paramencryption_type: 捕捉流量中的标准加密（'WEP', 'WPA-PWD', 或'WPA-PWK'，默认为WPA-PWK）；
    
        paramtshark_path: tshark代码路径；

###  从活动接口读取包内容：

    
    
    >>>capture = pyshark.LiveCapture(interface='eth0')
    
        >>>capture.sniff(timeout=50)
    
        >>>capture
    
        <LiveCapture(5 packets)>
    
        >>>capture[3]
    
        <UDP/HTTPPacket>
    
        for packet in capture.sniff_continuously(packet_count=5):
    
        print 'Just arrived:', packet

###  使用环状缓冲区从活动接口读取包内容：

    
    
    >>>capture = pyshark.LiveRingCapture(interface='eth0')
    
        >>>capture.sniff(timeout=50)
    
        >>>capture
    
        <LiveCapture(5 packets)>
    
        >>>capture[3]
    
        <UDP/HTTPPacket>
    
        for packet in capture.sniff_continuously(packet_count=5):
    
        print 'Just arrived:', packet

###  从远程活动接口读取包内容：

    
    
    >>>capture = pyshark.RemoteCapture('192.168.1.101', 'eth0')
    
        >>>capture.sniff(timeout=50)
    
        >>>capture

##  访问包数据

我们可以通过多种方式访问数据，Python包被划分成到了多个层，首先我们需要访问特定的层，然后选择相应的数据区域。

    
    
    >>>packet['ip'].dst
    
        192.168.0.1
    
        >>>packet.ip.src
    
        192.168.0.100
    
        >>>packet[2].src
    
        192.168.0.100

判断数据包中是否包含某一层，我们可以使用下列命令：

    
    
    >>>'IP' in packet
    
        True

如需查看所有的数据区域，可以使用“packet.layer.field_names”属性，例如“packet.ip.field_names”。当然了，我们还可以直接获取到数据区域的原始代码数据以及注释信息：

    
    
    >>>p.ip.addr.showname
    
        Sourceor Destination Address: 10.0.0.10 (10.0.0.10)
    
        # Andsome new attributes as well:
    
        >>>p.ip.addr.int_value
    
        167772170
    
        >>>p.ip.addr.binary_value
    
        '\n\x00\x00\n'

##  解密捕捉到的包

Pyshark支持自动化解密，支持的加密标准有WEP、WPA-PWD和WPA-PSK，默认为WPA-PWD：

    
    
    >>>cap1 = pyshark.FileCapture('/tmp/capture1.cap', decryption_key='password')
    
        >>>cap2 = pyshark.LiveCapture(interface='wi0', decryption_key='password',encryption_type='wpa-psk')

除此之外，Pyshark还支持以元组的形式传递支持的加密标准：

    
    
    >>>pyshark.FileCapture.SUPPORTED_ENCRYPTION_STANDARDS
    
        ('wep','wpa-pwd', 'wpa-psk')
    
        >>>pyshark.LiveCapture.SUPPORTED_ENCRYPTION_STANDARDS
    
        ('wep','wpa-pwd', 'wpa-psk')

##  项目地址

> Pyshark：【[GitHub传送门](https://github.com/KimiNewt/pyshark)】

***参考来源：[KimiNewt](https://github.com/KimiNewt/pyshark)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

