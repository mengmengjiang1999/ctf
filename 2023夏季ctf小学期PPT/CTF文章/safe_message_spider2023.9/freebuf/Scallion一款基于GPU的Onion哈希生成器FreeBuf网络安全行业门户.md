![](https://image.3001.net/images/20200203/1580663910_5e3704660be5f.gif!small)

##  Scallion

**Scallion可以帮助我们使用OpenCL来创建GPG密钥以及针对Tor隐藏服务的.onion地址。Scallion基于Mono软件平台开发和运行，并已在Arch
Linux平台上成功测试，工具的运行依赖.NET 3.5+（已在Windows 7和Windows Server 2008平台上测试）。**

Scallion当前仍处于测试阶段，正在积极开发中，但是它目前已经可以正常使用了。我们的开发当前主要集中在性能、用户界面和安装难度方面的改进上，而不是在生成密钥以及相关算法方面。

##  工具依赖

> 1、安装并配置好OpenCL以及相关驱动器。
>
> 2、OpenSSL，在Windows环境下，已包含有预内置的x64 DLL。
>
> 3、尽在Windows平台下，需要V[C++ Redistributable 2008](https://www.microsoft.com/en-> us/download/details.aspx?id=5582)。

###  工具下载

>
> 最新版本源码压缩包：【[点我下载](https://raw.githubusercontent.com/lachesis/scallion/binaries/scallion-v2.0.zip)】

##  Linux环境下构建

###  依赖组件

> 针对自己的Linux发行版，获取最新版本的Mono：【[传送门](http://www.mono-project.com/download/)】

使用下列命令安装常用依赖组件：

> sudo apt-get update
>
> sudo apt-get install libssl-dev mono-devel

AMD/OpenSource构建命令：

    
    
    sudo apt-get install ocl-icd-opencl-dev

Nvidia构建命令：

    
    
    sudo apt-get install nvidia-opencl-dev nvidia-opencl-icd

最后，运行下列命令：

    
    
    msbuild scallion.sln

##  Docker Linux配置（Nvidia GPU）

1、获取nvidia-docker容器运行时环境：【[点我获取](https://github.com/NVIDIA/nvidia-docker)】。

2、运行下列命令构建容器：

    
    
    docker build -t scallion -f Dockerfile.nvidia

3、运行下列命令：

    
    
    docker run --runtime=nvidia -ti --rm scallion -l

##  Windows环境下构建

> 1、在VS中打开“scallion.sln”
>
> 2、构建解决方案

##  工具使用

###  枚举设备：

    
    
    $ mono scallion/bin/Debug/scallion.exe -l

###  生成哈希：

    
    
    $ mono scallion/bin/Debug/scallion.exe -d 0 prefix
    
     Cooking up some delicious scallions...
    
     Using kernel optimized from file kernel.cl (Optimized4)
    
     Using work group size 128
    
     Compiling kernel... done.
    
     Testing SHA1 hash...
    
     CPU SHA-1: d3486ae9136e7856bc42212385ea797094475802
    
     GPU SHA-1: d3486ae9136e7856bc42212385ea797094475802
    
     Looks good!
    
     LoopIteration:40  HashCount:671.09MH  Speed:9.5MH/s  Runtime:00:01:10  Predicted:00:00:56  Found new key! Found 1 unique keys.
    
     <XmlMatchOutput>
    
       <GeneratedDate>2014-08-05T07:14:50.329955Z</GeneratedDate>
    
       <Hash>prefix64kxpwmzdz.onion</Hash>
    
       <PrivateKey>-----BEGIN RSA PRIVATE KEY-----    
     MIICXAIBAAKBgQCmYmTnwGOCpsPOqvs5mZQbIM1TTqOHK1r6zGvpk61ZaT7z2BCE
    
     FPvdTdkZ4tQ3/95ufjhPx7EVDjeJ/JUbT0QAW/YflzUfFJuBli0J2eUJzhhiHpC/
    
     1d3rb6Uhnwvv3xSnfG8m7LeI/Ao3FLtyZFgGZPwsw3BZYyJn3sD1mJIJrQIEB/ZP
    
     ZwKBgCTUQTR4zcz65zSOfo95l3YetVhfmApYcQQd8HTxgTqEsjr00XzW799ioIWt
    
     vaKMCtJlkWLz4N1EqflOH3WnXsEkNA5AVFe1FTirijuaH7e46fuaPJWhaSq1qERT
    
     eQT1jY2jytnsJT0VR7e2F83FKINjLeccnkkiVknsjrOPrzkXAkEA0Ky+vQdEj64e
    
     iP4Rxc1NreB7oKor40+w7XSA0hyLA3JQjaHcseg/bqYxPZ5J4JkCNmjavGdM1v6E
    
     OsVVaMWQ7QJBAMweWSWtLp6rVOvTcjZg+l5+D2NH+KbhHbNLBcSDIvHNmD9RzGM1
    
     Xvt+rR0FA0wUDelcdJt0R29v2t19k2IBA8ECQFMDRoOQ+GBSoDUs7PUWdcXtM7Nt
    
     QW350QEJ1hBJkG2SqyNJuepH4PIktjfytgcwQi9w7iFafyxcAAEYgj4HZw8CQAUI
    
     3xXEA2yZf9/wYax6/Gm67cpKc3sgKVczFxsHhzEml6hi5u0FG7aNs7jQTRMW0aVF
    
     P8Ecx3l7iZ6TeakqGhcCQGdhCaEb7bybAmwQ520omqfHWSte2Wyh+sWZXNy49EBg
    
     d1mBig/w54sOBCUHjfkO9gyiANP/uBbR6k/bnmF4dMc=
    
     -----END RSA PRIVATE KEY-----    
     </PrivateKey>
    
       <PublicModulusBytes>pmJk58BjgqbDzqr7OZmUGyDNU06jhyta+sxr6ZOtWWk+89gQhBT73U3ZGeLUN//ebn44T8exFQ43ifyVG09EAFv2H5c1HxSbgZYtCdnlCc4YYh6Qv9Xd62+lIZ8L798Up3xvJuy3iPwKNxS7cmRYBmT8LMNwWWMiZ97A9ZiSCa0=</PublicModulusBytes>
    
       <PublicExponentBytes>B/ZPZw==</PublicExponentBytes>
    
     </XmlMatchOutput>
    
     init: 491ms / 1 (491ms, 2.04/s)
    
     generate key: 1193ms / 6 (198.83ms, 5.03/s)
    
     cpu precompute: 10ms / 6 (1.67ms, 600/s)
    
     total without init: 70640ms / 1 (70640ms, 0.01/s)
    
     set buffers: 0ms / 40 (0ms, 0/s)
    
     write buffers: 3ms / 40 (0.08ms, 13333.33/s)
    
     read results: 67442ms / 40 (1686.05ms, 0.59/s)
    
     check results: 185ms / 40 (4.63ms, 216.22/s)
    
     9.50 million hashes per second
    
     Stopping the GPU and shutting down...

##  多模式哈希

Scallion支持通过原语正则表达式语句来搜索单一或多模式哈希，目前仅支持字符类型（例如[absd]）。“.”字符代表任意字符，Onion地址长度固定为16个字符，GPG指纹为40个字符。你可以通过“$”来寻找前缀或后缀匹配，例如DEAD$。除此之外，你还可以使用pipe语句(例如pattern1|pattern2)来寻找多模式哈希，当然了，这种搜索模式下运行速度肯定不乐观。

##  查询样例

    
    
    mono scallion.exe prefix[234567]
    
     mono scallion.exe -c prefix scallion hashes
    
     mono scallion.exe -c "prefix|scallion|hashes"
    
     mono scallion.exe .........badbeef
    
     mono scallion.exe --gpg badbeef$ # 生成GPG密钥
    
     mono scallion.exe "suffixa$|suffixb$|prefixa|prefixb|a.suffix$|a.test.$"

##  Scallion工作机制

> 1、使用OpenSSL以及CPU生成RSA密钥
>
> 2、向GPU发送密钥
>
> 3、增加密钥的公共指数
>
> 4、对密钥进行哈希计算
>
> 5、如果生成的哈希非部分冲突，则返回第三步
>
> 6、如果生成的密钥未通过PKCS #1 v2.1的及健全性检查，则返回第三步
>
> 7、生成全新的密钥

##  速度/性能

初始的RSA密钥生成是在CPU上完成的，SHA1哈希计算则是在GPU上完成的。下面给出的是常见GPU的计算速度表：

**GPU** **型号** |  **速度**  
---|---  
Intel i7-2620M  |  9.9 MH/s  
Intel i5-5200U  |  118 MH/s  
NVIDIA GT 520  |  38.7 MH/s  
NVIDIA Quadro K2000M  |  90 MH/s  
NVIDIA GTS 250  |  128 MH/s  
NVIDIA GTS 450  |  144 MH/s  
NVIDIA GTX 670  |  480 MH/s  
NVIDIA GTX 970  |  2350 MH/s  
NVIDIA GTX 980  |  3260 MH/s  
NVIDIA GTX 1050 (M)  |  1400 MH/s  
NVIDIA GTX 1070  |  4140 MH/s  
NVIDIA GTX 1070 TI  |  5100 MH/s  
NVIDIA GTX TITAN X  |  4412 MH/s  
NVIDIA GTX 1080  |  5760 MH/s  
NVIDIA Tesla V100  |  11646 MH/s  
AMD A8-7600 APU  |  120 MH/s  
AMD Radeon HD5770  |  520 MH/s  
AMD Radeon HD6850  |  600 MH/s  
AMD Radeon RX 460  |  840 MH/s  
AMD Radeon RX 470  |  957 MH/s  
AMD Radeon R9 380X  |  2058 MH/s  
AMD FirePro W9100  |  2566 MH/s  
AMD Radeon RX 480  |  2700 MH/s  
AMD Radeon RX 580  |  3180 MH/s  
AMD Radeon R9 Nano  |  3325 MH/s  
AMD Vega Frontier Edition  |  7119 MH/s  
  
###  MH/s = 百万哈希/秒

##  工具运行截图

![](https://image.3001.net/images/20200203/1580664019_5e3704d388290.png!small)

##  项目地址

> Scallion：【[GitHub传送门](https://github.com/lachesis/scallion)】

 ***
参考来源：[lachesis](https://github.com/lachesis/scallion)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

