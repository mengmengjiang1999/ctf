***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **前言**

 **在国际pwn大赛上，浏览器安全一直是重头戏，特别是神奇的沙盒穿越更是难上加难，本文开始分享学习浏览器安全的点点滴滴。**

###  **1.浏览器的Bug在哪里？**

首先要了解漏洞出现在哪里，才知道怎样找到浏览器的漏洞

> 用户界面
>
> 浏览器引擎
>
> 渲染引擎
>
> 网络交互
>
> JavaScript解释器
>
> UI后端
>
> 数据持久层

![浏览器的Bug在哪里](https://image.3001.net/images/20190430/1556570692_5cc7624479083.png!small)

###  **2.了解常见漏洞类型**

那么安全研究人员提交的浏览器漏洞都有哪些类型？

> 信息泄露  
>
>
> 拒绝服务
>
> 代码执行
>
> 模糊测试
>
> 同源策略
>
> 内容安全策略
>
> XHR
>
> 地址栏欺骗

![常见漏洞类型](https://image.3001.net/images/20190430/1556570716_5cc7625c4b555.png!small)
**何为Origin？**  

![Origin](https://image.3001.net/images/20190430/1556570826_5cc762cab9f95.png!small)

### **3\. SOP - Same origin policy**

在1996年Netscape规定，正常情况下，浏览器不会把页面A的数据给页面B

![SOP - Same origin
policy](https://image.3001.net/images/20190430/1556570928_5cc763301c2df.png!small)

Demo Code:  

![SOP - Same origin
policy](https://image.3001.net/images/20190430/1556570936_5cc76338b05cf.png!small)

如果这样一段代码可以让你在某个浏览器打开指定页面，那么恭喜你找到了一个SOP Bug

###  **4\. CSP - Content Security Policy**

它是W3C维护的一个标准，用于保护浏览器受到的多种攻击，像:

> UXSS
>
> SOP
>
> Code Injection
>
> Use Inline Styles Violation
>
> ...

 **Demo Code：**  

我们可以打开这样一个网站，点击“run”帮助我们自动化的测试CSP Bug  

Link:[http://csptesting.herokuapp.com/](http://csptesting.herokuapp.com/)

![CSP - Content Security
Policy](https://image.3001.net/images/20190430/1556570967_5cc763570fdd5.png!small)

###  **5\. RCE - Remote Code Execution**

> [https://developer.mozilla.org/en-> US/docs/Mozilla/Tech/XPCOM/Reference/Interface/nsILocalFile](https://developer.mozilla.org/en-> US/docs/Mozilla/Tech/XPCOM/Reference/Interface/nsILocalFile)

例如Mozilla提供了一个组件“nsilocfile”,这个组件可以使用字符串来引用

'@mozilla.org/file/local; 1' ---> Contract ID，使用JavaScript和CID，我们可以引用任何其他组件

 **Demo Code：**  

![RCE - Remote Code
Execution](https://image.3001.net/images/20190430/1556571006_5cc7637e1dbf6.png!small)![RCE
- Remote Code
Execution](https://image.3001.net/images/20190430/1556571011_5cc7638330c39.png!small)

**#2 RCE - UI Backend**

了解UI后端问题引起的RCE，

[https://paper.seebug.org/719/](https://paper.seebug.org/719/)

Edge RCE - UI Backend (CVE-2018-8495) Exploit Code：

![RCE - Remote Code
Execution](https://image.3001.net/images/20190430/1556571036_5cc7639c5e0b4.png!small)

###  **6\. Address Bar Spoofing**

地址栏欺骗，阅读经典的CVE-2018-8383了解，

writeup:[https://www.rafaybaloch.com/2018/09/apple-safari-microsoft-edge-browser.html](https://www.rafaybaloch.com/2018/09/apple-safari-microsoft-edge-browser.html)

Edge Browser Address Bar Spoofing (CVE-2018-8383) Exploit Code:

![Address Bar
Spoofing](https://image.3001.net/images/20190430/1556571070_5cc763beadb24.png!small)

###  **7\. Content Spoofing**

内容欺骗是Spoofing攻击的子集，类似这样的组合，现在的浏览器基本不存在这样的问题了，

Demo Code:  

![Content
Spoofing](https://image.3001.net/images/20190430/1556571098_5cc763dad7b8f.png!small)

**#2 Content Spoofing:**

Demo Code： **  
**

 **![Content
Spoofing](https://image.3001.net/images/20190430/1556571123_5cc763f352ad9.png!small)**如果前后复制的内容有变化，你就找到了新的Bug

###  **8\. uXSS**  

本来想拿CVE-2018-6128(<https://bugs.chromium.org/p/chromium/issues/detail?id=841105>)举例，

但liveoverflow已经给了最好的教程(<https://www.youtube.com/watch?v=0uejy9aCNbI>),

这里集了大多数浏览器uxss的poc/exploit(<https://github.com/Metnew/uxss-db>)，

可以尝试对各种国产浏览器进行测试，

因为国产浏览器都只是套Chromium，没修复的概率很大，混几个CVE应该不难

Demo Code：

![uXSS](https://image.3001.net/images/20190430/1556637754_5cc8683a3ec21.png!small)

 **9\. bUG Bounty  
**

报告漏洞有3个关键，确保拿到了钱，要有CVE ID，写writeup

> Safari:product-security@apple.com
>
>
> Chrome:[https://bugs.chromium.org/p/chromium/issues/](https://bugs.chromium.org/p/chromium/issues/)
>
> Mozilla
> Firefox:[https://bugzilla.mozilla.org/home](https://bugzilla.mozilla.org/home)
>
> Others:...

 **Phish Test:**

 **低成本**

此类攻击有几个很有意思的特点，设置简单，成本低，高回报

> 伪造子域 & 拼写错误
>
> 同形异义字攻击
>
> 标签伪造URL

![bUG Bounty
](https://image.3001.net/images/20190502/1556729291_5cc9cdcbcc1e0.png!small)

 **高回报**

此类攻击的作用通常是窃取账号，或者用来给受害者安装恶意软件

伪造子域 & 拼写错误

> <http://www.google.com.evil.org>
>
> <http://www.evil.org/p/google.com/support/>
>
> <http://www.rnicrosoft.com>

类似于这样的域名书写，让人误以为这是正规网站，取得信任度以后接下 来的操作就会很方便![bUG Bounty
](https://image.3001.net/images/20190502/1556729323_5cc9cdeb98341.png!small)

标签伪造URL，点进去看似谷歌的域名，会跑到"百度"上去

![bUG Bounty
](https://image.3001.net/images/20190502/1556729352_5cc9ce085f565.png!small)

只要这样一段简单的html，放到网页，邮箱等地方

![image.png](https://image.3001.net/images/20190502/1556729359_5cc9ce0f7694a.png!small)

![bUG Bounty
](https://image.3001.net/images/20190502/1556729366_5cc9ce16671d4.png!small)  

○印尼同形异义字攻击

(IDN homograph attack)

攻击手段且不说，当时我认为这是最容易获得一笔赏金的方式，

可以参考这些Report:

> [https://hackerone.com/reports/271324](https://hackerone.com/reports/271324)
>
> [https://hackerone.com/reports/172933](https://hackerone.com/reports/172933)
>
> [https://hackerone.com/reports/385372](https://hackerone.com/reports/385372)
>
> [https://hackerone.com/reports/59372](https://hackerone.com/reports/59372)

我们先来看一下Unicode是什么，打开Character Map,

![image.png](https://image.3001.net/images/20190502/1556729388_5cc9ce2c3ef61.png!small)

尝试"[www.freebuf.com](http://www.freebuf.com)"，  

![image.png](https://image.3001.net/images/20190502/1556729398_5cc9ce36dc6f8.png!small)  

当然这样有点蠢，我们接下来试一试这个办法

 **●EvilURL**

[
https://github.com/UndeadSec/EvilURL.git](https://github.com/UndeadSec/EvilURL.git)

我们用这样一个工具可以生成一个有Unicode的url，

![image.png](https://image.3001.net/images/20190502/1556729425_5cc9ce51607a4.png!small)  

打开地址会跳转到这样一个网址，

表示xn后面所有内容都是unicode编码的”,

因为DNS不支持，但你可以托管注册一个这样的域名，

以便跳转到假地址实施测试

![test.gif](https://image.3001.net/images/20190502/1556729660_5cc9cf3c3e187.gif!small)  

 **●用社会工程学完成二次交互**

像pwn2own这样的大赛上，一个浏览器的RCE可以让设备直接执行任何shellcode，

但这不符合大多数人实际情况，有一个解决办法就是用社会工程学，让对方下载然后打开我们的Payload,

![image.png](https://image.3001.net/images/20190502/1556729468_5cc9ce7cec4bc.png!small)  

在beef的这一栏目，像Chrome，Firefox的Bar，还有Fake Flash Update这些就符合需要，  

![image.png](https://image.3001.net/images/20190502/1556729494_5cc9ce96a4d29.png!small)  

它不仅仅是flash的一个欺骗框，配合对应的假图片和一点社工技巧，让对方运行你的恶意软件并不难，  

![test1.gif](https://image.3001.net/images/20190502/1556729602_5cc9cf02e8c3f.gif!small)

以上就是对Phish Test的一些案例，有兴趣的朋友们可以实践一番 **  
**

 **防范策略：**

> 细看域名，不明白的链接不要点
>
> 面对挂马Nday及时安装安全补丁和杀毒防护软件
>
> 好奇心驱使一定要看的东西选择，物理隔离，虚拟机，沙箱

未完待续...

 ***本文作者：conusys，转载请注明来自FreeBuf.COM**

