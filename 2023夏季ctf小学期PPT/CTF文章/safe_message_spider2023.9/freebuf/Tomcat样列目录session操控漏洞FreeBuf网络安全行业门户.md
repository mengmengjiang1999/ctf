原创： free雅轩  合天智汇

  

**  
**

**  
**

**友情链接：**

**[tomcat反序列化漏洞(cve-2016-8735)](http://mp.weixin.qq.com/s?__biz=MjM5MTYxNjQxOA==&mid=2652849031&idx=1&sn=c68d1ee5bc516d576b850977c38ee5b5&chksm=bd593f4a8a2eb65c2bfaded735e8188a9787aaaa2933fd4a0a9828d5254b620add355f5d3ca0&scene=21#wechat_redirect)  
**

[
**Tomcat的PUT的上传漏洞(CVE-2017-12615)**](http://mp.weixin.qq.com/s?__biz=MjM5MTYxNjQxOA==&mid=2652848963&idx=1&sn=57c933d581d53ca23dad797f265e90d9&chksm=bd593f8e8a2eb6987bbc039a49345b7150f04bf250a53f275586e80dbb1ca5bd2e69034ad4e6&scene=21#wechat_redirect)  

**[Tomcat后台弱口令上传war包漏洞复现](http://mp.weixin.qq.com/s?__biz=MjM5MTYxNjQxOA==&mid=2652848895&idx=1&sn=8367abae0a4407084664d2c9af981e47&chksm=bd593e328a2eb724ac00369835737de2c89ad7021cea8916c61b670a4a0a2909a07960aa176a&scene=21#wechat_redirect)**

##

 **复现起源：**

近期在项目中碰到的ApacheTomcat中间件愈来愈多，于是乎。想着做一个整理。将ApacheTomcat中间件的几大较为重要的高危漏洞做一个总结整理复现。用作来巩固更新自己的知识库。

在这里感谢公司Bearcat师傅和残忆师傅以及李师傅等指导和共享精神。

题外话：今天我们复现Tomcat样例目录session操控漏洞。在实战中也碰到过一些样例目录examples开放可以操控操控全局session的一些Tomcat。不过该漏洞挺鸡肋的。可能这里因为我们的圈子问题，听大佬说只有发布该漏洞的作者利用成功过，至今也没见过有人利用成功。原因就是后面我们要编写的三个后台登陆页面。

 **漏洞描述：**

ApacheTomcat默认安装页面中存在examples样例目录。里面存放着Servlets、JSP、WebSocket的一些服务脚本和接口等样例。其中Servletsexamples服务样例下存在一个session的样例。该样例可以允许用户对session来进行操控。因为session是全局通用的，所以也就可以利用该样例下的session来操控管理员的session来进行会话传输操控管理员的账户进行恶意操作。

##

##

 **漏洞分析：**

我们直接看核心代码:

  
![图片.png](https://image.3001.net/images/20181115/1542252919_5bece9775dcd8.png!small)  

##

上面的这段session控制的核心代码意思说的是用户通过表单提交name和value两个参数值。然后通过request里的getParameter（）函数获取name和value值。再通过session.setAttribute()函数将获取到的name和value值传递到session里面。即可以在通过前端页面去控制session值来获取管理员权限。

##  

##

漏洞复现：

漏洞复现环境：

Tomcat7.0.88

JDK1.8.0_181

Burp2.0

##

  
![图片.png](https://image.3001.net/images/20181115/1542252928_5bece98083024.png!small)  

这里以自己本地搭建的Tomcat版本为准。也不必刻意寻找相对应的Tomcat版本。

准备好环境之后我们开始复现。

<http://127.0.0.1:8080/examples/servlets/servlet/SessionExample>

我们来到Examples样例目录下的servlets下的session执行按钮。

在Thefollowing data is in
yoursession中我们来执行name名称和value值来获取我们需要的session会话值。下面的GETbased form

我的理解就是通过GET传值的方法来登陆。所以说这项我们就不用去关注了。

  
![图片.png](https://image.3001.net/images/20181115/1542252938_5bece98a36d70.png!small)  

这里我们需要三个页面来辅助我们完成这个漏洞的复现。因为在

Examples样例目录下默认是没有模拟登陆网站的页面，所以我们需要这三个页面来模拟通过操控session值来进行模拟登陆网站的后台获取管理权限。

Login.jsp：

  
![图片.png](https://image.3001.net/images/20181115/1542252946_5bece9928b136.png!small)  

Index.jsp：

![图片.png](https://image.3001.net/images/20181115/1542252952_5bece9989bc9d.png!small)  

Login_test.jsp:

![图片.png](https://image.3001.net/images/20181115/1542252960_5bece9a017a5d.png!small)  

准备好三个页面后放置在examples样例目录下。我们就可以开始复现漏洞了。

首先我们模拟访问index.jsp页面，这时候他没有获取到admin的session值，所以代码逻辑会做一个302跳转重定向到login_test.jsp页面。

  
![图片.png](https://image.3001.net/images/20181115/1542252967_5bece9a7644e0.png!small)  

接下来我们在样例目录下去获取并且传递admin的session。

![图片.png](https://image.3001.net/images/20181115/1542252974_5bece9aeebc54.png!small)  

再进行访问index.jsp页面。这时候获取到了admin的session值。代码逻辑即输出一个登陆成功。

  
![图片.png](https://image.3001.net/images/20181115/1542252981_5bece9b5cb2c4.png!small)  

接下来我们访问login.jsp页面并通过post表单的方法传递一个账户的值进去。即可发现跳转到index.jsp。到此操控session来进行绕过登陆复现完成。

  
![图片.png](https://image.3001.net/images/20181115/1542252988_5bece9bc8be99.png!small)  

##

 **漏洞修复方案：**

禁止访问或者直接删除examples样例目录下的资源。做目录访问权限设置，防止目录遍历。

参考来源：

<http://blog.51cto.com/chenjc/1434858>

