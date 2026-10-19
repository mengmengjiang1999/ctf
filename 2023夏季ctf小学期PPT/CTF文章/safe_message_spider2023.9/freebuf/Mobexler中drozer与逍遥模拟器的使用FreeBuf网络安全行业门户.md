### 1.drozer介绍

环境准备：Mobexler 、逍遥模拟器、drozer客户端。

### 2.工具下载

drozer客户端：

链接：<https://pan.baidu.com/s/1FBwV7RYy2OnX_TopczKRGg>

提取码：3344

Mobexler ：

链接：<https://pan.baidu.com/s/1CcrfyuJ5unG2ODM-63Jtsg>

提取码：3344

Mobexler 环境默认密码：12345

### 3.工具介绍

drozer

drozer 是一个全面的安卓安全审计和攻击框架。有助于确保您的组织正在开发或部署的 Android 应用程序和设备不会构成不可接受的风险水平。通过允许您与
Dalvik VM、其他应用程序的 IPC 端点和底层操作系统进行交互。

提供工具来帮助您使用和共享针对 Android 的公共漏洞。对于远程攻击，它可以生成 shellcode 来帮助您将 drozer
代理部署为远程管理员工具，最大限度地利用设备。

Mobexler

Mobexler是一个定制的虚拟机，旨在帮助Android和iOS应用程序的渗透测试。预装了几个开源工具，脚本，应用程序等，这些都是Android和iOS应用程序安全测试所必需的。android中的kali。

### 4 .网络环境搭建

将Mobexle与逍遥模拟器全部桥接到可上网网段，操作简单不再叨叨。

逍遥模拟器地址查看位置：设置-关于手机/平板-状态信息

![](https://image.3001.net/images/20220819/1660877704_62fefb8844ac24fd90301.png!small)

  

    
    
    Mobexle：192.168.179.15
    逍遥模拟器：192.168.179.16

### 5.测试环境搭建

5.1 drozer在Mobexler中已经集成无需安装。在逍遥模拟器安装drozer的客户端，在百度网盘中下载后直接拉入虚拟机或通过adb命令行安装。

5.2 安装后打开app，点击如下。

![](https://image.3001.net/images/20220819/1660877769_62fefbc9ba84a65725296.png!small)

5.3 将状态切换为enable

![](https://image.3001.net/images/20220819/1660877796_62fefbe4c0c61cc775d10.png!small)

5.4 由于是两台虚拟机需要远程连接。

进入逍遥模拟器后台路径后台开启监听端口

    
    
    D:\Program Files\Microvirt\MEmu  在下的安装路径，可以借鉴一下。

开启命令

    
    
    .\adb.exe tcpip 55555

![1660877884_62fefc3c04dd8fd21da7c.png!small?1660877884006](https://image.3001.net/images/20220819/1660877884_62fefc3c04dd8fd21da7c.png!small?1660877884006)

5.5进入Mobexler

使用adb连接到虚拟机，让两台虚拟机之间建立连接.

    
    
    adb connect 192.168.179.16:55555

输入命令转发端口，将两台虚拟机在上一步建立的连接转发到本地端口31415.

    
    
    adb forward tcp:31415 tcp:31415

![1660877892_62fefc44a06d1081df091.png!small?1660877892337](https://image.3001.net/images/20220819/1660877892_62fefc44a06d1081df091.png!small?1660877892337)

最后我们在终端中进入drozer的安装目录下，输入命令运行：

    
    
    drozer console connect

![1660877911_62fefc579b350eb649db2.png!small?1660877911481](https://image.3001.net/images/20220819/1660877911_62fefc579b350eb649db2.png!small?1660877911481)

