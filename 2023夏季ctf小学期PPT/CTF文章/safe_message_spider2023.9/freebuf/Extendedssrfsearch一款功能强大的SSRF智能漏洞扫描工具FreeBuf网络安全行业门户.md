![](https://image.3001.net/images/20200302/1583156223_5e5d0bff5d77f.png!small)

##  Extended ssrf search

 **Extended ssrf
search是一款功能强大的SSRF智能漏洞扫描工具，该工具可以通过在请求中设置不同的预定义参数来搜索SSRF漏洞，这些参数包括路径、主机、Header、POST和GET参数。**

##  工具下载

广大研究人员可以使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/Damian89/extended-ssrf-search.git

##  工具准备

将项目中的example.app-settings.conf文件重命名为app-settings.conf，然后调整相应设置。最重要的设置时回调URL地址，我建议大家使用Burp
Collaborator。接下来，将你的URL添加到config/url-to-test.txt中。在这里，脚本将接收域名和URL以及响应的查询参数。你还可以将你自己的Cookie添加到config/cookie-jar.txt中，或给请求添加额外的Header。针对POST以及GET请求的爆破列表当前体积不大，因为我们认为应该把重点放在那些最有可能存在漏洞的地方。

##  工具执行

该工具可以直接在不需要任何参数的情况下通过命令行接口来运行，运行命令如下：

    
    
    python3 extended-ssrf-search.py

##  工具配置

我们可以根据自己的需要来设置各种工具运行参数、设置以及选项。

##  文件

主配置文件为“app-settings.conf”，所有的工具配置都可以通过修改这个文件来实现。除此之外，该工具还有很多其他的文件可以帮助我们设置更加复杂的数据，例如Header、URL和Cookie。

###  config/cookie-jar.txt

使用此文件添加cookie字符串，我一般都直接拷贝Burp请求中的参数，你也可以拷贝"Cookie:"-header的值，默认文件中已提供了样本输入。

###  config/http-headers.txt

这个文件中定义了可以添加到请求和操作中的HTTP
Header，每个Header都添加了Payload，最重要的参数已经在项目文件中给出了，但你可以根据需要来自行添加。

###  config/parameters.txt

该工具提供了用于对GET和POST请求进行爆破的选项，其中涉及到的每一个参数都有对应的Payload作为值。

###  config/static-request-headers.txt

这些Header会被添加至每一个请求中，但无法被修改，因为它们都是静态值。这是添加授权或承载Cookie的最佳位置，其中每一行为一个（键：值）对。

###  config/urls-to-test.txt

可在该文件中添加需要扫描的链接，允许的参数格式如下：

> [https://domain.com](https://domain.com/)
>
> <https://domain.com/path>
>
> <https://domain.com/path?param=value>¶m1=value1

domain.com

当检测到最后一个样例格式时，会在前面加上一个“http://”。该工具只能配合格式正确的url列表来进行操作，因为建议使用Burp来导出这种格式的列表文件，并根据需要来添加Cookie。

##  设置

app-settings.conf文件定义的是程序的工作流，它是最重要的项目文件，你可以在该文件中激活/禁用不同的功能模块。

###  CallbackHost

定义发送所有DNS和HTTP请求的URL/主机，我一般使用的是Burp Collaborator，但DNSBin也是可以的。

###  HTTPMethod

定义请求方法，可选参数有GET、POST、PUT、DELETE、PATCH、GET、OPTIONS，无效值将引起工具运行错误。

###  HTTPTimeout

有些请求可能需要很长时间，在这里你可以定义一个请求的最长执行时间，我建议这个值设置在2到6秒之间。

###  MaxThreads

线程越多，脚本就越快。但是由于我们处理的是大量的连接，所以我通常在我的个人计算机上设置小于10的值，在我的VPS上设置值大约为30。

###  ShuffleTests

尤其是在处理一个较大的URL列表时，如果将此设置为“true”，则会打乱所有创建的测试。这样一来，同一个主机就不会受到那么多的攻击。如果你只扫描一台主机，那就随意了。

###  GetChunkSize

在处理一个较大的参数列表时，这个参数也许可以帮到你，并防止出现较严重的实体错误。

###  InPath

下面的样例中显示了一个GET请求，但根据我们的设置，它也可以是POST、PUT和DELETE等等：

    
    
    GET [INJECT HERE PAYLOAD] HTTP/1.1
    
        ...

###  InHost

下面的样例中显示了一个GET请求，但根据我们的设置，它也可以是POST、PUT和DELETE等等：

    
    
    GET /path HTTP/1.1
    
        Host: [INJECT HERE PAYLOAD]
    
        ...

###  InAdditionalHeaders

下面的样例中显示了一个GET请求，但根据我们的设置，它也可以是POST、PUT和DELETE等等：

    
    
    GET /path HTTP/1.1
    
        ...
    
        X-Forwarded-For: [INJECT HERE PAYLOAD]

###  InParamsGet

下面是一个针对GET请求的固定方法：

    
    
    GET /path?[INJECT HERE PAYLOAD] HTTP/1.1
    
        ...

###  InParamsPost

下面是一个针对POST请求的固定方法：

    
    
    POST /path HTTP/1.1
    
        ...
    
        Content-Type: application/x-www-form-urlencoded
    
        Content-Length: XXX
    
        [INJECT HERE PAYLOAD]

###  InParamsPostAsJson

下面是一个针对POST请求的固定方法：

    
    
    POST /path HTTP/1.1
    
        ...
    
        Content-Type: application/json
    
        Content-Length: XXX
    
        [INJECT HERE JSON-PAYLOAD]

##  攻击

该工具的默认配置下，可以直接尝试通过SSRF来触发HTTP请求。与此同时，也可以使用DNS以及OS命令注入等方式来实现数据提取。

在这里，我们可以设置代理服务器，格式为“ip : port”。结果如下，我们可以在Burp中查看到捕捉到的HTTP历史记录：

![](https://image.3001.net/images/20200302/1583156434_5e5d0cd225558.png!small)

##  攻击运行截图

![](https://image.3001.net/images/20200302/1583156442_5e5d0cda95ee4.png!small)

##  项目地址

> Extended ssrf search：【[GitHub传送门](https://github.com/Damian89/extended-ssrf-> search)】

 *** 参考来源：[Damian89](https://github.com/Damian89/extended-ssrf-search)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

