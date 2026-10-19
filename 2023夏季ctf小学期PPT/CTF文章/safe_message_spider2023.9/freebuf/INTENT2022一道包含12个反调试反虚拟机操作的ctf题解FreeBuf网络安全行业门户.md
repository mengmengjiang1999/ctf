# 从一道Re题学习12种反调试反虚拟技术

题目：AntiDebuggingEmporium

来源：INTENT CTF 2022 Re

这个题目很有意思，里面出现了总共12个反调试反虚拟机的操作，本文内容分两部分，前部分是题解，后部分是这12个反调试反虚拟机手法分析

## 题解

### 程序逻辑分析

文件信息：是个64位的Windows控制台程序，VS2022编译的。

![](https://image.3001.net/images/20221228/1672215112_63abfa484a790c1f0d044.png!small)

主函数：![](https://image.3001.net/images/20221228/1672215112_63abfa48de5a0dc0d4cba.png!small)

可以看到，逻辑很简单。

1.首先是调用一个函数等待一个对象执行完成

2.然后提示输入flag，

3.对一个数组的值进行判断，如果所有的值都是0，则处理输入字符串输出flag

这里去看看这个数组的值来自哪里：

通过交叉引用，发现这个数组在多个地方被赋值，基本上均在StartAddress这个函数里。

![](https://image.3001.net/images/20221228/1672215113_63abfa498e1db237d3ae0.png!small)

经分析，这里的这个数组保存的就是检测虚拟机和调试器的情况，检测到了则会有值被赋值为1：

![](https://image.3001.net/images/20221228/1672215114_63abfa4a422f066beedc1.png!small)

这个函数首先从当前文件的资源里读取了二进制数据，保存起来，然后进行了累计12个反虚拟机和反调试的函数，这部分内容我们在后文进行详细分析。

随便点开一个：

![](https://image.3001.net/images/20221228/1672215115_63abfa4b145373b9351ee.png!small)

可以看到，这里对一个数组的某个位置进行赋值了，这个赋值后面会用到，现在看一下StartAddress这个函数是在什么时候被调用的：

![](https://image.3001.net/images/20221228/1672215115_63abfa4beb755609f5fea.png!small)

  

通过交叉引用可以看到，在TLS回调函数中调用，TLS回调函数会在主函数执行前先执行，这里的hHandle就是主函数里等待的对象。也就是说，这个程序会先进行反调试反虚拟机的操作，然后检测完之后，获取用户输入，进行处理。

接下来看用户输入是被如何处理的：

![](https://image.3001.net/images/20221228/1672215116_63abfa4ca85311c8ded2b.png!small)

这里首先是用资源二进制数据和一个数组的对应值进行相加（这个数组的值就是反调试函数里检测成功后赋值的）。

然后进行校验，校验是通过异或进行的，这里用到一个哈希值，这个哈希值是对资源数据进行校验得到的，不去修改资源，则这里是固定值，所以可以直接动态调试得到这个值，然后异或用户输入，结果是资源数据计算后的值。

逻辑理清楚了，现在要做的事情就是：

1.拿到资源二进制数据

2.拿到反调试数组

3.拿到哈希值

4.计算flag

### 拿到资源数据

直接从die中就能得到：

![](https://image.3001.net/images/20221228/1672215117_63abfa4d60ac2484d5d6f.png!small)

### 拿到反调试数组和哈希值

把程序在物理机上跑起来，让程序卡在scanf里，这个时候调试器和虚拟机的检测已经结束了，反调试数组应该也计算好了。这个时候直接调试器附加，查看数组的地址：14000DBE0。

![](https://image.3001.net/images/20221228/1672215118_63abfa4e06c011dca3fa9.png!small)

拿到64字节的数据，哈希值也是保存在全局变量里的，可以直接拿到地址000000014000DB88，去查看即可：![](https://image.3001.net/images/20221228/1672215118_63abfa4e669dc4f6de29a.png!small)

### 计算flag

该有的都有了，写代码生成flag即可：

// antidebuggingemporium.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。  
//  
#include  
#include  
#include  
unsigned char RescourceData[68] = {  
0x72, 0x6C, 0xCA, 0x03, 0x75, 0x76, 0xE5, 0x00, 0x00, 0x43, 0x00, 0x00, 0x55,
0x16, 0xEA, 0x77,  
0x0B, 0x4C, 0xC1, 0x77, 0x48, 0x7D, 0x00, 0x00, 0x00, 0x7D, 0x00, 0x00, 0x00,
0x5B, 0xC1, 0x31,  
0x08, 0x43, 0xEE, 0x76, 0x55, 0x7D, 0xAF, 0x28, 0x64, 0x15, 0xF6, 0x75, 0x64,
0x00, 0x00, 0x00,  
0x64, 0x00, 0x00, 0x00, 0x52, 0x4C, 0xED, 0x71, 0x64, 0x00, 0x00, 0x00, 0x00,
0x00, 0xEA, 0x3F,  
0x46, 0x22, 0x3F, 0x46  
};  
  
unsigned char antiDbgNum[68] = {  
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x77, 0x56, 0x00, 0xF9, 0x77, 0x00,
0x00, 0x00, 0x00,  
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xA9, 0x2E, 0x08, 0x00, 0xAE, 0x28, 0x57,
0x00, 0x00, 0x00,  
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x55, 0xAA, 0x34,  
0x00, 0x16, 0xF9, 0x27, 0x00, 0x00, 0x00, 0x00, 0x00, 0x50, 0xAD, 0x27, 0x57,
0x13, 0x00, 0x00,  
0x00, 0x00, 0x00, 0x00  
};  
unsigned char flag[68] = { 0 };  
unsigned int hashsum = 0x469E223B;  
int main()  
{  
for (int i = 0; i < 68; ++i)  
{  
RescourceData[i] += antiDbgNum[i];  
}  
for (int j = 0; j < 68; j +=4)  
{  
*(DWORD*)&flag[j] = (hashsum ^ *(DWORD*)&RescourceData[j]);// 00000000469E223B  
}  
printf("%s", flag);  
}  
// INTENT{1mag1n4t10n_1s_7h3_0nly_w3ap0n_1n_7h3_w4r_4gains7_r3al1ty}

## 反调试反虚拟机手法分析

这里依次分析那12个反调试反虚拟机的函数。

### 0x0-反虚拟机-检测CPU核心数![](https://image.3001.net/images/20221228/1672215118_63abfa4ee04b68e606ef9.png!small)

这里通过GetSystemInfo
API获取系统信息，这里判断系统的处理器核心数量，现在的用户电脑CPU核心都是4核往上的，一般只有在虚拟机里可能会遇到只分配了1核的情况。

### 0x1-反调试器-检测PEB标志位1![](https://image.3001.net/images/20221228/1672215119_63abfa4f78447f58ee3b5.png!small)

看到这个+2偏移就很容易想到PEB里的BeingDebugged标志位。不过这里是使用ZwQueryInformationProcess获取PEB的：![](https://image.3001.net/images/20221228/1672215120_63abfa5000d26ef43e30f.png!small)

### 0x2-反调试器-检测PEB标志位2![](https://image.3001.net/images/20221228/1672215120_63abfa508849a13504897.png!small)

这个写的更直接，这个NtCurrentPeb()本质上就是从gs[0x60]处取值，得到的就是peb地址，这里检测的依然是BeingDebugged标志位

### 0x3-反调试器-检测PEB标志位3![](https://image.3001.net/images/20221228/1672215121_63abfa51198987b02746e.png!small)

这里使用了PEB的另一个标志位NtGlobalFlag，位置是偏移0xBC的地方，这里IDA的F5显示有问题，在反汇编里可以到是：add rax,
0BCh。

### 0x4-反调试器-检测PEB标志位4![](https://image.3001.net/images/20221228/1672215121_63abfa51a95d38ca9446d.png!small)

通过API的方式检测PEB偏移2位置的BeingDebugged的值。

### 0x5-反虚拟机-cpuid
1![](https://image.3001.net/images/20221228/1672215122_63abfa523cb11cc667970.png!small)

cpuid指令，通过rax传递功能号，将返回值保存在eax，ebx，ecx，edx里。当功能号是1的时候，ecx的最高位表示当前是否在虚拟机里。

### 0x6-反虚拟机-cpuid
0x40000000![](https://image.3001.net/images/20221228/1672215122_63abfa52b77ca615b72b3.png!small)

当功能号是0x40000000时，rbx rcx
rdx里返回的是一个cpu名称。![](https://image.3001.net/images/20221228/1672215123_63abfa5342513a0b6e2c3.png!small)

然后接下来检测是否是常见的虚拟机的cpu名称。

### 0x7-反虚拟机-cpuid
0![](https://image.3001.net/images/20221228/1672215124_63abfa5404fe4bf0f7823.png!small)

功能号是0时候，是另一种显示cpu相关信息的方法，依然是检测是否出现虚拟机常见字符。

### 0x8-反调试器-rdtsc![](https://image.3001.net/images/20221228/1672215124_63abfa54733d575e2f232.png!small)

通过rdtsc指令获取时间，当两次获取时间间隔过大，可以认为有调试器干扰了程序的正常执行。

### 0x9-反调试器-窗口检测![](https://image.3001.net/images/20221228/1672215125_63abfa55363b6fdb0a359.png!small)

检测是否存在调试器的窗口，如果存在，则认为有调试行为。

### 0xA-反调试器-异常处理

  

![](https://image.3001.net/images/20221228/1672215125_63abfa55bc9c7379cb346.png!small)

这里使用SetUnhandledExceptionFilter API设置无法处理的异常的处理函数。

通常情况下，当异常无法处理的时候会进入该函数去处理，但是有调试器存在，则会直接由调试器接管，不进入该函数.

处理的内容是：

![](https://image.3001.net/images/20221228/1672215126_63abfa5637987a0c8c471.png!small)

效果是跳过某些指令往下执行：

![](https://image.3001.net/images/20221228/1672215126_63abfa56b859a1411516b.png!small)

这里跳过了这个jmp，以至于下面的0x57能正常赋值到数组里。

### 0xB-反虚拟机-设备检测

![](https://image.3001.net/images/20221228/1672215127_63abfa5777e7b87706723.png!small)

这里通过API：SetupDiGetClassDevsExW 获取设备集，然后通过API：SetupDiEnumDeviceInfo 枚举设备

使用API：SetupDiGetDeviceRegistryPropertyW 对每一个设备获取其属性。

![](https://image.3001.net/images/20221228/1672215128_63abfa58182861ec6de3f.png!small)

对获取到的信息，去判断是否包含这几个虚拟机相关的特征字符串，来判断是否位于虚拟机内部。

作者：selph

