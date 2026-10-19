## 0x01 前言

最近产品来找我说客户有个需求，某个单位开发了一个客户端，能够接入内部系统做信息查询，但是其他单位使用需要少许的赞助一笔资金，客户需求破解客户端使其能够无限次查询。只想说作为一个安服仔，真心不会逆向，但是当着老板的面也不敢说不会，试试吧。动态分析没法速成，IDA这些看着就头大，只能靠静态分析看看能不能反编译拿到源代码再编译回exe。

## 0x02 客户端基本信息

主要看看有没有加壳和用什么语言写的，使用exeinfoPE查看基本信息

![1687831044_649a42043e0e9c6fd8561.jpg!small](https://image.3001.net/images/20230627/1687831044_649a42043e0e9c6fd8561.jpg!small)

这里主要关注最下面两行，以及EP Section其他我也看不懂

"try internal (.Zlib Ripper and unpacker - many file possible)"
表示该可执行文件可能使用了内部的.Zlib解压缩和提取工具，用于处理可能被压缩或打包的文件。

"Microsoft Visual C++ v14 - 2015 - (x64)
[www.microsoft.com](http://www.microsoft.com/)(exe 4883ec 28-48) - no sec.
CAB/7z/Zip" 表示该可执行文件是使用Microsoft Visual C++版本14（2015年）编译的，针对x64架构。

使用DIE查看exe信息

![1687831054_649a420e0601f25ce591d.jpg!small](https://image.3001.net/images/20230627/1687831054_649a420e0601f25ce591d.jpg!small)

初次运行exe程序，运行后弹窗如图，确定后退出进程

![1687831070_649a421e0adeec59f9c6c.jpg!small](https://image.3001.net/images/20230627/1687831070_649a421e0adeec59f9c6c.jpg!small)

使用火绒剑查看行为，发现执行exe后释放了一些.pyd后缀的文件以及创建了PyQt5的目录

![1687831077_649a42250ea071dd4478b.jpg!small](https://image.3001.net/images/20230627/1687831077_649a42250ea071dd4478b.jpg!small)

PyQt5是一个用于创建图形用户界面（GUI）应用程序的Python库。

.pyd是 Python 的动态链接库（Dynamic Link Library）文件的扩展名。

看完过后大概知道了exe没有加壳，使用pyinstaller打包，exe的编写语言大概率是python。

客户端大概运行流程：

![1687831083_649a422b7d38f4f68e998.jpg!small](https://image.3001.net/images/20230627/1687831083_649a422b7d38f4f68e998.jpg!small)

## 0x03 exe反编译

使用PyInstaller打包的exe文件可以使用[pyinstxtractor](https://github.com/extremecoders-re/pyinstxtractor)进行解包，但这取决于打包的方式和设置，另外PyInstaller的打包过程通常会对Python代码进行加密或混淆，以保护源代码。在这种情况下，使用pyinstxtractor无法直接解包出可读的源代码。

使用[pyinstxtractor](https://github.com/extremecoders-re/pyinstxtractor)尝试解包：

![1687831090_649a4232dae20b83ab419.jpg!small](https://image.3001.net/images/20230627/1687831090_649a4232dae20b83ab419.jpg!small)

运行后会在运行目录下生成一个tasks_query.exe_extracted的目录，里面是提取出来的文件，但是这里会发现出现告警信息，大概是说此脚本运行的
Python 版本与用于构建可执行文件的版本不同，请在 Python 3.8 中运行此脚本以防止在解组期间出现提取错误，跳过 pyz
提取，打开PYZ-00.pyz_extracted目录会发现目录是空的，最重要的文件并没有提取出来。

需要再根据提示安装一个python 3.8的环境在提取一次，提取后会获得一些.pyc，.pyo等文件；

![1687831099_649a423bdb05f3d57d355.jpg!small](https://image.3001.net/images/20230627/1687831099_649a423bdb05f3d57d355.jpg!small)

.pyc是 Python 编译后的字节码文件的扩展名，此时拿到的并不是源代码，还需要使用其他反编译工具将pyc编译成py文件；

下面是一些常用的将`.pyc`文件反编译为`.py`文件的工具，以下工具可以配合使用，通过测试发现主目录下的.pyc使用uncompyle6可以反编译出源代码，但是PYZ-00.pyz_extracted下的就不行，需要用pycdc。

  * [uncompyle6:](https://github.com/rocky/python-uncompyle6)一个流行的Python反编译工具，支持Python 2和Python 3的`.pyc`文件（推荐）。

  * [decompyle3](https://github.com/rocky/python-decompile3): 用于反编译Python 3的`.pyc`文件的工具。

  * [uncompyle2](https://github.com/wibiti/uncompyle2): 用于反编译Python 2的`.pyc`文件的工具。

  * [pycdc](https://github.com/zrax/pycdc): 一个基于C实现的反编译工具，可以将`.pyc`文件反编译为可读的Python代码（适用于更高版本的python，推荐）。

使用pip安装uncompyle6

    
    
    pip install uncompyle6

使用uncompyle6尝试编译，发现反编译出来的不是源代码，更换python 3.8环境也是一样的结果

![1687831126_649a4256d8a7ce94de239.jpg!small](https://image.3001.net/images/20230627/1687831126_649a4256d8a7ce94de239.jpg!small)

版本问题，部署[pycdc](https://github.com/zrax/pycdc)进行反编译

    
    
    Linux:  
    git clone https://github.com/zrax/pycdc.git  
    cd pycdc  
    cmake .  
    make

尝试反编译成功，获得源代码：

![1687831137_649a4261bc5b01d7d4b93.jpg!small](https://image.3001.net/images/20230627/1687831137_649a4261bc5b01d7d4b93.jpg!small)

看了下源代码，代码中写了很多敏感信息，数据库连接信息都在里面，如果是做渗透已经可以交差了，可惜。

![1687831150_649a426ec51b024b48d52.jpg!small](https://image.3001.net/images/20230627/1687831150_649a426ec51b024b48d52.jpg!small)

## 0x04 代码查看

在主目录下找到了main.pyc里面应该是网络检测相关的代码；

![1687831158_649a4276260aacd5e6579.jpg!small](https://image.3001.net/images/20230627/1687831158_649a4276260aacd5e6579.jpg!small)

也找到了查询限制相关的逻辑判断

![1687831164_649a427c0b25e7db3f762.jpg!small](https://image.3001.net/images/20230627/1687831164_649a427c0b25e7db3f762.jpg!small)

但是发现存在两个问题，根本没办法将.py在编译回exe

  * .pyc主文件过大（大于3800行代码），反编译出来的代码不完整，会报错Segmentation fault，没有找到解决办法

![1687831177_649a4289a99420ac38e34.jpg!small](https://image.3001.net/images/20230627/1687831177_649a4289a99420ac38e34.jpg!small)

  * 不知道目录结构，而且反编译出来的代码准确性还有问题，要将>50个pyc文件反编译为py再编译为exe难度不是一般大

## 0x05 总结

遇到构造比较简单的exe，反编译后最打包回exe还可以，但是遇到架构复杂，代码特多的，太难了。

通常情况下，将`.pyc`和`.py`文件一起打包为单个可执行文件（`.exe`）是不可行的，直接将单个`.pyc`文件重新打包为可执行文件（`.exe`）也是不可行的，也就是说你将main.py代码改了，其他文件不动，再编译到.pyc也没办法重新打包，必须要都是.py才能打包。

要将Python代码打包为可执行文件（`.exe`），需要使用打包工具（如PyInstaller、py2exe、cx_Freeze等），它们会将Python代码和相关的依赖项打包到单个可执行文件中。

