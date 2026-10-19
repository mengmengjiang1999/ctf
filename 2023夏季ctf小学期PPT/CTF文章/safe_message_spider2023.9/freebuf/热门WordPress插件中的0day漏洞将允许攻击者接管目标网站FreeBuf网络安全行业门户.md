## 前言

 **研究人员表示，网络犯罪分子目前正在利用一个热门WordPress插件中的安全漏洞来在目标站点中植入后门，并拿到网站的完整控制权。**

![a.png](https://image.3001.net/images/20181124/1543038439_5bf8e5e728b3c.png!small)

这个漏洞存在于WordPress插件-[WP GDPR Compliance](https://wordpress.org/plugins/wp-gdpr-compliance/)之中，而WP GDPR
Compliance这款插件的主要作用是帮助网站管理员让自己的网站满足GDPR条例（《通用数据保护条例》）。目前，这款插件是WordPress插件库中最热门的GDPR主题插件之一，而且已经有100000+的活跃安装量了。

大概在三周之前，攻击者似乎在这个插件中寻找到了一个安全漏洞，并开始利用这个漏洞来在目标网站中植入后门脚本。关于被黑网站的[初始数据报告](https://wordpress.org/support/topic/plugin-installed-itself-and-activated-itself-on-my-site/)目前已经提交到了另一款插件的论坛上，但是搞了半天这个插件原来是攻击者在第二阶段所要用到的攻击Payload…

WordPress安全团队在对整个事件进行了分析调查之后发现，攻击的源头就是WP GDPR
Compliance，而且所有被入侵的网站都安装并使用了这款插件。

WordPress团队也的确在这个插件的代码中发现了几个安全问题，并且认为这些安全问题就是导致那些报告网站被攻击的主要原因。目前，WordPress团队已经将相关插件从WordPress官方插件库中删除了。

不过，这款插件又在两天前重新上线了，因为该插件的开发者发布了[1.4.3版本](https://www.wpgdprc.com/wp-gdpr-compliance-1-4-3-security-release/)，并修复了之前存在的安全问题。

## 攻击仍在进行时…

[Defiant公司](https://www.wordfence.com/blog/2018/11/trends-following-vulnerability-in-wp-gdpr-compliance-plugin/)（Wordfence防火墙插件的开发商）的安全专家表示，虽然这个漏洞在新版本中已经修复了，但是攻击者目前仍然能够攻击那些运行了1.4.2版本以及更老版本WP
GDPR Compliance的网站。该公司的分析专家说到，他们目前仍然在监控和检测利用相关WP GDPR Compliance漏洞的网络攻击行为。

在这个漏洞的帮助下，攻击者可以调用插件中的内部函数，然后修改插件伸直整个WordPress网站系统的配置。

Wordfence团队还表示，他们目前已经检测到了两种不同类型的利用该漏洞来发动的网络攻击。第一种攻击场景如下：

> 1、 攻击者利用漏洞入侵网站的用户注册系统；
>
> 2、 攻击者利用漏洞将新账号的默认规则修改为“管理员”；
>
> 3、 攻击者注册一个新账号，这个账号在注册成功后就会自动变成管理员帐号，新账号默认用户名为“t2trollherten”；
>
> 4、 然后把默认用户角色修改为“订阅者”；
>
> 5、 攻击者禁用公共用户注册功能；
>
> 6、 攻击者登录新创建的“管理员”帐号；
>
> 7、 然后开始在网站系统中安装后门，后门文件为wp-cache.php；

这个后门脚本包含一个文件管理器、终端模拟器和一个PHP eval()函数运行工具，Wordfence表示，这种类型的脚本将允许攻击者部署任意Payload：

![部署任意Payload](https://image.3001.net/images/20181124/1543038452_5bf8e5f490ce0.png!small)

但是，安全研究人员还检测到了第二种类型的攻击，这种攻击技术不需要创建新的管理员帐号，因为账号创建操作很可能会被目标网站的管理员发现。

毫无疑问，第二种攻击方式的隐蔽性更强，它会使用WP GDPR Compliance漏洞来在WP-Cron中新增一个新任务，而WP-Cron则是WordPress内置的计划任务工具。

攻击者所创建的cron任务会下载并安装一个大小为2MB的Autocode插件，接下来，攻击者会利用这个插件来向目标站点上传另一个后门脚本，即wp-cache.php，但是它又跟我们之前介绍的wp-cache.php不同。

虽然第二种攻击场景的隐蔽性更强，但实际上，这个0
day漏洞之所以被我们发现，就是因为攻击者使用了第二种方法来实施攻击，很讽刺吧？因为在某些网站上，攻击者完成漏洞利用和攻击行为之后，无法删除他们所上传的Autocode插件。网站管理员发现了这个莫名其妙出现的插件之后，必定会有所警觉。一般来说在这种事情发生之后，网站管理员首先会去WordPress论坛上寻求帮助，这也导致了后续针对WP
GDPR Compliance插件的安全调查。

## 攻击者正在囤积被黑网站

根据Wordfence团队的说法，攻击者到目前为止都没有对受感染的网站执行任何的攻击操作。攻击者现在只是在大量囤积这些受感染的站点，而且Wordfence也没有看到攻击者尝试通过植入的后门来部署任何的恶意软件。

## 总结

如果你的网站安装并使用了WP GDPR Compliance插件的话，你现在还有时间来更新或者移除这款插件，然后在移除插件之后检查并清理任何后门。

 ***参考来源：[zdnet](https://www.zdnet.com/article/zero-day-in-popular-wordpress-plugin-exploited-in-the-wild-to-take-over-sites/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

