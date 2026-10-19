![20190102105434.png](https://image.3001.net/images/20190102/1546397720_5c2c28182cfce.png!small)

**Sodium一个易于使用的可为我们提供加密、解密、签名，密码哈希等功能的软件库。除了自身强大的功能外，它还为我们提供了一个兼容API和一个外部API，以进一步的帮助我们提高其可用性。Sodium的目标是提供构建更高级别加密工具所需的所有核心操作。**

Sodium支持跨平台和跨语言， 你可以在各种编译器和操作系统上运行它，包括Windows（使用MinGW或Visual
Studio，x86和x86_64），iOS和Android。Javascript和WebAssembly版本也可用并受到完全的支持。

值得一提的是，虽然Sodium的设计着重高安全和易用性，但其整体速度与大多数实现相比更快。

## libsodium 下载

>  **​[Github](https://github.com/jedisct1/libsodium)**
>
>  **​[Tarballs 和
> 预编译二进制文件](https://download.libsodium.org/libsodium/releases/)​**
>
> [ **​在线文档**](https://doc.libsodium.org/)

## 离线文档

该文档可下载保存为ePUB文件格式（适用于iPad，iPhone，Mac），MOBI（适用于Kindle）以及PDF：<https://www.gitbook.com/book/jedisct1/libsodium/details>​

## 安装

###  **在类Unix系统上编译安装**

Sodium是一个共享库具有独立于机器的标头集，因此可以轻松地被第三方项目所使用。

该库使用autotools构建，因此非常易于打包。

安装也很简单，编译和测试都可利用多个CPU内核。

首先我们下载[libsodium](https://download.libsodium.org/libsodium/releases/)，然后执行以下命令：

    
    
    ./configure
    make && make check
    sudo make install

由于不同的文件被编译用于不同的CPU类，并且为了防止不必要的优化，因此建议尽量避免链接时优化（LTO）。

在Linux上，如果进程在make check步骤中挂起，则系统PRG可能没有正确播种。有关解决此问题的方法，请参阅“使用”部分中的说明。

###  **在Windows系统上编译安装**

通常不需要在Windows上进行编译，因为MinGW和Visual Studio的预构建库是可用的（参见下文）。

但是，如果你想自己编译，先从Git存储库克隆[稳定分支](https://github.com/jedisct1/libsodium/archive/stable.zip)。

然后可以在builds/msvc目录中找到Visual Studio的解决方案。

要使用mingw进行编译，请在win32或x64目标上运行/dist build/msys2-win32.sh或/dist
build/msys2-win64.sh脚本。

###  **预构建库**

提供了可用于[Visual Studio
2010，2012，2013，2015和2017的预构建x86和x86_64库](https://download.libsodium.org/libsodium/releases/)，以及MinGW32和MinGW64的预构建库。包括头文件，以及所有受支持编译器版本的静态（.LIB）和共享（.DLL）库。

Visual Studio注意事项：

静态链接Sodium的项目必须定义一个名为SODIUM_STATIC的宏，这将防止符号定义被__dllexport引用。

###  **交叉编译**

支持交叉编译。以下是使用ARM嵌入式处理器的GNU工具交叉编译到ARM的示例

    
    
    export PATH=/path/to/gcc-arm-none-eabi/bin:$PATH
    export LDFLAGS='--specs=nosys.specs'
    export CFLAGS='-Os'
    ./configure --host=arm-none-eabi --prefix=/install/path
    make install 

make check也可以构建测试应用程序，但必须在本地平台上运行。

注意：--specs=nosys.specs仅用于ARM编译工具链。

###  **使用CompCert编译**

最新发布版可使用CompCert编译器进行编译。编译命令如下：

    
    
    $ env CC=ccomp CFLAGS="-O2 -fstruct-passing -Usize_t" ./configure && \
    make check && sudo make install

###  **稳定分支**

这里我们建议大家使用tarball来克隆libsodium
git存储库，因为tarball不需要libtool和autotools等依赖项，其次就是使用稳定分支下的版本。

获取稳定分支中的最新版：

    
    
    git clone https://github.com/jedisct1/libsodium --branch stable

## 使用入门

请参阅[快速开始](https://libsodium.gitbook.io/doc/quickstart)和[使用](https://libsodium.gitbook.io/doc/usage)部分。

##  **完整性检查**

可以使用[Minisign](https://jedisct1.github.io/minisign/)和以下Ed25519密钥验证分发文件：

    
    
    RWQf6LRCGA9i53mlYecO4IzT51TGPpvWucNSCh1CBM0QTaLn73Y7GFO3

或使用GnuPG和以下RSA密钥：

    
    
    -----BEGIN PGP PUBLIC KEY BLOCK----- 
    Version: GnuPG v1 (OpenBSD)
    ​
    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 =Hkmu 
    -----END PGP PUBLIC KEY BLOCK-----
## 漏洞报告

我们鼓励用户和研究人员使用PGP加密的电子邮件向我们发送报告有关Sodium库中可能存在的漏洞详情。

请使用上面的PGP密钥将详细信息发送到：j@pureftpd.org。

***参考来源：[libsodium](https://libsodium.gitbook.io/doc/)，FB小编secist编译，转载请注明来自FreeBuf.COM
**  

