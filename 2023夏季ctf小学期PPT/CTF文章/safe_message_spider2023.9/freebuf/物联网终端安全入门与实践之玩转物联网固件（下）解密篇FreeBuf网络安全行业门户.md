>
> ​上一篇文章主要介绍了终端设备固件仿真的概念、技术、工具和框架，以及手动固件仿真的过程和技巧。本篇将介绍终端设备固件常见的加密和解密方法，并通过实例带领读者了解某些场景下固件完整的解密流程。

## 0x01 背景

想象一下以下场景，当你跟随我们的《物联网终端安全入门与实践》系列文章学会了多种获取固件的方法，甚至忍痛将自家路由器拆了掏出了固件之后，正雄心勃勃准备继续学习提取文件系统、仿真时，发现一向满腹经纶的binwalk竟然哑火，它没有输出任何你期待的信息。别担心这可能不是你的binwalk坏了，一般情况下是这个固件格式和内容超出了它的理解范围，简单理解就是固件被厂商作了加密处理。

随着物联网的飞速发展，越来越多的设备被曝出存在大量的安全问题，这不仅给整个网络环境以及用户带来较大的安全隐患，更给厂商能否获取较好的品牌口碑带来足够大的挑战。为此，越来越多的厂商都会给自家设备发布加密固件来对抗一些存有恶意目的攻击者的分析和研究。

###

## 0x02 **固件的常见加解密方法**

在正式动手对固件进行解密之前，我们需提前了解厂商一般会以怎样的形式发布加密固件以及在设备启动和固件升级过程中，会在哪些地方对固件进行解密，从而思考实现解密的逻辑和方法。

###  **2.1** **从固件发布场景定位解密方法**

厂商发布加密固件一般有以下三种场景：

  1. 固件出厂时未加密，后续发布包含解密程序的未加密过渡版本，随后发布加密固件

  2. 固件出厂时加密，后续发布包含新版解密程序的未加密过渡版本，随后发布使用新加密方案加密的固件

  3. 固件出厂时加密，后续发布包含新版解密程序的加密版本（使用旧版本加密方案加密），随后发布使用新加密方案加密的固件

 **2.1.1 固件出厂未加密后续发布包含解密方案的未加密固件**

固件在出厂时未加密，也未包含任何解密代码，后续为了发布加密固件，会提前发布一个包含解密程序的未加密版本作为过渡版本，这样后续发布加密固件时可使用该解密程序进行解密，这类情况在发布时间较早的设备中比较常见。

