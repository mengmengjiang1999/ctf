本篇是”手上有啥就搞啥“系列的第三篇，研究对象是Miwifi放大器2，侧重点是 **ecos固件逆向** 和 **WiFi信号放大代码分析** 。

![](https://image.3001.net/images/20221105/1667625213_6365f0fd070c498f8a5e9.png!small)

现在Mesh组网遍地是，效果确实不错，WiFi放大器也就吃了灰。古老的Miwifi放大器2(version
R2)使用MT7628解决方案，Mipsel架构，固件则采用ecos RTOS，代码并不开源(找到MT7628
Openwrt代码作参考)，本文将从原理、代码和二进制层面分析。

内容主要包括：

  * 0x00 基础知识：ecos RTOS和WiFi放大器原理简介
  * 0x01 站在巨人肩上：MT7628资料，固件资源下载
  * 0x02 自己动手做：硬件拆解，WiFi放大原理分析，ecos固件逆向
  * 00x3 做个总结：简单总结
  * 0x04 参考资料：参考链接

往期回顾：

[ **手上有啥就搞啥(一) —
小米手环3**](https://www.freebuf.com/articles/endpoint/344640.html)

 **[手上有啥就搞啥(二) — 猫盘](https://www.freebuf.com/articles/endpoint/346606.html)**

## 0x00 基础知识

### 0x00 - 00 ecos RTOS

![](https://image.3001.net/images/20221105/1667625261_6365f12d6d826b384e7f5.png!small)

**eCos（embedded configurable operating system）**是一个在1997年由Cygnus Solutions Inc
开发的小型开放原始码实时操作系统。后来该公司被Redhat收购。此系统和嵌入式Linux系统的差异是它采用静态链接(static
library)的方式，最低编译核心可小至10K的级别，适合用于做bootloader增强，或者用于构建微小型系统。

除了自由版本以外，eCos还有一个称为eCosPro的商业版本。它是eCos的一个商业分支，由eCosCentric开发，并包含有私有组件。在2017年，eCosCentric发布了对于全部树莓派单板计算机的eCos移植，并同时发布了这些移植的自由版本。

### 0x00 - 01 WiFi信号放大原理

WiFi信号放大的原理实际上和两个无线路由器之间的无线桥接类似。WiFi信号放大器会通过无线的方式，和原来无线路由器建立连接，加强器自身并再提供一个无线信号，从而实现扩大无线信号覆盖范围的目的。![](https://image.3001.net/images/20221105/1667625320_6365f1682ee4ccedaf763.png!small)

中继器、网桥、WiFi放大器的 **区别** 在于**，中继器 **是** 物理层上 **的网络互连设备，网桥工作在** 数据链路层**，
**WiFi信号放大器** 类似两个无线路由器之间的无线桥接。

## 0x01 站在巨人肩上

### 0x01 - 00 MT7628资料

MT7628 整合了 2T2R 802.11n Wi-Fi 收发器、580MHz MIPS® 24KEc™ 中央处理器 (CPU)、5
端口高速以太网络端口物理层 (Ethernet PHY)、AES128/256 安全引擎、USB2.0 主机、PCIe
主机，以及连接不同传感器的多个慢速输入输出 (I/O)。

  * [ **MT7628 SOC.xin资源**](https://github.com/SoCXin/MT7628)
  *  **[MT7628 DataSheet](https://files.seeedstudio.com/products/114992470/MT7628_datasheet.pdf)**

### 0x01- 01 固件资源下载

  * [ **MT7628 AP OpenWrt 源码**](https://github.com/dcboy/mt7628-p4rev-120395.git)
  * [ **MiWiFi2 固件**](https://disk.yandex.ru/d/KiqeCwcB6RZaWw)

## 0x02 自己动手做

### 0x02 - 00 WiFi信号放大原理分析

首先通过一个特别简单的实现分析WiFi信号放大的实现，为后面逆向做准备。在
**[Github](https://github.com/mrtejas99/wifi-extender)** 上找到一个基于
**wpa_supplicant** 的工具，核心代码只使用了shell脚本。

  *  **wpa_supplicant**

 **wpa_supplicant** 开源项目是跨平台的 WPA 请求者程序 (supplicant)，支持 WEP、WPA 和 WPA2 (
**IEEE 802.11i**
)，简单的说，wpa_supplicant就是WiFi驱动和用户的中转站外加对协议和加密认证的支持，大部分Linux发行版自带该功能。

  *  **[wifi_extender](https://github.com/mrtejas99/wifi-extender)**

![](https://image.3001.net/images/20221105/1667625426_6365f1d23ab3a8ce56627.png!small)
**wifi_extender** 由 **bash_script** 和 **WebUI** 两部分组成，其中 WebUI 通过flask
实现：![](https://image.3001.net/images/20221105/1667625458_6365f1f2d5d850bc9b44f.png!small)

主功能是 **bash_script** ，完全用shell 脚本调用 **wpa_supplicant** 实现，代码页十分简单：

    
    
    install() {
        echo "Installing..."
        interactive_configurations
        validate_configurations
        check_interfaces
        echo "setup_systemd_networkd..."
        setup_systemd_networkd
        echo "config_wpsup"
        config_wpsup
        echo "setup_wlan1_client..."
        setup_wlan1_client
        echo "configure_interfaces"
        configure_interfaces
        echo "done. rebooting..."
        sleep 2
        /sbin/reboot
    }
    

关键函数是 **config_wpsup** 和 **setup_wlan1_client**
，通过这两个函数可以基本理清信号放大的流程就是桥接，即连需要放大的WiFi SSID，在开一个新的WiFi SSID，中间作转发。

    
    
    # 输入新旧SSID和密码
    interactive_configurations() {
        # Ask the user to input the correct configurations for ssid(s) and passwords
        read -p 'Please enter the name (SSID) of the network you wish to connect the pi: ' ORIGINAL_SSID
        while read -p "Please enter the password of the wifi network: " ORIGINAL_PASS && [ ${#ORIGINAL_PASS} -lt 8 ]; do
            echo "Please enter password with more than 8 characters."
        done
    
        read -p 'Please enter the name (SSID) of the new network you want to create:' NEW_SSID
        while read -p "Please enter the password of the wifi network: " NEW_PASS && [ ${#NEW_PASS} -lt 8 ]; do
            echo "Please enter password with more than 8 characters."
        done
    }
    
    # 配置旧SSID连接(需要放大的信号源)
    setup_wlan1_client() {
        {
            echo "country=IN"
            echo "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev"
            echo "update_config=1"
            echo "network={"
            echo '  ssid="'$ORIGINAL_SSID'"'
            echo '  psk='`generate_wpa2_psk $ORIGINAL_SSID $ORIGINAL_PASS`
            echo "}"
        } > $ws_wlan1
    
        chmod 600 $ws_wlan1
        systemctl disable wpa_supplicant.service
        systemctl enable wpa_supplicant@wlan1.service
    }
    
    # 配置新的SSID(放大后的信号源)
    config_wpsup() {
        {
            echo "country=IN"
            echo "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev"
            echo "update_config=1"
            echo "network={"
            echo '  ssid="'${NEW_SSID}'"'
            echo "  mode=2"
            echo "  key_mgmt=WPA-PSK"
            echo '  psk='`generate_wpa2_psk $NEW_SSID $NEW_PASS`
            echo "  frequency=2412"
            echo "}"
        } > $wp0conf
        chmod 600 $wp0conf
        # Restart wpa_supplicant service
        systemctl disable wpa_supplicant.service
        systemctl enable wpa_supplicant@wlan0.service
    }
    

在对信号放大器原理在实现层面有了基本认识，下面正式分析 **MiWiFi2** 。

### 0x02 - 01 硬件拆解与调试

说好的十秒拆机，结果边缘撬成了锯齿~.~。

![](https://image.3001.net/images/20221105/1667625573_6365f2659a10a9402f380.jpg!small)内部结构十分简单，可以看到
**MT7628** 印字和 **UART** ，但需要自己识别引脚，使用万用表测得引脚释义如下，具体方法不再赘述：

![](https://image.3001.net/images/20221105/1667625606_6365f286af94cb5fbcff2.png!small)手残式拆机加手残式焊接，本来焊了个排针，结果插的时候就掉了~.~.

![](https://image.3001.net/images/20221105/1667625639_6365f2a729e6f0dd30772.jpg!small)直接焊线上去，电烙铁还是要买个好点的，尤其我这样的手残党-.-![](https://image.3001.net/images/20221105/1667625656_6365f2b8b7b06b18dc8dc.jpg!small)

连接USB串口输出 **uboot** 信息：

    
    
    U-Boot 1.1.3 ( Nov 24 2016 - 15:25:121)
    
    Board: Ralink APSoC DRAM:   8 MB
    relocate_code Pointer at: 807b8000
    flash manufacture id: c2, device id 20 15
    ......
     estimate memory size =8 Mbytes
    RESET MT7628 PHY!!!!!!
    Please choose the operation:
       1: Load system code to SDRAM via TFTP.
       2: Load system code then write to Flash via TFTP.
       3: Boot system code via Flash (default).
       4: Entr boot command line interface.
       7: Load Boot Loader code then write to Flash via Serial.
       9: Load Boot Loader code then write to Flash via TFTP.
    ......
    

### 0x02 - 02 ecos固件逆向

  *  **固件分析**

首先 **binwalk**
解析一下，结构如下：![](https://image.3001.net/images/20221105/1667625764_6365f3246c44ade50ea5b.png!small)

必然是无法 **-e** 解决的，值得注意的关键字都已经用方框标出。猜测信息如下：

  * 固件可能使用ecos RTOS；
  * CPU架构是MIPS(实际是Mipsel)；
  * “zxrouter”可作为进一步搜索的关键字；
  * 0x5000和0x11000是固件主体，CRC相同(可能是分区备份？)。

从最明显的 **zxrouter** 关键字入手，使用如下命令先解开 **uImage** 文件:

    
    
    # dd if=firmware_Xiaomi_Mi_WIFI2.bin of=zxrouter.lzma bs=1 skip=1123424
    # xzcat zxrouter.lzma > zxrouter.bin
    

使用 **binwalk** 查看， **uImage** 的结构已经很清晰了，接下来就可以愉快的逆向了
-.-.![](https://image.3001.net/images/20221105/1667625788_6365f33c8dc8e593ce27a.png!small)

  *  **ecos逆向**

在之前的文章笔者也提到过，逆向一定要明确目的，否则就会陷入无尽的循环…在这里笔者并不打算作漏挖，所以目的还是 **加载地址** 、 **符号** 和
**关键函数流程** 的识别。

用010edit打开，可以看到前 **0x100字节**
存在一个明显的结构：![](https://image.3001.net/images/20221105/1667625814_6365f3562fd5f91561740.png!small)

但并没有长度和校验段，IDA也按代码识别：![](https://image.3001.net/images/20221105/1667625847_6365f3771110ed447fe0f.png!small)

>  **加载地址**

根据 **binwalk** 的输出信息，中断向量表的地址是 **0x80008200** ，猜测加载地址应该是 **0x80000000附近的某个地址**
。

加载地址获取的常用方法，可动态调试的看串口(或其他调试口)输出信息，一般有 **Load Address** 和 **Entry Point**
输出，静态分析一般可参考SDK
内存分布和固件自身(字符串/函数等)对应关系，注意到固件末尾有明显的地址标识：![](https://image.3001.net/images/20221105/1667625889_6365f3a1f337bf2e6efb0.png!small)

当加载地址设置时，在IDA中可自动识别：![](https://image.3001.net/images/20221105/1667625899_6365f3ab8a4d1356f0bdb.png!small)

在本系列上一篇也提到过，[
**Github**](https://github.com/soyersoyer/basefind2)有现成脚本可以使用，还是具备一定的准确性的：![](https://image.3001.net/images/20221105/1667625946_6365f3dac16f9b922c4e4.png!small)

通过字符串信息比对加载地址确实是 **0x80008400** 。使用 IDA PRO 工具加载固件，设置架构* **mips little
edition** ，*加载地址为 **0x80008400** ，在最开始处 **Make Code** 后，看到了熟悉的 **eCos kernel
exception handler** ：

    
    
    # mips cpu 产生exception/interrupt后，cpu会跳到特定的几个地址上,
    # BEV=0时，一般的在0x80000180,当然还有些其他地址
    FUNC_START(other_vector)
        mfc0    k0,cause        	  # K0 = exception cause
        nop
        andi    k0,k0,0x7F        	# isolate exception code
        la      k1,hal_vsr_table    # address of VSR table
        add     k1,k1,k0        	  # offset of VSR entry
        lw      k1,0(k1)        	  # k1 = pointer to VSR
        jr      k1            	    # go there
        nop                		      # (delay slot)
    FUNC_END(other_vector)
    

![](https://image.3001.net/images/20221105/1667625964_6365f3ec7ce236eee25f9.png!small)简单使用
**IDA python Script** (暴力)转换 **code** ：

    
    
    def fix_code(start_address, end_address):
        offset = start_address
        while offset <= end_address:
            offset = idc.next_addr(offset)
            flags = idc.get_full_flags(offset)
            try:
                idaapi.add_func(offset, idaapi.BADADDR)
            except:
                pass
    

再经过一些修正，成为 **Super Blue**
：![](https://image.3001.net/images/20221105/1667626049_6365f441d4f901155eaf9.png!small)

>  **符号**

固件不存在导入表及导出表，故无法区分哪些是常见的系统函数，这种RTOS如果有符号，一般都是通过表的形式，恢复方法和研究比较多的 **VXworks**
差不多，比如该固件，有明显的表结构如下：![](https://image.3001.net/images/20221105/1667626261_6365f515bc35b66e38ddb.png!small)

每一组结构包含两个地址，以红框里为例，第一个地址为 **0x801B1DBC** ，指向该函数名 **stainfo** 字符串，第二个地址为
**0x800804BC**
，指向的是该函数的代码位置：![](https://image.3001.net/images/20221105/1667626272_6365f52000cf07b6120f8.png!small)

用F5反编译，![](https://image.3001.net/images/20221105/1667626294_6365f536228e771e799ec.png!small)

大概也是获取状态信息的功能，红框内的log输出函数名也是由字符串出发识别的，这里不再赘述。

>  **关键函数流程**

虽然 **wifi_extender** 中的代码逻很简单，但是基于 **wpa_supplicant** 实现的，在 MiWiFi2
实现中当然不会如此草率，而固件中的符号并不全，所以参考 **[mt7628 AP
Openwrt](https://github.com/dcboy/mt7628-p4rev-120395)** 版代码，对 **wpa**
的关键功能函数作识别。参考的源码主要是
**[ap.c](https://github.com/dcboy/mt7628-p4rev-120395/blob/f1043a07e49381a633c65c718e09c61cdaf2788c/src/embedded/ap/ap.c)，[ap_wpa.c](https://github.com/dcboy/mt7628-p4rev-120395/blob/master/src/embedded/ap/ap_wpa.c)**。

    
    
    // 关键函数
    NDIS_STATUS APInitialize(RTMP_ADAPTER *pAd)
    VOID APStartUp(RTMP_ADAPTER *pAd)
    VOID APStop(RTMP_ADAPTER *pAd)
    VOID APShutdown(RTMP_ADAPTER *pAd)
    VOID WpaSend(RTMP_ADAPTER *pAdapter, UCHAR *pPacket, ULONG Len)
    VOID HandleCounterMeasure(RTMP_ADAPTER *pAd, MAC_TABLE_ENTRY *pEntry)
    

利用的基本是log字符串定位：

其他几个函数也是相同相同方法，还原的函数地址为：

    
    
    # 函数代码过长，截图展示效果不佳，且与上图基本相同，这里就只列出结果：
    APInitialize ====>   sub_8001C984
    APStartUp    ====>   sub_8001BCAC
    APStop       ====>   sub_8001BB38
    APShutdown   ====>   sub_8001C8AC
    WpaSend      ====>   sub_800274FC
    HandleCounterMeasure ====>   sub_800283A8
    

## 0x03 做个总结

本篇针对MiWIFi2作了固件逆向和WiFi信号放大实现的研究。通过拆解(其实都不用拆)看到该设备结构和功能都比较简单，逆向难度适中，研究价值一般。下一篇为了保护视力，准备远离RTOS，并侧重漏挖(装装样子~.~)，那就下个设(po)备(lan)见。

## 0x04 参考资料

[网桥，中继器，WiFi信号放大器他们什么区别啊？](https://www.zhihu.com/question/268884409/answer/447027278)

[Meross MSS310](http://projects.nesrada.de/mss310/index.html)

<https://github.com/dcboy/mt7628-p4rev-120395>

[python-miio/wifirepeater.py at master · rytilahti/python-miio](https://github.com/rytilahti/python-miio/blob/master/miio/wifirepeater.py)

[GitHub - mrtejas99/wifi-extender: A WiFi repeater built around Raspberry Pi
under 10 US$](https://github.com/mrtejas99/wifi-extender)

[wpa_supplicant详解_漳南的博客-CSDN博客_wpa_supplicant](https://blog.csdn.net/zm19930923zm/article/details/88743533)

<https://zhuanlan.zhihu.com/p/24246712>

[https://wiki.archlinux.org/title/Wpa_supplicant_(简体中文)](https://wiki.archlinux.org/title/Wpa_supplicant_\(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87\))

[Zyxel Auto-identifying eCos Firmwares Load
Address](https://ecos.wtf/2021/03/30/ecos-load-address)

[Zyxel设备eCos固件加载地址分析](https://cq674350529.github.io/2021/03/04/Zyxel%E8%AE%BE%E5%A4%87eCos%E5%9B%BA%E4%BB%B6%E5%8A%A0%E8%BD%BD%E5%9C%B0%E5%9D%80%E5%88%86%E6%9E%90/#eCos%E5%9B%BA%E4%BB%B6%E5%8A%A0%E8%BD%BD%E5%9C%B0%E5%9D%80%E5%88%86%E6%9E%90)

[openswc/uboot-MT7628](https://gitee.com/openswc/uboot-mt7628)

[Part 2: Serial Interface](http://projects.nesrada.de/mss310/serial.html)

[UART串口调试](https://www.secpulse.com/archives/157847.html)

[小米WiFi放大器pro拆机_小米WiFi放大器pro评测_智能家](https://www.znj.com/news/3744.html)

