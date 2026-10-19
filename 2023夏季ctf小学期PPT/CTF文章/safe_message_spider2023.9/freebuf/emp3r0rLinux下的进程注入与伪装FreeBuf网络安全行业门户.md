  * 背景  

  * 技术流程
    * 怎么调用dlopen  

    * 怎么注入  

  * 其他  

# 背景

距离[《emp3r0r：Linux用户打造的Linux后渗透框架》](https://www.freebuf.com/sectool/259079.html
"https://www.freebuf.com/sectool/259079.html")已经过了一年，本人继续发扬年初做更新（然后鸽一年）的优良传统，水一篇关于Linux进程注入的文章。

本文和我去年在安全客发表的Linux进程注入可能略有重合，但和上次不同的是，[emp3r0r](https://github.com/jm33-m0/emp3r0r
"https://github.com/jm33-m0/emp3r0r")加入了一个[用户态ELF加载器](https://github.com/jm33-m0/emp3r0r/tree/master/loader/elf
"https://github.com/jm33-m0/emp3r0r/tree/master/loader/elf")，将其编译为shared
library，并定义了`__attribute__((constructor))`以便被`dlopen`直接执行。不要问我为啥会执行，那是一个固定特性，而且你只能在使用`dl`家族的`open`时才会被`ld.so`加载执行，所以你如果要自己写个`dlopen`的话，你还得写个ELF加载器（等会儿，这个shared
library是干啥的来着？）

好接着讲，这个ELF加载器（就叫它`loader.so`吧）自然首先要被`dlopen`加载才行，然后我们的emp3r0r
agent就可以被加载到它所在的进程里执行了，对于`procfs`来说，这个被注入的进程还是原样，你用`ps`和`ss`这样的工具看到的所有活动也都是被注入的进程发出的。

先上个图吧，这是我刚写的新界面，各位大黑阔可以试用下。

