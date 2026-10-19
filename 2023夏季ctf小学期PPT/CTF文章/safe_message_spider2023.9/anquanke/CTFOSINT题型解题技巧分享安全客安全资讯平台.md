# CTF OSINT题型解题技巧分享

阅读量 **309870**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-09 15:30:54

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t011fffd7e0b8532ab3.jpg)

## 背景

近年来，开源情报（OSINT）作为一种新题型频繁出现在各大CTF赛事当中，也有一部分专门的OSINT赛事或黑客马拉松（Hackathon），旨在协助相关司法机构找回长期失踪的人员。还有团队制作了专门用于OSINT的虚拟机（Trace
Labs OSINT VM）。本文将回顾近年DownUnderCTF比赛中的几个OSINT挑战，并分享一些解题技巧。

## 挑战1 – Get over it!（DUCTF2021）

难度：简单

任务：根据图片找到桥的名字，以及桥梁的主跨长度

解题思路：根据图片的可交换图像文件格式（Exif），查看照片的属性信息，或通过搜图引擎进行反向图片识别。

  

1.1 – Get over it!

  

1\. 2 – 未知桥梁图片

  

1.3 – 通过exiftool工具，查看图片的数据信息。

通过exiftool工具对图片进行检查，发现图片的有效信息被擦除或修改了。所以，我们可以尝试搜图引擎对图片进行识别和反向搜索。在这推荐Yandex，一款来自俄罗斯的搜索引擎。Yandex在图片搜索方面，可能会比Google和Baidu等搜索引擎得到更多的信息，且更准确。

1.4 – 根据Yandex图片搜索的结果，发现在Instagram存在相似的照片

1.5 – 发布过相似照片的Instagram 用户，使用了#Eleanor Schonell这个标签

我们可以选择关键区域，帮助搜图引擎实现更准确的识别。这里我们可以发现一位Instagram用户曾发布过类似的照片。通过对比该用户的照片，我们可以发现两张桥梁的关键特征吻合，且该用户图片的标签显示，这座桥的名字是Eleanor
Schonell
Bridge（中文译作“埃莉诺思科内尔大桥”），位于澳大利亚布里斯班。进一步查阅大桥的资料，我们便可以得到该桥的主跨长度为185m。最终flag为
**DUCTF{Eleanor_Schonell_Bridge-185m}**

