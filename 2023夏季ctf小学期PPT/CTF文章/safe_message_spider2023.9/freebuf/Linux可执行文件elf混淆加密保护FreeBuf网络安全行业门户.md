ELF 全称 “Executable and Linkable Format”，即可执行可链接文件格式，目前常见的Linux、
Android可执行文件、共享库（.so）、目标文件（ .o）以及Core 文件（吐核）均为此格式。

那么如何对elf文件进行加密呢？这里推荐一款代码加密工具：Virbox Protector。直接将elf文件直接拖到Virbox
Protector加密工具里，选择函数，然后设定保护方式，然后一键加密。能快速的完成代码加密保护。提供工具和命令行操作，编译、加壳一体化快速完成

## Virbox Protector 加密技术

1.代码混淆，行业前沿的加密技术：指令集混淆，可以自由选择保护的函数，对指定函数进行“ARM指令级”的混淆，对编译后的ARM指令进行等价变换、多分支、花指令等手段，防止IDA反编译，同时极大地增加了动态分析的难度。相比使用基于LLVM编译器的混淆，基于ARM指令的混淆能以更少的指令达到更强的保护效果，耗电量更小。

2.代码加密.可以对指定函数进行代码片加密，只有程序运行的时候才能解密，破解者无法 Dump 出整体的内存，有效防止逆向工程工具对程序进行静态分析。

3.智能压缩。隐藏程序中的代码和数据，阻止 IDA PRO
等工具的反编译，并且有效的防止了加壳后的应用体积膨胀。加密后程序运行效率高，仅在程序被加载时轻微的性能损失。

## Virbox Protector支持的架构：

支持arm32,arm64,x86,x64多种CPU架构

## 代码混淆保护效果图

ARM 架构程序保护前，如图所示：

![webp](https://image.3001.net/images/20200421/1587462121_5e9ebfe91f05b.png!small)  

  

ARM 架构程序保护后，如图所示：

![webp](https://image.3001.net/images/20200421/1587462132_5e9ebff423602.png!small)  

 **代码加密保护效果图**

保护前，如图所示：

![webp](https://image.3001.net/images/20200421/1587462208_5e9ec04026090.png!small)

保护后，如图所示：

![webp](https://image.3001.net/images/20200421/1587462215_5e9ec0470a1a2.png!small)

 **压缩前后效果对比图**

保护前，如图所示：

![webp](https://image.3001.net/images/20200421/1587462221_5e9ec04dbec42.png!small)

保护后，如图所示：

![webp](https://image.3001.net/images/20200421/1587462229_5e9ec055a76d5.png!small)

## 试用版下载地址：

[http://dl.download.virbox.com/vps/10807/virboxprotector_trial_1.5.0.10808_windows.exe](https://links.jianshu.com/go?to=http%3A%2F%2Fdl.download.virbox.com%2Fvps%2F10807%2Fvirboxprotector_trial_1.5.0.10808_windows.exe)

官网：shell.virbox.com

试用版授权码：J6AJ-TLJM-3CUB-3S8K

授权码快速使用教程：

![webp](https://image.3001.net/images/20200421/1587462313_5e9ec0a9bf222.gif!small)

开始加密

![开始加密.gif](https://image.3001.net/images/20200421/1587462515_5e9ec17329d2b.gif!small)  
  

##  

  

