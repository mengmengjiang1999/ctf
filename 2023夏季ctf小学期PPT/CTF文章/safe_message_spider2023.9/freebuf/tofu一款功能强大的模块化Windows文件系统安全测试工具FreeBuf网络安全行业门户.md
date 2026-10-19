![](https://image.3001.net/images/20220809/1660047714_62f251629341625ef8dc5.png!small)

## 关于tofu

tofu是一款功能强大的针对Windows文件系统安全的模块化工具，该工具可以使用离线方法对目标Windows文件系统进行渗透测试，并通过绕过Windows系统登录界面来帮助广大研究人员测试Windows主机的安全性。除此之外，该工具还可以执行哈希转储、OSK后门和用户枚举等安全测试任务。

## 工具运行机制

当Windows计算机关闭时，除非它启用了Bitlocker或其他加密服务，否则它的存储设备中将包含设备上存储的所有内容，就好像它已经被解锁了一样。这也就意味着，我们可以在带有引导功能的U盘上从操作系统引导并访问其文件，甚至只需将文件系统连接到另一台计算机也可以实现类似的功能。

该工具可以帮助广大研究人员确定何时可以从Linux访问Windows文件系统，并执行NTLM密码哈希转储、用户枚举、后门安装和登录绕过等安全任务。

## 工具组件

> [ _PyCryptodome_](https://github.com/Legrandin/pycryptodome)
>
> [ _PypyKatz_](https://github.com/skelsec/pypykatz)

## 功能模块

由于tofu是以模块化架构开发的，因此我们也可以根据自己的需要来扩展其他的功能模块。该工具当前支持的模块如下：

> hashdump.py：从目标Windows文件系统导出NTLM哈希；
>
> osk_backdoor.py：后门程序osk.exe可绕过登录界面；
>
> list_users.py：枚举目标Windows系统用户；
>
> chrome.py：导出Chrome历史记录和所有用户的登录数据；
>
> get_dpapi_masterkeys.py：导出DPAPI主密钥；
>
> enum_unattend.py：枚举文件；
>
> memory_strings.py：搜索内存数据；
>
> startup.py：向用户启动目录注入一个程序；
>
> wifi.py：获取Wi-Fi密码；

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/puckblush/tofu.git

接下来，使用pip3命令并通过项目提供的requirements.txt文件来安装该工具所需的依赖组件：

    
    
    sudo pip3 install -r requirements.txt

最后，直接使用下列命令便可运行tofu：

    
    
    sudo python3 tofu.py

## 工具使用帮助

> 'list'：枚举所有的存储设备，并将驱动器路径加载到内存中；
>
> 'usedrive'：设置需要使用的驱动器，可以通过驱动器号进行设置；
>
> 'modules'：枚举功能模块，并将所有功能模块加载到内存中以便后续使用；
>
> 'use'：选择一个需要使用的功能模块；

## 项目地址

 **tofu** ：【[ _GitHub传送门_](https://github.com/puckblush/tofu)】

## 参考资料

> [
> _https://github.com/Legrandin/pycryptodome_](https://github.com/Legrandin/pycryptodome)
>
> [
> _https://github.com/skelsec/pypykatz﻿_](https://github.com/skelsec/pypykatz)

  

