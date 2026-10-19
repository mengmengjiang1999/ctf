# Zyxel设备eCos固件加载地址分析

阅读量 **192293**

发布时间 : 2021-03-04 14:30:59

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

最近在分析`Zyxel`
某型号设备时，发现该设备的固件无法采用`binwalk`等工具进行提取。根据`binwalk`的提示信息，猜测该设备使用的是`eCos`实时操作系统，其固件是一个单一大文件。由于不知道其加载地址，在使用`IDA`等工具进行分析时，无法建立正确的交叉引用，直接逆向会比较麻烦。而网上与`eCos`固件分析相关的资料不多，在没有相关的芯片文档或`SDK`手册等资料的前提下，从该固件本身出发，通过对固件进行简单分析，寻找固件中引用的固定地址，最终确定了该固件的加载地址。

## binwalk分析

首先使用`binwalk`工具对固件进行分析，如下。尝试使用`-e`选项进行提取时失败，说明该固件可能就是一个单一大文件。从输出中可以看到很多与`eCos`相关的字符串，其中`"eCos
kernel exception handler, architecture: MIPSEL, exception vector table base
address: 0x80000200"`指出了该文件的架构(`MIPSEL`)和异常向量表基地址(`0x80000200`)。

    
    
    $ binwalk RGS200-12P.bin 
    
    DECIMAL       HEXADECIMAL     DESCRIPTION
    --------------------------------------------------------------------------------    0             0x0             eCos kernel exception handler, architecture: MIPSEL, exception vector table base address: 0x80000200
    128           0x80            eCos kernel exception handler, architecture: MIPSEL, exception vector table base address: 0x80000200
    5475588       0x538D04        Unix path: /home/remus/svn/ivs/IVSPL5-ZyXEL_New/src_0603/build/../build/obj/ecos/install/include/cyg/libc/stdlib/atox.inl
    5475653       0x538D45        eCos RTOS string reference: "ecos/install/include/cyg/libc/stdlib/atox.inl"
    # ...
    5945083       0x5AB6FB        eCos RTOS string reference: "ecos_driver_vid_to_if_index!"
    5949577       0x5AC889        eCos RTOS string reference: "ecos_driver_inject vid=%u, length=%u"
    # ... 
    6525239       0x639137        eCos RTOS string reference: "eCos/packages/devs/serial/generic/16x5x/current/src/ser_16x5x.c"
    # ...
    

尝试使用`IDA`工具直接加载该文件，设置架构为`mipsel`、加载地址为`0x80000200`后，如下。可以看到没有识别出一个函数，整个`segment`都是`Unexplored`状态，估计是因为加载地址不正确，因此需要想办法获取固件的加载地址。

> 一般，判断加载地址是否正确的方式包括：1) 成功识别出的函数个数；2）正确的字符串交叉引用个数。
>
> 后来发现即使加载基址正确，初始状态也是这样，需要在对应的地方手动`Make Code`才行 。。。可能还需要有合适的loader 进行初始化 ???
> 相比而言，`Ghidra`就可以自动进行分析。

