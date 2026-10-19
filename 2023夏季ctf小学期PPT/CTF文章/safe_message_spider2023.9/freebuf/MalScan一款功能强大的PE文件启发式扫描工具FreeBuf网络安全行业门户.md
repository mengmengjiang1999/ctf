![](https://image.3001.net/images/20230704/1688478024_64a421485151560819096.jpg!small)

## 关于MalScan

MalScan是一款功能强大的PE文件启发式扫描工具，该工具基于Python开发，广大研究人员可以使用该工具快速分析PE文件并找出文件代码中是否存在任何可疑内容。值得一提的是，该工具是完全开源的，这也就意味着广大研究人员可以根据自己的需求随意扩展MalScan的功能。

## 功能支持

> 1、支持收集关于PE文件的信息，例如MD5、SHA1和时间戳等；
>
> 2、支持检查PEiD签名；
>
> 3、自定义Yara规则集成；
>
> 4、支持查看数据区块、导入、导出、资源和TLS回调等信息概述；
>
> 5、提供了一些自定义启发式算法；

## 工具依赖

> Python 2.7
>
> Yara-Python

## 工具安装

由于该工具基于Python 2.7开发，因此我们首先需要在本地设备上安装并配置好Python 2.7环境。

接下来，广大研究人员可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Ice3man543/MalScan.git .
    
    cd MalScan
    
    python malscan.py

## 工具使用

该工具的使用非常简单，我们只需要运行MalScan脚本并提供需要检测的PE文件名即可：

![](https://image.3001.net/images/20230704/1688478048_64a4216043217fd80bed9.png!small)

## 许可证协议

本项目的开发与发布遵循[ _BSD_
_-2-Clause_](https://github.com/Ice3man543/MalScan/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **MalScan** ：【[ _GitHub传送门_](https://github.com/Ice3man543/MalScan)】

