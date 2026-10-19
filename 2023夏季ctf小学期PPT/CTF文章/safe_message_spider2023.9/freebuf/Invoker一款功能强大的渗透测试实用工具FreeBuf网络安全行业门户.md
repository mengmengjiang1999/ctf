![](https://image.3001.net/images/20200508/1588932404_5eb52f340189d.png!small)

**Invoker是一款功能强大的渗透测试实用工具，在该工具的帮助下，广大研究人员可以通过GUI接口访问某些Windows操作系统功能，其中部分功能可能会要求管理员权限。**

## 功能介绍

> 1、调用命令行工具和PowerShell；
>
> 2、下载一个文件；
>
> 3、添加一个注册表键；
>
> 4、设置计划任务；
>
> 5、连接至一个远程主机；
>
> 6、终止运行进程；
>
> 7、运行一个新的进程；
>
> 8、向已运行进程中注入字节码；
>
> 9、向已运行进程注入DLL；
>
> 10、启用访问令牌权限；
>
> 11、从已运行进程中拷贝访问令牌；
>
> 12、枚举未引用的服务路径并重启一个已运行的服务；

该工具使用Dev-C++ IDE v5.11 (64位)构建，并使用TDM-GCC v4.9.2 (64位)编译，已在Windows 10
64位企业版平台上进行过测试。

> Dev-C++下载：【[下载地址](https://www.freebuf.com/wp-> admin/post.php?post=236088&action=edit)】

## PowerShell脚本

本项目的PowerShell脚本大部分采用C++程序开发，如需获取请点击【[ _这里_](https://github.com/ivan-sincek/invoker/tree/master/ps)】。

## 工具运行

[ _'\exec\Invoker.exe'_](https://github.com/ivan-sincek/invoker/tree/master/exec)

## 字节码注入

该工具还支持通过向更高权限的进程注入字节码来实现提权。

该工具可以解析一个HTTP响应，并从自定义元素中提取出Payload，比如说下列内容：

    
    
    <img class="bc" src="data:image/gif;base64,payload" alt="bc" hidden="hidden">

其中的Payload是一个使用了Base64编码的源码/文件。

如果反病毒产品不断地删除你的本地Payload的话，这个功能就比较有用了。

你还可以指定使用你的自定义元素，但你可能需要修改源代码并进行重新编译。

> 参考样例如下：【[ _点我查看_](https://pastebin.com/raw/Nd1tCBv6)】

### 生成一个反向Shell Payload

> 如需生成一个反向Shell Payload，请使用本人的另一个项目：【[ _传送门_](https://www.freebuf.com/wp-> admin/post.php?post=236088&action=edit#generate-a-reverse-shell-payload)】。

获取LocalSystem账号（NT AUTHORITY\SYSTEM）

以管理员权限运行Invoker.exe。

启用所有的访问令牌权限。

从类似Windows Logon应用程序（winlogon.exe）之类的地方拷贝访问令牌，并以新实例运行Invoker.exe。

在新的Invoker.exe实例中，打开命令行窗口，然后运行命令whoami，接下来你将会看到nt authority\system。

再次启用所有的访问令牌权限。

关闭旧的Invoker.exe实例。

除此之外，你还可以从本地安全授权子系统服务（lsass.exe）中获取更多的访问令牌权限。

## 工具运行截图

![](https://image.3001.net/images/20200508/1588932532_5eb52fb48363a.jpg!small)

![](https://image.3001.net/images/20200508/1588932537_5eb52fb9d7bc2.jpg!small)

![](https://image.3001.net/images/20200508/1588932544_5eb52fc0176cf.jpg!small)

![](https://image.3001.net/images/20200508/1588932551_5eb52fc73ab9f.jpg!small)

## 项目地址

> Invoker：【[ _GitHub传送门_](https://github.com/ivan-sincek/invoker)】

 *** 参考来源：[ _ivan-sincek_](https://github.com/ivan-sincek/invoker)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

