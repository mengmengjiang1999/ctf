## 一 背景介绍

Linux作为服务器和IoT设备使用的主要操作系统,针对它的恶意软件也层出不穷。针对Linux设备的恶意软件通常需要长期驻留于目标操作系统以达到获利目的，本篇文章对Linux服务器恶意软件（以下称为rootkit）可能的驻留思路进行了介绍和分析。

在接下来的说明中，我们统一使用一个名为evil的静态链接ELF文件作为我们要实现驻留的rootkit，所有的驻留尝试均围绕这个程序展开。

## 二 技术汇总

## 2.1 用户态下的可利用点

### 2.1.1 各种init的利用

#### Linux init

在systemd成为主流之前，sysvinit是大多数发行版的选择，即使是Ubuntu之前使用的upstart，和sysvinit也是完全兼容的，直到今天，Debian系发行版仍保留sysvinit的兼容性。作为Linux的init程序，也就是PID
1，负责启动之后的所有进程，所有的服务都是由它管理，因此它是实现rootkit驻留的最常见手段。

对于传统的sysvinit，常见的驻留点都需要以root身份写入：

    
    
    /etc/init.d
    /etc/rc[runlevel].d
    /etc/rc.local
    

其实sysv的服务文件就是遵循sysv规范的shell脚本，它在嵌入式设备中也很常见。给出一个sysv风格的服务文件如下：

    
    
    #!/bin/sh
    
    PATH=/bin:/usr/bin:/sbin:/usr/sbin
    DESC="cron daemon"
    NAME=cron
    DAEMON=/usr/sbin/cron
    PIDFILE=/var/run/crond.pid
    SCRIPTNAME=/etc/init.d/"$NAME"
    
    test -f $DAEMON || exit 0
    
    . /lib/lsb/init-functions
    
    [ -r /etc/default/cron ] && . /etc/default/cron
    
    parse_environment() {
        for ENV_FILE in /etc/environment /etc/default/locale; do
            [ -r "$ENV_FILE" ] || continue
            [ -s "$ENV_FILE" ] || continue
    
            for var in LANG LANGUAGE LC_ALL LC_CTYPE; do
                value=$(egrep "^${var}=" "$ENV_FILE" | tail -n1 | cut -d= -f2)
                [ -n "$value" ] && eval export $var=$value
    
                if [ -n "$value" ] && [ "$ENV_FILE" = /etc/environment ]; then
                    log_warning_msg "/etc/environment has been deprecated for locale information; use /etc/default/locale for $var=$value instead"
                fi
            done
        done
    
        # Get the timezone set.
        if [ -z "$TZ" -a -e /etc/timezone ]; then
            TZ=$(cat /etc/timezone)
        fi
    }
    
    # Parse the system's environment
    if [ "$READ_ENV" = "yes" ]; then
        parse_environment
    fi
    
    case "$1" in
    start)
        log_daemon_msg "Starting periodic command scheduler" "cron" # 这一行是我们修改的目标
        start_daemon -p $PIDFILE $DAEMON $EXTRA_OPTS
        log_end_msg $?
        ;;
    stop)
        log_daemon_msg "Stopping periodic command scheduler" "cron"
        killproc -p $PIDFILE $DAEMON
        RETVAL=$?
        [ $RETVAL -eq 0 ] && [ -e "$PIDFILE" ] && rm -f $PIDFILE
        log_end_msg $RETVAL
        ;;
    restart)
        log_daemon_msg "Restarting periodic command scheduler" "cron"
        $0 stop
        $0 start
        ;;
    reload | force-reload)
        log_daemon_msg "Reloading configuration files for periodic command scheduler" "cron"
        # cron reloads automatically
        log_end_msg 0
        ;;
    status)
        status_of_proc -p $PIDFILE $DAEMON $NAME && exit 0 || exit $?
        ;;
    *)
        log_action_msg "Usage: /etc/init.d/cron {start|stop|status|restart|reload|force-reload}"
        exit 2
        ;;
    esac
    exit 0
    

我们在start case中做些修改，使之在启动时执行我们的evil程序：

