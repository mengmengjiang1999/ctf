##  介绍

**我们知道，如果攻击者进入域(内网)环境中，攻击影响不敢想象，所以最重要的是快速检测它们。防病毒和EDR解决方案在检测和阻止攻击者方面已经走了很长一段路，但是牛批的黑客很可能通过各种奇技淫巧技术来规避这些控制措施。**

防守方通常会忽略的一种方法——使用蜜罐帐户。蜜罐帐户是一种策略性地定位在网络中的帐户，在这种情况下使用蜜罐帐户的主要目的是检测Kerberoasting（在[@
myexploit2600](https://twitter.com/myexploit2600)的文章），根据我们在行业中的经验，这是在攻击之后使用的最常见的攻击媒介之一。在网络内获得立足点。

使用蜜罐帐户的优点之一是没有额外的软件成本。许多蓝队解决方案要花费大量资金，并且需要大量资源来实施和管理。但是当使用蜜罐账户时，由于绝对不应请求或使用该账户，因此产生误报的可能性也为零。

##  设置蜜罐域管理员帐户

要设置蜜罐域管理员帐户，我们首先需要在Active Directory中创建一个。应该使用与现有“域管理员”帐户类似的命名约定来使其看起来合法。
**应该使用128个随机生成的字符的密码，以防止攻击者在获得哈希后能够破解哈希。**

![](https://image.3001.net/images/20200407/1586244076_5e8c29ec0f9dd.png!small)

分配权限后，我们需要选择合适的服务主体名称（SPN）。这是攻击者在进行Kerberoasting攻击时将看到的内容，因此重要的是使其看起来像合法的东西，例如惰性sys管理员已将其放入Domain
Admins组中的MSSQL服务帐户。使其具有唯一性也很重要，因此请检查您现有的SPN并再次检查“ adminCount”属性是否设置为1。

![](https://image.3001.net/images/20200407/1586244076_5e8c29ec10d00.png!small)

启用Audit Kerberos Service Ticket Operations日志记录,捕获事件4769，该事件在请求Kerberos服务票证时发生。

如果您拥有SIEM或使用SOC管理的服务，则应该已经捕获了这些事件，并且可以创建自定义警报，但是对于此博客文章，我们将说明如何在没有其他服务或产品的情况下识别此活动。

![](https://image.3001.net/images/20200407/1586244076_5e8c29ec25a5a.png!small)

创建一个自定义事件视图，以识别何时为我们的蜜罐用户帐户请求Kerberos服务票证。这可以通过使用以下包含我们新创建的帐户的XPath查询来完成。如果我们不执行此步骤，则在大型AD环境中，将有成千上万的4769事件日志，并且很难识别恶意活动。

    
    
    <QueryList>
    <Query Id="0" Path="Security">
    <Select Path="Security">*[System[(Level=4 or Level=0) and (EventID=4769)]] and
    * [EventData[Data[@Name='ServiceName']='tkerb']]</Select>
    </Query>
    </QueryList>

![](https://image.3001.net/images/20200407/1586244076_5e8c29eca62d2.png!small)

创建自定义事件视图后，我们将进行Kerberoasting攻击以测试其是否有效。

![](https://image.3001.net/images/20200407/1586244077_5e8c29ed09a30.png!small)

该事件已在我们的自定义事件视图中成功捕获，我们需要创建一种方法来警告管理员网络中可能存在攻击者。警报包含进行了Kerberoasting攻击的客户端计算机的IP地址。这可能是受感染的用户，或者是攻击者使用他们自己的设备物理连接到网络。

![](https://image.3001.net/images/20200407/1586244077_5e8c29ed0bd03.png!small)

现在，我们可以创建一个特定的事件查看器任务，该任务将在事件出现在自定义事件视图中时触发。该任务需要设置为“无论用户是否登录都运行”。

![](https://image.3001.net/images/20200407/1586244077_5e8c29ed3dcca.png!small)

设置任务后，请仔细检查触发器设置，以确保它在我们先前创建的事件XPath查询中触发。

![](https://image.3001.net/images/20200407/1586244077_5e8c29ed7120d.png!small)

在最后一步中，我们将操作设置为启动powershell.exe，但是您应该将其更改为启动PowerShell脚本，该脚本通过电子邮件向管理员发送电子邮件，说明正在进行中的恶意活动也将禁用该帐户。

![](https://image.3001.net/images/20200407/1586244077_5e8c29ede4e1b.png!small)

为了测试检测，我们执行了Kerberoasting攻击，并且可以看到powershell.exe启动。

![](https://image.3001.net/images/20200407/1586244078_5e8c29ee04224.png!small)

如果一切都按预期进行，那么您现在就可以找到一种有效的方法来识别攻击者，以在您的环境中进行Kerberoasting攻击。定期模拟此攻击向量和响应非常重要，以确保相关团队知道如何做出反应。

 ***参考来源:[pentestpartners](https://www.pentestpartners.com/security-blog/honeyroasting-how-to-detect-kerberoast-breaches-with-honeypots/)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**

  

