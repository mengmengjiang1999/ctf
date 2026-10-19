![](https://image.3001.net/images/20220803/1659536190_62ea833e242d0aae134dd.jpg!small)

## 关于kubeaudit

kubeaudit是一款针对Kubernetes集群安全的审计工具，该工具基于命令行实现其功能，并通过Golang包帮助广大研究人员审计Kubernetes集群中的各种安全问题，其中包括以非root权限运行或使用只读root文件系统等等。

## 工具安装

### Brew

    
    
    brew install kubeaudit

### 下载源码

广大研究人员还可以直接访问该项目的【[
_Releases页面_](https://github.com/Shopify/kubeaudit/releases)】下载最新的官方稳定版。

### 自定义构建

该项目可能随时会进行代码更新，如需使用最新版本的功能，你可以选择进行自定义构建，在构建前别忘了在本地设备上安装并配置好Go
v1.17+环境，然后运行下列命令：

    
    
    go get -v github.com/Shopify/kubeaudit

### Docker使用

该项目还提供了一个Docker镜像：[shopify/kubeaudit](https://hub.docker.com/r/shopify/kubeaudit)，广大研究人员也可以通过Docker镜像来运行kubeaudit。

## 工具使用

kubeaudit提供了以下三种模式：

> 1、Manifest模式
>
> 2、本地模式
>
> 3、集群模式

### Manifest模式

我们可以通过“-f/--manifest”选项来给工具提供一个Kubernetes
Manifest文件，此时kubeaudit将会审计这个Manifest文件。

参考命令如下：

    
    
    kubeaudit all -f "/path/to/manifest.yml"

输出结果如下：

    
    
    $ kubeaudit all -f "internal/test/fixtures/all_resources/deployment-apps-v1.yml"
    
     
    
    ---------------- Results for ---------------    
     
    
      apiVersion: apps/v1
    
      kind: Deployment
    
      metadata:
    
        name: deployment
    
        namespace: deployment-apps-v1
    
     
    
    --------------------------------------------    
     
    
    -- [error] AppArmorAnnotationMissing
    
       Message: AppArmor annotation missing. The annotation 'container.apparmor.security.beta.kubernetes.io/container' should be added.
    
       Metadata:
    
          Container: container
    
          MissingAnnotation: container.apparmor.security.beta.kubernetes.io/container
    
     
    
    -- [error] AutomountServiceAccountTokenTrueAndDefaultSA
    
       Message: Default service account with token mounted. automountServiceAccountToken should be set to 'false' or a non-default service account should be used.
    
     
    
    -- [error] CapabilityShouldDropAll
    
       Message: Capability not set to ALL. Ideally, you should drop ALL capabilities and add the specific ones you need to the add list.
    
       Metadata:
    
          Container: container
    
          Capability: AUDIT_WRITE
    
    ...

如果没有报错并且没有安全问题的话，则会返回下列内容：

    
    
    All checks completed. 0 high-risk vulnerabilities found

### 自动修复

Manifest模式还支持使用“autofix”命令自动修复所有的安全问题：

    
    
    kubeaudit autofix -f "/path/to/manifest.yml"

### 集群模式

kubeaudit支持检测当前环境是否是集群中的一个容器，并尝试审计该集群中所有的Kubernetes资源：

    
    
    kubeaudit all

### 本地模式

kubeaudit将会使用本地kubeconfig文件（$HOME/.kube/config）尝试与一个集群进行连接，可以使用“--kubeconfig”选项来指定kubeconfig路径：

    
    
    kubeaudit all --kubeconfig "/path/to/config" --context my_cluster

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/Shopify/kubeaudit/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **kubeaudit** ：【[ _GitHub传送门_](https://github.com/Shopify/kubeaudit)】

## 参考资料

> [
> _https://pkg.go.dev/github.com/Shopify/kubeaudit_](https://pkg.go.dev/github.com/Shopify/kubeaudit)
>
> [ _https://kubernetes.io/docs/concepts/configuration/organize-cluster-> access-> kubeconfig/_](https://kubernetes.io/docs/concepts/configuration/organize-> cluster-access-kubeconfig/)

