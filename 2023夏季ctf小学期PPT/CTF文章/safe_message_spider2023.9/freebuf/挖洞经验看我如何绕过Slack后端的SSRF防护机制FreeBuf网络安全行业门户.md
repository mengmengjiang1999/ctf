***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**![看我如何绕过Slack后端的SSRF防护机制](https://image.3001.net/images/20190225/1551087769_5c73b8998b1e4.png!small)**
**本文分享了一个存在于Slack接口api.slack.com中的缺陷，通过利用Slack内置的斜线命令（Slash
Commands）功能，可以绕过Slack后端的SSRF防护措施，在Slack接口上形成两个服务端请求伪造漏洞（SSRF）。** **  
**

>
> Slack是一个协同办公应用平台和聊天群组，它能将工作伙伴、沟通信息和使用工具进行聚合以便高效完成工作。从世界百强大公司到小型企业，全球有数百万人在使用Slack进行内部团队沟通协调，协同办公推动业务。

## 利用斜线命令（Slash Commands）绕过Slack的SSRF防护机制

### 漏洞分析

斜线命令/commands，为Slack中某些特定命令的快捷方式，在消息字段中输入斜线加命令，点击发送，即可完成一项命令操作。如/who为列出当前群组成员，/archive为对当前群组存档，/collapse为对当前群组进行视频图片的折叠显示。默认情况下，工作群组内所有成员都可使用斜线命令，群组管理员也可对组内成员进行斜线命令的权限设定。具体用法[点此](https://get.slack.help/hc/en-us/articles/201259356-Comandos-de-barra-integrados)查看。

早前在Hackerone上，看到了Nicolas Grégoire 提交的一个“[绕过Slack SSRF
防护机制](https://hackerone.com/reports/61312)”的漏洞，报告中Nicolas Grégoire有以下分析：

> 特殊情况下，一些Slack功能组合，如“Integrations / Phabricator”，以及“Integration / Slash
> Commands”，允许用户提交可由后端服务器处理的URL链接。在这种功能场景中，Slack自身有一个黑名单来限定对如loopback,
> 10.0.0.0/8,
> 192.168.0.0/24等特殊内部资源的访问，但是，可以使用“[::]”来作为某个Slack内部主机，对Slack后端服务器发起请求。这种请求方式仅对一些支持IPv6且绑定服务端口的Slack服务器有效。

在漏洞修复中，Nicolas Grégoire给出了在外部代理（Outgoing
Proxy）和斜线命令中请求中禁用IPv6的建议。Slack也依此做了修复。

![看我如何绕过Slack后端的SSRF防护机制](https://image.3001.net/images/20190225/1551087032_5c73b5b85cb0c.jpg!small)但是，这种修复过的SSRF防护机制，还是可以被绕过的。具体测试步骤如下：

1、登录 api.slack.com，在自己的slack服务中填写你预设的斜线命令（Slash Commands）配置，其中Request
URL填写的请求网站 <http://206.189.204.187/>，为我自己控制的网站：

![看我如何绕过Slack后端的SSRF防护机制](https://image.3001.net/images/20190225/1551087059_5c73b5d3ba3d8.png!small)2、在这个我控制的206.189.204.187网站服务器中，设置一个index.php访问页面，内容为包含一个‘Location’
头的重写向，跳转到一个新的地址http://[::]:22/。根据Nicolas
Grégoire的漏洞，这个地址http://[::]:22/为Slack支持IPv6的内部主机。index.php：

![看我如何绕过Slack后端的SSRF防护机制](https://image.3001.net/images/20190225/1551087128_5c73b618b4076.png!small)

    
    
    <?php
    
     header("location: http://[::]:22/");
     ?>

3、通过api.slack.com，访问自己的slack服务
xxxx.slack.com，加入相应的斜线命令，该过程中通过请求<http://206.189.204.187/>的操作，间接执行了对Slack内部服务器22端口的请求-http://[::]:22/，结果如下：  

![看我如何绕过Slack后端的SSRF防护机制](https://image.3001.net/images/20190225/1551087224_5c73b678e5e9c.png!small)4、在<http://206.189.204.187/>的index.php访问页面加入http://[::]:25/后，由于Slack内部服务器25端口是关闭的，所以结果如下：

![看我如何绕过Slack后端的SSRF防护机制](https://image.3001.net/images/20190225/1551087265_5c73b6a1168db.png!small)也就是，如果Slack内部服务器22端口是开放的，则会有以下响应：  

> Protocol mismatch.  
> SMTP on TCP/25

如果Slack内部服务器22端口是关闭的，则会有以下响应：

> 220 squid3.tinyspeck.com ESMTP Postfix  
> 221 2.7.0 Error: I can break rules, too. Goodbye.

### 漏洞影响

攻击者利用这种SSRF漏洞，可以借由服务端的功能特性，去读取服务器内部资源信息，探测内部服务端口和版本情况。

### 漏洞上报进程

> 2018.7.13 漏洞初报
>
> 2018.7.13 漏洞分类
>
> 2019.1.23 Slack $500发放
>
> 2019.2.22 漏洞披露

## 在Slack的Event Subscriptions接口参数处绕过SSRF防护机制  

### 漏洞分析

Slack的事件接口（Event API）<https://api.slack.com/events-api>，可在各种时间发生时进行触发调用，比如消息发送的时候、channels改变的时候等。当我们在创建一些私人定制化的Slack应用时，经常会用到Slack事件接口（Event
API）。

配置Slack事件接口时，我们须在事件订阅处（Event Subscriptions）设置一个Request
URL用来作为事件的订阅地址。设置好该地址后，当事件发生时，Slack会向该地址发送HTTP
POST请求，其中会包含事件验证的"type"、"challenge"和"token"参数。

![看我如何绕过Slack后端的SSRF防护机制](https://image.3001.net/images/20190225/1551087481_5c73b7798112f.png!small)这里，SSRF防护绕过漏洞就存在于此-<https://api.slack.com/apps/YOUAPPCODE/event-subscriptions?>，当我们设置的订阅地址URL不符合Slack API标准时，会返回以下响应消息：

![看我如何绕过Slack后端的SSRF防护机制](https://image.3001.net/images/20190225/1551087417_5c73b739617a7.png!small)

  

> Your request URL gave us a 500 error. Update your URL to receive a new
> request and challenge value.

经过测试，我发现同样用IPv6地址格式 [::] 同样在此可以利用。比如，在我的管理网站中，设置一个x.php，内容如下：

    
    
    <?php
    header("location: ".$_GET['u']);
    ?>

我们构造一个URL地址：<http://hacker.site/x.php/?u=http://>[::]:22/，URL编码后为：<http://hacker.site/x.php/?u=http://%5B::%5D:22/>，把它填写在订阅地址的Request
URL处，会有以下响应：

![看我如何绕过Slack后端的SSRF防护机制](https://image.3001.net/images/20190225/1551087537_5c73b7b1cb9ea.png!small)也就是说，这种请求Slack内部服务器22端口，且端口开放的响应如下：

    
    
    "body": {
     SSH-2.0-OpenSSH_7.2p2 Ubuntu-4ubuntu2.4
    Protocol mismatch.
    }

如果Slack内部服务器端口未开放（25），会有如下响应：

![看我如何绕过Slack后端的SSRF防护机制](https://image.3001.net/images/20190225/1551087606_5c73b7f6861bf.png!small)

    
    
    "body": {
     220 squid-iad-ypfw.tinyspeck.com ESMTP Postfix
    221 2.7.0 Error: I can break rules, too. Goodbye.
    }

如果Slack内部服务器端口不存在，会没有任何响应：

![看我如何绕过Slack后端的SSRF防护机制](https://image.3001.net/images/20190225/1551087634_5c73b8127613f.png!small)

### 漏洞影响

攻击者利用这种SSRF漏洞，可以借由服务端的功能特性，去读取服务器内部资源信息，探测内部服务端口和版本情况。漏洞上报后，Slack安全团队认为我的漏洞是重复报，但我觉得他们搞错了，最终Slack还是认为我的漏洞有效。

### 漏洞上报进程

> 2018.7.24 漏洞初报 被评为重复报
>
> 2018.9.2 漏洞验证分类 有效报
>
> 2019.1.23 Slack发放$500赏金
>
> 2019.2.22 漏洞披露

 ***参考来源：[medium](https://medium.com/@elberandre/1-000-ssrf-in-slack-7737935d3884)，clouds编译，转载请注明来自FreeBuf.COM**  

