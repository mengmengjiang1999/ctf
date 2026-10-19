![](https://image.3001.net/images/20210311/1615445847_6049bf5784f71d2f050f1.png!small)

## Horusec是什么？

Horusec是一款功能强大的开源工具，它可以帮助广大研究人员执行静态代码分析，以识别开发过程中的安全缺陷。目前，Horusec支持分析的语言有：C#、Java、Kotlin、Python、Ruby、Golang、Terraform、Javascript、Typescript、Kubernetes、PHP、C、HTML、JSON、Dart。该工具可以在项目的所有文件以及Git历史记录中搜索密钥泄漏和安全漏洞。Horusec可以由开发人员通过命令行接口使用，也可以由DevSecOps团队在CI/CD
mats上使用。

## Horusec完整体系架构

![](https://image.3001.net/images/20210311/1615445857_6049bf610a1a4ff9a5cd8.png!small)

## 工具安装

下载并安装最新版本代码：

    
    
    curl -fsSL https://horusec.io/bin/install.sh | bash

下载并安装指定版本代码：

    
    
    curl -fsSL https://horusec.io/bin/install.sh | bash -s v1-0-0

可选的操作系统包括：

    
    
    linux_x86, linux_x64, mac_x64, win_x86, win_x64

手动下载windows x64代码：

    
    
    curl "https://horusec.io/bin/latest/win_x64/horusec.exe" -o "./horusec.exe" && ./horusec.exe version

手动下载linux x64代码：

    
    
    curl "https://horusec.io/bin/latest/linux_x64/horusec" -o "./horusec" && chmod +x ./horusec && ./horusec version

手动下载macOS x64代码：

    
    
    curl "https://horusec.io/bin/latest/mac_x64/horusec" -o "./horusec" && chmod +x ./horusec && ./horusec version

## Docker镜像

我们还提供了专门的Docker镜像，可用于替换项目源码使用。使用样例如下：

    
    
    docker run -v /var/run/docker.sock:/var/run/docker.sock -v {path of project in host}:/src/horusec-vscode horuszup/horusec-cli:latest horusec start -p /src/horusec-vscode -P {path of project in host}

## 安装检测

    
    
    horusec version

## horusec-cli使用要求

  * Docker
  * git

## 工具使用

下列命令运行后即可使用horusec-cli并检查项目中的安全漏洞：

    
    
    horusec start

或者，发送授权认证令牌来查看Horusec管理员面板中的分析内容：

    
    
    horusec start -a="<YOUR_TOKEN_AUTHORIZATION>"

### 本地使用

如需在本地使用Horusec，首先需要将该项目源码克隆至本地：

    
    
    git clone https://github.com/ZupIT/horusec.git

然后运行下列命令即可使用 _horusec-cli_进行分析了：

    
    
    make install

### 默认开发账号

如需使用Horusec的完整功能，我们可以直接使用默认用户账号进行登录：

    
    
    email: dev@example.com
    
      password: Devpass0*

### 本地使用要求

> docker
>
> git
>
> docker-compose/helm
>
> golang
>
> rabbitmq
>
> postgres
>
> 邮件账号（可选）

## 支持的命令

Horusec支持的命令下表所示：

 ** **命令****

|

 ** **描述****  
  
---|---  
  
generate

|

此命令在当前路径中创建配置文件，如果存在新密钥，则更新（不删除当前密钥）  
  
start

|

此命令使用默认值在当前目录中启动分析  
  
version

|

你可以看到在本地计算机上运行的实际版本  
  
## 工具使用样例

简单使用：

    
    
    horusec start

使用其他目录：

    
    
    horusec start -a="REPOSITORY_TOKEN" -p="/home/user/project"

忽略指定目录或路径：

    
    
    horusec start -p="/home/user/project" -a="REPOSITORY_TOKEN" -i="./node_modules,./vendor,./public, **/*test.go"

获取JSON格式输出：

    
    
    horusec start -p="/home/user/project" -a="REPOSITORY_TOKEN" -o="json" -O="./output.json"

## 演示样例

![](https://image.3001.net/images/20210311/1615445961_6049bfc936fe80fcf5337.gif)

## 项目地址

Horusec：【[ _GitHub传送门_](https://github.com/ZupIT/horusec)】

## 参考资料

> [ _https://horusec.io/docs_](https://horusec.io/docs)
>
> [ _https://github.com/ZupIT/horusec-vscode-> plugin_](https://github.com/ZupIT/horusec-vscode-plugin)
>
> [ _https://github.com/ZupIT/horusec/blob/master/horusec-> cli#installing_](https://github.com/ZupIT/horusec/blob/master/horusec-> cli#installing)
>
> [ _https://github.com/ZupIT/horusec/blob/master/horusec-cli#horusec-> cli_](https://github.com/ZupIT/horusec/blob/master/horusec-cli#horusec-cli)

  

