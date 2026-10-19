[YARD Stick One](https://greatscottgadgets.com/yardstickone/)是一款低于 1 GHz 以下的
USB 无线收发器，基于德州仪器（TI）CC1111。它与 [IM-Me](http://ossmann.blogspot.com/2010/03/16-pocket-spectrum-analyzer.html)相同的无线电电路。现在，当你通过 USB 将 YARD Stick One 连接到计算机时，可以轻松定制 IM-Me
固件的无线电功能。你可以将 YARD Stick One 用于进行各种遥控信号的重放，汽车遥控锁的安全研究等。主要性能规格如下：

  * 半双工发送和接收

  * 官方工作频率：300-348 MHz，391-464 MHz 和 782-928 MHz

  * 非官方工作频率：281-361 MHz，378-481 MHz 和 749-962 MHz

  * 调制方式：ASK，OOK，GFSK，2-FSK，4-FSK，MSK

  * 数据速率高达 500 kbps

  * 全速 USB 2.0

YARD Stick One 带有 [RfCat](https://github.com/atlas0fd00m/rfcat)安装的固件，由
[atlas](https://twitter.com/at1as)提供。RfCat 允许从交互式 Python Shell
或计算机上运行的自己的程序控制无线收发器。YARD Stick One 还安装了[CC
Bootloader](https://github.com/AdamLaurie/CC-Bootloader)，因此你可以升级 RFCat
或安装自己的固件，而无需任何其他编程硬件。不包括天线。建议将[ANT500](https://www.greatscottgadgets.com/ant500/)用作
YARD Stick One 的启动天线。

YARD Stick One 最初基于 [ToorCon 14
Badge](https://www.greatscottgadgets.com/tc14badge/)设计，具有 CC1111 平台以前没有的几个功能：

  * SMA 母天线连接器，用于 [ANT500 ](https://www.greatscottgadgets.com/ant500/)等外部天线

  * 接收放大器，提高灵敏度

  * 发射放大器，输出功率更高

  * 在整个工作频率范围内均具有强大的 RF 性能

  * 低通滤波器，用于在 800 和 900 MHz 频段工作时消除谐波

  * 天线端口电源控制，可兼容为 [HackRF One ](https://www.greatscottgadgets.com/hackrf/)设计的天线端口附件

  * 兼容 [GoodFET](http://goodfet.sourceforge.net/)的扩展和编程头

  * 兼容 [GIMME](http://ossmann.blogspot.com/2012/10/programming-pink-pagers-in-style.html)的编程测试点

  

有关文档和开源设计文件，请访问[项目Wiki](https://github.com/greatscottgadgets/yardstick/wiki)。

  

## 搭建环境

以下测试环境在 ubuntu 16.04 下搭建

软件工具：RFcat、Osmocom、Inspectrum

设备：

YARD Stick One （重放信号）

RTL-SDR 电视棒 （捕获信号）

无线门铃，使用 ASK/OOK 调制的 1GHz 以下信号运行的设备。芯片是
[HS1527](https://datasheetspdf.com/datasheet/HS1527.html)， 发射频率为 433Mhz 。

  

## 安装 rfcat

下载 [rfcat](https://github.com/atlas0fd00m/rfcat)源码

    
    
    $ git clone https://github.com/atlas0fd00m/rfcat

需要安装 python-usb，libusb-1.0.0，make 和 sdcc 依赖和库。

    
    
    $ sudo apt install python-usb libusb-1.0.0 make sdcc  
    $ cd rfcat  
    $ pip install -r requirements.txt

> 其中 PySide2 安装时可能会碰到 “ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE
> REQUIREMENTS FILE. If you have updated the package versions, please update
> the hashes. Otherwise, examine the package contents carefully; someone may
> have tampered with them.”
>
> 可通过 wget 将 PySide2-5.15.1-5.15.1-cp27-cp27mu-manylinux1_x86_64.whl
> 下载到本地进行安装（pip install PySide2-5.15.1-5.15.1-cp27-cp27mu-> manylinux1_x86_64.whl）。

当加密狗显示在操作系统上时，如果你是非ROOT用户则必须具有对加密狗的读/写访问权限，对于大多数 Linux 发行版，这意味着你必须是“
dialout”组的成员。

    
    
    $ sudo usermod -a -G sudo $USER  
    $ su - $USER

还需要永久的符号链接到 USB 串行设备，以便在需要时与 CHRONOS，DONSDONGLE或 YARDSTICKONE 引导加载程序进行通信。

    
    
    $ sudo cp etc/udev/rules.d/20-rfcat.rules /etc/udev/rules.d  
    $ sudo udevadm control --reload-rules

安装客户端

    
    
    $ sudo python setup.py install

运行时，启用频谱仪发生的错误

> qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though
> it was found. This application failed to start because no Qt platform plugin
> could be initialized. Reinstalling the application may fix this problem.
>
> 可根据 <https://blog.csdn.net/zhanghm1995/article/details/106474505>提出的解决方案解决
    
    
    $ export QT_DEBUG_PLUGINS=1  
    $ sudo apt-get install libxcb-xinerama0

  

## 安装 gr-osmosdr

安装以后可以使用 **osmocom_fft** 命令进行频率录制。

    
    
    $ sudo apt install gr-osmosdr

运行后，界面如下

    
    
    $ osmocom_fft

![image-20200914163705146.png](https://image.3001.net/images/20210111/1610350075_5ffbfdfb38b01ee0c0493.png!small)

## 安装 inspectrum

Inspectrum是一款分析无线信号的工具，基于Linux和OSX。它兼容GNURadio、Osmocom_fft还有各类SDR设备导出的IQ文件格式（例如RTL-SDR、HackRF、BladeRF），界面如下图。 安装
Inspectrum，可参考Wiki：<https://github.com/miek/inspectrum/wiki/Build>

    
    
    # 安装依赖  
    $ sudo apt-get update  
    $ sudo apt-get install qt5-default libfftw3-dev cmake pkg-config  
    # 手动安装 libliquid1d 和 libliquid1d-dev  
    $ cd ~/Downloads  
    $ wget http://mirrors.kernel.org/ubuntu/pool/universe/l/liquid-dsp/libliquid1d_1.3.1-1_amd64.deb  
    $ dpkg -x libliquid1d_1.3.1-1_amd64.deb ./  
      
    $ wget http://mirrors.kernel.org/ubuntu/pool/universe/l/liquid-dsp/libliquid-dev_1.3.1-1_amd64.deb  
    $ dpkg -x libliquid-dev_1.3.1-1_amd64.deb ./  
      
    $ sudo cp  usr/lib/x86_64-linux-gnu/libliquid.* /usr/lib/x86_64-linux-gnu/  
    $ sudo cp -ar usr/include/liquid /usr/include/  
      
    # 安装编译工具  
    sudo apt-get install build-essential git  
      
    # 克隆存储库并编译安装 inspectrum  
    $ cd ~/Downloads  
    $ git clone https://github.com/miek/inspectrum.git  
    $ cd inspectrum  
    $ mkdir build  
    $ cd build  
    $ cmake ..  
    $ make  
    $ sudo make install

![image-20200914163916011.png](https://image.3001.net/images/20210111/1610350076_5ffbfdfc6bc2ccfc63d09.png!small)

## rfcat 接收测试

将 YARD Stick One 插入计算机 USB，然后连接到虚拟机上，选择 **虚拟机 - > 可移动设备 -> OpenMoko YARD Stick
One -> 连接(断开与主机的连接)**。

![image-20200910155416988.png](https://image.3001.net/images/20210111/1610350077_5ffbfdfd32c5b639ad2c4.png!small)

连接后，执行`lsusb`命令可以查看 usb 设备

![image-20200910155841040.png](https://image.3001.net/images/20210111/1610350078_5ffbfdfe1de09b47a0ba7.png!small)

运行 rfcat 进行交互式 Python Shell 进行测试

    
    
    $ sudo rfcat -r

![image-20200910172118884.png](https://image.3001.net/images/20210111/1610350078_5ffbfdfee1885d3216953.png!small)

如图，该命令行环境下有一个简单使用帮助：有一个加密狗的全局对象 d，你可以通过该对象与 YARD Stick One 设备进行交互：

  *  **d.setFreq(freq)** ：设置我们要传输的频率，其中“ freq” 替换成频率，例如d.setFreq(433000000)

  *  **d.setMdmModulation(modulation)** ：设置数字调制模式，例如遥控器是ASK / OOK，所以我使用d.setMdmModulation(MOD_ASK_OOK)。

  *  **d.makePktFLEN(length)** ：使用固定的数据包长度时，可以使用它指定数据包的大小，因此，如果发送的是“\xDE\xAD\xBE\xEF”，则为d.makePktFLEN(4)。

  *  **d.setMdmDRate(baud)** ：此函数设置波特率或一次设置多少数据，对于我的遥控器，它约为4800波特，因此我使用d.setMdmDRate(4800)

  *  **d.setMaxPower()** ：默认情况下，带有 rfcat 固件的 CC1111EMK 以低功率发送信号。如果运行此函数，则会将功率设置为最大，这会使信号传播得更长一些。

  *  **d.RFxmit( <bytestring>)**：该函数可以正常使用字符串，但出于处理数字等问题，发送字节串要容易得多，如果发送的是0xDEADBEEF，则应该使用d.RFxmit('\xDE\xAD\xBE\xEF')

  

探测信号，使用 d.specan(freq)，我这个遥控的频率为
433Mhz，使用此遥控的频率（433000000）作为参数，运行后弹出一个频谱扫描仪窗口，如图，可以看到 433Mhz 在这个扫描范围内。

    
    
    In [1]: d.specan(433000000)

![image-20200914160522592.png](https://image.3001.net/images/20210111/1610350080_5ffbfe0058749e27ae217.png!small)

按下门铃遥控后，设备成功扫描到该信号，频率为 434.257907Mhz

![image-20200914160628301.png](https://image.3001.net/images/20210111/1610350081_5ffbfe017aeb5bedf03f0.png!small)

也可以捕获信号并以数据包显示出来，依次设置参数（设置频率上面的峰值434257907hz）。

    
    
    In [2]: d.setFreq(434257907)  
      
    In [3]: d.setMdmModulation(MOD_ASK_OOK)  
      
    In [4]: d.setMdmDRate(4800)  
      
    In [5]: d.setMaxPower()  
      
    In [6]: d.lowball() // 这会将无线电配置为尽可能低的过滤级别，从而有可能使整个无线电噪声作为数据通过。  
    In [7]: d.RFlisten() //运行 d.RFlisten() 可以持续抓取数据传输，并以 HEX 和 ASCII 格式显示它们。按 Enter 将停止此命令，使用户返回交互式 shell。  
      
    Entering RFlisten mode...  packets arriving will be displayed on the screen  
    (press Enter to stop)  
    ...  
    (1599788652.686) Received:  ffffffffffffffffdffffffffffffffffffeffffdfffffffffffffffffffffffffffffffffffffffffffffffff7ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffdfffffffff7ffffffffffff7ffffffffffbffffffffffffbfffffffff00002000000e4c3fdc7861ffbff7ffbc3ffbc3ffef0ffffe7f3e1fffbe9e2f4fffef87c00004c8002fffbe1fffdf8f87c3fffefffffbfffff7f9fffffdfe1fffffeff0fffffdfe1ff3bfd3fffffffffce36fe17fffffa3ffffffffffcfbbe0000001040000002c0840620df7602580fbdffffff1aeffffffffffeffffffffffffffffff7ffffffffffffffffffff  | ..................................................................................................................L?.xa.....?........>..../O......../........................................o....................,.@b..`%................................  
    (1599788656.259) Received:  fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff3edbebf7cbffffffffffffffffffdffffffffffffffffffffdffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffc00000000008a21c020c28388c5efff387ffde1fff3c3fffbe1e1e1fffefa7c7c3fffefc7e0002710094fffe7c3fffefc3e1f8fffff3fffff7fffffdfe1ffffffb40325689d5ef0fff9fffdff0ff87f83fffffffdffc3fe3ff0fffffffff400000000000000003fcc3ff70e1c3ff7ff7ff387ffbc3fff7c7fff7d7e1f0ffffdfc7f0fe9ffffffbff7ffc02a281c  | ......................................................|............................................................!........8..............||?.....'..O......>....?............%h.^.................?..............?.?...?.......?.|..}~...............*(.

但通过观察数据包并没有发现什么规律，所以用接下来说的方法进行抓取。

## osmocom 捕获信号

将 SDR ，启动 osmocom 捕获信号，`-f`指定频率，`-s`设置采样率。

    
    
    $ osmocom_fft -f 43425e4 -s 8e6

点击右下角进行 REC 按钮进行录制捕获，它将产生一个`.cfile`的信号文件。

![image-20200916144646758.png](https://image.3001.net/images/20210111/1610350082_5ffbfe0280a3f4824e555.png!small)

然后按下遥控，并按住 2 秒后松开，再次点击右下角`stop`按钮，关闭窗口后在终端下，可以看到生成的信号文件路径。

![image-20200916152417724.png](https://image.3001.net/images/20210111/1610350083_5ffbfe03883a7fcb47234.png!small)

## inspectrum 处理信号

使用 inspectrum 加载信号文件

    
    
    $ inspectrum /tmp/name-f4.342500e+08-s2.000000e+06-t20200916152347.cfile

加载后，将采样率设置成之前录制使用的`-s`参数（本例为8e6），并调整 FFT
大小和缩放以更好地了解频谱图。通常，先缩小一点以查看我要处理的内容，在这种情况下（通常是使用基本OOK进行处理）是一个简单的重复信号。

![image-20200916152448998.png](https://image.3001.net/images/20210111/1610350084_5ffbfe04da4e60d7393f3.png!small)

现在，通过滚轮选择放大开头的那部分，并右键 Add derived plot -> Add threshold plot 添加阈值图，以更好地可视化信号。

![image-20200916152529356.png](https://image.3001.net/images/20210111/1610350092_5ffbfe0c26e3daa777907.png!small)

将红线对准信号的中心，下方会显示振幅图。通过调整红线两侧的白线，离红线越近，下面振幅图的峰值更接近直线。

![image-20200916152557309.png](https://image.3001.net/images/20210111/1610350098_5ffbfe123923fd6e45beb.png!small)

在左侧控制栏下的 Time selection 可对波形进行划分，启用 Enable cursors，这里我们以一位 **“内码”**
信号的宽度为标准。接着对Symbols数值进行递增，直至囊括一帧信号的波形区域。

![image-20200916153335471.png](https://image.3001.net/images/20210111/1610350104_5ffbfe18a5ff5e0c6484f.png!small)

关于内码，可以参考 [HS1527
芯片手册](https://datasheetspdf.com/datasheet/HS1527.html)，HS1527码型如下：

![image-20200915172212602.png](https://image.3001.net/images/20210111/1610350108_5ffbfe1c926996d5750ba.png!small)

现在我们知道在 inspectrum 里面看到的信号是什么意思了，总结下：一帧信号的编码格式为 **“≥8位同步码 + 20位内码 + 4位数据码”**
。本例一共为 32 位码。

![image-20200916153901578.png](https://image.3001.net/images/20210111/1610350110_5ffbfe1e56d1fe380a919.png!small)

选择 Extract symbols -> To stdout 提取 Symbols。

![image-20200916153933132.png](https://image.3001.net/images/20210111/1610350116_5ffbfe2416c5b9f84a41a.png!small)

提取后，在终端上会显示以下内容

![image-20200916154002747.png](https://image.3001.net/images/20210111/1610350120_5ffbfe2878f64fbc7ed9f.png!small)

在前面 rfcat -r 的交互命令行下将 symbol 解码成 32
位码`00000000101000111010101000100010`，再参考上面芯片手册截图中的同步位和内码将按高低电平宽度比换算成二进制位：`10000000000000000000000000000000111010001110100010001000111011101110100011101000111010001110100010001000111010001000100011101000`

![image-20200916162639232.png](https://image.3001.net/images/20210111/1610350121_5ffbfe29555ed9a98734b.png!small)

最后，再将二进制位转为十六进制，使用 **d.RFxmit()** 就可以使用 yardstickone 进行重放信号，运行以后，这时门铃会响起。

![image-20200916160723616.png](https://image.3001.net/images/20210111/1610350122_5ffbfe2a5de8aa94ca445.png!small)

整理成脚本

    
    
    from rflib import *  
    import sys, bitstring  
      
    def init(device):  
    device.setMdmModulation(MOD_ASK_OOK)  
    device.setFreq(433920000)  
    device.setMdmSyncMode(0x00)  
    device.setMdmNumPreamble(0)  
    device.setPktPQT(0)  
    device.setMaxPower()  
    device.setMdmDRate(2450)  
      
    def get_bitstring(*symbols):  
    bs = ''  
    for s in symbols:  
    if s > 0:  
    bs += '1'  
    else:  
    bs += '0'  
    print bs  
      
    def bits2bytes(bit_string):  
    return bitstring.BitArray(bin=str(bit_string.strip())).tobytes()

## rfcat 重放信号

终端执行 **bits2bytes()**
方法，将`10000000000000000000000000000000111010001110100010001000111011101110100011101000111010001110100010001000111010001000100011101000`转换为字节，最后执行
rfcat 的 d.RFxmit() 方法，进行重放信号（循环 10 次以上），运行后门铃响起

![image-20200915173032091.png](https://image.3001.net/images/20210111/1610350123_5ffbfe2b43fd25369ca49.png!small)

  

参考链接

[LimeSDR 无线信号重放攻击和逆向分析 -BG7YWL](https://blog.csdn.net/oYaseng/article/details/82353160)

My quickest and easiest method for OOK signal decoding & replication in 2016 -Gareth

[ASK/L(OOK)/Listen! – Basic Signal Decoding and Replay - Mike
Czumak](https://www.securitysift.com/ook-signal-decoding-replay/)

[HACKING FIXED KEY REMOTES -Andrewmohawk](https://www.andrewmohawk.com/2012/09/06/hacking-fixed-key-remotes/)

[HS1527 Datasheet PDF](https://datasheetspdf.com/datasheet/HS1527.html)

  

（本文为原创内容，转载请注明来源……）

![](https://image.3001.net/images/20210111/1610354123_5ffc0dcb14a1d4042137d.png!small)  

