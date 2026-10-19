首先的首先 2021年各位新年好 这是我2021年第一篇帖子

### 0x0 我们要实现什么

1 启动时无驱动程序运行  
2 没有线程创建时注入作弊游戏  
3\. 当我们完成注入时，内存中没有私有标志  
它将最小化内部检测的检测向量

### 0x1 背景

关于COW:

系统中存在一个叫做cow的机制 国外大神@can1357的perfect injecter帖子说的很清楚了:

> CoW是操作系统用来节省内存的一种技术，它使进程共享某些物理内存区域，直到它们真正被编辑。  
>
> 我们知道这一点ntdll.dll为每个进程加载，并且它的代码（.text）区域很少被修改（如果有的话），那么为什么要为它一次又一次地为数百个进程分配物理内存呢？这正是现代操作系统使用CoW技术的原因。  
> 实现非常简单：  
> 当一个PE文件被映射时，如果它也被映射到其他进程，并且它的VA在当前进程上也是空闲的，那么只需复制PFN并将标志设置为只读。  
> 当由于指令试图在页上写入而发生页错误时，请分配新的物理内存，设置PTE的PFN并删除只读标志。

综上所述：当我们更改了cow标志时，物理内存将比更改应用于全局，直到重新启动系统

![](https://image.3001.net/images/20210101/1609501112_5fef09b84f36883081379.png!small)

关于反作弊如何阻止dll：  
大多数反游戏（除了EAC）使用minifilter来过滤游戏加载文件。当一个PE文件被游戏访问时，minifilter回调将被激活,
然后反作弊驱动程序将文件路径和信息反馈给R3
anticheat（EasyAntiCheat.exe以及BEService.exe)R3反作弊会调用CreateFile读取要访问的PE文件并检查签名，如果不是白名单签名，它将被阻止加载.

### 0x2 实现COW注入器

首先定位cow物理内存:

![](https://image.3001.net/images/20210101/1609501380_5fef0ac45d990f4b75730.png!small)

获取cow模块地址和空间

![](https://image.3001.net/images/20210101/1609501419_5fef0aebd1939ae05a54b.png!small)

现在我们有了kernel32.dll、kernelbase.dll、ntdll.dll地址。当我们改变内存时，它将通过cow机制实现全局应用

  
3\. 写shellcode

![](https://image.3001.net/images/20210101/1609501451_5fef0b0b72ad3de12c28d.png!small)  
我写一个简单的createfileW hook,游戏开始时候会调用createfileW,此时我们会loadlibrary我们的dll
之后R3反作弊也会调用createfileW去检查文件数字签名,这个时候我们把createfilew读的文件换成ntdll.dll:你可以看到这里面有一些是
0x1234567812345678 这种无效地址,这种是给接下来定位用的

我不想滥用像perfect
inject这样的windows地址限制机制，所以我们需要找到一个可用内存（VAD中需要执行标志），并使用它保存shellcode：

![](https://image.3001.net/images/20210101/1609501344_5fef0aa038a96e02041e9.png!small)

如果一切顺利，我们可以得到一个空闲内存，可以容纳我们的shellcode和cow标志模块地址。  
请注意，我尝试将外壳代码直接放入只读地址（因为它更大）并对其进行修改PTE.noexcute=0尝试使页可执行，但是发现没软用。因为似乎即使物理地址相同，PTE属性也不同  
现在让我们获取导出函数以满足hook的需要：然后，最重要的是，自己手写hook：  
我们需要手写hook，这是非常痛苦的  
在win7中kernel32.createfileW是一个函数，但在win10中它是一个jmp origin_to_kernelbase.dll
这个代码困扰了我很长时间，直到我发现两个系统之间的差异。  
用一张图片来解释我们要钩什么：

![](https://image.3001.net/images/20210101/1609501148_5fef09dc3d3b0978c7bd9.png!small)

代码:

![](https://image.3001.net/images/20210101/1609501292_5fef0a6cc16e6b349a668.png!small)

然后我们将在shellcode中找到地址并传递正确的函数地址（这就是为什么我们需要写 0x123456789地址）：

![](https://image.3001.net/images/20210101/1609501268_5fef0a5432b015394efa2.png!small)

最后 hook:

![](https://image.3001.net/images/20210101/1609501241_5fef0a39181feba5c0ae9.png!small)

总结一下：  
0 手写shellcode  
1 加载我们的驱动程序  
2 获取kernelbase ntdll kernel32地址  
3 通过遍历pe头查找导出函数  
4 找到一个空间来保存我们的shellcode  
5 重新定位shellcode函数地址  
6 钩子Kernelbase.CreatefileW文件  
7 当游戏开始时，shellcode调用并加载我们的外挂dll，当反作弊调用createfilew时，给出一个假的ntdll路径

" **Now they will be afraid of you:** "(doom的梗)

![](https://image.3001.net/images/20210101/1609501160_5fef09e89189492261aa2.png!small)![](https://image.3001.net/images/20210101/1609501172_5fef09f4e706404a5e5b6.png!small)

  

  

**地址:[https://github.com/huoji120/CowInjecter﻿](https://github.com/huoji120/CowInjecter)**

注意事项:  
可以看出，滥用cow机制不仅可以实现注入，而且具有很大的潜力，包括不局限于绕过硬件禁止，修改签名检查功能，甚至劫持句柄, 你想怎么搞就怎么搞  
请注意：  
你不能只是复制一个函数作为shellcode，gcc会破shellcode，所以你需要像这样在R3中生成shellcode并把它放到驱动程序中：

![](https://image.3001.net/images/20210101/1609501211_5fef0a1bbddb43b8080ca.png!small)

