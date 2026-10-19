## 一、起因：

Xray是一个非常好的自动化漏洞挖掘工具。我们通常在进行漏洞挖掘的时候，都会通过BurpSuite+Xray进行自动化的漏洞挖掘，官方也给了配置和使用方法，链接放到参考文献中，感兴趣的朋友也可以自己搜索一下。

工具虽然好用，但这次遇到的是一个有签名算法的目标，在这种情况下，上面的这套组合就显得有气无力了。尝试扫了一下，虽然发送了很多payload，但没有发现任何漏洞。

![](https://image.3001.net/images/20210125/1611544366_600e372eec4fee621b9b3.png!small)

由于从事于漏洞挖掘工作，总有一种感觉（感觉很重要，大家都懂得），这个东西有漏洞。

最后通过自己努力和改造，终于挖到了XSS漏洞。这篇文章主要给大家说说我是怎么挖到这个漏洞的。  
  

> XSS是web安全中最为常见的漏洞，XSS全称是Cross Site
> Script。XSS攻击通常指黑客通过“HTML注入”篡改了网页，插入了恶意脚本，从而控制用户浏览的一种攻击。这里的跨站访问，可以是从正常的网站跨到黑客的服务器，也可以是黑客的服务器跨到正常的网站。XSS漏洞经常出现在需要用户输入的地方，这些地方一旦对输入不进行处理，黑客就可以进行HTML注入，进而篡改网页。

先放一张成功后的图片。

![](https://image.3001.net/images/20210125/1611542998_600e31d61083550ca6ac4.png!small)

## 二、必备工具：

操作系统: WIN10_X64

#### 1\. BurpSuite(Community)

渗透神器，如果你还不知道这个，那么只能说明你不是圈内人，赶快去百度一下吧。  
<https://portswigger.net/burp/communitydownload>

##### 2\. xray(免费社区版):

是从长亭洞鉴核心引擎中提取出的社区版漏洞扫描神器，支持主动、被动多种扫描方式，自备盲打平台、可以灵活定义 POC，功能丰富，调用简单，支持 Windows
/ macOS / Linux 多种操作系统，可以满足广大安全从业者的自动化 Web 漏洞探测需求。  
<https://github.com/chaitin/xray/releases>

#### 3\. jadx:

jadx是个人比较喜欢的一款反编译利器，同时支持命令行和图形界面，能以最简便的方式完成apk的反编译操作。  
<https://github.com/skylot/jadx>

#### 4\. Jython:

Jython本质上是一个Java应用程序，它允许编码人员使用Java编码调用Python库反之，也可以使用Python调用Java的库。  
<https://www.jython.org>

#### 5\. Python:

我使用的是Python3.7

## 三、原理：

### 1、首先看看我们常用的工具组合：

![](https://image.3001.net/images/20210125/1611543012_600e31e47b140b09cc2f8.png!small)

分析一下原因，通过服务器端都是url的请求，应该是这样的处理方法（python伪代码）：

    
    
    #接收到客户端请求
    def Get_Request(param):
    		if param.sign != get_sign(param.url):
    			 return 0
    #开始对参数进行逻辑操作
    

通过上面的图我们可以看出浏览器发出的链接都是直接发送到xray的，所以如果加入了签名算法，那么就直接返回了，根本到不了核心的逻辑。

### 2、改造现有的工具组合：

![](https://image.3001.net/images/20210125/1611543024_600e31f07be2b3b6c246f.png!small)

从上面的图可以看到，先把url发到xray,由xray转发到BurpSuite，在Burp中加入了ptyhon插件对url计算sign，替换了原有的url，这样就可以跳过签名的检测了。

知道了原理。我们就可以行动了。

## 四、最佳实践：

### 1\. 找到需要测试的目标。

这里是的目标是apk文件，打开BurpSuite进行抓包，找到需要渗透测试的请求，发现请求中有sign的字段，应该是有签名校验的。形式如下：

    
    
    https://www.xxxx.com/data?id=12346&imei=aabbcc&sign=88a5e407a1c85d2ef063b8e2007278e9
    

### 2\. 找到sign签名的算法。

关于怎么找算法，不是这篇文章的重点，这里简单介绍一下，无论是apk还是web都是一样的，apk的加密算法通常都放到so文件或者直接在java代码中；web的签名算法，通常都会写到js脚本中，作为一名合格的渗透人员，相信这个应该都不是难事。  
本文的目标算法比较简单，作者把算法直接写到了apk中，使用jadx,搜索sign的字段，很容易就找到了算法：

![](https://image.3001.net/images/20210125/1611543039_600e31ff1571e2dcce46f.png!small)

### 3\. 既然找到算法，下一步，就是开始编写BurpSuite的插件，插件的功能，就是根据url计算出sign的值，替换成新的url进行请求。

我们不造轮子，直接用官方的插件来修改。从Github上下载官方python插件，地址：

<https://github.com/portswigger/python-scripter>

官方有详细的API介绍文档，大家可以参考：

<https://portswigger.net/burp/extender/api/index.html>

贴上我修改后的源码的关键部分：

    
    
    def gen_sign(_uri):
    
     uri = _uri
     secret_key = "AABBBCCDDEEFFGG"
     parsed_tuple = urlparse.urlparse(uri)
     _param_json = urlparse.parse_qs(parsed_tuple.query)
    
     aList=[];
     for _json_key,_json_vaule in _param_json.iteritems():
             aList.append(_json_key)
    
     aList.sort()
     
     for _json_key1 in aList:
             sign +=_json_key1
             sign +=_param_json[_json_key1][0]
    
     sign +=secret_key
     m = hashlib.md5()
     m.update(sign)
     a_md5 = m.hexdigest()
     
     return a_md5
    

### 4\. 加载写好的插件加入到BurpSuite中，并且开启插件（Extender-->Extensions--->Burp Extensions
---->add）。

![](https://image.3001.net/images/20210125/1611543059_600e3213c1e0106e7f212.png!small)

### 5\. 按照上面的原理进行修改后，开始运行，出去吃个饭，回来后，发现XSS漏洞一枚。

  1. ![](https://image.3001.net/images/20210125/1611542973_600e31bdceba42877366e.png!small)

## 五、总结：

通过本文的介绍，相信大家以后遇到有sign校验的目标时，又多了一种处理的方式。当然也可以利用其他的组合，比如：xray+mitmproxy，burpsuite+scan等，总之方法有很多，适合自己就行，在这里只是抛砖引玉一下。只要是能达到目的就可以。

做为一个渗透测试人员，相信大家手上有很多优秀的渗透测试工具，这些工具的组合，就类似于我们手中的魔方，可以任意组合使用，使用的好，就可以事半功倍。

## 六、参考文献：

> [1]. Xray：<https://docs.xray.cool/#/scenario/burp>  
> [2]. burpSuite：<https://portswigger.net/burp>  
> [3]. jadx：<https://github.com/skylot/jadx>  
> [4]. jython: <https://www.jython.org>

