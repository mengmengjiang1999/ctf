**作者：Malayke  
本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

### 前言

由于工作原因一直都是网络空间搜索引擎重度用户，包括Shodan/ZoomEye/Censys/Fofa等平台都有过使用经验，甚至自己团队也尝试开发过类似平台。自认为还是非常了解的，在前面看过黑哥写的几篇文章后及国外研究者的一些文章后做了一些尝试，顺带也分享下多年使用搜索引擎的一些搜索套路，希望大家能喜欢，当然这个也是为了迎合下ZoomEye官方写文章送会员的活动
:)

不说废话了，步入正题：

### 1、Cobalt Strike

这个方法最早是在黑哥在medium上发布两篇文章介绍利用ZoomEye识别在野Cobalt
Strike服务器的文章[1][2]介绍的,因为文章是英文写的发布在medium上国内直接访问不到，所以这里再次简单介绍一下。在此之前我们需要提一下Fox-it的工作，是他们最早开始通过网络空间测绘技术去识别追踪在野Cobalt Strike的工作并在他们的blog上发布了对应的研究成果[3]，Cobalt
Strike提供的Web服务是基于NanoHTTPD开源框架开发的，而当时Fox-it工程师发现NanoHTTPD返回banner里存在一个异常的空格“bug”，然后通过这个异常的空格去识别。随后Cobalt
Strike官方在发布的3.13版本了对这个“bug”做了更新处理。

事实上我们不需要这个利用这个所谓的异常的空格“bug”，根据观察Cobalt
Strike的WEB服务返回http头存在比较明显的特征，由此来识别追踪Cobalt Strike。

