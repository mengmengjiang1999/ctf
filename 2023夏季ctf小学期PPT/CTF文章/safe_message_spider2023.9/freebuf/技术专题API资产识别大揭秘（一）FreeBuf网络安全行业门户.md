在API安全威胁不断加剧、多样化，数字化系统面临着巨大的安全挑战背景下，企业必须积极构建API安全能力。而企业API安全防护的首要任务是API资产进行清晰了解和有效管理。
**本期，我们将揭示API资产识别的关键技术，以帮助企业高效清晰地完成API资产梳理工作** 。

 **一、API资产识别技术概述**

API资产识别背景

 **1、API资产梳理究竟有什么意义？**

API资产梳理的重要性其实要先于API安全能力的建设，安全有效性依赖于能否准确识别被保护资产并进行纳管。对企业来说，各个业务内部、跨业务、对外开放、三方集成的场景下，到底有哪些API接口，这些接口的暴露情况、使用情况、风险情况，以及责任归属需要梳理清楚，从而能够有针对性地接入安全能力，保障API资产的安全。

 **2、API资产如何界定？**

要想准确全面识别API资产，首先要明确定义API资产的范围。

一条API资产基础信息通常包括以下内容，如下图的第二层所示：

![1692171663_64dc7d8fbd771cc00cac6.png!small](https://image.3001.net/images/20230816/1692171663_64dc7d8fbd771cc00cac6.png!small)

其中API唯一资产标识将由API资产基础信息中的操作方法、端点路径、参数计算而来。

根据上图可见，API资产的信息除了基础信息外，还必须包含API资产关联信息，如：部署IP、API访问源、通信次数等统计信息；API通信拓扑，功能标签、业务域划分信息；API安全风险监测信息；API数据安全监测信息等。

 **3、现有API识别手段或者方式的误区是什么？**

目前，用于安全工具梳理资产的技术实现主要包括自动化主机和端口扫描以及爬虫技术。由于API接口并没有统一的用户界面，而是研发团队内部商定的格式规范，因此大多数主机扫描、端口扫描和爬虫技术无法主动推测API的访问路径和参数格式，从而无法发现API资产。

这就导致当前大多数自动识别工具的结果将URL错误地识别为API。

实际上URL是统一资源定位符，是对可以从互联网上得到资源的位置和访问方法的一种简单表示。用于访问特定的网页、图像或文件。它和API从定义和作用上就有本质的区别。

举个栗子：

![1692171680_64dc7da05a1bff3c669db.png!small](https://image.3001.net/images/20230816/1692171680_64dc7da05a1bff3c669db.png!small)

在此URL中，https是协议，www.example.com是域，/news/article123是指向网站上特定文章的路径。

![1692171691_64dc7dabd9a869fd1c4f1.png!small](https://image.3001.net/images/20230816/1692171691_64dc7dabd9a869fd1c4f1.png!small)

此外URL还包括一些静态资源。

来看API的示例：

![1692171703_64dc7db7aa9dd8fbd4fd6.png!small](https://image.3001.net/images/20230816/1692171703_64dc7db7aa9dd8fbd4fd6.png!small)

对天气查询的API而言：https://api.weatherdata.com是天气数据 API 的基本
URL，/current?location=city123指定需要“city123”参数当前天气数据的端点。并且API 可能会以结构化格式（例如
JSON）响应数据，其中包含温度、湿度和其他天气相关信息。所以，API的组成要素中包含了URL。

 **4、各类识别手段对比，企业该如何选择？**

![1692171717_64dc7dc5e15be475b0072.png!small](https://image.3001.net/images/20230816/1692171717_64dc7dc5e15be475b0072.png!small)

通过比较API资产发现效果、实现成本和业务入侵性等方面，可以得出通过流量还原API资产成为了API资产识别最佳解决方案。除此之外，流量还原API资产的优势还在于：

  * API识别是持续进行的过程，一旦发现新API，应立即规范补充信息。通过流量还原，我们可以从各个维度监测API资产，并持续对其进行监测。

  * 在进行安全测试期间，测试人员可以利用流量恢复API资产来更全面地了解API的工作方式，以及对不同类型的数据和请求的处理。这个过程有助于发现API资产中隐藏的安全漏洞和风险。

经过上述问题的解答，相信大家对API资产梳理也有所了解。接下来，我们将介绍API资产识别的关键技术，以便帮助大家理解如何从流量中准确识别API资产。首先我们要了解：API有哪些分类，它们究竟长什么样子？

 **二、API协议与风格**

按照不同协议和风格形式，API可以分为：RESTful API、GraphQL API、SOAP API、gRPC API、类XML—RPC
API及其他技术类型API。

不同风格的API

  *  **RESTful API**

REST API也称为 RESTful API，是遵循 REST 架构规范的应用编程接口（API 或 Web API），支持与 RESTful Web
服务进行交互。REST 是一组架构规范，并非协议或标准。API 开发人员可以采用各种方式实施 REST。当客户端通过 RESTful API
提出请求时，它会将资源状态表述传递给请求者或终端。该信息或表述通过 HTTP 以下列某种格式传输：JSON（Javascript
对象表示法）、HTML、XLT、Python、PHP 或纯文本。RESTful API也是目前主流的API风格。

简易的例子：

    
    
    HTTP requestGET /api/user?id=1HTTP response{"id": 1,"name": "user1"}

 **使用场景：** 资源集中型服务、访问量大，且对访问时效要求比较高的服务、面向公网的，且安全性要求较低的开放型 API 服务等。

  *  **GraphQL API**

GraphQL是一种面向数据的 API 查询风格。传统的 API 拿到的是前后端约定好的数据格式，GraphQL 对 API
中的数据提供了一套易于理解的完整描述，客户端能够准确地获得它需要的数据，没有任何冗余，也让 API 更容易地随着时间推移而演进。

GraphQL最常见的是通过 HTTP 来发送请求，那么如何通过 HTTP 来进行 GraphQL 通信呢？

举个栗子，如何通过Get/Post方式来执行下面的GraphQL查询呢？

    
    
    query {me {name}}

获取简单的请求内容放在 URL 中，在content-type: application/json情况下发布，将 JSON 格式的内容放在请求体里：

    
    
    Get 方式http:/www.example.com/myapi/graphql?query={me{name}}# Post 方式的请求体{"query": "...","operationName": "...","variables": { "myVariable": "someValue", ... }}

返回的格式一般也是JSON体。

    
    
    正确返回{"data": { ... }}# 执行时发生错误{"errors": [ ... ]}

 **使用场景：** 比较复杂的数据查询和获取、需要从多个平台进行数据查询并集成、前后端分离模式下，需灵活开发，减少沟通成本、实时查询推送等。

  *  **SOAP API**

SOAP代表简单对象访问协议，本身属于API协议的一种。SOAP API是使用SOAP协议作为API接口交互方式的API应用，它允许 Web 服务通过
HTTP 通信和交换结构化信息。由于它使用 XML 来编写消息，因此该协议与平台和语言无关，并在所有操作中使用。

示例：请求内容：

    
    
    <?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><IsValidISBN10 xmlns="http://webservices.daehosting.com/ISBN"><sISBN>0-19-852663-6</sISBN></IsValidISBN10></soap:Body></soap:Envelope>

响应内容：

    
    
    <?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><m:IsValidISBN10Response xmlns:m="http://webservices.daehosting.com/ISBN"><m:IsValidISBN10Result>true</m:IsValidISBN10Result></m:IsValidISBN10Response></soap:Body></soap:Envelope>

 **使用场景：** B2B 交易、客户/服务器通讯、基于 Web 的电子商务应用、企业应用集成等。

  *  **gRPC API：** gRPC 是 Google Remote Procedure Call 的简写，是基于 RCP 架构的变体。该技术遵循一个使用 HTTP 2.0 协议的 RPC API 实现。此类API通过Protobuf协议来定义接口和条件约束，完成客户端和服务端的远程调用。

 **使用场景：** 大数据处理、微服务架构等。

  *  **类XML—RPC API及其他技术类型API：** 此类API包含多种技术，因此使用的普及率比较低，所以归为一类，通常包含XML-RPC的API、JMS（Java Message Service）接口、WebSocket API以及IOT通信协议的接口等。

  *  **特殊API**

特殊型API主要包括一些特殊协议框架下的API，例如Dubbo型API：Dubbo定位为一个RPC框架，专注于服务之间的调用。除了服务调用，随着微服务越来越火爆，Dubbo开始逐渐向服务治理、服务监控、服务网关等方向扩展，慢慢的演变为一个成熟的微服务框架。而在Dubbo框架下的API定义为Dubbo型API。请求报文：

    
    
    com.example.service.user/userinfo  dubbo2"timeout": 3000"group": "groupA""version": "1.0.0"Service: com.example.service.userMethod: userinfoArguments:- String: "admin"- Integer: 12345响应报文：dubbo2 200 OK Return Value:- Boolean: true

 **三、识别流量中的API**

流量处理

![1692171785_64dc7e0957d24dfd89b7b.png!small](https://image.3001.net/images/20230816/1692171785_64dc7e0957d24dfd89b7b.png!small)

  * 流量过滤：在拿到初始流量后，我们需要对此时的流量进行一些过滤，排除非接口类流量，比如静态资源或者视频流

  * 流量解析：流量解析主要包括协议解析和结构解析。在获取过滤后的流量后，将根据协议类型如HTTP、Dubbo、GRPC等协议类型进行完整包解析，对于复杂的参数结构，如JSON、XML和各种复杂编码，则使用各种解析引擎进行解析。

  * 片段存储：在解析之后，会对各类协议的特征字段以及参数接口进行片段式存储。

对于各类参数结构究竟是如何实现解析以及片段式存储又具体表现怎样呢？

我们以JSON格式的参数结构为例：

![1692171797_64dc7e157c8ab8689b7f0.png!small](https://image.3001.net/images/20230816/1692171797_64dc7e157c8ab8689b7f0.png!small)

如上图所示，简单来讲就是在获取到例一个json格式的API参数结构后，通过对参数进行分组，会将API参数解析为一个树状结构。root作为API的根节点，下面分支为各级参数的支节点和叶子节点，无论其嵌套的层次有多深，解析算法会将其中的所有键值对都解析为一个树结构。

不同风格API识别

在通过前面的流量处理的步骤之后，接下来就是对不同风格类型的API进行识别

####  **1、Restful API识别**

识别难点：要知道，RESTful API识别难点在于它是一种API风格，而不是一种约束或规则，过于理想的 RESTful API
可能在实际情况中会付出太多的成本，这样会导致很多企业并不会完全按照其规范进行，所以RESTful
API在流量中可能并不会存在很明显提取特征来计算出它的API唯一标识符。

所以，我们需要通过多种判断条件和方法对RESTful API进行识别：

  * HTTP 方法：HTTP 设计了很多动词，来标识不同的操作，不同的 HTTP 请求方法有各自的含义，就像上面所展示的，RESTful API 支持4种 HTTP 方法（如 GET、POST、PUT 和 DELETE）来描述操作。
  * 版本控制：版本控制的原则是在不影响现有客户的情况下，更新RESTful API的方法，一般最常见的版本控制方式是通过改变URL来表示不同的版本，例如：

    
    
    http://www.example.com/api/v1/xxxhttp://www.example.com/api/v2/xxx

除此之外，还可以通过请求标头Accept或者请求参数来进行RESTful API的版本控制。

  3. 统一返回数据格式：常用的返回数据格式有 JSON 和 XML。请求和响应的数据格式统一。

通过上述RESTful API规范组合为识别的判断条件，结合对请求-响应报文的分析，比如：RESTful
API的响应数据过多，返回的资源量可能会随着时间的推移而增加；统计URL端点前几位是否存在相同字段的分析方式来更加精准地识别RESTful API。

####  **2、GraphQL API识别**

相比于RESTful API，GraphQL
API的识别就比较容易。GraphQL作为一种用于API的查询语言，基于类型和字段的方式进行相关操作，这是一种类似于JSON的格式，可以看到下图左边部分。

![1692171819_64dc7e2b1fbc3bf119fb8.png!small](https://image.3001.net/images/20230816/1692171819_64dc7e2b1fbc3bf119fb8.png!small)

正因如此，GraphQL API相比于RESTful API，GraphQL
只用一个数据源就可以查询所有数据，所有的请求都可以访问一个服务端点；并且GraphQL 返回的结果响应准确地根据客户端的请求字段，也就是说，GraphQL
API存在一个类似于JSON的特殊格式，且请求中的参数和返回结果一一对应。

除此之外，GraphQL 的操作类型可以是 query、mutation 或 subscription，它们分别代表了查询、变更和订阅，在使用GraphQL
API发送的请求中也必定包括这些操作类型的特征字段。

比如，进行查询操作时，请求中必定带有”query“字段。

    
    
    query {user { id }}

在GraphQL
API的请求中通常会采用JSON的格式，而其特定类似JSON的数据格式会嵌套在对应的参数当中，例如下面的”query“参数的值就嵌套了整个查询的数据结构。

    
    
    {"query": "...","operationName": "...","variables": { "myVariable": "someValue", ... }}

通过上述的了解，其实我们已经找到了GraphQL API识别的方法，总结一下：

  * 解析JSON格式后，判断参数值是否为GraphQL特殊的数据结构

  * 提取响应参数是否和数据结构中一一对应

  * 识别匹配在请求中是否存在代表GraphQL API操作的特殊字段，例如"query"、"mutation" 或"subscription"

####  **3、SOAP API识别**

相比于前两种风格的API，SOAP API的识别应该最容易的，因为SOAP API使用 XML 作为API 客户端发送和接收的消息的数据格式。

![1692171841_64dc7e4119ca361f78188.png!small](https://image.3001.net/images/20230816/1692171841_64dc7e4119ca361f78188.png!small)

在SOAP API的消息中存在了四个不同的元素：

  *  **Envelope:** 是将文档标识为 SOAP 消息而不是任何其他类型的 XML 文档的基本元素。消息以信封的标签开始和结束。（必须元素）

  *  **Header:** 是一个可选元素，可以使用 SOAP 模块添加新特性和功能。一个Envelope中可以包含多个标题。（可选元素）

  *  **body:** 正文包含实际消息：请求或响应。（必须元素）

  *  **Fault:** 如果在处理过程中出现问题，则用于错误消息和状态信息。（可选元素）

并且在请求正文中必须包含Envelope、Body元素以及相关内容。

所以SOAP API的识别只需要识别请求-响应是否为XML的数据格式，并且在对请求中的XML数据格式进行解析后，匹配是否存在Envelope、Body及其内容的特殊字段。

 **专题预告**

下期我们将继续揭秘API资产聚合逻辑技术、以及特殊类型API例如Dubbo API该如何进行识别。

