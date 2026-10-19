![](https://image.3001.net/images/20220210/1644479984_6204c5f01ea39c717bdd5.jpeg!small)  

## 关于Second Order

Second
Order是一款功能强大的子域名接管漏洞安全扫描工具，该工具可以通过网络爬虫爬取App，并收集匹配特定规则或以特定形式响应数据的URL地址以及其他数据，以期帮助广大研究人员扫描Web应用程序并发现其中潜在的二级子域名接管问题。

## 工具安装

### 直接使用

广大研究人员可以直接从该项目的【[ _Releases页面_](https://github.com/mhmdiaa/second-order/releases/latest)】下载预构建好的工具代码，然后解压之后便可直接使用。

### 源码安装

该工具基于Go语言开发，因此广大研究人员在使用该工具之前还需要安装并配置好Go语言环境，我们建议使用Go v1.17版本。安装命令如下：

    
    
    go install -v github.com/mhmdiaa/second-order@latest

### Docker安装

    
    
    docker pull mhmdiaa/second-order

## 工具使用

### 命令行选项

    
    
    -target string
    
            设置目标URL地址
    
      -config string
    
            配置文件 (默认为"config.json")
    
      -depth int
    
            爬取深度 (默认为1)
    
      -header value
    
         Header名称和值，中间用分号隔开，例如'Name: Value'
    
      -insecure
    
            接受不受信任的SSL /TLS证书
    
      -output string
    
            存储输出结果的目录 (默认为"output")
    
      -threads int
    
            运行线程数量 (默认为10)

### 配置文件

该工具已在项目的[ _config_](https://github.com/mhmdiaa/second-order/blob/master/config)目录中提供了参考的配置文件样例：

>
> 1、LogQueries：该文件设置的是工具在爬取页面中需搜索的“标签”-“属性”的映射。比如说，“a”:“href”代表的是工具将记录每个a标签的每个href属性。
>
>
> 2、LogNon200Queries：该文件设置的是工具在爬取页面中需搜索的“标签”-“属性”的映射，并只会记录没有返回“200”状态码的有效URL地址。
>
> 3、LogInline：需要记录内部内容的标签立标，比如说“title”和“script”等等。

## 数据输出

该工具所有的扫描结果都将存储在JSON文件中，我们可以指定需要存储的具体数据以及位置。

 **LogQueries的输出结果存储在attributes.json中：**

    
    
    {
    
        "https://example.com/": {
    
            "input[name]": [
    
                "user",
    
                "id",
    
                "debug"
    
            ]
    
        }
    
    }

 **LogNon200Queries的输出结果存储在non-200-url-attributes.json中：**

    
    
    {
    
        "https://example.com/": {
    
            "script[src]": [
    
                "https://cdn.old_abandoned_domain.com/app.js",
    
            ]
    
        }
    
    }

 **LogInline的输出结果存储在inline.json中：**

    
    
    {
    
        "https://example.com/": {
    
            "title": [
    
                "Example - Home"
    
            ]
    
        },
    
          "https://example.com/login": {
    
            "title": [
    
                "Example - login"
    
            ]
    
        }
    
    }

## 工具使用建议

> 1、检测二级子域名接管：[ _takeover_ _.json_](https://github.com/mhmdiaa/second-> order/blob/master/config/takeover.json)；
>
> 2、收集标签内容以及导入的JS代码：[ _javascript_ _.json_](https://github.com/mhmdiaa/second-> order/blob/master/config/javascript.json)；
>
> 3、查找目标主机托管的静态文件：[ _cdn.json_](https://github.com/mhmdiaa/second-> order/blob/master/config/cdn.json)；
>
> 4、收集<input>的name属性并构建定制的暴力破解字典参数：[ _parameters_
> _.json_](https://github.com/mhmdiaa/second-> order/blob/master/config/parameters.json)；

## 项目地址

 **Second Order：** 【[ _GitHub传送门_](https://github.com/mhmdiaa/second-order)】

## 参考资料

> [ _https://shubs.io/high-frequency-security-bug-> hunting-120-days-120-bugs/#secondorder_](https://shubs.io/high-frequency-> security-bug-hunting-120-days-120-bugs/#secondorder)
>
> [ _https://edoverflow.com/2017/broken-link-> hijacking/_](https://edoverflow.com/2017/broken-link-hijacking/)
>
> [ _https://github.com/mhmdiaa/second-> order/blob/master/config_](https://github.com/mhmdiaa/second-> order/blob/master/config)

