# 【技术分享】绕过最新补丁，AR红包再遭技术流破解

阅读量 **108939**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-12-27 16:12:16

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

****

**作者：**[ **ChildZed**
****](http://bobao.360.cn/member/contribute?uid=2606963099)

**预估稿费：400RMB（不服你也来投稿啊！）**

******投稿方式：发送邮件至**[ **linwei#360.cn**](mailto:linwei@360.cn) **，或登陆**[
**网页版**](http://bobao.360.cn/contribute/index) **在线投稿******

**传送门**

[**【技巧分享】技术流花式“破解”支付宝AR红包，更多技巧征集中**
****](http://bobao.360.cn/learning/detail/3336.html)

**  
**

**（注：本文所提到的内容仅供技术研究，请勿用于非法用途）**

**  
**

**前言**

最近圈里流行破解支付宝的“AR红包”，有使用PS进行图片恢复的也有使用PHP脚本进行恢复的。当然支付宝那边也没闲着，先是声称减小了PS恢复图片后识别成功的概率，然后又是限制每人每日开启红包的次数，实话讲这是好事，毕竟如果AR红包步入Pokemon
Go的后尘，那就失去了“寻宝”的乐趣。不过如果可以从技术上来解决问题，比如提高对于实景和伪装图片的判别能力，那必然是喜闻乐见的。

  

**基于OpenCV恢复图像破解“AR红包”**

前面提到PS恢复图片识别成功的概率降低了许多，想想主要原因还是PS恢复出来的图片太过粗糙，而且还留有一定的细线条，这样机器进行识别时可以通过这些特征去判别图片是否是PS的。本文介绍的方法是基于OpenCV对图像进行处理，这种方法能够尽可能地还原原图像而不会产生条纹，目前成功率还不错。

在介绍方法之前先分析一下加了黑线的图片，可以对单一的浅色背景进行拍摄作为AR红包的图片，这样就可以从图片中了解黑线的分布。当然如果整幅图都是一个颜色程序是不允许的，所以。。我放了个硬币作为物体。

通过抓包得到的图片是100*100像素的，而在AR红包刚面世时图片都是200*200像素的，后者图片较为清晰，容易通过PS恢复，而前者较为模糊，因此PS难以对其进行较好的恢复，这也可能是支付宝的一个防作弊手段吧，但说实话，治标不治本，而且存在一个比较大的问题。

由于测试图片背景单一，且大小只为100*100像素，因此我们可以用PS打开图片并放大看看线条到底如何分布。

上图取的是图片的一部分，图中每个小方格是一个像素点。可以看出，线条有一个像素点宽的，也有两个像素点宽的，而线条颜色有黑和灰两种。我们把

这种类型的称为黑1，把

这种类型的称为黑2，把

这种类型的称为杂色，根据对整幅图的观察，其黑色线条分布规律为“黑2黑1黑2黑1黑2杂色”，相邻两种线条的距离为两个像素点。这样就可以确定线条的分布。

确定了线条的分布之后，就得考虑怎么去掉这些横线。对于一张正常图片而言，相邻像素点的色差并不大，而加了横线之后横线附近的相邻像素点色差非常大，如果可以将黑线部分的颜色修改为相邻的未被处理的像素点的颜色，那就可以较好的恢复图片的原貌。OpenCV提供了这项功能，废话不多说，上代码。(由于时间问题我直接将黑线条的像素坐标逐一处理，并没有按照前面总结的规律进行处理)

    
    
    #include "stdafx.h"
    #include"cv.h"
    #include"highgui.h"
    #include "cvaux.h"
    #include "cxcore.h"
    #include "opencv2/opencv.hpp"
    #include "opencv2/imgproc.hpp"
    using namespace cv;
    int _tmain(int argc, _TCHAR* argv[])
    {
    Mat src = imread("test.jpg");
    imshow("Raw", src);
    int i, j;
        for (j = 0; j < src.cols; j++)
    for (i = 0; i < src.rows; i++)
    {
    if (i == 3 || i == 6 || i == 10 || i == 14 || i == 17 || i == 21 || i == 24 || i == 28 || i == 31 || i == 35 || i == 39 || i == 42 || i == 46 || i == 49 || i == 53 || i == 56 || i == 60 || i == 63 || i == 67 || i == 71 || i == 74 || i == 78 || i == 81 || i == 85 || i == 89 || i == 92 || i == 96)
    {
    src.at<Vec3b>(i, j)[0] = src.at<Vec3b>(i - 1, j)[0];
    src.at<Vec3b>(i, j)[1] = src.at<Vec3b>(i - 1, j)[1];
    src.at<Vec3b>(i, j)[2] = src.at<Vec3b>(i - 1, j)[2];
    }
    if (i == 7 || i == 18 || i == 25 || i == 32 || i == 43 || i == 50 || i == 57 || i == 61 || i == 64 || i == 68 || i == 75 || i == 82 || i == 93)
    {
    src.at<Vec3b>(i, j)[0] = src.at<Vec3b>(i + 1, j)[0];
    src.at<Vec3b>(i, j)[1] = src.at<Vec3b>(i + 1, j)[1];
    src.at<Vec3b>(i, j)[2] = src.at<Vec3b>(i + 1, j)[2];
    }
    }
    imwrite("New.jpg", src);
    imshow("New.jpg", src);
    return 0;
    }

代码中src.at<Vec3b>(i, j)[0]，src.at<Vec3b>(i, j)[1]，src.at<Vec3b>(i,
j)[2]分别代表像素点的三个RGB通道。代码的含义就是将黑线的像素点的颜色根据情况修改为其上一坐标位置或者下一坐标位置的颜色。来看看效果如何。（左边是原图，右边是处理后的图，处理后的图上还有线的原因是代码中并没有对杂色类型线条中的灰色线条进行处理，只要处理一下线条就不存在了）。

不过这也有一些缺陷，比如斜线可能会还原成锯齿。对于支付宝的工作人员可以利用这个缺陷进行一下过滤。

前面说到的是100*100像素的图片，接下来讲讲AR红包刚推出时的200*200的图片。方法基本相同，也是通过使用相邻像素颜色修改黑线颜色来实现，不同的是黑线的宽度和黑线分布的方式，只需把上述代码的处理部分修改为如下所示即可处理。

    
    
    if (i == 5 || i == 55 || i == 105 || i == 155)
    {
    src.at<Vec3b>(i, j)[0] = src.at<Vec3b>(i - 1, j)[0];
    src.at<Vec3b>(i, j)[1] = src.at<Vec3b>(i - 1, j)[1];
    src.at<Vec3b>(i, j)[2] = src.at<Vec3b>(i - 1, j)[2];
    }
    if (i == 48 || i == 97 || i == 148)
    {
    src.at<Vec3b>(i, j)[0] = src.at<Vec3b>(i - 1, j)[0];
    src.at<Vec3b>(i, j)[1] = src.at<Vec3b>(i - 1, j)[1];
    src.at<Vec3b>(i, j)[2] = src.at<Vec3b>(i - 1, j)[2];
    src.at<Vec3b>(i + 1, j)[0] = src.at<Vec3b>(i - 1, j)[0];
    src.at<Vec3b>(i + 1, j)[1] = src.at<Vec3b>(i - 1, j)[1];
    src.at<Vec3b>(i + 1, j)[2] = src.at<Vec3b>(i - 1, j)[2];
    src.at<Vec3b>(i + 2, j)[0] = src.at<Vec3b>(i + 4, j)[0];
    src.at<Vec3b>(i + 2, j)[1] = src.at<Vec3b>(i + 4, j)[1];
    src.at<Vec3b>(i + 2, j)[2] = src.at<Vec3b>(i + 4, j)[2];
    src.at<Vec3b>(i + 3, j)[0] = src.at<Vec3b>(i + 4, j)[0];
    src.at<Vec3b>(i + 3, j)[1] = src.at<Vec3b>(i + 4, j)[1];
    src.at<Vec3b>(i + 3, j)[2] = src.at<Vec3b>(i + 4, j)[2];
    }
    if (i>5 && i<48 && ((i + 1) % 7 == 0))
    {
    src.at<Vec3b>(i, j)[0] = src.at<Vec3b>(i - 1, j)[0];
    src.at<Vec3b>(i, j)[1] = src.at<Vec3b>(i - 1, j)[1];
    src.at<Vec3b>(i, j)[2] = src.at<Vec3b>(i - 1, j)[2];
    src.at<Vec3b>(i + 1, j)[0] = src.at<Vec3b>(i - 1, j)[0];
    src.at<Vec3b>(i + 1, j)[1] = src.at<Vec3b>(i - 1, j)[1];
    src.at<Vec3b>(i + 1, j)[2] = src.at<Vec3b>(i - 1, j)[2];
    src.at<Vec3b>(i + 2, j)[0] = src.at<Vec3b>(i + 3, j)[0];
    src.at<Vec3b>(i + 2, j)[1] = src.at<Vec3b>(i + 3, j)[1];
    src.at<Vec3b>(i + 2, j)[2] = src.at<Vec3b>(i + 3, j)[2];
    }
    if (i > 48 && i < 97 && i % 7 == 0)
    {
    src.at<Vec3b>(i, j)[0] = src.at<Vec3b>(i - 1, j)[0];
    src.at<Vec3b>(i, j)[1] = src.at<Vec3b>(i - 1, j)[1];
    src.at<Vec3b>(i, j)[2] = src.at<Vec3b>(i - 1, j)[2];
    src.at<Vec3b>(i + 1, j)[0] = src.at<Vec3b>(i - 1, j)[0];
    src.at<Vec3b>(i + 1, j)[1] = src.at<Vec3b>(i - 1, j)[1];
    src.at<Vec3b>(i + 1, j)[2] = src.at<Vec3b>(i - 1, j)[2];
    src.at<Vec3b>(i + 2, j)[0] = src.at<Vec3b>(i + 3, j)[0];
    src.at<Vec3b>(i + 2, j)[1] = src.at<Vec3b>(i + 3, j)[1];
    src.at<Vec3b>(i + 2, j)[2] = src.at<Vec3b>(i + 3, j)[2];
    }
    if (i > 97 && i < 146 && ((i - 1) % 7 == 0))
    {
    src.at<Vec3b>(i, j)[0] = src.at<Vec3b>(i - 1, j)[0];
    src.at<Vec3b>(i, j)[1] = src.at<Vec3b>(i - 1, j)[1];
    src.at<Vec3b>(i, j)[2] = src.at<Vec3b>(i - 1, j)[2];
    src.at<Vec3b>(i + 1, j)[0] = src.at<Vec3b>(i - 1, j)[0];
    src.at<Vec3b>(i + 1, j)[1] = src.at<Vec3b>(i - 1, j)[1];
    src.at<Vec3b>(i + 1, j)[2] = src.at<Vec3b>(i - 1, j)[2];
    src.at<Vec3b>(i + 2, j)[0] = src.at<Vec3b>(i + 3, j)[0];
    src.at<Vec3b>(i + 2, j)[1] = src.at<Vec3b>(i + 3, j)[1];
    src.at<Vec3b>(i + 2, j)[2] = src.at<Vec3b>(i + 3, j)[2];
    }
    if (i > 147 && i<(src.rows - 2) && ((i - 2)) % 7 == 0)
    {
    src.at<Vec3b>(i, j)[0] = src.at<Vec3b>(i - 1, j)[0];
    src.at<Vec3b>(i, j)[1] = src.at<Vec3b>(i - 1, j)[1];
    src.at<Vec3b>(i, j)[2] = src.at<Vec3b>(i - 1, j)[2];
    src.at<Vec3b>(i + 1, j)[0] = src.at<Vec3b>(i - 1, j)[0];
    src.at<Vec3b>(i + 1, j)[1] = src.at<Vec3b>(i - 1, j)[1];
    src.at<Vec3b>(i + 1, j)[2] = src.at<Vec3b>(i - 1, j)[2];
    src.at<Vec3b>(i + 2, j)[0] = src.at<Vec3b>(i + 3, j)[0];
    src.at<Vec3b>(i + 2, j)[1] = src.at<Vec3b>(i + 3, j)[1];
    src.at<Vec3b>(i + 2, j)[2] = src.at<Vec3b>(i + 3, j)[2];
    }
    if (i == 43 || i == 93 || i == 143 || i == 193)
    {
    src.at<Vec3b>(i, j)[0] = src.at<Vec3b>(i + 2, j)[0];
    src.at<Vec3b>(i, j)[1] = src.at<Vec3b>(i + 2, j)[1];
    src.at<Vec3b>(i, j)[2] = src.at<Vec3b>(i + 2, j)[2];
    src.at<Vec3b>(i + 1, j)[0] = src.at<Vec3b>(i + 2, j)[0];
    src.at<Vec3b>(i + 1, j)[1] = src.at<Vec3b>(i + 2, j)[1];
    src.at<Vec3b>(i + 1, j)[2] = src.at<Vec3b>(i + 2, j)[2];
    }

来看看处理的效果。

  

**后记**

最后来说一下之前提到的支付宝使用100*100像素图片代替200*200像素图片存在的问题。由于后者清晰，因此容易进行PS，而前者比较模糊，PS效果不好，不过这也导致其识别效果不理想，按常理来说一个有棱有角的图片应该比一个模糊的图片容易识别的多，而图片模糊会造成识别上的误差，可能用户对实景进行扫描也没办法得到红包。因此个人认为比较好的解决方法应该是增强对于实景和图片的区别能力，毕竟叫AR红包，无法识别现实何来增强现实？

  

**传送门**

* * *

[**【技巧分享】技术流花式“破解”支付宝AR红包，更多技巧征集中**
****](http://bobao.360.cn/learning/detail/3336.html)

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ChildZed** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/85214](/post/id/85214)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) ChildZed

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

