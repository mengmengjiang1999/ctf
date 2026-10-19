![](https://image.3001.net/images/20220419/1650366725_625e990583b69426fa734.png!small)

本文解释什么是 BIMI，如何实施 BIMI 来提升邮件可信度，增加互动率，以及改善邮件抵达率和打开率。

#### 什么是 BIMI？

BIMI 是 Brand Indicator for Message Identification
的简称，它允许域名管理者和邮件客户端协作以在邮件中显示品牌标志。

#### 为什么要用 BIMI？

没有 BIMI 的话，邮件客户端只会显示一个通配的占位符标志和品牌首字母。除了通过查看品牌名称，邮件接收者可能无法轻易地识别您的品牌。

但是，一旦 BIMI 实施之后，品牌标志将会在邮件中显示，这可以提升品牌识别度。

下面图片对没有 BIMI 的邮件和激活 BIMI 后的邮件做了比较：

![no-bimi-vs-bimi](https://image.3001.net/images/20220419/1650366731_625e990b3ab3f61ce0641.png!small)

正如上图所示，在左图中 BIMI 没有被激活，邮件仅仅显示了一个通配的标志。在右图 BIMI
被激活了，邮件显示了品牌标志，这会立刻增加用户的信任，并且吸引用户打开邮件。

下面是当 BIMI 被激活时，一封带有受信任的品牌标志的邮件：

![gmail-bimi-brand-logo](https://image.3001.net/images/20220419/1650366736_625e99103f4ea7f4765c2.png!small)

与此对比，发自一个没有实施 BIMI 的域名的邮件不会显示品牌标志：

![gmail-no-bimi-brand-logo](https://image.3001.net/images/20220419/1650366741_625e991558417a92c9dff.png!small)

显然，BIMI 帮助建立和增加品牌知名度和用户信任度，从而增加邮件交互率，并且最终改善邮件抵达率。

<https://dmarcly.com/blog/what-is-bimi-bimi-explained>

#### BIMI 的前置条件

既然品牌标志仅仅显示在成功验证的邮件中，您需要先设置 SPF, DKIM 和 DMARC。

要在域名上设置 SPF, DKIM 和 DMARC，请参阅我们的[终极指南](https://dmarcly.com/blog/zh-CN/how-to-implement-dmarc-dkim-spf-to-stop-email-spoofing-phishing-the-definitive-guide)。

此外，请确保 DMARC 策略已经设成 p=quarantine 或者 p=reject。

一旦这些前置条件满足，就可以实施 BIMI 了。

#### 如何实施 BIMI？

在域名上面实施 BIMI 需要采取以下步骤：

  1. 为品牌标志注册一个商标；
  2. 购买一个验证商标证书 Verified Mark Certificate (VMC)；
  3. 把 VMC 上传到服务器上面；
  4. 把品牌标志上传到服务器上面；
  5. 创建一个 BIMI 记录；
  6. 把 BIMI 记录发布到 DNS 中；
  7. 检查 BIMI 记录来确保成功。

下面我们来逐一了解。

##### 1 为品牌标志注册一个商标

一些邮箱服务提供商像 Gmail 要求实施 BIMI 必须要有 VMC。在购买 VMC 之前，必须要到知识产权机构把品牌标志注册成商标。

可以在世界知识产权组织 (WIPO) 运营的[品牌数据库](https://www3.wipo.int/branddb/en/)搜索品牌标志。

##### 2 购买 VMC

一旦品牌标志被注册成了商标，请浏览至以下 VMC 发布者网站之一来获取
VMC：[DigiCert](https://www.digicert.com/tls-ssl/verified-mark-certificates)和
[Entrust](https://www.entrust.com/)。

在这个过程中，需要向该服务提交一个品牌标志的 SVG 文件，来获取一个指向该 SVG 文件的 PEM 文件。

##### 3 上传 VMC 到服务器

在从所选的数字证书发布服务获得所需的 PEM 文件后，需要把它上传到您的网页服务器中，使它可以被任何人访问。

请注意网页服务器必须使用 HTTPS 保护，并且指向该 PEM 文件的网址必须以 **https://** 开头，否则会失败。

这样就创建了一条指向该 PEM 文件的网址：

    
    
    https://yourserver.com/vmc.pem

##### 4 上传品牌标志

和上面的 PEM 文件类似，您需要上传用 SVG 格式编码的品牌标志到服务器上面，使得所有人可以访问。

这样就创建了一条指向该品牌标志文件的网址：

    
    
    https://yourserver.com/logo.svg

这条网址将在第 5 步中被用到。

##### 5 创建 BIMI 记录

和 DMARC 记录类似，BIMI 记录是一个 TXT 记录，它包含了多个标签，由分号分隔。

BIMI 记录中有 2 个必需的标签：`v`和 `l`。

`v`标签指定 BIMI 版本。目前必须是 `BIMI1`。

`l`标签指定标志 url。

`a`标签包含指向 PEM 文件的 url。这个标签对一些邮箱服务提供商比如 Gmail 是必需的。

下面是一个指定了品牌标志 SVG 和 PEM 的 BIMI 记录的例子：

    
    
    v=BIMI1; l=https://yourserver.com/logo.svg;a=https://yourserver.com/vmc.pem

这里需要注意的是 BIMI 记录中指向的 SVG 文件的内容应该和 PEM 文件中指向的 SVG 文件的内容完全相同。否则 BIMI 可能无法正常工作。

##### 6 在 DNS 中发布 BIMI

BIMI 记录是一个发布在 DNS 中的 TXT 记录，位置是：`default._bimi.yourdomain.com`。

这是一个在 DNS 中的完整的 BIMI 记录：

Record Type| Name| Value| TTL  
---|---|---|---  
TXT| default._bimi| v=BIMI1;
l=https://yourserver.com/logo.svg;a=https://yourserver.com/vmc.pem| Default  
  
##### 7 检查 BIMI 记录

在发布了 BIMI 记录后，检查一下它的合法性是好的做法。

使用我们的[免费 BIMI 记录检查器](https://dmarcly.com/tools/bimi-record-checker)来检查 BIMI
记录是否已经正确发布在域名上。只需要输入域名然后点击 Check Domain 按钮即可。

比如，检查 cnn.com 上面的 BIMI 记录返回以下结果：

![bimi-record-checker](https://image.3001.net/images/20220419/1650366744_625e9918b8a73a986677d.png!small)

如果 BIMI 已经设置好的话，检查器会显示品牌标记，如上图所示。

BIMI 正确设置好了以后，可能需要花费 48 小时才能在邮箱中显示品牌标志。

完成！您已经成功地在域名上面实施了 BIMI。

本文翻译自 <https://dmarcly.com/blog/what-is-bimi-bimi-explained>，转载请保留完整。

