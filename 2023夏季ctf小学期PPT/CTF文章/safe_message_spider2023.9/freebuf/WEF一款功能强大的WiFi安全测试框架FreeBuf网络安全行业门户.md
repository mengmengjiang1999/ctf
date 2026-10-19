## 关于WEF

WEF全名为WiFi Exploitation Framework，它是一款一款功能强大的Wi-Fi安全测试框架。WEF基于802.11网络和协议实现其功能，并且包含了大量针对WPA/WPA2和WEP的安全测试组件，能够帮助广大研究人员实现针对Wi-Fi和蓝牙的自动化渗透测试。

当前版本的WEF支持Kali Linux、Parrot OS、Arch Linux和Ubuntu操作系统。

## 功能介绍

> 日志生成
>
> WPA/WPA2、WPS和WEP攻击
>
> 自动握手破解
>
> 支持针对EvilTwin攻击的多个模板
>
> 检查监视器模式和状态
>
> 2Ghz和5Ghz攻击
>
> 自定义字典选择器
>
> 自动化检测
>
> 蓝牙支持（干扰、读取、写入）

## 支持的测试类型

> 去身份验证攻击
>
> 身份验证攻击
>
> Beacon洪泛攻击
>
> PMKID攻击
>
> EvilTwin攻击
>
> 被动/隐蔽攻击
>
> Pixie Dust攻击
>
> Null Pin攻击
>
> Chopchop攻击
>
> 重放攻击
>
> Michael Exploitation攻击
>
> Caffe-Latte攻击
>
> 干扰、读取和写入蓝牙连接
>
> 使用HackRF实现GPS欺骗

## 工具要求

我们无需手动安装下列工具组件，WEF会自动完成依赖组件的安装：

> aircrack-ng
>
> reaver
>
> mdk4
>
> macchanger
>
> hashcat
>
> xterm
>
> hcxtools
>
> pixiewps
>
> python3
>
> btlejack
>
> crackle
>
> php
>
> hostadp
>
> dnsmasq

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地，并完成工具安装：

    
    
    git clone https://github.com/D3Ext/WEF
    
    cd WEF
    
    bash setup.sh

 **One-Liner安装** ：

    
    
    git clone https://github.com/D3Ext/WEF && cd WEF && bash setup.sh

### Arch Linux额外要求

如果你使用的是Arch Linux，那么你还需要安装一些其他的包：

    
    
    curl -O https://blackarch.org/strap.sh
    
    chmod +x strap.sh
    
    sudo ./strap.sh
    
    pacman -S base-devel libnl openssl ethtool util-linux zlib libpcap sqlite pcre hwloc cmocka net-tools wpa_supplicant tcpdump screen iw usbutils pciutils

## 工具使用

    
    
    # 不同设备可能接口不同
    
    wef -i wlan0

或者

    
    
    wef --interface wlan0

当程序开始运行之后，可以输入“help”命令来查看该工具支持的更多功能和帮助信息。

如果你不想针对目标AP执行所有的扫描测试，那么可以通过下列方法来使用WEF：

    
    
    # 指定测试的名称
    
    set name my-wifi
    
    # 设置每次测试的时间间隔
    
    set time 60
    
    # 指定每种测试所要发送的数据包数量
    
    set packets 15

## 工具使用演示

![](https://image.3001.net/images/20220705/1657016122_62c40f3abf45375b85f5e.png!small)

![](https://image.3001.net/images/20220705/1657016129_62c40f41eb4c7e43c283d.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GNU_](https://github.com/D3Ext/WEF/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **WEF** ：【[ _GitHub传送门_](https://github.com/D3Ext/WEF)】

