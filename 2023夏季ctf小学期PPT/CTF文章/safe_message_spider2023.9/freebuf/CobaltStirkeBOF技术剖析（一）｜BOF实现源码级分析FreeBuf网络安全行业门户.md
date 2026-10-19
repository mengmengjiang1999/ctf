## 简介

对BOF(Beacon Object
File)的支持是在CobaltStrike4.1版本中新引入的功能。BOF文件是由c代码编译而来的可在Beacon进程中动态加载执行的二进制程序。无文件执行与无新进程创建的特性更加符合OPSEC的原则，适用于严苛的终端对抗场景。低开发门槛与便利的内部Beacon
API调用与使得BOF特别适合后渗透阶段攻击工具的快速开发与移植。

## BOF本质-OBJ文件

当我们通过file命令查看编译后的BOF文件，我们会发现它是一种名为COFF的文件格式。在Windows操作系统中编译产生的.obj中间文件使用的便是这种格式的文件，也可以作为BOF在cobaltstrike中被正确执行。

Intel amd64 COFF object file, no line number info, not stripped, 7 sections,
symboloffset=0x1330, 212 symbols

利用PEView等工具可以观察其结构：

![1627549288_61026e6818694194966bb.png!small?1627549291135](https://image.3001.net/images/20210729/1627549288_61026e6818694194966bb.png!small?1627549291135)

在.text段存在编译完成的代码

![1627549308_61026e7caa23cc8ee5fcf.png!small?1627549311551](https://image.3001.net/images/20210729/1627549308_61026e7caa23cc8ee5fcf.png!small?1627549311551)

通过如下命令可以调用cobaltstrike自带的BOF解析函数查看BOF文件的属性，及其中的重定向信息。

![1627549330_61026e92aa793dc6193df.png!small?1627549333641](https://image.3001.net/images/20210729/1627549330_61026e92aa793dc6193df.png!small?1627549333641)

![1627549337_61026e99dae1ccb1f541e.png!small?1627549340759](https://image.3001.net/images/20210729/1627549337_61026e99dae1ccb1f541e.png!small?1627549340759)

## BOF执行过程分析

cobaltstrike将一部分对BOF文件的处理在客户端程序中完成，传输至beacon的已经是解析过的数据。将bof文件的解析前置到客户端完成一方面减少了Beacon侧的代码，另外一方面也避免了诸如文件Magic头之类BOF文件本身存在的特征被应用于内存检测中。

![1627549377_61026ec124801c12c697f.png!small?1627549380081](https://image.3001.net/images/20210729/1627549377_61026ec124801c12c697f.png!small?1627549380081)

对于重定向表的处理是此步骤的核心，对.rdata、.data、.text段的重定向在此处未作过多处理，而对符号表中的函数则进行了分类处理。一类函数是Beacon中内置的函数，另一类函数则需要由Beacon动态解析函数地址。

###
![1627549392_61026ed09cc6c1ca12a03.png!small?1627549395535](https://image.3001.net/images/20210729/1627549392_61026ed09cc6c1ca12a03.png!small?1627549395535)

###  **BOF内部API**

在Beacon内部存在着BOF可调用的一系列内部API，在解析内部函数的地址时直接以函数数组的形式去计算内部地址。

![1627549417_61026ee97c161f2188c5a.png!small?1627549420543](https://image.3001.net/images/20210729/1627549417_61026ee97c161f2188c5a.png!small?1627549420543)

BOF C API共有以下几类：

Win32 API-主要用于函数动态解析

LoadLibraryA、FreeLibrary、GetProcAddress、GetModuleHandleA

数据解析API-用于从bof_pack打包的数据中提取函数参数

BeaconDataParse、BeaconDataPtr等

内容格式化API-辅助构造大型或重复性的输出

BeaconFormatAlloc、BeaconFormatReset等

打印输出API-将结果返回cobaltstrike控制端

BeaconOutput、BeaconPrintf等

Beacon 内部API-一些功能性的API，包括token操作、派生进程、进程注入等

BeaconUseToken、BeaconRevertToken、BeaconSpawnTemporaryProcess等

辅助性API

toWideChar-将多字节字符串转换为宽字符字符串

 **核心特性-动态函数解析DFR**

Dynamic Function Resolution(动态函数解析
DFR)是cobaltstrike在BOF文件解析中提供的特性，它支持动态解析并调用DLL的导出函数。动态解析的过程在beacon执行BOF的过程中完成。

![1627549461_61026f15cf87aa8ba5a4b.png!small?1627549464676](https://image.3001.net/images/20210729/1627549461_61026f15cf87aa8ba5a4b.png!small?1627549464676)

通过对beacon的逆向可知，DFR依然是利用GetModuleHandleA、LoadLibraryA、GetProcAddress这几个函数去动态解析函数地址，与直接调用这几个函数没有本质区别，但为函数的动态解析提供了一种简便的方法。

![1627549489_61026f31508aca870b82d.png!small?1627549492127](https://image.3001.net/images/20210729/1627549489_61026f31508aca870b82d.png!small?1627549492127)

###  **技巧-活用DFR导入libc函数**

在cobaltstrike官方文档中称：“由于不会将BOF链接到libc，strlen,strcmp等通用函数将无法使用”。但利用DFR的特性，我们可以通过直接调用msvcrt.dll中导出的标准c函数。

## BOF的优点

1\. 内存中不落地执行，避免针对文件内容的检测

2\. 在本进程加载执行BOF中的功能代码，规避了针对进程创建的检测（更符合opsec安全）

3\. 低成本地迁移由c编写的小型后渗透工具

4\. 基于BOF.NET等项目可以在避免创建新进程的情况下实现.NET程序加载执行

## BOF的局限性

1\. 不支持解析bss段，因此不能正确解析未手动初始化的全局变量（必须以非0值进行初始化）

2\. 若执行的BOF程序的执行错误将导致整个进程崩溃

3\. BOF执行期间将阻塞beacon进程，不能执行其他任务，也不会返回信息（若BOF执行进入死循环则session无响应）

4\. 不适于长时间运行的大型程序，对多线程没有官方支持

## 优秀BOF项目集合

1\. FindObjects-BOF：利用直接系统调用枚举具有特定模块或句柄的进程

<https://github.com/outflanknl/FindObjects-BOF>

2\. Situational Awareness BOF：提供了一些常用的信息收集命令的BOF实现（例如sc_query）

<https://github.com/trustedsec/CS-Situational-Awareness-BOF>

3\. BOF.NET：为Beacon BOF文件提供的.NET运行时

<https://github.com/CCob/BOF.NET>

## 参考

[https://www.cobaltstrike.com/help-beacon-object-files
](https://www.cobaltstrike.com/help-beacon-object-files)

[https://www.trustedsec.com/blog/a-developers-introduction-to-beacon-object-files/ ](https://www.trustedsec.com/blog/a-developers-introduction-to-beacon-object-files/)

[https://wbglil.gitbook.io/cobalt-strike/cobalt-strike-yuan-li-jie-shao/untitled-3 ](https://wbglil.gitbook.io/cobalt-strike/cobalt-strike-yuan-li-jie-shao/untitled-3)

<https://blog.cobaltstrike.com/2017/06/23/opsec-considerations-for-beacon-commands/>