首先我们看看Cobalt Strike版本小于3.13的，返回banner信息（直接复制的黑哥文章里的内容）

    
    
    ? curl http://x.x.x.x:8081/ -v
    
    - Rebuilt URL to: [http://x.x.x.x:8081/](http://x.x.x.x:8081/)
    - Trying x.x.x.x…
    - TCP_NODELAY set
    - Connected to x.x.x.x (x.x.x.x) port 8081 (#0)
    
    > GET / HTTP/1.1
    Host: x.x.x.x:8081
    User-Agent: curl/7.54.0
    Accept: /
    
    < HTTP/1.1 404 Not Found
    < Content-Type: text/plain
    < Date: Wed, 27 Feb 2019 14:43:19 GMT
    < Content-Length: 0
    <

通过curl直接请求Cobalt Strike的WEB服务器端口主页内容返回http头非常简单并且特征化，直接提取两个关键字符串`"HTTP/1.1 404
Not Found Content-Type: text/plain Date:"`及`"Content-Length: 0"`
(注：这里需要说明下ZoomEye在匹配处理是忽视回车换行的，不提取Date的部分是因为这个这个时间是变化的)，这里我们通过+进行“且”运算（注：这里顺带说明下ZoomEye支持的逻辑运算：空格
为or运算符 表示逻辑“或”运算，+ 为and运算符 表示逻辑“且”运算，- 为 not运算符 表示逻辑“非”运算）

搜索语法如下：

`"HTTP/1.1 404 Not Found Content-Type: text/plain Date:" +"Content-Length: 0"`

[https://www.zoomeye.org/searchResult?q="HTTP/1.1404NotFoundContent-Type:text/plainDate:"+"Content-Length:0"&t=all](https://www.zoomeye.org/searchResult?q="HTTP%2F1.1)

通过采样观察，这个搜索语法得到的结果有不少误报：比如Cobalt
Strike的返回头信息里是没有"Server:"头的，也没有"Connection:"等头，这里我们可以通过-运算(not运算)进行排除,通过尝试我们发现"Server"这个关键词在于ssl等信息里直接运算可能导致漏报，所以我们这里直接使用"Connection:"的not运算，最终搜索语法如下：

`"HTTP/1.1 404 Not Found Content-Type: text/plain Date:" +"Content-Length: 0"
-"Connection:"`

[https://www.zoomeye.org/searchResult?q="HTTP%2F1.1 404 Not Found Content-Type%3A text%2Fplain Date%3A" %2B"Content-Length%3A 0"
-"Connection%3A"](https://www.zoomeye.org/searchResult?q=%22HTTP%2F1.1%20404%20Not%20Found%20%20%20Content-Type%3A%20text%2Fplain%20Date%3A%22%20%2B%22Content-Length%3A%200%22%20-%22Connection%3A%22)

![
](https://images.seebug.org/content/images/2020/08/b06f4e2a-1212-40e2-8032-3a54a3245642.png-w331s)

上面我们提到Cobalt Strike在3.13版本的时候修复了“异常空格bug”的同时也修改了默认返回的http头：（直接复制的黑哥文章里的内容）

    
    
    ? curl http://x.x.x.x:8001/ -v
    
    - Rebuilt URL to: http://x.x.x.x:8001/
    - Trying x.x.x.x…
    - TCP_NODELAY set
    - Connected to x.x.x.x port 8001 (#0)
    
    > GET / HTTP/1.1
    Host: x.x.x.x:8001
    User-Agent: curl/7.54.0
    Accept: /
    
    < HTTP/1.1 404 Not Found
    < Date: Thu, 26 Mar 2020 13:19:16 GMT
    < Content-Type: text/plain
    < Content-Length: 0
    <

可以看到返回的http有内容顺序进行变动：Date:头提前了，所以之前的搜索语法是没办法直接工作了，那么我们按上面提到套路稍微改变下试一下，因为ZoomEye匹配模式不会去考虑回车换行的问题，我们把banner整理为一行：

`HTTP/1.1 404 Not Found Date: Fri, 10 Apr 2020 07:16:27 GMT Content-Type:
text/plain Content-Length: 0`

因为时间是变化的所以分割一下：

    
    
    HTTP/1.1 404 Not Found Date:
    Fri, 10 Apr 2020 07:16:27
    GMT Content-Type: text/plain Content-Length: 0

我们直接取1 +3搜索，并继续使用 -"Connection:"继续排除，得到最终搜索语法：

`"HTTP/1.1 404 Not Found Date:" +"GMT Content-Type: text/plain Content-Length:
0" -"Connection:"`

[https://www.zoomeye.org/searchResult?q="HTTP%2F1.1 404 Not Found Date%3A"
%2B"GMT Content-Type%3A text%2Fplain Content-Length%3A 0"
-"Connection%3A"](https://www.zoomeye.org/searchResult?q=%22HTTP%2F1.1%20404%20Not%20Found%20Date%3A%22%20%2B%22GMT%20Content-Type%3A%20text%2Fplain%20Content-Length%3A%200%22%20-%22Connection%3A%22)

![
](https://images.seebug.org/content/images/2020/08/54b0e4d9-4373-440e-8722-40264aca93bd.png-w331s)

大家如果有兴趣可以去推特等上找一些开源情报信息验证一下。

这里需要说明下这个主要是根据NanoHTTPD的返回头进行识别的尤其是针对Cobalt Strike
3.13之前的版本，所以有可能其他的设备也使用NanoHTTPD这个组件也会被识别出来形成误报，另外在黑哥发布方法后有很多的Cobalt
Strike使用团队开始修改了配置进行伪装，这个也是我这里需要提醒红队注意在使用Cobalt Strike的时候只是修改了证书啥的配置，那是远远不够的。

### 2、Meterpreter

Metasploit 的 Meterpreter
其实常用的方式有tcp也有http(s)的模式，在ZoomEye上有现成Metasploit相关的规则（提示：在搜索框里输入Metasploit及可关联出所有的Metasploit相关的app）：

`app:"Metasploit Rex httpd"` `app:"Metasploit meterpreter metsvc"`
`app:"Metasploit meterpreter"` `app:"Metasploit browser_autopwn"`

这几个规则大多是基于tcp的方式的，并不是这次主要目标。也就是http(s)的方式是我们今天的目标，在2019年的一篇文章里有国外的研究员提到了一个方法，这个方法有点类似Cobalt
Strike上面的方法[4]，都是从http(s)服务返回特征入手，这里我们看一下`msf`的相关代码
`lib/msf/core/handler/reverse_http.rb#L82 [5]`

    
    
        OptString.new('HttpUnknownRequestResponse',
          'The returned HTML response body when the handler receives a request that is not from a payload',
          default: '<html><body><h1>It works!</h1></body></html>'
        ),

返回特征也很明显，于是尝试搜索：`"<html><body><h1>It works!</h1></body></html>"`

<https://www.zoomeye.org/searchResult?q=%22%3Chtml%3E%3Cbody%3E%3Ch1%3EIt%20works!%3C/h1%3E%3C/body%3E%3C/html%3E%22>

很明显这个结果误报太多，我猜MSF开发人员当时就是想模仿Apache的默认返回内容，所以我们还得回到Cobalt
Strike套路上，看看Metasploit Meterpreter http(s)上线模式WEB服务的返回头的信息：

    
    
    - Trying 0.0.0.0:1337...
    - TCP_NODELAY set
    - Connected to 0.0.0.0 port 1337 (#0)
    
    > GET / HTTP/1.1
    Host: 0.0.0.0:1337
    User-Agent: curl/7.68.0
    Accept: /
    
    - Mark bundle as not supporting multiuse
    < HTTP/1.1 200 OK
    HTTP/1.1 200 OK
    < Connection: close
    Connection: close
    < Server: Apache
    Server: Apache
    < Content-Length: 44
    Content-Length: 44
    
    <
    
    - Closing connection 0
    <html><body><h1>It works!</h1></body></html>

在上面提到的国外研究员那篇文章[5]里提了一个特征：真正的Apache的默认返回页面的内容有一个额外的\n，而MSF的没有，于是通过Censys提供的body
hash规则进行匹配搜索[6],随机追踪了几个目标很显然这个方法存在很严重的误报。所以我们这里只能回归到ZoomEye的老套路上了，观察Metasploit
Meterpreter http(s)模式的WEB服务返回banner：

    
    
    HTTP/1.1 200 OK
    Connection: close
    Server: Apache
    Content-Length: 44
    
    <html><body><h1>It works!</h1></body></html>

因为这些没有存在变化的元素，那就直接复制上面的字符段开搜：

`"HTTP/1.1 200 OK Connection: close Server: Apache Content-Length: 44
<html><body><h1>It works!</h1></body></html>"`

当然因为这个Content-Length: 44 已经很唯一了，所以其实我们在简洁一下去掉后面的html内容，最终搜索语法如下：

`"HTTP/1.1 200 OK Connection: close Server: Apache Content-Length: 44"`

[https://www.zoomeye.org/searchResult?q="HTTP%2F1.1 200 OK Connection%3A close
Server%3A Apache Content-Length%3A
44"](https://www.zoomeye.org/searchResult?q=%22HTTP%2F1.1%20200%20OK%20Connection%3A%20close%20Server%3A%20Apache%20Content-Length%3A%2044%22)

![
](https://images.seebug.org/content/images/2020/08/309d92b9-3ceb-416b-8a30-6f919693a627.png-w331s)

### 3、Empire

相比Cobalt
Strike及Metasploit，可能Empire知名度稍微差那么一点点，不过目前也是有不少人在使用，在这里我需要说明一下我之前是没有用过这个东西的所以就不多做其他评价了，本文主要是介绍怎么通过ZoomEye去搜索这些框架，我这里不想现成单独去安装一个去获取指纹，那还有其他套路可以走？

这里我介绍一个很常用的套路：“从其他搜索引擎语法到ZoomEye搜索语法”。再此之前我留意到一个著名FireEye公司的研究者的的一个PPT[7]（这里需要说明下的是这个PPT的主题和本文其实一样的，本文的下面的一些研究的包括Empire等框架目标也是参考了这个PPT）另外顺带说一下题外八卦：

这个PPT里的主题和本文其实是一个主题，之前黑哥也在他的知识星球“黑科技”里吐槽过，大意是说他这个PPT里使用的套路尤其是Cobalt
Strike那部分是有参考了本文开始提到黑哥的那些研究内容的，而且全篇直接忽视了来自中国的ZoomEye，看来川普同学覆盖面还是很广的！

回归正题，在这个ppt里提到了一个Empire的shodan搜索语法：

http.html_hash:"611100469"  
[https://www.shodan.io/search?query=http.html_hash%3A"611100469"](https://www.shodan.io/search?query=http.html_hash%3A%22611100469%22)

这里利用的背后的原理也类似上面Metasploit
Meterpreter提到的问题，这里Empire是想伪装成为IIS服务器，但是因为使用空格、tab的区别导致跟真正的IIS页面不一致导致的，所以国外的研究人员都喜欢从比对这个角度去想办法。那么我们怎么从Shodan这个语法转化为ZoomEye的搜索语法呢？首先我们通过Shodan搜索结果找到如下banner：

    
    
    HTTP/1.0 200 OK
    Content-Type: text/html; charset=utf-8
    Content-Length: 682
    Cache-Control: no-cache, no-store, must-revalidate
    Pragma: no-cache
    Expires: 0
    Server: Microsoft-IIS/7.5
    Date: Wed, 19 Aug 2020 08:33:52 GMT

细心的人可以发现：真假IIS页面的主要区别在html里空格与tab的区别，那为什么你只关注http头呢？其实这个问题上面的例子就用过了那就是
"Content-Length: 682 "，页面内容长度变化都体现在http头Content-Length上，对于正常的IIS7的返回Content-Length 我们可以通过ZoomEye搜索:

`<title>IIS7</title>
[https://www.zoomeye.org/searchResult?q=<title>IIS7</title>](https://www.zoomeye.org/searchResult?q=%3Ctitle%3EIIS7%3C/title%3E)`

正常的为`"Content-Length: 689"`,
而且Empire的返回头的内容及顺序是相对固定的，IIS7本身很多设置相关而有变化，所以我们继续老套路提取http头特征：

`"HTTP/1.0 200 OK Content-Type: text/html; charset=utf-8 Content-Length: 682
Cache-Control: no-cache, no-store, must-revalidate Pragma: no-cache Expires:
0"`

[https://www.zoomeye.org/searchResult?q="HTTP%2F1.0 200 OK Content-Type%3A
text%2Fhtml%3B charset%3Dutf-8 Content-Length%3A 682 Cache-Control%3A no-cache%2C no-store%2C must-revalidate Pragma%3A no-cache Expires%3A
0"](https://www.zoomeye.org/searchResult?q=%22HTTP%2F1.0%20200%20OK%20Content-Type%3A%20text%2Fhtml%3B%20charset%3Dutf-8%20Content-Length%3A%20682%20Cache-Control%3A%20no-cache%2C%20no-store%2C%20must-revalidate%20Pragma%3A%20no-cache%20Expires%3A%200%22)

![
](https://images.seebug.org/content/images/2020/08/5e81c14f-9cf7-4dc0-9168-90b10c44350b.png-w331s)

### 4、SpiderLabs Responder

这个目标同样来自于FireEye公司的研究者的PPT，关于SpiderLabs
Responder的介绍可以自行搜索或者访问项目主页：<https://github.com/SpiderLabs/Responder>
这个框架字纹是由于http头里直接硬编码了Date:头[8]

    
    
    class IIS_Basic_401_Ans(Packet):
    fields = OrderedDict([
    ("Code", "HTTP/1.1 401 Unauthorized\r\n"),
    ("ServerType", "Server: Microsoft-IIS/6.0\r\n"),
    ("Date", "Date: Wed, 12 Sep 2012 13:06:55 GMT\r\n"),
    ("Type", "Content-Type: text/html\r\n"),
    ("WWW-Auth", "WWW-Authenticate: Basic realm=\"Authentication Required\"\r\n"),
    ("PoweredBy", "X-Powered-By: [ASP.NET](http://asp.net/)\r\n"),
    ("AllowOrigin", "Access-Control-Allow-Origin: *\r\n"),
    ("AllowCreds", "Access-Control-Allow-Credentials: true\r\n"),
    ("Len", "Content-Length: 0\r\n"),
    ("CRLF", "\r\n"),
    ])

![ ](https://images.seebug.org/content/images/2020/08/4942eb76-d50d-48a5-a6df-abc0abfa6daa.png-w331s)

从上面的案例或者正常情况来看Date是变化的，可以直接搜索：

`"Date: Wed, 12 Sep 2012 13:06:55 GMT"`

[https://www.zoomeye.org/searchResult?q="Date%3A Wed%2C 12 Sep 2012
13%3A06%3A55
GMT"](https://www.zoomeye.org/searchResult?q=%22Date%3A%20Wed%2C%2012%20Sep%202012%2013%3A06%3A55%20GMT%22)

这里需要注意的是在FireEye那个PPT里强调了"HTTP/1.1 401
Unauthorized",不过在我看来这个是没有必要的，在我看来这个Date:硬编码能撞上的几率那是非常小的，SpiderLabs
Responde是个开源项目，很可能有其他变种或者参考代码的项目，于是我在github上搜索了下确实找到不少：[https://github.com/search?q="Date%3A+Wed%2C+12+Sep+2012+13%3A06%3A55+GMT"&type=Code](https://github.com/search?q=%22Date%3A+Wed%2C+12+Sep+2012+13%3A06%3A55+GMT%22&type=Code)
大部分属于代理中间人框架。

![
](https://images.seebug.org/content/images/2020/08/28903f3e-8938-43bf-9e50-0d837319f02c.png-w331s)

### 5、PoshC2

PoshC2 是基于powershell开发的C2代理框架，介绍详见：<https://github.com/nettitude/PoshC2>
我们这里从另外一个使用网络空间搜索引擎的常用套路：“证书搜索”，在github项目主页搜索Certificate 后找到
<https://github.com/nettitude/PoshC2/blob/9d76be26e4c606c3630d0a54fb0d36566e696526/poshc2/server/Config.py>
代码：

    
    
    Certificate Options
    
    Cert_C = "US"
    Cert_ST = "Minnesota"
    Cert_L = "Minnetonka"
    Cert_O = "Pajfds"
    Cert_OU = "Jethpro"
    Cert_CN = "P18055077"
    Cert_SerialNumber = 1000
    Cert_NotBefore = 0
    Cert_NotAfter = (10 * 365 * 24 * 60 * 60)

看到"P18055077"这个很特别，直接使用ZoomEye证书搜索语法：

`ssl:"P18055077"`

[https://www.zoomeye.org/searchResult?q=ssl:"P18055077"](https://www.zoomeye.org/searchResult?q=ssl:%22P18055077%22)

![
](https://images.seebug.org/content/images/2020/08/a9011638-ace2-4847-8fa9-ebc9144d0030.png-w331s)

这里顺带提一句：证书搜索很可能出现覆盖不全的情况，这个例子里本身搜索出来的结果不太多所以不是很明显，所以遇到其他的例子可以先通过证书搜索的到返回的banner后，再根据提取banner特征去搜索匹配。

### 总结

1、主动扫描探测及网络空间搜索引擎可以协助我们追踪识别各种攻击者痕迹，也非常认同黑哥提出来的“动态测绘”的观点，通过动态测绘关联各种数据可以更加完善攻击者画像，比如上文里介绍的几个框架都是历史上多个APT组织使用过的框架。目前从火眼等多个公司的文章来看，有更多的安全关注到主动扫描及网络空间搜索引擎在APT追踪领域的应用。

2、对于红队来说应该注意到C2服务器的安全，尤其这些渗透攻击框架的默认配置需要做修改，以免被主动扫描追踪。

3、对于蓝队来说网络空间搜索引擎也是威胁情报的来源之一，我们能提前获取某些C2 IP并监控拉黑，或许有意想不到的发现。

### 参考

[1] [Identifying Cobalt Strike team servers in the wild by using
ZoomEye](https://medium.com/@80vul/identifying-cobalt-strike-team-servers-in-the-wild-by-using-zoomeye-debf995b6798)

[2] [Identifying Cobalt Strike team servers in the wild by using ZoomEye(Part
2)](https://medium.com/@80vul/identifying-cobalt-strike-team-servers-in-the-wild-by-using-zoomeye-part-2-acace5cc612c)

[3] [Identifying Cobalt Strike team servers in the wild](https://blog.fox-it.com/2019/02/26/identifying-cobalt-strike-team-servers-in-the-wild/)

[4] [Analysing meterpreter payload with
Ghidra](https://isc.sans.edu/forums/diary/Analysing+meterpreter+payload+with+Ghidra/24722/)

[5] <https://github.com/rapid7/metasploit-framework/blob/76954957c740525cff2db5a60bcf936b4ee06c42/lib/msf/core/handler/reverse_http.rb#L82>

[6]
<https://censys.io/ipv4?q=8f3ff2e2482468f3b9315a433b383f0cc0f9eb525889a34d4703b7681330a3fb>

[7] <https://github.com/aaronst/talks/blob/master/scanttouchthis.pdf>

[8] <https://github.com/SpiderLabs/Responder/blob/master/packets.py>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1301/>

