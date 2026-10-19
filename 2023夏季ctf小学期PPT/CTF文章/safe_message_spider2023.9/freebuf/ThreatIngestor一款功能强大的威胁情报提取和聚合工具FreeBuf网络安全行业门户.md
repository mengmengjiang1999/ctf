![](https://image.3001.net/images/20191101/1572540599_5dbb10b7e3871.jpg!small)

## ThreatIngestor

ThreatIngestor是一款功能强大的威胁情报提取和聚合工具，该工具易于扩展，并且能够从多个威胁情报feed收集并汇聚威胁情报信息以及入侵威胁指标IoC。该工具整合了[
_ThreatKB_](https://github.com/InQuest/ThreatKB)和[ _MISP_](https://www.misp-project.org/)，并且可以利用[ _SQS_](https://aws.amazon.com/sqs/)、[
_Beanstalk_](https://beanstalkd.github.io/)和[
_自定义插件_](https://inquest.readthedocs.io/projects/threatingestor/en/latest/developing.html)来跟很多现有的工作流实现无缝接入。

## 工具概览

ThreatIngestor通过配置之后，可以监控Twitter、RSS
feed以及其他的威胁情报源。除此之外，ThreatIngestor还可以提取类似恶意IP地址、恶意域名和YARA签名等更有价值的信息，并将其发送至其他的系统进行更加深入的分析。

![](https://image.3001.net/images/20191101/1572540609_5dbb10c1c3f91.png!small)

实际上，线上恶意活动的最新信息会一直源源不断地发布出来，但手动编译所有的这些信息需要花费大量的手动操作和时间。而ThreatIngestor可以尽可能多地自动化完成这些工作，因此广大研究人员可以将精力和时间专注到更加重要的事情上。

![](https://image.3001.net/images/20191101/1572540617_5dbb10c903f5c.png!small)

该工具是一款完全模块化的工具，并且高度可配置、可扩展，因此广大研究人员可以根据自己的需要来对其进行高度定制化修改，以接入现有的工作流中。

## 工具安装

ThreatIngestor的正常运行需要Python 3.6+环境以及相应的开发库支持。

首先，运行下列命令配置Python 3环境：

    
    
    sudo apt-get install python3-dev

广大研究人员可以使用下列命令从PyPI直接安装ThreatIngestor：

    
    
    pip install threatingestor

默认配置下，ThreatIngestor并不会直接安装所有的功能插件，如果你需要使用特定的插件，你就需要为该插件配置相应的依赖组件。比如说，如果你想使用SQS：

    
    
    pip install threatingestor[sqs]

如果你想使用Beanstalk和Twitter的话：

    
    
    pip install threatingestor[beanstalk,twitter]

如果需要使用其他功能插件的话，还需要安装额外的依赖库：

    
    
    pip install threatingestor[all]

## 工具使用

创建一个新的config.yml文件，并且配置每一个你所需要使用的威胁情报源和操作器模块。接下来，运行脚本：

    
    
    threatingestor config.yml

默认情况下，该工具会一直在后台运行，并且每隔15分钟便会导出一份情报收集报告。  

## 插件

ThreatIngestor使用了“source”(input)和“operator”(output)插件，除此之外该工具还支持整合以下功能插件：

### 威胁情报源：

> [Beanstalk work
> queues](https://inquest.readthedocs.io/projects/threatingestor/en/latest/sources/beanstalk.html)
>
> [Git
> repositories](https://inquest.readthedocs.io/projects/threatingestor/en/latest/sources/git.html)
>
> [GitHub repository
> search](https://inquest.readthedocs.io/projects/threatingestor/en/latest/sources/github.html)
>
> [RSS
> feeds](https://inquest.readthedocs.io/projects/threatingestor/en/latest/sources/rss.html)
>
> [Amazon SQS
> queues](https://inquest.readthedocs.io/projects/threatingestor/en/latest/sources/sqs.html)
>
>
> [Twitter](https://inquest.readthedocs.io/projects/threatingestor/en/latest/sources/twitter.html)
>
> [Generic web
> pages](https://inquest.readthedocs.io/projects/threatingestor/en/latest/sources/web.html)

### 操作器：

> [Beanstalk work
> queues](https://inquest.readthedocs.io/projects/threatingestor/en/latest/operators/beanstalk.html)
>
> [CSV
> files](https://inquest.readthedocs.io/projects/threatingestor/en/latest/operators/csv.html)
>
>
> [MISP](https://inquest.readthedocs.io/projects/threatingestor/en/latest/operators/misp.html)
>
> [MySQL
> table](https://inquest.readthedocs.io/projects/threatingestor/en/latest/operators/mysql.html)
>
> [SQLite
> database](https://inquest.readthedocs.io/projects/threatingestor/en/latest/operators/sqlite.html)
>
> [Amazon SQS
> queues](https://inquest.readthedocs.io/projects/threatingestor/en/latest/operators/sqs.html)
>
>
> [ThreatKB](https://inquest.readthedocs.io/projects/threatingestor/en/latest/operators/threatkb.html)
>
>
> [Twitter](https://inquest.readthedocs.io/projects/threatingestor/en/latest/operators/twitter.html)

ThreatIngestor运行截图

![](https://image.3001.net/images/20191101/1572540666_5dbb10fa3eab3.png!small)

## 工具地址

> ThreatIngestor：【[
> _GitHub传送门_](https://inquest.readthedocs.io/projects/threatingestor/en/latest/_images/webui-> domains.png)】

 *** 参考来源：[
_InQuest_](https://github.com/InQuest/ThreatIngestor)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

