![](https://image.3001.net/images/20230419/1681917142_644004d6346736b95a939.jpeg!small)

## 关于Popeye

Popeye是一款功能强大的Kubernetes集群配置与资源安全扫描工具，该工具可以实时扫描Kubernetes集群，并报告部署的资源和配置的潜在问题。Popeye可以根据部署的内容而不是磁盘上的内容来清理集群。通过扫描集群，它可以检测错误配置，并帮助我们确保采取了最佳实践，从而避免未来可能出现的安全问题。

除此之外，该工具也可以报告潜在的资源分配过多或不足问题，并在集群容量耗尽时尝试警告管理人员。

Popeye是一个只读工具，它不会以任何方式更改任何Kubernetes资源！

## 工具安装

当前版本的Popeye支持在Linux、macOS和Windows操作系统上运行。

广大研究人员可以直接访问该项目的【[
_Releases页面_](https://github.com/derailed/popeye/releases)】获取针对Linux、macOS和Windows操作系统的源代码。

使用Homebrew/LinuxBrew安装：

    
    
    brew install derailed/popeye/popeye

使用go install安装：

    
    
    go install github.com/derailed/popeye@latest

### 源码安装

该工具需要使用Go v1.12+环境来构建代码。

首先使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/derailed/popeye.git

然后在go.mod文件中添加下列命令：

    
    
    replace (
    
      github.com/derailed/popeye => MY_POPEYE_CLONED_GIT_REPO
    
    )

然后构建并运行可执行文件：

    
    
    go run main.go

## 命令行参数

    
    
    # 输出工具版本
    
    popeye version
    
    # 使用Popeye扫描当前kubconfig环境集群
    
    popeye
    
    # 使用配置文件执行扫描
    
    popeye -f spinach.yml
    
    # 使用一个kubeconfig上下文执行扫描
    
    popeye --context olive
    
    # 查看工具帮助信息
    
    popeye help

## 报告存储

将扫描报告保存在当前工作目录：

    
    
    $ POPEYE_REPORT_DIR=$(pwd) popeye --save

将扫描报告以HTML格式（report.html）保存在当前工作目录：

    
    
    $ POPEYE_REPORT_DIR=$(pwd) popeye --save --out html --output-file report.html

## 工具运行截图

![](https://image.3001.net/images/20230419/1681917296_64400570ee847b88d6102.png!small)![](https://image.3001.net/images/20230419/1681917305_6440057999872bb198663.png!small)

![](https://image.3001.net/images/20230419/1681917384_644005c8109e5fed45676.png!small)

  

## 许可证协议

本项目的开发与发布遵循[ _Apache_ _-2_ _._
_0_](https://github.com/derailed/popeye/blob/master/LICENSE)开源许可证协议，

## 项目地址

 **Popeye** ：【[ _GitHub传送门_](https://github.com/derailed/popeye)】

## 参考资料

> [ _https://docs.aws.amazon.com/sdk-for-> go/api/aws/session/_](https://docs.aws.amazon.com/sdk-for-> go/api/aws/session/)

