**AWS Transit Gateway是一项服务，可以将用户的 AmazonVirtual Private Clouds (VPC)
和本地网络连接到一个网关（AWS TransitGateway简称TGW，下文会混用这两个词，但实质就是一样的意思）。随着 AWS
上运行的工作负载数量不断增加，必须能够跨多个账户和 Amazon VPC 扩展您的网络，才能跟上发展步伐。现在，您可以使用对等连接 Amazon VPC
对。但是，如果无法集中管理连接策略，那么管理众多 AmazonVPC 之间的点对点连接会带来高昂运营成本而且十分繁琐。当 VPC
数量增加到数百时，构建此解决方案可能非常耗时，而且难以管理。**

借助 AWS Transit Gateway，只需创建和管理一条连接，这条连接从中央网关连接到您网络中的每个 Amazon
VPC、本地数据中心或远程办公室。Transit Gateway
充当中心，控制流量在所有连接的网络（相当于辐射网络）之间的路由方式。这种中心和辐射模型大大简化了管理工作并降低了运营成本，因为每个网络只需连接到
Transit Gateway，而无需连接到其他所有网络。任何新的 VPC 只需连接到 Transit Gateway，便可自动与连接到 Transit
Gateway 的其他所有网络建立连接。这种连接的简便性可以随着网络发展轻松扩展网络。

TGW可以支持同一Region里的VPC互联，也可以跨Region进行VPC互联，同时也支持VPN的互联，下文中的实践是基于同一Region里的VPC互联，之后会再继续编写跨Region与VPN互联的实践方案。

PS：TGW之前在AWS中国平台上还没有这项服务，但前不久发现在AWS中国里也支持此项目功能了，但只支持VPC的互联，应该暂时还不支持跨Region的Peering
Connection与VPN模式。因此本次只基于VPC的互通，考虑到访问速度的原因使用的平台是AWS中国。

在没有使用TGW时，如果有多个VPC需要进行互联，拓扑如下，每个VPC之间都需要建立对等连接，增加了扩展难度。同时如果在VPC数量非常庞大的情况下配置将会非常的复杂，管理起来也很混乱。

