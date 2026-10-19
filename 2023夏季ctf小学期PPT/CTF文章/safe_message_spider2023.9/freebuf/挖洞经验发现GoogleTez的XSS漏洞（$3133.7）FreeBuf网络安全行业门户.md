![](https://image.3001.net/images/20200416/1587037962_5e98470af2c98.png!small)

**该篇Writeup讲述的是作者发现Google Tez网站的一个DOM based
XSS漏洞，从而收获$3133.7奖励的经历，漏洞非常非常简单，我们一起来看看。**

某天，我使用了[Knock Subdomain
Scan](https://github.com/guelfoweb/knock)和[Sublist3r](https://github.com/aboul3la/Sublist3r)等其它工具去探测谷歌子域名信息，大致如下：

![](https://image.3001.net/images/20200416/1587037635_5e9845c321545.png!small)

之后，我收集到了很多的谷歌在用子域名，有意思的是，当我访问其中的子域名<https://tez.google.com/>（现在已更名为Google
Pay），我发现在其URL链接后包含了名为referrer_id的赋值参数，看似是用来传递某些变量值。

我当即就用谷歌搜索大法来查找referrer_id是否涉及到特定参数的链接，刚好有：

    
    
    site:tez.google.com inurl:referrer_id=

![](https://image.3001.net/images/20200416/1587037709_5e98460dd05b1.png!small)

我想方设法对这个referrer_id参数进行了构造利用，都不奏效。但是有意思的是，我发现referrer_id的参数值会响应在<https://tez.google.com/>的页面中，如下：

![](https://image.3001.net/images/20200416/1587037777_5e984651b9cec.png!small)

于是，我顺手就往其参数值中构造插入了一个XSS Payload - <svg
onload=confirm(document.domain)>，XSS漏洞就这样出现了：

![](https://image.3001.net/images/20200416/1587037792_5e984660b4657.png!small)

立马，我把该漏洞上报给了谷歌安全团队，之后，谷歌立即对该漏洞进行了分类并告知我漏洞等级和奖励赏金还需要等待评估。

![](https://image.3001.net/images/20200416/1587037826_5e98468273171.png!small)

数日过去，我终于收到了谷歌安全团队回复我的邮件，其中说明该漏洞只是一个DOM based XSS，但是谷歌还是奖励了我$3133.7。

![](https://image.3001.net/images/20200416/1587037840_5e98469079146.png!small)

按照谷歌漏洞奖励计划，我上报的漏洞符合以下“客户端代码执行”XSS部分的“谷歌一般应用”$3133.7奖励标准：

![](https://image.3001.net/images/20200416/1587037855_5e98469f7cf32.png!small)

同时，我也被谷歌列入了漏洞名人堂的致谢名单：

![](https://image.3001.net/images/20200416/1587037878_5e9846b695e53.png!small)

 ***参考来源：[pethuraj](https://pethuraj.com/blog/google-bug-bounty-writeup/)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

