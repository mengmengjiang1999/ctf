**今天给大家介绍的这款功能强大的开源工具名叫Scavenger，在该工具的帮助下，广大安全研究人员可以在不同的Paste站点上使用爬虫（Bot）来搜索用户泄露的凭证信息。**

##
![Scavenger：可在不同Paste站点爬取用户泄露凭证的强大工具](https://image.3001.net/images/20190530/1559225262_5cefe3aed160b.png!small)
Scavenger

自动化Snyk基于下列扫描结果：【[已知漏洞](https://snyk.io/)】

处于活动状态的Bot：【[Bot in action](https://twitter.com/leak_scavenger)】

## 工具介绍

平时，本人喜欢自己写一些Bot代码来作为自己的OSINT项目工具，在这个项目中，我整合了大量代码，并能够从不同的Paste站点中收集用户泄露的敏感信息。

支持搜索的内容：

> 1、 用户凭证
>
> 2、 RSA私钥
>
> 3、 Wordpress配置文件
>
> 4、 MySQL连接字符串
>
> 5、 Onion链接
>
> 6、 Onion内网文件链接（PDF、DOC、DOCX、XLS、XLSX）

这里需要提醒大家一下：

> 1、
> Scavenger所使用的bot目前并不是非常完美，因为该项目的代码编写得比较仓促，因为“时间紧任务重”，而且很多编码细节也没能考虑周全，但之后我会慢慢修改这些东西。
>
> 2、 项目代码目前还没编写完成，之后还会添加更多的功能，比如说凭证数据库，以及很多整合的第三方库。
>
> 3、 如果你想使用本项目的代码，大家可以随意使用，而且大家也可以根据自己的需要来自定义开发。
>
> 4、 本工具仍存在一定假阳性，也就是有些凭证可能会无法正常获取，欢迎大家贡献自己的代码噢！

## 运行机制

### Bot能够以下列两种主要模式运行：

> 1、 API模式
>
> 2、 爬取模式（使用TOR）  
>

我强烈建议大家使用API模式，因为这种方法非常适用于针对Pastebin.com来爬取Paste内容，而且准确率非常高。我们要做的就是申请一个Pastebin.com专业版(Pro)账号，然后在网站白名单列表中添加你的公共IP。

运行下列命令即可以API模式运行Scavenger：

    
    
    python run.py -0

注意：我们还有NAT模式可以使用，这种模式就不需要设置IP地址白名单了。

如果你想以爬取模式运行Bot的话，可以使用下列命令：

    
    
    python run.py -1

注意：你需要在系统上安装TOR服务并监听端口9050。除此之外，你还需要在/etc/tor/torrc文件中添加下列参数：

    
    
    MaxCircuitDirtiness 30

## 工具使用

如果你想了解更多工具使用信息，你可以使用-h/--help参数来运行Scavenger：

    
    
    python run.py –h

 **输出结果如下：**

![22222222.png](https://image.3001.net/images/20190530/1559225313_5cefe3e11d60f.png!small)  

目前，我只实现了Pastebin.com模块，现在正在开发针对Paste.org的模块，之后会及时更新脚本内容。

使用下列命令即可开启Pastebin.com模块：

    
    
    python P_bot.py

爬取到的Paste会存储在data/raw_pastes中，直到数量超过48000为止。超过之后，工具会对爬取到的数据进行过滤和压缩，并移植对应目录中。所有包含了用户凭证的的Paste数据都会存储在data/files_with_passwords中。数据格式如下：

    
    
    USERNAME:PASSWORD

当然了，我们还可以使用Scavenger的getProxyLogs.py文件来搜索代理日志（包含了用户名和密码对的URL）：

    
    
    python getProxyLogs.py data/raw_pastes

如果你想搜索特定字符串相关的元数据，你可以使用searchRaw.py（速度较慢）：

    
    
    python searchRaw.py SEARCHSTRING

使用下列命令可以查看Bot的统计数据：

    
    
    python status.py

findSensitiveData.py脚本还可以搜索类似信用卡数据、RSA密钥或mysqli_connect字符串，脚本使用的是grep命令，因此对于大型文件的爬取速度会相对较慢。如果你想分析大量Paste的话，我建议你使用ELK-Stack。

    
    
    python findSensitiveData.py data/raw_pastes

Scavenger还提供了两个脚本：stalk_user.py和stalk_user_wrapper.py，来帮助用户监控特定的Twitter用户。此时，该用户所有发布的推文都会被我们存储下来，而且每一个下载的URL也会被我存储下来。

    
    
    python stalk_user_wrapper.py

## 项目地址

Scavenger：【[GitHub传送门](https://github.com/rndinfosecguy/Scavenger)】

### 参考资料

1、 <https://jakecreps.com/2019/05/08/osint-collection-tools-for-pastebin/>

2、 <https://jakecreps.com/2019/01/08/scavenger/>  

***
参考来源：[Scavenger](https://github.com/rndinfosecguy/Scavenger)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

