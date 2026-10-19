***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

**大家好，在我的上一篇文章中，我分享了[Chrome浏览器中存在的一个Facebook用户信息泄露漏洞](https://www.imperva.com/blog/a-bug-in-chrome-gives-bad-actors-license-to-play-20-questions-with-your-private-data/)，此后，在接下来的研究中，我又发现了另外一个关于Facebook的漏洞，利用该漏洞，可允许其它网站提取出Facebook受害者用户和其好友的个人隐私信息。**

需要说明的是，我于2018年5月发现了该漏洞，出于漏洞影响的严重性，我及时上给了Facebook，并与其安全团队协作进行了缓解开发，最终实现了成功修复。由于该漏洞还暂未完全公开，以下内容只针对漏洞原因和危害作出解释。

![Facebook](https://image.3001.net/images/20181115/1542262782_5bed0ffe71349.png!small)

## 漏洞发现

在之前对Chrome浏览器的研究过程中，我认真浏览了Facebook的一些在线搜索结果，我注意到，在其每个在线搜索结果的HTML里，都会包含一个iframe元素，这个iframe元素很可能是Facebook用来进行内部跟踪的标记。因为我自己对iframes的一些特别跨域行为（cross-origin）算是有些了解，于是，我想到了以下测试技巧：

首先，让我们来看一下Facebook中内置的搜索功能页面，该功能有一个后端接口，用来接收一些搜索参数的GET请求，像大多数搜索接口一样，这里接口后端没有设置跨站请求伪造（cross-site request forgery，CSRF）保护机制，也就是说，用户可以通过URL来共享搜索结果页面。

大多数情况下，我们的Facebook用户是不会围绕这个搜索接口来执行多种操作的，当然，也就发现不了这背后的CSRF攻击。但事实是，与大多Web元素不同，iFrame会部份曝露于一些跨域文档中（cross-origin document），与搜索式的CSRF问题一结合，就会发现其中存在的漏洞问题。

以下是一个漏洞验证PoC视频，结合Facebook中的搜索接口，利用漏洞，我可以发现Facebook受害者 用户对其他Facebook用户主页的点赞情况：

## 演示视频：

## 漏洞利用过程

要使这种攻击有效，我们需要欺骗Facebook受害者用户去打开我们的构造的恶意网站，让他点击网站上的任何地方，这种地方可以嵌入一些JavaScript脚本进行迷惑，之后，用构造成型跳出的Facebook搜索页面弹出窗或新标签，引诱用户执行我们想要的任何搜索查询结果。

因为页面中iframe元素的个数代表了搜索结果数量，这样的话，我们可以调用访问fb.frames.length接口属性，对iframe执行一个简单的记数。

通过操纵Facebook的图谱搜索（Facebook’s Graph
Search）功能，我们可以构造一些反映Facebook受害者用户的个人隐私信息搜索请求。

> Facebook’s Graph
> Search：为Facebook的图谱搜索功能，并不是图片搜索的意思，这是Facebook于2013年初推出并加入的新型搜索功能，与常规搜索引擎的关键词搜索不同，Graph
> Search能够判断用户希望获取的信息，直接向用户提供有关人、照片、地方和兴趣等问题的答案。Facebook的图谱搜索算是一种社交图谱搜索。
>
> 比如，针对英文版Facebook的图谱搜索场景，在漏洞利用中，我用“pages I like named
> `Imperva`”搜索一些目标Facebook受害者用户赞过的主页用户，通过伪造带有迷惑性质的POC页面，引诱受害者用户执行搜索，返回我们想要收集的信息，这样就可以间接对其个人隐私的窃取。

![](https://image.3001.net/images/20181115/1542262507_5bed0eeba92f6.png!small)

## 延伸利用

类似的构造搜索，我们还可以构造诸如窃取Facebook受害者用户好友信息的操作，例如，用“my friends who like
Imperva”的构造搜索，来查看受害者用户列表中点赞过Imperva主页的好友有哪些。当然，其它有意思的构造搜索如下：

> 查看当前Facebook受害者是否有来自以色列的好友：
>
> <https://www.facebook.com/search/me/friends/108099562543414/home-> residents/intersect>
>
> 查看当前Facebook受害者是否有名为“Ron”的好友：
>
> <https://www.facebook.com/search/str/ron/users-named/me/friends/intersect>
>
> 查看当前Facebook受害者是否在某国或某个地方拍了照片：
>
> <https://www.facebook.com/search/me/photos/108099562543414/photos-> in/intersect>
>
> 查看当前Facebook受害者是否有伊斯兰朋友：
>
> <https://www.facebook.com/search/me/friends/109523995740640/users-religious-> view/intersect>
>
> 查看当前Facebook受害者是否有伊斯兰朋友且住在英国
>
> <https://www.facebook.com/search/me/friends/109523995740640/users-religious-> view/106078429431815/residents/present/intersect>
>
> 查看当前Facebook受害者是否在朋友圈发布了包含某个特定词汇的帖子：
>
>
> [https://www.facebook.com/search/posts/?filters_rp_author=%7B%22name%22%3A%22author_me%22%2C%22args%22%3A%22%22%7D&q=cute%20puppies](https://www.facebook.com/search/posts/?filters_rp_author=%7B%22name%22%3A%22author_me%22%2C%22args%22%3A%22%22%7D&q=cute%20puppies)
>
>
> 查看当前Facebook受害者是否有朋友，在朋友圈发布了包含某个特定词汇的帖子：[https://www.facebook.com/search/posts/?filters_rp_author=%7B%22name%22%3A%22author_friends%22%2C%22args%22%3A%22%22%7D&q=cute%20puppies](https://www.facebook.com/search/posts/?filters_rp_author=%7B%22name%22%3A%22author_friends%22%2C%22args%22%3A%22%22%7D&q=cute%20puppies)

由于攻击者可以通过运行以下代码来控制Facebook的窗口位置属性，所以，无需打开新的弹出窗口或标签即可重复构造搜索过程：

![重复构造搜索过程](https://image.3001.net/images/20181115/1542262573_5bed0f2d37ffb.png!small)

对适用场景来说，这种攻击对移动端用户的潜在威胁可能较大，因为移动端的搜索标签可能很容易被用户在后台忽略或丢失，这样就会让攻击者执行多种组合构造搜索，当用户在观看手机视频或阅读文章时，个人隐私信息就被攻击者悄悄窃取。

## 总结

简而言之，该漏洞暴露了Facebook受害者用户及其朋友的兴趣和活动相关信息，即使Facebook受害者用户在其隐私设置中，设置此类信息只有自己或朋友可见，这种攻击仍然有效。

 ***参考来源：[imperva](https://www.imperva.com/blog/facebook-privacy-bug/)，clouds编译，转载请注明来自FreeBuf.COM**

