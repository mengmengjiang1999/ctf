**最近使用IDA
Pro查看一个x86的exe文件，发现为静态编译文件，其中包含大量的OpenSSL的库函数，于是上网搜索对应的签名文件，并没有找到该版本OpenSSL的库函数签名，便亲自做一个签名文件。**

##  一、实验环境

> 操作系统：Windows 10
>
> 编程环境：VS 2015、ActivePerl 5.26.3 Build 2603
>
> IDA Pro 7.0

##  二、制作签名

制作和应用签名文件一共分为4个步骤，（1）获得静态库文件；（2）利用静态库生成模式文件；（3）利用模式文件生成签名文件；（4）应用签名文件。步骤如图1所示。

![](https://image.3001.net/images/20200426/1587889484_5ea5454c4eb3a.png!small)

图1 创建和应用签名文件的步骤

###  2.1 搭建编译环境

首先在虚拟机中安装好VS2015和Perl。Perl安装好后，如图2所示显示结果，则说明安装成功。

![](https://image.3001.net/images/20200426/1587889578_5ea545aa52628.png!small)

图2 测试perl是否安装成功

###  2.2 编译库文件

首先在exe文件中发现字符串“AESpart of OpenSSL 1.0.2h 3 May
2016”，可以确定OpenSSL的版本为1.0.2h；并且exe中有“openssl-dist-1.0.2h-vs2015”字符串，可以确定为VS2015编译。

（1）将下载到的openssl-1.0.2h.tar.gz源代码解压（下载地址<https://www.openssl.org/source/old/1.0.2/>）。

（2）在开始菜单打开“VS2015开发人员命令提示”命令行工具，切换到OpenSSL源代码目录下。

（3）在命令行中执行perlConfigure VC-WIN32 no-shared no-asm
--prefix=C:\Users\user\Desktop\download\x86_build_out命令，执行结果如图3所示。

![](https://image.3001.net/images/20200426/1587889638_5ea545e6305f2.png!small)

图3 执行perl命令

参数解释如下。

> Configure是OpenSSl源码中自带的命令文件，必选参数；
>
> VC-WIN32表示编译x86版本，VC-WIN64A表示编译x64版本，debug-VC-WIN32表示编译debug版x86版本，必选参数；
>
> no-shared表示编译成静态链接lib模块，shared表示编译成动态链接库dll模块，必选参数；
>
> no-asm如果要本地优化，还需要下载NASM，这里直接用no-asm选项，因此不需要下载NASM，必选参数；
>
> \--prefix是OpenSSL编译完后的安装路径，必选参数；

（4）在命令行中执行ms\do_ms，如图4所示。

![](https://image.3001.net/images/20200426/1587889732_5ea54644422aa.png!small)

图4 执行do_ms

然后执行nmake-f ms\nt.mak命令编译OpenSSL，该命令耗时较长，执行完毕后在源代码目录下/out32中生成编译结果。

执行nmake-f ms\nt.mak test命令测试上一步编译结果是否有问题。

执行nmake-f ms\nt.mak install命令，将编译结果整理到目标文件夹中，如图5所示。

![](https://image.3001.net/images/20200426/1587889829_5ea546a549932.png!small)

图5 编译结果文件夹

其中lib文件夹下有两个库文件：libeay32.lib（11.8MB），ssleay32.lib（1.96MB）。

###  2.3 生成签名文件

（1）使用IDA Pro 7.0的“flair70.zip”工具包中的pcf工具创建模式文件（pat）。使用命令pcf libeay32.lib
libeay32.pat生成模式文件，如图6所示。

![](https://image.3001.net/images/20200426/1587889943_5ea547171078e.png!small)

图6 生成libeay32.pat文件

（2）使用sigmake
libeay32.patlibeay32.sig命令生成sig文件，如图6所示。其中提示有116个函数有冲突，并且在当前文件下生成了libeay32.exc，libeay32.exc文件内容如下所示，该文件中列出了所有的冲突函数。

解决冲突的办法有2种，第一种方法是删除文件开头的4行，这样sigmake会排除所有这些冲突的函数。第二种方法是在你认为正确的函数名添加符号+，然后删除文件头前4行，如下所示。

将编辑后的exc文件保存，再次执行sigmake函数生成libeay32.sig文件，如图7所示。

![](https://image.3001.net/images/20200426/1587890568_5ea549888900b.png!small)

图7 生成sig文件

同样的步骤可以生成ssleay32.lib的签名文件。

###  2.4 应用签名

将生成的两个签名文件（libeay32.sig、ssleay32.sig）复制到IDA Pro的签名文件夹中（默认目录X:\Program
Files\IDA 7.0\sig\pc），使用热键Shift+F5打开IDA Pro的签名窗口，然后右键，选择“Apply new
signature...”菜单应用新的签名，结果如图8所示。

![](https://image.3001.net/images/20200426/1587890647_5ea549d79f7e2.png!small)

图8 签名文件应用结构

如图8所示，libeay32签名匹配出2441个库函数，ssleay32签名匹配出664个库函数，其中vcseh签名是IDA Pro自动加载的签名文件。

如果有多个lib文件，对应生成多个sig文件比较繁琐，也可以将多个模式文件生成一个签名文件，使用命令sigmake
libeay32.patssleay32.pat openSSL_102h.sig，如图9所示。

![](https://image.3001.net/images/20200426/1587890743_5ea54a37a052f.png!small)

图9 合并生成签名文件

##  三、冲突函数查看

打开libeay32.exc文件，可以看到如下的所示的内容，其中_SSL_CTX_sessions函数和_SSL_get_wbio函数为两个冲突的函数。

使用7-zip将ssleay32.lib解压开，使用IDA
Pro加载ssl_lib.obj文件，可以看到_SSL_CTX_sessions函数和_SSL_get_wbio函数分别如图10和图11所示，可见两个函数的机器码均为8B4424048B4010C3，所以两个函数冲突。

![](https://image.3001.net/images/20200426/1587890809_5ea54a79aaf54.png!small)

图10 _SSL_CTX_sessions函数

![](https://image.3001.net/images/20200426/1587890824_5ea54a885850e.png!small)

图11 _SSL_get_wbio函数

IDA Pro提供的签名识别技术称之为FLIRT（Fast Library Identification andRecognition
Technology，库文件快速识别与鉴定技术），该技术利用库文件中二进制函数的机器码，来快速识别文件中的库函数，使得反汇编代码可读性更强，FLIRT技术的具体细节详见参考文献【1】。

##  四、相关资源

这里给出两个收集签名文件的网址。

> <https://github.com/push0ebp/sig-database>
>
> <https://github.com/Maktm/FLIRTDB>

idb2pat.py是火眼公司FireEye Labs Advanced
ReverseEngineering团队编写的Python脚本，该脚本支持将IDB数据库转换成模式文件（pat），继而转换为签名文件（sig）。该脚本应用于已经分析了一个二进制文件，手工命名部分了关键函数，再次分析另一个类似二进制文件时，可以应用此脚本快速迁移函数名称。注意该脚本保存模式文件时，不支持中文目录。<https://github.com/fireeye/flare-ida>。

##  五、总结

制作一个优质的签名文件可以大大加快逆向进度。制作签名文件有许多的考虑的因素，包括源代码版本、编译优化选项、编译器类型、编译器版本、是否release版本等。如果签名匹配效果不好，可以尝试不同的编译参数。

##  参考文献

> [1] <https://www.hex-rays.com/products/ida/tech/flirt/in_depth/>IDA
> F.L.I.R.T. Technology: In-Depth
>
> [2]《IDA Pro权威指南》
>
> [3] <https://blog.csdn.net/traceme2011/article/details/90606018>
> 用VS2015编译OpenSSL
>
> [4]
> <https://blog.csdn.net/liang19890820/article/details/51658574>Windows下编译OpenSSL
>
> [5] <https://www.fireeye.com/blog/threat-> research/2015/01/flare_ida_pro_script.html>FLARE IDA Pro Script Series:
> Generating FLAIR function patterns using IDAPython

 ***本文作者： dolphin，转载请注明来自FreeBuf.COM**  
  

