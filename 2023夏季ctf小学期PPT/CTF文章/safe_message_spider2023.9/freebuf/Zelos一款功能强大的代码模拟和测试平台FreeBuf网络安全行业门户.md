![](https://image.3001.net/images/20200326/1585215503_5e7c780f2bf4d.png!small)

##  Zelos

 **Zelos是一款功能强大的代码模拟和测试平台，Zelos英文全称为“Zeropoint Emulated Lightweight Operating
System”，即Zeropoint轻量级模拟操作系统，该平台基于Python开发，可帮助广大研究人员快速实现代码行为模拟和测试。**

Zelos的其中一个强大功能就是能够通过命令行或Python脚本快速对目标代码的动态行为进行模拟、审计和评估。其中，所有的系统调用都会在与目标代码隔离的环境下进行模拟，并且支持Linux
x86_64 (32- 和64-bit)、ARM和MIPS代码。

##  工具安装

广大研究人员可以使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/zeropointdynamics/zelos.git

或者使用[pip](https://pip.pypa.io/en/stable/)包管理器来下载和安装Zelos：

    
    
    pip install zelos

当然了，在使用Zelos之前，请确保你的系统已安装好Python环境。

##  工具使用

###  命令行

使用默认选项模拟目标代码：

    
    
    $ zelos my_binary

如需查看已执行的代码指令，请添加-v参数：

    
    
    $ zelos -v my_binary

你还可以在每一个执行首次被执行时打印输出相关数据，此时需添加--fasttrace参数：

    
    
    $ zelos -v --fasttrace my_binary

默认配置下，系统调用可以通过stdout发出，如需将系统调用写入至文件，可以使用--strace参数：

    
    
    $ zelos --strace path/to/file my_binary

###  可编程处理

    
    
    import zelos
    
        z = zelos.Zelos("my_binary")
    
        z.start(timeout=3)

###  本地开发环境

首先，我们需要创建一个新的Python虚拟环境，这样可以确保不存在数据包所导致的版本冲突：

    
    
    $ python3 -m venv ~/.venv/zelos
    
        $ source ~/.venv/zelos/bin/activate

接下来，克隆代码库，并切换至zelos项目目录中：

    
    
    (zelos) $ git clone git@github.com:zeropointdynamics/zelos.git
    
        (zelos) $ cd zelos

安装可编程版本的Zelos至虚拟环境中，并确保import zelos可用，此时任何针对Zelos的本地修改将会立即生效：

    
    
    (zelos) $ pip install -e '.[dev]'

此时，通过测试并构建文档：

    
    
    (zelos) $ pytest
    
        (zelos) $ cd docs
    
        (zelos) $ make html

构建的文档可以在“docs/_build/html/”路径下找到

接下来，安装Zelos预编译的钩子来确保代码风格兼容：

    
    
    (zelos) $ pre-commit install
    
        (zelos) $ pre-commit run --all-files

###  Windows开发

我们可以直接在Windows平台中的命令行窗口中执行下列命令：

    
    
    C:\> python3 -m venv zelos_venv
    
        C:\> zelos_venv\Scripts\activate.bat
    
        (zelos) C:\> pip install -e .[dev]

##  工具运行截图

![](https://image.3001.net/images/20200326/1585215553_5e7c7841a00cc.png!small)

###  许可证协议

Zelos项目的开发与发布遵循[AGPL
v3开源许可证协议](https://www.gnu.org/licenses/agpl-3.0.en.html)。

##  项目地址

> Zelos：【[GitHub传送门](https://github.com/zeropointdynamics/zelos)】
>
> Zelos：【[官方网站](https://zelos.readthedocs.io/en/latest/index.html)】

 ***
参考来源：[zeropointdynamics](https://github.com/zeropointdynamics/zelos)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

