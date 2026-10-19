本文主要介绍了
WindowsAD域中基于访问控制列表（ACL）的攻击，在AD域的攻击手法中，基于ACL的攻击由于理解起来比较困难，现有的安全设备也很少有对ACL的监控，这种类型的攻击通常会被安全人员所忽视。

 **1.** **什么是ACL**

在Windows访问控制模型中，有两个主要的组成部分：访问控制令牌（Access Token）和安全描述符（Security
Descriptor），访问控制令牌由访问者持有，包含已登录用户的信息，安全描述符与访问对象相关联，主要有四个部分组成OWNER、GROUP、SACL、DACL，其中OWNER和GROUP分别表示对象的拥有者和对象所在的组，用SID的形式表示，SACL和DACL都是由若干条ACE组成，SACL的作用是控制对对象的某个属性访问日志的记录与否，DACL则控制着用户或者组是否对对象有访问权限，这也是我们主要关注的部分，AD域中的对象都是存储在LDAP数据库中，而对象的DACL就存储在nTSecurityDescriptor属性中，我们可以通过服务管理查看对象的ACL。

![1685600545_64783921d5e9514c62edf.png!small](https://image.3001.net/images/20230601/1685600545_64783921d5e9514c62edf.png!small)

也可以通过Adfind工具来查询域内对象的ACL

![1685600555_6478392b713956c9e7eb3.png!small](https://image.3001.net/images/20230601/1685600555_6478392b713956c9e7eb3.png!small)

可以看到图1中hackpc对象的ACL一目了然，而图2中OWNER和GROUP的SID还比较好理解，DACL和SACL的表示就完全不知所云了，其实这两者表示的意思是完全相同的，只不过Adfind查询的结果是ACL的原始存储形式，这种ACL表示的格式也就是SDDL（Security
Descriptor Definition Language）。

 **2.SDDL**

SDDL是一种文本表述格式，用于指示安全描述符的四个组成部分

    
    
    O:owner_sid
    G:group_sid
    D:dacl_flags(string_ace1)(string_ace2)... (string_acen)
    S:sacl_flags(string_ace1)(string_ace2)... (string_acen) 

owner_sid、group_sid分别是对象所有者和对象所有组的sid字符串，dacl_flags和sacl_flags分别是dacl和sacl的安全描述符控制标志，标识和含义如下：

![1685600566_647839360816b3cadff71.jpg!small](https://image.3001.net/images/20230601/1685600566_647839360816b3cadff71.jpg!small)

string_ace是对ACE的文本描述形式，语法如下：

    
    
    ace_type;ace_flags;rights;object_guid;inherit_object_guid;
    account_sid;(resource_attribute) 

各个字段的标识和含义可以参考微软文档

[https://learn.microsoft.com/zh-cn/windows/win32/secauthz/ace-strings](https://link.zhihu.com/?target=https%3A//learn.microsoft.com/zh-cn/windows/win32/secauthz/ace-strings)

我们以查询到的DACL中第一条ACE为例``

    
    
    (OA;;WP;5f202010-79a5-11d0-9020-00c04fc2d4cf;bf967a86-0de6-11d0-a285-00aa003049e2;S-1-5-21-12599190-3165991563-228399834-512)

ace_type为“OA”，对应ACCESS_ALLOWED_OBJECT_ACE_TYPE，表示是ALLOW类型的ACE，rights字段为“WP”，表示目录服务对象访问权限，对于权限值是ADS_RIGHT_DS_WRITE_PROP，表示目录对象写权限，object_guid表示权限的guid，account_sid标识这条ACE受托人的SID字符串。

 **3.** **场景1 重置密码**

在企业中it管理部门为了方便员工忘记域账号密码后进行重置密码，通常委派一些低权限的it管理员重置用户密码的权限，这样可能意外导致低权限用户重置高权限用户的密码从而获得权限提升。下图描述了这种攻击路径。

![1685600752_647839f044a936ab8767a.jpg!small](https://image.3001.net/images/20230601/1685600752_647839f044a936ab8767a.jpg!small)

我们通过委派控制赋予域内用户组itmgr重置域内所有用户密码的权限

![1685600762_647839faba87b09ed9a4f.png!small](https://image.3001.net/images/20230601/1685600762_647839faba87b09ed9a4f.png!small)

blyth用户为itmgr组内普通用户

利用samr重置administrator用户的密码

![1685600770_64783a0278ac5d1bb5d01.png!small](https://image.3001.net/images/20230601/1685600770_64783a0278ac5d1bb5d01.png!small)

 **4.** **场景2 资源约束委派**

约束委派和非约束委派的配置需要域管理员对相关属性进行配置，微软为了给域用户提供更大的灵活性，让域内资源所有者能够配置哪些账户是可信的，并允许委派给他们。资源约束委派攻击最核心的就是对计算机
msDS-AllowedToActOnBehalfOfOtherIdentity 属性的控制，计算机用户本身，以及拉计算机入域的用户都对该计算机的
msDS-AllowedToActOnBehalfOfOtherIdentity
有写权限，我们这里假设攻击者获取域管权限后进行权限维持，为域内普通用户blyth配置对域控DC01 msDS-AllowedToActOnBehalfOfOtherIdentity 属性的写权限。

![1685600782_64783a0ed1a8795a47513.png!small](https://image.3001.net/images/20230601/1685600782_64783a0ed1a8795a47513.png!small)

利用ldap修改

msDS-AllowedToActOnBehalfOfOtherIdentity 属性

配置资源约束委派

![1685600790_64783a16c4dd91e017fbc.png!small](https://image.3001.net/images/20230601/1685600790_64783a16c4dd91e017fbc.png!small)

利用S4U2self + S4U2Proxy获取DC01的CIFS票据

![1685600803_64783a2338c718d0dac0c.png!small](https://image.3001.net/images/20230601/1685600803_64783a2338c718d0dac0c.png!small)

pass the ticket

![1685600826_64783a3ae532599db3199.png!small](https://image.3001.net/images/20230601/1685600826_64783a3ae532599db3199.png!small)

 **5.** **场景3 DCSYNC**

DCSYNC是一种利用drsuapi模拟域控密码同步对域内凭据进行窃取的攻击手段，用户配置了以下两条ACL就可以对域控进行DCSYNC

  * 目录复制同步（Replicating Directory Changes）
  * 目录复制同步所有项（Replicating Directory Changes All）

在一些企业应用中可能存在一些应用账号需要利用DCSYNC对域内用户信息进行同步备份，攻击者在获取域控权限之后也可能会设置DCSYNC权限作为后门，我们给域内普通用户alice赋予上述两个必要的权限

![1685600849_64783a517d16c71d82904.png!small](https://image.3001.net/images/20230601/1685600849_64783a517d16c71d82904.png!small)

利用alice用户的凭据获取administrator用户的hash

![1685600858_64783a5a159c070306645.png!small](https://image.3001.net/images/20230601/1685600858_64783a5a159c070306645.png!small)

 **6.** **场景4 AdminSDHolder**

AdminSDHolder是为域内受保护的用户和组提供权限的“模板”，每60分钟SDProp会将受保护帐户和组的权限重置为与域的AdminSDHolder对象的权限匹配，这一特性频繁被攻击者用来进行留后门等操作。

首先修改AdminSDHolder对象的SD，为bob用户添加GA权限

    
    
    Admod.exe -b "CN=AdminSDHolder,CN=System,DC=test19,DC=local"
     "SD##ntsecuritydescriptor::{GETSD}{+D=(A;;GA;;;test19\bob)}" 

![1685600872_64783a6889fabeee56247.png!small](https://image.3001.net/images/20230601/1685600872_64783a6889fabeee56247.png!small)

经过一小时之后可以发现这条ACE已经同步到受保护的组的SD中

![1685600880_64783a707517609a44329.png!small](https://image.3001.net/images/20230601/1685600880_64783a707517609a44329.png!small)

这时候我们就可以利用bob的身份进行恶意操作，比如添加域管理员

![1685600888_64783a7854470ea6d3763.png!small](https://image.3001.net/images/20230601/1685600888_64783a7854470ea6d3763.png!small)

 **总结**

在AD域中，权限的梳理和监控是一项很重要的工作，不合理的权限配置会导致攻击者轻易的进行权限提升，如果对域内ACL不熟悉，对基于ACL的后门排查也无从谈起，对于安全管理人员，一些敏感的权限变更行为也能帮助我们快速定位攻击行为。

