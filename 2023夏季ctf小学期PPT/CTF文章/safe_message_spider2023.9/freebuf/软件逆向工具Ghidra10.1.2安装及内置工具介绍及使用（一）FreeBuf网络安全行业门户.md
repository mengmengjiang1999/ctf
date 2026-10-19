![](https://image.3001.net/images/20220319/1647679083_6235966b4dd8600f4b85d.png!small)

## 1 软件介绍

Ghidra
是美国国家安全局(RSA)开源发布的软件逆向工程框架，涵盖了反汇编、反编译等工具。该工具2019年3月开源。与之对标的有windows平台下的IDA
Pro和linux平台下的radare2等。  
2022年1月发布10.1.2版本。  
10.1.2更新内容:  
1.修复了Log4j漏洞。  
2.更新Debugger工具。

2.1该工具添加动作模拟程序，p-code模拟程序，它使用映射的当前程序启动一个空白跟踪，让后用户可以在“线程”窗口中使用通常的“模拟步骤”动作进行步进操作。例如，语言开发人员可以组装一个需要测试的指令，用光标在该指令处开始模拟，然后再“p-code
step”窗口中步进单个的p-code操作.

2.2添加LLDB支持。为了调试macOS目标，添加了对LLDB的支持。目前，在用户端需要做一些工作来克隆、打补丁和构建带有Java语言绑定的LLDB。完成之后，LLDB的新连接器就可以以正常方式使用了。虽然这些连接器是为macOS设计的，但它们也可以在Linux上工作，也可以在Windows上工作。这为那些更喜欢lldb而不是gdb的人提供了另一种选择。

2.3导入和分析到版本12的全部现有的(几乎)Android二进制文件集。现在支持X。支持的二进制文件类型包括:Android runtime
(ART)、Ahead-of-Time (OAT)/ELF、Dalvik Executables (DEX)、Compact DEX
(CDEX)、Verified DEX (VEX)、Boot Image和Boot
Loader格式。还包括DEX文件的Sleigh模块覆盖每个主要的Android版本;优化后的指令因版本不同而不同。现在，当导入DEX文件时，您可以选择适合Android版本的Dalvik语言，这将导致更好的分析。

## 2 软件安装

### 2.1 软件下载

> [https://github.com/topics/ghidra ](https://github.com/topics/ghidra)

### 2.2 java环境配置(jdk版本>=11)

2.2.1 Linux安装（以Ubuntu18为例）

> sudo apt install openjdk-11-jkd
>
> java -version

![](https://image.3001.net/images/20220319/1647679064_623596589ae16aa1ada8b.png!small)2.2.2
Windows安装（以windows7为例）

下载链接：

> <https://www.oracle.com/java/technologies/downloads/#jdk17-windows>

默认安装后需要配置环境变量。

我的电脑右键->属性->高级系统设置->环境变量

> 1.新建变量名：JAVA_HOME
>
> 内容：C:\Program Files (x86)\Java\jdk17 （具体以个人安装路径为准）  
> 2.新建变量名：CLASSPATH  
> 内容：.;%Java_Home%\bin;%Java_Home%\lib\dt.jar;%Java_Home%\lib\tools.jar;
> （注意以.开始）  
> 3.编辑Path  
> 内容  
> %Java_Home%\bin;%Java_Home%\jre\bin;  
> 4.在命令行输入java -version

![1647679464_623597e86a6ddbff8aab3.png!small?1647679465695](https://image.3001.net/images/20220319/1647679464_623597e86a6ddbff8aab3.png!small?1647679465695)

## 3 软件使用

### 3.1 主界面

以windows7使用为例，运行ghidraRun.bat

###
![](https://image.3001.net/images/20220319/1647679562_6235984a7f8f77466386e.png!small)

软件使用需要新建工程，并在工程内导入需要逆向的二进制文件。

### 3.2 CodeBrowser工具介绍

3.2.1 Listing 窗口

CodeBrowser工具是静态逆向工具，迭代版本比较多。

![](https://image.3001.net/images/20220319/1647679804_6235993c688f5a4fdfe36.png!small)3.2.2
Program Trees 程序树窗口

![](https://image.3001.net/images/20220319/1647679848_62359968c175dd7d8f4cc.png!small)程序树展示了PE文件的段的结构。点击可快速跳转至相应地址。

3.2.3 Symbol Tree 符号树窗口

![](https://image.3001.net/images/20220319/1647680035_62359a238b64c8536d97a.png!small)Imports类别包含了代表外部库命名空间的符号。  
Function包含了代表程序中函数的符号（除外部函数外）  
Class包含了那些可能包含函数命名空间或标记符号的类的命名空间  
namespace包含了全局命名空间的中通用命名空间，也可能包含类、函数、标记或者其他命名空间。

3.2.4 Functions 函数窗口

![1647680236_62359aece6c7d8cca7dbc.png!small?1647680238225](https://image.3001.net/images/20220319/1647680236_62359aece6c7d8cca7dbc.png!small?1647680238225)

functions函数窗口，可以查看反汇编得到的函数。由于Ghidra没有如IDA Pro强大的资源库，无法识别一些库函数。

3.2.5 Defined String 字符串窗口

![1647680347_62359b5b1d893b1f8bd35.png!small?1647680348458](https://image.3001.net/images/20220319/1647680347_62359b5b1d893b1f8bd35.png!small?1647680348458)

字符串窗口可以查到所有的字符串。

3.2.6 Function Call Graph函数调用图

![1647680380_62359b7c170636beb8f95.png!small?1647680381301](https://image.3001.net/images/20220319/1647680380_62359b7c170636beb8f95.png!small?1647680381301)

该功能能够十分清晰得到函数的调用关系。

3.2.7 Decompile 反编译窗口

![1647680423_62359ba79950c01a308c1.png!small?1647680424894](https://image.3001.net/images/20220319/1647680423_62359ba79950c01a308c1.png!small?1647680424894)

Ghidra和IDA Pro一样具有反编译功能，快捷键为Ctrl + E。在不安装插件的情况下，Ghidra的优化没有IDA Pro强大。

3.2.9 Undo和Redo功能

![1647680626_62359c726c4dd6358ba5f.png!small?1647680627663](https://image.3001.net/images/20220319/1647680626_62359c726c4dd6358ba5f.png!small?1647680627663)

点击左右箭头可以进行撤销和重做功能。

3.2.10 Memory Map 内存映射窗口

![1647680704_62359cc0ef23a836e00ea.png!small?1647680706267](https://image.3001.net/images/20220319/1647680704_62359cc0ef23a836e00ea.png!small?1647680706267)

内存映射窗口展示了当前的内存结构，包含了

> Name：段名
>
> Start：起始
>
> End：终止地址
>
> Length：长度
>
> R、W、X：读、写、执行权限
>
> Type：指示内存区块的类型（Default、Bit Mapped、Byte Mapped或是Overlay）
>
> Source：按照文件导入器生成这些字节填充该区块的文件名字。对于类别为Bit Mapped或是Byte
> Mapped的区块，Source会显示映射的源地址

3.2.11 Navigation 跳转功能

![1647680965_62359dc58fd9a1cdfe934.png!small?1647680966828](https://image.3001.net/images/20220319/1647680965_62359dc58fd9a1cdfe934.png!small?1647680966828)

![1647680925_62359d9da15318f193c7d.png!small?1647680926866](https://image.3001.net/images/20220319/1647680925_62359d9da15318f193c7d.png!small?1647680926866)

Ghidra也提供了强大跳转功能。可以跳转到某个函数和变量地址，并在listing界面展示。

### 3.3 Script Manager 脚本管理

![1647681066_62359e2a9a4194899e4a5.png!small?1647681068205](https://image.3001.net/images/20220319/1647681066_62359e2a9a4194899e4a5.png!small?1647681068205)

Ghidra提供了强大了脚本功能，用户可以使用Java和Python编写脚本。

在Help中的Ghidra API Help可以查看API接口。

![1647681169_62359e91ce6016685e07b.png!small?1647681171052](https://image.3001.net/images/20220319/1647681169_62359e91ce6016685e07b.png!small?1647681171052)

  

