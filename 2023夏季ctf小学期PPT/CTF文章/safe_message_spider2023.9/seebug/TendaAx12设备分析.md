**作者：The_Itach1@知道创宇404实验室  
日期：2022年11月22日**

## 设备简述

Tenda WiFi6
双频无线路由器工作在2.4GHz和5GHz频段，支持802.11ax技术，双频并发无线速率高达2976Mbps；支持OFDMA技术，实现在同一时刻多个用户同时并行传输，提高数据传输效率；支持宽带账号密码迁移，替换旧路由时，忘记宽带账号密码也不怕；支持IPv6，无需经过地址转换（NAT），上网更畅快。

![](https://images.seebug.org/content/images/2022/11/bb299938-4f7a-4196-b120-b4e235a81533.png-w331s)

这个路由器只有一个指示灯

  * 常亮， 路由器正在启动或者已联网成功
  * 慢闪，路由器未联网。
  * 快闪3秒， 网口有设备接入或者有设备移除
  * 快闪2分钟 路由器正在进行WPS协商

然后就是路由器的几个接口
![](https://images.seebug.org/content/images/2022/11/27308077-1605-444a-acbc-5d2c229bae42.png-w331s)

POWER, 电源接口，连接包装盒内的电源适配器。

  * WPS/RST，WPS、REST复用按钮。   
作为WPS按钮：按一下，即开始WPS协商，指示灯快闪（有效时间2分钟）。路由器进入WPS协商状态。2分钟内，客户端可以通过WPS-PBC方式便捷地连接到路由器的无限网络，无需输入无线密码。  
作为RST按钮：路由器正常运行时，按住此按钮约8秒，当知识点快闪时松开，路由器将会恢复出厂设置。当指示灯变成常亮时，恢复出厂设置成功。

  * WAN，互联网接口。10/100/1000Mbps自适应。用于链接光猫，DSL猫，有线电视猫，或宽带网口。 
  * 1、2、IPTV/3 内网接口、IPTV口复用，默认为内网接口。10/100/1000Mbps自适应。路由器启用IPTV功能后，默认绑定IPTV3/接口作为IPTV接口，只能连接机顶盒。根据需要可以修改IPTV口。 

里面的恢复出厂设置，我们可能会用到。

## 硬件分析

### 拆机

我们先拆机对其进行简单的分析，拆机过程对我一个新手还是比较痛苦。

观察路由器底部，只有两个螺丝，用对应的螺丝刀将其拆除，接下来就是拆开上面的那层塑料外壳，非常坚硬，并且其除了接口那一边，其他方向都是包裹着下方，缝隙很小，所以只能从接口那一方开始撬开，插解过程中，非常难撬开两边的部分，这里我是使用了很多螺丝钉(有塑料可以用塑料)，不断安放在以撬开的口中，然后继续向下撬开，最后终于拆开了外壳，发现其结构是内扣，所以拆解需要向外撬。

![](https://images.seebug.org/content/images/2022/11/045d2a40-50c1-4b75-b639-bb5bbf6b8848.png-w331s)

然后已经可以看到电路板了，但是在电路板的上面和下面还有两块金属散热板，用6个小螺丝相连。

![](https://images.seebug.org/content/images/2022/11/4a403684-7471-4f20-82c7-6d5febad6308.png-w331s)

我们这里就只用插上面的散热板，就可以看到电路板了，将整个电路板翻转过来，然后用螺丝刀将6个螺丝插下，然后发现仍然不能打开，观察后发现，散热板和下面电路板的两个金属盖之间还有一层胶，而且有两处，这里我是用细小的小刀，一点一点刮出来的，费了很多时间。

![](https://images.seebug.org/content/images/2022/11/05a575e3-e897-442a-a2ac-762ddfceb8fc.png-w331s)

接下来就可以看到整个电路板了，简单分析下电路板的一些东西。

![](https://images.seebug.org/content/images/2022/11/09ee6a40-d714-4030-81ea-f0198ecf794b.png-w331s)

蓝色的应该是4个串口，并且已经标好了名称。 紫色的是flash芯片，里面保存着固件，可根据上面的印字去找到芯片相关的信息。
绿色的就是4个天线，两个5G，2个2.4G。

然后中间的金属盖我就没有继续拆解了，没用到这个，拆解起来也比较麻烦，需要用扁形螺丝刀从边缘的缝隙去撬开。

### Flash芯片

去找了些关于flash芯片的介绍。

所谓Flash，是内存（Memory）的一种，但兼有RAM和ROM 的优点，是一种可在系统（In-System）进行电擦写，掉电后信息不丢失的存储器，同时它的高集成度和低成本使它成为市场主流。 Flash
芯片是由内部成千上万个存储单元组成的，每个单元存储一个bit。具有低功耗、大容量、擦写速度快、可整片或分扇区在系统编程（烧写）、擦除等特点，并且可由内部嵌入的算法完成对芯片的操作，因而在各种嵌入式系统中得到了广泛的应用。
作为一种非易失性存储器，Flash在系统中通常用于存放 程序 代码、常量表以及一些在系统掉电后需要保存的用户数据等。
常用的Flash为8位或16位的数据宽度，编程电压为单3.3V。主要的生产厂商为INTEL、ATMEL、AMD、HYUNDAI等。Flash
技术根据不同的应用场合也分为不同的发展方向，有擅长存储代码的NOR Flash和擅长存储数据的NAND Flash。

然后如果芯片上的印字没被擦除的话，我们完全可以通过芯片印字来获取到关于flash芯片的一些有用信息，图片来自iot-security.wiki

![](https://images.seebug.org/content/images/2022/11/0c684880-c91c-4b0f-8da5-a31dfce6164a.png-w331s)

完全可以获得厂商，flash类别，大小，编程电压，封装类型，温度等信息。

下面是Tenda Ax12的flag芯片印字，可以看到芯片印字为winbond 25Q128JVSQ 2104

![](https://images.seebug.org/content/images/2022/11/cea5d623-2cf6-4111-9255-e9955fc3cee8.png-w331s)

可以看出是华邦(winbond)的芯片，可到官网去查阅其技术文档获取更多的信息。[W25Q128JV - Serial NOR Flash - 闪存 -华邦电子 (winbond.com)](https://www.winbond.com/hq/product/code-storage-flash-memory/serial-nor-flash/index.html?__locale=zh&partNo=W25Q128JV)

![](https://images.seebug.org/content/images/2022/11/d7de67fc-2532-4584-b6e1-b427f071a670.png-w331s)

进入技术文档查看其引脚配置，如果我们打算用flash芯片来提取固件，我们需要芯片的引脚信息，Tenda Ax12的引脚应该是这一款。
![](https://images.seebug.org/content/images/2022/11/c388413f-3dab-4805-917b-379070a42f53.png-w331s)

其中第一个引脚会有一个圆点的凹槽，对应技术文档中的图片，在我上面拍摄的flash芯片也有体现。

关于Tenda
Ax12设备的flash芯片的一些信息我们就已经知道了，可以尝试对flash芯片进行固件提取，但是我这里没有设备，编程器，芯片夹这些设备，而且有点小贵。后面可能会买个便宜的CHA341A编程器，看看能不能提出来吧。

但是基本的过程还是需要知道，从芯片来提取固件主要分为两种，由于没有实操，所以更多的可能是文字描述。

  * 拆解芯片
  * 不插解芯片，飞线法读取

#### 拆解芯片提取固件

一般来说有两种插解芯片的方式，热风枪吹，还有个就是焊锡。

  * 热风枪吹：热风枪设置好合适的温度后，在芯片周围元件贴上锡箔纸进行保护，然后开吹，最后用镊子小心提取出芯片。
  * 焊锡：用电烙铁加热上锡，分别对芯片两侧进行上锡，然后，用镊子夹出。

然后就是将取出的芯片根据引脚放到弹跳座中，然后就是将USB线将编程器连接至电脑并打开编程器软件，软件自动识别芯片，提取即可，RT809F编程器，RT809H编程器都是常见的编程器，价格大概500左右。

留个具体操作的链接，方便以后实操可以看，<https://blog.csdn.net/Freedom_hzw/article/details/104216532>
这种拆解芯片的方式，优点就是离线读取，然后缺点就是必须将芯片拆下来，可能会损伤芯片，或者设备。

#### 飞线法读取

用芯片夹夹住引脚，然后另一端接到编程器上，引脚要一一对应，而且芯片夹也分种类，有像一个小夹子的，有些是带勾尖的。

然后将USB线将编程器连接至电脑并打开编程器软件，就可以识别芯片，进行固件提取了。
这种方法优点就是不用将芯片拆下来，几乎不损伤设备，但是缺点就是可能有过电保护。

后面买了一个CHA341A编程器，用芯片夹来提取了固件，下面展示下其中的操作。

用到的工具有，对应的编程器软件和驱动可以到淘宝卖家上的链接去下载。

  * CHA341A编程器：需要注意引脚1的位置
  * SOP8免拆夹：红色的线，就是引脚1
  * 转接板：上面有标注引脚

![](https://images.seebug.org/content/images/2022/11/25e852db-1f6d-4ce0-a024-d464f1a7a0c1.png-w331s)

然后将其连接起来，可参考[CH341A
编程器和SOIC8连接器免拆夹具组装方法](https://macoshome.com/hackintosh/hcourse/8672.html)。
![](https://images.seebug.org/content/images/2022/11/4a8cf45d-172d-4fb2-9708-d439f42b422b.png-w331s)

然后就是将芯片夹夹住芯片，然后usb接口接上电脑，感觉芯片夹不是太好用，那种钩子可能跟方便一点。
![](https://images.seebug.org/content/images/2022/11/a0e5da3a-1abb-40f2-b7a6-7f894a4c2ea7.png-w331s)

安装好驱动后，打开编程器软件，点击检测后，就自动识别好了flash芯片的类型，点击读取开始读取数据。
![](https://images.seebug.org/content/images/2022/11/7aaf7d22-2f6c-444f-b5a7-888edeb2aa22.png-w331s)

读取完成后保存，然后binwalk解下固件包，即可获取到文件系统。
![](https://images.seebug.org/content/images/2022/11/1cf5dd31-db90-4018-85bd-c0e6fac98450.png-w331s)

### 串口调试(UART)

采用串口调试的方式也是可以提取固件的，如果运气好，知道登录密码，或者厂商没有防护，是可以获取到设备shell的。

需要的工具有FT232，杜邦线，万用表，SecureCRT软件。
![](https://images.seebug.org/content/images/2022/11/84207dd7-4a6b-4d3a-982b-8838c2b234fb.png-w331s)

FT232 USB转UART串口模块。
![](https://images.seebug.org/content/images/2022/11/d9552475-94c5-4004-b8f5-73bfe5c54784.png-w331s)

UART引脚作用

  * VCC：供电pin，一般是3.3v-5v，正极
  * GND：接地，负极
  * RXD：接收数据引脚
  * TXD：发送数据引脚

虽然Tenda Ax12设备已经提供了引脚名称，但是我们也可以使用万用表来验证一下。

**定位GND**

将万用表扭至蜂鸣档，将一只表笔抵住电源焊锡点，另一个表笔抵住通孔位置进行测试，发出蜂鸣声的通孔，就可以初步判定为GND。

![](https://images.seebug.org/content/images/2022/11/b783930e-8670-4cd8-ba4e-ecd62395ebee.png-w331s)

**定位VCC**

将万用表扭至直流20V上，将一只表笔放置于GND上，另一只表笔依次对其它通孔进行测试，查看哪个是电压3.3V,如果是大概率就是VCC串口，虽然VCC串口我们可能用不到，但是这个我们可以排除这一个串口是其他串口的可能。

![](https://images.seebug.org/content/images/2022/11/bc932e4a-3511-4edd-b32d-ab7a5302cdfc.png-w331s)

**定位TXD**

每次有数据传输的时候该引脚电压都会发生变化。路由器开机的时候有启动信息会从这个引脚输出，这时候电压就会发生变化，此引脚即为TXD。

![](https://images.seebug.org/content/images/2022/11/105fe765-ff3e-4c27-82e2-ff7a5114908d.png-w331s)

**定位RXD**

其他3个引脚都以确认，剩下的一个就是RXD。

现在我们就知道了电路板上GND就是GND，IN就是RXD，OUT就是TXD，3V3就是VCC。但是连接杜邦线的时候需要这样连接，一般来说连GND，RXD，TXD就可以了。

  * FT232上的TXD连接到电路板的RXD(IN)
  * FT232上的RXD连接到电路板的RXD(TXD)
  * FT232上的GND连接到电路板的GND

连接完成后如下。

![](https://images.seebug.org/content/images/2022/11/cb89793d-be7a-4fb5-8dd2-ca4f40c526d0.png-w331s)

然后打开SecureCRT，网上随便都能找到下载和使用，配置好，就可以连接了。
![](https://images.seebug.org/content/images/2022/11/136a1d6d-94f9-4d17-a866-6ecedf5d25be.png-w331s)

然后重启路由器，就可以看到在打印启动日志了。
![](https://images.seebug.org/content/images/2022/11/5e63a38c-67b7-4bc9-81e3-d438e352b124.png-w331s)

由于日志太多，窗口没法完全显示，所以可以设置下，将日志导出，就可在指定目录下查看启动日志了。
![](https://images.seebug.org/content/images/2022/11/5c06dadc-0b61-46bd-b0af-3dcf3728394f.png-w331s)

大概浏览的日志内容后，可以获得一些有用的信息，文件系统是squashfs，linux版本，架构，以及挂载情况。

    
    
    20221102_10:11:42:  
    20221102_10:11:42:  ROM VER: 2.1.0
    20221102_10:11:42:  CFG 05
    20221102_10:11:42:  B
    20221102_10:11:44:  
    20221102_10:11:44:  
    20221102_10:11:44:  U-Boot 2016.07-INTEL-v-3.1.177 (Nov 25 2020 - 09:48:15 +0000)
    20221102_10:11:44:  
    20221102_10:11:44:  interAptiv
    20221102_10:11:44:  cps cpu/ddr run in 800/666 Mhz
    20221102_10:11:44:  DRAM:  224 MiB
    20221102_10:11:44:  manuf ef, jedec 4018, ext_jedec 0000
    20221102_10:11:44:  SF: Detected W25Q128BV with page size 256 Bytes, erase size 64 KiB, total 16 MiB
    20221102_10:11:44:  *** Warning - Tenda Environment, using default environment
    20221102_10:11:44:  
    20221102_10:11:44:  env size:8187, crc:a1e4bcc2 need a1e4bcc2
    20221102_10:11:44:  In:    serial
    20221102_10:11:44:  Out:   serial
    20221102_10:11:44:  Err:   serial
    20221102_10:11:44:  Net:   multi type
    20221102_10:11:44:  Internal phy firmware version: 0x8548
    20221102_10:11:44:  GRX500-Switch
    20221102_10:11:44:  
    20221102_10:11:44:  Type run flash_nfs to mount root filesystem over NFS
    20221102_10:11:44:  
    20221102_10:11:49:  Hit ESC to stop autoboot:  0 
    20221102_10:11:49:  Wait for upgrade... use GRX500-Switch
    20221102_10:11:55:  tenda upgrade timeout.
    20221102_10:11:55:  manuf ef, jedec 4018, ext_jedec 0000
    20221102_10:11:55:  SF: Detected W25Q128BV with page size 256 Bytes, erase size 64 KiB, total 16 MiB
    20221102_10:11:55:  device 0 offset 0x100000, size 0x200000
    20221102_10:11:58:  SF: 2097152 bytes @ 0x100000 Read: OK
    20221102_10:11:58:  ## Booting kernel from Legacy Image at 80800000 ...
    20221102_10:11:58:     Image Name:   MIPS UGW Linux-4.9.206
    20221102_10:11:58:     Created:      2021-08-23   9:11:35 UTC
    20221102_10:11:58:     Image Type:   MIPS Linux Kernel Image (lzma compressed)
    20221102_10:11:58:     Data Size:    2080384 Bytes = 2 MiB
    20221102_10:11:58:     Load Address: a0020000
    20221102_10:11:58:     Entry Point:  a0020000
    20221102_10:11:59:     Verifying Checksum ... OK
    20221102_10:12:01:     Uncompressing Kernel Image ... OK
    20221102_10:12:01:  [    0.000000] Linux version 4.9.206 (root@ubt1-virtual-machine) (gcc version 8.3.0 (OpenWrt GCC 8.3.0 v19.07.1_intel) ) #0 SMP Mon Aug 23 03:34:58 UTC 2021
    20221102_10:12:01:  [    0.000000] SoC: GRX500 rev 1.2
    20221102_10:12:01:  [    0.000000] CPU0 revision is: 0001a120 (MIPS interAptiv (multi))
    20221102_10:12:01:  [    0.000000] Enhanced Virtual Addressing (EVA 1GB) activated
    20221102_10:12:01:  [    0.000000] MIPS: machine is EASY350 ANYWAN (GRX350) Main model
    20221102_10:12:01:  [    0.000000] Coherence Manager IOCU detected
    20221102_10:12:01:  [    0.000000] Hardware DMA cache coherency disabled
    20221102_10:12:01:  [    0.000000] earlycon: lantiq0 at MMIO 0x16600000 (options '')
    20221102_10:12:01:  [    0.000000] bootconsole [lantiq0] enabled
    20221102_10:12:01:  [    0.000000] User-defined physical RAM map:
    20221102_10:12:01:  [    0.000000]  memory: 08000000 @ 20000000 (usable)
    20221102_10:12:01:  [    0.000000] Determined physical RAM map:
    20221102_10:12:01:  [    0.000000]  memory: 08000000 @ 20000000 (usable)
    20221102_10:12:01:  [    0.000000]  memory: 00007fa4 @ 206d7450 (reserved)
    20221102_10:12:01:  [    0.000000] Initrd not found or empty - disabling initrd
    20221102_10:12:01:  [    0.000000] cma: Reserved 32 MiB at 0x25c00000
    20221102_10:12:01:  [    0.000000] SMPCMP: CPU0: cmp_smp_setup
    20221102_10:12:01:  [    0.000000] VPE topology {2,2} total 4
    20221102_10:12:01:  [    0.000000] Detected 3 available secondary CPU(s)
    20221102_10:12:01:  [    0.000000] Primary instruction cache 32kB, VIPT, 4-way, linesize 32 bytes.
    20221102_10:12:01:  [    0.000000] Primary data cache 32kB, 4-way, PIPT, no aliases, linesize 32 bytes
    20221102_10:12:01:  [    0.000000] MIPS secondary cache 256kB, 8-way, linesize 32 bytes.
    20221102_10:12:01:  [    0.000000] Zone ranges:
    20221102_10:12:01:  [    0.000000]   DMA      [mem 0x0000000020000000-0x0000000027ffffff]
    20221102_10:12:01:  [    0.000000]   Normal   empty
    20221102_10:12:01:  [    0.000000] Movable zone start for each node
    20221102_10:12:01:  [    0.000000] Early memory node ranges
    20221102_10:12:01:  [    0.000000]   node   0: [mem 0x0000000020000000-0x0000000027ffffff]
    20221102_10:12:01:  [    0.000000] Initmem setup node 0 [mem 0x0000000020000000-0x0000000027ffffff]
    20221102_10:12:01:  [    0.000000] percpu: Embedded 12 pages/cpu s17488 r8192 d23472 u49152
    20221102_10:12:01:  [    0.000000] Built 1 zonelists in Zone order, mobility grouping on.  Total pages: 32480
    20221102_10:12:01:  [    0.000000] Kernel command line: earlycon=lantiq,0x16600000 nr_cpus=4 nocoherentio clk_ignore_unused root=/dev/mtdblock6 rw rootfstype=squashfs do_overlay console=ttyLTQ0,115200 ethaddr=D8:32:14:F8:24:08 panic=1 mtdparts=spi32766.1:512k(uboot),128k(ubootconfigA),128k(ubootconfigB),256k(calibration),2m(kernel),12m(rootfs),-(res) init=/etc/preinit active_bank= update_chk= maxcpus=4 pci=pcie_bus_perf ethwan= ubootver= mem=128M@512M 
    20221102_10:12:01:  [    0.000000] PID hash table entries: 512 (order: -1, 2048 bytes)
    20221102_10:12:01:  [    0.000000] Dentry cache hash table entries: 16384 (order: 4, 65536 bytes)
    20221102_10:12:01:  [    0.000000] Inode-cache hash table entries: 8192 (order: 3, 32768 bytes)
    20221102_10:12:01:  [    0.000000] Writing ErrCtl register=00000000
    20221102_10:12:01:  [    0.000000] Readback ErrCtl register=00000000
    20221102_10:12:01:  [    0.000000] Memory: 87656K/131072K available (5089K kernel code, 296K rwdata, 1268K rodata, 1268K init, 961K bss, 10648K reserved, 32768K cma-reserved)
    20221102_10:12:01:  [    0.000000] SLUB: HWalign=32, Order=0-3, MinObjects=0, CPUs=4, Nodes=1
    20221102_10:12:01:  [    0.000000] Hierarchical RCU implementation.
    20221102_10:12:01:  [    0.000000] NR_IRQS:527
    20221102_10:12:01:  [    0.000000] EIC is off
    20221102_10:12:01:  [    0.000000] VINT is on
    20221102_10:12:01:  [    0.000000] CPU Clock: 800000000Hz  mips_hpt_frequency 400000000Hz
    20221102_10:12:01:  [    0.000000] clocksource: gptc: mask: 0xffffffff max_cycles: 0xffffffff, max_idle_ns: 9556302233 ns
    20221102_10:12:01:  [    0.000010] sched_clock: 32 bits at 200MHz, resolution 5ns, wraps every 10737418237ns
    20221102_10:12:01:  [    0.008263] Calibrating delay loop... 531.66 BogoMIPS (lpj=2658304)
    20221102_10:12:01:  [    0.069297] pid_max: default: 32768 minimum: 301
    20221102_10:12:01:  [    0.074089] Mount-cache hash table entries: 1024 (order: 0, 4096 bytes)
    20221102_10:12:01:  [    0.080513] Mountpoint-cache hash table entries: 1024 (order: 0, 4096 bytes)
    20221102_10:12:01:  [    0.089028] CCA is coherent, multi-core is fine
    20221102_10:12:01:  [    0.098030] [vmb_cpu_alloc]:[645] CPU vpet.cpu_status = 11
    
    ····
    ····
    ····
    20221102_10:12:04:  [    2.630752] Creating 7 MTD partitions on "spi32766.1":
    20221102_10:12:04:  [    2.635944] 0x000000000000-0x000000080000 : "uboot"
    20221102_10:12:04:  [    2.641983] 0x000000080000-0x0000000a0000 : "ubootconfigA"
    20221102_10:12:04:  [    2.647466] 0x0000000a0000-0x0000000c0000 : "ubootconfigB"
    20221102_10:12:04:  [    2.652796] 0x0000000c0000-0x000000100000 : "calibration"
    20221102_10:12:04:  [    2.658323] 0x000000100000-0x000000300000 : "kernel"
    20221102_10:12:04:  [    2.663127] 0x000000300000-0x000000f00000 : "rootfs"
    20221102_10:12:04:  [    2.668196] mtd: device 6 (rootfs) set to be root filesystem
    20221102_10:12:04:  [    2.672755] 1 squashfs-split partitions found on MTD device rootfs
    20221102_10:12:04:  [    2.678831] 0x000000d00000-0x000001000000 : "rootfs_data"
    20221102_10:12:04:  [    2.685523] 0x000000f00000-0x000001000000 : "res"
    20221102_10:12:04:  [    2.689973] Lantiq SoC SPI controller rev 9 (TXFS 32, RXFS 32, DMA 1)
    20221102_10:12:04:  [    2.705499] libphy: Fixed MDIO Bus: probed
    20221102_10:12:04:  [    2.713792] libphy: gswitch_mdio: probed
    20221102_10:12:04:  [    2.719788] libphy: gswitch_mdio: probed
    20221102_10:12:04:  [    2.723371] lro_sram_membase_res0 from DT: a2013000 
    20221102_10:12:04:  [    2.727580] ltq_toe_membase: e2000000 and lro_sram_membase_res0: e2013000
    20221102_10:12:04:  [    2.734666] TOE Init Done !!

然后等待一段时间，就会出现登录了，前提是路由器要接网线(被坑了一段时间)，否则不会出现登录，猜测的原因应该是未接网线时，应该在某个地方被阻塞了，并且Tenda路由器的一些产品，都是支持Telnet连接的，但是Telnet的服务需要我们自己去打开，两个登录过程都是一样的。
![](https://images.seebug.org/content/images/2022/11/f55f19db-cb48-484c-ba70-a6db4690b52e.png-w331s)

## Shell登录

无论是串口还是Telnet，都是需要密码的，username为root，但是password不知道，但是通过搜索可以知道，对于Tenda路由器部分设备，开启Telnet服务的访问方式是<http://192.168.0.1/goform/telnet>，[CVE-2018-5770](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-5770)，并且对于密码，同样存在爆破得到密码其密码为Fireitup，CVE-2020-10988。

并且在/etc/shadow文件中，我们也能看到使用了md5加密的痕迹，想了解md5(unix)加密可以看看这篇文章[md5(unix)原理分析](https://www.jianshu.com/p/f007b81cb96f)。
我这里还是想了解下具体代码处理过程，login命令实际busybox程序处理的，于是将busybox拖到了ida中查看，发现处理过程的具体代码在sub_45A378。

先是获取用户名，然后根据这个用户名调用getpwnam函数去/etc/shadow寻找对应的名称，返回spwd结构体。
![](https://images.seebug.org/content/images/2022/11/3aa83a00-60ec-41c0-887b-6db2730faf26.png-w331s)

    
    
    struct spwd{
        char *sp_namp; /* 登录名 */ 
        char *sp_pwdp; /* 加密密码 */ 
        long sp_lstchg; /* 上次更改日期 */ 
        long sp_min; /* 更改密码的最少天数 */ 
        long sp_max; /* 更改密码的最大天数*/ 
        long sp_warn; /* 警告期 */ 
        long sp_inact; /* 最长不活动天数 */ 
        long sp_expire; /* 帐户到期日期 */ 
        unsigned long sp_flag; /* 未使用 */ 
    };

这里可以ida添加这个结构体，或许可以方便后面的分析，添加方式为View-->Open Subviews-->Local
Type，然后右键Insert，将结构体复制进去，点击ok即可，后面在对httpd文件分析的时候，也会用到Goahead里面的一些结构体。

LABEL_34:
![](https://images.seebug.org/content/images/2022/11/1f012396-5a24-45ca-ad71-471cb9d3d2ee.png-w331s)

查看验证函数，其中主要是打印Password:
字符串，并接受我们的输入，然后提取/etc/shadow中的salt，然后调用crypt()函数，将其进行md5加密，最后和密文进行比较。
![](https://images.seebug.org/content/images/2022/11/c117140e-70c3-47a4-8517-3997bad90ef9.png-w331s)

然后再贴一下hashcat的爆破过程吧，hashcat -m 500 -a 0 ./shadow.txt ./pwd.txt --force
![](https://images.seebug.org/content/images/2022/11/09f887c9-11f0-449b-bf9c-fcaaf402c242.png-w331s)

Telnet的连接实际上也是调用的这个login，Telnet服务开启会执行这样的命令。

    
    
    int __fastcall sub_41AE00(int a1)
    {
      system("/etc/init.d/telnet restart");
      sub_415368(a1, "load Telnet success.");
      return sub_415B54(a1, 200);
    }

去到对应文件查看，发现一连串下来，最后还是调用的，/bin/login
![](https://images.seebug.org/content/images/2022/11/8ad7dbad-e732-456f-8071-dc12763f0e95.png-w331s)

## 固件提取

其实除了从芯片中提取固件，还可以直接到官网下载，或者在串口获取shell后，使用一些命令，比如说nc，ftp，等命令将路由器的一些文件传出到主机中，前提是路由器的shell需要支持这些命令。

这里我采用最简单的nc命令来进行提取固件，这里我选择Telnet连接，方便一些。

首先查看系统磁盘分区信息，proc/mtd文件保存着系统的磁盘分区信息，然后使用dd命令获取Tenda Ax1的文件系统镜像。
![](https://images.seebug.org/content/images/2022/11/3feb5d73-cc3f-4238-badf-0d026f53b7dc.png-w331s)

然后关闭主机防火墙，确保路由器shell和主机之间能ping通，接着用nc命令将tenda.bin到主机中。

    
    
    nc -lp 1234 > tenda.bin

路由器shell连接上，进入tmp目录，nc连接主机，发送文件。

    
    
    cd /tmp
    nc 192.168.0.157 1234 < tenda.bin

效果如下
![](https://images.seebug.org/content/images/2022/11/27b18ce3-1c14-4b87-80ea-0811125dbfc2.png-w331s)

然后binwalk解包后的文件系统和官方的一致，如果想导出其他文件也可使用这种方式。

## Goahead源码分析

将固件解包后，就可以去看http服务对应的处理文件/usr/sbin/httpd，看了一会发现这好像是Goahead的架构，里面的回调函数很多，所以理解架构可以帮助我们理解处理流程，以及方便打断点进行调试。

搜索字符串可以发现2.1.8，所以应该是Goahead2.1.8的版本，在github上找到一个2.1.8源码:<https://github.com/trenta3/goahead-versions> 官网文档：<https://www.embedthis.com/goahead/doc>

**一些全局变量**

    
    
    //main.c
    static char_t       *rootWeb = T("web");            /* Root web directory */
    static char_t       *password = T("");              /* Security password */
    static int          port = 80;                      /* Server port */
    static int          retries = 5;                    /* Server port retries */
    static int          finished;                       /* Finished flag */
    
    //sock.c
    socket_t    **socketList;           /* List of open sockets */
    int         socketMax;              /* Maximum size of socket */
    int         socketHighestFd = -1;   /* Highest socket fd opened */
    
    
    //handler.c
    static websUrlHandlerType   *websUrlHandler;            /* URL handler list */
    static int                  websUrlHandlerMax;          /* Number of entries */
    static int                  urlHandlerOpenCount = 0;    /* count of apps */

rootWeb就是Web服务器的根目录，在Tenda Ax12中，实际上就是/www。
然后就是密码password，端口port为80端口，尝试次数retries为5，finished则是一个循环的标志。

socketList是一个结构体数组，保存所有的socket，socketMax是当前所有socket的数量值。

websUrlHandler是一个指针数组，指向websUrlHandlerType这个结构体，这个结构体后面会分析。websUrlHandlerMax就是当前url
handler的数量值。

**main.c**

    
    
    /*
     *  Main -- entry point from LINUX
     */
    
    int main(int argc, char** argv)
    {
    /*
     *  Initialize the memory allocator. Allow use of malloc and start 
     *  with a 60K heap.  For each page request approx 8KB is allocated.
     *  60KB allows for several concurrent page requests.  If more space
     *  is required, malloc will be used for the overflow.
     */
        bopen(NULL, (60 * 1024), B_USE_MALLOC);
        signal(SIGPIPE, SIG_IGN);
    
    /*
     *  Initialize the web server
     */
        if (initWebs() < 0) {
            return -1;
        }
    
    #ifdef WEBS_SSL_SUPPORT
        websSSLOpen();
    #endif
    
    /*
     *  Basic event loop. SocketReady returns true when a socket is ready for
     *  service. SocketSelect will block until an event occurs. SocketProcess
     *  will actually do the servicing.
     */
        while (!finished) {
            if (socketReady(-1) || socketSelect(-1, 1000)) {
                socketProcess(-1);
            }
            websCgiCleanup();
            emfSchedProcess();
        }
    
    #ifdef WEBS_SSL_SUPPORT
        websSSLClose();
    #endif
    
    #ifdef USER_MANAGEMENT_SUPPORT
        umClose();
    #endif
    
    /*
     *  Close the socket module, report memory leaks and close the memory allocator
     */
        websCloseServer();
        socketClose();
    #ifdef B_STATS
        memLeaks();
    #endif
        bclose();
        return 0;
    }

可以看到先是bopen()分配了内存，然后调用了initWebs()去初始化web服务，这个函数也是后面要重点分析的函数。
然后就是while循环，里面有下面几个函数

  * socketReady()，就是判断是否存在准备处理事件的套接字，有则会返回TRUE，其实现方式是遍历socketList，获取socket_t *sp的结构体成员信息进行if判断。
  * socketSelect()，此调用使用由 socketRegisterInterest 定义的感兴趣事件的掩码。它阻塞调用者，直到发生合适的 I/O 事件或超时。
  * socketProcess()，处理挂起的套接字 I/O 事件。
  * websCgiCleanup()，需要检查 cgiList 中的任何条目是否已完成，如果已完成，则处理其输出并清理。
  * emfSchedProcess()，以循环方式将任务从队列中取出。

后面部分就是关闭WebServer，关闭套接字，释放内存，分别由websCloseServer()，socketClose()，bclose()实现。

**initWebs()**

    
    
    static int initWebs()
    {
        struct hostent  *hp;
        struct in_addr  intaddr;
        char            host[128], dir[128], webdir[128];
        char            *cp;
        char_t          wbuf[128];
    
    /*
     *  Initialize the socket subsystem
     */
        socketOpen();
    
    #ifdef USER_MANAGEMENT_SUPPORT
    /*
     *  Initialize the User Management database
     */
        umOpen();
        umRestore(T("umconfig.txt"));
    #endif
    
    /*
     *  Define the local Ip address, host name, default home page and the 
     *  root web directory.
     */
        if (gethostname(host, sizeof(host)) < 0) {
            error(E_L, E_LOG, T("Can't get hostname"));
            return -1;
        }
        if ((hp = gethostbyname(host)) == NULL) {
            error(E_L, E_LOG, T("Can't get host address"));
            return -1;
        }
        memcpy((char *) &intaddr, (char *) hp->h_addr_list[0],
            (size_t) hp->h_length);
    
    
    
    /*
     *  Set ../web as the root web. Modify this to suit your needs
     */
        getcwd(dir, sizeof(dir)); 
        if ((cp = strrchr(dir, '/'))) {
            *cp = '\0';
        }
        sprintf(webdir, "%s/%s", dir, rootWeb);
    
    /*
     *  Configure the web server options before opening the web server
     */
        websSetDefaultDir(webdir);
        cp = inet_ntoa(intaddr);
        ascToUni(wbuf, cp, min(strlen(cp) + 1, sizeof(wbuf)));
        websSetIpaddr(wbuf);
        ascToUni(wbuf, host, min(strlen(host) + 1, sizeof(wbuf)));
        websSetHost(wbuf);
    
    /*
     *  Configure the web server options before opening the web server
     */
        websSetDefaultPage(T("default.asp"));
        websSetPassword(password);
    
    /* 
     *  Open the web server on the given port. If that port is taken, try
     *  the next sequential port for up to "retries" attempts.
     */
        websOpenServer(port, retries);
    
    /*
     *  First create the URL handlers. Note: handlers are called in sorted order
     *  with the longest path handler examined first. Here we define the security 
     *  handler, forms handler and the default web page handler.
     */
        websUrlHandlerDefine(T(""), NULL, 0, websSecurityHandler, 
            WEBS_HANDLER_FIRST);
        websUrlHandlerDefine(T("/goform"), NULL, 0, websFormHandler, 0);
        websUrlHandlerDefine(T("/cgi-bin"), NULL, 0, websCgiHandler, 0);
        websUrlHandlerDefine(T(""), NULL, 0, websDefaultHandler, 
            WEBS_HANDLER_LAST); 
    
    /*
     *  Now define two test procedures. Replace these with your application
     *  relevant ASP script procedures and form functions.
     */
        websAspDefine(T("aspTest"), aspTest);
        websFormDefine(T("formTest"), formTest);
    
    /*
     *  Create the Form handlers for the User Management pages
     */
    #ifdef USER_MANAGEMENT_SUPPORT
        formDefineUserMgmt();
    #endif
    
    /*
     *  Create a handler for the default home page
     */
        websUrlHandlerDefine(T("/"), NULL, 0, websHomePageHandler, 0); 
        return 0;
    }

先是调用socketOpen()，初始化socket系统，就是对sock.c的一些全局变量进行初始化。 然后对IP，host
name，还有网页的根目录进行获取和赋值。
调用websSetDefaultDir()设置根目录，websSetIpaddr()设置ip地址，websSetHost()设置host name。
websSetDefaultPage()设置默认访问页，websSetPassword()设置密码。 websOpenServer(port,
retries)，在指定端口打开webserver
如果这个端口不可用，就延续下一个，retries就是失败后可尝试的次数，里面实现了对websUrlHandler，websUrlHandlerMax的初始化，都为0。

下面要分析的就是websUrlHandlerDefine和一些结构体了，这是搞懂Gohead是如何如何处理前端发过来的请求的关键地方。

先来看下 **websUrlHandlerType** 结构体

    
    
    typedef struct {
        int     (*handler)(webs_t wp, char_t *urlPrefix, char_t *webDir, int arg, 
                char_t *url, char_t *path, 
                char_t *query);                 /* Callback URL handler function */
        char_t  *webDir;                        /* Web directory if required */
        char_t  *urlPrefix;                     /* URL leading prefix */
        int     len;                            /* Length of urlPrefix for speed */
        int     arg;                            /* Argument to provide to handler */
        int     flags;                          /* Flags */
    } websUrlHandlerType;

可以看到，其包含了以下成员

  * 函数指针handler，是这个Url的回调处理函数。
  * 然后就是webDir，Web 目录的可选根目录路径，但是给websUrlHandlerDefine函数传参是，一般都为0。
  * urlPrefix，要匹配的 URL 前缀，比如说“/goform”，"/cgi-bin"，“/”，“”等。
  * len，urlPrefix字符串的长度，后面排序会用到。
  * arg，传递给处理函数的参数。
  * flags，定义匹配顺序，有两个WEBS_HANDLER_LAST、WEBS_HANDLER_FIRST，那些先进行处理，那些后进行处理。

再来看看 **webs_t** 结构体

    
    
    /* 
     *  Per socket connection webs structure
     */
    typedef struct websRec {
        ringq_t         header;             /* Header dynamic string */
        time_t          since;              /* Parsed if-modified-since time */
        sym_fd_t        cgiVars;            /* CGI standard variables */
        sym_fd_t        cgiQuery;           /* CGI decoded query string */
        time_t          timestamp;          /* Last transaction with browser */
        int             timeout;            /* Timeout handle */
        char_t          ipaddr[32];         /* Connecting ipaddress */
        char_t          type[64];           /* Mime type */
        char_t          *dir;               /* Directory containing the page */
        char_t          *path;              /* Path name without query */
        char_t          *url;               /* Full request url */
        char_t          *host;              /* Requested host */
        char_t          *lpath;             /* Cache local path name */
        char_t          *query;             /* Request query */
        char_t          *decodedQuery;      /* Decoded request query */
        char_t          *authType;          /* Authorization type (Basic/DAA) */
        char_t          *password;          /* Authorization password */
        char_t          *userName;          /* Authorization username */
        char_t          *cookie;            /* Cookie string */
        char_t          *userAgent;         /* User agent (browser) */
        char_t          *protocol;          /* Protocol (normally HTTP) */
        char_t          *protoVersion;      /* Protocol version */
        int             sid;                /* Socket id (handler) */
        int             listenSid;          /* Listen Socket id */
        int             port;               /* Request port number */
        int             state;              /* Current state */
        int             flags;              /* Current flags -- see above */
        int             code;               /* Request result code */
        int             clen;               /* Content length */
        int             wid;                /* Index into webs */
        char_t          *cgiStdin;          /* filename for CGI stdin */
        int             docfd;              /* Document file descriptor */
        int             numbytes;           /* Bytes to transfer to browser */
        int             written;            /* Bytes actually transferred */
        void            (*writeSocket)(struct websRec *wp);
    #ifdef DIGEST_ACCESS_SUPPORT
        char_t          *realm;     /* usually the same as "host" from websRec */
        char_t          *nonce;     /* opaque-to-client string sent by server */
        char_t          *digest;    /* digest form of user password */
        char_t          *uri;       /* URI found in DAA header */
        char_t          *opaque;    /* opaque value passed from server */
        char_t          *nc;        /* nonce count */
        char_t          *cnonce;    /* check nonce */
        char_t          *qop;       /* quality operator */
    #endif
    #ifdef WEBS_SSL_SUPPORT
        websSSL_t       *wsp;       /* SSL data structure */
    #endif
    } websRec;
    
    typedef websRec *webs_t;
    typedef websRec websType;

这个就是每个套接字连接网络的结构体，包含了很多信息，就像我们bp抓包里面包含的那些信息。

还有个就是 **socket_t**

    
    
    typedef struct {
        char            host[64];               /* Host name */
        ringq_t         inBuf;                  /* Input ring queue */
        ringq_t         outBuf;                 /* Output ring queue */
        ringq_t         lineBuf;                /* Line ring queue */
        socketAccept_t  accept;                 /* Accept handler */
        socketHandler_t handler;                /* User I/O handler */
        int             handler_data;           /* User handler data */
        int             handlerMask;            /* Handler events of interest */
        int             sid;                    /* Index into socket[] */
        int             port;                   /* Port to listen on */
        int             flags;                  /* Current state flags */
        int             sock;                   /* Actual socket handle */
        int             fileHandle;             /* ID of the file handler */
        int             interestEvents;         /* Mask of events to watch for */
        int             currentEvents;          /* Mask of ready events (FD_xx) */
        int             selectEvents;           /* Events being selected */
        int             saveMask;               /* saved Mask for socketFlush */
        int             error;                  /* Last error */
    } socket_t;

这是socket套接字的结构体。

接下来分析websUrlHandlerDefine函数，这个函数是用来注册各个URL具体的处理函数的。

    
    
    /******************************************************************************/
    /*
     *  Define a new URL handler. urlPrefix is the URL prefix to match. webDir is 
     *  an optional root directory path for a web directory. arg is an optional
     *  arg to pass to the URL handler. flags defines the matching order. Valid
     *  flags include WEBS_HANDLER_LAST, WEBS_HANDLER_FIRST. If multiple users 
     *  specify last or first, their order is defined alphabetically by the 
     *  urlPrefix.
     */
    
    int websUrlHandlerDefine(char_t *urlPrefix, char_t *webDir, int arg,
            int (*handler)(webs_t wp, char_t *urlPrefix, char_t *webdir, int arg, 
            char_t *url, char_t *path, char_t *query), int flags)
    {
        websUrlHandlerType  *sp;
        int                 len;
    
        a_assert(urlPrefix);
        a_assert(handler);
    
    /*
     *  Grow the URL handler array to create a new slot
     */
        len = (websUrlHandlerMax + 1) * sizeof(websUrlHandlerType);
        if ((websUrlHandler = brealloc(B_L, websUrlHandler, len)) == NULL) {
            return -1;
        }
        sp = &websUrlHandler[websUrlHandlerMax++];
        memset(sp, 0, sizeof(websUrlHandlerType));
    
        sp->urlPrefix = bstrdup(B_L, urlPrefix);
        sp->len = gstrlen(sp->urlPrefix);
        if (webDir) {
            sp->webDir = bstrdup(B_L, webDir);
        } else {
            sp->webDir = bstrdup(B_L, T(""));
        }
        sp->handler = handler;
        sp->arg = arg;
        sp->flags = flags;
    
    /*
     *  Sort in decreasing URL length order observing the flags for first and last
     */
        qsort(websUrlHandler, websUrlHandlerMax, sizeof(websUrlHandlerType), 
            websUrlHandlerSort);
        return 0;
    }

先定义了结构体指针sp，然后计算了长度len，分配内存空间，根据websUrlHandlerMax计算偏移，然后给sp结构体赋值，最后就是对所有的url
handler进行个排序。

回到initWebs，分别有这几种，安全处理程序，表单处理程序和默认网页处理程序，默认主页创建处理程序

    
    
    websUrlHandlerDefine(T(""), NULL, 0, websSecurityHandler, WEBS_HANDLER_FIRST);
    websUrlHandlerDefine(T("/goform"), NULL, 0, websFormHandler, 0);
    websUrlHandlerDefine(T("/cgi-bin"), NULL, 0, websCgiHandler, 0);
    websUrlHandlerDefine(T(""), NULL, 0, websDefaultHandler, WEBS_HANDLER_LAST);
    websUrlHandlerDefine(T("/"), NULL, 0, websHomePageHandler, 0); 

接下来我们要找到其是如何调用的这些handler，我们对全局变量websUrlHandler进行搜索，最后找到其在handler.c的websUrlHandlerRequest(webs_t
wp)函数中找到了其调用方式。

**websUrlHandlerRequest(webs_t wp)**

    
    
    /******************************************************************************/
    /*
     *  See if any valid handlers are defined for this request. If so, call them
     *  and continue calling valid handlers until one accepts the request. 
     *  Return true if a handler was invoked, else return FALSE.
     */
    
    int websUrlHandlerRequest(webs_t wp)
    {
        websUrlHandlerType  *sp;
        int                 i, first;
    
        a_assert(websValid(wp));
    
    /*
     *  Delete the socket handler as we don't want to start reading any
     *  data on the connection as it may be for the next pipelined HTTP/1.1
     *  request if using Keep Alive
     */
        socketDeleteHandler(wp->sid);
        wp->state = WEBS_PROCESSING;
        websStats.handlerHits++;
    
        websSetRequestPath(wp, websGetDefaultDir(), NULL);
    
    /*
     *  Eliminate security hole
     */
        websCondenseMultipleChars(wp->path, '/');
        websCondenseMultipleChars(wp->url, '/');
    
    /*
     *  We loop over each handler in order till one accepts the request. 
     *  The security handler will handle the request if access is NOT allowed.
     */
        first = 1;
        for (i = 0; i < websUrlHandlerMax; i++) {
            sp = &websUrlHandler[i];
            if (sp->handler && gstrncmp(sp->urlPrefix, wp->path, sp->len) == 0) {
                if (first) {
                    websSetEnv(wp);
                    first = 0;
                }
                if ((*sp->handler)(wp, sp->urlPrefix, sp->webDir, sp->arg, 
                        wp->url, wp->path, wp->query)) {
                    return 1;
                }
                if (!websValid(wp)) {
                    trace(0, 
                    T("webs: handler %s called websDone, but didn't return 1\n"),
                        sp->urlPrefix);
                    return 1;
                }
            }
        }
    /*
     *  If no handler processed the request, then return an error. Note: It is 
     *  the handlers responsibility to call websDone
     */
        if (i >= websUrlHandlerMax) {
          /*
           * 13 Mar 03 BgP
           * preventing a cross-site scripting exploit
            websError(wp, 200, T("No handler for this URL %s"), wp->url);
           */
            websError(wp, 200, T("No handler for this URL"));
        }
        return 0;
    }
    
    #ifdef OBSOLETE_CODE

所有的请求都会到这个函数来寻找其对应的有效处理程序，具体过程如下

  * 调用socketDeleteHandler (wp->sid)，删除通过 socketCreateHandler 创建的套接字处理程序。
  * 然后处理一些路径安全的问题。
  * 接着for循环遍历websUrlHandler，根据sp->urlPrefix字符串，来决定对应的handler处理函数。

到这里就又产生了个问题，websUrlHandlerRequest是在哪调用的呢，不断向上跟会有这样一个调用链。

    
    
    apl
    websSocketEvent()
         |--判断读写操作
         |--读websReadEvent()
         |      |--websUrlHandlerRequest()
         |          |--查找wbsUrlHandler数组,调用和urlPrefix对应的回调函数(websFormHandler(),websDefaultHandler()等)
         |
         |--写,调用(wp->writeSocket)回调函数

接着我们需要知道websSocketEvent是哪来的，搜索发现，其是socketCreateHandler 创建的套接字处理程序。

    
    
    apl
    websOpenServer()
        |--websOpenListen()
            |--调用socketOpenConnection(NULL, port, websAccept, 0)，可是socketOpenConnection我在官方文档中并没有找到解释。
            |--websAccept()
                 |--做一些检查
                 |--socketCreateHandler(sid, SOCKET_READABLE, websSocketEvent, (int) wp)
                 |            |--把sid注册为读事件,初始化socket_t sp->handler = websSocketEvent等, 更新对应的socketList数组(handlerMask值等)

可以看出，是对socket_t
sp->handler进行了赋值，所以其实最开始的地方就是在main函数中的while循环中，执行socketProcess()，从而调用socket_t
sp->handler的处理函数进行相应的处理，下面是main函数中while循环的调用链。

    
    
    |--(main loop)
    |   |--socketReady(-1) || socketSelect(-1, 1000)
    |   |   |--轮询socketList     |--轮询socketList中的handlerMask
    |   |   |--中的几个变量           |--改变socketList中的currentEvents
    |   |
    |   |--socketProcess()
    |           |--轮询socketList[]
    |           |--socketReady()
    |           |--socketDoEvent()
    |                   |--如果有新的连接(来自listenfd)就调用socketAccept()
    |                   |           |--调用socketAlloc()初始化socket_t结构
    |                   |           |--把socket_t结构加入 socketList数组
    |                   |           |--调用socket_t sp->accept()回调函数
    |                   |
    |                   |--如果不是新的连接就查找socketList数组调用socket_t sp->handler()回调函数

现在我们知道了这些url
handler是如何被调用的了，但是还有个问题需要解决，就是websFormHandler表单处理程序，也就是当我们传入表单，发送post请求时的handler，在Goahead中，是这样定义ASP
脚本程序和表单功能的。

    
    
    /*
     *  Now define two test procedures. Replace these with your application
     *  relevant ASP script procedures and form functions.
     */
        websAspDefine(T("aspTest"), aspTest);
        websFormDefine(T("formTest"), formTest);
    
    /*
     *  Define an ASP Ejscript function. Bind an ASP name to a C procedure.
     */
    
    int websAspDefine(char_t *name, 
        int (*fn)(int ejid, webs_t wp, int argc, char_t **argv))
    {
        return ejSetGlobalFunctionDirect(websAspFunctions, name, 
            (int (*)(int, void*, int, char_t**)) fn);
    }
    
    /*
     *  Define a form function in the "form" map space.
     */
    
    int websFormDefine(char_t *name, void (*fn)(webs_t wp, char_t *path, 
        char_t *query))
    {
        a_assert(name && *name);
        a_assert(fn);
    
        if (fn == NULL) {
            return -1;
        }
    
        symEnter(formSymtab, name, valueInteger((int) fn), (int) NULL);
        return 0;
    }
    
    
    static sym_fd_t formSymtab = -1;            /* Symbol table for form handlers */
    
    
    /*
     *  The symbol table record for each symbol entry
     */
    
    typedef struct sym_t {
        struct sym_t    *forw;                  /* Pointer to next hash list */
        value_t         name;                   /* Name of symbol */
        value_t         content;                /* Value of symbol */
        int             arg;                    /* Parameter value */
    } sym_t;
    
    typedef int sym_fd_t;                       /* Returned by symOpen */
    
    
    typedef struct {
    
        union {
            char    flag;
            char    byteint;
            short   shortint;
            char    percent;
            long    integer;        //注意这个，根据后面分析，这个代表了form表单的函数地址
            long    hex;
            long    octal;
            long    big[2];
    #ifdef FLOATING_POINT_SUPPORT
            double  floating;
    #endif /* FLOATING_POINT_SUPPORT */
            char_t  *string;
            char    *bytes;
            char_t  *errmsg;
            void    *symbol;
        } value;
    
        vtype_t         type;
        unsigned int    valid       : 8;
        unsigned int    allocated   : 8;        /* String was balloced */
    } value_t;

在Tenda Ax12中，更多使用的是websFormDefine，通过上面的代码，我们可以知道下面的信息。

  * `symEnter(formSymtab, name, valueInteger((int) fn), (int) NULL);`，虽然找不到symEnter的定义，但是可以分析出来，这个函数应该是不断向链表插入定义的form表单处理程序，主要包含name和具体的函数地址。

  * formSymtab全局变量应该是指向sym_t结构体链表的表头。

接下来分析 **websFormHandler()**

    
    
    /*
     *  Process a form request. Returns 1 always to indicate it handled the URL
     */
    
    int websFormHandler(webs_t wp, char_t *urlPrefix, char_t *webDir, int arg, 
        char_t *url, char_t *path, char_t *query)
    {
        sym_t       *sp;
        char_t      formBuf[FNAMESIZE];
        char_t      *cp, *formName;
        int         (*fn)(void *sock, char_t *path, char_t *args);
    
        a_assert(websValid(wp));
        a_assert(url && *url);
        a_assert(path && *path == '/');
    
        websStats.formHits++;
    
    /*
     *  Extract the form name
     */
        gstrncpy(formBuf, path, TSZ(formBuf));
        if ((formName = gstrchr(&formBuf[1], '/')) == NULL) {
            websError(wp, 200, T("Missing form name"));
            return 1;
        }
        formName++;
        if ((cp = gstrchr(formName, '/')) != NULL) {
            *cp = '\0';
        }
    
    /*
     *  Lookup the C form function first and then try tcl (no javascript support 
     *  yet).
     */
        sp = symLookup(formSymtab, formName);
        if (sp == NULL) {
            websError(wp, 200, T("Form %s is not defined"), formName);
        } else {
            fn = (int (*)(void *, char_t *, char_t *)) sp->content.value.integer;
            a_assert(fn);
            if (fn) {
    /*
     *          For good practice, forms must call websDone()
     */
                (*fn)((void*) wp, formName, query);
    
    /*
     *          Remove the test to force websDone, since this prevents
     *          the server "push" from a form>
     */
    #if 0 /* push */
                if (websValid(wp)) {
                    websError(wp, 200, T("Form didn't call websDone"));
                }
    #endif /* push */
            }
        }
        return 1;
    }

整个过程如下

    
    
    |--websFormHandler()
    |       |--strncpy(),strchr()                   获取formName
    |       |--symLookup(formSymtab, formName)      遍历链表，根据name返回对应的结构体。
    |       |--sp->content.value.integer            从结构体中获取到函数地址。
    |       |--(*fn)((void*) wp, formName, query);  执行函数

到这里，关于Goahead源码的分析就差不多了，上面分析的内容可以帮助我们更好的去分析Tenda
AX12的httpd程序，比如如何找到开发者自定义的处理函数，还有整个数据的处理流程，以及ida伪代码符号表，结构体的恢复。

## httpd漏洞挖掘

虽然网上关于Tenda路由器设备的cve很多，大部分是堆栈溢出，少部分命令注入，但是实际上这些cve在真实环境下是没法利用的，基本上全都需要身份验证，因为Tenda路由器的安全处理函数处理得很好，在我分析完整个登录过程以及cookie验证过程，都没找到绕过的方式，所以还是只能搞一些经过身份验证的漏洞，然后还是收获了一些漏洞，分析过程中，我也使用了之前自己搞的一个idapython脚本插件[Audit](https://github.com/The-Itach1/Audit)，可以帮助快速定位到一些函数，节省了一些时间。

以下的漏洞攻击，都需要在有一次身份验证下，也就是有一次可用的cookie，才能进行攻击。

### 启动部分分析

来到main函数，大部分的过程和Goahead的源码差不多，但是有些区别的是host和username和userpass的获取方式。
![](https://images.seebug.org/content/images/2022/11/1d66d6bd-2b90-4a37-b5d8-fe97d13133f7.png-w331s)

可以看到是调用GetValue这个函数，但究竟是从哪获取到的呢，获取到这个信息可能可以帮助我们找到userpass的存储位置，这里我没找到关于GetValue这个函数的具体实现资料，但是我找到了关于[OpenWrt系统UCI详解](https://blog.csdn.net/dxt1107/article/details/115742249)的资料。

这些类似于network.lan.proto的字符串实际上都是uci的配置格式，其会保存在某个具体的配置文件中，一般都在etc目录下，GetValue这个函数的内部，推断应该就是使用了的内置函数来对值进行获取。

然后我先是先对binwalk分离的固件进行了grep匹配特征字符串，发现并没有找到对应的配置文件，最后感觉还是得去真实设备中去匹配，Telnet连接上后进行匹配，成功找到username和userpass在/etc/config/admin文件中，proto,ipaddr在/etc/config/network中。
![](https://images.seebug.org/content/images/2022/11/02ea10a6-1b92-4bba-944b-c4a39810012a.png-w331s)

![](https://images.seebug.org/content/images/2022/11/bf29c55e-f88a-411f-87f7-f7f13ad6f9d4.png-w331s)

### web登录后台验证过程分析

分析了Goahead的源码后，我们知道了这种框架的数据处理过程，以及一些结构体，我们可以恢复这些结构体，以及去官方找一些mips架构的老固件来进行一些符号表的修复，让分析过程变得简单一些。

#### 调试环境搭建

ida反编译出来的代码还是比较多，所以肯定需要进行调试分析，先搭建调试环境。
首先去根据路由器架构下载对应编译好的gdbserver，这里我是下载的gdbserver-7.12-mips-mips32rel2-v1-sysv。

接下来就是和前面传固件的方式，用nc命令来传文件到路由器的linux系统中，只不过有点不一样的是这次是从主机传文件到路由器。

同样也是关闭windows的防火墙，确保主机和路由器能ping通，主机监听一个端口，并传入文件。

    
    
    nc -lp 1234 < gdbserver-7.12-mips-mips32rel2-v1-sysv

路由器shell连接上，进入tmp目录，nc连接主机，接收文件。

    
    
    cd /tmp
    nc 192.168.0.157 1234 > gdbserver

然后给gdbserver文件提供可执行权限。

    
    
    chmod 777 ./gdbserver

效果如下。
![](https://images.seebug.org/content/images/2022/11/868296bf-83fc-4906-b81d-ee2d07ffc094.png-w331s)

然后gdbserver开启监听端口附加调试即可。
![](https://images.seebug.org/content/images/2022/11/0ce081f6-9f1b-4d3d-bc1b-2580547e1b21.png-w331s)

成功后，会出现Remote debugging from host ip。

#### 前端分析

首先先对前端登录的发包过程进行分析，随便输入一个密码试一下，然后抓个包。
![](https://images.seebug.org/content/images/2022/11/23083d04-1ac1-4f64-9a90-cea644a8dc77.png-w331s)

可以看到，访问了/login/Auth这个接口，username默认为admin，password为md5(input)，并且处理这个过程的文件应该是login.js。

可在浏览器中调试一下，大概分析下流程就是，注册了一个登陆过程的回调函数。

    
    
    var serviceUrl = '/login/Auth',
    authService = new PageService(serviceUrl),
    loginPageView = new PageView(),
    loginPageLogin = new PageLogic(loginPageView, authService);
    
    loginPageLogin.init();

然后每当登陆键按下，则会触发处理函数。

    
    
    view.addSubmitHandler(function () {
            that.validate.checkAll();
        });
    
    this.addSubmitHandler = function (callBack) {
        $('#subBtn').on('click', function (e) {
            e.preventDefault();
            callBack.apply();
        });

接下来就是，获取username和password，检测是否有效，然后将password进行md5加密，然后发送到后端。

    
    
    this.validate = $.validate({
        custom: function () {
            var username = view.getUsername(),
                password = view.getPassword();
    
            function checksValid(username, password) {
                return username !== '' && password !== '';
            }
    
            if (!checksValid(username, password)) {
                return _("Please specify a login password.");
            }
    
        },
    
        success: function () {
            var data = view.getSubmitData();
    
            authService.login(data, view.showSuccessful, view.showError);
        },
    
        error: function (msg) {
            view.showInvalidError(msg);
        }
    });
        //md5加密password，返回表单
        this.getSubmitData = function () {
            var ret = '';
    
            ret = {
                username: this.getUsername(),
                password: hex_md5(this.getPassword())
            };
    
            return ret;
        };
    
        //调用login函数，以POST的方式发送到后端进行验证
        this.login = function (subData, successCallback, errorCallback) {
            $.ajax({
                url: url,
                type: "POST",
                data: subData,
                success: successCallback,
                error: errorCallback
            });
        };

然后会根据后端传的值来决定，是否显示登陆错误，如果传的值为1，就代表密码错误。

    
    
        this.showSuccessful = function (str) {
            var num = str;
            if (num == 1) {
                $('#login-message').html(_("Incorrect password."));
            } else {
                // window.location.href = "/main.html"; //解决android系统下360浏览器不能正常登陆问题
                window.location.reload(true);
            }

这里我们就明白了登陆过程中前端是如何向后端发送数据的了。

#### 分析R7WebsSecurityHandler()

这个函数是路由器的安全处理函数，无论访问什么url，都会经过这个函数，登录后台的验证，以及访问各种接口时的cookie验证都在这个函数进行处理。

我们直接先访问http://ip，但是实际上的url会是http://ip/，其会先经过R7WebsSecurityHandler()，遍历一些接口，发现都不是，然后就会return
0，下面这些资源，都是可直接访问的，不需要验证。

    
    
      v12 = strncmp(a5, "/public/", 8);
      v13 = 4521984;
      if ( !v12 )
        goto LABEL_24;
      v14 = strncmp(a5, "/lang/", 6);
      v13 = 4521984;
      if ( !v14 )
        goto LABEL_24;
      if ( strstr(a5, "img/main-logo.png") )
        goto LABEL_24;
      if ( strstr(a5, "reasy-ui-1.0.3.js") )
        goto LABEL_24;
      if ( !strncmp(a5, "/favicon.ico", 12) )
        goto LABEL_24;
      v13 = 4521984;
      if ( !*(_DWORD *)&wp->type[22] )
        goto LABEL_24;
      v15 = strncmp(a5, "/kns-query", 10);
      v13 = 4521984;
      if ( !v15 )
        goto LABEL_24;
      if ( !strncmp(a5, "/wdinfo.php", 11) )
        goto LABEL_24;
      v16 = strlen((int)a5);
      v13 = 4521984;
      if ( v16 == 1 && *a5 == 47 )
        goto LABEL_24;
      v17 = strncmp(a5, "/redirect.html", 14);
      v13 = 4521984;
      if ( !v17 || !strncmp(a5, "/goform/getRebootStatus", 23) )
      {
    LABEL_24:
        puts("------ don't need check user -------", v13);
        return 0;
      }
      if ( dword_4697F8 && !memcmp(v56, "/login.html", 10) )
      {
        dword_4697F8 = 0;
        return 0;
      }
      if ( i == 4 && !strncmp(a5, "/loginerr.html", 14) )
        return 0;
      if ( (unsigned int)strlen((int)v56) >= 4 )
      {
        v19 = strchr(v56, 46);
        if ( v19 )
        {
          v20 = v19 + 1;
          if ( !memcmp(v19 + 1, "gif", 3)
            || !memcmp(v20, "png", 3)
            || !memcmp(v20, "js", 2)
            || !memcmp(v20, "css", 3)
            || !memcmp(v20, "jpg", 3)
            || !memcmp(v20, "jpeg", 3) )
          {
            memset(v58, 0, 128);
            snprintf(v58, 128, "/www%s", v56);
            if ( !access(v58, 0) )
              return 0;
          }
        }
      }

发现没有处理'/'的条件后，会交给websHomePageHandler来处理，其会根据程序初始化中定义好的websDefaultPage，也就是main.html，然后重定向到main.html。
![](https://images.seebug.org/content/images/2022/11/117175e9-d7fd-4011-b1ca-0344a998e3fd.png-w331s)

紧接着，又会经过R7WebsSecurityHandler()，然后经过遍历，最后会到到达这个位置LABEL_149，又将会重定向到login.html，login.html是不需要身份验证的，继续调试下去就会出现登录界面。
![](https://images.seebug.org/content/images/2022/11/1dfa9f23-30f2-400e-9590-d2164d95fe20.png-w331s)

接下来我们将断点打在，190行的/login/Auth，这就对应了前端的那个接口，我们随便输入密码进行测试。

断点断下来后，分析过程，先获取username和password，然后和保存在全局变量中的用户名和密码进行比较。
![](https://images.seebug.org/content/images/2022/11/4f3b3d6f-3f9f-4c14-a8a4-ae6447552bec.png-w331s)

这里先看密码不正确的处理流程，这里会到达LABEL_86，调用websWrite向WebRec结构体写了些东西，然后调用了webDone()函数，结束这次请求，websWrite((int)wp,
"%s", "1");，我猜测这应该是传给前面login.js的str，使得num=1，从而显示密码错误。
![](https://images.seebug.org/content/images/2022/11/24b50643-cb6a-4b95-8aae-fd290b692045.png-w331s)

接着再来看正确密码的处理流程，经过一些if判断后，对loginUserInfo进行赋值，也就是访问者的ip地址，最后会跳转到LABEL_118。
![](https://images.seebug.org/content/images/2022/11/748918f0-3194-47be-b443-191cec3c794e.png-w331s)

LABEL_118，这个地方就是在生成cookie，然后发送到前端了，并且其cookie的组成是有一种固定的方式的。
![](https://images.seebug.org/content/images/2022/11/48da54d2-2d94-4b30-9a37-2750128a0c80.png-w331s)

为了搞明白cookie的生成过程，进入websRedirectOpCookie分析。
![](https://images.seebug.org/content/images/2022/11/0228c1b3-5941-4795-8ee5-284c31365a29.png-w331s)

所以实际上cookie就是3部分组成password+3个a到z的随机数+3个字符(由访问者的ip地址决定是哪三个)。

接下来就是再次访问main.html，但和之前不同的是，这次loginUserInfo有值了，其会导致i!=4，执行这样的流程，其实就是在验证cookie是否有效。
![](https://images.seebug.org/content/images/2022/11/d2b1eaa6-77b3-4e85-b2df-ef2335ff1d45.png-w331s)

验证cookie是否有效，然后跳转到对应的界面，访问其他接口也一样，都需要验证cookie的有效性。

![](https://images.seebug.org/content/images/2022/11/e78fb679-5595-4e82-9948-54d9c48b5b59.png-w331s)

登录和cookie验证的分析就差不多了，其实还有很多地方可以继续分析，比如说我这个浏览器登录了，换个浏览器会怎么样，或者换个ip访问会怎么样，根据其cookie的生成过程来说，同一个ip访问时，最多只有一个有效cookie，换一个浏览器登录，就会造成之前浏览器的cookie失效，从而需要重新登录。

### CSRF恢复出厂设置

大部分Tenda的设备的CSRF漏洞都是一些接口直接提供system命令，这里我也找到一个Tenda
Ax12下还未提交过的，也就是/goform/SysToolRestoreSet。
![](https://images.seebug.org/content/images/2022/11/461abed2-9b75-4488-8089-53ad1ebe5028.png-w331s)

攻击也很简单，在经过身份验证后 Get访问这个接口，即可让整个路由器恢复出厂设置。

### CSRF删除修改密码，修改WiFi名称

这个漏洞发生在/goform/fast_setting_wifi_set接口下，这个接口实际上是设备恢复出厂设置后，重新设置WiFi名称，和密码的接口。
我们可以控制传入的web参数，来达到修改WiFi名称，修改密码的效果，并且在这个函数中，由于是重新设置的函数，所以并不会和先前的密码进行对比。

正常情况下，我们在恢复出厂设置后，其会让我们输入WiFi名称，无线密码，以及5-32位的管理员密码，抓包如下。
![](https://images.seebug.org/content/images/2022/11/1ef0c400-4baa-4855-bb76-681ee67baca2.png-w331s)

可以看到一些参数，如果选择无须密码，对应参数的值就是空。

  * ssid代表WiFi名称
  * WrlPassword代表连WiFi的密码
  * loginPwd代表管理员密码，被md5加密了。

然后在来分析这个接口对应的处理函数sub_4335C0。

先是获取ssid，判断是否为空，然后如果WiFi密码不为空，默认以psk-mixed方式加密，然后将WiFi名，加密方式，密码给到v17，然后调用tapi_set_wificfg，猜测应该是在设置WiFi密码吧，然后以同样的方式设置5g。
![](https://images.seebug.org/content/images/2022/11/6b8a070a-26ba-431d-a70c-ff2df13c2d9d.png-w331s)

然后就是设置管理员密码了，先获取前端传入的参数loginPwd，然后设置到/etc/config/admin文件中，下面是一些无关紧要的if判断，感觉没什么作用，而且管理员密码已经写入到了admin文件中。
![](https://images.seebug.org/content/images/2022/11/984ce679-3632-4c7d-8879-491aaff832ff.png-w331s)

后序就是timeZone的设置，一些webWrite，以及一些重新启动的过程。

所以如果在有一次有效cookie的前提下，我们完全可以构造参数，来达到修改WiFi名称密码，以及管理员密码的目的。

    
    
    POST /goform/fast_setting_wifi_set HTTP/1.1
    Host: 192.168.0.1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0
    Accept: */*
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    X-Requested-With: XMLHttpRequest
    Content-Length: 10
    Origin: http://192.168.0.1
    Connection: close
    Cookie: password=xxxxxxxxxx
    Referer: http://192.168.0.1/main.html
    
    ssid=xxx&WrlPassword=xxx&power=high&loginPwd=(md5(xxx))

### 未成功的XSS

Tenda
Ax12设备的WiFi名称和接入的设备名称都是可以设置的，这可能会导致xss，我对WiFi名称和设备名称都进行了测试，遗憾的是未能触发攻击，但是我感到很疑惑，因为名字都显示出来了，卡了好久最后才找到原因。

这里以设备名称为例，首先我们需要绕过前端长度验证，抓包修修改即可。
![](https://images.seebug.org/content/images/2022/11/e836ada4-a714-4584-a839-d072cf7701c8.png-w331s)

然后查看显示也是正常，html也正常，就有点奇怪为什么没弹窗。
![](https://images.seebug.org/content/images/2022/11/eca22d85-a083-4d21-96d9-63edaa532c0e.png-w331s)

卡了一会，最后将整个html下载下来才发现，其对<>字符进行了转义。

    
    
    <div class="dev-name text-fixed" style="padding-right: 30px;"
        title="&lt;script&gt;alert(&quot;The_Itach1&quot;)&lt;/script&gt;">
        <span
            class="dev-name-text">&lt;script&gt;alert("The_Itach1")&lt;/script&gt;</span>
    </div>

接着我尝试#" onclick="alert(/xss/)，发现“也被转义。

    
    
    <div class="dev-name text-fixed" style="padding-right: 30px;"
        title="#&quot; onclick=&quot;alert(/xss/)"><span
            class="dev-name-text">#"&nbsp;onclick="alert(/xss/)</span></div>
    <div class="">---</div>

遗憾的是这种xss没法利用，不然和已有的csrf配合，加上一点社会工程，或者修改自己设备名称，就可以到达比较不错的攻击效果。

### DOS，堆栈溢出

同样也是在/goform/fast_setting_wifi_set的ssid参数，其经过的sprintf函数，未对长度进行限制，这将导致堆栈溢出，而达到Dos拒绝服务的攻击效果。

![](https://images.seebug.org/content/images/2022/11/2d3b60e5-fbc4-4107-92a7-88cbe196edd5.png-w331s)

### 老固件版本的一个命令注入

在参考老固件版本时，我看到了一个函数疑似存在命令注入，但是由于我的Tenda
Ax12设备固件已经升级，貌似无法回退，于是就打算qemu模拟下，但毕竟是模拟环境，和实体设备不太一样，而且和网上其他的Tenda设备的模拟方式也不同。

在网上下载好[老固件版本](\[https://www.tenda.com.cn/download/detail-3170.html\]\(https://www.tenda.com.cn/download/detail-3170.html
"https://www.tenda.com.cn/download/detail-3170.html"\))后，readelf确定好是mips大端序架构后，直接先尝试直接qemu启动。
![](https://images.seebug.org/content/images/2022/11/f840b8cd-34a8-4730-94b3-684b46f9642f.png-w331s)

可以正常启动，但是实际上其监听的ip实际上有点问题，虽然对这个命令注入漏洞测试验证没什么影响，但是这个ip实际上我们是可以控制的。

通过之前启动部分的分析，我们可以在binwalk解析出来的文件系统中，在/etc/config目录下新建一个network文件，添加以下内容。

    
    
    config interface 'loopback'
            option ifname 'lo'
            option proto 'static'
            option ipaddr '127.0.0.1'
            option netmask '255.0.0.0'
    
    config globals 'globals'
    
    config interface 'lan'
            option type 'bridge'
            option proto 'static'
            option ipaddr '192.168.112.131'
            option netmask '255.255.255.0'

只要我们想修改listen的ip，就去修改ipaddr的值就行了，重新qemu启动效果如下。
![](https://images.seebug.org/content/images/2022/11/fab07512-e49d-4980-97be-5157e7d5a4fa.png-w331s)

可以看到监听ip就变成了我们设置的ip了，环境就差不多模拟好了，虽然和真实设备有差别，但是能正常接收http请求。

我是在fast_setting_internet_set接口的处理函数sub_431AD8中的一个子函数sub_42581发现了这个命令注入漏洞。
![](https://images.seebug.org/content/images/2022/11/9bb54005-565f-495f-9283-e41ce772fad9.png-w331s)

其先是从websRec结构体a1，调用websGetVar函数获取到了staticIp的值，然后用sprintf将其给到v5，然后调用doSystemCmd_route执行命令，我们可以通过控制传入staticIp的值来达到命令注入的效果。

开始编写exp，攻击效果如下，我的exp是将装有密码的admin配置文件给copy到了tmp目录下 并命名为hack。
![](https://images.seebug.org/content/images/2022/11/df8ec6b7-7f0b-49bf-bfaf-590f70850d03.png-w331s)

### 新固件的一个命令注入

这个漏洞发生在/goform/setMacFilterCfg接口，其对应的处理函数为sub_424334，本来这是一个存在栈溢出的函数，但是我偶然发现，其可能会存在命令注入。

在这个函数的最下面，有这样的代码。
![](https://images.seebug.org/content/images/2022/11/f82e709e-a040-4038-898a-cff9a76b6826.png-w331s)

可以看到，其很危险的调用了doSystemCmd函数，只为了输出一段话到/tmp/macfilter文件，仔细观察后，v2是传入的macFilterType参数，根据printf的那句话，&v14[2]是不是就是指向上一次macFilterType的值呢，如果能控制这个参数，就有可能造成命令注入。

这个接口对应了后台管理界面->高级功能->MAC地址过滤，macFilterType参数就是对应了白名单和黑名单，也就是write和black。先进行一次访问，但是我将macFilterType的值修改为test。
![](https://images.seebug.org/content/images/2022/11/4a6bf3ce-62be-4aca-8442-3377fc3886e7.png-w331s)

紧接着，继续再正常随便访问一次，发现&v14[2]的值就是test。
![](https://images.seebug.org/content/images/2022/11/059eab4b-2bca-4d37-9bd7-b53ec7c8de33.png-w331s)

这意味着，确实存在命令注入。

根据这个我尝试编写脚本进行攻击，主要是重启命令，恢复出厂设置命令，和/bin/sh命令，攻击效果如下。
![](https://images.seebug.org/content/images/2022/11/27dea60a-d341-46b5-9509-22775d883c91.png-w331s)

![](https://images.seebug.org/content/images/2022/11/feadff1d-51b5-43d3-8a36-a53846e46958.png-w331s)

重启命令和恢复出厂设置，都起了效果，但是/bin/sh却未成功，但是经过调试发现，确实进入dosystemcmd函数前的参数是/bin/sh，但不知道为什么没成功getshell。
![](https://images.seebug.org/content/images/2022/11/8cb887c2-400a-4aa9-b2fa-c08a70656096.png-w331s)

无论怎样，这个地方确实存在着命令注入，虽然需要一次身份验证，但是危害性还是较强。

## 参考

《揭秘家用路由器0day漏洞挖掘技术》

[Yaseng](https://yaseng.org/)

[H4lo-github](https://github.com/H4lo/IOT_Articles_Collection/blob/master/Collection.md)

[物联网终端安全入门与实践之玩转物联网固件上](https://www.freebuf.com/articles/endpoint/335030.html)

[物联网终端安全入门与实践之玩转物联网固件下](https://www.freebuf.com/articles/endpoint/344858.html)

[Tenda AC15 AC1900 Vulnerabilities Discovered and Exploited | by Sanjana Sarda
| Independent Security Evaluators](https://blog.securityevaluators.com/tenda-ac1900-vulnerabilities-discovered-and-exploited-e8e26aa0bc68)

[路由器web服务架构](https://tttang.com/archive/1777/)

[Tenda Ax12系列分析](https://www.anquanke.com/post/id/255290)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2024/>

