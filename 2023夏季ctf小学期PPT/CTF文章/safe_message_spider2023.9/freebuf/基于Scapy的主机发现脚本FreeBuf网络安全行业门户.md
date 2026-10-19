## 简介

scapy是python的一个第三方库，内部已经实现了许多网络协议，可以利用这个库来编写许多工具。当然，scapy可以实现的功能很多，下文只实现基于
**TCP** 、 **UDP** 、 **ARP** 的三种主机发现的简单脚本。下面介绍这次利用python工具编写所用到的命令和功能。

    
    
    tips:
    	由于scapy不太兼容Windows平台，所以该脚本使用主要用于Linux。
    创建一个IP和TCP的报文:
        packet = IP()/TCP()
    参数信息:
    	IP:
            src 			#源IP地址
            dst				#目的IP地址
            flags			#标记
        TCP:
        	dport  			#目标端口
        ARP:
        	hwsrc   		#源MAC地址
            psrc       		#源IP地址
            hwdst      		#目标MAC地址
            pdst       		#目标IP
    查看信息:
    	packet.show()       #查看发送过来的报文
    	ls(packet)			#查看报文结构
    	display()           #查看packet响应参数
    报文发送:
    	第三层发包:
            sr1    			#只捕获第一个响应报文忽略其他。
        第二层发包
            srp	   			#可以指定网卡
            srp1    		#只接收第一个响应
    

## 基于TCP的主机发现

正常的三次握手

  * 客户端向服务器发送SYN

  * 服务端返回SYN/ACK

  * 客户端发送ACK表示连接建立

##### 向服务端开放的端口发送SYN标志，服务端收到请求响应SYN+ACK

###### scapy里输入的命令

    
    
    ktp = IP()/TCP()                    # 构造数据包
    ktp[IP].dst = "192.168.5.129"		# 目标地址
    ktp[TCP].flags = "S"				# 标记
    ktp[TCP].dport = 80					# 目标端口
    recv = sr1(ktp)						# sr1在第三层发包并接收第一个响应包
    

##### 向服务端开放的端口发送SYN标志，服务端收到请求响应SYN/ACK

