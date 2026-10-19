**作者：heige@知道创宇404实验室  
时间：2021年11月17日  
原文链接：<https://mp.weixin.qq.com/s/cCXt6FUEYGd6s9cg5VFN0Q>**

在 [谈谈网络空间“行为测绘”](https://mp.weixin.qq.com/s/fQatA5iyewqRBMWtpVjsRA)
文章里我用了Trickbot作为例子，受当时样本数量的限制（2个IP），所以直接指定了一个特征的证书：

    
    
    subject: C=AU; ST=Some-State; O=Internet Widgits Pty Ltd
    issuer: C=AU; ST=Some-State; O=Internet Widgits Pty Ltd

今天看到一个最新的73个IP的样本：

<https://twitter.com/1ZRR4H/status/1460440775775375361>

<https://pastebin.com/35mhCsw2>

![](https://images.seebug.org/content/images/2021/11/406cf0b3-f7c6-4d41-8299-2b3e3f55c30b.jpg-w331s)

手工抽样看了下，证书有不符合之前特征的情况，比如下面：

    
    
    Issuer: ST=none
    Subject: ST=none

等等各种情况，所以这里对“行为测绘”进行一些补充：

1、 **群体行为可能有多种行为** ，这个取决于你的样本覆盖及更加通用的特征的提取（注：更宽松的规则固然覆盖更全漏报率低但很可能导致更多误报）

2、 **群体行为可以进化变异** ，在某个确定或者不确定周期下进行修改，甚至可能在文章发布后被这些APT、僵尸网络看到后进行修改的可能

以上2点其实在样本集更多更全的情况下，更能提炼出相对准确覆盖全面的搜索语法，当然这里是 **没有考虑原始样本归因是否存在错误**
的前提下，所以针对Trickbot C2搜索语句做了下更新：

    
    
    "HTTP/1.1 403 Forbidden" +"Server: nginx" +"Content-Length: 9" +"SSL Certificate" -"Content-Type"
    
    
    https://www.zoomeye.org/searchResult?q=%22HTTP%2F1.1%20403%20Forbidden%22%20%2B%22Server%3A%20nginx%22%20%2B%22Content-Length%3A%209%22%20%2B%22SSL%20Certificate%22%20-%22Content-Type%22&t=all

通过抽样验证上面提到的73个样本，效果还是不错的。当然还可能存在一些误报，不过简单过了下应该不太多了，所以就没做作那么精确了...

![](https://images.seebug.org/content/images/2021/11/4b131e0d-3807-4456-91cd-2f33731888d9.jpg-w331s)

通过ZoomEye查询到的数据，在前几页的目标看了下IP档案页面的详情，发现很多的IP都是MikroTik的设备，而且很多都开了vpn 如下图：

![](https://images.seebug.org/content/images/2021/11/4b0c49ae-75dd-4560-ab64-af7d7767d4d4.jpg-w331s)

所以我感觉这些都是这个团伙抓的肉鸡？从ZoomEye统计数据年份来看，最早可以追溯到2017年，Google了下发现Trickbot的开始的时间确实是2017年（历史数据还是很有用的！）。

![](https://images.seebug.org/content/images/2021/11/38a9b301-37fd-4ad9-8fb9-15f4f238e2e2.jpg-w331s)

通过2017年的证书特征来看：

    
    
    Issuer: C=AU, ST=f2tee4, L=gf23et65adt, O=tg4r6tds, OU=rst, CN=rvgvtfdf
    Subject: C=AU, ST=f2tee4, L=gf23et65adt, O=tg4r6tds, OU=rst, CN=rvgvtfdf

确实有行为进化变异的迹象！

> 还有一些比较奇怪有意思情况，少量证书特征跟BazarLoader重叠  
>  公众号：黑哥说安全 [【“行为测绘”应用实战】一个ZoomEye查询搜尽BazarLoader
> C2](https://mp.weixin.qq.com/s/2WOfABt6QAoTG2H-3IfA4g?scene=21#wechat_redirect)
    
    
    Issuer: C=GB, ST=London, L=London, O=Global Security, OU=IT Department, CN=example.com
    Subject: C=GB, ST=London, L=London, O=Global Security, OU=IT Department, CN=example.com

我简单搜索了下这个应该是某类默认证书形式，难道他们想到一块去了？：）

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1759/>

