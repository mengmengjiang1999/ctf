## BugKu CTF(杂项篇MISC)—善用工具

描 述: webp。

下载压缩包。解压得到以后3个文件。

![1620474777_60967b99369e5e5917f5a.png!small](https://image.3001.net/images/20210508/1620474777_60967b99369e5e5917f5a.png!small)

## 一、工具

十六进制编辑工具 010 editor

Free_File_Camouflage图片隐写工具

## 二、解题思路

1.先看看hint.png，发现打不开，用010 editor编辑器打开是乱码。属性也没有发现。

![1620474788_60967ba439d8739178a84.png!small](https://image.3001.net/images/20210508/1620474788_60967ba439d8739178a84.png!small)![1620474798_60967baeba38506252f07.png!small](https://image.3001.net/images/20210508/1620474798_60967baeba38506252f07.png!small)2.hint一般来说都是txt格式，因此将hint.png改为hint.txt。发现可以正常打开，但是没啥用。被玩了。

![1620474806_60967bb6e2990aecd06fd.png!small](https://image.3001.net/images/20210508/1620474806_60967bb6e2990aecd06fd.png!small)

3.那就看看sapphire .jpg这个图片吧。属性没什么东西，拖到010
editor编辑器看看吧。后面有一堆乱码，但是看不出来是什么东西。应该是有图片隐写。各种工具上一遍吧，结果没做出来。

![1620474812_60967bbcb7090863a5270.png!small](https://image.3001.net/images/20210508/1620474812_60967bbcb7090863a5270.png!small)

4.这里需要用到一个工具，Free_File_Camouflage，这是一款能够将文件伪装成图片隐藏的工具，利用软件用户能将一些自己的私密日记或者私密软件伪装成图片存放，软件支持还原。下载地

> https://download.csdn.net/download/zjzqxzhj/15178293

5.打开Free_File_Camouflage工具，用De-camouflage a flie加载sapphire .jpg图片，然后点击，De-camouflage，生成1个zip.passwd.doc文档。

![1620474819_60967bc3e259f92d90d02.png!small](https://image.3001.net/images/20210508/1620474819_60967bc3e259f92d90d02.png!small)

6.打开word文档，提示“远在天边近在眼前:”，用这个密码解压不好使。气死！

![1620474827_60967bcbb91318d4c7240.png!small](https://image.3001.net/images/20210508/1620474827_60967bcbb91318d4c7240.png!small)

7.看看文档属性，没什么发现，再用010 editor编辑器打开看看，发现文件头居然是50 4B 03
04，标准的zip压缩包开头啊。赶紧把文件后缀改为zip试试。

![1620474836_60967bd468bfd3f0f8e86.png!small](https://image.3001.net/images/20210508/1620474836_60967bd468bfd3f0f8e86.png!small)

8.把压缩包解压后，得到一堆文件。挨个找找吧。

![1620474870_60967bf6348e5d6b1959a.png!small](https://image.3001.net/images/20210508/1620474870_60967bf6348e5d6b1959a.png!small)

9.最后在document.xml文档里找到了刚才看到的提示，“远在天边近在眼前”，猜测密码就在附近。最后发现XiAo_1U是压缩包解压密码。这回可以把real
steg.zip压缩包解压了。

![1620474842_60967bdaf2e10f904018e.png!small](https://image.3001.net/images/20210508/1620474842_60967bdaf2e10f904018e.png!small)

10.把csgo文件拖到010 editor编辑器里，发现文件头是riff，修改文件后缀为riff，用画图打开是一张图片。

![1620474852_60967be4e5841dc57b4d6.png!small](https://image.3001.net/images/20210508/1620474852_60967be4e5841dc57b4d6.png!small)

11.图片如下。

![1620474884_60967c04169658ae1b134.png!small](https://image.3001.net/images/20210508/1620474884_60967c04169658ae1b134.png!small)

12.属性和各种工具用了一遍，不知道怎么解决了。这里请教了一下大佬，大佬提示，题目描述里有“webp”。查了一下可以用stegpy隐写工具进行恢复。

首先我们需要在Kali里安装stegpy

pip3 install stegpy

使用方法 在Kali2020版需要sudo，在2019不需要

stegpy csgo.riff

13.执行stegpy csgo.riff 命令，得到flag。具体flag要自己去做哦

![1620474892_60967c0c2e0e4eff5ab77.png!small](https://image.3001.net/images/20210508/1620474892_60967c0c2e0e4eff5ab77.png!small)

## 三、总结

本题需要掌握各种图片隐写工具，如Free_File_Camouflage、
stegpy、Stegsolve、stegdetect0.4、silenteye、jphide等等等等。

