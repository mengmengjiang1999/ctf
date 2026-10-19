在K8S架构中，安全是基础之一。安全策略是K8S安全架构中的强大的工具，用来降低K8S机器的安全风险、并实现K8S的安全配置和落地实施。本文中，虫虫带领大家一起学习K8S安全策略中的pod安全策略实施，我们以K8S官方的K8S
Pod安全建议为基础，介绍其安全策略的最佳实践。

![pod1.png](https://image.3001.net/images/20190916/1568614235_5d7f275be8031.png!small)  

# K8S pod安全策略介绍

K8S pod安全策略是K8S的配置，该配置定义了K8S
pod必须满足的安全相关的条件。只有满足这些条件的pod，才能别加入到集群。这些条件规定了pod如何和网络、存储等资源进行交互，并定义对这些资源基于角色的访问控制。

![pod2.png](https://image.3001.net/images/20190916/1568614246_5d7f27669c9e4.png!small)  

K8S
pod安全策略，也可以看作是K8S集群上运行的自动化一致性测试方法。我们知道一致性测试作为一种策略，用于确保环境或应用程序在运行之前必须满足的安全标准。K8S
pod安全策略确保pod加入集群之前必须满足策略中定义的安全要求。和一致性测试不同的是，K8S pod安全策略无需专门运行，配置的策略会被K8S自动执行。

# K8S pod安全策略实例级、集群级的资源

K8S
pod安全策略的作用范围是整个K8S实例，是集群级的资源。通过PodSecurityPolicy对象来控制并应用到各个pod和容器SecurityContext上，并非对单个Pod而言。

# pod安全策略配置

![pod3.png](https://image.3001.net/images/20190916/1568614264_5d7f27785ea28.png!small)  

和其他资源一样Pod安全策略也通过YAML文件中指定。pod安全策略可以指定的参数和控制范围包括：

privileged：已授权容器的运行

主机命名空间，包括 hostPID和hostIPC

主机网络和端口，包括hostNetwork和hostPorts

volumes：控制卷类型

allowedHostPaths：主机文件系统

allowedFlexVolumes：FlexVolume驱动白名单列表

fsGroup：分配拥有 Pod 数据卷的 FSGroup

runAsUser, runAsGroup, supplementalGroups：容器的用户和组

allowPrivilegeEscalation, defaultAllowPrivilegeEscalation：root提权限制

defaultAddCapabilities, requiredDropCapabilities, allowedCapabilities：Linux能力

seLinux：容器的SELinux

allowedProcMountTypes：容器允许的Proc Mount类型

annotations：容器使用的AppArmor或seccomp安全角色

forbiddenSysctls,allowedUnsafeSysctls：容器使用的sysctl角色

# 配置实例

下面是一个pod安全策略配置的实例：

    
    
    apiVersion: policy/v1beta1
    kind: PodSecurityPolicy
    metadata:
      name: example
    spec:
      privileged: false  # Don't allow privileged pods!
      # The rest fills in some required fields.
      seLinux:
        rule: RunAsAny
      supplementalGroups:
        rule: RunAsAny
      runAsUser:
        rule: RunAsAny
      fsGroup:
        rule: RunAsAny
      volumes:
      - '*'
    

# 激活安全策略

配置好pod安全策略后，需要使用kubectl激活：

    
    
    kubectl create -f example.yaml
    

# 获取实例策略

为了获取已存在策略列表，可以用 kubectl get：

    
    
    kubectl get example
    NAME PRIV CAPS SELINUX RUNASUSER FSGROUP SUPGROUP READONLYROOTFS VOLUMES
    permissive false [] RunAsAny RunAsAny RunAsAny RunAsAny false [*]
    privileged true [] RunAsAny RunAsAny RunAsAny RunAsAny false [*]
    restricted false [] RunAsAny MustRunAsNonRoot RunAsAny RunAsAny false [emptyDir secret downwardAPI configMap persistentVolumeClaim projected]
    

# 修改安全策略

通过交互方式修改策略，使用 kubectl edit。

    
    
    kubectl edit example permissive
    

该命令将打开默认文本编辑器，并通过它修改策略。

# 删除安全策略

删除安全策略也非常简单，通过 kubectl 命令删除它：

    
    
    kubectl delete example permissive
    podsecuritypolicy "permissive" deleted
    

# K8S pod安全策略实践

![6587b66fc5744f93a15580bd7968a57c](http://p1.pstatp.com/large/pgc-image/6587b66fc5744f93a15580bd7968a57c)

为了充分利用K8S pod安全策略，大家需要根据各自的K8S和pod集群环境以实际需求中具体问题具体配置，下面是我没建议的最佳pod安全策略实践方法。

# 启用pod安全策略

首先，确保启用Kubernetes pod安全策略。有些Kubernetes发行版默认情况下不会启用pod安全策略，这会有严重的安全隐患。

# 禁用特权容器

Kubernetes
pod中，容器可以以"特权"模式运行，这样容器内的进程可以不受限制地访问主机系统的资源。虽然某些用例需要这种访问级别，但这会带来严重的安全风险。

在Kubernetes pod安全策略禁止特权容器的运行，配置如下：

    
    
    apiVersion: policy/v1beta1
    kind: PodSecurityPolicy
    metadata:
    name: prevent-privileged-containers
    spec:
    privileged: false
    

# 只读文件系统

另一个很有用的安全实践是让容器以只读文件系统运行。该策略有助于实施不可变的基础架构策略，可以极大的减轻恶意进程在容器内存储或操纵数据的风险。

该策略的配置如下：

    
    
    apiVersion: policy/v1beta1
    kind: PodSecurityPolicy
    metadata:
    name: read-only-fs
    spec:
    readOnlyRootFilesystem: true
    

可以肯定的是，只读文件系统并非适用任何情况，如果你没有充足的理由必须修改容器内部数据，可以使用该策略。

# 防止提权

对于大多数管理员来说，权限提升代表安全隐患。默认情况下Kubernetes并下会阻止容器提权，为了禁止群集上的提权，必须配置下面的策略：

    
    
    apiVersion: policy/v1beta1
    kind: PodSecurityPolicy
    metadata:
    name: no-privilege-escalation
    spec:
    allowPrivilegeEscalation: false
    

# 防止容器以root身份运行

以root用户身份运行容器，是常见但是非常错误的方法。如果没有充分的理由，重要事情说三遍：请不要以root身份运行容器。请不要以root身份运行容器。请不要以root身份运行容器！

禁止root运行容器的策略如下：

    
    
    apiVersion: policy/v1beta1
    kind: PodSecurityPolicy
    metadata:
    name: no-privilege-escalation
    spec:
    MustRunAsNonRoot: true
    

# 打包以上策略

Kubernetes pod安全策略是配置在一个文件中，我们可以把以上策略打包在一起：

    
    
    apiVersion: policy/v1beta1
    kind: PodSecurityPolicy
    metadata:
    name: example
    spec:
    privileged: false
    spec:
    readOnlyRootFilesystem: true
    spec:
    allowPrivilegeEscalation: false
    spec:
    MustRunAsNonRoot: true
    

# 更多安全策略实例：

下面是K8S官方限制性策略的示例，要求用户以非特权用户身份运行，阻止可能的root提权，并启用多种安全机制：

    
    
    apiVersion: policy/v1beta1
    kind: PodSecurityPolicy
    metadata:
    name: restricted
    annotations:
    seccomp.security.alpha.kubernetes.io/allowedProfileNames: 'docker/default,runtime/default'
    apparmor.security.beta.kubernetes.io/allowedProfileNames: 'runtime/default'
    seccomp.security.alpha.kubernetes.io/defaultProfileName: 'runtime/default'
    apparmor.security.beta.kubernetes.io/defaultProfileName: 'runtime/default'
    spec:
    privileged: false
    # 禁止提权到root
    allowPrivilegeEscalation: false
    # 对于非root+disallow的提权，提供深度防御requiredDropCapabilities:
    - ALL
    # 允许核心的volume类型
    volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    #persistentVolumes由cluster管理安全使用.
    - 'persistentVolumeClaim'
    hostNetwork: false
    hostIPC: false
    hostPID: false
    runAsUser:
    # 容器非root运行
    rule: 'MustRunAsNonRoot'
    seLinux:
    # nodes使用AppArmor
    rule: 'RunAsAny'
    supplementalGroups:
    rule: 'MustRunAs'
    ranges:
    # 禁止添加root组
    - min: 1
    max: 65535
    fsGroup:
    rule: 'MustRunAs'
    ranges:
    # 禁止添加root组
    - min: 1
    max: 65535
    readOnlyRootFilesystem: false
    

更多的实例可以看考K8S官方文档（https://kubernetes.io/docs/concepts/policy/pod-security-policy/）。  

# 结论

K8S pod安全策略提供提供了便捷、强大、自动化集群安全配置的方法。通过它可以极大的提高K8S的安全性，减少不必要的风险。

