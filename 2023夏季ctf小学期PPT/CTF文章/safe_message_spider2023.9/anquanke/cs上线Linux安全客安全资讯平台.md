# cs上线Linux

阅读量 **182241**

发布时间 : 2022-05-27 10:30:15

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01bde4fc851f4174ed.jpg)

## 概述

基于自身办公环境的需求，想着在自己Mac上搭建cs的服务端和客户端，解决资源可以充分利用，学习cs摆脱多个机器的尴尬处境，之前不知道互联网上有没有这方面的实践，随手百度，得此文，记录之。

## 结论

多次实践，实现了Linux的上线，未实现Mac的正确返回结果，后续如知具体原有，会自行补充更新。

## 实验环境

cobaltstrike4.3版本 + mac + kali

## 实操

### 安装

如果想让上线Mac或者Linux系统，我们需要下载crossc2,

项目地址：`https://github.com/gloxec/CrossC2/`

![](https://p2.ssl.qhimg.com/t01ecc61c7b54561166.jpg)

注意：目前支持3.14和4.0以上的版本

**下载基础文件:**

  1. CrossC2.cna
  2. genCrossC2 (如果操作系统是Windows, 下载genCrossC2.Win.exe)
  3. 选择Script Manager，添加CrossC2.cna (如果成功安装，菜单栏会多出一项 CrossC2)
  4. 修改CrossC2.cna脚本中genCC2路径为真实路径
  5. $genCC2 = “/xxx/xx/xx/genCrossC2.MacOS”;
  6. 因为一些原因，目前强制只支持HTTPS beacon。
  7. 复制server上cs目录下的 .cobaltstrike.beacon_keys到本地目录下

具体修改如下：

![](https://p4.ssl.qhimg.com/t01a8b1d0c85c06b6d4.jpg)

![](https://p2.ssl.qhimg.com/t01041b86032869eb58.jpg)

![](https://p1.ssl.qhimg.com/t01077fc28041e90b24.jpg)

后面通过cs脚本管理,添加我们刚才配置好的CrossC2.cna

![](https://p0.ssl.qhimg.com/t0191f3ea3d1539db8c.jpg)

添加完成后，cs导航栏会有一个crossc2的选项卡。

### 上线Linux

  1. 先创建一个监听服务在Mac上，此监听必须用https的方式，上述安装过程中已经提到了。这里创建的时候注意下。
  2.   3. 生成相关载荷
  4.   5.   6. 选择要上线的系统类型。
  7.   8.   9. 最后说一句，这东西玩玩就好了，二十次的重启，可能会换来一次的成功，运气好的，可能一次就搞定。

### 上线mac

![](https://p3.ssl.qhimg.com/t01db402489a7cc6959.jpg)

![](https://p1.ssl.qhimg.com/t013080b7d104ab9491.jpg)

![](https://p2.ssl.qhimg.com/t010d01120d39287e75.jpg)

理论上有这个alive的返回cs应该就上线了，但是，很遗憾，并没有。反观上面的linux就可以。

![](https://p5.ssl.qhimg.com/t0161de8a97169c9d1c.jpg)

参考链接 `https://gloxec.github.io/CrossC2/zh_cn/redteam/attack_macos.html`

官方其实并没有给出Mac上线的截图，笔者这里也没有测试通。惭愧！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Tide安全团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/273432](/post/id/273432)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CS](/tag/CS)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t013dca47abc465f8d2.png) Tide安全团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

