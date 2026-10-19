![](https://image.3001.net/images/20191014/1571061327_5da47e4f1cbea.png!small)

##  DECAF

 **DECAF，英文全称为Dynamic Executable Code Analysis
Framework，即动态可执行文件代码分析框架。DECAF不仅是一款基于QEMU的二进制代码分析平台，而且还是DroidScope动态Android恶意软件分析平台的前身，目前DroidScope已作为DECAF扩展的形式集成到了DECAF中。**

##  DECAF++

DECAF++是全新版本的DECAF，它的污点分析速度大约是DECAF的两倍。据我们所知，它是目前整个系统动态污点分析框架中速度最快的。如果没有可疑（污点）输入存在的情况下，它的可用性更高，而且只会增加4%的资源开销。即使是在数据条件苛刻的工作负载情况下工作，DECAF++的性能也更好。DECAF++的高度灵活性使得它非常适合执行安全分析任务，并且适用于入侵检测系统（IDS），因为它可以过滤出良性的流量。关于更多的技术细节，请参考【[这篇文档](https://www.cs.ucr.edu/~adava003/RAID__Elastic_Whole_System_Dynamic_Taint_Analysis.pdf)】。

![](https://image.3001.net/images/20191014/1571061336_5da47e5807b38.png!small)

##  工具介绍

DECAF（Dynamic Executable Code Analysis
Framework）集成了TEMU（[BitBlaze](http://bitblaze.cs.berkeley.edu/)项目的动态分析组件）的二进制代码分析技术，并且基于TEMU进行了改良：

![](https://image.3001.net/images/20191014/1571061342_5da47e5e989fe.png!small)

上图中显示的是DECAF的整个框架结构，DECAF是一个平台无关的全系统动态二进制分析框架，它提供了以下几种关键特性。

###  虚拟机自省技术

跟TEMU不同的是，DECAF不会使用访客驱动程序来检索操作系统级语义。DECAF的VIM组件能够重新构建虚拟机的操作系统级视图，其中包括支持二进制分析的进程、线程、代码模块和符号。此外，为了支持多种体系结构和操作系统，它遵循与平台无关的设计。提取操作系统级语义信息的工作流在多个体系结构和操作系统中很常见。

###  支持多种平台

理想情况下，我们希望有相同的分析代码（具有最少的平台特定代码）适用于不同的CPU体系结构（如x86和ARM）和不同的操作系统（如Windows和Linux）。它要求分析框架能够在某些情况下隐藏目标体系结构和操作系统的详细信息。此外，为了使分析框架本身具有可维护性，并可扩展到新的体系结构和操作系统，框架中特定于平台的代码也应该最小化。DECAF可以同时支持多个体系结构和多个操作系统。目前，DECAF支持32位Windows
XP/Windows 7/Linux和x86/ARM。

###  污点分析开销低

DECAF可以通过维持CPU寄存器和内存的比特级精度以及编译代码块中污点规则的内联精度来在虚拟机的代码执行期间，同步处理和更新每个CPU寄存器和内存位置的污染状态。污点标签的传播是以异步方式完成的，工具主要在中间表示层（更具体地说，TCG
IR层）实现这种污染逻辑，就很容易将污染支持扩展到新的cpu架构。

###  事件驱动的编程接口

DECAF提供了一个事件驱动的编程接口。这意味着翻译阶段的“工具”和执行阶段的“分析”范式对于分析插件是不可见的。分析插件只需注册感兴趣的事件并实现相应的事件处理功能，代码插装的细节由框架负责。

###  动态指令管理

为了减少运行时开销，仅在必要时才将检测代码插入到转换后的代码中。例如，当插件在函数的入口点注册函数钩子时，此钩子的检测代码仅放置在函数入口点。当插件注销这个函数钩子时，插入的代码也将相应地从翻译的代码中删除。为了简化插件的开发，动态代码插装的管理在框架中也进行了相应的简化，因此插件是不可见的。

##  工具配置

###  项目编译命令

    
    
    sudo apt-get install qemu sudo apt-get build-dep qemu
    
        ./configure --enable-tcg-taint --enable-2nd-ccache --enable-opt-smem
    
        make

###  BFD库安装

    
    
    sudo apt-get install binutils-dev

###  Boost库安装

    
    
    sudo apt-get install libboost-all-dev ```

##  项目配置

    
    
    ./configure make ```
    
        ./configure --enable-tcg-taint make ```
    
        ./configure --enable-tcg-ir-log make ```
    
        ./configure --disable-vmi make ```

##  编译插件

    
    
    cd ./callbacktests
    
        #set decaf location
    
        ./configure --decaf-path=root directory of decaf
    
        make

##  加载插件

    
    
    #start virtual machine, change directory to (root directory of decaf)/i386-softmmu/
    
        ./qemu-­system­-i386 -­monitor stdio -­m 512 ­-netdev user,id=mynet -­device rtl8139,netdev=mynet “YOUR_IMAGE”
    
        #check available cmds
    
        help
    
        #load plugins
    
        load_plugin XXX/callbacktests/callbacktests.so

##  程序追踪

    
    
    #trace a specific program
    
        do_callbacktests calc.exe
    
        #now you can start calc.exe in the guest operating system to see the results.

##  项目地址

> DECAF：【[GitHub主页](https://github.com/decaf-project/DECAF)】
>
> DECAF++：【[WiKi页面](https://github.com/decaf-project/DECAF/wiki/DECAF--plus-> plus)】

 *** 参考来源：[decaf-project](https://github.com/decaf-project/DECAF)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

