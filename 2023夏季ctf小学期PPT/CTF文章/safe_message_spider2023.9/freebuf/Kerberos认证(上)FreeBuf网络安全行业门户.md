## Kerberos认证基本概念

> Kerberos起源于希腊神话，是一只守护者冥界的3头神犬

Kerberos 是一种由 MIT（麻省理工大学）提出的 **一种网络身份验证协议** 。
**它旨在通过使用密钥加密技术为客户端/服务器应用程序提供强身份验证** 。

Kerberos 主要是用在域环境下的身份认证协议。

## Kerberos认证过程(原理版)

### 基本概念(1)

 **1：Long-term Key** ：长时间保持不变的密钥( **不安全！**
因密钥长时间不变，所以一旦被破译则整个通信过程将被监听，网络传输中一般不使用Long-term Key)

 **2：Short-term Key/Session Key** ：只在一段时间内有效的密钥( **相对安全！**
密钥会随着Session或时间的改变而改变，即使有密钥失窃，仅会泄露一部分数据)

 **3：Master Key** ：用户密钥的Hash Code(为验证用户身份，将用户的密钥通过Hash算法生成唯一的散列值)

 **4：KDC** (Kerberos Distribution
Center)：Client与Server共同信任的第三方机构(类似于CA)，Kerberos的认证就是通过三方认证完成的

* * *

 **在Windows Domain(域)环境中:**

DC(Domain Controller)域控充当KDC

KDC维护存储着该Domain中所有账户的Account Database(由Active
Directory维护)，存储着所有每一个Account的名称和派生于该Account Password的Master Key(Hash Code)

* * *

### Kerbros认证整体流程

 **1：Client向KDC申请TGT**

—— **Authentication Service Exchange** ( **AS身份验证服务** )

 **2：Client通过获得的TGT向KDC申请用于访问Server的Ticket**

—— **Ticket Granting Service Exchange** ( **TGS票据发放服务** )

 **3：Client最终向Server提交Server为了验证自己(Client)身份的Ticket**

—— **Client/Server Exchange**

### 1：Client向KDC申请TGT

