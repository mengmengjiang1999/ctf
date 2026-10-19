**作者： Qixun Zhao(@S0rryMybad) of Qihoo 360 Vulcan Team**  
**原文链接：<https://blogs.projectmoon.pw/2019/10/30/iOS-13-1-3-Full-Chain-Eop/>**

该漏洞修复于 iOS 13.2, CVE 编号未明, 本来我打算用于 TianfuCup 的 iPhone rjb(当然还单纯只有漏洞^^),
但是遗憾在比赛前十多天被修复了, 但是该漏洞的成因很简单也很有趣. 关于 Safari 的漏洞我也会迟点写个 post.

漏洞出在最近添加的一个 syscall: kqueue_workloop_ctl, 它之后会调用底层函数
kqueue_workloop_ctl_internal. 在漏洞路径上没有任何 MACF check, 也就是说它可以用于任何沙盒内的提权, 包括
Safari.

kqueue_workloop_ctl_internal 函数内一共有两个问题, 第一个问题出在如下代码:

![](https://images.seebug.org/content/images/2019/10/9c8b2020-5c97-40c9-81a8-e361911468fc.jpg-w331s)

我们可以看到, 假如 TRP_RELEASED 这个 flag 没有设置, 就会调用 kqueue_release 两次, 一共减去两个引用计数,
如果设置了, 就代表这个 kq 已经被释放过了, 就只调用一次减去一个引用计数, 这一个引用计数是对应 kevent_get_kq 这个函数加上去的.

咋一看没有任何问题, 既可以避免了 race 的发生, 也可以避免多次释放同一个kq, 导致 over release.但是问题的关键在于这个 flag
设置在了一个栈变量上,而不是堆变量上, 也就是说, 无论如何设个 flag 都不会为 true.

![](https://images.seebug.org/content/images/2019/10/67e9506e-e4d8-4d6e-9112-81b8e024866a.jpg-w331s)

因此这个问题的起因虽然很简单, 但是也很难发现, 因为代码看上去没有任何的问题, 如果不连着上面的|trp|变量的来源一起看的话.关于 poc
的触发可以有两种方式, 第一种是通过 race, 导致 over release, 第二种是把 kq 挂在一个别的对象身上, 先把引用计数加一,
然后通过这个漏洞多次释放, 把对象引用计数减到 0 然后释放, 再通过别的对象的指针引用产生 UaF. 这里我的 poc 比较简单, 就是通过 race
触发, 如果要写 exploit, 则第二个触发方法比较靠谱:

![](https://images.seebug.org/content/images/2019/10/9eb3cf07-780e-45f5-bc35-31a578ee22b3.jpg-w331s)

关于漏洞的补丁很简单, 就是 flag 必须要设置到堆变量里, 不然产生不了任何效果:

![](https://images.seebug.org/content/images/2019/10/40d4ced2-2dbb-4ed8-b7ed-e4a7547c21e4.jpg-w331s)

至于第二个问题则存在于 kevent_get_kq 中, 留给读者自己去发现.

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1066/>

