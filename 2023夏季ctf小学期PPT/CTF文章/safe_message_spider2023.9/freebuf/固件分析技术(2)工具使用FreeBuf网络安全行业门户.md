历史文章：

> [固件分析技术(1)-简介](../terminal/273150.html)

文章首发于公众号：焊死车门

##  **一、固件分析需要的工具以及环境：**

虚拟机：我选择的是unbuntu16.04。

需要安装的工具：VMware Tools、python、binwalk、qemu、Firmadyne等。

 **Attify OS**

如果你觉得麻烦不想自己搭建虚拟机安装工具的话，也可以使用Attify OS。这是配置和设置IoT渗透测试所需的各种工具的一个iot虚拟机。

![](https://image.3001.net/images/20210514/1621003123_609e8b730dff828ed437d.png!small)

下载地址：

GitHub：https://github.com/adi0x90/attifyos

百度网盘地址：https://pan.baidu.com/s/1B9sjnSjA-yhC8p-aM4mD8w

提取码：39m0

 **虚拟机账号密码**

用户名:oit 密码 :attify123  
数据库:postgre 密码: firmadyne

##  **二、binwalk**

 **（1）安装：**

 **安装git工具**

    
    
    :~$ sudo apt –get update
    
    :~$ sudo apt-get install build-essential autoconf git

 **下载binwalk**

    
    
    :~$ sudo git clone https://github.com/devttys0/binwalk.git

 **安装sasquatch SquashFS提取工具**

    
    
    :~$ sudo apt-get install zliblg-dev liblzma-dev liblzo2-dev
    
    :~$ sudo git clone https://github.com/devttys0/sasquatch

 **安装binwalk**

    
    
    :~$ sudo python setup.py install

 **（2）binwalk的使用：**

 **获取帮助信息：**

binwalk –h

![](https://image.3001.net/images/20210514/1621003155_609e8b93c1ff669af1e91.png!small)

 **对固件进行扫描：**

binwalk xxx.bin

![](https://image.3001.net/images/20210514/1621003168_609e8ba08aa8bf214ebe0.png!small)

 **提取固件文件：**

binwalk –Me xxx.bin

![](https://image.3001.net/images/20210514/1621003182_609e8bae892726cd606fe.png!small)

##  **三、Firmadyne**

当分析路由器固件的时候，手边没有实际设备，只能使用软件模拟，当前对于固件模拟比较好的解决方案就是 Firmadyne。

由于安装较为复杂，本人安装没有成功。故使用Attify OS里面的Firmadyne工具。

 **Firmadyne** **使用**

打开虚拟机，Firmadyne工具目录在/home/tools/ firmadyne

![](https://image.3001.net/images/20210514/1621003203_609e8bc32f50e243c7213.png!small)

以DIR-645举例，将固件二进制文件移动或复制到firmadyne工具目录下运行./fat.py

下图中红框表示添加固件文件地址和固件型号

![](https://image.3001.net/images/20210514/1621003227_609e8bdb82d3dca0bc62d.png!small)

接下来会让你多次输入数据库口令。口令请看Attify OS 介绍部分。

程序完成初始化及镜像创建并分配IP地址后，Firmadyne将会反馈给我们一个IP地址，并提示用户已经完成了固件仿真（镜像创建时间可能较长）。我们可以通过该地址进行Web界面访问，以及通过SSH与固件进行交互等操作。

![](https://image.3001.net/images/20210514/1621003251_609e8bf377ddd977d4e02.png!small)![](https://image.3001.net/images/20210514/1621003269_609e8c05b0da26a72f739.png!small)

##  **四、根文件识别与提取**

固件文件通常以bin、zip、LZMA、arj等文件压缩类型封装，其中，最常见的为bin和zip格式，bin文件是二进制镜像形式，需要使用binwalk提取squashsf文件系统。

二进制镜像提取文件系统界面如下：

![](https://image.3001.net/images/20210514/1621003303_609e8c27ee5785cc2772e.png!small)

对于bin文件来说，不一定就是二进制镜像文件，也有可能是数据文件，首先要对文件进行识别，可以借助linux下的file命令，如下所示：

![](https://image.3001.net/images/20210514/1621003328_609e8c401d1021f78dfc6.png!small)

通过对bin文件的提取，获得了后缀为squashfs的固件文件，从而获得固件的根文件。以D-Link DIR300路由器为例：

![](https://image.3001.net/images/20210514/1621003406_609e8c8ed1c68d9a56c0f.png!small)

还有些经过加密的压缩包，无法直接解压缩，这是厂商对固件做了保护，防止逆向分析。以D-Link DWR-932B路由器为例：

固件地址：

>
> https://media.dlink.eu/ftp/products/dwr/dwr-932/driver_software/DWR-932_fw_revB_2_02_eu_en_20150709.zip

此固件以zip格式进行压缩打包，并经过加密，无法直接解压。

![](https://image.3001.net/images/20210514/1621003431_609e8ca7aea9709c3ac2c.png!small)

使用binwalk进行解包，生成_DWR-932_B1_FW v.02.02EU.zip.extracted文件夹。文件夹下存在40.zip包。

![](https://image.3001.net/images/20210514/1621003448_609e8cb8d0eba9d88e979.png!small)

继续对40.zip解压，发现需要密码。

![](https://image.3001.net/images/20210514/1621003476_609e8cd4e1d9226ee9b3c.png!small)

使用frackzip工具可以破解该zip密码，密码为：beUT9Z。解压后获得文件夹与文件。

![](https://image.3001.net/images/20210514/1621003493_609e8ce57e7ed8ed41878.png!small)

Yaffs2文件就是它的根文件系统，使用binwalk进行解压时发现无法提取出根文件系统。

![](https://image.3001.net/images/20210514/1621003507_609e8cf34741e93e2d1aa.png!small)

提取后的文件夹中并非根文件系统，百度资料后，了解到932B型号的路由器使用了yaffs的原生态压缩算法，可以使用工具unyaffs提取。

![](https://image.3001.net/images/20210514/1621003526_609e8d0634c9861fdcbc0.png!small)

使用unyaffs进行解压。将镜像文件提取到yaffs2-root目录，获得完整的根文件系统。

![](https://image.3001.net/images/20210514/1621003539_609e8d13be08adeece5dd.png!small)

