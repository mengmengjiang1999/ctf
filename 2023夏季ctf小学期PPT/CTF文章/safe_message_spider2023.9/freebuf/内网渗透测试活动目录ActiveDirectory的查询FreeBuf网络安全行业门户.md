![active-directory-monitoring](https://image.3001.net/images/20210806/1628258142_610d3f5e7882e407b6932.png!small)

## 前言

这又是一个关于域内基础概念与原理的系列，本系列将包含以下几篇文章：

> 《内网渗透测试：内网环境与活动目录基础概念》
>
> 《内网渗透测试：活动目录 Active Directory 的查询》
>
> 《内网渗透测试：域用户组及域内权限划分》
>
> 《内网渗透测试：OU 组织单位》
>
> 《内网渗透测试：域用户和机器用户》
>
> 《内网渗透测试：域内权限访问控制》
>
> 《内网渗透测试：Windows 令牌窃取》
>
> 《内网渗透测试：Windows 组策略讲解》
>
> 《内网渗透测试：Windows 组策略后门》

在上一节中，我们介绍了活动目录 Active Directory 的一些基本概念，活动目录中存储了域内的大部分信息，域内的每一台域控都有一份完整的本域的
Active Directory，我们可以通过连接域控的指定端口（636端口是LDAPS）来进行访问、查询与修改。

## Active Directory 的查询基础语法

### BaseDN

BaseDN 即基础可分辨名称，其指定了这棵树的根。比如指定 BaseDN
为`DC=whoamianony,DC=org`就是以`DC=whoamianony,DC=org`为根往下搜索，类似于在文件系统中指定了一个根目录：

![image-20210721224104515](https://image.3001.net/images/20210806/1628258142_610d3f5ec098112bbf39c.png!small)

若指定 BaseDN
为`CN=Computers,DC=whoamianony,DC=org`那么就是以`CN=Computers,DC=whoamianony,DC=org`为根往下搜索

### 过滤规则

LDAP 搜索过滤器语法有以下逻辑运算符：

运算符| 说明  
---|---  
&| AND 运算符  
|| OR 运算符  
!| NOT 运算符  
=| 用与名称和值做相等比较  
*| 通配符  
  
下面举几个例子

> `(uid=testuser)`：匹配 uid 属性为 testuser 的所有对象
>
> `(uid=test*)`：匹配 uid 属性以 test 开头的所有对象
>
> `(!(uid=test*))`：匹配 uid 属性不以 test 开头的所有对象
>
> `(&(department=1234)(city=Paris))`：匹配 department 属性为1234且city属性为Paris的所有对象
>
> `(|(department=1234)(department=56*))`：匹配 department
> 属性的值刚好为1234或者以56开头的所有对象。

一个需要注意的点就是运算符是放在前面的，跟我们之前常规思维的放在中间不一样。

### LDAP 查找中的按位搜索

在 LDAP 里面，有些属性字段是位字段，这里以 userAccountControl 举例，其记录了用户的 AD
账号的很多属性信息，该字段就是一个的位字段。之所以说 userAccountControl 是一个位字段，是因为它是由一个个位构成：

Property flag| Value in hexadecimal| Value in decimal  
---|---|---  
SCRIPT| 0x0001| 1  
ACCOUNTDISABLE| 0x0002| 2  
HOMEDIR_REQUIRED| 0x0008| 8  
LOCKOUT| 0x0010| 16  
PASSWD_NOTREQD| 0x0020| 32  
PASSWD_CANT_CHANGE| 0x0040| 64  
ENCRYPTED_TEXT_PWD_ALLOWED| 0x0080| 128  
TEMP_DUPLICATE_ACCOUNT| 0x0100| 256  
NORMAL_ACCOUNT| 0x0200| 512  
INTERDOMAIN_TRUST_ACCOUNT| 0x0800| 2048  
WORKSTATION_TRUST_ACCOUNT| 0x1000| 4096  
SERVER_TRUST_ACCOUNT| 0x2000| 8192  
DONT_EXPIRE_PASSWORD| 0x10000| 65536  
MNS_LOGON_ACCOUNT| 0x20000| 131072  
SMARTCARD_REQUIRED| 0x40000| 262144  
TRUSTED_FOR_DELEGATION| 0x80000| 524288  
NOT_DELEGATED| 0x100000| 1048576  
USE_DES_KEY_ONLY| 0x200000| 2097152  
DONT_REQ_PREAUTH| 0x400000| 4194304  
PASSWORD_EXPIRED| 0x800000| 8388608  
TRUSTED_TO_AUTH_FOR_DELEGATION| 0x1000000| 16777216  
  
比如一个账户，他的 userAccountControl 属性只有 LOCKOUT 和 NOT_DELEGATED
这两个位有值，其他的位都没有，那这个用户的 userAccountControl 属性的值就为 0x100000+0x0010，是个32 位 INT 类型。

现在，如果我要搜索域内所有设置了 NOT_DELEGATED 位的所有对象，那么像之前那样简单的 LDAP 搜索语法肯定是不行了。因为简单的 LDAP
搜索语法只能对某个属性进行过滤，还不能对属性里面的某个具体的位进行过滤，这就引出了 LDAP 的按位搜索。

LDAP 的按位搜索的语法如下：

    
    
    <属性名称>:<BitFilterRule-ID>:=<十进制比较值>

其中的`<BitFilterRule-ID>`指的是位过滤规则所对应的 ID，大致内容如下：

位过滤规则| OID  
---|---  
LDAP_MATCHING_RULE_BIT_AND| 1.2.840.113556.1.4.803  
LDAP_MATCHING_RULE_OR| 1.2.840.113556.1.4.804  
LDAP_MATCHING_RULE_TRANSITIVE_EVAL| 1.2.840.113556.1.4.1941  
LDAP_MATCHING_RULE_DN_WITH_DATA| 1.2.840.113556.1.4.2253  
  
比如我们查询域内所有设置了 NOT_DELEGATED 位的所有对象，NOT_DELEGATED 对应的十进制比较值位
1048576，那么根据语法，我们便可以构造以下过滤语法：

    
    
    (userAccountControl:1.2.840.113556.1.4.803:=1048576)

## Active Directory 访问查询工具

### ADSI 编辑器

ADSI Edit（AdsiEdit.msc）是一个 Microsoft Windows Server 工具，可用于通过 Active Directory
活动目录服务接口（ADSI）查看和编辑原始 Active Directory 目录服务属性。ADSI Edit 适用于编辑 Active Directory
中的单个对象或少量对象。ADSI Edit 不具备搜索功能。因此，必须预先知道要编辑的对象及其在 Active Directory 中的位置。

在域控中（普通域成员主机没有 ADSI 编辑器）执行 adsiedit.msc 打开 ADSI 编辑器，“操作” —> “连接” 即可：

![image-20210722192648732](https://image.3001.net/images/20210806/1628258143_610d3f5f0dfce23144ea2.png!small)

### LDP

LDP 是微软自带的一款域内信息查询工具，在域控中执行 ldp 即可打开 LDP。普通域成员主机默认是没有LDP的，可以自行上传 ldp.exe 工具上去。

打开 LDP 后，输入域控的 IP 和 389 端口进行连接：

![image-20210722193223379](https://image.3001.net/images/20210806/1628258143_610d3f5f59f3df81ce0a8.png!small)

然后点击 “连接” —> “绑定”，输入账号密码进行认证：

![image-20210722193421339](https://image.3001.net/images/20210806/1628258143_610d3f5f88d41d0278f8e.png!small)

![image-20210722193452959](https://image.3001.net/images/20210806/1628258143_610d3f5fdf9af15a67033.png!small)

然后再点击 “查看” —> “数”，输入一个 BaseDN 基础可分辨名称，指定这棵树的根，便可以用指定 BaseDN 作为根根往下搜索了。这里的
BaseDN 可以参照如下：

    
    
    DC=whoamianony,DC=org  
    CN=Users,DC=whoamianony,DC=org  
    CN=Builtin,DC=whoamianony,DC=org  
    CN=Computers,DC=whoamianony,DC=org  
    CN=Deleted Objects,DC=whoamianony,DC=org  
    OU=Domain Controllers,DC=whoamianony,DC=org  
    CN=ForeignSecurityPrincipals,DC=whoamianony,DC=org  
    ......

比如这里我们输入 BaseDN 为`DC=whoamianony,DC=org`，则 LDP
会以`DC=whoamianony,DC=org`为根往下搜索：

![image-20210722194240308](https://image.3001.net/images/20210806/1628258144_610d3f602e5f0c561343b.png!small)

![image-20210722194420616](https://image.3001.net/images/20210806/1628258144_610d3f608a930184b68da.png!small)

如果想要查看某个条目的信息，则 “右键” —> “搜索”，即可对指定的 BaseDN 进行过滤搜索：

![image-20210722195258253](https://image.3001.net/images/20210806/1628258144_610d3f60f376ce5687c4b.png!small)

![image-20210722195212920](https://image.3001.net/images/20210806/1628258145_610d3f61543642e52d7e5.png!small)

### Active Directory Explorer

Active Directory Explorer（AD
Explorer）是微软的一款域内信息查询工具，它是独立的可执行文件，无需安装。它能够列出域组织架构、用户账号、计算机账号等，它可以帮助你寻找特权用户和数据库服务器等敏感目标。

我们可以使用 AD Explorer 工具连接域控来访问活动目录，它可以方便的帮助用户进行浏览 Active Directory
数据库、自定义快速入口、查看对象属性、编辑权限、进行精确搜寻等操作。如下，在域内任意一台主机上，以域用户身份进行连接即可：

![image-20210721130756115](https://image.3001.net/images/20210806/1628258145_610d3f61ae79da2f4b1c3.png!small)

![image-20210721130825516](https://image.3001.net/images/20210806/1628258145_610d3f61eda3a3db8d065.png!small)

### Adfind

[AdFind](http://www.joeware.net/freetools/tools/adfind/)一款 C++
编写的域内查询信息的命令行工具，在域渗透里面的出场率极高。还有一个叫做 Admod ，可以修改。使用方法如下：

    
    
    AdFind.exe [switches]  [-b basedn]  [-f filter]  [attr list]

> -b：指定指定一个 BaseDN 基础可分辨名称作为查询的根节点
>
> -f：LDAP 过滤条件
>
> attr list：需要显示的属性
    
    
    # 搜索 whoamianony.org 域下 objectcategory=computer 的所有对象，会显示出所有对象以及对象的所有属性  
    Adfind.exe -b dc=whoamianony,dc=org -f "objectcategory=computer"  
      
    # 搜索 whoamianony.org 域下 objectcategory=user 的所有对象，会显示出所有对象以及对象的所有属性  
    Adfind.exe -b dc=whoamianony,dc=org -f "objectcategory=user"

![image-20210722221212990](https://image.3001.net/images/20210806/1628258146_610d3f62585ca6f9120ad.png!small)

    
    
    # 搜索 whoamianony.org 域下 objectcategory=computer 的所有对象，过滤出 name 和 operatingSystem 属性  
    Adfind.exe -b dc=whoamianony,dc=org -f "objectcategory=computer" name operatingSystem  
      
    # 搜索 whoamianony.org 域下 objectcategory=user 的所有对象，过滤出 cn 和 createTimeStamp 属性  
    Adfind.exe -b dc=whoamianony,dc=org -f "objectcategory=user" cn createTimeStamp

![image-20210722223327972](https://image.3001.net/images/20210806/1628258146_610d3f629a1f2856c7019.png!small)

![image-20210722221614923](https://image.3001.net/images/20210806/1628258146_610d3f62d2e995ff301ae.png!small)

更多查询命令：

    
    
    Adfind.exe -f objectclass=trusteddomain    # 信任关系  
    Adfind.exe -sc u:<username>    # 查询指定用户  
    Adfind.exe -sc getacls -sddlfilter ;;;;; -recmute    # 导出整个域的 ACL  
    Adfind.exe -sc u:<username> objectSid    # 查询指定用户的 SID  
    Adfind.exe -f "(&(objectCategory=person)(objectClass=user))"    # 查询所有用户  
    Adfind.exe -sc dclist    # 查询域控制器列表  
    Adfind.exe -schema -s base objectversion    # 查询域控制器版本  
    Adfind.exe -sc gpodmp    # 导出域内所有的 GPO  
    Adfind.exe -b "dc=whoamianony,dc=org" -f "mobile=*" mobile mail displayName title -s Subtree -recmute -csv mobile    # 导出域内所有的手机号为 csv 格式  
    Adfind.exe -b "dc=whoamianony,dc=org" -f "mail=*" mail displayName title -s Subtree -recmute -csv mobile    # 导出域内所有的邮箱为 csv 格式  
    Adfind.exe -b "dc=whoamianony,dc=org" -f "&(servicePrincipalName=*)(admincount=1)" servicePrincipalName    # 查询域内高权限的 SPN 服务主体名称  
    Adfind.exe -b "dc=whoamianony,dc=org" -f "useraccountcontrol:1.2.840.113556.1.4.803:=4194304" -dn    # 查找域内所有开启了 "Do not require Kerberos preauthentication" 选项的用户

并且 Adfind 还给我们提供了一个快捷的按位查询方式，可以直接用来代替那些复杂的 BitFilterRule-ID：

位过滤规则| OID| Adfind BitFilterRule  
---|---|---  
LDAP_MATCHING_RULE_BIT_AND| 1.2.840.113556.1.4.803| :AND:  
LDAP_MATCHING_RULE_OR| 1.2.840.113556.1.4.804| :OR:  
LDAP_MATCHING_RULE_TRANSITIVE_EVAL| 1.2.840.113556.1.4.1941| :INCHAIN:  
LDAP_MATCHING_RULE_DN_WITH_DATA| 1.2.840.113556.1.4.2253| :DNWDATA:  
  
如下实例：

    
    
    Adfind.exe -b dc=whoamianony,dc=org -f "(userAccountControl:AND:=524288)" -bit -dn

![image-20210730222110629](https://image.3001.net/images/20210806/1628258147_610d3f631c2bc138cf1ac.png!small)

## LDAP 查找中的 objectClass 和 objectCategory

### objectClass

上一篇文章中我们曾说过说过，在对象的 objectClass
属性里面，可以看到这个对象是哪一个类的实例，以及这个类所继承的所有父类。例如，域内主机`CN=EWS,CN=Computers,DC=whoamianony,DC=org`这个条目的`objectClass`属性的值中包括
top、person、organizationalPerson、user 和 computer：

![image-20210721221104273](https://image.3001.net/images/20210806/1628258147_610d3f634eb30d544a564.png!small)

根据类的继承关系可知，该对象是 computer 类的一个实例，而 computer 是 user 的子类，user 是
organizationalPerson 的子类，organizationalPerson 是 person 的子类，person 是 top
的子类。那么我们通过以下过滤语法都可以找到这个对象：

    
    
    (objectClass=user)  
    (objectClass=organizationalPerson)

由于所有的类都是 top 类的子类，所以当我们使用`(objectClass=top)`语句进行过滤时，域内所有的对象都可以搜索到

### objectCategory

对象类的每个实例还具有一个 objectCategory
属性，该属性是一个单值属性。并且建立了索引。其中包含的值为该实例对象的类或该类所继承的父类之一的专有名称。如下所示，

![image-20210722224810060](https://image.3001.net/images/20210806/1628258147_610d3f63b88efea2b2e2a.png!small)

域内主机`CN=EWS,CN=Computers,DC=whoamianony,DC=org`这个条目的`objectCategory`属性的值为`CN=Computer,CN=Schema,CN=Configuration,DC=whoamianony,DC=org`。如果我们想过滤所有
objectCategory
的属性为`CN=Computer,CN=Schema,CN=Configuration,DC=whoamianony,DC=org`的对象，使用以下语法即可：

    
    
    (objectCategory=CN=Computer,CN=Schema,CN=Configuration,DC=whoamianony,DC=org)

![image-20210722225216347](https://image.3001.net/images/20210806/1628258148_610d3f64101b923d355d7.png!small)

但是这样的话需要记住完整的 DN，为了方便，对象所属的类中还有一个 lDAPDisplayName
属性，用于指定该类所显示的名称。我们可以看到，对象`CN=EWS`所属的类存储在`CN=Computer,CN=Schema,CN=Configuration,DC=whoamianony,DC=org`中，里面有一个
lDAPDisplayName 属性的值正是 computer：

![image-20210722230015227](https://image.3001.net/images/20210806/1628258148_610d3f64480d61ea218ac.png!small)

而且， LDAP 是支持直接使用类的 lDAPDisplayName 属性作为条件进行搜索的，所以如果我们想要查找所有 objectCategory
的属性为`CN=Computer,CN=Schema,CN=Configuration,DC=whoamianony,DC=org`的对象，可以直接用
lDAPDisplayName 属性的值代替那一长串 DN：

    
    
    (objectCategory=computer)

![image-20210722230329811](https://image.3001.net/images/20210806/1628258148_610d3f64abd406adf91c2.png!small)

二者查询效果相同。

由于 objectCategory 建立索引，所以查询时间比较快，在对 Active Directory 进行查询时可以将二者结合使用以提高查询效率。

## Ending......

![20210722231242.jpg](https://image.3001.net/images/20210806/1628258148_610d3f64e3d751842ae34.jpg!small)

> 参考：
>
> <https://baike.baidu.com/item/ADSI/6600454?fr=aladdin>
>
> <https://blog.csdn.net/qq_36119192/article/details/107155203>
>
> <https://blog.csdn.net/qq_36119192/article/details/107152351>
>
> <https://blog.csdn.net/qq_36119192/article/details/107610208>
>
> <https://blog.csdn.net/qq_36119192/article/details/107529805>
>
> <https://daiker.gitbook.io/windows-protocol/ldap-pian/8#3schema-nc-zhong-de-> shu-xing>
>
> <https://daiker.gitbook.io/windows-protocol/ldap-pian/9#2-ldap-cha-zhao-> zhong-de-objectcategory-he-objectclass>

