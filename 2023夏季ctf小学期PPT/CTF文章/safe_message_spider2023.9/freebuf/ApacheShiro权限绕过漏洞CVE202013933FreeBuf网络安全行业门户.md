# **一、** ** **漏洞分析****

###  ** **1.1 Apache Shiro组件**** ** **介绍****

Apache
Shiro是一个强大且易用的Java安全框架,执行身份验证、授权、密码和会话管理。使用Shiro的易于理解的API,可以快速、轻松地获得任何应用程序,从最小的移动应用程序到最大的网络和企业应用程序。内置了可以连接大量安全数据源（又名目录）的Realm，如LDAP、关系数据库（JDBC）、类似INI的文本配置资源以及属性文件等。

###  ** **1.2 漏洞描述****

Apache
Shiro的CVE-2020-11989修补补丁依旧存在缺陷，由于shiro和spring在处理url中仍然存在差别，通过构造特殊的HTTP请求，可以再次绕过授权，访问未授权的信息。

###  ** **1.3 漏洞分析****

使用Apache Shiro
1.5.3进行分析，首先通过补丁对比，比较1.6.0版本和1.5.3版本，可以发现最新版本添加了一个InvalidRequestFilter类，该类从全局上对分号，反斜杠和非ASCII字符进行了过滤。

![](https://image.3001.net/images/20200820/1597891858.png!small)

根据漏洞的描述信息，可以发现该漏洞主要由于是shiro和spring对url的处理存在差别，所以直接去查看它们的区别。断点到shiro对URL的处理方法getPathWithinApplication如下：

![](https://image.3001.net/images/20200820/1597892118.png!small)

首先获取到解码后的url，接着取出其中的路径，最后返回分号之前的路径。其中removeSemicolon函数如下：

![](https://image.3001.net/images/20200820/1597892527.png!small)

后面对处理之后的url去除掉最后的/，并进行匹配，这里面只需要设置授权匹配时使用单*的弱匹配，并传入的构造的payload就可以使其匹配不上。

![](https://image.3001.net/images/20200820/1597892545.png!small)

![](https://image.3001.net/images/20200820/1597892572.png!small)

再看一下spring对url的处理，使用getRequestURI方法，首先获取原始url，然后直接进行分号的去除。

至此，就可以比较出shiro和spring的区别，并构造出payload绕过授权。

##  ** **1.4 漏洞复现****

搭建Apache Shiro 1.5.3漏洞环境，使用构造的payload进行攻击，最终绕过授权访问到未授权资源，效果如图：

![](https://image.3001.net/images/20200820/1597893410.png!small)

#  **二、** ** **影响范围****

目前受影响的Apache Shiro版本： ** **Apache Shiro < 1.6.0****

#  **三、** ** **解决方案****

###  ** **3.1修复建议****

Apache
Shiro最新版本已经修复此漏洞，请受漏洞影响的用户下载最新版本，下载链接：http://shiro.apache.org/download.html

###  ** **3.2 临时解决方案****

使用shiro授权时尽量避免使用单*的ant匹配。可以尝试将下图中的匹配方式更改为map.put(“hello/**”, “authc”)

#  **四、** ** **时间轴****

2020/8/17：Apache Shiro官网披露该漏洞。

2020/8/18 : 深信服千里目安全实验室发布漏洞安全通告。

2020/8/19 : 深信服千里目安全实验室复现漏洞并发布二次公告。

#  **五、** ** **参考链接****

  1. <http://shiro.apache.org/download.html>
  2. [" >https://lists.apache.org/thread.html/r539f87706094e79c5da0826030384373f0041068936912876856835f%40%3Cdev.shiro.apache.org%3E]()
  3. <https://github.com/apache/shiro/compare/shiro-root-1.5.3...shiro-root-1.6.0>

