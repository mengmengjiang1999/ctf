![](https://image.3001.net/images/20230605/1685954296_647d9ef8160ccb0013295.png!small)

## 关于Shoggoth

Shoggoth是个基于C++和Asmjit库的开源项目，该工具可以帮助广大研究人员针对给定的Shell代码、PE和COFF文件进行多态加密。

Shoggoth可以生成一个输出文件，并以经过模糊处理的形式存储Payload及其相关的加载器。由于输出的内容是与位置无关的，因此我们也可以直接将其作为Shellcode来执行。当Payload正在执行的时候，它会在运行时对自己进行解密。除了加密程序之外，Shoggoth还添加了一些垃圾指令，这些指令在不同程序之间不会做任何的数据修改操作。

## 功能介绍

当前版本的Shoggoth支持下列功能：

> 1、仅适用于x64输入；
>
> 2、能够将PIC
> [_COFF加载器_](https://github.com/frkngksl/Shoggoth/tree/main/COFFLoader)与COFF或BOF输入文件合并；
>
> 3、能够将PIC
> [_PE加载器_](https://github.com/frkngksl/Shoggoth/tree/main/PELoader)与PE输入文件合并；
>
> 4、采用RC4算法的流密码；
>
> 5、采用了随机生成操作的分组密码；
>
> 6、支持垃圾指令生成；

## 工具执行流

![](https://image.3001.net/images/20230605/1685954428_647d9f7ca75dba60be887.png!small)

## 工具要求

项目代码库中提供的原始代码并没有进行完整编译，因此我们还需要对项目进行手动构建和编译。或者，你想要编辑PE加载器或COFF加载器的源代码的话，你应该在设备上安装MinGW，并使用项目提供的Makefiles来进行代码构建。环境要求：

> Visual Studio 2019+
>
> MinGW编译器（可选）

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/frkngksl/Shoggoth.git

## 命令行参数

    
    
    ______ _                                  _
    
     / _____) |                             _  | |
    
    ( (____ | |__   ___   ____  ____  ___ _| |_| |__
    
     \____ \|  _ \ / _ \ / _  |/ _  |/ _ (_   _)  _ \
    
     _____) ) | | | |_| ( (_| ( (_| | |_| || |_| | | |
    
    (______/|_| |_|\___/ \___ |\___ |\___/  \__)_| |_|
    
                        (_____(_____|
    
     
    
                         by @R0h1rr1m
    
     
    
                    "Tekeli-li! Tekeli-li!"
    
     
    
    Usage of Shoggoth.exe:
    
     
    
        -h | --help                             显示工具帮助信息
    
        -v | --verbose                          启用Verbose输出
    
        -i | --input <Input Path>                要加密的Payload输入路径
    
        -o | --output <Output Path>            加密后的结果输出路径
    
        -s | --seed <Value>                    设置随机种子值
    
        -m | --mode <Mode Value>           设置Payload加密模式，支持raw、pe和coff
    
        --coff-arg <Argument>                 设置COSS加载器参数
    
        -k | --key <Encryption Key>             设置第一个加密密钥而不使用随机密钥
    
        --dont-do-first-encryption              不做第一次（流密码）加密
    
        --dont-do-second-encryption          不做第二次（分组密码）加密

## 项目地址

 **Shoggoth** ：【[ _GitHub传送门_](https://github.com/frkngksl/Shoggoth)】

## 参考资料

> [ _https://www.blackhat.com/eu-22/arsenal/schedule/index.html#shoggoth-> asmjit-based-polymorphic-> encryptor-29588_](https://www.blackhat.com/eu-22/arsenal/schedule/index.html#shoggoth-> asmjit-based-polymorphic-encryptor-29588)
>
> [ _https://asmjit.com/_](https://asmjit.com/)
>
> [
> _https://github.com/codewhitesec/HandleKatz_](https://github.com/codewhitesec/HandleKatz)
>
> [
> _https://github.com/frkngksl/Shoggoth/tree/main/COFFLoader_](https://github.com/frkngksl/Shoggoth/tree/main/COFFLoader)
>
> [
> _https://github.com/frkngksl/Shoggoth/tree/main/PELoader_](https://github.com/frkngksl/Shoggoth/tree/main/PELoader)
>
> [
> _https://github.com/frkngksl/Shoggoth/tree/main/stub_](https://github.com/frkngksl/Shoggoth/tree/main/stub)
>
> [ _https://www.nayuki.io/page/rc4-cipher-> in-x86-assembly_](https://www.nayuki.io/page/rc4-cipher-in-x86-assembly)
>
> [ _https://github.com/EgeBalci/sgn_](https://github.com/EgeBalci/sgn)

