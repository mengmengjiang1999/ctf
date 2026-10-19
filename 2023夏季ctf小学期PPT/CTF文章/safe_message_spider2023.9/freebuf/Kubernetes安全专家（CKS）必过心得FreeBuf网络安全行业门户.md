备注：参加 CKS 考试需要​[​经过认证的 Kubernetes 管理员(CKA)
认证。​](https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/)​如果您没有它或它已过期（持续三年），您可以​[​查看​](https://www.lullabot.com/articles/kubernetes-certifications-ckad-and-cka-exam-tips)​CKA考试的相关文章并完成考试。

![](https://image.3001.net/images/20221013/1665652841_6347d869b153434a084ed.png!small)

## 什么是CKS认证考试？

根据 CNFC
的说明，获得CKS证书证明考生具备在构建、部署和运行期间确保基于容器的应用程序和Kubernetes平台安全的技能、知识和能力。CKS考试内容和CKA类似，大部分也都是实操。

获取CKS认证的安全专家能够在就业市场中快速建立自己的信誉和价值，同时也让公司能够更快地聘请高素质的团队来支持他们的发展

## CKS考试大纲

CKS 考试旨在测试您在不同安全方面的技能。下表显示了 CKS 认证的不同领域及其权重。

 **考试内容​**

|

 **占比​**  
  
---|---  
  
集群设置​

|

10%​  
  
集群强化​

|

15%​  
  
系统强化​

|

15%​  
  
最小化微服务漏洞​

|

20%​  
  
供应链安全​

|

20%​  
  
监控、日志记录和运行时安全​

|

20%​  
  
！重要提示：考试中允许使用以下网站，建议多熟悉以下网站的内容结构，方便遇到问题快速查询

​[​https://github.com/aquasecurity/trivy​](https://github.com/aquasecurity/trivy)​  
  
---  
  
​[​https://docs.sysdig.com/​](https://docs.sysdig.com/)​  
  
​[​https://falco.org/docs/​](https://falco.org/docs/)​  
  
​[​https://gitlab.com/apparmor/apparmor/-/wikis/Documentation​](https://gitlab.com/apparmor/apparmor/-/wikis/Documentation)​  
  
## 准备工作：

首先需要一个k8s集群来学习和尝试CKS认证中涉及的所有概念。你可以根据下方建议选取合适方式部署、管理一个K8S环境：​

  1. MiniKube；​
  2. 使用 kubeadm 部署集群；​
  3. 使用免费 Google Cloud Credits 的​[​GKE 集群​](https://devopscube.com/setup-kubernetes-cluster-google-cloud/)​；​
  4. 腾讯云容器服务TKE；​
  5. 阿里云容器服务服务ACK；​
  6. Azure 上使用免费云积分​[​的 AKS 服务​](https://azure.microsoft.com/en-in/services/kubernetes-service/)​；​
  7. AWS 上使用免费套餐计划​[​的 EKS 服务​](https://aws.amazon.com/eks/)​。​

### 别名：

设置别名非常有利于节省我们执行操作的时间并且减少产生错误的可能

  

    
    
    vi ~/.bashrc  
    ---  
    alias k='kubectl'  
    alias kg='k get'  
    alias kd='k describe'  
    alias kl='k logs'  
    alias kc='k create'  
    source <(kubectl completion bash)  
    source <(kubectl completion bash | sed 's/kubectl/k/g' )  
    complete -F __start_kubectl k

\---​  
  
---  
  
### 资源快捷访问方式：

 **资源​**

|

 **简称​**  
  
---|---  
  
pods​

|

po​  
  
replicasets​

|

rs​  
  
deployments​

|

deploy​  
  
services​

|

svc​  
  
namespace​

|

ns​  
  
networkpolicy​

|

netpol​  
  
persistentstorage​

|

pv​  
  
persistentstorageclaim​

|

pvc​  
  
serviceaccounts​

|

sa​  
  
## 练习

### 从现有pod 生成 yaml 规范

  

    
    
    kgpo <pod-name> -o wide  
      
    # 生成 YAML Pod 规范  
    kgpo <pod-name> -o yaml  
    kgpo <pod-name> -o yaml > <pod-name>.yaml  
      
    # 获取不包含集群特定信息的 pod 的 YAML 规范  
    kgpo my-pod -o yaml --export > <pod-name>.yaml  
  
---  
  
### 查看日志并打印

  

    
    
    kubectl logs deploy/<podname>  
    kubectl logs deployment/<podname>  
    #Follow logs  
    kubectl logs deploy/<podname> --tail 1 --follow  
  
---  
  
### 创建

    
    
    kc cm my-cm --from-literal=APP_ENV=dev  
    kc cm my-cm --from-file=test.txt  
    kc cm my-cm --from-env-file=config.env  
      
    kc secret generic my-secret --from-literal=APP_SECRET=sdcdcsdcsdcsdc  
    kc secret generic my-secret --from-file=secret.txt  
    kc secret generic my-secret --from-env-file=secret.env

### 调试工具 busybox

可以使用 busybox 容器在集群内部进行各种系统调试，比如：端口验证、http、htpts验证、网络可达验证、域名解析等

  

    
    
    # 运行busybox 容器  
    k run busybox --image=busybox:1.28 --rm --restart=Never -it sh  
      
    # 进入busybox容器  
    k exec -it busybox -c busybox2 -- /bin/sh  
      
    # 添加资源限制  
    kubectl run nginx --image=nginx --restart=Never --requests='cpu=100m,memory=256Mi' --limits='cpu=200m,memory=512Mi'  
      
    # 给pod创建并绑定service  
    kubectl run nginx --image=nginx --restart=Never --port=80 --expose  
      
    # 端口检验  
    nc -z -v -w 2 <service-name> <port-name>  
    # NSLookup  
    nslookup <service-name>  
    nslookup 10-32-0-10.default.pod  
  
---  
  
### 网络策略：

在 Kubernetes 集群中，默认情况下所有 pod 都可以与所有 pod
通信，这在某些实现中可能是一个安全问题。为了解决这个问题，Kubernetes 引入了网络策略来允许或拒绝基于 pod 标签的流量，这些标签是 pod
规范的一部分。

下面的示例拒绝在所有命名空间中运行的 Pod 的 Ingress 和 Egress 流量。

  

    
    
    apiVersion: networking.k8s.io/v1  
    kind: NetworkPolicy  
    metadata:  
    name: example  
    namespace: default  
    spec:  
    podSelector: {}  
    policyTypes:  
    - Egress  
    - Ingress  
  
---  
  
下面的示例拒绝在所有命名空间中运行的 Pod 的 Ingress 和 Egress 流量。但它允许访问在端口 3306上运行的MySQL解析服务。

  

    
    
    apiVersion: networking.k8s.io/v1  
    kind: NetworkPolicy  
    metadata:  
    name: deny  
    namespace: default  
    spec:  
    podSelector: {}  
    policyTypes:  
    - Egress  
    - Ingress  
    egress:  
    - to:  
    ports:  
    - port: 3306  
    protocol: TCP  
    - port: 3306  
    protocol: UDP  
  
---  
  
拒绝除了 192.168.10.10以外的所有Ingress流量​

  

    
    
    apiVersion: networking.k8s.io/v1  
    kind: Ingress  
    metadata:  
    name:cloud-metadata-deny  
    namespace: default  
    spec:  
    podSelector: {}  
    policyTypes:  
    - Egress  
    egress:  
    - to:  
    - ipBlock:   
    cidr: 0.0.0.0/0  
    except:  
    - 192.168.10.10/32  
  
---  
  
允许Egress访问 192.168.10.10服务器的数据​

  

    
    
    apiVersion: networking.k8s.io/v1  
    kind: Ingress  
    metadata:  
    name: cloud-metadata-accessor  
    namespace: default  
    spec:  
    podSelector:  
    matchLabels:  
    role: metadata-accessor  
    policyTypes:  
    - Egress  
    egress:  
    - to:  
    - ipBlock:  
    cidr: 192.168.10.10/32

  
  
  
---  
  
使用 Kubesec 进行静态分析

  

    
    
    kubesec scan pod.yaml  
      
    # Using online kubesec API  
    curl -sSX POST --data-binary @pod.yaml https://v2.kubesec.io/scan  
      
    # Running the API locally  
    kubesec http 8080 &  
      
    kubesec scan pod.yaml -o pod_report.json -o json  
  
---  
  
  

使用trivy进行漏洞扫描​

  

    
    
    trivy image nginx:1.18.0  
    trivy image --severity CRITICAL nginx:1.18.0  
    trivy image --severity CRITICAL, HIGH nginx:1.18.0  
    trivy image --ignore-unfixed nginx:1.18.0  
      
    # Scanning image tarball  
    docker save nginx:1.18.0 > nginx.tar  
    trivy image --input archive.tar  
      
    # Scan and output results to file  
    trivy image --output python_alpine.txt python:3.10.0a4-alpine  
    trivy image --severity HIGH --output /root/python.txt python:3.10.0a4-alpine  
      
    # Scan image tarball  
    trivy image --input alpine.tar --format json --output /root/alpine.json  
  
---  
  
删除不需要的服务​

  

    
    
    列出服务：  
    systemctl list-units --type service  
      
    停止服务：  
    systemctl stop nginx  
      
    禁用服务：  
    systemctl disable nginx  
      
    删除服务  
    apt remove nginx  
  
---  
  
### 绑定运行时类：

Kubernetes 在新版本中引入了 RuntimeClass 功能，v1.12用于选择容器运行时配置。容器运行时配置用于运行 pod 的底层容器。

大多数 Kubernetes 集群将dockershim用作运行容器的 Runtime 类，但您可以使用不同的容器 Runtime。

在dockershimKubernetes 版本中已弃用v1.20，并将在v1.24.​

创建运行时类：​

  

    
    
    apiversion: node.k8s.io/v1beta1  
    kind: RuntimeClass  
    metadata:  
    name: gvisor  
    handler: runsc  
  
---  
  
给pod绑定运行时类​

  

    
    
    apiVersion: v1  
    kind: Pod  
    metadata:  
    labels:  
    run: nginx  
    name: nginx  
    spec:  
    runtimeClassName: gvisor  
    containers:  
    - name: nginx  
    image: nginx  
  
---  
  
### RBAC 使用：

基于角色的访问控制 (RBAC) 命令提供了一种基于单个用户或服务帐户的角色来调节对 Kubernetes 资源的访问的方法。​

  

    
    
    创建角色：  
    kubectl create role developer --resource=pods --verb=create,list,get,update,delete --namespace=development  
      
    角色绑定：  
    kubectl create rolebinding developer-role-binding --role=developer --user=zhangsan--namespace=development  
      
    验证：  
    kubectl auth can-i update pods --namespace=development --as=zhangsan   
      
    创建集群角色：  
    kubectl create clusterrole pvviewer-role --resource=persistentvolumes --verb=list  
      
    clusterrole和serviceaccount绑定  
    kubectl create clusterrolebinding pvviewer-role-binding --clusterrole=pvviewer-role --serviceaccount=default:pvviewer  
  
---  
  
### K8s 集群维护：

使用kubectl drain命令从给定节点中删除所有正在运行的工作负载（pod）。​

使用kubectl cordon命令来封锁节点以将其标记为可调度。​

使用kubectl uncordon命令将节点设置为可调度，这意味着控制器管理器可以将新 pod 调度到给定节点。

  

    
    
    排空所有 pod 的节点：  
    kubectl drain node-1  
      
    排空节点并忽略守护程序集：  
    kubectl drain node01 --ignore-daemonsets  
      
    将一个节点标记为不可调度，这样就不能在这个节点上调度新的 Pod  
    kubectl cordon node-1  
      
    标记节点可调度  
    kubectl uncordon node-1  
  
---  
  
## CKS考试技巧

Kuberneteskubectl get命令为用户提供了一个输出标志-o或--output，它帮助我们以 JSON、yaml、wide 或 custom-columns 的形式格式化输出。​

## CKS 真题分享

#### 如何保护和强化容器镜像

在设计容器映像以运行您的代码时，请特别注意保护和强化措施，以防止黑客入侵和特权升级。在构建容器镜像时请记住以下几点：​

  * 使用特定的包版本，例如alpine:3.13.​
  * 不要以 root 身份运行 - 使用USER <username>来阻止 root 访问。​
  * securityContext在使用中使文件系统只读readOnlyRootFilesystem: true​
  * 使用删除 shell 访问RUN rm -rf /bin/*​

#### 如何最小化操作系统占用空间

##### 容器层：

说明RUN、COPY和ADD创建容器层。其他指令创建临时中间图像并且不增加构建的大小。创建图层的说明会增加结果图像的大小。

典型的 Dockerfile 如下所示。RUN它使用指令添加单层。

  

  

  

    
    
    FROM ubuntu  
      
    RUN apt-get update && apt-get install -y golang-go  
      
    CMD ["sh"]  
  
---  
  
##### 多阶段构建

多阶段构建利用FROMDockerfile
中的多个语句。该FROM指令标志着构建的一个新阶段。它结合了多个FROM语句，允许利用以前的构建，以便有选择地将二进制文件复制到新的构建阶段，省略不必要的二进制文件。生成的
Docker 映像的大小要小得多，风险面也大大减少。​

  

  

  

    
    
    FROM ubuntu:20.04 AS build  
    ARG DEBIAN_FRONTEND=noninteractive  
    RUN apt-get update && apt-get install -y golang-go  
    COPY app.go .  
    RUN CGO_ENABLED=0 go build app.go  
      
    FROM alpine:3.13  
    RUN chmod a-w /etc  
    RUN addgroup -S appgroup && adduser -S appuser -G appgroup -h /home/appuser  
    RUN rm -rf /bin/*  
    COPY --from=build /app /home/appuser/  
    USER appuser  
    CMD ["/home/appuser/app"]

  
  
  
---  
  
## 总结：

勤加练习是通过CKS考试的关键，本文只列举了部分实操内容，更多考试内容以及详细信息可以前往CNCF官网或Linux
foundation查看，最后祝各位考试顺利通过！

## 关于HummerRisk

HummerRisk 是开源的云原生安全平台，以非侵入的方式对云原生环境进行全面安全检测。

![](https://image.3001.net/images/20221013/1665652904_6347d8a83810ccdbdbb05.png!small)

针对于K8s的安全，我们提供多方面的检测能力，可以帮助用户快速发现K8s集群中的各种安全问题。

访问项目地址了解试用：
​[​https://github.com/HummerRisk/HummerRisk​](https://github.com/HummerRisk/HummerRisk)​

  

