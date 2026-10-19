![Windows-Auditing-tool.jpg](https://image.3001.net/images/20180916/1537055527_5b9d9b2718309.jpg!small)

**[WINSpect](https://github.com/A-mIn3/WINspect)是一款基于Powershell的Windows安全审计工具，可用于枚举和识别Windows平台的安全漏洞，以进一步的优化和加固平台的安全防护策略。**

## 安装

使用管理员权限打开Powershell并运行WINSpect脚本。

## 特性

> WINSpect将为我们提供审计检查和枚举：
>
> 已安装的安全产品
>
> 本地文件系统共享
>
> 具有本地组成员身份的域用户和组
>
> 注册表autoruns
>
> 可由Authenticated Users组成员配置的本地服务
>
> Authenticated Users组成员可以写入相应二进制文件的本地服务
>
> 非system32 Windows托管服务及其相关的DLL
>
> 非引用服务路径漏洞
>
> 非系统计划任务DLL劫持
>
> 用户帐户控制设置
>
> 自动安装

##  **防火墙 & 杀毒软件**

![Screenshot-504-1.png](https://image.3001.net/images/20180916/1537055556_5b9d9b44e2567.png!small)

上图显示，脚本为我们识别出了防火墙和杀毒软件，并启用/禁用其功能。

##  **本地共享 & UAC**

![Screenshot-505.png](https://image.3001.net/images/20180916/1537055587_5b9d9b6347b06.png!small)

上图显示，脚本为我们枚举出了每个人的本地共享，并且“用户帐户控制”已启用。

## 可配置和非引用路径服务

![Screenshot-506.png](https://image.3001.net/images/20180916/1537055617_5b9d9b81d7010.png!small)

上图显示，脚本为我们枚举出了在后台运行的可配置和非引用路径服务。

##  **注册表** **autorun**

![Screenshot-508-1.png](https://image.3001.net/images/20180916/1537055637_5b9d9b9512793.png!small)

上图显示，脚本为我们枚举出了开机自动运行的软件服务。

##  **DLL劫持** **& **托管服务

![Screenshot-509.png](https://image.3001.net/images/20180916/1537055657_5b9d9ba97ab3b.png!small)

上图显示，脚本为我们检查了DLL是否可被劫持以及托管服务的状态。

## 计划任务

![Screenshot-510.png](https://image.3001.net/images/20180916/1537055673_5b9d9bb90637e.png!small)

上图显示，脚本为我们枚举并检查了当前计划任务。

想要了解更多有关注册表的内容，请参阅我们之前发布的“Windows注册表分析”一文。

 ***参考来源：[gbhackers](https://gbhackers.com/winspect-windows-auditing-tool/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

