## **前言**

了解过串口调试的一些基本信息，我们尝试通过串口拿设备shell。刚好，我们手上有树莓派4B的板子，决定使用树莓派4B进行测试。但初次尝试失败了，主要是因为树莓派4B的串口被默认分配给与蓝牙模块通信了。所以这篇文章主要是讲通过交换映射关系，开启树莓派串口调试，拿到shell。

##  **准备工具**

1.树莓派4B

2.串口小板+杜邦线

3.xshell（远程登录工具，可用友善串口调试助手等工具代替）

##  **树莓派配置修改**

树莓派4B的一共包含两个串口，一个是硬件串口（/dev/ttyAMA0），一个是mini串口（/dev/ttyS0）。

在所有的树莓派板卡中都通过排针将一个串口引出来了，目前只有树莓派3代，引出的串口默认是CPU的那个硬件串口。而在树莓派4B中，由于板载蓝牙模块，因此这个硬件串口被默认分配给与蓝牙模块通信了，而把那个mini串口默认分配给了排针引出的GPIO
Tx Rx。

所以要想使用树莓派4B进行串口调试，需要先交换映射关系。

###  **查看设备文件**

    
    
    ls -l /dev

![1661247285_63049f3554ac4962ea342.png!small?1661247285997](https://image.3001.net/images/20220823/1661247285_63049f3554ac4962ea342.png!small?1661247285997)

这时mini UART没打开串口功能的情况，只有serial1（蓝牙）默认使用是PL011 UART(ttyAMA0)硬件串口。

###  **打开mini UART串口**

    
    
    sudo raspi-config

![1661247330_63049f6266ac02c682941.png!small?1661247331273](https://image.3001.net/images/20220823/1661247330_63049f6266ac02c682941.png!small?1661247331273)

选择Interfacing Options

![1661247355_63049f7b65a78c131fc10.png!small?1661247356104](https://image.3001.net/images/20220823/1661247355_63049f7b65a78c131fc10.png!small?1661247356104)

选择serial

再选择 是，启用串口登录功能，将串口用于通信。

再选择 是，启动串口硬件。

再次查看设备文件：

![1661247378_63049f9252e5829ff23ae.png!small?1661247379016](https://image.3001.net/images/20220823/1661247378_63049f9252e5829ff23ae.png!small?1661247379016)

serial0（GPIO串口已启用）使用的是ttyS0设备（mini串口），serial1（蓝牙）使用的是ttyAMA0设备（硬件串口PL011）。

###  **交换映射关系**

编辑该文件：

    
    
    sudo gedit /boot/config.txt

在末尾添加一行代码：

    
    
    dtoverlay=pi3-miniuart-bit

修改完以后重启：

    
    
    sudo reboot

再看串口映射关系，已经换回来了：

![1661247440_63049fd0e6bfc7af6436c.png!small?1661247441453](https://image.3001.net/images/20220823/1661247440_63049fd0e6bfc7af6436c.png!small?1661247441453)

##  **串口连接**

针脚1 = 3.3V

针脚6 = GND

针脚8 = TXD

针脚10 = RXD

![1661247481_63049ff9106ac9c866b5b.png!small?1661247481873](https://image.3001.net/images/20220823/1661247481_63049ff9106ac9c866b5b.png!small?1661247481873)

###  **接线**

3.3V 接 3.3V （可不接，有USB供电）

GND 接 GND

TXD 接 TXD

RXD 接 RXD

![1661247581_6304a05d308583c642c82.jpg!small?1661247582292](https://image.3001.net/images/20220823/1661247581_6304a05d308583c642c82.jpg!small?1661247582292)

![1661247597_6304a06d85ffbd1114fae.jpg!small?1661247599226](https://image.3001.net/images/20220823/1661247597_6304a06d85ffbd1114fae.jpg!small?1661247599226)

###  **通电**

先接通树莓派电源，再将串口小板接入笔记本

###  **查看COM端口**

这里对应的是COM5

如果无法查看端口，自行安装驱动

![1661247671_6304a0b72aed436d878a8.png!small?1661247671961](https://image.3001.net/images/20220823/1661247671_6304a0b72aed436d878a8.png!small?1661247671961)

###  **xshell连接**

打开xshell，新建连接，选择协议为SERIAL

![1661247728_6304a0f036d2f20a45925.png!small?1661247728856](https://image.3001.net/images/20220823/1661247728_6304a0f036d2f20a45925.png!small?1661247728856)

然后配置串口，端口号为刚才查到的，这里为COM5，波特率默认是115200（树莓派里可以修改）

![1661247745_6304a1015a3050127893d.png!small?1661247745977](https://image.3001.net/images/20220823/1661247745_6304a1015a3050127893d.png!small?1661247745977)

串口登录成功，成功获取shell

![1661247764_6304a1144c2b9d2830049.png!small?1661247764919](https://image.3001.net/images/20220823/1661247764_6304a1144c2b9d2830049.png!small?1661247764919)

 **参考文章**

<https://blog.csdn.net/playmakerDJ/article/details/105399782>

<https://blog.csdn.net/qq_41208487/article/details/120863092>

<https://blog.csdn.net/weixin_45437140/article/details/102971270>

  

