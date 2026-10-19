![](https://image.3001.net/images/20200813/1597308728.png!small)

## 勒索软件概述

近期，Unit42的研究人员观察到了WastedLocker勒索软件的活动有所上升，自从2020年5月份WildFire对该勒索软件的初始样本进行了分析之后，该活动的频率在近期有所增加。WastedLocker这个勒索软件跟Samsa、Maze、EKANS、Ryuk和BitPaymer等勒索软件类似，它们跟那些大规模感染目标用户的勒索软件不同，比如说WannaCry。WastedLocker这类勒索软件的目标一般是拥有大量资产的组织，通过在短时间内将精心编制的勒索软件尽可能多地部署到目标组织的内部系统中，以尽可能多地获取数据赎金。

## 攻击目标

研究人员根据威胁情报平台提供的信息，AutoFocus和Unit42已经能够确定WastedLocker背后的攻击者主要的攻击目标了。其中，大部分目标组织都位于美国境内，这些组织涵盖了多个领域，包括专业的法律服务机构、公共事业单位、能源产业、制造业、批发和零售业、高科技公司、工程公司、制药和生命科学公司，以及运输和物流业等等。

## 技术细节分析

![](https://image.3001.net/images/20200813/1597308743.png!small)

### 初始感染向量

根据赛门铁克之前对[ _WastedLocker_](https://symantec-enterprise-blogs.security.com/blogs/threat-intelligence/wastedlocker-ransomware-us)的分析，WastedLocker攻击活动种最常见的初始感染机制是通过一个伪装成合法软件升级ZIP文件来是西安的，这个文件种包含了恶意SocGholish
JavaScript框架加载器组件，它能够分析目标用户的计算机系统，并使用PowerShell来部署最终的Cobalt Strike Payload。

### 横向活动

当Cobalt Strike
Payload成功在目标用户的系统中安装之后，攻击者将会利用这个Payload在目标用户的网络系统中进行横向渗透活动，并帮助攻击者识别出其他可以攻击的系统。除此之外，研究人员还发现WastedLocker攻击者会试用合法的Windows实用工具来进行攻击，比如说WMI和PsExec等等。对于那些价值比较高的勒索软件目标用户来说，攻击者还会直接去攻击目标用户面向客户的财务/业务操作系统，以及那些具有高可见性和高使用率的内部系统，其中也包括数据备份系统。

### 最终的攻击Payload

最后，一旦攻击者完成了针对目标网络的充分侦察之后，攻击者就会利用一个或多个系统管理工具来安装部署WastedLocker勒索软件Payload。当恶意Payload在目标主机中执行之后，勒索软件将会做以下几件事情：

  * 如果勒索软件没有管理员权限时，恶意软件将会尝试在目标系统中提升权限；
  * 恶意软件会尝试禁用目标系统中的Windows Defender监控进程；
  * 删除目标系统中的卷影拷贝副本文件；
  * 将勒索软件/恶意软件安装为系统服务；

安装完成之后，Payload的部署就已经完成了，该加密的文件也已经加密成功了。勒索软件会使用“<victim
name>wasted”作为加密文件的后缀名，不过包含了勒索信息详情的提示文件后缀名为“<victim_name>wasted_info”。

我们对“*.wasted_info”勒索信息文件进行了分析，我们发现其中的变量数据显示在“<>”之间，这可能是因为使用WastedLocker勒索软件的攻击者电子邮件可能会不同，相关的域名包括PROTONMAIL.CH、AIRMAIL.CC、ECLIPSO.CH、TUTANOTA.COM和PROTONMAIL.COM。

 **勒索信息样本如下：**

    
    
    <victim name>
    
     
    
    YOUR NETWORK IS ENCRYPTED NOW
    
     
    
    USE <actor email 1> | <actor email 2> TO GET THE PRICE FOR YOUR DATA
    
     
    
    DO NOT GIVE THIS EMAIL TO 3RD PARTIES
    
     
    
    DO NOT RENAME OR MOVE THE FILE
    
     
    
    THE FILE IS ENCRYPTED WITH THE FOLLOWING KEY:
    
     
    
    [begin_key]<base64 encoded public key>[end_key]
    
     
    
    KEEP IT

## 参考资料

> [
> _https://isc.sans.edu/forums/diary/Fake+browser+update+pages+are+still+a+thing/25774/_](https://isc.sans.edu/forums/diary/Fake+browser+update+pages+are+still+a+thing/25774/)
>
> [ _https://labs.sentinelone.com/wastedlocker-ransomware-abusing-ads-and-> ntfs-file-attributes/_](https://labs.sentinelone.com/wastedlocker-> ransomware-abusing-ads-and-ntfs-file-attributes/)
>
> [ _https://symantec-enterprise-blogs.security.com/blogs/threat-> intelligence/wastedlocker-ransomware-us_](https://symantec-enterprise-> blogs.security.com/blogs/threat-intelligence/wastedlocker-ransomware-us)
>
> [ _https://research.nccgroup.com/2020/06/23/wastedlocker-a-new-ransomware-> variant-developed-by-the-evil-corp-> group/_](https://research.nccgroup.com/2020/06/23/wastedlocker-a-new-> ransomware-variant-developed-by-the-evil-corp-group/)
>
> [ _https://pan-unit42.github.io/playbook_viewer/?pb=wastedlocker-> ransomware_](https://pan-unit42.github.io/playbook_viewer/?pb=wastedlocker-> ransomware)
>
> [ _https://docs.paloaltonetworks.com/best-> practices_](https://docs.paloaltonetworks.com/best-practices)

