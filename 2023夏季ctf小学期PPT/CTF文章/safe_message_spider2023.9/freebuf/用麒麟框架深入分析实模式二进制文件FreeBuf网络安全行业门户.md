## 前言

分析一个实模式二进制文件，比如 DOS 可执行文件或者 MBR 代码从来不是一个简单的任务。目前最好的办法是先用 Bochs, QEMU 或者 Dosbox
模拟运行，然后再使用 gdb, debug.exe 或者 IDA
Pro来远程调试。但是这都是在没有[麒麟框架](https://github.com/qilingframework/qiling)(Qiling
Framework)的情况下。现在我们想骄傲的宣布，麒麟框架正式支持 16bit 二进制的模拟运行，并且与之伴随的还有麒麟框架多维度分析二进制文件的能力。

本文在介绍实模式模拟实现细节的同时也会作为一篇教程来介绍麒麟框架的使用。

本文同样发表于[我的博客](https://blog.ihomura.cn/2020/09/06/%E7%94%A8%E9%BA%92%E9%BA%9F%E6%A1%86%E6%9E%B6%E6%B7%B1%E5%85%A5%E5%88%86%E6%9E%90%E5%AE%9E%E6%A8%A1%E5%BC%8F%E4%BA%8C%E8%BF%9B%E5%88%B6%E6%96%87%E4%BB%B6/)。

## Unicorn

麒麟框架基于 Unicorn 引擎，所以在介绍麒麟之前，我想先介绍一下 Unicorn 引擎。Unicorn 是一个以 QEMU
部分代码为基础实现的一个纯粹的 CPU 模拟器。与 QEMU 相比，Unicorn 有很多亮眼的特点：

  * 平台无关。
  * 易于使用和理解的 API。
  * 动态 hook。
  * 编译更快。:D

但是正如之前所说，Unicorn是一个 **纯粹** 的CPU模拟器，它不知道自己上层运行的操作系统是什么，所以这里就有了麒麟框架。

## 麒麟

> 有时候，我自己都不知道怎么解释麒麟到底是什么。 ---- Lau Kaijern，麒麟的作者

确实，很难用一句话来定义麒麟。为了更全面的描述麒麟，我想从麒麟四个核心功能来说明：模拟、分析、调试、扩展。

### 模拟

麒麟最基础的功能就是模拟，但是和 Unicorn 的模拟有所不同。刚才提到过，Unicorn 是一个 CPU
模拟器，而麒麟实际上是一个操作系统模拟器。下面是一个简单的图来说明一个原生应用和一个模拟应用的联系。

    
    
    |-------|           |---------|
    |Program| <-------> | Binary  |
    |  OS   | <-------> | Qiling  |
    |  CPU  | <-------> | Unicorn |
    |-------|           |---------|
    
    原生应用              模拟应用

通常来说，原生应用在一个特定的操作系统环境上运行，这个操作系统会提供各种各样的 API，而操作系统运行在一个 CPU
之上。对于一个用麒麟模拟的应用，架构是非常相似的：Unicorn 扮演了 CPU
模拟器的角色，麒麟来完成操作系统的任务执行目标二进制文件。为了实现这些，麒麟分为了三层。

    
    
    |--------|  ---    |   os   |   |
    | loader | Qiling
    |  arch  |   |
    |--------|  ---
  * arch 层进行一些和 CPU 架构相关的设置，比如大小端，寄存器等等。
  * loader 层像真正的系统二进制加载器一样，解析目标二进制文件，设置内存布局，把代码和数据加载到内存里。
  * os 层是最重要的部分，提供了系统调用的实现。

### HI.COM 例子

接下来用 DOS 和
[HI.COM](https://github.com/qilingframework/qiling/blob/bc3de75033cf01652e50d1970d32f10048ea4ed6/examples/rootfs/8086_dos/HI.COM)作为例子来讲解这三层是如何相互配合来模拟操作系统的。

对于 arch 层，我们可以假设 CPU 是 8086，它设置起来比较简单，只需要设置好寄存器即可。

COM 文件就只是一个内存镜像，没有任何文件头。因此 loader 层的实现极其简单：分配足够的内存，把整个文件写入到内存，设置好 PC 和栈即可。

对于 os 层，麒麟要做的事情就是尽可能多的实现中断。下面是 HI.COM 的源代码：

    
    
    mov ah,9
    mov dx, 10d
    int 21
    mov ax, 4c00
    int 21
    nop
    db "Hello world!$"

当 Unicorn 执行到 INT 21 的时候，它并不知道这个中断的具体含义，因此它会调用我们在 os 层中定义的 hook 函数，下面就是 os
层相应的实现：

    
    
    def int21(self): # Handler for INT 21
            ah = self.ql.reg.ah
            if ah == 0x4C:
                self.ql.uc.emu_stop() # Stop emulation
            # other interrupts...
            elif ah == 0x9:
                s = self.read_dos_string_from_ds_dx() # Read string
                self.ql.nprint(s) # Print the string to console
            # other interrupts...

这就是麒麟为了模拟 COM 执行文件所有的工作。其实还是蛮简单的，不是吗？

### Petya 例子

实际上，为了模拟一个 16bit 二进制文件，我大多数的工作都是合理的实现中断。比如 Petya 是一个 MBR 病毒，它大量的使用了 BIOS 提供的
INT 10 图像服务。在现代终端上一个对应的实现是 curses 所以我花了很多时间来把过去的图像中断翻译成了 curses 的调用。以 INT10, 0
为例子。

    
    
    def int10(self):
            # BIOS video support
            # https://stanislavs.org/helppc/idx_interrupt.html
            # implemented by curses
            ah = self.ql.reg.ah
            al = self.ql.reg.al
            if ah==0:
                # time to set up curses
                # copied from curses.wrapper
                self.stdscr = curses.initscr()
                curses.noecho()
                curses.cbreak()
                self.stdscr.keypad(1)
                try:
                    curses.start_color()
                except:
                    pass
                if al == 0 or al == 1:
                    curses.resizeterm(25, 40)
                elif al == 2 or al == 3:
                    curses.resizeterm(25, 80)
                elif al == 4 or al == 5 or al == 9 or al == 0xD or al == 0x13:
                    curses.resizeterm(200, 320)
                elif al == 6:
                    curses.resizeterm(200, 640)
                elif al == 8:
                    curses.resizeterm(200, 160)
                elif al == 0xA or al == 0xE:
                    curses.resizeterm(200, 640)
                elif al == 0xF:
                    curses.resizeterm(350, 640)
                elif al == 0x10:
                    curses.resizeterm(350, 640)
                elif al == 0x11 or al == 0x12:
                    curses.resizeterm(480, 640)
                else:
                    self.ql.nprint("Exception: int 10h syscall Not Found, al: %s" % hex(al))
                    raise NotImplementedError()
                # Quoted from https://linux.die.net/man/3/resizeterm
                #
                # If ncurses is configured to supply its own SIGWINCH handler, 
                # the resizeterm function ungetch's a KEY_RESIZE which will be 
                # read on the next call to getch.
                ch = self._get_ch_non_blocking()
                if ch == curses.KEY_RESIZE:
                    self.ql.nprint(f"[!] You term has been resized!")
                elif ch != -1:
                    curses.ungetch(ch)
                self.stdscr.scrollok(True)
                    
                if not curses.has_colors():
                    self.ql.nprint(f"[!] Warning: your terminal doesn't support colors, content might not be displayed correctly.")
                
                # blink support?
                if curses.has_colors():
                    for fg in range(16):
                        for bg in range(16):
                            color_pair_index = 16*fg + bg + 1
                            if fg not in self.color_pairs:
                                self.color_pairs[fg] = {}
                            curses.init_pair(color_pair_index, COLORS_MAPPING[fg], COLORS_MAPPING[bg])
                            color_pair = curses.color_pair(color_pair_index)
                            self.color_pairs[fg][bg] = color_pair
                            self.revese_color_pairs[color_pair] = (fg, bg)

英文有句名言是 "Simple is better"。现在，相比以前的屏幕，终端已经变得越来越复杂了，结果实现一个简单的屏幕反而变得更难了，因为有太多的
corner cases。

### 模拟侧重点的区别

有心的读者可能已经注意到了，我们这里的模拟其实和真正的 DOS
系统行为并不完全一样。没错，麒麟的模拟就是这样的。完美和快速的模拟从来不是麒麟的首要目标。麒麟关注的是为用户在二进制分析时提供最大的便利。我马上会谈到这一点。

顺带一提，麒麟从设计之初就是平台无关的。这意味着用户可以在 Windows 上运行一个 Linux ELF，在 Mac OS 上运行一个 Windows
exe。然而对于 QEMU 来说这是不可能的，因为它需要把系统调用转发到主机上。

### 分析

麒麟远远不止是一个模拟器。它同样提供了大量的API。

### fs_mapper

让我们以 fs_mapper 为例（因为我刚重构过 XD）：

    
    
    #!/usr/bin/env python3
    # Source: https://github.com/qilingframework/qiling/blob/dev/examples/hello_x86_linux_fake_urandom.py
    # 
    # Cross Platform and Multi Architecture Advanced Binary Emulation Framework
    # Built on top of Unicorn emulator (www.unicorn-engine.org) 
    
    from qiling import *
    from qiling.os.mapper import QlFsMappedObject
    
    class Fake_urandom(QlFsMappedObject):
    
        def read(self, size):
            return b"\x01" # fixed value for reading /dev/urandom
    
        def fstat(self): # syscall fstat will ignore it if return -1
            return -1
    
        def close(self):
            return 0
    
    if __name__ == "__main__":
        ql = Qiling(["rootfs/x86_linux/bin/x86_fetch_urandom"], "rootfs/x86_linux")
        ql.add_fs_mapper("/dev/urandom", Fake_urandom())
        ql.run()

目标二进制文件 x86_fetch_urandom 的源代码为：

    
    
    // Souce: https://github.com/qilingframework/qiling/blob/dev/examples/src/linux/fetch_urandom.c
    #include <stdio.h>
    
    int main(void) {
        FILE *fp;
        int randno; 
    
        if ((fp = fopen("/dev/urandom", "r")) == NULL) {
    	    fprintf(stderr, "Error! Could not open /dev/urandom for read\n");
        	return -1;
        }
    
        randno = fgetc(fp);
        printf("randno: %d\n", randno);
        fclose(fp);
    
        return 0;
    }

这个二进制文件就简单的从 Linux 系统下的伪随机字节流 /dev/urandom 获取一个字节。然而，如果使用了
ql.add_fs_mapper("/dev/urandom", Fake_urandom()) 我们就可以劫持这次读取过程并且返回一个固定的字节。

除了设备文件，fs_mapper 还可以模拟一个完整的磁盘。下面是模拟 Petya 的代码：

    
    
    #!/usr/bin/env python3
    # Source: https://github.com/qilingframework/qiling/blob/dev/examples/petya_8086_mbr.py
    # 
    # Cross Platform and Multi Architecture Advanced Binary Emulation Framework
    # Built on top of Unicorn emulator (www.unicorn-engine.org)
    
    import sys
    sys.path.append("..")
    from qiling import *
    from qiling.os.disk import QlDisk
    
    if __name__ == "__main__":
        ql = Qiling(["rootfs/8086/petya/mbr.bin"], 
                     "rootfs/8086",
                     console=False, 
                     output="debug", 
                     log_dir=".")
        # Note:
        # This image is only intended for PoC since the core petya code resides in the
        # specific sectors of a harddisk. It doesn't contain any data, either encryted
        # or unencrypted.
    
        ql.add_fs_mapper(0x80, QlDisk("rootfs/8086/petya/out_1M.raw", 0x80))
        ql.run()

0x80 是实模式下磁盘的索引。对于 Linux 和 Windows，这个值可以是 /dev/sda 或者
\\\\.\PHYSICALDRIVE0。QlDisk 是一个类，可以把一个文件模拟成磁盘，比如磁头、柱面和扇区的支持等等。之所以要模拟一个侧畔，是因为
Petya 使用了 BIOS 提供的 INT 13 磁盘服务来直接读写硬盘。为了实现这些中断，把一个文件映射成模拟环境下的磁盘是有必要的。

### 系统调用劫持

另一个例子是系统调用劫持。下面是[文档](https://docs.qiling.io/en/latest/hijack/#posix-qlset_api)里的一个例子。

    
    
    from qiling import *
    
    def my_puts(ql):
        addr = ql.os.function_arg[0]
        print("puts(%s)" % ql.mem.string(addr))
    
    if __name__ == "__main__":
        ql = Qiling(["rootfs/x8664_linux/bin/x8664_hello"], "rootfs/x8664_linux", output="debug")
        ql.set_api('puts', my_puts)
        ql.run()

因为麒麟自己就是整个 OS 环境，所以把系统调用暴露给用户是非常简单就可以实现的。

### 快照 & 部分执行

快照可以让用户保存或者恢复一个程序执行的上下文，包括 CPU
寄存器，内存内容甚至是文件描述符。配合部分执行的API，快照可以让用户完全控制一个程序，随意的测试一个程序内的任何一段代码。下面是分析 Petya 的例子：

    
    
    def one_round(ql: Qiling, key: bytes, key_address):
        gkeys = generate_key(key)
        ql.mem.write(key_address, gkeys)
        # Partial executaion
        ql.run(begin=verfication_start_ip, end=verfication_start_ip+6)
        lba37 = ql.mem.read(ql.reg.sp + 0x220, 0x200)
        for ch in lba37:
            if ch != 0x37:
                return False
        return True
    
    # In this stage, we will crack for the password.
    def second_stage(ql: Qiling):
        disk = QlDisk("rootfs/8086/petya/out_1M.raw", 0x80)
        #nonce = get_nonce(disk)
        # Prepare stack
        verfication_data = disk.read_sectors(0x37, 1)
        nonce_data = disk.read_sectors(0x36, 1)
        ql.reg.sp -= 0x200
        verification_data_address = ql.reg.sp
        ql.reg.sp -= 0x200
        nonce_address = ql.reg.sp + 0x21
        ql.reg.sp -= 0x20
        key_address = ql.reg.sp
        ql.mem.write(verification_data_address, verfication_data)
        ql.mem.write(nonce_address - 0x21, nonce_data)
        ql.arch.stack_push(0x200)
        ql.arch.stack_push(verification_data_address)
        ql.arch.stack_push(0)
        ql.arch.stack_push(nonce_address)
        ql.arch.stack_push(key_address)
        for x in product(list(accepted_chars), repeat=2):
            ctx = ql.save()
            # 3xMxjxXxLxoxmxAx
            key = b"3xMxjxXxLxoxmx" + ("".join(x)).encode("utf-8")
            print(f"Trying: {key}")
            if one_round(ql, key, key_address):
                print(f"Key: {key}")
                return key
            else:
                ql.restore(ctx)
        return None

在上面的代码中，我们首先准备好了堆栈，然后保存了一次快照。之后我们把解密的 key 写入到函数参数然后直接调用了验证函数。如果结果表明 key
是错误的，那么我们直接恢复之前保存的快照然后再次尝试。

限于篇幅，我无法在这里介绍麒麟所有的功能。如果有兴趣可以参考麒麟的[文档](https://docs.qiling.io/en/latest/)。总而言之，正是这些强大的
API 让麒麟成为了一个真正的动态打桩分析框架，让麒麟区别于其他的模拟器。

### 调试

我们知道，QEMU 是支持 gdb 远程调试的，那么麒麟怎么能不支持这么好的 feature 呢？

在写下这篇文章的时候，麒麟的调试功能仍然在紧张开发中，但是 16bit 调试已经完成了。简单的增加一行 ql.debugger=True 然后连接 gdb
到 127.0.0.1:9999 即可，下面是一张截图。

![](https://image.3001.net/images/20200909/1599635748.png!small)

### 扩展

目前，麒麟正在把一些逻辑解耦成为单独的扩展。其中我们最近的一个工作是 [IDA
插件](https://docs.qiling.io/en/latest/ida/)，下面是相应的截图：

![](https://image.3001.net/images/20200909/1599635789.png!small)

哦，等一下，我知道大家都是命令行高手，这样的插件真的有意义吗？

当然，正是有了 IDA 插件，至少你不需要再买一份 IDA Linux 授权，因为你可以在 Windows/Mac OS 上运行 Linux
ELF，不是吗？

在麒麟的 [qiling/extensions directory
目录](https://github.com/qilingframework/qiling/tree/dev/qiling/extensions)下还有很多有意思的插件，有兴趣可以查看相应的
REAME 或者文档。

## 总结

麒麟框架是一个非常有野心的框架。我们的终极目标是写出十全十美的分析框架，解除各种限制，比如因为平台或者系统不同导致的壁垒，为广大的逆向工程师们提供最好的体验。没有什么能阻止我们进一步的二进制分析！

然而，麒麟框架现在仍然不完美。欢迎大家给我们一个 [star
](https://github.com/qilingframework/qiling)以示鼓励并且加入到我们的开发中来！我们期待合并你的第一个 PR！

项目地址为：https://github.com/qilingframework/qiling

## 后记

> Qiling 确实是一个拼写错误。本来应该是 Qilin 的。不过无所谓啦 :P
>
> 实际上，暴力穷举破解 Petya 的 key 是没法在可接受的时间内完成的。这里我们仅仅是展示麒麟的 API。
>
> IDA 7.0 不支持 Python3，但是 Ghidra 支持马上就会有了。
>
> TLDR：点个 [star ](https://github.com/qilingframework/qiling)再走吧。

