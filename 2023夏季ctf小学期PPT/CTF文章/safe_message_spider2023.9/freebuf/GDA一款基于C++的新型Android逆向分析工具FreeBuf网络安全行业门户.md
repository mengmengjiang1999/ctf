![](https://image.3001.net/images/20200203/1580671550_5e37223e795e7.png!small)

## GDA(GJoy Dex Analysizer)

**GDA是一款完全基于C++开发的新型反编译工具，因此该工具并不仅依赖于Java平台。该工具使用起来非常方便，而且运行速度非常快，支持APK、DEX、OBED和oat等文件格式。**

实际上，GDA是一款新型的Dalvik字节码反编译工具。该工具是完全独立的，并且运行非常稳定，并且能够在没有安装Java
VM的环境下运行。GDA的大小只有2MB，我们可以直接在任何新安装的Windows操作系统或虚拟机系统中使用该工具，无需进行额外配置。此外，GDA还有以下更加出色的功能：

![](https://image.3001.net/images/20200203/1580671559_5e372247674f6.png!small)

## 功能介绍

### 交互式操作

> 1、字符串、类、方法和域的交叉引用；
>
> 2、搜索字符串、类方法和域；
>
> 3、Java代码注释；
>
> 4、方法、域、类的重命名；
>
> 5、将分析结果存储至GDA数据库文件中；

### 辅助分析实用程序

> 1、从ODEX中提取DEX；
>
> 2、从OAT中提取DEX；
>
> 3、XML解码器；
>
> 4、算法工具；
>
> 5、设备内存导出；

### 新功能

> 1、采用C++开发的全新Dalvik反编译工具；
>
> 2、有好的GUI界面；
>
> 3、支持Python脚本；
>
> 4、封装器识别；
>
> 5、多DEX支持；
>
> 6、反混淆支持；
>
> 7、扫描恶意API链；
>
> 8、等等......

## 工具安装

目前，广大用户可以将项目源码直接克隆至本地，然后鼠标双击bin文件即可开始使用。下载命令如下：

    
    
    git clone https://github.com/charles2gan/GDA-android-reversing-Tool.git

### 算法工具

该工具支持下列算法：

> 1、散列算法：md2 md4 md5 sha sha1 sha224 sha256 sha384 sha512
>
> 2、对称加密：des idea rc2 rc4 rc4-40 rc2-40 rc2-64 bf cast5 aes（128192256），具有ecb
> cbc ofb cfb等模式，其他模式例如（cfb1 cfb8）
>
> 3、RSA编码算法：base62，base64

## 工具运行截图

文件加载和反编译

![](https://image.3001.net/images/20200203/1580671601_5e3722717d4bd.gif!small)

恶意软件扫描、API查询、x-ref...

Url、Xml、字符串x-ref...

![](https://image.3001.net/images/20200203/1580671629_5e37228d041b4.gif!small)

变量追踪

![](https://image.3001.net/images/20200203/1580671637_5e37229594e7a.gif!small)

## 项目地址

> GDA：【[ _GitHub传送门_](https://github.com/charles2gan/GDA-android-reversing-> Tool)】

 *** 参考来源：[ _charles2gan_](https://github.com/charles2gan/GDA-android-reversing-Tool)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

