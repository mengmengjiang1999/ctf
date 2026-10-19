最近研究下pineapple 大菠萝，看了下原版设备还挺贵，手上有现成cpu的板子，就想试试看能正常使用么。顺便把遇到的坑记录下。

## 官方硬件说明

WiFi Pineapple NANO

### Specifications

  * CPU: 400 MHz MIPS Atheros AR9331 SoC
  * Memory: 64 MB DDR2 RAM
  * Disk: 16 MB ROM + Micro SD (not included. up to 200GB)
  * Wireless: Atheros AR9331 (wlan0) + Atheros AR9271 (wlan1), both IEEE 802.11 b/g/n
  * Ports: (2) RP-SMA Antenna, Ethernet over USB (ASIX AX88772A)
  * USB 2.0 Host, Micro SD card reader
  * Power: USB 5V 1.5A. Includes USB Y-Cable
  * Configurable Status Indicator LED
  * Configurable Reset Button

看配置nano版本就是很常见的过时路由器，像tp-link的703N这种改下ram和rom应该就能直接用。

## 固件下载与刷新

### 官方固件下载地址

<https://www.wifipineapple.com/downloads>

### 刷机方式

通过web界面一般都刷机不成功，提示板型不匹配

直接把固件上传到路由器/tmp目录 通过命令刷新，-F是不验证板型强制刷新。推荐大家加上-n不保存配置。![命令更新](https://image.3001.net/images/20211013/1634113372_6166975cde5eb5737d6f6.png!small)成功后通过http://172.16.42.1:1471/进行配置![配置界面](https://image.3001.net/images/20211013/1634113847_61669937846dbccc84347.png!small)

## 遇到的坑

这里的坑主要还是在配置与激活的地方，如果用第三方板子，运气好的话按键的配置正好与官方板子一样，可以顺利激活。这里我遇到的是不一样的。![](https://image.3001.net/images/20211013/1634113990_616699c601bbff40ebf88.png!small)

这里因为安全配置需要按下板子上的rest键才能继续。

### 能软件解决绝对不动硬件（失败）

首先想到的是web程序嘛，绕过就好了哈哈。

打开浏览器的调试功能看到有这个请求![](https://image.3001.net/images/20211013/1634114204_61669a9c098e0f310c611.png!small)

那就burpsuit试试。![](https://image.3001.net/images/20211013/1634114289_61669af159eb7147d7453.png!small)

对请求的返回进行拦截![](https://image.3001.net/images/20211013/1634114321_61669b1148e7c55fe8355.png!small)修改返回值，看起来能进入到下一步![](https://image.3001.net/images/20211013/1634114361_61669b392510fece62d11.png!small)配置完成后点击提交，啪~快来没了。![](https://image.3001.net/images/20211013/1634114424_61669b7883302d2dcff8b.png!small)

## 失败原因分析

估计还有其他校验，既然有固件，那就分析一把。打开binwalk
对固件进行解压。![](https://image.3001.net/images/20211013/1634114769_61669cd1acf3ad3f72ba1.png!small)![](https://image.3001.net/images/20211013/1634114818_61669d02a666e2ccc46e6.png!small)比较显眼的目录![](https://image.3001.net/images/20211013/1634114841_61669d19b2d6cecd30cac.png!small)管理界面就在这里了。看了下是php的界面。

根据界面错误提示定位到代码的位置如下：![](https://image.3001.net/images/20211013/1634115068_61669dfc7162182d757d3.png!small)

这里有个检测函数![](https://image.3001.net/images/20211013/1634115077_61669e0507352e9c72dfd.png!small)直接检测文件是否存在，由于ssh密码是配置后才生成，不能通过ssh去touch个文件。看了写系统按键监听文件如下：![](https://image.3001.net/images/20211013/1634115175_61669e67ad05b2a1a9103.png!small)看来只能走硬件解决了。

## 硬件解决

硬件解决其实就是补上按键问题。

查看了下按键的gpio口定义![](https://image.3001.net/images/20211013/1634115343_61669f0f1e2f1fd501b60.png!small)![](https://image.3001.net/images/20211013/1634115356_61669f1c8bacd096f0475.png!small)这里可以看到，按键定义在gpio12

查看ar9331的datasheet![](https://image.3001.net/images/20211013/1634115395_61669f43bc2af078f2308.png!small)可以看到gpio在A56
这个引脚上。

对比电路板找到对应位置![](https://image.3001.net/images/20211013/1634115541_61669fd5db7dad46a83c5.png!small)看到muc引脚出来接了个电阻，只需要把这个电阻箭头的引脚用杜邦线接地就能触发对应的按键。![](https://image.3001.net/images/20211013/1634115822_6166a0ee54cfb25794e02.png!small)顺利完成

![](https://image.3001.net/images/20211013/1634115838_6166a0feb57f1ff4add34.png!small)登陆后测试功能![](https://image.3001.net/images/20211013/1634115862_6166a11638954bc2615ba.png!small)

使用方法看官方wiki吧：https://wiki.wifipineapple.com/#!index.md

