**近期，我们发现了一种新型的勒索软件家族-Anatova。Anatova发现于一个私人的点对点（p2p）网络中，目前我们已经确保客户得到了有效的安全保护，并打算在这篇文章中公开我们的研究成果。**

![1.png](https://image.3001.net/images/20190403/1554251193_5ca3fdb9346f1.png!small)

考虑到Anatova是以模块化扩展的形式开发的，因此我们认为它将会发展成为非常严重的安全威胁。

除此之外，它还会检查目标设备是否连接了网络共享，并加密所有的共享文件。根据我们的分析，Anatova背后的开发者技术水平非常高，因为我们捕捉到的每一个样本都拥有唯一的密钥和不同的功能，这在勒索软件领域中很少见。

在这篇文章中，我们将讨论Anatova的技术细节，以及关于这个新型勒索软件家族其他的一些有意思的东西。

分析样本hash：

    
    
    170fb7438316f7335f34fa1a431afc1676a786f1ad9dee63d78c3f5efd3a0ac0

Anatova的主要目的是加密目标设备上的所有文件，并向目标用户勒索数据赎金。

## Anatova概述

Anatova一般会使用游戏或者常见应用的图标来欺骗用户下载恶意软件，然后请求获取管理员权限：

![2.png](https://image.3001.net/images/20190403/1554251214_5ca3fdce054b9.png!small)

Anatova勒索软件是一款64位应用程序，编译日期为2019年1月1日。我们的样本文件大小为307kb，但具体会根据样本使用的资源发生变化。如果我们移除所有资源，Anatova的大小仅为32kb。对于一款拥有如此强大机制的勒索软件来说，这个体积确实非常小。

Anatova还拥有强大的保护机制来对抗静态分析：

1、 大多数字符串都使用了Unicode或ASCII进行加密，使用了不同的解密密钥，数据全部嵌入在可执行文件中。

2、 90%都是动态调用，只使用了常见Windows
API的标准库（C语言）：GetModuleHandleW、LoadLibraryW、GetProcAddress、ExitProcess和MessageBoxA。

3、 当我们在IDA Pro中查看代码并对功能函数进行分析时，IDA Pro一直报错，我们不确定这是IDA Pro的Bug还是恶意软件开发者有意而为之的。

![3.png](https://image.3001.net/images/20190403/1554251222_5ca3fdd6beea2.png!small)

### V1.0亮点

因为这是一款新型的勒索软件，所以我们暂且将其归为v1.0版本。

恶意软件首先会获取“kernel32.dll”来作为模块处理库，并使用函数“GetProcAddress”来从处理库中获取29个功能函数。

![3-1.png](https://image.3001.net/images/20190403/1554251553_5ca3ff210a084.png!small)

如果恶意软件无法获取kernel32模块处理库，而且也无法获取其他的功能函数，它将会退出执行。

接下来，恶意软件会尝试使用硬编码名称（6a8c9937zFIwHPZ309UZMZYVnwScPB2pR2MEx5SY7B1xgbruoO）来创建原语，但不同样本中的原语名称也不同。创建完成并获取到处理库后，它会调用“GetLastError”函数，并判断最后一条错误信息是否为ERROR_ALREADY_EXISTS或ERROR_ACCESS_DENIED。这两条错误信息指的是“之前的原语对象实例已存在”。如果出现这样的情况，恶意软件会清空内存，我们之后会详细介绍这部分。

![4.png](https://image.3001.net/images/20190403/1554251522_5ca3ff02e2209.png!small)

通过这项检测后，Anatoa会使用相同的机制从“advapi32.dll”、“Crypt32.dll”和“Shell32.dll”库中获取某些功能函数。所有的文本都经过了加密处理，并且挨个进行解密，然后获取函数，释放内存，然后处理下一个请求。

如果无法获取到必要模块或函数，它将会运行清理工具并退出运行。

有意思的是，Anatoa还会获取已登陆/活动用户的用户名并搜索比对一个加密用户名列表：

    
    
    LaVirulera
    
    tester
    
    Tester
    
    analyst
    
    Analyst
    
    lab
    
    Lab
    
    Malware
    
    Malware

很明显这是一种躲避虚拟机和沙盒的方法。

接下来，Anatova还会检测目标系统的语言，即系统使用的区域语言选项，这样是为了确保用户无法通过屏蔽某种语言来绕过文件加密。

下面的国家不会受到Anatova的影响：

    
    
    所有独联体国家
    
    叙利亚
    
    埃及
    
    摩洛哥
    
    伊拉克
    
    印度

独联体国家被排除在攻击名单外的情况很常见，这也表明攻击者很有可能来自于其中的一个国家。但是，有多个国家被排除在外就有些奇怪了。

![5.png](https://image.3001.net/images/20190403/1554251508_5ca3fef4ae20e.png!small)

语言检测完成后，Anatova会寻找一个标记（该标记在所有样本中的值都为0），如果这个标记值变成了1，它将会加载两个DLL文件：“extra1.dll”和“extra2.dll”。这也表明，Anatova是以模块化的形式开发的，并且将来会实现更多的功能扩展。

![6.png](https://image.3001.net/images/20190403/1554251496_5ca3fee8dd8cd.png!small)

接下来，Anatova会使用加密API来生成RSA密钥对。它会使用加密API“CryptGenRandom”（Salsa20算法）来创建一个32位的随机密钥以及一个8字节值。文件加密过程中，它还会解码样本中的主RSA公钥：

![7.png](https://image.3001.net/images/20190403/1554251486_5ca3fedea3903.png!small)

用于实现文件加密功能的部分代码如下：

![8.png](https://image.3001.net/images/20190403/1554251472_5ca3fed01d2cd.png!small)

下面给出的是Anatova显示给目标用户的勒索信息：

![9.png](https://image.3001.net/images/20190403/1554251460_5ca3fec454bf3.png!small)

文件加密完成后，Anatova还会删除目标设备上的卷硬拷贝，跟其他勒索软件一样，这里Anatova同样会使用vssadmin程序：

![10.png](https://image.3001.net/images/20190403/1554251442_5ca3feb239778.png!small)

所有的操作步骤都完成后，勒索软件会进入代码清洁流程，也就是清除内存中的代码以防止用户创建解密工具。

### 入侵威胁指标IoC

样本使用了下列攻击技术：

> 1、 通过API执行；
>
> 2、 应用进程发现；
>
> 3、 文件和目录发现：搜索文件进行加密；
>
> 4、 加密文件；
>
> 5、 进程发现：枚举终端设备上的所有进程，并终止特定进程；
>
> 6、 创建文件；
>
> 7、 权限提升；

### 哈希：

    
    
    2a0da563f5b88c4d630aefbcd212a35e
    
    366770ebfd096b69e5017a3e33577a94
    
    9d844d5480eec1715b18e3f6472618aa
    
    61139db0bbe4937cd1afc0b818049891
    
    596ebe227dcd03863e0a740b6c605924

 *** 参考来源：[securingtomorrow](https://securingtomorrow.mcafee.com/other-blogs/mcafee-labs/happy-new-year-2019-anatova-is-here/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