![1644733200_6208a3100b2a469a2282e.png!small](https://image.3001.net/images/20220213/1644733200_6208a3100b2a469a2282e.png!small)

# 技术流程

## 怎么调用dlopen

上面说过了，我们不会去自己实现一个`dlopen`，那么就只能调用现成的了。众所周知，`dlopen`是`libdl.so`的一个导出函数，那么为了调用它，我们注入的目标进程必须是链接了`libdl.so`的，也就是说它得事先给我们准备好了。

但如果你看一下就会发现，很多进程是没有加载`libdl.so`的，毕竟谁闲着没事总跟外部`so`文件互动呢？好在我们还有其他选择，要知道`libc.so`是几乎每个Linux进程都会加载的，哪怕它自己静态链接了其他`libc.so`，道理也是一样的，那么`libc.so`怎么会有一个`dlopen`呢？严格来说它并没有，这个函数不是libc导出函数，而是它内部的一个函数，叫做`__libc_dlopen_mode`，属于是Glibc的一个`dlopen`实现。

道理懂了，那么我们怎么在目标进程的地址空间里找到`__libc_dlopen_mode`呢？首先它通常不会位于一个固定的地址，其次ASLR只是把base随机化，但offset是固定的，也就是说我们只要找到`libc.so`的base，就可以根据offset算出`__libc_dlopen_mode`的地址。

鉴于我们是直接在emp3r0r
agent里实现的，所以这个问题就很容易解决，直接读取`procfs`里的`/proc/pid/maps`文件就可以获取一切我们需要的东西。

![1644734477_6208a80d67c6687fa161e.png!small?1644734477861](https://image.3001.net/images/20220213/1644734477_6208a80d67c6687fa161e.png!small?1644734477861)

这就是我们要找的东西，从左到位依次是：起止地址（address），权限（permission），偏移量（offset），inode（不知道中文是啥，可以理解成文件系统的操作单位），长度，文件路径。

这里面我们需要关注的就是起始地址，offset，以及路径。

起始地址不必多说，就是我们要的base。权限呢必须带有`x`也就是执行权限，offset则是在当前base的基础上加上一个值，当计算`__libc_dlopen_mode`地址的时候，需要在考虑ELF镜像offset的基础上减去这个值。

## 怎么注入

GDB就可以直接调用进程里的任意函数，你可以在GDB里执行`print __libc_dlopen("loader.so",
2)`，然后GDB直接就会按照你的参数来调用。

但作为一个后渗透工具，不能指望别人还安装一个GDB吧？所以我就把这个部分自己实现了。

思路的话上面也说了，现在我们有了`__libc_dlopen_mode`的地址，剩下的工作就是shellcode了。

如果你还有疑问，没关系，emp3r0r已经实现了这部分，直接去看[代码](https://github.com/jm33-m0/emp3r0r/blob/6b917738d64ccb6c225deb3df5607f8b15717849/core/lib/agent/injector.go#L260
"https://github.com/jm33-m0/emp3r0r/blob/6b917738d64ccb6c225deb3df5607f8b15717849/core/lib/agent/injector.go#L260")吧。另外我实现的是动态shellcode，支持可变参数。

注入的思路很简单，就是和上次我在安全客发过的方法一样，使用`ptrace`把shellcode扔到`$rip`的位置，执行完了再把原先的register恢复了，当然你也可以不恢复，在我这里的话`loader.so`会在子进程里执行ELF，如果你不在乎原进程死活的话也可以在当前进程执行ELF。

这里主要讲讲shellcode，这个shellcode只需要做一件事：设置好`__libc_dlopen_mode`的参数，并按照给定的地址`call`进去。这个shellcode管杀不管埋，所以可能执行完不能干净的返回，不过没关系，哪怕挂了，我们也可以`wait`接住，然后`ptrace`恢复原先的registers（虽然也不干净），具体的cleanup工作我后续有空了再说吧。

![1644734407_6208a7c7c819cbab8b8dc.png!small?1644734408142](https://image.3001.net/images/20220213/1644734407_6208a7c7c819cbab8b8dc.png!small?1644734408142)

这里需要注意的是[stack alignment](https://community.intel.com/t5/Intel-ISA-Extensions/About-the-x64-stack-Alignment/m-p/881085
"https://community.intel.com/t5/Intel-ISA-Extensions/About-the-x64-stack-Alignment/m-p/881085")，push的字节数必须是16的整数倍，不足的话后面执行会挂。

由于文件路径和`__libc_dlopen_mode`地址都是动态的，我们需要把shellcode也弄成动态生成的。

首先把shellcode用`nasm`汇编器汇编成机器码，然后把字节dump出来。我有个脚本，调用`rasm2`实现。

![1644734309_6208a76547162ae07e751.png!small?1644734309556](https://image.3001.net/images/20220213/1644734309_6208a76547162ae07e751.png!small?1644734309556)

然后你就可以做一个shellcode模板，具体请参考[emp3r0r的源码](https://github.com/jm33-m0/emp3r0r/blob/master/core/lib/agent/shellcode.go
"https://github.com/jm33-m0/emp3r0r/blob/master/core/lib/agent/shellcode.go")。

![1644734351_6208a78f56164ee1f7ee5.png!small?1644734351703](https://image.3001.net/images/20220213/1644734351_6208a78f56164ee1f7ee5.png!small?1644734351703)``

另外如果需要调试shellcode的话，你可以使用GDB的`restore`功能，把shellcode二进制文件恢复到`$rip`下面，然后就可以很方便地观察执行情况。

执行`restore shellcode.bin binary $rip`然后继续执行即可。

![1644734962_6208a9f2299609a6fe6ab.png!small?1644734962734](https://image.3001.net/images/20220213/1644734962_6208a9f2299609a6fe6ab.png!small?1644734962734)

``

# 其他

上述技术细节虽然不够详细，但鉴于已经开源，我就不废那么多话了。效果图就是开头的那个截图，不难看到，emp3r0r的代码已经在`/sbin/init`里运行了，`loader.so`伪装成了`libpam.so`注入了systemd的进程。从进程角度来看，整个emp3r0r的活动都是systemd发出的。这个注入目前还不太稳定，需要进一步优化。

另外不知道你注意到没有，我用`tmux`实现了一个简单的终端分屏界面，这样emp3r0r的一些输出可以从主界面剥离，放到副窗口中，这样的副窗口还包括了一个内置的`bash`shell，会随着你选择的agent来变化。

“内置的`bash`shell”是啥呢？就是我把一个完整的纯静态`bash`可执行文件压缩并base64编码之后塞进emp3r0r，运行时自动释放。

另外我也编译了纯静态的`bettercap`，效果见[Github首页视频](https://github.com/jm33-m0/emp3r0r
"https://github.com/jm33-m0/emp3r0r")。

关于前些天挺火的CVE-2021-4034 PwnKit，我也写了个[武器化exploit](https://github.com/jm33-m0/go-lpe)，纯Go零依赖零BS（实名diss下那些说”如果目标环境没有gcc“的人，目标环境直接给你root得了，提权干什么）。已经集成进emp3r0r，以后会武器化更多的提权漏洞，敬请期待。

谢谢大家。

