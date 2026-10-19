![](https://image.3001.net/images/20230605/1685968800_647dd7a0cd33abd8ab12d.gif!small)

## 关于sandfly-entropyscan

sandfly-entropyscan是一款功能强大的熵扫描工具，该工具可以用于检测与恶意软件相关的打包文件或加密二进制文件。除此之外，该工具还支持查找恶意文件和Linux进程相关的安全信息，并提供带有加密哈希的输出结果。

sandfly-entropyscan能够快速扫描文件或正在运行的进程，可以判断它们是否是Linux/Unix
ELF类型的可执行程序，并报告其熵（随机性度量）。一些针对Linux的恶意软件经过打包或加密之后，会显示出非常高的熵，在该工具的帮助下，广大研究人员可以快速找到高熵可执行文件或进程。

## 功能介绍

> 1、基于Golang开发，支持跨平台和多种架构；
>
> 2、独立的运行代码，不需要其他依赖组件，可以直接在目标计算机设备上直接使用；
>
> 3、不受LD_PRELOAD风格rootkit的影响；
>
> 4、内置PID破解，可以从某些类型的可加载内核模块（LKM） rootkit中找到隐藏文件或隐藏进程；
>
> 5、生成目标文件的熵、MD5、SHA1、SHA256和SHA512哈希值；
>
> 6、可用于扫描脚本以自动查找问题；
>
> 7、事件响应人员可以使用它快速扫描并锁定Linux主机上潜在的恶意软件；

## 工具下载

广大研究人员可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/sandflysecurity/sandfly-entropyscan.git

## 代码构建

首先，我们需要在本地设备上安装并配置好最新版本的[ _Golang_](http://www.golang.org/)环境。

接下来，在命令行终端中切换到项目目录中，并运行下列命令构建代码：

    
    
    cd sandfly-entropyscan/
    
    go build

然后根据需求和参数选项来运行工具代码即可：

    
    
    ./sandfly-entropyscan

## 工具参数选项

> -csv：以CSV格式输出结果；
>
> -delim：修改CSV文件的默认分隔符，默认为“,”，可修改为“|”等；
>
> -dir string：指定要分析的目录名称；
>
> -file string：指定要分析的单个文件完整路径；
>
> -proc：检测正在运行的进程；
>
> -elf：仅检测ELF可执行程序；
>
> -entropy float：显示所有熵大于或等于某个值的任意文件/进程，最小0.0-最大8.0，默认0即显示所有文件；
>
> -version：显示工具版本和退出；

## 工具使用样例

搜索/temp目录下的所有可执行文件：

    
    
    sandfly-entropyscan -dir /tmp -elf

搜索/var/www目录中熵大于等于7.7的可执行文件

    
    
    sandfly-entropyscan -dir /var/www -elf -entropy 7.7

以CSV格式生成所有正在运行进程的熵和加密哈希：

    
    
    sandfly-entropyscan -proc -csv

搜索熵大于7.7的可能经过打包或加密的任意进程：

    
    
    sandfly-entropyscan -proc -entropy 7.7

为/bin目录下的所有文件生成熵和加密哈希，并以CSV格式输出：

    
    
    sandfly-entropyscan -dir /bin -csv

扫描一个目录中的所有熵大于7.7的文件：

    
    
    sandfly-entropyscan -dir /path/to/dir -entropy 7.7

快速检测一个文件并生成熵和加密哈希，并判断是否为可执行程序：

    
    
    sandfly-entropyscan -file /dev/shm/suspicious_file

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/sandflysecurity/sandfly-entropyscan/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **sandfly-entropyscan** ：【[
_GitHub传送门_](https://github.com/sandflysecurity/sandfly-entropyscan)】

## 参考资料

> [ _https://www.sandflysecurity.com/_](https://www.sandflysecurity.com/)
>
> [ _http://www.golang.org/_](http://www.golang.org/)

