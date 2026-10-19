![](https://image.3001.net/images/20210917/1631888093_6144a2dd167ec4abf2a4a.png!small)

## 关于Speakeasy

Speakeasy是一款功能强大的模块化二进制模拟器，旨在帮助广大研究人员模拟Windows内核以及用户模式恶意软件。

Speakeasy模拟的是Windows的特定组件，而不是尝试使用整个虚拟化操作系统执行动态分析。具体地说，Speakeasy可以通过模拟操作系统API、对象、正在运行的进程/线程、文件系统和网络，给研究人员提供一个能够让待分析样本完整执行的环境。

样本可以很容易地在容器或云服务中进行模拟，这将允许研究人员同时分析多个样本。当前版本的Speakeasy支持用户模式和内核模式Windows应用程序。

在进行模拟之前，工具会识别代码中的入口点，而且还可以模拟在运行时所发现的动态入口点。除此之外，Speakeasy可以在模拟过程中尽可能多地覆盖代码。

Speakeasy完全基于Python 3开发，并且基于Unicorn仿真引擎来模拟CPU指令。

## 工具安装

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/fireeye/speakeasy

Speakeasy可以在Docker容器中执行，或者以单独的脚本执行，也可以在云服务中执行。安装该工具最简单的方法就是先安装好Speakeasy所需的依赖包，然后运行项目中的setup.py脚本：

    
    
    cd <repo_base_dir>
    
    python3 -m pip install -r requirements.txt
    
    python3 setup.py install

项目中还提供了一个Docker文件，可以用于构建Docker镜像。不过，Speakeasy的依赖组件可以安装在本地系统，或直接通过Python运行。

## Docker容器运行

该项目中提供的Dockerfile可以用于生成Docker镜像。

### Docker镜像构建

首先，我们需要使用下列命令创建一个容器，标签名为“my_tag”：

    
    
    cd <repo_base_dir>
    
    docker build -t "my_tag" .

接下来，使用下列命令运行Docker镜像，并在/sandbox中创建一个本地卷：

    
    
    docker run -v <path_containing_malware>:/sandbox -it "my_tag"

## 工具使用

### 以代码库运行

下面的例子中，我们演示了如何模拟一个Windows DLL：

    
    
    import speakeasy
    
     
    
        # Get a speakeasy object
    
        se = speakeasy.Speakeasy()
    
     
    
        # Load a DLL into the emulation space
    
        module = se.load_module("myfile.dll")
    
     
    
        # Emulate the DLL's entry point (i.e. DllMain)
    
        se.run_module(module)
    
     
    
        # Set up some args for the export
    
        arg0 = 0x0
    
        arg1 = 0x1
    
        # Walk the DLLs exports
    
        for exp in module.get_exports():
    
            if exp.name == 'myexport':
    
                # Call an export named 'myexport' and emulate it
    
                se.call(exp.address, [arg0, arg1])
    
     
    
        # Get the emulation report
    
        report = se.get_report()
    
     
    
        # Do something with the report; parse it or save it off for post-processing

### 以命令行工具运行

    
    
    usage: run_speakeasy.py [-h] [-t TARGET] [-o OUTPUT] [-p [PARAMS ...]] [-c CONFIG] [-m] [-r] [--raw_offset RAW_OFFSET]
    
                            [-a ARCH] [-d DUMP_PATH] [-q TIMEOUT] [-z DROP_FILES_PATH] [-l MODULE_DIR] [-k] [--no-mp]
    
     
    
    Emulate a Windows binary with speakeasy
    
     
    
    optional arguments:
    
      -h, --help            显示帮助信息并退出
    
      -t TARGET, --target TARGET
    
                           模拟的输入文件路径
    
      -o OUTPUT, --output OUTPUT
    
                           保存报告的输出文件路径
    
      -p [PARAMS ...], --params [PARAMS ...]
    
                           提供个模拟进程的命令行参数
    
      -c CONFIG, --config CONFIG
    
                            模拟器配置文件路径
    
      -m, --mem-tracing      启用内存跟踪，记录样本访问的所有内存
    
      -r, --raw              尝试模拟未解析的文件
    
      --raw_offset RAW_OFFSET
    
                           原始模式下开始模拟的偏移量地址
    
      -a ARCH, --arch ARCH   设置模拟过程中所使用的架构，支持[ x86 | amd64 ]
    
      -d DUMP_PATH, --dump DUMP_PATH
    
                           存储压缩内存转储包的路径
    
      -q TIMEOUT, --timeout TIMEOUT
    
                           模拟超时（默认为60秒）
    
      -z DROP_FILES_PATH, --dropped-files DROP_FILES_PATH
    
                           存储模拟过程中创建的文件的路径
    
      -l MODULE_DIR, --module-dir MODULE_DIR
    
                            存储可加载PE模块的目录路径
    
      -k, --emulate-children
    
                            模拟CreateProcess API创建的任意进程
    
      --no-mp               在当前进程中运行模拟任务

## 工具使用样例

### 模拟一个Windows驱动程序

    
    
    user@mybox:~/speakeasy$ python3 run_speakeasy.py -t ~/drivers/MyDriver.sys

### 模拟32位Windows Shellcode

    
    
    user@mybox:~/speakeasy$ python3 run_speakeasy.py -t ~/sc.bin  -r -a x86

### 模拟64位Windows Shellcode并创建完整的内存转储

    
    
    user@mybox:~/speakeasy$ python3 run_speakeasy.py -t ~/sc.bin  -r -a x64 -d memdump.zip

## 项目地址

 **Speakeasy：** 【[ _GitHub传送门_](https://github.com/fireeye/speakeasy)】

## 参考资料

> [ _https://www.fireeye.com/blog/threat-research/2020/08/emulation-of-> malicious-shellcode-with-> speakeasy.html_](https://www.fireeye.com/blog/threat-> research/2020/08/emulation-of-malicious-shellcode-with-speakeasy.html)
>
> [ _https://github.com/unicorn-engine/unicorn﻿_](https://github.com/unicorn-> engine/unicorn)
>
> [
> _https://github.com/fireeye/speakeasy/blob/master/doc/configuration.md_](https://github.com/fireeye/speakeasy/blob/master/doc/configuration.md)
>
> [
> _https://github.com/fireeye/speakeasy/blob/master/doc/limitations.md﻿_](https://github.com/fireeye/speakeasy/blob/master/doc/limitations.md)

