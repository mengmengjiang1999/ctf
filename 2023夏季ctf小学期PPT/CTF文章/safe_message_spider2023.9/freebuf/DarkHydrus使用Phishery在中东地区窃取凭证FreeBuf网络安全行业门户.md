**在上周，Unit
42发表了一个篇关于介绍一个名为DarkHydrus的新威胁组织的博文，我们观察到该组织的目标是位于中东地区的政府实体。在这篇文章中，我们对通过鱼叉式网络钓鱼传播的被我们称之为RogueRobin的PowerShell
payload进行了讨论。并且，我们还知道DarkHydrus在2018年6月实施了一次凭证窃取攻击。另外，这似乎还是一场仍在继续进行中的活动，因为我们有证据表明使用相同基础设施的凭证窃取尝试可以追溯到2018年秋季，而这些攻击所针对的目标均是位于中东地区的政府实体和教育机构。**

凭据窃取攻击使用了包含恶意Microsoft
Office文档的鱼叉式网络钓鱼电子邮件，这些文档利用“attachTemplate”技术从远程服务器加载模板。当尝试加载这个远程模板时，Microsoft
Office将显示一个身份验证对话框，要求用户输入登录凭证。在输入之后，这些凭证将被发送到C2服务器，DarkHydrus便是通过这种方式来窃取用户帐户凭证的。

基于Unit
42的分析，DarkHydrus使用开源Phishery工具创建了两个用于凭证窃取攻击的Word文档。正如我们在之前的博文中所讨论的那样，这进一步突显了DarkHydrus对开源攻击工具的依赖。

像这样目的在于窃取凭证的网络钓鱼攻击并不是什么新鲜事：US-CERT
在2017年就曾发出警告，称有不同的威胁组织使用了与此类似的攻击技术。值得注意的是，DarkHydrus使用开源工具对这些实体进行有针对性的攻击，这与他们对开源工具的依赖相吻合，而这些攻击与我们上周报道的目标也一致。基于此，我们可以合理地推测，在不久的将在，该组织有极大可能会继续在中东地区针对此类目标发起攻击。

## 凭证窃取攻击

在2018年6月24日，Unit 42观察到DarkHydrus对位于中东地区的一个教育机构实施了凭证窃取攻击。在这起攻击中，涉及到一封以“Project
Offer（项目邀请函）”为主题的鱼叉式网络钓鱼电子邮件以及一个恶意的Word文档附件（SHA256：d393349a4ad00902e3d415b622cf27987a0170a786ca3a1f991a521bff645318）。在打开恶意Word文档时，会显示一个验证对话框，要求用户输入凭证，如图1所示。

