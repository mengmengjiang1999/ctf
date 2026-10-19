![](https://image.3001.net/images/20221125/1669369382_63808e26477bdf40d10a0.png!small)

## 关于stegoWiper

在最近这十年中，很多网络威胁组织都在使用基于隐写术的恶意软件或相关隐写技术来攻击全球范围内各个地区的不同部门和组织。比如说APT*15/Vixen
Panda、APT*23/Tropic Trooper、APT*29/Cozy
Bear、APT*32/OceanLotus、APT*34/OilRig、APT*37/ScarCruft、APT*38/Lazarus
Group、Duqu Group、Turla、Vawtrack、Powload、Lokibot、Ursnif和IceID等。

我们的研究表明，大多数威胁团体都在使用非常简单的技术（至少从学术角度来看）和已知的工具来规避外部防御，尽管更先进的威胁团体也在使用隐写术来隐藏C&C通信和数据过滤。我们认为，这种缺乏复杂性并不是因为缺乏隐写术知识（一些APT，如Turla，已经尝试了先进的算法），而是因为组织和部门无法保护自己，即使威胁团体使用的是最简单的隐写术技术。

出于这个原因，我们创建了stegoWiper，这是一种通过攻击所有隐写算法中最薄弱的一点（鲁棒性）来盲目破坏任何基于图像的隐写恶意软件的工具。经过测试后发现，stegoWiper

能够破坏目前使用的所有隐写技术和基于隐写术实现的工具（Invoke
PSImage、F5、Steghide、openstego等），以及学术文献中基于矩阵加密和wet-papers,等的最先进算法（例如Hill、J-Uniward、Hugo）。事实上，隐写技术越复杂，stegoWiper产生的干扰就越大。

除此之外，stegoWiper实现的主动攻击技术允许我们实时中断组织通过网络代理ICAP（互联网内容适配协议）服务交换的所有图像中的任何隐写Payload，而无需首先识别图像是否包含隐藏数据。

## 工具运行机制

stegoWiper能够删除输入文件中的所有元数据注释，还为图像添加了一些难以察觉的噪声（不管它是否包含隐藏的Payload）。如果图像确实包含隐写Payload，这种随机噪声会改变它，因此如果你尝试提取它，它将失败或损坏，因此隐写软件无法执行。

值得注意的是，由于噪声是随机的并且分布在整个图像上，攻击者无法知道如何避免，这一点很重要。

## 工具下载

该工具本质上是一个Shell脚本，广大研究人员可以使用下列命令将该项目源码克隆至本地，然后直接运行脚本即可：

    
    
    git clone https://github.com/mindcrypt/stegowiper.git

## 工具使用&参数

    
    
    stegoWiper v0.1 - Cleans stego information from image files
    
                      (png, jpg, gif, bmp, svg)
    
     
    
    Usage: ${myself} [-hvc <comment>] <input file> <output file>
    
     
    
    Options:
    
      -h              显示工具帮助信息和退出
    
      -v              开启Verbose模式
    
      -c <comment>    像输出的图像文件添加注释<comment>

## 工具使用样例-破坏隐写术

    
    
    stegowiper.sh -c "stegoWiped" ursnif.png ursnif_clean.png

项目提供的examples/目录中包含一些基础图像文件，这些文件中使用了各种不同的隐写算法隐藏了敏感信息，大家可以使用setgoWiper对这些文件进行测试。

## 许可证协议

本项目的开发与发布遵循GPL v3开源许可证协议。

## 项目地址

 **stegoWiper** ：【[ _GitHub传送门_](https://github.com/mindcrypt/stegowiper)】

