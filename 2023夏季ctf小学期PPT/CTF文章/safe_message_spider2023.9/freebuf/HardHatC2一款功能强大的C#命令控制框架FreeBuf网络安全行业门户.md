![](https://image.3001.net/images/20230803/1691075633_64cbc4312c7d4d528b4b7.png!small)

## 关于HardHatC2

HardHatC2是一款功能强大的C#命令控制框架，该工具基于C# .NET开发，支持多用户同时使用，旨在协助红队安全研究人员执行安全分析和渗透测试任务。

HardHatC2主要包含三个重要组件，即一个ASP.NET团队服务器、一个.NET客户端和一个基于C#的植入程序，这三个组件能够完成C2操作中的所有功能。

## 工具架构

![](https://image.3001.net/images/20230803/1691075646_64cbc43e0dd9c7fe657ad.png!small)

## 工具要求

> [ _.NET 7 SDK_](https://dotnet.microsoft.com/en-> us/download/dotnet/7.0)（安装完成后，就可以使用dotnet run命令运行团队服务器和客户端了）；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地，然后手动完成项目构建：

    
    
    git clone https://github.com/DragoQCC/HardHatC2.git

除此之外，我们也可以直接访问该项目的【[
_Releases页面_](https://github.com/DragoQCC/HardHatC2/releases)】直接下载该工具的预编译版本。

## 工具使用

### 团队服务器

首先，我们需要配置团队服务器的起始地址。编辑HardHatC2\TeamServer\Properties\LaunchSettings.json文件，然后将"applicationUrl":
"https://127.0.0.1:5000"修改为指定的地址和端口。

接下来，在命令行终端中切换到../HrdHatC2/Teamserver/目录下，并运行dotnet run命令来启动团队服务器即可：

![](https://image.3001.net/images/20230803/1691075667_64cbc45381fa48c4f9009.png!small)

### 客户端

首先，在启动客户端时就要指定团队服务器的地址，样例命令如下：

    
    
    dotnet run https://127.0.0.1:5000

接下来，打开Web浏览器并访问https://localhost:7096/，此时你将会看到一个登录页面。使用HardHat_Admin登录，然后切换到设置页面并创建一个新的用户，现在我们就可以使用这个新的账号来访问完整的客户端功能了：

![](https://image.3001.net/images/20230803/1691075678_64cbc45ee7a5c9cb3815b.png!small)

## 工具运行截图

 **管理员仪表盘：**

![](https://image.3001.net/images/20230803/1691075689_64cbc469896d7e0fa3d0d.png!small)

 **连接成功：**

![](https://image.3001.net/images/20230803/1691075695_64cbc46f5e7956b680212.png!small)

 **C2配置信息：**

![](https://image.3001.net/images/20230803/1691075701_64cbc4754be8a4006adab.png!small)

 **HTTP植入物和绑定的TCP植入物图片概述：**

![](https://image.3001.net/images/20230803/1691075707_64cbc47b0f14bebf16489.png!small)

 **帮助命令表格样例：**

![](https://image.3001.net/images/20230803/1691075712_64cbc480845f2fdbe27d8.png!small)

 **IoC跟踪：**

![](https://image.3001.net/images/20230803/1691075718_64cbc486923a4f3ac6015.png!small)

## 许可证协议

本项目的开发与发布遵循[ _BSD_
_-3-Clause_](https://github.com/DragoQCC/HardHatC2/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **HardHatC2** ：【[ _GitHub传送门_](https://github.com/DragoQCC/HardHatC2)】

## 参考资料

> [ _https://dotnet.microsoft.com/en-> us/download/dotnet/7.0_](https://dotnet.microsoft.com/en-> us/download/dotnet/7.0)
>
> [
> _https://docs.hardhat-c2.net/documentation/_](https://docs.hardhat-c2.net/documentation/)

