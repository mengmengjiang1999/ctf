![20210806214543.png](https://image.3001.net/images/20210806/1628258305_610d4001381dff19a33b2.png!small)

## 前言

这又是一个关于域内基础概念与原理的系列，本系列将包含以下几篇文章：

> 《内网渗透测试：内网环境与活动目录基础概念》
>
> 《内网渗透测试：活动目录 Active Directory 的查询》
>
> 《内网渗透测试：域用户组及域内权限划分》
>
> 《内网渗透测试：OU 组织单位》
>
> 《内网渗透测试：域用户和机器用户》
>
> 《内网渗透测试：域内权限访问控制》
>
> 《内网渗透测试：Windows 令牌窃取》
>
> 《内网渗透测试：Windows 组策略讲解》
>
> 《内网渗透测试：Windows 组策略后门》

在前面《内网渗透测试：域用户组及域内权限划分》的学习中，我们讲过，当运维需要一些特殊的管理权限来对公司的网络进行管理时，我们不建议直接对该用户赋予权限，而是设置个域用户组，对这个组配置权限，然后再将运维拉进这个组里面，这样组里面的运维就拥有了该组的权限。同样，如果我们需要对指定部门里面的用户进行统一管理，那我们便可以设置个类似于集合的东西，然后把该部门的用户拉进这个集合，这样就可以对该部门里面的用户进行集中管理了，比如下发组策略等。本篇文章我们要讲的就是后者，而这个集合就是
OU。

## 什么是 OU

OU，即组织单位（Organization
Unit），是一个容器对象，将域中的对象组织成逻辑组，帮助网络管理员简化管理组。组织单位包含下列类型的对象：用户，计算机，工作组，打印机，安全策略以及其他组织单位等。可以在组织单位基础上部署组策略，统一管理组织单位中的域对象。
在企业域环境里面，我们经常可以看到按照部门划分的一个个 OU，如下图所示：

![image-20210802162822557](https://image.3001.net/images/20210806/1628258305_610d40016e14f665c7d7e.png!small)

## OU 与容器的区别

组织单位（OU）是专用容器，与常规容器的区别在于管理员可以将组策略应用于 OU，然后系统将其下推到 OU
中的所有计算机，但是你不能将组策略应用于容器。这也是 OU 与容器主要的区别。需要注意的是`Domain
Computers`是一个普通容器，而`Domain Controllers`是一个 OU，因此可以可以将组策略应该于`Domain
Controllers`，而不可以将组策略应用于`Domain Computers`。注意这里所说的`Domain Computers`和`Domain
Controllers`特指根域的，而不是`User`容器底下的那两个组：

![image-20210802153950699](https://image.3001.net/images/20210806/1628258305_610d4001ac37950ceb4ad.png!small)

## OU 跟组的区别

组织单位跟组是两个完全不同的概念。OU
是管理对象的集合，而组是权限的集合。举个前面举过的例子，运维需要对公司的网络进行管理，需要一些特殊的管理权限，我们就可以设置个组，对这个组配置权限，然后再将运维拉进这个组里面，这样组里面的运维就拥有了该组的权限。又比如我们需要对财务部里面的用户进行统一管理，那我们便可以设置个
OU，然后把财务部的用户拉进这个 OU，这样就可以对财务部里面的用户进行集中管理，比如下发组策略等。说通俗点说，组是管理的集合，而 OU 是被管理的集合。

## 组织单位的创建

### 创建 OU

在域控制器的 “管理工具” —> “Active Directory 用户和计算机”，选中你的域名后 “右键” —> “新建” —> “组织单位”：

![image-20210802160036634](https://image.3001.net/images/20210806/1628258306_610d40021a33ae71c875b.png!small)

填入需要创建的组织单位的名称后点击确定：

![image-20210802160402453](https://image.3001.net/images/20210806/1628258306_610d40027267848b4c61c.png!small)

如下图所示，成功创建了一个名为 “行政部” 的组织单位：

![image-20210802160847814](https://image.3001.net/images/20210806/1628258306_610d4002c355b7f984b88.png!small)

但此时新创建的 OU 里面没有任何管理对象。

### 向 OU 中添加对象

我们可以向新创建的 OU 中添加管理对象，比如用户，计算机，工作组，打印机等。选中你当创建的组织单位，然后 “右键” —> “新建”：

![image-20210802161201315](https://image.3001.net/images/20210806/1628258307_610d40030bc8e71a8922e.png!small)

然后选择相应类型的对象即可。如下，我们向 “行政部” 这个组织单位中添加了一台计算机：

![image-20210802161442814](https://image.3001.net/images/20210806/1628258307_610d400352b4e5dfb8c78.png!small)

![image-20210802161629183](https://image.3001.net/images/20210806/1628258307_610d40039f822763e86f9.png!small)

## OU 的查询

在 Active Directory 中，所有的 OU 组织单位都是 organizationalUnit 类的实例：

![image-20210802163840801](https://image.3001.net/images/20210806/1628258307_610d4003e06aae055c52a.png!small)

所以我们可以用`(objectClass=organizationalUnit)`或者`(objectCategory=organizationalUnit)`来过滤查询
OU。

    
    
    Adfind.exe -b dc=whoamianony,dc=org -f "(objectClass=organizationalUnit)" -dn  
    Adfind.exe -b dc=whoamianony,dc=org -f "(objectCategory=organizationalUnit)" -dn

![image-20210802164452785](https://image.3001.net/images/20210806/1628258308_610d40043153b876ed4bc.png!small)

如果要查询指定 OU 里面的账户，可以指定 BaseDN 为指定的 OU 就行，如下我们查询 “行政部” 里面的对象：

    
    
    Adfind.exe -b "OU=行政部,DC=whoamianony,DC=org" -dn

![image-20210802165401053](https://image.3001.net/images/20210806/1628258308_610d4004681c936a230e8.png!small)

## OU 的委派

OU 组织单位的委派其实就是赋予某个域内用户对 OU 组织单位的某些管理权限。考虑这样一种需求，如果我们想允许某个用户把其他用户拉进某个
OU，而不赋予这个用户域管权限，那么我们可以在这个 OU 给这个用户委派一个添加成员的权限。下面演示一下委派过程。

选中 OU，“右键” —> “委派控制”：

![image-20210802165917630](https://image.3001.net/images/20210806/1628258308_610d400499851f7243b4d.png!small)

然后进入 “控制委派向导”：

![image-20210802170240471](https://image.3001.net/images/20210806/1628258308_610d4004ddd5090064af0.png!small)

点击下一步添加一个或多个你想要委派控制的用户或组：

![image-20210802170343871](https://image.3001.net/images/20210806/1628258309_610d40053e8c6810758ae.png!small)

然后点击下一步选择你想要委派的任务即可：

![image-20210802170417132](https://image.3001.net/images/20210806/1628258309_610d400592d39a9d9c8b4.png!small)

## Ending......

![20210802171513.jpg](https://image.3001.net/images/20210806/1628258309_610d4005d680185560de6.jpg!small)

## 参考

> <https://blog.csdn.net/qq_36119192/article/details/113762959>
>
> <https://daiker.gitbook.io/windows-protocol/ldap-pian/9#0x02-zu-zhi-dan-wei-> organization-unit>
>
> <https://www.anquanke.com/post/id/195737#h3-15>

