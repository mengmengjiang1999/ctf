文章目录：

  * 【二进制分析】佳能打印机DryOS操作系统代码分析与ShellCode利用
    * 启动加载器分析
    * 固件分析
    * 寻找漏洞
    * 漏洞代码
    * 漏洞利用方法
      * DryOS 分配器
      * 漏洞攻击场景
      * 后期漏洞利用

# 【二进制分析】佳能打印机DryOS操作系统代码分析与ShellCode利用

原文链接：<https://www.synacktiv.com/en/publications/the-printer-goes-brrrrr>  
翻译感受：这篇文章作者本身写得非常有水平，并且图文丰富，操作点理解起来是比较难的，文中涉及了大量操作系统知识，例如状态机、栈、段等，反复翻译了好几遍才有了以下通顺易读的结果。

>
> 网络打印机首次在2021年的美国奥斯汀城Pwn2Own比赛中亮相。比赛中包括了三种流行的激光打印机：惠普（HP）、利盟（Lexmark）和佳能（Canon）。在比赛中，我们团队（Synacktiv）成功入侵了所有这些打印机，从而赢得了整个比赛。本文将重点介绍我们如何在佳能打印机上实现代码执行的过程。

从攻击者的角度来看，网络打印机是一个很好的攻击目标，因为它们很少被重新安装配置或检查，因此变成网络上隐藏攻击的完美场所。此外，它们为攻击者提供了持久化访问敏感文档的可能性，这些文档甚至可能被扫描或打印。佳能
Image CLASS MF644Cdw打印机是在2021年奥斯汀Pwn2Own比赛期间被攻击的三台打印机之一。

每个想要参加Pwn2Own比赛的团队都要注册一台或多台设备，他们希望在比赛中攻破这些设备。然后，如果他们在三次尝试中成功了其中一次，他们将获得“主人公”积分、现金奖励（根据目标设备而异）和设备本身。这些“主人公”积分用于建立总排名，以便在比赛结束时把“主人公”的称号授予赢家。我们在第一次尝试中就攻破了佳能打印机，因此赢得了2个“主人公”积分和2万美元的现金奖励。

![](./img/866296302679954638.png)

## 启动加载器分析

引导加载程序，其中包括BIOS引导加载程序和UEFI引导加载程序。BIOS引导加载程序在较旧的计算机上可以找到，它使用基本输入/输出系统(BIOS)与硬件设备通信。另一方面，UEFI引导加载程序出现在较新的计算机上，使用统一可扩展固件接口(UEFI)与硬件设备通信。

对引导装载程序的分析通常包括检查它的代码，以了解它是如何工作的以及它做了什么，涉及对代码进行逆向工程，以识别关键功能和算法，以及分析任何嵌入的数据或配置文件。

引导加载程序安全性的一个重要方面是确保它不会被恶意行为者轻易修改或替换。这涉及诸如安全引导之类的技术，安全引导使用数字签名来验证引导加载程序的完整性，然后才允许它运行，分析引导加载程序是理解计算机系统的底层架构并确保其安全性和稳定性的重要步骤。

启动逆向工程研究的第一步是获取设备执行的二进制文件。为此，一种方法是转储设备的存储器。观察印刷电路板，我们可以识别出一些有趣的集成电路和一个可能的UART连接器

![](./img/8761903360161722382.png)

