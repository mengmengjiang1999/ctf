![](https://image.3001.net/images/20210428/1619581013_6088d855808aa8f40b899.jpg!small)  

## 关于Kubesploit

Kubesploit是一个功能强大的跨平台后渗透漏洞利用HTTP/2命令&控制服务器和代理工具，该工具基于Golang开发，基于Merlin项目实现其功能，主要针对的是容器化环境的安全问题。

我们的主要目标是提高社区对容器化环境安全的认识，并改进各种网络中实施的缓解措施。所有这些都是通过一个框架来实现的，这个框架为PT团队和红队成员在这些环境中的活动提供了适当的工具。使用这些工具将帮助你评估这些环境的优势，并进行必要的更改以保护它们。

由于C&C和代理基础设施已经由Merlin完成，我们只需要继承Go解释器（“Yaegi”）就可以在服务器端和代理运行Golang代码了。

它允许我们在Golang中编写模块，为模块提供更大的灵活性，并动态加载新模块。这是一个正在进行的项目，我们计划在未来添加更多与Docker和Kubernetes相关的模块。

## 功能介绍

  * 支持容器加载；
  * 支持sock；
  * 利用CVE-2019-5736漏洞攻击容器；
  * 扫描Kubernetes集群中的已知CVE漏洞；
  * 端口扫描，重点是Kubernetes服务；
  * 从容器内扫描Kubernetes服务；
  * 使用RCE扫描容器；
  * 扫描Pods和容器；
  * 扫描所有可用容器中的令牌；
  * 使用多个选项运行命令；

## 快速开始

我们在Katacoda中创建了一个专用的Kubernetes环境，可以帮助你使用Kubesploit对目标环境进行测试。在下面的演示样例中，我们演示了一整套完整的操作，并告诉大家如何使用Kubesploit的自动化功能。

 **演示样例：**
https://github.com/cyberark/kubesploit/raw/assets/kubesploit_demo_with_progress_bar.gif

## 项目构建

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/cyberark/kubesploit.git

然后切换到项目根目录，运行下列命令即可：

    
    
    make

### 快速构建

如需在Linux系统下对项目进行快速构建，可以直接运行下列命令：

    
    
    export PATH=$PATH:/usr/local/go/bin
    
    go build -o agent cmd/merlinagent/main.go
    
    go build -o server cmd/merlinserver/main.go

## YARA规则

我们所创建的YARA规则可以帮助广大研究人员获取Kubesploit源码，规则编写在kubesploit.yara文件中。

## 代理记录

代理中加载的每一个Go模块都会在目标设备中被记录下来。

## MITRA地图

我们还为Kubesploit中所使用的每一个攻击向量创建了MITRE地图：

![](https://image.3001.net/images/20210428/1619581054_6088d87e47514a507d308.png!small)

## 许可证协议

本项目的开发与发布遵循GPL v3.0开源许可证协议。

## 项目地址

 **Kubesploit：** https://github.com/cyberark/kubesploit

