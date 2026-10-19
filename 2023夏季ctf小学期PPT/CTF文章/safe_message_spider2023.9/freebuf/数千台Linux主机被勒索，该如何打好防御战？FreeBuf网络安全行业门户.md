**近日，国外安全媒体先后报道了一款名为Lilocked的Linux勒索病毒，该勒索病毒目前为止已感染了6000+台Linux主机，加密后缀为.lilocked。俄国的安全研究员认为，Lilocked很有可能是通过Exim邮件转发软件的最新远程执行漏洞CVE-2019-15846进行传播的。**

![](https://image.3001.net/images/20190916/1568633784_5d7f73b86995f.png!small)

其实，这个勒索病毒从今年7月中旬就已经出现了，只不过当时“表现平平”，并没有引起大众的关注，但是在近期感染量突增，有爆发感染的趋势。

![](https://image.3001.net/images/20190916/1568633789_5d7f73bd51813.png!small)

使用Google搜索"#README.lilocked"关键字，可以关联到约6340个结果，也就是说，公网上已知的Linux主机，有近6340个主机被该病毒勒索了，然而事实上被勒索的Linux主机肯定远超这个数字，因为还有很多些未联网或未被搜索引擎关联到的主机。

![](https://image.3001.net/images/20190916/1568633798_5d7f73c68f09a.png!small)

使用zoomeye侦测这些主机的端口，发现大部分都开启邮件的服务，以此推断俄罗斯研究员关于Exim漏洞的说法还是有依据的。

![](https://image.3001.net/images/20190916/1568633802_5d7f73caedd1d.png!small)

勒索Tor地址为：y7mfrrjkzql32nwcmgzwp3zxaqktqywrwvzfni4hm4sebtpw5kuhjzqd.onion，跟Sodinokibi相似，需要输入key才能跳转到相应的勒索联系界面，黑客提示想要解密文件，必须发送0.03个BTC到钱包地址1KxvqPWMVpCzjx7TevBY3XbMeFNj85Keef。

![](https://image.3001.net/images/20190916/1568633813_5d7f73d5d07cc.png!small)

那么，Linux下的勒索病毒跟Windows平台的勒索病毒有什么不同？该如何进行防御呢？其实，无论在什么平台，勒索病毒的工作原理都是相似的：

> 杀软检测 -> 特定语言国家免疫 -> 生成加密密钥 -> 遍历除系统文件路径以外的目录 -> 加密特定后缀的文件 -> 删除备份文件 -> 退出。

但Linux勒索病毒一般会比Windows勒索病毒多一个步骤，就是在开始前会利用漏洞进行提权，包括这次的Lilocked勒索病毒，也使用了未公开的漏洞将自身提升为root权限后再进行加密操作。下面就使用开源的Linux勒索病毒GonnaCry演示下，有无root权限情况下的运行情况。GonnaCry的功能比较简单，使用AES算法加密文件内容，然后修改主机桌面。

![](https://image.3001.net/images/20190916/1568633824_5d7f73e0821c2.png!small)

在普通用户权限下，GonnaCry几乎无法完成加密操作，只能加密几个临时文件。

![](https://image.3001.net/images/20190916/1568633833_5d7f73e99cf42.png!small)

而当以root权限运行时，GonnaCry成功加密，主目录下的doc文件都被加密成了GNNCRY后缀的文件。可见，Linux勒索病毒在有无root权限下运行，结果是截然不同的。

![](https://image.3001.net/images/20190916/1568633840_5d7f73f081d84.png!small)

由于Linux操作系统的权限管控是很严格的，除非是在同一个用户组里的用户，不然是无法操作其他用户的文件的，比如：若一个勒索病毒是通过redis漏洞进来的，那么它的所拥有者就是redis账号（假设使用redis用户启动的应用），它将无法读写root、user1、user2等其他用户的文件，这就是为什么Linux恶意软件都想方设法进行提权的原因。

MSF上面有许多Linux提权漏洞的EXP，勒索病毒只需集成相关的核心代码即可实现提权，提升到root权限之后，就能够读写操作任意文件了。当然，若你的root密码是弱密码，勒索病毒也不用通过漏洞提权那么麻烦了，直接爆破密码以root权限运行。

![](https://image.3001.net/images/20190916/1568633846_5d7f73f6be140.png!small)

其实对于上述情况，Linux系统还是做出了相应的对策的，那就是SELinux和AppArmor。这两者的主要作用就是采用MAC的策略，最大限度地减小系统中服务进程可访问的资源（最小权限原则），即使是root用户也无法随意操作文件。网上也有相关的使用教程，若规则编写得当的话，用来防御勒索行为还是挺有效的。

![](https://image.3001.net/images/20190916/1568633850_5d7f73fa1e5c3.png!small)

最后，总结一下Linux平台下防御勒索病毒的几点使用建议：

> 1\. 尽量不要使用root权限运行Web应用程序。
>
> 2\. 及时打上重要的补丁，防止应用程序被漏洞利用入侵。
>
> 3\. root账号增强密码复杂性，避免被爆破。
>
> 4\. 开启SELinux、AppArmor等功能保护重要文件。
>
> 5\. 部署终端安全软件进行防护。

 ***本文作者： 深信服千里目安全实验室，转载请注明来自FreeBuf.COM**  

