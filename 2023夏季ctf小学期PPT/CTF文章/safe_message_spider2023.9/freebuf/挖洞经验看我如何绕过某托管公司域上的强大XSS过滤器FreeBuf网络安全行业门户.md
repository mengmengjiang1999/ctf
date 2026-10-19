***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **本文为大家分享的是最近一次绕过某托管公司域上的XSS过滤器的经历。话不多说，下面我们直入主题！**

首先，我尝试在目标站点上获取信息，我还借助了Google Dork搜索语法，例如site:*.*.namecheap.com &
site:*.namecheap.com来查找子域。

所以，目标域是support.namecheap.com，一个在赏金计划范围之外的域。据了解，我的朋友Ahsan
leet已经在他们的网站上发现了一些关键问题和XSS。在这里我暗自下定决心，并告诉自己我一定能成功绕过他们的保护策略。

但这似乎并不容易。两个域的防火墙，几乎阻止了我发送的所有有效载荷。

![看我如何绕过某托管公司域上的强大XSS过滤器](https://image.3001.net/images/20180425/15246158812496.png!small)

![看我如何绕过某托管公司域上的强大XSS过滤器](https://image.3001.net/images/20180425/15246158611015.png!small)

难道就此放弃吗？不，我绝不是一个轻言放弃的人！

![看我如何绕过某托管公司域上的强大XSS过滤器](https://image.3001.net/images/20180425/15246159143723.png!small)

在近3个小时的各种尝试后，我想到了一种较为特别的payload，我将其编码并作为一个URL发送。但令我失望的是这个payload仅仅只是绕过了防火墙，并没有成功弹窗。这让我意识到，我需要比这更加先进的payload。

![看我如何绕过某托管公司域上的强大XSS过滤器](https://image.3001.net/images/20180425/152461593884.png!small)

有效载荷被注入，但仍然无法弹出。为了绕过过滤器，我添加了一些类似的有效载荷和炸弹！

 ****

    
    
    -- 一些类似的 payload 在主payload之前
    
     <a href=”javascript&ampcolonalert&amplpardocument&ampperioddomain&amprpar”>Click Here</a>   
    
    
    -- 一些类似的payload在主payload之后

 ****

bingo！成功绕过保护机制并弹出！

![看我如何绕过某托管公司域上的强大XSS过滤器](https://image.3001.net/images/20180425/15246159606332.png!small)

顺着这个思路，我又获取到了第二个XSS payload：

    
    
    -- 一些类似的payload在主payload之前”>
    
    <iframe/src=javascript&ampcolon[document&ampperioddomain].find(alert)>
    
    -- 一些类似的payload在主payload之后

## PoC视频

看不到？点[这里](https://v.qq.com/x/page/p0638maxw8s.html)

看不到？点[这里](https://v.qq.com/x/page/u06383vak4r.html)

注意：该域名实际上并不在namecheap赏金计划的范围之内，并由kayako托管。但这个XSS问题对这两个网站来说非常重要，因此他们依然给予了我丰厚的奖励。

![如何绕过某托管公司域上的强大XSS过滤器](https://image.3001.net/images/20180425/15246159882064.png!small)

最后，我要特别感谢Brute和Samuel Esteban。

谢谢大家的阅读，希望为你们带来好的思路和经验！

 ***参考来源：[medium](https://medium.com/@Skylinearafat/the-story-behined-the-namecheap-xss-filter-bypass-be79624fd0c3)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**  

