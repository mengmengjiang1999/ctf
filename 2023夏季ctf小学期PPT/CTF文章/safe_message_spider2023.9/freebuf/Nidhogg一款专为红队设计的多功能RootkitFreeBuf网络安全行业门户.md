![](https://image.3001.net/images/20230607/1686109898_647ffeca038ebfe2caa25.jpg!small)  

## 关于Nidhogg

Nidhogg是一款专为红队设计的多功能Rootkit，该工具的主要目的是为红队研究人员提供一个多合一的切易于使用的多功能Rootkit，并允许研究人员通过单个头文件来将其引入到自己的C2框架之中。

当前版本的Nidhogg支持任意版本的x64 Windows 10和Windows 11。

该项目代码库包含了一个内核驱动程序，并提供了一个C++ Header来与之进行交互。

## 工具功能

> 1、进程隐藏和显示；
>
> 2、进程提升；
>
> 3、进程保护（防关闭和转储）；
>
> 4、绕过pe-sieve；
>
> 5、线程隐藏；
>
> 6、线程保护（防关闭）；
>
> 7、文件保护（防删除和覆盖）；
>
> 8、文件隐藏；
>
> 9、注册表键值保护（防删除和覆盖）；
>
> 10、注册表键值隐藏；
>
> 11、查询当前受保护的进程、线程、文件、注册表键和值；
>
> 12、任意内核R/W；
>
> 13、函数修补；
>
> 14、内置AMSI绕过；
>
> 15、内置ETW修补；
>
> 16、进程签名（PP/PPL）修改；
>
> 17、Shellcode注入：APC、NtCreateThreadEx；
>
> 18、DLL注入：APC、NtCreateThreadEx；
>
> 19、查询内核回调：ObCallbacks、进程和线程创建程序、镜像加载程序、注册表回调；
>
> 20、移除和恢复内核回调；

## 工具下载

广大研究人员可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Idov31/Nidhogg.git

## 工具配置

### 构建客户端

如需编译客户端代码，我们还需要在本地设备上按准过并配置好[
_CMake_](https://community.chocolatey.org/packages/cmake.install/3.13.1)和[
_Visual_ __ _Studio_ _2022_](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=Community&rel=16)，然后运行下列命令即可：

    
    
    cd <NIDHOGG PROJECT DIRECTORY>\Example
    
    mkdir build
    
    cd build
    
    cmake ..
    
    cmake --build .

### 构建驱动程序

如需编译项目代码，我们还需要使用到下列工具：

> [ _Visual_ __ _Studio_ _2022_](https://visualstudio.microsoft.com/thank-you-> downloading-visual-studio/?sku=Community&rel=16)
>
> [ _Windows_ __ _Driver_ __ _Kit_](https://docs.microsoft.com/en-us/windows-> hardware/drivers/download-the-wdk)

克隆项目代码之后，构建驱动程序代码即可。

### 驱动程序测试

如需在你自己的环境中测试驱动程序，可以直接在提权cmd中运行下列命令：

    
    
    bcdedit /set testsigning on

重启之后，创建一个服务并运行驱动程序即可：

    
    
    sc create nidhogg type= kernel binPath= C:\Path\To\Driver\Nidhogg.sys
    
    sc start nidhogg

## 工具使用

该工具的使用非常简单，我们只需要引入头文件即可开始使用Nidhogg：

    
    
    #include "Nidhogg.hpp"
    
     
    
    int main() {
    
        HANDLE hNidhogg = CreateFile(DRIVER_NAME, GENERIC_WRITE | GENERIC_READ, 0, nullptr, OPEN_EXISTING, 0, nullptr);
    
        // ...
    
        DWORD result = Nidhogg::ProcessUtils::NidhoggProcessProtect(pids);
    
        // ...
    
    }

## 许可证协议

本项目的开发与发布遵循[ _BSD_ _-2-_
_Clause_](https://github.com/Idov31/Nidhogg/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Nidhogg** ：【[ _GitHub传送门_](https://github.com/Idov31/Nidhogg)】

## 参考资料

> [
> _https://github.com/TheCruZ/kdmapper_](https://github.com/TheCruZ/kdmapper)
>
> [
> _https://en.wikipedia.org/wiki/Kernel_Patch_Protection_](https://en.wikipedia.org/wiki/Kernel_Patch_Protection)
>
> [
> _https://github.com/zodiacon/windowskernelprogrammingbook_](https://github.com/zodiacon/windowskernelprogrammingbook)
>
> [ _https://www.vergiliusproject.com/_](https://www.vergiliusproject.com/)
>
> [ _https://github.com/JKornev/hidden_](https://github.com/JKornev/hidden)
>
> [
> _https://github.com/itm4n/PPLcontrol_](https://github.com/itm4n/PPLcontrol)
>
> [
> _https://github.com/DarthTon/Blackbone_](https://github.com/DarthTon/Blackbone)
>
> [ _https://learn.microsoft.com/en-> us/sysinternals/downloads/debugview_](https://learn.microsoft.com/en-> us/sysinternals/downloads/debugview)

