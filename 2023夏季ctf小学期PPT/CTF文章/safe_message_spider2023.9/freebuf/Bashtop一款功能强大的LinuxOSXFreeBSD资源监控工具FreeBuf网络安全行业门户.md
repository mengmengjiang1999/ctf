![](https://image.3001.net/images/20200926/1601116869_5f6f1ac56b9f13074a7a6.png!small)

Bashtop是一款针对Linux/OSX/FreeBSD的基于终端的资源监控实用程序，虽然该工具是一个命令行工具，但它也提供了非常美观的UI界面，并且可以直观地显示CPU、内存、正在运行的进程和带宽等统计数据。它带有游戏风格的响应式终端UI和可自定义的菜单，各种显示部分的整齐排列使监视各种系统指标变得容易了很多。

通过使用Bashtop，我们还可以对进程进行排序，以及轻松地在各种排序选项之间切换。此外，我们还可以将SIGKILL，SIGTERM和SIGINT发送到所需的进程。

该工具的运行速度非常快，并且还提供了很多其他支持，比如说：

> 支持鼠标点击；
>
> 可切换迷你模式；
>
> 支持个性化定制；
>
> 显示内存消耗图；

Bashtop可以安装在Linux，macOS，甚至FreeBSD上。除此之外，Bashtop现在还发布了Python版本，感兴趣的用户可以点击【[
_这里_](https://github.com/aristocratos/bpytop)】直接获取使用。

## 功能介绍

> 易于使用，带有受游戏启发的菜单系统。
>
> 快速响应的 UI，带有 UP、DOWN 键可快速对进程进行选择。
>
> 可显示所选进程的详细统计信息。
>
> 可以过滤进程。
>
> 在排序选项之间轻松切换。
>
> 发送 SIGTERM、SIGKILL、SIGINT 选择进程。
>
> 带有用于更改所有配置文件选项的 UI 菜单。
>
> 网络使用情况的自动缩放图。
>
> 如果有新版本可用，则在菜单中显示消息。

## 工具依赖

要安装和使用Bashtop，请确保系统中已准备好下列依赖组件。

> Bash 4.4或更高版本
>
> Git
>
> GNU Coreutils
>
> GNU sed，awk，grep和ps命令行工具
>
> Lm传感器–可选（用于收集CPU温度统计信息）

## 工具安装

首先，我们将开始手动安装Bashtop，工具适用于所有基于Linux的发行版系统。

### 手动安装

要手动安装Bashtop，请如下所示克隆git仓库，并使用以下命令从源代码编译：

    
    
    $ git clone https://github.com/aristocratos/bashtop.git
    
    $ cd bashtop
    
    $ sudo make install

要卸载Bashtop，请运行：

    
    
    $ sudo make uninstall

### 在Ubuntu中安装Bashtop

在Ubuntu上安装Bashtop的方法有两种：使用snap或使用APT软件包管理器。

要使用snap安装，执行：

    
    
    $ snap install bashtop

要使用APT软件包管理器进行安装，请首先添加如下所示的Bashtop PPA：

    
    
    $ sudo add-apt-repository ppa:bashtop-monitor/bashtop

接下来，更新软件包列表，然后如图所示安装Bashtop。

    
    
    $ sudo apt update
    
    $ sudo apt install bashtop

### 在Debian中安装Bashtop

Bashtop在Debian的官方存储库中可用。要安装它，只需运行以下命令：

    
    
    $ sudo apt install bashtop

另外，您可以运行显示的命令。

    
    
    $ git clone https://github.com/aristocratos/bashtop.git
    
    $ cd bashtop/
    
    $ cd DEB
    
    $ sudo ./build

### 在Fedora中安装Bashtop

要将Bashtop放入Fedora中，只需运行以下命令：

    
    
    $ sudo dnf install bashtop

### 在CentOS / RHEL 8中安装Bashtop

对于CentOS 8 / RHEL 8系统，您需要首先启用EPEL存储库，然后再运行以下命令：

    
    
    $ sudo yum install epel-release
    
    $ sudo dnf install bashtop

### 在Arch Linux上安装Bashtop

Bashtop在AUR以bashtop-git的形式提供。要安装Bashtop，只需运行：

    
    
    $ sudo pacman -S bashtop

## 如何在Linux上使用Bashtop资源监视器

要启动Bashtop，只需在终端上运行以下命令:

    
    
    bashtop

## 工具配置项

该工具所有的配置项都可以在配置文件中修改，配置文件地址为"$HOME/.config/bashtop"。

### bashtop.cfg（自动生成）：

    
    
    #? Config file for bashtop v. 0.9.21
    
     
    
    #* Color theme, looks for a .theme file in "$HOME/.config/bashtop/themes" and "$HOME/.config/bashtop/user_themes"
    
    #* Should be prefixed with either "themes/" or "user_themes/" depending on location, "Default" for builtin default theme
    
    color_theme="Default"
    
     
    
    #* Update time in milliseconds, increases automatically if set below internal loops processing time, recommended 2000 ms or above for better sample times for graphs
    
    update_ms="2500"
    
     
    
    #* Processes sorting, "pid" "program" "arguments" "threads" "user" "memory" "cpu lazy" "cpu responsive"
    
    #* "cpu lazy" updates sorting over time, "cpu responsive" updates sorting directly
    
    proc_sorting="cpu lazy"
    
     
    
    #* Reverse sorting order, "true" or "false"
    
    proc_reversed="false"
    
     
    
    #* Show processes as a tree
    
    proc_tree="false"
    
     
    
    #* Check cpu temperature, only works if "sensors", "vcgencmd" or "osx-cpu-temp" commands is available
    
    check_temp="true"
    
     
    
    #* Draw a clock at top of screen, formatting according to strftime, empty string to disable
    
    draw_clock="%X"
    
     
    
    #* Update main ui when menus are showing, set this to false if the menus is flickering too much for comfort
    
    background_update="true"
    
     
    
    #* Custom cpu model name, empty string to disable
    
    custom_cpu_name=""
    
     
    
    #* Enable error logging to "$HOME/.config/bashtop/error.log", "true" or "false"
    
    error_logging="true"
    
     
    
    #* Show color gradient in process list, "true" or "false"
    
    proc_gradient="true"
    
     
    
    #* If process cpu usage should be of the core it's running on or usage of the total available cpu power
    
    proc_per_core="false"
    
     
    
    #* Optional filter for shown disks, should be names of mountpoints, "root" replaces "/", separate multiple values with space
    
    disks_filter=""
    
     
    
    #* Enable check for new version from github.com/aristocratos/bashtop at start
    
    update_check="true"
    
     
    
    #* Enable graphs with double the horizontal resolution, increases cpu usage
    
    hires_graphs="false"
    
     
    
    #* Enable the use of psutil python3 module for data collection, default on OSX
    
    use_psutil="true"

## 工具运行截图

### 工具主UI界面将显示选中进程的资源消耗细节：

![](https://image.3001.net/images/20200926/1601116983_5f6f1b374302c3b1745d8.png!small)

### 工具主菜单：

![](https://image.3001.net/images/20200926/1601116989_5f6f1b3d067ddb8a474fb.png!small)

### 工具选项菜单：

![](https://image.3001.net/images/20200926/1601116994_5f6f1b42742d9dec10f13.png!small)

## 项目地址

Bashtop：【[ _GitHub传送门_](https://github.com/aristocratos/bashtop)】

