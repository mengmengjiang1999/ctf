**近期，Snapchat曾发生过一次[源代码泄漏事件](https://thenextweb.com/security/2018/08/07/hacker-swipes-snapchats-source-code-publishes-it-on-github/)，在此次事件中攻击者从Snapchat网站上下载了完整的网站源码，并将其上传到了GitHub上。在过去的几年里，很多网站都存在错误配置的问题，而且这些安全问题都会被攻击者所利用。除此之外，由于Web开发的门槛相对来说比较低，所以很多经验不够丰富的开发人员很可能在Web开发的过程中泄漏一些机密数据，比如说Git代码库的密钥组件，这个密钥一旦泄露，也就意味着任何人都可以直接访问代码库中的敏感源代码、访问密钥以及密码等等。**

![1.png](https://image.3001.net/images/20181119/1542626353_5bf29c317bd26.png!small)

所以最近一段时间，我一直都在研究Git错误配置方面的问题，那么在这篇文章中，我将告诉大家我如何访问并下载的印度最大电信服务商的源代码。

## Git是什么？

Git是一种版本控制系统（VCS），它可以帮助开发人员跟踪计算机文件的修改情况，并与网络上的其他伙伴协同工作。目前，Git主要用于软件开发过程中的源代码管理，但是它还可以用来跟踪其他文件的修改情况。在Git的帮助下，开发人员可以管理源代码的版本，并通过fork和branch的形式来跟踪代码的修改。

如果一个应用程序绑定了一个错误配置的Git目录，并且公开可访问（暴露在外）的话，那么这个目录应该是下面这样的：

![2.png](https://image.3001.net/images/20181119/1542626363_5bf29c3ba87ce.png!small)

为了直接从目录中递归下载每一个文件，我们这里需要用到wget，即：

    
    
    wget –r https://www.example.com/.git

运行之后，也就是当你下载了完整的.git目录之后，你还需要利用git命令来获取git对象，这一步大家可以参考这两份手册：【[参考资料一](https://en.internetwache.org/dont-publicly-expose-git-or-how-we-downloaded-your-websites-sourcecode-an-analysis-of-alexas-1m-28-07-2015/)】【[参考资料二](https://blog.netspi.com/dumping-git-data-from-misconfigured-web-servers/)】

## 技术细节

在开始之前，如果各位不熟悉git以及git命令的话，我建议大家先阅读一下上面的参考资料。

接下来，我们一起看一看如何去实现这种源代码下载攻击。

子域名的重要性其实和主域名的是一样的，这也就是为什么很多网络侦查活动中需要进行子域名枚举的原因之一。因为一般来说，git错误配置不会只发生在主域名身上，旗下的子域名同样也会存在这样的问题。所以，为了找出所有存在git错误配置的域名、子域名或公司组织，我需要结合子域名枚举技术和.git目录下载技术才能实现。这里我给大家推荐一款优秀的开源子域名枚举工具-[Sublist3r](https://github.com/aboul3la/Sublist3r)，这款工具可以利用不同的源来枚举主域名下的子域名，并给用户提供子域名列表。除此之外，还有一款名叫[Git-dumper](https://github.com/arthaud/git-dumper)的工具，这款工具可以检查并下载公开可访问的Git目录。接下来，我通过脚本把这两个工具绑定在了一起，然后开发出了git-domian.py，它可以帮我做以下三件事情：

> 1、 git-domain.py需要一份文件作为输入参数，这个文件要包含所有的主域名（列表，按行分隔）。
>
> 2、 它会遍历每一行域名，然后找出对应的子域名，并检测相应的.git目录是否暴露在外。
>
> 3、 如果公开可访问，那么它会递归下载特定子域名对应的完整git目录，然后将其存在本地主机中。

这就是我要做的事情：收集设立了漏洞奖励计划或漏洞披露政策的公司名单，然后收集相应公司的域名列表，然后把它们传入到git-domain.py中：

![3.png](https://image.3001.net/images/20181119/1542626398_5bf29c5e7093a.png!small)![4.png](https://image.3001.net/images/20181119/1542626398_5bf29c5ec6881.png!small)

没错，这份主域名列表中也包含印度最大电信服务商的域名，而且我也成功地下载到了完整的官网源码。值得一提的是，他们的子域名也存在类似的错误配置。

![5.png](https://image.3001.net/images/20181119/1542626408_5bf29c68e08c8.png!small)![6.png](https://image.3001.net/images/20181119/1542626408_5bf29c68e6afe.png!small)

## 缓解方案

Web服务器管理员或开发者们需要确保.git目录没有被索引，并且所有的目录、子目录和全部文件都无法使用服务器权限规则来直接访问。除此之外，建议各位使用.gitignore文件来确保敏感文件能够被隐藏。缓解这种攻击的最简单的办法就是禁止访问.git目录：

    
    
    <DirectoryMatch“^/.*/\.git/”>
    
    Requireall denied
    
    </DirectoryMatch>

大家还等什么？赶紧看看自家屋顶有没有漏雨吧！

 ***参考来源：[medium](https://medium.com/@logicbomb_1/bugbounty-how-i-was-able-to-download-the-source-code-of-indias-largest-telecom-service-52cf5c5640a1)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

