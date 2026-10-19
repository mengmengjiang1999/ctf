> **本文作者：** i春秋作家HAI_ZHU  
>

  

**[HAI_的使用手册（各种好东西）](https://bbs.ichunqiu.com/thread-35905-1-1.html?from=beef)**

 **0x00 前言**

Dalvik模式是Android 4.4及其以下采用的模式，之后到了Android 5.0
之后就是ART模式，关于这两个模式的详细内容，请自行百度，如果在文章看不来的地方，可以翻翻之前的文章。如果有问题也可以私聊我。

废话不多说，直接上操作。

 **内容** ：demo 动态 dump 出 dex文件

## 环境说明

1.系统 小米 9.0  
2.ida 7.0

# 0x01 demo 动态 dump 出 dex文件

## 1.启动ida 端口监听

### 1.1启动Android_server 服务

![图片.png](https://image.3001.net/images/20180321/15216273673532.png!small)  

### 1.2端口转发

![图片.png](https://image.3001.net/images/20180321/15216273796428.png!small)  

### 1.3软件进入调试模式

![图片.png](https://image.3001.net/images/20180321/1521627389475.png!small)  

## 2.ida 下断

### 2.1 attach 附加进程

![图片.png](https://image.3001.net/images/20180321/1521627418136.png!small)

### 2.2 断三项

![图片.png](https://image.3001.net/images/20180321/15216274336208.png!small)  

### 2.3 选择进程

![图片.png](https://image.3001.net/images/20180321/1521627449139.png!small)  

### 2.4 打开Modules

搜索art

![图片.png](https://image.3001.net/images/20180321/15216274622077.png!small)  

PS：小知识

Android 4.4版本之前 系统函数在libdvm.so

Android 5.0之后 系统函数在libart.so

### 2.5 打开Openmemory（）函数

在libart.so中搜索Openmemory函数并且跟进去。

![图片.png](https://image.3001.net/images/20180321/15216274769727.png!small)

PS：小知识

一般来说，系统dex都会在这个函数中进行加载，但是会出现一个问题，后面说。

### 2.6 下断点

![图片.png](https://image.3001.net/images/20180321/15216274882757.png!small)  

## 3.运行程序到下断处

### 3.1 jdb转发运行程序

![图片.png](https://image.3001.net/images/20180321/15216275008103.png!small)  

### 3.2 查看IDA运行

成功下断，并且运行到我们下断的地方。

![图片.png](https://image.3001.net/images/20180321/15216275165164.png!small)  

  

### 3.3 查看 dex的位置

打开寄存器窗口，可以看到R1就是我们的dex

![图片.png](https://image.3001.net/images/20180321/15216275292141.png!small)  

然后在Hex窗口打开R1。  

![图片.png](https://image.3001.net/images/20180321/15216275609543.png!small)

很明显就看到了dex文件的二进制结构。如果不明白可以看看之前的dex文件分析。

### 3.4 提取关键信息

第一个关键信息：地址偏移：0xF35CA328

![图片.png](https://image.3001.net/images/20180321/15216275738297.png!small)  

第二个关键信息：文件偏移：70 35 01 00，转换一下就是 0x00013570  

![图片.png](https://image.3001.net/images/20180321/15216275851510.png!small)  

使用16进制加法器进行相加，F35DD898  

![图片.png](https://image.3001.net/images/20180321/15216275964546.png!small)

## 4\. dump

### 4.1 使用脚本进行dump

static main(void){ auto fp, begin, end, dexbyte; //打开或创建一个文件 fp =
fopen("d:\\\dump.dex", "wb"); //dex基址 begin = 0xF34C6320; //dex基址 + dex文件大小end
= begin \+ 0x00013570; for ( dexbyte = begin; dexbyte < end; dexbyte ++
){//按字节将其dump到本地文件中fputc(Byte(dexbyte), fp); }}  

### 4.2 脚本dump run

脚本填写好了之后，点击run即可。

![图片.png](https://image.3001.net/images/20180321/15216276261866.png!small)  

### 4.3 成功dump

![图片.png](https://image.3001.net/images/20180321/15216276362090.png!small)  

  
  

# 0x02 后续

这里dump出来的dex还是和原来的dex有一些区别的，要进行一些修复才可以。关于修复的内容还在探讨中，如果有大佬路过指教一二，感激不尽。

  

  

