## **前记**

今天闲来无事，来到漏洞盒子发现没啥好挖的，就跑去野战了:smile:突然灵机一动，想到了我以前最喜欢的app,作业帮，想挖app是没可能了，毕竟我这么菜，对吧！所以就找到了官网，用目录扫描器扫了一遍，一个个的点开链接，查找漏洞，发现了个会话令牌存在泄漏，(仙哥说不能发链接哦)

跑去问群里的大佬，结果都说我不要再浪费审核的时间了，

我不死心，功夫不负有心人，我终于又找到了个漏洞，就是作业帮的cors的配置存在问题，

## 漏洞细节

    
    
    <!-- wp:paragraph -->
    <p>Access-Control-Allow-Origin：http : //2PZaB9f2.com</p>
    <!-- /wp:paragraph -->
    
    <!-- wp:paragraph -->
    <p>Access-Control-Allow-Credentials：true</p>
    <!-- /wp:paragraph -->
    
    <!-- wp:paragraph -->
    <p>再给你们来个http请求，方便各位大佬的操作，</p>
    <!-- /wp:paragraph -->
    
    <!-- wp:paragraph -->
    <p>GET/修哥说不能发链接哦HTTP/1.1Pragma:no-cacheCache-Control:no-cacheReferer:https:修哥说不能发链接哦Host:www.zybang.comConnection:Keep-aliveAccept-Encoding:gzip,deflateUser-Agent:已隐藏Origin:http://2PZaB9f2.com</p>
    <!-- /wp:paragraph -->

## 漏洞url（修哥说不能发链接哦）

可能有些大佬不知道cors，容我给大佬们科普下，

中文名叫跨域资源共享

CORS（Cross-origin resource sharing
），是指通过XMLHttpRequest的ajax方式访问其他域名下资源，而不是在A域名的页面上点击打开一个B域名的页面。引入不同域上的js脚本文件也是没用问题的。出于安全考虑，跨域请求不能访问document.cookie对象。

CORS技术允许跨域访问多种资源，比如javascript，字体文件等

——来源百度百科，因为这个我只是初略学过，大佬勿喷

说到这里就不得不提一下同源策略了

## 同源策略

同源就是域名，协议，端口相同

同源策略与浏览器的关系就像是你和你女朋友的一个约定，它是浏览器最核心也最基本的安全功能，如果缺少了同源策略，则浏览器的正常功能可能都会受到影响。有哪些危害呢？我再给大佬们说细一点

1.无法读取cookie、localStorage、indexDB

2.DOM无法获得

3.ajax请求无法发送

可以说 Web 是构建在同源策略基础之上的，浏览器只是针对同源策略的一种实现。

### 一.DOM 同源策略：

禁止对不同源页面 DOM 进行操作。这里主要场景是 iframe 跨域的情况，不同域名的 iframe 是限制互相访问的。

iframe是什么？

就是html，如果连这都不懂，我也不想说你了

它是一个HTML内联框架元素，它能够将另一个HTML页面嵌入到当前页面中。

DOM又是啥?

文档对象模型，是 HTML 和 XML 文档的编程接口。

HTML DOM 定义了访问和操作 HTML 文档的标准方法。

表示嵌套的browsing context。它能够将另一个HTML页面嵌入到当前页面中。

### 二.XMLHttpRequest 同源策略：

禁止使用 XHR 对象向不同源的服务器地址发起 HTTP 请求。

XHR是啥？

就是 XMLHttpRequest 对象。

也就是ajax功能实现所依赖的对象

语法：

1.Access-Control-Allow-Origin响应头

的 Access-Control-Allow-Origin 报头指示是否一个资源可以被共享的基于通过返回的值Origin在响应请求头，“*”，或“空”。

规则：

Access-Control-Allow-Origin = “Access-Control-Allow-Origin” “:” origin-list-or-null | “*”

实际上， origin-list-or-null生产受到更多限制。不是允许使用空格分隔的起源列表 ，它要么是单个起源，要么是字符串“ null”。

