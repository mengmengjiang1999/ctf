![](https://image.3001.net/images/20211009/1633736727_6160d8172408ba86b5806.png!small)

## 关于EDD

EDD是一款功能强大的域数据枚举工具，该工具的功能类似于PowerView，但EDD是基于.NET开发和构建的。众所周知，PowerView本质上是一款域枚举工具，但我们自己基于.NET实现了EDD这款工具，而EDD主要通过查看各种现有项目中不同功能的实现，并将它们组合到EDD中来实现其功能的。

## 工具下载

广大研究人员可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/FortyNorthSecurity/EDD.git

## 工具使用

如需使用EDD，我们需要调用应用程序，并将需要执行的函数以参数的形式提供个EDD，并携带功能函数所需的其他参数：

![](https://image.3001.net/images/20211009/1633736741_6160d825d52034b166551.png!small)

## 功能函数

下列功能函数可以配合“-f”参数一起使用，以指定需要枚举的数据或是要执行的操作。

### 域森林/域信息

> getdomainsid - 返回目标域SID
>
> getforest - 返回当前域森岭的名称
>
> getforestdomains - 反汇当前域森林中所有域的名称
>
> convertsidtoname - 将一个SID转换为对应的组或域名
>
> getadcsservers - 获取当前域中正在运行AD CS的服务器列表

### 计算机信息

> getdomaincomputers - 获取目标域中所有计算机列表
>
> getdomaincontrollers - 获取所有的域控制器列表
>
> getdomainshares - 获取所有的域共享列表
>
> getreadabledomainshares - 获取所有可抵达的域共享列表

### 用户信息

> getnetlocalgroupmember - 返回远程系统中一个逻辑组的所有用户列表
>
> getnetdomaingroupmember -返回一个域组中的所有用户列表
>
> getdomainuser - 获取特定用户的相关信息
>
> getnetsession - 返回目标系统中携绑定特定会话的账号列表
>
> getnetloggedon - 返回目标系统中的已登录账号列表
>
> getuserswithspns - 返回绑定了SPN的所有域账号列表

### 链信息

> finddomainprocess - 在域中的所有系统中搜索特定进程（需要远程系统的管理员权限）
>
> finddomainuser - 在域环境中搜索指定的用户或组，并尝试查找活动会话（默认搜索域管理员）
>
> findinterestingdomainsharefile - 在域环境中搜索所有可访问的共享。一旦找到，它将解析所有文件名中有价值的字符串
>
> findwritableshares - 枚举域中的所有共享，然后检查当前帐户是否可以在root级别共享和一级深度共享中创建文本文件

## 项目地址

 **EDD：** 【[ _GitHub传送门_](https://github.com/FortyNorthSecurity/EDD)】

## 参考资料

> PowerView -> [_https://github.com/PowerShellMafia/PowerSploit/blob/master/Recon/PowerView.ps1_](https://github.com/PowerShellMafia/PowerSploit/blob/master/Recon/PowerView.ps1)
>
> CSharp-Tools - [_https://github.com/RcoIl/CSharp-> Tools_](https://github.com/RcoIl/CSharp-Tools)
>
> SharpView - [_https://github.com/tevora-> threat/SharpView﻿_](https://github.com/tevora-threat/SharpView)

