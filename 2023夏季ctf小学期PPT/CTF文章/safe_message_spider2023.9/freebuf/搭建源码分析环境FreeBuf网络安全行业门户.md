在日常的工作中，很多场景都需要分析人员编译Android系统源码，例如：

  * 动态调试Android系统源码

  * 将最新的Android官方系统源码刷入自己的Android设备

  * 定制Android系统，大早专属的脱壳工具

  * 编译Android内核并刷机，以绕过反调试Android官方支持在linux中编译系统源码。Docker的研发与使用，让Windows平台的用户也能不安装虚拟机而顺利地在Windows中编译Android系统源码。目前，在Windows和linux这两大系统平台上，都能够正常编译Android源码和刷机。

## 一、在Ubuntu中编译Android源码

Ubuntu是Android官方默认支持的Android系统源码编译系统，按照官方网站的环境配置说明进行配置后，就可以进行编译了。首先是安装JDK。编译不同版本的Android源码，就需要安装不同版本的JDK。这一点我们前面也讲过很多次，此处就不再赘述。然后，执行如下命令，安装下载和编译Android源码时需要使用的软件。

    
    
    sudo apt-get install git-core gnupg flex bison gperf build-essential

![1596608333895-25ffb8e3-b87f-40c2-a4bc-e7e197c8242f.png](https://image.3001.net/images/20200820/1597901735.png!small)sudo
apt-get install zip curl zlib1g-dev gcc-multilib g++-multilib
libc6-dev-i386![1596608333931-5a8a8cec-ba13-43c6-8dd3-896013838272.png](https://image.3001.net/images/20200820/1597902167.png!small)sudo
apt-get install lib32ncurses5-dev x11proto-core-dev libx11-dev lib32z-dev
ccache
![1596608333973-15ba7552-a331-49b4-923d-e8f3d2af8386.png](https://image.3001.net/images/20200820/1597902167.png!small)sudo
apt-get install libgl1-mesa-dev libxml2-utils xsltproc
unzip![1596608334008-32d1926e-617e-4130-8e61-5b130eb69aec.png](https://image.3001.net/images/20200820/1597902168.png!small)安装完成后，执行以下命令，下载repo，并配置Git用户名

    
    
    curl https://storage.googleapis.com/git-repo-downloads/repo > usr/bin/repo

![1596608334046-19b585d6-4f86-4389-9212-5a9385d561bb.png](https://image.3001.net/images/20200820/1597902169.png!small)chmod
a+x usr/bin/repo

    
    
    git config --global user.name "your name"  
    git config --global user.email "you@example.com"

接下来执行以下命令，下载和同步源码。

    
    
    repo init -u https://android.googlesource.com/platform/mainfest -b android-7.1.1_r1

![1596608334079-1c401787-e865-45dc-9fb4-bcd845026b1f.png](https://image.3001.net/images/20200820/1597902169.png!small)

    
    
    repo sync --force-sync --force-broken

![1596608334124-ba15de6b-2690-482c-b0b5-f1ed98ee0b0d.png](https://image.3001.net/images/20200820/1597902170.png!small)源码下载完成后，执行如下命令，就可以进行编译了。

    
    
    export USE_CCACHE=1  
    export CCACHE_DIR=ccache  
    prebuilts/misc/linux-x86/ccache/ccache -M 50G  
    source build/envsetup.sh  
    lunch aosp_angler-userdebug  
    make clobber  
    make -j8

## 二、在Windows中编译Android源码

Docker支持的最低Windows版本是Windows7。该版本需要借助Docker
Toolbox在VirtualBox虚拟机汇总的容器进行通信，效率相对较低。由于Windows
10原生系统支持Docker，则我们用Windows10来编译Android系统源码。

Docker 有专门的 Win10 专业版系统的安装包，需要开启Hyper-V。通过控制面板-程序-程序和功能，找到启用或关闭Windows功能，选中Hyper-V![1596608334156-9c11d736-590a-4ca2-a404-b28ed30c9ed0.png](https://image.3001.net/images/20200820/1597902170.png!small)访问Docker官方网站（<https://www.docker.com>)下载Windows版本的Docker
ToolBox。其稳定版本的下载地址为：<https://download.docker.com/win/stable/DockerToolbox.exe>.
双击下载的安装文件，在Windows中安装Docker
ToolBox。![1596608334196-ee167c36-be69-4dfc-9f6d-82b7f6a455ef.png](https://image.3001.net/images/20200820/1597902171.png!small)安装后，桌面上会出现Docker和Kitematic等软件的图标。![1596608334237-ff24bcc0-57c5-4dff-97e8-f0b62989b7fc.png](https://image.3001.net/images/20200820/1597902171.png!small)启动Kitematic(Alpha),会打开Docker
Hub页面，在这里可以下载Docker官方及第三方的Docker镜像。在Kitematic(Alpha)的主界面中搜索“aosp”,查找编译Android源码系统的环境，会列出所有的搜索结果，如下图所示：![1596608334270-6899a506-38be-468a-987a-195e9a1358f7.png](https://image.3001.net/images/20200820/1597902172.png!small)下载第一个aosp镜像，用它来编译Android4.4源码。单击该镜像下方的三个小圆点按钮，选择4.4版本，然后返回。单击“CREATE”按钮，开始下载镜像，如下图所示。![1596608334304-8ad3db74-7e3b-4915-8ae3-6d3504415f58.png](https://image.3001.net/images/20200820/1597902173.png!small)下载完成后，选中aosp镜像，单击界面右上方的setting按钮，选中volumes一栏，修改Android4.4.4_r1源码的位置及ccache的缓存位置，如下如图所示。配置完成后，单击“RESTART”按钮重启镜像，然后单击“EXEC”按钮打开shell环境。此时，aosp镜像已经帮我们设置了编译参数和环境变量，我们可以直接编译Android源码了。当然，我们也可以手动设置环境变量。![1596608334375-9cb0fae1-01ef-4e98-87cb-635a2a2818ba.png](https://image.3001.net/images/20200820/1597902174.png!small)操作完成后，执行make
-j4命令，开始进行编译，如下如所示。

![](https://image.3001.net/images/20200930/1601442606_5f74132e1d9c09f6f957f.png!small)备注：在shell环境下输入make
-j4 报make: * No targets specified and no makefile found. Stop.的错误.解决方法：

    
    
    wget http://ftp.gnu.org/pub/gnu/ncurses/ncurses-5.6.tar.gz  
    tar zxvf ncurses-5.6.tar.gz  
    cd ncurses-5.6/  
    ./configure -prefix=/usr/local -with-shared-without-debug  
    make  
    make install

