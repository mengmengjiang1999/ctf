## **前言**

在此前分析了CVE-2022-22972 VMware Workspace ONE Access和CVE-2022-22954 VMware
Workspace ONE Access SSTI
RCE之后，发现当时的安全公告中同时披露了很多cve漏洞，其中就包括CVE-2022-22955和CVE-2022-22957，之前漏洞环境也一直还在，也正好再学习分析一波。

##  **漏洞描述**

从4月6号的漏洞公告（https://www.vmware.com/security/advisories/VMSA-2022-0011.html）显示，VMware
Workspace ONE Access 在 OAuth2 ACS
框架中有两个身份验证绕过漏洞，CVE-2022-22955就是其中一个，攻击者可通过获取OAuth2客户端的激活码，激活OAuth2客户端以此绕过身份验证；而CVE-2022-22957属于JDBC注入导致的远程代码执行，具有管理访问权限的攻击者通过可控参数构造恶意JDBC
URL触发反序列化，从而执行任意命令获取系统权限。

##  **利用范围**

产品利用范围可参考https://www.vmware.com/security/advisories/VMSA-2022-0011.html

![](https://image.3001.net/images/20220826/1661494719_630865bf9a110c1c46c9a.png!small)

##  **漏洞分析**

###  **环境搭建**

漏洞环境使用的是VMware Workspace ONE Access 21.08.0.1 OVA

具体搭建可参考https://mp.weixin.qq.com/s/zVYQQgDjcwJKAnX8SZJ5Cw

###  **分析复现**

 **CVE-2022-22955 OAuth2TokenResourceController ACS 身份验证绕过**

定位com.vmware.horizon.rest.controller.oauth2.OAuth2TokenResourceController#generateActivationToken

存在路径：/generateActivationToken/{id}

在generateActivationToken方法中将为oauth2客户端生成激活码activationToken

![](https://image.3001.net/images/20220826/1661494852_6308664463033de8aba57.png!small)接着在com.vmware.horizon.rest.controller.oauth2.OAuth2TokenResourceController#activateOauth2Client上方注解说明得很清楚，通过交换activationToken也就是前面获取到的激活码来激活oauth2客户端，获取
client ID 和 client secret，用于/SAAS/auth/oauthtoken做身份认证。  

![](https://image.3001.net/images/20220826/1661494892_6308666c5399d248de2b6.png!small)

其实也就是获取到client ID 和 client secret后就可以进行身份认证的绕过。

那如果不存在如上分析的 OAuth2 客户端，也就无法利用。

在默认情况下，VMware Workspace ONE Access会安装两个内部客户端。

![](https://image.3001.net/images/20220826/1661494911_6308667f0bd0a3ccb877a.png!small)在VMware
Workspace ONE
Access安装过程中，会调用com.vmware.horizon.rest.controller.system.BootstrapController类进行初始化。  

![](https://image.3001.net/images/20220826/1661494929_63086691a9cd16dac45b5.png!small)本质上会导致com.vmware.horizon.rest.controller.oauth2.OAuth2TokenResourceController#createTenant调用createDefaultServiceOAuth2Client函数，从而创建系统范围内的oauth2
客户端。  

![](https://image.3001.net/images/20220826/1661494946_630866a2222eb34bbbad0.png!small)![](https://image.3001.net/images/20220826/1661494957_630866adee2a1f79de61a.png!small)

通过如上分析进行漏洞复现，看看实际效果。

首先通过/generateActivationToken/{id}，获取oauth2客户端激活码。

![](https://image.3001.net/images/20220826/1661494979_630866c32e9928e94dced.png!small)再通过交换activation激活码来激活oauth2客户端，获取a
client ID 和 client secret  

![](https://image.3001.net/images/20220826/1661494994_630866d246e063eb0b0f7.png!small)最后使用
client ID 和 client secret做身份认证，并获取到可用jwt token  

![](https://image.3001.net/images/20220826/1661495009_630866e190582f599bb28.png!small)

至此，可通过获取到的jwt token进行身份验证的绕过。

 **CVE‐2022‐22957 VMware Workspace ONE Access JDBC注入漏洞**

VMware Workspace ONE Access 默认安装PostgreSQL数据库。

代码定位到com.vmware.horizon.rest.controller.system.DBConnectionCheckController.class

存在doCheck函数。

获取到jdbcUrl、dbUsername、encryptedPwd（加密后dbPassword）后调用dbConnectionCheckService.checkConnection

![](https://image.3001.net/images/20220826/1661495041_6308670113e8baa1e93f8.png!small)com.vmware.horizon.datastore.impl.
DbConnectionCheckServiceLmpl#checkConnection中将会调用testConnection  

![](https://image.3001.net/images/20220826/1661495056_630867109b9e3548393cb.png!small)而在testConnection中会继续调用FactoryHelper.getConnection  

![](https://image.3001.net/images/20220826/1661495078_63086726d0fec784eb722.png!small)在FactoryHelper.getConnection中最终调用DriverManager.getConnection用于获取数据库的连接，而其中的jdbc
URL完全可控。  

![](https://image.3001.net/images/20220826/1661495107_63086743123f5f4d01bda.png!small)

这就导致了jdbc注入，从而任意命令执行。

后续利用可参考

https://srcincite.io/blog/2022/08/11/i-am-whoever-i-say-i-am-infiltrating-vmware-workspace-one-access-using-a-0-click-exploit.html

##  **修复建议**

根据官方解决方案https://kb.vmware.com/s/article/88098 进行修复。

##  **参考材料**

1.https://www.vmware.com/security/advisories/VMSA-2022-0011.html

2.https://srcincite.io/blog/2022/08/11/i-am-whoever-i-say-i-am-infiltrating-vmware-workspace-one-access-using-a-0-click-exploit.html

3.https://su18.org/post/jdbc-connection-url-attack/

4.https://kb.vmware.com/s/article/88098

