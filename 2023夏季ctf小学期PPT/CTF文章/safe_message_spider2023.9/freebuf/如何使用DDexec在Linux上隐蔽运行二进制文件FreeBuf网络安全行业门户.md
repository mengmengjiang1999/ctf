![](https://image.3001.net/images/20220507/1651932968_62767f28e17d07fd95e67.jpeg!small)

## 关于DDexec

DDexec是一种能够在Linux上使用无文件技术和隐秘技术运行二进制文件的方法，它可以使用dd工具来将Shell替换为其他进程。

众所周知，在Linux上运行一个程序，则这个程序必须以一个文件的形式存在，而且必须能够通过文件系统层次结构并以某种方式访问到它，这也是execve()的工作机制。这样的一种文件可能位于磁盘中或RAM（tmpfs、memfd）中，但我们肯定需要一个文件路径。这种机制不仅使得我们可以轻松控制Linux系统中运行的内容，而且还可以轻松检测到安全威胁或攻击者植入的恶意程序，甚至还可以阻止攻击者尝试执行他们的任何工具，比如说不允许未经授权的用户将可执行文件放在任何地方。

但是，DDexec的出现改变了这种情况。

## 技术机制

>
> 1、大多数的Shell解释器都允许创建文件描述符，而这些文件描述符随后将被子进程继承。我们可以创建一个fd，并指向Shell（带有写入权限）的mem文件，此时子进程将使用这个fd并修改Shell的内存；
>
> 2、ASLR不会成为“拦路虎”，因为我们可以检查Shell的maps文件或其他信息来获取关于进程地址空间的相关信息；
>
> 3、使用lseek()来对文件进行查询，在Shell的帮助下，我们可以使用dd工具轻松实现；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/arget13/DDexec.git

## 依赖组件

该脚本依赖下列组件实现其功能：

> dd
>
> bash | zsh | ash (busybox)
>
> head
>
> tail
>
> cut
>
> grep
>
> od
>
> readlink
>
> wc
>
> tr
>
> base64

## 工具使用

将ddexec.sh注入到需要运行的Base64源代码中，注意不要有换行符出现。脚本的参数也就是程序的运行参数，以“argv[0]”开始。

下面给出的是一个使用样例：

    
    
    base64 -w0 /bin/ls | bash ddexec.sh /bin/ls -lA

项目中还提供了一个ddsc.sh脚本，该脚本允许我们直接运行二进制代码，下面给出的是一段“Hello world”的Shellcode：

    
    
    bash ddsc.sh -x <<< "4831c0fec089c7488d3510000000ba0c0000000f054831c089c7b03c0f0548656c6c6f20776f726c640a00"

或者：

    
    
    bash ddsc.sh < <(xxd -ps -r <<< "4831c0fec089c7488d3510000000ba0c0000000f054831c089c7b03c0f0548656c6c6f20776f726c640a00")

没错，这种方法也适用于Meterpreter。

该工具目前已经在Debian、Alpine和Arch平台上进行过测试，支持的Shell包括Bash、zsh和ash，且支持x86_64和aarch64（arm64）架构。

## 许可证协议

本项目的开发与发布遵循[ _GP_
_L-3.0_](https://github.com/arget13/DDexec/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **DDexec：** 【[ _GitHub传送门_](https://github.com/arget13/DDexec)】

## 参考资料

> [
> _https://porkmail.org/era/unix/award.html_](https://porkmail.org/era/unix/award.html)
>
> [ _https://www.sektor7.net/_](https://www.sektor7.net/)
>
> [ _https://blog.sektor7.net/#!res/2018/pure-in-memory-> linux.md_](https://blog.sektor7.net/#!res/2018/pure-in-memory-linux.md)
>
> [ _https://github.com/carlospolop_](https://github.com/carlospolop)
>
> [ _https://book.hacktricks.xyz/_](https://book.hacktricks.xyz/)
>
> [ _https://github.com/carlospolop/PEASS-> ng_](https://github.com/carlospolop/PEASS-ng)
>
> [ _https://rootedcon.com/_](https://rootedcon.com/)

