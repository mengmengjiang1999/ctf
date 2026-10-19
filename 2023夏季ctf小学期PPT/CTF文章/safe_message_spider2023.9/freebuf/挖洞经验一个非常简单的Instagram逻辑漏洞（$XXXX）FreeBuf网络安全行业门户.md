![](https://image.3001.net/images/20191217/1576572333_5df895adc921e.jpg!small)

**本文分享的是作者通过普通浏览就发现的Instagram的一个逻辑漏洞，漏洞非常非常非常简单，最终该漏洞获得了Facebook官方$XXXX的奖励和榜单致谢，作者也收获了漏洞测试的一些新思路和新视角，我们一起来看看。**

我平时不怎么用Instagram，但是，有天晚上我突然需要确认一下我的Instagram账户，于是我进行了登录，由于好长时间不用，我想把密码更改成一个容易记住的，所以我去到了设置项中更改了密码。

但当更改完密码之后，我在设置栏中发现了一个新功能-“Authorized
App”，经过了解可知这是一个授权第三方APP应用访问我Instagram数据的功能，其中存在两个按钮“Active“和”Expired”，当我点击“Active“之后，我看到了一个经授权激活的第三方APP-“TikTok”（抖音）。

![](https://image.3001.net/images/20191217/1576572189_5df8951db70f3.png!small)

可是，我从来没有TikTok账户，也从来没在Instagram中授权过TikTok啊！之后，我只有通过其中的可选按钮“Remove”进行了删除，但是，点击“Remove”之后，在页面左下角又跳出了一个告警消息“there
was a problem revoking access”（撤销出错）。

![](https://image.3001.net/images/20191217/1576572207_5df8952f1bc1b.png!small)

我想，这可能属于逻辑漏洞范畴，所以我选择上报给了Facebook，之后，Facebook收下了该漏洞并给予了我$XXXX的奖励以及榜单致谢。

 ***参考来源：[medium](https://medium.com/nassec-cybersecurity-writeups/this-is-how-i-got-xxxx-from-facebook-for-instagram-bug-aaff50342246)，clouds
编译整理，转载请注明来自 FreeBuf.COM**

