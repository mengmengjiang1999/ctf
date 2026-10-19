## **前言**

在上篇分析[CVE-2022-26135Atlassian Jira Mobile Plugin
SSRF漏洞](http://mp.weixin.qq.com/s?__biz=Mzg3NDcwMDk3OA==&mid=2247483981&idx=1&sn=66f22ccf39f434401c24ee38ba73a0f2&chksm=cecd8b90f9ba0286ed40e9942dd42a23727c79771a582b6c39afd862a82e0b87f051c037a544&scene=21#wechat_redirect)之后，发现在此之前，jira也曾爆出过身份验证绕过漏洞，CVE编号为cve-2022-0540。趁着环境还热乎，对其产生的原理和代码进行一波分析和学习。

##  **漏洞描述**

Atlassian
Jira是澳大利亚Atlassian公司的一套缺陷跟踪管理系统。该系统主要用于对工作中各类问题、缺陷进行跟踪管理。攻击者可利用此漏洞向目标系统发送特制的HTTP请求，以使用受影响的配置绕过
WebWork 操作中的身份验证和授权要求。

##  **利用范围**

 **Jira**

  * Jira 所有版本 < 8.13.18

  * Jira 8.14.x、8.15.x、8.16.x、8.17.x、8.18.x、8.19.x

  * Jira 8.20.x < 8.20.6

  * Jira 8.21.x

 **Jira Service Management**

  * Jira Service Management 所有版本 < 4.13.18

  * Jira Service Management 4.14.x、4.15.x、4.16.x、4.17.x、4.18.x、4.19.x

  * Jira Service Management 4.20.x < 4.20.6

  * Jira Service Management 4.21.x

##  **漏洞分析**

###  **环境搭建**

本次环境使用docker搭建

Dockerfile

    
    
    FROM atlassian/jira-software:8.13.17
    USER root
    COPY "atlassian-agent.jar" /opt/atlassian/jira/
    RUN echo 'export CATALINA_OPTS="-javaagent:/opt/atlassian/jira/atlassian-agent.jar  -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005 ${CATALINA_OPTS}"' >> /opt/atlassian/jira/bin/setenv.sh

5005为idea debug端口；atlassian-agent.jar项目地址：https://github.com/hgqapp/atlassian-agent，使用maven编译为jar文件即可。

后续创建容器根据提示配置。

![](https://image.3001.net/images/20220818/1660814658_62fe0542de466b36acbf3.png!small)调试源码：将以下三个文件夹设置为Libraries。

    
    
    \atlassian-jira-software-8.13.17-standalone\lib
    \atlassian-jira-software-8.13.17-standalone\atlassian-jira\WEB-INF\classes
    \atlassian-jira-software-8.13.17-standalone\atlassian-jira\WEB-INF\lib

###  **前置知识**

在漏洞分析之前，先简单了解一下Jira相关的背景知识。

 **WebWork**

Jira使用MVC框架WebWork来处理用户发起的WEB请求。每个请求都是使用WebWork action来处理，在其中又使用了其他的utility
and Manager
classes来完成一个任务。作为响应返回给客户端的HTML大部分都是View层的JSP生成的。URL中的”.jspa”后缀标识其后端对应的是一个JSP文件。

 **Seraph**

Seraph是一个开源认证框架，主要由Atlassian开发和维护。Jira、Confluence的登录认证是都由Seraph来负责的。Seraph是通过Servlet的Filter实现的。Seraph的功能只是用来在给定一个Web请求的情况下，将该请求与特定用户相关联。

###  **动态分析**

通过前置知识可以了解到Seraph是一个开源认证框架，也是jira核心身份验证机制。Seraph是通过Servlet和Filter实现的。

查看Filter，发现com.atlassian.jira.security.JiraSecurityFilter.class

在doFilter中调用父方法super.doFilter

![](https://image.3001.net/images/20220818/1660814743_62fe0597046c59afbb0c7.png!small)

com.atlassian.seaph.filter.SecurityFilter#doFilter

这里处于atlassian-seaph-4.0.4.jar中filter也就是seraph过滤器，它会根据请求用户权限进行判断，进一步确定所需要的角色，确定是否需要认证。

![](https://image.3001.net/images/20220818/1660814760_62fe05a89a85a81fc93b7.png!small)

持续跟进，发现会通过循环会出现三种Service

JiraPathService

![](https://image.3001.net/images/20220818/1660814798_62fe05ce4aa1f1ee067aa.png!small)JiraPathService是处理：如果请求的
servlet 路径以 /secure/admin/ 开头，那其角色权限必须是admin（管理员权限）。

![](https://image.3001.net/images/20220818/1660814814_62fe05dee230ae75f67ee.png!small)WebworkService

![](https://image.3001.net/images/20220818/1660814828_62fe05ecbeb51077230c6.png!small)WebworkService则是在actions.xml文件中获取角色所需要的webwork配置。

![](https://image.3001.net/images/20220818/1660814841_62fe05f954d5944f8dfd6.png!small)经过调试，会多次进入getRequiredRoles函数，其中获取URl的方式为getRequestURL。

![](https://image.3001.net/images/20220818/1660814855_62fe0607e96de0a3d4053.png!small)继续跟进发现在通过getRequestURL方式提取请求URL后，会通过提取最后一个/后面的接口产生一个targetURL，这里传入的是/secure/InsightPluginShowGeneralConfiguration.jspa，而targetURL为/InsightPluginShowGeneralConfiguration.jspa

![](https://image.3001.net/images/20220818/1660814870_62fe0616803b3dae8a996.png!small)JiraSeraphSecurityService

![](https://image.3001.net/images/20220818/1660814886_62fe0626d3182572b9b5a.png!small)继续往下就是第三个服务JiraSeraphSecurityService，作用是在所有插件的
atlassian-plugin.xml 文件中获取角色所需的 webwork 操作配置。

![](https://image.3001.net/images/20220818/1660814903_62fe0637073ac71430ac9.png!small)

在跟进JiraSeraphSecurityService时，发现会调用WebworkPluginSecurityServiceHelper.getRequiredRoles，和WebworkService.getRequiredRoles代码是相同的。

![](https://image.3001.net/images/20220818/1660814925_62fe064dd47c2a86c3cf2.png!small)接口权限必须是admin。

![](https://image.3001.net/images/20220818/1660814939_62fe065b79c1935b0a5f0.png!small)

在com.atlassian.jira.web.dispatcher.JiraWebworkActionDispatche中会对jspa进行处理。

service函数会从请求中获取Action名称，后续使用/和。jspa切割字符来获取ActionName。

![](https://image.3001.net/images/20220818/1660814959_62fe066f1f8deeaa782cb.png!small)

![](https://image.3001.net/images/20220818/1660814973_62fe067de0b1b5e3ab515.png!small)在webwork.dispatcher.GenericDispatcher#executeAction函数，会对Action进行检查。

![](https://image.3001.net/images/20220818/1660814989_62fe068d7f0b7af983765.png!small)系列Action工厂。

![](https://image.3001.net/images/20220818/1660815004_62fe069c46fd6953fc61f.png!small)

如上分析，其实目前已经知道在Filter中提取URL的方法是getRequestURL，在Servlet中使用getServletPatch。

在URL加入上“;”，传入/secure/InsightPluginShowGeneralConfiguration.jspa;那么在Filter中无法找到InsightPluginShowGeneralConfiguration.jspa；对应的Action，后续进入Servlrt处理，而getServletPath会将;删除，这样也就绕过了Filter层的认证。

![](https://image.3001.net/images/20220818/1660815019_62fe06abd489257d54931.png!small)但实际效果上，这样还需要进行验证才能访问资源。

![](https://image.3001.net/images/20220818/1660815032_62fe06b8e67f1895158e1.png!small)

继续动态调试发现。

在LookupAliasActionFactoryProxy同样进行了权限检查。

![](https://image.3001.net/images/20220818/1660815053_62fe06cd1557cf0e397c7.png!small)

参考了其他大佬分析的文章，了解到在编写插件的时候可使用webwork1元素添加roles-required属性。这里直接使用受影响的插件insight8.9.10进行复现。

添加角色属性可参考https://developer.atlassian.com/server/jira/platform/webwork/

###  **漏洞复现**

在官网上下载插件Insight8.9.10版本。

![](https://image.3001.net/images/20220818/1660815083_62fe06eb1ac48d386d2fa.png!small)

![](https://image.3001.net/images/20220818/1660815091_62fe06f3bec716ff6e25a.png!small)上传成功后，在未登录的情况下，访问/secure/InsightPluginUpdateGeneralConfiguration.jspa;

![](https://image.3001.net/images/20220818/1660815108_62fe070434aab394c9d14.png!small)

成功绕过登录认证限制。

##  **修复建议**

受影响用户可将产品更新至最新安全版本，具体参考官网公告：

https://jira.atlassian.com/browse/JRASERVER-73650

##  **参考材料**

> 1.https://jira.atlassian.com/browse/JRASERVER-73650
>
> 2.https://developer.atlassian.com/server/jira/platform/webwork/
>
> 3.https://marketplace.atlassian.com/apps/1212137/insight-asset-> management/version-history
>
> 4.https://blog.viettelcybersecurity.com/cve-2022-0540-authentication-bypass-> in-seraph/

