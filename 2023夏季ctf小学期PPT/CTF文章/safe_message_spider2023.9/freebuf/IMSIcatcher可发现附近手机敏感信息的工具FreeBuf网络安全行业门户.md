**严正声明：该工具主要是为了让大家更好的了解GSM网络的工作原理而设计开发的，请不要用于恶意目的！**

## 前言

 **IMSI-catcher是一个可以帮助你发现附近手机的IMSI号码，国家，品牌和运营商等信息的工具。**

![IMSI-catcher](https://image.3001.net/images/20181121/1542757231_5bf49b6faee4b.png!small)

## 你需要准备的设备

> 一台PC电脑

> 1个带有天线的[USB DVB-T key（RTL2832U）](https://osmocom.org/projects/sdr/wiki/rtl-> sdr)（大概在15美元以内），或是一部[OsmocomBB手机](https://osmocom.org/projects/baseband/wiki/Phones)一个[HackRF](https://greatscottgadgets.com/hackrf/)设备。

## 设置

    
    
    git clone https://github.com/Oros42/IMSI-catcher.git
    # or wget https://github.com/Oros42/IMSI-catcher/archive/master.zip && unzip -q master.zip
    
    sudo apt install python-numpy python-scipy python-scapy

对于Debian Testing (10) 和 Ubuntu 18.04+ gr-gsm
的安装，请参阅：<https://osmocom.org/projects/gr-gsm/wiki/Installation>

对于老版本的Debian 和 Ubuntu的安装命令如下 :

    
    
    sudo add-apt-repository -y ppa:ptrkrysik/gr-gsm
    sudo apt update
    sudo apt install gr-gsm

如果gr-gsm设置失败，请参照：<https://github.com/ptrkrysik/gr-gsm/wiki/Installation> 进行设置。

Debian：<https://tracker.debian.org/pkg/gr-gsm>

## 运行

### 使用旧版本的gr-gsm

打开2个终端。

在终端1中输入：

    
    
    sudo python simple_IMSI-catcher.py --sniff

你可以添加-h参数显示可用选项。

在终端2中，搜索频率：

    
    
    grgsm_scanner

使用grgsm_livemon命令嗅探你搜索到的频率：

    
    
    grgsm_livemon -f <your_frequency>M

例如：

    
    
    grgsm_livemon -f 938.2M

运行后应该会产生类似以下输出：

    
    
    15 06 21 00 01 f0 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b
    25 06 21 00 05 f4 f8 68 03 26 23 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b
    49 06 1b 95 cc 02 f8 02 01 9c c8 03 1e 57 a5 01 79 00 00 1c 13 2b 2b
    ...

你可以根据需求更换不同的频率。

### gr-gsm >= 0.41.2-1

同样，打开2个终端。

在终端1中输入：

    
    
    python simple_IMSI-catcher.py

你可以添加-h参数显示可用选项。

在终端2中输入：

    
    
    python scan-and-livemon

这个过程可能需要几分钟的时间。因为，它需要运行grgsm_scanner来查找附近的基站，并请求grgsm_livemon_headless接收信号。

或是先找到附近基站的频率。

    
    
    grgsm_scanner

接着，使用grgsm_livemon命令嗅探你搜索到的频率：

    
    
    grgsm_livemon -f <your_frequency>M

例如：

    
    
    grgsm_livemon -f 938.2M

运行后应该会产生类似以下输出：

    
    
    15 06 21 00 01 f0 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b
    25 06 21 00 05 f4 f8 68 03 26 23 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b
    49 06 1b 95 cc 02 f8 02 01 9c c8 03 1e 57 a5 01 79 00 00 1c 13 2b 2b
    ...

你可以根据需求更换不同的频率。

完成以上操作后，下面我们要做的就是等待结果。大概一分钟左右的时间，我们就能够在终端1中看到IMSI号码。如果一分钟后没有出现任何内容，那么请更改你的频率。

> 相关文档：<https://fr.wikipedia.org/wiki/Global_System_for_Mobile_Communications>

例如法国的频率为：9.288e+08 Bouygues

查看捕获到的数据包：

    
    
    sudo wireshark -k -Y '!icmp && gsmtap' -i lo

## 可选项

获取有关信号塔的信息：

    
    
    sudo python find_cell_id.py

获取Immediate Assignment信令：

    
    
    sudo python immediate_assignment_catcher.py

## 查找频率

除了可以使用上面提到的grgsm_scanner来查找频率，你也可以使用像kalibrate-hackrf这样的工具来查找：

    
    
    sudo apt-get install automake autoconf libhackrf-dev
    git clone https://github.com/scateu/kalibrate-hackrf
    cd kalibrate-hackrf/
    ./bootstrap
    ./configure
    make
    sudo make install

## 运行

    
    
    kal -s GSM900
    
    
    kal: Scanning for GSM-900 base stations.
    GSM-900:
      chan:   14 (937.8MHz + 10.449kHz)	power: 3327428.82
      chan:   15 (938.0MHz + 4.662kHz)	power: 3190712.41

## 参考资料：

> Gr-Gsm 设置：<https://github.com/ptrkrysik/gr-gsm/wiki/Installation>
>
>
> 频率：<http://www.worldtimezone.com/gsm.html>（<https://fr.wikipedia.org/wiki/Global_System_for_Mobile_Communications>）
>
> MNC：<https://en.wikipedia.org/wiki/Mobile_Network_Code>
>
> Scapy：<http://secdev.org/projects/scapy/doc/usage.html>
>
> IMSI：<https://fr.wikipedia.org/wiki/IMSI>
>
> Realtek RTL2832U：<https://osmocom.org/projects/sdr/wiki/rtl-> sdr>（<http://doc.ubuntu-fr.org/rtl2832u>）<http://doc.ubuntu-fr.org/rtl-sdr>

 ***参考来源：[GitHub](https://github.com/Oros42/IMSI-catcher)，FB小编secist编译，转载请注明来自FreeBuf.COM**

