Jenkins通过Kubernetes插件配置动态创建slave agent

[ 87d6dc4b11a7](https://www.jianshu.com/u/87d6dc4b11a7)关注赞赏支持

# Jenkins通过Kubernetes插件配置动态创建slave agent

### 环境准备：

  * kubernetes集群
  * 已安装Jenkins实例
  * 已安装kubernetes插件

### 配置：

Manage Jenkins -> Manage Nodes and Clouds -> Configure Clouds -> Add a new
cloud -> Kubernetes

##### kubernetes信息获取

从`/root/.kube/config`获取K8S信息  
Kubernetes 地址：对应文件中的clusters.cluster.server地址  
Kubernetes 服务证书 key：对应文件中的clusters.cluster.certificate-authority-
data，需要base64解码  
将clusters.cluster.certificate-authority-data写入tmp文件中，进行解码

    
    
    [root@localhost ~]# cat tmp | base64 -d
    -----BEGIN CERTIFICATE-----
    MIIC5zCCAc+gAwIBAgIBADANBgkqhkiG9w0BAQsFADAVMRMwEQYDVQQDEwprdWJl
    cm5ldGVzMB4XDTIxMDkwOTEzMDIzMloXDTMxMDkwNzEzMDIzMlowFTETMBEGA1UE
    AxMKa3ViZXJuZXRlczCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAM7J
    FAYXJKlpLhk/Hd5fAGdbSXRktSD/Kiu9rfr4Vcn6N1UhCqO5dzoldCmQdrNpsXfq
    odp4MCIzVAz8R8v3O16jfG3wAgIu9pg1gy2InveOvcTWQNN/yZe5oFISgygpvcZe
    tJPm4SJ+w7bKknIJIa+1K63SPba/1ahmFJUY00JZMLEodZvYYRnr2bwj0X72MedK
    bWkfpdI7jgbmgG33SBzUZnkgCT2xB+H0WAoFEYFUCCtJeRCJIKDZEy2zB7qJ3bPN
    t7M1lBoQ5jFMXMgKr6zKcC5t0v942Em2E38B1DVqAtfIGaVOKVkd9C1+KEGkuLZq
    Vi06ZtLm5jxMLkZn9yUCAwEAAaNCMEAwDgYDVR0PAQH/BAQDAgKkMA8GA1UdEwEB
    /wQFMAMBAf8wHQYDVR0OBBYEFG4n14BhJm6tDcX7p7HwntKWJIadMA0GCSqGSIb3
    DQEBCwUAA4IBAQAgk2rt4ffbeb1RGjqhlWio6QEhp/myo8jV79Mfrp3zdirqG4GK
    HjAM6y6fOZkqR0U3bA6CTF6XpyY4OxST3A9rE6hKb/oKAlFW9Vgl3KEDVWMPA6qO
    5ZMa+/liUs6KwXOAPOLWQjYCamIcfESFczfcU4TBFT9v2OHe4tfpoNpOi1j8I6m8
    RrHepYUqylWjHlEBvWlAkfTGnzH9oug22zRAkAy63fis8pkBAiFtFW//iC/xSBym
    j+n3jo+J+16eheh1cEia88Z6/OuZPmKcdZ1PGCGDDCKCgajdeDmDgG+v24aGo2V2
    2bJtNjr0eOaT6smyVwaTNBdTVkPhFfP7cbu8
    -----END CERTIFICATE-----
    

凭据：  
一、Secret text (Token-based authentication)

    
    
    # 创建命名空间
    kubectl create namespace jenkins
    # 创建sa-jenkins用户
    kubectl create serviceaccount jenkins -n jenkins
    # 绑定admin角色到sa-jenkins用户
    kubectl create clusterrolebinding -n jenkins jenkins-cluster-admin --clusterrole='cluster-admin' --serviceaccount=jenkins:jenkins
    # 查询token
    kubectl get secrets -n jenkins -o jsonpath="{.items[?(@.metadata.annotations['kubernetes\.io/service-account\.name']=='jenkins')].data.token}" | base64 -d
    

添加凭据.png

  

配置完成后，点击“连接测试”。

  

连接测试成功.png

当勾选`禁用HTTPS证书检查`时，可以不用输入Kubernetes 服务证书 key  

添加pod模板

更新：  
搭建了 v1.25 版本的 k8s集群，使用 `kubectl get secrets -n jenkins -o
jsonpath="{.items[?(@.metadata.annotations['kubernetes\.io/service-
account\.name']=='jenkins')].data.token}" | base64 -d` 无法获取到 token。使用`kubectl
describe sa jenkins -n jenkins`查询结果如下。

    
    
    root@nianyu-virtual-machine:~#  kubectl describe sa jenkins -n jenkins
    Name:                jenkins
    Namespace:           jenkins
    Labels:              <none>
    Annotations:         <none>
    Image pull secrets:  <none>
    Mountable secrets:   <none>
    Tokens:              <none>
    Events:              <none>
    

谷歌后发现从 1.24 开始，服务帐户令牌的 Secret API 对象不再为每个 ServiceAccount自动生成。  
参考官方文档 [https://kubernetes.io/zh-
cn/docs/concepts/configuration/secret/#service-account-token-
secrets](https://links.jianshu.com/go?to=https%3A%2F%2Fkubernetes.io%2Fzh-
cn%2Fdocs%2Fconcepts%2Fconfiguration%2Fsecret%2F%23service-account-token-
secrets) 为服务账户创建 secret 。

    
    
    apiVersion: v1
    kind: Secret
    metadata:
      name: jenkins-token
      namespace: jenkins
      annotations:
        kubernetes.io/service-account.name: "jenkins"
    type: kubernetes.io/service-account-token
    

创建后再次查询

    
    
    root@nianyu-virtual-machine:~# kubectl describe sa jenkins -n jenkins
    Name:                jenkins
    Namespace:           jenkins
    Labels:              <none>
    Annotations:         <none>
    Image pull secrets:  <none>
    Mountable secrets:   <none>
    Tokens:              jenkins-token
    Events:              <none>
    root@nianyu-virtual-machine:~# kubectl get secrets -n jenkins -o jsonpath="{.items[?(@.metadata.annotations['kubernetes\.io/service-account\.name']=='jenkins')].data.token}" | base64 -d
    eyJhbGciOiJSUzI1NiIsImtpZCI6IllDX3QtSG1ZQW81akdNVWFrX3hLQVRnMFRoYnVGdk1ieU5xTkdjVE5tb3cifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJqZW5raW5zIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImplbmtpbnMtdG9rZW4iLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiamVua2lucyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI2Yjg0NWQ4LTU0NmUtNDMwNS05MzA2LTRhZTljMDAwMWNhYSIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpqZW5raW5zOmplbmtpbnMifQ.CDWy7ykD7A9Cl-2Ql68H_PtvTVP3O24luC0Io2szaROp1UyI81qMCy9vCvcCFd4dxYHlWlbDrLkOJOkorsX8bN__rx3ElhPA48xr2r68y8veYDc8mUXRezeiF0G-lYuqtCpR0tM6nLpiTxcNHgTZsJ5a_zIEPCuaxw0dzfwc3sjeJKd6RDDtqLn1Tp3QPBH-fzHXnQpClhjquWt-48gh6BO5_5ixVwroiUtQbiy6z2iL2KIFq6gQF-YEL87BdH4VcdWN7wXXMhOIOyDBK_638k6-iBqOKTGzqSvNStLd8OGWkXotwIBnyiCKjX_aHxqxAKsGC0sFlmUhRr_4lr0noA
    

参考：[https://plugins.jenkins.io/kubernetes/](https://links.jianshu.com/go?to=https%3A%2F%2Fplugins.jenkins.io%2Fkubernetes%2F)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [04 Jenkins Kubernetes插件动态创建slave agent](https://www.jianshu.com/p/4652bb23de6f)

完成03 Jenkins master安装（在Kubernetes平台上）的Jenkins master安装后，我...

[georgesre](https://www.jianshu.com/u/1dccda0ce716)阅读 5,473评论 0赞 1

  * [kubernetes（k8s） jenkins CI/CD（动态创建slave）](https://www.jianshu.com/p/0aef1cc27d3d)

jenkins CI/CD（动态创建slave）简述： 持续构建与发布是我们日常工作中必不可少的一个步骤，目前大多...

[祁恩达](https://www.jianshu.com/u/df8978d3d5e9)阅读 9,475评论 3赞 5

  * [《Cloud Native 》云原生技术汇总](https://www.jianshu.com/p/37559245489a)

An awesome & curated list of best applications and tools ...

[运维前线](https://www.jianshu.com/u/4e7e2ebc67d1)阅读 3,071评论 0赞 5

  * [kubernetes部署jenkins(Docker in Docker)及认证](https://www.jianshu.com/p/b68ec8c6cfd5)

引言 Jenkins是一款开源 CI&CD 软件，用于自动化各种任务，包括构建、测试和部署软件。本文将Jenkin...

[我给你一个大大的YES](https://www.jianshu.com/u/5ce64f2a316d)阅读 740评论 0赞 1

  * [Jenkins使用Kubernetes(同/不同集群)启动动态slave的几种方式(kubec...](https://www.jianshu.com/p/4cf53c689c5c)

需要用到两个插件：kubernetes-plugin，credential-plugin https://gith...

[jaymz明](https://www.jianshu.com/u/3e048dfc7ec0)阅读 721评论 1赞 6

 