![image](https://image.3001.net/images/20221030/1667121831_635e42a70137515dbe76b.png!small)

##### 向服务端不开放的端口发送SYN标志，服务端收到请求响应RST/ACK

![image](https://image.3001.net/images/20221030/1667121848_635e42b8747d8187c4d09.png!small)

##### 向服务端直接发送ACK标志，服务端收到请求响应RST重置连接

![image](https://image.3001.net/images/20221030/1667121910_635e42f6c0ee4359c69af.png!small)

##### 目标机器响应的flags字段为R，表示请求主机给我们发送了一个重置连接的标志，因此可以由此来判断主机是否存活。

![image](https://image.3001.net/images/20221030/1667121936_635e431023f43e1745c93.png!small)

##### 可以根据flags判断主机是否存活，编写python代码

    
    
    #!/usr/bin/env python3
    # -*- coding:utf-8 -*-    import gevent
    from gevent.pool import Pool  # 使用协程
    
    gevent.monkey.patch_all()   #使用monkey来识别io操作，必须放在scapy模块之前
    from scapy.all import *
    from random import randint
    import logging
    
    logging.getLogger("scapy.runtime").setLevel(logging.ERROR) # 屏蔽scapy日志输出ERROR以下的信息
    
    
    def scan(dst):
        try:
            dport = randint(1, 65535)
            packet = IP(dst=dst) / TCP(flags='A', dport=dport)
            res = sr1(packet, timeout=2.0, verbose=False)
            gevent.sleep(0.5)
            if res:
                if 'R' in res[TCP].flags:
                    print(dst + "is alive")
                else:
                    print('no')
        except AttributeError as err:
            pass
    
    
    if __name__ == "__main__":
        import time
        starttime = time.time()
        g = Pool(150)  # 限制协程的并发数量
        run_list = [g.spawn(scan, "192.168.5.{}".format(host)) for host in range(256)]
        gevent.joinall(run_list)
        stoptime = time.time()
        print("用时{}".format(starttime - stoptime))
    

![image](https://image.3001.net/images/20221030/1667121965_635e432d57755131f0b5d.png!small)

##### 在kali端开启抓包看到扫描段发过来的包

![image](https://image.3001.net/images/20221030/1667121988_635e4344bf146b4ad3267.png!small)

##### 存活主机的响应

![image](https://image.3001.net/images/20221030/1667122007_635e43579fb6b86d5cbf2.png!small)

## 基于UDP的主机发现

UDP是一个面向无连接的通信服务，在程序接收到UDP的数据时，会立刻原模原样的发到网络时。即便出现丢包、或者数据包顺序错乱，也不会再次发送。向目标发送UDP数据包时，对方并不会返回任何的UDP包。但是当主机存活时，如果发送的目标端口是关闭的，目标会响应一个
**unreachable** 的ICMP数据包，否则无响应，我们可以利用此原理编写扫描工具

###### scapy命令

    
    
    ukp = IP()/UDP()
    ukp[IP].dst = "192.168.5.129"
    ukp[UDP].dport = 445
    recv = sr1(ukp)
    

##### 可以看到不可达的响应

![image](https://image.3001.net/images/20221030/1667122020_635e4364df0539a80de16.png!small)

##### 根据此原理编写python脚本，判断有无响应包

    
    
    #!/usr/bin/env python3
    # -*- coding:utf-8 -*-    import gevent
    from gevent.pool import Pool
    gevent.monkey.patch_all()
    from scapy.all import *
    from random import randint
    import logging
    logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
    
    
    def scan(dst):
        try:
            dport = randint(1, 65535)
            packet = IP(dst=dst)/UDP(dport=dport)
            res = sr1(packet, timeout=1.0, verbose=False)
            if res:
                print(dst+"is alive")
        except AttributeError as err:
            pass
    
    if __name__ == "__main__":
    
        import time
        starttime = time.time()
        g = Pool(150)  # 限制协程的并发数量
        run_list = [g.spawn(scan, "192.168.5.{}".format(host)) for host in range(256)]
        gevent.joinall(run_list)
        stoptime = time.time()
        print("用时{}".format(starttime - stoptime))
    

##### 扫描成功

![image](https://image.3001.net/images/20221030/1667122033_635e43714171070b6b9af.png!small)

##### 在kali端看到了响应给扫描机的ICMP包

![image](https://image.3001.net/images/20221030/1667122062_635e438e3f040c3b8ef89.png!small)

### 基于ARP的主机发现

地址解析协议ARP处于数据链路层，用于根据IP（网络层）获取MAC（数据链路层）地址，简单的来说，在一个局域网内，一台主机想要和另一台主机通信时，需要知道
**对方** 的 **MAC**
地址，如果本地ARP缓存没有对方的MAC地址，就会向局域网进行广播发送ARP的请求，询问目标IP的MAC地址，同时数据包里包含自己的IP和MAC地址，局域网内的所有主机都会收到该请求。如果
**自身IP** 与ARP请求的IP一致，则将自己的MAC地址发回给请求方，并将请求数据包中的IP与MAC地址存入本地。

我们可以利用arp请求扫描存活的主机，ARP请求涉及网络层与数据链路层，因此我们需要scapy模块里的 **Ether** 与 **ARP**

    
    
    编写扫描器需要用到的参数
    Ether:
        src    # 源MAC地址
        dst    # 目表MAC地址
    ARP:
        hwsrc 	  # 源MAC地址
        hwdst    # 源IP地址
        pdst     # 目标IP地址
        op       # 1是ARP请求  2是ARP的响应
    

![image](https://image.3001.net/images/20221030/1667122076_635e439c80fafc5456d41.png!small)

##### 构造一个ARP请求，这是对方主机响应后的正常回显，可以看到对方的mac地址

![image](https://image.3001.net/images/20221030/1667122099_635e43b3166b010dee933.png!small)

##### 响应信息里对方的MAC地址

![image](https://image.3001.net/images/20221030/1667122121_635e43c92fcc8f265561f.png!small)

![image](https://image.3001.net/images/20221030/1667122136_635e43d8e33820f2c3573.png!small)

##### 再次发送一个ARP请求，这次请求一个局域网里不存在的主机IP

![image](https://image.3001.net/images/20221030/1667122159_635e43efd6ac234e9088b.png!small)

##### 可以看到并没有响应信息

![image](https://image.3001.net/images/20221030/1667122184_635e44086a600d081f5e3.png!small)

##### 可以根据响应信息来进行扫描器的编写

    
    
    #!/usr/bin/env python3
    # -*- coding:utf-8 -*-    import gevent
    from gevent.pool import Pool
    gevent.monkey.patch_all()
    from scapy.all import *
    import logging
    logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
    
    def scan(dst, conf):
        try:
            ip, mac, iface = conf
            kpt = Ether() / ARP()
            kpt[Ether].src = mac    # 源MAC地址
            kpt[Ether].dst = "FF:FF:FF:FF:FF:FF"    # 目的MAC地址
            kpt[ARP].hwsrc = "00:0c:29:ec:dc:d2"
            kpt[ARP].hwdst = mac
            kpt[ARP].pdst = dst
            kpt[ARP].op = 1
            ares = srp(kpt, iface=iface, timeout=2.0, verbose=False)
            if ares[0].res:
                print("\nIP:{0}\nMAC:{1}".format(dst, ares[0].res[0][1].src))
        except AttributeError as err:
            pass
    
    if __name__ == "__main__":
        import time
        import subprocess
        import re
    
        rec = input("请输入扫描网卡:").strip()
        # 提取本地IP与MAC信息
        res = subprocess.Popen(rec, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        tmp = res.stdout.read().decode() + res.stderr.read().decode()
        IP = re.search('inet(.*?)netmask', tmp, re.S)
        MAC = re.search('ether(.*?)txqueuelen', tmp, re.S)
    
        starttime = time.time()
        g = Pool(150)  # 限制协程并发数量，单线程的，不要设置太大
        run_list = [g.spawn(scan, "192.168.5.{}".format(host), (IP, MAC, rec)) for host in range(256)]
        gevent.joinall(run_list)
        stoptime = time.time()
        print("用时{}".format(starttime - stoptime))
    

##### 查看要扫描网段的网卡

![image](https://image.3001.net/images/20221030/1667122208_635e4420ba5cf47883dc2.png!small)

##### 可以看到扫描的结果是三种方法里最快的

![image](https://image.3001.net/images/20221030/1667122222_635e442e29a25e74fffad.png!small)

##### 当然，上文只是简单的实现了主机扫描的功能，代码运行速度还有很大的提升空间，后续会整合成一个工具，能力有限大佬勿喷。

