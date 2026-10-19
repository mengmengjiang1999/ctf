在写[《一个通过ZoomEye获取IOC的案例》](http://mp.weixin.qq.com/s?__biz=MzU0MTkxMzkwNw==&mid=2247484262&idx=1&sn=216e7b256f7ff906a94e0b4fe28910d3&chksm=fb23e53acc546c2c6fcf4a67e1fe498683b230277694cf9850494916c8fab41dff8ae0d9e06d&scene=21#wechat_redirect)我发现搜索Docker的关键词：`Server:
Docker`会匹配到大量的蜜罐，而这些蜜罐[符合Anglerfish类蜜罐的特征](https://github.com/knownsec/KCon/blob/master/2019/25%E6%97%A5/%E5%A6%82%E4%BD%95%E5%8E%BB%E6%8C%96%E6%8E%98%E7%89%A9%E8%81%94%E7%BD%91%E7%8E%AF%E5%A2%83%E4%B8%AD%E7%9A%84%E9%AB%98%E7%BA%A7%E6%81%B6%E6%84%8F%E8%BD%AF%E4%BB%B6%E5%A8%81%E8%83%81-%E5%8F%B6%E6%A0%B9%E6%B7%B1.pdf)，目前这里蜜罐非常常见部署也非常多，显然它并不是今天的主角，我们先通过排除掉这些Anglerfish类的数据，搜索语法：

    
    
    "Server: Docker" -"<title>"

[解释下：因为我们要搜索的Docker是个API服务基本上是不可能出现"<title>"这个词的，所以直接排除] 如下：

![](https://image.3001.net/images/20210312/1615515012_604acd842a7a55085aeb4.png!small)

一共得到3.6w+的结果，随机做一些访问确认发现一个比较有意思显现，Docker
api默认端口为2375，但是在侧栏的端口分布栏来看可以看出很多其他端口，我们使用排除语法搜索：

    
    
    "Server: Docker" -"<title>" -port:2375

![](https://image.3001.net/images/20210312/1615515026_604acd92133b88dd926f6.png!small)

尝试访问基本都访问不到，端口服务处于关闭状态，这是一个非常异常的情况。然后我们看看banner信息，从ZoomEye里显示的banner信息很多请求应该是直接获取dorker版本信息的请求记录，注意观察你会发现这些请求都是版本信息Server:
Docker/18.06.1-ce (linux)及`Content-Length: 626`都非常统一，继续搜索：

    
    
    "Server: Docker" +"Content-Length: 626"

可以得到1.2w+的结果，而且这些很多基本访问不到，或者开始能访问，访问几次后就没有响应了，非常奇怪现象。随即我选了几个IP查看IP档案页面看看其他端口情况：  
![](https://image.3001.net/images/20210312/1615515058_604acdb24afc90e35a7c4.png!small)

从这个Server:头的很典型的“蜜罐”风格，初步推测这些是设备为“蜜罐”并且带有IP阻断功能。当然可能有人会问你这个`Content-Length:
626`很可能默认的配置就是这个长度，那么我们那在banner里选一个其他的关键词进行，完整的banner如下：

> `HTTP/1.1 200 OK``Date: Thu, 11 Mar 2021 07:04:33 GMT``Server:
> Docker/18.06.1-ce (linux)``Api-Version: 1.38``Docker-Experimental:
> false``Ostype: linux``Content-Type: application/json``Content-Length:
> 626````{"Platform": {"Name": ""}, "Components": [{"Name": "Engine",
> "Version": "18.06.1-ce", "Details": {"ApiVersion": "1.38", "Arch": "amd64",
> "BuildTime": "2018-10-26T23:39:57.000000000+00:00", "Experimental": "false",
> "GitCommit": "e68fc7a/18.06.1-ce", "GoVersion": "go1.10.3", "KernelVersion":
> "4.14.47-64.38.amzn2.x86_64", "MinAPIVersion": "1.12", "Os": "linux"}}],
> "Version": "18.06.1-ce", "ApiVersion": "1.38", "MinAPIVersion": "1.12",
> "GitCommit": "e68fc7a/18.06.1-ce", "GoVersion": "go1.10.3", "Os": "linux",
> "Arch": "amd64", "KernelVersion": "4.14.47-64.38.amzn2.x86_64", "BuildTime":
> "2018-10-26T23:39:57.000000000+00:00"}`

我们选GitCommit这个值`e68fc7a/18.06.1-ce`搜索语法：`Server:
Docker`+`e68fc7a/18.06.1-ce`得到1.4w+的结果，继续我们看看还有没有其他Content-Length的目标
搜索语法：`Server: Docker`+`e68fc7a/18.06.1-ce`-`Content-Length: 626`找到2,465
条而且都是2019年的数据，具体banner如下：

> `HTTP/1.1 200 OK``Content-Length: 583``Server: Docker/18.06.1-ce
> (linux)``Ostype: linux``Api-Version: 1.38``Docker-Experimental: false``Date:
> Sat, 20 Apr 2019 23:57:57 GMT``Content-Type:
> application/json````{"Platform":{"Name":""},"Components":[{"Name":"Engine","Version":"18.06.1-ce","Details":{"ApiVersion":"1.38","Arch":"amd64","BuildTime":"2018-10-26T23:39:57.000000000+00:00","Experimental":"false","GitCommit":"e68fc7a/18.06.1-ce","GoVersion":"go1.10.3","KernelVersion":"4.14.47-64.38.amzn2.x86_64","MinAPIVersion":"1.12","Os":"linux"}}],"Version":"18.06.1-ce","ApiVersion":"1.38","MinAPIVersion":"1.12","GitCommit":"e68fc7a/18.06.1-ce","GoVersion":"go1.10.3","Os":"linux","Arch":"amd64","KernelVersion":"4.14.47-64.38.amzn2.x86_64","BuildTime":"2018-10-26T23:39:57.000000000+00:00"}`

从http头及下面返回的内容参数除里http头里的Date内容好像没啥不一样，但是这个Content-Length是不一样的，一个是626
一个是583，然后仔细核对你会发现，在http body里的json里626的是多了很多空格，如：

    
    
    {"Platform": {"Name": ""}{"Platform":{"Name":""}

这个空格的问题让我想起《利用 ZoomEye 追踪多种 Redteam C&C 后渗透攻击框架》
https://paper.seebug.org/1301/ 这篇文章里提到的，到这里基本上可以实锤，搜索语法搜索出来的`Server:
Docker`+`Content-Length:
626`就是“蜜罐”，而且从选用的模版信息可以确定，这个蜜罐模版选用18.06.1-ce版本最为模版，而这个版本主要出现在2019年！

最后一个问题一直困扰着我：既然是“蜜罐”不应该是吸引火力吗？为什么直接拦jie访问IP呢？

 **编者注** ：ZoomEye一直提供蜜罐识别业务，打标结果目前只对VIP用户开放。目前ZoomEye已经支持这类蜜罐识别并打标！

