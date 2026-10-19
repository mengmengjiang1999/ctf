![](https://image.3001.net/images/20200228/1582882222_5e58ddaebee8d.png!small)

## Multi-Juicer

 **Multi-Juicer是一款帮助用户结合[ _OWASP Juice
Shop_](https://github.com/bkimminich/juice-shop)来运行CTF以及安全培训的多用户平台工具集。各位安全研究人员可能知道，在[ _OWASP Juice
Shop_](https://github.com/bkimminich/juice-shop)的帮助下，我们可以轻松地搭建CTF平台，或者进行安全培训。但是，OWASP Juice Shop的设计理念并不支持多用户同时使用的情况。**
**除此之外，用户在自己的设备上搭建OWASP Juice Shop时，可能需要花费很多的时间。不过别担心，Multi-Juicer可以帮你解决各种“疑难杂症”。**

Multi-Juicer能够帮助我们在一个中央Kubernetes集群中，为每一个OWASP Juice Shop的参与者单独运行一个Juice
Shop实例，而且每一个用户都无需再本地运行Juice Shop实例。

## 功能介绍

> 1、在用户需要的时候，动态创建新的Juice Shop实例；
>
> 2、在单个域名中运行，并使用了一个负载均衡器来帮助Juice Shop实例的参与者发送流量；
>
> 3、为防止Juice Shop容器重启，可自动备份并恢复挑战进程；
>
> 4、自动清除旧的和未使用的Juice Shop实例；

![](https://image.3001.net/images/20200228/1582882240_5e58ddc0ad97f.png!small)

## 工具安装

Multi-Juicer需要在Kubernetes上运行，在安装过程中，我们需要用到helm【[ _点我获取_](https://helm.sh/)】：

    
    
    helm repo add multi-juicer<https://iteratec.github.io/multi-juicer/>
    
    # for helm <= 2
    
    helm install multi-juicer/multi-juicer --name multi-juicer
    
    # for helm >= 3
    
    helm install multi-juicer multi-juicer/multi-juicer

### 云服务商安装指引

通常情况下，Multi-Juicer可以在任意Kubernetes集群中正常运行，为了方便大家在不同云服务提供商的Kubernetes集群中安装、配置和运行Multi-Juicer，大家可以参考下面相应的配置参考文档：

> Digital Ocean：【[ _参考文档_](https://github.com/iteratec/multi-> juicer/blob/master/guides/digital-ocean/digital-ocean.md)】
>
> OpenShift：【[ _参考文档_](https://github.com/iteratec/multi-> juicer/blob/master/guides/openshift/openshift.md)】
>
> AWS：【[ _参考文档_](https://github.com/iteratec/multi-> juicer/blob/master/guides/aws/aws.md)】
>
> [WIP]Azure：【[ _参考文档_](https://github.com/iteratec/multi-> juicer/blob/master/guides/azure/azure.md)】

### 自定义配置

在安装Multi-Juicer的过程中，我们可以通过多种自定义配置来配置我们自己的Juice Shop实例。你可以点击【[
_这里_](https://github.com/iteratec/multi-juicer/blob/master/helm/multi-juicer/values.yaml)】获取默认配置值。

下载并存储文件【[ _点我下载_](https://github.com/iteratec/multi-juicer/blob/master/helm/multi-juicer/values.yaml)】，然后让helm使用我们的配置文件来执行工具的安装与配置：

helm install -f values.yaml multi-juicer ./multi-juicer/helm/multi-juicer/

## 工具卸载

helm delete multi-juicer

### 工具依赖

为了能够正常在Kubernetes集群上运行Multi-Juicer，工具对集群的计算资源需求如下：

> -1GB内存 & 1 CPU
>
> -针对单个JuiceShop实例，200MB & 0.2CPU*参与人数

## 项目地址

> Multi-Juicer：【[ _GitHub传送门_](https://github.com/iteratec/multi-juicer)】

 *** 参考来源：[ _iteratec_](https://github.com/iteratec/multi-juicer)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

