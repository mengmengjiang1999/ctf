![1.jpg](https://image.3001.net/images/20190721/1563705694_5d34415e9a807.jpg!small)

## Rifiuti2介绍

 **Rifiuti2是一款专门用于分析Windows回收站文件-INFO2格式文件的分析工具。在Windows环境下的设备取证分析工作中，经常需要涉及到针对Windows回收站文件的分析工作。Rifiuti2可以提取出目标时间的文件删除时间，原始文件路径和被删除的文件大小，并判断被删除的文件是否已被永久移除。**

### 工具下载

Rifiuti2：【[Windows
32/64位源码](https://github.com/abelcheung/rifiuti2/releases/latest)】

### 注意事项

1、 系统支持UTF-8编码（除Windows控制台外），文件输出同样为UTF-8格式。

2、 -8选项已失效，不会以任何方式影响输出。

## 工具使用

Rifiuti2为可移植版本，并且可以在命令行环境中运行。根据对应的Windows回收站格式，我们可以选择两种二进制文件（大多数情况下只需使用第一种格式）：

**程序** **** |  **操作系统版本** **** |  **功能** ****  
---|---|---  
rifiuti-vista |  Vista – Win10 |  扫描 \$Recycle.bin 风格目录  
rifiuti |  Win95 – XP/2003 |  读取 \RECYCLED or \RECYCLER 目录中的INFO 或 INFO2 文件  
  
下面给出的是大多数用户的常用选项：

**选项** **** |  **功能** ****  
---|---  
-o <FILE> |  将数据输出至文件  
-x |  输出XML格式文件  
-l <CP> |  显示文件遗留信息  
  
有关完整的工具选项以及详细的用法说明，可以参阅[readme.html文档](https://github.com/abelcheung/rifiuti2/blob/master/README.md)。

### 工具使用样例

扫描\case\S-1-2-3\目录下的索引文件，根据本地时间Zone调整所有的文件删除时间，并将分析结果写入到result.xml文件中：

    
    
    rifiuti -vista.exe-x -z -o result.xml \case\S-1-2-3\

假设INFO2文件是日版Windows（codepage932）生成的，你可以使用下列命令按行生成所有信息：

    
    
    rifiuti -l CP932 -t "\n" INFO2

### 支持的平台

目前该工具已在Linux、Windows 7和FreeBSD平台上成功测试，并使用了Qemu模拟器在很多大端平台上进行了测试。

## 工具下载

### Windows

Windows代码可以直接从该项目的GitHub
Release页面中获取：【[传送门](https://github.com/abelcheung/rifiuti2/releases)】

请注意，v0.6.1版本为目前Rifiuti2的最新版本，可以直接在Windows XP和Windows
2003上运行，我们会在之后的版本中添加对Vista或更高版本的支持。

### Linux

1、 用户可从Debian和Ubuntu获取官方DEB数据包，并支持大多数专注于安全和取证的衍生产品：

> Kali Linux
>
> Deft X Virtual Appliance
>
> BackBoxLinux

2、
[Linux取证工具库（LiFTeR）](https://forensics.cert.org/ByPackage/rifiuti2.html)的RPM包可以在Fedora上使用，并支持CentOS和Rhel。

3、
Rifiuti2支持[ArchStrike](https://archstrike.org/packages/rifiuti2)（Archsault），一个渗透测试衍生工具。

### FreeBSD

支持官方[FreeBSD端口](https://www.freebsd.org/cgi/ports.cgi?query=rifiuti2)。

### 其他平台（需编译源码）

针对目前Rifiuti2还不支持的平台，我们可以直接编译源码来进行平台适配。Rifiuti2基于常用的autotools机制：

    
    
    ./configure&& make check && make install

更多信息，请参考这篇【[文档](https://github.com/abelcheung/rifiuti2/wiki/Compile-From-Source)】。

## 工机具运行截图

![2.png](https://image.3001.net/images/20190721/1563705798_5d3441c695d44.png!small)

![3.png](https://image.3001.net/images/20190721/1563705802_5d3441cac25ea.png!small)

![4.png](https://image.3001.net/images/20190721/1563705807_5d3441cf32dd3.png!small)

### 许可证协议

Rifiuti2遵循[BSD开源许可证协议](https://github.com/abelcheung/rifiuti2/blob/master/docs/LICENSE.md)。

## 项目地址

Rifiuti2：【[GitHub传送门](https://github.com/abelcheung/rifiuti2)】

***参考来源：[abelcheung](https://github.com/abelcheung/rifiuti2)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

