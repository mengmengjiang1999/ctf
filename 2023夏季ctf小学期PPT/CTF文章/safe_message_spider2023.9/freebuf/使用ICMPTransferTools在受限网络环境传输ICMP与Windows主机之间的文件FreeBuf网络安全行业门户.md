## 关于ICMP-TransferTools

ICMP-TransferTools是一款功能强大的文件传输工具，可以帮助广大研究人员在受限网络环境中通过ICMP与Windows主机之间传输文件。

ICMP-TransferTools由四个不同的脚本文件组成，即一个Python服务器和针对不同传输方向（下载和上传）的PowerShell客户端。

## 工具依赖

该工具基于Python和PowerShell开发，除了PowerShell之外，我们还需要在本地设备上安装并配置好Python环境。

该工具唯一需要的依赖组件就是Impacket，我们可以通过pip命令来安装该组件：

    
    
    pip3 install impacket

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/icyguider/ICMP-TransferTools.git

## 工具使用

### 通过ICMP下载文件

在使用该功能的时候，需要用到ICMP-SendFile.py和Invoke-IcmpDownload.ps1这两个脚本并通过ICMP将文件下载到一台Windows主机中。

Python服务器必须要提前运行才可以实现文件下载，脚本的使用方法请参见下列帮助信息：

    
    
    usage: ICMP-SendFile.py [-h] [-v] [-b 1000] source destination file
    
     
    
    ICYGUIDER'S ICMP FILE DOWNLOAD SERVER
    
     
    
    positional arguments:
    
      source                当前主机的公共IP地址
    
      destination            目的主机的公共IP地址
    
      file                   通过ICMP传输的文件
    
     
    
    optional arguments:
    
      -h, --help             显示帮助信息和退出
    
      -v, --verbose          开启Verbose输出模式
    
      -b 1000, --block-size 1000
    
                           每个数据区块的大小（默认：1000）

接下来，我们就可以按照下列方式使用PowerShell客户端来下载文件了：

    
    
    Invoke-IcmpDownload PublicIPAddressOfServer FileToDownload

 **功能使用演示**

![](https://image.3001.net/images/20220414/1649867389_6256fa7d8512fbd6cc17d.gif)

### 通过ICMP上传文件

在使用该功能的时候，需要用到ICMP-ReceiveFile.py和Invoke-IcmpUpload.ps1这两个脚本并通过ICMP将文件上传/提取到一台Windows主机中。

Python服务器必须要提前运行才可以实现文件上传，脚本的使用方法请参见下列帮助信息：

    
    
    usage: ICMP-ReceiveFile.py [-h] src file
    
     
    
    ICYGUIDER'S ICMP FILE UPLOAD SERVER
    
     
    
    positional arguments:
    
      src         客户端的公共IP地址
    
      file         写入数据的目标文件
    
     
    
    optional arguments:
    
      -h, --help   显示帮助信息和退出

接下来，我们就可以按照下列方式使用PowerShell客户端来下载文件了：

Invoke-IcmpUpload PublicIPAddressOfServer FileToUpload

 **功能使用演示**

![](https://image.3001.net/images/20220414/1649867411_6256fa93912b8605fe271.gif)

## 开源许可证

本项目的开发与发布遵循[ _GPL_ _-3.0_](https://github.com/icyguider/ICMP-TransferTools/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **ICMP-TransferTools：** 【[ _GitHub传送门_](https://github.com/icyguider/ICMP-TransferTools)】

