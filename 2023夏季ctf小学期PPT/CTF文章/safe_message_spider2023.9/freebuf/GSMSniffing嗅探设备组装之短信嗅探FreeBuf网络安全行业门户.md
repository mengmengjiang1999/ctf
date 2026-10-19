## *注：本文章只能用来测试，请勿用于非法用途。违者必究，且行且珍惜。  

## 0x0 前言

**嗅探装置价格低廉，很容易买到，一般几百块钱就可以配一套。一般使用摩托罗拉C118手机主板、天线、串口模块改装成嗅探设备。现在虽然大家都用4G的LTE网络了但是还有大量的2G的GSM网络存在，现在的GSM网络主要是中国移动的用户，中国电信没有GSM网络，中国联通在清退GSM网络，中国移动先清退的是3G
的TD网络而不是2G的GSM网络。GSM网络有一个很大的缺陷就是有很多的伪基站存在，在说伪基站之前先说我们相互之间通信的过程。我们打电话/发短信的过程是，手机信号是连接到离你最近的基站（BTS）然后进入RNC，MSC进行核心网的交换，再发给离对方最近的基站最后传到对方的手机中。如果这个时候你的手机接入的不是运营商的基站，那就危险了，这就相当于你进了“贼窝”了，这个不是运营商的基站就是伪基站。**

为什么我们的手机会进入假的基站呢？

这是因为GSM网络的鉴权存在缺陷。在GSM网络中手机接入网络要鉴权验证，简单说就是运营商验证你的手机是否是合法用户，如果是就可以通信了，但是手机不会验证接入的基站是不是运营商的正规基站，这样即便接入了伪基站用户也是不知道的，在3G、4G的网络中会有这样的鉴权验证，比GSM网络安全的多。
嗅探设备的组装换汤不换药，只是组了一个更大的设备出来，用来复现短信嗅探场景。

## 0x1 设备清单

1\. 摩托罗拉 C118手机 （6个改装过）

2\. 树莓派板

3\. USB拓展板 （6口的）

4\. USB 转串口 FT232rl (6个)

5\. 电源变压器一个

6\. 自定义电源中心控制器一个

7\. 天线 6根

8\. 承载用盒子一枚

9\. N个开关

10\. N个电阻和针脚

11\. 小号信号降频设备 （测试用）

12\. 6类网线或者其他类型的线。（串联设备用）

13\. 锡焊机器 (焊接设备用)

14\. 无线wifi路由器 (调试用)

## 0x2 设备安装

### 1\. 改装C118手机

C118手机是不可缺少的一部分，为什么要用6个设备呢？因为一台c118手机只能够监听也就是嗅探一个频点，所以按道理来说手机越多越好。来一个改装过全图，下图中是我做好的C118手机，仅供参考，实际情况看你自己需求。

