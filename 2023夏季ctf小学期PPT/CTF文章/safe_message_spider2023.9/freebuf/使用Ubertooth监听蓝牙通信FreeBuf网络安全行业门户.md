**作为没有使用过Ubertooth的小白，尝试从零开始搭建Ubertooth的环境，相关配置、依赖，来进行蓝牙数据的监听，配合Wireshark，进行蓝牙数据监听和分析。**  

## 环境说明

> VMWare版本：14.0.0 build-6661328
>
> 操作系统：Ubuntu 14.04.5 LTS
>
> Ubertooth软件版本：ubertooth 2018-12-R1
>
> Libbtbb版本：libbtbb 2018-12-R1
>
> Wireshark版本： Version 2.6.6 (Git v2.6.6 packaged as 2.6.6-1~ubuntu14.04.0)

本次编译安装的目的，是能够借助Wireshark去查看和分析监听到的蓝牙数据包，因此需要2个部分：Ubertooth（应用程序本体）和libbtbb（蓝牙基带库，源码中带有Wireshark插件）

实际上还有一部分需要关注，附带在Ubertooth下载的源码里，就是硬件对应的固件。由于固件是和软件配套的，因此在编译软件的时候需要给硬件刷入对应的固件，否则会报api不匹配的问题（下文中会说到）

## 软件编译

软件的编译部分其实很简单，使用Ubuntu系统的话官方git上是有相关说明的，而且很详细，可以傻瓜的照做。下面就简单说明一下。

