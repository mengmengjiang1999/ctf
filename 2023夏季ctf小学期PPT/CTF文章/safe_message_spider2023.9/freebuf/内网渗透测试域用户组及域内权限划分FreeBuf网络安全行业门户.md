![20210730222825.jpg](https://image.3001.net/images/20210806/1628258207_610d3f9f9aa4bfa3320c0.jpg!small)

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

在域环境中，我们并不建议直接给某个用户赋予特定的权限，而是通过一个域用户组，对这个域用户组赋予一个组权限，然后再将该用户拉进这个域用户组中，这样该用户便有了这个域用户组的权限。本节我们将介绍几个域组的概念与权限划分。

## 域用户组介绍

组（Group）是用户账号的集合。通过向一组用户分配权限，就可以不必向每个用户分别分配权限了。按照用途分类，域组分为通讯组和安全组。

对于通讯组，我们接触的比较多的就是邮件组，将若干个人划分到一个通讯组，给这个通讯组发件，那组内用户都能收到。但本节我们主要讲的还是安全组。

安全组则是用户权限的集合。举个例子，管理员在日常的网络管理中，不必向每个单个用户账号都设置单独的访问权限，只需要创建一个组，对这个组配置访问权限，然后将需要配置该访问权限的用户账号拉进这个组中即可。并且如果管理员在网络运维中需要一些特殊的管理权限时，只需将自己的运维账号拉进该组中就行了。

## 组的作用域

组的作用域是相对于域林的概念。每个安全组和通信组均有作用域，该作用域标识组在域树或树林中应用的范围。

安全组可以按照其作用范围划分为：

> 全局组（Global Group）
>
> 通用组（Universal Group）
>
> 域本地组（Domain Local Group）

### 域本地组（Domain Local Group）

听他的名字就知道了，域本地组就是本域内的本地组。域本地组主要用于本域内资源的访问权限，不适用于林，但可以包含域林内任何一个域的账户、通用组和全局组，也可以包含相同域内的域本地组，但无法包含其他域内的域本地组。本地域组只能够访问该域内的资源，无法访问其他不同域内的资源，即当你在设置权限时，只可以设置相同域内的域本地组的权限，无法设置其他不同域内的域本地组的权限。

当多域用户访问单域资源（访问本域、同一个域）时，可以从任何域向这个域的域本地组添加用户账户、通用组和全局组，但只能在其所在域内指派权限。比如一个域林里面，只有林根域有`Enterprise
Admins`这个组（通用组），然后其他子域的域本地组`Administrators`会把林根域的`Enterprise
Admins`组加进来，所以林根域的`Enterprise
Admins`组用户才在整个域林内具备管理员权限。可见，如果想要一个只允许访问同一个域中的资源的组，那么使用域本地组即可。

以下命令可以查询域内的所有域本地组：

    
    
    Adfind.exe -b dc=whoamianony,dc=org -bit -f "(&(objectClass=group)(grouptype:AND:=4))" cn -dn

![image-20210725150747080](https://image.3001.net/images/20210806/1628258207_610d3f9fe9deda8667dcd.png!small)

下面介绍几个的常见的系统内置的域本地组及其组权限：

>
> Administrators：管理员组，改该组的成员可以不受限制地存取计算机/域的资源。不仅是最具有权限的一个组，也是在活动目录和域控制器中默认具有管理员权限的组，是域森林中强大的服务管理组。
>
> Remote Desktop Users：远程登录组，处于远程登录组中的用户才有权限使用远程登录服务。
>
> Print Operators：打印机操作员组，位于该组内的成员可以管理网络中的打印机，包括建立、管理和删除网络打印机，并可以在本地登录和关闭域控制器。
>
> Account Operators：账号操作员组，该组的成员可以创建和管理该域中的用户和组并为其设置权限，也可以在本地登录域控制器，但是，不能更改属于
> Administrators 或 Domain Admins 组的账户，也不能修改这些组。在默认情况下，该组中没有成员。
>
> Server
> Operators：服务器操作员组，该组的成员可以管理域服务器，其权限包括建立/管理/删除任意服务器的共享目录、管理网络打印机、备份任何服务器的文件、格式化服务器硬盘、锁定服务器、变更服务器的系统时间、关闭域控制器等。在默认情况下，该组中没有成员。
>
>
> BackupOperators，备份操作员组，改组的成员可以在域控制器中执行备份和还原操作，并可以在本地登录和关闭域控制器。在默认情况下，该组中没有成员。

### 通用组（Universal Group）

通用组的成员可包括域林中任何域的用户账号、全局组和其他通用组，可以在该域林的任何域中指派权限，可以嵌套在其他组中，非常适合在域森林内的跨域访问中使用。

> 通用组的成员保存在全局编录服务器（GC）中而不是保存在各自的域控制器中，任何变化都会导致全林复制。
>
>
> 全局编录通常用于存储一些不经常发生变化的信息。由于用户账号信息是经常变化的，建议不要直接将用户账号添加到通用组中，而要先将用户账号添加到全局组中，再把这些相对稳定的全局组添加到通用组中。

通用组可以在所有域内被分配访问权限，以便访问所有域内的资源，比如林根域的`Enterprise
Admins`组。通用组具备万用领域的特性，其成员可以包含林中任何一个域内的用户、全局组和其他通用组。但是它无法包含任何一个域内的本地域组。通用组可以访问任何一个域内的资源、也就是说您可以在任何一个域内来设置通用组的权限，这个通用组可以位于任何一个域内，以便让此通用组具备权限来访问该域内的资源。

以下命令可以查询域内的所有通用组：

    
    
    Adfind.exe -b dc=whoamianony,dc=org -bit -f "(&(objectClass=group)(grouptype:AND:=8))" cn -dn

![image-20210725150655066](https://image.3001.net/images/20210806/1628258208_610d3fa028ae8d7ba2f49.png!small)

下面介绍两个的常见的系统内置的通用组及其组权限：

> Enterprise Admins：企业系统管理员组，改组是域森林根域中的一个组。Enterprise Admins 组在域森林中的每个域内都是
> Administrators 组的成员，因此对所有域控制器都有完全访问控制权。
>
> Schema Admins：架构管理员组，是域森林根域中的一个组，可以修改活动目录和域森林的模式。Schema Admins
> 组是为活动目录和域控制器提供完整权限的域用户组，因此，该组成员的资格是非常重要的。

### 全局组（Global Group）

前面说了，在单域中适用域本地组，在域林中适用通用组。而全局组则是一个介于二者中间一个组，它可以在域林中使用，但是只能包含本域内的账户。全局组的使用范围是本域以及受信任关系的其他域。

只能在创建该全局组的域中添加用户和全局组，也就是说全局组只能包含本域内的用户账户，因此来自一个域的账户不能嵌套在另一个域中的全局组中。这就是为什么来自同一个域的用户不符合在外部域中的域管的成员资格。但是可以将本域内某个全局组添加或嵌套到同一个域的另一个全局组中，或者添加到其他域的通用组和域本地组中。

以下命令可以查询域内的所有全局组：

    
    
    Adfind.exe -b dc=whoamianony,dc=org -bit -f "(&(objectClass=group)(grouptype:AND:=2))" cn -dn

![image-20210725150532282](https://image.3001.net/images/20210806/1628258208_610d3fa05d8d8e2b140d0.png!small)

下面介绍几个的常见的系统内置的全局组及其组权限：

> Domain Admins，管理员组，该组的成员在所有加入域的服务器、域控制器和活动目录中均默认拥有完整的管理员权限。因为该组会被添加到自己所在域的
> Administrators 组中，因此可以继承 Administrators 组的所有权限。同时，该组默认会被添加到每台域成员计算机的本地
> Administrators 组中，这样，Domain Admins
> 组就获得了域中所有计算机的所有权。如果希望某用户成为域系统管理员，建议将该用户添加到 Domain Admins 组中，而不要直接将该用户添加到
> Administrators 组中。
>
> Domain Users，域用户组，该组的成员中是所有的域用户。在默认情况下，任何由我们建立的更户账号都属于 Domain Users
> 组。因此，如果想让所有的账号都获得某种资源在取权限、可以将该权限指定给域用户组，或者让域用户组属于具有该权限的组。
>
> Domain Computers，域成员主机组，该组的成员是域内所有的域成员主机，任何由我们建立的计算机账号都属于 Domain Computers
> 组。
>
> Domain Controllers，域控制器组，该组成员包含了域内所有的域控制器。
>
> Domain Guests，域访客用户组，该组内的成员默认为域访客用户，域成员计算机会自动将此组加到本地的 Guests 组中。
>
> Group Policy Creator Owners：此组成员可以修改域的组策略。
>
> DnsUpdateProxy：此组成员允许替其他客户端（如DHCP服务器）执行动态更新的 DNS 客户端。
>
> Read-only Domain Controllers：此组中的成员是域中的只读域控制器

### 三种组作用域的比较

组类型| 作用范围| 可包含的成员| 成员是否在全局编录复制  
---|---|---|---  
域本地组| 在同一个域内，本域内。| 来自任何域或任何受信任域的帐户。 来自任何域或任何受信任域的全局组。 来自同一林中任何域的通用组。
来自同一域的其他域本地组。| 否  
通用组| 所有域。| 来自同一林中任何域的帐户。 来自同一林中任何域的全局组。 来自同一林中任何域的其他通用组。| 是  
全局组| 所有域。| 来自同一域的帐户。 来自同一域的其他全局组。| 否  
  
## 域组的建立

### 建立域组

建立域组很简单，下面我们以 Windows Server 2012 为例，建立一个名为 Domain Test 的域用户组。

首先在域控的 “管理工具” 中打开 “Active Directory 用户和计算机”，选中一个容器后右键 “新建” —> “组”：

![image-20210725142431240](https://image.3001.net/images/20210806/1628258208_610d3fa095741a7d28700.png!small)

输入组名并选择组作用域后点击确定即可：

![image-20210725142524344](https://image.3001.net/images/20210806/1628258209_610d3fa11557a3e34e6a4.png!small)

此时，执行以下命令：

    
    
    net group /domain

可以成功查询到刚刚建立的 Domain Test 组：

![image-20210725143056559](https://image.3001.net/images/20210806/1628258209_610d3fa16039714ad0ef8.png!small)

### 添加组成员

选择刚刚建立的组，右键 “属性” —> “成员” —> “添加”，输入域用户的名称，然后点击 “检查名称”，最后选择确定即可：

![image-20210725142850282](https://image.3001.net/images/20210806/1628258209_610d3fa1963431a6523ae.png!small)

![image-20210725142909847](https://image.3001.net/images/20210806/1628258209_610d3fa1e673b4ca9dc59.png!small)

此时，执行以下命令：

    
    
    net group Domain Test /domain

可以成功在 Domain Test 组中查询到刚刚添加的域用户 bunny ：

![image-20210725143227016](https://image.3001.net/images/20210806/1628258210_610d3fa22d186a9e36e56.png!small)

## 域组的查询

域环境中的组都是`group`类的实例，所以我们可以用`(objectClass=group)`或者`(objectCategory=group)`来查询域组。

> 上一篇文章中我们曾说过说过，在对象的 objectClass 属性里面，可以看到这个对象是哪一个类的实例，以及这个类所继承的所有父类。除此之外还有一个
> objectCategory 属性，该属性是一个单值属性。并且建立了索引。

如下查询所有域组：

    
    
    Adfind.exe -b dc=whoamianony,dc=org -f "(objectClass=group)" cn -dn  
    Adfind.exe -b dc=whoamianony,dc=org -f "(objectCategory=group)" cn -dn

![image-20210725145101496](https://image.3001.net/images/20210806/1628258210_610d3fa258d090bedd761.png!small)

那我们该如何区分不同作用域的域组呢？域组的作用类型是由其属性`groupType`决定，该`groupType`是一个位字段，所以这里涉及到了按为查询。以下是`groupType`属性各个位所代表的含义：

属性值| 说明  
---|---  
1 (0x00000001)| 指定一个组为系统创建的组  
2 (0x00000002)| 指定一个组为全局组  
4 (0x00000004)| 指定一个组为域本地组  
8 (0x00000008)| 指定一个组为通用组  
16 (0x00000010)| 为 Windows Server 授权管理器指定一个 APP_BASIC 组  
32 (0x00000020)| 为 Windows Server 授权管理器指定一个 APP_QUERY 组  
2147483648 (0x80000000)| 指定一个组为安全组， 如果未设置此位标志，则该组默认是通讯组  
  
知道了`groupType`属性各个位代表的含义后，我们便可以对域组进行按位查询了。

查询域内的所有全局组：

    
    
    Adfind.exe -b dc=whoamianony,dc=org -bit -f "(&(objectClass=group)(grouptype:AND:=2))" cn -dn

![image-20210725150532282](https://image.3001.net/images/20210806/1628258208_610d3fa05d8d8e2b140d0.png!small)

查询域内的所有通用组：

    
    
    Adfind.exe -b dc=whoamianony,dc=org -bit -f "(&(objectClass=group)(grouptype:AND:=8))" cn -dn

![image-20210725150655066](https://image.3001.net/images/20210806/1628258208_610d3fa028ae8d7ba2f49.png!small)

查询域内的所有域本地组：

    
    
    Adfind.exe -b dc=whoamianony,dc=org -bit -f "(&(objectClass=group)(grouptype:AND:=4))" cn -dn

![image-20210725150747080](https://image.3001.net/images/20210806/1628258207_610d3f9fe9deda8667dcd.png!small)

查询域内的所有安全组，包括全局组，通用组，域本地组：

    
    
    Adfind.exe -b dc=whoamianony,dc=org -bit -f "(&(objectClass=group)(grouptype:AND:=2147483648))" cn -dn

![image-20210725150936937](https://image.3001.net/images/20210806/1628258211_610d3fa36a67813339bbb.png!small)

查询域内的所有通讯组：

    
    
    Adfind.exe -b dc=whoamianony,dc=org -bit -f "(&(objectClass=group)(!(grouptype:AND:=2147483648)))" cn -dn  
    # 即不是安全组的其他的组

查询域内系统创建的群组：

    
    
    Adfind.exe -b dc=whoamianony,dc=org -bit -f "(&(objectClass=group)(grouptype:AND:=1))" cn -dn

![image-20210725151224994](https://image.3001.net/images/20210806/1628258211_610d3fa3b86ac39ee0387.png!small)

## AGDLP 权限划分策略介绍

安全组就是域内权限的集合，所以在域环境中我们并不建议单独赋予某个用户权限，而是赋予一个组权限，然后将用户拉近这个组。AGDLP，A-G-DL-P
策略是指将用户账号（A）添加到全局组（G）中，将全局组（G）添加到域本地组（DL）中，然后为域本地组（DL）分配资源权限（P）。

> A（Account）表示用户账号
>
> G（Global Group）表示全局组
>
> U（Universal Group）表示通用组
>
> L（Local Group）表示本地组
>
> DL（Domain Local Group）表示域本地组
>
> P（Resource Permissions）表示资源权限

按照 AGDLP 权限划分策略对域用户进行组织和管理十分方便，在 AGDLP
策略形成之后，如果需要给一个用户添加某个特定权限时，只需要把这个用户添加到其所在域的域本地组中就行了。下面我们来举一个例子说明。

> 假设，你有两个域，a.com 和 b.com，a.com 中的 5 个财务人员和 b.com 中的 3 个财务人员都需要访问 B 中的 “FINA”
> 文件夹，这时，你可以在 b.com 中建一个域本地组（DL），因为域本地组（DL）的成员可以来自所有的域，然后把这 8
> 个人都加入这个域本地组（DL），并把 FINA 的访问权赋给域本地组（DL）。但是这样做的坏处是什么呢？因为域本地组（DL）是在 b.com
> 域中，所以管理权也在 b.com 域，如果 a.com 域中的 5 个人变成 6 个人，那只能 a.com 域管理员通知 b.com
> 域管理员，将域本地组（DL）的成员做一下修改， 这样 b.com 域的管理员就太累了。
>
> 这时候，我们可以改变一下思路，在 a.com 和 b.com 域中都各建立一个全局组（G），然后在 b.com
> 域中建立一个域本地组（DL），把这两个全局组（G）都加入 b.com 域的域本地组（DL）中，然后把 FINA 的访问权赋给
> DL。这下两个全局组（G）就都有权访问 FINA 文件夹了。此时，这两个全局组（G）分布在 A 和 B 域中，也就是 a.com 域和 b.com
> 域的管理员便都可以自己管理自己的全局组（G）了，只要把那 5 个人和 3
> 个人分别加入各自的全局组（G）中就可以了。以后有任何修改，都可以自己做了，再也不用麻烦 b.com 域的管理员了。

除了 AGDLP 策略以外，还有几种常见的权限划分方式：

> AGP：A-G-P，将用户账号（A）添加到全局组（G），然后为全局组分配资源权限（P）。
>
> AGLP：A-G-L-P，将用户账号（A）添加到全局组（G），将全局组（G）添加到本地组（L）， 然后为本地组（L）分配资源权限（P）。
>
> ADLP：A-DL-P，将用户账号（A）添加到域本地组（DL），然后为域本地组（DL）分配资源权限（P）。
>
> AGDLP：A-G-DL-P，将用户账号（A）添加到全局组（G），将全局组（G）添加到域本地组（DL）， 然后为域本地组（DL）分配资源权限（P）。
>
> AGUDLP，A-G-U-DL-P，将用户账号（A）添加到全局组（G），将全局组（G）添加到通用组（U），将通用组（U）添加到域本地组（DL），
> 然后为域本地组（DL）分配资源权限（P）。

## Ending......

![20210730222957.jpg](https://image.3001.net/images/20210806/1628258211_610d3fa3f15748c4a1cb1.jpg!small)

> 参考：
>
> <https://www.anquanke.com/post/id/195737#h2-11>
>
> <https://daiker.gitbook.io/windows-protocol/ldap-pian/9#0x02-zu-zhi-dan-wei-> organization-unit>
>
> <https://docs.microsoft.com/zh-cn/windows-server/identity/ad-ds/active-> directory-functional-levels>
>
> <https://baike.baidu.com/item/AGDLP/10014146?fr=aladdin>
>
> <https://blog.csdn.net/qq_36119192/article/details/112471464>

