# MassVet—发现Android应用恶意代码仅需10秒【附视频】

阅读量 **122539**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2015-09-10 10:08:20

 **x**

##### 译文声明

本文是翻译文章，文章来源：iie.ac.cn

译文仅供参考，具体内容表达以及含义原文为准。

由印第安纳大学、中国科学院信息工程研究所和宾州州立大学组成的研究团队发明了一种快速高效的Android应用(未知)恶意代码检测方法——MassVet,该方法对一个应用的平均检测时间仅需不到10秒,在相关领域产生了很大的影响。  

传统的基于特征的静态分析方法需要建立恶意代码特征库进行匹配,基于行为的动态分析方法通常需要动态执行程序,且覆盖率较低。无论是静态匹配或动态分析,都难以对未知行为的恶意代码进行检测。MassVet打破了传统的检测方法框架,无需使用恶意特征匹配,也无需了解恶意应用的内部逻辑和运行模式,仅在快速比对代码的基础上完成对市场级别的海量的应用软件进行检测分析。具体地,利用软件同源性对Android应用进行“同源”与“非同源”分类,并进行函数级和视图级别的相关性分析,从而快速定位恶意代码。MassVet的运行框架如下图所示:

图1 MassVet架构

MassVet基于上述原理和算法,已实现了对GooglePlay等33个Android软件市场,共计120万个Android应用的检测分析,发现共计12万恶意软件,其中至少2000个软件被下载50000次以上,影响1亿以上的用户。另外,MassVet对一个应用的检测时间仅需不到10秒,在相关领域产生了很大的影响。

研究团队还发现了另一个有趣的现象,一些开发人员上传的相同或类似的恶意程序到Google
Play后会被下架,然而这些恶意程序在被删除一段时间后,他们又会再次出现在Google
Play上。研究人员追踪了3711个应用的2265名开发者,发现其中604(28.4%)个应用被确定为恶意应用并且未做任何改动重新出现在Google
Play上,829 个应用以不同的名字重新出现在Google
Play上。这表明谷歌对于那些恶意程序甚至有些已知的恶意程序一直没有给予足够的重视,而这些恶意应用均能够被MassVet检测出来。

MassVet可以帮助应用软件市场对已提交、待审核的应用程序进行审核和过滤,也可以帮助用户进行恶意软件的检测,具有广泛的市场价值和应用前景。

更多细节,可以阅读研究团队的论文:

[http://www.informatics.indiana.edu/xw7/papers/vetfast.pdf](http://www.informatics.indiana.edu/xw7/papers/vetfast.pdf)

演示demo:

MassVet系统已发布:[www.appomicsec.com](/Users/zhoufei-s/Desktop/www.appomicsec.com)

关于作者:[http://www.kaichen.org/](http://www.kaichen.org/)

本文翻译自iie.ac.cn [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/82365](/post/id/82365)

安全客 - 有思想的安全新媒体

本文转载自: [iie.ac.cn]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

