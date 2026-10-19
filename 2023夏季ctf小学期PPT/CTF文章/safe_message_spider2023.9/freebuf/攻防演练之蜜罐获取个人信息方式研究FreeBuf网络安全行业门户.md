## 前言

随着攻防演练的不断开展，为了更好的进行溯源，很多企业都使用了蜜罐技术。蜜罐是一种欺骗的技术，能够详细记录攻击者的攻击步骤，消耗攻击者的精力，并且可能获取到攻击者的个人信息。

一直都很奇怪 **蜜罐是如何获取到个人的敏感信息的** ，因此找了一些商业和开源的蜜罐，看他们是通过什么方式来收集个人信息的。

![1690784609_64c75361b988888e75795.png!small?1690784610069](https://image.3001.net/images/20230731/1690784609_64c75361b988888e75795.png!small?1690784610069)

我们知道蜜罐可以模拟各种服务，如web服务，mysql服务，redis服务等等。在测试过程中发现，蜜罐主要是通过web蜜罐和mysql蜜罐来获取个人信息。

## web站点蜜罐

web蜜罐收集个人信息使用的技术主要有两种，分别是JSONP劫持和XSS。

### JSONP劫持获取敏感信息

JSONP是JSON with padding（填充式JSON或参数式JSON），是一种为了跨域获取资源而产生的一种技术手段。这是一种非官方的协议。

 **JSONP实现跨域的原理**

同源策略限制了不同源的站点通过ajax获取信息，但是web页面调用js文件则不受跨域的影响并且凡是拥有src属性的标签都可以跨域请求，如script,img等标签。JSONP正是利用这种原理去实现了跨域请求。

 **JSONP劫持**

从JSONP的原理中可以看出这种方式实现了数据的跨域访问，如果网站B对网站A的JSONP请求没有进行安全检查直接返回数据，则网站B 便存在JSONP
漏洞，网站A 利用JSONP漏洞能够获取用户在网站B上的数据。

这种漏洞与CSRF非常相似，只不过CSRF只是发送数据去达到一定的目的，而JSONP劫持是为了获取返回的敏感数据。

![1690784782_64c7540e4e6d8f12b62d9.png!small?1690784783037](https://image.3001.net/images/20230731/1690784782_64c7540e4e6d8f12b62d9.png!small?1690784783037)

 **实际利用**

访问蜜罐，会发现它发出了很多的数据包去请求不同的网站的接口，其中一个如下：

![1690784834_64c754428f5d6464a0121.png!small?1690784835230](https://image.3001.net/images/20230731/1690784834_64c754428f5d6464a0121.png!small?1690784835230)

如果你处于登录的状态，那么看看你可以获取到的信息

![1690784846_64c7544e4735eac959d25.png!small?1690784846874](https://image.3001.net/images/20230731/1690784846_64c7544e4735eac959d25.png!small?1690784846874)

上面就是通过JSONP的去获取个人信息的方式。首先找到一个网站中的JSONP接口返回了敏感信息，将该接口放到自己蜜罐网站中，等待攻击者点击，如果攻击者点击以后，并且其登录该网站，则可以获取到该网站的敏感信息。

### XSS漏洞获取敏感信息

同样，如果目标网站存在XSS漏洞，也可以被利用获取敏感信息。将存在xss的url放入蜜罐web页面中，攻击者点击以后就会自动去请求存在xss漏洞的网址，从而触发xss漏洞，获取用户的敏感信息。这种方式与我们平常使用xss漏洞很相似，这里不在多说。

目前，很多企业外部都有waf进行防护，因此xss漏洞利用就会很困难，这种方式用的比较少。

## mysql蜜罐

mysql有一个功能是可以读取本地的文件存储到数据库中，该函数是local data local
infile。mysql蜜罐获取个人敏感信息也是通过这种特性完成的。

local data local infile函数用于高速地从一个文本中读取，并写入一个表中。文件名称必须为一个文字字符串。Local data
infile是select…into outfile地相对语句。把表的数据备份到文件中使用select…into
outfile，从备份文件回复表数据，使用load data infile。

这个功能默认关闭，查看是否开启：

    
    
    show global variables like 'local_infile';
    set global local_infile=1; #开启

### 原理

mysql客户端向Server发起查询后，Server会返回一个Response
TABULAR的响应包。而如果在这个数据包中指定文件路径，就可以读取Client相应的文件。实际上Server可以在回复任何Client端的请求时返回Response
TABULAR响应包，而不仅仅是在Client发起Load data local infile后。

根据mysql的这种机制，当攻击者访问mysql蜜罐时，我们可以发送一个包含文件路径的响应包去读取客户端的文件。

### 利用

 **读取微信号**

win系统下，读取手机号和微信ID的方法（默认常见微信文件路径）

我们可以下面的步骤来获取用户的微信号

1）通过C:/Windows/PFRO.log获取windows用户名

2）通过C:/Users/用户名/Documents/WeChat Files/All Users/config/config.data获取wxid

3）通过C:/Users/用户名/Documents/WeChat Files/wx_id/config/AccInfo.dat获取微信号、手机号

 **读取chrome的登录数据**

读取chrome的login data，虽然无法解密出密码，但是还是可以获取到对方的一些账号

C:/Users/' + username + '/AppData/Local/Google/Chrome/User Data/Default/Login
Data

 **chrome的历史记录**

我们还可以读取chrome的历史记录

C:/Users/' + username + '/AppData/Local/Google/Chrome/User
Data/Default/History

### 应用

开源蜜罐系统hfish中的mysql蜜罐就利用了这种方式来获取攻击者的文件，如下首先在蜜罐中设置要读取的文件。

![1690785622_64c7575673bded03392d8.png!small?1690785622939](https://image.3001.net/images/20230731/1690785622_64c7575673bded03392d8.png!small?1690785622939)

然后，攻击者访问该蜜罐时，可以读取到配置的文件

![1690785638_64c757661c31af5be8a75.png!small?1690785638836](https://image.3001.net/images/20230731/1690785638_64c757661c31af5be8a75.png!small?1690785638836)

## 总结

蜜罐获取个人信息使用的一般是上面两种方式，灵活的运用蜜罐可以帮助我们溯源到攻击者。

 **由于本人水平有限，文章中可能会出现一些错误，欢迎各位大佬指正，感激不尽。如果有什么好的想法也欢迎交流，谢谢大家了~~**

