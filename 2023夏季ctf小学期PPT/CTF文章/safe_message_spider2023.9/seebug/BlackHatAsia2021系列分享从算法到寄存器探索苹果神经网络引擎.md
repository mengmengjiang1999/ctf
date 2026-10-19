**作者：此彼@蚂蚁安全实验室  
原文链接：<https://mp.weixin.qq.com/s/CjWMFtPpl5YutgdP2LctKQ>**

在今年的Black Hat Asia上，蚂蚁安全实验室共入选了5个议题和3个工具。本期分享的是蚂蚁天穹实验室的议题《从算法到寄存器探索苹果神经网络引擎》。

# 1 引言

自 iPhone X
面世以来，越来越多的智能设备开始采用面容识别作为生物特征验证手段。然而对这些智能设备端的神经网络计算可靠性和安全性的研究少有报道，已有的技术文章也没有深入到代码操作硬件的实现层面。从iPhone
X上市已过去3年半，仍然没有公开的对面容ID实现层面的研究资料。

为了验证
iPhone面容识别的安全性，探索端设备生物特征识别的安全防护技术，更好的帮助移动设备的安全提升，本文将首次展示我对iPhone设备神经网络计算安全实现方式的一手研究成果，并分析其原理和可能存在的安全风险。

## 1.1 内容简介

本分享包含4个主要内容。

第一部分：逆向分析面容ID和安全神经网络引擎，并分析面容ID在软件层面上的实现方法。

第二部分：逆向找到“机器学习算法”转化为“寄存器操作”的过程中涉及所有组件。

第三部分：提取独立ANE编译器、开发ANE反汇编器。反汇编器可以解析内核驱动加载的内部神经网络文件。

第四部分：总结出6个可能的攻击面，介绍已经获得苹果致谢的bug。

## 1.2 名词解释

ANE: Apple Neural Engine 苹果神经网络引擎

AP: Application Processor 应用处理器

SEP: Secure Enclave Processor 安全隔区处理器

SEP APP: Application for SEP 运行在SEP中的应用程序

FaceID: 面容ID

# 2 面容ID和安全神经网络引擎

本章节着重介绍3个最受关心的逆向成果：1.面容ID的软件架构 2. 面容ID的神经网络参数解密 3. 安全神经网络引擎硬件如何被操作的。

## 2.1 FaceID的实现架构

