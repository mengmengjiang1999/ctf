# 容器安全建设最佳实践系列-使用Kubernetes Audit日志发现集群风险与入侵

阅读量 **174684**

发布时间 : 2022-07-13 17:30:57

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t011ce7eddd975f884a.jpg)

## 阅读说明

本文适用于企业容器安全建设参考，篇幅较长可先浏览目录，跳转到关注的部分进行阅读。

## 背景

随着Kubernetes的广泛应用，生产效率提升的同时也逐渐暴露出了一些典型风险面，例如

### Kubernetes及第三方应用漏洞利用

集群化部署在提高效率的同时也带来了新的攻击面。Kubernetes以及第三方应用不断出现新的漏洞，比如使用较广的Nginx
Ingress、Helm等就曾出现过敏感信息泄露、权限提升等类型漏洞。在补丁修复完成前的窗口期，该如何及时发现漏洞利用行为呢？

### 高风险配置资源成为突破口

特权容器、挂载节点目录等场景增加了容器逃逸风险、信息泄露风险等。尽管很多合规配置检查都明确指出了这些风险，但实际总会因为历史包袱、特殊场景需求，导致业务环境中仍然存在这类资源。在业务优先的背景下，短时间下线所有风险配置业务较为困难，在业务改造窗口期，如何感知此类风险呢？

### 局部资源被控持续扩大失陷范围

随着混合云、多集群管控等形态趋势变化，攻击路径也更加复杂多样。对外提供服务的应用容器、配置不当的节点机、有集群凭证的办公网用户被钓鱼都可能是突破口。凭证泄露在攻击中屡试不爽，一个配置不当的普通账户往往会成为获得权限提升的突破口，如何及时发现横向移动中的蛛丝马迹及时止损呢？

Kubernetes
Auditing拥有独特的视角，帮助我们看清集群层面的风险操作。阿里云云安全中心（以下简称云安全中心）容器安全从2020年开始支持Kubernets
Audit日志入侵检测，经过两年的优化和攻击数据积累沉淀了一套丰富的检测模型，本文分享一些建设经验，抛砖引玉。

## 集群之眼-Kubernetes Auditing

