**今天给大家介绍是一款名叫IoT-Implant-Toolkit的开源工具，这款工具专门针对物联网设备而设计，可直接向目标IoT设备植入木马，广大研究人员可利用这款工具来测试IoT设备的安全性。**

![一款针对IoT设备的木马植入工具](https://image.3001.net/images/20190314/1552539103_5c89dddfb35fc.png!small)

## IoT-Implant-Toolkit

IoT-Implant-Toolkit是一个整合了多种实用工具的木马植入框架，其中涉及到固件修改、串口调试、软件分析和间谍客户端植入等等，可帮助研究人员对IoT设备进行恶意软件注入研究。该工具简单易用，且提供了类Shell环境的可扩展能力。在IoT-Implant-Toolkit的帮助下，复杂的IoT恶意软件植入操作也可以变得轻松简单。

在我们的研究过程中，我们利用IoT-Implant-Toolkit成功在八台设备上植入了木马，其中包括智能扬声器、摄像头、行车记录仪和移动翻译器等等。

### 工具操作演示

![一款针对IoT设备的木马植入工具](https://image.3001.net/images/20190314/1552539166_5c89de1ee4187.gif!small)

## 如何使用IoT-Implant-Toolkit

### 工具安装

确保你已经安装好了git、Python3和setuptools。

如果你需要处理/播放音频信息的话，你还需要安装alsa、sox和ffplay。在Ubuntu 18.04上你可以运行下列命令：

    
    
    $sudo apt install sox ffmpeg

从项目的GitHub代码库上下载源代码：

    
    
    $ git clone https://github.com/arthastang/IoT-Implant-Toolkit.git

配置环境并安装依赖组件：

    
    
    $ cd IoT-Implant-Toolkit/
    $ python3 setup.py install

### 工具运行

![一款针对IoT设备的木马植入工具](https://image.3001.net/images/20190314/1552539206_5c89de46cc26a.png!small)

 **工具支持下列三种命令：**

> list：显示所有可用插件；
>
> run：运行指定插件，命令样本："run [插件名] [参数]"；
>
> exit：退出；

## 功能介绍

该框架中的每一款软件都以插件的形式运行，因此该工具的可扩展性非常高，而且使用起来也非常方便。

目前该工具自带了11款插件，主要分类四大类，其中包括串口调试、固件封装/解封装、软件分析和间谍软件植入。

### 插件列表

**分类** **** |  **工具名** **** |  **描述** **** |  **资源引用** ****  
---|---|---|---  
串口调试  |  pyserial |  Modem控制和终端模拟工具 |
[https://github.com/pyserial/pyserial](https://github.com/pyserial/pyserial)  
串口调试  |  baudrate.py |  寻找正确的baudrate |
[https://github.com/devttys0/baudrate](https://github.com/devttys0/baudrate)  
固件封装/解封装  |  mksquashfs |  可创建和提取Squashfs文件系统 |
[https://github.com/plougher/squashfs-tools](https://github.com/plougher/squashfs-tools)  
固件封装/解封装  |  mkbootimg_tools |  针对Android平台boot.img的解封装&封装工具 |
[https://github.com/xiaolu/mkbootimg_tools](https://github.com/xiaolu/mkbootimg_tools)  
固件封装/解封装  |  cramfs |  制作cramfs 文件系统 |
[https://sourceforge.net/projects/cramfs/files/cramfs/1.1/](https://sourceforge.net/projects/cramfs/files/cramfs/1.1/)  
固件封装/解封装  |  mountimg |  针对Android system.img&data.img 的ext4 文件系统处理工具 |
<https://github.com/arthastang/IoT-Implant-Toolkit>  
软件分析  |  setools-android |  针对Android应用的分析工具 |
[https://github.com/xmikos/setools-android](https://github.com/xmikos/setools-android)  
软件分析  |  crosscomplie |  针对ARM的crosscompile工具集 |
<https://github.com/arthastang/IoT-Implant-Toolkit>  
软件分析  |  odex unpack |  Android 应用：Odex转smali  |
<https://github.com/arthastang/IoT-Implant-Toolkit>  
代码植入  |  spy client&server |  稳定的间谍客户端+服务器 |
<https://github.com/arthastang/IoT-Implant-Toolkit>  
代码植入  |  denoise tool |  用于音频处理 |  <https://github.com/arthastang/IoT-Implant-Toolkit>  
  
### 创建新插件

代码结构：

    
    
    --IoT-Implant_toolkit.py         #Startup script
    --outputs/                       #Default folder ofoutputs
    --toolkit/                      
      |---core/                     
          |---basic/                 #Basic plugin class defination
          |---cli/                   #Shell-like cli defination
          |---toollist/              #Auto updating toollist ofplugins
      |---plugins/                  
          |---firmware/              #Plugins for firmwaremodification
          |---implant/               #Plugins for generate spy programs
          |---serialport/            #Plugins for serial port debugging
          |---software/              #Plugins for software analysisespecially for Android
      |---tools/                     #Other tools

在相应分类目录中创建[newplugin].py，并定义init属性来添加新的插件，IoT-Implant-Toolkit将会自动配置并加载目录中的新插件。

## 其他工具

### 硬件工具

项目的HardwareTools/目录中还提供了很多针对恶意软件植入研究的硬件工具。

**工具名** **** |  **描述** ****  
---|---  
Soldering Iron |  Solder 工具  
Solder Wire |  Solder 工具  
Solder Paste |  Solder 工具  
Solder Wick |  Solder 工具  
Hot Air Gun |  Solder 工具  
Reballing Tool |  Reballing 工具  
usb to ttl |  调试/ 控制台线缆  
Dupont Wire |  电线  
EPROM Burner Programmer |  Burner 编程器  
  
### 其他实用软件工具

由于时间问题，我们现在还没有添加太多的功能插件，下面这个列表中的工具虽然现在不适用于我们这款框架，但也许会对大家有用。

**分类** **** |  **工具名** **** |  **描述** **** |  **资源引用** ****  
---|---|---|---  
固件分析 |  binwalk |  简单易用的固件镜像分析、逆向分析和提取工具 |
[https://github.com/ReFirmLabs/binwalk](https://github.com/ReFirmLabs/binwalk)  
固件分析 |  firmware mod kit |  用于提取和重建Linux固件镜像的工具 |
[https://github.com/rampageX/firmware-mod-kit](https://github.com/rampageX/firmware-mod-kit)  
交叉编译 |  buildroot |  针对arm mips powerpc的交叉编译工具 |
[https://buildroot.org/](https://buildroot.org/)  
  
## 项目地址

IoT-Implant-Toolkit：【[GitHub传送门](https://github.com/arthastang/IoT-Implant-Toolkit)】

 *** 参考来源：[arthastang](https://github.com/arthastang/IoT-Implant-Toolkit)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

