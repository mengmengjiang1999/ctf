![](https://image.3001.net/images/20201124/1606217087_5fbced7f3d1720ce007ed.jpg!small)

## Binbloom

Binbloom是一款针对二进制源码的固件分析软件，该工具旨在帮助广大研究人员分析固件的二进制源码，并自动化判断目标固件中的某些功能特性。该工具兼容所有常见的系统架构，因为该工具只会对目标固件进行简单的特性统计。

为了计算出加载地址，在使用Binbloom之前，我们还需要一些外部逆向工程分析工具来帮助我们提取目标固件中的潜在函数列表。

## 功能特性

  * 加载地址：Binbloom可以解析原始二进制固件并确定其加载地址。
  * 字节顺序：Binbloom可以使用一些启发式算法来确定目标固件的字节顺序。
  * UDS数据库：Binbloom可以解析原始二进制固件，并检查它是否存在有包含UDS命令id的数组。

## 工具下载/安装

首先，广大研究人员需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/quarkslab/binbloom.git
    
    cd binbloom

接下来，使用下列命令构建最新版本的Binbloom：

    
    
    mkdir build
    
    cd build
    
    cmake ..
    
    make

最后，使用下列命令安装最新版本的Binbloom（仅支持Linux系统）：

    
    
    make install

## 工具使用

### 判断字节顺序：

    
    
    binbloom -f firmware.bin -e

运行上述命令后，Binbloom将返回下列的输出数据：

    
    
    Loaded firmware.bin, size:624128, bit:fff00000, 000fffff, nb_segments:4096, shift:20
    
    End address:00098600
    
    Determining the endianness
    
    Computing heuristics in big endian order:
    
    Base: 00000000: unique pointers:1839, number of array elements:217900
    
    Base: 01000000: unique pointers:1343, number of array elements:13085
    
    Base: 02000000: unique pointers:621, number of array elements:5735
    
    Base: 03000000: unique pointers:566, number of array elements:3823
    
    Base: 05000000: unique pointers:575, number of array elements:6139
    
    Base: 80000000: unique pointers:642, number of array elements:528
    
    247210
    
    Computing score in little endian order:
    
    Base: 00000000: unique pointers:8309, number of array elements:515404
    
    515404
    
    This firmware seems to be LITTLE ENDIAN

在上述输出数据中，最后一行才是最重要的一行，因为它给出的是最终的分析结果。其他几行代表的是Binbloom在目标固件中，无论是在大端模式下还是小端模式下能够找到的唯一指针的数量和数组元素的数量，而这些信息可以用来帮助确定工具在确定字节顺序时所要使用的启发式方法。

### 判断加载地址

首先，我们需要提供一个包含了潜在函数地址列表的文件，文件内数据格式为十六进制，每个数据占一行，数据形式如下所示：

    
    
    00000010
    
    00000054
    
    000005f0
    
    00000a50
    
    00000a54
    
    00000ac0
    
    00000b40
    
    00000b6c
    
    00000b74
    
    00000bc0

这个文件需要以固件文件的文件名来进行名命，后跟“.fun”作为文件的后缀名。

这个文件可以利用tag_code.py这个Python脚本所提供的tag_code()函数来生成，使用IDA Pro的生成步骤如下：

  * 在IDA Pro中加载固件文件，选择地址0；
  * 从IDA Pro的文件菜单中，选择脚本文件，并选择py；
  * 在IDA Pro窗口底部的命令行终端中，使用tag_code()，此时将会自动生成函数文件；

如果你想使用其他工具来生成函数文件的话，只要你是以地址0加载固件文件话就都可以。比如说，函数文件中的十六进制值对应的就是固件中的偏移量。

接下来，我们就可以让Binbloom通过计算潜在函数和固件中的函数指针数组之间的相关分数来计算潜在加载地址（列表）：

    
    
    binbloom -f firmware.bin -b

上述命令执行后，Binbloom将会给我们返回如下所示的输出结果：

    
    
    Loaded firmware.bin, size:2668912, bit:ffc00000, 003fffff, nb_segments:1024, shift:22
    
    End address:0028b970
    
    loaded 14903 functions
    
     
    
    Highest score for base address: 1545, for base address 80010000
    
    For information, here are the best scores:
    
    For base address 80010000, found 1545 functions
    
    Saving function pointers for this base address...
    
    Done.

在上述输出文件中，我们可以看到目标固件提供了14903个潜在函数，当程序假设加载的基地址为0x8001000时，工具总共在函数指针数组中找到了1545个符合条件的对象。

如果目标固件源码中存在不同的区域，那么Binbloom将把固件中的不同区域以及对应的加载地址全部显示出来：

    
    
    Highest score for base address: 93, for base address 00000000
    
    For information, here are the best scores:
    
    For base address 00000000, found 93 functions
    
    For base address 00040000, found 93 functions

此时，我们已经获取到了地址0x00000000以及0x00040000处的代码段了。

 **Binbloom将生成两份输出文件：**

  * firmware.fad：该文件中包含了已识别函数的地址；
  * firmware.fpt：该文件中包含了已识别函数指针的地址；

现在，我们可以再次打开IDA Pro（或其他逆向工程分析软件），以指定的地址加载固件，然后将1545个已识别函数的地址导入进去：

  * 在IDA Pro中以指定地址加载固件；
  * 在文件菜单中，选择脚本文件，然后选择py；
  * 选择.fad文件；
  * 选择.fpt文件；

## 寻找UDS数据库（针对ECU固件）

Binbloom可以尝试搜索任何包含了UDS/KWP2000 ID的数组，这里可以使用-u选项实现：

    
    
    binbloom -f firmware.bin -u

上述命令将返回下列输出内容：

    
    
    Loaded firmware.bin, size:1540096, bit:ffe00000, 001fffff, nb_segments:2048, shift:21
    
    End address:00178000
    
    UDS DB position: 1234 with a score of 12 and a stride of 12:
    
    10 00 31 00 26 27 00 80 00 00 00 00
    
    11 00 31 00 24 3d 01 80 00 00 00 00
    
    22 00 10 00 2c 42 01 80 00 00 00 00
    
    27 00 10 00 1c 41 01 80 60 a8 01 80
    
    28 00 31 00 36 7f 01 80 00 00 00 00
    
    2e 00 10 00 18 88 01 80 08 ae 01 80
    
    31 00 30 00 10 41 01 80 00 00 00 00
    
    34 00 10 00 46 4e 01 80 00 00 00 00
    
    36 00 10 00 2a 2d 01 80 00 00 00 00
    
    37 00 10 00 32 3c 00 80 00 00 00 00
    
    3e 00 31 00 54 5b 01 80 00 b2 01 80
    
    85 00 31 00 6a 2f 01 80 00 00 00 00

## 许可证协议

本项目的开发与发布遵循Apache v2.0开源许可证协议。

## 项目地址

Binbloom：【[ _GitHub传送门_](https://github.com/quarkslab/binbloom)】