2.Access-Control-Allow-Credentials响应头

的 Access-Control-Allow-Credentials
报头指示是否请求的响应可以在被暴露省略凭证标志未设置。当对预检请求的响应的一部分时，表明 实际请求可以包括用户凭据。

规则：

Access-Control-Allow-Credentials: “Access-Control-Allow-Credentials” “:” true

true: %x74.72.75.65 ; “true”，区分大小写

3.Access-Control-Expose-Headers响应头

的 Access-Control-Expose-Headers 报头指示该标头是安全，以暴露到CORS API规范的API。

规则：

Access-Control-Expose-Headers = “Access-Control-Expose-Headers” “:” #field-name

4.Access-Control-Max-Age响应头

的 Access-Control-Max-Age 报头指示多长时间的结果预检请求 可以在被缓存预检结果缓存。规则：

Access-Control-Max-Age = “Access-Control-Max-Age” “:” delta-seconds

5.Access-Control-Allow-Methods响应标题

的 Access-Control-Allow-Methods 报头指示，作为响应于一部分 预检要求，可在过程中使用的方法 的实际请求。

在Allow头是不相关的CORS协议的目的。

规则：

Access-Control-Allow-Methods: “Access-Control-Allow-Methods” “:” #Method

6.Access-Control-Allow-Headers响应头

的 Access-Control-Allow-Headers 报头指示，作为响应于一部分 预检请求，该头字段名称可以在过程中使用实际的请求。

规则：

Access-Control-Allow-Headers: “Access-Control-Allow-Headers” “:” #field-name

7.Origin请求头

的 Origin 报头指示了跨来源请求或 预检请求从始发。

8.Access-Control-Request-Method请求头

的 Access-Control-Request-Method 报头指示该方法将在使用 实际的请求作为一部分 预检请求。

规则：

Access-Control-Request-Method: “Access-Control-Request-Method” “:” Method

9.Access-Control-Request-Headers请求头

的 Access-Control-Request-Headers 报头指示哪些报头将在使用 实际的请求作为一部分 预检请求。

规则：

Access-Control-Request-Headers: “Access-Control-Request-Headers” “:” #field-name

简单的跨域请求简单的跨域请求:

应用发出请求的步骤，并在发出请求时遵守下面的 请求规则。

如果未设置手动重定向标志，并且响应的HTTP状态代码为301、302、303、307或308

应用重定向步骤。

如果最终用户取消请求应用中止步骤。如果出现网络错误

如果发生DNS错误，TLS协商失败或其他类型的网络错误，请应用网络错误步骤。不要请求任何类型的最终用户交互。这不包括指示某种错误类型的HTTP响应，例如HTTP状态代码410。除此以外执行资源共享检查。如果返回失败，请应用网络错误步骤。否则，如果返回pass，则终止此算法并将
跨域请求状态设置为success。实际不终止请求。

大佬们可能又要问了，扯了半天有啥风险啊？

默认情况下，CORS机制不读取cookie值，即跨域访问时没有带上cookie，当需要跨域访问带cookie时，需要设置另一个文件头，Access-Control-Allow-Credentials，值为true。该选项设定了是否允许跨域请求带cookie。当设定为true后，对于XMLHttpRequest还需要设定withCredentials为true，在Jquery中为xhrFields:
{withCredentials: true}

一旦允许了带cookie的跨域访问，那么遭到CSRF攻击的概率大大的增加了，比如之前的假设a.html页面内有一段恶意的js，它每隔1分钟去跨域请求用户b页面，并将请求后的数据偷偷的存入自己的数据库内。假设b页面需在要用户登录的情况下，可以请求到很多机密数据，比如xingyong卡号等，那当用户打开a页面后，在非授意的情况下，获取到b面值的内容，引发泄密。

简单的说就是任何网站都可以发出使用用户凭据发出的请求，并读取对这些请求的响应。

## warning：

网站漏洞已提交，请勿将本文章用于非法用途，出了责任与本人概无关系！

