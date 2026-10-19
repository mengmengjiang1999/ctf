# 0x01 概述

Solarwinds Web Help
Desk是美国Solarwinds公司的一套服务台和资产管理软件。该软件支持集中式知识库、IT资产管理、项目和任务管理等功能。Web Help Desk
收集并自动处理工单[管理任务，](https://www.solarwinds.com/zh/web-help-desk/use-cases/help-desk-ticketing-software)可以更好地服务及跟踪任务，包括工单分配、途径选择和升级，找出事故工单对应的单个问题，以优化组织结构，关联问题工单与 IT
资产，并跟踪资产服务请求的历史记录，简化从服务请求到解决问题的流程。

![1644374479_620329cfdc655991e772e.png!small](https://image.3001.net/images/20220209/1644374479_620329cfdc655991e772e.png!small)

根据CVE-2021-35232漏洞描述，在SolarWinds Web Help Desk产品中存在硬编码凭据，通过这些凭据，可以对Web Help
Desk主机具有本地访问权限的攻击者允许对数据库执行任意HQL查询，并利用该漏洞窃取用户的密码哈希或将任意数据插入数据库中。

# 0x02 漏洞复现

Solarwinds Web Help
Desk软件比较容易获取，下载安装完成后，进入程序的安装目录，找到安全配置文件，可以看到文件对相关路由设置了访问控制策略，找到函数HelpdeskIntegrationAuthenticationManager()：

![1644374501_620329e58bed283e05b9f.png!small](https://image.3001.net/images/20220209/1644374501_620329e58bed283e05b9f.png!small)

可以看到该函数是一个鉴权函数，首先函数中先获取了我们的账号密码，然后对其进行判断：token.getDetails()是设置this.remoteAddress为request.getRemoteAddr()，接着就是两个账号的判断，可以看到这里比较的账号密码是硬编码的，继续往下：

![1644374518_620329f6b88233c73d7ee.png!small](https://image.3001.net/images/20220209/1644374518_620329f6b88233c73d7ee.png!small)

InternalCommunicationUtils.isAllowedAddress检查是否为环回地址，new
SimpleGrantedAuthority("ROLE_INTEGRATION")如果所有条件都满足，用户将得到ROLE_INTEGRATION权限：

![1644374555_62032a1bc1d27733afa34.png!small](https://image.3001.net/images/20220209/1644374555_62032a1bc1d27733afa34.png!small)

通过上面的分析，如果利用硬编码的账号密码将成功鉴权。

继续来到assetReport路由中，看到这里有一个子路由/rawHQL,跟进去看一下:

![1644374663_62032a87996147cb15c2d.png!small](https://image.3001.net/images/20220209/1644374663_62032a87996147cb15c2d.png!small)

可看到直接对提交过来的sql语句进行了执行处理：

![1644374679_62032a97342216df447e5.png!small](https://image.3001.net/images/20220209/1644374679_62032a97342216df447e5.png!small)

但在路由之前会对IP进行判断，判断IP地址是否为本地IP，如果不是则返回404：

![1644374698_62032aaae0e8a496c15b8.png!small](https://image.3001.net/images/20220209/1644374698_62032aaae0e8a496c15b8.png!small)

如下图测试所示：

![1644374717_62032abdca65f5e2c4da7.png!small](https://image.3001.net/images/20220209/1644374717_62032abdca65f5e2c4da7.png!small)

InternalCommunicationUtils.isAllowedAddress函数检查我们的请求是否来自环回地址，因此无法远程利用此漏洞。但是，这个函数判断存在安全隐患，这也是此漏洞比较有意思的地方：当Solarwinds
Web Help Desk
在同一主机上部署反向代理时，此函数将会失效。因为在JSP里，获取客户端的IP地址的方法是来自request.getRemoteAddr()，这种方法在大部分情况下都是有效的。但是在通过Apache、Squid等反向代理软件后就不能获取到客户端的真实IP地址了，因为request.getRemoteAddr()将返回一个环回IP地址或者本地的其他网卡IP地址，从而绕过判断。

当我们配置了反向代理后，便可进行远程漏洞利用了：

![1644374750_62032ade7e9f11374e0c7.png!small](https://image.3001.net/images/20220209/1644374750_62032ade7e9f11374e0c7.png!small)

# 0x03 总结

大多数企业内部都部署了类似Solarwinds Web Help Desk的IT服务平台软件，此类软件的安全性容易被用户忽视。本文分析了Solarwinds
Web Help Desk的一个硬编码漏洞，以及由其引起的对数据库执行任意HQL语句。

