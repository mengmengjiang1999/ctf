作者：[Crazyman_Army](https://bbs.ichunqiu.com/thread-43041-1-1.html?from=beef)

原文来自：[https://bbs.ichunqiu.com/thread-43041-1-1.html](https://bbs.ichunqiu.com/thread-43041-1-1.html?from=beef)

  

0x00 序言:

1.自从上次笔者调戏完盗取文件密码大黑客后,这激发了笔者的创作热情,就给大家带来程序逆向系列,当然有一些地方还是有所欠缺,请大家在私聊中指出我文中的错误,我会加以改正。

  

2.本篇教程每篇文章都会在附件中给出一个程序逆向例子,所用到的知识都会在该篇文章中体现,有兴趣的同学可以自己实践实践

  

3.为什么要学习逆向破解?

a.你可以汉化一些软件给予大家使用

b.你可以进行病毒分析

c.外挂辅助的研究

d.程序的破解

  

4.这套系列笔者所用的工具已经被笔者整理为工具包,链接地址:
[https://bbs.ichunqiu.com/thread-43019-1-1.html](https://bbs.ichunqiu.com/thread-43041-1-1.html?from=beef)

  

5.破解的环境要求由于一些程序的编写者不期望自己的程序被破解(其实谁也不期望),所以就采取了一些比较极端的方法,比如:格式化您的重要资料 ……

  

所以，程序破解的时候需要用到虚拟机，虚拟机推荐使用vmware

  

下载链接:
[https://pan.baidu.com/s/19eBzCzPrSs4xnkwrcWNV_Q](https://pan.baidu.com/s/19eBzCzPrSs4xnkwrcWNV_Q%20%E5%AF%86%E7%A0%81%EF%BC%9A9954)

密码: 9954

虚拟机安装教程: <https://jingyan.baidu.com/article/25648fc1c467eb9191fd00d6.html>

系统镜像下载地址:

<https://msdn.itellyou.cn/>

  
![image.png](https://image.3001.net/images/20180723/1532330095260.png!small)  

只需要把您需要用到的镜像的下载链接放到迅雷里即可

——————————————————————————————————————————————————————————————————

0x01首先认识一下OD(Ollydbg)

打开OD界面,呈现出下图的窗口分布,这里笔者对OD界面的几个窗口进行了一下标识。

  
![image.png](https://image.3001.net/images/20180723/15323301809434.png!small)  

1.菜单窗口:

  
![image.png](https://image.3001.net/images/20180723/15323301885541.png!small)  

从左往右依次去说这些按钮的作用以及快捷键:

(1) 打开新的可执行文件[快捷键F3]

(2) 重新载入程序[快捷键Ctrl+F2]

(3) 关闭程序 [快捷键Alt+F2]

(4) 运行程序[快捷键F9]

(5) 暂停执行程序 [快捷键F12]

(6) 单步步入[快捷键F7]

(7) 单步步过[快捷键F8]

(8) 跟踪步入[快捷键Ctrl+F11]

(9) 跟踪步过[快捷键Ctrl+F12]

(10) 执行到返回[快捷键Ctrl+F9]

(11) 转到反汇编窗中口的地址(转到表达式)[快捷键Ctrl+G]

(12) 显示记录窗口[快捷键Alt+L]

(13) 显示模块窗口[快捷键Alt+E]

(14) 显示内存窗口[快捷键Alt+M]

(15) 显示线程窗口

(16) 显示窗口

(17) 显示句柄窗口

(18) 显示CPU窗口[快捷键Alt+C]

(19) 显示补丁窗口[快捷键Ctrl+P]

(20) 显示调用堆栈窗口[快捷键Alt+K]

(21) 显示断点窗口[快捷键Alt+B]

(22) 显示参考窗口[快捷键Alt+R]

(23) 显示Run 跟踪窗口

(24) 显示源码窗口

(25) 调试选项(快捷键Alt+O)

(26) 界面选项

(27) 帮助

2.反汇编窗口:

为了演示方便笔者决定用C语言写个简单的Hello World!程序

代码如下:

![image.png](https://image.3001.net/images/20180723/15323302016583.png!small)  

将编译好的文件拖入OD

  
![image.png](https://image.3001.net/images/20180723/15323302416758.png!small)  

这里笔者对反汇编窗口进行了一下划分和标注:

  
![image.png](https://image.3001.net/images/20180723/15323302489784.png!small)  

这里面地址即为程序的内存地址,hex即为hex数据，反汇编就是程序的汇编代码，注释即为od分析出来的，双击即可编辑，信息窗口能对操作进行更加详细的查看。

3.寄存器窗口:

  
![image.png](https://image.3001.net/images/20180723/1532330255104.png!small)  

这里就简单介绍几个通用寄存器

ESP:指向堆栈栈顶

EBP:大部分用来定位局部变量和参数

其余的就各自拆开来用

这里面不低寄存器做更加深入的讲解，有兴趣的同学可以看看王爽的《汇编语言(第3版) 》。

另外, 点击标签寄存器 (FPU) 可以切换显示寄存器的方式

4.数据窗口:

  
![image.png](https://image.3001.net/images/20180723/15323302638979.png!small)  

数据窗口主要的即为程序或者内存的数据,右键可以切换显示方式

5.堆栈窗口:

  
![image.png](https://image.3001.net/images/20180723/15323302686131.png!small)  

主要存放线程的临时数据,可以用于动态调试.

6.命令行窗口:

  
![image.png](https://image.3001.net/images/20180723/15323302903424.png!small)  

主要就是执行一些下断命令

比如:bp+API函数名称

——————————————————————————————————————————————————

0x02 一些常用的操作

为了方便演示下面的操作,笔者写了一段代码来检测explorer.exe进程的程序

代码如下:

  

#include <windows.h>

#include <tlhelp32.h>

#include <stdio.h>

int main()

{

char* procressName = "explorer.exe";

char pName[MAX_PATH];

strcpy(pName, procressName);

CharLowerBuff(pName, MAX_PATH);

PROCESSENTRY32 currentProcess;

currentProcess.dwSize = sizeof(currentProcess);

HANDLE hProcess = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);

if (hProcess == INVALID_HANDLE_VALUE)

{

printf("函数CreateToolhelp32Snapshot调用失败!\n");

return FALSE;

}

BOOL bMore = Process32First(hProcess, ¤tProcess);

while (bMore)

{

CharLowerBuff(currentProcess.szExeFile, MAX_PATH);

if (strcmp(currentProcess.szExeFile, pName) == 0)

{

CloseHandle(hProcess);

printf("发现explorer.exe");

system("pause");

exit(0);

}

bMore = Process32Next(hProcess, ¤tProcess);

}

printf("没有发现explorer.exe\n");

CloseHandle(hProcess);

printf("Cracke Success!");

getchar();

return 0;

}

  

编译完成后运行

  
**![image.png](https://image.3001.net/images/20180723/15323303195278.png!small)**  

打开OD

1\. OD载入程序的两种方法

(1) 拖拽exe文件载入,这个很简单直接把exe文件拖拽到OD窗口中就行

(2) 进程附加,前提是你需要先运行所要附加的exe

a. 首先运行需要附加的exe

b.点击 文件->附加,找到需要附加的进程,选中后点击附加

  
**![image.png](https://image.3001.net/images/20180723/15323303274700.png!small)**  

2\. 字符串搜索方法

在反汇编窗口上点击右键->中文搜索引擎[根据需要你可以选取相应的筛选选项(1.搜索ASCII,2.搜索UNICODE,3.智能搜索)]

PS: ASCII 又叫ANSI 简写为A

UNICODE又叫WideChar 简写为W

程序API里面的A/W就是指的这两种编码

用刚刚那个检测explorer进程的exe为例子:

ASCII搜索:

  
**![image.png](https://image.3001.net/images/20180723/15323303341345.png!small)**  

UNICODE搜索:

![image.png](https://image.3001.net/images/20180723/15323303419401.png!small)  

智能搜索:

  
![image.png](https://image.3001.net/images/20180723/15323303483017.png!small)  

在这里面笔者推荐在搜索字符串的时候使用智能搜索

3\. 下断点以及删除断点:

(1).快捷键下断点(F2):用鼠标选中需要下段的代码，按一下F2

  
![image.png](https://image.3001.net/images/20180723/15323303544160.png!small)  

(2) 用鼠标选中代码右键 -> 断点 -> 切换

  
![image.png](https://image.3001.net/images/20180723/15323303662548.png!small)  

(3)命令行下断点:

a. 先找到需要下段的内存地址:

  
![image.png](https://image.3001.net/images/20180723/15323303881854.png!small)  

b. 在命令行窗口输入bp 内存地址

本程序中需要下段的内存地址为: 00B510EC输入命令: bp 00B510EC,回车

  
![image.png](https://image.3001.net/images/20180723/15323303934711.png!small)  

(4)删除断点

a.查看 –> 断点 然后就进入到显示断点窗口(快捷键 Alt+B)

  
![image.png](https://image.3001.net/images/20180723/15323303993476.png!small)  

b.用鼠标点击需要删除的断点右键删除即可

(PS:这里面断点的使用并不全面，这是做了一个简单的介绍而已)

4.保存文件

就以这个检测Explorer.exe的程序为例子

我们需要将程序改为直接输出Cracke Success!

首先搜索字符串找到Cracke Success!

  
![image.png](https://image.3001.net/images/20180723/15323304072791.png!small)  

双击字符串跟踪

  
![image.png](https://image.3001.net/images/20180723/15323304128264.png!small)  

往上翻一翻字符串会发现”没有发现explorer.exe\n”这段ASCII,用鼠标选中ASCII所在的代码,如图所示

这里面用白色圆形所传出来的是一段跳转，我们需要跟踪一下

（这里的红线代表的是跳转实现，而白线则是不实现。）

  
![image.png](https://image.3001.net/images/20180723/15323304182826.png!small)  

发现是从je short Checking.00B510EC跳转过来

  
![image.png](https://image.3001.net/images/20180723/15323304279410.png!small)  

这里面普及一下汇编的条件跳转指令:

jmp :无条件跳转 (jump)

je/jz :结果为0跳转 (jump zero)

jnz/jne: 结果不为0跳转 (jump not zero)

js:结果为负跳转 (Jump if sign)

jns:结果为正跳转(Jump if not sign)

jb:小于则跳转（Jump below）

jnb:大于或等于则跳转(Jump not below)

回到这个程序中,程序的意思就是调用CreateToolhelp32Snapshot函数去创造一个当前进程快照,利用ProcessFirst和
ProcessNext这两个API函数去遍历进程快照的进程并且与Explorer.exe做cmp,如果结果为真就不跳转,输出“

发现explorer.exe”,如果结果为假就跳转“没有发现explorer.exe Cracke Success!”

  
![image.png](https://image.3001.net/images/20180723/15323304351965.png!small)  

所以这其中的关键就在于遍历查找部分

  
![image.png](https://image.3001.net/images/20180723/15323304431603.png!small)  

用鼠标选中后，双击编辑

  
![image.png](https://image.3001.net/images/20180723/15323304493223.png!small)  

将条件跳转的je改为无条件跳转的jmp

  
![image.png](https://image.3001.net/images/20180723/15323304558541.png!small)  

右键 -> 复制到可执行文件 –> 所有修改

  
![image.png](https://image.3001.net/images/20180723/15323304612613.png!small)  

点击全部复制

  
![image.png](https://image.3001.net/images/20180723/15323304678615.png!small)  

右键后，找到保存文件

  
![image.png](https://image.3001.net/images/20180723/15323304745102.png!small)  

我们将其重命名为Cracker-Checking Explorer.exe

保存在桌面上

  
![image.png](https://image.3001.net/images/20180723/15323304792398.png!small)  

运行一下

  
![image.png](https://image.3001.net/images/20180723/15323304863658.png!small)  

这个检测进程就被我们绕过了

——————————————————————————————————————————————————

0x03 常用汇编指令扫盲

1.通用数据传送指令  
MOV（Move）传送

例如 mov a,b 就是把b的值传给a  
PUSH（Push onto the stack）进栈  
POP（Pop from the stack）出栈

注:push和pop由于堆栈平衡原理

有push就必须要有pop  
XCHG（Exchange）交换

2.标志寄存器传送指令  
PUSHF(push the flags) 标志进栈  
POPF(pop the flags) 标志出栈

3.条件跳转(一般配合cmp使用)

JMP(jump) 无条件跳转  
JZ/JE(Jump if zero,or equal) 结果为零(或相等)则跳转 注：检测Z位

JNZ/JNE(Jump if not zero,or not equal) 结果不为零(或不相等)则跳转 注：检测Z位

JS(Jump if sign) 结果为负则跳转 注：检测S位

JNS(Jump if not sign) 结果为正则跳转 注：检测S位

JB(Jump Below):小于则跳转 注：检测C位

JNB(Jump Not Below ):大于或等于则跳转 注：检测C位

那这些C位,Z位，S位在哪里看呢?

在0x01认识OD中在寄存器窗口中认识了标志寄存器,如图:

  
![image.png](https://image.3001.net/images/20180723/15323304948969.png!small)  

这里用jnz去举例,jnz的判断检查Z位，当Z位是0的时候就不跳转，在Z为是1的时候就跳转

  
![image.png](https://image.3001.net/images/20180723/15323305006854.png!small)![image.png](https://image.3001.net/images/20180723/1532330504103.png!small)  

4.子程序  
CALL 调用指令  
RET 返回指令

5.LOOP 循环指令

6.算数指令

ADD 加法指令

SUB 减法指令

SUBR 减法指令

MUL 乘法指令

DIV 除法指令

DIVR ;除法指令

7.nop 空指令

0x04 总结

本篇文章介绍了OD 的基础使用,以及一些基础操作

介绍了一些常用的汇编指令,如果有哪些常用的汇编指令没有补充到位的以及文章中出现瑕疵的地方欢迎在评论区中指出，我会及时审改的

  

[阅读原文](https://bbs.ichunqiu.com/thread-43041-1-1.html?from=beef)可下载附件，附件中有本篇文章的例子以及一个演示例子[。](https://bbs.ichunqiu.com/thread-43041-1-1.html?from=beef)

