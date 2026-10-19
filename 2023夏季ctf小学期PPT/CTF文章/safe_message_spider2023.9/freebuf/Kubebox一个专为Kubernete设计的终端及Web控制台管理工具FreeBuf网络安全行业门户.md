![](https://image.3001.net/images/20200804/1596533428.png!small)

## Kubebox

Kubebox是一个专为Kubernete设计的终端及Web控制台管理工具。目前该工具可以给广大管理员提供以下功能：

  * 使用fubeconfig文件配置Kubernetes集群，即通过KUBECONFIG环境变量或$HOME/.kube；
  * 交互式切换上下文环境；
  * _认证支持_（bearer令牌、基础认证、私钥/整数、OAuth、OpenID Connect、Amazon EKS、Google Kubernetes引擎、Digital ocean）
  * 命名空间选择和Pods列表监控；
  * 容器日志查看；
  * 容器资源使用（内存、CPU、网络、文件系统图表）；
  * 通过终端实现容器远程命令执行；
  * 集群、命名空间、Pod事件监控

## 工具安装&执行

首先，访问该项目的Release页面，根据你自己的操作系统平台下载对应的Kubebox可执行程序，或直接使用下列命令完成下载部署：

    
    
    # Linux
    
    $ curl -Lo kubebox https://github.com/astefanutti/kubebox/releases/download/v0.8.0/kubebox-linux && chmod +x kubebox
    
    # OSX
    
    $ curl -Lo kubebox https://github.com/astefanutti/kubebox/releases/download/v0.8.0/kubebox-macos && chmod +x kubebox
    
    # Windows
    
    $ curl -Lo kubebox.exe https://github.com/astefanutti/kubebox/releases/download/v0.8.0/kubebox-windows.exe

接下来，执行下列命令来运行Kubebox工具：

    
    
    $ ./kubebox

## 服务器

Kubebox可以直接托管在我们的Kubernetes集群中并以服务的方式给我们提供其功能。终端模拟功能基于Xterm.js实现，服务器端将作为代理并允许通过Kubernetes
Master API来与集群进行网络通信。

如需在Kubernetes集群中部署服务器，可直接运行下列命令：

    
    
    $ kubectl apply -f https://raw.github.com/astefanutti/kubebox/master/kubernetes.yaml

如需关闭服务器并清理所有资源，可直接运行下列命令：

    
    
    $ kubectl delete namespace kubebox

或者说，如果你需要在OpenShift集群中部署服务器端，可直接运行下列命令：

    
    
    $ oc new-app -f https://raw.github.com/astefanutti/kubebox/master/openshift.yaml

## Docker

当然了，你也可以直接使用Docker来部署和运行Kubebox：

    
    
    $ docker run -it --rm astefanutti/kubebox

如果你需要将本地主目录加载进Kubebox的话（以便利用~/.kube/config），可以运行下列命令：

    
    
    $ docker run -it --rm -v ~/.kube/:/home/node/.kube/:ro astefanutti/kubebox

## 在线使用

除了通过代码部署的方式之外，我们还可以直接在线使用Kubebox，点击【[
_这里_](https://kube.sh/)】即可直接体验。请注意，弹出框需要填写的地址必须匹配API服务器CORS同源策略所允许的地址，这里可以通过Kubernetes
API服务器命令行接口进行配置：

    
    
    $ kube-apiserver --cors-allowed-origins .*

Kubebox在线地址：[
_https://kube.sh/_](https://kube.sh/)![](https://image.3001.net/images/20200804/1596533667.png!small)

## 工具本地部署

    
    
    $ git clone https://github.com/astefanutti/kubebox.git
    
    $ cd kubebox
    
    $ npm install
    
    $ node index.js

## 工具运行截图

### 集群事件：![](https://image.3001.net/images/20200804/1596533757.png!small)

### 容器Shell连接：![](https://image.3001.net/images/20200804/1596533779.png!small)

### 终端主题支持：![](https://image.3001.net/images/20200804/1596533801.png!small)

### Web浏览器版本：![](https://image.3001.net/images/20200804/1596533821.png!small)

## 项目地址

Kubebox：【[ _GitHub传送门_](https://github.com/astefanutti/kubebox)】

