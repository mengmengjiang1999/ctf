### 1、概述

在本节中，我们将研究支撑`Active Directory`工作的协议和技术。从本质上讲，`Active
Directory`是一个存储在域控制器上的分布式数据库，并且在这些域控制器上所做的更改会在林中相互复制。现在的问题是`AD`将所有数据存储在哪里？它将其存储在一个数据库中，该数据库存储在`NTDS.DIT`文件中。并且通过`LDAP`（轻量级目录访问协议）协议来访问它。简而言之，`Active
Directory`是一个简单的数据库，而`LDAP`是一种访问数据库的方式。

### 2、NTDS.DIT

表示‌‌‌‍‍​‍‍‌‌‌​‌‍‍‌‌​​‌‍‍‌‌`NT Directory Services`

`DIT`表示目录信息树（`Directory Information Tree`）

之所以将其命名为`NTDS`，是因为`Active Directory`最初称为`NT`目录服务。`Active
Directory`中的目录信息树(`DIT`)是基于`X.500`标准的数据库，主数据库文件为`NTDS.DIT`，默认情况下存储在`%SystemRoot%\NTDS`文件夹中(除非在升级域控制器初始设置时更改了位置)。

众所周知，`Active
Directory`包含称为组织单位的文件夹，其中包含用户、计算机或其他`AD`对象，由于它是分布式数据库，因此可以同时复制和存储在多个位置。当存在多个域时，将复制这些域的`NTDS.DIT`中的数据，并相互共享这些域中的资源。`NTDS.DIT`文件是存储`Active
Directory`数据的数据库，其中包括有关用户对象、组和组成员身份的信息。使用`LDAP`(轻量级目录访问协议)访问目录中的信息。`Active
Directory`数据库基于轻量级目录访问协议 (`LDAP`)，并支持`RFC 2251`中定义的`LDAP v 3`规范。

