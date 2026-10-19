## 关于pamspy

pamspy是一款基于eBPF的Linux凭证转储工具，该工具的功能与[ _3_
_snake_](https://github.com/blendin/3snake)类似，但pamspy使用了eBPF技术，可以帮助广大研究人员更好地获取和导出Linux系统中的相关凭证信息。

该工具可以跟踪PAM（可插入的身份验证模块）库中的特定用户空间函数，而这个库以及相关的函数是很多关键应用程序在处理身份验证时都会使用到的，比如说：

> sudo
>
> sshd
>
> passwd
>
> gnome
>
> x11
>
> ......

## 运行机制

pamspy首先会加载一个用户空间的eBPF程序，并通过libpam.so并在pam_get_authtok函数中设置一个钩子。PAM表示“Pluggable
Authentication Modules”，即可插入的身份验证模块，而这个模块的实现非常灵活，可以处理Linux上各种不同类型的身份验证机制。

每当身份验证进程想要尝试验证一个新用户时，它都会调用pam_get_authtok函数，此时pamspy就可以导出关键敏感信息中的内容了。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/citronneur/pamspy.git

除此之外，我们也可以直接访问该项目的【[
_Releases页面_](https://github.com/citronneur/pamspy/releases/)】来获取项目静态代码。

## 项目构建

在构建项目静态代码时，我们还需要使用到第三方程序组件。对于eBPF，我们需要使用clang来将C代码编译为eBPF CO-RE代码。除此之外，我们还需要使用bpftool来为eBPF程序创建一个框架，其中将包含我们的用户空间程序，并使用libelf来寻找libpam中正确的符号：

    
    
    sudo apt install make clang-11 gcc libelf-dev bpftool

接下来，使用下列命令即可编译项目代码：

    
    
    git clone https://github.com/citronneur/pamspy --recursive
    
    cd pamspy/src
    
    make

## 工具使用

### 工具帮助信息

    
    
    Usage: pamspy [OPTION...]
    
    pamspy
    
     
    
    Uses eBPF to dump secrets use by PAM (Authentication) module
    
    By hooking the pam_get_authtok function in libpam.so
    
     
    
    USAGE: ./pamspy -p $(/usr/sbin/ldconfig -p | grep libpam.so | cut -d ' ' -f4) -d /var/log/trace.0
    
     
    
      -d, --daemon=PATH TO OUTPUT CREDENTIALS
    
                                 以守护进程模式启动pamspy，并将结果输出至文件
    
      -p, --path=PATH            libpam.so文件的路径
    
      -r, --print-headers           打印目标程序的Header
    
      -v, --verbose               开启Verbose模式
    
      -?, --help                  获取工具帮助信息
    
          --usage                提供简单的使用帮助信息
    
      -V, --version                打印工具版本信息
    
     
    
    Mandatory or optional arguments to long options are also mandatory or optional
    
    for any corresponding short options.
    
     
    
    Report bugs to .

### 使用演示

由于pamspy基于libpam实现其功能，因此我们首先需要设置libpam在你操作系统上的安装路径。我们可以使用下列命令找到libpam的安装路径：

    
    
    > /usr/sbin/ldconfig -p | grep libpam.so | cut -d ' ' -f4
    
    /lib/x86_64-linux-gnu/libpam.so.0

当你拿到了libpam的安装路径之后，就可以通过下列命令运行pamspy了：

    
    
    > ./pamspy -p /lib/x86_64-linux-gnu/libpam.so.0

下面这种方法也可以运行pamspy：

    
    
    > ./pamspy -p $(/usr/sbin/ldconfig -p | grep libpam.so | cut -d ' ' -f4)

pamspy也能够以守护进程的方式启动，此时需要提供凭证写入的输出文件地址：

    
    
    ./pamspy -p $(/usr/sbin/ldconfig -p | grep libpam.so | cut -d ' ' -f4) -d /tmp/credentials

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_-2.0_](https://github.com/citronneur/pamspy/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **pamspy** ：【[ _GitHub传送门_](https://github.com/citronneur/pamspy)】

## 参考资料

> [ _https://github.com/blendin/3snake_](https://github.com/blendin/3snake)

