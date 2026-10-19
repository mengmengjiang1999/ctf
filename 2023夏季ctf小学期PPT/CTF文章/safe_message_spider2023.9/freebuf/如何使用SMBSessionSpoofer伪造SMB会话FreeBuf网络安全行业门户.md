![](https://image.3001.net/images/20220623/1655994360_62b477f804f0ee66b58f9.jpeg!small)

## 关于SMBSessionSpoofer

SMBSessionSpoofer是一款针对SMB会话的安全工具，该工具可以帮助广大研究人员轻松创建出一个伪造的SMB会话，并以此来欺骗攻击者访问和进入蜜罐设备。该工具虽然结构简单，但功能强大，我们只需要将其cpp主程序文件下载下来，并在Visual
Studio 2019中进行编译后，即可上手使用。

## 工具机制

当攻击者运行SharpHound并收集目标组织中的会话信息时，会根据自己的经验来分析针对目标主体的攻击路径，并且还可以识别在第二层基础设施（工作站）中登录了的高权限用户。接下来，他们会尝试访问并导出凭证以获取域管理员访问权限。

在上诉场景中，攻击者已经入侵了"wadm-tom@contoso.com"用户，即lab-wkst-2.contoso.com的本地管理员。而用户"svc-admin"已经在lab-wkst-2.contoso.com登录了，那么这也就意味着，攻击者需要做的就是直接登录工作站，运行Mimikatz并导出凭证。攻击路径如下图所示：

![](https://image.3001.net/images/20220623/1655994370_62b478028e7ad944b2d23.png!small)

不过，这一切都是我们营造出来的假象，那么我们该如何捕捉和监控这种行为呢？

## 监控配置

该工具的实现和部署非常重要，而过程监控也同样重要。如果在不执行监控的情况下，使用该工具是没有任何意义的。监控主机最有效的方法就是在出现任何登录行为的时候便发送警报。SMBSessionSpoofer最好在没有用户活动的主机上使用，并将标准的协同监控工具（例如EDR、AV或Windows
Event Log Forwarding等）加入到同一域中。

我们建议使用电子邮件警报或SMS警报，以此来确保我们能够在第一时间接收到相关警报信息。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Sq00ky/SMB-Session-Spoofing.git

## 工具使用

### 程序修改指令

使用之前，我们需要对程序代码稍微进行修改。在主文件的第144行，代码调用了CreateProcessWithLogonW API（一个Windows
API），这里需要提供两个参数，即svc-admin（用户名）和contoso.com（域），因此我们需要根据实际环境来提供这两个值：

    
    
    CreateProcessWithLogonW(L"DomainAdminUser", L"YourDomain.com", NULL, LOGON_NETCREDENTIALS_ONLY, <snip>);

### 程序部署指令

修改完代码后，即可在Visual Studio 2019中进行编译，然后运行下列命令：

    
    
    sc create servicename binpath="C:\ProgramData\Services\Inject\service.exe" start="auto"

### 验证阶段

验证程序是否能够正常工作，我们需要检查和判断会话是否已经存在于目标系统中了。此时我们可以通过下列命令实现：

    
    
    C:\ProgramData\Services\Inject> net sessions
    
    Computer               User name            Client Type       Opens Idle time
    
    -------------------------------------------------------------------------------    
    \\[::1]                svc-admin                                  0 00:00:04
    The command completed successfully.

## 项目地址

 **SMBSessionSpoofer：** 【[ _GitHub传送门_](https://github.com/Sq00ky/SMB-Session-Spoofing)】

## 参考资料

> [ _https://docs.microsoft.com/en-us/windows/win32/services/the-complete-> service-sample_](https://docs.microsoft.com/en-> us/windows/win32/services/the-complete-service-sample)
>
> [ _https://docs.microsoft.com/en-us/windows/win32/services/svc-> cpp_](https://docs.microsoft.com/en-us/windows/win32/services/svc-cpp)
>
> [ _https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-> createprocesswithlogonw_](https://docs.microsoft.com/en-> us/windows/win32/api/winbase/nf-winbase-createprocesswithlogonw)

