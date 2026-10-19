***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **![facebook-users-people-diversity1-ss-1920.jpg](https://image.3001.net/images/20190402/1554196986_5ca329fa026f3.jpg!small)**
**当拥有个人信息的组织机构发生数据失窃或遭受未授权访问行为时，就可能发生用户信息泄露事件。通常来说，这是种安全事件会导致一些敏感受保护的机密数据被广泛流传、分析或恶意利用。本文分享的漏洞writeup，只需知道Facebook用户的注册邮箱或者手机号码，就能间接获取该用户相关的隐私好友列表，进而推断出用户的一个大致的社交关系图谱。漏洞最终获得了Facebook官方$10,000美金的奖励。**
**  
**

按照Facebook[帮助页面的说明](https://www.facebook.com/help/163810437015615?helpref=faq_content)来看，“你可能认识的人”（People
You May Know）这项功能可以帮助Facebook用户找到更多相识的朋友，该功能建立起你和对方之间的关系是基于以下因素来进行判断的：

> 1.你们之间有共同朋友或存在相互朋友关系，这也是建立这种可能认识关系的最根本原因；
>
> 2.你们在同一个Facebook群组中，或是在同一张照片中被标记过；
>
> 3.另外就是你们通过同一个网络出口（学校、单位）登录过Facebook账户。

## Facebook好友列表的隐私设置

默认来说，Facebook用户的好友列表是公开的，当然，Facebook也给这个好友列表设置了三种不同的隐私选项：公开、朋友可见和仅自己可见等自定义设置），具体参考[Facebook帮助页面说明](https://www.facebook.com/help/ipad-app/115450405225661?helpref=uf_permalink)。

## 漏洞发现

这里作者发现的漏洞是这样的：首先，在用户注册阶段，恶意攻击者可以通过先输入目标受害者的手机号码作为注册确认的手机号码，如下：

![04.jpg](https://image.3001.net/images/20190402/1554196426_5ca327cab130c.jpg!small)之后，Facebook会向这个手机号码发送一个短信验证码，而且要求在确认界面输入这个验证码，如下：

![xx01.png](https://image.3001.net/images/20190402/1554196748_5ca3290ca9fd6.png!small)当然了，恶意攻击者肯定是不知道目标受害者的短信内容了，更别提这个短信验证码了。所以，在这里攻击者可以点击界面中出现的“更新联系方式”（Update
Contact info）按钮，在跳出的新手机号码或新邮箱地址添加栏中，填写攻击者自己的邮箱地址hack@rajsek.com，如下：

![xx02.png](https://image.3001.net/images/20190402/1554196765_5ca3291def531.png!small)接下来，攻击者自己的邮箱hack@rajsek.com中会收到一封Facebook发来的验证码邮件，在之前的确认界面中填写这个验证码，选择“继续”（Continue）。然后，Facebook会提示该账户与hack@rajsek.com是绑定关系，且需攻击者以邮箱hack@rajsek.com作为登录凭据完成登录：

![xx03.png](https://image.3001.net/images/20190402/1554196816_5ca3295048d9c.png!small)现在，我们转到以下链接去：

> <https://www.facebook.com/friends/requests/?fcref=swpsa>

这个链接是“你可能认识的人”URL，或者直接用curl对以下链接请求进行抓包：

    
    
    curl ‘https://www.facebook.com/gettingstarted/?step=friend_requests' -H ‘authority: www.facebook.com' -H ‘referer: https://www.facebook.com/gettingstarted/' -H ‘cookie: xxxx’ — compressed

这里，Facebook向恶意攻击者推送的“你可能认识的人”相关列表，正是目标受害者的好友列表，如下：

![xx04.png](https://image.3001.net/images/20190402/1554196871_5ca329870b574.png!small)

整个过程可在以下PoC视频中观看，视频中作者用目标受害者邮箱为注册人信息，用自己的手机号码作为联系更新信息，最终，这种方式也能同样获得目标受害者好友列表：

## 漏洞总结

该漏洞可以被一些恶意用户或攻击者利用，间接判断出目标受害者的社交关系图谱。前提在于，只需要知道目标受害者的注册Facebook时使用的邮箱地址或者手机号码，可以通过社工方式或是前述提到的好友关系建立依据来获得。

## 漏洞上报进程

2018.10.16 向Facebook进行漏洞初报；

2019.3.20 Facebook奖励我 $10,000 USD；

![xx05.png](https://image.3001.net/images/20190402/1554196946_5ca329d226d85.png!small)

 ***参考来源：[medium](https://medium.com/@rajsek/how-i-was-able-to-get-your-facebook-private-friend-list-responsible-disclosure-91984606e682)，clouds编译，转载请注明来自FreeBuf.COM**  

