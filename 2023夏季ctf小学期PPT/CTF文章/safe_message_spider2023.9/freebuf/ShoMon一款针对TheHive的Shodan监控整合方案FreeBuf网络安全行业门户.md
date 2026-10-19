![](https://image.3001.net/images/20221024/1666614925_6356868da648851589548.png!small)

## 关于ShoMon

ShoMon是一款针对TheHive的Shodan监控整合方案，该工具基于Golang开发，专为TheHive设计，经过多个版本的迭代，当前的ShoMon
v2.0功能将更加强大！

而TheHive则是一个可扩展的四合一开源和免费的安全事件响应平台。这4个是TheHive, Cortex, TheHive4py
(TheHive的python
API)和MISP。TheHive的设计是为了让soc、csirt、cert和任何信息安全从业者在处理需要迅速调查和采取行动的安全事件时生活得更轻松。

## 功能介绍

> 1、可以用作Webhook或Stream侦听器：Webhook侦听器为Shodan打开一个restful
> API端点以发送警报。这意味着此节点可访问公共网络；而Stream侦听器则需要连接到Shodan并获取/解析警报流；
>
> 2、整合了[ _shadowscatcher/shodan_](https://github.com/shadowscatcher/shodan)；
>
> 3、终端日志为JSON格式，支持转发到其他日志管理工具；
>
> 4、支持通过GitHub Action的CI/CD；
>
> 5、提供了一个针对TheHive的[ _docker_
> _-compose_](https://github.com/KaanSK/shomon/blob/master/docker-> compose.yml)文件和依赖；
>
> 6、工具速度非常快，工具占用空间非常小；
>
> 7、模块化开发，易于维护和二次开发；
>
> 8、支持使用配置文件或环境变量来动态调整工具运行；

## 工具使用

### Releases安装

广大研究人员可以直接访问该项目的【[
_Releases页面_](https://github.com/KaanSK/shomon/releases/latest)】下载最新版本的预构建项目源码。

### 源码编译

首先，我们需要搭建并配置好一个Golang工作环境。接下来，可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/KaanSK/shomon.git

然后切换到项目目录中，并使用“go build”命令构建源码：

    
    
    cd shomon
    
    go build

除此之外，我们还可以使用下列命令自定义编译项目并生成体积更小的源码：

    
    
    go build -ldflags="-s -w"

### 公共容器使用

    
    
    docker pull ghcr.io/kaansk/shomon
    
    docker pull kaansk/shomon

### docker-compose文件使用

首先，编辑[docker-compose文件](https://github.com/KaanSK/shomon/blob/master/docker-compose.yml)中的环境变量和配置信息。

接下来，运行下列命令即可：

    
    
    docker-compose run -d

## 工具使用

我们可以通过conf.yaml文件或环境变量给工具传递运行参数。接下来，直接运行下列命令即可使用ShoMon：

    
    
    ./shomon

### 配置文件样例

    
    
    HIVE_URL: "http://localhost:9000"
    
    HIVE_KEY:
    
    HIVE_CASE_TEMP*LATE:
    
    HIVE_TYPE: "SHODAN"
    
    HIVE_TAGS:
    
      - 'test:test2="test3"'
    
      - 'test4:test5="test6"'
    
    SHODAN_KEY:
    
    INCLUDE_BANNER: true
    
    LOG_LEVEL: DEBUG
    
    WEBHOOK: true
    
    WEBHOOK_ENDPOINT: "/"
    
    WEBHOOK_PORT: 8080

## 工具运行截图

![](https://image.3001.net/images/20221024/1666615023_635686ef211b37276709a.png!small)

![](https://image.3001.net/images/20221024/1666615030_635686f622f7f0775a2c3.png!small)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/KaanSK/shomon/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **ShoMon** ：【[ _GitHub传送门_](https://github.com/KaanSK/shomon)】

## 参考资料

> [
> _https://github.com/shadowscatcher/shodan_](https://github.com/shadowscatcher/shodan)
>
> [ _https://www.cloudreach.com/en/resources/blog/cts-build-golang-> dockerfiles/_](https://www.cloudreach.com/en/resources/blog/cts-build-> golang-dockerfiles/)
>
> [ _https://goreleaser.com/_](https://goreleaser.com/)

