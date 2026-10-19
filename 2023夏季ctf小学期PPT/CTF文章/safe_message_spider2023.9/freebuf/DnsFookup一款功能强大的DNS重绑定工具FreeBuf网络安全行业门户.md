![](https://image.3001.net/images/20200304/1583314910_5e5f77de4752d.jpg!small)

**今天给大家介绍的这款工具名叫DnsFookup，这是一款功能强大的DNS重绑定工具，广大研究人员可以使用该工具来对目标DNS服务器进行安全测试。**

本质上来说，DnsFookup是一款[DNS重绑定](https://en.%2A%2A%2A%2A%2A%2A%2A%2A%2A.org/wiki/DNS_rebinding)框架，该框架包含下列组件：

> 1、一个DNS服务器；
>
> 2、Web API，用于创建新的子域名，控制DNS服务器和查看日志等；
>
> 3、整合了React App，让工具使用更加方便；

##  工具机制

该工具可以帮助我们创建DNS绑定，其功能类似一个Burp Collaborator，但是DnsFookup能提供的功能更加丰富和强大：

![](https://image.3001.net/images/20200304/1583314927_5e5f77efade7e.png!small)

在工具界面中，你可以指定DNS服务器需要解析的IP地址以及重复次数，目前版本的DnsFookup只支持A记录。接下来，你就可以直接在日志记录中查看到请求来源，以及解析结果了。

![](https://image.3001.net/images/20200304/1583314933_5e5f77f55f96f.png!small)

##  工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/makuga01/dnsFookup.git

##  工具运行

首先，我们需要检查.py文件中的参数配置信息，相关配置信息一般使用下列形式进行标注：

    
    
    """
    
        *** CONFIG ***
    
        """

当然了，别忘了修改下列文件中的Docker以及Redis密码：

    
    
    docker-compose.yml
    
        app.py
    
        dns_resources

接下来，可以使用下列命令配置Postgres和Redis：

    
    
    sudo docker-compose up

切换到./BE中，运行下列命令：

    
    
    pip3 install -r requirements.txt
    
        python3 dns.py # to start the dns server

如果仅出于测试目的的话，开发版服务器已经足够了：

    
    
    FLASK_APP=app.py
    
        FLASK_ENV=development
    
        flask run

接下来，在./FE中运行下列命令：

    
    
    npm install
    
        npm start

##  API文档

> 为了登录和使用API，你需要使用令牌来完成身份验证，并在application/json中设置Content-Type。

##  注册-/auth/signup

    
    
    POST /auth/signup

JSON主体：

    
    
    {
    
            "username": "marek",
    
            "password": "ffffffff"
    
        }

响应：

    
    
    {
    
            "name": "marek",
    
            "access_token": "eyJuYW1lIjoiMTMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzNyBTZUtyM1QgVDBLM24ifQo="
    
        }

##  登录-/auth/login

    
    
    POST /auth/signup

JSON主体：

    
    
    {
    
            "username": "marek",
    
            "password": "ffffffff"
    
        }

响应：

    
    
    {
    
            "name": "marek",
    
            "access_token": "eyJuYW1lIjoiMTMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzNyBTZUtyM1QgVDBLM24ifQo="
    
        }

##  注销-/auth/logout

    
    
    POST /auth/logout

响应：

    
    
    {
    
            "message": "Access token has been revoked"
    
        }

##  获取用户名

    
    
    GET /api/user

响应：

    
    
    {
    
            "name": "marek"
    
        }

##  创建新的令牌-/api/fookup/new

    
    
    POST /api/fookup/new

JSON主体：

    
    
    {
    
        "name":"dsads",
    
        "ip_props":
    
        {
    
        "1":{
    
        "ip":"123.0.0.1"
    
        ,"repeat":13
    
        },
    
        "2":{
    
        "ip":"3.2.1.1",
    
        "repeat": "4ever"
    
        }
    
        }
    
        }

响应：

    
    
    {
    
            "subdomain": "0dd4d9083d7647e1a5fd5f1444e655ce.gel0.space"
    
        }

###  使用样例1

假设，我们向工具提供下列内容：

    
    
    {
    
        "name":"dsads",
    
        "ip_props":
    
        {
    
        "1":{
    
        "ip":"1.1.1.1"
    
        ,"repeat":2
    
        },
    
        "2":{
    
        "ip":"2.2.2.2",
    
        "repeat": 1
    
        }
    
        }
    
        }

接下来，针对该域名使用host命令来进行测试：

    
    
    $host {domain}
    
        {domain} has address 1.1.1.1
    
        $host {domain}
    
        {domain} has address 1.1.1.1
    
        $host {domain}
    
        {domain} has address 2.2.2.2
    
        $host {domain}
    
        {domain} has address 1.1.1.1
    
        $host {domain}
    
        {domain} has address 1.1.1.1
    
        $host {domain}
    
        {domain} has address 2.2.2.2
    
        ...

###  使用样例2

    
    
    {
    
        "name":"dsads",
    
        "ip_props":
    
        {
    
        "1":{
    
        "ip":"1.1.1.1"
    
        ,"repeat":2
    
        },
    
        "2":{
    
        "ip":"2.2.2.2",
    
        "repeat": "4ever"
    
        }
    
        }
    
        }

Host命令的输出如下：

    
    
    $host {domain}
    
        {domain} has address 1.1.1.1
    
        $host {domain}
    
        {domain} has address 1.1.1.1
    
        $host {domain}
    
        {domain} has address 2.2.2.2
    
        $host {domain}
    
        {domain} has address 2.2.2.2
    
        $host {domain}
    
        {domain} has address 2.2.2.2
    
        $host {domain}
    
        {domain} has address 2.2.2.2
    
        $host {domain}
    
        {domain} has address 2.2.2.2

##  获取所有的日志文件-/api/fookup/logs/all

这个API可以帮助我们返回所有的日志文件：

    
    
    GET /api/fookup/logs/all

响应：

    
    
    [
    
           {
    
               "uuid": "0dd4d9083d7647e1a5fd5f1444e655ce",
    
               "resolved_to": "123.0.0.0",
    
               "domain": "0dd4d9083d7647e1a5fd5f1444e655ce.gel0.space",
    
               "origin_ip": "127.0.0.1",
    
               "port": "41095",
    
               "created_date": "2019-09-17 20:38:44.769560"
    
           },
    
        ...snip...
    
           {
    
               "uuid": "ffffffffffffffffffffffffffffffff",
    
               "resolved_to": "99.123.64.19",
    
               "domain": "0dd4d9083d7647e1a5fd5f1444e655ce.gel0.space",
    
               "origin_ip": "127.0.0.1",
    
               "port": "51515",
    
               "created_date": "2019-09-17 20:38:50.321975"
    
           }
    
        ]

##  统计数据-/api/statistics

这个API可以帮助我们获取到前端App的统计数据：

    
    
    GET /api/statistics

响应：

    
    
    {
    
           "request_count": 420,
    
           "created_bins": 69
    
        }

##  项目地址

> DnsFookup：【[GitHub传送门](https://github.com/makuga01/dnsFookup)】

 ***
参考来源：[makuga01](https://github.com/makuga01/dnsFookup)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

