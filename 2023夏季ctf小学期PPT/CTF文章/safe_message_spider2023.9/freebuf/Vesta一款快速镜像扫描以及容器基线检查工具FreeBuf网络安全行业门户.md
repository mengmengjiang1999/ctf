## Vesta

vesta是一款集容器扫描，Docker和Kubernetes配置基线检查于一身的工具。检查内容包括镜像或容器中包含漏洞版本的组件，Docker以及Kubernetes的危险配置。同时也是一个灵活，快速的工具，能够在各种系统上运行，包括但不限于Windows，Linux以及MacOS

## 场景介绍

伴随着容器技术的快速发展，容器安全问题也逐渐成为企业所关注的话题，越来越多的公司以及个人开发着选择将他们的服务迁移到云上。目前市面上的容器扫描或容器配置检查的产品大部门都需要进行繁琐的环境配置，同时对机器性能也有着比较高的要求，而开发者或安全测试者或许只是需要扫描少数的镜像或者配置，繁琐的配置和高昂的机器费用对他们来说难以承担，导致安全检查的效率不佳。

Vesta为开发者和安全测试者提供了方便、快速的解决方案。整个程序由golang编写，只需要使用`go
build`或者从releases下载，无需配置任何环境和数据库，并且在1 vCPU, 2G Memory的机器上就可运行，最大化方便使用者们。

此外，vesta在CTF上面也能够成为一款有用的辅助工具。在解题过程中，主办方通常会给出Dockerfile文件，可以使用vesta对构建镜像的依赖组件进行扫描，根据已有的CVE漏洞进行辅助判断。出题方也能够使用vesta进行容器的配置扫描辅助检查从而降低因为疏忽而导致的非预期。

## 功能介绍

Vesta包含两大模块

  * scan: 扫描容器和镜像的组件信息，检测是否包含CVE漏洞版本

  * analyze: 检查Docker和Kubernetes配置，是否包含危险配置。后续考虑附加攻击方法

## 检查列表

> Docker检查

Supported| Check Item| Description| Severity  
---|---|---|---  
✔| PrivilegeAllowed| 危险的特权模式| critical  
✔| Capabilities| 危险capabilities被设置| critical  
✔| Volume Mount| 敏感或危险目录被挂载| critical  
✔| Docker Unauthorized| 2375端口打开并且未授权| critical  
✔| Kernel version| 当前内核版本存在逃逸漏洞| critical  
✔| Network Module| Net模式为`host`模式并且在特定containerd版本下| critical  
✔| Docker Server version| Docker Server版本存在漏洞| critical/high/medium/low  
✔| Docker env password check| Docker env是否存在弱密码| high/medium  
✔| Image tag check| Image没有被打tag或为默认latest| low  
待定| Container env| 检查数据库是否未设置密码, 包括但不限于`MySQL`,`Redis`,`Memcache`| -  
待定| IaC scan| IaC 扫描| -  
  
* * *

> Kubernetes检查

Supported| Check Item| Description| Severity  
---|---|---|---  
✔| PrivilegeAllowed| 危险的特权模式| critical  
✔| Capabilities| 危险capabilities被设置| critical  
✔| PV and PVC| PV 被挂载到敏感目录并且状态为active| critical/medium  
✔| ClusterRoleBinding| 默认账户被赋予了权限| high/medium  
✔| Kubernetes-dashborad| 检查`-enable-skip-login`以及 dashborad的账户权限|
critical/high/low  
✔| Kernel version (k8s versions is less than v1.24)| 当前内核版本存在逃逸漏洞| critical  
✔| Docker Server version (k8s versions is less than v1.24)| Docker
Server版本存在漏洞| critical/high/medium/low  
✔| Kubernetes certification expiration| 证书到期时间小于30天| medium  
✔| ConfigMap and Secret check| ConfigMap 或者 Secret是否存在弱密码| high/medium  
✔| Auto Mount ServiceAccount Token|
Pod默认挂载了`/var/run/secrets/kubernetes.io/serviceaccount/token`.| low  
✔| NoResourceLimits| 没有限制资源的使用，例如CPU,Memory, 存储| low  
✔| Job and Cronjob| Job或CronJob没有设置seccomp或seLinux安全策略| low  
✔| Envoy admin| Envoy admin被配置以及监听`0.0.0.0`.| high/medium  
待定| CVE-2022-29179| 检测CVE-2022-29179是否存在| critical  
待定| Kubelet 10255 and Kubectl proxy| 10255 port 打开或 Kubectl proxy开启| -  
待定| Trampoline attack| RBAC权限不安全，容易遭受Trampoline攻击| -  
待定| IaC scan| Iac扫描| -  
  
