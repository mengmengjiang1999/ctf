![](https://image.3001.net/images/20230802/1690961533_64ca067db967403aae85a.jpg!small)  

## 关于LSMS

LSMS是一款功能强大的Linux安全管理与行为监控工具，该工具是由多种安全和监控脚本组成的，广大研究人员可以使用这些脚本来监控Linux系统中与安全相关的事件或对安全活动进行分析和调查。

LSMS中的每个脚本都有自己的作用，并且独立于其他脚本。脚本可以设置为直接打印出结果，通过邮件发送，或者使用[
_AlertR_](https://github.com/sqall01/alertR)作为通知方式。

## 项目目录结构

脚本位于目录scripts/中，每个脚本在文件头中都包含一个简短的摘要，其中描述了它应该做什么，（如果需要）必须安装的依赖项，以及（如果可用）对该脚本思想来源的引用。

每个脚本在scripts/config/目录中都有一个配置文件来配置它们，如果在脚本执行过程中找不到配置文件，脚本将返回到默认设置并打印出结果。因此，没有必要提供配置文件。

scripts/lib/目录包含不同脚本之间共享的代码。

使用monitor_前缀的脚本可以用于监视目的，在安全调查中单独使用它们只会显示Linux系统的当前状态，而不会显示可能与系统安全相关的更改。

## 脚本列表

 ** **名称****

|

 ** **脚本****  
  
---|---  
  
监控cron 文件

|

[monitor_cron.py](https://github.com/sqall01/LSMS/blob/main/scripts/monitor_cron.py)  
  
监控/etc/hosts 文件

|

[monitor_hosts_文件.py](https://github.com/sqall01/LSMS/blob/main/scripts/monitor_hosts_file.py)  
  
监控/etc/ld.so.preload 文件

|

[monitor_ld_preload.py](https://github.com/sqall01/LSMS/blob/main/scripts/monitor_ld_preload.py)  
  
监控/etc/passwd 文件

|

[monitor_passwd.py](https://github.com/sqall01/LSMS/blob/main/scripts/monitor_passwd.py)  
  
监控模块

|

[monitor_modules.py](https://github.com/sqall01/LSMS/blob/main/scripts/monitor_modules.py)  
  
监控SSH authorized_keys 文件

|

[monitor_ssh_authorized_keys.py](https://github.com/sqall01/LSMS/blob/main/scripts/monitor_ssh_authorized_keys.py)  
  
监控systemd unit 文件

|

[monitor_systemd_units.py](https://github.com/sqall01/LSMS/blob/main/scripts/monitor_systemd_units.py)  
  
在/dev/shm中搜索可执行文件

|

[search_dev_shm.py](https://github.com/sqall01/LSMS/blob/main/scripts/search_dev_shm.py)  
  
搜索程序(memfd_create)

|

[search_memfd_create.py](https://github.com/sqall01/LSMS/blob/main/scripts/search_memfd_create.py)  
  
搜索隐藏ELF文件

|

[search_hidden_exe.py](https://github.com/sqall01/LSMS/blob/main/scripts/search_hidden_exe.py)  
  
搜索不可改变的文件

|

[search_immutable_文件s.py](https://github.com/sqall01/LSMS/blob/main/scripts/search_immutable_files.py)  
  
搜索内核线程伪造

|

[search_non_kthreads.py](https://github.com/sqall01/LSMS/blob/main/scripts/search_non_kthreads.py)  
  
搜索由断开SSH会话创建的进程

|

[search_ssh_leftover_processes.py](https://github.com/sqall01/LSMS/blob/main/scripts/search_ssh_leftover_processes.py)  
  
搜索删除的程序

|

[search_deleted_exe.py](https://github.com/sqall01/LSMS/blob/main/scripts/search_deleted_exe.py)  
  
通知测试脚本

|

[test_alert.py](https://github.com/sqall01/LSMS/blob/main/scripts/test_alert.py)  
  
验证.deb包的完整性

|

[verify_deb_packages.py](https://github.com/sqall01/LSMS/blob/main/scripts/verify_deb_packages.py)  
  
## 工具下载

由于该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python
3环境。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/sqall01/LSMS.git

## 工具使用

每一个脚本的代码开头部分都包含有一个简短的描述，这个脚本应该做什么以及相关的依赖组件，如果 有需要的话，请在执行脚本之前完成依赖组件的安装和配置。

共享配置文件scripts/config/config.py包含所有脚本都使用的设置。此外，每个脚本都可以使用scripts/config/目录中相应的配置文件进行配置。如果未找到配置文件，则使用默认设置并打印出结果。

最后，我们可以通过执行start_search.py（位于主目录中）或手动执行每个脚本来运行所有配置的脚本。

## 安全监控

如果你想使用脚本来持续监控你的Linux系统，则必须执行以下步骤：

> 1、设置脚本支持的通知方式（当前打印、邮件或AlertR）；
>
> 2、使用scripts/config/目录中的配置文件配置要运行的脚本；
>
> 3、使用--init参数执行start_search.py，以初始化带有monitor_前缀的脚本，并让它们建立系统的状态；
>
> 4、将cron作业设置为执行start_search.py的root用户（每小时启动一次搜索： 0 * * * * root
> /opt/LSMS/start_search.py）；

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/sqall01/LSMS/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **LSMS** ：【[ _GitHub传送门_](https://github.com/sqall01/LSMS)】

## 参考资料

> [ _https://github.com/sqall01/alertR_](https://github.com/sqall01/alertR)

