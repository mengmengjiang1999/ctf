**在大学的时候看到某安全大会的时候，YQ大佬演示了汽车电子钥匙重放，然后成功搞定了汽车锁。我就想汽车的电子钥匙可以重放，电动车的肯定更容易，只要重复造轮子就能偷尽学校的电动车，迎娶漂亮学姐，走向人生巅峰。**

(因为是大学做的也没留存图片和数据，只能凭记忆写了，图片来源网络)

![](https://image.3001.net/images/20200515/1589507182_5ebdf46eade8f.png!small)

## 一、HackRF简介

HackRF是一个开源硬件工程，由Mike
Ossmann发起且被美国国防部高级研究计划局（DRAPA）赞助。由于这是一个开源项目，某些中国厂商现在也在生产和销售HackRF one。

## 二、特性

支持GNURadio

30MHz – 6GHz

与RTL2832U(RTLSDR)不同，HackRF可以进行发射

比USRP更廉价

已经在KickStarter上拿到投资

最大采样率: 20 Msps (10倍于电视棒RTLSDR)

接口: High Speed USB

USB供电

硬件/软件全部开源

获得了DARPA的Cyber Fast Track项目的支持

## 三、安装

来源：<https://www.hackrf.net/2013/12/linux>系统上搭建hackrf环境

2016年12月更新: 现在推荐使用TUNA镜像提供的PyBOMBS来安装GNURadio。

注意:不要使用软件源里的GNURadio，因为软件源里的GNURadio太久没有重新打包。

### 方法一:Ubuntu 14.04版本上搭建环境方法

此种环境搭建的方法，用的是已经经过编译的程序，因而不用翻墙，并且速度较快。

首先需要安装Ubuntu 14.04，之后你只需要在Ubuntu 14.04下，输入以下命令即可：

    
    
    sudo add-apt-repository ppa:gqrx/releases  
    sudo apt-get update  
    sudo apt-get upgrade  
    sudo apt-get install gqrx gnuradio gr-osmosdr hackrf

如果安装时出现 ‘Held packages’ 类型的报错，那么应该是由于之前已经进行过安装，这时，输入以下命令即可：

    
    
    sudo apt-get dist-upgrade

### 方法二: 手动编译

由于build-gnuradio脚本经常受到不可抗力的影响，导致安装失败。于是需要我们进行手动编译。

手动编译的顺序是

> 1、安装各种依赖包
>
> 2、gnuradio
>
> 3、hackrf / rtlsdr
>
> 4、gr-osmosdr

安装依赖包

    
    
    sudo apt-get -y install build-essential cmake git-core autoconf automake  libtool g++ python-dev swig pkg-config libfftw3-dev libboost1.53-all-dev libcppunit-dev libgsl0-dev libusb-dev sdcc libsdl1.2-dev python-wxgtk2.8 python-numpy python-cheetah python-lxml doxygen python-qt4 python-qwt5-qt4 libxi-dev libqt4-opengl-dev libqwt5-qt4-dev libfontconfig1-dev libxrender-dev libusb-1.0

编译GNURadio  

    
    
    git clone --progress http://gnuradio.org/git/gnuradio.git  
    cd gnuradio  
    mkdir build  
    cd build  
    cmake ../  
    make -j4 #4代表用4核编译  
    sudo make install  
    sudo ldconfig

编译hackrf

    
    
    git clone --progress http://github.com/mossmann/hackrf.git  
    cd hackrf/host  
    mkdir build  
    cd build  
    cmake ../ -DINSTALL_UDEV_RULES=ON  
    make  
    sudo make install  
    sudo ldconfig

编译rtlsdr(可选)

    
    
    git clone --progress git://git.osmocom.org/rtl-sdr  
    cd rtl-sdr  
    mkdir build  
    cd build  
    cmake ../ -DINSTALL_UDEV_RULES=ON -DDETACH_KERNEL_DRIVER=ON  
    sudo make install  
    sudo ldconfig

编译gr-osmosdr

    
    
    git clone --progress git://git.osmocom.org/gr-osmosdr  
    cd gr-osmocom  
    mkdir build  
    cd build  
    cmake ../  
    make  
    sudo make install  
    sudo ldconfig

编译gqrx(可选)

    
    
    git clone https://github.com/csete/gqrx.git  
    cd gqrx  
    mkdir build  
    cd build  
    qmake ../gqrx.pro  
    make  
    sudo make install  
    sudo ldconfig

编译完成后

你可以尝试以下命令

> osmocom_fft : 一个简单的HackRF频谱仪
>
> osmocom_siggen : 一个简单的HackRF信号源
>
> gqrx: 类似于SDR#的广播接收器

## 四、实验开始

为了便于携带本次实验采用树莓派+HackRF One

流程也很简单：查找频率→录制开锁→重放开锁

### 4.1osmocom_fft查找频率

先在网上搜了一下频率范围，大致为315,330,443。所以先看这几个频率附近

![](https://image.3001.net/images/20200515/1589507575_5ebdf5f771447.png!small)

如上图所示频峰在433.7左右。初步判断频率应该为433，网上说的没错，0.7只是附近的干扰叠加。但是录制的时候还是选择433.7。

### 4.2信号录制和重放

打开gnuradio增加录制模块。添加信号录制模块。（依葫芦画瓢，其实我也不是太懂所有的模块）

![](https://image.3001.net/images/20200515/1589507583_5ebdf5ffe940e.png!small)

这张图是剽窃某老哥的，当时我做绝壁没有这么多模块。我当时只设置了433.7MHZ。

> 原文地址：<https://www.jianshu.com/p/ea856d5cb575>

这是那位老哥的分析：

上次我们使用的 WX 模式，这次使用的是 QT 模式。

所以有些模块的名字会不一样。

> osmocom source：还是不变，只是我们设置其频率为433.7MHz
>
> low pass filter：低通滤波器，参数为保留过滤掉400KHz以上频率(相对于samp rate而言)。

其他模块：(输出模块)

> QT Frequency Sink:类似于 wx模式中的 FFT模块。(频域)
>
> QT Time Sink：类似于 wx模式中 Scope 模块。(时域)
>
> File Sink：将内容输出到文件中，不要忘记点开设置文件的路径。(二进制模式，无法直接打开）

![](https://image.3001.net/images/20200515/1589507731_5ebdf693ed3de.png!small)

保存为文件重放就行了。

## 五、坑点

虽然重放成功能打开电子锁，但是当时我实验我蹲学校食堂门外来一辆抓一辆，人多不仅存在信号干扰，录制距离也是需要注意的，最坑的是，电子钥匙解锁后锁了车头锁的一点办法都没，没锁车头锁的也仅仅百分之30能够直接开走。总结下坑点：

> 距离不能太远
>
> 信号干扰严重
>
> 锁车头锁不能成功
>
> 加了物理锁的也是扑街
>
> 没锁车头锁和物理锁的即使电子钥匙解锁，能直接启动的只占百分之30.

迎娶漂亮学姐，走上人生巅峰的计划就此搁浅。

![](https://image.3001.net/images/20200515/1589507802_5ebdf6da130c9.jpg!small)

 ***本文作者：꧁，转载请注明来自FreeBuf.COM**

