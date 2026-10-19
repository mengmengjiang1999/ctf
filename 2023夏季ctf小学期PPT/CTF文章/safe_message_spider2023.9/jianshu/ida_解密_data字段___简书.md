ida 解密.data字段

[ 萌木盖](https://www.jianshu.com/u/0e56159ab5a7)关注赞赏支持

# ida 解密.data字段

# 不讲案例讲思路

# 问题

打开so后，进来之后，他搁这加解密呢

  

image.png

image.png

进来看可以看他初始值

  

image.png

  

可以硬扣代码，一个一个进行异或算。

# 当然还可以按照今天要讲的办法

### 1、ida打开叼毛厂开发的so

### 2、shift + F7 或者 view->open subviews->segments 打开Program Segmentation界面

### 3、记录.data的起始地址

image.png

### 4、dump内存

  * 1、adb shell 进手机里
  * 2、 ps -ef查看app进程
  * 3、 cat 该进程的maps | grep so的名字 查找so的起始地址
  * 4、下面代码块里得知`bc387000`是起始地址，上图得知偏移地址是`6B000`,两个数相加再转成10进制。得出skip的数字`3158253568`，然后上图的结束地址-起始地址`（6FAC0-6B000）`再转10进制得出count的值`19136`,of填上你要保存的文件位置。

    
    
    你本机： adb shell
    sailfish:/ $ su
    sailfish:/ # ps -ef | grep app包名
    u0_a140       2014   729 2 15:40:00 ?     00:01:18 包名:titan
    u0_a140       2593   729 23 15:40:07 ?    00:14:52 包名
    u0_a140       3206   729 1 15:40:25 ?     00:00:23 包名support
    u0_a140       3650   729 2 15:40:32 ?     00:01:04 包名:lifecycle
    root          8204  8162 6 16:45:35 pts/1 00:00:00 grep 包名
    sailfish:/ # cat /proc/2593/maps | grep so_name
    bc387000-bc3f0000 r-xp 00000000 103:13 917860                            /data/app/包名-gnpaWrsVoW1BLVXfcCE8DQ==/lib/arm/libpdd_secure.so
    bc3f1000-bc3f2000 r--p 00069000 103:13 917860                            /data/app/包名-gnpaWrsVoW1BLVXfcCE8DQ==/lib/arm/libpdd_secure.so
    bc3f2000-bc3f7000 rw-p 0006a000 103:13 917860                            /data/app/包名-gnpaWrsVoW1BLVXfcCE8DQ==/lib/arm/libpdd_secure.so
    sailfish:/ # dd if=/proc/2593/mem of=/sdcard/你想保存成的文件名 skip=3158253568 ibs=1 count=19136
    19136+0 records in
    37+1 records out
    19136 bytes transferred in 0.101 secs (189465 bytes/sec)
    

### 5、查看文件

可以用任意16进制查看器，我这里使用的是010editor，能看到一堆文字

  

image.png

### 6、塞到ida里

打开ida >> file >> script command...

  

image.png

    
    
    import copy
    import idc
    import idaapi
    import idautils
    from idc import *
    from idaapi import *
    
    
    data_ea = 0x6B000
    data_ed = 0x6FAC0
    
    int_array = []
    
    with open('你那个文件_patch', 'rb') as fd:
        byte_array = list(fd.read())
        for val in byte_array:
            int_array.append(ord(val))
    
    for addr in range(data_ea, data_ed):
        idc.patch_byte(addr, int_array[addr-data_ea])
    
    print('=====patch end=====')
    

### 7、转换字符 进入 .data 段 按快捷键A

image.png

### 大结局

把刚才那段加密的A出来 你就知道那片东西是啥了！  
随便点一进去一个函数再按ESC键返回，当前函数会刷新，且变成这样，集体犯红。

  

image.png

  

这是因为你刚才在.data 段A的，导致现在他之前那种分析方式不适用现在。它混乱了。

#### 解决办法

点中红的地方按`Y`或者右击选择`set item type` 输入`char*`  

image.png

  
就变成了  

image.png

  
很明显这片代码是为了拼成`linuxVersion`和`procVersion`两个字符串  
拼成这个 肯定是so想获取linux的版本信息和内核的版本信息

image.png

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [Android逆向之旅---应用的"反调试"方案解析(附加修改IDA调试端口和修改内核信息)](https://www.jianshu.com/p/ee3f4d225f4c)

一、前言在前一篇文章中详细介绍了Android现阶段可以采用的几种反调试方案策略，我们在破解逆向应用的时候，一般现...

[JiangWei_App](https://www.jianshu.com/u/132a12c46a89)阅读 1,481评论 2赞 5

  * [pwnable.tw 题解一 Start orw calc doublesort](https://www.jianshu.com/p/0ec5f169128d)

0x01 Start checksec 的时候可以看到程序没有打开任何的安全保护措施，然后查看IDA下的汇编代码，...

[Nevv](https://www.jianshu.com/u/ee0e3eea3687)阅读 1,495评论 0赞 2

  * [深度解密HTTP通信细节](https://www.jianshu.com/p/4203b4513ed5)

上一篇文章中，我们学会了用wireshark和tcpdump来分析TCP的“三次握手，四次挥手”，非常好用。这哥俩...

[饶全成](https://www.jianshu.com/u/6b6e18ffefd3)阅读 1,047评论 0赞 0

  * [IDA PRO权威指南--阅读笔记（一）](https://www.jianshu.com/p/95e4733842f1)

站在巨人的肩膀上——IDA PRO权威指南阅读笔记 一，窗口 view->open subviews 打开/关闭各...

[SueLyon](https://www.jianshu.com/u/0a024919f946)阅读 13,436评论 0赞 6

  * [看雪2018CTF APK-ExecuteTable](https://www.jianshu.com/p/bc4d90d49a08)

此题为一道移动APP的逆向题，里面的坑很多，无法一一表述。该篇文章也是看了大牛们的wp后，加上自己的调试心得和体会...

[静析机言](https://www.jianshu.com/u/fd954951a7f2)阅读 1,036评论 0赞 0

 