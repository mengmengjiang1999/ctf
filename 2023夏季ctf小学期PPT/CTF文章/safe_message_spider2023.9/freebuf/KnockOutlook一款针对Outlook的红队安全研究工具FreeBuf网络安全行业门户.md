![](https://image.3001.net/images/20210917/1631846069_6143feb52d4351970ee0a.jpg!small)

## 关于KnockOutlook

KnockOutlook是一款基于C#开发的工具， **该工具可以跟Outlook的COM对象进行交互，并且能够帮助红队安全研究人员执行各种安全操作。**

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/eksperience/KnockOutlook.git

## 命令行使用

    
    
    __ __                  __   ____        __  __            __
    
         / //_/____  ____  _____/ /__/ __ \__  __/ /_/ /___  ____  / /__
    
        / ,<  / __ \/ __ \/ ___/ //_/ / / / / / / __/ / __ \/ __ \/ //_/
    
       / /| |/ / / / /_/ / /__/ ,< / /_/ / /_/ / /_/ / /_/ / /_/ / ,<
    
      /_/ |_/_/ /_/\____/\___/_/\_\\____/\__,_/\__/_/\____/\____/_/\_\
    
     
    
     
    
    Parameters:
    
        --operation  :  指定需要执行的操作
    
        --keyword   :  指定搜索操作的关键词
    
        --id        :  指定保存操作的目标
    
        --bypass    :  绕过编程访问安全设置（需要管理员权限）
    
     
    
    Operations:
    
        check       :  执行各种检测以确保操作安全
    
        contacts     :  提取每一个账号的所有联系人
    
        mails       :   提取每一个账号的邮箱元数据
    
    search      :  根据关键词搜索每一个邮箱
    
    save        :  保存指定EntryID的邮件
    
     
    
    Examples:
    
        KnockOutlook.exe --operation check
    
        KnockOutlook.exe --operation contacts
    
        KnockOutlook.exe --operation mails --bypass
    
        KnockOutlook.exe --operation search --keyword password
    
        KnockOutlook.exe --operation save --id {EntryID} --bypass

## 功能操作

### 安全检测（check）

枚举Outlook安装详细信息，以便构造正确的注册表项并检索编程访问安全设置。

如果此值设置为“Warn when antivirus is inactive or out-of-date”，它将会查询WMI以查找任何已安装的防病毒产品并分析其当前状态。

### 联系人信息枚举（contacts）

枚举每个已配置帐户的联系人并提取以下信息：

完整名称（全名）

电子邮件地址

### 电子邮件枚举（mails）

枚举每个已配置帐户的邮件并提取以下元数据：

ID

时间戳

主题

邮件发送者

邮件接收者

附件

### 搜索查询（search）

使用Outlook的内置搜索引擎在每个已配置帐户的邮箱中搜索，并返回邮件正文中包含所提供关键字的EntryID。

### 数据保存（save）

使用Outlook内置的另存为机制导出由其EntryID引用的邮件。

## 对象模型保护绕过

由于当前进程是以高级完整权限运行的，因此该工具所提供的“--bypass”选项可以与联系人信息枚举（contacts）、电子邮件枚举（mails）、搜索查询（search）以及数据保存（save）这几个功能结合使用。

KnockOutlook将尝试获取当前Outlook安全策略的快照，并以自动允许编程访问安全提示的方式对其进行篡改操作，在操作完成后还会将其恢复为初始状态。

## 数据输出

KnockOutlook的所有操作都会将基础数据直接输出在屏幕上。

联系人信息枚举（contacts）和电子邮件枚举（mails）操作将会把输出数据以JSON格式保存至gzip压缩文件中。

数据保存（save）操作将会把输出数据以.msg格式导出。

所有的文件名都会在运行时随机生成。

默认配置下，Outlook的安全临时目录会用来存储所有的导出文件。

## 项目地址

 **KnockOutlook：** 【[
_GitHub传送门_](https://github.com/eksperience/KnockOutlook)】

