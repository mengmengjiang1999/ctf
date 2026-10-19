![](https://image.3001.net/images/20210408/1617886946_606efee2294a79d65f331.jpg!small)

## 关于ThreatMapper

ThreatMapper是Deepfence本地云工作负载保护平台的子集，ThreatMapper作为社区版发布，并且能够给广大研究人员提供下列功能：

> 可视化：以近乎实时的方式可视化监控kubernetes集群、虚拟机、容器、镜像、正在运行的进程和网络连接。
>
> 运行时漏洞管理：对正在运行的容器和主机以及容器镜像执行漏洞扫描。
>
> 容器注册表扫描：检查存储在AWS ECR、Azure容器注册表、Google容器注册表、Docker
> Hub、Docker自托管私有注册表、Quay、Harbor、Gitlab和JFrog注册表上的镜像漏洞。
>
> CI/CD扫描：将镜像以CircleCI、Jenkins和GitLab等现有[
> _CI/CD管道_](https://github.com/deepfence/ThreatMapper/blob/master/ci-cd-> integrations)的部分进行扫描。
>
> 与SIEM、通知信道和凭证的集成：与Slack、PagerDuty、HTTP endpoint、Jira、Splunk、ELK、Sumo
> Logic和Amazon S3集成。

## 平台运行演示

视频地址：https://deepfence.io/community-demo-form/

## 平台架构

下图显示的是ThreatMapper平台的系统架构：

![](https://image.3001.net/images/20210408/1617886958_606efeee05da349ed4380.png!small)

## 工具概述

Deepfence管理控制台首先需要安装在单独的系统上，然后将Deepfence代理安装到部署应用程序工作负载的裸机服务器、虚拟机或Kubernetes集群上，以便可以扫描主机系统或应用程序工作负载中的漏洞。

Deepfence安全平台的架构图示如下：

![](https://image.3001.net/images/20210408/1617886966_606efef6679a56bd3ffa3.jpg!small)

## Deepfence管理控制台安装

1、将 _docker-compose.yml_ 文件下载到目标系统中。

2、执行下列命令：

    
    
    docker-compose -f docker-compose.yml up -d

3、在浏览器中打开管理控制台IP地址/域名（https://x.x.x.x），然后注册一个新的账号。

4、获取Deepfence
API密钥：点击设置->用户管理，然后复制API密钥。在下列Docker中运行命令，使用你自己的API密钥替换掉C8TtyEtNB0gBo1wGhpeAZICNSAaGWw71BSdS2kLELY0：

    
    
    docker run -dit --cpus=".2" --name=deepfence-agent --restart on-failure --pid=host --net=host --privileged=true -v /sys/kernel/debug:/sys/kernel/debug:rw -v /var/log/fenced -v /var/run/docker.sock:/var/run/docker.sock -v /:/fenced/mnt/host/:ro -e USER_DEFINED_TAGS="" -e DF_BACKEND_IP="127.0.0.1" -e DEEPFENCE_KEY="C8TtyEtNB0gBo1wGhpeAZICNSAaGWw71BSdS2kLELY0" deepfenceio/deepfence_agent_ce:latest

这是快速开始扫描各种容器映像所需的最小化安装。接下来，我们可以将镜像下载到这个管理控制台并执行漏洞扫描任务了。

## Deepfence代理安装

为了检查主机是否存在漏洞，或者如果必须检查漏洞的Docker映像或容器保存在不同的主机上，则需要在这些主机上安装Deepfence代理。

Deepfence代理的安装步骤取决于所使用的系统环境。

### 在单一虚拟机或主机上安装

1、获取Deepfence API密钥：点击设置->用户管理，然后复制API密钥。

2、在Docer中运行虾类命令，使用管理控制台的IP地址替换其中的x.x.x.x，使用你自己的API密钥替换掉C8TtyEtNB0gBo1wGhpeAZICNSAaGWw71BSdS2kLELY0：

    
    
    docker run -dit --cpus=".2" --name=deepfence-agent --restart on-failure --pid=host --net=host --privileged=true -v /sys/kernel/debug:/sys/kernel/debug:rw -v /var/log/fenced -v /var/run/docker.sock:/var/run/docker.sock -v /:/fenced/mnt/host/:ro -e USER_DEFINED_TAGS="" -e DF_BACKEND_IP="x.x.x.x" -e DEEPFENCE_KEY="C8TtyEtNB0gBo1wGhpeAZICNSAaGWw71BSdS2kLELY0" deepfenceio/deepfence_agent_ce:latest

3、可以使用USER_DEFINED_TAGS=""对上述命令中的代理节点进行标记，标签使用逗号分隔，比如说"dev,front-end"。

### Kubernetes安装

1、开启Deepfence代理（使用管理控制台的IP地址替换其中的x.x.x.x，使用你自己的API密钥替换掉C8TtyEtNB0gBo1wGhpeAZICNSAaGWw71BSdS2kLELY0）：

    
    
    # helm v2
    
    helm install --repo https://deepfence.github.io/ThreatMapper/files/helm-chart deepfence-agent \
    
        --name=deepfence-agent \
    
        --set managementConsoleIp=x.x.x.x \
    
        --set deepfenceKey=C8TtyEtNB0gBo1wGhpeAZICNSAaGWw71BSdS2kLELY0
    
    # helm v3
    
    helm install deepfence-agent --repo https://deepfence.github.io/ThreatMapper/files/helm-chart deepfence-agent \
    
        --set managementConsoleIp=x.x.x.x \
    
    --set deepfenceKey=C8TtyEtNB0gBo1wGhpeAZICNSAaGWw71BSdS2kLELY0

2、删除Deepfence代理：

    
    
    # helm v2
    
    helm delete --purge deepfence-agent
    
    # helm v3
    
    helm delete deepfence-agent

## 如何使用ThreatMapper

### 注册一个用户

首先，我们需要在管理控制台中注册一个用户，在浏览器中访问平台IP地址x.x.x.x：

![](https://image.3001.net/images/20210408/1617887013_606eff252a4c433fd1a04.png!small)

### Deepfence API密钥设置

使用API或跟代理连接都需要用到API密钥：

![](https://image.3001.net/images/20210408/1617887020_606eff2cb82b4d2dbf1e3.png!small)

### 使用样例-可视化

你可以在topology标签页下以可视化的形式监控正在运行的虚拟机、主机、容器的整个拓扑。您可以单击各个节点来启动各种任务，如漏洞扫描：

![](https://image.3001.net/images/20210408/1617887028_606eff34745b13c85547b.png!small)

### 使用样例-运行时漏洞管理

从拓扑视图中，可以使用控制台仪表板或使用API启动针对容器和主机的运行时漏洞扫描：

![](https://image.3001.net/images/20210408/1617887039_606eff3f26fde0a2d8667.png!small)

导航到“漏洞”菜单，可以查看每个节点的漏洞和安全建议：

![](https://image.3001.net/images/20210408/1617887050_606eff4adef58badc0a0f.png!small)

单击上图中的某个项目可提供详细视图：

![](https://image.3001.net/images/20210408/1617887057_606eff516a4edde59899b.png!small)

“最易受攻击的漏洞”选项卡提供了目标系统中要按优先级修复的漏洞排序列表。排名是使用各种参数计算的，比如镜像是否正在运行、CVE分数和漏洞的严重性：

![](https://image.3001.net/images/20210408/1617887063_606eff576b2cb4eaa79f2.png!small)

## 项目地址

ThreatMapper：https://github.com/deepfence/ThreatMapper

