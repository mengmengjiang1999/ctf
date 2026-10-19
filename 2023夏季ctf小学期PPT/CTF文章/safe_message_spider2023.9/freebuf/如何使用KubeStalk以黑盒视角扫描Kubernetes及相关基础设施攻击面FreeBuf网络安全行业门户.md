![](https://image.3001.net/images/20230522/1684745210_646b2bfacd8f76fa86560.jpg!small)

## 关于KubeStalk

KubeStalk是一款针对Kubernetes的安全扫描工具，在该工具的帮助下，广大研究人员能够以黑盒测试的视角来扫描和检测Kubernetes及其相关基础设施的安全问题，并以此来识别出潜在的攻击面。除此之外，广大研究人员还可以使用该工具来检测不安全的Kubernetes集群。

## 工具安装

KubeStalk基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python 3环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/redhuntlabs/KubeStalk.git

代码克隆完成之后，我们还需要安装requests库，我们可以使用下列命令直接安装：

    
    
    python3 -m pip install requests

或使用pip命令和项目提供的requirements.txt文件来安装该工具所需的依赖组件：

    
    
    python3 -m pip install -r requirements.txt

现在，一切都已经准备就绪，接下来我们就可以开始直接使用该工具了。

## 命令行参数

我们可以使用-h选项来查看该工具提供的所有命令行参数：

    
    
    $ python3 kubestalk.py  -h
    
     
    
        +---------------------+
    
        |  K U B E S T A L K  |
    
        +---------------------+   v0.1
    
     
    
    [!] KubeStalk by RedHunt Labs - A Modern Attack Surface (ASM) Management Company
    
    [!] Author: 0xInfection (RHL Research Team)
    
    [!] Continuously Track Your Attack Surface using https://redhuntlabs.com/nvadr.
    
     
    
    usage: ./kubestalk.py <url(s)>/<cidr>
    
     
    
    Required Arguments:
    
      urls                  待扫描的主机地址列表
    
     
    
    Optional Arguments:
    
      -o OUTPUT, --output OUTPUT
    
                            将路径输出写入到CSV文件中
    
      -f SIG_FILE, --sig-dir SIG_FILE
    
                            要加载的签名目录路径
    
      -t TIMEOUT, --timeout TIMEOUT
    
                            HTTP超时值（单位为秒）
    
      -ua USER_AGENT, --user-agent USER_AGENT
    
                            HTTP请求中要设置的用户代理Header
    
      --concurrency CONCURRENCY
    
                            同时需要处理的主机数量
    
      --verify-ssl           验证SSL证书
    
      --version             显示KubeStalk版本并退出

## 工具使用

### 工具基础使用

    
    
    $ python3 kubestalk.py https://███.██.██.███:10250
    
     
    
        +---------------------+
    
        |  K U B E S T A L K  |
    
        +---------------------+   v0.1
    
     
    
    [!] KubeStalk by RedHunt Labs - A Modern Attack Surface (ASM) Management Company
    
    [!] Author: 0xInfection (RHL Research Team)
    
    [!] Continuously Track Your Attack Surface using https://redhuntlabs.com/nvadr.
    
     
    
    [+] Loaded 10 signatures to scan.
    
    [*] Processing host: https://███.██.██.██:10250
    
    [!] Found potential issue on https://███.██.██.██:10250: Kubernetes Pod List Exposure
    
    [*] Writing results to output file.
    
    [+] Done.

### 并发设置

我们可以使用--concurrency参数来控制并行扫描的主机数量，默认值为5。

### 结果输出

扫描结果会写入到一个CSV文件中，可以通过--output参数来控制。

下面给出的是一个CSV输出文件格式样例：

 ** **主机****

|

 ** **路径****

|

 ** **问题****

|

 ** **类型****

|

 ** **严重性****  
  
---|---|---|---|---  
  
https://█.█.█.█:10250

|

/pods

|

Kubernetes Pod 列表暴露

|

核心组件

|

漏洞/错误配置  
  
https://█.█.█.█:443

|

/api/v1/pods

|

Kubernetes Pod 列表暴露

|

核心组件

|

漏洞/错误配置  
  
http://█.█.██.█:80

|

/

|

etcd Viewer 仪表盘暴露

|

插件

|

漏洞/暴露  
  
http://██.██.█.█:80

|

/

|

cAdvisor Metrics Web UI 仪表盘暴露

|

插件

|

漏洞/暴露  
  
## 工具使用演示

![](https://image.3001.net/images/20230522/1684745326_646b2c6ee5005a932462c.gif)

## 许可证协议

本项目的开发与发布遵循[ _BSD_
_-3-Clause_](https://github.com/redhuntlabs/KubeStalk/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **KubeStalk** ：【[ _GitHub传送门_](https://github.com/redhuntlabs/kubestalk)】

## 参考资料

> [ _https://redhuntlabs.com/blog/unsecured-kubernetes-clusters-> exposed/_](https://redhuntlabs.com/blog/unsecured-kubernetes-clusters-> exposed/)
>
> [ _https://redhuntlabs.com/nvadr_](https://redhuntlabs.com/nvadr)

