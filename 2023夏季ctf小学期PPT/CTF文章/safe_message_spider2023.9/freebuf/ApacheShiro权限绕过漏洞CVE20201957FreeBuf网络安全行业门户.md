## ****漏洞分析****

###  ** **1 Apache Shiro组件**** ** **介绍****

Apache
Shiro是一个强大且易用的Java安全框架,执行身份验证、授权、密码和会话管理。使用Shiro的易于理解的API,可以快速、轻松地获得任何应用程序,从最小的移动应用程序到最大的网络和企业应用程序。内置了可以连接大量安全数据源（又名目录）的Realm，如LDAP、关系数据库（JDBC）、类似INI的文本配置资源以及属性文件等。

###  ** **2 漏洞描述****

Apache Shiro
1.5.2之前的版本，由于Shiro拦截器和requestURI的匹配流程与Web框架的拦截器的匹配流程有差异，攻击者构造一个特殊的http请求，可以绕过Shiro的认证，未授权访问敏感路径。

此漏洞有两种攻击方式，第一种攻击方式适用于Shiro < 1.5.0版本，由于Shiro
1.5.0版本修复补丁考虑不全面，导致补丁绕过，出现了第二种攻击方式，适用于Shiro < 1.5.2版本。

###  ** **3 漏洞分析****

 ** **Shiro 1.4.2 - > 1.5.0 版本补丁分析****

对比Shiro 1.4.2与Shiro
1.5.0版本的改动，Shiro在org.apache.shiro.web.filter.PathMatchingFilter类中添加了删除requestURI结尾的/的代码。

