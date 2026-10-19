![1.jpg](https://image.3001.net/images/20200203/1580736669_5e38209d191aa.jpg!small)

**Socialscan是一款社交账号搜索工具，它可以帮助用户检测在线平台上已注册的邮件地址以及用户名，并且准确率为100%。用户只需要提供一个邮件地址或者用户名，Socialscan可以告诉你这个邮件或用户名在当前的在线平台上是否可用。**

### Socialscan跟其他类似工具（例如knowem.com、Namechk和Sherlock）的不同之处在于：

> 1、100%准确率：Socialscan的查询方法消除了目前社区中类似工具经常出现的误报和漏报，确保查询结果始终准确。
>
>
> 2、查询速度：Socialscan使用了asyncio和aiohttp来同时执行所有查询，即使批量查询数百个用户名和电子邮件地址，Socialscan也能够快速提供准确的搜索结果。在我们的测试设备上，Socialscan在4秒内可以执行100次查询。
>
> 3、Python库/命令行：Socialscan可以通过命令行工具来执行，或者以Python库的形式在其他代码中使用。
>
> 4、电子邮件支持：Socialscan支持查询电子邮件地址和用户名。

## Socialscan支持的平台

下面给出的是Socialscan当前支持的查询平台：

![11.png](https://image.3001.net/images/20200203/1580736702_5e3820be06ba8.png!small)

## 工具背景

社区中类似的用户名查询工具通过请求目标用户名的配置页面来检查用户名的可用性，并根据请求页上的HTTP状态码或错误文本等信息来判断目标用户名是否存在。这种方法其实并不可靠，并且在以下情况失效：

> 1、保留关键字：大多数平台都有一组不允许用户在用户名中使用的关键词；
>
> 2、删除/禁用账户：删除/禁用帐户用户名往往是不可用的，即使配置文件页可能不存在；

因此，这些工具往往会出现误报和漏报。这种检查方法还依赖于具有基于web的配置文件页面的平台，并且不能扩展到电子邮件地址。

Socialscan的目标是通过直接查询平台的注册服务器，检索适当的CSRF令牌、头和cookie来填补这些空白。

## 工具安装

### 使用pip安装：

    
    
    > pip install socialscan

### 通过源码安装：

    
    
    > git clone <https://github.com/iojw/socialscan.git>  
    
    > cd socialscan  
    
    > pip install .

## 工具使用

    
    
    usage: socialscan [list of usernames/email addresses to check]
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      --platforms [platform [platform ...]], -p [platform [platform ...]]
    
                            list of platforms to query (default: all platforms)
    
      --view-by {platform,query}
    
                            view results sorted by platform or by query (default:
    
                            query)
    
      --available-only, -a  only print usernames/email addresses that are
    
                            available and not in use
    
      --cache-tokens, -c    cache tokens for platforms requiring more than one
    
                            HTTP request (Snapchat, GitHub, Instagram. Lastfm &
    
                            Tumblr), reducing total number of requests sent
    
      --input input.txt, -i input.txt
    
                            file containg list of queries to execute
    
      --proxy-list proxy_list.txt
    
                            file containing list of HTTP proxy servers to execute
    
                            queries with
    
      --verbose, -v         show query responses as they are received
    
      --version             show program's version number and exit

## 作为Python库使用

Socialscan还可以作为Python库的形式导入到已有代码之中。

Socialscan
v1.0.0引入了异步方法execute_queries，以及对应的同步封装器sync_execute_queries来接收查询列表、可选平台列表以及代理。所有的查询方法都会按相同顺序返回一个结果列表：

    
    
    from socialscan.util import Platforms, sync_execute_queries
    
     
    
    queries = ["username1", "email2@gmail.com", "mail42@me.com"]
    
    platforms = [Platforms.GITHUB, Platforms.LASTFM]
    
    results = sync_execute_queries(queries, platforms)
    
    for result in results:
    
    print(f"{result.query} on {result.platform}: {result.message} (Success: {result.success}, Valid: {result.valid}, Available: {result.available})")

输出结果如下：

    
    
    username1 on GitHub: Username is already taken (Success: True, Valid: True, Available: False)
    
    username1 on Lastfm: Sorry, this username isn't available. (Success: True, Valid: True, Available: False)
    
    email2@gmail.com on GitHub: Available (Success: True, Valid: True, Available: True)
    
    email2@gmail.com on Lastfm: Sorry, that email address is already registered to another account. (Success: True, Valid: True, Available: False)
    
    mail42@me.com on GitHub: Available (Success: True, Valid: True, Available: True)
    
    mail42@me.com on Lastfm: Looking good! (Success: True, Valid: True, Available: True)

## 文本文件输入

对于批量查询，用户可以使用“--input”参数来传入一个.txt文件，用户可以在该文件中写入需要查询的用户名或电子邮件，每一条记录占一行：

    
    
    username1
    
    email2@mail.com
    
    username3

## 工具运行截图

![2.gif](https://image.3001.net/images/20200203/1580736789_5e38211548de3.gif!small)![3.gif](https://image.3001.net/images/20200203/1580736789_5e3821154a63a.gif!small)

### 许可证协议

Socialscan的开发与发布遵循MPL v2.0开源许可证协议。

## 项目地址

Socialscan：【[ _GitHub传送门_](https://github.com/iojw/socialscan)】

 ***参考来源：[
_iojw_](https://github.com/iojw/socialscan)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

