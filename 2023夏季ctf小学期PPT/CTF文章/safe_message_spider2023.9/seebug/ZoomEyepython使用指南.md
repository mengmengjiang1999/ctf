### 0x01 前言

`ZoomEye` 作为一款网络空间搜索引擎，通过浏览器可以快速搜索网络设备。对于技术人员来说这并不是很友好，技术人员期待一款能够便捷有效的查询
`ZoomEye` 的信息、数据以及格式化结果等操作并且还能作为 SDK 集成到其他的工具中，于是便有了 `ZoomEye-python` 这样一个工具。

`ZoomEye-python` 是一款基于 `ZoomEye API` 开发的 Python 库，提供了 `ZoomEye` 命令行模式，同时也可以作为
`SDK` 集成到其他工具中。该库可以让技术人员更便捷地 **搜索** 、 **筛选** 、 **导出** `ZoomEye` 的数据。

### 0x02 ZoomEye API

`ZoomEye` 官方提供了[搜索数据](https://www.zoomeye.org/doc#search-filters)，[用户登陆](https://www.zoomeye.org/doc#login)，[剩余资源](https://www.zoomeye.org/doc#resources-info)以及[设备历史](https://www.zoomeye.org/doc#history-data)接口，目前 ZoomEye API
对外开放开发者(developer) 权限，有一定的额度限制。每个月的额度为 10000
条，对外开放的开发者套餐每个月会重置相应资源的请求额度。注册用户即可获得 API 的开发者套餐使用权限。

### 0x03 安装步骤

可直接从 `pypi` 进行安装：

    
    
    pip3 install zoomeye

也可以通过 `github` 进行安装：

    
    
    pip3 install git+https://github.com/knownsec/zoomeye-python.git

### 0x04 如何使用

`ZoomEye-python` 提供了 cli 和 SDK 两种工作模式。

#### 1.使用cli

在完成安装后，可以使用 `zoomeye -h` 命令验证是否安装成功。

    
    
    $ zoomeye -h
    usage: zoomeye [-h] {info,search,init} ...
    
    positional arguments:
      {info,search,init}
        info              Show ZoomEye account info
        search            Search the ZoomEye database
        init              Initialize the token for ZoomEye-python
    
    optional arguments:
      -h, --help          show this help message and exit

##### 1.初始化

`ZoomEye-python` 的初始化非常简单，使用下列方式中的一种就可以：

**APIKEY (推荐)**

    
    
    $ zoomeye init -apikey "01234567-acbd-00000-1111-22222222222"
    successfully initialized
    Role: developer
    Quota: 10000

or

**username/password**

    
    
    $ zoomeye init -username "username@zoomeye.org" -password "password"
    successfully initialized
    Role: developer
    Quota: 10000

这两种方式本质上没有区别，通过 `username/password` 的方式初始化 cli ，这种方式认证后会返回 `JWT-token`，具有一定的时效性 (大概 12 个小时)，`JWT-toekn`失效后需要用户重新登陆。而`APIKEY`
不会过期，用户可根据需求在个人信息中进行重置。因此我们推荐 **使用 APIKEY 的方式** 进行初始化。

> 登陆 `ZoomEye` 在个人信息中(<https://www.zoomeye.org/profile>) 获取 `APIKEY` 。

##### 2.账户资源

`ZoomEye API` 规定每个账户注册即可获得 10000 条数据的额度，在使用搜索之前记得查看账户所剩下的配额。

使用命令 `zoomeye info` 即可查询账户的剩余配额。

    
    
    $ zoomeye info
    Role: developer
    Quota: 10000

> 需要注意：info 命令只显示了免费部分的配额，将在下个版本修复。

##### 3.搜索

    
    
    $ zoomeye search -h
    usage: zoomeye search [-h] [-num value] [-facet [field]]
                          [-filter [field=regexp]] [-stat [field]]
                          [-save [field=regexp]] [-count]
                          dork
    
    positional arguments:
      dork                  The ZoomEye search keyword or ZoomEye exported file
    
    optional arguments:
      -h, --help            show this help message and exit
      -num value            The number of search results that should be returned
      -facet [field]        Perform statistics on ZoomEye database, field:
                            [app,device,service,os,port,country,city]
      -filter [field=regexp]
                            Output more clearer search results by set filter
                            field, field:
                            [app,version,device,port,city,country,asn,banner,*]
      -stat [field]         Perform statistics on search results, field:
                            [app,device,service,os,port,country,city]
      -save [field=regexp]  Save the search results with ZoomEye json format, if
                            you specify the field, it will be saved with JSON
                            Lines
      -count                The total number of results in ZoomEye database for a
                            search

`search` 命令提供了对数据进行 **筛选** 、 **搜索** 、 **导出** 、 **聚合统计** 的能力，下面以 `飞致云堡垒机` 为例展示
`ZoomEye-python` 的功能：

**搜索数据**

    
    
    $ zoomeye search "app:"飞致云堡垒机""
    ip:port                service          country          app                 banner
    46.*.*.254:80         http              Russian Federation  Tornado httpd    HTTP/1.1 302 FOUND\r\nContent-...
    139.*.*.11:6080       http              China               nginx            HTTP/1.1 200 OK\x0d\nServer: n...
    180.*.*.202:8880      http              China               nginx            HTTP/1.1 200 OK\r\nServer: ngi...
    180.*.*.181:80        nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nEtag: W/"600...
    180.*.*.104:80        nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nContent-Type...
    180.*.*.195:80        http              China                                HTTP/1.1  200 OK\nContent-Leng...
    180.*.*.118:80        nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nCache-Contro...
    180.*.*.120:80        nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nDate: Mon, 1...
    180.*.*.212:80        http              China                                HTTP/1.1  200 OK\nDate: Mon, 1...
    180.*.*.119:80        nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nAccept-Range...
    101.*.*.237:8888      http              China               nginx            HTTP/1.1 200 OK\r\nServer: ngi...
    175.*.*.71:443        https             China               nginx            HTTP/1.1 200 OK\r\nServer: ngi...
    182.*.*.7:80          nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nStrict-Trans...
    182.*.*.114:80        nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nDate: Mon, 1...
    182.*.*.45:80         nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nAccept-Range...
    182.*.*.79:80         nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nDate: Mon, 1...
    52.*.*.175:80         http              China               nginx            HTTP/1.1 302 Found\r\nServer: ...
    182.*.*.131:80        http              China                                HTTP/1.1  200 OK\nExpires: Tue...
    182.*.*.183:80        nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nLast-Modifie...
    182.*.*.41:80         http              China                                HTTP/1.1  200 OK\nAccept-Range...
    
    total: 20

搜索功能是 `ZoomEye-python` 最重要的功能，其优点是在于不仅能获取到数据而且能对数据进行筛选，统计，导入导出。

Tips： **可以通过`-num` 指定展示的数量。**

这里为什么不是获取的数量？

> 因为 `ZoomEye API` 单次查询的最小数量为 20 条， 所以 `-num` 参数消耗的配额为 20 的整数倍。

下次获取数据时是否重复消耗配额？

> 并不会，在对数据进行搜索时，ZoomEye-python 对 API 返回的数据进行了缓存，下次获取将从缓存中获取，超过缓存的数量再从 API
> 获取，缓存的时间为 5 天，这样做的目的在一定程度上节约用户的配额，也保证了数据的准确性。

**查看总量**

    
    
    $ zoomeye search "app:"飞致云堡垒机"" -count
    7748

**在线数据聚合**

    
    
    $ zoomeye search "app:"飞致云堡垒机"" -facet "country"
    country                            count
    China                              6921
    United States                      252
    Singapore                          152
    Japan                              129
    Russian Federation                 114
    Asia Pacific Regions               26
    Republic of Korea                  26
    South Africa                       24
    India                              15
    Philippines                        10

以上是获取 `ZoomEye API` 对全部数据统计的结果，可以直观的看出`飞致云堡垒机`在中国的使用是最多的，设备总量。在分析能提供不小的帮助。

**本地数据聚合**

    
    
    zoomeye search "app:"飞致云堡垒机"" -stat "country,city"
    country                            count
    China                              19
    Russian Federation                 1
    city                               count
    Beijing                            9
    Shanghai                           6
    Kamyshin                           1
    New Taipei City                    1
    Hangzhou                           1
    Chengdu                            1
    Zhongwei                           1

本地数据聚合能够对当前获取的数据进行统计。

**筛选数据**

面对众多的数据，往往看起来比较麻烦，为了方便我们在查看数据时更加方便，`ZoomEye-python` 提供了一个贴心的功能 —— 筛选。`ZoomEye-python` 在筛选可以指定字段 ( `key` ) 也可以指定字段和值 ( `key=value` )。`value` 支持正则表达式，如：

    
    
    $ zoomeye search "app:"飞致云堡垒机"" -filter "city=Beijing,port=8*"
    ip                         city                          port
    180.*.*.181                Beijing                       80
    180.*.*.104                Beijing                       80
    182.*.*.7                  Beijing                       80
    182.*.*.114                Beijing                       80
    182.*.*.45                 Beijing                       80
    182.*.*.79                 Beijing                       80
    182.*.*.131                Beijing                       80
    182.*.*.183                Beijing                       80
    182.*.*.41                 Beijing                       80
    
    total: 9

**保存数据**

根据不同的需求我们需要导出格式不尽相同的数据，在 `ZoomEye-python` 提供了两种保存方式：一种是行 json ，另外一种是`ZoomEye
API`返回的元数据，同时支持筛选。

保存行 json 时，可以指定自己想要的字段，语法与上面的 `filter` 一致，同样支持正则表达式。

    
    
    # 保存筛选数据
    $ zoomeye search "app:"飞致云堡垒机"" -save "city=Beijing,port"
    save file to /app:飞致云堡垒机_9_1610962280.json successful!
    
    $ cat app:飞致云堡垒机_9_1610962280.json
    {'ip': '180.*.*.181', 'city': 'Beijing', 'port': 80}
    {'ip': '180.*.*.104', 'city': 'Beijing', 'port': 80}
    {'ip': '182.*.*.7', 'city': 'Beijing', 'port': 80}
    {'ip': '182.*.*.114', 'city': 'Beijing', 'port': 80}
    {'ip': '182.*.*.45', 'city': 'Beijing', 'port': 80}
    {'ip': '182.*.*.79', 'city': 'Beijing', 'port': 80}
    {'ip': '182.*.*.131', 'city': 'Beijing', 'port': 80}
    {'ip': '182.*.*.183', 'city': 'Beijing', 'port': 80}
    {'ip': '182.*.*.41', 'city': 'Beijing', 'port': 80}

在没有指定字段时，将保存从 `ZoomEye API` 获取的元数据。

    
    
    # 保存元数据
    $ zoomeye search "app:"飞致云堡垒机"" -save
    save file to /app:飞致云堡垒机_20_1610962433.json successful!
    
    $ cat app:飞致云堡垒机_20_1610962433.json
    {"total": 7748, "matches": [{"geoinfo": {"city": {"geoname_id": null, "names": {"zh-CN": "\u5361\u6885\u7533", "en": "Kamyshin"}}, "country": {"geoname_id": null, "code": "RU", "names": {"zh-CN": "\u4fc4\u7f57\u65af", "en": "Russian Federation"}}, "isp": "abrikosnet.ru", ......

**导入数据**

`ZoomEye-python` 能够对保存的 `ZoomEye API` 元数据进行载入并对其进行筛选、搜索等操作，如：

    
    
    $ zoomeye search app:飞致云堡垒机_20_1610962433.json
    ip:port                service          country          app                 banner
    46.*.*.254:80         http              Russian Federation  Tornado httpd    HTTP/1.1 302 FOUND\r\nContent-...
    139.*.*.11:6080       http              China               nginx            HTTP/1.1 200 OK\x0d\nServer: n...
    180.*.*.202:8880      http              China               nginx            HTTP/1.1 200 OK\r\nServer: ngi...
    180.*.*.181:80        nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nEtag: W/"600...
    180.*.*.104:80        nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nContent-Type...
    180.*.*.195:80        http              China                                HTTP/1.1  200 OK\nContent-Leng...
    180.*.*.118:80        nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nCache-Contro...
    180.*.*.120:80        nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nDate: Mon, 1...
    180.*.*.212:80        http              China                                HTTP/1.1  200 OK\nDate: Mon, 1...
    180.*.*.119:80        nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nAccept-Range...
    101.*.*.237:8888      http              China               nginx            HTTP/1.1 200 OK\r\nServer: ngi...
    175.*.*.71:443        https             China               nginx            HTTP/1.1 200 OK\r\nServer: ngi...
    182.*.*.7:80          nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nStrict-Trans...
    182.*.*.114:80        nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nDate: Mon, 1...
    182.*.*.45:80         nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nAccept-Range...
    182.*.*.79:80         nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nDate: Mon, 1...
    52.*.*.175:80         http              China               nginx            HTTP/1.1 302 Found\r\nServer: ...
    182.*.*.131:80        http              China                                HTTP/1.1  200 OK\nExpires: Tue...
    182.*.*.183:80        nagios-nsca       China               Nagios NSCA      HTTP/1.1  200 OK\nLast-Modifie...
    182.*.*.41:80         http              China                                HTTP/1.1  200 OK\nAccept-Range...
    
    total: 20

#### 2\. SDK

在 `ZoomEye-python` 中提供了一下接口：

    
    
    1.login()
      使用 username/password 进行认证
    2.dork_search(dork, page=0, resource="host", facets=None)
      根据 dork 搜索指定页的数据
    3.multi_page_search(dork, page=1, resource="host", facets=None)
      根据 dork 搜索多页数据
    4.resources_info()
      获取当前用户的信息
    5.show_count()
      获取当前 dork 下全部匹配结果的数量
    6.dork_filter(keys)
      从搜索结果中提取指定字段的数据
    7.get_facet()
      从搜索结果中获取全量数据的聚合结果
    8.history_ip(ip)
      查询某个 ip 的历史数据信息
    9.show_site_ip(data)
      遍历 web-search 结果集，并输出域名和ip地址
    10.show_ip_port(data)
      遍历 host-search 结果集，并输出ip地址和端口

##### 使用实例

**使用 username/password 初始化**

    
    
    $ python3
    >>> import zoomeye.sdk as zoomeye
    >>> dir(zoomeye)
    ['ZoomEye', 'ZoomEyeDict', '__builtins__', '__cached__', '__doc__',
    '__file__', '__loader__', '__name__', '__package__', '__spec__',
    'fields_tables_host', 'fields_tables_web', 'getpass', 'requests',
    'show_ip_port', 'show_site_ip', 'zoomeye_api_test']
    >>> # Use username and password to login
    >>> zm = zoomeye.ZoomEye()
    >>> zm.username = 'username@zoomeye.org'
    >>> zm.password = 'password'
    >>> print(zm.login())
    ....JIUzI1NiIsInR5cCI6IkpXVCJ9.....
    >>> data = zm.dork_search('apache country:cn')
    >>> zoomeye.show_site_ip(data)
    213.***.***.46.rev.vo***one.pt ['46.***.***.213']
    me*****on.o****e.net.pg ['203.***.***.114']
    soft********63221110.b***c.net ['126.***.***.110']
    soft********26216022.b***c.net ['126.***.***.22']
    soft********5084068.b***c.net ['126.***.***.68']
    soft********11180040.b***c.net ['126.***.***.40']
    ...

**使用 APIKEY 初始化**

    
    
    $ python3
    >>> import zoomeye.sdk as zoomeye
    >>> zm = zoomeye.ZoomEye()
    >>> zm.api_key = "01234567-acbd-00000-1111-22222222222"
    >>> zm.dork_search("apache country:cn")
    ...

**搜索**

如上所示，使用 `dork_search()` 函数进行搜索，`dork_search` 提供了 page，resource，facets
参数用来获取指定页数，Web/Host 设备以及对数据总量的聚合统计。其中 resource 默认为 host 设备，facets 为 None。

    
    
    data = zm.dork_search('telnet', facets='app')
    zm.get_facet()
    {'product': [{'name': '', 'count': 28323128}, {'name': 'BusyBox telnetd', 'count': 10180912}, {'name': 'Linux telnetd', ......

同时 SDK 还提供了获取多页数据的函数 `multi_page_search` ，`multi_page_search()` 与
`dork_search()` 的区别在于：`multi_page_search` 中的 page 为获取数据的页数，而 `dork_search` 中的
page 为第几页的数据。

**筛选**

为了更加容易的获取数据，`SDK` 提供了帮助用户筛选的数据的函数 `dork_filter` ，用于获取指定字段的数据，如：

    
    
    data = zm.dork_search("telnet")
    zm.dork_filter("ip,port")
    
    [['180.*.*.166', 5357], ['180.*.*.6', 5357], ......

根据 `ZoomEye API` 提供的接口，分别为 `/host/search` 和 `/web/search`
，这两个接口返回的数据有一定的区别。因此在进行筛选时请根据指定的搜索类型填入正确的字段。

`/web/search` 包含的字段有：app / headers / keywords / title / ip / site / city /
country `/host/search` 包含的字段有：app / version / device / ip / port / hostname /
city / country / asn / banner

### 0x05 Knownsec 404 Team星链计划

`ZoomEye-python` 是 `Knownsec 404 Team星链计划` 中的一员。

“404星链计划”是知道创宇404实验室于2020年8月开始的计划，旨在通过开源或者开放的方式， **长期维护**
并推进涉及安全研究各个领域不同环节的工具化，就像星链一样，将立足于不同安全领域、不同安全环节的研究人员链接起来。

其中不仅限于突破安全壁垒的大型工具，也会包括涉及到优化日常使用体验的各种小工具，除了404本身的工具开放以外，也会不断收集安全研究、渗透测试过程中的痛点，希望能通过“404星链计划”改善安全圈内工具庞杂、水平层次不齐、开源无人维护的多种问题，营造一个更好更开放的安全工具促进与交流的技术氛围。

<https://github.com/knownsec/404StarLink-Project>

### 0x06 项目地址

`ZoomEye-python` 完全开源，任何人可以在此基础上修改或提交代码。

GitHub：<https://github.com/knownsec/ZoomEye-python>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1461/>

