**Shadow-box是** **一款基于虚拟化技术实现的轻量级Linux系统监控框架。**  

## 关于 Gatekeeper

Gatekeeper基于Shadow-box。

如果你想了解更多有关Gatekeeper的信息，请转到[Gatekeeper项目分支](https://github.com/kkamagui/shadow-box-for-x86/tree/gatekeeper)。

## 注意

Shadow-box v2（适用于ARM）是下一代的Shadow-box v1（适用于x86）。如果你想了解ARM的Shadow-box，请访问[Shadow-box for ARM项目](https://github.com/kkamagui/shadow-box-for-arm)。

主要变化如下：

> 支持页表隔离（PTI）
>
> 支持英特尔集成显卡睡眠模式

演讲及论文

Shadow-box是一个实用的轻量级内核保护程序，它在以下安全会议上已被多次介绍。

> Gatekeeper：[beVX
> 2018](https://www.beyondsecurity.com/bevxcon/speakers.html#SeunghunHan)
>
> [Black Hat Asia
> 2018](https://www.blackhat.com/asia-18/briefings.html#shadow-box-v2-the-> practical-and-omnipotent-sandbox-for-arm)
>
> [Black Hat Asia 2017](https://www.blackhat.com/asia-17/briefings.html#myth-> and-truth-about-hypervisor-based-kernel-protector-the-reason-why-you-need-> shadow-box)和[Black Hat Asia Arsenal
> 2017](https://www.blackhat.com/asia-17/arsenal.html#shadow-box-lightweight-> hypervisor-based-kernel-protector)
>
> [HITBSecConf
> 2017](http://conference.hitb.org/hitbsecconf2017ams/sessions/shadowbox-the-> practical-and-omnipotent-sandbox/)

你可以观看下面的演示视频。

> [Gatekeeper
> Demo：](https://youtu.be/gjpxeKlzA9s)该演示向我们展示了Gatekeeper可以检测并阻止本地提权漏洞的利用。
>
> [Shadow-box Demo
> 1：](https://youtu.be/3_cFDVHWCXA)该演示向我们展示了rootkit可以neutralize内核保护机制。
>
> [Shadow-box Demo 2：](https://youtu.be/s7iZYg4vP4E)该演示向我们展示了Shadow-> box可以阻止来自rootkit的内核。

##
![1.jpg](https://image.3001.net/images/20190720/1563603842_5d32b382c9b19.jpg!small)![2.jpg](https://image.3001.net/images/20190720/1563603842_5d32b382cacf2.jpg!small)

## Shadow-Box 介绍

Shadow-box使用最先进的虚拟化技术的操作系统安全监视框架。Shadow-box拥有一个受shadow
play启发的新颖架构。我们从头开始构建了Shadow-box，它主要由轻量级管理程序和安全监视程序组成。

轻量级管理程序Light-box可有效隔离客户机计算机内的操作系统，并将客户机的静态和动态内核对象投射到主机中，以便主机中的安全监视器可以调查投射映像。安全监视器Shadow-Watcher将事件监视器放在静态内核元素上，并测试动态内核元素的安全性。

Shadow-box操纵从客户机物理地址到主机物理地址的地址转换，以排除对主机和管理程序空间的未授权访问。通过这种方式，即使操作系统受到安全威胁，Shadow-box也可以正确地内省（introspect）客户机操作系统并协调所有访问。

## Shadow-Box 架构

Shadow-box是一个使用虚拟化技术的轻量级实用安全监视框架。

![architecture.png](https://image.3001.net/images/20190720/1563603864_5d32b39818a73.png!small)

我们开发了一个安全监视框架Shadow-box，通过过滤掉对重要内核元素的未授权访问，并定期保护内核元素的完整性来保障操作系统的安全。Shadow-box依赖于它的两个子部分：轻量级管理程序和安全监视器。轻量级管理程序Light-box可以高效地隔离客户机计算机内的操作系统，并将客户机的静态和动态内核对象投射到主机中，以便主机中的安全监视器可以调查投影映像。安全监视器Shadow-watcher将事件监视器放在静态内核元素上，并测试动态内核元素的安全性。在主机内运行，即使在客户机操作系统被破坏的情况下，也能在不受恶意干扰的测试客户机的安全性。

如果你想了解更多有关Shadow-box的信息，请参阅我在[Black Hat Asia
2017](https://www.blackhat.com/asia-17/briefings.html#myth-and-truth-about-hypervisor-based-kernel-protector-the-reason-why-you-need-shadow-box) 和
[HITBSecConf
2017](http://conference.hitb.org/hitbsecconf2017ams/sessions/shadowbox-the-practical-and-omnipotent-sandbox/)的演讲和论文。

## 如何构建

准备内核构建环境（Ubuntu 16.04）

因为Shadow-box保护内核的代码区域，所以它会与运行时内核修补功能（CONFIG_JUMP_LABEL）冲突。因此，如果你的内核使用运行时内核修补程序功能，则应删除该功能。想要删除它，你需要设置内核构建环境，更改内核选项并安装。过程如下：

    
    
    # Prepare kernel source and build environment.
    $> apt-get source linux
    $> sudo apt-get build-dep linux
    $> sudo apt-get install ncurses-dev
    
    # Make new .config file.
    $> cd linux-<your_kernel_version>
    $> cp /boot/config-<your_kernel_version> .config
    $> make menuconfig
    # Load the .config file using the "Load" menu and save it to .config using the "Save" menu.
    
    $> sed -i 's/CONFIG_JUMP_LABEL=y/# CONFIG_JUMP_LABEL is not set/g' .config
    
    # Build kernel and modules.
    $> make -j8; make modules
    
    # Install kernel and modules.
    $> sudo make modules_install
    $> sudo make install

##  **准备 Shadow-Box 和内核符号**

Shadow-box应定位数据结构和函数以进行内核的完整性验证。这些符号可以通过使用kallsyms找到，但所有符号都不会暴露于kallsyms。因此，Shadow-box使用System.map文件嵌入符号和内核版本。关于如何在Shadow-box中添加符号和内核版本如下：

    
    
    # Prepare Shadow-box source.
    $> git clone https://github.com/kkamagui/shadow-box-for-x86.git
    $> cd shadow-box-for-x86
    
    # Prepare kernel symbols.
    $> uname -v
    #37-Ubuntu SMP Mon Apr 18 18:33:37 UTC 2016			<== Kernel version
    
    # Copy system.map file to kernel_version name.
    $> cp /boot/System.map-<your_kernel_version> system.map/"#37-Ubuntu SMP Mon Apr 18 18:33:37 UTC 2016.map"

## 构建 Shadow-Box

内核符号准备就绪后，键入“make”命令构建Shadow-box。然后你可以在同一目录中找到shadow_box.ko。

    
    
    $> make
    $> ls
    shadow_box.ko shadow_box.h ...

## 如何使用

Shadow-box是可加载的内核模块（LKM）。因此，当你需要保护时，可以使用insmod命令将shadow-box.ko模块加载到内核中。

    
    
    $> sudo insmod shadow-box.ko

![4.png](https://image.3001.net/images/20190720/1563603892_5d32b3b4c20fe.png!small)

加载Shadow-box后，你可以使用Adore-ng等rootkit测试Shadow-box的保护机制。如果你想观看演示视频，请点击此处[ [Demo
1](https://youtu.be/3_cFDVHWCXA)][ [Demo 2](https://youtu.be/s7iZYg4vP4E)]。

这是rootkit的检测示例。如果Shadow-box检测到rootkit，则Shadow-box会写入有关rootkit攻击的内核日志消息。

    
    
    # Load Adore-ng rootkit by command-line.
    $> insmod adore_ng.ko
    Segmentation fault (codre dumped)
    
    # Show kernel log messages.
    $> dmesg
    ... omitted ...
    [    4.182249] Bluetooth: BNEP filters: protocol multicast
    [    4.182252] Bluetooth: BNEP socket layer initialized
    [   43.615020] shadow_box: module verification failed: signature and/or required key missing - tainting kernel
    [   43.625298]      
    [   43.625299] ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗      ██████╗  ██████╗ ██╗  ██╗
    [   43.625300] ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ██║      ██╔══██╗██╔═══██╗╚██╗██╔╝
    [   43.625301] ███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║█████╗██████╔╝██║   ██║ ╚███╔╝ 
    [   43.625302] ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║╚════╝██╔══██╗██║   ██║ ██╔██╗ 
    [   43.625303] ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝      ██████╔╝╚██████╔╝██╔╝ ██╗
    [   43.625303] ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝       ╚═════╝  ╚═════╝ ╚═╝  ╚═╝
    [   43.625304]      
    [   43.625304]                Lightweight Hypervisor-Based Kernel Protector
    [   43.625305]      
    [   43.633127] Shadow-box: CPU Count 4
    [   43.633128] Shadow-box: Booting CPU ID 0
    [   43.648616] Shadow-box: Protect Kernel Code Area
    [   43.670134] Shadow-box:     [*] Complete
    [   43.670135] Shadow-box: Protect Module Code Area
    [   43.677168] Shadow-box:     [*] Complete
    [   43.677338] Shadow-box: Framework Preinitialize
    [   43.678077] Shadow-box:     [*] Complete
    [   43.702142] Shadow-box: Framework Initailize
    [   43.702180] Shadow-box:     [*] Task count 225
    [   43.702181] Shadow-box:     [*] Module count 86
    [   43.702182] Shadow-box:     [*] Complete
    [   44.793463] Shadow-box: Lock IOMMU
    [   44.794091] Shadow-box:     [*] Lock IOMMU complete
    [   44.921020] Shadow-box: Execution Complete
    [   44.921023] Shadow-box: ErrorCode: 0
    
    #==================================================
    # Adore-ng rootkit module is detected.
    #==================================================
    [   67.081071] Shadow-box: VM [0] Kernel module is loaded. Current PID: 1805, PPID: 1804, process name: insmod, module: adore_ng
    
    [   67.081411]  ▄▄▄      ▓█████▄  ▒█████   ██▀███  ▓█████        ███▄    █   ▄████ 
    [   67.081412]  ▒████▄    ▒██▀ ██▌▒██▒  ██▒▓██ ▒ ██▒▓█   ▀        ██ ▀█   █  ██▒ ▀█▒ 
    [   67.081413]  ▒██  ▀█▄  ░██   █▌▒██░  ██▒▓██ ░▄█ ▒▒███    ███  ▓██  ▀█ ██▒▒██░▄▄▄░ 
    [   67.081414]  ░██▄▄▄▄██ ░▓█▄   ▌▒██   ██░▒██▀▀█▄  ▒▓█  ▄  ▒▒▒  ▓██▒  ▐▌██▒░▓█  ██▓ 
    [   67.081415]   ▓█   ▓██▒░▒████▓ ░ ████▓▒░░██▓ ▒██▒░▒████▒      ▒██░   ▓██░░▒▓███▀▒ 
    [   67.081415]    ▒▒   ▓▒█░ ▒▒▓  ▒ ░ ▒░▒░▒░ ░ ▒▓ ░▒▓░░░ ▒░ ░      ░ ▒░   ▒ ▒  ░▒   ▒ 
    [   67.081416]      ▒   ▒▒ ░ ░ ▒  ▒   ░ ▒ ▒░   ░▒ ░ ▒░ ░ ░  ░      ░ ░░   ░ ▒░  ░   ░ 
    [   67.081417] 	   ░   ▒    ░ ░  ░ ░ ░ ░ ▒    ░░   ░    ░            ░   ░ ░ ░ ░   ░ 
    [   67.081418] 	         ░  ░   ░        ░ ░     ░        ░  ░               ░       ░ 
    [   67.081418] 			            ░                                                       
    [   67.081419] Hide process PID 1738
    
    #==================================================
    # A memory attack at FFFFFFFF81A2D2400 is detected.
    #==================================================
    [   67.081448] Shadow-box: VM [0] Memory attack is detected
    [   67.081450] Shadow-box: VM [0] Guest Linear: -2120035776, FFFFFFFF81A2D240
    [   67.081451] Shadow-box: VM [0] Guest Physical: 44225088, 0000000002A2D240
    [   67.081452] Shadow-box: VM [0] virt_to_phys: virt FFFFFFFF81A2D240 phys 0000000002A2D240
    [   67.081453] Shadow-box: ErrorCode: 4
    [   67.081463] general protection fault: 0000 [#1] SMP 
    [   67.081485] Modules linked in: bnep snd_hda_codec_hdmi dell_led snd_hda_codec_realtek snd_hda_codec_generic nls_iso8859_1 snd_hda_intel snd_hda_codec intel_rapl x86_pkg_temp_thermal intel_powerclamp coretemp snd_hda_core kvm_intel snd_hwdep kvm dell_wmi sparse_keymap input_leds joydev snd_pcm irqbypass crct10dif_pclmul crc32_pclmul dcdbas snd_seq_midi snd_seq_midi_event aesni_intel aes_x86_64 lrw gf128mul glue_helper ablk_helper snd_rawmidi cryptd snd_seq serio_raw
    
    #==================================================
    # A hidden process, backdoor, is detected.
    #==================================================
    [   67.081632] Shadow-box: VM [1] Task count is different: expect 220, real 219
    [   67.081653]  snd_seq_device
    [   67.081659] Shadow-box: VM [1] Task PID: 1738, TGID: 1738, fork name: backdoor, process name: backdoor is hidden
    
    [   67.081692]  snd_timer snd soundcore mei_me shpchp mei hci_uart btbcm btqca 8250_fintek btintel bluetooth intel_lpss_acpi intel_lpss acpi_als kfifo_buf acpi_pad industrialio mac_hid parport_pc ppdev lp parport autofs4 hid_generic usbhid i915_bpo intel_ips i2c_algo_bit drm_kms_helper syscopyarea sysfillrect e1000e psmouse sysimgblt fb_sys_fops ptp drm ahci pps_core libahci wmi video pinctrl_sunrisepoint i2c_hid pinctrl_intel hid fjes
    [   67.081843] CPU: 0 PID: 1805 Comm: insmod Tainted: G           OE   4.4.0-21-generic #37-Ubuntu
    [   67.081867] Hardware name: Dell Inc. OptiPlex 7040/096JG8, BIOS 1.2.8 01/26/2016
    [   67.081887] task: ffff8801535dd880 ti: ffff880153520000 task.ti: ffff880153520000
    [   67.081908] RIP: 0010:[<ffffffffc00081ac>]  [<ffffffffc00081ac>] init_module+0x1ac/0x1000 [adore_ng]
    [   67.081939] RSP: 0018:ffff880153523c60  EFLAGS: 00010286
    [   67.081974] RAX: ffffffff81a2d240 RBX: ffffffff81e11080 RCX: 0000000000050bc5
    [   67.081993] RDX: ffffffff8127a080 RSI: ffffffffc0620480 RDI: ffff880155001300
    [   67.082012] RBP: ffff880153523c88 R08: 000000000001a080 R09: ffffffff8121be34
    [   67.082032] R10: ffffea00019f9a00 R11: 0000000000000000 R12: ffff880150f87300
    [   67.082051] R13: 0000000000000000 R14: ffffffffc0008000 R15: ffff8801516802a0
    [   67.082071] FS:  00007fabee1ad700(0000) GS:ffff880159c00000(0000) knlGS:0000000000000000
    [   67.082093] CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080040033
    [   67.082109] CR2: 000055b34445f5b8 CR3: 0000000135b46000 CR4: 00000000003426f0
    [   67.082131] DR0: 0000000000000041 DR1: 0000000000000041 DR2: 0000000000000041
    [   67.082151] DR3: 0000000000000041 DR6: 0000000000000041 DR7: 0000000000000041
    [   67.082157] Shadow-box: ErrorCode: 4
    [   67.082180] Stack:
    [   67.082186]  ffffc900012b3fff 00000000b870b587 ffffffff81e11080 ffff880150fa4340
    [   67.082211]  0000000000000000 ffff880153523d08 ffffffff81002123 ffffea000278af80
    [   67.082234]  ffff880153523ce0 0000000000000286 0000000000000001 0000000000000007
    [   67.082258] Call Trace:
    [   67.082270]  [<ffffffff81002123>] do_one_initcall+0xb3/0x200
    [   67.082287]  [<ffffffff811eaeb3>] ? kmem_cache_alloc_trace+0x183/0x1f0
    [   67.082308]  [<ffffffff8118c163>] do_init_module+0x5f/0x1cf
    [   67.082324]  [<ffffffff81109df7>] load_module+0x1667/0x1c00
    [   67.082341]  [<ffffffff811063a0>] ? __symbol_put+0x60/0x60
    [   67.082358]  [<ffffffff812126b0>] ? kernel_read+0x50/0x80
    [   67.082374]  [<ffffffff8110a5d4>] SYSC_finit_module+0xb4/0xe0
    [   67.082391]  [<ffffffff8110a61e>] SyS_finit_module+0xe/0x10
    [   67.082408]  [<ffffffff818244f2>] entry_SYSCALL_64_fastpath+0x16/0x71
    [   67.082426] Code: ff fe ff 0f 22 c0 49 8b 44 24 18 48 89 15 25 83 61 00 48 c7 c6 80 04 62 c0 48 8b 40 30 48 8b 40 20 48 8b 10 48 89 15 cc 82 61 00 <48> c7 00 f0 9e 61 c0 48 c7 c2 70 90 61 c0 48 8b 3d 67 3e 61 00 
    [   67.082539] RIP  [<ffffffffc00081ac>] init_module+0x1ac/0x1000 [adore_ng]
    [   67.082559]  RSP <ffff880153523c60>
    [   67.089935] ---[ end trace f2a6f5de2615c18a ]---    
    #==================================================
    # A hidden module, adore_ng, is detected.
    #==================================================
    [   67.120456] Shadow-box: VM [2] Module count is different: expect 87, real 86
    [   67.120479] Shadow-box: VM [2] Hidden module name: adore_ng, ptr: ffffffffc061c080
    [   67.121298] Shadow-box: ErrorCode: 4

## 警告

Shadow-box保护来自rootkit的内核代码，只读数据，系统表，权限寄存器等。因此，如果你想使用Shadow-box，则应禁用以下某些功能。

1、禁用CONFIG_JUMP_LABEL

更改内核配置（.config）

2、禁用休眠并暂停

更改系统电源管理设置

3、禁用IRQ重映射以使用IOMMU保护功能

在grub.cfg文件中的linux/boot/vmlinuz...行的末尾插入intremap=off

## 已知问题

Shadow-box可能会出现以下问题。

1、太多日志在secure world中会导致系统间歇性地停止工作。

如果你想记录大量信息，请将FIFO设置为kfifo并连接normal world 和 secure world

## 致谢

Shadow-box已被用于保护Gooroom平台的内核，这是一个开源项目。这项工作得到了韩国政府（MSIP）（No.R0236-15-1006，开源软件推广）信息与通信技术促进研究所（IITP）的资助。

 ***参考来源：[GitHub](https://github.com/kkamagui/shadow-box-for-x86)，FB小编secist编译，转载请注明来自FreeBuf.COM**