## 使用样例

### 命令行介绍

    
    
    $./vesta -h
    Vesta is a static analysis of vulnerabilities, Docker and Kubernetes configuration detect toolkit
                 Tutorial is available at https://github.com/kvesta/vesta
    
    Usage:
    vesta [command]
    
    Available Commands:
    analyze     Kubernetes analyze
    completion  Generate the autocompletion script for the specified shell
    help        Help about any command
    scan        Container scan
    upgrade     Upgrade vulnerability database
    version     Print version information and quit
    
    Flags:
    -h, --help   help for vesta
    

  * 使用vesta检查镜像或容器中的漏洞组件版本（使用镜像ID，镜像标签或使用`-f`文件输入均可）, 此处使用Vulnhub Django 环境扫描

    
    
    $./vesta scan container cve-2019-14234_web1
    
    2022/11/29 22:50:00 Searching for container
    2022/11/29 22:50:19 Begin upgrading vulnerability database
    2022/11/29 22:50:19 Vulnerability Database is already initialized
    2022/11/29 22:50:19 Begin to analyze the layer
    2022/11/29 22:50:35 Begin to scan the layer
    
    Detected 216 vulnerabilities
    
    +-----+--------------------+-----------------+------------------+-------+----------+------------------------------------------------------------------+
    | 208 | python3.6 - Django | 2.2.3           | CVE-2019-14232   |   7.5 | high     | An issue was discovered                                          |
    |     |                    |                 |                  |       |          | in Django 1.11.x before                                          |
    |     |                    |                 |                  |       |          | 1.11.23, 2.1.x before 2.1.11,                                    |
    |     |                    |                 |                  |       |          | and 2.2.x before 2.2.4. If                                       |
    |     |                    |                 |                  |       |          | django.utils.text.Truncator's                                    |
    |     |                    |                 |                  |       |          | chars() and words() methods                                      |
    |     |                    |                 |                  |       |          | were passed the html=True                                        |
    |     |                    |                 |                  |       |          | argument, t ...                                                  |
    +-----+                    +-----------------+------------------+-------+----------+------------------------------------------------------------------+
    | 209 |                    | 2.2.3           | CVE-2019-14233   |   7.5 | high     | An issue was discovered                                          |
    |     |                    |                 |                  |       |          | in Django 1.11.x before                                          |
    |     |                    |                 |                  |       |          | 1.11.23, 2.1.x before 2.1.11,                                    |
    |     |                    |                 |                  |       |          | and 2.2.x before 2.2.4.                                          |
    |     |                    |                 |                  |       |          | Due to the behaviour of                                          |
    |     |                    |                 |                  |       |          | the underlying HTMLParser,                                       |
    |     |                    |                 |                  |       |          | django.utils.html.strip_tags                                     |
    |     |                    |                 |                  |       |          | would be extremely ...                                           |
    +-----+                    +-----------------+------------------+-------+----------+------------------------------------------------------------------+
    | 210 |                    | 2.2.3           | CVE-2019-14234   |   9.8 | critical | An issue was discovered in                                       |
    |     |                    |                 |                  |       |          | Django 1.11.x before 1.11.23,                                    |
    |     |                    |                 |                  |       |          | 2.1.x before 2.1.11, and 2.2.x                                   |
    |     |                    |                 |                  |       |          | before 2.2.4. Due to an error                                    |
    |     |                    |                 |                  |       |          | in shallow key transformation,                                   |
    |     |                    |                 |                  |       |          | key and index lookups for                                        |
    |     |                    |                 |                  |       |          | django.contrib.postgres.f ...                                    |
    +-----+--------------------+-----------------+------------------+-------+----------+------------------------------------------------------------------+
    

  3. 使用vesta检查Docker的基线配置

    
    
    $./vesta analyze docker
    

![vesta扫描docker](https://image.3001.net/images/20221205/1670237131_638dcbcb8169d3d8fa1b2.png!small)

  * 使用vesta检查Kubernetes的基线配置

    
    
    $./vesta analyze k8s
    

![vesta
扫描k8s](https://image.3001.net/images/20221205/1670237088_638dcba04ee25d709b62a.png!small)

## 项目地址

<https://github.com/kvesta/vesta>

