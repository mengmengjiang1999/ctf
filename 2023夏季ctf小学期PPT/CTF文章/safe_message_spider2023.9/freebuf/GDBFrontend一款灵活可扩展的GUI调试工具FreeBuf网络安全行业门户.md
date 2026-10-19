![](https://image.3001.net/images/20200220/1582210550_5e4e9df6a59de.jpg!small)

**今天给大家介绍的是一款名叫GDBFrontend的工具，这是一款GUI调试工具，该工具易于使用，并且灵活可扩展，广大研究人员可以根据自己的需求来对GDBFrontend进行功能扩充。**

## 工具安装

### Debian安装（Debian / Ubuntu / KDE Neon）

如果你使用的是基于Debian发行版的操作系统平台，你可以使用Deb包来安装GDBFrontend。

广大用户可以使用下列命令完成工具安装：

    
    
    echo "deb [trusted=yes]<https://oguzhaneroglu.com/deb/>./" | sudo tee -a /etc/apt/sources.list > /dev/null
    
    sudo apt update
    
    sudo apt install gdbfrontend

通过apt完成安装后，我们还需要使用apt upgrade来完成新版本更新，获取更新的命令如下：

    
    
    sudo apt update
    
    sudo apt upgrade gdbfrontend

接下来，我们就可以使用下列命令来运行GDBFrontend了：

    
    
    gdbfrontend

### GIT安装

当然了，广大研究人员也可以直接下载该项目的最新版本源码，然后配置并运行GDBFrontend。

工具要求：

> 1、GDB => 8.2 (python3)
>
> 2、python3
>
> 3、tmux

此时，我们可以使用下列命令将项目源码克隆至本地，然后安装并使用GDBFrontend：

    
    
    git clone<https://github.com/rohanrhu/gdb-frontend.git>gdb-frontend
    
    cd gdb-frontend
    
    ./gdbfrontend

接下来，使用下列命令运行工具：

    
    
    http://127.0.0.1:5551/terminal/

如果你不需要配合终端使用的话，可以运行下列命令：

    
    
    http://127.0.0.1:5551/

我们还可以使用下列命令打开GBD Shell：

    
    
    tmux a -t gdb-frontend

### Flatpak

在新版本的GDBFrontend中，还会添加针对Flatpak包的支持。

## ./gdbfrontend

    
    
    $ gdbfrontend --help
    
    GDBFrontend is a easy, flexible and extensionable gui debugger.
    
    Options:
    
    --help, -h: 显示帮助信息
    
    --version, -v: 显示版本信息
    
    --gdb-executable=PATH, -g PATH: 指定GDB可执行文件路径
    
    --tmux-executable=PATH, -tmux PATH: 指定Tmux可执行文件路径
    
    --terminal-id=NAME, -t NAME: 指定tmux 终端识别符名称
    
    --verbose, -V: 启用verbose 输出

### 参数选项

    
    
    --help, -h

显示帮助信息

    
    
    --version, -v

显示版本信息

    
    
    --gdb-executable=PATH, -g PATH

指定GDB可执行文件路径，例如：gdbfrontend --gdb-executable=/path/to/gdb。（可选项）

    
    
    --tmux-executable=PATH, -tmux PATH

指定Tmux可执行文件路径，例如：gdbfrontend --tmux-executable=/path/to/tmux。（可选项）

    
    
    --terminal-id=PATH, -t PATH

指定tmux 终端识别符名称（ID），例如：gdbfrontend --terminal-id=terminal-name。（默认: gdb-frontend）

    
    
    --verbose, -v

启用verbose 输出

### 错误解决

有的时候GDB和GDBFrontend可能会以非正常状态关闭，此时我们可以使用下列命令终止gdb-frontend Shell：

    
    
    tmux kill-session -t gdb-frontend

## 插件系统开发

### 插件样本

下面给出的是一个插件样本，可以在项目目录plugins/hello中的hello文件中找到相关代码。

首先，我们需要找到config.py文件，然后取消下列代码的注释：

    
    
    disabled_plugins = [
    
    "hello"
    
    ]

GDBFrontend的插件都存储在plugins/目录中，典型的插件文件结构如下：

    
    
    plugins/
    
    hello/
    
    frontend/
    
    html/
    
    hello.html
    
    js/
    
    hello.js
    
    css/
    
    hello.css
    
    url_modules/
    
    api.py
    
    config.py
    
    urls.py
    
    hello.py

### 插件文件-config.py

一个插件文件应当包含的基础信息如下：

    
    
    DESCRIPTION = "Example GDBFrontend plugin."
    
    AUTHOR = "Oğuzhan Eroğlu <rohanrhu2@gmail.com> (<https://oguzhaneroglu.com/>)"
    
    HOMEPAGE = "<https://github.com/rohanrhu/gdb-frontend>"
    
    VERSION = [0, 0, 1]

### hello.py样本代码：

    
    
    import importlib
    
    import plugin
    
    gdb = importlib.import_module("gdb")
    
    class HelloPlugin(plugin.GDBFrontendPlugin):
    
    def __init__(self):
    
    plugin.GDBFrontendPlugin.__init__(self)
    
    def loaded(self):
    
    gdb.events.new_objfile.connect(self.gdb_on_new_objfile)
    
    def unloaded(self):
    
    gdb.events.new_objfile.disconnect(self.gdb_on_new_objfile)
    
    def gdb_on_new_objfile(self, event):
    
    print("[HELLO] Event: new_objfile:", event)

## 工具运行截图

![](https://image.3001.net/images/20200220/1582210935_5e4e9f77c3b7c.png!small)

![](https://image.3001.net/images/20200220/1582210935_5e4e9f77c1ac0.png!small)

![](https://image.3001.net/images/20200220/1582210935_5e4e9f77db07d.png!small)

![](https://image.3001.net/images/20200220/1582210936_5e4e9f7863ff2.png!small)

![](https://image.3001.net/images/20200220/1582210936_5e4e9f7898239.png!small)

![](https://image.3001.net/images/20200220/1582210937_5e4e9f791aca9.png!small)

## 许可证协议

本项目的开发与发布遵循GNU General Public License v3 (GPL-3)开源许可证协议。

## 项目地址

> GDBFrontend：【[GitHub传送门](https://github.com/rohanrhu/gdb-frontend)】

 *** 参考来源：[ _rohanrhu_](https://github.com/rohanrhu/gdb-frontend)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

