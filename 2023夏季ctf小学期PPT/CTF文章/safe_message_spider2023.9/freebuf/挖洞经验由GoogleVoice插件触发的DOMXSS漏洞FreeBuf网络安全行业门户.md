![](https://image.3001.net/images/20200515/1589536423_5ebe66a7a0a37.jpg!small)

**本文讲述了作者在安装了Google Voice插件的环境中，通过Gmail接收邮件时偶尔发现的一个DOM XSS漏洞，经对Google
Voice插件的源代码分析，最终找到了漏洞根源。漏洞获得了谷歌$3,133.7的奖励。**

## 漏洞端倪

该全局性DOM XSS漏洞的发现也纯属偶然，当我构造了oneerror=alert(1)的XSS
Payload进行发送测试，打开了Gmail邮箱收取Google Ads的信件时，突然在Gmail收件箱中跳出了以下弹窗：

![](https://image.3001.net/images/20200515/1589536180_5ebe65b4e8150.png!small)

当时我的反应是，这是一个Google Ads规则触发的存在于Gmail中的存储型XSS，所以立马就想着上报，但仔细一分析，事情没这么简单。

## 漏洞分析

这里存在两方面的因素：我的系统中安装了Google Voice插件、XSS Payload-'444-555-4455 <img src=x
onerror=alert(1)>'是显示在收件箱中的文本字段。

经过分析，我发现该XSS漏洞是由Google
Voice插件引发的，在谷歌本身的用户相关网站accounts.google.com和其它第三方注册网站如facebook.com，都能有效触发并执行javascript代码。如下：

 **  
**

![Y1qEs87.png](https://image.3001.net/images/20200515/1589536221_5ebe65dd2765e.png!small)![OJsMuco.png](https://image.3001.net/images/20200515/1589536231_5ebe65e79bb91.png!small)于是乎，我把Google
Voice的源代码提取出来进行了一番分析，果然在其中的文件contentscript.js中，存在一个方法函数Wg()，就是它导致了DOM
XSS。该函数如下：

    
    
    function Wg(a) {
    
        for (var b = /(^|\s)((\+1\d{10})|((\+1[ \.])?\(?\d{3}\)?[ \-\.\/]{1,3}\d{3}[ \-\.]{1,2}\d{4}))(\s|$)/m, c = document.evaluate('.//text()[normalize-space(.) != ""]', a, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null), d = 0; d < c.snapshotLength; d++) {
    
            a = c.snapshotItem(d);
    
            var f = b.exec(a.textContent);
    
            if (f && f.length) {
    
                f = f[2];
    
                var g = "gc-number-" + Ug,
    
                    h = '<span id="' + g + '" class="gc-cs-link"title="Call with Google Voice">' + f + "</span>",
    
                    k;
    
                if (k = a.parentNode && !(a.parentNode.nodeName in Og)) k = a.parentNode.className,
    
                    k = "string" === typeof k && k.match(/\S+/g) || [], k = !Fa(k, "gc-cs-link");
    
                if (k) try {
    
                    if (!document.evaluate('ancestor-or-self::*[@googlevoice = "nolinks"]', a, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null)
    
                        .snapshotLength) {
    
                        if (0 == a.parentNode.childElementCount) {
    
                            var w = a.parentNode.innerHTML,
    
                                y = w.replace(f, h);
    
                            a.parentNode.innerHTML = y
    
                        } else {
    
                            w = a.data;
    
                            y = w.replace(f, h);
    
                            var u = Qc("SPAN");
    
                            u.innerHTML = y;
    
                            h = u;
    
                            k = a;
    
                            v(null != h && null != k, "goog.dom.insertSiblingAfter expects non-null arguments");
    
                            k.parentNode && k.parentNode.insertBefore(h,
    
                                k.nextSibling);
    
                            Vc(a)
    
                        }
    
                        var t = Ic(document, g);
    
                        t && (Ug++, nc(t, "click", ma(Sg, t, f)))
    
                    }
    
                } catch (E) {}
    
            }
    
        }
    
    }

上述代码理解起来不难，开发者试图从元素内容中查找抓取用户电话号码，然后使用抓取的电话号码作为其内容来创建另一个span元素，以便用户可以直接从网页中点击并实施呼叫操作。

仔细分解开来，在代码的第1行到第9行，用到了document.evaluate方法遍历元素内容，它可以在HTML和XML文档中进行搜索，并返回代表结果的实体XPathResult。也就是说，函数Wg()就是负责抓取元素内容的，它会把所有的文本结点赋值给变量
'a'，以此作为源进行后续处理查找，而以下代码就是导致DOM XPath注入的原因：

    
    
    (var b = /(^|\s)((\+1\d{10})|((\+1[ \.])?\(?\d{3}\)?[ \-\.\/]{1,3}\d{3}[ \-\.]{1,2}\d{4}))(\s|$)/m, c = document.evaluate('.//text()[normalize-space(.) != ""]', a, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null), d = 0; d < c.snapshotLength; d++) {
    
            a = c.snapshotItem(d);

在上述代码之后，当函数Wg()继续执行搜索时，变量'b'会以正则方式在变量'a'中去匹配美国电话号码，如果有匹配结果，则赋值给变量
'f'，接下来，把它定义为变量'h'中的内容。

代码第10和11行主要是检查变量'f'中的HTML元素标记，它既不是形如SCRIPT, STYLE, HEAD, OBJECT, TEXTAREA,
INPUT, SELECT, 或A这样的标记，也不是带有"gc-cs-link"的类属性名，它执行的检查目的在于：

> 1、防止插件与DOM混淆，因为它不想调用诸如SCRIPT、STYLE和HEAD之类的元素上的内容，也不希望用INPUT、SELECT等操作；
>
> 2、如果已经抓取到了电话号码，就停止代码，防止继续遍历循环。

代码第12行到27行中，存在一个if条件，如果其中的k变量为真，则说明找不到类属性名为gc-cs-link的内容，然后它会继续执行一个try声明，而在该try声明中的另一个if条件则会继续执行一个检查，如果找不到名为"googlevoice"的属性和名为"nolinks"的内容元素，则继续循环document.evaluate方法，检查变量'a'中的内容是否具备子元素，以下是其入口逻辑代码：

    
    
    w = a.parentNode.innerHTML,
    
    y = w.replace(f, h);
    
    a.parentNode.innerHTML = y

接着，如果变量'a'中的内容不具备子元素，则将继续执行下一条语句：

    
    
    k.parentNode && k.parentNode.insertBefore(h, k.nextSibling);

## 漏洞修复

我认为开发者可能是想执行变量 'f'中的内容，因为该内容中保存了由(innerHTML,
insertBefore)方法获取的电话变量值，如'+12223334455'，但可能写代码的时候错误地执行了变量'a'
，而在该变量中可以构造形如'444-555-4455 <img src=x onerror=alert(1)>' 的XSS
Payload，然后漏洞就发生了。

## 漏洞奖励

> $3,133.7

 ***参考来源：[missoumsai](http://www.missoumsai.com/google-accounts-xss.html)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

