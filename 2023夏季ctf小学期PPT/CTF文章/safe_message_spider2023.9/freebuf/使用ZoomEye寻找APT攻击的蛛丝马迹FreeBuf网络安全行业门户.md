**今年一月发布的ZoomEye
2020里上线了ZoomEye的历史数据查询API接口，这个历史数据接口还是非常有价值的，这里就介绍我这几天做的一些尝试追踪APT的几个案例。**  

在开始之前首先你需要了解ZoomEye历史api接口的使用，参考文档：<https://www.zoomeye.org/doc#history-ip-search> 这里可以使用的是ZoomEye SDK<https://github.com/knownsec/ZoomEye>
另外需要强调说明下的是：ZoomEye线上的数据是覆盖更新的模式 **，**
也就是说第2次扫描如果没有扫描到数据就不会覆盖更新数据，ZoomEye上的数据会保留第1次扫描获取到的banner数据，这个机制在这种恶意攻击溯源里其实有着很好的场景契合点：恶意攻击比如Botnet、APT等攻击使用的下载服务器被发现后一般都是直接停用抛弃，当然也有一些是被黑的目标，也是很暴力的直接下线！所以很多的攻击现场很可能就被ZoomEye线上缓存。

当然在ZoomEye历史api里提供的数据，不管你覆盖不覆盖都可以查询出每次扫描得到的banner数据，但是目前提供的ZoomEye历史API只能通过IP去查询，而不能通过关键词匹配搜索，所以我们需要结合上面提到的ZoomEye线上缓存数据搜索定位配合使用。

## 案例一：Darkhotel APT

在前几天其实我在“黑科技”知识星球里提到了，只是需要修复一个“bug”：这次Darkhotel使用的IE 0day应该是CVE-2019-1367
而不是CVE-2020-0674（感谢廋肉丁@奇安信），当然这个“bug”不影响本文的主题。

