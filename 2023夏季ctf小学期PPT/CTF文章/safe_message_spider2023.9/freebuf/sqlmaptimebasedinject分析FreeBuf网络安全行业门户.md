# 1\. 前言

  

之前在一次会议上分享过sql注入的检测方法，当@chengable大牛问我sql注入如何检测的的时候，我的回答是：在甲方做安全，sql注入检测还是比较好做的。  

1) 报错注入检测。

2) 别做bool的报错注入，误报比较高。

3) 做基于time-based的时间注入，联系运维做上慢日志db记录，监控sleep，benchmark的关键字监控，可以在sleep的时间小数点上加上扫描任务的id号，方便定位。(p.s.
这种方法能找到99%的sql注入了)

因此，在做基于time-based的时间注入时，我把时间误差限制的非常苛刻。但是，@chengable在乙方做安全相关工作，基于time-based的时间注入一般是做不了的。据了解，他主要是先过滤存在注入点的情况，再加上sqlmapapi.py检测。早之前我也用sqlmap做过检测，遇到的问题就是误报多、扫描时间久，然后尝试了sqlmapapi.py，问题还是扫描时间过久，而且它不支持json格式的注入([详情](https://github.com/sqlmapproject/sqlmap/issues/2576))。但是，sqlmap的时间注入还是比较准的，如果不想用sqlmapapi.py怎么办？这里就把sqlmap的time-based注入的逻辑搬出来。

  

# 2\. 简单分析sqlmap的time-based注入

  

吐槽一下：sqlmap的代码不规范、难看、量又大。之前有大佬推荐我阅读sqlmap源码，学习一波，现在想想还好我放弃的早。  

所以，偷懒不想看源码加上--technique=T -v 3 就先看看sqlmap检测payload。

![Wechat1.jpeg](https://image.3001.net/images/20180410/15233404751365.jpeg!small)

![Wechat2.jpeg](https://image.3001.net/images/20180410/1523340489903.jpeg!small)​

​​​​![Wechat3.jpeg](https://image.3001.net/images/20180410/15233405058162.jpeg!small)

  

貌似偷懒还找到了一些门道，从截图中可以看到：  

首先，sqlmap塞入了sleep的注入payload：

先是塞入了 sleep(5)，发现执行了之后；又塞入sleep(0)，最后又塞入sleep(5)。

然后猜测一下，大概的检查思路就是先sleep(5)，秒延时成功的话，再sleep(0)。如果没有发现延时现象，继续sleep(5)，此时如果再次延时成功，就出现认为可能有注入的提醒：

![Wechat4.jpeg](https://image.3001.net/images/20180410/15233405268856.jpeg!small)  

  

​最后，很巧妙的是，sqlmap为了防止出现误报使用了if
的判断条件来排除误报，从上图可以看到sqlmap分别让等式成立测试两次，又让等式不成立测试两次，根据秒延时情况来判断误报。

  

# 3\. 深入分析一下源码

  

回归源码看看：根据前面的一些关键字，我们直接到代码里面去看看。比如搜索之前出现* **appears to be** * 看到第一步的代码：  

sqlmap/lib/controller/checks.py:

![Wechat5.jpeg](https://image.3001.net/images/20180410/15233405656198.jpeg!small)  

​这里发现，和前面猜测的八九不离十。

再找一下payload在哪里，特别是if条件的payload，还是用关键字查询，发现在这里：

sqlmap/xml/payloads/time_blind.xml:

![Wechat6.jpeg](https://image.3001.net/images/20180410/15233405857255.jpeg!small)  

​可以看到每个if条件的payload都在vector这个字段中。

  

# 4\. 闭合

  

闭合注入点前面的字符是能否注入的关键。  

观察到 tools/sqlmap/xml/boundaries.xml，所以，我们还需要参考这里面的多种闭合情况：

![Wechat7.jpeg](https://image.3001.net/images/20180410/15233406079882.jpeg!small)​​

#  

# 5\. 判断是否延时

## 5.1 方法一

参考之前awvs的注入，我想到一个比较容易理解的检测方法。取6次无注入payload正常测试的消耗时间，计算平均值为原生请求时间(ori_time)。

当注入时间为sleep(5)，将当前时间减去ori_time，作为sleep_time。如果sleep_time小于4，认为延时没有发生。（这里考虑到ori_time
受到网络影响导致变大，所以把阀值调到了四秒）

当注入时间为sleep(0)，将当前时间减去ori_time，作为sleep_time。如果sleep_time大于2，说明延时有误报。

## 5.2 方法二

再看一下sqlmap的代码，人家用了一个我搞不懂的数学问题([详情](https://blog.csdn.net/think_ycx/article/details/52083782))  

跟进：Request.queryPage --->wasLastResponseDelayed
就可以看到逻辑为：取30次的无注入payload正常测试的消耗时间，将他们放到kb.responseTimes中。计算30次的标准差为deviation，根据deviation计算出一个最慢的响应时间为lowerStdLimit：

​![Wechat8.jpeg](https://image.3001.net/images/20180410/15233406434225.jpeg!small)

​

它的值为30次的平均值加上TIME_STDEV_COEFF*标准差(deviation)，至于TIME_STDEV_COEFF，设置为7可以使得判断的准确度在99.9999999997440%。

最后判断当前这次请求的消耗时间是不是大于lowerStdLimit，大于说明延时发生，小于说明没有(另外，当lowerStdLimit小于0.5秒时候，lowerStdLimit取0.5秒)。

感性告诉我该选方法一，理性告诉我该选方法二。我还是选择方法二，测了一下这个注入点（[详情](http://testphp.vulnweb.com/listproducts.php?cat=1)）。很稳定的扫描出了注入漏洞。

  

# 6\. 结尾

  
我自己写的代码这里就不贴出来了，整个检测逻辑还是很清晰的，sqlmap基于时间的盲注入还是值得学习和参考的。

