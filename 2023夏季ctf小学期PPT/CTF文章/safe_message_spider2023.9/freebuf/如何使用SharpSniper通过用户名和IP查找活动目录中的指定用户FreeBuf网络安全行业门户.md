![](https://image.3001.net/images/20220626/1656243822_62b8466e6410111812ed4.png!small)  

## 关于SharpSniper

SharpSniper是一款针对活动目录安全的强大工具，在该工具的帮助下，广大研究人员可以通过目标用户的用户名和登录的IP地址在活动目录中迅速查找和定位到指定用户。

在一般的红队活动中，通常会涉及到针对域管理账号的操作任务。在某些场景中，某些客户（比如说企业的CEO）可能会更想知道自己企业或组织中域特定用户是否足够安全。

SharpSniper便应运而生，SharpSniper是一款简单且功能强大的安全工具，可以寻找目标域用户的IP地址，并帮助我们轻松寻找和定位到这些用户。

## 工具运行机制

该工具需要我们拥有目标域控制器中读取日志的权限。

首先，SharpSniper会查询并枚举出目标组织内的域控制器，然后以列表形式呈现。接下来，该工具会搜索目标用户账号相关的任何域控制器登录事件，并读取DHCP最新分配给TA的登录IP地址。

## 环境要求

> .Net Framework v3.5

## 关于域控制器

域控制器( Domain controller，DC)是活动目录的存储位置,安装了活动目录的计算机称为域控制器。

![](https://image.3001.net/images/20220626/1656243846_62b84686a847cd43b7294.png!small)

域控制器中包含了由这个域的账户、密码、属于这个域的计算机等信息构成的数据库。当电脑联入网络时，域控制器首先要鉴别这台电脑是否是属于这个域的，用户使用的登录账号是否存在、密码是否正确。如果以上信息有一样不正确，那么域控制器就会拒绝这个用户从这台电脑登录。不能登录，用户就不能访问服务器上有权限保护的资源，他只能以对等网用户的方式访问Windows共享出来的资源，这样就在一定程度上保护了网络上的资源。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/HunnicCyber/SharpSniper.git

## 工具使用

### cmd.exe（提供凭证）

    
    
    C:\> SharpSniper.exe emusk DomainAdminUser DAPass123
    
     
    
    User: emusk - IP Address: 192.168.37.130

### cmd.exe（提供当前认证令牌，例如Mimikatz pth）

    
    
    C:\> SharpSniper.exe emusk
    
     
    
    User: emusk - IP Address: 192.168.37.130

### Cobalt Strike（提供凭证）

    
    
    > execute-assembly /path/to/SharpSniper.exe emusk DomainAdminUser DAPass123
    
     
    
    User: emusk - IP Address: 192.168.37.130

### Cobalt Strike（Beacon的令牌）

    
    
    > execute-assembly /path/to/SharpSniper.exe emusk
    
     
    
    User: emusk - IP Address: 192.168.37.130

## 项目地址

 **SharpSniper** ：【[ _GitHub传送门_](https://github.com/HunnicCyber/SharpSniper)】

