# 路由器0day漏洞挖掘实战

阅读量 **580482**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-06-25 14:30:28

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t018ecf600607a3d7a1.jpg)

去年7月的时候在公司内部分享过这个议题，说来也将近一年了，懒得现在才发出来。

在2018年的3，4月两个多三个月的时间里，花了比较多的时间去搞一个国产的路由器，挖了一些漏洞后，之后也就没搞了。

也写了个有一点作用的MIPS IDAPYTHON审计辅助脚本

<https://github.com/giantbranch/mipsAudit>

## 基础知识

**简介**

1、路由器基本都是阉割版的linux系统  
2、架构以MIPS和ARM为主  
3、一般含有telnet服务  
4、很多基础命令以busybox的方式实现（如cat，chmod，date，echo，ifconfig，ls，kill等）

比如下面路由器中的busybox

![](https://p4.ssl.qhimg.com/t01fca18bd6f427c11b.png)

**路由器常见漏洞**

Web漏洞

  * XSS
  * CSRF

二进制漏洞

  * 主要是栈溢出

自带后门

  * 磊科路由器后门：私有协议，硬编码密码的后门

**环境及工具**

> Ubuntu虚拟机  
>  python  
>  IDA  
>  Binwalk  
>  QEMU  
>  对应架构的qemu虚拟机  
>  gdb及静态编译的gdbserver  
>  Burp，filefox插件  
>  。。。。。。

## 固件的提取与解压

**总览**

![](https://p0.ssl.qhimg.com/t012fda7ca4b65fd08a.png)

###  固件提取

1、对智能硬件（路由器）的升级进行抓包，提取url  
2、通过烧录器读取拆卸下来的芯片

![](https://p4.ssl.qhimg.com/t01a7be762f1d960dbe.png)

3、通过mtd的方式

  * 查看分区信息

![](https://p0.ssl.qhimg.com/t015764f28db31ad468.png)

  * 一般别人用dd命令来提取，其实用cp和cat也可以

![](https://p2.ssl.qhimg.com/t01fb007dfebd734a7d.png)

4、通过串口的方式  
假如串口可以获得shell，那么可以使用第三种方法

###  固件解压

binwalk -Me XXXXXX.bin  
M ，—matryoshka 递归扫描可解压的  
e，—extract 提取  
解压到的是_XXXXXX.bin.extracted/

![](https://p0.ssl.qhimg.com/t01e23ff842be2a9a36.png)

## 以某个路由器为例的漏洞挖掘

###  Web安全漏洞

审计web源码，发现有些目录（下面的goform）不存在，代码在二进制中实现，故使用黑盒测试

![](https://p1.ssl.qhimg.com/t016f11e891df4f3daa.png)

随便试了一下搞了几个XSS

![](https://p1.ssl.qhimg.com/t01d96bd95de2a29992.png)

![](https://p5.ssl.qhimg.com/t01ba8e9c15f4656d3e.png)

![](https://p2.ssl.qhimg.com/t01cd5168f2e37cd821.png)

还有自带命令执行的

![](https://p5.ssl.qhimg.com/t019abd87c4c7966bc0.png)

添加路由处存在命令注入漏洞，这个是找到溢出后顺便发现的

![](https://p2.ssl.qhimg.com/t01d3b5c17573a23bdb.png)

###  二进制漏洞挖掘之静态分析

这个我编写了个IDAPYTHON审计辅助脚本，用处嘛，有一点点吧。。。

开源地址：<https://github.com/giantbranch/mipsAudit>

辅助脚本功能如下：  
1、找到危险函数的调用处，并且高亮该行（也可以下断点）  
2、给参数赋值处加上注释  
3、最后以表格的形式输出函数名，调用地址，参数，还有当前函数的缓冲区大小

详细见下图

![](https://p3.ssl.qhimg.com/t01c3bcc5756a3075cb.png)

![](https://p5.ssl.qhimg.com/t01bf6f54ccf9ac9108.png)

针对不确定参数的函数

![](https://p3.ssl.qhimg.com/t01c599e4927fdcaf29.png)

我们可以点击addr那一列直接到达函数调用处，方便审计

其实跑出来的量还是很大的，我只不过是偶然的机会遇到了刚好又漏洞的。。

我定位到的是下面这里，有strcat和sprintf

![](https://p3.ssl.qhimg.com/t01566b212b26ed437f.png)

向上回溯有个route add的字符串

![](https://p5.ssl.qhimg.com/t01f7b1612afd082920.png)

那应该是添加路由的地方

![](https://p3.ssl.qhimg.com/t01777b40346f89055a.png)

测试

![](https://p0.ssl.qhimg.com/t01c8cbce2af1ee46f7.png)

发现后面goahead的pid都变了，那应该溢出崩溃，重启了

![](https://p2.ssl.qhimg.com/t01f291dd3310649c9f.png)

上gdb调试确认溢出

![](https://p5.ssl.qhimg.com/t0118cf485f55ba1198.png)

那么漏洞成因就是：strcat和sprintf的拼接

###  动态调试

1、基于qemu  
2、在设备上调试

**qemu**

qemu有两种运作模式  
用户模式（User mode），启动不同架构的Linux程序  
系统模式（System mode），模拟整个电脑系统（这个暂时还没能够实现动态调试）

注：有些程序比较依赖于特定的函数（比如nvram系列函数）就很难用qemu启动了

将对应的qemu程序及其依赖库拷贝到对应目录，使用静态的就没这烦恼了

![](https://p4.ssl.qhimg.com/t0158d80052e667e45a.png)

![](https://p1.ssl.qhimg.com/t01adf70646c1ea66cd.png)

启动一个mipsel的程序

    
    
    sudo chroot ./ ./qemu-mipsel ./bin/busybox
    

![](https://p1.ssl.qhimg.com/t01597a11739ad7fd43.png)

调试只要加-g参数即可（下面会监听23946端口）  
sudo chroot ./ ./qemu-mipsel -g 23946 ./bin/busybox  
ida 使用remote gdb debuger即可

![](https://p1.ssl.qhimg.com/t0104908b89f5441080.png)

###  在设备上调试

条件  
1、有shell权限  
2、有静态编译的gdbserver或者gdb

![](https://p0.ssl.qhimg.com/t01dfd5ad757114f0bf.png)

![](https://p5.ssl.qhimg.com/t01244781b0967890e9.png)

![](https://p4.ssl.qhimg.com/t0155e9a92312b67042.png)

## Reference

《揭秘家用路由器0day漏洞挖掘技术》  
《IDA Pro权威指南》  
《python 灰帽子》  
<https://github.com/wangzery/SearchOverflow/blob/master/SearchOverflow.py>  
<https://www.hex-rays.com/products/ida/support/idapython_docs/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **giantbranch** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/180714](/post/id/180714)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [IoT](/tag/IoT)
  * [路由器](/tag/路由器)
  * [漏洞挖掘](/tag/漏洞挖掘)

 **+1** __28赞

 __收藏

![](https://p3.ssl.qhimg.com/t01446b9b2e8e10b2db.png) giantbranch

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

