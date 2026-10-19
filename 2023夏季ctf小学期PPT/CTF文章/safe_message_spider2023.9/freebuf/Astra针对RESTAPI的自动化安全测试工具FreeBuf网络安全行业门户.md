![1.png](https://image.3001.net/images/20200403/1585917164_5e872cec51581.png!small)  

**REST即表述性状态传递（英文：Representational State
Transfer，简称REST）是一套新兴的WEB通讯协议，访问方式和普通的HTTP类似，平台接口分GET和POST两种请求方式。**

针对REST
API的渗透测试非常的复杂，因为不仅现有的API会不断更新和变化，而且还会不断增加新的API。对于广大安全研究人员、安全工程师和开发者们来说，Astra这款工具可以帮助他们完成大量工作，并在开发周期的早期过程中检测并修复安全漏洞。Astra可以自动检测并测试登录&注销功能（认证API），因此任何人都可以轻松将其集成到CICD管道中。除此之外，Astra还可以将API**作为输入参数来进行测试，并可在独立模式下测试大量API安全。

## 功能介绍

> 1、SQL注入
>
> 2、跨站脚本XSS
>
> 3、信息泄露
>
> 4、不安全的身份认证和会话管理
>
> 5、CSRF（包括Blind CSRF）
>
> 6、频率限制
>
> 7、CORS错误配置（包括CORS绕过技术）
>
> 8、JWT攻击
>
> 9、CRLF检测
>
> 10、XEE盲注

## 工具要求

> Linux或macOS
>
> Python 2.7
>
> MongoDB

## 工具安装``

    
    
    $ git clone https://github.com/flipkart-incubator/Astra
    
    $ cd Astra
    
    $ sudo pip install -r requirements.txt

## Docker安装

### 运行Mongo容器：

    
    
    $ docker pull mongo
    
    $ docker run --name astra-mongo -d mongo

### 安装GUI Docker：

    
    
    $ git clone https://github.com/flipkart-incubator/Astra.git
    
    $ cd Astra
    
    $ docker build -t astra .
    
    $ docker run --rm -it --link astra-mongo:mongo -p 8094:8094 astra

### 安装CLI Docker：

    
    
    $ git clone -b docker-cli https://github.com/flipkart-incubator/Astra.git
    
    $ cd Astra
    
    $ docker build -t astra-cli .
    
    $ docker run --rm -it --link astra-mongo:mongo astra-cli

## 依赖组件

    
    
    - requests
    
    - logger
    
    - pymongo
    
    - ConfigParser
    
    - pyjwt
    
    - flask
    
    - sqlmap

## 工具使用-命令行

    
    
    $ python astra.py --help
    
                          _
    
            /\       | |
    
           /  \   ___| |_ _ __ __ _
    
          / /\ \ / __| __| '__/ _` |
    
         / ____ \__ \ |_| | | (_| |
    
        /_/    \_\___/\__|_|  \__,_|
    
    usage: astra.py [-h] [-c {Postman,Swagger}] [-n COLLECTION_NAME] [-u URL]
    
                    [-headers HEADERS] [-method {GET,POST}] [-b BODY]
    
                    [-l LOGINURL] [-H LOGINHEADERS] [-d LOGINDATA]
    
    REST API Security testing Framework
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -c {Postman,Swagger}, --collection_type {Postman,Swagger}
    
                            Type of API collection
    
      -n COLLECTION_NAME, --collection_name COLLECTION_NAME
    
                            Type of API collection
    
      -u URL, --url URL     URL of target API
    
      -headers HEADERS, --headers HEADERS
    
                            Custom headers.Example: {"token" : "123"}
    
      -method {GET,POST}, --method {GET,POST}
    
                            HTTP request method
    
      -b BODY, --body BODY  Request body of API
    
      -l LOGINURL, --loginurl LOGINURL
    
                            URL of login API
    
      -H LOGINHEADERS, --loginheaders LOGINHEADERS
    
                            Headers should be in a dictionary format. Example:
    
                            {"accesstoken" : "axzvbqdadf"}
    
      -d LOGINDATA, --logindata LOGINDATA
    
                            login data of API

##  工具使用-Web接口

直接在命令行中运行api.py，然后打开浏览器，通过访问<http://127.0.0.1:8094>的进入工具Web接口：

    
    
    $ cd API
    
    $ python api.py

## 工具运行截图

### 新建扫描任务：

![2.png](https://image.3001.net/images/20200403/1585917251_5e872d434dfae.png!small)

### 生成扫描报告：

![3.png](https://image.3001.net/images/20200403/1585917260_5e872d4c258e0.png!small)![4.png](https://image.3001.net/images/20200403/1585917271_5e872d571fea0.png!small)

### 详细报告：

![5.png](https://image.3001.net/images/20200403/1585917285_5e872d653af35.png!small)

## 项目地址

Astra：【[ _GitHub传送门_](https://github.com/flipkart-incubator/Astra)】

参考文档：【[传送门](https://www.astra-security.info/)】

 *** 参考来源：[ _flipkart-incubator_](https://github.com/flipkart-incubator/Astra)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