![](https://p5.ssl.qhimg.com/t0170257ec7e76d0419.png)

1.6 – 搜索Eleanor Schonell的图片结果

  

1.7 – 发现Eleanor Schonell正是我们要找到的桥

1.8 – 关于Eleanor Schonell的详细信息

## 挑战2 – Apartment Views（DUCTF2021）

难度：中等

任务：根据图片信息，定位犯罪团伙所在的公寓，并找到其交易的位置

解题思路：使用exiftool查看图片数据信息，利用搜图引擎，街景地图软件进一步定位

  

2.1 – Apartment Views

  

2.2 – 由线人提供的疑似犯罪团伙所在公寓拍摄的照片

2.3 – exiftool检查结果

首先尝试用exiftool检查图片的exif信息，并没有什么发现。现实比赛中，需要进行位置信息溯源的图片，往往都经过了剪辑和修改，很难直接获得位置信息。因此，我们接着使用Yandex进行图片搜索。由于图片分辨率不高，试图放大照片查看细节时像素感人，并无结果。但我们可以考虑从地标建筑开始，逐一进行检查。很快我们就有了发现，找到了与其中一个地标建筑相似的照片。继续搜索，我们得知这个地标属于澳新银行全球总部大厦（ANZ
World HQ），位于澳大利亚墨尔本，皇后街100号（100 Queen St,
Melbourne）。为了验证结果的正确性，接下来我们使用街景地图软件Google 地球，寻找照片的大概拍摄位置。

2.4 – Yandex图片搜索结果，发现了相似的建筑信息

2.5 – 该建筑可能是ANZ World HQ (澳新银行全球总部大厦)位于墨尔本

2.6 – ANZ World HQ （Google地球3D模型）

不断调整视角，我们可以发现，左侧的Google 地球3D模型图，与右侧我们需要溯源的图片吻合。

2.7 – 图片细节比对 1

2.8 – 图片细节比对 2

通过其它参照物，比如窗户样式，特殊建筑和建筑的突出部分，我们可以确认照片的拍摄地点为附近的公寓。切换到街景模式，我们可以得到公寓附近的所有街道信息。因为犯罪团伙的交易地点是附近的小巷，所以我们逐一查看小巷的街景。最后我们找到了犯罪团伙将要进行交易的小巷。（还有一个路人刚好出现在了交易地点，算是一个彩蛋吧）最终flag为
**DUCTF{mclean_alley}**

2.9 – 犯罪团伙藏身的公寓

2.10 – 目标公寓附近的街景地图，红色所在的小巷为犯罪团伙的交易地点

2.11 – 犯罪团伙交易地点的街景图

## 挑战3 – I think this one is really going to take off（DUCTF2020）

难度：中等

任务：根据路人提供的信息，找出2020年9月1日当天，飞过Boxing croc（拳击鳄鱼）附近的大型美国加油机，最终得到该飞机的首飞日期

解题思路：确认飞机飞过的位置，通过相关新闻报道以及第三方飞机追踪数据找到飞机的详细信息（机型，飞行器识别号，飞行日程和路线等）

  

3.1 – 题目描述

已有的情报信息如下，

目标：大型美国加油机（Big American refuelin plane）

位置：拳击鳄鱼（Boxing croc）附近

时间：2020年9月1日

通过搜索Boxing croc，我们可以看到一座拳击鳄鱼雕像，像是一个旅游景点，位于澳大利亚北领地达尔文附近。

3.2

3.3 – 拳击鳄鱼雕像（Boxing croc）位置

经过观察，我们可以发现附近有一座机场，达尔文国际机场（Darwin International
Airport）。但情报显示是一架大型美国加油机，应该属于军用飞机。因此我们需要找到当天（9月1日）飞过达尔文上空的一架美国军机。由于军机飞行记录可能涉敏，不同于民航信息。所以我们需要借助一些额外的飞行开放信息，对其进行追踪。（本篇内容仅限CTF
OSINT题型探讨。考虑到不同国家的法律有所差异，执行这些操作之前，请务必了解当地的法律法规，避免不必要的法律纠纷。）如果你是一名资深的军事爱好者，对各国飞行器比较了解，且已经猜出来该加油机型号，可以跳过接下来的内容，直接前往航空器注册号（Aircraft
registration）查询部分。

为了获得更多关于2020年9月1日飞经达尔文上空的美国加油机信息，我们可以先从新闻入手，寻找是否有相关的新闻报道。通过Google查找”american
refueling plane darwin”（美国加油机，达尔文）可以发现一则澳大利亚国防部的新闻，时间为2020年9月3日。大概内容为“美国空军
B-1B Lancers 和 B-2 Spirit 轰炸机最近参加了在北领地举行的美澳联合演习。虽然 B1-B 和 B-2
轰炸机没有在澳大利亚降落，但它们得到了从 RAAF 达尔文基地飞出的美国空军空对空加油机的支持”。

3.4 Google 搜索 “american refueling plane darwin”（美国加油机达尔文） 的结果

[https://news.defence.gov.au/media/media-releases/united-states-bomber-training-top-end](https://news.defence.gov.au/media/media-releases/united-states-bomber-training-top-end)

3.5 – 澳大利亚国防部网报道的美澳军事演习新闻里，提到了美国空军的加油机

进一步对新闻内容进行挖掘，我们可以发现新闻提及到RAAF Base
Darwin（澳大利亚达尔文空军基地），且有美国加油机从这一座机场飞出，为参与军事演习的轰炸机提供支持。而该空军基地正好位于达尔文国际机场附近。继续搜索更多关于RAAF
达尔文空军基地的新闻，我们找到了一些关于该空军基地的介绍，“RAAF达尔文基地没有永久飞机，但一些军用飞机在该基地过境或运行”。另外两则新闻是关于美澳联合演习的详情，分别出自澳大利亚地方媒体“海军科技”（Naval
Technology），以及美国印度洋–太平洋司令部（U.S. Indo-Pacific Command），内容为“日本嘉手纳空军基地第 909
空中加油中队的一个 KC-135
中队飞往澳大利亚达尔文，对演习的轰炸机进行支援”。因此，我们可以推测这正是飞过达尔文拳击鳄鱼雕像上空的美国加油机。接下来我们要做的事情是，通过开放的飞行数据网站，找到当天该军机的飞行记录。

[https://www.defence.gov.au/aircraftnoise/Darwin/Aircraft.asp](https://www.defence.gov.au/aircraftnoise/Darwin/Aircraft.asp)

3.6 – RAAF达尔文空军基地的介绍

3.7 – 进一步搜索RAAF附近的美军加油机新闻

[https://www.naval-technology.com/news/usaf-aircraft-participate-in-usmc-adf-joint-exercise/](https://www.naval-technology.com/news/usaf-aircraft-participate-in-usmc-adf-joint-exercise/)

3.8 – 新闻1， 来源（海军科技）

[https://www.pacom.mil/Media/News/News-Article-View/Article/2336270/increasing-interoperability-b-2s-b-1s-join-us-marine-corps-australian-defence-f/](https://www.pacom.mil/Media/News/News-Article-View/Article/2336270/increasing-interoperability-b-2s-b-1s-join-us-marine-corps-australian-defence-f/)

3.9 – 新闻2 ，来源（美国印度洋–太平洋司令部）

[http://www.planeflighttracker.com/2014/04/united-states-military-aircraft-in.html](http://www.planeflighttracker.com/2014/04/united-states-military-aircraft-in.html)

3.10 – [Plane Flight
Tracker](http://www.planeflighttracker.com/)提供了军用加油机的国际民航组织航空器型号的查询

3.11 – KC-135加油机的国际民航组织航空器型号为K35R

通过[Plane Flight
Tracker这个网站，我们得到了](http://www.planeflighttracker.com/)KC-135加油机的国际民航组织航空器型号
(ICAO aircraft type designator)为K35R。接下来通过Radarbox（部分功能需要付费）和ads-b提供的数据资料，我们找到了符合条件的美军加油机。其航空器注册号(Aircraft Registration
Code)为58-0086。最后我们通过planefinder这个网站和Google，找到了该飞机的首飞日期为16-07-59（1959年7月16日，真是古老），我们还发现另一架美军加油机当天也飞过了拳击鳄鱼雕像的上空，航空器注册号为58-0095，但两架飞机机型相同，并不影响最终的flag结果。

所以flag为 **DUCTF{16-07-59}**

[https://www.radarbox.com/data/aircraft/K35R](https://www.radarbox.com/data/aircraft/K35R)

![](https://p3.ssl.qhimg.com/t01253a34cee8ab3de4.jpg)

3.12 – 航空器注册号58-0086（目标加油机）2020年9月1日的飞行记录 1

[https://ads-b.nl/index.php?pageno=303&selectmove=day](https://ads-b.nl/index.php?pageno=303&selectmove=day)

3.13 – 航空器注册号58-0086（目标加油机）2020年9月1日的飞行记录 2

[https://www.ads-b.nl/track.php?AircraftID=11404541&datum=20200901&selectmove=day](https://www.ads-b.nl/track.php?AircraftID=11404541&datum=20200901&selectmove=day)

3.14 – 另一架美军加油机（航空器注册号58-0095） 当天的飞行记录（红色框内红点为拳击鳄鱼雕像位置）

[https://planefinder.net/data/aircraft/58-0086](https://planefinder.net/data/aircraft/58-0086)

3.15 – 目标加油机KC-135 的首飞时间为1959年7月16日（16-07-59）

## 小结

OSINT题目比较灵活，且可以与Forensics（取证）结合，多方位考察选手们的信息挖掘能力以及情报分析技巧。考虑到篇幅有限，有关OSINT与Forensics相结合的题目，我将会在后面的文章中分享。此处想引用
**Micropoor** 前辈说过的一句话，“渗透的本质是信息搜集”。而在情报学中，“有价值的”信息则称之为情报。

## 参考链接

[https://www.missingpersons.gov.au/about/national-events/hackathon-2020](https://www.missingpersons.gov.au/about/national-events/hackathon-2020)

[https://www.aware-online.com/en/osint-tutorials/reverse-image-search/](https://www.aware-online.com/en/osint-tutorials/reverse-image-search/)

[https://github.com/DownUnderCTF/Challenges_2020_public/tree/master/OSINT](https://github.com/DownUnderCTF/Challenges_2020_public/tree/master/OSINT)

[https://github.com/DownUnderCTF/Challenges_2021_Public/tree/main/osint](https://github.com/DownUnderCTF/Challenges_2021_Public/tree/main/osint)

[https://www.tracelabs.org/initiatives/osint-vm](https://www.tracelabs.org/initiatives/osint-vm)

[https://joyce.fyi/posts/ductf-2020/](https://joyce.fyi/posts/ductf-2020/)

[https://gijn.org/flight-tracking/](https://gijn.org/flight-tracking/)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **K0walski** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/258632](/post/id/258632)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t01a1ddb12314175131.jpg) K0walski

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

