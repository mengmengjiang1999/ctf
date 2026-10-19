## 0x10 基本原理

Syzkaller 是一个白盒 fuzzing 工具，利用系统调用对内核进行 fuzzing。 Syzkaller
优势在于会根据内核的代码路径覆盖信息来更新 fuzz 用的变异数据，以达到尽可能大的代码覆盖率。

![image](https://image.3001.net/images/20210820/1629451107_611f736353430affb0c64.png!small)

>  **syz-manager** : 运行在 PC 上的主控程序。负责 fuzzing 调度、异常判断、问题复现和日志记录等。测试者通过 syz-> manager 启动测试。 通过 **ssh adb** 等方式发送`syz-fuzzer`可执行文件并到虚拟机中并启动。syz-manager
> 还会开启一个简单的 Web 服务，可查看当前的 fuzz 状态。
>
>  **syz-fuzzer** : 进行 fuzzing
> 的主程序，根据文件系统`/sys/kernel/debug/kcov`获取内核代码覆盖率，并且生成新的变异数据，然后调用 syz-executor。
>
>  **syz-executor** : 执行模块，根据 syz-fuzzer 传入的数据，执行系统调用。

源码目录结构

bin| 编译后生成的可执行文件所在目录  
---|---  
extract_arm64.sh| 编译 txt 用的脚本  
Godeps| syzkaller 依赖 Go 语言库（节省了大量自己去外面找依赖库的时间）  
sys| 存放系统调用定制的目录（含驱动定制），以及编译txt用到的工具  
pkg| 公共库  
syz-manager| syz-manager 代码目录  
syz-fuzzer| sys-fuzzer 代码目录  
executor| sys-executor 代码目录  
prog| program 解析和生成相关代码目录  
tools| 其它工具的源码  
vm| 被测对象操控相关处理的代码存放路径，手机用的就是 adb 目录下的 adb.go；vm.go是所有 vm 的抽象接口，供 syz-manager
调用  
  
## 0x20 编译内核

我们以 goldfish 为例，其他 Android 真机内核也是一样的（各个 Android 手机厂商的开发也可能会有自己的编译环境）。什么是
goldfish？gold 项目包含适用于 **模拟平台** 的内核源代码

> Google 使用 QEMU 模拟的是 ARM926ej-S 的 Goldfish 处理器，Android 中所指的 goldfish
> 就可以理解为一个虚拟的arm处理器，也就是模拟器的名字，在代码层面表现为 **适配 goldfish 处理器的内核** 。

 **编译 goldfish 内核不仅仅需要内核代码，还需要 AOSP 源码提供的配置文件和交叉编译工具。**

### 0x21 前期准备

 **1\. 内核（Goldfish）**

下载 goldfish 内核

<https://android.googlesource.com/kernel/goldfish.git/+/refs/heads/android-goldfish-4.14-dev>

    
    
    git clone https://android.googlesource.com/kernel/goldfish -b android-goldfish-4.14-dev
    

对应的官方编译文档

> [AOSP 内核编译官方文档](https://source.android.google.cn/source/building-> kernels?hl=zh-cn)
>
>
> [https://android.googlesource.com/platform/external/qemu/+/refs/heads/master/docs/ANDROID-> KERNEL.TXT﻿](https://android.googlesource.com/platform/external/qemu/+/refs/heads/master/docs/ANDROID-> KERNEL.TXT)

 **2\. Android 源码树（AOSP，可选）**

如果想编译 x86 架构的内核，需要从 AOSP 源码中拉取以下配置文件和交叉编译工具（Android SDK
也提供了相应的交叉编译工具）。我们有两种方式进行编译：使用 AOSP 提供的编译配置脚本，达到一键编译的效果；使用传统的 make 编译方式。

使用编译脚本直接编译，好处显而易见，比较简单，不用手动配置环境，但是缺点也显而易见，想进行内核配置的时候，就需要手动修改 arch 目录下相应的配置文件。

 **3\. Android NDK（可选）**

使用 NDK 提供的交叉编译工具，就无需使用 AOSP 提供的交叉编译工具了。我们可以从 [Android
NDK](https://developer.android.com/ndk/downloads/?hl=zh-cn)中找到对应的编译器。编译环境是
Linux，所以要下载 [android-ndk-r21e-linux-x86_64.zip](https://dl.google.com/android/repository/android-ndk-r22b-linux-x86_64.zip?hl=zh-cn)，放到相应目录下。

### 0x22 编译内核

 **1\. 编译脚本编译内核**

 _编译脚本_

将 Android 源码树 [xref](http://androidxref.com/)（OpenGrok）
/[prebuilts](http://androidxref.com/9.0.0_r3/xref/prebuilts/)/[qemu-kernel](http://androidxref.com/9.0.0_r3/xref/prebuilts/qemu-kernel/)/ 目录下的
[kernel-toolchain](http://androidxref.com/9.0.0_r3/xref/prebuilts/qemu-kernel/kernel-toolchain/)/ 以及 [build-kernel.sh](http://androidxref.com/9.0.0_r3/xref/prebuilts/qemu-kernel/build-kernel.sh)文件（ **编译配置脚本** ）拷贝到内核源码根目录

>  **Tips** : OpenGrok 最大的问题是只能看代码，而不能下载。在 Google Git 可以使用 git 下载 Android
> 源码树中的单个文件，当然网站也提供了压缩包，例如，我们要下载 [pie-> qpr3-release](https://android.googlesource.com/platform/prebuilts/qemu-> kernel/+/refs/heads/pie-qpr3-release)，选择 tgz 即可

赋予可执行权限

    
    
    chmod -R +x ./kernel-toolchain
    

_交叉编译工具_

将 Android 源码树 xref
/[prebuilts](http://androidxref.com/9.0.0_r3/xref/prebuilts/)/[gcc](http://androidxref.com/9.0.0_r3/xref/prebuilts/gcc/)/[linux-x86](http://androidxref.com/9.0.0_r3/xref/prebuilts/gcc/linux-x86/)/[x86](http://androidxref.com/9.0.0_r3/xref/prebuilts/gcc/linux-x86/x86/)/[x86_64-linux-android-4.9](http://androidxref.com/9.0.0_r3/xref/prebuilts/gcc/linux-x86/x86/x86_64-linux-android-4.9/)/ 文件（x86-64 **交叉编译工具** ）连同路径复制到内核源码根目录

>  **Tips** : Android 9.0 代号 pie，对应 git 目录为 [pie-> qpr3-release](https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/x86/x86_64-linux-> android-4.9/+/refs/heads/pie-qpr3-release)，选择 tgz 即可，特别注意：交叉编译工具的架构不要选错了！

创建编译目录，例如 build，并将 AOSP 提供的交叉编译工具复制到相应目录

    
    
    mkdir build
    cd build
    mkdir -p prebuilts/gcc/linux-x86/x86/x86_64-linux-android-4.9
    

根据`build-kernel.sh`，需要设置编译路径

    
    
    export ANDROID_BUILD_TOP=`pwd`
    

_编译_

    
    
    ./build-kernel.sh --arch=x86_64  --config=x86_64_ranchu
    

**2\. 手动编译**

 _配置交叉编译器_

交叉编译工具的下载方法，上面已有说明。将交叉编译器路径添加到系统环境变量 PATH 中

    
    
    export PATH=/goldfish/build/prebuilts/gcc/linux-x86/x86/x86_64-linux-android-4.9/bin:$PATH
    

配置交叉编译器

    
    
    export ARCH=x86_64
    export CROSS_COMPILE=x86_64-linux-android-    

_配置内核并编译_

    
    
    # 在源码根目录下生成了.config文件
    make x86_64_ranchu_defconfig
    make -j$(nproc)
    

编译好内核之后，会在相应的目录下生成 bzImage 压缩的内核映像文件，用其替代 Android 模拟器的内核即可。如果是真机，那就需要使用
fastboot 将内核刷入手机中。

### 0x23 **使用 KASAN + KCOV 构建 Goldfish 内核**

AOSP 官网 [使用 KASAN+KCOV 构建 Pixel
内核](https://source.android.com/devices/tech/debug/kasan-kcov?hl=zh-cn)已经有详细说明。

> Kernel Address Sanitizer
> ([KASAN](https://www.kernel.org/doc/html/latest/dev-tools/kasan.html))
> 可以帮助内核开发者和测试人员找出与运行时内存相关的错误，例如出界读取或写入操作问题，以及“释放后使用”相关问题。虽然 KASAN
> 因其运行时性能低以及导致内存使用量增加而未在正式 build 中启用，但它仍然是用来测试调试 build 的重要工具。
>
> 在与另一个名为 Kernel Coverage ([KCOV](https://lwn.net/Articles/671640/))
> 的运行时工具搭配使用时，经过 KASAN 排错和 KCOV
> 插桩的代码可以帮助开发者与测试人员检测运行时内存错误以及获取代码覆盖率信息。在内核模糊测试（例如通过
> [syzkaller](https://github.com/google/syzkaller)）的情景中，KASAN 可以协助确定崩溃的根本原因，而
> KCOV 则会向模糊引擎提供代码覆盖率信息，以在测试用例或语料库重复数据删除方面提供帮助。

利用我们在前述章节中介绍的手动编译内核的方法，修改`.config`文件，添加以下编译选项

    
    
    CONFIG_KASAN=y
    CONFIG_KASAN_INLINE=y
    CONFIG_KCOV=y
    

编译

    
    
    # 终端会提示一些关于 KASAN 和 KCOV 细粒度设置，默认就好，也可自行配置
    make -j$(nproc)
    # 或者重新生成配置文件再编译
    make olddefconfig & make -j$(nproc)
    

## 0x30 Syzkaller

Syzkaller 是一款针对内核驱动进行白盒 Fuzz 的工具。

### 0x31 基础环境

Syzkaller 主要使用 go 语言编写，因此我们需要安装 go 语言环境

 **Go**

1.安装 [go](https://golang.org/dl/)语言环境

下载相应的 go 语言版本，由于我们的编译环境是 Linux，这里选择 [go1.16.6.linux-amd64.tar.gz](https://golang.org/dl/go1.16.6.linux-amd64.tar.gz)，解压到任意目录

2.交叉编译器

由于这里我们需要编译生成的二进制是放在 Android 模拟器上的（x86架构），因此使用普通的 gcc 即可。若是在真机上（aarch64，即
ARMv8），则需要使用交叉编译器，可参考 [交叉编译工具 aarch64-linux-gnu-gcc
的介绍与安装](https://blog.csdn.net/song_lee/article/details/105487177)，亦或者直接运行

    
    
    apt-get install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu
    

3.设置全局环境

    
    
    export GOROOT=/mygo/go					# go 根目录
    export GOPATH=/mygo						# go 上层目录
    export PATH=$GOROOT/bin:$PATH
    export PATH=..							# 交叉编译器路径
    

当然，你也可以不用管上述复杂的操作，直接使用以下方法，一键配置 Go 语言的环境

 **一键配置 Go**

    
    
    wget https://golang.org/dl/go1.16.6.linux-amd64.tar.gz
    tar -xf go1.16.6.linux-amd64.tar.gz
    mv go goroot
    mkdir gopath
    export GOPATH=`pwd`/gopath
    export GOROOT=`pwd`/goroot
    export PATH=$GOPATH/bin:$PATH
    export PATH=$GOROOT/bin:$PATH
    

**Syzkaller**

获取源码

    
    
    git clone https://github.com/google/syzkaller.git
    

将源码拷贝至 go 语言目录的 src 文件下，并且需要根据 Syzkaller 源码，对路径进行修改

比如，查看`syz-fuzzer/fuzzer.go`导入的包如下所示

    
    
    import (
    	"flag"
    	"fmt"
    	"math/rand"
    	"os"
    	"runtime"
    	"runtime/debug"
    	"sort"
    	"sync"
    	"sync/atomic"
    	"time"
    
    	"github.com/google/syzkaller/pkg/csource"
    	"github.com/google/syzkaller/pkg/hash"
    	"github.com/google/syzkaller/pkg/host"
    	"github.com/google/syzkaller/pkg/ipc"
    	"github.com/google/syzkaller/pkg/ipc/ipcconfig"
    	"github.com/google/syzkaller/pkg/log"
    	"github.com/google/syzkaller/pkg/osutil"
    	"github.com/google/syzkaller/pkg/rpctype"
    	"github.com/google/syzkaller/pkg/signal"
    	"github.com/google/syzkaller/pkg/tool"
    	"github.com/google/syzkaller/prog"
    	_ "github.com/google/syzkaller/sys"
    	"github.com/google/syzkaller/sys/targets"
    )
    

所以这里我们要在`go/src`下创建相应的目录，将 Syzkaller 的源码拷贝进去

    
    
    mkdir -p github.com/google
    mv syzkaller github.com/google/
    

抛开 1、2 两步，我们也可以直接使用以下步骤

 **一键配置 syzkaller**

以下方法亲测已失效（https://github.com/google/syzkaller/issues/2686）

    
    
    cd goroot/src
    mkdir -p github.com/google
    cd github.com/google
    git clone https://github.com/google/syzkaller.git
    make TARGETOS=linux TARGETARCH=arm64
    

或者（亲测OK）

    
    
    cd gopath
    mkdir -p src/github.com/google
    cd src/github.com/google
    git clone https://github.com/google/syzkaller.git
    make TARGETOS=linux TARGETARCH=arm64
    

或者（该方法容易出现证书问题）

    
    
    go get -u -d github.com/google/syzkaller/prog
    cd gopath/src/github.com/google/syzkaller/
    make
    

编译完成之后，我们会在 bin 目录中生成以下文件

    
    
    linux_amd64  syz-db  syz-manager  syz-mutate  syz-prog2c  syz-repro  syz-runtest  syz-sysgen  syz-upgrade
    

![image](https://image.3001.net/images/20210820/1629451219_611f73d3e5c9423b6e301.png!small)

### 0x32 Fuzzing 流程

 **1\. 创建工作目录**

    
    
    mkdir myworkspace
    

**2\. 编写配置文件**

syzkaller`syz-manager`进程的操作由配置文件管理，在调用时通过`-config`选项传递。因此需要创建配置文件，针对不同平台（如
Linux、Andriod、QEMU 虚拟机），所需要的参数也是不一样的，详细语法可参考
[configuration.md](https://github.com/google/syzkaller/blob/master/docs/configuration.md)

针对手机

    
    
    {
    	"target": "linux/amd64",			// 目标平台
    	"workdir": "/syzkaller/workdir",	// 工作目录
    	"http": "127.0.0.1:80",				// 查看 syz-manager 运行状态信息的 Web 地址
    	"syzkaller": "/home/lys/Documents/syz_workspace/gopath/src/github.com/google/syzkaller",
        "workdir_template": "/home/lys/Documents/syzkaller/syzkaller/myvmlinux/",
    	"procs": 4,
    	"type": "adb",
    	"vm": {
    		"devices":["10.0.2.2:5555"]		// x86 架构的 Android 模拟器
    	}
    }
    

一些有用的可选配置项：限制系统调用

    
    
    "enable_syscalls": [
        "open$proc",
        "read$proc",
        "write$proc",
        "close$proc"
    ],
    

**使用 syz-manager 开始 fuzzing**

    
    
    ./bin/syz-manager -config ./workdir/myconfig.cfg
    

出现以下页面，说明 Syzkaller 的环境已经没有问题了！  
![image](https://image.3001.net/images/20210820/1629451179_611f73ab651d784a939aa.png!small)

## 0x40 根据驱动编写 fuzzing 配置文件

### 0x41 Linux 驱动编程模型

在内核中，各种驱动形式不过是表象，本质还是把 fops 注册到
inode，如下所示（linux/v3.18.140/source/drivers/staging/android/ion/ion.c）

    
    
    struct ion_device *ion_device_create(long (*custom_ioctl)
    				     (struct ion_client *client,
    				      unsigned int cmd,
    				      unsigned long arg))
    {
    	struct ion_device *idev;
    	int ret;
    
    	idev = kzalloc(sizeof(struct ion_device), GFP_KERNEL);
    	if (!idev)
    		return ERR_PTR(-ENOMEM);
    
    	idev->dev.minor = MISC_DYNAMIC_MINOR;
    	idev->dev.name = "ion";
    	idev->dev.fops = &ion_fops;
    

这是一个典型的驱动注册或者说是初始化的地方，而`ion_fops`变量就是我们关注的重点

    
    
    static const struct file_operations ion_fops = {
    	.owner          = THIS_MODULE,
    	.open           = ion_open,
    	.release        = ion_release,
    	.unlocked_ioctl = ion_ioctl,
    	.compat_ioctl   = compat_ion_ioctl,
    };
    

这里就是一个用户态函数到内核态函数的映射表，专业表达就是： **每个驱动程序都有一个 file-operation
的数据结构，包含指向驱动程序内部函数的指针**
，当我们用户态的程序打开这个驱动节点时，对文件的操作，其实就会引用相应的内核函数。例如，`open("/dev/ion")`，其实就会调用`ion_open`。

### 0x42 syz-extract 和 syz-sysgen

Syzkaller 默认不会编译 syz-extract 和 syz-sysgen，需要单独编译

  * make bin/syz-extract

  * make bin/syz-sysgen # 新版 syzkaller 默认会编译生成 syz-sysgen

这两个二进制的作用是什么？

    
    
    xxx.txt +------> xxx.const  +----> xxx.go
    
           syz-extract          syz-sysgen
    

针对某个驱动接口编写的配置文件 xxx.txt，syz-extract 二进制根据 **配置文件** 和 **内核源码** 生成 const 文件，syz-sysgen 会根据 **txt 配置文件** 和 **const** 生成一个 .go（因为 Syzkaller 是用 go 语言进行编写的）

### 0x43 根据驱动接口编写 txt 配置文件

☆ ！需要在 Linux 环境下直接编写 txt，因为 Windows 编写的 txt 与 unix 不兼容，需要使用 notepad++ 转换
(notepad++ 右下角转换为 Unix LF)。

[系统调用配置语法](https://github.com/google/syzkaller/blob/master/docs/syscall_descriptions_syntax.md)给出了详细说明

典型样例：

  * <https://github.com/google/syzkaller/blob/master/sys/android/dev_ion.txt>

  * <https://github.com/google/syzkaller/blob/master/sys/linux/dev_trusty.txt>

系统调用描述，即我们需要编写的配置文件，需要包含以下几部分

  * 内核头文件

  * 资源

  * 系统调用描述

  * 函数

  * 结构体定义

 **头文件**

顾名思义，系统调用描述会有一些定义，需要用到内核的头文件

 **资源**

资源表示从一个系统调用的输出，传递到另外一个系统调用的输入。可以理解为一个别名，例如

    
    
    resource fd_ion[fd]
    resource fd_ion_generic[fd]
    
    resource ion_handle[int32]
    
    ion_fd_data {
    	handle	ion_handle		# int32
    	fd	fd_ion_generic		# fd
    }
    

**系统调用描述**

在`syzkaller/sys/linux/`下新建`proc_operation.txt`

我们一般关注的系统调用主要有 **open、read、write、ioctl、mmap、lseek**

系统调用描述

    
    
    open$proc(file ptr[in, string["/proc/test"]], flags flags[proc_open_flags], mode flags[proc_open_mode]) fd
    read$proc(fd fd, buf buffer[out], count len[buf])
    write$proc(fd fd, buf buffer[in], count len[buf])
    ioctl$SWITCH分支(fd fd, cmd const[SWITCH分支], arg ptr[in/out/inout, 结构体类型])
    

规则：$ 符号前面的是系统调用名，后面是特定类型（type）的系统调用。in 表示输入（copy_from_user ），out
表示输出（copy_to_user ）。不确定输入还是输出，可以使用 inout，官方描述如下

    
    
    syscallname "(" [arg ["," arg]*] ")" [type] ["(" attribute*")"]
    arg = argname type
    argname = identifier
    type = typename [ "[" type-options "]" ]
    typename = "const" | "intN" | "intptr" | "flags" | "array" | "ptr" |
    "string" | "strconst" | "filename" | "glob" | "len" |
    "bytesize" | "bytesizeN" | "bitsize" | "vma" | "proc"
    type-options = [type-opt ["," type-opt]]
    

结构体：把涉及到的所有结构体定义转成 go 语言的形式写下来。syzkaller 源码给出了很多 linux 驱动 fuzzing
案例，最好的方法是将这些定制好的 txt 配置文件，结合 linux 源码中驱动的接口定义，弄清楚定义。

### 0x44 测试

生成 .const

    
    
    bin/syz-extract -os linux -arch amd64 -sourcedir 内核目录 -builddir(可选项) 编译目录/KERNEL_OBJ xxx.txt
    

生成 .go

    
    
    make generate
    

重新编译生成 syzkaller

    
    
    make TARGETOS=linux TARGETARCH=amd64
    

开始测试

    
    
    ./bin/syz-manager -config ./workdir/myconfig.cfg
    

## 0x50 后 fuzzing 阶段

### 0x51 复现 crash

在 fuzzing 过程中，程序被并行执行（取决于配置文件中的选项程序），因此导致崩溃的程序不一定立即在它之前执行。使用以下方法：

  1. 在 qemu 或者其他虚拟机中跑内核。

  2. 将`syz-execprog`和`syz-executor`复制到目标系统上。

  3. 使用`syz-execprog`程序在VM上运行崩溃日志。逐渐从日志中删除不相关的程序，直到只剩下一个程序。可以删除程序中的无关的 syscall，使其更小。

    
    
    ./syz-execprog -executor=./syz-executor -repeat=1 -sandbox=setuid -enable=none -collide=false ./log0
    

找到崩溃的系统调用之后，再使用`syz-prog2c`将引发崩溃的 syzkaller 程序转化为 C 程序

    
    
    syz-prog2c -prog crash.syz -repeat=1 -enable=none > crash.c
    

### 0x52 分析报告

代码覆盖率的统计依赖于内核源码以及 KCOV 编译选项，因此要统计此项，必须要使得`syz-manager`运行在带有整个编译环境的 Linux 主机上。

lost connection to test machine: 这是由于`sys-manager`和`sys-fuzzer`无法通行造成的，常见的原因如下

  * 目标系统重启

  * syz-fuzzer 进程异常

几个跟踪源码与对应的汇编代码行号的工具

  * addr2line

    
    
    addr2line -e vmlinux 0x46a149 -f -C -s
    

  * gdb （调试 vmlinux，可以通过命令找到 syzkaller log 中相应符号对应的源码位置）

    
    
    gef➤  list *(goldfish_dma_mmap + 0xa7)
    0xffffffff80e25447 is in goldfish_dma_mmap (drivers/platform/goldfish/goldfish_pipe_v2.c:950).
    945     in drivers/platform/goldfish/goldfish_pipe_v2.c
    

## 总结

Syzkaller 是谷歌 2015 年前后开源的一个 fuzzing 内核系统调用工具，推出之初，好评如潮，也发现了很多 Linux
内核的安全漏洞。不过近几年来，热度有所下降。使用 Syzkaller
的难点有三：第一，需要对待测驱动，进行定制，一些复杂的驱动往往包含复杂的结构体嵌套，对于其中用到的每一个结构体，都需要写入配置文件中。第二，需要内核源码的支持，也就是说，我们并不能以黑盒的方式测试其他
Android 厂商的手机，而只能在有内核源码的情况下，编译带有 KCON+KASAN
编译选项的内核镜像。第三，在测试过程中，有一定的误报率，待测设备（Android 手机）往往跟我们的监控设备（Linux
主机）无故断开连接，也会出现死机等现象，在一定程度上增加了测试周期。

当然，Syzkaller
优点还是很明显的，会根据代码覆盖率变异系统调用的输入，增加代码覆盖率。驱动包含的复杂结构体，用白盒审计的方式往往难以发现深层次问题，通过 fuzzing
可以很容易找到一些隐藏深处的代码安全漏洞。

安全顶会上一些关于 Syzkaller 的研究和改进

  * [MoonShine: Optimizing OS Fuzzer Seed Selection with Trace Distillation, 2018](https://www.usenix.org/conference/usenixsecurity18/presentation/pailoor)：哥伦比亚大学团队开发的 MoonShine，这是一种新颖的策略，可从真实程序的系统调用中提取 fuzz 种子。作为对 Syzkaller 的扩展， MoonShin 能够将 Syzkaller 的 Linux 内核代码覆盖率平均提高 13％。

  * [Razzer: Finding Kernel Race Bugs through Fuzzing, 2019](https://www.computer.org/csdl/proceedings-article/sp/2019/666000a296/19skfwZLirm)：韩国科学技术院 (KAIST) DR Jeong 设计并提出了针对内核中的数据竞争类型漏洞的模糊测试（fuzzing）工具 Razzer 。 Razzer 的两阶段模糊测试基于Syzkaller。确定性调度程序是使用 QEMU / KVM 实现的。

  * [HFL: Hybrid Fuzzing on the Linux Kernel (2020)](https://www.unexploitable.systems/publication/kimhfl/)：美国俄勒冈州立大学提出的一个新兴混合 fuzz 工具。据作者所属，HFL 代码覆盖率分别比 Moonshine 和 Syzkaller 高出15%和26%，并发现 20+ 个内核漏洞。该工具好像没有开源。

有关 **Fuzzing** 更多的研究和洞察：<https://github.com/liyansong2018/fuzzing-tutorial>

