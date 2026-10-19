# Tenda AX12 路由器设备分析（三）之OpenWrt 浅析

阅读量 **186028**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-04 14:30:25

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 0x01 前言

任何系统的启动原理和流程都是相关安全人员需要了解的，因为只有了解了系统的启动流程和启动机制，才会更高的来研究整体的安全性，本文章打算来介绍一下Tenda
AX 12 路由器的在启动流程，设备的系统是开源的 OpenWrt 二次开发出来的，系统中提供http服务的组件并不是OpenWrt
的uhttpd，而是goahead 开源框架二次开发而来的httpd，因此我还打算从httpd 的角度来介绍设备openwrt
是符合启动和调用httpd组件的。

本文是个人在对Tenda AX12设备分析和研究，班门弄斧，可能讲的不够全面，如有不对，望及时指正，多多包涵。

## 0x02 启动流程

iot 设备的固件的典型结构由 引导加载程序bootloader、参数、内核Kernel、文件系统squashfs，应用程序组成。

![](https://p1.ssl.qhimg.com/t014b9060faa61943a9.png)

设备在上电之后，处理器首先会加载固化在flash/ROM中的代码到RAM中执行，而这段代码就是Bootloader（U-boot），在Tenda AX12
上电的时候，设备UART串口输出的log信息中，我们可以看到U-boot 的版本和发布日期，接着U-boot 设置和初始化RAM，
进行基本的硬件初始化；初始化串口端口，这样启动的log信息可以通过串口输出；对CPU处理器进行检测；设置和初始化内核Kernel 启动参数

做完这些之后，U-boot 会加载内核Kernel 从flash 到RAM中，U-boot 将退出舞台，后面就交给Kernel 。

U-Boot从启动设备上面读取、分析环境变量获得kernel和rootfs存储位置，以及所需的kernel command line；  
自动检测系统RAM和eMMC/Nand Flash容量和参数；  
设置以太网口MAC地址，并配置好硬件准备加载Linux kernel；  
加载Linux kernel到RAM，至此系统控制权则转移到kernel来处理；  
设备的UART log信息刚启动的部分信息如下所示：

    
    
    U-Boot 2016.07-INTEL-v-3.1.177 (Nov 25 2020 - 09:48:15 +0000)
    
    interAptiv
    cps cpu/ddr run in 800/666 Mhz
    DRAM:  224 MiB
    manuf ef, jedec 4018, ext_jedec 0000
    SF: Detected W25Q128BV with page size 256 Bytes, erase size 64 KiB, total 16 MiB
    *** Warning - Tenda Environment, using default environment
    
    env size:8187, crc:d89b57c5 need d89b57c5
    In:    serial
    Out:   serial
    Err:   serial
    Net:   multi type
    Internal phy firmware version: 0x8548
    GRX500-Switch
    
    Type run flash_nfs to mount root filesystem over NFS
    
    Hit ESC to stop autoboot:  0 
    Wait for upgrade... use GRX500-Switch
    tenda upgrade timeout.
    manuf ef, jedec 4018, ext_jedec 0000
    SF: Detected W25Q128BV with page size 256 Bytes, erase size 64 KiB, total 16 MiB
    device 0 offset 0x100000, size 0x200000
    SF: 2097152 bytes @ 0x100000 Read: OK
    ## Booting kernel from Legacy Image at 80800000 ...
       Image Name:   MIPS UGW Linux-4.9.206
       Created:      2020-11-18   5:39:29 UTC
       Image Type:   MIPS Linux Kernel Image (lzma compressed)
       Data Size:    2079952 Bytes = 2 MiB
       Load Address: a0020000
       Entry Point:  a0020000
       Verifying Checksum ... OK
       Uncompressing Kernel Image ... OK
    [    0.000000] Linux version 4.9.206 (root@ubt1-virtual-machine) (gcc version 8.3.0 (OpenWrt GCC 8.3.0 v19.07.1_intel) ) #0 SMP Fri Nov 13 09:14:24 UTC 2020
    [    0.000000] SoC: GRX500 rev 1.2
    [    0.000000] CPU0 revision is: 0001a120 (MIPS interAptiv (multi))
    [    0.000000] Enhanced Virtual Addressing (EVA 1GB) activated
    [    0.000000] MIPS: machine is EASY350 ANYWAN (GRX350) Main model
    [    0.000000] Coherence Manager IOCU detected
    [    0.000000] Hardware DMA cache coherency disabled
    [    0.000000] earlycon: lantiq0 at MMIO 0x16600000 (options '')
    [    0.000000] bootconsole [lantiq0] enabled
    [    0.000000] User-defined physical RAM map:
    [    0.000000]  memory: 08000000 @ 20000000 (usable)
    [    0.000000] Determined physical RAM map:
    [    0.000000]  memory: 08000000 @ 20000000 (usable)
    [    0.000000]  memory: 00007fa4 @ 206d5450 (reserved)
    [    0.000000] Initrd not found or empty - disabling initrd
    [    0.000000] cma: Reserved 32 MiB at 0x25c00000
    [    0.000000] SMPCMP: CPU0: cmp_smp_setup
    [    0.000000] VPE topology {2,2} total 4
    [    0.000000] Detected 3 available secondary CPU(s)
    [    0.000000] Primary instruction cache 32kB, VIPT, 4-way, linesize 32 bytes.
    [    0.000000] Primary data cache 32kB, 4-way, PIPT, no aliases, linesize 32 bytes
    [    0.000000] MIPS secondary cache 256kB, 8-way, linesize 32 bytes.
    [    0.000000] Zone ranges:
    [    0.000000]   DMA      [mem 0x0000000020000000-0x0000000027ffffff]
    [    0.000000]   Normal   empty
    [    0.000000] Movable zone start for each node
    [    0.000000] Early memory node ranges
    [    0.000000]   node   0: [mem 0x0000000020000000-0x0000000027ffffff]
    [    0.000000] Initmem setup node 0 [mem 0x0000000020000000-0x0000000027ffffff]
    [    0.000000] percpu: Embedded 12 pages/cpu s17488 r8192 d23472 u49152
    [    0.000000] Built 1 zonelists in Zone order, mobility grouping on.  Total pages: 32480
    [    0.000000] Kernel command line: earlycon=lantiq,0x16600000 nr_cpus=4 nocoherentio clk_ignore_unused root=/dev/mtdblock6 rw rootfstype=squashfs do_overlay console=ttyLTQ0,115200 ethaddr=CC:2D:21:EE:D9:F0 panic=1 mtdparts=spi32766.1:512k(uboot),128k(ubootconfigA),128k(ubootconfigB),256k(calibration),2m(kernel),12m(rootfs),-(res) init=/etc/preinit active_bank= update_chk= maxcpus=4 pci=pcie_bus_perf ethwan= ubootver= mem=128M@512M 
    [    0.000000] PID hash table entries: 512 (order: -1, 2048 bytes)
    [    0.000000] Dentry cache hash table entries: 16384 (order: 4, 65536 bytes)
    [    0.000000] Inode-cache hash table entries: 8192 (order: 3, 32768 bytes)
    [    0.000000] Writing ErrCtl register=00000000
    [    0.000000] Readback ErrCtl register=00000000
    [    0.000000] Memory: 87656K/131072K available (5087K kernel code, 294K rwdata, 1264K rodata, 1276K init, 961K bss, 10648K reserved, 32768K cma-reserved)
    [    0.000000] SLUB: HWalign=32, Order=0-3, MinObjects=0, CPUs=4, Nodes=1
    [    0.000000] Hierarchical RCU implementation.
    [    0.000000] NR_IRQS:527
    [    0.000000] EIC is off
    [    0.000000] VINT is on
    [    0.000000] CPU Clock: 800000000Hz  mips_hpt_frequency 400000000Hz
    [    0.000000] clocksource: gptc: mask: 0xffffffff max_cycles: 0xffffffff, max_idle_ns: 9556302233 ns
    [    0.000010] sched_clock: 32 bits at 200MHz, resolution 5ns, wraps every 10737418237ns
    [    0.008266] Calibrating delay loop... 531.66 BogoMIPS (lpj=2658304)
    [    0.069297] pid_max: default: 32768 minimum: 301
    [    0.074090] Mount-cache hash table entries: 1024 (order: 0, 4096 bytes)
    [    0.080515] Mountpoint-cache hash table entries: 1024 (order: 0, 4096 bytes)
    [    0.089026] CCA is coherent, multi-core is fine
    [    0.098050] [vmb_cpu_alloc]:[645] CPU vpet.cpu_status = 11
    ...
    

我们可能比较关心的是加载内核镜像和文件系统映像以及设置 Kernel command line 内核启动参数。

    
    
    Kernel command line: earlycon=lantiq,0x16600000 nr_cpus=4 nocoherentio clk_ignore_unused root=/dev/mtdblock6 rw rootfstype=squashfs do_overlay console=ttyLTQ0,115200 ethaddr=CC:2D:21:EE:D9:F0 panic=1 mtdparts=spi32766.1:512k(uboot),128k(ubootconfigA),128k(ubootconfigB),256k(calibration),2m(kernel),12m(rootfs),-(res) init=/etc/preinit active_bank= update_chk= maxcpus=4 pci=pcie_bus_perf ethwan= ubootver= mem=128M@512M
    

启动mtdparts 的作用是配置MTD层的分区，然后u-boot 将分区信息传递给命令行中的mtdparts 参数。

    
    
    [    2.641030] Creating 7 MTD partitions on "spi32766.1":
    [    2.646216] 0x000000000000-0x000000080000 : "uboot"
    [    2.652273] 0x000000080000-0x0000000a0000 : "ubootconfigA"
    [    2.657866] 0x0000000a0000-0x0000000c0000 : "ubootconfigB"
    [    2.663350] 0x0000000c0000-0x000000100000 : "calibration"
    [    2.668827] 0x000000100000-0x000000300000 : "kernel"
    [    2.673587] 0x000000300000-0x000000f00000 : "rootfs"
    [    2.678642] mtd: device 6 (rootfs) set to be root filesystem
    [    2.683251] 1 squashfs-split partitions found on MTD device rootfs
    [    2.689144] 0x000000d00000-0x000001000000 : "rootfs_data"
    [    2.695934] 0x000000f00000-0x000001000000 : "res"
    

console 的参数是配置串口信息，这里ttyLTQ0 为虚拟出来的串口设备，115200是这个串口的Baudrat波特率

root 的参数配置是设置跟文件系统，/dev/mtdblock6 为rootfs, rw 的意思是在启动是以读写的方式挂载/dev/mtdblock6。

init 的参数是设置系统的默认启动项，这里设置成为/etc/preint

这一部分在openwrt 的源码kernel 函数中有体现，当内核启动参数init
已经设置了，那么就使用设置的参数作为init程序，如果没有，就按照以下顺序依次尝试启动，看到这段代码，设备所有设置的init
程序都无法正常启动，那么最终会启动/bin/sh，从下面的代码我们可以理解，设备使用/etc/preint 作为初始化init程序的时候，UART
串口接入shell，需要登录凭证，如果我们进入u-boot 更改kernel 内核启动参数init 为 /bin/sh ，是否就可以绕过登录了。

    
    
    --- a/init/main.c
    +++ b/int/main.c
    @@ -844,7 +844,8 @@ static int _ref kernel_init(void *unuse 
                                    pr_err("Failed to execute %s. Attempting default...\n"),
                                    execute_command);
                    }
    -                 if(!run_init_process("/sbin/init")||
    +                 if(!run_init_process("/etc/preinit")||
                        !run_init_process("/sbin/init")||
                        !run_init_process("/etc/init")||
                        !run_init_process("/bin/preinit")||
                        !run_init_process("/bin/sh")
    

通过UART Log 信息 ，在初始化/preinit 脚本之后，接着会执行procd 模块，当然设备UART 输出的启动log
远不止我上面讲述的这些，这就需要安全人员的仔细分析。

    
    
    [    6.188804] kmodloader: done loading kernel modules from /etc/modules-boot.d/*
    [    6.200760] init: - preinit -    ubimkvol: error!: UBI is not present in the system
    ls: /lib/modules/4.9.206/ltq_atm*: No such file or directory
    [    7.505491] mount_root: switching to jffs2 overlay
    [    7.554060] urandom-seed: Seeding with /etc/urandom.seed
    nanddump: error!: Unable to write to output
              error 32 (Broken pipe)
    chown: unknown user/group nwk:nwk
    [    8.856209] procd: - early -    [    8.857722] procd: - watchdog -    [    9.594215] procd: - watchdog -    [    9.596328] procd: - ubus -    [    9.656987] procd: - init -    Please press Enter to activate this console.
    

## 0x03 procd 模块的作用

在OpenWrt
嵌入式系统中，有一些通用的基础内核模块，如：基础库libubox、系统总线ubus、网络接口总线ubus、网络接口管理模块netifd、核心工具模块ubox、服务管理模块procd。

在Tenda AX12 设备中的进程信息如下：

    
    
      1 root        1656 S    /sbin/procd
      752 root      1252 S    /sbin/ubusd
     2009 root      1840 S    /sbin/netifd
    

由于嵌入式设备存在漏洞风险点多与服务有关，因此这里我们来了解一下procd 服务。

在了解procd
服务之前，我们先讲述续一下守护进程，通常嵌入式系统中有一个守护进程，该守护进程监控系统进程的状态，如果某些系统进程异常退出，将再次启动这些进程。Procd就是这样的进程。我这里讲述以下我为什么会关注procd
模块。

我在Tenda AX12 设备上的httpd
组件服务上发现了一个缓冲区栈溢出的漏洞，当我兴致勃勃的构造好简单的poc，并且打算触发漏洞造成设备httpd服务拒绝服务效果的时候，我的每次漏洞触发都是无效的，因为我看到设备的httpd服务从外界依旧可以访问和请求，为此，我甚至一度怀疑漏洞的有效性了，于是我从设备的另一个漏洞获取shell
之后，看到设备的httpd 进程Pid
每次在我发送缓冲区栈溢出POC之后，都会更改，于是我猜测设备上有一个守护进程，会在httpd进程异常退出之后将起再次启动。

为此我做了一个简单的测试，我在Tenda AX12 设备中kill 掉httpd 服务的进程，随后httpd服务又重新启动。

这里我们来查看一下设备正在运行的程序。

    
    
    root@AX12:~# ps
      PID USER       VSZ STAT COMMAND
        1 root      1656 S    /sbin/procd
      752 root      1252 S    /sbin/ubusd
      753 root       940 S    /sbin/askfirst /bin/login.sh
     1715 root      1596 S    /opt/intel/bin/dump_handler -i 0 -f /opt/intel/wave/
     1755 root      2544 S    /usr/sbin/dwpal_cli -iDriver -vwlan0 -lFW_DUMP_READY
     1760 root      1288 S    /sbin/logd -S 64
     1969 root      1952 S    sys_cli eth -F /tmp/ppa_cfg.conf
     2009 root      1840 S    /sbin/netifd
     2063 root      3296 S    /usr/bin/td_netlink_recv_online
     2094 root      3780 S    /usr/bin/td_ol_srv
     2139 root      3300 S    /bin/td_flow_statistic_ctl -w
     2201 root      1092 S    /bin/td_wan_speed
     2293 root      1396 S    /usr/sbin/crond -f -c /etc/crontabs -l 5
     2728 root      3616 S    /bin/td_serverd
     2971 root      1392 S<   /usr/sbin/ntpd -n -N -S /usr/sbin/ntpd-hotplug -p 0.
     3196 dnsmasq   1452 S    /usr/sbin/dnsmasq -C /var/etc/dnsmasq.conf.cfg01411c
     3227 root      3904 S    /usr/sbin/httpd
     3438 root      1396 S    /bin/sh /sbin/limitTemperature.sh
     3593 root      3328 S    /usr/bin/td_filter_ctrl
     3765 root      4856 S    /usr/sbin/hostapd -s -P /var/run/wifi-phy1.pid -B /v
     4888 root      3796 S    /bin/ucloud -l 4
     6967 root      1400 R    /usr/sbin/telnetd -F -l /bin/login.sh
     。。。
    

我企图kill 掉td_serverd 和httpd，来测试td_serverd 是否是httpd的守护进程，没想到td_serverd 和httpd
依旧会自启动。于是我查看td_serverd 文件的调用流程和模式，看到了如下的stop 命令，尝试执行后，td_serverd 进程成功的停止了。

![](https://p1.ssl.qhimg.com/t01469d1b0be7aaa92e.png)

在openwrt 系统中，ubus 模块可以将需要procd 模块管理的进程以实例的方式进行注册，注册的方式用ubus
命令来将带有进程名，进程实例信息，进程启动脚本等信息作为参数的形式传递给procd，而后procd 将这个进程信息加入到管理的内存数据中。在openwrt中
procd.sh 将ubus 传递参数的功能封装成为函数，每个需要被procd管理的进程都将使用procd.sh 提供的函数进程注册。

在httpd 服务注册进procd 进程调用procd.sh 封装的函数，调用的脚本（/etc/init.d/httpd）如下
，脚本中用到的procd.sh 封装的函数有
procd_open_instance、procd_open_instance、procd_set_param、procd_close_instance

    
    
    #!/bin/sh /etc/rc.common
    # 使用/etc/rc.common来解释脚本
    # Copyright (C) 2010-2012 OpenWrt.org
    
    USE_PROCD=1   # 使用procd 来管理进程
    START=99      # 数值越小，启动顺序排在越前面
    SERVICE_DAEMONIZE=1
    
    start_service() {
        stop_service # 让procd 解除注册，并关闭服务，将servers中管理对象删除。
        procd_open_instance httpd # 开始增加一个服务实例
        procd_set_param limits core="unlimited"
        procd_set_param respawn # 设置服务进程意外退出重启机制及策略。
        procd_set_param command /usr/sbin/httpd # 设置服务进程意外退出重启机制及策略。
        procd_close_instance # 设置服务进程意外退出重启机制及策略。
    }
    

其中简单要介绍的是procd_set_param 函数，如果设置respawn ，那么这个进程异常退出之后，procd就会将进程重启。

> procd_set_param：设置服务实例的参数值。通常会有以下几种类型的参数：（每次只能使用一种类型参数，其后是这个类型参数的值）。  
>  command：服务的启动命令行。  
>  respawn：进程意外退出的重启机制及策略，它需要有 3 个设置值。第一个设置为 判断异常失败边界值（threshold），默认为 3600
> 秒，如果小于这个时间退出，则 会累加重新启动次数，如果大于这个临界值，则将重启次数置 0。第二个设置为
> 重启延迟时间（timeout），将在多少秒后启动进程，默认为 5 秒。第三个设置是总
> 的失败重启次数（retry），是进程永久退出之前的重新启动次数，超过这个次数进 程退出之后将不会再启动。默认为 5
> 次。也可以不带任何设置，那这些设置都是 默认值。  
>  env：进程的环境变量。  
>  file：配置文件名，比较其文件内容是否改变。  
>  netdev：绑定的网络设备（探测 ifindex 更改）。  
>  limits：进程资源限制。

procd.sh 中封装的函数远不止这些，还有以下几个

  * procd_open_trigger
  * procd_close_trigger
  * procd_add_reload_trigger
  * procd_open_validate
  * procd_close_validate
  * procd_kill
  * procd_close_service
  * procd_open_service(name, [script])
  * uci_validate_section

在前面我们调用stop命令可以停止进程的运行，但是使用kill 命令无法停止进程，是因为procd 的作用。

可是上面的 /etc/init.d/httpd 脚本内容并没有 stop 函数内容，那是因为脚本调用了 /etc/rc.common
文件内的函数，而在rc.common 中的stop函数内容中调用了procd.sh 中的procd_kill 函数。

![](https://p2.ssl.qhimg.com/t01a00f3ec79e276604.png)

procd_kill 函数的内容如下，会调用ubus delete 删除指定的进程，从而结束对进程的调用。

> procd_kill 函数
>
> 杀掉服务实例（或所有的服务实例）。至少需要一个参数，第一个参 数是服务名称，通常为进程名，第二个是可选参数，是进程实例名称，因为可能有多个进
> 程示例，如果不指定所有的实例将被关闭。该函数在 rc.common 中调用，用户从命令行调 用 stop 函数时会使用该函数杀掉进程。

![](https://p1.ssl.qhimg.com/t012e103dfa8e4dc27b.png)

在/etc/init.d/httpd 脚本中自定义了start_service()
函数，这个函数在rc.common中也有，那么对于httpd而言，重写了这个函数，在/etc/init.d/httpd 中还定义了USE_PROCD
变量，这个变量的作用除了使用procd来管理httpd进程，还能调用procd预定义的函数，procd预定义的函数有以下几个函数：

  * start_service 向 procd 注册并启动服务，是将在 services 所管理对象里面增加了一项
  * stop_service 让 procd 解除注册，并关闭服务, 是将在 services 中的管理对象删除
  * service_triggers 配置文件或网络接口改变之后触发服务重新读取配置
  * service_running 查询服务的状态
  * reload_service 重启服务，如果定义了该函数，在 reload 时将调用该函数，否则再次调用 start 函数
  * service_started 用于判断进程是否启动成功

另外，我使用kill 命令尝试结束procd 进程的时候，procd 进程的pid号是1。这是因为在内核参数启动调用的初始化进程preint后，procd
会继承preint 的进程号pid 1。并且在kill 1 的时候，Tenda AX12 设备会进行重启。

procd 启动的顺序为：

![](https://p0.ssl.qhimg.com/t01a76baa1179e3437a.png)

## 0x04 httpd 启动

对于httpd 进程的启动，结合OpenWrt 系统的启动流程，和对procd 模块的了解。设备在上电的之后，uboot 会自己启动，在uboot
启动之后，调用Kernel ，Kernel 会调用/etc/preinit 脚本，并且设备在自启动的时候，根据linux
的特性，会启动/etc/init.d目录下的脚本。httpd 脚本会自启动，调用procd.h 中定义的预函数，使用ubus模块向procd
模块注册httpd进程的实例信息。httpd 启动的流程如下图所示：

![](https://p5.ssl.qhimg.com/t011e64c1dac86def3d.png)

## 0x05 总结

本文通过Tenda AX12 Wi-Fi6 路由器 UART log 信息和OpenWrt 的特性对设备的启动流程进程梳理和分析，另外，还介绍了procd
守护进程的作用和procd 守护进程对系统做是如何进行对设备内的进程进行管理。当掌握这些之后，对设备的研究会更加熟练。

## 0x06 参考

<https://oldwiki.archive.openwrt.org/inbox/procd-init-scripts>  
<https://www.kernel.org/doc/html/v4.14/admin-guide/kernel-parameters.html>  
<https://blog.csdn.net/sunheshan/article/details/39207829>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **大中午啊** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/264194](/post/id/264194)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [路由器](/tag/路由器)
  * [OpenWRT](/tag/OpenWRT)
  * [嵌入式](/tag/嵌入式)

 **+1** __18赞

 __收藏

![](https://p0.ssl.qhimg.com/t01ac7436631a1f31ef.png) 大中午啊

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

