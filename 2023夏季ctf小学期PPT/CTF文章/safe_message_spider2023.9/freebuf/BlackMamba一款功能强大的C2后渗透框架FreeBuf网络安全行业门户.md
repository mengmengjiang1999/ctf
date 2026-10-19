![](https://image.3001.net/images/20210310/1615370419_604898b3617b2b87478c0.png!small)

## BlackMamba

BlackMamba是一款多客户端C2/后渗透框架，并且还支持某些网络间谍软件的功能。该工具基于Python
3.8.6和QT框架开发，可以在渗透测试任务中为广大研究人员提供帮助。

 **BlackMamba的功能如下：**

> 多客户端支持：支持同时连接多个客户端；
>
> 实时通信更新：支持客户端和服务器端之间的实时通信和更新；
>
> 通信加密：支持对除了屏幕视频流之外的所有通信信息进行加密；
>
> 截屏收集：从客户端获取实时截屏；
>
> 视频流：实时查看客户端屏幕视频流；
>
> 客户端锁定：锁定和解锁客户端设备；
>
> 文件传输加密（上传/下载）：可从客户端下载文件，或向客户端上传文件；
>
> 键盘记录：记录客户端键盘按键信息；
>
> Web下载器：支持从URL下载文件；

## 工具安装-服务器端

首先，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/loseys/BlackMamba.git

接下来，安装PIP包：

    
    
    pip install -r requirements.txt
    
     
    
    PyQt5
    
    Pillow
    
    PyAutoGUI
    
    pytest-shutil
    
    cryptography
    
    pynput
    
    pygame

接下来，在网关或路由器打开端口65000和65005，具体端口号可选。为BlackMamba创建防火墙例外规则，或直接禁用防火墙。

打开“BlackMamba/bin/profile/socket.txt”文件，然后输入打开的端口号：

    
    
    SERVER_IP=0.0.0.0
    
    PORT=65000
    
    PORT_VIDEO=65005
    
     
    
    IMPORTANT: Do not change the 0.0.0.0.

打开BlackMamba目录，然后打开“keygen.py”文件。拷贝结果密钥并拷贝到“BlackMamba/bin/profile/crypt_key.py”文件中。

返回BlackMamba根目录，然后打开“main.py”文件：

### WINDOWS

    
    
    python main.py

### GNU/LINUX

    
    
    sudo chmod 777 main.py
    
    sudo python3.8 main.py
    
     
    
        KALI LINUX
    
        (sudo chmod 777 main.py)
    
    (sudo python3 main.py)

点击一个人形和加号的按钮，输入待创建Python文件的路径，输入端口号和主机的IP地址，然后点击“创建”按钮。

## 工具安装-客户端

创建好客户端脚本之后，你将需要在目标主机上运行该脚本。

### Windows

    
    
    python script.py

### GNU/Linux

下载代码包：

    
    
    scrot -y
    
    python3-pip -y
    
    python3-tk -y
    
    python3-dev -y

然后运行下列命令：

    
    
    sudo python3.8 script.py
    
     
    
    KALI LINUX
    
    (sudo python3 script.py)

注意事项：客户端脚本并不会实现持久化运行，如果你想实现持久化，你得需要自行动手实现。除此之外，客户端脚本可能会有几秒钟或几分钟的延迟，具体取决于通信连接的质量。

## 工具运行截图

![](https://image.3001.net/images/20210310/1615370515_60489913b231f01465caf.png!small)

![](https://image.3001.net/images/20210310/1615370526_6048991e20fa1c830e29a.png!small)

![](https://image.3001.net/images/20210310/1615370533_60489925822fc665c5483.png!small)

![](https://image.3001.net/images/20210310/1615370542_6048992e067b18e2a5fd9.png!small)

![](https://image.3001.net/images/20210310/1615370549_604899357a4b649a430b0.png!small)

![](https://image.3001.net/images/20210310/1615370557_6048993d272020ece42e5.png!small)

## 项目地址

BlackMamba：【[ _GitHub传送门_](https://github.com/loseys/BlackMamba)】

