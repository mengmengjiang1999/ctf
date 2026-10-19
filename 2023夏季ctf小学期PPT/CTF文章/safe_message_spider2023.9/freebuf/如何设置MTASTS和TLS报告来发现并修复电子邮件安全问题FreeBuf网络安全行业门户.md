![](https://image.3001.net/images/20220419/1650377642_625ec3aaf0c9fc7dd7eed.png!small)

这篇教程阐述如何使用 DMARCLY 来设置 MTA-STS 和 TLS 报告。

#### 什么是 MTA-STS

MTA-STS 是 Mail Transfer Agent - Strict Transport Security 的简称。这个技术允许邮件服务器宣称接受
TLS 连接的能力，以及决定发送 SMTP 服务器是否应该拒绝向没有使用可信服务器证书实施 TLS 的服务器投递邮件。

#### 为什么需要 MTA-STS

中间人 (MiTM)
攻击是一种网络攻击，攻击者暗中截获邮件并篡改这些邮件。通过中继发送者和接收者的消息，攻击者可以使用中间人攻击来窃取敏感信息，比如登录密码，银行帐户，或者毁坏数据。

STARTTLS 可以被用来把一个明文 SMTP 连接变成加密连接，如果接收服务器支持 TLS 的话。但是这仍然无法避免中间人攻击，因为 STARTTLS
命令可以被攻击者覆盖，并且接收服务器对此一无所知。

使用 MTA-STS，域名管理者可以命令支持 MTA-STS 的邮件服务器不把邮件通过不加密的连接投递到他们的域名上。这大大增加了中间人攻击的实施难度。

#### 如何设置 MTA-STS

要设置 MTA-STS，首先需要创建一条 TXT 记录，并发布在 _mta-sts.your-domain 上面，由此来宣称域名支持 MTA-STS：

    
    
    _mta-sts.your-domain IN TXT "v=STSv1; id=12345678"

在上面的 `v=STSv1; id=12345678`中：

  * `v`标签必须是 `STSv1`；
  * `id`标签包含由字母和数字组成的串，最大长度是 32，用来标记策略 (见下面说明) 更新；它必须唯一地指定一个策略，这样通过和之前记录 的 id 比较，发送者就能够知道策略是否已经改变。

您可以[登录](https://dmarcly.com/login)到控制台，到 DNS 记录/MTA-STS & TLS-RPT，就能够找到这样一条记录，如下所示：

![MTA-STS
Record](https://image.3001.net/images/20220419/1650377647_625ec3af987af2b5db8c6.png!small)

接下来需要创建如下的 MTA-STS 策略：

    
    
    version: STSv1
    mode: testing
    mx: your-email-host
    max_age: 86400

在上面的策略中：

  * version 必须是 `STSv1`；
  * mode 可以是 `enforce`, `testing`, 或者 `none`： 
    * enforce 模式：如果接收主机 MX 匹配失败，证书无效，或者不支持 STARTTLS，发送服务器一定不能把邮件投递到该主机；
    * testing 模式：发送服务器投递邮件；如果实施了 TLS 报告，发送服务器会发送一份 TLS 报告到指定的邮件地址，表明策略应用失败，如果接收主机 MX 匹配失败，证书无效，或者不支持 STARTTLS；
    * none 模式：发送服务器将域名视为没有发布任何活跃策略；
  * mx 指向 MX 主机；可以有多对 mx 键/值；
  * max_age 是策略的最大生命期，以秒计算；最大是 31557600。

根据您自己的 MX 设置来对 MTA-STS 策略中的 mx 值进行调整。比如，如果域名的 MX 记录指向：`your-email-server.com`，需要把策略更新成：

    
    
    version: STSv1
    mode: testing
    mx: your-email-server.com
    max_age: 86400

如果有多条 MX 记录的话，在策略中创建多条 mx 键/值对：

    
    
    version: STSv1
    mode: testing
    mx: your-email-server.com
    mx: another-email-server.com
    max_age: 86400

一旦策略更改完毕，将它保存在一个本地电脑上的文本文件 `mta-sts.txt`中。

接下来我们需要发布该 MTA-STS 策略文件，这样它可以被任何人访问到：

    
    
    https://mta-sts.your-domain/.well-known/mta-sts.txt

采取以下 2 步：

  1. 在 DNS 中创建一个 `mta-sts`子域名；
  2. 在网页根目录下面创建一个 `.well-known`子目录，并将 mta-sts.txt 拷贝到 `.well-known/`。

一旦完成，请在浏览器中输入下面的 url，确保该 MTA-STS 策略文件可以访问：

    
    
    https://mta-sts.your-domain/.well-known/mta-sts.txt

> 请确保 SSL 证书已经在 Web 服务器上面正确设置，使得 https://mta-sts.your-domain/.well-known/mta-> sts.txt 可以通过 **HTTPS** 访问，而不是HTTP。使用自签名证书将无法正常工作。

如果可以在浏览器中看到该策略，那么策略文件就已经正确发布了。

<https://dmarcly.com/blog/how-to-set-up-mta-sts-and-tls-reporting>

#### 为什么需要 TLS 报告

既然已经实施了 MTA-STS，现在可以实施 TLS 报告 (TLS-RPT) 来接收 TLS aggregate 报告了。有了 TLS aggregate
报告，可以发现电子邮件安全问题，并且采取行动来修复。

#### 如何设置 TLS 报告

要设置 TLS 报告，在域名上面发布一个 TXT 记录即可：

    
    
    _smtp._tls.your-domain IN TXT "v=TLSRPTv1; rua=mailto:5b1121ef0d8a3@tls.dmarcly.com"

在上面的记录 `v=TLSRPTv1; rua=mailto:5b1121ef0d8a3@tls.dmarcly.com`中：

  * `v`标签必须是 `TLSRPTv1`；
  * `rua`标签指向一个由逗号分隔的电子邮件地址列表；TLS aggregate 报告会发送到这些电子邮件地址；

如果使用 DMARCLY 的话，系统已经为您创建了一个邮箱来接收 TLS 报告。[登录](https://dmarcly.com/login)控制台，去
DNS 记录/MTA-STS & TLS-RPT，就能够发现类似下面的指向该邮箱的 TLS-RPT 记录：

![Default TLS-RPT
Record](https://image.3001.net/images/20220419/1650377650_625ec3b266f38c6c8a4dc.png!small)

注意需要使用在控制台中实际显示的值，而不是上面的。

在发布了指向该邮箱的 TLS 记录以后，DMARCLY 会帮您接收 TLS 报告。这些报告通常每天发送一次，因此在发布了 TLS 记录后的一两天，就能在
DMARCLY 中看到报告。

下面是一个 TLS 报告的例子，JSON 格式编码：

    
    
    {
       "organization-name":"Google Inc.",
       "date-range":{
          "start-datetime":"2021-05-20T00:00:00Z",
          "end-datetime":"2021-05-20T23:59:59Z"
       },
       "contact-info":"smtp-tls-reporting@google.com",
       "report-id":"2021-05-20T00:00:00Z_acme.com",
       "policies":[
          {
             "policy":{
                "policy-type":"sts",
                "policy-string":[
                   "version: STSv1",
                   "mode: testing",
                   "mx: acme.com",
                   "max_age: 86400"
                ],
                "policy-domain":"acme.com"
             },
             "summary":{
                "total-successful-session-count":0,
                "total-failure-session-count":3
             },
             "failure-details":[
                {
                   "result-type":"validation-failure",
                   "sending-mta-ip":"209.85.222.201",
                   "receiving-ip":"173.212.201.41",
                   "receiving-mx-hostname":"acme.com",
                   "failed-session-count":2
                },
                {
                   "result-type":"validation-failure",
                   "sending-mta-ip":"209.85.208.176",
                   "receiving-ip":"173.212.201.41",
                   "receiving-mx-hostname":"acme.com",
                   "failed-session-count":1
                }
             ]
          }
       ]
    }

下面是在 DMARCLY 控制台中显示的 TLS 记录数据：

![TLS Aggregate Report
Example](https://image.3001.net/images/20220419/1650377667_625ec3c3943bc830aee9e.png!small)

本文翻译自 <https://dmarcly.com/blog/how-to-set-up-mta-sts-and-tls-reporting>，转载时请保留完整内容。