![](https://images.seebug.org/content/images/2021/06/013be129-efa3-494b-8774-5ff290742ed8.jpg-w331s)

上图用一些图框和箭头表示不同特权空间和交互方法。以人脸解锁为例，一些守护进程会通过XPC通知进程biometrickitd。biometrickitd通过IOKit调用内核中的驱动。内核驱动通过IOP调用协处理器SEP，SEPAPP
sprl会处理一些摄像头调用等行为，最终交给SEPAPP esipAppl去执行真正的神经网络计算。

由于SEP的固件和启动链有着严格的加密验签机制，过去很长的一段时间里我们完全不知道里面发生了什么。

## 2.2 SEP从AP加载加密神经网络参数并解密

![](https://images.seebug.org/content/images/2021/06/57b24727-6291-4fdb-a0b3-e1ecc3df2715.jpg-w331s)

操作系统启动后，FaceID会从文件系统加载名为DCNKernel.bin的文件。此文件可能是神经网络的训练好的权重，但被AES加密过的，解密用的iv和key被硬编码在SEP的固件里。且SEP会检查文件的SHA384数字摘要，摘要也是硬编码在代码中。

这就意味着SEP固件版本和系统版本需要基本一致，否则FaceID可能不可用。这也解释了 checkm8
越狱的手机如果系统降级但sep不降级导致FaceID不可用的原因。

## 2.3 FaceID在SEP中直接操作硬件寄存器

    
    
    伪代码：
    [(addr, value), …] = InterpreterLikeProduce(DmaBaseSetup, Setup, StaticCfg)
    
    for (addr,value) in [(addr, value), …]
    
        ffwCommon_writeReg32(addr, value)

左右滑动查看完整代码

FaceID直接操作硬件寄存器实现神经网络的计算过程。代码会从静态硬编码的数据中提取信息，计算出需要写入的寄存器地址和数值，然后调用函数写入。

本质上FaceID在SEP中实现了一种像解释器的程序，它将3种不同的设置信息转化为寄存器地址和需要向这些地址写入的数值。可惜这些寄存器地址和数值的含义我们是不知道的。寄存器被写入后，到底进行了哪些运算我们也是不知道的。

# 3 苹果神经网络引擎框架

在A11处理器上只有安全神经网络引擎，没有给AP开放接口使用。自A12处理器起，苹果将神经网络引擎分为，专门为SEP使用的“安全神经网络引擎”和为AP使用的“神经网络引擎”。

安全和非安全的神经网络引擎存在软硬件隔离。本章将展示逆向AP使用的“神经网络引擎”的成果。

## 3.1 开放给App使用的架构

![](https://images.seebug.org/content/images/2021/06/760a3b5b-d358-4c2c-9c7c-4aa01338347d.jpg-w331s)

苹果从A12芯片起开放了ANE给App使用。虽然苹果公司的白皮书上说Application Processor Neural Engine和Secure
Neural Engine有硬件级别的隔离，但是他们对寄存器的使用上可能有相似之处。

同样的，我用一些图框和箭头表示不同特权空间和交互方法。与Secure Neural
Engine不同的是App可以直接访问几个内核驱动接口。ANE的编译会在独立的隔离的进程里。且ANE的固件是不加密的。

## 3.2 ANE内部数据处理流程

![](https://images.seebug.org/content/images/2021/06/30501a27-7fa1-4426-b2c6-4fc30a62426e.jpg-w331s)

上图中的方框代表数据，圆圈代表处理，描述了ANE框架内部将预训练模型加工成寄存器操作的完整过程。网络上有很多训练好的神经网络，但依赖不同的机器学习框架运行。苹果提供了coremltools将他们转化成统一的mlmodel格式。

coremlcompiler会将mlmodel文件编译成一些文件存放于特定文件夹下面，一般是mlmodelc为后缀名的文件夹。mlmodelc文件夹下面的一些文件会提供给ANE的与编译器处理，产生包含net.plist文件在内的另一批文件。将net.plist等文件提供给ANE编译器后，会编译出model.hwx文件。

model.hwx文件会被内核驱动加载。内核驱动会解析文件提取寄存器操作信息传递给ANE协处理器。最终由ANE协处理器操作寄存器来执行实际的神经网络运算。这处理流程比较长和复杂，其中很可能会出现bug。

## 3.3 内部处理流程所处空间的关系

![](https://images.seebug.org/content/images/2021/06/fce252fe-48e4-44af-a5e5-e884d136252d.jpg-w331s)

为了方便研究安全风险，我把不同的过程按不同的特权空间进行划分。因为在安全问题的研究上我们更关心特权提升的问题，这些过程恰恰可能提供这样的机会。coremltools一般运行在开发者的主机电脑上，他会将其他机器学习框架的预训练好的数据转化为统一的mlmodel格式。

这一过程需要coremltools解析各种格式的文件，且这些文件可能是从不可信的渠道获得的，比如网络上公开的预训练数据。coremlcompiler过程既可以在开发者电脑上进行也可以在App中运行，在App中运行时coremlcompiler与App的进程权限一致，同样此时的App也可能加载的是不可信来源的mlmodel文件。

ANE预编译和完整编译过程发生在一个名为ANECompilerService的守护进程中，被编译的文件直接来自于App。对ANECompilerService进程来说App提供的文件也是不可信的，所以苹果也限制了ANECompilerService进程的权限。ANE内核驱动运行在内核空间，与前三个处理一样的是他们都运行在application
processor中。ANE固件则运行于独立的协处理器中。

## 3.4 ANE内核驱动

![](https://images.seebug.org/content/images/2021/06/7eb3034b-216d-49f2-908b-cef9fd6d5479.jpg-w331s)

ANE内核驱动为App和aned守护进程提供了不同的客户端。App的客户端只有打开、关闭和ProgramSendRequest三个接口。

aned守护进程有使用驱动所有接口的权利。aned进程也负责把编译出的model.hwx文件传递给内核驱动解析加载，并把一些具柄传递给App。内核驱动会通过anecmdsend函数与ane固件交互。

## 3.5 ANE固件

    
    
    Load Program:
        CSneTMDrv::ParseTD(void const*,ulong,ANERegs_t *,ane_TD_HEADER_t *,bool)
    
    Execute:
        CSneTMDrv::AddTDList(void const*,ulong,ulong,ulong,uint,uint *,uint,ulong volatile*,_rtk_timer_call *,bool)

左右滑动查看完整代码

ane固件运行于独立的协处理器中，二进制代码可以在刷机包中找到，且没有被加密。这里主要介绍两个函数，一个是对model.hwx中可执行数据段的内部数据进行解析的函数，另一个是涉及实际操作寄存器进行神经网络运算的函数。在这里不分析固件的所有实现，因为这不是主要内容。

# 4 ANE工具集

为了方便各位研究，我把我写的工具集全部开源。工具开源地址：https://github.com/antgroup-arclab/ANETools

工具集包含了我编写的通过命令行直接调用苹果内部组件的工具、我开发的反汇编ANE寄存器操作的工具和一些实用脚本。

## 4.1 所有算法与mlmodel文件

![](https://images.seebug.org/content/images/2021/06/a1e2bf24-b326-45b7-84ed-3ab76aba3b84.jpg-w331s)

为了把其他机器学习框架转化为统一的mlmodel文件，苹果开发了一种模型中间语言。此中间语言支持一百几十种元算法，所有其他机器学习框架中的算法必须都由元算法组合而成。你可直接使用这些元算法构造出自定义的机器学习算法。

## 4.2 编译mlmodel文件的coremlcompiler

    
    
    开发机上的工具路径:
        /Applications/Xcode.app/Contents/Developer/usr/bin/coremlc
        /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/coremlcompiler
    设备上的相关类名:
        CoreML
    
    输入: *.mlmodel 文件
    输出: *.mlmodelc/ 文件夹

左右滑动查看完整代码

coreml编译器不仅存在于主机上也存在于苹果设备中。开发App时如果包含静态mlmodel文件，Xcode会使用自带的coreml编译器，直接将编译出的文件夹包含到App文件中。

App也可以远程下载即时编译mlmodel文件。幻灯片中也展示了一般mlmodelc文件夹包含的文件，mlmodel文件也可以包含多个机器学习模型。

## 4.3 Espresso预编译coremlcompiler产出的文件

    
    
    0x1b0009cb0 Foundation!-[NSDictionary(NSDictionary) writeToFile:atomically:]
    0x1dd6316d0 Espresso!Espresso::ANECompilerEngine::compiler::dump_ir(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)
    0x1dd5a78dc Espresso!espresso_dump_ir
    0x1047f1c0c ANECompilerService!0x9c0c +[_ANEEspressoIRTranslator translateModelAt:key:outputPath:error:]
    0x1047f2ac0 ANECompilerService!0xaac0 +[_ANECoreMLModelCompiler compileModelAt:csIdentity:key:optionsFilename:tempDirectory:outputURL:ok:error:]

左右滑动查看完整代码

如果此mlmodel文件需要通过ANE执行，App会跟aned守护进程通信，提供mlmodelc文件夹下面的文件信息。

如果文件没有被ANE编译器编译过，aned会唤起ANECompilerService进程开始编译。ANE实际编译之前主要会把mlmodelc文件夹下的神经网络描述文件预编译成plist格式。

## 4.4 ANE编译器

![](https://images.seebug.org/content/images/2021/06/447647d6-2559-47d2-b186-8261d22fb141.jpg-w331s)

预编译完成后就会进行实际编译。实际编译过程也在ANECompilerService进程中。代码存在于ANECompiler模块，并以一个函数ANECCompile()做为入口。此函数会将神经网络描述文件、网络权重等文件编译成包含寄存器写入在内的model.hwx文件。

我编写的工具可以从命令行直接调用ANECCompile()函数，不经过ANECompilerService Daemon进程，方便测试研究。

![](https://images.seebug.org/content/images/2021/06/2575056c-46cc-4d83-bb0a-a2a275ed9c97.jpg-w331s)

ANE编译器拥有很多编译选项。可以参考ANETools的代码。需要注意的是，除了输入输出路径参数，至少还需要目标架构参数，才能正常编译。其中还有叫DebugMask的flag可以设置成整型最大值，编译后会产生很多中间文件。

## 4.5 ANE反汇编器

我通过逆向数据结构后独立编写了反汇编工具ANEDisassembler，用于反汇编model.hwx文件。我目前没有发现苹果有解析model.hwx文件的代码。

![](https://images.seebug.org/content/images/2021/06/98fe2346-fd7b-4d1c-aeb9-ada5f6134635.jpg-w331s)

——ANE反汇编器的部分代码。

![](https://images.seebug.org/content/images/2021/06/cd386822-1a57-4544-9b75-3d6bc311392b.jpg-w331s)

——ANE反汇编器的部分代码。

通过分析model.hwx文件，并在ANECompiler模块找到每个比特的含义，我编写的反汇编器ANEDisassembler工具会详细打印出寄存器的数值和对应的比特位，这样能更方便的猜比特位的具体作用。

目前ANETools只实现了对ANE v5指令集的支持，还没有兼容更高版本的ANE指令集。可能兼容的设备有：iPhone Xs, iPhone Xs Max
, iPhone XR ,iPad Air3 ,iPad mini5 ,iPad8。希望ANETools这个工具能对各位有所帮助。

# 5 攻击面分析与漏洞

本章包含了我总结的可能存在的6个攻击面，并且通过漏洞挖掘验证了部分攻击面是真实存在的。

## 5.1 可能的攻击面

我把ANE可能的攻击面分为6种，每一种攻击面都是一个特权空间到另一个特权空间的提升。

第一个可能的攻击面是从远程到本地电脑或远程到App。如之前所述，mlmodel文件不仅可以在开发者电脑上被xcode的coremlcompiler处理，也可以在iOS设备上被App处理。mlmodel文件可以来自网络或其他不可信的地方。

第二个可能的攻击面是从App到aned守护进程。App会将几乎所有跟ane相关的工作交给aned守护进程去做，他们交互过程中很可能有一些漏洞存在。

第三个可能的攻击面是App到ANE编译器。虽然App不直接与ANE编译器交互，但文件会直接由aned守护进程转交给ANE编译器。ANE编译器一定程度上对App是透明的。实现编译器代码安全是很困难的，比如针对浏览器javascript编译器的攻击总能被实现。一旦拿下ANE编译器的权限，就意味着可以篡改任意ANE计算结果了。

第四个可能的攻击面是App到内核驱动，这个攻击面现在看起来有些难，因为内核驱动现在只开放了3个接口给App。但在较低版本的系统上存在App可以访问所有ANE内核驱动接口的漏洞。

第五个可能的攻击面是从aned守护进程到内核驱动。这个攻击面需要攻击者已获取到aned守护进程的权限。aned守护进程有访问ane内核驱动的所有接口权限。这些接口并不暴露给App，所以很可能存在各种检查不严的情况。

第六个可能的攻击面有关ANE内核驱动和ANE固件。他们之间也存在复杂的交互。使用这个攻击面需要攻击者已取得内核权限或已取得ANE固件权限。

## 5.2 已获苹果承认的ANE相关漏洞

![](https://images.seebug.org/content/images/2021/06/694423cd-5077-47d9-9017-471c99ec8aed.jpg-w331s)

苹果已经在iOS14.5中修复了一个内核ANE内核驱动相关漏洞：https://support.apple.com/zh-cn/HT212317

另有3个ANE相关漏洞已被苹果接受还在修复中。

# 6 总结

苹果神经网络引擎已是相当复杂且庞大，本文的介绍集中在框架、流程和ANE指令分析，虽然还没有深入进入硬件，但把一些关键环节值得关注的要点做了总结，也获得了不错的产出。非常期待同行们能够进一步深入研究与分享，如果有什么问题也欢迎交流。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1617/>

