***本文作者：barcating，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 前言

 **本文主要介绍 Nordic 的[nRF51
Dongle](https://www.nordicsemi.com/eng/Products/nRF51-Dongle)
(PCA10031)工具的安装和配置，以及使用该工具配合Wireshark软件，针对蓝牙BLE通信数据进行抓包合协议分析。文中使用的硬件如图所示。**

![nRF51 Dongle
](https://image.3001.net/images/20181108/1541643780_5be39e04c1642.png!small)

## 一、软件安装

（1）下载nRF Sniffer software v2.x 或者更高的版本，可以在NordicSniffer产品里下载 Sniffer
Download，这里我们选择下载[nRF-Sniffer-v2](https://www.nordicsemi.com/eng/Products/Bluetooth-low-energy/nRF-Sniffer)。

![一、软件安装](https://image.3001.net/images/20181108/1541643883_5be39e6b9e669.png!small)

该文件里面包含了Segger-jlink工具、Dongle固件包、Sniffer的Python源码程序。打开文件夹，其主要文件如下。

![主要文件](https://image.3001.net/images/20181108/1541643889_5be39e71e5386.png!small)

![主要文件](https://image.3001.net/images/20181108/1541643895_5be39e77ee477.png!small)

（2） 安装[Wireshark v2.4.2 ](https://www.wireshark.org/download.html)或者更高的版本；

（3） 操作系统：运行Wireshark的环境，Windows 7或者更高版本。

（4） SEGGER J-Link v6.16c（用于下载 Sniffer工具固件），Sniffer software
v2.x里面已经提供了segger_jlink软件，直接安装即可。

![直接安装](https://image.3001.net/images/20181108/1541644030_5be39efea7ac6.png!small)

（5）
安装[Python2.7.x](https://www.python.org/downloads/)，安装Python运行环境，运行上面提及的Sniffer软件。（安装时勾选添加环境变量）

（6） 安装pyserial v3.4 或者更高版本，Sniffer的Python程序中使用到了该模块，安装教程可网上搜索pyserial安装。

在Python的安装目录下，文件夹Scripts中有pip.exe。

![pip.exe](https://image.3001.net/images/20181108/1541644044_5be39f0c2f76c.png!small)

来到该目录，输入命令`pip.exe install pyserial`即可。

![pip.exe install
pyserial](https://image.3001.net/images/20181108/1541644159_5be39f7f9b12e.png!small)

## 二、nRF Sniffer安装和配置

（1） 打开 Wireshark 软件，Go to Help > About Wireshark，点击 Folders，双击 Extcappath。

![二、nRF
Sniffer安装和配置](https://image.3001.net/images/20181108/1541644199_5be39fa7301ae.png!small)

将nrf_sniffer_(version)_(hash).zip 文件解压到这个目录下，并将extcap目录的内容复制到该目录下，如下图所示。

![将extcap目录的内容复制到该目录](https://image.3001.net/images/20181108/1541644211_5be39fb35062d.png!small)

（2） 打开 Wireshark 软件，Go to Help > About Wireshark，点击 Folders，双击
Personalconfiguration，打开该目录，将Profile_nRF_Sniffer-(version) 文件拷贝到该目录。

![将Profile_nRF_Sniffer-\(version\)
文件拷贝到该目录](https://image.3001.net/images/20181108/1541644230_5be39fc653a82.png!small)

打开 Wireshark 软件，Edit > Configuration Profiles，选中Profile_nRF_Sniffer-(version)
，并确认。

![确认](https://image.3001.net/images/20181108/1541644264_5be39fe8c9bbd.png!small)

![确认](https://image.3001.net/images/20181108/1541644272_5be39ff0060a2.png!small)

## 三、烧录固件

（1） 将Sniffer Dongle插到PC上，打开nRFgo Studio软件。

（2） 在软件左侧的选择框中依次点击Device Manager > nRF51 #### > Segger ######，点击Erase all。

![三、烧录固件](https://image.3001.net/images/20181108/1541644311_5be3a0178987b.png!small)

然后，选择ProgramApplication > Browse

（3） 选择固件文件，然后点击Program即可。

![点击Program](https://image.3001.net/images/20181108/1541644320_5be3a02080d33.png!small)

固件文件在\nrf_sniffer_2.0.0-beta-2_10Sep2018_3ef662e\hex\目录下，选择sniffer_pca10028_####.hex、sniffer_pca10031_####.hex均可，都支持对BLE通信数据的嗅探功能。

![嗅探功能](https://image.3001.net/images/20181108/1541644527_5be3a0ef244a1.png!small)

## 四、嗅探蓝牙通信数据

（1） 将Sniffer Dongle插到PC上。打开 Wireshark 软件，选中nRF Sniffer COM# 接口，并点击开始。

![四、嗅探蓝牙通信数据](https://image.3001.net/images/20181108/1541644558_5be3a10e99caa.png!small)

（2） 通过主界面， 可以看到嗅探到BLE数据。默认选择的是“All advertising devices”，即周围所有的BLE通信的广播数据。

![所有的BLE通信的广播数据](https://image.3001.net/images/20181108/1541644609_5be3a141cab1b.png!small)

（3） 通过Device下拉菜单，可以选择要嗅探的目标设备。

![要嗅探的目标设备](https://image.3001.net/images/20181108/1541644627_5be3a1534226c.png!small)

选中要嗅探的目标设备，就可以将该设备的通信数据过滤出来。下图所示，是该设备在配对时的Master端发送的蓝牙BLE数据信息。

![发送的蓝牙BLE数据信息](https://image.3001.net/images/20181108/1541644637_5be3a15dbf0ee.png!small)

（4）选择任意其他的设备，可以嗅探到其蓝牙通信数据。

![嗅探到其蓝牙通信数据](https://image.3001.net/images/20181108/1541645000_5be3a2c81d2f4.png!small)

 ***本文作者：barcating，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

