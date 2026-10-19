**XSS是一种非常常见的漏洞类型，它的影响非常的广泛并且很容易的就能被检测到。**

攻击者可以在未经验证的情况下，将不受信任的JavaScript片段插入到你的应用程序中，然后这个JavaScript将被访问目标站点的受害者执行【[阅读更多](https://gbhackers.com/a3-cross-site-scripting-xss/)】。

跨站点“Scripter”（又名XSSer）是一个自动化框架，用于检测、利用以及报告基于Web应用程序中的XSS漏洞。

它包含多个尝试绕过某些过滤器的选项，以及各种特殊的代码注入技术。

##  **安装XSSer – XSS**

XSSer支持多平台运行。它需要Python和以下库：

    
    
    - python-pycurl - Python bindings to libcurl
    - python-xmlbuilder - create xml/(x)html files - Python 2.x
    - python-beautifulsoup - error-tolerant HTML parser for Python
    - python-geoip - Python bindings for the GeoIP IP-to-country resolver library

在基于Debian的系统上安装

    
    
    sudo apt-get install python-pycurl python-xmlbuilder python-beautifulsoup python-geoip

## 使用

显示帮助信息“xsser -h”

    
    
    root@kali:~# xsser -h

![Xsserscan1.jpg](https://image.3001.net/images/20180529/15275599522079.jpg!small)

启动简单的注入攻击

    
    
    root@kali:~# xsser -u “http://192.168.169.130/xss/example1.php?name=hacker”

## ![2XSSerscan1
\(1\).jpg](https://image.3001.net/images/20180529/15275599694693.jpg!small)

![3XSSerscan1-1.jpg](https://image.3001.net/images/20180529/15275599989017.jpg!small)

## 选择“ **google** ”作为搜索引擎从Dork注入：

    
    
    root@kali:~# xsser –De “google” -d “search.php?q=”

![4XSSER2scan.jpg](https://image.3001.net/images/20180529/15275600154182.jpg!small)

在这个[KaliLinux教程](https://gbhackers.com/kalitutorials/)中，从URL执行多个注入，自动有效载荷，并建立反向连接。

    
    
    xsser -u “http://192.168.169.130/xss/example1.php?name=hacker” –auto –reverse-check -s

![5XSSERScan.jpg](https://image.3001.net/images/20180529/15275600412881.jpg!small)

简单的URL注入，使用GET，Cookie注入并使用DOM shadow

    
    
    xsser -u “http://192.168.169.130/xss/example1.php?name=hacker” -g “/path?vuln=” –Coo –Dom –Fp=”vulnerablescript”

##
![6XSSERscan4-1.jpg](https://image.3001.net/images/20180529/15275600813511.jpg!small)

![7XSSERscan4-2.jpg](https://image.3001.net/images/20180529/15275601093213.jpg!small)![8XSSERscan4-3.jpg](https://image.3001.net/images/20180529/15275601319255.jpg!small)

## 启发式参数过滤

    
    
    root@kali:~# xsser -u “http://192.168.169.130/xss/example1.php?name=hacker” –heuristic

##
![9XSSER5scan.jpg](https://image.3001.net/images/20180529/15275601509301.jpg!small)

![10XSSER5-1scan.jpg](https://image.3001.net/images/20180529/15275601728623.jpg!small)

## 启动GUI界面

    
    
    root@kali:~# xsser –gtk

你也可以将TOR代理与XSSer一起使用。

XSSER自动化框架来检测，利用和报告XSS漏洞

## 主要特性

> 同时使用GET和POST方法注入。
>
> 包括各种过滤器和绕过技术。
>
> 可以与命令行和GUI一起使用。
>
> 将提供攻击的详细统计数据。

## XSS防御

> 对style属性里面的数据进行严格的检查，并且对于用户输出到xss里面的内容进行适当的CSS编码。
>
> 行严格的JavascriptEncode，将某些字符转义，如 " 变成 \" ，' 变成 \' 等等。
>
> 使用 HTMLEncode 编码，保证你从js输出到HTML的元素和属性不会脱离你的控制。
>
> 使用 JavascriptEncode，对事件里面的js代码进行编码。
>
> 对var变量进行HtmlEncode，那么我就无论如何也构建不了<>任何元素了。也就不可能有<script> 或新建元素利用Onload事件等。

 ***参考来源：[gbhackers](https://gbhackers.com/xsser-automated-framework-detectexploit-report-xss-vulnerabilities/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**  

