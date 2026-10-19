![](https://image.3001.net/images/20200304/1583312146_5e5f6d1286dc7.jpg!small)

##  Xencrypt

 **今天给大家介绍的这款工具名叫Xencrypt，它是一款基于PowerShell脚本实现的反病毒绕过工具。如果你不想花时间对类似invoke-mimikatz这样的PowerShell脚本进行混淆处理以避免其被检测到的话，那么Xencrypt就是你的最佳选择了。Xencrypt能够自动对目标脚本代码进行处理，并且可以生成近乎无限量的变种代码，以帮助研究人员绕过基于签名机制的反病毒检测产品。**

从本质上来说，Xencrypt是一款PowerShell代码加密工具，它使用了AES加密算法以及Gzip/DEFLATE压缩算法来对目标脚本代码进行处理，并生成一个完全不同的脚本，但功能却一模一样。首先，它会对输入的脚本代码进行加密和压缩，然后将脚本数据以Payload的形式存储在新的脚本中，而这个新的脚本Payload在运行之前是无法被解密或解压的。

###  功能介绍

当前版本的Xencrypt拥有以下几种强大的功能：

> 1、绕过AMSI以及VirusToal上目前所使用的所有现代反病毒检测引擎；
>
> 2、压缩和加密PowerShell脚本；
>
> 3、资源消耗和开销非常小；
>
> 4、使用随机化变量名以进一步实现混淆处理；
>
> 5、随机化加密和压缩，还可以调整语句在代码中的顺序，以获得最大熵；
>
> 6、可根据用户需求自行修改并创建自己的密码器变种；
>
> 7、支持递归分层加密，最多可支持500层加密；
>
> 8、支持Import-Module以及标准方式来运行；
>
> 9、GPLv3-开源许可证协议；
>
> 10、所有的功能都以单一文件实现，最大程度实现灵活性；

##  工具使用

广大研究人员可以直接使用下列命令来生成加密和压缩处理后的新脚本：

    
    
    Import-Module ./xencrypt.ps1
    
        Invoke-Xencrypt -InFile invoke-mimikatz.ps1 -OutFile xenmimi.ps1

运行了上述命令之后，你将会拿到一个已加密的文件名为“xenmimi.ps1”的PowerShell文件，该文件存储在当前工作目录下。你可以按照正常的脚本使用方式来运行或使用该脚本：

    
    
    Import-Module ./xenmimi.ps1
    
        Invoke-Mimikatz

除此之外，它还支持通过-Iterations参数来进行递归分层加密：

    
    
    Invoke-Xencrypt -InFile invoke-mimikatz.ps1 -OutFile xenmimi.ps1 -Iterations 100

上述命令将会对目标脚本进行100次的压缩和加密处理，这种方式对于动态反病毒产品绕过来说是非常有用的，因为这些反病毒产品都有一个代码分析的超时时间。在这里，动态扫描必须要扫描完整个文件代码链才有可能识别到恶意负载，因此通过递归分层加密将能够绕过这类AV产品。

不过，使用递归分层加密的话，将有可能导致最终生成的脚本文件体积过大，而且生成和输出文件可能也需要花很长的时间，具体将取决于脚本和请求的迭代次数。

##  工具运行截图

![](https://image.3001.net/images/20200304/1583312191_5e5f6d3f2a6a5.png!small)![](https://image.3001.net/images/20200304/1583312191_5e5f6d3f39e2d.png!small)

##  项目地址

> Xencrypt：【[GitHub传送门](https://github.com/the-xentropy/xencrypt)】

 *** 参考来源：[the-xentropy](https://github.com/the-xentropy/xencrypt)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

