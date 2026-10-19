i春秋作家：[anyedt](https://bbs.ichunqiu.com/thread-42390-1-1.html?from=beef)

原文来自：[https://bbs.ichunqiu.com/thread-42390-1-1.html](https://bbs.ichunqiu.com/thread-42390-1-1.html?from=beef)

  

一款好的[渗透测试](http://bbs.ichunqiu.com/portal.php?from=beef)浏览器插件可以大大提高我们渗透测试的效率，那么作为渗透测试人员，我们是否有一些不可或缺的浏览器插件呢。嗯，必须有。往下看文章。

    
    
    ## 01.Firebug

Firebug是firefox下的一个扩展,能够调试所有网站语言，如Html,Css等，但FireBug最吸引人的就是javascript调试功能，使用起来非常方便，而且在各种浏览器下都能使用（IE,Firefox,Opera,
Safari）。除此之外，其他功能还很强大，比如html,css,dom的查看与调试，网站整体分析等等。总之就是一整套完整而强大的
WEB开发工具。再有就是其为开源的软件。  
Firebug是网页浏览器 Mozilla Firefox
下的一款开发类扩展，现属于Firefox的五星级强力推荐扩展之一。它集HTML查看和编辑、Javascript控制台、网络状况监视器于一体，是开发JavaScript、CSS、HTML和Ajax的得力助手。Firebug如同一把精巧的瑞士军刀，从各个不同的角度剖析Web页面内部的细节层面，给Web开发者带来很大的便利。例如
Yahoo! 的网页速度优化建议工具 YSlow。[1]Firebug也是一个除错工具。用户可以利用它除错、编辑、甚至删改任何网站的
CSS、HTML、DOM 以及JavaScript 代码[2]。

### 如何安装(我用waterfox演示)

打开设置-Add-ones-输入firebug(如果不能直接搜索到就得按最下面的显示更多结果进行跳转)-Add-to-firebox-Add

  
![image.png](https://image.3001.net/images/20180705/15307723333661.png!small)![image.png](https://image.3001.net/images/20180705/15307723403565.png!small)![image.png](https://image.3001.net/images/20180705/15307723531009.png!small)![image.png](https://image.3001.net/images/20180705/15307723569381.png!small)![image.png](https://image.3001.net/images/20180705/15307723604885.png!small)![image.png](https://image.3001.net/images/20180705/15307723698409.png!small)

  

### 简单演示使用（演示我两个常用的小功能）

#### 1.查看Html源代码

在渗透测试过程中为了进一步了解网站或者通过收集信息（程序员注释可能存在敏感信息），我们都会尝试去查看html代码，而firebug就给我提供好了这个功能了，主要是比一般浏览器值得自带的调试工具更为好看。我们可以按F12打开界面选择HTMl进行查看
（注意：必须提前把firebug开启，当firebug为黄色的时候意味着已经开启。）

  
![image.png](https://image.3001.net/images/20180705/1530772390652.png!small)  

#### 2.定位元素对应的html代码为止

在渗透测试中我们经常需要定位某元素的位置，例如头像、表单等。但是代码太多，手工定位容易出错且时间成本较高，所以我们可以使用该插件进行快速定位。首先选中图标，然后单击你需要定位的元素即可。

![image.png](https://image.3001.net/images/20180705/15307723996082.png!small)![image.png](https://image.3001.net/images/20180705/15307724034330.png!small)

  

## 02.User-Agent Switcher

该插件用于改变浏览器User-Agent 。

  
![image.png](https://image.3001.net/images/20180705/1530772433959.png!small)  

### 1.更改User-Agent

我们尝试更改为安卓设备，刷新之后我们查看页面会变为手机端的界面。

![image.png](https://image.3001.net/images/20180705/15307724427077.png!small)![image.png](https://image.3001.net/images/20180705/15307724471899.png!small)

  

## 03.Hacker

黑客必备插件，辅助黑客完成SQL注入和XSS攻击已经表单提交等等。

  
![image.png](https://image.3001.net/images/20180705/15307724605190.png!small)  

### 1.网址相关功能

    
    
    load Url   把浏览器导航栏的网址导入右侧的文本框
    split Url  剪切网址
    Execute  执行访问
    Enable Post data 是否开启表单（用于填写表单数据）
    Enable Referrer  是否开启Referer

  
![image.png](https://image.3001.net/images/20180705/1530772470258.png!small)![image.png](https://image.3001.net/images/20180705/15307724777621.png!small)

![image.png](https://image.3001.net/images/20180705/15307724943065.png!small)  
![image.png](https://image.3001.net/images/20180705/15307724833688.png!small)

  

### 02.注入和XSS辅助功能

我只演示一部分功能，剩下的大家动手自己探索。

#### 1.mysql注入辅助

栗子:dvwa下注入获取用户名，数据库名，版本号信息。

步骤:获取链接-借助插件构造Payload-Execute（执行访问）

![image.png](https://image.3001.net/images/20180705/15307725164716.png!small)![image.png](https://image.3001.net/images/20180705/15307725196504.png!small)![image.png](https://image.3001.net/images/20180705/15307725248533.png!small)![image.png](https://image.3001.net/images/20180705/15307725297631.png!small)

  

#### 2.XSS辅助

我们可以借助其编码构造payload。

栗子:dvwa下low等级下的反射型xss payload构造。

步骤:获取地址-借助插件构造payload-执行访问。  

![image.png](https://image.3001.net/images/20180705/15307725395019.png!small)

![image.png](https://image.3001.net/images/20180705/15307725543019.png!small)![image.png](https://image.3001.net/images/20180705/15307725596955.png!small)![image.png](https://image.3001.net/images/20180705/15307725637846.png!small)

  

### 3.编码辅助

该插件可以辅助我们生成多种编码格式的字符。

  
![image.png](https://image.3001.net/images/20180705/15307725741257.png!small)

![image.png](https://image.3001.net/images/20180705/15307725791772.png!small)![image.png](https://image.3001.net/images/20180705/15307725852611.png!small)

  

## 4.HttpFox

监测和分析浏览器与web服务器之间的HTTP流量，可以当做一个抓包插件。(Ctril+shift+F2打开或者关闭，然后start开启监控)

![image.png](https://image.3001.net/images/20180705/1530772590496.png!small)![image.png](https://image.3001.net/images/20180705/15307725957734.png!small)![image.png](https://image.3001.net/images/20180705/15307726009745.png!small)

  

## 5：Live HTTP Header

用于查看一个网站的HTTP头信息的插件。（需要重启浏览器，注意有些插件需要重启浏览器才可以生效。）

  
![image.png](https://image.3001.net/images/20180705/1530772614875.png!small)![image.png](https://image.3001.net/images/20180705/1530772617687.png!small)![image.png](https://image.3001.net/images/20180705/153077262152.png!small)![image.png](https://image.3001.net/images/20180705/15307726242500.png!small)

  

## 6.ShowIP

在状态栏显示当前页的IP地址、主机名、ISP、国家和城市等信息。

  
![image.png](https://image.3001.net/images/20180705/15307726395839.png!small)![image.png](https://image.3001.net/images/20180705/153077264285.png!small)

  

## 7：XSS Me

XSS辅助型工具，前提一定要有表单这东西才有用。误差较大，优点就在于可以自定义payload他会自动进行编码检测。最好自己打开页面看，看到有弹框就确定存在XSS了，或者自己选择payload单独测试。毕竟插件是死的，人是活的。

栗子:dvwa low等级反射型xss检测 （最后没有检测出来，坑。）

使用步骤:右键打开插件-设置-执行

  
![image.png](https://image.3001.net/images/20180705/15307726539908.png!small)![image.png](https://image.3001.net/images/20180705/15307726569776.png!small)![image.png](https://image.3001.net/images/20180705/15307726611883.png!small)![image.png](https://image.3001.net/images/20180705/15307726647213.png!small)![image.png](https://image.3001.net/images/20180705/15307726704313.png!small)

  

## 8.SQL Inject Me

SQL注入辅助工具，payload比较少，感觉就是鸡肋。

  
![image.png](https://image.3001.net/images/20180705/15307726822604.png!small)![image.png](https://image.3001.net/images/20180705/1530772685318.png!small)![image.png](https://image.3001.net/images/20180705/15307726885746.png!small)

  

## 9.Javascript Deobfuscator

显示网页上运行的Javascript代码。感觉在研究DOM xss很有用。（按F12打开，记得先关了firebug）

  
![image.png](https://image.3001.net/images/20180705/15307726986014.png!small)![image.png](https://image.3001.net/images/20180705/15307727038964.png!small)

  

## 10：Modify Headers

修改HTTP请求头。

  
![image.png](https://image.3001.net/images/20180705/15307727131384.png!small)  

## 11\. FoxyProxy

代理工具，安装过后得重启。

演示如何设置Burp 8080代理。

![image.png](https://image.3001.net/images/20180705/15307727479151.png!small)

![image.png](https://image.3001.net/images/20180705/15307727219898.png!small)![image.png](https://image.3001.net/images/20180705/15307727242626.png!small)![image.png](https://image.3001.net/images/20180705/15307727283332.png!small)

  

## 12.FlagFox

可以在地址栏或状态栏上显示出当前网站所在国家的国旗，也有更多的其他功能，如：双击国旗可以实现WOT功能；鼠标中键点击是whois功能。当然用户可以在选项里设置快捷键实现诸如复制IP，维基百科查询等功能。

  
![image.png](https://image.3001.net/images/20180705/1530772767760.png!small)![image.png](https://image.3001.net/images/20180705/15307727723791.png!small)

  

## 13.Greasemonkey

greasemonkey 使你可以向任何网页添加DHTML语句(用户脚本)来改变它们的显示方式。就像CSS可以让你接管网页的样式，而用户脚本(User
Script)则可以让你轻易地控制网页设计与交互的任何方面。例如:

  * 使页面上显示的 URL 都成为可以直接点击进入的链接。

  * 增强网页实用性，使你经常访问的网站更符合你的习惯。

  * 绕过网站上经常出现的那些烦人的 Bug。

  
![image.png](https://image.3001.net/images/20180705/15307727841754.png!small)  

## 14.Domain Details

显示服务器类型、IP地址、域名注册信息等。

有问题大家可以留言哦~也欢迎大家到春秋论坛中来玩耍呢！
[>>>点击跳转](https://bbs.ichunqiu.com/portal.php?from=beef)

