![](https://image.3001.net/images/20201105/1604505979_5fa2d17b340f829804669.png!small)

## GRAT2

GRAT2是一款功能强大的命令&控制（C2）工具，该工具出于教育目的开发和设计，GRAT2采用Python3编程语言开发，客户端基于.NET 4.0实现。

我们之所以开发GRAT2，是因为我们发现虽然社区目前有很多很多的C2工具，但是我们开发这款工具是为了帮助大家更好地了解命令&控制服务器的运行原理，以及相关的规避技术，这就是我们开发GRAT2的原因。

## 当前功能

### 规避技术：

> 沙箱（检测当前设备是否处于域中，如果不在则退出）；
>
> Windows(ETW)日志；
>
> AMSI；
>
> caretrun：以caret格式(^i^p^c^o^n^f^i^g)，通过cmd.exe和explorer.exe执行命令；

### 通信：

> 使用XOR和Base64编码HTTP通信；
>
> 代理识别

### 模块：

> uac - 尝试使用静默磁盘清理和父级PID欺骗技术绕过UAC；
>
> maketoken - 删除当前令牌并使用给定的凭据（域或本地）创建一个新的令牌；
>
> revtoself - 移除当前令牌；
>
> stealtoken - 尝试从正在运行的进程中窃取令牌并模拟用户（需要管理员权限）；
>
> rportfwd - 尝试创建反向端口转发；
>
> whoami - 显示当前用户；
>
> hostname - 显示计算机主机名；
>
> domain - 显示域FQDN；
>
> screenshot - 获取屏幕截图；
>
> download -下载文件；
>
> upload - 上传文件；
>
> cd - 修改目录；
>
> run - 使用explorer.exe作为父PID并通过cmd.exe来执行命令；
>
> caretrun - 使用explorer.exe作为父PID并通过cmd.exe以caret格式(^i^p^c^o^n^f^i^g) ；执行命令；
>
> sleep - 设置新的睡眠时间；
>
> exit - 退出；
>
> shell - 通过cmd.exe执行命令；
>
> powershell - 使用非托管PowerShell执行PowerShell命令；
>
> powerscript - 使用非托管PowerShell执行PowerShell脚本；
>
> executeassembly - 尝试在内存中执行.NET程序集；
>
> ps - 打印当前进程；
>
> pwd - 打印当前目录；
>
> ls - 目录枚举；
>
> pid - 打印当前进程ID；

### 进程注入技术：

> dynamic_injectcrt - 尝试使用动态调用技术将Shell代码注入进程；
>
> ppid_processhollow - 尝试使用Process Hollowing和父PID欺骗技术将Shell代码注入进程(资源管理器)；
>
> processhollow - 尝试使用Process Hollowing和父PID欺骗技术将Shell代码注入进程；
>
> injectppidapc - 尝试使用QueueUserAPC和父PID欺骗技术将Shell代码注入进程(资源管理器)；
>
> injectapc - 尝试使用QueueUserAPC技术将Shell代码注入进程；
>
> injectcrt - 尝试使用远程线程创建技术将Shell代码注入进程；

## 配置文件

![](https://image.3001.net/images/20201105/1604506002_5fa2d1923524c6fc86be5.png!small)

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/r3nhat/GRAT2.git

## 工具使用

首先，使用Visual
Studio打开GRAT2客户端项目（GRAT2_Client.sln），将Solution配置由Debug修改为Release，然后构建Solution。

接下来，使用下列方法开启GRAT2服务器：

![](https://image.3001.net/images/20201105/1604506044_5fa2d1bcb03cc408ddf48.png!small)

使用下列命令开启GRAT2客户端可执行程序：

    
    
    GRAT2_Client\bin\Release\GRAT2_Client.exe

现在，我们就可以使用下列方法跟代理进行交互了：

![](https://image.3001.net/images/20201105/1604506298_5fa2d2baf36b98fbe8b78.png!small)

## 项目地址

> GRAT2：【[ _GitHub传送门_](https://github.com/r3nhat/GRAT2)】

