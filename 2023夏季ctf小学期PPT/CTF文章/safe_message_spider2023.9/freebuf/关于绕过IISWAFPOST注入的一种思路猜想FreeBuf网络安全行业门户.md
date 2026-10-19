本文是一种设想绕过IIS
WAF的思路猜想，并不代表真正的有这样的漏洞，连作者自己都没有去验证过，仅当大家在吃完晚饭以后刷刷Freebuf打发时间吧。IIS仅限于IIS6，当然不排除把IIS6的插件丢到IIS7上面跑的情况。

## 一. IIS WAF是什么？

什么是WAF，关于这个问题不多解释，连面试官都问过我好几次。 IIS WAF是一种利用IIS的ISAPI
FILTER插件来完成的一种过滤，拦截WEB工具的软墙。该插件直接安装于IIS扩展属性里。市面上面对应的有早期的MYIIS-VIF，如今的什么什么盾，什么什么狗，什么什么宝，什么什么防篡改系统。但随着时间的推移，在基于端口转发的NGINX的waf成为了主流（统一拦截）。

## 二. IIS WAF是怎么做成的？

相关的安装文章等，大家可以在这里看到：<https://docs.microsoft.com/en-us/iis/configuration/system.webServer/isapiFilters/>
通俗点，就是利用微软提供的接口文档提前捕获了用户的输入和输出场景，然后用安全的套路去规划和寻找安全风险点。详细的接口文档大家可以看到这里：
<https://msdn.microsoft.com/zh-tw/library/ms525878.ASPX>

## 三. 针对SQL注入来具体聊聊  

SQL注入是web安全里的大头，特别是POST注入环节。所有，如果你的渗透测试行为在提交POST参数的被拦截了，肯定是非常头疼的。针对sdk开发中HttpFilterProc回调函数中，对POST数据的拦截主要在回调消息：SF_NOTIFY_READ_RAW_DATA中。

![微信截图_20180927212231.png](https://image.3001.net/images/20180927/1538054574_5bacd9ae17a47.png!small)针对SF_NOTIFY_READ_RAW_DATA的消息参数分析，我们可以看到这样的数据结构信息：

    
    
    typedef struct _HTTP_FILTER_RAW_DATA HTTP_FILTER_RAW_DATA {
          PVOID pvInData;
          DWORD cbInData;
          DWORD cbInBuffer;
          DWORD dwReserved;
    } HTTP_FILTER_RAW_DATA, * PHTTP_FILTER_RAW_DATA;
    

pvindata是传入的原始数据指针地址，cbinData是传入的总数据大小，cbinbuffer是传入的现有数据大小。为了组合数据，我们需要在这个消息体里不断分配内存去拼合数据。站在攻防的角度来分析问题，此时此刻我们应该站在软件设计者的角度来分析问题，因为为了防护的性能和效果，很可能在防护软件开发中存在一些安全代码空洞。

（1） 如何检测传入数据的安全？

对每个cbinbuffer进行检查，包括用正则表达式扫描。

（2）可以把数据全部组合完毕后一起扫描吗？

可行，但万一用户提交的数据非常非常大怎么办？不要把自己玩死。

（3）是否可以折中？

可以，只检测数据前1M的内容。后面的忽略？！

（4）武断点？

只要cbinData够大，就直接断开连接或者输出错误信息。但这样做是不完整的，是不够人性的，是tmd的很武断的..........................  

四 . 攻击猜想

针对cbinBuffer的数据大小，有2000字节的规定，也就是说，我们提交的数据是以做多2000字节的一个Buff来进行处理的。我们是否可以提交这样的数据：

猜想1：  

AAAAAAAAAAAAAAAA......AAASEL(2000 BYTE)

ECTAAAAAAA*AAAAA.......AAAF(2000 BYTE)

ROMAAAAAAAAAAAA......AAAA(2000 BYTE)

猜想2：

AAAAAAAAAAAAAA..(200000)........

（猜想1的数据）

这样的模式是构建比较大的数据，在2000缓冲区的折断区存放需要注入的关键字和数据内容，从而绕过针对特定关键字的检查。反正，都是脑洞大开了，怎么去研究和测试，留给青少年们去吧，反正都是一种猜想，想想而已。欢迎大家来评论区一起碰水。下回我来给大家继续聊聊NGINX
waf常被人绕过和忽略的中招小姿势。

关于作者：顾问级网络安全专家，首席软件设计师，有多年大型安全产品和渗透工具的开发经验，理论与实践相结合型。专注于大数据分析、数据建模，趋势分析。MYIIS-VIF软件作者(IIS WAF)。  

