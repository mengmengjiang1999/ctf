![](https://image.3001.net/images/20230826/1693059228_64ea089c96d021f64e225.png!small)

## 关于Polaris

Polaris是一款针对Kubernetes的开源安全策略引擎，可以帮助广大研究人员通过验证和修复Kubernetes的资源配置，来审查Kubernetes集群是否遵循了最佳安全实践。

当前版本的Polaris包含了30多种内置的配置策略，并且能够使用JSON
Schema构建自定义策略。如果你通过命令行或Webhook运行Polaris的话，Polaris则可以根据策略标准自动修复问题。

## 工具特性

Polaris支持下列三种运行模式：

> 1、[
> _仪表盘模式_](https://polaris.docs.fairwinds.com/dashboard)：根据“策略即代码”来验证Kubernetes资源安全态势；
>
> 2、[ _准入控制器模式_](https://polaris.docs.fairwinds.com/admission-> controller)：自动拒绝或修改不符合组织策略的工作负载；
>
> 3、[ _命令行工具_](https://polaris.docs.fairwinds.com/infrastructure-as-> code)：将策略作为代码纳入CI/CD流程，以测试本地YAML文件；

![](https://image.3001.net/images/20230826/1693059240_64ea08a8aeac7a67bc91f.png!small)

## Polaris仪表盘

Polaris仪表盘可以使用kubectl或Helm安装在集群上。它也可以在本地运行，并使用存储在KUBECONFIG中的凭据连接到集群。

需要注意的是，仪表盘是了解集群或“代码基础结构”中哪些工作负载不符合最佳实践的好方法。

## 工具安装

### Helm安装

    
    
    helm repo add fairwinds-stable https://charts.fairwinds.com/stable
    
    helm upgrade --install polaris fairwinds-stable/polaris --namespace polaris --create-namespace
    
    kubectl port-forward --namespace polaris svc/polaris-dashboard 8080:80

### 本地代码安装

首先，你需要一个有效的KUBECONFIG来设置仪表盘并连接到你的集群。

广大研究人员可以直接访问该项目的【[
_Releases页面_](https://github.com/fairwindsops/polaris/releases)】来下载最新的代码发布版本，或使用【[
_Homebrew_](https://brew.sh/)】安装：

    
    
    brew tap reactiveops/tap
    
    brew install reactiveops/tap/polaris
    
    polaris dashboard --port 8080

我们还可以将仪表盘指向本地文件系统：

    
    
    polaris dashboard --port 8080 --audit-path=./deploy/

### 本地Docker容器安装

    
    
    docker run -d -p8080:8080 -v ~/.kube/config:/opt/app/config:ro  quay.io/fairwinds/polaris:1.2 polaris dashboard --kubeconfig /opt/app/config

## 工具使用

Polaris仪表板可以简单直观地了解Kubernetes工作负载的当前状态，以及可以改进的路线图。仪表板提供了集群范围的概述，以及按类别、命名空间和工作负载划分结果：

![](https://image.3001.net/images/20230826/1693059277_64ea08cd3bb464a2bece7.png!small)

Polaris的默认标准是非常高的，所以如果你的分数低于你的预期，请不要感到惊讶。Polaris的一个关键目标是设定一个高标准，并在默认情况下实现出色的配置。如果我们包含的默认值过于严格，那么很容易将配置作为部署配置的一部分进行调整，以更好地适应你的工作负载。

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_-2.0_](https://github.com/FairwindsOps/polaris/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Polaris** ：【[ _GitHub传送门_](https://github.com/FairwindsOps/polaris)】

## 参考资料

> [
> _https://polaris.docs.fairwinds.com/_](https://polaris.docs.fairwinds.com/)
>
> [
> _https://github.com/FairwindsOps/Goldilocks_](https://github.com/FairwindsOps/Goldilocks)
>
> [
> _https://github.com/FairwindsOps/Pluto_](https://github.com/FairwindsOps/Pluto)
>
> [
> _https://github.com/FairwindsOps/Nova_](https://github.com/FairwindsOps/Nova)
>
> [ _https://github.com/FairwindsOps/rbac-> manager_](https://github.com/FairwindsOps/rbac-manager)

