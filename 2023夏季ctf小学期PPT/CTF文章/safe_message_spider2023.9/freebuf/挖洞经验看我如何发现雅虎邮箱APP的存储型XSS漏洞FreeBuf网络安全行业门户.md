![看我如何发现雅虎邮箱APP的存储型XSS漏洞](https://image.3001.net/images/20180911/1536648513_5b976541b831a.jpg!small)**今天我要分享的是参与雅虎（Yahoo!）漏洞众测项目发现的一个关于雅虎邮箱
iOS应用的漏洞，最终，凭借该漏洞，我进入了雅虎安全名人堂并获得了$3500美金奖励。**

## 漏洞情况

我测试的对象是 Yahoo! Mail iOS
APP应用，也就是雅虎邮箱的iOS版本，在该APP应用程序的xml文件中存在一个存储型XSS漏洞。攻击者可以利用XML特性构造任意HTML/Javascript代码嵌入邮件，在该APP用户打开邮件时，都可以实现这种任意代码渲染呈现，极端点来说，利用XML的实体扩展攻击，可以形成DoS攻击，造成APP服务崩溃。

> XML实体扩展攻击：XML Entity
> Expansion实现，通过在XML的DOCTYPE中创建自定义实体的定义实现，比如，这种定义可以在内存中生成一个比XML的原始允许大小大出很多的XML结构，用它来使这种攻击得以耗尽网络服务器正常有效运行的必需内存资源。

## 漏洞分析

### 漏洞初报

在任意的雅虎邮箱登录网页或客户端中登录进入你的雅虎邮箱，然后上传以下样式的一个xml文件作为邮件附件，之后，把这封带以下 yahoo-xss.xml
附件的邮件，发送到你自己的雅虎邮箱或另一雅虎测试邮箱中去。

    
    
    <?xml version=”1.0″ encoding=”utf-8″?>
    <svg xmlns=”http://www.w3.org/2000/svg”>
    <script>prompt(document.location)</script>
    </svg>

用雅虎邮箱iOS客户端（Yahoo! Mail iOS APP），进入你的收件测试雅虎邮箱，查看 yahoo-xss.xml
附件，打开它，看看是否有XSS反应。结果是当然有的，会吓了你一跳。如下：

![看我如何发现雅虎邮箱APP的存储型XSS漏洞](https://image.3001.net/images/20180911/1536647698_5b97621251be0.png!small)注意：我也搞不懂啥原因，雅虎邮箱iOS应用中的XML渲染机制非常怪异危险。如果你收到包含以上yahoo-xss.xml 附件的多个附件，那么，即使你打开其它附件的时候，这个 yahoo-xss.xml 触发的存储型XSS都会解析跳出。

我匆匆忙忙地上报了这个漏洞，以下是雅虎安全团队人员在HackerOne上给我的回应：

![看我如何发现雅虎邮箱APP的存储型XSS漏洞](https://image.3001.net/images/20180911/1536647739_5b97623be2feb.png!small)到了这步，接下来我要做的就是想办法来最大化利用这个漏洞，看看能对雅虎邮箱iOS应用形成什么比较坏的安全威胁和影响。但无奈我一时半会也没什么头绪，只好先放一放。

### 漏洞续报

后来有一天，我突然想到了一种提升漏洞利用且安全无害的方法，那就是我可以用HTTP请求，像“GET”方式一样，尝试对本地APP客户端资源进行获取！BingGo！我一试，真成了！我可以用这种方法获取到雅虎邮箱iOS应用的整个缓存数据，其中包括用户cookie、通讯录列表、邮件内容等等。

## 漏洞利用复现

首先，在任意雅虎邮箱网页或客户端中登录你的雅虎邮箱账户，上传一个如下包含如下代码的XML文件，然后，把它作为附件发送到你的另外一个测试雅虎邮箱中（受害者邮箱）。

![看我如何发现雅虎邮箱APP的存储型XSS漏洞](https://image.3001.net/images/20180911/1536647806_5b97627e9e988.png!small)在你的雅虎测试邮箱中打开这个收到的XML附件，基于上面我提到的那个“怪异”的XML解析原因，这里可以想像一种情况：当攻击者向你发送了一个PPT文档，但在附件中也附加了以上那个可以触发XSS的XML文件，那么，当你打开收到的PPT文档时，这个XML文件也就会同时触发XSS反应。也就是说，无论你有多少个附件（包括视频附件），只要包含以上那个XML附件，你打开其它任何一个附件，都会奇怪地触发XML文件中XSS漏洞。

利用该漏洞，构造key.xml，我可以获取受害者邮箱中包括发送者、接收者和联系人在内的通讯录信息。在XML附件代码中，XSS漏洞会首先显示客户端的浏览器版本信息，然后是定位文件位置，再之后是获取邮件列表信息（这里看网速，估计需要30秒左右的时间）。之后，点击key.xml的OK之后，邮件列表信息就通过GET方式回传给攻击者了，像下图这样。我是在内部局域网中做的测试，我的Server接收端用nc
-lvvv 8090开启了8090端口监听：

![看我如何发现雅虎邮箱APP的存储型XSS漏洞](https://image.3001.net/images/20180911/1536647835_5b97629b68fe9.png!small)利用该漏洞，构造cachedbpost.xml，我可以获取受害者的Cookie信息。点击cachedbpost.xml的OK之后，整个Cache.db文件就会通过POST方式回传给攻击者，如下图所示。我在内部局域网中做的测试，我的Server接收端用nnc
-lvvv 8090 > yahoo.db命令开启了8090端口监听，并把Cache.dbd存储为yahoo.db：

![看我如何发现雅虎邮箱APP的存储型XSS漏洞](https://image.3001.net/images/20180911/1536647856_5b9762b08e59f.png!small)收到完整的Cache.db文件之后，我们把其中的标题头内容过滤，用以下命令检索形成完整的受害者cookie信息：

> strings yahoo.db | grep -i Cookie -A 10 -B 5

另外，还可以按http服务端来进行枚举，形成对特定网站的请求cookie：

> strings yahoo.db | grep -i https

雅虎安全团队工作人员接收到该漏洞后，迅速进行了分类、修复和处置。

##
![看我如何发现雅虎邮箱APP的存储型XSS漏洞](https://image.3001.net/images/20180911/1536647906_5b9762e21ca9b.png!small)![看我如何发现雅虎邮箱APP的存储型XSS漏洞](https://image.3001.net/images/20180911/1536647913_5b9762e9c99a5.png!small)漏洞影响

任何攻击者可以利用该漏洞，构造特定的XML文件发送给任何用户，进而获取到受害者用户邮箱中包括发送者、接收者、Cookie和联系人在内的敏感信息。

> 我的测试环境：
>
> iPhone 6 – iOS v11.2.5.
>
> 受影响iOS客户端版本:
>
> Yahoo! Mail app v4.XX.X (XXXXX)

 ***参考来源：[omespino](http://omespino.com/write-up-lovestory-from-closed-as-informative-to-xx00-usd-in-yahoo-ios-mail-app/)，clouds编译，转载请注明来自FreeBuf.COM **  

