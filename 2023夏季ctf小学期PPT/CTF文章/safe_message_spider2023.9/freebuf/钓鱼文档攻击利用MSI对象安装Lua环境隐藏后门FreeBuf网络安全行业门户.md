## **情报背景**

近期随着俄乌冲突不断升级，Proofpoint公司观察到，
**有组织利用已被感染盗用的乌克兰武装部队成员的邮件账号传播带有宏的XLS文档，以此对欧洲政府发起网络钓鱼攻击。** 该活动中使用宏代码对象Windows
Installer和MSI释放安装基于Lua语言后门的利用方式非常独特。

 **组织**

 **名称**

|

UNC1151  
  
---|---  
  
 **关联组织**

|

Ghostwriter  
  
 **战术标签**

|

网络钓鱼  
  
 **技术标签**

|

VBA MSI lua  
  
 **情报来源**

|

https://www.proofpoint.com/us/blog/threat-insight/asylum-ambuscade-state-actor-uses-compromised-private-ukrainian-military-emails  
  
##  **01** 攻击技术分析

整体攻击流程：

1\. 被盗人员电子邮件账号传播带有宏代码的XLS文档

2\. 文档被打开并启用后向攻击者的恶意地址发起连接

3\. 从连接处下载恶意MSI安装包

4\. MSI安装包首先释放执行Lua脚本所需的依赖文件，创造了一个Lua执行环境，同时释放了一个LNK文件用于持久化

5\. 当下次Windows启动的时候，Lnk将启动Lua的可执行文件去运行包含恶意代码的Lua脚本

6\. 恶意Lua脚本将获取C盘的序列信息，并每两秒一次与攻击者的C2地址通讯，执行攻击者的下达的后续请求

![1649300697_624e54d9371b3e6a36d92.png!small?1649300698180](https://image.3001.net/images/20220407/1649300697_624e54d9371b3e6a36d92.png!small?1649300698180)

###  **1.1 独特的宏代码-WindowsInstaller**

在攻击流程2中，当受害者打开恶意文档启用宏执行，会执行一段简单但独特的宏代码。该宏通过CreateObject创建一个 Windows
Installer（msiexec.exe）对象。该对象调用Windows Installer以远程连接在攻击者控制下的IP下载安装恶意MSI包。

通过将UILevel设置为2，将指定Windows Installer以安全静默模式安装，对用户隐藏的安装请求与安装过程界面。

Windows
Installer对象的InstallProduct方法会将从URL获取的MSI安装文件，缓存到本地，然后调用msiexec.exe安装恶意MSI包。由于攻击者使用MSI包作为后续基于Lua的恶意软件的安装程序，所以通过网络钓鱼传递的宏文档进行安装部署非常合适。

使用宏文档来进行网络钓鱼攻击非常常见，但本次攻击者使用了一个比较少见和独特的对象Windows
Installer来实现恶意后门的部署，这种方式还比较独特和少见。从使用效果来看，该方式非常方便，不需要很多的宏代码和行为就将攻击过程从office转移到msi，只要终端安全软件针对宏代码执行windows
installer没有限制执行，就可以利用这个合法对象切入下一阶段的恶意攻击。较为有效和隐蔽。

![1649300735_624e54ff2c0bff1e54cb8.png!small?1649300736301](https://image.3001.net/images/20220407/1649300735_624e54ff2c0bff1e54cb8.png!small?1649300736301)

###  **1.2 使用MSI部署基于Lua的恶意软件**

在将宏文档钓鱼转换到恶意MSI安装包后，攻击者也没有直接去安装恶意的二进制后门和脚本，而是先安装了一系列Lua依赖的合法文件，在这些合法文件中包含了恶意Lua脚本。通过这种方式，攻击者可以进一步去规避与安全软件在二进制文件查杀的直接对抗，通过选择恶意lua脚本的方式实现后门执行。利用MSI安装包的方式也适合去安装脚本执行环境的一系列依赖文件。之后通过安装用于Windows
启动运行的LNK文件实现持久性。

释放的合法Lua文件：

> luacom.dll （LuaCom 库文件）
>
> ltn12.lua （LuaSocket 脚本）
>
> mime.lua
>
> http.lua
>
> url.lua
>
> tp.lua
>
> socket.lua
>
> tp.lua
>
> core.dll
>
> mime.dll
>
> lua51.dll
>
> sppsvc.exe(经过攻击者修改的Lua解释器，该版本不会对用户输出控制台界面)
>
> <6 characters>.rbs （windows 安装回滚脚本）

释放的恶意Lua文件：

print.lua

释放的恶意LNK位置

    
    
    ~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Software Protection Service.lnk

恶意LNK被设置为启动释放于C:\ProgramData\\.security-soft\目录的sppsvc.exe去运行print.lua,
之后该脚本尝试从攻击者的C2获取额外的恶意Lua代码。

##  **02** 总结

在网络钓鱼攻击中，攻击者通常会选定一些独特的方式去规避与安全软件的直接对抗。在这次攻击活动中我们看到在宏文档中运行windows
installer对象安装恶意的MSI安装包。之后利用MSI包来安装基于脚本语言的后门非常有趣，如果相关安全软件针对这两点没有完好的防护方案，攻击者就能够有机可乘。

