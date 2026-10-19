![](https://image.3001.net/images/20201031/1604144475_5f9d4d5b3336e15f72452.png!small)

## Polypyus

Polypyus支持从相似的二进制文件中提取出已知函数，并以此来学习如何再原始二进制文件中定位函数。该工具是一个固件源码分析工具，它不需要对二进制文件进行反汇编，这就是它的一个很大的优势，因为有些二进制文件的反汇编是比较困难的。除此之外，该工具仅对二进制源码进行分析，因此它的执行速度非常快，在几秒钟之内即可完成。但是，该工具所使用的方法要求二进制文件使用相同的体系结构，并且具有类似的编译器选项。

Polypyus支持集成到现有工具的工作流中，比如说Ghidra、IDA、BinDiff和Diaphora等等。比如说，它可以导入以前注释过的函数并从中学习，还可以导出要导入到IDA中寻找的函数。由于Polypyus使用了相当严格的阈值，所以它只能在我们的实验中找到正确的匹配。

在处理原始固件二进制文件（即各种Broadcom和Cypress Bluetooth固件版本）时，我们发现IDA自动分析经常错误地启动已识别的函数。在IDA
Pro 6.8中，自动分析更具攻击性，会导致更多的结果，但也会导致更多的误报。而IDA Pro 7.2就更惨了，因为它会遗漏很多函数。

## 工具运行机制

Polypyus能够通过比较带注释的固件二进制文件数据集中的常见函数来创建二进制模糊匹配模块。当前版本的Polypyus支持下列注释：

> WICED Studio patch.elf文件，这是一种特殊的ELF文件，其中仅包含符号定义；
>
> .symdefs文件，即大多数ARM编译器支持生成的文件；
>
> .csv文件，带有格式化样本数据；

这些注释包含已知函数的地址、大小和名称。历史记录数据集中输入二进制文件的共性越多，Polypyus的性能和结果就越好。给定几个稍有不同的函数，Polypyus就可以创建非常好的匹配器。

## 工具安装

Polypyus要求Python 3.6及其更高版本的环境，我们建议大家使用一个Virtualenv虚拟环境来执行工具的安装。

首先，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/seemoo-lab/polypyus.git

接下俩，切换到项目目录下，执行下列命令:

    
    
    pip install .

## 工具运行

工具安装完成之后，我们可以使用下列命令来运行该工具：

    
    
    polypyus-gui
    
    polypyus-cli

## Polypyus的使用

我们可以通过图形化界面或命令行接口来使用Polypyus，分别对应的是polypyus-gui和polypyus-cli这两条命令，并且它们都支持下列调用参数：

    
    
    --verbose is the verbosity level. By default, it shows warnings -v shows info -vv show debug information.
    
      --project sets the location of the project file. This is either a file path or ":memory:".
    
      --help    Show help message.

## 图形化界面使用

一般的图形化界面工作流都是从视窗的左手边往右手边操作的。首先，需要将二进制源码添加到历史记录中。接下来，工具会添加符号注释，并添加目标源码。如需获取匹配函数，可以点击“Create
matchers from history”。匹配器创建完成之后，我们就可以选择单个目标了，或者通过选择“batch
match”来匹配所有的目标代码。最后，所有的结果数据都将存储在一个.csv文件中。

在下面这个演示视频中，我们可以看到Polypyus只需要几秒钟，即可从两份输入代码中完成学习过程、注释代码、创建匹配器，并将匹配函数应用到新的代码中。

视频地址：【[ _点我观看_](https://github.com/seemoo-lab/polypyus/blob/master/doc/gui_demo.mp4)】

## 命令行接口使用

使用命令行接口的好处就是它能够自动化执行任务。目前来说，命令行接口的数据输出格式可能会因版本变化而改变。下面给出的是一个调用示例：

    
    
    polypyus-cli --history examples/history/20819-A1.bin --annotation examples/history/20819-A1_patch.elf --history examples/history/20735B1.bin --annotation examples/history/20735B1_patch.elf --project test.sqlite
    
    polypyus-cli --target examples/history/20739B1.bin --project test.sqlite

## 许可证协议

本项目的开发与发布遵循GPL v3开源许可证协议。

## 项目地址

Polypyus：【[ _GitHub传送门_](https://github.com/seemoo-lab/polypyus)】

