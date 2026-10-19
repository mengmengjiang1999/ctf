***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

 **![blog-145-article-var2.jpg](https://image.3001.net/images/20190720/1563586191_5d326e8fea0b2.jpg!small)**

**每周，我们都会收到大量关于新数据或个人数据泄露的消息。这使得网络安全也成为了任何IT项目的首要任务。黑客的攻击模式和工具不断创新和改进。因此，密切关注新的威胁防护工具显得尤为重要。**

保护网络安全的方法之一是设置蜜罐。在本文中，我们将向你展示如何在Kubernetes集群中创建，配置和部署一个蜜罐诱饵。

我们将继续与你分享我们与[Kubernetes](https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/)的工作经验，Kubernetes是一个用于部署，扩展和管理容器化应用程序的开源框架。在[之前的文章中](https://www.apriorit.com/dev-blog/616-web-virtualization-getting-started-with-kubernetes)，我们也专门讨论过了Kubernetes的基础架构和关键组件。

## 蜜罐简介

众所周知，[蜜罐](https://en.wikipedia.org/wiki/Honeypot_\(computing\))是一种网络安全机制，用于检测和对抗黑客攻击。这是一个置于网络内部的诱饵，它将自己伪装成敏感的资产或网络漏洞。当攻击者试图访问这些伪造的机密数据时，蜜罐会记录并通知该行为。蜜罐还会收集和分析有关黑客攻击的数据。

![1.jpg](https://image.3001.net/images/20190720/1563586214_5d326ea66944d.jpg!small)

蜜罐配置有两种类型：

1、生产蜜罐主要由公司使用。它们可以提高企业系统的安全性，仅保护黑客最有可能访问的数据。生产蜜罐更易于部署和维护，因为它们主要用于分散攻击者的注意力。

2、研究蜜罐主要由网络安全研究人员，政府和军事组织使用。研究蜜罐的目标不是阻止黑客，而是研究新的威胁和攻击模式。

我们还可以将蜜罐分为：

> 低交互蜜罐，只复制最常见的攻击服务。
>
> 高交互蜜罐，复制所有系统服务。
>
> 纯蜜罐，是生产系统的完整副本，不包含任何的敏感数据。

在部署蜜罐之前，让我们回顾一下我们在本教程中需要使用到的Kubernetes元素。

## 基本 Kubernetes 元素

Kubernetes是一个开源的，用于管理云平台中多个主机上的容器化的应用。我们在之前的一篇文章中，已经仔细研究和探讨了它的架构和功能。它包含有大量的内置工具。在本教程中，我们将只使用以下四个组件

> [Pod](https://kubernetes.io/docs/concepts/workloads/pods/pod-overview/) \-> 一个基本的Kubernetes单元，用于为存储的容器建模主机并创建容器运行的环境
>
> 集群（Cluster） -> 运行容器化应用程序的一组[节点](https://kubernetes.io/docs/concepts/architecture/nodes/)
>
>
> [ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)
> \-> 一个副本控制器，用于确保在任何给定时刻运行所需数量的容器。ReplicaSet定义有多个字段，其中包含有关此控制器应保留的Pod类型和数量的信息以及用于创建新Pod的模板。
>
>
> 部署（[Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)）
> - 负责Pods和ReplicaSet的声明性更新的控制器。部署控制器需要描述所需的状态才能维护这两个实体。

尽管功能丰富，但Kubernetes的使用却非常的简单。它允许你操作高级实体（如，部署和[StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)），而无需直接与Pod交互。

Kubernetes集群使用[仪表板](https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/)或称为kubectl的嵌入式命令行工具进行管理。在本文中，我们使用[kubectl](https://kubernetes.io/docs/reference/kubectl/overview/)在Kubernetes集群中部署蜜罐系统，并收集有关基础架构当前状态的数据。

![2.jpg](https://image.3001.net/images/20190720/1563586231_5d326eb7ef374.jpg!small)

## 在 Kubernetes 中部署蜜罐

在了解了蜜罐和Kubernetes的基础知识后，现在让我们开始在Kubernetes集群中创建蜜罐系统。

定义受保护的边界：

让我们开始通过定义我们想要保护的资源来建立蜜罐。Kubernetes文档包含了WordPress和MySQL部署的示例。我们可以使用此[示例](https://kubernetes.io/docs/tutorials/stateful-application/mysql-wordpress-persistent-volume/)中的应用程序和部署文件。
假设我们的Kubernetes网络包含我们想要保护的敏感数据。

创建 MySQL 蜜罐：

我们需要选择保护敏感数据的方法。最好的方法是创建一个MySQL服务诱饵。

为此，我们需要使用到MySQL蜜罐。在我们的教程中，我们将使用这个低交互蜜罐示例，你也可以使用你喜欢的任何其他模板。

在开始之前，我们必须确保[示例](https://github.com/skyformat99/mysql-honeypotd)蜜罐正常工作。让我们下载存储库：然后，我们需要创建Kubernetes文档中描述的依赖项：

    
    
    > git clone https://github.com/skyformat99/mysql-honeypotd ./honeypot

然后，我们需要创建Kubernetes文档中描述的依赖项：

    
    
    > apt-get install libev-dev

编译项目：

    
    
    > make

如果kubectl没有返回任何错误，则我们可以启动该项目：

    
    
    > ./mysql-honypotd -s 5.6 -n mysql-replica

命令执行后，MySQL蜜罐将启动并运行。现在，我们需要使用以下命令连接到它：

    
    
    > mysql -root -h [host-IP]  
      
    ERROR 1045 (28000): Access denied for user ‘user’@’ip’

蜜罐回应了我们的请求，这说明蜜罐已准备就绪。让我们来查看下它的日志：

    
    
    mysql-replica: New connection from IP:PORT to host-IP
    
    mysql-replica: Access denied for user ‘user’ from IP:PORT to  host-IP:3306
    
    mysql-replica: Closing connection for IP:PORT

该记录表示我们的蜜罐运行一切正常。下一步是将蜜罐添加到Kubernetes集群。

创建蜜罐 Docker 镜像：

在Kubernetes集群中启动我们的蜜罐之前，我们需要创建一个Docker镜像。稍后我们将需要用它来启动Pod。

你可以通过以下四个简单的步骤来创建Docker镜像：

> 1、选择一个基本容器（在我们的示例中，将使用Ubuntu 14.04）。
>
> 2、设置一个工作目录并将蜜罐复制到该目录。
>
> 3、创建依赖项。
>
> 4、设置入口点。

所有这些步骤都需要记录在Docker文件中：

    
    
    FROM ubuntu:14.04
      
    WORKDIR /tmp/honeymsql
    COPY . ./
      
    RUN apt-get update
    RUN apt-get install libev-dev
      
    ENTRYPOINT [“./mysql-honypotd”]

现在，我们需要创建一个Docker镜像：

    
    
    > docker build -f ./Dockerfile -t mysql-honeypot:1 

构建完成后，我们的本地Docker镜像就可以使用了。为了创建一个Pod，我们必须将这个Docker镜像上传到Docker Hub：

    
    
    > docker push dockerID/repositoryName

此时，我们已在Pod中创建了一个MySQL蜜罐。

将蜜罐添加到 Kubernetes：

Pod的所需状态由我们前面讨论过的Deployment对象维护。开始部署之前，我们需要先创建一个[YAML](https://en.wikipedia.org/wiki/YAML)文件。基于此，Deployment自动控制Pod的状态。如有需要，我们可以使用ReplicaSet运行多个蜜罐。

编写YAML文档，你可以参考[Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)文档。我们项目的声明如下：

    
    
    apiVersion: extensions/v1beta1
    kind: Deployment
    metadata:
      name: mysql-replica
    spec:
      replicas: 1
      template:
       metadata:
         labels:
       app: mysql-replica
       spec:
         containers:
         - name: mysql-replica
       image: dockerID/repo:tag
       imagePullPolicy: Always
       args: ["-s 5.6"]
       securityContext:
                privileged: true

让我们注意这个声明中的两行字符串：

    
    
    image: dockerID/repo:tag

这一行是指我们之前为了构建Pod而创建的Docker镜像。请注意，如果你使用私有存储库，则需要创建一个额外的Secrets对象，该对象将存储访问令牌到镜像。

    
    
    args: ["-s 5.6"]

该行定义了我们已启动的应用程序的参数。我们可以在创建Docker镜像时在入口点定义它们。但是这种方法不允许在未重构镜像的情况下更改参数。

在创建Pod时声明参数使得设置应用程序的过程更加灵活。

让我们保存文件并创建一个Deployment资源：

    
    
    > kubectl create -f honeypot-deployment.yaml

现在，我们需要检查Pod的状况：

    
    
    > kubectl get pods
    
    mysql-replica-5895cb77dd-9ltrr 1/1 Running 0 2m

使用以下命令查看蜜罐是否按预期工作：

    
    
    > mysql -root -h [POD-IP]
    
    ERROR 1045 (28000): Access denied for user ‘user’@’ip’ {/code}

最后，让我们来看看蜜罐日志：

    
    
    > kubectl logs mysql-replica-5895cb77dd-9ltrr
    
    mysql-honeypotd[1]: New connection from IP:PORT to [POD-IP]:3306
    
    mysql-honeypotd[1]: Access denied for user 'user from IP:PORT to POD-IP:3306
    
    mysql-honeypotd[1]: Closing connection for IP:PORT

任务完成！我们已成功在Kubernetes集群中创建，配置和部署了低交互蜜罐。

## 总结

在本教程中，我们向大家描述了如何在Kubernetes网络中部署蜜罐的过程。此类诱饵陷阱对于我们研究黑客的攻击模式，以及保护我们的敏感数据非常有用。而创建蜜罐诱饵的过程也非常简单，你只需具备一些基本的知识，就可以通过简单的四个步骤将蜜罐添加到你的Kubernetes基础架构中。

我们创建的MySQL诱饵是蜜罐技术的一个很好的例子。但是，蜜罐无法有效抵御零日攻击。因此，蜜罐可以成为你额外的网络安全工具，但你却不能完全的依赖与它。

 ***参考来源：[apriorit](https://www.apriorit.com/dev-blog/619-web-cybersecurity-honeypots-in-kubernetes)，FB小编secist编译，转载请注明来自FreeBuf.COM**

