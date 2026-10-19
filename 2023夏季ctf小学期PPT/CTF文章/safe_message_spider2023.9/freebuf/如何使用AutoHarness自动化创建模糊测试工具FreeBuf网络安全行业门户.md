![](https://image.3001.net/images/20211002/1633187239_615875a7e872df9a9f8d2.png!small)

## 关于AutoHarness

AutoHarness是一款功能强大的自动化工具，可以帮助广大研究人员以自动化的形式生成模糊测试工具。该工具的初衷源于目前模糊代码库中的一个并发问题：大型代码库有数千个函数和代码片段，可以嵌入到库中相当深层的地方。对于更加智能的模糊测试工具来说，想要达到那个代码路径都是非常困难的，有时甚至都不可能到达。对于更加大型的模糊测试项目，例如oss-fuzz，仍然会有部分代码无法被覆盖到。因此，AutoHarness的主要作用就是试图在一定程度上缓解这一问题，并提供一种工具，供安全研究人员用于对代码库初始化测试。

当前版本的AutoHarness仅支持C和C++代码库。

## 工具安装

该程序利用llvm和clang（libfuzzer、Codeql）来寻找代码中的函数，并使用了Python来生成模糊测试工具。这个程序目前已在Ubuntu
20.04（llvm 12和Python 3）上进行过测试。

首先，我们需要使用下列命令来初始化AutoHarness的安装：

    
    
    sudo apt-get update;
    
    sudo apt-get install python3 python3-pip llvm-12* clang-12 git;
    
    pip3 install pandas lief subprocess os argparse ast;

接下来，我们还需要安装Codeql进程，具体请参考【[这里](https://github.com/github/codeql)】。确保已经安装好的命令行工具和代码库。

最后，使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/parikhakshat/autoharness.git

## 工具使用

下面的例子中，我们对运行在Nginx中的多个参数模式集执行了AutoHarness，并拿到如图所示的输出结果：

    
    
    python3 harness.py -L /home/akshat/nginx-1.21.0/objs/ -C /home/akshat/codeql-h/ -M 1 -O /home/akshat/autoharness/ -D nginx -G 1 -Y 1 -F "-I /home/akshat/nginx-1.21.0/objs -I /home/akshat/nginx-1.21.0/src/core -I /home/akshat/nginx-1.21.0/src/event -I /home/akshat/nginx-1.21.0/src/http -I /home/akshat/nginx-1.21.0/src/mail -I /home/akshat/nginx-1.21.0/src/misc -I /home/akshat/nginx-1.21.0/src/os -I /home/akshat/nginx-1.21.0/src/stream -I /home/akshat/nginx-1.21.0/src/os/unix" -X ngx_config.h,ngx_core.h

![](https://image.3001.net/images/20211002/1633187336_6158760860599d1a31faa.png!small)

通过进一步调试编译并添加更多头文件等，肯定可以提高成功率。注意：nginx项目在编译后没有任何共享对象。不过，该程序支持将PIE可执行程序转换为共享库。

## 计划添加的功能

> 结构化模糊测试
>
> 实现基于Harness的创建功能
>
> 并行模糊测试/假阳性检测

## 项目地址

 **AutoHarness：** 【[
_GitHub传送门_](https://github.com/parikhakshat/autoharness)】

## 参考资料

> [
> _https://lief.quarkslab.com/doc/latest/tutorials/08_elf_bin2lib.html﻿_](https://lief.quarkslab.com/doc/latest/tutorials/08_elf_bin2lib.html)

