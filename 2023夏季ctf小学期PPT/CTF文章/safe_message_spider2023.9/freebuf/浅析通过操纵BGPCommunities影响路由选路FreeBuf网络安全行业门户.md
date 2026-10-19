**安全领域的讨论离不开漏洞，但是若说世界上最严重的漏洞是什么呢？（不许说是人~），如果说是BGP的漏洞，应该没有人反对吧？（二进制和web大佬表示不服......）**

关于BGP的安全问题，Freebuf上有很多文章已经讨论过了，例如 <https://www.freebuf.com/tag/bgp> 这个列表。

最近看了CCS19新鲜出炉的一篇论文《 **SICO:Surgical Interception Attacks by Manipulating BGP
Communities**
》，感觉很受启发。这篇论文是美国普林斯顿大学的一个团队发表的，也是由DARPA（美国国防高级研究计划局）和AFRL（美国空军研究实验室）支持的项目。我这里只结合我的理解介绍一下文中提出的三种代表性场景。

##  **一、BGP前置知识**

###  1、AS之间的商业关系

> （1）provider-customer
>
> （2）peer-peer
>
> （3）customer-provider

其中customer 需向 provider（服务提供商）付费，才能够访问互联网资源。peer
之间就是完全平等的，免费交换网络流量。其实AS之间还有其它的关系，但主要是以上三种。

###  2、路由的导入规则与导出规则

如下图，左侧展示了路由的导出规则，右侧展示了路由的导入规则（选路原则），总结一下就是：

(1) 导出规则

> 1) 从customers学到的路由向所有邻居宣告；
>
> 2) 从peers和providers学习到的路由只向 customers宣告。

(2) 导入规则

> 1）优选Local preference高的，通常从高到低排列为 customer > peer > provider；
>
> 2）其次看AS-Path长度，长度越小越优先。

其时路由的导入规则还有很多，本文只用到这关键的两条。

![](https://image.3001.net/images/20191225/1577262875_5e031f1b63fc0.png!small)  
3、BGP Community属性

BGPcommunities 是一种路由标记方法，用来添加到BGP的宣告 中用来控制上游ASes的路由策略。

BGPcommunities 是可选传递属性，不支持该属性的BGProuter 原封不动的将community值传递给下游BGP邻居。

本文用到的 community actions：

> Lower local-preference below peer (LowerPref) 降低本地优先级
>
> No export to select peer (NoExportSelect) 不向指定的 peer导出路由
>
> No export to all peers (NoExportAll) 不向全部 peer导出路由

##  二、三种典型攻击场景

![](https://image.3001.net/images/20191225/1577264243_5e0324730dab5.png!small)

攻击者（图中小黑人）有两个provider：A和B，攻击者伪造原本属于Victim的IP前缀，向A发送欺骗宣告报文，希望把原本去往Victim的网络流量吸引过来，再通过provider
B返还给Victim，相当于做了中间人劫持攻击。为了达到这种效果，需要使得B相信去往Victim的路由R，而不是去往攻击者的路由R*。通过BGP
的Community属性可以达到这一点，下面分三种不同场景讨论：

###  场景一 图a

 **问题** ：B会更喜欢R*，因为选路原则中，优选Local
preference高的，R*来自peer，R来自provider，peer>provider。

**解决方案** ：攻击者可以用Community action的 **NoExportAll** 或 **NoExportSelect**
阻止A向B导出R*，这样B学不到R*，只能选择R。

###  场景二 图b

 **问题** ：B会更喜欢R*，因为R和R*全部来自provider，Local
preference相同，但B去往攻击者只需要3跳，而去往受害者需要四跳，优选跳数少的R*。

**解决方案** ：攻击者可以用Community action的LowPref来降低Shared tier-1上R*的Local
preference，这样B会优选R。

###  场景三 图c

 **问题** ：B不确定会更喜欢R还是R*，需要借助其他条件判断。因为R*和R的Local
preference相同，都是来自peer；B去往攻击者和Victim的跳数相同，均为2跳。

**解决方案** ：攻击者可以用Community action的 **NoExportAll** 或 **NoExportSelect**
阻止A向B导出R*，这样B学不到R*，只能选择R。

##  三、总结

通过操纵BGP
Communities来实现劫持攻击是一种很新颖的方式，这种劫持方式可以避免路由黑洞，隐蔽性高，很多传统的检测方式无法检测到。当然，有攻即有防，论文中也提出了几种防御方式，例如限制Community的传播、限制BGP
update报文中communities的数量等方式。互联网对人类社会太重要了，希望可以在网络安全研究人员的不断努力下安全稳定地发展下去。

 ***本文原创作者： Chris东方，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
  

