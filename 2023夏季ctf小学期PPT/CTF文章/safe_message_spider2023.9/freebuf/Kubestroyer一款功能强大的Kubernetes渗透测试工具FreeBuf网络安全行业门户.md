![](https://image.3001.net/images/20230802/1690959452_64c9fe5c783a58a17e01b.png!small)  

## 关于Kubestroyer

Kubestroyer是一款功能强大的Kubernetes渗透测试工具，该工具旨在利用Kubernetes集群中的错误配置，以帮助广大研究人员挺升Kubernetes的安全性。简而言之，Kubestroyer是一个多功能的网络安全渗透测试工具，可以帮助广大研究人员完成针对Kubernetes的安全研究分析。

Kubestroyer基于Golang开发，支持扫描已知的暴露在外的Kubernetes端口，并利用其中潜在的安全问题以及错误配置。

## 支持的功能

> 1、多目标扫描；
>
> 2、通过文件输入扫描目标；
>
> 3、已知端口扫描；
>
> 4、节点端口扫描（30000-32767）；
>
> 5、Kubelet匿名RCE；
>
> 6、支持自选命令执行；

## 工具要求

由于该工具基于Golang开发，因此我们首先需要在本地设备上安装并配置好Go v1.19环境：

    
    
    wget https://go.dev/dl/go1.19.4.linux-amd64.tar.gz
    
    tar -C /usr/local -xzf go1.19.4.linux-amd64.tar.gz

## 工具安装

配置好Go环境之后，广大研究人员可以使用下列命令直接安装：Kubestroyer

    
    
    $ go install github.com/Rolix44/Kubestroyer@latest

除此之外，广大研究人员也可以将该项目源码克隆至本地，并进行手动代码构建：

    
    
    $ git clone https://github.com/Rolix44/Kubestroyer.git
    
    cd /Kubestroyer
    
    $ go build -o Kubestroyer cmd/kubestroyer/main.go

当然了，我们也可以访问该项目的【[
_Releases页面_](https://github.com/Rolix44/Kubestroyer/releases)】下载预编译的Kubestroyer。

## 工具使用

 ** **参数****

|

 ** **描述****

|

 ** **必须**** ** **/**** ** **可选****

|

 ** **使用样例****  
  
---|---|---|---  
  
-t / --target

|

目标IP、域名或文件

|

必须

|

-t localhost,127.0.0.1 / -t ./domain.txt  
  
\--node-scan

|

启用节点端口扫描（30000-32767）

|

可选

|

-t localhost --node-scan  
  
\--anon-rce

|

使用Kubelet API匿名认证实现远程代码执行

|

可选

|

-t localhost --anon-rce  
  
-x

|

需要远程执行的命令

|

可选

|

-t localhost --anon-rce -x "ls -al"  
  
## 工具使用演示

![](https://image.3001.net/images/20230802/1690959490_64c9fe82ecd6bdbf792a3.gif)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/Rolix44/Kubestroyer/blob/master/LICENSE.txt)开源许可证协议。

## 项目地址

 **Kubestroyer** ：【[ _GitHub传送门_](https://github.com/Rolix44/Kubestroyer)】

