**作者：xxhzz@星阑科技PortalLab  
原文链接：<https://mp.weixin.qq.com/s/zGDZeG3_lz5IdJ-V4zZjhg>**

## **项目介绍**

Bonitasoft 是一个业务自动化平台，可以更轻松地在业务流程中构建、部署和管理自动化应用程序；Bonita
是一个用于业务流程自动化和优化的开源和可扩展平台。

## **漏洞描述**

在Bonitasoft Authorization漏洞版本，由于 API 授权过滤器中配置问题，通过精心构造的的字符串附加到 API
URL，能够绕过权限认证。拥有普通用户权限的攻击者在绕过权限认证后，将恶意代码部署到服务器上，进行远程代码执行。

## **利用范围**

**For community（社区版）:**

2022.1-u0 (7.14.0) 以下

**For subscription（订阅版）:**

2022.1-u0 (7.14.0) 以下

2021.2-u4 (7.13.4) 以下

2021.1-0307 (7.12.11) 以下

7.11.7 以下

## **漏洞分析**

#### **环境搭建**

使用docker搭建环境，docker镜像（<https://hub.docker.com/_/bonita/tags>）选择7.13.0版本。

![](https://images.seebug.org/content/images/2022/10/19d8e0c0-042d-440e-b33d-9c7924c6a0ff.png-w331s)

下载镜像之后，直接输入命令docker run -d -p 8080:8080 -p 5050:5050，5050为远程动态调试端口。

在/opt/bonita目录下载源码。

![](https://images.seebug.org/content/images/2022/10/541865a6-5fdc-4ac9-b500-8907b7d4416d.png-w331s)

使用idea进行远程调试配置。

![](https://images.seebug.org/content/images/2022/10/4ba372ce-c64e-459a-bb31-1b1235a437df.png-w331s)

在/opt/bonita/BonitaCommunity-2021.2-u0/server/bin/catalina.sh中加入配置。

![](https://images.seebug.org/content/images/2022/10/864b2166-df0d-4c71-9c6b-13c4f5192b8f.png-w331s)

随即访问<http://ip:8080>，环境搭建成功。

![](https://images.seebug.org/content/images/2022/10/6976c633-a14d-4f5e-a166-236c9da88fef.png-w331s)

默认账号密码：install/install

#### **代码调试**

从漏洞披露参考文章看，该漏洞产生的原理是由于身份验证/权限绕过，导致没有特权的用户可以通过api端口上传恶意文件，从而命令执行。

![](https://images.seebug.org/content/images/2022/10/3ddb18c8-abf6-4df1-a15c-258f5a3d6c3a.png-w331s)

定位到参考文章所提交到的filers

在bonita\BonitaCommunity-2021.2-u0\server\webapps\bonita\WEB-INF\web.xml配置文件中，自定义了filter，并且对参数excludePatterns进行了赋值。

![](https://images.seebug.org/content/images/2022/10/98fcb66d-7463-44ba-88d4-bb9d432d05c9.png-w331s)

2个不同的过滤器类RestAPIAuthorizationFilter、TokenValidatorFilter中的参数excludePattern都被指定为“i18ntranslation”

![](https://images.seebug.org/content/images/2022/10/e4eb355f-c623-4e3a-be2d-0514c9916c69.png-w331s)

![](https://images.seebug.org/content/images/2022/10/a88a3806-8396-44c6-a2c3-7bb359257728.png-w331s)

在web.xml的192行和215行定义了/API/*路由下对应的filter为RestAPIAuthorizationFilter、TokenValidatorFilter

而RestAPIAuthorizationFilter和TokenValidatorFilter都属于AbstractAuthorizationFilter子类。

![](https://images.seebug.org/content/images/2022/10/22c7bb25-c8c4-486b-b7bc-e7ebb36ae36e.png-w331s)

![](https://images.seebug.org/content/images/2022/10/f96bdb89-236a-4bee-b604-bb67e463ece4.png-w331s)

定位到org.bonitasoft.console.common.server.login.filter.AbstractAuthorizationFilter#doFilter函数。

![](https://images.seebug.org/content/images/2022/10/8c926f9a-86d3-451b-9b70-daf5ce897521.png-w331s)

会使用“sessionIsNotNeeded”函数进行检查，如果它返回 true，它将继续应用程序流程。

而sessionIsNotNeeded 函数检查匹配 URL 中的是否包含excludePatterns

在web.xml已经对excludePatterns进行了赋值为“i18ntranslation”，所以当url中包含“i18ntranslation”时，isMatched
就会返回true

![](https://images.seebug.org/content/images/2022/10/13fd3edc-d3c9-4e43-a65f-556562584769.png-w331s)

流程就会继续，就相当于绕过了权限过滤，允许访问资源。

![](https://images.seebug.org/content/images/2022/10/13256065-9606-4b8c-a69e-f8caaee25777.png-w331s)

总结就是在URl包含“/i18ntranslation/../”或“;i18ntranslation”就可以绕过权限认证。

为实现远程命令执行，思路是上传恶意文件，上传接口在web.xml中也定义了，为/API/pageUpload

![](https://images.seebug.org/content/images/2022/10/761bdb65-5789-453f-8f11-f8438e6afca5.png-w331s)

找到org.bonitasoft.console.common.server.servlet.PageUploadServlet#getPagePermissions

在文件处理过程中，需要获取的session存在apisession

![](https://images.seebug.org/content/images/2022/10/6195f26e-4722-4430-a6ca-8db84185722f.png-w331s)

![](https://images.seebug.org/content/images/2022/10/0e01f59e-0fe1-40a8-afae-eb26a1aa66d5.png-w331s)

而且未登录的情况下，apisession也没法赋值，就会导致getPagePermissions抛出异常。

所以，为实现远程命令执行，还需要拥有一个普通的用户。

#### **漏洞复现**

先创建一个test/test用户。

![](https://images.seebug.org/content/images/2022/10/4035f351-9361-435e-9f65-16e0b6bafcf4.png-w331s)

根据以上分析原理，使用exp，成功执行命令。

![](https://images.seebug.org/content/images/2022/10/2c7ae5a1-df73-4140-bd6e-6f5633c20ef9.png-w331s)

## **修复建议**

更新至安全无漏洞版本。

## **参考材料**

1.<https://rhinosecuritylabs.com/application-security/cve-2022-25237-bonitasoft-authorization-bypass/>

2.<https://hub.docker.com/_/bonita>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1985/>