![](https://image.3001.net/images/20200211/1581396637_5e42329d0f48d.png!small)

如果使用了TransitGateway方案后将会简化很多，形成一个VPC间的Hub-Spoke架构，只需将各个VPC连接至AWS Transit
Gateway，该服务就会在各个VPC之间路由流量了，简化了VPC连接方式，拓扑如下：

![](https://image.3001.net/images/20200211/1581396649_5e4232a9d0c98.png!small)

我们可以把此拓扑再演变一下，如下图：

![](https://image.3001.net/images/20200211/1581396665_5e4232b9b6dae.png!small)

通过一些相关配置可以实现所有VPC1~VPC4都可以访问Share_VPC，同时仍然保持VCP1~VPC4之间的隔离性。

## 应用场景

### 全网VPC互连

构建跨数千个VPC的应用程序，无需承担管理分布式网络的运营负担。通过对等连接和管理成百上千个 VPC
需要大量路由表，这很难部署、管理，并且容易出错。现在，要配置的路由要少得多，因为您只需配置到 AWS Transit Gateway 的路由，而不是到每个
VPC 的路由。

### 应用共享

可以在所有 Amazon VPC 之间轻松共享 AWS 服务，如 DNS、ActiveDirectory 和 IPS/IDS。

### 负载均衡

TGW支持负载均衡，当需要高带宽连接时，TGW还支持ECMP负载均衡模式，来提供链路带宽，轻松满足带宽扩容能力。

### 安全防护

任何VPC之间的访问都必须通过TGW路由至一个安全VPC（可以在里面部署防火墙、WAF等安全设备）进行中转，以此来进行安全防护功能。

### 集中审计与管理

可以单独部署一个集中审计与管理的VPC，通过TGW与所有VPC进行连接，此时可以方便的进行日志审计与集中管理，对于一些态势感知或是SIEM等应用也同样适应。

### 蜜罐部署

把蜜罐放置在一个公共VPC中，通过TGW可以让所有VPC都可以访问部署了蜜罐的VPC，以此解决连接性问题。

## AWS TransitGateway配置实战

### 网络拓扑：

![](https://image.3001.net/images/20200211/1581396683_5e4232cb48e5a.png!small)

### 实验目的：

在实现VPC1与VPC2安全隔离的同时都可以访问VPC_Core里的实例。

### 配置步骤

VPC配置（配置略），配置了3个VPC，分别为VPC1、VPC2、VPC_Core

![](https://image.3001.net/images/20200211/1581396699_5e4232db0dff4.png!small)

基于VPC分别创建相应的VPC子网（配置略）

![](https://image.3001.net/images/20200211/1581396709_5e4232e5efe03.png!small)

分别为每个VPC创建相应的IGW，并且配置IGW的缺省路由，以使其可以访问Internet（配置略）

![](https://image.3001.net/images/20200211/1581396722_5e4232f29d2a9.png!small)

VPC1的IGW路由配置

![](https://image.3001.net/images/20200211/1581396731_5e4232fb41354.png!small)

VPC2的IGW路由配置

![](https://image.3001.net/images/20200211/1581396746_5e42330accb95.png!small)

VPC_Core的IGW路由配置

![](https://image.3001.net/images/20200211/1581396757_5e4233159b1cc.png!small)

### 创建EC2实例

分别在VPC1与VPC2里创建两个EC2实例，在VPC_Core里创建一个EC2实例

![](https://image.3001.net/images/20200211/1581396773_5e42332547082.png!small)

EC2实例标签与私网地址如下：

> VPC1_Subnet1_EC2A：192.168.0.151
>
> VPC1_Subnet2_EC2A：192.168.1.20
>
> VPC2_Subnet1_EC2A：172.16.0.250
>
> VPC2_Subnet2_EC2A：172.16.1.81
>
> VPC_Core_EC2A： 10.1.1.14

### 创建TGW（TransitGateways）

![](https://image.3001.net/images/20200211/1581396786_5e423332e122a.png!small)

![](https://image.3001.net/images/20200211/1581396793_5e423339c263d.png!small)

等待TGW状态从pending变为available后，则说明TGW创建完成

![](https://image.3001.net/images/20200211/1581396807_5e4233470f913.png!small)

Transit Gateway Attachments

### 把新创建的TGW与VPC进行关联

![](https://image.3001.net/images/20200211/1581396822_5e4233567aeb7.png!small)

![](https://image.3001.net/images/20200211/1581396828_5e42335c172c7.png!small)

分别把所有VPC与TGW进行关联。等待Attachment变化available后则说明生效。

![](https://image.3001.net/images/20200211/1581396841_5e423369b71fb.png!small)

### TGW路由配置

通过路由表的配置实现VPC1、VPC2与VPC_Core的互连，同时保持VPC1与VPC2的隔离。

增加VPC1路由表的配置，使VPC1可以访问VPC_Core 10.1.1.0/24网段。

![](https://image.3001.net/images/20200211/1581396860_5e42337c3f57a.png!small)

![](https://image.3001.net/images/20200211/1581396864_5e423380eec8a.png!small)

![](https://image.3001.net/images/20200211/1581396869_5e4233852d68a.png!small)

同理，添加VPC2至VPC_Core10.1.1.0/24的TGW路由

![](https://image.3001.net/images/20200211/1581396880_5e42339064bdc.png!small)

添加VPC_Core至VPC1 192.168.0.0/16与VPC2 172.16.0.0/16的TGW路由

![](https://image.3001.net/images/20200211/1581396891_5e42339be8ad6.png!small)

到此所有配置完成，查看TGW的TransitGateway route
Tables的路由表，TGW里有至所有VPC（VPC1、VPC2）的路由，由此可以实现VPC间Hub-Spoke的连接，但是VCP1与VPC2的路由表里只有至VPC_Core的路由。

![](https://image.3001.net/images/20200211/1581396908_5e4233acc406b.png!small)

 ***本文作者：ZhiXian，转载请注明来自FreeBuf.COM**  