![](https://image.3001.net/images/20200908/1599557706.png!small)

![](https://image.3001.net/images/20200908/1599557716.png!small)

 ** **Shiro 1.4.2代码分析****

传入的payload首先被服务器接收，并传送给Shiro拦截器处理(org.apache.shiro.web.servlet.OncePerRequestFilter#doFilter方法作为入口)。

![](https://image.3001.net/images/20200908/1599557735.png!small)

调用createSubject方法创建Subject，并调用execute方法进入Shiro FilterChain中。

![](https://image.3001.net/images/20200908/1599557747.png!small)

![](https://image.3001.net/images/20200908/1599557761.png!small)

进入org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#

getChain方法中，首先获取请求URI路径，之后迭代获取拦截器的表达式。

![](https://image.3001.net/images/20200908/1599557788.png!small)

![](https://image.3001.net/images/20200908/1599557799.png!small)

这里重点关注/hello/*表达式。代码进入pathMatches方法，最终调用org.apache.shiro.util.AntPathMatcher#doMatch方法进行传入的requestURI与拦截器表达式进行匹配。

![](https://image.3001.net/images/20200908/1599557814.png!small)

匹配过程中，分别将拦截器表达式与requestURI以/作为分隔符进行字符串到数组的转换，通过循环匹配数组中对应的元素，判断requestURI是否符合拦截器表达式匹配形式。

![](https://image.3001.net/images/20200908/1599557847.png!small)

如果表达式中存在通配符*，会将containsStar标志位赋值为true，进入 else if (patIdxEnd == 0)判断条件，返回true。

![](https://image.3001.net/images/20200908/1599557866.png!small)

继续跟进代码，在requestURI与拦截器表达式匹配结束后，还会进行一次判断，而漏洞产生的原因也是由于判断的条件。如果Shiro拦截器表达式不以/结尾，且requestURI以/结尾，判断代码将返回false表示匹配失败，从而绕过Shiro认证。

![](https://image.3001.net/images/20200908/1599557900.png!small)

跟进到Spring处理URI的代码，进入org.springframework.web.servlet.handler.AbstractHandlerMethodMapping#getHandlerInternal方法，获取requestURI。

![](https://image.3001.net/images/20200908/1599557924.png!small)

进入lookupHandlerMethod方法，调用addMatchingMappings方法，获取Spring拦截器。

![](https://image.3001.net/images/20200908/1599557947.png!small)

![](https://image.3001.net/images/20200908/1599557960.png!small)

进入org.springframework.web.servlet.mvc.condition.PatternsRequestCondition#getMatchingCondition方法进行调用doMatch方法进行requestURI和拦截器表达式的匹配。

![](https://image.3001.net/images/20200908/1599557978.png!small)

![](https://image.3001.net/images/20200908/1599557989.png!small)

Spring拦截器匹配流程和Shiro大致相同，都是将字符串转换为数组进行匹配。

![](https://image.3001.net/images/20200908/1599558008.png!small)

![](https://image.3001.net/images/20200908/1599558025.png!small)

由于Spring多了一个环节，在检测拦截器表达式与requestURI结尾是否为/之后，并没有直接返回false。而是将拦截器表达式结尾添加/，并继续进行

path.startsWith(this.pathSeparator) != pattern.startsWith(this.pathSeparator)

测试，从而完成了拦截器表达式与requestURI的匹配。

![](https://image.3001.net/images/20200908/1599558044.png!small)

![](https://image.3001.net/images/20200908/1599558056.png!small)

上述攻击方式在Shiro 1.5.0版本中修复，但是被二次绕过，绕过分析如下。

 ** **Shiro 1.5.1 - > 1.5.2 版本补丁分析****

对比Shiro 1.5.1与Shiro 1.5.2版本的改动

![](https://image.3001.net/images/20200908/1599558072.png!small)

Shiro
1.5.2版本中，在进行decodeAndCleanUriString方法之前会先进行URI解析，调用request.getServletPath()和request.getPathInfo()获取ServletPath和PathInfo并进行路径拼接。

 ** **Shiro 1.5.1代码分析****

Shiro 1.5.0 -1.5.1在认证过程中基本没有变化，主要分析一下二次绕过的利用点。还是以org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getChain作为起点。

![](https://image.3001.net/images/20200908/1599558096.png!small)

在获取requestURI时,依旧会在getPathWithinApplication方法中调用getRequestUri方法进行requestURI的解析并获取，但是在URI正规化处理时，先调用decodeAndCleanUriString方法进行路径的解码，并清理URI。

![](https://image.3001.net/images/20200908/1599558124.png!small)

![](https://image.3001.net/images/20200908/1599558137.png!small)

进入decodeAndCleanUriString方法，发现此方法会以分号将传入的URI进行截断，并将分号以及分号后面的数据进行清空，返回分号前面的URI数据，从而让/a/b;/c变为/a/b。

继续跟进到Spring拦截器的decodeAndCleanUriString方法中。

![](https://image.3001.net/images/20200908/1599558157.png!small)

![](https://image.3001.net/images/20200908/1599558168.png!small)

从代码中可以发现，Spring对于分号的处理方式与Shiro不同，Spring会先获取分号的位置，并检测分号后是否存在/，如果有，将/的位置记录在slashIndex变量中，并将分号前的数据与/之后的数据进行拼接，从而让/a/b;/c变为/a/b/c。返回处理后的requestURI。

由于Spring与Shiro的decodeAndCleanUriString方法不同，攻击者可以使用分号构造路径，绕过Shiro认证，并可以匹配Spring的动态控制器。

###  ** **4 漏洞复现****

搭建Apache Shiro漏洞环境，使用构造的payload进行攻击，最终绕过授权访问到未授权资源，效果如图：

 ** **正常访问：****

![](https://image.3001.net/images/20200908/1599558186.png!small)

 ** **Apache Shiro 1.4.2环境****

![](https://image.3001.net/images/20200908/1599558201.png!small)

 ** **Apache Shiro 1.5.1环境****

 ** **![](https://image.3001.net/images/20200908/1599558214.png!small)****

#  ** **影响范围****

目前受影响的Apache Shiro版本：

 ** **Apache Shiro < 1.5.2****

#  ** **修复建议****

Apache
Shiro最新版本已经修复此漏洞，请受漏洞影响的用户下载最新版本，下载链接：http://shiro.apache.org/download.html

#  ** **时间轴****

2020/3/25：Apache Shiro官网披露该漏洞。

2020/9/5 : 深信服千里目安全实验室发布漏洞分析文章。

#  ** **参考链接****

1.<http://shiro.apache.org/download.html>

2.https://github.com/apache/shiro

