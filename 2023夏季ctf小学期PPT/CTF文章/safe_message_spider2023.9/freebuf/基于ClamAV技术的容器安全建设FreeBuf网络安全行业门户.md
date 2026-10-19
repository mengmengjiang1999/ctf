# 概述

随着云原生技术被越来越多的企业使用，容器作为云原生技术架构最重要的基础组件之一，容器自身是否存在安全风险、是否提供足够的安全机制来保障业务安全问题运行，成为了企业实践云原生架构最大的绊脚石之一。试想，如果容器存在一个严重漏洞，那么基于容器的一切数据甚至是运行容器的宿主机，将被攻击者控制。

据《Sysdig 2022
云原生安全和使用报告》显示，超过75%的运行容器存在高危或严重漏洞、62%的容器被检测出包含shell命令、76%的容器使用root权限运行。

那么如何发现这些危险的容器、如何发现容器中是否包含恶意文件了？这篇文章试着提供一个基于ClamAV的容器安全建设方法，供大家参考。

# ClamAV介绍

ClamAV是一个开源病毒扫描工具，最近发布了1.0正式版本，稳定性有了很大提升，同时，ClamAV也从0.96版本支持针对容器的规则编写，具体规则编写方法，可以参考[官方文档](https://docs.clamav.net/manual/Signatures/ContainerMetadata.html)。

新版ClamAV的安装过程有几个需要注意的地方：

  1. Linux环境如果不存在ClamAV用户名、用户组，则直接手动创建即可。
  2. 运行是如果提示目录不存在，手动创建后，设置为ClamAV用户可读写。
  3. 根据官方文档生成配置文件后，需要打开配置文件，删除无用的Example那一行，不然运行是会报错。

# ClamAV更新规则库

由于ClamAV官方不在提供更新规则库连接，因此，很多网上的方法都无法使用，这地方，直接介绍一个最简单的办法。

  1. 下载安装cvdupdate工具：`pip install cvdupdate`
  2. 运行cvdupdate命令更新规则库：`cvdupdate update`
  3. 启动规则库私服：`cvdupdate serve`
  4. 打开freshclam配置文件: /usr/local/etc/freshclam.conf，找到PrivateMirror配置项，取消前面的注释，如果第三步的私服和clamav在一台机器，则可以配置为：`PrivateMirror localhost:8000`
  5. 运行freshclam命令导入clamav规则

# ClamAV扫描容器

ClamAV扫描方式有两种

  1. daemon方式：先运行clamd daemon进程，然后使用clamdscan把要扫描的对象传给clamd daemon扫描。
  2. cli方式：使用clamscan命令，指定目标扫描。  
为简单演示，本篇文章使用clamscan cli方式进行扫描。

  3. 导出容器镜像文件  
与Trivy不同的是，ClamAV需要对容器里的文件内容进行扫描，所以，在扫描之前，我们需要先把容器镜像导出来，比如我们导出名为：vibersastra/ubuntu的镜像：  
`docker save -o ubuntu.tar vibersastra/ubuntu:latest`

  4. 解压扫描容器镜像  
解压上一步导出的镜像文件：`tar xvf ubuntu.tar`，假设我们解压到了temp目录，则可以使用 `clamscan -r
temp`进行扫描(-r表示递归扫描)，扫描结果如下：

![](https://image.3001.net/images/20221221/1671591569_63a27691ae04a18c6d24e.jpg!small)

通过ClamAV，可以成功发现容器中包含的挖矿病毒文件。

tips：由于clamscan每次都需要load一次规则库文件，导致每次开始扫描都很慢，在正式的环境中，建议使用daemon方式运行。

# 与Trivy结合实现安全左移

到这，我们已经学会了ClamAV的使用，接下来，如何使用ClamAV实现安全左移，把安全问题发现在业务上线前了？

Trivy这个工具，相信很多了解容器安全的小伙伴都在用，通过Trivy可以发现容器镜像的安全漏洞，包括容器里的静态代码。但是Trivy是一个发现漏洞的工具，至于容器镜像里是否存在恶意样本，比如远控病毒、挖矿木马等，Trivy是无法发现的，一个典型的Trivy扫描容器的接入如下：

![](https://image.3001.net/images/20221221/1671591571_63a2769371891e2b1e4e4.png!small)

所以，我们可以通过综合使用Trivy和ClamAV，来保障容器运行时的安全：

  * trivy：确认容器无漏洞，从而无法被攻击。
  * clamav：保证容器运行时无恶意文件，从而杜绝供应链攻击。

# 结语

随着使用docker的企业越来越多，容器防病毒也将会得到更多的关注，这在一定程度上可以借鉴主机安全建设的思路，但容器的灵活性，注定无法像主机那样部署Agent，更多的还是依赖宿主机层面的Agent，实现对容器的安全扫描，从而排除安全风险。

