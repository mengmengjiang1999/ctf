## **前言**

2021年4月，Kubernetes社区披露了一个编号为CVE-2020-8562的安全漏洞，授权用户可以通过此漏洞访问 Kubernetes
控制组件上的私有网络。

通过查阅此漏洞披露报告可发现，这个漏洞拥有较低的CVSS
v3评分，其分值仅有2.2分，与以往披露的Kubernetes高危漏洞相比，这个拥有较低评分的漏洞极其容易被安全研究人员以及运维人员所忽视。但经过研发测试发现，在实际情况中，这个低风险的漏洞却拥有着不同于其风险等级的威胁：在与云上业务结合后，CVE-2020-8562漏洞将会为云厂商带来不可忽视的安全挑战。

在这篇文章中，云鼎实验室将为大家带来业内首个CVE-2020-8562漏洞分析报告，一同来看一下这个被忽视的低风险漏洞引发的“血案”。

##  **CVE-2020-8555漏洞简述**

Kubernetes为了缓解CVE-2020-8555等历史漏洞带来的安全问题，对APIServer
Proxy请求进行域名解析以校验请求的IP地址是否处于本地链路 (169.254.0.0/16) 或 localhost (127.0.0.0/8)
范围内，Kubernetes通过此方式禁止由用户触发的对Services，Pods，Nodes，StorageClass对象的内网Proxy访问权限。

但是在完成校验并通过校验之后，Kubernetes立即进行第二次域名解析，此次域名解析后并不再进行IP地址的校验，这将导致上述校验存在绕过问题，如果一个DNS服务器不断返回不同的非缓存解析请求，攻击者可以利用此方式绕过Kubernetes的API
Server Proxy IP地址限制，并访问内网ControlPlane管控组件。

详细的漏洞细节可参见如下图Issue所示：

