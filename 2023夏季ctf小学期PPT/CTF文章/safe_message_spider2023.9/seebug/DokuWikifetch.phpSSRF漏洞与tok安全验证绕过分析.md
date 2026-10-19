作者： **baolongniu** of Tencent Security Platform Department

### 关于DokuWiki

DokuWiki是一个开源wiki引擎程序，运行于PHP环境下。DokuWiki程序小巧而功能强大、灵活，适合中小团队和个人网站知识库的管理。

### 漏洞简介

DokuWiki最新 2016-06-26a版本存在一个SSRF漏洞，当DokuWiki
fetch.php允许下载外部资源时（fetchsize不为零），外部攻击者可以通过猜解tok绕过安全验证，请求服务器内网资源。

### 漏洞分析

DokuWiki fetch.php文件允许下载外部文件，外部文件地址传递给参数media，但是在请求时候有tok安全校验，请求如下：
`/dokuwiki/lib/exe/fetch.php?media=http://192.168.141.128:80/test.php?test.jpg&tok=0f35df`

安全校验在checkFileStatus()函数中，如图：

![](https://images.seebug.org/content/images/2017/02/97463DFF-6C18-49C9-852D-B9742B2652A1.png-w331s)

由上图中可见，tok安全校验就是把`$media`、`$width`（不传递值为空）和`$height`（不传递值为空）三个变量在media_get_token()函数中计算一下，然后把结算结果和tok参数比对，只有比对一致才能通过校验，继续看media_get_token()函数，如图：

![](https://images.seebug.org/content/images/2017/03/279407BE-93E7-4A70-ACE5-3F64B7A30E32.png-w331s)

由上图中可见，media_get_token()函数把width和token变量）返回。继续看auth_cookiesalt()函数，如图：

![](https://images.seebug.org/content/images/2017/02/C15576F7-23DB-4197-A945-E1769BDFF563.png-w331s)

由上图中可见，`auth_cookiesalt()`的函数值是由DokuWiki
_htcookiesalt2文件存储的盐值，再拼接`session_id()`函数构成的。
`auth_cookiesalt()`函数使用`session_id()`函数生成salt是不安全的，在最新php版本中`session_id()`函数存在一个bug（低版本php不存在），构造如下代码：

    
    
    <?php
    session_name("niubl");
    session_start();
    var_dump(session_id());

直接请求test.php文件返回：

![](https://images.seebug.org/content/images/2017/02/0FACB041-B126-407A-8742-A7BEFEB0121B.png-w331s)

设置Cookie参数niubl值为http://192.168.141.128:80/test.php?test.jpg ，再次请求：

![](https://images.seebug.org/content/images/2017/02/5FD533D9-B7E6-4079-A97C-FC9A1AD442E4.png-w331s)

由上图中可见，php发现Cookie参数niubl值中含有非法字符，但是php并没有重新生成session_id，导致传入的非法字符仍然可用，被`var_dump()`函数打印了出来。
`auth_cookiesalt()`函数使用`session_id()`函数生成salt，现在`session_id()`函数外部可控，且可以接收非法字符串，那么我们找一出使用依赖`auth_cookiesalt()`函数生成数值的代码，就可以推测_htcookiesalt2了。

![](https://images.seebug.org/content/images/2017/02/9C9CE717-DB92-42AD-8C8F-EBAA88E170DC.png-w331s)

上图中getSecurityToken()是用来产生CSRF token的函数，CSRF
token广泛出现在表单中，他的实现和`media_get_token()`函数类似，只是`PassHash::hmac()`函数第二个参数换成了`session_id()`加`$INPUT->server->str('REMOTE_USER')，$INPUT->server->str('REMOTE_USER')`变量在不传递参数的时候值为空，那么我们可以通过传递`session_id()`为fetch.php的media参数，这时`getSecurityToken()`函数就生成了我们进行SSRF攻击时需要校验的tok。`getSecurityToken()`函数广泛用表单token中，测试：

![](https://images.seebug.org/content/images/2017/02/B80FAFEC-AF23-4839-8FEA-0FAB74B2A325.png-w331s)

上图中，传递Cookie参数DokuWiki值http://192.168.141.128:80/test.php?test.jpg
，生成sectok值0f35dfabdb3fb00c4de06facec6c2d43
，他的前6位0f35df就是我们进行SSRF攻击时需要校验的tok值，验证：

![](https://images.seebug.org/content/images/2017/02/8BDAFD80-A353-4348-88E2-D4615FB2033A.png-w331s)

![](https://images.seebug.org/content/images/2017/02/E9BE7FF3-FF0F-452C-9E15-2B1A26610CD4.png-w331s)

### 漏洞修复

php的bug（ https://bugs.php.net/bug.php?id=73860
）已经反馈给php官方开发团队，开发人员认为这个bug导致的漏洞是因为webapp使用了sessiond_id
生成salt，依赖session_id生成salt是不合理的，目前该bug仍未被确认。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/230/>

