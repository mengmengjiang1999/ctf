![](https://image.3001.net/images/20200305/1583383590_5e6084266ad70.jpg!small)

**这篇Writeup介绍了谷歌数据报表平台Google Data
Studio中的一个授权漏洞，作者利用该漏洞可以修改其他人分享的报告链接，实现对他人报告的劫持。**

## 漏洞介绍

Google Data Studio是谷歌的可视化报告处理平台，要发现授权漏洞需要了解目标应用的具体工作机制，为此我花了一些时间去熟悉Google Data
Studio。首先，我创建了一份空白报告，如下：

![](https://image.3001.net/images/20200305/1583383163_5e60827be2e7c.png!small)

![](https://image.3001.net/images/20200305/1583383175_5e6082877bc7e.png!small)

点击报告中的“共享”（Share）按钮右边的向下小箭头，会跳出一些功能选项，我们点击图中红框中的“获取报告链接”按钮，就能生成一个报告链接。

![](https://image.3001.net/images/20200305/1583383194_5e60829a4342e.png!small)

该报告链接是一个datastudio.google.com加随机字符串的样式，点击下方的“链接到当前报告的数据视图”（Link go your
current report view），就会向datastudio.google.com服务端发送一个网络请求，如下：

![](https://image.3001.net/images/20200305/1583383213_5e6082ada2042.png!small)

我们用Burp来进行抓包，内容如下：

![](https://image.3001.net/images/20200305/1583383227_5e6082bbe5fb0.png!small)

仔细观察其中的POST请求，可以发现其荐在两个参数，一个是reportId，另一个是shortLink里面的id：

    
    
    reportId : 87d41ef9–1ebc-4d92–84e7-d5948e5940ed
    
    id : m7PKn-j4R_s

起初看上去，id参数可能是我点击“链接到当前报告的数据视图”（Link go your current report
view）后生成的报告id，我想看看如果用其它随机值替换它会是什么样，为此，在reportId不变为87d41ef9–1ebc-4d92–84e7-d5948e5940ed的情况下，我把id参数换为“iamsushi”，然后提交请求：

![](https://image.3001.net/images/20200305/1583383267_5e6082e31c824.png!small)

之后，我访问<https://datastudio.google.com/s/iamsushi>链接，它竟然能成功跳转到了之前reportId为87d41ef9–1ebc-4d92–84e7-d5948e5940ed的报告来。默认来说，普通用户是无权访问特定报告的，除非在分享中有所指定。所以，照着这个思路，我想如果某报告已经由Google
Data Studio分配了一个id参数和reportId参数，那么，我是否能在reportId参数不变的情况下，对其id参数实施变换，修改成其它值呢？

非常意外，这种方法可以成功修改我另一个Google Data
Studio账号创建的报告，POST请求后，服务端也响应回来了200的状态码。这一修改之后，我另一Google Data
Studio账号创建的报告其最终链接中的id参数被覆盖，变成了其它链接。而本来的情况是，该报告是禁止下载和可读的。如下：

![](https://image.3001.net/images/20200305/1583383286_5e6082f61fcf3.png!small)

所以，这里的攻击思路是，我创建自己的报告，生成<https://datastudio.google.com/s/XXXX>的报告链接，然后通过Google
Dork方式查找一些在线的，曝露shortlinks中id参数的其他人报告，接下来，就把其他人的报告id参数更改成我自己的报告id参数XXXX，这样一来，如果用户访问其他人的报告也就会指向了我的报告，实现对他人报告的劫持。

![](https://image.3001.net/images/20200305/1583383305_5e608309c76ed.png!small)

按耐不住心情，我及时把漏洞上报，之后谷歌很快回复称漏洞已被接收分配。但是，我却发现其中的reportId参数我还没测试过啊，所以我继续进行了测试。我简单把上述创建报告的reportId参数87d41ef9–1ebc-4d92–84e7-d5948e5940ed，把最前面的8变成了7，换为77d41ef9–1ebc-4d92–84e7-d5948e5940ed，进行了POST提交，得到的却是状态码为500的响应。

![](https://image.3001.net/images/20200305/1583383392_5e6083602b339.png!small)

我想估计77d41ef9–1ebc-4d92–84e7-d5948e5940ed是一个无效的reportId参数，所以当我把它替换成另一个有效的reportId参数后，执行POST请求，Google
Data Studio服务端可以有效响应。

![](https://image.3001.net/images/20200305/1583383405_5e60836da6ab2.png!small)

之后，我及时向谷歌上报解释了该情况。

## 经验总结

> 在做Web应用测试之前，应该熟悉目标应用的工作机制；
>
> 抱着游戏的心态去分析测试漏洞，在其中反复测试，去发现一些可疑行为；
>
> 站在安全防护的角度去考虑问题，去想办法突破固定的安全模式；
>
> 测试IDOR漏洞时，要留意服务端响应，有些响应虽然不成功，但其中透露的信息可能有用；
>
> 要学会记录和思考，判断哪些操作是开发者忽视掉的，而用户却可执行的；
>
> 发现漏洞时，要认真思考它的危害性。

## 漏洞上报和修复进程

> 2019.11.22: 漏洞初报
>
> 2019.11.23: 追加reportId参数可替换的解释
>
> 2019.12.5：谷歌无法复现漏洞
>
> 2019.12.5：我发送详细漏洞信息
>
> 2019.12.14：漏洞被分类为P2级别
>
> 2019.12.16：漏洞被分类为P1级别
>
> 2020.1.4：谷歌发放漏洞奖励
>
> 2020.2.4：谷歌修复漏洞

 **参考来源：[medium](https://medium.com/@sushiwushi2/hijacking-shared-report-links-in-google-data-studio-75eab320c391)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

