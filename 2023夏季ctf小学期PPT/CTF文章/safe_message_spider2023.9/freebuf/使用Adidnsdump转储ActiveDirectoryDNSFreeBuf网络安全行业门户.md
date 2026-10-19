**DNS域传送漏洞是在黑客常用的一种漏洞攻击手段。要实现域传送漏洞，就需要一个不安全配置的DNS服务器，允许匿名用户传输所有记录并收集有关网络中主机的信息。然后网络上的任何用户都可以获取所有传送记录并收集有关网络中服务器的信息。然而，目前还很少有人知道，如果使用Active
Directory集成DNS，任何用户都可以默认查询所有DNS记录。**

本文，我会给你介绍了一个默认查询所有DNS记录的工具——[Adidnsdump](http://feedproxy.google.com/~r/PentestTools/~3/8FXqJbJc7lY/adidnsdump-active-directory-integrated.html)
，即使你是一个没有读取传送记录权限的用户，也可以使用以下方法获得域环境中的所有DNS解析记录。

## 0x01

就个人而言，每当我接手一个新的渗透测试任务时，我会去了解网络布局，使用了那些软件以及数据的位置。如果公司有非描述性的服务器名称或描述，像BloodHound或ldapdomaindump这样的工具不会有太大帮助，因为`SRV00001.company.local`仍然没有告诉我在这台主机上运行的是什么。在大量IP地址上运行EyeWitness等发现工具通常会返回大量默认的Apache
/
IIS页面，因为大多数站点都配置为侦听DNS名称而不是IP地址。此时你如果知道DNS记录，可能就会发现SRV00001.company.local和gitlab.company.local指向同一个IP，这个IP上可能存放着大量源码。因此，我认为访问AD的DNS记录非常有价值。为此我编写了一个可以转储这些DNS记录的Adidnsdump。你既可以直接在网络中的主机运行它，也可以通过SOCKS隧道利用。

## 0x02

该工具的设计思路，是在我研究Active Directory DNS时开始的，主要受到Kevin
Robertson在[ADIDNS](https://blog.netspi.com/exploiting-adidns/)
上工作的启发。当我作为普通用户提取了ADSI
Edit并突然看到了域中所有DNS记录时，我试图找出AD如何在LDAP中使用域来存储DNS记录。令我惊讶的是，早在2013年，就有人开发出可以提取DNS记录的[PowerShell脚本](https://room362.com/post/2013/2013-10-04-ad-zone-transfers-as-a-user/)，但它并没有完全符合我的要求，所以我决定用Python编写一个版本，并添加一些选项来枚举比默认情况下更多的记录。

## 0x03

在LDAP中查询DNS记录的最明显方法是执行查询，选择该类的所有对象，这些对象`dnsNode`表示DNS区域中的条目。当我使用过滤器执行查询时`(objectClass=dnsNode)`，这会返回非常有限的结果，即使我可以看不到更多记录：

![1.png](https://image.3001.net/images/20190626/1561542582_5d133fb694f7f.png!small)

如上图所示，很多记录的objectClass都处于隐藏状态。这是因为计算机DNS记录的默认权限（我认为其他记录也不是通过AD DNS
gui创建的），这些记录不允许所有用户查看内容。由于IP地址实际上存储为此对象的属性，因此无法查看这些记录的IP地址。

但是，默认情况下，任何用户都可以创建新的DNS记录，任何用户也可以默认列出DNS区域的子对象。所以我们知道有记录，我们只是无法使用LDAP查询它。

![2.png](https://image.3001.net/images/20190626/1561542590_5d133fbe2b541.png!small)

通过使用LDAP枚举知道记录所在的位置之后，我们就可以直接使用DNS查询它，因为执行常规DNS查询不需要什么特别权限，这样我们就可以解析域中的所有记录。

## 0x04

使用adidnsdump，您可以[从GitHub](https://github.com/dirkjanm/adidnsdump)获取，可以枚举DNS区域中的所有记录。首先，首先显示您当前所在域中的区域`--print-zones`。这将显示存在哪些区域。并非所有区域都很有趣，例如转发，缓存和存根区域不包含该域的所有记录。如果找到这些区域，最好查询它们实际所属的域。下面的输出显示我的测试域只有默认区域：

    
    
    user@localhost:~/adidnsdump$ adidnsdump -u icorp\\testuser --print-zones icorp-dc.internal.corp  
    Password:   
    [-] Connecting to host...  
    [-] Binding to host  
    [+] Bind OK  
    [-] Found 2 domain DNS zones:  
        internal.corp  
        RootDNSServers  
    [-] Found 2 forest DNS zones:  
        ..TrustAnchors  
        _msdcs.internal.corp

如果我们为工具指定区域（或者为默认区域指定为空），我们将获得所有记录的列表。显示可以列出所谓的“隐藏”记录，但仅显示问号，因为不知道哪种类型的记录存在以及它指向何处。记录全部保存到名为的文件中`records.csv`。

![3.png](https://image.3001.net/images/20190626/1561542598_5d133fc6cf94e.png!small)

要解析未知记录，请指定`-r`标志，该标志将对`A`所有未知记录执行查询（`AAAA`如果您在IPv6网络中，则可以在代码中轻松将其更改为）。之前空白的几个节点突然有记录：

![4.png](https://image.3001.net/images/20190626/1561542609_5d133fd1c0dff.png!small)

如果您没有直接连接但是通过代理工作，则可以通过socks代理该工具并使用该`--dns-tcp`标志在TCP上执行DNS查询。

## 缓解措施

为了安全起见，我建议你首先要对DNS记录的安全性持有客观的认知态度。如果你确实要隐藏DNS记录，就请删除“Everyone”和“Pre-Windows
2000 Compatible Access”的“列出内容”权限，以阻止普通用户查询DNS记录。但这可能会产生负面影响，所以我不建议那样做。

所以最好的办法是及时检测DNS查询活动的出现，通过监控大量DNS查询或启用对DNS区域列表的审计可能是一种更好的缓解措施。

### 工具

adidnsdump可在[GitHub](https://github.com/dirkjanm/adidnsdump)和PyPI（`pip install
adidnsdump`）上下载。该工具还可以将记录转储到CSV文件，但随时可以提交替代格式的请求。

 ***参考来源：[dirkjanm](https://dirkjanm.io/getting-in-the-zone-dumping-active-directory-dns-with-adidnsdump/)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**

