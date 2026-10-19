![](https://image.3001.net/images/20210519/1621408894_60a4bc7e2fce9ce11668a.png!small)

## 关于Red-Kube

Red-Kube是一套kubectl命令工具集，该工具旨在帮助广大研究人员从网络攻击者的角度评估Kubernetes集群的安全态势。

这些命令可以实现被动数据收集和信息披露，或者用于主动执行影响集群的实际操作。这些命令被映射到了MITRE ATT&CK
Tactics以帮助广大安全研究人员了解集群安全间隙。

当前版本的Red-Kube被封装成了使用python模块，以便基于不同的场景或策略在一次任务执行中运行多个命令。

## 依赖组件

 **Python3依赖：**

    
    
    pip3 install -r requirements.txt

 **Kubectl（Ubuntu/Debian）：**

    
    
    sudo apt-get update
    
    sudo apt-get install -y apt-transport-https ca-certificates curl
    
    sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
    
    echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
    
    sudo apt-get update
    
    sudo apt-get install -y kubectl

 **Kubectl（Red Hat）：**

    
    
    cat <<EOF > /etc/yum.repos.d/kubernetes.repo
    
    [kubernetes]
    
    name=Kubernetes
    
    baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
    
    enabled=1
    
    gpgcheck=1
    
    repo_gpgcheck=1
    
    gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
    
    EOF
    
    yum install -y kubectl

 **jq：**

    
    
    sudo apt-get update -y
    
    sudo apt-get install -y jq

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/lightspin-tech/red-kube.git

## 工具使用

    
    
    usage: python3 main.py [-h] [--mode active/passive/all] [--tactic TACTIC_NAME] [--show_tactics] [--cleanup]
    
     
    
    required arguments:
    
    --mode            run kubectl commands which are active / passive / all modes
    
    --tactic          choose tactic
    
     
    
    other arguments:
    
    -h --help         show this help message and exit
    
    --show_tactics    show all tactics

## MITRE ATT&CK Tactics命令

 ** **策略****

|

 ** **数量****  
  
---|---  
  
网络侦察

|

2  
  
初始访问

|

0  
  
命令执行

|

0  
  
持久化

|

2  
  
权限提升

|

4  
  
防御规避

|

1  
  
凭证访问

|

8  
  
扫描发现

|

15  
  
横向渗透

|

0  
  
数据收集

|

1  
  
命令控制

|

2  
  
数据提取

|

1  
  
影响

|

0  
  
## 项目地址

Red-Kube：【[ _GitHub传送门_](https://github.com/lightspin-tech/red-kube)】

## 许可证协议

本项目的开发与发布遵循[ _Apache v2.0_](https://github.com/lightspin-tech/red-kube/blob/main/LICENSE)开源许可证协议。

