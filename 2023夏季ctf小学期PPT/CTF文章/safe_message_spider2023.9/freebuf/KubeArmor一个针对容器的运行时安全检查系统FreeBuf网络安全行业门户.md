![](https://image.3001.net/images/20210508/1620461872_6096493013afdbea7a523.png!small)

## KubeArmor介绍

KubeArmor是一个支持容器的运行时安全实施系统，它可以从系统级别限制容器的行为（如进程执行、文件访问、网络操作和资源利用率）。

KubeArmor使用Linux安全模块（LSM）运行，这意味着如果Linux内核中启用了Linux安全模块（例如AppArmor、SELinux或KRSI），它将可以在任何Linux平台（如Alpine、Ubuntu和Google的容器优化操作系统）上运行。KubeArmor将使用适当的LSM来执行所需的策略。

KubeArmor是为Kubernetes环境设计的，因此研究人员只需定义安全策略并将其应用于Kubernetes即可。接下来，KubeArmor将自动检测来自Kubernetes的安全策略更改，并将其强制执行到相应的容器中，而无需任何人为干预。

如果检测到了任何违反安全策略的行为，KubeArmor会立即生成具有容器标识的审核日志。如果研究人员还使用了其他日志记录系统，也会自动将审计日志发送至他们的系统中。

![](https://image.3001.net/images/20210508/1620461881_60964939108f31c5787b0.png!small)

## 功能性概览

> 系统级别限制容器行为
>
> 在运行时对容器强制执行安全策略
>
> 生成支持容器的安全审计日志
>
> 为策略定义提供易于使用的语义
>
> 支持容器间的网络安全实施

## 工具部署

KubeArmor目前支持自管理的Kubernetes和Google Kubernetes Engine (GKE)，此后还将支持Amazon
Elastic Kubernetes Service (EKS)和Azure Kubernetes Service (AKS)。

根据你的环境，可以选择以下选项之一：

 **在自管理Kubernetes中部署KubeArmor（使用Docker）：**

    
    
    $ cd deployments/generic-docker
    
      (generic-docker) $ kubectl apply -f .

 **在自管理Kubernetes中部署KubeArmor（使用容器）：**

    
    
    $ cd deployments/generic-containerd
    
      (generic-containerd) $ kubectl apply -f .

 **在MicroK8中部署KubeArmor：**

    
    
    $ cd deployments/microk8s
    
      (microk8s) $ kubectl apply -f .

 **在GKE中部署KubeArmor：**

    
    
    $ cd deployments/GKE
    
      (GKE) $ kubectl apply -f .

## 针对容器的安全策略定义

    
    
    apiVersion: security.accuknox.com/v1
    
    kind:KubeArmorPolicy
    
    metadata:
    
      name: [policy name]
    
      namespace: [namespace name]
    
     
    
    spec:
    
      severity: [1-10]
    
     
    
      tag:                                     # --> optional
    
      - [tag]
    
     
    
      message: [message]                       # --> optional
    
     
    
      selector:
    
        matchLabels:
    
          [key1]: [value1]
    
          [keyN]: [valueN]
    
     
    
      process:
    
        matchPaths:
    
        - path: [absolute executable path]
    
          ownerOnly: [true|false]              # --> optional
    
          fromSource:                          # --> optional
    
            - path: [absolute exectuable path]
    
            - dir: [absolute directory path]
    
              recursive: [true|false]
    
        matchDirectories:
    
        - dir: [absolute directory path]
    
          recursive: [true|false]              # --> optional
    
          ownerOnly: [true|false]              # --> optional
    
          fromSource:                          # --> optional
    
            - path: [absolute exectuable path]
    
            - dir: [absolute directory path]
    
              recursive: [true|false]
    
        matchPatterns:
    
        - pattern: [regex pattern]
    
          ownerOnly: [true|false]              # --> optional
    
     
    
      file:
    
        matchPaths:
    
        - path: [absolute file path]
    
          readOnly: [true|false]               # --> optional
    
          ownerOnly: [true|false]              # --> optional
    
          fromSource:                          # --> optional
    
            - path: [absolute exectuable path]
    
            - dir: [absolute directory path]
    
              recursive: [true|false]
    
        matchDirectories:
    
        - dir: [absolute directory path]
    
          recursive: [true|false]              # --> optional
    
          readOnly: [true|false]               # --> optional
    
          ownerOnly: [true|false]              # --> optional
    
          fromSource:                          # --> optional
    
            - path: [absolute exectuable path]
    
            - dir: [absolute directory path]
    
              recursive: [true|false]
    
        matchPatterns:
    
        - pattern: [regex pattern]
    
          readOnly: [true|false]               # --> optional
    
          ownerOnly: [true|false]              # --> optional
    
     
    
      network:
    
        matchProtocols:
    
        - protocol: [TCP|tcp|UDP|udp|ICMP|icmp]
    
          fromSource:                          # --> optional
    
          - path: [absolute exectuable path]
    
          - dir: [absolute directory path]
    
            recursive: [true|false]
    
     
    
      capabilities:
    
        matchCapabilities:
    
        - capability: [capability name]
    
          fromSource:                          # --> optional
    
          - path: [absolute exectuable path]
    
          - dir: [absolute directory path]
    
            recursive: [true|false]
    
     
    
      action: [Audit|Allow|Block|AllowWithAudit|BlockWithAudit]

## 许可证协议

本项目的开发与发布遵循Apache V2.0开源许可证协议，基于eBPF的容器监控器基于GPL V2.0开源许可证协议。

## 项目地址

KubeArmor：【[ _GitHub传送门_](https://github.com/accuknox/KubeArmor)】

## 参考资料

[ _https://github.com/accuknox/KubeArmor/blob/master/getting-started/security_policy_specification.md_](https://github.com/accuknox/KubeArmor/blob/master/getting-started/security_policy_specification.md)

[ _https://github.com/accuknox/KubeArmor/blob/master/getting-started/security_policy_examples.md_](https://github.com/accuknox/KubeArmor/blob/master/getting-started/security_policy_examples.md)

[ _https://github.com/accuknox/KubeArmor/blob/master/getting-started/host_security_policy_specification.md_](https://github.com/accuknox/KubeArmor/blob/master/getting-started/host_security_policy_specification.md)

[ _https://github.com/accuknox/KubeArmor/blob/master/getting-started/host_security_policy_examples.md_](https://github.com/accuknox/KubeArmor/blob/master/getting-started/host_security_policy_examples.md)

[
_https://github.com/accuknox/KubeArmor/blob/master/contribution/technical_roadmap.md_](https://github.com/accuknox/KubeArmor/blob/master/contribution/technical_roadmap.md)

[ _https://kubearmor.herokuapp.com/﻿_](https://kubearmor.herokuapp.com/)

