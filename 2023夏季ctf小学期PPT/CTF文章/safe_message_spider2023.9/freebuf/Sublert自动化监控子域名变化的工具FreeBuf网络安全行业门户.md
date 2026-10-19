**漏洞赏金（Bug
bounty）行业在近年来可以说是发展迅速，几乎每天都有一些新的赏金项目推出，这也带来了白帽黑客间激烈的竞争。这是一种货币化的竞赛，围绕着第一个报告漏洞的竞争，先到先得。因此，想要占得先机并保持领先，学习和扩展你的技能将是一个必不可少的过程。另外，测试方法的改进也是至关重要的，例如优化你的侦察工作，**
**这肯定会给你带来巨大的帮助。**

在这方面，我已构建了一个安全和侦察工具，我自己已经用了很长一段时间。这款工具可以自动化的监控特定组织的子域，并在找到新内容时向你发送通知。

该工具由[OWASP Seasides](http://owaspseasides.com/)发布于[NullCon
2019](http://nullcon.net/)期间。

##  **Sublert 简介**

>
> 证书透明度（CT）是一种新的互联网标准，使TLS/SSL证书颁发过程更加透明和公开。其旨在允许域所有者了解公共证书颁发机构（CA）颁发给域的TLS/SSL证书。

[Sublert](https://github.com/yassineaboukir/sublert)是一个由Python编写的安全和侦察工具，其主要用途是监控特定组织部署的新子域并颁发TLS/SSL证书。该工具支持定时任务，你可以设置固定的时间，日期或间隔（理想情况是每天）定期运行它。新的已识别子域将通过通知推送，发送到Slack工作区。此外，该工具会通过DNS解析来确定工作子域。

Sublert主要是为漏洞赏金猎人而定制的，以加强他们的侦察能力，并通过获取的新子域来击败竞争对手。但Sublert也可在内部使用，用以监控工程团队部署的各种子域。

## Sublert 的优势

虽然市面上已有开源的监控工具，如[Cert Spotter](http://certspotter.com/) 或 [Facebook monitoring
tool](https://developers.facebook.com/tools/ct/)，但这些工具主要是为组织监控网络钓鱼活动而构建的，因此每当有以欺诈手段或错误方式向域名颁发证书时都会收到通知。这意味着如果你正在监控拥有大量资产的组织，你将被不相关的结果（包括网络钓鱼域名、无意义的超范围资产以及每天数百封电子邮件）所困扰。

## 设置

 **环境要求**

> 在Unix上运行的VPS。（我用的是 [digitalOcean](https://digitalocean.com/)）
>
> Python 2.x or 3.x.
>
> Free Slack workplace

首先，我们从Github将工具克隆到你的Web服务器：

    
    
    $ git clone https://github.com/yassineaboukir/sublert.git && cd sublert

现在，我们使用以下命令安装所需的模块：

Python 2：

    
    
    $ sudo pip install -r requirements.txt

Python 3：

    
    
    $ sudo pip3 install -r requirements.txt

下一步是创建一个Slack工作区，以便将新子域发送到该工作区。打开浏览器访问<https://slack.com/>，并创建一个免费帐户即可。

然后，创建两个channel：一个用于子域，另一个用于错误记录，如下所示：

![1_qgbEA3BLA1Fug7ps1Sx6Lg.png](https://image.3001.net/images/20190316/1552698237_5c8c4b7d295a5.png!small)

接下来，我们需要为每个channel生成Webhook URL，以便我们可以利用Slack API。

访问<https://api.slack.com/apps>，并创建一个新应用。

浏览到Incoming Webhooks创建两个Webhook，并将每个Webhook链接到之前创建的两个channel。

![2_27FDRsv51uhmu2t8oF8NKw.png](https://image.3001.net/images/20190316/1552698255_5c8c4b8fad05f.png!small)

并将每个webhook与相应的Slack channel链接。

![3_TqEP-nDTLR--2ZTia_Ga-w.png](https://image.3001.net/images/20190316/1552698275_5c8c4ba3e60c2.png!small)

你将获取到一个如下格式的链接：

    
    
    https://hooks.slack.com/services/XXXXXXX/BF0XXXXME/XXXXXXXXXXXXX

复制两个webhook链接并编辑config.py文件：

![4_4PL5zkAqT58IPGj7GBjeoA.png](https://image.3001.net/images/20190316/1552698293_5c8c4bb51bf63.png!small)

完成以上操作后，现在我们就可以添加域来监控新子域了。我们添加PayPal看看：

    
    
    $ python sublert.py -u paypal.com

![5_Sfu555IO6P07UZ02UHD0bg.png](https://image.3001.net/images/20190316/1552698316_5c8c4bccd84ef.png!small)

如果你想监控其它域名，只需以相同的方式进行操作即可。完成目标添加后，下一步是设置定时任务，以在固定的时间定期执行Sublert。

创建一个Sublert.py可执行文件：

    
    
    $ chmod u+x sublert.py

现在，我们来添加一个新的定时任务，输入命令：

    
    
    $ Crontab -e

在Cron文件的末尾添加以下行：

    
    
    0 */12 * * * cd /root/sublert/ && /usr/bin/python /root/sublert/sublert.py -r -l >> /var/log/sublert.log 2>&1

你需要将/root/sublert/更改为Sublert的所在目录。

如果你使用的是python3，请将/usr/bin/python更改为/usr/bin/python3

> **0 */12 * * *** →
> 表示每12小时运行一次Sublert。你可以使用<https://crontab.guru/>，来自定义你所希望的固定执行时间。
>
> **-r** → 执行DNS解析。这是可选的，但建议使用。
>
> ****\- l →**** 记录错误并将其推送到Slack channel。这是可选的，但建议使用。
>
> **/var/log/sublert.log 2 >&1** → 将输出保存到/var/log/sublert.log。

你可以通过执行以下命令，来验证它是否已被正确配置并顺利运行。你应该会收到关于Slack的通知推送：

    
    
    $ python sublert.py -l -r

Sublert将每12小时执行一次，如果你监控的域名列表部署了一个新的子域名，那么你将收到有关以下内容的Slack通知：

![6_YuYGp-LRBOSX6vFAK2FEZA.png](https://image.3001.net/images/20190316/1552698355_5c8c4bf36508c.png!small)

如果Sublert被执行但未找到任何内容，你会收到未发现任何新子域的通知推送。如下：

![7_CSDgFt4kv-o6ese-U9U-Og.png](https://image.3001.net/images/20190316/1552698378_5c8c4c0a7696f.png!small)

建议你在手机上安装Slack移动版，并禁用“Do Not Disturb”模式，以便随时随地获取通知。

![8_vwCqJR91P7vFFK46u9mK_A.png](https://image.3001.net/images/20190316/1552698399_5c8c4c1f7e93f.png!small)

你可以随时添加新的监控域名或删除其中一些不必要的内容。以下是支持的各种参数：

将yahoo.com添加到受监控列表中。

    
    
    $ python sublert.py -u yahoo.com

从列表中删除yahoo.com。

    
    
    $ python sublert.py -d yahoo.com

显示当前正在监控的所有域名。

    
    
    $ python sublert.py -a

指定要使用的并发线程数（默认值为：20）。如有必要，你还可以将参数添加到定时任务中。

    
    
    $ python sublert.py -t 30

执行DNS解析。

    
    
    $ python sublert.py -r

启用基于Slack的错误记录。如有必要，你还可以将参数添加到定时任务中。

    
    
    $ python sublert.py -l

重置所有内容：将清理受控的列表并删除所有本地存储的文件。建议仅在出现问题时使用。

    
    
    $ python sublert.py -m

 **注意：** 你所监控的对象必须为开放范围内的漏洞赏金程序，以避免未经授权的监控和违反程序的安全策略。

## Sublert 的弱势

Sublert利用证书透明度，这意味着它只会监控为其颁发SSL/TLS证书的子域，无法识别在HTTP/80上运行的子域。但你可以使用其它开源工具（如Massdns，Aquatone，Sublist3r等）。

## 未来计划

> 使用关系数据库而不是文本文件进行存储。
>
> 提取尽可能多的信息，包括：标题，状态码，屏幕截图和检查潜在的子域接管。
>
> 集成Telegram用于通知推送。

## 反馈和问题

如果你有任何反馈意见，请随时在<https://github.com/yassineaboukir/sublert/issues>页面提交你的问题。也欢迎大家关注我的Twitter：[@yassineaboukir](https://twitter.com/yassineaboukir)。感谢阅读！

*参考来源：[medium](https://medium.com/@yassineaboukir/automated-monitoring-of-subdomains-for-fun-and-profit-release-of-sublert-634cfc5d7708)，FB小编secist编译，转载请注明来自FreeBuf.COM   

