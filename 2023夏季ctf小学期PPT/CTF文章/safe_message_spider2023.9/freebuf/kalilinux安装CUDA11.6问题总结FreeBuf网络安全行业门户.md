> CUDA是一种NVIDIA推出的通用并行计算架构，该架构使GPU能解决复杂的计算问题。

N卡优越的情况下，使用cuda是最好的。

##  **一、查看自身的N卡及适合的cuda版本**

### 查看如下：

1.在右下角选择n卡的控制面板

![](https://image.3001.net/images/20220414/1649876113_62571c91328211d20dd78.png!small)

2.控制面板左下角——系统信息——组件——文件名下第三个既是显卡cuda 11.4.136

 **下载的cuda版本要高于n卡支持最大值，理论上只要下载最新版cuda就能涵盖所有显卡。**

![](https://image.3001.net/images/20220414/1649875981_62571c0d3ad3aea044a86.png!small)

## 二、[ **CUDA官网下载地址（点击可用）**](https://developer.nvidia.com/cuda-downloads)

> [kali
> linux](https://baike.baidu.com/item/kali%20linux/8305689#:~:text=Kali%20Linux%E6%98%AF%E5%9F%BA%E4%BA%8E%20Debian%20%E7%9A%84%20Linux%20%E5%8F%91%E8%A1%8C%E7%89%88%EF%BC%8C%20%E8%AE%BE%E8%AE%A1%E7%94%A8%E4%BA%8E%E6%95%B0%E5%AD%97%E5%8F%96%E8%AF%81%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E3%80%82%20%E6%AF%8F%E4%B8%80%E5%AD%A3%E5%BA%A6%E6%9B%B4%E6%96%B0%E4%B8%80%E6%AC%A1%E3%80%82,%E7%94%B1Offensive%20Security%20Ltd%E7%BB%B4%E6%8A%A4%E5%92%8C%E8%B5%84%E5%8A%A9%E3%80%82%20%E6%9C%80%E5%85%88%E7%94%B1Offensive%20Security%E7%9A%84Mati%20Aharoni%E5%92%8CDevon%20Kearns%E9%80%9A%E8%BF%87%E9%87%8D%E5%86%99BackTrack%E6%9D%A5%E5%AE%8C%E6%88%90%EF%BC%8CBackTrack%E6%98%AF%E4%BB%96%E4%BB%AC%E4%B9%8B%E5%89%8D%E5%86%99%E7%9A%84%E7%94%A8%E4%BA%8E%E5%8F%96%E8%AF%81%E7%9A%84Linux%E5%8F%91%E8%A1%8C%E7%89%88%20%E3%80%82)（百度介绍）是基于Debian的linux发行版，所以在此选择Debian发行版

![](https://image.3001.net/images/20220414/1649874807_625717776b43a3d6e6cc5.png!small)

查询版本不一定有效，比如： **lsb_release -a**

![](https://image.3001.net/images/20220414/1649874289_62571571460ee070e27eb.png!small)
显示linux rolling，在cuda中没有相对应的版本

> 根据安装指南，将下方代码放入终端运行即可下载，确保网络稳定

![](https://image.3001.net/images/20220414/1649874947_6257180320172262b8895.png!small)

> 如果网络不稳定，反复运行产生多个文件，注意将无效文件删除，有效文件重命名

下载时防止虚拟机挂起，执行以下操作：

linux系统如下：

设置setting

![](https://image.3001.net/images/20220414/1649884192_62573c206c4a17e8a9910.png!small)

电源管理器power manager

![](https://image.3001.net/images/20220414/1649884274_62573c72922787c8289b1.png!small)

显示display-全部改成never

![](https://image.3001.net/images/20220414/1649884309_62573c95e9a6153ecbb91.png!small)

## 三、[linux debian11遇到Warning: apt-key is deprecated
(SOLVED)](https://suay.site/?p=526)

    
    
    运行安装指南第三条：sudo apt-key add /var/cuda-repo-debian11-11-6-local/7fa2af80.pu **提示 warning：apt-key is deprecated**参照国外大佬的内容，我们可以很好解决这个问题，将语句转化成以下形式。（具体看三号标题的链接，或直接看下方翻译）

 **1.远程密钥的添加**

    
    
    curl -s URL | sudogpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/NAME.gpg --import

 **2.本地密钥的添加**

    
    
    catURL.pub | sudogpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/NAME.gpg --import

 **这些指令, 需要替换如下内容:**

>  **URL** \- .pub文件的地址
>
>  **NAME** \- 自定任意文件名
>
>  **FILE** \- .pub文件的文件名

 **然后必须使用以下指令，为添加后的文件设置正确权限:**

sudochmod644 /etc/apt/trusted.gpg.d/NAME.gpg

![](https://image.3001.net/images/20220414/1649882228_62573474be07d125f65e2.png!small)

> 运行第四条：sudo add-apt-repository contrib``

![](https://image.3001.net/images/20220414/1649900866_62577d421376c73b21c6c.png!small)显示已经有了，不用管

> 运行第五条：sudo apt-get update``

运行后，可以再运行下sudo apt-get upgrade

##  **四、linux debian11遇到软件包liburcu6没有可安装候选**

 **libcufile-11-6：依赖：liburcu6但无法安装它**

> 运行第六条：sudo apt-get -y install cuda

直接运行第六条出现以下问题——XXXXXX：依赖liburcu6但无法安装

![](https://image.3001.net/images/20220414/1649901705_62578089ee570563faa98.png!small)

解决方案是下载liburcu6，但是直接下载sudo apt-get install liburcu6会出现以下问题（见下图）

E：软件包liburcu6没有可安装候选![1649901389_62577f4de457800aac420.png!small](https://image.3001.net/images/20220414/1649901389_62577f4de457800aac420.png!small)

**上面两个问题是相同的解决方案，要求下载liburcu6：[下载链接](https://packages.debian.org/bullseye/liburcu6)**

经过以上（sudo apt-get install
liburcu6），可知国内软件源中找不到相应软件包，需要我们将liburcu6的镜像放入软件源中，具体如下：

> 根据上方刚给的链接，debian11版本下，选择amd64，在给出的url中选择亚洲镜像
>
> 下方其一
>
>
> [ftp.cn.debian.org/debian](http://ftp.cn.debian.org/debian/pool/main/libu/liburcu/liburcu6_0.12.2-1_amd64.deb)
>
>
> [ftp.jp.debian.org/debian](http://ftp.jp.debian.org/debian/pool/main/libu/liburcu/liburcu6_0.12.2-1_amd64.deb)
>
>
> [ftp.kr.debian.org/debian](http://ftp.kr.debian.org/debian/pool/main/libu/liburcu/liburcu6_0.12.2-1_amd64.deb)
>
>
> [ftp.hk.debian.org/debian](http://ftp.hk.debian.org/debian/pool/main/libu/liburcu/liburcu6_0.12.2-1_amd64.deb)
>
>
> [ftp.tw.debian.org/debian](http://ftp.tw.debian.org/debian/pool/main/libu/liburcu/liburcu6_0.12.2-1_amd64.deb)
>
> 打开换源文件（换源方式在后面），添加下面这样一行：
>  
>  
>     deb http://ftp.de.debian.org/debian bullseye main
>  
>
> 根据url，替换示例中的 ftp.de.debian.org/debian

例如：deb
http://[ftp.cn.debian.org/debian](http://ftp.cn.debian.org/debian/pool/main/libu/liburcu/liburcu6_0.12.2-1_amd64.deb)bullseye
main

![](https://image.3001.net/images/20220414/1649903127_6257861701166c8b2ab11.png!small)

> 换源口令：sudo vim /etc/apt/sources.list
>
>
> ![](https://image.3001.net/images/20220414/1649903189_62578655c7be396f8ca83.png!small)
>
> 添加完后，esc——：号——输入wq，回车退出

此时才能正常下载liburcu6，正常运行

![](https://image.3001.net/images/20220414/1649903622_62578806d6ae2ea969039.png!small)第六条指令也正常运行

![](https://image.3001.net/images/20220414/1649903694_6257884e9ae9ca55a6c00.png!small)安装的步骤到此结束，用cd切换路径，查看cuda安装情况，具体如下

![](https://image.3001.net/images/20220414/1649904364_62578aec2612d1c7dcf81.png!small)

## 五、linux中cuda添加环境变量（ **nvcc** -V显示Command ‘ **nvcc** ’ not found|source
~/.bashrc 报错：source not found）

最后是添加环境变量，执行以下命令

>  **$ sudo vim ~/.bashrc**

将下面两条放在打开的文件最下方，保存退出

> export PATH=/usr/local/cuda/bin:$PATH  
> export LD_LIBRARY_PATH=/usr/local/cuda/lib64$LD_LIBRARY_PATH

在终端输入nvcc -V，此时发现没有nvcc的指令。因为环境变量的修改没有立即生效，可以使用以下指令立即生效

    
    
     **$ source ~/.bashrc  
    **

在终端输入nvcc -V，如果还是没有，可以先查看/usr/local/cuda/bin内有无nvcc，确认有再进行下一步

可能是因为source没有顺利执行，因为没有进入到linux系统自带的bash shell ，此时在终端尝试先打一个bash，再执行source

然后再执行nvcc -V就行了，具体如下

如下则成功安装

![](https://image.3001.net/images/20220414/1649917977_6257c01969b25dd9fdca1.png!small)

