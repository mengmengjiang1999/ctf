![](https://image.3001.net/images/20220928/1664368214_63343e562f32b79df93c6.png!small)  

## 关于CATS

CATS是一款功能强大的针对OpenAPI的REST
API模糊与逆向测试工具，在不需要复杂配置和代码编写的情况下，CATS能够自动生成和运行测试，并提供测试报告。工具生成的所有测试都是通过一组预定义的93个模糊测试器自动生成和运行的，并涵盖了广泛的边界测试和负面场景。更重要的是，我们可以利用CATS动态生成请求Payload并编写简单的端到端功能测试。

## 功能介绍

> 1、覆盖率高：基于大量场景自动生成测试，覆盖每个字段和Header；
>
> 2、智能化：根据数据类型和约束生成测试；根据测试场景，每个模糊测试器都有特定的期望值；
>
> 3、高度可配置：提供了大量自定义配置，可以过滤特定的模糊测试器、HTTP响应代码、HTTP方法和请求路径，并提供业务上下文等；
>
> 4、自我修复：在生成测试时，任何OpenAPI规范更改都会自动拾取；
>
> 5、简单易用：学习曲线平坦，配置和语法直观，易于使用；
>
> 6、运行速度快：写入、运行和报告测试的自动过程，在几分钟内即可涵盖数千种场景；

## 工具安装

### Homebrew

    
    
    > brew tap endava/tap
    
    > brew install cats

### 手动安装

CATS捆绑了一个可执行JAR以及原生代码，原生代码不需要安装Java。访问该项目【[
_Releases页面_](https://github.com/Endava/cats/releases)】并下载了对应操作系统的原生代码之后，我们可以将其添加到PATH中：

    
    
    sudo cp cats /usr/local/bin/cats

然后下载cats_autocomplete脚本自动完成安装：

    
    
    source cats_autocomplete

接下来，我们就可以运行下列命令来启动CATS了：

    
    
    java -jar cats.jar

### 源码构建

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Endava/cats.git

接下来，安装并配置好Java 17+和Maven，然后切换到项目目录并运行下列Maven命令来构建该项目：

    
    
    ./mvnw package -Dquarkus.package.type=uber-jar

此时我们将会在target目录中看到cats-runner.jar，然后使用下列命令运行CATS即可：

    
    
    java -jar cats-runner.jar

## 工具运行

### 查看工具帮助信息

    
    
    > cats -h

### 黑盒模式

    
    
    > cats --contract=openapi.yaml --server=http://localhost:8080 --headers=headers.yml --blackbox

### 上下文模式

    
    
    > cats --contract=openapi.yaml --server=http://localhost:8080 --headers=headers.yml --refData=referenceData.yml

## 工具运行截图

![](https://image.3001.net/images/20220928/1664368292_63343ea43a4673ca3dfc4.png!small)![](https://image.3001.net/images/20220928/1664368303_63343eaf07880f91f1ae2.png!small)

![](https://image.3001.net/images/20220928/1664368310_63343eb61f3686c380872.png!small)

![](https://image.3001.net/images/20220928/1664368320_63343ec0acbedde07d90e.png!small)

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_-2.0_](https://github.com/Endava/cats/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **CATS** ：【[ _GitHub传送门_](https://github.com/Endava/cats)】

## 参考资料

> [ _https://ludovicianul.github.io/2020/10/05/github-api-> testing/_](https://ludovicianul.github.io/2020/10/05/github-api-testing/)
>
> [
> _https://ludovicianul.github.io/2020/09/09/cats/_](https://ludovicianul.github.io/2020/09/09/cats/)

