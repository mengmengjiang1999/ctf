**作者：知道创宇404实验室翻译组**  
**原文链接：<https://blog.malwarebytes.com/cybercrime/2020/10/fake-covid-19-survey-hides-ransomware-in-canadian-university-attack/>**

最近，我们观察到了Silent Librarian
APT黑客组织针对[全球范围内大学](https://blog.malwarebytes.com/malwarebytes-news/2020/10/silent-librarian-apt-phishing-attack/)的[网络钓鱼](https://blog.malwarebytes.com/malwarebytes-news/2020/10/silent-librarian-apt-phishing-attack/)活动。10月19日，通过伪装的COVID-19调查，我们确定了针对哥伦比亚大学（UBC）员工的新型网络钓鱼文档，该文档是一个会自动下载勒索软件并勒索受害者的恶意Word文件。幸运的是，基于UBC网络安全团队的迅速对应措施，该网络钓鱼活动并未成功。

### 一、COVID-19强制性调查

黑客组织通过mailpoof.com服务器创建电子邮件地址，进而在Box.net和DropBox中注册帐户。不直接通过电子邮件发送假调查，而是将文档上传到Box和DropBox并使用其共享功能进行分发。这可能是为了规避会阻止来自信誉低电子邮件的网络钓鱼过滤器。黑客组织声称自己是管理员，并通过文件共享功能中发表以下评论：

> 晚上好，伙计们！管理员正在与您共享一项关于对组织应对流行病的反应的看法的强制性调查，请务必在周一前提交并尽快填写！
>
> 文末附带物资申请表格，包括：手套、洗手液、口罩或消毒喷雾剂。只需签名并输入所需物资的数量便可获取！感谢您的反馈！

![](https://images.seebug.org/content/images/2020/11/8911a633-c1aa-4154-b46c-a8fcc8ce20ca.png-w331s)
图1 针对UBC员工的网络钓鱼文档

UBC称，指定部门中有不到一百人收到该链接，文件非公开共享，因此推断黑客必须拥有Box或Dropbox帐户才能下载文件，这可能是为了规避检测或猜测到受害群体在使用这两种共享服务之一。

### 二、网络钓鱼文件分析

网络钓鱼文件使用模板注入来下载并执行带有恶意宏的远程模板（template.dotm），该文件已上传到免费的代码托管网站（notabug.org）。

![](https://images.seebug.org/content/images/2020/11/3d738aa8-ec98-4157-8399-58aa31543c31.png-w331s)
图2 模板注入和宏视图

执行宏后，它将执行以下操作：

  * 获取 _％APPDATA_ ％目录

  * 在％APPDATA％中创建 _Byxor_ 目录

  * 从以下URL下载文件并将其写为 _Polisen.exe_

_notabug[.]org/Microsoft-Office/Word-Templates/raw/master/lamnarmighar/polisen.exe_

  * 从以下URL下载文件并将其写为 _Killar.exe_

_notabug[.]org/Microsoft-Office/Word-Templates/raw/master/lamnarmighar/killar.exe_

  * 调用Shell函数执行 _killar.exe_

  * 检查shell函数的输出以及它是否成功（返回值为执行的应用程序的任务ID）

  * 如果成功，它将GET http请求发送到： _canarytokens.com/about/d4yeyvldfg6bn5y29by4e9fs3/post.jsp_

  * 如果失败，则将GET http请求发送至： _canarytokens.com/articles/6dbbnd503z06qitej1sdzzcvv/index.html_

![](https://images.seebug.org/content/images/2020/11/e4db8d85-a04d-4fa7-b890-94a4a8d9580d.png-w331s)
图3 包含勒索软件有效载荷的代码存储库

我们能够确定远程模板和有效负载的其他四个变体，发现了一些使用瑞典语的文件夹，这表明黑客可能熟悉该语言。打开网络钓鱼文档将通过canarytokens.com网站触发通知，该服务对黑客访问网络的预警系统非常有用。在这种情况下，黑客可能会对多少人打开文档以及他们来自何处感兴趣。

### 三、Vaggen勒索软件

勒索软件加密用户文件并向其添加.VAGGEN扩展名。加密过程完成后，它会在桌面上留下赎金票据，要求支付相当于80美元的比特币。

![](https://images.seebug.org/content/images/2020/11/02483f4b-dcf3-45fa-a9fe-f7eb35a6b2c1.png-w331s)
图4 赎金票据

勒索软件似乎是用Go编写的、以“
main_main”功能开头的相对简单的应用程序。主应用程序的其他功能具有混淆的名称，例如：main_FOLOJVAG、main_DUVETVAD、main_ELDBJORT、main_HIDDENBERRIES、main_LAMNARDETTA、main_SPRINGA。

    
    
    main_LAMNARDETTA-> main_enumDir
    main_ELDBJORT-> main_encryptFile
    main_SPRINGA-> main_encryptAndRename
    main_FOLOJVAG-> main_runCommands
    main_DUVETVAD-> main_dropFile
    main_HIDDENBERRIES-> main_xteaDecryptAndWriteToFile

点击[此处](https://github.com/MBThreatIntel/malspam/blob/master/killar.csv)获取功能及RVA完整列表
。

![](https://images.seebug.org/content/images/2020/11/5e5514ef-407c-4843-a51f-15d98e3d1393.png-w331s)
图5 文件枚举

恶意软件使用的某些字符串（即赎金票据的内容）通过XXTEA（使用库：[xxtea-go](https://github.com/xxtea/xxtea-go)）进行了加密 。首先解码加密的块来自Base64，XXTEA密钥是硬编码的（“
STALKER”）。执行结束时，赎金记录将被放到桌面上。文件的加密和重命名被部署为标准Golang函数回调：path.filepath.Walk。

![](https://images.seebug.org/content/images/2020/11/ac12d5c5-9a2f-4207-ae9f-fc5d04da113d.png-w331s)
图6 回调函数进行加密和重命名

在GCM模式下，文件使用AES-256（32字节长的密钥）进行加密。

![](https://images.seebug.org/content/images/2020/11/0c331174-8ff1-4b6c-81e6-ce115b110ff4.png-w331s)
图7 AES-256密码

加密算法类似于[此处](https://www.golangprograms.com/data-encryption-with-aes-gcm.html)演示的算法 ，使用由CryptGenRandom生成的硬编码密钥和12个字节长的随机数，借助gcm.Seal函数对文件内容进行加密。

![](https://images.seebug.org/content/images/2020/11/9eb1201b-97ad-4ab5-894b-e7164e13d760.png-w331s)
图8 加密例程

输出文件（扩展名为.VAGGEN）的内容包含：

  * 12个字节长的随机数
  * 加密内容
  * 16字节长的GCM标签

![](https://images.seebug.org/content/images/2020/11/d6c6cfcc-dce4-4563-919c-05696c8a29ef.png-w331s) 图9 突出显示的部分包含加密内容

在恶意软件代码中找到的硬编码密钥“ du_tar_mitt_hjart_mina_pengarna0”是瑞典语，意为“you take my heart
my
money”。[使用此密钥](https://gchq.github.io/CyberChef/#recipe=AES_Decrypt\({'option':'Latin1','string':'du_tar_mitt_hjart_mina_pengarna0'},{'option':'Hex','string':'DA
D7 BE 65 29 4D 99 2D 55 C8 B3
AB'},'GCM','Hex','Raw',{'option':'Hex','string':'D91D67EE45C247B8F9E0353F89342542'}\)&input=OTIgNTQgMzUgRTIgNEYgODggNzYgMTkgOTEgMkIgMTIgRTYgMEIgMUIgN0EgQTQgOEMgQjcgNDQgODEgNUMgRTAgQjUgQzYgQTIgOTggMEYgRjIgQjcgRkIgMDUgRDUgMkQgQzggNTYgODUgMzAgRUYgMEUgRDUgNDEgRTcgOEEgOTIgNjkgMjcgMjEgRUIgMkYgQTMgNEMgOUEgQkMgN0UgRjQgRjQgQ0UgQUIgMDkgMDYgQjggOTcgMkUgQ0EgNTAgMTAgMUUgNjMgNjEgM0MgRTcgQjMgMUQgNzIgNUEgNkEgOEQgQzIgQTYgMEMgMjcgOTggQzUgRTMgMUUgNzUgOUEgNTYgOTggNTIgOTIgRTMgREMgRUEgMjggQTIgNDYgNTAgMEIgRDEgOEEgNjQgNkYgOEEgRDIgN0IgRjIgRDEgODkgRTUgQ0UgMzMgQzcgREMgRjIgNkMgNjcgRTYgREEgNDcgMjkgRTggRjMgOUYgMUMgRUUgNjEgOUMgOTEgNTQgNDYgODIgRkQgODAgRUIgNkYgQTMgREEgNzcgREMgQkIgQ0EgRUQgQTYgRTcgODUgRkIgREYgMTQgQkQgRUUgNTYgMkYgNzggMDAgQjkgRTQgQjEgMUYgMkYgRjcgRjEgMDkgQUIgMjAgRjAgQzYgQUMgREMgQzYgNjIgNDAgQkUgM0QgMEMgNTggNDggQjAgMkIgRkIgQ0YgREIgQTYgNzcgQkEgOEMgRTIgQkEgMjUgN0MgNzUgNDUgRjkgNDQgNEUgQTUgNjkgMTIgREEgMUQgOEEgODQgRUEgOUYgRTIgMzkgRjYgMzEgRDUgMzcgM0YgNUEgOTcgRTIgMzkgQkMgQzMgQkEgRkYgMzggODUgNjYgNTAgQUQgQzQgMUYgMEUgQzIgNjIgNkYgOEMgQTkgRjUgQUYgREQgQzUgREYgN0EgMzAgRjkgODkgMTYgOUQgNjkgQkEgRTUgNDYgMjkgNTkgQjUgQzIgRjMgRkUgRUUgQUEgNjUgQzYgRUQgNjQgQTMgQjggRkIgQTIgNkUgREIgMzkgOEUgRDEgN0YgOTcgOUMgQUIgRjMgRTggMDUgMTMgOUQgNDQgMDMgRTggOEIgN0QgNjYgQzcgMDIgQUMgNzYgRjEgNDIgOUQgRDkgMzEgMEUgMkMgNDEgOEYgOUYgNUEgOEYgQjMgM0IgMDUgMzggRDEgMzkgMUIgREMgMzcgQzAgMDUgRTIgRUIgRjQgNUQgQTEgMTIgQjQgOEQgM0MgMTQgNUIgN0IgQTMgNjkgMUYgMjMgMTEgNEEgODIgMTcgMjYgRTMgNzIgQkUgNjEgRUIgMkEgQUMgQzMgODQgNjggOTYgNDcgNTkgQkEgOTAgQzIgOUEgMkQgNzcgMUMgREUgMTEgN0YgMEQgNzggQzAgREUgMDcgMzUgMUQgNjIgMDEgODkgRjQgMkUgMkYgMzggOTMgREUgRkQgNDQgQTMgNkQgMTEgRkUgODAgREQgNDggMDYgOUQgQ0IgRTAgNDkgRTcgQTYgQkMgOEUgN0YgRjkgRDMgMzEgRjIgNzggNDkgNzUgREEgRkMgQzYgN0MgMjYgNzUgNjcgRTIgOTEgQzMgQzggNUEgQzYgMjMgRkEgMTQ)，我们可以轻松地解密内容。

![](https://images.seebug.org/content/images/2020/11/d21087a2-5b72-44f2-9354-11b4dd72af71.png-w331s)
图10 在代码中找到的加密密钥

通过所有这些元素，我们可以恢复加密文件而无需支付赎金。到目前为止，该黑客组织似乎尚未收到任何付款。

![](https://images.seebug.org/content/images/2020/11/3d5cf74f-0536-4b09-9a13-97221b1cd2a7.png-w331s)
图11 比特币地址显示没有付款

### 四、赎金数额异常偏低

我们认为该黑客组织并不复杂，它不隶属于Ryuk等大型勒索软件团队 ，其勒索数量极少，并且不同于专业勒索软件，极其容易被恢复。

但是，该网络钓鱼活动的构想很周到，模板设计得很好，并带有添加金丝雀标记的感觉。目前尚不清楚哥伦比亚大学是否为唯一受害者。

搜寻存储库，我们发现了[其他Word模板文件](http://notabug.org/austrianzer0/Microsoft-Tools/)，这些[文件](http://notabug.org/austrianzer0/Microsoft-Tools/)使用了非常相似的宏，这引发了有关该网络钓鱼活动背后的更多问题。

感谢哥伦比亚大学与我们共享信息，进而更好地了解该黑客组织。借助无签名防利用层，Malwarebytes客户已受到保护。

![](https://images.seebug.org/content/images/2020/11/e2768070-3e03-4280-8815-1befdf327984.png-w331s)
图12 被恶意软件端点保护阻止的网络钓鱼文档

## 五、IOCs

**Variant1:**  
_summerofficetemplate.dotm_  
634264996c0d27b71a5b63fb87042e29660de7ae8f18fcc27b97ab86cb92b6d4  
notabug[.]org/arstidar/VARLDVINNA/raw/master/irving.exe  
notabug[.]org/arstidar/VARLDVINNA/raw/master/alderson.exe  
canarytokens[.]com/traffic/jnk5rpagi54vztro6tau6g1v6/index.html  
canarytokens[.]com/traffic/articles/tags/z8yobwprmmopmyfyw8sb1fb0a/index.html  
_alderson.exe_  
34842eff9870ea15ce3b3f3ec8d80c6fd6a22f65b6bae187d8eca014f11aafa5  
_irving.exe_  
00c60593dfdc9bbb8b345404586dcf7197c06c7a92dad72dde2808c8cc66c6fe

**Variant2:**  
_UBC-COVID19-Survey-Mandatory.docx_  
e869e306c532aaf348725d94c1d5da656228d316071dede76be8fcd7384391c3  
_template.dotm_  
334531228a447e4dfd427b08db228c62369461bb2ccde9ab1315649efd0316b1  
notabug[.]org/Microsoft-Office/Word-Templates/raw/master/lamnarmighar/polisen.exe  
notabug[.]org/Microsoft-Office/Word-Templates/raw/master/lamnarmighar/killar.exe  
canarytokens[.]com/about/d4yeyvldfg6bn5y29by4e9fs3/post.jsp  
canarytokens[.]com/articles/6dbbnd503z06qitej1sdzzcvv/index.html  
_polisen.exe_  
03420a335457e352e614dd511f8b03a7a8af600ca67970549d4f27543a151bcf  
_killar.exe_  
43c222eea7f1e367757e587b13bf17019f29bd61c07d20cbee14c4d66d43a71f

**Variant3:**  
_template1.dotm_  
225e19abba17f70df00562e89a5d4ad5e3818e40fd4241120a352aba344074f4  
notabug[.]org/Microsoft-Templates/Template/raw/master/irving.exe  
notabug[.]org/Microsoft-Templates/Template/raw/master/alderson.exe  
canarytokens[.]com/images/tags/8pkmk2o11dmp1xjv5i9svji32/contact.php  
canarytokens[.]com/articles/traffic/5ayx8tydzeuzhmq6y5u2lxhpa/post.jsp

**Variant4:**  
_smoothtemplates.dotm_  
ada43ee41f70e327944121217473c536024cd9c90e25088a1a6c5cf895f59fe1  
notabug[.]org/arstidar/VARLDVINNA/raw/master/irving.exe  
notabug[.]org/arstidar/VARLDVINNA/raw/master/alderson.exe  
canarytokens[.]com/traffic/jnk5rpagi54vztro6tau6g1v6/index.html  
canarytokens[.]com/traffic/articles/tags/z8yobwprmmopmyfyw8sb1fb0a/index.html  
_alderson.exe_  
b4a1a0012abde1ae68f50fa1fe53df7a5d933ec5410731622ab0ad505915cfb6  
_irving.exe_  
00c60593dfdc9bbb8b345404586dcf7197c06c7a92dad72dde2808c8cc66c6fe

**Variant5:**  
template.dotm:  
7ad8a3c438f36cdfc5928e9f3c7c052463b5987055f583ff716d0382d0eb23b4  
notabug[.]org/Microsoft-Office/Office-Templates/raw/master/mrclean.exe  
notabug[.]org/Microsoft-Office/Office-Templates/raw/master/mrmonster.exe  
canarytokens[.]com/images/feedback/tags/0xu6dnwmpc1k1j2i3nec3fq2b/post.jsp  
canarytokens[.]com/traffic/about/images/ff6x6licr69lmjva84rn65hao/contact.php  
mrmonster.exe  
f42bbb178e86dc3449662b5fe4c331e3489de01277f00a56add12501bf8e6c23  
mrclean.exe  
71aadf3c1744f919cddcc157ff5247b1af2e2211b567e1eee2769973b2f7332a

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1390/>

