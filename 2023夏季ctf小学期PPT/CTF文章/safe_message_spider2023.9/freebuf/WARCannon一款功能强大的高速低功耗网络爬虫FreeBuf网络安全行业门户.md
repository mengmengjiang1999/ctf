![](https://image.3001.net/images/20210907/1631017651_61375ab3c4fdd584ea5cf.png!small)

## 关于WARCannon

WARCannon是一款功能强大的 **高速低功耗网络爬虫** ，可以帮助广大研究人员以最简单和快速的方式爬取网络资源。

 **WARCannon支持的功能如下：**

> 针对真实场景中常见的爬取数据构建和测试正则表达式模式；
>
> 支持加载常见爬取数据库，支持并行处理；
>
> 支持大规模数据计算处理（异步）；
>
> 数据存储，轻松检索爬取结果；

## 工作机制

WARCannon巧妙地利用AWS技术，可以横向扩展以支持任何规模的数据爬取，并且能够根据需求转换服务传输地区以将成本降至最低，然后以最快的速度从S3中提取数据，每个节点速度高达100Gbps，并使用数百个CPU内核进行并行处理，然后通过DynamoDB和CloudFront报告爬取状态，并通过S3存储结果。

## 工具安装

WARCannon的运行需要我们安装并配置好下列组件：

> awscli (v2)
>
> terraform (v0.11)
>
> jq
>
> jsonnet
>
> npm (v12或v14)

接下来，使用下列命令将该项目源码克隆至本地，然后拷贝配置样本文件：

    
    
    $ git clone git@github.com:c6fc/warcannon.git
    
    $ cd warcannon
    
    warcannon$ cp settings.json.sample settings.json

## 开发正则表达式

首先，我们需要打开lambda_functions/warcannon/matches.js文件，然后修改regex_patterns对象来引入正则表达式。数据格式为“name:
pattern”格式。下面给出的是默认搜索数据集的一个样本：

    
    
    exports.regex_patterns = {
    
    "access_key_id": /(\'A|"A)(SIA|KIA|IDA|ROA)[JI][A-Z0-9]{14}[AQ][\'"]/g,
    
    };

除此之外，我们还可以从指定域名爬取数据：

    
    
    exports.domains = ["example1.com", "example2.com"];

## 工具运行演示

![](https://image.3001.net/images/20210907/1631017692_61375adc78bc8f91f4c36.png!small)

## 项目地址

 **WARCannon：** 【[ _GitHub传送门_](https://github.com/c6fc/warcannon)】

 **参考资料：**

> [ _https://regexr.com/﻿_](https://regexr.com/)
>
> [ _https://commoncrawl.org/_](https://commoncrawl.org/)
>
> [ _https://registry.opendata.aws/_](https://registry.opendata.aws/)

