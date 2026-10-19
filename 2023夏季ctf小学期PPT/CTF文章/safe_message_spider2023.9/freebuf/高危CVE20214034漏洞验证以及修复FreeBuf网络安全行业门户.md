# CVE-2021-4034漏洞复现

## 漏洞简述

原理参考：<https://mp.weixin.qq.com/s/bBroPqXgzD9kTslN1Sqdvg>

2022年01月26日，`Linux`发布了`pkexec`的风险通告，漏洞编号为`CVE-2021-4034`，漏洞等级：`高危`。目前该漏洞的poc已公开。

`pkexec`应用程序是一个`setuid`工具，旨在允许非特权用户根据预定义的策略以特权用户身份运行命令。

`polkit`的`pkexec`实用程序中存在一个本地权限提升漏洞。当前版本的`pkexec`无法正确处理调用参数计数，并最终尝试将环境变量作为命令执行。攻击者可以通过控制环境变量来利用这一点，从而诱导`pkexec`执行任意代码。利用成功后，会导致本地特权升级，非特权用户获得管理员权限。

## 安全版本

### CentOS系列：

    
    
    CentOS 6：polkit-0.96-11.el6_10.2  
    ​  
    CentOS 7：polkit-0.112-26.el7_9.1  
    ​  
    CentOS 8.0：polkit-0.115-13.el8_5.1  
    ​  
    CentOS 8.2：polkit-0.115-11.el8_2.2  
    ​  
    CentOS 8.4：polkit-0.115-11.el8_4.2

### Ubuntu系列：

    
    
    Ubuntu 20.04 LTS：policykit-1 - 0.105-26ubuntu1.2  
    ​  
    Ubuntu 18.04 LTS：policykit-1 - 0.105-20ubuntu0.18.04.6  
    ​  
    Ubuntu 16.04 ESM：policykit-1 - 0.105-14.1ubuntu0.5+esm1  
    ​  
    Ubuntu 14.04 ESM：policykit-1 - 0.105-4ubuntu3.14.04.6+esm1

  

## 漏洞验证

### centos

通过以下命令可查看 Polkit 是否为安全版本：

`rpm -qa polkit`

### Ubuntu

`dpkg -l policykit-1`

### 实例

![image-20220126191537681](https://image.3001.net/images/20220126/1643196311_61f12f97bcc991325e1b8.png!small)

  

## 修复建议

建议广大用户及时将`pkexec`升级到最新版本。

 **CentOS用户可待官方源更新后采用如下命令升级到安全版本：**

    
    
    yum clean all && yum makecacheyum update polkit -y

 **验证修复，通过以下命令可查看Polkit是否为安全版本：**

    
    
    rpm -qa polkit  
    

 **Ubuntu用户可采用如下命令升级至安全版本或更高版本：**

    
    
    sudo apt-get updatesudo apt-get install policykit-1

 **验证修复，通过以下命令可查看Polkit是否为安全版本：**

    
    
    dpkg -l policykit-1

目前各Linux发行版官方均已给出安全补丁，建议用户尽快升级至安全版本，或参照官方说明措施进行缓解，CentOS、Ubuntu及Debian用户可参考以下链接：
<https://ubuntu.com/security/CVE-2021-4034>

  

## POC以及漏洞复现

### FOFA 查询

[app="Linux-操作系统"](http://dev.fofa.so/result?qbase64=YXBwPSJMaW51eC3mk43kvZzns7vnu58i)

### poc

<https://github.com/berdav/CVE-2021-4034>[姿势1最简单]

<https://github.com/arthepsy/CVE-2021-4034>

<https://github.com/dzonerzy/poc-cve-2021-4034>[需要go环境]

![image-20220126171927138](https://image.3001.net/images/20220126/1643196328_61f12fa88d14c7e486df8.png!small)

![image-20220126172230102](https://image.3001.net/images/20220126/1643196394_61f12fea30e34e22e10e7.png!small)

  

  

