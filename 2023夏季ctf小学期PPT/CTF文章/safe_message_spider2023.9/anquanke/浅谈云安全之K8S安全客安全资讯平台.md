# 浅谈云安全之K8S

阅读量 **281272**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-07-14 12:00:20

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01908f01cc1b7e7367.png)

## k8s是什么?

Kubernetes
是一个可移植的，可扩展的开源容器编排平台，用于管理容器化的工作负载和服务，方便了声明式配置和自动化。它拥有一个庞大且快速增长的生态系统。Kubernetes
的服务，支持和工具广泛可用。

###  为什么现在流行使用容器?

早期: 在物理服务器上面部署应用程序存在资源分配问题,因为其不能在物理服务器中的应用程序定义资源边界,导致应用程序资源利用不足而无法扩展.

后来: 为了解决该问题,引入了虚拟化技术, 虚拟化技术是指允许你在单个物理服务器的 CPU
上运行多个虚拟机,可以让多个应用程序在虚拟机之间进行隔离,具有一定的安全型, 每一个虚拟机就是一台完整的计算机, 在虚拟化硬件之上运行所有组件.

现在: 多数在物理服务器上面部署应用程序都是采kubectl用容器的方式,容器类似于虚拟机,他们都具有自己的文件系统、CPU、内存、进程空间等,
且由于它们与基础架构分离，因此可以跨云和 OS 发行版本进行移植。基于此点被企业大范围使用.

###  为什么需要使用k8s容器?

若出现这样一个环境: 在生产环境中如果一个容器发生故障,则我们需要手动去启动另外一个容器,这样的操作是对我们的管理员来说是不太方便的,
若一个容器出现故障,另一个容器可以自动启动容器接管故障的容器,这样是最好的.

k8s就可以实现该效果,Kubernetes 提供了一个可弹性运行分布式系统的框架。 Kubernetes 会满足你的扩展要求、故障转移、部署模式等。

k8s功能: 服务发现和负载均衡, 存储编排, 自动部署和回滚, 自动完成装箱计算, 自我修复, 密钥与配置管理

## 名词解释

###  secret

Secret有三种类型：

  * Service Account：用来访问Kubernetes API，由Kubernetes自动创建，并且会自动挂载到Pod的`/run/secrets/kubernetes.io/serviceaccount`目录中；
  * Opaque：base64编码格式的Secret，用来存储密码、密钥等；
  * kubernetes.io/dockerconfigjson：用来存储私有docker registry的认证信息。

## k8s的组成

k8s是由组件,API,对象等组成.

包含所有相互关联组件的 Kubernetes 集群图如下:

![](https://p5.ssl.qhimg.com/t015bbe5d19fc096fd2.png)

###  组件

![](https://p3.ssl.qhimg.com/t01b15a6d4ef6661144.png)

  * 控制平面组件 
    * kube-apiserver: 为k8s的api服务器,公开了所有Kubernetes API, 其他所有组件都必须通过它提供的API来操作资源数据. 
      * 保证集群状态访问的安全
      * 隔离集群状态访问的方式和后端存储实现的方式：API Server是状态访问的方式，不会因为后端存储技术etcd的改变而改变。
    * etcd: 为k8s的键值数据库,保存了k8s所有集群数据的后台数据库。
    * kube-scheduler: 收集和分析当前Kubernetes集群中所有Node节点的资源(内存、CPU)负载情况，然后依此分发新建的Pod到Kubernetes集群中可用的节点。 kube-controller-manager: 在主节点上运行 控制器 的组件。
    * cloud-controller-manager: 云控制器管理器是指嵌入特定云的控制逻辑的 控制平面组件
  * Node 组件 
    * kubelet: 一个在集群中每个节点（node）上运行的代理。 它保证容器（containers）都 运行在 Pod 中。
    * kube-proxy: kube-proxy是集群中每个节点上运行的网络代理,维护节点上的网络规则。这些网络规则允许从集群内部或外部的网络会话与 Pod 进行网络通信。
    * 容器运行时: 负责运行容器的软件。
  * 插件(Addons) 
    * DNS: 集群 DNS 是一个 DNS 服务器，和环境中的其他 DNS 服务器一起工作，它为 Kubernetes 服务提供 DNS 记录。
    * Web 界面（仪表盘）: Dashboard 是Kubernetes 集群的通用的、基于 Web 的用户界面。
    * 容器资源监控: 容器资源监控 将关于容器的一些常见的时间序列度量值保存到一个集中的数据库中，并提供用于浏览这些数据的界面。
    * 集群层面日志: 集群层面日志 机制负责将容器的日志数据 保存到一个集中的日志存储中，该存储能够提供搜索和浏览接口。

###  API

Kubernetes 控制面 的核心是 API 服务器。 API 服务器负责提供 HTTP API，以供用户、集群中的不同部分和集群外部组件相互通信。

###  对象

Kubernetes对象是Kubernetes系统中的持久实体。Kubernetes使用这些实体来表示集群的状态.

具体来说，他们可以描述：

  * 容器化应用正在运行(以及在哪些节点上)
  * 这些应用可用的资源
  * 关于这些应用如何运行的策略，如重新策略，升级和容错

## Kubernetes 架构

![](https://p2.ssl.qhimg.com/t01e95d27f581f5dcd1.png)

Kubernetes 架构由节点,控制面到节点通信, 控制器, 云控制器管理器组成.

###  master 流程图

![](https://p2.ssl.qhimg.com/t01a4f08383d6597cd9.png)

  * Kubecfg将特定的请求，比如创建Pod，发送给Kubernetes Client。
  * Kubernetes Client将请求发送给API server。
  * API Server根据请求的类型，比如创建Pod时storage类型是pods，然后依此选择何种REST Storage API对请求作出处理。
  * REST Storage API对的请求作相应的处理。
  * 将处理的结果存入高可用键值存储系统Etcd中。
  * 在API Server响应Kubecfg的请求后，Scheduler会根据Kubernetes Client获取集群中运行Pod及Minion/Node信息。
  * 依据从Kubernetes Client获取的信息，Scheduler将未分发的Pod分发到可用的Minion/Node节点上。

###  节点

节点可以是一个虚拟机或者物理机器，取决于所在的集群配置。 每个节点包含运行 Pods 所需的服务， 这些 Pods 由 控制面 负责管理.

节点上的组件包括 kubelet、 容器运行时以及 kube-proxy。

**节点状态**

可以使用 kubectl 来查看节点状态和其他细节信息：

    
    
    kubectl describe node <节点名称>
    

一个节点包含以下信息:

  * 地址 
    * HostName：由节点的内核设置。可以通过 kubelet 的 —hostname-override 参数覆盖。
    * ExternalIP：通常是节点的可外部路由（从集群外可访问）的 IP 地址。
    * InternalIP：通常是节点的仅可在集群内部路由的 IP 地址。
  * 状况(conditions 字段描述了所有 Running 节点的状态) 
    * Ready 如节点是健康的并已经准备好接收 Pod 则为 True；False 表示节点不健康而且不能接收 Pod；Unknown 表示节点控制器在最近 node-monitor-grace-period 期间（默认 40 秒）没有收到节点的消息
    * DiskPressure为True则表示节点的空闲空间不足以用于添加新 Pod, 否则为 False
    * MemoryPressure为True则表示节点存在内存压力，即节点内存可用量低，否则为 False
    * PIDPressure为True则表示节点存在进程压力，即节点上进程过多；否则为 False
    * NetworkUnavailable为True则表示节点网络配置不正确；否则为 False
  * 容量与可分配 
    * 描述节点上的可用资源：CPU、内存和可以调度到节点上的 Pod 的个数上限。
  * 信息 
    * 关于节点的一般性信息，例如内核版本、Kubernetes 版本（kubelet 和 kube-proxy 版本）、 Docker 版本（如果使用了）和操作系统名称。这些信息由 kubelet 从节点上搜集而来。

###  控制面到节点通信

  * 节点到控制面 
    * apiserver在安全的 HTTPS 端口（443）上监听远程连接请求
    * 以客户端证书的形式将客户端凭据提供给 kubelet
  * 控制面到节点 
    * API 服务器到 kubelet连接用于 
      * 获取 Pod 日志
      * 挂接（通过 kubectl）到运行中的 Pod
      * 提供 kubelet 的端口转发功能。
      * (注: 在连接状态下, 默认apiserver 不检查 kubelet 的服务证书。容易受到中间人攻击，不安全.)
    * apiserver 到节点、Pod 和服务 
      * SSH 隧道(目前已经废弃) 
        * 产生原因: 若无服务证书, 又要求避免在非受信网络或公共网络上进行连接,则可以在apiserver 和 kubelet 之间使用ssh隧道.
        * Kubernetes 支持使用 SSH 隧道来保护从控制面到节点的通信路径。
      * Konnectivity 服务 
        * 为ssh隧道的替代品, Konnectivity 服务提供 TCP 层的代理，以便支持从控制面到集群的通信。

###  控制器

在 Kubernetes 中，控制器通过监控集群 的公共状态，并致力于将当前状态转变为期望的状态。

举个例子: 当前室内温度为20度, 我们通过调节遥控器,使其温度上升至24度, 这20度到24度的变化即为让其从当前状态接近期望状态。

控制器模式分为直接控制和通过API服务器来控制.

###  云控制器管理器

云控制器管理器是指嵌入特定云的控制逻辑的 控制平面组件。 云控制器管理器允许您链接聚合到云提供商的应用编程接口中，
并分离出相互作用的组件与您的集群交互的组件。

云控制器管理器中的控制器包括：

  * 节点控制器 
    * 节点控制器负责在云基础设施中创建了新服务器时为之 创建 节点（Node）对象。 节点控制器从云提供商获取当前租户中主机的信息。
    * 执行功能: 
      * 针对控制器通过云平台驱动的 API 所发现的每个服务器初始化一个 Node 对象
      * 利用特定云平台的信息为 Node 对象添加注解和标签
      * 获取节点的网络地址和主机名
      * 检查节点的健康状况。
  * 路由控制器 
    * Route 控制器负责适当地配置云平台中的路由，以便 Kubernetes 集群中不同节点上的 容器之间可以相互通信。
  * 服务控制器 
    * 服务（Service）与受控的负载均衡器、 IP 地址、网络包过滤、目标健康检查等云基础设施组件集成。 服务控制器与云驱动的 API 交互，以配置负载均衡器和其他基础设施组件。

## Kubernetes 安全性

###  云原生安全

云原生安全4个C: 云(Cloud)、集群(Cluster)、容器(Container)和代码(Code)

![](https://p4.ssl.qhimg.com/t01fb78526c1a1bae8e.png)

云原生安全模型的每一层都是基于下一个最外层，代码层受益于强大的基础安全层（云、集群、容器）。我们无法通过在代码层解决安全问题来为基础层中糟糕的安全标准提供保护。

**基础设施安全**

Kubetnetes 基础架构关注领域 | 建议  
---|---  
通过网络访问 API 服务（控制平面) | 所有对 Kubernetes 控制平面的访问不允许在 Internet
上公开，同时应由网络访问控制列表控制，该列表包含管理集群所需的 IP 地址集。  
通过网络访问 Node（节点) | 节点应配置为 仅能 从控制平面上通过指定端口来接受（通过网络访问控制列表）连接，以及接受 NodePort 和
LoadBalancer 类型的 Kubernetes 服务连接。如果可能的话，这些节点不应完全暴露在公共互联网上。  
Kubernetes 访问云提供商的 API | 每个云提供商都需要向 Kubernetes
控制平面和节点授予不同的权限集。为集群提供云提供商访问权限时，最好遵循对需要管理的资源的最小特权原则。Kops 文档提供有关 IAM 策略和角色的信息。  
访问 etcd | 对 etcd（Kubernetes 的数据存储）的访问应仅限于控制平面。根据配置情况，你应该尝试通过 TLS 来使用
etcd。更多信息可以在 etcd 文档中找到。  
etcd 加密 | 在所有可能的情况下，最好对所有驱动器进行静态数据加密，但是由于 etcd
拥有整个集群的状态（包括机密信息），因此其磁盘更应该进行静态数据加密。  
  
**集群组件安全**

  * 运行的应用程序的安全性关注领域 
    * 访问控制授权(访问 Kubernetes API)
    * 认证方式
    * 应用程序 Secret 管理 (并在 etcd 中对其进行静态数据加密)
    * Pod 安全策略
    * 服务质量（和集群资源管理）
    * 网络策略
    * Kubernetes Ingress 的 TLS 支持

**容器安全**

  * 容器安全性关注领域 
    * 容器搭建配置(配置不当,危险挂载, 特权用户)
    * 容器服务自身缺陷
    * Linux内核漏洞
    * 镜像签名和执行

**代码安全**

  * 代码安全关注领域 
    * 仅通过 TLS 访问(流量加密)
    * 限制通信端口范围
    * 第三方依赖性安全
    * 静态代码分析
    * 动态探测攻击(黑盒)

## Kubernetes架构常见问题

###  Kubernetes ATTACK 矩阵

![](https://p3.ssl.qhimg.com/t012cfc5618e25d855a.png)

###  信息泄漏

**云账号AK泄露**

API凭证（即阿里云AccessKey）是用户访问内部资源最重要的身份凭证。用户调用API时的通信加密和身份认证会使用API凭证.

API凭证是云上用户调用云服务API、访问云上资源的唯一身份凭证。

API凭证相当于登录密码，用于程序方式调用云服务API.

**k8s configfile泄露**

kubeconfig文件所在的位置: `$HOME/.kube/config`

Kubeconfig文件包含有关Kubernetes集群的详细信息，包括它们的位置和凭据。

云厂商会给用户提供该文件,以便于用户可以通过kubectl对集群进行管理.
如果攻击者能够访问到此文件（如办公网员工机器入侵、泄露到Github的代码等），就可以直接通过API Server接管K8s集群，带来风险隐患。

![](https://p4.ssl.qhimg.com/t01cc64f4d734124c26.png)

**Master节点SSH登录泄露**

常见的容器集群管理方式是通过登录Master节点或运维跳板机，然后再通过kubectl命令工具来控制k8s。

云服务器提供了通过ssh登陆的形势进行登陆master节点.

![](https://p3.ssl.qhimg.com/t011fbeaff1f605cd22.png)

若Master节点SSH连接地址泄漏,攻击者可对ssh登陆进行爆破,从而登陆上ssh,控制集群.

###  容器组件未鉴权服务

Kubernetes架构下常见的开放服务指纹如下:

  * kube-apiserver: 6443, 8080
  * kubectl proxy: 8080, 8081
  * kubelet: 10250, 10255, 4149
  * dashboard: 30000
  * docker api: 2375
  * etcd: 2379, 2380
  * kube-controller-manager: 10252
  * kube-proxy: 10256, 31442
  * kube-scheduler: 10251
  * weave: 6781, 6782, 6783
  * kubeflow-dashboard: 8080

注:前六个重点关注: 一旦被控制可以直接获取相应容器、相应节点、集群权限的服务

**了解各个组件被攻击时所造成的影响**

组件分工图:

![](https://p4.ssl.qhimg.com/t01e410cb7ac6db2b2e.png)

假如用户想在集群里面新建一个容器集合单元, 流程如下:

  1. 用户与 kubectl进行交互,提出需求(例: kubectl create -f pod.yaml)
  2. kubectl 会读取 ~/.kube/config 配置，并与 apiserver 进行交互，协议：http/https
  3. apiserver 会协同 ETCD, kube-controller-manager, scheduler 等组件准备下发新建容器的配置给到节点，协议：http/https
  4. apiserver 与 kubelet 进行交互，告知其容器创建的需求，协议：http/https；
  5. kubelet 与Docker等容器引擎进行交互，创建容器，协议：http/unix socket.
  6. 容器已然在集群节点上创建成功

###  攻击apiserver

apiserver介绍:  
在Kubernetes中,对于未鉴权对apiserver, 能访问到 apiserver 一般情况下就能获取了集群的权限.

在攻击者眼中Kubernetes APIServer

  * 容器编排K8S总控组件
  * pods, services, secrets, serviceaccounts, bindings, componentstatuses, configmaps,
  * endpoints, events, limitranges, namespaces, nodes, persistentvolumeclaims,
  * persistentvolumes, podtemplates, replicationcontrollers, resourcequotas …
  * 可控以上所有k8s资源
  * 可获取几乎所有容器的交互式shell
  * 利用一定技巧可获取所有容器母机的交互式shell

默认情况下apiserver都有鉴权:

未鉴权配置如下:

![](https://p0.ssl.qhimg.com/t01706b8fbabe0acd6d.png)

对于这类的未鉴权的设置来说，访问到 apiserver 一般情况下就获取了集群的权限：

![](https://p5.ssl.qhimg.com/t011e28b315f58c19ae.png)

如何通过apiserver来进行渗透,可参考:<https://Kubernetes.io/docs/reference/generated/kubectl/kubectl-commands>

###  攻击kubelet

每一个Node节点都有一个kubelet(每个节点上运行的代理)服务，kubelet监听了10250，10248，10255等端口。

10250端口,是kubelet与apiserver进行通信对主要端口,
通过该端口,kubelet可以知道当前应该处理的任务.该端口在最新版Kubernetes是有鉴权的,
但在开启了接受匿名请求的情况下，不带鉴权信息的请求也可以使用10250提供的能力, 在Kubernetes早期,很多挖矿木马基于该端口进行传播.

在`/var/bin/kubulet/config/yaml`配置文件中,若进行如下配置,则可能存在未授权访问漏洞.

![](https://p2.ssl.qhimg.com/t0178ce3d788441cf68.png)

若10250端口存在未授权访问漏洞,我们可以直接访问/pods进行查看

![](https://p2.ssl.qhimg.com/t01543913efe19a2333.png)

![](https://p3.ssl.qhimg.com/t01864aeb34d67215f7.png)

根据在pods中获取的信息,我们可以在容器中执行命令

    
    
    curl -Gks https://host:10250/exec/{namespace}/{podname}/{containername} \
    -d 'input=1' -d 'output=1' -d 'tty=1' \
    -d 'command=whoami'
    

上述命令得到websocket地址，连接websocket得到命令结果：

![](https://p3.ssl.qhimg.com/t01937cb75914eb5437.png)

使用wscat工具连接websocket

    
    
    wscat -c “https://X.X.X.X:10250/{websocket}” --no-check
    

即可得到我们执行命令的结果.

获取token

    
    
    /var/run/secrets/kubernetes.io/serviceaccount
    

然后即可访问kube-api server,获取集群权限

    
    
    curl -ks -H "Authorization: Bearer <TOKEN>" \
      ttps://master:6443/api/v1/namespaces/{namespace}/secrets
    

攻击kubelet总体步骤如下:

  * 访问pods获取信息
  * 获取namespace、podsname、containername
  * 执行exec获取token
  * /var/run/secrets/kubernetes.io/serviceaccount
  * 利用Token访问API Server进行对pods操作。

###  攻击dashboard

dashboard登陆链接如下: `http://xxx.xxx.xxx.xxx:xxxx/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/login`

dashboard界面如下:

![](https://p2.ssl.qhimg.com/t01da347b24b51c044d.png)

dashboard是Kubernetes官方推出的控制Kubernetes的图形化界面.在Kubernetes配置不当导致dashboard未授权访问漏洞的情况下，通过dashboard我们可以控制整个集群。

默认情况下, dashboard是需要进行鉴权操作的,当用户开启了enable-skip-login时可以在登录界面点击Skip跳过登录进入dashboard.

通过skip登陆的dashboard默认是没有操作集群的权限,因为Kubernetes使用RBAC(Role-based access
control)机制进行身份认证和权限管理，不同的serviceaccount拥有不同的集群权限。

但有些开发者为了方便或者在测试环境中会为Kubernetes-dashboard绑定cluster-admin这个ClusterRole（cluster-admin拥有管理集群的最高权限）.

为Kubernetes-dashboard绑定cluster-admin 设置如下:

  1. 新建dashboard-admin.yaml内容 
    
        apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRoleBinding
    metadata:
     name: kubernetes-dashboard
    roleRef:
     apiGroup: rbac.authorization.k8s.io
     kind: ClusterRole
     name: cluster-admin
    subjects :
     kind: ServiceAccount
     name: kubernetes-dashboard
     namespace: kubernetes-dashboard
    

  2. 执行kubectl create -f dashboard-admin.yaml

后通过skip登陆dashboard便有了管理集群的权限.

创建Pod控制node节点,该pod主要是将宿主机根目录挂载到容器tmp目录下。

新建一个Pod如下:

![](https://p0.ssl.qhimg.com/t019813e939a3aafbda.png)

通过该容器的tmp目录管理node节点的文件

![](https://p2.ssl.qhimg.com/t01efaa4c22a6d84ed3.png)

![](https://p2.ssl.qhimg.com/t014f164118b8a86d64.png)

###  攻击etcd

Kubernetes默认使用了etcd v3来存储数据, 若能na  
etcd对内暴露2379端口，本地127.0.0.1可免认证访问. 其他地址要带—endpoint参数和cert进行认证。

未授权访问流程:

  * 检查是否正常链接`etcdctl endpoint health`
  * 读取service account token `etcdctl get / --prefix --keys-only | grep /secrets/kube-system/clusterrole`
  * 通过token认证访问API-Server端口6443，接管集群：
  * `kubectl --insecure-skip-tls-verify -s https://127.0.0.1:6443/ --token="[ey...]" -n kube-system get pods`

###  攻击docker remote api(Docker daemon公网暴露)

2375是docker远程操控的默认端口，通过这个端口可以直接对远程的docker 守护进程进行操作。Docker 守护进程默认监听2375端口且未鉴权.

当机器以`docker daemon -H=0.0.0.0:2375`方式启动daemon时，可以在外部机器对该机器的docker
daemon进行直接操作：

![](https://p5.ssl.qhimg.com/t01b6c223ccc1faad59.png)

![](https://p2.ssl.qhimg.com/t017d5a013530ac28e0.png)

之后依次执行systemctl daemon-reload、systemctl restart docker

外部主机使用`-H` 即可操作暴露2375端口的主机.

![](https://p4.ssl.qhimg.com/t01f8108e35277c8319.png)

因此当你有访问到目标Docker API 的网络能力或主机能力的时候，你就拥有了控制当前服务器的能力。我们可以利用Docker
API在远程主机上创建一个特权容器，并且挂载主机根目录到容器.

![](https://p1.ssl.qhimg.com/t01eee803e3c5d2a2d1.png)

检测目标是否存在docker
api未授权访问漏洞的方式也很简单，访问http://[host]:[port]/info路径是否含有ContainersRunning、DockerRootDir等关键字。

![](https://p3.ssl.qhimg.com/t01d32393c18a8fee7f.png)

###  攻击kubectl proxy

**二次开发所产生的问题**

管理Kubernetes无论是使用 kubectl 或 Kubernetes dashboard 的UI功能，其实都是间接在和 APIServer 做交互.

如果有需求对k8s进行二次开发的话,大部分的开发功能请求了 APIServer 的 Rest API 从而使功能实现的。

例如:

  * 给用户销毁自己POD的能力 
    * `DELETE https://apiserver:8443/api/v1/namespaces/default/pods/sleep-75c6fd99c-g5kss`

类似于这样去调用apiserver, 攻击者若修改namespace、pod和容器名, 那么即可造成越权.

## 推荐工具

###  Kube-Hunter扫描漏洞

kube-hunter是一款用于寻找Kubernetes集群中的安全漏洞扫描器

下载地址: <https://github.com/aquasecurity/kube-hunter>

###  CDK(强推)

CDK是一款为容器环境定制的渗透测试工具，在已攻陷的容器内部提供零依赖的常用命令及PoC/EXP。集成Docker/K8s场景特有的
逃逸、横向移动、持久化利用方式，插件化管理。

下载地址: <https://github.com/cdk-team/CDK/wiki/CDK-Home-CN>

## 参考链接

<https://developer.aliyun.com/article/765449?groupCode=aliyunsecurity>  
<https://xz.aliyun.com/t/4276#toc-2>  
<https://www.secrss.com/articles/29544>  
<https://kubernetes.io/zh/docs/concepts/workloads/pods/#what-is-a-pod>  
<https://www.huweihuang.com/kubernetes-notes/concepts/architecture/kubernetes-architecture.html>  
<https://www.kubernetes.org.cn/service-account>  
<https://www.aquasec.com/cloud-native-academy/cloud-native-applications/cloud-native-infrastructure/>  
<https://www.cdxy.me/?p=827>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **no0neeeeeee** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/245526](/post/id/245526)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [云安全](/tag/云安全)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t010857340ce46bb672.jpg) no0neeeeeee

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

