**![](https://image.3001.net/images/20200223/1582461133_5e5270cd1f986.png!small)**

**在2019年6月买了一台特斯拉Model
3之后，我就开始研究它的工作机制，并把重点放在了其信息系统上。为了更好地深入发现更多安全问题，我于2019年8月在特斯拉漏洞众测平台注册成为了一名硬件安全研究者，着手开干。截至目前，前后我发现了好几个有效的安全漏洞，今天和大家分享两个有意思的Web漏洞。**

##  **从特斯拉零部件目录网站入手**

虽然我主要关注于特斯拉的硬件问题，但偶尔也会研究一下特斯拉系统中的某些Web属性。随着特斯拉Model Y车型的发布在即，所以我就想看看特斯拉在Model
Y车型上会不会出现数据泄露风险，我是否能从特斯拉信息系统中发现一些尚未公开的Model Y车型数据。

有了这个想法之后，我想到了一个网站，那就是特斯拉的零部件目录网站（Tesla Parts
Catalog）<https://epc.tesla.com/>，之前我从该网站中发现了一些有意思但不属于数据泄露的东西。

![](https://image.3001.net/images/20200223/1582461263_5e52714f9f504.jpeg!small)

##  漏洞1：编辑Cookie信息访问获取未公开车型Model Y的参数信息

我发现的漏洞是这样的。普通用户可以通过编辑Cookie信息，利用浏览器访问获取到特斯拉的一些非公开网页或数据。拥有特斯拉账户的公众用户，可以登录特斯拉零部件目录网站（epc.tesla.com）访问其中公布的车型部件数据。在访问测试该网站过程中，我发现了其中一个有意思的Cookie，可以通过编辑该Cookie信息，让非授权用户访问到特斯拉内部的非公众用户可浏览数据。如果放到过去，我觉得这没什么敏感的。但是，在Model
Y车型发布在即的关头，作为一个超级特斯拉爱好者，我通过媒体了解到了很多该款车型相关的信息，因此，急切想目睹那些还未公开的Model
Y相关零部件和原理图的心理驱使着我。

首先，我用我自己的公众账号登录特斯拉零部件目录网站（epc.tesla.com），之后，我在登录数据包中发现了一个名为EPCClaim的Cookie，在浏览器中它是base64编码的，如下：

![](https://image.3001.net/images/20200223/1582460897_5e526fe1c2b55.jpeg!small)解码之后的内容如下：

    
    
    {“employeeId”:0,”firstName”:”General”,”lastName”:”Public”,”email”:”REDACTED@*****.com”,”countryCode”:”US”,”languageId”:null,”languageCode”:null,”currencyCode”:null,”isInternalUser”:false,”isBodyShopUser”:false,”isGeneralPublic”:true,”tabs”:false,”locationId”:null,”bodyShopId”:0,”bodyShopName”:null,”bodyShopCategory”:null,”permissions”:[]}

哦，仔细观察上述解码内容，其中竟然出现了permission（权限）的键值，这是用来干什么的？于是，我在另外一个JS脚本文件<https://epc.tesla.com/scripts/scripts.8c9383be.js>中发现了一些相关线索：

    
    
    {accountManagement:”ACCOUNT_MANAGEMENT”,bodyShopManagement:”BODY_SHOP_MANAGEMENT”,bodyShopAccountManagement:”BODY_SHOP_ACCOUNT_MANAGEMENT”,repairOrder:”REPAIR_ORDER”,orderPane:”ORDER_PANE”,admins:”ADMINS”,epcUser:”EPC_USER”,addToolingData:”ADD_TOOLING_DATA”,model3Catalog:”MODEL3_CATALOG”,modelYCatalog:”READONLY_CATALOG”,toolingCatalog:”TOOLING_CATALOG”,serviceToolingCatalog:”SERVICE_TOOLING_CATALOG”,returns:”RETURNS”,statements:”STATEMENTS”,creditmemos:”CREDIT_MEMO”,genealogy:”GENEALOGY”,generalAccountManagement:”GENERAL_ACCOUNT_MANAGEMENT”,orderModel3:”ORDER_MODEL3",orderModelX:”ORDER_MODELX”,orderRoadster:”ORDER_ROADSTER”,orderModelS:”ORDER_MODELS”,orderTooling:”ORDER_TOOLING”,orderServiceTooling:”ORDER_SERVICE_TOOLING”,orderModelSR:”ORDER_MODELSR”}

可以看到，该JS脚本文件是我买车型Model 3的相关访问参数，但其中一个键值 **modelYCatalog:“READONLY_CATALOG”**
引起了我的注意，看到没，它包含了 **Model Y** ！

好吧，那我就来编辑一下上述Cookie，看看编辑重发请求之后，我会收到什么响应内容。

大多数权限值都会向UI用户界面添加选项，但是它们对应的API接口只会相应地限制给具有Token令牌的授权用户，并且不允许访问或写入数据。那么Model
Y涉及到的参数选项又如何呢？

这是访问我Model 3车型的Cookie：

    
    
    {“employeeId”:0,”firstName”:”General”,”lastName”:”Public”,”email”:”REDACTED@*****.com”,”countryCode”:”US”,”languageId”:null,”languageCode”:null,”currencyCode”:null,”isInternalUser”:false,”isBodyShopUser”:false,”isGeneralPublic”:true,”tabs”:false,”locationId”:null,”bodyShopId”:0,”bodyShopName”:null,”bodyShopCategory”:null,”permissions”:[]}

对比上述Model
3车型Cookie，我把其中的isGeneralPublic参数值更改为false（意思也就是非公众用户），把isInternalUser参数值更改为ture（内部用户），然后根据前述JS脚本中涉及Model
Y车型的modelYCatalog:“READONLY_CATALOG”线索，把permissions参数值更改为READONLY_CATALOG，最后的访问Cookie如下：

    
    
    {“employeeId”:0,”firstName”:”General”,”lastName”:”Public”,”email”:”REDACTED@*****.com”,”countryCode”:”US”,”languageId”:null,”languageCode”:null,”currencyCode”:null,”isInternalUser”:true,”isBodyShopUser”:false,”isGeneralPublic”:false,”tabs”:false,”locationId”:null,”bodyShopId”:0,”bodyShopName”:null,”bodyShopCategory”:null,”permissions”:”READONLY_CATALOG”}

接下来，我把该Cookie内容进行Base64编码形成Cookie值，用它去访问特斯拉零部件目录网站<https://epc.tesla.com/>
。之后，惊喜的是，我竟然可以在网站响应回来的零部件目录中看到Model Y车型的选项，点击进入，显示在眼前的就是完整的Model Y车型零部件参数数据！

##  漏洞上报和处理进程

> 2020.1.30 14:30:36 EST — 漏洞上报
>
> 2020.1.30 15:28:34 EST — 漏洞分类
>
> 2020.1.30 16:34:27 EST — 特斯拉把Model Y车型数据从中删除
>
> 2020.2.11 18:44:27 EST — 特斯拉修复漏洞并发放漏洞赏金

##  漏洞2：构造搜索功能访问获取未公开车型Model Y的参数信息

过了几天，我在访问特斯拉零部件目录网站<https://epc.tesla.com/>的过程中，又突发奇想，能不能通过其它方式获取到Model
Y车型数据？网站中的搜索功能引起了我的注意，通过它可以查询到给定车型的所有零部件目录信息。在搜索测试中我发现，该功能仅依靠当前用户的浏览目录来过滤数据，就比如，在目录3中搜索时就只能查询到Model
3车型的零部件数据。

之后，我想通过浏览器检查功能的网络请求操作，观察是否可以更改搜索功能的API调用参数，去查询Model
Y车型数据。然后我发现其API搜索建议为<https://epcapi.tesla.com/api/searchSuggestions>，其中提到搜索功能调用的三个主要请求参数：

> CatalogModel（车型目录）
>
> countryCode（国家代码）
>
> Term（关键词）

比如说，如果我们用关键词“bumper”（保险杠）在目录3（Model 3车型）下执行搜索，之后发起的搜索请求就是：

>
> [https://epcapi.tesla.com/api/searchSuggestions?catalogModel=Model3&countryCode=US&term=bumper](https://epcapi.tesla.com/api/searchSuggestions?catalogModel=Model3&countryCode=US&term=bumper)

用户登录特斯拉零部件目录网站后会生成一个Token令牌并存储在本地名为EPCToken参数中，搜索请求用该Token作为用户身份验证。但是我发现，Model
Y
车型数据却不受任何安全限制，任何可以登录特斯拉零部件目录网站的公众用户，只要具备EPCToken参数下有效的Token令牌，在搜索功能中把CatalogModel指定为ModelY，就能访问Model
Y 车型的详细参数数据。也就是这样的：

    
    
    curl ‘[https://epcapi.tesla.com/api/searchSuggestions?catalogModel=ModelY&countryCode=US&term=XYZ_Part_Name](https://epcapi.tesla.com/api/searchSuggestions?catalogModel=ModelY&countryCode=US&term=XYZ_Part_Name)’ -H ‘Connection: keep-alive’ -H ‘Accept: application/json, text/plain, /’ -H ‘Authorization: Bearer REDACTED’ -H ‘Accept-Language: en-us’ -H ‘User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36' -H ‘Origin: [https://epc.tesla.com](https://epc.tesla.com/)’ -H ‘Sec-Fetch-Site: same-site’ -H ‘Sec-Fetch-Mode: cors’ -H ‘Referer: <https://epc.tesla.com/>’ -H ‘Accept-Encoding: gzip, deflate, br’ — compressed

按照其中的term关键词请求之后，特斯拉零部件目录网站服务端会返回Model Y 车型与关键词匹配的详细零部件信息，包括零部件编号、名称、注释等。

另外，我还发现可以通过参数systemGroupId对零部件所属的部件组（the group of
parts）进行查询，比如可以通过以下包含systemGroupId的请求，查询相关部件组的使用情况：

>
> <https://epcapi.tesla.com/api/catalogs/XXX/categories/0/subcategories/0/systemGroups/XXXXX?vin=>

利用以上两种未授权方式，可以获取到目录Y下与Model Y 车型相关的所有参数信息。此外，通过Model
3车型的公开数据，可以变换搜索关键字、标题、注释方式查询Model Y 车型的大部份部件信息，与此对比Model
3车型的异同之处，然后再通过各个零部件识别相应的部件组，完全有可能逐一查询到Model Y 车型的各个零部件参数信息。

##  漏洞上报和处理进程

> 2020.2.19 12:53:43 EST — 漏洞上报
>
> 2020.2.19 14:15:49 EST — 特斯拉把Model Y车型数据从中删除
>
> 2020.2.19 17:06:47 EST — 漏洞修复 赏金发放

不得不说，特斯拉的漏洞修复处理和赏金发放流程非常快速及时。

***参考来源：[medium](https://medium.com/@evan.connelly/hunting-tesla-model-y-secrets-in-the-parts-catalog-2f453f853dd8)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

  

