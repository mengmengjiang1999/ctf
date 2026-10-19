# **概述** ****

奇安信病毒响应中心在日常的样本监控中发现，越来越多的黑客团伙通过极具诱惑性语言名命的诱饵文件，并使用黄赌毒方面的图片放到诱饵文件中，有些用户看到图片后会情不自禁的双击可执行程序从而启动远控木马，上传用户敏感信息
。

除此之外，我们根据相关线索，进行溯源分析后，发现这起攻击事件背后实际上是一个趋于成熟的色情产业链。

鉴于该产业链已经非常成熟，且越来越多的人从事该行业，为防止更多人一时冲动酿成惨剧，我们将此次捕捉到的攻击细节进行披露。

 ****

# 详细分析

诱饵一分析

MD5| 93988f9456e2403e95caeb81c6e6a29e  
---|---  
文件名| 上集街角素人搭訕在线观看  
文件类型| Zip  
  
捕获的初始样本名称为：上集街角素人搭訕在线观看.zip。

压缩包内容如下图所示：

![图片.png](https://image.3001.net/images/20191016/1571213070_5da6cf0e44d61.png!small)

上集街角素人搭訕在线观看.exe是通过Acronis
installer打包而成的SFX程序，运行之后会释放123.bat和svchost.exe文件经过分析，svchost.exe为大灰狼远控。

![图片.png](https://image.3001.net/images/20191016/1571213077_5da6cf15d1c7e.png!small)

远控连接的C&C地址和端口为154.223.133.104:2014，而123.bat的内容为：

![图片.png](https://image.3001.net/images/20191016/1571213084_5da6cf1cea4de.png!small)

上集街角素人搭訕在线观看.exe在运行过程中，调用ShellExecuteExW执行该bat脚本：

![图片.png](https://image.3001.net/images/20191016/1571213091_5da6cf2344464.png!small)

使用默认浏览器打开指定的色情网站，该网站使用的是目前主流**网站的模板：

![图片.png](https://image.3001.net/images/20191016/1571213097_5da6cf295e092.png!small)

通过对该网站进行溯源分析，我们发现该团伙注册了近百个网址用于重定向规避检测：

![图片.png](https://image.3001.net/images/20191016/1571213104_5da6cf3069e02.png!small)

还发现了两个同源apk样本，其中有个加了BaiduProtect壳，经过分析这类App都是使用同一框架和iapp接口。

![图片.png](https://image.3001.net/images/20191016/1571213112_5da6cf386e641.png!small)

运行之后则会调用WebView打开上述的Av网站，有趣的是app会弹框提示联系作者或加入QQ群，且每个推广app内置的QQ号和QQ群都不一样。

![图片.png](https://image.3001.net/images/20191016/1571213119_5da6cf3f***9f.png!small)

有些app，甚至还暗自刷量。

![图片.png](https://image.3001.net/images/20191016/1571213126_5da6cf464214e.png!small)

所以，我们基本可以得出结论，这些app的作者类似于推销员，弹出这个框的目的应该是吸引更多色情网站搭建者找他们推广自己的站点。通过对app内置的站点进行关联分析，我们发现了该团伙的另一处资产：

![图片.png](https://image.3001.net/images/20191016/1571213132_5da6cf4cec576.png!small)  

也找到了一些同源apk样本，这些样本依然使用上述的框架，访问内置的色情页面，其中有个伪装成聚分享图标的app：

![图片.png](https://image.3001.net/images/20191016/1571213140_5da6cf54a6281.png!small)

经过深度挖掘，我们发现了另外一个色情站点hxxp://www.XXXbb.com，该站点使用的模板与上述一致，但其位于另外一台服务器上：

![图片.png](https://image.3001.net/images/20191016/1571213145_5da6cf59a7dfe.png!small)

该站点注册的域名较少，最近开始活跃，且没有相应的app进行推广。有趣的是该网站所用的图片源和视频源与www.15XXXX.com一致，也就是说为同一个资源供应商。

图片源：hxxp://hb.avXXXXage.com/xxx.jpg

视频源：hxxps://xxx.sXXXXd1.com/视频网站(52av)/日期/具体类别

对资源供应商的域名进行关联分析，发现了一款免杀效果很好的apk文件,主要功能为成人电影播放器，内置付费功能，支持支付宝和微信，根据代码内容判断该app应为资源供应商直属的官方影音播放器。

![图片.png](https://image.3001.net/images/20191016/1571213153_5da6cf614ad81.png!small)

该apk全部使用的开源类库：

![图片.png](https://image.3001.net/images/20191016/1571213160_5da6cf68dee7d.png!small)  

其主界面位于com.fykj.newmovie.activity，运行时会检查有没有更新：

![图片.png](https://image.3001.net/images/20191016/1571213169_5da6cf717b9b5.png!small)

获取播放列表：

![图片.png](https://image.3001.net/images/20191016/1571213174_5da6cf76803b2.png!small)

有些影片只能使用手机迅雷或者影音先锋才能观看，在处理这类影片时会弹出温馨提示，提示用户安装影音先锋和手机迅雷，用于引流：

![图片.png](https://image.3001.net/images/20191016/1571213180_5da6cf7cef79a.png!small)  

手机迅雷的下载网址的域名：m.down.XXXXai.net

至此我们可以描绘出这类色情网站大致的运营流程。

![图片.png](https://image.3001.net/images/20191016/1571213191_5da6cf87ee663.png!small)

无独有偶，在我们捕获的另一个诱饵文件中也使用了相似的手法。

MD5| 90b33c691919b65559c1d8b534da73ff  
---|---  
文件名| 醫生猥褻過程詳細描述及藥物比對.doc  
文件类型| Doc  
  
该文件名比较具有诱惑性，很多用户可能会出于好奇而双击查看。

![图片.png](https://image.3001.net/images/20191016/1571213199_5da6cf8f8c9e8.png!small)

启用宏后，执行Powershell命令：

![图片.png](https://image.3001.net/images/20191016/1571213206_5da6cf968e1a9.png!small)

从hxxps://winupdate.site:443/updates下载ps脚本并执行：

![图片.png](https://image.3001.net/images/20191016/1571213212_5da6cf9c6dc10.png!small)

解密后为：

![图片.png](https://image.3001.net/images/20191016/1571213217_5da6cfa1745d3.png!small)

注入一段shellcode，shellcode为msf反弹shell，链接的C2：154.223.180.21:443

通过关联分析，我们发现该团伙主要从事私服、个人信息非法收集以及盗号相关的操作：

![图片.png](https://image.3001.net/images/20191016/1571213224_5da6cfa812cb8.png!small)  

# 总结

上述两个案例均是不同团伙采用相似的手法，即利用具有诱惑性的标题和图片，吸引受害者去点击相关带有恶意代码的诱饵文件。鉴于色情产业链的逐步完善，未来基于类似手法的攻击次数会越来越多，攻击的方式和手段也会越来越成熟。在跟踪该色情产业链的过程中，我们发现资源供应商有很多家，类似的攻击活动可能会更多。

在此希望用户遇到上述类似的具有诱惑性的文件，不要轻易点击。

目前奇安信集团全线产品，包括天眼、SOC、态势感知、威胁情报平台，支持对涉及该报告相关的攻击活动检测。

# IOC

文件MD5

93988f9456e2403e95caeb81c6e6a29e

8d0328d6ff17499b204e26a20c6973ff

6532eabadd42f6375c7902cdc223201b

b943a628f151a6d44d0363383b1bdc87

0f5594ba31a7ef6adeda52472ef26a12

9037f39ce6b627078b2a313d071d3fa8

7941657b529be01edb3dc6b8f50b8992

33fc200a128bccb26a64635121b24863

90b33c691919b65559c1d8b534da73ff

09c4a2cac0be0a3c62f4bc15cb3443f8

ae202d6ae06160beb2956a5162b9a058

1e935d0992fa7ed652e2885c4f490937

d43d503ea528de24d48f66d81d242550

14cd2a0d130418e0703d8e972a9f7d3b

c00d5c8e8090267e447db1a526f5d0ec

325a85c78a6a34d34d7a68ff409140fb

57eaf4488dc06ea7e147b7f3520ea3a7

C2：

154.223.133.104:2014

154.223.180.21:443

Host:

www.winupdate.site

b2rpt.hjkl45678.xyz

cltrpt.hjkl45678.xyz

  
  

