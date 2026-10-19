**今天给大家介绍的是一款名叫LAPSToolkit的工具，广大研究人员可以利用该工具来对LAPS环境进行安全审计或渗透测试。**

![aaaaaaaaaaaaa.png](https://image.3001.net/images/20190413/1555151588_5cb1bae411dd9.png!small)

## 何为LAPS？

LAPS（Microsoft LocalAdministrator Password
Solution），即本地管理员密码解决方案。是微软发布的一款用来在LDAP上存储本地管理员密码的工具。只要一切都配置正确，那么该工具使用起来将非常不错。然而，如果你没有正确地设置LDAP属性的权限，那么可能会将本地管理员凭证暴露给域内的所有用户。

LAPS使用两个LDAP属性来存储本地管理员凭证，这两个属性分别是ms-MCS-AdmPwd（存储密码）和ms-MCS-AdmPwdExpirationTime（存储过期时间）。

微软建议将特定用户和组的扩展权限移动到这些属性中。这是一个不错的方法，但它正确设置起来将非常痛苦。长话短说，如果你正在使用LAPS，那么域内的某一个用户将能够读取到这些本地管理员凭证的明文信息。

然而，这并不总是用来进行特权提升，当你攻击敏感系统并进行特权提升之后，你可以使用该方法来获取一些关键信息和敏感数据。

## LAPSToolkit

该工具采用PowerShell开发，可以利用PowerView来对部署了微软LAPS的活动目录环境进行安全审计与渗透测试。该工具可以查询由系统管理员指定的用户组，查找具有“全部扩展权限”的用户（可查看密码），而且还可以查看全部启用了LAPS的计算机设备。

## 功能命令介绍

### Get-LAPSComputers

显示全部启用了LAPS和密码扩展的计算机设备。

### Find-LAPSDelegatedGroups

查询所有的OU并检测哪一个活动目录组可读取ms-Mcs-AdmPwd属性。

### Find-AdmPwdExtendedRights

针对每一个启用了LAPS的活动目录计算机，进行扩展权限分析，并查找哪一个用户组拥有AD读取权限，以及其中的用户是否具有“全部扩展权限”。系统管理员可能不知道哪一个具有“全部扩展权限”的用户可以查看密码，以及用户组中的哪一个用户安全等级比较低。这个功能可以针对每一个AD设备解析ACL权限，但对于范围比较大的域，解析时间会比较久。

## 脚本下载

LAPSToolkit：【[点我下载](https://github.com/leoloobeek/LAPSToolkit/archive/master.zip)】

 ***
参考来源：[leoloobeek](https://github.com/leoloobeek/LAPSToolkit)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

