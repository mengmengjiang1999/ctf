# **一、** ** **漏洞分析****

###  ** **1.1 Apache Shiro组件**** ** **介绍****

Apache
Shiro是一个强大且易用的Java安全框架,执行身份验证、授权、密码和会话管理。使用Shiro的易于理解的API,可以快速、轻松地获得任何应用程序,从最小的移动应用程序到最大的网络和企业应用程序。内置了可以连接大量安全数据源（又名目录）的Realm，如LDAP、关系数据库（JDBC）、类似INI的文本配置资源以及属性文件等。

###  ** **1.2 漏洞描述****

Apache Shiro
1.5.3之前版本，由于Shiro拦截器与requestURI的匹配流程和Web框架的拦截器的匹配流程有差异，攻击者构造一个特殊的http请求，可以绕过Shiro的认证，未授权访问敏感路径。此漏洞存在两种攻击方式。

###  ** **1.3 漏洞分析****

 ** **First Attack****

传入的payload首先被服务器接收，并传送给Shiro拦截器处理(org.apache.shiro.web.servlet.OncePerRequestFilter#doFilter方法作为入口)。

![](https://image.3001.net/images/20200910/1599737403.png!small)

调用createSubject方法创建Subject，并调用execute方法进入Shiro FilterChain中。

![](https://image.3001.net/images/20200910/1599738069.png!small)

![](https://image.3001.net/images/20200910/1599738081.png!small)

进入org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getChain方法中，首先获取请求URI路径。

![](https://image.3001.net/images/20200910/1599738096.png!small)

在Shiro1.5.2版本中，对于requestURI处理的方式存在一些不同，此处也是漏洞触发点所在。Shiro1.5.2使用的是request.getContextPath()，request.getServletPath()，request.getPathInfo()拼接的方式。由于getServletPath()方法会对requestURI进行一次url解码，在之后的decodeAndCleanUriString方法中进行第二次url解码。

![](https://image.3001.net/images/20200910/1599738110.png!small)

回到getChain方法中，迭代获取拦截器的表达式。

![](https://image.3001.net/images/20200910/1599738127.png!small)

![](https://image.3001.net/images/20200910/1599738140.png!small)

这里重点关注/hello/*表达式。代码进入pathMatches方法，最终调用org.apache.shiro.util.AntPathMatcher#doMatch方法进行传入的requestURI与拦截器表达式进行匹配。

![](https://image.3001.net/images/20200910/1599738154.png!small)

匹配过程中，分别将拦截器表达式与requestURI以/作为分隔符进行字符串到数组的转换，通过循环匹配数组中对应的元素，判断requestURI是否符合拦截器表达式匹配形式。

![](https://image.3001.net/images/20200910/1599738169.png!small)

如果表达式中存在通配符*，会将containsStar标志位赋值为true，进入 else if (patIdxEnd == 0)判断条件，返回true。

![](https://image.3001.net/images/20200910/1599738183.png!small)

最终回到doMatch方法中，通过判断表达式数组的元素个数与requestURI的元素个数，以及表达式中是否包含**，完成后续的匹配。

![](https://image.3001.net/images/20200910/1599738200.png!small)

跟进到Spring处理URI的代码，进入org.springframework.web.servlet.handler.AbstractHandlerMethodMapping#getHandlerInternal方法，获取requestURI。由于Spring获取requestURI时使用getRequestURI()方法，此方法不会进行URL解码。只会在decodeAndCleanUriString完成一次url解码。

![](https://image.3001.net/images/20200910/1599738216.png!small)

进入lookupHandlerMethod方法，调用addMatchingMappings方法，获取Spring拦截器。

![](https://image.3001.net/images/20200910/1599738233.png!small)

![](https://image.3001.net/images/20200910/1599738244.png!small)

进入org.springframework.web.servlet.mvc.condition.PatternsRequestCondition#getMatchingCondition方法调用doMatch方法进行requestURI和拦截器表达式的匹配。

![](https://image.3001.net/images/20200910/1599738257.png!small)

![](https://image.3001.net/images/20200910/1599738273.png!small)

Spring拦截器匹配流程和Shiro大致相同，同样是将字符串转换为数组进行匹配。

![](https://image.3001.net/images/20200910/1599738290.png!small)由于Spring只进行了一次URL解码，所以将未完全解码的部分作为一个整体，从而完成了拦截器表达式与requestURI的匹配。

![](https://image.3001.net/images/20200910/1599738312.png!small)

 ** **Second Attack****

漏洞触发点同样是Shiro在修复CVE-2020-1957漏洞时，使用request.getContextPath()，request.getServletPath()，request.getPathInfo()拼接的方式，进行requestURI的获取。<br>直接跟踪到uri
= valueOrEmpty(request.getContextPath()) + "/" +
valueOrEmpty(request.getServletPath()) + valueOrEmpty(request.getPathInfo());

![](https://image.3001.net/images/20200910/1599738331.png!small)

在调用getContextPath()方法获取context-path时，会调用removePathParameter方法清除掉分号以及分号到下一个/中间的数据。

![](https://image.3001.net/images/20200910/1599738348.png!small)

接下来进入for循环中匹配candidate与conotext-path是否相同。

![](https://image.3001.net/images/20200910/1599738365.png!small)

如果不同，则从传入的URL中继续读取下一级目录，直到condidate与context-path相同，返回从URL截取的目录作为contextPath。由于context-path获取方式和removePathparameters方法对URL的处理，攻击者可以请求，让contextPath变量获取到带有分号的非预期值。

在进行requestURI拼接时，构造出根路径带有分号的requestURI。利用CVE-2020-1957漏洞原理，经过decodeAndCleanUriString方法时，截断reqeustURI中分号后的数据，并返回。从而绕过了shiro权限控制。

 ** **回顾CVE-2020-1957漏洞****

在URI正规化处理时，先调用decodeAndCleanUriString方法进行路径的解码，并清理URI。

![](https://image.3001.net/images/20200910/1599738393.png!small)

![](https://image.3001.net/images/20200910/1599738410.png!small)

进入decodeAndCleanUriString方法，发现此方法会以分号将传入的URI进行截断，并将分号以及分号后面的数据进行清空，返回分号前面的URI数据，从而让/a/b;/c变为/a/b。

继续跟进到Spring拦截器的decodeAndCleanUriString方法中。

![](https://image.3001.net/images/20200910/1599738432.png!small)

![](https://image.3001.net/images/20200910/1599738444.png!small)

从代码中可以发现，Spring对于分号处理的方式与Shiro不同，Spring会先获取分号的位置，并检测分号后是否存在/，如果有，将/的位置记录在slashIndex变量中，并将分号前的数据与/之后的数据进行拼接，从而让/a/b;/c变为/a/b/c。返回处理后的requestURI。

 ** **补丁分析****

对比Shiro 1.5.2与Shiro
1.5.3版本的改动，在org.apache.shiro.web.util.WebUtils类中添加了删除requestURI结尾的/的代码。

![](https://image.3001.net/images/20200910/1599738461.png!small)

![](https://image.3001.net/images/20200910/1599738473.png!small)

![](https://image.3001.net/images/20200910/1599738487.png!small)

补丁主要优化了getPathWithinApplication方法，并单独定义了getServletPath方法，getPathInfo方法。补丁修复后，调用getPathWithinApplication方法获取requestURI只会在进行getServletPath方法中进行一次url解码，保持与Spring获取requestURI过程中相同的url解码次数。防御了双重url编码绕过。

获取requestURI直接调用getServletPath方法和getPathInfo方法进行拼接，由于不需要与contextpath拼接，从而防御了First
Attack攻击。

###  ** **1.4 漏洞复现****

搭建Apache Shiro漏洞环境，使用构造的payload进行攻击，最终绕过授权访问到未授权资源，效果如图：

 ** **正常访问：****

![](https://image.3001.net/images/20200910/1599738526.png!small)

 ** **First Attack****

![](https://image.3001.net/images/20200910/1599738539.png!small)

 ** **Second Attack****

 ** **![](https://image.3001.net/images/20200910/1599738551.png!small)****

#  **二、** ** **影响范围****

目前受影响的Apache Shiro版本：

 ** **Apache Shiro < 1.5.3****

#  **三、** ** **修复建议****

Apache Shiro最新版本已经修复此漏洞，请受漏洞影响的用户下载最新版本，
下载链接：http://shiro.apache.org/download.html

#  **四、** ** **参考链接****

1.<http://shiro.apache.org/download.html>

2.https://github.com/apache/shiro

