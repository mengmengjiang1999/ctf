![](https://image.3001.net/images/20201105/1604566720_5fa3bec0c21d28018bc97.png!small)

## Bpytop

Bpytop是一款功能强大的Linux/OSX/FreeBSD资源监控工具，该工具可以显示目标系统中的资源用量和处理器状态，其中包括内存用量、磁盘空间、网络流量和进程状态。

## 功能介绍

> 易于使用，带有一个交互性极强的菜单系统；
>
> 完整的鼠标支持，所有的按钮都高亮显示并且可点击，还支持鼠标滚动进程列表以及菜单栏；
>
> 快速响应式UI，可使用小键盘上下键切换进程；
>
> 可显示选中进程的完整状态信息；
>
> 支持过滤进程，支持多重过滤；
>
> 可轻松切换排序选项；
>
> 可向选中进程发送SIGTERM、SIGKILL和SIGINT；
>
> 提供了UI菜单来修改所有的配置文件；
>
> 自动生成可缩放的网络用量图；
>
> 如果检测到了新版本，则会在工具菜单中显示；
>
> 显示磁盘当前的读写速度；

## 主题支持

Bpytop使用的主题文件跟bashtop相同，所以bashtop支持的主题文件Bpytop也可以使用。点击【[
_这里_](https://github.com/aristocratos/bpytop/tree/master/themes)】查看所有支持的主题文件。

如果使用make
install命令安装的话，主题文件会默认存放在/usr/local/share/bpytop/themes中。如果使用pip3命令安装的话，主题将会存放在一个名为bpytop-themes的目录下。用户自己创建的主题应该存放在$HOME/.config/bpytop/themes路径下。

## 工具依赖

  * Python 3（6或更高版本）；
  * Psutil模块（7.0或更高版本）；

## 工具安装

### PyPi（只安装最新版本）

    
    
    pip3 install bpytop --upgrade

### Arch Linux

    
    
    https://aur.archlinux.org/packages/bpytop/

### Debian

    
    
    sudo apt install bpytop

### FreeBSD包

    
    
    sudo pkg install bpytop

### Fedora/CenOS 8包

    
    
    sudo dnf install bpytop

### Gentoo/Calculate Linux

    
    
    sudo emerge -av sys-process/bpytop

### Mageia Cauldron（Mageia 8）

    
    
    sudo urpmi bpytop
    
    sudo dnf install bpytop

### MX Linux

    
    
    http://mxrepo.com/mx/testrepo/pool/test/b/bpytop/

## 手动安装

    
    
    git clone https://github.com/aristocratos/bpytop.git
    
    cd bpytop
    
    sudo make install

### 工具卸载

    
    
    sudo make uninstall

## 工具配置

该工具所有的配置选项都可以通过UI界面来进行配置和修改，其中的配置文件存储在"$HOME/.config/bpytop"目录中。配置文件将自动生成，文件名为bpytop.cfg（/etc/bpytop.conf将作为配置文件生成的默认种子）：

    
    
    #? Config file for bpytop v. 1.0.22
    
     
    
    #* Color theme, looks for a .theme file in "/usr/[local/]share/bpytop/themes" and "~/.config/bpytop/themes", "Default" for builtin default theme.
    
    #* Prefix name by a plus sign (+) for a theme located in user themes folder, i.e. color_theme="+monokai"
    
    color_theme="Default"
    
     
    
    #* If the theme set background should be shown, set to False if you want terminal background transparency
    
    theme_background=False
    
     
    
    #* Set bpytop view mode, "full" for everything shown, "proc" for cpu stats and processes, "stat" for cpu, mem, disks and net stats shown.
    
    view_mode=full
    
     
    
    #* Update time in milliseconds, increases automatically if set below internal loops processing time, recommended 2000 ms or above for better sample times for graphs.
    
    update_ms=2000
    
     
    
    #* Processes sorting, "pid" "program" "arguments" "threads" "user" "memory" "cpu lazy" "cpu responsive",
    
    #* "cpu lazy" updates top process over time, "cpu responsive" updates top process directly.
    
    proc_sorting="cpu lazy"
    
     
    
    #* Reverse sorting order, True or False.
    
    proc_reversed=False
    
     
    
    #* Show processes as a tree
    
    proc_tree=False
    
     
    
    #* Use the cpu graph colors in the process list.
    
    proc_colors=True
    
     
    
    #* Use a darkening gradient in the process list.
    
    proc_gradient=True
    
     
    
    #* If process cpu usage should be of the core it's running on or usage of the total available cpu power.
    
    proc_per_core=True
    
     
    
    #* Show process memory as bytes instead of percent
    
    proc_mem_bytes=True
    
     
    
    #* Check cpu temperature, needs "osx-cpu-temp" on MacOS X.
    
    check_temp=True
    
     
    
    #* Draw a clock at top of screen, formatting according to strftime, empty string to disable.
    
    draw_clock="%X"
    
     
    
    #* Update main ui in background when menus are showing, set this to false if the menus is flickering too much for comfort.
    
    background_update=True
    
     
    
    #* Custom cpu model name, empty string to disable.
    
    custom_cpu_name=""
    
     
    
    #* Optional filter for shown disks, should be last folder in path of a mountpoint, "root" replaces "/", separate multiple values with comma.
    
    #* Begin line with "exclude=" to change to exclude filter, oterwise defaults to "most include" filter. Example: disks_filter="exclude=boot, home"
    
    disks_filter=""
    
     
    
    #* Show graphs instead of meters for memory values.
    
    mem_graphs=True
    
     
    
    #* If swap memory should be shown in memory box.
    
    show_swap=True
    
     
    
    #* Show swap as a disk, ignores show_swap value above, inserts itself after first disk.
    
    swap_disk=True
    
     
    
    #* If mem box should be split to also show disks info.
    
    show_disks=True
    
     
    
    #* Set fixed values for network graphs, default "10M" = 10 Mibibytes, possible units "K", "M", "G", append with "bit" for bits instead of bytes, i.e "100mbit"
    
    net_download="100Mbit"
    
    net_upload="100Mbit"
    
     
    
    #* Start in network graphs auto rescaling mode, ignores any values set above and rescales down to 10 Kibibytes at the lowest.
    
    net_auto=True
    
     
    
    #* Sync the scaling for download and upload to whichever currently has the highest scale
    
    net_sync=False
    
     
    
    #* If the network graphs color gradient should scale to bandwith usage or auto scale, bandwith usage is based on "net_download" and "net_upload" values
    
    net_color_fixed=False
    
     
    
    #* Show init screen at startup, the init screen is purely cosmetical
    
    show_init=False
    
     
    
    #* Enable check for new version from github.com/aristocratos/bpytop at start.
    
    update_check=True
    
     
    
    #* Set loglevel for "~/.config/bpytop/error.log" levels are: "ERROR" "WARNING" "INFO" "DEBUG".
    
    #* The level set includes all lower levels, i.e. "DEBUG" will show all logging info.
    
    log_level=WARNING

## 命令行选项

    
    
    USAGE: bpytop [argument]
    
     
    
    Arguments:
    
        -f, --full            Start in full mode showing all boxes [default]
    
        -p, --proc            Start in minimal mode without memory and net boxes
    
        -s, --stat            Start in minimal mode without process box
    
        -v, --version         Show version info and exit
    
        -h, --help            Show this help message and exit
    
        --debug               Start with loglevel set to DEBUG overriding value set in config

## 工具运行截图

### 工具主界面将显示选中进程的资源使用情况：

![](https://image.3001.net/images/20201105/1604566829_5fa3bf2d494d1d7c94cc1.png!small)

### 主界面的迷你模式：

![](https://image.3001.net/images/20201105/1604566836_5fa3bf341ed23a058b4e7.png!small)

### 工具主菜单：

![](https://image.3001.net/images/20201105/1604566846_5fa3bf3ed48225a4990da.png!small)

### 工具选项菜单：

![](https://image.3001.net/images/20201105/1604566854_5fa3bf469f3bd6b8f1bdd.png!small)

## 依赖包版本

![](https://image.3001.net/images/20201105/1604566878_5fa3bf5e8c874b8f6f644.png!small)

## 许可证协议

本项目的开发与发布遵循[ _Apache Lisense
2.0_](https://github.com/aristocratos/bpytop/blob/master/LICENSE)开源许可证协议。

## 项目地址

Bpytop：【[ _GitHub传送门_](https://github.com/aristocratos/bpytop)】

