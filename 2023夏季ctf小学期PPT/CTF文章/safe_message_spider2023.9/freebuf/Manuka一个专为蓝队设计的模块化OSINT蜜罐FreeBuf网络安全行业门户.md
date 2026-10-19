![](https://image.3001.net/images/20201121/1605969557_5fb92695df79f629f1970.png!small)

## 工具介绍

Manuka是一款公开资源情报（OSINT）蜜罐，可以帮助广大研究人员监控威胁攻击者的网络侦察活动，并为蓝队研究人员生成实用的行动情报信息。该工具能够创建一个模拟环境，包括分阶段的OSINT源，如社交媒体简介和泄露的凭证，并跟踪对手的兴趣迹象，以及与MITRE的PRE-ATT&CK框架密切相关的一些信息。Manuka可以为蓝队人员提供预攻击网络侦察阶段的可视化信息，并为安全防御人员提供预警信号。

尽管它们的规模和复杂程度各不相同，但大多数传统蜜罐都专注于网络方面的行为。这些蜜罐系统可以在网络攻击链中的第二阶段至第七阶段发现攻击者的活动：

![](https://image.3001.net/images/20201121/1605969575_5fb926a74234cbfd28662.png!small)

Manuka能够在网络攻击链的第一阶段执行OSINT威胁检测，并且Manuka支持自定义扩展。这也就意味着，研究人员可以轻松添加新的监听器模块，然后将其插入到Docker化的环境中。它们还可以协同跟多个蜜罐进行交互活动，以扩展蜜罐的应用范围。此外，用户可以快速定制和部署Manuka以匹配不同的用例。值得一提的是，Manuka的数据格式可以轻松移植到其他组织工作流中的第三方可视化分析工具之中。

由于OSINT技术的复杂性和广泛性，设计一个良好的OSINT蜜罐就变成了一个新的挑战，为此，Manuka便应运而生。

## 工具架构

Manuka的构建基于下列关键元素和执行流程：

![](https://image.3001.net/images/20201121/1605969585_5fb926b142f43634659d5.jpg!small)

> Sources：即可能的OSINT向量，例如社交媒体资料、泄露的凭证信息和泄露的源代码。
>
> Listeners：用于监控攻击者交互行为的服务器。
>
> Hits：一些有趣的指标，例如使用泄露凭证的登录尝试和社交媒体连接。
>
> Honeypots：用于监听单一活动，并分析和跟踪一段时间内的活动行为。

## 工具系统设计

![](https://image.3001.net/images/20201121/1605969596_5fb926bc53d8c787587ca.jpg!small)

工具框架本身由多个Docker容器组成，支持部署在单一主机上：

> manuka-server：中央Golang服务器，负责执行CURD操作，并从监听器获取信息；
>
> manuka-listener：模块化Golang服务器，可执行不同的监听器角色；
>
> manuka-client：为蓝队人员提供仪表盘以管理Manuka的资源；

这些容器可以通过一个Docker-Compose命令来进行管理。

## 工具要求

    
    
    docker >= 19.03.8
    
    docker-compose >= 1.25.4
    
    ngok >= 2.3.35

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/spaceraccoon/manuka.git

 **在开发过程中，相应组件运行的端口如下：**

    
    
    manuka-client: 3000
    
    manuka-server: 8080
    
    manuka-listener: 8080

## 工具运行

    
    
    COMPANY_NAME='Next Clarity Financial' NGINX_USERNAME=username NGINX_PASSWORD=password docker-compose -f docker-compose.yml -f docker-compose-prod.yml up --build --remove-orphans -d

其中，NGINX_USERNAME和NGINX_PASSWORD即为仪表盘登录的基础认证凭据，而COMPANY_NAME则为伪造的登陆页面企业名称。

## 当前支持的监听器

### 社交媒体监听器

监控Facebook和LinkedIn上的社交活动，当前支持网络连接尝试通知。请注意，受监视的社交媒体帐户应启用电子邮件通知。从社交媒体平台接收电子邮件通知的相应电子邮件帐户应配置为将这些电子邮件转发到集中的Gmail帐户。

### 登录监听器

支持监听在蜜罐网站上使用泄露凭证进行登录尝试的行为。

## 工具仪表盘

![](https://image.3001.net/images/20201121/1605969641_5fb926e90837438c5fb45.png!small)

## 项目地址

Manuka：【[ _GitHub传送门_](https://github.com/spaceraccoon/manuka)】

  

