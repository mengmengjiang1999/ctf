**Sniffle是一个基于使用TI CC1352/CC26x2硬件的蓝牙5和4.x LE嗅探器。**

Sniffle具有许多有用的功能，包括：

> 支持BT5/4.2扩展长度广播和数据包
>
> 支持BT5 Channel选择算法#1 和 #2
>
> 支持所有BT5 PHY模式（常规1M，2M和编码模式）
>
> 支持仅嗅探广播和忽略连接
>
> 支持channel map，连接参数和PHY更改操作
>
> 支持通过MAC地址和RSSI进行广播过滤
>
> 支持BT5扩展广播（非定期）
>
> 支持使用单个嗅探器在所有三个主广播信道上从目标MAC捕获广播。这使得连接检测的可靠性比大多数仅嗅探一个广播信道的嗅探器要高出近三倍。
>
> 用Python编写的易于扩展的主机端软件
>
> 与Ubertooth兼容的PCAP导出

##  必要条件

> TI CC26x2R Launchpad 板：<https://www.ti.com/tool/LAUNCHXL-CC26X2R1>
>
> 或TI CC1352R Launchpad 板：<https://www.ti.com/tool/LAUNCHXL-CC1352R1>
>
> GNU ARM嵌入式工具链：<https://developer.arm.com/open-source/gnu-toolchain/gnu-> rm/downloads>
>
> TI CC26x2 SDK 3.20.00.68：<https://www.ti.com/tool/download/SIMPLELINK-> CC13X2-26X2-SDK>

TI DSLite 编程软件：请参见下文

Python 3.5+ 并安装了 PySerial

**注意：** 通过少量适当的修改编译Sniffle应该是可以让它运行在CC1352P Launchpad板上的，但具体可行性如何我并未尝试。

##  安装 GCC

通过各种Linux发行版的软件包管理器提供的arm-none-eabi-gcc，通常都会缺少一些头文件或需要对连接器配置进行一些更改。为了尽量减少麻烦，我建议使用上面链接提供的ARM GCC。你可以下载并提取预构建的可执行文件。

##  安装 TI SDK

TI
SDK是作为一个可执行二进制文件提供的，一旦你接受了许可协议，该二进制文件就会提取一堆源代码。在Linux和Mac上，默认安装目录为~/ti/，我建议在此处使用默认设置，实践证明它工作的非常的好。

提取SDK之后，你将需要编辑一个makefile以匹配你的构建环境。在~/ti/simplelink_cc13x2_26x2_sdk_3_20_00_68（或安装SDK的任何位置）中，都有一个名为imports.mak的生成文件。构建Sniffle只需要在这里设置GCC和XDC的路径。请参阅以下diff示例，并根据安装的位置进行调整。

    
    
    diff --git a/imports.mak b/imports.mak
    index 270196a5..1918effd 100644
    --- a/imports.mak
    +++ b/imports.mak
    @@ -18,13 +18,13 @@
     # will build using each non-empty *_ARMCOMPILER cgtool.
     #
     
    -XDC_INSTALL_DIR        ?= /home/username/ti/xdctools_3_51_03_28_core
    +XDC_INSTALL_DIR        ?= $(HOME)/ti/xdctools_3_51_03_28_core
     SYSCONFIG_TOOL         ?= /home/username/ti/ccs910/ccs/utils/sysconfig/sysconfig_cli.sh
     
     
     CCS_ARMCOMPILER        ?= /home/username/ti/ccs910/ccs/tools/compiler/ti-cgt-arm_18.12.2.LTS
     CLANG_ARMCOMPILER      ?= /path/to/clang/compiler
    -GCC_ARMCOMPILER        ?= /home/username/ti/ccs910/ccs/tools/compiler/gcc-arm-none-eabi-7-2017-q4-major
    +GCC_ARMCOMPILER        ?= $(HOME)/arm_tools/gcc-arm-none-eabi-8-2018-q4-major
     
     # The IAR compiler is not supported on Linux
     # IAR_ARMCOMPILER      ?=

##  获取 DSLite

DSLite是TI用于XDS110调试器的命令行编程和调试服务器的工具。CC26xx和CC13xx
Launchpad板均包含了XDS110调试器。不幸的是，TI没有提供独立的命令行DSLite下载。获取DSLite的最简单方法是从TI安装UniFlash。它适用于Linux，Mac和Windows。相对于UniFlash安装目录，DSLite可执行文件将位于deskdb/content/TICloudAgent/linux/ccs_base/DebugServer/bin/DSLite中。在Linux上，默认的UniFlash安装目录位于~/ti/中。

同时，你应该将DSLite可执行目录添加到$PATH中。

##  构建和安装

一旦GCC，DSLite和SDK安装并开始运行，构建Sniffle就变得非常轻松了。只需转到fw目录并运行make。如果未将SDK安装到默认目录，则可能需要在makefile中编辑SIMPLELINK_SDK_INSTALL_DIR。

要使用DSLite在（插入的）CC26x2 Launchpad上安装Sniffle，请在fw目录中运行make load。你也可以使用UniFlash
GUI flash已编译的sniffle.out二进制文件。

如果要在CC1352R启动板上而不是CC26x2R上进行构建或安装，则必须指定PLATFORM=CC1352R1F3作为make的参数，或者在调用make之前将其定义为环境变量。在CC13x2和CC26x2之间切换前，请确保已执行了make
clean命令。

