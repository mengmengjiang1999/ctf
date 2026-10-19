![](https://image.3001.net/images/20210927/1632706816_61512100853f12300fb72.png!small)

## 关于Brutus

Brutus是一款功能强大的漏洞利用框架，该框架基于模块化开发，并且具备高度可扩展特性。除此之外，Brutus还采用多任务和多进程架构，因此具备高性能特性。

Brutus基于Python开发，可以自动化基于网络的漏洞利用测试和基于Web的网络侦察活动。作为一个轻量级框架，Brutus旨在最大限度地减少对第三方依赖的依赖。Brutus针对Kali
Linux进行了优化，它还与macOS和大多数Linux发行版兼容，具有完全交互式的命令行界面和多功能插件系统。

Brutus具有高度可扩展的模块化体系结构，这些模块在“任务层”上运行，而任务层由线程池和线程安全异步队列组成。主线程在一个多进程池上运行，该池管理应用程序上下文并分派新进程，以便任务可以在后台或单独的Shell中运行。

Brutus的UI层也是可扩展的，默认情况下，Brutus附带有一个基于菜单的命令行界面UI，但广大研究人员可以自行添加GUI、参数解析器以及HTTP
API等等。

除此之外，Brutus有一个实用程序层，它具有文件系统操作、Shell管理、持久化方法和系统元数据的通用功能。

## 功能介绍

Brutus包括几个模块，这些模块可以概括为三大类：基于网络的、基于Web的和Payload。最后一类是一个编译器库，附带有Payload，而Brutus的交互式命令行菜单可以编译这些Payload，随后将其加载至Brutus的其他基于网络的模块中。

Brutus的底层利用POSIX线程进行并发多任务处理，有些模块还使用Python的异步I/O库。

 **包含的实用工具/脚本：**

> IP表管理
>
> HTTPS降级至HTTP
>
> 启用监控模式
>
> 启用端口转发
>
> 键盘记录

## 工具安装

首先，我们需要安装并配置好下列依赖组件：

> sslstrip
>
> pipenv

Brutus专门针对Kali Linux系统进行过优化，网上也有很多关于如何在虚拟机中运行Kali Linux的资料了，因此我们在这里不再进行赘述。

安装好依赖组件之后，我们可以运行下列命令将该项目源码克隆至本地，并进行工具安装：

    
    
    git clone https://github.com/MatthewZito/brutus.git
    pipenv install

## 工具使用

 **工具运行：**

    
    
    pipenv run brutus

 **执行测试：**

    
    
    pipenv run test

 **Lint：**

    
    
    pipenv run lint

 **配置Git Hook开发环境：**

    
    
    pipenv run setup

## 工具使用演示

 **GIF：** 【[
_点我查看_](https://github.com/MatthewZito/Brutus/blob/dev/assets/brutus_demo1.gif)】

## 工具演示视频

 **视频地址：** 【[ _点我观看_](https://streamable.com/scybvn)】

## 项目地址

 **Brutus：** 【[ _GitHub传送门_](https://github.com/MatthewZito/brutus)】

