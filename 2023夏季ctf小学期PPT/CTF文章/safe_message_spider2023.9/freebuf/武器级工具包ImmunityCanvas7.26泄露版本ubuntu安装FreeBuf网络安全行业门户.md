Immunity CANVAS是Immunity公司的一款商业级漏洞利用和渗透测试工具，包含了480多个以上的漏洞利用，该工具并不开源，其中文版介绍如下：

“Canvas是ImmunitySec出品的一款安全漏洞检测工具。它包含几百个以上的漏洞利用。对于渗透测试人员来说，Canvas是比较专业的安全漏洞利用工具。Canvas
也常被用于对IDS和IPS的检测能力的测试。Canvas目前已经使用超过700个的漏洞利用，在兼容性设计也比较好，可以使用其它团队研发的漏洞利用工具，例如使用Gleg,
Ltd’s VulnDisco 、 the Argeniss Ultimate0day 漏洞利用包。”

## 泄露事件

2021年03月02日，Twitter上一位安全研究员披露了Immunity CANVAS 7.26工具源码包泄露事件

![img](https://image.3001.net/images/20210307/1615099047_604474a7c7d66660dffb4.jpg!small)

经过评估，本次泄露事件是该工具的完整源码，可在Windows及Linux平台直接安装使用

源码随后在网络上大量传播

## 泄露代码目录

![image-20210305141828622](https://image.3001.net/images/20210307/1615099048_604474a83f9400fd28527.jpg!small)

根据目录名我们可以大致推断其用途，如backdoors存放后门文件，exploits存放漏洞攻击组件等

## 安装

工具包提供了Windows与Linux安装方式 ,处于安全考虑,我将此工具包安装在虚拟机上的kali中,工具包提供了Linux的安装与使用方式:

    
    
    Pre Requests for installing Canvas: (tested setup) Ubuntu 18.04 (updated but not upgraded)
    Copy Canvas.zip to Linux PC
    Unzip it to working folder.
    
    Run command as root:
    sudo apt-get update
    sudo apt-get -y install python-pip
    sudo apt-get -y install gtk2.0
    sudo apt-get -y install python-glade2
    sudo apt-get -y install python-nacl python-bcrypt
    sudo pip install pycrypto
    sudo pip install pyasn1
    sudo pip install diskcache==4.1.0
    sudo pip install asn1tools
    sudo apt-get install -y python-pycurl
    sudo apt-get install -y libcanberra-gtk-module
    sudo pip install pycurl
    sudo pip install requests
    sudo pip install pygame
    
    Go to CANVAS folder, then run:
    sudo bash CANVAS/installer/linux_installer.sh
    
    Setup is finished
    Executing: 
    sudo python CANVAS/runcanvas.py
    
    You are breathtaking!
    
    

依次安装依赖:

    
    
    sudo apt-get update
    sudo apt-get -y install python-pip
    sudo apt-get -y install gtk2.0
    sudo apt-get -y install python-glade2
    sudo apt-get -y install python-nacl python-bcrypt
    sudo pip install pycrypto
    sudo pip install pyasn1
    sudo pip install diskcache==4.1.0
    sudo pip install asn1tools
    sudo apt-get install -y python-pycurl
    sudo apt-get install -y libcanberra-gtk-module
    sudo pip install pycurl
    sudo pip install requests
    sudo pip install pygame
    

然后cd进源码目录运行`installer/linux_installer.sh`

    
    
    sudo bash CANVAS/installer/linux_installer.sh
    

安装完成

#### 安装时的几个坑

一个是pygame要安装1.9系列版本的,但是安装说明中并未指定版本,如果使用2.x最新版本将无法启动并报错

解决方案:

    
    
    sudo pip uninstall pygame
    sudo pip install pygame==1.9.6
    

再者`linux_installer.sh`中有好多资源是国外的非常慢

在`linux_installer.sh`的第185行上:

    
    
    URLs=(["https://download.gnome.org/sources/pygtk/2.24/pygtk-2.24.0.tar.bz2"]="cd1c1ea265bd63ff669e92a2d3c2a88eb26bcd9e5363e0f82c896e649f206912"
              ["https://ftp.gnome.org/pub/GNOME/sources/pygobject/2.28/pygobject-2.28.7.tar.xz"]="bb9d25a3442ca7511385a7c01b057492095c263784ef31231ffe589d83a96a5a"
              ["https://cairographics.org/releases/py2cairo-1.10.0.tar.bz2"]="d30439f06c2ec1a39e27464c6c828b6eface3b22ee17b2de05dc409e429a7431"
              ["http://archive.ubuntu.com/ubuntu/pool/universe/v/vte/vte_0.28.2.orig.tar.xz"]="86cf0b81aa023fa93ed415653d51c96767f20b2d7334c893caba71e42654b0ae"
              ["http://archive.ubuntu.com/ubuntu/pool/universe/v/vte/vte_0.28.2-5ubuntu4.debian.tar.xz"]="f50ead3db07cf55a6ecd7ecd732aa5404d980b8acc20bba5d2303417f74e41ce"
              ["https://ftp.gnome.org/pub/GNOME/sources/libglade/2.6/libglade-2.6.4.tar.bz2"]="64361e7647839d36ed8336d992fd210d3e8139882269bed47dc4674980165dec"
             )
    
    

在下载时由于太慢会导致timeout从而致使整个脚本停止,可以先下到自己的服务器上,再替换其中的url,这样就不会导致脚本中断

## 运行

运行`sudo python runcanvas.py`开启

![image-20210307141251231](https://image.3001.net/images/20210307/1615099049_604474a96bce9c5c450e1.jpg!small)

下载链接:

> 复制这段内容后打开百度网盘App，操作更方便哦。  
> 链接：https://pan.baidu.com/s/1SC7kdjNsoMVB4tfl4txKBQ  
> 提取码：0iE2

压缩包解压密码 base64_decode("aGFja2VyMTk2MQ==")

