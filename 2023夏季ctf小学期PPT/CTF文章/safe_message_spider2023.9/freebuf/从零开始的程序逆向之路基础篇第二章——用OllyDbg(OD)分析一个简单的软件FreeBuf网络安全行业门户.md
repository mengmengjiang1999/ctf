作者：Crazyman_Army

原文来自：[https://bbs.ichunqiu.com/thread-43469-1-1.html](https://bbs.ichunqiu.com/thread-43469-1-1.html?from=beef)

  

0x00知识回顾 (由于笔者省事,没开XP虚拟机,而且没关闭ASLR,所以每次重载的内存地址会不一样)

在第一章的内容中，笔者已经讲了OllyDbg(简称OD)的界面介绍以及基础的操作,普及了常用的汇编指令

  
上次课在底下的附件中,我留下了一个演示样例,大家载入OD后搜索到字符串点击跟踪到反汇编窗口的时候会发现与第一章所讲的程序的框架不太一样.

![image.png](https://image.3001.net/images/20180730/1532935128_5b5ebbd8c12dc.png!small)

  
尤其可见多出了很多的call指令,call指令在汇编中就是调用子程序,下面放出代码,各位同学可以比对一下与上篇文件所贴出代码的不同

代码如下:

  

#include <windows.h>

#include <tlhelp32.h>

#include <stdio.h>

BOOL getProcess(const char *procressName);

BOOL getProcess(const char *procressName)

{

char pName[MAX_PATH];

strcpy(pName, procressName);

CharLowerBuff(pName, MAX_PATH);

PROCESSENTRY32 currentProcess;

currentProcess.dwSize = sizeof(currentProcess);

HANDLE hProcess = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);

if (hProcess == INVALID_HANDLE_VALUE)

{

printf("CreateToolhelp32Snapshot()调用失败!\n");

return FALSE;

}

_asm NOP;

BOOL bMore = Process32First(hProcess, ¤tProcess);

while (bMore)

{

CharLowerBuff(currentProcess.szExeFile, MAX_PATH);

if (strcmp(currentProcess.szExeFile, pName) == 0)

{

CloseHandle(hProcess);

return TRUE;

}

bMore = Process32Next(hProcess, ¤tProcess);

}

CloseHandle(hProcess);

return FALSE;

}

int main()

{

char* process = "explorer.exe";

if (getProcess(process))

{

printf("发现explorer.exe\n");

system("pause");

exit(0);

}

else

{

printf("没有发现explorer.exe\n");

printf("Cracke Success!");

}

getchar();

return 0;

}

  

从代码角度来看,很明显,这次笔者讲判断进程封装成一个返回布尔值的函数,所以才会在核心判断部分出现如此多的调用，那这当然不能像上次一样改一步简单的跳转就解决问题，如果改得不对就会造成程序的崩溃。

下面笔者通过三种方法来绕过这个检验explorer.exe进程的小程序

  

方法一:修改判断进程的变量名称

  
在只能搜索中，我们看到了explorer.exe这个进程的字符串,我们用鼠标选中后，双击，在反汇编窗口中跟随

![image.png](https://image.3001.net/images/20180730/1532935163_5b5ebbfb489e4.png!small)

  
反汇编窗口显示的如下:

![image.png](https://image.3001.net/images/20180730/1532935172_5b5ebc0475b67.png!small)

  
用鼠标选中这条代码右键 -> 数据窗口中跟随–> 内存地址

  

![image.png](https://image.3001.net/images/20180730/1532935181_5b5ebc0d84e3f.png!small)

  
数据窗口随之发生了变化,在数据窗口上选中一部分数据右键

  

![image.png](https://image.3001.net/images/20180730/1532935189_5b5ebc15e8a6f.png!small)  

  
右键 –> 复制到可执行文件

  

![image.png](https://image.3001.net/images/20180730/1532935194_5b5ebc1a769b4.png!small)  

  
点击放大键放大该窗口

![image.png](https://image.3001.net/images/20180730/1532935200_5b5ebc20c5d81.png!small)

  

  
然后就可以胡乱修改explorer.exe这个字符串

  

![image.png](https://image.3001.net/images/20180730/1532935207_5b5ebc278cd55.png!small)  

  
笔者这里就随便修改了

  

![image.png](https://image.3001.net/images/20180730/1532935213_5b5ebc2d418f7.png!small)  

  
修改如下:

  

![image.png](https://image.3001.net/images/20180730/1532935219_5b5ebc33ad3d4.png!small)  

  
在窗口上右键,保存文件

  

![image.png](https://image.3001.net/images/20180730/1532935226_5b5ebc3a9d23d.png!small)  

  
文件保存成功

  

![image.png](https://image.3001.net/images/20180730/1532935231_5b5ebc3f18b60.png!small)  

  
点击运行

  

![image.png](https://image.3001.net/images/20180730/1532935236_5b5ebc445f49e.png!small)  

  
第一种方法破解成功

  

方法二:确认过眼神,你不是我们的人

  

回到判断的核心代码,这里面是jnz来进行进程的判断

那jnz 的全拼写是 jump not zero 那其的反义词即为 jump

  
Zero,即为jz 或者 je （jump
equal）,那这样原来的判断explorer.exe就改为了不判断explorer.exe，这样就绕过了检测进程.

  

![image.png](https://image.3001.net/images/20180730/1532935244_5b5ebc4ce94e4.png!small)  

  
下面我们来实际操作,用鼠标选中后

  

  
![image.png](https://image.3001.net/images/20180730/1532935252_5b5ebc5484692.png!small)  

  
双击

  

![image.png](https://image.3001.net/images/20180730/1532935257_5b5ebc594f9a7.png!small)  

  
将jnz short 00291158改为 jz short 00291158或者 je short 00291158,将使用nop填充勾掉

  

  
点击汇编

  

![image.png](https://image.3001.net/images/20180730/1532935263_5b5ebc5f0a7ea.png!small)  

  
然后再保存文件,保存后运行

  

![image.png](https://image.3001.net/images/20180730/1532935269_5b5ebc65b09d7.png!small)  

  
第二种破解方法成功

  

方法三:条件改强制

  

如下图,这个jnz short 00101158是如果zf=0时就会跳转

  
而jnz所在代码的地址为00101137,我们尝试让其无条件跳转到00101137下面一个地址,也就是00101139(下图红框锁标注的区域)

  

![image.png](https://image.3001.net/images/20180730/1532935276_5b5ebc6c1a545.png!small)  

  
双击地址为00101137的那条代码,如下图所示 将jnz short 00101158改为jmp short 00101139，点击汇编

  

  

![image.png](https://image.3001.net/images/20180730/1532935281_5b5ebc71a7ad4.png!small)

  
点击运行按钮

  

![image.png](https://image.3001.net/images/20180730/1532935286_5b5ebc76edc9a.png!small)

  
程序运行截图:

![image.png](https://image.3001.net/images/20180730/1532935295_5b5ebc7fb9bfc.png!small)  

  
很显然破解成功了,那具体是怎么个原理呢,我们这里留个悬念,等用od能分析一个简单程序后,我们回过头来解释这个问题

  

00x01 用OllyDbg分析一个简单的程序

下面,笔者将带领同学去用OllyDbg来分析一个简单的程序

  
笔者为了方便写了一个简单的判断输入数字的程序,代码如下:

  

![image.png](https://image.3001.net/images/20180730/1532935310_5b5ebc8e15683.png!small)  

  
载入OD

  

![image.png](https://image.3001.net/images/20180730/1532935320_5b5ebc981359d.png!small)  

  
反汇编窗口上右键中文搜搜引擎 -> 智能搜索

  

![image.png](https://image.3001.net/images/20180730/1532935324_5b5ebc9cc6005.png!small)  

  
跟踪后的代码可以看到:

  

![image.png](https://image.3001.net/images/20180730/1532935331_5b5ebca3c7149.png!small)  

  
在有程序保护的情况下,你可能无法搜索到字符串,这里先不讨论,笔者将带领同学一步一步分析这个简单的程序

  
这里面push ebp movebp,esp push ecx可以简单的理解为源码中的int main()后的{ (这里为了方便于理解)

  

![image.png](https://image.3001.net/images/20180730/1532935341_5b5ebcad23201.png!small)  

  
push Text.013E3E34,push的意思自然是压栈

这里就不得不要说说C语言中的printf

  
下面是printf的函数声明

> int printf(const char *format, ...);

  
那在默认的情况下,printf函数应该有一个const char*型的参数,而这一行就是把“Please Input Flag
Number:”这个字符串指针当成参数1,压入栈中

  

![image.png](https://image.3001.net/images/20180730/1532935348_5b5ebcb4666f9.png!small)  

  
mov [local.1],0x0

那究竟这个[local.1]是何方神圣呢?

  
我们选中这段代码

  

![image.png](https://image.3001.net/images/20180730/1532935356_5b5ebcbc0168b.png!small)  

  
右键 -> 分析 –> 从模块中删除分析

  

![image.png](https://image.3001.net/images/20180730/1532935362_5b5ebcc285c37.png!small)  

  
此时[local.1]就露出了他真面目[ebp-4]

第一章的时候我们讲到了,mov(move)数据传送指令

mov a,b 把b的值传给a

当然mov也可以对内存中的数据进行赋值

这里面 mov [ebp-4],0x0 就是把0赋值给内存中所设置的变量,其中[]操作符可以引用内存中的数据

类似于源码中

![image.png](https://image.3001.net/images/20180730/1532935372_5b5ebccc96d0e.png!small)![image.png](https://image.3001.net/images/20180730/1532935378_5b5ebcd23b696.png!small)

  

call指令就是调用,那就是调用printf函数输出”PleaseInput Flag Number”这个字符串指针

  

![image.png](https://image.3001.net/images/20180730/1532935384_5b5ebcd81d958.png!small)

  
lea eax,dword ptrss:[ebp-0x4]

LEA指令是一个计算机指令，可以将有效地址传送到指定的的寄存器。

  
按道理来说就把变量1的地址传递给了eax寄存器

  

![image.png](https://image.3001.net/images/20180730/1532935390_5b5ebcde888dc.png!small)  

  
push eax

push Text.00EE3E50

现在的eax其实被传递了变量1的地址

往下面一瞥会发现scanf函数

  
下面是scanf函数的定义

> int scanf(const char * restrict format,...);

  
一般代码中都是scanf(“格式说明符”,&变量地址)

这里面格式说明符是函数的参数1,变量地址是函数的参数2

而这个变量地址就类似于图中的push eax-> 参数2

而格式说明符就类似于图中的pushText.00EE3E50 ->参数1

那为何是先把参数2推入,再把参数1推入呢?

比如 int Text(a,b,c)这个函数Text参数为a,b,c

在Windows调用规定中

这个函数在汇编中会

Push c

Push b

Push a

Call Text函数的地址

  
在此你应该能发现参数啊a,b,c却被反向以c,b,a的顺序压入栈中,然后再callText函数的地址

![image.png](https://image.3001.net/images/20180730/1532935398_5b5ebce6ec140.png!small)

  
Call指令当然就是调用scanf函数读取输入flag的值

  

![image.png](https://image.3001.net/images/20180730/1532935406_5b5ebcee3e1a7.png!small)

  
Add esp,0xc

由于_cdcel调用约定,故需要进行堆栈平衡

  
cmp dword ptrss:[ebp-0x4],0x2F59

cmp是比较指令 而这里面比较的两个对象是变量1与0x2F9(12121)

  
故cmp指令可以影响标志寄存器

![image.png](https://image.3001.net/images/20180730/1532935414_5b5ebcf633bc6.png!small)

  
Jnz short Text.009E1036

Jnz跳转指令,由于前面的cmp指令

若变量1-12121=0 Z位=1 jnz不跳转

  
若变量1-12121!=0 Z位=0 jnz跳转到009E1036

  

![image.png](https://image.3001.net/images/20180730/1532935421_5b5ebcfd7cb76.png!small)  

  
那这个程序的大致流程就是输入变量1的数以后与12121做比较,如果两个数相等,Z位=1
,jnz不跳转,输入Right!;如果两个数不相等,Z位=0,jnz跳转到009E1036上,输出Error!

  
然后剩下的代码分析和前面所讲的差不多,大家可以自己写一下注释

  

![image.png](https://image.3001.net/images/20180730/1532935426_5b5ebd02cd51a.png!small)

  
00x02总结

  

本篇我们介绍如何用OD来分析一个简单的程序,同学可以在事后自己用OD跑一下,这样会理解的更加深刻

下一章 如何用OD(OllyDbg)动态调试程序  

  

点击[“阅读原文”](https://bbs.ichunqiu.com/thread-43469-1-1.html?from=beef)即可下载本次文章所用到的几个程序的例子哦~

