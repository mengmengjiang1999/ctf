***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、前言

 **Oracle Fusion
Middleware（Oracle融合中间件）是美国甲骨文（Oracle）公司的一套面向企业和云环境的业务创新平台。该平台提供了中间件、软件集合等功能。Oracle
WebLogic Server是其中的一个适用于云环境和传统环境的应用服务器组件。**

WebLogic中默认包含的wls-wast 与wls9_async_response
war包，由于以上WAR包采用XMLDecoder反序列化机制来处理发送过来的XML数据，远程恶意攻击者可以通过发送精心构造的HTTP请求，在未授权的情况下远程执行命令，获得目标服务器的权限。也就是说，攻击者能够直接获取服务器系统权限，进行数据窃取，进而甚至会威胁受害者的内网安全。

Weblogic因为XMLDecoder反序列化不安全数据导致的漏洞目前有三个，第一个是CVE-2017-3506
，第二个是CVE-2017-10271。这两个历史漏洞的数据输入点在 /wls-wsat/* 目录下。第三个是
CVE-2019-2725，这个漏洞的数据输入点增加了一个/_async/*.

**网藤CRS/ARS产品已全面支持该漏洞的检测与验证，网藤用户可直接登陆**
**[www.riskivy.com](http://www.riskivy.com)** **进行验证。**

##  **二、影响版本**

> Oracle WebLogic Server 10.x
>
> Oracle WebLogic Server 12.1.3

## 三、漏洞危害

1.可通过访问路径/_async/AsyncResponseServiceSoap12判断wls9_async_response组件是否存在。若返回如下页面，请引起关注，及时采取防护措施。  

![2.png](https://image.3001.net/images/20190616/15606616772653.png!small)  

2.可通过访问路径/wls-wsat/CoordinatorPortType，判断wls-wsat组件是否存在。若返回如下页面，则此组件存在。请引起关注，及时采取防护措施。

![3.png](https://image.3001.net/images/20190616/15606617187348.png!small)

## 四、修复方案

### 4.1 配置访问控制策略

可通过配置访问控制策略禁止非法用户访问以下路径

    
    
    /wls-wsat/*
    
    /_async/*

### 4.2 删除不安全文件

删除 wls9_async_response.war 与 wls-wsat.war 文件及相关文件夹，并重启 Weblogic 服务。具体文件路径如下：

    
    
    Oracle WebLogic Server 10.3.x ：
    
    \Middleware\wlserver_10.3\server\lib\
    
    %DOMAIN_HOME%\servers\AdminServer\tmp\_WL_internal\
    
    %DOMAIN_HOME%\servers\AdminServer\tmp\.internal\
    
    Oracle WebLogic Server 12.1.3 ：
    
    \Middleware\Oracle_Home\oracle_common\modules\
    
    %DOMAIN_HOME%\servers\AdminServer\tmp\.internal\
    
    %DOMAIN_HOME%\servers\AdminServer\tmp\_WL_internal\

### 4.3 升级JDK 版本

本次漏洞绕过只生效于JDK6，可升级JDK版本至JDK7及以上。

以上是本次高危漏洞预警的相关信息，如有任何疑问或需要更多支持，可通过以下方式与我们取得联系。

> 联系电话：400-156-9866
>
> Email：help@tophant.com

 ***本文作者：TCC-星光，转载请注明来自FreeBuf.COM**

