**作者：xxhzz@星阑科技PortalLab  
原文链接：<https://mp.weixin.qq.com/s/HRqWtQh1q1R--NDIlHLCMA>**

## **漏洞描述**

7月21日，Atlassian官方发布了2022年7月的安全更新，其中涉及到Confluence
Server的多个漏洞，其中CVE-2022-26138为一个硬编码漏洞。

当Confluence Server或Data Center上的Questions for Confluence
app启用时，它会创建一个名为disabledsystemuser的Confluence用户帐户。此帐户旨在帮助将数据从应用程序迁移到 Confluence
Cloud的管理员账号中。该帐户通过使用硬编码密码创建并添加到confluence-users组中，在默认情况下允许查看和编辑 Confluence
中的所有非受限页面。未经身份验证攻击者可以利用所知的硬编码密码登录Confluence并访问该组有权限访问的所有页面。

![](https://images.seebug.org/content/images/2022/10/d24bc20c-1584-4f6a-9c45-dcb622f3f8ab.png-w331s)

## **相关介绍**

Atlassian Confluence
Server是澳大利亚Atlassian公司的一套具有企业知识管理功能，并支持用于构建企业WiKi的协同软件的服务器版本。

## **利用范围**

Questions for Confluence app == 2.7.34

Questions for Confluence app == 2.7.35

Questions for Confluence app == 3.0.2

## **漏洞分析**

### **环境搭建**

此次漏洞分析环境可参考[CVE-2022-26134 Confluence OGNL RCE
漏洞分析](http://mp.weixin.qq.com/s?__biz=Mzg3NDcwMDk3OA==&mid=2247483775&idx=1&sn=2a6eeede0ac6c65900572e07b19f3f8f&chksm=cecd88a2f9ba01b49c1079d1ffcf3d89a4a6792378cd56abf4a29e22727a8a90dee86806b359&scene=21#wechat_redirect)。

进行搭建。分析源码为confluence-questions-3.0.2.jar或者另外两个版本。

### **代码分析**

动态调试之前，在配置文件default.properties中可以找到所创建用户的相关信息，其中的username和password都是固定的。

![](https://images.seebug.org/content/images/2022/10/cb19d7db-cff5-45b5-a8ca-68de4a91459e.png-w331s)

紧接着在com.atlassian.confluence.plugins.questions.util#BuildInformationManager处打下断点。

![](https://images.seebug.org/content/images/2022/10/1643a0e1-d833-4cbd-b7b4-ad2504997e55.png-w331s)

开启debug模式，随后在confluence中上传confluence-questions.jar应用。

![](https://images.seebug.org/content/images/2022/10/ad7fecf3-9362-4808-a1c4-f8e598028455.png-w331s)

在安装应用的过程中，会从配置文件中获取到固定的账号信息。

![](https://images.seebug.org/content/images/2022/10/ccd64eaf-e24f-48e3-a032-7584f1788b6f.png-w331s)

随后进入com.atlassian.confluence.plugins.questions.service.UserCreatorServiceImpl

实例化UserCreatorServiceImpl对象。

![](https://images.seebug.org/content/images/2022/10/c68bd207-3921-4bbe-982e-625f4cc26250.png-w331s)

继续跟进，会进入下面的addPredefinedPermittedDisabledUser方法。

![](https://images.seebug.org/content/images/2022/10/b7322ace-d4e0-40f8-91e3-7040c82f775c.png-w331s)

在此，固定disabledsystemuser用户完成创建并将其添加到confluence-users组。

![](https://images.seebug.org/content/images/2022/10/04e5086d-593a-444f-9605-60ba7ef93f22.png-w331s)

### **漏洞复现**

成功上传Questions for Confluence应用程序。

![](https://images.seebug.org/content/images/2022/10/c98282a5-6f72-41de-bb08-7b9d9ea47195.png-w331s)

使用硬编码密码创建的账号进行登录。

![](https://images.seebug.org/content/images/2022/10/e301c20f-c607-4eb6-ab59-7ec0219428b3.png-w331s)

成功登录，且该用户拥有管理员权限。

![](https://images.seebug.org/content/images/2022/10/281fa941-d2fa-4656-bfcc-a59e7bc4ad4a.png-w331s)

![](https://images.seebug.org/content/images/2022/10/94a795b3-23bc-48e1-949a-113a1a62afa0.png-w331s)

## **修复建议**

参考官方公告中的修复建议：

更新Questions for Confluence扩展至以下安全版本:

2.7.x >= 2.7.38 (Confluence 6.13.18 到 7.16.2)

Versions >= 3.0.5 (Confluence 7.16.3 之后的版本)

## **参考材料**

1.<https://confluence.atlassian.com/doc/questions-for-confluence-security-advisory-2022-07-20-1142446709.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1989/>

