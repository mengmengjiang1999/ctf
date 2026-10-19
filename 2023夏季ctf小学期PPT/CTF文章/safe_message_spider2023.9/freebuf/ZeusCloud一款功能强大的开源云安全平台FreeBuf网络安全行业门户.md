![](https://image.3001.net/images/20230811/1691760866_64d638e294dc65b3e0ed7.png!small)  

## 关于ZeusCloud

ZeusCloud是一款功能强大的开源云安全平台，在该工具的帮助下，广大研究人员可以以最快的速度发现、确定优先级并修复云平台环境中的安全风险。

## 工具特性

> 1、帮助建立AWS帐户的资产清单；
>
> 2、根据公开暴露（资产）、IAM、漏洞等元素来发现攻击路径；
>
> 3、使用图形上下文对调查结果进行优先级排序；
>
> 4、按照分步指引修复发现的安全问题；
>
> 5、自定义安全和合规控制以满足不同的需求；
>
> 6、符合PCI DSS、CIS、SOC 2等法规遵从性标准；

## 功能介绍

> 1、发现攻击路径；
>
> 2、图形化上下文；
>
> 3、图形化访问查看；
>
> 4、识别错误配置；
>
> 5、自定义配置；
>
> 6、安全即代码；
>
> 7、分步指引安全问题修复；
>
> 8、确保云安全态势遵从PCI DSS、CIS基准测试等；

![](https://image.3001.net/images/20230811/1691760886_64d638f6bf78dd4222ef7.gif)

## 工具安装&部署

### 本地部署ZeusCloud

首先，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone --recurse-submodules https://github.com/Zeus-Labs/ZeusCloud.git

接下来，切换到项目目录中，并运行构建脚本：

    
    
    cd ZeusCloud
    
    make quick-deploy

然后打开浏览器，并访问http://localhost:80，即可开始使用ZeusCloud。

### 容器运行

以开发模式运行容器：

    
    
    cd frontend && yarn && cd -    
    docker-compose down && docker-compose -f docker-compose.dev.yaml --env-file .env.dev up --build

重制neo4j或postgres数据：

    
    
    rm -rf .compose/neo4j
    
    rm -rf .compose/postgres

后端部署：

    
    
    docker-compose -f docker-compose.dev.yaml --env-file .env.dev up --no-deps --build backend

然后打开浏览器，并访问http://localhost:80，即可开始使用ZeusCloud。

### ZeusCloud与AWS连接

部署好ZeusCloud之后，我们还需要将其与需要扫描的目标AWS账号连接。点击Settings > Add new
account，填写目标账号名称，然后选择Named Profile或Connection
Method，在Profile标签页中，选择之前创建的账号信息即可。

## 工具使用

连接了账号之后，ZeusCloud将会对其进行扫描并运行多种安全规则，整个过程大约10-15分钟。

通过UI监控整个过程，Settings页面将会显示任务进度完成的百分比。

除此之外，我们也可以通过终端窗口来监控：

![](https://image.3001.net/images/20230811/1691760929_64d639215c55fca11c397.png!small)

## 工具使用DEMO

 **演示地址** ：【[ _点我尝试_](https://demo.zeuscloud.io/)】

## 许可证协议

本项目的开发与发布遵循[ _Apache_ _-2.0_](https://github.com/Zeus-Labs/ZeusCloud/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **ZeusCloud** ：【[ _GitHub传送门_](https://github.com/Zeus-Labs/ZeusCloud)】

## 参考资料

> [ _https://docs.zeuscloud.io/introduction/get-> started_](https://docs.zeuscloud.io/introduction/get-started)
>
> [ _https://demo.zeuscloud.io/_](https://demo.zeuscloud.io/)

