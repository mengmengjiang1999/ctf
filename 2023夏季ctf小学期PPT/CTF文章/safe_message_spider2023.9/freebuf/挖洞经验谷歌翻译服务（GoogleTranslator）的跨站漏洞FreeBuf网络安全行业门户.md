![](https://image.3001.net/images/20200112/1578818160_5e1ada70c4f1e.png!small)

**在这篇文章里，越南籍作者通过发现了谷歌翻译服务（Google
Translator）越翻英界面中存在的跨站漏洞（XSS），最后经测试验证，获得了谷歌官方奖励的$3133.70，我们一起来看看。**

##  凌晨发现XSS漏洞

河内，凌晨2点的冬天，大家都进入了梦乡，我还在投入地加班工作，结束时已经是凌晨02:45。临睡前准备放松一下，打算找部电影看看，但记不起电影的准确英文名了，于是打开了谷歌翻译网站translate.google.com，在其中输入了越南语，想把它转换成英语，之后，我突然发现了一些端倪，于是尝试在其中输入了其它验证性Payload，如下图红色部分所示：

![](https://image.3001.net/images/20200112/1578817960_5e1ad9a8e8316.jpeg!small)我马上按F12进入的Chrome开发者模式进行检查，我发现我输入的Payload已经被成功执行了，如下：

![](https://image.3001.net/images/20200112/1578817974_5e1ad9b6a2543.jpeg!small)这说明......，谷歌针对HTML标签功能未做完善的过滤和编码规则，所以导致了我能在这里执行XSS。于是我尝试看看谷歌的其它语言翻译界面是否存在该漏洞，但是好像不行，它们都实施了过滤编码，只有这里的越南语（Primary
language）翻译为英语（Language after translation）界面存在该漏洞。

为了更好地验证该XSS漏洞，我构造了HTML代码试图让translate.google.com反弹出当前域名和用户Cookie信息，这里比较难的是对字符长度的控制，最后的HTML
Payload如下：

    
    
    <iframe onload=”javascript:prompt(document.domain, document.cookie)” id=”xss” role=”xss”>hello xss

translate.google.com反弹出的提示窗如下：

![](https://image.3001.net/images/20200112/1578817994_5e1ad9caedda9.jpeg!small)

##  谷歌会接收这种漏洞吗？

结合上述HTML Payload，最终在浏览器端可执行的URL XSS Payload如下：

>
> [https://translate.google.com/?hl=en#view=home&op=translate&sl=vi&tl=en&text=%3Ciframe%20onload=%22javascript:alert](https://translate.google.com/?hl=en#view=home&op=translate&sl=vi&tl=en&text=%3Ciframe%20onload=%22javascript:alert)(document.domain)%22%20id=%22xss%22%20role=%22xss%22%3Ehello%20xss

运行该URL XSS Payload后，浏览器中其请求的参数为：

    
    
    & sl = en => Primary language    
    
        
    
            & tl = en => Language after translation    
    
        
    
            & text => Paragraphs

所以，常规来说，只要我对其中的XSS
Payload做一些相应的编码转换，然后把上述URL发送给受害者，XSS的执行是没问题的。但是，当我把该漏洞提交给谷歌安全团队之后，却被告知这是一个无效漏洞，因为他们认为其中的域名隶属于“沙箱安全域名”（sandbox
domains）范畴，所以该漏洞直接被归为了“不需要修复”（Won’t Fix）的类别。

![](https://image.3001.net/images/20200112/1578818046_5e1ad9fe08543.jpeg!small)当时我非常沮丧，于是就去查了查谷歌所谓的sandbox
domains范围，如下：

![](https://image.3001.net/images/20200112/1578818064_5e1ada10032f9.jpeg!small)这......，上面根本没有translate.google.com啊！谷歌设置所谓的sandbox
domains目的在于，针对提供给用户的前端服务中，避免用户植入木马、病毒等恶意程序从而影响到其它谷歌服务，因此实行沙箱隔离的一类域名。这里的translate.google.com就不在谷歌所述的sandbox
domain之内，他们绝对是搞错了。

之后，我又向谷歌发送了相关说明，他们接收并提高了该漏洞的威胁级别，还给了我奖励。最后我要感谢漏洞众测社区的网友，他们中的一些人帮我一起验证谷歌搞错了，并给了我鼓励。

##  漏洞上报及处理进程

> 14/11/201914:05 — 漏洞初报
>
> 14/11/2019 20:29 — 谷歌回应该漏洞归为“不需要修复” 类别
>
> 14/11/2019 21:29 — 我提供了更多参考信息
>
> 11/15/2019 00:36 — 我向谷歌说明了translate.google.com不在他们所说的沙箱域名之内
>
> 21/11/2019 23:23 — 我又向谷歌发送了一个PoC验证视频
>
> 11/22/2019 00:12 — 谷歌接收了该漏洞并提高了漏洞级别
>
> 11/28, 2019 01:20 — 谷歌奖励了我 $3133.70
>
> 23/12/2019 03:47 — 谷歌修复了该漏洞

***参考来源：[medium](https://medium.com/monetary/how-did-i-earn-3133-70-from-google-translator-9becf942dbdc)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

  

