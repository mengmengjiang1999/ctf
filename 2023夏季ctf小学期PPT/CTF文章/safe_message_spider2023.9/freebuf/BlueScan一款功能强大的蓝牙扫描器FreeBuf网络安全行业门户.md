![](https://image.3001.net/images/20201012/1602433797_5f8333054e6d68a3f900c.jpg!small)

## BlueScan

BlueScan是一款功能强大的蓝牙扫描器，广大研究人员可以使用BlueScan来扫描BR/LE设备、LMP、SDP、GATT以及相关的蓝牙漏洞。

考虑到目前社区中针对蓝牙安全方面的工具并不多，而且现有的工具很多也都无人更新或维护了，因此我们便基于Python3开发出了这款功能强大的蓝牙扫描器-BlueScan.

在针对新的蓝牙设备进行渗透攻击时，BlueScan扫描器将能够帮助广大研究人员收集大量信息，其中包括：

> BR设备信息；
>
> LE设备信息；
>
> LMP特性信息；
>
> GATT服务信息；
>
> SDP服务信息；
>
> 各种蓝牙漏洞；

## 工具要求

该工具基于BlueZ实现其功能，也就是官方的Linux蓝牙栈，因此在使用BlueScan之前我们还需要安装下列代码包：

    
    
    sudo apt install libglib2.0-dev libbluetooth-dev

如果你是在一台Linux虚拟机上使用该工具的话，建议让虚拟机独占一个 USB 蓝牙适配器，比如说售价为99元的Ostran Bluetooth USB
Adapter OST-105 CSR 8150 v4.0【 _链接_】之类的，如果你资金雄厚的话也可以尝试560元的Parani UD100-G03【
_链接_】，毕竟一分钱一分货。

## 工具安装

广大研究人员可以使用下列命令直接将该项目源码克隆至本地并使用：

    
    
    git clone https://github.com/fO-000/bluescan.git

除此之外，最新版本的BlueScan源码我们也已经上传到了PyPI上，所以大家也可以使用下列命令安装BlueScan：

    
    
    sudo pip3 install bluescan

## 工具使用

    
    
    $ bluescan -h
    
    bluescan v0.2.2
    
     
    
    A powerful Bluetooth scanner.
    
     
    
    Author: Sourcell Xu from DBAPP Security HatLab.
    
     
    
    License: GPL-3.0
    
     
    
    Usage:
    
        bluescan (-h | --help)
    
        bluescan (-v | --version)
    
        bluescan [-i <hcix>] -m br [--inquiry-len=<n>]
    
        bluescan [-i <hcix>] -m lmp BD_ADDR
    
        bluescan [-i <hcix>] -m sdp BD_ADDR
    
        bluescan [-i <hcix>] -m le [--timeout=<sec>] [--le-scan-type=<type>] [--sort=<key>]
    
        bluescan [-i <hcix>] -m gatt [--include-descriptor] --addr-type=<type> BD_ADDR
    
        bluescan [-i <hcix>] -m vuln --addr-type=br BD_ADDR
    
     
    
    Arguments:
    
        BD_ADDR    Target Bluetooth device address. FF:FF:FF:00:00:00 means local device.
    
     
    
    Options:
    
        -h, --help                  Display this help.
    
        -v, --version               Show the version.
    
        -i <hcix>                   HCI device for scan. [default: hci0]
    
        -m <mode>                   Scan mode, support BR, LE, LMP, SDP, GATT and vuln.
    
        --inquiry-len=<n>           Inquiry_Length parameter of HCI_Inquiry command. [default: 8]
    
        --timeout=<sec>             Duration of LE scan. [default: 10]
    
        --le-scan-type=<type>       Active or passive scan for LE scan. [default: active]
    
        --sort=<key>                Sort the discovered devices by key, only support RSSI now. [default: rssi]
    
        --include-descriptor        Fetch descriptor information.
    
    --addr-type=<type>          Public, random or BR.

## 扫描BR设备

    
    
    -m br

典型蓝牙设备可能使用的有三种技术：BR（基本速率）、EDR（增强数据速率）和AMP（备用MAC/PHY）。由于它们都属于基本速率系统，所以当扫描这些设备时，即为BR设备扫描：

![](https://image.3001.net/images/20201012/1602433845_5f8333352613039f70afa.png!small)

如上图所示，通过BR设备扫描，可以得到周边经典蓝牙设备的地址、页面扫描重复模式、设备类别、时钟偏移量、RSSI、扩展查询响应（名称、TX功率等）等信息。

## 扫描LE设备

    
    
    -m le

蓝牙技术中，除了基本速率系统外之外，其他都属于低能耗（LE）系统，当扫描蓝牙低能量设备时，即为LE设备扫描：

![](https://image.3001.net/images/20201012/1602433860_5f833344cd9e1eb416b9f.png!small)

如上图所示，通过执行LE设备扫描，我们将能够得到周围LE设备的地址、地址类型、连接状态、RSSI和周围LE设备的GAP数据。

## 扫描SDP服务

典型蓝牙设备可以通过SDP来告诉外界关于它的开放服务的相关信息，通过进行SDP扫描，我们将能获取到指定典型蓝牙设备相关的服务记录：

![](https://image.3001.net/images/20201012/1602434488_5f8335b8b1bcd45b0cfab.png!small)

## 扫描LMP特性

突破检测典型蓝牙设备的LMP特性，我们就可以判断目标蓝牙设备的底层安全状况了：

![](https://image.3001.net/images/20201012/1602434500_5f8335c470b57569ab8d2.png!small)

## 扫描GATT服务

LE设备可以通过GATT来告诉外界它所支持的开放服务信息，进行了GATT扫描之后，我们就可以获取到指定LE设备的GATT服务信息了，你可以尝试读取并记录这些GATT信息以备后续渗透使用：

![](https://image.3001.net/images/20201012/1602434511_5f8335cf0de70ac6310cc.png!small)

## 漏洞扫描

漏洞扫描功能目前仍处于测试阶段，因此当前仅支持扫描漏洞CVE-2017-0785：

    
    
    $ sudo bluescan -m vuln --addr-type=br ??:??:??:??:??:??
    
    ... ...
    
    CVE-2017-0785

## 疑难解答

如果遇到"Can't find the ID of hci0 in rfkill"报错信息，是因为某些旧版本的rfkill不支持-r或-n选项，比如说：

    
    
    # Ubuntu 16.04.1
    
    rfkill --version
    
    # rfkill 0.5-1ubuntu3 (Ubuntu)"

请更新rfkill或操作系统版本便可解决该问题。

## 许可证协议

BlueScan项目的开发与发布遵循GPL v3.0开源许可证协议。

## 项目地址

BlueScan：【[ _GitHub传送门_](https://github.com/fO-000/bluescan)】

