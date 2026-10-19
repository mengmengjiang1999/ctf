# CVE-2019-5096：GoAhead远程代码执行漏洞分析

阅读量 **1425024**

|评论 **10**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-12-05 18:44:18

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01312012a4a8d8cba7.jpg)

## 0x00 前言

GoAhead是一个开源(商业许可)、简单、轻巧、功能强大、可以在多个平台运行的嵌入式Web Server，可在github下载源码，链接如下：

<https://github.com/embedthis/goahead>

GoAhead Web服务器最近被曝光在版本v5.0.1，v.4.1.1和v3.6.5中存在一个可利用的代码执行漏洞，漏洞存在http请求的multi-part/form-data字段处理中，若是发送畸形的HTTP请求，可导致GoAhead Web服务器在处理此请求期间触发double-free漏洞。
该畸形请求可以未经身份验证的GET或POST请求形式发送，并且请求的服务器上不需要存在web页面。

## 0x01 漏洞分析

漏洞曝光者给出了触发漏洞的源码：

    
    
    / src/upload.c /
    66 static void freeUploadFile(WebsUpload *up)
    67 {
    68 if (up) {
    69 if (up->filename) { // BUG: First UAF here
    70 unlink(up->filename); // BUG: UAF/unlink - probably not a good idea
    71 wfree(up->filename); // BUG: Double free here
    72 }
    73
    74 wfree(up->clientFilename);
    75 wfree(up->contentType);
    76 wfree(up);
    77 }
    78 }

经过笔者的分析发现，freeUploadFile（）函数会在/src/upload.c的websFreeUpload（）函数中调用，而websFreeUpload（）函数会在/src/http.c中调用，/src/http.c中termWebs（）函数会调用websFreeUpload（）函数，/src/http.c中reuseConn（）函数会调用termWebs（）函数，从中可以看出漏洞触发函数freeUploadFile（）的调用过程。

在函数freeUploadFile（）的调用过程中，查看源码可发现有两行如下代码：

    
    
    / src/upload.c /
    255 freeUploadFile(wp->currentFile);
    256 file = wp->currentFile = walloc(sizeof(WebsUpload));

在此处变量 wp->currentFile会被free一次，但是被free的变量wp->currentFile在代码：

    
    
    / src/upload.c /
    371 hashEnter(wp->files, wp->uploadVar, valueSymbol(file), 0);
    372 defineUploadVars(wp);

在此处代码中把变量wp->currentFile加入了一个数组中，该数组中的变量在接下来的代码中会被free一次，free代码如下：

    
    
    / src/upload.c /
    86 for (s = hashFirst(wp->files); s; s = hashNext(wp->files, s)) {
    87 up = s->content.value.symbol;
    88 freeUploadFile(up);

变量wp->currentFile再次被free之后，导致了double-free漏洞触发，是fastbin double
free，利用方法和思路已经很成熟。

## 0x02 漏洞补丁

查看github源码可以发现，在v5.10版本中存在一处#287修补，如下图所示：

![](https://p3.ssl.qhimg.com/t011f7ab05e01f07c00.png)

从修补的结果来看，源码维护方在src/upload.c中的373行添加了一句赋0操作，通过将变量
wp->currentFile赋0以后，/src/upload.c第255行不会再对变量进行free操作，因此也不会发生double-free的漏洞了。

## 0x03 修补方案

鉴于GoAhead
Web服务器支持的体系结构和操作系统的非常广泛，使用面非常广，分布在大量交换机、路由器、智能摄像头等IOT设备中，下图是使用钟馗之眼搜索的分布数量：

![](https://p5.ssl.qhimg.com/t016d342bdbc6a12c08.png)

由于实际情况中，设备厂商可能会对GoAhead
Web服务器进行裁减或者修改，与原来的默认代码不一致，会致使漏洞可产生的效果或者利用方法不同，但是默认配置的话，漏洞是存在的，建议设备厂商尽快修补。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **binhry** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/194322](/post/id/194322)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [GOAhead](/tag/GOAhead)

 **+1** __11赞

 __收藏

![](https://p1.ssl.qhimg.com/t010857340ce46bb672.jpg) binhry

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

