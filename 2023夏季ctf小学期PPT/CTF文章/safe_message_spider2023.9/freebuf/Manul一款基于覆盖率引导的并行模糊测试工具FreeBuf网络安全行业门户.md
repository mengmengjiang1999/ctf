![](https://image.3001.net/images/20200220/1582203043_5e4e80a3616d8.jpg!small)

**Manul是一款基于覆盖率引导的并行模糊测试工具，该工具采用纯Python开发，并且已完全开源，广大研究人员可以使用Manul在Windows、Linux和macOS平台上对目标代码进行模糊测试或黑盒测试。**

##  马上使用

    
    
    pip3 install psutil
    
        git clone <https://github.com/mxmssh/manul>
    
        cd manul
    
        mkdir in
    
        mkdir out
    
        echo "AAAAAA" > in/test
    
        python3 manul.py -i in -o out -n 4 "linux/test_afl @@"

###  安装Radamsa

    
    
    sudo apt-get install gcc make git wget
    
        git clone <https://gitlab.com/akihe/radamsa.git> && cd radamsa && make && sudo make install

如果你是用的是Windows平台，那你就不需要安装Radamsa了，因为Manul针对Windows平台的发布包中已经包含了Radamsa库了。

##  公共CVE列表

**CVE IDs** |  **产品** |  **发现人**  
---|---|---  
CVE-2019-9631 CVE-2019-7310 CVE-2019-9959  |  Poppler  |  Maksim Shudrak  
CVE-2018-17019 CVE-2018-16807 CVE-2019-12175  |  Bro/Zeek  |  Maksim Shudrak  
  
如果你使用Manul成功发现了新的漏洞的话，大家可以将漏洞信息添加到这个列表之中。

###  工具演示样例

![Image](https://image.3001.net/images/20200420/1587382831_5e9d8a2f5ff0b.gif)

##  工具依赖

1、Python3（Python2从2020年1月1日开始就已经过时了，但是Manul在Python2环境下理论来说可以正常工作）

2、Psutil：【[传送门](https://pypi.org/project/psutil/)】

3、Pywin32（Windows平台下，DBI持久模式），安装命令如下：

    
    
    pip install pywin32

##  基于覆盖率引导的模糊测试

当前版本的Manul支持两种类型的操作指令，即基于AFL的指令（afl-gcc、afl-clang和afl-clang-fast）和DBI模式。

###  基于覆盖率引导的模糊测试-AFL指令模式

你可以使用afl-gcc、afl-clang-fast或Address Sanitizer（建议使用）命令来进行操作，演示样例如下：

    
    
    CC=afl-gcc CXX=afl-g++ CFLAGS=-fsanitize=address CXXFLAGS=-fsanitize=address cmake <path_to_your_target>
    
        make -j 8
    
        USE_ASAN=1 CC=afl-clang-fast CXX=afl-clang-fast++ cmake <path_to_your_target>
    
        make -j 8

如需获取详细使用样例，可以点击【[这里](http://lcamtuf.coredump.cx/afl/QuickStartGuide.txt)】获取。

###  基于覆盖率引导的模糊测试-DBI模式

在使用该模式时，无需使用专门的命令，但是我们需要在Windows或Linux平台中下载最新版本的DynamoRIO框架。

    
    
    Manul在Linux和Windows平台上，是以x86/x64预编译客户端的形式发布的，你可以在下列目录中找到它们：
    
        linux/dbi_32|dbi_64/libbinafl.so (DynamoRIO client)
    
        win/dbi_32|dbi_64/binafl.dll

不幸的是，DynamoRIO目前还不支持在macOS上使用。

###  使用DynamoRIO对代码进行黑盒模糊测试

DynamoRIO：【[最新版下载](https://github.com/DynamoRIO/dynamorio/wiki/Downloads)】

在使用之前，你需要去掉manul.config文件中的下列代码行的注释，并且给DynamoRIO启动器和客户端提供正确的路径：

    
    
    # Choose DBI framework to provide coverage back to Manul ("dynamorio" or "pin"). Example dbi = dynamorio
    
        dbi = dynamorio
    
        # If dbi parameter is not None the path to dbi engine launcher and dbi client should be specified.
    
        dbi_root = /home/max/DynamoRIO/bin64/drrun
    
        dbi_client_root = /home/max/manul/linux/dbi_64/libbinafl.so
    
        dbi_client_libs = None

除此之外，广大用户还可以使用持续内存模糊测试功能来提升黑盒模糊测试的性能。在这个模式下，你可以控制Manul对特定的函数进行测试，并通过取消下列代码行注释来实现循环执行：

    
    
    dbi_persistence_mode = 1
    
        dbi_target_module = afl_test
    
        dbi_target_method = open_file
    
        #dbi_target_offset = 0x3198 # optionally you can provide offset of this function instead of name
    
        dbi_fuzz_iterations = 1000

winAFL的开发者对这种模式进行了非常详细的介绍，感兴趣的话大家可以点击【[这里](https://github.com/googleprojectzero/winafl/blob/master/readme_dr.md#in-app-persistence-mode)】了解更多。而Manul引用了winAFL中大部分指令库的代码，用来跟待测目标发送指令或进行通信。

##  编译DynamoRIO客户端代码

编译指令库，我们需要安装最新版本的[DynamoRIO](https://github.com/DynamoRIO/dynamorio/releases/download/)。指令库源代码可以在Manul主目录下的“dbi_clients_src”中找到。

###  64-bit Linux

    
    
    cd dbi_clients_src
    
        wget <DynamoRIO-x86_64-Linux-X.XX.XXXX-X.tar.gz> - download the latest DynamoRIO
    
        tar xvf DynamoRIO-x86_64-X.XX.XXXX-X.tar.gz
    
        mkdir client_64
    
        cd client_64
    
        cmake ../dr_cov/ -DDynamoRIO_DIR=/home/max/manul/dbi_clients_src/DynamoRIO-x86_64-Linux-X.XX.XXXX-X.tar.gz/cmake
    
        Make

###  32-bit Linux

    
    
    cd dbi_clients_src
    
        wget <DynamoRIO-i386-Linux-X.XX.XXXX-X.tar.gz> - download the latest DynamoRIO
    
        tar xvf DynamoRIO-x86_64-X.XX.XXXX-X.tar.gz
    
        mkdir client_64
    
        cd client_64
    
        CFLAGS=-m32 CXXFLAGS=-m32 cmake ../dr_cov/ -DDynamoRIO_DIR=/home/max/manul/dbi_clients_src/DynamoRIO-i386-Linux-X.XX.XXXX-X.tar.gz/cmake
    
        Make

在Windows下，需要安装Visual Studio（2017或2013），然后启动“VS20XX Cross Tools Command
Prompt”，并运行下列命令：

###  64-bit Windows

    
    
    cd dbi_clients_src
    
        <Download and extract the latest version of DynamoRIO>
    
        mkdir client_64
    
        cd client_64
    
        cmake -G"Visual Studio 15 Win64" ..\dr_cov\ -DDynamoRIO_DIR=C:\Users\max\manul\dbi_clients_src\DynamoRIO-Windows-XXXX.XX.X.X\cmake
    
        cmake --build . --config RelWithDebInfo (or just Debug if needed)

###  32-bit Windows

    
    
    cd dbi_clients_src
    
        <Download and extract the latest version of DynamoRIO>
    
        mkdir client_32
    
        cd client_32
    
        cmake -G"Visual Studio 15" ..\dr_cov\ -DDynamoRIO_DIR=C:\Users\max\manul\dbi_clients_src\DynamoRIO-Windows-XXXX.XX.X.X\cmake
    
        cmake --build . --config RelWithDebInfo (or just Debug if needed)

##  工具命令行参数

    
    
    Example: python3 manul.py -i corpus -o out_dir -n 40 "target @@"
    
        positional arguments:
    
          target_binary  The target binary and options to be executed (don't forget to include quotes e.g. "target e @@").
    
        optional arguments:
    
          -h, --help     show this help message and exit
    
          -n NFUZZERS    Number of parallel fuzzers
    
          -s             Run dumb fuzzing (no code instrumentation)
    
          -c CONFIG      Path to config file with additional options (see Configuration File Options section below)
    
          -r             Restore previous session
    
        Required parameters:
    
          -i INPUT       Path to directory with initial corpus
    
          -o OUTPUT      Path to output directory

##  状态视图

![](https://image.3001.net/images/20200220/1582203215_5e4e814f53ca4.jpg!small)

##  项目地址

> Manul：【[GitHub传送门](https://github.com/mxmssh/manul)】

***参考来源：[mxmssh](https://github.com/mxmssh/manul)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

