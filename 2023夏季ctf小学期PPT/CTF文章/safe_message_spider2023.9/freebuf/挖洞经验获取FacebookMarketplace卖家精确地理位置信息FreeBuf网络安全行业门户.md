***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **![获取Facebook
Marketplace卖家精确地理位置信息](https://image.3001.net/images/20190506/1557147441_5cd02f315a9f9.jpg!small)**
**本文分享的writeup是与Facebook
Marketplace销售系统相关的用户信息泄露漏洞，通过该漏洞可以获取到发布商品卖家的精确到经纬度和邮编等具体地理位置信息。漏洞上报一波三折，经历拒绝后再次被Facebook接收，最终Facebook给予的奖励为$5,000美金。以下是作者的漏洞发现分享。**

##  **Facebook Marketplace 简介  
**

Facebook
Marketplace是Facebook于2016年10月在移动端推出的一个P2P（个人对个人）的商品拍卖和交易功能，允许用户在其上购买和销售物品。

点击Facebook底部的Marketplace按钮进入，在界面中用户可以像网络商城那样直接以商品名字、种类和售价等分类来搜索某商品，Facebook会自动为用户显示最靠近用户身边的Facebook卖家，并显示该卖家的报价和商品信息。在找到心仪商品之后，用户便可以直接用Messenger来与该卖家联络。而如果你是卖家，你也可以直接在Marketplace中添加商品、报价、地点等相关消息。与一般拍卖网站不同的是，其内置的地点工具可以调整中你正在查看的地区，或变更为其它城市。目前，Facebook
Marketplace服务仅在某些国家开放。

## 发现漏洞的原因

Facebook Marketplace上线后，有些卖家会在上面销售一些被盗商品，所以我有时会协助调查Facebook
Marketplace中的一些被盗商品，在分析其相关的可追回技术可行性过程中，我发现了其中存在的一个漏洞，利用该漏洞可以发现卖家的一些敏感数据，获取其包含经纬度的精确地理位置。  

以我要卖掉的下图这辆7000欧的山地自行车拍卖销售页面分析入手，经测试，我发现Facebook
Marketplace中与地理位置相关的数据信息相对具体，它包含在销售商品返回的广告中，其相关的响应消息为JSON格式内容，而这种卖家商品的地理位置又可以通过Facebook
Marketplace进行设定。

![获取Facebook
Marketplace卖家精确地理位置信息](https://image.3001.net/images/20190506/1557146799_5cd02cafef56a.png!small)为此，我觉得有些疑惑，为什么Facebook
Marketplace呈现在用户页面上的商品地理位置又非常简单呢？这看来值得深究一番。

## 深入分析

于是，我又登录进入Facebook Marketplace应用，把这辆7000欧的山地自行车，用其中的地图位置选择工具设置了一个随机地址，看看有什么反应：

![获取Facebook
Marketplace卖家精确地理位置信息](https://image.3001.net/images/20190506/1557146985_5cd02d69d3333.jpg!small)哦，看到没，在右下角之处，有一行小而灰色的字，Facebook
Marketplace声称为了保护卖家隐私，位置信息仅只是大概位置（“Location is approximate to protect the
seller’s privacy”），哟，还不错。

好吧，退出Facebook
Marketplace看看这次请求包中的位置数据是什么，注意此时我是一个未授权的普通用户。在销售页面中，我开启了Chrome的浏览器网络监控功能，当我点击了这辆山地车的相关信息之后，可以在网络数据包中看到很多关于该商品的位置信息，查看后，我发现是Facebook的API
- facebook.com/api/graphql 在响应时泄露了一些地理位置信息，如下：

![获取Facebook
Marketplace卖家精确地理位置信息](https://image.3001.net/images/20190506/1557147082_5cd02dca0a8d3.png!small)其中竟然包含了商品发布的精确地理位置信息，有经纬度数据、城市、国家、邮编，如下：

    
    
    "location": {
    
       "latitude": 54.9942235,
    
       "longitude": -1.6041244,
    
       "reverse_geocode": {
    
             "city": "Newcastle upon Tyne",
    
             "state": "England",
    
             "postal_code": ""
    
       },
    
       "reverse_geocode_detailed": {
    
          "city": "Newcastle upon Tyne",
    
          "state": "England",
    
          "postal_code": "NE2 2DS"
    
       }
    
    }

经纬度！？哦，足够了！打开谷歌地图，输入其中的经纬度信息进行查找，当然，就发现了我在商品后台设置的具体地理位置了！

![获取Facebook
Marketplace卖家精确地理位置信息](https://image.3001.net/images/20190506/1557147152_5cd02e103a286.png!small)由于卖家很少会去刻意伪造销售商品的实际地理位置，而这种精确到米的地理位置和城市及邮编信息泄露，再结合交易过程涉及的卖家真实姓名，恶意攻击者或其它别有用心者可以利用它来准确确定卖家的具体住址。

## 这算是安全漏洞或问题吗？

由于卖家必须在商品发布过程中标明确切的个人位置信息，而Facebook
Marketplace又声称会保护用户隐私，会做地理位置模糊化显示给浏览者。就像我设置山地车的销售位置时，拖动地图选择的圆圈后，Facebook
Marketplace表明只会显示大概位置，当然，很少有卖家会刻意伪造这种地理位置信息。

另外，当我想用Facebook
Marketplace提交一些具体精确的地理位置时，Facebook提供的位置或地址选择项中根本没有一些更准确或更近的位置可以选择，就算输入完整邮编或地址都不行。

![获取Facebook
Marketplace卖家精确地理位置信息](https://image.3001.net/images/20190506/1557147302_5cd02ea698bae.png!small)所以，这种就互相矛盾了，那么，这就算是一种安全问题了。

## 这难道是Facebook的预期行为？

我本以为Facebook会从地图选择圆圈中随机分配到其中的一个位置，或者像某些Web应用一样会捕捉到最近的大概位置。我也期望Facebook只显示邮编的前三四个数字。但事实，当Facebook采取措施防止这些信息泄露时，以上模糊化的大概位置显示貌似是他们采取的方法。但是，现在当我试图在Facebook
Marketplace添加一个销售商品时，Facebook甚至会去抓拍与其位置相关的当地一个公园图片，完全说不通。

## 漏洞上报

这无疑是一个安全漏洞了，我及时上报给了Facebook，并高亮显示了其中的邮编，但是却被Facebook拒绝了，他们认为这不是一个安全漏洞。不服气的我又继续分析了其中的相关参数，并再次更新上报，WTF，又被拒。好在我认识一个在Facebook工作的朋友，和他聊了聊，他把漏洞转给了某位内部人士进行了深入了解，最终，我的漏洞被接收了，一周后Facebook修复了漏洞并奖励了我$5,000美金。

 ***参考来源：[7elements](https://www.7elements.co.uk/resources/blog/facebooks-burglary-shopping-list/)，clouds编译，转载请注明来自FreeBuf.COM**  

