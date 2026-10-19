**今天给大家介绍的是一款转为Android平台设计的图形化无线渗透测试工具，该工具名叫Hijacker，并集成了Aircrack、Airodump、Aireplay、MDK3和Reaver等知名的无线渗透工具，希望大家喜欢。**

## ![1.png](https://image.3001.net/images/20180529/15275845281627.png!small)

## Hijacker

Hijacker是一款带有图形化界面的渗透测试工具，Hijacker集成了[Aircrack-ng、Airodump-ng](https://www.aircrack-ng.org/)、[MDK3](https://tools.kali.org/wireless-attacks/mdk3)和[Reaver](https://tools.kali.org/wireless-attacks/reaver)等工具。它提供了简单易用的UI界面，用户不需要在控制台中输入任何的命令，而且也不需要手动复制粘贴MAC地址。

Hijacker适用于ARM架构的Android设备，设备的内部无线适配器必须支持Monitor模式，不过目前市面上只有少部分产品带有这种模式。这也就意味着，大部分用户都需要使用一种自定义固件。BCM4439芯片（MSM8974，例如Nexus5、Xperia
Z1/Z2、LG G2、LG G Flex、Samsung Galaxy
Note3）可以搭配[Nexmon](https://github.com/seemoo-lab/nexmon)（它也支持某些其他芯片）。带有BCM4330的设备可以选择使用 [bcmon](http://bcmon.blogspot.gr/)。

除此之外，用户也可以使用支持Monitor模式的外接无线适配器（通过OTG线缆）。

当然了，Root权限是必须的。

## 功能介绍

### 信息收集

> 1\. 查看附近的无线接入点（包括隐藏接入点）和基站。
>
> 2\. 查看特定网络的活动信息以及客户端信息。
>
> 3\. 收集接入点和基站统计信息。
>
> 4\. 从OUI数据库获取目标设备厂商信息。
>
> 5\. 查看设备信号强度，并过滤出信号强的目标。
>
> 6\. 保存捕获到的.cap数据包文件。

### 渗透测试

> 1\. 对目标网络中的所有客户端进行去认证操作。
>
> 2\. 使用MDK3和自定义选项对目标进行Beacon Flooding攻击。
>
> 3\. 对特定网络或附近AP进行MDK3 Authentication DoS攻击。
>
> 4\. 捕获WPA握手包。
>
> 5\. ReaverWPS破解攻击。

## 运行截图

![2.png](https://image.3001.net/images/20180529/152758451660.png!small)![3.png](https://image.3001.net/images/20180529/15275845156238.png!small)![4.png](https://image.3001.net/images/20180529/15275845169427.png!small)  

## 工具安装

要求：

> 1\. Android5+;
>
> 2\. 设备root（[SuperSU](http://www.supersu.com/download)）；
>
> 3\. 支持Monirot模式的固件；

最新版本下载地址：【[点我下载](https://github.com/chrisk44/Hijacker/releases)】

当你首次运行Hijacker时，工具会询问用户是否需要安装Nexmon固件。如果你已经安装了自己的固件或使用了外接无线适配器，你可以直接取消安装即可。

### 资源获取

Hijacker：【[点我下载](https://github.com/chrisk44/Hijacker/releases)】

Aircrack-ng/Airodump-ng：【[点我下载](https://www.aircrack-ng.org/)】

MDK3：【[点我下载](https://tools.kali.org/wireless-attacks/mdk3)】

Reaver：【[点我下载](https://tools.kali.org/wireless-attacks/reaver)】

Nexmon：【[点我下载](https://github.com/seemoo-lab/nexmon)】

Bcmon：【[点我下载](http://bcmon.blogspot.gr/)】

SuperSU：【[点我下载](http://www.supersu.com/download)】

***
参考来源：[Hijacker](https://github.com/chrisk44/Hijacker)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

