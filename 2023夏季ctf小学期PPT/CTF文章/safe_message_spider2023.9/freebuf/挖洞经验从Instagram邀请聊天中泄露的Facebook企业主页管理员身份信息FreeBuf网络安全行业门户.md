![](https://image.3001.net/images/20200813/1597328823.png!small)

**在[前一篇博客](https://link.medium.com/HlmBzz4E45)中，作者发现了Facebook企业主页管理员身份泄露和未授权添加的漏洞，收获了$1000的奖励，而该篇Writeup则讲述作者在Instagram与Facebook之间进行消息发送的过程中，发现Facebook企业主页管理员（Page
Admin）账户信息泄露的漏洞，漏洞收获$5500。以下是作者的分享，我们一起来看看。**

> Facebook企业主页管理员：Facebook企业页面中用来对页面和其他管理人员进行维护的用户身份。

![](https://image.3001.net/images/20200813/1597326829.png!small)

## 漏洞发现过程

最近，我一直在做 Instagram 和 Facebook集成功能的安全测试，如果你对Instagram 或
Facebook企业主页集成功能有了解的话，你也就明白了为何可以从Instagram账户链接到
Facebook企业主页的原因了，而且之后，还可以在Facebook企业主页中向Instagram用户发送或接收消息。在Facebook企业主页中，能以下聊天窗口方式向有Instagram链接的用户发送消息：

![](https://image.3001.net/images/20200813/1597326858.png!small)

当我在测试上述Facebook企业页面的消息功能时，我无法从其中发现任何admin
id，但当我去测试Instagram的响应时，却从其中的WebSocket响应消息中发现了admin
id。也就是说，当从Facebook企业主页消息框向Instagram用户发送消息时，我从其WebSocket消息中发现了Facebook企业主页管理员ID。

来看看具体的漏洞发现过程。首先，我可以以管理员身份从Facebook企业主页中向其中设置有Instagram链接的Instagram用户evilboyajay发送一条消息：

![](https://image.3001.net/images/20200813/1597328491.png!small)之后，当我从Instagram用户evilboyajay收件箱中查看Facebook企业主页管理员发送过来的消息时，我发现还可以从其中邀请Facebook企业主页管理员账户加入聊天：

![](https://image.3001.net/images/20200813/1597328513.png!small)接下来，当我从Instagram用户evilboyajay收件箱中邀请Facebook企业主页管理员账户加入聊天后，Facebook企业主页管理员账户的ID等敏感信息竟然泄露在Instagram的websocket响应消息中：

![](https://image.3001.net/images/20200813/1597328548.png!small)此外，从上述Instagram的websocket响应消息中，可以轻易识别出泄露的Facebook企业主页管理员账户，由于是Instagram
用户邀请的聊天，所以还可在下述GET请求中，通过请求Instagram 用户ID的形式获得其邀请聊天的Facebook企业主页管理员账户：

> https://i.instagram.com/api/v1/users/{id}/info/

![](https://image.3001.net/images/20200813/1597328579.png!small)

## 漏洞上报和处理进程

> 2020.5.2 漏洞上报
>
> 2020.6.8 漏洞分类
>
> 2020.6.9 漏洞修复
>
> 2020.6.18 漏洞奖励$3500

![](https://image.3001.net/images/20200813/1597328711.png!small)

## 后续

之后，Facebook告知我漏洞已经修复，但是，在我的复测过程中，我发现仍然可以从Instagram接口/api/v1/users/{id}/info/的GET请求中，获取Instagram邀请聊天的Facebook企业主页管理员用户信息，再次上报后，Facebook也确认漏洞有效：

![](https://image.3001.net/images/20200813/1597328722.png!small)几天后，Facebook告诉我漏洞已经完全修复，我再次获得$2000的奖励。最终，从该漏洞上，我总计获得了$5500的奖励。

![](https://image.3001.net/images/20200813/1597328754.png!small)

文章参考

> <https://medium.com/@tnirmalz/facebook-bugbounty-disclosing-page-> members-1178595cc520>
>
> <https://seekurity.com/blog/2018/02/25/admin/general/the-2-5mins-> or-2-5k-hawk-eye-bug-a-facebook-pages-admins-disclosure-vulnerability>

**参考来源**

> [medium](https://medium.com/nassec-cybersecurity-writeups/how-i-was-able-to-> find-page-personal-account-disclosure-on-instagram-d9607de4883f)

