## 0x00 前言

specterops发布了一篇关于Active Directory 证书服务相关漏洞的白皮书

https://www.specterops.io/assets/resources/Certified_Pre-Owned.pdf，关于Active
Directory 证书服务的攻击第一次系统的进入我们的视野。

我在白皮书的基础上学习了Active Directory 证书服务相关的漏洞，作为学习成果，用两篇文章来介绍Active Directory
证书服务相关的基础以及相关的漏洞利用。截止这篇文章发布为止，有些漏洞利用相关的工具并没有发布出来，在文章里面我会用其他的方式来演示。

白皮书里面，最核心的点在于证书服务发布的部分证书可用于kerberos认证，并且在返回的PAC里面能拿到NTLM hash。这就是可以做很多事了，比如

1、拿到用户的凭据，能不能用用户的凭据来申请一个证书，这个证书用于kerberos认证，后面就算用户的密码改了，只要证书在手，就能用证书随时拿回NTLM。

2、能不能在用户的电脑上找到证书，以后拿着这个证书去做认证。

3、什么样的证书能用于kerberos认证。

4、拿到CA服务器证书之后，能不能给任何用户颁发证书，再用这个证书做认证，跟黄金票据一样。

5、CA服务器上有没有一些配置，能让一个用户申请别人的证书，然后拿到这个证书做认证。

6、CA证书申请有个界面是http的，http默认不开签名，我们能不能通过Ntlm_Relay将请求relay到这里，申请用以进行kerberos认证的证书。

关于这些，都会在这两篇文章里面讨论。在写完之后，由于内容过长，我将文章拆分为两篇，第一篇是介绍一些基础部分，以及三个相关的利用

1、窃取证书

2、通过凭据申请可用以Kerberos认证的证书

3、通过证书窃取用户凭据

在第二篇主要介绍一些其他的利用，包括

1、证书服务中的Ntlm_Relay

2、证书模板配置错误

3、黄金证书

3、PKI 设计缺陷

4、防御指南

整体的思路如下图

