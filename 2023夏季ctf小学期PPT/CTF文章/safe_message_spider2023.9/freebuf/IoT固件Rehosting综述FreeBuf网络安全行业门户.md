最近抽空浏览了一些IoT固件安全论文，试用了部分工具，这里作简单总结。文章主要 **从论文出发** ，对 **Rehosting** ( **托管**
)囊括的不一定全面，希望可以为小伙伴抛砖引玉。本文是笔者正在总结的《物联网固件安全研究手册》部分内容，全册完成后会在 **Github** 公布。

 **Rehosting** 是固件 **动态分析** 的重要手段，本文将澄清 **Rehosting山寨版定义** ，重点阐述
**Rehosting的一些方式** ，文末简单提及固件 **静态分析， **并给出** 参考论文**列表。

## 0x00 Rehosting定义

 **Rehosting** 一般译为 **托管** ，但可能与 **机房机器托管** 的意思混淆，而 **Re+Host**
较为直观，即通过将所需的固件模块在新的宿主(host)上运行，已达到成规模的低成本动态分析和安全研究目的。下文将直接使用Rehosting。

 **[1]** 给出的定义如下:

 **Definition 1**.Virtual Environment (VE): A software environment in which
code can be executed transparently.

 **Definition 2**.Hardware Emulation System (HES): A VE designed to accurately
recreate the features of one or more selected pieces of hardware. Commonly
called an emulator.

 **Definition 3**.Rehosted Embedded System (RES): A combination of a firmware
image and **VE** designed to sufficiently recreate the firmware’s hardware
dependencies such that analyses produce results representative of the firmware
running on its original hardware.

 **Definition 4**. **Rehosting** : The process of building an **RES** for a
given embedded system to enable a specified analysis task. May include
modifications to the firmware.

与 **Rehosting** 类似概念有 **固件移植** 和 **固件模拟(Emulation)** ，笔者认为区别在于， **固件移植**
指将PC软件交叉编译安装至开发板，Rehosting往往相反； **而与**
固件模拟相比，Rehosting一般仅将需要的功能模块提取出，必要时适当修改，以用于 **Fuzzing和安全性研究** 。

当然，对此见仁见智，这并非阐述重点，本文提及的论文和工具侧重功能模拟和动态安全测试，在概念上不会深究界限区别。

## 0x01 Rehosting方式

 **Rehosting** 方式最直观的与固件类型相关，IOT固件粗略可分两种，一种是有明确 **文件系统** 目录的，一般基于 **Linux** ，
**FreeBSD** 等开源系统/内核；一种是没有的文件系统的 **RTOS(Real-time operating system)**
，比如Vxworks，FreeRTOS等。基于Linux的固件Rehosting相对简单，而RTOS模块较难分离，笔者收集的论文大部分都是针对RTOS展开。

 **模拟运行**
是二进制分析的重要手段，常用的有QEMU、Unicon，包括后起之秀Qiling等等，这些框架或模拟系统，或模拟执行指令，代码也都有交集，本文重点并不在此，不会对基础模拟器作过多讨论。

### 基于Linux的固件

  *  **Firmadyne [2]**

 **Firmadyne框架基于QEMU，旨在完成整个固件系统的运行。**

一些Rehosting&Fuzzing的框架会在其基础上二次开发，Firmadyne模块如下图所示：

