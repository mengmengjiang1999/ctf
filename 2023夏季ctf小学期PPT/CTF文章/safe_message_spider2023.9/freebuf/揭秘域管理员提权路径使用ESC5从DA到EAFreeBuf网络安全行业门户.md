一种从域管理员提权到企业管理员的全新攻击路径。

##  **ESC5**

ESC5又被称为“易受攻击的PKI对象访问控制”。Will Schroeder和Lee Christensen编写的《Certified Pre-Owned》白皮书在讨论ESC5时提到了三类对象：

  * CA服务器的AD计算机对象（即通过S4U2Self或S4U2Proxy进行攻击）
  * CA服务器的RPC/DCOM 服务
  * 容器中的子对象或子容器（例如证书模板容器、证书颁发机构容器、NTAuthCertificates 对象、注册服务容器等）

本文主要讨论第三项的工作原理，并演示如何使用它通过域信任提升到企业管理员。

##  **ADCS LDAP 层次结构**

ADCS在LDAP中存储有关CA和证书模板的信息，可以通过打开ADSI并连接到配置命名上下文（Configuration
NC）来查看这些对象。然后向下检索：

![](https://image.3001.net/images/20230714/1689329573_64b11fa5299d97e2617cc.png!small)

Configuration > Services > Public Key Services

下面是该层次结构的图表，包括将要滥用的对象：

![](https://image.3001.net/images/20230714/1689329601_64b11fc1924daeb80762b.png!small)"Certificate
Templates"容器存储着可以发布到ADCS CA的模板。查看下述对话框，它能够帮助列出该容器中的所有模板对象：

![](https://image.3001.net/images/20230714/1689329649_64b11ff18cd65608dcf6b.png!small)"Enrollment
Services"容器为每个CA存储一个pKIEnrollmentService对象。这些对象在其"Certificate
Templates"属性上列出了已“发布”到CA的模板：

  

![](https://image.3001.net/images/20230714/1689329674_64b1200a53b1e091d7188.png!small)这是需要控制来执行ESC5
的两个LDAP对象，包括一个证书模板和
pKIEnrollmentService对象。假设pKIEnrollmentService对象与受信任执行域身份验证的CA相关联，并且它要么作为根CA受信任，要么链接到根CA。

##  **Configuration NC的特殊现象**

在展示如何进行攻击之前，需要了解一些基础知识。  
配置命名上下文（Configuration NC）是Active
Directory中存储着整个林范围配置数据的位置，子域在复制配置数据时必须从这里复制。Configuration NC的Distinguished
Name为CN=Configuration，DC=example，DC=local，其中 DC=example，DC=local是林根域的DN。  
正如您所预想的那样，如果配置中的某个对象在林根域处发生更改，则该更改会向下复制到林中的所有域。但您可能不知道的是，反之亦然：如果配置中的对象在子域中发生更改，则该更改会复制到林根。这是因为林中的每个可写域控制器都有一个林配置命名上下文（Configuration
NC）的可写副本。  
Jonas Bülow Knudsen、Martin Sohn Christensen和 Tobias Thorbjørn Munch Torp
撰写了一篇博客文章（https://improsec.com/tech-blog/sid-filter-as-security-boundary-between-domains-part-4-bypass-sid-filtering-research），文章中提到他们滥用此机制，通过滥用指向站点的GPO链接，从子域中的域管理员升级到林根中的企业管理员。  
这里是一个实验环境，域管理员有一个名为ForestRoot.local的林根域和一个名ChildDomain.ForestRoot.Local的子域：

![](https://image.3001.net/images/20230714/1689329721_64b120394a672d76dc433.png!small)当连接到子域的配置命名上下文（Configuration
NC）时，查看公钥服务容器的DN，然后查看配置命名上下文（Configuration NC）的域名：

![](https://image.3001.net/images/20230714/1689329742_64b1204eb44329a15a097.png!small)

这里查看的其实是林根域对象的子域本地副本。  
现在看一下此对象的安全描述符：  
![](https://image.3001.net/images/20230714/1689329766_64b12066eeb312ea69204.png!small)  
作为子域中的域管理员，无法控制此对象。您可以看到此处添加ACE的按钮变灰，但需要注意到SYSTEM主体对此对象具有完全控制权。关闭MMC并重新打开它，但这次使用PsExec以SYSTEM用户身份启动MMC：![](https://image.3001.net/images/20230714/1689329786_64b1207a8331d6ee6aa11.png!small)再次连接到域本地配置命名上下文（Configuration
NC），导航到Public Key
Services容器，并显示其安全描述符：![](https://image.3001.net/images/20230714/1689329802_64b1208abbcbdd1dfde32.png!small)现在可以添加ACE。向该对象添加一个ACE，以便Bob
- 子域中的用户
-完全控制该容器：![](https://image.3001.net/images/20230714/1689329821_64b1209d7cb37bb26110a.png!small)现在再看一下Public
Key Services容器，但这次是在林根域控制器上的配置命名上下文（Configuration
NC）中：![](https://image.3001.net/images/20230714/1689329844_64b120b47872edeb743d2.png!small)可以看到ACE已经从子域复制到了林根域。

## 整合

当想滥用LDAP中PKI对象的控制时，至少需要以下能力来执行 ESC5：

  * 能够将新模板添加到证书模板容器。
  * 对与林根CA关联的pKIEnrollmentService对象的写入访问权限，以及与NT身份验证可信的CA关联或链接到的pKIEnrollmentService 对象。

接下来将向您展示如何将子域中的域管理员转换为林根目录中的企业管理员。通过之前的知识您可以看到，作为子域中的域管理员，可以完全控制Public Key
Services容器。

虽然无法完全控制 pKIEnrollmentService 对象，但可以授予自己其控制权，因为该对象启用了权限继承：

![](https://image.3001.net/images/20230714/1689329902_64b120ee44b0668d8e177.png!small)但是默认模板禁用了权限继承，作为子域中的域管理员无法控制它们：

![](https://image.3001.net/images/20230714/1689329956_64b121245dab4a1180b36.png!small)

接下来看一下Certificate Templates容器本身的安全描述符：

![](https://image.3001.net/images/20230714/1689329977_64b121399eaedf74885c3.png!small)使用PsExec以SYSTEM用户身份在子DC上启动MMC：

![](https://image.3001.net/images/20230714/1689329999_64b1214f22f9eb601be85.png!small)

然后，将连接到域本地配置命名上下文（Configuration NC）并导航到Certificate
Templates容器。现在可以完全控制该对象，其中包括添加子对象的能力。

可以用SYSTEM用户身份打开certsrv.msc，然后复制现有模板：

![](https://image.3001.net/images/20230714/1689330024_64b12168d8f3a9baed050.png!small)

打开新模板的属性，通过在模板配置以下选项来执行ESC1：

1.向在子域中控制的主体授予注册权限。

2.将客户端身份验证包含在应用程序策略中。

3.允许证书请求中的 SAN。

4.未启用管理员批准或授权签名。

将新模板写入企业配置命名上下文（Configuration NC）的子域副本中，然后它将自行复制到林根域控制器的配置命名上下文（Configuration
NC）中：

![](https://image.3001.net/images/20230714/1689330070_64b12196de3a46a877d60.png!small)现在，需要将模板发布到CA。可以通过滥用对该对象的完全控制，以子DC上的SYSTEM用户身份执行此操作：

![](https://image.3001.net/images/20230714/1689330088_64b121a89cace3254322b.png!small)

当证书在此对象的certificateTemplates属性上列出时，证书就会“发布”到CA。所以说，想将模板“发布”到CA，需要做的就是将模板添加到该列表中：

![](https://image.3001.net/images/20230714/1689330110_64b121be11f84d0983f80.png!small)

如果在林根域控制器上启动certsrv.ms 并检查CA的“证书模板”，确实可以看到这个新的恶意模板现在已“发布”并可供使用：

![](https://image.3001.net/images/20230714/1689330132_64b121d451e00a1d6d8cf.png!small)

现在准备工作已经完成，可以执行 ESC1 将子域中的 DA 转换为林根域的 EA。

使用 Certify 来获取证书，指定恶意模板和想要模拟的企业管理员：

![](https://image.3001.net/images/20230714/1689330157_64b121edd9b11f8ecaf45.png!small)

使用openssl将证书转换为PFX：

![](https://image.3001.net/images/20230714/1689330204_64b1221c6380252ad0b2c.png!small)通过
RDP 连接将 PFX 放到子域DC上，使用Rubeus为企业管理员用户获取 TGT：

![](https://image.3001.net/images/20230714/1689330217_64b122297d820eca146cd.png!small)

可以通过wmic证明TGT是有效的：

![](https://image.3001.net/images/20230714/1689330235_64b1223ba990ec095bdf3.png!small)

##  **基于图表思考**

用图表来描述这个攻击路径将有助于理解所有的横向移动关键点。

从林根域及其配置命名上下文（Configuration NC）中的相关对象开始，青色节点是根域，橙色节点是容器，紫色节点是C 对象：

![](https://image.3001.net/images/20230714/1689330269_64b1225d648ea5852bfb3.png!small)

现在添加与林根域具有双向信任的子域：

![](https://image.3001.net/images/20230714/1689330296_64b12278c35deef52de68.png!small)子域具有林根域的配置命名上下文（Configuration
NC）的子域本地副本：

![](https://image.3001.net/images/20230714/1689330309_64b1228549e051028a2d1.png!small)对子域中的域本地对象所做的更改将复制到林根域中的相应对象：

![](https://image.3001.net/images/20230714/1689330324_64b12294065306257868e.png!small)子域的域控制器上的SYSTEM用户可以完全控制从林根域的配置命名上下文（Configuration
NC）复制到本地子域的某些对象：

![](https://image.3001.net/images/20230714/1689330338_64b122a2a82b762044822.png!small)对"Certificate
Templates"容器的完全控制意味着能够向该容器添加新对象。此处添加的任何新模板也会复制到林根域：

![](https://image.3001.net/images/20230714/1689330362_64b122ba6bc23ea6f1758.png!small)CA是林根域的根CA，林根域有着自己的用户，如ForestRootDA用户：

![](https://image.3001.net/images/20230714/1689330376_64b122c895167dfd25152.png!small)红色边缘显示了从子域的域控制器到林根域管理员的整个攻击路径：

![](https://image.3001.net/images/20230714/1689330387_64b122d3cba780d98ea9e.png!small)

## 结语

这篇文章展示了攻击者如何使用ESC5，然后使用ESC1将子域中的DA转换为林根域处的EA。  
还有一些问题需要花时间去思考：如果 ADCS 尚未部署怎么办？例如，如果完全控制"Public Key
Services"容器但没有CA，是否可以引导必要的LDAP对象并颁发CA将DA转变为EA？

  

