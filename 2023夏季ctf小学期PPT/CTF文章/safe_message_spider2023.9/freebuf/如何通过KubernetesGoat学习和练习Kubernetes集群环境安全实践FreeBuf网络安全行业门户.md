![](https://image.3001.net/images/20220101/1641008929_61cfcf21f30077ff74d55.png!small)

## 关于Kubernetes Goat

Kubernetes
Goat是一款针对Kubernetes安全的学习、测试和练习工具，该工具可以给广大研究人员提供一个存在安全缺陷（故意留下漏洞）的集群环境，来帮助广大安全爱好者学习和实践Kubernetes安全。

![](https://image.3001.net/images/20220101/1641008960_61cfcf40c8c5e5bce8c58.png!small)

  

## 在线体验

![](https://image.3001.net/images/20220101/1641008973_61cfcf4d8948797107d4f.png!small)

 **传送门：** 【[ _Katacoda Playground Kubernetes
Goat_](https://katacoda.com/madhuakula/scenarios/kubernetes-goat)】

## Kubernetes Goat配置

在配置Kubernetes Goat之前，请确保你已经创建了Kubernetes集群，并且拥有管理员访问权限：

    
    
    kubectl version --short

在路径中配置helm2版本【[ _文档_](https://github.com/helm/helm/releases)】：

    
    
    helm2 --help

接下来，运行下列命令配置Kubernetes Goat：

    
    
    git clone https://github.com/madhuakula/kubernetes-goat.git
    
    cd kubernetes-goat
    
    bash setup-kubernetes-goat.sh

运行下列命令，在本地导出端口/服务，来开启学习之路：

    
    
    bash access-kubernetes-goat.sh

最后，在浏览器中访问[ _http://127.0.0.1:1234_](http://127.0.0.1:1234/)即可使用Kubernetes
Goat。

## 应用场景

> 代码库中的敏感密钥
>
> DIND（docker-in-docker）利用
>
> K8S中的SSRF
>
> 容器转义以访问主机系统
>
> Docker CIS基准分析
>
> Kubernetes CIS基准分析
>
> 私有注册表安全
>
> NodePort公开服务
>
> 驾驶v2舵柄至仪表组
>
> 分析加密矿工容器
>
> Kubernetes名称空间旁路
>
> 获取环境信息
>
> DoS内存/CPU资源
>
> Hacker容器预览
>
> RBAC最小特权错误配置
>
> Kubaudit-审计Kubernetes集群
>
> Sysdig Falco-运行时安全监控和检测
>
> Popeye-Kubernetes群集净化
>
> 使用NSP保护网络边界

## 工具演示

 **OWASP Bay Area Meetup：【** https://you*tu.be/DQllxpb46Yw】

 **DEFCON Red Team Village：【** https://you*tu.be/aEaSZJRbnTo】

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/madhuakula/kubernetes-goat/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Kubernetes Goat：** 【[
_GitHub传送门_](https://github.com/madhuakula/kubernetes-goat)】

## 参考资料

> [ _https://madhuakula.com/kubernetes-> goat_](https://madhuakula.com/kubernetes-goat)
>
> [ _https://github.com/madhuakula/kubernetes-> goat/blob/master/guide/src/getting-involved/i-use-this-> project.md_](https://github.com/madhuakula/kubernetes-> goat/blob/master/guide/src/getting-involved/i-use-this-project.md)
>
> [
> _https://forum.defcon.org/node/237237_](https://forum.defcon.org/node/237237)
>
> [ _https://cloud-village.org/#talks?collapseMadhuAkula_](https://cloud-> village.org/#talks?collapseMadhuAkula)

  

