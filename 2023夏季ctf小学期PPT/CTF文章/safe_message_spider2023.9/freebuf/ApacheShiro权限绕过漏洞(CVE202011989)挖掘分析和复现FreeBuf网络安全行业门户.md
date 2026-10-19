## 1.1 状态

完成漏洞挖掘条件分析、漏洞复现。

## 1.2 简介

Apache Shiro作为Java框架，可被用于身份认证、授权等任务。

整合Apache Shiro至Spring Boot中时，请求可能会导致越权绕过身份验证现象的出现，存在两种较好的利用现象，称为利用方法1和利用方法2。

存在安全缺陷的版本：Apache Shiro 1.5.3以前的版本。JDK:1.8.0_181。

## 1.3 漏洞挖掘能力条件

  * 应清晰Spring Boot、Apache Shiro框架源码的逻辑功能。

  * 清晰常见的反过滤、非常规字符的特点。

## 1.4 利用方法1

### 1.4.1 环境

设置Tomcat根目录为“/test/”【仅Apache Shiro
1.5.2有此严格限制】，端口为8088；设置“./admin/*”路径需要认证访问，成功则显示“hello, admin page”，具体配置见源代码
(https://github.com/HYWZ36/HYWZ36-CVE-2020-11989-code/tree/main/springboot-shiro-master0)。

### 1.4.2 目标

绕过认证访问“./admin/*”路径。

### 1.4.3 分析方法

对于输入的恶意URL“http://localhost:8088/;/test/admin/page”，首先采用Shiro进行权限验证处理。Shiro框架的decodeAndCleanUriString方法会根据“；”截取URI“/;/test//admin/page”的前部分内容，从而使得此请求通过权限验证。依次经过的重要类、方法如下：

类+方法

|

关键内容  
  
---|---  
  
org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getChain

|

-  
  
org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getPathWithinApplication

|

String contextPath = getContextPath(request); 【=”/;/test”】  
String requestUri = getRequestUri(request);

#输出内容作为Shiro的权限验证输入值

if (StringUtils.startsWithIgnoreCase(requestUri, contextPath)) {

// Normal case: URI contains context path.

String path = requestUri.substring(contextPath.length());

return (StringUtils.hasText(path) ? path : "/");

} else {

// Special case: rather unusual.

return requestUri;

}  
  
org.apache.shiro.web.util.WebUtils#getRequestUri

|

uri = valueOrEmpty(request.getContextPath()) + "/" +
valueOrEmpty(request.getServletPath()) +
valueOrEmpty(request.getPathInfo());【=”/;/test//admin/page”】

return normalize(decodeAndCleanUriString(request, uri));  
  
org.apache.shiro.web.util.WebUtils#decodeAndCleanUriString

|

int semicolonIndex = uri.indexOf(';');

![1605173147_5facff9b86afefe5fb684.png!small?1605173147735](https://image.3001.net/images/20201112/1605173147_5facff9b86afefe5fb684.png!small?1605173147735)  
  
  
  
随后，在Spring框架中解析URL。关键点是在解码过程中，仅剔除URI中“;”而保全其他所有内容，从而解析得目标路径“/admin/page”。依次经过的重要类、方法如下：

类+方法

|

关键内容  
  
---|---  
  
org.springframework.web.util.UrlPathHelper#getPathWithinServletMapping

|

String pathWithinApp = getPathWithinApplication(request);

String servletPath = getServletPath(request);

return servletPath;  
  
org.springframework.web.util.UrlPathHelper#getPathWithinApplication

|

String contextPath = getContextPath(request); 【=”/;/test”】

String requestUri = getRequestUri(request);

return requestUri;  
  
org.springframework.web.util.UrlPathHelper#getRequestUri

|

String uri = (String)
request.getAttribute(WebUtils.INCLUDE_REQUEST_URI_ATTRIBUTE);
【=”/;/test/admin/page”】

return decodeAndCleanUriString(request, uri);  
  
org.springframework.web.util.UrlPathHelper#decodeAndCleanUriString

|

uri = removeSemicolonContent(uri); 【="//test/admin/ page"】

uri = decodeRequestString(request, uri); 【=" / /test/ admin / page”】

uri = getSanitizedPath(uri); 【=" / /test/ admin/ page”】

return uri;  
  
org.springframework.web.util.UrlPathHelper#getServletPath

|

String servletPath = (String)
request.getAttribute(WebUtils.INCLUDE_SERVLET_PATH_ATTRIBUTE);
【=”/admin/page”】

return servletPath; 【=”/admin/page”】  
  
## 1.5 利用方法2

### 1.5.1 环境

设置Tomcat根目录为“/test/”【仅Apache Shiro
1.5.2有此严格限制】，端口为8081；设置“./admin/*”路径需要认证访问，成功则显示“hello,admin”，具体配置见源代码
(https://github.com/HYWZ36/HYWZ36-CVE-2020-11989-code/tree/main/springboot-shiro-master)。

### 1.5.2 目标

绕过认证访问“./admin/{name}”路径。

### 1.5.3 分析方法

对于输入的恶意URL“http://localhost:8081/test/admin/a%25%32%66a”，首先采用Shiro进行权限验证处理。Shiro框架的decodeRequestString方法会进行两次解码得到URI“/admin/a/a”，并因其分割后的数组长度大于模板“/admin/*”而使得此请求通过权限验证。依次经过的重要类、方法如下：

类+方法

|

关键内容  
  
---|---  
  
org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getChain

|

String requestURI = getPathWithinApplication(request);

if (pathMatches(pathPattern, requestURI)) {……

return null;  
  
org.apache.shiro.web.util.WebUtils#getPathWithinApplication

|

String contextPath = getContextPath(request); 【=”/test”】

String requestUri = getRequestUri(request);  
  
org.apache.shiro.web.util.WebUtils#getRequestUri

|

uri = valueOrEmpty(request.getContextPath()) + "/"
+valueOrEmpty(request.getServletPath()) +valueOrEmpty(request.getPathInfo());
【=" /test/ / admin/a%2fa "】

return normalize(decodeAndCleanUriString(request, uri));  
  
org.apache.shiro.web.util.WebUtils#decodeAndCleanUriString

|

uri = decodeRequestString(request, uri);

return (semicolonIndex != -1 ? uri.substring(0, semicolonIndex) : uri);  
  
org.apache.shiro.web.util.WebUtils#decodeRequestString

|

return URLDecoder.decode(source, enc);  
  
java.net.URLDecoder#decode(java.lang.String, java.lang.String)

|

#可解码“%2f”为“/”

while (i < numChars) {

c = s.charAt(i);

switch (c) {

case '+':

sb.append(' ');

i++;

needToChange = true;

break;

case '%':…………

return (needToChange? sb.toString() : s); 【=”/test//admin/a/a”】  
  
org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#pathMatches

|

return pathMatcher.matches(pattern, path); 【pattern : " / admin/*"，source: " /
admin/ a / a "】  
  
org.apache.shiro.util.PatternMatcher#matches

|

return match(pattern, source);  
  
org.apache.shiro.util.AntPathMatcher#doMatch

|

#判断得模板长度短于URI长度，说明URI和当前模板不属于同一类。

if (pathIdxStart > pathIdxEnd) {

// Path is exhausted, only match if rest of pattern is * or **'s

……

} else if (pattIdxStart > pattIdxEnd) {

// String not exhausted, but pattern is. Failure.

return false;  
  
  

随后，在Spring框架中解析URL。关键点是在解码过程中，仅解码得路径是“/test/admin/a%252f”，因此符合“/admin/{name}”规则得以正常访问。依次经过的重要类、方法如下：

类+方法

|

关键内容  
  
---|---  
  
javax.servlet.Servlet#service

|

-  
  
javax.servlet.http.HttpServlet#doGet

|

-  
  
## 1.6 补丁分析

如下图，修改了org.apache.shiro.web.util.WebUtils#getPathWithinApplication，采用两个标准方法获取URI有效应对了“/;/…”安全缺陷，且无解码操作从而有效应对了“a%25%32%66a”安全缺陷。

![1605173228_5facffec7f0805df89b68.png!small?1605173228752](https://image.3001.net/images/20201112/1605173228_5facffec7f0805df89b68.png!small?1605173228752)

## 1.7 docker复现

加载容器tar为镜像的例子：

cat ./ubuntu-xxx.tar | docker import - ubuntu-new

设置局域网及容器ip、启动容器的例子：

（1）自定义网络

docker network create --subnet=192.168.10.1/24 testnet

（2）启动docker容器

docker run -p 8088:8088 -p 8081:8081 -it --name testt3 --hostname testt3
--network testnet --ip 10.10.10.100 ubuntuxxx:xxx /bin/bash

镜像名称为ubuntu_cve-2020-11989:v1，需开启8088和8081的端口映射功能。

启动进入容器后，复现利用方法1。切换到目录【/springboot-shiro-master0/target】下，执行命令【java -jar
srpingboot-shiro-0.0.1-SNAPSHOT.jar】。随后在宿主机浏览器输入【http://localhost:8088/;/test/admin/page】，成功访问表明复现成功，如下图。

![1605173275_5fad001b417761e3c6a1b.png!small?1605173275543](https://image.3001.net/images/20201112/1605173275_5fad001b417761e3c6a1b.png!small?1605173275543)

复现利用方法2。中断当前程序，切换到目录【/springboot-shiro-master1/target】下，执行命令【java -jar
srpingboot-shiro-0.0.1-SNAPSHOT.jar】。随后在宿主机浏览器输入【http://localhost:8081/test/admin/a%25%32%66a】，成功访问表明复现成功，如下图。

![1605173283_5fad00235d0519c5a8ac8.png!small?1605173283576](https://image.3001.net/images/20201112/1605173283_5fad00235d0519c5a8ac8.png!small?1605173283576)

## 1.8 参考资料

  * https://www.freebuf.com/vuls/249380.html

  * https://xlab.tencent.com/cn/2020/06/30/xlab-20-002/

  * idea 快速创建spring boot项目 以及打包 - 知乎

https://zhuanlan.zhihu.com/p/149736921

