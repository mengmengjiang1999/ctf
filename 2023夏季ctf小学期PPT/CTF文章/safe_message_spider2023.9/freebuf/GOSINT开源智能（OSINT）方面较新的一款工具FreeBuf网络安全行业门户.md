**GOSINT是一款使用Go语言编写的开源智能信息收集工具。由于该工具刚推出不久，因此目前仍处在开发之中。我们也欢迎任何愿意为该工具做出贡献的人，加入到我们的开发之中。在某些方面，gOSINT可以说比Recon-ng更具优势。你可以在此阅读我之前[关于Recon-ng评估的帖子](https://www.prismacsi.com/en/osint-with-recon-ng/)。**

gOSINT依赖于开源OCR引擎Tesseract ，libtesseract-dev和libleptonica-dev，在使用之前必须先在机器上安装它们。另外，gOSINT同时支持Linux和Windows系统。

在Linux系统上安装它的最简单方法是使用go get命令，该系统也是黑客或渗透测试人员最喜欢使用的操作系统。

    
    
    go get github.com/Nhoya/gOSINT/cmd/gosint

我们也可以使用以下命令克隆存储库来安装它：

    
    
    git clone https://github.com/Nhoya/gOSINT.git

然后手动安装依赖项：

    
    
    curl https://raw.githubusercontent.com/golang/dep/master/install.sh | sh

（无需使用Golang）

Recon-ng优于gOSINT的一点是它的安装更为简单，因为它的大部分依赖性通常已在大多数Linux版本中可用（并且已被集成在Kali Linux上）。

安装完成后，我们就可以使用迄今为止已在gOSINT中集成和实现的几个模块。首先，我们导航到可以运行gOSINT的目录。

    
    
    root@prismacsi:~/go/src/github.com/Nhoya/gOSINT/cmd/gosint#

然后键入：

    
    
    ./gosint –help

![1metu.png](https://image.3001.net/images/20181201/1543626180_5c01ddc4646f4.png!small)

查看该工具的帮助信息。

可以看到到目前为止，gOSINT已经实现了以下模块：

> 1.Git支持使用github API或普通克隆和搜索进行邮件检索
>
> 2.在PGP服务器中搜索电子邮件地址，别名和KeyID
>
> 3.从hadibeenpawned.com搜索泄露的电子邮件地址
>
> 4.检索Telegram公共组消息历史
>
> 5.发送查询到shodan.io
>
> 6.检索电话号码所有者名称
>
> 7.使用crt.sh枚举子域

有些模块的功能尚未完善，如前所述gOSINT仍在开发中。让我们来看看已经实现的少数几个模块。

## PGP MODULE

此模块将会为我们在Pretty Good Privacy（PGP）服务器中搜索电子邮件地址，别名和KeyID。

此模块使用命令格式如下：

    
    
    ./gosint pgp <domain_name>

以下结果来自两个示例域名。

![2PGPgosint1.png](https://image.3001.net/images/20181201/1543626211_5c01dde3970e6.png!small)![3PGPgosint2.png](https://image.3001.net/images/20181201/1543626211_5c01dde3f00ba.png!small)

现在，让我们来比较下gOSINT和recon-ng的结果（同样是那两个域名）。

![4PGPrecon2.png](https://image.3001.net/images/20181201/1543626230_5c01ddf612800.png!small)

不难看出，虽然gOSINT的界面没有recon-ng的好，但相较于recon-ng它能为我们提供更加详细的结果。当然，这并不意味着recon-ng不能完成任务。相反，recon-ng直接将检索到的数据保存在其内部数据库中，这更便于用户日后的侦察利用。

## PNI MODULE

此模块将会为我们在sync.me服务器中查找电话号码并返回所有者的名称。但目前该模块还存在一些待解决的问题，例如验证码限制还未解决。但我相信在后续的开发中，这一问题将会得到解决。以下截图显示了可以从当前状态模块所获取的结果。

![5gosintPNI.png](https://image.3001.net/images/20181201/1543626255_5c01de0f1224d.png!small)

Recon-ng中没有执行该功能的模块，但有一个模块能够返回与给定主机或域名关联的电子邮件地址和名称列表。如下截图所示：

![6whoisRECON@.png](https://image.3001.net/images/20181201/1543626274_5c01de22a52f1.png!small)

##
![7whoisRECON.png](https://image.3001.net/images/20181201/1543626295_5c01de37d08a3.png!small)

## PWD MODULE

该模块会为我们从hasibeenpawned.com服务上检索，是否存在泄露的电子邮件地址。这可能是黑客攻击目标的潜在来源。因此，渗透测试人员会建议显示电子邮件地址公司的员工，采取更好的主动防护措施来保护其电子邮件帐户。

使用命令格式如下：

    
    
    ./gosint pwd <email_address>

示例：

![8PWDgosint.png](https://image.3001.net/images/20181201/1543626327_5c01de57c5485.png!small)

## SHODAN MODULE

这是本文为大家介绍的最后一个模块。根据其维基百科的定义，Shodan是一个搜索引擎，允许用户通过自定义过滤器查找连接到互联网的特定类型计算机。

关于gOSINT的Shodan实现仍然是基本的，但它执行预期的功能包括发现蜜罐，这些蜜罐通常用于捕获攻击行为并对其进行分析，从而进一步加强企业自身的安全防护能力。

    
    
    ./gosint shodan 23.22.39.120 honeypot

返回结果如下：

![9shodanGOSINT.png](https://image.3001.net/images/20181201/1543626350_5c01de6e139cc.png!small)

shodan.io允许在应用各种过滤器时执行多种不同的搜索，但迄今为止在gOSINT的shodan模块中实现的并不多。随着越来越多的开发人员参与到该项目中，相信在未来该模块会实现更多的功能。相比起recon-ng，gOSINT仍有很长的路要走。以下是recon-ng中shodan模块的执行结果。可以看到，该模块为我们返回了与指定域名关联的多个主机名。

![10Screenshot-from-2018-10-30-10-36-02.png](https://image.3001.net/images/20181201/1543626372_5c01de84960c2.png!small)![11Screenshot-from-2018-10-30-10-37-01.png](https://image.3001.net/images/20181201/1543626372_5c01de84ba44d.png!small)

这也再次证明了recon-ng在这方面的优越性，这对于任何希望在OSINT侦察中节省时间的渗透测试人员或黑客来说至关重要。这就是为什么大多黑客在入侵或试图渗透某些计算机系统/基础设施之前，首先选择使用recon-ng工具的原因。但近些年来recon-ng在改进开发方面开始陷入自己的瓶颈期，因此在这个领域也迫切需要新鲜血液的注入。一旦所有模块都正常启动并运行，gOSINT就有可能成为一个非常强大的侦察工具。相信时间会证明这一切！

 ***参考来源：[prismacsi](https://www.prismacsi.com/en/osint-with-gosint/)，FB小编secist编译，转载请注明来自FreeBuf.COM**

