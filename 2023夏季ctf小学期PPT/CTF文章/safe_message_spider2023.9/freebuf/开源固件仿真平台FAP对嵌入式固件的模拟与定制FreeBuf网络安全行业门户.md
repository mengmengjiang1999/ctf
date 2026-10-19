固件，即烧录进芯片的嵌入式程序，通常包含`bootloader`、内核以及文件系统。因其一般不容易更改，我们称之为“固件”。固件可以通过硬件手段获取，也可以在网上下载各种嵌入式产品的固件。但是更多时候，我们手中没有相应的设备。也就是说，获取各种固件成本低廉，而获取产品则需要花费一定财力。

对固件的仿真需求由此出现，`firmadyne`是诞生于2016年的一个优秀开源固件分析工具，可以较好的完成常见路由器固件的模拟。但是其仿真流程较为繁琐，后来有相应的开源项目`firmware-analysis-toolkit`整合了仿真流程，进行了简化。但其环境依赖存在较多问题，在不同的`Linux`发行版上，会遇到各种奇奇怪怪的问题，可能需要耗费很长时间才能将工具的环境搭建好。

在这种情况下，笔者整合和修改了部分代码，构建了一个新的开源仿真平台 —— [firmware-analysis-plus](https://github.com/liyansong2018/firmware-analysis-plus)。使用该工具，可以进一步缩减搭建环境耗费的时间，让我们的精力进一步聚焦于各种路由器仿真的定制以及漏洞挖掘。

## 0x10 firmware-analysis-plus

上游项目支持：[binwalk](https://github.com/ReFirmLabs/binwalk)、[firmadyne](https://github.com/firmadyne/firmadyne)、[firmware-analysis-toolkit](https://github.com/attify/firmware-analysis-toolkit)

 **firmware-analysis-plus** （ **FAP** ）主要用于常见 **路由器固件的仿真**
，可以进行固件的安全测试。感谢以下开源项目：`binwalk`提供优秀的固件提取
API，`firmadyne`提供优秀的固件仿真核心支持，`firmware-analysis-toolkit`提供简化流程的思想。

![](https://image.3001.net/images/20210223/1614044204_60345c2c1a28799c61b0b.png!small)

 **FAP**
只是站在巨人的肩膀上，做出改进和定制，提供一个更加高效的仿真平台。包括精简不必要组件，优化仿真流程，优化网络环境大幅压缩安装时间，修复若干`bug`，一键仿真固件。其原理主要包括两点

> `qemu`提供多种架构指令的模拟，使用预先编译好的内核启动固件中的核心业务
>
>
> 多数嵌入式设备含有一个`nvram`芯片，保存一些重要的配置信息，`firmadyne`实现一个新的`libnvram.so`库文件，通过代码模拟固件启动时加载`nvram`配置信息的行为。

FAP 版本| python 版本| 支持系统| 安装方法  
---|---|---|---  
[v0.1](https://github.com/liyansong2018/firmware-analysis-plus/releases/tag/0.1)| python2、python3| Ubuntu16.04、Ubuntu 18.04、Kali
2020.02| [FAP v0.1 版本手册](https://github.com/liyansong2018/firmware-analysis-plus/wiki/FAP-v0.1-%E7%89%88%E6%9C%AC%E6%89%8B%E5%86%8C)  
[v1.0](https://github.com/liyansong2018/firmware-analysis-plus/releases/tag/1.0)| python2、python3| Beta| Beta  
[v2.0](https://github.com/liyansong2018/firmware-analysis-plus/releases/tag/2.0)| python3| Kali 2020.04（不支持 Ubuntu 20.04，其他未测试）| 如下所示  
  
### 0x11 安装 binwalk

以编译源码的方式安装`binwalk`，时至今日，`binwalk`构建脚本中的诸多依赖已无法正常安装，于是自己`fork`了一份新的`binwalk`，进行了修改。关于修改细节的描述，可参考：https://github.com/liyansong2018/binwalk

    
    
    git clone https://github.com/liyansong2018/binwalk.git
    cd binwalk
    ./deps.sh
    sudo python3 setup.py install
    

### 0x12 安装 FAP

    
    
    git clone https://github.com/liyansong2018/firmware-analysis-plus.git
    cd firmware-analysis-plus
    ./setup.sh
    

### 0x13 配置

修改`fat.config`文件中的密码，改为`root`系统用户的密码

### 0x14 运行

运行`fat.py`脚本，即可对相应的固件进行模拟

    
    
    ./fat.py -q ./2.5.0/ ./testcases/wnap320_V3.7.11.4_firmware.tar
    

结果

    
    
    ┌──(lys㉿kali)-[~/Tools/firmware-analysis-plus]
    └─$ ./fat.py -q ./2.5.0/ ./testcases/wnap320_V3.7.11.4_firmware.tar
    
    
                    ______   _                ___
                    |  ___| (_)              / _ \
                    | |_     _   _ __ ___   / /_\ \  _ __    ___
                    |  _|   | | | '_ ` _ \  |  _  | | '_ \  / __| ++
                    | |     | | | | | | | | | | | | | | | | \__ \ 
                    \_|     |_| |_| |_| |_| \_| |_/ |_| |_| |___/
    
                    Welcome to the Firmware Analysis Plus - v2.0
                By lys - https://blog.csdn.net/song_lee | @liyansong
    
    [+] Firmware: wnap320_V3.7.11.4_firmware.tar
    [+] Extracting the firmware...
    [+] Image ID: 1
    [+] Identifying architecture...
    [+] Architecture: mipseb
    [+] Building QEMU disk image...
    [+] Setting up the network connection, please standby...
    [+] Network interfaces: [('brtrunk', '192.168.0.100')]
    [+] Using qemu-system-mips from /home/lys/Tools/firmware-analysis-plus/qemu-builds/2.5.0
    [+] All set! Press ENTER to run the firmware...
    [+] When running, press Ctrl + A X to terminate qemu
    

通过回车键即可模拟运行目标固件，通过提供的网络接口，打开相应的路由器管理页面

![image](https://image.3001.net/images/20210221/1613877363_6031d073de3633f1d2aec.png!small)

### 0x15 重置

如果仿真次数过多，会生成较多的中间文件，直接运行`reset.py`删除即可

    
    
    ./reset.py
    

## 0x20 定制

上游的`firmadyne`已经设定好了一些规则，在不对源码进行修改的情况下，可以仿真以下版本的固件

> wnap320_V3.7.11.4_firmware.tar
>
> DIR-601_REVB_FIRMWARE_2.01.BIN
>
> DIR890A1_FW103b07.bin
>
> ...

但更多时候，我们想要模拟的程序往往不在上述列表中，这就需要考虑对`firmaydne`进行定制，其实就是对`libnvram`的定制。不同设备芯片上的配置信息是不一样的，固件在启动过程中，所读取的硬件信息也是不一样的，固件在启动之初，会依靠`libnvram.so`提供的函数，读取（如`flash`）芯片上的内容。而在实际环境中，我们没有该芯片，所以就要靠定制`libnvram`，预先设定好一些参数，这样就达到模拟真实硬件的目的。

`firmadyne`提供的`libnvram`源码结构如下

    
    
    firmware-analysis-plus/firmadyne/sources/libnvram$ tree
    .
    ├── alias.c     # 一些libnvram库函数的别名
    ├── alias.h
    ├── config.h    # 预先设定好的nvram配置信息
    ├── LICENSE.txt
    ├── Makefile
    ├── nvram.c     # libnvram库函数
    ├── nvram.h     # 要初始化的所有key/value
    ├── README.md
    └── test.c
    

在仿真不同固件时，往往需要对上述代码进行定制，下面重点讲解几种常用方法。

### 0x21 设置固件封装的库函数别名

固件通常使用`libvram.so`提供的库函数，实现对硬件存储的配置信息的访问和修改

> `nvram_get`，顾名思义，从内核的`NVRAM`模块获取值，其实就是从芯片中获取某个键对应的值，例如获取`LAN_MAC`对应的`mac`地址
>
> `nvram_set`，与上述 API 相反，给硬件设置一个键值对
>
> `nvram_clear`，通过写入1，覆盖所有的键对应的值

`libnvram.so`提供的函数还有很多，功能都是类似的。

但是，在一些固件中，往往会封装自己的`API`，以 **Tenda AC 15** 为例，文件系统中的`libCfm.so`实现了自己的`nvram`库函数

![image](https://image.3001.net/images/20210222/1613963743_603321df78070ba1f2331.png!small)

而`firmadyne`只是实现了了`libnvram.so`标准库函数的`hook`，因此我们需要将目标固件封装的一些函数添加到`firmadyne`源码中

在`alias.c`源码中添加如下代码

    
    
    /* Tenda AC15 */
    int bcm_nvram_set(const char *key, const char *val) __attribute__ ((alias ("nvram_set")));
    char *bcm_nvram_get(const char *key) __attribute__ ((alias ("nvram_get")));
    int bcm_nvram_init(void) __attribute__ ((alias ("nvram_init")));
    // ...
    

### 0x22 预先设置固件需要的 nvram 键值对

`config.h`文件已经包含作者设定好的一些固件需要的键值对

    
    
    // Default values for NVRAM.
    #define NVRAM_DEFAULTS \
        /* Linux kernel log level, used by "WRT54G3G_2.11.05_ETSI_code.bin" (305) */ \
        ENTRY("console_loglevel", nvram_set, "7") \
        /* Reset NVRAM to default at bootup, used by "WNR3500v2-V1.0.2.10_23.0.70NA.chk" (1018) */ \
        ENTRY("restore_defaults", nvram_set, "1") \
        ENTRY("sku_name", nvram_set, "") \
        ENTRY("wla_wlanstate", nvram_set, "") \
        ENTRY("lan_if", nvram_set, "br0") \
        ENTRY("lan_ipaddr", nvram_set, "192.168.0.50") \
        ENTRY("lan_bipaddr", nvram_set, "192.168.0.255") \
        ENTRY("lan_netmask", nvram_set, "255.255.255.0") \
    

但是我们的目标固件往往是没有包含在其中的，因此需要手动添加。一般来说包含一下两种情况

一、`firmadyne`错误日志（`./firmadyne/scratch/1/qemu.initial.serial.log`）直接提供。这种情况比较简单，直接根据错误日志直接找到缺少的键值对，如下所示

![image](https://image.3001.net/images/20210222/1613968368_603333f01e70854d0d364.png!small)

直接在`config.h`中添加键值

    
    
    /* Tenda AC15 */ \
        ENTRY("default_nvram", nvram_set, "1") \
        ENTRY("image_boot", nvram_set, "0")
    

二、更多时候，没有办法直接从错误日志中直接找到问题所在，那就只能分析相应的二进制，如下所示是 **DIR-2640** 固件在仿真中产生的错误日志

![image](https://image.3001.net/images/20210222/1613969381_603337e5db2a81bd5b279.png!small)

根据打印的一些错误日志和调用栈，找到相应的错误代码

![image](https://image.3001.net/images/20210222/1613969349_603337c54908b05d9755d.png!small)

也就是说，缺少`factory_mode`键对应的值，同样的，增加键值到`config.h`中即可。

### 0x23 其他函数拦截

某些固件可能还会遇到一些其他函数带来的错误，导致固件运行失败，遇到这种情况，可以使用`IDA`给相应的二进制打`patch`，绕过该函数，不过这种方式需要重新打包固件。好在`firmadyne`也考虑到此类情况，可以直接`hook`普通函数。

例如在 AC15 中，加载如下函数遇到错误，导致`malloc`失败

![image](https://image.3001.net/images/20210222/1613972457_603343e99b3e10936c99d.png!small)

跟踪该函数，发现该函数的目的是读取某些`mtd`设备的大小，很明显，我们是没有实际设备

![image](https://image.3001.net/images/20210222/1613972519_60334427b8fb96180fcbd.png!small)

因此需要`hook`该函数，返回一个恰当值，在`alias.c`添加相应函数的定义

    
    
    int get_cfm_blk_size_from_cache(){
        return 0x20000;
    }
    

### 0x24 编译

修改后的`libnvram`需要编译，拷贝到相应位置，`firmadyne`提供了[交叉编译工具](https://github.com/liyansong2018/Tools2Firmware/tree/master/toochains/musl-1.1.12)

    
    
    # arm
    cd ./firmadyne/sources/libnvram
    make clean && CC=/opt/cross/arm-linux-musleabi/bin/arm-linux-musleabi-gcc make && mv libnvram.so ../../binaries/libnvram.so.armel
    # mipseb
    make clean && CC=/opt/cross/mipseb-linux-musl/bin/mipseb-linux-musl-gcc make && mv libnvram ../../binaries/libnvram.so.mipseb
    # mipsel
    make clean && CC=/opt/cross/mipsel-linux-musl/bin/mipsel-linux-musl-gcc make && mv libnvram ../../binaries/libnvram.so.mipsel
    

这样就完成了`libnvram`的定制。

## 0x30 总结

固件仿真不是一蹴而就的，无论是 **FAP** 还是 **firmadyne**
，只是为我们提供了一个框架，预置代码支持的固件类型和版本有限。尝试运行不同厂商的固件往往会遇到各种奇奇怪怪的问题，需要根据 **firmadyne**
提供的崩溃日志，定位到出错的代码，分析崩溃原因，定制`libnvram`。这是一个艰难而漫长的过程，但是在这个过程中，可以加深对目标固件业务的理解，并且一旦仿真成功，我们可以复现各种已知`CVE`，甚至可以很容易挖掘到各种`0day﻿`漏洞。

