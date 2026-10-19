## 一、漏洞概述

**2019年6月，Microsoft发布了一条安全更新。该更新针对CVE-2019-1040漏洞进行修复。此次漏洞，攻击者可以通过中间人攻击，绕过NTLM
MIC（消息完整性检查）保护，将身份验证流量中继到目标服务器。 通过这种攻击使得攻击者在仅有一个普通域账号的情况下可以远程控制 Windows
域内的任何机器，包括域控服务器。**

## 二、漏洞利用

### 攻击方式一：Exchange

 **验证环境：**

**角色** | **系统版本** | **计算机名** | **地址** | **域**  
---|---|---|---|---  
Attacker | Ubuntu Server 18.04 | ubuntu | 192.168.123.69 |  
DC | Windows Server 2012 R2 | topsec-dc | 192.168.123.150 | test.local  
Exchange | Windows Server 2012 R2 | topsec | 192.168.123.143 | test.local  
  
**验证过程：**

① 环境搭建

> 安装配置域控制器
>
> 安装配置Exchange Server，参考[1]
>
> 在域中新建一个用于测试的账户test

②执行ntlmrelayx.py脚本进行NTLM中继攻击，设置SMB服务器并将认证凭据中继到LDAP协议。其中--remove-mic选项用于清除MIC标志，--escalate-user用于提升指定用户权限。
![1.png](https://image.3001.net/images/20190702/1562049337_5d1afb390ebb0.png!small)③
执行printerbug.py脚本，触发SpoolService的bug。
![2.png](https://image.3001.net/images/20190702/1562049345_5d1afb4199970.png!small)④
SpoolService的bug导致Exchange服务器回连到ntlmrelayx.py，即将认证信息发送到ntlmrelayx.py。可以在下图中看到认证用户是TEST\TOPSEC$。
![3.png](https://image.3001.net/images/20190702/1562049353_5d1afb4913029.png!small)接着ntlmrelayx.py开始执行LDAP攻击，加上-debug选项后可以看到更详细的信息。
首先，通过遍历验证中继帐户所在用户组及权限，发现当前账户可以创建用户、可以修改test.local域的ACL，因为域中的Exchange Windows
Permissions用户组被允许修改ACL，如下图所示：
![4.png](https://image.3001.net/images/20190702/1562049362_5d1afb5240201.png!small)该用户组下的成员正是中继的计算机账户TOPSEC：
![5.png](https://image.3001.net/images/20190702/1562049373_5d1afb5d21fdd.png!small)因此脚本会首选修改ACL来提权，因为这相比创建用户的方式更隐秘一些。具体方式是通过LDAP修改域的安全描述符（Security
Descriptor），可以在下面的数据包中看到ACL中每一条具体的访问控制条目（ACE，Access Control Entries）：
![6.png](https://image.3001.net/images/20190702/1562049379_5d1afb63cfeed.png!small)⑤
完成ACL的修改后，test就可以通过secretsdump.py的DCSync功能dump出所有密码哈希值：
![7.png](https://image.3001.net/images/20190702/1562049401_5d1afb79ceadf.png!small)

### 攻击方式二：Kerberos委派

 **验证环境：**

**角色** | **系统版本** | **计算机名** | **地址** | **域**  
---|---|---|---|---  
Attacker | Ubuntu Server 18.04 | ubuntu | 192.168.123.69 |  
DC | Windows Server 2012 R2 | topsec-dc | 192.168.123.212 | test.local  
SDC | Windows Server 2012 R2 | topsec | 192.168.123.62 | test.local  
  
**验证过程：** ① 环境搭建

> 安装配置域控制器，同时开启LDAPS支持，因为该攻击方式需要添加新的计算机账户，必须在LDAPS进行。开启方法参考[2]
>
> 安装配置辅助域控制器，方法参考[3]
>
> 在域中新建一个用于测试的账户topsec，一个域管理员admin

② 和攻击方式一相同，执行ntlmrelayx.py本，使用--delegate-access选项，delegate-access选项将中继计算机帐户（这里即辅助域控制器）的访问权限委托给attacker。
![8.png](https://image.3001.net/images/20190702/1562049414_5d1afb86a5a3e.png!small)③
attacker对辅助域控制器(SDC)执行printerbug.py脚本
![9.png](https://image.3001.net/images/20190702/1562049422_5d1afb8e69a1b.png!small)③
printerbug.py脚本执行成功后，将触发辅助域控制器(SDC)回连Attacker主机，回连使用的认证用户是辅助域控制器(SDC)本地计算机账户TEST/TOPSEC$。
ntlmrelayx.py通过ldaps将该用户账户中继到域控服务器(DC)，因为这种攻击方式下所冒用的身份TEST/TOPSEC$并不在Exchange
Windows Permissions组内，不具有修改ACL权限，但是可以通过此身份在DC上添加一个新计算机账户（下图中EJETBTTB$）,
并修改其约束委派授权，授予它对受害计算机（辅助域控制器）的委派权限。
![10.png](https://image.3001.net/images/20190702/1562049436_5d1afb9ce12f7.png!small)![11.png](https://image.3001.net/images/20190702/1562049446_5d1afba6a6811.png!small)④使用getSP.py脚本，通过-impersonate参数模拟用户admin请求其票证，保存为ccache，admin用户为Domain
Admins组的成员，具有对辅助域控制器(SDC)的管理与访问权限。
![12.png](https://image.3001.net/images/20190705/15623133355524.png!small) ⑤
使用上一步骤中保存的Kerberos服务票证，我们可以在目标主机(SDC)上模拟admin身份，从而执行任何操作，例如使用secretsdump转储哈希值。通过secretsdump
dump出所有密码哈希值：
![13.png](https://image.3001.net/images/20190702/1562049462_5d1afbb6bc2c7.png!small)

## 三、漏洞细节

此次的攻击流程有如下两个方式：

>
> Exchange攻击流程：使用任何AD帐户，通过SMB连接到目标Exchange服务器，并触发SpoolService错误。目标服务器将通过SMB回连至攻击者主机，使用ntlmrelayx将SMB身份验证中继到LDAP。使用中继的LDAP身份验证，为攻击者帐户授予DCSync权限。攻击者帐户使用DCSync转储AD中的所有密码哈希值。

>
> Kerberos委派攻击流程：使用任何AD帐户，通过SMB连接到目标服务器，并触发SpoolService错误。目标服务器将通过SMB回连至攻击者主机，使用ntlmrelayx将SMB身份验证中继到LDAP。使用中继的LDAP身份验证，将目标服务器的基于资源的约束委派权限授予攻击者控制下的计算机帐户。攻击者作为受害者服务器上的任何用户进行身份验证。

### Exchange攻击流程

下文出现的攻击流量图中,个角色与ip对应关系同上文验证环境搭建：

**角色** | **系统版本** | **计算机名** | **地址** | **域**  
---|---|---|---|---  
Attacker | Ubuntu Server 18.04 | ubuntu | 192.168.123.69 |  
DC | Windows Server 2012 R2 | topsec-dc | 192.168.123.150 | test.local  
Exchange | Windows Server 2012 R2 | topsec | 192.168.123.143 | test.local  
  
下文标题内容，即为攻击流程，对应流程图中红框所示的流程 如果对SMB协议不是很清楚的读者，可以先参考技术点分析-客户端与服务器端的SMB通信一节内容

 **1\. attacker使用普通AD账户登陆Exchange**

在攻击的开始阶段，attacker需要确保拥有一个可使用的AD账号，这是满足触发SpoolService错误的必要条件。
首先attacker利用已拥有的AD账号，连接到远程服务器的打印服务（spoolsv.exe），下图是Attacker通过SMB2协议登陆Exchange流程和流量：
![14.png](https://image.3001.net/images/20190702/1562049477_5d1afbc5b3425.png!small)![15.png](https://image.3001.net/images/20190702/1562049488_5d1afbd021987.png!small)成功的通过该阶段，就可以请求对一个新的打印作业进行更新，令其将该通知发送给指定目标。

 **2\. 触发SpoolService错误**

attacker通过Printerbug脚本，触发Exchange服务器SpoolService错误，强制Exchange服务器通过MS-RPRN
RPC接口向attacker进行身份验证。具体细节见 **技术点分析** 一章中的 **SpoolService/printer bug**
。下图是Attacker触发SpoolService错误payload流程和流量：
![16.png](https://image.3001.net/images/20190702/1562049497_5d1afbd9c89b6.png!small)![17.png](https://image.3001.net/images/20190702/1562049504_5d1afbe00aa13.png!small)

**3\. Exchange主机向Attacker发送Negotiate Protocol Request**

在触发SpoolService错误后，Exchange服务器向Attacker进行身份验证，即发送Negotiate Protocol
Request，这是客户端向服务器发送第一个SMB请求，可参考 **技术点分析-客户端与服务器端的SMB通信**
。下图是Exchange向Attacker发送SMB协商请求流程和流量：
![18.png](https://image.3001.net/images/20190702/1562049516_5d1afbec77e11.png!small)![19.png](https://image.3001.net/images/20190702/1562049526_5d1afbf6b0bc7.png!small)在正常的业务场景中，用户想登陆并使用Exchange，往往需要向Exchange服务器发送SMB协商请求流量，以便验证身份并登陆。但由于SpoolService错误，在这里，Exchange向Attacker发送SMB协商请求流量，以便验证身份。这便造成了Attacker可以作为中间人身份中继此身份认证以冒充Exchange欺骗DC的机会。

 **4\. Attacker将协商请求通过ldap中继到DC服务器**

Attacker作为中间人，将Negotiate Protocol Request通过ldap请求中继到ad服务器
在此步骤以及以下攻击流程中，有需要将SMB身份验证通过LDAP中继至DC的环节。由于NTLM协议的工作方式，无法将SMB流量直接通过LDAP中继，因此需要对流量进行修改，而需改流量，势必需要绕过MIC验证，此处便是本次漏洞的重点，详情见
**技术点分析-MIC校验绕过**
部分。![20.png](https://image.3001.net/images/20190702/1562049542_5d1afc06e225b.png!small)![21.png](https://image.3001.net/images/20190702/1562049551_5d1afc0fe5f95.png!small)

 **5\. attacker向Exchange发送Negotiate Protocol Response**
![22.png](https://image.3001.net/images/20190702/1562049568_5d1afc20432bc.png!small)![23.png](https://image.3001.net/images/20190702/1562049577_5d1afc293506c.png!small)

**6\. Exchange向attacker发送Session Setup Request**
![24.png](https://image.3001.net/images/20190702/1562049603_5d1afc43cac49.png!small)![25.png](https://image.3001.net/images/20190702/1562049612_5d1afc4c6e2f5.png!small)

**7\. Attacker向DC中继Session Setup Request**

Attacker将Exchange发送来的Session Setup Request 中继给DC， DC将包含
CHALLENGE的Response发送给Attacker。![26.png](https://image.3001.net/images/20190702/1562049622_5d1afc560c0f6.png!small)![27.png](https://image.3001.net/images/20190702/1562049631_5d1afc5f06f13.png!small)

 **8\. Attacker 向exchange发送Session Setup Response（CHALLENGE）**

Attacker 将DC发出的包含challenge的Session Setup
Response发送给exchange。![28.png](https://image.3001.net/images/20190702/1562049648_5d1afc7049341.png!small)
![29.png](https://image.3001.net/images/20190702/1562049657_5d1afc794f45c.png!small)

**9\. exchange向Attacker发送包含了身份验证请求的Session Setup**
![30.png](https://image.3001.net/images/20190702/1562049672_5d1afc88505c7.png!small)![31.png](https://image.3001.net/images/20190702/1562049682_5d1afc927e614.png!small)我们可以看到上图中的认证用户为TEST\TOPSEC$，而不是运行Exchange的SYSTEM账户，这是因为SYSTEM账户具有太高权限，如果用此帐户对网络资源进行身份验证，则会出现安全问题。所以当访问网络资源时，使用本地计算机的网络帐户对网络进行身份验（形式为domain\computername$，即TEST\TOPSEC$）。
Exchange收到challenge后，向attacker发送包含了身份验证请求的Session Setup流量。

 **10\. Attacker向 DC中继含有Exchange的身份认证的Session Setup Request**

Attacker将身份认证请求中继到DC，并使用Exchange的身份认证通过DC认证
![32.png](https://image.3001.net/images/20190702/1562049694_5d1afc9e9160b.png!small)![33.png](https://image.3001.net/images/20190702/1562049706_5d1afcaa592ef.png!small)DC认证通过Exchange身份，并向Attcker发送认证通过的Response，此时，DC对Attacker的身份验证结束，Attacker成功冒用Exchange身份。
由于安装Exchange后，Exchange在Active
Directory域中具有高权限，Exchange的本地计算机账户TOPSEC$会被加入用户组Exchange Trusted
Subsystem，该用户组又隶属于Exchange Windows Permissions。Exchange Windows
Permissions组可以通过WriteDacl方式访问Active
Directory中的Domain对象，该对象允许该组的任何成员修改域权限，从而可以修改当前域ACL达到提权目的。
使用提权后的用户或计算机可以执行域控制器通常用于复制的同步操作，这允许攻击者同步Active Directory中用户的所有哈希密码。
![34.png](https://image.3001.net/images/20190702/1562049718_5d1afcb60be52.png!small)

### Kerberos委派攻击流程

下文出现的攻击流量图中,个角色与ip对应关系同上文验证环境搭建：

**角色** | **系统版本** | **计算机名** | **地址** | **域**  
---|---|---|---|---  
Attacker | Ubuntu Server 18.04 | ubuntu | 192.168.123.69 |  
DC | Windows Server 2012 R2 | topsec-dc | 192.168.123.212 | test.local  
SDC | Windows Server 2012 R2 | topsec | 192.168.123.62 | test.local  
  
Kerberos委派攻击流程与Exchange攻击利用，在DC对Attacker的身份验证结束之前的阶段是类似的。区别在于后续提权过程，下面介绍下Kerberos委派攻击后续攻击流程。
在Attacker冒用SDC身份后，由于SDC计算机身份没有修改访问控制列表(ACL)的权限，无法直接提权。而后续提权利用中的S4U2Self不适用于没有SPN的帐户。在域环境中，任何域用户都可以通过MachineAccountQuota创建新的计算机帐户，并为其设置SPN。Attacker通过此方式新建一个域中的计算机账号。这一过程通过LDAP实现并设置账户与密码
，如下图
![35.png](https://image.3001.net/images/20190702/1562049729_5d1afcc1ab4fb.png!small)![36.png](https://image.3001.net/images/20190702/1562049736_5d1afcc8d82db.png!small)
![37.png](https://image.3001.net/images/20190702/1562049750_5d1afcd627bbf.png!small)DC上可见computers列表中新创建的名为EJETBTTB的计算机：
![38.png](https://image.3001.net/images/20190702/1562049763_5d1afce396c1d.png!small)在域中新的计算机账户EJETBTTB(下图中的service
A)建立成功后，后续攻击如下图攻击步骤
![39.png](https://image.3001.net/images/20190702/1562049778_5d1afcf29fbaf.png!small)

**1\. 攻击者为Service A配置了基于资源的约束委派**

由于通过S4U2Self请求到的TGS forwardable标志位为 Non-forwardable,这意味着该TGS服务票据是不可转发的，不可以在接下来的S4U2Proxy中进行转发。但是不可转发的TGS竟然可以用于基于资源的约束委派，S4U2Proxy会接收这张不可转发的TGS。由于我们拥有Service
A的计算机账号以及密码，所以在这里可以为Service A到SDC配置了基于资源的约束委派，将默认的约束委派更改为基于资源的约束委派，以便后续攻击。

 **2\. Service A 调用S4U2Self向认证服务器(SDC)为admin请求访问自身的服务票据**
![40.png](https://image.3001.net/images/20190702/1562049790_5d1afcfe3840c.png!small)通过国外安全研究员Elad
Shami的研究可知，无论服务账号的UserAccountControl属性是否被设为TrustedToAuthForDelegation，
服务自身都可以调用S4U2Self为任意用户请求访问自己的服务票据，也就是说，这里Service A
可以调用S4U2Self向SDC为admin用户申请可访问自身的服务票据。

 **3\. SDC将为admin用户申请的访问Service A的TGS发送给Service
A**![41.png](https://image.3001.net/images/20190702/1562049799_5d1afd07a0209.png!small)

 **4、 Service A通过S4U2Proxy
转发TGS，并为admin申请访问SDC票据**![42.png](https://image.3001.net/images/20190702/1562049812_5d1afd1410670.png!small)

 **5、SDC将为admin用户申请的访问SDC的TGS发送给Service A**

在这里，Service A为Attacker创建并控制，Attacker获得TGS票据，利用该票据以admin身份访问SDC，完成提权
![43.png](https://image.3001.net/images/20190702/1562049819_5d1afd1bb91e0.png!small)

### 技术点分析

在理清利用流程后，接下来详解利用流程中的技术点。

 **客户端与服务器端的SMB通信**

补充介绍一些关于SMB通信协议相关内容，通过这部分内容，可以加深对的漏洞流程的理解。对SMB通信协议熟悉的读者，可以跳过此部分。
下图是客户端与服务器端的SMB通信流程：
![44.png](https://image.3001.net/images/20190702/1562049826_5d1afd22a2b5b.png!small)

**SMB2 / Negotiate Protocol** Negotiate
Protocol是在SMB2的任何新TCP会话上发出的第一个SMB2命令，它用于协商要使用的协议版本。Negotiate
Protocol命令分为Negotiate Protocol Request/ Negotiate Protocol Response两部分：

Negotiate Protocol Request： 客户端向服务器发送第一个SMB请求：“Negotiate Protocol
Request”。这个请求包含了客户端所支持的各种 SMB Dialect。

Negotiate Protocol Response: 服务器收到该请求后，选择一个它支持的最新版本（比如NTLM 0.12），再通过“Negotiate
Protocol Response”回复给客户端。

 **SMB2 / Session Setup** SMB2 / Session
Setup命令用于对用户进行身份验证并获取分配的UserID。此命令通常是SMB2 / Negotiate
Protocol阶段完成后从客户端发出的第一个命令。Session Setup分为两部分：

Session Setup Request: Negotiate
Protocol阶段结束之后，，客户端请求和服务器建立一个session，在客户端发送的Session Setup Request里，包含了身份验证请求。

Session Setup Response: 服务器回复是否通过验证。

 **SpoolService/printer bug**

在攻击利用流程中，需要使用到一个名为printerbug.py的工具，此工具触发SpoolService/printer
bug，强制Windows主机通过MS-RPRN RPC接口向攻击者进行身份验证。 Windows的MS-RPRN协议用于打印客户机和打印服务器之间的通信，默认情况下是启用的。协议定义的RpcRemoteFindFirstPrinterChangeNotificationEx()调用创建一个远程更改通知对象，该对象监视对打印机对象的更改，并将更改通知发送到打印客户端。

任何经过身份验证的域成员都可以连接到远程服务器的打印服务（spoolsv.exe），并请求对一个新的打印作业进行更新，令其将该通知发送给指定目标。之后它会将立即测试该连接，即向指定目标进行身份验证（攻击者可以选择通过Kerberos或NTLM进行验证）。另外微软表示这个bug是系统设计特点，无需修复。
![45.png](https://image.3001.net/images/20190702/1562049835_5d1afd2b15ba2.png!small)在本次漏洞的利用过程中，我们通过printerbug.py脚本触发了上述bug，强制Exchange服务器对攻击者（192.168.123.69）发起身份验证，而Exchange默认是以SYSTEM身份执行的。
![46.png](https://image.3001.net/images/20190702/1562049842_5d1afd320032e.png!small)下图是printerbug.py执行后的数据包：
![47.png](https://image.3001.net/images/20190702/1562049847_5d1afd37775f5.png!small)

第一次身份验证由攻击者向exchange服务器发起，以便可以远程连接到Spoolsv服务，可以看到使用的账号是一个普通的域成员账号test；

接着，printerbug.py脚本中调用RpcRemoteFindFirstPrinterChangeNotificationEx()，请求对一个新的打印作业进行更新，并令其将该通知发送给我们指定的attackerhost（192.168.123.69）。这部分数据就是上图中Encrypted
SMB3中的一部分。
![48.png](https://image.3001.net/images/20190702/1562049854_5d1afd3ef32f0.png!small)

第二次身份验证便是使Exchange向attackerhost（192.168.123.69）发起的身份验证，用户为TEST\TOPSEC$，（不是SYSTEM的原因是：如果本地服务使用SYSTEM帐户访问网络资源，则使用本地计算机的网络帐户domain\computername$对网络进行身份验证）

 **SMB中继LDAP思路以及难点**

在攻击利用流程中，需要将SMB身份验证通过LDAP中继至DC，由于NTLM协议的工作方式，无法将SMB流量直接通过LDAP中继，将SMB流量通过LDAP中继难点以及绕过思路如下：

默认情况下，SMB中的NTLM身份验证:NEGOTIATE_SIGN为set状态
![49.png](https://image.3001.net/images/20190702/1562049902_5d1afd6e0efbc.png!small)

将此SMB流量中继到LDAP时，由于此时的Negotiate
Sign设置为set，该标志会触发LDAP签名，而此SMB流量为Attacker从Exchange服务器上中继而来，无法通过LDAP的签名校验，从而被LDAP忽略，导致攻击失败

为了防止攻击失败，需要将NEGOTIATE_SIGN设置为Not set

MIC保护不被篡改，如果简单的改包，将NEGOTIATE_SIGN设置Not set，将会导致MIC校验不通过

需要寻找一种可以绕过MIC校验的方式，以便更改包中的值

在绕过MIC校验之后，更改NEGOTIATE_SIGN值为Not set，使得在不触发LDAP签名校验的情况下，将SMB中继LDAP

 **MIC校验**

NTLM身份验证由3种消息类型组成：

> NTLM_NEGOTIATE
>
> NTLM_CHALLENGE
>
> NTLM_AUTHENTICATE

分别对应位于SMB协议中的SessionSetup阶段，下图就是Clinet与Server交互流程图和流量：
![50.png](https://image.3001.net/images/20190702/1562049912_5d1afd7819fc5.png!small)![51.png](https://image.3001.net/images/20190702/1562049923_5d1afd8301916.png!small)
![52.png](https://image.3001.net/images/20190702/1562049940_5d1afd94ef511.png!small)

为了确保恶意行为者不在传输过程中处理消息，在NTLM_AUTHENTICATE消息中添加了一个额外的MIC（消息完整性代码）字段，如下图所示：
![53.png](https://image.3001.net/images/20190702/1562049952_5d1afda0509f9.png!small)MIC是使用会话密钥应用于所有3个NTLM消息的串联的HMAC_MD5，该会话密钥仅对启动认证的帐户和目标服务器是已知的。因此，试图篡改其中一条消息的攻击者（例如，修改签名协商）将无法生成相应的MIC，这将导致攻击失败。

 **MIC校验绕过**

Microsoft服务器允许无MIC 的NTLM_AUTHENTICATE消息。 如果想要将SMB身份验证中继到LDAP，并完成中继攻击，可以通过如下步骤：
取消MIC校验以确保可以修改数据包中的内容：

从NTLM_AUTHENTICATE消息中删除MIC

从NTLM_AUTHENTICATE消息中删除版本字段（删除MIC字段而不删除版本字段将导致错误）。

 **LDAP签名绕过**

在绕过MIC校验之后，可以修改NEGOTIATE_SIGN值以便将SMB流量顺利通过LDAP签名校验 将NEGOTIATE_SIGN设置为not
set以绕过LDAP验证

取消设置NTLM_NEGOTIATE消息中的签名标志

> NTLMSSP_NEGOTIATE_ALWAYS_SIGN
>
> NTLMSSP_NEGOTIATE_SIGN

取消设置NTLM_AUTHENTICATE消息中的以下标志：

> NTLMSSP_NEGOTIATE_ALWAYS_SIGN
>
> NTLMSSP_NEGOTIATE_SIGN
>
> NEGOTIATE_KEY_EXCHANGE
>
> NEGOTIATE_VERSION

 **SMB中继LDAP流程**

为了实现SMB中继LDAP流程，这里使用ntlmrelayx.py工具作为中继
![54.png](https://image.3001.net/images/20190702/1562049963_5d1afdab20664.png!small)Ntlmrelayx中继流程如下：

取消设置NTLM_NEGOTIATE消息中的签名标志（NTLMSSP_NEGOTIATE_ALWAYS_SIGN，NTLMSSP_NEGOTIATE_SIGN）
![55.png](https://image.3001.net/images/20190702/1562049974_5d1afdb6381d2.png!small)Exchange向Attacker发送NTLMSSP_NEGOTIATE包内容：
![56.png](https://image.3001.net/images/20190702/1562049985_5d1afdc117d7c.png!small)Attacker将NTLMSSP_NEGOTIATE通过LDAP中继到DC包内容：
![57.png](https://image.3001.net/images/20190702/1562049994_5d1afdcad9c3a.png!small)可见，在通过LDAP中继时，已经取消设置NTLM_NEGOTIATE消息中的签名标志（NTLMSSP_NEGOTIATE_ALWAYS_SIGN，NTLMSSP_NEGOTIATE_SIGN）

从NTLM_AUTHENTICATE消息中删除MIC以及版本字段
![58.png](https://image.3001.net/images/20190702/1562050004_5d1afdd428bd2.png!small)Exchange向Attacker发送NTLMSSP_AUTH：
![59.png](https://image.3001.net/images/20190702/1562050012_5d1afddc9b56f.png!small)Attacker将NTLMSSP_AUTH通过LDAP中继到DC：
![60.png](https://image.3001.net/images/20190702/1562050019_5d1afde3f0838.png!small)在通过LDAP中继时，NTLM_AUTHENTICATE消息中MIC以及版本字段已被删除。

取消设置NTLM_AUTHENTICATE消息中的以下标志：NTLMSSP_NEGOTIATE_ALWAYS_SIGN，NTLMSSP_NEGOTIATE_SIGN，NEGOTIATE_KEY_EXCHANGE，NEGOTIATE_VERSION。![63.png](https://image.3001.net/images/20190702/1562050074_5d1afe1a8123c.png!small)Exchange向Attacker发送NTLMSSP_AUTH包内容：
![61.png](https://image.3001.net/images/20190702/1562050036_5d1afdf4f2e23.png!small)Attacker将NTLMSSP_AUTH通过LDAP中继到DC包内容：
![62.png](https://image.3001.net/images/20190702/1562050049_5d1afe011dd86.png!small)在通过LDAP中继时，
NTLM_AUTHENTICATE消息中的以下标志：NTLMSSP_NEGOTIATE_ALWAYS_SIGN，NTLMSSP_NEGOTIATE_SIGN，NEGOTIATE_KEY_EXCHANGE，NEGOTIATE_VERSION已经被设置为‘NOT
set’。

## 参考链接

> [1] [Exchange Server 2013
> 一步步安装图解](https://www.cnblogs.com/jianyus/p/3170732.html)
>
> [2] [Enable LDAP over SSL (LDAPS) for Microsoft Active Directory
> servers](https://gist.github.com/magnetikonline/0ccdabfec58eb1929c997d22e7341e45)
>
> [3] [Windows Server 2012 R2 辅助域控制器搭建](http://www.mamicode.com/info-> detail-2275954.html)
>
> [4] [滥用基于资源约束委派来攻击Active
> Directory](https://www.cnblogs.com/backlion/p/10537813.html)
>
> [5] [Abusing S4U2Self: Another Sneaky Active Directory
> Persistence](https://alsid.com/company/news/abusing-s4u2self-another-sneaky-> active-directory-persistence)
>
> [6] [利用CVE-2019-1040 - 结合RCE和Domain
> Admin的中继漏洞](https://dirkjanm.io/exploiting-CVE-2019-1040-relay-> vulnerabilities-for-rce-and-domain-admin/)
>
> [7] [滥用Exchange：远离域管理员的一个API调用](https://dirkjanm.io/abusing-exchange-one-> api-call-away-from-domain-admin/)
>
> [8] [The SYSTEM
> Account](https://wiki.samba.org/index.php/The_SYSTEM_Account)
>
> [9] [Wagging the Dog: Abusing Resource-Based Constrained Delegation to
> Attack Active Directory](https://shenaniganslabs.io/2019/01/28/Wagging-the-> Dog.html#generic-dacl-abuse)

 ***本文作者：alphalab，转载请注明来自FreeBuf.COM**

