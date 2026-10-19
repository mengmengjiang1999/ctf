# 开篇

在《智能硬件固件分析》中讲了关于固件静态分析部分，从常见的固件获取方式，以及拿到固件后如何分析，涉及到的相关工具，并最后完成自己的静态分析脚本；然后静态分析的弊端也是非常明显，具体可以看以前写的《APP动态分析-Eclipse调试》，《APP动态分析-AndroidStudio调试+IDA
我来了》，就是因为在移动端的静态分析完不成一部分工作，或者说很多问题要通过动态调试来发现，当时讲的动静态分析是根据移动端的分析目的角度来讲的，这里就简单补充一下静态跟动态的区别；

静态分析也就是反编译后看程序逻辑，但是对于较大的系统或者软件来说，可能会涉及到多线程、系统的状态或者无法定位到关键代码，只能通过检索的方式来一个个过滤需要查看的点；这个时候静态分析的方式就过于庞杂，也可能无法掌握所有的信息，此时就需要动态调试的方式，动态调试有助于我们对程序的执行流程进一步理解，可以看到每一步执行状态和相应的变化。

常见的动态调试工具如下：

  * gdb-multiarch
  * [Peda](https://github.com/longld/peda)
  * Frida
  * ptrace
  * strace
  * IDA Pro
  * Ghidra
  * Binary Ninja
  * Hopper

Linux环境下用的最多的调试工具是gdb，设置断点可以让程序在断点处暂停，供我们查看程序的状态。gdb提供三种类型断点，代码断点(breakpoint)、内存断点(watchpoint)和事件断点(catchpoint)。

## gdb是什么？

gdb全称“GNU symbolic debugger”，诞生于GUN计划，是linux下常用的程序调试器。

当下的 GDB 支持调试多种编程语言编写的程序，包括 C、C++、Go、Objective-C、OpenCL、Ada 等。实际场景中，GDB 更常用来调试
C 和 C++ 程序。

## gdb有什么用？

总的来说，借助 GDB 调试器可以实现以下几个功能（其实所有的调试工具都具备2 3 的功能）：

  1. 程序启动时，可以按照我们自定义的要求运行程序，例如设置参数和环境变量；
  2. 使被调试程序在指定代码处暂停运行，并查看当前程序的运行状态；
  3. 程序执行过程中，可以改变某个变量的值，还可以改变代码的执行顺序，从而尝试修改程序中出现的逻辑错误。 

先了解一下gdb常见的调试指令

调试指令

|

作用  
  
---|---  
  
b（break） 行号

|

在源代码指定的某一行设置断点，其中行号用于指定具体打断点的位置。  
  
r（run）

|

执行被调试的程序，其会自动在第一个断点处暂停执行。  
  
step

|

执行一行代码，而且进入函数内部  
  
print

|

print + 变量名：输出该变量名的值  
  
n（next）

|

令程序一行代码一行代码的执行。  
  
p（print） 变量名

|

打印指定变量的值  
  
l（list）

|

显示源程序代码的内容，包括各行代码所在的行号。  
  
clear

|

清除断点：clear + 要清除断点的行号  
  
continute

|

继续执行正在调试的程序  
  
q（quit）

|

终止调试。  
  
watch

|

watch + 变量名：监视一个变量的值  
  
kill

|

终止调试程序  
  
调试工具是软件开发其中的一步，对于开发PC软件通常系统已经继承了调试工具（比如Linux系统的GDB），很多开发软件直接支持对程序的调试如IDE，gdb和其他调试工具的区别在于，只有dos界面；Linux系统一般自带gdb工具，执行情况如下，用于执行和调试本地文件，但是无法用在嵌入式调试中，原因在于嵌入式架构以及远程调试；所以需要在知道嵌入式架构的情况下，单独编译一个gdbserver程序；

gdb源码包下载地址：http://ftp.gnu.org/gnu/gdb/

![1639712588_61bc074c7aadac846a027.png!small?1639712591135](https://image.3001.net/images/20211217/1639712588_61bc074c7aadac846a027.png!small?1639712591135)

## GDB本地调试

### 编译自己的文件

一份简单的源代码

![1639712607_61bc075fba1bd2b93a597.png!small?1639712608389](https://image.3001.net/images/20211217/1639712607_61bc075fba1bd2b93a597.png!small?1639712608389)

> #include<stdio.h>
>
> intmain(intargc,char*argv[])
>
> {
>
> if(1>= argc)
>
> {
>
> printf("usage:hello name\n");
>
> return0;
>
> }
>
> printf("Hello World %s!\n",argv[1]);
>
> return0;
>
> }

### 编译过程

有关编译过程的详细内容，这里推荐《程序员的自我修养-链接、装载与库》一书，建议每个开发者都可以看一看，就好像现在的演员都要看一下演员的自我修养一样，让自己静下心来细细阅读。或者可以看看我写的汇总《程序员的自我修养-链接、装载与库》-gcc编译流程。

![1639712622_61bc076ebafa7cc30266c.png!small?1639712623508](https://image.3001.net/images/20211217/1639712622_61bc076ebafa7cc30266c.png!small?1639712623508)

## GDB本地调试

调试连接，并执行run，可以看到执行结果；

![1639712637_61bc077db645e19e2c340.png!small?1639712639525](https://image.3001.net/images/20211217/1639712637_61bc077db645e19e2c340.png!small?1639712639525)

### 简单的调试

![1639712716_61bc07ccd3ea2656e727d.png!small?1639712721906](https://image.3001.net/images/20211217/1639712716_61bc07ccd3ea2656e727d.png!small?1639712721906)

以上就简单的了解和操作gdb本地调试流程。

如果遇到程序已经运行了，怎么办？

可以先在系统中ps找到对应进程的id，然后进入gdb，通过attach 对应的pid来调试对应的进程；

## GDB远程调试

但是如果遇到嵌入式设备，设备上的系统又不带gdb调试工具，然后嵌入式开发调试工具也没有现成的，且嵌入式系统比较繁杂多样，这时候就需要我们通过gdb进行远程调试，在嵌入式设备上开启gdbserver，通过本地gdb连接gdbserver的方式来远程调试，gdbserver需要根据目标系统单独编译，并放到嵌入式设备系统下执行。

其实可能有些同学会想，为啥要用到gdbserver，我直接在设备系统上跑gdb不也一样的吗，没错，确实是一样的；只是有很多时候，设备性能不支持，比如内存不够等问题，使得在设备上跑不起gdb，从而gdbserver远程调试就诞生了，通过本地gdb远程连接gdbserver的方式来进行调试。

## gdbserver编译举例

在编译gdb之前，需要安装交叉编译工具链；这里以arm举例；

找到对应的交叉编译工具链；

将文件拷贝到指定的文件目录下面，我这里放/usr/local/arm

> export PATH=$PATH:/usr/local/arm/gcc-4.6.4/bin
>
> export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/arm/gcc-4.6.4/lib
>
> source ~/.zshrc

完成后执行验证；

![1639712775_61bc08079ae5f5b841b82.png!small?1639712778529](https://image.3001.net/images/20211217/1639712775_61bc08079ae5f5b841b82.png!small?1639712778529)

### gdb和gdbserver编译

> > wget <https://ftp.gnu.org/gnu/gdb/gdb-6.8a.tar.gz>
>
> > tar -xzvf gdb-6.8a.tar.gz
>
> > cd gdb-6.8
>
> > ../configure --target=arm-linux --prefix=$PWD
>
> > make
>
> > cd gdb-6.8a/gdb/gdbserver
>
> > mkdir arm-uclibc
>
> > cd arm-uclibc
>
> > ../configure --target=arm-linux --host=arm-linux --prefix=$PWD
>
> > make
>
> > make install
>
> > ls bin/
>
> > arm-linux-gdbserver

### 简单了解一下这几步的原理：

整个过程分为三步：

1.配置

configure 脚本负责在你使用的系统上准备好软件的构建环境。确保接下来的构建和安装过程所需要的依赖准备好，并且搞清楚使用这些依赖需要的东西。

Unix 程序一般是用 C 语言写的，所以我们通常需要一个 C
[编译器](https://www.zhihu.com/search?q=%E7%BC%96%E8%AF%91%E5%99%A8&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra=%7B%22sourceType%22%3A%22article%22%2C%22sourceId%22%3A77813702%7D)去构建它们。在这个例子中
configure 要做的就是确保系统中有 C 编译器，并确定它的名字和路径。

2.构建

当 configure 配置完毕后，可以使用 make 命令执行构建。这个过程会执行在 Makefile
文件中定义的一系列任务将软件源代码编译成可执行文件。

你下载的源码包一般没有一个最终的 Makefile
文件，一般是一个[模版文件](https://www.zhihu.com/search?q=%E6%A8%A1%E7%89%88%E6%96%87%E4%BB%B6&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra=%7B%22sourceType%22%3A%22article%22%2C%22sourceId%22%3A77813702%7D)Makefile.in
文件，然后 configure 根据系统的参数生成一个定制化的 Makefile 文件。

3.安装

现在软件已经被构建好并且可以执行，接下来要做的就是将可执行文件复制到最终的路径。make install
命令就是将可执行文件、第三方依赖包和文档复制到正确的路径。

这通常意味着，可执行文件被复制到某个 PATH 包含的路径，程序的调用文档被复制到某个 MANPATH
包含的路径，还有程序依赖的文件也会被存放在合适的路径。

因为安装这一步也是被定义在 Makefile 中，所以程序安装的路径可以通过 configure 命令的参数指定，或者 configure
通过系统参数决定。

如果要将可执行文件安装在[系统路径](https://www.zhihu.com/search?q=%E7%B3%BB%E7%BB%9F%E8%B7%AF%E5%BE%84&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra=%7B%22sourceType%22%3A%22article%22%2C%22sourceId%22%3A77813702%7D)，执行这步需要赋予相应的权限，一般是通过
sudo。

> configure配置解析
>
> └─$ ../configure --help
>
> `configure' configures this package to adapt to many kinds of systems.
>
>  
>
>
> Usage: ../configure [OPTION]... [VAR=VALUE]...
>
>  
>
>
> To assign environment variables (e.g., CC, CFLAGS...), specify them as
>
> VAR=VALUE. See below for descriptions of some of the useful variables.
>
>  
>
>
> Defaults for the options are specified in brackets.
>
>  
>
>
> Configuration:
>
> -h, --help display this help and exit
>
> \--help=short display options specific to this package
>
> \--help=recursive display the short help of all the included packages
>
> -V, --version display version information and exit
>
> -q, --quiet, --silent do not print `checking...' messages
>
> \--cache-file=FILE cache test results in FILE [disabled]
>
> -C, --config-cache alias for `--cache-file=config.cache'
>
> -n, --no-create do not create output files
>
> \--srcdir=DIR find the sources in DIR [configure dir or `..']
>
>  
>
>
> Installation directories:
>
> \--prefix=PREFIX install architecture-independent files in PREFIX
>
> [/usr/local]
>
> \--exec-prefix=EPREFIX install architecture-dependent files in EPREFIX
>
> [PREFIX]
>
>  
>
>
> By default, `make install' will install all the files in
>
> `/usr/local/bin', `/usr/local/lib' etc. You can specify
>
> an installation prefix other than `/usr/local' using `--prefix',
>
> for instance `--prefix=$HOME'.
>
>  
>
>
> For better control, use the options below.
>
>  
>
>
> Fine tuning of the installation directories:
>
> \--bindir=DIR user executables [EPREFIX/bin]
>
> \--sbindir=DIR system admin executables [EPREFIX/sbin]
>
> \--libexecdir=DIR program executables [EPREFIX/libexec]
>
> \--datadir=DIR read-only architecture-independent data [PREFIX/share]
>
> \--sysconfdir=DIR read-only single-machine data [PREFIX/etc]
>
> \--sharedstatedir=DIR modifiable architecture-independent data [PREFIX/com]
>
> \--localstatedir=DIR modifiable single-machine data [PREFIX/var]
>
> \--libdir=DIR object code libraries [EPREFIX/lib]
>
> \--includedir=DIR C header files [PREFIX/include]
>
> \--oldincludedir=DIR C header files for non-gcc [/usr/include]
>
> \--infodir=DIR info documentation [PREFIX/info]
>
> \--mandir=DIR man documentation [PREFIX/man]
>
>  
>
>
> Program names:
>
> \--program-prefix=PREFIX prepend PREFIX to installed program names
>
> \--program-suffix=SUFFIX append SUFFIX to installed program names
>
> \--program-transform-name=PROGRAM run sed PROGRAM on installed program names
>
>  
>
>
> System types:
>
> \--build=BUILD configure for building on BUILD [guessed]
>
> \--host=HOST cross-compile to build programs to run on HOST [BUILD]
>
> \--target=TARGET configure for building compilers for TARGET [HOST]
>
>  
>
>
> Some influential environment variables:
>
> CC C compiler command
>
> CFLAGS C compiler flags
>
> LDFLAGS linker flags, e.g. -L<lib dir> if you have libraries in a
>
> nonstandard directory <lib dir>
>
> CPPFLAGS C/C++ preprocessor flags, e.g. -I<include dir> if you have
>
> headers in a nonstandard directory <include dir>
>
> CPP C preprocessor
>
>  
>
>
> Use these variables to override the choices made by `configure' or to help
>
> it to find libraries and programs with nonstandard names/locations.

# 实践：做道PWN

![1639712927_61bc089f2df75c7135599.png!small?1639712927728](https://image.3001.net/images/20211217/1639712927_61bc089f2df75c7135599.png!small?1639712927728)

下载附件，简单查看一下执行文件的架构和编译情况；

![1639712950_61bc08b6d621f8fbe45d0.png!small?1639712951306](https://image.3001.net/images/20211217/1639712950_61bc08b6d621f8fbe45d0.png!small?1639712951306)

![1639712970_61bc08ca2b3c6d18a246b.png!small?1639712970617](https://image.3001.net/images/20211217/1639712970_61bc08ca2b3c6d18a246b.png!small?1639712970617)

直接用64位的ida打开看看；

看到main函数，很明显，两个地方都有溢出的问题；(可以查看C、C++不安全的函数）

![1639712986_61bc08da8855ac04d5914.png!small?1639712987388](https://image.3001.net/images/20211217/1639712986_61bc08da8855ac04d5914.png!small?1639712987388)

继续看其他的，可以看到sub_40060D()函数直接执行查看flag.txt文件，思路很明确，溢出覆盖偏移到sub_40060D()函数的位置，直接执行查看flag.txt;

![1639713000_61bc08e87998746dfdb8a.png!small?1639713001260](https://image.3001.net/images/20211217/1639713000_61bc08e87998746dfdb8a.png!small?1639713001260)

生成一个200字符的字符串，用来判断溢出点到返回地址的偏移；

![1639713069_61bc092d7174ba3b9f5cf.png!small?1639713076908](https://image.3001.net/images/20211217/1639713069_61bc092d7174ba3b9f5cf.png!small?1639713076908)

可以看到RBP已经被输出的内容覆盖；

这里了解一下RBP寄存器，x86-64的寄存器有：rax，rbx，rcx，rdx，rbp，rsp，rsi，rdi，r8，r9，r10，r11，r12，r13，r14，r15。

  * 栈寄存器：RBP：栈基址寄存器，RSP：栈顶指针寄存器
  * RIP：指令寄存器
  * 参数传递的前六个参数通过RDI，RSI，RDX，RCX，R8，R9这6个寄存器传递，其余参数通过栈空间传递

（其实这些都是大学学过的内容，就是不常用所以就容易忘记）

![1639713089_61bc09419258adc1da1bd.png!small?1639713090136](https://image.3001.net/images/20211217/1639713089_61bc09419258adc1da1bd.png!small?1639713090136)

通过计算当前RBP下AAdAA3AA的字符串所在的偏移位置，可以看到是64，所以在输入64个字节后，接下来的8个字符就会修改RIP的值，控制程序执行流，也就是常见的ret2text；

我们找到sub_40060D函数的位置；

![1639713118_61bc095e6dc70c59421db.png!small?1639713121371](https://image.3001.net/images/20211217/1639713118_61bc095e6dc70c59421db.png!small?1639713121371)

## 构造利用脚本

pwntool说明文档：https://docs.pwntools.com/en/stable/

pwntools是一个CTF框架和exploit开发库。它用 Python 编写，专为快速原型设计和开发而设计，旨在使漏洞利用编写尽可能简单。

根据pwntools工具的接口函数，构造以下脚步

> from pwn import *
>
> r=remote("node4.buuoj.cn",27741)
>
> flag_addr=0x40060D
>
> print(type(p64(flag_addr)))
>
> r.sendline(b'a'*(0x48)+p64(flag_addr))
>
> r.interactive()

![1639713149_61bc097df184c3c0d0467.png!small?1639713153009](https://image.3001.net/images/20211217/1639713149_61bc097df184c3c0d0467.png!small?1639713153009)

## 总结

静态分析和动态调试是相辅相成的，两者是协助作用，有些场景直接静态分析就可以看到结果，有些需要在动态调试的操作下才可以分析出来；后续为大家带来GDB插件，以及misp架构的远程调试分析。

> 参考：http://c.biancheng.net/gdb/
>
> 参考：https://liwugang.github.io/2020/05/10/gdb_break.html
>
> 参考：https://blog.csdn.net/qq_35031421/article/details/108557903
>
> 参考：https://zhuanlan.zhihu.com/p/77813702

