## 关于BackupOperatorToDA

BackupOperatorToDA是一款功能强大的红队提权工具，该工具能够在不使用域控制器RDP或WinRM的情况下，帮助广大研究人员将Backup
Operators组的成员账号提升为域管理员权限。

如果红队研究人员在渗透测试的过程中，拿到了目标网络系统中Backup
Operators组的成员账号，那么BackupOperatorToDA将能够把这个账号提升为域管理员权限。除此之外，该工具还支持使用其他的参数来将远程共享中的SAM数据库进行转储。

## 工具组件

该工具实现的代码非常简单，操作步骤总共分为三步（三个组件）：

> RegConnectRegistryA : 负责与另一台计算机中预定义的注册表键建立通信连接；
>
> RegOpenKeyExA : 负责打开一个指定的注册表键；
>
> RegSaveKeyA : 将指定的注册表键及其子键对应的值存储到一个新文件中；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/mpgn/BackupOperatorToDA.git

## 工具帮助信息

    
    
    PS C:\Users\mpgn\POC> .\BackupOperatorToDA.exe -h
    
     
    
    Backup Operator to Domain Admin (by @mpgn_x64)
    
     
    
      This tool exist thanks to @filip_dragovic / https://github.com/Wh04m1001
    
     
    
    Mandatory argument:
    
      -t <TARGET>      \\计算机名称（例如: \\dc01.pouldard.wizard）
    
      -o <PATH>        存储SAM/系统/安全文件的路径，可以是UNC路径
    
     
    
    Optional arguments:
    
     
    
      -u <USER>          用户名
    
      -p <PASSWORD>    密码
    
      -d <DOMAIN>       目标域
    
      -h                  显示工具帮助信息

## 工具使用样例

在下面的工具演示样例中，我们进行了如下所示的操作：

> 1、使用另一台服务器的Backup Operators组RON成员，而非DC上的用户成员；
>
> 2、我们转储并导出了远程共享中的SAM数据库；
>
> 3、接下来，我们使用了secretdump来读取SAM文件；
>
> 4、最后，使用了DC的计算机账号来转储NTDS；

![](https://image.3001.net/images/20220511/1652257629_627b735ddfdb0b6ff2950.png!small)

## 工具运行截图

![](https://image.3001.net/images/20220511/1652257644_627b736c0413dd76a2276.png!small)

## 项目地址

 **BackupOperatorToDA：** 【[
_GitHub传送门_](https://github.com/mpgn/BackupOperatorToDA)】

## 参考资料

> [ _https://twitter.com/filip_dragovic_](https://twitter.com/filip_dragovic)
>
> [
> _https://raw.githubusercontent.com/Wh04m1001/Random/main/BackupOperators.cpp_](https://raw.githubusercontent.com/Wh04m1001/Random/main/BackupOperators.cpp)
>
> [ _https://twitter.com/aas_s3curity_](https://twitter.com/aas_s3curity)