![](https://image.3001.net/images/20190213/1550037614_5c63b26ece978.jpg!small)

先把C118手机外壳扒掉，准备 7根颜色不同的线，推荐6类网线，方便区分。接线方法请参照图中标识。

![](https://image.3001.net/images/20190213/1550037629_5c63b27dcd149.jpg!small)

![](https://image.3001.net/images/20190213/1550037706_5c63b2ca97996.jpg!small)

电源接口处接上针脚：

![4.jpg](https://image.3001.net/images/20190213/1550037661_5c63b29d5a836.jpg!small)

usb串口转接线 一定别接错了 否则无法开机无法刷机。。

![5.jpg](https://image.3001.net/images/20190213/1550037728_5c63b2e00db22.jpg!small)

![6.jpg](https://image.3001.net/images/20190213/1550037740_5c63b2ec70030.jpg!small)

因为天线接口我在网上找了半天也没有找到 用易拉罐做了一个相似的接头。可以参照我的发挥。 到此手机已经改装好了 按照上图 在做 5个出来

### 2\. 组装

 **2.1 供电**

![7.jpg](https://image.3001.net/images/20190213/1550037756_5c63b2fc991af.jpg!small)

由于我设备已经焊死 不好拆卸，只好以上图方式 分开说明。可以看到上图 电源集合供电处，有块开发板，这个板的作用是给所有
设备供电，如手机树莓派，usb集线器，等等，可以参照我的做，但是也可以自己重新设计。

 **2.2 树莓派和USB集线器**

![8.jpg](https://image.3001.net/images/20190213/1550037770_5c63b30ac7d0f.jpg!small)

接口太多 按照上图编号所示，

1\. USB集线器数据线接到树莓派USB口

2\. USB集线器电源接到供电开发板上

3\. USB集线器电源接口

4\. 树莓派供电口

5\. 树莓派接集线器USB接口

6\. 树莓派USB接的无线网卡

7\. 树莓派网口接的网线转接头

上图中 可以看到树莓派起到控制中心的作用，用来控制手机刷机嗅探等功能。至于USB集线器为什么要选择单独供电，是因为可能会导致电流不稳定，导致刷机失败。

 **2.3 电源开关控制器**

![9.jpg](https://image.3001.net/images/20190213/1550037785_5c63b319cf2c2.jpg!small)

上图是比较复杂的手工制作的电路控制器，用的c51可编程单片机。

下图是电路原理图，看电路图可能看的更佳清晰明了。

![10.jpg](https://image.3001.net/images/20190213/1550037800_5c63b3283a405.jpg!small)

C52单片机代码

    
    
    #include <reg52.h>
    
    void delay(unsigned int);
    sbit LED0 = P0^0;
    sbit LED1 = P0^1;
    sbit LED2 = P0^2;
    sbit LED3 = P0^3;
    sbit LED4 = P0^4;
    sbit LED5 = P0^5;
    sbit LED6 = P0^6;
    sbit LED7 = P0^7;
    sbit LED_0 = P1^0;
    sbit LED_1 = P1^1;
    sbit LED_2 = P1^2;
    sbit LED_3 = P1^3;
    sbit LED_4 = P1^4;
    sbit LED_5 = P1^5;
    sbit LED_6 = P1^6;
    sbit LED_7 = P1^7;   
    sbit STAU_A = P2^3;  
    sbit STAU_B = P2^2;
    sbit KEY = P2^1;
    
    void delay(unsigned int i){
        unsigned int j,k;
        while(i--){
            for(j = 0; j < 255; j++)
        for(k = 0; k < 240; k++);
        }
    }
    
    void main(){
        unsigned char i;
        while(1){   
            i=KEY;
        STAU_A=0;
            if(i==0){
                i=KEY;
                if(i==0)
          STAU_B = 0;
          LED0 = 0;
          LED1 = 0;
          LED2 = 0;
          LED3 = 0;
          LED4 = 0;
          LED5 = 0;
          LED6 = 0;
          LED7 = 0;
          LED_0 = 0;
          LED_1 = 0;
          LED_2 = 0;
          LED_3 = 0;
          LED_4 = 0;
          LED_5 = 0;
          LED_6 = 0;
          LED_7 = 0;
          delay(10);
          STAU_B=1;
          LED0 = 1;
          LED1 = 1;
          LED2 = 1;
          LED3 = 1;
          LED4 = 1;
          LED5 = 1;
          LED6 = 1;
          LED7 = 1;
            }else{
                i=KEY;
            }
        }
    }  
    

![11.jpg](https://image.3001.net/images/20190213/1550037822_5c63b33eb9c65.jpg!small)

完工,在实际操作中碰到很多坑，大部分配件都是自己纯手工制作，虽然GSM嗅探技术年代久远，没有新鲜技术，但是想要研究无线安全技术，这是必定经历的一关。

## 0x3 设备调试

### 1\. 树莓派调试

把树莓派口网线口插入到路由器lan口。获取到ip后直接ssh连接。如果没有提前配置好ip的话估计要采用串口的方式连接了，这里不细做解释，自行百度。下面演示没有什么新鲜的配置和技术。

![12.jpg](https://image.3001.net/images/20190213/1550037843_5c63b353917a3.jpg!small)

### 2\. 编译

工具:

    
    
    sudo apt-get install libtool shtool autoconf git-core pkg-config make gcc

gnuarm:

    
    
    32 bit wget <http://www.gnuarm.com/bu-2.16.1_gcc-4.0.2-c-c++_nl-1.14.0_gi-6.4_x86-64.tar.bz2> tar xf bu-2.16.1_gcc-4.0.2-c-c++_nl-1.14.0_gi-6.4_x86-64.tar.bz2 mv gnuarm-* ~/gnuarm export PATH=~/gnuarm/bin:$PATH

libosmocore:

    
    
    git clone git://git.osmocom.org/libosmocore.git cd libosmocore/ autoreconf -i
    
    ./configure
    
    make
    
    sudo make install
    
    cd ..
    
    ldconfig

具体编译过程可以参照网上的编译方法 也可以直接下载2进制文件.

> <https://github.com/K1two2/OsmocomBB_Raspberry-Pi_SMS_WEB_CODE>

### 3\. 确定当前手机接入基站

使用降频设备降频后查看苹果手机基站ARFCN值。

![13.jpg](https://image.3001.net/images/20190213/1550037886_5c63b37ef0606.jpg!small)![14.jpg](https://image.3001.net/images/20190213/1550037902_5c63b38ee150f.jpg!small)

手机在连入GSM基站时，我们可通过一些方式确定自己手机连入的是哪个基站、ARFCN是多少，安卓手机在2G状态时，可在键盘拨号界面输入：
*#*#4636#*#* 上面这个是安卓通用的如果你的手机没反应，还可以尝试：  

    
    
    Samsung (Android) : *#*#197328640#*#* or *#0011#
    iPhone (all) : *3001#12345#* 拨号
    HTC (Android) : *#*#7262626#*#*
      
    

进去以后能找到基站的MCC、MNC、ARFCN这些参数。  

    
    
    MCC 移动国家码
    
    MNC Mobile Network Code，移动网络码，共2位，中国联通GSM系统使用01，中国移动GSM系统使用02
    
    ARFCN 绝对无线频道编号（Absolute Radio Frequency Channel Number – ARFCN ），是在GSM无线系统中，用来鉴别特殊射频通道的编号方案。
    
    手机开机后，即搜索广播控制信道（BCCH）的载频。因为系统随时都向在小区中的各用户发送出用广播控制信息。手机收集到最强的（BCCH）对应的载频频率后，读取频率校正信道（FCCH），使手机（MS）的频率与之同步。所以每一个用户的手机在不同的位置（即不同的小区）的载频是固定的，它是由GSM网络运营商组网时确定，而不是由用户的GSM手机来决定。
    
    手机读取同步信道（SCH）的信息后找出基地站（BTS）的认别码，并同步到超高帧TDMA的帧号上。手机在处理呼叫前要读取系统的信息。如：领近小区的情况、现在所处小区的使用频率及小区是否可以使用移动系统的国家号码和网络号码等等，这些信息都以BCCH上得到。
    
    手机在请求接入信道（RACH）上发出接入请求的信息，向系统传送SIM卡帐号等信息。系统在鉴权合格后，通过允许接入信道（AGCH）使GSM手机接入信道上并分配给GSM手机一个独立专用控制信道（SDCCH）。手机在SDCCH上完成登记。在慢速随路控制信道（SACCH）上发出控制指令。然后手机返回空闲状态，并监听BCCH和CCCH公共控制信道上的信息。  
    

### 4\. 测试设备

短信嗅探其实可以分为三步曲 刷机>扫描>监听嗅探。

![15.jpg](https://image.3001.net/images/20190213/1550038091_5c63b44b02b8f.jpg!small)

切换到root模式下查看usb串口是否读取到。我这里有6个USB口，可以看到上图是正常能够读取到usb口。

刷机：

![16.jpg](https://image.3001.net/images/20190213/1550038108_5c63b45cbffc1.jpg!small)![17.jpg](https://image.3001.net/images/20190213/1550038122_5c63b46af36e9.jpg!small)

刷机成功，接下来扫描频段：  

![18.jpg](https://image.3001.net/images/20190213/1550038154_5c63b48a103ee.jpg!small)![19.jpg](https://image.3001.net/images/20190213/1550038180_5c63b4a40c610.jpg!small)

启动wireshark ：  

    
    
    sudo wireshark -k -i lo -f 'port 4729'

网卡一定要选择对，否则只能在本地抓包，-i 是指定网卡：

![20.jpg](https://image.3001.net/images/20190213/1550038198_5c63b4b6ebacc.jpg!small)

/root/c118bin/bin/layer23/misc/ccch_scan -i 你的外网地址 -a 频段：

![21.jpg](https://image.3001.net/images/20190213/1550038229_5c63b4d5a1d20.jpg!small)![22.jpg](https://image.3001.net/images/20190213/1550038267_5c63b4fb99765.jpg!small)

收到数据。

### 5\. 开车

这里使用<https://github.com/lxf94/GSM-Sniffer>
按照smshack要求填入响应的路径，这里一定要注意里面的路径是否正常，否则是无法测试成功的。git开源的这个还不错，能支持多个设备同时，不过也有弊端。到时候再改吧。

![23.jpg](https://image.3001.net/images/20190213/1550038292_5c63b51461dac.jpg!small)

## 0x4 结尾

GSM嗅探不算什么最新技术，但是是一个无线安全的必经之路，该文章单为记录操作过程，方便以后观看，设备也是花了不少时间才做完。

上文作为学习，各位大神就别喷我了。设备后期还需要更多更改和优化，后期有时间会出一个详细的改后的文章，比如通过web
一键启动手机软刷机等等，未完待续！！！by：凌天实验室

## 0x5 参考文献

> [https://github.com/K1two2/OsmocomBB_Raspberry-Pi_SMS_WEB_CODE
> ](https://github.com/K1two2/OsmocomBB_Raspberry-Pi_SMS_WEB_CODE)
>
> [https://github.com/lxf94/GSM-Sniffer ](https://github.com/lxf94/GSM-> Sniffer)
>
> [https://www.freebuf.com/geek/160171.html
> ](https://www.freebuf.com/geek/160171.html)
>
> [http://www.ver007.org ](http://www.ver007.org)
>
> <https://bbs.pediy.com/thread-182574.htm>

***本文作者：安百科技，转载请注明来自FreeBuf.COM**