![](https://image.3001.net/images/20220919/1663557530_6327df9ae5c3824875177.jpg!small)

对于此种情况，可寻找固件过渡版本v1.1，从中分析出所包含的解密逻辑和算法，从而实现对后续加密固件的解密。因为用户无法从v1.0直接升级v1.2的固件，所以在官方的固件发布描述中，一般会存在如下图所述的描述。

![](https://image.3001.net/images/20220919/1663557546_6327dfaa792194421a08d.png!small)

 **2.1.2 固件出厂加密后续发布包含新版解密方案的未加密固件**

固件在出厂时加密，厂商决定更改加密方案并发布一个未加密的转换版本v1.1，其中包含了新版本的解密程序，这样后续发布加密固件时可使用新版本的解密程序进行解密。

![](https://image.3001.net/images/20220919/1663557601_6327dfe16a19ddb93de22.jpg!small)

以过渡版本v1.1作为分界线，我们分别对其前后版本固件的解密进行说明。

  *  **对于v2.0及更高版本的固件即过渡版本之后的固件（假设都使用同一种加密方案，无其它过渡版本）：**

与上述场景1中描述的一致，可以通过寻找过渡版本v1.1，从中分析出v2.0的解密方法从而对v2.0固件进行解密

  *  **对于v1.0及更低版本的固件即过渡版本之前的固件（假设都使用同一种加密方案，无其它过渡版本）：**

一是可购买实体设备，通过设备的调试接口或管理服务等直接从设备中提取解密后的固件。

二是需设法获取内容完整的固件，直接对加密的固件进行分析，寻找包含在其中的解密算法。

第三种方法则比较取巧，需要历史版本固件存在RCE漏洞可以获取到设备的Linux Shell，从而分析其固件升级逻辑获取解密算法。

 **说明：**
对于上述方法没有绝对的优劣势，需根据具体情况进行选择，对于有条件的小伙伴，推荐购买相应实体设备，一是有几率通过调试接口或管理服务等直接从设备上dump出解密后的固件，二是能从Flash中提取出包含解密方法的完整版固件，以便于后续的分析。

 **2.1.3 固件出厂加密后续发布包含新版解密方案的加密固件**

固件在出厂时加密，厂商决定更改加密方案并发布一个包含新版本解密程序的加密固件，这样后续发布加密固件时可使用新版本的解密程序进行解密。

![](https://image.3001.net/images/20220919/1663557641_6327e00904dad342abdd8.jpg!small)

此类场景发布的固件自始至终都是加密形态存在的，与上述场景中v1.1及之前的固件类似，常见的解密方法有3种，具体情况得具体选择。

###  **2.2** **设备启动流程中的加解密逻辑**

接下来我们从设备启动流程来描述下固件的加解密逻辑。

![](https://image.3001.net/images/20220919/1663557651_6327e013dad1ccb5d8445.jpg!small)

首先我们来看看设备的启动流程：

  1. 设备上电后，加载芯片中的BootROM程序（芯片厂商固化在CPU中的程序）到SRAM（片内RAM，一般较小）中运行

  2. BootROM加载SPL程序（二级引导程序，可用于初始化片外更大的RAM以提供系统运行环境）到SRAM中运行

  3. SPL加载BootLoader到片外RAM中运行

  4. BootLoader随即引导内核启动

  5. 内核随后完成对文件系统的加载，执行启动脚本完成设备的最终启动

上述的启动过程包含BootROM、SPL、BootLoader、Kernel、FileSystem五大部分，其中BootROM是由芯片厂商固化在芯片内的程序，设备厂商一般无法自定义，其余四块内容厂商都可进行定制，但对SPL进行加密的场景没有见过，这里不加以赘述。下表展示了常见情况下固件中的某块数据被加密后解密方法可能存在的位置：

 **类型**

|

 **特点**

|

 **被加密后由哪块数据负责解密**  
  
---|---|---  
  
FileSystem

|

厂商核心数据

|

一般由BootLoader或者Kernel负责解密  
  
Kernel

|

开源、可定制

|

一般由BootLoader负责解密  
  
BootLoader

|

开源、可定制

|

SPL负责解密（SPL不能过大，难以植入复杂的解密逻辑）  
  
###  **2.3** **固件更新流程中的加解密逻辑**

接下来我们从设备固件升级流程来描述下固件的加解密逻辑。

![](https://image.3001.net/images/20220919/1663557694_6327e03e57a9ab7bd865e.jpg!small)

固件更新流程如下：

  1. 用户本地上传固件或者设备联网下载新版固件存储到设备Flash中

  2. 判断负责处理固件更新的后台服务是否存在解密的功能

 **a.（常见情况）** 如果有解密功能，则后台服务执行解密逻辑对固件进行解密，即当前文件系统中会存在解密逻辑代码

 **b.** 如果后台服务不负责对固件进行解密，则会在后续重启过程中由BootLoader或Kernel进行解密

  3. 设置Boot标识位后重启设备

  4. 运行新版本固件

从固件的更新流程中我们知道对固件的解密有2种情况，但由后台服务调用解密逻辑进行解密是比较常见的，所以在拿到文件系统后，如果想分析其解密逻辑以实现对其它版本固件的解密，可以从设备的固件更新功能入手来定位解密逻辑。

###  **2.4** **常见解密方法总结**

从上述固件的发布场景、设备的启动和固件升级流程中，我们发现固件的加密情况有很多种，厂商会根据设备性能、应用场景、预算等多个条件来选择适合的加密方式，某些对安全性要求较高的产品如工控设备等往往还会采用硬件加密的形式，将解密算法存储在单独的芯片中，强行读取会导致芯片损坏。(PS:在本文中我们只讲述了一些常见的解密方法和技巧，大家有更好的想法或方法欢迎在评论区留言交流)

针对物联网终端设备的固件解密，我们总结了如下五种方法和技巧：

 **基于老版本未加密固件中的解密程序实现新版本加密固件的解密**

对于固件出厂时未加密，后续发布的固件是加密的情况，可以通过对比边界版本，解包最后一个未加密版本逆向升级程序还原加密过程，以实现对加密固件的解密。

 **基于调试串口直接提取未加密固件**

如果设备存在UART、JTAG等调试接口，可通过连接硬件接口获取设备的Shell，从而dump出设备的固件。

对于可直接进入Linux Shell的情况，具体的操作可参考我们之前发布的《物联网终端安全入门与实践之玩转物联网固件（上）》一文。

但由于某些设备安全限制较高导致无法进入Linux Shell，我们可尝试进入BootLoader Shell（最常见的是Uboot
Shell）对固件进行提取。这里要说明的一点是部分设备更新固件后会将解密后的新版固件写回Flash，这种情况下dump出的固件是未加密的，而相反的是部分设备Flash中的固件一直是加密状态存在，只是在每次设备启动时进行动态解密。所以此种方法提取出的固件可能也是加密的，但好处在于可以避免因拆解设备Flash去读固件导致设备损坏的风险，并且可以获取到较为完整的固件（官方下载的固件可能只是某块数据的更新包）。

 **基于管理服务获取设备Shell提取文件系统**

对于有Telnet、SSH等服务的设备，可以通过这些服务进入设备的Linux
Shell进行固件提取。服务一般在设备的web管理页面中可手动开启，但需要说明的一点是某些厂商会开发自家的CLI屏蔽掉底层Linux
Shell，连接这些服务进入的Shell只是厂商的CLI，也无法提取文件系统，不过某些设备（光猫居多）的CLI存在可进入Linux
Shell的命令，具体可自行在互联网上搜索相应的方法。

 **基于低版本固件RCE漏洞获取设备Shell分析解密逻辑实现对新版固件的解密**

如果设备历史加密版本固件出现过RCE漏洞，可将存在漏洞的固件刷入设备，通过RCE漏洞获取设备Linux
Shell，再分析其包含的解密逻辑，最终通过该解密逻辑实现对更新版本固件的解密。需要注意的是存在RCE漏洞版本的固件所使用的加密方案需要与新版本固件一致。

 **直接分析完整固件中包含的解密逻辑实现对固件的解密**

常见情况下固件的解密逻辑肯定是存在Flash中的，当获取到完整版固件（拆机从Flash读取或者从BootLoader
Shell中提取等）后，可以直接对整个固件进行逆向分析寻找解密逻辑代码实现对固件的解密，但此种方法难度较大，并且这类设备安全性一般较高，很有可能分析出了解密逻辑但拿不到解密密钥，如密钥单独存放在某个安全芯片中。

## 0x03 解密实战

本章首先讲述一些判断固件是否被加密或压缩的方法，之后通过两个实例讲解不同场景下如何对物联网设备固件进行解密，由于篇幅限制，这里仅对上述解密方法中的其中2种辅以实例讲解，另外两种网上均有不错的分析文章，文末也会推荐相应的文章供大家学习。

###  **3.1** **判** **断固件是否被加密或压缩的方法**

对于存在过渡版本的固件，可以通过阅读厂商所发布固件的Notes关键信息，能够帮助我们判断固件从哪个版本开始进行加密。

![](https://image.3001.net/images/20220919/1663557738_6327e06a06e0beab5330a.png!small)

查看固件的熵值进行判断，熵是对随机性的一种度量，它的值在0到1之间，值越高表示随机性越好，接近1的值被认为是高熵，反之亦然，压缩或加密的数据具有较高的熵值。我们可以通过binwalk
-E以图形化的形式查看加密和未加密固件熵值的变化，如下图1中未加密的固件熵值存在较大波动，而下图2中加密的固件熵值基本都保持在1。

  

![](https://image.3001.net/images/20220919/1663557751_6327e077ee8baa843dfe4.jpg!small)  
![](https://image.3001.net/images/20220919/1663557762_6327e08264b6499bb5828.png!small)

###  **3.2** **实例一** **：** **DrayTek Vigor2962固件解密**

 **3.2.1 多角度尝试解密**

一般拿到一个加密固件后，我们可以先从多个角度对其进行分析，不要急于购买设备或者拆解设备，或许互联网上就存在着你要想的那个key。

1\.
对官网下载的固件解压以及使用binwalk解包均失败，查看熵值一直保持1，遂判断固件加密。从厂商官网和其他渠道也未发现疑似过渡版本的固件，判断此设备出厂时固件就已是加密形态存在。

2\. 在互联网上尝试搜索公开的文章或工具也无果。

3\. 为了更好的进行解密，购买一台实体设备。

![](https://image.3001.net/images/20220919/1663557776_6327e090a2bedf346243e.png!small)

4.扫描设备开放的端口，发现开启了Telnet和SSH服务。

![](https://image.3001.net/images/20220919/1663557789_6327e09d6b1d5d3488b0f.png!small)

5\. Telnet连接上后，发现是个自定义的受限CLI，尝试使用`$(telnetd -l /bin/sh -p
2323)`盲测失败。SSH登录后也是相同的情况，从Telnet、SSH获取Linux Shell的路也被堵死。

![](https://image.3001.net/images/20220919/1663557823_6327e0bf7b2fa22f382b3.png!small)

![](https://image.3001.net/images/20220919/1663558441_6327e329621e3e25c8aec.png!small)![](https://image.3001.net/images/20220919/1663558451_6327e3335d7920fdb1a7b.png!small)

6\. 互联网搜索该设备的历史漏洞，但也一无所获，无法通过历史RCE漏洞获取Linux Shell。

7\. 没办法只能拆解设备，发现存在UART串口，连接UART串口后启动设备进入的是一个Console Shell，无法进入Linux
Shell，只能从里面获取一些日志和进程信息，不能提取解密后的文件系统。

![](https://image.3001.net/images/20220919/1663558555_6327e39b2b0d1952c637b.png!small)![](https://image.3001.net/images/20220919/1663558565_6327e3a599d6f9fec35d7.png!small)![](https://image.3001.net/images/20220919/1663558575_6327e3afa2f2b71a4dbac.png!small)

 **3.2.2 Uboot Shell提取固件**

1\. 于是尝试从Uboot Shell中进行固件提取，重新启动后快速按任意键进入Uboot Shell。

![](https://image.3001.net/images/20220919/1663558841_6327e4b922b909d8edb53.png!small)

2\. 查看Uboot Shell中支持的命令。

    
    
    draytek> help 
    ?       - alias for 'help'
    base    - print or set address offset
    bdinfo  - print Board Info structure
    blkcache- block cache diagnostics and control
    boot    - boot default, i.e., run 'bootcmd'
    bootd   - boot default, i.e., run 'bootcmd'
    bootefi - Boots an EFI payload from memory
    bootelf - Boot from an ELF image in memory
    booti   - boot arm64 Linux Image image from memory
    bootm   - boot application image from memory
    bootp   - boot image via network using BOOTP/TFTP protocol
    bootvx  - Boot vxWorks from an ELF image
    bubt    - Burn a u-boot image to flash
    cmp     - memory compare
    coninfo - print console devices and information
    cp      - memory copy
    crc32   - checksum calculation
    dcache  - enable or disable data cache
    dhcp    - boot image via network using DHCP/TFTP protocol
    dm      - Driver model low level access
    dray    - Draytek ops
    draytftp- Use tftp client to get firmware then boot
    echo    - echo args to console
    editenv - edit environment variable
    efuse   - efuse - read/Write SoC eFuse entries
    
    env     - environment handling commands
    exit    - exit script
    ext2load- load binary file from a Ext2 filesystem
    ext2ls  - list files in a directory (default /)
    ext4load- load binary file from a Ext4 filesystem
    ext4ls  - list files in a directory (default /)
    ext4size- determine a file's size
    ext4write- create a file in the root directory
    false   - do nothing, unsuccessfully
    fatinfo - print information about filesystem
    fatload - load binary file from a dos filesystem
    fatls   - list files in a directory (default /)
    fatsize - determine a file's size
    fdt     - flattened device tree utility commands
    fstype  - Look up a filesystem type
    go      - start application at address 'addr'
    gpio    - query and control gpio pins
    gzwrite - unzip and write memory to block device
    help    - print command description/usage
    i2c     - I2C sub-system
    icache  - enable or disable instruction cache
    iminfo  - print header information for application image
    imxtract- extract a part of a multi-image
    ir      - ir        - Reading and changing internal register values.
    
    itest   - return true/false on integer compare
    ln      - Create a symbolic link
    load    - load binary file from a filesystem
    loadb   - load binary file over serial line (kermit mode)
    loads   - load S-Record file over serial line
    loadx   - load binary file over serial line (xmodem mode)
    loady   - load binary file over serial line (ymodem mode)
    loop    - infinite loop on address range
    ls      - list files in a directory (default /)
    lzmadec - lzma uncompress a memory region
    md      - memory display
    md5sum  - compute MD5 message digest
    mdio    - MDIO utility commands
    mii     - MII utility commands
    mm      - memory modify (auto-incrementing address)
    mmc     - MMC sub system
    mmcinfo - display MMC info
    mw      - memory write (fill)
    nfs     - boot image via network using NFS protocol
    nm      - memory modify (constant address)
    part    - disk partition related commands
    ping    - send ICMP ECHO_REQUEST to network host
    printenv- print environment variables
    pxe     - commands to get and boot from pxe files
    reset   - Perform RESET of the CPU
    run     - run commands in an environment variable
    save    - save file to a filesystem
    saveenv - save environment variables to persistent storage
    setenv  - set environment variables
    sf      - SPI flash sub-system
    showvar - print local hushshell variables
    size    - determine a file's size
    sleep   - delay execution for some time
    source  - run script from memory
    sspi    - SPI utility command
    switch  - Switch Access commands
    sysboot - command to get and boot from syslinux files
    test    - minimal test like /bin/sh
    tftpboot- boot image via network using TFTP protocol
    tftpsrv - act as a TFTP server and boot the first received file
    time    - run commands and summarize execution time
    true    - do nothing, successfully
    unzip   - unzip a memory region
    usb     - USB sub-system
    usbboot - boot from USB device
    version - print monitor, compiler and linker version

3\.
这里考虑将存储分区中的文件加载到内存后，再进行读取。使用printenv打印一下Uboot环境变量，发现了一些关键信息，rootfs.uboot.img存储在eMMC的分区2中。

>  **什么是eMMC？**
>
> eMMC ( Embedded Multi Media Card) 采用统一的MMC标准接口， 把高密度NAND Flash以及MMC
> Controller封装在一颗BGA芯片中。针对Flash的特性，产品内部已经包含了Flash管理技术，包括错误探测和纠正，Flash平均擦写，坏块管理，掉电保护等技术。用户无需担心产品内部Flash晶圆制程和工艺的变化。同时eMMC单颗芯片为主板内部节省更多的空间。
>
> 简单地说，eMMC=Nand Flash+控制器+标准封装

![](https://image.3001.net/images/20220919/1663558993_6327e5519cee98c087c6f.png!small)

这里介绍以下Uboot Shell中常见的操作eMMC的命令：

![](https://image.3001.net/images/20220919/1663559012_6327e5640f7f3f0abee8e.png!small)

    
    
    mmc list:列出当前的mmc设备mmc dev 1:切换到eMMC设备mmc part:显示当前eMMC的所有分区

常见的TypeID对应的文件系统如下表：

![](https://image.3001.net/images/20220919/1663559096_6327e5b840d084c11b922.jpg!small)

查看所有分区中的文件内容，发现rootfs.uboot.img的确存在分区2中。

 **分区1**

|
![](https://image.3001.net/images/20220919/1663559126_6327e5d60ace63fd29049.png!small)  
---|---  
  
 **分区2**

|
![](https://image.3001.net/images/20220919/1663559140_6327e5e403c5f497ada35.png!small)  
  
 **分区3**

|
![](https://image.3001.net/images/20220919/1663559161_6327e5f9d89ac0761adfb.png!small)  
  
 **分区4**

|

交换分区，无法查看  
  
 **分区5**

|
![](https://image.3001.net/images/20220919/1663559208_6327e628ac3d929c4923d.png!small)  
  
 **分区6**

|
![](https://image.3001.net/images/20220919/1663559249_6327e651e8a7ba77b2e36.png!small)  
  
5\. 由于需要提取的文件系统存在于eMMC存储（一种NAND存储）中，所以需要先将其加载至内存中，再将数据读取保存。

在Uboot Shell中将eMMC的某分区中的文件读到内存中某个地址的方法如下：

![](https://image.3001.net/images/20220919/1663559310_6327e68ea444140123d32.png!small)

从加载的地址处读取固定大小数据的方法如下

![](https://image.3001.net/images/20220919/1663559333_6327e6a5b97b8aa94b50b.png!small)

这里有个问题就是内存中读到了数据，如何保存？

  * 尝试将数据保存到U盘上，提示报了`Unsupported feature metadata_csum found, not writing.`Uboot下ext4分区不支持metadata_csum和64位特性。

  * 通过记录日志的形式：

由于我们使用的是Xshell连接的串口，而Xshell自带了日志记录功能，所以需在使用md命令读取内存中数据前将日志启动，读取完成后将日志中记录的十六进制字符串转为二进制程序即可。

![](https://image.3001.net/images/20220919/1663559349_6327e6b526ab270f2c7b3.png!small)

 **注：** 由于波特率只有115200，传输速度较慢，需要挂机跑一晚。

6\.
使用上述方法，我们最终将分区6中的image.sav文件（分区5下的uffs目录下v2962_ram_flash.bin文件无法读进内存中）从设备中dump出来，发现固件并未加密，使用binwalk可直接进行解析。

![](https://image.3001.net/images/20220919/1663559361_6327e6c1ae8967838b42e.png!small)

 **3.2.3 固件解密逻辑的分析**

这里说明下为什么拿到文件系统后还需要进一步分析其解密逻辑：

  * 官网固件是加密的，想要分析其它版本的固件，需刷入所需版本的固件后按照上述方法进行提取

  * 由于波特率较低传输速率慢，单次提取耗时较长，我们花费了几乎1晚的时间，才完成了Vigor 2962某版本未加密固件的提取

  * 分析出解密逻辑，可以直接使用该解密方法实现对其它版本固件的解密，这种以点带面的解密方法的使用，节省了大量的固件解密时间/设备采购成本

1\. 使用Binwalk解出来的ext文件系统不全。

![](https://image.3001.net/images/20220919/1663559385_6327e6d97ea1def0e3a16.png!small)

2.尝试使用挂载的方式，挂载文件系统`mount 0.ext ./ext-root`，发现能正常获取ext文件系统下的所有文件。

![](https://image.3001.net/images/20220919/1663559395_6327e6e391b7ba1de96e9.png!small)

3.尝试在文件系统下搜索字符串decrypt，发现存在一个名为decrypt_firmware的函数，该函数存在于fw_upload脚本中，根据命名推测该脚本用于处理固件更新。

![](https://image.3001.net/images/20220919/1663559409_6327e6f1e56d27ffd612d.png!small)

4\.
decrypt_firmware函数实现如下，分析其逻辑，发现chacha20应该就是解密程序，理论上只要按照该函数中解密的命令进行执行即可完成解密。

    
    
    decrypt_firmware(){input_file=$1decrypt_data_sect="/tmp/decrypt_data_sect"data_sect="/tmp/data_sect"head_sect="/tmp/head_sect"tail -c +$((256 + 64 + 64 + 1)) $input_file > $data_secthead -c $((256 + 64 + 64)) $input_file > $head_sect​enc_signature=$(head -c $((320 + 36)) $head_sect | tail -c 4)if [ "$enc_signature" == "0204" ]; thenecho "Firmware is encypt, start to decrypt."nonce=$(head -c $((320 + 48)) $head_sect | tail -c 12)/draytek/drayapp/chacha20 $data_sect $decrypt_data_sect $noncecat $head_sect $decrypt_data_sect > $input_file || abort "Unable to decrypt"rm $decrypt_data_sectfi​rm $data_sect $head_sect}​decrypt_firmware $TMP_FW_PATH

5\. 由于要执行chacha20程序，理论上由于异架构问题，需要仿真运行，而qemu-user模式不支持arm64，只能使用qemu-system模式。但是在实际操作过程中发现使用chroot切换文件系统根目录后也可以执行。

![](https://image.3001.net/images/20220919/1663565861_63280025b3ed5f66811d8.png!small)![](https://image.3001.net/images/20220919/1663565885_6328003d201ca214f966e.png!small)

6\. 最终我们对官网下载到的最新版固件也能进行解密。

![](https://image.3001.net/images/20220919/1663565899_6328004beba69f67699d4.png!small)

 **3.2.4 小结**

针对DrayTek
Vigor2962固件的解密，首先尝试寻找过渡版本以及互联网搜索公开的解密方法未果，之后尝试通过自带的SSH、Telnet服务以及历史RCE漏洞获取Shell均未成功。之后，拆机连接UART串口也无法获取到Linux
Shell。最终，利用Uboot Shell dump出eMMC分区中的未加密固件，继而分析其解密逻辑，实现了对Vigor 2962最新版本固件的解密。

###  **3.3** **实例二：** **飞某** **星VW1900设备固件解密**

由于我们已有实体设备，且已掌握该设备某版本固件的RCE漏洞，所以刷入低版本固件后，通过漏洞能够获取设备Root Shell，进而深入分析其解密逻辑。

该实例着重讲解在此种场景下定位解密程序、分析解密逻辑的方法，以实现对更高版本固件的解密。

 **3.3.1 定位解密程序**

1\. 由于我们可以获取到设备的Shell，因此我们可以通过固件升级时的一些接口信息定位后台中用于处理固件更新的具体服务。

2\. 通过BurpSuite拦截设备自动升级包。

![](https://image.3001.net/images/20220919/1663565934_6328006e89f9796e0998c.png!small)

但发现固件升级失败了。

![](https://image.3001.net/images/20220919/1663565993_632800a976e2e3cb7b518.png!small)

3\. 尝试拦截手动上传的固件更新包。

![](https://image.3001.net/images/20220919/1663566007_632800b73edcc214b10af.png!small)  
![](https://image.3001.net/images/20220919/1663566031_632800cf6603b98b309b4.png!small)

发现更新固件时调用的后台接口是一个名为manual_update.cgi程序。

4\. 在Shell终端中搜索该接口名，发现该接口功能在webserver程序中实现。

![](https://image.3001.net/images/20220919/1663566062_632800ee8da8a67e3b33f.png!small)

Ghidra加载该程序定位具体字符串，发现设备的更新功能主要在函数FUN_0001e9a8中实现。

![](https://image.3001.net/images/20220919/1663566078_632800fe4f5394738a700.png!small)

分析该函数的具体实现逻辑，首先从NVRAM中读取CPU_TYPE，根据不同值执行不同的脚本。

![](https://image.3001.net/images/20220919/1663566089_63280109e6e27bfa0ed43.png!small)

为了分析其具体执行流程，获取设备Shell后，读取nvram中相应的值，发现CPU_TYPE=bcm4708。

![](https://image.3001.net/images/20220919/1663566101_632801155788d461ff3db.png!small)

之后处理固件上传的POST请求，将加密的固件写入/mnt/code.bin文件中。

![](https://image.3001.net/images/20220919/1663566132_632801343526ea6ad0c57.png!small)

随后执行如下系统命令对固件进行解密，从命令中可看出/usr/bin/rc5-update应该就是固件的解密程序。

![](https://image.3001.net/images/20220919/1663566144_63280140753ed6b28964f.png!small)

直接在设备上测试该方法验证我们的分析结论，发现可以成功解密。

![](https://image.3001.net/images/20220919/1663566159_6328014f0667b12885755.png!small)

外传解密后的固件，使用binwalk可直接进行解包获取完整的文件系统。

![](https://image.3001.net/images/20220919/1663566170_6328015a5fc6bedf81a9c.png!small)  
![](https://image.3001.net/images/20220919/1663566183_632801674d65e37d90b45.png!small)

 **3.3.2 以点带面解密其它版本固件**

至此，我们已经知道rc5-update是解密程序以及使用方法，所以针对其它版本固件的解密，有两种思路：

  * 直接使用程序对固件进行解密，这种方法是最简单的，这里需要注意程序的架构问题

  * 分析rc5-update中的解密算法，自己编写代码实现。由于程序包含解密算法，需要有一定的逆向分析功底

 **3.3.2.1 局部仿真调用解密程序**

由于该设备是arm架构的，rc5-update无法直接在除arm架构之外的主机上运行，但可以通过局部仿真的方式运行该解密程序实现对其它版本固件的解密。具体的仿真原理和方法可参考上一篇文章。

1\. 局部仿真解密当前版本固件成功。

![](https://image.3001.net/images/20220919/1663566201_632801797597cd7f13e27.png!small)![](https://image.3001.net/images/20220919/1663566219_6328018b35b836bd8d9a2.png!small)  
2.局部仿真解密最新版本固件成功。

![](https://image.3001.net/images/20220919/1663566434_6328026237eaad6c920fe.png!small)![](https://image.3001.net/images/20220919/1663566445_6328026d635bafc44a1b4.png!small)

 **3.3.2.2 逆向解密算法**

1\. 读取内置在解密程序中的一个31字节数组数据，经过计算得出一个20字节的数组作为密钥的第一部分。

![](https://image.3001.net/images/20220919/1663566471_63280287c0d91af0d7804.png!small)2\.
该程序提供加密和解密功能，使用不同的参数进行区分。

![](https://image.3001.net/images/20220919/1663566488_63280298bbe8dfa3175a1.png!small)

3\.
读取加密固件的前10字节数据作为密钥的第二部分拼接在第一部分后面，最终根据这30字节的数组生成一个1056字节大小的最终密钥数组，之后循环读取加密固件，每8192字节作为一个block进行解密。

![](https://image.3001.net/images/20220919/1663566506_632802aaa5529752f3e66.png!small)

4\. 我们使用代码还原整个解密算法，最终能成功对加密的固件实现解密。

![](https://image.3001.net/images/20220919/1663566524_632802bca627068e8da6c.png!small)

 **3.3.3 小结**

该实例主要讲述了在拿到解密的固件后，定位解密逻辑以及分析解密算法的思路，最终通过局部仿真和自己实现解密算法2种方法实现了对其它版本固件的解密。

## 0x03 **总结**

本文从设备固件的发布场景、设备的启动流程以及固件升级流程等多方面描述了物联网终端固件常见的加解密方案，总结了5种常见的解密方法，之后详细讲述了运用其中2种方法实现解密的实例。由于篇幅的限制，另外几种解密方法本文没有给出具体的例子，文末会贴出相关的参考链接。

###  **参考链接**

> 【1】寻找过渡版本实现解密 <https://payatu.com/blog/munawwar/solving-the-problem-of-> encrypted-firmware>
>
> 【2】直接分析完整版固件实现解密 <https://cloud.tencent.com/developer/article/1005700>
>
> 【3】<https://www.freebuf.com/articles/endpoint/254257.html>