![](https://image.3001.net/images/20200526/1590460083_5ecc7eb32ed5b.jpg!small)从上图可以看出我们通过ZoomEye线上数据定位到了当时一个Darkhotel水坑攻击现场IP，我们使用ZoomEye
SDK查询这个IP的历史记录：

    
    
    ╭─heige@404Team ~  
    ╰─$python                                                                                                                                      
    Python 2.7.16 (default, Mar 15 2019, 21:13:51)  
    [GCC 4.2.1 Compatible Apple LLVM 10.0.0 (clang-1000.11.45.5)] on darwin  
    Type "help", "copyright", "credits" or "license" for more information.  
     import zoomeye  
     zm = zoomeye.ZoomEye(username="xxxxx", password="xxxx")  
     zm.login()  
     u'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpX...'  
     data = zm.history_ip("202.x.x.x")  
     22  
    

列举ZoomEye历史数据里收录这个IP数据的时间节点及对应端口服务

    
    
     ...  
     >>>for i in data['data']:  
     ...     print(i['timestamp'],i['portinfo']['port'])  
     ...  
     (u'2020-01-28T10:58:02', 80)  
     (u'2020-01-05T18:33:17', 80)  
     (u'2019-11-25T05:27:58', 80)  
     (u'2019-11-02T16:10:40', 80)  
     (u'2019-10-31T11:39:02', 80)  
     (u'2019-10-06T05:24:44', 80)  
     (u'2019-08-02T09:52:27', 80)  
     (u'2019-07-27T19:22:11', 80)  
     (u'2019-05-18T10:38:59', 8181)  
     (u'2019-05-02T19:37:20', 8181)  
     (u'2019-05-01T00:48:05', 8009)  
     (u'2019-04-09T16:29:58', 8181)  
     (u'2019-03-24T20:46:31', 8181)  
     (u'2018-05-18T18:22:21', 137)  
     (u'2018-02-22T20:50:01', 8181)  
     (u'2017-03-13T03:11:39', 8181)  
     (u'2017-03-12T16:43:54', 8181)  
     (u'2017-02-25T09:56:28', 137)  
     (u'2016-11-01T00:22:30', 137)  
     (u'2015-12-30T22:53:17', 8181)  
     (u'2015-03-13T20:17:45', 8080)  
     (u'2015-03-13T19:33:15', 21)  
    

我们再看看被植入IE 0day的进行水坑攻击的时间节点及端口：

    
    
    >>> for i in data['data']:  
     ...     if "164.js" in i['raw_data']:  
     ...             print(i['timestamp'],i['portinfo']['port'])  
     ...  
     (u'2020-01-28T10:58:02', 80)  
     (u'2020-01-05T18:33:17', 80)  
     (u'2019-11-25T05:27:58', 80)  
     (u'2019-11-02T16:10:40', 80)  
     (u'2019-10-31T11:39:02', 80)  
     (u'2019-10-06T05:24:44', 80)  
    

很显然这个水坑攻击的大致时间区间是从2019-10-06 05:24:44到2020-01-28
10:58:02，另外这个IP很显然不是攻击者购买的VPS之类，而是直接攻击了某个特定的网站来作为“水坑”进行攻击，可以确定的是这个IP网站早在2019-10-06之前就已经被入侵了！从这个水坑的网站性质可以基本推断Darkhotel这次攻击的主要目标就是访问这个网站的用户！

我们继续列举下在2019年这个IP开了哪些端口服务，从而帮助我们分析可能的入侵点：

    
    
    >>> for i in data['data']:  
     ...     if "2019" in i['timestamp']:  
     ...             print(i['timestamp'],i['portinfo']['port'],i['portinfo']['service'],i['portinfo']['product'])  
     ...  
     (u'2019-11-25T05:27:58', 80, u'http', u'nginx')  
     (u'2019-11-02T16:10:40', 80, u'http', u'nginx')  
     (u'2019-10-31T11:39:02', 80, u'http', u'nginx')  
     (u'2019-10-06T05:24:44', 80, u'http', u'nginx')  
     (u'2019-08-02T09:52:27', 80, u'http', u'nginx')  
     (u'2019-07-27T19:22:11', 80, u'http', u'nginx')  
     (u'2019-05-18T10:38:59', 8181, u'http', u'Apache Tomcat/Coyote JSP engine')  
     (u'2019-05-02T19:37:20', 8181, u'http', u'Apache Tomcat/Coyote JSP engine')  
     (u'2019-05-01T00:48:05', 8009, u'ajp13', u'Apache Jserv')  
     (u'2019-04-09T16:29:58', 8181, u'http', u'Apache httpd')  
     (u'2019-03-24T20:46:31', 8181, u'http', u'Apache Tomcat/Coyote JSP engine')  
    

很典型的JSP运行环境，在2019年5月的时候开了8009端口，Tomcat后台管理弱口令等问题一直都是渗透常用手段～～

顺带提一句，其实这次的攻击还涉及了另外一个IP，因为这个IP相关端口banner因为更新被覆盖了，所以直接通过ZoomEye线上搜索是搜索不到的，不过如果你知道这个IP也可以利用ZoomEye历史数据API来查询这个IP的历史数据，这里就不详细展开了。

## 案例二：毒云藤（APT-C-01）

关于毒云藤（APT-C-01）的详细报告可以参考<https://ti.qianxin.com/uploads/2018/09/20/6f8ad451646c9eda1f75c5d31f39f668.pdf>我们直接把关注点放在

“毒云藤组织使用的一个用于控制和分发攻击载荷的控制域名
[http://updateinfo.servegame.org](http://updateinfo.servegame.org/)”

“然后从 `hxxp://updateinfo.servegame.org/tiny1detvghrt.tmp` 下载 payload”

URL上，我们先尝试找下这个域名对应的IP，显然到现在这个时候还没有多大收获：

    
    
    ╭─heige@404Team ~  
    ╰─$ping updateinfo.servegame.org  
    ping: cannot resolve updateinfo.servegame.org: Unknown host  
    

在奇安信的报告里我们可以看到使用的下载服务器WEB服务目录可以遍历

![](https://image.3001.net/images/20200526/1590460250_5ecc7f5acd877.png!small)所以我们应该可以直接尝试搜索那个文件名“tiny1detvghrt.tmp”，果然被我们找到了

![f47bff11961e4fccb2ca07eb5e02c8a.png](https://image.3001.net/images/20200527/15905708684773.png!small)这里我们可以基本确定了`updateinfo.servegame.org`对应的IP为165.227.220.223
那么我们开始老套路查询历史数据：

    
    
        >>> data = zm.history_ip("165.227.220.223")  
        >>> 9  
        >>> for i in data['data']:  
         ...     print(i['timestamp'],i['portinfo']['port'])  
         ...  
         (u'2019-06-18T19:02:22', 22)  
         (u'2018-09-02T08:13:58', 22)  
         (u'2018-07-31T05:58:44', 22)  
         (u'2018-05-20T00:55:48', 80)  
         (u'2018-05-16T20:42:35', 22)  
         (u'2018-04-08T07:53:00', 80)  
         (u'2018-02-22T19:04:29', 22)  
         (u'2017-11-21T19:09:14', 80)  
         (u'2017-10-04T05:17:38', 80)  
    

继续看看这个`tiny1detvghrt.tmp`部署的时间区间：

    
    
    >>> for i in data['data']:  
     ...     if "tiny1detvghrt.tmp" in i['raw_data']:  
     ...             print(i['timestamp'],i['portinfo']['port'])  
     ...  
     (u'2018-05-20T00:55:48', 80)  
     (u'2018-04-08T07:53:00', 80)  
     (u'2017-11-21T19:09:14', 80)  
    

最起码可以确定从2017年11月底就已经开始部署攻击了，那么在这个时间节点之前还有一个时间节点2017-10-04
05:17:38，我们看看他的banner数据：

    
    
    >>> for i in data['data']:  
     ...     if "2017-10-04" in i['timestamp']:  
     ...             print(i['raw_data'])  
     ...  
     HTTP/1.1 200 OK  
     Date: Tue, 03 Oct 2017 21:17:37 GMT  
     Server: Apache  
     Vary: Accept-Encoding  
     Content-Length: 1757  
     Connection: close  
     Content-Type: text/html;charset=UTF-8<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><html>  
     <head>  
      <title>Index of /</title>  
     </head>  
     <body><h1>Index of /</h1>  
      <table>  
       <tr><th valign="top">< img src="/icons/blank.gif" alt="[ICO]"></th><th>< a href=" ">Name</ a></th><th>< a href="?C=M;O=A">Last modified</ a></th><th>< a href="?C=S;O=A">Size</ a></th><th>< a href="?C=D;O=A">Description</ a></th></tr>  
       <tr><th col="5"><hr></th></tr><tr><td valign="top">< img src="/icons/unknown.gif" alt="[   ]"></td><td>< a href="doajksdlfsadk.tmp">doajksdlfsadk.tmp</ a></td><td align="right">2017-09-15 08:21  </td><td align="right">4.9K</td><td> </td></tr><tr><td valign="top">< img src="/icons/unknown.gif" alt="[   ]"></td><td>< a href="doajksdlfsadk.tmp.1">doajksdlfsadk.tmp.1</ a></td><td align="right">2017-09-15 08:21  </td><td align="right">4.9K</td><td> </td></tr><tr><td valign="top">< img src="/icons/unknown.gif" alt="[   ]"></td><td>< a href="doajksdlrfadk.tmp">doajksdlrfadk.tmp</ a></td><td align="right">2017-09-27 06:36  </td><td align="right">4.9K</td><td> </td></tr><tr><td valign="top">< img src="/icons/unknown.gif" alt="[   ]"></td><td>< a href="dvhrksdlfsadk.tmp">dvhrksdlfsadk.tmp</ a></td><td align="right">2017-09-27 06:38  </td><td align="right">4.9K</td><td> </td></tr><tr><td valign="top">< img src="/icons/unknown.gif" alt="[   ]"></td><td>< a href="vfajksdlfsadk.tmp">vfajksdlfsadk.tmp</ a></td><td align="right">2017-09-27 06:37  </td><td align="right">4.9K</td><td> </td></tr><tr><td valign="top">< img src="/icons/unknown.gif" alt="[   ]"></td><td>< a href="wget-log">wget-log</ a></td><td align="right">2017-09-20 07:24  </td><td align="right">572 </td><td> </td></tr>  
       <tr><th col="5"><hr></th></tr></table></body></html>  
    

从这个banner数据里可以得出结论，这个跟第一个案例里目标明确的入侵后植入水坑不一样的是，这个应该是攻击者自主可控的服务器，从`doajksdlfsadk.tmp`这些文件命名方式及文件大小（都为4.9k）基本可以推断这个时间节点应该是攻击者进行攻击之前的实战演练！所以这个IP服务器一开始就是为了APT攻击做准备的，到被发现后就直接抛弃！

## 总结

网络空间搜索引擎采用主动探测方式在网络攻击威胁追踪上有很大的应用空间，也体现了历史数据的价值，通过时间线最终能复盘攻击者的攻击手段、目的及流程。最后感谢所有支持ZoomEye的朋友们，ZoomEye作为国际领先的网络空间测绘搜索引擎，我们一直在努力！

 ***作者：Heige(a.k.a Superhei) of KnownSec 404 Team，转载请注明来自 FreeBuf.COM**  

