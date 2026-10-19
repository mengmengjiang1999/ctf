# 一、Ghidra今世前生

Ghidra是一个由美国国家安全局（NSA）研究部门创造并维护的软件逆向工程框架。这个框架包括了一套完善的软件分析工具，涵盖了反汇编、汇编、反编译、图形化以及许多其他有用的功能。  
在2019年3月NSA已经以开源方式放出。

GitHub：

<https://github.com/NationalSecurityAgency/ghidra>

![](https://image.3001.net/images/20211227/1640587968_61c962c08272150c7ca65.png!small)

# 二、Ghidra优点

 **（1）兼容优良**  
可以运行于Windows、macOS、Linux等主流平台，工具由Java编写。  
 **（2）功能强大**  
Ghidra完善地整合如IDA Pro、Radare、Binary
Ninja等工具所拥有的大部分功能。并且Ghidra同样支持庞大的处理器指令集与可执行格式。  
 **（3）开源方式**  
如上所说，Ghidra在2019年3月之后已经被开源，协议为Apache License 2.0。该协议允许用户对代码进行更改与再发布。  
 **（4）可扩展化与定制化**  
可扩展化体现在插件功能可以提供独特的功能。Tools（工具）用户可以自定义插件与工具的配置、创建新的工具、编写自己的插件。从UI到功能的可自定义性，Ghidra能够满足绝大多数用户的需求。  
 **（5）操作可撤回**  
通常我们在进行研究时，难免会碰到意外情况。Ghidra允许用户对操作进行撤回（Undo）和重做(Redo)。用户可以自定义操作的储存深度。

![](https://image.3001.net/images/20211227/1640588007_61c962e7a5325bb4b18d0.png!small)

# 三、安装、配置环境

 **（1）配置要求**  
 **硬件**  
4GB RAM，1 GB 存储空间，双显示器或多显示器最佳  
 **操作系统**  
Microsoft Windows 7 或 10 (64-bit)

Linux (64-bit, CentOS 7 最佳)

macOS (OS X) 10.8.3+  
不支持32位的操作系统  
 **软件**  
Java 11 Runtime and Development Kit（JDK）  
推荐使用的环境为OpenJDK  
 **（2）Ghidra下载**  
建议通过github下载，见上文。或者可以于Ghidra官网（[https://ghidra-sre.org/)](https://ghidra-sre.org/%EF%BC%89%E4%B8%8B%E8%BD%BDGhidra%E7%9A%84%E6%9C%80%E6%96%B0%E5%8E%8B%E7%BC%A9%E5%8C%85)[下载Ghidra的最新压缩包](https://ghidra-sre.org/%EF%BC%89%E4%B8%8B%E8%BD%BDGhidra%E7%9A%84%E6%9C%80%E6%96%B0%E5%8E%8B%E7%BC%A9%E5%8C%85)。

![](https://image.3001.net/images/20211227/1640588080_61c963303840580bf1b32.png!small)

 **（3）配置环境**  
Ghidra需要特定版本的JDK位于PATH中才能够运行。如果PATH中的Java版本Ghidra并不支持，它将使用该版本的Java来寻找用户系统中受支持的Java版本。如果仍然找不到受支持的Java版本，用户会被要求输入一个Java的主目录以供使用。

Ghidra是通过OpenJDK进行的开发与测试，因此我们建议使用这个OpenJDK来获取最稳定的体验。

如果Ghidra由于PATH中没有任何版本的Java而不能运行，用户需要手动安装一个受支持的JDK并将其添加到PATH，以下是操作流程：

 **1\. Windows**  
提取JDK发行版本(.zip文件)，之后

Windows 10: 右键点击左下角Windows键，然后点击【系统】

Windows 7: 点击左下角Windows键，右键点击【计算机】，点击【属性】

点击【系统信息】，之后点击【高级系统设置】  
点击【环境变量】  
在【系统变量】下方，选中Path，并点击【编辑】  
在【编辑系统变量】的窗口中，在变量值的最后加入一个分号“;”，并接着输入<JDK目录的路径>bin  
确认以上修改  
 **2.Linux 与macOS (OS X)**  
提取JDK。  
tar xvf <JDK文件.tar.gz>  
用编辑器打开~/.bashrc，譬如  
vi ~/.bashrc  
在文件最后，将JDK的bin目录加入PATH变量。  
export PATH=<提取出的JDK目录路径>/bin:$PATH  
保存文件。  
重启所有终端来让改动生效

## 四、快速项目入门

配置好环境并运行Ghidra之后，我们可以点击File→New
Project，或者使用快捷键Ctrl+N，来创建一个新项目。鉴于我们暂时先讲单人作业，选择Non-Shared
Project，并接着输入项目目录与名称以完成项目的创建。

![](https://image.3001.net/images/20211231/1640921384_61ce7928479acfb4a4070.png!small)之后导入文件，我们可以简单地将文件拖入Ghidra窗口，也可以选择File→Import
File（快捷键I）来导入文件。

![](https://image.3001.net/images/20211231/1640921426_61ce795253869cfcb62fe.png!small)导入文件后，我们选择CodeBrowser工具，按钮为喷火的龙头图标，也即是Ghidra自带的工具来打开文件。

![](https://image.3001.net/images/20211231/1640921454_61ce796e41da45669abf3.png!small)在用CodeBrowser打开我们的文件后，由于是第一次打开，Ghidra会提醒我们，需不需要对文件进行分析，我们选Yes并且以默认的分析工具设置对文件进行分析（直接点选Analyze）。

![](https://image.3001.net/images/20211231/1640921488_61ce79903217a01efb436.png!small)![](https://image.3001.net/images/20211231/1640921520_61ce79b099170cb58b878.png!small)分析的进度会在界面右下角显示

联系方式：2250126767@qq.com

  

  

  

  

  

  

  

  

  

  

  

  

  

  

