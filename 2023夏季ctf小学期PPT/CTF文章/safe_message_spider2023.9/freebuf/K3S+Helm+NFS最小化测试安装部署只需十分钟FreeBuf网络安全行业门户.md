## k3s 简介

官方文档：[k3s](https://docs.rancher.cn/docs/k3s/_index/)

什么是k3s

`k3s 是一个轻量级的 Kubernetes 发行版 它针对边缘计算、物联网等场景进行了高度优化。 k3s 有以下增强功能：﻿`

1\. 打包为单个二进制文件。

2\. 使用基于 sqlite3 的轻量级存储后端作为默认存储机制。同时支持使用 etcd3、MySQL 和 PostgreSQL 作为存储机制。

3\. 封装在简单的启动程序中，通过该启动程序处理很多复杂的 TLS 和选项。

4\. 默认情况下是安全的，对轻量级环境有合理的默认值。

5\. 添加了简单但功能强大的batteries-included功能，例如：本地存储提供程序，服务负载均衡器，Helm controller 和
Traefik Ingress controller。

6\. 所有 Kubernetes control-plane 组件的操作都封装在单个二进制文件和进程中，使 k3s
具有自动化和管理包括证书分发在内的复杂集群操作的能力。

7\. 最大程度减轻了外部依赖性，k3s 仅需要 kernel 和 cgroup 挂载。 k3s 软件包需要的依赖项包括：

`containerd Flannel CoreDNS CNI 主机实用程序（iptables、socat 等） Ingress
controller（Traefik） 嵌入式服务负载均衡器（service load balancer） 嵌入式网络策略控制器（network
policy controller）`

## 为什么叫 k3s?

`k3s内存占用是k8s的一半 kubernetes是一个10个字母的单词，简写为k8s kubenetes的一半是5个字母，简写为k3s`

## 适用场景

k3s 适用于以下场景：

> 边缘计算-Edge
>
> 物联网-IoT
>
> CI
>
> Development
>
> ARM
>
> 嵌入 k8s

`由于运行 k3s 所需的资源相对较少，所以 k3s 也适用于开发和测试场景。
在这些场景中，如果开发或测试人员需要对某些功能进行验证，或对某些问题进行重现，那么使用 k3s 不仅能够缩短启动集群的时间，还能够减少集群需要消耗的资源。`

# 架构介绍

`k3s server 是运行k3s server命令的机器（裸机或虚拟机），而 k3s worker 节点是运行 k3s worker命令的机器`

## 单节点架构

`k3s 单节点集群的架构如下图所示，该集群有一个内嵌 SQLite 数据库的单节点 k3s server。 在这种配置中，每个 worker
节点都注册到同一个 server 节点。 k3s 用户可以通过调用 server 节点上的 k3s API 来操作 Kubernetes 资源。`

![img](https://image.3001.net/images/20221130/1669779681_6386d0e1741c86bd4dc27.png!small)

## 高可用架构

`虽然单节点 k3s 集群可以满足各种用例，但对于 Kubernetes control-plane 的正常运行至关重要的环境，您可以在高可用配置中运行
k3s。 一个高可用 k3s 集群由以下几个部分组成：`

  1. k3s Server 节点：两个或更多的server节点将为 Kubernetes API 提供服务并运行其他 control-plane 服务

  2. 外部数据库：与单节点 k3s 设置中使用的嵌入式 SQLite 数据存储相反，高可用 k3s 需要挂载一个external database外部数据库作为数据存储的媒介。

###  **k3s高可用架构:**

![img](https://image.3001.net/images/20221130/1669779682_6386d0e280eda6221c433.png!small)

## 固定 worker 节点的注册地址

`在高可用 k3s server 配置中，每个节点还必须使用固定的注册地址向 Kubernetes API 注册，注册后，worker 节点直接与其中一个
server 节点建立连接`

如下图所示：

![image.png](https://image.3001.net/images/20221130/1669779683_6386d0e36c25e774d8732.png!small)

## 注册 worker 节点

`Agent 节点用k3s worker进程发起的 websocket 连接注册，连接由作为代理进程一部分运行的客户端负载均衡器维护。`

`Agent 将使用节点集群 secret 以及随机生成的节点密码向 k3s server 注册，密码存储在
/etc/rancher/node/password路径下。 k3s server 将把各个节点的密码存储为 Kubernetes
secrets，随后的任何尝试都必须使用相同的密码。节点密码秘密存储在kube-system命名空间中，名称使用模板.node-password.k3s
``注意: 在 k3s v1.20.2 之前，k3s server 将密码存储在/var/lib/rancher/k3s/server/cred/node-passwd的磁盘上。 如果您删除了 worker 的/etc/rancher/node目录，则需要为该 worker 重新创建密码文件，或者从
server 中删除该条目。 通过使用--with-node-id标志启动 k3s server 或 worker，可以将唯一的节点 ID 附加到主机名中。
`自动部署的清单

    
    
    位于目录路径/var/lib/rancher/k3s/server/manifests 的清单在构建时被捆绑到 k3s 二进制文件中
    将由rancher/helm-controller在运行时安装。
    

## k3s默认容器运行时

`k3s默认使用 containerd 作为容器运行时 在 goroutine 中以 子进程 方式 启动 containerd `验证:

    
    
    ps aux | grep “k3s server”
    
    
    
    ps -A -ostat,pid,ppid,cmd |grep 7897
    

## 准备工作

### 关闭SELinux

    
    
    # 临时关闭
    setenforce 0
    # 永久关闭
    sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config
    

### 关闭swap

    
    
    # 临时关闭swap分区，当前会话生效，重启失效
    swapoff -a
    # 永久关闭swap分区
    sed -ri 's/.*swap.*/#&/' /etc/fstab
    

### 设置主机名

    
    
    # 临时修改主机名:hostname newname（本文涉及四台机器：一主三从）
    hostname k3s-master1
    hostname k3s-node1
    hostname k3s-node2
    hostname k3s-node3
    注：这种方式是立即生效，但是在服务器重启后会恢复成原来的名字
    # 永久性修改主机名：修改/etc/sysconfig/network文件内容
    vim /etc/sysconfig/network
    NETWORKING=yes
    HOSTNAME=localhost1
    注：这种方式不会立即生效，需要重启服务器才会生效，且永久性修改
    

## 离线安装

### 概述

`你可以使用两种不同的方法在离线环境中安装 k3s。 离线环境是不直接连接到 Internet 的任何环境。
你可以部署一个私有镜像仓库，或者你可以手动部署镜像，比如用于小型集群。`

 **离线安装的过程主要分为以下两个步骤：**

 **步骤 1：部署镜像**

 **步骤 2：安装 k3s**

**离线升级 k3s 版本: **完成离线安装 k3s 后，您还可以通过脚本升级 k3s 版本，或启用自动升级功能，以保持离线环境中的 k3s 版本与最新的
k3s 版本同步。

## 部署私有镜像仓库

 **前提条件**

`搭建私有仓库 ，例如 harbor仓库`

搭建参考[Harbor安装](http://xingyun.jd.com/shendeng/article/detail/6734?forumId=79&jdme_router=jdme%3A%2F%2Fweb%2F202206081297%3Furl%3Dhttps%3A%2F%2Fshendengh5.jd.com%2FarticleDetail%3Fid%3D6734)

 **创建镜像仓库 YAML**

`请按照 K3S 私有镜像仓库配置创建并配置registry.yaml文件。 完成后，现在可以转到下面的[安装 k3s]部分，开始安装 K3`

 **手动部署镜像**  
 **前提条件**

> 假设已经在离线环境中创建了节点。  
> 这种方法需要您手动将必要的镜像部署到每个节点，适用于运行无法部署镜像仓库的边缘部署场景。

 **操作步骤**

> 请按照以下步骤准备镜像目录和 k3s 二进制文件

  1. 从k3s GitHub Release页面获取你所运行的 k3s 版本的镜像 tar 文件。

  2. 将 tar 文件放在images目录下，例如：

    
    
    sudo mkdir -p /var/lib/rancher/k3s/worker/images/
    sudo cp k3s-airgap-images-amd64.tar /var/lib/rancher/k3s/worker/images/
    

  3. 将 k3s 二进制文件放在 /usr/local/bin/k3s路径下，并确保拥有可执行权限。完成后，现在可以转到下面的安装 k3s部分，开始安装 k3s。

    
    
    chmod +x k3s && cp k3s /usr/local/bin/
    

## 安装 k3s

> 更多安装选项参考 安装选项介绍 | Rancher文档

 **前提条件**

  1. 在安装 k3s 之前，完成上面的部署私有镜像仓库或手动部署镜像，导入安装 k3s 所需要的镜像。

  2. 从 release 页面下载 k3s 二进制文件，k3s 二进制文件需要与离线镜像的版本匹配。将二进制文件放在每个离线节点的 /usr/local/bin 中，并确保这个二进制文件是可执行的。

  3. 下载 k3s 安装脚本：<https://get.k3s.io>。将安装脚本放在每个离线节点的任意地方，并命名为 [install.sh](http://install.sh)。

> 当使用 INSTALL_K3S_SKIP_DOWNLOAD 环境变量运行 k3s 脚本时，k3s 将使用本地的脚本和二进制。

## 单节点安装

 **server节点**

    
    
    INSTALL_K3S_SKIP_DOWNLOAD=true ./install.sh
    

![image.png](https://image.3001.net/images/20221130/1669779684_6386d0e44df1c2c009cc7.png!small)

**worker节点**

    
    
    # 将 myserver 替换为 server 的 IP 或有效的 DNS
    # 将 mynodetoken 替换 server 节点的 token
    # token 通常在/var/lib/rancher/k3s/server/node-token
    
    INSTALL_K3S_SKIP_DOWNLOAD=true 
    K3S_URL=https://172.16.100.126:6443 K3S_TOKEN=K10ccf50e87c24f9a1db535bdc5f6cd0c7e87b4b7b321118c393563b07e0fa8b39f::server:6b9604a66f7a2d2ac22a2835e3aa7500 ./install.sh
    

> 注意：k3s 还为 kubelets 提供了一个--resolv-conf标志，这可能有助于在离线网络中配置 DNS

![image-20221118231106968](/Users/haojianwei1/Library/Application
Support/typora-user-images/image-20221118231106968.png)

 **添加worker角色标签**

    
    
    # 设置worker角色，工作节点不能默认添加 worker 角色，需要手动执行命令添加，新版本可能已修复此问题，
    # kubectl label nodes 节点名字 node-role.kubernetes.io/你想要的roles(=/-)
    # 最后括号里的加减号，减号就是删除roles，等号就是增加roles
    
    kubectl label node k3s-node1 node-role.kubernetes.io/worker=true --overwrite
    kubectl label node k3s-node2 node-role.kubernetes.io/worker=true --overwrite
    kubectl label node k3s-node3 node-role.kubernetes.io/worker=true --overwrite
    # --overwrite 代表如果已经存在worker角色标签，则覆盖（新标签创建时此操作不生效）
    

![image.png](https://image.3001.net/images/20221130/1669779685_6386d0e54384e68789f0b.png!small)

## kubectl命令行补全

    
    
    yum install bash-completion -y
    source /usr/share/bash-completion/bash_completion
    source <(kubectl completion bash)
    echo "source <(kubectl completion bash)" >> ~/.bashrc
    

## 高可用安装

>
> 需要调整安装命令，以便指定INSTALL_K3S_SKIP_DOWNLOAD=true并在本地运行安装脚本。您还将利用INSTALL_K3S_EXEC='args'为
> k3s 提供其他参数。

> 例如，使用外部数据库实现高可用安装指南的第二步提到了以下内容：
    
    
    curl -sfL https://get.k3s.io | sh -s - server \
    --datastore-endpoint='mysql://username:password@tcp(hostname:3306)/database-name'
    

> 由于在离线环境中无法使用curl命令进行安装，所以您需要参考以下示例，将这条命令行修改为离线安装：
    
    
    INSTALL_K3S_SKIP_DOWNLOAD=true INSTALL_K3S_EXEC='server' K3S_DATASTORE_ENDPOINT='mysql://username:password@tcp(hostname:3306)/database-name' ./install.sh
    

# 升级 k3s

### 通过脚本升级

 **离线环境的升级可以通过以下步骤完成：**

  1. 从k3s GitHub Release页面下载要升级到的 k3s 版本。将 tar 文件放在每个节点的/var/lib/rancher/k3s/worker/images/目录下。删除旧的 tar 文件。

  2. 复制并替换每个节点上/usr/local/bin中的旧 k3s 二进制文件。复制https://get.k3s.io 的安装脚本（因为它可能在上次发布后发生了变化）。再次运行脚本。

  3. 重启 k3s 服务。

### 启用自动升级功能

> 除了可以通过脚本升级 k3s 以外，您还可以启用自动升级功能，以保持离线环境中的 k3s 版本与最新的 k3s 版本同步。

> 从 v1.17.4+k3s1 开始，k3s 支持自动升级。要在离线环境中启用此功能，您必须确保所需镜像在您的私有镜像仓库中可用。

  1. 你将需要与你打算升级到的 k3s 版本相对应的 rancher/k3s-upgrade 版本。  
注意，镜像标签将 k3s 版本中的+替换为-，因为 Docker 镜像不支持+。

  2. 你还需要在你要部署的system-upgrad-controller manifestYAML 中指定的 system-upgrad-controller和kubectl的版本。  
在这里检查 system-upgrad-controller 的最新版本，并下载 system-upgrad-controller.yaml来确定你需要推送到私有镜像仓库的版本。例如，在system-upgrade-controller的 v0.4.0 版本中，在
manifest YAML 中指定了这些镜像：

    
    
    rancher/system-upgrade-controller:v0.4.0
    rancher/kubectl:v0.17.0将必要的 rancher/k3s-upgrade、rancher/system-upgrade-controller 和 rancher/kubectl 镜像添加到您的私有镜像仓库中以后 ，就可以按照k3s 自动升级指南进行操作。
    

# 停止k3s

### server节点停止k3s

    
    
    # 停止k3s
    systemctl stop k3s
    systemctl disable k3s
    # 杀掉进程的kill命令
    /usr/local/bin/k3s-killall.sh
    # 如果使用的是docker，需要执行发下命令
    docker ps -a|grep -v CONTAINER|awk '{print $1}'|xargs docker  stop
    docker ps -a|grep -v CONTAINER|awk '{print $1}'|xargs docker  rm
    systemctl stop docker
    systemctl disable docker
    

### worker节点停止k3s

    
    
    # 停止k3s-agent
    systemctl stop k3s-agent
    systemctl disable k3s-agent
    # 如果使用的是docker，需要执行发下命令
    docker ps -a|grep -v CONTAINER|awk '{print $1}'|xargs docker  stop
    docker ps -a|grep -v CONTAINER|awk '{print $1}'|xargs docker  rm
    systemctl stop docker
    systemctl disable docker
    

# 卸载 k3s

> 卸载 k3s 会删除集群数据和所有脚本。

> 要使用不同的安装选项重新启动集群，请使用不同的标志重新运行安装脚本。

### server 节点卸载 k3s

    
    
    /usr/local/bin/k3s-uninstall.sh
    

### worker 节点卸载 k3s

    
    
    /usr/local/bin/k3s-agent-uninstall.sh
    

# Helm简介

Helm 是 Kubernetes 生态系统中的一个软件包管理工具。本文将介绍 Helm 中的相关概念和基本工作原理，并通过一个具体的示例学习如何使用
Helm 打包、分发、安装、升级及回退 Kubernetes 应用。

## Kubernetes 应用部署的挑战

Kubernetes 是一个提供了基于容器的应用集群管理解决方案，Kubernetes
为容器化应用提供了部署运行、资源调度、服务发现和动态伸缩等一系列完整功能。

Kubernetes 的核心设计理念是: 用户定义要部署的应用程序的规则，而 Kubernetes
则负责按照定义的规则部署并运行应用程序。如果应用程序出现问题导致偏离了定义的规格，Kubernetes
负责对其进行自动修正。例如：定义的应用规则要求部署两个实例（Pod），其中一个实例异常终止了，Kubernetes 会检查到并重新启动一个新的实例。

用户通过使用 Kubernetes API 对象来描述应用程序规则，包括
Pod、Service、Volume、Namespace、ReplicaSet、Deployment、Job等等。一般这些资源对象的定义需要写入一系列的
YAML 文件中，然后通过 Kubernetes 命令行工具 Kubectl 调 Kubernetes API 进行部署。

以一个典型的三层应用 Wordpress 为例，该应用程序就涉及到多个 Kubernetes API 对象，而要描述这些 Kubernetes API
对象就可能要同时维护多个 YAML 文件。

![image.png](https://image.3001.net/images/20221208/1670479427_63917e4314fc87bb3e0c4.png!small)

从上图可以看到，在进行 Kubernetes 软件部署时，我们面临下述几个问题：

  * 如何管理、编辑和更新这些这些分散的 Kubernetes 应用配置文件。

  * 如何把一套相关的配置文件作为一个应用进行管理。

  * 如何分发和重用 Kubernetes 的应用配置。

Helm 的出现就是为了很好地解决上面这些问题。

## Helm 是什么？

Helm 是[Deis](https://deis.com/)开发的一个用于 Kubernetes 应用的包管理工具，主要用来管理 Charts。有点类似于
Ubuntu 中的 APT 或 CentOS 中的 YUM。

Helm Chart 是用来封装 Kubernetes 原生应用程序的一系列 YAML 文件。可以在你部署应用的时候自定义应用程序的一些
Metadata，以便于应用程序的分发。

对于应用发布者而言，可以通过 Helm 打包应用、管理应用依赖关系、管理应用版本并发布应用到软件仓库。

对于使用者而言，使用 Helm 后不用需要编写复杂的应用部署文件，可以以简单的方式在 Kubernetes 上查找、安装、升级、回滚、卸载应用程序。

## Helm 组件及相关术语

  * Helm

Helm 是一个命令行下的客户端工具。主要用于 Kubernetes 应用程序 Chart 的创建、打包、发布以及创建和管理本地和远程的 Chart 仓库。

  * Tiller

Tiller 是 Helm 的服务端，部署在 Kubernetes 集群中。Tiller 用于接收 Helm 的请求，并根据 Chart 生成
Kubernetes 的部署文件（ Helm 称为 Release ），然后提交给 Kubernetes 创建应用。Tiller 还提供了 Release
的升级、删除、回滚等一系列功能。

  * Chart

Helm 的软件包，采用 TAR 格式。类似于 APT 的 DEB 包或者 YUM 的 RPM 包，其包含了一组定义 Kubernetes 资源相关的
YAML 文件。

  * Repoistory

Helm 的软件仓库，Repository 本质上是一个 Web 服务器，该服务器保存了一系列的 Chart 软件包以供用户下载，并且提供了一个该
Repository 的 Chart 包的清单文件以供查询。Helm 可以同时管理多个不同的 Repository。

  * Release

使用`helm install`命令在 Kubernetes 集群中部署的 Chart 称为 Release。

> 注：需要注意的是：Helm 中提到的 Release 和我们通常概念中的版本有所不同，这里的 Release 可以理解为 Helm 使用 Chart
> 包部署的一个应用实例。

## Helm 工作原理

这张图描述了 Helm 的几个关键组件 Helm（客户端）、Tiller（服务器）、Repository（Chart
软件仓库）、Chart（软件包）之间的关系。

![image.png](https://image.3001.net/images/20221208/1670479460_63917e64a33911a1e0b0b.png!small)

Chart Install 过程

  * Helm 从指定的目录或者 TAR 文件中解析出 Chart 结构信息。

  * Helm 将指定的 Chart 结构和 Values 信息通过 gRPC 传递给 Tiller。

  * Tiller 根据 Chart 和 Values 生成一个 Release。

  * Tiller 将 Release 发送给 Kubernetes 用于生成 Release。

Chart Update 过程

  * Helm 从指定的目录或者 TAR 文件中解析出 Chart 结构信息。

  * Helm 将需要更新的 Release 的名称、Chart 结构和 Values 信息传递给 Tiller。

  * Tiller 生成 Release 并更新指定名称的 Release 的 History。

  * Tiller 将 Release 发送给 Kubernetes 用于更新 Release。

Chart Rollback 过程

  * Helm 将要回滚的 Release 的名称传递给 Tiller。

  * Tiller 根据 Release 的名称查找 History。

  * Tiller 从 History 中获取上一个 Release。

  * Tiller 将上一个 Release 发送给 Kubernetes 用于替换当前 Release。

Chart 处理依赖说明

Tiller 在处理 Chart 时，直接将 Chart 以及其依赖的所有 Charts 合并为一个 Release，同时传递给 Kubernetes。因此
Tiller 并不负责管理依赖之间的启动顺序。Chart 中的应用需要能够自行处理依赖关系。

# 部署 Helm

### 安装 Helm 客户端

Helm 的安装方式很多，这里采用二进制的方式安装。更多安装方法可以参考 Helm
的[官方帮助文档](https://docs.helm.sh/using_helm/#installing-helm)。

  * 使用官方提供的脚本一键安装

    
    
    curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get > get_helm.sh$ chmod 700 get_helm.sh
    ./get_helm.sh
    

  * 手动下载二进制包安装

    
    
    # 下载 Helm 
    wget https://get.helm.sh/helm-v3.9.3-linux-amd64.tar.gz
    
    # 解压 Helm$ 
    tar -zxvf helm-v3.9.3-linux-amd64.tar.gz
    
    # 复制客户端执行文件到 bin 目录下
    cp linux-amd64/helm /usr/local/bin/
    

Tiller 是以 Deployment 方式部署在 Kubernetes 集群中的，只需使用以下指令便可简单的完成安装。

    
    
    helm init
    

注：**[storage.googleapis.com](http://storage.googleapis.com/)**默认是不能访问的，该问题请自行解决。如果不清楚是否能访问，当你把这行命令cp
linux-amd64/helm /usr/local/bin/完，看一下是否都是ok的

![image.png](https://image.3001.net/images/20221130/1669779690_6386d0ea24bc53645df15.png!small)

    
    
    可以可以看到 Tiller 的 Service、Deployment是正常的，
    但是Pod是不正常的；镜像拉取失败，默认我们是注：storage.googleapis.com 默认是不能访问的，换个源下载一下；
    参考：https://www.hi-linux.com/posts/21466.html  换源
    

由于 Helm
默认会去[storage.googleapis.com](http://storage.googleapis.com/)拉取镜像，如果你当前执行的机器不能访问该域名的话可以使用以下命令来安装：

    
    
    # 使用某云镜像安装并把默认仓库设置为某云上的镜像仓库$ helm init --upgrade --tiller-image 某云镜像地址/google_containers/tiller:v2.12.2 --stable-repo-url https://某云镜像地址/charts
    
    可以看出现在已经正常running了，
    查看详细的信息
    kubectl describe pod tiller-deploy-dc95dbd5c-gvldb --namespace=kube-system
    

接下来查看状态

![image.png](https://image.3001.net/images/20221130/1669779690_6386d0eabfdcb64b86627.png!small)

上图可看出：现在，`helm version`已经能够查看到服务器的版本信息了，部署完成

后面下载包会报错，是因为从 Kubernetes 1.6 版本开始，API Server 启用了 RBAC 授权。目前的 Tiller
部署时默认没有定义授权的 ServiceAccount，这会导致访问 API Server 时被拒绝。所以我们需要明确为 Tiller 部署添加授权。

### 生成.kube配置

    
    
    ## 当使用helm 部署 Pod 的时候如果报以下错误，需要执行此步骤操作（说明没有访问kube-apiserver 权限）
    ## 如果 kubectl 在其他非master节点部署时同样也报如下错误，也需要执行此步骤操作
    Error: INSTALLATION FAILED: Kubernetes cluster unreachable: Get "http://localhost:8080/version": dial tcp [::1]:8080: connect: connection refused
    
    ## 不可用的时候需要复制master节点的/etc/rancher/k3s/k3s.yaml文件内容复制至客户端$HOME/.kube/config
    cat /etc/rancher/k3s/k3s.yaml
    mkdir -p $HOME/.kube
    sudo touch $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config
    

# 安装NFS

### 部署说明

Kubernetes网络文件系统，主要用于ES、Kafka、Minio等持久化存储。

### nfs搭建

    
    
    # ===========服务端（nfs节点）操作如下===========
    # 通过yum目录安装nfs服务和rpcbind服务
    yum -y install nfs-utils rpcbind
    
    # 启动服务
    systemctl start rpcbind
    systemctl enable rpcbind
    systemctl start nfs
    systemctl enable nfs
    
    # 查看nfs服务是否安装正常
    rpcinfo -p localhost
    
    # 或者是通过公网测试服务端的nfs服务是否可用。
    rpcinfo -p ServerIP
    
    # 显示如下即正常
    program vers proto port service
    100000 4 tcp 111 portmapper
    100000 3 tcp 111 portmapper
    ...
    100024 1 udp 45993 status
    100024 1 tcp 39431 status
    ...
    100005 1 udp 20048 mountd
    100005 1 tcp 20048 mountd
    ...
    100003 3 tcp 2049 nfs
    100003 4 tcp 2049 nfs
    100227 3 tcp 2049 nfs_acl
    ...
    100021 3 tcp 33941 nlockmgr
    100021 4 tcp 33941 nlockmgr
    
    # ===========客户端（k8s节点）操作如下===========
    # 通过yum目录安装nfs服务和rpcbind服务
    yum -y install nfs-utils rpcbind
    

### **配置共享目录**

    
    
    # ===========以下全部为nfs节点操作如下===========
    # 比如我们在服务端的共享目录为/export/nfs-share，接着输入以下命令
    echo "/export/nfs-share 172.16.100.0/20(rw,sync,no_root_squash,no_all_squash)" > /etc/exports
    
    # 要保证/export/nfs-share目录已经存在节点上，然后输入以下命令使共享目录生效。
    exportfs -r
    
    # 重新启动服务
    systemctl restart rpcbind
    systemctl restart nfs
    
    # 测试
    showmount -e localhost
    
    # 或者
    showmount -e 公网ip
    showmount 命令查询“mountd”守护进程，以显示NFS服务器加载的信息
    

# 部署Pod遇到的问题

### Helm部署Chart时报错

    
    
    Error: INSTALLATION FAILED: create: failed to create: Request entity too large: limit is 3145728
    
    以上报错信息，一般是由于chart目录里面存在大文件，把不必要的文件删除，只保留chart相关的，再次helm install即可
    

### 部署 nfs pod时报错

![image.png](https://image.3001.net/images/20221130/1669779691_6386d0eb7a7dd00aad480.png!small)

    
    
    # 上面的原因一般是由于nfs运行所在的节点，访问nfs不通，需要在集群的全部工作节点执行安装nfs客户端命令：
    yum -y install nfs-utils rpcbind
    

### Pod拉取镜像超时报错

![image.png](https://image.3001.net/images/20221130/1669779692_6386d0ec7b2b08588a013.png!small)

    
    
    以上报错信息，一般是由于官网方法部署k3s，默认使用的是containerd作为容器运行环境，使用的是海外的镜像仓库，导致拉镜像超时，可在pod配置镜像加速，设置地址为国内，参考常用命令：crictl命令使用 --> 配置containerd镜像加速
    
    注：如果受公网限制，可能在有公网的环境下，把对应的镜像先自行下载下来，再上传到集群用命令行导入到镜像库
    

# 常用命令行

### kubectl命令

### node的标签操作

    
    
    # 查看当前所有node的标签
    kubectl get nodes --show-labels
    

![image.png](https://image.3001.net/images/20221130/1669779693_6386d0ed5c11405239172.png!small)

    
    
    # 查看某个node的标签
    kubectl describe node k3s-master  # k3s-master 节点名
    

![image.png](https://image.3001.net/images/20221130/1669779694_6386d0ee79fbb19a912e4.png!small)

    
    
    # node自定义标签
    kubectl label node k3s-master1 project=k8snew
    node/k3s-master1 labeled
    
    kubectl label node k3s-master1 node=second-node
    node/k3s-master1 labeled
    
    
    
    # yaml引用node的label示范
    # vim haproxyDep.yaml 
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      namespace: k8s-new
      name: haproxy-deployment
      labels:
        app: haproxy
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: haproxy
      template:
        metadata:
          labels:
            app: haproxy
        spec:
          containers:
          - name: haproxy
            image: k8s.org/haproxy-2.5.0:v1
            imagePullPolicy: IfNotPresent
            resources:
              requests:
                cpu: 200m
                memory: 200Mi
            ports:
            - containerPort: 9999
              protocol: TCP
              name: status
            - containerPort: 9527
              protocol: TCP
              name: haproxy01
          nodeSelector:         #注意必须配置在containers参数结束后的部分
            node: first-node    #之前配置的192.168.1.96节点的label
    
    
    
    # 自定义node label的删除
    kubectl label nodes k3s-master1 project-    
    注：命令格式即：kubectl  label  nodes  node节点名称/nodeIP  node对应的key-    

### ctr 命令使用

containerd 相比于docker , 多了namespace概念, 每个image和container 都会在各自的namespace下可见

    
    
    # 查询ctr版本
    ctr version
    
    
    
    # 查看ctr image可用操作
    ctr image list
    ctr i list
    ctr i ls
    
    
    
    # 镜像标记tag
    ctr -n k8s.io i tag registry.cn-hangzhou.aliyuncs.com/google_containers/pause:3.2 k8s.gcr.io/pause:3.2
    
    # 若新镜像reference 已存在, 需要先删除新reference, 或者如下方式强制替换
    ctr -n k8s.io i tag --force registry.cn-hangzhou.aliyuncs.com/google_containers/pause:3.2 k8s.gcr.io/pause:3.2
    
    
    
    # 删除镜像
    ctr -n k8s.io i rm k8s.gcr.io/pause:3.2
    
    
    
    # 拉取镜像
    ctr -n k8s.io i pull -k k8s.gcr.io/pause:3.2
    
    
    
    # 推送镜像
    ctr -n k8s.io i push -k k8s.gcr.io/pause:3.2
    
    
    
    # 导出镜像
    ctr -n k8s.io i export pause.tar k8s.gcr.io/pause:3.2
    
    
    
    # 导入镜像
    # 不支持 build,commit 镜像
    ctr -n k8s.io i import pause.tar
    
    
    
    # 查看容器相关操作
    ctr c
    
    
    
    # 运行容器
    –null-io: 将容器内标准输出重定向到/dev/null
    –net-host: 主机网络
    -d: 当task执行后就进行下一步shell命令,如没有选项,则会等待用户输入,并定向到容器内
    –mount 挂载本地目录或文件到容器
    –env 环境变量
    ctr -n k8s.io run --null-io --net-host -d \
    –env PASSWORD="123456"
    –mount type=bind,src=/etc,dst=/host-etc,options=rbind:rw
    
    
    
    # 容器日志
    注意: 容器默认使用fifo创建日志文件, 如果不读取日志文件,会因为fifo容量导致业务运行阻塞
    
    如要创建日志文件,建议如下方式创建:
    ctr -n k8s.io run --log-uri file:///var/log/xx.log
    

ctr，crictl，docker命令对比

Ctr命令| Crictl命令| Docker命令| 详细描述  
---|---|---|---  
ctr task ls| crictl ps -a| docker ps| 查看运行中的容器  
ctr image ls| crictl images| docker images| 获取image列表信息  
ctr image pull zookeeper| crictl pull zookeeper| docker pull zookeeper| 拉取镜像  
ctr image push zookeeper|  
| docker push zookeeper| 推送镜像  
ctr image rmi| crictl rmi| docker rmi| 删除镜像  
ctr image export zookeeper.tar
[docker.io/bitnami/zookeeper:3.4.14](http://docker.io/bitnami/zookeeper:3.4.14)|  
| docker save -o zookeeper.tar
[docker.io/bitnami/zookeeper:3.4.14](http://docker.io/bitnami/zookeeper:3.4.14)|
导出镜像  
ctr image import zookeeper.tar|  
| docker load -i zookeeper.tar| 导入本地镜像  
ctr run -d zookeeper zookeeper|  
| docker run -d --name=kafka zookeeper| 运行容器  
ctr image tag zookeeper-new-tag zookeeper|  
| docker tag zookeeper-new-tag zookeeper| 镜像打tag  
  
### crictl 命令使用

    
    
    # 进入容器：
    命令：crictl exec -it CONTAINER-ID bash
    例如：crictl exec -it f57ba7a2d9df4 bash
    
    
    
    # 查询容器：
    命令：crictl ps -a
    
    
    
    # 查询日志：
    命令：crictl logs -f CONTAINER-ID
    例如：crictl logs -f f57ba7a2d9df4
    

### 配置containerd镜像加速

    
    
    # 拷贝配置文件，原文件不要删除
    cp /var/lib/rancher/k3s/agent/etc/containerd/config.toml /var/lib/rancher/k3s/agent/etc/containerd/config.toml.tmpl
    
    
    
    # 修改配置文件
    vim /var/lib/rancher/k3s/agent/etc/containerd/config.toml.tmpl 在最后增加以下配置
    
    [plugins.cri.registry]
      [plugins.cri.registry.mirrors]
        [plugins.cri.registry.mirrors."docker.io"]
          endpoint = ["https://mirror地址"]
        [plugins.cri.registry.mirrors."gcr.io"]
          endpoint = ["https://mirror地址"]
        [plugins.cri.registry.mirrors."k8s.gcr.io"]
          endpoint = ["https://mirror地址"]
        [plugins.cri.registry.mirrors."quay.io"]
          endpoint = ["https://mirror地址"]
    
    
    
    # 重启k3s使配置生效
    systemctl restart k3s
    
    
    
    #检查配置是否生效
    crictl info|grep  -A 30 registry
    

其他命令：

    
    
    crictl images list 列出镜像
    crictl ps 查看运行中的容器
    

## 几种Containerd常用命令对比

    
    
    # 查看容器运行状态
    
    # 1.ctr
    ctr container ls
    #指定命名空间
    ctr --namespace=k8s.io container ls
    
    # 2.crictl
    crictl ps
    
    # 3.nerdctl
    nerdctl ps
    
    
    
    # 查看镜像
    
    # 1.ctr
    ctr image ls
    #指定命名空间
    ctr --namespace=k8s.io image ls
    
    # 2.crictl
    crictl image
    
    # 3.nerdctl
    nerdctl image
    
    
    
    # 查看容器日志
    
    # 1.ctr
    没有相关命令
    
    # 2.crictl
    crictl logs
    
    # 3.nerdctl
    nerdctl logs
    
    
    
    # 修改镜像标签
    
    # 1.ctr
    ctr image tag
    
    # 2.crictl
    没有相关命令
    
    # 3.nerdctl
    nerdctl tag
    
    
    
    # 导出镜像
    
    # 1.ctr
    ctr image export
    
    # 2. crictl
    没有相关命令
    
    # 3.nerdctl
    nerdctl save
    
    
    
    # 导入镜像
    
    # 1.ctl
    ctr image import
    
    # 2.crictl
    没有相关命令
    
    # 3.nerdctl
    nerdctl load
    
    
    
    7.删除镜像
    
    # 1.ctr
    ctr image rm
    
    # 2.crictl
    crictl rmi
    
    #3. nerdctl
    nerdctl rmi
    
    
    
    8.拉取镜像
    
    # 1.ctr
    ctr image pull
    
    # 2.crictl
    crictl pull
    
    # 3.nerdctl
    nerdctl pull
    
    
    
    9.推送镜像
    
    # 1.ctr
    ctr image push
    
    # 2.crictl
    没有相关命令
    
    # 3.nerdctl
    nerdctl push
    

