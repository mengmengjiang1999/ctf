# 运用命令行、注册表编程、windowsAPI修改本地安全策略

阅读量 **411926**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-05-22 10:30:00

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01d15207aa6ead1cbe.png)

## 0、本地安全策略介绍

windows安全策略个人理解就是计算机使用者对计算机进行的一些了安全配置。配置安全策略的方法是：Control Panel->Administrative
tool->Local Security Policy。

![](https://p4.ssl.qhimg.com/t011bfa062cf2307484.png)

(注意需要把右上角的视图改为大图标，一般是按类别)

![](https://p4.ssl.qhimg.com/t01b882c6f87d644a06.png)

![](https://p1.ssl.qhimg.com/t01054f06e0bda3ba60.png)

以win10系统为例。一级安全策略有： **账户策略(Account Policies)、本地策略(Local Policies)、高级安全windows
Defender 防火墙(Windows Defender Firewall with Advanced)、网络列表管理器策略(Network List
Manager Polices)、公钥策略(Public Key Policies)、软件限制策略(Software Restriction
Policies)、应用程序控制策略(Application Control Policies )、IP安全策略(IP Security Policies
on Local Computer)、高级审计策略配置(Advanced Audit Policy Configuration)。**

![](https://p4.ssl.qhimg.com/t01bcc6f586e3309c71.png)

具体的内容可以自己去MSDN上找，可以根据自己的需求进行配置。这部分并不是本文的主要内容。本文主要是用过本地策略中的审核策略和高级审核策略来进行如题中的三种配置。其他策略理论上也是可以配置的，比较麻烦的就是在MSDN上寻找资料。（当初我也是这么过来的）。  
稍微拓展一点就是本地安全审核策略和高级审核策略到底有什么不同呢。简单来数就是高级审核策略就是本地安全审核策略的细化版。下图就是本地安全审核策略，可以看到里面一共有九个项

![](https://p5.ssl.qhimg.com/t010be4bccff98e2e2d.png)

之后观察高级审核策略，发现里面的二级策略就有十个，且基本和本地安全策略一致

![](https://p4.ssl.qhimg.com/t01cd42c2b4b91aca35.png)

随便进其中一个二级策略发现里面是更加细化的一些配置。这两个策略虽然互有重叠，但是还是有区别的。总的来说就是两种策略都配置的话以高级审核策略为主。如果需要回退到本地安全策略，则需要将所有的高级审核策略设置为：不审核（“Not
audting”）。

## 1、命令行配置

接下来就是正题了。首先介绍的就是命令行配置。对于高级审核策略来说，命令行配置用到的命令叫做： **auditpol**

这个命令的语法如下

`Auditpol /set [/user[:<username>|<{sid}>][/include][/exclude]]
[/category:<name>|<{guid}>[,:<name|<{guid}>]]
[/success:<enable>|<disable>][/failure:<enable>|<disable>]
[/subcategory:<name>|<{guid}>[,:<name|<{guid}>]]
[/success:<enable>|<disable>][/failure:<enable>|<disable>] [/option:<option
name> /value: <enable>|<disable>]`

具体解释如下

* * *

/user：为其设置类别或子类别指定的每用户审核策略的安全主体。 必须指定 “类别” 或 “子类别” 选项，作为安全标识符（SID）或名称。

/include：用/user 指定;指示用户的每用户策略将导致生成审核，即使系统审核策略未指定审核也是如此。 此设置是默认设置，如果/include
和/exclude 参数均未显式指定，则会自动应用此设置。

/exclude：用/user 指定;指示无论系统审核策略如何，用户的每用户策略都将导致抑制审核。 对于作为本地 Administrators
组成员的用户，此设置将被忽略。

/category：由全局唯一标识符（GUID）或名称指定的一个或多个审核类别。 如果未指定用户，则设置系统策略。

/subcategory：GUID 或名称指定的一个或多个审核子类别。 如果未指定用户，则设置系统策略。

/success：指定成功审核。 此设置是默认设置，如果/success 和/failure 参数均未显式指定，则会自动应用此设置。
此设置必须与指示是否启用或禁用该设置的参数一起使用。

/failure：指定失败的审核。 此设置必须与指示是否启用或禁用该设置的参数一起使用。

/option：为 CrashOnAuditFail、FullprivilegeAuditing、AuditBaseObjects 或
AuditBasedirectories 选项设置审核策略。

/sd：设置用于委托审核策略访问的安全描述符。 安全描述符必须使用安全描述符定义语言（SDDL）来指定。 安全描述符必须具有自由访问控制列表（DACL）。

/? 在命令提示符下显示帮助。

* * *

知道以上信息之后就可以利用命令行修改高级审核策略，记得要使用管理员权限打开命令行窗口

由于高级审核策略比较多，这里就以”Account Logon”、”Account Management”、”DS Access”为例子，其他的大同小异。

这里将Account Logon里的子策略都设置为Scccess

![](https://p2.ssl.qhimg.com/t01350702f76a78c7b6.png)

这里将Account Management里的子策略都设置为Scccess

![](https://p1.ssl.qhimg.com/t0171890d1af33cb643.png)

这里将DS Access里的子策略都设置为Failure

![](https://p2.ssl.qhimg.com/t012381f81b190cc364.png)

## 2、注册表编程

windows注册表这个机制一直饱受争议，喜欢的人把它吹得老高了，不喜欢的人又把它贬得老低了。（因为我还比较菜，所以不做评论。）国内对这方面的资料不是那么好找，比如要找高级安全策略对应的注册表项就找不到。当然不是所有的安全策略都有对应的注册表项。不确定的可以去MSDN上搜索对应计算机版本的Group
Policy Settings Reference Spreadsheet。我去找的时候是有一个excel，里面有各种策略对应的注册表项。

反正最后呢，在国外某个大佬的博客上找到一个很有用的信息。根据<https://countuponsecurity.com/tag/poladtev/>
这个博主的信息，高级安全审核策略对应注册表的处在HKEY_LOCAL_MACHINESecurityPolicyPolAdtEv
key并且可以得到一个比较直观的图片。

![](https://p4.ssl.qhimg.com/t01cc40ff129090fef7.png)

从这张图片可以看出来，每一个策略下面的子策略对应注册表中的位置很清楚的标出来。那么进行修改的时候只要将对应位置上的值修改为自己想要的就行了。一共有四个值：
**00 00——No Auditing、01 00 ——Success、02 00——Failure、03 00 ——-SuccessFailure**
。只要按照如下进行修改就行了

![](https://p3.ssl.qhimg.com/t01c3c49ad1cd818ef7.png)

完整脚本如下（使用powershell）：

    
    
    function Set-RegistryValue
    {
        $Parameters = @{
            Path        = $Registry.Path
            Name        = $Registry.ValueName
            ErrorAction = 'SilentlyContinue'
        }
    
        Get-ItemProperty @Parameters
    
        Remove-ItemProperty @Parameters
    
        $Parameters.Remove('ErrorAction')
        $Parameters.Add('Value', $Registry.ValueData)
        $Parameters.Add('PropertyType', $Registry.ValueType)
    
        New-ItemProperty @Parameters
    }
    
    #region Add access for Administrators
    $RegistrySubKey = 'SECURITY'
    
    $RegistryKeyControl = [Microsoft.Win32.Registry]::
    LocalMachine.OpenSubKey(
    $RegistrySubKey,
    [Microsoft.Win32.RegistryKeyPermissionCheck]::ReadWriteSubTree,
    [System.Security.AccessControl.RegistryRights]::ChangePermissions
    )
    
    $AccessControlList = $RegistryKeyControl.GetAccessControl()
    $BackupOfAccessControlList = $RegistryKeyControl.GetAccessControl()
    
    $Account = [System.Security.Principal.NTAccount]'BUILTINAdministrators'
    $Permissions = [System.Security.AccessControl.RegistryRights]'FullControl'
    $InheritanceFlag = [System.Security.AccessControl.InheritanceFlags]'ContainerInherit,ObjectInherit'
    $PropagationFlag = [System.Security.AccessControl.PropagationFlags]'None'
    $AccessType = [System.Security.AccessControl.AccessControlType]'Allow'
    
    $AccessRule = New-Object System.Security.AccessControl.RegistryAccessRule(
    $Account,
    $Permissions,
    $InheritanceFlag,
    $PropagationFlag,
    $AccessType
    )
    
    $AccessControlList.AddAccessRule($AccessRule)
    
    $RegistryKeyControl.SetAccessControl($AccessControlList)
    #endregion
    
    #region set audit values
    #Advanced Audit Policy Configuration
    #https://countuponsecurity.com/tag/poladtev
    #https://www.kazamiya.net/files/PolAdtEv_Structure_en_rev2.pdf
    $Registry = @{
    Path = 'HKLM:SecurityPolicyPolAdtEv'
    ValueName = '(default)'
    ValueData = [byte[]] @(
    0, 1, 0, 0, 9, 0, 0, 0, 128, 0, 0, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3,
    0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3,
    0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3,
    0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3,
    0, 3, 0, 0, 0, 5, 0, 10, 0, 14, 0, 3, 0, 5, 0, 6, 0, 6, 0, 4, 0, 4, 0
    )
    ValueType = 'None'
    }
    
    Set-RegistryValue
    
    #Audit: Force audit policy subcategory settings (Windows Vista or later) to override audit policy category settings ==&gt; Enabled
    #https://technet.microsoft.com/en-us/library/jj852246(v=ws.11).aspx
    $Registry.Path = 'HKLM:SYSTEMCurrentControlSetControlLsa'
    $Registry.ValueName = 'SCENoApplyLegacyAuditPolicy'
    $Registry.ValueData = 1
    $Registry.ValueType = 'DWord'
    
    Set-RegistryValue
    #endregion
    
    #region Remove access for Administrators
    $RegistryKeyControl.SetAccessControl($BackupOfAccessControlList)
    #endregion
    

需要注意的时,powershell需要使用管理员权限打开。并且windows出于安全性的考虑，默认情况下这个脚本是无法运行的

![](https://p0.ssl.qhimg.com/t017f14a56311b63f9d.png)

原因是因为默认情况下LocalMachine进行了限制

![](https://p5.ssl.qhimg.com/t01c7881d1fadc8726a.png)

针对这个问题有两种解决方法，第一个不安全的做法就是直接解开限制，第二个是打开临时授权。在这里选择直接解开限制，运行完之后再加上限制

![](https://p5.ssl.qhimg.com/t018ee490e393242107.png)

接下来脚本就可以运行成功了

![](https://p3.ssl.qhimg.com/t018d1a0d5e9e0e77d4.png)

## 3、Windows API编程

有句老话说得好：windows一切即对象，linux一切即文件。这一句话的前半句在这部分深有体会。怎么说呢，既然想要用Windows
API进行编程，最权威的就是MSDN了，但是呢MSDN的排版有的时候又会让人很抓狂，有些函数你就是找不到，找到了但是但看这个你又用不了，又得看另一个函数，看着看着，就看了几十个函数。十分难受。所以这里把思路发出来也是避免后人走弯路（看文档真的老费时间了）

审核策略的话主要是用了几个结构，下面一一介绍一下。

###  3.1结构体

    
    
    POLICY_INFORMATION_CLASS
    typedef enum _POLICY_INFORMATION_CLASS {
      PolicyAuditLogInformation,
      PolicyAuditEventsInformation,
      PolicyPrimaryDomainInformation,
      PolicyPdAccountInformation,
      PolicyAccountDomainInformation,
      PolicyLsaServerRoleInformation,
      PolicyReplicaSourceInformation,
      PolicyDefaultQuotaInformation,
      PolicyModificationInformation,
      PolicyAuditFullSetInformation,
      PolicyAuditFullQueryInformation,
      PolicyDnsDomainInformation,
      PolicyDnsDomainInformationInt,
      PolicyLocalAccountDomainInformation,
      PolicyMachineAccountInformation,
      PolicyLastEntry
    } POLICY_INFORMATION_CLASS, *PPOLICY_INFORMATION_CLASS;
    

这个结构在代码中并没有用，但是这里起到一个引导作用。也就是说这个结构里面的很多成员其实对应的就是安全策略
中的某一项，比如说第一个和第二个就是跟审核策略相关的。之后再找其对应的内容就好了（相当于一个方法论，留着大家继续研究）

    
    
    POLICY_AUDIT_EVENTS_INFO
    typedef struct _POLICY_AUDIT_EVENTS_INFO {
      BOOLEAN                     AuditingMode;
      PPOLICY_AUDIT_EVENT_OPTIONS EventAuditingOptions;
      ULONG                       MaximumAuditEventCount;
    } POLICY_AUDIT_EVENTS_INFO, *PPOLICY_AUDIT_EVENTS_INFO;
    

这个结构就要用到了，具体内容子啊MSDN上都用，但是看文档好费眼和时间，这里就粗略介绍一下，想深入的话还是推荐看官方文档。  
第一个成员变量表示是否可以对审核策略进行修改，true代表可以，false代表不行。第二个成员变量代表策略的具体内容分别是：unchanged、success、failure、none。第三个参数代表目前这个结构支持修改的策略数量。

    
    
    POLICY_AUDIT_EVENT_TYPE
    typedef enum _POLICY_AUDIT_EVENT_TYPE {
      AuditCategorySystem,
      AuditCategoryLogon,
      AuditCategoryObjectAccess,
      AuditCategoryPrivilegeUse,
      AuditCategoryDetailedTracking,
      AuditCategoryPolicyChange,
      AuditCategoryAccountManagement,
      AuditCategoryDirectoryServiceAccess,
      AuditCategoryAccountLogon
    } POLICY_AUDIT_EVENT_TYPE, *PPOLICY_AUDIT_EVENT_TYPE;
    

这个结构就是目前支持可修改的高级审核策略。未来还有可能拓展。

###  3.2 API接口函数

这里用到的API主要有三个。

    
    
    LsaOpenPolicy
    NTSTATUS LsaOpenPolicy(
      PLSA_UNICODE_STRING    SystemName,
      PLSA_OBJECT_ATTRIBUTES ObjectAttributes,
      ACCESS_MASK            DesiredAccess,
      PLSA_HANDLE            PolicyHandle
    );
    

这个函数比较 好理解就是打开Lsa句柄。（Lsa—-Local Security Auditing）  
第一个参数就是要访问策略的计算机名，设为NULL代表本地计算机；第二个参数一般都是ZeroMemory这个函数置为0使用；第三个参数代表访问权限，需要设置为ACCESS_MASK；最后一个参数就是打开的句柄。如果函数执行成功那么返回结果是STATUS_SUCCESS，但是在实际编程中（VS
Code），返回结果是CMS_STATUS_SUCCESS。（我实验的环境是VS
Code，可能别的编译器的值会有所不同吧，官方文档里给的返回值是STATUS_SUCCESS）

    
    
    LsaQueryInformationPolicy function
    NTSTATUS LsaQueryInformationPolicy(
      LSA_HANDLE               PolicyHandle,
      POLICY_INFORMATION_CLASS InformationClass,
      PVOID                    *Buffer
    );
    

函数的功能就是枚举审核策略；第一个参数是PolicyHandle的句柄，通过LsaOpenPolicy这个函数获得，第二个参数通过要获得的不同策略的对象进行设置，在这里设置为PolicyAuditEventsInformation。最后一个参数是指针，指向要获得策略的地址。

    
    
    LsaSetInformationPolicy function
    NTSTATUS LsaSetInformationPolicy(
      LSA_HANDLE               PolicyHandle,
      POLICY_INFORMATION_CLASS InformationClass,
      PVOID                    Buffer
    );
    

这个函数的功能就是修改本地策略，参数于LsaSetInformationPolicy基本一致，但是要注意最后一个参数不是指针，在这里要特别注意。返回结果也是一致的。

###  3.3具体实现

接下来就是具体编程了，代码中对原有API进行了封装。主要是三个：GetHandle()用来返回句柄、Get_Sec_AuditSetting()用来打印当前策略、SET_Audit_Policy()用来对策略进行设置。

首先来看一下GetHandle()

    
    
    LSA_HANDLE GetHandle()
    {
        LSA_HANDLE myPolicyHandle;
        LSA_OBJECT_ATTRIBUTES ObjectAttributes;
        PVOID *Buffer;
        ZeroMemory(&ObjectAttributes, sizeof(ObjectAttributes));
    
        NTSTATUS tmp1 = LsaOpenPolicy(NULL,&ObjectAttributes,POLICY_ALL_ACCESS,&myPolicyHandle);
        if(tmp1 == ERROR_SUCCESS){
            printf("get handle successfully!n");
            return myPolicyHandle;
        }
        printf("failed to get handle!n");
        return NULL;
    }
    

这个就是调用LsaOpenPolicy这个API进行创建句柄，至于为什么要用ZeroMemory在介绍LsaOpenPolicy函数的时候有介绍了。如果创建句柄成功，则会返沪改句柄

    
    
    BOOL Get_Sec_AuditSetting()
    {
        LSA_HANDLE handle = GetHandle();
         PPOLICY_AUDIT_EVENTS_INFO pInfo;
         string tmp;
         if(handle){
             NTSTATUS status = LsaQueryInformationPolicy(handle,PolicyAuditEventsInformation,(void **)&pInfo);
             //cout<<"MaximumAuditEventCount:"<<pInfo->MaximumAuditEventCount<<endl;
             if(status == CMC_STATUS_SUCCESS && pInfo->AuditingMode){
                 for(int i =0;i<pInfo->MaximumAuditEventCount;i++)
                 {
                     switch(i)
                     {
                        case AuditCategoryAccountLogon:
                            tmp = GET_AUDIT_STR("Audit Account Logon: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
                        case AuditCategoryAccountManagement:
                            tmp = GET_AUDIT_STR("Audit Account Management: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
                        case AuditCategoryDetailedTracking:
                            tmp = GET_AUDIT_STR("Audit Detailed Tracking: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
                        case AuditCategoryDirectoryServiceAccess:
                            tmp = GET_AUDIT_STR("Audit CategoryDirectory Service Access: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
                        case AuditCategoryLogon:
                            tmp = GET_AUDIT_STR("Audit Logon/Logoff: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
                        case AuditCategoryObjectAccess:
                            tmp = GET_AUDIT_STR("Audit Object Access: ",pInfo,i);
                            cout<<tmp<<endl;
    
                        case AuditCategoryPolicyChange:
                            tmp = GET_AUDIT_STR("Audit Policy Change: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
                        case AuditCategoryPrivilegeUse:
                            tmp = GET_AUDIT_STR("Audit Privilege Use: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
                        case AuditCategorySystem:
                            tmp = GET_AUDIT_STR("Audit System: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
    
                        default:
                            break;
                     }
    
                 }
             }
             else{
                 printf("STATUES ERROR %u",status);
             }
    
         }
         return true;
    }
    

在结构体介绍那一节介绍了MaximumAuditEventCount这个成员变量代表策略的数量，实际上，具体是哪一个策略其实是有值表示的，代码中诸如：AuditCategoryAccountLogon等其实有对应的具体数值。根据匹配当前指针指向的内存的值就可以判断是哪一个策略。致于代码中出现的GET_AUDIT_STR其实就是一个打印字符，根据该策略的状态是否是Succuss或Failure来进行打印字符。

    
    
    void SET_Audit_Policy(POLICY_AUDIT_EVENT_TYPE eventtype,POLICY_AUDIT_EVENT_OPTIONS eventoption)
    {
    
    
        LSA_HANDLE handle = GetHandle();
        POLICY_AUDIT_EVENTS_INFO *AuditEvent ;
        NTSTATUS status;
        status = LsaQueryInformationPolicy(handle,PolicyAuditEventsInformation,(void **)&AuditEvent);
        //AuditEvent->AuditingMode = true;
        AuditEvent->EventAuditingOptions[eventtype] = eventoption;
        //cout<<"!!!"<<endl;
        status = LsaSetInformationPolicy(handle,PolicyAuditEventsInformation,(void *)AuditEvent);
             if(status == CMC_STATUS_SUCCESS )
             {
                 cout<<"Set successfully!n";
             }
             else
             {
                 cout<<"Failed to set!n";
             }
    }
    

SET_Audit_Policy这个函数也比较好理解。解释一下参数就很容易明白。eventtype代表的要修改的策略，比如：AuditCategoryAccountLogon、AuditCategoryAccountManagement等等。第二个参数eventoption就是设置的策略是Success、Failure或者SuccessFailure都可以

主函数也很好理解，直接把整个代码都贴一下(要成功运行的话，编译器也要以管理员权限打开哦)

    
    
    #include "stdio.h"
    #include "stdlib.h"
    #include "windows.h"
    #include "tchar.h"
    #include "Winreg.h"
    #include "shlwapi.h"
    #include "Ntsecapi.h"
    //#include "ntifs.h"
    #include <iostream>
    #include <string>
    #include <vector>
    #include <sddl.h>
    #include <cstdlib>
    using namespace std;
    
    LSA_HANDLE GetHandle();
    BOOL Get_Sec_AuditSetting();
    void SET_Audit_Policy(POLICY_AUDIT_EVENT_TYPE eventtype,POLICY_AUDIT_EVENT_OPTIONS eventoption);
    string GET_AUDIT_STR(string s,PPOLICY_AUDIT_EVENTS_INFO pInfo,int i);
    
    int _tmain(int argc, _TCHAR* argv[])
    {
        //string result;
         Get_Sec_AuditSetting();
         while(1)
         {
        cout<<"Please choose one of the Audit Policies to set:n";
        cout<<"1: Account Logonn";
        cout<<"2: Account Managementn";
        cout<<"3: Detailed Trackingn";
        cout<<"4: DS Accessn";
        cout<<"5: Logon/Logoffn";
        cout<<"6: Object Accessn";
        cout<<"7: Policy Changen";
        cout<<"8: Privilege Usen";
        cout<<"9: Systemn";
        cout<<"0: exitn";
        cout<<"Input the numboer of your chioce:";
        int EventType,EventOption;
        cin>>EventType;
    
        if(EventType == 0)
        {
            break;
        }
    
        cout<<"Please choose the configuration you want to set:n";
        cout<<"1: Successn";
        cout<<"2: Failuren";
        cin>>EventOption;
    
        POLICY_AUDIT_EVENT_TYPE eventtype;
        POLICY_AUDIT_EVENT_OPTIONS eventoption = POLICY_AUDIT_EVENT_SUCCESS;
    
        if(EventOption == 1)
        {
            eventoption = POLICY_AUDIT_EVENT_SUCCESS;
        }
    
        else
        {
            eventoption = POLICY_AUDIT_EVENT_FAILURE;
        }
    
    
        switch (EventType)
        {
            case 1:
                eventtype = AuditCategoryAccountLogon;
                break;
            case 2:
                eventtype = AuditCategoryAccountManagement;
                break;
            case 3:
                eventtype = AuditCategoryDetailedTracking;
                break;
            case 4:
                eventtype = AuditCategoryDirectoryServiceAccess;
                break;
            case 5:
                eventtype = AuditCategoryLogon;
                break;
            case 6:
                eventtype = AuditCategoryObjectAccess;
                break;
            case 7:
                eventtype = AuditCategoryPolicyChange;
                break;
            case 8:
                eventtype = AuditCategoryPrivilegeUse;
                break;
            case 9:
                eventtype = AuditCategorySystem;
                break;
    
        }
         SET_Audit_Policy(eventtype,eventoption);
         }
         cout<<"After settingn";
         Get_Sec_AuditSetting();
         system("pause");
         return 0;
    
    }
    
    
    LSA_HANDLE GetHandle()
    {
        LSA_HANDLE myPolicyHandle;
        LSA_OBJECT_ATTRIBUTES ObjectAttributes;
        PVOID *Buffer;
        ZeroMemory(&ObjectAttributes, sizeof(ObjectAttributes));
    
        NTSTATUS tmp1 = LsaOpenPolicy(NULL,&ObjectAttributes,POLICY_ALL_ACCESS,&myPolicyHandle);
        if(tmp1 == ERROR_SUCCESS){
            printf("get handle successfully!n");
            return myPolicyHandle;
        }
        printf("failed to get handle!n");
        return NULL;
    }
    string GET_AUDIT_STR(string x,PPOLICY_AUDIT_EVENTS_INFO pInfo,int i)
    {
    
        string str;
        string result;
        if(POLICY_AUDIT_EVENT_SUCCESS&pInfo->EventAuditingOptions[i]){
            str+="Success";
        }
        if(POLICY_AUDIT_EVENT_FAILURE&pInfo->EventAuditingOptions[i]){
            str+=str.size()==0?"Failure":"| Failure";
        }
        if(str.size() == 0){
            str+="No Audit";
        }
        //str+="n";
        result = x+str;
        return result;
    
    }
    
    BOOL Get_Sec_AuditSetting()
    {
        LSA_HANDLE handle = GetHandle();
         PPOLICY_AUDIT_EVENTS_INFO pInfo;
         string tmp;
         if(handle){
             NTSTATUS status = LsaQueryInformationPolicy(handle,PolicyAuditEventsInformation,(void **)&pInfo);
             //cout<<"MaximumAuditEventCount:"<<pInfo->MaximumAuditEventCount<<endl;
             if(status == CMC_STATUS_SUCCESS && pInfo->AuditingMode){
                 for(int i =0;i<pInfo->MaximumAuditEventCount;i++)
                 {
                     switch(i)
                     {
                        case AuditCategoryAccountLogon:
                            tmp = GET_AUDIT_STR("Audit Account Logon: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
                        case AuditCategoryAccountManagement:
                            tmp = GET_AUDIT_STR("Audit Account Management: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
                        case AuditCategoryDetailedTracking:
                            tmp = GET_AUDIT_STR("Audit Detailed Tracking: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
                        case AuditCategoryDirectoryServiceAccess:
                            tmp = GET_AUDIT_STR("Audit CategoryDirectory Service Access: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
                        case AuditCategoryLogon:
                            tmp = GET_AUDIT_STR("Audit Logon/Logoff: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
                        case AuditCategoryObjectAccess:
                            tmp = GET_AUDIT_STR("Audit Object Access: ",pInfo,i);
                            cout<<tmp<<endl;
    
                        case AuditCategoryPolicyChange:
                            tmp = GET_AUDIT_STR("Audit Policy Change: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
                        case AuditCategoryPrivilegeUse:
                            tmp = GET_AUDIT_STR("Audit Privilege Use: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
                        case AuditCategorySystem:
                            tmp = GET_AUDIT_STR("Audit System: ",pInfo,i);
                            cout<<tmp<<endl;
                            break;
    
                        default:
                            break;
                     }
    
                 }
             }
             else{
                 printf("STATUES ERROR %u",status);
             }
    
         }
         return true;
    }
    
    void SET_Audit_Policy(POLICY_AUDIT_EVENT_TYPE eventtype,POLICY_AUDIT_EVENT_OPTIONS eventoption)
    {
    
    
        LSA_HANDLE handle = GetHandle();
        POLICY_AUDIT_EVENTS_INFO *AuditEvent ;
        NTSTATUS status;
        status = LsaQueryInformationPolicy(handle,PolicyAuditEventsInformation,(void **)&AuditEvent);
        //AuditEvent->AuditingMode = true;
        AuditEvent->EventAuditingOptions[eventtype] = eventoption;
        //cout<<"!!!"<<endl;
    
        status = LsaSetInformationPolicy(handle,PolicyAuditEventsInformation,(void *)AuditEvent);
             if(status == CMC_STATUS_SUCCESS )
             {
                 cout<<"Set successfully!n";
             }
             else
             {
                 cout<<"Failed to set!n";
             }
    }
    

这里可以看一下运行结果

首先是调用的枚举函数，可以知道除了Account Logon外其他都没被配置（这个是之前测试时配置的）

![](https://p4.ssl.qhimg.com/t012fd7834f7364321d.png)

之后进行配置，这里配置Accoun tManagement并配置为Failure

![](https://p2.ssl.qhimg.com/t012ae9e9d547572ac0.png)

最后再运行枚举的接口函数，可以发现这时候Account Logon和Account Management都已经被设置为各自的值了

![](https://p2.ssl.qhimg.com/t01fee0e87b982e0aa2.png)

## 4后记

整个流程下来，学习到了很多知识，当然还有很多不足。对于查看MSDN文档然后进行编程我觉得对于我的能力提高有很大帮助，自己目前还是个菜鸟，希望未来能向大牛看齐。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **fightingman** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/202639](/post/id/202639)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Windows](/tag/Windows)
  * [系统安全](/tag/系统安全)

 **+1** __6赞

 __收藏

![](https://p1.ssl.qhimg.com/t0134280c7759acdc58.png) fightingman

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