![image.png](https://image.3001.net/images/20181031/1540976444_5bd96f3cb603c.png!small)

对于systemd，我们可以用更多手段实现驻留，甚至不需要root权限也可以：

    
    
    /etc/systemd/system
    /etc/systemd/user
    /lib/systemd/system
    /lib/systemd/user
    ~/.local/share/systemd/user
    ~/.config/systemd/user
    

以下是一个利用systemd服务文件的示例：

![image.png](https://image.3001.net/images/20181031/1540976662_5bd9701624fa7.png!small)

`systemctl --user enable service`可以使服务随用户登录启动，`systemctl enable
service`可以让服务随系统启动。

#### bashrc

`bashrc`或者`zshrc`等文件会随着shell的运行而被执行，利用时只需在里面加入恶意的shell script即可。

常见位置：

    
    
    /etc/profile
    ~/.bashrc
    ~/.bash_profile
    ~/.bash_logout
    

示例如下：

![image.png](https://image.3001.net/images/20181031/1540977215_5bd9723f08a66.png!small)

#### xinitrc

如果目标主机有安装Xorg，我们也可以以下位置写入shell script实现rootkit驻留，不需要root权限。

    
    
    ～/.xinitrc
    ~/.xserverrc
    /etc/X11/xinit/xinitrc
    /etc/X11/xinit/xserverrc
    

#### 其它initrc

任何应用程序都可能在启动时执行代码，而且它们很可能会执行用户`home`目录的rc文件。例如，我们甚至可以在`vimrc`里
写入vimscript来执行代码实现rookit的驻留，这同样不需要root权限。

一个可能的示例如下：

![image.png](https://image.3001.net/images/20181031/1540980014_5bd97d2e781df.png!small)

### 2.1.2 图形化环境的利用

虽然标准的服务器版Linux发行版是不会预装Xorg的，但还是存在相当一部分用户使用CentOS预装gnome2的版本作为服务器操
作系统。因此，基于gnome等桌面环境和Xorg的驻留有时候也是重要的而且会容易被忽略的手段。

#### XDG autostart for system

`/etc/xdg/autostart`下的desktop文件会被主流桌面环境在启动时执行。一个可能的示例如下：

![image.png](https://image.3001.net/images/20181031/1540980146_5bd97db25f4ee.png!small)

#### XDG autostart for user

类似的，用户可以在自己的`~/.config/autostart`目录下加入需要自启动的desktop文件。

### 2.1.3 crond的利用

这是一个很常见的驻留点，但需要注意的是，很多恶意软件并不仅仅会把自己写入用户的crontab（如`/var/spool/cron/root`），它们会把自己写入软件包使用的crontab里面，如`/etc/cron.d`，这样更不容易引起用户注意。

![image.png](https://image.3001.net/images/20181031/1540981769_5bd98409959cf.png!small)

### 2.1.4 替换文件

替换或者patch一些会被服务或用户本身执行的程序文件，以同时执行恶意代码，也是很常见的驻留方式。

我们可以方便的获取到开源项目的源码，进行修改，加上我们的恶意代码并重新编译，替换目标系统的相应文件。这样我们的代码就会随之执行。

下面我们修改openssh portable 7.9的源码，使之在特定条件下执行我们的代码：

![image.png](https://image.3001.net/images/20181031/1540981939_5bd984b3319ce.png!small)

这里修改的函数是`uncompress_buffer`，用于处理压缩传输的ssh连接。我们需要触发它的时候，只需发起一个`ssh -C`即可。

![image.png](https://image.3001.net/images/20181031/1540981790_5bd9841eda266.png!small)

如果没有源码，我们同样可以给现有的binary注入shellcode，不过这种实现达到的功能相对有限，且可能会导致原文件损坏 。下面使用`backdoor-factory`进行shellcode注入，这个工具支持自定义shellcode：

![image.png](https://image.3001.net/images/20181031/1540981652_5bd98394b2de5.png!small)

如果我们的目标主机是git或svn服务器，有机会接触到项目源码的话，也可以通过修改目标的源码植入恶意代码，或者把编译环境动手脚，在项目构建时插入恶意代码，比如在`configure`脚本里或者`Makefile`里插入代码，既可以在本机运行，又有可能在编译之后在更多主机（取决于项目用途）上运行，进一步扩大感染范围。这个思路也是当年中国xcode事件黑客的思路。

### 2.1.5 动态链接库劫持

#### 替换动态链接库

libc会被几乎所有的ELF调用，而特定的lib则会被特定的ELF调用，只要某个ELF的执行概率够高，我们同样可以用我们重新编译的恶意so替换掉它所链接的某个so文件，达到执行恶意代码的效果。

当然，以这种思路来看，替换掉整个libc也是未尝不可的。

下面以sshd的动态链接库为例，sshd使用的so文件如下：

![image.png](https://image.3001.net/images/20181031/1540980516_5bd97f242efa5.png!small)

`libz.so.1`看上去像是zlib的文件，可以验证一下：

![image.png](https://image.3001.net/images/20181031/1540980561_5bd97f51edab6.png!small)

那么我们可以去下载zlib源码，在可能会被调用的函数里加上我们的私货。

经过grep搜索openssh portable 7.9的源码，可以看到`packet.c`使用了zlib的函数：

![image.png](https://image.3001.net/images/20181031/1540980691_5bd97fd3ada79.png!small)

确定了我们需要注入代码的函数，就可以去修改zlib源码了，在`inflate.c`的`inflate`函数里加入简单的`system`调用，来执行我们的evil程序：

![image.png](https://image.3001.net/images/20181031/1540989701_5bd9a3050739f.png!small)

完成修改之后我们make构建项目，然后用我们的恶意`libz.so`替换原本的文件。

此处修改的zlib，通常只会在ssh客户端指定了使用压缩时，才会被使用。所以我们需要使用`ssh -C`命令去测试。

![image.png](https://image.3001.net/images/20181031/1540981581_5bd9834de1bb3.png!small)

提醒一点，作为动态链接库，它们的函数可能被频繁调用，我们在利用的时候要避免造成不必要的负载。另外，由于大部分程序都是动态链接库文件，我们也需要格外小心，避免加入的代码调用的程序最终往回调用我们修改的库文件本身（尤其是在修改libc的时候），造成死循环，导致系统停止响应。

#### ld.so.preload

最常见的实现是在`/etc/ld.so.preload`中写入我们需要让libc执行的so文件，或者设置`LD_PRELOAD`环境变量，这样，任何依赖系统libc的user
space程序，都会在运行之前执行我们的so文件，从而实现了有效的rootkit驻留（鉴于几乎所有目标主
机都是动态编译的，几乎所有程序都要使用系统libc）。

下面我们编写一个简单的恶意so（shared object）作为说明：

这里的恶意so将编译为`libevil.so`。通常的lib都是为主程序提供库函数的，只有被调用的代码才会被执行，于是我们需要
解决的第一个问题是让我们的代码在lib被加载时直接自动运行。类似于Windows下的`DllMain`，gcc提供了function
attributes，我们可以用形如`__attribute__((constructor))`的attribute来达到目的。对应的，`__attribute__((destructor))`
则会在lib被unload的时候执行。

具体解释见官方文档：

![image.png](https://image.3001.net/images/20181031/1540981084_5bd9815c3ac6e.png!small)

我们使用如下代码构建libevil，这里有一个坑，`execl`函数只有出错时才返回，如果使用它执行了外部程序,那么在外部程
序执行完之后，libevil将会退出当前进程(也就是我们本来要执行的进程)，使任何ELF都无法正常执行。解决方法是使用​ `fork​`
函数创建子进程，在子进程里执行​`execl​`启动外部程序。

![image.png](https://image.3001.net/images/20181031/1540981151_5bd9819f2db11.png!small)

使用如下命令构建我们的​ `libevil.so​`:

![image.png](https://image.3001.net/images/20181031/1540981526_5bd9831687cbf.png!small)

设置`​LD_PRELOAD`​环境变量，使我们的libevil在`ld`执行任何ELF之前被执行。

![image.png](https://image.3001.net/images/20181031/1540981542_5bd98326cfe76.png!small)

需要注意的是，我们的libevil会在每个动态ELF执行之前被执行，如果在其中调用了外部的动态ELF，那个ELF执行时会再次调用libevil，就会造成死循环，使系统处于不可用状态。

我们也可以在libevil里实现rootkit的所有功能。

## 2.2 内核态的驻留

传统的rootkit就是指这类恶意软件，对于Linux rootkit来说，最有效的方法就是把自己作为kernel
module加载，因为大多数Linux目标都是允许动态加载kernel module的。

在kernel space里运行恶意代码的好处显而易见，由于大部分审计工具都在user
space运行，管理员通常很难发现恶意软件的存在，这就带来了上面的方法所不能达到的隐蔽性。

### 2.2.1 LKM - 可加载内核模块

目前有一些开源的LKM (Loadable Kernel Modules) 木马demo，比较有代表性的是Reptile，它使用自己的kernel
module实现了隐藏和驻留。

下面我们使用这个思路来实现一个简单的内核恶意代码执行：

这里的LKM实现比较简单，只是在加载和退出的时候执行了两个shell脚本，并使用printk输出了内核调试信息。我们只需定义两个函数分别用于initialize和exit即可完成LKM的主体框架了，module.h会有相应函数`module_init`和`module_exit`用来实现。

`MODULE_LICENSE`也需要设置，因为Linux是GPL授权，我们需要声明兼容的授权协议，否则Linux会提示tainted
kernel（虽然不影响正常使用，但会比较容易引起注意）。编译LKM的方法可以参考Linux内核文档，或者直接参考现有的LKM项目的Makefile，这里的Makefile内容如下：

![image.png](https://image.3001.net/images/20181031/1540981194_5bd981ca0fe7b.png!small)

LKM代码如下，使用user space helper达到了执行外部程序的目的：

![image.png](https://image.3001.net/images/20181031/1540981247_5bd981ffabad4.png!small)

使用`insmod`命令动态加载LKM到内核，立即生效：

![image.png](https://image.3001.net/images/20181031/1540981340_5bd9825cbb971.png!small)

下面是`dmesg`的相关输出：

![image.png](https://image.3001.net/images/20181031/1540981350_5bd9826663f6e.png!small)

LKM执行恶意代码有比较大的局限性，因为必须针对相同内核版本编译才能正常使用，从而引入了Linux
headers的依赖，实现大范围传播的难度较大。防范此类攻击（也是最危险和隐蔽的一种）的最有效方法就是关闭Linux的动态模块加载功能，对于大多数Linux服务器，关掉这个功能通常不会造成额外影响。

### 2.2.2 initrd的利用

Reptile会把自己写入`/etc/rc.modules`以便在系统启动时插入自己的module。但通过initrd实现更加隐蔽可靠。initrd即init
ram disk，用于提供一个基本的环境以便启动完整的Linux。

鉴于initrd很少受到关注和保护，它又一定会在启动时被加载入内存，我们可以在这个内存文件系统中插入自己的LKM并修改init脚本使我们的LKM在启动时被加载，从而实现恶意代码执行。

这里以Kali（Linux 4.18，基于Debian Sid）为例，分析可能的利用点：

下图是init脚本functions定义中，加载自定义kernel module的函数，我们可以把自己的LKM放到modules目录下（例如
`./usr/lib/modules/4.17.0-kali3-amd64/kernel`），然后在
`./conf/modules`里写上自己的LKM，我们的LKM就会随着initrd加载到内核。

或者我们也可以直接在`load_modules`函数内增加`modprobe`操作来加载恶意LKM。

![image.png](https://image.3001.net/images/20181031/1540981317_5bd98245f30cd.png!small)

## 三 总结

Linux下的恶意软件虽然种类不多，但就其驻留技术实现而言，还是有不少的方法。本文除了主流的实现之外，也提出了一些通常很少有人注意的实现方法，希望对Linux攻防对抗的朋友有所帮助。

## 四 参考链接

[
_https://wiki.archlinux.org/index.php/SysVinit_](https://wiki.archlinux.org/index.php/SysVinit)

[ _https://specifications.freedesktop.org/autostart-spec/autostart-spec-latest.html_](https://specifications.freedesktop.org/autostart-spec/autostart-spec-latest.html)

[ _https://en.wikipedia.org/wiki/Init_](https://en.wikipedia.org/wiki/Init)

[ _https://gcc.gnu.org/onlinedocs/gcc-4.7.0/gcc/Function-Attributes.html_](https://gcc.gnu.org/onlinedocs/gcc-4.7.0/gcc/Function-Attributes.html)

[
_http://www.ouah.org/LKM_HACKING.html_](http://www.ouah.org/LKM_HACKING.html)

[
_https://wiki.archlinux.org/index.php/Xinit_](https://wiki.archlinux.org/index.php/Xinit)

