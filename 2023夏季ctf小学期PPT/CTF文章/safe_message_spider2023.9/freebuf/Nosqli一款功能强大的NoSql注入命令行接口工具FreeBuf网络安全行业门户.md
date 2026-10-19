![](https://image.3001.net/images/20201201/1606834916_5fc65ae466e65057212bc.png!small)  

## Nosqli

Nosqli是一款功能强大的NoSql注入命令行接口工具，本质上来说，它就是一款NoSQL扫描和注入工具。Nosqli基于Go语言开发，是一款易于使用的NoSql注入工具，并且提供了完整的命令行接口，而且支持安全研究人员根据自己的需要来进行自定义配置。

该工具的运行速度非常快，而且扫描结果准确，具备高可用性。除此之外，其命令行接口的使用也非常简单。

## 功能介绍

Nosqli当前支持针对MongoDB的NoSql注入检测，该工具目前可以执行下列测试：

  * 基于错误的测试：注入各种字符和Payload，扫描已知的Mongo错误响应；
  * 布尔盲注测试：注入包含True/False参数的Payload，并尝试判断是否存在注入点；
  * 基于时间的测试：尝试向目标服务器注入时间延迟，并根据响应判断是否存在注入点；

## 工具下载

广大研究人员请直接访问该项目的[ _Releases页面_](https://github.com/Charlie-belmer/nosqli/releases)并现在对应操作系统的最新版本Nosqli。下载完成后，安装在指定路径，或直接从本地文件目录中运行。

![](https://image.3001.net/images/20201201/1606834932_5fc65af4593547cc64989.png!small)

## 工具使用

广大研究人员可以直接按照下列方式直接运行注入命令或查看帮助信息。

    
    
    $ nosqli
    
    NoSQLInjector is a CLI tool for testing Datastores that
    
    do not depend on SQL as a query language.
    
     
    
    nosqli aims to be a simple automation tool for identifying and exploiting
    
    NoSQL Injection vectors.
    
     
    
    Usage:
    
      nosqli [command]
    
     
    
    Available Commands:
    
      help        Help about any command
    
      scan        Scan endpoint for NoSQL Injection vectors
    
      version     Prints the current version
    
     
    
    Flags:
    
          --config string       config file (default is $HOME/.nosqli.yaml)
    
      -d, --data string         Specify default post data (should not include any injection strings)
    
      -h, --help                help for nosqli
    
      -p, --proxy string        Proxy requests through this proxy URL. Defaults to HTTP_PROXY environment variable.
    
      -r, --request string      Load in a request from a file, such as a request generated in Burp or ZAP.
    
      -t, --target string       target url eg. http://site.com/page?arg=1
    
      -u, --user-agent string   Specify a user agent
    
     
    
    Use "nosqli [command] --help" for more information about a command.
    
     
    
    $ nosqli scan -t http://localhost:4000/user/lookup?username=test
    
    Running Error based scan...
    
    Running Boolean based scan...
    
    Found Error based NoSQL Injection:
    
      URL: http://localhost:4000/user/lookup?=&username=test
    
      param: username
    
      Injection: username='

大家可以使用存在漏洞的NodeJS应用程序或其他的NoSql注入实验平台来测试该工具的使用。

## 源码构建

如果大家想要自行动手构建源码，或针对特定的平台进行源码编译，大家可以先按照下列方式将该项目源码克隆至本地，然后安装依赖，最后手动构建项目。这里要求设备上安装好最新的Go开发远景，然后配置好GOPATH环境变量。

    
    
    $ git clone https://github.com/Charlie-belmer/nosqli
    
    $ cd nosqli
    
    $ go get ./..
    
    $ go install
    
    $ nosqli -h

## 运行测试

该工具自带了一个测试套件，研究人员可以在该项目根目录下运行go test来进行简单的注入检测：

    
    
    go test ./...

除此之外，Nosqli还提供了针对本地运行的已知易受攻击应用程序来进行注入的测试集。要使用集成测试，请安装并运行易受攻击的NodeJS
Mongo注入应用程序，或者我提供的PHP Lab。接下来，我们需要在运行命令时提供集成参数：

    
    
    go test ./... -args -integrations=true

## 项目地址

Nosqli：【[ _GitHub传送门_](https://github.com/Charlie-belmer/nosqli)】

