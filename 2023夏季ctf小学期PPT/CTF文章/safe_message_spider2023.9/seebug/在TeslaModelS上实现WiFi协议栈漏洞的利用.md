**作者：腾讯科恩实验室  
公众号：<https://mp.weixin.qq.com/s/rULdN3wVKyR3GlGBhunpoQ>**

在过去的两年里，腾讯科恩实验室对特斯拉汽车的安全性进行了深入的研究并在Black Hat 2017与Black Hat
2018安全会议上两次公开分享了我们的研究成果。我们的研究成果覆盖了车载系统的多个组件。我们展示了如何攻入到特斯拉汽车的CID、IC、网关以及自动驾驶模块。这一过程利用了内核、浏览器、MCU固件、UDS协议及OTA更新过程中的多个漏洞。值得注意的是，最近我们在自动驾驶模块上做了一些有趣的工作。我们分析了自动雨刷和车道识别功能的具体实现细节并且在真实的世界中对其中的缺陷进行了攻击尝试。

为了更深入的了解特斯拉车载系统的安全性，我们研究了无线功能模块（Model
S上的Parrot模块）并在其中找到了两个漏洞。一个存在于无线芯片固件当中，另一个存在于无线芯片驱动当中。通过组合这两个漏洞，攻击者可以在Parrot模块的Linux系统当中执行任意命令。

本文会揭示这两个漏洞的细节并介绍漏洞的利用过程来证明这两个漏洞是可以被攻击者用来通过无线协议远程攻入到特斯拉车载系统当中的。