![Hydrus_1-768x454.png](https://image.3001.net/images/20180808/1533719989_5b6ab5b5b6c5c.png!small)

图1.在打开文档时向用户展示的“身份验证”对话框

如图1所示，在验证对话框上有这样一行文字“Connecting to <这里对域名进行了屏蔽>.
0utl00k[.]net”，它实际上是DarkHydrus的一个C2服务器。如果用户在此对话框中输入了自己的凭证并按下“OK”按钮，凭证则将通过URL
https://<
这里对域名进行了屏蔽>.0utl00k[.]net/download/template.docx发送​​到这个C2服务器。在验证对话框消失之后，Word文档将呈现它的内容。在我们展示的这个样本中，它的内容是空白的。

DarkHydrus在创建他们C2域时似乎也进行了仔细思考，试图进一步诱使目标用户输入他们的凭证。0utl00k[.]net域看上去非常像是微软提供免费电子邮件服务的合法“outlook.com”域，这种相似性更加不容易引起用户的怀疑，进而使他们更有可能输入自己的凭证。

我们利用0utl00k
[.]net域找到了另外两个用于窃取凭证的Word文档，如表1所示。我们首次发现这两个文档的时间分别是在2017年9月和11月，这表明DarkHydrus几乎一直在进行这种凭证窃取活动。

![list1.jpg](https://image.3001.net/images/20180808/1533720002_5b6ab5c26af28.jpg!small)

表1.用于窃取凭证的另外两个Word文档

这两个文档都使用了attachmentTemplate技术，通过将凭证发送到URL
<https://0utl00k>[.]net/docs来对其进行窃取。与2018年6月的文档不同，在凭证被窃取之后，这两个文档都呈现了与目标受害者相关的内容。其中，2017年9月的文档呈现的是一份员工调查表，如图2所示。

![Hydrus_2.png](https://image.3001.net/images/20180808/1533720013_5b6ab5cd7dba3.png!small)

图2.凭证被窃取后显示的员工调查表

2017年11月的文档呈现的是一份密码移交表，如图3所示。我们没有能够在已公开的研究中找到相同的文档，这可能表明这份密码移交表是攻击者在其以前的活动中收集到的。

![Hydrus_3-768x677.png](https://image.3001.net/images/20180808/1533720027_5b6ab5db27990.png!small)

图3.凭证被窃取后显示的密码移交表

在这些凭证窃取攻击中使用的基础设施都使用了0utl00k [.]net域，在攻击中解析为107.175.150[.]113 and
195.154.41[.]150。在[之前关于介绍这场活动的博文](https://researchcenter.paloaltonetworks.com/2018/07/unit42-new-threat-actor-group-darkhydrus-targets-middle-east-government/)中，我们已经就对相同的基础架构进行了讨论。

## Phishery工具

在分析了三个恶意Word文档之后，我们确定其中两个文档是使用名为Phishery的开源工具创建的。Phishery工具包含了以下功能：

1.通过注入远程模板URL来创建恶意Word文档；

2.在尝试获取远程模板时，托管的C2服务器会收集输入到身份验证对话框中的凭证。

我们能够确认的是，DarkHydrus的确使用了开源的Phishery来创建这些Word文档，并连接到自己的C2服务器。在2018年6月攻击中，DarkHydrus所使用的恶意Word文档就添加了一个远程模板URL，如图4所示。

![Hydrus_4-768x714.png](https://image.3001.net/images/20180808/1533720043_5b6ab5eba2573.png!small)

图4.在2018年6月的文档中发现的远程模板URL

我们利用Phishery创建了一个用于测试的文档，并使用了图4中的远程模板URL。图5展示了这个过程，Phishery能够将这个URL注入到我们所创建的名为“good_test.docx”的文件中，我们将生成的文件保存为“bad_test.docx”。

![Hydrus_5-650x69.png](https://image.3001.net/images/20180808/1533720057_5b6ab5f9b889b.png!small)

图5.利用Phishery创建测试文档

为了验证恶意文档的功能，我们使用了Phishery的C2服务器，并打开了DarkHydrus在2018年6月的攻击中使用的Word文档。当出现验证对话框时，我们输入“fakename”和“fakepass”作为凭证，如图6所示，然后按回车键。

![Hydrus_6-768x459.png](https://image.3001.net/images/20180808/1533720073_5b6ab60983373.png!small)

图6.在身份验证对话框中输入虚假的凭证

在C2服务器上，我们观察到Phishery收到了入站请求并获取到了凭证，如图7所示。具体来讲，当我们打开DarkHydrus的Word文档时，C2服务器能够获取到我们在身份验证对话框中输入的“fakename”和“fakepass”。

![Hydrus_7-650x104.png](https://image.3001.net/images/20180808/1533720086_5b6ab6168df32.png!small)

图7. PhisheryC2获取到的凭证

## 结论

DarkHydrus是一个新发现的威胁组织，以中东地区的组织为目标开展攻击活动。我们发现，DarkHydrus使用恶意Word文档来实施凭据窃取攻击，并通过鱼叉式网络钓鱼电子邮件将这些文档发送给政府实体和教育机构。恶意文档是使用Phishery工具创建的，DarkHydrus使用了自己的C2服务器来窃取凭证。对于Phishery的使用进一步表明，Dark
Hydrus主要依赖于开源工具来开展活动。

## IoCs

样本：

> d393349a4ad00902e3d415b622cf27987a0170a786ca3a1f991a521bff645318
>
> 9eac37a5c675cd1750cd50b01fc05085ce0092a19ba97026292a60b11b45bf49
>
> 0b1d5e17443f0896c959d22fa15dadcae5ab083a35b3ff6cb48c7f967649ec82

基础设施：

> 0utl00k[.]net
>
> 107.175.150[.]113
>
> 195.154.41[.]150

 ***本文作者：Hydralab，转载请注明来自FreeBuf.COM**

