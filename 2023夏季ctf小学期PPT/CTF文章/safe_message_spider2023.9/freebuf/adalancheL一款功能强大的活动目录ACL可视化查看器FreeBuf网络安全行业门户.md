![](https://image.3001.net/images/20210922/1632323608_614b481865caed22173e2.png!small)

## 关于adalancheL

adalancheL是一款功能强大的活动目录ACL可视化查看器，可以直接提供实时结果，并显示用户和组在一个活动目录中的权限。该工具可以通过可视化的形式，更好地帮助广大研究人员查看谁可以接管账号、设备或整个域，并识别和显示错误配置信息。

众所周知，活动目录的安全问题一直都是一件麻烦事。小型组织通常不知道他们在做什么，而且太多的人只是被添加到域管理员中。在大型组织中，你有大量不同需求的人，而且还会被授予不同的权限。如果某个人在某个时间点犯了错误，就可能会让你付出高昂的代价。

## 工具安装

### 手动构建

首先，我们需要安装好Go 1.17环境。然后使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/lkarlslund/adalanche.git
    

接下来，切换至项目根目录，然后运行构建语句，针对我们的操作系统进行代码构建：

    
    
    go build
    

此时，我们将拿到针对Windows、Linux或macOS的代码。

### Releases安装

或者，我们也可以直接访问该项目的【[
_Releases页面_](https://github.com/lkarlslund/adalanche/releases)】，下载对应操作系统版本的最新程序。

## 工具使用

该工具将会尽可能地尝试进行自动化检测，因此我们可以直接让其在一台加入了Windows域的设备上运行，且无需任何参数：

    
    
    adalanche.exe
    

如果没有提供任何命令，该工具将会以导出分析模式运行，即导出并分析。

如果你在一台没有加入域的Windows设备或其他操作系统上运行，你至少需要使用“-domain”参数。

LDAPS（TLS，端口636）为默认配置，如果你使用的是实验室环境，并且没有配置证书，此时将出现连接错误，因为计算机不信任AD证书。我们可以使用“-ignorecert”选项禁用证书验证，或者使用“adalanche
-authmode NoTLS -port 389”将协议修改为LDAP。

下列命令可以针对contoso.local创建缓存文件：

    
    
    adalanche -domain contoso.local -username joe -password Hunter42 dump
    

下列命令可以分析contoso.lcal的缓存文件，并启动浏览器：

    
    
    adalanche -domain contoso.local analyze
    

## 用户接口截图

###
分析目标域![](https://image.3001.net/images/20210922/1632323676_614b485c8cee63dcbc076.png!small)

###
分析方法![](https://image.3001.net/images/20210922/1632323685_614b486589310f58d4f57.png!small)

###
LDAP查询弹窗![](https://image.3001.net/images/20210922/1632323696_614b48708d5da390e6bd4.png!small)

###
分析结果显示![](https://image.3001.net/images/20210922/1632323708_614b487c6a6b86530c266.png!small)

###
选取目标![](https://image.3001.net/images/20210922/1632323721_614b4889304f82d332a02.png!small)

###
路由至目标![](https://image.3001.net/images/20210922/1632323727_614b488f0fe6679900e1a.png!small)

###
选取到目标的路径![](https://image.3001.net/images/20210922/1632323735_614b4897630eaff472895.png!small)

## 项目地址

 **adalancheL：** 【[ _GitHub传送门_](https://github.com/lkarlslund/adalanche)】

## 参考资料

> [
> _https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Active%20Directory%20Attack.md_](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Active%20Directory%20Attack.md)
>
> [
> _https://ldapwiki.com/wiki/LDAP_MATCHING_RULE_BIT_AND_](https://ldapwiki.com/wiki/LDAP_MATCHING_RULE_BIT_AND)
>
> [
> _https://ldapwiki.com/wiki/LDAP_MATCHING_RULE_BIT_OR_](https://ldapwiki.com/wiki/LDAP_MATCHING_RULE_BIT_OR)
>
> [
> _https://ldapwiki.com/wiki/LDAP_MATCHING_RULE_IN_CHAIN﻿_](https://ldapwiki.com/wiki/LDAP_MATCHING_RULE_IN_CHAIN)

