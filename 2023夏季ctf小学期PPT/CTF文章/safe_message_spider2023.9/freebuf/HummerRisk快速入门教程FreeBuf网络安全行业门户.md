## 1、一键部署

1\. 部署服务器要求

  * 操作系统要求：任何支持 Docker 的 Linux x64
  * CPU内存要求：最低要求 4C8G，推荐 8C16G
  * 部署目录空间（默认/opt目录）要求： 50G
  * 网络要求：可访问互联网（如遇内网环境，理论上除公有云安全检测、Github源码检测外，其他功能可照常使用）

2\. 执行以下脚本进行一键安装：curl -sSL
https://github.com/HummerRisk/HummerRisk/releases/latest/download/quick_start.sh
-o quick_start.sh

3\. HummerRisk 是一款 B/S 架构的产品，即浏览器/服务器结构，在服务器安装完成后，客户端通过浏览器访问以下地址，即可开始使用。

  * http://目标服务器 IP 地址：服务运行端口，例如：http: 82.157.130.20:80（默认端口为80，用户可在安装时自定义）
  * 使用默认用户名 admin 密码 hummer 进行登录。

## 2、模块介绍

HummerRisk 主界面后可以看到界面左侧导航栏，有【首页】【混合云安全】【云原生安全】【任务编排】【检测管理】【系统设置】六大模块  
![2338041f-7820-496c-a311-e7767a64957d.jpg](https://image.3001.net/images/20221109/1667975506_636b4952915e26f4d640e.jpg!small)

## 3 、快速上手

### 3.1 场景一：混合云安全

### 3.1.1 绑定账号

添加/编辑云账号

  * 进入云账号设置页面，首先需要绑定多云的账号信息（Access Key ID / Access Key Secret）。
  * 点击左上角「创建云账号」按钮，可以添加云账号。
  * 通过对应的云平台，获取账号信息（一般为AK/SK），填写信息并绑定，自动获取区域和认证等信息。
  * 更详细的账号配置操作请参考 多云检测

![0c065426-214c-4abc-abc1-e7209511b3c8.jpg](https://image.3001.net/images/20221109/1667975507_636b4953614133064a388.jpg!small)

  * 绑定完成后系统会自动校验账号的状态，状态显示为『有效』时即为绑定成功。
  * 点击账号列表中操作按钮的第三个「编辑」，对已绑定的账号进行编辑。

![530af73a-12a6-4b6f-89c9-430609324cf5.jpg](https://image.3001.net/images/20221109/1667975508_636b49543c0c6c93baf7f.jpg!small)

云账号调参 因为检测规则的参数可以灵活配置，不同的云账号可以有不同的安全合规标准，所以在此页面用户可以根据自身需求自定义规则的参数与任意区域。

  * 通过账号列表第二个调参按钮，打开云账号调参页面。
  * 保存参数后，执行检测将优先执行当前调参内容，而且在调参页面可以快速执行某一规则的某些区域快速检测。（注：不设置调参内容不影响检测，检测内容为内置默认参数和所有待检测区域）

![1f2967d6-92d5-4ea4-8003-f3409e1ef54c.jpg](https://image.3001.net/images/20221109/1667975508_636b4954ee0a1db8d7816.jpg!small)

### 3.1.2 执行检测

基于规则组进行检测

  * 多云检测基于规则组进行场景检测的，例如检测 Aliyun ECS 最佳安全实践，将检测此规则组下一系列规则，达到覆盖场景的目的。 有两种方式可以快速开始检测：
  * 通过云账号列表第一个「一键检测」按钮选取多个规则组执行一键检测。
  * 在规则组页面，选择希望执行的规则，选取某个云账号执行快速检测。

![e9910c4a-b479-41c1-b526-a9dfd47b0f9d.jpg](https://image.3001.net/images/20221109/1667975509_636b4955a2003d7c67f14.jpg!small)![ffaa97b0-76fb-4d70-bcc5-6f73c99212aa.jpg](https://image.3001.net/images/20221109/1667975510_636b49566a321a0ed7b4e.jpg!small)  
云资源检测结果

  * 在点击上述一键检测后，将自动跳转云资源检测结果页面，检测结果将会显示正在执行。
  * 等待检测执行完毕后获得检测结果的安全合规信息与优化建议。

![dfe7bc99-c519-4b06-9e65-4f91d554a4bf.jpg](https://image.3001.net/images/20221109/1667975511_636b49572b18d06048d51.jpg!small)

  * 漏洞检测主要用于扫描网络信息安全，通过设置目标地址信息即可。
  * 绑定的目标地址可以是域名，也可以是 IP + 端口。

![ff9a4c44-2f99-453c-98df-55a0cade557b.jpg](https://image.3001.net/images/20221109/1667975511_636b4957cc21e9f23202f.jpg!small)

  * 完成上述漏洞设置后，点击一键检测，将自动跳转漏洞检测结果页面，检测结果将会显示正在执行。
  * 等待检测执行完毕后，获得检测结果的漏洞信息与优化建议。

![c13a6a9f-5072-42ab-a705-d45885d9bc09.jpg](https://image.3001.net/images/20221109/1667975512_636b49587348e5d355d4f.jpg!small)

### 3.1.3 查看报告

云资源合规报告

  * 待云资源检测完毕后，根据检测结果生成合规报告，用户可查看和下载合规报告。 详细的合规报告相关操作，请参考文档的 多云检测

![25123bd9-eba6-485a-b147-8fafdab0bb3a.jpg](https://image.3001.net/images/20221109/1667975513_636b49592868c791e15c4.jpg!small)

### 3.1.4 分析和审计

操作审计

  * 云操作审计，帮助您监控并记录多云账号的活动，包括通过云控制台、OpenAPI、开发者工具对云上产品和服务的访问和使用行为。
  * 用户可以查看这些行为事件，然后进行行为分析、安全分析、资源变更行为追踪和行为合规性审计等操作。

![3968cc7c-93bd-4063-a943-78dc8ae60b89.jpg](https://image.3001.net/images/20221109/1667975513_636b4959e4a826455188f.jpg!small)

资源态势

  * 根据绑定混合云账号信息，即可同步获取云资源汇总信息。
  * 执行检测后，可以自动关联云资源态势信息，可以查看到具体哪些资源具有安全合规风险。

![157111fa-8b0a-4b11-9ab3-96b5b001a416.jpg](https://image.3001.net/images/20221109/1667975514_636b495aa23c0ebf980f9.jpg!small)

### 3.2 场景二：云原生安全

### 3.2.1 前置 K8s 配置

K8s 检测前置条件使用云原生 K8s 安全检测任务前需在 k8s 集群上安装 tirvy-operator

 **K8s 检测前置条件**

    
    
    使用云原生 K8s 安全检测任务前需在 k8s 集群上安装 tirvy-operator
    # 1.添加 chart 仓库
    helm repo add hummer https://registry.hummercloud.com/repository/charts
    
    # 2.更新仓库源
    helm repo update
    
    # 3.开始安装, 可以自定义应用名称和NameSpace
    helm install trivy-operator hummer/trivy-operator \
     --namespace trivy-system \
     --set="image.repository=registry.cn-beijing.aliyuncs.com/hummerrisk/trivy-operator" \
     --create-namespace --set="trivy.ignoreUnfixed=true"
    
    # 4.检测operator是否启动成功
    kubectl get pod -A|grep trivy-operator
    trivy-system   trivy-operator-69f99f79c4-lvzvs           1/1     Running            0          118s

 **K8s 账号添加校验**

  1. 确定部署 hummerrisk 的主机可以访问该 k8s 集群的 6443 端口，需要网络可达、端口可以通，如果不通可以检查防火墙;
  2. 确定提供的 k8s Token 有足够的权限，hummerrisk 会通过该 Token 调用 k8s apiserver 的 api
  3. k8s token 权限可以参考如下

创建 ServiceAccount

    
    
    cat <<EOF > hummer-sa.yaml
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: hummer
      namespace: kube-system
    EOF

创建 clusterrolebinding

    
    
    cat <<EOF > hummer-clusterrolebinding.yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRoleBinding
    metadata:
      name: hummer-user
    roleRef:
      apiGroup: rbac.authorization.k8s.io
      kind: ClusterRole
      name: cluster-admin
    subjects:
      - kind: ServiceAccount
      name: hummer
      namespace: kube-system
    EOF

创建资源

    
    
    kubectl create -f ./hummer-sa.yaml
    kubectl create -f ./hummer-clusterrolebinding.yaml

获取 token

    
    
    # 获取 token
    kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep hummer | awk '{print $1}') | grep token: | awk '{print $2}'

  

### 3.2.2 检测 K8s 风险⚓︎

Kuberbetes 配置

  * K8s 配置与云原生 K8s 环境安全检测功能，绑定 K8s Url 与 Token 信息即可进行安全检测，并生成安全漏洞结果。
  * K8s 平台环境有四种：分别是 Kubernetes、Rancher、OpenShift、KubeSphere。

![1a3d853d-16e9-42e3-a4bb-dcabfae7831a.jpg](https://image.3001.net/images/20221109/1667975515_636b495bafc8892aa60f6.jpg!small)![f5ff5e9b-6aa0-42e4-924c-8b009772671a.jpg](https://image.3001.net/images/20221109/1667975516_636b495c8e7464e1e8170.jpg!small)

K8s 检测结果

  * K8s 检测结果，主要展示 K8s 环境的漏洞安全信息和配置审计风险信息。

![7bc25e1a-d646-446f-a369-3f7375e14cb2.jpg](https://image.3001.net/images/20221109/1667975517_636b495d36b79e119c65c.jpg!small)![1aee474e-c004-4283-90eb-9f45c4e9558a.jpg](https://image.3001.net/images/20221109/1667975517_636b495decf1c8b27ba97.jpg!small)  
  

K8s 资源态势

  * 资源态势功能，绑定 K8s 环境信息，即可获取 K8s 的 Namespace、Pod、Node、Deployment、Service 等20余种资源信息。
  * 绑定完 K8s 账号是可以自动获取资源态势信息的。
  * 同时，也可以在同步日志页面手动获取资源态势信息。
  * 手动创建同步任务，即可查看同步资源数与同步状态。

![90671b40-59f4-4044-97ac-163046d49bb1.jpg](https://image.3001.net/images/20221109/1667975518_636b495eac64e57a13164.jpg!small)

### 3.2.3 检测部署文件

K8s 部署配置

  * K8s 部署检测功能，输入 K8s 部署配置 YAML 文件，即可进行部署检测，输出部署配置检测结果。

![ab540f7c-7e17-40e7-ab9c-dd32a7460b6a.jpg](https://image.3001.net/images/20221109/1667975519_636b495f6b8632b75c06c.jpg!small)

部署检测结果

  * 针对部署文件（YAML），一键执行检测后展示结果。
  * 用户可以根据检测结果的提示，修改对应的 YAML 文件内容，达到最佳要求。

![2c563ae5-bbda-471d-b8ed-163437e40777.jpg](https://image.3001.net/images/20221109/1667975520_636b49603e75f311bebc1.jpg!small)  
![7f2a997d-3752-488d-a6f3-6f75d636491f.jpg](https://image.3001.net/images/20221109/1667975521_636b4961018ffefea6da6.jpg!small)  
![ac6ca196-8a9e-44ac-8244-829dae1e8823.jpg](https://image.3001.net/images/20221109/1667975521_636b4961afabaf106f1e1.jpg!small)

### 3.2.4 检测镜像风险

镜像仓库

  * 用户可以绑定镜像仓库，之后检测的镜像可以从绑定的镜像仓库中查找和获取。
  * 镜像仓库类型：目前支持四种类型 harbor、dockerhub、nexus 和 other。如果选择 other 不会同步镜像，只做登录验证。
  * 镜像仓库中同步的镜像列表，可以直接执行检测，直接跳转到检测结果页面。（这个过程也会默认在镜像管理中新建一条数据）

![912c673c-db09-4d55-9298-f56072dd195c.jpg](https://image.3001.net/images/20221109/1667975522_636b496281c7adc23c892.jpg!small)

镜像管理

  * 在镜像管理页面，我们可以对具体需要检测的镜像进行管理。
  * 镜像列表中会显示出已经创建成功的待检测镜像，列表会显示出镜像的名称、状态、地址等信息。
  * 通过校验的镜像，镜像状态会显示为 [有效]，可以对其执行检测。
  * 镜像可以是公有镜像，也可以是私有镜像。可以手动填写镜像地址，上传镜像tar包，也可以从镜像仓库中选择同步的镜像。
  * 在镜像列表中，选择希望执行检测的镜像，点击列表后的[检测]按钮，确认后系统就会对该镜像进行检测。

![11b1a21d-a936-43f3-8568-da23116435bc.jpg](https://image.3001.net/images/20221109/1667975523_636b49634d9b03116b428.jpg!small)![7699a3e5-d906-45ad-9aa1-893696df1224.jpg](https://image.3001.net/images/20221109/1667975524_636b49641811f05e04ab2.jpg!small)

镜像检测结果

  * 镜像检测结果列表，展示镜像的漏洞信息。

![f398eef7-ece7-40d8-9519-b9390bbffcc6.jpg](https://image.3001.net/images/20221109/1667975524_636b4964c00bf86b5d4cd.jpg!small)  
![0c04b200-89dc-47af-a652-be3559a16b4d.jpg](https://image.3001.net/images/20221109/1667975525_636b49658d2d53272fefa.jpg!small)

### 3.2.5 检测主机风险

添加 统一凭据

  * 用户可以在统一凭据页面将常用的或重复的主机认证进行保存，这样在创建主机的过程中可以直接绑定，方便操作防止重复拷贝。
  * 新建、修改主机信息时，可灵活绑定凭据，统一凭据有三种类型，密码、密钥字符串、密钥文件。

![69ff96bd-273f-4285-8fff-8f0df3846080.jpg](https://image.3001.net/images/20221109/1667975526_636b49663a702bc625d83.jpg!small)

添加主机 & 执行检测

  * 主机管理列表页面提供了对主机分组、主机的创建、删除、编辑、查找、校验、检测等操作。
  * 创建主机时，可以为多个主机批量添加统一凭据，也可以分别为主机添加凭据。
  * 目前只针对 Linux 操作系统类型的主机。

![09a006f8-b733-4a14-a171-faa84c2aed8b.jpg](https://image.3001.net/images/20221109/1667975526_636b4966dfc9ad776c75c.jpg!small)![0bda2096-fdb3-4632-b674-35fd366fd832.jpg](https://image.3001.net/images/20221109/1667975527_636b4967966fd30861d0f.jpg!small)

  
主机检测结果

  * 在主机管理界面，选中待检测主机，一键执行后将自动跳转到主机检测结果页面。
  * 主检测结果页面将只会保留最新的一次检测结果，历史检测结果请到主机检测历史记录中查看。
  * 点击检测状态按钮，可以查看检测结果日志详情。

![842d7039-3e18-4c89-822b-7ecffcc035e2.jpg](https://image.3001.net/images/20221109/1667975528_636b4968460cf28a85c80.jpg!small)![caeec055-9418-41af-a1ec-3aa3fdf95f2e.jpg](https://image.3001.net/images/20221109/1667975529_636b496912bf3c3560650.jpg!small)

### 3.2.6 检测项目风险

项目源码配置

  * 在源码检测部分，通过对源码依赖的扫描，发现项目中存在的漏洞。
  * 目前绑定仓库支持两种类型：GitHub 和 GitLab 。
  * Token 的获取：首先私有仓库需要填入Token，公有仓库无需填写Token。

![840e7773-b8d8-4e72-88b3-efdc518616e7.jpg](https://image.3001.net/images/20221109/1667975529_636b4969b84432508c86e.jpg!small)![26e6c5ba-5d9b-4467-a888-7d9822f85963.jpg](https://image.3001.net/images/20221109/1667975530_636b496a7bbc82117d75f.jpg!small)

源码检测结果

  * 源码检测，可以针对 branch 分支、可以针对 tag 标签、可以针对 commit 某次提交。
  * 源码检测结果列表，展示源码项目依赖的漏洞信息。

![6bb3f0ea-2f78-4f47-87e3-81c38f9ec2d7.jpg](https://image.3001.net/images/20221109/1667975531_636b496b3146fd85b9999.jpg!small)![deac9812-e840-4f70-a3a6-63453d6d96a3.jpg](https://image.3001.net/images/20221109/1667975531_636b496bde192229e11db.jpg!small)

  
依赖文件管理

  * 对于源码检测的补充，如果只想检测源码项目的依赖文件检测，可以上传对应的文件进行检测。
  * 依赖文件可以是单个文件，也可以是文件夹的压缩文件。
  * 依赖文件的格式，例如 java 的 pom.xml，vue 的 package.json 或 yarn.lock 等。

![7bb9c276-0485-45ce-84c9-01e6b94399a9.jpg](https://image.3001.net/images/20221109/1667975532_636b496cabd28467fe056.jpg!small)

![76c8cb7f-3fdb-4058-a23a-96ab9d45bd00.jpg](https://image.3001.net/images/20221109/1667975533_636b496d66eb822e030ac.jpg!small)

依赖文件检测结果

  * 依赖文件检测结果列表，展示项目依赖的漏洞信息。

![2ed51c4d-6ec1-43b0-a4cc-ae7afe5e7c7e.jpg](https://image.3001.net/images/20221109/1667975534_636b496e2083c41b177b4.jpg!small)

## 4 、参考信息

https://docs.hummerrisk.com/

