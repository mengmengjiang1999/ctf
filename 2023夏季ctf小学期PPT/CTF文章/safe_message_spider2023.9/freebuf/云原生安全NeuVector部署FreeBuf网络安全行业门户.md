****NeuVector概览****

NeuVector
致力于保障企业级容器平台安全，可以提供实时深入的容器网络可视化、东西向容器网络监控、主动隔离和保护、容器主机安全以及容器内部安全，容器管理平台无缝集成并且实现应用级容器安全的自动化，适用于各种云环境、跨云或者本地部署等容器生产环境。2021年，
NeuVector 被 SUSE 收购，并在 2022 年 1
月完成开源，成为业界首个端到端的开源容器安全平台，唯一为容器化工作负载提供企业级零信任安全的解决方案。

 ** **NeuVector部署****

 ** **K8S部署NeuVector****

##  ** **1.创建NeuVector命名空间****

kubectl create namespace neuvector

##  ** **2.为 NeuVector 安全规则创建自定义资源 (CRD)****

###  ** **2.1对于 Kubernetes 1.19+****

kubectl apply -f
https://raw.githubusercontent.com/neuvector/manifests/main/kubernetes/5.0.0/crd-k8s-1.19.yaml  
kubectl apply -f
https://raw.githubusercontent.com/neuvector/manifests/main/kubernetes/5.0.0/waf-crd-k8s-1.19.yaml  
kubectl apply -f
https://raw.githubusercontent.com/neuvector/manifests/main/kubernetes/5.0.0/dlp-crd-k8s-1.19.yaml  
kubectl apply -f
https://raw.githubusercontent.com/neuvector/manifests/main/kubernetes/5.0.0/admission-crd-k8s-1.19.yaml

###  ** **2.2 对于Kubernetes 1.18及更早版本****

kubectl apply -f
https://raw.githubusercontent.com/neuvector/manifests/main/kubernetes/5.0.0/crd-k8s-1.16.yaml  
kubectl apply -f
https://raw.githubusercontent.com/neuvector/manifests/main/kubernetes/5.0.0/waf-crd-k8s-1.16.yaml  
kubectl apply -f
https://raw.githubusercontent.com/neuvector/manifests/main/kubernetes/5.0.0/dlp-crd-k8s-1.16.yaml  
kubectl apply -f
https://raw.githubusercontent.com/neuvector/manifests/main/kubernetes/5.0.0/admission-crd-k8s-1.16.yaml

##  ** **3.添加读取权限以访问 kubernetes API****

Kubernetes 1.8+ 正式支持 RBAC。 Kubernetes 1.9+ 支持准入控制。

kubectl create clusterrole neuvector-binding-app --verb=get,list,watch,update
--resource=nodes,pods,services,namespaces  
kubectl create clusterrole neuvector-binding-rbac --verb=get,list,watch
--resource=rolebindings.rbac.authorization.k8s.io,roles.rbac.authorization.k8s.io,clusterrolebindings.rbac.authorization.k8s.io,clusterroles.rbac.authorization.k8s.io  
kubectl create clusterrolebinding neuvector-binding-app
--clusterrole=neuvector-binding-app --serviceaccount=neuvector:default  
kubectl create clusterrolebinding neuvector-binding-rbac
--clusterrole=neuvector-binding-rbac --serviceaccount=neuvector:default  
kubectl create clusterrole neuvector-binding-admission
--verb=get,list,watch,create,update,delete
--resource=validatingwebhookconfigurations,mutatingwebhookconfigurations  
kubectl create clusterrolebinding neuvector-binding-admission
--clusterrole=neuvector-binding-admission --serviceaccount=neuvector:default  
kubectl create clusterrole neuvector-binding-customresourcedefinition
--verb=watch,create,get,update --resource=customresourcedefinitions  
kubectl create clusterrolebinding neuvector-binding-customresourcedefinition
--clusterrole=neuvector-binding-customresourcedefinition
--serviceaccount=neuvector:default  
kubectl create clusterrole neuvector-binding-nvsecurityrules
--verb=list,delete --resource=nvsecurityrules,nvclustersecurityrules  
kubectl create clusterrolebinding neuvector-binding-nvsecurityrules
--clusterrole=neuvector-binding-nvsecurityrules
--serviceaccount=neuvector:default  
kubectl create clusterrolebinding neuvector-binding-view --clusterrole=view
--serviceaccount=neuvector:default  
kubectl create rolebinding neuvector-admin --clusterrole=admin
--serviceaccount=neuvector:default -n neuvector  
kubectl create clusterrole neuvector-binding-nvwafsecurityrules
--verb=list,delete --resource=nvwafsecurityrules  
kubectl create clusterrolebinding neuvector-binding-nvwafsecurityrules
--clusterrole=neuvector-binding-nvwafsecurityrules
--serviceaccount=neuvector:default  
kubectl create clusterrole neuvector-binding-nvadmissioncontrolsecurityrules
--verb=list,delete --resource=nvadmissioncontrolsecurityrules  
kubectl create clusterrolebinding neuvector-binding-nvadmissioncontrolsecurityrules --clusterrole=neuvector-binding-nvadmissioncontrolsecurityrules --serviceaccount=neuvector:default  
kubectl create clusterrole neuvector-binding-nvdlpsecurityrules
--verb=list,delete --resource=nvdlpsecurityrules  
kubectl create clusterrolebinding neuvector-binding-nvdlpsecurityrules
--clusterrole=neuvector-binding-nvdlpsecurityrules
--serviceaccount=neuvector:default