![](https://image.3001.net/images/20210816/1629104449_611a294172b0ad5fd1574.png!small)

## 0x01 Active Directory 证书服务安装

在开始讲解证书服务之前，我们先装个证书服务，方便起见，直接在域控上安装就行。

下一步下一步比较简单。

![](https://image.3001.net/images/20210816/1629104450_611a2942796c13750f7da.png!small)

![](https://image.3001.net/images/20210816/1629104451_611a294343107da1f973a.png!small)

![](https://image.3001.net/images/20210816/1629104452_611a294484bfb2a0cf303.png!small)

![](https://image.3001.net/images/20210816/1629104453_611a29459ccbe5b935cc7.png!small)

![](https://image.3001.net/images/20210816/1629104454_611a29468fd2a0018a4c0.png!small)

![](https://image.3001.net/images/20210816/1629104455_611a29477e6577f775ec7.png!small)

![](https://image.3001.net/images/20210816/1629104456_611a29483ea885bf1301c.png!small)

![](https://image.3001.net/images/20210816/1629104457_611a29492e78d245666d5.png!small)

![](https://image.3001.net/images/20210816/1629104458_611a294a6039e5d7c30a3.png!small)

![](https://image.3001.net/images/20210816/1629104459_611a294b55240330f37b7.png!small)

![](https://image.3001.net/images/20210816/1629104460_611a294c7a9709627f3b2.png!small)

![](https://image.3001.net/images/20210816/1629104461_611a294d75a3ac5746f13.png!small)

![](https://image.3001.net/images/20210816/1629104462_611a294e85fe88cb27f45.png!small)

![](https://image.3001.net/images/20210816/1629104463_611a294f7c341518032ce.png!small)

![](https://image.3001.net/images/20210816/1629104464_611a29509d74453adeada.png!small)

## 0x02 Active Directory 证书服务概述

### 0x0201 企业 PKI

PKI是一个术语，有些地方会采用中文的表述——公钥基本结构，用来实现证书的产生、管理、存储、分发和撤销等功能。我们可以把他理解成是一套解决方案，这套解决方案里面需要有证书颁发机构，有证书发布，证书撤掉等功能。

微软的Active Directory 证书服务(我们可以简称AD
CS)就是对这套解决方案的实现。ADCS能够跟现有的ADDS服务进行结合，可以用以加密文件系统，数字签名，以及身份验证。下面详细介绍下AD
CS中比较重要的的证书颁发机构以及证书模板。

### 0x0202 证书颁发机构

证书颁发机构 (CA) 接受证书申请，根据 CA 的策略验证申请者的信息，然后使用其私钥将其数字签名应用于证书。然后 CA
将证书颁发给证书的使用者。此外，CA 还负责吊销证书和发布证书吊销列表 (CRL)。

ADCS里面的CA分为企业CA和独立CA，最主要的区别在于企业CA与ADDS服务结合，他的信息存储在ADDS数据库里面(就是LDAP上)。企业CA也支持基于证书模板和自动注册证书，这也是我们比较关心的东西，如果没有特指，文章里面提到的CA默认就是企业CA。

举个例子，我们有个有个域名`daiker.com`，如果要做https，我们就需要找证书颁发机构申请证书，比如说沃通CA。

我们也可以自己搭建一个证书颁发机构。

![](https://image.3001.net/images/20210816/1629104466_611a29523093855f95724.png!small)

但是使用自建的证书发布服务之后,浏览器还是不信任我们证书，我们经常可以看到

![](https://image.3001.net/images/20210816/1629104467_611a2953d5d64ec6323fe.png!small)

自行签名的根证书。之所以出现这个是因为电脑本身并不相信我们的CA证书。以下证书是windows内置的CA证书。如果我们能够把我们的CA证书放在这个列表里面，我们的证书就能得到信任。

![](https://image.3001.net/images/20210816/1629104470_611a2956632c053d8823b.png!small)对于企业来说，如果使用ADCS服务，想让员工的计算机信任我们企业自己的CA证书，有以下几种方式

1、安装企业根CA时，它使用组策略将其证书传播到域中所有用户和计算机的“受信任的根证书颁发机构”证书存储

2、如果计算机不在域内，可以手动导入CA证书

另外AD CS支持可缩放的分层 CA 模型，在此模型中，子从属 CA 由其父 CA 颁发的证书认证。层次结构顶部的 CA 称为根 CA。根 CA 的子 CA
称为从属 CA。

![](https://image.3001.net/images/20210816/1629104476_611a295c922698a46a21b.png!small)

以上图为例子，每个企业仅有一个根CA，他由自己颁发，在大多数组织中，它们只用于颁发从属
CA，不直接颁发证书。而具体的证书由从属CA颁发，比如网站的证书，LDAPS的证书，这样做方便管理，在机器比较多的域内还能起到负载均衡的作用。当然，AD
CS支持分层的CA模型不代表一定要分层，对于比较小的公司，一般都只有一个根CA，所有的证书由这个根CA进行颁发。

### 0x0203 证书模板

证书模板是证书策略的重要元素，是用于证书注册、使用和管理的一组规则和格式。这些规则是指谁可以注册证书。证书的主题名是什么。比如要注册一个web证书，那可以在`Web服务器`这个默认的证书模板里面定义谁可以注册证书，证书的有效时间是多久，证书用于干啥，证书的主题名是什么，是由申请者提交，还是由证书模板指定。

我们可以使用`certtmpl.msc`打开证书模板控制台

![](https://image.3001.net/images/20210816/1629104478_611a295e3364566a4c348.png!small)

这些都是系统默认的证书模板。

如果需要发布一个新的模板的话，可以右键复制模板，然后自己定义这些规则。

![](https://image.3001.net/images/20210816/1629104481_611a29616fb7bd972af92.png!small)

我们关心以下规则

**常规设置：**交付证书的有效期，默认是一年

![](https://image.3001.net/images/20210816/1629104483_611a2963de048d6670415.png!small)

**请求处理：**证书的目的和导出私钥的能力(虽然设置了证书不可被导出，但是mimikatz依旧能导出，我们后面会详细说)

![](https://image.3001.net/images/20210816/1629104485_611a29659805695f2ce8e.png!small)

**加密：**要使用的加密服务提供程序 (CSP) 和最小密钥大小

![](https://image.3001.net/images/20210816/1629104488_611a296876e3e9e2d2767.png!small)

 **Subject name**
，它指示如何构建证书的专有名称：来自请求中用户提供的值，或来自请求证书的域主体的身份。这个需要注意的是，默认勾选了`在使用者名称中说那个电子邮件名`，当用户去申请的时候，如果用户的LDAP属性没有mail就会申请失败。

![](https://image.3001.net/images/20210816/1629104491_611a296b3f70d08fb42c5.png!small)

 **颁发要求** ：CA证书经理程序批准

这个值得注意，就算用户有注册权限(在ACL里面体现)，但是证书模板勾选了这个，也得得到证书管理的批准才能申请证书，如果没有勾选这个，那有权限就可以直接申请证书了。

![](https://image.3001.net/images/20210816/1629104493_611a296d50b6999e0325f.png!small)

 **安全描述符** ：证书模板的 ACL，包括具有注册到模板所需的扩展权限的主体的身份。关于这个的内容看证书注册那节的证书注册权限里面。

**扩展：**要包含在证书中的 X509v3 扩展列表及其重要性（包括`KeyUsage`和`ExtendedKeyUsages`）

这里我们要特别注意的是扩展权限里面的应用程序模板，

![](https://image.3001.net/images/20210816/1629104494_611a296ec16dfa4323974.png!small)

这个扩展决定了这个模板的用途，比如说文档加密，文档签名，智能卡登陆等等。

![](https://image.3001.net/images/20210816/1629104496_611a29705f51fad718c9d.png!small)

经过测试与研究，spectorops的工程师发现包含以下扩展的证书可以使用证书进行kerberos认证。

1、客户端认证

2、PKINIT 客户端身份验证

3、智能卡登录

4、任何目的

5、子CA

其中PKINIT不是默认存在的，需要我们手动创建，点击新建，名称自定义，对象标识符为`1.3.6.1.5.2.3.4`

![](https://image.3001.net/images/20210816/1629104497_611a2971b660c6c52678c.png!small)

![](https://image.3001.net/images/20210816/1629104498_611a2972e6ea581c37efc.png!small)

## 0x03 证书注册

### 0x00301 证书注册流程

![](https://image.3001.net/images/20210816/1629104500_611a29747462307d53349.png!small)

1、客户端生成一个证书申请文件，这一步可以使用openssl生成,比如

    
    
    openssl req -new -SHA256 -newkey rsa:4096 -nodes -keyout www.netstarsec.com.key -out www.netstarsec.com.csr -subj "/C=CN/ST=Beijing/L=Beijing/O=netstarsec/OU=sec/CN=www.netstarsec.com"
    

或者直接找个在线的网站https://myssl.com/csr_create.html生成

2、客户端把证书申请文件发送给CA，然后选择一个证书模板。

![](https://image.3001.net/images/20210816/1629104503_611a29772972041fab6b0.png!small)

这一步可以申请的方式比较多，上面这种是通过访问证书注册界面进行注册的。ADCS请求注册证书的方式在下一小节具体说明。

3、CA证书会判断模板是否存在，根据模板的信息判断请求的用户是否有权限申请证书。证书模板会决定证书的主题名是什么，证书的有效时间是多久，证书用于干啥。是不是需要证书管理员批准。

4、CA会使用自己的私钥来签署证书。签署完的证书可以在颁发列表里面看到。

![](https://image.3001.net/images/20210816/1629104504_611a2978bbf42ab81c56c.png!small)

### 0x00302 证书注册接口

1、访问证书注册网页界面

要使用此功能，ADCS 服务器需要安装证书颁发机构 Web 注册角色。我们可以在添加角色和功能向导>AD证书颁发机构Web注册服务里面开启。

![](https://image.3001.net/images/20210816/1629104506_611a297aed4a4814d9408.png!small)

开启完就访问https://CA/certsrv 访问证书注册网页界面

![](https://image.3001.net/images/20210816/1629104508_611a297c4a721df098996.png!small)

2、域内机器可以通过启动 certmgr.msc (用于用户证书)或 certlm.msc (用于计算机证书)来使用 GUI 请求证书

![](https://image.3001.net/images/20210816/1629104509_611a297dd6299cd951115.png!small)

3、域内机器可以通过命令行`certreq.exe`和Powershell`Get-Certificate `来申请证书

4、使用`MS-WCCE`,`MS-ICPR`这俩RPC，具体交互流程得去看文档

5、使用CES，需要安装证书注册WEB服务，soap的格式，具体的交互流程得看`MS-WS-TEP`和`MS-XCEP`

![](https://image.3001.net/images/20210816/1629104512_611a29802626476722aae.png!small)

6、使用网络设备注册服务，得安装网络设备注册服务

![](https://image.3001.net/images/20210816/1629104514_611a298240bdf21710e6b.png!small)

### 0x0303 证书注册权限

知道了证书注册的流程，注册的接口，接下来我们关注的就是证书注册的权限。跟证书注册相关的权限主要有两块，一块体现在CA证书上，一块体现在证书模板上。

我们可以运行`certsrv.msc`之后右键证书颁发机构，右键属性，安全查看权限。

![](https://image.3001.net/images/20210816/1629104515_611a2983db37858cee834.png!small)

对于CA证书的权限，我们比较关注的是请求证书的权限。默认情况下，所有认证用户都有请求权限。如果有请求的权限，CA就去判断请求的模板是否存在，如果存在，就交给证书模板去管理权限。

证书模板的权限，可以运行`certtmpl.msc`之后选择特定的证书模板，右键属性，安全查看权限

![](https://image.3001.net/images/20210816/1629104517_611a2985e51c7a2c74a67.png!small)

我们比较关注以下权限

注册权限(Enroll)

拥有这个权限的用户拥有注册权限

![](https://image.3001.net/images/20210816/1629104519_611a2987a75e1d20cc65f.png!small)

自动注册的权限(AutoEnrollment)  
在配置证书自动注册的时候需要证书模板开启这个权限，关于证书自动注册的更多细节，在下一小节会详细说明。

AllExtendedRights/Full Control  
AllExtendedRights 包括所有的扩展权限，就包括了注册权限和自动注册权限。  
Full Control包括所有权限，也包括有的扩展权限

我们关心完CA的权限以及证书模板的权限之外，还得注意一个配置`CA证书管理程序批准`

![](https://image.3001.net/images/20210816/1629104521_611a29896be9335dcf183.png!small)

如果证书模板没有勾选这个，那么有ca的证书请求权限，证书模板的注册权限，就可以申请下证书。但是如果勾选了这个选项，那么就算有注册权限，那也得得到证书管理员的批准才能注册证书。

### 0x0304 证书自动化注册

相较于注册，自动化注册顾名思义就是自动化，不需要用户手动注册。有些软件需要用户证书去访问，让每个用户自己手动申请证书又不太现实，这个时候自动化注册证书的优势就体现出来了。

接下来演示下怎么配置证书自动化注册。

1、配置一个证书模板

选择一个已有的模板，右键复制模板

![](https://image.3001.net/images/20210816/1629104522_611a298a781856933f7ef.png!small)

名字改成用户自动化注册

![](https://image.3001.net/images/20210816/1629104523_611a298b3c5d57dd63c53.png!small)

去掉以下两个勾，因为有些用户可能没有配置邮箱，自动化申请证书的时候就会失败。

![](https://image.3001.net/images/20210816/1629104524_611a298c5e7bc414356ab.png!small)

给这个证书模板赋予任何`Domain Users`有注册和自动化注册的权限

![](https://image.3001.net/images/20210816/1629104526_611a298e55b8bb1ee6fae.png!small)

然后下发一个组策略

新建一个组策略，命名为`自动注册证书`

然后打开用户配置>策略>安全设置>公钥策略,配置下图圈出来的三个

![](https://image.3001.net/images/20210816/1629104528_611a2990a4356d5da1316.png!small)

![](https://image.3001.net/images/20210816/1629104530_611a29926133cb948c09c.png!small)

![](https://image.3001.net/images/20210816/1629104531_611a299396597a1704b95.png!small)

![](https://image.3001.net/images/20210816/1629104532_611a2994c2ca53d21bfce.png!small)

然后等组策略生效，域内的每个用户登录的时候都会自动申请一个证书，不用人为申请证书。

## 0x04 Active Directory 证书服务在LDAP中的体现

ADCS的信息同样也存储在LDAP上，我们可以在配置分区底下的Service底下的`Public Key Services`看到证书相关的信息

，比如在我们的环境就位于`CN=Public Key
Services,CN=Services,CN=Configuration,DC=test16,DC=local`。

![](https://image.3001.net/images/20210816/1629104535_611a29978038f9ded01d8.png!small)

每一块的对象的用途都不一样，接下来我们详细介绍我们比较关注的几个对象

Certification Authorities

这个对象是证书颁发机构，定义了受信任的根证书。

每个 CA 都表示为容器内的一个 AD 对象,objectClass为`certificationAuthority`。

CA证书的内容以二进制的内容放在cACertificate底下。

Enrollment Services  
这个对象定义了每个企业 CA。  
每个企业CA 都表示为容器内的一个 AD 对象,objectClass为`pKIEnrollmentService`  
CA证书的内容以二进制的内容放在cACertificate底下。dNSHostName定义了CA的DNS主机

certificateTemplates  
这个对象定义了所有证书模板

NTAuthCertificates  
此条目用于存储有资格颁发智能卡登录证书并在 CA 数据库中执行客户端私钥存档的 CA
的证书。关于智能卡，后面会单独写一篇文章详细阐述智能卡，在这篇文章里面，默认提及的证书都是软件层面的，不涉及到硬件的。

CDP  
这个容器存储了被吊销的证书列表

## 0x05 窃取证书

在我们控的计算机上可能会存在一些证书，这些证书有可能是用客户端身份验证，有可能是CA证书，用以信任其他证书的。我们可以将这些证书导出来，这里我们分为两种情况导出来。

### 0x0501 从系统存储导出证书

这种情况我们使用windows自带的命令`certutil`来导出

`certutil`默认查看的是计算机证书，可以通过指定`-user`参数来查看用户证书

(图形化查看用户证书是命令是`certmgr.msc`，图形化查看计算机证书的命令是`certlm.msc`)

`certutil`还可以通过`-store`来查看存储分区，参数有`CA`,`root`,`My`分别对应`中间证书机构`,`个人证书`,`受信任的根证书颁发机构`。

有些证书在导入的时候需要密码或者勾选证书不可导出

![](https://image.3001.net/images/20210816/1629104539_611a299b7564acd4609ea.png!small)

这个时候就需要使用mimikatz来导出证书了。下面我们举两个导出的案例。

1、导出用户证书

打开`certmgr.msc`

![](https://image.3001.net/images/20210816/1629104541_611a299d77df838dcfc44.png!small)

如果我们想查看个人证书可以用

`certutil -user -store My`

![](https://image.3001.net/images/20210816/1629104543_611a299f88c80ba72e45d.png!small)

找到我们想导出的证书的hash

如果仅仅是只是导出证书，不导出私钥

`certutil -user -store My f95e6b5dbafac54963c450052848745a54ec7bd9
c:\Users\test1\Desktop]test1.cer`

![](https://image.3001.net/images/20210816/1629104546_611a29a274868462fcccf.png!small)

如果要导出证书包含私钥

`certutil -user -exportPFX f95e6b5dbafac54963c450052848745a54ec7bd9
c:\Users\test1\Desktop]test1.pfx`

这一步如果我们需要输入一个密码，这个密码是待会儿这个导出的证书 导入到咱们的电脑的时候要用的

![](https://image.3001.net/images/20210816/1629104549_611a29a571ae317681f0d.png!small)

2、查看计算机证书

打开`certlm.msc`

![](https://image.3001.net/images/20210816/1629104551_611a29a7b5012b187b1a4.png!small)

如果我们想查看计算机证书可以用

`certutil -store My`

![](https://image.3001.net/images/20210816/1629104553_611a29a9b6a650f04e39e.png!small)

找到我们想导出的证书的hash

`certutil -store My 888d67d9ef30adc94adf3336462b96b5add84af4
c:\Users\test1\Desktop\win10.cer`

![](https://image.3001.net/images/20210816/1629104557_611a29ad379aa2bec2979.png!small)

在我们要导出pfx文件的时候

![](https://image.3001.net/images/20210816/1629104561_611a29b19018b0f1ac967.png!small)

这种是勾选了证书不允许被导出的，certutil就导出不了，回过去看我们刚刚查看证书的hash的时候

![](https://image.3001.net/images/20210816/1629104564_611a29b4df4585fd7da65.png!small)

就可以看到，里面标志着私钥不能被导出，这个时候我们就需要用到mimikatz了,mimikatz的`crypto::certificates`默认也是不支持导出`私钥不能被导出`类型的证书的私钥】

![](https://image.3001.net/images/20210816/1629104567_611a29b78c5b3cecfea3f.png!small)

这个时候可以使用`crypto::capi`修改lsass

![](https://image.3001.net/images/20210816/1629104571_611a29bb1f80306954c4c.png!small)

然后就可以导出了

![](https://image.3001.net/images/20210816/1629104573_611a29bd11961533c7ac8.png!small)

### 0x0502 从文件系统搜索证书

我们经常可以在邮件，磁盘里面看到证书，我们一般按照后缀来搜索证书的，我们一般关注以下后缀

1、key后缀的，只包含私钥

2、crt/cer 后缀的，只包含公钥

3、csr后缀的，证书申请文件，不包含公钥，也不包含私钥。没啥用

4、pfx,pem,p12后缀的，包含公私钥，我们最喜欢的。

搜索文件后缀的每个人使用的工具不一样，我个人比较喜欢的是`SharpSearch`，.Net的项目，支持内存加载，可以写成CNA插件。

## 0x06 通过用户凭据申请可用于kerberos认证的证书

在所有默认的证书模板里面，我们最关注的模板默认有用户模板和计算机模板。

前面我们说过，使用认证进行kerberos认证的需要扩展权限里面包含以下其中一个

1、客户端身份认证

2、PKINIT 客户端身份验证

3、智能卡登录

4、任何目的

5、子CA

如果用户如果想要注册证书，需要经过两个权限的检验。

1、在CA上具有请求证书的权限，这个默认所有认证的用户都有请求证书的权限。

2、在模板上具有注册证书的权限。

用户/计算机模板，他刚好满足这些条件。

1、他们的扩展属性都有客户端身份认证

2、用户证书默认所有的域用户都有注册权限

![](https://image.3001.net/images/20210816/1629104575_611a29bfb13739921c8be.png!small)

3、计算机默认所有的域内计算机都有注册权限

![](https://image.3001.net/images/20210816/1629104577_611a29c1e4d6aca46febe.png!small)

4、用户/计算机模板不需要企业管理员批准

这两个默认的证书模板，让我们不需要有域管的凭据，只需要一个域内用户的凭据，就可以注册证书，这个证书还可用于进行kerberos认证。因此我们这里注册的时候选择的模板是用户/计算机模板(具体哪个模板看我们拥有的凭据是用户还是计算机)。

当我们拿到用户的凭据，想使用这个凭据去申请用户证书，我们可以

1、访问证书注册网页界面

这个咱们之前说过，需要安装证书颁发机构 Web
注册角色。我们可以尝试访问下，访问的路径是`https://CA/certsrv`，会弹401认证，我们输入用户的凭据就行。

![](https://image.3001.net/images/20210816/1629104579_611a29c34567015e14586.png!small)![](https://image.3001.net/images/20210816/1629104580_611a29c43282f9f4b94ad.png!small)

这个浏览器建议用IE

2、使用`certmgr.msc`申请

如果我们在域内，直接打开`certmgr.msc`申请就行

![](https://image.3001.net/images/20210816/1629104581_611a29c53203df72446aa.png!small)

![](https://image.3001.net/images/20210816/1629104582_611a29c65edfa483720c0.png!small)

![](https://image.3001.net/images/20210816/1629104583_611a29c7a05178fec1aad.png!small)

## 0x07 通过证书窃取用户凭据

### 0x0701 请求kerberos证书

在传统的kerberos认证的时候，是使用用户密码进行认证的。回顾下申请TGT的过程。

用用户hash加密时间戳作为value，type为PA-ENC-TIMESTAMP，
放在PA_DATA上。KDC收到请求，使用用户hash解密value的值得到时间戳跟当前时间做比对，如果在合理的范围(正常五分钟)，就认证通过。

事实上也可以使用证书作为认证，这也是这次spectorops关于ADCS研究的最大亮点，后面漏洞紧紧围绕这点。

RFC4556引入了对 Kerberos 预身份验证的公钥加密支持。这个RFC 的title是`Public Key Cryptography for
Initial Authentication in Kerberos`，后面我们使用简称PKINIT来介绍使用证书进行kerberos身份认证这种方法。

PKINIT同样也使用时间戳，但不是使用用户密码派生密钥加密消息，而是使用属于证书的私钥对消息进行签名。

我们可以使用rubeus 进行验证。

我们首先为用户Administrator注册一个证书，使用`certmgr.msc`进行注册

![](https://image.3001.net/images/20210816/1629104584_611a29c89f697a977f8f0.png!small)

然后导出来，记得跟私钥一起导出来

![](https://image.3001.net/images/20210816/1629104586_611a29ca0eb37ac45ac52.png!small)

接下来我们拿着这个证书去请求kerberos认证

    
    
    Rubeus4.0.exe asktgt /user:Administrator /certificate:administrator.pfx /domain:test16.local /dc:dc-05.test16.local
    

![](https://image.3001.net/images/20210816/1629104589_611a29cd97baaf2b37b64.png!small)

### 0x0703 请求NTLM 凭据

在微软的文档https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-pkca/4e5fb325-eabc-4fac-a0da-af2b6b4430cb里面有一段话

![](https://image.3001.net/images/20210816/1629104597_611a29d5ea51ce193f2c1.png!small)

也就是当使用证书进行kerberos认证的时候，返回的票据的PAC包里面还有NTLM票据。

这个东西Benjamin(mimikatz,kekeo作者)在17年已经研究并进行武器化

详情见https://twitter.com/gentilkiwi/status/826932815518371841

![](https://image.3001.net/images/20210816/1629104600_611a29d8d8b1165214727.png!small)

下面我们用一个案例来说明。

当我们控制了一台主机，里面有个用户的证书

![](https://image.3001.net/images/20210816/1629104605_611a29ddb8192d6739085.png!small)

我们使用`certutil`来导出证书(如果导出不了的话，就用mimikatz来导出证书)

![](https://image.3001.net/images/20210816/1629104607_611a29dfa4727eac94d6f.png!small)然后把pfx文件拷贝到我们自己的计算机，双击导入，输入刚刚我们输的密码。

我们本地的计算机做个代理进内网，并且把dns也代理进去(dns设置为内网的域控)

![](https://image.3001.net/images/20210816/1629104610_611a29e20cd447724929b.png!small)

使用kekeo获取用户的NTLM

![](https://image.3001.net/images/20210816/1629104610_611a29e2ed3c80568e850.png!small)

我们再做个测试，把用户的密码改了

![](https://image.3001.net/images/20210816/1629104612_611a29e41cf824bbc5dc9.png!small)

这个时候用之前获取的证书继续发起请求，还是能获取到NTLM Hash。

![](https://image.3001.net/images/20210816/1629104612_611a29e4eb90324850b6e.png!small)

## 0x08 引用

https://www.specterops.io/assets/resources/Certified_Pre-Owned.pdf

[ **https://forsenergy.com/zh-cn/certsvr/html/c8955f83-fed9-4a18-80ea-31e865435f73.htm**](https://forsenergy.com/zh-cn/certsvr/html/c8955f83-fed9-4a18-80ea-31e865435f73.htm)

[ **https://docs.microsoft.com/zh-cn/learn/modules/implement-manage-active-directory-certificate-services/**](https://docs.microsoft.com/zh-cn/learn/modules/implement-manage-active-directory-certificate-services/)

[ **https://forsenergy.com/zh-cn/certtmpl/html/85e1436e-4c52-489a-93a2-6603f1abadf7.htm**](https://forsenergy.com/zh-cn/certtmpl/html/85e1436e-4c52-489a-93a2-6603f1abadf7.htm)

[ **https://www.riskinsight-wavestone.com/en/2021/06/microsoft-adcs-abusing-pki-in-active-directory-environment/﻿**](https://www.riskinsight-wavestone.com/en/2021/06/microsoft-adcs-abusing-pki-in-active-directory-environment/)``

