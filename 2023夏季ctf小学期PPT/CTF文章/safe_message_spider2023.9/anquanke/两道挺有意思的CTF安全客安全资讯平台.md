# 两道挺有意思的 CTF

阅读量 **194063**

发布时间 : 2022-01-05 17:30:21

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01a418f040b20b79ab.jpg)

## 深育杯-Disk

难点:

> BitLocker 爆破
>
> rdp 缓存

文件：

![](https://p0.ssl.qhimg.com/t0138d5dd2372ee4fee.png)

文件后缀为 vera，是 veracrypt 的加密容器，解密文件需要密码

![](https://p1.ssl.qhimg.com/t0146fab9e2acea963a.png)

根据文件名在键盘上画出的轨迹

![](https://p2.ssl.qhimg.com/t0102b5b7b0939bbb26.png)

小写的 pvd 作为密码挂载 veracrypt 到本地

![](https://p3.ssl.qhimg.com/t01f0533e83c013545f.png)

查看 `goooood` 的文件头可以知道文件使用 7z 进行压缩

![](https://p1.ssl.qhimg.com/t0127c0dc558fcf0c6c.png)

解压后发现是套娃，里面还有一个 goood 文件，再次解压后里面有两个文件

![](https://p5.ssl.qhimg.com/t012e119099cffc4488.png)

其中 `Microsoft reserved partition.img`是个空文件，使用 HexEditXP 打开后里面什么也没有

![](https://p2.ssl.qhimg.com/t01fa0aa49b6861ec20.png)

`Basic data partition.img` 使用 DiskGenius 打开后显示使用 bitlocker 加密

![](https://p3.ssl.qhimg.com/t01faec2133eb0fa239.png)

使用 bitlocker2john 跑出 4 个 hash，一般使用第一个或第二个，第三个和第四个 hashcat 会识别不出来

`bitlocker2john -i Basic\ data\ partition.img`

![](https://p1.ssl.qhimg.com/t0181c192fc1d8e80ef.png)

![](https://p5.ssl.qhimg.com/t01e965847ebb54a6ec.png)

再用 hashcat 爆破 bitlocker 密码，hashcat —help 得到 bitlocker 对应的 hash 类型

![](https://p4.ssl.qhimg.com/t01c96f8111eeccb436.png)

把之前 bitlocker2john 跑出的 hash 保存成 txt 文件，使用经典的 rockyou 字典

`.\hashcat.exe -m 22100 hash.txt rockyou.txt`

![](https://p3.ssl.qhimg.com/t0106edc4feebd1ab9c.png)

得到密码 abcd1234，DiskGenius 解锁后在回收站内找到一个体积较大的文件，提取后发现文件使用 7z 压缩

![](https://p5.ssl.qhimg.com/t0196c2e8b9ad9322a9.png)

解压后得到一个 17.4MB 的 bcache24 文件，为 rdp 缓存文件

使用 [bmc-tools](https://github.com/ANSSI-FR/bmc-tools) 解密文件，得到 1115 张 bmp 图片

一开始以为是拼图，但由于量是在太大放弃

![](https://p3.ssl.qhimg.com/t01a2143c2534e14cc9.png)

翻到一张文件的缩略图，不出意外就是 flag

继续往下翻找到了两张疑似文件名的图片

![](https://p4.ssl.qhimg.com/t0177a15ce6a7481818.png)

拼起来后再与上面的缩略图作比较后确认文件名与图片上的内容完全一致

![](https://p4.ssl.qhimg.com/t0127371cc5ee671391.png)

尝试提交提示 flag 错误，base64 解码后提交正确

## 深育杯-bridge

难点:

> lsb 隐写
>
> idat 数据块

文件：

经典开局一张图，先用 zsteg 跑一遍，提示有 zlib stream，只不过文件头从 789c 被改成了 879c

![](https://p0.ssl.qhimg.com/t014940b61534bc20a6.png)

导出 zlib 解压后得到一个 rar 文件

提示可以去看看 flag1，可是还没找到 flag1，所以先暂时放一边

![](https://p2.ssl.qhimg.com/t0189ad3e4a0203edfe.png)

用 exiftool 查看图片 exif 信息，发现 Copyright 行有一串 hex 文本

![](https://p3.ssl.qhimg.com/t01bc35a00ce6c0e525.png)

解码后为 `dynamical-geometry` 后面会用到

用 StegSolve 查看图片，发现 PNG 文件头，前面有空数据导致 zsteg 没识别成功

![](https://p4.ssl.qhimg.com/t01e502ef4035986e2c.png)

导出后手动清理多余的空数据，得到一张图

![](https://p2.ssl.qhimg.com/t01f084dab925f24cb3.png)

凭借经验，应该是把数据藏在某个通道了，按列查看颜色值，发现蓝色通道出现经典 `504B0304`，妥妥的 zip 文件头，在 StegSolve
勾选蓝色通道，Extract by Column 后导出文件

![](https://p5.ssl.qhimg.com/t018104b0b860050cdd.png)

得到 zip 文件，解压需要密码

密码为刚刚在 exif 中得到的 `dynamical-geometry`

解压得到一个 stl 文件，以前做过 3D ，所以一眼认出了这是个模型文件

使用 Windows 自带的 3D 查看器即可打开，得到一半的 flag

![](https://p2.ssl.qhimg.com/t01efa9ca3f703d28c2.png)

根据刚刚的提示，另一个压缩包里的文件应该也是 stl 文件

同样用 3D 查看器打开，得到剩下的一半 flag

![](https://p5.ssl.qhimg.com/t0124e3cff634e01be5.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **雷石安全实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/264234](/post/id/264234)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __5赞

 __收藏

![](https://p2.ssl.qhimg.com/t01ebe472d127128939.png) 雷石安全实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