![此图像的alt属性为空；文件名为微信图片_20201119222226-1024x475.jpg](https://image.3001.net/images/20201121/1605931684_5fb892a4c25074d13395e.jpg!small)

#### 基本概念

 **1：TGS：** Ticket Grantng Service(票据发放服务)：为申请的Client提供TGT

 **2：TGT：** Ticket Granting Ticket(认证票据)："入场券"

#### 具体过程

1：首先 **Client携带账户信息**
向KDC的AS服务发起对TGT的申请(内容大致为"我需要一张TGT用以申请获取访问所有Server的Ticket")

2：KDC的AS服务在收到该申请后，生成一个用于该Client和KDC进行安全通信的Session Key (SKDC-Client)

3：为了保证 **该Session Key仅供该Client和自己(KDC)使用** ，KDC使用 **Client的Master
Key和自己的Master Key** 分别对该Session Key进行加密，从而获得两个不同Master Key加密的同一个Session
Key(SKDC-Client)的两个加密版本(对于使用 **KDC Master Key加密的SKDC-Client，随其一起加密的还有一些关于Client的信息(Client Info)** )

这份用KDC Mster Key加密的SKDC Client+Client Info就是TGT

4：之后， **KDC将两份加密的SKDC-Client都发给Client** (KDC不会保存用自己Master Key加密的那份SKDC-Client，否则若有多个Client则需要建立对照表，低效)

5： **Client收到** 这2个加密的SKDC-Client后，先使用自己的Master Key解密用自己Master Key加密的那份SKDC-Client，获得其中的SKDC-Client(Session Key)

6：随后Client **将Session Key(SKDC-Client)与TGT(用KDC Master Key加密的SKDC Key+Client
Info)缓存在本地**

### 2： **Client通过获得的TGT向KDC申请用于访问Server的Ticket**

![此图像的alt属性为空；文件名为微信图片_20201119232405-1024x442.jpg](https://image.3001.net/images/20201121/1605931691_5fb892abacf1d86f12fbb.jpg!small)

#### 基础概念

1：SKDC-Client是一个Session Key，有生命周期，与TGT相关联

2： **Session Key(SKDC-Client)过期—— >TGT自动宣告失败，需要重新向KDC申请**

3：SKDC-Client又称 Logon Session Key

 **4：Authenticator：** 具体包括Client Info+Timestamp(时间戳)

* * *

#### 为什么要加入Timestamp(时间戳)？

若不使用Timestamp， **可能出现中间人攻击(通过截获Client发给Server的报文，达到盗用'凭证'冒充Client的目的)**

#### 加入时间戳后的验证措施

在Authenticator中加入Timestamp后，Server 对 Authenticator中的Client Info与TGT中的Client
Info进行比较前，
**会先提取Authenticator中的Timestamp，并于当前时间进行比较，如果他们之间的偏差超出了一个可接受的时间范围(一般是5min)，Server会拒绝Client的请求**

#### Server端对时间戳的管理

>  **在Server端维持着一个列表，这个列表记录着这个可接受的时间范围内所有进行认证的Client和认证的时间**

对于时间偏差在这个可接受范围中的Client，Server会从这个列表中获取最近一个该Client的认证时间(由于SKDC-Client为Session
Key所以是short-term key，所以在Server的时间列表中会有一系列Session
Key的时间戳)，只有当Authentication中的Timestamp晚于
通过一个Client的最近的认证时间的情况下，Server才进行后续的验证流程

#### Time Synchronization 的重要性

> Timestamp只有在Client与Server时间同步的情况下，才有意义。

在一个Domain中， **一般通过访问同一个Time Server(时间同步服务器)获得当前时间的方式来实现时间同步**

* * *

#### 具体过程

1：Client获取到Session Key(SKDC-Client)与TGT

2： **生成Authenticator(Client Info与Timestamp)，以及要访问的Server的名称，并使用SKDC-Client加密，连同TGT** (使用KDC Master Key加密的SKDC-Client+Client Info) **一起发给KDC**

3： **KDC使用自己的Master key对TGT进行解密** ，提取其中的Client Info和Session Key(SKDC-Client)

4： **KDC使用SKDC-Client解密Autehnticator** ，获得Client Info

5： **比较两个Client Info** ，比较成功后生成一份基于Client要访问的Server的Ticket给Client

生成新的2个分别用Server Master加密的与用Client Master加密的Session Key(Session Key一样，加密的Master
Key不同)一并发给Client， **其中使用Server Master Key加密的那一份中，还要加上Client
Info，共同被加密后称为Ticket(票据)**

* * *

在这里还有一个问题， **为什么不将用Server Master Key加密的发给Server，将用Client Master
Key加密的发给Client** ，主要是为了：

1：若出现多个Client对一个Server的情况，则会加大Server的开销，Server不得不为每一个Client对应的Session
Key建立一个表项

2：防止异步问题，若Client端的Session
Key到达了，但Master端的丢失了，即使Client端用该Session加密，Server端也不会识别

* * *

 **Ticket是基于某个具体Server的，而TGT和具体的Server无关**
。Client可以使用一个TGT从KDC获得基于不同Server的Ticket

* * *

###  **3：Client最终向Server提交Server验证自己(Client)身份的Ticket**

![此图像的alt属性为空；文件名为微信图片_20201119234119-1024x431.jpg](https://image.3001.net/images/20201121/1605931694_5fb892aed850d64557c6f.jpg!small)

#### 具体过程

1：上一步中最后由KDC生成新的加密的Sserver Session Key， **所以Client首先对加密的Sserver Session
Key进行解密，获得Session Key**

2： **创建Authenticator(Client Info+Timestamp)** ，并用Sserver Session Key对其加密

3： **将Authenticator连同从KDC获得的Ticket** (用Server Master加密的Sserver Session
Key+Client Info)， **一并发到Server端**

4： **Server端收到后，首先用自己的Master Key解密Ticket** ，获得 Sserver Session Key 与 Client
Info

5：随后 **用Sserver Session Key解密Authenticator**

6：通过 **比较Authenticator中与Ticket中的Client Info** ，一样则Server对Client认证完毕

7：若Client也要对Server进行认证 **(Kerberos支持双向认证 Mutual Authenticator**
)，则需要在前面向Server的凭证中设置一个需要认证的Flag位，设置后，Server在对Client认证成功后，会将Authticator中的Timestamp提取出来，用Sserver
Session Key加密，Client经解密，若与原来的一致，则Client对Server认证成功

  

