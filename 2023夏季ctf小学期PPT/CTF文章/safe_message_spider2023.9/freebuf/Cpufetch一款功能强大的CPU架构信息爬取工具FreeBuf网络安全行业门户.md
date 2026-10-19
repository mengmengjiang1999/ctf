![](https://image.3001.net/images/20210413/1618317781_607591d5bf735962a80b3.png!small)

## 关于Cpufetch

Cpufetch是一款功能强大的CPU架构信息获取工具，该工具支持x86、x86_64（Intel和AMD）以及ARM架构的CPU。Cpufetch支持在Linux、Windows和macOS操作系统上运行，但我们建议广大用户在Linux操作系统上使用Cpufetch。

![](https://image.3001.net/images/20210413/1618317798_607591e688f134468ebfa.png!small)

## 工具安装

### 源码构建

首先，我们需要将该项目源码克隆至本地，然后切换到项目目录下运行“make”命令对源码进行编译：

    
    
    git clone https://github.com/Dr-Noob/cpufetch
    
    cd cpufetch
    
    make
    
    ./cpufetch

生成的Makefile支持在Linux、Windows和macOS上使用。

### Linux安装

Arch Linux上提供了可用的Cpufetch包（cpufetch-git），如果你使用的是其他的Linux发行版系统，则需要使用源码构建Cpufetch。

### Windows安装

在该项目的Releases页面中，我们可以找到针对Windows系统编译的可执行程序。直接下载并使用CMD命令行工具运行即可。

![](https://image.3001.net/images/20210413/1618317818_607591facbb2892213251.png!small)

### macOS安装

需要使用源码构建Cpufetch。

### Android安装

首先，我们需要安装好termux应用程序（终端模拟器）。然后在termux中运行下列命令：

    
    
    pkg install -y git make clang

接下来，进行源码构建：

    
    
    git clone https://github.com/Dr-Noob/cpufetch
    
    cd cpufetch
    
    make
    
    ./cpufetch

## 工具使用样例

接下来，我们会给大家演示如何使用Cpufetch获取和查看不同CPU架构的信息。

### x86_64 CPU

![](https://image.3001.net/images/20210413/1618317842_60759212af56cf398bafb.png!small)

![](https://image.3001.net/images/20210413/1618317849_607592194ddf939b3f657.png!small)

### ARM CPU

![](https://image.3001.net/images/20210413/1618317857_607592216cd6ec7e94589.png!small)

![](https://image.3001.net/images/20210413/1618317863_60759227787c05edbe50b.png!small)

## 颜色和风格

默认配置下，Cpufetch将会使用系统默认的配色方案来显示关于CPU的信息。但是，你也可以使用自定义的颜色方案：

    
    
    ./cpufetch --color intel (Intel默认颜色风格)
    
    ./cpufetch --color amd (AMD默认颜色风格)
    
    ./cpufetch --color 239,90,45:210,200,200:100,200,45:0,200,200 (样例)

使用RGB设置颜色时，必须要以下列形式提供四个颜色值：

    
    
    [R,G,B:R,G,B:R,G,B:R,G,B]

这些颜色对应的是CPU以及文字颜色，因此我们需要自定义配置所有的颜色值。

## 项目地址

Cpufetch：https://github.com/Dr-Noob/cpufetch

## 参考资料

> https://github.com/Gonzalocl
>
> https://github.com/OdnetninI
>
> https://github.com/Dr-Noob/cpufetch/issues
>
> https://github.com/Dr-Noob/cpufetch/blob/master/doc/README.md

