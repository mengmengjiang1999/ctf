![](https://image.3001.net/images/20200807/1596785837.png!small)

## 前言

近期，研究人员在Kubernetes节点的网络组件kube-proxy中发现了一个严重的安全漏洞（[
_CVE-2020-8558_](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-8558)），而这个安全漏洞会将Kubernetes节点的内部服务暴露在外。在某些情况下，这个漏洞还有可能将api-server暴露在外，这将允许未经认证的攻击者获取Kubernetes集群的完整控制权限。在这种情况下，攻击者将能够窃取目标集群中存储的敏感信息，部署加密挖矿软件，或移除线上服务等等。

该漏洞会暴露目标Kubernetes节点的“localhost服务”，这个服务原本是一个仅可以从节点内部或节点本身访问的服务，但该漏洞现在会将其暴露给本地网络或运行在该节点上的Pods。本地主机所绑定的服务原本只能允许受信任的本地进程与之交互，因此通常不需要身份验证就可以请求服务了。如果你的节点在运行“localhost服务”时没有要求强制进行身份验证的话，你也将会受到该漏洞的影响。

简而言之，漏洞CVE-2020-8558将允许攻击者访问目标Kubernetes集群中的insecure-port，并获取到目标集群的完整控制权。

## kube-proxy

kube-proxy是一个运行在[
_Kubernetes集群_](https://kubernetes.io/docs/concepts/services-networking/service/)中每一个节点上的网络代理，它的任务就是管理Pods和服务之间的连接。Kubernetes服务会暴露一个clusterIP，并且可能由多个后端Pods组成以实现均衡负载。一个服务一般由三个Pods组成，每一个都拥有其自己的IP地址，但是它们只会暴露一个clusterIP，假设是“10.0.0.1”。Podas在访问目标服务时，会将数据包发送给它的clusterIP，也就是“10.0.0.1”，但随后数据包必须重定向给其中一个Pods。

在这里，kube-proxy的作用就是为每一个节点提供路由表服务，这样才能保证请求能够正确路由至其中一个Pods。

## 罪魁祸首 - route_localnet

kube-proxy可以通过[
_sysctl文件_](https://www.kernel.org/doc/Documentation/sysctl/README)来配置多个网络参数，其中一个就是net.ipv4.conf.all.route_localnet，而它就是导致这个漏洞出现的罪魁祸首。根据[
_sysctl文档_](https://sysctl-explorer.net/net/ipv4/route_localnet/)的描述：“route_localnet：路由时不需要将回环地址设定为目的地址，这样就可以使用127/8作为本地路由地址，默认为FALSE。”

针对IPv4地址，回环地址由127.0.0.0/8块（127.0.0.1-127.255.255.255）组成，一般我们使用的是127.0.0.1，并将“localhost”映射到该地址，针对本地服务的数据包将通过回环网络接口发送至IP
127.0.0.1。

设置route_localnet时，需要指示内核不要将地址127.0.0.1/8
IP定义为“martian”，那么这里的“martian”是什么意思呢？比如说，有些数据包在抵达一个网络接口时，可以声明它们的源IP地址或目的IP地址，假设抵达的数据包源IP地址为255.255.255.255，那么这个数据包本应该不存在，因为255.255.255.255这个地址时一个用于标识广播地址的保留地址。此时，你的内核就无法确定了，只能判定这个数据包来自未知地方，应该被丢弃。

“Martian”数据包往往意味着有人在试图通过网络攻击你，在上面的例子中，攻击者可能想要你的服务去响应IP
255.255.255.255，并让路由来广播响应信息。但是在一些复杂的路由场景中，你可能想要内核去允许某些特定的“martian”包通过，这就是route_localnet的作用了。它可以让内核不要将地址127.0.0.1/8
IP定义为“martian”包。kube-proxy能够让route_localnet支持各种路由包，那么在没有部署适当安全机制的情况下，攻击者将能够通过本地网络并利用route_localnet来执行各种攻击了。

## Localhost-only服务

Linux允许进程去监听一个指定的IP地址，这样就可以让它们跟地址对应的网络接口进行绑定了。内部服务通常会使用这种功能来监听127.0.0.1，一般来说，这样可以确保只有本地进程能够访问该服务。但是由于route_localnet的存在，外部数据包将同样能够抵达127.0.0.0/8。

## 访问内部服务

在这种情况下，如果攻击者尝试访问目标设备的内部服务，则需要构建一个目的IP为127.0.0.1，并且目的MAC地址为目标设备MAC地址的恶意数据包。如果目的IP无效，恶意数据包只能依赖于第二层（基于MAC）路由来抵达目标设备了。因此，即使目标用户启用了route_localnet，那么只有处于本地网络中的攻击者才能够访问目标设备的localhost服务。

当目标设备接收到恶意数据包之后，route_localnet将允许这个包通过，因为这个包的目的IP为127.0.0.1，那么它将被允许访问localhost服务。下表中显示的是恶意包的结构：![](https://image.3001.net/images/20200807/1596785873.png!small)

由于kube-proxy的存在，集群中的每一个节点都启用了route_localnet。因此，节点本地网络中的每一台主机都将能够访问节点的内部服务。如果你的节点在运行内部服务时没有部署身份认证机制，那你将会受到该漏洞的影响。值得一提的是，除了节点内部网络中的相邻主机之外，运行在节点内的Pods同样能够访问其内部服务。

## 漏洞修复

Unit 42团队将该漏洞报告给了Kubernetes安全团队，该团队表示如果集群启用了api-server insecure-port，则该漏洞的严重程度为高危，未启用则为中危。幸运的是，该漏洞的影响仅限于大部分托管Kubernetes服务，例如Azure Kubernetes
Service（AKS），Amazon的Elastic Kubernetes Service（EKS）和Google Kubernetes
Engine（GKE）。

该漏洞影响Kubernetes
1.1.0版本至1.16.10版本，1.17.0版本至1.17.6版本，和1.18.0版本至1.18.3版本。Kubernetes
1.18.4版本，1.17.7版本和1.16.11版本已修复该漏洞。

## 参考文档

> 1、 _https://cloud.google.com/kubernetes-engine/docs/concepts/network-> overview#kube-proxy_
>
> 2、[ _https://cilium.io/_](https://cilium.io/)
>
> 3、[ _https://cve.mitre.org/cgi-> bin/cvename.cgi?name=CVE-2020-8558_](https://cve.mitre.org/cgi-> bin/cvename.cgi?name=CVE-2020-8558)
>
> 4、[
> _https://github.com/kubernetes/kubernetes/issues/90259_](https://github.com/kubernetes/kubernetes/issues/90259)
>
> 5、[
> _https://github.com/kubernetes/kubernetes/pull/91569_](https://github.com/kubernetes/kubernetes/issues/90259)

