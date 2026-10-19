***本文原创作者：NT00，本文属FreeBuf原创奖励计划，未经许可禁止转载**

## 前言

 **这一章介绍如何使用BeEF来** **测试用户和浏览器，攻击用户和浏览器的效果相对于上一章来说比较简单，效果也直接有效。**

查看之前的五篇文章：

> [浏览器攻击框架BeEF Part 1](http://www.freebuf.com/articles/web/175755.html)
>
> [浏览器攻击框架BeEF Part 2：初始化控制](http://www.freebuf.com/articles/web/176139.html)
>
> [浏览器攻击框架BeEF Part 3：持续控制](http://www.freebuf.com/articles/web/176550.html)
>
> [浏览器攻击框架BeEF Part
> 4：绕过同源策略与浏览器代理](http://www.freebuf.com/articles/web/176873.html)
>
> [浏览器攻击框架BeEF Part
> 5：攻击Web应用与攻击网络](http://www.freebuf.com/articles/web/176912.html)

## 攻击用户

攻击用户可分为三部分：内容劫持、捕获用户输入、社会工程学。

### 内容劫持

内容劫持是指替换被勾连的浏览器中当前页面内容，比如替换被勾连的浏览器中当前页面中所有的<a>元素的href。

BeEF自带了很多内容劫持相关的攻击模块：

![攻击模块](https://image.3001.net/images/20180729/1532859774_5b5d957e0ce6e.png!small)上图中Get
xxx系列的攻击模块就是简单获取xxx，比如Get Cookie 就是获取勾连浏览器当前页面的Cookie，Get Form Values
就是获取From表单中值。Replace HREFs系列就是替换所有<a>元素中的HREF属性，比如常用的Replace
HREFs是循环替换所有<a>元素的HREF属性，Replace HREFs(Click Events)和Replace
HREFs类似，唯一的区别是只有onClick 事件发生时才触发修改HREF属性。Replace
HREFs(HTTPs)是把所有指向https站点的链接改写为http协议。Redirect
Browser模块是把被勾连的浏览器重定向到指定的页面。Replace
Content（Deface）是直接修改页面的内容。这些功能可以窃取一些内容，也可以配合钓鱼网站来攻击用户。

### 捕获用户输入

捕获用户的输入也就是我们常说的键盘记录器，BeEF通过使用焦点事件，键盘事件，鼠标和指针事件这四个事件来实时监控着用户的操作。其中焦点事件是指用户的焦点是否还在被勾连的页面，下面笔者在一个被勾连的浏览器中分别触发四个事件：

![分别触发四个事件](https://image.3001.net/images/20180729/1532861590_5b5d9c96403f6.png!small)

然后来看看BeEF中实时的返回：

###
![实时的返回](https://image.3001.net/images/20180729/1532861632_5b5d9cc05a0dc.png!small)

### 社会工程学

BeEF有一个目录，里面是专门用于社会工程学的攻击模块：

![用于社会工程学的攻击模块](https://image.3001.net/images/20180729/1532863095_5b5da277111ec.png!small)这里笔者挑Pretty
Theft（完美盗窃）来演示， 演示环境是上一章演示攻击Web应用时用到的metasploitable2 dvwa + BeEF + kali。

名称  
| 角色  
| ip  
---|---|---  
Ubuntu | BeEF服务器 / metasploit  
| 外网  
kali | 攻击者 | 外网  
Windows7 / 浏览器A  | 受害者 | 内网 10.0.2.4  
metasploitable2  | 内网有漏洞的主机 | 内网 10.0.2.5  
  
Pretty Theft 攻击模块会在被勾连浏览器上弹出一个弹框，然后通过欺骗性的语句来使用户输入帐号和密码。当网站有http-only这个响应首部，无法窃取cookie时，可以使用完美盗窃这个模块来窃取用户的帐号和密码。

使用Pretty Theft前，需要做一些参数的设置：

![参数设置](https://image.3001.net/images/20180729/1532869698_5b5dbc42cf0c8.png!small)点击Execute运行，
被勾连的浏览器会有一个提示性的弹框弹出：

![提示性的弹框](https://image.3001.net/images/20180729/1532869772_5b5dbc8c53311.png!small)如果用户输入帐号和密码：

![输入帐号和密码](https://image.3001.net/images/20180729/1532869811_5b5dbcb33c69a.png!small)那么在BeEF的管理UI上就能看到了帐号和密码：

![看到帐号和密码](https://image.3001.net/images/20180729/1532870067_5b5dbdb3a76ec.png!small)

读者可能注意到了，Pretty
Theft默认下弹出的诱惑性弹框中所使用的语言是英文。在国内效果肯定要打折扣了。所以要修改一下，在beef/modules/social_engineering/pretty_theft/command.js中修改：

![修改文件](https://image.3001.net/images/20180729/1532870373_5b5dbee51777d.png!small)修改后的效果如下：

![修改后的效果](https://image.3001.net/images/20180729/1532870567_5b5dbfa749c74.png!small)样貌有点不太好看，主要是因为logo太大了，如果读者懂得js和html，那么你也可以在beef/modules/social_engineering/pretty_theft/command.js中自己定制一个好看一些的。这样可信度就会提高很多了。

除了pretty_theft外还有一些社会工程学的攻击模块，这些就留给读者自行测试了。

## 攻击浏览器

攻击浏览器的技术，笔者只介绍一个：联合metasploit来攻击浏览器。演示的环境与上面演示pretty_theft是一样的。

要使用Metasploit + BeEF之前，需要做一下设置。

首先要在BeEF中修改beef/extensions/metasploit/config.yaml配置文件：

![修改配置文件](https://image.3001.net/images/20180811/1533975989_5b6e9db507d4e.png!small)  

上图中的port, user, pass 需要与下面在msf中启动MSGRPC接口中的port, user, pass一样。而图中最下面的"{os:
'custom', path:'/opt/metasploit-framework/'}"要根据实际情况来改，这里写的是msf的路径，这里笔者是在Ubuntu中安装了msf，所以路径是/opt/metasploit-framework/, 如果读者是使用kali来测试，那么默认已经有写路径了。

接着修改beef/config.yaml, 设置开启metasploit模块：

![开启metasploit模块](https://image.3001.net/images/20180805/1533433798_5b6657c6020bb.png!small)设置好BeEF后，现在来开启Metasploit的MSGRPC接口，
先在一个空白文件msf_beef.txt中写入：

    
    
    load msgrpc ServerHost=127.0.0.1 ServerPort=xxxx User=msf Pass=xxxxx  
    

ServerPort, User, Pass 需要与BeEF中设置的一样。 接着启动msf服务器，
因为笔者是在远程的服务器上启动msf的，而且msf必需保持运行状态，所以笔者使用screen命令来启动msf。这样即使我关闭了ssh连接，也可以保证msf保持运行状态：

    
    
    screen -S msf   //创建一个名为msf的session  
    msfconsole -r msf_beef.txt    //启动msf，并启动msgrpc接口  
    

启动成功后，会有如下图的输出：

![输出结果截图](https://image.3001.net/images/20180805/1533434634_5b665b0a8b2f9.png!small)接着按住Ctrl键
+ a + d， 暂时离开"msf" session窗口， 回到原本的窗口。 这样即使退出了ssh连接， "msf"session还是会在继续运行。  

    
    
    screen  -ls   //可以看到当前有多少个session窗口在运行
    screen  -r  id  //可以进入到 某个session窗口  
    

启动了msfconsole之后， 就可以启动BeEF了。这个顺序不能反了，需要先启动msfconsole，才能启动BeEF。

    
    
    nohup ./beef &  
    

现在环境设置好了。 说一下BeEF + msf攻击原理， 原本如果只是使用metasploit
来攻击浏览器（这里是IE8），那么metasploit会生成一个URL，如果IE访问了这个URL，那么就会中招。

![中招](https://image.3001.net/images/20180811/1533977137_5b6ea231ea3b9.png!small)现在有BeEF，
BeEF可以把metasploit生成的URL嵌入到被勾连浏览器的一个iframe中。通过msgrpc接口，可以直接在BeEF的管理UI中设置metasploit的参数并直接使用msf的exploit模块。

![使用msf的exploit模块](https://image.3001.net/images/20180811/1533979145_5b6eaa09ae520.png!small)这里笔者挑了ms11_003_ie_css_import来做测试
， 在BeEF的metaspliot 目录下可以找到。 设置好参数之后点击Execute就可以运行了。  

回到Ubuntu服务器， 查看msfconsole控制台：

![查看msfconsole控制台](https://image.3001.net/images/20180811/1533979551_5b6eab9f12740.png!small)可以看到回连了meterpreter。在测试的时候，要确保网络的速度，
笔者因为网速问题，测了好几次才成功。

## 结语

这一章就到这里了，这个系列也完结了。

 ***本文原创作者：NT00，本文属FreeBuf原创奖励计划，未经许可禁止转载**

