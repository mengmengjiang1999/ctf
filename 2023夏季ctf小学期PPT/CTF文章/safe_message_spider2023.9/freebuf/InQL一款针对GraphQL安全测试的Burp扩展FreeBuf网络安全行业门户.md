![](https://image.3001.net/images/20200408/1586317965_5e8d4a8d708ed.png!small)

##  InQL Scanner

 **InQL Scanner是一款安全测试工具，也是一个Burp
Suite扩展，在它的帮助下，广大研究人员可以更好地对[GraphQL](https://graphql.org/)技术进行安全审计。**

InQL可以直接以脚本的方式单独运行，或者以[Burp Suite](https://portswigger.net/burp)扩展的方式执行任务。

##  工具下载

广大研究人员可以使用下列命令将InQL项目源码克隆至本地：

    
    
    git clone https://github.com/doyensec/inql.git

###  InQL单独运行-脚本

在你的主机环境中安装好Python环境之后，运行inql，脚本将会向目标GraphQL节点发送一个自检查询请求，并尝试获取下列元数据信息：

> 1、Query/Mutation/Subscription；
>
> 2、字段和参数；
>
> 3、对象和自定义对象类型；

InQL可以检查自省查询的结果，并以不同的数据格式生成干净简洁的文档，支持的格式有HTML和JSON等。除此之外，InQL还可以根据所有已知基础数据类型生成模板（可选占位符）。

最终的结果HTML文档页面中将包含关于全部有效Query/Mutation/Subscription的详细信息，样例如下：

![](https://image.3001.net/images/20200408/1586318024_5e8d4ac8f2378.png!small)

在下面给出的样例图中，显示的是模板生成的使用：

![](https://image.3001.net/images/20200408/1586318038_5e8d4ad6f148a.png!small)

##  工具帮助信息

如需查看InQL支持的所有选项参数，可以使用help命令查看：

    
    
    usage: inql [-h] [-t TARGET] [-f SCHEMA_JSON_FILE] [-k KEY] [-p PROXY]
    
                    [--header HEADERS HEADERS] [-d] [--generate-html]
    
                    [--generate-schema] [--generate-queries] [--insecure]
    
                    [-o OUTPUT_DIRECTORY]
    
        InQL Scanner
    
        optional arguments:
    
          -h, --help            show this help message and exit
    
          -t TARGET             Remote GraphQL Endpoint (https://<Target_IP>/graphql)
    
          -f SCHEMA_JSON_FILE   Schema file in JSON format
    
          -k KEY                API Authentication Key
    
          -p PROXY              IP of web proxy to go through ([http://127.0.0.1:8080](http://127.0.0.1:8080/))
    
          --header HEADERS HEADERS
    
          -d                    Replace known GraphQL arguments types with placeholder
    
                                values (useful for Burp Suite)
    
          --generate-html       Generate HTML Documentation
    
          --generate-schema     Generate JSON Schema Documentation
    
          --generate-queries    Generate Queries
    
          --insecure            Accept any SSL/TLS certificate
    
          -o OUTPUT_DIRECTORY   Output Directory

##  InQL Burp Suite扩展

从InQL的v1.0版本开始，InQL就已经支持以Burp
Suite扩展的方式执行了。在这个模式下，该工具不仅拥有独立脚本的全部功能，而且还可以借助Burp
Suite来给广大研究人员提供更加便捷的用户接口来执行查询。

InQL的Burp Suite扩展模式有以下几种功能特性：

> 1、搜索查询已知的GraphQL URL路径，工具降火搜索和匹配已知的值来在目标站点内检测GraphQL节点；
>
> 2、搜索暴露在外的GraphQL开发控制台（GraphiQL、GraphQL Playground和其他常见控制台）；
>
> 3、使用自定义GraphQL标签来显示包含了GraphQL的每一个HTTP请求/响应；
>
> 4、通过向Burp的Repeater工具发送请求来生成模板；
>
> 5、通过使用自定义设置标签来对工具进行配置；

如果你想在Burp Suite中使用InQL，那么你就需要导入Python扩展：

> 1、下载Jython Jar：【[点我下载](https://www.jython.org/download)】；
>
> 2、开启Burp Suite；
>
> 3、点击Extender标签 > 选项 > Python 环境 >设置Jython独立Jar包地址；
>
> 4、点击Extender标签 > 扩展 > 添加 > 扩展类型 > 选择Python；
>
> 5、下载最新版本的inql_burp.py：【[点我下载](https://github.com/doyensec/inql/releases)】；
>
> 6、点击扩展文件 > 设置inql_burp.py的地址 > 下一步；
>
> 7、如果一切配置妥当，此时的输出结果应该为：InQL Scanner Started!；

注意：之后我们会考虑将InQL扩展整合进Burp的BApp Store之中。

##  Burp扩展使用

InQL Burp扩展的使用非常简单，我们只需要按照下列步骤操作即可：

1、在顶部的输入窗口中，加载一个GraphQL节点，或加载一个JSON文件；

2、点击“加载”按钮；

3、等待几秒钟之后，左侧的面板将会刷新所选目标节点的目录结构，该目录结构的参考样例如下：

![](https://image.3001.net/images/20200408/1586318200_5e8d4b78dda7a.png!small)

4、选择Query/Mutation/Subscription中的任意一个，该工具将会在主文本域中显示对应的模板；

##  项目地址

> InQL Scanner：【[GitHub传送门](https://github.com/doyensec/inql)】

 ***
参考来源：[doyensec](https://github.com/doyensec/inql)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

