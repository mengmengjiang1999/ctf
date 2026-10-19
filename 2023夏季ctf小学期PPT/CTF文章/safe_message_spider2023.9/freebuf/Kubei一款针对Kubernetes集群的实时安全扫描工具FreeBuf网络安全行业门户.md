![](https://image.3001.net/images/20200804/1596492908.png!small)

## Kubei

Kubei是一款针对Kubernetes集群的实时安全扫描工具，该工具将允许广大研究人员对正在运行的Kubernetes集群进行实时扫描，并获取准确及时的安全评估结果。Kubei能够扫描一个Kubernetes集群中使用的全部镜像，包括应用程序Pod和系统Pod镜像。需要注意的是，Kubei不会扫描整个镜像注册表，也不需要跟CI/CD管道进行初步集成。

Kubei是一个易于扩展且支持自定义配置的工具，这将允许研究人员自行定义扫描的范围、目标命名空间、扫描速度和感兴趣的漏洞风险等级。

除此之外，Kubei还提供了非常友好的图形化用户接口，以帮助研究人员快速查看、识别和发现Kubernetes集群中潜在的安全问题。

## 工具要求

  * 已正常运行的Kubernetes集群；
  * 目标Kubernetes集群以存在正确配置的kubeconfig（~/.kube/config）文件；

### 权限要求

  * 可在集群范围内读取敏感数据，能够扫描隐私镜像库；
  * 可在集群范围内枚举Pod，能够计算待扫描的目标Pod数量；
  * 可在集群范围内创建Job，能够创建在目标命名空间内对目标Pod进行扫描的Job作业；

## 工具配置

在使用Kubei时，需要利用deploy/kubei.yaml来在目标集群中部署和配置Kubei：

首先，我们需要给Kubei设置扫描范围，这里可以通过设置“IGNORE_NAMESPACES”环境变量来忽略不需要扫描的命名空间。设置“TARGET_NAMESPACE”环境变量可以指定一个待扫描的命名空间，留空表示扫描所有的命名空间/

接下来，我们需要设置Kubei的扫描速度。这里可以使用并行运行扫描器的方式来加快扫描速度，或者通过“MAX_PARALLELISM”环境变量来设置并行扫描器的最大数量。

第三步，我们需要设置Kubei扫描的安全严重等级阈值，此时严重性等级高于或等于这个阈值的所有漏洞和安全问题都将被报告给用户。Kubei支持的严重性等级分为别未知、可忽略的、低、中、高和Defcon1，默认为“中”。

最后，我们需要设置Job作业的删除策略。这里可以通过设置“DELETE_JOB_POLICY”环境变量来定义是否需要删除已完成的扫描器作业，支持的值如下：

    
    
    -All：所有已完成的作业都将被删除；
    
    -Successful：只有执行成功的作业才会被删除（默认）；
    
    -Never：任务不会被删除；

## 工具使用

我们需要运行下列命令将Kubei部署到目标Kubernetes集群之中：

    
    
    kubectl apply -f https://raw.githubusercontent.com/Portshift/kubei/master/deploy/kubei.yaml

接下来，执行下列命令来判断Kubei是否已正常运行：

    
    
    kubectl -n kubei get pod -lapp=kubei

确保Kubei已正常运行之后，通过执行下列命令将端口数据转发至Kubei Webapp中：

    
    
    kubectl -n kubei port-forward $(kubectl -n kubei get pods -lapp=kubei -o jsonpath='{.items[0].metadata.name}') 8080

然后打开Web浏览器，访问“http://localhost:8080/view/”，然后点击“Go”来运行扫描任务。

如需检查Kubei的运行状态以及正在进行的扫描进程，可以运行下列命令：

    
    
    kubectl -n kubei logs $(kubectl -n kubei get pods -lapp=kubei -o jsonpath='{.items[0].metadata.name}')

刷新页面（http://localhost:8080/view/）即可更新扫描结果。

## 使用外部HTTP/HTTPS代理运行Kubei

打开deploy/kubei.yaml，去掉针对Clari和Kubei部署中代理环境变量的相关注释，并填写配置信息即可。

### 亚马逊ECR支持

使用“AmazonEC2ContainerRegistryFullAccess”权限创建一个AWS
IAM用户，并使用用户凭证（AWS_ACCESS_KEY_ID、AWS_SECRET_ACCESS_KEY和AWS_DEFAULT_REGION）来创建下列密钥：

    
    
    cat <<EOF | kubectl apply -f -    
    apiVersion: v1
    
    kind: Secret
    
    metadata:
    
      name: ecr-sa
    
      namespace: kubei
    
    type: Opaque
    
    data:
    
      AWS_ACCESS_KEY_ID: $(echo -n 'XXXX'| base64 -w0)
    
      AWS_SECRET_ACCESS_KEY: $(echo -n 'XXXX'| base64 -w0)
    
      AWS_DEFAULT_REGION: $(echo -n 'XXXX'| base64 -w0)
    
    EOF

注意事项：

首秀按，密钥名称必须为ecr-sa。其次，密钥中的data键值必须设置为AWS_ACCESS_KEY_ID、AWS_SECRET_ACCESS_KEY和AWS_DEFAULT_REGION。

### Google GCR支持

使用“Artifact Registry Reader”权限创建一个 _Google服务账号_。

使用服务账号的JSON文件来创建下列密钥：

    
    
    kubectl -n kubei create secret generic --from-file=sa.json gcr-sa

注意事项：

首先，密钥名必须为gcr-sa。其次，sa.json名必须是服务账号JSON文件的名称。第三，Kubei使用的是应用程序默认凭证。

## 工具限制

  * 支持Kubernetes Image Manifest V2， Schema 2，不支持扫描更早的版本；

  * CVE漏洞数据库每日一更；

## 项目地址

Kubei：【[ _GitHub传送门_](https://github.com/Portshift/Kubei)】

