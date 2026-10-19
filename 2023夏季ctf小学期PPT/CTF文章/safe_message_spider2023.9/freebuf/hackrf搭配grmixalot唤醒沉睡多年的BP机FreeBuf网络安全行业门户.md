## 0x00 前言

18年左右从微信群里看到水滴安全实验室唤醒寻呼机的一个测试视频，出于一些原因，一直没有机会复现。刚好在卧室里翻出当年从表舅那截获的一台寻呼机。

![1539192-20210317162245784-1015771518.png](https://image.3001.net/images/20210618/1624005693_60cc5c3d05ba6b744bad3.png!small)

>
> 在2006年，中国最后一家寻呼运营商停止了寻呼服务，BP机寻呼台的信号也随之消失，老百姓手中的BP机也随之成了收藏品。寻呼服务到底是怎样的呢？呼号、地址码、工作频率都是什么？

根据查询资料得知，当年买了寻呼机之后是不能直接使用的，需要到当地运营商那里对寻呼机进行写码（这里是地址码）和改频（BP机的工作频率），改好之后可能会对BP机进行加密，加密之后的BP机如果没有解密，是不能再次进行写码操作的（读取也不可以）。完了之后呢，运营商会给这个BP机分配一个呼号（相当于现在的手机号码），一个呼号对应一个地址码和工作频率。然后BP机就可以装上电池拿回家使用了。

当有人拨通你的呼号时，运营商会将此呼号对应的地址码和工作频率找出，然后将地址码和需要发送的信息一起进行`POCSAG`编码，最后通过寻呼台的无线电发送设备（调制模式为NFM，无线电的频率要和BP机的工作频率一致）将数据发送出去。BP机接收到寻呼台发送过来的信号，就会响起来和显示信息了。

现在寻呼运营商早就没有了，因此通过呼号来呼响BP机肯定是行不通的，只能通过地址码和工作频率来呼响你的BP机。

 **唤醒寻呼机的方式多种多样：可以通过某宝售卖的寻呼机发射台，也可以使用hackrf
one+portpack中的pocsag发射模块。由于笔者手中只有一个hackrf one，所以这里使用github上的gr-mixalot项目来唤醒寻呼机。**

这里，需要明确如下信息：

> 确定型号：摩托罗拉顾问型汉字寻呼机（俗称大汉显或者大顾问）
>
> 工作编码：POCSAG
>
> 波特率：？
>
> 地址码：？
>
> 工作频率：？

## 0x01拆机获取晶振频率

拆开之后将频率板取出（一般BP机内部会有两个电路板，比较小的有天线的那个电路板是频率板。）

![](https://image.3001.net/images/20210618/1624005900_60cc5d0cd3f947cd58cc1.jpg!small)

![](https://image.3001.net/images/20210618/1624005956_60cc5d4481591a93f0308.jpg!small)

![](https://image.3001.net/images/20210618/1624005992_60cc5d68f3a548d03665a.png!small)

计算工作频率只需要用到这两个晶振频率，计算结果为：

工作频率=44.208KHz*3+17.9MHz=150.524MHz

## 0x02 用读码设备读取波特率和地址码：

![](https://image.3001.net/images/20210618/1624006130_60cc5df2f1cd559894d3c.jpg!small)

![](https://image.3001.net/images/20210618/1624006181_60cc5e2552ad64ea555ff.jpg!small)

由上图可以看到波特率为1200，地址码为1964281。

汇总一下得到的信息

 **确定型号：摩托罗拉顾问型汉字寻呼机（俗称大汉显或者大顾问）**

> 工作编码：POCSAG
>
> 波特率：1200
>
> 地址码：1964281
>
> 工作频率：150.524MHz

##  **0x03 软件环境搭建**

由于使用ubuntu编译gr-mixalot时经常报错，这里使用 dargon-os进行编译。

编译运行gr-mixalot

    
    
    $sudo git clone https://github.com/unsynchronized/gr-mixalot.git
    $cd gr-mixalot
    $sudo mkdir build 
    $cd build/
    $sudo cmake ..
    $sudo make install
    $sudo ldconfig
    $cd ..
    $cd /examples
    $gnuradio_companion pocsagtx_hackrf.grc

## 0x03 配置gr-mixalot 参数

![](https://image.3001.net/images/20210618/1624006254_60cc5e6ee64f8d2f7c983.png!small)

## 0x04 发送汉字编码

![](https://image.3001.net/images/20210618/1624006273_60cc5e8153838360f2588.png!small)

## 0x05 演示

[https://www.bilibili.com/video/BV1n64y1r78G?from=search&seid=3053408081578742006](https://www.bilibili.com/video/BV1n64y1r78G?from=search&seid=3053408081578742006)

## 0x06 参考：

[https://www.bilibili.com/video/BV194411y71Z?from=search&seid=7727686611103159348](https://www.bilibili.com/video/BV194411y71Z?from=search&seid=7727686611103159348)

<https://www.bilibili.com/video/BV1sE411G7W9/?spm_id_from=333.788.recommend_more_video.-1>

<https://359303267.github.io/Get-BP-Code/>

[https://www.you*tube.com/channel/UC9U2kaqhE716J2WNSTcOghg/featured](https://www.youtube.com/channel/UC9U2kaqhE716J2WNSTcOghg/featured)

[https://www.you*tube.com/watch?v=nzzIvZFrDNw](https://www.youtube.com/watch?v=nzzIvZFrDNw)

[https://www.you*tube.com/watch?v=nzzIvZFrDNw&ab_channel=HackedExistence](https://www.youtube.com/watch?v=nzzIvZFrDNw&ab_channel=HackedExistence)

<https://github.com/unsynchronized/gr-mixalot>

