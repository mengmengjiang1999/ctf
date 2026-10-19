![](https://image.3001.net/images/20221125/1669361012_63806d74e9baa100b6e75.png!small)

## 关于nuvola

nuvola是一款功能强大的针对AWS环境的自动化安全分析工具，该工具可以使用通过Yaml语句创建的简单的预定义可扩展的自定义规则来转储AWS环境中的各种数据，并对AWS环境的配置信息和服务进程执行自动/手动安全分析。

这项目的主要目标是创建一个抽象的数字化云平台副本，可以帮助广大研究人员更好地研究和分析AWS云环境安全，其中还会覆盖活动目录安全和BloodHound等。

该工具还提供了一个图形数据库，可以增加发现不同攻击路径的可能性，而且还可以用作离线的轻量级数字化拷贝。

## 工具要求

> 1、docker-compose；
>
>
> 2、一个AWS账号，需配置awscli具备云环境资源的完整访问权，最好使用ReadOnly模式（arn:aws:iam::aws:policy/ReadOnlyAccess）；

## 工具下载&构建

由于该工具基于Golang开发，因此我们需要在本地设备上安装并配置好Go环境。

首先，我们需要使用下列命令将该项目源码克隆至本地，并切换到项目目录下

    
    
    git clone --depth=1 https://github.com/primait/nuvola.git
    
    cd nuvola

接下来，创建并编辑.env文件，然后设备你的数据库用户名、密码和URL地址：

    
    
    cp .env_example .env;

然后使用下列命令开启Neo4j Docker实例：

    
    
    make start

最后，使用make命令构建项目源码即可：

    
    
    make build

## 工具使用

第一步：首先你需要导出所有支持的AWS服务配置信息，并将数据加载到Neo4j数据库中：

    
    
    ./nuvola dump -profile default_RO -outputdir ~/DumpDumpFolder -format zip

第二步：将之前执行的导出操作所拿到的数据导入到Neo4j数据库中：

    
    
    ./nuvola assess -import ~/DumpDumpFolder/nuvola-default_RO_20220901.zip

第三步：使用[
_预定义规则集_](https://github.com/primait/nuvola/tree/master/assess/rules)对加载到Neo4j数据库中的数据执行静态安全审计分析：

    
    
    ./nuvola assess

第四步：或者，使用[ _Neo_ _4_ _j浏览器_](https://neo4j.com/docs/operations-manual/current/installation/neo4j-browser/)对数据执行手动安全分析：

![](https://image.3001.net/images/20221125/1669363326_6380767eb7d3c151340d2.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/primait/nuvola/blob/master/LICENSE.md)开源许可证协议。

## 项目地址

 **nuvola** ：【[ _GitHub传送门_](https://github.com/primait/nuvola)】

## 参考资料

> [ _https://neo4j.com/docs/operations-> manual/current/installation/neo4j-browser/_](https://neo4j.com/docs/operations-> manual/current/installation/neo4j-browser/)
>
> [
> _https://github.com/primait/nuvola/tree/master/assets/slides/RomHack_2022-You_shall_not_PassRole.pdf_](https://github.com/primait/nuvola/tree/master/assets/slides/RomHack_2022-You_shall_not_PassRole.pdf)
>
> [
> _https://github.com/primait/nuvola/tree/master/assets/demos/_](https://github.com/primait/nuvola/tree/master/assets/demos/)