![](https://image.3001.net/images/20211025/1635148077_6176612d56f100e1151e3.jpg!small)

图 1 CVE-2020-8562漏洞细节

Issue地址如下：

https://github.com/kubernetes/kubernetes/issues/101493

在正式开始介绍这个漏洞是如何对Kubernetes集群带来危害之前，我们先来看看这个漏洞中应用到主要攻击技巧：DNS重绑定攻击（DNS
Rebinding）。

##  **DNS重绑定攻击  
**

DNS重绑定攻击技术的实现主要依赖于攻击者可将其自建的DNS服务器中DNS TTL配置为设置为0或者极小值。DNS
TTL表示DNS记录的生存时间,数值越小, DNS记录在DNS服务器上缓冲的时间越小。

在攻击者将DNS
TTL数值设置为一个极小值时，当受害目标第一次访问恶意域名时并发起域名解析请求时，恶意DNS服务器会返回一个ip地址A；当受害目标第二次发起域名解析请求时，却会得到ip地址B的解析结果。具体的原理，我们可以通过一道CTF题目，深入了解一下：

    
    
    $dst = @$_GET['KR'];$res = @parse_url($dst);$ip = @dns_get_record($res['host'], DNS_A)[0]['ip'];...$dev_ip = "54.87.54.87";if($ip === $dev_ip) {$content = file_get_contents($dst);echo $content;}

这道CTF题目需要参赛者访问内网127.0.0.1地址并获取存储于其中的Flag。

从代码中可见，题目将会判断参赛者传入的域名解析后的ip，并仅允许访问54.87.54.87地址的内容。

如何绕过题目中的条件语句，利用到的就是DNS重绑定攻击技术。

从上文代码段可见，程序通过以下代码来执行第一次DNS解析以获取ip：

$ip = @dns_get_record($res['host'], DNS_A)[0]['ip'];

假设此时参赛者传入的域名为www.a.com，将会进行如下的解析：

![](https://image.3001.net/images/20211025/1635148161_61766181eaac1a24f785a.jpg!small)

图 2首次DNS解析流程

此时www.a.com域名解析出来的ip为54.87.54.87。

程序继续往下执行，执行到了如下代码块：

$dev_ip = "54.87.54.87";

if($ip === $dev_ip){}

此时ip参数为54.87.54.87，满足条件分支判断，程序执行进入if条件分支。

随后，程序执行到如下语句：

$content = file_get_contents($dst);

注意，此时file_get_contents方法内的参数为参赛者控制的域名dst,而非ip地址。

也就是说，程序执行file_get_contents方法时，需要获取此域名的ip地址解析。由于攻击者将DNS
TTL设置的数值极其小，从程序第一次获取ip到执行file_get_contents方法处时，DNS缓存早已失效，CTF服务器此时需要重新发起域名解析请求以获取www.a.com的ip，此时参赛者修改DNS解析结果以完成DNS重绑定攻击，见下图：

![](https://image.3001.net/images/20211025/1635148496_617662d06a4eb164f2a23.jpg!small)

图 3重绑定DNS解析

此时获取到的解析ip值为127.0.0.1，参赛者通过此方式绕过限制并访问127.0.0.1资源，实现重绑定攻击。

##  **KuBernetes中DNS重绑定攻击的应用  
**

Kubernetes为了防止用户对Services，Pods，Nodes，StorageClass对象的内网Proxy进行非法访问，采用了域名解析的方式解析并校验Proxy请求的IP地址是否位于本地链路
(169.254.0.0/16) 或 localhost (127.0.0.0/8) 范围内。

Kubernetes通过此方式防止恶意内网资源的Proxy访问行为，但是Kubernetes在校验通过之后，会进行第二次域名解析，获取IP地址访问而不再进行IP地址的校验。

联想到上一章节的DNS重绑定攻击方式：攻击者可以控制DNS解析的IP地址，在第一次校验时返回一个合法值，随后在第二次获取IP地址时，返回一个本地链路或
localhost地址，详见下图：

![](https://image.3001.net/images/20211025/1635148282_617661faaa2629542e1c2.jpg!small)

图 4 Kubernetes中DNS重绑定流程

通过这个技术方式，攻击者可以绕过apiserver proxy的内网限制，构造恶意请求访问集群中的资源。

这种攻击技术将为云服务商带来了极大的安全问题：大多数云服务商提供Kubernetes托管版集群服务，采用此服务的用户Master节点将由云厂商创建并托管，如果攻击者通过方式访问到本地链路
(169.254.0.0/16) 或 localhost (127.0.0.0/8)地址，则有可能访问同为托管模式下其他用户的apiserver。

##  **CVE-2020-8562漏洞原理**

首先，使用云厂商提供的Kubernetes托管版集群服务创建一个集群。在此场景下，我们创建的集群的Master节点将与其他采用托管服务的用户一并，由云厂商创建并托管管理，这为后续的利用提供了先决条件。

![](https://image.3001.net/images/20211025/1635148320_61766220f14cd11d63a00.jpg!small)

图 5 Kubernetes托管版集群服务

在集群创建完毕后，通过编写如下yaml来创建一个名为cve-2020-8562的node，见下图：

![](https://image.3001.net/images/20211025/1635148339_617662332da2e18c0650e.jpg!small)

图 6 使用yaml创建node

通过上图可见，在此yaml中，将只能在集群内进行路由的节点的IP地址InternalIP设置为攻击者可控的www.attacker.com。

创建完毕后，可以通过kubectl get nodes查看到此节点：

![](https://image.3001.net/images/20211025/1635148352_61766240997e9e57a39ab.jpg!small)

图 7 通过kubetctl查看cve-2020-8562节点

从上图红框处可以发现，此时我们创建的cve-2020-8562节点的状态为NotReady，但即使此时cve-2020-8562节点的状态为NotReady，也并不影响后续的利用流程。

使用如下命令启动Kubernetes API 服务器的代理：

kubectl proxy &

![](https://image.3001.net/images/20211025/1635148368_617662502ad42a04cb911.jpg!small)

图 8 通过kebuectl开启代理

在成功启动Kubernetes API 服务器的代理之后，通过如下命令使用apiserver
proxy来访问cve-2020-8562节点的apiserver：

![](https://image.3001.net/images/20211025/1635148383_6176625f0664baeb14c73.jpg!small)

图 9访问cve-2020-8562节点的apiserver

通过上文来看，cve-2020-8562节点处于NotReady，我们可以正常的访问其apiserver吗？

我们来看一下Kubernetes是如何完成接下来的访问：

首先，为了可以访问cve-2020-8562节点，Kubernetes首先需要获取cve-2020-8562节点的InternalIP，我们通过如下指令查看一下cve-2020-8562
的InternalIP：

![](https://image.3001.net/images/20211025/1635148399_6176626f5492cdb1fb4d6.jpg!small)

图 10 查看cve-2020-8562节点详情

通过上图可知，cve-2020-8562节点的InternalIP值与生成此节点yaml中配置项一致，为我们配置的www.attacker.com。

由于InternalIP为域名而非IP地址，Kubernetes需要对其进行域名解析，随后校验获取到的IP地址是否位于本地链路
(169.254.0.0/16) 或 localhost (127.0.0.0/8) 范围内，如果获取到的IP属于此范围，则禁止访问。

在第一次DNS解析时，攻击者自建的DNS服务器将会返回一个合法的IP地址（非本地链路或 localhost范围），例如172.x.x.x，流程见下图：

![](https://image.3001.net/images/20211025/1635148417_6176628150c5b752f33ce.jpg!small)

图 11 第一次DNS解析

通过此方式，可以绕过k8s的本地链路/localhost范围IP校验。

在通过安全校验之后，K8s将会发起第二次域名解析。由于攻击者将DNS
TTL设置的数值极其小，此时DNS缓存已失效，k8s需要重新发起域名解析请求以获取www.attacker.com的ip地址，流程见下图：

![](https://image.3001.net/images/20211025/1635148433_6176629142d0420eda6d8.jpg!small)

图 12 DNS重绑定攻击

从上图可见，此时攻击者可以将
www.attacker.com域名的IP解析为一个localhost范围内的IP地址并返回，在此例中，我们返回一个127.x.x.x地址。

此时，k8s apiserver proxy访问情况可以类比于下图情况：

![](https://image.3001.net/images/20211025/1635148447_6176629f2e20321e4b124.jpg!small)

图 13当前访问可抽象成此情况

如果127.x.x.x这个节点的apiserver 存在未授权访问情况，我们就可以通过此方式直接访问其apiserver，见下图：

![](https://image.3001.net/images/20211025/1635148461_617662ad97c18a1d68476.jpg!small)

图 14 攻击者访问托管服务中Master

通过此方式，可以访问其他使用Kubernetes托管集群服务的租户的apiserver。

##  **总结**

在安全研究以及运维中，一些低风险的集群漏洞极其容易被安全以及运维人员所忽略，但是这些漏洞在一些特定场景中仍为云上安全带来了极大的安全挑战，正如本文中所举例的CVE-2020-8562安全漏洞，这个仅有2.2评分的Kubernetes安全漏洞，在与实际业务结合后，仍可为业务带来极大的安全风险。因此与云上安全相关的漏洞，无论严重与否，都应得到安全人员以及运维人员的相应重视。

###  **参考链接  
**

https://github.com/kubernetes/kubernetes/issues/101493

https://zhuanlan.zhihu.com/p/89426041

https://cloud.tencent.com/developer/article/1400018

