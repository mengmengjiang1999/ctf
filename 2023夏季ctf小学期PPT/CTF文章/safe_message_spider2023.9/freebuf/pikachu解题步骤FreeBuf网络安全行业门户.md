# Burte Force

## 基于表单的暴力破解

1、打开题目，是个登陆框，可以尝试暴力破解

![在这里插入图片描述](https://image.3001.net/images/20221119/1668856642_6378bb423fda0f7efb8d4.png!small)

2、抓包爆破

![在这里插入图片描述](https://image.3001.net/images/20221119/1668856643_6378bb4303839824facbc.png!small)

![在这里插入图片描述](https://image.3001.net/images/20221119/1668856643_6378bb43d6f323c55e7bd.png!small)

## 验证码绕过(on server)

解题步骤

1、打开题目，发现这次添加了验证码，还是抓包

![在这里插入图片描述](https://image.3001.net/images/20221119/1668856644_6378bb44c1523b1000aba.png!small)

2、暴力破解发现`验证码无条件不刷新`，
**无条件不刷新是指在某一时间段内，无论登录失败多少次，只要不刷新页面，就可以无限次的使用同一个验证码来对一个或多个用户帐号进行暴力猜解** 。直接破解成功

![image.png](https://image.3001.net/images/20221122/1669109029_637c95259ce2681de5dc9.png!small)

## 验证码绕过(on client)

解题步骤

1、打开题目，发现有验证码  
![在这里插入图片描述](https://image.3001.net/images/20221119/1668856645_6378bb45b73bbcddde595.png!small)

2、

![image.png](https://image.3001.net/images/20221122/1669109052_637c953c6966b6ff064e4.png!small)

尝试点击登陆，发现弹窗是  
![image.png](https://image.3001.net/images/20221122/1669109083_637c955b7589ee8deb128.png!small)

而不是请输入用户名和密码， **说明这是前端检验** ，没有数据包的通过。

3、抓包爆破  
![image.png](https://image.3001.net/images/20221122/1669109102_637c956e648214d4a7703.png!small)

我们可以利用Response Modification中的`Remove all Javascript`功能，将所有JS移除

![image.png](https://image.3001.net/images/20221122/1669109123_637c9583484fc1c87f914.png!small)

然后爆破

![image.png](https://image.3001.net/images/20221122/1669109159_637c95a71b06d63adc028.png!small)

## token防爆破?

解题步骤

1、打开题目，照常抓包

![image.png](https://image.3001.net/images/20221122/1669109176_637c95b8535bdd42381a0.png!small)

发现多了token认证，那么我们可以换一种爆破方式

2、选择爆破方式

这里有两个爆破点，一个是`password`，一个是`token`  
![image.png](https://image.3001.net/images/20221122/1669109196_637c95cc02bdfb26139f5.png!small)

然后在option中选择

![image.png](https://image.3001.net/images/20221122/1669109220_637c95e4d622f42a3d489.png!small)

这里一定要填总是

在这个地方

![image.png](https://image.3001.net/images/20221122/1669109236_637c95f4b20137331998b.png!small)

添加token值

![image.png](https://image.3001.net/images/20221122/1669109334_637c9656c862aca130b9f.png!small)

在有效载荷内选择play类型为 **递归匹配**

然后把token值放在这里

![image.png](https://image.3001.net/images/20221122/1669109273_637c96192be23b11724a9.png!small)

然后再设置第一个爆破点，用普通列表以及密码本爆破即可

![image.png](https://image.3001.net/images/20221122/1669109289_637c9629a36ca20dcdeb6.png!small)

爆破成功

# XSS

## 反射型xss(get)

解题步骤

本题没有任何防护措施，可以直接做出来，playload如下

    
    
    <script>alert('xss')</script>
    

发现被截断了  
![image.png](https://image.3001.net/images/20221122/1669109467_637c96db52d3029484f97.png!small)

可以打开开发者工具，直接修改最大值。

![image.png](https://image.3001.net/images/20221122/1669109424_637c96b01136eceb1072e.png!small)

本题得解

## 反射性xss(post)

解题步骤

1、打开题目，发现是个登录框，登陆之后

![image.png](https://image.3001.net/images/20221122/1669109904_637c98909382f899636d0.png!small)

2、可以直接利用xss做，playload如下

    
    
    <script>alert(document.cookie)</script>
    

![image.png](https://image.3001.net/images/20221122/1669109924_637c98a4e88821cab0bcd.png!small)

![image.png](https://image.3001.net/images/20221122/1669109938_637c98b2167573c4b631d.png!small)

本题得解

## 存储型xss

解题步骤

1、打开题目，发现是个留言板，直接利用xss，playload如下

    
    
    <script>alert(document.cookie)</script>
    

![image.png](https://image.3001.net/images/20221122/1669109870_637c986ef247946459da9.png!small)

本题得解

2、然后在另外一个浏览器中来到本关页面，也出现了同样的弹框。说明存储型XSS能危害所有访问受影响页面的用户。

![image.png](https://image.3001.net/images/20221122/1669109878_637c9876e6a4a5683331e.png!small)

## DOM型xss

解题步骤

1、打开题目，尝试输入

![image.png](https://image.3001.net/images/20221122/1669109832_637c984826ffc420b59e0.png!small)

2、发现不可以，查看源码  
![image.png](https://image.3001.net/images/20221122/1669109839_637c984fbd0bcc646c992.png!small)

![image.png](https://image.3001.net/images/20221122/1669109847_637c9857f34fa6fa24c13.png!small)  
本题得解，这里要注意的是`onclick`函数只有点击才会生效，所以只有点击`what do you see`才会有弹窗。

## DOM型xss-x

解题步骤

1、打开题目，秉持有框就打的原则，尝试输入playload

    
    
    '><src='a' onmouseover="javascript:alert('Asson');">
    

![image.png](https://image.3001.net/images/20221122/1669109804_637c982c5356242ca864e.png!small)

2、根据源码

![image.png](https://image.3001.net/images/20221122/1669109767_637c980764100c0fab698.png!small)

只有点击这个`[有些费尽心机想要忘记的事情,后来真的就忘掉了`才会执行domxss，我们点击一下

![image.png](https://image.3001.net/images/20221122/1669109782_637c981667cbdb4ca8ba8.png!small)

本题得解

## xss盲打

解题步骤

1、打开xss之盲打，随意输入看看是什么效果。```发现并不任何反应  
![image.png](https://image.3001.net/images/20221122/1669109689_637c97b9abc46d74d813a.png!small)

2、所以我们输入的内容并不会在前端输出，看起来应该是存到了后台，也就是说可能只有管理员可以看。  
我们输入`<script>alert('xss')</script>`，设置一个弹窗，看看管理员在后台登陆上，是否会被x到。如果被x到这种场景就叫做盲打。

![image.png](https://image.3001.net/images/20221122/1669109708_637c97cc9522b60983562.png!small)  
![image.png](https://image.3001.net/images/20221122/1669109722_637c97da1e7a6665eea05.png!small)  
果然如此

## xss之过滤

解题步骤

1、打开题目，秉持有框就打的原则，输入playload

2、看到过滤，就先试了下<>和script都没被过滤，但两者合在一起`<script>`就被过滤了。我们可以利用大小写绕过`<Script>alert('xss')</SCript>)`

![在这里插入图片描述](https://image.3001.net/images/20221119/1668856651_6378bb4bc702ed56f9fc0.png!small)

## xss之htmlspecialchars

在做这道题之前我们必须知道什么是htmlspecialchars

    
    
    htmlspecialchars()是PHP里面把预定义的字符转换为HTML实体的函数
    预定义的字符是
    & 成为 &ampamp
    " 成为 &ampquot
    ' 成为 '
    < 成为 &amplt
    > 成为 &ampgt
    可用引号类型
    ENT_COMPAT：默认，仅编码双引号
    ENT_QUOTES：编码双引号和单引号
    ENT_NOQUOTES：不编码任何引号
    

但是，有一个非常重要的点就是htmlspecialchars默认不过滤`'`，这样就好办了，playload如下

    
    
    ' onclick = ' alert(1)
    

![](https://image.3001.net/images/20221119/1668856652_6378bb4c720d602248568.png!small)

## xss之href输出

解题步骤

1、打开题目，尝试输入，发现输进去的东西在href标签中

![在这里插入图片描述](https://image.3001.net/images/20221119/1668856653_6378bb4d294ed97e34689.png!small)

2、这里要用到js协议的知识

> javascript:这个特殊的协议类型声明了URL的主体是任意的javascript代码，它由javascript的解释器运行

3、playload如下

    
    
    javascript:alert(1)
    

![在这里插入图片描述](https://image.3001.net/images/20221119/1668856653_6378bb4dd14fc8da8e031.png!small)

## xss之js输出

解题步骤

1、打开题目，照例输入，没有反应

2、查看源码才发现，我们的输入被放到了`<script>`标签内

![在这里插入图片描述](https://image.3001.net/images/20221119/1668856654_6378bb4e9240a6e3c0de8.png!small)

3、我们尝试闭合，playload如下

    
    
    </script><script>alert(1)</script><script>
    

成功

![在这里插入图片描述](https://image.3001.net/images/20221119/1668856655_6378bb4f5e24761d49631.png!small)

# XXE

在开始之前我必须介绍一下什么是XXE。

一、基础知识

1、什么是XXE

> XXE -“xml external entity injection"既"xml外部实体注入漏洞”。  
> 概括一下就是" **攻击者通过向服务器注入指定的xml实体内容,从而让服务器按照指定的配置进行执行,导致问题"**  
>  **也就是说服务端接收和解析了来自用户端的xml数据,而又没有做严格的安全控制,从而导致xml外部实体注入** 。

2、什么是xml

> XML 指可扩展标记语言（EXtensible Markup Language）。  
>  **XML 是一种很像HTML的标记语言，但它不是HTML的替代品，HTML聚焦于数据的外观，而XML聚焦于数据的传输** 。  
> XML 的设计宗旨是传输数据，而不是显示数据。  
> XML 标签没有被预定义。您需要自行定义标签。  
> XML 被设计为具有自我描述性。  
> XML 是 W3C 的推荐标准。  
> 简而言之它就是个存储数据的  
> XML 不会做任何事情。XML 被设计用来结构化、存储以及传输信息。

更多知识大家可以看这篇文章[XXE漏洞利用技巧：从XML到远程代码执行]([XXE漏洞利用技巧：从XML到远程代码执行 -FreeBuf网络安全行业门户](https://www.freebuf.com/articles/web/177979.html))。

二、解题步骤

1、随便输入个包含命名实体（内部实体）的xml数据

    
    
    <?xml version = "1.0"?>
    <!DOCTYPE note [
        <!ENTITY hacker "XXE">
    ]>
    <name>&amphacker</name>
    

![在这里插入图片描述](https://image.3001.net/images/20221119/1668856656_6378bb5091c9cdf766af1.png!small)

成功回显

2、接下来使用外部实体构造playload

    
    
    <?xml version="1.0"  encoding="UTF-8"?> 
    <!DOCTYPE name [
    	<!ENTITY xxe SYSTEM "file:///E:/phpStudy/PHPTutorial/WWW/i/pikachu/password.txt">
    ]> 
    <name>&ampxxe</name>
    

![在这里插入图片描述](https://image.3001.net/images/20221119/1668856657_6378bb515e15bc3ba167f.png!small)

当然XXE不止有这些用途，详细可见[pikachu XXE (XML外部实体注入)]([(74条消息) pikachu XXE
(XML外部实体注入)（皮卡丘漏洞平台通关系列）_仙女象的博客-CSDN博客_pikaqiu漏洞平台](https://blog.csdn.net/elephantxiang/article/details/113812331))

# CSRF

## CSRF(get)

解题步骤

1、抓包  
![在这里插入图片描述](https://image.3001.net/images/20221119/1668856658_6378bb523698e92bef16d.png!small)

2、生成CSRF POC  
![在这里插入图片描述](https://image.3001.net/images/20221119/1668856659_6378bb531278b1603e294.png!small)

3、访问即可

## CSRF(post)

解题步骤

本题修改了传参方式，将`GET`修改为`POST`

![image.png](https://image.3001.net/images/20221122/1669109646_637c978e3bed02f0f087e.png!small)

做法与上一题相同，在此就不多做赘述。

## CSRF(token）

本题添加了token，无法修改

CSRF 攻击之所以能够成功，是因为黑客可以完全伪造用户的请求，该请求中所有的用户验证信息都是存在于 cookie
中，因此黑客可以在不知道这些验证信息的情况下直接利用用户自己的 cookie 来通过安全验证。要抵御
CSRF，关键在于在请求中放入黑客所不能伪造的信息，并且该信息不存在于 cookie 之中。 **可以在 HTTP 请求中以参数的形式加入一个随机产生的
token** ，并在服务器端建立一个拦截器来验证这个 token，如果请求中没有 token 或者 token 内容不正确，则认为可能是 CSRF
攻击而拒绝该请求。

# PHP反序列化

一、基础知识

1、什么是序列化与反序列化：序列化是将对象转化成字符串，其目的是方便传输；  
![image.png](https://image.3001.net/images/20221122/1669109599_637c975f70dd86ae0f38e.png!small)

反序列化就是把被序列化的字符串还原为对象,然后在接下来的代码中继续使用。

2、具体代码

 **序列化**

    
    
    <?php
    class S{
        public $test ="pikachu";
    }
    $s=new S();
    echo serialize($s);
    ?>
    

![image.png](https://image.3001.net/images/20221122/1669109621_637c977591424cdb8c286.png!small)

二、解题步骤

playload：`O:1:"S":1:{s:4:"test";s:29:"<script>alert('xss')</script>";}`，会出现弹窗。  
![image.png](https://image.3001.net/images/20221122/1669109569_637c9741eaf2b9e27e639.png!small)

# RCE

## exec "ping"

解题步骤

1、打开题目，发现要ping地址  
![image.png](https://image.3001.net/images/20221122/1669109548_637c972c075b730f0596d.png!small)

随便ping一个

![image.png](https://image.3001.net/images/20221122/1669109523_637c97138a319e1b05322.png!small)

可以ping通

2、尝试playload

    
    
    127.0.0.1 | ipconfig
    

可以直接解出  
![image.png](https://image.3001.net/images/20221122/1669109506_637c97025a5399d816f22.png!small)

到这里还没有结束，我们可以研究一下漏洞的起因，查看源码

    
    
    $result.=shell_exec('ping '.$ip);//直接将变量拼接进来，没做处理
        }else {
            $result.=shell_exec('ping -c 4 '.$ip);
        }
    

`shell_exec()`函数通过 shell 执行命令并将完整的输出以字符串的方式返回，在没有做处理的情况下直接拼接