![img](https://images.seebug.org/content/images/2020/01/02/1577944962000-image1.png-w331s)

## Parrot 模块

Tesla Model
S上的Parrot模块是一个第三方模块，型号是FC6050W，它集成了无线及蓝牙功能。Parrot通过USB协议与CID相连。Parrot运行着Linux系统并使用了USB
Ethernet gadget，因此Parrot与CID在USB协议基础之上实现了以太网连接。当Tesla Model
S连接到无线网络时，实际上Parrot模块连接到该无线网络中。这时，网络流量被Parrot从CID路由到外部网络。

从一份公开的资料[1]中，我们找到了Parrot模块的硬件组成。

![img](https://images.seebug.org/content/images/2020/01/02/1577944963000-image2.png-w331s)

Parrot模块的引脚定义也在这份datasheet中。Linux系统的shell可以通过Debug UART引脚得到。

![img](https://images.seebug.org/content/images/2020/01/02/1577944963000-image3.png-w331s)

![img](https://images.seebug.org/content/images/2020/01/02/1577944963000-image4.png-w331s)

其中的reset引脚连到到CID的GPIO上，因此CID有能力通过下列命令重置整个Parrot模块

    
    
    echo 1 \> /sys/class/gpio/gpio171/valuesleep 1echo 0 \> /sys/class/gpio/gpio171/value

## Marvell 无线芯片

Marvell
88W8688是一款低成本、低功耗、高度集成的支持IEEE802.11a/g/bMAC/基带/射频集无线和蓝牙于一体的基带/射频系统级芯片[2]。

Marvell官方网站[3]提供了一份该芯片的设计框图。

![img](https://images.seebug.org/content/images/2020/01/02/1577944963000-image5.png-w331s)

Marvell 88W8688包含了一个嵌入式高性能Marvell Ferocean ARM9处理器。通过修改固件，我们获得了Main
ID寄存器中的数值0x11101556，据此推断88W8688使用的处理器型号可能是Feroceon 88FR101 rev
1。在Parrot模块上，Marvell 88w8688芯片通过SDIO接口与主机系统相连。

Marvell 88W8688的内存区域如下：

![img](https://images.seebug.org/content/images/2020/01/02/1577944963000-table1.png-w331s)

## 芯片固件

固件的下载过程包含两个阶段。首先是辅助固件”sd8688_helper.bin”的下载，然后是主固件”sd8688.bin”的下载。辅助固件负责下载主固件及验证主固件中每个数据块是否正确。主固件中包含了很多的数据块，每个块的结构定义如下。

    
    
    struct fw_chunk {     int chunk_type;  int addr;  unsigned int length;  unsigned int crc32;  unsigned char [1];} __packed;

88w8688固件的运行基于ThreadX实时操作系统，该实时操作系统多用于嵌入式设备。ThreadX的代码存在于ROM内存区域，因此固件”sd8688.bin”实际上作为ThreadX的应用运行。

在特斯拉上，固件”sd8688.bin”的版本ID是”sd8688-B1, RF868X, FP44,
13.44.1.p49”,本文的所有研究均基于此版本。

在逆向识别出所有的ThreadX API之后，各个任务的信息便可以得到。

![img](https://images.seebug.org/content/images/2020/01/02/1577944963000-table2.png-w331s)

同时，内存池的相关信息也可以得到。

![img](https://images.seebug.org/content/images/2020/01/02/1577944963000-table3.png-w331s)

## 日志及调试

芯片固件没有实现Data Abort、Prefetch
Abort、Undefine和SWI等CPU异常向量的处理过程。这意味着，固件崩溃后处理器会停止工作。我们不知道固件在哪里因何崩溃。

![img](https://images.seebug.org/content/images/2020/01/02/1577944963000-image6.png-w331s)

所以我们修改了固件，并自己实现了这些异常处理过程。这些处理过程会记录固件崩溃时的一些寄存器信息，包括通用寄存器，系统模式及中断模式下的状态寄存器和链接寄存器。通过这种方式，我们可以知道崩溃时系统模式或中断模式下的一些寄存器信息。

![img](https://images.seebug.org/content/images/2020/01/02/1577944963000-image7.png-w331s)

我们将这些寄存器信息写到末使用的内存区域，例如0x52100~0x5FFFF。这样，这些信息在芯片重置后仍然可以被读取。

在实现了undefine异常处理过程及修改一些指令为undefine指令后，我们可以在固件运行时获取或设置寄存器的内容。用这种方式，我们可以调试固件。

将新的固件下载到芯片中运行，可在内核驱动中发送命令HostCmd_CMD_SOFT_RESET到芯片。随后芯片会重置，新的固件会下载。

## 固件中的漏洞

88w8688芯片支持802.11e WMM (Wi-Fi Multimedia)协议。在这个协议中，STA会通过Action帧来发送ADDTS
request给其他设备。请求中包含有TSPEC信息。然后其他设备同样通过Action帧返回ADDTS response。下面是该Action帧的具体格式。

![img](https://images.seebug.org/content/images/2020/01/02/1577944963000-image8.png-w331s)

ADDTS的整个过程如下：当系统想要发送ADDTS请求时，内核驱动会发送HostCmd_CMD_WMM_ADDTS_REQ命令给芯片，然后芯片将ADDTS请求通过无线协议发送出去。当芯片收到ADDTS
response后，将该回复信息去掉Action帧头部复制到HostCmd_CMD_WMM_ADDTS_REQ结构体，作为ADDTS_REQ命令的结果在HostCmd_DS_COMMAND结构体中返回给内核驱动。内核驱动来实际处理ADDTS
response。

    
    
    struct _HostCmd_DS_COMMAND{    u16 Command;    u16 Size;    u16 SeqNum;    u16 Result;    union    {        HostCmd_DS_GET_HW_SPEC hwspec;        HostCmd_CMD_WMM_ADDTS_REQ;        //…….     }}

漏洞存在于将ADDTS
response复制到HostCmd_CMD_WMM_ADDTS_REQ结构体的过程中。函数wlan_handle_WMM_ADDTS_response在复制时，需要复制的长度为Action帧的长度减去4字节Action帧头部。如果Action帧只有头部且长度为3。那么复制时的长度会变为0xffffffff。这样，内存将会被完全破坏，导致稳定的崩溃。

## 驱动中的漏洞

在芯片与驱动之间，有三种数据包类型通过SDIO接口传递，MV_TYPE_DATA, MV_TYPE_CMD和
MV_TYPE_EVENT。其定义可在源码中找到。

![img](https://images.seebug.org/content/images/2020/01/02/1577944963000-image9.png-w331s)

命令处理的过程大致如下。驱动接收到用户态程序如ck5050、wpa_supplicant发来的指令，在函数wlan_prepare_cmd()中初始化HostCmd_DS_COMMAND结构体，该函数的最后一个参数pdata_buf指向与命令有关的结构，函数wlan_process_cmdresp()负责处理芯片返回的结果并将相关信息复制到pdata_buf指向的结构中。

    
    
    intwlan_prepare_cmd(wlan_private * priv,                 u16 cmd_no,                 u16 cmd_action,                 u16 wait_option, WLAN_OID cmd_oid, void *pdata_buf);

漏洞存在于函数wlan_process_cmdresp()处理HostCmd_CMD_GET_MEM的过程中。函数wlan_process_cmdresp()没有检查HostCmd_DS_COMMAND结构体中的成员size的大小是否合法。因此在把HostCmd_DS_COMMAND结构中的数据复制到其他位置时发生了内存溢出。

## 芯片内代码执行

很显然，固件中的漏洞是一个堆溢出。为了利用这个漏洞实现芯片内代码执行，我们需要知道memcpy()函数是怎样破坏内存的，以及芯片是怎样崩溃的，在哪里崩溃的。

为了触发这个漏洞，action帧头部的长度应该小于4。同时我们需要在Action帧中提供正确的dialog
token，这意味着memcpy()接收的长度只能是0xffffffff。源地址是固定的，因为该内存块是从内存池pool_start_id_rmlmebuf分配的，并且这个内存池只有一个内存块。目的地址是从内存池pool_start_id_tx分配的，所以目的地址可能是四个地址中的某一个。

![img](https://images.seebug.org/content/images/2020/01/02/1577944964000-table4.png-w331s)

源地址及目的地址均位于RAM内存区域0xC0000000~0xC003FFFF，但是内存地址0xC0000000到0xCFFFFFFF都是合法的。结果就是，读或写下面这些内存区域会得到完全一样的效果。

![img](https://images.seebug.org/content/images/2020/01/02/1577944964000-table5.png-w331s)

因为内存区域0xC0000000到0xCFFFFFFF都是可读可写的，所以复制过程几乎不会碰到内存的边界。在复制了0x40000个字节后，整个内存可被看作是整体移位了，其中有些数据被覆盖并且丢失了。

![img](https://images.seebug.org/content/images/2020/01/02/1577944964000-image10.png-w331s)

88w8688中的CPU是单核的，所以复制过程中芯片不会崩溃直到有中断产生。因为这时内存已被破坏，在大多数情况下，芯片崩溃在中断过程中。

中断控制器给中断系统提供了一个接口。当一个中断产生时，固件可从寄存器中获取中断事件类型并调用相应的中断处理过程。

![img](https://images.seebug.org/content/images/2020/01/02/1577944964000-table6.png-w331s)

中断源有很多，所以漏洞触发后，芯片可能崩溃在多个位置。

一个可能性是中断0x15的处理过程中，函数0x26580被调用。0xC000CC08是一个链表指针，这个指针在漏洞触发后可能会被篡改。然而，对这个链表的操作很难给出获得代码执行的机会。

![img](https://images.seebug.org/content/images/2020/01/02/1577944964000-image11.png-w331s)

另一个崩溃位置在时钟中断的处理过程中。处理过程有时会进行线程的切换，这时其他任务会被唤醒，那么复制过程就会被暂停。然后芯片可能崩溃在其他任务恢复运行之后。在这种情况下，固件通常崩溃在函数0x4D75C中。

![img](https://images.seebug.org/content/images/2020/01/02/1577944964000-image12.png-w331s)

这个函数会读取一个指针0xC000D7DC，它指向结构TX_SEMAPHORE。触发漏洞后，我们可以覆盖这个指针，使其指向一个伪造的TX_SEMAPHORE结构。

    
    
    typedef struct TX_SEMAPHORE_STRUCT{    ULONG       tx_semaphore_id;    CHAR_PTR    tx_semaphore_name;    ULONG       tx_semaphore_count;    struct TX_THREAD_STRUCT  *tx_semaphore_suspension_list;    ULONG                    tx_semaphore_suspended_count;    struct TX_SEMAPHORE_STRUCT *tx_semaphore_created_next;      struct TX_SEMAPHORE_STRUCT *tx_semaphore_created_previous;} TX_SEMAPHORE;

如果伪造的TX_SEMAPHORE结构中的tx_semaphore_suspension_lis指针刚好指向伪造的TX_THREAD_STRUCT结构。那么当函数_tx_semaphore_put()更新TX_THREAD_STRUCT结构中的链表的时候，我们可以得到一次任意地址写的机会。

![img](https://images.seebug.org/content/images/2020/01/02/1577944964000-image13.png-w331s)

我们可以直接将”BL
os_semaphore_put”指令的下一条指令改成跳转指令来实现任意代码执行，因为ITCM内存区域是RWX的。困难在于我们需要同时在内存中堆喷两种结构TX_SEMAPHORE和TX_THREAD_STRUCT，并且还要确保指针tx_semaphore_suspension_list指向TX_THREAD_STRUCT结构。这些条件可以被满足，但是利用成功率会非常低。

我们主要关注第三个崩溃位置，在MCU中断的处理过程中。指向struct_interface结构的指针g_interface_sdio会被覆盖。

    
    
    struct struct_interface{  int field_0;  struct struct_interface *next;  char *name_ptr;  int sdio_idx;  int fun_enable;  int funE;  int funF;  int funD;  int funA;  int funB; // 0x24  int funG;  int field_2C;};

结构中函数指针funB会被使用。如果g_interface_sdio被篡改，那么就会直接实现代码执行。

![img](https://images.seebug.org/content/images/2020/01/02/1577944964000-image14.png-w331s)

这是当函数interface_call_funB()中的指令”BX
R3”在地址0x3CD4E执行时的一份寄存器日志信息。此时，g_interface_sdio被覆盖成了0xabcd1211。

    
    
    LOG_BP_M0_CPSR      : 0xa000009bLOG_BP_M0_SP        : 0x5fec8LOG_BP_M0_LR        : 0x3cd50LOG_BP_M0_SPSP      : 0xa00000b2LOG_BP_M1_CPSR      : 0xa0000092LOG_BP_M1_SP        : 0x5536cLOG_BP_M1_LR        : 0x4e3d5LOG_BP_M1_SPSP      : 0xa0000013LOG_BP_M2_CPSR      : 0LOG_BP_M2_SP        : 0x58cb8LOG_BP_M2_LR        : 0x40082e8LOG_BP_M2_SPSP      : 0LOG_BP_R1           : 0x1cLOG_BP_R2           : 0LOG_BP_R3           : 0xefdeadbeLOG_BP_R4           : 0x40c0800LOG_BP_R5           : 0LOG_BP_R6           : 0x8000a500LOG_BP_R7           : 0x8000a540LOG_BP_R8           : 0x140LOG_BP_R9           : 0x58cb0LOG_BP_R10          : 0x40082e8LOG_BP_FP           : 0LOG_BP_IP           : 0x8c223fa3LOG_BP_R0           : 0xabcd1211

函数interface_call_funB()在地址0x4E3D0处被MCU中断的处理过程使用。

![img](https://images.seebug.org/content/images/2020/01/02/1577944964000-image15.png-w331s)

当复制的源地址到达0xC0040000时，整个内存可被看作是做了一次偏移。当复制的源地址到达0xC0080000时，整个内存偏移了两次。每次偏移的距离如下。

    
    
    0xC0016478-0xC000DC9B=0x87DD0xC0016478-0xC000E49B=0x7FDD0xC0016478-0xC000EC9B=0x77DD0xC0016478-0xC000F49B=0x6FDD

在多数情况下，漏洞触发后再产生中断时，这样的内存偏移会发生3至5次。所以指针g_interface_sdio会被来自下列地址的数据所覆盖。

    
    
    0xC000B818+0x87DD*1=0xC0013FF50xC000B818+0x87DD*2=0xC001C7D20xC000B818+0x87DD*3=0xC0024FAF0xC000B818+0x87DD*4=0xC002D78C…0xC000B818+0x7FDD*1=0xC00137F50xC000B818+0x7FDD*2=0xC001B7D20xC000B818+0x7FDD*3=0xC00237AF0xC000B818+0x7FDD*4=0xC004B700…0xC000B818+0x77DD*1=0xC0012FF50xC000B818+0x77DD*2=0xC001A7D20xC000B818+0x77DD*3=0xC0021FAF0xC000B818+0x77DD*4=0xC002978C…0xC000B818+0x6FDD*1=0xC00127F50xC000B818+0x6FDD*2=0xC00197D20xC000B818+0x6FDD*3=0xC00207AF0xC000B818+0x6FDD*4=0xC002778C…

地址0xC0024FAF、 0xC00237AF和0xC0021FAF刚好位于一个巨大的DMA buffer
0xC0021F90~0xC0025790之中。这个DMA buffer用于存储无线芯片接收到的802.11数据帧。所以这个DMA
buffer可以用来堆喷伪造的指针。

![img](https://images.seebug.org/content/images/2020/01/02/1577944964000-image16.png-w331s)

为了堆喷伪造的指针，我们可以发送许多正常的802.11数据帧给芯片，其中填满了伪造的指针。DMA
buffer非常大，因此shellcode也可以直接放在数据帧中。为了提高利用的成功率，我们用了Egg Hunter在内存中查找真正的shellcode。

![img](https://images.seebug.org/content/images/2020/01/02/1577944964000-image17.png-w331s)

如果g_interface_sdio被成功的覆盖。Shellcode或egg
hunter会非常的接近0xC000B818。我们所使用的伪造指针是0x41954，因为在地址0x41954+0x24处有一个指针0xC000B991。这样，我们可以劫持$PC到0xC000B991。同时，指针0x41954可被作为正常的指令执行。

    
    
    54 19 ADDS            R4, R2, R504 00 MOVS            R4, R0

用这种方法有25%的成功率获得代码执行。

## 攻击主机系统

内核驱动中的漏洞可通过由芯片发送命令数据包给主机系统来触发。命令HostCmd_CMD_GET_MEM通常由函数wlan_get_firmware_mem()发起。

![img](https://images.seebug.org/content/images/2020/01/02/1577944964000-image18.png-w331s)

这种情况下，pdata_buf指向的buffer由kmalloc()分配，所以这是一个内核堆溢出。在真实环境中函数wlan_get_firmware_mem()不会被用到，并且堆溢出的利用较复杂。

然而，一个被攻陷的芯片在返回某个命令的结果时可以更改命令ID。因此漏洞可以在许多命令的处理过程中被触发。这时，根据pdata_buf指向的位置，漏洞即可以是堆溢出也可以是栈溢出。我们找到了函数wlan_enable_11d()，它把局部变量enable的地址作为pdata_buf。因此我们可以触发一个栈溢出。

![img](https://images.seebug.org/content/images/2020/01/02/1577944964000-image19.png-w331s)

函数wlan_enable_11d()被wlan_11h_process_join()调用。显然HostCmd_CMD_802_11_SNMP_MIB会在与AP的连接过程中被使用。固件中的漏洞只能在Parrot已经加入AP后使用。为了触发wlan_enable_11d()中的栈溢出，芯片需要欺骗内核驱动芯片已经断开与AP的连接。接着，驱动会发起重连，在这个过程中HostCmd_CMD_802_11_SNMP_MIB会发送给芯片。于是，为了触发重连过程，芯片需要发送EVENT_DISASSOCIATED事件给驱动。

当在芯片中触发漏洞并获得代码执行之后芯片不能再正常工作。所以我们的shellcode需要自己处理重连过程中的一系列命令并返回相应的结果。在命令HostCmd_CMD_802_11_SNMP_MIB来到之前，唯一一个我们要构造返回结果的命令是HostCmd_CMD_802_11_SCAN。下面是断开连接到触发内核漏洞的整个过程。

![img](https://images.seebug.org/content/images/2020/01/02/1577944964000-image20.png-w331s)

SDIO接口上事件和命令数据包的发送可直接通过操作寄存器SDIO_CardStatus和SDIO_SQReadBaseAddress0来完成。SDIO接口上获得内核发来的数据可借助SDIO_SQWriteBaseAddress0寄存器。

## Linux系统中命令执行

Parrot的Linux内核2.6.36不支持NX，所以可以直接在栈上执行shellcode。同时结构HostCmd_DS_COMMAND中的size是u16类型，所以shellcode可以足够大来做许多事情。

在触发栈溢出并控制$PC之后，$R7刚好指向内核栈，所以可以很方便的执行shellcode。

在shellcode中的函数run_linux_cmd调用了Usermode Helper API来执行Linux命令。

## 远程获取shell

在漏洞触发后，芯片中的内存被完全破坏无法继续正常工作。同时内核栈已损坏，无法正常工作。

为了让Parrot的无线功能可以重新正常工作，我们做了如下事情：

1.在向内核发送完payload之后，我们通过如下命令重置了芯片。在这之后，内核驱动会重新发现芯片然后重新下载固件。

    
    
    *(unsigned int *)0x8000201c|=2;*(unsigned int *)0x8000a514=0;*(unsigned int *)0x80003034=1;

2.在shellcode的函数fun_ret()中调用内核函数rtnl_unlock()来解开rtnl_mutex锁。否则Linux的无线功能会无法正常功能，导致Parrot被CID重启。

3.在shellcode的函数fun_ret()中调用do_exit()来终止用户态进程wpa_supplicant并重新运行，这样就不需要修复内核栈。

4.杀掉进程ck5050并重新运行，否则稍后ck5050会因芯片重置而崩溃，导致Parrot被CID重启。

为了远程获取shell，我们强制让Parrot连入我们自己的AP并修改iptables规则。之后，便可通过23端口访问到Parrot的shell。

最终拿到shell的成功率在10%左右。

## 完整的利用过程

  1. 攻击者发送DEAUTH帧给附近的所有AP。
  2. 当Tesla重连至AP时，攻击者可以嗅探到特斯拉的MAC地址。
  3. 堆喷伪造的指针，然后发送Action帧来触发固件中的漏洞。
  4. 函数memcpy()会一直工作直到有中断产生。
  5. 在芯片内成功执行任意代码。
  6. 第一阶段shellcode发送EVENT_DISASSOCIATED事件给驱动。
  7. 第一阶段shellcode处理一系列命令并等待命令HostCmd_CMD_802_11_SNMP_MIB。
  8. 第一阶段shellcode通过SDIO接口发送payload来触发内核栈溢出。
  9. 第二阶段shellcode执行并调用call_usermodehelper()函数。
  10. 成功执行Linux系统命令并尝试修复Parrot的无线功能。
  11. 攻击者搭建自己的AP热点及DHCP服务器。
  12. 通过Linux命令强制Parrot加入攻击者建立的AP热点并修改iptables规则。
  13. 攻击者可通过Parrot的23端口获得Parrot的shell。

![img](https://images.seebug.org/content/images/2020/01/02/1577944964000-image21.png-w331s)

## 演示视频

## 总结

在这篇文章中，我们展示了Marvell无线芯片固件及驱动中漏洞的具体细节，并演示了如何利用这两个漏洞仅通过发送无线数据包的形式远程在Parrot系统内部实现命令执行。

## 负责任的漏洞披露

本文所提到的两个漏洞已于2019年3月报告给Tesla，Tesla已经在2019.36.2版本中对该漏洞进行了修复。同时，Marvell也修复了该漏洞并针对该漏洞发布了安全公告[4]。漏洞研究报告的披露已事先与特斯拉沟通过，特斯拉对我们的发布知情。

你可以通过下列链接来跟踪本文提到的漏洞。

  1. <https://www.cnvd.org.cn/flaw/show/CNVD-2019-44105>
  2. <http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201911-1040>
  3. <http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201911-1038>
  4. <https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-13581>
  5. <https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-13582>

## 参考资料

[1] <https://fccid.io/RKXFC6050W/Users-Manual/user-manual-1707044>

[2] <https://www.marvell.com/wireless/88w8688/>

[3] <https://www.marvell.com/wireless/assets/Marvell-88W8688-SoC.pdf>

[4] <https://www.marvell.com/documents/ioaj5dntk2ubykssa78s/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1106/>

