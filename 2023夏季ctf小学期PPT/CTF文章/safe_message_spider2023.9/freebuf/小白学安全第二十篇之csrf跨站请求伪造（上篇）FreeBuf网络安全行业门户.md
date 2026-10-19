  
![1.png](https://image.3001.net/images/20180810/1533884380_5b6d37dc2453f.png!small)  

  

### CSRF？

之前学习了SQL注入、XSS，现在又多了一个CSRF，好多名称缩写记不住怎么办？不要急，我们先理解CSRF是什么，有助于我们对名称的记忆。

CSRF（Cross site request
forgery）跨站请求伪造，用一句话解释就是“通过欺骗，使受害者替攻击者执行操作”。什么？没解释清楚，我们再细致分析下CSRF攻击过程：

1、网站存在跨站请求伪造漏洞；

2、攻击者构造恶意URL诱使受害者点击；

3、执行恶意URL中的内容；

  
![2.png](https://image.3001.net/images/20180810/1533884391_5b6d37e7b8ad1.png!small)  

### CSRF漏洞

那什么是CSRF漏洞呢？我们都知道，一些网站当你登录后可以对自己的账户系统进行一些设置，如修改密码。你有没有观察过修改密码后的URL呢？

  
![3.png](https://image.3001.net/images/20180810/1533884400_5b6d37f019e2a.png!small)  

 **[http://192.168.237.134/DVWA-master/vulnerabilities/csrf/?password_new=360&password_conf=360&Change=Change#](http://192.168.237.134/DVWA-master/vulnerabilities/csrf/?password_new=360&password_conf=360&Change=Change#)**当你点击这个URL时，账户密码就修改为了360，这也就是CSRF攻击的本质，攻击者构造的URL能使你毫不知情的执行一些操作。但是直接将修改密码的URL发送给受害者很容易被发现，这时该怎么办呢？

将URL写入另一个页面中，将这个页面的URL发送给受害者，既能伪装攻击意图，还可以执行相应的命令。

  
![4.png](https://image.3001.net/images/20180810/1533884410_5b6d37fa7cb30.png!small)  

CSRF攻击被认为是Web安全领域的沉睡巨人，尽管如果执行得当，是一种隐秘而强大的攻击，但是并没有太多被认真对待，与注入攻击、跨站脚本相比地位要低许多。虽然攻击者无法直接获取受害者系统权限，但攻击者可以使用受害者代替执行操作，所造成的危害是相同的。

了解了CSRF以后，是不是迫不及待想知识该如何防护这种攻击方式了呢，还是留一个悬念，大家自己思考一下，在生活中的网站是怎么防护的，用了什么样的方法，我们下期在叙！

