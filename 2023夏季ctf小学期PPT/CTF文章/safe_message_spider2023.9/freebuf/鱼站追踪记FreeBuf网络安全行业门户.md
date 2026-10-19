[i春秋版主：Sp4ce](https://bbs.ichunqiu.com/thread-41217-1-1.html?from=beef)

  

事情的起因很简单，一哥们在I春秋韩群发了个链接  

![image.png](https://image.3001.net/images/20180604/15281018389360.png!small)

闲的没事干看了下

这个钓鱼用到了凤凰网的一个XSS漏洞，而由于凤凰网是腾讯白名单，所以该链接在发出时是绿标【腾讯被友商坑惨了】

![image.png](https://image.3001.net/images/20180604/15280997722403.png!small)![image.png](https://image.3001.net/images/20180604/15280997804812.png!small)由于该鱼站对访问者的UA和Refer做了检测
所以找一个表哥要了他的iPhone X的UA  

![image.png](https://image.3001.net/images/20180604/15280997914681.png!small)![image.png](https://image.3001.net/images/20180604/15280997994882.png!small)由于chrome在访问带有`<script>`
标签的页面会被拦截  

![image.png](https://image.3001.net/images/20180604/15280998096731.png!small)  

因此换用360“安全”浏览器

首先安装魔变插件，然后添加UA

`Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15
(KHTML, like Gecko) Mobile/15E302 QQ/7.5.8.422 V1_IPH_SQ_7.5.8_1_APP_A
Pixel/1125 Core/UIWebView Device/Apple(iPhone X) NetType/4G QBWebViewType/1`

![image.png](https://image.3001.net/images/20180604/1528099829725.png!small)然后设置代理服务器  

![image.png](https://image.3001.net/images/20180604/15280998391363.png!small)  

然后开始抓包分析 看看到底在哪一步出现了钓鱼网站

由于鱼站用了凤凰网的反射型XSS漏洞，因此第一个请求是凤凰网的

群友发的链接是`[https://m.so.com/tjump?u=//pvp.qq.com%40url.cn/5NCxnuh&?_wv=3FiWJqlkhtY](https://m.so.com/tjump?u=//pvp.qq.com%40url.cn/5NCxnuh&?_wv=3FiWJqlkhtY)`

经过url解码是`[https://m.so.com/tjump?u=//pvp.qq.com@url.cn/5NCxnuh&?_wv=3FiWJqlkhtY](https://m.so.com/tjump?u=//pvp.qq.com@url.cn/5NCxnuh&?_wv=3FiWJqlkhtY)`

这里需要讲下URL中的@作用

对比下下面2个地址栏  

![image.png](https://image.3001.net/images/20180604/15280998748553.png!small)

![image.png](https://image.3001.net/images/20180604/15280998669676.png!small)@符号在URL中会将前面内容无效化（个人理解为注释，比如图一，前面的`pvp.qq.com`就被X掉了），因此图一会访问百度而不是王者农药官网  

因此，整个流程如下  

![image.png](https://image.3001.net/images/20180604/1528099900465.png!small)  

最终鱼站为：

`fhuanxi.aa49b.cn/view.php`

该页面无法直接访问，需要更改UA和加refer

![image.png](https://image.3001.net/images/20180604/1528099910938.png!small)又利用了`hao123`的跳转漏洞：  

![image.png](https://image.3001.net/images/20180604/15280999214146.png!small)![image.png](https://image.3001.net/images/20180604/15280999253966.png!small)  

跳到了`美团`的一个链接

`s3.meituan.net/v1/mss_beb8568dae034a508fb2d11abbf9920e/zhaopin/social%2Ftemp%2Fc91aff92f99df7b726dee1fdcdbee986`

该链接经过请求后会302到t.cn的短链接

![image.png](https://image.3001.net/images/20180604/1528099936376.png!small)`<http://t.cn/R1UYRSJ>`经过请求后会回传一个JS文件  

  

JS文件经过本地搭建测试为钓鱼网站源码【实际为HTML代码经过URLencode后的】

网页代码经过解码格式化后发现了点好玩的

首先是`<http://huanxi.aa49b.cn/template/js/pvp.js>`文件

![image.png](https://image.3001.net/images/20180604/15280999566577.png!small)  

这个文件对iPhone设备做过处理，防止用户认出是钓鱼网站并且对UA做了判断，不是移动设备直接跳到`pvp.qq.com/m`

但是在安卓上就很败笔

【安卓设备，SM-G9300】![image.png](https://image.3001.net/images/20180604/15280999672171.png!small)

【苹果设备：iPhone X】  

![image.png](https://image.3001.net/images/20180604/15280999846675.png!small)  

另外在苹果设备上如果直接访问美团的链接会出现下图

【设备：iPhone
6】![image.png](https://image.3001.net/images/20180604/15280999944924.png!small)

这也解释了为什么鱼站大费周折利用了N多跳转漏洞来进行钓鱼的原因

另外美团的页面好像能加载外部JS![image.png](https://image.3001.net/images/20180604/15281000051560.png!small)接着对HTML代码分析，发现了抽奖JS`<http://www.bzggbl.com.cn/template/js/page.js>`

`![image.png](https://image.3001.net/images/20180604/15281000155187.png!small)  
`

以及一个未知的json.php![image.png](https://image.3001.net/images/20180604/15281000307337.png!small)和登录页面的JS![image.png](https://image.3001.net/images/20180604/15281000388968.png!small)<http://huanxi.aa49b.cn/js/login.js>![image.png](https://image.3001.net/images/20180604/15281000476906.png!small)该页面同样为urlencode后的html，解码后为真正钓QQ的页面![image.png](https://image.3001.net/images/20180604/15281000557894.png!small)钓鱼网站的后台经过几分钟扫出来了![image.png](https://image.3001.net/images/20180604/1528100063539.png!small)<http://huanxi.aa49b.cn/admin__/login.php>![image.png](https://image.3001.net/images/20180604/15281000718702.png!small)  

先小结下

本次跳转链接涉及到的厂商均互为白名单

涉及到厂商及URL跳转数量

> hao123【现属于百度】1个  
> 360搜索1个  
> 腾讯1个  
> 美团1个  
> 凤凰网1个【凤凰网全站均存在不同程度的URL跳转漏洞并多次被利用，希望贵司安全部看到后能自查】

随后动用某平台进行了威胁情报反查  
域名对应IP：`185.243.243.48`

![image.png](https://image.3001.net/images/20180604/152810009217.png!small)域名whios反查：  

注册者 韩琴 （相关域名 498 个）

邮箱 2070169918@qq.com （相关域名 499 个）

可视化：![image.png](https://image.3001.net/images/20180604/1528100126394.png!small)  

鱼站的渗透工作随后与一些表哥展开

[@美团点评SRC](https://bbs.ichunqiu.com/thread-41217-1-1.html?from=beef)
[@360SRC](https://bbs.ichunqiu.com/thread-41217-1-1.html?from=beef)
[@百度SRC](https://bbs.ichunqiu.com/thread-41217-1-1.html?from=beef)
[@腾讯SRC](https://bbs.ichunqiu.com/thread-41217-1-1.html?from=beef)

鱼站用到的文件打包好了，[查看原文](https://bbs.ichunqiu.com/thread-41217-1-1.html?from=beef)即可下载。

截至2018年6月4日 11:20 鱼站已暂停。。  

![image.png](https://image.3001.net/images/20180604/15281001493124.png!small)
**i春秋推出优享会员制，开通会员可以免费畅享多类课程、实验、CTF赛题等付费内容，并可享有包括会员日专属福利、就业推荐等多种特权福利，更多活动详情可点击：[https://bbs.ichunqiu.com/thread-40795-1-1.html](https://bbs.ichunqiu.com/thread-40795-1-1.html?from=qd)**
**了解哦~**  

