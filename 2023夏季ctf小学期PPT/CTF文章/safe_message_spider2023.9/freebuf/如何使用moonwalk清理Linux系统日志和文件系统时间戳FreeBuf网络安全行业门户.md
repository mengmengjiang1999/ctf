![](https://image.3001.net/images/20220508/1652009737_6277ab096163ba696c3f7.jpeg!small)

## 关于moonwalk

moonwalk是一款专为红队研究人员设计的痕迹隐藏工具，在该工具的帮助下，广大研究人员可以在针对Linux系统的漏洞利用或渗透测试过程中，不会在系统日志或文件系统时间戳中留下任何痕迹。

moonwalk是一个大小仅有400KB的二进制可执行文件，能够清理研究人员在针对Unix设备进行渗透测试时留下的痕迹。该工具能够保存渗透测试之前的目标系统日志状态，并在测试完成后恢复该状态，其中包括文件系统时间戳和系统日志，而且也不会在后渗透过程中留下Shell的执行痕迹。

moonwalk是一款开源工具，旨在协助红队人员开展研究活动。

## 功能介绍

> 1、可执行文件体积小：轻松使用 curl获取工具；
>
> 2、运行速度快：可以在五毫秒内执行包括日志记录、痕迹清理和文件系统操作在内的所有会话命令；
>
> 3、网络侦查：保存系统日志状态，moonwalk会寻找一个全局可写的路径，并将会话存储在该路径中，然后在会话结束之后清理该目录；
>
> 4、Shell历史记录：moonwalk不会直接清理整个历史记录文件，而是将其恢复到测试之前的状态；
>
> 5、文件系统时间戳：通过恢复文件的访问/修改时间戳来防止被检测到；

## 工具安装

### curl安装

广大研究人员可以直接使用curl命令安装moonwalk：

    
    
    $ curl -L https://github.com/mufeedvh/moonwalk/releases/download/v1.0.0/moonwalk_linux -o moonwalk

### 源码获取

在使用源码构建时，首先需要确保本地设备上安装并配置好了下列组件：

> [ _git_](https://git-scm.org/downloads)
>
> [ _rust_](https://rust-lang.org/tools/install)
>
> cargo（安装Rust时会自动安装）
>
> A C Linker（仅Linux）

接下来，我们就可以直接使用下列命令将该项目源码克隆至本地，并完成代码构建：

    
    
    $ git clone https://github.com/mufeedvh/moonwalk.git
    
    $ cd moonwalk/
    
    $ cargo build --release

### Cargo安装

或者，也可以使用cargo来安装moonwalk：

    
    
    $ cargo install --git https://github.com/mufeedvh/moonwalk.git

### 发布版安装

直接访问该项目的【[
_Releases页面_](https://github.com/mufeedvh/moonwalk/releases)】下载预构建的moonwalk可执行程序。

## 工具使用

当我们拿到了针对目标Unix设备的Shell之后，就可以使用下列命令来开启一个moonwalk会话了：

    
    
    $ moonwalk start

当你在执行网络侦查或渗透测试的时候，可能会操作很多的文件，此时你需要使用下列命令来记录和存储相关文件的访问/修改时间戳：

    
    
    $ moonwalk get ~/.bash_history

操作完成后，可以使用下列命令清理痕迹，并关闭会话：

    
    
    $ moonwalk finish

此时，一切全部轻松搞定！

## 工具运行截图

![](https://image.3001.net/images/20220508/1652009802_6277ab4a4656ebaaa49b6.png!small)

## 许可证协议

本项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

 **moonwalk：** 【[ _GitHub传送门_](https://github.com/mufeedvh/moonwalk)】

## 参考资料

> [
> _https://en.wiki*pedia.org/wiki/Red_team_](https://en.wikipedia.org/wiki/Red_team)
>
> [ _https://rust-lang.org/tools/install_](https://rust-> lang.org/tools/install)

