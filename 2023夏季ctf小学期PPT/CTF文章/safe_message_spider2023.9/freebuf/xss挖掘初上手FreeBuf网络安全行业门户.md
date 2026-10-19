本文主要总结了xss可能出现的场景。  
偏向于案例，最后分享一哈简单的绕过和比较好用的标签。  
  
  

1.搜索框

  * 首先看能否闭合前面的标签。  

如输入111”><svg/onload=alert(1)>

查看源码是否将前面标签闭合，可闭合的话可触发xss

  * 如过无法闭合时，用事件来触发xss.  

输入1111”><svg/onload=alert(1)>，F12看源码

![141645v444cmmpnmb4xp9x.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201812/05/141645v444cmmpnmb4xp9x.png.thumb.jpg)

  

发现”>无法闭合前面的标签。那么就用事件。

输入1111”onmouseout=”alert(1) 此处的事件是当鼠标放上去移走时触发xss

![141709df782fub6we474z5.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201812/05/141709df782fub6we474z5.png.thumb.jpg)  

  

  

2\. url参数

  
  
直接在url参数上插入xss代码。  

![141746we1ec0euvccl45zl.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201812/05/141746we1ec0euvccl45zl.png.thumb.jpg)  

  

  

3\. Post传递的参数

在Post数据包的参数的xss

![141811ldbrrzrrffgrbrr9.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201812/05/141811ldbrrzrrffgrbrr9.png.thumb.jpg)  

  

  

4\. 留言板

留言板的基本都是存储xss

一般都是闭合前面字符，再插入xss代码。

具体要看插入的xss在源码中的位置。

  

5\. 发布文章

发布文章处就和自定义一个html页面差不多。

可以自己自定义代码。同时要看系统的过滤了哪些标签。

src中存在较多的一般是某某智能系统，给你了模版，还可以自定义的。  

![141849d4h3oo4c4s8o8hjj.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201812/05/141849d4h3oo4c4s8o8hjj.png.thumb.jpg)  

  

![141906jip1hz5hifo6tpoh.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201812/05/141906jip1hz5hifo6tpoh.png.thumb.jpg)  

  

6\. 文件上传的名称处

此处xss较为少见，是因为返回包将输入的文件名重新输出了出来，造成了xss。

![141927v7x8vz8abs2zn8x2.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201812/05/141927v7x8vz8abs2zn8x2.png.thumb.jpg)  

  

7\. 文件上传内容（可定义html页面）

此处一般是上传文件php,asp,jsp等文件，系统会将其存储起来，而不解析。从而上传一个自定义的html让其解析。

![142201l6aw5msc25ssdnvf.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201812/05/142201l6aw5msc25ssdnvf.png.thumb.jpg)

  

访问返回的路径即可。

![142223bdwu2a4uaz9w9u6v.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201812/05/142223bdwu2a4uaz9w9u6v.png.thumb.jpg)

  

8\. 数据包的cookie处

![142253v22l2l766szvts3v.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201812/05/142253v22l2l766szvts3v.png.thumb.jpg)

  

9\. url无参数处

![142320l4dd4bw54zyfzp8o.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201812/05/142320l4dd4bw54zyfzp8o.png.thumb.jpg)

  

一般的提交框中插入xss

![142343sm3izn39zdnn9bi9.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201812/05/142343sm3izn39zdnn9bi9.png.thumb.jpg)

  

无参数时。

![142404quca9lavieks9cu9.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201812/05/142404quca9lavieks9cu9.png.thumb.jpg)

![142420bamajc0objrwm3j2.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201812/05/142420bamajc0objrwm3j2.png.thumb.jpg)  

  
  

  * 简单的绕过和标签  

  

最后分享一下简单xss绕过。（还是要看输入的代码在源码中的位置）

三个弹窗函数 alert confirm prompt

如设置了黑名单可通过编码绕过（url编码，html编码，bs64编码）

过滤了（）或者将（）输出成中文的（）可以用``代替。

  
  

拿出较为好用的payload

<details/open/ontoggle=alert(1)>

<svg/onload=alert(1)>

<img/src/onerror=alert(1)>

<video/src/onerror=alert(1)>

<script>(alert)(1)</script>

<video><sourceonerror="javascript:alert(1)">

<video/src/onloadstart="alert(1)">

<ahref=javascript:alert(1)>222</a>

  

