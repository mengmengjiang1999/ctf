![](https://image.3001.net/images/20221018/1666090820_634e87445330e208c0ead.png!small)

## 关于Matano

Matano是一款针对AWS的开源安全湖平台，该平台允许我们从各种数据源获取并注入大量和安全以及日志相关的数据，并将其存储到一个开源的Apache
Iceberg数据湖中，同时这也方便广大研究人员进行后续的安全数据查询。除此之外，该工具还会创建Python脚本对代码进行实时监测，并会在检测到问题是发出实时警报。Matano是以完全无服务架构形式实现的，并且专为AWS设计。该工具的特性为大规模、低成本和零操作，支持广大研究人员轻松将Matano部署到目标AWS账户中。

## 功能介绍

### 从各种数据源收集安全与日志数据

Matano支持从各种数据源收集数据并存储到[ _S_
_3_](https://github.com/matanolabs/matano)或其他给予SQS的存储中。

### 存储、传输和日志数据格式化处理

Matano可以使用[
_VRL_](https://vector.dev/docs/reference/vrl/)来对数据进行格式化和传输，Matano默认使用[
_ECS_](https://www.elastic.co/guide/en/ecs/current/index.html)，我们也可以定义自己的模式。

### 将数据存储至S3对象存储中

日志数据存储在S3对象存储中，实现经济高效、长期耐用地数据存储。

### Apchae Iceberg数据湖

所有数据都被接收到一个基于Apache Iceberg的数据湖中，允许我们对所有日志数据执行ACID事务和其他操作等。Apache
Iceberg是一种开放表格式，因此我们始终拥有自己的原始数据，不存在其他锁定或限制。

### 无服务架构

Matano是一个完全无服务平台，旨在实现零操作和无限弹性的水平扩展。

### Python脚本实时监测日志数据

可以通过编写Python脚本实现对日志数据的实时警报。

## 工具运行机制

![](https://image.3001.net/images/20221018/1666090846_634e875e63f4d0114d3a6.png!small)

## 工具安装

### 依赖要求

> Docker

### Nightly版本

Matano还提供了一个[
_Nightly版本_](https://github.com/matanolabs/matano/releases/tag/nightly)，其中包含最新版本的预构建文件，可以用来安装matano命令行工具。除此之外，我们也可以直接下载和安装Matano安装程序。

比如说，下列命令可以在Linux上安装并配置好Matano命令行工具：

    
    
    curl -OL https://github.com/matanolabs/matano/releases/download/nightly/matano-linux-x64.sh
    
    chmod +x matano-linux-x64.sh
    
    sudo ./matano-linux-x64.sh

### 源码安装

广大研究人员还可以使用下列命令直接将项目源码克隆至本地，并完成项目构建：

    
    
    git clone https://github.com/matanolabs/matano.git
    
    cd matano
    
    make package

上述命令将在项目根目录下生成一个matano-linux-x64.sh安装文件，直接运行该文件即可。

## 工具部署

如需使用Matano，直接运行下列命令即可：

    
    
    matano init

确保你已经在环境变量或AWS CLI配置文件中定义了AWS凭证。

交互式命令行工具的安装程序会自动帮助我们生成一个初始化Matano目录，并初始化AWS账号，然后将Matano部署到AWS账号中。

部署过程需要几分钟，请耐心等待。

## 工具使用演示

![](https://image.3001.net/images/20221018/1666090883_634e8783bdc77cca905de.gif)

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_-2.0_](https://github.com/matanolabs/matano/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Matano** ：【[ _GitHub传送门_](https://github.com/matanolabs/matano)】

## 参考资料

> [
> _https://github.com/matanolabs/matano#_](https://github.com/matanolabs/matano)
>
> [
> _https://vector.dev/docs/reference/vrl/_](https://vector.dev/docs/reference/vrl/)
>
> [
> _https://www.elastic.co/guide/en/ecs/current/index.html_](https://www.elastic.co/guide/en/ecs/current/index.html)
>
> [ _https://www.matano.dev/docs_](https://www.matano.dev/docs)

