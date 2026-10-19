![](https://image.3001.net/images/20190924/1569303086_5d89aa2e09e36.png!small)

## 工具介绍

Scout Suite是一款针对云集群环境的开源安全审计工具，主要针对的是云端环境的安全状况。通过使用云服务提供商暴露的API，Scout
Suite可以从高安全风险区域收集配置数据以备研究人员进行人工审计。值得一提的是，Scout
Suite在进行完安全审计之后，可以自动给研究人员呈现清晰详尽的攻击面概览，而无需研究人员浏览繁杂的Web控制台信息。

注意：当前版本的Scout Suite为稳定版，并且会定期更新，同时会对内部功能和实现方法进行修改。

## 工具支持

当前版本的Scout Suite支持（或计划支持）下列云服务提供商：

> 1、Amazon Web Services
>
> 2、Microsoft Azure (测试版)
>
> 3、Google Cloud Platform
>
> 4、Alibaba Cloud (早期版本)
>
> 5、Oracle Cloud Infrastructure (早期版本)

## 工具安装

依赖组件

Scout Suite采用Python编程语言开发，目前仅支持下列Python版本：

    
    
    3.5
    
    3.6
    
    3.7

我们建议大家在虚拟环境中配置和使用Scout Suite。

其他依赖库，可以从[
_requirements.txt_](https://github.com/nccgroup/ScoutSuite/blob/master/requirements.txt)文件中获取。

## 工具安装

### 通过pip命令安装：

    
    
    $ virtualenv -p python3 venv
    
    $ source venv/bin/activate
    
    $ pip install scoutsuite
    
    $ scout --help

### 通过git命令安装：

    
    
    $ git clone <https://github.com/nccgroup/ScoutSuite>
    
    $ cd ScoutSuite
    
    $ virtualenv -p python3 venv
    
    $ source venv/bin/activate
    
    $ pip install -r requirements.txt
    
    $ python scout.py --help

## 工具使用

使用下列命令即可获取所有可用的命令行选项：

    
    
    $ python scout.py --help

我们还可以使用下列命令来获取指定的提供商帮助信息：

    
    
    $ python scout.py PROVIDER --help

更多详细信息，请点击【[ _这里_](https://github.com/nccgroup/ScoutSuite/wiki)】。

在执行完API调用之后，Scout
Suite将会创建一个本地HTML报告，并使用默认浏览器打开。需要注意的是，如果只输入了部分命令，那么命令行会尝试推测并补全命令参数。比如说，我们可使用下列命令来选择属性文件：

    
    
    $ python scout.py aws --profile PROFILE

## 凭证

假设你已经配置好了云服务提供商的命令行工具，并已设置了凭证信息，那么我们就可以使用下列对应的命令来运行Scout Suite了。

### Amazon Web Services

    
    
    $ python scout.py aws

### Azure

    
    
    $ python scout.py azure --cli

### Google Cloud Platform

    
    
    $ python scout.py gcp --user-account

更多详细信息，请点击【[ _这里_](https://github.com/nccgroup/ScoutSuite/wiki)】。

## 项目地址

Scout Suite：【[ _GitHub传送门_](https://github.com/nccgroup/ScoutSuite)】

## 参考资料

> 1、[ _https://docs.microsoft.com/en-us/azure/security/azure-security-pen-> testing_](https://docs.microsoft.com/en-us/azure/security/azure-security-> pen-testing)
>
> 2、[ _https://www.microsoft.com/en-us/msrc/pentest-rules-of-> engagement_](https://www.microsoft.com/en-us/msrc/pentest-rules-of-> engagement)
>
> 3、[
> _https://cloud.google.com/terms/aup_](https://cloud.google.com/terms/aup)
>
> 4、[ _https://cloud.google.com/terms/_](https://cloud.google.com/terms/)

 *** 参考来源：[
_nccgroup_](https://github.com/nccgroup/ScoutSuite)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