根据其上的标识，Flash电路是W25Q16JV，一种16Mbit串行NOR
Flash。使用其数据手册中描述的引脚配置，可通过使用SOP8夹和CH341A以及[flashrom](https://www.flashrom.org/Flashrom).  
轻松提取Flash的内容。

![](./img/419798372828561297.png)

转储的二进制文件不包含文件系统、ELF或PE可执行文件，但可能仍然包含编译后的二进制文件，正如此binwalk输出所述：

> 关于ELF文件和PE文件：  
>  ELF是主要用于Unix系统的二进制可执行文件格式，而PE是主要用于Windows系统的二进制可执行文件格式。因此，它们的头部结构和标记的方式也不同。  
>
> ELF文件包含多个节区（section），并且每个节区都可以包含代码、数据或元数据等信息。而PE文件使用段（segement）来组织程序代码和数据，每个段包含多个节。  
>
> ELF文件和PE文件还有一些特定的区域用于存储符号表、重定位信息、调试信息以及其他元信息，这些信息可以帮助链接器（linker）将多个目标文件链接成一个可执行文件，ELF文件和PE文件都是用于描述可执行文件格式的标准。
    
    
    $ binwalk flash.bin
    
    DECIMAL       HEXADECIMAL     DESCRIPTION
    --------------------------------------------------------------------------------    336448        0x52240         Zlib compressed data, default compression
    337968        0x52830         Zlib compressed data, default compression
    341524        0x53614         Zlib compressed data, default compression
    348537        0x55179         Copyright string: "Copyright (C) 1997-2015 by CANON Inc."
    350068        0x55774         Certificate in DER format (x509 v3), header length: 4, sequence length: 859
    351488        0x55D00         SHA256 hash constants, little endian
    361256        0x58328         Unix path: /home/nca/workspace/RB-EMERALD/printing_pf/release/modules/dryos/../dryos/src/mohacs_boot/device/lcd_7line.c
    361468        0x583FC         Unix path: /home/nca/workspace/RB-EMERALD/printing_pf/release/modules/dryos/../dryos/src/mohacs_boot/device/emmc.c
    361748        0x58514         Unix path: /home/nca/workspace/RB-EMERALD/printing_pf/release/modules/dryos/../dryos/src/mohacs_boot/device/sicdlIntegritycheck.c
    362256        0x58710         Unix path: /home/nca/workspace/RB-EMERALD/printing_pf/release/modules/dryos/../dryos/src/mohacs_boot/device/sicdlRomData.c
    365496        0x593B8         Unix path: /home/nca/workspace/RB-EMERALD/printing_pf/release/modules/dryos/../dryos/src/oscore/stdlib/iobuf.c
    365712        0x59490         Unix path: /home/nca/workspace/RB-EMERALD/printing_pf/release/modules/dryos/../dryos/src/mohacs_boot/drysh/cmd_chkcachelib.c
    444441        0x6C819         Certificate in DER format (x509 v3), header length: 4, sequence length: 1288
    […]
    

接着，我们在 [IDA Pro](https://hex-rays.com/ida-pro/)
中加载了转储的二进制文件来使用逆向工程的方法。在找到绝对地址后，我们推断出该二进制文件的加载地址为
0x10000000。但是，这并不是设备上运行的固件部分，而只是用于启动它的引导加载程序，实际的固件存储在 eMMC 上的地址为
0x1500000，并映射到地址 0x40b00000。

    
    
    if ( emmc_direct_read(0x40B00000, 0x1500000u, 0x40u) != 0x40 )
      {
        printf("BOOTABLE HEADER READ ERROR\n");
        return -1;
      }
      if ( BOOTLOADER_GET_ROM_HEADER_INFO(&v7, (nca1_header *)0x40B00000) )
      {
        printf("BOOTABLE GET ROM HEADER ERROR \n");
        return -1;
      }
      if ( BOOTLOADER_ROM_HEADER_HEADER_CHKSUM(&v7, 0x40B00000) )
      {
        printf("BOOTABLE ROM HEADER CHECK ERROR \n");
        return -1;
      }
      printf("BOOTLOADER BOOTABLE START\n");

引导加载程序能够将固件 "下载" 到 eMMC 存储器中。根据反编译的代码，固件格式由以 4
个字节为首的标志头组成，并且根据这个标志头，内容会进行混淆操作。

    
    
    int __fastcall firmware_header_check(_BYTE a1[4], int a2, int a3, unsigned int a4)
    {
      unsigned int magic; // r0
      unsigned int v6; // [sp+0h] [bp-8h] BYREF
    
      v6 = a4;
      like_memcpy((unsigned __int8 *)&v6, a1, 4u, a4);
      magic = bswap32(v6);
      v6 = magic;
      if ( magic == 'NCFW' )
        return 1;
      if ( magic == 0xAFAF9C9C )
        return 0;
      do_assert("unknown = 0x%08x\n", magic);
      return 2;
    }

用于反混淆固件的程序如下：

    
    
    _BYTE *__fastcall NCFW_deobfuscate(_BYTE *data, unsigned int size, char offset)
    {
      unsigned int i; // r3
      unsigned int tmp; // r4
    
      for ( i = 0; i < size; ++i )
      {
        tmp = (unsigned __int8)(data[i] - (offset + i) - 1);
        data[i] = ~((2 * tmp) | (tmp >> 7));
      }
      return data;
    }

## 固件分析

有几种方法可以获取固件。虽然通过转储 eMMC 可能可以检索它，但我们成功地通过简单地设置 HTTP 代理，并使用打印机的管理面板 Web
接口来检查更新的方式获取了它。由于纯文本 HTTP 用于固件更新，因此如果有更新可用，可以轻松获得固件下载
URL。另一种方法是从佳能支持网站上提供的“MF643Cdw/ MF641Cw 固件更新工具”中提取固件。该工具提供为 PE 文件（例如 win-mf643-641-fw-v1005.exe）或 macOS 磁盘映像文件（例如 mac-mf643-641-fw-v1005-64.dmg），并允许使用
Windows 或 MacOS 工作站进行固件更新。PE 文件还是一个自解压缩档案，包含另一个 PE（例如
mf643c_mf642c_mf641c_v1005_typea_w.exe），从中可以提取三个 NCFW
包，因为它们只是作为原始文件附加的。可以按以下方式提取这些 NCFW 包：

    
    
    user@debian:~/ 7z x win-mf643-641-fw-v1005.exe
    user@debian:~/ grep --byte-offset --only-matching --text 'NCFW' mf643c_mf642c_mf641c_v1005_typea_w.exe
    470016:NCFW
    140927837:NCFW
    152682373:NCFW
    user@debian:~ dd if=mf643c_mf642c_mf641c_v1005_typea_w.exe of=package1.bin bs=1 skip=470016 count=$((140927837-470016))
    user@debian:~ dd if=mf643c_mf642c_mf641c_v1005_typea_w.exe of=package2.bin bs=1 skip=140927837 count=$((152682373-140927837))
    user@debian:~ dd if=mf643c_mf642c_mf641c_v1005_typea_w.exe of=package3.bin bs=1 skip=152682373
    

Three NCFW packages can be identified, the firmware itself (134MB), a language
package (12MB), and a DCON package (506K) related to the DC controller. It
should be noted that the CEFW package exists only for firmware updates coming
from the internet.  
The package format is depicted by the following figure:

可以确定三个NCFW包，分别是固件本身（134MB）、语言包（12MB）和与DC控制器相关的DCON包（506K）。需要注意的是，CEFW包仅存在于来自互联网的固件更新中。  
包的格式如下图所示：

![](./img/2122774806754694837.png)

1.当打印机直接从佳能网站之一下载升级时，CEFW包才存在。内容被压缩，并且标头包含以下内容：标头大小、未压缩大小和实际包大小。未压缩的数据包含一个到多个NCFW包。  
2.NCFW包具有标头，其中包括标头大小和包大小，内容使用先前显示的例程进行混淆。解混淆的数据包含一个到多个NCA包。  
3.NCA包表示写入eMMC上的数据块。其标头包含应将包写入的eMMC地址、其大小以及显然的发布日期（直接使用十六进制表示，例如2022年2月22日为0x20220222）和版本。在大多数情况下，NCFW包中的第一个NCA包是特殊的，并包含一个SIG包和一个到多个Mm包：  
4.Sig包保存不同NCA包的数据的加密签名。  
5.Mm包仅是包含其他NCFW包中NCA包的eMMC地址的标头。因此，它允许知道还剩多少个NCA包。

已经实现了一个IDA加载器，以便在IDA中加载佳能固件，我们的链接： [Synacktiv's Github
repository](https://github.com/synacktiv/canon-mf644/).

在本篇文章中，我们将重点关注比赛期间（当时可用的最新固件）运行在目标设备上的版本为10.02的固件。

打印机上的操作系统基于一种名为“DryOS”的自定义实时操作系统。

    
    
    DRYOS version 2.3, release #0059

我们在之前的一项工作中![](),识别出了这个操作系统，它运行在一个相当旧的基于佳能的打印机上（MX920系列），该打印机运行着一个早期版本的dryOS（发布版本号为
_#0049_ ）。这个系统本身是基于日本µITRON实时操作系统规范开发的。DryOs不仅被佳能用于他们的打印机，也被用于数码单反相机上。

正如我们所知道的，这个操作系统提供了一个称为DryShell的调试shell，因此我们尝试使用Saleae逻辑分析仪在主板上找到UART。我们还发现引导加载程序通过UART发送了几条调试信息：

![](./img/2930584434552184714.png)

在确定了UART的位置后，我们进行了简单的焊接（TX、RX和GND），以便使用USB串口适配器。这允许使用pyserial等工具来利用调试shell。一旦打印机启动初始化过程完成，就会显示出DryOs
shell提示符，并可以使用几个命令：

    
    
    Dry> vers
    DRYOS version 2.3, release #0059
      Dry-MK 2.66
      Dry-DM 1.21
      Dry-FSM 0.10
      Dry-EFAT 1.22
      Dry-stdlib 1.57
      Dry-PX 1.15
      Dry-drylib 1.22
      Dry-shell 1.19
      Dry-command alpha 065
    

可以使用xd或xm等命令分别对内存进行转储或修改，这在我们的漏洞利用过程中会非常有用，如下。

## 寻找漏洞

该固件非常庞大，因为它包含超过100,000个函数，可以使用IDA自动发现。由于固件不包含任何符号信息，因此分析此类固件的常见任务是识别可能用于调试目的的字符串。通过简要查看几个函数，我们发现一个日志记录函数在固件中被使用了超过19,000次。以下是一些调用该函数的示例：

    
    
    logf(2802, 3, "[CPC] %s ERROR [Fail getOperationParam]\n", "pjcc_act_checkUserPassword2");
    logf(3604, 3, "[CADM] %s: cadmMessage.message.pEventMessage is NULL", "cadm_sendEventMessage");
    logf(3520, 6, "[USBD] %s EPNo = 0x%X EPNoSS = 0x%X\n", "ScanBULK Out", (unsigned __int8)v14[0], v1)

虽然这个日志记录函数并不总是使用固定的模式，但第三个参数经常匹配类似于“[PREFIX]
%s”的字符串，其中第一个变参函数参数是函数的名称。因此，我们开发了一个基于[BIP](https://github.com/synacktiv/bip)的IDA
Python脚本，利用HexRay的API可以自动地给一些函数命名。

为了确定攻击面并选择可能成为攻击目标的网络服务，我们运行了一个简单的nmap扫描，以查找在默认配置中暴露的所有UDP和TCP端口。然后我们尝试找到每个网络服务的相关DryOs任务及其入口点：

Service | Port | Task name | Notes  
---|---|---|---  
HTTP/HTTPS | 80/TCP, 443/TCP | HtpInit | Canon HTTP Server  
LPD | 515/TCP | LPDCtrl | Line Printer Daemon Protocol  
IPP/IPPS | 631/TCP,10443/TCP | IPP_INIT | Internet Printing Protocol  
Jetdirect | 9100/TCP | RAWctrl | Allow printing using PDL (Page Description
Language)  
Canon MFNP | 8610/TCP 8610/UDP | pscan_TCP_Task pscan_UDP_Task | Print/Scan
jobs over the network (based on BJNP protocol)  
Canon CADM | 9007/TCP 9013/TCP 47545/TCP 47547/TCP (SSL) 47545/UDP |
cadm_tcp_res cadm_tcp_cal cadm_tcp_adm cadm_tcp_sec cadm_udp_adm | Canon
administration proprietary protocol  
NetBIOS | 137/UDP, 138/UDP | smbinit | NetBIOS  
SNMP | 161/UDP | SNAgent | Simple Network Management Protocol  
SLP | 427/UDP | SLPSvcAgent | Service Location Protocol  
WSD | 3702/UDP | WSINinit | Web Services Dynamic Discovery  
Zeroconf | 5353/UDP | BN_BNSet | Multicast DNS (Bonjour Apple)  
  
为了实现基于CGI脚本的网络管理面板，打印机使用了一个定制的HTTP服务器。大多数CGI脚本需要进行身份验证才能访问，因此被排除在我们的分析之外。HTTP服务器还用于处理基于HTTP的IPP请求（Internet
Printing
Protocol）。毫不奇怪，HTTP服务器还处理TLS，因此支持HTTPS和IPPS。与HTTP服务器一样，TLS堆栈似乎也不是基于开源项目开发的。除了IPP之外，还实现了其他标准的打印相关协议，例如LDP或Jetdirect。为了允许设备和服务在典型的办公计算机网络中进行发现，支持诸如SLP、WSD和Zeroconf之类的协议。  
MFNP是一个佳能定制的协议，基于BJNP，允许创建网络上的打印和扫描任务。最后，另一个名为CADM的佳能定制协议允许通过TCP（47545）、TCP+TLS（47547）或UDP（47545）在网络上对打印机进行管理。我们决定将重点放在这个协议上，因为分析数据包流程处理和反向工程命令处理程序是比较直接的。

## 漏洞代码

漏洞存在于CADM服务中。下图展示了CADM消息的格式：

![](./img/5911972904764920205.png)

    
    
    struct pjcc_handlers {
        uint16_t operation_code;
        uint16_t field_2;
        void    *field_4;
        uint32_t field_8;
        uint32_t (*decode_func)(void);
        uint32_t (*encode_func)(void);
        uint32_t (*release_func)(void);
        uint32_t (*field_14)(void);
        uint32_t field_1c;
        uint32_t field_20;
    }

漏洞存在于负责检查密码（操作代码=0x83）的处理程序的解码函数中，即函数pjcc_act_checkUserPassword2（0x4198ecf0）。

下图展示了有效载荷。有效载荷由3个不同的缓冲区以及它们的大小编码为1字节字段组成。

![](./img/2229450141425472861.png)

如下面的代码片段所示，受漏洞影响的函数分配了一个大小为428字节的结构，并在未检查大小的情况下将数据从数据包复制到其内联缓冲区中：

    
    
    uint32_t pjcc_dec_ope_checkUserPassword2(int *a1, int a2, int *a3)
    {
        /* ... */
    
        alloc = (pjcc_checkpassword_payload *)pjcc_zeroAlloc(428);
        pjcc_checkpass_obj = alloc;
    
        v7 = pjcc_dec_ubyte(a1, alloc);
        v12 = pjcc_dec_ulong(a1, (int)&pjcc_checkpass_obj->field_4);
    
        v14 = pjcc_dec_ubyte(a1, &pjcc_checkpass_obj->buffer_len);
        v17 = pjcc_dec_buffer(a1, pjcc_checkpass_obj->buffer_len, (char *)
            pjcc_checkpass_obj->buffer, v15);
    
        v19 = pjcc_dec_ubyte(a1, &pjcc_checkpass_obj->salt_len);
        v22 = pjcc_dec_buffer(a1, pjcc_checkpass_obj->salt_len, (char *)
            pjcc_checkpass_obj->salt, v20);
    
        v24 = pjcc_dec_ubyte(a1, &pjcc_checkpass_obj->hash_len);
    
        result = pjcc_dec_buffer(a1, pjcc_checkpass_obj->hash_len, (char *)
            pjcc_checkpass_obj->hash, v25);
    
        /* ... */
    }

受漏洞影响的对象pjcc_checkpass_obj具有以下数据结构：

    
    
    struct pjcc_checkpassword_payload
    {
        unsigned uint8_t type;
        unsigned uint8_t field_4;
        unsigned uint8_t buffer_len;
        unsigned uint8_t buffer[256];
        unsigned uint8_t salt[32];
        unsigned uint8_t salt_len;
        unsigned uint8_t hash[128];
        unsigned uint8_t hash_len;
    };
    

下图展示了缓冲区salt和hash，它们容易受到基于堆的溢出攻击：

![](./img/4942676691041673377.png)

## 漏洞利用方法

利用这个漏洞需要深入研究分配器的内部机制。

### DryOS 分配器

DryOS分配器是一个简单的“最佳适合”分配器，它维护一个空闲块的单向链表。这个freelist存储在地址0x45f17540处。如下图所示，它是一个空闲块的链表：

![](./img/4964566974644995402.png)

分配函数遍历freelist并返回满足请求大小的第一个块。如果剩余空间（chunk_size - request_size >
metadata_size）大于块元数据（40字节）的大小，则当前块会被分割，并创建一个新块。然后将分配的块从freelist中删除。

![](./img/2571191954935833437.png)

freelist中的块按其地址排序，并且当一个块被释放时，它会被插入回freelist。该块与相邻的空闲块合并。

为了跟踪分配，我们实现了一个DryShell命令，用于转储freelist。

### 漏洞攻击场景

我们的攻击策略是通过溢出hash缓冲区并破坏与受漏洞影响的对象相邻内存中的下一个字段，然后实现在任意地址强制进行后续分配这一目标。

漏洞利用的第一步是将堆进行分片，然后插入大块，以便从大块中分配我们的易受攻击对象，以防止在易受攻击块重新插入空闲列表时，我们的伪造块在早期阶段被使用。  
使用HTTPS请求UI即可创建所需的堆状态：

    
    
    DryOs > !hd
    magic = 0x0, size = 0x5ff930, next = 0x49c1dc88
    magic = 0x46524545, size = 0x48, next = 0x49c1e7c0
    magic = 0x46524545, size = 0x78, next = 0x49c30e50
    magic = 0x46524545, size = 0x30, next = 0x49c30f10
    magic = 0x46524545, size = 0x60, next = 0x49c35c98
    magic = 0x46524545, size = 0x48, next = 0x49d0b578
    magic = 0x46524545, size = 0x60, next = 0x49d14c70
    magic = 0x46524545, size = 0x60, next = 0x49d15a18
    magic = 0x46524545, size = 0x240, next = 0x49d22268
    magic = 0x46524545, size = 0x2848, next = 0x49d24b68
    magic = 0x46524545, size = 0x9198, next = 0x49d2ddd8
    magic = 0x46524545, size = 0x292140, next = 0x0

第二步是触发溢出并破坏已释放块的“下一个”字段。在攻击中，我们将“next”指针设置为地址0x44557b14。选择该地址是因为它位于多个CADM结构（状态机、处理程序等）之前，这些结构包含多个函数指针。此外，由于在地址0x44557b14+4处的内存包含非常大的值（size字段），因此该地址是伪造块的良好候选者。大尺寸允许我们请求无法满足空闲列表中先前空闲块的大量分配。地址0x44557b14+8处的内存包含空指针（next字段），用以关闭空闲列表。请注意，无需在所选地址处拥有字符串“FREE”，因为分配器不进行安全检查。

![](./img/338669950332349598.png)

最后一步是发送一个大的CADM回显数据包，以获取我们的伪造块，并将受控数据与CADM数据结构重叠。更准确地说，我们将这些数据结构重写为原始内容，以避免破坏CADM状态机。我们只破坏负责处理回显请求（pjcc_act_echo）的处理程序，使其指向我们的shellcode。Shellcode也被嵌入在回显数据包的有效负载中，在处理CADM回显数据包时立即执行，按照CADM状态机的要求执行。

### 后期漏洞利用

为了说明漏洞的成功利用，我们决定编写一个显示图片（Synacktiv的标志）在液晶打印机屏幕上的shellcode。因此，第一步是了解屏幕帧缓冲区的工作原理。我们确定它被映射到0x40900000。然后，我们使用DryShell的xm（修改内存）命令，将绿色像素（0x00FF00）作为长整型值写入：

    
    
    Dry> xm --help
    usage: xm [-|addr [access [e_addr value flag]]]
          - : usage
       addr : [0-9a-fA-F]*
     access : b(byte:default) | w(word) | l(long word)
     e_addr : [0-9a-fA-F]*
      value : [0-9a-fA-F]*
       flag : f(fill) | s(search) | u(unmatch)
       -> + : auto increment
    Dry> xm 0x40900000 l 0x40900000 0x00ff00 f

我们注意到液晶打印机屏幕的第一个像素变成了绿色，并迅速恢复到其先前的值。因此，我们理解帧缓冲区只是一个数组，其中使用3个字节来存储单个像素值。这3个字节中的每个分别定义了像素的红色、绿色和蓝色强度。由于屏幕分辨率为800x480像素，因此帧缓冲区的大小为800x480x3。

![](./img/463960492498227712.png)

为了实现一个相当小的shellcode，使用TCP套接字从由Python脚本发送的图片中读取每个像素值，使用PIL（Python图像处理库）实现服务器端。

该shellcode通过调用以下与网络相关的函数来实现：

  * _netSocket_ (0x424bbfb4)
  * _netConnect_ (0x424bc298)
  * _netRecv_ (0x424bc554)

值得注意的是，在sockaddr_in结构中指定的sin_family字段必须设置为0x100，以指定AF_INET（即它与Linux不同，其中AF_INET为0x02）。由于shellcode在无限循环中调用netRecv，因此DryOS能够执行任务上下文切换，只有CADM服务受到漏洞利用的影响。也可以选择另一种方法，即创建一个适当的DryOs任务，并恢复劫持的函数上下文。

漏洞利用代码可以在Synacktiv的Github中找到，下显示了是我们的图片被显示在打印机屏幕上的情况：

![](./img/6864554396009374225.png)

