## 0x00 漏洞描述

> polkit
> 是一个应用程序级别的工具集，通过定义和审核权限规则，实现不同优先级进程间的通讯：控制决策集中在统一的框架之中，决定低优先级进程是否有权访问高优先级进程。
>
> Polkit 在系统层级进行权限控制，提供了一个低优先级进程和高优先级进程进行通讯的系统。和 sudo 等程序不同，Polkit 并没有赋予进程完全的
> root 权限，而是通过一个集中的策略系统进行更精细的授权。
>
> Polkit 定义出一系列操作，例如运行 GParted, 并将用户按照群组或用户名进行划分，例如 wheel
> 群组用户。然后定义每个操作是否可以由某些用户执行，执行操作前是否需要一些额外的确认，例如通过输入密码确认用户是不是属于某个群组。
>
> polkit存在于所有主流的 Linux 发行版的默认配置中，目前主流Linux版本均受到影响。

## 0x01 不受影响版本

> CentOS系列：
>
> CentOS 6：polkit-0.96-11.el6_10.2
>
> CentOS 7：polkit-0.112-26.el7_9.1
>
> CentOS 8.0：polkit-0.115-13.el8_5.1
>
> CentOS 8.2：polkit-0.115-11.el8_2.2
>
> CentOS 8.4：polkit-0.115-11.el8_4.2
>
> Ubuntu系列：
>
> Ubuntu 20.04 LTS：policykit-1 - 0.105-26ubuntu1.2
>
> Ubuntu 18.04 LTS：policykit-1 - 0.105-20ubuntu0.18.04.6
>
> Ubuntu 16.04 ESM：policykit-1 - 0.105-14.1ubuntu0.5+esm1
>
> Ubuntu 14.04 ESM：policykit-1 - 0.105-4ubuntu3.14.04.6+esm1

## 0x02 漏洞复现

通过公网爆出的Exp进行漏洞复现，复现过程比较简单，如果小伙伴们需要Exp的话可以私信我。

### 1.创建普通ceshi账户

![1643248765_61f1fc7d256d6940ed080.png!small](https://image.3001.net/images/20220127/1643248765_61f1fc7d256d6940ed080.png!small)

### 2.查看polkit版本

该Ubuntu版本存在漏洞

![1643249996_61f2014ce9b1abd1c288c.png!small](https://image.3001.net/images/20220127/1643249996_61f2014ce9b1abd1c288c.png!small)

### 3.使用Exp进行测试

Exp默认使用python3，如果使用python2则需要修改相应代码。

![1643249315_61f1fea3ef920ab460e6d.png!small](https://image.3001.net/images/20220127/1643249315_61f1fea3ef920ab460e6d.png!small)

![1643249347_61f1fec3f1afb3ef9d672.png!small](https://image.3001.net/images/20220127/1643249347_61f1fec3f1afb3ef9d672.png!small)

### 4.升级polkit到最新版本

![1643251217_61f2061109caf5b3a3e4c.png!small](https://image.3001.net/images/20220127/1643251217_61f2061109caf5b3a3e4c.png!small)

![1643251172_61f205e4ed7532e691b91.png!small](https://image.3001.net/images/20220127/1643251172_61f205e4ed7532e691b91.png!small)

## 0x03 修复建议

Centos通过如下命令查看是否是安全版本

    
    
    rpm -qa polkit

CentOS用户可采用如下命令升级到最新版

    
    
    yum clean all && yum makecache 
    yum update polkit -y

Ubuntu通过如下命令查看是否是安全版本

    
    
    dpkg -l policykit-1

Ubuntu用户可采用如下命令升级到最新版

    
    
    sudo apt-get update   
    sudo apt-get install policykit-1

如果无补丁，采用临时解决方案，从 pkexec 中删除 SUID 位。

    
    
    chmod 0755 /usr/bin/pkexec