首先先给出[官方WiKi (Build-Guide)](https://github.com/greatscottgadgets/ubertooth/wiki/Build-Guide)的链接，如果阅读能力强的可以直接看官方说明，下面的描述都以Ubuntu为例。

首先安装编译环境，如cmake, gcc等，一条命令：

    
    
    sudo apt-get install cmake libusb-1.0-0-dev make gcc g++ libbluetooth-dev \
    pkg-config libpcap-dev python-numpy python-pyside python-qt4
    

## libbtbb(蓝牙基带库)

接下来安装蓝牙基带库（Bluetooth Baseband
Library），下载源码并解压，这里也是借用了官方给出的命令，正好我安装的也是2018-12-R1的版本。

    
    
    wget https://github.com/greatscottgadgets/libbtbb/archive/2018-12-R1.tar.gz -O libbtbb-2018-12-R1.tar.gz
    tar -xf libbtbb-2018-12-R1.tar.gz
    

如果不用`wget`命令的话，也可以直接在[Releases页面](https://github.com/greatscottgadgets/libbtbb/releases)上下载（注意版本和文件名哦），然后手动解压~~

接下来按照官方的说明，`cd`命令进入解压好的文件夹，使用`mkdir`命令新建一个名为`build`的文件夹，用于编译源码。之后就是简单粗暴的`make`过程。不过注意，最后的`make
install`一定要用`sudo`去跑（长期用Kali已经忘记还有”以管理员身份运行“这回事了……）完整的命令如下：

    
    
    cd libbtbb-2018-12-R1
    mkdir build
    cd build
    cmake ..
    make
    sudo make install
    

如果没有报错，那就说明安装成功了。下面放出几张我build过程的截图：

![2019-06-17_135840.png](https://image.3001.net/images/20190711/1562814237_5d26a71d3ec0f.png!small)

![2019-06-17_135948.png](https://image.3001.net/images/20190711/1562814249_5d26a729dbc75.png!small)

![2019-06-17_140050.png](https://image.3001.net/images/20190711/1562814254_5d26a72e805d8.png!small)  

根据官方说明，首次安装的时候可能会报错，或者出现找不到lib库的情况，此时则需要在命令行中执行

    
    
    sudo ldconfig
    

即可，虽然不知道为什么，而且我安装的时候并未出现任何报错的提示。

## Ubertooth工具软件

Ubertooth工具软件就是指在命令行中输入`ubertooth-xxx`这样的命令能执行的那个玩意。编译的时候和libbtbb类似，用`wget`命令或者直接在[Release页面](https://github.com/greatscottgadgets/ubertooth/releases)进行下载，并解压。官方的命令如下：

    
    
    wget https://github.com/greatscottgadgets/ubertooth/releases/download/2018-12-R1/ubertooth-2018-12-R1.tar.xz
    tar xf ubertooth-2018-12-R1.tar.xz
    

后面的步骤也是一样的，新建build文件夹，在这个文件夹里cmake - make - make install完成安装：

    
    
    cd ubertooth-2018-12-R1/host
    mkdir build
    cd build
    cmake ..
    make
    sudo make install
    

需要注意的是，这里是在`host`文件夹下进行编译，解压出的源码中还有很多其他的文件夹，注意不要弄错了

同样的，这里官方也给了提示，如果首次编译或报找不到lib库的问题，请在命令行中输入：

    
    
    sudo ldconfig
    

至此，基带和工具全部都安装完成了，这时候插上Ubertooth，将其分配给虚拟机，并在命令行中输入`ubertooth-util
-v`即可查看到当前你的Ubertooth的固件版本。

![2019-06-17_142417.png](https://image.3001.net/images/20190711/1562814275_5d26a7431361c.png!small)

这里是我已经刷过了固件，所以显示的版本是2018-12-R1（原来没刷固件之前忘记截图了），能看到固件，说明btbb库和Ubertooth工具都安装成功了。

## Wireshark插件

根据官方libbtbb github的 [issus
50](https://github.com/greatscottgadgets/libbtbb/issues/50)，作者对Wireshark插件的问题进行了回答：  

  * 对于Wireshark 2.0之前的版本，需要编译`plugins-legacy`中的插件
  * 对于Wireshark 2.0 ~ 2.2 的版本，需要编译`plugins`中的插件
  * 对于Wireshark 2.2+的版本，无需编译任何插件即可，因为Wireshark官方已经自带了相关插件。

因此插件的编译步骤可以直接略过。

## 固件更新

在使用之前，需要对Ubertooth硬件中的固件进行更新。上面Ubertooth tools部分提到了`ubertooth-util
-v`命令可以查看到当前刷入的固件版本，同时有一个`API 版本`的问题，Ubertooth要求固件的API版本与Ubertooth
tools的版本一致，否则不能使用。

在Ubertooth
tools的源码中是包含了固件的，固件是`.dfu`格式的文件。源码中有可以直接用的固件，在`ubertooth-2018-12-R1/ubertooth-one-firmware-bin/bluetooth_rxtx.dfu`。更新固件的命令是：

    
    
    ubertooth-dfu -d bluetooth_rxtx.dfu -r
    

我在虚拟机中执行这一步的时候报错了，每次执行的时候都会尝试切换到DFU模式，然后USB显示无法识别，同时硬件上面的四个由深到浅的红色指示灯一直循环跑马灯。不知道这里是我虚拟机有问题，还是我的USB口有问题。

![2019-06-17_160303.png](https://image.3001.net/images/20190711/1562814292_5d26a7546193c.png!small)

尝试了很久都不成功之后，找了一台macbook，安装ubertooth tool，执行上面的命令，成功刷入。

这里官方给出了一个troubleshooting，如果有报错`libUSB Error: Command Error:
(-1)`，或者硬件上面四个灯跑马灯的话，需要重新编译固件，就要用到`ubertooth-2018-12-R1/firmware`文件夹的内容了，编译命令如下：

    
    
    cd ubertooth-2018-12-R1/firmware
    make clean all && make
    ubertooth-dfu -r -d bluetooth_rxtx/bluetooth_rxtx.dfu
    

在之前一直提示`Unable to find
Ubertooth`错误的时候，我也尝试编译了固件，证明并不是固件的问题。由于没有成功刷入编译的固件，此部分不再赘述。

## 抓包验证

## Wireshark设置

到了这一步，前期准备工作就都完成了。现在需要把Ubertooth和Wireshark进行联动，将Ubertooth收集到的数据传到Wireshark进行解析。这里主要参考[官方Wiki](https://github.com/greatscottgadgets/ubertooth/wiki/Capturing-BLE-in-Wireshark)，步骤如下：

> 1.在终端中运行命令：`mkfifo /tmp/pipe`
>
> 2.打开Wireshark，选择 'Capture -> Options' 对抓包接口进行设置
>
> 3.点击右下角 ‘Manage Interfaces’ 对接口进行管理
>
> 4.切换到 'Pipes' 选项卡
>
> 5.保存设置，选中 '/tmp/pipe' 并点击开始
>
> 6.此时，在终端中运行命令：`ubertooth-btle -f -c /tmp/pipe`

![2019-06-17_162401.png](https://image.3001.net/images/20190711/1562814350_5d26a78e58160.png!small)

切回Wireshark，应该可以看到滚动的数据包了。

这里有一点需要注意，“mkfifo /tmp/pipe”
命令需要在所有步骤前进行，即先创建pipe这个文件，再设置wireshark读取，最后用Ubertooth-btle命令写入，顺序错了是会不成功的。

## 一些小问题

### DLT=147, check your Preferences->Protocols->DLT_USER

这个问题我的个人理解是Wireshark没有能识别出这类数据包的具体类别，因此需要手动指定一下。

这个是没进行操作之前（有报错的时候）。

![2019-06-17_151144.png](https://image.3001.net/images/20190711/1562814363_5d26a79ba82dd.png!small)

步骤很简单：

> 1.点击 Edit -> Preference (编辑 -> 首选项)；
>
> 2.在左侧选择 `Protocol`下的`DLT_USER`选项；
>
> 3.点击`Edit`按钮；
>
> 4.点击左下角的 “+” 添加一条记录，在`DLT`处选择DLT=147，`Payload protocol`部分双击修改，填入btle，点击OK保存。

此时显示就正常了。

![2019-06-17_163721.png](https://image.3001.net/images/20190711/1562814379_5d26a7ab796ec.png!small)

这是修复过的样子：

![2019-06-17_163522.png](https://image.3001.net/images/20190711/1562814393_5d26a7b95388c.png!small)

### undefined symbol: new_create_dissector_handle

这个问题是在Wireshark 2.2+版本下按照官方Build
Guide编译插件后造成的。原因在上面的插件编译那一节已经说到了，2.2+版本可以直接用，不需要进行任何插件的编译工作。

因为折腾了很久才明白各个版本之间的区别，因此还是在这里提一句，记录一下。

下面是这个错误报错的截图：

![2019-06-18_193005.png](https://image.3001.net/images/20190711/1562814400_5d26a7c0ac8a6.png!small)