##  使用

    
    
    [skhan@serpent python_cli]$ ./sniff_receiver.py --help
    usage: sniff_receiver.py [-h] [-s SERPORT] [-c {37,38,39}] [-p] [-r RSSI]
                             [-m MAC] [-a] [-e] [-H] [-l] [-o OUTPUT]
    Host-side receiver for Sniffle BLE5 sniffer
    optional arguments:
      -h, --help            show this help message and exit
      -s SERPORT, --serport SERPORT
                            Sniffer serial port name
      -c {37,38,39}, --advchan {37,38,39}
                            Advertising channel to listen on
      -p, --pause           Pause sniffer after disconnect
      -r RSSI, --rssi RSSI  Filter packets by minimum RSSI
      -m MAC, --mac MAC     Filter packets by advertiser MAC
      -a, --advonly         Sniff only advertisements, don't follow connections
      -e, --extadv          Capture BT5 extended (auxiliary) advertising
      -H, --hop             Hop primary advertising channels in extended mode
      -l, --longrange       Use long range (coded) PHY for primary advertising
      -o OUTPUT, --output OUTPUT
                            PCAP output file name

Launchpad板上的XDS110调试器将创建两个串行端口。在Linux上，它们通常会被命名为ttyACM0和ttyACM1。创建的两个串行端口中的第一个用于与Sniffle通信。默认情况下，Python
CLI使用/dev/ttyACM0进行通信，但是如果你未在Linux上运行或连接其他USB CDC-ACM设备，则可能需要使用-s命令行选项覆盖此选项。

对于-r（RSSI过滤器）选项，如果嗅探器非常接近或几乎接触到了传输设备，则-40值通常会很好地起作用。RSSI过滤器对于在繁忙的RF环境中忽略无关的广播非常有用。RSSI过滤器仅在捕获广播时才处于活动状态，因为你总是希望捕获正在跟踪的连接数据通信流量。MAC过滤处于活动状态时，你可能不想使用RSSI过滤器，因为当RSSI过低时，你可能会丢失感兴趣的MAC地址的广播。

想要与广播一起跳转并进行可靠的连接嗅探，需要使用-m选项设置MAC过滤器。你应该指定外围设备而不是中央设备的MAC地址。想要确定要嗅探的MAC地址，你可以将嗅探器放置在目标附近，然后运行带有RSSI过滤的嗅探器。这将向你显示来自目标设备的广播，包括其MAC地址。需要注意的是，许多BLE设备使用随机MAC地址进行广播，而非标签上写的“真实”固定MAC地址。

为方便起见，MAC过滤器有一个特殊的模式，它使用-m top调用脚本，而不是使用-m
MAC地址调用脚本。在这种模式下，嗅探器将锁定通过RSSI过滤器的第一个广播客户MAC地址。因此-m
top模式应始终与RSSI过滤器一起使用，以避免锁定到虚假的MAC地址。嗅探器锁定MAC地址后，嗅探接收器脚本将自动禁用RSSI过滤器（使用-e选项时除外）。

要在Bluetooth 5扩展广告中启用以下辅助指针，请启用-e选项。为了提高扩展广播捕获的性能和可靠性，即使设置了MAC过滤器，此选项也可以在主广播信道上禁用跳频。如果不确定是通过传统广播还是扩展广播建立连接，则可以将-H标志与-e结合使用，以对传统广播执行主信道跳频，并计划监听扩展广播辅助数据包。与-e和-H组合使用时，与仅在主（传统）或次要（扩展）广播信道上跳频相比，连接检测的可靠性可能会降低。

要在主广播信道上监听远程PHY，请指定-l选项。注意，由于所有远程广播都使用了BT5扩展机制，因此在远程模式下不支持在主广播信道之间进行跳频。在扩展机制下，所有三个主信道上的辅助指针都将指向相同的辅助数据包，因此在主信道之间跳频是不必要的。

如果由于某些原因嗅探器固件锁定，并且即使禁用了过滤器也拒绝捕获任何流量，那么你应该重置嗅探器MCU。在Launchpad板上，重置按钮位于micro
USB端口旁。

##  使用示例

嗅探信道38上的所有广播，忽略RSSI < -50，即使看到CONNECT_REQ仍停留在广播信道上。

    
    
    ./sniff_receiver.py -c 38 -r -50 -a

从MAC 12:34:56:78:9A:BC监听广告，即使看到CONNECT_REQ仍停留在广播信道上，将广播保存到data1.pcap中。

    
    
    ./sniff_receiver.py -m 12:34:56:78:9A:BC -a -o data1.pcap

嗅探广播和RSSI> = -40看到的第一个MAC地址的连接。一旦MAC地址被锁定，RSSI过滤器将自动禁用。将捕获的数据保存到data2.pcap中。

    
    
    ./sniff_receiver.py -m top -r -40 -o data2.pcap

嗅探来自附近（RSSI> = -55）设备的BT5扩展广播和连接。

    
    
    ./sniff_receiver.py -r -55 -e

从具有指定MAC地址的设备嗅探传统和扩展的广播和连接。将捕获的数据保存到data3.pcap中。

    
    
    ./sniff_receiver.py -eH -m 12:34:56:78:9A:BC -o data3.pcap

使用38信道上的远距离主PHY嗅探扩展广播和连接。

    
    
    ./sniff_receiver.py -le -c 38

***参考来源：[GitHub](https://github.com/nccgroup/Sniffle)，FB小编secist编译，转载请注明来自FreeBuf.COM**

  

  

