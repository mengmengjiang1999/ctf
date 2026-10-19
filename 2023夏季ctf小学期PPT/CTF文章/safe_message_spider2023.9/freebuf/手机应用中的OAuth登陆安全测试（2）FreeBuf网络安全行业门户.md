手机应用中的OAuth登陆安全测试（1）见：<https://www.freebuf.com/vuls/262710.html>

## 效果展示

鉴于本文写的太乱，实在怕有些同学因保护视力而不继续看下去，先放出通过后文描述的两种方法挖掘到的一小部分漏洞作为吸引。  
![图片.png](https://image.3001.net/images/20210201/1612193782_60181ff6dcf6c333267b0.png!small)  
![图片.png](https://image.3001.net/images/20210201/1612193783_60181ff75e82a35cbb9a0.png!small)  
![图片.png](https://image.3001.net/images/20210201/1612193784_60181ff804417eaf67795.png!small)

本次要说的问题是，微博access_token校验不严格导致交互后劫持账号

这种问题存在于99%的应用内，这种利用方法，也只针对微博快捷登陆。这种问题的危害不如第一种明显，是一种需要交互进行的漏洞，随便提交了几家观察了一下厂商的反应，多数是中危，少数是高危，也有些厂商因为自己家有大量app存在该问题，打包提交，也能给出个高危的奖励。更多厂商的评级看各位的提交结果了～

当一个应用不存在第上一篇提到的问题的时候并不一定完全没了风险，通过[微博的官方调试平台](https://open.weibo.com/tools/console#)你看得出来每个微博`api`请求只需要一个`access_token`凭证就可以了，并不需要一些`appid`或者`uid`的信息。  
其中有一些非常简单的请求，比如：  
![图片.png](https://image.3001.net/images/20210201/1612193815_60182017b3e57c37e8bdf.png!small)

如果客户端获得了微博帐号的`uid`和`access_token`并进行了校验。但是如果只是通过这样类似的接口，通过`access_token`请求得到`uid`，然后就认为这个`uid`是我们的用户了，这样是不正确的。

先看一下利用方法如下：  
我在微博开发者自建了一个应用是这样的

![图片.png](https://image.3001.net/images/20210201/1612193817_601820191b4efe471d2aa.png!small)

![图片.png](https://image.3001.net/images/20210201/1612193817_60182019e1d17a976af2a.png!small)

`Oauth2.0`授权回调页是攻击者的站点。  
这里的快捷登陆链接就是：  
https://api.weibo.com/oauth2/authorize?client_id=2xxx&response_type=code&redirect_uri=https%3A%2F%2Fwww.baidu.com%2f&state=30  
登陆之后将会带着code进入百度（实际中是进入攻击者站点）：  
![图片.png](https://image.3001.net/images/20210201/1612193818_6018201aa876e11cbe801.png!small)通过官方手册，`code`是这样使用的：  
![图片.png](https://image.3001.net/images/20210201/1612193820_6018201c9f196fadab858.png!small)此时攻击者获得了用户的`access_token`和`uid`  
回到第一种利用方法：  
![图片.png](https://image.3001.net/images/20210201/1612193829_601820254791ae8e0edf6.png!small)

这一次将`access_token`和`uid`同时进行替换就可以登陆别人绑定的帐号。  
原因在于没有通过这一次将`access_token`和`uid`同时进行替换就可以登陆别人绑定的帐号。  
原因在于没有通过<https://open.weibo.com/wiki/Oauth2/get_token_info>  
获取`appkey`来校验这个`access_token`是不是真是由你的应用产生的。

> 1.访问攻击者的微博快捷登陆  
> 2.攻击者获取`code`->获取`access_token`和`uid`  
> 3.其他的应用帐号被劫持

## 修复方法：

通过<https://open.weibo.com/wiki/Oauth2/get_token_info>  
获取`appkey`来校验这个`access_token`是不是真是由你的应用产生的。

![图片.png](https://image.3001.net/images/20210201/1612193833_601820295b21eeede15c1.png!small)

## 最后

在当今，不管国内国外，几乎每一个站点都存在第三方快捷登录，国内主流的可能就是QQ/微博/微信，当然还是有其他的快捷登录方式，希望本文能够抛砖引玉，让各位同学能够发现更多种的快捷登录方式漏洞。

