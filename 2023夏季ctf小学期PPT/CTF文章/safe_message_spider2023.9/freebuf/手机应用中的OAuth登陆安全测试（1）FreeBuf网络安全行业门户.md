## 效果展示

鉴于本文写的太乱，实在怕有些同学因保护视力而不继续看下去，先放出通过后文描述的两种方法挖掘到的一小部分漏洞作为吸引。  
![图片.png](https://image.3001.net/images/20210201/1612193782_60181ff6dcf6c333267b0.png!small)![图片.png](https://image.3001.net/images/20210201/1612193783_60181ff75e82a35cbb9a0.png!small)![图片.png](https://image.3001.net/images/20210201/1612193784_60181ff804417eaf67795.png!small)

## OAuth2授权访问之implicit模式

首先来看下OAuth的定义：
OAuth（开放授权）是一个开放标准，允许用户授权第三方网站访问他们存储在另外的服务提供者上的信息，而不需要将用户名和密码提供给第三方网站或分享他们数据的所有内容。  
在大家测试过程中，常见到的快捷登录都是`授权码模式（authorization_code）`，也就是应用（QQ/微博）给出授权码`code`，服务端通过`code`换取`access_token`，再继续进行下一步请求。  
以我们外部的视角来看，大致流程如下：

![图片.png](https://image.3001.net/images/20210201/1612193784_60181ff8ee1b31c04b74e.png!small)

访问网站`a`，选择`微博`快捷登录，跳转到`api.weibo.com`，微博用户点击授权，然后会从`api.weibo.com`携带`code`参数跳转回网站`a`，我们的应用`a.com`得到了`code`就会在后端调用第三方提供的api去获取`uid、access_token`，这里参照微博给出的api文档https://open.weibo.com/wiki/%E5%BE%AE%E5%8D%9AAPI，通过`code`获取  
![图片.png](https://image.3001.net/images/20210201/1612193786_60181ffa925c259606b43.png!small)

下一步就可以继续通过`access_token`去请求第三方的其他api，来看一下[account/get_uid](https://open.weibo.com/wiki/2/account/get_uid)

![图片.png](https://image.3001.net/images/20210201/1612193789_60181ffd716fd697db13a.png!small)如上图，通过`access_token`请求该接口即可返回`uid`。

上面的描述，全部都是关于`授权码模式`，实际上implicit模式和`授权码模式`非常相似，只不过缺少了一个`code
=》access_token`的步骤，第三方会直接提供`access_token`给开发者使用，不再给出`code`。

 **1.未对微博的**` **access_token**` **校验导致任意用户登陆**

这个问题在多个app中见到了，我测试过的应用中大约有`10%`的app存在该问题，一旦出现后果就会很严重。这种利用方法，针对有微博快捷登陆的应用。

app中的微博快捷登陆是通过调起微博app请求`https://api.weibo.com/oauth2/sso_authoriz`，然后获取这个请求的返回`access_token`和`uid`，所以对于app中的微博快捷登陆并不存在`code`这一说法，这也就是我们第一段提到过的`implicit`模式。获取`access_token`的请求如下：  
![图片.png](https://image.3001.net/images/20210201/1612193792_601820006a48a68af2a06.png!small)

多数的应用会获取返回的`access_token`然后使用微博的api进行操作，但是应用只获取了`uid`而不去校验`access_token`然后就代入数据库进行查询，那么就存在一个任意登陆的问题。

#####一个案例：  
在这个应用内点击微博快捷登陆，然后调起微博app，注意到上面截图的`https://api.weibo.com/oauth2/sso_authoriz`请求，修改该请求返回的`uid`后放行后面的全部请求即可。

![图片.png](https://image.3001.net/images/20210201/1612193798_60182006857533acdd16d.png!small)

此时已经越权登陆了该微博绑定的账号，所有功能可用。  
原因如下，注意到在应用中的请求中有一个：`https://victim.com/user/thirdapp/login`，  
![图片.png](https://image.3001.net/images/20210201/1612193801_60182009c9654f7709f69.png!small)这是最关键的一个`set-cookie`的请求，其中请求参数`open_id`就是刚刚返回的微博帐号的用户`uid`，也就是刚刚我们修改的返回包的数值。  
微信快捷登陆也是这种`implicit`模式，但是这种攻击方法并不适用于微信快捷登陆，首先微信帐号的`open_id`不是公开内容，当然如果你想到可以自己搭一个第三方登录的平台，来获取微信用户的`open_id`也是不行的，因为同一个微信账号给不同的APP生成的`open_id`都是不一样的，所以无法利用，在这里给微信点赞。

这里补充一下如何获取指定微博账号的uid，查看用户页面的源代码搜索：$CONFIG['oid']  
https://weibo.com/wflanker  
![图片.png](https://image.3001.net/images/20210201/1612193805_6018200de0170d038fcd1.png!small)

## 修复方式：

如果一定要使用`uid`，使用此接口对`access_token`校验：<https://open.weibo.com/wiki/Oauth2/get_token_info>

![图片.png](https://image.3001.net/images/20210201/1612193810_601820120f980f61a9ca8.png!small)请求获取返回的uid，不要相信用户输入给你的uid。  
![图片.png](https://image.3001.net/images/20210201/1612193812_601820146ba0f528c1687.png!small)

## 最后

在当今，不管国内国外，几乎每一个站点都存在第三方快捷登录，国内主流的可能就是QQ/微博/微信，当然还是有其他的快捷登录方式，希望本文能够抛砖引玉，让各位同学能够发现更多种的快捷登录方式漏洞。

