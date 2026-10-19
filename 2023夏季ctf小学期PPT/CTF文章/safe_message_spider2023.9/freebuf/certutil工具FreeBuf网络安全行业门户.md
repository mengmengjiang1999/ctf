## Certutil介绍

 **Certutil.exe** 是一个命令行程序，作为证书服务的一部分安装。您可以使用 certutil.exe 转储和显示证书颁发机构 (CA)
配置信息、配置证书服务、备份和恢复 CA 组件以及验证证书、密钥对和证书链。

如果 certutil 在没有附加参数的证书颁发机构上运行，它会显示当前的证书颁发机构配置。如果 certutil
在非证书颁发机构上运行，则该命令默认为运行该certutil [-dump]命令。 -来自微软官方的解释

但其也可以用来校验文件hash值(支持MD2 MD4 MD5 SHA1 SHA256 SHA384
SHA512)，需要注意的是使用该命令时，算法名称区分大小写，否则会报错；编码解码，下载恶意文件等。

使用命令：

    
    
    certutil -?

查看帮助信息![1639459864_61b82c181a33f376b183e.png!small?1639459863751](https://image.3001.net/images/20211214/1639459864_61b82c181a33f376b183e.png!small?1639459863751)

可以使用certutil -v -?查看更详细的帮助命令。

## 部分命令应用

###  **base64编码**  

在桌面新建了一个名为1.txt的文件，内容为hello certutil

![1639461445_61b83245004096fc86be5.png!small?1639461444093](https://image.3001.net/images/20211214/1639461445_61b83245004096fc86be5.png!small?1639461444093)

使用命令：

    
    
    certutil -encode 1.txt encode.txt

![1639461717_61b833556cd31d707938a.png!small?1639461716328](https://image.3001.net/images/20211214/1639461717_61b833556cd31d707938a.png!small?1639461716328)

![1639461775_61b8338f54fc7ac096d42.png!small?1639461774494](https://image.3001.net/images/20211214/1639461775_61b8338f54fc7ac096d42.png!small?1639461774494)

###  **16进制编码**

使用命令：

    
    
    certutil -encodehex 1.txt encode1.txt

![1639461854_61b833deb8847fae51ed1.png!small?1639461853682](https://image.3001.net/images/20211214/1639461854_61b833deb8847fae51ed1.png!small?1639461853682)

![1639461905_61b83411ee565f0f73468.png!small?1639461905394](https://image.3001.net/images/20211214/1639461905_61b83411ee565f0f73468.png!small?1639461905394)
**base64位解码**

    
    
    certutil -decodehex  InFile OutFile

 **16进制解码**

    
    
    certutil -decodehex InFile OutFile

 **文件hash值校验﻿**

此处以seay源代码审计系统2.1.zip文件举例 **注意MD5大写**

![1639462329_61b835b9b44db3ae9699d.png!small?1639462328627](https://image.3001.net/images/20211214/1639462329_61b835b9b44db3ae9699d.png!small?1639462328627)

 **下载网络文件**

![1639462718_61b8373e6ee60e2a6f2ae.png!small?1639462717473](https://image.3001.net/images/20211214/1639462718_61b8373e6ee60e2a6f2ae.png!small?1639462717473)

 **系统错误代码**

![1639462853_61b837c5bad7e87a75d37.png!small?1639462852606](https://image.3001.net/images/20211214/1639462853_61b837c5bad7e87a75d37.png!small?1639462852606)