![](https://p4.ssl.qhimg.com/t014703af89e8c548a7.png)

根据相关信息进行查找，文章[ecos vector.S
分析II](https://blog.csdn.net/qq_20405005/article/details/77971929)中简单介绍了`eCos`异常中断的初始化及处理等知识，如下，尝试其中提到的地址`0x80000180`似乎不对。

    
    
    # mips cpu 产生exception/interrupt后，cpu会跳到特定的几个地址上,
    # BEV=0时，一般的在0x80000180,当然还有些其他地址，详细的要去看mips书籍
    # 这里有这样的代码
    FUNC_START(other_vector)
        mfc0    k0,cause            # K0 = exception cause
        nop
        andi    k0,k0,0x7F            # isolate exception code
        la    k1,hal_vsr_table        # address of VSR table
        add    k1,k1,k0                # offset of VSR entry
        lw    k1,0(k1)                # k1 = pointer to VSR
        jr    k1                    # go there
        nop                            # (delay slot)
    FUNC_END(other_vector)
    

在`MLT
linker`文件[mips_tx49.ld](https://git.falcom.de/pub/ecos/-/blob/5ae20c384f92067161fe47cd1bed577d4e5b1a2b/packages/hal/mips/tx49/current/src/mips_tx49.ld)中提到了`hal_vsr_table`和`hal_virtual_vector_table`等地址，搜索`SECTION_rom_vectors
(rom`，尝试找到的一些地址后仍然不对。

    
    
    // MLT linker script for MIPS TX49
    
    /* this version for ROM startup */
    #define SECTION_rom_vectors(_region_, _vma_, _lma_) \
        .rom_vectors _vma_ : _lma_ \
        { KEEP (*(.reset_vector)) \
        . = ALIGN(0x200); KEEP (*(.utlb_vector)) \
        . = ALIGN(0x100); . = . + 4; \
        . = ALIGN(0x80); KEEP(*(.other_vector)) \
        . = ALIGN(0x100); KEEP(*(.debug_vector)) } \
        > _region_
    
    #endif /* ROM startup version of ROM vectors */
    
    // 0-0x200 reserved for vectors
    hal_vsr_table = 0x80000200;
    hal_virtual_vector_table = 0x80000300;
    
    // search results
    // packages/hal/mips/idt79s334a/current/include/pkgconf/mlt_mips_idt32334_refidt334_rom.ldi
    SECTION_rom_vectors (rom, 0x80200000, LMA_EQ_VMA)
    // ...
    

## bare-metal firmware加载地址分析

一般来说，针对`bare-metal
firmware`，为了确定其加载地址，可以通过查询对应的芯片文档或`SDK`手册等资料，得到内存空间的映射分布。示例如下，其中`Flash
memory`的范围为`0x08000000~0x0801FFFF`。

![](https://p0.ssl.qhimg.com/t01eeb720d4863c3652.png)

> 来源: [STM32F103C8 memory
> mapping](https://www.st.com/resource/en/datasheet/stm32f103c8.pdf)

此外，对于一些`ARM`架构的`bare-metal firmware`，还可以通过中断向量表来推测加载地址。中断向量表中的前2项内容分别为`Initial
SP value`和`Reset`，其中`Reset`为`reset
routine`的地址，设备上电/重置时将会从这里开始执行，根据该地址推测可能的加载地址。

> In the used cores, an ARM Cortex-M3, the boot process is build around the
> reset exception. At device boot or reboot the core assumes the vector table
> at `0x0000.0000`. The vector table contains exception routines and the
> initial value of the stack pointer. On power-on now the microcontroller
> first loads the initial stack pointer from `0x0000.0000` and then address of
> the reset vector (`0x0000.0004`) into the program counter register (`R15`).
> The execution continues at this address. ([来源](https://blog.3or.de/starting-> embedded-reverse-engineering-freertos-libopencm3-on-stm32f103c8t6.html))

![](https://p0.ssl.qhimg.com/t019d07724ee131cb74.png)

> 来源：[ARM Cortex-M3 Vector
> table](https://developer.arm.com/documentation/dui0552/a/the-> cortex-m3-processor/exception-model/vector-table)

在没有对应的芯片文档或`SDK`手册等资料时，可以尝试从固件本身出发，通过分析固件中的一些特征来推测可能的加载地址。例如，[Magpie](https://www.anquanke.com/post/id/198276)通过识别`ARM`固件中的函数入口表，然后基于函数入口表中的地址去推测可能的加载基址；[limkopi.me](https://limkopi.me/analysing-sj4000s-firmware/)通过查找指令中引用的固定地址，成功试出了该`eCos`固件的加载地址。上述方法的本质都是查找固件中存在的固定地址(绝对地址)，因为即使加载地址不正确，引用的这些固定地址也不会改变。下面尝试通过同样的方法来对`Zyxel`
`RGS200-12P`设备的固件进行分析。

> 由于该固件是`MIPS`架构的，而`Magpie`的工具是针对`ARM`架构的，因此并未直接尝试该工具。

## eCos固件加载地址分析

前面使用`binwalk`工具进行分析时，其输出结果中包含`"eCos kernel exception handler, architecture:
MIPSEL, exception vector table base address:
0x80000200"`。通过查看`binwalk`中`ecos`对应的[magic](https://github.com/ReFirmLabs/binwalk/blob/master/src/binwalk/magic/ecos)，如下，表明`binwalk`在该固件中匹配到一些模式。

    
    
    # eCos kernel exception handlers
    #
    # mfc0    $k0, Cause       # Cause of last exception
    # nop                      # Some versions of eCos omit the nop
    # andi    $k0, 0x7F
    # li      $k1, 0xXXXXXXXX
    # add     $k1, $k0
    # lw      $k1, 0($k1)
    # jr      $k1
    # nop
    0       string      \x00\x68\x1A\x40\x00\x00\x00\x00\x7F\x00\x5A\x33    eCos kernel exception handler, architecture: MIPSEL,
    >14     leshort     !0x3C1B                                             {invalid}
    >18     leshort     !0x277B                                             {invalid}
    >12     uleshort    x                                                   exception vector table base address: 0x%.4X
    >16     uleshort    x                                                   \b%.4X
    

使用`IDA`工具加载该文件，设置架构为`mipsl`、加载地址为`0x80000000`，在最开始处`Make Code`后，看到了熟悉的`eCos
kernel exception
handler`，同时其中包含一个固定地址为`0x80000200`。由于该固件文件有点大(约`10M`)，仅靠单个地址去猜测加载地址比较费事：(1)
一次完整的分析比较耗时(大概几分钟)，猜测多个地址的话需要分析好几次；(2)
手动去确认识别出的函数以及字符串交叉引用是否正确也比较麻烦(可能包含成百上千个函数及字符串交叉引用)。因此还需要查找更多的固定地址以及更有规律的地址，来确定加载地址的区间。

> 由于对`eCos`系统不了解，刚开始以为加载地址可能在`0x80000000~0x80000200`之间 :(，后来发现不对。
    
    
    ROM:80000000  # Segment type: Pure code
    ROM:80000000                 .text # ROM
    ROM:80000000                 mfc0    $k0, Cause       # Cause of last exception
    ROM:80000004                 nop
    ROM:80000008                 andi    $k0, 0x7F
    ROM:8000000C                 li      $k1, unk_80000200
    ROM:80000014                 add     $k1, $k0
    ROM:80000018                 lw      $k1, 0($k1)
    ROM:8000001C                 jr      $k1
    ROM:80000020                 nop
    

在`Hex View`窗口中快速浏览固件时，发现了一些有规律的内容，如下。其中，存在一些连续的内容(以4字节为单位)，其最后2个字节均相同，对应到`IDA
View`窗口中，分别为指向代码片段的地址和指向字符串的地址。由于此时加载地址不正确，故看到的字符串引用比较奇怪。

> 当然，文件中还存在一些其他的规律，比如以8字节为单位，以16字节为单位等等。

![](https://p1.ssl.qhimg.com/t01026be75638908cdf.png)

根据上述规律可以从固件文件中提取出所有的固定地址，一方面可以缩小加载地址所在的范围，另一方面可以利用这些固定地址去判断尝试的加载地址是否正确。[Magpie](https://www.anquanke.com/post/id/198276)根据代码片段地址引用处是否是函数的序言指令来判断加载地址是否正确，由于函数的序言指令需要考虑多种情况，这里采用另一种简单的方式：根据字符串交叉引用是否正确来进行判断。

针对该`eCos`固件，确定其加载地址的方法如下：

(1)
以4字节为单位，判断邻近内容的低/高2字节是否相同，提取固件中所有符合规律的固定地址。考虑到大小端差异，在实际比较时以2字节为单位，判断相邻浅蓝色框(或红色框)内的内容是否相同。

![](https://p2.ssl.qhimg.com/t01433cb541e444d5a2.png)

(2)
提取出所有的固定地址后，先筛掉不合法的地址，然后对剩下的地址进行排序，排序后的结果中的第一个地址为加载地址的上限。同时，排序后的结果中前半部分为指向代码片段的地址，后半部分为指向字符串的地址。从中选择一个地址，将指向字符串的地址和指向代码的地址分开。之后，随机从字符串地址列表中选取一定数量的地址，作为后续判断的依据。

> 模糊的正确，只需要保证分到字符串地址列表中的地址均正确即可，因此可以尽量从列表后半部分取，至于是否有字符串引用地址分到了代码片段引用地址列表中不重要。

(3)
在确定的加载地址范围内逐步进行尝试，同时针对每个尝试的加载地址，判断之前选取的每个字符串引用地址指向的字符串是否”正确”，并记录下正确的个数。对应字符串地址”命中”最多的那个加载地址，很有可能就是正确的加载地址。

>
> 判断字符串引用地址是否正确，可根据该地址是否指向完整字符串的开头判断，即对应地址处的前一个字节是否为`'\x00'`。当然，也存在一些字符串引用地址指向某个完整字符串的中间(“字符串复用”)，但大部分的地址还是指向完整字符串的开头。

根据上述思路，推测出了该`eCos`固件的加载地址为`0x80040000`。通过分析部分函数逻辑和字符串交叉引用，验证该加载地址是正确的。另外，采用该方法对另外几个`eCos`固件(包括其他厂商的)进行分析，也可以得出正确的加载地址，说明该方法是可行的。当然，该方法还存在可以改进或优化的地方，不过目前暂时够用了。

    
    
    $ python find_ecos_load_addr.py
    # ...
    [+] Top 10 string hit count ...
     ---> load_base: 0x80040000, str_hit_count: 19
     ---> load_base: 0x80019a30, str_hit_count: 11
     ---> load_base: 0x800225a0, str_hit_count: 11
     ---> load_base: 0x80041cd0, str_hit_count: 11
     ---> load_base: 0x800442d0, str_hit_count: 11
     ---> load_base: 0x80019680, str_hit_count: 10
     ---> load_base: 0x80019940, str_hit_count: 10
     ---> load_base: 0x80019af0, str_hit_count: 10
     ---> load_base: 0x80026090, str_hit_count: 10
     ---> load_base: 0x80008b90, str_hit_count: 9
    [+] Possible load_base: 0x80040000
    

## binwalk magic添加

设置正确的加载地址后，在对文件进行分析时，在文件头部发现与`VSR table`初始化相关的代码，如下。

    
    
    .text:80040118                 li      $gp, 0x809A1140
    .text:80040120                 li      $a0, 0x8099B7D0
    .text:80040128                 move    $sp, $a0
    .text:8004012C                 li      $v0, loc_80040224
    .text:80040134                 li      $v1, 0x80000200
    .text:8004013C                 sw      $v0, 4($v1)
    .text:80040140                 sw      $v0, 8($v1)
    .text:80040144                 sw      $v0, 0xC($v1)
    .text:80040148                 sw      $v0, 0x10($v1)
    .text:8004014C                 sw      $v0, 0x14($v1)
    .text:80040150                 sw      $v0, 0x18($v1)
    .text:80040154                 sw      $v0, 0x1C($v1)
    .text:80040158                 sw      $v0, 0x20($v1)
    .text:8004015C                 sw      $v0, 0x24($v1)
    # ...
    

参考文章[ecos vector.S
分析II](https://blog.csdn.net/qq_20405005/article/details/77971929)中对`eCos`异常中断的初始化及处理的介绍，对照上述代码可知，`0x80000200`为`hal_vsr_table`的地址，而`0x80040224`则为`__default_exception_vsr`的地址。根据前面推测出的加载地址`0x80040000`，猜测该地址与`__default_exception_vsr`有关，即根据`__default_exception_vsr`的地址，考虑地址对齐，可以推测出对应的加载地址。

    
    
    # mips cpu 产生exception/interrupt后，cpu 会跳到特定的几个地址上,
    # BEV=0时，一般的在0x80000180,当然还有些其他地址，详细的要去看mips书籍
    # 这里有这样的代码
    FUNC_START(other_vector)
        mfc0    k0,cause            # K0 = exception cause
        nop
        andi    k0,k0,0x7F            # isolate exception code
        la    k1,hal_vsr_table        # address of VSR table
        add    k1,k1,k0                # offset of VSR entry
        lw    k1,0(k1)                # k1 = pointer to VSR
        jr    k1                    # go there
        nop                            # (delay slot)
    FUNC_END(other_vector)
    
    # 从cause 里取出exception ExcCode,然后到hal_vsr_table 取相应的处理vsr, hal_vsr_table的内容是由 hal_mon_init 填充的
    
        .macro  hal_mon_init
        la      a0,__default_interrupt_vsr
        la      a1,__default_exception_vsr    # <===
        la      a3,hal_vsr_table              # <===
        sw      a0,0(a3)
        sw      a1,1*4(a3)
        sw      a1,2*4(a3)
        sw      a1,3*4(a3)
        sw      a1,4*4(a3)
        sw      a1,5*4(a3)
        sw      a1,6*4(a3)
        sw      a1,7*4(a3)
        sw      a1,8*4(a3)
        # ...
        .endm
    # 这里填充的是__default_interrupt_vsr和__default_exception_vsr,
    # ExcCode=0是interrupt,其他的都是exception,就是说产生interrupt会调用__default_interrupt_vsr，产生exception会调用__default_exception_vsr。
    

根据上述代码特征，通过在`binwalk`中添加对应的`eCos
magic`，再次对文件进行分析时即可匹配对应的代码模式，输出`__default_exception_vsr`地址信息，如下，根据该信息即可推测出对应的加载地址。

> 利用`binwalk`对另外几个`eCos`固件(包括其他厂商的)进行分析，也可以输出相关的信息，推测出对应的加载地址。
    
    
    $ binwalk RGS200-12P.bin 
    
    DECIMAL       HEXADECIMAL     DESCRIPTION
    --------------------------------------------------------------------------------    0             0x0             eCos kernel exception handler, architecture: MIPSEL, exception vector table base address: 0x80000200
    128           0x80            eCos kernel exception handler, architecture: MIPSEL, exception vector table base address: 0x80000200
    300           0x12C           eCos vector table initialization handler, architecture: MIPSEL, default exception vector table base address: 0x80040224, hal_vsr_table base address: 0x80000200
    # ...
    

## 其他

###  自动分析

使用`IDA`加载该固件并设置正确的架构、加载地址等参数后，默认情况下`IDA`不会自动进行分析。相比而言，`Ghidra`则可以自动进行分析，成功识别出函数并建立字符串的交叉引用。因此，一种方式是对照`Ghidra`分析的结果，在`IDA`中进行部分手动`Make
Code` (当然，也可以直接使用`Ghidra` … )；另一种方式是写一个简单的`eCos loader`插件，然后`IDA`就可以自动进行分析了。

###  函数名恢复

该单一大文件中不存在导入表及导出表，故无法区分哪些是常见的系统函数，比如`memcpy()`,
`strcpy()`等。但也有其好处，在代码中存在很多函数名/日志等信息，根据这些信息可以很容易地对函数名进行恢复。

![](https://p1.ssl.qhimg.com/t01327ae197e7a32b92.png)

###  函数调用约定

对于`MIPS32`架构的程序，常见的函数调用约定遵循`O32
ABI`，即`$a0-$a3`寄存器用于函数参数传递，多余的参数通过栈进行传递，返回值保存在`$v0-$v1`寄存器中。而该`eCos`固件则遵循[N32
ABI](https://en.wikipedia.org/wiki/MIPS_architecture#Calling_conventions)，最大的不同在于`$a0-$a7`寄存器用于函数参数传递(对应`O32
ABI`中的`$a0-$a3`, `$t0-$t3`)。

![](https://p5.ssl.qhimg.com/t01b1f2274985007430.png)

`IDA`中支持更改处理器选项中的`ABI`模式，但仅修改该参数似乎不起作用。默认情况下`"Compiler"`是`"Unknown"`，将其修改为`"GNU
C++"`，同时修改`ABI`为`n32`，之后反编译代码中函数参数的显示就正常了。

![](https://p1.ssl.qhimg.com/t0162ce5b40b51b2b90.png)

## 小结

本文通过对`Zyxel`某设备`eCos`固件进行分析，寻找固件中引用的固定地址，给出了推测固件加载地址的思路，根据该思路成功得到了固件的加载地址。同时，通过对文件进行分析，在文件中发现了与`VSR
table`初始化相关的代码，根据该代码可以反推出固件的加载地址，并在`binwalk`中添加对应的`eCos magic`来自动匹配该模式。

## 相关链接

  * [ecos vector.S 分析II: exception/interrupt](https://blog.csdn.net/qq_20405005/article/details/77971929)
  * [Starting Embedded Reverse Engineering: FreeRTOS, libopencm3 on STM32F103C8T6](https://blog.3or.de/starting-embedded-reverse-engineering-freertos-libopencm3-on-stm32f103c8t6.html)
  * [Magpie: ARM固件基址定位工具开发](https://www.anquanke.com/post/id/198276)
  * [limkopi.me: Analysing SJ4000’s firmware](https://limkopi.me/analysing-sj4000s-firmware/)
  * [MIPS calling conventions](https://en.wikipedia.org/wiki/MIPS_architecture#Calling_conventions)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360信安-涅槃团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/233361](/post/id/233361)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Zyxel](/tag/Zyxel)

 **+1** __7赞

 __收藏

![](https://p3.ssl.qhimg.com/t018799f60cb7058aec.png) 360信安-涅槃团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

