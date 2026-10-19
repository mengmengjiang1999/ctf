目录遍历

目录遍历（路径遍历）是由于web服务器或者web应用程序对用户输入的文件名称的安全性验证不足而导致的一种安全漏洞，使得攻击者通过利用一些特殊字符就可以绕过服务器的安全限制，访问任意的文件（可以使web根目录以外的文件），甚至执行系统命令。

漏洞原理：

程序在实现上没有充分过滤用户输入的…/之类的目录跳转符，导致恶意用户可以通过提交目录跳转来遍历服务器上的任意文件。

读取文件的url：http://www.test.com/my.jsp?file=abc.html

恶意url:http://www.test.com/my.jsp?file=../../Windows.system.ini

漏洞防御：

1.对用户的输入进行验证，特别是路径替代字符“…/”

2.尽可能采用白名单的形式，验证所有输入

3.合理配置web服务器的目录权限

4.程序出错时，不要显示内部相关细节

漏洞位置：

出现在文件读取或者展示图片等对文件读取交互的功能块。

目录遍历

删除框内

![1615367884_60488ecc7943f63ccebe8.png!small](https://image.3001.net/images/20210310/1615367884_60488ecc7943f63ccebe8.png!small)

会出现当前目录

![1615367897_60488ed961503d346cb4b.png!small](https://image.3001.net/images/20210310/1615367897_60488ed961503d346cb4b.png!small)

加入../直接就会爆出整个文件的目录

![1615367905_60488ee1237dbbea18072.png!small](https://image.3001.net/images/20210310/1615367905_60488ee1237dbbea18072.png!small)

敏感信息泄露

敏感数据包括但不限于：口令、密钥、证书、会话标识、License、隐私数据（如短消息的内容）、授权凭据、个人数据（如姓名、住址、电话等）等，在程序文件、配置文件、日志文件、备份文件及数据库中都有可能包含敏感数据

检测方法：

1.检测形式多样，工具爬虫扫描得到敏感文件的路径，从而找到敏感数据，

2.手工挖掘，根据web容器或者网页源代码的查看，找到敏感信息。

漏洞防御：

禁止在代码中存储敏感数据：禁止在代码中存储如数据库连接字符串、口令和密钥之类的敏感数据，这样容易导致泄密。用于加密密钥的密钥可以硬编码在代码中。

禁止密钥或帐号的口令以明文形式存储在数据库或者文件中：密钥或帐号的口令必须经过加密存储。例外情况，如果Web容器的配置文件中只能以明文方式配置连接数据库的用户名和口令，那么就不用强制遵循该规则，将该配置文件的属性改为只有属主可读写。

禁止在 cookie
中以明文形式存储敏感数据：cookie信息容易被窃取，尽量不要在cookie中存储敏感数据；如果条件限制必须使用cookie存储敏感信息时，必须先对敏感信息加密再存储到cookie。

禁止在隐藏域中存放明文形式的敏感数据。

禁止用自己开发的加密算法，必须使用公开、安全的标准加密算法。

禁止在日志中记录明文的敏感数据：禁止在日志中记录明文的敏感数据（如口令、会话标识jsessionid等）， 防止敏感信息泄漏。

禁止带有敏感数据的Web页面缓存：带有敏感数据的Web页面都应该禁止缓存，以防止敏感信息泄漏或通过代理服务器上网的用户数据互窜问题。

目录泄露

在开发者工具中即可看到密码泄露

![1615367917_60488eede3f704bc4484b.png!small](https://image.3001.net/images/20210310/1615367917_60488eede3f704bc4484b.png!small)

Web敏感信息泄露

*phpinfo()信息泄漏

http://[ip]/test.php和http://[ip]/phpinfo.php

* 测试页面泄漏在外网

test.cgi、phpinfo.php、info.php等

* 编辑器备份文件泄漏在外网

http://[ip]/.test.php.swp

http://[ip]/test.php.bak

http://[ip]/test.jsp.old

http://[ip]/cgi~

常见编辑器备份后缀

* 版本管理工具(如git)文件信息泄漏

http://[ip]/.git/config

http://[ip]/CVS/Entriesp

http://[ip]/.svn/entriesp

* HTTP认证泄漏漏洞

http://[ip]/basic/index.php

Web目录开启了HTTP Basic认证，但未限制IP，导致可暴力破解账号、密码

* 管理后台地址泄漏

http://[ip]/login.php

http://[ip]/admin.php

http://[ip]/manager.php

http://[ip]/admin_login.php

* 泄漏员工邮箱、分机号码

泄漏邮箱及分机号码可被社工，也可生成字典

* 错误页面暴漏信息

面熟sql错误、php错误、暴漏cms版本等

* 探针文件

* robots.txt

* phpMyAdmin

* 网站源码备份文件(www.rar/sitename.tar.gz/web/zip等)

* 其他

敏感信息搜集工具

https://github.com/ring04h/weakﬁlescan

https://github.com/lijiejie/BBScan

whatweb

dnsenum

github

相关链接

<https://blog.csdn.net/jpygx123/article/details/83098369>

<https://www.cnblogs.com/bmjoker/p/9096081.html>

