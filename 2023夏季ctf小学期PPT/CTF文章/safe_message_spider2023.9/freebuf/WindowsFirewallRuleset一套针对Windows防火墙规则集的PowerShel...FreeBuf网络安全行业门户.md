![](https://image.3001.net/images/20200109/1578577293_5e172d8d231f1.jpg!small)

##  WindowsFirewallRuleset

 **该工具根据下列因素，已将Windows防火墙规则组织成为了单独的PowerShell脚本：**

> 1、规则组
>
> 2、流量方向
>
> 3、IP版本（IPv4/IPv6）
>
> 4、根据程序和服务进行进一步分类

###  例如：

> 1、ICMP流量
>
> 2、浏览器规则
>
> 3、Windows系统规则
>
> 4、存储的应用程序
>
> 5、Windows服务
>
> 6、微软程序
>
> 7、第三方程序
>
> 8、广播流量
>
> 9、等等...

你可以根据需要来选择使用的规则，使用命令即可完成防火墙配置。

所有的规则都可以直接加载进组策略中，这种方式比默认的Windows防火墙配置规则更加强大。

##  系统要求

> 1、Windows 10专业版或企业版
>
> 2、Windows PowerShell 5.1：【[点我下载](https://github.com/PowerShell/PowerShell)】
>
> 3、Git（可选项）：【[点我下载](https://git-scm.com/downloads)】

##  工具下载和使用

首先，右键点击任务栏，然后选择“任务栏设置”，勾选“当我右键点击’开始’按钮或按下Windows键+X时，在菜单中将命令提示符替换为Windows
PowerShell”。

右键点击“开始”按钮，点击“Windows PowerShell（管理员）”，以管理员权限打开PowerShell，输入下列命令：

    
    
    Get-ExecutionPolicy

然后输入：

    
    
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted -Force
    
        cd C:\
    
        git clone git@github.com:metablaster/WindowsFirewallRuleset.git
    
        cd WindowsFirewallRuleset
    
        .\SetupFirewall.ps1

执行完成后，我们再输入下列命令来执行脚本即可完成规则设置：

    
    
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force\

##  应用单独规则集

如果你只想应用特定的规则，你有下列两种方法：

> 1、执行SetupFirewall.ps1脚本，然后输出需要使用的规则集，或者输入“n”并按回车键跳过当前规则集。
>
> 2、在PowerShell终端窗口中，进入包含规则集脚本的目录，然后执行特定PowerShell脚本。
>
> 3、运行FirewallProfile.ps1脚本来应用默认防火墙规则，或者直接在GPO中手动配置。

##  删除规则

根据该版本，我们可以直接在本地组策略中选择我们需要删除的规则，然后右键点击并删除即可。如果需要还原防火墙的状态，我们还需要从GPO中删除所有规则，然后右键点击“Windows
Defender Firewall with Advanced Security - Local Group Policy
Object”结点，并将所有的属性设置为“Not configured”。

##  管理已加载的规则

我们有下列两种方法管理已加载的规则：

> 1、使用本地组策略，这种方法会对规则的使用有一定的限制；
>
> 2、编辑PowerShell脚本，这种方法允许我们拥有最完整的控制权，我们可以提升规则，新增规则或修改规则；

###  许可证协议

>
> WindowsFirewallRuleset这个项目的开发与发布遵循[MIT开源许可证协议](https://raw.githubusercontent.com/metablaster/WindowsFirewallRuleset/master/LICENSE)。
>
> 子项目Indented.Net.IP（第三方代码，位于
> "Indented.Net.IP"子目录）遵循[ISC协议](https://raw.githubusercontent.com/metablaster/WindowsFirewallRuleset/master/Indented.Net.IP/LICENSE)。
>
> 子项目VSSetup（第三方代码，位于
> "VSSetup"子目录）遵循[MIT协议](https://raw.githubusercontent.com/metablaster/WindowsFirewallRuleset/master/VSSetup/LICENSE.txt)。

##  项目地址

>
> WindowsFirewallRuleset：【[GitHub传送门](https://github.com/metablaster/WindowsFirewallRuleset)】

 ***
参考来源：[metablaster](https://github.com/metablaster/WindowsFirewallRuleset)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

