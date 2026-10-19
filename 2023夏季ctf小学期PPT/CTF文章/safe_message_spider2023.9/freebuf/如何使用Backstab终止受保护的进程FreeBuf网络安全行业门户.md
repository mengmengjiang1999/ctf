![](https://image.3001.net/images/20210722/1626956090_60f9613ae73442b8b1616.png!small)

## 关于Backstab

Backstab是一款功能强大的安全研究工具，在该工具的帮助下，广大研究人员可以轻松终止那些受反恶意软件产品保护的进程。

当你拿到了目标设备的本地管理员凭证之后，你发现EDR仍然“在线”，该怎么办呢？卸载钩子或者直接系统调用针对EDR也无法起作用，又该怎么办呢？没错，我们为何不直接终止相关进程呢？

Backstab这款工具能够通过利用sysinternals的进程管理驱动器（ProcExp）终止受反恶意软件产品保护的进程，而这个驱动器是由微软签名的。

## 工具运行机制

ProcExp有一个在启动时加载的带签名的内核驱动器，而这个驱动器将允许ProcExp终止那些即使作为管理员也无法终止的句柄。当我们查看到UI时，你可能无法终止受保护的进程，但可以终止它的句柄，因为ProcExp
UI会指示内核驱动程序终止这些句柄。而Backstab能做到同样的事情，只不过没有提供UI。

### Backstab会做哪些事情？

> 将嵌入式驱动器存储至磁盘上；
>
> 创建HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services；
>
> 由于需要加载驱动器，因此获取SE_PRIVILEGE_ENABLED权限；
>
> 使用NtLoadDriver加载驱动器以避免创建服务；
>
> 创建的注册表项被删除（执行期间服务不可见）；
>
> 通过DeviceIoControl与驱动器通信；
>
> 调用NtQuerySystemInformation实现进程句柄枚举；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Yaxser/Backstab

## 工具使用帮助

    
    
    Usage: backstab.exe <-n name || -p PID> [options]  
    
    -n, 通过名称选择进程，需包含.exe后缀
    
    -p, 通过PID选择进程
    
    -l, 列举所有受保护进程的句柄
    
    -k, 选择要终止的受保护进程的句柄
    
    -x, 选择一个指定的句柄
    
    -d, 指定ProcExp提取路径
    
    -s, 指定服务名称注册表键
    
    -u, 卸载ProcExp驱动器
    
    -a, 添加SeDebugPrivilege
    
    -h, 显示该帮助菜单
    
     
    
    Examples:
    
    backstab.exe -n cyserver.exe -k [kill cyserver]
    
    backstab.exe -n cyserver.exe -x E4C [Close handle E4C of cyserver]
    
    backstab.exe -n cyserver.exe -l [list all handles of cyserver]
    
    backstab.exe -p 4326 -k -d c:\\driver.sys [kill protected process with PID 4326, extract ProcExp driver to C:\ drive]

## 项目地址

 **Backstab：** 【[ _GitHub传送门_](https://github.com/Yaxser/Backstab)】

