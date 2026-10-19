![](https://image.3001.net/images/20220421/1650498937_62609d79efa8576310801.jpg!small)

DMARC 标签在 DMARC 记录中被用来定义 DMARC 实现的不同方面，比如策略，aggregate 报告邮箱地址 URI，forensic
报告邮箱地址 URI，以及其他。

#### 什么是 DMARC 记录？

DMARC 记录是一个发布在 DNS 中，域名上面的 TXT 资源记录。它包含一个由分号隔开的 DMARC 标签的列表，用来告知邮件接收服务器在邮件
DMARC 验证失败时，应该如何处理。

以下是一个 DMARC 记录的例子：

    
    
    v=DMARC1; p=reject; rua=mailto:5b06a2badd9f1@report.com; ruf=mailto:5b06a2badd9f1@report.com; sp=none; fo=0;

要参阅更为详尽的 DMARC 记录的描述，可以看[关于 DMARC 记录的一切](https://dmarcly.com/blog/zh-CN/everything-about-a-dmarc-record)。

<https://dmarcly.com/blog/what-are-dmarc-tags-dmarc-tags-explained>

#### 什么是 DMARC 标签

正如上面所看到的，该 DMARC 记录包含多个部分，由分号隔开：`v`, `p`, `rua`, `ruf`, `sp`, 和
`fo`。每一个标签都有一个值，用来定义 DMARC 的一个方面。

有以下可用的 DMARC 标签：

  * `v`是 DMARC 版本；其值总是 `DMARC1`；
  * `p`是 DMARC 策略；可以是：`none`, `quarantine`, 和 `reject`, 依次对应 DMARC 的三个模式；
  * `rua`指定接收 DMARC aggregate 报告的邮箱的 URI。要请求 DMARC aggregate 报告的话，这是必须的；
  * `ruf`指定接收 DMARC failure/forensic 报告的邮箱的 URI。要请求 DMARC failure/forensic 报告的话，这是必须的；
  * `adkim`(可选，缺省是 "r") 指定 DKIM Identifier 对齐模式。可以是以下其中之一： 
    * r: 宽松模式
    * s: 严格模式
  * `aspf`(可选，缺省是 "r") 指定 SPF Identifier 对齐模式。可以是以下其中之一： 
    * r: 宽松模式
    * s: 严格模式
  * `fo`(可选，缺省是 "0") 指定 failure/forensic 报告选项。如果 ruf 标签未定义的话，该标签会被忽略。这个标签的值是一串由冒号隔开的字符：'0', '1', 'd', 和 's':

    * 0: 发送 DMARC failure/forensic 报告，如果 SPF 和 DKIM 同时对齐失败；
    * 1: 发送 DMARC failure/forensic 报告，如果 SPF 和 DKIM 之一对齐失败；
    * d: 发送 DKIM failure 报告，如果邮件的 DKIM 签名验证失败；
    * s: 发送 SPF failure 报告，如果邮件的 SPF 验证失败。

举个例子，下面的 DMARC 记录请求接收所有的 failure 报告：

    
        v=DMARC1; p=reject; rua=mailto:5b06a2badd9f1@report.com; ruf=mailto:5b06a2badd9f1@report.com; sp=none; fo=0:1:d:s;

  * `pct`(可选，缺省是 100) 指定将 DMARC 策略应用到的邮件的百分比。例如，下面的 DMARC 记录请求把 reject 策略应用到 10% 的邮件： 
    
        v=DMARC1; p=reject; rua=mailto:5b06a2badd9f1@report.com; ruf=mailto:5b06a2badd9f1@report.com; sp=none; pct=10;

  * `sp`(可选) 指定所有子域名的策略。它仅应用到子域名，而不是域名本身。语法和 `p`标签完全一致。如果不定义的话，`p`标签的值将会应用到子域名上面；
  * `rf`(可选，缺省是 "afrf") 指定 failure/forensic 报告的语法。当前只有 "afrf" 被支持；
  * `ri`(可选，缺省是 86400) 指定发送 aggregate 报告的时间间隔，以秒计算。缺省情况下，DMARC aggregate 报告每天发送。

本文翻译自 <https://dmarcly.com/blog/what-are-dmarc-tags-dmarc-tags-explained>，转载请保留完整内容。