![](https://image.3001.net/images/20220609/1654776873_62a1e4292b59f6acfc0ec.jpg!small)

其运行流程是：

1、通过网络途径获取固件(ARM/MIPS)，并对固件解包；

2、利用定制动态链接库完成库函数劫持以完成NVRAM设备调用；

3、利用定制内核完成系统启动、网络探测、虚拟硬件和网络构建；

4、调用QEMU仿真系统。

对固件解包模拟的比较熟悉的小伙伴通过以上描述就会 **大概率放弃该工具** ，因为该流程存在大量不确定因素，成规模使用的 **成功利率会很低**
，而测试结果也正是如此。在Firmadyne获取的23035个固件中，8617个可解包；解包成功后有8591个可启动系统；启动系统后2797个可配置网络；最后只有1971个可以正常访问网络。也就是仅有
**22.9%** 的固件完成模拟并进行测试。

 **Firmadyne** 的使用方法这里略过，[
**Github**](https://github.com/firmadyne/firmadyne)上教程也很详细。

  *  **FirmAE [3]**

 **FirmAE目标是创造一个可以供用户动态调试分析的环境，而不是复现和硬件一模一样的环境,，其卖点是大规模(Large-Scale)。**

论文开头就直指“友商”Firmadyne，提出其模拟成功率低等问题，其将原本Firmadyne的成功率16.28%提高到79.36%，其底层还是使用了
**QEMU** 。FirmAE从固件的启动、网络、NVRAM、内核和其它五个方面，总结了导致固件仿真失败的原因及通用解决方法，并集成 **check**
、 **run** 、 **analyze** 和 **debug** 四种模式。check
模式会对固件进行各项仿真检测，并保存相关的日志信息记录在缓存文件中。run模式是根据check模式构建的各种处理信息进行仿真。

![](https://image.3001.net/images/20220609/1654777051_62a1e4db79a606523b263.jpg!small)

在漏洞检测方面，FirmAE根据固件的文件系统和内核日志来推断 **Web** 服务状态，其发现了23个设备的12个0DAY。

 **FirmAE** 的使用方法网上不乏[
**教程**](https://www.52pojie.cn/thread-1572565-1-1.html)，也可以参考[
**Github**](https://github.com/pr0v3rbs/FirmAE)。

  *  **FirmAFL [4]**

 **FirmAFL使用并改进了Firmdyne模拟方式，并利用AFL对IoT固件实施高通量灰盒Fuzzing。**

FirmAFL的贡献在于：

1、针对全系统仿真(高通用性、低效率)和用户模式仿真(低通用性、高效率)的矛盾特点，提出了 **增强过程仿真** 的新技术；

2、设计并实现了第一个基于代码覆盖率的灰盒fuzzer—FirmAFL，支持mipsel、mipseb和armel三种CPU架构，涵盖Firmadyne数据库中90.2%的固件。

![](https://image.3001.net/images/20220609/1654777136_62a1e530c43242e8b57e8.jpg!small)

FirmAFL的使用可参考Github，以下简单梳理(详见参考链接(5))：

    
    
    # 安装依赖
    sudo apt-get install zlib1g-dev libglib2.0-dev automake libtool binwalk
    sudo apt-get install python-lzma
    sudo -H pip install git+https://github.com/ahupp/python-magic
    sudo -H pip install git+https://github.com/sviehb/jefferson
    sudo pip3 install python3-magic
    
    # 编译用户模式
    cd ./FirmAFL/user_mode/
    sed -i '40s/static //' util/memfd.c
    ./configure --target-list=mipsel-linux-user,mips-linux-user,arm-linux-user --static --disable-werror
    make
    
    # 编译系统模式
    cd ../qemu_mode/DECAF_qemu_2.10/
    sed -i '40s/static //' util/memfd.c
    ./configure --target-list=mipsel-softmmu,mips-softmmu,arm-softmmu --disable-werror
    make
    
    # 安装Firmadyne并设置数据库
    cd ../../
    sudo apt-get install busybox-static fakeroot git dmsetup kpartx netcat-openbsd nmap python-psycopg2 python3-psycopg2 snmp uml-utilities util-linux vlan
    git clone --recursive <https://github.com/firmadyne/firmadyne.git>
    cd ../FirmAFL/firmadyne
    sudo apt-get install postgresql
    sudo apt-get install libpq-dev
    dropdb -U firmadyne -h 127.0.0.1 firmware
    sudo -u postgres createuser -P firmadyne
    sudo -u postgres createdb -O firmadyne firmware
    cd database
    cp /home/churchkm/Downloads/data.xz ./
    xz -d data.xz
    mv data schema
    chmod +x schema
    sudo -u postgres psql -d firmware < ./schema
    
    # 使用Firmadyne仿真固件
    cd ../
    sudo ./download.sh
    sed -i '4s/#//' firmadyne.config
    cp ../firmadyne_modify/makeImage.sh ./scripts/
    sudo ./sources/extractor/extractor.py -b dlink -sql 127.0.0.1 -np -nk "../firmware/DIR-815_FIRMWARE_1.01.ZIP" images
    sudo ./scripts/getArch.sh ./images/9050.tar.gz
    sudo ./scripts/makeImage.sh 9050
    sudo ./scripts/inferNetwork.sh 9050
    
    # 使用FirmAFL进行Fuzzing
    cd ../
    python3 FirmAFL_setup.py 9050 mipsel
    cp ./FirmAFL_config/9050/run.sh ./image_9050/  #即用FirmAFL_config中的run.sh替换image_9050中的run.sh
    cd image_9050
    sudo ./run.sh
    # 固件启动后，新终端下执行
    python3 test.py
    sudo user.sh

![](https://image.3001.net/images/20220609/1654777187_62a1e5634824bceaf8cf6.jpg!small)

  *  **FirmFuzz [5]**

**FirmFuzz通过监控固件运行所生成的日志以检测漏洞，侧重挖掘命令注入、缓冲区溢出和空指针引用等。FirmFuzz在模拟层面基于QEMU，支持MIPS和ARM架构。**

![](https://image.3001.net/images/20220609/1654777227_62a1e58b2ec71417df53d.png!small)

Firmfuzz论文中将固件可能存在的缺陷归因于三个方面，分别是 **(Linux)内核** 、 **开源软件** 和 **厂商自研软件**
，Firmfuzz重点 **挖掘厂商自研软件漏洞** 。其主要贡献点在于：

1、利用这些设备的web应用界面作为入口，生成语法上合法的输入；

2、将运行监控器嵌入固件的运行时环境中，以允许上下文感知的监控；

3、从 **静态分析中收集信息** 来指导固件模拟和Fuzzing生成。

 **输入检测** 、 **插庄反馈** 和 **静态预分析** 都是Fuzzing的常规操作，只是框架使用的方案各异。

![](https://image.3001.net/images/20220609/1654777309_62a1e5dd022b8db39b16a.png!small)

FirmFuzz的使用侧重Fuzzing，固件解包可单独使用firmadyne extractor或者binwalk，具体可参见
**[Github](https://github.com/HexHive/FirmFuzz)** 教程。

可以看到，在上述提及的Linux-based的框架和工具中，大部分都 **直接或间接基于QEMU** 模拟，以下探讨一些基于RTOS的固件分析框架。

### 基于RTOS固件

  *  **Avatar [6]**

 **Avatar 在物理设备与外部模拟器之间架构一个软件代理Avatar，可以执行模拟器中的固件指令，来对物理设备进行IO操作。**

![](https://image.3001.net/images/20220609/1654777338_62a1e5fae19a928596d54.jpg!small)

Avatar框架比较经典(老牌)的框架之一，其最早将符号执行应用于嵌入式设备固件分析领域，提供了一个仿真器后端组件，用于控制 S2E(Symbolic
Sombolic Exection)，选择性地执行二进制代码。S2E 是一个选择性的符号执行平台，底层基于QEMU之上。S2E
提供了一个功能强大的插件接口，可以通过这些接口拦截仿真事件，通过符号化执行特定代码段可以检测固件中存在的漏洞。

其迭代框架 **Avatar2 [7]**
允许分析人员选择不同的执行环境，共同在相同的执行状态上执行其分析任务，其优势在于可以在多个分析环境中共享不同分析工具得到的分析状态。Avatar2
支持的动态分析工具包括GDB、OpenOCD、QEMU、angr 和 PANDA。

使用方法这里略过，可以参见[ **Avatar Github**](https://github.com/avatarone)和[ **Avatar2
Github**](https://github.com/avatartwo)，值得注意的是Avatar2编译使用较为简单。

  *  **Jetset [8]**

**Jetset来自一篇较新(2021)的论文，其使用符号执行来推断固件期望从目标设备得到什么操作，通过C模拟实现硬件外设模块功能，利用QEMU启动固件。**

Jetset测试了13个不同的固件，包括3个架构、3个应用领域(电网、航空电子设备和消费电子设备)和5个不同的操作系统。同时Fuzzing了一个航空电子设备固件，挖掘出一个提权0Day。

![](https://image.3001.net/images/20220609/1654777376_62a1e6201bd03d24e7c98.jpg!small)

抛开繁琐的细节，Jetset从整体上还是比较好理解的，即 **利用符号执行技术找到固件正常运行的代码流路径，再通过软件模块方式满足**
，最终实现固件的Rehosting。

Jetset安装和使用可参考 **[Github](https://github.com/aerosec/jetset)** ：

    
    
    # 安装 Jetset
    apt-get install git make build-essential zlib1g-dev pkg-config libglib2.0-dev binutils-dev libboost-all-dev autoconf libtool libssl-dev libpixman-1-dev virtualenv xterm
    Once you have these, you can build Jetset:
    
    make clone
    make config_qemu
    make build_qemu
    make virtualenv
    make build_jetset_engine
    
    # 运行 Jetset
    The top-level script that coordinates symbolic execution and generates peripheral devices is in jetset_engine/execution/jetset_server.py.
    
    Usage:
    
    usage: jetset_server.py [-h] [--useFunctionPrologues] [--useSlicer]
                            [--useFinalizer] [--verbose] [--noAutoDetectLoops]
                            [--port PORT] [--soc SOCNAME] [-o OUTFILE]
                            [--cmdfile CMDFILE]
    
    Run Symbolic Execution engine for Jetset
    
    optional arguments:
      -h, --help            show this help message and exit
      --useFunctionPrologues
                            Try to infer the start of functions (for CFG) using
                            architecture specific function prologues
      --useSlicer           Use constraint slicer to improve performance of
                            constraint solving
      --useFinalizer        After making a certain decision n times, finalize and
                            make that always the solution
      --verbose             Print out all log messages and other warnings
      --noAutoDetectLoops   Omit auto loop detection
      --port PORT           Port number to communicate with Qemu (over localhost)
      --soc SOCNAME         Type of soc (console | heat_press | steering_control |
                            robot | gateway | drone | reflow_oven | cnc | stm32f4
                            | rpi | beagle)
      -o OUTFILE            output file
      --cmdfile CMDFILE     path to script to invoke qemu instance. If window
                            doesn't open, make sure that the qemu run script is
                            executable
    

  * **HALucinator [9]**

 **HALucinator利用硬件抽象层(HAL: Hardware Abstract
Layers)作为Rehosting和分析固件的基础，通过提供HAL功能的高级替代品(称为HLE)，使硬件与固件脱钩，并利用QEMU模拟固件。**

![](https://image.3001.net/images/20220609/1654777444_62a1e6644ccec21896c9b.png!small)
其主要贡献在于：

1、提出HAL库模拟技术，可在无需依赖实际硬件的情况下使用QEMU等模拟器仿真二进制固件，

改进了现有的依赖库匹配技术；

2、提出HALucinator仿真系统，可通过抽象处理程序和外设模型库的方式进行交互式仿真和固件Fuzzing；

3、通过对16个固件的模拟，证明了方法的实用性。并通过Fuzzing的方式发现了两个0day。

其缺点在于，HALucinator **仅适用于固件中使用了芯片厂商提供了HAL的那些设备** ，并且 **编译环境要跟固件的编译环境类似**
，仅这两点就大大限制了其可用范围。

HALucinator使用可参见[ **Github**](https://github.com/embedded-sec/halucinator)。

  *  **P²IM [10]**

 **P²IM(Processor-Peripheral Interface
Modeling)针对MCU处理器和外设之间的处理接口，根据处理器设计文档，自动化提供与之等价的接口模型来模拟外部 I/O 操作。**

 **P²IM** 在模拟层面仍然使用 **QEMU** ，其主要使用 **抽象模型定义** (Abstract Model Definition)和
**自动模块实例化** (Automatic Model
Instantiation)模块。抽象模型定义基于专家经验定义模型，把寄存器分为控制寄存器、状态寄存器、数据寄存器、控制-状态寄存器。自动模块实例化则基于之前的模型定义，基于执行对模型进行填充。主要是查找寄存器的类型、寄存器在内存中的位置、中断等。

![](https://image.3001.net/images/20220609/1654777495_62a1e697bfe6c08ee5946.png!small)P²IM只实现了寄存器和中断，没有实现DMA(Direct
Memory Access)的情况，下文的DICE正为此问题而构建。其目录结构如下：

    
    
    .
    ├── afl                           # fuzzer source code
    ├── docs                          # more documentation
    ├── externals                     # git submodules referencing external git repos for unit tests, real firmware, and ground truth
    ├── fuzzing
    │   └── templates                 # "random" seeds and configuration file template to bootstrap fuzzing
    ├── LICENSE
    ├── model_instantiation           # scripts for instantiating processor-peripheral interface model and fuzzing the firmware
    ├── qemu
    │   ├── build_scripts             # scripts for building QEMU from source code
    │   ├── precompiled_bin           # pre-compiled QEMU binary for a quick start
    │   └── src                       # QEMU source code. AFL and QEMU system mode emulation integration is based on TriforceAFL.
    ├── README.md
    └── utilities
        ├── coverage                  # scripts for counting fuzzing coverage
        └── model_stat                # scripts for calculating statistics of the processor-peripheral interface model instantiated
    

安装与使用可参见 **[Github](https://github.com/RiS3-Lab/p2im)** 。

  *  **DICE [11]**

 **DICE是一种模拟并生成DMA(Direct Memory Access)输入的动态分析方法，其核心思想是识别和模拟抽象的DMA input
channel(作者定义的一个抽象概念，可以视为固件与外设通过DMA交换数据的桥梁)，而不是模拟种类繁多的外设及控制器。**

目前的针对于固件的动态分析一般无法处理固件中的DMA操作，比如上文的P²IM，从而限制分析所支持的设备种类以及代码覆盖率。作者在针对ARM Cortex-M的P²IM以及针对于MIPS
M4K/M-class的PIC32模拟器上使用了DICE。在83个benchmarks上进行测试，检测到了来自5个不同厂商的9种不同的DMA
控制器。对7个fuzz-tested的真实世界的固件进行分析，执行路径比之前的高79倍，并额外发现了5个位置漏洞。

![](https://image.3001.net/images/20220609/1654777563_62a1e6db5c5b2f3aa4b38.png!small)研究细节这里就不作展开，DICE主要贡献在于：针对DMA在基于MCU设备上的普遍性和多样性，通过集成到现有分析方案，实现了与硬件无关的DMA输入模拟，并能够自动化的推断出DMA缓冲区的位置和大小。

DICE结构如下：

    
    
    .
    ├── DICE-Evaluation
    │   ├── ARM
    │   │   ├── DICE-P2IM-Utilities     # DICE-P2IM scripts for model instantiation 
    │   │   ├── Fuzzing                 # Firmware binaries, source code and scripts for fuzz testing with DICE-P2IM
    │   │   └── Unit-Test               # Firmware binaries, source code and scripts for unit test with DICE-P2IM
    │   └── MIPS
    │       └── Unit-Test               # Firmware binaries, source code and scripts for unit test with DICE-MIPS-emulator 
    ├── DICE-Patches                    # DICE patches (Add-ons) for P2IM and MIPS-emulator
    ├── DICE-precompiled
    │   ├── ARM_bin                     # Precompiled QEMU-DICE-P2IM binaries with DMA input channels identification and emulation for the ARM Cortex-M
    │   ├── ARM_bin_Disabled            # Precompiled QEMU-DICE-P2IM binaries with DMA input channels identification for the ARM Cortex-M
    │   └── MIPS_bin                    # Precompiled QEMU-DICE-MIPS-emulator with DMA input channels identification for the MIPS M4K/M-class
    ├── mips-emulator                   # Vanilla MIPS emulator submodule
    └── p2im                            # Vanilla P2IM framework submodule
    

安装与使用可参见[ **Github**](https://github.com/RiS3-Lab/DICE-DMA-Emulation)。

  *  **Para-rehosting [12]**

 **Para-rehosting针对MCU软件的可移植性问题，使用POSIX接口抽象和实现了一个可移植的MCU来降低移植难度，其会对MCU的常见函数建模。**

![](https://image.3001.net/images/20220609/1654777596_62a1e6fcea17ea6fe9e9f.jpg!small)
Para-rehosting与前文介绍的HALucinator类似，也在HAL上做文章，其使用基于HAL的次要函数替换，即用主机上的等效后端驱动程序替换高级硬件功能，这些后端驱动程序由para-api调用，可以在许多MCU操作系统中重用。Para-rehosting成功地重新rehost了9个MCU操作系统，包括广泛部署的Amazon
FreeRTOS、ARM
Mbed、Zephyr和LiteOS，并使用动态分析工具（AFL和ASAN）发现了28个未知的bug，其中五个获得了CVE，19个被厂商承认。

官方推荐Para-rehosting在Ubuntu 18.04环境下编译使用，具体可参见
**[Github](https://github.com/MCUSec/para-rehosting)** 。

  *  **Firmwire [13]**

 **Firmwire是一个支持三星和联发科的全系统基带固件分析平台，它支持对基带固件映像进行模糊测试、模拟和调试。**

![](https://image.3001.net/images/20220609/1654777641_62a1e72911752f5a504d3.jpg!small)
FIRMWIRE提供基带专用API，可轻松添对供应商、固件映像和安全分析的支持。论文中选择 LTE 和 GSM
协议进行Fuzzing，发现7个可能导致RCE，其中包含 4 个0Day。

使用Firmwire需安装 **[Panda](https://github.com/panda-re/panda)(基于QEMU的仿真器，分支众多，本文就不在赘述**) **，** 安装使用了参见
**[Firmwire手册](https://firmwire.github.io/docs/installation.html)** ，或从
**[Github](https://github.com/FirmWire/FirmWire)** 获取更多信息。

![](https://image.3001.net/images/20220609/1654777760_62a1e7a0238756fd30865.png!small)

  *  **Fuzzware [14]**

 **Fuzzware是一个以可扩展方式对原始单片机固件进行模糊测试的专用系统，其提出了一种细粒度的access modeling
方法，使用精准的MMIO建模，可以通过固件逻辑保存所有路径，帮助Fuzzing变换集中在改变重要的输入上，从而增加了代码覆盖率和Fuzzing效率。**

论文中总结了之前一些Rehosting的方法和弊端：

1、 **High-level emulation** ：通过 **hook**
和从新部署已知库来解决缺少外设的问题，从而避免硬件访问抱错，这样会导致前期手动工作量很大；

2、 **Pattern-based modeling** ：通过将访问模式 **匹配**
到常见的静态硬件寄存器类型来建模外设寄存器，弊端是开销消除不完整(可以消除 full input overhead，无法消除partial input
overhead)；

3、 **Guided symbolic execution-based modeling** ：将硬件寄存器视为 **符号**
输入源，然后将得到的符号值求解到固件最可能运行的路径，缺点当然是需要解决路径消除。

而对硬件外设的许多访问是short-lived，且这些访问的原因是与固件的整体行为无关的(例如：检查外设的状态或设置其配置)。对于确实影响固件行为的访问，固件通常不会使用所有的输入。(例如：directly：从32位数据中提取几位；indirectly：区分少数几个状态值)
因此Fuzzware给出了其解决方案，由于篇幅有限，仅阐释其MMIO访问处理设计，如下所示 ：

![](https://image.3001.net/images/20220609/1654777785_62a1e7b9c16f35af5f876.jpg!small)Fuzzing引擎生成一个原始输入文件，在MMIO访问时，MMIO访问模型将使用输入文件的块，并将其转换为(可能更大的)硬件生成值，然后将其提供给仿真固件。一旦原始输入耗尽，覆盖反馈将提供给Fuzzing引擎以指导继续Fuzzing操作。

Fuzzware的安装与使用可参见[ **Github**](https://github.com/fuzzware-fuzzer/fuzzware)。

  *  **Periscope [15]**

 **Periscope是用于分析设备与驱动之间交互的动态分析框架，并在此框架扩展提出了专用于该场景下的fuzzing框架PeriFuzz。**

![](https://image.3001.net/images/20220609/1654777828_62a1e7e4144eb6c88fc23.jpg!small)
Periscope贡献在于提出了分析硬件和驱动之间交互的分析框架和fuzz框架，在技术上主要通过hook page fault
handler来分析针对驱动与设备共享内存的读写操作，PeriFuzz在两种WiFi的驱动上发现了15个不同的漏洞，其中包括9个0Day。本文的核心贡献在于。

硬件和驱动之间的交互方式可以分为 **设备中断** 、 **MMIO(Memory mapping IO)** 和 **DMA(Direct Memory
Access)** 3类，目前常用的分析设备和驱动间的方法主要包括以下3种：

1、通过为设备加入额外的能力来 **分析交互流程** ，好处是不依赖于操作系统，缺点是要求设备的可编程性或者分析人员即设备开发者。

2、分析驱动与虚拟设备在 **虚拟运行** 环境下的交互，但要求比较苛刻，对每款设备的分析都需要与之对应的虚拟化设备支持。

3、将设备向驱动传输的数据都认为是符号化的值，从而进行 **符号执行** 。虽然不需要虚拟化设备和可编程设备的支持，但可能会产生路径爆炸。

Periscope则通过hook MMIO或DMA下的allocate函数来标记共享的memory region，进一步通过hook page fault
handler，将针对这些memory region的读写都记录下来，从而达到分析的效果。

PeriFuzz使用AFL作为Fuzzing工具，关于Periscope和PeriFuzz安装与使用可参见[
**GitHub**](https://github.com/securesystemslab/periscope)。

  *  **Pretender [16]**

**Pretender通过观测固件与设备之间的交互记录，使用机器学习/模式识别为每一个外设创建模型，再使用QEMU或angr结合生成的外设模型实现固件Rehosting。**

![](https://image.3001.net/images/20220609/1654777883_62a1e81b2c9aeeef47e60.jpg!small)
值得注意的是，Pretender的使用条件 **比较苛刻**
，需安装Avatar，OpenOCD及其众多依赖项，在设置和部署时可能出现问题。组件中的任何一个小版本更改都可能导致工具无法运行，或者间歇性地运行，尤其在中断方面。官方建议在
**Ubuntu 16.04** 环境下，使用`mkvirtualenv`安装运行Pretender，具体可参见
**[Github](https://github.com/ucsb-seclab/pretender)** 。

  *  **Laelaps [17]**

 **Laelaps针对ARM MCU，通过符号执行辅助外设仿真来推断固件的预期行为，从而生成适当的输入以动态地引导具体模拟执行。**

![](https://image.3001.net/images/20220609/1654777927_62a1e84721dc635fa5dbd.jpg!small)
Laelaps结合了固件常规运行和符号执行，在常规运行因访问未实现的外设卡住时，切换到符号执行，以找到正确的输入，从而引导 **QEMU**
找到与实际执行最相近的路径。其主要贡献在于：

1、对基于ARM Cortex-M的MCU系统模型进行了抽象，并提取了系统仿真中所缺少的关键部分；

2、通过设计一个符号化引导的模拟器，填补了全系统设备仿真的缺失部分，该模拟器能够运行各种固件的ARM MCU与以前未知的外设；

3、融入了boofuzz、angr和PANDA等工具辅助动态分析，以Fuzzing固件中的漏洞。

Laelpas的安装和使用可参见[ **Github**](https://github.com/dongmu/Laelaps)。

  *  ** **μEmu [18]****

 ** **μEmu是一种针对ARM微处理器(MCU)固件task
code的动态分析工具，其核心组件是一个设备无关的仿真器，用于仿真未知外设的驱动代码。****

![](https://image.3001.net/images/20220609/1654777977_62a1e879a1cd2e8276642.jpg!small)
在μEmu论文中，研究人员将以往Rehosting思路和弊端大致总结：

1、思路： **将不支持的外设转发给真实的硬件** 。

弊端：需要真是硬件，无法大规模操作。

2、思路： **模拟抽象层，固件依赖抽象层运行** 。

弊端：需要生态支持，不支持定制SOC；不好解耦固件和驱动的安全测试；没有对外设逻辑的测试。

3、思路： **全系统模拟，可在硬件不可知时实现高保真模拟** 。

弊端：不能模拟复杂系统； **P²IM** 需要盲猜状态寄存器的反应，搜索范围过大； **Laelaps** 只能找到短期好的选择； **P²IM** 和
**Laelaps** 都可能造成崩溃或死机。

μEmu不像现存的工作为每个外设建立一个通用的模型，μEmu **着眼于正确模拟外设的每一个独立的存取点** 。要实现这一举措需解决外设输入 **获取**
和 **判断** 两个难点。μEmu使用 **符号执行**
获取模拟固件映像所需信息，固件收到的反应不正确时，执行阶段应该反射出错误，并进入一种失效状态，而失效的执行状态直接反应为一条失效的路径。

μEmu的结构如下：

    
    
    .
    ├── LICENSE
    ├── README.md
    ├── docs                     # more documentation about implementation and configuration
    ├── uEmu-helper.py           # helper scripts to configurate μEmu based on configration file (e.g., μEmu.cfg)
    ├── launch-uEmu-template.sh  # template scripts to launch μEmu
    ├── launch-AFL-template.sh   # template scripts to launch AFL fuzzer
    ├── uEmu-config-template.lua # template config file of μEmu and S2E plugins
    ├── library.lua              # contains convenience functions for the uEmu-config.lua file.
    ├── uEmu-unit_tests          # uEmu unit test samples and config files
    ├── uEmu-fuzzing_tests       # uEmu fuzzing test samples (real-world MCU firmware) and config files
    ├── ptracearm.h
    ├── totalbbrange.py          # IDA plugin for basic block range calculation
    ├── vagrant-bootstrap.sh     # bootstrap file for vagrant box
    └── Vagrantfile              # configuration file for vagrant box
    

安装与使用可参见 **[Github](https://github.com/MCUSec/uEmu#%CE%BCemu)** 。

  *  **Frankenstein [19]**

 **Frankenstein
提供了一个虚拟环境来fuzzing无线设备固件，该工具在固件在运行时转储其当前状态，然后在虚拟环境中重新执行以进fuzzing。**

![](https://image.3001.net/images/20220609/1654778005_62a1e89534a87ef1fd5cb.jpg!small)
Frankenstein使用 **QEMU**
运行仿真，其特点在于通过转储状态使固件“恢复生机”，并为芯片的虚拟调制解调器提供模糊输入。研究人员利用Frankenstein在Broadcom和Cypress蓝牙堆栈中发现三个0Day，该堆栈广泛应用于Apple、三星、Raspberry
Pi等设备。

Frankenstein可使用Web接口配置，功能包括符号管理和内存转储，生成文件和链接器脚本均可自动生成。通过`python3 manage.py
runserver`启动服务后，访问本机8000端口完成配置。

![](https://image.3001.net/images/20220609/1654778033_62a1e8b167ee5a044d677.png!small)Frankenstein更多安装和使用信息可参见
**[Github](https://github.com/seemoo-lab/frankenstein)** 。

 **Rehosting** 的难点在于找到 **规模** 和 **精确** 的平衡点，想在效率和规模上有所建树需要提高工具的 **通用性**
，有些复杂固件难以模拟；而想精确模拟需要提高工具的 **专用性**
，此时又难以扩大规模。针对某些固件静态分析也不失为较好的方式，动静当然各有优劣，静态分析一般围绕 **符号执行** 和 **污点分析**
开展，下文提及部分静态分析工具。

  

## 0x02 静态分析工具

  *  **PATCHECKO [20]**

PATCHECKO是一个针对可执行文件漏洞和补丁存在性检测的框架PATCHECKO。它混合了静态检测和动态检测方法，能够对X86和arm架构的二进制代码进行漏洞检测。

  *  **KARONTE [21][Github](https://github.com/ucsb-seclab/karonte)**

KARONTE是一种静态分析方法，能够通过建模和跟踪多二进制交互来分析嵌入式设备固件，该方法基于污点信息分析，以检测不安全的交互并识别漏洞。

  *  **SaTC [22][Github](https://github.com/NSSL-SJTU/SaTC)**

SaTC
通过利用前后端共享关键字作为污点分析输入，从而能够聚焦在后端执行体中与前端输入强相关的数据引入点，将其作为污点分析的开始位置，降低符号执行复杂度，同时能够更加精准、高效地发现多种类型的安全漏洞。

  *  ** **Firmalice [23]****

Firmalice是一个二进制静态分析框架，能够自动化的检测固件程序中的认证旁路漏洞，Firmalice构建在符号化执行引擎上，结合了程序切片的相关技术来提高其扩展性。

  *  **FIE [24]**

对于某些固件，完整的分析是难以处理的，分析中的各种不精确来源可能会导致误报或漏报。FIE使用符号执行描述外设，改进符号执行技术来适应固件特定的功能，并致力于发现固件中的内存错误。

  *  **PASAN [25]**

PASAN是第一个用于检测嵌入式系统并发外设访问内在问题的静态分析工具。PASAn使用解析器准备的内存布局自动查找每个外设的MMIO地址范围，使用对应的设备驱动提取外设的内部状态机，自动检测外设访问的并发Bug。

  *  **Basespec [26][Github](https://github.com/SysSec-KAIST/BaseSpec)**

BaseSpec是对基带固件中软件和设置做比较性分析的戏方法，通过利用标准的消息结构，BaseSpec能够系统地检查基带软件中的信息结构。

  *  **LightBlue [27][Github](https://github.com/purseclab/lightblue)**

LightBlue是一个BLE固件分析剪裁工具，可以自动感知蓝牙栈的配置文件的框架，允许用户通过删除不需要的蓝牙特性来自动减少他们的蓝牙攻击面。

  *  **FirmXRay [28][Github](https://github.com/OSUSecLab/FirmXRay)**

FirmXRay是Ghidra BLE 固件静态反汇编插件，直接从固件分析link layer漏洞。

## 0x03 总结

1、笔者 **从近期浏览的论文** 出发， **对IoT固件Rehosting作了综述**
，虽然Rehosting的目的一般是Fuzzing一类的动态分析，但由于Fuzzing完全可以单开主题讨论，所以文章并没有过多着墨。

2、笔者在总结中发现，大多数Rehosting框架底层仍青睐 **QEMU** ，对Unicon等指令集模拟涉及并不多；框架或使用符号执行找到模拟
**路径** ，或研究MCU与外设 **关系** ，或针对 **HAL** 等MCU特性，最终目的都是
**让固件Rehosting完成更多更远的顺序执行。**

3、笔者理论根基浅薄，读论文全为弥补自身不足，在浏览这些论文的时候发现学术与实战的侧重点不同，学术注重理论和研究过程，前人的成果既是参考，又不得已避开，所以有些论文给人以花大力气解决小问题的错觉，与之相比，论文中
**对领域内的问题归纳** 和 **解决思路** 更为吸引笔者。

4、笔者由于能力有限，该领域论文(工具)可能有所遗漏，文中提及也只能浅尝辄止，感兴趣的小伙伴可以阅读下文列表中的原论文。单纯就固件分析工具而言，从易用性或二次开发的角度，笔者更倾向于
**实验室开源框架或者商业软件** ，当然很多框架和软件也有顶会论文作为支撑。

## 0x04 论文列表

[1] [SoK: Enabling Security Analyses of Embedded Systems via
Rehosting](https://dspace.mit.edu/bitstream/handle/1721.1/130505/asiafp242-fasanoA-CC-BY.pdf?sequence=1&isAllowed=y)

[2] [Towards Automated Dynamic Analysis for Linux-based Embedded
Firmware](https://www.ndss-symposium.org/wp-content/uploads/2017/09/towards-automated-dynamic-analysis-linux-based-embedded-firmware.pdf)

[3] [FirmAE: Towards Large-Scale Emulation of IoT Firmware for Dynamic
Analysis](https://syssec.kaist.ac.kr/pub/2020/kim_acsac2020.pdf)

[4] [FIRM-AFL: High-Throughput Greybox Fuzzing of IoT Firmware via Augmented
Process Emulation](https://www.cs.ucr.edu/~heng/pubs/FirmAFL.pdf)

[5] [FirmFuzz: Automated IoT Firmware Introspection and
Analysis](https://nebelwelt.net/files/19IOTSP.pdf)

[6] [Avatar: A Framework to Support Dynamic Security Analysis of
EmbeddedSystems’ Firmwares](https://www.ndss-symposium.org/wp-content/uploads/2017/09/02_3_1.pdf)

[7] [Avatar2: A Multi-target Orchestration Platform](https://www.ndss-symposium.org/wp-content/uploads/2018/07/bar2018_1_Muench_paper.pdf)

[8] [Jetset: Targeted Firmware Rehosting for Embedded
Systems](https://www.usenix.org/system/files/sec21fall-johnson.pdf)

[9] [HALucinator: Firmware Re-hostingThrough Abstraction Layer
Emulation](https://www.usenix.org/system/files/sec20summer_clements_prepub.pdf)

[10] [P²IM: Scalable and Hardware-independent Firmware Testing viaAutomatic
Peripheral Interface
Modeling](https://www.usenix.org/system/files/sec20-feng.pdf)

[11] [DICE: Automatic Emulation of DMA InputChannels for Dynamic Firmware
Analysis](https://seclab.nu/static/publications/ieeesp21dice.pdf)

[12] [From Library Portability to Para-rehosting:Natively Executing
Microcontroller Softwareon Commodity Hardware](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_6B-3_24308_paper.pdf)

[13] [FIRMWIRE: Transparent Dynamic Analysis for Cellular Baseband
Firmware](https://hernan.de/research/papers/firmwire-ndss22-hernandez.pdf)

[14] [Fuzzware: Using Precise MMIO Modeling for Effective Firmware
Fuzzing](https://www.usenix.org/system/files/sec22summer_scharnowski.pdf)

[15] [PeriScope: An Effective Probing and FuzzingFramework for the Hardware-OS
Boundary](https://www.ndss-symposium.org/wp-content/uploads/2019/02/ndss2019_04A-1_Song_paper.pdf)

[16] [Toward the Analysis of Embedded Firmware through Automated Re-hosting](https://www.usenix.org/system/files/raid2019-gustafson.pdf)

[17] [Device-agnostic Firmware Execution is Possible: A ConcolicExecution
Approach for Peripheral Emulation](https://openreview.net/pdf?id=rylaZ6iIDr)

[18] [Automatic Firmware Emulation through Invalidity-guided Knowledge
Inference](https://www.usenix.org/system/files/sec21fall-zhou.pdf)

[19] [Frankenstein: Advanced Wireless Fuzzing to Exploit New Bluetooth
Escalation Targets](https://www.usenix.org/system/files/sec20-ruge.pdf)

[20] [Hybrid Firmware Analysis for KnownMobile and IoT Security
Vulnerabilities](https://par.nsf.gov/servlets/purl/10211514)

[21] [KARONTE: Detecting InsecureMulti-binary Interactions in Embedded
Firmware](https://sefcom.asu.edu/publications/karonte-oakland2020.pdf)

[22] [Sharing More and Checking Less:Leveraging Common Input Keywords to
Detect Bugs in Embedded
Systems](https://www.usenix.org/system/files/sec21fall-chen-libo.pdf)

[23] [Firmalice - Automatic Detection of Authentication Bypass Vulnerabilities
in Binary Firmware](https://www.ndss-symposium.org/wp-content/uploads/2017/09/11_1_2.pdf)

[24] [FIE on Firmware: Finding Vulnerabilities in Embedded Systems using
Symbolic
Execution](https://www.usenix.org/system/files/conference/usenixsecurity13/sec13-paper_davidson.pdf)

[25] [PASAN: Detecting Peripheral Access Concurrency Bugs with Bare-Metal
Embedded Applications](https://www.usenix.org/system/files/sec21-kim.pdf)

[26] [BASESPEC: Comparative Analysis of BasebandSoftware and Cellular
Specifications for L3 Protocols](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_6B-4_24365_paper.pdf)

[27] [LightBLue: Automatic Profile-Aware Debloating of Bluetooth
Stacks](https://hexhive.epfl.ch/publications/files/21SEC.pdf)

[28] [FirmXRay: Detecting Bluetooth Link Layer VulnerabilitiesFrom Bare-Metal
Firmware](http://web.cse.ohio-state.edu/~wen.423/papers/ccs20_FirmXRay)

[29]
[嵌入式设备固件安全分析技术研究综述](https://cjc.ict.ac.cn/online/bfpub/yyc-2020818141436.pdf)

## 0x05 参考链接

(1) [基于用户态虚拟化的物联网设备仿真方法](https://paper.seebug.org/1634/)

(2)
[[漏洞分析]FirmAE及DlinkDIR320、600、645漏洞复现](https://www.52pojie.cn/thread-1572565-1-1.html)

(3) [物联网设备的几种固件仿真方式](http://blog.nsfocus.net/qemu/)

(4) [Firm-AFL：高效的IOT固件灰盒fuzz-外文翻译](https://bbs.pediy.com/thread-266036.htm)

(5)
[论文FirmAFL固件模糊测试工具——复现之路](https://blog.csdn.net/weixin_43695001/article/details/123486237)

(6) [Avatar:
一个支持嵌入式系统固件的动态安全分析的框架](https://blog.csdn.net/WateranFire/article/details/79470453)

(7) [HALucinator
虚拟化硬件层模拟启动固件](https://blog.csdn.net/still_night/article/details/109153132)

(8) [Usenix 2020 P²IM
论文阅读笔记](https://blog.lyle.ac.cn/2020/07/04/2020-7-4-p2im-reading-notes/)

(9) [【论文笔记】DICE: Automatic
Emulation](https://gange666.github.io/2021/07/12/paper_notes/2021-0712-DICE%20105af14bb31f41cd8b1f654117fb948d/)

(10)
[2022论文阅读计划——1月](https://www.theseus.top/2022/01/10/2022%E8%AE%BA%E6%96%87%E9%98%85%E8%AF%BB%E8%AE%A1%E5%88%92%E2%80%94%E2%80%941%E6%9C%88/)

(11) [Fuzzware 阅读笔记](https://zhuanlan.zhihu.com/p/499972340)

(12) [跟着白泽读论文丨PeriScope:Effective Probing and
Fuzzing](https://zhuanlan.zhihu.com/p/62174894)

(13) [论文精炼：Device-agnostic Firmware Execution is
Possible](https://blog.csdn.net/weixin_44229639/article/details/121124600)

(14)
[Frankenstein：高级无线模糊测试以利用新的蓝牙升级目标](https://www.x-mol.com/paper/1273712483739660288)

(15) [μEmu论文分析及总结](http://123.56.68.177/2021/09/14/Inference/)

