![](https://image.3001.net/images/20190820/1566295709_5d5bc69d3f7b0.jpg!small)

**大家好，今天分享这篇Writeup是关于Youtube的两个漏洞，确切来说，是Youtube
Studio平台（<https://studio.youtube.com/>）漏洞。作者通过其中涉及的视频id和频道id，从而可以对任意Youtube视频进行属性修改，并获取到相关用户的私享频道视频。**

[Youtube
Studio平台](https://studio.youtube.com/)是全新的创作中心，用户可以在上面轻松管理YouTube帐号、上传视频、推动频道发展并与观众互动，该平台具备多种炫酷功能，包括查看视频分析数据、更改社区和频道相关设置以及批量视频更新等。

##  一、更改任意Youtube视频的设置信息

当访问Youtube
Studio主页，可以看到左边有一列菜单栏，其中有一个名为“视频（Videos）”的菜单，点击它之后，会跳出Youtub上所有你上传或编辑过的视频，如下：

![](https://image.3001.net/images/20190820/1566295343_5d5bc52f7cc7f.png!small)

如果你是一名视频制作者，想一次对所有视频做个批量修改，比如，在视频描述中添加合作者链接，在标题中添加标签或把视频设置为私有等等。那么，这里有一个功能可以实现这种操作。首先，选中你要编辑的视频，然后在视频栏上方黑色区域会出现一条工具栏（toolbar），在“修改”按钮下有“标题”、“说明”、“标签”、“公开范围”、“评论”等属性可待修改，按照不同类别选定修改后，在右边会出现一个“更新（UPDATE
VIDEOS）”按钮，点击即可完成视频属性更改。

![](https://image.3001.net/images/20190820/1566295372_5d5bc54c6bd01.png!small)

> 当点击这个“更新（UPDATE
> VIDEOS）”按钮之后，便会触发一个发送到Youtube服务器的POST请求：<https://studio.youtube.com/youtubei/v1/creator/enqueue_creator_bulk_action>

请求主体为JSON格式代码，该JSON内容包括各种视频属性和配置参数，但是在其中有一个参数引起了我的注意，那就是名为“videos”的参数，它由一个包含视频id的videoIds数组表示，如下:

![](https://image.3001.net/images/20190820/1566295403_5d5bc56ba1e37.png!small)

分析一番之后，我发现没有任何验证或保护措施来保证这些视频id确实与用户实际发起更改的视频相对应，也就是说，我可以通过更改这些视频id来实现对任意Youtube视频的属性更改。

该漏洞影响还是相对较大的，比如我可以把一些频道的视频设置为私有，间接关闭掉该频道，造成视频无法公开被观看，导致粉丝流失。当然，也还可以在某些流行视频的说明中加入某些内容或链接，实现宣传某些网站或产品的目的。另外，某些投机份子甚至会在一些高点击量视频中加入与自己账户对应的“打赏”功能，来赚取零花钱。以下就是该漏洞的一个POC验证：

## 演示视频

漏洞上报进程

> 2018.11.11 漏洞上报
>
> 2018.11.12 漏洞分类 - 被评定为好洞“Nice catch”
>
> 2018.11.13 漏洞奖励
>
> 2018.11.13 漏洞修复

##  二、获取任意Youtube用户私享播放资源列表

这是一个逻辑漏洞，因为攻击者可以通过它来获取目标Youtube用户未列出的播放资源列表。任何时候，当Youtube用户想在Studio平台中编辑发布某个视频时，需要点击该视频，之后会跳出一个发布编辑窗口，如下：

![](https://image.3001.net/images/20190820/1566295493_5d5bc5c5ed47b.png!small)

> 当该窗口打开时，会在后台发起一个请求Youtube
> Studio服务的POST请求：<https://studio.youtube.com/youtubei/v1/creator/list_creator_playlists>
> endpoint

如其链接所表达的意思，它会提取出当前视频对应的登录用户信息，该请求的作用在于，从其对应的编辑窗口充实播放列表的相关信息。

另外，该请求也是一个JSON格式，其中包含了频道名称对应的channelId参数，它表示当前编辑视频对应的频道。经过研究，我发现在这个channelId参数数值与用户身份之间，Youtube也未做必要的验证措施。

![](https://image.3001.net/images/20190820/1566295551_5d5bc5ff395a7.png!small)

通过Youtube返回的响应消息我发现，当某个频道满足一个条件：只有PUBLIC（公开）和UNLISTED（私享）两种播放列表时，我们就能利用该漏洞获取到它所有的播放列表资源。

![](https://image.3001.net/images/20190820/1566295570_5d5bc61219f67.png!small)

如果目标Youtube用户满足上述条件，攻击者可以利用该漏洞获取到任意Youtube用户的任何私享视频（Unlisted），由于私享视频不会出现在YouTube搜索结果或频道网页中，只有获得链接的用户才能观看，所以这个漏洞算是一个涉及隐私的漏洞。（YouTube为用户提供了第三种视频隐私选项“unlisted”，方便用户私下与好友分享视频。隐私选项被设置为“unlisted”的视频不会出现在YouTube搜索结果、频道网页或用户档案中，只有获得链接的用户才能观看“unlisted”视频。）

漏洞上报进程

> 2018.11.12 漏洞上报
>
> 2018.11.13 漏洞分类
>
> 2018.11.14 被评定为好洞“Nice catch”
>
> 2018.11.30 漏洞奖励
>
> 2018.12.12 漏洞修复

##  总结

在我的Hacking Google经历中，我尝试着对不同功能点进行了安全分析，其中也学到了很多经验，这两个漏洞仅当分享，希望大家都能有所收获。

***参考来源：[medium](https://medium.com/@dekeeu/reposted-2019-hacking-youtube-for-fun-and-profit-8685dd475e30)，clouds编译整理，转载请注明来自FreeBuf.COM**

  

