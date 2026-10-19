**作者：Heige@知道创宇404实验室  
原文链接：<https://mp.weixin.qq.com/s/tpk61Uvc6ZF-qY7NQnahDg>**

「Prompt也是可编程的
--黑哥尔」既然ChatGPT火了后就诞生了“提示工程师”，所以Prompt本身的“编程”成为理所当然。这段时间一直在尝试Prompt进行“编程”，通过一些尝试得到的感触是还是比较复杂，一言难尽的……

![图片](https://images.seebug.org/content/images/2023/05/30/1685415178000-1ouwrz.png-w331s)

实际上对于利用ChatGPT生成各种查询语句，算是GPT的一个非常基础的应用点，如微软Bing
Chat就是很好的结合了GPT的这个场景，所以自然而然就想到网络空间搜索引擎上，最早落地的就是之前我文章里介绍过的ztz做的一个项目：<https://github.com/zt2/uncover-turbo>

随后Censys推出了一个CensysGPT：<https://gpt.censys.io/>

基于Prompt的实现实际上是存在各种不稳定的，因为提交的数据是有限的，对于这种使用说明类的文档如果数据比较多实际上是比较适合精调模式（Fine-tuning）的，这个我在[《大模型是小模型的基础》](http://mp.weixin.qq.com/s?__biz=Mzg5OTU1NTEwMg==&mid=2247484013&idx=1&sn=e580bb3850cc33f49ff9a0a91ebc14f6&chksm=c050c81cf727410af2222f14f2203c5d506e5bbe58296dfec2a602090f1583f37f32457feeaf&scene=21#wechat_redirect)
所看好的一个模式。

ZoomEyeGPT实现的方式也是基于Prompt的：<https://github.com/knownsec/ZoomeyeGPT>

为了方便使用我们采用浏览器插件的模式来进行，使用浏览器插件可能很好的实现数据交互，目前实现了两个功能：

1、是通过自然语言生成ZoomEye搜索语法

这个需求就不用多做说明了，注意是让大家不用去纠结各种语法词了。

2、通过选择banner生成ZoomEye搜索语法

这个需求是[《无名之辈,ChatGPT》](http://mp.weixin.qq.com/s?__biz=Mzg5OTU1NTEwMg==&mid=2247483918&idx=1&sn=d399181a42395920371a5cb6bd584262&chksm=c050c87ff72741694d8a578566236d0b7a1298b4926e4a1624780f6a492bb05d1d0e541b35cb&scene=21#wechat_redirect)更进一步，在原文里是通过ChatGPT编程能力来实现查询提取，而这次是直接用ChatGPT直接处理实现，这个是“黄世仁思维”更要进一步，这个功能也是更加方便实战“行为测绘”进行自动拓线。

具体的Prompt请参考：<https://github.com/knownsec/ZoomeyeGPT/blob/main/sw.js>

这个提示词里涉及到的逻辑还是比较多比较复杂的，实际上我是测试做了很多次，比如我最早的一个版本如下（实现上面banner处理的功能）：

    
    
    要求处理的只有一条http请求数据，请按如下处理：
    
    第一步
    
    删除http头里的”Date“字段
    删除http头了的"Connection"字段
    删除HTTP协议版本
    
    按以上规则处理如下http请求：
    
    HTTP/1.1  404 Not Found
    Server: nginx/1.18.0 (Ubuntu)
    Content-Type: text/plain; charset=utf-8
    Date: Sun, 09 Apr 2023 00:14:01 GMT
    Set-Cookie: abcdef=pp77drqb4l5fpdpogi0ehcl7gb; path=/
    Content-Length: 19
    Cache-Control: no-store, no-cache, must-revalidate
    Pragma: no-cache
    Keep-Alive: timeout=5, max=98
    Connection: Keep-Alive
    Connection: close
    
    404 page not found<html><head><body>a aaa bbb</body>
    
    得到：
    
    404 Not Found
    Server: nginx/1.18.0 (Ubuntu)
    Content-Type: text/plain; charset=utf-8
    Set-Cookie: abcdef=pp77drqb4l5fpdpogi0ehcl7gb; path=/
    Content-Length: 19
    Cache-Control: no-store, no-cache, must-revalidate
    Pragma: no-cache
    Keep-Alive: timeout=5, max=98
    
    404 page not found<html><head><body>a aaa bbb</body>
    
    
    第二步
    
    对Server及X-Powered-By头进行处理忽视掉/符号后面的字符。
    对Set-Cookie头里的第一个Cookie名保留。
    替换引号为空
    其他的内容请直接保留。
    
    得到的结果如下：
    
    404 Not Found
    Server: nginx
    Content-Type: text/plain; charset=utf-8
    Set-Cookie: abcdef
    Content-Length: 19
    Cache-Control: no-store, no-cache, must-revalidate
    Pragma: no-cache
    Keep-Alive: timeout=5, max=98
    
    404 page not found<html><head><body>a aaa bbb</body>
    
    第三步，对第二步的结果组合从字符串，用引号及加号连接，最终得到如下结果：
    
    "404 Not Found" +"Server: nginx" +"Content-Type: text/plain; charset=utf-8" +"Set-Cookie: abcdef" +"Content-Length: 19" +"Cache-Control: no-store, no-cache, must-revalidate" +"Pragma: no-cache" +"Keep-Alive: timeout=5, max=98" +"404 page not found<html><head><body>a aaa bbb</body>" 
    
    请学习以上处理方式处理如下HTTP response banner，只要求输出最终的处理的结果！
    
    HTTP/1.1 302 Moved Temporarily
    Server: nginx
    Date: Tue, 18 Apr 2023 13:52:49 GMT
    Content-Type: text/html
    Content-Length: 154
    Connection: close
    Location: https://api.cloudflare.com/client/v4//
    Referrer-Policy: no-referrer
    
    <html>
    <head><title>302 Found</title></head>
    <body bgcolor="white">
    <center><h1>302 Found</h1></center>
    <hr><center>nginx</center>
    </body>
    </html>

这个版本最大的特点是分步分解需求，这个在我这里测试实际上还是比较符合需求的，但是到另外小伙那测试发现各种不稳定的情况就出现了，因为提交的内容比较多很多逻辑都需要去强调处理，很多规则点很容易被忽视，这个学习的例子有限有很大的关系，所以我把这个提示词提交给ChatGPT，让他给我优化，优化后的结构跟我们最后发布的结构差不多（只是一些细节做了强调优化），所以最终按我的实际体验把Prompt的结构可以分为：

    
    
    * 数据处理规则
    * 学习实例说明
    * 强调关键词汇
    * 输出格式说明

![图片](https://images.seebug.org/content/images/2023/05/30/1685415181000-2gdqot.png-w331s)

给我的感受是“学习实例说明”是非常重要的，当然在“微调”的的强调关键词汇也非常重要，但是不管你怎么强调仍然存在各种乱生成的情况。

在实现“1、是通过自然语言生成ZoomEye搜索语法”的部分的时候，ZoomEye因为是国内最早的网络空间搜索引擎，在很多的语法设计上是比较“特立独行”的，比如用空格来表示或运算，常用的计算机编程里是用OR/or或者||
，所以你在使用或运算的时候非常容易出错，而且很多搜索引擎空格是用来表示一部分and运算的，比如shodan、google等搜索习惯！

再比如service:这个语法词的设计，在ZoomEye里这个主要表示常见协议，但是在http协议里还有一个Server的http头，很多人理解混淆了，黑哥尔之前也说过：

“ChatGPT是用集体的经验替代了个人的经验主义”

![图片](https://images.seebug.org/content/images/2023/05/30/1685415181000-3upotl.png-w331s)

所以这些很容易让人混淆的设计，理所当然也会影响集体经验主义的ChatGPT，在这个部分的Prompt里使用了比较多的“学习实例说明”，来强化ChatGPT的理解。

由于ZoomEyeGPT是基于Prompt的，提交的数据很有限，这也意味着app:语法词其实上面提到的service:这个语法词都属于我们标注生成的确定的“字典”，所以不太好提交直接提交给ChatGPT，为了不让ChatGPT随意生成，所以我直接删除了app这个语法词。好在ZoomEye是支持全局分词后关键词查询的，所以这个时候需要你在提供的提示词里使用，这里实际上目前这个方式不能随意把你提交的自然语言翻译成为ZoomEye搜索关键词，还是需要你对ZoomEye的语法及搜索机制有所理解的基础上。

这里我需要说明的是，即使你做了一些强调，ChatGPT仍然存在混乱的情况。这个时候你输入的提示词，直接使用关键词是还是比较好的，这个或许使用Fine-tuning的模式，能更好的实现。

![图片](https://images.seebug.org/content/images/2023/05/30/1685415181000-4ahmxb.png-w331s)

![图片](https://images.seebug.org/content/images/2023/05/30/1685415181000-5ltywv.png-w331s)

**Prompt 与 Program 互相转换**

如果说Prompt是可编程的，那么通过ChatGPT的处理，完全可以实现，Prompt 与
Program互换，这个也源于上面提到的[《无名之辈,ChatGPT》](http://mp.weixin.qq.com/s?__biz=Mzg5OTU1NTEwMg==&mid=2247483918&idx=1&sn=d399181a42395920371a5cb6bd584262&chksm=c050c87ff72741694d8a578566236d0b7a1298b4926e4a1624780f6a492bb05d1d0e541b35cb&scene=21#wechat_redirect)里写用ChatGPT根据Prompt写Python，到ZoomGPT里直接用让ChatGPT直接按Prompt处理提交的数据。所以我也做了一个这样的尝试，我把上面做好的Prompt提交给ChatGPT让它直接实现JS的处理，而这个代码的核心直接就是ZoomEyeGPT里那个“regx->ZoomEye”实现的那个代码。

![图片](https://images.seebug.org/content/images/2023/05/30/1685415181000-6ozxpa.png-w331s)

最后我想提一下的是：

ChatGPT这种东西在逐步打破各种领域的界限，更低门槛成本实现各种跨领域的结合，这些取决于你的学习能力，执行能力及创新的想法，“被AI取代”只能是无能者的墓志铭。

ZoomEyeGPT的演示：

