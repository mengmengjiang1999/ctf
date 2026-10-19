近日，在对某个网站进行漏洞挖掘时，发现一个会导致短信轰炸的逻辑漏洞。在用户注册页面，可以获得发送手机验证码的数据包，然后并发的发送该数据包，导致同一个手机号收到大量验证码，造成短信轰炸漏洞。

# Turbo Intruder

Turbo Intruder 是一个 Burp Suite 的插件，用于发送大量 HTTP
请求并分析结果。它旨在通过处理需要异常速度、持续时间或复杂性的攻击来补充 Burp Intruder。  
插件下载地址：<https://github.com/PortSwigger/turbo-intruder>  
关于安装插件中遇到的一些问题，可以看我另一篇博客：[Burpsuite安装Turbo
Intruder插件报错问题](https://blog.s8ark.top/2023/04/07/Burpsuite%E5%AE%89%E8%A3%85Turbo%20Intruder%E6%8F%92%E4%BB%B6%E6%8A%A5%E9%94%99%E9%97%AE%E9%A2%98/)

## 默认脚本race.py解析

Turbo Intruder自带了很多优秀的脚本，我们来分析一下待会儿会用到的race.py脚本。  
![image.png](https://image.3001.net/images/20230425/1682390046_64473c1e88f9f0472c6a5.png!small)

  * 首先，这个脚本定义了一个名为 **queueRequests** 的函数，它接受两个参数：target 和 wordlists。

  * 在函数内部，它创建了一个名为 **engine** 的 RequestEngine 对象，并使用指定的参数初始化它。然后，它使用一个 for 循环向 engine 实例的请求队列中添加 **30 个 HTTP 请求** ，每个连接发送 **100 个请求** ，总共发送 **3000 个请求** 。

  * 在循环内部，使用 **engine.queue()** 方法将请求添加到请求队列中。这个方法接受三个参数：target.req，target.baseInput 和 gate='race1'。其中，target.req 是 HTTP 请求的基本部分（即请求方法、目标 URL、HTTP 版本号和请求头），target.baseInput 是请求的数据体。gate='race1' 表示这些请求会被添加到名为 race1 的队列中，并在请求的最后一个字节被阻塞，直到 engine.openGate('race1') 被调用。

  * 接下来，它调用 engine.openGate('race1') 方法，等待所有的 race1 请求准备就绪，然后发送请求的最后一个字节。

  * 最后，它使用 engine.complete(timeout=60) 方法等待所有的请求完成。

  * 另外，这个脚本还定义了一个名为 handleResponse 的函数，用于处理 HTTP 响应。它接受两个参数：req 和 interesting。其中，req 是 HTTP 响应对象，interesting 是一个布尔值，用于指示是否只对感兴趣的数据进行处理。在函数内部，它将响应添加到名为 table 的列表中。

# 短信轰炸漏洞

短信轰炸(也叫短信炸弹)是一种逻辑漏洞，攻击者利用网站漏洞，对用户的手机号不间断地发送短信，造成轰炸短信满天飞的现象。这种漏洞攻击会对个人用户的生活造成极大困扰，同时也会对网站所属公司的资产上造成冲击。  
造成短信轰炸漏洞的原因大概可以总结为两个，一是没有验证用户是否为正常用户，二是没有限制短信下发的频率。  
防御思路也可以根据这两个方面来展开。针对于用户校验方面，可以通过在发送短信验证之前，增加图形验证码或者是滑块验证等方式来防止机器人恶意攻击。针对于限制短信下发频率方面，可以通过设置时间间隔、次数限制等方式来限制短信下发的频率。

# 实战

在某个网站上发现了用户注册页面中有一个获取验证码  
![image.png](https://image.3001.net/images/20230425/1682390980_64473fc4bc69aaa8ac640.png!small)  
抓一下发送验证码的数据包  
![image.png](https://image.3001.net/images/20230425/1682391079_64474027ecb0a4eee57e5.png!small)  
![image.png](https://image.3001.net/images/20230425/1682391148_6447406c7bf3e30e9c4de.png!small)  
我们看到手机号在POST参数中，把这个数据包发到Turbo Intruder  
记得在请求头加一个`X: %s`(turbo中的`%s`类似于burp
intruder里面的`§s§`，虽然我们没有迭代的变量，但是turbo启动时会检查`%s`)  
![image.png](https://image.3001.net/images/20230425/1682391234_644740c299d9535877e71.png!small)  
并发发送数据包  
![image.png](https://image.3001.net/images/20230425/1682391333_6447412597f8a9bd76b81.png!small)  
我们看到发送结果大部分的长度都为`328`，`328`就是发送成功  
我们可以在手机上收到大量验证码，漏洞利用成功  
![image.png](https://image.3001.net/images/20230425/1682391483_644741bbb1e93f2c2f4b1.png!small)

