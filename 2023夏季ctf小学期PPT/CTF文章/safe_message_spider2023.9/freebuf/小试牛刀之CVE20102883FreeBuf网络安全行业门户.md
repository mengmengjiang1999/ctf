##  前言

 **近来正在学习《漏洞战争》，也是头一回分析二进制漏洞，花了好大一番功夫才搞明白，便想记录下过程。**

初次分析，若有不正之处，还请多多指教。

##  分析环境

> Windos XP & Ollydbg & Immunity debugger & IDA Pro & Adobe Reader 9.3.4

##  分析过程

###  1.定位漏洞点

根据书中给出的信息，漏洞存在于CoolType.dll中，使用IDA Pro反编译CoolType.dll，找到字符串 "SING"
，使用交叉引用功能定位到漏洞代码附近

![](https://image.3001.net/images/20200321/1584803186_5e762d728e421.png!small)![](https://image.3001.net/images/20200321/1584803251_5e762db373916.png!small)但造成漏洞的主要原因是strcat，Adobe
Reader在调用strcat时，未对uniqueName字段的字符串长度进行检测，导致可以将任意长度的字符串复制到固定大小的栈空间中，最终导致栈溢出。（摘抄自《漏洞战争》）

###  2.如何控制EIP

知道从哪可以复制数据到栈中导致栈溢出后，下一步就该考虑该复制多少数据进去才能控制eip。

使用ollydbg附加adobe reader，在0x803DDAB处，也就是call strcat的位置下断点。

使用msf生成样本文件，随后用adobe reader打开，同时触发断点。

![](https://image.3001.net/images/20200321/1584804052_5e7630d401669.png!small)执行F8，数据被复制到栈中，目的地址为0x12E4D8

![](https://image.3001.net/images/20200321/1584804256_5e7631a00f12a.png!small)使用immunity
debugger的mona插件生成溢出字符串，并复制该字符串到0x12E4D8的位置。

至于为什么是溢出字符串的长度为什么是572字节，其实这里我是抄样本里的数据长度。尝试过用500字节会覆盖函数的返回地址，但并非当前函数，使用600、1000、1200都会触发STACK_BUFFER_OVERRUN异常。主要是想搞明白书中的内容，所以这里也用572字节。

![](https://image.3001.net/images/20200321/1584805364_5e7635f4ed121.png!small)

执行F9，触发异常，但此处并未能覆盖EIP

![](https://image.3001.net/images/20200321/1584805986_5e76386247948.png!small)异常信息显示，无法访问[6B413187]，为了消除影响，通过计算偏移找到6B413187的位置，然后使用一个可读写的内存地址去替换它。

但如果直接拿6B413187去计算偏移的话是算不出来的，原因在于6B413187并不在我们生成的溢出字符串中。而EAX来源于[ECX+1C]，应该拿ECX中的值去计算偏移才对。

![](https://image.3001.net/images/20200321/1584806311_5e7639a7cf994.png!small)找到偏移0x130的位置，将6B41316B替换成一个读写的内存地址，比如0x4A8A08E2，这是书中给出的地址，也可替换成其他的。（0x130也就是十六进制的304）

重新调试，将修改后的溢出字符串再次复制到缓冲区。（缓冲区的起始地址是0x12E4D8，被修改的位置在0x12E608，也就是0x12E4D8+0x130）

![](https://image.3001.net/images/20200322/1584806571_5e763aabd0fee.png!small)执行F9，再次触发异常，且成功覆盖EIP

![](https://image.3001.net/images/20200322/1584808083_5e764093bb133.png!small)

再次使用immunity debugger的mona插件去计算偏移

![](https://image.3001.net/images/20200322/1584808115_5e7640b3eda42.png!small)重启调试进程，执行完0x803DDAB的call
strcat后，在0x12E4D8+0x1F8的位置设置内存断点（0x1F8也就是504的十六进制）

![](https://image.3001.net/images/20200322/1584809041_5e76445192b1e.png!small)F9继续执行，执行到第三次断点，找到能覆盖EIP的指令。

![](https://image.3001.net/images/20200322/1584855828_5e76fb14902c5.png!small)

###  3.分析ShellCode

知道如何控制EIP后，继续来分析样本中的ShellCode。

重启调试进程，执行完0x803DDAB的call strcat后，在0x12E6D0的位置设置内存断点

![](https://image.3001.net/images/20200322/1584848972_5e76e04c2b555.png!small)
多次F9执行到0x808B308，也就是call dword ptr ds:[eax]

![](https://image.3001.net/images/20200322/1584849050_5e76e09a516d2.png!small)F7单步执行call
dword ptr ds:[eax]，跟入0x4A80CB38

![](https://image.3001.net/images/20200322/1584849128_5e76e0e858dea.png!small)此时的ESP的值为0x12DD24，而溢出字符串的位置在0x12E4D8。shellcode中通过ADD
EBP,794; LEAVE；回到原来的栈空间中去。

![](https://image.3001.net/images/20200322/1584849331_5e76e1b38e1ed.png!small)F7继续执行

![](https://image.3001.net/images/20200322/1584849517_5e76e26da284b.png!small)而用来绕过DEP的ROP指令和shellcode都存放在堆中，使用POP
ESP修改ESP的值为0x0C0C0C0C

![](https://image.3001.net/images/20200322/1584849791_5e76e37f0350a.png!small)F7继续执行到ESP=0x0C0C0C1C，EIP=4A801F90的位置，前面那几条ROP指令暂不清楚作用是什么，尝试过替换掉成其他无意义的指令和去除这几条指令，shellcode依旧能正常运行。

![](https://image.3001.net/images/20200322/1584850107_5e76e4bbae02c.png!small)而0x4A801F90正是关键的ROP指令之一，除此之外还有0x4A80B692

![](https://image.3001.net/images/20200322/1584850489_5e76e63969cd2.png!small)EAX中的值指向icucnv36.dll的IAT表，通过提前构造好栈中的参数，再利用POP
EAX; JMP DWORD PTR DS:[EAX] 实现函数调用。后面几个函数的调用都是使用这种思路。

第一次调用了Kernel32.CreateFileA函数，其参数为

![](https://image.3001.net/images/20200322/1584850773_5e76e75584fe0.png!small)但后面调用的函数需要用到前一个函数的返回值，shellcode通过以下三条ROP指令将上一个函数的返回值放到下一个函数的参数列表中。

ROP1: XCHG EAX,EDI，此时EAX中存放的正是上一个函数的返回值。

![](https://image.3001.net/images/20200322/1584851005_5e76e83da68f0.png!small)

ROP2: POP EBX，EBX中的值将参下一条ROP指令的计算。

![](https://image.3001.net/images/20200322/1584851156_5e76e8d4f0ce2.png!small)

ROP3: AND DWORD PTR SS:[EBX*2+ESP],EDI，这里才是将返回值放到参数列表的指令。

![](https://image.3001.net/images/20200322/1584851318_5e76e976c4541.png!small)

第二个调用的函数为Kernel32.CreateFileMappingA，参数列表如下

![](https://image.3001.net/images/20200322/1584851449_5e76e9f963fd8.png!small)运用同样的手法调用第三个函数Kernel32.MapViewOfFile，参数列表如下

![](https://image.3001.net/images/20200322/1584851568_5e76ea7048e64.png!small)第四个函数为MSVCR80.memcpy，参数列表如下。位于ESP中的值(0x4F70000)为函数返回地址，也就是Shellcode的位置。

![](https://image.3001.net/images/20200322/1584851728_5e76eb100be7a.png!small)至此，整个shellcode的布局思路也分析得七七八八了。

##  小结

接下来，讨论下分析过程中的几个问题。

> 1.为什么ROP指令的地址都在icucnv36.dll的地址空间
>
> 这点书中也提到，因为在Adobe Reader的各个版本上这个dll的地址都是不变的。通过对比win7和xp中的icucnv36.dll(同一adobe
> reader版本)，发现只有icucnv36.dll没有开启REBASE，DEP，ASLR，且存在可读可执行的.text段和可读可写的.data段。
>
> 2.既然使用500个字节的溢出字符串也能覆盖EIP，那要怎么做才能成功执行shellcode呢？
>
> 直接使用POP ESP的地址覆盖返回地址，将ESP设为0x0C0C0C0C即可，后面的都一样了。（测试时并没有发现GS的影子）
>
> 3.ROP3中的AND DWORD PTR SS:[EBX*2+ESP],EDI能换成诸如mov、xor吗？
>
> 可以，但找不到，尝试过在icucnv36.dll中查找mov、xor、or等指令来替换and，但都找不到。但也许还有其他办法实现该功能。

##  参考资料

> 《漏洞战争》
>
> 《灰帽黑客》第四版 第12章

 ***本文作者：wnltc0，转载请注明来自FreeBuf.COM**

