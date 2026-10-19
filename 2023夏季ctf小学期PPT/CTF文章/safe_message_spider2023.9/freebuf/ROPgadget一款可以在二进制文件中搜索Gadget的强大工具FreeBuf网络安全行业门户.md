![](https://image.3001.net/images/20230705/1688565948_64a578bc04824ed8fbb71.jpg!small)  

## 关于ROPgadget

ROPgadget是一款可以在二进制文件中搜索Gadget的强大工具，本质上来说，ROPgadget
是一个小工具查找程序和自动操作程序。在该工具的帮助下，广大研究人员可以在二进制文件中搜索Gadget，以方便我们实现对 ROP 的利用。ROPgadget
支持 x86，x64，ARM，PowerPC，SPARC 和 MIPS 体系结构，并支持 ELF / PE / Mach-O 格式。

值得一提的是，从ROPgadget v5 开始，ROPgadget 具有一个新的内核，该内核是使用
[_Capstone_](http://www.capstone-engine.org/)（一个轻量级的多平台架构支持的反汇编架构）实现的。

## 工具安装

由于该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python
3环境。接下来，广大研究人员可以直接使用PyPi安装ROPgadget：

    
    
    $ sudo apt install python3-pip
    
    $ sudo -H python3 -m pip install ROPgadget
    
    $ ROPgadget --help

或者使用下列命令将该项目源码克隆至本地，但此时你需要先手动安装[ _Capstone_](http://www.capstone-engine.org/)：

    
    
    $ sudo apt install python3-pip
    
    $ sudo -H python3 -m pip install capstone
    
    $ sudo git clone https://github.com/JonathanSalwan/ROPgadget.git

安装完成后，我们就可以将ROPgadget以独立工具运行和使用了：

    
    
    $ python3 ROPgadget.py --help

## 工具使用

    
    
    usage: ROPgadget.py [-h] [-v] [-c] [--binary <binary>] [--opcode <opcodes>]
    
                        [--string <string>] [--memstr <string>] [--depth <nbyte>]
    
                        [--only <key>] [--filter <key>] [--range <start-end>]
    
                        [--badbytes <byte>] [--rawArch <arch>] [--rawMode <mode>]
    
                        [--rawEndian <endian>] [--re <re>] [--offset <hexaddr>]
    
                        [--ropchain] [--thumb] [--console] [--norop] [--nojop]
    
                        [--callPreceded] [--nosys] [--multibr] [--all] [--noinstr]
    
                        [--dump] [--silent] [--align ALIGN] [--mipsrop <rtype>]
    
     
    
    description:
    
      ROPgadget lets you search your gadgets on a binary. It supports several
    
      file formats and architectures and uses the Capstone disassembler for
    
      the search engine.
    
     
    
    formats supported:
    
      - ELF
    
      - PE
    
      - Mach-O
    
      - Raw
    
     
    
    architectures supported:
    
      - x86
    
      - x86-64
    
      - ARM
    
      - ARM64
    
      - MIPS
    
      - PowerPC
    
      - Sparc
    
      - RISC-V 64
    
      - RISC-V Compressed
    
     
    
    optional arguments:
    
      -h, --help            显示工具帮助信息和退出
    
      -v, --version          显示ROPgadget版本
    
      -c, --checkUpdate     检测是否有新版本
    
      --binary <binary>      指定需要分析的代码文件名
    
      --opcode <opcodes>    搜索可执行区段中的opcode
    
      --string <string>        搜索可读区段中的字符串
    
      --memstr <string>      搜索所有可读区段中的每一个字节
    
      --depth <nbyte>       搜索引擎深度（默认为10）
    
      --only <key>          仅显示指定指令
    
      --filter <key>           过滤特定助记符
    
      --range <start-end>     在两个地址之间执行搜索(0x...-0x...)
    
      --badbytes <byte>      屏蔽Gadget地址中的特定字节
    
      --rawArch <arch>        指定原始文件架构，例如x86|arm|arm64|sparc|mips|ppc|riscv
    
      --rawMode <mode>      指定原始文件模式，例如32|64|arm|thumb
    
      --rawEndian <endian>    为原始文件设置大/小端，例如little|big
    
      --re <re>             正则表达式
    
      --offset <hexaddr>     指定Gadget地址偏移量
    
      --ropchain            启用ROP链生成
    
      --thumb               怼搜索引擎启用thumb模式
    
      --console             使用搜索引擎的交互式终端
    
      --norop               禁用ROP搜索引擎
    
      --nojop               禁用JOP搜索引擎
    
      --callPreceded         仅显示前面调用过的Gadget
    
      --nosys               应用SYS搜索引擎
    
      --multibr             启用多分支Gadget
    
      --all                  禁用重复Gadget删除功能
    
      --noinstr               禁用Gadget指令终端打印
    
      --dump                输出Gadget
    
      --silent               在分析过程中不打印Gadget信息
    
      --align ALIGN         对齐Gadget地址（字节）
    
      --mipsrop <rtype>  搜索其他有用的Gadget，例如stackfinder|system|tails|lia0|registers

## 工具使用样例

    
    
    ROPgadget.py --binary ./test-suite-binaries/elf-Linux-x86
    
      ROPgadget.py --binary ./test-suite-binaries/elf-Linux-x86 --ropchain
    
      ROPgadget.py --binary ./test-suite-binaries/elf-Linux-x86 --depth 3
    
      ROPgadget.py --binary ./test-suite-binaries/elf-Linux-x86 --string "main"
    
      ROPgadget.py --binary ./test-suite-binaries/elf-Linux-x86 --string "m..n"
    
      ROPgadget.py --binary ./test-suite-binaries/elf-Linux-x86 --opcode c9c3
    
      ROPgadget.py --binary ./test-suite-binaries/elf-Linux-x86 --only "mov|ret"
    
      ROPgadget.py --binary ./test-suite-binaries/elf-Linux-x86 --only "mov|pop|xor|ret"
    
      ROPgadget.py --binary ./test-suite-binaries/elf-Linux-x86 --filter "xchg|add|sub|cmov.*"
    
      ROPgadget.py --binary ./test-suite-binaries/elf-Linux-x86 --norop --nosys
    
      ROPgadget.py --binary ./test-suite-binaries/elf-Linux-x86 --range 0x08041000-0x08042000
    
      ROPgadget.py --binary ./test-suite-binaries/elf-Linux-x86 --string main --range 0x080c9aaa-0x080c9aba
    
      ROPgadget.py --binary ./test-suite-binaries/elf-Linux-x86 --memstr "/bin/sh"
    
      ROPgadget.py --binary ./test-suite-binaries/elf-Linux-x86 --console
    
      ROPgadget.py --binary ./test-suite-binaries/elf-Linux-x86 --badbytes "00|01-1f|7f|42"
    
      ROPgadget.py --binary ./test-suite-binaries/Linux_lib64.so --offset 0xdeadbeef00000000
    
      ROPgadget.py --binary ./test-suite-binaries/elf-ARMv7-ls --depth 5
    
      ROPgadget.py --binary ./test-suite-binaries/elf-ARM64-bash --depth 5
    
      ROPgadget.py --binary ./test-suite-binaries/raw-x86.raw --rawArch=x86 --rawMode=32
    
      ROPgadget.py --binary ./test-suite-binaries/elf-Linux-RISCV_64 --depth 8

## 工具运行截图

![](https://image.3001.net/images/20230705/1688566007_64a578f7243f4cde245dd.png!small)![](https://image.3001.net/images/20230705/1688566013_64a578fd11de5cb6eedf0.png!small)

![](https://image.3001.net/images/20230705/1688566020_64a5790447401da9cd618.png!small)

![](https://image.3001.net/images/20230705/1688566026_64a5790aac6d7a198bc8e.png!small)

![](https://image.3001.net/images/20230705/1688566032_64a57910afe6ab5a7e996.png!small)

![](https://image.3001.net/images/20230705/1688566038_64a5791677ebba9dbe6ed.png!small)

## 许可证协议

本项目的开发与发布遵循[
_BSD_](https://github.com/JonathanSalwan/ROPgadget/blob/master/LICENSE_BSD.txt)开源许可证协议。

## 项目地址

 **ROPgadget** ：【[ _GitHub传送门_](https://github.com/JonathanSalwan/ROPgadget)】

## 参考资料

> [ _http://www.capstone-engine.org/_](http://www.capstone-engine.org/)

