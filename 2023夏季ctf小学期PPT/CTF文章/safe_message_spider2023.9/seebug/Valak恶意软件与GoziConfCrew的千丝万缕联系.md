**原文链接：[Valak Malware and the Connection to Gozi Loader
ConfCrew](https://labs.sentinelone.com/valak-malware-and-the-connection-to-gozi-loader-confcrew/ "Valak Malware and the Connection to Gozi Loader
ConfCrew")**  
**译者：知道创宇404实验室翻译组**

Valak是使用基于脚本的多阶段恶意软件，该软件劫持电子邮件并嵌入恶意URL附件，以使用无文件脚本来感染设备。这些恶意软件主要在广告活动中使用，会让人联想到Gozi
ConfCrew。

关Valak详情请见报告：<https://assets.sentinelone.com/labs/sentinel-one-valak-i>

## 背景

截止目前，Gozi已经以各种形式存在了十多年。该软件的某些变种操作过程更加复杂，主要通过特洛伊木马或租用服务模式来进行操作。其中一个变体使用了密钥10291029JSJUYNHG，由于其独特的回复方式以及线程垃圾邮件的劫持引得不少关注。在实际过程中，秘钥虽然与dreambot混淆，但两者的操作却相互分开，该项服务主要进行程序加载以及垃圾邮件分发。

虽然这个Gozi服务已经持续运行了几年，在2019年10月中旬，Valak开始出现测试模式。这个新的基于javascript的系统还涉及到受破坏的服务器以及基于链接的电子邮件活动，这与典型的密码保护附件方法有所不同。

## 研究思路

**交付——ConfCrew交付系统**

最近的Valak传递链利用了与PHP传递代理联系的文档文件，以便下拉并执行初始DLL有效负载。这个系统以前曾被Gozi操作人员用于竞选活动，经常被标记为Gozi流量（类似于URL结构）。

例如：

`5184b70eef0d99c77e3e56f7e7b67727e515364e`

下载：

`80af349e1d41195576eeb7badc26d9b7873bdfbc`

通过以下URL：

`hxxp://a8xui1akl9gjqucfa[.]com/vv55v37kts7et/idq9p9t142vyk.php?l=frraw2.cab`

这是解压后的Valak DLL加载程序。从IOC和沙箱报告中可以看到，这种恶意软件的切换已经引起了混乱，并且某些报告中其被标记为Gozi。

### 投放——受损的网站

检索恶意文档的另一种传递途径是电子邮件中的链接，该链接随后与受感染的网站联系以检索初始DLL加载器来进行引爆。这些链接在受感染的网站上标记为随机PHP文件，这些PHP文件将返回文档中而不是DLL中。广告类别服务器可同时用于文档和DLL，用户可以进行查找并同时执行。

![](https://images.seebug.org/content/images/2020/06/1c846005-48c3-4528-8ea1-4f6f178e7110.jpg-w331s)

### 受损的PHP脚本

下面列出了最近的Valak交付的请求结构：

    
    
    /_3ZyKva_O9zPO1K_k.php?x=MDAwMCCz9oR8W_gfwzPN6OQPNnku8FfF-ORh5orr1PzC0Avh3LkS4cvcHcQm38Efx3sZMnArLlPqOq5dmdcTOCewa7719Cc84VKgzrxYXx_1dF6N2TuRZ_A_wW8lpm2QOdV0_o-ebn1WCpHJl7o1CJKc3KfF8T-nLUAzS-P_dBt2BVUaVi2OQs-a35JD6DWiJux2-xL2eyIwGBlte-n8hD-egM3iqfh8Zw

这种看似随机的数据与base64有一些惊人的相似之处，但是我们需要PHP来进行解码。

![](https://images.seebug.org/content/images/2020/06/c71aa576-d6ac-4cdf-8f34-83cb208f711c.jpg-w331s)

该脚本采用URL参数，并使用嵌入式密钥解密联系人URL。首先，可以清除base64编码的数据并进行初始解码，例如：

    
    
    >>>a = 'MDAwMCCz9oR8W_gfwzPN6OQPNnku8FfF-ORh5orr1PzC0Avh3LkS4cvcHcQm38Efx3sZMnArLlPqOq5dmdcTOCewa7719Cc84VKgzrxYXx_1dF6N2TuRZ_A_wW8lpm2QOdV0_o-ebn1WCpHJl7o1CJKc3KfF8T-nLUAzS-P_dBt2BVUaVi2OQs-a35JD6DWiJux2-xL2eyIwGBlte-n8hD-egM3iqfh8Zw~
    >>> a = a.replace('-', '+')
    >>> a = a.replace('_', '/')
    >>> a = a.replace('~', '=')
    >>> a
    'MDAwMCCz9oR8W/gfwzPN6OQPNnku8FfF+ORh5orr1PzC0Avh3LkS4cvcHcQm38Efx3sZMnArLlPqOq5dmdcTOCewa7719Cc84VKgzrxYXx/1dF6N2TuRZ/A/wW8lpm2QOdV0/o+ebn1WCpHJl7o1CJKc3KfF8T+nLUAzS+P/dBt2BVUaVi2OQs+a35JD6DWiJux2+xL2eyIwGBlte+n8hD+egM3iqfh8Zw=='
    >>> b = base64.b64decode(a)
    >>> a
    'MDAwMCCz9oR8W/gfwzPN6OQPNnku8FfF+ORh5orr1PzC0Avh3LkS4cvcHcQm38Efx3sZMnArLlPqOq5dmdcTOCewa7719Cc84VKgzrxYXx/1dF6N2TuRZ/A/wW8lpm2QOdV0/o+ebn1WCpHJl7o1CJKc3KfF8T+nLUAzS+P/dBt2BVUaVi2OQs+a35JD6DWiJux2+xL2eyIwGBlte+n8hD+egM3iqfh8Zw=='
    >>> b
    '0000 \xb3\xf6\x84|[\xf8\x1f\xc33\xcd\xe8\xe4\x0f6y.\xf0W\xc5\xf8\xe4a\xe6\x8a\xeb\xd4\xfc\xc2\xd0\x0b\xe1\xdc\xb9\x12\xe1\xcb\xdc\x1d\xc4&\xdf\xc1\x1f\xc7{\x192p+.S\xea:\xae]\x99\xd7\x138\'\xb0k\xbe\xf5\xf4\'<\xe1R\xa0\xce\xbcX_\x1f\xf5t^\x8d\xd9;\x91g\xf0?\xc1o%\xa6m\x909\xd5t\xfe\x8f\x9en}V\n\x91\xc9\x97\xba5\x08\x92\x9c\xdc\xa7\xc5\xf1?\xa7-@3K\xe3\xfft\x1bv\x05U\x1aV-\x8eB\xcf\x9a\xdf\x92C\xe85\xa2&\xecv\xfb\x12\xf6{"0\x18\x19m{\xe9\xfc\x84?\x9e\x80\xcd\xe2\xa9\xf8|g'

然后，PHP脚本中的segment变量为0，此例子的压缩标志为空格；如果被压缩，则为“z”。

剩余的URL部分使用内置密钥解码。密钥数据非常多，我们之前解码的分段值实际上是该巨型密钥的索引乘数。

![](https://images.seebug.org/content/images/2020/06/6b62da4a-faea-40d0-aa0f-5f6893d91bc8.jpg-w331s)

知道了这一点并有了密钥，我们现在可以解码出联系人URL。

    
    
    >>> test = bytearray(b[5:])
    >>> key = bytearray(base64.b64decode('24LwDGHXMPQL49nWNhhLHsh5/czLDIfjh/mfqrVoirnLP4Wur3bpUraseuoZeEBdR0c9gUmBMPCkcBdT2QXHhoBGSJJ9yaDYPScxhRwusoppwzi0d4geUudZ43WyCoCywTEoHWHIhs74A2Hlrq2SjogSikk0bAqOkTZYJGljbRJMuBOm45ikJ41nwROeT4xqlShaenQvByGiie1bqfWM0vCaRBmIkM9aEhfrEgfsj2TVSkpT+UWiEt/CfDj0xV+1YCjpJw+E3qwO9X0FOtZ4PpetY5cnif5QWN0Evg7k1nBh+choS2ydJyhsDlmhhASlCI4xkj8A6zjrJkrNVguMr6CanLlIwJZycHqcm7TntyKChEKrsJE4VyNMUAfpMSWnEk61QBapDw7t67h/lg9mwLsmm/UMmhNGkLR+55HHk92XoD0BNTOtnfpnZ0eI77z5aRiZTixoz8FVteOtc3vP2MHZ2rjffbhAqf3ayVcwjQpS/5KnK0FWkjruI34LXSFgeRZvCXrH5ZNBzamTpVDnhKR0L98Ksztvpk77jGGx5vhoZ0MYDExkM4F6fhlBNHR9ZCCpelT8kR2g5v0RK9iMkc3GtMyQwKgL37XfcTQciSYjaH6D2jFsC7/ODK0IeIJIujcHaXx0ddLFJMibvnRqAEfYTbRAQRwjSrHfBQkk14GyehISjqKwJF8XOoRs/Jt6OllExDUI35xe6moFR3L6zZAzot7CtNIOeTvJ+bROHxWxUZheRQW3+Q/9jGryWHA6q+x/f+kz+ZqrsF6Wnax9hk91SI1bMOwE3lYvIjxQCVYOo2moVyE4Dy6iIHZBrSVNNBcmJ9NQEFDGCPPqhI/JMxE92UddkfzPyC+nlkKcnGguIUaJMZ3gceZnmksH/XN2XUnW1VEh8TC2tfsvThIMbB0Mxh5zX9CiTpwIrDN/4Xo2xE9apnRCJ+uLBW+cGoRM8X69xuoY/EgfLPGP7JBwIMYD56PjyyrNjZSI4Mh4/zokOP0h5OmQEXFTU9wBeWhJMgZWkCyA5jyw2lmI'))
    >>> for i in range(len(test)):
    ...  test[i] ^= key[i]
    ...
    >>> test
    bytearray(b'http://78.129.208.84/mail-checker-desk-time-bar-links/misc/tinystats/index.php?SRR_DHIqwA4sLg~UKkYOYB6iw2q5Ky--dt_AmnBCRl6wDa6QiyG6deRc5r9wxcSxJl6jZKuid7uA0Yb8~')

在执行解密后，我们才算真正的下载了URL。使用这个PHP脚本检索的活动文件（如Office文档和
DLL加载器），不会直接存储在PHP文件中，而是存储在预先生成的活动UPL传递给代理脚本的结果中，以便在执行时检索到它们.

总而言之，代理脚本利用嵌入式密钥来解密URL并检索内容。

外观相似的编码字符串`index.php`作为参数传递给文件(包含广告系列特定数据的编码消息)。如果我们继续研究此PHP文件的功能，可以推测出它可用于跟踪统计信息以及广告系列文件的交付过程。

![](https://images.seebug.org/content/images/2020/06/cea9c781-3044-43b6-a1c2-3d4fa09fe044.jpg-w331s)

从后端提供广告系列文件：

![](https://images.seebug.org/content/images/2020/06/6a0d28f5-8a0b-4ac8-80c9-981b0018a58f.jpg-w331s)

## 统计面板

经过进一步分析，发现统计小组证实了我们的假设，对每个广告系列都进行仔细跟踪。在下图中，将显示每个文件的匹配项以及运算符和文件名。这对于典型的负载服程序，其需要统计信息才能准确地向客户收费。

![](https://images.seebug.org/content/images/2020/06/fd5d701a-87e1-4448-a531-10cc90f27cd3.jpg-w331s)

该面板还显示其活动中每个链接的跟踪，这样可以更加深入了解每个活动的成功执行次数。

![](https://images.seebug.org/content/images/2020/06/32097097-7fba-47b0-bf69-bad54f1ac1ab.jpg-w331s)

## Valak

其他研究人员已经对Valak进行了广泛的研究，我们将从Gozi
ConfCrew和Valak之间联系的方面来进行入手，这些研究主要围绕新插件的使用。当Valak在2019年进行测试时，看到了许多不同的插件。但存在两个涉及电子邮件凭据数据的收集的问题，其中一个是交换抓取器。

收集电子邮件凭据与Gozi之前的策略一致，他们会从帐户中收集电子邮件，然后在垃圾邮件中使用电子邮件链进行“回复链攻击”。该攻击围绕劫持现有的合法电子邮件，并将回复信息发送到垃圾邮件中。这种技术可以让用户措手不及，由于用户之前接受过识别假邮件的训练，当看到这封邮件是一个回复（尤其是使用用户信任的接收方式时），用户会放松警惕。回复链攻击还意味着参与者无需投资于创建看起来合法的电子邮件模板，因为他们能够利用真正的电子邮件通信链。

### Exchange数据插件——EXCHGRABBER

如果用户打算利用垃圾邮件中的回复链攻击，那就需要一些电子邮件数据。有趣的是，当攻击活动转移到Valak而不是Gozi时，却出现了围绕盗窃交换数据的插件。

![](https://images.seebug.org/content/images/2020/06/fda7f35b-ef58-444c-93f6-772535bd757f.jpg-w331s)

该插件在config部分中将其自身命名为“exchgrabber”或交换抓取器。该名称适合.NET编译插件，因为该插件可以从凭据管理器中找到凭据，可以更方便对Office相关联的凭据进行查找。然后，使用来自autodiscover.xml的数据，并将它构建成为报告。

![](https://images.seebug.org/content/images/2020/06/4b8003e4-cec0-4c66-b31d-204d093e585b.jpg-w331s)

检索数据后，它将数据渗入C2：

![](https://images.seebug.org/content/images/2020/06/304b0944-ca8a-42ba-994d-5ac29d9ff375.jpg-w331s)

### 电子邮件凭证插件——CLIENTGRABBER

最近关注点已转移到电子邮件盗窃和企业目标定位上，这很有趣。在进行这项研究时，我们还发现了一个名为“clientgrabber”的新插件，该插件主要用于从注册表中窃取电子邮件凭据。

![](https://images.seebug.org/content/images/2020/06/607d1736-22bf-4d78-916f-b9e6cc43602a.jpg-w331s)

在注册表位置中搜索“键”。

![](https://images.seebug.org/content/images/2020/06/db400e4a-9f54-4967-91ff-3d6018279109.jpg-w331s)

一旦找到，它将检查该值是否使用较新的加密方法（包含可以解密的实际加密数据）。

![](https://images.seebug.org/content/images/2020/06/9d5c28fc-d726-407d-be67-a1e049bf6b55.jpg-w331s)

## IoCs

**Endpoint**

`%temp%\\[a-f0-9]{12}.bin`  
`Scheduled task 'PerfWatson_[a-f0-9]+'`

**ADS executable and script files:**

`HKCU\\Software\\ApplicationContainer\\Appsw64\\ShimV4`
`HKCU\\Software\\ApplicationContainer\\Appsw64\\SetupServiceKey`

**Network**

Base64 encoded PE files transferred over the wire

**Samples**

435ec42fefc05eba0a8005256c815979877d430a  
693e681e7be554e50e4ff9bf7cbfe5aeab3fe91f  
e22b404e1fec743f0795cdea8a95337660878860  
dba1337a0a8293b721642b8b45a86352bcdfd04f  
4d33425d7031284cf5ee323dc616d9f84987dc0d  
17b74a4c3f43c21504b355b1ffc333280ef4cd74  
7f58d22d9e95f65170acadd05e324ec2d8ef13f6  
9be234bf2268f4e055ea59cf7bef76781a36c35c  
19f481063ca956688824e3cc022b8eedb6dd0bea  
4ae3ed6c1ab2fe41daf6f650a54dae63684d2064  
30fd553dedfadc81522adf37e11dfc4039d4ea31

## 参考链接

  1. <https://twitter.com/vk_intel/status/1207917643291910144>

  2. <https://en.wikipedia.org/wiki/ROT13>

  3. <http://prsecurity.org/2019-valak-c2.html>

  4. <https://www.zdnet.com/article/this-phishing-trick-steals-your-email-and-then-fools-your-friends-into-downloading-malware/>

  5. <https://app.any.run/tasks/8e5b6f19-c3e5-4c87-87ac-8c8e012cbb5f/>

  6. <https://www-cybereaso-com.cdn.ampproject.org/c/s/www.cybereason.com/blog/valak-more-than-meets-the-eye>

  7. <https://securityxploded.com/outlookpasswordsecrets.php>

  8. <https://www.webroot.com/blog/2019/04/03/hijacked-email-reply-chains/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1246/>

