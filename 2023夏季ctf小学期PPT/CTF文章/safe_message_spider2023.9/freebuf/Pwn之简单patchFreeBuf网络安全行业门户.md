本文首发于“合天智汇”公众号 作者：hope

## 1.引言

在攻防的时候不仅仅需要break，还需要fix将漏洞patch上。

## 2.工具

这里我使用的是keypatch这个ida脚本

下载地址:https://github.com/keystone-engine/keypatch/blob/master/keypatch.py

## 3.栈溢出的patch

### 漏洞原理

由于输入函数的输入长度超过了局部变量所开辟的空间，因此使得输入能够覆盖到返回地址

### patch

简单了解原理之后，我们可以知道，栈溢出起始就是输入的长度过大，那么我们将输入长度修改到局部变量开辟空间的范围内即可

### 例子

###
32为情况下![](https://image.3001.net/images/20201012/1602493568_5f841c801584d8176b281.png!small)

我们可以看到,buf距离ebp（栈底）距离0x28，但是输入却能够输入0x100，很明显的栈溢出漏洞![](https://image.3001.net/images/20201012/1602493577_5f841c8965903618661d4.png!small)

可以看到这里参数为0x100，因为32位程序是通过栈传参的。![](https://image.3001.net/images/20201012/1602493587_5f841c93619ad015be880.png!small)

再装好keypatch之后，会在Edit选项栏中出现keypatch的选项，接着选中参数0x100，点击patch![](https://image.3001.net/images/20201012/1602493598_5f841c9e88d8c3fe5caad.png!small)

将长度改成小于0x28即可，这里需要注意输入长度要为16进制。这里输入输入3个nop指令是因为这条指令本身Size为5，然后push
0x20为2，因此需要填充三个nop与原本的Size一致。![](https://image.3001.net/images/20201012/1602493610_5f841caad1b37faab74f2.png!small)

修改完毕后，保存即可

64位情况下

我们zhidao64位下是通过寄存器传参数的，因此我们再找长度的参数时，找到相应的寄存器即可![](https://image.3001.net/images/20201012/1602493622_5f841cb695681284a9fe0.png!small)

例如read函数的长度参数是通过rdx(edx)传入的，找到相应的寄存器按照上面方法修改即可。

## 4.格式化字符串的patch

### 漏洞原理

格式化字符串的漏洞是因为，程序中存在着格式化字符串输出函数，典型的printf，但是printf，只有格式化字符串参数，而没有后续的参数一,参数二,并且格式化字符串参数由我们所控制，从而导致了任意地址读写的漏洞触发。

###
例子![](https://image.3001.net/images/20201012/1602493635_5f841cc39ff8d7c39ca24.png!small)

题目中存在着典型的格式化字符串漏洞，那么修改漏洞有几种方法，例如将printf函数修改为puts函数或者添加%s的参数。

### 方法一

若程序中即存在printf函数，又存在puts函数，那么我们可以将printf函数修改为puts函数![](https://image.3001.net/images/20201012/1602493643_5f841ccbc86856fc20d45.png!small)

我们找到puts函数的plt表地址，因为puts函数也是带一个参数，并且puts函数与printf函数的plt表地址长度一致，因此直接修改不会造成程序down掉![](https://image.3001.net/images/20201012/1602493652_5f841cd42cb6ea0b42d10.png!small)

修改成puts函数的地址![](https://image.3001.net/images/20201012/1602493661_5f841cdd9fc342d0c0687.png!small)

修改成功后的效果，但是puts函数与printf函数还是有一点点区别的，因为puts函数是自动在输出的字符串尾部加入一个回车符，在有些比赛的check脚本中是通过比较两次输入与输出是否全等，就会导致这种patch方法不能过关。

方法二

加入一个%s参数![](https://image.3001.net/images/20201012/1602493672_5f841ce8974f14c6a8984.png!small)

可以看到除了传递格式化字符串参数以为，程序还存在mov
eax,0，我们可以利用该指令修改，但是想要修改为%s还有一个问题，程序中不存在%s这个字符，就需要我们手动添加进去![](https://image.3001.net/images/20201012/1602493680_5f841cf0c461e36ef42a3.png!small)

我们可以在.eh_frame这个段中填入%s这个字符串，这个段中的信息不会影响程序的正常运行。![](https://image.3001.net/images/20201012/1602493691_5f841cfba8cdc3381a5af.png!small)

记住填入的地址0x400c01![](https://image.3001.net/images/20201012/1602493702_5f841d06d55e83e8fb58f.png!small)

mov edi, offset 0x400c01; mov rsi,offset format;

完成参数修改![](https://image.3001.net/images/20201012/1602493715_5f841d134dea25a0546b1.png!small)

修改完成

### 堆之uaf漏洞

堆中较为常见的漏洞use after free

漏洞原理

由于堆块释放后没有给指针置空，使得被释放的堆块能够被修改或者重复使用，导致漏洞

例子![](https://image.3001.net/images/20201012/1602493727_5f841d1f95ebf86440fe4.png!small)

free完之后没有将指针置空，很明显的uaf漏洞，想要修补uaf漏洞，则将free之后的指针置空即可![](https://image.3001.net/images/20201012/1602493738_5f841d2aba82be21d036e.png!small)

可以看到在调用完free之后，没有多少空间可以写下新的汇编代码，因此需要与上一个方法一致，跳转到.eh_frame段上![](https://image.3001.net/images/20201012/1602493748_5f841d348ba17a6550897.png!small)

将call free指令修改为跳转指令，在.eh_frame段上写汇编代码
![](https://image.3001.net/images/20201012/1602493759_5f841d3ff32cf217f4053.png!small)

call 0x900; #调用free函数 mov eax, [rbp-0xc]; #取出下标值 cdqe; lea rdx, ds:0[rax*8];
lea rax, qword ptr [heap]; mov r8,0; #段地址不能直接赋予立即数 mov [rdx+rax],r8; jmp
0xD56;

![](https://image.3001.net/images/20201012/1602493772_5f841d4c64f94d08d34a3.png!small)patch效果

5.总结

  * 对于栈溢出来说，patch比较简单，只需要修改输入长度即可

  * 对于格式化字符串漏洞来说，若有puts函数则将printf函数修改为puts函数，若没有则在.eh_frame段上创造%s

  * 对于堆的uaf来说，漏洞patch思路很简单，只需要将指针置空即可，但是需要了解汇编代码。

6.参考文章

[https://xz.aliyun.com/t/5868](https://xz.aliyun.com/t/5868)

7.相关实验

CTF-PWN练习

[实验:CTF-PWN练习(合天网安实验室)](https://sourl.cn/yQLHrN)

PWN是CTF竞赛中的主要题型之一，主要考查参赛选手的逆向分析、漏洞挖掘以及Exploit编写能力。通过由浅入深的方式，一步一步讲解栈溢出攻击原理与实践，同时详细介绍了Linux下GDB调试器的基本使用方法。

