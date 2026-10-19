## 目标

车机上有一个10pin的类似jtag口，但是没有引脚标识，用Jtagulator把SWD引脚识别出来。

## 环境准备

### 硬件环境

  * Jtagulator硬件

  * 杜邦线若干

  * 万用表

  * mini5P数据线，用来把Jtagulator硬件连接到PC

### 软件环境

SecureCRT，串口的上位机

P8X32A-Setup-Propeller-Tool-v1.3.2.zip ，用来下载jtagulator固件

## 判断Jtagulator硬件是否完好

### Jtagulator指示灯

待机状态时，绿灯

G--W后， 红灯

在j识别时，灯会一闪一闪，红绿交替。

### 判断Jtagulator板子上的引脚是否正常

收到设备后，设备已经烧写好了固件，版本是1.1，首先需要判断Jtagulator板子上的引脚是否正常。首先在SecureCRT页面，我们将GPIO引脚都设置成高电压3.3V，如下设置

![v2-b318fdd50d2c4c438f665153a965ad3f_720w.png](https://image.3001.net/images/20221020/1666232545_6350b0e1615569d46a423.png!small)

出现了各引脚都是0V，如下图的情况，根据绿灯，板子是待机状态可以推测，本次的上位机指令，板子并没有收到，所以再重新试一次，第二次下发指令，板子灯变红了，万用表测23个引脚的电压均是3.3V。Jtagulator板子上的引脚没有问题，这个问题貌似是1.1版本固件的一个BUG。

![v2-2fdd7134871a718a76e309945d40e1e0_720w.png](https://image.3001.net/images/20221020/1666232546_6350b0e2791f55a60b0cc.png!small)

### ​判断jtag识别功能

手边有个stm32f103开发板，上面有两个跳帽，运行状态是boot0和boot1都接0，在烧写状态时，把boot0跳帽接到1上即可。本次测试用的是运行状态。

它的SWD引脚如图

![v2-355fc68a65973753bf59cc55e210ef78_720w.png](https://image.3001.net/images/20221020/1666232547_6350b0e3a9cd45f9a8d61.png!small)

​连接这6个引脚，用VAJD连接3V3给stm32供电，GND连接GND，其他四个脚连接到任意的Channel。当然也可以不连接3V3，用usb口给stm32供电。

![v2-b813af6aade1e6fd0bc060795457cb05_720w.png](https://image.3001.net/images/20221020/1666232548_6350b0e469ccff25276c7.png!small)

​识别结果如下，说明识别功能没有问题。

![v2-48b2c05ececc80774bef8acdd772fac9_720w.png](https://image.3001.net/images/20221020/1666232549_6350b0e54241a1dbda1d8.png!small)

## ​开始识别车机

我先把10个PIN都连接到了Jtagulator板子的任意channel上，GND连接的是车机的天线。发现我一执行，车机的电流就变成了800mA，车机屏幕黑掉一半，推测是10个PIN里有个VCC口，我把VCC设成0，影响了车机的供电。

所以，我用万用表做了一件大胆的事，来推测10个pin里，哪个是VCC。我把万用表设成连通性测试，黑笔接触车机天线，红笔分别接触10个pin1秒，发现接触第三个pin时，车机电流变小，推测pin3是VCC。

此时我改变连接方式，把pin3连接到VAJD，其余不变，结果如下

![v2-cafc43b4401e93bb20f8865978c096c8_720w.png](https://image.3001.net/images/20221020/1666232550_6350b0e679b35201f926c.png!small)

  

![v2-b2d704573aeaa5b69b78a6a5851a960a_720w.png](https://image.3001.net/images/20221020/1666232551_6350b0e7872dac7a69deb.png!small)

​我执行了两次，结果识别到了几组。

![v2-574c0e290b278f9c3a63c168022c68ec_720w.png](https://image.3001.net/images/20221020/1666232552_6350b0e8b502cc1d13b1e.png!small)

​

![v2-7c57d64a80efa731523a201edf1cdaf0_720w.png](https://image.3001.net/images/20221020/1666232553_6350b0e9895144d232ba6.png!small)

​

![v2-9b164dea7701d52212aa2321e4927209_720w.png](https://image.3001.net/images/20221020/1666232554_6350b0ea530b11676056c.png!small)

​

![v2-8cdf3355fb10d47a876a85e577d81d48_720w.png](https://image.3001.net/images/20221020/1666232555_6350b0eb544814d9c5b7c.png!small)

## 结论

先列出10个PIN对应的通道号。

Pin1----ch6

Pin2----ch0

Pin3----VAJD

Pin4----ch1

Pin5----ch2

Pin6----ch5

Pin7----ch7

Pin8----ch3

Pin9----ch4

Pin10----ch8

在做连通性测试时，pin1，4，5，7，8，10是和地连通的。

两次测试的结果如下：

第一次：

153

154（没有device ID）

140

102

第二次：

184（没有device ID）

154（没有device ID）

153

140

106

  

### 参考链接

<https://www.bilibili.com/read/cv13047230>