Kubernetes提供了一种持续监控集群活动的可视化能力-审计(Auditing _）_ ，能够记录kube-apiserver的交互响应，支持写入日志、自定义webhook等处理方式。

本文重点介绍如何利用Kubernetes Audit日志检测集群风险以及攻击行为，对webhook的方式不作展开。

## 云上Kubernetes集群告警现状

云安全中心支持接入Kubernetes
Audit日志检测集群风险以及攻击行为，下图为不同安全事件类型两年内的告警事件量分布，其中”容器目录挂载配置不当”、”容器启动权限配置不当”事件量远超其他类型(这两类因达到图表高度上限，不代表真实比例)。

![](https://p1.ssl.qhimg.com/t01bc84537fbc71c53b.png)

Kubernetes日志可以帮助我们发现多种安全事件，下面我们来认识这份日志并了解如何使用它。

## 五分钟看懂Kubernetes Audit日志

### 采集原理

Audit日志记录了kube-apiserver各种交互活动，kube-apiserver 可以看做集群的核心管控中心，提供了管理集群的REST API
接口，支持认证、鉴权、集群资源控制、集群状态变更等功能，并将 API 操作对象持久化存储到
etcd。以使用kubectl创建pod为例，主要流程可分为以下几步：

  1. kubectl向kube-apiserver发送创建pod的http post请求
  2. kube-apiserver收到请求，进行认证、鉴权等操作
  3. 鉴权通过后，请求被kube-apiserver路由到对应的api handler进行处理，并将配置参数持久化到etcd中
  4. kubelet根据配置参数在节点上创建pod

Auditing可以在第2步或第3步进行日志记录，目前支持指定以下四个阶段：

  1. RequestReceived：审计处理器接收到请求后，转给其他handler之前
  2. ResponseStarted：响应消息的头部发送后到响应消息体发送前这段时间内。通常为持续一段时间的操作如watch
  3. ResponseComplete：响应消息构建完成时
  4. Panic：发生错误时

如下图所示

![](https://p1.ssl.qhimg.com/t01863c08ad151f2c14.png)

日志详细程度通过指定审计级别（Level）来实现，常见审计级别有四种：

  1. None：不记录审计日志
  2. Metadata：记录请求的元数据，例如请求的user/method/时间/资源类型等，但不包括请求和响应具体内容
  3. Request：记录包括Metadata和请求，但不包括响应
  4. RequestResponse：记录包括Metadata、请求、响应

下面是一个简单的Audit日志采集策略样例，目的是详细记录集群内所有pod资源操作。

apiVersion: audit.k8s.io/v1beta1

kind: Policy

omitStages:

– “RequestReceived”

rules:

– level: RequestResponse

resources:

– group: “”

resources: [“pods”]

在实际业务场景下，通常需要更全面的采集策略，这里提供阿里云容器服务的示例作为参考<https://help.aliyun.com/document_detail/91406.html>。关于如何将数据上报到日志存储中心有很多公开方案，此处不作展开。

### 日志解读

下图是创建pod产生的一条json格式的Audit日志

![](https://p2.ssl.qhimg.com/t012ec1b453739eee5d.png)

这里根据实际使用经验，提供字段说明参考：

字段 | 类型 | 说明  
---|---|---  
apiVersion | string | Kubernetes对象api版本，比如ingress
nginx从Kubernetes1.22版本开始只支持networking.k8s.io/v1，此前版本可使用networking.k8s.io/v1beta1。在检测一些特殊对象时需要考虑api多版本问题  
kind | string | 请求类型，大多数场景固定为”Event”  
level | Level，基础类型string |
审计级别，代表日志完整度，为None值时不记录任何日志，为RequestResponse时记录最完整，参考前文介绍的四个程度None、Metadata、Request、RequestResponse  
auditID | UID，基础类型string | 请求唯一标识，可以作为告警等场景的唯一键，具体使用github.com/google/uuid生成  
stage | Stage，基础类型string |
日志记录阶段，比如前文介绍的四个阶段ResponseComplete、RequestReceived、ResponseStarted、Panic  
requestURI | string | 客户端向kube-apiserver发送的请求URI，可以获取到API Handler信息  
verb | string | 请求Kubernetes资源时，为特定动词如create，patch。 |
非资源请求时为小写的http方法，如get，post  
user | UserInfo | 用户信息，包含了username、uid、groups等  
impersonatedUser | UserInfo | 如果请求扮演了另一个用户，则为被扮演用户的信息  
sourceIPs | 切片 | 请求发起者IP以及中间经过的代理IP  
userAgent | string | 客户端代理信息  
objectRef | ObjectReference结构体 |
请求的目标对象的引用，比如操作ServicAccount时，该字段包含了ServicAccount所属命名空间、名称等信息。在list操作、非资源请求等情况下可能为空  
responseStatus | Status结构体 | 返回的HTTP状态码及错误消息。Success状态下只返回状态码。Failure时包含报错信息  
requestObject | Unknown类型结构体 |
请求对象的详细信息，json格式，当审计级别为Request或RequestResponse出现。对于非资源请求可能为空。 |
如果集群注册了修改原始请求的功能(version
conversion/defaulting/admission/merging)，此时requestObject记录的仍是原始请求，比如使用mutiating
webhook修改请求内容。  
responseObject | Unknown类型结构体 | 请求的响应，json格式，当审计级别为Response时出现  
requestReceivedTimestamp | MicroTime | 请求到达kube-apiserver的时间  
stageTimestamp | MicroTime | 请求到达当前审计阶段的时间  
annotations | map[string]string |
注解，无固定格式的映射。通常可以从这个字段观察到请求处理链路经过了哪些模块处理、决策结果等，比如身份认证、鉴权以及准入控制等。  
  
### 重点字段

Audit日志字段众多，在处理其产生的安全告警时该重点关注哪些字段呢？

  1. sourceIPS：该字段记录了请求发起者的IP以及中间经过的代理IP，起点为外网IP时可能指向攻击源头，起点为内网IP可能指向内部失陷的源头。可重点进行排查溯源。
  2. user：请求发起者的身份，关注身份不符合历史基线的行为，例如某普通应用的ServiceAccount突然被用于进入其他容器中执行命令、枚举读取secrets时，则有可能是应用的默认账户被用于权限提升、横向移动的导致。
  3. 操作资源：重点关注请求操作什么资源(objectRef)，以及动作(verb)，快速筛选出一些敏感的行为
  4. userAgent：客户端代理，用于辅助分析请求产生的来源，比如容器内通过curl发起的恶意请求，失陷dashboard发起的请求。下图展示了云上Kubernets集群请求的来源UserAgent按一周请求量排序的情况。可以看到来源于curl的请求量非常小

![](https://p5.ssl.qhimg.com/t0156aa014bbebcb774.png)

## 检测集群风险及攻击行为

在提升生产效率的同时，Kubernetes也引入了新的攻击面，贯穿容器内、主机节点、集群层面、镜像仓库等。Audit日志拥有独特的视角，帮助我们看清集群层面的操作行为。下面介绍一些攻防阶段中利用Audit日志发现风险和攻击行为的思路。

### 横向移动

横向移动这个词常在内网渗透中出现，在Kubernetes的场景下，由多集群、多节点、多应用组成的复杂环境就是一个大内网。以失陷容器或节点为跳板，收集集群信息，进一步提升权限和可控范围，最终实现控制单集群甚至多集群。下面介绍几种典型场景。

**凭据泄露**

一种较为常见的入侵场景是，攻击者通过web等外部可访问的服务入侵到容器内部后，首先摸清容器挂载的ServiceAccount具有哪些权限以进行权限提升或横向移动。例如下图中，尝试获取当前ServiceAccount权限信息

kubectl auth can-i –list

![](https://p0.ssl.qhimg.com/t01c0439982497e55bc.png)

在没有kubectl的情况下，也可能会用curl等方式直接访问SelfSubjectRulesReview获取权限细节

curl -XPOST -H “Content-Type: application/json” –header “Authorization: Bearer
$TOKEN” –insecure
hxxps://x.x.x.x:443/apis/authorization.k8s.io/v1/selfsubjectrulesreviews -d
‘{“apiVersion”:”authorization.k8s.io/v1″,”kind”:”SelfSubjectRulesReview”,”spec”:{“namespace”:”default”}}’

![](https://p0.ssl.qhimg.com/t01869d81d1c2b891a3.png)

经过上面的初步试探，发现只有读取pods、secrets、configmap等资源的权限，无修改以及进入容器执行命令等权限，于是列举并读取secrets，看是否有突破点

![](https://p4.ssl.qhimg.com/t01a442d26a817cf009.png)

使用读取到的ServiceAccount的token，再次查看权限，发现这个新身份的权限很高，实现权限提升。

![](https://p1.ssl.qhimg.com/t01167bff6e90888a3f.png)

在真实业务场景中，特别是在一些规模较大且复杂的集群中，经常会出现账号权限配置不当的情况。除了配置检查，检测异常列举、读取、使用secrets等行为很重要。但日常运维中可能会出现类似行为，大量异常审计容易形成疲劳。

一种比较通用的解决方法是，重点关注一些可疑度更高的场景或者根据自身的业务环境，根据镜像/应用/命名空间等维度，结合UserAgent、sourceIPs、访问对象等信息，建立历史访问基线，关注基线外的行为。

下图为使用curl访问API SelfSubjectRulesReview获取当前账户权限信息时，产生的Audit日志

![](https://p5.ssl.qhimg.com/t01d4a91c912cfa33e1.png)

**信息泄露漏洞**

以为集群内服务提供外部访问能力的应用nginx-ingress为例，CVE-2021-25742是一个nginx-ingress的高危漏洞，当开启了Snippets特性且攻击者拥有创建或修改ingress实例的权限时，可以在 server
指令域注入lua代码读取secrets，造成多租户场景下的越权访问和集群维度的敏感信息泄露。如下图，漏洞环境下访问构造的路径读取读取Kubernetes的CA

![](https://p1.ssl.qhimg.com/t0159c635a7d628b2ec.png)

我们可以从Audit日志中观察到requestObject.metadata.annotations中有关于server-snippet的设置，含有读取nginx ingress容器敏感信息的指令

![](https://p4.ssl.qhimg.com/t014ecd2e56857fb016.png)

另外还有两个原理较为类似的漏洞CVE-2021-25745、CVE-2021-25746，可重点关注spec.rules[].http.paths[].path以及metadata.annotations的异常代码。

可以预见的是这类风险会再次出现，虽然触发的位置和方式不同，但利用方式是相通的。因此可以通过检测常见的恶意命令，未雨绸缪。

**移动到容器**

进入容器执行命令是一种攻击者常用的方式，常出现在横向移动寻找更高权限、反弹SHELL等场景。

例如下图是一个真实的入侵案例发起的请求，攻击者进入容器并尝试下载启动一个恶意脚本。对于这类场景，可以利用Audit日志覆盖常见的恶意命令如反弹shell、下载程序并执行类操作等等。

![](https://p0.ssl.qhimg.com/t018e51bee16bb694ca.png)

下面是云安全中心在某真实入侵事件中利用Audit日志检测恶意命令执行的告警

![](https://p1.ssl.qhimg.com/t013821ceff2bd4ba68.png)

另外值得注意的是，Audit日志无法记录建立exec通道之后的交互命令。原理参考以下exec命令通道建立的流程图，对于此类行为，基于容器内的命令采集更为重要，这涉及到运行时安全检测和防御，此处不作展开。

![](https://p4.ssl.qhimg.com/t0152b3e6e0acf0ca62.png)

**中间人攻击**

CVE-2020-8554是一个中间人攻击(Man-in-the-MiddleAttack，简称“MITM攻击”)中危漏洞，在一个多租集群中，攻击者可以通过创建和更新Service实例的LoadBalancer、External
IPs等字段来劫持集群中其他pod的流量。例如流传较广的一个案例是将集群的DNS流量劫持到攻击者控制的DNS服务中

apiVersion: v1

kind: Service

metadata:

name: mitm-example

spec:

selector:

app: evil-dns-server

ports:

– protocol: UDP

name: dns

port: 53

targetPort: 53

externalIPs:

– 8.8.8.8

可以重点关注Service服务创建、更新时externalIPs等参数的变动情况，比如服务的externalIPs指向业务不相关的公网IP段、已知域8.8.8.8、本地127.0.0.1来劫持节点流量等等。上面的yaml执行时将产生的Audit日志如下

![](https://p1.ssl.qhimg.com/t0113c0b0872b4ca55e.png)

### 权限提升

权限提升是Kubernetes攻防中的重要环节，不合理的配置是引入风险的主要原因之一。下面主要介绍使用Audit日志检测高风险资源的思路。

**高风险配置**

特权容器、可写模式挂载host节点系统目录等使用方式埋下了容器逃逸、信息泄露等隐患。

我们可以通过Audit日志动态捕获具有风险配置的资源创建，重点关注如Pod/ReplicaSet/ReplicationController/Deployment/StatefulSet/DaemonSet/Job/CronJob的创建和更新。

以创建一个具有SYS_ADMIN权限、挂载节点/etc目录的pod为例，它的Audit日志表现如下

![](https://p0.ssl.qhimg.com/t01c8ab478a66d4b8f9.png)

通过获取容器capabilities，容器挂载节点目录等信息，对危险的capability、具有读写节点敏感目录权限的资源创建行为进行告警。

阿里云安全中心默认支持检测高风险配置资源启动，包括挂载节点目录、权限配置不当等等。

![](https://p2.ssl.qhimg.com/t01973188526531f982.png)

**高权限用户**

Kubernetes集群的用户大致可以分为两种：使用者是人的User、使用者是应用程序的ServiceAccount。

其中使用非常广泛、权限又比较高的组件的ServiceAccount往往是重点利用对象，如Helm、Cilium、Nginx
Ingress、Prometheus等等。一些可重点关注的行为如：

  1. 绑定管理员权限
  2. 为ServiceAccount赋予了高权限，如创建容器、进入容器执行命令、枚举和读取secrets等权限

比如Helm 2这个版本曾出现过可借助Tiller的高权限为账户赋予cluster admin权限的问题

![](https://p0.ssl.qhimg.com/t01b060a802deb4de8f.png)

可以通过Audit日志对高权限绑定行为进行检测，相对于大多数安全场景，通常管理员级别的绑定事件数量并没有那么多，是可以人工运营的。ClusterRoleBinding的Audit日志表现如下

![](https://p0.ssl.qhimg.com/t01452c00ed4cdcc254.png)

### 持久化

持久化的方式很多，这里重点介绍一下静态pod场景。

我们知道静态pod是一种仅存在于特定节点、不漂移、无法通过kube-apiserver进行管理的特殊pod。因此静态pod具有一定隐蔽性、持久化特性。在一些渗透场景如拥有节点特定目录写权限时，可以通过创建静态pod来运行攻击者指定的镜像。创建静态pod只需要指定一个本地或者远端的yaml文件即可。kubelet进程会定期扫描目录进行资源创建和销毁。

一个比较常见的疑问是，Audit日志是否能观测到静态pod的创建呢？

kubelet在创建静态Pod时，会为其创建一个mirror pod并上报给kube-apiserver，因此kube-apiserver可以观测到静态pod。但由于mirror
pod是一个虚假的资源，对其进行操作实际上不会影响静态pod。我们可以从Audit日志中观测到静态Pod的信息，创建静态pod时，请求中的annotations带有kubernetes.io/config.mirror特征，下面是一个静态pod的创建请求样例

![](https://p1.ssl.qhimg.com/t0127f3e3239875be43.png)

相对普通pod而言，静态pod的创建量级会小很多，一般都是为特定业务，因此从排白的角度看是比较有规律的。最常见的静态pod比如kube-apiserver等，参考/etc/kubernetes/manifests/目录下的配置

在早期的Kubernetes版本如1.6中，可能会出现静态pod已经在正常运行，但mirror
pod创建失败导致静态pod不可见的报错场景，这也提供了一种绕过mirror pod达到更加隐蔽状态的思路。

### 蠕虫挖矿

在集群中启动恶意pod，是一种常见的占用资源、维持权限的方式。一些互联网传播的蠕虫入侵集群后，选择启动挖矿容器进行牟利。另一种常见的场景是是从dockerhub下载攻击工具镜像启动容器，使用容器内的黑客工具对集群或内网其他资源持续进行攻击。很多镜像单从镜像仓库地址、启动命令参数就可以判断为具有危害的镜像，比如挖矿、流行的攻击工具套件。虽然这种匹配已知特征的方式简单粗暴，容易绕过，但在很多场景下效果不错。

以创建挖矿pod为例，可以从requestObject获得容器启动使用的镜像、启动参数进行恶意特征匹配，参考下面的日志表现

![](https://p3.ssl.qhimg.com/t01f72934f97e75319d.png)

### 异常访问

对于有公网连接端点的集群，每天可能会接受来自公网的大量访问，一个比较极端的场景是，给匿名用户赋予了集群管理员的权限，一旦集群存在可通过公网访问入口，就等同于直接获取到整个集群的控制权限。如下面这个为匿名用户绑定cluster
admin之后，匿名用户可从外网访问并管理集群的案例

kind: ClusterRoleBinding

apiVersion: rbac.authorization.k8s.io/v1beta1

metadata:

name: binding-test

namespace: kube-system

subjects:

– kind: User

name: system:anonymous

apiGroup: “rbac.authorization.k8s.io”

roleRef:

kind: ClusterRole

name: cluster-admin

apiGroup: “rbac.authorization.k8s.io”

下面是匿名用户发起请求时的Audit日志表现

![](https://p4.ssl.qhimg.com/t01ccbb7b92169a073f.png)

对于这个场景，可以关注来自公网IP的匿名用户高权限行为，或者用前文提到的高权限账户配置行为。这种情况在早期生产和测试集群环境居多，现在已经逐渐收敛。

对于暴露在公网的集群，通常情况下运维人员会设置安全组缩小来源IP范围来提升安全性。但攻击渠道总是复杂多样的，例如处在信任IP段、保存了集群管理凭证的办公网机器失陷。这种场景的检测难点在于同正常运维行为高度相似。相比检测，更多的被应用于入侵之后的溯源，串联起整条攻击路径、快速止血。

## 以子之矛，攻子之盾

在使用日志的同时，我们需要重视日志组件本身的安全性，及时修复相关漏洞。Kubernetes历史上曾出现过日志泄露敏感信息的问题(CVE-2020-8564/CVE-2020-8565/CVE-2020-8566)。CVE-2020-8564是一个kubelet组件漏洞，在漏洞版本的环境下，日志级别≥4且触发私有镜像仓库配置解析报错时，docker
config凭证通过报错信息写入了日志，如下图漏洞环境下，因仓库解析报错从日志中读到了的仓库凭证信息

![](https://p4.ssl.qhimg.com/t017044f6695c19cf93.png)

## 总结

随着业务部署管理逐渐向容器集群的形态演进，攻防对抗也随之改变并产生了复杂攻击路径与组合技。安全贯穿端点、集群、供应链等等。仅保护其中一个面是远远不够的。Kubernetes
Auditing拥有独特的视角，帮助我们看清集群层面风险操作。

云安全中心容器安全产品默认支持Kubernetes Audit日志入侵检测，经过两年的Kubernetes
Audit攻击数据积累沉淀了一套丰富的检测模型，配合镜像扫描、集群主动防御、运行时入侵检测和防御、网络微隔离等功能构建基于容器全生命周期的安全防护体系，保障云原生安全。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **阿里云安全** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/276426](/post/id/276426)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [容器](/tag/容器)
  * [企业安全建设](/tag/企业安全建设)

 **+1** __6赞

 __收藏

![](https://p1.ssl.qhimg.com/t01d437704d9b31097b.png) 阿里云安全

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

