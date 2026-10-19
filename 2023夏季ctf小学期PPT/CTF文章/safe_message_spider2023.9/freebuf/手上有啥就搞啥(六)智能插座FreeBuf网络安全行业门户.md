本篇是”手上有啥就搞啥“系列的第六篇，也是最后一篇，研究对象是智能插座，侧重点是 **协议分析** 与 **指令控制** 。

![](https://image.3001.net/images/20230509/1683636307_645a4053478cc54a17393.png!small)

之前的设备研究皆偏重静态分析，此次将直接跳过逆向环节，通过动态扫描等方式还原协议，最终实现指令控制。

内容主要包括：

  * 0x00 基础知识：智能插座简介
  * 0x01 站在巨人肩上：设备信息与硬件拆解
  * 0x02 自己动手做：设备扫描、协议分析与指令控制
  * 0x03 做个总结：简单总结
  * 0x04 写在最后：系列总结
  * 0x05 参考资料：参考链接

往期回顾：

 **[手上有啥就搞啥(一) —
小米手环3](https://www.freebuf.com/articles/articles/endpoint/344640.html)**

 **[手上有啥就搞啥(二) —
猫盘](https://www.freebuf.com/articles/articles/endpoint/346606.html)**

 **[手上有啥就搞啥(三) —
WiFi信号放大器](https://www.freebuf.com/articles/articles/endpoint/348964.html)**

 **[手上有啥就搞啥(四) — H3C
智能摄像头](https://www.freebuf.com/articles/articles/endpoint/355770.html)**

 **[手上有啥就搞啥(四) — H3C
智能摄像头](https://www.freebuf.com/articles/articles/endpoint/355770.html)**

 **[手上有啥就搞啥(五) —
小米电力猫](https://www.freebuf.com/articles/endpoint/359099.html)**

##  **0x00 基础知识**

###  **0x00 - 00 智能插座简介**

 **智能插座 (smart plug)**
是一种电源插头或插座，可安装在电源线和插座之间，用作遥控电源开关，从而使用该设备达到家庭自动化或楼宇自动化目的。智能插头可通过移动应用程序、智能家居集线器或虚拟助手进行控制。与智能插头通信的协议可包括Wi-Fi，蓝牙，Zigbee 和 Z-Wave。许多智能插头都有一个内置的电流表，因此可以监控连接设备的电能消耗。

###  **0x00 - 01 智能插座工作原理**

智能插座基本原理很简单，可阅读 **[这篇文章](https://zhuanlan.zhihu.com/p/332816650)** 。

一般WiFi智能插座由 **按键模块** 、 **WiFi模块** 和 **继电器模块**
组成。按键模块负责控制插座开关和重置设备；WiFi模块连接路由器，连接远程的服务器，让APP控制插座；继电器模块控制220V电压通断。

![](https://image.3001.net/images/20230509/1683636417_645a40c1a55510918daaf.png!small)

手机APP远程控制与之前提到的家用IOT设备相同，都使用云“中继”，其原理如下图：![](https://image.3001.net/images/20230509/1683636428_645a40cc5dfa6bba56d64.png!small)

##  **0x01 站在巨人肩上**

本次不侧重硬件和固件，简单看一下型号和拆解。

###  **0x01 - 00
设备信息![](https://image.3001.net/images/20230509/1683636594_645a4172617a62d19b92e.png!small)**

###  **0x01 - 01
硬件拆解![](https://image.3001.net/images/20230509/1683636625_645a419187c7299906a2f.png!small)**

WiFi模块可直接拆解下来：![](https://image.3001.net/images/20230509/1683636634_645a419aaa0fe1c21c7c3.png!small)

##  **0x02 自己动手做**

常规操作是先作设备扫描等 **信息收集** ，然后通过 **逆向** 和 **抓包分析** 等方式还原协议，最后编写工具实现 **指令控制**
。但实际操作中，设备扫描后搜索信息发现已经有成熟的三方控制方案 **python-miio** ，阅读python
代码显然比逆向协议分析容易的多，尤其在协议加密的情况下，顾笔者先通过工具实现设备控制，在回过头来学习协议细节。

###  **0x02 - 00 设备扫描**

利用 Nmap 扫描设备，发现 TCP 无端口开放，UDP 开放54321 端口。

    
    
    # nmap 192.168.31.16
    Starting Nmap 7.93 ( <https://nmap.org> ) at 2023-04-17 19:03 CST
    Nmap scan report for 192.168.31.16
    Host is up (0.0027s latency).
    All 1000 scanned ports on 192.168.31.16 are in ignored states.
    Not shown: 1000 closed tcp ports (reset)
    MAC Address: 40:31:3C:D6:A9:94 (Xiaomi Electronics,co.)
    
    Nmap done: 1 IP address (1 host up) scanned in 28.44 seconds
    MacBook-Pro ~ % sudo nmap -A 192.168.31.16
    Starting Nmap 7.93 ( <https://nmap.org> ) at 2023-04-17 19:04 CST
    NSOCK ERROR [1.3100s] ssl_init_helper(): OpenSSL legacy provider failed to load.
    
    Nmap scan report for 192.168.31.16
    Host is up (0.0048s latency).
    All 1000 scanned ports on 192.168.31.16 are in ignored states.
    Not shown: 1000 closed tcp ports (reset)
    MAC Address: 40:XX:XX:XX:XX:XX (Xiaomi Electronics,co.)
    Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
    Device type: specialized|general purpose
    Running: Espressif embedded, lwIP, NodeMCU embedded
    OS CPE: cpe:/a:lwip_project:lwip cpe:/o:nodemcu:nodemcu
    OS details: Espressif esp8266 firmware (lwIP stack), NodeMCU firmware (lwIP stack)
    Network Distance: 1 hop
    
    TRACEROUTE
    HOP RTT     ADDRESS
    1   4.76 ms 192.168.31.16
    
    OS and Service detection performed. Please report any incorrect results at <https://nmap.org/submit/> .
    Nmap done: 1 IP address (1 host up) scanned in 19.58 seconds
    # nmap -sU 192.168.31.16
    Starting Nmap 7.93 ( <https://nmap.org> ) at 2023-04-17 19:05 CST
    Nmap scan report for 192.168.31.16
    Host is up (0.0028s latency).
    Not shown: 999 closed udp ports (port-unreach)
    PORT      STATE         SERVICE
    54321/udp open|filtered bo2k
    MAC Address:  40:XX:XX:XX:XX:XX (Xiaomi Electronics,co.)
    
    Nmap done: 1 IP address (1 host up) scanned in 104.54 seconds
    

通过时下流行手段搜索一下，追赶潮流：![](https://image.3001.net/images/20230509/1683636674_645a41c2c659885279b2a.png!small)![](https://image.3001.net/images/20230509/1683636683_645a41cb7437e96fdd886.png!small)

先不管细节是否正确，起码知道了 54321 端口是 Xiaomi 常见的设备管理端口。进一步搜索发现已有现成的三方管理工具， **python-miio**
是其中教完善的，下简述使用该工具实现对智能插座的指令控制。

###  **0x02 - 01 指令控制**

  * 工具安装

    
    
    # pip install python-miio
    

  * 发现设备

    
    
    > miiocli discover
    INFO:miio.miioprotocol:Sending discovery to <broadcast> with timeout of 5s..
    INFO:miio.miioprotocol:  IP 192.168.31.23 (ID: 07XXXXX5) - token: b'00000000000000000000000000000000'
    INFO:miio.miioprotocol:  IP 192.168.31.29 (ID: 0eXXXXXa) - token: b'00000000000000000000000000000000'
    INFO:miio.miioprotocol:  IP 192.168.31.192 (ID: 1bXXXXX5) - token: b'ffffffffffffffffffffffffffffffff'
    INFO:miio.miioprotocol:  IP 192.168.31.250 (ID: 21XXXXX5) - token: b'ffffffffffffffffffffffffffffffff'
    INFO:miio.miioprotocol:Discovery done
    

此时的 **token** 显然不正确。

  * 获取token

由于协议采用加密传输， **token** 是 APP 与设备通信所需的密钥， **token** 为 16 字节 **hexstring**
，值得注意的是，设备与云端通信的 CloudKey 也是 16 字节，不同之处在于 **CloudKey 不会改变** ，而 **token 在设备连接新
wifi 时会重新生成** 。

之前的方法是向设备发送 **helobytes** ，设备会返回token值：

    
    
    #-*-coding:utf8-*-    import codecs
    import socket
    from protocol import Message
    
    helobytes = bytes.fromhex('21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(helobytes, ('192.168.42.17', 54321))#插座ip，端口54321
    data, addr = s.recvfrom(1024)
    m = Message.parse(data)
    tok = codecs.encode(m.checksum, 'hex')
    print("token:%s" % tok)
    

但是此方法已经失效，返回信息为全0。

    
    
    miio> python3 miio_test.py
    token:b'00000000000000000000000000000000'
    

**python-miio** 中推荐的 **micloud** 返回值也为空。其原理就是利用官方API查询。

笔者在此没有过多研究，通过 **[Xiaomi-cloud-tokens-extractor](https://github.com/PiotrMachowski/Xiaomi-cloud-tokens-extractor)**
实现了获取 **token** 的操作，此外还有
[**Get_MiHome_devices_token**](https://github.com/Maxmudjon/Get_MiHome_devices_token)，感兴趣的小伙伴可以尝试
( **该类工具需要输入用户名和密码，笔者未审计代码是否存在后门，使用需谨慎！！！**
)。![](https://image.3001.net/images/20230509/1683636721_645a41f1b5b64f2260a83.png!small)

  * 实现控制

获取 token 后，工具使用十分简单：

    
    
    # miiocli plug --ip 192.168.31.16 --token 00000000000000000000000000000000 [cmd]
    

获取插座信息( 错误由于python 库版本原因，自行忽略
)：![](https://image.3001.net/images/20230509/1683636736_645a42000b0ca82270959.png!small)

关闭智能插座：![](https://image.3001.net/images/20230509/1683636744_645a42080c5e316f01534.png!small)

打开智能插座：![](https://image.3001.net/images/20230509/1683636754_645a42126a9e53473dcb9.png!small)

下文将基于此工具分析控制协议的细节。

###  **0x02 - 02 协议分析**

首先定位控制 Plug 模块代码，通过 **CHANGELOG.md** 得知控制模块为 **ChuangmiPlug** 。

    
    
    # CHANGELOG.md
    * Plug, PlugV1, PlugV3 - use ChuangmiPlug
    

在 **chuangmi_plug.py** 文件中定位到 **on** 和 **off** 的函数实现，关键代码为 **send** 函数：

    
    
    # miio\\integrations\\chuangmi\\plug\\chuangmi_plug.py
    @command(default_output=format_output("Powering on"))
        def on(self):
            """Power on."""
            if self.model == MODEL_CHUANGMI_PLUG_V1:
                return self.send("set_on")
    
            return self.send("set_power", ["on"])
    
        @command(default_output=format_output("Powering off"))
        def off(self):
            """Power off."""
            if self.model == MODEL_CHUANGMI_PLUG_V1:
                return self.send("set_off")
    
            return self.send("set_power", ["off"])
    

**send** 函数在 **miioprotocol.py** 实现，列出部分关键代码如下：

    
    
    # miio\\miioprotocol.py
    
    def send(
            self,
            command: str,
            parameters: Optional[Any] = None,
            retry_count: int = 3,
            *,
            extra_parameters: Optional[Dict] = None
        ) -> Any:
            """Build and send the given command. Note that this will implicitly call
            :func:`send_handshake` to do a handshake, and will re-try in case of errors
            while incrementing the `_id` by 100.
    
            :param str command: Command to send
            :param dict parameters: Parameters to send, or an empty list
            :param retry_count: How many times to retry in case of failure, how many handshakes to send
            :param dict extra_parameters: Extra top-level parameters
            :raises DeviceException: if an error has occurred during communication.
            """
    
            if not self.lazy_discover or not self._discovered:
                self.send_handshake()
    
            request = self._create_request(command, parameters, extra_parameters)
    
            send_ts = self._device_ts + timedelta(seconds=1)
            header = {
                "length": 0,
                "unknown": 0x00000000,
                "device_id": self._device_id,
                "ts": send_ts,
            }
    
            msg = {"data": {"value": request}, "header": {"value": header}, "checksum": 0}
            m = Message.build(msg, token=self.token)
            
    	      ......
    
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(self._timeout)
    
            try:
                s.sendto(m, (self.ip, self.port))
            except OSError as ex:
                _LOGGER.error("failed to send msg: %s", ex)
                raise DeviceException from ex
    
            try:
                data, addr = s.recvfrom(4096)
                m = Message.parse(data, token=self.token)
    
                ......
    
                header = m.header.value
                payload = m.data.value
    
                self.__id = payload["id"]
                self._device_ts = header["ts"]  # type: ignore  # ts uses timeadapter
    
    						......
    
                if "error" in payload:
                    self._handle_error(payload["error"])
    
                try:
                    return payload["result"]
                except KeyError:
                    return payload
            ......
    

代码结构十分清晰，主要流程如下：![](https://image.3001.net/images/20230509/1683636805_645a42450d01724017714.png!small)

 **send_handshake** 时默认尝试 **3** 次 **discover** ，

    
    
    def send_handshake(self, *, retry_count=3) -> Message:
            """Send a handshake to the device.
    
            This returns some information, such as device type and serial,
            as well as device's timestamp in response.
    
            The handshake must also be done regularly to enable communication
            with the device.
    
            :raises DeviceException: if the device could not be discovered after retries.
            """
            try:
                m = MiIOProtocol.discover(self.ip)
            except DeviceException as ex:
                if retry_count > 0:
                    return self.send_handshake(retry_count=retry_count - 1)
    
                raise ex
    				......
    
            header = m.header.value
            self._device_id = header.device_id
            self._device_ts = header.ts
            self._discovered = True
    
    	      ......
    
            return m
    

**discover** 函数实现向设备 **UDP 54321** 端口的 broadcast：

    
    
    @staticmethod
        def discover(addr: Optional[str] = None, timeout: int = 5) -> Any:
            """Scan for devices in the network. This method is used to discover supported
            devices by sending a handshake message to the broadcast address on port 54321.
            If the target IP address is given, the handshake will be send as an unicast
            packet.
    
            :param str addr: Target IP address
            """
            is_broadcast = addr is None
            seen_addrs: List[str] = []
            ......
            # magic, length 32
            helobytes = bytes.fromhex(
                "21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
            )
    
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.settimeout(timeout)
            for _ in range(3):
                s.sendto(helobytes, (addr, 54321))
            while True:
                try:
                    data, recv_addr = s.recvfrom(1024)
                    m: Message = Message.parse(data)
                ......
    
                    if recv_addr[0] not in seen_addrs:
                        ......
                        seen_addrs.append(recv_addr[0])
                ......
    

通信会维护一个 **Message** 结构体：

    
    
    Message = Struct(
        # for building we need data before anything else.
        "data" / Pointer(32, RawCopy(EncryptionAdapter(GreedyBytes))),
        "header"
        / RawCopy(
            Struct(
                Const(0x2131, Int16ub),
                "length" / Rebuild(Int16ub, Utils.get_length),
                "unknown" / Default(Int32ub, 0x00000000),
                "device_id" / Hex(Bytes(4)),
                "ts" / TimeAdapter(Default(Int32ub, datetime.datetime.utcnow())),
            )
        ),
        "checksum"
        / IfThenElse(
            Utils.is_hello,
            Bytes(16),
            Checksum(Bytes(16), Utils.md5, Utils.checksum_field_bytes),
        ),
    )
    

当然，静态看再多都不如动态调试来的清晰，在 python 中只需添加 **print** 打印：

    
    
    def send(
    ......
    		m = Message.build(msg, token=self.token)
    		print ("######## sending message: ########")
    		print (m)
    		......
        s.sendto(m, (self.ip, self.port))
    	  ......
        data, addr = s.recvfrom(4096)
        m = Message.parse(data, token=self.token)
    		print ("######## recv message: ########")
    		print (m)
    

打印输出：![](https://image.3001.net/images/20230509/1683636859_645a427b15a51b4dcf1ab.png!small)``

最后来看设备、APP和云端之间的通信协议，如下图所示(并非针对智能插座，而是更复杂的设备)：![](https://image.3001.net/images/20230509/1683636880_645a42905a60ecb834f80.png!small)

该图来自DEFCON 26 的议题分享 **[Reverse Engineering and Hacking of Xiaomi IoT
Devices](https://dontvacuum.me/talks/DEFCON26/DEFCON26-Having_fun_with_IoT-Xiaomi.pdf)** ，感兴趣的小伙伴可以自行阅读。

##  **0x03 做个总结**

本篇针对智能插座作研究，实现协议分析与指令hack。由于整个xiaomi IOT 的生态比较完整，资料丰富，大大降低了研究难度，结合python-miio工具不仅可以作三方控制的开发，也可以对设备作一些Fuzz，有兴趣的小伙伴可以自行尝试。

##  **0x04 写在最后**

本系列旨在利用业余时间对手头闲置设备作点研究记录，达到发挥余热的目的，由于是“有啥搞啥”，研究的难度各异，文章的价值也就参差不齐，对于一些资料丰富的设备独立思考的空间不大，重在学习记录补齐短板。除却一些烂大街的路由器，手上能折腾的设(po)备(lan)也差不多了，坐等下一批设备淘汰再折腾，那就先到这，下个系列见吧。

##  **0x05 参考资料**

[智能插座原理？智能插座有什么用？智能插座推荐？最全智能插座介绍~](https://zhuanlan.zhihu.com/p/332816650)

[Installation — python-miio documentation](https://python-miio.readthedocs.io/en/latest/)

[小米 token(token在哪里获取)-腾讯云开发者社区-腾讯云](https://cloud.tencent.com/developer/beta/article/2062161)

[智能家居从新出发： 第二篇 获取米家设备的token_智能设备_什么值得买](https://post.smzdm.com/p/apzeg9d2/)

[最简单方法获取米家token，再也不用root、模拟器和抓包了 - 『HomeAssistant』综合讨论区 - 『瀚思彼岸』» 智能家居技术论坛 -Powered by Discuz!](https://bbs.hassbian.com/thread-12952-1-1.html)

[Xiaomi Miio](https://www.home-assistant.io/integrations/xiaomi_miio/#retrieving-the-access-token)

