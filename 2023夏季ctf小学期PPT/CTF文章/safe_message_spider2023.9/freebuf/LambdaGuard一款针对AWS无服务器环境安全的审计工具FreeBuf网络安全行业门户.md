![](https://image.3001.net/images/20220624/1656051066_62b5557a80c76edfa3711.png!small)

## 关于LambdaGuard

AWS Lambda是由Amazon Web
Services提供的事件驱动的无服务器计算平台。它是一种计算服务，支持开发人员运行代码以响应各种事件，并自动管理代码所需的计算资源。

而LambdaGuard则是一款针对AWS
Lambda的安全审计工具，该工具旨在创建资产可见性并提供可操作的结果。它可以从安全角度提供统计分析、AWS服务依赖性和配置检查方面的更有意义的安全态势概述。

## 工具要求

> Python 3.6 +
>
> Java 11（可选，SonarQube需要使用）

## 工具安装&配置

### PyPI安装

在本地设备上安装并配置好Python 3环境之后，我们可以使用pip3命令来安装LambdaGuard：

    
    
    pip3 install lambdaguard

### GitHub安装

除此之外，广大研究人员也可以使用下列命令将该项目源码克隆至本地，并完成代码安装：

    
    
    git clone https://github.com/Skyscanner/lambdaguard
    
    cd lambdaguard
    
    sudo make install

### AWS访问

工具安装完成之后，我们还需要相关的AWS访问密钥，以及运行LambdaGuard的权限：

    
    
    make aws

然后在“~/.aws/credentials”路径下使用新创建的密钥来创建一个配置文件：

    
    
    [LambdaGuardProfile]
    
    aws_access_key_id = ...
    
    aws_secret_access_key = ...

除此之外，你也可以直接在命令行界面中以参数的形式直接提供访问密钥，但不推荐这种使用方式。

## 工具运行

    
    
    lambdaguard --help：查看工具帮助信息
    
    lambdaguard --function arn:aws:lambda:function：需要测试的AWS Lambda
    
    lambdaguard --input function-arns.txt：以文件列表的形式输入测试目标
    
    lambdaguard --output /tmp/lambdaguard：输出结果文件路径
    
    lambdaguard --profile LambdaGuardProfile：工具配置文件
    
    lambdaguard --keys ACCESS_KEY_ID SECRET_ACCESS_KEY：AWS访问密钥
    
    lambdaguard --region eu-west-1：设置AWS实例区域
    
    lambdaguard --verbose：开启Verbose模式

## SonarQube-静态代码分析

下载sonar-scanner-cli：【[ _点我下载_](https://github.com/SonarSource/sonar-scanner-cli)】

### 构建SonarQube

    
    
    make sonarqube

### 使用SonarQube

    
    
    lambdaguard --sonarqube config.json

配置文件格式如下：

    
    
    {
    
        "command": "sonar-scanner -X",
    
        "url": "http://localhost:9000",
    
        "login": "admin",
    
        "password": "admin"
    
    }

## 工具开发&代码贡献

    
    
    make -B clean
    
    make dev
    
    . dev/bin/activate
    
    make install-dev
    
    make test

## 许可证协议

本项目的开发与发布遵循[Apache-2.0](https://github.com/Skyscanner/LambdaGuard/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **LambdaGuard：** 【[ _GitHub传送门_](https://github.com/Skyscanner/LambdaGuard)】

