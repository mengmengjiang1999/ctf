# 【工具分享】PCRT：一款自动化检测修复PNG损坏的取证工具

阅读量 **410763**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-09-08 11:16:59

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

作者：[sherlly_666](http://bobao.360.cn/member/contribute?uid=1319383851)

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**简介**

****

工具使用Python2.7编写， 旨在实现检查并自动化修复损坏的PNG图像，可用于恢复取证中提取到的缺失的图片流，或者提取隐藏在PNG图片中的恶意样本。

**具体包括：**

显示图片文件信息

修复PNG文件头错误

修复由于错误的图片长度或宽度导致的IHDR块crc校验出错

修复由于DOS->UNIX平台自动格式转换导致的部分IDAT块数据长度出错

修复由于自身错误导致的IDAT块crc校验出错

修复丢失的IEND块

提取追加在IEND块后的数据

自动显示修复后的图片

添加payload到图片文件

根据图片有限压缩数据尽可能恢复并显示

…

  

**特点**

****

支持跨平台运行（ **Windows/Linux/Mac OS** ）

支持窗口打开待修复文件，无需手动输入文件路径

自动化检测修复问题

支持修复结果即时显示

支持提取追加在IEND块后的数据（恶意程序常使用的传播方式）

支持插入payload到辅助块/关键块

修复结果去除所有辅助块

  

**安装**

****

**安装 Python 2.7**

[Python 2.7](https://www.python.org/downloads/)

**安装需要的Python 依赖包**

Tkinter

[PIL](https://pypi.python.org/pypi/PIL/1.1.6)

ctypes (For Windows)

**拷贝源码到本地**

    
    
    git clone https://github.com/sherlly/PCRT.git
    cd PCRT
    python PCRT.py

使用方法

    
    
    > python PCRT.py -h
    usage: PCRT.py [-h] [-q] [-y] [-v] [-m] [-n NAME] [-p PAYLOAD] [-w WAY]
                 [-d DECOMPRESS] [-i INPUT] [-f] [-o OUTPUT]
    optional arguments:
    -h, --help            show this help message and exit
    -q, --quiet           don't show the banner infomation
    -y, --yes             auto choose yes
    -v, --verbose         use the safe way to recover
    -m, --message         show the image information
    -n NAME, --name NAME  payload name [Default: random]
    -p PAYLOAD, --payload PAYLOAD
                          payload to hide
    -w WAY, --way WAY     payload chunk: [1]: ancillary [2]: critical
                          [Default:1]
    -d DECOMPRESS, --decompress DECOMPRESS
                          decompress zlib data file name
    -i INPUT, --input INPUT
                          Input file name (*.png) [Select from terminal]
    -f, --file            Input file name (*.png) [Select from window]
    -o OUTPUT, --output OUTPUT
                          Output repaired file name [Default: output.png]

**[注意]** 如果不添加 **-v** 选项则默认所有IDAT块长度均合法， 即不出现声明的IDAT数据块长度和实际数据长度不符合的情况。

  

**示例**

****

以IHDR.png为例显示图片信息

以0707.png为例修复IHDR块crc校验出错

以corrupt.png为例修复DOS->UNIX自动格式转换导致的IDAT块数据长度出错

以append.png为例提取附加在IEND块后的数据

以IHDR.png为例添加payload

以new.bin为例对以Deflate方式压缩的数据进行解析展示

附：文中示例文件已放入PCRT/examples文件夹下

  

**项目地址**

****

地址：<https://github.com/sherlly/PCRT>

欢迎提交issue，如有更好的想法也可以一起交流：）

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **sherlly_666** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86793](/post/id/86793)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t018b2c7ad9cc3999e9.jpg)
sherlly_666

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

