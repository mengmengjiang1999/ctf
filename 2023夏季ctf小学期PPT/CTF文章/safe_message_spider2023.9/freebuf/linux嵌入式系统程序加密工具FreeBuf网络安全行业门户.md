linux嵌入式系统程序加密工具推荐：Virbox Protector.

## 软件开发商

Virbox Protector是由北京深思数盾科技股份有限公司研发，2018年上市的一款加密工具。

## ARM-Linux程序加密效果

![arm1.jpg](https://image.3001.net/images/20200618/1592446974_5eeacffe90344.jpg!small)  

## Virbox Protector加密技术

1.代码混淆，行业前沿的加密技术：指令集混淆，可以自由选择保护的函数，对指定函数进行“ARM指令级”的混淆，对编译后的ARM指令进行等价变换、多分支、花指令等手段，防止IDA反编译，同时极大地增加了动态分析的难度。相比使用基于LLVM编译器的混淆，基于ARM指令的混淆能以更少的指令达到更强的保护效果，耗电量更小。

2.代码加密.可以对指定函数进行代码片加密，只有程序运行的时候才能解密，破解者无法 Dump 出整体的内存，有效防止逆向工程工具对程序进行静态分析。

3.智能压缩。隐藏程序中的代码和数据，阻止 IDA PRO
等工具的反编译，并且有效的防止了加壳后的应用体积膨胀。加密后程序运行效率高，仅在程序被加载时轻微的性能损失。

4.反调试。包括检测调试器功能，主要防止保护后的程序被反编译工具(如gdb、IDA等)进行调试。

## 加密支持

支持arm32,arm64,x86,x64多种CPU架构

## 软件试用

Virbox
Protector提供全功能的试用版测试。试用版下载链接：[https://shell.virbox.com/apply.html](https://links.jianshu.com/go?to=https%3A%2F%2Fshell.virbox.com%2Fapply.html)

  

