## ****背景介绍****

APT28是一个疑似具有俄罗斯政治背景的APT组织。情报如下图（https://www.yuque.com/p1ut0/qtmgyx/iuzruy#fCnk4）![](https://image.3001.net/images/20210917/1631885267_614497d3b5a699b58c977.png!small)

样本来源于沙箱app.any.run:[
_https://app.any.run/tasks/d6a8d1db-52c8-4371-b6d3-bf740408bb10/_](https://app.any.run/tasks/d6a8d1db-52c8-4371-b6d3-bf740408bb10/)![](https://image.3001.net/images/20210917/1631885327_6144980fa074d9990aeea.png!small)

**文件pe信息**![](https://image.3001.net/images/20210917/1631885456_614498909e67b09525472.png!small)

## 火绒剑和网络流量捕获

###  **火绒剑**

打开界面如下![](https://image.3001.net/images/20210917/1631885516_614498cc5f1a176cef8f4.png!small)

过滤->进程过滤->添加进程->开始监控，运行病毒样本

 **
**执行监控****![](https://image.3001.net/images/20210917/1631885584_6144991050104634ccd95.png!small)

**文件监控**![](https://image.3001.net/images/20210917/1631885660_6144995c3b5a02ae6487e.png!small)

**注册表监控**![](https://image.3001.net/images/20210917/1631885717_61449995614601e8abcde.png!small)

###  ** **网络流量捕获****

这里所用为fakenet，右键->管理员身份运行，部分流量如下![](https://image.3001.net/images/20210917/1631885842_61449a12aa5a7ef2b889f.png!small)

## 动态调试&静态分析

###  **D** **ropper分析**

 ** **loc_40140C****

sub_1301DEF执行自解密模块，会解密出
system32等字符串，同时解密出RtlGetCompressionWorkSpaceSize、RtlDecompressBuffer两个函数。![](https://image.3001.net/images/20210917/1631885924_61449a64e44ad2a253aff.png!small)

 ** **1**** ** **4**** ** **b**** **
**9****![](https://image.3001.net/images/20210917/1631885976_61449a981670e01139319.png!small)

 ** **1**** **
**e34****![](https://image.3001.net/images/20210917/1631886040_61449ad8c265899b5ff39.png!small)

对应的静态代码如下![](https://image.3001.net/images/20210917/1631886080_61449b00d51e436af8c45.png!small)

随后利用loadLibrary加载库文件然后进行相关地址的获取![](https://image.3001.net/images/20210917/1631886122_61449b2aa05f9c0a510f6.png!small)

loadLibrary运行结果如下![](https://image.3001.net/images/20210917/1631886164_61449b54ee8f9aa6e60da.png!small)

GetProcAddress执行结果如下![](https://image.3001.net/images/20210917/1631886204_61449b7c70fe8b15841f8.png!small)

随后调用上面获取的函数地址![](https://image.3001.net/images/20210917/1631886296_61449bd8215c49a341ecd.png!small)

接着调用了RtlDecompressBuffer释放pe文件，执行前![](https://image.3001.net/images/20210917/1631886348_61449c0c2f086558b004d.png!small)

接着调用了RtlDecompressBuffer释放pe文件，执行前![](https://image.3001.net/images/20210917/1631886391_61449c37c3ca1b1a30223.png!small)

执行后

![](https://image.3001.net/images/20210917/1631886483_61449c930fa544e5398bd.png!small)

该函数主要完成pe文件的释放操作

 **155B**

函数主要做if判断后然以后跳转到对应位置进行执行![](https://image.3001.net/images/20210917/1631886568_61449ce8d1e4ea197250d.png!small)

函数在401571位置处执行call函数后调用LoadLibraryW函数加载dll函数

 ** **264c****

函数内部调用1def进行解密处理，首次处理结果如下![](https://image.3001.net/images/20210917/1631886631_61449d2746552a2197bff.png!small)

为rundll32.exe

第二次进行解密结果![](https://image.3001.net/images/20210917/1631886671_61449d4f2a4752be7254f.png!small)

第三次解密结果![](https://image.3001.net/images/20210917/1631886727_61449d879cb0622bdd616.png!small)

第四次![](https://image.3001.net/images/20210917/1631886770_61449db24fbcb24fd0997.png!small)

第五次![](https://image.3001.net/images/20210917/1631886817_61449de1ad0b551b15169.png!small)

第六次![](https://image.3001.net/images/20210917/1631886859_61449e0b2590e909ada66.png!small)

第七次

![](https://image.3001.net/images/20210917/1631886938_61449e5a986230271fe54.png!small)

 **278E**

这里执行结果为 RegOpenKeyExW操作注册表函数

![](https://image.3001.net/images/20210917/1631887026_61449eb2eb4c2b5e95cb9.png!small)

调用createFileA进行文件的创建

![](https://image.3001.net/images/20210917/1631887128_61449f1812fc1f9122e8d.png!small)

创建的文件名如下

![](https://image.3001.net/images/20210917/1631887168_61449f4048fa82f6013b5.png!small)

写入的文件内容如下

![](https://image.3001.net/images/20210917/1631887209_61449f69be1eaaae18458.png!small)

收尾函数，获取启动相关进程分配堆块，然后进行销毁

![](https://image.3001.net/images/20210917/1631887258_61449f9a58ec413fbbd67.png!small)

函数返回后进行字符串拼接

![](https://image.3001.net/images/20210917/1631887301_61449fc5872010a8a9548.png!small)

写入注册表

![](https://image.3001.net/images/20210917/1631887356_61449ffc6dcf7e5018614.png!small)

释放文件的pe文件的dos头

![](https://image.3001.net/images/20210917/1631887414_6144a0363ba51bfd6629c.png!small)

创建注册表UserInitMprlogonScript

![](https://image.3001.net/images/20210917/1631887484_6144a07c13448798cbde4.png!small)

该函数最后主要完成写入注册表操作，完成免杀。

 ** **1707****

该处有个关于1707的调用

![](https://image.3001.net/images/20210917/1631887532_6144a0ac6290d4d3181b0.png!small)

内部调用三次1def函数进行解密，结果如下

![](https://image.3001.net/images/20210917/1631887568_6144a0d0889f363111fda.png!small)

![](https://image.3001.net/images/20210917/1631887598_6144a0ee4037d5c278c1d.png!small)

 **1d09**

内部函数如下，获取进程的执行权限

![](https://image.3001.net/images/20210917/1631887677_6144a13d83f834229a906.png!small)

获取执行权限后，带参数执行如下

![](https://image.3001.net/images/20210917/1631887722_6144a16ac7cbd02461b4d.png!small)

后通过deletefile函数清除文件

![](https://image.3001.net/images/20210917/1631887755_6144a18b62c43addf67c4.png!small)

### Dll文件静态分析

首先文件内执行的内容为

![](https://image.3001.net/images/20210917/1631887802_6144a1ba269a7fe9b4c0e.png!small)

接着分析cdnver.dll文件内，我们首先考虑寻找特定字符串cdnver，相关函数部分如下

![](https://image.3001.net/images/20210917/1631887836_6144a1dc3bedf64448607.png!small)

创建进程前压入了sub_10002CA0，相关参数解释为远程进程中线程过程的起始地址，该处为相关马的入口

![](https://image.3001.net/images/20210917/1631887875_6144a20396449ab21d499.png!small)

 ** **2CA0****

函数进入以后会调用如下函数![](https://image.3001.net/images/20210917/1631887918_6144a22ebf73cfb820597.png!small)

 **2cfd**

函数内如下

![](https://image.3001.net/images/20210917/1631887966_6144a25ec8c972f1a8b81.png!small)

函数执行流程如下

![](https://image.3001.net/images/20210917/1631888007_6144a287e4f895a47d641.png!small)

获取调试信息

![](https://image.3001.net/images/20210917/1631888052_6144a2b4bd70f9b8b737d.png!small)

读入dll文件

![](https://image.3001.net/images/20210917/1631888087_6144a2d77157d043cfc8d.png!small)

LoadLibraryExA加载文件

![](https://image.3001.net/images/20210917/1631888123_6144a2fbd4eeab421ff6d.png!small)

解密函数部分

![](https://image.3001.net/images/20210917/1631888156_6144a31c05055155a235c.png!small)

 **20c0**

函数如下

![](https://image.3001.net/images/20210917/1631888196_6144a3445f0559509c152.png!small)

解密结果

![](https://image.3001.net/images/20210917/1631888228_6144a36421a62b0642cc5.png!small)

 ** **G**** ** **et**** ** **hostname****

获取主机信息

![](https://image.3001.net/images/20210917/1631888269_6144a38d38ec598cb553a.png!small)

 ** **G**** ** **et**** ** **Volume**** ** **info**** ** **mationW****

获取磁盘信息

![](https://image.3001.net/images/20210917/1631888324_6144a3c417d0469038736.png!small)

 ** **3**** ** **6FB****

请求头

![](https://image.3001.net/images/20210917/1631888366_6144a3eec0ab2bb4804b7.png!small)

 ** **5**** ** **262****

操作注册表

![](https://image.3001.net/images/20210917/1631888406_6144a4169ba2e001028fc.png!small)

写入Domain

![](https://image.3001.net/images/20210917/1631888445_6144a43d9d04d91abad0c.png!small)

 ** **5**** ** **2**** ** **f**** ** **3****

访问网络

![](https://image.3001.net/images/20210917/1631888498_6144a47209772a1657e2e.png!small)

 ** **5**** ** **48**** ** **c****

解密cdnverify.net

![](https://image.3001.net/images/20210917/1631888541_6144a49d7e7f3fe7a0413.png!small)

###  ** **威胁情报查询****

![](https://image.3001.net/images/20210917/1631888614_6144a4e6730102bf9652a.png!small)

 **586a**

函数内进行加密

![](https://image.3001.net/images/20210917/1631888653_6144a50d49d98c8e7cc3f.png!small)

![](https://image.3001.net/images/20210917/1631888750_6144a56e4d7b6dd236a1b.png!small)

跳转到2d8f进行加密base64加密

TW96aWxsYS80LjAgKGNvbXBhdGlibGU7IE1TSUUgNy4wOyBXaW5kb3dzIE5UIDYuMTsgV09XNjQ7IFRyaWRlbnQvNC4wOyBTTEND![](https://image.3001.net/images/20210917/1631888807_6144a5a7adc8bf04c1207.png!small)

进行网络请求相关函数![](https://image.3001.net/images/20210917/1631888844_6144a5cc7ec7906c0499e.png!small)

第一个![](https://image.3001.net/images/20210917/1631888879_6144a5efc2edd6f1ba5b1.png!small)

第二个![](https://image.3001.net/images/20210917/1631888914_6144a6122fb655c72e9fd.png!small)

收集的信息![](https://image.3001.net/images/20210917/1631888971_6144a64bc7bebd363e77f.png!small)

提交数据方式![](https://image.3001.net/images/20210917/1631889034_6144a68a0acbd3767d606.png!small)

文章参考：

[一例APT28(Fancybear)样本详细分析
](https://www.yuque.com/p1ut0/qtmgyx/iuzruy)https://www.yuque.com/p1ut0/qtmgyx/iuzruy#17RRg

  

  

