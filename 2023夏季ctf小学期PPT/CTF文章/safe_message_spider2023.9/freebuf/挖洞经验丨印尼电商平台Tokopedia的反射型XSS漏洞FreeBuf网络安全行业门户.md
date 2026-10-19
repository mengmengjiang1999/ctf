*****本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。** ****  
**

**![6a4215d8b37e3e69a5a11355747faab2_Banner-Lapak-Pulsa-Tokopedia.jpg](https://image.3001.net/images/20190627/1561625446_5d148366e4c17.jpg!small)****本文分享的Writeup是关于印尼电商平台Tokopedia的火车票票务系统反射型XSS漏洞（Reflected
XSS），作者在测试该系统时，通过参数分离构造绕过了系统的XSS过滤防护机制，实现了反射型XSS，获得了3,000,000印尼盾（IDR）的赏金。**

## 漏洞说明

对于一般的网站系统而言，通常情况下其XSS过滤防护机制，当GET请求中包含有左尖和右尖括号时（<>
），一般就会对该GET请求进行编码。本文中，作者通过把</script/>分隔成了</script/和>两部份，巧妙地绕过了目标系统的XSS过滤机制。

早在2018年5月，我就在Tokopedia火车票票务系统（Tokopedia Train
Ticket）中发现了一个反射型XSS漏洞，当时来看这只是一个简单的XSS，并且我把漏洞上报给Tokopedia后，他们告诉我这是一个重复报，之后我就放在一边再没检查过了。

但今年3月，我在翻旧邮件的过程中偶然看到了该漏洞，好奇心驱使，我重新进行了测试，发现该漏洞依然存在，从未修复。

## 标签过滤

如果在Tokopedia火车票票务系统中查票时，会被执行一个重定向跳转，会被跳转到以下链接：

> [https://tiket.tokopedia.com/kereta-api/search/Jakarta-Gambir-GMR/Bandung-> Bandung-> BD?adult=1&infant=0&trip=departure&dep_date=16-09-2019&ori=GMR&dest=BD](https://tiket.tokopedia.com/kereta-> api/search/Jakarta-Gambir-GMR/Bandung-Bandung-> BD?adult=1&infant=0&trip=departure&dep_date=16-09-2019&ori=GMR&dest=BD)

请求中所有的GET参数都会被存储在一个名为dataJs.query的JS变量中。

![01.png](https://image.3001.net/images/20190627/1561624932_5d148164e0c30.png!small)由于上下文环境为JS，所以如果要想触发XSS必须实现实现以下方法之一：

> （1）突破JS环境限制，在其中一个GET参数中插入</script><script>alert(1)</script>
> ，这样构造的目的在于使HTML解析用</script>结束一个标签语境，导致JS运行出错，同时执行攻击者控制的脚本alert(1)；
>
> （2）突破JS变量dataJs.query的限制，在其中一个GET参数中插入"}; alert(1);
> //，这样也会使JS解析提前关闭变量语境，同时执行我们控制的脚本alert(1)，并在//作用下忽略其它语义。

在我第一次漏洞上报中我就用了第（1）种方法。由于目标系统不会把一些危险字符编码，如不会把<编码为&amplt，但会把"编码为\"，把\编码为\\\，这种情况下，上述第（2）种方法也就不适用了。

## 发现端倪

但后来我发现了个异常行为，ori和dest参数值的编码机制和其它参数存在不同，如以下实例中，其它参数值的“都会被编码为%22，而ori和dest不会：

![02.png](https://image.3001.net/images/20190627/1561624941_5d14816da2371.png!small)之后，我又ori和dest尝试了>，发现它们都未对>做编码：  

**![03.png](https://image.3001.net/images/20190627/1561624957_5d14817dbf20e.png!small)**好吧，那我尝试同时在dest中插入
<和>呢？最后发现，><没做编码： ****  

**![04.png](https://image.3001.net/images/20190627/1561624978_5d1481923e56c.png!small)**<
>做了编码：

****![05.png](https://image.3001.net/images/20190627/1561624995_5d1481a30f61c.png!small)很显然，目标系统未对参数ori和dest进行完全过滤，只对其中的
<.*>样式串实现了过滤。

## 绕过过滤

到了这步，我一开始觉得没什么可利用的了。但是，我通过谷歌搜索发现了一个经典的XSS漏洞利用库 -<https://github.com/s0md3v/AwesomeXSS#awesome-tips--tricks>，其中提到： **可以利用//来代替
>关闭一个标签（You can use // to close a tag instead of >）。**

试试看：

![06.png](https://image.3001.net/images/20190627/1561625038_5d1481cede50a.png!small)这样之后，浏览器抛出了“Uncaught
SyntaxError: Invalid or unexpected token”的错误，看似有点进步了，再来试试这样的：

![07.png](https://image.3001.net/images/20190627/1561625053_5d1481dd3f57f.png!small)还是不行，JS解析不把它识别为关闭标签，我又重新研究了上述AwesomeXSS库中的"Bypass
tag
blacklisting"介绍部份的</script/>应用，从上述分析来看，同时在一个参数中插入<>是会经编码过滤的，但如果我们把</script/>分散成</script/和>在ori和dest两个参数中来实现会如何？这里也就是</script/","dest":">样式，那么能绕过吗？

![08.png](https://image.3001.net/images/20190627/1561625159_5d1482478e28c.png!small)

最后发现，这种构造可以实现对标签的关闭，实现我们预想的reflected
XSS。所以，在Tokopedia票务系统中，我做了以下Payload构造，实现了反射型XSS的运行：

    
    
    https://tiket.tokopedia.com/kereta-api/search/Jakarta-Gambir-GMR/Bandung-Bandung-BD?dep_date=26-06-2019&adult=1&infant=0&trip=departure&ori=</script//&dest=><svg/onload=alert(document.location.href))//

 ****
****![09.png](https://image.3001.net/images/20190627/1561625183_5d14825f2d0ce.png!small)

## 深入分析

经进一步的研究发现，Tokopedia票务系统的会话cookie为_SID_Tokopedia，它是具备js脚本不能读取的HTTP-only属性的，所以从这点来看，不可能通过XSS来获取到它。但是，我后来发现，会话cookie被存储到了一个名为dataSession.session.cookies的JS变量中，而这和HTTP-only属性相冲突，所以攻击者利用这种反射型XSS漏洞，可以诱使受害者用户点击经过专门构造的URL链接，实现受害者会话窃取和账户劫持。

![xss.jpg](https://image.3001.net/images/20190627/1561625208_5d148278bd66e.jpg!small)![xss2.jpg](https://image.3001.net/images/20190627/1561625214_5d14827eb09cc.jpg!small)

## 漏洞上报

> 2019.3.28 漏洞初报给Tokopedia安全团队；
>
> 2019.4.8 Tokopedia安全团队回复称漏洞高危有效，已经进行了修复；
>
> 2019.6.11 Tokopedia官方奖励了印尼盾IDR 3.000.000 （￥1456RMB）；

 ***参考来源：[visat](https://visat.me/security/reflected-xss-in-tokopedia-train-ticket/)，clouds编译，转载请注明来自FreeBuf.COM**  

