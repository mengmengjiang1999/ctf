# 背景

在 [k8s中各组件和kube
apiserver通信时的认证和鉴权](https://mp.weixin.qq.com/s/JLsNAKHPOUPsFqq506WbPg)中提到"NodeRestriction准入插件"，实际上它是一个"准入控制器"。

"准入控制器"是一个重要的概念，在istio、apisix、某些安全产品中都有用到。

本文简要记录一下以下内容：

  * "准入控制器"是什么

  * 怎么开启"准入控制器"

  * 从源码浅析"准入控制器"

>
> 本文使用的k8s集群是用[kubekey](https://github.com/kubesphere/kubekey/blob/master/README_zh-> CN.md)搭建，命令是./kk create cluster --with-kubernetes v1.21.5 --with-kubesphere
> v3.2.1

# 分析

## "准入控制器"是什么？

它有点类似"插件"，为apiserver提供了很好的"可扩展性"。

请求apiserver时，通过认证、鉴权后、持久化("api对象"保存到etcd)前，会经过"准入控制器"，让它可以做"变更和验证"。

"变更"可以修改"api对象"，比如istio用来实现pod注入。"验证"可以用来校验"api对象"，比如
校验当前集群是否有足够多的资源满足"api对象"、校验当前提交的"pod对象"是否合法。

## 怎么开启"准入控制器"？

    
    
    root@ip-172-31-14-33:~/kubernetes-1.21.5/_output/bin# ./kube-apiserver --help |grep admission-plugins
        ...
        --enable-admission-plugins strings       admission plugins that should be enabled in addition to default enabled ones (NamespaceLifecycle, LimitRanger, ServiceAccount, TaintNodesByCondition, Priority, DefaultTolerationSeconds, DefaultStorageClass, StorageObjectInUseProtection, PersistentVolumeClaimResize, RuntimeClass, CertificateApproval, CertificateSigning, CertificateSubjectRestriction, DefaultIngressClass, MutatingAdmissionWebhook, ValidatingAdmissionWebhook, ResourceQuota). Comma-delimited list of admission plugins: AlwaysAdmit, AlwaysDeny, AlwaysPullImages, CertificateApproval, CertificateSigning, CertificateSubjectRestriction, DefaultIngressClass, DefaultStorageClass, DefaultTolerationSeconds, DenyServiceExternalIPs, EventRateLimit, ExtendedResourceToleration, ImagePolicyWebhook, LimitPodHardAntiAffinityTopology, LimitRanger, MutatingAdmissionWebhook, NamespaceAutoProvision, NamespaceExists, NamespaceLifecycle, NodeRestriction, OwnerReferencesPermissionEnforcement, PersistentVolumeClaimResize, PersistentVolumeLabel, PodNodeSelector, PodSecurityPolicy, PodTolerationRestriction, Priority, ResourceQuota, RuntimeClass, SecurityContextDeny, ServiceAccount, StorageObjectInUseProtection, TaintNodesByCondition, ValidatingAdmissionWebhook. The order of plugins in this flag does not matter.
    

根据命令行帮助可以知道，默认会开启17个"准入控制器"。

    
    
    >>> a="NamespaceLifecycle, LimitRanger, ServiceAccount, TaintNodesByCondition, Priority, DefaultTolerationSeconds, DefaultStorageClass, StorageObjectInUseProtection, Persis
    tentVolumeClaimResize, RuntimeClass, CertificateApproval, CertificateSigning, CertificateSubjectRestriction, DefaultIngressClass, MutatingAdmissionWebhook, ValidatingAdmissionWebhook, ResourceQuota"
    >>> len(a.split(","))
    17
    

也可以用--enable-admission-plugins开启额外的"准入控制器"。

这些"准入控制器"介绍可以查看 [使用准入控制器](https://kubernetes.io/zh-cn/docs/reference/access-authn-authz/admission-controllers/)文档。在我的实验环境中，可以看到额外开启了`NodeRestriction准入控制器`，它实现了apiserver对kubelet请求的权限控制。

    
    
    root@ip-172-31-14-33:~# ps aux|grep kube-apis
    root      9567  4.8  7.8 1381988 613048 ?      Ssl  03:49  17:48 kube-apiserver ... --enable-admission-plugins=NodeRestriction ...
    

## 从源码浅析"准入控制器"

我们可以通过"断点调试"结合源码分析，验证前面说的两个结论：

  * 请求先经过认证、鉴权，然后经过"准入控制器"

  * 默认开启17个"准入控制器"；加上NodeRestriction就是18个

"认证、日志审计、鉴权"在apiserver中都是以filter的形式存在，而"准入控制器"有点像包装了一层servlet。

    
    
    func DefaultBuildHandlerChain(apiHandler http.Handler, c *Config) http.Handler {
    	handler := filterlatency.TrackCompleted(apiHandler)
    	handler = genericapifilters.WithAuthorization(handler, c.Authorization.Authorizer, c.Serializer) // 鉴权
    	...
    	handler = genericapifilters.WithAudit(handler, c.AuditBackend, c.AuditPolicyChecker, c.LongRunningFunc)  // 日志审计
    	...
      handler = genericapifilters.WithAuthentication(handler, c.Authentication.Authenticator, failedHandler, c.Authentication.APIAudiences) // 认证
    	...
    	return handler
    }
    

finishRequest函数中会开goroutine调用"准入控制器"  
![img](https://image.3001.net/images/20220704/1656905816_62c26058be4009818c6cd.png!small)

可以看到 admissionHandler切片长度是18，17个"默认开启的准入控制器"加上NodeRestriction  
![img](https://image.3001.net/images/20220704/1656905902_62c260ae996c28443f14c.png!small)

部分控制器代码在plugin/pkg/admission目录中，会实现Admit接口  
![img](https://image.3001.net/images/20220704/1656905947_62c260db707f42a22d868.png!small)

# 总结

  * 请求先经过认证、鉴权，然后经过"准入控制器"

  * 默认开启17个"准入控制器"；NodeRestriction不是默认开启的

默认开启的"准入控制器"中有两个很特殊的，ValidatingAdmissionWebhook和MutatingAdmissionWebhook。这两个控制器让apiserver有了更多的可扩展性，实现了"动态准入控制"。作者：leveryd

