**MalConfScan是一个Volatility插件，可从已知的恶意软件家族中提取配置信息。Volatility则是一个用于事件响应和恶意软件分析的开源内存取证框架。此工具会在内存映像中搜索恶意软件并转储配置数据。此外，它还具有列出恶意代码所引用的字符串的功能。**

**![MalConfScan：从已知的恶意软件家族中提取配置信息](https://image.3001.net/images/20190516/1557962688_5cdc9fc06aef1.png!small)**

## 支持的恶意软件家族

MalConfScan可以转储以下恶意软件配置数据，已解码的字符串或DGA域：

> Ursnif
>
> Emotet
>
> Smoke Loader
>
> PoisonIvy
>
> CobaltStrike
>
> NetWire
>
> PlugX
>
> RedLeaves / Himawari / Lavender / Armadill / zark20rk
>
> TSCookie
>
> TSC_Loader
>
> xxmm
>
> Datper
>
> Ramnit
>
> HawkEye
>
> Lokibot
>
> Bebloh (Shiotob/URLZone)
>
> AZORult
>
> NanoCore RAT
>
> AgentTesla
>
> FormBook
>
> NodeRAT (<https://blogs.jpcert.or.jp/ja/2019/02/tick-activity.html>)
>
> Pony

## 安装

 **安装软件包**

如果你未安装Yara，请[查看此页面并进行安装](https://yara.readthedocs.io/en/v3.9.0/gettingstarted.html#compiling-and-installing-yara)。

Volatility仅支持Python2。如果你未安装Python2，请安装它。

 **下载 Volatility**

> 下载[Volatility源码](https://www.volatilityfoundation.org/releases)；
>
> 从zip或tar.gz文件中提取Volatility源码
    
    
    $ wget http://downloads.volatilityfoundation.org/releases/2.6/volatility-2.6.zip
    $ unzip volatility-2.6.zip

或从Github克隆。

    
    
    $ git clone https://github.com/volatilityfoundation/volatility.git

 **安装 MalConfScan**

从Github存储库克隆MalConfScan：

    
    
    $ git clone https://github.com/JPCERTCC/MalConfScan.git

安装Python requirements：

    
    
    $ pip install -r MalConfScan/requirements.txt

将MalConfScan复制到Volatility Plug-in文件夹：

    
    
    $ cd MalConfScan
    $ cp -R malconfscan.py utils yara [Extract Volatility Folder]/volatility/plugin/malware

有关Linux上的Volatility安装，请参阅[Volatility
wiki](https://github.com/volatilityfoundation/volatility/wiki/Installation#installing-volatility)。

## 使用

MalConfScan主要有两个功能malconfscan和malstrscan。

 **导出已知的恶意软件配置**

malconfscan可以转储恶意软件配置数据，已解码的字符串或DGA域。

    
    
    $ python vol.py malconfscan -f images.mem --profile=Win7SP1x64

 **示例**

RedLeaves配置数据

![MalConfScan：从已知的恶意软件家族中提取配置信息](https://image.3001.net/images/20190516/1557962710_5cdc9fd68c19e.png!small)

Bebloh配置数据和DGAs

![MalConfScan：从已知的恶意软件家族中提取配置信息](https://image.3001.net/images/20190516/1557962717_5cdc9fddc1fdf.png!small)

FormBook解码的字符串

![MalConfScan：从已知的恶意软件家族中提取配置信息](https://image.3001.net/images/20190516/1557962726_5cdc9fe69e967.png!small)

 **列出引用的字符串**

malstrscan可以列出恶意代码所引用的字符串。配置数据通常由恶意软件编码。恶意软件将已解码的配置数据写入到内存，它可能在内存中。此功能可列出已解码的配置数据。

该功能默认仅列出来自PE加载的内存空间的字符串。-a选项还将列出父内存空间中的字符串，例如Heap。

    
    
    $ python vol.py malstrscan -a -f images.mem --profile=Win7SP1x64

 **示例**

列出Ramnit的引用字符串

![MalConfScan：从已知的恶意软件家族中提取配置信息](https://image.3001.net/images/20190516/1557962750_5cdc9ffe1a971.png!small)

## 和 Cuckoo Sandbox 一起工作

通过将MalConfScan添加到Cuckoo
Sandbox，可以自动转储恶意软件配置数据。如果你想要了解更多详细信息以及如何安装，请查看[MalConfScan with
Cuckoo](https://github.com/JPCERTCC/MalConfScan-with-Cuckoo)。

![MalConfScan：从已知的恶意软件家族中提取配置信息](https://image.3001.net/images/20190516/1557962764_5cdca00c61804.png!small)

 **
*参考来源：[GitHub](https://github.com/JPCERTCC/MalConfScan/wiki)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