![image-20220406120955746](https://image.3001.net/images/20220426/1650934612_62674354227a01dad653c.png!small)

`NTDS.DIT`文件还包括域中所有用户的密码哈希。

##### 3、LDAP (轻量级目录访问协议)

`LDAP`协议用于访问目录服务，并为应用程序和其他系统提供与目录服务器通信和交互的机制。它负责跟踪网络上的内容，应用程序可以使用`LDAP`来检索`Active
Directory`数据库的任何对象和属性，甚至可以对其进行修改。当我们从`AD`枚举信息时，在后端使用的是`LDAP`。不仅如此，`LDAP`还允许我们修改对象，如修改组成员、更改对象的属性。许多枚举工具都使用`LDAP`从`AD`中查询信息，例如`Powerview
`或`Sharpound`等。任何使用`Active
Directory`的人，如管理员、红队渗透人员或编写与`AD`交互程序的开发人员，那么对`LDAP`的透彻了解将会对充分利用`Active
Directory`非常重要。

 **LDAP 端口**

`LDAP`的端口是`389`

LDAP加密（`LDAPS`）端口是636

 **LDAP语法**

了解一下`ldap`的基本语法对于使用`ldap`访问对象层次结构是很有帮助的。

`LDAP`使用`canonical name
(规范名称)`或`cn`。如果您想访问一个名为`John`的对象，使用`cn=john`。如果存在多个`cn=John`对象，那么我们需要通过提供更多细节来区分这个特定的`John`和其他对象，比如对象所在的位置，以便我们可以唯一地定位该对象。这可以通过`DN`（Distinguished
Name）实现。`DN`是最重要的`LDAP`属性，因为它可以唯一的标识一个条目，比如`cn=john,ou=users,dc=rootdse,dc=lab`。

在`LDAP`中每个条目由三个部分组成：

1、Distinguished Name (DN) //专有名称

2、Object Classes //对象类

3、Attributes //属性

 **专有名称
(`DN`)**该条目在整个树中的唯一名称标识。比如，对于用户对象`SQLServiceAccount`，其`DN`标识为：`CN=SQLServiceAccount,CN=Users,DC=rootdse,DC=lab`。

**objectClass（对象类）**是一种特殊类型的属性。`LDAP`中的所有对象都必须具有`objectClass`属性。`objectClass`定义指定每个`LDAP`对象需要哪些属性，并指定条目的对象类。该属性的值可以被客户端修改，但`objectClass`属性本身不能被删除。`objectClass`定义本身存储在`Schema`（模式）文件中。后面会讨论`Schema`。

**Attributes(属性)**保存条目的数据。每个属性都有一个类型、选项和一组值。属性值可以自定义。下面是顶级类中可用的一些属性的列表，这些属性在`Active
Directory`中创建的每个对象上定义。

属性| 描述  
---|---  
cn| RDN attribute for most object classes, also referred to as the common
name.//大多数对象类的 RDN 属性，也称为通用名称  
whenCreated| Timestamp when the object was created. See Recipe 4.26 for more
information. //创建对象时的时间戳  
description| attribute that can be used as a generic field for storing a
description of the object //可用作存储对象描述的通用字段的属性  
displayName| Name of the object displayed in administrative
interfaces.//管理界面中显示的对象的名称  
distinguishedName| Distinguished name of the object. //对象专有名称  
whenChanged| Timestamp when the object was last changed by the local
server.//本地服务器上次更改对象时的时间戳  
name| RDN of the object. The value of this attribute will mirror the naming
attribute (e.g., cn, ou, dc).//对象的 RDN。此属性的值将反映命名属性（例如 cn、ou、dc）  
nTSecurityDescriptor| Security descriptor assigned to the object.//分配给对象的安全描述符  
objectCategory| Used as a grouping mechanism for objects with a similar
purpose (e.g., Person).//用作具有相似目的的对象（例如`Person`）的分组机制。  
objectClass| List of classes from which the object’s class was
derived.//派生对象类的类列表  
objectGUID| Globally unique identifier for the object.//对象的全局唯一标识符  
uSNChanged| Update sequence number (USN) assigned by the local server after
the last change to the object //在上次更改对象后更新本地服务器分配的序列号(USN）  
uSNCreated| USN assigned by the local server when the object was
created.//创建对象时本地服务器分配的 USN。  
  
 **objectClass 属性**

用户对象的`objectClass`属性将标识`top`、`person`、`organizationalPerso`和`user`类。当创建对象实例时，系统将设置`objectClass`值，并且不能更改。

 **objectCategory 属性**

对象类的每个实例还具有一个`objectCategory`属性，该属性是一个单值属性，它包含对象是其实例或其某个超类的类的专有名称。
创建对象时，系统会将其`objectCategory`属性设置为其对象类的`defaultObjectCategory`属性指定的值。
不能更改对象的`objectCategory `属性。

`ObjectClass`与`ObjectCategory`的组合有点复杂且不直观，下表记录了指定`objectCategory
`和`objectClass`值的子句的各种组合的结果：

 **objectCategory**|  **objectClass**|  **Result**  
---|---|---  
person| user| user objects  
person|  
| user and contact objects  
person| contact| contact objects  
  
| user| user and computer objects  
computer|  
| computer objects  
user|  
| user and contact objects  
  
| contact| contact objects  
  
| computer| computer objects  
  
| person| user, computer, and contact objects  
contact| user and contact objects|  
  
group|  
| group objects  
group| group objects|  
  
person| organizationalPerson| user and contact objects  
  
| organizationalPerson| user, computer, and contact objects  
organizationalPerson|  
| user and contact objects  
  
在`Powershell`中可以通过内置的`.NET`接口执行`LDAP`查询，使用`[adsisearcher]
`类型加速器，我们可以传递`LDAP`查询并获得结果，因为这允许我们访问`Active
Directory`对象而无需导入额外的`PowerShell`模块。

下面是我们如何运行`LDAP`查询(`objectCategory=Computer`)以查找所有域计算机对象的示例：

    
    
    PS C:\> ([adsisearcher]'(objectCategory=computer)').FindAll()
    
    Path                                                  Properties
    ----                                                  ----------    LDAP://CN=DC1,OU=Domain Controllers,DC=pentest,DC=com {ridsetreferences, logoncount, codepage, objectcategory...}
    LDAP://CN=CYZ,CN=Computers,DC=pentest,DC=com          {logoncount, codepage, objectcategory, iscriticalsystemobject...}
    
    
    PS C:\>
    
    

![image-20220406131609710](https://image.3001.net/images/20220426/1650934613_6267435516443935d6907.png!small)

### 4、常见的LDAP筛选器

以下是几个常见的`LDAP`筛选器的示例：

Task description (任务描述)| LDAP Filter(LDAP筛选器)  
---|---  
All accounts with a SPN(所有具有 SPN 的帐户)| (serviceprincipalname=*)  
All Group Policy Objects(所有组策略对象)| (objectcategory=groupPolicyContainer)  
All the domains(所有域)| (objectClass=domain)  
All the security groups in AD(AD中的所有安全组)| (samaccounttype=268435456)  
All the organizational units(所有组织单位)| (objectcategory=organizationalUnit)  
  
获取所有启用了`serviceprincipalname`属性值的服务帐户。

    
    
    PS C:\> ([adsisearcher]'(serviceprincipalname=*)').FindAll()
    
    Path                                                  Properties
    ----                                                  ----------    LDAP://CN=DC1,OU=Domain Controllers,DC=pentest,DC=com {ridsetreferences, logoncount, codepage, objectcategory...}
    LDAP://CN=CYZ,CN=Computers,DC=pentest,DC=com          {logoncount, codepage, objectcategory, iscriticalsystemobject...}
    LDAP://CN=krbtgt,CN=Users,DC=pentest,DC=com           {logoncount, codepage, objectcategory, description...}
    
    

![image-20220406132719019](https://image.3001.net/images/20220426/1650934613_62674355d13f7e92ea304.png!small)

可以使用`ConvertTo-JSON`在`JSON`中获得更多详细信息。它对获取所有属性的所有细节非常有帮助。

    
    
    PS C:\> ([adsisearcher]'(serviceprincipalname=*)').FindAll() | ConvertTo-Json
    

![image-20220406132928069](https://image.3001.net/images/20220426/1650934614_626743568922efab4b223.png!small)

### 5、Schema（模式）

`Active Directory`林中的模式是数据应如何存储在 AD
中的蓝图，它包含可以创建的所有对象类的定义，以及这些对象的所有属性的定义。举个例子：我们想创建一个用户帐户并通过填充其属性来添加信息。在这里，用户帐户是`User`类的实例，它使用属性来存储有关该对象的信息，并在查询用户帐户时显示它。`User`类和许多其他已知类(如`User`、`Computer`、`OrganizationalUnit)`和属性(如`TelephoneNumber`和`objectSID`)的定义都在`Active
Directory`模式中定义。

 **注意** ：在`AD`林中，只有一个模式，因此如果对林中的模式定义进行更改，则会影响所有的域。

以下是`Active Directory`中的一些重要属性：

User Attribute| Description  
---|---  
userPrincipalName| A common logon name (format is similar to email
like`scarred.monk@rootdse.org`)//常用的登录名（格式类似于像scarred.monk@rootdse.org
这样的电子邮件）  
objectGUID| Uniquely identifies a user account. Even if account is
moved/renamedd, objectGUID never changes //唯一标识用户帐户。即使帐户被移动/重命名，objectGUID
也永远不会改变  
sAmAccountName| Used for account logons to a domain. Used to support clients
running on older windows versions //用于帐户登录域。用于支持在较早的Windows版本上运行的客户端  
objectSID| Security identifier (SID) of the user, used by servers to identify
user and their group memberships to authorize users access to domain resources
//用户的安全标识符(SID)，由服务器用来标识用户及其组成员身份，以授权用户访问域资源  
sIDHistory| This attribute contains previous SIDs for the user object. This is
only needed if a user has moved to another domain
//此属性包含用户对象的以前的SID。仅当用户已移动到另一个域时才需要此操作  
Distinguished Name (DN)| Used to locate objects in Active Directory (by
services and applications) //用于定位 Active Directory 中的对象（按服务和应用程序）  
  
`AD`模式由一个层次结构的类组成，这些层次定义了可以在`Active
Directory`中创建的对象的类型，以及它们可以拥有的不同属性。这些类支持继承，这使开发人员能够为多种类型的对象重用现有的类定义；例如，描述属性可用于每种类型的`AD`对象，但该属性本身仅在模式中定义一次。继承树的顶部是顶层类，模式中的每个类都从该类派生而来。

##### 6、RootDSE

`rootDSE`是目录服务器上目录数据树的根，`rootDSE`的目的是提供有关目录服务器的数据。检查`RootDSE`的属性对于发现有关林、域或域控制器的基本信息很有用。

要查看`RootDSE`的属性，我们可以使用以下命令：

    
    
    PS C:\> Get-ADRootDSE
    

![image-20220406140404360](https://image.3001.net/images/20220426/1650934615_626743577455af25cd871.png!small)

要使用`LDAP`查询检查目录对象的数量，我们可以使用以下方法：

    
    
    Get-ADObject -Filter {(objectClass -eq "user") -and (objectCategory -eq "person")} | Measure-Object | FL Count
    

![image-20220406140433277](https://image.3001.net/images/20220426/1650934616_626743584a9710951a2e8.png!small)

### 7、参考资料

https://ldapwiki.com/wiki/ObjectClass%20vs%20ObjectCategory

### 8、说明

本文由笔者在原文上编译，转载请注明原文出处。

原文出处：[Active Directory Fundamentals (Part 4)- NTDS.DIT, LDAP, Schema,
Attributes)- Group Policies](https://rootdse.org/posts/active-directory-basics-4/)

