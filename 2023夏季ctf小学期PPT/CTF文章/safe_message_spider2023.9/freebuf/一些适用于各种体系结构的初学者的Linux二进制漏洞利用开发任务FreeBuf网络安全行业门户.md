![](https://image.3001.net/images/20190906/1567700495_5d71360fa8c38.jpg!small)

##  Linux的PWN并不难

 **这是一套针对初学者的Linux二进制漏洞利用开发任务，目前这一套学习内容主要针对的是堆栈缓冲区溢出问题。**

**我创建这个项目是为了学习如何在不同体系结构上执行简单的二进制开发，出于教育目的，在解决这一系列任务时，必须遵守下面列出的一组规则。这些任务其实非常小，有的规则是故意没有实现的。它与大多数CTF挑战相反，因为这些任务是直接提供给大家的，我们只需要去实现即可。**

##  规则

> 1、所有任务都必须使用建议的方法来解决，即使你有其他更简单的方法。
>
> 2、所有任务都必须通过假定启用或禁用的特定保护来解决，即使体系结构、工具链或特定环境不支持它们。
>
> 3、所有任务都假设了一个动态链接的libc和已知的二进制文件。
>
> 4、所有的ROP链都必须手动构造。

##  任务

###  建议的方法

> 1、[01-local-overflow](https://github.com/xairy/easy-linux-> pwn/blob/master/src/01-local-overflow.c)：溢出buffeer，并重写x的值。
>
> 2、[02-overwrite-ret](https://github.com/xairy/easy-linux-> pwn/blob/master/src/02-overwrite-ret.c)：使用not_called()的地址重写堆中任意的返回地址。
>
> 3、[03one-gadget](https://github.com/xairy/easy-linux-> pwn/blob/master/src/03-one-> gadget.c)：跳转到一个one_gadget地址，确保满足特定的条件，对于某些架构，可能需要使用到ROP链。
>
> 4、[04-shellcode-static](https://github.com/xairy/easy-linux-> pwn/blob/master/src/04-shellcode-static.c)：在栈中分配一个shellcode，并启动/bin/sh。
>
> 5、[05-shellcode-dynamic](https://github.com/xairy/easy-linux-> pwn/blob/master/src/05-shellcode-dynamic.c)：跟之前的任务一样，但这里的栈地址是未知的。
>
> 6、[06-system-rop](https://github.com/xairy/easy-linux-> pwn/blob/master/src/06-system-rop.c)：组成一个ROP链来执行system("/bin/sh")。
>
> 7、[07-execve-rop](https://github.com/xairy/easy-linux-> pwn/blob/master/src/07-execve-> rop.c)：组成一个ROP链并通过syscall执行execve("/bin/sh",NULL, NULL)
>
> 8、[08-overwrite-global](https://github.com/xairy/easy-linux-> pwn/blob/master/src/08-overwrite-global.c)：组成一个ROP链来重写x值，并跳转到not_called()。

##  保护机制

空白处意味着保护状态跟建议的方法不相关。

![](https://image.3001.net/images/20190906/1567700528_5d713630235bd.png!small)

**禁用ALSR：**

    
    
    echo 0 | sudo tee /proc/sys/kernel/randomize_va_space

**启用ASLR：**

    
    
    echo 2 | sudo tee /proc/sys/kernel/randomize_va_space

##  解决方案

这些解决方案仅供参考，并不一定适用于所有场景。

![](https://image.3001.net/images/20190906/1567700551_5d71364782daa.png!small)

**环境要求**

这些任务已经在x86-64 CPU设备上进行了测试，测试平台为Linux Mint 19.1，下面是相关的软件版本：

![](https://image.3001.net/images/20190906/1567700561_5d71365178d57.png!small)

##  工具安装

###  安装包：

> sudo apt-get install build-essential
>
> sudo apt-get install gcc-arm-linux-gnueabihf gcc-aarch64-linux-gnugcc-mips-> linux-gnu gcc-mips64-linux-gnuabi64 gcc-powerpc-linux-gnugcc-> powerpc64-linux-gnu gcc-sparc64-linux-gnu
>
> sudo apt-get install libc6-dev:i386 libc6-armhf-cross libc6-arm64-cross
> libc6-mips-crosslibc6-mips64-cross libc6-powerpc-cross libc6-ppc64-cross
> libc6-sparc64-cross
>
> sudo apt-get install qemu-user
>
> sudo apt-get install gdb gdb-multiarch
>
> #These are probably not required, but just in case:
>
> #sudo apt-get install gcc-7-multilib gcc-multilib-arm-linux-gnueabigcc-> multilib-mips-linux-gnu gcc-multilib-mips64-linux-gnuabi64gcc-multilib-> powerpc-linux-gnu gcc-multilib-powerpc64-linux-gnu

###  构建代码：

    
    
    ./build.sh

###  使用pip安装pwntools和ropper：

    
    
    pip install --user pwntools ropper

为QWMU和pwntools安装qemu-binfmt：

> sudo mkdir /etc/qemu-binfmt
>
> sudo ln -s /usr/arm-linux-gnueabihf/ /etc/qemu-binfmt/arm
>
> sudo ln -s /usr/aarch64-linux-gnu /etc/qemu-binfmt/aarch64
>
> sudo ln -s /usr/mips-linux-gnu/ /etc/qemu-binfmt/mips
>
> sudo ln -s /usr/mips64-linux-gnuabi64/ /etc/qemu-binfmt/mips64
>
> sudo ln -s /usr/powerpc-linux-gnu/ /etc/qemu-binfmt/ppc
>
> sudo ln -s /usr/powerpc64-linux-gnu/ /etc/qemu-binfmt/ppc64
>
> sudo ln -s /usr/sparc64-linux-gnu/ /etc/qemu-binfmt/sparc64

##  项目地址

> easy-linux-pwn：【[GitHub传送门](https://github.com/xairy/easy-linux-pwn)】

##  参考资料

> 1、<https://w3challs.com/syscalls/>
>
> 2、<https://azeria-labs.com/writing-arm-assembly-part-1/>
>
> 3、<https://github.com/invictus1306/Workshop-> BSidesMunich2018/blob/master/workshop_slides.pdf>
>
> 4、<https://static.docs.arm.com/ddi0487/b/DDI0487B_a_armv8_arm.pdf>
>
>
> 5、[https://blog.linuxplumbersconf.org/2014/ocw//system/presentations/2361/original/02%20-%20a64-isa-> intro-> final.pdf](https://blog.linuxplumbersconf.org/2014/ocw/system/presentations/2361/original/02%20-%20a64-isa-> intro-final.pdf)
>
> 6、<https://blog.perfect.blue/ROPing-on-Aarch64>
>
> 7、<https://0xabe.io/ctf/exploit/2016/05/02/GoogleCTF-forced-puns.html>

 ***参考来源：[xairy](https://github.com/xairy/easy-linux-pwn)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

