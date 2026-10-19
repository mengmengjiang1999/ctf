![](https://image.3001.net/images/20221116/1668603396_6374de0486a3cf165484f.png!small)

## 关于UnBlob

UnBlob是一款针对容器安全的强大工具，该工具可以从任意格式的容器中提取文件。该工具运行速度非常快，准确率高，并且易于使用。UnBlob能够解析已知的超过30种不同格式的文档、压缩文件和文件系统，并能够从中递归提取文件内容。

UnBlob是完全开源免费的，并提供了一个命令行接口。除此之外，该工具还能够以Python库的形式来使用。这些特性使得UnBlob成为文件/数据提取、分析和逆向固件镜像的完美工具。

## 工具特性

> 1、准确率高：支持使用自定义规则识别数据区块的起始偏移量，并根据数据格式标准自动计算数据区块的终止偏移量；
>
> 2、安全性高：UnBlob不需要使用高级权限即可执行，并自动将依赖的第三方组件升级到最新版本；
>
> 3、可扩展性强：UnBlob提供了一个API，广大研究人员可以自行编写自定义格式处理器和数据提取器；
>
> 4、运行速度快：UnBlob的运行速度非常快，默认使用多线程机制；

## 技术特性

> 1、UnBlob基于Python语言开发；
>
> 2、为了快速搜索文件中的代码模式，使用了[ _Hyperscan_](https://www.hyperscan.io/)；
>
> 3、为了提取已识别的格式，使用了各种不同类型的数据提取工具；
>
> 4、针对ELF分析，使用了[ _LIEF_](https://lief-project.github.io/)及其[ _Python_ __
> _binding_](https://pypi.org/project/lief/)；
>
> 5、针对CPU密集型任务（例如熵的计算），使用了[ _Rust_](https://www.rust-lang.org/)来提速；
>
> 6、为了提供更美观的命令行接口，使用了[ _Click_](https://click.palletsprojects.com/)库；
>
> 7、为了提供结构化的日志记录，使用了[ _structlog_](https://www.structlog.org/)库；

## 工具下载&安装

该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/onekey-sec/unblob.git

然后使用Poetry安装所需的依赖组件：

    
    
    cd unblob
    
    poetry install --no-dev

接下来，根据对应的操作系统安装所需的数据提取器：

    
    
    # Ubuntu 22.04
    
    sudo apt install e2fsprogs p7zip-full unar zlib1g-dev liblzo2-dev lzop lziprecover img2simg libhyperscan-dev zstd

如果你需要使用squashfs的话，可以安装sasquatch：

    
    
    curl -L -o sasquatch_1.0_amd64.deb https://github.com/onekey-sec/sasquatch/releases/download/sasquatch-v1.0/sasquatch_1.0_amd64.deb
    
    sudo dpkg -i sasquatch_1.0_amd64.deb
    
    rm sasquatch_1.0_amd64.deb

最后，请检查所有的依赖组件是否已安装完成：

![](https://image.3001.net/images/20221116/1668603495_6374de670ac1bcf2b0fa6.png!small)

## 工具使用

UnBlob提供了一个易于使用的命令行接口，我们可以直接传递一个需要提取的文件即可：

    
    
    $ unblob alpine-minirootfs-3.16.1-x86_64.tar.gz
    
    2022-07-30 06:33.07 [info     ] Start processing file          file=openwrt-21.02.2-x86-64-generic-ext4-combined.img.gz pid=7092

该工具将会创建一个新的目录，名称带有“_extract”：

    
    
    $ ls -l
    
    total 2656
    
    drwxrwxr-x 3 walkman walkman    4096 Jul 30 08:43 alpine-minirootfs-3.16.1-x86_64.tar.gz_extract
    
    -rw-r--r-- 1 walkman walkman 2711958 Jul 30 08:43 alpine-minirootfs-3.16.1-x86_64.tar.gz

此时，工具会递归提取出所有已知的文件格式，直到到达指定的递归路径层级为止（默认为10层）：

![](https://image.3001.net/images/20221116/1668603521_6374de81da1b1371cf5d4.png!small)

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/onekey-sec/unblob/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **UnBlob** ：【[ _GitHub传送门_](https://github.com/onekey-sec/unblob)】

## 参考资料

> [ _https://unblob.org/_](https://unblob.org/)
>
> [ _https://onekey.com/_](https://onekey.com/)
>
> [ _https://www.python.org/_](https://www.python.org/)
>
> [ _https://www.hyperscan.io/_](https://www.hyperscan.io/)
>
> [ _https://lief-project.github.io/_](https://lief-project.github.io/)
>
> [ _https://pypi.org/project/lief/_](https://pypi.org/project/lief/)
>
> [ _https://www.rust-lang.org/_](https://www.rust-lang.org/)
>
> [ _https://click.palletsprojects.com/_](https://click.palletsprojects.com/)
>
> [ _https://www.structlog.org/_](https://www.structlog.org/)

