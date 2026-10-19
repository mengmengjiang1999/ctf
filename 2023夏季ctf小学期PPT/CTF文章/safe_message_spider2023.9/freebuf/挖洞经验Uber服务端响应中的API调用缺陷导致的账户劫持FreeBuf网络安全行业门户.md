***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![Uber服务端响应中的API调用缺陷导致的账户劫持](https://image.3001.net/images/20190419/1555648826_5cb9513a2d082.jpg!small)
**今天分享的writeup是香港白帽Ron Chan
(@ngalongc)发现的一个关于Uber网站的漏洞，他通过分析Uber的微服务架构和其中的API调用机制，利用其中的服务端响应缺陷，能以SSRF和目录遍历（PAth
Traversal）方式获取到服务端为用户分配的token信息，从而实现对用户的账户劫持。虽然整个漏洞利用构造链亮点不多，但“Old but
GOLD”，姜还是老的辣，漏洞还是老的好。**

## Uber微服务架构

****微服务英文名称Microservice，Microservice架构模式就是将整个Web应用组织为一系列小的Web服务。这些小的Web服务可以独立地编译及部署，并通过各自暴露的API接口相互通讯。它们彼此相互协作，作为一个整体为用户提供功能，也可以独立地进行修改和扩容。

Uber的Web应用服务体系是基于[很多微服务架构](http://wordpress.redirectingat.com/?id=725X1342&xcust=8982&xs=1&isjs=1&url=https%3A%2F%2Feng.uber.com%2Ftag%2Fmicroservice%2F&xguid=c988db3a756cb87dd663811cf6e0e304&xuuid=b7a6af824b44acb8edcd7587a0929cbd&xsessid=&xcreo=0&xed=0&sref=https%3A%2F%2Fngailong.wordpress.com%2F2019%2F04%2F07%2Fold-but-gold-dot-dot-slash-to-get-the-flag-uber-microservice%2F&pref=https%3A%2F%2Fblog.intigriti.com%2F2019%2F04%2F16%2Fbug-bytes-14-better-exfiltration-via-html-injection-by-fransrosen-dell-kace-k1000-rce-by-mrtuxracer-burpfeed%2F&xtz=-480&jv=13.14.0-stackpath&bv=2.5.1)部署的，由于微服务中会涉及到大量的REST模式，因此，在与各种Uber应用的交互过程中，Uber服务端难免会调用到一些REST
API接口。就比如说，你要查看某位司机的状态信息，Uber后端会涉及到类似如下的REST API接口调用：

>
> [https://localhost:1234/partner/PARTNER_UUID/trips?from=2018-01-01&to=2019-01-01](https://localhost:1234/partner/PARTNER_UUID/trips?from=2018-01-01&to=2019-01-01)

## 从请求响应中发现端倪

设计理论上来说，显然，这种调用都是在Web应用后端（Backend）来执行实现的，因为在调用过程中，其内部的微服务架构没有针对IDOR攻击的安全检查权限。所以，矛盾点来了，如果这类API调用都是以预定的path/variables/host方式进行的，而且，这些调用是用户无法控制的，那么，Web应用后端（Backend）设置的身份验证措施又有何用呢？

用户确实不能控制这类API调用吗？我觉得这里要打个问号。2018年初，我在Uber网站partners.uber.com下发现了一个有意思的路径（Endpoint），它用来查询读取Uber司机的服务状态，其前端请求链接如下：

> <https://partners.uber.com/p3/money/statements/view/current>  
>

该查询链接涉及的请求看不出什么问题，但服务端对其的响应消息中却存在一些有意思的参数，如下：

    
    
    {
      "request": {
        "uri": {
          "protocol": "http:",
          "slashes": true,
          "auth": null,
          "host": "127.0.0.1:123",
          "port": "123",
          "hostname": "127.0.0.1",
          "hash": null,
          "search": "?earnings_structure_type=&locale=en&user_id=xxxxx",
          "query": "earnings_structure_type=&locale=en&user_id=xxxxx",
          "pathname": "/v1/partners/xxxxx/statements/current",
          "path": "/v1/partners/xxxxxx/statements/current?earnings_structure_type=&locale=en&user_id=xxxxx",
          "href": "http://127.0.0.1:123/v1/partners/xxxxx/statements/current?earnings_structure_type=&locale=en&user_id=xxxxxx"
        },
       "token":"ACCESS_TOKEN_OF_USER",
    ....

从上述响应消息可看出，涉及该查询链接的后端API GET请求调用如下所示：  

>
> [http://127.0.0.1:123/v1/partners/xxxx/statements/current?earnings_structure_type=&locale=en&user_id=xxxx](http://127.0.0.1:123/v1/partners/xxxx/statements/current?earnings_structure_type=&locale=en&user_id=xxxx)

这是一个典型的后端REST API调用。

仔细观察上述响应消息，可见其中的API调用对current的请求来自于原始前端请求链接：
**<https://partners.uber.com/p3/money/statements/view/current>** ，而且还会把
**current** 添加到 "pathname"参数的结尾，形成 " **/v1/partners/xxxxx/statements/current**
" 。另外，调用中还包含其它查询相关参数，如涉及收入结构类型的earnings_structure_type，以及查询区域locale=en等。  

上述响应消息的有意思之处在于，第一，其中包含了应用用户的访问token键值对 - **"token":"ACCESS_TOKEN_OF_USER"**
，这里还曾出现过一个Uber第三方应用的token撤销漏洞；第二，在查询请求request中缺乏验证调用者身份的 **X-Auth-Token**
头，但是，在服务端响应消息中竟然还返回了用户的访问token！  

## 构造漏洞利用

这样来看，在请求中，如果我们能以某种方式，通过把我当前账户相关的用户ID数值（user_id或my_user_uuid）
更改为其他用户对应的用户ID数值（victim_id或victim_uuid），就可能实现对请求调用的操纵。之后，服务端通过这个其他用户的用户ID数值，会响应回来与其对应的账户token，那么，有了这个token，我们就能实现对该用户的账号劫持了。

基于以上思路，需要找到一个具备以下条件的前端请求路径（Endpoint）:

> 能从其GET请求中传递任意相关参数；
>
> 能从其GET请求中传递经过编码转义的字符，防止一些不必要的字符解析和参数传递错误，如 %23 或 # 会截断URL中的参数截断；
>
> 服务端对GET请求能完整响应并可读。

## 漏洞实现

最终，经过查找分析，我发现了满足以上测试条件的一个前端请求路径（Endpoint）:

>
> <https://partners.uber.com/p3/money/statements/view/4cb88fb1-d3fa-3a10-e3b5-ceef8ca71faa>

Uber服务端对这个请求路径的响应包含了如下的API GET请求调用：

    
    
    "href": "http://127.0.0.1:123/v1/statements/4cb88fb1-d3fa-3a10-e3b5-ceef8ca71faa?earnings_structure_type=&locale=en&statement_uuid=4cb88fb1-d3fa-3a10-e3b5-ceef8ca71faa&user_id=your_user_id"

我觉得其中的uuid - 4cb88fb1-d3fa-3a10-e3b5-ceef8ca71faa，是用来在API
GET请求调用中传递给path和query参数的，所以，我对原始的前端请求路径（Endpoint）做了如下修改：

>
> <https://partners.uber.com/p3/money/statements/view/4cb88fb1-d3fa-3a10-e3b5-ceef8ca71faa%2f..%2f4cb88fb1-d3fa-3a10-e3b5-ceef8ca71faa>

“/” 经url编码后为%2f，哪想到，上述查询链接的请求发起后，服务端响应的消息竟然和修改之前是一样的！那么，也就间接说明可用
“../”来对目录路径进行转义编码，还能用它来进行目录遍历。接下来，我们可以用 .. /
这种目录遍历方式，构造直达服务端根目录的前端请求链接，然后，到达根目录后，可以构造请求，获得服务端包含用户token和API调用的响应，另外，还可以用 #
来截断一些不必要的请求字段。其实，这就是一种间接的服务端请求伪造（SSRF）结合目录遍历（PAth Traversal）的漏洞利用。

预想一下，我们希望在服务端响应中能返回的API GET请求调用如下：

>
> [http://127.0.0.1:123/v1/partners/victim_uuid/statements/current?earnings_structure_type=&locale=en&user_id=victim_uuid](http://127.0.0.1:123/v1/partners/victim_uuid/statements/current?earnings_structure_type=&locale=en&user_id=victim_uuid)

这样，我们可以对它进行控制修改的样式就为：

>
> [http://127.0.0.1:123/v1/statements/INJECTION_HERE?earnings_structure_type=&locale=en&statement_uuid=INJECTION_HERE&user_id=your_user_id](http://127.0.0.1:123/v1/statements/INJECTION_HERE?earnings_structure_type=&locale=en&statement_uuid=INJECTION_HERE&user_id=your_user_id)

因此，基于要在服务端响应中获得以上预想的API GET请求调用，我构造了如下的前端请求链接：

>
> <https://partners.uber.com/p3/money/statements/view/15327ef1-2acc-e468-e17a-576a7d12312%2f..%2f..%2f..%2Fv1%2Fpartners%2FVICTIM_UUID%2Fstatements%2Fcurrent%3Fearnings_structure_type%3D%26locale%3Den%26user_id%3DVICTIM_UUID%23>

最终，我们执行以上前端请求链接后，在服务端响应中，获得了预想的如下API GET请求调用：

>
> [http://127.0.0.1:123/v1/statements/15327ef1-2acc-e468-e17a-576a7d12312/../../../v1/partners/VICTIM_UUID/statements/current?earnings_structure_type=&locale=en&user_id=VICTIM_UUID#......](http://127.0.0.1:123/v1/statements/15327ef1-2acc-e468-e17a-576a7d12312/../../../v1/partners/VICTIM_UUID/statements/current?earnings_structure_type=&locale=en&user_id=VICTIM_UUID#......)

因为服务端响应回来的消息包含了当前请求用户的token，所以，我们只要在上述构造的前端请求链接中，修改VICTIM_UUID为其他用户的的UUID，就能在服务端响应中获得该用户的token信息，从而间接实现了对该账户的账号劫持了。

以上即为[Ron Chan](https://ngailong.wordpress.com/)对于这个漏洞的分享，整个过程就 是SSRF + Path
Tranversal = Account Takeover。基于Uber漏洞赏金政策和漏洞的严重性来看，该漏洞的奖励赏金应该不会低于$4,000美金。

 ***参考来源：[Ron Chan](https://ngailong.wordpress.com/2019/04/07/old-but-gold-dot-dot-slash-to-get-the-flag-uber-microservice/)，clouds编译，转载请注明来自FreeBuf.COM**  

