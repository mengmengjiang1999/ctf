![](https://image.3001.net/images/20200203/1580724125_5e37ef9dddfdd.png!small)

## See-SURF

 **See-SURF是一款基于Python开发的扫描工具，它可以帮助安全研究人员查找并发现目标Web应用程序中潜在的SSRF参数。**

SSRF(Server-Side Request Forgery:服务器端请求伪造)
是一种由攻击者构造形成由服务端发起请求的一个安全漏洞。一般情况下，SSRF是要目标网站的内部系统。（因为他是从内部系统访问的，所有可以通过它攻击外网无法访问的内部系统，也就是把目标网站当中间人）

SSRF
形成的原因大都是由于服务端提供了从其他服务器应用获取数据的功能，且没有对目标地址做过滤与限制。比如从指定URL地址获取网页文本内容，加载指定地址的图片，文档，等等。

在Web安全领域中，SSRF毫无疑问已经成为了一种严重的安全漏洞，但是行业内貌似我没看到有工具能够自动查找这种类型漏洞参数的工具。因此，See-SURF便应运而生，它可以帮助我们在进行漏洞搜索或Web安全测试时，提供很大的帮助。

### 工具依赖

> Python 3

## 功能介绍

1、可以接收Burp的sitemap作为输入，并使用强大的正则表达式匹配语句来解析文件，并匹配任何包含了潜在SSRF漏洞关键词的GET/POST
URL参数，比如说URL或站点信息等等。除此之外，它还可以检测任意URL或IP地址中的参数值。下面给出的是可分析的样本GET请求：

google.com/url=[https://yahoo.com](https://yahoo.com/)

google.com/q=[https://yahoo.com](https://yahoo.com/)

FORMS -
    
    
    <input type="text" name="url" value="https://google.com" placeholder="https://msn.com">

2、内置多线程网络爬虫，能够尽可能多地收集数据，并解析和识别潜在的SSRF参数。

3、提供了cookie以便支持认证扫描。

4、默认配置下，工具已常规模式运行，开启Verbose模式后，我们将能够查看到不同终端节点的各种漏洞参数。样例如下：

> <https://google.com/path/1/urlToConnect=https://yahoo.com>
>
> <https://google.com/differentpath/urlToConnect=https://yahoo.com>

5、漏洞利用：向Burp Collaboraor或其他HTTP服务器发送包含漏洞参数的外部请求，以确认SSRF漏洞的有效性。

### 工具安装

> git clone<https://github.com/In3tinct/See-SURF.git>
>
> cd See-SURF/
>
> pip3 install BeautifulSoup4
>
> pip3 install requests

## 工具使用

下面这条命令将以默认线程=10的配置运行See-SURF，未开启cookie/session，未开启Verbose模式：

    
    
    python3 see-surf.py -H https://www.google.com

提供Cookie，以空格隔开，实现认证会话爬取：

    
    
    python3 see-surf.py -H https://www.google.com -c cookie_name1=value1 cookie_name2=value2

开启Verbose模式，设置Cookie：

    
    
    python3 see-surf.py -H https://www.google.com -c cookie_name1=value1 cookie_name2=value2 -t 20 -v

其他使用样例：

> <https://google.com/abc/1/urlToConnect=https://yahoo.com>
>
> <https://google.com/123/urlToConnect=https://yahoo.com>

## Burp使用样例

Burp Sitemap(-b和-p)

完整的命令样例：

    
    
    python3 see-surf.py -H https://www.google.com -c cookie_name1=value1 cookie_name2=value2 -b burp_file.xml -p http://72.72.72.72:8000

-b参数可以提供Burp Sitemap文件，以便更好地发现潜在的SSRF参数。这个脚本首先回解析Burp文件，并尝试查找潜在的参数，然后针对目标运行内置的爬虫。

在BurpSuite中查看待分析目标，发送某些GET/POST请求，数量越多越好。然后点击“Target”标签，右键点击“Save selected
Items”，然后保存。提供的脚本运行参数如下：

    
    
    python3 see-surf.py -H https://www.google.com -c cookie_name1=value1 cookie_name2=value2 -b burp_file.xml

![](https://image.3001.net/images/20200203/1580724197_5e37efe550727.png!small)

-p参数将会开启BurpSuite Collaborator，并向主机传递-p参数，或者开启一个Python Http服务器，并等待漏洞参数以执行请求。此时，Payload将会带参数执行，参考样例如下:
    
    
    python3 see-surf.py -H https://www.google.com -c cookie_name1=value1 cookie_name2=value2 -p http://72.72.72.72:8000

![](https://image.3001.net/images/20200203/1580724205_5e37efedb10e4.png!small)

### 工具运行截图

![](https://image.3001.net/images/20200203/1580724219_5e37effbd689e.png!small)

### 许可证协议

See-SURF的开发与发布遵循GNU v3开源许可证协议。

## 项目地址

> See-SURF：【[ _GitHub传送门_](https://github.com/In3tinct/See-SURF)】

 *** 参考来源：[ _In3tinct_](https://github.com/In3tinct/See-SURF)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

