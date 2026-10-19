**![128-1024x731.jpg](https://image.3001.net/images/20181017/1539740513_5bc69361b3672.jpg!small)**

**密码安全问题一直都受到个人和企业的关注。对于个人而言，或许仅仅只是个人隐私的被公开，而对于企业而言则可能会是灾难性的。为了避免出现这种情况，越来越多的企业都开始使用一些不可逆，且强度高的加密算法来加密其账户密码。但一些安全意识薄弱的企业或个人，仍在使用可逆加密存储其账户密码。一旦使用可逆加密，即使你的密码设置的非常长也可以被攻击者轻易的破解。**

说到破解，Hashcat绝对是我的首选工。我可以一边开着Hashcat，一边做其它的事情。可能只需几分钟，几个小时或短短的几天，Hashcat就能为我得到我想要的一切！

Hashcat的工作原理也很简单。首先，它会获取潜在的密码（例如Autumn2018）并计算其哈希值。然后，Hashcat将新计算的代表Autumn2018的哈希值，与你给出的哈希值列表进行比较。如果找到一个或多个匹配项，则表示这些帐户使用的密码为Autumn2018。

![1pasted image
0.png](https://image.3001.net/images/20181017/1539740536_5bc6937816142.png!small)![2pasted
image
0.png](https://image.3001.net/images/20181017/1539740536_5bc6937819e29.png!small)

好了，话不多说！下面进入我们的正题。

这一切都始于从域控中提取哈希值。通常我们需要先将权限提升为域管并登录到域控才能获取到这些文件。但在某些特殊情况下，可能会存在一个可供较低权限帐户访问的备份文件，该文件包含Active
Directory（AD）数据库。

由于当前的AD数据库出于活动运行状态，因此我们无法复制该文件（使用时会被系统锁定）。为此，我创建了一个VSS快照并将ntds.dit文件与包含提取哈希所需的BOOTKEY的SYSTEM注册表hive一起复制。我通常使用内置的ntdsutil命令来执行此操作，如下所示：

![3pasted image
0.png](https://image.3001.net/images/20181017/1539740561_5bc69391f0cc5.png!small)

然后，我们可以使用Impacket secretsdump Python脚本来从数据库中提取哈希值。

    
    
    secretsdump.py -system SYSTEM -ntds ntds.dit LOCAL -outputfile breakme

我原本只想获取包含NTLM哈希值的*.NTDS文件。但在测试中我意外的发现，脚本还会输出了扩展名为“.CLEARTEXT”的文件。

![4pasted image
0.png](https://image.3001.net/images/20181017/1539740591_5bc693afcbaac.png!small)

secretsdump脚本使用outputfile参数指定，将所有哈希写入前缀为“breakme”的文件。在这个过程中我们发现了NTLM哈希，cleartext哈希，以及Kerberos
密钥。在“CLEARTEXT”文件中包含了相关用户的明文密码，其中包括几个长度为128个字符的密码！

![5pasted image
0.png](https://image.3001.net/images/20181017/1539740612_5bc693c4121b1.png!small)

说实话，做了这么多的测试任务这是我头一次碰到这种情况。文件中包含的用户账户和相应的密码一目了然，没有任何的加密保护措施！我立即检查了其中的一些账户（呵呵~其中竟有一个域管理员的账户），经过验证域管的账户密码为真实可用密码！经过一番调查，我了解到至少有几种不同的机制会强制存储明文凭据。

 **注：**
Cleartext（明文）并不意味着密码就是按原样存储。它们一般会使用RC4加密形式存储。而用于加密和解密的密钥是SYSKEY，它被存储在注册表中，可以由域管理员提取。这意味着哈希值可逆为明文，因此我们称它为“可逆加密”。

对于使用可逆加密存储密码的帐户，Active Directory用户和计算机（ADUC）中的帐户属性，会显示使用可逆加密存储密码的复选框。如下所示：

![6pasted image
0.png](https://image.3001.net/images/20181017/1539740638_5bc693dea770e.png!small)

你可以使用以下PowerShell命令，来查询AD活动目录中UserAccountControl属性中设置了可逆加密标志的任何用户：

    
    
    Get-ADUser  -Filter  ‘useraccountcontrol  -band  128’  -Properties useraccountcontrol  | Format-Table name, samaccountname,useraccountcontrol

![7pasted image
0.png](https://image.3001.net/images/20181017/1539740656_5bc693f05ec51.png!small)

那么，为什么要支持这种不安全的可逆加密存储呢？答案是为了满足某些应用程序的需要。因此，微软为需要知道用户密码值的应用程序提供了一种机制，就是强制存储可逆加密的密码，以便对用户进行身份验证。我所知道的需要可逆加密的应用程序是MS
CHAP, SASL
Digest身份验证，需要对Windows域进行身份验证的旧版MacOS主机。也很可能还有其他一些我不知道的，第三方应用程序也需要用到。

以下是[微软关于该设置的最佳实践提示](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/store-passwords-using-reversible-encryption)：

![8pasted image
0.png](https://image.3001.net/images/20181017/1539740674_5bc6940264ee8.png!small)

  1. 即使它需要域管理员使用上面的方法，从Active Directory数据库中提取哈希值，也意味着DA（或被盗取的DA帐户）可以轻松地学习其他用户的密码。这违反了不可否认原则。不可否认性的目的是为解决有关事件或行为是否发生过纠纷，而对涉及被声称事件或行为不可辩驳的证据进行收集、维护和使其可用并且证实。
  2. 我们经常发现包含VSS快照的备份可以访问AD数据库。备份文件通常可由较低权限的帐户访问，甚至是所有的域用户。在这种情况下，任何域用户都可以轻松访问，使用可逆加密存储的任何帐户密码。

下面，我来分解下之前那条使用PowerShell从AD中提取使用可逆加密存储密码用户的命令。

    
    
    Get-ADUser  -Filter  ‘useraccountcontrol  -band  128’  -Properties useraccountcontrol  | Format-Table name, samaccountname,useraccountcontrol

 **Get-ADUser –** 是Active Directory PowerShell模块中的cmdlet，默认情况下安装在Windows
Server 2008 R2及更高版本上。可以使用Import-Module命令导入它。

![9pasted image
0.png](https://image.3001.net/images/20181017/1539740695_5bc694171d5eb.png!small)

 **Filter –**
使用PowerShell表达式告诉cmdlet搜索参数是什么。这里，我们搜索的是具有特定UserAccountControl属性值的用户帐户。

你也可以使用LDAPFilter，它与Filter是相同的，但使用的是LDAP查询语法。查找所需UserAccountControl值的正确语法如下：

    
    
    Get-ADUser -LDAPFilter “(&(objectCategory=Person)(UserAccountControl:1.2.840.113556.1.4.803:=128))” -Properties useraccountcontrol | Format-Table name,samaccountname

 **![10pasted image
0.png](https://image.3001.net/images/20181017/1539740713_5bc6942966cf2.png!small)**

 **useraccountcontrol -band 128**

AD中的UserAccountControl属性是与用户帐户的设置相关联的属性，长度为32位。每个位代表有关该用户帐户的特定设置。例如，当帐户被禁用时，第二个低位被设置为“1”。在可逆加密的情况下，将第8个低位设置为“1”。第8个低位对应于十进制值128。

要访问其中特定位的值，必须使用逻辑位级操作。了解有关更多按位操作的信息，请点击[这里](https://ldapwiki.com/wiki/Bitmask)（或[此处](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_arithmetic_operators?view=powershell-6#bitwise-operators)）查看。在我们的示例中，-band
128表示使用值为128的按位AND运算，来确定其是否设置了第8个低位（无论在32位数内设置了哪些其它位）。

![11pasted image
0.png](https://image.3001.net/images/20181017/1539740736_5bc6944026cbe.png!small)

如果使用LDAPFilter，则可以通过LDAP语法1.2.840.113556.1.4.803来指定按位操作。通过指定值128，我们请求返回第8个低位设置为“1”的所有记录。

![12pasted image
0.png](https://image.3001.net/images/20181017/1539740753_5bc69451287df.png!small)

 **Properties useraccountcontrol**

由于Get-ADUser命令检索不包含UserAccountControl属性的默认属性集，因此必须使用-Properties参数在结果中明确进行询问。

 **Format-Table name, samaccountname,useraccountcontrol**

Format-Table命令将告诉PowerShell格式化输出以及要显示的属性。如果你希望结果垂直列出而不是以表格的形式列出，那么你可以使用Format-List命令。

![13pasted image
0.png](https://image.3001.net/images/20181017/1539740776_5bc6946853d12.png!small)

当然，你也可以将结果全部输出到一个文件中....

    
    
    Get-ADUser  -Filter  ‘useraccountcontrol  -band  128’  -Properties useraccountcontrol  | Format-Table name, samaccountname,useraccountcontrol | Out-File -Encoding ascii MyOutput.txt

 **![14pasted image
0.png](https://image.3001.net/images/20181017/1539740790_5bc69476a1eb2.png!small)**

 ***参考来源：[blackhillsinfosec](https://www.blackhillsinfosec.com/how-i-cracked-a-128-bit-password/) ，FB小编secist编译，转载请注明来自FreeBuf.COM**

