![](https://image.3001.net/images/20220911/1662861469_631d409d6fe189c083525.png!small)

## 关于ForceAdmin

ForceAdmin是一款针对Windows操作系统安全的强大工具，该工具可以不断地创建UAC弹窗，直到目标用户提供管理员运行权限为止。在该工具的帮助下，广大研究人员不仅可以对组织内员工进行安全意识培训，而且也可以测试网络中Windows主机的安全性。

ForceAdmin本质上是一个C#
Payload构建/生成工具，输入的命令可以通过PowerShell直接调用cmd.exe运行，并且支持使用批处理语法。在某些情况下，有些用户会将UAC设置为始终显示，因此我们就无法使用UAC绕过技术了。但是有了ForceAdmin的帮助，我们就可以通过不断弹出UAC弹窗来迫使目标用户以管理员权限运行程序，并绕过这些设置。

## 工具要求

如需自行构建项目代码，则需要安装下列NuGet包：

> [ _Fody_](https://www.nuget.org/packages/Fody/)：用于构建.NET程序集所需要的扩展工具；
>
> [ _Costrua_
> _.Fody_](https://www.nuget.org/packages/Costura.Fody/)：Fody的附加程序，用于嵌入各种资源；
>
> [ _Microsoft_
> _.AspNet.WebApi.Client_](https://www.nuget.org/packages/Microsoft.AspNet.WebApi.Client/)：这个包可以为System.Net.Http添加数据格式化和内容转换支持，其中包括针对JSON、XML和表单URL编码数据的支持；

## 工具安装

广大研究人员可以直接访问该项目的【[
_Releases页面_](https://github.com/catzsec/ForceAdmin/releases)】下载构建好的ForceAdmin.exe程序。

我们还可以直接以Tarball形式【[
_点我下载_](https://github.com/CatzSec/ForceAdmin/tarball/master)】或以Zipball形式【[
_点我下载_](https://github.com/catzsec/ForceAdmin/zipball/master)】下载最新版本的ForceAdmin。

除此之外，我们还可以直接使用下列命令将该项目源码克隆至本地：

    
    
    $ git clone https://github.com/catzsec/ForceAdmin.git

然后在控制台中切换到项目目录：

    
    
    $ cd ForceAdmin

下列命令可以直接运行ForceAdmin：

    
    
    $ dotnet run

我们还可以自行编译ForceAdmin的项目代码以实现功能的扩展：

    
    
    $ dotnet publish -r win-x64 -c Release -o ./publish/

## 工具运行截图

![](https://image.3001.net/images/20220911/1662861501_631d40bd63fb1672ce776.png!small)

## 工具使用演示

![](https://image.3001.net/images/20220911/1662861508_631d40c4ab246f86d6414.gif)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/catzsec/ForceAdmin/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **ForceAdmin** ：【[ _GitHub传送门_](https://github.com/catzsec/ForceAdmin)】

## 参考资料

> [
> _https://www.nuget.org/packages/Fody/_](https://www.nuget.org/packages/Fody/)
>
> [
> _https://www.nuget.org/packages/Costura.Fody/_](https://www.nuget.org/packages/Costura.Fody/)
>
> [
> _https://www.nuget.org/packages/Microsoft.AspNet.WebApi.Client/_](https://www.nuget.org/packages/Microsoft.AspNet.WebApi.Client/)

