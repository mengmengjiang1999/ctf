Hashcat系列软件是非常强大的开源的密码破译软件。号称世界上最快的密码破解软件。配合强大的字典，可以破译超过百分之九十的密码。

在之前的文章中，我们简述了hashcat的发展过程，以及一些简单的命令使用方法。但是想要充分发挥hashcat的功能，仅有虚拟机还是不够的。最好把hashcat安装到本机/服务器，利用GPU进行密码破译。

在本机/服务器使用hashcat的第一步就是安装，在这里除了跟大家交流一下hashcat在不同环境下的安装方法，也想帮大家规避一下安装过程中踩过的坑。

## 硬件：

系统：win7 x64

配置：两块NVIDIA显卡：GeForce GTX 750 和Tesla K20c

我安装了两块显卡，一块用于显示，一块用于计算。Tesla是专门用于大规模计算GPU，我用的K20大概比我的CPU快个几百倍。目前Tesla
P系列是NVIDA家计算最快的GPU，但是真的太贵了，舍不得买。对GPU感兴趣的可以自行google学习。

![1.jpg](https://image.3001.net/images/20180530/15276623327477.jpg!small)

TeslaK20c功率比较大，普通的电源没有办法同时带动两块GPU，所以把普通电源换成了800w的大功率电源。啊~，这个电源好贵的o(╥﹏╥)o。

![2.png.jpg](https://image.3001.net/images/20180530/15276623552706.jpg!small)

## 准备活动

1.下载[hashcat](https://hashcat.net/hashcat/)。

官网中有两个下载链接，一个是二进制文件，一个是源程序。

![55555.png](https://image.3001.net/images/20180530/15276624495392.png!small)
如果电脑提前已经配置好的话，可以下载二进制文件，解压即可运行。

但是如果不清楚自己电脑是否配置完整，还是建议大家下载源代码。因为hashcat的Makefile文件中的编译程序非常完善，按照提示一步一步安装一定可以完整运行。而二进制文件不能保证在所有电脑上都可以运行，配置出问题的话会很难搞。

2.阅读hashcat中的文档

其实在hashcat中主要是看三个文件：README.md,BULID.md,Makefile。  

首先看README.md：README.md文件中有对hashcat的相关介绍，包括一个简短的介绍，证书，下载地址，安装说明，以及其他注意事项。

然后看BUILD.md文件：BUILD.md文件中是hashcat在不同系统下的安装命令。按照BUILD.md文件的说明就可以成功安装hashcat。

最后看Makefile：src/Makefile文件是hashcat的编译代码。包含完整的安装过程，完整运行Makefile文件就可以生成hashcat.exe。配置过程中出现文件路径或配置问题，可以到Makefile文件中找一找，搞不好就会有收获。

## 如何在windows环境下安装hashcat

Hashcat通常是在服务器上运行，然后进行远程调用。但是个人使用还要搭建服务器的话，感觉很麻烦。Hahscat非常人性化，它的源码在Windows,苹果，Linux三种系统中通用。大部分人都使用Windows系统，那我们不妨试试在windows环境下安装hashcat。

Windows环境下要想安装hashcat首先要安装编译器,我这里利用mingWG编译hashcat源代码。Hashcat的3.0,4.0版本兼容cpu版本和GPU版本。在安装时，hashcat会自主判断你的电脑有没有GPU，没有GPU就会安装CPU版本。

### 下载并安装MinGW

MinGW是适用于Windows的轻量级GNU，它是一些头文件和端口库的集合，它可以让我们在没有第三方库文件的情况下使用GCC。MinGW的核心是GCC,而GCC是一套可以移植到几乎所有计算机平台上的编译系统。MinGW除了GCC它还包含其他的GNU程序工具。

我们先[下载]()安装WinGW。找你喜欢的版本，安装到你熟悉的位置，OK!

![1.png](https://image.3001.net/images/20180530/15276624921316.png!small)

在MinGW Installation Manager中可以对MinGW进行设置，右键选择“Mark for
Installation”,然后选择Installation ->Apply Changes。

![2.png](https://image.3001.net/images/20180530/15276633531214.png!small)

### winGW环境配置

安装完成后，需要设置环境变量：

我的电脑->属性->高级系统设置->高级->环境变量

![3.png](https://image.3001.net/images/20180530/1527663365131.png!small)

在系统变量一栏中找到“Path”并编辑。环境变量Path会指定的可执行文件的搜索路径，这样我们可以在任何路径下打开该文件。这样系统除了在当前目录下寻找程序还会到path指定的目录下寻找。Bin文件其实是mingw中的命令所在的文件夹。

![4.png](https://image.3001.net/images/20180530/15276633958999.png!small)

把MinGW的路径放到path变量值的最前面，并用“；”分隔开。

### 安装hashcat  

打开hashcat的BUILD.MD文件，这个文件是hashcat的安装文件。Windows下的安装方法如下：

![00000.png](https://image.3001.net/images/20180530/15276636743732.png!small)

在hashcat的目录下，运行make win64命令。

![5.png](https://image.3001.net/images/20180530/15276636895957.png!small)

发现make命令不存在，但是在MinGW的bin目录下，我们找到wingw32-make命令，改用wingw32-make
win64执行。运行该命令后，出现错误。找不到模块，这是没有安装opencl的缘故。Hashcat要在opencl环境下运行，调用很多opencl库

![6.png](https://image.3001.net/images/20180530/15276637956636.png!small)

Opencl有intel版本，nvida版本和AMD版本。这几个版本都是可以的。我下载的intel的opencl的地址是：<https://software.intel.com/en-us/articles/opencl-drivers>，大家根据自己电脑的配置自行选择合适的安装包。我的电脑之前没有进行任何有关opencl的配置，所以下载了SDK和dirver,防止在后续安装过程中出现其它意料之外的问题：

Intel® SDK for OpenCL™ Applications 2017R2 for Windows* (64-bit)

OpenCL™ Runtime for Intel® Core™ and Intel®Xeon® Processors

![7.png](https://image.3001.net/images/20180530/1527664197198.png!small)

安装完成后，我们再make一下又出现了错误:

![8.png](https://image.3001.net/images/20180530/15276643038930.png!small)

这是因为makefile文件中的路径问题，可以在hashcat中找到libiconv文件。我发现我的hashcat中没有这个文件路径，所以又下载了一个libiconv。下载之后修改makefile文件中的调用。再make一下。成功！

![9.png](https://image.3001.net/images/20180530/15276643218511.png!small)

安装成功后，我们可以按照前面WinGW设置path的方式，把hashcat64这是为全局命令。如果觉得每次输入hashcat64做命令还是很麻烦，把hashcat64.exe重命名为任何你喜欢的名字，比如个人姓名's
Tool，看起来就很带感！  

### 测试

安装完成后我们要检测一下hashcat能否正常运行，从cmd切到hashcat所在的目录。-b 命令测试一下效率吧！

![10.png](https://image.3001.net/images/20180530/15276643431630.png!small)

测试显示两块GPU都能正常运行。这样，我们的Hashcat的安装就算大功告成了。

![11.png](https://image.3001.net/images/20180530/15276643577710.png!small)

### 总结：

虽然看起来Hashcat的安装很简单，但是安装过程中还是出现了很多问题，在配置过程中，文件配置的路径尤其容易出问题。所以大家一定要注意安装过程中，Hashcat的Makefile文件中调用的模块和路经，当调用出现问题时，先检查一下MinGW和OpenCL中是否有被调用的文件。通过修改路径可以解决我在安装过程程碰到的大半问题。这样也可以避免多余的操作。

考虑到大部分使用Hashcat的人还是倾向于Linux系统，下次我们来分享一下Hashcat在linux系统下的安装。另外从本周开始我们会持续推出干货，大家感兴趣的话，可以持续关注哦！

 ***本文作者：EVA。本文属丁牛网安实验室原创出品，转载请注明来自FreeBuf.COM。**

