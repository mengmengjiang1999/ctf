![](https://image.3001.net/images/20210616/1623848068_60c9f4840cc40961c9838.jpg!small)

## 关于Krane

Krane是一款功能强大的Kubernetes RBAC静态分析与可视化工具，该工具可以帮助广大研究人员分析K8s
RBAC设计中存在的安全隐患，并提供相应的安全防范措施及建议。Krane的仪表盘可以显示当前RBAC的安全态势，并允许我们查看其他相关详情。

## 功能介绍

> RBAC风险规则：Krane可以评估一组内置的RBAC风险规则，并支持使用一组自定义规则修改或扩展这些规则。
>
> 便携性：Krane能够以下列模式执行：命令行工具、Docker容器、CI/CD管道或单独服务。
>
> 报告：Krane能够以机器可读的格式声称详细的RBAC风险评估报告。
>
> 仪表盘：Krane提供了简单友好的仪表盘UI，帮助广大研究人员更好地了解目标Kubernetes RBAC的安全情况。
>
> 警报：如果检测到了中、高安全风险，Krane将会通过Slack向用户发出警报。
>
> 图形化RBAC：Krane可以将Kubernetes
> RBAC全部索引到一个本地图形数据库中，这使得RBAC数据的任何进一步的特殊查询都变得容易，支持使用任意CypherQL查询。

## 工具架构

![](https://image.3001.net/images/20210616/1623848086_60c9f496e1c1de0d83566.png!small)

## Krane本地运行

Krane的功能依赖于RedisGraph，docker-compose栈定义了Krane服务本地构建和运行的所有依赖：

    
    
    docker-compose up -d

注意，Krane的Docker镜像会自动进行预编译。

在本地运行docker-compose时，Krane不会自动开启RBAC报告和仪表盘，容器默认会休眠24小时，这个可以在docker-compose.override.yml中调整。

 **Krane执行：**

    
    
    # Exec into a running Krane container
    
    docker-compose exec krane bash
    
    # Once in the container you can start using `krane` commands. Try `krane -help`.
    
    $ krane -h

 **检查正在运行的服务以及相关端口：**

    
    
    docker-compose ps

 **停止Krane运行及其相关服务：**

    
    
    docker-compose down

## Krane可用命令

    
    
    $ krane --help
    
      NAME:
    
        krane
    
      DESCRIPTION:
    
        Kubernetes RBAC static analysis & visualisation tool
    
      COMMANDS:
    
        dashboard Start K8s RBAC dashboard server
    
        help      Display global or [command] help documentation
    
        report    Run K8s RBAC report
    
      GLOBAL OPTIONS:
    
        -h, --help
    
            Display help documentation
    
     
    
        -v, --version
    
            Display version information
    
     
    
        -t, --trace
    
            Display backtrace when an error occurs
    
     
    
      AUTHOR:
    
     
    
        Marcin Ciszak <marcin.ciszak@appvia.io> - Appvia Ltd <appvia.io>

## 生成RBAC报告

针对一个正在运行的集群，生成报告时需要提供一个kubectl上下文：

    
    
    krane report -k <context>

针对本地RBAC yaml/json文件运行，需要提供一个目录路径：

    
    
    krane report -d </path/to/rbac-directory>

针对一个正在Kubernetes集群中运行的容器生成报告：

    
    
    krane report --incluster

## 可视化仪表盘

查看RBAC数、网络图和最新的报告结果，首先需要启动仪表盘服务器：

    
    
    krane dashboard

注意：本地Web服务器默认端口为8000，并且会显示仪表盘地址。

## 项目地址

 **Krane：** 【[ _GitHub传送门_](https://github.com/appvia/krane)】

