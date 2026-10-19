BugkuCTF—流量分析—WriteUp(持续更新)

[ syxvip](https://www.jianshu.com/u/380fd93bae2c)关注赞赏支持

# BugkuCTF—流量分析—WriteUp(持续更新)

# flag被盗

image.png

一个shell.php

里面包含一个flag.txt

image.png

# 这么多数据包

image.png

解压后有个ctf 数据包 丢尽wireshark看下

因为题目中给了提示，已经getshell了

找到 1234 跟 3588 这个握手包，追踪下tcp流

  

image.png

  

这个诡异的base64 就是flag

image.png

  

解密即可

  

image.png

# 流量分析(cnss)

100

  

image.png

只有几条数据  
随便老一条 追踪下tcp流

  

image.png

  

是B站的流量

  

image.png

  
我们来看下这位大牛的B站

    
    
    GET /stat.htm?id=2724999&r=http://space.bilibili.com/17190571&lg=zh-cn&ntime=1490634009&cnzz_eid=418561883-1487085537-http://www.bilibili.com/&showp=1536x864&p=http://space.bilibili.com/17190571/#!/&t=Chrstm的个人空间 - 哔哩哔哩 ( ゜- ゜)つロ 乾杯~ Bilibil...&umuuid=15ab677e5a02ed-064c9a36304b67-27d1a36-144000-15ab677e5a4205b&h=1&rnd=1218637328
    

发现base64：

image.png

  

image.png

what？？？？

# BugkuCTF—手机热点—WriteUp

100

  

image.png

用wireshark 打开以后很是懵逼  
乱折腾了一通，什么也没有（应该是我太菜）

来仔细阅读下题目  
没有流量，还可以通过什么方式进行传输，蓝牙！！嗯  
怎么看蓝牙的数据包？不会  
既然传了东西，为何不用binwalk分析下？  
好的，binwalk 歪打正着，出了flag

  

image.png

SYC{this_is_bluetooth}

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [iOS 面试宝典 没有比这更全的了（持续更新）](https://www.jianshu.com/p/3b7f3f596bcb)

1.ios高性能编程 (1).内层 最小的内层平均值和峰值(2).耗电量 高效的算法和数据结构(3).初始化时...

[欧辰_OSR](https://www.jianshu.com/u/f2a07930242f)阅读 28,206评论 8赞 265

  * [第三届上海市大学生网络安全大赛 流量分析 WriteUp](https://www.jianshu.com/p/df962f325e6b)

背景:本人ctf小萌新一个，学习了一点wireshark后，就自信满满的去刷题。在i春秋发现了一道300分的题目，...

[Mr_赵仙笙](https://www.jianshu.com/u/c8a45218e240)阅读 2,934评论 0赞 2

  * [Chapter 3. 用户界面](https://www.jianshu.com/p/62df49cb4da7)

3.1. 介绍 现在，您已经安装了Wireshark并有可能热衷于开始捕捉您的第一个数据包。在接下来的章节中，我们...

[wwyyzz](https://www.jianshu.com/u/788c8cf7829c)阅读 1,205评论 0赞 1

  * [2018-06-10](https://www.jianshu.com/p/52af615ddca4)

后期整理字体以及排版问题，修订不适合的翻译 “A wealth of information. Smart, ye...

[iamzzz](https://www.jianshu.com/u/59a7b077cd9d)阅读 623评论 0赞 0

  * [我的故事我做主](https://www.jianshu.com/p/6711534b6111)

我要开通简书了，我想把很多故事写给自己 我想把自己在生活中的所感所闻都记录下来，在这里展现所有美丽或者哀伤的...

[周子翼](https://www.jianshu.com/u/c0862fd238b4)阅读 255评论 1赞 1

 