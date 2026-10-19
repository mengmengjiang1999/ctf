![](https://image.3001.net/images/20191115/1573815584_5dce8520a40f3.png!small)

## 工具概述

类似Intel SGX这样的可信执行环境能够保证目标计算机在受到网络攻击或入侵的时候，仍然能够保证敏感计算不受影响。而本文所介绍的SGX-Step是一款针对Intel SGX平台的开源测信道攻击研究框架，SGX-Step由一个Linux内核驱动器和用户空间库组成，它将允许我们配置不受信任的页表条目并完全从用户空间环境（Enclave）中断x86
APIC计时器。我们提出并评估了一种改进的从指令级粒度上出发的单步Enclave执行技术，并演示了SGX-Step如何来执行多种高级攻击。

与以前的Enclave抢占方案不同，SGX-Step设计的关键是为了保存页表项的物理内存位置以及本地APIC内存映射I/O配置寄存器和x86中断描述符表（IDT）。这将允许不受信任的主机进程（攻击者控制）轻松（i）跟踪或修改Enclave页表条目，（ii）配置APIC计时器的一次性/定期中断源，（iii）触发内部处理器中断，（iv）以及完全在用户空间中注册自定义的中断处理程序。

下图中显示的是我们的框架中断和恢复SGX Enclave时的硬件和软件操作步骤：

![](https://image.3001.net/images/20191115/1573815600_5dce85302a08d.png!small)

> 1、本地APIC计时器中断抵达一个加密指令内。
>
>
> 2、处理器执行AEX过程，该过程安全地将执行上下文存储在enclave的SSA帧中，初始化CPU寄存器，并将向量存储到IDT中注册的（用户空间）中断处理程序。
>
> 3、此时，任何特定于攻击的间谍代码都可以轻松插入。
>
> 4、代码库会返回至用户空间AEP。我们修改了官方SGX SDK的不受信运行时环境，以便轻松注册自定义AEP stub。
>
> 5、接下来，我们在执行（6）ERESUME之前，通过写入初始计数MMIO寄存器，为下一个中断配置本地APIC计时器。

## 项目构建&运行

SGX-Step需要使用到一个[ _SGX-capabel_](https://github.com/ayeks/SGX-hardware)
Intel处理器以及一个Linux内核。我们将其升级为了i7-6500U/6700 CPU，并且能够在Ubuntu
16.04（内核版本4.15.0）平台上运行。相关的Linux内核参数如下：

 **Linux内核参数** ****|  **功能** ****  
---|---  
 **nox2apic**|  **在内存映射I/O模式下配置本地APIC设备（以利用SGX-Step的精确单步执行功能）。**  
 **iomem=relaxed, no_timer_check**|  **过滤内核日志中不需要的警告消息。**  
 **isolcpus=1**|  **将目标进程与一个独立的CPU核心关联起来。**  
 **dis_ucode_ldr**|  **禁用CPU微码更新。**  
  
我们可以通过下列方式来将相应启动参数传递至内核执行：

    
    
    $ sudo vim /etc/default/grub
    
      # GRUB_CMDLINE_LINUX_DEFAULT="quiet splash nox2apic iomem=relaxed no_timer_check isolcpus=1"
    
    $ sudo update-grub && sudo reboot

最后，为了复现我们的研究成果，请确保在BIOS中禁用了了C-States和SpeedStep技术。下表中列出的是该工具目前所支持的Intel
CPU以及相应的单步APIC计时器间隔（libsgxstep/config.h）：

 **模块名称** ****|  **CPU** ****|  **频率** ****|  **APIC计时器间隔** ****  
---|---|---|---  
Skylake| [i7-6700](https://ark.intel.com/products/88196)| 3.4 GHz| 19  
Skylake| [i7-6500U](https://ark.intel.com/products/88194)| 2.5 GHz| 25  
Skylake| [i5-6200U](https://ark.intel.com/products/88193)| 2.3 GHz| 28  
Kaby Lake R| [i7-8650U](https://ark.intel.com/products/124968)| 1.9 GHz| 34  
Coffee Lake R| [i9-9900K](https://ark.intel.com/products/186605)| 3.6 GHz| 21  
  
### 1、修复和安装SGX SDK

为了启用和注册自定义的AEP stub，我们修改了官方Intel SGX SDK的不受信运行时环境：

    
    
    $ git submodule init
    
    $ git submodule update
    
    $ ./install_SGX_driver.sh # tested on Ubuntu 16.04
    
    $ ./patch_sdk.sh
    
    $ ./install_SGX_SDK.sh    # tested on Ubuntu 16.04

### 2、构建和加载/dev/sgx-step

SGX-Step自带了可加载的内核模块，支持导出IOCTL接口。运行下列命令即可构建和加载/dev/sgx-step驱动器：

    
    
    $ cd kernel
    
    $ make clean load

### 3、构建并运行测试应用

    
    
    $ cd app/bench
    
    $ NUM=100 STRLEN=1 make parse   # alternatively vary NUM and use BENCH=1 or ZIGZAG=1
    
    $ # (above command defaults to the Dell Inspiron 13 7359 evaluation laptop machine;
    
    $ # use DESKTOP=1 to build for a Dell Optiplex 7040 machine)
    
    $ # use SGX_SDK=/home/jo/sgxsdk/ for a local SDK installation
    
    $ # use M32=1 To produce a 32-bit executable

## 在项目中使用SGX-Step

如果你想在自己的项目中使用SGX-Step的话，最简单的方法就是通过[ _git子模块_](https://git-scm.com/book/en/v2/Git-Tools-Submodules)来使用：

    
    
    $ cd my/git/project
    
    $ git submodule add [email protected]:jovanbulck/sgx-step.git
    
    $ cd sgx-step # Now build `/dev/sgx-step` and `libsgxstep` as described above

接下来，进入app目录并查看Makefiles，我们将会看到一个客户端应用程序与libsgxstep以及其他本地SGX SDK/PSW包建立了连接。

## 项目地址

> SGX-Step：【[ _GitHub传送门_](https://github.com/jovanbulck/sgx-step)】

 *** 参考来源：[ _kitploit_](https://www.kitploit.com/2019/11/sgx-step-practical-attack-framework-for.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

