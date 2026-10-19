拿到一个系统后，很多情况下只有一个登录入口。如果想进一步得到较为高危的漏洞，只能去寻找权限校验相关的漏洞，再结合后台洞，最终得到一个较为满意的漏洞。  
这里列出一些较为常见的安全认证配置：

  * Spring Security

  * Apache Shiro

  * 服务器本身(Tomcat、Nginx、Apache）401 认证

  * Tomcat 安全认证(结合Web.Xml) 无需代码实现

  * JSON Web Token

以上只是简单列出了一些笔者见过的、常见的安全认证配置组件。不同的鉴权组件存在异同的审计思路。

##  **寻找未授权**

这是笔者首先会入手去看的点，毕竟如果能直接从未授权的点进入，就没必要硬刚鉴权逻辑了。

 **1.一些第三方组件大概率为未授权应用**

###
Druid、Webservice、Swagger等内置于程序中的应用大多被开发者设计为无需权限校验接口。![](https://image.3001.net/images/20220121/1642760391_61ea88c7edf2bb07d8657.jpg!small)第三方组件本身又存在历史漏洞，且以jar包的形式内置于应用中，低版本的情况很常见。  
利用Druid的未授权获取了管理员session：![](https://image.3001.net/images/20220121/1642760406_61ea88d617001b1f08088.jpg!small)
**2.安全认证框架配置中存在的未授权接口**

出于业务需要或者开发失误，开发者会对外开放一些接口，这些接口无需访问权限。细心查看配置文件中各个Filter、Servlet、Listener，可能有意想不到的收获。![](https://image.3001.net/images/20220121/1642760419_61ea88e3cdb7d5c721ddc.jpg!small)Web.Xml  
这里是以拦截器的方式，对外开放了未授权请求处理：![](https://image.3001.net/images/20220121/1642760510_61ea893e7d40051d95cc9.jpg!small)Spring-mvc.Xml  
![](https://image.3001.net/images/20220121/1642760519_61ea8947ee484465adcc2.jpg!small)Tomcat
安全配置  
Apache Shiro、Spring
Security等支持以@Configuare注解方式配置权限认证——只要按照配置去寻找。当然以上框架也支持配置文件方式配置，寻找思路一样。![](https://image.3001.net/images/20220121/1642760540_61ea895caa4f24c4360ff.jpg!small)配置类

 **3.未授权访问接口配合ssrf获取localhost本身需鉴权服务**

一些多服务组件中，存在服务之间的相互调用。服务之间的相互调用或许不需要身份校验，或者已经配置了静态的身份凭证，又或者通过访问者IP是否为127.0.0.1来进行鉴权。

这时我们需要一个SSRF漏洞即可绕过权限验证。很经典的为Apache Module mod_proxy场景绕过：SSRF CVE-2021-4043。

##  **安全认证框架本身存在鉴权漏洞**

###  **1.Apache Shiro**

Shiro相关的权限绕过漏洞，我觉得可以归类到下面的路径归一化的问题上。

###  **2.Spring Security**

### 某些配置下，存在权限绕过——当配置文件放行了/**/.js时。  
![](https://image.3001.net/images/20220121/1642760575_61ea897f7a2d6aadea7bb.jpg!small)  
![](https://image.3001.net/images/20220121/1642760582_61ea8986ea7d813df297f.jpg!small)
**3.JWT 存在的安全风险**

  * 敏感信息泄露

  * 未校验签名

  * 签名算法可被修改为none

  * 签名密钥爆破

  * 修改非对称密码算法为对称密码算法

  * 伪造密钥(CVE-2018-0114)

jwt测试工具：https://github.com/ticarpi/jwt_tool

##  **静态资源访问**

静态资源css、js等文件访问往往不需要权限，开发者可能将鉴权逻辑放在Filter里。当我们在原有路由基础上添加.js后缀时，即可绕过验证。![](https://image.3001.net/images/20220121/1642760598_61ea89966d2235cf32577.jpg!small)这里可能会有一个问题，添加了.js后缀后是否还能正常匹配到处理类呢？

答案是，在spring应用里是可以的。默认配置下的spirng
configurePathMatch支持添加后缀匹配路由，如果想开启后缀匹配模式，需要手动重写configurePathMatch方法：![](https://image.3001.net/images/20220121/1642760607_61ea899f094acb8ca98cf.jpg!small)
**路径归一化问题**

###  **1.简单定义**

两套组件对同一个URI解析，或者说处理的不一致，导致路径归一化问题的产生。

orange 的 breaking parser logic是他在2018黑帽大会上的演讲议题，后续许多路径归一化的安全问题，都是延伸自他的PPT。

###  **2.Shiro权限绕过漏洞**

一个很经典的路径归一化问题，导致权限的绕过，比如Shiro CVE-2020-1957。

针对用户访问的资源地址，也就是URI地址，shiro的解析和 spring的解析不一致。

shiro的Ant中的*通配符匹配是不能匹配这个URI
的/test/admin/page/。shiro认为它是一个路径，所以绕过了/test/admin/*这个ACL。

而spring认为/test/admin/page和/test/admin/page/是一样的，它们能在spring中获取到同样的资源。

###  **3.CVE-2021-21982 VMware CarbonBlack Workstation**

算是一个老1day了，组件本身身份验证通过Spring Security + JWT来实现。且存在两套url的处理组件：Envoy以及Springboot。

PS：Envoy是专为大型现代SOA（面向服务架构）架构设计的L7 代理和通信总线。

通过diff可以定位到漏洞点，一个本地获取token的接口：![](https://image.3001.net/images/20220121/1642760621_61ea89ad7e1a963f5b237.jpg!small)但是我们通过外网直接访问无法获取到token：![](https://image.3001.net/images/20220121/1642760630_61ea89b61a1ad4fb300bc.jpg!small)简单了解一下组件的基本架构：![](https://image.3001.net/images/20220121/1642760639_61ea89bf3b8298febe5ef.jpg!small)抓一下envoy
与本机服务的通信。rr师傅yyds：

“./tcpdump -i lo -nn -s0 -w lo1.cap -v”

envoy本身起到一个请求转发作用，可以精确匹配到协议ip端口
url路径等，指定很详细的路由转发规则，且可以对请求进行转发和修改：![](https://image.3001.net/images/20220121/1642760646_61ea89c6aed18eaeee15b.jpg!small)url编码即可绕过envoy的转发规则，POC如下：![](https://image.3001.net/images/20220121/1642760654_61ea89ce7e20bc9b1ff1c.jpg!small)由于envoy转发规则不能匹配URL编码，但Springboot可以理解，两个组件对url的理解不同，最终导致漏洞产生。

###  **3.Other**

扩展一下思路，当存在一个或者多个代码逻辑处理url时，由于对编码、通配符、"/"、";" 等处理的不同，极有可能造成安全问题。

##  **Apache、Nginx、Jetty、HAProxy 等**

Chybeta在其知识星球分享了很多：Nginx 场景绕过之一: URL white spaces +
Gunicornhttps://articles.zsxq.com/id_whpewmqqocrw.htmlNginx 场景绕过之二：斜杠(trailing
slash) 与 #https://articles.zsxq.com/id_jb6bwow4zf5p.htmlNginx
场景绕过之三：斜杠(trailing slash) 与
;https://articles.zsxq.com/id_whg6hb68xkbd.htmlHAProxy 场景绕过之一:
CVE-2021-40346https://articles.zsxq.com/id_ftx67ig4w57u.html利用hop-by-hop绕过：结合CVE-2021-33197https://articles.zsxq.com/id_rfsu4pm43qno.htmlSquid
场景绕过之一: URN bypass ACLhttps://articles.zsxq.com/id_ihsdxmrapasa.htmlApache
Module mod_proxy 场景绕过：SSRF CVE-2021-4043。

##  **简单的fuzz测试**

造成权限绕过的根本原因可能有多种，但是不妨碍我们总结出一些常见的绕过方式——编码、插入某些特定字符、添加后缀等。远海曾公布一个权限绕过的fuzz字典：![](https://image.3001.net/images/20220121/1642760664_61ea89d87deb8630a9b0f.jpg!small)最后，放上参考链接，大家可以自行学习。

<https://wx.zsxq.com/dweb2/index/group/555848225184>

<https://www.vmware.com/security/advisories/VMSA-2021-0005.html>

<https://cloud.tencent.com/developer/article/1552824>

