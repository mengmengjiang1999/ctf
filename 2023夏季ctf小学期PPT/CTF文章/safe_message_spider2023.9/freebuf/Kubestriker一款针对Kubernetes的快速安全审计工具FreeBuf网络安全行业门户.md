![](https://image.3001.net/images/20210317/1615968781_6051ba0d1c29108c57835.png!small)

## 基本概述

Kubestriker是一款针对Kubernetes的快速安全审计工具，Kubestriker可以对Kubernetes的infra容器执行大量深入检测，以帮助研究人员识别其中存在的安全错误配置以及其他安全问题。这些安全问题可能是工程师或开发人员在使用Kubernetes会遇到的，尤其是在大规模生成环境之中，一个小小的安全问题可能会带来严重的安全风险。

Kubestriker不依赖于特定平台运行，它可以在多个平台上工作，比如说自托管的[
_Kubernetes_](https://kubernetes.io/)、[ _Amazon
EKS_](https://aws.amazon.com/eks)、[ _Azure
AKS_](https://azure.microsoft.com/en-us/services/kubernetes-service/)和[
_Google GKE_](https://cloud.google.com/kubernetes-engine)等。

![](https://image.3001.net/images/20210317/1615968801_6051ba21d76a041b8b15a.gif)

## 支持的功能

> 扫描自管理和云提供商管理的Kubernetes infra；
>
> 各种服务或开放端口的网络侦察阶段扫描；
>
> 如果启用了不安全的读写或只读服务，则执行自动扫描；
>
> 执行验证扫描和未验证扫描；
>
> 扫描群集中的各种IAM错误配置；
>
> 扫描各种包含错误配置的容器；
>
> 扫描各种包含错误配置的Pod安全策略；
>
> 扫描各种错误配置的网络策略；
>
> 扫描群集中某个主题的权限；
>
> 在容器上运行命令并返回输出；
>
> 提供包含错误配置的服务的终端节点；
>
> 提供可能的权限提升详细信息；
>
> 详细的扫描报告；

## 工具安装

### 克隆代码库并安装

在安装该工具或克隆并运行该应用程序之前，我们需要在本地安装好[ _Git_](https://git-scm.com/)、[ _Python
3_](https://www.python.org/downloads/)和[
_pip_](https://pypi.org/project/pip/)。我们建议广大研究人员在[
_虚拟环境_](https://virtualenv.pypa.io/en/latest/installation.html)中安装和使用该工具。

接下来，我们可以在命令行工具中运行下列命令。

创建Python虚拟环境：

    
    
    $ python3 -m venv env

激活Python虚拟环境：

    
    
    $ source env/bin/activate

克隆项目代码库：

    
    
    $ git clone https://github.com/vchinnipilli/kubestriker.git

切换至项目目录：

    
    
    $ cd kubestriker

安装依赖组件:

    
    
    $ pip install -r requirements.txt

避免弹出错误提醒：

    
    
    $ pip install prompt-toolkit==1.0.15
    
    $ pip install -r requirements.txt

部署Kubestriker：

    
    
    $ python -m kubestriker

此时，我们将能够看到当前工作目录中已经生成了工具实例。

### 使用pip安装

为了安装并运行Kubestriker，我们需要在本地系统上安装好pip工具。接下来，我们可以在命令行工具中运行下列命令。

创建Python虚拟环境：

    
    
    $ python3 -m venv env

激活Python虚拟环境：

    
    
    $ source env/bin/activate

使用pip安装Kubestriker：

    
    
    $ pip install kubestriker

避免弹出错误提醒：

    
    
    $ pip install prompt-toolkit==1.0.15
    
    $ pip install kubestriker

部署Kubestriker：

    
    
    $ python -m kubestriker

此时，我们将能够看到当前工作目录中已经生成了工具实例。

## 如何配置Kubestriker容器

点击【[
_这里_](https://hub.docker.com/repository/docker/cloudsecguy/kubestriker)】获取Kubestriker容器的最新发布版本。

配置Kubestriker容器：

    
    
    $ docker run -it --rm -v /Users/vasantchinnipilli/.kube/config:/root/.kube/config -v "$(pwd)":/kubestriker --name kubestriker cloudsecguy/kubestriker:v1.0.0

将商上述命令中的用户vasantchinnipilli 替换成你自己的用户名，并修改Kube配置文件的绝对路径：

    
    
    $ docker run -it --rm -v /Users/<yourusername>/.kube/config:/root/.kube/config -v "$(pwd)":/kubestriker --name kubestriker cloudsecguy/kubestriker:v1.0.0

部署Kubestriker：

    
    
    $ python -m kubestriker

此时，我们将能够看到当前工作目录中已经生成了工具实例。

![](https://image.3001.net/images/20210317/1615968896_6051ba802a1b5f1201d74.gif)

## 支持的扫描类型

### 认证扫描

认证扫描要求用户至少具有只读权限，并在扫描期间提供令牌。请使用下面提供的链接创建只读用户：

Amazon EKS只读权限用户创建：【[
_传送门_](https://docs.aws.amazon.com/eks/latest/userguide/add-user-role.html)】

Azure AKS只读权限用户创建：【[ _传送门_](https://docs.microsoft.com/en-us/azure/aks/control-kubeconfig-access)】

Google GKE只读权限用户创建：【[ _传送门_](https://cloud.google.com/kubernetes-engine/docs/how-to/iam)】

使用基于访问控制的角色创建一个主题：【[ _传送门_](https://medium.com/@rschoening/read-only-access-to-kubernetes-cluster-fcf84670b698)】

从EKS集群获取一个令牌：

    
    
    $ aws eks get-token --cluster-name cluster-name --region ap-southeast-2

从AKS集群获取一个令牌：

    
    
    $ az aks get-credentials --resource-group myResourceGroup --name myAKSCluster

从GKE集群获取一个令牌：

    
    
    $ gcloud container clusters get-credentials CLUSTER_NAME --zone=COMPUTE_ZONE

从服务账号获取一个令牌：

    
    
    $ kubectl -n namespace get secret serviceaccount-token -o jsonpath='{.data.token}'

从一个Pod直接获取令牌或通过命令行执行漏洞获取令牌：

    
    
    $ cat /run/secrets/kubernetes.io/serviceaccount/token

### 未认证扫描

如果允许对目标群集进行匿名访问，则可以对目标执行未认证扫描。

 **识别Kubernetes主节点上开放的不安全端口：**

![](https://image.3001.net/images/20210317/1615968933_6051baa5d02d753604c12.gif)

 **使用kubelet读写和只读开放端口来识别Worker节点：**

![](https://image.3001.net/images/20210317/1615968987_6051badb2e525995b9451.gif)

## 许可证协议

本项目的开发与发布遵循Apache开源许可证协议。

## 项目地址

Kubestriker：【[ _GitHub传送门_](https://github.com/vchinnipilli/kubestriker)】

## 参考资料

> [ _https://docs.aws.amazon.com/eks/latest/userguide/add-user-> role.html_](https://docs.aws.amazon.com/eks/latest/userguide/add-user-> role.html)
>
> [ _https://docs.microsoft.com/en-us/azure/aks/control-kubeconfig-> access_](https://docs.microsoft.com/en-us/azure/aks/control-kubeconfig-> access)
>
> [ _https://cloud.google.com/kubernetes-engine/docs/how-> to/iam_](https://cloud.google.com/kubernetes-engine/docs/how-to/iam)
>
> [ _https://medium.com/@rschoening/read-only-access-to-kubernetes-cluster-> fcf84670b698_](https://medium.com/@rschoening/read-only-access-to-> kubernetes-cluster-fcf84670b698)
>
> [
> _https://hub.docker.com/repository/docker/cloudsecguy/kubestriker_](https://hub.docker.com/repository/docker/cloudsecguy/kubestriker)
>
> [ _https://pypi.org/project/pip/_](https://pypi.org/project/pip/)
>
> [
> _https://virtualenv.pypa.io/en/latest/installation.html_](https://virtualenv.pypa.io/en/latest/installation.html)
>
> [ _https://git-scm.com/_](https://git-scm.com/)
>
> [ _https://www.python.org/downloads/_](https://www.python.org/downloads/)

