***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ****

[](https://youtu.be/ug5ZuezbD3c)

**如果你想拥有一个可以帮助你轻松方便的开发shellcode的环境，那么Shellen将会是你的首先。Shellen是一个交互式的shellcoding环境。除了用于编写shellcode外，Shellen也可被我们当作汇编或反汇编工具使用。**

所有Shellen的操作都是基于[keystone](https://github.com/keystone-engine/keystone)和[capstone](https://github.com/aquynh/capstone)引擎的。

Shellen当前仅支持在python3上运行。对于python2的支持未来可能会实现。

## 安装

首先，我们需要安装shellen的依赖关系：

    
    
    $ sudo apt-get install cmake python3-dev python3-setuptools

你可以使用pip3安装shellen的稳定版：

    
    
    $ sudo pip3 install shellen

或者，如果你已安装了所需软件包（请参阅[所需软件包](https://github.com/merrychap/shellen#%E6%89%80%E9%9C%80%E8%BD%AF%E4%BB%B6%E5%8C%85)）：

    
    
    $ python3 setup.py install

如果你在安装keystone-engine时遇到任何问题，那么你应该编译keystone-engine（请参阅[keystone](https://github.com/keystone-engine/keystone)存储库中的[COMPILE.md](https://github.com/keystone-engine/keystone/blob/master/docs/COMPILE.md)文件）

## 如何运行Shellen

安装shellen及其必要软件包后，可以在终端中输入以下命令来运行shellen：

    
    
    $ shellen

你可以运行shellen的help命令来获取有关shellen的用法信息。

## Shellen的特性

Shellen具有编译和反编译的功能，因此有两种使用模式：asm和dsm。还有其他功能，包括搜索系统调用表和搜索常见的shellcode。

 **提示**

Shellen有一个非常实用的提示，会向我们展示当前的模式，OS（系统调用的操作系统）以及当前模式选择的架构。Shellen的提示信息如下：

    
    
    L:asm:x86_32 >

你可以像在终端一样编辑输入。此外，shellen会记录你的命令历史记录（只需输入向上箭头即可查看你之前使用过的命令）。

L是提示符中缩写的Linux名称。其他操作系统缩写名如下：

  * `L` Linux
  * `W` Windows
  * `M` MacOS

如果你想改变操作系统，那么输入setos [linux/windows/macos]如下：

    
    
    L:asm:x86_32 > setos windows
    
    [+] OS changed to windows.

要更改当前的模式，请在提示中输入asm或dsm。

    
    
    L:dsm:arm32 > asm
    
    [+] Changed to asm (assembly) mode
    
    L:asm:x86_32 > dsm
    
    [+] Changed to dsm (disassembly) mode
    
    L:dsm:arm32 > 

**基本命令**

命令| 描述  
---|---  
`clear`| 与Windows或* nix系统上的命令相同，主要用于清屏  
`help`| 显示帮助信息  
`quit,q,exit`| 完成当前session并退出  
  
 **汇编**

编译说明请键入以下命令，并用分号分隔它们，如下所示：

    
    
    L:asm:x86_32 > mov edx, eax; xor eax, eax; inc edx; int 80;
       [+] Bytes count: 7
           Raw bytes:  "\x89\xc2\x31\xc0\x42\xcd\x50"
           Hex string: "89c231c042cd50"

如果你的汇编字节包含一个空字节，那么shellen会告诉你这个。

 **反汇编**

反汇编与汇编类似。在提示符中键入你的字节并查看结果！

    
    
    L:dsm:x86_32 > 89c231c042cd50
            0x00080000:     mov     edx, eax
            0x00080002:     xor     eax, eax
            0x00080004:     inc     edx
            0x00080005:     int     0x50

 **运行shellcode**

另外，你也可以在子进程中运行你的shellcode。 **不过请注意，这会对你的系统造成损害！**
跳转到子进程中的最后一个shellcode。有什么可能出错？请注意，你无法控制代码被加载的基址，并且假定这些指令对你的CPU是有意义的。在shellen中通过help了解它的使用方法。

我打算在一些虚拟环境中执行子进程，以便更安全地运行潜在危险的shellcode。

 **架构**

asm和dsm模式适用于不同的架构。要查看Shellen当前模式的可用架构列表，请键入以下命令：

    
    
    L:dsm:x86_32 > archs
    ┌────────┬────────┬─────────┬─────────┬────────┐
    │        │        │         │         │        │
    │ arm32  │ mips32 │ sparc32 │ systemz │ x86_16 │
    │ arm64  │ mips64 │ sparc64 │         │ x86_32 │
    │ arm_tb │        │         │         │ x86_64 │
    └────────┴────────┴─────────┴─────────┴────────┘

你可以通过以下命令更改当前架构：

    
    
    L:dsm:x86_32 > setarch arm32
    
    [+] Architecture of dsm changed to arm32

### Syscalls

当你创建一个shellcode时，你将需要系统调用。shellen查找系统调用，请键入sys和所需系统调用的名称。Shellen将产生一个系统调用列表，其中可能包含你正在查找的系统调用。

    
    
    L:asm:x86_32 > sys open
    
    ┌────────┬───────┬──────────────────────┬──────────────────────┬──────────────┬──────────────┐
    │ name   │ eax   │ ebx                  │ ecx                  │ edx          │ esi          │
    ├────────┼───────┼──────────────────────┼──────────────────────┼──────────────┼──────────────┤
    │ open   │ 0x05  │ const char *filename │ int flags            │ umode_t mode │ -            │
    │ openat │ 0x127 │ int dfd              │ const char *filename │ int flags    │ umode_t mode │
    └────────┴───────┴──────────────────────┴──────────────────────┴──────────────┴──────────────┘

shellen搜索的系统调用表取决于所选架构和操作系统（OS）。在当前情况下，架构为x86_32，系统为Linux。

 **常见的Shellcode**

Shellen可以根据你提供的关键字，向你显示一个常见shellcode的列表。Shellen的关键字查找使用的是shell-storm.org的API（感谢作者！），使用方法如下：

    
    
    L:asm:x86_32 > shell <keyword> <count>

请注意，count参数并不是必需的。在[截图部分](https://github.com/merrychap/shellen#%E6%88%AA%E5%9B%BE)有shell
<keyword> <count>的结果输出图像。

 **支持的操作系统**

目前，shellen仅支持Linux系统。如果你想为Windows或MacOS添加功能，请在issue栏告知你的想法我将添加支持。

##  **如何报告问题或提出建议**

如果你发现了一些问题或错误，或认为某个功能需要添加。那么同样你也可以在issue栏写出来。

##  **所需软件包**

  * [keystone](https://github.com/keystone-engine/keystone)
  * [capstone](https://github.com/aquynh/capstone)
  * [colorama](https://github.com/tartley/colorama)
  * [termcolor](https://pypi.python.org/pypi/termcolor)
  * [terminaltables](https://github.com/Robpol86/terminaltables)

## 截图

都是一些以前使用时的截图。

![help.png](https://image.3001.net/images/20180307/15203848021210.png!small)

![use.png](https://image.3001.net/images/20180307/1520384823889.png!small)  

![syscalls.png](https://image.3001.net/images/20180307/15203848421583.png!small)  

![shell.png](https://image.3001.net/images/20180307/15203848607745.png!small)  

![tables.png](https://image.3001.net/images/20180307/15203848772536.png!small)  

***参考来源：[github](https://github.com/merrychap/shellen)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

