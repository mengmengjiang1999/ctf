![](https://image.3001.net/images/20201205/1607100280_5fca67780d2cecf3b5e88.png!small)

## 关于AutoGadgetFS

AutoGadgetFS是一款开源框架，它可以帮助广大研究人员在无需深入了解USB协议的情况下对USB设备以及相关的主机/驱动器/软件进行评估。该工具基于Python
3开发，并且使用了RabbitMQ和WiFi访问来帮助研究人员对远程USB设备进行安全审计。在ConfigFS的帮助下，AutoGadgetFS允许用户迅速克隆和模拟设备而无需深入研究每一个实现细节。除此之外，该框架还允许用户创建自己的模糊测试器。

## 功能介绍

> 轻松查找、选择并连接到USB设备。
>
> 模拟任何USB HID设备。
>
> 以中间件设备身份执行AGFS嗅探HID设备（将通信保存到磁盘）。
>
> 设备嗅探（任何设备）。
>
> 多个Fuzzer允许您对设备或主机进行模糊测试。
>
> 随机Fuzzer（具有固定或随机长度的数据包）。
>
> 智能Fuzzer，可以从以前的USB通信中学习。
>
> 可以告诉Fuzzer哪些字节要模糊化，使包的其余部分保持不变。
>
> 小工具Fuzzer。
>
> 顺序Fuzzer。
>
> 控制传输枚举器。
>
> 从文件中重放数据包。
>
> 从保存的USBLyzer捕获重放数据包。
>
> 显示数据包的可视方式，以便于对通信信息进行逆向分析。
>
> DFU模式下的设备警报，或者设备泄漏信息。
>
> 支持对USB设备和主机进行远程调试。
>
> 监控突然的界面变化。

## 工具要求

> 一台运行了Linux的主机（Debian/Ubuntu/Kali）；
>
> 支持WiFi访问的树莓派Raspberry Pi Zero；
>
> 目标设备选择：虚拟机或单一主机；
>
> 两条USB线缆；
>
> 目标USB设备；
>
> 硬件调试器（可选）；

## 工具配置图

### 设备测试

![](https://image.3001.net/images/20201205/1607100370_5fca67d2a590335a01e23.jpeg!small)

### 设置中间件

![](https://image.3001.net/images/20201205/1607100377_5fca67d968369b4f58fca.jpeg!small)

### 设置中间件并支持设备调试

![](https://image.3001.net/images/20201205/1607100385_5fca67e10b88c06e83c5f.jpeg!small)

## 工具安装

### Linux设备

    
    
    sudo apt install python3 ipython3 git python3-pip rabbitmq-server dfu-util
    
    sudo service rabbitmq-server start
    
    git clone https://github.com/ehabhussein/AutoGadgetFS
    
    cd AutoGadgetFS
    
    sudo -H pip3 install -r requirements.txt
    
    sudo python3 -m pip install prompt-toolkit~=2.0
    
    sudo rabbitmq-plugins enable rabbitmq_management
    
    http://localhost:15672/ to reach the web interface
    
    sudo rabbitmqctl add_user autogfs usb4ever
    
    sudo rabbitmqctl set_user_tags autogfs administrator
    
    sudo service rabbitmq-server restart

### 安装完成后，请按照下列方式测试安装结果

    
    
    sudo ipython3
    
    Python 3.7.7 (default, Apr  1 2020, 13:48:52)
    
    Type 'copyright', 'credits' or 'license' for more information
    
    IPython 7.9.0 -- An enhanced Interactive Python. Type '?' for help.
    
    In [1]: import libagfs
    
    In [2]: x = libagfs.agfs()
    
    ***************************************
    
    AutoGadgetFS: USB testing made easy
    
    ***************************************
    
    Enter IP address of the rabbitmq server: 127.0.0.1
    
    In [3]: exit
    
    sudo `python3` agfsconsole.py
    
    ***************************************
    
    AutoGadgetFS: USB testing made easy
    
    ***************************************
    
    Enter IP address of the rabbitmq server: 127.0.0.1
    
    Give your project a name?!:

## 工具运行截图

### 中间人攻击

![](https://image.3001.net/images/20201205/1607100442_5fca681ae4dc50b619819.png!small)

### USB设备模糊测试

![](https://image.3001.net/images/20201205/1607100451_5fca6823e205fbf8c1a91.png!small)

### 主机端基于代码覆盖的模糊测试

![](https://image.3001.net/images/20201205/1607100464_5fca68300d88ecb224fc5.png!small)

### 基于字节的模糊测试

![](https://image.3001.net/images/20201205/1607100473_5fca6839c9c944cd09472.png!small)

### AutoGadgetFS命令行终端

![](https://image.3001.net/images/20201205/1607100487_5fca684715b635b4a0403.png!small)

## 基于流量学习的智能Fuzzer

    
    
    In [44]: x.devSmartFuzz(engine="smart",samples=5,filename="/home/raindrop/PycharmProjects/AutoGadgetFs/binariesdb/Nud-Nuvoton-1046-20764-1590421333.5169587-Nuvoton-1046-20764-1590421600.8067
    
    ...: 274-device.bin")                               
    
    [+]General Statistics
    
    Full charset                : !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~
    
    Discarded charset           : !"#$%&'()*+,-./:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`ghijklmnopqrstuvwxyz{|}~
    
    Final charset               : 0123456789abcdef
    
    Word Length                 : 128
    
    Lower Case index usage      : 92%
    
    Lower Case index locations  : [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 121, 122, 124, 125, 127]
    
    Upper Case index usage      : 0%
    
    Upper Case index locations  : []
    
    Digit index usage           : 96%
    
    Digit index locations       : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 123, 126]
    
    NonAN index usage           : 0%
    
    NonAN index locations       : []
    
    Counter statistics          : Uppercase: 0 , Lowercase: 133071, Digits:212017 , NonAlphaNumeric:0
    
    All char Frequencies        :
    
    character:5 found:5012 times
    
    character:2 found:22563 times
    
    character:3 found:12197 times
    
    character:8 found:15008 times
    
    character:4 found:13275 times
    
    character:0 found:98056 times
    
    character:1 found:17861 times
    
    character:f found:87823 times
    
    character:d found:7221 times
    
    character:7 found:9614 times
    
    character:a found:11148 times
    
    character:6 found:10472 times
    
    character:b found:8189 times
    
    character:9 found:7959 times
    
    character:c found:9172 times
    
    character:e found:9518 times
    
    ***********************
    
    generated:5 Packets
    
    ***********************
    
    Out[44]:
    
    ['5608305852bf2ffd61770e2c827542f20be0b0fcba09db916bd07e1734b04cb0352b1d278068064d19f033bfad6fa90e53d865693fd4fee0214f00000eb0aa2c',
    
     '3b083595f276e2f1353a535c32f0f59516fc9328f7673bb80262c4da11c93683afe6dcff8a7a83018d78f41498a0da4d141ebd39c361b1724f2b00000eb0aa2c',
    
     '0120961963495c4dab9470738b497eddde07b0d70b357795ad9554d7964761969a6d997205e17eada6fa84eb33dcfb11412f75e04c195001283900000eb0aa2c',
    
     '091065d52127bbc6e840e02f8e1316f1c4d9c92a23931c00cdbb8c158368852ef8fabd461b98812b51ec84e1ccc5c04aaa366fbafabec623bd3500000eb0aa2c',
    
     '7300cc61151b7af27a578e766f49bebb2de68c48b37a00df1030ae464f456928eedd035303e697208bf58217af728a2a346fda5c8aef0335b82e00000eb0aa2c'
    
     
    
    In [46]: x.edap.packets                                                                                                                                                                       
    
    Out[46]:
    
    ['5608305852bf2ffd61770e2c827542f20be0b0fcba09db916bd07e1734b04cb0352b1d278068064d19f033bfad6fa90e53d865693fd4fee0214f00000eb0aa2c',
    
     '3b083595f276e2f1353a535c32f0f59516fc9328f7673bb80262c4da11c93683afe6dcff8a7a83018d78f41498a0da4d141ebd39c361b1724f2b00000eb0aa2c',
    
     '0120961963495c4dab9470738b497eddde07b0d70b357795ad9554d7964761969a6d997205e17eada6fa84eb33dcfb11412f75e04c195001283900000eb0aa2c',
    
     '091065d52127bbc6e840e02f8e1316f1c4d9c92a23931c00cdbb8c158368852ef8fabd461b98812b51ec84e1ccc5c04aaa366fbafabec623bd3500000eb0aa2c',
    
     '7300cc61151b7af27a578e766f49bebb2de68c48b37a00df1030ae464f456928eedd035303e697208bf58217af728a2a346fda5c8aef0335b82e00000eb0aa2c']

### 帮助模式

    
    
    In [15]: x.help("")                                
    Currently supported methods:
    __________________________________________________________________________________________________________________________________________________________________
    
    Method               ||-->Description
    
    ----------------------------------------------------------------------------------------------------------------------------    
    MITMproxy            ||-->This method creates a connection to the RabbitMQ and listen on received messages on the todev queue
    
    ____________________________________________________________________________________________________________________________
    
    MITMproxyRQueues     ||-->This method reads from the queue todev and sends the request to the device its self.
    ____________________________________________________________________________________________________________________________
    
    SmartFuzz            ||-->This method is generates packets based on what it has learned from a sniff from either the host or the device
    ____________________________________________________________________________________________________________________________
    
    chgIntrfs            ||-->This method allows you to change and select another interface
    ____________________________________________________________________________________________________________________________
    
    clearqueues          ||-->this method clears all the queues on the rabbitMQ queues that are set up
    
    ____________________________________________________________________________________________________________________________
    
    clonedev             ||-->This method does not need any parameters it only saves a backup of the device incase you need to share it or use it later.
    
    ____________________________________________________________________________________________________________________________
    
    createctrltrsnfDB    ||-->creates a SQLite database containing values that were enumerated from control transfer enumeration
    
    ____________________________________________________________________________________________________________________________
    
    createdb             ||-->create the sqlite table and columns from usblyzer captures
    
    ____________________________________________________________________________________________________________________________
    
    decodePacketAscii    ||-->This method decodes packet bytes back to Ascii
    
    ____________________________________________________________________________________________________________________________
    
    describeFuzz         ||-->This method allows you to describe a packet and select which bytes will be fuzzed
    
    ____________________________________________________________________________________________________________________________
    
    devEnumCtrltrnsf     ||-->This method enumerates all possible combinations of a control transfer request
    
    ____________________________________________________________________________________________________________________________
    
    devReset             ||-->This method Resets the device
    
    ____________________________________________________________________________________________________________________________
    
    devWrite             ||-->To use this with a method you would write to a device make sure to run the startSniffReadThread(self,endpoint=None, pts=None, queue=None,channel=None)
    
    ____________________________________________________________________________________________________________________________
    
    devctrltrnsf         ||-->This method allows you to send ctrl transfer requests to the target device
    
    ____________________________________________________________________________________________________________________________
    
    deviceInfo           ||-->gets the complete info only for any usb connected to the host
    
    ____________________________________________________________________________________________________________________________
    
    deviceInterfaces     ||-->get all interfaces and endpoints on the device
    
    ____________________________________________________________________________________________________________________________
    
    devrandfuzz          ||-->this method allows you to create fixed or random size packets created using urandom
    
    ____________________________________________________________________________________________________________________________
    
    devseqfuzz           ||-->This method allows you to create sequential incremented packets and send them to the device
    
    ____________________________________________________________________________________________________________________________
    
    findSelect           ||-->This method enumerates all USB devices connected and allows you to select it as a target device as well as its endpoints
    
    ____________________________________________________________________________________________________________________________
    
    help                 ||-->AutogadgetFS Help method
    
    ____________________________________________________________________________________________________________________________
    
    hostwrite            ||-->This method writes packets to the host either targeting a software or a driver in control of the device
    
    ____________________________________________________________________________________________________________________________
    
    hstrandfuzz          ||-->this method allows you to create fixed or random size packets created using urandom and send them to the host queue
    
    ____________________________________________________________________________________________________________________________
    
    monInterfaceChng     ||-->Method in charge of monitoring interfaces for changes this is called from def startMonInterfaceChng(self)
    
    ____________________________________________________________________________________________________________________________
    
    newProject           ||-->creates a new project name if you were testing something else
    
    ____________________________________________________________________________________________________________________________
    
    releasedev           ||-->releases the device and re-attaches the kernel driver
    
    ____________________________________________________________________________________________________________________________
    
    removeGadget         ||-->This method removes the gadget from the raspberryPI
    
    ____________________________________________________________________________________________________________________________
    
    replaymsgs           ||-->This method searches the USBLyzer parsed database and give you the option replay a message or all messages from host to device
    
    ____________________________________________________________________________________________________________________________
    
    searchmsgs           ||-->This method allows you to search and select all messages for a pattern which were saved from a USBlyzer database creation
    
    ____________________________________________________________________________________________________________________________
    
    setupGadgetFS        ||-->setup variables for gadgetFS : Linux Only, on Raspberry Pi Zero best option
    
    ____________________________________________________________________________________________________________________________
    
    showMessage          ||-->shows messages if error or warn or info
    
    ____________________________________________________________________________________________________________________________
    
    sniffdevice          ||-->read the communication between the device to hosts
    
    ____________________________________________________________________________________________________________________________
    
    startMITMusbWifi     ||-->Starts a thread to monitor the USB target Device
    
    ____________________________________________________________________________________________________________________________
    
    startMonInterfaceChng||-->This method Allows you to monitor a device every 10 seconds in case it suddenly changes its interface configuration.
    
    ____________________________________________________________________________________________________________________________
    
    startQueuewrite      ||-->initiates a connection to the queue to communicate with the host
    
    ____________________________________________________________________________________________________________________________
    
    startSniffReadThread ||-->This is a thread to continuously read the replies from the device and dependent on what you pass to the method either pts or queue
    
    ____________________________________________________________________________________________________________________________
    
    stopMITMusbWifi      ||-->Stops the man in the middle thread between the host and the device
    
    ____________________________________________________________________________________________________________________________
    
    stopMonInterfaceChang||-->Stops the interface monitor thread
    
    ____________________________________________________________________________________________________________________________
    
    stopQueuewrite       ||-->stop the thread incharge of communicating with the host machine
    
    ____________________________________________________________________________________________________________________________
    
    stopSniffing         ||-->Kills the sniffing thread strted by startSniffReadThread()
    
    ____________________________________________________________________________________________________________________________
    
    usblyzerparse        ||-->This method will parse your xml exported from usblyzer and then import them into a database
    
    ____________________________________________________________________________________________________________________________
    
     
    
    In [16]: x.help("findSelect")                                                                                                                                                                 
    
    ****
    
    [+]Help for findSelect Method:
    
    [-]Signature: findSelect(self, chgint=None)
    
     
    
     
    
    [+]findSelect Help:
    
    This method enumerates all USB devices connected and allows you to select it as a target device as well as its endpoints

## 项目地址

AutoGadgetFS：【[ _GitHub传送门_](https://github.com/ehabhussein/AutoGadgetFS)】

## 参考资料

> [ _https://docs.agfs.io/_](https://docs.agfs.io/)
>
> [
> _https://downloads.raspberrypi.org/raspios_lite_armhf_latest_](https://downloads.raspberrypi.org/raspios_lite_armhf_latest)
>
> [ _https://www.balena.io/etcher/_](https://www.balena.io/etcher/)

