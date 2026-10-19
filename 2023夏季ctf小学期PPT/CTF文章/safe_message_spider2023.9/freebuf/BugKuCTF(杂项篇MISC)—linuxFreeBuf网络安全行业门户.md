# BugKu CTF(杂项篇MISC)—linux

提 示: key{}

描 述: linux基础问题

下载后是一个linux.zip的压缩包。

![1620474599_60967ae7e524463f6a527.png!small](https://image.3001.net/images/20210508/1620474599_60967ae7e524463f6a527.png!small)

一、工具

十六进制编辑工具 010 editor

二、解题思路

1.解压缩后得到一个flag文件，直接用010
editor编辑器打开。搜索key关键字，得到flag。key{feb81d3834e2423c9903f4755464060b}

![1620474606_60967aeedd8df63e760cd.png!small](https://image.3001.net/images/20210508/1620474606_60967aeedd8df63e760cd.png!small)

2.第二种方法，把压缩包放到linux系统下，然后用cat或者strings命令搜索文件里的关键字key，得到flag。

三、总结

本题需要掌握010编辑器的使用方法，linux系统常用命令。

杂项题考点

常见载体：

图片：细微颜色差别，GIF图多帧隐藏，exif信息隐藏，图片修复等 ----解题工具
Stegsolve、stegdetect、jphide、photoshop、2345看图王

音频：信息隐藏在声音里(逆序)，信息隐藏在数据里(分析音频数据) ----解题工具 Audition，Matlab

视频：信息隐藏在视频的某个或多个帧里 ---解题工具 Premiere

文件隐写：把多个文件拼接成一个 ---解题工具 binwalk、foremost

Linux查看文件命令

cat //cat flag.php

tac //tac flag.php

head //head flag.php

tail //tail flag.php

nl //nl flag.php

more //more flag.php

less //less flag.php

od //od flag.php

grep //grep 'fla' flag.php

strings //strings flag.php

sort //sort flag.php

