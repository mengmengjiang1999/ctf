## 前言

当我们平时拿到云服务的访问凭证即 Access Key 时，通常的做法可能是看下对方的 OSS 对象存储、或者在实例上执行个命令，但 AK
的利用远不止这些，通过 AK 我们可以做太多太多的事情，为了方便 AK 的利用，于是有了这个工具。

CF 是一个云环境利用框架，主要用来方便红队人员在获得云服务的访问凭证的后续工作。

项目地址：[github.com/teamssix/cf](https://github.com/teamssix/cf)

下载地址：[github.com/teamssix/cf/releases](https://github.com/teamssix/cf/releases)

> 代码完全开源，师傅们可以放心使用，提前祝师傅打下一个又一个点、拿下一个又一个云上管理员权限。

截止到 2022 年 7 月 10 日，CF 已迭代到 v0.2.2 版本，目前 CF 仅支持阿里云，当前 CF 已支持以下功能：

  * 一键列出目标 AK 的 OSS、ECS、RDS 服务

  * 一键获得实例上的临时访问凭证

  * 一键为实例反弹 Shell

  * 一键接管控制台

  * 一键为所有实例执行三要素，方便你懂得

  * 一键查看当前配置的权限

  * ……

## 使用手册

使用手册请参见：[wiki.teamssix.com/cf](https://wiki.teamssix.com/cf)

![image](https://image.3001.net/images/20220711/1657512297_62cba169239c34c626a2f.png!small)

## 简单上手

![image](https://image.3001.net/images/20220711/1657512286_62cba15ed272e6527dd8b.png!small)

配置 CF

    
    
    cf configure
    

![image](https://image.3001.net/images/20220711/1657512275_62cba153c63a9727c637e.png!small)

一键列出当前访问凭证的云服务资源

    
    
    cf ls
    

![image](https://image.3001.net/images/20220711/1657512266_62cba14a2fe8a502384d2.png!small)

一键列出当前访问凭证的权限

    
    
    cf ls permissions
    

![image](https://image.3001.net/images/20220711/1657512255_62cba13fc02216978f230.png!small)

一键接管控制台

    
    
    cf console
    

![image](https://image.3001.net/images/20220711/1657512244_62cba13467f96038df330.png!small)

查看 CF 为实例执行命令的操作的帮助信息

    
    
    cf ecs exec -h
    

![image](https://image.3001.net/images/20220711/1657512233_62cba12923782cec3c58d.png!small)

一键为所有实例执行三要素，方便你懂得

    
    
    cf ecs exec -b
    

![image](https://image.3001.net/images/20220711/1657512220_62cba11ccf5438b728db2.png!small)

一键获取实例中的临时访问凭证数据

    
    
    cf ecs exec -m
    

![image](https://image.3001.net/images/20220711/1657512206_62cba10ee501746dbe469.png!small)

如果感觉还不错的话，师傅记得给个 Star 呀 ~，另外 CF
的更多使用方法可以参见使用手册：[wiki.teamssix.com/cf](https://wiki.teamssix.com/cf)

