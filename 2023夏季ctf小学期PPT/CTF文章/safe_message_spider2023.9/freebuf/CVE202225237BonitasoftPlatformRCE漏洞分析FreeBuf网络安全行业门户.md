## **项目介绍**

Bonitasoft 是一个业务自动化平台，可以更轻松地在业务流程中构建、部署和管理自动化应用程序；Bonita
是一个用于业务流程自动化和优化的开源和可扩展平台。

##  **漏洞描述**

在Bonitasoft Authorization漏洞版本，由于 API 授权过滤器中配置问题，通过精心构造的的字符串附加到 API
URL，能够绕过权限认证。拥有普通用户权限的攻击者在绕过权限认证后，将恶意代码部署到服务器上，进行远程代码执行。

##  **利用范围**

 **For community（社区版）:**

2022.1-u0 (7.14.0) 以下

 **For subscription（订阅版）:**

2022.1-u0 (7.14.0) 以下

2021.2-u4 (7.13.4) 以下

2021.1-0307 (7.12.11) 以下

7.11.7 以下

##  **漏洞分析**

###  **环境搭建**

使用docker搭建环境，docker镜像（https://hub.docker.com/_/bonita/tags）选择7.13.0版本。

![](https://image.3001.net/images/20221013/1665643394_6347b3822350db55e252b.png!small)

下载镜像之后，直接输入命令docker run -d -p 8080:8080 -p 5050:5050，5050为远程动态调试端口。

在/opt/bonita目录下载源码。

![](https://image.3001.net/images/20221013/1665646363_6347bf1b74fa04d830ea6.png!small)使用idea进行远程调试配置。  

![](https://image.3001.net/images/20221013/1665646379_6347bf2b9c8e721fe9972.png!small)在/opt/bonita/BonitaCommunity-2021.2-u0/server/bin/catalina.sh中加入配置。  

![](https://image.3001.net/images/20221013/1665646401_6347bf411fecc7f7d9842.png!small)随即访问http://ip:8080，环境搭建成功。  

![](https://image.3001.net/images/20221013/1665646419_6347bf5379d681698c159.png!small)

默认账号密码：install/install

###  **代码调试**

从漏洞披露参考文章看，该漏洞产生的原理是由于身份验证/权限绕过，导致没有特权的用户可以通过api端口上传恶意文件，从而命令执行。

![](https://image.3001.net/images/20221013/1665646468_6347bf8411e6c92927c83.png!small)

定位到参考文章所提交到的filers

在bonita\BonitaCommunity-2021.2-u0\server\webapps\bonita\WEB-INF\web.xml配置文件中，自定义了filter，并且对参数excludePatterns进行了赋值。

![](https://image.3001.net/images/20221013/1665646487_6347bf9701b7cb403b068.png!small)2个不同的过滤器类RestAPIAuthorizationFilter、TokenValidatorFilter中的参数excludePattern都被指定为“i18ntranslation”  

![](https://image.3001.net/images/20221013/1665646546_6347bfd27b60cf8ca773b.png!small)![](https://image.3001.net/images/20221013/1665646560_6347bfe074a3bf90f041f.png!small)

在web.xml的192行和215行定义了/API/*路由下对应的filter为RestAPIAuthorizationFilter、TokenValidatorFilter

而RestAPIAuthorizationFilter和TokenValidatorFilter都属于AbstractAuthorizationFilter子类。

![](https://image.3001.net/images/20221013/1665646589_6347bffd483c12ded58e5.png!small)![](https://image.3001.net/images/20221013/1665646600_6347c0080e768feb8f63a.png!small)定位到org.bonitasoft.console.common.server.login.filter.AbstractAuthorizationFilter#doFilter函数。  

![](https://image.3001.net/images/20221013/1665646615_6347c017e4cf2fe48f5d0.png!small)

会使用“sessionIsNotNeeded”函数进行检查，如果它返回 true，它将继续应用程序流程。

而sessionIsNotNeeded 函数检查匹配 URL 中的是否包含excludePatterns

在web.xml已经对excludePatterns进行了赋值为“i18ntranslation”，所以当url中包含“i18ntranslation”时，isMatched
就会返回true

![](https://image.3001.net/images/20221013/1665646638_6347c02e8ac23757258a3.png!small)流程就会继续，就相当于绕过了权限过滤，允许访问资源。  

![](https://image.3001.net/images/20221013/1665646653_6347c03defcd327d43014.png!small)

总结就是在URl包含“/i18ntranslation/../”或“;i18ntranslation”就可以绕过权限认证。

为实现远程命令执行，思路是上传恶意文件，上传接口在web.xml中也定义了，为/API/pageUpload

![](https://image.3001.net/images/20221013/1665646672_6347c050b30fcee9aaf18.png!small)

找到org.bonitasoft.console.common.server.servlet.PageUploadServlet#getPagePermissions

在文件处理过程中，需要获取的session存在apisession

![](https://image.3001.net/images/20221013/1665646701_6347c06d26481333eb584.png!small)![](https://image.3001.net/images/20221013/1665646712_6347c07839d4daa9e9ba3.png!small)

而且未登录的情况下，apisession也没法赋值，就会导致getPagePermissions抛出异常。

所以，为实现远程命令执行，还需要拥有一个普通的用户。

###  **漏洞复现**

先创建一个test/test用户。

![](https://image.3001.net/images/20221013/1665646737_6347c0913bb79900edade.png!small)根据以上分析原理，使用exp，成功执行命令。  

![](https://image.3001.net/images/20221013/1665646751_6347c09f4c0b11ea40916.png!small)

##  **修复建议**

更新至安全无漏洞版本。

##  **参考材料**

1.https://rhinosecuritylabs.com/application-security/cve-2022-25237-bonitasoft-authorization-bypass/

2.https://hub.docker.com/_/bonita