###  ** **3.1 检查是否有以下 RBAC 对象****

kubectl get clusterrolebinding | grep neuvector

neuvector-binding-admission ClusterRole/neuvector-binding-admission 32m  
neuvector-binding-app ClusterRole/neuvector-binding-app 32m  
neuvector-binding-customresourcedefinition ClusterRole/neuvector-binding-customresourcedefinition 32m  
neuvector-binding-nvadmissioncontrolsecurityrules ClusterRole/neuvector-binding-nvadmissioncontrolsecurityrules 32m  
neuvector-binding-nvdlpsecurityrules ClusterRole/neuvector-binding-nvdlpsecurityrules 32m  
neuvector-binding-nvsecurityrules ClusterRole/neuvector-binding-nvsecurityrules 32m  
neuvector-binding-nvwafsecurityrules ClusterRole/neuvector-binding-nvwafsecurityrules 32m  
neuvector-binding-rbac ClusterRole/neuvector-binding-rbac 32m  
neuvector-binding-view ClusterRole/view 32m  
​

kubectl get rolebinding -n neuvector | grep neuvector

neuvector-admin ClusterRole/admin 34m

##  ** **4.部署Neuvector****

###  ** **4.1需要上传Neuvector的镜像包****

![1651715603_62732e138dd8527b7702d.png!small?1651715604550](https://image.3001.net/images/20220505/1651715603_62732e138dd8527b7702d.png!small?1651715604550)

###  ** **4.2 底层Runtime为Docker****

在master上和node上加载镜像：

docker load -i neuvector.tar.gz

运行yaml文件

kubectl apply -f
https://raw.githubusercontent.com/neuvector/manifests/main/kubernetes/5.0.0/neuvector-docker-k8s.yaml

###  ** **4.3 底层Runtime为Containerd****

在master上和node上加载镜像：

nerdctl load - i neuvector.tar.gz

运行yaml文件

kubectl apply -f
https://raw.githubusercontent.com/neuvector/manifests/main/kubernetes/5.0.0/neuvector-containerd-k8s.yaml

###  ** **4.4查看neuvector服务是否running****

root@master:~# kubectl get pods -n neuvector

NAME READY STATUS RESTARTS AGE

neuvector-controller-pod-5dfcb9df96-c25xz 1/1 Running 0 41m

neuvector-controller-pod-5dfcb9df96-jn4c2 1/1 Running 0 41m

neuvector-controller-pod-5dfcb9df96-l8tkj 1/1 Running 0 41m

neuvector-enforcer-pod-6v6nf 1/1 Running 0 41m

neuvector-enforcer-pod-pj44w 1/1 Running 0 41m

neuvector-manager-pod-5b48dbbfd9-78qt9 1/1 Running 0 41m

neuvector-scanner-pod-fcc55c85b-99wgr 1/1 Running 0 41m

neuvector-scanner-pod-fcc55c85b-hmd2n 1/1 Running 0 41m

###  ** **4.5 查看webui端口****

![1651715625_62732e2955e53d88221cd.png!small?1651715625822](https://image.3001.net/images/20220505/1651715625_62732e2955e53d88221cd.png!small?1651715625822)

###  ** **4.6如何访问NeuVector****

访问 https://node_ip:30876

默认密码为 admin/admin

![1651715729_62732e910822c6bea8c4b.png!small?1651715729935](https://image.3001.net/images/20220505/1651715729_62732e910822c6bea8c4b.png!small?1651715729935)

