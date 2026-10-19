3月30日，Spring框架曝出RCE 0day漏洞。已经证实由于 SerializationUtils#deserialize 基于 Java
的序列化机制，可导致远程代码执行 (RCE)，使用JDK9及以上版本皆有可能受到影响。

相关监测发现该漏洞可能已被远程攻击者利用，国家信息安全漏洞共享平台（CNVD）已收录了Spring框架远程命令执行漏洞（CNVD-2022-23942），考虑到Spring框架的广泛应用，FreeBuf对漏洞评级为：危险。

目前，漏洞利用细节已大范围公开，Spring官方已发布补丁修复该漏洞。

![](https://image.3001.net/images/20220330/1648598879_62439f5fc106ced1886ee.png!small)

## 漏洞描述：

作为目前全球最受欢迎的Java轻量级开源框架，Spring允许开发人员专注于业务逻辑，简化Java企业级应用的开发周期。

但在Spring框架的JDK9版本（及以上版本）中，远程攻击者可在满足特定条件的基础上，通过框架的参数绑定功能获取AccessLogValve对象并诸如恶意字段值，从而触发pipeline机制并
写入任意路径下的文件。

目前已知，触发该漏洞需要满足两个基本条件：

  * 使用JDK9及以上版本的Spring MVC框架
  * Spring 框架以及衍生的框架spring-beans-*.jar 文件或者存在CachedIntrospectionResults.class

## 漏洞影响范围：

> 版本低于5.3.18和5.2.20的Spring框架或其衍生框架构建的网站或应用。

## 解决方案：

目前，Spring官方已发布新版本完成漏洞修复，建议受漏洞影响的产品（服务）厂商和信息系统运营者尽快进行自查，并及时升级至最新版本：

<https://spring.io/blog/2022/03/31/spring-framework-rce-early-announcement>

