***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ** ***文章作者：Arrowzzzzzz，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
**

 **本文主要是分析慢雾安全团队[《⼀个通杀绝⼤多数交易平台的 XSS 0day
漏洞》](https://mp.weixin.qq.com/s/yfbKf_5Nk2NXFl2-xlFqKg?https://msdn.microsoft.com/zh-cn/library/be21c7hw\(v=vs.94\).aspx)，根据慢雾区匿名情报，通用 K 线展示 JS 库 TradingView 存在
XSS 0day 漏洞，可绕过 Cloudflare 等防御机制。该漏洞被利用会导致用户帐号权限被盗、恶意操作等造成资产损失。**

下面进入正题。

Tradingview 图表库，下载下来是一个charting_library文件夹，文件夹里面有：

![Tradingview
dom_xss1.png](https://image.3001.net/images/20181014/1539513855_5bc31dffd86d4.png!small)

其中charting_library.min.js
包含外部图表库widget接口。此文件不应该被修改。static文件夹中存储图表库内部资源，不适用于其他目的。

问题是出现在tv-chart.630b704a2b9d0eaf1593.html(tv-chart*.html)，当我下载好TradingView插件后会自动生成tv-chart*.html这个文件，中间的*是随机值

![Tradingview
dom_xss2.png](https://image.3001.net/images/20181014/1539513855_5bc31dffe8fa6.png!small)

我们查看该html ：  
![Tradingview
dom_xss3.png](https://image.3001.net/images/20181014/1539513857_5bc31e0103dbf.png!small)

因为他是dom型xss，那么就查看是否有script标签(一般获取dom值使用javascript获取的)。

查看后你会发现没有获取disabledFeatures ;enabledFeatures
;indicatorsFile这3个参数的地方，那么第二种可能就是html里远程加载的js了(这些远程加载js就像我们写python种导入的库一样，当我们需要某些功能的结果时，就导入对应的库，执行里面的函数，获取结果值，在将值放到我们需要操作的地方)

在这里我们发现他远程加载了3个js：

![Tradingview
dom_xss4.png](https://image.3001.net/images/20181014/1539513856_5bc31e001a292.png!small)![Tradingview
dom_xss5.png](https://image.3001.net/images/20181014/1539513856_5bc31e0048a91.png!small)

我们去一一查看对应的js文件。

spin.min.js：

![Tradingview
dom_xss6.png](https://image.3001.net/images/20181014/1539513856_5bc31e005e9a5.png!small)

vendors.fd8604c09abed9f6643a.js：  
![Tradingview
dom_xss7.png](https://image.3001.net/images/20181014/1539513856_5bc31e00ba0ee.png!small)

我们对上面2个js未能查找到存在xss的参数。

library.19c99ed5d0307c67f071.js：

![Tradingview
dom_xss8.png](https://image.3001.net/images/20181014/1539513856_5bc31e00c55e9.png!small)

我们分析下存在漏洞的参数indicatorsFile。

    
    
    D ? $.getScript(urlParams.indicatorsFile).done(function() 

这个是当时代码，我们看看?号,在js中问号是运算符，语法如下：

    
    
    test ? expression1 : expression2

参数：

test-任何 Boolean 表达式。

expression1-如果 test 为 true，则返回表达式，可能是逗号表达式。

expression2-如果 test 为 false，则返回表达式，可以使用逗号表达式链接多个表达式。

所以D是test，要是他是真就执行expression1($.getScript(urlParams.indicatorsFile).done(function())如果是假就执行:(冒号)后面的代码。

![Tradingview
dom_xss9.png](https://image.3001.net/images/20181014/1539513857_5bc31e01291c0.png!small)

我们再看。

$.getScript()，在js中代表通过 HTTP GET 请求载入并执行 JavaScript 文件。

![Tradingview
dom_xss10.png](https://image.3001.net/images/20181014/1539513857_5bc31e015c295.png!small)

$查询了下资料，这里面可能代表我们导入的jquery，就像python中导入time库，要用到sleep函数的时候需要time.sleep()这样写。  
![Tradingview
dom_xss11.png](https://image.3001.net/images/20181014/1539513857_5bc31e016a3e9.png!small)

urlParams.indicatorsFile：

后面的indicatorsFile我们知道是dom的参数，那么urlParams是什么了，我们查看之前的html文件。

![Tradingview
dom_xss12.png](https://image.3001.net/images/20181014/1539513857_5bc31e0167270.png!small)

location.href;(设置或返回完整的 URL)  
![Tradingview
dom_xss13.png](https://image.3001.net/images/20181014/1539513857_5bc31e01b3353.png!small)

    
    
    p.indexOf("#");

p是前面location.href;的返回值；indexOf()可返回某个指定的字符串值在字符串中首次出现的位置。

语法：

    
    
    stringObject.indexOf(searchvalue,fromindex)

参数：

searchvalue-必需。规定需检索的字符串值。

fromindex-可选的整数参数。规定在字符串中开始检索的位置。它的合法取值是 0 到 stringObject.length -1。如省略该参数，则将从字符串的首字符开始检索。

注释：

如果要检索的字符串值没有出现，则该方法返回 -1。

![Tradingview
dom_xss14.png](https://image.3001.net/images/20181014/1539513857_5bc31e01d1805.png!small)

后面if判断是否有#，如果有函数k的返回值是p.substring(o + 1) 。  
![Tradingview
dom_xss15.png](https://image.3001.net/images/20181014/1539513857_5bc31e01bef5a.png!small)

substring()用于提取字符串中介于两个指定下标之间的字符。

语法：

    
    
    stringObject.substring(start,stop)

参数：

start-必需。一个非负的整数，规定要提取的子串的第一个字符在 stringObject 中的位置。

stop -可选。一个非负的整数，比要提取的子串的最后一个字符在 stringObject 中的位置多
1。如果省略该参数，那么返回的子串会一直到字符串的结尾。

![Tradingview
dom_xss16.png](https://image.3001.net/images/20181014/1539513858_5bc31e0244ed0.png!small)

后面就是正则匹配出我们#后的参数和值了 ：  
![Tradingview
dom_xss17.png](https://image.3001.net/images/20181014/1539513858_5bc31e021a9a9.png!small)

/([^&=]+)=?([^&]*)/g中g的意思是执行全局匹配（查找所有匹配而非在找到第一个匹配后停止）。  
![Tradingview
dom_xss18.png](https://image.3001.net/images/20181014/1539513858_5bc31e02498ce.png!small)![Tradingview
dom_xss19.png](https://image.3001.net/images/20181014/1539513858_5bc31e025878d.png!small)![Tradingview
dom_xss20.png](https://image.3001.net/images/20181014/1539513858_5bc31e029194d.png!small)

已经把传参和值都匹配出来了。

j是个列表，他的值是[disabledFeatures=[321],disabledFeatures,[321]]，所以我取后面的2个值。

![Tradingview
dom_xss21.png](https://image.3001.net/images/20181014/1539513858_5bc31e02af2c6.png!small)![Tradingview
dom_xss22.png](https://image.3001.net/images/20181014/1539513858_5bc31e02e9ae3.png!small)

n[e(j[1])] = e(j[2])这个就是在n这个object中添加属性和值。

创建对象：

    
    
    var obj = {}; //或者 var obj=new Object();

添加属性和值：

    
    
    var key = "name";
    
    var value = "张三丰"
    
    obj[key] = value;

![Tradingview
dom_xss23.png](https://image.3001.net/images/20181014/1539513859_5bc31e0335cd6.png!small)![Tradingview
dom_xss24.png](https://image.3001.net/images/20181014/1539513859_5bc31e0336bae.png!small)![Tradingview
dom_xss25.png](https://image.3001.net/images/20181014/1539513859_5bc31e037475c.png!small)![Tradingview
dom_xss26.png](https://image.3001.net/images/20181014/1539513859_5bc31e03b2d6c.png!small)![Tradingview
dom_xss27.png](https://image.3001.net/images/20181014/1539513860_5bc31e0406a44.png!small)![Tradingview
dom_xss28.png](https://image.3001.net/images/20181014/1539513860_5bc31e0424cb2.png!small)

e中replace是返回一个由替换值替换一些或所有匹配的模式后的新字符串。模式可以是一个字符串或者一个正则表达式，替换值可以是一个字符串或者一个每次匹配都要调用的函数。

语法如下：

    
    
    str.replace(regexp|substr, newSubStr|function)
    
    regexp (pattern)

一个RegExp 对象或者其字面量。该正则所匹配的内容会被第二个参数的返回值替换掉。

    
    
    substr (pattern)

一个要被 newSubStr 替换的字符串。其被视为一整个字符串，而不是一个正则表达式。仅仅是第一个匹配会被替换。

    
    
    newSubStr (replacement)

用于替换掉第一个参数在原字符串中的匹配部分的字符串。该字符串中可以内插一些特殊的变量名。参考下面的使用字符串作为参数。

    
    
    function (replacement)

一个用来创建新子字符串的函数，该函数的返回值将替换掉第一个参数匹配到的结果。参考下面的指定一个函数作为参数。

![Tradingview
dom_xss29.png](https://image.3001.net/images/20181014/1539513860_5bc31e0412835.png!small)![Tradingview
dom_xss30.png](https://image.3001.net/images/20181014/1539513860_5bc31e04ada2e.png!small)

将我disabledFeatures参数值1+2+3里+号替换成空格。  
![Tradingview
dom_xss31.png](https://image.3001.net/images/20181014/1539513860_5bc31e04ab7b6.png!small)

匹配</等开始到>结束,将匹配到的值替换成空。

urlParams.indicatorsFile就是indicatorsFile参数的值：

![Tradingview
dom_xss32.png](https://image.3001.net/images/20181014/1539513860_5bc31e049f32a.png!small)所以，library.19c99ed5d0307c67f071.js.中$.getScript(urlParams.indicatorsFile)就是获取indicatorsFile的值，并且用getScript加载该值
。  

***文章作者：Arrowzzzzzz，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

